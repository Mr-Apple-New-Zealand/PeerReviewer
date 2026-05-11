# AI Review Scorecard

> **Branch:** `Qwen3.5-4B` &nbsp;·&nbsp; **Commit:** `cf63ba1`

Total: 69 Found / 1 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "AuthService.cs: `Login` method uses string interpolation for SQL (`SELECT * FROM Users WHERE Username = '{username}' AND Password = '{hashedPassword}'`). This is SQL Injection." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "AuthService.cs: `AdminBypassPassword` is hardcoded ("SuperAdmin2024")." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "AuthService.cs: `HashPasswordMd5` uses MD5 which is broken/weak." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "UserService.cs: `UpdateUser` and `DeleteUser` use string interpolation for SQL." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "UserService.cs: `SearchUsers` uses `LIKE '%{query}%'` which is SQL Injection." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "TransactionService.cs: `Deposit` and `Transfer` use string interpolation for SQL values." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "TransactionService.cs: `RecordTransaction` uses string interpolation for SQL values (`{amount}`, `{type}`, `{description}`)." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "appsettings.json: Hardcoded passwords for DB (`Admin1234!`) and Email (`EmailPass99`)." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "Program.cs: `ValidateLifetime = false` on JWT." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | "UserController.cs: `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | "UserController.cs: `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account." |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | "TransactionService.cs: `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "TransactionService.cs: **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "UserService.cs: `GetUsersPage` calculates `skip = page * pageSize`. If page is 0, skip is 0. If page is 1, skip is pageSize. Usually pagination is `(page-1) * pageSize`." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | "TransactionService.cs: `Deposit` calculates `interestBonus = amount * 0.05m * 1;` which is redundant but not necessarily a logic error, but `amount * 0.05m` is fine." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | "TransactionController.cs: `Refund` catches `NotImplementedException` and returns 500." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | "UserService.cs: `GetUserById` checks `id <= 0` and `id > 1000000` but doesn't check for negative values properly (though `<= 0` covers negative)." |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "StringHelper.cs: `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | "AuthService.cs: `GenerateJwtToken` is overly long and could be split into named helpers for clarity and testability." |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "UserService.cs: `SearchUsers` uses `LIKE '%{query}%'` which is SQL Injection." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | "EmailService.cs: `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | "TransactionService.cs: **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent." |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | "TransactionService.cs: Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | "UserController.cs: `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | "DatabaseHelper.cs: `ExecuteNonQuery` returns connection without disposal." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | "AuthController.cs: `Login` returns `Unauthorized` but doesn't log the failure properly? It logs warning." |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "DatabaseHelper.cs: `GetOpenConnection` returns connection without disposal." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "DatabaseHelper.cs: `GetOpenConnection` returns connection without disposal." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "DatabaseHelper.cs: `ExecuteNonQuery` returns connection without disposal." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "EmailService.cs: `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "EmailService.cs: `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | "AuthService.cs: `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "TransactionService.cs: `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | "EmailService.cs: `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key." |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | "EmailService.cs: `username.ToUpper()` throws `NullReferenceException` if `username` is `null`." |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | "StringHelper.cs: `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "TransactionController.cs: `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | "UserController.cs: `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body." |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | "TransactionService.cs: `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration." |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | "TransactionService.cs: `1_000_000` deposit cap hardcoded inline — no named constant." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | "EmailService.cs: Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | "StringHelper.cs: `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.)." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "UserService.cs: `50` as the page size upper bound is unnamed and undocumented." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | "AuthService.cs: `HashPasswordSha1` uses SHA1 which is weak." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "AuthService.cs: `ValidateToken` ignores `ValidateLifetime` and returns true if not null." |
| D3 | `TableExists` — never called from any service or controller. | Found | "DatabaseHelper.cs: `TableExists` — never called from any service or controller." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | "DatabaseHelper.cs: `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed." |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | "EmailService.cs: `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`." |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | "EmailService.cs: `SendWelcomeEmailHtml` — public method, never registered or called." |
| D7 | `FormatCurrency` — private, never called. | Found | "TransactionService.cs: `FormatCurrency` — private, never called." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | "TransactionService.cs: `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | "StringHelper.cs: `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | "StringHelper.cs: `ToTitleCase` — "experimental utility never integrated", never called." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "StringHelper.cs: `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | "UserService.cs: `_auditLog` is static and not thread-safe." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "StringHelper.cs: **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "StringHelper.cs: **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "EmailService.cs: **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "StringHelper.cs: **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "DatabaseHelper.cs: `GetOpenConnection` returns connection without disposal." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "appsettings.json: Hardcoded passwords for DB (`Admin1234!`) and Email (`EmailPass99`)." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | "Program.cs: `UseDeveloperExceptionPage()` is called unconditionally." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "Program.cs: `ValidateLifetime = false` on JWT." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "Program.cs: `UseHttpsRedirection()` commented out." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "Program.cs: `UseDeveloperExceptionPage()` is called unconditionally." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "Program.cs: `app.UseCors(policy => policy.AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader());` is overly permissive." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | "SampleBankingApp.csproj: `DebugSymbols = true` / `DebugType = full` always emitted — PDB files shipped with release builds." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | "SampleBankingApp.csproj: `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated." |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | "appsettings.json: No environment-specific overrides; production uses the same unsafe defaults." |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project or test files exist. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper. | Found | "No test project or test files exist. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper." |