# AI Review Scorecard

> **Branch:** `Claude-Opus-4.7` &nbsp;·&nbsp; **Commit:** `fc69ad9`

Total: 50 Found / 6 Partial / 14 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) in `AuthService.Login` | Found | "SQL Injection in login query via string interpolation." |
| C2 | Backdoor / hardcoded admin bypass `AdminBypassPassword` | Found | "Hardcoded admin backdoor password bypasses authentication." |
| C3 | Broken password hashing (MD5, no salt) | Partial | "MD5 used for password hashing, which is cryptographically broken." (Misses specific lack of salt detail, but identifies MD5 weakness). |
| C4 | SQL Injection (UpdateUser / DeleteUser) in `UserService` | Found | "SQL Injection in user update via string interpolation." and "SQL Injection in user deletion via string interpolation." |
| C5 | SQL Injection (SearchUsers) in `UserService` | Found | "SQL Injection in user search via string interpolation in `ExecuteQuery`." |
| C6 | SQL Injection (Transfer/Deposit) in `TransactionService` | Found | "SQL Injection in balance update via string interpolation." and "SQL Injection in deposit update via string interpolation." |
| C7 | SQL Injection (RecordTransaction) in `TransactionService` | Found | "SQL Injection in transaction record insertion via string interpolation." |
| C8 | Hardcoded production credentials in `appsettings.json` | Found | "Production database credentials committed to source control." |
| C9 | JWT lifetime validation disabled | Found | "`ValidateLifetime = false` on JWT validation." |
| C10 | Broken Access Control (PUT /api/user/{id}) | Found | "Broken Access Control: Any authenticated user can update/delete any user." |
| C11 | Missing Authorization (DELETE /api/user/{id}) | Partial | "Broken Access Control: Any authenticated user can update/delete any user." (Groups C10 and C11; does not explicitly distinguish the missing role check for DELETE vs ownership for PUT, but covers the general lack of auth checks). |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | Zero-value transfers allowed (`amount < 0` check) | Missed | No mention of zero-value transfer logic or `amount < 0` check flaw. |
| L2 | Balance check excludes fee | Found | "Balance check excludes transaction fee, allowing negative balances." |
| L3 | Off-by-one in pagination | Found | "Pagination offset calculation is incorrect (off-by-one page)." |
| L4 | Incorrect interest rate | Partial | "Deposit interest calculation multiplies by 1, adding no bonus." (Identifies the bug effect but misattributes the cause to `* 1` rather than the wrong rate constant `0.05m` vs `0.01m`). |
| L5 | Self-transfer allowed | Missed | No mention of self-transfer prevention or `fromUserId != request.ToUserId` check. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in `UserService` | Missed | No mention of duplicated ID validation logic. |
| R2 | Loop string concatenation in `JoinWithSeparator` | Found | "String concatenation in loop; O(nÂ²) performance." |
| R3 | Overly long `GenerateJwtToken` | Missed | No mention of refactoring `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows exceptions | Found | "Catches broad `Exception` and returns empty list, hiding errors." |
| E2 | `SendWelcomeEmail` catches broad Exception | Found | "Swallows exception in `SendWelcomeEmail`, failing silently." |
| E3 | No database transaction in Transfer | Found | "Multiple DB writes without transaction, risking partial updates." |
| E4 | Email failure propagates after commit | Missed | No mention of email failure handling post-commit. |
| E5 | Exposes `ex.Message` to client | Found | "Returns raw exception message to client in 500 response." |
| E6 | `ExecuteNonQuery` connection leak on exception | Partial | "`ExecuteNonQuery` opens connection but doesn't dispose command/adapter." (Identifies disposal issue but doesn't explicitly state the exception path skips close). |
| E7 | No rate limiting on login | Missed | No mention of rate limiting or brute force protection. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection`/`SqlDataReader` leak in `Login` | Found | "`SqlConnection` opened but never closed/disposed in `Login`." |
| RL2 | `GetOpenConnection` leak | Found | "`GetOpenConnection` returns open connection; caller must dispose." |
| RL3 | `ExecuteNonQuery` connection leak | Found | "`ExecuteNonQuery` opens connection but doesn't dispose command/adapter." |
| RL4 | `SmtpClient` instance field leak | Found | "`SmtpClient` held as instance field; not thread-safe and leaks sockets." |
| RL5 | `MailMessage` not disposed | Found | "`MailMessage` not disposed after sending." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` null check | Found | "`_config["Jwt:SecretKey"]` used without null check." |
| N2 | `Rows[0]` access without count check | Found | "Accesses `Rows[0]` without checking `Rows.Count > 0`." |
| N3 | `SmtpPort` config fallback | Missed | No mention of SMTP port config fallback issues. |
| N4 | `username.ToUpper()` null ref | Missed | No mention of `username` null check in email service. |
| N5 | `email.Length`/`username.Length` null ref | Missed | No mention of null checks on string length properties. |
| N6 | `User.FindFirst` null parse | Found | "`int.Parse` on potentially null claim value." |
| N7 | `request == null` check missing | Missed | No mention of null request body checks. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate`/`MaxTransactionsPerDay` constants | Missed | No mention of these specific constants needing config. |
| M2 | `1_000_000` deposit cap hardcoded | Found | "Magic number `1000000` for deposit limit." |
| M3 | Email addresses hardcoded | Found | "Magic string `"notifications@company.com"` repeated." |
| M4 | Bare literals in `StringHelper` | Found | "Magic number `254` for email length." and "Magic numbers `3` and `20` for username length." |
| M5 | Page size `50` unnamed | Found | "Magic number `50` for page size limit." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` unused | Found | "`HashPasswordSha1` is unused." |
| D2 | Unreachable code in `ValidateToken` | Partial | "`ValidateToken` is unused." (Identifies the method as unused, which implies the code is dead, but doesn't explicitly mention the unreachable code after return). |
| D3 | `TableExists` unused | Missed | No mention of `TableExists`. |
| D4 | `ExecuteQueryWithParams` unused | Found | "`ExecuteQueryWithParams` is marked obsolete and unused." |
| D5 | `BuildHtmlTemplate` unused | Found | "`BuildHtmlTemplate` is unused." |
| D6 | `SendWelcomeEmailHtml` unused | Found | "`SendWelcomeEmailHtml` is unused." |
| D7 | `FormatCurrency` unused | Found | "`FormatCurrency` is unused." |
| D8 | `IsWithinDailyLimit` unused | Missed | No mention of `IsWithinDailyLimit`. |
| D9 | `ObfuscateAccount` unused | Found | "`ObfuscateAccount` is unused." |
| D10 | `ToTitleCase` unused | Found | "`ToTitleCase` is unused." |
| D11 | `JoinWithSeparatorFixed` unused | Found | "`JoinWithSeparatorFixed` is unused; duplicate of `string.Join`." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state in `UserService` | Found | "Static mutable state `_auditLog` and `_requestCount` shared across instances." |
| A2 | Regex compiled per-call | Found | "`new Regex` created on every call; should be static readonly." |
| A3 | String concatenation in loop | Found | "String concatenation in loop; O(nÂ²) performance." |
| A4 | Shared mutable `SmtpClient` | Found | "`SmtpClient` as instance field; not thread-safe." |
| A5 | Reimplementing BCL (`IsBlank`) | Partial | "`IsBlank` is unused." (Identifies it as dead code, but doesn't explicitly critique it as reimplementing `string.IsNullOrWhiteSpace`). |
| A6 | Leaking connection anti-pattern | Found | "`GetOpenConnection` returns open connection; caller must dispose." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Found | "Production database credentials committed to source control." |
| CF2 | Log level `Debug` in production | Found | "Debug log level set for all namespaces in production." |
| CF3 | JWT `ValidateLifetime = false` | Found | "`ValidateLifetime = false` on JWT validation." |
| CF4 | HTTPS disabled | Found | "HTTPS redirection commented out." |
| CF5 | `UseDeveloperExceptionPage()` unconditional | Found | "`UseDeveloperExceptionPage()` enabled unconditionally." |
| CF6 | Open CORS policy | Found | "Overly permissive CORS policy (`AllowAnyOrigin`)." |
| CF7 | `DebugSymbols`/`DebugType` in release | Found | "`DebugSymbols` and `DebugType` set for release builds." |
| CF8 | Pinned outdated `Newtonsoft.Json` | Found | "`Newtonsoft.Json` version 12.0.3 is outdated and vulnerable." |
| CF9 | No `appsettings.Production.json` | Missed | No mention of missing environment-specific config files. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage | Found | "No test project exists." and lists specific services needing tests. |