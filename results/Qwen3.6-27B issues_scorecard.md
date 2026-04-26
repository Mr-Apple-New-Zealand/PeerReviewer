# AI Review Scorecard

> **Branch:** `Qwen3.6-27B` &nbsp;·&nbsp; **Commit:** `cd2e1f4`

# AI Review Scorecard

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | `AuthService.cs` line 38 uses string interpolation for SQL query construction. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | `AuthService.cs` line 22 contains hardcoded admin bypass password. |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | `AuthService.cs` line 68 uses MD5 hashing without salt. |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | `UserService.cs` lines 38 and 48 use string interpolation for SQL updates. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | `UserService.cs` line 88 interpolates query into LIKE clause. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | `TransactionService.cs` lines 50 and 64 use string concatenation for SQL updates. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | `TransactionService.cs` line 78 interpolates description into INSERT statement. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | `DatabaseHelper.cs` line 18 and `appsettings.json` contain hardcoded credentials. |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | `Program.cs` line 28 disables JWT lifetime validation. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | `UserController.cs` lines 28 lack ownership validation for update operations. |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | `UserController.cs` line 28 lacks authorization checks for delete operations. |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | `TransactionService.cs` line 48 checks `amount < 0` instead of `<= 0`. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | `TransactionService.cs` line 48 compares balance to amount instead of total debit. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | `UserService.cs` line 68 calculates skip incorrectly as `page * pageSize`. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | `TransactionService.cs` line 62 uses 5% interest rate instead of 1%. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | `TransactionService.cs` line 38 does not check for self-transfer. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | `UserService.cs` lines 20, 38, 54 all contain duplicated validation logic. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | `StringHelper.cs` line 28 uses inefficient string concatenation in loop. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | `AuthService.cs` line 82 has a long method that could be broken into smaller helpers. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | `UserService.cs` line 88 catches all exceptions and returns empty list. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | `EmailService.cs` line 68 catches generic Exception and discards it. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | `TransactionService.cs` line 40 does not wrap database updates in a transaction. |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | `TransactionService.cs` line 56 sends email after database commit. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | `UserController.cs` line 48 exposes raw exception message to client. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | `DatabaseHelper.cs` line 48 closes connection only on success path. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | `AuthService.cs` line 38 does not implement rate limiting or account lockout. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | `AuthService.cs` lines 42-43 open resources without disposal. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | `DatabaseHelper.cs` line 22 returns open connection without disposal contract. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | `DatabaseHelper.cs` line 48 closes but does not dispose connection. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | `EmailService.cs` line 22 holds SmtpClient as instance field. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | `EmailService.cs` lines 48 and 72 create MailMessage without disposal. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | `Program.cs` line 22 force-unpacks potentially null config value. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | `TransactionService.cs` lines 44 and 45 access Rows without count check. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | `EmailService.cs` line 28 uses fallback for potentially missing config. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | `EmailService.cs` line 68 accesses username without null check. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | `StringHelper.cs` lines 12 and 20 access Length without null check. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | `TransactionController.cs` lines 28 and 38 force-unpack potentially null claims. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | `UserController.cs` line 28 does not check for null request body. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | `TransactionService.cs` lines 13-14 define constants that should be configurable. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | `TransactionService.cs` line 62 hardcodes deposit cap. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | `EmailService.cs` lines 14-15, 49, 72 hardcode email addresses. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | `StringHelper.cs` lines 12, 20 use bare literals for validation. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | `UserService.cs` line 66 hardcodes page size limit. |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | `AuthService.cs` line 88 defines unused SHA1 method. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | `AuthService.cs` line 98 contains unreachable code. |
| D3 | `TableExists` — never called from any service or controller. | Found | `DatabaseHelper.cs` line 58 defines unused method. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | `DatabaseHelper.cs` line 62 defines obsolete method. |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | `EmailService.cs` line 78 defines unused private method. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | `EmailService.cs` line 78 defines unused public method. |
| D7 | `FormatCurrency` — private, never called. | Found | `TransactionService.cs` line 82 defines unused method. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | `TransactionService.cs` line 72 defines unused method. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | `StringHelper.cs` line 49 defines unused method. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | `StringHelper.cs` line 54 defines unused method. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | `StringHelper.cs` lines 34-37 define unused fixed version. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | `UserService.cs` lines 12-13 define static mutable state. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | `StringHelper.cs` lines 14 and 24 create Regex per call. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | `StringHelper.cs` line 28 uses string concatenation in loop. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | `EmailService.cs` line 22 holds SmtpClient as instance field. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | `StringHelper.cs` line 58 reimplements built-in method. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | `DatabaseHelper.cs` line 22 returns open connection without contract. |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | `appsettings.json` contains production secrets. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | `appsettings.json` line 18 sets debug log levels. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | `Program.cs` line 28 disables JWT lifetime validation. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | `Program.cs` line 35 comments out HTTPS redirection. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | `Program.cs` line 33 unconditionally calls developer exception page. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | `Program.cs` line 38 allows any origin/method/header. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | `SampleBankingApp.csproj` lines 8-10 enable debug symbols. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | `SampleBankingApp.csproj` line 14 pins outdated package. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Missing environment-specific configuration files. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project exists in the repository. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results. | Found | The repository contains no test project or test files. |