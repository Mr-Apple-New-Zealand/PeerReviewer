# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22`

> ⚠ **1 row(s) rated Found name a target that never appears in the review** (D6). Adjusted Found: **22** of 70. See the spot-check below.

Total: 23 Found / 46 Partial / 1 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "SQL injection in login method" — review identifies the specific SQL injection vulnerability in the Login method |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Partial | Review mentions "Magic string `AdminBypassPassword` is hardcoded" but does not specifically name the constant "AdminBypassPassword" in the context of backdoor access |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Partial | Review mentions "HashPasswordMd5 method uses an insecure hashing algorithm" but does not specifically name the MD5 hashing issue in the context of broken password hashing |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "Raw SQL queries are constructed using string concatenation" — review identifies the specific SQL injection vulnerability in UpdateUser/DeleteUser methods |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "Raw SQL query in `SearchUsers` method is vulnerable to SQL injection" — review identifies the specific SQL injection vulnerability in SearchUsers method |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Partial | Review mentions "Raw SQL queries are constructed using string concatenation" but does not specifically name the Transfer/Deposit methods or their parameters |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Partial | Review mentions "Raw SQL queries are constructed using string concatenation" but does not specifically name the RecordTransaction method or its parameter |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Partial | Review mentions "Database connection string is hardcoded", "Email SMTP credentials are hardcoded", and "JWT secret key is hardcoded" but does not specifically name the combination of all three credential types |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Partial | Review mentions "JWT validation parameters are hardcoded" but does not specifically name the ValidateLifetime parameter or its disabled state |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Partial | Review mentions "No check for zero or negative amount in transfer method" but does not specifically name the access control issue in UserController |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Partial | Review mentions "No check for zero or negative amount in transfer method" but does not specifically name the authorization issue in UserController |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | "No check for zero or negative amount in transfer method" — review identifies the specific logic error with zero-value transfers |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Partial | Review mentions "Invalid deposit amount check allows for deposits of zero or more than $1,000,000" but does not specifically name the balance check logic error |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "Invalid user ID check in `UpdateUser` method allows for IDs of zero or more than 1,000,000" — review identifies the pagination logic error |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | Review mentions "Interest bonus calculation in the `Deposit` method is hardcoded to always be 0.05% of the deposit amount" but does not specifically name the incorrect interest rate |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Partial | Review mentions "No check for zero or negative amount in transfer method" but does not specifically name the self-transfer logic error |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | Review mentions "Invalid user ID check in `UpdateUser` method allows for IDs of zero or more than 1,000,000" but does not specifically name the duplicated validation issue |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "JoinWithSeparator method concatenates strings in a loop, which is inefficient" — review identifies the specific string concatenation issue |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | Review mentions "JWT validation parameters are hardcoded" but does not specifically name the GenerateJwtToken method or its refactoring opportunity |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "Exception in `SearchUsers` method is swallowed" — review identifies the specific error handling issue |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | Review mentions "Email sending failures are not handled properly" but does not specifically name SendWelcomeEmail or its broad exception handling |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Partial | Review mentions "Raw SQL queries are constructed using string concatenation" but does not specifically name the missing database transaction |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Partial | Review mentions "Email sending failures are not handled properly" but does not specifically name the Transfer method or its email failure behavior |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Partial | Review mentions "Failed login attempt is not logged as an error" but does not specifically name the exception message exposure issue |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Partial | Review mentions "SqlConnection is opened but never closed" but does not specifically name ExecuteNonQuery or its connection handling |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | Review mentions "Failed login attempt is not logged as an error" but does not specifically name the rate limiting issue |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "SqlConnection is opened but never closed" — review identifies the specific resource leak issue |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Partial | Review mentions "Raw SQL queries are constructed using string concatenation" but does not specifically name GetOpenConnection or its resource leak |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Partial | Review mentions "SqlConnection is opened but never closed" but does not specifically name ExecuteNonQuery or its disposal issue |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "SmtpClient is created as an instance field but never disposed of" — review identifies the specific resource leak issue |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "MailMessage objects are created but not disposed of in case of email sending failures" — review identifies the specific resource leak issue |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Partial | Review mentions "Configuration values are not checked for null" but does not specifically name Jwt:SecretKey or its null handling |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Partial | Review mentions "DataTable returned by `ExecuteQuerySafe` method is not checked for null or empty" but does not specifically name the row access issue |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | Review mentions "Configuration values are not checked for null" but does not specifically name Email:SmtpPort or its parsing issue |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | Review mentions "Configuration values are not checked for null" but does not specifically name username or its null handling |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | Review mentions "Configuration values are not checked for null" but does not specifically name email/username length access |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Partial | Review mentions "UserId claim is not checked for null or empty" but does not specifically name the FindFirst issue |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | "UpdateUserRequest object is not checked for null before accessing its properties" — review identifies the specific null check issue |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | "Magic number `MaxTransactionsPerDay` is hardcoded" — review identifies the specific magic number issue |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | "Magic numbers `1000000` and `50` are hardcoded" — review identifies the specific magic number issue |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | Review mentions "Magic strings `TransferSubject` and `WelcomeSubject` are hardcoded" but does not specifically name email addresses |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Partial | Review mentions "Magic numbers `MaxRetries` and `SmtpTimeoutMs` are hardcoded" but does not specifically name the email length constants |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "Magic numbers `1000000` and `50` are hardcoded" — review identifies the specific magic number issue |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Partial | Review mentions "HashPasswordSha1 method uses an insecure hashing algorithm" but does not specifically name HashPasswordSha1 or its dead code status |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "ValidateToken method is not used" — review identifies the specific unreachable code issue |
| D3 | `TableExists` — never called from any service or controller. | Partial | Review mentions "Obsolete method `ExecuteQueryWithParams` is still present" but does not specifically name TableExists |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | "Obsolete method `ExecuteQueryWithParams` is still used" — review identifies the specific dead code issue |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Partial | Review mentions "Obsolete method `ExecuteQueryWithParams` is still present" but does not specifically name BuildHtmlTemplate |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | "Obsolete method `ExecuteQueryWithParams` is still present" — review identifies the specific dead code issue |
| D7 | `FormatCurrency` — private, never called. | Partial | Review mentions "RefundTransaction method is not implemented" but does not specifically name FormatCurrency |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Partial | Review mentions "Interest bonus calculation in the `Deposit` method is hardcoded to always be 0.05% of the deposit amount" but does not specifically name IsWithinDailyLimit |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Partial | Review mentions "JoinWithSeparatorFixed method is a duplicate of `string.Join` method" but does not specifically name ObfuscateAccount |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Partial | Review mentions "JoinWithSeparatorFixed method is a duplicate of `string.Join` method" but does not specifically name ToTitleCase |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "JoinWithSeparatorFixed method is a duplicate of `string.Join` method" — review identifies the specific dead code issue |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | Review mentions "Shared mutable static state `_auditLog` and `_requestCount` is used" but does not specifically name the static state issue |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Partial | Review mentions "IsValidEmail method uses a regular expression that may not be fully compliant" but does not specifically name the regex compilation issue |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "JoinWithSeparator method concatenates strings in a loop, which is inefficient" — review identifies the specific anti-pattern |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "SmtpClient is created as an instance field but never disposed of" — review identifies the specific anti-pattern |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Missed | _(ungrounded: no matching sentence in review)_ |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Partial | Review mentions "Raw SQL queries are constructed using string concatenation" but does not specifically name GetOpenConnection |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Partial | Review mentions "Database connection string is hardcoded", "Email SMTP credentials are hardcoded", and "JWT secret key is hardcoded" but does not specifically name the combination of all three credential types |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | Review mentions "JWT validation parameters are hardcoded" but does not specifically name log level configuration |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Partial | Review mentions "JWT validation parameters are hardcoded" but does not specifically name ValidateLifetime parameter |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "HTTPS redirection is commented out" — review identifies the specific configuration issue |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "UseDeveloperExceptionPage is called unconditionally" — review identifies the specific configuration issue |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Partial | Review mentions "JWT validation parameters are hardcoded" but does not specifically name CORS policy |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Partial | Review mentions "JWT validation parameters are hardcoded" but does not specifically name debug symbols configuration |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | Review mentions "JWT validation parameters are hardcoded" but does not specifically name the package vulnerability |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | Review mentions "JWT validation parameters are hardcoded" but does not specifically name missing production settings |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `TransactionService.Transfer`, etc. | Found | "The source code does not include a test project" — review identifies the specific missing unit tests issue |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Partial | `RecordTransaction` | **no** | **UNSUPPORTED** |
| R3 | Partial | `GenerateJwtToken` | **no** | **UNSUPPORTED** |
| E7 | Partial | `rate limit` | **no** | **UNSUPPORTED** |
| N3 | Partial | `SmtpPort` | **no** | **UNSUPPORTED** |
| D1 | Partial | `HashPasswordSha1` | yes | under-credited? |
| D3 | Partial | `TableExists` | yes | under-credited? |
| D4 | Found | `ExecuteQueryWithParams` | yes | - |
| D5 | Partial | `BuildHtmlTemplate` | **no** | **UNSUPPORTED** |
| D6 | Found | `SendWelcomeEmailHtml` | **no** | **MIS-CREDIT** |
| D7 | Partial | `FormatCurrency` | **no** | **UNSUPPORTED** |
| D8 | Partial | `IsWithinDailyLimit` | yes | under-credited? |
| D9 | Partial | `ObfuscateAccount` | **no** | **UNSUPPORTED** |
| D10 | Partial | `ToTitleCase` | **no** | **UNSUPPORTED** |
| D11 | Found | `JoinWithSeparatorFixed` | yes | - |
| CF9 | Partial | `appsettings.Production` | **no** | **UNSUPPORTED** |
| UT | Found | `Tests.csproj` | yes | - |
| C2 | Partial | `SuperAdmin2024` | yes | under-credited? |
| C3 | Partial | `MD5` | yes | under-credited? |
| C9 | Partial | `ValidateLifetime` | **no** | **UNSUPPORTED** |
| L3 | Found | `GetUsersPage` | yes | - |
| L4 | Partial | `0.05` | yes | under-credited? |
| E1 | Found | `SearchUsers` | yes | - |
| E5 | Partial | `ex.Message` | yes | under-credited? |
| RL4 | Found | `SmtpClient` | yes | - |
| RL5 | Found | `MailMessage` | yes | - |
| N2 | Partial | `Rows[0]` | **no** | **UNSUPPORTED** |
| N4 | Partial | `ToUpper` | **no** | **UNSUPPORTED** |
| M1 | Found | `TransactionFeeRate` | yes | - |
| M2 | Found | `1000000` | yes | - |
| D2 | Found | `ValidateToken` | yes | - |
| A1 | Partial | `_auditLog` | yes | under-credited? |
| A2 | Partial | `Regex` | yes | under-credited? |
| A5 | Missed | `IsBlank` | **no** | - |
| CF3 | Partial | `ValidateLifetime` | **no** | **UNSUPPORTED** |
| CF4 | Found | `UseHttpsRedirection` | yes | - |
| CF5 | Found | `UseDeveloperExceptionPage` | yes | - |
| CF6 | Partial | `AllowAnyOrigin` | **no** | **UNSUPPORTED** |
| CF7 | Partial | `DebugType` | **no** | **UNSUPPORTED** |
| CF8 | Partial | `Newtonsoft` | **no** | **UNSUPPORTED** |

**Adjusted Found: 22 of 70** (23 reported, less 1 mis-credited).

> **16 row(s) rated `Partial` whose target string appears NOWHERE in the review** (C7, R3, E7, N3, D5, D7, D9, D10, CF9, C9, N2, N4, CF3, CF6, CF7, CF8). A Partial on an unmentioned issue is a Missed; the reported Missed count is correspondingly understated.

> **9 row(s) rated `Partial`/`Missed` whose target string IS present in the review** (D1, D3, D8, C2, C3, L4, E5, A1, A2). The score is left as the scorer rated it; read these rows before trusting the Missed count.

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Codestral-22B-imatrix:Q4_K_S` |
| Reasoning strength (system prompt) | (model default) |
| System prompt | `You are an expert computer programmer with an eye for detail, who loves to provide high quality answers.` |
| Ollama `think` | (unset) |
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
| Review citations past end of file | `0 of 79` |
| Precision (checkable Found rows) | `93% (13 of 14)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 67ece22` |
