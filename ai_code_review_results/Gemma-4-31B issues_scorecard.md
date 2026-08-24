# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `3d4ff91`

Total: 45 Found / 25 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | AuthService.cs line 32: "SQL injection via string interpolation in Login method." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | AuthService.cs line 17: "Hardcoded administrative bypass password." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | AuthService.cs line 61: "Use of weak MD5 hashing algorithm for passwords." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | UserService.cs line 47: "SQL injection via interpolation in UpdateUser." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | UserService.cs line 99: "SQL injection via interpolation in SearchUsers." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | TransactionService.cs line 47: "SQL injection via interpolation in Transfer update." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | TransactionService.cs line 89: "SQL injection via interpolation in RecordTransaction." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | appsettings.json line 3: "Production database credentials stored in plain text." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Partial | Program.cs line 24: "JWT lifetime validation is disabled." (does not name specific method or config block) |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | UserController.cs line 39: "Missing ownership check on UpdateUser endpoint." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | UserController.cs line 57: "Missing ownership check on DeleteUser endpoint." |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | TransactionService.cs line 42: "Balance check only verifies amount but deducts amount plus fee." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | TransactionService.cs line 42: "Balance check only verifies amount but deducts amount plus fee." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | UserService.cs line 72: "Pagination skip calculation is off-by-one." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | TransactionService.cs line 68: "Interest bonus calculation contains a redundant multiplication by 1." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Partial | TransactionController.cs lines 27 and 41: "Parse will throw if NameIdentifier claim is missing." (does not name specific method or logic) |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | AuthService.cs line 53: "Admin bypass allows login without verifying account status in DB." (does not name specific duplicated validation) |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | StringHelper.cs line 33: "String concatenation inside a loop." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | AuthService.cs line 91: "Use of weak SHA1 hashing algorithm for passwords." (does not name specific method or refactoring opportunity) |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | UserService.cs line 105: "Broad Exception catch swallows errors and returns empty list." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | EmailService.cs lines 39, 69, 89: "MailMessage is created but not disposed." (does not name specific method or error handling issue) |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | TransactionService.cs line 47: "Multiple database writes in Transfer are not wrapped in a transaction." |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Partial | TransactionService.cs line 52: "Email notification is sent after DB commit and may fail." (does not name specific method or logic) |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | UserController.cs lines 52, 48: "Raw exception message is returned to the HTTP client." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Partial | DatabaseHelper.cs line 52: "SqlConnection from GetOpenConnection is closed but not disposed." (does not name specific method or logic) |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | AuthService.cs lines 34, 37, 38: "SqlConnection is opened but never closed or disposed." (does not name specific missing check or security feature) |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | AuthService.cs lines 34, 37, 38: "SqlConnection is opened but never closed or disposed." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | DatabaseHelper.cs line 28: "SqlConnection from GetOpenConnection is never disposed in ExecuteQuery." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | DatabaseHelper.cs line 52: "SqlConnection from GetOpenConnection is closed but not disposed." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | EmailService.cs line 16: "SmtpClient held as instance field is not thread-safe and not disposed." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | EmailService.cs lines 39, 69, 89: "MailMessage is created but not disposed." |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Program.cs line 28: "GetBytes will throw if Jwt:SecretKey is missing from config." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | TransactionService.cs lines 36, 37: "Accesses Rows[0] without checking if the table has rows." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | EmailService.cs line 22: "SmtpHost configuration value may be null." (does not name specific method or logic) |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | TransactionController.cs lines 27, 41: "Parse will throw if NameIdentifier claim is missing." (does not name specific method or logic) |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | StringHelper.cs lines 16, 25: "Regex object instantiated inside a method." (does not name specific method or logic) |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | TransactionController.cs lines 27, 41: "Parse will throw if NameIdentifier claim is missing." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | UserController.cs line 39: "Missing ownership check on UpdateUser endpoint." (does not name specific method or logic) |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | TransactionService.cs lines 11, 12: "Hardcoded fee rate 0.015m." |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | TransactionService.cs line 65: "Hardcoded deposit cap 1000000." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | EmailService.cs lines 40, 67, 69, 89: "Hardcoded sender email address." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Partial | StringHelper.cs lines 16, 25: "Regex object instantiated inside a method." (does not name specific magic strings or numbers) |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | UserService.cs line 70: "Hardcoded page size limit 50." |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | AuthService.cs line 91: "HashPasswordSha1 method is never called." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Partial | AuthService.cs line 98: "ValidateToken method is never called." (does not name specific unreachable code) |
| D3 | `TableExists` — never called from any service or controller. | Found | DatabaseHelper.cs line 59: "TableExists method is never called." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | DatabaseHelper.cs line 68: "ExecuteQueryWithParams method is never called." |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Partial | EmailService.cs line 86: "SendWelcomeEmailHtml method is never called." (does not name specific unreachable code) |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | EmailService.cs line 86: "SendWelcomeEmailHtml method is never called." |
| D7 | `FormatCurrency` — private, never called. | Found | TransactionService.cs line 94: "FormatCurrency method is never called." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | TransactionService.cs line 77: "IsWithinDailyLimit method is never called." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Partial | StringHelper.cs line 54: "ObfuscateAccount method is never called." (does not name specific dead code) |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | StringHelper.cs line 59: "ToTitleCase method is never called." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Partial | StringHelper.cs line 38: "JoinWithSeparatorFixed method is never called." (does not name specific dead code) |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | UserService.cs lines 10, 11: "Shared mutable static state in _auditLog." (does not name specific method or logic) |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | StringHelper.cs lines 16, 25: "Regex object instantiated inside a method." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | StringHelper.cs line 33: "String concatenation inside a loop." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | EmailService.cs line 16: "SmtpClient held as instance field is not thread-safe and not disposed." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Partial | StringHelper.cs line 65: "IsBlank reimplements string.IsNullOrWhiteSpace." (does not name specific method or logic) |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Partial | DatabaseHelper.cs line 28: "SqlConnection from GetOpenConnection is never disposed in ExecuteQuery." (does not name specific method or logic) |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | appsettings.json line 3: "Production database credentials stored in plain text." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | Program.cs line 18: "Log level set to Debug for production." (does not name specific method or logic) |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Program.cs line 24: "JWT lifetime validation is disabled." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Partial | Program.cs line 36: "HTTPS redirection is commented out." (does not name specific method or logic) |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Program.cs line 34: "Developer exception page enabled unconditionally." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Program.cs line 38: "CORS policy allows any origin." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Partial | SampleBankingApp.csproj line 15: "Outdated Newtonsoft.Json version 12.0.3." (does not name specific method or logic) |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | SampleBankingApp.csproj line 15: "Outdated Newtonsoft.Json version 12.0.3." (does not name specific method or logic) |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | appsettings.json lines 16-20: "Log level set to Debug for production." (does not name specific method or logic) |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | **No test project exists in the solution.** Key areas that need tests include: `AuthService.Login`, `TransactionService.Transfer`, `UserService.GetUsersPage` etc. | Found | Missing Unit Tests line 1: "No test project exists in the solution." |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Partial | `GenerateJwtToken` | **no** | - |
| E7 | Partial | `rate limit` | **no** | - |
| N3 | Partial | `SmtpPort` | **no** | - |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Found | `TableExists` | yes | - |
| D4 | Found | `ExecuteQueryWithParams` | yes | - |
| D5 | Partial | `BuildHtmlTemplate` | **no** | - |
| D6 | Found | `SendWelcomeEmailHtml` | yes | - |
| D7 | Found | `FormatCurrency` | yes | - |
| D8 | Found | `IsWithinDailyLimit` | yes | - |
| D9 | Partial | `ObfuscateAccount` | yes | under-credited? |
| D10 | Found | `ToTitleCase` | yes | - |
| D11 | Partial | `JoinWithSeparatorFixed` | yes | under-credited? |
| CF9 | Partial | `appsettings.Production` | **no** | - |

No mis-credits detected in the watchlist.

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Gemma-4-31B-it-imatrix:Q4_K_M` |
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
| Branch / commit | `main @ 3d4ff91` |
