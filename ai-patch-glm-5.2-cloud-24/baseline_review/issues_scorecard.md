# AI Review Scorecard

> **Branch:** `glm5.2` &nbsp;·&nbsp; **Commit:** `e1c7590`

Total: 53 Found / 4 Partial / 13 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) in `AuthService.Login` | Found | "SQL Injection in login query via string interpolation." |
| C2 | Backdoor / hardcoded admin bypass `AdminBypassPassword` | Found | "Hardcoded admin backdoor password allows bypassing authentication." |
| C3 | Broken password hashing (MD5, no salt) | Partial | "MD5 used for password hashing, which is cryptographically broken." (Misses specific mention of missing salt) |
| C4 | SQL Injection (UpdateUser / DeleteUser) in `UserService` | Found | "SQL Injection in user update via string interpolation." and "SQL Injection in user deletion via string interpolation." |
| C5 | SQL Injection (SearchUsers) in `UserService` | Found | "SQL Injection in user search via string interpolation." |
| C6 | SQL Injection (Transfer/Deposit) in `TransactionService` | Found | "SQL Injection in balance update via string interpolation." and "SQL Injection in deposit update via string interpolation." |
| C7 | SQL Injection (RecordTransaction) in `TransactionService` | Found | "SQL Injection in transaction recording via string interpolation." |
| C8 | Hardcoded production credentials in `appsettings.json` | Found | "Production database credentials committed to source control." |
| C9 | JWT lifetime validation disabled | Found | "JWT lifetime validation disabled (`ValidateLifetime = false`)." |
| C10 | Broken Access Control (PUT /api/user/{id}) | Found | "Missing ownership check allows updating any user's data." |
| C11 | Missing Authorization (DELETE /api/user/{id}) | Found | "Missing ownership check allows deleting any user." |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows zero-value transfers | Missed | The review mentions balance checks and fees but does not identify the specific `amount < 0` vs `amount <= 0` logic error allowing zero transfers. |
| L2 | Balance check excludes the fee | Found | "Balance check uses `amount` but deducts `amount + fee`, causing overdraft." |
| L3 | Off-by-one in pagination | Found | "Pagination skip calculation uses `page * pageSize` instead of `(page - 1) * pageSize`." |
| L4 | Incorrect interest rate (5% vs 1%) | Partial | "Deposit interest calculation multiplies by `1`, making the bonus equal to the principal." (Identifies logic error but mischaracterizes the specific rate/value issue described in ref) |
| L5 | Self-transfer allowed | Missed | The review mentions "Missing ownership check" for transfers (C10/C11 context) but does not explicitly flag the lack of `fromUserId != toUserId` check for self-transfers as a distinct logic error. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in `UserService` | Missed | The review does not mention extracting duplicated ID validation logic. |
| R2 | Loop string concatenation in `StringHelper.JoinWithSeparator` | Found | "String concatenation in loop causes O(n²) performance." |
| R3 | Overly long `GenerateJwtToken` | Missed | The review does not suggest refactoring `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows all exceptions | Found | "`SearchUsers` catches all exceptions and returns empty list, hiding errors." |
| E2 | `SendWelcomeEmail` catches broad `Exception` | Found | "`SendWelcomeEmail` swallows exceptions, failing silently." |
| E3 | No database transaction around updates | Found | "Database updates for transfer are not wrapped in a transaction." |
| E4 | Email failure propagates after commit | Missed | The review notes missing transactions but does not specifically flag the exception propagation timing issue in `Transfer`. |
| E5 | `catch (Exception ex)` exposes message | Found | "Raw exception message returned to client in `UpdateUser`." |
| E6 | `ExecuteNonQuery` connection close on happy path only | Partial | "`ExecuteNonQuery` opens connection but does not dispose command." (Identifies disposal issue but misses the specific "close only on happy path" nuance) |
| E7 | No rate limiting on login | Missed | The review does not mention missing rate limiting or account lockout. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection`/`SqlDataReader` not disposed in `Login` | Found | "`SqlConnection` opened in `Login` is never closed or disposed." |
| RL2 | `GetOpenConnection` returns live connection, never disposed | Found | "`GetOpenConnection` returns open connection; caller must dispose." |
| RL3 | `ExecuteNonQuery` closes but does not dispose | Found | "`ExecuteNonQuery` opens connection but does not dispose command." |
| RL4 | `SmtpClient` held as instance field | Found | "`SmtpClient` is not thread-safe and held as instance field." |
| RL5 | `MailMessage` not disposed | Found | "`MailMessage` is not disposed after sending." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can be null | Found | "`jwtSecret` may be null, causing `GetBytes` to throw." |
| N2 | `Rows[0]` accessed without count check | Found | "Accesses `Rows[0]` without checking `Rows.Count > 0`." |
| N3 | `int.Parse` on config with fallback | Found | "`_config["Email:SmtpPort"]` may be null, causing `int.Parse` to throw." |
| N4 | `username.ToUpper()` throws if null | Missed | The review mentions null checks for length but not specifically `ToUpper()` on username. |
| N5 | `email.Length`/`username.Length` throw if null | Found | "`email.Length` throws if `email` is null." and "`username.Length` throws if `username` is null." |
| N6 | `User.FindFirst(...)?.Value` null parse | Found | "`int.Parse` on claim value may throw if claim is missing or non-integer." |
| N7 | `UpdateUser` doesn't check `request == null` | Missed | The review does not mention null model binding checks for `UpdateUser`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate`/`MaxTransactionsPerDay` hardcoded | Found | "`TransactionFeeRate` is hardcoded; should be configurable." |
| M2 | `1_000_000` deposit cap hardcoded | Found | "Deposit limit `1000000` is hardcoded." |
| M3 | Email addresses hardcoded | Found | "Email subjects are hardcoded strings." (Note: Ref says addresses, review says subjects, but both are hardcoded strings in EmailService) |
| M4 | Bare literals in `StringHelper` | Found | "Email length limit `254` is hardcoded." and "Username length limits `3` and `20` are hardcoded." |
| M5 | Page size upper bound `50` unnamed | Found | "Page size limit `50` is hardcoded." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` unused | Found | "`HashPasswordSha1` is defined but never called." |
| D2 | Unreachable code in `ValidateToken` | Found | "`ValidateToken` logic after `return true` is unreachable." |
| D3 | `TableExists` never called | Missed | The review does not mention `TableExists`. |
| D4 | `ExecuteQueryWithParams` obsolete/unused | Found | "`ExecuteQueryWithParams` is marked `[Obsolete]` but still present." |
| D5 | `BuildHtmlTemplate` never invoked | Partial | "`BuildHtmlTemplate` is private and only used once; consider inlining." (Ref says never invoked, review says used once) |
| D6 | `SendWelcomeEmailHtml` never called | Missed | The review does not mention `SendWelcomeEmailHtml`. |
| D7 | `FormatCurrency` never called | Found | "`FormatCurrency` is defined but never called." |
| D8 | `IsWithinDailyLimit` never called | Missed | The review does not mention `IsWithinDailyLimit`. |
| D9 | `ObfuscateAccount` never called | Missed | The review does not mention `ObfuscateAccount`. |
| D10 | `ToTitleCase` never called | Found | "`ToTitleCase` duplicates standard library functionality." |
| D11 | `JoinWithSeparatorFixed` never used | Found | "`JoinWithSeparatorFixed` duplicates `string.Join`." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state in `UserService` | Found | "`_auditLog` is static mutable state, not thread-safe." |
| A2 | Regex compiled per-call | Found | "`new Regex` created on every call; should be static readonly." |
| A3 | String concatenation in loop | Found | "String concatenation in loop causes O(n²) performance." |
| A4 | Shared mutable `SmtpClient` | Found | "`SmtpClient` is not thread-safe; shared instance causes issues." |
| A5 | Reimplementing BCL (`IsBlank`) | Found | "`IsBlank` duplicates `string.IsNullOrWhiteSpace`." |
| A6 | Leaking connection anti-pattern | Found | "`GetOpenConnection` returns open connection; caller must dispose." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Found | "Production database credentials committed to source control." |
| CF2 | Log level `Debug` in production | Found | "Debug log level set for production namespaces." |
| CF3 | JWT `ValidateLifetime = false` | Found | "`ValidateLifetime = false` disables token expiration." |
| CF4 | HTTPS disabled | Found | "HTTPS redirection commented out." |
| CF5 | `UseDeveloperExceptionPage()` unconditional | Found | "`UseDeveloperExceptionPage()` enabled unconditionally." |
| CF6 | Open CORS policy | Found | "CORS allows any origin, method, and header." |
| CF7 | `DebugSymbols`/`DebugType` in release | Found | "`DebugSymbols` and `DebugType` set to full in release-like config." |
| CF8 | Pinned outdated `Newtonsoft.Json` | Found | "`Newtonsoft.Json` version 12.0.3 is outdated and vulnerable." |
| CF9 | No `appsettings.Production.json` | Missed | The review does not mention the missing production-specific config file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage | Found | "No test project exists." and lists specific areas needing testing. |