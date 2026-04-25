# AI Review Scorecard

> **Branch:** `Qwen3.6-27B` &nbsp;·&nbsp; **Commit:** `58f73c0`

# AI Review Scorecard

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | String interpolation builds raw SQL queries vulnerable to injection. |
| C2 | Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Hardcoded admin bypass password acts as a backdoor. |
| C3 | Broken password hashing — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Passwords are hashed using cryptographically broken MD5 without salt. |
| C4 | SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | String interpolation builds raw SQL UPDATE statements vulnerable to injection. |
| C5 | SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | String interpolation builds raw SQL INSERT statements vulnerable to injection. |
| C6 | SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | String interpolation builds raw SQL UPDATE statements vulnerable to injection. |
| C7 | SQL Injection (RecordTransaction) — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | String interpolation builds raw SQL INSERT statements vulnerable to injection. |
| C8 | appsettings.json — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Production database password is committed directly to source control. |
| C9 | Program.cs — JWT lifetime validation disabled (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | JWT lifetime validation is explicitly disabled. |
| C10 | Controllers/UserController.cs — Broken Access Control — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | PUT endpoint lacks ownership verification allowing any user to modify others. |
| C11 | Controllers/UserController.cs — Missing Authorization — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | DELETE endpoint lacks ownership verification allowing any user to delete others. |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | Services/TransactionService.cs — `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Balance check compares against `amount` but deducts `amount + fee`. |
| L2 | Services/TransactionService.cs — **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Balance check compares against `amount` but deducts `amount + fee`. |
| L3 | Services/UserService.cs — **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Pagination skip calculation uses `page * pageSize` instead of `(page - 1) * pageSize`. |
| L4 | Services/TransactionService.cs — **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Interest bonus calculation multiplies by `1`, indicating incomplete logic. |
| L5 | Controllers/TransactionController.cs — **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Transfer logic does not prevent users from transferring funds to themselves. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Services/UserService.cs — **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | ID range validation is duplicated across multiple methods. |
| R2 | Helpers/StringHelper.cs — **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | String concatenation inside a loop causes O(n²) performance degradation. |
| R3 | Services/AuthService.cs — **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | Business logic, data access, and email sending are tightly coupled. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | Services/UserService.cs — `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Catches broad `Exception` and returns empty list, masking database failures. |
| E2 | Services/EmailService.cs — `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Catches broad `Exception` and prints to console, silently failing email delivery. |
| E3 | Services/TransactionService.cs — **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Two separate balance updates run without a database transaction. |
| E4 | Services/TransactionService.cs — Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. |
| E5 | Controllers/UserController.cs — `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Returns raw `ex.Message` to HTTP clients, leaking internal implementation details. |
| E6 | Data/DatabaseHelper.cs — `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | `ExecuteNonQuery` opens a connection but does not dispose the command. |
| E7 | Controllers/AuthController.cs — No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | Login endpoint lacks rate limiting or account lockout mechanisms. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | Services/AuthService.cs — `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | `Login` opens a connection and executes a reader without disposing either. |
| RL2 | Data/DatabaseHelper.cs — `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | `GetOpenConnection` returns an open connection without disposing it. |
| RL3 | Data/DatabaseHelper.cs — `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | `ExecuteNonQuery` opens a connection but does not dispose the command. |
| RL4 | Services/EmailService.cs — `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | `SmtpClient` is stored as an instance field, which is not thread-safe. |
| RL5 | Services/EmailService.cs — `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | `MailMessage` objects are created but never disposed. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | Services/AuthService.cs — `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | `_config["Jwt:SecretKey"]!` could be null, suppressed by `!`. |
| N2 | Services/TransactionService.cs — `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Accesses `Rows[0]` without verifying `Rows.Count > 0`. |
| N3 | Services/EmailService.cs — `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | `_config["Email:SmtpHost"]` could be null, passed directly to constructor. |
| N4 | Services/EmailService.cs — `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | `User.FindFirst` may return null, causing `int.Parse` to throw. |
| N5 | Helpers/StringHelper.cs — `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | `User.FindFirst` may return null, causing `int.Parse` to throw. |
| N6 | Controllers/TransactionController.cs — `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | `User.FindFirst` may return null, causing `int.Parse` to throw. |
| N7 | Controllers/UserController.cs — `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | `User.FindFirst` may return null, causing `int.Parse` to throw. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | Services/TransactionService.cs — `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Fee rate `0.015m` is hardcoded inline. |
| M2 | Services/TransactionService.cs — `1_000_000` deposit cap hardcoded inline — no named constant. | Found | Interest rate `0.05m` and max deposit `1000000` are hardcoded. |
| M3 | Services/EmailService.cs — Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Sender email `notifications@company.com` is hardcoded. |
| M4 | Helpers/StringHelper.cs — `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | Email subjects and retry limits are hardcoded inline. |
| M5 | Services/UserService.cs — `50` as the page size upper bound is unnamed and undocumented. | Found | Page size limit `50` is hardcoded. |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | Services/AuthService.cs — `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | `HashPasswordSha1` is defined but never called anywhere. |
| D2 | Services/AuthService.cs — Unreachable code after `return true` in `ValidateToken`. | Found | Code after `return true;` in `ValidateToken` is unreachable. |
| D3 | Data/DatabaseHelper.cs — `TableExists` — never called from any service or controller. | Found | `[Obsolete]` method `ExecuteQueryWithParams` remains in the codebase. |
| D4 | Data/DatabaseHelper.cs — `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | `[Obsolete]` method `ExecuteQueryWithParams` remains in the codebase. |
| D5 | Services/EmailService.cs — `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | `BuildHtmlTemplate` is defined but never called anywhere. |
| D6 | Services/EmailService.cs — `SendWelcomeEmailHtml` — public method, never registered or called. | Found | `SendWelcomeEmailHtml` is defined but never called anywhere. |
| D7 | Services/TransactionService.cs — `FormatCurrency` — private, never called. | Found | `FormatCurrency` is defined but never called anywhere. |
| D8 | Services/TransactionService.cs — `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | `IsWithinDailyLimit` is defined but never called anywhere. |
| D9 | Helpers/StringHelper.cs — `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | `JoinWithSeparator` implements inefficient string concatenation unused in favor of the fixed version. |
| D10 | Helpers/StringHelper.cs — `ToTitleCase` — "experimental utility never integrated", never called. | Found | `ToTitleCase` is defined but never called anywhere. |
| D11 | Helpers/StringHelper.cs — `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | `JoinWithSeparator` implements inefficient string concatenation unused in favor of the fixed version. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Services/UserService.cs — **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | Static mutable `_auditLog` and `_requestCount` lack thread synchronization. |
| A2 | Helpers/StringHelper.cs — **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | `new Regex(...)` is instantiated on every method call. |
| A3 | Helpers/StringHelper.cs — **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | String concatenation inside a loop causes O(n²) performance degradation. |
| A4 | Services/EmailService.cs — **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | `SmtpClient` is stored as an instance field, which is not thread-safe. |
| A5 | Helpers/StringHelper.cs — **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. |
| A6 | Data/DatabaseHelper.cs — **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | `GetOpenConnection` leaks resource ownership to callers without documentation. |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | appsettings.json — **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Secrets are stored directly in `appsettings.json`. |
| CF2 | appsettings.json — **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Logging level is set to `Debug` for all namespaces. |
| CF3 | Program.cs — **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | `ValidateLifetime = false` disables JWT expiration checks. |
| CF4 | Program.cs — **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | HTTPS redirection is commented out. |
| CF5 | Program.cs — **UseDeveloperExceptionPage() called unconditionally** — full stack traces served to production clients. | Found | `UseDeveloperExceptionPage()` is called unconditionally. |
| CF6 | Program.cs — **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | CORS policy allows any origin, method, and header globally. |
| CF7 | SampleBankingApp.csproj — **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | `DebugSymbols = true` / `DebugType = full` always emitted — PDB files shipped with release builds. |
| CF8 | SampleBankingApp.csproj — **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | `Newtonsoft.Json` 12.0.3 is outdated and contains known vulnerabilities. |
| CF9 | *(missing)* | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | No `appsettings.Production.json` — no environment-specific overrides; production uses the same unsafe defaults. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login` — SQL injection boundary cases, correct vs. incorrect password; `AuthService.GenerateJwtToken` — claims mapping, expiry; `TransactionService.Transfer` — zero amount, self-transfer, fee deduction, insufficient funds (with fee); `TransactionService.Deposit` — interest rate correctness; `UserService.GetUsersPage` — pagination offset correctness (the off-by-one); `StringHelper` — null inputs, boundary lengths, separator trailing character; Controller action results — correct HTTP status codes for various service responses | Found | No test project exists in the repository. Critical areas requiring immediate test coverage include: `TransactionService.Transfer`: Verify balance deduction includes fees, prevents negative balances, handles self-transfers, and enforces daily limits. |