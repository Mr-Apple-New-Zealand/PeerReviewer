# AI Review Scorecard

> **Branch:** `Qwen3.5-2B` &nbsp;·&nbsp; **Commit:** `1b232c6`

Total: 49 Found / 3 Partial / 18 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query. | Found | "SQL Injection via string interpolation in `ExecuteQuery`" and "`Login` does not handle exceptions" imply the vulnerability in the login flow, though the specific interpolation in `Login` is covered by the general `ExecuteQuery` finding. |
| C2 | Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "Hardcoded admin bypass password (`SuperAdmin2024`)" and "Admin bypass logic allows login without DB check". |
| C3 | Broken password hashing — MD5 with no salt. | Found | "MD5 used for password hashing (cryptographically broken)." |
| C4 | SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated. | Found | "`UpdateUser` does not pass parameters to `ExecuteNonQuery`" and "`DeleteUser` does not pass parameters". |
| C5 | SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause. | Found | "`SearchUsers` catches all exceptions... `ExecuteQuery` used for search, vulnerable to SQL injection." |
| C6 | SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` concatenated. | Found | "`ExecuteNonQuery` called with raw SQL string, not parameterized" in `TransactionService.cs` lines 52/54. |
| C7 | SQL Injection (RecordTransaction) — `description` is interpolated. | Found | "`RecordTransaction` uses string interpolation for IDs, risking SQL injection." |
| C8 | Hardcoded production credentials — DB password, JWT secret, SMTP credentials committed. | Found | "Production database credentials committed to source control", "JWT secret key is weak and committed", "SMTP password committed". |
| C9 | JWT lifetime validation disabled (`ValidateLifetime = false`). | Found | "JWT `ValidateLifetime` set to `false`." |
| C10 | Broken Access Control — `PUT /api/user/{id}` has no check that caller owns account. | Found | "Missing authorization check for user update. Ensure user can only update their own data". |
| C11 | Missing Authorization — `DELETE /api/user/{id}` has no role check. | Found | "Missing authorization check for user deletion. Ensure user can only delete their own data". |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows zero-value transfers. | Missed | The review mentions balance checks and self-transfers but does not mention the zero-amount validation flaw. |
| L2 | Balance check excludes the fee — `fromBalance >= amount` should be `>= amount + fee`. | Found | "Balance check uses `amount` but deducts `amount + fee`. Change condition to `fromBalance >= totalDebit`." |
| L3 | Off-by-one in pagination — `skip = page * pageSize`. | Missed | The review mentions pagination tests are missing but does not identify the off-by-one logic error itself. |
| L4 | Incorrect interest rate — uses `0.05m` instead of `0.01m`. | Partial | "Interest bonus rate hardcoded" is noted, but the specific incorrect value (5% vs 1%) is not identified. |
| L5 | Self-transfer allowed — no check that `fromUserId != request.ToUserId`. | Found | "No check for self-transfer (`fromUserId == toUserId`). Add validation to prevent transferring to oneself." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation — identical guard blocks in `GetUserById`, `UpdateUser`, `DeleteUser`. | Missed | The review does not mention extracting the duplicated ID validation logic. |
| R2 | Loop string concatenation in `JoinWithSeparator`. | Found | "String concatenation in loop. Use `StringBuilder` or `string.Join`." |
| R3 | Overly long `GenerateJwtToken`. | Missed | The review does not comment on the length or structure of `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows all exceptions. | Found | "`SearchUsers` catches all exceptions and returns empty list." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad). | Found | "`SendWelcomeEmail` catches `Exception` and prints to console." |
| E3 | No database transaction around two UPDATE statements in `Transfer`. | Missed | The review notes SQL injection and parameterization issues but does not mention the lack of a DB transaction for consistency. |
| E4 | Email failure in `Transfer` propagates exception after commit. | Missed | The review does not mention the error propagation issue in `Transfer`. |
| E5 | `catch (Exception ex)` exposes `ex.Message` in `UserController`. | Found | "`UpdateUser` catches `ArgumentException` and returns message... `DeleteUser` catches broad `Exception`". |
| E6 | `ExecuteNonQuery` closes connection only on happy path. | Found | "`ExecuteNonQuery` opens connection but does not use `using`... exception path skips even the close" (implied by resource leak findings). |
| E7 | No rate limiting or account lockout on failed login attempts. | Missed | The review does not mention rate limiting or brute-force protection. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` in `Login` never closed. | Found | "`Login` does not handle exceptions from DB operations" and general resource leak findings in `DatabaseHelper`. |
| RL2 | `GetOpenConnection()` returns live connection; `ExecuteQuery` never disposes. | Found | "`GetOpenConnection` returns open connection without disposal" and "`ExecuteQuery` opens connection but does not dispose it". |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose`; exception path skips close. | Found | "`ExecuteNonQuery` opens connection but does not use `using`". |
| RL4 | `SmtpClient` held as instance field on non-disposable service. | Found | "`SmtpClient` held as instance field, not thread-safe." |
| RL5 | `MailMessage` never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "`MailMessage` created but not disposed" in multiple lines. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`. | Found | "`jwtSecret` may be null, causing `GetBytes` to throw." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking count. | Found | "No check if `toUserTable` has rows before accessing `Rows[0]`" and "No check if `fromUserTable` has rows". |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` hides missing config. | Found | "`_config["Email:SmtpPort"]` may be null, causing `int.Parse` to throw." |
| N4 | `username.ToUpper()` throws if `username` is `null`. | Missed | The review does not mention the null check for `username` in email services. |
| N5 | `email.Length` and `username.Length` throw if argument is `null`. | Missed | The review does not mention null guards for string length checks in `StringHelper`. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws. | Found | "`userIdClaim` may be null, causing `int.Parse` to throw." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null`. | Missed | The review does not mention null checks for the request body in controllers. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate` and `MaxTransactionsPerDay` as source-code constants. | Found | "`TransactionFeeRate` hardcoded" and "`MaxTransactionsPerDay` hardcoded". |
| M2 | `1_000_000` deposit cap hardcoded inline. | Missed | The review mentions interest rate hardcoding but not the deposit cap constant. |
| M3 | Email addresses hardcoded as literals. | Missed | The review mentions subjects and timeouts but not the specific email address literals. |
| M4 | `254`, `3`, `20` used as bare literals in `StringHelper`. | Missed | The review does not mention the specific numeric literals in `StringHelper`. |
| M5 | `50` as page size upper bound is unnamed. | Found | "Page size limit hardcoded." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — never called. | Found | "`HashPasswordSha1` is unused." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "`ValidateToken` is unused" (implies the method itself is dead code, covering the unreachable block). |
| D3 | `TableExists` — never called. | Missed | The review states "`TableExists` uses `using`... No issue" implying it's valid code, missing that it's unused. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called. | Found | "`ExecuteQueryWithParams` marked `[Obsolete]` but still present." |
| D5 | `BuildHtmlTemplate` — private method never invoked. | Partial | "`BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml`" — the review misses that `SendWelcomeEmailHtml` is also unused, making this dead code. |
| D6 | `SendWelcomeEmailHtml` — never registered or called. | Missed | The review does not explicitly state `SendWelcomeEmailHtml` is unused/dead code, only that it lacks exception handling. |
| D7 | `FormatCurrency` — private, never called. | Found | "`FormatCurrency` is unused." |
| D8 | `IsWithinDailyLimit` — defined but never called. | Missed | The review mentions adding tests for it but does not identify it as dead code. |
| D9 | `ObfuscateAccount` — superseded, never called. | Partial | "`MaskAccountNumber` and `ObfuscateAccount` are similar. Consolidate" — implies redundancy but doesn't explicitly state `ObfuscateAccount` is unused/dead. |
| D10 | `ToTitleCase` — never called. | Found | "`ToTitleCase` duplicates standard library functionality. Remove if not used". |
| D11 | `JoinWithSeparatorFixed` — correct implementation never used. | Found | "`JoinWithSeparatorFixed` duplicates `string.Join`. Remove if not used". |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state — `_auditLog` and `_requestCount`. | Found | "Static mutable state `_auditLog`" and "Static mutable state `_requestCount`". |
| A2 | Regex compiled per-call. | Found | "`new Regex` inside method. Use `static readonly` regex." |
| A3 | String concatenation in loop. | Found | "String concatenation in loop. Use `StringBuilder` or `string.Join`." |
| A4 | Shared mutable `SmtpClient`. | Found | "`SmtpClient` held as instance field, not thread-safe." |
| A5 | Reimplementing BCL — `IsBlank`. | Found | "`IsBlank` duplicates `string.IsNullOrWhiteSpace`." |
| A6 | Leaking connection — `GetOpenConnection()`. | Found | "`GetOpenConnection` returns open connection without disposal." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control. | Found | "Production database credentials committed to source control." |
| CF2 | Log level `Debug` in production. | Found | "Debug log levels set for production." |
| CF3 | JWT `ValidateLifetime = false`. | Found | "JWT `ValidateLifetime` set to `false`." |
| CF4 | HTTPS disabled. | Found | "HTTPS redirection commented out." |
| CF5 | `UseDeveloperExceptionPage()` called unconditionally. | Found | "`UseDeveloperExceptionPage()` enabled unconditionally." |
| CF6 | Open CORS policy. | Found | "CORS policy allows any origin, method, and header." |
| CF7 | `DebugSymbols = true` in release. | Found | "`DebugSymbols` set to `true` in release." |
| CF8 | Pinned outdated package `Newtonsoft.Json`. | Missed | The review does not mention the outdated Newtonsoft.Json package. |
| CF9 | No `appsettings.Production.json`. | Missed | The review does not mention the missing production-specific config file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage for key areas. | Found | "No test project exists. Create test project with unit tests for critical methods." |