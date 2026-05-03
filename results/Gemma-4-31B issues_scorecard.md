# AI Review Scorecard

> **Branch:** `Gemma-4` &nbsp;·&nbsp; **Commit:** `8f1df23`

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | SQL injection via string interpolation in Login query |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Hardcoded admin bypass password backdoor |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Weak MD5 hashing algorithm used for passwords |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | SQL injection via string interpolation in UpdateUser |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | SQL injection via string interpolation in SearchUsers |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | SQL injection via string interpolation in balance updates |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | SQL injection via string interpolation in RecordTransaction |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Hardcoded database credentials in fallback string |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | JWT ValidateLifetime set to false |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | Missing ownership check on UpdateUser endpoint |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | Missing ownership check on DeleteUser endpoint |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | No check to prevent transferring funds to self |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Balance check ignores transaction fee |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Pagination off-by-one error in skip calculation |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Redundant multiplication by 1 in interest calculation |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | No check to prevent transferring funds to self |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | No specific mention of duplicated validation |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | String concatenation in loop creates O(n2) complexity |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | No specific mention of token generation complexity |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Broad Exception catch swallows errors in SearchUsers |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Broad Exception catch swallows errors in SendWelcomeEmail |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Multiple DB writes and email send lack atomicity |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response.** | Found | No specific mention of email failure propagation |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Internal exception message returned to HTTP client |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | No specific mention of connection closing |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | No specific mention of rate limiting |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | SqlConnection and SqlCommand not disposed in Login |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | SqlConnection returned by GetOpenConnection is not disposed |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | No specific mention of connection disposal |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | SmtpClient held as field and never disposed |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | MailMessage object not disposed |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Potential null reference from config key in GenerateJwtToken |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Accessing Rows[0] without checking if table is empty |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | Potential null reference from config key in SmtpClient |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | Potential null reference when accessing email.Length |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | Potential null reference when accessing username.Length |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Potential null reference when parsing userIdClaim |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | No specific mention of null request checks |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Transaction fee rate hardcoded as literal |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | User ID range limit hardcoded as 1000000 |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Notification email address hardcoded |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | No specific mention of these literals |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Max page size hardcoded as 50 |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | HashPasswordSha1 method is never used |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Unreachable code after return true in ValidateToken |
| D3 | `TableExists` — never called from any service or controller. | Found | No specific mention of TableExists |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | No specific mention of ExecuteQueryWithParams |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | No specific mention of BuildHtmlTemplate |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | No specific mention of SendWelcomeEmailHtml |
| D7 | `FormatCurrency` — private, never called. | Found | FormatCurrency method is never called |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | No specific mention of IsWithinDailyLimit |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | No specific mention of ObfuscateAccount |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | No specific mention of ToTitleCase |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | JoinWithSeparator is a duplicate of JoinWithSeparatorFixed |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | Static mutable state used in scoped service |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Regex object instantiated on every method call |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | String concatenation in loop creates O(n2) complexity |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | SmtpClient held as field and never disposed |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | Manual implementation of IsBlank |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | No specific mention of GetOpenConnection |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Production database password stored in plain text |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Log levels set to Debug for production |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | JWT ValidateLifetime set to false |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | HttpsRedirection is commented out |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | UseDeveloperExceptionPage called unconditionally |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | CORS policy allows any origin |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | No specific mention of debug symbols |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | No specific mention of package versions |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | No specific mention of missing production settings |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | **No test project exists in the solution** — key areas like AuthService.Login, TransactionService.Transfer, UserService.GetUsersPage, and StringHelper need tests. | Found | No test project exists in the solution |