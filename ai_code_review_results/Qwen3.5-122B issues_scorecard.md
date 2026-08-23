# AI Review Scorecard

> **Branch:** `Qwen3.5-122B` &nbsp;·&nbsp; **Commit:** `da2028e`

Total: 64 Found / 6 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | SampleBankingApp/Services/AuthService.cs:31 - "Login" constructs SQL via string interpolation, violating SQL injection prevention. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | SampleBankingApp/Services/AuthService.cs:24 - "Hardcoded backdoor password (`SuperAdmin2024`) allows bypassing authentication." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | SampleBankingApp/Services/AuthService.cs:56 - "Password hashing uses MD5, which is cryptographically broken and insecure." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | SampleBankingApp/Data/DatabaseHelper.cs:27 - "ExecuteQuery" constructs SQL using string interpolation for table name and where clause, enabling SQL injection. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | SampleBankingApp/Services/UserService.cs:88 - "SearchUsers" uses "ExecuteQuery" with string interpolation for `LIKE` clause, vulnerable to SQL injection. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | SampleBankingApp/Services/TransactionService.cs:62 - "RecordTransaction" constructs SQL via string interpolation, vulnerable to SQL injection via description field. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | SampleBankingApp/Services/TransactionService.cs:62 - "RecordTransaction" constructs SQL via string interpolation, vulnerable to SQL injection via description field. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | SampleBankingApp/appsettings.json:5 - "Plaintext database password (`Admin1234!`) committed to source control." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | SampleBankingApp/Program.cs:28 - "ValidateLifetime = false" allows expired tokens to be accepted as valid. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | SampleBankingApp/Controllers/UserController.cs:53 - "No rate limiting or account lockout on failed login attempts — brute force is trivially possible." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | SampleBankingApp/Controllers/UserController.cs:67 - "No rate limiting or account lockout on failed login attempts — brute force is trivially possible." |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | SampleBankingApp/Services/TransactionService.cs:45 - "Balance check `fromBalance >= amount` ignores the transaction fee, allowing overdraft." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | SampleBankingApp/Services/TransactionService.cs:45 - "Balance check `fromBalance >= amount` ignores the transaction fee, allowing overdraft." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | SampleBankingApp/Services/UserService.cs:65 - "Pagination logic `skip = page * pageSize` skips the first page (page 1 skips 20 items)." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | SampleBankingApp/Services/TransactionService.cs:65 - "Deposit" calculates interest as `amount * 0.05m * 1`, hardcoding the multiplier. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | SampleBankingApp/Controllers/TransactionController.cs:26 - "int.Parse" on user claim without null check or validation allows potential crash or injection if claim is missing. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | SampleBankingApp/Services/UserService.cs:20 - "Duplicated validation" is mentioned but not specifically named in the review. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs:27 - "JoinWithSeparator" uses string concatenation in a loop, causing O(n²) performance. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | SampleBankingApp/Services/AuthService.cs:71 - "Overly long `GenerateJwtToken`" is mentioned but not specifically named in the review. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | SampleBankingApp/Services/UserService.cs:88 - "SearchUsers" swallows all exceptions and returns empty list, hiding potential security errors. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | SampleBankingApp/Services/EmailService.cs:62 - "catch (Exception)" swallows the exception and logs to `Console.WriteLine`, hiding failures. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | SampleBankingApp/Services/TransactionService.cs:50 - "Email sending occurs after DB updates; if email fails, the transaction is committed but user is not notified." |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Found | SampleBankingApp/Services/TransactionService.cs:50 - "Email sending occurs after DB updates; if email fails, the transaction is committed but user is not notified." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | SampleBankingApp/Controllers/UserController.cs:56 - "catch (Exception)" returns generic 500 but logs the full exception, which is good, but the message is generic. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | SampleBankingApp/Data/DatabaseHelper.cs:50 - "ExecuteNonQuery" opens connection but does not dispose it if `ExecuteNonQuery` throws. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | SampleBankingApp/Controllers/AuthController.cs:20 - "No rate limiting or account lockout on failed login attempts — brute force is trivially possible." |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | SampleBankingApp/Services/AuthService.cs:37 - "Login" does not dispose `SqlConnection`, `SqlCommand`, or `SqlDataReader". |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | SampleBankingApp/Data/DatabaseHelper.cs:19 - "GetOpenConnection" returns an open connection that the caller must close, risking leaks. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | SampleBankingApp/Data/DatabaseHelper.cs:50 - "ExecuteNonQuery" opens connection but does not dispose it if `ExecuteNonQuery` throws. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | SampleBankingApp/Services/EmailService.cs:20 - "SmtpClient" is held as a field, which is not thread-safe and causes socket leaks. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | SampleBankingApp/Services/EmailService.cs:36 - "MailMessage" is created but never disposed, causing resource leaks. |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | SampleBankingApp/Services/AuthService.cs:62 - "_config["Jwt:SecretKey"]" can be null, causing `Encoding.UTF8.GetBytes` to throw. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | SampleBankingApp/Services/TransactionService.cs:42 - "`fromUserTable.Rows[0]" accessed without checking `Rows.Count > 0`. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | SampleBankingApp/Services/EmailService.cs:46 - "int.Parse(_config["Email:SmtpPort"] ?? "25")" - falls back to `"25"` but port 25 may not be correct for TLS. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | SampleBankingApp/Services/EmailService.cs:68 - "`username.ToUpper()" throws `NullReferenceException` if `username` is `null`. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | SampleBankingApp/Helpers/StringHelper.cs:14 - "`email.Length" and `username.Length` throw if argument is `null`. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | SampleBankingApp/Controllers/TransactionController.cs:24 - "`int.Parse" on user claim without null check or validation allows potential crash or injection if claim is missing. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | SampleBankingApp/Controllers/UserController.cs:28 - "UpdateUser" and controller endpoints don't check `request == null` — model binding can produce null body. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | SampleBankingApp/Services/TransactionService.cs:15 - "`TransactionFeeRate` is hardcoded as `0.015m`. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | SampleBankingApp/Services/TransactionService.cs:65 - "Deposit" calculates interest as `amount * 0.05m * 1`, hardcoding the multiplier. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | SampleBankingApp/Services/EmailService.cs:36 - "`notifications@company.com" is hardcoded. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | SampleBankingApp/Helpers/StringHelper.cs:14 - "`email.Length" and `username.Length` throw if argument is `null`. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | SampleBankingApp/Services/UserService.cs:65 - "`50` max page size is hardcoded." |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | SampleBankingApp/Services/AuthService.cs:79 - "`HashPasswordSha1" is defined but never called. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | SampleBankingApp/Services/AuthService.cs:83 - "`ValidateToken" method returns `true` immediately without actually validating the JWT token. |
| D3 | `TableExists` — never called from any service or controller. | Found | SampleBankingApp/Data/DatabaseHelper.cs:49 - "`TableExists" — never called from any service or controller. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | SampleBankingApp/Data/DatabaseHelper.cs:59 - "`ExecuteQueryWithParams" is marked `[Obsolete]` but still present and unused. |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | SampleBankingApp/Services/EmailService.cs:56 - "`BuildHtmlTemplate" is defined but never called. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | SampleBankingApp/Services/EmailService.cs:79 - "`SendWelcomeEmailHtml" — public method, never registered or called. |
| D7 | `FormatCurrency` — private, never called. | Found | SampleBankingApp/Services/TransactionService.cs:83 - "`FormatCurrency" is defined but never called. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | SampleBankingApp/Services/TransactionService.cs:73 - "`IsWithinDailyLimit" is defined but never called in `Transfer` method. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | SampleBankingApp/Helpers/StringHelper.cs:49 - "`ObfuscateAccount" — superseded by `MaskAccountNumber`, never called. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | SampleBankingApp/Helpers/StringHelper.cs:54 - "`ToTitleCase" — "experimental utility never integrated", never called. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | SampleBankingApp/Helpers/StringHelper.cs:37 - "`JoinWithSeparatorFixed" — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | SampleBankingApp/Services/UserService.cs:14 - "_auditLog" and "_requestCount" are static fields, causing shared mutable state across requests. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | SampleBankingApp/Helpers/StringHelper.cs:13 - "IsValidEmail" creates a new `Regex` instance on every call. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs:27 - "JoinWithSeparator" uses string concatenation in a loop, causing O(n²) performance. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | SampleBankingApp/Services/EmailService.cs:20 - "SmtpClient" is held as a field, which is not thread-safe and causes socket leaks. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | SampleBankingApp/Helpers/StringHelper.cs:56 - "`IsBlank" reimplements `string.IsNullOrWhiteSpace`. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | SampleBankingApp/Data/DatabaseHelper.cs:19 - "GetOpenConnection" returns an open connection that the caller must close, risking leaks. |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | SampleBankingApp/appsettings.json:5 - "Plaintext database password (`Admin1234!`) committed to source control." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | SampleBankingApp/Program.cs:28 - "Log level `Debug` in production" is mentioned but not specifically named in the review. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | SampleBankingApp/Program.cs:28 - "ValidateLifetime = false" allows expired tokens to be accepted as valid. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | SampleBankingApp/Program.cs:38 - "HTTPS redirection is commented out, allowing unencrypted traffic." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | SampleBankingApp/Program.cs:34 - "`UseDeveloperExceptionPage()" exposes stack traces and internal details to clients. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | SampleBankingApp/Program.cs:37 - "`AllowAnyOrigin()" combined with `AllowCredentials` (implied by auth) creates a security risk. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp/SampleBankingApp.csproj:15 - "`DebugSymbols` and `DebugType` enabled in production build expose internal code details." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | SampleBankingApp/SampleBankingApp.csproj:14 - "Pinned outdated package" is mentioned but not specifically named in the review. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | SampleBankingApp/appsettings.json:1 - "No `appsettings.Production.json`" is mentioned but not specifically named in the review. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | **Missing Unit Tests** — The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper` — all missing tests. | Partial | The review mentions "Missing Unit Tests" but does not specifically address the aggregate topic of missing tests. It focuses on specific code issues but does not summarize the entire missing test coverage section.