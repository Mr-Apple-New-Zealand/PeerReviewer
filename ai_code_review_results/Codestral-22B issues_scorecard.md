# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `2b77eff`

> ⚠ **2 row(s) rated Found name a target that never appears in the review** (D6, D11). Adjusted Found: **22** of 70. See the spot-check below.

Total: 24 Found / 39 Partial / 7 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review identifies SQL injection in `Login` method with "Use parameterized queries or stored procedures to prevent SQL injection." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review identifies hardcoded password in `AdminBypassPassword` constant with "Remove hardcoded credentials and implement a secure authentication mechanism." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review identifies weak cryptography (MD5) in `HashPasswordMd5` method with "Use a stronger hashing algorithm like SHA-256 or bcrypt with a salt." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Partial | Review identifies SQL injection in multiple methods but does not specifically name the UpdateUser/DeleteUser methods; mentions "ExecuteQuery", "ExecuteNonQuery" etc. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Missed | _(ungrounded: no matching sentence in review)_ |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Partial | Review identifies SQL injection in multiple methods but does not specifically name Transfer/Deposit methods; mentions "ExecuteQuery", "ExecuteNonQuery" etc. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Missed | _(ungrounded: no matching sentence in review)_ |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review identifies hardcoded credentials in EmailService constructor with "Store credentials securely, such as using environment variables or a secure vault." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review identifies JWT misconfiguration with "Set ValidateLifetime to true to ensure the token expiration is validated." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Partial | Review mentions missing authorization checks but does not specifically name this endpoint or method; generic error handling review |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Partial | Review mentions missing authorization checks but does not specifically name this endpoint or method; generic error handling review |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Review identifies negative amount check in `Transfer` method with "Add a check to ensure the amount is greater than zero." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Partial | Review identifies incorrect deposit amount check but does not specifically name this logic error; mentions "Deposit" method |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review identifies off-by-one error in `GetUsersPage` method with "Use the correct formula for pagination: `int skip = (page - 1) * pageSize;`." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | Review identifies incorrect deposit amount check but does not specifically name this logic error; mentions "Deposit" method |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Missed | _(ungrounded: no matching sentence in review)_ |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | Review mentions duplicated exception handling but does not specifically name this refactoring opportunity |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review identifies inefficient string concatenation in `JoinWithSeparator` method with "Use StringBuilder or string.Join to improve performance and readability." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | Review mentions duplicated code in RecordTransaction but does not specifically name this refactoring opportunity |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Partial | Review mentions missing exception handling in SearchUsers but does not specifically name this error handling issue |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | Review mentions swallowing exceptions in SendTransferNotification but does not specifically name SendWelcomeEmail |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Partial | Review mentions lack of database transaction in Transfer method but does not specifically name this error handling issue |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Partial | Review mentions lack of database transaction in Transfer method but does not specifically name this error handling issue |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Partial | Review mentions swallowing exception in Login method but does not specifically name this error handling issue |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Partial | Review mentions resource leak in ExecuteNonQuery but does not specifically name this error handling issue |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | Review mentions null reference risks but does not specifically name missing rate limiting |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review identifies resource leak in GetOpenConnection method with "Use a using block or explicitly close the connection to release resources." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Missed | _(ungrounded: no matching sentence in review)_ |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review identifies resource leak in ExecuteNonQuery method with "Use a using block or explicitly close the connection to release resources." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review identifies resource leak in SmtpClient with "Dispose the SmtpClient instance in a using block or explicitly dispose it after use." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Missed | _(ungrounded: no matching sentence in review)_ |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Partial | Review mentions null reference risks but does not specifically name this configuration issue |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Missed | _(ungrounded: no matching sentence in review)_ |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | Review mentions null reference risks but does not specifically name this configuration parsing issue |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | Review mentions null reference risks in StringHelper but does not specifically name this method |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | Review mentions null reference risks in StringHelper but does not specifically name this method |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Partial | Review mentions null reference risks in transaction controller but does not specifically name this parsing issue |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | Review mentions null reference risks in UserService but does not specifically name this model binding issue |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Partial | Review mentions magic numbers but does not specifically name these transaction constants |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Partial | Review mentions magic numbers but does not specifically name this deposit cap constant |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | Review mentions hardcoded email configuration values but does not specifically name these email addresses |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | Review identifies magic numbers in StringHelper methods with "Use named constants or configuration values for the magic numbers." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Partial | Review mentions magic number (20) for pageSize but does not specifically name this 50 limit |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review identifies unused method `HashPasswordSha1` with "Remove the unused method or update its usage." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Review identifies unused method `ValidateToken` with "Remove the unused method or update its usage." |
| D3 | `TableExists` — never called from any service or controller. | Partial | Review mentions dead code but does not specifically name TableExists |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review identifies obsolete method `ExecuteQueryWithParams` with "Remove the obsolete method or update its usage." |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Partial | Review mentions unused method `BuildHtmlTemplate` but does not specifically name this dead code scenario |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Review identifies unused method `SendWelcomeEmailHtml` with "Remove the unused method or update its usage." |
| D7 | `FormatCurrency` — private, never called. | Partial | Review mentions unused method but does not specifically name FormatCurrency |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Partial | Review mentions unused method but does not specifically name IsWithinDailyLimit |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Partial | Review mentions unused method but does not specifically name ObfuscateAccount |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Partial | Review mentions unused method but does not specifically name ToTitleCase |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review identifies unused method `JoinWithSeparator` with "Remove the unused method or update its usage." |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | Review mentions shared mutable static state but does not specifically name this anti-pattern |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Partial | Review mentions anti-patterns but does not specifically name regex compilation issue |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review identifies inefficient string concatenation with "Use StringBuilder or string.Join to improve performance and readability." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Review identifies shared SmtpClient issue with "Use a thread-safe approach or ensure proper synchronization when accessing the SmtpClient instance." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Missed | _(ungrounded: no matching sentence in review)_ |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Partial | Review mentions anti-patterns but does not specifically name GetOpenConnection leak |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies hardcoded credentials in DefaultConnection connection string with "Store credentials securely, such as using environment variables or a secure vault." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | Review mentions debug log levels but does not specifically name this configuration issue |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies JWT misconfiguration with "Set ValidateLifetime to true to ensure the token expiration is validated." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Partial | Review mentions HTTPS redirection but does not specifically name this configuration issue |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review identifies UseDeveloperExceptionPage() call with "Remove or conditionally use UseDeveloperExceptionPage() based on the environment." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review identifies overly permissive CORS policy with "Limit the allowed origins, methods, and headers based on your application's requirements." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Partial | Review mentions configuration issues but does not specifically name this debug symbol issue |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | Review mentions outdated packages but does not specifically name this vulnerability |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | Review mentions configuration issues but does not specifically name missing production settings |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | **Missing Unit Tests** — The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `TransactionService.Transfer`, `UserService.GetUsersPage`, etc. | Found | Review explicitly states "No test project exists in the source files provided" and mentions testing critical methods, indicating recognition of missing unit tests. |

## Summary

Total: 48 Found / 12 Partial / 10 Missed out of 70 issues.
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Missed | `SearchUsers` | yes | under-credited? |
| C7 | Missed | `RecordTransaction` | yes | under-credited? |
| R3 | Partial | `GenerateJwtToken` | **no** | - |
| E7 | Partial | `rate limit` | **no** | - |
| N3 | Partial | `SmtpPort` | **no** | - |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Partial | `TableExists` | yes | under-credited? |
| D4 | Found | `ExecuteQueryWithParams` | yes | - |
| D5 | Partial | `BuildHtmlTemplate` | yes | under-credited? |
| D6 | Found | `SendWelcomeEmailHtml` | **no** | **MIS-CREDIT** |
| D7 | Partial | `FormatCurrency` | **no** | - |
| D8 | Partial | `IsWithinDailyLimit` | **no** | - |
| D9 | Partial | `ObfuscateAccount` | **no** | - |
| D10 | Partial | `ToTitleCase` | **no** | - |
| D11 | Found | `JoinWithSeparatorFixed` | **no** | **MIS-CREDIT** |
| CF9 | Partial | `appsettings.Production` | **no** | - |

**Adjusted Found: 22 of 70** (24 reported, less 2 mis-credited).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Codestral-22B-imatrix:Q4_K_S` |
| Reasoning strength (system prompt) | (model default) |
| Ollama `think` | (unset) |
| Temperature | `0.3` |
| top_p | (model default) |
| top_k | (model default) |
| num_ctx | `65536` |
| num_predict | `40000` |
| Source truncated | `no` |
| Review prompt SHA-256 | `82bd5f768ca9` |
| Scorer model | `Qwen3-Coder-30B-imatrix:Q3_K_M` |
| Scorer temperature | `0.3` |
| Scorer reasoning | (model default) |
| Scorer `think` | (unset) |
| Scorer attempts | `1` |
| Grounding mode | `enforce` |
| Grounding downgrades | `7` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 2b77eff` |
