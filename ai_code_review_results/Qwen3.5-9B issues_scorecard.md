# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `04c7dd4`

Total: 41 Found / 28 Partial / 1 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | SampleBankingApp/Services/AuthService.cs:32 - SQL injection vulnerability via string interpolation in WHERE clause. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | SampleBankingApp/Services/AuthService.cs:53 - Hardcoded admin bypass logic allows unauthorized access. |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Partial | SampleBankingApp/Services/AuthService.cs:63 - MD5 used for password hashing. |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | SampleBankingApp/Services/UserService.cs:47 - SQL injection vulnerability via string interpolation in UPDATE statement. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | SampleBankingApp/Services/UserService.cs:99 - SQL injection vulnerability via string interpolation in LIKE clause. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | SampleBankingApp/Services/TransactionService.cs:47 - SQL injection vulnerability via string interpolation in UPDATE statement. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | SampleBankingApp/Services/TransactionService.cs:90 - SQL injection vulnerability via string interpolation in INSERT statement. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | SampleBankingApp/appsettings.json:3 - Hardcoded database password in configuration file. |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Partial | SampleBankingApp/Program.cs:24 - ValidateLifetime is set to false on JWT. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Partial | SampleBankingApp/Controllers/UserController.cs:52 - Returning raw exception message to client exposes internal error details. |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Partial | SampleBankingApp/Controllers/UserController.cs:48 - Returning raw exception message to client exposes internal error details. |

## Logic Errors

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Partial | SampleBankingApp/Services/TransactionService.cs:42 - Balance check excludes the transaction fee, allowing overdrafts. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | SampleBankingApp/Services/TransactionService.cs:42 - Balance check excludes the transaction fee, allowing overdrafts. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | SampleBankingApp/Services/UserService.cs:72 - Pagination offset calculation uses `page * pageSize` instead of `(page - 1) * pageSize`. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | SampleBankingApp/Services/TransactionService.cs:68 - Interest bonus calculation uses incorrect multiplier logic. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Partial | SampleBankingApp/Controllers/TransactionController.cs:27 - Null-assertion on userIdClaim without verifying existence risks parsing null. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | SampleBankingApp/Services/UserService.cs:47 - SQL injection vulnerability via string interpolation in UPDATE statement. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs:31 - String concatenation in a loop for joining items. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | SampleBankingApp/Services/AuthService.cs:93 - SHA1 used for password hashing. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Partial | SampleBankingApp/Services/UserService.cs:105 - Catching broad Exception and returning empty list instead of propagating error. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | SampleBankingApp/Services/EmailService.cs:56 - Logging exception message to console instead of structured logging. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Partial | SampleBankingApp/Services/TransactionService.cs:47 - SQL injection vulnerability via string interpolation. |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Partial | SampleBankingApp/Controllers/TransactionController.cs:56 - Catching NotImplementedException and returning a 500 status code. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | SampleBankingApp/Controllers/UserController.cs:46 - Catching ArgumentException and returning the raw message to the client. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Partial | SampleBankingApp/Data/DatabaseHelper.cs:21 - SqlConnection is opened but never closed or disposed. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | SampleBankingApp/Services/AuthService.cs:98 - ValidateToken method returns true without validating the token. |

## Resource Leaks

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | SampleBankingApp/Data/DatabaseHelper.cs:21 - SqlConnection is opened but never closed or disposed. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | SampleBankingApp/Data/DatabaseHelper.cs:28 - SqlConnection returned from helper method is not disposed by caller. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | SampleBankingApp/Data/DatabaseHelper.cs:52 - SqlConnection is opened but never closed or disposed. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | SampleBankingApp/Services/EmailService.cs:16 - SmtpClient is held as an instance field and never disposed. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | SampleBankingApp/Services/EmailService.cs:39 - MailMessage is created but not disposed after sending. |

## Missing Null Checks

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | SampleBankingApp/Services/AuthService.cs:70 - Null-assertion on Jwt:SecretKey without checking for null. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Partial | SampleBankingApp/Services/TransactionService.cs:53 - Null-assertion on Email configuration value. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | SampleBankingApp/Services/EmailService.cs:24 - Null-assertion on SmtpPort configuration value. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | SampleBankingApp/Services/EmailService.cs:26 - Null-assertion on Email:Username configuration value. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | SampleBankingApp/Helpers/StringHelper.cs:13 - Magic number 254 used for email length limit. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | SampleBankingApp/Controllers/TransactionController.cs:27 - Null-assertion on userIdClaim without verifying existence risks parsing null. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | SampleBankingApp/Controllers/UserController.cs:48 - Returning raw exception message to client exposes internal error details. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | SampleBankingApp/Services/TransactionService.cs:11 - Magic number 0.015 used for transaction fee rate. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | SampleBankingApp/Services/TransactionService.cs:65 - Magic number 1000000 used for maximum deposit amount. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | SampleBankingApp/Services/EmailService.cs:13 - Magic number 3 used for maximum email retries. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | SampleBankingApp/Helpers/StringHelper.cs:13 - Magic number 254 used for email length limit. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | SampleBankingApp/Services/UserService.cs:70 - Magic number 50 used for maximum page size. |

## Dead Code

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | SampleBankingApp/Services/AuthService.cs:91 - HashPasswordSha1 is never called by any method. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | SampleBankingApp/Services/AuthService.cs:98 - ValidateToken is never called by any method. |
| D3 | `TableExists` — never called from any service or controller. | Partial | SampleBankingApp/Data/DatabaseHelper.cs:49 - TableExists method is not used. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Partial | SampleBankingApp/Data/DatabaseHelper.cs:56 - ExecuteQueryWithParams method is obsolete and unused. |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Partial | SampleBankingApp/Services/EmailService.cs:79 - BuildHtmlTemplate method is not used. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | SampleBankingApp/Services/EmailService.cs:85 - SendWelcomeEmailHtml method is not used. |
| D7 | `FormatCurrency` — private, never called. | Found | SampleBankingApp/Services/TransactionService.cs:94 - FormatCurrency is never called by any method. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | SampleBankingApp/Services/TransactionService.cs:99 - RefundTransaction is never called by any method. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Partial | SampleBankingApp/Helpers/StringHelper.cs:49 - JoinWithSeparatorFixed is never called by any method. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Partial | SampleBankingApp/Helpers/StringHelper.cs:54 - ToTitleCase method is not used. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | SampleBankingApp/Helpers/StringHelper.cs:38 - JoinWithSeparatorFixed is never called by any method. |

## Anti-patterns

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | SampleBankingApp/Services/UserService.cs:85 - GetAuditReport method has three distinct responsibilities. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | SampleBankingApp/Helpers/StringHelper.cs:16 - Regex created inside method called repeatedly. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs:31 - String concatenation in a loop for joining items. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | SampleBankingApp/Services/EmailService.cs:16 - SmtpClient is held as an instance field and never disposed. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Partial | SampleBankingApp/Helpers/StringHelper.cs:60 - Reimplementing BCL. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Partial | SampleBankingApp/Data/DatabaseHelper.cs:26 - GetOpenConnection method returns a live connection. |

## Configuration Issues

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | SampleBankingApp/appsettings.json:3 - Hardcoded database password in configuration file. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | SampleBankingApp/appsettings.json:18 - Default log level is set to Debug. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | SampleBankingApp/Program.cs:24 - ValidateLifetime is set to false on JWT. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | SampleBankingApp/Program.cs:36 - HTTPS redirection is commented out. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | SampleBankingApp/Program.cs:34 - UseDeveloperExceptionPage is called unconditionally. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | SampleBankingApp/Program.cs:38 - CORS policy allows any origin, method, and header. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp/SampleBankingApp.csproj:8 - DebugSymbols is set to true. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | SampleBankingApp/SampleBankingApp.csproj:15 - Newtonsoft.Json version 12.0.3 is outdated. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | SampleBankingApp/appsettings.json:18 - Default log level is set to Debug. |

## Missing Unit Tests

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results. | Missed | _(ungrounded: no matching sentence in review)_ |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Partial | `GenerateJwtToken` | yes | under-credited? |
| E7 | Partial | `rate limit` | **no** | **UNSUPPORTED** |
| N3 | Found | `SmtpPort` | yes | - |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Partial | `TableExists` | **no** | **UNSUPPORTED** |
| D4 | Partial | `ExecuteQueryWithParams` | **no** | **UNSUPPORTED** |
| D5 | Partial | `BuildHtmlTemplate` | **no** | **UNSUPPORTED** |
| D6 | Found | `SendWelcomeEmailHtml` | yes | - |
| D7 | Found | `FormatCurrency` | yes | - |
| D8 | Found | `IsWithinDailyLimit` | yes | - |
| D9 | Partial | `ObfuscateAccount` | **no** | **UNSUPPORTED** |
| D10 | Partial | `ToTitleCase` | **no** | **UNSUPPORTED** |
| D11 | Found | `JoinWithSeparatorFixed` | yes | - |
| CF9 | Partial | `appsettings.Production` | **no** | **UNSUPPORTED** |
| UT | Missed | `Tests.csproj` | yes | under-credited? |
| C2 | Found | `SuperAdmin2024` | yes | - |
| C3 | Partial | `MD5` | yes | under-credited? |
| C9 | Partial | `ValidateLifetime` | yes | under-credited? |
| L3 | Found | `GetUsersPage` | yes | - |
| L4 | Found | `0.05` | yes | - |
| E1 | Partial | `SearchUsers` | yes | under-credited? |
| E5 | Found | `ex.Message` | yes | - |
| RL4 | Found | `SmtpClient` | yes | - |
| RL5 | Found | `MailMessage` | yes | - |
| N2 | Partial | `Rows[0]` | yes | under-credited? |
| N4 | Partial | `ToUpper` | **no** | **UNSUPPORTED** |
| M1 | Found | `TransactionFeeRate` | yes | - |
| M2 | Found | `1000000` | yes | - |
| D2 | Found | `ValidateToken` | yes | - |
| A1 | Partial | `_auditLog` | **no** | **UNSUPPORTED** |
| A2 | Found | `Regex` | yes | - |
| A5 | Partial | `IsBlank` | **no** | **UNSUPPORTED** |
| CF3 | Found | `ValidateLifetime` | yes | - |
| CF4 | Found | `UseHttpsRedirection` | yes | - |
| CF5 | Found | `UseDeveloperExceptionPage` | yes | - |
| CF6 | Found | `AllowAnyOrigin` | yes | - |
| CF7 | Found | `DebugType` | yes | - |
| CF8 | Found | `Newtonsoft` | yes | - |

No mis-credits detected in the watchlist.

> **10 row(s) rated `Partial` whose target string appears NOWHERE in the review** (E7, D3, D4, D5, D9, D10, CF9, N4, A1, A5). A Partial on an unmentioned issue is a Missed; the reported Missed count is correspondingly understated.

> **6 row(s) rated `Partial`/`Missed` whose target string IS present in the review** (R3, UT, C3, C9, E1, N2). The score is left as the scorer rated it; read these rows before trusting the Missed count.

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3.5-9B-imatrix:Q4_K_S` |
| Reasoning strength (system prompt) | (model default) |
| System prompt | `You are an expert computer programmer with an eye for detail, who loves to provide high quality answers.` |
| Ollama `think` | `False` |
| Temperature | `0.0` |
| top_p | (model default) |
| top_k | (model default) |
| Effort (Anthropic only) | (n/a) |
| num_ctx | `65536` |
| num_predict | `40000` |
| Source truncated | `no` |
| Review prompt SHA-256 | `82bd5f768ca9` |
| Scorer model | `Qwen3-Coder-30B-imatrix:Q3_K_M` |
| Scorer temperature | `0.0` |
| Scorer reasoning | (model default) |
| Scorer system prompt | `You are an expert computer programmer with an eye for detail, who loves to provide high quality answers.` |
| Scorer `think` | (unset) |
| Scorer attempts | `1` |
| Grounding mode | `enforce` |
| Grounding downgrades | `1` |
| Self-declared-absent downgrades | `0` |
| Rows misaligned with ISSUES.md | `0` |
| Review citations past end of file | `1 of 97` |
| Precision (checkable Found rows) | `100% (24 of 24)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 04c7dd4` |
