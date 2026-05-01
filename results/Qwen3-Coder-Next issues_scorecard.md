# AI Review Scorecard

> **Branch:** `Qwen3-Coder-Next` &nbsp;·&nbsp; **Commit:** `8c55374`

# AI Review Scorecard

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "SQL injection in login query via string interpolation" |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "Hardcoded admin bypass password in source" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "MD5 hashing used for passwords" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "SQL injection in `Transfer` via string interpolation" |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "SQL injection in `SearchUsers` via `ExecuteQuery`" |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "SQL injection in `Transfer` via string interpolation" |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "SQL injection in `RecordTransaction` via string interpolation" |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "Production connection string with plaintext password" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "ValidateLifetime = false on JWT" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "Transfer checks `fromBalance >= amount` but deducts `amount + fee`, risking negative balance" |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "Pagination offset uses `page * pageSize` instead of `(page-1) * pageSize`" |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | "Deposit interest bonus calculated as `amount * 0.05m * 1` (redundant `* 1`)" |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "`result += item + separator` in loop (O(n²))" |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "`SearchUsers` catches `Exception` and returns empty list" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | "`SearchUsers` catches `Exception` and returns empty list" |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | "Balance updates lack transaction scope" |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | "Email sent after DB updates — if email fails, state is inconsistent" |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | "`ex.Message` returned directly to client" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | "`ExecuteNonQuery` does not dispose `SqlCommand`/`SqlConnection`" |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "`SqlConnection`, `SqlCommand`, `SqlDataReader` not disposed" |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "`GetOpenConnection()` returns open connection without disposal contract" |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "`ExecuteNonQuery` does not dispose `SqlCommand`/`SqlConnection`" |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "`_smtpClient` held as instance field (not thread-safe, socket leak risk)" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "`MailMessage` not disposed in `SendTransferNotification`" |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | "`_config["Jwt:SecretKey"]!` used without null check" |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "`fromUserTable.Rows[0]` accessed without `Rows.Count > 0` check" |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | "SMTP credentials read from config without null guard" |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | "`userIdClaim!` used without null check" |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | "`userIdClaim!` used without null check" |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "`userIdClaim!` used without null check" |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | "`userIdClaim!` used without null check" |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | "`TransactionFeeRate = 0.015m` hardcoded" |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | "`amount > 1000000` deposit cap hardcoded" |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | `"notifications@company.com"` hardcoded in multiple places |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | "No check for self-transfer (`fromUserId == toUserId`)" |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "`pageSize > 50` limit hardcoded" |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | "`ValidateToken` has unreachable code after `return true`" |
| D2 | `ValidateToken` — replaced by `HashPasswordMd5`, never called. | Found | "`ValidateToken` has unreachable code after `return true`" |
| D3 | `TableExists` — never called from any service or controller. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |
| D7 | `FormatCurrency` — private, never called. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "`JoinWithSeparator` duplicated by `JoinWithSeparatorFixed`" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | "Static `_auditLog` list (mutable shared state)" |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "`new Regex(...)` created per call" |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "`result += item + separator` in loop (O(n²))" |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "`_smtpClient` held as instance field (not thread-safe, socket leak risk)" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "`GetOpenConnection()` returns open connection without disposal contract" |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "Production connection string with plaintext password" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | "Log level set to `Debug` for all namespaces" |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "ValidateLifetime = false on JWT" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "HTTPS redirection commented out" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "`UseDeveloperExceptionPage()` called unconditionally" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "Overly permissive CORS" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | "<DebugType>full</DebugType> in release builds" |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | "No check for self-transfer (`fromUserId == toUserId`)" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project exists. Critical methods to test: `AuthService.Login` (SQL injection, MD5, bypass), `TransactionService.Transfer` (balance checks, self-transfer, fee calculation), `TransactionService.Deposit` (cap, interest), `UserService.GetUsersPage` (pagination offset), `StringHelper.IsValidEmail` (edge cases), `AuthService.ValidateToken` (dead code). | Found | "No test project exists. Critical methods to test: `AuthService.Login` (SQL injection, MD5, bypass), `TransactionService.Transfer` (balance checks, self-transfer, fee calculation), `TransactionService.Deposit` (cap, interest), `UserService.GetUsersPage` (pagination offset), `StringHelper.IsValidEmail` (edge cases), `AuthService.ValidateToken` (dead code)." |