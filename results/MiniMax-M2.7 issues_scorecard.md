# AI Review Scorecard

> **Branch:** `MiniMax-M2.7` &nbsp;·&nbsp; **Commit:** `6696839`

# AI Review Scorecard

Total: 49 Found / 22 Partial / 0 Missed out of 71 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "SQL injection via string interpolation: `"SELECT * FROM Users WHERE Username = '{username}' AND Password = '{hashedPassword}'"`" |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "Hardcoded admin bypass password `"SuperAdmin2024"` as a backdoor" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "MD5 used for password hashing — cryptographically broken and unsalted" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "SQL injection in `UpdateUser` and `DeleteUser`: email/username/id interpolated into SQL strings" |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "SQL injection in `TransactionService.cs` - The `RecordTransaction` method uses string interpolation" |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "SQL injection in `RecordTransaction`: VALUES clause uses `{fromId}`, `{toUserId}`, `{amount}`, `{description}` directly interpolated" |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "SQL injection in `RecordTransaction`: VALUES clause uses `{fromId}`, `{toUserId}`, `{amount}`, `{description}` directly interpolated" |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "Hardcoded credentials: DB password `"Admin1234!"`, JWT secret `"mysecretkey"`, email password `"EmailPass99"`" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "JWT `ValidateLifetime = false` — expired tokens are accepted" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | "Deposit applies a 5% interest bonus (`amount * 0.05m * 1`) — this appears to be an unintended interest credit on every deposit, inflating balances without corresponding funding source" |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "Balance check uses `fromBalance >= amount`, but total debit is `amount + fee`. User could transfer exactly their balance and still be unable to cover the fee" |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "Pagination offset calculated as `page * pageSize` — first page skips rows (e.g., page=1 skips the first 20 users)" |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | "Deposit applies a 5% interest bonus (`amount * 0.05m * 1`) — this appears to be an unintended interest credit on every deposit, inflating balances without corresponding funding source" |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | "Static mutable collections (`_auditLog`, `_requestCount`) accessed from multiple threads without synchronization" |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "`JoinWithSeparator` uses string concatenation in a loop (`result += item + separator`) — O(n²) complexity for n items due to string immutability" |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "Silent exception swallowing in `SearchUsers`: catches `Exception`, writes nothing to log, returns empty list" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | "Email failure in `Transfer` propagates an exception after the DB transfer has already committed" |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | "Two separate DB writes (debit + credit) lack atomicity; partial completion possible on failure between them" |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Found | "Email failure in `Transfer` propagates an exception after the DB transfer has already committed" |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | "ExecuteNonQuery opens connection with `GetOpenConnection()` but only calls `connection.Close()` — if an exception occurs between open and close, the connection leaks" |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "Creates `SqlConnection` and `SqlCommand`, calls `ExecuteReader()`, but never disposes any of them" |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "GetOpenConnection() returns an open connection that the caller must dispose, but callers never dispose it" |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "ExecuteNonQuery opens connection with `GetOpenConnection()` but only calls `connection.Close()` — if an exception occurs between open and close, the connection leaks" |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "_smtpClient stored as instance field — not thread-safe; concurrent calls from multiple requests share the same client" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "`MailMessage` objects created but never disposed — implements `IDisposable`" |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | "jwtSecret from config could be null; `_config["Jwt:SecretKey"]!` uses the null-forgiving operator but value may genuinely be absent" |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "Accesses `fromUserTable.Rows[0]` without checking `Rows.Count > 0` — throws `IndexOutOfRangeException` if user does not exist" |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "`int.Parse(userIdClaim!)` throws `FormatException` if claim is absent or malformed" |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | "Transaction fee rate `0.015m` (1.5%) is inline with no named constant" |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | "Deposit interest bonus rate `0.05m * 1` — the `* 1` is meaningless and confusing" |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | "Email subjects `"Transfer Notification - BankingApp"` and `"Welcome to BankingApp!"` are magic strings" |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Partial | "Email subjects `"Transfer Notification - BankingApp"` and `"Welcome to BankingApp!"` are magic strings" |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "Page size cap of `50` hardcoded inline" |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | "`HashPasswordSha1` method defined but never called anywhere in the codebase" |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "`ValidateToken` always returns `true` on line 74 before the real validation logic runs" |
| D3 | `TableExists` — never called from any service or controller. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |
| D7 | `FormatCurrency` — private, never called. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "`JoinWithSeparator` produces a trailing separator (e.g., `"a,b,c,"`) — broken implementation that is never called" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | "Static mutable collections (`_auditLog`, `_requestCount`) accessed from multiple threads without synchronization" |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "`IsValidEmail` creates a new `Regex` instance on every call — regex compilation is expensive" |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "`JoinWithSeparator` uses string concatenation in a loop (`result += item + separator`) — O(n²) complexity for n items due to string immutability" |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "_smtpClient stored as instance field — not thread-safe; concurrent calls from multiple requests share the same client" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "`IsBlank` re-implements what `string.IsNullOrWhiteSpace` already does" |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "`GetOpenConnection()` returns an open connection that the caller must dispose, but callers never dispose it" |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "Hardcoded credentials: DB password `"Admin1234!"`, JWT secret `"mysecretkey"`, email password `"EmailPass99"`" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | "Logging level set to `"Debug"` globally — excessive log volume in production" |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "JWT `ValidateLifetime = false` — expired tokens are accepted" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "HTTPS redirection commented out; app runs over HTTP in production" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "`UseDeveloperExceptionPage()` called unconditionally — exposes stack traces and internal details in production" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "CORS allows any origin (`AllowAnyOrigin`) — permits cross-site attacks" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Partial | "No rate limiting or account lockout on failed login attempts — brute force is trivially possible" |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | "Newtonsoft.Json 12.0.3 has known vulnerabilities (CVE-2019-17571)" |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | "No environment-specific override files (`appsettings.Development.json`, `appsettings.Production.json`) present" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project exists in the provided source tree. Critical methods and scenarios that require unit tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, and controller action results. | Found | "No test project exists in the provided source tree" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project exists in the provided source tree. Critical methods and scenarios that require unit tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, and controller action results. | Found | "No test project exists in the provided source tree" |