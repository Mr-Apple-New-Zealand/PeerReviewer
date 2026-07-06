# AI Review Scorecard

> **Branch:** `Qwen3.5-4B` &nbsp;·&nbsp; **Commit:** `1e986df`

Total: 18 Found / 6 Partial / 46 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query. | Missed | The review mentions SQL queries are hardcoded (A3/A4 area) and MD5 issues, but does not explicitly identify the SQL injection vulnerability in the `Login` method's string interpolation. |
| C2 | Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` | Missed | The review mentions hardcoded credentials generally but does not identify the specific `AdminBypassPassword` backdoor constant. |
| C3 | Broken password hashing — MD5 with no salt. | Found | "MD5 is cryptographically broken and unsuitable for password hashing." |
| C4 | SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated. | Missed | The review mentions SQL queries are hardcoded in services but does not explicitly flag the SQL injection in `UpdateUser` or `DeleteUser`. |
| C5 | SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause. | Missed | The review mentions `SearchUsers` swallows exceptions (E1) but does not identify the SQL injection vulnerability. |
| C6 | SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated. | Missed | The review mentions SQL queries are hardcoded but does not explicitly identify the SQL injection in `Transfer` or `Deposit`. |
| C7 | SQL Injection (RecordTransaction) — `description` is interpolated. | Missed | The review does not identify the SQL injection in `RecordTransaction`. |
| C8 | Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed. | Found | "Hardcoded fallback credentials (`sa`/`Admin1234!`) in source code." and "Hardcoded fallback SMTP credentials in source code." |
| C9 | JWT lifetime validation disabled (`ValidateLifetime = false`) | Partial | The review notes "JWT token expiration is set to 30 days" and suggests reducing it, but misses the specific `ValidateLifetime = false` configuration issue that disables expiration entirely. |
| C10 | Broken Access Control — `PUT /api/user/{id}` has no check that the caller owns the account. | Found | "`UpdateUser` lacks authorization check, allowing any user to update any other user's data." |
| C11 | Missing Authorization — `DELETE /api/user/{id}` has no role check. | Found | "`DeleteUser` lacks authorization check, allowing any user to delete any other user." |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows zero-value transfers. | Missed | The review does not mention the zero-value transfer logic error. |
| L2 | Balance check excludes the fee. | Missed | The review does not mention the balance check logic error regarding fees. |
| L3 | Off-by-one in pagination — `skip = page * pageSize`. | Missed | The review mentions validating page/pageSize but does not identify the off-by-one calculation error. |
| L4 | Incorrect interest rate — uses `0.05m` instead of `0.01m`. | Missed | The review mentions interest rate is hardcoded (M2/CF area) but does not identify the incorrect value/logic. |
| L5 | Self-transfer allowed — no check that `fromUserId != request.ToUserId`. | Found | "`Transfer` does not verify that the `fromUserId` in the request matches the authenticated user's ID." (Note: While the review frames it as auth mismatch, it effectively covers the self-transfer/ownership check missing). |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation — identical `id <= 0 / id > 1_000_000` guard blocks. | Missed | The review mentions `ValidateUserId` caps ID arbitrarily but does not suggest extracting duplicated validation logic. |
| R2 | Loop string concatenation — `JoinWithSeparator` uses `+=`. | Partial | The review mentions `JoinWithSeparator` simply wraps `string.Join` (which is incorrect per ref doc, it uses `+=`) and suggests removing it, but doesn't explicitly flag the O(n^2) concatenation anti-pattern as the primary issue. |
| R3 | Overly long `GenerateJwtToken` | Missed | The review does not mention refactoring `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows all exceptions and returns an empty list. | Found | "`SearchUsers` catches `Exception` and returns an empty list, hiding errors from the caller." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad). | Found | "`SendWelcomeEmail` catches `Exception` and prints to console, silently failing in production." |
| E3 | No database transaction around the two UPDATE statements. | Missed | The review mentions `SqlTransaction` is used but not disposed (RL area), but does not identify the missing transaction context for consistency. |
| E4 | Email failure in `Transfer` propagates an exception after DB commit. | Missed | The review does not identify this specific error handling inconsistency. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client. | Missed | The review does not identify the leakage of internal error details in `UserController`. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path. | Missed | The review mentions `SqlDataAdapter` disposal but does not identify the connection leak on exception in `ExecuteNonQuery`. |
| E7 | No rate limiting or account lockout on failed login attempts. | Missed | The review does not mention rate limiting or account lockout. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed. | Missed | The review does not explicitly identify the resource leak in `Login`. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` never disposes. | Missed | The review mentions `ExecuteQuerySafe` issues but does not identify the connection leak in `GetOpenConnection`/`ExecuteQuery`. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection. | Missed | The review does not identify this specific disposal issue. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service. | Found | "`SmtpClient` is instantiated in the constructor but never disposed, holding socket resources." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed. | Found | "`MailMessage` is created but not disposed in `SendTransferNotification`." and "`MailMessage` is created but not disposed in `SendWelcomeEmail`." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`. | Missed | The review mentions JWT secret fallback but does not identify the null reference risk in `GetBytes`. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Found | "`Transfer` accesses `fromUserTable.Rows[0]["Email"]` and `toUserTable.Rows[0]["Username"]` without null checks." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct. | Missed | The review does not identify this specific null/config fallback issue. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | The review does not identify this specific null reference risk. |
| N5 | `email.Length` and `username.Length` throw if argument is `null`. | Missed | The review does not identify these null reference risks in `StringHelper`. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws. | Found | "`User.FindFirst(...)?.Value` is parsed as int, but `Value` could be null if claim exists but value is null." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null`. | Missed | The review does not identify the missing null check for the request body. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants. | Found | "`TransactionFeeRate` (0.01m) is hardcoded." and "`MaxTransactionsPerDay` (10) is hardcoded." |
| M2 | `1_000_000` deposit cap hardcoded inline. | Found | "`MaxDepositAmount` (1000000) is hardcoded." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded. | Partial | The review mentions "Email subjects are hardcoded" and "Hardcoded fallback SMTP credentials", but does not explicitly flag the hardcoded email address literals in the code. |
| M4 | `254`, `3`, `20` used as bare literals in `StringHelper`. | Missed | The review does not identify these specific magic numbers in `StringHelper`. |
| M5 | `50` as the page size upper bound is unnamed. | Found | "`pageSize` limit (50) is hardcoded." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Missed | The review does not identify `HashPasswordSha1` as dead code. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Missed | The review mentions `ValidateToken` catches exceptions but does not identify the unreachable code. |
| D3 | `TableExists` — never called from any service or controller. | Missed | The review does not identify `TableExists` as dead code. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called. | Missed | The review does not identify `ExecuteQueryWithParams` as dead code. |
| D5 | `BuildHtmlTemplate` — private method never invoked. | Missed | The review does not identify `BuildHtmlTemplate` as dead code. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Missed | The review does not identify `SendWelcomeEmailHtml` as dead code. |
| D7 | `FormatCurrency` — private, never called. | Missed | The review does not identify `FormatCurrency` as dead code. |
| D8 | `IsWithinDailyLimit` — defined but never called. | Missed | The review does not identify `IsWithinDailyLimit` as dead code. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Missed | The review mentions `MaskAccountNumber` is unused (D10/D9 confusion), but does not identify `ObfuscateAccount`. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Missed | The review does not identify `ToTitleCase` as dead code. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`. | Missed | The review mentions `JoinWithSeparator` wraps `string.Join` (incorrectly) and suggests removing it, but does not identify `JoinWithSeparatorFixed` as unused dead code. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state — `_auditLog` and `_requestCount` are `static`. | Missed | The review does not identify the mutable static state anti-pattern. |
| A2 | Regex compiled per-call — `new Regex(...)` inside instance methods. | Partial | The review mentions `Regex` is instantiated in a static field but not marked `static readonly` correctly, which is partially related but misses the per-call allocation issue in instance methods. |
| A3 | String concatenation in loop — classic O(n²) pattern. | Missed | The review mentions `JoinWithSeparator` wraps `string.Join` but does not explicitly flag the O(n^2) concatenation anti-pattern in the loop. |
| A4 | Shared mutable `SmtpClient` — `SmtpClient` is not thread-safe. | Found | "`SmtpClient` is not thread-safe and is held as an instance field." |
| A5 | Reimplementing BCL — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Missed | The review does not identify `IsBlank` as a BCL reimplement. |
| A6 | Leaking connection — `GetOpenConnection()` is an anti-pattern. | Missed | The review mentions `ExecuteQuerySafe` issues but does not explicitly flag `GetOpenConnection` as an anti-pattern. |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control — DB password, JWT secret, SMTP password. | Found | "Hardcoded fallback credentials (`sa`/`Admin1234!`) in source code." |
| CF2 | Log level `Debug` in production. | Missed | The review does not identify the debug log level issue. |
| CF3 | JWT `ValidateLifetime = false`. | Partial | The review mentions JWT expiration is set to 30 days, but misses the `ValidateLifetime = false` configuration. |
| CF4 | HTTPS disabled — `UseHttpsRedirection()` commented out. | Missed | The review does not identify the HTTPS redirection issue. |
| CF5 | `UseDeveloperExceptionPage()` called unconditionally. | Partial | The review mentions `UseDeveloperExceptionPage()` is used in development but ensures it's not in production, which is a mitigation suggestion but doesn't explicitly flag the unconditional call as an issue. |
| CF6 | Open CORS policy — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`. | Found | "CORS policy allows any origin, method, and header, enabling cross-site attacks." |
| CF7 | `DebugSymbols = true` / `DebugType = full` always emitted. | Missed | The review mentions `DebugSymbols` is false (incorrectly) and suggests setting it to true, missing the issue that it should be false in release. |
| CF8 | Pinned outdated package — `Newtonsoft.Json 12.0.3`. | Missed | The review does not identify the outdated package issue. |
| CF9 | No `appsettings.Production.json`. | Missed | The review does not identify the missing production config file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage. | Found | "No test project exists." and lists specific areas needing tests. |