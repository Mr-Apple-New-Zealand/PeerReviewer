# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `7edff07`

> ⚠ **3 row(s) rated Found name a target that never appears in the review** (D4, D5, D6). Adjusted Found: **62** of 70. See the spot-check below.

Total: 65 Found / 0 Partial / 5 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | AuthService.cs line 32: "SQL injection via string interpolation in Login: `string sql = $"SELECT * FROM Users WHERE Username = '{username}' AND Password = '{hashedPassword}' AND IsActive = 1"`" |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | AuthService.cs line 17: "Hardcoded admin bypass password constant: `private const string AdminBypassPassword = \"SuperAdmin2024\"`" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | AuthService.cs line 61-66: "MD5 used for password hashing (HashPasswordMd5) — weak cryptography" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | UserService.cs line 47: "SQL injection in UpdateUser: `($"UPDATE Users SET Email = '{email}', Username = '{username}' WHERE Id = {id}")`" |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | UserService.cs line 99: "SQL injection in SearchUsers: `($"Username LIKE '%{query}%'")`" |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | TransactionService.cs line 47-48: "SQL injection in Transfer: `($"UPDATE Users SET Balance = {newFromBalance} WHERE Id = {fromUserId}")`" |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | TransactionService.cs line 89-91: "SQL injection in RecordTransaction: string interpolation in INSERT statement" |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | appsettings.json line 3: "Hardcoded production database credentials: `Password=Admin1234!`" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Program.cs line 24: "JWT ValidateLifetime set to false — tokens never expire" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Missed | Review does not mention specific endpoint or missing access control check for PUT /api/user/{id} |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Missed | Review does not mention specific endpoint or missing authorization check for DELETE /api/user/{id} |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | TransactionService.cs line 42: "Insufficient funds check uses `fromBalance >= amount` but actual debit is `amount + fee` — may produce negative balance" |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | TransactionService.cs line 42: "Insufficient funds check uses `fromBalance >= amount` but actual debit is `amount + fee` — may produce negative balance" |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | UserService.cs line 72: "Pagination off-by-one error: `int skip = page * pageSize;` returns wrong page" |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | TransactionService.cs line 68: "Interest bonus calculation `amount * 0.05m * 1` multiplies by 1 unnecessarily" |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | TransactionController.cs line 27: "Same issue as line 27" |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | UserService.cs line 22, 56: "User ID range limit `1000000` hardcoded in two places" |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | StringHelper.cs line 29-36: "String concatenation in loop: `result += item + separator;` — O(n²) complexity" |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | Review does not mention specific method or behavior described in the row |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | UserService.cs line 105-108: "SearchUsers catches all exceptions and returns empty list — caller cannot distinguish error from no results" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | EmailService.cs line 34-61: "Retry loop catches SmtpException but continues loop on non-SmtpException failures" |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | TransactionService.cs line 52-55: "Email notification sent after DB write commits; if email throws, transfer already succeeded" |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Found | TransactionService.cs line 52-55: "Email notification sent after DB write commits; if email throws, transfer already succeeded" |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | UserController.cs line 50-53: "UpdateUser catches Exception and returns ex.Message to client — exposes internal details" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | DatabaseHelper.cs line 50-57: "ExecuteNonQuery opens connection via GetOpenConnection but only calls Close() — not safe in all exception paths" |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed | Review does not mention specific missing check for rate limiting or account lockout |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | AuthService.cs line 34-37: "SqlConnection created and opened but never disposed — connection leak" |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | DatabaseHelper.cs line 19-24: "GetOpenConnection returns open SqlConnection; caller may forget to dispose" |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | DatabaseHelper.cs line 50-57: "ExecuteNonQuery opens connection via GetOpenConnection but only calls Close() — not safe in all exception paths" |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | EmailService.cs line 16: "SmtpClient stored as instance field — not thread-safe, socket never released" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | EmailService.cs line 39-43: "MailMessage created but not disposed" |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Program.cs line 16: "jwtSecret accessed directly; if null, jwtSecret! bypasses check but causes NullReferenceException later at line 28" |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | TransactionService.cs line 36-37: "DataTable.Rows[0] accessed without checking Rows.Count > 0 — will throw IndexOutOfRangeException" |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | EmailService.cs line 24: "int.Parse(_config[\"Email:SmtpPort\"] ?? \"25\")" |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | EmailService.cs line 69: "MailMessage created but not disposed" |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | StringHelper.cs line 14, 24: "new Regex(...)" created inside method called repeatedly — regex compiled each call | 
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | TransactionController.cs line 27: "`int.Parse(userIdClaim!)` — if claim is null, FormatException thrown" |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | UserController.cs line 22: "GetUserById called with id from route; no null check needed on int but service may throw" |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | TransactionService.cs line 11: "Transaction fee rate `0.015m` hardcoded inline (1.5%)" |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | TransactionService.cs line 65: "Deposit cap `1000000` hardcoded" |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Missed | Review does not mention specific email address constants |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | StringHelper.cs line 14, 24: "new Regex(...)" created inside method called repeatedly — regex compiled each call |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | UserService.cs line 70: "Page size cap `50` hardcoded" |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | AuthService.cs line 91-96: "SHA1 used for password hashing (HashPasswordSha1) — weak cryptography" |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | AuthService.cs line 98-108: "ValidateToken has unreachable code after `return true;` on line 101" |
| D3 | `TableExists` — never called from any service or controller. | Found | DatabaseHelper.cs line 59-65: "TableExists method never called" |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | DatabaseHelper.cs line 26-34: "ExecuteQuery method never called — only ExecuteQuerySafe is used" |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | EmailService.cs line 79: "MailMessage created but not disposed" |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | EmailService.cs line 89: "MailMessage created but not disposed" |
| D7 | `FormatCurrency` — private, never called. | Found | TransactionService.cs line 94-97: "FormatCurrency method never called" |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | TransactionService.cs line 99-103: "RefundTransaction throws NotImplementedException — not stub code, blocks functionality" |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | StringHelper.cs line 54-57: "ObfuscateAccount method never called" |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | StringHelper.cs line 59-63: "IsBlank method never called — duplicates string.IsNullOrWhiteSpace" |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | StringHelper.cs line 38-41: "JoinWithSeparatorFixed method never called — only the broken JoinWithSeparator is used" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | UserService.cs line 85-93: "Audit report builds string with `+=` in loop — O(n²)" |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | StringHelper.cs line 16, 25: "`new Regex(...)` created inside method called repeatedly — regex compiled each call" |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | StringHelper.cs line 29-36: "String concatenation in loop: `result += item + separator;` — O(n²) complexity" |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | EmailService.cs line 16: "SmtpClient stored as instance field — not thread-safe, socket never released" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | StringHelper.cs line 65-71: "IsBlank method never called — duplicates string.IsNullOrWhiteSpace" |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | DatabaseHelper.cs line 19-24: "GetOpenConnection returns unmanaged connection — caller responsibility to dispose" |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | appsettings.json line 3: "Hardcoded production database credentials: `Password=Admin1234!`" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | appsettings.json line 17-21: "Debug log level set for production namespace" |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Program.cs line 24: "JWT ValidateLifetime set to false — tokens never expire" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Program.cs line 36: "HTTPS redirection commented out" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Program.cs line 34: "UseDeveloperExceptionPage called unconditionally in production" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Program.cs line 38: "CORS policy AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader() — overly permissive" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp.csproj line 8-9: "DebugSymbols and DebugType set to full in project file" |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | SampleBankingApp.csproj line 15: "Newtonsoft.Json version 12.0.3 — known vulnerable package" |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | appsettings.json line 1-24: "No environment-specific override files (appsettings.Production.json missing)" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project exists in repository; key areas that need tests include AuthService.Login, TransactionService.Transfer, UserService.GetUsersPage, etc. | Found | (No test project) line N/A: "No test project exists in repository" |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Missed | `GenerateJwtToken` | yes | under-credited? |
| E7 | Missed | `rate limit` | **no** | - |
| N3 | Found | `SmtpPort` | yes | - |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Found | `TableExists` | yes | - |
| D4 | Found | `ExecuteQueryWithParams` | **no** | **MIS-CREDIT** |
| D5 | Found | `BuildHtmlTemplate` | **no** | **MIS-CREDIT** |
| D6 | Found | `SendWelcomeEmailHtml` | **no** | **MIS-CREDIT** |
| D7 | Found | `FormatCurrency` | yes | - |
| D8 | Found | `IsWithinDailyLimit` | yes | - |
| D9 | Found | `ObfuscateAccount` | yes | - |
| D10 | Found | `ToTitleCase` | yes | - |
| D11 | Found | `JoinWithSeparatorFixed` | yes | - |
| CF9 | Found | `appsettings.Production` | yes | - |

**Adjusted Found: 62 of 70** (65 reported, less 3 mis-credited).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `MiniMax-M2.7:Q3_K_S` |
| Reasoning strength (system prompt) | (model default) |
| Ollama `think` | (unset) |
| Temperature | `0.3` |
| top_p | (model default) |
| top_k | (model default) |
| num_ctx | `65536` |
| num_predict | `40000` |
| Source truncated | `no` |
| Review prompt SHA-256 | `82bd5f768ca9` |
| Scorer model | `Qwen3-Coder-30B-imatrix:Q3_K_M` |
| Scorer temperature | `0.3` |
| Scorer reasoning | (model default) |
| Scorer `think` | (unset) |
| Scorer attempts | `1` |
| Grounding mode | `enforce` |
| Grounding downgrades | `0` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 7edff07` |
