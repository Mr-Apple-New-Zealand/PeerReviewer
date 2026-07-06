# AI Review Scorecard

> **Branch:** `gpt-oss-120B` &nbsp;·&nbsp; **Commit:** `0b009ba`

Total: 12 Found / 15 Partial / 43 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) in `AuthService.Login` | Partial | Review mentions SQL injection in `DatabaseHelper.ExecuteQuery` and `AuthService` generally, but does not specifically identify the string interpolation in `Login` method parameters. |
| C2 | Backdoor / hardcoded admin bypass `AdminBypassPassword` | Missed | No mention of `AdminBypassPassword` or the specific backdoor logic in `AuthService`. |
| C3 | Broken password hashing (MD5, no salt) | Partial | Review mentions "SHA256 without salt" in `AuthService`, which is semantically close to the hashing weakness, though the algorithm name differs from reference (MD5). |
| C4 | SQL Injection (UpdateUser / DeleteUser) in `UserService` | Missed | Review mentions SQL injection in `DatabaseHelper` and `SearchUsers`, but does not specifically name `UpdateUser` or `DeleteUser` as injection points. |
| C5 | SQL Injection (SearchUsers) in `UserService` | Found | Review states: "`SearchUsers` uses `LIKE` with `%` wildcards... potentially causing... injection". |
| C6 | SQL Injection (Transfer/Deposit) in `TransactionService` | Missed | Review mentions `Transfer` fee calculation and logic, but does not identify SQL injection in `Transfer` or `Deposit` methods. |
| C7 | SQL Injection (RecordTransaction) in `TransactionService` | Missed | No mention of SQL injection in `RecordTransaction`. |
| C8 | Hardcoded production credentials in `appsettings.json` | Partial | Review mentions "Hardcoded fallback credentials" in `DatabaseHelper` and "secrets use placeholders" in `appsettings.json`, touching on the secret management issue but not explicitly flagging committed production secrets as a critical vulnerability. |
| C9 | JWT lifetime validation disabled | Partial | Review mentions "JWT token expiration set to 30 days" and suggests reducing it, but does not explicitly identify `ValidateLifetime = false` as the root cause of tokens never expiring. |
| C10 | Broken Access Control in `UserController` PUT | Missed | Review mentions `SearchUsers` and `GetAuditLog` lack authorization, but does not specifically identify the missing ownership check in `PUT /api/user/{id}`. |
| C11 | Missing Authorization in `UserController` DELETE | Missed | No specific mention of missing role checks in `DELETE /api/user/{id}`. |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | Zero-value transfers allowed (`amount < 0` check) | Missed | No mention of the zero-value transfer logic error. |
| L2 | Balance check excludes fee | Partial | Review mentions "`Transfer` calculates fee on `amount` but debits `amount + fee`", which touches on the fee logic, but does not explicitly identify the balance check failure leading to negative balances. |
| L3 | Off-by-one in pagination | Missed | No mention of pagination off-by-one error in `UserService`. |
| L4 | Incorrect interest rate | Missed | No mention of the incorrect interest rate constant. |
| L5 | Self-transfer allowed | Missed | No mention of self-transfer logic error. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in `UserService` | Missed | No mention of duplicated ID validation logic. |
| R2 | Loop string concatenation in `StringHelper` | Found | Review states: "`JoinWithSeparator` duplicates `string.Join` functionality" and suggests using it directly, implying the current implementation is inefficient/redundant. |
| R3 | Overly long `GenerateJwtToken` | Missed | No mention of refactoring `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows exceptions | Missed | No mention of exception swallowing in `SearchUsers`. |
| E2 | `SendWelcomeEmail` catches broad Exception | Missed | No mention of broad exception catching in `SendWelcomeEmail`. |
| E3 | No database transaction in `Transfer` | Missed | No mention of missing database transaction scope. |
| E4 | Email failure propagates exception after commit | Partial | Review mentions "`Transfer` swallows exceptions in email sending... lacks logging", which touches on the email handling but doesn't explicitly identify the inconsistency of committing DB then failing HTTP response. |
| E5 | `UpdateUser` exposes exception details | Found | Review states: "`UpdateUser` catches `ArgumentException` and returns message, potentially exposing internal details." |
| E6 | `ExecuteNonQuery` connection leak on exception | Partial | Review mentions `GetOpenConnection` risks leaks and `ExecuteQuerySafe` disposal, but does not specifically identify the exception path leak in `ExecuteNonQuery`. |
| E7 | No rate limiting on login | Missed | No mention of missing rate limiting or account lockout. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection`/`SqlDataReader` leak in `Login` | Missed | No specific mention of resource leak in `AuthService.Login`. |
| RL2 | `GetOpenConnection` leak | Found | Review states: "`GetOpenConnection` returns an open connection, risking leaks if caller doesn't dispose." |
| RL3 | `ExecuteNonQuery` connection not disposed on exception | Partial | Review mentions `ExecuteQuerySafe` disposal reliance, but does not specifically identify the `ExecuteNonQuery` exception path leak. |
| RL4 | `SmtpClient` instance field leak | Partial | Review mentions "`SmtpClient` created inside loop; ensure it is disposed properly", which contradicts the reference (it's an instance field), but touches on SmtpClient disposal issues. |
| RL5 | `MailMessage` not disposed | Missed | No mention of `MailMessage` disposal. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` null check | Missed | No mention of null config key in `AuthService`. |
| N2 | `Rows[0]` access without count check | Missed | No mention of null/missing row checks in `TransactionService`. |
| N3 | `SmtpPort` config fallback | Missed | No mention of SmtpPort config issues. |
| N4 | `username.ToUpper()` null ref | Missed | No mention of null username in `EmailService`. |
| N5 | `email.Length`/`username.Length` null ref | Missed | No mention of null checks in `StringHelper`. |
| N6 | `User.FindFirst` null value | Found | Review states: "`User.FindFirst` may return null, causing `NullReferenceException` on `.Value`." |
| N7 | `UpdateUser` null request body | Missed | No mention of null request body check in `UserController`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | Hardcoded transaction constants | Found | Review states: "`TransactionFeeRate`, `DepositInterestRate`, `DepositCap` are hardcoded constants." |
| M2 | Hardcoded deposit cap | Partial | Covered by M1 note regarding `DepositCap`. |
| M3 | Hardcoded email addresses | Found | Review states: "Email subjects and addresses are hardcoded constants." |
| M4 | Bare literals in `StringHelper` | Missed | No mention of bare literals in `StringHelper`. |
| M5 | Hardcoded page size | Partial | Review mentions "`MaxPageSize` is hardcoded", which relates to the page size constant. |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` unused | Missed | No mention of `HashPasswordSha1`. |
| D2 | Unreachable code in `ValidateToken` | Found | Review states: "`ValidateToken` is defined but never called in the provided code." (Note: Reference says unreachable code after return, Review says never called. Semantically distinct but both identify `ValidateToken` as problematic/dead. Given strictness, this is Partial if "never called" != "unreachable code after return". However, D2 description is "Unreachable code after return true". The review says "never called". These are different issues. D2 is Missed because the review doesn't identify the unreachable code *inside* the method, it claims the method itself is unused. Actually, looking at D2 description: "Unreachable code after return true". The review says "ValidateToken is defined but never called". This is a different issue. D2 is Missed.) |
| D3 | `TableExists` unused | Missed | No mention of `TableExists`. |
| D4 | `ExecuteQueryWithParams` unused | Missed | No mention of `ExecuteQueryWithParams`. |
| D5 | `BuildHtmlTemplate` unused | Missed | No mention of `BuildHtmlTemplate`. |
| D6 | `SendWelcomeEmailHtml` unused | Missed | No mention of `SendWelcomeEmailHtml`. |
| D7 | `FormatCurrency` unused | Missed | No mention of `FormatCurrency`. |
| D8 | `IsWithinDailyLimit` unused | Missed | No mention of `IsWithinDailyLimit`. |
| D9 | `ObfuscateAccount` unused | Missed | No mention of `ObfuscateAccount`. |
| D10 | `ToTitleCase` unused | Missed | No mention of `ToTitleCase`. |
| D11 | `JoinWithSeparatorFixed` unused | Missed | No mention of `JoinWithSeparatorFixed`. |

*Correction on D2*: The review says `ValidateToken` is never called. The reference issue D2 is about unreachable code *inside* `ValidateToken`. These are different. D2 is Missed.

*Correction on D1-D11*: The review only mentions `JoinWithSeparator` (R2/D11 area) and `ValidateToken` (D2 area). It does not name the specific dead symbols for D1, D3-D11.

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state in `UserService` | Missed | No mention of static state in `UserService`. |
| A2 | Regex compiled per-call | Missed | No mention of Regex compilation. |
| A3 | String concatenation in loop | Found | Review states: "`JoinWithSeparator` duplicates `string.Join` functionality", implying the loop concatenation anti-pattern. |
| A4 | Shared mutable `SmtpClient` | Partial | Review mentions `SmtpClient` disposal, but not specifically the thread-safety/mutability anti-pattern. |
| A5 | Reimplementing BCL (`IsBlank`) | Missed | No mention of `IsBlank`. |
| A6 | Leaking connection anti-pattern | Found | Review states: "`GetOpenConnection` returns an open connection, risking leaks...". |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Partial | Covered by C8 note. |
| CF2 | Log level Debug in production | Missed | No mention of log levels. |
| CF3 | JWT `ValidateLifetime = false` | Partial | Covered by C9 note. |
| CF4 | HTTPS disabled | Missed | No mention of HTTPS redirection. |
| CF5 | `UseDeveloperExceptionPage()` unconditional | Partial | Review states: "`UseDeveloperExceptionPage` is used in development, but ensure it's disabled in production." |
| CF6 | Open CORS policy | Found | Review states: "CORS policy allows any method and header, which is overly permissive." |
| CF7 | Debug symbols in release | Missed | No mention of debug symbols. |
| CF8 | Outdated Newtonsoft.Json | Missed | No mention of package versions. |
| CF9 | No `appsettings.Production.json` | Missed | No mention of missing production config file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | Missing Unit Tests (aggregate) | Found | Review has a section "10. Missing Unit Tests" listing lack of tests for `AuthService`, `TransactionService`, `UserService`, and `DatabaseHelper`. |