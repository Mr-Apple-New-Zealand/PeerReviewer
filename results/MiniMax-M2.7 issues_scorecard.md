# AI Review Scorecard

> **Branch:** `MiniMax-M2.7` &nbsp;·&nbsp; **Commit:** `d71bbc0`

Total: 50 Found / 20 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "Login constructs SQL queries using string concatenation instead of parameterized statements, creating a critical SQL injection vulnerability" |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "AdminBypassPassword provides a hardcoded backdoor that bypasses normal authentication" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "MD5 hashing is used for passwords, which is cryptographically weak and vulnerable to collision attacks" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "UpdateUser and DeleteUser both use direct string interpolation in SQL statements rather than parameterized commands, exposing the system to injection attacks" |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "ExecuteQuery uses string interpolation for tableName and whereClause - SQL injection vulnerability!" |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "RecordTransaction constructs SQL using string concatenation instead of parameterized queries, creating an injection risk" |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "RecordTransaction constructs SQL using string concatenation instead of parameterized queries, creating an injection risk" |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "Hardcoded fallback credentials in the connection string represent a significant security gap" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "ValidateLifetime is disabled, allowing tokens to remain valid indefinitely" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | "UpdateUser catches ArgumentException and returns ex.Message - could leak internal details" |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | "DeleteUser catches generic Exception and logs, but returns a generic message" |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | "Transfer validates that balance exceeds the amount but doesn't account for transaction fees when checking available funds" |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "Transfer validates that balance exceeds the amount but doesn't account for transaction fees when checking available funds" |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "Pagination calculates offset as page * pageSize when it should be (page - 1) * pageSize to skip the correct number of records" |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | "Deposit method has incorrect interest rate calculation" |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | "Transfer validates that balance exceeds the amount but doesn't account for transaction fees when checking available funds" |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | "UpdateUser and DeleteUser both use direct string interpolation in SQL statements rather than parameterized commands, exposing the system to injection attacks" |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "JoinWithSeparator builds strings through concatenation in a loop rather than using StringBuilder or the built-in Join method" |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | "The JWT token expiration is set to 30 days without proper validation checks" |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "ExecuteQuery uses string interpolation for tableName and whereClause - SQL injection vulnerability!" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | "SmtpClient is stored as an instance field and reused across calls, which is not thread-safe for SMTP operations" |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | "Email notifications are sent after the database update commits, so if sending fails after the transaction completes, the operation cannot be rolled back" |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Found | "Email notifications are sent after the database update commits, so if sending fails after the transaction completes, the operation cannot be rolled back" |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | "UpdateUser catches ArgumentException and returns ex.Message - could leak internal details" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | "ExecuteNonQuery also uses raw SQL string concatenation" |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | "Login method doesn't have rate limiting or account lockout after failed attempts" |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "Login constructs SQL queries using string concatenation instead of parameterized statements, creating a critical SQL injection vulnerability" |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "GetOpenConnection returns an open connection that caller must dispose - resource leak risk" |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "ExecuteNonQuery also uses raw SQL string concatenation" |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "SmtpClient is stored as an instance field and reused across calls, which is not thread-safe for SMTP operations" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "SmtpClient is stored as an instance field and reused across calls, which is not thread-safe for SMTP operations" |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Partial | "The JWT token expiration is set to 30 days without proper validation checks" |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Partial | "Transfer validates that balance exceeds the amount but doesn't account for transaction fees when checking available funds" |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | "Hardcoded fallback credentials in the connection string represent a significant security gap" |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | "UpdateUser catches ArgumentException and returns ex.Message - could leak internal details" |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | "IsValidEmail and IsValidUsername compile regex patterns on every call instead of reusing static instances" |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Partial | "Login method doesn't have rate limiting or account lockout after failed attempts" |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | "UpdateUser catches ArgumentException and returns ex.Message - could leak internal details" |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Partial | "The JWT token expiration is set to 30 days without proper validation checks" |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Partial | "Deposit method has incorrect interest rate calculation" |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | "Hardcoded fallback credentials in the connection string represent a significant security gap" |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Partial | "IsValidEmail and IsValidUsername compile regex patterns on every call instead of reusing static instances" |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Partial | "Pagination calculates offset as page * pageSize when it should be (page - 1) * pageSize to skip the correct number of records" |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | "HashPasswordSha1" |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "ValidateToken contains unreachable code after the return statement, making it incomplete" |
| D3 | `TableExists` — never called from any service or controller. | Found | "TableExists" |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | "ExecuteQueryWithParams" |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | "BuildHtmlTemplate" |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | "SendWelcomeEmailHtml" |
| D7 | `FormatCurrency` — private, never called. | Found | "FormatCurrency" |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | "IsWithinDailyLimit" |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | "ObfuscateAccount" |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | "ToTitleCase" |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "JoinWithSeparator builds strings through concatenation in a loop rather than using StringBuilder or the built-in Join method" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | "UpdateUser catches ArgumentException and returns ex.Message - could leak internal details" |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "IsValidEmail and IsValidUsername compile regex patterns on every call instead of reusing static instances" |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "JoinWithSeparator builds strings through concatenation in a loop rather than using StringBuilder or the built-in Join method" |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "SmtpClient is stored as an instance field and reused across calls, which is not thread-safe for SMTP operations" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "IsBlank duplicates functionality that string.IsNullOrWhiteSpace already provides" |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "GetOpenConnection returns an open connection that caller must dispose - resource leak risk" |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "Hardcoded fallback credentials in the connection string represent a significant security gap" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | "UseDeveloperExceptionPage is active in the production environment" |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "ValidateLifetime is disabled, allowing tokens to remain valid indefinitely" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "HTTPS redirection is commented out, leaving the app vulnerable to man-in-the-middle attacks" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "UseDeveloperExceptionPage is active in the production environment" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "CORS policy allows unrestricted access from any origin with all methods and headers permitted" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Partial | "The JWT token expiration is set to 30 days without proper validation checks" |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | "Hardcoded fallback credentials in the connection string represent a significant security gap" |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | "Hardcoded fallback credentials in the connection string represent a significant security gap" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login — SQL injection boundary cases, correct vs. incorrect password; AuthService.GenerateJwtToken — claims mapping, expiry; TransactionService.Transfer — zero amount, self-transfer, fee deduction, insufficient funds (with fee); TransactionService.Deposit — interest rate correctness; UserService.GetUsersPage — pagination offset correctness (the off-by-one); StringHelper — null inputs, boundary lengths, separator trailing character; Controller action results — correct HTTP status codes for various service responses | Found | "The project contains no test project and no test files whatsoever" |