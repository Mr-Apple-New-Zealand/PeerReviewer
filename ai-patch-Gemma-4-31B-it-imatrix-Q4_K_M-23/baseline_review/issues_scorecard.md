# AI Review Scorecard

> **Branch:** `Gemma-4` &nbsp;·&nbsp; **Commit:** `845c0f8`

Total: 56 Found / 2 Partial / 12 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) in `AuthService.Login` | Found | "SQL Injection via string interpolation in `Login` method." |
| C2 | Backdoor / hardcoded admin bypass `AdminBypassPassword` | Found | "Hardcoded admin backdoor password allows bypassing authentication." |
| C3 | Broken password hashing (MD5, no salt) | Partial | "MD5 is cryptographically broken..." (Misses specific mention of missing salt). |
| C4 | SQL Injection (UpdateUser / DeleteUser) | Found | "SQL Injection in `UpdateUser` via string interpolation." and "SQL Injection in `DeleteUser` via string interpolation." |
| C5 | SQL Injection (SearchUsers) | Found | "SQL Injection in `SearchUsers` via `ExecuteQuery` with raw `LIKE` clause." |
| C6 | SQL Injection (Transfer/Deposit) | Found | "SQL Injection in `Transfer` via string interpolation..." and "SQL Injection in `Deposit` via string interpolation..." |
| C7 | SQL Injection (RecordTransaction) | Found | "SQL Injection in `RecordTransaction` via string interpolation." |
| C8 | Hardcoded production credentials in `appsettings.json` | Found | "Production database credentials committed to source control." |
| C9 | JWT lifetime validation disabled | Found | "JWT lifetime validation is disabled (`ValidateLifetime = false`)." |
| C10 | Broken Access Control (PUT /api/user/{id}) | Found | "Missing authorization check allows any authenticated user to update/delete any user." |
| C11 | Missing Authorization (DELETE /api/user/{id}) | Found | "Missing authorization check allows any authenticated user to delete any user." |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows zero-value transfers | Missed | Review mentions balance check and self-transfer, but not the zero-amount validation logic specifically. |
| L2 | Balance check excludes fee | Found | "Balance check uses `amount` but deducts `amount + fee`, allowing negative balances." |
| L3 | Off-by-one in pagination | Found | "Pagination offset calculation is incorrect (`page * pageSize` instead of `(page - 1) * pageSize`)." |
| L4 | Incorrect interest rate (5% vs 1%) | Partial | "Deposit interest calculation multiplies by `1`, making the bonus equal to the full amount instead of 5%." (Identifies wrong rate but misattributes cause to `* 1` rather than the constant `0.05m`). |
| L5 | Self-transfer allowed | Found | "No check prevents users from transferring funds to themselves." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in UserService | Missed | Review does not mention extracting `ValidateUserId` or duplicated ID checks. |
| R2 | Loop string concatenation in `JoinWithSeparator` | Found | "`JoinWithSeparator` is inefficient... String concatenation in loop causes O(n²) performance." |
| R3 | Overly long `GenerateJwtToken` | Missed | Review does not mention refactoring `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows exceptions | Found | "`SearchUsers` swallows all exceptions and returns empty list, hiding errors." |
| E2 | `SendWelcomeEmail` catches broad Exception | Found | "`SendWelcomeEmail` swallows exceptions silently." |
| E3 | No database transaction in Transfer | Found | "Database writes in `Transfer` are not atomic; failure after debit causes data inconsistency." |
| E4 | Email failure propagates after commit | Missed | Review notes atomicity issues but not the specific behavior of email failure post-commit. |
| E5 | `ex.Message` exposed to client | Found | "Raw exception message returned to client in `UpdateUser`." |
| E6 | `ExecuteNonQuery` connection leak on exception | Found | "`ExecuteNonQuery` opens connection but does not dispose command or connection on exception." |
| E7 | No rate limiting on login | Missed | Review does not mention rate limiting or brute force protection. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection`/`SqlDataReader` leak in Login | Found | "`SqlConnection` and `SqlDataReader` in `Login` are never disposed." |
| RL2 | `GetOpenConnection` leak | Found | "`GetOpenConnection` returns open connection without disposing..." |
| RL3 | `ExecuteNonQuery` dispose issue | Found | "`ExecuteNonQuery` opens connection but does not dispose command or connection on exception." |
| RL4 | `SmtpClient` instance field leak | Found | "`SmtpClient` is instantiated once and reused; it is not thread-safe and may leak sockets." |
| RL5 | `MailMessage` not disposed | Found | "`MailMessage` in `SendTransferNotification` is not disposed." and "`MailMessage` in `SendWelcomeEmail` is not disposed." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` null check | Found | "`_config["Jwt:SecretKey"]` may be null, causing `GetBytes` to throw." |
| N2 | `Rows[0]` access without count check | Found | "Accessing `Rows[0]` without checking `Rows.Count` throws if user not found." |
| N3 | `SmtpPort` config fallback/null | Found | "`_config["Email:SmtpPort"]` may be null, causing `int.Parse` to throw." |
| N4 | `username.ToUpper()` null ref | Missed | Review mentions null checks for config, but not specifically `username.ToUpper()` in EmailService. |
| N5 | `email.Length`/`username.Length` null ref | Missed | Review does not mention null guards for string length properties. |
| N6 | `User.FindFirst(...)?.Value` null parse | Found | "`int.Parse` on `userIdClaim` may throw if claim is null or invalid format." |
| N7 | `request == null` check missing | Missed | Review does not mention null model binding checks in controllers. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate`/`MaxTransactionsPerDay` constants | Found | "`TransactionFeeRate` (0.015) is hardcoded..." and "`MaxTransactionsPerDay` (10) is hardcoded..." |
| M2 | `1_000_000` deposit cap hardcoded | Found | "Deposit limit (1000000) is hardcoded..." |
| M3 | Email addresses hardcoded | Missed | Review mentions email subjects and credentials, but not the specific hardcoded email address literals. |
| M4 | Bare literals in StringHelper | Found | "Email length limit (254) is hardcoded..." and "Username length limits (3, 20) are hardcoded..." |
| M5 | Page size `50` unnamed | Found | "Page size limit (50) is hardcoded..." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` unused | Found | "`HashPasswordSha1` is defined but never called." |
| D2 | Unreachable code in `ValidateToken` | Found | "`ValidateToken` always returns `true` due to early return before validation logic." |
| D3 | `TableExists` unused | Missed | Review does not mention `TableExists`. |
| D4 | `ExecuteQueryWithParams` unused | Found | "`ExecuteQueryWithParams` is marked `[Obsolete]` but still present." |
| D5 | `BuildHtmlTemplate` unused | Found | "`BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml`, which is likely unused." |
| D6 | `SendWelcomeEmailHtml` unused | Found | "`BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml`, which is likely unused." (Implies SendWelcomeEmailHtml is unused/dead). |
| D7 | `FormatCurrency` unused | Found | "`FormatCurrency` is defined but never called." |
| D8 | `IsWithinDailyLimit` unused | Missed | Review does not mention `IsWithinDailyLimit`. |
| D9 | `ObfuscateAccount` unused | Found | "`ObfuscateAccount` duplicates functionality of `MaskAccountNumber`." |
| D10 | `ToTitleCase` unused | Found | "`ToTitleCase` duplicates standard library functionality." |
| D11 | `JoinWithSeparatorFixed` unused | Found | "`JoinWithSeparatorFixed` duplicates `string.Join`; likely unused." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state in UserService | Found | "Static mutable state `_auditLog` shared across threads..." and "Static mutable state `_requestCount`..." |
| A2 | Regex compiled per-call | Found | "`new Regex` created on every call; should be static readonly." |
| A3 | String concatenation in loop | Found | "String concatenation in loop causes O(n²) performance." |
| A4 | Shared mutable `SmtpClient` | Found | "`SmtpClient` is not thread-safe; shared instance causes race conditions." |
| A5 | Reimplementing BCL (`IsBlank`) | Found | "`IsBlank` duplicates `string.IsNullOrWhiteSpace`." |
| A6 | Leaking connection anti-pattern | Found | "`GetOpenConnection` returns open connection without disposing..." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Found | "Production connection string committed to source control." |
| CF2 | Log level Debug in production | Found | "Debug log level set for production namespaces." |
| CF3 | JWT `ValidateLifetime = false` | Found | "JWT `ValidateLifetime` set to `false`." |
| CF4 | HTTPS disabled | Found | "HTTPS redirection commented out." |
| CF5 | `UseDeveloperExceptionPage()` unconditional | Found | "`UseDeveloperExceptionPage()` enabled unconditionally." |
| CF6 | Open CORS policy | Found | "CORS allows any origin, method, and header." |
| CF7 | `DebugSymbols` true in release | Found | "`DebugSymbols` enabled in project file; may leak in release." |
| CF8 | Pinned outdated Newtonsoft.Json | Found | "`Newtonsoft.Json` version 12.0.3 is outdated and vulnerable." |
| CF9 | No `appsettings.Production.json` | Missed | Review does not mention missing environment-specific config files. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage | Found | "No test project exists." and lists specific missing tests for Transfer, Deposit, Login, etc. |