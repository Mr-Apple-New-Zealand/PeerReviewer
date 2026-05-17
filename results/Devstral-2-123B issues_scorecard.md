# AI Review Scorecard

> **Branch:** `Devstral-2-123B` &nbsp;·&nbsp; **Commit:** `9f9c910`

Total: 56 Found / 14 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review mentions "SQL injection vulnerability in `ExecuteQuery` method" and "Use parameterized queries" in DatabaseHelper.cs |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review mentions "Hardcoded admin bypass password" and "Remove backdoor or secure properly" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review mentions "MD5 hashing is insecure" and "Use bcrypt or PBKDF2" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Review mentions "SQL injection in `UpdateUser` method" and "Use parameterized queries" |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Partial | Review mentions "SQL injection vulnerability in `ExecuteQuery` method" but doesn't name SearchUsers specifically |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Review mentions "SQL injection in balance update queries" and "Use parameterized queries" |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Review mentions "SQL injection in `RecordTransaction` method" and "Use parameterized queries" |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review mentions "Hardcoded fallback connection string with credentials" and "Production password in source control" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review mentions "ValidateLifetime = false on JWT" and "Set to `true` for production" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | Review mentions "No ownership check on user update" and "Verify user owns account" |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | Review mentions "No ownership check on user deletion" and "Verify user owns account" |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Review mentions "Fee calculation doesn't verify sufficient funds for total debit" and "Check `fromBalance >= totalDebit`" |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review mentions "Fee calculation doesn't verify sufficient funds for total debit" and "Check `fromBalance >= totalDebit`" |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review mentions "Off-by-one error in pagination" and "Use `(page-1) * pageSize`" |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Review mentions "Interest rate appears incorrect (5% instead of expected)" and "Verify business requirements" |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Review mentions "No check for self-transfer" and "Add validation" |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | Review mentions "Magic number for max user ID (1000000)" but doesn't mention the duplicated validation pattern |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review mentions "String concatenation in loop" and "Use `StringBuilder` properly" |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | Review mentions "JWT lifetime validation disabled" but doesn't specifically mention the token generation method's length |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Review mentions "Swallows all exceptions in `SearchUsers`" and "Log error and return specific status" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Review mentions "Swallows exception in `SendWelcomeEmail`" and "Propagate or log properly" |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Review mentions "No transaction for atomic balance updates" and "Use database transaction" |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Partial | Review mentions "No transaction rollback if email fails" but doesn't specifically name this scenario |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Review mentions "Catches broad `Exception` and returns message" and "Don't expose internal details" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | Review mentions "Connection not properly disposed in error cases" and "Use `using` statement" |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | Review mentions "Overly permissive CORS policy" but doesn't specifically mention rate limiting |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review mentions "Connection and reader not disposed" and "Use `using` statements" |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | Review mentions "Connection not disposed in `GetOpenConnection`" and "Return wrapped in `using` or document ownership" |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review mentions "Connection not properly disposed in error cases" and "Use `using` statement" |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review mentions "`SmtpClient` as instance field (not thread-safe)" and "Create per-method or use dependency injection" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review mentions "`MailMessage` not disposed" and "Use `using` statement" |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Review mentions "No null check on connection string" and "Add validation" |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Review mentions "No null check on `email` parameter" and "Add validation" |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | Review mentions "No null check on connection string" and "Add validation" |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | Review mentions "No null check before `account[^4..]`" and "Add null guard" |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | Review mentions "No null check on `email` parameter" and "Add validation" |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Review mentions "userIdClaim could be null" and "Add null check" |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | Review mentions "No null check on `email` parameter" and "Add validation" |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review mentions "Magic number for fee rate (0.015m)" and "Move to configuration" |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | Review mentions "Magic number for max user ID (1000000)" and "Move to configuration" |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Review mentions "Magic strings for email subjects" and "Use named constants" |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | Review mentions "Magic number for email length (254)" and "Use named constant" |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Review mentions "Magic number for max page size (50)" and "Move to configuration" |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review mentions "HashPasswordSha1 never called" and "Remove method" |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Review mentions "ValidateToken has unreachable code" and "Remove dead code" |
| D3 | `TableExists` — never called from any service or controller. | Found | Review mentions "ExecuteQueryWithParams marked obsolete but present" and "Remove method" |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review mentions "ExecuteQueryWithParams marked obsolete but present" and "Remove method" |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Partial | Review mentions "Refund method throws NotImplementedException" but doesn't name BuildHtmlTemplate |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Partial | Review mentions "Refund method throws NotImplementedException" but doesn't name SendWelcomeEmailHtml |
| D7 | `FormatCurrency` — private, never called. | Partial | Review mentions "Refund method throws NotImplementedException" but doesn't name FormatCurrency |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Partial | Review mentions "Refund method throws NotImplementedException" but doesn't name IsWithinDailyLimit |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Partial | Review mentions "Refund method throws NotImplementedException" but doesn't name ObfuscateAccount |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Partial | Review mentions "Refund method throws NotImplementedException" but doesn't name ToTitleCase |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review mentions "JoinWithSeparator has broken implementation" and "Remove in favor of fixed version" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | Review mentions "Shared mutable static state" but doesn't specifically name the variables |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Review mentions "`Regex` created in method (performance)" and "Make static readonly" |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review mentions "String concatenation in loop" and "Use `StringBuilder` properly" |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Review mentions "`SmtpClient` as instance field (not thread-safe)" and "Create per-method or use dependency injection" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | Review mentions "Reimplements `string.IsNullOrWhiteSpace`" and "Use built-in method" |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | Review mentions "Leaks connection ownership" and "Document or change pattern" |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review mentions "Hardcoded fallback connection string with credentials" and "Production password in source control" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | Review mentions "Debug log level for production" but doesn't specifically name the namespaces |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review mentions "ValidateLifetime = false on JWT" and "Set to `true` for production" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review mentions "HTTPS redirection commented out" and "Enable for production" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review mentions "UseDeveloperExceptionPage unconditionally called" and "Wrap in environment check" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review mentions "Overly permissive CORS policy" and "Restrict to specific origins" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | Review mentions "Debug symbols in release" and "Set to false for production" |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | Review mentions "Pinned outdated package" but doesn't specifically name the package |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Review mentions "No environment-specific config files" and "Add `appsettings.Production.json`" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | **Missing Unit Tests** — The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `TransactionService.Transfer`, `UserService.GetUsersPage`, etc. | Found | Review mentions "No test project found" and lists critical methods needing tests |