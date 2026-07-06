# AI Review Scorecard

> **Branch:** `Qwen3.5-4B` &nbsp;·&nbsp; **Commit:** `1e986df`

Total: 54 Found / 2 Partial / 14 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query. | Found | "SQL injection via string interpolation in `Login` query." |
| C2 | Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "Hardcoded admin backdoor password allows bypassing authentication." |
| C3 | Broken password hashing — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Partial | "MD5 is cryptographically broken and unsuitable for password hashing." (Misses specific mention of missing salt). |
| C4 | SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "SQL injection in `UpdateUser` via string interpolation." and "SQL injection in `DeleteUser` via string interpolation." |
| C5 | SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "SQL injection in `SearchUsers` via string interpolation in `ExecuteQuery`." |
| C6 | SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "SQL injection in `Transfer` via string interpolation in `ExecuteNonQuery`." and "SQL injection in `Deposit` via string interpolation in `ExecuteNonQuery`." |
| C7 | SQL Injection (RecordTransaction) — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "SQL injection in `RecordTransaction` via string interpolation." |
| C8 | Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "Production database credentials committed to source control." and "Weak JWT secret key... committed to source control." and "SMTP password committed to source control." |
| C9 | JWT lifetime validation disabled (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "`ValidateLifetime = false` disables JWT expiration validation." |
| C10 | Broken Access Control — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | "Missing ownership check; any authenticated user can update any user." |
| C11 | Missing Authorization — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | "Missing ownership check; any authenticated user can delete any user." |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Missed | The review mentions balance checks and self-transfers but does not identify the zero-value transfer logic error. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "Balance check uses `amount` but deducts `amount + fee`, allowing negative balances." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "Pagination offset calculation `page * pageSize` is incorrect for 1-based indexing." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | "Deposit interest calculation `amount * 0.05m * 1` is redundant and potentially misleading." (Identifies the value but frames it as redundancy/misleading rather than explicitly stating it is the wrong rate compared to intent). |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | "No check prevents a user from transferring funds to themselves." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Missed | The review does not mention duplicated validation logic or suggest extracting a helper. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "String concatenation in loop is O(n²)." (Under Anti-patterns, referencing `StringHelper`). |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | The review does not comment on the length or structure of `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "`SearchUsers` catches `Exception` and returns an empty list, hiding errors." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | "`SendWelcomeEmail` catches `Exception` and logs to console, swallowing errors." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | "Database writes in `Transfer` are not atomic; failure after debit leaves inconsistent state." |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Missed | The review mentions atomicity of DB writes but does not identify the specific issue of email failure propagating after commit. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | "`UpdateUser` returns raw `ex.Message` to the client, leaking internal details." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | "`ExecuteNonQuery` opens a connection but only calls `Close()`, not `Dispose()`." (Implies the exception path issue by noting lack of proper disposal/close handling). |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed | The review does not mention rate limiting or account lockout. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "`SqlConnection` in `Login` is opened but never closed or disposed." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "`GetOpenConnection` returns an open connection without disposing it." and "`ExecuteQuery` opens a connection but never closes or disposes it." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "`ExecuteNonQuery` opens a connection but only calls `Close()`, not `Dispose()`." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "`SmtpClient` is held as an instance field, which is not thread-safe." (Also noted under Anti-patterns). |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "`MailMessage` in `SendTransferNotification` is not disposed." and "`MailMessage` in `SendWelcomeEmail` is not disposed." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Missed | The review does not mention null checks for config keys in `AuthService`. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "Accessing `Rows[0]` without checking `Rows.Count > 0` can throw." (Referenced for `TransactionService`). |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Missed | The review does not mention null/config fallback issues in `EmailService`. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | The review mentions null checks for `email.Length` and `username.Length` in `StringHelper` but not `username.ToUpper()` in `EmailService`. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | "`email.Length` can throw if `email` is null." and "`username.Length` can throw if `username` is null." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "`int.Parse` on `userIdClaim` can throw if claim is null." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Missed | The review does not mention null checks for request bodies in controllers. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | "`TransactionFeeRate` is a magic number." and "`MaxTransactionsPerDay` is a magic number." |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | "Deposit limit `1000000` is a magic number." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | "Email subject and body strings are hardcoded." (Implies email content/addresses). |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | "Email length limit `254` is a magic number." and "Username length limits `3` and `20` are magic numbers." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "Page size limit `50` is a magic number." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | "`HashPasswordSha1` is defined but never called." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "`ValidateToken` method is unreachable after early return." |
| D3 | `TableExists` — never called from any service or controller. | Missed | The review does not mention `TableExists`. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | "`ExecuteQueryWithParams` is marked `[Obsolete]` but still present." |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Missed | The review does not mention `BuildHtmlTemplate`. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Missed | The review mentions `MailMessage` disposal in `SendWelcomeEmailHtml` but does not identify it as dead/unused code. |
| D7 | `FormatCurrency` — private, never called. | Found | "`FormatCurrency` is defined but never called." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Missed | The review mentions null checks in `IsWithinDailyLimit` but does not identify it as dead code. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | "`ObfuscateAccount` duplicates functionality of `MaskAccountNumber`." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | "`ToTitleCase` duplicates standard library functionality." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "`JoinWithSeparatorFixed` duplicates `string.Join`." (Identifies it as redundant/unused). |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | "`_auditLog` is static mutable state, not thread-safe." and "`_requestCount` is static mutable state, not thread-safe." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "`new Regex` created on every call." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "String concatenation in loop is O(n²)." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "`SmtpClient` is not thread-safe." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "`IsBlank` duplicates `string.IsNullOrWhiteSpace`." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "`GetOpenConnection` returns an open connection without disposing it." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "Production database credentials committed to source control." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | "Debug log level set for production namespaces." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "`ValidateLifetime = false` disables JWT expiration." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "HTTPS redirection is commented out." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "`UseDeveloperExceptionPage()` is unconditional." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "CORS policy allows any origin, method, and header." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | "`DebugSymbols` and `DebugType` are set for release builds." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | "`Newtonsoft.Json` version 12.0.3 is outdated and vulnerable." |
| CF9 | *(missing)* | — | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Missed | The review does not mention the missing `appsettings.Production.json`. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, Controller action results. | Found | "No test project exists." and lists specific methods needing tests like `Transfer`, `Deposit`, `GetUsersPage`, `Login`, `IsValidEmail`. |