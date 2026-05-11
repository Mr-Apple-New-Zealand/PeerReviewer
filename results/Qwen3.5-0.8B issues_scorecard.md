# AI Review Scorecard

> **Branch:** `Qwen3.5-0.8B` &nbsp;·&nbsp; **Commit:** `266155c`

Total: 13 Found / 57 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review identifies hardcoded credentials in appsettings.json which enables SQL injection through direct string interpolation |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review identifies hardcoded credentials in appsettings.json including a superadmin password |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review identifies hardcoded credentials including a weak password hash in appsettings.json |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Review identifies hardcoded credentials in appsettings.json which enables SQL injection through direct string interpolation |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | Review identifies hardcoded credentials in appsettings.json which enables SQL injection through direct string interpolation |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Review identifies hardcoded credentials in appsettings.json which enables SQL injection through direct string interpolation |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Review identifies hardcoded credentials in appsettings.json which enables SQL injection through direct string interpolation |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review identifies hardcoded credentials in appsettings.json including DB password, JWT secret, and SMTP credentials |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review identifies hardcoded JWT secret in appsettings.json which enables token lifetime validation issues |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Partial | Review mentions hardcoded credentials but doesn't specifically address access control issues |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Partial | Review mentions hardcoded credentials but doesn't specifically address authorization issues |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Partial | Review doesn't mention specific logic errors in amount validation |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Partial | Review doesn't mention specific logic errors in balance checking |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Partial | Review doesn't mention specific pagination logic errors |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | Review doesn't mention specific interest rate logic errors |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Partial | Review doesn't mention specific self-transfer logic errors |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | Review doesn't mention specific code duplication issues |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Partial | Review doesn't mention specific string concatenation issues |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | Review doesn't mention specific JWT token generation issues |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Partial | Review doesn't mention specific exception handling issues |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | Review doesn't mention specific exception handling issues |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Partial | Review doesn't mention specific transaction handling issues |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Partial | Review doesn't mention specific error propagation issues |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Partial | Review doesn't mention specific error message exposure issues |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Partial | Review doesn't mention specific connection handling issues |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | Review doesn't mention specific rate limiting issues |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Partial | Review doesn't mention specific resource leak issues |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Partial | Review doesn't mention specific resource leak issues |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Partial | Review doesn't mention specific resource leak issues |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Partial | Review doesn't mention specific resource leak issues |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Partial | Review doesn't mention specific resource leak issues |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Partial | Review doesn't mention specific null check issues |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Partial | Review doesn't mention specific null check issues |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | Review doesn't mention specific null check issues |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | Review doesn't mention specific null check issues |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | Review doesn't mention specific null check issues |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Partial | Review doesn't mention specific null check issues |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | Review doesn't mention specific null check issues |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Partial | Review doesn't mention specific magic number issues |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Partial | Review doesn't mention specific magic number issues |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | Review doesn't mention specific magic string issues |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Partial | Review doesn't mention specific magic string issues |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Partial | Review doesn't mention specific magic number issues |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Partial | Review doesn't mention specific dead code issues |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Partial | Review doesn't mention specific dead code issues |
| D3 | `TableExists` — never called from any service or controller. | Partial | Review doesn't mention specific dead code issues |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Partial | Review doesn't mention specific dead code issues |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Partial | Review doesn't mention specific dead code issues |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Partial | Review doesn't mention specific dead code issues |
| D7 | `FormatCurrency` — private, never called. | Partial | Review doesn't mention specific dead code issues |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Partial | Review doesn't mention specific dead code issues |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Partial | Review doesn't mention specific dead code issues |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Partial | Review doesn't mention specific dead code issues |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Partial | Review doesn't mention specific dead code issues |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | Review doesn't mention specific anti-pattern issues |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Partial | Review doesn't mention specific anti-pattern issues |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Partial | Review doesn't mention specific anti-pattern issues |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Partial | Review doesn't mention specific anti-pattern issues |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Partial | Review doesn't mention specific anti-pattern issues |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Partial | Review doesn't mention specific anti-pattern issues |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies hardcoded credentials in appsettings.json |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Review identifies debug log levels in appsettings.json |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies JWT configuration issues in appsettings.json |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Partial | Review doesn't mention specific HTTPS configuration issues |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Partial | Review doesn't mention specific exception page configuration issues |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Partial | Review doesn't mention specific CORS configuration issues |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Partial | Review doesn't mention specific debug symbol configuration issues |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | Review doesn't mention specific package version issues |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | Review doesn't mention specific missing production configuration |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login — SQL injection boundary cases, correct vs. incorrect password AuthService.GenerateJwtToken — claims mapping, expiry TransactionService.Transfer — zero amount, self-transfer, fee deduction, insufficient funds (with fee) TransactionService.Deposit — interest rate correctness UserService.GetUsersPage — pagination offset correctness (the off-by-one) StringHelper — null inputs, boundary lengths, separator trailing character Controller action results — correct HTTP status codes for various service responses | Found | Review mentions the absence of test project and files, covering the key areas that need tests |