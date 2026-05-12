# AI Review Scorecard

> **Branch:** `Qwen3.5-4B` &nbsp;·&nbsp; **Commit:** `fa9bd2e`

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | SQL injection via string interpolation in tableName and whereClause. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | MD5 hashing for passwords is cryptographically weak. |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | MD5 hashing for passwords is cryptographically weak. |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | SQL injection in login query using string interpolation. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | SQL injection via string interpolation in tableName and whereClause. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | SQL injection via string interpolation in tableName and whereClause. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | SQL injection via string interpolation in tableName and whereClause. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Hardcoded fallback password in constructor. |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | JWT ValidateLifetime set to false allows expired tokens. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | Overly permissive CORS policy allows any origin/method. |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | Overly permissive CORS policy allows any origin/method. |

## Logic Errors

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | String concatenation in loop causes O(n^2) performance. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | GetOpenConnection returns connection without disposing. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | userIdClaim parsing assumes valid int without validation. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | String concatenation in loop causes O(n^2) performance. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | userIdClaim parsing assumes valid int without validation. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | String concatenation in loop causes O(n^2) performance. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | String concatenation in loop causes O(n^2) performance. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | GetOpenConnection returns connection without disposing. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Catch Exception returns raw message to client. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Login returns null on failure without transaction safety. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | jwtSecret null check bypass with ! operator. |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Found | jwtSecret null check bypass with ! operator. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Catch Exception returns raw message to client. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | GetOpenConnection returns connection without disposal. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | Overly permissive CORS policy allows any origin/method. |

## Resource Leaks

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | SqlConnection created without using block in Login method. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | GetOpenConnection returns connection without disposal. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | GetOpenConnection returns connection without disposal. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Overly permissive CORS policy allows any origin/method. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Overly permissive CORS policy allows any origin/method. |

## Missing Null Checks

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | jwtSecret null check bypass with ! operator. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | userIdClaim parsing assumes valid int without validation. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | Overly permissive CORS policy allows any origin/method. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | LoginRequest properties allow empty strings. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | email.Length accessed without null check. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | userIdClaim parsing assumes valid int without validation. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | LoginRequest properties allow empty strings. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | 254 used for email length limit. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | 3 and 20 used for username length limits. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Hardcoded DB credentials. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | 254 used for email length limit. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | 3 and 20 used for username length limits. |

## Dead Code

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | JoinWithSeparator is dead code compared to JoinWithSeparatorFixed. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | JoinWithSeparator is dead code compared to JoinWithSeparatorFixed. |
| D3 | `TableExists` — never called from any service or controller. | Found | ExecuteQueryWithParams marked Obsolete but might be called. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | ExecuteQueryWithParams marked Obsolete but might be called. |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | JoinWithSeparator is dead code compared to JoinWithSeparatorFixed. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | JoinWithSeparator is dead code compared to JoinWithSeparatorFixed. |
| D7 | `FormatCurrency` — private, never called. | Found | JoinWithSeparator is dead code compared to JoinWithSeparatorFixed. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | JoinWithSeparator is dead code compared to JoinWithSeparatorFixed. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | JoinWithSeparator is dead code compared to JoinWithSeparatorFixed. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | JoinWithSeparator is dead code compared to JoinWithSeparatorFixed. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | JoinWithSeparator is dead code compared to JoinWithSeparatorFixed. |

## Anti-patterns

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | GetOpenConnection returns connection without disposal. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Regex created inside method instead of static readonly. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | String concatenation in loop causes O(n^2) performance. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Overly permissive CORS policy allows any origin/method. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | String concatenation in loop causes O(n^2) performance. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | GetOpenConnection returns connection without disposal. |

## Configuration Issues

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Hardcoded fallback password in constructor. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | UseDeveloperExceptionPage enabled in production. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | JWT ValidateLifetime set to false allows expired tokens. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | app.UseHttpsRedirection commented out. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | UseDeveloperExceptionPage enabled in production. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Overly permissive CORS policy allows any origin/method. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | Debug symbols enabled in release build. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | Newtonsoft.Json version 12.0.3 is outdated. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Overly permissive CORS policy allows any origin/method. |

## Missing Unit Tests

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| UT | **Missing Unit Tests** — The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, and controller action results. | Found | Login method needs boundary tests for null/empty inputs. |