# AI Review Scorecard

> **Branch:** `Codestral-22B` &nbsp;·&nbsp; **Commit:** `9980e6e`

Total: 20 Found / 50 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review mentions "SQL injection vulnerabilities" in DatabaseHelper.cs |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review mentions "Magic string (AdminBypassPassword)" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review mentions "Weak cryptography (MD5)" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Partial | Review mentions "SQL injection vulnerabilities" but doesn't name specific methods |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Partial | Review mentions "SQL injection vulnerabilities" but doesn't name specific methods |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Partial | Review mentions "SQL injection vulnerabilities" but doesn't name specific methods |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Partial | Review mentions "SQL injection vulnerabilities" but doesn't name specific methods |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review mentions "Hardcoded credentials in source file" and "Hardcoded credentials in configuration file" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review mentions "JWT misconfiguration (ValidateLifetime set to false)" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Partial | Review mentions "Missing authorization attributes on endpoints" but doesn't name specific endpoint |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Partial | Review mentions "Missing authorization attributes on endpoints" but doesn't name specific endpoint |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Review mentions "Incorrect boundary conditions for transfer amount (>= 0)" |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Partial | Review mentions "Incorrect boundary conditions for deposit amount" but doesn't name specific logic error |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review mentions "Off-by-one error in pagination (page * pageSize)" |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | Review mentions "Incorrect boundary conditions for deposit amount" but doesn't name specific logic error |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Partial | Review mentions "Missing authorization attributes on endpoints" but doesn't name specific logic error |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | Review mentions "Duplicated validation logic in UpdateUser() and DeleteUser()" but doesn't name specific refactoring opportunity |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Partial | Review mentions "Reimplementing string concatenation inside a loop" but doesn't name specific method |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | Review mentions "JWT misconfiguration" but doesn't name specific refactoring opportunity |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Partial | Review mentions "Swallowing exceptions in search method" but doesn't name specific method |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | Review mentions "Catching broad Exception and swallowing it silently" but doesn't name specific method |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Partial | Review mentions "TransactionService.cs" but doesn't name specific error handling issue |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Partial | Review mentions "TransactionService.cs" but doesn't name specific error handling issue |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Partial | Review mentions "Catching broad Exception and returning a generic error message" but doesn't name specific method |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Partial | Review mentions "Not closing or disposing SqlConnection and SqlDataAdapter" but doesn't name specific method |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | Review mentions "Missing authorization attributes on endpoints" but doesn't name specific method |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Partial | Review mentions "Not closing or disposing SqlConnection and SqlDataAdapter" but doesn't name specific method |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Partial | Review mentions "Not closing or disposing SqlConnection and SqlDataAdapter" but doesn't name specific method |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Partial | Review mentions "Not closing or disposing SqlConnection and SqlDataAdapter" but doesn't name specific method |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Partial | Review mentions "Not closing or disposing SmtpClient" but doesn't name specific method |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Partial | Review mentions "Leaking resource ownership to callers" but doesn't name specific method |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Partial | Review mentions "Using configuration.GetConnectionString() without null check" but doesn't name specific method |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Partial | Review mentions "Using user input (id) without validation or null check" but doesn't name specific method |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | Review mentions "Using configuration values without null checks" but doesn't name specific method |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | Review mentions "Using string.Length without null check" but doesn't name specific method |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | Review mentions "Using string.Length without null check" but doesn't name specific method |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Partial | Review mentions "Using User.FindFirst() without null check" but doesn't name specific method |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | Review mentions "Using user input (id) without validation or null check" but doesn't name specific method |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review mentions "Magic numbers (0.015, 10)" |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Partial | Review mentions "Incorrect boundary conditions for deposit amount" but doesn't name specific method |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Review mentions "Magic strings (email subjects)" |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Partial | Review mentions "Magic strings (email subjects)" but doesn't name specific method |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Review mentions "Magic number (50)" |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Partial | Review mentions "Obsolete method ExecuteQueryWithParams()" but doesn't name specific method |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Partial | Review mentions "NotImplementedException in RefundTransaction()" but doesn't name specific method |
| D3 | `TableExists` — never called from any service or controller. | Partial | Review mentions "Obsolete method ExecuteQueryWithParams()" but doesn't name specific method |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review mentions "Obsolete method ExecuteQueryWithParams()" |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Partial | Review mentions "Leaking resource ownership to callers" but doesn't name specific method |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Partial | Review mentions "Leaking resource ownership to callers" but doesn't name specific method |
| D7 | `FormatCurrency` — private, never called. | Partial | Review mentions "NotImplementedException in RefundTransaction()" but doesn't name specific method |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Partial | Review mentions "NotImplementedException in RefundTransaction()" but doesn't name specific method |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Partial | Review mentions "Reimplementing string concatenation inside a loop" but doesn't name specific method |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Partial | Review mentions "Reimplementing string concatenation inside a loop" but doesn't name specific method |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Partial | Review mentions "Reimplementing string concatenation inside a loop" but doesn't name specific method |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | Review mentions "Duplicated validation logic" but doesn't name specific anti-pattern |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Partial | Review mentions "Reimplementing string concatenation inside a loop" but doesn't name specific method |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review mentions "Reimplementing string concatenation inside a loop" |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Partial | Review mentions "Not closing or disposing SmtpClient" but doesn't name specific method |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Partial | Review mentions "Reimplementing string concatenation inside a loop" but doesn't name specific method |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Partial | Review mentions "Not closing or disposing SqlConnection and SqlDataAdapter" but doesn't name specific method |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review mentions "Hardcoded credentials in source file" and "Hardcoded credentials in configuration file" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | Review mentions "Outdated or vulnerable NuGet packages" but doesn't name specific configuration issue |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review mentions "JWT misconfiguration (ValidateLifetime set to false)" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review mentions "HTTPS disabled" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review mentions "Developer exception pages in production" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review mentions "Overly permissive CORS policy" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Partial | Review mentions "Outdated or vulnerable NuGet packages" but doesn't name specific configuration issue |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | Review mentions "Outdated or vulnerable NuGet packages" |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Review mentions "Missing environment-specific config overrides" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, controller action results. | Found | Review mentions "The source code does not include a test project" and lists key areas needing tests |