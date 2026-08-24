# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `9e0947e`

> ⚠ **1 row(s) rated Found name a target that never appears in the review** (E7). Adjusted Found: **33** of 67. See the spot-check below.

Total: 34 Found / 7 Partial / 26 Missed out of 67 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "SampleBankingApp/Services/AuthService.cs | 32 | SQL query constructed using string interpolation for table name. | Use parameterized queries to prevent SQL injection." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin bypass password allows unauthorized access. | Remove hardcoded password and enforce role-based access." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "SampleBankingApp/Services/AuthService.cs | 63 | Password hashing uses MD5 which is cryptographically broken. | Use BCrypt or Argon2 for password hashing." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 29 | SQL query constructed using string interpolation for table name. | Use parameterized queries to prevent SQL injection." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 53 | SQL query constructed using string interpolation for WHERE clause. | Use parameterized queries to prevent SQL injection." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "SampleBankingApp/Services/TransactionService.cs | 90 | RecordTransaction uses string interpolation for SQL. | Use parameterized queries to prevent SQL injection." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "SampleBankingApp/Services/TransactionService.cs | 90 | RecordTransaction uses string interpolation for SQL. | Use parameterized queries to prevent SQL injection." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "SampleBankingApp/appsettings.json | 3 | Hardcoded database password in configuration file. | Move secrets to environment variables or secure vault." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime is set to false. | Set ValidateLifetime to true to enforce token expiration." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | "SampleBankingApp/Controllers/UserController.cs | 52 | Returns raw exception message string to client. | Return standardized error response instead of ex.Message." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | "SampleBankingApp/Controllers/UserController.cs | 48 | Returns raw exception message string to client. | Return standardized error response instead of ex.Message." |

## Logic Errors

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | "SampleBankingApp/Services/TransactionService.cs | 25 | Transfer allows negative amount check. | Add check for amount > 0." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "SampleBankingApp/Services/TransactionService.cs | 42 | Transfer checks balance against amount but deducts fee. | Check balance against totalDebit (amount + fee)." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "SampleBankingApp/Services/UserService.cs | 72 | Pagination skip calculation is off by one. | Change to (page - 1) * pageSize." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | "SampleBankingApp/Services/TransactionService.cs | 68 | Deposit interest calculation multiplies by 1 unnecessarily. | Remove redundant multiplication operator." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | "SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest for failure. | Ensure consistent error response format." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | "SampleBankingApp/Services/UserService.cs | 34 | GetUserById accesses row without checking count. | Check Rows.Count > 0 before accessing row." |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Partial | "SampleBankingApp/Helpers/StringHelper.cs | 31 | JoinWithSeparator uses string concatenation in loop. | Use StringBuilder or string.Join." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | "SampleBankingApp/Services/AuthService.cs | 103 | ValidateToken method returns true unconditionally. | Implement proper token validation logic." |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "SampleBankingApp/Services/UserService.cs | 99 | SearchUsers swallows exceptions and returns empty list. | Return meaningful error or handle exception properly." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | "SampleBankingApp/Services/EmailService.cs | 29 | SMTP client has SSL disabled. | Enable SSL for secure email transmission." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Missed | _(ungrounded: no matching sentence in review)_ |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Missed | _(ungrounded: no matching sentence in review)_ |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | "SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Partial | "SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded database password in fallback connection string. | Remove hardcoded password and enforce configuration." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | "SampleBankingApp/Controllers/AuthController.cs | 22 | Login method passes raw request data to service without validation. | Validate input parameters before passing to service." |

## Resource Leaks

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "SampleBankingApp/Services/AuthService.cs | 32 | SQL query constructed using string interpolation for table name. | Use parameterized queries to prevent SQL injection." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 29 | SQL query constructed using string interpolation for table name. | Use parameterized queries to prevent SQL injection." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 53 | SQL query constructed using string interpolation for WHERE clause. | Use parameterized queries to prevent SQL injection." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "SampleBankingApp/Services/EmailService.cs | 29 | SMTP client has SSL disabled. | Enable SSL for secure email transmission." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Missed | _(ungrounded: no matching sentence in review)_ |

## Missing Null Checks

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Missed | _(ungrounded: no matching sentence in review)_ |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "SampleBankingApp/Services/TransactionService.cs | 35–36 | fromUserTable.Rows[0] and toUserTable.Rows[0] accessed without checking Rows.Count > 0. | Check for row existence before accessing." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Missed | _(ungrounded: no matching sentence in review)_ |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | _(ungrounded: no matching sentence in review)_ |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Missed | _(ungrounded: no matching sentence in review)_ |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Missed | _(ungrounded: no matching sentence in review)_ |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Missed | _(ungrounded: no matching sentence in review)_ |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Missed | _(ungrounded: no matching sentence in review)_ |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Missed | _(ungrounded: no matching sentence in review)_ |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Missed | _(ungrounded: no matching sentence in review)_ |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Missed | _(ungrounded: no matching sentence in review)_ |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Missed | _(ungrounded: no matching sentence in review)_ |

## Dead Code

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Missed | _(ungrounded: no matching sentence in review)_ |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "SampleBankingApp/Services/AuthService.cs | 103 | ValidateToken method returns true unconditionally. | Implement proper token validation logic." |
| D3 | `TableExists` — never called from any service or controller. | Missed | _(ungrounded: no matching sentence in review)_ |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Missed | _(ungrounded: no matching sentence in review)_ |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Missed | _(ungrounded: no matching sentence in review)_ |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Missed | _(ungrounded: no matching sentence in review)_ |
| D7 | `FormatCurrency` — private, never called. | Missed | _(ungrounded: no matching sentence in review)_ |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Missed | _(ungrounded: no matching sentence in review)_ |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Missed | _(ungrounded: no matching sentence in review)_ |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Missed | _(ungrounded: no matching sentence in review)_ |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Missed | _(ungrounded: no matching sentence in review)_ |

## Anti-patterns

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Missed | _(ungrounded: no matching sentence in review)_ |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 16 | Regex created inside method called repeatedly. | Move regex to static readonly field." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 25 | Regex created inside method called repeatedly. | Move regex to static readonly field." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "SampleBankingApp/Services/EmailService.cs | 22 | SMTP client instance field is not thread-safe. | Use singleton pattern or lock for SMTP client access." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 61 | ToTitleCase calls ToTitleCase on lowercased string. | Use System.Globalization.CultureInfo.TextInfo.ToTitleCase directly." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 26 | GetOpenConnection() returns a live connection. | Remove anti-pattern." |

## Configuration Issues

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "SampleBankingApp/appsettings.json | 3 | Hardcoded database password in configuration file. | Move secrets to environment variables or secure vault." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | "SampleBankingApp/Program.cs | 34 | Developer exception page enabled in production. | Remove UseDeveloperExceptionPage or set to false." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime is set to false. | Set ValidateLifetime to true to enforce token expiration." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out. | Uncomment UseHttpsRedirection for production." |
| CF5 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "SampleBankingApp/Program.cs | 38 | CORS policy allows any origin and method. | Restrict allowed origins and methods to specific values." |
| CF6 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | "SampleBankingApp/appsettings.json | 6 | Hardcoded JWT secret key in configuration file. | Use environment variables or secure vault for secrets." |

## Missing Unit Tests

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, Controller action results — correct HTTP status codes for various service responses | Missed | _(ungrounded: no matching sentence in review)_ |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Partial | `GenerateJwtToken` | **no** | - |
| E7 | Found | `rate limit` | **no** | **MIS-CREDIT** |
| N3 | Missed | `SmtpPort` | **no** | - |
| D1 | Missed | `HashPasswordSha1` | **no** | - |
| D3 | Missed | `TableExists` | **no** | - |
| D4 | Missed | `ExecuteQueryWithParams` | **no** | - |
| D5 | Missed | `BuildHtmlTemplate` | **no** | - |
| D6 | Missed | `SendWelcomeEmailHtml` | **no** | - |
| D7 | Missed | `FormatCurrency` | **no** | - |
| D8 | Missed | `IsWithinDailyLimit` | **no** | - |
| D9 | Missed | `ObfuscateAccount` | **no** | - |
| D10 | Missed | `ToTitleCase` | yes | under-credited? |
| D11 | Missed | `JoinWithSeparatorFixed` | **no** | - |

**Adjusted Found: 33 of 67** (34 reported, less 1 mis-credited).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3.5-4B-imatrix:Q5_K_S` |
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
| Grounding downgrades | `26` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 9e0947e` |
