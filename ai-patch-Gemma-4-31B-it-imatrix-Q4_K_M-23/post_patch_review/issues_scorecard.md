# AI Review Scorecard

> **Branch:** `Gemma-4` &nbsp;·&nbsp; **Commit:** `845c0f8`

Total: 8 Found / 12 Partial / 50 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) in `AuthService.Login` | Missed | The review mentions password hashing and token validation but does not identify the SQL injection in the login query construction. |
| C2 | Backdoor / hardcoded admin bypass `AdminBypassPassword` | Missed | The review does not mention the hardcoded backdoor password constant. |
| C3 | Broken password hashing (MD5, no salt) | Partial | The review states "Passwords are hashed with unsalted SHA-256", identifying the lack of salt and weak hashing, though it misidentifies the algorithm as SHA-256 instead of MD5. |
| C4 | SQL Injection (UpdateUser / DeleteUser) | Missed | The review mentions uniqueness checks for UpdateUser but does not identify the SQL injection in the UPDATE/DELETE statements. |
| C5 | SQL Injection (SearchUsers) | Missed | The review mentions authorization for SearchUsers but does not identify the SQL injection in the LIKE clause. |
| C6 | SQL Injection (Transfer/Deposit) | Missed | The review discusses race conditions and balance checks but does not identify the SQL injection in the UPDATE statements. |
| C7 | SQL Injection (RecordTransaction) | Missed | The review does not identify the SQL injection in the RecordTransaction description parameter. |
| C8 | Hardcoded production credentials in `appsettings.json` | Partial | The review notes "Connection string and secrets are placeholders... ensure they are not committed", touching on the risk but not explicitly flagging the existing hardcoded secrets as a current vulnerability. |
| C9 | JWT lifetime validation disabled | Missed | The review mentions JWT validation generally but does not specifically flag `ValidateLifetime = false`. |
| C10 | Broken Access Control (PUT /api/user/{id}) | Missed | The review mentions authorization for `GetUser` and `SearchUsers` but does not identify the missing ownership check in `UpdateUser`. |
| C11 | Missing Authorization (DELETE /api/user/{id}) | Missed | The review does not identify the missing role check for the delete endpoint. |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | Zero-value transfers allowed (`amount < 0` check) | Partial | The review mentions "Transfer allows negative amounts if `amount <= 0` check is bypassed", touching on the amount validation logic but not explicitly identifying the zero-value bypass. |
| L2 | Balance check excludes fee | Missed | The review discusses stale data and race conditions but does not identify the specific logic error where the fee is excluded from the balance check. |
| L3 | Off-by-one in pagination | Missed | The review mentions indexing for pagination performance but does not identify the off-by-one error in the skip calculation. |
| L4 | Incorrect interest rate | Partial | The review states "Deposit adds interest bonus (`amount * 0.01m`) but does not record the bonus amount", identifying the interest logic but not the incorrect rate value (0.05m vs 0.01m). |
| L5 | Self-transfer allowed | Missed | The review does not identify the missing check for `fromUserId != toUserId`. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in UserService | Missed | The review does not identify the duplicated ID validation blocks. |
| R2 | Loop string concatenation in `JoinWithSeparator` | Partial | The review states "`JoinWithSeparator` duplicates `string.Join` functionality", suggesting removal, which addresses the inefficiency but not explicitly the O(n²) concatenation issue. |
| R3 | Overly long `GenerateJwtToken` | Missed | The review does not identify the lack of helper methods in `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows exceptions | Missed | The review does not identify the exception swallowing in `SearchUsers`. |
| E2 | `SendWelcomeEmail` catches broad Exception | Partial | The review states "`SendWelcomeEmail` catches `SmtpException` and prints to console", identifying the poor error handling but misidentifying the exception type caught. |
| E3 | No database transaction in Transfer | Partial | The review mentions "Balance is read, then updated in a separate transaction without row-level locking", identifying the transactional integrity issue. |
| E4 | Email failure propagates after commit | Missed | The review does not identify the specific issue of email failure propagating after DB commit. |
| E5 | `UpdateUser` exposes `ex.Message` | Found | The review states "`UpdateUser` catches `ArgumentException` and returns `ex.Message`, potentially leaking internal details." |
| E6 | `ExecuteNonQuery` connection leak on exception | Missed | The review mentions `GetOpenConnection` disposal but not the specific exception path leak in `ExecuteNonQuery`. |
| E7 | No rate limiting on login | Missed | The review does not identify the lack of rate limiting or account lockout. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection`/`SqlDataReader` leak in `Login` | Missed | The review does not identify the resource leak in the `Login` method. |
| RL2 | `GetOpenConnection` leak | Found | The review states "`GetOpenConnection` returns an open `SqlConnection` without ensuring disposal." |
| RL3 | `ExecuteNonQuery` connection not disposed | Partial | The review mentions `GetOpenConnection` disposal issues, which covers the general pattern, but does not specifically address the `ExecuteNonQuery` disposal failure. |
| RL4 | `SmtpClient` instance field leak | Missed | The review states "`SmtpClient` is created per send operation", which contradicts the issue (it is an instance field), thus missing the leak. |
| RL5 | `MailMessage` not disposed | Missed | The review does not identify the `MailMessage` disposal issue. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` null check | Missed | The review does not identify the null reference risk in JWT secret retrieval. |
| N2 | `Rows[0]` access without count check | Partial | The review states "`row["Id"]` cast to `int` will throw if the database column is null", identifying the null/DBNull risk in row access. |
| N3 | `SmtpPort` config fallback | Missed | The review does not identify the config fallback issue. |
| N4 | `username.ToUpper()` null ref | Missed | The review does not identify the null reference in `username.ToUpper()`. |
| N5 | `email.Length`/`username.Length` null ref | Missed | The review does not identify the null reference in StringHelper validation. |
| N6 | `User.FindFirst` null ref | Missed | The review does not identify the null reference in `int.Parse`. |
| N7 | `request == null` check missing | Partial | The review states "`request.Username` and `request.Password` are used without null checks", touching on the null safety of the request object. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate`/`MaxTransactionsPerDay` constants | Missed | The review does not identify these specific magic numbers. |
| M2 | `1_000_000` deposit cap | Missed | The review does not identify this specific magic number. |
| M3 | Hardcoded email addresses | Found | The review states "Email subjects and addresses are hardcoded." |
| M4 | Bare literals in StringHelper | Missed | The review does not identify the bare literals in StringHelper. |
| M5 | `50` page size bound | Found | The review states "`MaxPageSize` (50) is hardcoded." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` unused | Missed | The review does not identify `HashPasswordSha1` as dead code. |
| D2 | Unreachable code in `ValidateToken` | Missed | The review states "`ValidateToken` is defined but never called", which is incorrect (it is called) and misses the unreachable code after return. |
| D3 | `TableExists` unused | Missed | The review does not identify `TableExists` as dead code. |
| D4 | `ExecuteQueryWithParams` unused | Missed | The review does not identify `ExecuteQueryWithParams` as dead code. |
| D5 | `BuildHtmlTemplate` unused | Missed | The review does not identify `BuildHtmlTemplate` as dead code. |
| D6 | `SendWelcomeEmailHtml` unused | Missed | The review does not identify `SendWelcomeEmailHtml` as dead code. |
| D7 | `FormatCurrency` unused | Missed | The review does not identify `FormatCurrency` as dead code. |
| D8 | `IsWithinDailyLimit` unused | Missed | The review does not identify `IsWithinDailyLimit` as dead code. |
| D9 | `ObfuscateAccount` unused | Missed | The review does not identify `ObfuscateAccount` as dead code. |
| D10 | `ToTitleCase` unused | Missed | The review does not identify `ToTitleCase` as dead code. |
| D11 | `JoinWithSeparatorFixed` unused | Missed | The review identifies `JoinWithSeparator` as duplicate functionality but does not identify `JoinWithSeparatorFixed` as unused dead code. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state `_auditLog` | Found | The review states "`_auditLog` is a static `ConcurrentBag`, leading to unbounded memory growth." |
| A2 | Regex compiled per-call | Missed | The review does not identify the Regex compilation anti-pattern. |
| A3 | String concatenation in loop | Partial | The review suggests removing `JoinWithSeparator` and using `string.Join`, addressing the anti-pattern. |
| A4 | Shared mutable `SmtpClient` | Missed | The review states `SmtpClient` is created per send, which is incorrect, thus missing the anti-pattern. |
| A5 | Reimplementing BCL `IsBlank` | Missed | The review does not identify `IsBlank` as a BCL reimplement. |
| A6 | Leaking connection `GetOpenConnection` | Found | The review states "`GetOpenConnection` returns an open `SqlConnection` without ensuring disposal." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Partial | The review notes "ensure they are not committed with real values", touching on the risk but not explicitly flagging the current state. |
| CF2 | Log level Debug in production | Missed | The review does not identify the debug log level issue. |
| CF3 | JWT `ValidateLifetime = false` | Missed | The review does not identify this specific configuration issue. |
| CF4 | HTTPS disabled | Missed | The review does not identify the disabled HTTPS redirection. |
| CF5 | `UseDeveloperExceptionPage()` unconditional | Missed | The review states it is "only enabled in development", which is incorrect, thus missing the issue. |
| CF6 | Open CORS policy | Found | The review states "CORS policy allows `AllowAnyMethod()` and `AllowAnyHeader()`, increasing attack surface." |
| CF7 | DebugSymbols true in release | Missed | The review states `DebugSymbols` are disabled, which is incorrect, thus missing the issue. |
| CF8 | Pinned outdated Newtonsoft.Json | Missed | The review does not identify the outdated package. |
| CF9 | No `appsettings.Production.json` | Missed | The review does not identify the missing production config file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage | Found | The review states "No test project exists" and lists specific services needing tests. |