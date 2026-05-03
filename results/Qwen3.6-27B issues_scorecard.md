# AI Review Scorecard

> **Branch:** `Qwen3.6-27B` &nbsp;·&nbsp; **Commit:** `59cf8b8`

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | String interpolation builds raw SQL queries vulnerable to injection. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Hardcoded admin bypass password allows unauthorized privilege escalation. |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Password hashing uses cryptographically broken MD5 algorithm. |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | String interpolation builds raw SQL UPDATE and INSERT statements. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | String interpolation builds raw SQL UPDATE, DELETE, and LIKE clauses. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | String interpolation builds raw SQL UPDATE and INSERT statements. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | String interpolation builds raw SQL UPDATE and INSERT statements. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Production database and SMTP passwords are committed to source control. |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | JWT configuration disables token lifetime validation. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | PUT and DELETE endpoints lack ownership or role-based authorization checks. |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | PUT and DELETE endpoints lack ownership or role-based authorization checks. |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Balance check compares against `amount` but deducts `amount + fee`, risking negative balances. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Balance check compares against `amount` but deducts `amount + fee`, risking negative balances. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Pagination calculates skip as `page * pageSize`, causing an off-by-one error. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Daily transaction limit method is defined but never invoked during transfers. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Transfer logic allows users to send funds to their own account. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | User ID validation logic is duplicated across three methods. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | String concatenation inside a loop causes O(n²) performance degradation. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | `ExecuteQuerySafe` method is defined but never called. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Broad exception catch silently returns an empty list, masking database failures. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Welcome email failure is caught and printed to console, silently failing in production. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Two separate balance updates run without a database transaction wrapper. |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Raw exception message is returned directly to the HTTP client. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | `ExecuteQuery` opens a connection and command but never closes or disposes them. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | Login endpoint lacks rate limiting or account lockout mechanisms. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | `SqlConnection` and `SqlDataReader` are opened but never closed or disposed. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | `GetOpenConnection` returns an open connection without disposing it. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | `ExecuteQuery` opens a connection and command but never closes or disposes them. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | `SmtpClient` is stored as an instance field, which is not thread-safe and leaks sockets. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | `MailMessage` objects are created but never disposed after sending. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Configuration values are accessed with `!` null-forgiving operator without validation. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | `Rows[0]` is accessed without verifying `Rows.Count > 0`. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | `int.Parse` is called on a potentially null SMTP port configuration value. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | `.Length` is called on string parameters without null checks. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | `.Length` is called on string parameters without null checks. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | `int.Parse` is called on a potentially null claim value without a null guard. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | `int.Parse` is called on a potentially null claim value without a null guard. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Hardcoded fee rate, daily limit, and deposit cap lack named constants or config. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | Hardcoded user ID range and page size limits are scattered inline. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Hardcoded email subjects, retry counts, and timeouts are inline literals. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | Hardcoded string length limits and masking thresholds are inline literals. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Hardcoded user ID range and page size limits are scattered inline. |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | `HashPasswordSha1` is defined but never called anywhere. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Code after `return true;` in `ValidateToken` is unreachable. |
| D3 | `TableExists` — never called from any service or controller. | Found | `[Obsolete]` method `ExecuteQueryWithParams` remains in the codebase. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | `[Obsolete]` method `ExecuteQueryWithParams` remains in the codebase. |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | `BuildHtmlTemplate` and `SendWelcomeEmailHtml` are never called externally. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | `BuildHtmlTemplate` and `SendWelcomeEmailHtml` are never called externally. |
| D7 | `FormatCurrency` — private, never called. | Found | `FormatCurrency` is defined but never invoked. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | `IsWithinDailyLimit` is defined but never called in transfer flow. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | `FormatCurrency` is defined but never invoked. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | `FormatCurrency` is defined but never invoked. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | String concatenation inside a loop causes O(n²) performance degradation. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | Static mutable lists and counters are shared across threads without synchronization. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | `new Regex(...)` is instantiated on every method call. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | String concatenation inside a loop causes O(n²) performance degradation. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | `SmtpClient` is stored as an instance field, which is not thread-safe and leaks sockets. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | `GetOpenConnection` returns an open connection without disposing it. |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Production database and SMTP passwords are committed to source control. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Debug log levels are set for all namespaces. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | JWT `ValidateLifetime` is explicitly set to `false`. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | HTTPS redirection is commented out. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | `UseDeveloperExceptionPage()` is called unconditionally. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | CORS policy allows any origin, method, and header. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | Debug symbols are explicitly enabled, which is unsafe for release builds. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | `Newtonsoft.Json` version 12.0.3 contains known vulnerabilities. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Base configuration file contains production secrets. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project exists in the repository. Critical methods and scenarios requiring immediate test coverage include: `AuthService.Login`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `DatabaseHelper` methods, `StringHelper` utilities, and controller endpoints. | Found | No test project exists in the repository. Critical methods and scenarios requiring immediate test coverage include: `AuthService.Login`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `DatabaseHelper` methods, `StringHelper` utilities, and controller endpoints. |