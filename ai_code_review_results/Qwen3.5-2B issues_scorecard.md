# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `46d4dd3`

> ⚠ **3 row(s) rated Found name a target that never appears in the review** (D3, D6, D8). Adjusted Found: **16** of 70. See the spot-check below.

Total: 19 Found / 37 Partial / 14 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | SampleBankingApp/Services/AuthService.cs:32 - "SQL injection via string interpolation: `SELECT * FROM Users WHERE Username = '{username}' AND Password = '{hashedPassword}'`" |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | SampleBankingApp/Services/AuthService.cs:17 - "Hardcoded password constant `AdminBypassPassword = \"SuperAdmin2024\"`" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | SampleBankingApp/Services/AuthService.cs:30 - "MD5 hashing function using `MD5.Create()` - Weak cryptographic algorithm" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | SampleBankingApp/Services/UserService.cs:99 - "SQL injection via string interpolation: `VALUES ({fromId}, {toId}, ...)`" |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Partial | SampleBankingApp/Services/UserService.cs:76 - "SQL query uses `OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY` - Syntax may not work in all databases" |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | SampleBankingApp/Services/TransactionService.cs:71 - "Balance update: `Balance + amount + interestBonus` - Should be `Balance + amount`" |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Partial | SampleBankingApp/Services/UserService.cs:99 - "SQL injection via string interpolation: `VALUES ({fromId}, {toId}, ...)`" |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | SampleBankingApp/appsettings.json:3 - "Hardcoded connection string with password in production environment" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Partial | SampleBankingApp/Controllers/AuthController.cs:25 - "_logger.LogWarning(\"Failed login attempt for username: {Username}\", request.Username); - Logs sensitive data" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Partial | SampleBankingApp/Controllers/UserController.cs:52 - "`return StatusCode(500, ex.Message);` - Exposes full exception message to client" |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Partial | SampleBankingApp/Controllers/UserController.cs:66 - "`_logger.LogError(ex, \"Error deleting user {Id}\", id);` - Logs sensitive data" |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Partial | SampleBankingApp/Services/TransactionService.cs:72 - "Balance update: `Balance + amount + interestBonus` - Should be `Balance + amount`" |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Partial | SampleBankingApp/Services/TransactionService.cs:71 - "Interest bonus calculated as `amount * 0.05m * 1` - Rate appears correct but logic unclear" |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | SampleBankingApp/Services/UserService.cs:72 - "Page offset calculation: `skip = page * pageSize` - Correct formula" |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | SampleBankingApp/Services/TransactionService.cs:71 - "Interest bonus calculated as `amount * 0.05m * 1` - Rate appears correct but logic unclear" |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Partial | SampleBankingApp/Controllers/TransactionController.cs:26 - "`int.Parse(userIdClaim!)` - Could throw exception on invalid ID format" |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | SampleBankingApp/Services/UserService.cs:72 - "Page offset calculation: `skip = page * pageSize` - Correct formula" |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Partial | SampleBankingApp/Services/UserService.cs:101 - "Row iteration without null check: `row[\"Username\"]` - Could throw NullReferenceException" |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | SampleBankingApp/Services/AuthService.cs:70 - "JWT secret key hardcoded in code: `builder.Configuration[\"Jwt:SecretKey\"]!`" |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Partial | SampleBankingApp/Controllers/TransactionController.cs:53-59 - "Catch block swallowing exceptions and returning empty response" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | SampleBankingApp/Services/EmailService.cs:16 - "SmtpClient instance field - Not thread-safe, socket never released" |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Partial | SampleBankingApp/Services/AuthService.cs:34 - "SqlConnection created directly without proper transaction handling" |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Partial | SampleBankingApp/Controllers/TransactionController.cs:56 - "`throw new NotImplementedException();` - Production error should return proper status code" |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | SampleBankingApp/Controllers/UserController.cs:48 - "`return BadRequest(ex.Message);` - Exposes full exception message to client" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Missed | _(ungrounded: no matching sentence in review)_ |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | SampleBankingApp/Controllers/AuthController.cs:25 - "_logger.LogWarning(\"Failed login attempt for username: {Username}\", request.Username); - Logs sensitive data" |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Partial | SampleBankingApp/Services/AuthService.cs:34 - "SqlConnection created directly without proper transaction handling" |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Missed | _(ungrounded: no matching sentence in review)_ |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Missed | _(ungrounded: no matching sentence in review)_ |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | SampleBankingApp/Services/EmailService.cs:16 - "SmtpClient instance field - Not thread-safe, socket never released" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Partial | SampleBankingApp/Services/EmailService.cs:39-43 - "MailMessage created but not disposed" |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Partial | SampleBankingApp/Services/AuthService.cs:70 - "JWT secret key hardcoded in code: `builder.Configuration[\"Jwt:SecretKey\"]!`" |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Missed | _(ungrounded: no matching sentence in review)_ |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | SampleBankingApp/Services/EmailService.cs:22 - "Configuration value for SMTP host - Could be better to use Environment variable" |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | SampleBankingApp/Services/EmailService.cs:68 - "username.ToUpper()" |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | SampleBankingApp/Helpers/StringHelper.cs:14, 24 - "`email.Length` and `username.Length` throw if argument is `null`" |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Partial | SampleBankingApp/Controllers/TransactionController.cs:19, 31 - "`int.Parse(userIdClaim!)` - Could throw exception on invalid ID format" |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | SampleBankingApp/Controllers/UserController.cs:28 - "UpdateUser" |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Missed | _(ungrounded: no matching sentence in review)_ |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Missed | _(ungrounded: no matching sentence in review)_ |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | SampleBankingApp/Services/EmailService.cs:10 - "`TransferSubject = \"Transfer Notification - BankingApp\";` - Magic string literal" |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Partial | SampleBankingApp/Helpers/StringHelper.cs:14, 24 - "`email.Length` and `username.Length` throw if argument is `null`" |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Missed | _(ungrounded: no matching sentence in review)_ |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Dead code identified in methods defined but never called: `HashPasswordSha1` |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Partial | SampleBankingApp/Services/AuthService.cs:68 - "JWT expiration set to 30 days - Acceptable but consider shorter default" |
| D3 | `TableExists` — never called from any service or controller. | Found | Dead code identified in methods defined but never called: `TableExists` |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Dead code identified in methods defined but never called: `ExecuteQueryWithParams` |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Partial | SampleBankingApp/Services/EmailService.cs:79 - "BuildHtmlTemplate" |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Dead code identified in methods defined but never called: `SendWelcomeEmailHtml` |
| D7 | `FormatCurrency` — private, never called. | Partial | SampleBankingApp/Services/TransactionService.cs:91 - "FormatCurrency" |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | Dead code identified in methods defined but never called: `IsWithinDailyLimit` |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Partial | SampleBankingApp/Helpers/StringHelper.cs:49 - "ObfuscateAccount" |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | Dead code identified in methods defined but never called: `ToTitleCase` |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Partial | SampleBankingApp/Helpers/StringHelper.cs:37 - "JoinWithSeparatorFixed" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | SampleBankingApp/Services/UserService.cs:10 - "Static audit log collection - Not thread-safe" |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Missed | _(ungrounded: no matching sentence in review)_ |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Missed | _(ungrounded: no matching sentence in review)_ |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | SampleBankingApp/Services/EmailService.cs:16 - "SmtpClient instance field - Not thread-safe, socket never released" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Missed | _(ungrounded: no matching sentence in review)_ |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Missed | _(ungrounded: no matching sentence in review)_ |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | SampleBankingApp/appsettings.json:3 - "Hardcoded connection string with password in production environment" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | SampleBankingApp/appsettings.json:16 - "Logging level set to Debug for production namespaces" |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Partial | SampleBankingApp/Controllers/AuthController.cs:25 - "_logger.LogWarning(\"Failed login attempt for username: {Username}\", request.Username); - Logs sensitive data" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Partial | SampleBankingApp/Program.cs:37 - "Open CORS policy" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | SampleBankingApp/appsettings.json:38 - "CORS policy overly permissive: `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | SampleBankingApp/(project root) - "No appsettings.Production.json" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project found. Critical tests needed: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results | Found | Missing Unit Tests section addressed in review - "No test project found" and lists critical areas needing tests |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Partial | `SearchUsers` | yes | under-credited? |
| C7 | Partial | `RecordTransaction` | **no** | - |
| R3 | Partial | `GenerateJwtToken` | yes | under-credited? |
| E7 | Partial | `rate limit` | **no** | - |
| N3 | Partial | `SmtpPort` | **no** | - |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Found | `TableExists` | **no** | **MIS-CREDIT** |
| D4 | Found | `ExecuteQueryWithParams` | yes | - |
| D5 | Partial | `BuildHtmlTemplate` | **no** | - |
| D6 | Found | `SendWelcomeEmailHtml` | **no** | **MIS-CREDIT** |
| D7 | Partial | `FormatCurrency` | **no** | - |
| D8 | Found | `IsWithinDailyLimit` | **no** | **MIS-CREDIT** |
| D9 | Partial | `ObfuscateAccount` | yes | under-credited? |
| D10 | Found | `ToTitleCase` | yes | - |
| D11 | Partial | `JoinWithSeparatorFixed` | yes | under-credited? |
| CF9 | Partial | `appsettings.Production` | **no** | - |

**Adjusted Found: 16 of 70** (19 reported, less 3 mis-credited).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3.5-2B-imatrix:Q4_K_S` |
| Reasoning strength (system prompt) | (model default) |
| Ollama `think` | `medium` |
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
| Grounding downgrades | `14` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 46d4dd3` |
