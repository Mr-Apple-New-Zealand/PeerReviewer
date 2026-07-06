# AI Review Scorecard

> **Branch:** `Qwen3-Coder-30B` &nbsp;·&nbsp; **Commit:** `2844476`

Total: 51 Found / 4 Partial / 15 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) in `AuthService.Login` | Found | "SQL Injection via string interpolation in `Login` method." |
| C2 | Backdoor / hardcoded admin bypass `AdminBypassPassword` | Found | "Hardcoded admin backdoor password allows bypassing authentication." |
| C3 | Broken password hashing (MD5, no salt) | Found | "Weak cryptography: Passwords hashed using MD5 without salt." |
| C4 | SQL Injection (UpdateUser / DeleteUser) | Found | "SQL Injection in `UpdateUser`... SQL Injection in `DeleteUser`..." |
| C5 | SQL Injection (SearchUsers) | Found | "SQL Injection in `SearchUsers` via string interpolation in `ExecuteQuery`." |
| C6 | SQL Injection (Transfer/Deposit) | Found | "SQL Injection in `Transfer`... SQL Injection in `Deposit`..." |
| C7 | SQL Injection (RecordTransaction) | Found | "SQL Injection in `RecordTransaction` via string interpolation for `INSERT` statement." |
| C8 | Hardcoded production credentials in `appsettings.json` | Found | "Production database credentials committed to source control." |
| C9 | JWT lifetime validation disabled | Found | "JWT lifetime validation disabled (`ValidateLifetime = false`)." |
| C10 | Broken Access Control (`PUT /api/user/{id}`) | Found | "Broken Access Control: `UpdateUser` allows any authenticated user to update any user's data." |
| C11 | Missing Authorization (`DELETE /api/user/{id}`) | Found | "Broken Access Control: `DeleteUser` allows any authenticated user to delete any user." |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows zero-value transfers | Missed | The review mentions balance checks and fees but does not identify the specific flaw allowing zero-value transfers (`amount == 0`). |
| L2 | Balance check excludes fee | Found | "Balance check excludes transaction fee, allowing negative balances." |
| L3 | Off-by-one in pagination | Found | "Pagination offset calculation is incorrect (`page * pageSize`)." |
| L4 | Incorrect interest rate (5% vs 1%) | Partial | "Interest bonus calculation uses magic number `1` and unclear logic." (Mentions the location and magic number but fails to identify the specific incorrect rate value of 0.05m vs 0.01m). |
| L5 | Self-transfer allowed | Missed | The review identifies access control issues in Transfer but does not mention the missing check for `fromUserId != ToUserId` (self-transfer). |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in UserService | Missed | The review does not mention the duplicated ID validation guards in `GetUserById`, `UpdateUser`, and `DeleteUser`. |
| R2 | Loop string concatenation in `JoinWithSeparator` | Found | "String concatenation in loop (`result += item + separator`)." |
| R3 | Overly long `GenerateJwtToken` | Missed | The review does not suggest refactoring `GenerateJwtToken` into smaller helpers. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows exceptions | Found | "`SearchUsers` catches broad `Exception` and returns empty list, hiding errors." |
| E2 | `SendWelcomeEmail` catches broad Exception | Found | "`SendWelcomeEmail` swallows exception silently, hiding failures." |
| E3 | No database transaction in Transfer | Found | "`Transfer` lacks database transaction for atomic balance updates." |
| E4 | Email failure propagates exception after commit | Missed | The review notes the lack of DB transactions but does not identify the specific issue of email failure causing error responses after successful DB commits. |
| E5 | `ex.Message` exposed to client | Found | "Raw exception message returned to client in `UpdateUser`." |
| E6 | `ExecuteNonQuery` connection leak on exception | Found | "`ExecuteNonQuery` opens connection but may leak on exception." |
| E7 | No rate limiting on login | Missed | The review does not mention the lack of rate limiting or account lockout on failed login attempts. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection`/`SqlDataReader` leak in Login | Found | "`SqlConnection` opened but never closed/disposed in `Login`." |
| RL2 | `GetOpenConnection` leak in `ExecuteQuery` | Found | "`ExecuteQuery` opens connection but never closes/disposes it." |
| RL3 | `ExecuteNonQuery` connection leak | Found | "`ExecuteNonQuery` opens connection but may leak on exception." |
| RL4 | `SmtpClient` instance field leak | Found | "`SmtpClient` held as instance field, not thread-safe, and never disposed." |
| RL5 | `MailMessage` not disposed | Found | "`MailMessage` created but never disposed in `SendTransferNotification`... `SendWelcomeEmail`..." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` null check | Found | "`jwtSecret` may be null, causing `Encoding.UTF8.GetBytes` to fail." |
| N2 | `Rows[0]` access without count check | Found | "`fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`." |
| N3 | `SmtpPort` config fallback issue | Partial | "`_config["Email:SmtpPort"]` may be null, causing `int.Parse` to fail." (Identifies the null risk but misses the specific concern about the fallback value "25" being incorrect for TLS). |
| N4 | `username.ToUpper()` null ref | Missed | The review does not mention the `NullReferenceException` risk in `username.ToUpper()` in `EmailService`. |
| N5 | `email.Length`/`username.Length` null ref | Missed | The review does not mention the null guard missing before `Length` access in `StringHelper`. |
| N6 | `User.FindFirst` null parse | Found | "`int.Parse` on `userIdClaim` may throw if claim is null or non-integer." |
| N7 | `request == null` check missing | Missed | The review does not mention the missing null check for the request body in `UpdateUser`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate`/`MaxTransactionsPerDay` constants | Missed | The review does not identify these specific constants as magic numbers that should be in configuration. |
| M2 | `1_000_000` deposit cap hardcoded | Found | "Magic number `1000000` for deposit limit." |
| M3 | Email addresses hardcoded | Found | "Magic string `"notifications@company.com"`... Magic string `"support@company.com"`..." |
| M4 | `254`, `3`, `20` bare literals | Found | "Magic number `254` for email length... Magic numbers `3` and `20` for username length." |
| M5 | `50` page size unnamed | Found | "Magic number `50` for page size limit." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` unused | Found | "`HashPasswordSha1` is defined but never called." |
| D2 | Unreachable code in `ValidateToken` | Found | "`ValidateToken` always returns `true` due to early return." |
| D3 | `TableExists` unused | Missed | The review does not mention `TableExists` as unused dead code. |
| D4 | `ExecuteQueryWithParams` unused | Found | "`ExecuteQueryWithParams` is marked `[Obsolete]` but still present." |
| D5 | `BuildHtmlTemplate` unused | Partial | "`BuildHtmlTemplate` is only called by `SendWelcomeEmailHtml`." (Identifies it as low-value/duplicate but doesn't explicitly state it's dead/unused in the context of the main flow, though it is technically unused by the primary public methods). |
| D6 | `SendWelcomeEmailHtml` unused | Missed | The review does not explicitly identify `SendWelcomeEmailHtml` as unused dead code. |
| D7 | `FormatCurrency` unused | Found | "`FormatCurrency` is defined but never called." |
| D8 | `IsWithinDailyLimit` unused | Missed | The review does not mention `IsWithinDailyLimit` as unused dead code. |
| D9 | `ObfuscateAccount` unused | Found | "`ObfuscateAccount` duplicates `MaskAccountNumber` functionality." |
| D10 | `ToTitleCase` unused | Missed | The review does not mention `ToTitleCase` as unused dead code. |
| D11 | `JoinWithSeparatorFixed` unused | Partial | "`JoinWithSeparatorFixed` duplicates `string.Join` functionality." (Identifies redundancy but doesn't explicitly state the fixed version is unused/dead code in the same way as others). |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state in UserService | Found | "Shared mutable static state `_auditLog`... `_requestCount` accessed without synchronization." |
| A2 | Regex compiled per-call | Found | "`new Regex(...)` created on every call in `IsValidEmail`... `IsValidUsername`." |
| A3 | String concatenation in loop | Found | "String concatenation in loop (`result += item + separator`)." |
| A4 | Shared mutable `SmtpClient` | Found | "`SmtpClient` held as instance field, not thread-safe..." |
| A5 | `IsBlank` reimplements BCL | Found | "`IsBlank` duplicates `string.IsNullOrWhiteSpace`." |
| A6 | Leaking connection anti-pattern | Found | "`GetOpenConnection` returns open connection without disposal contract." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Found | "Production connection string committed to source control." |
| CF2 | Log level Debug in production | Found | "Debug log levels set for production namespaces." |
| CF3 | JWT `ValidateLifetime = false` | Found | "`ValidateLifetime = false` on JWT configuration." |
| CF4 | HTTPS disabled | Found | "HTTPS redirection commented out." |
| CF5 | `UseDeveloperExceptionPage()` unconditional | Found | "`UseDeveloperExceptionPage()` called unconditionally." |
| CF6 | Open CORS policy | Found | "Overly permissive CORS policy (`AllowAnyOrigin`)." |
| CF7 | `DebugSymbols`/`DebugType` in release | Found | "`DebugSymbols` and `DebugType` set in production-ready project." |
| CF8 | Pinned outdated `Newtonsoft.Json` | Found | "`Newtonsoft.Json` version `12.0.3` is outdated and vulnerable." |
| CF9 | No `appsettings.Production.json` | Missed | The review does not mention the missing environment-specific configuration file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage | Found | "No test project exists... Create test project for critical services." |