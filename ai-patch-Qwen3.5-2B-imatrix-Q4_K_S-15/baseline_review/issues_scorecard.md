# AI Review Scorecard

> **Branch:** `Qwen3.5-2B` &nbsp;·&nbsp; **Commit:** `1b232c6`

Total: 54 Found / 4 Partial / 12 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) in `AuthService.Login` | Found | "SQL Injection via string interpolation in `Login` method." |
| C2 | Backdoor / hardcoded admin bypass (`AdminBypassPassword`) | Found | "Hardcoded admin backdoor password allows bypassing authentication." |
| C3 | Broken password hashing (MD5, no salt) | Partial | "Passwords hashed using MD5, which is cryptographically broken." (Misses specific mention of missing salt). |
| C4 | SQL Injection (UpdateUser / DeleteUser) | Found | "SQL Injection in `UpdateUser` via string interpolation..." and "SQL Injection in `DeleteUser` via string interpolation..." |
| C5 | SQL Injection (SearchUsers) | Found | "SQL Injection in `SearchUsers` via string interpolation in `ExecuteQuery`." |
| C6 | SQL Injection (Transfer/Deposit) | Found | "SQL Injection in `Transfer` via string interpolation..." and "SQL Injection in `Deposit` via string interpolation..." |
| C7 | SQL Injection (RecordTransaction) | Found | "SQL Injection in `RecordTransaction` via string interpolation..." |
| C8 | Hardcoded production credentials in `appsettings.json` | Found | "Production database credentials committed to source control." |
| C9 | JWT lifetime validation disabled | Found | "JWT `ValidateLifetime` is set to `false`." |
| C10 | Broken Access Control (PUT /api/user/{id}) | Found | "Missing authorization check; any authenticated user can update any user." |
| C11 | Missing Authorization (DELETE /api/user/{id}) | Found | "Missing authorization check; any authenticated user can delete any user." |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` allows zero-value transfers | Missed | The review mentions balance checks and self-transfers but does not identify the specific flaw allowing `amount == 0` due to `< 0` check. |
| L2 | Balance check excludes fee | Found | "Balance check uses `amount` but deducts `amount + fee`, allowing negative balances." |
| L3 | Off-by-one in pagination | Found | "Pagination offset calculation `page * pageSize` skips the first page of results." |
| L4 | Incorrect interest rate (5% vs 1%) | Partial | "Deposit interest calculation `0.05m * 1` is redundant and potentially misleading." (Identifies the value but frames it as redundancy/misleading rather than explicitly stating it is the wrong rate compared to intent). |
| L5 | Self-transfer allowed | Found | "No check to prevent transferring funds to oneself." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in UserService | Missed | The review does not mention extracting the duplicated ID validation logic. |
| R2 | Loop string concatenation in `JoinWithSeparator` | Found | "String concatenation in loop is O(n²)." |
| R3 | Overly long `GenerateJwtToken` | Missed | The review does not suggest refactoring `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows exceptions | Found | "`SearchUsers` catches all exceptions and returns empty list, hiding errors." |
| E2 | `SendWelcomeEmail` catches broad Exception | Found | "`SendWelcomeEmail` swallows exceptions, failing silently." |
| E3 | No database transaction in Transfer | Found | "Database updates in `Transfer` are not atomic..." |
| E4 | Email failure propagates after commit | Missed | The review notes atomicity issues but does not specifically flag that email failure throws after DB commit. |
| E5 | `ex.Message` leaked to client | Found | "`UpdateUser` returns raw exception message to client, leaking internal details." |
| E6 | `ExecuteNonQuery` connection leak on exception | Found | "`ExecuteNonQuery` opens connection but does not dispose command or handle exceptions properly." |
| E7 | No rate limiting on login | Partial | "Logging failed login attempts with username can aid enumeration attacks." (Identifies enumeration risk but doesn't explicitly call out missing rate limiting/lockout as the primary fix). |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection`/`SqlDataReader` leak in Login | Found | "`SqlConnection` and `SqlDataReader` in `Login` are not disposed." |
| RL2 | `GetOpenConnection` leak | Found | "`GetOpenConnection` returns an open connection without disposing it..." |
| RL3 | `ExecuteNonQuery` dispose/close issue | Found | "`ExecuteNonQuery` opens connection but does not dispose command or handle exceptions properly." |
| RL4 | `SmtpClient` instance field leak | Found | "`SmtpClient` is not thread-safe and shared across requests..." |
| RL5 | `MailMessage` not disposed | Found | "`MailMessage` objects are not disposed after sending." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` null check | Missed | The review does not mention null checks for config keys in `AuthService`. |
| N2 | `Rows[0]` access without count check | Found | "Accessing `fromUserTable.Rows[0]` without checking if rows exist." |
| N3 | `SmtpPort` config fallback/null | Missed | The review does not mention null/fallback issues with `SmtpPort`. |
| N4 | `username.ToUpper()` null ref | Missed | The review mentions null checks for `email.Length` and `username.Length` in StringHelper, but not specifically `username.ToUpper()` in EmailService. |
| N5 | `email.Length`/`username.Length` null ref | Found | "`email.Length` can throw if `email` is null." and "`username.Length` can throw if `username` is null." |
| N6 | `User.FindFirst` null parse | Found | "`int.Parse` on `userIdClaim` can throw if claim is null or invalid." |
| N7 | `request == null` check missing | Missed | The review does not mention null checks for controller request bodies. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate`/`MaxTransactionsPerDay` constants | Found | "`TransactionFeeRate` is a magic number." and "`MaxTransactionsPerDay` is a magic number." |
| M2 | `1_000_000` deposit cap hardcoded | Found | "Deposit limit `1000000` is a magic number." |
| M3 | Hardcoded email addresses | Partial | "Email subjects are hardcoded strings." (Mentions subjects, but reference specifies addresses `notifications@company.com` etc. as the issue). |
| M4 | Bare literals in StringHelper | Found | "Email length limit `254` is a magic number." and "Username length limits `3` and `20` are magic numbers." |
| M5 | Page size `50` unnamed | Found | "Page size limit `50` is a magic number." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` unused | Found | "`HashPasswordSha1` is defined but never called." |
| D2 | Unreachable code in `ValidateToken` | Found | "`ValidateToken` always returns `true` due to early return before validation logic." |
| D3 | `TableExists` unused | Missed | The review does not mention `TableExists`. |
| D4 | `ExecuteQueryWithParams` unused | Found | "`ExecuteQueryWithParams` is marked obsolete but still present." |
| D5 | `BuildHtmlTemplate` unused | Found | "`BuildHtmlTemplate` is only called by `SendWelcomeEmailHtml`, which is unused." |
| D6 | `SendWelcomeEmailHtml` unused | Found | "`BuildHtmlTemplate` is only called by `SendWelcomeEmailHtml`, which is unused." |
| D7 | `FormatCurrency` unused | Found | "`FormatCurrency` is defined but never called." |
| D8 | `IsWithinDailyLimit` unused | Missed | The review mentions null checks in `IsWithinDailyLimit` but does not flag it as dead/unused code. |
| D9 | `ObfuscateAccount` unused | Missed | The review does not mention `ObfuscateAccount`. |
| D10 | `ToTitleCase` unused | Found | "`ToTitleCase` duplicates standard library functionality." |
| D11 | `JoinWithSeparatorFixed` unused | Found | "`JoinWithSeparatorFixed` duplicates `string.Join`." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state in UserService | Found | "Static mutable state `_auditLog` and `_requestCount` are not thread-safe." |
| A2 | Regex compiled per-call | Found | "`new Regex` created on every call." |
| A3 | String concatenation in loop | Found | "String concatenation in loop is O(n²)." |
| A4 | Shared mutable `SmtpClient` | Found | "`SmtpClient` is not thread-safe and shared." |
| A5 | Reimplementing BCL (`IsBlank`) | Found | "`IsBlank` duplicates `string.IsNullOrWhiteSpace`." |
| A6 | Leaking connection (`GetOpenConnection`) | Found | "`GetOpenConnection` returns an open connection without disposing it..." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Found | "Production database credentials committed to source control." |
| CF2 | Log level `Debug` in production | Found | "Logging level is set to `Debug` for all namespaces." |
| CF3 | JWT `ValidateLifetime = false` | Found | "JWT `ValidateLifetime` is set to `false`." |
| CF4 | HTTPS disabled | Found | "HTTPS redirection is commented out." |
| CF5 | `UseDeveloperExceptionPage()` unconditional | Found | "`UseDeveloperExceptionPage()` is enabled unconditionally." |
| CF6 | Open CORS policy | Found | "CORS policy allows any origin, method, and header." |
| CF7 | DebugSymbols/DebugType in release | Found | "`DebugSymbols` and `DebugType` are set for release builds." |
| CF8 | Pinned outdated `Newtonsoft.Json` | Found | "`Newtonsoft.Json` version 12.0.3 is outdated and potentially vulnerable." |
| CF9 | No `appsettings.Production.json` | Missed | The review does not mention the missing production-specific config file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage | Found | "No test project exists." and lists specific areas needing tests. |