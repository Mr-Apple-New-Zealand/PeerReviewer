# AI Review Scorecard

> **Branch:** `Qwen3.5-122B` &nbsp;·&nbsp; **Commit:** `c09505e`

Total: 21 Found / 11 Partial / 38 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) in `AuthService.Login` | Missed | The review mentions SQL injection in `DatabaseHelper` and `ExecuteQuery`, but does not explicitly identify the string interpolation in `AuthService.Login`. |
| C2 | Backdoor / hardcoded admin bypass `AdminBypassPassword` | Missed | The review mentions hardcoded fallback credentials in `DatabaseHelper`, but does not mention the specific `AdminBypassPassword` constant or backdoor logic in `AuthService`. |
| C3 | Broken password hashing (MD5, no salt) | Found | "Passwords hashed using MD5, which is cryptographically broken." and "No salt is used in the MD5 hashing process." |
| C4 | SQL Injection (UpdateUser / DeleteUser) | Missed | The review identifies SQL injection in `DatabaseHelper.ExecuteQuery`, but does not explicitly link it to the vulnerable `UpdateUser` or `DeleteUser` methods in `UserService`. |
| C5 | SQL Injection (SearchUsers) | Missed | The review identifies SQL injection in `DatabaseHelper.ExecuteQuery`, but does not explicitly link it to the `SearchUsers` method in `UserService`. |
| C6 | SQL Injection (Transfer/Deposit) | Missed | The review identifies SQL injection in `DatabaseHelper.ExecuteQuery`, but does not explicitly link it to the `Transfer` or `Deposit` methods in `TransactionService`. |
| C7 | SQL Injection (RecordTransaction) | Missed | The review identifies SQL injection in `DatabaseHelper.ExecuteQuery`, but does not explicitly link it to the `RecordTransaction` method in `TransactionService`. |
| C8 | Hardcoded production credentials in `appsettings.json` | Partial | The review mentions "Connection string placeholders... may fail" and hardcoded fallbacks in `DatabaseHelper`, but does not explicitly flag the committed secrets in `appsettings.json`. |
| C9 | JWT lifetime validation disabled | Missed | The review mentions JWT config validation, but does not specifically identify `ValidateLifetime = false`. |
| C10 | Broken Access Control in `UpdateUser` | Found | "`UpdateUser` allows any authenticated user to update any profile... logic is flawed". |
| C11 | Missing Authorization in `DeleteUser` | Found | "`DeleteUser` allows non-admins to delete users... Enforce strict role-based access control". |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | Zero-value transfers allowed (`amount < 0` check) | Missed | The review discusses fee calculation and race conditions, but does not mention the missing check for zero amounts. |
| L2 | Balance check excludes fee | Found | "`Transfer` calculates fee but does not deduct it from sender in the final balance update logic correctly". |
| L3 | Off-by-one in pagination | Missed | The review mentions pagination metadata, but does not identify the off-by-one error in the offset calculation. |
| L4 | Incorrect interest rate | Partial | The review mentions interest bonus recording, but does not explicitly flag the incorrect rate value (5% vs 1%). |
| L5 | Self-transfer allowed | Missed | The review does not mention the lack of a check for `fromUserId != toUserId`. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in `UserService` | Missed | The review does not mention the duplicated ID validation blocks. |
| R2 | Loop string concatenation in `JoinWithSeparator` | Partial | The review mentions `JoinWithSeparator` duplicates `string.Join`, implying the inefficiency, but doesn't explicitly cite the O(n²) allocation issue. |
| R3 | Overly long `GenerateJwtToken` | Missed | The review does not mention the length or structure of `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows exceptions | Found | "`SearchUsers` catches `Exception` and returns empty list, masking errors." |
| E2 | `SendWelcomeEmail` catches broad Exception | Found | "`SendWelcomeEmail` swallows all exceptions silently." |
| E3 | No database transaction in `Transfer` | Found | "`Transfer` method lacks atomic database transaction wrapper for balance updates." |
| E4 | Email failure propagates after commit | Missed | The review mentions rolling back on exception, but does not specifically identify the issue where email failure throws after DB commit. |
| E5 | `UpdateUser` exposes `ex.Message` | Found | "`UpdateUser` returns `ex.Message` to client in `BadRequest`." |
| E6 | `ExecuteNonQuery` connection leak on exception | Partial | The review mentions `ExecuteQuery` disposal issues, but does not specifically identify the exception path leak in `ExecuteNonQuery`. |
| E7 | No rate limiting on login | Missed | The review does not mention missing rate limiting or account lockout. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection`/`SqlDataReader` leak in `Login` | Found | "`Login` opens connection but does not dispose `SqlDataReader` explicitly". |
| RL2 | `GetOpenConnection` leak | Found | "`GetOpenConnection` returns open connection without disposing, risking leaks". |
| RL3 | `ExecuteNonQuery` dispose/close issue | Partial | The review mentions `ExecuteQuery` disposal, but does not specifically address `ExecuteNonQuery`'s close/dispose inconsistency. |
| RL4 | `SmtpClient` instance field leak | Missed | The review mentions `SmtpClient` thread-safety, but does not identify the instance field leak. |
| RL5 | `MailMessage` not disposed | Partial | The review states "`MailMessage` should be disposed (it is, via `using`)", which contradicts the issue that it is NOT disposed in some paths, or misses the specific leak in `SendTransferNotification`. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` null check | Found | "`jwtSecret` from config is used without null check, passed to `GetBytes`." |
| N2 | `Rows[0]` access without count check | Found | "`fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`". |
| N3 | `SmtpPort` config fallback | Missed | The review does not mention the `SmtpPort` config fallback issue. |
| N4 | `username.ToUpper()` null ref | Missed | The review does not mention the null reference risk in `username.ToUpper()`. |
| N5 | `email.Length`/`username.Length` null ref | Missed | The review does not mention null checks for string length properties. |
| N6 | `User.FindFirst` null parse | Found | "`User.FindFirst(...)?.Value` used, but `int.Parse` called on potentially null result." |
| N7 | `UpdateUser` null request body | Missed | The review does not mention checking for null request bodies in `UpdateUser`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | Hardcoded fee/limit constants | Found | "Fee rate `0.015` and interest rate `0.01` are hardcoded with fallbacks." |
| M2 | Hardcoded deposit cap | Missed | The review does not mention the hardcoded `1_000_000` deposit cap. |
| M3 | Hardcoded email addresses | Partial | The review mentions "Email subjects are hardcoded", but does not explicitly flag the hardcoded email addresses (`notifications@company.com`). |
| M4 | Bare literals in `StringHelper` | Missed | The review does not mention the bare literals (254, 3, 20) in `StringHelper`. |
| M5 | Hardcoded page size bound | Found | "Page size limit `50` is hardcoded." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` unused | Missed | The review does not mention `HashPasswordSha1`. |
| D2 | Unreachable code in `ValidateToken` | Missed | The review does not mention unreachable code in `ValidateToken`. |
| D3 | `TableExists` unused | Missed | The review does not mention `TableExists`. |
| D4 | `ExecuteQueryWithParams` unused | Missed | The review does not mention `ExecuteQueryWithParams`. |
| D5 | `BuildHtmlTemplate` unused | Missed | The review does not mention `BuildHtmlTemplate`. |
| D6 | `SendWelcomeEmailHtml` unused | Missed | The review does not mention `SendWelcomeEmailHtml`. |
| D7 | `FormatCurrency` unused | Missed | The review does not mention `FormatCurrency`. |
| D8 | `IsWithinDailyLimit` unused | Missed | The review does not mention `IsWithinDailyLimit`. |
| D9 | `ObfuscateAccount` unused | Missed | The review does not mention `ObfuscateAccount`. |
| D10 | `ToTitleCase` unused | Missed | The review does not mention `ToTitleCase`. |
| D11 | `JoinWithSeparatorFixed` unused | Partial | The review mentions `JoinWithSeparator` duplicates `string.Join`, implying the fixed version is redundant/unused, but doesn't name `JoinWithSeparatorFixed` specifically. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state in `UserService` | Found | "`_auditLog` and `_requestCount` are mutable static-like state in scoped service." |
| A2 | Regex compiled per-call | Missed | The review does not mention the Regex compilation anti-pattern. |
| A3 | String concatenation in loop | Partial | The review mentions `JoinWithSeparator` duplicates `string.Join`, implying the concatenation issue, but doesn't explicitly cite the O(n²) pattern. |
| A4 | Shared mutable `SmtpClient` | Found | "`SmtpClient` is not thread-safe; creating new instance per call is okay but inefficient." (Identifies the thread-safety issue). |
| A5 | Reimplementing BCL (`IsBlank`) | Found | "`IsBlank` duplicates `string.IsNullOrWhiteSpace`." |
| A6 | Leaking connection anti-pattern | Found | "`GetOpenConnection` returns open connection without disposing, risking leaks". |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Partial | The review mentions hardcoded fallbacks and config placeholders, but does not explicitly flag the secrets in `appsettings.json` as a source control issue. |
| CF2 | Log level Debug in production | Missed | The review does not mention the Debug log level. |
| CF3 | JWT `ValidateLifetime = false` | Missed | The review does not mention `ValidateLifetime = false`. |
| CF4 | HTTPS disabled | Missed | The review does not mention HTTPS redirection being commented out. |
| CF5 | `UseDeveloperExceptionPage()` unconditional | Missed | The review does not mention the developer exception page. |
| CF6 | Open CORS policy | Found | "CORS policy allows `AllowAnyMethod()` and `AllowAnyHeader()`." |
| CF7 | DebugSymbols/DebugType in release | Partial | The review mentions `DebugSymbols` and `DebugType` are disabled, which is the opposite of the issue (they should be disabled in release, but the issue is they are enabled). The review suggests enabling them, which is incorrect for release, but identifies the config line. |
| CF8 | Pinned outdated package | Missed | The review mentions `System.Data.SqlClient` deprecation, but not `Newtonsoft.Json` version. |
| CF9 | No `appsettings.Production.json` | Missed | The review does not mention the missing production config file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | Missing Unit Tests (aggregate) | Found | The review lists multiple missing tests for `Transfer`, `Login`, `Pagination`, `SQL execution`, and `Email sending`. |