# AI Review Scorecard

> **Branch:** `glm5.2` &nbsp;·&nbsp; **Commit:** `92cc625`

Total: 54 Found / 0 Partial / 16 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "DatabaseHelper.cs | 28 | `ExecuteQuery` concatenates user input into SQL string, enabling SQL injection." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Missed |  |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Missed |  |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Missed |  |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Missed |  |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Missed |  |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Missed |  |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "DatabaseHelper.cs | 16 | Hardcoded fallback credentials (`sa`/`Admin1234!`) in constructor." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "Program.cs | 23 | JWT secret key read directly from config without validation for empty/null in production." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | "UserController.cs | 46 | `UpdateUser` allows any authenticated user to update any user if they are not Admin, but logic is flawed (see Logic Errors)." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | "UserController.cs | 78 | `DeleteUser` allows any Admin to delete any user without audit trail or soft-delete." |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | "TransactionService.cs | 68 | `Transfer` checks balance against `amount + fee` but only deducts `fee` from sender and adds `amount` to receiver, losing the fee amount." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "TransactionService.cs | 68 | `Transfer` checks balance against `amount + fee` but only deducts `fee` from sender and adds `amount` to receiver, losing the fee amount." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "UserService.cs | 75 | `GetUsersPage` uses `OFFSET`/`FETCH` which can be slow on large tables; no total count returned for pagination." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | "TransactionService.cs | 108 | `Deposit` adds interest bonus to balance but does not record the interest amount separately in transaction log." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | "TransactionController.cs | 25 | `Transfer` does not validate `request.ToUserId` or `request.Amount` for null/negative values." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Missed |  |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "StringHelper.cs | 28 | `JoinWithSeparator` duplicates `string.Join` functionality." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed |  |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Missed |  |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | "EmailService.cs | 72 | `SendWelcomeEmail` swallows `SmtpException` silently, losing error visibility." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | "TransactionService.cs | 68 | Race condition: Balance check and update are not atomic; concurrent requests can lead to overdrafts." |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response.** | Found | "TransactionService.cs | 75 | `Transfer` catches `Exception` in transaction block and re-throws, but does not log the error." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | "UserController.cs | 58 | `UpdateUser` catches `Exception` and returns generic 500, potentially hiding specific errors." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | "DatabaseHelper.cs | 35 | `ExecuteQuerySafe` does not handle SQL exceptions, propagating raw errors to callers." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | "TransactionController.cs | 53 | `Refund` catches `NotImplementedException` and returns 500, leaking implementation details." |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "DatabaseHelper.cs | 22 | `CreateConnection` returns `SqlConnection` without disposing; caller must manage disposal." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "DatabaseHelper.cs | 35 | `SqlDataAdapter` and `DataTable` not explicitly disposed; rely on GC." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "TransactionService.cs | 70 | `connection` opened in `Transfer` but not disposed if exception occurs before `using` block ends." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "EmailService.cs | 35 | `SmtpClient` created per call; not thread-safe and may leak sockets if not disposed properly." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "EmailService.cs | 48 | `SendTransferNotification` retries on `SmtpException` but does not handle network timeouts or other exceptions." |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | "Program.cs | 23 | JWT secret key read directly from config without validation for empty/null in production." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "TransactionService.cs | 62 | `fromUserTable.Rows[0]` accessed without checking count." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | "EmailService.cs | 35 | `_config["Email:SmtpHost"]` may be null, causing `SmtpClient` constructor to fail." |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | "TransactionService.cs | 65 | `toUserTable.Rows[0]` accessed without checking count." |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | "AuthService.cs | 23 | `table.Rows[0]` accessed without checking `Rows.Count > 0` in `Login`." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "TransactionController.cs | 25 | `Transfer` does not validate `request.ToUserId` or `request.Amount` for null/negative values." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | "UserController.cs | 46 | `UpdateUser` allows any authenticated user to update any user if they are not Admin, but logic is flawed (see Logic Errors)." |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | "TransactionService.cs | 12 | `DefaultTransactionFeeRate` hardcoded; should be configurable." |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | "TransactionService.cs | 14 | `MaxDepositAmount` hardcoded; should be configurable." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | "EmailService.cs | 18 | `NotificationEmail` and `SupportEmail` hardcoded; should be configurable." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | "StringHelper.cs | 28 | `JoinWithSeparator` duplicates `string.Join` functionality." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "UserService.cs | 10 | `MaxUserId` and `MaxPageSize` hardcoded; should be configurable." |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | "TransactionService.cs | 115 | `IsWithinDailyLimit` method is defined but never called." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "AuthService.cs | 85 | `ValidateToken` is defined but not used anywhere." |
| D3 | `TableExists` — never called from any service or controller. | Found | "DatabaseHelper.cs | 35 | `SqlDataAdapter` and `DataTable` not explicitly disposed; rely on GC." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | "TransactionService.cs | 130 | `RecordTransaction` overload with connection/transaction is used, but the other overload is also present." |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | "EmailService.cs | 48 | `SendTransferNotification` retries on `SmtpException` but does not handle network timeouts or other exceptions." |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | "EmailService.cs | 72 | `SendWelcomeEmail` swallows `SmtpException` silently, losing error visibility." |
| D7 | `FormatCurrency` — private, never called. | Found | "TransactionService.cs | 115 | `IsWithinDailyLimit` method is defined but never called." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | "TransactionService.cs | 115 | `IsWithinDailyLimit` method is defined but never called." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | "StringHelper.cs | 28 | `JoinWithSeparator` duplicates `string.Join` functionality." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | "StringHelper.cs | 28 | `JoinWithSeparator` duplicates `string.Join` functionality." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "StringHelper.cs | 28 | `JoinWithSeparator` duplicates `string.Join` functionality." |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Missed |  |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Missed |  |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "StringHelper.cs | 28 | `JoinWithSeparator` duplicates `string.Join` functionality." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "EmailService.cs | 35 | `SmtpClient` created per call; not thread-safe and may leak sockets if not disposed properly." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "StringHelper.cs | 28 | `JoinWithSeparator` duplicates `string.Join` functionality." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "DatabaseHelper.cs | 22 | `CreateConnection` returns `SqlConnection` without disposing; caller must manage disposal." |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "DatabaseHelper.cs | 16 | Hardcoded fallback credentials (`sa`/`Admin1234!`) in constructor." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Missed |  |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "Program.cs | 23 | JWT secret key read directly from config without validation for empty/null in production." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Missed |  |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "Program.cs | 45 | `UseDeveloperExceptionPage()` only in development, but no custom error page for production." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "Program.cs | 38 | CORS policy allows any method and header, which may be overly permissive." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Missed |  |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Missed |  |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Missed |  |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | **Missing Unit Tests** — The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, Controller action results. | Found | "All Services | - | No test project exists; critical business logic untested." |