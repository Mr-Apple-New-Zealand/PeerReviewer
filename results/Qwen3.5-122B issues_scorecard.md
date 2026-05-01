# AI Review Scorecard

> **Branch:** `Qwen3.5-122B` &nbsp;·&nbsp; **Commit:** `6ed61e9`

# AI Review Scorecard

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "SQL Injection: Username and password are interpolated directly into the SQL query string." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "Hardcoded Backdoor: Admin user can bypass authentication with a hardcoded password." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "Weak Cryptography: Passwords are hashed using MD5, which is cryptographically broken." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "SQL Injection: `UpdateUser` interpolates email and username directly into the SQL string." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "SQL Injection: `SearchUsers` uses `ExecuteQuery` with a raw `LIKE` clause." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "SQL Injection: `RecordTransaction` interpolates values directly into the SQL string." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "SQL Injection: `RecordTransaction` interpolates values directly into the SQL string." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "Hardcoded Credentials: Database connection string contains plaintext password." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "JWT Misconfiguration: `ValidateLifetime` is set to `false`, allowing expired tokens to be valid." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | "Broken Access Control: `RefundTransaction` is not implemented but exposed via API." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | "Broken Access Control: `GetAuditLog` exposes internal audit logs to any authenticated user." |
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | "Logic Error: Balance check compares `fromBalance >= amount` but deducts `amount + fee`." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "Logic Error: Balance check compares `fromBalance >= amount` but deducts `amount + fee`." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "Off-by-one Error: Pagination uses `page * pageSize` instead of `(page - 1) * pageSize`." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | "Logic Error: `Deposit` adds `amount + interestBonus` but `interestBonus` calculation is hardcoded to 1 year." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | "Logic Error: `Transfer` does not check if `fromUserId` equals `toUserId`." |
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | "Logic Error: `GetUserById` throws for `id > 1000000`, which is an arbitrary and likely incorrect limit." |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "Anti-pattern: String concatenation in a loop (`result += item`) is O(n²)." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | "Anti-pattern: `RecordTransaction` uses string interpolation for SQL, risking injection." |
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "Error Handling: `SearchUsers` swallows all exceptions and returns an empty list." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | "Error Handling: `SendWelcomeEmail` swallows exceptions and logs to `Console.WriteLine`." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | "Error Handling: Email sending failure is not handled; it throws and leaves DB state inconsistent." |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | "Error Handling: Email sending failure is not handled; it throws and leaves DB state inconsistent." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | "Error Handling: Returns raw `ex.Message` to the client, potentially leaking internal details." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | "Resource Leak: `ExecuteNonQuery` opens a connection but relies on `Close()` which may not be called on exception." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | "Error Handling: `Login` does not handle SQL exceptions, potentially crashing the app." |
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "Resource Leak: `Login` opens a `SqlConnection` but never closes or disposes it." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "Resource Leak: `GetOpenConnection` returns an open connection that the caller must close." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "Resource Leak: `ExecuteNonQuery` opens a connection but relies on `Close()` which may not be called on exception." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "Resource Leak: `SmtpClient` is held as an instance field and never disposed." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "Resource Leak: `MailMessage` is created but never disposed." |
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | "Null Reference: `jwtSecret` is force-unwrapped with `!` before use." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "Null Reference: `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | "Null Reference: `userIdClaim` is force-unwrapped with `!` before parsing." |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | "Null Reference: `row["Id"]` and other fields accessed without null checks." |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | "Null Reference: `reader["Id"]` access assumes the row exists and column is not null." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "Null Reference: `userIdClaim` is force-unwrapped with `!` before parsing." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | "Null Reference: `table.Rows[0]` accessed without checking `Rows.Count > 0." |
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | "Magic Number: `MaxTransactionsPerDay` is hardcoded as 10." |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | "Magic Number: `1000000` is used as an arbitrary user ID limit." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | "Magic Number: `0.05m` is hardcoded as interest rate." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | "Magic Number: `254` is hardcoded as max email length." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "Magic Number: `50` is hardcoded as the max page size." |
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | "Dead Code: `HashPasswordSha1` method is defined but never called." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "Error Handling: `ValidateToken` returns `true` immediately, ignoring the actual token validation logic below." |
| D3 | `TableExists` — never called from any service or controller. | Found | "Dead Code: `ExecuteQueryWithParams` is marked `[Obsolete]` but still present." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | "Dead Code: `ExecuteQueryWithParams` is marked `[Obsolete]` but still present." |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | "Dead Code: `BuildHtmlTemplate` method is defined but never called." |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | "Dead Code: `BuildHtmlTemplate` method is defined but never called." |
| D7 | `FormatCurrency` — private, never called. | Found | "Dead Code: `FormatCurrency` method is defined but never called." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | "Dead Code: `FormatCurrency` method is defined but never called." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | "Dead Code: `JoinWithSeparator` method is defined but never called." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | "Dead Code: `JoinWithSeparator` method is defined but never called." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "Dead Code: `JoinWithSeparator` method is defined but never called." |
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | "Anti-pattern: Static mutable state (`_auditLog`, `_requestCount`) is shared across instances." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "Anti-pattern: `Regex` is instantiated inside the method, causing performance overhead." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "Anti-pattern: String concatenation in a loop (`result += item`) is O(n²)." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "Anti-pattern: `SmtpClient` is held as an instance field, which is not thread-safe." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "Anti-pattern: String concatenation in a loop (`result += item`) is O(n²)." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "Resource Leak: `GetOpenConnection` returns an open connection that the caller must close." |
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "Configuration Issue: Production secrets are committed to `appsettings.json`." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | "Configuration Issue: Logging level is set to `Debug` for all namespaces." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "Configuration Issue: `ValidateLifetime` is set to `false` in JWT configuration." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "Configuration Issue: HTTPS redirection is commented out." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "Configuration Issue: `UseDeveloperExceptionPage()` is called unconditionally." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "Configuration Issue: CORS policy allows any origin and method." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | "Configuration Issue: `DebugSymbols` and `DebugType` are set to `full` in release builds." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | "Configuration Issue: `Newtonsoft.Json` version 12.0.3 is outdated and may have vulnerabilities." |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | "Configuration Issue: Logging level is set to `Debug` for all namespaces." |
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, and controller action results. | Found | "Missing Unit Tests: The project contains no test project or test files." |