# AI Review Scorecard

> **Branch:** `Qwen3-Coder-30B` &nbsp;·&nbsp; **Commit:** `2844476`

Total: 21 Found / 5 Partial / 44 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) in `AuthService.Login` | Missed | The review mentions SQL injection in `DatabaseHelper.ExecuteQuery` and `AuthService` generally, but does not specifically identify the string interpolation in `AuthService.Login` or the `admin'--` bypass vector. |
| C2 | Backdoor / hardcoded admin bypass `AdminBypassPassword` | Missed | The review mentions hardcoded credentials in `DatabaseHelper` but does not identify the specific `AdminBypassPassword` constant or the backdoor logic in `AuthService`. |
| C3 | Broken password hashing (MD5, no salt) | Found | "Passwords hashed using MD5, which is cryptographically broken and unsalted." |
| C4 | SQL Injection (UpdateUser / DeleteUser) | Missed | The review identifies SQL injection in `ExecuteQuery` generally, but does not specifically name `UpdateUser` or `DeleteUser` as vulnerable methods using string interpolation. |
| C5 | SQL Injection (SearchUsers) | Missed | The review mentions `SearchUsers` swallows exceptions, but does not identify the SQL injection vulnerability in the `LIKE` clause construction. |
| C6 | SQL Injection (Transfer/Deposit) | Missed | The review discusses transaction logic and email sending in `Transfer`, but does not identify the SQL injection via string interpolation in the UPDATE statements. |
| C7 | SQL Injection (RecordTransaction) | Missed | The review mentions `RecordTransaction` is called inside a transaction, but does not identify the SQL injection risk from the `description` parameter. |
| C8 | Hardcoded production credentials in `appsettings.json` | Partial | The review notes placeholders `__SET_VIA_ENV__` in `appsettings.json` and hardcoded creds in `DatabaseHelper`, but does not explicitly flag the committed DB/JWT/SMTP secrets in `appsettings.json` as a security issue (it treats them as config placeholders). |
| C9 | JWT lifetime validation disabled | Missed | The review mentions JWT secret validation, but does not identify `ValidateLifetime = false` as a vulnerability. |
| C10 | Broken Access Control (PUT /api/user/{id}) | Missed | The review mentions `UpdateUser` checks `callerId != id` but doesn't check Admin, which is a logic fix, not the missing ownership check described in C10. It does not explicitly state that *any* user can overwrite *any* profile due to missing checks. |
| C11 | Missing Authorization (DELETE /api/user/{id}) | Missed | The review does not mention the `DELETE` endpoint or its lack of role checks. |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | Zero-value transfers allowed (`amount < 0` check) | Missed | The review does not mention the `amount < 0` check allowing zero values. |
| L2 | Balance check excludes fee | Missed | The review discusses transaction rollbacks and email failures, but does not identify the specific logic error where the balance check fails to account for the fee. |
| L3 | Off-by-one in pagination | Missed | The review mentions `GetUsersPage` lacks tests for pagination, but does not identify the off-by-one error in the skip calculation. |
| L4 | Incorrect interest rate (5% vs 1%) | Partial | The review notes the interest calculation is "redundant and potentially confusing" and suggests simplifying, but does not explicitly identify the wrong rate (5% vs 1%) as a logic error. |
| L5 | Self-transfer allowed | Missed | The review does not mention the lack of a check for `fromUserId != toUserId`. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in UserService | Missed | The review mentions `ValidateUserId` rejects IDs arbitrarily, but does not suggest extracting the duplicated guard blocks into a helper. |
| R2 | Loop string concatenation in `JoinWithSeparator` | Found | "`JoinWithSeparator` duplicates `string.Join`." (Implies the inefficiency/duplication). |
| R3 | Overly long `GenerateJwtToken` | Missed | The review does not mention refactoring `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows exceptions | Found | "`SearchUsers` catches all exceptions and returns empty list, hiding errors." |
| E2 | `SendWelcomeEmail` catches broad Exception | Found | "`SendWelcomeEmail` catches `Exception` and prints to console, swallowing errors." |
| E3 | No database transaction around UPDATEs | Partial | The review mentions `ExecuteNonQuery` doesn't accept transaction param and suggests ensuring it does, but doesn't explicitly state the current code lacks a transaction wrapper causing inconsistency. |
| E4 | Email failure propagates after commit | Found | "Email sent inside database transaction; if email fails, transaction rolls back... Move email sending to after `transaction.Commit()`." |
| E5 | `ex.Message` exposed to client | Found | "`UpdateUser` returns `ex.Message` to client, leaking internal details." |
| E6 | `ExecuteNonQuery` connection leak on exception | Found | "`ExecuteQuery` creates `SqlConnection` but doesn't dispose if exception occurs during `Open()`." (Note: Reference says `ExecuteNonQuery`, Review says `ExecuteQuery`, but both are in `DatabaseHelper` and describe the same resource leak pattern on exception). |
| E7 | No rate limiting on login | Missed | The review does not mention rate limiting or brute force protection. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection`/`SqlDataReader` leak in `Login` | Missed | The review mentions `DatabaseHelper` leaks, but not specifically the `Login` method's failure to close/dispose. |
| RL2 | `GetOpenConnection` leak | Found | "`GetOpenConnection` returns open connection; caller must dispose, risking leaks." |
| RL3 | `ExecuteNonQuery` connection not disposed | Found | "`ExecuteQuery` creates `SqlConnection` but doesn't dispose if exception occurs..." (Similar to E6, covers the disposal issue). |
| RL4 | `SmtpClient` instance field leak | Missed | The review mentions `SmtpClient` created per call in `SendTransferNotification`, but the reference issue is about the *instance field* in `EmailService` not being disposed. The review says "created per call", which contradicts the reference's "instance field". |
| RL5 | `MailMessage` not disposed | Missed | The review does not mention `MailMessage` disposal. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` null check | Found | "`_config["Jwt:SecretKey"]` can be null; `GetBytes` throws if null." |
| N2 | `Rows[0]` access without count check | Found | "`fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`..." |
| N3 | `SmtpPort` config fallback issue | Missed | The review mentions `SmtpHost` null check, but not the `SmtpPort` fallback to "25" issue. |
| N4 | `username.ToUpper()` null ref | Missed | The review does not mention `username.ToUpper()` throwing on null. |
| N5 | `email.Length`/`username.Length` null ref | Missed | The review does not mention null guards for string length checks. |
| N6 | `User.FindFirst` null parse | Found | "`User.FindFirst(...)?.Value` can be null; `int.Parse` throws `ArgumentNullException`." |
| N7 | `request == null` check missing | Missed | The review does not mention checking for null request body. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate`/`MaxTransactionsPerDay` hardcoded | Found | "`TransactionFeeRate` (0.015m) hardcoded." and "`MaxTransactionsPerDay` (10) hardcoded." |
| M2 | `1_000_000` deposit cap hardcoded | Found | "`DepositCap` (1,000,000) hardcoded." |
| M3 | Email addresses hardcoded | Partial | The review mentions "Email subjects hardcoded" and "EmailService.cs ... Email subjects", but does not explicitly name the hardcoded *addresses* (`notifications@company.com`). |
| M4 | Bare literals in `StringHelper` | Missed | The review does not mention the bare literals (254, 3, 20) in `StringHelper`. |
| M5 | Page size upper bound unnamed | Missed | The review does not mention the unnamed page size limit. |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` unused | Missed | The review does not mention `HashPasswordSha1`. |
| D2 | Unreachable code in `ValidateToken` | Missed | The review says `ValidateToken` is "never called", which is different from "unreachable code after return". |
| D3 | `TableExists` unused | Missed | The review does not mention `TableExists`. |
| D4 | `ExecuteQueryWithParams` unused | Found | "`ExecuteQueryWithParams` marked `[Obsolete]` but still present." |
| D5 | `BuildHtmlTemplate` unused | Missed | The review does not mention `BuildHtmlTemplate`. |
| D6 | `SendWelcomeEmailHtml` unused | Missed | The review does not mention `SendWelcomeEmailHtml`. |
| D7 | `FormatCurrency` unused | Missed | The review does not mention `FormatCurrency`. |
| D8 | `IsWithinDailyLimit` unused | Missed | The review does not mention `IsWithinDailyLimit`. |
| D9 | `ObfuscateAccount` unused | Missed | The review does not mention `ObfuscateAccount`. |
| D10 | `ToTitleCase` unused | Missed | The review does not mention `ToTitleCase`. |
| D11 | `JoinWithSeparatorFixed` unused | Missed | The review mentions `JoinWithSeparator` duplicates `string.Join`, but does not mention the unused `JoinWithSeparatorFixed`. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state in `UserService` | Found | "`_auditLog` and `_requestCount` are static mutable state; thread-unsafe." |
| A2 | Regex compiled per-call | Found | "`new Regex(...)` created per call; should be static readonly." |
| A3 | String concatenation in loop | Found | "String concatenation in loop for audit report. Use `StringBuilder` or `string.Join`." |
| A4 | Shared mutable `SmtpClient` | Missed | The review says `SmtpClient` is created per call, contradicting the reference's claim it's a shared field. It does not identify the anti-pattern of sharing it. |
| A5 | Reimplementing BCL (`IsBlank`) | Missed | The review does not mention `IsBlank` duplicating `string.IsNullOrWhiteSpace`. |
| A6 | Leaking connection via `GetOpenConnection` | Found | "`GetOpenConnection` returns open connection; caller must dispose, risking leaks." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Partial | The review notes placeholders in `appsettings.json` but doesn't explicitly flag the *presence* of secrets as a source control issue (it assumes they are placeholders). |
| CF2 | Log level Debug in production | Missed | The review does not mention log levels. |
| CF3 | JWT `ValidateLifetime = false` | Missed | The review does not mention `ValidateLifetime`. |
| CF4 | HTTPS disabled | Missed | The review does not mention HTTPS redirection. |
| CF5 | `UseDeveloperExceptionPage()` unconditional | Missed | The review says it's "only in development; good practice", missing the issue that it might be unconditional or misconfigured. |
| CF6 | Open CORS policy | Found | "CORS policy allows any method/header with credentials." |
| CF7 | DebugSymbols/DebugType in release | Missed | The review says "Enable debug symbols for development builds", implying they are currently disabled or misconfigured, but doesn't flag the *release* build issue. |
| CF8 | Outdated Newtonsoft.Json | Missed | The review does not mention package versions. |
| CF9 | No `appsettings.Production.json` | Missed | The review does not mention missing environment-specific config files. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage | Found | "No test project exists. Create test project with unit tests." |