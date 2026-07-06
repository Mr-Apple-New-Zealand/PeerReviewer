# AI Review Scorecard

> **Branch:** `Qwen3-32B` &nbsp;·&nbsp; **Commit:** `52391af`

Total: 55 Found / 3 Partial / 12 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) | Found | "SQL injection via string interpolation in `Login` method." |
| C2 | Backdoor / hardcoded admin bypass | Found | "Hardcoded admin backdoor password allows bypassing authentication." |
| C3 | Broken password hashing | Found | "MD5 used for password hashing is cryptographically broken." |
| C4 | SQL Injection (UpdateUser / DeleteUser) | Found | "SQL injection in `UpdateUser` via string interpolation." and "SQL injection in `DeleteUser` via string interpolation." |
| C5 | SQL Injection (SearchUsers) | Found | "SQL injection in `SearchUsers` via `ExecuteQuery` with raw WHERE clause." |
| C6 | SQL Injection (Transfer/Deposit) | Found | "SQL injection in `Transfer` via string interpolation in `ExecuteNonQuery`." and "SQL injection in `Deposit` via string interpolation." |
| C7 | SQL Injection (RecordTransaction) | Found | "SQL injection in `RecordTransaction` via string interpolation." |
| C8 | Hardcoded production credentials | Found | "Production database credentials and SMTP passwords are hardcoded in source control." |
| C9 | JWT lifetime validation disabled | Found | "JWT `ValidateLifetime` is set to `false`, allowing expired tokens to remain valid." |
| C10 | Broken Access Control (PUT /api/user/{id}) | Found | "Missing authorization check allows any authenticated user to update any user." |
| C11 | Missing Authorization (DELETE /api/user/{id}) | Found | "Missing authorization check allows any authenticated user to delete any user." |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | Zero-value transfers allowed | Missed | The review mentions balance checks and self-transfers but does not explicitly identify the `amount < 0` vs `amount <= 0` logic error allowing zero-value transfers. |
| L2 | Balance check excludes fee | Found | "Balance check uses `amount` but deducts `amount + fee`, allowing negative balances." |
| L3 | Off-by-one in pagination | Found | "Pagination skip calculation uses `page * pageSize` instead of `(page - 1) * pageSize`." |
| L4 | Incorrect interest rate | Partial | "Interest bonus calculation multiplies by `1`, making the `0.05m` rate effectively 5% instead of intended logic." (Identifies the 5% issue but attributes it to a redundant `* 1` rather than the hardcoded 0.05m constant itself). |
| L5 | Self-transfer allowed | Found | "No check prevents a user from transferring funds to themselves." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation | Missed | The review does not mention extracting the repeated `id <= 0 / id > 1_000_000` guard blocks into a helper method. |
| R2 | Loop string concatenation | Found | "String concatenation in loop in `JoinWithSeparator`." |
| R3 | Overly long GenerateJwtToken | Missed | The review does not suggest refactoring `GenerateJwtToken` into smaller helpers. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | SearchUsers swallows exceptions | Found | "`SearchUsers` catches all exceptions and returns empty list, hiding errors from caller." |
| E2 | SendWelcomeEmail catches Exception | Found | "`SendWelcomeEmail` swallows exceptions silently, failing silently on email delivery." |
| E3 | No database transaction in Transfer | Found | "Database updates in `Transfer` are not wrapped in a transaction, risking partial updates." |
| E4 | Email failure propagates exception | Missed | The review notes missing transactions but does not identify that email failure after commit causes inconsistent client responses. |
| E5 | ex.Message exposed to client | Found | "`ex.Message` is returned to the client, leaking internal implementation details." |
| E6 | ExecuteNonQuery connection leak on exception | Found | "`ExecuteNonQuery` opens connection but does not close it on exception paths." |
| E7 | No rate limiting on login | Missed | The review does not mention missing rate limiting or account lockout mechanisms. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | SqlConnection/Reader not disposed in Login | Found | "`SqlConnection` opened in `Login` is never closed or disposed." and "`SqlDataReader` is never closed or disposed." |
| RL2 | GetOpenConnection returns live connection | Found | "`GetOpenConnection` returns an open connection, shifting disposal responsibility to caller without guarantee." |
| RL3 | ExecuteNonQuery does not Dispose | Found | "`ExecuteNonQuery` opens connection but does not close it on exception paths." |
| RL4 | SmtpClient held as instance field | Found | "`SmtpClient` is held as an instance field; it is not thread-safe and may leak sockets." |
| RL5 | MailMessage not disposed | Found | "`MailMessage` is not disposed after sending." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | Jwt:SecretKey can be null | Found | "`jwtSecret` from config may be null, causing `GetBytes` to throw." |
| N2 | Rows[0] accessed without count check | Found | "`fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`." |
| N3 | SmtpPort fallback hides missing config | Missed | The review mentions null checks for SmtpHost but does not specifically critique the SmtpPort fallback logic or TLS implications. |
| N4 | username.ToUpper() NRE | Missed | The review does not identify the potential NullReferenceException in `username.ToUpper()`. |
| N5 | email/username Length NRE | Missed | The review does not identify missing null guards before accessing `.Length` on email/username arguments. |
| N6 | User.FindFirst Value null parse | Found | "`userIdClaim` may be null, causing `int.Parse` to throw." |
| N7 | UpdateUser request null check | Missed | The review does not mention missing null checks for the request body in `UpdateUser`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | TransactionFeeRate/MaxTransactionsPerDay constants | Found | "`TransactionFeeRate` (0.015m) is hardcoded." and "`MaxTransactionsPerDay` (10) is hardcoded." |
| M2 | Deposit cap hardcoded | Found | "Deposit limit `1000000` is hardcoded." |
| M3 | Email addresses hardcoded | Partial | "Email subjects are hardcoded." (Mentions subjects, not the specific sender/recipient address literals like `notifications@company.com`). |
| M4 | Bare literals for lengths | Found | "Email length limit `254` is hardcoded." and "Username length limits `3` and `20` are hardcoded." |
| M5 | Page size 50 unnamed | Found | "Page size limit `50` is hardcoded." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | HashPasswordSha1 unused | Found | "`HashPasswordSha1` is defined but never called." |
| D2 | ValidateToken unreachable code | Found | "`ValidateToken` has unreachable code after `return true`." |
| D3 | TableExists unused | Missed | The review does not mention `TableExists` as unused dead code. |
| D4 | ExecuteQueryWithParams unused | Found | "`ExecuteQueryWithParams` is marked `[Obsolete]` but still present." |
| D5 | BuildHtmlTemplate unused | Found | "`BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml` which is likely unused." |
| D6 | SendWelcomeEmailHtml unused | Partial | The review links it to `BuildHtmlTemplate` being unused but doesn't explicitly state `SendWelcomeEmailHtml` itself is never called/registered. |
| D7 | FormatCurrency unused | Found | "`FormatCurrency` is defined but never called." |
| D8 | IsWithinDailyLimit unused | Missed | The review does not identify `IsWithinDailyLimit` as unused dead code. |
| D9 | ObfuscateAccount unused | Found | "`ObfuscateAccount` duplicates `MaskAccountNumber` logic." |
| D10 | ToTitleCase unused | Found | "`ToTitleCase` duplicates standard library functionality." |
| D11 | JoinWithSeparatorFixed unused | Found | "`JoinWithSeparatorFixed` duplicates `string.Join` functionality." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state | Found | "`_auditLog` is static mutable state, causing memory leak and thread safety issues." |
| A2 | Regex compiled per-call | Found | "`new Regex` created on every call in `IsValidEmail`." |
| A3 | String concatenation in loop | Found | "String concatenation in loop in `JoinWithSeparator`." |
| A4 | Shared mutable SmtpClient | Found | "`SmtpClient` is held as an instance field; it is not thread-safe..." |
| A5 | Reimplementing BCL (IsBlank) | Found | "`IsBlank` duplicates `string.IsNullOrWhiteSpace`." |
| A6 | Leaking connection anti-pattern | Found | "`GetOpenConnection` returns an open connection, shifting disposal responsibility..." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Found | "Production database credentials and SMTP passwords are hardcoded in source control." |
| CF2 | Log level Debug in production | Found | "Logging level set to `Debug` for all namespaces." |
| CF3 | JWT ValidateLifetime false | Found | "JWT `ValidateLifetime = false` disables token expiration." |
| CF4 | HTTPS disabled | Found | "HTTPS redirection is commented out." |
| CF5 | UseDeveloperExceptionPage unconditional | Found | "`UseDeveloperExceptionPage()` enabled unconditionally." |
| CF6 | Open CORS policy | Found | "CORS allows any origin, method, and header." |
| CF7 | DebugSymbols/DebugType in release | Found | "`DebugSymbols` and `DebugType` set to full in project file." |
| CF8 | Pinned outdated Newtonsoft.Json | Found | "`Newtonsoft.Json` version 12.0.3 is outdated and vulnerable." |
| CF9 | No appsettings.Production.json | Missed | The review does not mention the absence of environment-specific configuration files. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | Missing Unit Tests (aggregate) | Found | "No test project exists." and lists specific areas needing testing like Transfer, Deposit, Login, etc. |