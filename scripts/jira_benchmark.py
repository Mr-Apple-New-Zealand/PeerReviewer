#!/usr/bin/env python3
"""Jira ticket-analysis benchmark.

Runs each candidate model over the synthetic ticket cases in
jira_benchmark/cases/, has a judge model grade every analysis against that
case's answer key, and records what each model cost to run: resident memory,
share on GPU, load time, seconds per case and throughput. The summary ranks
quality against cost. See docs/JIRA_BENCHMARK.md for the method.

Environment:
  OLLAMA_URL          On-prem Ollama endpoint (required for local models)
  OLLAMA_CLOUD_URL    Hosted Ollama, used for any ':cloud' tag (default https://ollama.com)
  OLLAMA_API_KEY      Bearer key for ':cloud' tags
  ANTHROPIC_API_KEY   Required when the judge is a claude-* model

Examples:
  python3 scripts/jira_benchmark.py --models "Qwen2.5-VL-7B-Instruct:latest, qwen3.6:27b=false"
  python3 scripts/jira_benchmark.py --calibrate-judge
  python3 scripts/jira_benchmark.py --rejudge jira_benchmark_results/run-12
  python3 scripts/jira_benchmark.py --list-cases
  python3 scripts/jira_benchmark.py --compare jira_analyst_results
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import random
import re
import statistics
import struct
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BENCH_DIR = ROOT / "jira_benchmark"
CASES_DIR = BENCH_DIR / "cases"
ANALYST_PROMPT_FILE = BENCH_DIR / "analyst_system_prompt.md"
JUDGE_PROMPT_FILE = BENCH_DIR / "judge_prompt.md"
IMAGES_DIR = BENCH_DIR / "images"
LOGS_DIR = BENCH_DIR / "logs"
TEXT_ATTACHMENT_KINDS = {"log", "text", "csv", "json"}

# Scoring weights. Each point in the answer key is worth 1 (partial 0.5).
# Penalties are subtracted from the points earned before dividing by the
# number of points, and the case score is floored at zero.
POINT_VALUE = {"found": 1.0, "partial": 0.5, "missed": 0.0}
TRAP_PENALTY = 1.0              # asserted one of the case's planted false claims
INVENTED_KEY_PENALTY = 1.0      # cited a ticket key that appears nowhere in the input
INVENTED_KEY_CAP = 3.0
UNSUPPORTED_PENALTY = 0.5       # any other claim the judge found unsupported by the tickets
UNSUPPORTED_CAP = 2.0

# Chars-per-token for the pre-flight fit check (the review workflow uses the
# same 2.5). Measured on C08: 2.86 chars/token, so this over-estimates. The real count comes back as
# prompt_eval_count and is checked again after every call.
CHARS_PER_TOKEN = 2.5
PROMPT_OVERHEAD_TOKENS = 500

JUDGE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["checkpoints", "unsupported_claims"],
    "properties": {
        "checkpoints": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "verdict", "quote", "reason"],
                "properties": {
                    "id": {"type": "string"},
                    "verdict": {"type": "string",
                                "enum": ["found", "partial", "missed", "violated", "clean"]},
                    "quote": {"type": "string"},
                    "reason": {"type": "string"},
                },
            },
        },
        "unsupported_claims": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["quote", "reason"],
                "properties": {
                    "quote": {"type": "string"},
                    "reason": {"type": "string"},
                },
            },
        },
    },
}


# ── Small helpers ────────────────────────────────────────────────────────────

def sha12(text: str) -> str:
    """SHA-256 of text after \\r\\n normalisation, first 12 hex chars. Same
    convention as the review and scorer workflows, so a Windows checkout and
    the Linux runner agree."""
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()[:12]


def joined(value) -> str:
    """Case files hold long text as a list of lines so the JSON stays readable."""
    if value is None:
        return ""
    if isinstance(value, list):
        return "\n".join(value)
    return str(value)


def slug(model: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", model).strip("_")


def fmt_s(secs) -> str:
    if secs is None:
        return "-"
    if secs >= 60:
        return f"{int(secs // 60)}m {secs % 60:.0f}s"
    return f"{secs:.1f}s"


def median(values):
    values = [v for v in values if v is not None]
    return round(statistics.median(values), 1) if values else None


def mean(values):
    values = [v for v in values if v is not None]
    return round(sum(values) / len(values), 1) if values else None


# ── Cases ────────────────────────────────────────────────────────────────────

NOISE_PEOPLE = ["Priya Nair", "Tom Becker", "Marcus Reid", "Ravi Kumar", "Hana Sato",
                "Lena Fischer", "Sam Okafor", "Jo Tan"]
NOISE_BRANCHES = ["feature/emailhub", "feature/emailhub-webhooks", "feature/emailhub-templates",
                  "chore/emailhub-deps"]


def noise_comments(spec: dict) -> list[dict]:
    """Deterministic low-value comments of the kind real long-running tickets
    accumulate: CI bots, automation reminders, chasers and status chatter.
    None of them carries a decision, an owner change or a date, so the
    answer key is unaffected by how many are generated."""
    rng = random.Random(spec["seed"])
    start = datetime.fromisoformat(spec["from"])
    end = datetime.fromisoformat(spec["to"])
    span = int((end - start).total_seconds())
    # Work-in-progress chatter comes from whoever owned the ticket at the
    # time, so the noise never contradicts the real handovers.
    owners = sorted((datetime.fromisoformat(o["from"]), o["who"]) for o in spec.get("owners", []))

    def owner_at(when):
        current = None
        for since, who in owners:
            if since <= when:
                current = who
        return current

    out = []
    for _ in range(spec["comments"]):
        when = start + timedelta(seconds=rng.randrange(span))
        roll = rng.random()
        if roll < 0.40:
            build = rng.randrange(4100, 4999)
            branch = rng.choice(NOISE_BRANCHES)
            ok = rng.random() < 0.8
            body = [f"Build #{build} {'passed' if ok else 'FAILED'} for branch {branch}.",
                    f"Duration {rng.randrange(4, 19)}m {rng.randrange(0, 59)}s. "
                    f"Tests: {rng.randrange(812, 860)} run, {0 if ok else rng.randrange(1, 6)} failed, "
                    f"{rng.randrange(3, 12)} skipped.",
                    "Pipeline: build > unit-tests > integration-tests > package"]
            if not ok:
                body.append("Failing stage: integration-tests (flaky: EmailTemplateRenderingTests)")
            author = "CI Bot"
        elif roll < 0.52:
            body = ["This issue has not been updated in 7 days. Please add a status update "
                    "or move it to the correct column.",
                    "(This is an automated message from Jira Automation rule 'Stale in-progress reminder'.)"]
            author = "Jira Automation"
        elif roll < 0.62:
            body = [rng.choice([
                "A page was linked to this issue: 'EmailHub integration notes'.",
                "A page was linked to this issue: 'Sprint review notes'.",
                "A page was linked to this issue: 'Email deliverability dashboard'.",
            ])]
            author = "Confluence"
        elif roll < 0.72:
            body = [rng.choice([
                "Any update on this?",
                "Is there an ETA for this one?",
                "Bumping this - support keep asking about the new emails.",
                "+1, customers mention the old email styling in feedback.",
            ])]
            author = rng.choice(["Marcus Reid", "Tom Becker", "Lena Fischer"])
        elif roll < 0.86:
            body = [rng.choice([
                "Still working through this, nothing blocking today.",
                "Paired on the template mapping this morning, continuing tomorrow.",
                "Rebased on main, fixed the merge conflicts in EmailService.",
                "Updated unit tests after the template changes.",
                "Tidied up logging in the EmailHub client, no behaviour change.",
                "Dependabot bumped the HTTP client library; checked it still builds.",
                "Ran the local smoke test again, still green.",
            ])]
            author = owner_at(when) or rng.choice(NOISE_PEOPLE)
        else:
            body = [rng.choice([
                "Moved to the next sprint board during sprint planning.",
                "Discussed in standup, no change.",
                "Reviewed in backlog refinement, no change to scope.",
            ])]
            author = rng.choice(["Aroha Walker", "Dev Patel"])
        out.append({"author": author, "created": when.strftime("%Y-%m-%d %H:%M"), "body": body})
    return out


def load_cases(selected: list[str] | None = None) -> list[dict]:
    cases = []
    for path in sorted(CASES_DIR.glob("*.json")):
        case = json.loads(path.read_text(encoding="utf-8"))
        case["_file"] = path.name
        case["_sha"] = sha12(path.read_text(encoding="utf-8"))
        cases.append(case)
    if selected:
        wanted = {c.strip().upper() for c in selected if c.strip()}
        cases = [c for c in cases if c["id"].upper() in wanted]
        missing = wanted - {c["id"].upper() for c in cases}
        if missing:
            sys.exit(f"ERROR: unknown case id(s): {', '.join(sorted(missing))}")
    for case in cases:
        validate_case(case)
        for ticket in case["tickets"]:
            for att in ticket.get("attachments") or []:
                if not att.get("file"):
                    continue
                # Images go to the model as images; logs and other text files are
                # inlined into the ticket, the way an integration would paste an
                # attached file into the prompt.
                text = att.get("kind") in TEXT_ATTACHMENT_KINDS
                path = (LOGS_DIR if text else IMAGES_DIR) / att["file"]
                if not path.exists():
                    sys.exit(f"ERROR: {case['id']} attachment {att['name']}: {path} not found")
                if text:
                    att["_text"] = path.read_text(encoding="utf-8").rstrip()
                    # The case SHA has to move when an attached file changes, or
                    # two runs with different inputs would look comparable.
                    case["_sha"] = sha12(case["_sha"] + att["_text"])
                else:
                    att["_path"] = path
        for ticket in case["tickets"]:
            spec = ticket.pop("noise", None)
            if spec:
                ticket["comments"] = sorted(ticket.get("comments", []) + noise_comments(spec),
                                            key=lambda c: c["created"])
    return cases


def validate_case(case: dict) -> None:
    where = case.get("_file", case.get("id", "?"))
    for field in ("id", "title", "request", "analysis_date", "tickets", "answer_key"):
        if field not in case:
            sys.exit(f"ERROR: {where} has no '{field}'")
    ids = [cp["id"] for cp in case["answer_key"]]
    if len(ids) != len(set(ids)):
        sys.exit(f"ERROR: {where} has duplicate answer-key ids")
    for cp in case["answer_key"]:
        if cp.get("kind") not in ("point", "inference", "trap"):
            sys.exit(f"ERROR: {where} {cp.get('id')} has kind {cp.get('kind')!r}")
        if not cp.get("expect"):
            sys.exit(f"ERROR: {where} {cp['id']} has no 'expect'")
    if not any(cp["kind"] != "trap" for cp in case["answer_key"]):
        sys.exit(f"ERROR: {where} has no scorable points")


def render_ticket(t: dict) -> str:
    def val(key, default="None"):
        v = t.get(key)
        if v in (None, "", []):
            return default
        return ", ".join(v) if isinstance(v, list) else str(v)

    lines = [f"=== {t['key']}: {t['summary']} ===",
             f"Type: {val('type')} | Status: {val('status')} | Resolution: {val('resolution', 'Unresolved')}"
             f" | Priority: {val('priority')}",
             f"Assignee: {val('assignee', 'Unassigned')} | Reporter: {val('reporter')}",
             f"Created: {val('created')} | Updated: {val('updated')} | Due date: {val('due')}",
             f"Components: {val('components')} | Affects versions: {val('affects_versions')}"
             f" | Fix versions: {val('fix_versions')}",
             f"Sprint: {val('sprint')} | Story points: {val('story_points')} | Labels: {val('labels')}"]
    links = t.get("links") or []
    lines.append("Links: " + ("; ".join(f"{l['type']} {l['key']}" for l in links) if links else "None"))
    atts = t.get("attachments") or []
    lines.append("Attachments: " + ("; ".join(
        f"{a['name']} ({a.get('size', '?')}, {a.get('kind', 'file')})"
        + (" [provided with this request]" if a.get("_path") else "")
        + (" [contents included below]" if a.get("_text") else "")
        for a in atts) if atts else "None"))
    lines += ["", "Description:", joined(t.get("description")) or "(empty)"]
    history = t.get("history") or []
    if history:
        lines += ["", "History:"]
        for h in history:
            lines.append(f"  {h['when']} {h['who']}: {h['field']}: {h.get('from') or 'None'} -> {h.get('to') or 'None'}")
    comments = t.get("comments") or []
    lines += ["", f"Comments ({len(comments)}):"]
    for c in comments:
        lines.append(f"[{c['created']}] {c['author']}:")
        lines.append(joined(c["body"]))
        lines.append("")
    for a in atts:
        if a.get("_text"):
            lines += ["", f"--- Attached file: {a['name']} ---", a["_text"],
                      f"--- End of {a['name']} ---"]
    return "\n".join(lines).rstrip()


def render_case(case: dict) -> str:
    """The user message the analyst receives: tickets first, the question last,
    which is the order that holds up best on long inputs."""
    tickets = "\n\n".join(render_ticket(t) for t in case["tickets"])
    return (f"Today's date: {case['analysis_date']}\n\n"
            f"The following Jira ticket export is provided for analysis.\n\n"
            f"{tickets}\n\n"
            f"=== End of tickets ===\n\n"
            f"Request: {case['request']}")


def case_images(case: dict) -> list[Path]:
    """Attachment files to send with the request, in ticket then attachment order."""
    return [a["_path"] for t in case["tickets"] for a in (t.get("attachments") or []) if a.get("_path")]


def image_tokens(path: Path) -> int:
    """Rough token cost of an image for a Qwen-VL model: 28px patches, merged
    2x2. Only used for the pre-flight fit check; the real count comes back as
    prompt_eval_count."""
    try:
        with open(path, "rb") as f:
            head = f.read(33)
        if head[1:4] != b"PNG":  # not a PNG: fall back to a flat allowance
            return 1500
        w, h = struct.unpack(">II", head[16:24])
        return -(-w // 28) * -(-h // 28) // 4
    except OSError:
        return 1500


# Ticket keys are only policed for the projects the dataset actually uses, so
# identifiers like EH-413 or SHA-256 in an analysis are not flagged.
KEY_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,9})-(\d+)\b")


def project_prefixes(cases: list[dict]) -> set[str]:
    return {t["key"].split("-")[0] for c in cases for t in c["tickets"]}


def invented_keys(analysis: str, case_text: str, prefixes: set[str]) -> list[str]:
    known = {m.group(0) for m in KEY_RE.finditer(case_text)}
    found = []
    for m in KEY_RE.finditer(analysis):
        if m.group(1) in prefixes and m.group(0) not in known and m.group(0) not in found:
            found.append(m.group(0))
    return found


# ── HTTP ─────────────────────────────────────────────────────────────────────

class HttpError(RuntimeError):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body[:500]}")
        self.status = status


def post_json(url: str, body: dict, headers: dict | None = None, timeout: int = 7200) -> dict:
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise HttpError(e.code, e.read().decode("utf-8", "replace")) from None


def get_json(url: str, timeout: int = 30) -> dict:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


class Endpoints:
    def __init__(self):
        self.ollama = (os.environ.get("OLLAMA_URL") or "").strip().rstrip("/")
        self.cloud = (os.environ.get("OLLAMA_CLOUD_URL") or "https://ollama.com").strip().rstrip("/")
        self.cloud_key = (os.environ.get("OLLAMA_API_KEY") or "").strip()
        self.anthropic_key = (os.environ.get("ANTHROPIC_API_KEY") or "").strip()
        self._caps = {}

    @staticmethod
    def is_cloud(model: str) -> bool:
        return model.strip().lower().endswith(":cloud")

    @staticmethod
    def is_claude(model: str) -> bool:
        return model.strip().lower().startswith("claude-")

    def ollama_route(self, model: str) -> tuple[str, dict]:
        # Local Ollama answers 400 to an Authorization header, so only the
        # hosted endpoint gets one.
        if self.is_cloud(model):
            if not self.cloud_key:
                raise RuntimeError(f"'{model}' is a cloud model but OLLAMA_API_KEY is unset.")
            return self.cloud, {"Authorization": f"Bearer {self.cloud_key}"}
        if not self.ollama:
            raise RuntimeError(f"'{model}' is a local model but OLLAMA_URL is not set.")
        return self.ollama, {}

    def capabilities(self, model: str) -> list[str] | None:
        if model in self._caps:
            return self._caps[model]
        caps = None
        try:
            caps = post_json(f"{self.ollama}/api/show", {"model": model}, timeout=30).get("capabilities") or []
        except Exception:
            pass
        self._caps[model] = caps
        return caps

    def ps(self) -> list[dict]:
        try:
            return get_json(f"{self.ollama}/api/ps").get("models") or []
        except Exception as e:
            print(f"      (could not read /api/ps: {e})")
            return []

    def unload(self, model: str) -> None:
        try:
            post_json(f"{self.ollama}/api/generate", {"model": model, "keep_alive": 0}, timeout=120)
        except Exception as e:
            print(f"      (unload of {model} failed: {e})")


def ollama_chat(ep: Endpoints, model: str, system: str, user: str, options: dict,
                think: str = "", fmt: dict | None = None, images: list[Path] | None = None) -> dict:
    base, headers = ep.ollama_route(model)
    user_msg = {"role": "user", "content": user}
    if images:
        user_msg["images"] = [base64.b64encode(p.read_bytes()).decode() for p in images]
    messages = ([{"role": "system", "content": system}] if system else []) + [user_msg]
    body = {"model": model, "messages": messages, "stream": False, "options": options}
    if think:
        t = think.lower()
        body["think"] = True if t == "true" else False if t == "false" else think
    if fmt:
        body["format"] = fmt
    t0 = time.monotonic()
    try:
        data = post_json(f"{base}/api/chat", body, headers)
    except (urllib.error.URLError, ConnectionError, TimeoutError) as e:
        # One retry for a dropped connection. HTTP errors are not retried --
        # a 400 or 404 will not fix itself and retrying hides the cause.
        print(f"      (connection error, retrying once: {e})")
        time.sleep(10)
        data = post_json(f"{base}/api/chat", body, headers)
    wall = time.monotonic() - t0
    msg = data.get("message") or {}
    content = re.sub(r"<think>.*?</think>\s*", "", msg.get("content") or "",
                     flags=re.DOTALL | re.IGNORECASE).strip()

    def s(key):
        v = data.get(key)
        return round(v / 1e9, 2) if v else None

    def tps(tok_key, dur_key):
        tok, dur = data.get(tok_key), data.get(dur_key)
        return round(tok / (dur / 1e9), 1) if tok and dur else None

    total, load = s("total_duration"), s("load_duration")
    return {
        "content": content,
        "thinking": msg.get("thinking") or "",
        "metrics": {
            "wall_s": round(wall, 2),
            "total_s": total,
            "load_s": load,
            # Time the request actually spent working, excluding the one-off
            # model load, which is reported separately as cold-load time.
            "gen_s": round(total - (load or 0), 2) if total is not None else round(wall, 2),
            "prompt_tokens": data.get("prompt_eval_count"),
            "output_tokens": data.get("eval_count"),
            "prompt_tps": tps("prompt_eval_count", "prompt_eval_duration"),
            "output_tps": tps("eval_count", "eval_duration"),
            "done_reason": data.get("done_reason"),
            "thinking_chars": len(msg.get("thinking") or ""),
            "content_chars": len(content),
        },
    }


def anthropic_json(ep: Endpoints, model: str, system: str, user: str, schema: dict,
                   effort: str, max_tokens: int = 16000) -> tuple[dict, dict]:
    """Claude call constrained to a JSON schema. No temperature: current Claude
    models reject it; depth is set with output_config.effort instead."""
    if not ep.anthropic_key:
        raise RuntimeError(f"judge '{model}' needs ANTHROPIC_API_KEY, which is unset.")
    body = {
        "model": model.strip().lower(),
        "max_tokens": max_tokens,
        "system": system,
        "messages": [{"role": "user", "content": user}],
        "thinking": {"type": "adaptive"},
        "output_config": {"effort": effort,
                          "format": {"type": "json_schema", "schema": schema}},
    }
    headers = {"x-api-key": ep.anthropic_key, "anthropic-version": "2023-06-01"}
    delay = 15
    for attempt in range(4):
        t0 = time.monotonic()
        try:
            data = post_json("https://api.anthropic.com/v1/messages", body, headers, timeout=900)
            break
        except HttpError as e:
            if attempt < 3 and (e.status == 429 or e.status >= 500):
                print(f"      (judge HTTP {e.status}, retry in {delay}s)")
                time.sleep(delay)
                delay *= 2
                continue
            raise
    stop = data.get("stop_reason")
    if stop in ("refusal", "max_tokens"):
        raise RuntimeError(f"judge stop_reason={stop}")
    text = "".join(b.get("text", "") for b in data.get("content") or [] if b.get("type") == "text")
    usage = data.get("usage") or {}
    return json.loads(text), {"wall_s": round(time.monotonic() - t0, 1),
                              "input_tokens": usage.get("input_tokens"),
                              "output_tokens": usage.get("output_tokens")}


# ── Judging ──────────────────────────────────────────────────────────────────

def _norm(s: str) -> str:
    s = s.lower()
    for a, b in (("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'),
                 ("–", "-"), ("—", "-"), ("→", "->"), ("…", "...")):
        s = s.replace(a, b)
    # Emphasis markers are deleted, not spaced: "**Status**: In Progress" must
    # match a judge quote of "Status: In Progress". Replacing them with spaces
    # left "status : in progress" and threw out two correct verdicts in run 2.
    s = re.sub(r"[*_`]", "", s)
    s = re.sub(r"[#>|\[\]]", " ", s)
    s = re.sub(r"\s+", " ", s)
    return re.sub(r" ([:;,.!?)])", r"\1", s).strip()


def grounded(quote: str, analysis_norm: str) -> bool:
    """Is the judge's quote really in the analysis? A verdict the judge cannot
    back with the analysis's own words is not credited. Tolerates markdown,
    smart quotes, '...' elisions and small copy slips, nothing more."""
    q = _norm(quote).strip(" \"'")
    if not q:
        return False
    if q in analysis_norm:
        return True
    frags = [f.strip(" \"'") for f in q.split("...")]
    frags = [f for f in frags if len(f) >= 12]
    if frags and all(f in analysis_norm for f in frags):
        return True
    words = q.split()
    if len(words) < 5:
        return False
    vocab = set(analysis_norm.split())
    if sum(w in vocab for w in words) / len(words) < 0.9:
        return False
    return any(" ".join(words[i:i + 5]) in analysis_norm for i in range(len(words) - 4))


def build_judge_input(case: dict, case_text: str, analysis: str) -> str:
    key = [{"id": cp["id"], "kind": cp["kind"], "expect": cp["expect"]} for cp in case["answer_key"]]
    return (f"<input_given_to_analyst>\n{case_text}\n</input_given_to_analyst>\n\n"
            f"<answer_key>\n{json.dumps(key, indent=2)}\n</answer_key>\n\n"
            f"<analysis>\n{analysis}\n</analysis>")


def judge_json(content: str, thinking: str) -> dict:
    """Parse an Ollama judge's reply into the verdict object.

    Not every model honours the format schema: some wrap the object in a
    markdown fence, some prepend a sentence, and a reasoning model can return
    empty content with the answer left in its thinking. Recover the object
    from any of those rather than failing the case, and if it really is not
    there, say what came back instead of just 'Expecting value'.
    """
    for candidate in (content, thinking):
        if not candidate or not candidate.strip():
            continue
        text = candidate.strip()
        fence = re.search(r"```(?:json)?\s*(.+?)```", text, re.DOTALL)
        if fence:
            text = fence.group(1).strip()
        else:
            # An unterminated fence: the model opened ```json and stopped
            # without closing it. The array inside is often complete.
            text = re.sub(r"^```(?:json)?\s*", "", text).strip()
        attempts = [text]
        # Arrays first: a truncated array's last '}' closes its FIRST element,
        # so brace extraction would quietly return one checkpoint and score
        # the rest as missed. Better to fail loudly than to lose the verdicts.
        for opener, closer in (("[", "]"), ("{", "}")):
            a, b = text.find(opener), text.rfind(closer)
            if a != -1 and b > a:
                attempts.append(text[a:b + 1])
        for attempt in attempts:
            try:
                parsed = json.loads(attempt)
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, list):
                return {"checkpoints": parsed}
            if isinstance(parsed, dict):
                # A lone checkpoint is a fragment of a truncated array, not the
                # envelope the schema asks for.
                if "id" in parsed and "verdict" in parsed:
                    continue
                return parsed
    got = (content or "").strip() or (thinking or "").strip()
    where = "content" if (content or "").strip() else ("thinking only" if got else "nothing")
    if not got:
        raise RuntimeError("judge returned empty content and empty thinking")
    detail = f"{len(got)} chars"
    if got.count("[") != got.count("]") or got.count("{") != got.count("}"):
        detail += ", brackets unbalanced so the reply looks truncated"
    raise RuntimeError(f"judge returned no JSON object ({where}, {detail}): {got[:200]!r}")


def judge_analysis(ep: Endpoints, cfg: dict, judge_prompt: str, case: dict,
                   case_text: str, analysis: str) -> dict:
    user = build_judge_input(case, case_text, analysis)
    last_err = None
    for attempt in range(2):
        try:
            if Endpoints.is_claude(cfg["judge"]):
                raw, usage = anthropic_json(ep, cfg["judge"], judge_prompt, user, JUDGE_SCHEMA,
                                            cfg["judge_effort"])
            else:
                r = ollama_chat(ep, cfg["judge"], judge_prompt, user,
                                {"temperature": 0, "num_ctx": cfg["judge_num_ctx"],
                                 "num_predict": cfg["judge_num_predict"]},
                                think=cfg.get("judge_think", ""), fmt=JUDGE_SCHEMA)
                raw = judge_json(r["content"], r.get("thinking", ""))
                usage = {"wall_s": r["metrics"]["wall_s"]}
            return apply_judgement(case, analysis, raw, usage)
        except (json.JSONDecodeError, RuntimeError, HttpError, KeyError,
                TypeError, AttributeError) as e:
            last_err = e
            print(f"      (judge attempt {attempt + 1} failed: {e})")
    raise RuntimeError(f"judge failed twice: {last_err}")


VERDICT_LIST_KEYS = ("checkpoints", "verdicts", "results", "items",
                     "judgements", "judgments", "evaluations")


def verdict_items(raw: dict, known_ids: set) -> list:
    """The judge's verdict list, whatever it decided to call it.

    A judge that follows the schema returns {"checkpoints": [...]}. Others
    return the same list under 'verdicts' or 'results', or a map of checkpoint
    id to verdict. The content is identical and correct in each case, so take
    it rather than defaulting every checkpoint to missed and scoring a good
    judgement as zero.
    """
    for key in VERDICT_LIST_KEYS:
        value = raw.get(key)
        if isinstance(value, list):
            return value
    return [dict(v, id=v.get("id") or k) for k, v in raw.items()
            if k in known_ids and isinstance(v, dict)]


def apply_judgement(case: dict, analysis: str, raw: dict, usage: dict) -> dict:
    """Validate the judge's verdicts against the answer key and the analysis.

    - Every key id must get a verdict. Omitted ids count as missed / clean and
      are reported, so a lazy judge shows up rather than hiding.
    - A verdict of the wrong family for its kind (e.g. 'found' on a trap) is
      mapped to its equivalent and counted as a normalisation.
    - found / partial / violated need a quote that is actually in the analysis.
      Ungrounded ones are downgraded to missed / clean and counted.
    """
    analysis_norm = _norm(analysis)
    known_ids = {cp["id"] for cp in case["answer_key"]}
    by_id = {}
    for item in verdict_items(raw, known_ids):
        by_id.setdefault(str(item.get("id", "")).strip(), item)
    rows, notes = [], {"omitted": [], "normalised": [], "ungrounded": [], "unknown_ids": []}
    notes["unknown_ids"] = sorted(set(by_id) - known_ids)
    for cp in case["answer_key"]:
        item = by_id.get(cp["id"])
        trap = cp["kind"] == "trap"
        if item is None:
            notes["omitted"].append(cp["id"])
            verdict, quote, reason = ("clean" if trap else "missed"), "", "judge gave no verdict"
            judge_verdict = None
        else:
            verdict = str(item.get("verdict", "")).lower()
            judge_verdict = verdict
            quote, reason = item.get("quote") or "", item.get("reason") or ""
            if trap and verdict not in ("violated", "clean"):
                notes["normalised"].append(cp["id"])
                verdict = "violated" if verdict in ("found", "partial") else "clean"
            elif not trap and verdict not in ("found", "partial", "missed"):
                notes["normalised"].append(cp["id"])
                verdict = "missed"
        if verdict in ("found", "partial", "violated") and not grounded(quote, analysis_norm):
            notes["ungrounded"].append(cp["id"])
            reason = f"[downgraded: quote not found in analysis] {reason}"
            verdict = "clean" if trap else "missed"
        # judge_verdict is what the judge said before any downgrade, so a
        # harness fix can be re-applied later without paying for the judge again.
        rows.append({"id": cp["id"], "kind": cp["kind"], "verdict": verdict,
                     "judge_verdict": judge_verdict, "quote": quote, "reason": reason})
    unsupported = []
    for claim in raw.get("unsupported_claims") or []:
        if grounded(claim.get("quote") or "", analysis_norm):
            unsupported.append({"quote": claim.get("quote"), "reason": claim.get("reason")})
        else:
            notes["ungrounded"].append("unsupported_claim")
    return {"checkpoints": rows, "unsupported_claims": unsupported, "judge_notes": notes,
            "judge_usage": usage, "raw": raw}


def score_case(judged: dict, invented: list[str]) -> dict:
    rows = judged["checkpoints"]
    points = [r for r in rows if r["kind"] != "trap"]
    traps = [r for r in rows if r["kind"] == "trap"]
    earned = sum(POINT_VALUE[r["verdict"]] for r in points)
    violated = [r["id"] for r in traps if r["verdict"] == "violated"]
    unsupported = len(judged["unsupported_claims"])
    penalty = (TRAP_PENALTY * len(violated)
               + min(INVENTED_KEY_CAP, INVENTED_KEY_PENALTY * len(invented))
               + min(UNSUPPORTED_CAP, UNSUPPORTED_PENALTY * unsupported))
    return {
        "score": round(max(0.0, earned - penalty) / len(points) * 100, 1),
        "coverage": round(earned / len(points) * 100, 1),
        "found": sum(r["verdict"] == "found" for r in points),
        "partial": sum(r["verdict"] == "partial" for r in points),
        "missed": sum(r["verdict"] == "missed" for r in points),
        "points": len(points),
        "traps_violated": violated,
        "traps": len(traps),
        "invented_keys": invented,
        "unsupported_claims": unsupported,
        "penalty": round(penalty, 2),
    }


# ── Candidate runs ───────────────────────────────────────────────────────────

def parse_models(raw: str, default_think: str) -> list[tuple[str, str]]:
    """'model=think' per entry, as in the scorer benchmark. '=' because ':'
    is already in every Ollama tag; 'none' sends no think field at all."""
    out = []
    for entry in [e.strip() for e in raw.split(",") if e.strip()]:
        name, _, override = entry.partition("=")
        override = override.strip()
        out.append((name.strip(), "" if override.lower() == "none" else (override or default_think)))
    return out


def run_model(ep: Endpoints, cfg: dict, model: str, think: str, cases: list[dict],
              case_texts: dict, analyst_prompt: str, judge_prompt: str,
              prefixes: set[str], out_dir: Path) -> dict:
    mdir = out_dir / slug(model)
    mdir.mkdir(parents=True, exist_ok=True)
    local = not Endpoints.is_cloud(model)
    record = {"model": model, "think": think or None, "cases": [], "resource": {}, "errors": []}

    if think and think.lower() != "false" and local:
        caps = ep.capabilities(model)
        if caps is not None and "thinking" not in caps:
            print(f"   (think={think} dropped: {model} has no thinking capability)")
            think = ""
            record["think"] = None

    if local:
        others = [m.get("name") for m in ep.ps() if m.get("name") != model]
        if others:
            print(f"   WARNING: other models resident before start: {others}. Timings may be contended.")
        record["resource"]["resident_before_start"] = others

    # A case with an attached image cannot be answered by a text-only model:
    # Ollama rejects the request outright. Those cases are recorded as errors
    # and scored 0 rather than skipped, because reading the screenshot IS the
    # task the case sets.
    no_vision = []
    if local and any(case_images(c) for c in cases):
        caps = ep.capabilities(model)
        if caps is not None and "vision" not in caps:
            no_vision = [c["id"] for c in cases if case_images(c)]
            print(f"   WARNING: {model} has no vision capability; case(s) {', '.join(no_vision)} "
                  f"need an attached image and will score 0.")

    options = {"temperature": cfg["temperature"], "num_ctx": cfg["num_ctx"], "num_predict": cfg["num_predict"]}
    if cfg.get("seed") is not None:
        options["seed"] = cfg["seed"]

    first = True
    for rep in range(cfg["repeats"]):
        for case in cases:
            tag = case["id"] + (f".r{rep + 1}" if cfg["repeats"] > 1 else "")
            print(f"   {tag} {case['title']} ...", end=" ", flush=True)
            entry = {"case": case["id"], "repeat": rep + 1}
            if case["id"] in no_vision:
                print("SKIPPED: model cannot see the attached image")
                entry.update({"error": "model has no vision capability", "score": 0.0,
                              "flags": ["case needs vision; model has none"]})
                record["cases"].append(entry)
                record["errors"].append(f"{tag}: model has no vision capability")
                continue
            try:
                r = ollama_chat(ep, model, analyst_prompt, case_texts[case["id"]], options, think,
                                images=case_images(case))
            except Exception as e:
                print(f"ERROR: {e}")
                entry.update({"error": f"request failed: {e}", "score": 0.0})
                record["cases"].append(entry)
                record["errors"].append(f"{tag}: {e}")
                continue
            m = r["metrics"]
            entry["metrics"] = m
            (mdir / f"{tag}.analysis.md").write_text(r["content"], encoding="utf-8")
            if r["thinking"]:
                (mdir / f"{tag}.thinking.md").write_text(r["thinking"], encoding="utf-8")
            if first and local:
                snapshot = next((p for p in ep.ps() if p.get("name") == model or p.get("model") == model), None)
                if snapshot:
                    size, vram = snapshot.get("size") or 0, snapshot.get("size_vram") or 0
                    record["resource"].update({
                        "resident_gb": round(size / 1e9, 2),
                        "vram_gb": round(vram / 1e9, 2),
                        "gpu_pct": round(vram / size * 100, 1) if size else None,
                        "loaded_context": snapshot.get("context_length"),
                    })
                record["resource"]["cold_load_s"] = m["load_s"]
                first = False
            flags = []
            if m["done_reason"] == "length":
                flags.append("output hit num_predict")
            if m["prompt_tokens"] and m["prompt_tokens"] >= cfg["num_ctx"] - cfg["num_predict"]:
                flags.append(f"prompt {m['prompt_tokens']} tok may have been truncated to fit num_ctx")
            if not r["content"]:
                flags.append(f"empty content (thinking {m['thinking_chars']} chars)")
            entry["flags"] = flags
            if not r["content"]:
                print(f"EMPTY ({fmt_s(m['gen_s'])})")
                entry.update({"error": "empty content", "score": 0.0})
                record["cases"].append(entry)
                record["errors"].append(f"{tag}: empty content")
                continue
            entry["invented_keys"] = invented_keys(r["content"], case_texts[case["id"]], prefixes)
            if cfg["skip_judge"]:
                print(f"{fmt_s(m['gen_s'])}, {m['output_tokens']} tok")
            else:
                try:
                    judged = judge_analysis(ep, cfg, judge_prompt, case, case_texts[case["id"]], r["content"])
                    (mdir / f"{tag}.judge.json").write_text(json.dumps(judged, indent=2), encoding="utf-8")
                    entry.update(score_case(judged, entry["invented_keys"]))
                    entry["judge_notes"] = judged["judge_notes"]
                    print(f"{entry['score']:.0f}/100 in {fmt_s(m['gen_s'])}, {m['output_tokens']} tok")
                except Exception as e:
                    print(f"judge ERROR: {e}")
                    entry["judge_error"] = str(e)
                    record["errors"].append(f"{tag}: judge failed: {e}")
            for f in flags:
                print(f"      ! {f}")
            record["cases"].append(entry)

    if local and not cfg["keep_loaded"]:
        ep.unload(model)
    return record


# ── Aggregation and report ───────────────────────────────────────────────────

def aggregate(record: dict) -> dict:
    ok = [c for c in record["cases"] if "metrics" in c]
    scored = [c for c in record["cases"] if "score" in c]
    per_case = {}
    for c in scored:
        per_case.setdefault(c["case"], []).append(c["score"])
    case_means = {k: round(sum(v) / len(v), 1) for k, v in per_case.items()}
    reps = {}
    for c in scored:
        reps.setdefault(c["repeat"], []).append(c["score"])
    rep_means = [sum(v) / len(v) for v in reps.values()]
    res = record["resource"]
    return {
        "quality": round(sum(case_means.values()) / len(case_means), 1) if case_means else None,
        "quality_range": (round(min(rep_means), 1), round(max(rep_means), 1)) if len(rep_means) > 1 else None,
        "coverage": mean([c.get("coverage") for c in scored if "coverage" in c]),
        "traps_violated": sum(len(c.get("traps_violated", [])) for c in scored),
        "traps_total": sum(c.get("traps", 0) for c in scored),
        "invented_keys": sum(len(c.get("invented_keys", [])) for c in scored),
        "unsupported": sum(c.get("unsupported_claims", 0) for c in scored),
        "case_scores": case_means,
        "resident_gb": res.get("resident_gb"),
        "gpu_pct": res.get("gpu_pct"),
        "cold_load_s": res.get("cold_load_s"),
        "mean_case_s": mean([c["metrics"]["gen_s"] for c in ok]),
        "output_tps": median([c["metrics"]["output_tps"] for c in ok]),
        "prompt_tps": median([c["metrics"]["prompt_tps"] for c in ok]),
        "mean_output_tokens": mean([c["metrics"]["output_tokens"] for c in ok]),
        "errors": len(record["errors"]),
        "flags": sum(len(c.get("flags", [])) for c in record["cases"]),
        "ungrounded": sum(len(c.get("judge_notes", {}).get("ungrounded", [])) for c in scored),
        "omitted": sum(len(c.get("judge_notes", {}).get("omitted", [])) for c in scored),
    }


def pareto(aggs: dict) -> set[str]:
    """Models no other model beats on quality, memory and time at once."""
    pts = {m: a for m, a in aggs.items()
           if a["quality"] is not None and a["resident_gb"] is not None and a["mean_case_s"] is not None}
    front = set()
    for m, a in pts.items():
        dominated = any(
            b["quality"] >= a["quality"] and b["resident_gb"] <= a["resident_gb"]
            and b["mean_case_s"] <= a["mean_case_s"]
            and (b["quality"] > a["quality"] or b["resident_gb"] < a["resident_gb"]
                 or b["mean_case_s"] < a["mean_case_s"])
            for n, b in pts.items() if n != m)
        if not dominated:
            front.add(m)
    return front


RUN_SETTINGS = ("started", "harness_commit", "num_ctx", "num_predict", "temperature", "seed", "repeats",
                "system_prompt", "analyst_prompt_sha", "judge", "judge_effort", "judge_prompt_sha", "cases_sha")


def write_summary(out_dir: Path, cfg: dict, records: list[dict], cases: list[dict], title: str | None = None,
                  settings: tuple = RUN_SETTINGS, runs: dict | None = None, notes: list[str] | None = None) -> str:
    """Summary for one run, or (with title/settings/runs) the cross-run leaderboard.
    runs maps model -> the run it came from, shown as its own table because
    num_ctx, num_predict and repeats may differ between models there."""
    aggs = {r["model"]: aggregate(r) for r in records}
    front = pareto(aggs)
    ranked = sorted(aggs, key=lambda m: (aggs[m]["quality"] is None, -(aggs[m]["quality"] or 0)))
    L = [title or f"# Jira Analyst Benchmark - run {cfg['run_id']}", ""]
    L += ["| Setting | Value |", "|---|---|"]
    for k in settings:
        L.append(f"| {k} | {cfg.get(k)} |")
    L.append(f"| cases | {', '.join(c['id'] for c in cases)} |")
    L.append("")

    if not cfg["skip_judge"]:
        best = ranked[0] if ranked and aggs[ranked[0]]["quality"] is not None else None
        if best:
            L += ["## Headline", ""]
            bq = aggs[best]["quality"]
            L.append(f"- **Best quality:** {best} at {bq:.1f}/100.")
            margin = cfg["value_margin"]
            near = [m for m in ranked if aggs[m]["quality"] is not None and aggs[m]["quality"] >= bq - margin
                    and aggs[m]["resident_gb"] is not None]
            if near:
                value = min(near, key=lambda m: (aggs[m]["resident_gb"], aggs[m]["mean_case_s"] or 0))
                a = aggs[value]
                L.append(f"- **Best value** (smallest memory within {margin:g} points of the best): {value} "
                         f"at {a['quality']:.1f}/100, {a['resident_gb']:.1f} GB resident, "
                         f"{fmt_s(a['mean_case_s'])} per case.")
            L.append(f"- **Pareto front** (nothing else is better on quality, memory and time at once): "
                     f"{', '.join(m for m in ranked if m in front) or 'n/a'}.")
            L.append("")

    L += ["## Ranking", "",
          "| # | Model | Quality | Coverage | Traps hit | Invented keys | Unsupported | Resident GB | On GPU "
          "| Cold load | Time / case | Out tok/s | Out tok / case | Pareto |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]

    def f(v, fmt="{:.1f}", dash="-"):
        return dash if v is None else fmt.format(v)

    for i, m in enumerate(ranked, 1):
        a = aggs[m]
        q = f(a["quality"])
        if a["quality_range"]:
            q += f" ({a['quality_range'][0]:.0f}-{a['quality_range'][1]:.0f})"
        L.append(f"| {i} | {m} | {q} | {f(a['coverage'], '{:.0f}%')} "
                 f"| {a['traps_violated']}/{a['traps_total']} | {a['invented_keys']} | {a['unsupported']} "
                 f"| {f(a['resident_gb'])} | {f(a['gpu_pct'], '{:.0f}%')} | {fmt_s(a['cold_load_s'])} "
                 f"| {fmt_s(a['mean_case_s'])} | {f(a['output_tps'])} | {f(a['mean_output_tokens'], '{:.0f}')} "
                 f"| {'yes' if m in front else ''} |")
    L.append("")

    if runs:
        L += ["## Runs", "",
              "Resident GB includes the KV cache at each run's own num_ctx, so it reads higher for a model "
              "run at a larger context.", "",
              "| Model | Run | Started | num_ctx | num_predict | Repeats | Harness | Folder |",
              "|---|---|---|---|---|---|---|---|"]
        for m in ranked:
            ri = runs[m]
            L.append(f"| {m} | {ri['run_id']} | {ri['started']} | {ri['num_ctx']} | {ri['num_predict']} "
                     f"| {ri['repeats']} | {ri['harness_commit']} | {ri['folder']} |")
        L.append("")

    if notes:
        L += notes + [""]

    if not cfg["skip_judge"]:
        L += ["## Score per case", "", "| Model | " + " | ".join(c["id"] for c in cases) + " |",
              "|---|" + "---|" * len(cases)]
        for m in ranked:
            cs = aggs[m]["case_scores"]
            L.append(f"| {m} | " + " | ".join(f(cs.get(c["id"]), "{:.0f}") for c in cases) + " |")
        L.append("")
        L += ["Cases: " + "; ".join(f"{c['id']} {c['title']}" for c in cases), ""]

    warnings = []
    for r in records:
        a = aggs[r["model"]]
        for e in r["errors"]:
            warnings.append(f"{r['model']}: {e}")
        for c in r["cases"]:
            for fl in c.get("flags", []):
                warnings.append(f"{r['model']} {c['case']}: {fl}")
        if a["gpu_pct"] is not None and a["gpu_pct"] < 100:
            warnings.append(f"{r['model']}: only {a['gpu_pct']:.0f}% on GPU - part of the model ran on CPU, "
                            f"so its times reflect spill, not the model.")
        if r["resource"].get("resident_before_start"):
            warnings.append(f"{r['model']}: other models were resident at start "
                            f"({', '.join(r['resource']['resident_before_start'])}); timings may be contended.")
        if a["ungrounded"] or a["omitted"]:
            warnings.append(f"{r['model']}: judge had {a['ungrounded']} ungrounded and {a['omitted']} "
                            f"omitted verdicts (downgraded / defaulted).")
    if warnings:
        L += ["## Warnings", ""] + [f"- {w}" for w in warnings] + [""]

    L += ["## How to read this", "",
          f"- **Quality** = mean case score. Each case: (points found + 0.5 x partial - penalties) / points, "
          f"floored at 0. Penalties: {TRAP_PENALTY:g} per trap asserted, {INVENTED_KEY_PENALTY:g} per invented "
          f"ticket key (max {INVENTED_KEY_CAP:g}), {UNSUPPORTED_PENALTY:g} per other unsupported claim "
          f"(max {UNSUPPORTED_CAP:g}).",
          "- **Coverage** ignores penalties: the share of answer-key points the analysis made.",
          "- **Resident GB / On GPU** come from Ollama's /api/ps after the first case, at this run's num_ctx.",
          "- **Time / case** is Ollama's server-side duration minus load time. Cloud models report none.",
          "- With ~10 cases, differences under ~5 points are within judge and sampling noise. Use --repeats "
          "to measure it.", ""]
    text = "\n".join(L)
    (out_dir / "summary.md").write_text(text, encoding="utf-8")
    return text


def save_results(out_dir: Path, cfg: dict, records: list[dict]) -> None:
    payload = {"config": cfg, "results": [{**r, "aggregate": aggregate(r)} for r in records]}
    (out_dir / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


# ── Leaderboard across runs ──────────────────────────────────────────────────

# Scores are only comparable when these match. num_ctx, num_predict and
# repeats may differ: each model runs at the settings that suit it, and none of
# them changes a score unless the run was truncated, which the run's own
# warnings flag.
COMPARABLE_ON = ("cases_sha", "judge", "judge_effort", "judge_prompt_sha", "analyst_prompt_sha",
                 "temperature", "system_prompt")


def compare_runs(roots: list[Path], out_dir: Path, value_margin: float) -> str:
    """Rank the latest comparable run of every model found under roots."""
    entries, notes = [], []
    for root in roots:
        for path in sorted(root.rglob("results.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                cfg = data["config"]
            except (json.JSONDecodeError, KeyError) as e:
                notes.append(f"- `{path}`: unreadable ({e})")
                continue
            if cfg.get("skip_judge"):
                notes.append(f"- `{(Path(root.name) / path.parent.relative_to(root)).as_posix()}`: "
                             f"run {cfg.get('run_id')} was not judged")
                continue
            for rec in data.get("results", []):
                # Shown relative to the folder being compared, e.g. jira_analyst_results/run-4
                folder = (Path(root.name) / path.parent.relative_to(root)).as_posix()
                entries.append({"model": rec["model"], "rec": rec, "cfg": cfg, "folder": folder,
                                "fp": tuple(cfg.get(k) for k in COMPARABLE_ON)})
    if not entries:
        sys.exit(f"ERROR: no judged results.json found under {', '.join(map(str, roots))}")

    # The reference conditions are the ones most models were run under; on a
    # tie, the most recent run's. Anything else is listed, not silently mixed in.
    counts = {}
    for e in entries:
        counts.setdefault(e["fp"], set()).add(e["model"])
    newest = max(entries, key=lambda e: e["cfg"].get("started") or "")
    ref = max(counts, key=lambda fp: (len(counts[fp]), fp == newest["fp"]))
    ref_cfg = dict(zip(COMPARABLE_ON, ref))

    latest = {}
    for e in entries:
        if e["fp"] != ref:
            diff = [f"{k} {v!r} (ranked runs: {ref_cfg[k]!r})"
                    for k, v in zip(COMPARABLE_ON, e["fp"]) if v != ref_cfg[k]]
            notes.append(f"- {e['model']} in `{e['folder']}` (run {e['cfg'].get('run_id')}): "
                         f"different {'; '.join(diff)}")
            continue
        prev = latest.get(e["model"])
        if prev is None or (e["cfg"].get("started") or "") > (prev["cfg"].get("started") or ""):
            if prev:
                notes.append(f"- {e['model']}: run {prev['cfg'].get('run_id')} in `{prev['folder']}` "
                             f"superseded by run {e['cfg'].get('run_id')}")
            latest[e["model"]] = e
        else:
            notes.append(f"- {e['model']}: run {e['cfg'].get('run_id')} in `{e['folder']}` "
                         f"superseded by run {prev['cfg'].get('run_id')}")

    records = [{k: v for k, v in e["rec"].items() if k != "aggregate"} for e in latest.values()]
    runs = {m: {"run_id": e["cfg"].get("run_id"), "started": e["cfg"].get("started"),
                "num_ctx": e["cfg"].get("num_ctx"), "num_predict": e["cfg"].get("num_predict"),
                "repeats": e["cfg"].get("repeats"), "harness_commit": e["cfg"].get("harness_commit"),
                "folder": str(e["folder"])} for m, e in latest.items()}
    case_ids = {c["case"] for r in records for c in r["cases"]}
    cases = [c for c in load_cases() if c["id"] in case_ids]
    cfg = {**ref_cfg, "run_id": "leaderboard", "skip_judge": False, "value_margin": value_margin,
           "generated": datetime.now().isoformat(timespec="seconds"), "models": len(records)}
    out_dir.mkdir(parents=True, exist_ok=True)
    extra = (["## Not ranked", ""] + notes) if notes else None
    text = write_summary(out_dir, cfg, records, cases, title="# Jira Analyst Leaderboard",
                         settings=("generated", "models") + COMPARABLE_ON, runs=runs, notes=extra)
    # Deliberately not named results.json, so a leaderboard written inside a
    # results folder is never read back in as a run.
    (out_dir / "leaderboard.json").write_text(json.dumps(
        {"config": cfg, "runs": runs, "not_ranked": notes,
         "results": [{"model": r["model"], "aggregate": aggregate(r)} for r in records]}, indent=2),
        encoding="utf-8")
    return text


# ── Judge calibration ────────────────────────────────────────────────────────

NULL_ANALYSIS = ("## Summary\nThis ticket needs attention from the team.\n\n"
                 "## Next actions\n- Review the ticket in the next refinement session and follow up as needed.")


def synthetic_analyses(case: dict) -> dict:
    points = [cp for cp in case["answer_key"] if cp["kind"] != "trap"]
    traps = [cp for cp in case["answer_key"] if cp["kind"] == "trap"]
    perfect = "## Analysis\n" + "\n".join(
        f"- {'Inference (not confirmed in the ticket): ' if cp['kind'] == 'inference' else ''}{cp['expect']}"
        for cp in points)
    trap_text = perfect + "\n\n## Additional notes\n" + "\n".join(f"- {cp['claim']}" for cp in traps if cp.get("claim"))
    return {"perfect": perfect, "null": NULL_ANALYSIS, "trap": trap_text}


def calibrate(ep: Endpoints, cfg: dict, cases: list[dict], case_texts: dict, judge_prompt: str,
              out_dir: Path) -> None:
    """Grade analyses whose right answers are known, as the scorer benchmark
    does for the review scorer. Perfect should score ~100 with no traps hit,
    null ~0, and trap should hit every trap. This screens out a broken judge;
    it does not prove a working one is well calibrated on real prose."""
    cdir = out_dir / "calibration"
    cdir.mkdir(parents=True, exist_ok=True)
    rows = []
    for case in cases:
        for kind, text in synthetic_analyses(case).items():
            print(f"   {case['id']} {kind} ...", end=" ", flush=True)
            try:
                judged = judge_analysis(ep, cfg, judge_prompt, case, case_texts[case["id"]], text)
            except Exception as e:
                print(f"ERROR: {e}")
                rows.append({"case": case["id"], "kind": kind, "error": str(e)})
                continue
            (cdir / f"{case['id']}.{kind}.judge.json").write_text(json.dumps(judged, indent=2), encoding="utf-8")
            s = score_case(judged, [])
            traps_with_claims = sum(1 for cp in case["answer_key"] if cp["kind"] == "trap" and cp.get("claim"))
            rows.append({"case": case["id"], "kind": kind, **s, "traps_with_claims": traps_with_claims,
                         "ungrounded": len(judged["judge_notes"]["ungrounded"])})
            print(f"coverage {s['coverage']:.0f}%, traps hit {len(s['traps_violated'])}/{s['traps']}, "
                  f"unsupported {s['unsupported_claims']}")
    L = [f"# Judge calibration - {cfg['judge']} (effort {cfg['judge_effort']})", "",
         "| Case | Perfect coverage | Perfect traps hit | Null coverage | Null traps hit | Trap analysis: traps caught | Ungrounded |",
         "|---|---|---|---|---|---|---|"]
    by = {(r["case"], r["kind"]): r for r in rows}
    for case in cases:
        p, n, t = (by.get((case["id"], k), {}) for k in ("perfect", "null", "trap"))
        def cov(r): return f"{r['coverage']:.0f}%" if "coverage" in r else "ERR"
        def hit(r): return f"{len(r['traps_violated'])}/{r['traps']}" if "traps" in r else "ERR"
        caught = f"{len(t['traps_violated'])}/{t['traps_with_claims']}" if "traps" in t else "ERR"
        ung = sum(r.get("ungrounded", 0) for r in (p, n, t))
        L.append(f"| {case['id']} | {cov(p)} | {hit(p)} | {cov(n)} | {hit(n)} | {caught} | {ung} |")
    L += ["", "Expected: perfect ~100% coverage and 0 traps hit; null ~0% and 0 traps hit; "
          "trap analysis catches every trap. Perfect is built from the answer key's own wording, so it is "
          "an easy test: failing it means the judge or the key is broken."]
    (out_dir / "calibration.md").write_text("\n".join(L), encoding="utf-8")
    (out_dir / "calibration.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("\n" + "\n".join(L))


# ── Main ─────────────────────────────────────────────────────────────────────

def git_commit() -> str:
    try:
        head = (ROOT / ".git" / "HEAD").read_text().strip()
        if head.startswith("ref: "):
            return (ROOT / ".git" / head[5:]).read_text().strip()[:7]
        return head[:7]
    except Exception:
        return os.environ.get("GITHUB_SHA", "?")[:7] or "?"


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", default=os.environ.get("JIRA_BENCH_MODELS", ""),
                    help="Comma-separated model tags; per-model think as model=value or model=none")
    ap.add_argument("--think", default="", help="Default Ollama think value for every model")
    ap.add_argument("--cases", default="", help="Comma-separated case ids (default: all)")
    ap.add_argument("--num-ctx", type=int, default=32768)
    ap.add_argument("--num-predict", type=int, default=4096)
    ap.add_argument("--temperature", type=float, default=0.3)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--repeats", type=int, default=1)
    ap.add_argument("--system-prompt", default="file", choices=("file", "modelfile"),
                    help="'file' sends jira_benchmark/analyst_system_prompt.md to every model (default); "
                         "'modelfile' sends none, so each model's own SYSTEM applies")
    ap.add_argument("--judge", default="claude-sonnet-5")
    ap.add_argument("--judge-effort", default="high")
    ap.add_argument("--judge-num-ctx", type=int, default=65536, help="Only for an Ollama judge")
    # A reasoning judge spends this budget on thinking before it writes any
    # JSON, and an Ollama judge that runs out returns empty content -- which
    # is how minimax-m3:cloud failed all 54 calls at the old fixed 8192.
    # 16384 matches what the Claude judge path allows itself (16000).
    ap.add_argument("--judge-num-predict", type=int, default=16384,
                    help="Only for an Ollama judge; raise it for a reasoning judge")
    ap.add_argument("--judge-think", default="", help="Only for an Ollama judge")
    ap.add_argument("--value-margin", type=float, default=5.0,
                    help="Best-value pick: smallest model within this many points of the best")
    ap.add_argument("--skip-judge", action="store_true")
    ap.add_argument("--keep-loaded", action="store_true", help="Do not unload each model after its run")
    ap.add_argument("--calibrate-judge", action="store_true")
    ap.add_argument("--rejudge", default="", help="Re-grade the analyses in an earlier run directory")
    ap.add_argument("--list-cases", action="store_true")
    ap.add_argument("--compare", nargs="+", default=None, metavar="DIR",
                    help="Build a leaderboard from every judged results.json under these folders "
                         "(no model or judge calls)")
    ap.add_argument("--out", default="", help="Output directory (default jira_benchmark_results/run-<id>)")
    args = ap.parse_args()

    if args.compare:
        out = Path(args.out) if args.out else ROOT / "jira_benchmark_results" / "leaderboard"
        print(compare_runs([Path(p) for p in args.compare], out, args.value_margin))
        print(f"\nWritten to {out}")
        return

    cases = load_cases([c for c in args.cases.split(",")] if args.cases else None)
    case_texts = {c["id"]: render_case(c) for c in cases}
    prefixes = project_prefixes(cases)
    analyst_prompt = ANALYST_PROMPT_FILE.read_text(encoding="utf-8").strip()
    judge_prompt = JUDGE_PROMPT_FILE.read_text(encoding="utf-8").strip()
    system_for_models = analyst_prompt if args.system_prompt == "file" else ""

    budget = args.num_ctx - args.num_predict - PROMPT_OVERHEAD_TOKENS
    img_tokens = {c["id"]: sum(image_tokens(p) for p in case_images(c)) for c in cases}
    sizes = {cid: int((len(t) + len(system_for_models)) / CHARS_PER_TOKEN) + img_tokens[cid]
             for cid, t in case_texts.items()}
    if args.list_cases:
        for c in cases:
            pts = sum(cp["kind"] != "trap" for cp in c["answer_key"])
            trs = sum(cp["kind"] == "trap" for cp in c["answer_key"])
            imgs = case_images(c)
            note = f"  [{len(imgs)} image, ~{img_tokens[c['id']]} tok, needs vision]" if imgs else ""
            print(f"{c['id']}  ~{sizes[c['id']]:>6} tok  {pts} points, {trs} traps  {c['title']}{note}")
        print(f"Budget at num_ctx {args.num_ctx} / num_predict {args.num_predict}: {budget} tokens of input")
        return

    run_id = os.environ.get("RUN_NUMBER") or datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.out) if args.out else ROOT / "jira_benchmark_results" / f"run-{run_id}"
    out_dir.mkdir(parents=True, exist_ok=True)
    ep = Endpoints()
    cfg = {
        "run_id": run_id, "started": datetime.now().isoformat(timespec="seconds"),
        "harness_commit": git_commit(),
        "num_ctx": args.num_ctx, "num_predict": args.num_predict, "temperature": args.temperature,
        "seed": args.seed, "repeats": args.repeats, "think_default": args.think or None,
        "system_prompt": args.system_prompt,
        "analyst_prompt_sha": sha12(analyst_prompt) if system_for_models else "modelfile",
        "judge": args.judge, "judge_effort": args.judge_effort, "judge_num_ctx": args.judge_num_ctx,
        "judge_think": args.judge_think, "judge_prompt_sha": sha12(judge_prompt),
        "judge_num_predict": args.judge_num_predict,
        "cases_sha": sha12("".join(c["_sha"] for c in cases)),
        "value_margin": args.value_margin, "skip_judge": args.skip_judge, "keep_loaded": args.keep_loaded,
    }

    if args.calibrate_judge:
        print(f"Calibrating judge {args.judge} on {len(cases)} cases x 3 synthetic analyses")
        cfg["skip_judge"] = False
        calibrate(ep, cfg, cases, case_texts, judge_prompt, out_dir)
        return

    if args.rejudge:
        src = Path(args.rejudge)
        prev = json.loads((src / "results.json").read_text(encoding="utf-8"))
        for k in ("num_ctx", "num_predict", "temperature", "seed", "repeats", "system_prompt",
                  "analyst_prompt_sha", "harness_commit"):
            cfg[k] = prev["config"].get(k)
        cfg["rejudged_from"] = str(src)
        cfg["skip_judge"] = False
        by_id = {c["id"]: c for c in cases}
        records = []
        for rec in prev["results"]:
            print(f"\n== Re-judging {rec['model']}")
            new = {k: rec[k] for k in ("model", "think", "resource")}
            new["cases"], new["errors"] = [], []
            for entry in rec["cases"]:
                case = by_id.get(entry["case"])
                if case is None:
                    continue
                tag = entry["case"] + (f".r{entry['repeat']}" if cfg["repeats"] > 1 else "")
                apath = src / slug(rec["model"]) / f"{tag}.analysis.md"
                keep = {k: entry[k] for k in ("case", "repeat", "metrics", "flags") if k in entry}
                if not apath.exists() or "metrics" not in entry:
                    new["cases"].append({**keep, "error": entry.get("error", "no analysis"), "score": 0.0})
                    new["errors"].append(f"{tag}: {entry.get('error', 'no analysis')}")
                    continue
                analysis = apath.read_text(encoding="utf-8")
                keep["invented_keys"] = invented_keys(analysis, case_texts[case["id"]], prefixes)
                print(f"   {tag} ...", end=" ", flush=True)
                try:
                    judged = judge_analysis(ep, cfg, judge_prompt, case, case_texts[case["id"]], analysis)
                    mdir = out_dir / slug(rec["model"])
                    mdir.mkdir(parents=True, exist_ok=True)
                    (mdir / f"{tag}.judge.json").write_text(json.dumps(judged, indent=2), encoding="utf-8")
                    keep.update(score_case(judged, keep["invented_keys"]))
                    keep["judge_notes"] = judged["judge_notes"]
                    print(f"{keep['score']:.0f}/100")
                except Exception as e:
                    print(f"judge ERROR: {e}")
                    keep["judge_error"] = str(e)
                    new["errors"].append(f"{tag}: judge failed: {e}")
                new["cases"].append(keep)
            records.append(new)
            save_results(out_dir, cfg, records)
        print("\n" + write_summary(out_dir, cfg, records, cases))
        return

    models = parse_models(args.models, args.think)
    if not models:
        sys.exit("ERROR: no models given (--models or JIRA_BENCH_MODELS)")
    too_big = {cid: n for cid, n in sizes.items() if n > budget}
    if too_big:
        sys.exit(f"ERROR: case(s) {too_big} estimated over the {budget}-token input budget "
                 f"(num_ctx {args.num_ctx} - num_predict {args.num_predict} - {PROMPT_OVERHEAD_TOKENS}). "
                 f"Ollama would silently drop the start of the prompt. Raise --num-ctx or use --cases.")
    if not args.skip_judge and Endpoints.is_claude(args.judge) and not ep.anthropic_key:
        sys.exit("ERROR: judge is a Claude model but ANTHROPIC_API_KEY is unset (or pass --skip-judge).")

    print(f"Models: {[m for m, _ in models]}")
    print(f"Cases: {len(cases)} ({', '.join(c['id'] for c in cases)}), largest ~{max(sizes.values())} tok; "
          f"judge: {'none' if args.skip_judge else args.judge}")
    print(f"Output: {out_dir}")
    records = []
    for model, think in models:
        print(f"\n== {model}" + (f" (think={think})" if think else ""))
        records.append(run_model(ep, cfg, model, think, cases, case_texts, system_for_models,
                                 judge_prompt, prefixes, out_dir))
        # Rewritten after every model, so a crash late in a long run keeps
        # everything already measured.
        save_results(out_dir, cfg, records)
    print("\n" + write_summary(out_dir, cfg, records, cases))


if __name__ == "__main__":
    main()
