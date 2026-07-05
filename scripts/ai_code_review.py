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
        chunks.append(f"### File: {rel}\n```\n{body}\n```\n")

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


REVIEW_PROMPT_TEMPLATE = (
    "You are an expert software engineer performing a thorough peer code review.\n"
    "Review the source files from branch '{branch_name}' (commit {commit_sha}).\n\n"
    "{truncation_note}\n\n"
    "Work through EVERY category below methodically. For each category, read every file "
    "carefully and report ALL issues you find, no matter how minor. Do not skip a category "
    "because you found nothing — if a category is clean, say so.\n\n"
    "---\n\n"
    "## Review Categories\n\n"
    "### 1. Security Vulnerabilities\n"
    "Check for: SQL injection (including string-interpolated queries, LIKE clauses, UPDATE/DELETE/INSERT statements, "
    "and helper methods that accept raw SQL fragments); hardcoded credentials, passwords, API keys, or backdoors "
    "in source files or config; broken or weak cryptography (MD5, SHA1, no salt); JWT misconfiguration "
    "(ValidateLifetime, weak secrets); broken access control (missing ownership checks on PUT/DELETE endpoints); "
    "missing authorization attributes; open CORS policy; developer exception pages in production; HTTPS disabled; "
    "debug symbols in release builds; production secrets committed to source control.\n\n"
    "### 2. Logic Errors\n"
    "Check for: off-by-one errors (especially in pagination — e.g. `page * pageSize` vs `(page-1) * pageSize`); "
    "incorrect boundary conditions (e.g. `< 0` when `<= 0` is needed); balance or fee calculations that exclude "
    "a component (e.g. checking balance >= amount but then deducting amount + fee); incorrect rates or constants "
    "(e.g. interest rate applied as 5% instead of 1%); missing self-referential checks (e.g. transferring to yourself); "
    "any operation that can produce a negative balance or nonsensical result.\n\n"
    "### 3. Error Handling\n"
    "Check for: methods that catch broad `Exception` and swallow it silently; catch blocks that return empty "
    "collections — callers cannot distinguish 'no results' from 'error'; operations that lack a database "
    "transaction where two or more writes must be atomic; side effects (e.g. email sending) that can throw "
    "after a DB write has already committed; raw `ex.Message` or stack traces returned to HTTP clients; "
    "missing rate limiting or account lockout on authentication endpoints.\n\n"
    "### 4. Resource Leaks\n"
    "Check for: `SqlConnection`, `SqlDataReader`, `SqlCommand` that are opened but never closed or disposed; "
    "connections returned from helper methods where the caller never disposes them; `SmtpClient` held as an "
    "instance field (not thread-safe, socket never released); `MailMessage` or other `IDisposable` objects "
    "created but never disposed; any exception path that skips a `Close()` or `Dispose()` call.\n\n"
    "### 5. Null Reference Risks\n"
    "Check for: configuration values read with `_config[\"key\"]` passed directly to methods that cannot "
    "accept null (e.g. `Encoding.UTF8.GetBytes`); `DataTable.Rows[0]` accessed without first checking "
    "`Rows.Count > 0`; `.Value` on a nullable or `?.Value` result passed to `int.Parse` without null guard; "
    "method parameters used (`.ToUpper()`, `.Length`, etc.) before a null check; model-bound request objects "
    "used in controller actions without a null check.\n\n"
    "### 6. Dead Code\n"
    "Check for: private or public methods that are never called anywhere in the codebase; methods marked "
    "`[Obsolete]` that are still present; code after an unconditional `return` statement (unreachable); "
    "duplicate implementations where a fixed version exists alongside a broken one but only the broken one "
    "is called; `throw new NotImplementedException()` in non-stub code.\n\n"
    "### 7. Magic Strings and Numbers\n"
    "Check for: numeric literals used inline without a named constant (e.g. fee rates, page size limits, "
    "deposit caps, string length limits); string literals for email addresses, role names, or config keys "
    "repeated in multiple places; values that belong in configuration (e.g. `appsettings.json`) but are "
    "hardcoded in source.\n\n"
    "### 8. Anti-patterns and Code Quality\n"
    "Check for: string concatenation inside a loop (O(n²) — use `StringBuilder` or `string.Join`); "
    "`new Regex(...)` inside a method called repeatedly (should be `static readonly`); shared mutable "
    "static state accessed from multiple threads without synchronization; reimplementing standard library "
    "methods that already exist (e.g. `string.IsNullOrWhiteSpace`); helper methods designed to leak "
    "resource ownership to callers with no documented contract; duplicated validation logic that should "
    "be extracted to a shared method.\n\n"
    "### 9. Configuration Issues\n"
    "Check for: `UseDeveloperExceptionPage()` called unconditionally; `ValidateLifetime = false` on JWT; "
    "HTTPS redirection commented out; overly permissive CORS (`AllowAnyOrigin` + `AllowAnyMethod`); "
    "debug log levels set for production namespaces; outdated or vulnerable NuGet packages (check `.csproj`); "
    "missing environment-specific config overrides (`appsettings.Production.json`).\n\n"
    "### 10. Missing Unit Tests\n"
    "Check whether a test project exists. If not, list the specific methods and scenarios that are most "
    "critical to test, focusing on boundary conditions, auth flows, financial calculations, and pagination.\n\n"
    "---\n\n"
    "## Output Format\n\n"
    "Produce a Markdown report with one `##` section per category above.\n"
    "**You MUST include all 10 sections.** If a category has no issues, write 'No issues found.'\n\n"
    "Within each section use a compact Markdown table with columns:\n"
    "| File | Line | Issue | Fix |\n"
    "Keep each cell to one sentence maximum — no code blocks, no nested bullets.\n\n"
    "Complete all 10 sections before adding any additional commentary.\n\n"
    "---\n\n"
    "## Source Files\n\n"
    "{diff}"
)


SCORING_PREAMBLE = (
    "You are a QA evaluator assessing how well an AI code review tool performed.\n\n"
    "CRITICAL: The AI review was produced by a model that has NEVER seen the reference "
    "issue list. It will NOT use issue IDs like C1 or L2. It will describe problems in "
    "its own words. Your job is STRICT semantic matching: for each reference issue you "
    "must locate a specific sentence in the review that names the SAME target — the same "
    "file, the same method or symbol, or the same concrete behavior described in the "
    "reference Description. If you cannot locate such a sentence, the issue is Missed. "
    "Wording differences are fine; target differences are NOT.\n\n"
    "Scoring rules (apply strictly, with evidence):\n"
    "- Found: the review identifies THIS specific issue. There must exist a sentence in "
    "the review that names the same method/file/symbol/behavior as the Description. "
    "Generic class-level mentions are NOT enough when the Description names a specific "
    "target. Each Found rating must be backed by its OWN sentence — you cannot reuse one "
    "sentence to mark multiple unrelated rows Found.\n"
    "  Concretely:\n"
    "  * SQL-injection rows C1, C4, C5, C6, C7 each name a different method (Login, "
    "UpdateUser/DeleteUser, SearchUsers, Transfer/Deposit, RecordTransaction). Found "
    "requires the review to mention THAT method or its specific parameters. A generic "
    "'SQL injection exists' sentence credits AT MOST one of these — the others are Partial.\n"
    "  * Dead-code rows D1-D11 each name a different unused symbol (HashPasswordSha1, "
    "ValidateToken's unreachable code, TableExists, ExecuteQueryWithParams, "
    "BuildHtmlTemplate, SendWelcomeEmailHtml, FormatCurrency, IsWithinDailyLimit, "
    "ObfuscateAccount, ToTitleCase, JoinWithSeparatorFixed). Found requires the review "
    "to name THAT symbol. 'Dead code exists' or naming ONE unused method does not credit "
    "the others — those are Missed.\n"
    "  * Access-control rows C10, C11, L5, E7, N7 each name a different missing check. "
    "'ValidateToken returns true' is NOT evidence for any of them — it covers ONLY D2 "
    "(unreachable code). Found requires the review to name the specific endpoint or "
    "missing check.\n"
    "  * C2 (backdoor password constant 'AdminBypassPassword') and C8 (production "
    "secrets in appsettings.json) and CF1 (secrets in source control) are RELATED but "
    "DISTINCT. The review must name AdminBypassPassword to credit C2; a generic "
    "'hardcoded credentials' sentence credits C8 or CF1 but not C2.\n"
    "- Partial: the review touches the right area but materially misses the specific "
    "point. Examples: mentions MD5 is weak but not the missing salt (C3); mentions SQL "
    "injection generally but not the specific method named in the row; mentions "
    "hardcoded values broadly but not the specific constant in the row.\n"
    "- Missed: the review does not identify this specific issue. After careful reading, "
    "you cannot quote a sentence that addresses THIS row's specific target. Phrasing "
    "differences are fine — semantic match is required, but the semantic TARGET "
    "(method/symbol/file/behavior) must be the same. DO NOT default to Found when in "
    "doubt — default to Missed if you cannot point to specific evidence.\n\n"
    "Evidence rule for the Notes column (NON-NEGOTIABLE):\n"
    "- For every Found or Partial rating, the Note must quote or closely paraphrase the "
    "supporting sentence and MUST name the same target (method/file/symbol/behavior) as "
    "THIS row's Description. If your Note text names a different target than the "
    "Description, the rating is wrong — downgrade to Missed.\n"
    "- Self-check before finalizing each row: read your Note next to the row's "
    "Description. Do they refer to the same specific thing? If not, change Status to "
    "Missed and clear the Note.\n"
    "- Do not reuse identical Note text across multiple IDs. Each row needs independent "
    "evidence drawn from a different part of the review.\n\n"
    "Your task:\n"
    "- Work through EVERY issue ID in the reference document: C1-C11, L1-L5, R1-R3, "
    "E1-E7, RL1-RL5, N1-N7, M1-M5, D1-D11, A1-A6, CF1-CF9 (69 rows), plus ONE aggregate "
    "row for the entire '## Missing Unit Tests' prose section (see below).\n"
    "- Output a Markdown document titled '# AI Review Scorecard' with:\n"
    "  1. Exactly ONE summary line of the form: "
    "Total: <N> Found / <P> Partial / <M> Missed out of <T> issues.\n"
    "     N, P, and M MUST be computed ONLY by counting Status cells across ALL of your "
    "tables after every row is written; T must equal N+P+M (the same as the number of "
    "data rows in those tables). If your draft counts disagree with the tables, fix "
    "either the tables or the summary before you stop — never leave contradictory numbers.\n"
    "  2. One table per category matching the categories in the reference document.\n"
    "     Each table must have columns: | ID | Description | Status | Notes |\n"
    "     Use EXACTLY those four columns — do not insert an extra file/location column "
    "between ID and Description (ISSUES.md already embeds file and lines inside the "
    "Description text). Extra columns break automated counting; Notes may contain `|` "
    "characters, so keep pipe delimiters only between the four columns.\n"
    "     Status must be exactly one of: Found | Partial | Missed\n"
    "     Notes: one sentence quoting or closely paraphrasing the relevant part of the "
    "review, or blank if Missed. If Status is Found or Partial, the Note must clearly "
    "relate to THAT row's Description (same vulnerability, bug, or symbol named there). "
    "Reusing the same Note text for multiple different IDs is invalid — use Partial or "
    "Missed instead for rows the review does not actually cover.\n"
    "     Concretely: for dead-code rows D1-D11, each Found/Partial Note must mention "
    "that row's specific unused symbol or scenario (e.g. D1 → HashPasswordSha1, D4 → "
    "ExecuteQueryWithParams). Copy-pasting one JoinWithSeparator sentence for every "
    "D-row is wrong. Likewise, do not paste one SmtpClient or Transfer paragraph "
    "under unrelated SQL-injection or pagination IDs.\n"
    "  3. Row-count rules (strict):\n"
    "     - You must output EXACTLY 70 data rows across all tables: one row per ID "
    "C1 through CF9 (69 rows), matching the reference tables in ISSUES.md, plus EXACTLY "
    "ONE row for Missing Unit Tests.\n"
    "     - For Missing Unit Tests ONLY: use a single row with ID **UT**. In the "
    "Description cell, briefly summarize the whole section (no test project / missing "
    "coverage and the key areas listed in ISSUES.md). Score whether the review addresses "
    "that aggregate topic (missing tests, need for coverage, etc.).\n"
    "     - Do NOT add multiple rows for Missing Unit Tests (no one-row-per-bullet, no "
    "rows with ID '-' listing individual test scenarios). Do NOT add extra IDs beyond "
    "C1-CF9 and UT.\n"
    "- Do not add any commentary outside the scorecard document.\n\n"
    "---\n"
    "## Reference Issues\n\n"
)


_STATUS_CELL = re.compile(r"\|\s*(Found|Partial|Missed)\s*\|", re.IGNORECASE)
_ROW_ID = re.compile(r"^\|\s*([A-Z]{1,3}\d*|UT)\s*\|", re.IGNORECASE)
_THINK_BLOCK = re.compile(r"<think>.*?</think>\s*", re.DOTALL | re.IGNORECASE)


def strip_thinking(text: str) -> str:
    """Remove Qwen3-style <think>…</think> blocks (including empty ones)."""
    return _THINK_BLOCK.sub("", text).lstrip()


def count_table_statuses(md: str) -> tuple[int, int, int]:
    found = partial = missed = 0
    for raw in md.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 3:
            continue
        id_cell = parts[1] if len(parts) > 1 else ""
        if id_cell.lower() == "id" or not id_cell:
            continue
        if re.match(r"^-{3,}$", id_cell):
            continue
        m = _STATUS_CELL.search(line)
        if not m:
            continue
        s = m.group(1).lower()
        if s == "found":
            found += 1
        elif s == "partial":
            partial += 1
        elif s == "missed":
            missed += 1
    return found, partial, missed


def warn_repeated_notes(md: str) -> None:
    from collections import defaultdict

    note_to_ids: dict[str, list[str]] = defaultdict(list)
    for raw in md.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        m_id = _ROW_ID.match(line)
        if not m_id:
            continue
        issue_id = m_id.group(1).upper()
        if issue_id == "ID" or re.match(r"^-{3,}$", issue_id):
            continue
        m = _STATUS_CELL.search(line)
        if not m:
            continue
        if m.group(1).lower() not in ("found", "partial"):
            continue
        notes = line[m.end():].lstrip("|").strip()
        if len(notes) < 20:
            continue
        norm = re.sub(r"\s+", " ", notes).strip().lower()
        note_to_ids[norm].append(issue_id)

    for norm, ids in note_to_ids.items():
        if len(ids) >= 3:
            uniq = sorted(set(ids), key=lambda x: (len(x), x))
            preview = norm[:140] + ("…" if len(norm) > 140 else "")
            print(
                f"WARN: Scorecard reused the same Notes text for {len(uniq)} issues "
                f"({', '.join(uniq)}). Scorer model ignored per-issue Notes rules; "
                f"compare review.md. Example: {preview!r}",
                file=sys.stderr,
            )


def reconcile_summary_line(md: str) -> str:
    fnd, prt, mis = count_table_statuses(md)
    total = fnd + prt + mis
    if total == 0:
        print("WARN: Could not parse any table Status cells; leaving model summary unchanged.")
        return md
    new_line = f"Total: {fnd} Found / {prt} Partial / {mis} Missed out of {total} issues."
    pattern = re.compile(
        r"^Total:\s*\d+\s*Found\s*/\s*\d+\s*Partial\s*/\s*\d+\s*Missed\s*out\s*of\s*\d+\s*issues\.?\s*$",
        re.MULTILINE | re.IGNORECASE,
    )
    md2, n = pattern.subn(new_line, md, count=1)
    if n:
        print(f"Scorecard summary reconciled from tables: {new_line}")
        return md2
    insert = "\n" + new_line + "\n"
    first_nl = md.find("\n")
    if first_nl != -1:
        return md[:first_nl + 1] + insert + md[first_nl + 1:]
    return insert + md


def ns_to_s(ns: int | None) -> float:
    return round(ns / 1e9, 1) if ns else 0.0


def tps(tokens: int | None, duration_ns: int | None) -> float:
    return round(tokens / max(duration_ns / 1e9, 0.001), 1) if tokens and duration_ns else 0.0


def fmt_s(secs: float) -> str:
    if secs >= 60:
        return f"{int(secs // 60)}m {secs % 60:.0f}s"
    return f"{secs:.1f}s"


def main() -> int:
    review_model = os.environ.get("OLLAMA_MODEL", "glm-5.2:cloud")
    scoring_model = os.environ.get("AI_ASSISTANT_OLLAMA_MODEL_REVIEWER", review_model)

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

    review_payload = {
        "model": review_model,
        "messages": [{"role": "user", "content": review_prompt}],
        "stream": False,
        "think": False,
        "options": {"temperature": temperature, "num_predict": num_predict},
    }
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

    scoring_payload = {
        "model": scoring_model,
        "messages": [{"role": "user", "content": scoring_prompt}],
        "stream": False,
        "think": False,
        "options": {"temperature": temperature, "num_predict": num_predict},
    }
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

    body = reconcile_summary_line(scorecard)
    warn_repeated_notes(body)
    rf, rp, rm = count_table_statuses(body)
    row_total = rf + rp + rm
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
    (output_dir / "issues_scorecard.md").write_text(header + body, encoding="utf-8")

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
