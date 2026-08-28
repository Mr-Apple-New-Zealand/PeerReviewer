"""Mechanical verification of which seeded bugs survive in a patched source tree.

The patcher benchmark's headline number is a *proxy*: it compares how many issues the
peer reviewer could name before and after the patch, and treats the difference as bugs
fixed. That proxy fails in both directions -- a bug the reviewer simply overlooked counts
as resolved, and a genuinely fixed bug that the reviewer falsely re-reports counts as
unresolved. On the Muse-Glimmer run it reported 36 of 70 resolved where direct inspection
of the patched tree showed roughly 60.

This module checks the source instead. Each entry names one seeded issue and a marker
whose presence (or absence) decides whether that bug is still in the code. No thresholds,
no similarity metrics, no model in the loop -- the same reasoning as the scorecard
watchlist, applied to code rather than prose.

Two deliberate limits:

  * It is a SUBSET. Only issues with an unambiguous textual marker are listed; anything
    needing real semantic judgement (E1's swallowed exception, M-class "should be in
    config") is left out rather than guessed at. `coverage()` reports how much of
    ISSUES.md is covered so the number is never mistaken for the whole answer key.
  * A marker proves the SHAPE of the bug is gone, not that the replacement is correct.
    `ValidateLifetime = true` is a real fix; a patcher that deleted the whole auth block
    would also pass. Read it alongside the peer review, not instead of it.
"""
from __future__ import annotations

import re
from pathlib import Path

PRESENT = "present"   # bug still there if the pattern matches
ABSENT = "absent"     # bug still there if the pattern is MISSING (the fix is an addition)
CUSTOM = "custom"     # the pattern slot holds a predicate: text -> bug still there?


def _method_body(text: str, name: str) -> str | None:
    """The brace-matched body of a named method, or None if it is not there."""
    m = re.search(r"\b%s\s*\(" % re.escape(name), text)
    if not m:
        return None
    start = text.find("{", m.end())
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return text[start:i]
    return text[start:]


def _r3_long_method(text: str) -> bool:
    """R3: is GenerateJwtToken still doing everything itself?

    Measured rather than name-matched. The original body is 20 lines; a patcher
    that extracts the claims, credentials and token construction leaves about 5,
    whatever it calls the helpers. The previous marker looked for three specific
    names and missed BuildUserClaims / CreateJwtToken / CreateSigningCredentials.
    """
    body = _method_body(text, "GenerateJwtToken")
    if body is None:
        return False                      # method gone entirely
    return body.count("\n") > 12


def _a5_duplicates_bcl(text: str) -> bool:
    """A5: does IsBlank still reimplement string.IsNullOrWhiteSpace?

    Two valid fixes: delegate to the BCL, or delete the method. The old marker
    recognised only the first, so a clean deletion read as an unfixed bug.
    """
    if not re.search(r"\bIsBlank\b", text):
        return False                      # removed; callers checked separately
    return "IsNullOrWhiteSpace" not in text


def _cf7_unconditional_symbols(text: str) -> bool:
    """CF7: are debug symbols emitted in RELEASE builds?

    `<DebugSymbols>true` inside a Debug-conditioned PropertyGroup is correct and
    expected. The bug is shipping PDBs from a release build, so this looks for a
    Release group that turns them off rather than for the string anywhere.
    """
    if not re.search(r"<DebugSymbols>\s*true", text, re.I):
        return False
    for grp in re.findall(r"<PropertyGroup\b[^>]*>(.*?)</PropertyGroup>", text, re.S | re.I):
        header_ok = False
        # Re-find this group's opening tag to read its Condition.
        for m in re.finditer(r"<PropertyGroup\b([^>]*)>", text, re.I):
            if text[m.end():m.end() + len(grp)] == grp:
                header_ok = re.search(r"Release", m.group(1), re.I) is not None
                break
        if header_ok and re.search(r"<DebugSymbols>\s*false|<DebugType>\s*none", grp, re.I):
            return False
    return True


# id -> (relative path, regex OR predicate, polarity, what the marker means)
CHECKS: dict[str, tuple] = {
    # ---- SQL injection: interpolated SQL is the bug; parameters are the fix ----------
    "C1":  ("Services/AuthService.cs", r'\$@?"\s*SELECT', PRESENT,
            "Login builds its SELECT by interpolation"),
    "C4":  ("Services/UserService.cs", r'\$@?"\s*(UPDATE|DELETE)', PRESENT,
            "UpdateUser/DeleteUser interpolate into UPDATE/DELETE"),
    "C5":  ("Services/UserService.cs", r"LIKE\s+'%\{", PRESENT,
            "SearchUsers interpolates into a LIKE clause"),
    "C6":  ("Services/TransactionService.cs", r'\$@?"\s*UPDATE', PRESENT,
            "Transfer/Deposit interpolate balance updates"),
    "C7":  ("Services/TransactionService.cs", r'\$@?"\s*INSERT', PRESENT,
            "RecordTransaction interpolates the INSERT"),
    "A6":  ("Data/DatabaseHelper.cs", r"ExecuteQuery\(\s*string\s+tableName", PRESENT,
            "raw tableName/whereClause helper still accepts SQL fragments"),

    # ---- credentials and crypto -----------------------------------------------------
    "C2":  ("Services/AuthService.cs", r"AdminBypassPassword", PRESENT,
            "hardcoded admin bypass constant"),
    "C3":  ("Services/AuthService.cs", r"\bMD5\b", PRESENT,
            "MD5 password hashing"),
    "C8":  ("appsettings.json", r'Password=(?!__)[^;"]{3,}', PRESENT,
            "a real DB password is still committed"),

    # ---- auth / access control ------------------------------------------------------
    "C9":  ("Program.cs", r"ValidateLifetime\s*=\s*false", PRESENT,
            "JWT lifetime validation disabled"),
    "C10": ("Controllers/UserController.cs", r"ClaimTypes\.NameIdentifier", ABSENT,
            "UpdateUser performs no ownership check"),
    "C11": ("Controllers/UserController.cs", r"ClaimTypes\.Role", ABSENT,
            "DeleteUser performs no role check"),
    "E7":  ("Controllers/AuthController.cs", r"(?i)\b429\b|TooManyRequests|lockout|ratelimit|_failedAttempts", ABSENT,
            "login endpoint has no rate limiting or lockout"),

    # ---- logic ----------------------------------------------------------------------
    "L1":  ("Services/TransactionService.cs", r"amount\s*<\s*0\b", PRESENT,
            "zero-value transfers still allowed (`< 0` not `<= 0`)"),
    "L3":  ("Services/UserService.cs", r"skip\s*=\s*page\s*\*\s*pageSize", PRESENT,
            "pagination off-by-one"),
    "L4":  ("Services/TransactionService.cs", r"0\.05m", PRESENT,
            "5% deposit bonus instead of 1%"),
    "L5":  ("", r"(fromUserId\s*==\s*(request\.)?[tT]oUserId|Self-transfer)", ABSENT,
            "no self-transfer guard anywhere"),

    # ---- resource handling ----------------------------------------------------------
    "RL2": ("Data/DatabaseHelper.cs", r"GetOpenConnection", PRESENT,
            "connection-leaking helper still exported"),
    "RL4": ("Services/EmailService.cs", r"private\s+readonly\s+SmtpClient", PRESENT,
            "SmtpClient still held as an instance field"),

    # ---- refactoring ----------------------------------------------------------------
    "R1":  ("Services/UserService.cs", r"ValidateUserId", ABSENT,
            "duplicated id validation not extracted"),
    "R2":  ("Helpers/StringHelper.cs", r"\+=\s*\w+\s*\+\s*separator|result\s*\+=", PRESENT,
            "JoinWithSeparator still concatenates in a loop"),
    "R3":  ("Services/AuthService.cs", _r3_long_method, CUSTOM,
            "GenerateJwtToken still over 12 lines — not split into helpers"),

    # ---- dead code: the symbol's continued existence IS the bug ---------------------
    "D1":  ("Services/AuthService.cs", r"HashPasswordSha1", PRESENT, "unused SHA1 helper"),
    "D3":  ("Data/DatabaseHelper.cs", r"TableExists", PRESENT, "unused TableExists"),
    "D4":  ("Data/DatabaseHelper.cs", r"ExecuteQueryWithParams", PRESENT, "obsolete method retained"),
    "D5":  ("Services/EmailService.cs", r"BuildHtmlTemplate", PRESENT, "unreachable template builder"),
    "D6":  ("Services/EmailService.cs", r"SendWelcomeEmailHtml", PRESENT, "uncalled public method"),
    "D7":  ("Services/TransactionService.cs", r"FormatCurrency", PRESENT, "uncalled helper"),
    "D8":  ("Services/TransactionService.cs", r"IsWithinDailyLimit", PRESENT, "daily limit never enforced"),
    "D9":  ("Helpers/StringHelper.cs", r"ObfuscateAccount", PRESENT, "superseded helper retained"),
    "D10": ("Helpers/StringHelper.cs", r"ToTitleCase", PRESENT, "experimental helper retained"),
    "D11": ("Helpers/StringHelper.cs", r"JoinWithSeparatorFixed", PRESENT, "duplicate implementation retained"),

    # ---- anti-patterns --------------------------------------------------------------
    "A1":  ("Services/UserService.cs", r"static\s+(readonly\s+)?List<string>\s+_auditLog", PRESENT,
            "mutable static audit log"),
    "A2":  ("Helpers/StringHelper.cs", r"static\s+readonly\s+Regex", ABSENT,
            "Regex still constructed per call"),
    "A5":  ("Helpers/StringHelper.cs", _a5_duplicates_bcl, CUSTOM,
            "IsBlank still reimplements the BCL"),

    # ---- configuration --------------------------------------------------------------
    "CF4": ("Program.cs", r"^\s*app\.UseHttpsRedirection\(\)", ABSENT,
            "HTTPS redirection still commented out"),
    "CF5": ("Program.cs", r"IsDevelopment\(\)", ABSENT,
            "developer exception page still unconditional"),
    "CF6": ("Program.cs", r"AllowAnyOrigin", PRESENT, "open CORS policy"),
    "CF7": ("SampleBankingApp.csproj", _cf7_unconditional_symbols, CUSTOM,
            "debug symbols still emitted in Release builds"),
    "CF8": ("SampleBankingApp.csproj", r'Newtonsoft\.Json"\s+Version="12\.', PRESENT,
            "vulnerable Newtonsoft.Json 12.x pinned"),
    "CF9": ("appsettings.Production.json", r".", ABSENT,
            "no environment-specific config file"),
}


def _read(root: Path, rel: str) -> str | None:
    """Whole-tree search when rel is empty; None when a named file is missing."""
    if not rel:
        return "\n".join(
            p.read_text(encoding="utf-8", errors="replace")
            for p in sorted(root.rglob("*.cs"))
        )
    path = root / rel
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def verify(source_root: str | Path) -> dict:
    """Check every marker against the tree. Returns per-issue results and totals."""
    root = Path(source_root)
    rows, still_present, fixed, skipped = [], [], [], []

    for issue_id, (rel, pattern, polarity, meaning) in CHECKS.items():
        text = _read(root, rel)
        if text is None:
            # A missing file is itself the signal for ABSENT checks (CF9), otherwise
            # we cannot judge and say so rather than guessing.
            if polarity is ABSENT:
                rows.append((issue_id, rel, "STILL PRESENT", meaning))
                still_present.append(issue_id)
            else:
                rows.append((issue_id, rel, "unknown (file missing)", meaning))
                skipped.append(issue_id)
            continue

        if polarity is CUSTOM:
            bug_remains = bool(pattern(text))
        else:
            hit = re.search(pattern, text, re.MULTILINE) is not None
            bug_remains = hit if polarity is PRESENT else not hit
        rows.append((issue_id, rel, "STILL PRESENT" if bug_remains else "fixed", meaning))
        (still_present if bug_remains else fixed).append(issue_id)

    return {
        "rows": rows,
        "still_present": still_present,
        "fixed": fixed,
        "unknown": skipped,
        "checked": len(CHECKS) - len(skipped),
        "total_checks": len(CHECKS),
    }


def coverage(issues_md: str | Path = "ISSUES.md") -> tuple[int, int]:
    """(checks defined, reference issues) so the subset is never read as the whole."""
    text = Path(issues_md).read_text(encoding="utf-8", errors="replace")
    ids = re.findall(r"^\|\s*([A-Z]{1,3}\d+)\s*\|", text, re.MULTILINE)
    return len(CHECKS), len(set(ids))


def render(result: dict, checks: int, reference_total: int) -> str:
    """Markdown section for patch_summary.md."""
    remaining = len(result["still_present"])
    lines = [
        "## Mechanical patch verification",
        "",
        f"Direct inspection of the patched source for {checks} of the {reference_total} "
        "seeded issues — those with an unambiguous textual marker. Independent of the "
        "peer reviewer, so it is not affected by review recall or scorer mis-attribution.",
        "",
        f"**{len(result['fixed'])} fixed / {remaining} still present**"
        + (f" / {len(result['unknown'])} undetermined" if result["unknown"] else "")
        + f" (of {result['checked']} checked).",
        "",
    ]
    if result["still_present"]:
        lines += ["| ID | File | Still present |", "|---|---|---|"]
        for issue_id, rel, status, meaning in result["rows"]:
            if status == "STILL PRESENT":
                lines.append(f"| {issue_id} | `{rel or '(tree)'}` | {meaning} |")
        lines.append("")
    lines += [
        "A marker proves the bug's *shape* is gone, not that the replacement is correct — "
        "read this next to the peer review, not instead of it.",
        "",
    ]
    return "\n".join(lines)
