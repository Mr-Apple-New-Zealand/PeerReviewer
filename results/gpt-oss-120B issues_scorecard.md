# AI Review Scorecard

> **Branch:** `gpt-oss-120B` &nbsp;·&nbsp; **Commit:** `4d1f610`

# AI Review Scorecard

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | `AuthService.cs` | 30‑33 | SQL injection: username and hashed password interpolated into raw SQL. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | `AuthService.cs` | 23 | Hard‑coded admin bypass password (`SuperAdmin2024`). |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | `AuthService.cs` | 45‑48 | MD5 used for password hashing (weak, unsalted). |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | `UserService.cs` | 57‑60 | `UpdateUser` builds UPDATE with raw email/username strings. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | `UserService.cs` | 92‑95 | `SearchUsers` builds WHERE clause with raw `query` → SQL injection. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | `TransactionService.cs` | 45‑48 | `ExecuteNonQuery` with interpolated balances allows SQL injection if values are tampered. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | `TransactionService.cs` | 71‑73 | `RecordTransaction` builds INSERT with raw description, possible injection. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | `appsettings.json` | 9‑13 | Plain‑text DB password, JWT secret, and email password committed to source. |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | `Program.cs` | 31 | `ValidateLifetime = false` disables JWT expiration checks. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | `UserController.cs` | 53 | No check that the caller owns the account; any user can overwrite any other user's profile. |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | `UserController.cs` | 67 | No role check; any authenticated user can delete any account. |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | `TransactionService.cs` | 38‑44 | Fee is added to debit but balance check uses only `amount`, allowing overdraft after fee. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | `TransactionService.cs` | 57‑58 | `newFromBalance` may become negative if fee > available balance. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | `UserService.cs` | 106‑108 | Pagination offset calculated as `page * pageSize`; should be `(page‑1) * pageSize`. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | `TransactionService.cs` | 68‑70 | `interestBonus = amount * 0.05m * 1` – extra `* 1` is unnecessary but harmless. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | `TransactionController.cs` | 26 | No check that `fromUserId != request.ToUserId`. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | `UserService.cs` | 15–16 | Mutable static state — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | `StringHelper.cs` | 28‑31 | `JoinWithSeparator` builds string via repeated concatenation (O(n²)). |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | `AuthService.cs` | 84‑90 | Unreachable code after `return true;` – intended validation never runs. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | `UserService.cs` | 124‑128 | `SearchUsers` catches all exceptions and returns empty list, hiding errors. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | `EmailService.cs` | 61‑68 | Generic `catch (Exception)` logs to console and swallows error. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | `TransactionService.cs` | 38‑84 | No try/catch around DB updates; any failure bubbles up as 500. |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | `TransactionService.cs` | 86‑92 | Email send failures are not caught; could cause unhandled exception after DB commit. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | `UserController.cs` | 58 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | `DatabaseHelper.cs` | 45‑50 | `ExecuteNonQuery` disposes connection but not `SqlCommand`. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | `AuthController.cs` | 20 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | `AuthService.cs` | 30‑48 | `SqlConnection` and `SqlCommand` are never disposed; any exception leaks resources. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | `DatabaseHelper.cs` | 21‑27 | `SqlConnection`, `SqlCommand`, `SqlDataAdapter` not disposed in `ExecuteQuery`. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | `DatabaseHelper.cs` | 33‑38 | `SqlCommand` not disposed in `ExecuteNonQuery`. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | `EmailService.cs` | 24‑27 | `SmtpClient` stored as a singleton field (not thread‑safe). |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | `EmailService.cs` | 44‑48, 61‑66, 78‑82 | `MailMessage` objects are not disposed. |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | `Program.cs` | 31 | `builder.Configuration["Jwt:SecretKey"]` may be null; `Encoding.UTF8.GetBytes` would throw. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | `TransactionService.cs` | 45‑48 | `fromUserTable.Rows[0]` assumes a row exists; if user not found, throws. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | `EmailService.cs` | 17‑20 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | `EmailService.cs` | 68 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | `StringHelper.cs` | 12‑14, 20‑22 | `IsValidEmail` does not check for null before `email.Length`. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | `TransactionController.cs` | 24‑27 | `int.Parse(userIdClaim!)` will throw if claim missing; no error handling. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | `UserController.cs` | 28 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | `TransactionService.cs` | 14‑15 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` hard‑coded. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | `TransactionService.cs` | 60 | `1_000_000` deposit cap hardcoded inline — no named constant. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | `EmailService.cs` | 14–15, 49, 72 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | `StringHelper.cs` | 14, 24 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | `UserService.cs` | 69 | Page size capped at 50 inline. |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | `AuthService.cs` | 71‑78 | `HashPasswordSha1` never called. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | `AuthService.cs` | 84‑90 | Code after `return true;` is unreachable. |
| D3 | `TableExists` — never called from any service or controller. | Found | `DatabaseHelper.cs` | 49 | `TableExists` uses `using` for connection but not for `DataTable`; fine, but could be wrapped. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | `DatabaseHelper.cs` | 57‑66 | `ExecuteQueryWithParams` marked `[Obsolete]` but still present; not used anywhere. |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | `EmailService.cs` | 79 | `BuildHtmlTemplate` only used by `SendWelcomeEmailHtml`; acceptable but could be inlined. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | `EmailService.cs` | 85 | `SendWelcomeEmailHtml` — public method, never registered or called. |
| D7 | `FormatCurrency` — private, never called. | Found | `TransactionService.cs` | 91 | `FormatCurrency` never used. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | `TransactionService.cs` | 91 | `IsWithinDailyLimit` is never called, so daily‑limit rule is ineffective. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | `StringHelper.cs` | 49 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | `StringHelper.cs` | 54 | `ToTitleCase` — "experimental utility never integrated", never called. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | `StringHelper.cs` | 37 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | `UserService.cs` | 5‑7 | Static mutable fields `_auditLog` and `_requestCount` are not thread-safe. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | `StringHelper.cs` | 12‑14, 20‑22 | New `Regex` created on each call. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | `StringHelper.cs` | 28‑30 | `JoinWithSeparator` builds string via repeated concatenation (O(n²)). |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | `EmailService.cs` | 24‑27 | `SmtpClient` stored as field (not thread‑safe). |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | `StringHelper.cs` | 60 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | `DatabaseHelper.cs` | 26 | `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | `appsettings.json` | 9‑13 | Plain‑text DB password, JWT secret, and email password committed to source. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | `appsettings.json` | 23‑27 | Logging level set to `Debug` for all categories in production. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | `Program.cs` | 31 | `ValidateLifetime = false` disables JWT expiration checks. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | `Program.cs` | 42 | HTTPS redirection commented out. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | `Program.cs` | 38 | `UseDeveloperExceptionPage()` always enabled (exposes stack traces). |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | `Program.cs` | 41 | CORS policy `AllowAnyOrigin/AllowAnyMethod/AllowAnyHeader` is overly permissive. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | `SampleBankingApp.csproj` | 7–10 | `DebugSymbols = true` / `DebugType = full` always emitted — PDB files shipped with release builds. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | `SampleBankingApp.csproj` | 14 | `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | *(missing)* | — | No `appsettings.Production.json` — no environment-specific overrides; production uses the same unsafe defaults. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, and controller action results. | Found | **No test project found** | N/A | Critical business logic lacks automated verification. |