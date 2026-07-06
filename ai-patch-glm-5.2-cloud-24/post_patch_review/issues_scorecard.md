# AI Review Scorecard

> **Branch:** `glm5.2` &nbsp;·&nbsp; **Commit:** `e1c7590`

Total: 5 Found / 21 Partial / 44 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) in `AuthService.Login` | Missed | The review mentions `AuthService.cs` line 23 returning user objects, but does not identify the SQL injection in the login query construction. |
| C2 | Backdoor / hardcoded admin bypass `AdminBypassPassword` | Missed | No mention of the specific backdoor constant or logic. |
| C3 | Broken password hashing (MD5, no salt) | Partial | Review mentions "unsalted SHA-256" (incorrect algorithm) and suggests BCrypt, but misses the specific MD5/no-salt issue described. |
| C4 | SQL Injection (UpdateUser / DeleteUser) | Missed | No mention of SQL injection in `UserService` update/delete methods. |
| C5 | SQL Injection (SearchUsers) | Partial | Review mentions `SearchUsers` uses `LIKE` with wildcards and notes it is vulnerable if not parameterized, but the reference states it *is* interpolated (injection exists). The review is ambiguous/partial on the severity. |
| C6 | SQL Injection (Transfer/Deposit) | Missed | No mention of SQL injection in `TransactionService` transfer/deposit methods. |
| C7 | SQL Injection (RecordTransaction) | Missed | No mention of SQL injection in `RecordTransaction`. |
| C8 | Hardcoded production credentials in `appsettings.json` | Partial | Review mentions "Hardcoded fallback database credentials in source code" in `DatabaseHelper.cs`, which is related but distinct from the `appsettings.json` secrets issue. |
| C9 | JWT lifetime validation disabled | Missed | No mention of `ValidateLifetime = false`. |
| C10 | Broken Access Control (PUT /api/user/{id}) | Missed | Review mentions `UpdateUser` lacks audit logging, but not the missing ownership check. |
| C11 | Missing Authorization (DELETE /api/user/{id}) | Missed | No mention of missing role check on delete. |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows zero-value transfers | Missed | No mention of zero-value transfer logic error. |
| L2 | Balance check excludes the fee | Partial | Review mentions `Transfer` checks balance before deducting fee and race conditions, but does not explicitly state the fee is excluded from the balance check logic. |
| L3 | Off-by-one in pagination | Missed | No mention of pagination off-by-one error. |
| L4 | Incorrect interest rate | Partial | Review mentions `Deposit` adds interest bonus but records only base amount, which is related to the interest logic but not the specific rate error. |
| L5 | Self-transfer allowed | Missed | No mention of self-transfer logic error. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in `UserService` | Missed | No mention of duplicated validation blocks. |
| R2 | Loop string concatenation in `StringHelper` | Partial | Review mentions `JoinWithSeparator` duplicates `string.Join`, which implies the inefficiency, but doesn't explicitly call out the O(n²) concatenation anti-pattern. |
| R3 | Overly long `GenerateJwtToken` | Missed | No mention of `GenerateJwtToken` complexity. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows all exceptions | Missed | No mention of exception swallowing in `SearchUsers`. |
| E2 | `SendWelcomeEmail` catches `Exception` too broadly | Missed | No mention of broad exception catching in `SendWelcomeEmail`. |
| E3 | No database transaction around UPDATEs | Partial | Review mentions `Transfer` swallows email exceptions and manual transaction management, but not the lack of DB transaction for the updates themselves. |
| E4 | Email failure propagates exception after commit | Partial | Review mentions `Transfer` swallows email notification exceptions, which is the opposite of the issue (it says it swallows, reference says it propagates). |
| E5 | `catch (Exception ex)` exposes `ex.Message` | Partial | Review mentions `UpdateUser` catches `Exception` and returns generic error, which is related to error handling but not the specific leakage of `ex.Message`. |
| E6 | `ExecuteNonQuery` closes connection only on happy path | Partial | Review mentions `SqlConnection` not disposed if exception occurs in `DatabaseHelper`, which is related to resource leak/error handling. |
| E7 | No rate limiting on failed login attempts | Missed | No mention of rate limiting or brute force protection. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection`/`SqlDataReader` not closed in `Login` | Partial | Review mentions `SqlConnection` not disposed in `TransactionService`, but not specifically in `AuthService.Login`. |
| RL2 | `GetOpenConnection()` returns live connection, never disposed | Partial | Review mentions `SqlConnection` not explicitly closed in `DatabaseHelper`, which is related. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` | Partial | Review mentions `SqlConnection` not disposed in `DatabaseHelper`, which is related. |
| RL4 | `SmtpClient` held as instance field | Partial | Review mentions `SmtpClient` created but not disposed if `Send` throws, which is related to disposal but not the field lifetime issue. |
| RL5 | `MailMessage` not disposed | Missed | No mention of `MailMessage` disposal. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null` | Missed | No mention of null config key. |
| N2 | `fromUserTable.Rows[0]` accessed without check | Found | Review mentions `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` hides missing config | Missed | No mention of null config fallback for SMTP port. |
| N4 | `username.ToUpper()` throws if `username` is `null` | Missed | No mention of null username in email service. |
| N5 | `email.Length`/`username.Length` throw if null | Missed | No mention of null checks in `StringHelper`. |
| N6 | `User.FindFirst(...)?.Value` can be `null` | Missed | No mention of null claim value. |
| N7 | `UpdateUser` doesn't check `request == null` | Missed | No mention of null request body. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate`/`MaxTransactionsPerDay` hardcoded | Found | Review mentions `TransactionFeeRate`, `MaxTransactionsPerDay` are hardcoded constants. |
| M2 | `1_000_000` deposit cap hardcoded | Missed | No mention of the specific deposit cap constant. |
| M3 | Email addresses hardcoded | Found | Review mentions `TransferSubject`, `WelcomeSubject` are hardcoded strings, but not the email addresses themselves. |
| M4 | `254`, `3`, `20` bare literals | Missed | No mention of bare literals in `StringHelper`. |
| M5 | `50` page size upper bound unnamed | Missed | No mention of page size constant. |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` never called | Missed | No mention of `HashPasswordSha1`. |
| D2 | Unreachable code after `return true` in `ValidateToken` | Missed | No mention of unreachable code in `ValidateToken`. |
| D3 | `TableExists` never called | Missed | No mention of `TableExists`. |
| D4 | `ExecuteQueryWithParams` never called | Missed | No mention of `ExecuteQueryWithParams`. |
| D5 | `BuildHtmlTemplate` never invoked | Missed | No mention of `BuildHtmlTemplate`. |
| D6 | `SendWelcomeEmailHtml` never called | Missed | No mention of `SendWelcomeEmailHtml`. |
| D7 | `FormatCurrency` never called | Missed | No mention of `FormatCurrency`. |
| D8 | `IsWithinDailyLimit` never called | Missed | No mention of `IsWithinDailyLimit`. |
| D9 | `ObfuscateAccount` never called | Missed | No mention of `ObfuscateAccount`. |
| D10 | `ToTitleCase` never called | Missed | No mention of `ToTitleCase`. |
| D11 | `JoinWithSeparatorFixed` never used | Partial | Review mentions `JoinWithSeparator` duplicates `string.Join`, implying the fixed version is redundant, but doesn't explicitly name `JoinWithSeparatorFixed` as dead code. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state `_auditLog`/`_requestCount` | Partial | Review mentions `_auditLog` and `_requestCount` are instance fields but not used effectively, which is related but not the static state issue. |
| A2 | Regex compiled per-call | Missed | No mention of regex compilation. |
| A3 | String concatenation in loop | Partial | Review mentions `JoinWithSeparator` duplicates `string.Join`, which implies the concatenation issue. |
| A4 | Shared mutable `SmtpClient` | Partial | Review mentions `SmtpClient` created but not disposed, which is related to the shared mutable issue. |
| A5 | Reimplementing BCL `IsBlank` | Missed | No mention of `IsBlank` duplicating `string.IsNullOrWhiteSpace`. |
| A6 | Leaking connection `GetOpenConnection()` | Partial | Review mentions raw SQL queries with parameters are error-prone, which is related to the connection leak anti-pattern. |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Partial | Review mentions "Hardcoded fallback database credentials in source code", which is related to secrets in source control. |
| CF2 | Log level `Debug` in production | Missed | No mention of debug log level. |
| CF3 | JWT `ValidateLifetime = false` | Missed | No mention of JWT lifetime validation. |
| CF4 | HTTPS disabled | Missed | No mention of HTTPS redirection. |
| CF5 | `UseDeveloperExceptionPage()` called unconditionally | Partial | Review mentions `UseDeveloperExceptionPage()` is used in development, but ensure it's not enabled in production, which is related. |
| CF6 | Open CORS policy | Found | Review mentions CORS policy allows any method and header, which is overly permissive. |
| CF7 | `DebugSymbols = true` / `DebugType = full` | Missed | No mention of debug symbols in release builds. |
| CF8 | Pinned outdated package `Newtonsoft.Json` | Missed | No mention of outdated packages. |
| CF9 | No `appsettings.Production.json` | Missed | No mention of missing production config file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | Missing Unit Tests (aggregate) | Found | Review lists multiple methods lacking unit tests, including `Login`, `Transfer`, `GetUserById`, `SendTransferNotification`, and `ExecuteQuerySafe`. |