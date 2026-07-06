# AI Review Scorecard

> **Branch:** `Qwen3.5-9B` &nbsp;·&nbsp; **Commit:** `a4284fb`

Total: 39 Found / 8 Partial / 23 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) in `AuthService.Login` | Missed | The review mentions SQL injection in `DatabaseHelper`, `TransactionService`, `UserService`, and `AuthService` generally, but does not specifically identify the `Login` method's string interpolation vulnerability. |
| C2 | Backdoor / hardcoded admin bypass (`AdminBypassPassword`) | Missed | The review mentions hardcoded credentials in `appsettings.json` but does not identify the specific `AdminBypassPassword` constant or backdoor logic in `AuthService`. |
| C3 | Broken password hashing (MD5, no salt) | Partial | The review states "Passwords are hashed using SHA-256 without salt", which incorrectly identifies the algorithm (it is MD5 in the code) but correctly identifies the lack of salt and vulnerability to rainbow tables. |
| C4 | SQL Injection (UpdateUser / DeleteUser) | Found | The review explicitly lists `UpdateUser` and `DeleteUser` in `UserService.cs` as constructing SQL via string interpolation. |
| C5 | SQL Injection (SearchUsers) | Found | The review explicitly lists `SearchUsers` in `UserService.cs` as passing raw query input to `ExecuteQuery`. |
| C6 | SQL Injection (Transfer/Deposit) | Found | The review explicitly lists `TransactionService.cs` line 48 (`ExecuteNonQuery` for UPDATE statements) as enabling SQL injection. |
| C7 | SQL Injection (RecordTransaction) | Found | The review explicitly lists `RecordTransaction` in `TransactionService.cs` as using string interpolation for INSERT statements. |
| C8 | Hardcoded production credentials in `appsettings.json` | Found | The review explicitly states "Production database credentials and SMTP passwords are hardcoded in source control" in `appsettings.json`. |
| C9 | JWT lifetime validation disabled | Found | The review explicitly states "JWT lifetime validation is disabled (`ValidateLifetime = false`)" in `Program.cs`. |
| C10 | Broken Access Control (`PUT /api/user/{id}`) | Found | The review explicitly states `UpdateUser` in `UserController.cs` lacks ownership checks. |
| C11 | Missing Authorization (`DELETE /api/user/{id}`) | Found | The review explicitly states `DeleteUser` in `UserController.cs` lacks ownership checks. |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows zero-value transfers | Missed | The review does not mention the specific boundary condition allowing zero-value transfers in `TransactionService`. |
| L2 | Balance check excludes the fee | Found | The review explicitly states "Balance check compares `fromBalance >= amount` but deducts `amount + fee`" in `TransactionService.cs`. |
| L3 | Off-by-one in pagination | Found | The review explicitly states "Pagination logic uses `page * pageSize` for skip" in `UserService.cs`. |
| L4 | Incorrect interest rate | Partial | The review mentions the interest calculation is "redundant and confusing" and suggests clarifying business logic, but does not explicitly flag the incorrect rate value (5% vs 1%) as a bug. |
| L5 | Self-transfer allowed | Found | The review explicitly states "`Transfer` does not check if `fromUserId` equals `toUserId`" in `TransactionService.cs`. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in `UserService` | Missed | The review does not mention the duplicated ID validation guards in `GetUserById`, `UpdateUser`, and `DeleteUser`. |
| R2 | Loop string concatenation in `JoinWithSeparator` | Partial | The review mentions `JoinWithSeparator` is a duplicate of `JoinWithSeparatorFixed` and `string.Join`, but does not explicitly flag the O(n²) performance issue of the loop concatenation itself as a primary concern, though it is implied by suggesting removal. |
| R3 | Overly long `GenerateJwtToken` | Missed | The review does not mention the length or structure of `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows all exceptions | Found | The review explicitly states "`SearchUsers` catches all exceptions and returns an empty list" in `UserService.cs`. |
| E2 | `SendWelcomeEmail` catches `Exception` too broadly | Found | The review explicitly states "`SendWelcomeEmail` catches exceptions and prints to console, failing silently" in `EmailService.cs`. |
| E3 | No database transaction in `Transfer` | Found | The review explicitly states "Database updates in `Transfer` are not wrapped in a transaction" in `TransactionService.cs`. |
| E4 | Email failure propagates exception after commit | Missed | The review does not mention the specific issue of email failure propagating an exception after the DB transfer has committed. |
| E5 | `catch (Exception ex)` exposes `ex.Message` | Found | The review explicitly states "`UpdateUser` returns `ex.Message` to the client" in `UserController.cs`. |
| E6 | `ExecuteNonQuery` closes connection only on happy path | Partial | The review mentions `ExecuteNonQuery` does not dispose the command/connection, but does not specifically highlight the exception path skipping the close operation as a distinct resource leak logic error. |
| E7 | No rate limiting on failed login attempts | Missed | The review does not mention the lack of rate limiting or account lockout in `AuthController`. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection`/`SqlDataReader` not closed in `Login` | Missed | The review mentions SQL injection in `AuthService` but does not specifically identify the resource leak in the `Login` method. |
| RL2 | `GetOpenConnection` returns live connection, never disposed | Found | The review explicitly states "`GetOpenConnection` returns an open connection without disposing it" in `DatabaseHelper.cs`. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` | Found | The review explicitly states "`ExecuteNonQuery` opens a connection but does not dispose the command" in `DatabaseHelper.cs`. |
| RL4 | `SmtpClient` held as instance field | Partial | The review mentions `SmtpClient` is created inside a loop (which is incorrect, it's a field) and suggests reuse or disposal, but does not clearly identify the thread-safety/socket exhaustion risk of holding it as a non-disposable field. |
| RL5 | `MailMessage` not disposed | Found | The review explicitly states "`MailMessage` is not disposed after sending" in `EmailService.cs`. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null` | Found | The review explicitly states "`_config["Jwt:SecretKey"]` is accessed with `!` operator, risking null reference" in `AuthService.cs`. |
| N2 | `fromUserTable.Rows[0]` accessed without check | Found | The review explicitly states "`fromUserTable.Rows[0]` is accessed without checking `Rows.Count`" in `TransactionService.cs`. |
| N3 | `int.Parse(_config["Email:SmtpPort"])` fallback issues | Found | The review explicitly states "`_config["Email:SmtpPort"]` is parsed without null check" in `EmailService.cs`. |
| N4 | `username.ToUpper()` throws if `username` is `null` | Missed | The review does not mention the null reference risk in `username.ToUpper()` in `EmailService`. |
| N5 | `email.Length`/`username.Length` throw if null | Missed | The review does not mention the null reference risks in `StringHelper` validation methods. |
| N6 | `User.FindFirst(...)?.Value` can be `null` | Missed | The review does not mention the null reference risk in `TransactionController`. |
| N7 | `UpdateUser` doesn't check `request == null` | Missed | The review does not mention the missing null check for the request body in `UserController`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate`/`MaxTransactionsPerDay` hardcoded | Found | The review explicitly lists `TransactionFeeRate` and `MaxTransactionsPerDay` as hardcoded in `TransactionService.cs`. |
| M2 | `1_000_000` deposit cap hardcoded | Found | The review explicitly lists "Deposit limit `1000000` is hardcoded" in `TransactionService.cs`. |
| M3 | Email addresses hardcoded | Found | The review explicitly lists "Sender email `notifications@company.com` is hardcoded" in `EmailService.cs`. |
| M4 | `254`, `3`, `20` bare literals in `StringHelper` | Missed | The review does not mention the bare literals in `StringHelper`. |
| M5 | `50` page size upper bound unnamed | Found | The review explicitly lists "Page size limit `50` is hardcoded" in `UserService.cs`. |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` never called | Missed | The review does not mention `HashPasswordSha1`. |
| D2 | Unreachable code in `ValidateToken` | Missed | The review mentions `ValidateToken` catches exceptions, but does not identify the unreachable code after `return true`. |
| D3 | `TableExists` never called | Partial | The review mentions `TableExists` opens a connection without disposing it, implying it exists, but does not explicitly state it is dead/unused code. |
| D4 | `ExecuteQueryWithParams` never called | Missed | The review does not mention `ExecuteQueryWithParams`. |
| D5 | `BuildHtmlTemplate` never invoked | Missed | The review does not mention `BuildHtmlTemplate`. |
| D6 | `SendWelcomeEmailHtml` never called | Missed | The review does not mention `SendWelcomeEmailHtml`. |
| D7 | `FormatCurrency` never called | Found | The review explicitly states "`FormatCurrency` is defined but never called" in `TransactionService.cs`. |
| D8 | `IsWithinDailyLimit` never called | Found | The review explicitly states "`IsWithinDailyLimit` is defined but never called" in `TransactionService.cs`. |
| D9 | `ObfuscateAccount` never called | Missed | The review does not mention `ObfuscateAccount`. |
| D10 | `ToTitleCase` never called | Missed | The review does not mention `ToTitleCase`. |
| D11 | `JoinWithSeparatorFixed` never used | Found | The review explicitly states "`JoinWithSeparatorFixed` is a duplicate... Remove one of the duplicate methods", implying it is unused/redundant. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state in `UserService` | Found | The review explicitly states "`_auditLog` and `_requestCount` are static mutable state" in `UserService.cs`. |
| A2 | Regex compiled per-call in `StringHelper` | Missed | The review does not mention the Regex compilation issue. |
| A3 | String concatenation in loop in `JoinWithSeparator` | Partial | The review mentions `JoinWithSeparator` is a duplicate and suggests removal, but does not explicitly flag the O(n²) performance anti-pattern as the primary issue. |
| A4 | Shared mutable `SmtpClient` | Partial | The review mentions `SmtpClient` is created inside a loop (incorrectly) and suggests reuse/disposal, but does not clearly identify the thread-safety anti-pattern of holding it as a field. |
| A5 | `IsBlank` duplicates BCL | Found | The review explicitly states "`IsBlank` duplicates `string.IsNullOrWhiteSpace`" in `StringHelper.cs`. |
| A6 | Leaking connection in `GetOpenConnection` | Found | The review explicitly states "`GetOpenConnection` returns an open connection without disposing it" in `DatabaseHelper.cs`. |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Found | The review explicitly states "Production database credentials and SMTP passwords are hardcoded in source control" in `appsettings.json`. |
| CF2 | Log level `Debug` in production | Found | The review explicitly states "Logging level is set to `Debug` for all namespaces" in `appsettings.json`. |
| CF3 | JWT `ValidateLifetime = false` | Found | The review explicitly states "JWT lifetime validation is disabled" in `Program.cs`. |
| CF4 | HTTPS disabled | Found | The review explicitly states "HTTPS redirection is commented out" in `Program.cs`. |
| CF5 | `UseDeveloperExceptionPage()` unconditional | Found | The review explicitly states "`UseDeveloperExceptionPage()` is called unconditionally" in `Program.cs`. |
| CF6 | Open CORS policy | Found | The review explicitly states "CORS policy allows any origin, method, and header" in `Program.cs`. |
| CF7 | `DebugSymbols = true` in release | Missed | The review does not mention the debug symbols setting in the csproj. |
| CF8 | Pinned outdated `Newtonsoft.Json` | Found | The review explicitly states "`Newtonsoft.Json` version `12.0.3` is outdated" in `SampleBankingApp.csproj`. |
| CF9 | No `appsettings.Production.json` | Missed | The review does not mention the missing production-specific configuration file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage | Found | The review explicitly states "No test project exists" and lists specific methods needing tests. |