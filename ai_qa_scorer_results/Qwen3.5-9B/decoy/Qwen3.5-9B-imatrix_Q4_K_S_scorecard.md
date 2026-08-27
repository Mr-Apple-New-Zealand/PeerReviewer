# Scorer: Qwen3.5-9B-imatrix:Q4_K_S
# Review type: decoy

# AI Review Scorecard

Total: 11 Found / 0 Partial / 58 Missed out of 69 issues.

## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | The review identifies: "SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query." |
| C2 | Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | The review identifies: "Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record." |
| C3 | Broken password hashing — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | The review identifies: "Broken password hashing — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks." |
| C4 | SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | The review identifies: "SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements." |
| C5 | SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | The review identifies: "SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause via `ExecuteQuery`." |
| C6 | SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | The review identifies: "SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements." |
| C7 | SQL Injection (RecordTransaction) — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | The review identifies: "SQL Injection (RecordTransaction) — `description` is interpolated; a malicious description can inject arbitrary SQL." |
| C8 | Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed to source control. | Found | The review identifies: "Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed to source control." |
| C9 | JWT lifetime validation disabled (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | The review identifies: "JWT lifetime validation disabled (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever." |
| C10 | Broken Access Control — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | The review identifies: "Broken Access Control — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile." |
| C11 | Missing Authorization — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | The review identifies: "Missing Authorization — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account." |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | The review identifies: "`amount < 0` check allows zero-value transfers (`amount == 0`). Should be `amount <= 0`." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | The review identifies: "Balance check excludes the fee — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | The review identifies: "Off-by-one in pagination — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | The review identifies: "Incorrect interest rate — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | The review identifies: "Self-transfer allowed — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Missed | The review mentions SQL injection in `UserService` but does not identify the duplicated validation logic or suggest extracting it. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Missed | The review does not mention `JoinWithSeparator`, `JoinWithSeparatorFixed`, or loop string concatenation issues. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | The review does not mention `GenerateJwtToken` or suggest splitting it into named helpers. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Missed | The review does not mention exception swallowing in `SearchUsers` or returning empty lists. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Missed | The review does not mention `SendWelcomeEmail` catching broad exceptions. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Missed | The review does not mention missing database transactions in `Transfer`. |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Missed | The review does not mention email failure propagation after DB commit in `Transfer`. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Missed | The review does not mention leaking `ex.Message` in controllers. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Missed | The review does not mention connection closing issues in `DatabaseHelper`. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed | The review does not mention rate limiting or account lockout. |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Missed | The review does not mention `SqlConnection` or `SqlDataReader` leaks in `Login`. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Missed | The review does not mention `GetOpenConnection` or disposal issues. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Missed | The review does not mention `Dispose` issues on connections. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Missed | The review does not mention `SmtpClient` field holding or socket leaks. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Missed | The review does not mention `MailMessage` disposal issues. |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Missed | The review does not mention null checks for config keys or `Encoding.UTF8.GetBytes`. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Missed | The review does not mention null checks for database rows. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Missed | The review does not mention null checks for config ports or fallback logic. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | The review does not mention null checks for `username` before `ToUpper`. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Missed | The review does not mention null checks before accessing `.Length`. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Missed | The review does not mention null checks for `User.FindFirst` results. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Missed | The review does not mention null checks for request bodies. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Missed | The review does not mention hardcoded constants like `TransactionFeeRate` or `MaxTransactionsPerDay`. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Missed | The review does not mention the hardcoded deposit cap `1_000_000`. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Missed | The review does not mention hardcoded email addresses. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Missed | The review does not mention hardcoded string length literals. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Missed | The review does not mention the hardcoded page size limit of `50`. |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Missed | The review does not mention `HashPasswordSha1` as dead code. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Missed | The review does not mention unreachable code in `ValidateToken`. |
| D3 | `TableExists` — never called from any service or controller. | Missed | The review does not mention `TableExists` as dead code. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Missed | The review does not mention `ExecuteQueryWithParams` as dead code. |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Missed | The review does not mention `BuildHtmlTemplate` as dead code. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Missed | The review does not mention `SendWelcomeEmailHtml` as dead code. |
| D7 | `FormatCurrency` — private, never called. | Missed | The review does not mention `FormatCurrency` as dead code. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Missed | The review does not mention `IsWithinDailyLimit` as dead code. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Missed | The review does not mention `ObfuscateAccount` as dead code. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Missed | The review does not mention `ToTitleCase` as dead code. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Missed | The review does not mention `JoinWithSeparatorFixed` as dead code. |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Missed | The review does not mention mutable static state or thread-safety issues. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Missed | The review does not mention Regex compilation performance issues. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Missed | The review mentions loop string concatenation in the context of `JoinWithSeparator` (R2) but does not flag it as an anti-pattern in `StringHelper` or `JoinWithSeparator`. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Missed | The review does not mention `SmtpClient` thread-safety issues. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Missed | The review does not mention reimplementing BCL methods. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Missed | The review does not mention `GetOpenConnection` as an anti-pattern. |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | The review identifies: "Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed to source control." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Missed | The review does not mention log levels or `Debug` settings. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | The review identifies: "JWT lifetime validation disabled (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Missed | The review does not mention HTTPS or `UseHttpsRedirection`. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Missed | The review does not mention `UseDeveloperExceptionPage`. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Missed | The review does not mention CORS policies. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Missed | The review does not mention `DebugSymbols` or `DebugType` in the project file. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Missed | The review does not mention `Newtonsoft.Json` or outdated packages. |
| CF9 | **(project root)** — **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Missed | The review does not mention missing `appsettings.Production.json`. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, Controller action results. | Missed | The review does not mention the absence of a test project or the need for unit tests in any of the listed areas.