# AI Review Scorecard

> **Branch:** `Qwen3-Coder-Next` &nbsp;·&nbsp; **Commit:** `9f23812`

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review identifies SQL injection in login query via string interpolation and recommends using parameterized query with `@Username`, `@Password` |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review identifies hardcoded admin bypass password and recommends removing it |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review identifies MD5 hashing used for password hashing and recommends replacing with bcrypt/Argon2/scrypt with salt |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Review identifies SQL injection in UPDATE queries via string interpolation and recommends using parameterized queries |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | Review identifies SQL injection in `SearchUsers` via `ExecuteQuery(tableName, whereClause)` and recommends using parameterized LIKE clause |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Review identifies SQL injection in UPDATE queries via string interpolation and recommends using parameterized queries |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Review identifies SQL injection in `RecordTransaction` via string interpolation and recommends using parameterized INSERT query |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review identifies production secrets in source control and recommends removing them |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review identifies `ValidateLifetime = false` in JWT config and recommends setting it to `true` |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | Review identifies missing authorization checks in user update endpoint |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | Review identifies missing authorization checks in user delete endpoint |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Review identifies transfer checks `fromBalance >= amount` but deducts `amount + fee` and recommends checking `fromBalance >= totalDebit` |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review identifies transfer checks `fromBalance >= amount` but deducts `amount + fee` and recommends checking `fromBalance >= totalDebit` |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review identifies pagination offset uses `page * pageSize` instead of `(page - 1) * pageSize` and recommends changing to `skip = (page - 1) * pageSize` |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Review identifies deposit interest bonus calculated as `amount * 0.05m * 1` and recommends removing `* 1` or clarifying intent |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Review identifies no self-transfer check (`fromUserId == toUserId`) and recommends adding guard clause to prevent self-transfers |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | Review identifies duplicated validation in UserService methods |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review identifies string concatenation in loop and recommends using `string.Join` |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | Review identifies JWT token generation as overly long and recommends splitting into named helpers |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Review identifies `SearchUsers` catches all exceptions and returns empty list, recommending to log exception and rethrow |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Review identifies `SendWelcomeEmail` swallows all exceptions silently and recommends logging exception |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Review identifies no transaction scope around balance updates and recommends wrapping in `TransactionScope` |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | Review identifies email sent after DB updates and recommends moving email after commit or using outbox pattern |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Review identifies `ex.Message` returned directly to client and recommends returning generic error message |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | Review identifies connection not properly disposed and recommends wrapping in `using` blocks |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | Review identifies lack of rate limiting on failed login attempts |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review identifies `SqlConnection`, `SqlCommand`, `SqlDataReader` opened but never disposed and recommends wrapping in `using` blocks |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | Review identifies `GetOpenConnection()` returns undisposed `SqlConnection` and recommends documenting contract or returning `IDisposable` wrapper |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review identifies `ExecuteNonQuery` opens connection but never disposes `SqlCommand` or `SqlConnection` and recommends wrapping in `using` blocks |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review identifies `_smtpClient` held as instance field and recommends implementing `IDisposable` in `EmailService` |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review identifies `MailMessage` created but never disposed and recommends wrapping in `using` block |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Review identifies `_config["Jwt:SecretKey"]!` used with null-forgiving operator and recommends validating secret key exists |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Review identifies `table.Rows[0]` accessed without checking `Rows.Count` and recommends adding null checks |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | Review identifies SMTP credentials read from config without null checks and recommends guarding against null config values |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | Review identifies `username.ToUpper()` throws `NullReferenceException` if `username` is `null` |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | Review identifies null guard before Length access |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Review identifies `userIdClaim!` used with null-forgiving operator and recommends validating claim exists before parsing |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | Review identifies null request handling |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review identifies `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` should be configurable |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | Review identifies `1_000_000` deposit cap hardcoded inline |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Review identifies `"notifications@company.com"` and `"support@company.com"` hardcoded as literals |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | Review identifies magic numbers used as bare literals |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Review identifies `pageSize > 50` limit hardcoded |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review identifies `HashPasswordSha1` method defined but never called |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Review identifies `ValidateToken` has unreachable code after `return true` |
| D3 | `TableExists` — never called from any service or controller. | Found | Review identifies `TableExists` method never called |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review identifies `ExecuteQueryWithParams` marked `[Obsolete]` and never called |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review identifies `BuildHtmlTemplate` private method never invoked |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Review identifies `SendWelcomeEmailHtml` public method, never registered or called |
| D7 | `FormatCurrency` — private, never called. | Found | Review identifies `FormatCurrency` private method never called |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | Review identifies `IsWithinDailyLimit` defined but never called |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Review identifies `ObfuscateAccount` superseded by `MaskAccountNumber`, never called |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | Review identifies `ToTitleCase` "experimental utility never integrated", never called |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review identifies `JoinWithSeparator` duplicated by `JoinWithSeparatorFixed` |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | Review identifies `_auditLog` and `_requestCount` are static and not thread-safe |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Review identifies `new Regex(...)` created per call and recommends making `static readonly` |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review identifies string concatenation in loop and recommends using `string.Join` |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Review identifies `_smtpClient` held as instance field |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | Review identifies `IsBlank` duplicates `string.IsNullOrWhiteSpace` |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | Review identifies `GetOpenConnection()` returns undisposed `SqlConnection` |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies production secrets in source control |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Review identifies log level set to `Debug` for all namespaces |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies `ValidateLifetime = false` in JWT config |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review identifies HTTPS redirection commented out |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review identifies `UseDeveloperExceptionPage()` called unconditionally |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review identifies overly permissive CORS policy |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | Review identifies `<DebugSymbols>true</DebugSymbols>` and `<DebugType>full</DebugType>` in release |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | Review identifies outdated package |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Review identifies missing environment-specific overrides |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project exists | Found | Review identifies no test project exists and recommends adding `xunit`/`MSTest` test project with tests for key areas |