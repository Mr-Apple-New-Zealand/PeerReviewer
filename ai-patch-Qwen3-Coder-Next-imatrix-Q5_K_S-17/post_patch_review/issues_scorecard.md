# AI Review Scorecard

> **Branch:** `Qwen3-Coder-Next` &nbsp;·&nbsp; **Commit:** `9c30f02`

Total: 17 Found / 11 Partial / 42 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query. | Partial | Review mentions `ExecuteQuery` concatenates user input causing SQL injection, but does not specifically name `AuthService.Login` or the login bypass payload. |
| C2 | Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin. | Missed | |
| C3 | Broken password hashing — MD5 with no salt. | Partial | Review mentions "Passwords hashed with SHA-256 without salt", which is factually incorrect (code uses MD5) but identifies the missing salt issue. |
| C4 | SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated. | Missed | Review mentions SQL injection generally via `ExecuteQuery` but does not name `UpdateUser` or `DeleteUser`. |
| C5 | SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause. | Missed | Review mentions `SearchUsers` in Null Reference section but not SQL injection specifically for this method. |
| C6 | SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated. | Missed | Review mentions `Transfer` resource leaks and logic errors, but not SQL injection specifically. |
| C7 | SQL Injection (RecordTransaction) — `description` is interpolated. | Missed | |
| C8 | Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed. | Partial | Review mentions "Hardcoded fallback credentials" in `DatabaseHelper` and "JWT signing key falls back to hardcoded weak secret", covering parts of this. |
| C9 | JWT lifetime validation disabled (`ValidateLifetime = false`). | Missed | Review mentions JWT expiration is hardcoded, but not that lifetime validation is disabled. |
| C10 | Broken Access Control — `PUT /api/user/{id}` has no check that the caller owns the account. | Missed | Review mentions `Refund` lacks checks, but not `UpdateUser` ownership check. |
| C11 | Missing Authorization — `DELETE /api/user/{id}` has no role check. | Missed | |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows zero-value transfers. | Missed | |
| L2 | Balance check excludes the fee. | Missed | |
| L3 | Off-by-one in pagination — `skip = page * pageSize`. | Partial | Review mentions `GetUsersPage` calculates skip but doesn't validate `page < 1`, missing the specific off-by-one formula error. |
| L4 | Incorrect interest rate — deposit bonus uses `0.05m`. | Missed | |
| L5 | Self-transfer allowed — no check that `fromUserId != request.ToUserId`. | Missed | |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation — identical `id <= 0` guard blocks. | Missed | |
| R2 | Loop string concatenation — `JoinWithSeparator` uses `+=`. | Missed | Review mentions `JoinWithSeparatorFixed` is dead code, but not the O(n²) issue in `JoinWithSeparator`. |
| R3 | Overly long `GenerateJwtToken`. | Missed | |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows all exceptions. | Partial | Review mentions `SearchUsers` catches Exception and re-throws, which is slightly different from swallowing, but addresses the error handling. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad). | Partial | Review mentions `SendWelcomeEmail` catches `SmtpException`, missing the broader `Exception` catch issue. |
| E3 | No database transaction around the two UPDATE statements. | Found | Review states "`Transfer` uses a new connection for updates instead of the transaction-scoped connection, breaking atomicity." |
| E4 | Email failure in `Transfer` propagates an exception after commit. | Missed | |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly. | Partial | Review mentions `Refund` leaks implementation details, but not `UpdateUser` specifically. |
| E6 | `ExecuteNonQuery` closes connection only on happy path. | Missed | |
| E7 | No rate limiting or account lockout on failed login attempts. | Missed | |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed. | Missed | |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` never disposes. | Found | Review states "`GetOpenConnection` returns an open `SqlConnection` without disposing it, leaking connections." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection. | Missed | |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service. | Missed | |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed. | Missed | |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`. | Found | Review states "`GetSigningKey` uses `Environment.GetEnvironmentVariable` which can return null, passed to `GetBytes`." |
| N2 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Missed | |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` hides missing config. | Missed | |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | |
| N5 | `email.Length` and `username.Length` throw if argument is `null`. | Missed | |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws. | Partial | Review mentions `User.FindFirst(...)?.Value` can be null but says `int.TryParse` handles it, missing the potential crash if parsing fails or isn't used. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null`. | Partial | Review mentions moving `request == null` check before token validation, implying the check exists but is misplaced. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate` and `MaxTransactionsPerDay` as source-code constants. | Found | Review states "`TransactionFeeRate`, `MaxTransactionsPerDay`... are hardcoded." |
| M2 | `1_000_000` deposit cap hardcoded inline. | Found | Review states "`DepositCap`... are hardcoded." |
| M3 | Email addresses hardcoded as literals. | Found | Review states "Email subjects and addresses are hardcoded constants." |
| M4 | `254`, `3`, `20` used as bare literals. | Missed | |
| M5 | `50` as the page size upper bound is unnamed. | Found | Review states "Default `pageSize` 20 and max 50 in `GetUsersPage` are hardcoded." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Missed | |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Missed | |
| D3 | `TableExists` — never called from any service or controller. | Missed | |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called. | Found | Review states "`ExecuteQueryWithParams` is marked `[Obsolete]` but still present." |
| D5 | `BuildHtmlTemplate` — private method never invoked. | Missed | |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Missed | |
| D7 | `FormatCurrency` — private, never called. | Found | Review states "`FormatCurrency` is defined but never used." |
| D8 | `IsWithinDailyLimit` — defined but never called. | Missed | |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Review states "`ObfuscateAccount` duplicates logic of `MaskAccountNumber` and is never called." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | Review states "`ToTitleCase` is never called anywhere in the codebase." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists but is never used. | Found | Review states "`JoinWithSeparatorFixed` is a duplicate of `JoinWithSeparator` and is never called." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state — `_auditLog` and `_requestCount` are `static`. | Found | Review states "`AuditLog` and `RequestCount` are static mutable state, not thread-safe." |
| A2 | Regex compiled per-call — `new Regex(...)` inside instance methods. | Missed | |
| A3 | String concatenation in loop — classic O(n²) pattern. | Missed | |
| A4 | Shared mutable `SmtpClient` — not thread-safe. | Missed | |
| A5 | Reimplementing BCL — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | Review states "`IsBlank` duplicates `string.IsNullOrWhiteSpace` and is never called." |
| A6 | Leaking connection — `GetOpenConnection()` is an anti-pattern. | Found | Review states "`GetOpenConnection` returns an open `SqlConnection` without disposing it, leaking connections." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control. | Partial | Review mentions hardcoded credentials and fallbacks, but not explicitly that secrets are committed to source control in `appsettings.json`. |
| CF2 | Log level `Debug` in production. | Missed | |
| CF3 | JWT `ValidateLifetime = false`. | Missed | |
| CF4 | HTTPS disabled. | Missed | |
| CF5 | `UseDeveloperExceptionPage()` called unconditionally. | Partial | Review mentions ensuring it's not in Prod, implying it might be, but doesn't explicitly flag it as unconditional. |
| CF6 | Open CORS policy. | Found | Review states "CORS policy allows any method and header, potentially increasing attack surface." |
| CF7 | `DebugSymbols = true` / `DebugType = full` always emitted. | Missed | Review suggests setting them for dev, implying they might be off, but doesn't flag them as always on in release. |
| CF8 | Pinned outdated package — `Newtonsoft.Json 12.0.3`. | Missed | |
| CF9 | No `appsettings.Production.json`. | Missed | |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage. | Found | Review states "No test project exists" and lists specific areas needing tests. |