#!/usr/bin/env python3
"""AI code review + ISSUES.md scorecard.

Ports .github/workflows/ai_code_review.yml into a single script so it can run
locally from a git pre-commit hook. Collects every tracked source file under
SampleBankingApp/, asks an Ollama-hosted model for a peer review, asks a
(possibly different) Ollama model to score that review against ISSUES.md,
then writes review.md, issues_scorecard.md, metrics.md, and metrics.json into
the chosen output directory.

Optional env vars (defaults target Ollama's hosted cloud and the
`glm-5.2:cloud` model; override OLLAMA_URL/OLLAMA_MODEL to run elsewhere):
  OLLAMA_URL                              On-prem Ollama endpoint used for any
                                          model tag NOT ending in ':cloud'.
                                          Default: https://ollama.com
  OLLAMA_CLOUD_URL                        Hosted endpoint used for ':cloud'
                                          model tags. Default: https://ollama.com
  OLLAMA_API_KEY                          Bearer token; sent only to the cloud
                                          endpoint. Required for ':cloud' models.
  OLLAMA_MODEL                            Default: glm-5.2:cloud
  AI_ASSISTANT_OLLAMA_MODEL_REVIEWER      Scoring model. Default: OLLAMA_MODEL
  AI_ASSISTANT_MODEL_NUM_CTX              Default: 32768
  AI_ASSISTANT_MODEL_NUM_PREDICT          Default: 16384
  AI_ASSISTANT_MODEL_TEMPERATURE          Default: 0.3
  AI_REVIEW_OUTPUT_DIR                    Default: .ai-review
  AI_REVIEW_SOURCE_GLOB_ROOT              Default: SampleBankingApp/
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SOURCE_EXT = re.compile(r"\.(cs|json|csproj|yml|yaml|config|xml|html|css|js|ts|md)$", re.IGNORECASE)
EXCLUDE_RE = re.compile(r"(\.min\.js|\.min\.css|package-lock\.json|yarn\.lock|\.lock|\.sum)$", re.IGNORECASE)


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, **kwargs)


def _iter_source_files_fs(source_root: str) -> list[str]:
    """Filesystem walk under source_root (repo-root-relative). Used when the
    directory is not git-tracked, e.g. a scratch tree produced by the patcher.
    Returns forward-slash relative paths for stable prompt output.
    """
    root_abs = (REPO_ROOT / source_root).resolve()
    if not root_abs.exists():
        return []
    files: list[str] = []
    for p in sorted(root_abs.rglob("*")):
        if not p.is_file():
            continue
        rel_posix = p.relative_to(REPO_ROOT).as_posix()
        if not SOURCE_EXT.search(rel_posix) or EXCLUDE_RE.search(rel_posix):
            continue
        files.append(rel_posix)
    return files


def _iter_source_files_git(source_root: str) -> list[str]:
    res = run(["git", "ls-files", "--", source_root], cwd=REPO_ROOT)
    if res.returncode != 0:
        print(f"ERROR: git ls-files failed: {res.stderr}", file=sys.stderr)
        sys.exit(1)
    return [
        f for f in res.stdout.splitlines()
        if f and SOURCE_EXT.search(f) and not EXCLUDE_RE.search(f)
    ]


def collect_branch_content(source_root: str) -> tuple[str, int]:
    """Concatenate all reviewable source files under source_root.

    Uses `git ls-files` by default so review scope matches what's committed.
    Set AI_REVIEW_USE_FS_WALK=1 to walk the filesystem instead — required when
    reviewing an untracked scratch tree (e.g. the patcher's output directory).
    """
    if os.environ.get("AI_REVIEW_USE_FS_WALK", "").strip() in {"1", "true", "yes"}:
        files = _iter_source_files_fs(source_root)
    else:
        files = _iter_source_files_git(source_root)

    chunks: list[str] = []
    for rel in files:
        path = REPO_ROOT / rel
        try:
            body = path.read_text(encoding="utf-8", errors="replace")
        except (OSError, UnicodeError) as exc:
            print(f"WARN: could not read {rel}: {exc}", file=sys.stderr)
            continue
        # Line-numbered, matching `nl -ba` in ai_code_review.yml -- without this the
        # model invents the Line column and the scorer cannot verify citations.
        numbered = "\n".join(
            f"{i:6d}\t{line}" for i, line in enumerate(body.splitlines(), 1)
        )
        chunks.append(f"### File: {rel}\n```\n{numbered}\n```\n")

    content = "\n".join(chunks)
    return content, len(files)


def resolve_endpoint(model: str) -> tuple[str, str | None]:
    """Pick the Ollama base URL + API key for a given model tag.

    The routing rule is dead simple: the model tag is the ONLY signal.
      - Model ending in ':cloud' -> OLLAMA_CLOUD_URL (default https://ollama.com)
        with OLLAMA_API_KEY as a Bearer token.
      - Any other model tag       -> OLLAMA_URL (must be set explicitly), no
        auth header. Local Ollama rejects Authorization headers with 400, so
        the key is deliberately NOT forwarded to on-prem endpoints.

    This lets one run mix a cloud patcher (e.g. glm-5.2:cloud) with a local
    reviewer (e.g. Qwen3.6-27B:Q4_K_S) without either clobbering the other.

    Raises RuntimeError if the configuration for the requested model is
    missing — we fail loudly rather than silently sending a local model
    request to the cloud (or vice versa).
    """
    cloud_url = os.environ.get("OLLAMA_CLOUD_URL", "https://ollama.com").strip().rstrip("/")
    onprem_url = os.environ.get("OLLAMA_URL", "").strip().rstrip("/")
    api_key = os.environ.get("OLLAMA_API_KEY", "").strip() or None

    if model.endswith(":cloud"):
        if not cloud_url:
            raise RuntimeError(
                f"Model '{model}' is a cloud model but OLLAMA_CLOUD_URL is empty."
            )
        if not api_key:
            raise RuntimeError(
                f"Model '{model}' requires the hosted Ollama cloud, but "
                "OLLAMA_API_KEY is not set."
            )
        return cloud_url, api_key

    if not onprem_url:
        raise RuntimeError(
            f"Model '{model}' is a local (on-prem) model but OLLAMA_URL is not "
            "set. Set OLLAMA_URL to your Ollama server (e.g. "
            "http://192.168.10.100:11434), or use a ':cloud' model tag if you "
            "meant to hit the hosted API."
        )
    return onprem_url, None


def ollama_chat(base_url: str, payload: dict, payload_path: Path, label: str,
                api_key: str | None = None) -> dict:
    """POST a chat request to Ollama via curl and return the parsed response."""
    payload_path.write_text(json.dumps(payload), encoding="utf-8")
    print(f"Calling {base_url}/api/chat — {label} (model: {payload['model']}) …")

    cmd = [
        "curl", "-s", "--show-error", "--fail-with-body", "--max-time", "7200",
        "-X", "POST", f"{base_url}/api/chat",
        "-H", "Content-Type: application/json",
    ]
    if api_key:
        cmd += ["-H", f"Authorization: Bearer {api_key}"]
    cmd += ["-d", f"@{payload_path}"]

    res = run(cmd)
    if res.returncode != 0:
        print(
            f"ERROR: curl failed (exit {res.returncode})\n"
            f"stderr: {res.stderr}\n"
            f"body  : {res.stdout[:2000]}",
            file=sys.stderr,
        )
        sys.exit(1)
    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Could not parse Ollama response: {exc}", file=sys.stderr)
        print(f"Raw output (first 500 chars): {res.stdout[:500]}", file=sys.stderr)
        sys.exit(1)


REPO_ROOT_PATH = Path(__file__).resolve().parent.parent

# The review instructions and the scoring preamble are the SAME files the GitHub
# workflows use. They used to be duplicated literals in this module and had drifted
# badly: the review prompt predated the dead-code enumeration procedure, and the
# scoring preamble was 1,236 chars behind. Reading them means the patcher grades on
# the same instrument as ai_code_review.yml.
def _shared_text(name: str) -> str:
    path = REPO_ROOT_PATH / name
    if not path.exists():
        print(f"ERROR: {name} not found at {path}. It is shared with the GitHub "
              f"workflows and must be present in the checkout.", file=sys.stderr)
        sys.exit(1)
    return path.read_text(encoding="utf-8")


REVIEW_PROMPT_TEMPLATE = _shared_text("review_prompt.md")
SCORING_PREAMBLE = _shared_text("scorer_prompt.md")

# Scorecard post-processing, shared with the workflows for the same reason.
sys.path.insert(0, str(REPO_ROOT_PATH))
from scorecard_tools import (  # noqa: E402
    count_table_statuses,
    drop_duplicate_ids,
    enforce_note_grounding,
    hedge_check,
    reconcile_summary_line,
    spot_check,
    warn_repeated_notes,
)


# Used by strip_thinking() for models that emit inline <think> tags rather than
# Ollama's separate message.thinking field.
_THINK_BLOCK = re.compile(r"<think>.*?</think>\s*", re.DOTALL | re.IGNORECASE)


def reasoning_controls(prefix: str) -> tuple[list[dict], object]:
    """Build the system message and `think` value for one model role.

    prefix is AI_ASSISTANT_MODEL, AI_ASSISTANT_SCORER or AI_PATCH_MODEL. Both knobs
    are blank by default so the model's own Modelfile applies -- the benchmark
    default. Returns ([] or [system message], think value or None).

    These payloads previously hardcoded `"think": False`, which did not merely omit
    the control: it actively DISABLED reasoning for every model in the pipeline.
    Qwen3.8-27B scores 71.4% with thinking off against ~96% with it on.
    """
    messages: list[dict] = []
    reasoning = (os.environ.get(f"{prefix}_REASONING") or "").strip()
    if reasoning:
        # A system message replaces the Modelfile SYSTEM block wholesale, so the
        # assistant line must be reproduced alongside the level.
        messages.append({
            "role": "system",
            "content": f"Reasoning strength: {reasoning}\n\nYou are a helpful assistant.",
        })
    raw = (os.environ.get(f"{prefix}_THINK") or "").strip()
    think: object = None
    if raw:
        low = raw.lower()
        think = True if low == "true" else False if low == "false" else raw
    if reasoning or raw:
        print(f"  {prefix}: reasoning={reasoning or '(model default)'} "
              f"think={think if raw else '(unset)'}")
    return messages, think


def strip_thinking(text: str) -> str:
    """Remove Qwen3-style <think>…</think> blocks (including empty ones)."""
    return _THINK_BLOCK.sub("", text).lstrip()


def ns_to_s(ns: int | None) -> float:
    return round(ns / 1e9, 1) if ns else 0.0


def tps(tokens: int | None, duration_ns: int | None) -> float:
    return round(tokens / max(duration_ns / 1e9, 0.001), 1) if tokens and duration_ns else 0.0


def fmt_s(secs: float) -> str:
    if secs >= 60:
        return f"{int(secs // 60)}m {secs % 60:.0f}s"
    return f"{secs:.1f}s"


def main() -> int:
    # `os.environ.get(k, default)` returns the default only when k is missing;
    # an env var set to '' (as GitHub Actions passes for unset inputs) would
    # otherwise slip through as an empty model tag. Use `or` to fall back.
    review_model = (os.environ.get("OLLAMA_MODEL") or "").strip() or "glm-5.2:cloud"
    scoring_model = (os.environ.get("AI_ASSISTANT_OLLAMA_MODEL_REVIEWER") or "").strip() or review_model

    try:
        review_url, review_key = resolve_endpoint(review_model)
        scoring_url, scoring_key = resolve_endpoint(scoring_model)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    num_ctx = int(os.environ.get("AI_ASSISTANT_MODEL_NUM_CTX", "32768"))
    num_predict = int(os.environ.get("AI_ASSISTANT_MODEL_NUM_PREDICT", "16384"))
    temperature = float(os.environ.get("AI_ASSISTANT_MODEL_TEMPERATURE", "0.3"))
    source_root = os.environ.get("AI_REVIEW_SOURCE_GLOB_ROOT", "SampleBankingApp/")

    output_dir = Path(os.environ.get("AI_REVIEW_OUTPUT_DIR", str(REPO_ROOT / ".ai-review")))
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    branch = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=REPO_ROOT).stdout.strip() or "(detached)"
    head = run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT).stdout.strip() or "(no-commit)"
    commit_sha = head + " (pre-commit working tree)"

    print(f"Collecting tracked source files under {source_root} …")
    diff, file_count = collect_branch_content(source_root)
    if not diff:
        print("No reviewable files found — skipping AI review.")
        return 0
    print(f"Collected {file_count} files ({len(diff)} bytes).")

    chars_per_token = 2.5
    instruction_chars = len(REVIEW_PROMPT_TEMPLATE.format(
        branch_name=branch, commit_sha=commit_sha, diff="", truncation_note=""))
    available_tokens = num_ctx - num_predict - 500
    max_diff_chars = max(0, int(available_tokens * chars_per_token) - instruction_chars)
    truncated = len(diff) > max_diff_chars
    if truncated:
        diff = diff[:max_diff_chars]
        truncation_note = "[Note: the source listing below was truncated to fit the context window]"
    else:
        truncation_note = ""

    print(f"Context: {num_ctx} tokens, instruction overhead: {instruction_chars} chars, "
          f"diff budget: {max_diff_chars} chars, actual diff: {len(diff)} chars, truncated: {truncated}")

    review_prompt = REVIEW_PROMPT_TEMPLATE.format(
        branch_name=branch, commit_sha=commit_sha, diff=diff, truncation_note=truncation_note,
    )

    _msgs, _think = reasoning_controls("AI_ASSISTANT_MODEL")
    review_payload = {
        "model": review_model,
        "messages": _msgs + [{"role": "user", "content": review_prompt}],
        "stream": False,
        # num_ctx was computed and reported but never SENT: Ollama fell back to its
        # server default (~4k), so the model saw a fraction of the source listing the
        # budget maths had sized for.
        "options": {"temperature": temperature, "num_predict": num_predict,
                    "num_ctx": num_ctx},
    }
    if _think is not None:
        review_payload["think"] = _think
    review_data = ollama_chat(review_url, review_payload, output_dir / "payload.json", "review", review_key)
    review = strip_thinking((review_data.get("message") or {}).get("content", "")).strip()
    if not review:
        print("ERROR: Ollama returned an empty review.", file=sys.stderr)
        return 1
    (output_dir / "review.md").write_text(review, encoding="utf-8")

    review_metrics = {
        "model": review_model,
        "total_duration_s": ns_to_s(review_data.get("total_duration")),
        "load_duration_s": ns_to_s(review_data.get("load_duration")),
        "prompt_tokens": review_data.get("prompt_eval_count", 0),
        "output_tokens": review_data.get("eval_count", 0),
        "output_token_limit": num_predict,
        "prompt_tps": tps(review_data.get("prompt_eval_count"), review_data.get("prompt_eval_duration")),
        "output_tps": tps(review_data.get("eval_count"), review_data.get("eval_duration")),
        "context_window": num_ctx,
        "context_utilization_pct": round(
            (review_data.get("prompt_eval_count", 0) + review_data.get("eval_count", 0)) / num_ctx * 100, 1
        ),
        "content_truncated": truncated,
        "done_reason": review_data.get("done_reason", ""),
    }
    print(f"Review metrics: {review_metrics['total_duration_s']}s total | "
          f"prompt {review_metrics['prompt_tokens']:,} tok @ {review_metrics['prompt_tps']} tok/s | "
          f"output {review_metrics['output_tokens']:,} tok @ {review_metrics['output_tps']} tok/s | "
          f"context {review_metrics['context_utilization_pct']}% used | "
          f"done_reason={review_metrics['done_reason']}")

    issues_path = REPO_ROOT / "ISSUES.md"
    if not issues_path.exists():
        print(f"ERROR: ISSUES.md not found at {issues_path} — cannot score.", file=sys.stderr)
        return 1
    issues = issues_path.read_text(encoding="utf-8", errors="replace")

    max_chars = num_ctx * 2
    full_prompt = SCORING_PREAMBLE + issues + "\n\n---\n## AI Review Output\n\n" + review + "\n"
    review_for_scoring = review
    if len(full_prompt) > max_chars:
        overhead = len(SCORING_PREAMBLE) + len(issues) + 50
        review_for_scoring = review[: max(0, max_chars - overhead)]
    scoring_prompt = SCORING_PREAMBLE + issues + "\n\n---\n## AI Review Output\n\n" + review_for_scoring + "\n"

    # The scorer gets its own budget and temperature, matching ai_code_review.yml --
    # it is the measuring instrument and must not move when the reviewer is retuned.
    scorer_num_predict = int(os.environ.get("AI_ASSISTANT_SCORER_NUM_PREDICT", "24000"))
    scorer_temperature = float(os.environ.get("AI_ASSISTANT_SCORER_TEMPERATURE", "0.3"))
    _smsgs, _sthink = reasoning_controls("AI_ASSISTANT_SCORER")
    scoring_payload = {
        "model": scoring_model,
        "messages": _smsgs + [{"role": "user", "content": scoring_prompt}],
        "stream": False,
        "options": {"temperature": scorer_temperature,
                    "num_predict": scorer_num_predict,
                    "num_ctx": num_ctx},
    }
    if _sthink is not None:
        scoring_payload["think"] = _sthink
    scoring_data = ollama_chat(
        scoring_url, scoring_payload, output_dir / "scoring_payload.json", "scoring", scoring_key,
    )
    scorecard = strip_thinking((scoring_data.get("message") or {}).get("content", "")).strip()
    if not scorecard:
        print("ERROR: Ollama returned an empty scorecard.", file=sys.stderr)
        return 1

    scorecard = re.sub(
        r"^#\s*AI\s+Review\s+Scorecard\s*\n+", "", scorecard, count=1, flags=re.IGNORECASE,
    ).lstrip()

    # Same chain ai_code_review.yml runs, in the same order: dedupe, drop Notes the
    # review cannot support, then recount so the summary matches the tables.
    grounding_mode = (os.environ.get("AI_ASSISTANT_SCORECARD_GROUNDING", "enforce")
                      .strip().lower())
    if grounding_mode not in ("enforce", "warn", "off"):
        print(f"WARN: unknown grounding mode {grounding_mode!r}; using 'enforce'.",
              file=sys.stderr)
        grounding_mode = "enforce"

    body = drop_duplicate_ids(scorecard)
    body, grounding_downgrades = enforce_note_grounding(body, review, grounding_mode)
    body = reconcile_summary_line(body)
    warn_repeated_notes(body)
    rf, rp, rm = count_table_statuses(body)
    row_total = rf + rp + rm

    spot_rows, miscredits, undercredits, unsupported = spot_check(body, review)
    hedged = hedge_check(body)
    adjusted_found = rf - len(miscredits)
    found_floor = adjusted_found - len([h for h in hedged if h[0] not in miscredits])

    if miscredits:
        print(
            f"WARN: {len(miscredits)} row(s) rated Found whose target string never appears "
            f"in the review: {', '.join(miscredits)}. Adjusted Found: {adjusted_found}.",
            file=sys.stderr,
        )
    if unsupported:
        print(
            f"WARN: {len(unsupported)} row(s) rated Partial whose target string never "
            f"appears in the review: {', '.join(unsupported)}. A Partial on an "
            f"unmentioned issue is a Missed, so Missed={rm} is understated.",
            file=sys.stderr,
        )
    if hedged:
        print(
            f"WARN: {len(hedged)} row(s) rated Found concede in their own Note that the "
            f"review fell short ({', '.join(h[0] for h in hedged)}). Floor: {found_floor}.",
            file=sys.stderr,
        )
    if row_total != 70:
        print(
            f"WARN: Scorecard has {row_total} table data rows; expected exactly 70 "
            f"(69 IDs C1-CF9 plus one UT row for Missing Unit Tests).",
            file=sys.stderr,
        )

    header = (
        f"# AI Review Scorecard\n\n"
        f"> **Branch:** `{branch}` &nbsp;·&nbsp; **Commit:** `{head[:7]}`\n\n"
    )
    if miscredits:
        header += (
            f"> ⚠ **{len(miscredits)} row(s) rated Found name a target that never appears "
            f"in the review** ({', '.join(miscredits)}). Adjusted Found: "
            f"**{adjusted_found}** of {row_total}.\n\n"
        )
    spot_section = (
        "\n---\n\n## Evidence Spot-Check\n\n"
        "| ID | Status | Target string | In review | Verdict |\n|---|---|---|---|---|\n"
        + "".join(f"| {r[0]} | {r[1]} | `{r[2]}` | {r[3]} | {r[4]} |\n" for r in spot_rows)
        + (f"\n**Adjusted Found: {adjusted_found} of {row_total}**"
           f" ({rf} reported, less {len(miscredits)} mis-credited).\n"
           if miscredits else "\nNo mis-credits detected in the watchlist.\n")
        + (f"\n> **{len(unsupported)} row(s) rated `Partial` whose target string appears "
           f"NOWHERE in the review** ({', '.join(unsupported)}). A Partial on an "
           f"unmentioned issue is a Missed; the reported Missed count is "
           f"correspondingly understated.\n"
           if unsupported else "")
    )
    (output_dir / "issues_scorecard.md").write_text(
        header + body + spot_section, encoding="utf-8")

    scoring_metrics = {
        "model": scoring_model,
        "total_duration_s": ns_to_s(scoring_data.get("total_duration")),
        "load_duration_s": ns_to_s(scoring_data.get("load_duration")),
        "prompt_tokens": scoring_data.get("prompt_eval_count", 0),
        "output_tokens": scoring_data.get("eval_count", 0),
        "prompt_tps": tps(scoring_data.get("prompt_eval_count"), scoring_data.get("prompt_eval_duration")),
        "output_tps": tps(scoring_data.get("eval_count"), scoring_data.get("eval_duration")),
        "done_reason": scoring_data.get("done_reason", ""),
    }
    score_result = {
        "found": rf, "partial": rp, "missed": rm,
        "found_adjusted": adjusted_found,
        "found_floor": found_floor,
        "spotcheck_miscredits": miscredits,
        "spotcheck_unsupported_partials": unsupported,
        "hedged_rows": [h[0] for h in hedged],
        "grounding_downgrades": len(grounding_downgrades),
        "total": row_total,
        "score_pct": round(rf / max(row_total, 1) * 100, 1),
    }
    metrics = {
        "review": review_metrics,
        "scoring": scoring_metrics,
        "score": score_result,
        "combined_total_s": round(review_metrics["total_duration_s"] + scoring_metrics["total_duration_s"], 1),
    }
    (output_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    out_tokens = review_metrics["output_tokens"]
    out_limit = review_metrics["output_token_limit"]
    done_r = review_metrics["done_reason"]
    done_s = scoring_metrics["done_reason"]
    metrics_lines = [
        "# AI Model Performance Metrics\n",
        f"> **Branch:** `{branch}` &nbsp;·&nbsp; **Commit:** `{head[:7]}`\n",
        "",
        "## Score",
        f"Total: {score_result['found']} Found / {score_result['partial']} Partial / "
        f"{score_result['missed']} Missed out of {score_result['total']} issues "
        f"({score_result['score_pct']}% Found)",
        "",
        "## Review Performance",
        f"**Model:** `{review_metrics['model']}`\n",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total time | {fmt_s(review_metrics['total_duration_s'])} |",
        f"| Model load time | {fmt_s(review_metrics['load_duration_s'])} |",
        f"| Inference time | {fmt_s(review_metrics['total_duration_s'] - review_metrics['load_duration_s'])} |",
        f"| Prompt tokens | {review_metrics['prompt_tokens']:,} |",
        f"| Output tokens | {out_tokens:,} of {out_limit:,} limit |",
        f"| Output speed | {review_metrics['output_tps']} tok/s |",
        f"| Prompt speed | {review_metrics['prompt_tps']} tok/s |",
        f"| Context window | {review_metrics['context_window']:,} tokens |",
        f"| Context utilization | {review_metrics['context_utilization_pct']}% |",
        f"| Content truncated | {'**Yes**' if truncated else 'No'} |",
        f"| Completed naturally | {'No (hit token limit)' if done_r == 'length' else 'Yes'} |",
        "",
        "## Scoring Performance",
        f"**Model:** `{scoring_metrics['model']}`\n",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total time | {fmt_s(scoring_metrics['total_duration_s'])} |",
        f"| Model load time | {fmt_s(scoring_metrics['load_duration_s'])} |",
        f"| Prompt tokens | {scoring_metrics['prompt_tokens']:,} |",
        f"| Output tokens | {scoring_metrics['output_tokens']:,} |",
        f"| Output speed | {scoring_metrics['output_tps']} tok/s |",
        f"| Prompt speed | {scoring_metrics['prompt_tps']} tok/s |",
        f"| Completed naturally | {'No (hit token limit)' if done_s == 'length' else 'Yes'} |",
        "",
        "## Combined",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Review + scoring time | {fmt_s(metrics['combined_total_s'])} |",
    ]
    (output_dir / "metrics.md").write_text("\n".join(metrics_lines) + "\n", encoding="utf-8")

    print()
    print("=" * 70)
    print("  PERFORMANCE METRICS")
    print("=" * 70)
    print((output_dir / "metrics.md").read_text(encoding="utf-8"))
    print("=" * 70)
    print("  ISSUES.md SCORECARD")
    print("=" * 70)
    print((output_dir / "issues_scorecard.md").read_text(encoding="utf-8"))
    print()
    print(f"Artifacts written to: {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
