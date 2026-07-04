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
  OLLAMA_URL                              Default: https://ollama.com
  OLLAMA_API_KEY                          Bearer token when using ollama.com.
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

    resolved = None
    if b.get("found") is not None and p.get("found") is not None:
        resolved = p["found"] - b["found"]

    combined = {
        "patcher_model": patcher_model,
        "reviewer_model": reviewer_model,
        "scorer_model": scorer_model,
        "patcher": patcher_metrics,
        "baseline": baseline_metrics,
        "post_patch": post_metrics,
        "delta": {
            "issues_newly_resolved": resolved,
            "found_delta": delta(b.get("found"), p.get("found")),
            "missed_delta": delta(b.get("missed"), p.get("missed")),
        },
        "patched_files": patched_paths,
        "rejected_paths": rejected_paths,
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

    if resolved is not None:
        # Fewer 'Missed' after patching = the coding agent resolved that many
        # of the seeded bugs, as judged by the peer reviewer.
        missed_reduction = None
        if b.get("missed") is not None and p.get("missed") is not None:
            missed_reduction = b["missed"] - p["missed"]
        lines += [
            "## Verdict",
            "",
            f"- Peer reviewer now flags **{p.get('missed', '?')}** issues as still "
            f"present (vs **{b.get('missed', '?')}** before the patch).",
            f"- Net issues that appear resolved: **{missed_reduction}**.",
            "- Note: because the reviewer scores by *what it can still see*, "
            "reduction in the `Missed` column is the meaningful signal — the "
            "`Found` column measures the reviewer's recall, not the patcher's "
            "success.",
            "",
        ]

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


def main() -> int:
    base_url = os.environ.get("OLLAMA_URL", "https://ollama.com").rstrip("/")
    api_key = os.environ.get("OLLAMA_API_KEY", "").strip() or None
    patcher_model = os.environ.get("AI_PATCHER_MODEL", "glm-5.2:cloud")
    reviewer_model = os.environ.get("AI_REVIEWER_MODEL", patcher_model)
    scorer_model = os.environ.get("AI_SCORER_MODEL", reviewer_model)

    if "ollama.com" in base_url and not api_key:
        print(
            "ERROR: OLLAMA_URL points at the hosted Ollama cloud but "
            "OLLAMA_API_KEY is not set. Export your API key, e.g. "
            "`export OLLAMA_API_KEY=...`.",
            file=sys.stderr,
        )
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
    payload = {
        "model": patcher_model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "think": False,
        "options": {"temperature": temperature, "num_predict": num_predict, "num_ctx": num_ctx},
    }

    data = ollama_chat(base_url, payload, output_dir / "patch_payload.json", "patch", api_key)
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
        return 1
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
