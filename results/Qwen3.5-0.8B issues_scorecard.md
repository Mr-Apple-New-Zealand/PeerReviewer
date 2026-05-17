# AI Review Scorecard

> **Branch:** `Qwen3.5-0.8B` &nbsp;·&nbsp; **Commit:** `90f61e1`

Total: 38 Found / 32 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review mentions "SQL injection exists" in the AuthService.Login method |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review mentions "hardcoded credentials" in AuthService |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review mentions "MD5 hashing" and "password hashing" issues |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Review mentions "SQL injection" in UserService |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | Review mentions "SQL injection" in UserService |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Review mentions "SQL injection" in TransactionService |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Review mentions "SQL injection" in TransactionService |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review mentions "hardcoded credentials" and "secrets in source control" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review mentions "JWT lifetime validation disabled" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | Review mentions "access control" issues in UserController |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | Review mentions "authorization" issues in UserController |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Review mentions "logic error" in Transfer method |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review mentions "balance check" issues in Transfer method |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review mentions "pagination" issues in UserService |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Review mentions "interest rate" issues in Deposit method |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Review mentions "self-transfer" issues in Transfer method |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | Review mentions "validation" but doesn't specifically call out the duplicated validation pattern |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Partial | Review mentions "string concatenation" but doesn't specifically identify this pattern |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | Review mentions "JWT token generation" but doesn't specifically call out this refactoring opportunity |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Partial | Review mentions "error handling" but doesn't specifically identify this pattern |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | Review mentions "exception handling" but doesn't specifically identify this pattern |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Partial | Review mentions "database transaction" but doesn't specifically identify this pattern |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Partial | Review mentions "email failure" but doesn't specifically identify this pattern |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Partial | Review mentions "error handling" but doesn't specifically identify this pattern |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Partial | Review mentions "resource management" but doesn't specifically identify this pattern |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | Review mentions "rate limiting" but doesn't specifically identify this pattern |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review mentions "resource leaks" and "SqlConnection" issues |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | Review mentions "resource leaks" and "connection management" |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review mentions "resource leaks" and "connection management" |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review mentions "SmtpClient" resource leak |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review mentions "resource leaks" and "MailMessage" issues |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Partial | Review mentions "null reference" but doesn't specifically identify this pattern |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Partial | Review mentions "null reference" but doesn't specifically identify this pattern |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | Review mentions "null reference" but doesn't specifically identify this pattern |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | Review mentions "null reference" but doesn't specifically identify this pattern |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | Review mentions "null reference" but doesn't specifically identify this pattern |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Partial | Review mentions "null reference" but doesn't specifically identify this pattern |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | Review mentions "null reference" but doesn't specifically identify this pattern |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Partial | Review mentions "magic numbers" but doesn't specifically identify this pattern |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Partial | Review mentions "magic numbers" but doesn't specifically identify this pattern |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | Review mentions "magic strings" but doesn't specifically identify this pattern |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Partial | Review mentions "magic strings" but doesn't specifically identify this pattern |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Partial | Review mentions "magic numbers" but doesn't specifically identify this pattern |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review mentions "dead code" and "HashPasswordSha1" |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Review mentions "dead code" in AuthService |
| D3 | `TableExists` — never called from any service or controller. | Found | Review mentions "dead code" and "TableExists" |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review mentions "dead code" and "ExecuteQueryWithParams" |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review mentions "dead code" and "BuildHtmlTemplate" |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Review mentions "dead code" and "SendWelcomeEmailHtml" |
| D7 | `FormatCurrency` — private, never called. | Found | Review mentions "dead code" and "FormatCurrency" |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | Review mentions "dead code" and "IsWithinDailyLimit" |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Review mentions "dead code" and "ObfuscateAccount" |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | Review mentions "dead code" and "ToTitleCase" |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review mentions "dead code" and "JoinWithSeparatorFixed" |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | Review mentions "anti-patterns" but doesn't specifically identify this pattern |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Partial | Review mentions "anti-patterns" but doesn't specifically identify this pattern |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Partial | Review mentions "anti-patterns" but doesn't specifically identify this pattern |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Partial | Review mentions "anti-patterns" but doesn't specifically identify this pattern |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Partial | Review mentions "anti-patterns" but doesn't specifically identify this pattern |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Partial | Review mentions "anti-patterns" but doesn't specifically identify this pattern |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review mentions "hardcoded credentials" and "secrets in source control" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | Review mentions "configuration" but doesn't specifically identify this pattern |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review mentions "JWT lifetime validation disabled" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review mentions "HTTPS disabled" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review mentions "UseDeveloperExceptionPage() called unconditionally" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review mentions "CORS policy" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Partial | Review mentions "configuration" but doesn't specifically identify this pattern |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | Review mentions "configuration" but doesn't specifically identify this pattern |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | Review mentions "configuration" but doesn't specifically identify this pattern |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results | Found | Review explicitly states "No test project" and "No test files" in the analysis |