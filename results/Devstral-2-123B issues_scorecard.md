# AI Review Scorecard

> **Branch:** `Devstral-2-123B` &nbsp;·&nbsp; **Commit:** `a779b05`

Total: 63 Found / 7 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review identifies SQL injection vulnerability in `Login` method using string concatenation |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review identifies hardcoded admin bypass password |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review identifies MD5 hashing as insecure |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Review identifies SQL injection in `UpdateUser` and `DeleteUser` methods |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | Review identifies SQL injection in `SearchUsers` method |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Review identifies SQL injection in `Transfer` method |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Review identifies SQL injection in `RecordTransaction` method |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review identifies hardcoded credentials in appsettings |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review identifies `ValidateLifetime = false` on JWT |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | Review identifies missing authorization checks in user update |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | Review identifies missing authorization in user delete |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Review identifies fee calculation excludes minimum fee check |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review identifies balance check doesn't account for fee |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review identifies pagination uses `page * pageSize` instead of `(page - 1) * pageSize` |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Review identifies interest rate applied as 5% instead of 1% |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Review identifies no self-transfer check in transaction controller |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | Review mentions duplicated validation but doesn't specifically identify the repeated guard blocks |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review identifies string concatenation in loop as O(n²) pattern |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | Review mentions JWT token generation but doesn't specifically identify the need for splitting into helpers |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Review identifies SearchUsers returning empty list on error |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Review identifies broad exception catching in email service |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Review identifies no transaction around database updates |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | Review identifies email send after DB commit |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Review identifies broad exception handling that returns messages to client |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | Review identifies connection not disposed in error path |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | Review mentions login security but doesn't specifically identify rate limiting |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review identifies connection not disposed in Login method |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | Review identifies connection ownership transfer issue |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review identifies connection not disposed in ExecuteNonQuery |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review identifies SmtpClient as instance field |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review identifies MailMessage not disposed in email service |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Review identifies configuration key might be null |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Review identifies no check for empty result set |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | Review identifies configuration parsing but doesn't specifically mention the port fallback issue |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | Review identifies null reference risk in username handling |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | Review identifies null check before Length access |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Review identifies null check before int.Parse |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | Review identifies null check for UpdateUser request |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review identifies fee rate and max transactions as magic numbers |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | Review identifies hardcoded deposit cap |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Review identifies email addresses as magic strings |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | Review identifies magic numbers in string helper |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Review identifies page size limit as magic number |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review identifies unused HashPasswordSha1 method |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Review identifies unreachable code in ValidateToken |
| D3 | `TableExists` — never called from any service or controller. | Found | Review identifies unused TableExists method |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review identifies obsolete ExecuteQueryWithParams method |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review identifies unused BuildHtmlTemplate method |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Review identifies unused SendWelcomeEmailHtml method |
| D7 | `FormatCurrency` — private, never called. | Found | Review identifies unused FormatCurrency method |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | Review identifies IsWithinDailyLimit method not called |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Review identifies unused ObfuscateAccount method |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | Review identifies unused ToTitleCase method |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review identifies JoinWithSeparator as broken implementation |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | Review identifies shared mutable static state |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Partial | Review identifies regex compilation but doesn't specifically mention static readonly |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review identifies string concatenation in loop |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Review identifies SmtpClient as instance field |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | Review identifies reimplementing string.IsNullOrWhiteSpace |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | Review identifies GetOpenConnection as anti-pattern |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies production secrets in source control |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Review identifies debug log level in production |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies JWT ValidateLifetime = false |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review identifies HTTPS redirection commented out |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review identifies UseDeveloperExceptionPage unconditionally called |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review identifies overly permissive CORS policy |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | Review identifies debug symbols enabled in release build |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | Review mentions outdated package but doesn't specifically identify Newtonsoft.Json |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | Review mentions environment-specific config but doesn't specifically identify missing production settings |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project found. Critical methods needing tests: AuthService.Login, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, UserService.SearchUsers, StringHelper, EmailService.SendTransferNotification, DatabaseHelper.ExecuteQuerySafe, UserController.UpdateUser, TransactionController.Transfer | Found | Review identifies missing test project and lists key areas needing tests |