# AI Review Scorecard

> **Branch:** `Devstral-2-123B` &nbsp;·&nbsp; **Commit:** `a8a8342`

Total: 50 Found / 4 Partial / 16 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) in `AuthService.Login` | Found | "SQL Injection in login query via string interpolation." |
| C2 | Backdoor / hardcoded admin bypass `AdminBypassPassword` | Found | "Hardcoded admin backdoor password allows bypassing authentication." |
| C3 | Broken password hashing (MD5, no salt) | Found | "MD5 used for password hashing is cryptographically broken." |
| C4 | SQL Injection (UpdateUser / DeleteUser) in `UserService` | Found | "SQL Injection in user update via string interpolation." and "SQL Injection in user deletion via string interpolation." |
| C5 | SQL Injection (SearchUsers) in `UserService` | Found | "SQL Injection in user search via string interpolation in LIKE clause." |
| C6 | SQL Injection (Transfer/Deposit) in `TransactionService` | Found | "SQL Injection in balance update via string interpolation." and "SQL Injection in deposit update via string interpolation." |
| C7 | SQL Injection (RecordTransaction) in `TransactionService` | Found | "SQL Injection in transaction recording via string interpolation." |
| C8 | Hardcoded production credentials in `appsettings.json` | Found | "Production database credentials and SMTP passwords are hardcoded in config." |
| C9 | JWT lifetime validation disabled | Found | "JWT lifetime validation is disabled, allowing tokens to never expire." |
| C10 | Broken Access Control (PUT /api/user/{id}) | Found | "Broken Access Control: Any authenticated user can update/delete any user." |
| C11 | Missing Authorization (DELETE /api/user/{id}) | Partial | The review mentions "update/delete any user" generally but does not explicitly distinguish the missing role check for the DELETE endpoint specifically from the PUT endpoint. |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | Zero-value transfers allowed (`amount < 0` check) | Missed | The review mentions balance checks and fees but does not identify the specific flaw allowing zero-value transfers due to the `<` instead of `<=` check. |
| L2 | Balance check excludes fee | Found | "Balance check only verifies `amount`, ignoring the `fee`, allowing negative balances." |
| L3 | Off-by-one in pagination | Found | "Pagination skip calculation uses `page * pageSize` instead of `(page - 1) * pageSize`." |
| L4 | Incorrect interest rate | Found | "Deposit interest bonus calculation multiplies by 1, making the bonus equal to the full 5% amount incorrectly." |
| L5 | Self-transfer allowed | Missed | The review does not mention the lack of a check for `fromUserId != toUserId`. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in `UserService` | Missed | The review does not mention extracting the duplicated ID validation logic. |
| R2 | Loop string concatenation in `JoinWithSeparator` | Found | "String concatenation in loop is O(n²)." |
| R3 | Overly long `GenerateJwtToken` | Missed | The review does not suggest refactoring `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows exceptions | Found | "Catch block swallows exception and returns empty list, hiding errors." |
| E2 | `SendWelcomeEmail` catches too broad `Exception` | Found | "Exception caught and logged to Console, then silently ignored." |
| E3 | No database transaction in `Transfer` | Found | "Multiple DB writes (debit, credit, record) lack atomic transaction scope." |
| E4 | Email failure propagates exception after commit | Missed | The review mentions missing transactions but not the specific issue of email failure causing error responses after successful DB commits. |
| E5 | Raw exception message exposed in `UserController` | Found | "Raw exception message returned to client in 500 response." |
| E6 | `ExecuteNonQuery` connection leak on exception | Found | "`ExecuteNonQuery` opens connection but does not dispose command or adapter." |
| E7 | No rate limiting on login | Missed | The review does not mention missing rate limiting or account lockout. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection`/`SqlDataReader` leak in `Login` | Found | "`SqlConnection` and `SqlDataReader` opened but never closed/disposed." |
| RL2 | `GetOpenConnection` leak | Found | "`GetOpenConnection` returns open connection without disposing; caller must manage it." |
| RL3 | `ExecuteNonQuery` connection leak | Found | "`ExecuteNonQuery` opens connection but does not dispose command or adapter." |
| RL4 | `SmtpClient` instance field leak | Found | "`SmtpClient` is not thread-safe and held as instance field; sockets may leak." |
| RL5 | `MailMessage` not disposed | Found | "`MailMessage` is `IDisposable` but never disposed." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` null check | Found | "`jwtSecret` may be null, passed to `Encoding.UTF8.GetBytes`." |
| N2 | `Rows[0]` access without count check | Found | "`fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`." |
| N3 | `SmtpPort` config fallback | Missed | The review mentions `SmtpHost` null check but not the specific `SmtpPort` fallback issue. |
| N4 | `username.ToUpper()` null ref | Missed | The review does not mention the null reference risk in `username.ToUpper()`. |
| N5 | `email.Length`/`username.Length` null ref | Missed | The review does not mention null checks for string length properties. |
| N6 | `User.FindFirst` null parse | Found | "`userIdClaim` may be null; `int.Parse` will throw `NullReferenceException`." |
| N7 | `request == null` check in `UpdateUser` | Missed | The review does not mention missing null checks for the request body. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate`/`MaxTransactionsPerDay` constants | Found | "`TransactionFeeRate` (0.015) is hardcoded." and "`MaxTransactionsPerDay` (10) is hardcoded." |
| M2 | Deposit cap hardcoded | Found | "Deposit limit (1000000) is hardcoded." |
| M3 | Email addresses hardcoded | Missed | The review does not mention hardcoded email addresses. |
| M4 | String length literals | Found | "Email length limit (254) is hardcoded." and "Username length limits (3, 20) are hardcoded." |
| M5 | Page size limit hardcoded | Found | "Page size limit (50) is hardcoded." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` unused | Missed | The review does not mention `HashPasswordSha1`. |
| D2 | Unreachable code in `ValidateToken` | Found | "`ValidateToken` always returns true due to early return before validation logic." |
| D3 | `TableExists` unused | Missed | The review does not mention `TableExists`. |
| D4 | `ExecuteQueryWithParams` unused | Found | "`ExecuteQueryWithParams` is marked `[Obsolete]` but still present." |
| D5 | `BuildHtmlTemplate` unused | Partial | The review says "Keep if used, but verify usage" for `BuildHtmlTemplate`, implying uncertainty rather than confirming it is dead/unused. |
| D6 | `SendWelcomeEmailHtml` unused | Partial | The review says "Verify usage; remove if dead" for `SendWelcomeEmailHtml`, implying uncertainty. |
| D7 | `FormatCurrency` unused | Found | "`FormatCurrency` is defined but never called." |
| D8 | `IsWithinDailyLimit` unused | Missed | The review does not mention `IsWithinDailyLimit`. |
| D9 | `ObfuscateAccount` unused | Found | "`ObfuscateAccount` duplicates functionality of `MaskAccountNumber`." |
| D10 | `ToTitleCase` unused | Missed | The review does not mention `ToTitleCase`. |
| D11 | `JoinWithSeparatorFixed` unused | Partial | The review mentions `JoinWithSeparator` is inefficient and `JoinWithSeparatorFixed` exists, but doesn't explicitly state the fixed version is unused/dead code. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state | Found | "Static mutable state `_auditLog` and `_requestCount` shared across threads." |
| A2 | Regex compiled per-call | Found | "`new Regex` created on every call." |
| A3 | String concatenation in loop | Found | "String concatenation in loop is O(n²)." |
| A4 | Shared mutable `SmtpClient` | Found | "`SmtpClient` is not thread-safe and held as instance field." |
| A5 | Reimplementing BCL (`IsBlank`) | Found | "`IsBlank` reimplements `string.IsNullOrWhiteSpace`." |
| A6 | Leaking connection anti-pattern | Found | "`GetOpenConnection` returns open connection without disposing; caller must manage it." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Found | "Production database credentials and SMTP passwords are hardcoded in config." |
| CF2 | Log level Debug in production | Found | "Debug log level set for all namespaces in production config." |
| CF3 | JWT `ValidateLifetime = false` | Found | "JWT lifetime validation is disabled, allowing tokens to never expire." |
| CF4 | HTTPS disabled | Found | "HTTPS redirection is commented out." |
| CF5 | `UseDeveloperExceptionPage()` unconditional | Found | "`UseDeveloperExceptionPage()` enabled unconditionally." |
| CF6 | Open CORS policy | Found | "CORS allows any origin, method, and header." |
| CF7 | Debug symbols in release | Found | "`DebugSymbols` and `DebugType` set to full in release-like config." |
| CF8 | Outdated `Newtonsoft.Json` | Found | "`Newtonsoft.Json` version 12.0.3 is outdated and vulnerable." |
| CF9 | No `appsettings.Production.json` | Missed | The review does not mention the missing production-specific config file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage | Found | "No test project exists." and "Create unit tests for all services." |