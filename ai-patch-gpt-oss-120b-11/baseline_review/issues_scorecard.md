# AI Review Scorecard

> **Branch:** `gpt-oss-120B` &nbsp;·&nbsp; **Commit:** `0b009ba`

Total: 55 Found / 2 Partial / 13 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) | Found | "SQL Injection via string interpolation in `Login` method." |
| C2 | Backdoor / hardcoded admin bypass | Found | "Hardcoded admin backdoor password allows bypassing authentication." |
| C3 | Broken password hashing | Found | "Passwords hashed using weak MD5 algorithm without salt." |
| C4 | SQL Injection (UpdateUser / DeleteUser) | Found | "SQL Injection via string interpolation in `UpdateUser` method." and "SQL Injection via string interpolation in `DeleteUser` method." |
| C5 | SQL Injection (SearchUsers) | Found | "SQL Injection via string interpolation in `SearchUsers` method." |
| C6 | SQL Injection (Transfer/Deposit) | Found | "SQL Injection via string interpolation in `Transfer` method." and "SQL Injection via string interpolation in `Deposit` method." |
| C7 | SQL Injection (RecordTransaction) | Found | "SQL Injection via string interpolation in `RecordTransaction` method." |
| C8 | Hardcoded production credentials | Found | "Production database credentials committed to source control." |
| C9 | JWT lifetime validation disabled | Found | "`ValidateLifetime` set to false, allowing expired tokens." |
| C10 | Broken Access Control (UpdateUser) | Found | "Missing ownership check on `UpdateUser` endpoint (any authenticated user can update any user)." |
| C11 | Missing Authorization (DeleteUser) | Found | "Missing ownership check on `DeleteUser` endpoint (any authenticated user can delete any user)." |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | Zero-value transfers allowed | Missed | The review mentions balance checks and fees but does not explicitly identify the `amount < 0` vs `amount <= 0` logic error allowing zero transfers. |
| L2 | Balance check excludes fee | Found | "Balance check compares against `amount` but deducts `amount + fee`, allowing negative balances." |
| L3 | Off-by-one in pagination | Found | "Pagination offset calculation is incorrect (`page * pageSize` instead of `(page - 1) * pageSize`)." |
| L4 | Incorrect interest rate | Partial | "Deposit interest calculation multiplies by 1, effectively ignoring the bonus logic or applying it incorrectly." (Identifies the issue but mischaracterizes the specific math error described in reference). |
| L5 | Self-transfer allowed | Missed | The review mentions "Missing ownership check on `Transfer` endpoint" but this refers to unauthorized transfers between users, not the specific self-transfer fee deduction bug. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation | Missed | The review does not mention extracting the duplicated ID validation logic into a helper method. |
| R2 | Loop string concatenation | Found | "String concatenation in loop (`result += item + separator`). Use `StringBuilder` or `string.Join`." |
| R3 | Overly long GenerateJwtToken | Missed | The review does not suggest refactoring `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | SearchUsers swallows exceptions | Found | "`SearchUsers` catches broad `Exception` and returns empty list, hiding errors." |
| E2 | SendWelcomeEmail catches Exception | Found | "`SendWelcomeEmail` catches broad `Exception` and swallows it, hiding failures." |
| E3 | No database transaction in Transfer | Found | "`Transfer` lacks database transaction; partial failures can corrupt balances." |
| E4 | Email failure propagates after commit | Missed | The review mentions transaction issues but does not specifically identify the exception propagation after DB commit in `Transfer`. |
| E5 | Exposes ex.Message to client | Found | "`UpdateUser` returns raw `ex.Message` to client, leaking internal details." |
| E6 | ExecuteNonQuery connection leak on exception | Found | "`ExecuteNonQuery` opens connection but may leak if `ExecuteNonQuery` throws." |
| E7 | No rate limiting on login | Missed | The review does not mention missing rate limiting or account lockout mechanisms. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | SqlConnection/Reader not disposed in Login | Found | "`SqlConnection` opened but never closed/disposed in `Login`." |
| RL2 | GetOpenConnection leak | Found | "`GetOpenConnection` returns open connection without disposal responsibility." |
| RL3 | ExecuteNonQuery not disposed | Found | "`ExecuteQuerySafe` opens connection but `SqlDataAdapter` may not close it properly if exception occurs." (Note: Review maps this to ExecuteQuerySafe/ExecuteNonQuery context). |
| RL4 | SmtpClient instance field leak | Found | "`SmtpClient` held as instance field; not thread-safe and may leak sockets." |
| RL5 | MailMessage not disposed | Found | "`MailMessage` created but never disposed." (Mentioned for multiple locations). |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | Jwt:SecretKey null check | Found | "`jwtSecret` used without null check in `GetBytes`." |
| N2 | Rows[0] access without count check | Found | "`fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`." |
| N3 | SmtpPort fallback hiding missing key | Missed | The review mentions null checks for config but does not specifically critique the `?? "25"` fallback logic for port correctness. |
| N4 | username.ToUpper() null ref | Missed | The review mentions null checks for email/username length but not specifically `username.ToUpper()` in `SendWelcomeEmail`. |
| N5 | email/username Length null guard | Found | "`email.Length` accessed without null check." and "`username.Length` accessed without null check." |
| N6 | User.FindFirst null parse | Found | "`int.Parse` on `userIdClaim` can throw if claim is null or non-integer." |
| N7 | UpdateUser null request check | Missed | The review does not mention checking for null request body in `UpdateUser`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | TransactionFeeRate/MaxTransactions constants | Found | "Hardcoded transaction fee rate." and "Hardcoded max transactions per day." |
| M2 | Deposit cap hardcoded | Found | "Hardcoded deposit limit (1000000)." |
| M3 | Email addresses hardcoded | Found | "Hardcoded sender email address." (Mentioned for multiple locations). |
| M4 | StringHelper bare literals | Found | "Hardcoded email length limit (254)." and "Hardcoded username length limits (3, 20)." |
| M5 | Page size upper bound unnamed | Found | "Hardcoded page size limit (50)." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | HashPasswordSha1 unused | Found | "`HashPasswordSha1` is defined but never called." |
| D2 | ValidateToken unreachable code | Found | "`ValidateToken` method returns `true` immediately, ignoring actual token validation." |
| D3 | TableExists unused | Missed | The review does not mention `TableExists` as dead code. |
| D4 | ExecuteQueryWithParams unused | Found | "`ExecuteQueryWithParams` marked `[Obsolete]` but still present." |
| D5 | BuildHtmlTemplate unused | Found | "`BuildHtmlTemplate` is only called by `SendWelcomeEmailHtml`, which is unused." |
| D6 | SendWelcomeEmailHtml unused | Found | "`SendWelcomeEmailHtml` is defined but never called." |
| D7 | FormatCurrency unused | Found | "`FormatCurrency` is defined but never called." |
| D8 | IsWithinDailyLimit unused | Missed | The review does not mention `IsWithinDailyLimit` as dead code. |
| D9 | ObfuscateAccount unused | Missed | The review does not mention `ObfuscateAccount` as dead code. |
| D10 | ToTitleCase unused | Found | "`ToTitleCase` duplicates standard library functionality." |
| D11 | JoinWithSeparatorFixed unused | Partial | "`JoinWithSeparatorFixed` duplicates `string.Join`." (Identifies it as redundant/unused but phrasing is slightly different from "never used"). |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state | Found | "Static mutable state `_auditLog` shared across instances." |
| A2 | Regex compiled per-call | Found | "`new Regex` created on every call." |
| A3 | String concatenation in loop | Found | "String concatenation in loop (`result += item + separator`)." |
| A4 | Shared mutable SmtpClient | Found | "`SmtpClient` held as instance field; not thread-safe..." |
| A5 | Reimplementing BCL (IsBlank) | Found | "`IsBlank` duplicates `string.IsNullOrWhiteSpace`." |
| A6 | Leaking connection anti-pattern | Found | "`GetOpenConnection` returns open connection without disposal responsibility." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control | Found | "Production database credentials committed to source control." |
| CF2 | Log level Debug in production | Found | "Debug log levels set for production namespaces." |
| CF3 | JWT ValidateLifetime false | Found | "`ValidateLifetime` set to false." |
| CF4 | HTTPS disabled | Found | "HTTPS redirection commented out." |
| CF5 | UseDeveloperExceptionPage unconditional | Found | "`UseDeveloperExceptionPage()` called unconditionally." |
| CF6 | Open CORS policy | Found | "Overly permissive CORS policy." |
| CF7 | DebugSymbols true in release | Found | "`DebugSymbols` and `DebugType` set in project file." |
| CF8 | Pinned outdated Newtonsoft.Json | Found | "`Newtonsoft.Json` version 12.0.3 is outdated and vulnerable." |
| CF9 | No appsettings.Production.json | Missed | The review does not mention the missing environment-specific configuration file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | Missing Unit Tests (aggregate) | Found | "No test project exists." and lists specific methods needing tests like `Login`, `Transfer`, `Deposit`, `GetUsersPage`. |