# AI Review Scorecard

> **Branch:** `Qwen3.5-9B` &nbsp;·&nbsp; **Commit:** `71872c4`

Total: 63 Found / 7 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | The review identifies SQL injection in `Login` method via string interpolation in `Services/AuthService.cs` and recommends using parameterized queries. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | The review mentions hardcoded `AdminBypassPassword` and recommends removing it or using configuration. |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | The review identifies MD5 hashing in `AuthService.cs` and recommends replacing with bcrypt or Argon2. |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | The review identifies SQL injection in `UpdateUser` and `DeleteUser` methods via string interpolation in `Services/UserService.cs` and recommends parameterized queries. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | The review identifies SQL injection in `SearchUsers` method via string interpolation in `Services/UserService.cs` and recommends parameterized queries. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | The review identifies SQL injection in `Transfer` and `Deposit` methods via string interpolation in `Services/TransactionService.cs` and recommends parameterized queries. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | The review identifies SQL injection in `RecordTransaction` method via string interpolation in `Services/TransactionService.cs` and recommends parameterized queries. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | The review identifies hardcoded credentials in `appsettings.json` and recommends using environment variables or secrets manager. |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | The review identifies `ValidateLifetime = false` in `Program.cs` and recommends setting it to `true`. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | The review identifies missing ownership checks in `Login` method and recommends implementing authorization. |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | The review identifies missing authorization in `DeleteUser` method and recommends implementing role checks. |

## Logic Errors

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | The review identifies logic error in `Transfer` method and recommends checking `fromBalance >= amount + fee` before deducting. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | The review identifies balance check logic error in `Transfer` method and recommends checking `fromBalance >= amount + fee`. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | The review identifies pagination logic error in `GetUsersPage` method and recommends fixing `skip` calculation to `(page - 1) * pageSize`. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | The review identifies incorrect interest rate logic in `Deposit` method and recommends correcting the interest bonus rate. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | The review identifies self-transfer logic error in `Transfer` method and recommends adding check for `fromUserId != request.ToUserId`. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | The review mentions duplicated validation but does not specifically mention extracting to a private method. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | The review identifies string concatenation in loop in `JoinWithSeparator` and recommends using `string.Join`. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | The review mentions the method but does not specifically mention splitting into helpers. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | The review identifies exception handling issue in `SearchUsers` and recommends catching specific exceptions or logging generic errors. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | The review identifies broad exception handling in `SendWelcomeEmail` and recommends using `ILogger` for logging. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Partial | The review mentions missing transaction handling but does not specifically name this issue. |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Partial | The review mentions email failure handling but does not specifically name this issue. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | The review identifies error message exposure in `UserController.cs` and recommends logging internally without exposing stack traces. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | The review identifies resource leak in `ExecuteNonQuery` and recommends using `using` blocks for all database objects. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | The review identifies missing rate limiting in `AuthController.cs` and recommends implementing account lockout. |

## Resource Leaks

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | The review identifies resource leak in `Login` method and recommends using `using` blocks. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | The review identifies resource leak in `ExecuteQuery` and recommends using `using` blocks. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | The review identifies resource leak in `ExecuteNonQuery` and recommends using `using` blocks. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | The review identifies resource leak in `EmailService.cs` and recommends using `using` blocks for `SmtpClient`. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | The review identifies resource leak in `MailMessage` and recommends using `using` blocks. |

## Missing Null Checks

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | The review identifies null reference risk in `GenerateJwtToken` and recommends adding null check for `Jwt:SecretKey`. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | The review identifies null reference risk in `Transfer` method and recommends adding null checks. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | The review identifies null reference risk in `EmailService.cs` and recommends adding null checks for configuration values. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | The review identifies null reference risk in `EmailService.cs` and recommends adding null checks. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | The review identifies null reference risk in `StringHelper.cs` and recommends adding null checks. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | The review identifies null reference risk in `TransactionController.cs` and recommends adding null checks. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | The review identifies null reference risk in `UserController.cs` and recommends adding null checks for request body. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | The review identifies magic numbers in `TransactionService.cs` and recommends defining named constants. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | The review identifies magic number in `UserService.cs` and recommends defining named constant. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | The review identifies magic strings in `EmailService.cs` and recommends using configuration values. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | The review identifies magic numbers in `StringHelper.cs` and recommends defining named constants. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | The review identifies magic number in `UserService.cs` and recommends defining named constant. |

## Dead Code

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | The review identifies unused `HashPasswordSha1` method and recommends removing it. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | The review identifies unreachable code in `ValidateToken` method and recommends completing validation logic. |
| D3 | `TableExists` — never called from any service or controller. | Found | The review identifies unused `TableExists` method and recommends removing it. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | The review identifies obsolete method `ExecuteQueryWithParams` and recommends removing it. |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | The review identifies unused `BuildHtmlTemplate` method and recommends removing it. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | The review identifies unused `SendWelcomeEmailHtml` method and recommends removing it. |
| D7 | `FormatCurrency` — private, never called. | Found | The review identifies unused `FormatCurrency` method and recommends removing it. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | The review identifies unused `IsWithinDailyLimit` method and recommends removing it. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | The review identifies unused `ObfuscateAccount` method and recommends removing it. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | The review identifies unused `ToTitleCase` method and recommends removing it. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | The review identifies unused `JoinWithSeparatorFixed` method and recommends removing it. |

## Anti-patterns

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | The review mentions static state but does not specifically name this anti-pattern. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | The review identifies regex compilation issue in `StringHelper.cs` and recommends making Regex instance `static readonly`. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | The review identifies string concatenation in loop in `StringHelper.cs` and recommends using `string.Join`. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | The review identifies shared mutable `SmtpClient` issue and recommends using `using` blocks. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | The review identifies reimplemented BCL in `StringHelper.cs` and recommends using `string.IsNullOrWhiteSpace`. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | The review identifies leaking connection issue in `DatabaseHelper.cs` and recommends using `using` blocks. |

## Configuration Issues

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | The review identifies production secrets in source control and recommends using environment variables. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | The review identifies debug logging level in production and recommends setting to `Information` or `Warning`. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | The review identifies JWT lifetime validation disabled and recommends setting `ValidateLifetime = true`. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | The review identifies HTTPS redirection disabled and recommends uncommenting `UseHttpsRedirection()`. |
| CF5 | **UseDeveloperExceptionPage() called unconditionally** — full stack traces served to production clients. | Found | The review identifies unconditional `UseDeveloperExceptionPage()` and recommends guarding behind development environment check. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | The review identifies open CORS policy and recommends restricting to specific origins and methods. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | The review identifies debug symbols in release builds and recommends setting `DebugSymbols=false` and `DebugType=pdbonly`. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | The review mentions outdated packages but does not specifically name this issue. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | The review mentions missing environment-specific config but does not specifically name this issue. |

## Missing Unit Tests

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| UT | **Missing Unit Tests** — The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `TransactionService.Transfer`, `UserService.GetUsersPage`, etc. | Found | The review identifies the missing unit tests and recommends adding tests for key service methods and controller actions.