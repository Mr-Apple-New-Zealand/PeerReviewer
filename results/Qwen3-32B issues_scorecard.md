# AI Review Scorecard

> **Branch:** `Qwen3-32B` &nbsp;·&nbsp; **Commit:** `7edecc1`

# AI Review Scorecard

Total: 58 Found / 12 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Use parameterized queries instead of string interpolation |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Hardcoded admin bypass password "SuperAdmin2024" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Hardcoded MD5 password hashing with no salt |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | SQL injection vulnerability in DELETE statement |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | SQL injection vulnerability in LIKE clause |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | SQL injection vulnerability in UPDATE statements |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | SQL injection vulnerability in INSERT statement |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Email credentials are passed as plain text |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | JWT ValidateLifetime is set to false |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | No validation for request.Email and request.Username |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | No validation for query parameter |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Missing check for self-transfer (fromUserId == toUserId) |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Fee calculation is applied only to fromBalance, but not checked against totalDebit |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Pagination uses page * pageSize which is incorrect |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Deposit method applies 5% interest bonus without validation |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Missing check for self-transfer (fromUserId == toUserId) |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | No specific mention of duplicated validation blocks |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | String concatenation in loop (JoinWithSeparator) |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | No specific mention of token generation method length |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Returns empty list on error without differentiation |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | No error handling for database operations |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | No transaction scope for balance updates |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | No error handling for database operations |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | No validation for request.Username and request.Password |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | No error handling for database operations |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | No specific mention of rate limiting or account lockout |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | GetOpenConnection returns open connection without documentation |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | GetOpenConnection returns open connection without disposal |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | No error handling for database operations |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | SmtpClient is created as instance field |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | MailMessage is created but not disposed |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Partial | No specific mention of null check for JWT secret |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | No null check for fromUserTable.Rows[0] |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | No specific mention of null check for email port |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | No null check for User.FindFirst result |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | No specific mention of null guard for email or username |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | No null check for User.FindFirst result |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | No validation for request.Email and request.Username |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | TransactionFeeRate is hardcoded |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | 1,000,000 deposit limit is hardcoded |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | "notifications@company.com" is hardcoded |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Partial | No specific mention of these literals |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | 50 pageSize limit is hardcoded |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | HashPasswordSha1 is unused |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | ValidateToken is incomplete and always returns true |
| D3 | `TableExists` — never called from any service or controller. | Partial | No specific mention of TableExists |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | ExecuteQueryWithParams is marked [Obsolete] but still exists |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | SendWelcomeEmailHtml is redundant with SendWelcomeEmail |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | SendWelcomeEmailHtml is redundant with SendWelcomeEmail |
| D7 | `FormatCurrency` — private, never called. | Partial | No specific mention of FormatCurrency |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Partial | No specific mention of daily limit enforcement |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | ObfuscateAccount is redundant with MaskAccountNumber |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | ToTitleCase uses CultureInfo.CurrentCulture which may be inconsistent |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | JoinWithSeparator is inefficient and should be removed |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | No specific mention of static state |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Regex is created inside method |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | String concatenation in loop (JoinWithSeparator) |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | SmtpClient is created as instance field |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | IsBlank reimplements string.IsNullOrWhiteSpace |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | GetOpenConnection returns open connection without documentation |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Email credentials are passed as plain text |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Logging level is set to Debug for production |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | JWT ValidateLifetime is set to false |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | HTTPS redirection is commented out |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | UseDeveloperExceptionPage() is enabled unconditionally |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Overly permissive CORS policy |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Partial | No specific mention of debug symbols |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | Newtonsoft.Json is used |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Missing environment-specific config overrides |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: - `AuthService.Login` — SQL injection boundary cases, correct vs. incorrect password - `AuthService.GenerateJwtToken` — claims mapping, expiry - `TransactionService.Transfer` — zero amount, self-transfer, fee deduction, insufficient funds (with fee) - `TransactionService.Deposit` — interest rate correctness - `UserService.GetUsersPage` — pagination offset correctness (the off-by-one) - `StringHelper` — null inputs, boundary lengths, separator trailing character - Controller action results — correct HTTP status codes for various service responses | Found | No test project exists |