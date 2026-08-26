# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `19b916c`

Total: 22 Found / 36 Partial / 12 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "SampleBankingApp/Services/AuthService.cs | 32 | SQL injection via string interpolation in query | Use parameterized query or executeQuerySafe method" |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password in constructor | Remove hardcoded value; rely on database authentication only" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "SampleBankingApp/Services/AuthService.cs | 61 | MD5 hashing of passwords (weak cryptography) | Switch to SHA256 or stronger algorithm" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "SampleBankingApp/Services/UserService.cs | 72 | SQL injection via string interpolation in UPDATE statement | Use parameterized query or executeQuerySafe" |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Partial | "SampleBankingApp/Services/UserService.cs | 105 | Exception caught and swallowed silently | Log exception details; do not return empty list" - mentions SQL injection but not the specific method |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Partial | "SampleBankingApp/Services/TransactionService.cs | 42-45 | Balance calculation logic excludes fee deduction | Ensure `totalDebit` is subtracted from both balances correctly" - mentions SQL injection but not the specific method |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Partial | "SampleBankingApp/Services/TransactionService.cs | 99-103 | RefundTransaction throws NotImplementedException | Implement actual refund logic" - mentions SQL injection but not the specific method |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "SampleBankingApp/Program.cs | 16 | Hardcoded JWT secret key in source code | Move to `.env` file or configuration management system" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables token expiration enforcement | Set to `true` to enforce token validity period" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | "SampleBankingApp/Controllers/UserController.cs | 56 | Delete endpoint lacks ownership check | Add `[Authorize(Roles = "SuperAdmin")]` or similar permission check" |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | "SampleBankingApp/Controllers/UserController.cs | 56 | Delete endpoint lacks ownership check | Add `[Authorize(Roles = "SuperAdmin")]` or similar permission check" |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Partial | "SampleBankingApp/Services/TransactionService.cs | 42-45 | Balance calculation logic excludes fee deduction | Ensure `totalDebit` is subtracted from both balances correctly" - mentions logic error but not the specific check |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Partial | "SampleBankingApp/Services/TransactionService.cs | 42-45 | Balance calculation logic excludes fee deduction | Ensure `totalDebit` is subtracted from both balances correctly" - mentions logic error but not the specific check |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Partial | "SampleBankingApp/Services/UserService.cs | 72 | SQL injection via string interpolation in UPDATE statement | Use parameterized query or executeQuerySafe" - mentions pagination but not the specific error |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | "SampleBankingApp/Services/TransactionService.cs | 68 | Interest bonus calculated as 5% but not applied to total balance update | Verify interest is added to the correct balance field" - mentions interest rate but not the specific error |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Partial | "SampleBankingApp/Controllers/TransactionController.cs | 27 | Integer parsing without null check on userIdClaim | Add null check: `int fromUserId = int.Parse(userIdClaim!);`" - mentions self-transfer but not the specific error |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | "SampleBankingApp/Services/UserService.cs | 27 | ExecuteQuerySafe called without null check on sql | Add null check: `if (string.IsNullOrEmpty(sql)) throw new ArgumentException();`" - mentions duplicated validation but not the specific method |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Missed | _(ungrounded: no matching sentence in review)_ |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | "SampleBankingApp/Services/AuthService.cs | 68 | JWT token expiration set to 30 days but no validation logic enforced | Ensure `ValidateToken` is called before using token and handles expired tokens" - mentions JWT but not the specific method |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "SampleBankingApp/Services/UserService.cs | 105 | Exception caught and swallowed silently | Log exception details; do not return empty list" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | "SampleBankingApp/Services/EmailService.cs | 73 | `SendWelcomeEmail` catches exceptions but doesn't close connection | Ensure connection is closed on exception" - mentions error handling but not the specific method |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Partial | "SampleBankingApp/Services/TransactionService.cs | 42-45 | Balance calculation logic excludes fee deduction | Ensure `totalDebit` is subtracted from both balances correctly" - mentions database transaction but not the specific error |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Partial | "SampleBankingApp/Controllers/TransactionController.cs | 56 | Catch-all exception handler returns generic error | Implement proper error response" - mentions email failure but not the specific error |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | "SampleBankingApp/Controllers/UserController.cs | 66 | Error message contains sensitive data | Sanitize error messages to remove stack traces or internal IDs" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Partial | "SampleBankingApp/Data/DatabaseHelper.cs | 44 | Connection not explicitly closed after Send | Use using statement for SmtpClient" - mentions connection but not the specific method |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | "SampleBankingApp/Controllers/AuthController.cs | 25 | Hardcoded username in logger message | Replace with parameterized string or use `request.Username` directly" - mentions rate limiting but not the specific error |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Partial | "SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection opened without null check on config | Add null check: `var connectionString = _config.GetConnectionString("DefaultConnection");`" - mentions resource leak but not the specific method |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Missed | _(ungrounded: no matching sentence in review)_ |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Partial | "SampleBankingApp/Data/DatabaseHelper.cs | 44 | Connection not explicitly closed after Send | Use using statement for SmtpClient" - mentions resource leak but not the specific method |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "SampleBankingApp/Services/EmailService.cs | 16 | `_smtpClient` instance field never disposed | Dispose after successful send or wrap in try-finally" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "SampleBankingApp/Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` creates MailMessage but doesn't dispose | Ensure MailMessage is disposed" |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Partial | "SampleBankingApp/Services/AuthService.cs | 60 | No null check on username parameter | Add null check: `if (string.IsNullOrEmpty(username)) return null;`" - mentions null check but not the specific method |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "SampleBankingApp/Services/TransactionService.cs | 36 | Accessing row index without checking count first | Add `if (table.Rows.Count == 0)` before accessing `Rows[0]`" |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | "SampleBankingApp/Services/EmailService.cs | 73 | `SendWelcomeEmail` catches exceptions but doesn't close connection | Ensure connection is closed on exception" - mentions null check but not the specific method |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | "SampleBankingApp/Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` creates MailMessage but doesn't dispose | Ensure MailMessage is disposed" - mentions null check but not the specific method |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Missed | _(ungrounded: no matching sentence in review)_ |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "SampleBankingApp/Controllers/TransactionController.cs | 27 | Integer parsing without null check on userIdClaim | Add null check: `int fromUserId = int.Parse(userIdClaim!);`" |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | "SampleBankingApp/Controllers/AuthController.cs | 22 | LoginRequest passed directly without null check | Add null check: `if (request == null) return BadRequest();`" |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Partial | "SampleBankingApp/Services/TransactionService.cs | 68 | Interest bonus calculated as 5% but not applied to total balance update | Verify interest is added to the correct balance field" - mentions magic numbers but not the specific method |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Partial | "SampleBankingApp/Services/UserService.cs | 27 | ExecuteQuerySafe called without null check on sql | Add null check: `if (string.IsNullOrEmpty(sql)) throw new ArgumentException();`" - mentions magic numbers but not the specific method |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | "SampleBankingApp/Services/EmailService.cs | 73 | `SendWelcomeEmail` catches exceptions but doesn't close connection | Ensure connection is closed on exception" - mentions magic strings but not the specific method |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Missed | _(ungrounded: no matching sentence in review)_ |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Partial | "SampleBankingApp/Services/UserService.cs | 72 | SQL injection via string interpolation in UPDATE statement | Use parameterized query or executeQuerySafe" - mentions magic numbers but not the specific method |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Partial | "SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection opened without null check on config | Add null check: `var connectionString = _config.GetConnectionString("DefaultConnection");`" - mentions dead code but not the specific method |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Partial | "SampleBankingApp/Services/AuthService.cs | 53-56 | Hardcoded admin bypass logic bypasses authorization checks | Remove inline check; ensure `Login` returns null for invalid credentials" - mentions dead code but not the specific method |
| D3 | `TableExists` — never called from any service or controller. | Missed | _(ungrounded: no matching sentence in review)_ |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Partial | "SampleBankingApp/Data/DatabaseHelper.cs | 44 | Connection not explicitly closed after Send | Use using statement for SmtpClient" - mentions dead code but not the specific method |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Partial | "SampleBankingApp/Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` creates MailMessage but doesn't dispose | Ensure MailMessage is disposed" - mentions dead code but not the specific method |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Partial | "SampleBankingApp/Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` creates MailMessage but doesn't dispose | Ensure MailMessage is disposed" - mentions dead code but not the specific method |
| D7 | `FormatCurrency` — private, never called. | Partial | "SampleBankingApp/Services/TransactionService.cs | 99-103 | RefundTransaction throws NotImplementedException | Implement actual refund logic" - mentions dead code but not the specific method |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Partial | "SampleBankingApp/Services/TransactionService.cs | 99-103 | RefundTransaction throws NotImplementedException | Implement actual refund logic" - mentions dead code but not the specific method |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Missed | _(ungrounded: no matching sentence in review)_ |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Missed | _(ungrounded: no matching sentence in review)_ |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Missed | _(ungrounded: no matching sentence in review)_ |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | "SampleBankingApp/Services/UserService.cs | 105 | Exception caught and swallowed silently | Log exception details; do not return empty list" - mentions anti-pattern but not the specific method |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Missed | _(ungrounded: no matching sentence in review)_ |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Missed | _(ungrounded: no matching sentence in review)_ |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "SampleBankingApp/Services/EmailService.cs | 16 | `_smtpClient` instance field never disposed | Dispose after successful send or wrap in try-finally" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Missed | _(ungrounded: no matching sentence in review)_ |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Missed | _(ungrounded: no matching sentence in review)_ |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "SampleBankingApp/Program.cs | 16 | Hardcoded JWT secret key in source code | Move to `.env` file or configuration management system" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | "SampleBankingApp/Program.cs | 34 | Developer exception page enabled in production | Disable `UseDeveloperExceptionPage()` in production environment" - mentions configuration but not the specific method |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables token expiration enforcement | Set to `true` to enforce token validity period" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out | Enable `app.UseHttpsRedirection();` |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "SampleBankingApp/Program.cs | 34 | Developer exception page enabled in production | Disable `UseDeveloperExceptionPage()` in production environment" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "SampleBankingApp/Program.cs | 38 | CORS allows any origin (`AllowAnyOrigin`) | Restrict to specific trusted origins" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Partial | "SampleBankingApp/Program.cs | 34 | Developer exception page enabled in production | Disable `UseDeveloperExceptionPage()` in production environment" - mentions configuration but not the specific method |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | "SampleBankingApp/Program.cs | 34 | Developer exception page enabled in production | Disable `UseDeveloperExceptionPage()` in production environment" - mentions configuration but not the specific method |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | "SampleBankingApp/Program.cs | 34 | Developer exception page enabled in production | Disable `UseDeveloperExceptionPage()` in production environment" - mentions configuration but not the specific method |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login` — SQL injection boundary cases, correct vs. incorrect password; `AuthService.GenerateJwtToken` — claims mapping, expiry; `TransactionService.Transfer` — zero amount, self-transfer, fee deduction, insufficient funds (with fee); `TransactionService.Deposit` — interest rate correctness; `UserService.GetUsersPage` — pagination offset correctness (the off-by-one); `StringHelper` — null inputs, boundary lengths, separator trailing character; Controller action results — correct HTTP status codes for various service responses | Found | "SampleBankingApp/Controllers/AuthController.cs | No tests for login flow | Create unit tests for `Login`, `GenerateJwtToken`, `ValidateToken`" - mentions missing unit tests but not the specific areas listed in the reference document |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Partial | `SearchUsers` | yes | under-credited? |
| C7 | Partial | `RecordTransaction` | yes | under-credited? |
| R3 | Partial | `GenerateJwtToken` | yes | under-credited? |
| E7 | Partial | `rate limit` | **no** | **UNSUPPORTED** |
| N3 | Partial | `SmtpPort` | **no** | **UNSUPPORTED** |
| D1 | Partial | `HashPasswordSha1` | yes | under-credited? |
| D3 | Missed | `TableExists` | **no** | - |
| D4 | Partial | `ExecuteQueryWithParams` | **no** | **UNSUPPORTED** |
| D5 | Partial | `BuildHtmlTemplate` | yes | under-credited? |
| D6 | Partial | `SendWelcomeEmailHtml` | yes | under-credited? |
| D7 | Partial | `FormatCurrency` | **no** | **UNSUPPORTED** |
| D8 | Partial | `IsWithinDailyLimit` | **no** | **UNSUPPORTED** |
| D9 | Missed | `ObfuscateAccount` | **no** | - |
| D10 | Missed | `ToTitleCase` | **no** | - |
| D11 | Missed | `JoinWithSeparatorFixed` | **no** | - |
| CF9 | Partial | `appsettings.Production` | **no** | **UNSUPPORTED** |
| UT | Found | `Tests.csproj` | yes | - |
| C2 | Found | `SuperAdmin2024` | yes | - |
| C3 | Found | `MD5` | yes | - |
| C9 | Found | `ValidateLifetime` | yes | - |
| L3 | Partial | `GetUsersPage` | **no** | **UNSUPPORTED** |
| L4 | Partial | `0.05` | yes | under-credited? |
| E1 | Found | `SearchUsers` | yes | - |
| E5 | Found | `ex.Message` | yes | - |
| RL4 | Found | `SmtpClient` | yes | - |
| RL5 | Found | `MailMessage` | yes | - |
| N2 | Found | `Rows[0]` | yes | - |
| N4 | Partial | `ToUpper` | **no** | **UNSUPPORTED** |
| M1 | Partial | `TransactionFeeRate` | **no** | **UNSUPPORTED** |
| M2 | Partial | `1000000` | yes | under-credited? |
| D2 | Partial | `ValidateToken` | yes | under-credited? |
| A1 | Partial | `_auditLog` | **no** | **UNSUPPORTED** |
| A2 | Missed | `Regex` | **no** | - |
| A5 | Missed | `IsBlank` | **no** | - |
| CF3 | Found | `ValidateLifetime` | yes | - |
| CF4 | Found | `UseHttpsRedirection` | yes | - |
| CF5 | Found | `UseDeveloperExceptionPage` | yes | - |
| CF6 | Found | `AllowAnyOrigin` | yes | - |
| CF7 | Partial | `DebugType` | **no** | **UNSUPPORTED** |
| CF8 | Partial | `Newtonsoft` | **no** | **UNSUPPORTED** |

No mis-credits detected in the watchlist.

> **12 row(s) rated `Partial` whose target string appears NOWHERE in the review** (E7, N3, D4, D7, D8, CF9, L3, N4, M1, A1, CF7, CF8). A Partial on an unmentioned issue is a Missed; the reported Missed count is correspondingly understated.

> **9 row(s) rated `Partial`/`Missed` whose target string IS present in the review** (C5, C7, R3, D1, D5, D6, L4, M2, D2). The score is left as the scorer rated it; read these rows before trusting the Missed count.

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3.5-2B-imatrix:Q4_K_S` |
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
| Grounding downgrades | `12` |
| Self-declared-absent downgrades | `0` |
| Rows misaligned with ISSUES.md | `0` |
| Review citations past end of file | `0 of 143` |
| Precision (checkable Found rows) | `100% (13 of 13)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 19b916c` |
