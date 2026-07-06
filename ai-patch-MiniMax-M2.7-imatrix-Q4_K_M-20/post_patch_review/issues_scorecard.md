# AI Review Scorecard

> **Branch:** `MiniMax-M2.7` &nbsp;·&nbsp; **Commit:** `717c543`

Total: 10 Found / 6 Partial / 54 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query. | Missed | The review mentions `AddWithValue` in `DatabaseHelper` but does not identify the specific SQL injection in `AuthService.Login` via string interpolation. |
| C2 | Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Missed | The review does not mention the hardcoded backdoor password or the `AdminBypassPassword` constant. |
| C3 | Broken password hashing — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Partial | The review states "Passwords are hashed using SHA-256 without a salt", identifying the missing salt issue but incorrectly identifying the algorithm (MD5 vs SHA-256). |
| C4 | SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Missed | The review does not mention SQL injection in `UserService.UpdateUser` or `DeleteUser`. |
| C5 | SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Partial | The review mentions `SearchUsers` constructs LIKE pattern manually which "may allow SQL injection", but notes parameters are used, missing the critical fact that the query string itself is interpolated in the reference description. |
| C6 | SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Missed | The review mentions non-atomic transactions in `TransactionService` but does not identify the SQL injection via string concatenation in `Transfer` or `Deposit`. |
| C7 | SQL Injection (RecordTransaction) — `description` is interpolated; a malicious description can inject arbitrary SQL. | Missed | The review does not mention SQL injection in `RecordTransaction`. |
| C8 | Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed to source control. | Missed | The review mentions connection string placeholder and JWT secret config, but does not explicitly flag hardcoded production credentials in `appsettings.json`. |
| C9 | JWT lifetime validation disabled (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Partial | The review mentions "JWT expiration is hardcoded to 30 days" and suggests reducing it, but misses the specific `ValidateLifetime = false` configuration issue that disables expiry entirely. |
| C10 | Broken Access Control — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Missed | The review mentions `GetUser` lacks authorization, but does not specifically address the missing ownership check in `PUT /api/user/{id}`. |
| C11 | Missing Authorization — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Missed | The review does not mention the missing authorization/role check for `DELETE /api/user/{id}`. |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Missed | The review does not mention the zero-value transfer logic error. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Missed | The review mentions non-atomic transactions but does not identify the specific balance check logic error excluding the fee. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Missed | The review mentions validating `page > 0` but does not identify the off-by-one error in the skip calculation. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Missed | The review mentions interest rate is hardcoded but does not identify the incorrect value or the logic error of applying it on every deposit. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Missed | The review does not mention the self-transfer logic error. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Missed | The review does not mention duplicated validation logic in `UserService`. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Partial | The review mentions `JoinWithSeparator` simply wraps `string.Join` and suggests removing it, but misses the O(n²) loop concatenation issue in the broken version. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | The review does not mention the overly long `GenerateJwtToken` method. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Missed | The review does not mention `SearchUsers` swallowing exceptions. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | The review mentions `SmtpException` in `SendWelcomeEmail` is caught and printed to console, failing silently, but misses the overly broad `catch (Exception)` issue. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | The review states "Balance checks and updates are not atomic within a single transaction scope for the read-check-write pattern" in `TransactionService`. |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Missed | The review mentions email failure is caught and ignored in `TransactionService`, but does not identify the specific issue of propagating exception after commit. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | The review states "`ArgumentException` message is returned directly to the client, leaking internal implementation details" in `UserController`. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Missed | The review mentions `ExecuteInTransaction` logging but does not identify the connection leak in `ExecuteNonQuery`. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | The review states "Failed login attempts are logged but not rate-limited, enabling brute-force attacks" in `AuthController`. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Missed | The review does not mention resource leaks in `AuthService.Login`. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Missed | The review does not mention the resource leak in `GetOpenConnection` or `ExecuteQuery`. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Missed | The review does not mention the resource leak in `ExecuteNonQuery`. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Missed | The review states `SmtpClient` is disposed via `using`, which is incorrect based on the reference, and thus misses the leak. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Missed | The review states `MailMessage` is disposed via `using`, which is incorrect based on the reference, and thus misses the leak. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Missed | The review does not mention null check for `Jwt:SecretKey`. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Missed | The review does not mention null/missing row checks in `TransactionService`. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Missed | The review does not mention null check for `SmtpPort`. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | The review does not mention null check for `username` in `EmailService`. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Missed | The review does not mention null checks in `StringHelper`. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | The review states "`User.FindFirst` may return null, and `.Value` is accessed without null check" in `TransactionController` and `UserController`. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Missed | The review does not mention null check for `request` in `UserController`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | The review states "Default fee rate `0.015m` is hardcoded" and suggests moving to configuration in `TransactionService`. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | The review states "Default deposit cap `1_000_000m` is hardcoded" and suggests moving to configuration in `TransactionService`. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Missed | The review mentions email subjects are hardcoded but does not mention the hardcoded email addresses. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Missed | The review does not mention the bare literals in `StringHelper`. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | The review states "Max page size `50` is hardcoded" and suggests moving to configuration in `UserService`. |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Missed | The review does not mention `HashPasswordSha1`. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Missed | The review does not mention unreachable code in `ValidateToken`. |
| D3 | `TableExists` — never called from any service or controller. | Missed | The review does not mention `TableExists`. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Missed | The review does not mention `ExecuteQueryWithParams`. |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Missed | The review does not mention `BuildHtmlTemplate`. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Missed | The review does not mention `SendWelcomeEmailHtml`. |
| D7 | `FormatCurrency` — private, never called. | Missed | The review does not mention `FormatCurrency`. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Missed | The review does not mention `IsWithinDailyLimit`. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Missed | The review does not mention `ObfuscateAccount`. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Missed | The review does not mention `ToTitleCase`. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Missed | The review mentions `JoinWithSeparator` wraps `string.Join` but does not identify `JoinWithSeparatorFixed` as dead code. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | The review states "`AuditLog` is a static list, which can grow indefinitely and cause memory leaks" and "`AuditLock` is used for thread safety, but static state is generally discouraged" in `UserService`. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Missed | The review does not mention regex compilation per call. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Missed | The review mentions `JoinWithSeparator` wraps `string.Join` but does not identify the O(n²) loop concatenation anti-pattern. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Missed | The review states `SmtpClient` is disposed via `using`, missing the shared mutable state anti-pattern. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Missed | The review does not mention `IsBlank`. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Missed | The review does not mention `GetOpenConnection` as an anti-pattern. |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Missed | The review mentions connection string placeholder and JWT secret config, but does not explicitly flag production secrets in source control. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Missed | The review does not mention log level configuration. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Partial | The review mentions JWT expiration is hardcoded to 30 days, but misses the specific `ValidateLifetime = false` configuration. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Missed | The review does not mention HTTPS redirection. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Missed | The review does not mention `UseDeveloperExceptionPage`. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | The review states "CORS policy allows any method and header, which is overly permissive" in `Program.cs`. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Missed | The review does not mention debug symbols in csproj. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Missed | The review does not mention outdated packages. |
| CF9 | *(missing)* | — | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Missed | The review does not mention missing production config file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, Controller action results. | Found | The review states "No test project exists" and lists specific areas needing tests including `Transfer`, `Deposit`, `Login`, `GetUserById`, and controllers. |