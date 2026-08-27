# Scorer: Qwen3.5-9B-imatrix:Q4_K_S
# Review type: null

# AI Review Scorecard

Total: 0 Found / 0 Partial / 69 Missed out of 69 issues.

### Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) — Username and Password are string-interpolated directly into a SELECT query. | Missed | |
| C2 | Backdoor / hardcoded admin bypass — AdminBypassPassword = "SuperAdmin2024" allows login as superadmin without a DB record. | Missed | |
| C3 | Broken password hashing — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Missed | |
| C4 | SQL Injection (UpdateUser / DeleteUser) — email, username, and id are string-interpolated into UPDATE/DELETE statements. | Missed | |
| C5 | SQL Injection (SearchUsers) — query is interpolated into a LIKE clause via ExecuteQuery. | Missed | |
| C6 | SQL Injection (Transfer/Deposit) — fromUserId, toUserId, amount all concatenated into UPDATE statements. | Missed | |
| C7 | SQL Injection (RecordTransaction) — description is interpolated; a malicious description can inject arbitrary SQL. | Missed | |
| C8 | Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed to source control. | Missed | |
| C9 | JWT lifetime validation disabled (ValidateLifetime = false) — tokens never expire, stolen tokens are valid forever. | Missed | |
| C10 | Broken Access Control — PUT /api/user/{id} has no check that the caller owns the account; any user can overwrite any other user's profile. | Missed | |
| C11 | Missing Authorization — DELETE /api/user/{id} has no role check; any authenticated user can delete any account. | Missed | |

### Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | amount < 0 check allows zero-value transfers (amount == 0). Should be amount <= 0. | Missed | |
| L2 | Balance check excludes the fee — if (fromBalance >= amount) should be >= amount + fee. | Missed | |
| L3 | Off-by-one in pagination — skip = page * pageSize skips pageSize extra rows for page 1. | Missed | |
| L4 | Incorrect interest rate — deposit bonus uses 0.05m (5%) instead of intended 0.01m (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Missed | |
| L5 | Self-transfer allowed — no check that fromUserId != request.ToUserId. | Missed | |

### Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation — identical id <= 0 / id > 1_000_000 guard blocks repeated in GetUserById, UpdateUser, and DeleteUser. | Missed | |
| R2 | Loop string concatenation — JoinWithSeparatorFixed exists but JoinWithSeparator uses += in a loop (O(n²) allocations). | Missed | |
| R3 | Overly long GenerateJwtToken — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | |

### Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | SearchUsers swallows all exceptions and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Missed | |
| E2 | SendWelcomeEmail catches Exception (too broad) — programming errors like NullReferenceException are silently discarded. | Missed | |
| E3 | No database transaction around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Missed | |
| E4 | Email failure in Transfer propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Missed | |
| E5 | catch (Exception ex) exposes ex.Message directly to the HTTP client — internal error details leaked. | Missed | |
| E6 | ExecuteNonQuery closes the connection only on the happy path — an exception skips connection.Close(). | Missed | |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed | |

### Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | SqlConnection and SqlDataReader opened in Login and never closed or disposed. | Missed | |
| RL2 | GetOpenConnection() returns a live connection; ExecuteQuery calls it and never disposes the result. | Missed | |
| RL3 | ExecuteNonQuery closes but does not Dispose the connection; exception path skips even the close. | Missed | |
| RL4 | SmtpClient held as an instance field on a non-disposable service — underlying socket never released. | Missed | |
| RL5 | MailMessage implements IDisposable but is never disposed in SendTransferNotification or SendWelcomeEmail. | Missed | |

### Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | _config["Jwt:SecretKey"] can return null; Encoding.UTF8.GetBytes(null!) throws. | Missed | |
| N2 | fromUserTable.Rows[0] and toUserTable.Rows[0] accessed without checking Rows.Count > 0 — throws if user ID doesn't exist. | Missed | |
| N3 | int.Parse(_config["Email:SmtpPort"] ?? "25") — falls back to "25" but port 25 may not be correct for TLS; real concern is the first ?? hiding a missing config key. | Missed | |
| N4 | username.ToUpper() throws NullReferenceException if username is null. | Missed | |
| N5 | email.Length and username.Length throw if argument is null — no null guard before Length access. | Missed | |
| N6 | User.FindFirst(...)?.Value can be null; int.Parse(null!) throws ArgumentNullException. | Missed | |
| N7 | UpdateUser and controller endpoints don't check request == null — model binding can produce null body. | Missed | |

### Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | TransactionFeeRate = 0.015m and MaxTransactionsPerDay = 10 as source-code constants — should be in configuration. | Missed | |
| M2 | 1_000_000 deposit cap hardcoded inline — no named constant. | Missed | |
| M3 | Email addresses "notifications@company.com" and "support@company.com" hardcoded as literals in multiple places. | Missed | |
| M4 | 254, 3, 20 used as bare literals — should be named constants (MaxEmailLength, MinUsernameLength, etc.). | Missed | |
| M5 | 50 as the page size upper bound is unnamed and undocumented. | Missed | |

### Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | HashPasswordSha1 — replaced by HashPasswordMd5, never called. | Missed | |
| D2 | Unreachable code after return true in ValidateToken. | Missed | |
| D3 | TableExists — never called from any service or controller. | Missed | |
| D4 | ExecuteQueryWithParams — marked [Obsolete] and never called; should be removed. | Missed | |
| D5 | BuildHtmlTemplate — private method reachable only from SendWelcomeEmailHtml (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Missed | |
| D6 | SendWelcomeEmailHtml — public method, never registered or called. | Missed | |
| D7 | FormatCurrency — private, never called. | Missed | |
| D8 | IsWithinDailyLimit — defined but never called; daily limit is therefore never enforced. | Missed | |
| D9 | ObfuscateAccount — superseded by MaskAccountNumber, never called. | Missed | |
| D10 | ToTitleCase — "experimental utility never integrated", never called. | Missed | |
| D11 | JoinWithSeparatorFixed — correct implementation exists alongside the broken JoinWithSeparator, but fixed version is never used. | Missed | |

### Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state — _auditLog and _requestCount are static, shared across all DI instances and request threads. | Missed | |
| A2 | Regex compiled per-call — new Regex(...) inside instance methods allocates and JIT-compiles a new automaton on every call. | Missed | |
| A3 | String concatenation in loop — classic O(n²) pattern; use string.Join or StringBuilder. | Missed | |
| A4 | Shared mutable SmtpClient — SmtpClient is not thread-safe and should be created per-send, not held as a field. | Missed | |
| A5 | Reimplementing BCL — IsBlank duplicates string.IsNullOrWhiteSpace. | Missed | |
| A6 | Leaking connection — GetOpenConnection() is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Missed | |

### Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control — DB password, JWT secret, SMTP password all present. | Missed | |
| CF2 | Log level Debug in production — Microsoft and System namespaces also set to Debug, flooding logs with framework internals. | Missed | |
| CF3 | JWT ValidateLifetime = false — tokens never expire regardless of the expires field. | Missed | |
| CF4 | HTTPS disabled — UseHttpsRedirection() commented out. | Missed | |
| CF5 | UseDeveloperExceptionPage() called unconditionally — full stack traces served to production clients. | Missed | |
| CF6 | Open CORS policy — AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader() is too permissive for a banking API. | Missed | |
| CF7 | DebugSymbols = true / DebugType = full always emitted — PDB files shipped with release builds. | Missed | |
| CF8 | Pinned outdated package — Newtonsoft.Json 12.0.3 has known vulnerabilities; should be updated. | Missed | |
| CF9 | No appsettings.Production.json — no environment-specific overrides; production uses the same unsafe defaults. | Missed | |

### Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | The project contains no test project and no test files whatsoever. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results. | Missed | |