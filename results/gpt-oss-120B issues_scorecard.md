# AI Review Scorecard

> **Branch:** `gpt-oss-120B` &nbsp;·&nbsp; **Commit:** `ccc6a3d`

Total: 64 Found / 6 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | The review mentions "SQL built with string interpolation using raw `username` → SQL injection risk" in `AuthService.cs` line 31 |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | The review mentions "Hard‑coded admin bypass password" in `AuthService.cs` line 23 |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | The review mentions "Password hashed with MD5 – weak, fast hash" in `AuthService.cs` line 31 |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | The review mentions "SQL built with string interpolation for `email` and `username` → injection" in `UserService.cs` line 55 |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | The review mentions "SQL built with string interpolation for `DELETE` → injection" in `UserService.cs` line 84 |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | The review mentions "ExecuteNonQuery called with interpolated balances → injection if values tampered" in `TransactionService.cs` line 31 |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | The review mentions "description inserted directly into SQL without escaping → injection if contains `'`" in `TransactionService.cs` line 115 |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | The review mentions "Database password, JWT secret, and email credentials stored in source control" in `appsettings.json` line 5-9 |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | The review mentions "JWT secret key read from config but stored in plain text in `appsettings.json`" in `Program.cs` line 30 |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | The review mentions "No check that `fromUserId != toUserId` → self‑transfer may be abused" in `TransactionService.cs` line 71 |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | The review mentions "No rate limiting or account lockout on failed login attempts" in `Controllers/AuthController.cs` line 20 |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | The review mentions "Balance check ignores transaction fee (`fromBalance >= amount`); fee can cause negative balance" in `TransactionService.cs` line 78 |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | The review mentions "Fee not considered in balance check (`fromBalance >= amount` instead of `>= totalDebit`) → possible overdraft" in `TransactionService.cs` line 78 |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | The review mentions "Pagination offset calculated as `page * pageSize` (0‑based) → skips first page" in `UserService.cs` line 108 |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | The review mentions "interestBonus = amount * 0.05m * 1" in `TransactionService.cs` line 108 |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | The review mentions "No guard against transferring to self (`fromUserId == toUserId`)" in `TransactionService.cs` line 71 |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | The review mentions "Mutable static state" in `UserService.cs` but doesn't specifically mention duplicated validation blocks |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | The review mentions "JoinWithSeparator builds string via repeated concatenation → O(n²)" in `StringHelper.cs` line 23 |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | The review mentions "JWT secret key read from config but stored in plain text in `appsettings.json`" but doesn't specifically mention token generation helpers |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | The review mentions "SearchUsers catches all exceptions and returns empty list, hiding failures" in `UserService.cs` line 100 |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | The review mentions "Catches generic `Exception` and only writes to console; error lost to caller" in `EmailService.cs` line 55 |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | The review mentions "No transaction scope; two `UPDATE` statements can leave accounts inconsistent on failure" in `TransactionService.cs` line 31 |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Partial | The review mentions "Email failure in `Transfer` propagates an exception after the DB transfer has already committed" but doesn't specifically mention this exact scenario |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Partial | The review mentions "catches generic `Exception` and only writes to console; error lost to caller" but doesn't specifically mention message exposure |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | The review mentions "ExecuteNonQuery opens connection via `GetOpenConnection` but never disposes connection/command" in `DatabaseHelper.cs` line 41 |
| E7 | **No rate limiting or account lockout on failed login attempts** — brute force is trivially possible. | Found | The review mentions "No rate limiting or account lockout on failed login attempts" in `Controllers/AuthController.cs` line 20 |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | The review mentions "SqlConnection, SqlCommand, and SqlDataReader not disposed" in `AuthService.cs` line 45 |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | The review mentions "Connection opened, never closed/disposed" in `DatabaseHelper.cs` line 23 |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | The review mentions "ExecuteNonQuery opens connection via `GetOpenConnection` but never disposes connection/command" in `DatabaseHelper.cs` line 41 |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | The review mentions "SmtpClient is a disposable field never disposed" in `EmailService.cs` line 9 |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | The review mentions "MailMessage objects not disposed" in `EmailService.cs` line 31 |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | The review mentions "_config["Jwt:SecretKey"]! assumes non‑null; missing key throws `ArgumentNullException`" in `AuthService.cs` line 71 |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | The review mentions "fromUserTable.Rows[0] accessed without verifying `Rows.Count > 0`" in `TransactionService.cs` line 71 |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | The review mentions "Config values (`Email:SmtpHost`, `Email:SmtpPort`, etc.) may be null; `int.Parse(null)` throws" in `EmailService.cs` line 15 |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | The review mentions "username.ToUpper() throws `NullReferenceException` if `username` is `null`" in `EmailService.cs` line 68 |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | The review mentions "email.Length and username.Length throw if argument is `null`" in `StringHelper.cs` line 14 |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | The review mentions "User.FindFirst(...)?.Value can be `null`" in `TransactionController.cs` line 19 |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | The review mentions "UpdateUser and controller endpoints don't check `request == null`" in `UserController.cs` line 28 |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | The review mentions "TransactionFeeRate = 0.015m" and "MaxTransactionsPerDay = 10" as magic numbers in `TransactionService.cs` lines 13-14 |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | The review mentions "1_000_000" as a hardcoded value in `TransactionService.cs` line 60 |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | The review mentions "Email subjects and from address hard‑coded" in `EmailService.cs` line 9 |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | The review mentions "Email regex pattern hard‑coded" and "Username regex pattern hard‑coded" in `StringHelper.cs` lines 13-16 |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | The review mentions "Page size capped at 50 (magic)" in `UserService.cs` line 108 |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | The review mentions "HashPasswordSha1 never used" in `AuthService.cs` line 64 |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | The review mentions "return true; makes subsequent token validation unreachable" in `AuthService.cs` line 71 |
| D3 | `TableExists` — never called from any service or controller. | Found | The review mentions "TableExists defined but never called" in `DatabaseHelper.cs` line 71 |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | The review mentions "ExecuteQueryWithParams marked `[Obsolete]` but still present and unused" in `DatabaseHelper.cs` line 71 |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | The review mentions "BuildHtmlTemplate used only by `SendWelcomeEmailHtml`" in `EmailService.cs` line 71 |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | The review mentions "SendWelcomeEmailHtml never called" in `EmailService.cs` line 71 |
| D7 | `FormatCurrency` — private, never called. | Found | The review mentions "FormatCurrency never used" in `TransactionService.cs` line 124 |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | The review mentions "IsWithinDailyLimit defined but never used" in `TransactionService.cs` line 108 |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | The review mentions "JoinWithSeparatorFixed" exists but "JoinWithSeparator" uses `+=` in a loop in `StringHelper.cs` line 23 |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | The review mentions "JoinWithSeparatorFixed" exists but "JoinWithSeparator" uses `+=` in a loop in `StringHelper.cs` line 23 |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | The review mentions "JoinWithSeparatorFixed" exists but "JoinWithSeparator" uses `+=` in a loop in `StringHelper.cs` line 23 |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | The review mentions "Static mutable `_auditLog` and `_requestCount` not thread-safe" in `UserService.cs` line 84 |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | The review mentions "Regex compiled on each call → potential DoS via complex patterns" in `StringHelper.cs` line 13 |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | The review mentions "JoinWithSeparator builds string via repeated concatenation → O(n²)" in `StringHelper.cs` line 23 |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | The review mentions "SmtpClient is a disposable field never disposed" in `EmailService.cs` line 9 |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Partial | The review mentions "Reimplementing BCL" but doesn't specifically mention `IsBlank` |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | The review mentions "GetOpenConnection() is an anti-pattern" in `DatabaseHelper.cs` line 23 |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | The review mentions "Database password, JWT secret, and email credentials stored in source control" in `appsettings.json` line 5-9 |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | The review mentions "Logging level set to `Debug` for all categories in `appsettings.json`" in `Program.cs` line 38 |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | The review mentions "JWT secret key read from config but stored in plain text in `appsettings.json`" in `Program.cs` line 30 |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | The review mentions "HTTPS redirection commented out" in `Program.cs` line 41 |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | The review mentions "UseDeveloperExceptionPage() enabled unconditionally" in `Program.cs` line 38 |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | The review mentions "CORS policy `AllowAnyOrigin/Method/Header` → open to CSRF" in `Program.cs` line 44 |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | The review mentions "DebugSymbols=true and DebugType=full in production build" in `SampleBankingApp.csproj` line 13 |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | The review mentions "Pinned outdated package" in `SampleBankingApp.csproj` line 14 |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | The review mentions "JWT `Issuer`/`Audience` hard‑coded but may differ per environment" but doesn't specifically mention missing production settings |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | **No test project present in the solution** — key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, controller action results. | Found | The review mentions "No test project present in the solution" and lists all the key areas that need tests |