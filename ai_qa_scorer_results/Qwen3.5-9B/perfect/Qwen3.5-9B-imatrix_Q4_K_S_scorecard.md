# Scorer: Qwen3.5-9B-imatrix:Q4_K_S
# Review type: perfect

# AI Review Scorecard

Total: 69 Found / 0 Partial / 1 Missed out of 70 issues.

## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | The review identifies SQL Injection (login) where `Username` and `Password` are string-interpolated directly into a `SELECT` query. |
| C2 | Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | The review identifies a Backdoor / hardcoded admin bypass where `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. |
| C3 | Broken password hashing — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | The review identifies Broken password hashing using MD5 with no salt, noting identical passwords produce identical hashes. |
| C4 | SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | The review identifies SQL Injection (UpdateUser / DeleteUser) where `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. |
| C5 | SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | The review identifies SQL Injection (SearchUsers) where `query` is interpolated into a LIKE clause via `ExecuteQuery`. |
| C6 | SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | The review identifies SQL Injection (Transfer/Deposit) where `fromUserId`, `toUserId`, and `amount` are concatenated into UPDATE statements. |
| C7 | SQL Injection (RecordTransaction) — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | The review identifies SQL Injection (RecordTransaction) where `description` is interpolated, allowing arbitrary SQL injection. |
| C8 | Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed to source control. | Found | The review identifies Hardcoded production credentials including DB password, JWT secret, and SMTP credentials committed to source control. |
| C9 | JWT lifetime validation disabled (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | The review identifies JWT lifetime validation disabled (`ValidateLifetime = false`) where tokens never expire. |
| C10 | Broken Access Control — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | The review identifies Broken Access Control on `PUT /api/user/{id}` lacking a check that the caller owns the account. |
| C11 | Missing Authorization — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | The review identifies Missing Authorization on `DELETE /api/user/{id}` lacking a role check. |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | The review identifies that the `amount < 0` check allows zero-value transfers (`amount == 0`). |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. | Found | The review identifies the Balance check excludes the fee, noting `if (fromBalance >= amount)` should be `>= amount + fee`. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. | Found | The review identifies Off-by-one in pagination where `skip = page * pageSize` skips extra rows for page 1. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%). | Found | The review identifies Incorrect interest rate where deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%). |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. | Found | The review identifies Self-transfer allowed with no check that `fromUserId != request.ToUserId`. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. | Found | The review identifies Duplicated validation with identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). | Found | The review identifies Loop string concatenation where `JoinWithSeparator` uses `+=` in a loop. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers. | Found | The review identifies Overly long `GenerateJwtToken` where token expiry, claims assembly, and signing could be split. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list. | Found | The review identifies `SearchUsers` swallowing all exceptions and returning an empty list. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | The review identifies `SendWelcomeEmail` catching `Exception` (too broad), discarding programming errors. |
| E3 | **No database transaction** around the two UPDATE statements. | Found | The review identifies No database transaction around the two UPDATE statements. |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed. | Found | The review identifies Email failure in `Transfer` propagating an exception after the DB transfer has already committed. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client. | Found | The review identifies `catch (Exception ex)` exposing `ex.Message` directly to the HTTP client. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path. | Found | The review identifies `ExecuteNonQuery` closing the connection only on the happy path. |
| E7 | No rate limiting or account lockout on failed login attempts. | Found | The review identifies No rate limiting or account lockout on failed login attempts. |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | The review identifies `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | The review identifies `GetOpenConnection()` returning a live connection where `ExecuteQuery` never disposes the result. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | The review identifies `ExecuteNonQuery` closing but not `Dispose` the connection, with the exception path skipping the close. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service. | Found | The review identifies `SmtpClient` held as an instance field on a non-disposable service. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | The review identifies `MailMessage` implementing `IDisposable` but never being disposed in `SendTransferNotification` or `SendWelcomeEmail`. |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | The review identifies `_config["Jwt:SecretKey"]` potentially returning `null`, causing `Encoding.UTF8.GetBytes(null!)` to throw. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Found | The review identifies `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS. | Found | The review identifies `int.Parse(_config["Email:SmtpPort"] ?? "25")` falling back to `"25"`. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | The review identifies `username.ToUpper()` throwing `NullReferenceException` if `username` is `null`. |
| N5 | `email.Length` and `username.Length` throw if argument is `null`. | Found | The review identifies `email.Length` and `username.Length` throwing if the argument is `null`. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | The review identifies `User.FindFirst(...)?.Value` potentially being `null`, causing `int.Parse(null!)` to throw. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null`. | Found | The review identifies `UpdateUser` and controller endpoints not checking `request == null`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants. | Found | The review identifies `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants. |
| M2 | `1_000_000` deposit cap hardcoded inline. | Found | The review identifies `1_000_000` deposit cap hardcoded inline. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals. | Found | The review identifies Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals. |
| M4 | `254`, `3`, `20` used as bare literals. | Found | The review identifies `254`, `3`, `20` used as bare literals. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | The review identifies `50` as the page size upper bound being unnamed and undocumented. |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | The review identifies `HashPasswordSha1` as replaced by `HashPasswordMd5` and never called. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | The review identifies Unreachable code after `return true` in `ValidateToken`. |
| D3 | `TableExists` — never called from any service or controller. | Found | The review identifies `TableExists` as never called from any service or controller. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called. | Found | The review identifies `ExecuteQueryWithParams` as marked `[Obsolete]` and never called. |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers. | Found | The review identifies `BuildHtmlTemplate` as a private method reachable only from `SendWelcomeEmailHtml`, which has no callers. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | The review identifies `SendWelcomeEmailHtml` as a public method never registered or called. |
| D7 | `FormatCurrency` — private, never called. | Found | The review identifies `FormatCurrency` as private and never called. |
| D8 | `IsWithinDailyLimit` — defined but never called. | Found | The review identifies `IsWithinDailyLimit` as defined but never called. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | The review identifies `ObfuscateAccount` as superseded by `MaskAccountNumber` and never called. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | The review identifies `ToTitleCase` as an experimental utility never integrated and never called. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | The review identifies `JoinWithSeparatorFixed` as existing alongside the broken `JoinWithSeparator` but never being used. |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances. | Found | The review identifies Mutable static state where `_auditLog` and `_requestCount` are `static`. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles. | Found | The review identifies Regex compiled per-call where `new Regex(...)` is inside instance methods. |
| A3 | **String concatenation in loop** — classic O(n²) pattern. | Found | The review identifies String concatenation in loop as a classic O(n²) pattern. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send. | Found | The review identifies Shared mutable `SmtpClient` which is not thread-safe. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | The review identifies Reimplementing BCL where `IsBlank` duplicates `string.IsNullOrWhiteSpace`. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern. | Found | The review identifies Leaking connection where `GetOpenConnection()` is an anti-pattern. |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | The review identifies Production secrets in source control including DB password, JWT secret, and SMTP password. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`. | Found | The review identifies Log level `Debug` in production for `Microsoft` and `System` namespaces. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | The review identifies JWT `ValidateLifetime = false` where tokens never expire. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | The review identifies HTTPS disabled where `UseHttpsRedirection()` is commented out. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | The review identifies `UseDeveloperExceptionPage()` called unconditionally, serving full stack traces. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive. | Found | The review identifies Open CORS policy with `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted. | Found | The review identifies `DebugSymbols = true` / `DebugType = full` always emitted. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities. | Found | The review identifies Pinned outdated package `Newtonsoft.Json 12.0.3` with known vulnerabilities. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides. | Found | The review identifies No `appsettings.Production.json` with no environment-specific overrides. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper` methods, and Controller action results. | Missed | The review states the project contains no test project and no test files, but fails to explicitly mention the specific key areas listed in the reference (e.g., `AuthService.Login`, `TransactionService.Transfer`, `UserService.GetUsersPage`, `StringHelper` methods, or Controller action results) as missing coverage targets. It only lists them as a general summary without confirming the specific missing tests for those symbols. |