#!/usr/bin/env python3
"""AI code patcher + peer-review scorecard.

Given a specified coding-agent model and ISSUES.md as the fix specification,
this script:

1. Sends the sample source tree AND the full issue list to the patcher model
   and asks it to return corrected file contents (as `### File: <path>` blocks
   in the same format `ai_code_review.py` already produces).
2. Extracts those blocks, validates the paths against the on-disk tree, and
   writes them into a scratch mirror of `SampleBankingApp/` (default
   `.ai-patch/SampleBankingApp/`).
3. Runs `scripts/ai_code_review.py` twice — once against the pristine tree
   (baseline) and once against the patched tree (post-patch) — so the peer
   reviewer gives us a before/after score using the SAME reviewer/scorer model
   for a fair comparison.
4. Writes `patch_summary.md` and `patch_summary.json` combining both runs so
   you can see how many issues the coding agent actually resolved.

Env vars (all optional; sensible defaults for Ollama's hosted cloud):
  OLLAMA_URL                              On-prem Ollama endpoint used for any
                                          model tag that does NOT end in ':cloud'.
                                          Default: https://ollama.com
  OLLAMA_CLOUD_URL                        Hosted Ollama endpoint used for any
                                          ':cloud' model tag. Default: https://ollama.com
  OLLAMA_API_KEY                          Bearer token; sent ONLY to the cloud
                                          endpoint (local Ollama rejects auth
                                          headers with 400). Required if any of
                                          the three model roles use ':cloud'.
  AI_PATCHER_MODEL                        Model that produces the fix.
                                          Default: glm-5.2:cloud
  AI_REVIEWER_MODEL                       Model that reviews + scores. Passed
                                          through to ai_code_review.py as
                                          OLLAMA_MODEL. Default: patcher model.
  AI_SCORER_MODEL                         Scorer model. Passed through as
                                          AI_ASSISTANT_OLLAMA_MODEL_REVIEWER.
                                          Default: reviewer model.
  AI_PATCH_MODEL_NUM_CTX                  Default: 49152
  AI_PATCH_MODEL_NUM_PREDICT              Default: 24000
  AI_PATCH_MODEL_TEMPERATURE              Default: 0.2 (patch code should be
                                          near-deterministic).
  AI_PATCH_SOURCE_ROOT                    Repo-relative source tree the patcher
                                          reads from. Default: SampleBankingApp/
  AI_PATCH_OUTPUT_DIR                     Where scratch tree + reports go.
                                          Default: .ai-patch/
  AI_PATCH_SKIP_BASELINE=1                Skip the baseline review pass.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import hashlib
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Import the shared helpers from the reviewer script so we don't duplicate the
# curl/Ollama plumbing or the source-file collector.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
try:
    from ai_code_review import (  # type: ignore
        collect_branch_content,
        fmt_s,
        ns_to_s,
        ollama_chat,
        resolve_endpoint,
        run,
        strip_thinking,
        tps,
    )
except ImportError as exc:  # pragma: no cover
    print(f"ERROR: could not import ai_code_review helpers: {exc}", file=sys.stderr)
    sys.exit(1)


PATCH_PROMPT_TEMPLATE = (
    "You are an expert .NET software engineer acting as a coding agent.\n\n"
    "Your task: FIX the deliberate bugs documented in the reference issue list "
    "below by producing corrected versions of the affected source files. This "
    "is graded — a second, independent AI peer reviewer that has never seen "
    "the issue list will read your patched code and count how many of the "
    "listed problems it can still find. Your job is to leave as few of them "
    "detectable as possible while keeping the app well-formed and its intended "
    "behaviour intact.\n\n"
    "Rules:\n"
    "1. Fix EVERY issue you can. Do not skip categories. Common-sense fixes for "
    "the specific bug named in each row are what's being scored — do not "
    "refactor unrelated code, rename public types, or change API surface.\n"
    "2. For SQL: switch to parameterised commands (SqlParameter / @param "
    "placeholders). Do not concatenate or interpolate user input into SQL.\n"
    "3. For access control: add the ownership/role checks named in the issue.\n"
    "4. For resource leaks: use `using` statements or explicit dispose in a "
    "`finally` block.\n"
    "5. For error handling: replace swallowed generic catches with specific "
    "handling, use DB transactions where two writes must be atomic, and stop "
    "leaking `ex.Message`/stack traces to HTTP clients.\n"
    "6. For dead code, unused private helpers, unreachable branches, and "
    "obsolete duplicates: DELETE them from the file entirely.\n"
    "7. For magic values: extract them into named `const` fields or move them "
    "into `appsettings.json` with a config-bound accessor.\n"
    "8. Configuration: remove hardcoded production secrets from `appsettings.json` "
    "(replace with placeholder strings such as `\"__SET_VIA_ENV__\"`); tighten "
    "JWT (`ValidateLifetime = true`); scope CORS; guard developer exception "
    "pages behind `env.IsDevelopment()`; re-enable HTTPS redirection.\n"
    "9. Preserve build correctness: keep namespaces, class names, and method "
    "signatures the same unless the fix requires a signature change. Do not "
    "introduce new NuGet references.\n"
    "10. Missing tests are out of scope for this patch step — do not create a "
    "test project.\n\n"
    "## Output format — read carefully, this is mechanically parsed\n\n"
    "Return ONE Markdown document containing ONLY the files you modified. For "
    "each modified file emit a header line followed by a fenced code block "
    "with the FULL new file contents:\n\n"
    "### File: SampleBankingApp/Services/AuthService.cs\n"
    "```\n"
    "<complete new file contents here>\n"
    "```\n\n"
    "Requirements:\n"
    "- Path must be the exact repo-relative path shown in the '## Source Files' "
    "section below (forward slashes, case-sensitive).\n"
    "- Only include files you actually changed.\n"
    "- The fenced block must contain the WHOLE file, not a diff, not a snippet, "
    "not an ellipsis. Anything omitted will simply be missing from the patched "
    "tree.\n"
    "- Do NOT wrap the whole response in an outer code fence.\n"
    "- Do NOT include prose commentary between file blocks. Any explanation "
    "belongs in a single `## Change Log` section AT THE END, after every file.\n\n"
    "---\n\n"
    "## Reference Issues (the answer key you must resolve)\n\n"
    "{issues}\n\n"
    "---\n\n"
    "## Source Files (current state — patch these)\n\n"
    "{diff}"
)


# Recognise `### File: <path>` (H3) file headers regardless of how many spaces.
_FILE_HEADER_RE = re.compile(r"^\s*#{1,6}\s*File\s*:\s*(.+?)\s*$", re.MULTILINE)


# Reuse the reviewer's implementation rather than a fourth copy.
sys.path.insert(0, str(REPO_ROOT / "scripts"))
from ai_code_review import reasoning_controls as _reasoning_controls  # noqa: E402
from ai_code_review import resolve_think as _resolve_think  # noqa: E402
from ai_code_review import DEFAULT_SYSTEM_PROMPT as _DEFAULT_SYSTEM_PROMPT  # noqa: E402

sys.path.insert(0, str(REPO_ROOT))
import patch_checks  # noqa: E402
import build_check  # noqa: E402


def extract_file_blocks(patch_output: str) -> dict[str, str]:
    """Parse `### File: <path>` + fenced-block pairs out of the LLM response.

    Returns a mapping of repo-relative path -> new file contents. Ignores
    headers that aren't immediately followed by a fenced code block.
    """
    blocks: dict[str, str] = {}
    lines = patch_output.splitlines()
    i = 0
    while i < len(lines):
        m = _FILE_HEADER_RE.match(lines[i])
        if not m:
            i += 1
            continue
        rel_path = m.group(1).strip().strip("`").strip()
        # Find the opening fence on a subsequent line (skip blank lines).
        j = i + 1
        while j < len(lines) and lines[j].strip() == "":
            j += 1
        if j >= len(lines) or not lines[j].lstrip().startswith("```"):
            i = j
            continue
        # Capture body until matching closing fence.
        body_lines: list[str] = []
        k = j + 1
        while k < len(lines) and not lines[k].lstrip().startswith("```"):
            body_lines.append(lines[k])
            k += 1
        if k >= len(lines):
            # Unterminated fence — skip this block rather than swallowing rest of output.
            print(f"WARN: unterminated code fence for {rel_path}; skipping.", file=sys.stderr)
            i = k
            continue
        blocks[rel_path] = "\n".join(body_lines) + ("\n" if body_lines else "")
        i = k + 1
    return blocks


def build_scratch_tree(
    source_root: Path, scratch_root: Path, patched_files: dict[str, str],
) -> tuple[int, int, list[str]]:
    """Mirror source_root -> scratch_root/<basename>, then overlay patched_files.

    Returns (files_copied, files_patched, rejected_paths).
    """
    if scratch_root.exists():
        shutil.rmtree(scratch_root)
    scratch_root.mkdir(parents=True)

    dest = scratch_root / source_root.name
    shutil.copytree(source_root, dest)
    files_copied = sum(1 for _ in dest.rglob("*") if _.is_file())

    files_patched = 0
    rejected: list[str] = []
    source_prefix = source_root.relative_to(REPO_ROOT).as_posix().rstrip("/") + "/"
    for rel_posix, content in patched_files.items():
        # Normalise both patcher-emitted paths and the scratch layout to
        # SampleBankingApp/... form.
        rel_norm = rel_posix.replace("\\", "/").lstrip("./")
        if not rel_norm.startswith(source_prefix):
            rejected.append(rel_posix)
            continue
        # Reject any path that escapes the scratch root via ..
        target = (dest.parent / rel_norm).resolve()
        try:
            target.relative_to(dest.resolve())
        except ValueError:
            rejected.append(rel_posix)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        files_patched += 1
    return files_copied, files_patched, rejected


def run_reviewer(
    source_root_rel: str,
    output_dir: Path,
    reviewer_model: str,
    scorer_model: str,
    *,
    use_fs_walk: bool,
    base_env: dict[str, str],
) -> dict:
    """Invoke scripts/ai_code_review.py against the given source root and
    return the parsed metrics.json.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    env = dict(base_env)
    env["OLLAMA_MODEL"] = reviewer_model
    env["AI_ASSISTANT_OLLAMA_MODEL_REVIEWER"] = scorer_model
    env["AI_REVIEW_SOURCE_GLOB_ROOT"] = source_root_rel
    env["AI_REVIEW_OUTPUT_DIR"] = str(output_dir)
    env["AI_REVIEW_USE_FS_WALK"] = "1" if use_fs_walk else "0"

    cmd = [sys.executable, str(REPO_ROOT / "scripts" / "ai_code_review.py")]
    print(f"\n>>> Running peer reviewer against {source_root_rel} (fs_walk={use_fs_walk})")
    print(f"    reviewer={reviewer_model}, scorer={scorer_model}")
    print(f"    output={output_dir}")
    res = subprocess.run(cmd, env=env, cwd=REPO_ROOT)
    if res.returncode != 0:
        print(f"ERROR: peer reviewer exited {res.returncode}", file=sys.stderr)
        sys.exit(res.returncode)

    metrics_path = output_dir / "metrics.json"
    if not metrics_path.exists():
        print(f"ERROR: reviewer did not produce {metrics_path}", file=sys.stderr)
        sys.exit(1)
    return json.loads(metrics_path.read_text(encoding="utf-8"))


def build_run_config(
    patcher_model: str,
    reviewer_model: str,
    scorer_model: str,
    patcher_metrics: dict,
    baseline_metrics: dict | None,
    post_metrics: dict,
) -> str:
    """Everything needed to re-dispatch this exact run.

    Recorded from the environment and the responses as they actually were, not from
    the workflow file, which may have moved on. Three separate model roles each with
    their own sampler is more configuration than anyone reconstructs from memory.
    """
    def val(v, blank="(model default)"):
        return f"`{v}`" if v not in (None, "") else blank

    def env(name, blank="(model default)"):
        return val((os.environ.get(name) or "").strip() or None, blank)

    rev = (post_metrics or {}).get("review", {})
    sco = (post_metrics or {}).get("scoring", {})

    rows = [
        ("**Patcher**", ""),
        ("Model", val(patcher_model)),
        ("Temperature", val(patcher_metrics.get("temperature") or os.environ.get("AI_PATCH_MODEL_TEMPERATURE"))),
        ("num_ctx / num_predict",
         f"{val(patcher_metrics.get('context_window'))} / {val(patcher_metrics.get('output_token_limit'))}"),
        ("Reasoning / `think`", f"{env('AI_PATCH_MODEL_REASONING')} / {env('AI_PATCH_MODEL_THINK', '(unset)')}"),
        ("Source truncated", val("yes" if patcher_metrics.get("content_truncated") else "no")),
        ("**Reviewer**", ""),
        ("Model", val(reviewer_model)),
        ("Temperature", val(rev.get("temperature") or os.environ.get("AI_ASSISTANT_MODEL_TEMPERATURE"))),
        ("num_ctx / num_predict",
         f"{val(rev.get('context_window'))} / {val(rev.get('output_token_limit'))}"),
        ("Reasoning / `think`",
         f"{val(rev.get('reasoning'))} / {val(rev.get('think'), '(unset)')}"),
        ("Source truncated", val("yes" if rev.get("content_truncated") else "no")),
        ("**Scorer**", ""),
        ("Model", val(scorer_model)),
        ("Temperature", env("AI_ASSISTANT_SCORER_TEMPERATURE", "0.3")),
        ("num_predict", env("AI_ASSISTANT_SCORER_NUM_PREDICT", "24000")),
        ("Reasoning / `think`",
         f"{env('AI_ASSISTANT_SCORER_REASONING')} / {env('AI_ASSISTANT_SCORER_THINK', '(unset)')}"),
        ("Grounding mode", env("AI_ASSISTANT_SCORECARD_GROUNDING", "enforce")),
        ("**Reference**", ""),
        ("Branch / commit", val(_git_head(), "(unknown)")),
        ("ISSUES.md SHA-256", val(_sha_of(REPO_ROOT / "ISSUES.md"), "(unknown)")),
        ("Scorer prompt SHA-256", val(_sha_of(REPO_ROOT / "scorer_prompt.md"), "(unknown)")),
        ("Review prompt SHA-256", val(_sha_of(REPO_ROOT / "review_prompt.md"), "(unknown)")),
    ]
    lines = [
        "## Run Configuration",
        "",
        "Values as actually used, so this run can be re-dispatched exactly. Blank sampler "
        "entries mean the request omitted them and the model's own Modelfile applied.",
        "",
        "| Setting | Value |",
        "|---|---|",
    ]
    lines += [f"| {k} | {v} |" for k, v in rows]
    lines.append("")
    return "\n".join(lines)


def _git_head() -> str | None:
    """'branch @ shortsha' for the harness itself.

    The review benchmark records this and the patch pipeline did not, so a sweep
    could not be checked for having run on a single harness revision -- the first
    question asked of any set of results here.
    """
    try:
        branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"],
                                capture_output=True, text=True, cwd=REPO_ROOT).stdout.strip()
        head = subprocess.run(["git", "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, cwd=REPO_ROOT).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                               capture_output=True, text=True, cwd=REPO_ROOT).stdout.strip()
    except OSError:
        return None
    if not head:
        return None
    return f"{branch or '(detached)'} @ {head}" + (" (dirty)" if dirty else "")


def _sha_of(path) -> str | None:
    try:
        # Normalise line endings: a Windows checkout is CRLF and the runner is LF,
        # so raw bytes made identical content hash differently by platform.
        text = Path(path).read_text(encoding='utf-8', errors='replace')
        return hashlib.sha256(
            text.replace("\r\n", "\n").encode("utf-8")
        ).hexdigest()[:12]
    except OSError:
        return None


def run_patch_checks(scratch_source_root) -> tuple[dict, str]:
    """Inspect the patched tree directly for each seeded bug's marker.

    The review delta answers "what can the reviewer still name?", which is a proxy for
    "what did the patcher fix" and fails both ways. This answers the second question
    without a model in the loop, for the subset of issues with an unambiguous marker.
    """
    result = patch_checks.verify(scratch_source_root)
    checks, reference_total = patch_checks.coverage(REPO_ROOT / "ISSUES.md")
    section = patch_checks.render(result, checks, reference_total)
    print(f"\n>>> Mechanical verification: {len(result['fixed'])} fixed / "
          f"{len(result['still_present'])} still present of {result['checked']} checked "
          f"({checks} of {reference_total} reference issues have a marker)")
    if result["still_present"]:
        print("    still present: " + ", ".join(sorted(result["still_present"])))
    return result, section


def write_no_patch_report(
    output_dir: Path,
    patcher_model: str,
    reviewer_model: str,
    scorer_model: str,
    patcher_metrics: dict,
    reason: str,
) -> None:
    """Artefact for a run where the patcher emitted nothing to apply.

    Same filenames and the same delta/verified keys as a normal run, so anything
    reading the archive gets a comparable row rather than a special case. The
    figures are not estimates: an unchanged tree resolves nothing, leaves every
    marker in place, and compiles exactly as the original does.
    """
    checks, reference_total = patch_checks.coverage(REPO_ROOT / "ISSUES.md")
    combined = {
        "config": {"harness_commit": _git_head()},
        "patcher_model": patcher_model,
        "reviewer_model": reviewer_model,
        "scorer_model": scorer_model,
        "patcher": patcher_metrics,
        "baseline": None,
        "post_patch": None,
        "delta": {
            "patch_failed": True,
            "patch_failure_reason": reason,
            "issues_resolved": 0,
            "issues_resolved_raw": 0,
            "resolution_pct": 0.0,
            "detectable_before": None,   # no review was run; see reason
            "detectable_after": None,
            # No verdict rather than a pass. The untouched tree does compile, but
            # recording that as True would let a model that produced nothing rank
            # beside models whose patches actually survive the compiler.
            "build_compiles": None,
            "build_new_errors": None,
            "build_skipped_reason": "no patch was applied, so nothing was compiled",
            "harness_commit": _git_head(),
        },
        "patched_files": [],
        "rejected_paths": [],
        "verified": {
            "fixed": [], "still_present": [], "undetermined": [],
            "checked": checks, "fixed_count": 0, "still_present_count": checks,
        },
    }
    (output_dir / "patch_summary.json").write_text(
        json.dumps(combined, indent=2), encoding="utf-8")

    lines = [
        "# AI Patch + Peer Review Summary",
        "",
        f"- **Patcher model:** `{patcher_model}`",
        f"- **Files the patcher rewrote:** 0",
        "",
        "## Verdict",
        "",
        f"- **No patch was produced.** {reason[0].upper() + reason[1:]}.",
        "- **Issues resolved: 0** (0.0% of all seeded bugs). The source tree is "
        "unchanged, so nothing was fixed and every seeded issue remains.",
        f"- Mechanical verification: **0 fixed / {checks} still present** — not a "
        "measurement of the patch but of its absence.",
        "- The peer review was skipped: reviewing the unmodified source would "
        "spend several minutes reproducing the baseline every other run already "
        "establishes.",
        "",
        "## Patcher performance",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total time | {patcher_metrics.get('total_duration_s')}s |",
        f"| Prompt tokens | {patcher_metrics.get('prompt_tokens'):,} |",
        f"| Output tokens | {patcher_metrics.get('output_tokens'):,} |",
        f"| Output speed | {patcher_metrics.get('output_tps')} tok/s |",
        f"| Completed naturally | {'Yes' if patcher_metrics.get('done_reason') == 'stop' else patcher_metrics.get('done_reason')} |",
        "",
        "## Build check",
        "",
        "Not run — no patch was applied, so there was nothing to compile. The "
        "pristine tree builds as it always did; that is a fact about the sample "
        "project, not about this model, and is recorded as no verdict rather "
        "than as a pass.",
        "",
        f"## Run Configuration",
        "",
        f"| Setting | Value |",
        "|---|---|",
        f"| Patcher | `{patcher_model}` |",
        f"| Branch / commit | `{_git_head() or '(unknown)'}` |",
        f"| ISSUES.md SHA-256 | `{_sha_of(REPO_ROOT / 'ISSUES.md') or '(unknown)'}` |",
        "",
        "The raw response is in `patch_response.md`.",
        "",
    ]
    (output_dir / "patch_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"\n>>> No patch produced. Recorded a zero result in {output_dir}")


def write_comparison_report(
    output_dir: Path,
    patcher_model: str,
    reviewer_model: str,
    scorer_model: str,
    patcher_metrics: dict,
    baseline_metrics: dict | None,
    post_metrics: dict,
    patched_paths: list[str],
    rejected_paths: list[str],
    checks: dict | None = None,
    checks_section: str = "",
    config_section: str = "",
    build_result: dict | None = None,
    build_section: str = "",
) -> None:
    def score(m: dict | None) -> dict:
        if not m:
            return {"found": None, "partial": None, "missed": None, "total": None, "score_pct": None}
        return m.get("score", {})

    b = score(baseline_metrics)
    p = score(post_metrics)

    def delta(a, c) -> str:
        if a is None or c is None:
            return "n/a"
        d = c - a
        sign = "+" if d > 0 else ""
        return f"{sign}{d}"

    # The success metric is the change in *undetectable* issues, not the
    # change in Found. When the patcher genuinely fixes a bug, the reviewer
    # can no longer point at it, so that bug moves into the Missed column.
    # A positive number is good news; zero or negative means the patch had no
    # visible effect (or made things worse from the reviewer's perspective).
    #
    # Partials the review does not support count as Missed. Taking Missed
    # literally makes the headline depend on the scorer rather than the patch:
    # the same patched tree, reviewed by the same model, read as 51 resolved
    # under a Gemma scorer and 25 under Qwen3-Coder-30B, purely because the
    # latter parked 37 of 69 rows in Partial.
    def detectable(d: dict) -> int | None:
        """Issues the reviewer genuinely named at this stage.

        Every row the scorer credited without support in the review is excluded,
        on both sides and by the same rule:

          * Found rows the evidence spot-check could not corroborate -- already
            subtracted in found_adjusted.
          * Partials with nothing in the review behind them.

        Symmetry is the point. Discounting only the post-patch side inflates the
        result: one run's baseline showed 69 Found against found_adjusted of 60,
        every one of the nine a fabricated citation, and counting them made nine
        never-detected bugs look resolved. Discounting only the baseline would
        understate it just as badly.

        Partials count as detected. A partial credit is not nothing, and treating
        it as full detection keeps the estimate conservative.
        """
        if d.get("found") is None:
            return None
        found = d.get("found_adjusted")
        if found is None:
            found = d["found"]
        partial = d.get("partial") or 0
        unsupported = len(d.get("spotcheck_unsupported_partials") or [])
        return found + max(0, partial - unsupported)

    issues_resolved: int | None = None
    issues_resolved_raw: int | None = None
    detectable_before: int | None = None
    detectable_after: int | None = None
    resolution_pct: float | None = None
    row_count_mismatch: str | None = None
    if (
        b.get("missed") is not None
        and p.get("missed") is not None
        and b.get("total") is not None
        and p.get("total") is not None
    ):
        detectable_before = detectable(b)
        detectable_after = detectable(p)
        issues_resolved = detectable_before - detectable_after
        issues_resolved_raw = p["missed"] - b["missed"]
        if b["total"]:
            resolution_pct = round(issues_resolved / b["total"] * 100, 1)
        # The two halves must be measured against the same denominator. A scorer
        # that drops a row shrinks its own sheet, and the comparison then spans
        # two different yardsticks without saying so.
        if b["total"] != p["total"]:
            row_count_mismatch = (
                f"baseline sheet has {b['total']} rows, post-patch has {p['total']} "
                "-- the scorer dropped a row, so the two halves are not measured "
                "against the same set of issues"
            )
            print(f"WARN: {row_count_mismatch}", file=sys.stderr)

    def _env(name):
        return (os.environ.get(name) or "").strip() or None

    def _sys_prompt(prefix):
        """What reasoning_controls() would have sent for this role."""
        raw = (os.environ.get(f"{prefix}_SYSTEM_PROMPT") or "").strip()
        if raw.lower() == "none":
            return None                      # no system message; Modelfile applies
        return raw or _DEFAULT_SYSTEM_PROMPT

    combined = {
        "config": {
            "harness_commit": _git_head(),
            "patcher": {
                "temperature": patcher_metrics.get("temperature") or _env("AI_PATCH_MODEL_TEMPERATURE"),
                "think": _env("AI_PATCH_MODEL_THINK"),
                "reasoning": _env("AI_PATCH_MODEL_REASONING"),
                "system_prompt": _sys_prompt("AI_PATCH_MODEL"),
                "num_ctx": patcher_metrics.get("context_window"),
                "num_predict": patcher_metrics.get("output_token_limit"),
            },
            "reviewer": {
                "temperature": (post_metrics or {}).get("review", {}).get("temperature")
                               or _env("AI_ASSISTANT_MODEL_TEMPERATURE"),
                "think": _env("AI_ASSISTANT_MODEL_THINK"),
                "reasoning": _env("AI_ASSISTANT_MODEL_REASONING"),
                "system_prompt": _sys_prompt("AI_ASSISTANT_MODEL"),
            },
            "scorer": {
                "temperature": _env("AI_ASSISTANT_SCORER_TEMPERATURE"),
                "think": _env("AI_ASSISTANT_SCORER_THINK"),
                "system_prompt": _sys_prompt("AI_ASSISTANT_SCORER"),
                "grounding": _env("AI_ASSISTANT_SCORECARD_GROUNDING") or "enforce",
            },
            "issues_sha": _sha_of(REPO_ROOT / "ISSUES.md"),
            "review_prompt_sha": _sha_of(REPO_ROOT / "review_prompt.md"),
            "scorer_prompt_sha": _sha_of(REPO_ROOT / "scorer_prompt.md"),
        },
        "patcher_model": patcher_model,
        "reviewer_model": reviewer_model,
        "scorer_model": scorer_model,
        "patcher": patcher_metrics,
        "baseline": baseline_metrics,
        "post_patch": post_metrics,
        "delta": {
            # Positive => issues moved from detectable to undetectable
            # (i.e. the patcher successfully hid them from the reviewer).
            "issues_resolved": issues_resolved,
            "issues_resolved_raw": issues_resolved_raw,
            "row_count_mismatch": row_count_mismatch,
            # None, not 0, when the check did not run -- 0 new errors is the same
            # value a clean build produces, and the two must not be confused.
            "build_compiles": (build_result or {}).get("compiles"),
            "build_new_errors": (len(build_result["new_errors"])
                                 if (build_result or {}).get("ran") else None),
            "build_skipped_reason": (None if (build_result or {}).get("ran")
                                     else (build_result or {}).get("reason")),
            "harness_commit": _git_head(),
            "resolution_pct": resolution_pct,
            "detectable_before": detectable_before,
            "detectable_after": detectable_after,
            # Raw column-level deltas kept for debugging. Note that
            # `found_delta` is NOT a success signal — see comment above.
            "found_delta": delta(b.get("found"), p.get("found")),
            "partial_delta": delta(b.get("partial"), p.get("partial")),
            "missed_delta": delta(b.get("missed"), p.get("missed")),
        },
        "patched_files": patched_paths,
        "rejected_paths": rejected_paths,
        # Source inspection, independent of the reviewer. `issues_resolved` above is a
        # proxy that moves with review recall; this does not.
        "verified": {
            "fixed": sorted(checks["fixed"]),
            "still_present": sorted(checks["still_present"]),
            "undetermined": sorted(checks["unknown"]),
            "checked": checks["checked"],
            "fixed_count": len(checks["fixed"]),
            "still_present_count": len(checks["still_present"]),
        } if checks else None,
    }
    (output_dir / "patch_summary.json").write_text(
        json.dumps(combined, indent=2), encoding="utf-8",
    )

    def row(label: str, s: dict) -> str:
        return (
            f"| {label} | {s.get('found', '?')} | {s.get('partial', '?')} | "
            f"{s.get('missed', '?')} | {s.get('total', '?')} | {s.get('score_pct', '?')}% |"
        )

    lines = [
        "# AI Patch + Peer Review Summary",
        "",
        f"- **Patcher model:** `{patcher_model}`",
        f"- **Reviewer model:** `{reviewer_model}`",
        f"- **Scorer model:** `{scorer_model}`",
        f"- **Files the patcher rewrote:** {len(patched_paths)}",
        f"- **Rejected paths** (outside source root or invalid): "
        f"{len(rejected_paths)}",
        "",
        "## Score comparison",
        "",
        "| Stage | Found | Partial | Missed | Total | % Found |",
        "|-------|-------|---------|--------|-------|---------|",
    ]
    if baseline_metrics:
        lines.append(row("Baseline (before patch)", b))
    else:
        lines.append("| Baseline (before patch) | *skipped* |  |  |  |  |")
    lines.append(row("Post-patch", p))
    lines.append("")
    lines += [
        "> **How to read this table.** `%Found` is the peer reviewer's *recall*, "
        "not the patcher's success. A patch that removes bugs makes them "
        "undetectable, so those IDs move into `Missed` — that's the column to "
        "watch. `Found` and `Partial` can even shift *upwards* post-patch when "
        "the reviewer gets a cleaner view of the bugs that weren't fixed.",
        "",
    ]

    if issues_resolved is not None:
        good = issues_resolved > 0
        emoji_label = "resolved" if good else ("unchanged" if issues_resolved == 0 else "regressed")
        pct_str = f" ({resolution_pct}% of all seeded bugs)" if resolution_pct is not None else ""
        lines += [
            "## Verdict",
            "",
            f"- **Issues {emoji_label}: {issues_resolved}**{pct_str}. "
            "Bugs the reviewer named before the patch and cannot name after. "
            "Rows the scorer credited without support in the review are excluded "
            "from both sides — unverifiable `Found` ratings and `Partial` "
            "ratings alike.",
            f"- Reviewer still detects **{detectable_after}** of the "
            f"{p.get('total', '?')} seeded issues, down from "
            f"**{detectable_before}** before the patch.",
        ]
        # Both figures, because the gap between them is the scorer's Partial
        # habit rather than anything the patcher did. On one run the raw figure
        # was 25 and the corrected one 40, from the same patch.
        _drop_b = (b["found"] - (b.get("found_adjusted") or b["found"])
                   + len(b.get("spotcheck_unsupported_partials") or []))
        _drop_p = (p["found"] - (p.get("found_adjusted") or p["found"])
                   + len(p.get("spotcheck_unsupported_partials") or []))
        if _drop_b or _drop_p:
            lines.append(
                f"- Taking the scorer's columns at face value would give "
                f"**{issues_resolved_raw}**. {_drop_b} baseline and {_drop_p} post-patch "
                "rows were credited with evidence the review does not contain, and are "
                "excluded. Baseline fabrications matter most: they invent bugs the "
                "reviewer never detected, each of which then counts as resolved."
            )
        if row_count_mismatch:
            lines.append(f"- **Warning:** {row_count_mismatch}.")
        if issues_resolved < 0:
            lines.append(
                "- Warning: `issues_resolved` is negative. The reviewer now "
                "detects MORE seeded issues than it did against the pristine "
                "tree — the patcher likely introduced regressions, or the "
                "reviewer's recall improved coincidentally against the "
                "rewritten code. Inspect the two scorecards side-by-side."
            )
        lines.append("")

    if patcher_metrics:
        lines += [
            "## Patcher performance",
            "",
            "| Metric | Value |",
            "|--------|-------|",
            f"| Total time | {fmt_s(patcher_metrics.get('total_duration_s', 0))} |",
            f"| Prompt tokens | {patcher_metrics.get('prompt_tokens', 0):,} |",
            f"| Output tokens | {patcher_metrics.get('output_tokens', 0):,} |",
            f"| Output speed | {patcher_metrics.get('output_tps', 0)} tok/s |",
            f"| Prompt speed | {patcher_metrics.get('prompt_tps', 0)} tok/s |",
            f"| Completed naturally | "
            f"{'No (hit token limit)' if patcher_metrics.get('done_reason') == 'length' else 'Yes'} |",
            "",
        ]

    if patched_paths:
        lines += ["## Files patched", ""]
        lines += [f"- `{p}`" for p in patched_paths]
        lines.append("")

    if build_section:
        lines += ["", build_section]

    if config_section:
        lines += ["", config_section]

    if checks_section:
        lines += ["", checks_section]

    if rejected_paths:
        lines += [
            "## Rejected paths",
            "",
            "The patcher named files outside the source tree — these were "
            "ignored:",
            "",
        ]
        lines += [f"- `{p}`" for p in rejected_paths]
        lines.append("")

    (output_dir / "patch_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _env_or(name: str, default: str) -> str:
    """Like os.environ.get(name, default) but also falls back when the var
    is set to an empty string. GitHub Actions passes `''` for unset inputs,
    which would otherwise slip through and hit downstream APIs as model=''.
    """
    return (os.environ.get(name) or "").strip() or default


def main() -> int:
    patcher_model = _env_or("AI_PATCHER_MODEL", "glm-5.2:cloud")
    reviewer_model = _env_or("AI_REVIEWER_MODEL", patcher_model)
    scorer_model = _env_or("AI_SCORER_MODEL", reviewer_model)

    # Each model routes independently: :cloud tags go to OLLAMA_CLOUD_URL, all
    # others to OLLAMA_URL. Validate all three up-front so a missing key for
    # the scorer doesn't surface only after the patcher run.
    try:
        patcher_url, patcher_key = resolve_endpoint(patcher_model)
        resolve_endpoint(reviewer_model)
        resolve_endpoint(scorer_model)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    num_ctx = int(os.environ.get("AI_PATCH_MODEL_NUM_CTX", "49152"))
    num_predict = int(os.environ.get("AI_PATCH_MODEL_NUM_PREDICT", "24000"))
    temperature = float(os.environ.get("AI_PATCH_MODEL_TEMPERATURE", "0.2"))

    source_root_rel = os.environ.get("AI_PATCH_SOURCE_ROOT", "SampleBankingApp/").rstrip("/") + "/"
    source_root = (REPO_ROOT / source_root_rel).resolve()
    if not source_root.exists():
        print(f"ERROR: source root {source_root} does not exist", file=sys.stderr)
        return 1

    output_dir = Path(os.environ.get("AI_PATCH_OUTPUT_DIR", str(REPO_ROOT / ".ai-patch")))
    if not output_dir.is_absolute():
        output_dir = REPO_ROOT / output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    issues_path = REPO_ROOT / "ISSUES.md"
    if not issues_path.exists():
        print(f"ERROR: ISSUES.md not found at {issues_path}", file=sys.stderr)
        return 1
    issues = issues_path.read_text(encoding="utf-8", errors="replace")

    print(f"Collecting source files under {source_root_rel} …")
    diff, file_count = collect_branch_content(source_root_rel)
    if not diff:
        print("No reviewable source files — nothing to patch.", file=sys.stderr)
        return 1
    print(f"Collected {file_count} files ({len(diff)} bytes).")

    chars_per_token = 2.5
    instruction_chars = len(PATCH_PROMPT_TEMPLATE.format(issues=issues, diff=""))
    available_tokens = num_ctx - num_predict - 500
    max_diff_chars = max(0, int(available_tokens * chars_per_token) - instruction_chars)
    truncated = len(diff) > max_diff_chars
    if truncated:
        diff = diff[:max_diff_chars]
        print(
            f"WARN: source listing truncated to fit context — patcher may miss "
            f"issues in the trailing {file_count} files.",
            file=sys.stderr,
        )
    print(
        f"Context: {num_ctx} tokens; instruction overhead {instruction_chars} chars; "
        f"diff budget {max_diff_chars} chars; actual diff {len(diff)} chars; "
        f"truncated={truncated}"
    )

    prompt = PATCH_PROMPT_TEMPLATE.format(issues=issues, diff=diff)
    _pmsgs, _pthink = _reasoning_controls("AI_PATCH_MODEL")
    _pthink = _resolve_think(patcher_model, _pthink, patcher_url, patcher_key)
    payload = {
        "model": patcher_model,
        "messages": _pmsgs + [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {"temperature": temperature, "num_predict": num_predict, "num_ctx": num_ctx},
    }
    if _pthink is not None:
        payload["think"] = _pthink

    data = ollama_chat(patcher_url, payload, output_dir / "patch_payload.json", "patch", patcher_key)
    raw = (data.get("message") or {}).get("content", "")
    patch_output = strip_thinking(raw).strip()
    if not patch_output:
        print("ERROR: patcher returned an empty response.", file=sys.stderr)
        return 1
    (output_dir / "patch_response.md").write_text(patch_output, encoding="utf-8")

    patcher_metrics = {
        "model": patcher_model,
        "total_duration_s": ns_to_s(data.get("total_duration")),
        "load_duration_s": ns_to_s(data.get("load_duration")),
        "prompt_tokens": data.get("prompt_eval_count", 0),
        "output_tokens": data.get("eval_count", 0),
        "output_token_limit": num_predict,
        "prompt_tps": tps(data.get("prompt_eval_count"), data.get("prompt_eval_duration")),
        "output_tps": tps(data.get("eval_count"), data.get("eval_duration")),
        "context_window": num_ctx,
        "content_truncated": truncated,
        "done_reason": data.get("done_reason", ""),
    }
    print(
        f"Patcher: {patcher_metrics['total_duration_s']}s | "
        f"in {patcher_metrics['prompt_tokens']:,} tok / "
        f"out {patcher_metrics['output_tokens']:,} tok @ "
        f"{patcher_metrics['output_tps']} tok/s | "
        f"done_reason={patcher_metrics['done_reason']}"
    )

    blocks = extract_file_blocks(patch_output)
    if not blocks:
        print(
            "ERROR: could not extract any `### File: <path>` blocks from the "
            "patcher output. See patch_response.md for the raw response.",
            file=sys.stderr,
        )
        write_no_patch_report(
            output_dir, patcher_model, reviewer_model, scorer_model, patcher_metrics,
            "the patcher produced no `### File:` blocks — its response contains "
            "prose about the code but no code",
        )
        # Not an error exit: "cannot produce a patch" is a measurement, and the
        # sweep needs the row. A non-zero exit here would leave the weakest model
        # with no artefact, which reads as "not run" rather than "scored zero".
        return 0
    print(f"Extracted {len(blocks)} patched files from response.")

    scratch_root = output_dir / "scratch"
    files_copied, files_patched, rejected = build_scratch_tree(
        source_root, scratch_root, blocks,
    )
    print(f"Scratch tree: {files_copied} copied, {files_patched} patched, "
          f"{len(rejected)} rejected.")
    if rejected:
        for r in rejected:
            print(f"  rejected: {r}", file=sys.stderr)

    # Compute the repo-relative path for the reviewer to walk.
    patched_source_rel = (scratch_root / source_root.name).relative_to(REPO_ROOT).as_posix() + "/"

    base_env = os.environ.copy()

    baseline_metrics: dict | None = None
    if os.environ.get("AI_PATCH_SKIP_BASELINE", "").strip() not in {"1", "true", "yes"}:
        baseline_metrics = run_reviewer(
            source_root_rel,
            output_dir / "baseline_review",
            reviewer_model,
            scorer_model,
            use_fs_walk=False,
            base_env=base_env,
        )
    else:
        print("Skipping baseline review (AI_PATCH_SKIP_BASELINE set).")

    post_metrics = run_reviewer(
        patched_source_rel,
        output_dir / "post_patch_review",
        reviewer_model,
        scorer_model,
        use_fs_walk=True,
        base_env=base_env,
    )

    patched_paths = sorted(blocks.keys())
    checks, checks_section = run_patch_checks(scratch_root / "SampleBankingApp")

    # Whether the result compiles. Differential against the pristine tree, so the
    # sample project's pre-existing NU1605 is not charged to the patcher. Opt out
    # with AI_PATCH_BUILD_CHECK=0 on a runner with no .NET SDK.
    build_result: dict = {"ran": False, "reason": "disabled (AI_PATCH_BUILD_CHECK=0)"}
    build_section = ""
    if os.environ.get("AI_PATCH_BUILD_CHECK", "1").strip() not in {"0", "false", "no"}:
        print("\n>>> Build check: compiling pristine and patched trees \u2026")
        build_result = build_check.compare(
            source_root, scratch_root / source_root.name,
            timeout=int(os.environ.get("AI_PATCH_BUILD_TIMEOUT", "600")),
        )
        if not build_result.get("ran"):
            print(f"    not run: {build_result.get('reason')}")
        elif build_result["new_errors"]:
            print(f"    FAILED: {len(build_result['new_errors'])} new compiler error(s) "
                  f"(baseline had {build_result['baseline_errors']})")
            for e in build_result["new_errors"][:5]:
                print(f"      {e['code']} {e['file']}:{e['line'] or '?'} {e['message'][:90]}")
        else:
            print(f"    compiles (baseline errors: {build_result['baseline_errors']})")
    build_section = build_check.render(build_result)
    config_section = build_run_config(
        patcher_model, reviewer_model, scorer_model,
        patcher_metrics, baseline_metrics, post_metrics,
    )
    write_comparison_report(
        output_dir,
        patcher_model,
        reviewer_model,
        scorer_model,
        patcher_metrics,
        baseline_metrics,
        post_metrics,
        patched_paths,
        rejected,
        checks,
        checks_section,
        config_section,
        build_result,
        build_section,
    )

    print()
    print("=" * 70)
    print("  PATCH + REVIEW SUMMARY")
    print("=" * 70)
    print((output_dir / "patch_summary.md").read_text(encoding="utf-8"))
    print(f"Artifacts written to: {output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
