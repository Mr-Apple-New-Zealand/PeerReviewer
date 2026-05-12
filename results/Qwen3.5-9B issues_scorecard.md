# AI Review Scorecard

> **Branch:** `Qwen3.5-9B` &nbsp;·&nbsp; **Commit:** `eaaf237`

Total: 38 Found / 32 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | AI review identifies SQL injection via string interpolation in username and password parameters in AuthService.cs |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | AI review identifies hardcoded admin bypass password "SuperAdmin2024" in AuthService.cs |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | AI review identifies weak MD5 hashing for passwords without salt in AuthService.cs |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | AI review identifies SQL injection via string interpolation in sql parameter in DatabaseHelper.cs |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | AI review identifies SQL injection via string interpolation in sql parameter in DatabaseHelper.cs |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | AI review identifies SQL injection via string interpolation in sql parameter in DatabaseHelper.cs |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | AI review identifies SQL injection via string interpolation in sql parameter in DatabaseHelper.cs |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | AI review identifies hardcoded database credentials (sa/Password) in DatabaseHelper.cs |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | AI review identifies JWT lifetime validation disabled (ValidateLifetime = false) in Program.cs |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | AI review identifies missing validation for negative amounts in UpdateUserRequest in UserController.cs |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | AI review identifies missing validation for negative amounts in UpdateUserRequest in UserController.cs |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | AI review identifies missing check for negative amounts in TransferRequest in TransactionController.cs |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | AI review identifies missing check for negative amounts in DepositRequest in TransactionController.cs |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | AI review identifies potential integer overflow when parsing userIdClaim without range check in TransactionController.cs |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | AI review mentions incorrect interest rate but doesn't specifically identify the 5% vs 1% issue |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | AI review identifies missing check for self-transfer (ToUserId == FromUserId) in TransactionController.cs |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | AI review mentions logic errors but doesn't specifically identify duplicated validation blocks |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | AI review identifies string concatenation in loop for JoinWithSeparator in Helpers/StringHelper.cs |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | AI review doesn't specifically mention this refactoring opportunity |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | AI review identifies broad Exception catch swallows errors and returns empty result in AuthService.cs |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | AI review mentions error handling but doesn't specifically identify the broad exception catch in email service |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Partial | AI review doesn't specifically identify missing database transaction |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Partial | AI review doesn't specifically identify this error handling issue |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | AI review identifies catch block returns raw exception message to client in TransactionController.cs |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | AI review identifies SqlConnection and SqlCommand not disposed in ExecuteNonQuery in DatabaseHelper.cs |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | AI review doesn't specifically identify missing rate limiting |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | AI review identifies SqlConnection and SqlCommand not disposed in ExecuteQuery in DatabaseHelper.cs |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | AI review identifies SqlConnection and SqlCommand not disposed in ExecuteQuery in DatabaseHelper.cs |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | AI review identifies SqlConnection and SqlCommand not disposed in ExecuteNonQuery in DatabaseHelper.cs |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Partial | AI review doesn't specifically identify SmtpClient resource leak |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Partial | AI review doesn't specifically identify MailMessage disposal issues |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | AI review identifies null check missing for JWT secret key in Program.cs |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Partial | AI review doesn't specifically identify this null check issue |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | AI review doesn't specifically identify this null check issue |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | AI review doesn't specifically identify this null check issue |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | AI review doesn't specifically identify this null check issue |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Partial | AI review doesn't specifically identify this null check issue |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | AI review doesn't specifically identify this null check issue |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Partial | AI review doesn't specifically identify these magic numbers |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Partial | AI review doesn't specifically identify this magic number |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | AI review doesn't specifically identify these magic strings |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | AI review identifies magic number 254 for email length limit in Helpers/StringHelper.cs |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Partial | AI review doesn't specifically identify this magic number |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Partial | AI review doesn't specifically identify this dead code |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Partial | AI review doesn't specifically identify this dead code |
| D3 | `TableExists` — never called from any service or controller. | Partial | AI review doesn't specifically identify this dead code |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Partial | AI review doesn't specifically identify this dead code |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Partial | AI review doesn't specifically identify this dead code |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Partial | AI review doesn't specifically identify this dead code |
| D7 | `FormatCurrency` — private, never called. | Partial | AI review doesn't specifically identify this dead code |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Partial | AI review doesn't specifically identify this dead code |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | AI review identifies ObfuscateAccount method is unused in Helpers/StringHelper.cs |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | AI review identifies ToTitleCase method is unused in Helpers/StringHelper.cs |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | AI review identifies JoinWithSeparatorFixed is a duplicate of standard library functionality in Helpers/StringHelper.cs |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | AI review doesn't specifically identify this anti-pattern |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | AI review identifies Regex instantiated inside method call in Helpers/StringHelper.cs |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | AI review identifies string concatenation in loop for JoinWithSeparator in Helpers/StringHelper.cs |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Partial | AI review doesn't specifically identify this anti-pattern |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | AI review identifies IsBlank method is unused in Helpers/StringHelper.cs |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | AI review identifies leaking connection in DatabaseHelper.cs |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | AI review identifies hardcoded database credentials (sa/Password) in DatabaseHelper.cs |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | AI review doesn't specifically identify this configuration issue |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | AI review identifies JWT lifetime validation disabled (ValidateLifetime = false) in Program.cs |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | AI review identifies HTTPS redirection is commented out in Program.cs |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | AI review identifies Developer exception page enabled for production in Program.cs |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | AI review identifies open CORS policy allows any origin, method, and header in Program.cs |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | AI review identifies DebugSymbols and DebugType set to true for release builds in SampleBankingApp.csproj |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | AI review doesn't specifically identify this outdated package |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | AI review doesn't specifically identify this missing configuration file |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | **Missing Unit Tests** — The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper` — all missing tests. | Found | AI review identifies no test project exists in the repository and recommends creating tests for key areas |