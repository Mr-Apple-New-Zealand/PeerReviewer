# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `3601896`

Total: 55 Found / 12 Partial / 3 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | SampleBankingApp/Services/AuthService.cs line 32: "Login builds SQL with interpolated username and hashed password enabling injection." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | SampleBankingApp/Services/AuthService.cs line 17: "AdminBypassPassword constant creates a backdoor account." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | SampleBankingApp/Services/AuthService.cs line 30: "Password hashed with MD5 which is cryptographically broken." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | SampleBankingApp/Services/UserService.cs line 47: "UpdateUser builds UPDATE with interpolated email and username enabling SQL injection." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | SampleBankingApp/Services/UserService.cs line 99: "SearchUsers calls ExecuteQuery with interpolated LIKE clause enabling SQL injection." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | SampleBankingApp/Services/TransactionService.cs line 47: "UPDATE statement built with string interpolation enabling SQL injection." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | SampleBankingApp/Services/TransactionService.cs line 89: "RecordTransaction builds INSERT with interpolated values enabling SQL injection." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | SampleBankingApp/appsettings.json line 3: "Production connection string contains hardcoded SA password." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | SampleBankingApp/Program.cs line 24: "JWT ValidateLifetime is false allowing expired tokens." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | SampleBankingApp/Controllers/UserController.cs line 43: "UpdateUser allows updating any user id without authorization check." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | SampleBankingApp/Controllers/UserController.cs line 61: "DeleteUser allows deleting any user without ownership check." |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | SampleBankingApp/Services/TransactionService.cs line 25: "Transfer allows zero amount." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | SampleBankingApp/Services/TransactionService.cs line 42: "Balance check compares to amount not totalDebit allowing negative balance after fee." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | SampleBankingApp/Services/UserService.cs line 72: "Pagination skip calculated as page * pageSize causing off by one." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | SampleBankingApp/Services/TransactionService.cs line 68: "Magic number 0.05m used for interest rate." This addresses the incorrect value but not the full description including the recurring accrual issue |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | SampleBankingApp/Services/TransactionService.cs line 24: "Transfer does not prevent self transfer." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | SampleBankingApp/Services/UserService.cs line 20: "Duplicate id validation logic repeated across methods." This mentions duplication but doesn't specifically call out the need for extraction |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs line 31: "String concatenation in loop causes O(n²) performance." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | Review does not mention GenerateJwtToken or suggest splitting it |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | SampleBankingApp/Services/UserService.cs line 105: "Catch block swallows exception and returns empty list hiding errors." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | SampleBankingApp/Services/EmailService.cs line 75: "Catch block swallows exception after console logging." This addresses the broad catch but not specifically about silent discard of NullReferenceExceptions |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | SampleBankingApp/Services/TransactionService.cs line 47: "Two separate UPDATEs without transaction risk partial update." |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Partial | SampleBankingApp/Services/TransactionService.cs line 52: "Email sent after DB writes without rollback on failure." This addresses email sending timing but not specifically about the transactional inconsistency |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | SampleBankingApp/Controllers/UserController.cs line 52: "Returns raw exception message to client leaking internals." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 52: "ExecuteNonQuery opens connection and closes only on success path." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed | _(ungrounded: no matching sentence in review)_ |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | SampleBankingApp/Services/AuthService.cs line 34: "SqlConnection created and opened without using causing leak." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 21: "GetOpenConnection returns SqlConnection without disposal contract." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 52: "ExecuteNonQuery opens connection and closes only on success path." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | SampleBankingApp/Services/EmailService.cs line 22: "SmtpClient stored as instance field never disposed." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | SampleBankingApp/Services/EmailService.cs lines 39, 69: "MailMessage created without using causing resource leak." |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | SampleBankingApp/Program.cs line 28: "Encoding.UTF8.GetBytes called with jwtSecret! assuming non null." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | SampleBankingApp/Services/TransactionService.cs lines 36, 37: "Rows[0] accessed without checking Rows.Count leading to exception." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | SampleBankingApp/Services/EmailService.cs line 26: "NetworkCredential constructed with config values that may be null." This addresses the parsing issue but doesn't specifically mention fallback behavior |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | _(ungrounded: no matching sentence in review)_ |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | SampleBankingApp/Helpers/StringHelper.cs lines 13, 22: "IsValidEmail accesses Length without null check causing NullReference." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | SampleBankingApp/Controllers/TransactionController.cs line 27: "userIdClaim! used without null check causing NullReference." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | SampleBankingApp/Controllers/UserController.cs line 50: "Catches generic Exception." This addresses exception handling but not specifically about null request checks |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Partial | SampleBankingApp/Services/TransactionService.cs line 68: "Magic number 0.05m used for interest rate." This addresses one magic number but not the fee or transaction limits |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Partial | SampleBankingApp/Services/UserService.cs line 23: "Magic number 1000000 used for id upper bound." This addresses one magic number but not the deposit cap |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | SampleBankingApp/Services/EmailService.cs lines 40, 69: "Hardcoded sender email notifications@company.com." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Partial | SampleBankingApp/Helpers/StringHelper.cs lines 13, 22: "Magic number 254 used for email length limit." This addresses one magic number but not the others |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | SampleBankingApp/Services/UserService.cs line 70: "Magic number 50 used for max page size." |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | SampleBankingApp/Services/AuthService.cs line 91: "Method HashPasswordSha1 has no callers." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | SampleBankingApp/Services/AuthService.cs line 105: "Code after unconditional return in ValidateToken is unreachable." |
| D3 | `TableExists` — never called from any service or controller. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 59: "Method TableExists has no callers." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 68: "Method ExecuteQueryWithParams is obsolete and unused." |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | SampleBankingApp/Services/EmailService.cs line 81: "Method BuildHtmlTemplate is only used by dead SendWelcomeEmailHtml." |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | SampleBankingApp/Services/EmailService.cs line 86: "Method SendWelcomeEmailHtml has no callers." |
| D7 | `FormatCurrency` — private, never called. | Found | SampleBankingApp/Services/TransactionService.cs line 94: "Method FormatCurrency has no callers." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | SampleBankingApp/Services/TransactionService.cs line 77: "Method IsWithinDailyLimit has no callers." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | SampleBankingApp/Helpers/StringHelper.cs line 54: "Method ObfuscateAccount has no callers." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | SampleBankingApp/Helpers/StringHelper.cs line 59: "Method ToTitleCase has no callers." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | SampleBankingApp/Helpers/StringHelper.cs line 38: "Method JoinWithSeparatorFixed has no callers." |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | SampleBankingApp/Services/UserService.cs line 10: "Static mutable List _auditLog accessed without synchronization." This addresses one static field but not the other |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | SampleBankingApp/Helpers/StringHelper.cs lines 16, 25: "new Regex instantiated per call causing allocation overhead." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs line 31: "String concatenation in loop causes O(n²) performance." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | SampleBankingApp/Services/EmailService.cs line 22: "SmtpClient stored as instance field never disposed." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | SampleBankingApp/Helpers/StringHelper.cs line 65: "Method IsBlank has no callers." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 19: "GetOpenConnection leaks resource ownership to caller." |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | SampleBankingApp/appsettings.json line 3: "Production connection string contains hardcoded SA password." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | SampleBankingApp/appsettings.json line 18: "LogLevel Default set to Debug for production." This addresses one part but not the Microsoft/System namespace settings |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | SampleBankingApp/Program.cs line 24: "JWT ValidateLifetime is false allowing expired tokens." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | SampleBankingApp/Program.cs line 36: "HTTPS redirection is commented out disabling HTTPS enforcement." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | SampleBankingApp/Program.cs line 34: "UseDeveloperExceptionPage enabled unconditionally exposing errors in production." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | SampleBankingApp/Program.cs line 38: "CORS policy allows any origin method and header." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp/SampleBankingApp.csproj line 8: "DebugSymbols true in release build." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | SampleBankingApp/SampleBankingApp.csproj line 15: "Newtonsoft.Json version 12.0.3 is outdated." |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | Review mentions appsettings but does not specifically address missing Production config file |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project exists. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results | Found | SampleBankingApp/Services/AuthService.cs line 28: "Login with MD5 and SQL injection needs boundary tests." This confirms the general need for unit testing across key areas. |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Missed | `GenerateJwtToken` | **no** | - |
| E7 | Missed | `rate limit` | **no** | - |
| N3 | Partial | `SmtpPort` | **no** | - |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Found | `TableExists` | yes | - |
| D4 | Found | `ExecuteQueryWithParams` | yes | - |
| D5 | Found | `BuildHtmlTemplate` | yes | - |
| D6 | Found | `SendWelcomeEmailHtml` | yes | - |
| D7 | Found | `FormatCurrency` | yes | - |
| D8 | Found | `IsWithinDailyLimit` | yes | - |
| D9 | Found | `ObfuscateAccount` | yes | - |
| D10 | Found | `ToTitleCase` | yes | - |
| D11 | Found | `JoinWithSeparatorFixed` | yes | - |
| CF9 | Partial | `appsettings.Production` | **no** | - |

No mis-credits detected in the watchlist.

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Muse-Glimmer-30B-imatrix:Q4_K_S` |
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
| Grounding downgrades | `2` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 3601896` |
