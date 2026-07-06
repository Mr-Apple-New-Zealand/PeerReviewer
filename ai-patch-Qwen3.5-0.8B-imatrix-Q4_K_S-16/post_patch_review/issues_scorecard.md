# AI Review Scorecard

> **Branch:** `Qwen3.5-0.8B` &nbsp;·&nbsp; **Commit:** `4c8e082`

Total: 46 Found / 5 Partial / 19 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) in `AuthService.Login` | Found | "SQL Injection via string interpolation in `Login` method." |
| C2 | Backdoor / hardcoded admin bypass `AdminBypassPassword` | Found | "Hardcoded admin backdoor password allows bypassing authentication." |
| C3 | Broken password hashing (MD5, no salt) | Partial | "Passwords hashed using MD5, which is cryptographically broken." (Misses specific mention of missing salt) |
| C4 | SQL Injection (UpdateUser / DeleteUser) | Found | "SQL Injection in `UpdateUser` method... SQL Injection in `DeleteUser` method..." |
| C5 | SQL Injection (SearchUsers) | Found | "SQL Injection in `SearchUsers` method via string interpolation in `ExecuteQuery`." |
| C6 | SQL Injection (Transfer/Deposit) | Found | "SQL Injection in `Transfer` method... SQL Injection in `Deposit` method..." |
| C7 | SQL Injection (RecordTransaction) | Found | "SQL Injection in `RecordTransaction` method via string interpolation for INSERT statement." |
| C8 | Hardcoded production credentials in `appsettings.json` | Found | "Production database credentials hardcoded in source control." |
| C9 | JWT lifetime validation disabled | Missed | Review mentions JWT secret strength but does not mention `ValidateLifetime = false` or token expiry issues. |
| C10 | Broken Access Control (PUT /api/user/{id}) | Missed | Review does not mention missing ownership checks on user updates. |
| C11 | Missing Authorization (DELETE /api/user/{id}) | Missed | Review does not mention missing role checks on user deletion. |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows zero-value transfers | Missed | Review does not mention the zero-amount transfer logic error. |
| L2 | Balance check excludes the fee | Found | "Balance check `fromBalance >= amount` ignores the transaction fee, allowing negative balances." |
| L3 | Off-by-one in pagination | Found | "Pagination offset calculation `page * pageSize` is off-by-one for 1-based indexing." |
| L4 | Incorrect interest rate (5% vs 1%) | Partial | "Deposit interest bonus calculation `amount * 0.05m * 1` is redundant and potentially confusing." (Identifies the value but frames it as redundancy/confusion rather than incorrect business logic/interest rate error) |
| L5 | Self-transfer allowed | Missed | Review does not mention the lack of self-transfer prevention. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in UserService | Missed | Review does not mention extracting duplicated ID validation logic. |
| R2 | Loop string concatenation in `JoinWithSeparator` | Found | "String concatenation in loop is O(n²); use `StringBuilder` or `string.Join`." (Referencing `Helpers/StringHelper.cs`) |
| R3 | Overly long `GenerateJwtToken` | Missed | Review does not mention refactoring `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows all exceptions | Found | "`SearchUsers` catches all exceptions and returns empty list, hiding errors." |
| E2 | `SendWelcomeEmail` catches too broad `Exception` | Found | "`SendWelcomeEmail` swallows exceptions, failing silently." |
| E3 | No database transaction around UPDATEs | Missed | Review does not mention the lack of DB transactions for balance updates. |
| E4 | Email failure propagates after commit | Missed | Review does not mention the exception propagation issue after successful transfer. |
| E5 | `catch (Exception ex)` exposes `ex.Message` | Found | "Raw exception message returned to client in `UpdateUser` catch block." |
| E6 | `ExecuteNonQuery` closes connection only on happy path | Partial | "`ExecuteQuerySafe` opens connection but `SqlDataAdapter.Fill` may not close it on error." (Identifies resource leak on error, which is related, but doesn't explicitly name the missing `finally`/`using` pattern for `ExecuteNonQuery` specifically as described in E6, though RL3 covers similar ground. Given RL3 is separate, this is Partial for E6's specific description of the close logic). |
| E7 | No rate limiting on login | Missed | Review does not mention missing rate limiting or account lockout. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection`/`SqlDataReader` not disposed in `Login` | Found | "`SqlConnection` opened in `Login` but never closed or disposed... `SqlDataReader` created but never closed or disposed." |
| RL2 | `GetOpenConnection` returns live connection, never disposed | Found | "`GetOpenConnection` returns open connection, shifting disposal responsibility to caller." |
| RL3 | `ExecuteNonQuery` closes but doesn't `Dispose`/exception path | Found | "`ExecuteQuerySafe` opens connection but `SqlDataAdapter.Fill` may not close it on error." (Note: Review maps this to `ExecuteQuerySafe`/`DatabaseHelper`, covering the disposal/close issue on error paths). |
| RL4 | `SmtpClient` held as instance field | Found | "`SmtpClient` stored as instance field; not thread-safe and may leak sockets." |
| RL5 | `MailMessage` not disposed | Found | "`MailMessage` not disposed after sending." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can be null | Found | "`jwtSecret` may be null, causing `GetBytes` to throw." |
| N2 | `fromUserTable.Rows[0]` / `toUserTable.Rows[0]` no count check | Found | "`fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`... `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` hides missing config | Missed | Review does not mention the specific risk of the fallback port or missing config key in EmailService. |
| N4 | `username.ToUpper()` throws if null | Missed | Review does not mention `username.ToUpper()` null reference in EmailService. |
| N5 | `email.Length` / `username.Length` throw if null | Found | "`email.Length` called without null check in `IsValidEmail`... `username.Length` called without null check in `IsValidUsername`." |
| N6 | `User.FindFirst(...)?.Value` can be null | Found | "`userIdClaim` may be null, causing `int.Parse` to throw." (Referencing `Controllers/TransactionController.cs`) |
| N7 | `UpdateUser` doesn't check `request == null` | Missed | Review does not mention missing null check for request body in UserController. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate` / `MaxTransactionsPerDay` hardcoded | Found | "`TransactionFeeRate` is hardcoded... `MaxTransactionsPerDay` is hardcoded..." |
| M2 | `1_000_000` deposit cap hardcoded | Found | "Deposit limit `1000000` is hardcoded..." |
| M3 | Email addresses hardcoded | Partial | "Email subjects are hardcoded..." (Review mentions subjects, but misses the specific email address literals like `"notifications@company.com"`). |
| M4 | `254`, `3`, `20` bare literals | Found | "Email length limit `254` is hardcoded... Username length limits `3` and `20` are hardcoded..." |
| M5 | `50` page size unnamed | Found | "Page size limit `50` is hardcoded..." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` unused | Found | "`HashPasswordSha1` method is never called." |
| D2 | Unreachable code in `ValidateToken` | Partial | "`ValidateToken` method is never called." (Review claims the whole method is unused, which implies the unreachable code is dead, but doesn't specifically identify the *unreachable code after return* as the issue, rather the method itself. This is a semantic mismatch: D2 is about unreachable code *inside* a called method, Review says method is unused. If method is unused, D2 is moot. However, if the method IS called (which it might be in other contexts not shown), the unreachable code is the bug. Given the review says "never called", it misses the specific "unreachable code" nuance if the method were called. But since it says "never called", it effectively flags the dead code. I will mark Partial because it doesn't identify the *unreachable code* specifically, just the method usage). |
| D3 | `TableExists` unused | Missed | Review does not mention `TableExists`. |
| D4 | `ExecuteQueryWithParams` unused | Missed | Review does not mention `ExecuteQueryWithParams`. |
| D5 | `BuildHtmlTemplate` unused | Found | "`BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml`, which is likely unused." |
| D6 | `SendWelcomeEmailHtml` unused | Found | "`SendWelcomeEmailHtml` is likely unused." |
| D7 | `FormatCurrency` unused | Found | "`FormatCurrency` method is never called." |
| D8 | `IsWithinDailyLimit` unused | Missed | Review does not mention `IsWithinDailyLimit`. |
| D9 | `ObfuscateAccount` unused | Found | "`ObfuscateAccount` duplicates `MaskAccountNumber` logic; likely unused." |
| D10 | `ToTitleCase` unused | Found | "`ToTitleCase` is likely unused." |
| D11 | `JoinWithSeparatorFixed` unused | Found | "`JoinWithSeparatorFixed` duplicates `string.Join`; likely unused." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state `_auditLog` / `_requestCount` | Found | "Static mutable state `_auditLog` and `_requestCount` are not thread-safe." |
| A2 | Regex compiled per-call | Found | "`new Regex` created on every call; should be static readonly." |
| A3 | String concatenation in loop | Found | "String concatenation in loop is O(n²); use `StringBuilder` or `string.Join`." |
| A4 | Shared mutable `SmtpClient` | Found | "`SmtpClient` is not thread-safe; shared instance causes race conditions." |
| A5 | Reimplementing BCL (`IsBlank`) | Found | "`IsBlank` duplicates `string.IsNullOrWhiteSpace`; likely unused." (Identifies duplication/reimplementation). |
| A6 | Leaking connection `GetOpenConnection` | Found | "`GetOpenConnection` leaks resource ownership to caller." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Found | "Production connection string includes credentials." |
| CF2 | Log level `Debug` in production | Found | "Logging level set to `Debug` for all namespaces." |
| CF3 | JWT `ValidateLifetime = false` | Missed | Review mentions JWT secret validation but not `ValidateLifetime`. |
| CF4 | HTTPS disabled | Found | "HTTPS redirection is commented out." |
| CF5 | `UseDeveloperExceptionPage()` unconditional | Found | "`UseDeveloperExceptionPage()` enabled unconditionally." |
| CF6 | Open CORS policy | Found | "CORS policy allows any origin, method, and header." |
| CF7 | `DebugSymbols = true` in release | Missed | Review does not mention DebugSymbols/DebugType in csproj. |
| CF8 | Pinned outdated `Newtonsoft.Json` | Found | "`Newtonsoft.Json` version 12.0.3 is outdated and vulnerable." |
| CF9 | No `appsettings.Production.json` | Missed | Review does not mention missing environment-specific config files. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage for key areas | Found | "No tests for login logic... No tests for transfer logic... No tests for deposit logic... No tests for user CRUD operations... No tests for pagination logic... No tests for search functionality... No tests for string validation helpers... No integration tests for login endpoint... No integration tests for transfer and deposit endpoints... No integration tests for user CRUD endpoints." |