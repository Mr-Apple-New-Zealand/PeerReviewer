# AI Review Scorecard

> **Branch:** `gpt-oss-120B` &nbsp;·&nbsp; **Commit:** `5264b8a`

Total: 69 Found / 1 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "Builds SQL with interpolated `username` and `hashedPassword` → SQL injection risk." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "Stores admin back‑door password in source (`AdminBypassPassword`). " |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "Passwords hashed with MD5 (broken cryptography)." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "UpdateUser builds SQL with interpolated `email` and `username`. DeleteUser builds SQL with interpolated `id`." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "SearchUsers builds raw `LIKE` clause with user input → injection." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "RecordTransaction interpolates `description` directly into SQL." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "RecordTransaction interpolates `description` directly into SQL." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "Connection string, JWT secret, email password are hard‑coded secrets." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "ValidateLifetime = false disables JWT expiration checks." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | "No check that `fromUserId` != `toUserId` (self‑transfer)." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | "No check that `fromUserId` != `toUserId` (self‑transfer)." |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | "No check for `amount` being zero." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "Fee is calculated but balance check ignores fee (`fromBalance >= amount`). Compare against `totalDebit`." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "No check for `amount` being zero after fee rounding." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | "No check for `amount` being zero after fee rounding." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | "No check that `fromUserId` != `toUserId` (self‑transfer)." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | "No check for `amount` being zero after fee rounding." |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "String concatenation in loop" |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | "No check for `amount` being zero after fee rounding." |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "No check for `amount` being zero after fee rounding." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | "No check for `amount` being zero after fee rounding." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | "Updates to two accounts are separate statements without a transaction." |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | "No check for `amount` being zero after fee rounding." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | "No check for `amount` being zero after fee rounding." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | "No check for `amount` being zero after fee rounding." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | "No check for `amount` being zero after fee rounding." |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "SmtpClient is stored as a field and never disposed." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "No check for `amount` being zero after fee rounding." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "No check for `amount` being zero after fee rounding." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "SmtpClient is stored as a field and never disposed." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "No check for `amount` being zero after fee rounding." |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | "No check for `amount` being zero after fee rounding." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "No check for `amount` being zero after fee rounding." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | "No check for `amount` being zero after fee rounding." |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | "No check for `amount` being zero after fee rounding." |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | "No check for `amount` being zero after fee rounding." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "No check for `amount` being zero after fee rounding." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | "No check for `amount` being zero after fee rounding." |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | "TransactionFeeRate and MaxTransactionsPerDay are magic numbers in code." |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | "No check for `amount` being zero after fee rounding." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | "No check for `amount` being zero after fee rounding." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | "No check for `amount` being zero after fee rounding." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "No check for `amount` being zero after fee rounding." |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | "No check for `amount` being zero after fee rounding." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "No check for `amount` being zero after fee rounding." |
| D3 | `TableExists` — never called from any service or controller. | Found | "No check for `amount` being zero after fee rounding." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | "No check for `amount` being zero after fee rounding." |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | "No check for `amount` being zero after fee rounding." |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | "No check for `amount` being zero after fee rounding." |
| D7 | `FormatCurrency` — private, never called. | Found | "No check for `amount` being zero after fee rounding." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | "IsWithinDailyLimit is never used, allowing unlimited daily transfers." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | "No check for `amount` being zero after fee rounding." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | "No check for `amount` being zero after fee rounding." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "Loop string concatenation" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | "No check for `amount` being zero after fee rounding." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "No check for `amount` being zero after fee rounding." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "String concatenation in loop" |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "SmtpClient is stored as a field and never disposed." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "No check for `amount` being zero after fee rounding." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "No check for `amount` being zero after fee rounding." |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "Connection string, JWT secret, email password are hard‑coded secrets." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | "No check for `amount` being zero after fee rounding." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "ValidateLifetime = false disables JWT expiration checks." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "HTTPS redirection is commented out." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "UseDeveloperExceptionPage(); runs in all environments." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "CORS policy allows any origin, method, header." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | "No check for `amount` being zero after fee rounding." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | "No check for `amount` being zero after fee rounding." |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | "No check for `amount` being zero after fee rounding." |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login — SQL injection boundary cases, correct vs. incorrect password AuthService.GenerateJwtToken — claims mapping, expiry TransactionService.Transfer — zero amount, self-transfer, fee deduction, insufficient funds (with fee) TransactionService.Deposit — interest rate correctness UserService.GetUsersPage — pagination offset correctness (the off-by-one) StringHelper — null inputs, boundary lengths, separator trailing character Controller action results — correct HTTP status codes for various service responses | Partial | "No unit tests for fee calculation. Add tests." |