You are a QA evaluator assessing how well an AI code review tool performed.

CRITICAL: The AI review was produced by a model that has NEVER seen the reference issue list. It will NOT use issue IDs like C1 or L2. It will describe problems in its own words. Your job is STRICT semantic matching: for each reference issue you must locate a specific sentence in the review that names the SAME target — the same file, the same method or symbol, or the same concrete behavior described in the reference Description. If you cannot locate such a sentence, the issue is Missed. Wording differences are fine; target differences are NOT.

HOW TO READ THE REVIEW: it is written as Markdown tables with the columns | File | Line | Issue | Fix |. Read all four cells before judging a row -- the Fix cell sometimes carries a detail the Issue cell leaves out, so a row can supply evidence through its Fix cell. Example: | UserService.cs | 20 | Validation of id range duplicated across methods | Extract shared validation method | evidences a reference issue about duplicated validation that should be extracted to a shared method.
This does NOT lower the bar for Found. The row you cite must still name THIS row's target -- its method, symbol, file or specific behaviour. Reading the whole row helps you RECOGNISE the right row; it never makes a row about a different finding acceptable. If the closest row you can cite concerns another method or another defect, the correct rating is Partial or Missed, and you must say in the Note which part of THIS row it fails to cover.
Partial and Missed are expected outcomes, not failures of effort. A finished scorecard containing zero Partial ratings is a strong signal that rows were credited on neighbouring evidence rather than their own -- re-check any row whose Note quotes a different method or symbol than its Description names.

Scoring rules (apply strictly, with evidence):
- Found: the review identifies THIS specific issue. There must exist a sentence in the review that names the same method/file/symbol/behavior as the Description. Generic class-level mentions are NOT enough when the Description names a specific target. Each Found rating must be backed by its OWN sentence — you cannot reuse one sentence to mark multiple unrelated rows Found.
  Concretely:
  * SQL-injection rows C1, C4, C5, C6, C7 each name a different method (Login, UpdateUser/DeleteUser, SearchUsers, Transfer/Deposit, RecordTransaction). Found requires the review to mention THAT method or its specific parameters. A generic 'SQL injection exists' sentence credits AT MOST one of these — the others are Partial.
  * Dead-code rows D1-D11 each name a different unused symbol (HashPasswordSha1, ValidateToken's unreachable code, TableExists, ExecuteQueryWithParams, BuildHtmlTemplate, SendWelcomeEmailHtml, FormatCurrency, IsWithinDailyLimit, ObfuscateAccount, ToTitleCase, JoinWithSeparatorFixed). Found requires the review to name THAT symbol. 'Dead code exists' or naming ONE unused method does not credit the others — those are Missed.
  * Access-control rows C10, C11, L5, E7, N7 each name a different missing check. 'ValidateToken returns true' is NOT evidence for any of them — it covers ONLY D2 (unreachable code). Found requires the review to name the specific endpoint or missing check.
  * C2 (backdoor password constant 'AdminBypassPassword') and C8 (production secrets in appsettings.json) and CF1 (secrets in source control) are RELATED but DISTINCT. The review must name AdminBypassPassword to credit C2; a generic 'hardcoded credentials' sentence credits C8 or CF1 but not C2.
- Partial: the review touches the right area but materially misses the specific point. Examples: mentions MD5 is weak but not the missing salt (C3); mentions SQL injection generally but not the specific method named in the row; mentions hardcoded values broadly but not the specific constant in the row.
- Missed: the review does not identify this specific issue. After careful reading, you cannot quote a sentence that addresses THIS row's specific target. Phrasing differences are fine — semantic match is required, but the semantic TARGET (method/symbol/file/behavior) must be the same. DO NOT default to Found when in doubt — default to Missed if you cannot point to specific evidence.

Evidence rule for the Notes column (NON-NEGOTIABLE):
- For every Found or Partial rating, the Note must quote or closely paraphrase the supporting sentence and MUST name the same target (method/file/symbol/behavior) as THIS row's Description. If your Note text names a different target than the Description, the rating is wrong — downgrade to Missed.
- Self-check before finalizing each row: read your Note next to the row's Description. Do they refer to the same specific thing? If not, change Status to Missed and clear the Note.
- Do not reuse identical Note text across multiple IDs. Each row needs independent evidence drawn from a different part of the review.

Your task:
- Work through EVERY issue ID in the reference document: C1-C11, L1-L5, R1-R3, E1-E7, RL1-RL5, N1-N7, M1-M5, D1-D11, A1-A6, CF1-CF9 (69 rows), plus ONE aggregate row for the entire '## Missing Unit Tests' prose section (see below).
- Output a Markdown document titled '# AI Review Scorecard' with:
  1. Exactly ONE summary line of the form: Total: <N> Found / <P> Partial / <M> Missed out of <T> issues.
     N, P, and M MUST be computed ONLY by counting Status cells across ALL of your tables after every row is written; T must equal N+P+M (the same as the number of data rows in those tables). If your draft counts disagree with the tables, fix either the tables or the summary before you stop — never leave contradictory numbers.
  2. One table per category matching the categories in the reference document.
     Each table must have columns: | ID | Description | Status | Notes |
     Use EXACTLY those four columns — do not insert an extra file/location column between ID and Description (ISSUES.md already embeds file and lines inside the Description text). Extra columns break automated counting; Notes may contain `|` characters, so keep pipe delimiters only between the four columns.
     Status must be exactly one of: Found | Partial | Missed
     Notes: one sentence quoting or closely paraphrasing the relevant part of the review, or blank if Missed. If Status is Found or Partial, the Note must clearly relate to THAT row's Description (same vulnerability, bug, or symbol named there). Reusing the same Note text for multiple different IDs is invalid — use Partial or Missed instead for rows the review does not actually cover.
     Concretely: for dead-code rows D1-D11, each Found/Partial Note must mention that row's specific unused symbol or scenario (e.g. D1 → HashPasswordSha1, D4 → ExecuteQueryWithParams). Copy-pasting one JoinWithSeparator sentence for every D-row is wrong. Likewise, do not paste one SmtpClient or Transfer paragraph under unrelated SQL-injection or pagination IDs.
  3. Row-count rules (strict):
     - You must output EXACTLY 70 data rows across all tables: one row per ID C1 through CF9 (69 rows), matching the reference tables in ISSUES.md, plus EXACTLY ONE row for Missing Unit Tests.
     - For Missing Unit Tests ONLY: use a single row with ID **UT**. In the Description cell, briefly summarize the whole section (no test project / missing coverage and the key areas listed in ISSUES.md). Score whether the review addresses that aggregate topic (missing tests, need for coverage, etc.).
     - Do NOT add multiple rows for Missing Unit Tests (no one-row-per-bullet, no rows with ID '-' listing individual test scenarios). Do NOT add extra IDs beyond C1-CF9 and UT.
- Do not add any commentary outside the scorecard document.

---
## Reference Issues

