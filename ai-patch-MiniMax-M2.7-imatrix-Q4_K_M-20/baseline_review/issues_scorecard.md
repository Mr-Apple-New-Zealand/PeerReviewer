# AI Review Scorecard

> **Branch:** `MiniMax-M2.7` &nbsp;·&nbsp; **Commit:** `717c543`

Total: 55 Found / 2 Partial / 13 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) in `AuthService.Login` | Found | "SQL injection via string interpolation in `Login` method." |
| C2 | Backdoor / hardcoded admin bypass `AdminBypassPassword` | Found | "Hardcoded admin bypass password allows authentication without DB check." |
| C3 | Broken password hashing (MD5, no salt) | Found | "Passwords hashed using MD5, which is cryptographically broken." |
| C4 | SQL Injection (UpdateUser / DeleteUser) in `UserService` | Found | "SQL injection via string interpolation in `UpdateUser` method." and "SQL injection via string interpolation in `DeleteUser` method." |
| C5 | SQL Injection (SearchUsers) in `UserService` | Found | "SQL injection via string interpolation in `SearchUsers` method." |
| C6 | SQL Injection (Transfer/Deposit) in `TransactionService` | Found | "SQL injection via string interpolation in `Transfer` method." and "SQL injection via string interpolation in `Deposit` method." |
| C7 | SQL Injection (RecordTransaction) in `TransactionService` | Found | "SQL injection via string interpolation in `RecordTransaction` method." |
| C8 | Hardcoded production credentials in `appsettings.json` | Found | "Production database credentials committed to source control." |
| C9 | JWT lifetime validation disabled (`ValidateLifetime = false`) | Found | "`ValidateLifetime = false` disables JWT expiration checks." |
| C10 | Broken Access Control on `PUT /api/user/{id}` | Found | "Missing authorization check; any authenticated user can update any user." |
| C11 | Missing Authorization on `DELETE /api/user/{id}` | Found | "Missing authorization check; any authenticated user can delete any user." |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows zero-value transfers | Missed | The review mentions balance checks and fee deduction but does not identify the specific flaw that `amount == 0` is allowed by the `< 0` check. |
| L2 | Balance check excludes the fee | Found | "Balance check uses `amount` but deducts `amount + fee`, allowing negative balances." |
| L3 | Off-by-one in pagination | Found | "Pagination offset calculation `page * pageSize` is off-by-one for 1-based pages." |
| L4 | Incorrect interest rate | Partial | "Deposit interest calculation `amount * 0.05m * 1` is redundant and potentially misleading." (Identifies the code but misses the specific error that 5% is wrong vs 1%). |
| L5 | Self-transfer allowed | Missed | The review does not mention the missing check for `fromUserId != request.ToUserId`. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in `UserService` | Missed | The review does not identify the duplicated `id <= 0 / id > 1_000_000` guard blocks. |
| R2 | Loop string concatenation in `JoinWithSeparator` | Found | "String concatenation in loop (`result += item`)." |
| R3 | Overly long `GenerateJwtToken` | Missed | The review does not suggest splitting `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows all exceptions | Found | "Catch block swallows exception and returns empty list, hiding errors." |
| E2 | `SendWelcomeEmail` catches `Exception` too broadly | Found | "Exception swallowed in `SendWelcomeEmail`, hiding failures." |
| E3 | No database transaction in `Transfer` | Found | "No database transaction for atomic balance updates in `Transfer`." |
| E4 | Email failure propagates exception after commit | Missed | The review notes missing transactions but does not identify the specific issue of exception propagation after DB commit in `Transfer`. |
| E5 | `ex.Message` exposed to client | Found | "Raw exception message returned to client in `UpdateUser`." |
| E6 | `ExecuteNonQuery` closes connection only on happy path | Found | "`ExecuteNonQuery` closes connection but doesn't dispose command/adapter." (Implies the exception path issue). |
| E7 | No rate limiting on login | Missed | The review does not mention missing rate limiting or account lockout. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection`/`SqlDataReader` not disposed in `Login` | Found | "`SqlConnection` and `SqlDataReader` not disposed in `Login`." |
| RL2 | `GetOpenConnection` returns live connection, never disposed | Found | "`GetOpenConnection` returns open connection without disposal contract." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` | Found | "`ExecuteNonQuery` closes connection but doesn't dispose command/adapter." |
| RL4 | `SmtpClient` held as instance field | Found | "`SmtpClient` held as instance field; not thread-safe and may leak sockets." |
| RL5 | `MailMessage` not disposed | Found | "`MailMessage` not disposed in `SendTransferNotification`." and "`MailMessage` not disposed in `SendWelcomeEmail`." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null` | Found | "`_config["Jwt:SecretKey"]` could be null." |
| N2 | `Rows[0]` accessed without checking `Rows.Count` | Found | "`fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` hides missing config | Found | "`_config["Email:SmtpPort"]` could be null, causing `int.Parse` to throw." |
| N4 | `username.ToUpper()` throws if `username` is `null` | Missed | The review does not specifically identify the `username.ToUpper()` null reference risk in `SendWelcomeEmail`. |
| N5 | `email.Length`/`username.Length` throw if argument is `null` | Missed | The review does not identify the null guard missing in `StringHelper` validation methods. |
| N6 | `User.FindFirst(...)?.Value` can be `null` | Found | "`int.Parse` on `userIdClaim` can throw if claim is null or non-integer." |
| N7 | `UpdateUser` doesn't check `request == null` | Missed | The review does not identify the missing null check for the request body in `UpdateUser`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate` and `MaxTransactionsPerDay` hardcoded | Found | "`TransactionFeeRate` (0.015) is hardcoded." and "`MaxTransactionsPerDay` (10) is hardcoded." |
| M2 | `1_000_000` deposit cap hardcoded | Found | "Deposit limit (1000000) is hardcoded." |
| M3 | Email addresses hardcoded | Missed | The review does not identify the hardcoded email addresses `"notifications@company.com"` and `"support@company.com"`. |
| M4 | `254`, `3`, `20` bare literals in `StringHelper` | Found | "Email length limit (254) is hardcoded." and "Username length limits (3, 20) are hardcoded." |
| M5 | `50` page size upper bound unnamed | Found | "Page size limit (50) is hardcoded." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` never called | Found | "`HashPasswordSha1` is defined but never called." |
| D2 | Unreachable code in `ValidateToken` | Found | "`ValidateToken` has unreachable code after `return true`." |
| D3 | `TableExists` never called | Missed | The review does not identify `TableExists` as dead code. |
| D4 | `ExecuteQueryWithParams` never called | Found | "`ExecuteQueryWithParams` is marked `[Obsolete]` but still present." |
| D5 | `BuildHtmlTemplate` never invoked | Found | "`BuildHtmlTemplate` is only called by `SendWelcomeEmailHtml`, which is unused." |
| D6 | `SendWelcomeEmailHtml` never registered/called | Partial | The review notes `BuildHtmlTemplate` is called by `SendWelcomeEmailHtml` which is unused, implying D6, but doesn't explicitly name `SendWelcomeEmailHtml` as the dead public method. |
| D7 | `FormatCurrency` never called | Found | "`FormatCurrency` is defined but never called." |
| D8 | `IsWithinDailyLimit` never called | Missed | The review does not identify `IsWithinDailyLimit` as dead code. |
| D9 | `ObfuscateAccount` never called | Found | "`ObfuscateAccount` duplicates `MaskAccountNumber` logic." |
| D10 | `ToTitleCase` never called | Found | "`ToTitleCase` duplicates standard library functionality." |
| D11 | `JoinWithSeparatorFixed` never used | Found | "`JoinWithSeparatorFixed` duplicates `string.Join`." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state `_auditLog`/`_requestCount` | Found | "`_auditLog` is static mutable state without synchronization." and "`_requestCount` is static mutable state without synchronization." |
| A2 | Regex compiled per-call | Found | "`new Regex` created on every call in `IsValidEmail`." |
| A3 | String concatenation in loop | Found | "String concatenation in loop (`result += item`)." |
| A4 | Shared mutable `SmtpClient` | Found | "`SmtpClient` is not thread-safe; shared instance causes race conditions." |
| A5 | Reimplementing BCL `IsBlank` | Found | "`IsBlank` duplicates `string.IsNullOrWhiteSpace`." |
| A6 | Leaking connection `GetOpenConnection` | Found | "`GetOpenConnection` returns open connection without disposal contract." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Found | "Production database credentials committed to source control." |
| CF2 | Log level `Debug` in production | Found | "Logging level set to `Debug` for all namespaces." |
| CF3 | JWT `ValidateLifetime = false` | Found | "`ValidateLifetime = false` disables JWT expiration checks." |
| CF4 | HTTPS disabled | Found | "`UseHttpsRedirection()` is commented out." |
| CF5 | `UseDeveloperExceptionPage()` unconditional | Found | "`UseDeveloperExceptionPage()` enabled unconditionally." |
| CF6 | Open CORS policy | Found | "CORS policy allows any origin, method, and header." |
| CF7 | `DebugSymbols = true` in release | Found | "`DebugSymbols` and `DebugType` set to full in project file." |
| CF8 | Pinned outdated `Newtonsoft.Json` | Found | "`Newtonsoft.Json` version 12.0.3 is outdated and vulnerable." |
| CF9 | No `appsettings.Production.json` | Missed | The review does not mention the missing environment-specific configuration file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage | Found | "No test project exists." and lists specific areas needing testing like `Transfer`, `Deposit`, `GetUsersPage`, `Login`, `StringHelper`. |