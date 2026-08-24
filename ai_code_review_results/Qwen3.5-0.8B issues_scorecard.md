# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `46d4dd3`

Total: 6 Found / 31 Partial / 33 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Missed | Review does not mention the specific Login method or its SQL injection vulnerability |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Missed | Review does not name AdminBypassPassword constant |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Partial | Review mentions "MD5 hashing vulnerable to collision attacks" but doesn't specifically mention the missing salt aspect of this vulnerability |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Missed | Review does not name specific methods like UpdateUser or DeleteUser for SQL injection |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Missed | Review does not mention SearchUsers method or its SQL injection vulnerability |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Missed | Review does not name specific methods like Transfer or Deposit for SQL injection |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Missed | Review does not mention RecordTransaction method or its SQL injection vulnerability |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Partial | Review mentions "Hardcoded credentials in connection string" but doesn't specifically name the appsettings.json file or all hardcoded secrets |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Partial | Review mentions JWT ValidateLifetime = false but does not explicitly mention that this disables token expiration |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Missed | Review does not name UserController or specific endpoint for access control issue |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Missed | Review does not name UserController or specific DELETE endpoint for missing authorization |

## Logic Errors

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Partial | Review mentions "Incorrect boundary condition for negative ID parsing" but doesn't specifically address the zero-value transfer logic |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Partial | Review mentions "Balance calculation excludes deposit fee component" but doesn't specifically mention that this affects the balance check logic |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review identifies "Off-by-one error in pagination offset calculation" and suggests correct formula |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | Review mentions "Fee rate applied incorrectly (5% vs 1%)" but doesn't specifically mention that this is about interest rate |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Partial | Review mentions "Missing self-referential checks for user IDs" but doesn't specifically name this as a self-transfer issue |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Missed | Review does not mention specific duplicated validation logic or suggest extraction |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Partial | Review mentions "JoinWithSeparator uses string concatenation in loop" but doesn't specifically mention the fixed version |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | Review does not name GenerateJwtToken method or suggest refactoring |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Missed | Review does not name SearchUsers method or its exception handling issue |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | Review mentions "Raw exception message returned to HTTP clients" but doesn't specifically mention SendWelcomeEmail's overly broad Exception catch |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Missed | Review does not name specific TransactionService methods or mention missing transactions |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Missed | Review does not name Transfer method or its email handling issue |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Partial | Review mentions "Raw exception message returned to HTTP clients" but doesn't specifically mention this exact pattern in UserController |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Missed | Review does not name DatabaseHelper or specific ExecuteNonQuery method |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | Review mentions "No account lockout on failed login attempts" but doesn't specifically mention the AuthController context |

## Resource Leaks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Partial | Review mentions "SqlConnection opened but never closed" but doesn't specifically name Login method |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Missed | Review does not mention GetOpenConnection or specific DatabaseHelper methods |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Partial | Review mentions "Exception path skips Close() or Dispose()" but doesn't specifically name ExecuteNonQuery method |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Missed | Review does not mention SmtpClient or EmailService |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Partial | Review mentions "MailMessage created but never disposed" but doesn't specifically name these methods |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Missed | Review does not mention Jwt:SecretKey or specific null handling issue |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Partial | Review mentions "DataTable.Rows[0] accessed without Rows.Count > 0 check" but doesn't specifically name these variables |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | Review mentions "Debug symbols enabled in release builds" but doesn't specifically address null config handling |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | Review does not mention username or specific null reference issue |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | Review mentions "IsBlank checks value == null but not value == """ but doesn't specifically name the length access issues |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Missed | Review does not mention User.FindFirst or specific parsing issue |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | Review mentions "UpdateUserRequest used in controller action without null check" but doesn't specifically name UpdateUser method |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Partial | Review mentions "TransactionFeeRate hardcoded without validation" but doesn't specifically name these variables |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Missed | Review does not mention specific numeric constant or deposit cap |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | Review mentions "JWT:SecretKey hardcoded in config" but doesn't specifically name email address constants |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Partial | Review mentions "TransactionFeeRate hardcoded without validation" but doesn't specifically mention these numeric literals |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Partial | Review mentions "MaxTransactionsPerDay hardcoded without context" but doesn't specifically name this page size constant |

## Dead Code

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Missed | Review does not mention HashPasswordSha1 or specific dead method |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Missed | _(ungrounded: no matching sentence in review)_ |
| D3 | `TableExists` — never called from any service or controller. | Missed | Review does not mention TableExists method |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Partial | Review mentions "ExecuteQueryWithParams marked obsolete but still exists" but doesn't specifically name the method |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Missed | Review does not mention BuildHtmlTemplate or specific dead code chain |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Missed | _(ungrounded: no matching sentence in review)_ |
| D7 | `FormatCurrency` — private, never called. | Missed | Review does not mention FormatCurrency method |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Missed | Review does not mention IsWithinDailyLimit or specific dead code |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Partial | Review mentions "IsBlank method checks value == null but not value == """ but doesn't specifically name ObfuscateAccount |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Missed | Review does not mention ToTitleCase or specific dead code |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Partial | Review mentions "StringBuilder created but never closed" but doesn't specifically name JoinWithSeparatorFixed |

## Anti-patterns

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Missed | Review does not mention static variables or threading issues |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Partial | Review mentions "Regex inside repeated method calls (IsValidEmail)" but doesn't specifically name this anti-pattern |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Partial | Review mentions "JoinWithSeparator uses string concatenation in loop" but doesn't specifically name the anti-pattern |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Missed | Review does not mention SmtpClient or threading issues |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Partial | Review mentions "IsBlank checks value == null but not value == """ but doesn't specifically name this anti-pattern |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Missed | Review does not mention GetOpenConnection or specific anti-pattern |

## Configuration Issues

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies "Production secrets committed to source" and suggests moving sensitive values to configuration files |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | Review mentions "Debug symbols enabled in release builds" but doesn't specifically mention log levels or Debug logging |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies JWT ValidateLifetime = false as a security issue and suggests setting it to true |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review identifies "HTTPS disabled in production" and suggests enabling HTTPS redirection |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Partial | Review mentions "UseDeveloperExceptionPage called unconditionally" but doesn't specifically name this configuration issue |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review identifies overly permissive CORS policy and suggests restricting to specific origins only |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | Review identifies "Debug symbols in release build" and suggests disabling debug symbols for production |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | Review mentions "Production secrets committed to source" but doesn't specifically name the outdated package |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Missed | Review does not mention appsettings.Production.json or environment-specific configuration |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results | Missed | _(ungrounded: no matching sentence in review)_ |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Missed | `SearchUsers` | **no** | - |
| C7 | Missed | `RecordTransaction` | **no** | - |
| R3 | Missed | `GenerateJwtToken` | **no** | - |
| E7 | Partial | `rate limit` | yes | under-credited? |
| N3 | Partial | `SmtpPort` | **no** | - |
| D1 | Missed | `HashPasswordSha1` | **no** | - |
| D3 | Missed | `TableExists` | **no** | - |
| D4 | Partial | `ExecuteQueryWithParams` | yes | under-credited? |
| D5 | Missed | `BuildHtmlTemplate` | **no** | - |
| D6 | Missed | `SendWelcomeEmailHtml` | **no** | - |
| D7 | Missed | `FormatCurrency` | **no** | - |
| D8 | Missed | `IsWithinDailyLimit` | **no** | - |
| D9 | Partial | `ObfuscateAccount` | **no** | - |
| D10 | Missed | `ToTitleCase` | **no** | - |
| D11 | Partial | `JoinWithSeparatorFixed` | **no** | - |
| CF9 | Missed | `appsettings.Production` | **no** | - |

No mis-credits detected in the watchlist.

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3.5-0.8B-imatrix:Q4_K_S` |
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
| Grounding downgrades | `3` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 46d4dd3` |
