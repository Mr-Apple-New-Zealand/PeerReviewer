# AI Review Scorecard

> **Branch:** `Qwen3.5-0.8B` &nbsp;·&nbsp; **Commit:** `4c8e082`

Total: 54 Found / 4 Partial / 12 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) | Found | "SQL Injection via string interpolation in `Login` query." |
| C2 | Backdoor / hardcoded admin bypass | Found | "Hardcoded admin bypass password (`SuperAdmin2024`)." |
| C3 | Broken password hashing | Partial | "Weak cryptography: MD5 used for password hashing." (Misses missing salt detail) |
| C4 | SQL Injection (UpdateUser / DeleteUser) | Found | "SQL Injection in `UpdateUser`... SQL Injection in `DeleteUser`..." |
| C5 | SQL Injection (SearchUsers) | Found | "SQL Injection in `SearchUsers` via `ExecuteQuery`..." |
| C6 | SQL Injection (Transfer/Deposit) | Found | "SQL Injection in `Transfer`... SQL Injection in `Deposit`..." |
| C7 | SQL Injection (RecordTransaction) | Found | "SQL Injection in `RecordTransaction`..." |
| C8 | Hardcoded production credentials | Found | "Production database credentials committed to source control." |
| C9 | JWT lifetime validation disabled | Found | "`ValidateLifetime = false` on JWT validation." |
| C10 | Broken Access Control (UpdateUser) | Found | "Missing authorization check on `UpdateUser`..." |
| C11 | Missing Authorization (DeleteUser) | Found | "Missing authorization check on `DeleteUser`..." |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | Zero-value transfers allowed | Missed | Review mentions balance check and self-transfer, but not the `amount < 0` vs `amount <= 0` boundary specifically. |
| L2 | Balance check excludes fee | Found | "Balance check uses `amount` but deducts `amount + fee`, allowing negative balances." |
| L3 | Off-by-one in pagination | Found | "Pagination offset calculation `page * pageSize` is off-by-one..." |
| L4 | Incorrect interest rate | Partial | "Deposit interest bonus calculation... is redundant and unclear." (Misses specific 5% vs 1% error) |
| L5 | Self-transfer allowed | Found | "Missing check for self-transfer (`fromUserId == toUserId`)." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation | Missed | Review does not mention extracting `ValidateUserId` or duplicated ID guards. |
| R2 | Loop string concatenation | Found | "String concatenation in loop (`result += item`)." |
| R3 | Overly long GenerateJwtToken | Missed | Review does not mention splitting `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | SearchUsers swallows exceptions | Found | "`SearchUsers` catches `Exception` and returns empty list..." |
| E2 | SendWelcomeEmail catches Exception | Found | "`SendWelcomeEmail` catches `Exception` and prints to console..." |
| E3 | No database transaction (Transfer) | Found | "`Transfer` lacks database transaction for atomic balance updates." |
| E4 | Email failure propagates after commit | Found | "Side effect (email) occurs after DB writes; if email fails, transaction is already committed." |
| E5 | Exposes ex.Message | Found | "`UpdateUser` returns raw `ex.Message` to client..." |
| E6 | ExecuteNonQuery connection leak | Found | "`ExecuteNonQuery` opens connection; if `ExecuteNonQuery` throws, connection leaks." |
| E7 | No rate limiting | Missed | Review does not mention brute force protection or rate limiting. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | SqlConnection/Reader leak in Login | Found | "`SqlConnection` opened but never closed/disposed in `Login`." |
| RL2 | GetOpenConnection leak | Found | "`GetOpenConnection` returns open connection; caller must dispose." |
| RL3 | ExecuteNonQuery dispose issue | Found | "`ExecuteNonQuery` opens connection; if `ExecuteNonQuery` throws, connection leaks." |
| RL4 | SmtpClient instance field | Found | "`SmtpClient` held as instance field; not thread-safe and may leak sockets." |
| RL5 | MailMessage not disposed | Found | "`MailMessage` not disposed after sending." (Multiple entries cover this) |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | Jwt:SecretKey null check | Found | "`_config["Jwt:SecretKey"]` used without null check." |
| N2 | Rows[0] access without count check | Found | "`fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`." |
| N3 | SmtpPort config fallback | Partial | "`_config["Email:SmtpPort"]` used without null check..." (Misses specific port 25 TLS concern) |
| N4 | username.ToUpper() null ref | Missed | Review mentions config nulls, but not `username.ToUpper()` NRE. |
| N5 | StringHelper null args | Missed | Review does not mention null guards for `email.Length`/`username.Length`. |
| N6 | User.FindFirst null parse | Found | "`int.Parse` on `userIdClaim` can throw if claim is missing..." |
| N7 | UpdateUser null request | Missed | Review does not mention checking `request == null`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | TransactionFeeRate/MaxTransactions hardcoded | Found | "`TransactionFeeRate`... is hardcoded." / "`MaxTransactionsPerDay`... is hardcoded." |
| M2 | Deposit cap hardcoded | Found | "Deposit limit (1000000) is hardcoded." |
| M3 | Email addresses hardcoded | Found | "Sender email ("notifications@company.com") is hardcoded." |
| M4 | StringHelper literals | Found | "Email length limit (254) is hardcoded." / "Username length limits... are hardcoded." |
| M5 | Page size 50 unnamed | Found | "Page size limit (50) is hardcoded." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | HashPasswordSha1 unused | Found | "`HashPasswordSha1` is defined but never called." |
| D2 | ValidateToken unreachable code | Found | "`ValidateToken` has unreachable code after `return true`." |
| D3 | TableExists unused | Missed | Review does not mention `TableExists`. |
| D4 | ExecuteQueryWithParams unused | Found | "`ExecuteQueryWithParams` is marked `[Obsolete]` but still present." |
| D5 | BuildHtmlTemplate unused | Missed | Review does not mention `BuildHtmlTemplate`. |
| D6 | SendWelcomeEmailHtml unused | Missed | Review does not mention `SendWelcomeEmailHtml`. |
| D7 | FormatCurrency unused | Found | "`FormatCurrency` is defined but never called." |
| D8 | IsWithinDailyLimit unused | Missed | Review does not mention `IsWithinDailyLimit`. |
| D9 | ObfuscateAccount unused | Found | "`ObfuscateAccount` duplicates `MaskAccountNumber` functionality." |
| D10 | ToTitleCase unused | Missed | Review does not mention `ToTitleCase`. |
| D11 | JoinWithSeparatorFixed unused | Partial | "`JoinWithSeparator` is inefficient and likely unused; `JoinWithSeparatorFixed` exists." (Implies fixed version is the alternative, but doesn't explicitly state it's dead code) |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state | Found | "Static mutable state `_auditLog` and `_requestCount` shared across instances." |
| A2 | Regex compiled per-call | Found | "`new Regex(...)` created on every call; should be static readonly." |
| A3 | String concatenation in loop | Found | "String concatenation in loop (`result += item`)." |
| A4 | Shared mutable SmtpClient | Found | "`SmtpClient` is not thread-safe; shared instance causes race conditions." |
| A5 | Reimplementing BCL (IsBlank) | Found | "`IsBlank` duplicates `string.IsNullOrWhiteSpace`." |
| A6 | Leaking connection anti-pattern | Found | "`GetOpenConnection` returns open connection; caller must dispose." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Found | "Production database credentials committed to source control." |
| CF2 | Log level Debug in production | Found | "Debug log level set for all namespaces." |
| CF3 | JWT ValidateLifetime false | Found | "`ValidateLifetime = false` on JWT validation." |
| CF4 | HTTPS disabled | Found | "`UseHttpsRedirection()` is commented out." |
| CF5 | UseDeveloperExceptionPage unconditional | Found | "`UseDeveloperExceptionPage()` enabled unconditionally." |
| CF6 | Open CORS policy | Found | "CORS allows any origin, method, and header." |
| CF7 | DebugSymbols in release | Found | "`DebugSymbols` and `DebugType` set for release builds." |
| CF8 | Outdated Newtonsoft.Json | Found | "`Newtonsoft.Json` version 12.0.3 is outdated and vulnerable." |
| CF9 | No appsettings.Production.json | Found | "No environment-specific config files..." |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage | Found | "No test project exists." / "Create unit tests for critical services." |