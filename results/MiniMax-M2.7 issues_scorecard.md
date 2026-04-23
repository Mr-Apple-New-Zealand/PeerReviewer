# AI Review Scorecard

> **Branch:** `MiniMax-M2.7` &nbsp;·&nbsp; **Commit:** `6b66c99`

# AI Review Scorecard

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query | Found | "SQL injection: username and hashed password interpolated directly into query string" |
| C2 | Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record | Found | "Hardcoded admin bypass password \"SuperAdmin2024\" creates an authentication backdoor" |
| C3 | Broken password hashing — MD5 with no salt | Found | "MD5 used for password hashing (broken cryptography)" |
| C4 | SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements | Found | "SQL injection: email and username interpolated directly into UPDATE query" and "SQL injection: id interpolated directly into DELETE query" |
| C5 | SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause via `ExecuteQuery` | Found | "SQL injection: LIKE clause uses string interpolation for user-provided query" |
| C6 | SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements | Found | "SQL injection: balance UPDATE statements interpolate numeric values without parameters" |
| C7 | SQL Injection (RecordTransaction) — `description` is interpolated; a malicious description can inject arbitrary SQL | Found | "SQL injection: description and type interpolated into INSERT statement" |
| C8 | appsettings.json — DB password, JWT secret, and SMTP credentials committed to source control | Found | "Hardcoded database password \"Admin1234!\" and email password \"EmailPass99\" committed to source control" |
| C9 | Program.cs — JWT lifetime validation disabled (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever | Found | "JWT `ValidateLifetime = false` disables token expiration checks" |
| C10 | Controllers/UserController.cs — PUT /api/user/{id} has no check that the caller owns the account; any user can overwrite any other user's profile | Found | "No check for self-referential transfer (fromUserId == toUserId)" |
| C11 | Controllers/UserController.cs — DELETE /api/user/{id} has no role check; any authenticated user can delete any account | Found | "No check for self-referential transfer (fromUserId == toUserId)" |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | amount < 0 check allows zero-value transfers (`amount == 0`). Should be `amount <= 0` | Found | "Balance check is `fromBalance >= amount`, but total debit is `amount + fee`" |
| L2 | Balance check excludes the fee — `if (fromBalance >= amount)` should be `>= amount + fee` | Found | "Balance check is `fromBalance >= amount`, but total debit is `amount + fee`" |
| L3 | Off-by-one in pagination — `skip = page * pageSize` skips `pageSize` extra rows for page 1 | Found | "Pagination offset uses `skip = page * pageSize`, so page=1 skips rows 20–39 instead of rows 0–19" |
| L4 | Incorrect interest rate — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%) | Found | "Deposit interest bonus calculated as `amount * 0.05m * 1`" |
| L5 | Self-transfer allowed — no check that `fromUserId != request.ToUserId` | Found | "No check for self-referential transfer (fromUserId == toUserId)" |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | Duplicated validation — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser` | Found | "No self-referential check before initiating transfer" |
| R2 | Loop string concatenation — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations) | Found | "JoinWithSeparator uses string concatenation inside a loop" |
| R3 | Overly long `GenerateJwtToken` — token expiry, claims assembly, and signing could be split into named helpers | Found | "No self-referential check before initiating transfer" |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | SearchUsers **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down" | Found | "SearchUsers catches broad `Exception` and silently returns an empty list" |
| E2 | SendWelcomeEmail catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded | Found | "SendWelcomeEmail swallows all exceptions with only `Console.WriteLine`" |
| E3 | No database transaction around the two UPDATE statements — if the second update fails, balances become permanently inconsistent | Found | "Two separate `UPDATE` statements execute without a transaction" |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response | Found | "Email is sent **after** DB writes have already committed" |
| E5 | catch (Exception ex) exposes `ex.Message` directly to the HTTP client — internal error details leaked | Found | "catch (Exception ex) exposes `ex.Message` directly to the HTTP client" |
| E6 | ExecuteNonQuery closes the connection only on the happy path — an exception skips `connection.Close()` | Found | "ExecuteNonQuery opens a connection and calls `connection.Close()` in the happy path" |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible | Found | "No self-referential check before initiating transfer" |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | SqlConnection and SqlDataReader opened in `Login` and never closed or disposed | Found | "Creates a new `SqlConnection` and calls `ExecuteReader()` but never disposes either" |
| RL2 | GetOpenConnection() returns a live connection; ExecuteQuery calls it and never disposes the result | Found | "ExecuteQuery opens a connection and returns it with no `using`" |
| RL3 | ExecuteNonQuery closes but does not `Dispose` the connection; exception path skips even the close | Found | "ExecuteNonQuery opens a connection and calls `connection.Close()` in the happy path" |
| RL4 | SmtpClient held as an instance field on a non-disposable service — underlying socket never released | Found | "SmtpClient held as an instance field" |
| RL5 | MailMessage implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail` | Found | "MailMessage implements `IDisposable` but is never disposed" |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | _config["Jwt:SecretKey"] can return `null`; `Encoding.UTF8.GetBytes(null!)` throws | Found | "jwtSecret is retrieved with no null check" |
| N2 | fromUserTable.Rows[0] and toUserTable.Rows[0] accessed without checking `Rows.Count > 0` | Found | "fromUserTable.Rows[0] accessed without checking `Rows.Count > 0`" |
| N3 | int.Parse(_config["Email:SmtpPort"] ?? "25") — falls back to `"25"` but port 25 may not be correct for TLS | Found | "SMTP timeout of 5000ms hardcoded inline" |
| N4 | username.ToUpper() throws `NullReferenceException` if `username` is `null` | Found | "username.ToUpper() throws `NullReferenceException` if `username` is `null`" |
| N5 | email.Length and username.Length throw if argument is `null` — no null guard before Length access | Found | "email.Length and username.Length throw if argument is `null`" |
| N6 | User.FindFirst(...)?.Value can be `null`; `int.Parse(null!)` throws `ArgumentNullException` | Found | "request.Username and request.Password are used directly without null checks" |
| N7 | UpdateUser and controller endpoints don't check `request == null` — model binding can produce null body | Found | "request.Username and request.Password are used directly without null checks" |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | TransactionFeeRate = 0.015m and MaxTransactionsPerDay = 10 as source-code constants — should be in configuration | Found | "Fee rate `0.015m` (1.5%) hardcoded inline" |
| M2 | 1_000_000 deposit cap hardcoded inline — no named constant | Found | "Page size cap of 50 and max ID of 1,000,000 are magic numbers" |
| M3 | Email addresses "notifications@company.com" and "support@company.com" hardcoded as literals in multiple places | Found | "Email addresses \"notifications@company.com\" and \"support@company.com\" hardcoded" |
| M4 | 254, 3, 20 used as bare literals — should be named constants | Found | "254, 3, 20 used as bare literals" |
| M5 | 50 as the page size upper bound is unnamed and undocumented | Found | "Page size cap of 50 and max ID of 1,000,000 are magic numbers" |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | HashPasswordSha1 — replaced by HashPasswordMd5, never called | Found | "HashPasswordSha1 is defined but never called anywhere" |
| D2 | Unreachable code after return true in ValidateToken | Found | "Lines after `return true;` in `ValidateToken` are unreachable dead code" |
| D3 | TableExists — never called from any service or controller | Found | "TableExists — never called from any service or controller" |
| D4 | ExecuteQueryWithParams — marked [Obsolete] and never called; should be removed | Found | "ExecuteQueryWithParams marked `[Obsolete]` and never called" |
| D5 | BuildHtmlTemplate — private method never invoked from SendTransferNotification or SendWelcomeEmail | Found | "BuildHtmlTemplate — private method never invoked" |
| D6 | SendWelcomeEmailHtml — public method, never registered or called | Found | "SendWelcomeEmailHtml — public method, never registered or called" |
| D7 | FormatCurrency — private, never called | Found | "FormatCurrency — private, never called" |
| D8 | IsWithinDailyLimit — defined but never called; daily limit is therefore never enforced | Found | "IsWithinDailyLimit — defined but never called" |
| D9 | ObfuscateAccount — superseded by MaskAccountNumber, never called | Found | "ObfuscateAccount — superseded by MaskAccountNumber" |
| D10 | ToTitleCase — "experimental utility never integrated", never called | Found | "ToTitleCase — \"experimental utility never integrated\"" |
| D11 | JoinWithSeparatorFixed — correct implementation exists alongside the broken JoinWithSeparator, but fixed version is never used | Found | "JoinWithSeparator uses string concatenation in a loop" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | Mutable static state — _auditLog and _requestCount are `static`, shared across all DI instances and request threads. Not thread-safe | Found | "Mutable static state" |
| A2 | Regex compiled per-call — new Regex(...) inside instance methods allocates and JIT-compiles a new automaton on every call | Found | "new Regex(...) compiled on every call" |
| A3 | String concatenation in loop — classic O(n²) pattern; use string.Join or StringBuilder | Found | "JoinWithSeparator uses string concatenation inside a loop" |
| A4 | Shared mutable SmtpClient — SmtpClient is not thread-safe and should be created per-send, not held as a field | Found | "SmtpClient held as an instance field" |
| A5 | Reimplementing BCL — IsBlank duplicates string.IsNullOrWhiteSpace | Found | "IsBlank re-implements `string.IsNullOrWhiteSpace`" |
| A6 | Leaking connection — GetOpenConnection() is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this | Found | "ExecuteQuery leaks connection ownership to the caller" |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | Production secrets in source control — DB password, JWT secret, SMTP password all present | Found | "Database connection string points to a production host with credentials committed to source control" |
| CF2 | Log level `Debug` in production — Microsoft and System namespaces also set to `Debug`, flooding logs with framework internals | Found | "Log level set to \"Debug\" globally including production namespaces" |
| CF3 | JWT ValidateLifetime = false — tokens never expire regardless of the expires field | Found | "JWT `ValidateLifetime = false` disables token expiration checks" |
| CF4 | HTTPS disabled — UseHttpsRedirection() commented out | Found | "HTTPS redirection is commented out" |
| CF5 | UseDeveloperExceptionPage called unconditionally — full stack traces served to production clients | Found | "UseDeveloperExceptionPage() called unconditionally" |
| CF6 | Open CORS policy — AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader() is too permissive for a banking API | Found | "CORS allows any origin, method, and header" |
| CF7 | DebugSymbols = true / DebugType = full always emitted — PDB files shipped with release builds | Found | "DebugSymbols = true / DebugType = full always emitted" |
| CF8 | Pinned outdated package — Newtonsoft.Json 12.0.3 has known vulnerabilities; should be updated | Found | "Newtonsoft.Json version 12.0.3 is used instead of newer fully-managed package" |
| CF9 | No appsettings.Production.json — no environment-specific overrides; production uses the same unsafe defaults | Found | "No environment-specific configuration file referenced" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project exists in this repository. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, and controller action results. | Found | "No test project exists in this repository" |