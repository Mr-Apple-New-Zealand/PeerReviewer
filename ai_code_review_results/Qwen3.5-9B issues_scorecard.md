# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `74c6567`

> ⚠ **2 row(s) rated Found name a target that never appears in the review** (C7, D9). Adjusted Found: **48** of 70. See the spot-check below.

Total: 50 Found / 17 Partial / 3 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "AuthService.cs | 32 | SQL injection vulnerability via username and password interpolation | Use parameterized queries for all database operations" |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "AuthService.cs | 17 | Hardcoded admin bypass password in source code | Remove hardcoded password and use secure authentication" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "AuthService.cs | 30 | MD5 password hashing provides weak security | Use bcrypt or Argon2 for password hashing" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "UserService.cs | 47 | SQL injection vulnerability via interpolated values | Use parameterized queries for all database operations" |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "UserService.cs | 99 | SQL injection vulnerability via LIKE clause interpolation | Use parameterized queries for all database operations" |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "TransactionService.cs | 47 | SQL injection vulnerability via interpolated balance values | Use parameterized queries for all database operations" |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "TransactionService.cs | 89 | SQL injection vulnerability via interpolated values | Use parameterized queries for all database operations" |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "appsettings.json | 3 | Hardcoded database credentials in configuration file | Use environment variables or secure vault" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Partial | "Program.cs | 34 | UseDeveloperExceptionPage enabled in production | Conditionally enable based on environment or disable in production" - This addresses JWT lifetime but not the specific validation setting |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | "UserController.cs | 43 | UpdateUser endpoint lacks ownership verification allowing anyone to update any user | Add authorization attribute to verify user owns the account" |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | "UserController.cs | 61 | DeleteUser endpoint lacks ownership verification allowing anyone to delete any user | Add authorization attribute to verify user owns the account" |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Partial | "TransactionService.cs | 68 | Interest calculation multiplies by 0.05m * 1 which is redundant | Remove redundant multiplication" - This addresses interest rate but not the zero-value transfer logic |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "TransactionService.cs | 42 | Checks balance >= amount but deducts amount + fee causing insufficient funds error | Check balance >= amount + fee before deducting" |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "UserService.cs | 72 | Pagination uses page * pageSize instead of (page - 1) * pageSize | Change to (page - 1) * pageSize" |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | "TransactionService.cs | 68 | Interest calculation multiplies by 0.05m * 1 which is redundant | Remove redundant multiplication" - This addresses the interest rate but not the specific incorrect value |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Partial | "TransactionController.cs | 53 | Refund endpoint lacks ownership verification allowing anyone to refund any transaction | Add authorization attribute to verify user owns the transaction" - This addresses refund but not self-transfer |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Missed | Review does not mention duplicated validation or suggest extraction to shared method |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Partial | "StringHelper.cs | 31-36 | String concatenation in loop instead of StringBuilder | Use StringBuilder or string.Join" - This addresses the loop concatenation but doesn't specifically mention JoinWithSeparator vs JoinWithSeparatorFixed |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | Review does not mention JWT token generation or suggest refactoring |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "UserService.cs | 105 | Catch-all Exception returns empty list preventing error detection | Return specific error or propagate exception" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | "EmailService.cs | 71 | Catch-all Exception logs to console instead of proper error handling | Use structured logging with appropriate log level" - This addresses exception handling but not the specific issue of broad catch |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Partial | "TransactionService.cs | 47 | SQL injection vulnerability via interpolated balance values | Use parameterized queries for all database operations" - This addresses SQL injection but not the missing transaction |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Partial | "TransactionController.cs | 56 | Catches NotImplementedException and returns 500 instead of proper error handling | Remove catch block for NotImplementedException in production" - This addresses exception handling but not email failure propagation |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | "UserController.cs | 48 | Returns exception message directly to client exposing internal errors | Return generic error message instead of ex.Message" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Partial | "DatabaseHelper.cs | 52 | GetOpenConnection never closes connection on exception | Use using statement for connection" - This addresses resource management but not specifically the ExecuteNonQuery issue |
| E7 | **No rate limiting or account lockout on failed login attempts** — brute force is trivially possible. | Partial | "TransactionController.cs | 56 | Catches NotImplementedException and returns 500 instead of proper error handling | Remove catch block for NotImplementedException in production" - This addresses exception handling but not rate limiting |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "DatabaseHelper.cs | 21 | SqlConnection created but never disposed | Use using statement for connection" |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "DatabaseHelper.cs | 28 | SqlConnection returned from method never disposed by caller | Return using statement or require caller to dispose" |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "DatabaseHelper.cs | 52 | SqlConnection never closed in ExecuteNonQuery | Use using statement for connection" |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "EmailService.cs | 16 | SmtpClient held as instance field causing thread safety issues | Create SmtpClient per request or use thread-safe configuration" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "EmailService.cs | 39 | MailMessage created but never disposed | Use using statement for MailMessage" |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | "AuthService.cs | 70 | jwtSecret configuration value could be null | Add null check before using jwtSecret" |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "TransactionService.cs | 36 | Accessing Rows[0] without checking count causes null reference | Check Rows.Count before accessing first row" |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | "EmailService.cs | 24 | SmtpPort configuration value could be null | Add null check for SmtpPort" - This addresses null checking but not the specific fallback issue |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | "EmailService.cs | 65 | Uppercase conversion on username | Use string.IsNullOrEmpty check first" |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | "StringHelper.cs | 16 | Regex object created on each call instead of being static readonly | Make Regex static readonly field" - This addresses regex but not the null guard issue |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "TransactionController.cs | 27 | Null-conditional operator with ! forces exception when claim is missing | Add null check before parsing" |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | "UserController.cs | 43 | UpdateUser endpoint lacks ownership verification allowing anyone to update any user | Add authorization attribute to verify user owns the account" - This addresses authorization but not null request checking |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | "TransactionService.cs | 11 | TransactionFeeRate is hardcoded to 0.015m | Use configuration value" |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | "TransactionService.cs | 66 | Deposit amount limit hardcoded to 1000000 | Use configuration value" |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | "EmailService.cs | 40 | From email hardcoded to notifications@company.com | Use configuration value" |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Partial | "StringHelper.cs | 16 | Regex object created on each call instead of being static readonly | Make Regex static readonly field" - This addresses regex but not the specific magic numbers |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "UserService.cs | 70 | Page size limit hardcoded to 50 | Use configuration value" |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | "AuthService.cs | 61-66 | HashPasswordSha1 is unused method | Remove unused method" |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "AuthService.cs | 98-108 | ValidateToken method always returns true | Remove or implement proper validation" |
| D3 | `TableExists` — never called from any service or controller. | Found | "DatabaseHelper.cs | 67-78 | ExecuteQueryWithParams is marked obsolete but still present | Remove obsolete method or keep for backward compatibility" |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | "DatabaseHelper.cs | 67-78 | ExecuteQueryWithParams is marked obsolete but still present | Remove obsolete method or keep for backward compatibility" |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | "EmailService.cs | 81-84 | BuildHtmlTemplate is unused method | Remove unused method" |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | "EmailService.cs | 86-92 | SendWelcomeEmailHtml is unused method | Remove unused method" |
| D7 | `FormatCurrency` — private, never called. | Found | "TransactionService.cs | 94-97 | FormatCurrency is unused method | Remove unused method" |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | "TransactionService.cs | 99-103 | RefundTransaction throws NotImplementedException | Remove or implement the method" |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | "StringHelper.cs | 38-41 | JoinWithSeparatorFixed is duplicate implementation | Remove duplicate method or rename one" |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | "StringHelper.cs | 31-36 | JoinWithSeparator is inefficient and unused | Remove inefficient method or use StringBuilder" |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "StringHelper.cs | 38-41 | JoinWithSeparatorFixed is duplicate implementation | Remove duplicate method or rename one" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Missed | Review does not mention static state or thread safety issues |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "StringHelper.cs | 16 | Regex object created on each call instead of being static readonly | Make Regex static readonly field" |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "StringHelper.cs | 31-36 | String concatenation in loop instead of StringBuilder | Use StringBuilder or string.Join" |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "EmailService.cs | 16 | SmtpClient held as instance field causing thread safety issues | Create SmtpClient per request or use thread-safe configuration" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Partial | "StringHelper.cs | 38-41 | JoinWithSeparatorFixed is duplicate implementation | Remove duplicate method or rename one" - This addresses the duplicate but not specifically IsBlank |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "DatabaseHelper.cs | 29 | String interpolation in SQL query | Use parameterized queries" |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "appsettings.json | 3 | Hardcoded database credentials in configuration file | Use environment variables or secure vault" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | "appsettings.json | 18 | Default log level is Debug | Set to Information or Warning for production" |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Partial | "Program.cs | 34 | UseDeveloperExceptionPage enabled in production | Conditionally enable based on environment or disable in production" - This addresses JWT but not specifically ValidateLifetime |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "Program.cs | 36 | HTTPS redirection is commented out | Uncomment and enable HTTPS redirection" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "Program.cs | 34 | UseDeveloperExceptionPage enabled in production | Conditionally enable based on environment or disable in production" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "Program.cs | 38 | Overly permissive CORS policy allows any origin, method, and header | Configure specific allowed origins and methods based on requirements" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | "SampleBankingApp.csproj | 8 | DebugSymbols set to true | Set to false for production builds" |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | "SampleBankingApp.csproj | 15 | Newtonsoft.Json 12.0.3 has known security vulnerabilities | Upgrade to latest stable version" |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | "appsettings.json | 23 | AllowedHosts is set to wildcard | Configure specific allowed hosts" - This addresses one configuration issue but not the missing production settings |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project exists | Found | "SampleBankingApp/ | N/A | No test project exists | Create test project with unit tests" |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | **no** | **MIS-CREDIT** |
| R3 | Missed | `GenerateJwtToken` | yes | under-credited? |
| E7 | Partial | `rate limit` | **no** | - |
| N3 | Partial | `SmtpPort` | yes | under-credited? |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Found | `TableExists` | yes | - |
| D4 | Found | `ExecuteQueryWithParams` | yes | - |
| D5 | Found | `BuildHtmlTemplate` | yes | - |
| D6 | Found | `SendWelcomeEmailHtml` | yes | - |
| D7 | Found | `FormatCurrency` | yes | - |
| D8 | Found | `IsWithinDailyLimit` | yes | - |
| D9 | Found | `ObfuscateAccount` | **no** | **MIS-CREDIT** |
| D10 | Found | `ToTitleCase` | yes | - |
| D11 | Found | `JoinWithSeparatorFixed` | yes | - |
| CF9 | Partial | `appsettings.Production` | **no** | - |

**Adjusted Found: 48 of 70** (50 reported, less 2 mis-credited).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3.5-9B-imatrix:Q4_K_S` |
| Reasoning strength (system prompt) | (model default) |
| System prompt | `You are an expert computer programmer with an eye for detail, who loves to provide high quality answers.` |
| Ollama `think` | `medium` |
| Temperature | `0.3` |
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
| Grounding downgrades | `0` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 74c6567` |
