"""Scorecard post-processing shared by ai_code_review.yml and scorer_benchmark.yml.

Every function takes the scorer's raw Markdown and returns a corrected version or a
verdict. Nothing here calls a model; it is all deterministic text analysis, which is the
point -- these checks have to be trustworthy when the scorer is not.

Kept in one file because the same logic was previously copy-pasted into the benchmark
workflow and silently drifted 1,236 characters behind production.
"""
import re
import sys

_STATUS_CELL = re.compile(r"\|\s*(Found|Partial|Missed)\s*\|", re.IGNORECASE)
_ROW_ID = re.compile(r"^\|\s*\*{0,2}([A-Z]{1,3}\d*|UT)\*{0,2}\s*\|", re.IGNORECASE)

# Minimum fraction of a Note's content words that must appear in a single
# line of the review for that Note to count as evidence. Tuned against run
# #133, where the scorer invented three quotes by copying ISSUES.md wording
# verbatim (D6 scored 0.43, N4 0.33, D10 0.17) while every legitimate row
# scored >= 0.55.
_GROUNDING_MIN = 0.5
# Fallback for Notes that legitimately summarise several review lines at once
# (the aggregate UT row, or a Note citing two findings). A Note can clear the
# check on whole-review vocabulary alone, but only at a much higher bar.
_GROUNDING_VOCAB_MIN = 0.8
_QUOTED = re.compile(r'"([^"]{4,})"')
_STOPWORDS = frozenset(
    "the a an is are was were be been in on of to and or for with without not "
    "no this that it its as at by from than then so if but review mentions "
    "does doesn specifically name named issue context".split()
)

def _content_words(text: str) -> set:
    text = re.sub(r"[^a-z0-9_]+", " ", text.lower())
    return {w for w in text.split() if len(w) > 2 and w not in _STOPWORDS}

def _evidence_text(note: str) -> str:
    """Isolate the quoted evidence inside a Note.

    Scorers commonly write: "file" line N: "quoted finding" - explanation of
    what it does or does not cover. That trailing explanation is drawn from
    the reference issue, not the review, so matching the whole Note punishes
    correctly-evidenced rows. Match the quoted spans when there are any.
    """
    quoted = " ".join(_QUOTED.findall(note))
    return quoted if len(_content_words(quoted)) >= 3 else note

def drop_duplicate_ids(md: str) -> str:
    """Keep the first row per issue ID; models sometimes emit an ID twice
    with contradictory statuses, which inflates the denominator."""
    seen, out, dropped = {}, [], []
    for line in md.splitlines():
        m_id = _ROW_ID.match(line.strip())
        m = _STATUS_CELL.search(line)
        if m_id and m:
            rid = m_id.group(1).upper()
            status = m.group(1).capitalize()
            if rid in seen:
                dropped.append((rid, seen[rid], status))
                continue
            seen[rid] = status
        out.append(line)
    for rid, kept, dup in dropped:
        print(
            f"WARN: duplicate scorecard row for {rid} "
            f"(kept '{kept}', dropped '{dup}').",
            file=sys.stderr,
        )
    return "\n".join(out)

def reference_ids(issues_text: str) -> set:
    """The IDs ISSUES.md actually defines, plus the synthetic UT row.

    UT has no table row of its own -- Missing Unit Tests is a prose section with
    a bullet list -- so it is added explicitly rather than parsed.
    """
    ids = set()
    for line in issues_text.splitlines():
        m = _ROW_ID.match(line.strip())
        if m:
            ids.add(m.group(1).upper())
    ids.add("UT")
    return ids


def drop_unknown_ids(md: str, issues_text: str):
    """Drop rows whose ID is not defined in ISSUES.md.

    Distinct from drop_duplicate_ids, which keys on a REPEATED id. A scorer that
    invents a new id gets past that check, and every such row is scored twice
    over: once under its real id and once under the invention. It also corrupts
    the denominator, which is counted from the emitted rows.
    """
    known = reference_ids(issues_text)
    out, dropped = [], []
    for line in md.splitlines():
        m_id = _ROW_ID.match(line.strip())
        if m_id and _STATUS_CELL.search(line):
            rid = m_id.group(1).upper()
            if rid not in known:
                dropped.append(rid)
                continue
        out.append(line)
    for rid in dropped:
        print(
            f"WARN: dropped scorecard row '{rid}' -- no such issue in ISSUES.md.",
            file=sys.stderr,
        )
    return "\n".join(out), dropped


def enforce_note_grounding(md: str, review_text: str, mode: str):
    """Downgrade Found/Partial rows whose Notes are not supported by the review.

    The scorer is asked to quote the review, but it can instead paraphrase the
    reference issue back at us -- producing confident evidence for text the
    review never contained. Comparing each Note against the review the scorer
    actually received catches that mechanically.
    """
    if mode == "off":
        return md, []
    spans = [_content_words(l) for l in review_text.splitlines() if l.strip()]
    spans = [s for s in spans if s]
    if not spans:
        print("WARN: review has no comparable text; skipping grounding check.",
              file=sys.stderr)
        return md, []
    review_vocab = set().union(*spans)

    out, downgraded = [], []
    for line in md.splitlines():
        m_id = _ROW_ID.match(line.strip())
        m = _STATUS_CELL.search(line)
        if not m_id or not m:
            out.append(line)
            continue
        status = m.group(1).capitalize()
        if status == "Missed":
            out.append(line)
            continue
        note_words = _content_words(_evidence_text(line[m.end():].lstrip("|")))
        if len(note_words) < 3:
            out.append(line)
            continue
        best = max(len(note_words & s) / len(note_words) for s in spans)
        vocab = len(note_words & review_vocab) / len(note_words)
        if best >= _GROUNDING_MIN or vocab >= _GROUNDING_VOCAB_MIN:
            out.append(line)
            continue
        rid = m_id.group(1).upper()
        downgraded.append((rid, status, round(best, 2)))
        if mode == "enforce":
            line = (line[: m.start()]
                    + "| Missed | _(ungrounded: no matching sentence in review)_ |")
        out.append(line)

    if downgraded:
        verb = "Downgraded" if mode == "enforce" else "Would downgrade"
        print(
            f"WARN: {verb} {len(downgraded)} scorecard row(s) whose Notes are not "
            f"supported by review.md: "
            + ", ".join(f"{r}({s}, overlap {b})" for r, s, b in downgraded),
            file=sys.stderr,
        )
    return "\n".join(out), downgraded

# ------------------------------------------------------------------------
# Self-declared absence.
#
# A Note that says the review never mentions the issue, on a row that still
# awards credit. Distinct from the ordinary Partial hedge ("addresses X but not
# Y"), which is what Partial legitimately means -- these assert that NOTHING was
# found. Across the archive the pattern hits 46 Missed rows (correct usage), 6
# Partial rows and zero Found rows, so it discriminates rather than firing
# everywhere.
#
# Downgraded rather than merely flagged: unlike a missing watchlist target, this
# is the scorer's own statement that there is no evidence, which is the same
# standing as an ungrounded Note.
# ------------------------------------------------------------------------
_SELF_DECLARED_ABSENT = re.compile(
    r"no (?:specific|explicit)? ?mention"
    r"|no matching sentence"
    r"|not mentioned (?:at all )?in the review"
    r"|(?:the )?review does not (?:mention|address|discuss|cover)"
    r"|does not appear in the review",
    re.IGNORECASE,
)


_CODE_SPAN = re.compile(r"`([^`]+)`")
_ALIGN_MIN = 0.5


def _row_cells(line: str):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _descriptions(text: str, idx: int):
    """Map ID -> Description cell. idx is -1 for ISSUES.md (4 columns: id, file,
    line, description) and 1 for a scorecard (id, description, status, notes)."""
    out = {}
    for line in text.splitlines():
        c = _row_cells(line)
        if len(c) > abs(idx) and re.fullmatch(r"\*{0,2}([A-Z]{1,3}\d*|UT)\*{0,2}", c[0]):
            out.setdefault(c[0].strip("*").upper(), c[idx])
    return out


# File extensions and type names carry no information about WHICH issue a row is
# about. Without this, reference CF8 (`Newtonsoft.Json`) and a misaligned row
# holding CF9 (`appsettings.Production.json`) share the token "json" and the
# misalignment is missed.
_IDENT_STOP = frozenset({
    "json", "xml", "config", "csproj", "cshtml", "http", "https", "true",
    "false", "null", "string", "value", "class", "method", "public", "private",
    "static", "void", "async", "task", "list", "type", "name", "file", "line",
})


def _identifiers(text: str) -> set:
    """Identifiers named inside code spans -- the subject of the issue.

    Only these distinguish a reworded row from a misaligned one, so generic
    tokens are dropped: they are shared by issues that have nothing to do with
    each other.
    """
    out = set()
    for span in _CODE_SPAN.findall(text):
        for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", span):
            low = tok.lower()
            if low not in _IDENT_STOP:
                out.add(low)
    return out


def check_row_alignment(md: str, issues_text: str):
    """Find rows whose Description does not match the reference issue for that ID.

    A scorer that omits one row and renumbers the rest produces a sheet where
    every ID after the gap is scored against the wrong issue. That is corruption
    rather than a bad judgement: the ratings, the Notes and the spot-check
    verdicts for those IDs all describe something else.

    Two conditions, because scorers legitimately reword: the Description must
    both share little vocabulary with the reference AND name none of the same
    code identifiers.
    """
    ref = _descriptions(issues_text, -1)
    got = _descriptions(md.split("## Evidence Spot-Check")[0], 1)
    misaligned, missing = [], []
    for rid, ref_desc in ref.items():
        if rid not in got:
            missing.append(rid)
            continue
        a, b = _content_words(ref_desc), _content_words(got[rid])
        sim = len(a & b) / max(len(a | b), 1)
        if sim >= _ALIGN_MIN:
            continue
        if _identifiers(ref_desc) & _identifiers(got[rid]):
            continue  # reworded, same subject
        misaligned.append((rid, round(sim, 2)))

    if misaligned or missing:
        print(
            "ERROR: scorecard rows do not line up with ISSUES.md. "
            + (f"Misaligned (scored against another issue): "
               f"{', '.join(f'{r}({s})' for r, s in misaligned)}. " if misaligned else "")
            + (f"Absent from the scorecard: {', '.join(missing)}. " if missing else "")
            + "Ratings for these IDs describe a different issue and cannot be trusted.",
            file=sys.stderr,
        )
    return misaligned, missing


def downgrade_self_declared_absent(md: str):
    """Rate as Missed any Found/Partial row whose Note declares no evidence."""
    out, downgraded = [], []
    for line in md.splitlines():
        m_id = _ROW_ID.match(line.strip())
        m = _STATUS_CELL.search(line)
        if not m_id or not m:
            out.append(line)
            continue
        status = m.group(1).capitalize()
        note = line[m.end():].lstrip("|").strip().rstrip("|").strip()
        # "ungrounded" rows are already Missed from the grounding pass, and their
        # standard wording contains "no matching sentence" -- skip, do not double-count.
        if status == "Missed" or "ungrounded" in note.lower():
            out.append(line)
            continue
        if not _SELF_DECLARED_ABSENT.search(note):
            out.append(line)
            continue
        downgraded.append((m_id.group(1).upper(), status))
        out.append(line[: m.start()] + "| Missed | " + note
                   + " _(downgraded: Note states the review does not cover this)_ |")

    if downgraded:
        print(
            f"WARN: downgraded {len(downgraded)} row(s) whose own Note says the review "
            "never mentions the issue: "
            + ", ".join(f"{r}({s})" for r, s in downgraded),
            file=sys.stderr,
        )
    return "\n".join(out), downgraded


def count_table_statuses(md: str) -> tuple[int, int, int]:
    """Count Found / Partial / Missed from scorecard tables.

    Rows must be | ID | Description | Status | Notes | but models sometimes insert an
    extra column (e.g. file path) or put pipes inside Notes. Naive split("|") then mis-
    classifies Status. We detect the Status column by the first | Found|Partial|Missed |
    marker, which precedes the Notes cell (even when Notes contains additional pipes).
    """
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
        # Markdown separator row (first cell is ---)
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
    """Emit WARN when the scorer pasted identical Notes for many distinct issue IDs."""
    from collections import defaultdict

    note_to_ids = defaultdict(list)
    for raw in md.splitlines():
        line = raw.strip()
        if not line.startswith("|"):
            continue
        m_id = _ROW_ID.match(line)
        if not m_id:
            continue
        issue_id = m_id.group(1).upper()
        if issue_id == "ID":
            continue
        if re.match(r"^-{3,}$", issue_id):
            continue
        m = _STATUS_CELL.search(line)
        if not m:
            continue
        status = m.group(1).lower()
        if status not in ("found", "partial"):
            continue
        notes = line[m.end() :].lstrip("|").strip()
        if len(notes) < 20:
            continue
        norm = re.sub(r"\s+", " ", notes).strip().lower()
        note_to_ids[norm].append(issue_id)

    for norm, ids in note_to_ids.items():
        if len(ids) >= 3:
            uniq = sorted(set(ids), key=lambda x: (len(x), x))
            preview = norm[:140] + ("…" if len(norm) > 140 else "")
            print(
                "WARN: Scorecard reused the same Notes text for "
                f"{len(uniq)} issues ({', '.join(uniq)}). "
                "Scorer model ignored per-issue Notes rules; compare review.md. "
                f"Example: {preview!r}",
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
    # No matching summary line — insert machine-derived counts after the first line.
    insert = "\n" + new_line + "\n"
    first_nl = md.find("\n")
    if first_nl != -1:
        return md[: first_nl + 1] + insert + md[first_nl + 1 :]
    return insert + md


# ------------------------------------------------------------------------
# Evidence spot-check.
#
# Hand-picked rows whose target is an unambiguous string. If that string does
# not appear ANYWHERE in the review, the review cannot have found the issue --
# absence is decisive, and no threshold or similarity metric is involved. The
# converse does NOT hold: a review can name GenerateJwtToken while saying
# nothing about splitting it, so a present target is not proof of a correct
# Found. Only the Found-but-absent direction is treated as an error.
#
# Curated by hand precisely because the automatic versions of this check were
# tried and failed: identifier matching against Descriptions ran at ~31%
# precision, and restricting to source-defined method names caught nothing.
# ------------------------------------------------------------------------
WATCHLIST = {
    # --- original entries -------------------------------------------------
    "C5":  ["SearchUsers"],
    "C7":  ["RecordTransaction"],
    "R3":  ["GenerateJwtToken"],
    "E7":  ["rate limit", "rate-limit", "ratelimit", "lockout",
            "brute force", "brute-force", "throttl"],
    "N3":  ["SmtpPort"],
    "D1":  ["HashPasswordSha1"],
    "D3":  ["TableExists"],
    "D4":  ["ExecuteQueryWithParams"],
    "D5":  ["BuildHtmlTemplate"],
    "D6":  ["SendWelcomeEmailHtml"],
    "D7":  ["FormatCurrency"],
    "D8":  ["IsWithinDailyLimit"],
    "D9":  ["ObfuscateAccount"],
    "D10": ["ToTitleCase"],
    "D11": ["JoinWithSeparatorFixed"],
    "CF9": ["appsettings.Production", "Production.json"],
    # UT is the only reference issue whose evidence is prose rather than a
    # table row, and it sits in the last section of the review -- the two
    # things that make a scorer most likely to lose it. Both targets name a
    # file that does not exist, so a mention can only be the review noting
    # its absence.
    # Widened after a temperature-0 Muse-Glimmer run was flagged: its review
    # carries a full "Missing Unit Tests" section covering Login,
    # GenerateJwtToken, Transfer, Deposit and GetUsersPage -- the very areas
    # the reference issue lists -- while never using the words "Tests.csproj"
    # or "test project". Absence of those strings was not proof of anything.
    "UT":  ["Tests.csproj", "test project", "unit test", "lacks tests",
            "no test"],

    # --- added after the Muse-Glimmer-30B run -----------------------------
    # That sheet reported 70/70 with four mis-credits caught. Four more were
    # invisible because the rows had no entry here: R3, N4, N7 and M1 each
    # carried a Note quoting a real finding about a DIFFERENT issue. R3 was
    # already listed and still slipped, because its target genuinely appears
    # in the review -- attached to the token-lifetime finding. That is the
    # limit of a string test and the reason these are additions rather than
    # a redesign.
    #
    # Every target below is an exact source identifier or literal constant,
    # held to the same bar as the originals: a review that engages with the
    # issue at all essentially must name it. Loose paraphrase targets were
    # considered and rejected -- N7 ("request == null") has no such string,
    # since reviews phrase it a dozen ways, and a target a correct review
    # might not use manufactures false mis-credits. N7 is therefore still
    # absent by choice, not oversight.
    # Widened: most reviews name the CONSTANT or call it a backdoor and never
    # quote the literal password, so "SuperAdmin2024" alone flagged 7 of 19
    # archived runs that had all found it.
    "C2":  ["SuperAdmin2024", "AdminBypassPassword", "bypass password",
            "backdoor"],
    "C3":  ["MD5"],
    "C9":  ["ValidateLifetime"],
    "L3":  ["GetUsersPage"],
    "L4":  ["0.05", "5%"],
    "E1":  ["SearchUsers"],
    "E5":  ["ex.Message", "exception message"],
    "RL4": ["SmtpClient"],
    "RL5": ["MailMessage"],
    "N2":  ["Rows[0]", "Rows.Count"],
    "N4":  ["ToUpper"],
    # Widened: reviews commonly cite the value 0.015 rather than the identifier.
    "M1":  ["TransactionFeeRate", "MaxTransactionsPerDay", "0.015", "fee rate"],
    "M2":  ["1000000", "1_000_000"],
    "D2":  ["ValidateToken"],
    "A1":  ["_auditLog"],
    "A2":  ["Regex"],
    "A5":  ["IsBlank"],
    "CF3": ["ValidateLifetime"],
    # Widened: "HTTPS redirection is commented out" is the usual phrasing and
    # contains a space, so it never matched the method name.
    "CF4": ["UseHttpsRedirection", "HttpsRedirection", "https redirect"],
    "CF5": ["UseDeveloperExceptionPage", "DeveloperExceptionPage",
            "developer exception"],
    # Widened: "CORS policy allows any origin" is the usual phrasing.
    "CF6": ["AllowAnyOrigin", "any origin"],
    "CF7": ["DebugType", "DebugSymbols"],
    "CF8": ["Newtonsoft"],
}

def spot_check(md, review_text):
    status_by_id = {}
    for line in md.splitlines():
        m_id = _ROW_ID.match(line.strip())
        m = _STATUS_CELL.search(line)
        if m_id and m:
            status_by_id.setdefault(m_id.group(1).upper(), m.group(1).capitalize())
    low = review_text.lower()
    rows, miscredits, undercredits, unsupported = [], [], [], []
    for rid, targets in WATCHLIST.items():
        status = status_by_id.get(rid)
        if status is None:
            continue
        present = any(t.lower() in low for t in targets)
        verdict = "-"
        if status == "Found" and not present:
            verdict = "**MIS-CREDIT**"
            miscredits.append(rid)
        elif status == "Partial" and not present:
            # A Partial on an issue the review never mentions is not partial
            # coverage -- it is a Missed with a consolation prize. Tracked
            # separately from mis-credits because Partial does not feed
            # Adjusted Found, so there is nothing to deduct; the harm is to any
            # Found + 0.5*Partial ranking, and to the Missed count, which reads
            # as zero when the real figure is not.
            verdict = "**UNSUPPORTED**"
            unsupported.append(rid)
        elif status in ("Partial", "Missed") and present:
            verdict = "under-credited?"
            undercredits.append(rid)
        # Missed-and-absent is the one combination that needs no flag: the
        # scorer and the evidence agree.
        rows.append((rid, status, targets[0], "yes" if present else "**no**", verdict))
    return rows, miscredits, undercredits, unsupported

# ------------------------------------------------------------------------
# Self-hedged ratings.
#
# The scorer sometimes writes the counter-argument into its own Note and then
# records Found anyway -- "implicitly covering the null request case", "does not
# specifically name the fee rate". That phrasing describes a Partial. It is a
# far better signal than the Partial count: on the Qwen3.8-27B run it caught 3
# of the 4 over-credits with zero false positives across 70 rows, whereas the
# zero-Partial heuristic fired on a review that was genuinely near-perfect.
#
# Reported, never auto-applied: a hedged Note can still sit on a correct Found
# when the conceded detail is incidental to the reference issue.
# ------------------------------------------------------------------------
_HEDGE = re.compile(
    r"implicitly"
    r"|does not (?:specifically|explicitly)?\s*(?:name|mention|cover|address)"
    r"|but does not|though it does not|without naming|only partially"
    r"|not specifically name"
    # N4 was rated Found with the Note "there's no specific mention of
    # username.ToUpper()". The clauses above only caught the verb form
    # ("does not specifically mention"), not the noun form.
    r"|no (?:specific|explicit) ?mention|no mention of",
    re.IGNORECASE,
)

def hedge_check(md):
    out = []
    for line in md.splitlines():
        m_id = _ROW_ID.match(line.strip())
        m = _STATUS_CELL.search(line)
        if not m_id or not m or m.group(1).lower() != "found":
            continue
        note = line[m.end():].lstrip("|").strip().rstrip("|").strip()
        if len(note) < 25:
            continue
        hit = _HEDGE.search(note)
        if hit:
            out.append((m_id.group(1).upper(), hit.group(0), note))
    return out
