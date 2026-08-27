# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22`

> ⚠ **2 row(s) do not line up with ISSUES.md** (RL2, A6). The scorer dropped or renumbered rows, so these IDs were scored against a different issue -- their ratings, Notes and spot-check verdicts are void and the totals below are unreliable.

> ⚠ **4 row(s) rated Found name a target that never appears in the review** (D6, D9, D11, CF8). Adjusted Found: **25** of 70. See the spot-check below.

Total: 29 Found / 11 Partial / 30 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review identifies SQL injection vulnerability in Login method using string interpolation |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review identifies hardcoded admin bypass password "SuperAdmin2024" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review identifies weak MD5 hashing used for password storage |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Partial | Review mentions SQL injection in ExecuteQuery method but doesn't specifically name UpdateUser/DeleteUser methods |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Partial | Review mentions SQL injection in ExecuteQuery method but doesn't specifically name SearchUsers method |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Partial | Review mentions string interpolation for SQL in ExecuteNonQuery but doesn't specifically name Transfer/Deposit methods |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Partial | Review mentions SQL injection in ExecuteQuery method but doesn't specifically name RecordTransaction method |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review identifies hardcoded default connection string with password "Admin1234!" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review identifies JWT ValidateLifetime set to false allowing infinite token validity |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Missed | Review does not mention specific endpoint or missing access control check |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Missed | Review does not mention specific endpoint or missing authorization check |

## Logic Errors

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Partial | Review identifies insufficient funds check missing transaction fee but doesn't address zero-value transfer logic |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review identifies insufficient funds check missing transaction fee in Transfer method |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review identifies pagination off-by-one error using page * pageSize instead of (page-1) * pageSize |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | Review mentions hardcoded interest bonus rate but doesn't specifically identify the incorrect 0.05m value |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Missed | Review does not mention self-transfer validation |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Missed | Review does not mention duplicated validation or suggest extraction to shared method |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review identifies string concatenation in loop (O(n²)) and suggests replacement with string.Join |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | Review does not mention GenerateJwtToken method or suggest refactoring |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Partial | Review mentions swallowing exceptions in SearchUsers but doesn't specifically identify the problem of returning empty list vs. exception |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Missed | Review does not mention SendWelcomeEmail method or broad exception handling |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Review identifies no transaction for multiple database updates in Transfer method |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Missed | Review does not mention email failure propagation or transaction consistency issues |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Review identifies exposing raw exception messages to clients |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Partial | Review mentions connection not properly disposed but doesn't specifically identify ExecuteNonQuery method |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed | Review does not mention rate limiting or account lockout |

## Resource Leaks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review identifies SqlConnection not properly disposed in Login method |
| RL2 | `Data/DatabaseHelper.cs` | ~26 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Partial | Review mentions connection opened but not guaranteed to be closed but doesn't specifically identify GetOpenConnection |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review identifies connection opened but not properly disposed in ExecuteQuery method |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review identifies SmtpClient as instance field (not thread-safe) |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Missed | Review does not mention MailMessage disposal |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Missed | Review does not mention JWT secret null handling |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Review identifies no null check before accessing DataTable.Rows[0] |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Missed | Review does not mention SMTP port parsing or null handling |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | Review does not mention username null handling |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Missed | Review does not mention email/username length null checks |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Review identifies no null check before int.Parse on userIdClaim |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Missed | Review does not mention null request checking |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review identifies hardcoded transaction fee rate 0.015m |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Partial | Review mentions hardcoded max transactions per day but doesn't specifically identify the 1_000_000 value |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Missed | Review does not mention email address literals |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Missed | Review does not mention specific numeric literals |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Partial | Review mentions hardcoded transaction fee rate but doesn't specifically identify page size limit |

## Dead Code

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Missed | Review does not mention HashPasswordSha1 method |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Missed | Review does not mention ValidateToken unreachable code |
| D3 | `TableExists` — never called from any service or controller. | Missed | Review does not mention TableExists method |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review identifies obsolete ExecuteQueryWithParams still present |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Missed | Review does not mention BuildHtmlTemplate method |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Review identifies unused SendWelcomeEmailHtml method |
| D7 | `FormatCurrency` — private, never called. | Missed | Review does not mention FormatCurrency method |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Missed | Review does not mention IsWithinDailyLimit method |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Review identifies JoinWithSeparator not used anywhere in codebase |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Missed | Review does not mention ToTitleCase method |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review identifies JoinWithSeparator not used anywhere in codebase |

## Anti-patterns

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Missed | Review does not mention static fields or thread safety issues |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Missed | Review does not mention regex compilation issues |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review identifies string concatenation in loop (O(n²)) and suggests replacement with string.Join |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Review identifies SmtpClient as instance field (not thread-safe) |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Missed | Review does not mention IsBlank method |
| A6 | `Data/DatabaseHelper.cs` | ~26 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Missed | _(ungrounded: no matching sentence in review)_ |

## Configuration Issues

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies hardcoded default connection string with password "Admin1234!" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Missed | Review does not mention log levels or debug logging |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies JWT ValidateLifetime set to false allowing infinite token validity |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review identifies HTTPS redirection commented out |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review identifies UseDeveloperExceptionPage called unconditionally |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review identifies overly permissive CORS policy |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Missed | Review does not mention debug symbols or PDB files |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | Review identifies outdated NuGet packages |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Review identifies missing environment-specific config overrides |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results | Missed | _(ungrounded: no matching sentence in review)_ |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Partial | `SearchUsers` | yes | under-credited? |
| C7 | Partial | `RecordTransaction` | **no** | **UNSUPPORTED** |
| R3 | Missed | `GenerateJwtToken` | **no** | - |
| E7 | Missed | `rate limit` | **no** | - |
| N3 | Missed | `SmtpPort` | **no** | - |
| D1 | Missed | `HashPasswordSha1` | **no** | - |
| D3 | Missed | `TableExists` | yes | under-credited? |
| D4 | Found | `ExecuteQueryWithParams` | yes | - |
| D5 | Missed | `BuildHtmlTemplate` | **no** | - |
| D6 | Found | `SendWelcomeEmailHtml` | **no** | **MIS-CREDIT** |
| D7 | Missed | `FormatCurrency` | **no** | - |
| D8 | Missed | `IsWithinDailyLimit` | **no** | - |
| D9 | Found | `ObfuscateAccount` | **no** | **MIS-CREDIT** |
| D10 | Missed | `ToTitleCase` | **no** | - |
| D11 | Found | `JoinWithSeparatorFixed` | **no** | **MIS-CREDIT** |
| CF9 | Found | `appsettings.Production` | yes | - |
| UT | Missed | `Tests.csproj` | yes | under-credited? |
| C2 | Found | `SuperAdmin2024` | yes | - |
| C3 | Found | `MD5` | yes | - |
| C9 | Found | `ValidateLifetime` | yes | - |
| L3 | Found | `GetUsersPage` | yes | - |
| L4 | Partial | `0.05` | yes | under-credited? |
| E1 | Partial | `SearchUsers` | yes | under-credited? |
| E5 | Found | `ex.Message` | yes | - |
| RL4 | Found | `SmtpClient` | yes | - |
| RL5 | Missed | `MailMessage` | **no** | - |
| N2 | Found | `Rows[0]` | yes | - |
| N4 | Missed | `ToUpper` | **no** | - |
| M1 | Found | `TransactionFeeRate` | yes | - |
| M2 | Partial | `1000000` | **no** | **UNSUPPORTED** |
| D2 | Missed | `ValidateToken` | **no** | - |
| A1 | Missed | `_auditLog` | yes | under-credited? |
| A2 | Missed | `Regex` | **no** | - |
| A5 | Missed | `IsBlank` | **no** | - |
| CF3 | Found | `ValidateLifetime` | yes | - |
| CF4 | Found | `UseHttpsRedirection` | yes | - |
| CF5 | Found | `UseDeveloperExceptionPage` | yes | - |
| CF6 | Found | `AllowAnyOrigin` | yes | - |
| CF7 | Missed | `DebugType` | **no** | - |
| CF8 | Found | `Newtonsoft` | **no** | **MIS-CREDIT** |

**Adjusted Found: 25 of 70** (29 reported, less 4 mis-credited).

> **2 row(s) rated `Partial` whose target string appears NOWHERE in the review** (C7, M2). A Partial on an unmentioned issue is a Missed; the reported Missed count is correspondingly understated.

> **6 row(s) rated `Partial`/`Missed` whose target string IS present in the review** (C5, D3, UT, L4, E1, A1). The score is left as the scorer rated it; read these rows before trusting the Missed count.

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3-32B-imatrix:Q4_K_M` |
| Reasoning strength (system prompt) | (model default) |
| System prompt | `You are an expert computer programmer with an eye for detail, who loves to provide high quality answers.` |
| Ollama `think` | (unset) |
| Temperature | `0.0` |
| top_p | (model default) |
| top_k | (model default) |
| Effort (Anthropic only) | (n/a) |
| num_ctx | `65536` |
| num_predict | `40000` |
| Source truncated | `no` |
| Review prompt SHA-256 | `82bd5f768ca9` |
| Scorer model | `Qwen3-Coder-30B-imatrix:Q3_K_M` |
| Scorer temperature | `0.0` |
| Scorer reasoning | (model default) |
| Scorer system prompt | `You are an expert computer programmer with an eye for detail, who loves to provide high quality answers.` |
| Scorer `think` | (unset) |
| Scorer attempts | `1` |
| Grounding mode | `enforce` |
| Grounding downgrades | `2` |
| Self-declared-absent downgrades | `0` |
| Rows misaligned with ISSUES.md | `2` |
| Review citations past end of file | `0 of 44` |
| Precision (checkable Found rows) | `78% (14 of 18)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 67ece22` |
