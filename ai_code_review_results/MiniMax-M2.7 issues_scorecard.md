# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22`

> ⚠ **1 row(s) rated Found name a target that never appears in the review** (D11). Adjusted Found: **57** of 70. See the spot-check below.

Total: 58 Found / 7 Partial / 5 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review identifies SQL injection via string interpolation in Login: `sql = $"SELECT * FROM Users WHERE Username = '{username}' AND Password = '{hashedPassword}' AND IsActive = 1"` |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review identifies hardcoded admin bypass password constant: `AdminBypassPassword = "SuperAdmin2024"` |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review identifies MD5 hashing used for password storage (broken cryptography) |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Review identifies SQL injection via string interpolation in UpdateUser |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | Review identifies SQL injection via string interpolation in SearchUsers |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Review identifies SQL injection via string interpolation in balance updates |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Review identifies SQL injection via string interpolation in RecordTransaction |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review identifies hardcoded production database password |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review identifies JWT ValidateLifetime set to false |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | Review identifies UpdateUser endpoint missing authorization attribute |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | Review identifies DeleteUser endpoint missing authorization attribute |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Review identifies that only checks `amount < 0` but should also reject zero |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review identifies that balance check uses `fromBalance >= amount` but deduction is `amount + fee` |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review identifies off-by-one error in pagination: `skip = page * pageSize` should be `(page - 1) * pageSize` |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | Review identifies interest bonus rate 0.05m hardcoded but doesn't specifically name this exact issue |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Review identifies no validation that fromUserId != toUserId |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | Review identifies that GetUserById and UpdateUser share identical ID validation block |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review identifies string concatenation in loop (O(n²)) |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | _(ungrounded: no matching sentence in review)_ |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Review identifies that SearchUsers catches all exceptions and returns empty list |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Missed | _(ungrounded: no matching sentence in review)_ |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Review identifies that two separate ExecuteNonQuery calls without transaction wrapping |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response.** | Found | Review identifies email sending occurs after DB write with no rollback on failure |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Review identifies that raw exception message exposed to client |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | Review identifies that connection and reader not disposed on all code paths |
| E7 | **No rate limiting or account lockout on failed login attempts** — brute force is trivially possible. | Found | Review identifies no rate limiting on login endpoint |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review identifies SqlConnection created but never disposed |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | Review identifies GetOpenConnection returns connection caller must dispose with no contract |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review identifies ExecuteNonQuery creates connection via GetOpenConnection but never disposes it |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review identifies SmtpClient held as instance field (not thread-safe, socket not released) |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review identifies MailMessage created but never disposed |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Review identifies jwtSecret used with ! but no runtime null guard |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Review identifies fromUserTable.Rows[0] and toUserTable.Rows[0] accessed without checking Rows.Count > 0 |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | Review identifies SmtpClient constructed with potentially null config values but doesn't specifically name this issue |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | _(ungrounded: no matching sentence in review)_ |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Missed | _(ungrounded: no matching sentence in review)_ |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Partial | Review identifies that fromUserTable.Rows.Count == 0 before accessing Rows[0] but doesn't specifically name this issue |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | Review identifies UpdateUser endpoint missing authorization attribute |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review identifies transaction fee rate 0.015m hardcoded |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | Review identifies deposit cap 1000000 hardcoded |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Review identifies "notifications@company.com" hardcoded in multiple places |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Missed | _(ungrounded: no matching sentence in review)_ |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Review identifies max page size 50 hardcoded |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review identifies HashPasswordSha1 method never called |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Review identifies unconditional return true before actual validation code |
| D3 | `TableExists` — never called from any service or controller. | Partial | Review mentions TableExists but doesn't specifically name this dead code |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review identifies ExecuteQueryWithParams marked [Obsolete] but still exists |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Partial | Review mentions BuildHtmlTemplate but doesn't specifically name this dead code |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Review identifies SendWelcomeEmailHtml method never called |
| D7 | `FormatCurrency` — private, never called. | Found | Review identifies FormatCurrency method never called |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Partial | Review mentions IsWithinDailyLimit but doesn't specifically name this dead code |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Review identifies ObfuscateAccount method never called |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | Review identifies ToTitleCase method never called |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review identifies JoinWithSeparator method never called |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | Review mentions static mutable fields but doesn't specifically name this anti-pattern |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Review identifies new Regex created inside IsValidEmail method |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review identifies string concatenation in loop (O(n²)) |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Review identifies SmtpClient held as instance field (not thread-safe, socket not released) |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | Review identifies IsBlank duplicates string.IsNullOrWhiteSpace |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | Review identifies GetOpenConnection returns SqlConnection with no documented ownership contract |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies hardcoded production database password |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Review identifies debug log level set for production |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies JWT ValidateLifetime set to false |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review identifies HTTPS redirection commented out |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review identifies UseDeveloperExceptionPage called unconditionally |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review identifies CORS policy allows any origin, method, and header |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | Review identifies debug symbols enabled in project file |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | Review identifies Newtonsoft.Json 12.0.3 is outdated with known vulnerabilities |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Review identifies no appsettings.Production.json override |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project exists in provided files. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results | Found | Review identifies no test project exists in provided files |

## Summary

Total: 58 Found / 7 Partial / 5 Missed out of 70 issues.
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Missed | `GenerateJwtToken` | yes | under-credited? |
| E7 | Found | `rate limit` | yes | - |
| N3 | Partial | `SmtpPort` | **no** | **UNSUPPORTED** |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Partial | `TableExists` | yes | under-credited? |
| D4 | Found | `ExecuteQueryWithParams` | yes | - |
| D5 | Partial | `BuildHtmlTemplate` | yes | under-credited? |
| D6 | Found | `SendWelcomeEmailHtml` | yes | - |
| D7 | Found | `FormatCurrency` | yes | - |
| D8 | Partial | `IsWithinDailyLimit` | **no** | **UNSUPPORTED** |
| D9 | Found | `ObfuscateAccount` | yes | - |
| D10 | Found | `ToTitleCase` | yes | - |
| D11 | Found | `JoinWithSeparatorFixed` | **no** | **MIS-CREDIT** |
| CF9 | Found | `appsettings.Production` | yes | - |
| UT | Found | `Tests.csproj` | yes | - |
| C2 | Found | `SuperAdmin2024` | yes | - |
| C3 | Found | `MD5` | yes | - |
| C9 | Found | `ValidateLifetime` | yes | - |
| L3 | Found | `GetUsersPage` | yes | - |
| L4 | Partial | `0.05` | yes | under-credited? |
| E1 | Found | `SearchUsers` | yes | - |
| E5 | Found | `ex.Message` | yes | - |
| RL4 | Found | `SmtpClient` | yes | - |
| RL5 | Found | `MailMessage` | yes | - |
| N2 | Found | `Rows[0]` | yes | - |
| N4 | Missed | `ToUpper` | **no** | - |
| M1 | Found | `TransactionFeeRate` | yes | - |
| M2 | Found | `1000000` | yes | - |
| D2 | Found | `ValidateToken` | yes | - |
| A1 | Partial | `_auditLog` | yes | under-credited? |
| A2 | Found | `Regex` | yes | - |
| A5 | Found | `IsBlank` | yes | - |
| CF3 | Found | `ValidateLifetime` | yes | - |
| CF4 | Found | `UseHttpsRedirection` | yes | - |
| CF5 | Found | `UseDeveloperExceptionPage` | yes | - |
| CF6 | Found | `AllowAnyOrigin` | yes | - |
| CF7 | Found | `DebugType` | yes | - |
| CF8 | Found | `Newtonsoft` | yes | - |

**Adjusted Found: 57 of 70** (58 reported, less 1 mis-credited).

> **2 row(s) rated `Partial` whose target string appears NOWHERE in the review** (N3, D8). A Partial on an unmentioned issue is a Missed; the reported Missed count is correspondingly understated.

> **5 row(s) rated `Partial`/`Missed` whose target string IS present in the review** (R3, D3, D5, L4, A1). The score is left as the scorer rated it; read these rows before trusting the Missed count.

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `MiniMax-M2.7:Q3_K_S` |
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
| Grounding downgrades | `5` |
| Self-declared-absent downgrades | `0` |
| Rows misaligned with ISSUES.md | `0` |
| Review citations past end of file | `0 of 176` |
| Precision (checkable Found rows) | `97% (31 of 32)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 67ece22` |
