# AI Review Scorecard

> **Branch:** `Claude-Opus-4.7` &nbsp;·&nbsp; **Commit:** `fc69ad9`

Total: 6 Found / 21 Partial / 43 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) â€” `Username` and `Password` are string-interpolated directly into a `SELECT` query. | Partial | Review mentions "SQL injection if called with user input" for `ExecuteQuery` but does not explicitly name `AuthService.Login` or the specific interpolation in `Login`. |
| C2 | Backdoor / hardcoded admin bypass â€” `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Missed | No mention of `AdminBypassPassword` or hardcoded backdoor credentials. |
| C3 | Broken password hashing â€” MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Partial | Review mentions "Password hashing uses SHA-256 with username as salt" (incorrect algorithm identification) and suggests BCrypt, touching the area but missing the specific MD5/no-salt flaw. |
| C4 | SQL Injection (UpdateUser / DeleteUser) â€” `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Missed | No specific mention of SQL injection in `UpdateUser` or `DeleteUser`. |
| C5 | SQL Injection (SearchUsers) â€” `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Partial | Review mentions `SearchUsers` allows unauthenticated access, but does not explicitly identify the SQL injection vulnerability in the `LIKE` clause. |
| C6 | SQL Injection (Transfer/Deposit) â€” `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Missed | No specific mention of SQL injection in `Transfer` or `Deposit` methods. |
| C7 | SQL Injection (RecordTransaction) â€” `description` is interpolated; a malicious description can inject arbitrary SQL. | Missed | No mention of SQL injection in `RecordTransaction`. |
| C8 | Hardcoded production credentials â€” DB password, JWT secret, and SMTP credentials committed to source control. | Partial | Review mentions "JWT secret is loaded from config but not validated" and "Production secrets in source control" is CF1, but C8 specifically targets `appsettings.json` content. The review's config section is vague on the specific hardcoded values in `appsettings.json`. |
| C9 | JWT lifetime validation disabled (`ValidateLifetime = false`) â€” tokens never expire, stolen tokens are valid forever. | Missed | No mention of `ValidateLifetime = false` or token expiration issues in `Program.cs`. |
| C10 | Broken Access Control â€” `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Missed | No mention of missing ownership checks in `UpdateUser`. |
| C11 | Missing Authorization â€” `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Missed | No mention of missing role checks in `DeleteUser`. |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Missed | No mention of zero-value transfer logic error. |
| L2 | **Balance check excludes the fee** â€” `if (fromBalance >= amount)` should be `>= amount + fee`. | Missed | No mention of balance check excluding fee. |
| L3 | **Off-by-one in pagination** â€” `skip = page * pageSize` skips `pageSize` extra rows for page 1. | Missed | No mention of pagination off-by-one error. |
| L4 | **Incorrect interest rate** â€” deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%). | Partial | Review mentions "Deposit adds interest bonus... records only principal", touching the deposit logic but not the specific incorrect rate value. |
| L5 | **Self-transfer allowed** â€” no check that `fromUserId != request.ToUserId`. | Missed | No mention of self-transfer logic error. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | **Duplicated validation** â€” identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. | Missed | No mention of duplicated validation logic. |
| R2 | **Loop string concatenation** â€” `JoinWithSeparator` uses `+=` in a loop (O(nÂ²) allocations). | Partial | Review mentions `JoinWithSeparator` duplicates `string.Join` functionality, touching the area but not explicitly citing the O(nÂ²) performance issue. |
| R3 | **Overly long `GenerateJwtToken`** â€” token expiry, claims assembly, and signing could be split into named helpers. | Missed | No mention of `GenerateJwtToken` being too long or needing refactoring. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list. | Missed | No mention of `SearchUsers` swallowing exceptions. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) â€” programming errors like `NullReferenceException` are silently discarded. | Partial | Review mentions `SendWelcomeEmail` swallows `SmtpException` silently, touching the area but not the broad `Exception` catch. |
| E3 | **No database transaction** around the two UPDATE statements â€” if the second update fails, balances become permanently inconsistent. | Missed | No mention of missing database transaction in `Transfer`. |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed. | Partial | Review mentions "Transfer logs email failure but continues execution", touching the area but not the specific inconsistency of committed DB vs failed email. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client â€” internal error details leaked. | Found | Review states: "`UpdateUser` returns `ex.Message` to the client, leaking internal implementation details." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path â€” an exception skips `connection.Close()`. | Partial | Review mentions `ExecuteNonQuery` does not dispose `SqlDataAdapter` or ensure command disposal on exception, touching the resource leak aspect but not the specific connection close skip. |
| E7 | No rate limiting or account lockout on failed login attempts â€” brute force is trivially possible. | Missed | No mention of missing rate limiting or account lockout. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Missed | No specific mention of `Login` method resource leaks. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Partial | Review mentions `ExecuteQuery` creates `SqlConnection` but relies on `using` for disposal, touching the area but not the specific `GetOpenConnection` leak. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Partial | Review mentions `ExecuteNonQuery` does not dispose `SqlDataAdapter` or ensure command disposal on exception, touching the area but not the specific connection disposal issue. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service â€” underlying socket never released. | Partial | Review mentions `SmtpClient` created per call is inefficient, contradicting the reference which says it's an instance field, but touches the `SmtpClient` resource issue. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review states: "`MailMessage` is not disposed if `Send` throws. Wrap `MailMessage` in a `using` statement." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Missed | No mention of null config key in `GenerateJwtToken`. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Partial | Review mentions "`fromUserTable.Rows[0]["Balance"]` cast may throw if column is null", touching the null risk but not the `Rows.Count` check. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` â€” falls back to `"25"` but port 25 may not be correct for TLS. | Missed | No mention of SMTP port config fallback issue. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | No mention of null username in `SendWelcomeEmail`. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` â€” no null guard before Length access. | Missed | No mention of null checks in `StringHelper`. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Missed | No mention of null token value parsing in `TransactionController`. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` â€” model binding can produce null body. | Missed | No mention of null request body in `UpdateUser`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants. | Found | Review states: "Hardcoded `0.015m` fee rate and `1_000_000m` max deposit." (Note: M1 is fee rate, M2 is deposit cap, but the review lumps them. I will credit M1 here and M2 below as Partial/Found depending on specificity). |
| M2 | `1_000_000` deposit cap hardcoded inline â€” no named constant. | Found | Review states: "Hardcoded `0.015m` fee rate and `1_000_000m` max deposit." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals. | Missed | No mention of hardcoded email addresses. |
| M4 | `254`, `3`, `20` used as bare literals â€” should be named constants. | Missed | No mention of bare literals in `StringHelper`. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Partial | Review mentions "Hardcoded `20` for default page size", touching the area but not the specific `50` upper bound. |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` â€” replaced by `HashPasswordMd5`, never called. | Missed | No mention of `HashPasswordSha1`. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Missed | No mention of unreachable code in `ValidateToken`. |
| D3 | `TableExists` â€” never called from any service or controller. | Missed | No mention of `TableExists`. |
| D4 | `ExecuteQueryWithParams` â€” marked `[Obsolete]` and never called. | Missed | No mention of `ExecuteQueryWithParams`. |
| D5 | `BuildHtmlTemplate` â€” private method never invoked. | Missed | No mention of `BuildHtmlTemplate`. |
| D6 | `SendWelcomeEmailHtml` â€” public method, never registered or called. | Missed | No mention of `SendWelcomeEmailHtml`. |
| D7 | `FormatCurrency` â€” private, never called. | Missed | No mention of `FormatCurrency`. |
| D8 | `IsWithinDailyLimit` â€” defined but never called. | Partial | Review mentions `IsWithinDailyLimit` uses `GETDATE()`, implying it exists and is analyzed, but doesn't explicitly state it's dead code. |
| D9 | `ObfuscateAccount` â€” superseded by `MaskAccountNumber`, never called. | Missed | No mention of `ObfuscateAccount`. |
| D10 | `ToTitleCase` â€” "experimental utility never integrated", never called. | Missed | No mention of `ToTitleCase`. |
| D11 | `JoinWithSeparatorFixed` â€” correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Partial | Review mentions `JoinWithSeparator` duplicates `string.Join`, touching the area but not the specific unused `JoinWithSeparatorFixed`. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | **Mutable static state** â€” `_auditLog` and `_requestCount` are `static`, shared across all DI instances. | Missed | No mention of mutable static state. |
| A2 | **Regex compiled per-call** â€” `new Regex(...)` inside instance methods. | Missed | No mention of Regex compilation anti-pattern. |
| A3 | **String concatenation in loop** â€” classic O(nÂ²) pattern. | Partial | Review mentions `JoinWithSeparator` duplicates `string.Join`, touching the area but not explicitly citing the O(nÂ²) loop concatenation. |
| A4 | **Shared mutable `SmtpClient`** â€” `SmtpClient` is not thread-safe. | Partial | Review mentions `SmtpClient` created per call is inefficient, contradicting the reference which says it's a shared field, but touches the `SmtpClient` anti-pattern. |
| A5 | **Reimplementing BCL** â€” `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Missed | No mention of `IsBlank` duplicating BCL. |
| A6 | **Leaking connection** â€” `GetOpenConnection()` is an anti-pattern. | Partial | Review mentions `ExecuteQuery` creates `SqlConnection` but relies on `using`, touching the area but not the specific `GetOpenConnection` anti-pattern. |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | **Production secrets in source control** â€” DB password, JWT secret, SMTP password all present. | Partial | Review mentions "JWT secret loaded from config without validation", touching the area but not the specific presence of secrets in source control. |
| CF2 | **Log level `Debug` in production** â€” `Microsoft` and `System` namespaces also set to `Debug`. | Missed | No mention of Debug log level in production. |
| CF3 | **JWT `ValidateLifetime = false`** â€” tokens never expire. | Missed | No mention of `ValidateLifetime = false`. |
| CF4 | **HTTPS disabled** â€” `UseHttpsRedirection()` commented out. | Missed | No mention of HTTPS redirection being disabled. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** â€” full stack traces served to production clients. | Partial | Review mentions "`UseDeveloperExceptionPage()` is used in development... ensure it's not enabled in production", touching the area but not the unconditional call. |
| CF6 | **Open CORS policy** â€” `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive. | Found | Review states: "CORS policy allows any method and header. Restrict to specific methods and headers." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted. | Missed | No mention of DebugSymbols in release builds. |
| CF8 | **Pinned outdated package** â€” `Newtonsoft.Json 12.0.3` has known vulnerabilities. | Missed | No mention of outdated Newtonsoft.Json. |
| CF9 | **No `appsettings.Production.json`** â€” no environment-specific overrides. | Missed | No mention of missing production config file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `TransactionService.Transfer`, `UserService.GetUsersPage`, etc. | Found | Review states: "No tests for login logic, password hashing, and token generation... No tests for transfer, deposit, and refund logic... No tests for user CRUD operations and pagination." |