# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `00111c5`

> ⚠ **7 row(s) rated Found name a target that never appears in the review** (C7, D3, D4, D5, D7, D9, D10). Adjusted Found: **50** of 70. See the spot-check below.

Total: 57 Found / 0 Partial / 13 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review identifies SQL injection vulnerability in Login method using string interpolation |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review identifies hardcoded admin bypass password |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review identifies MD5 hashing which is insecure for passwords |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Review identifies SQL injection vulnerability in UpdateUser method using string interpolation |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | Review identifies SQL injection vulnerability in SearchUsers method using string interpolation |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Review identifies SQL injection vulnerability in Transfer method using string interpolation |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Review identifies SQL injection vulnerability in Deposit method using string interpolation |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review identifies hardcoded JWT secret key in appsettings.json |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review identifies ValidateLifetime = false in JWT configuration |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | Review identifies missing authorization check on GetUser endpoint |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | Review identifies missing authorization check on DeleteUser endpoint |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Review identifies balance check uses >= instead of > which could allow negative balances |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review identifies fee calculation rounds to 2 decimal places but doesn't ensure precision |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review identifies pagination calculation uses `page * pageSize` instead of `(page-1) * pageSize` |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Review identifies interest bonus calculation is incorrect (0.05m * 1) |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Review identifies potential null dereference on userIdClaim if user is not authenticated |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | Review identifies duplicated validation logic |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review identifies JoinWithSeparator method uses string concatenation in loop which is O(n²) |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | Review identifies complex return path with multiple exit points |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Review identifies SearchUsers catches all exceptions and returns empty list silently |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Review identifies generic Exception catch swallows all exceptions without logging |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Review identifies Transfer method has multiple database operations without transaction |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Missed | _(ungrounded: no matching sentence in review)_ |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Review identifies returns StatusCode(500, ex.Message) which exposes stack trace details |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | Review identifies ExecuteNonQuery method opens connection but doesn't properly dispose it |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed | _(ungrounded: no matching sentence in review)_ |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review identifies opens connection without using `using` statement |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | Review identifies GetOpenConnection method opens connection but caller must remember to dispose it |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review identifies ExecuteNonQuery method opens connection but doesn't properly dispose it |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Missed | _(ungrounded: no matching sentence in review)_ |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Missed | _(ungrounded: no matching sentence in review)_ |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Review identifies _config["Jwt:SecretKey"] could be null |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Review identifies accesses Rows[0] without checking if Rows.Count > 0 |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | Review identifies _config["Email:SmtpPort"] could be null |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | _(ungrounded: no matching sentence in review)_ |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | Review identifies email.Length and username.Length accessed without null check |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Review identifies userIdClaim is used without null check before parsing |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Missed | _(ungrounded: no matching sentence in review)_ |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review identifies magic number 0.015m for transaction fee rate |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | Review identifies magic number 1000000 for deposit limit |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Missed | _(ungrounded: no matching sentence in review)_ |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Missed | _(ungrounded: no matching sentence in review)_ |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Review identifies magic number 50 for max page size |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review identifies HashPasswordSha1 method is unused and marked as private |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Review identifies ValidateToken method has unreachable code after unconditional return |
| D3 | `TableExists` — never called from any service or controller. | Found | Review identifies GetAuditReport method returns string instead of structured data |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review identifies JoinWithSeparator method is duplicated by JoinWithSeparatorFixed |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | Review identifies GetAuditReport method returns string instead of structured data |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Review identifies SendWelcomeEmailHtml method needs HTML email testing |
| D7 | `FormatCurrency` — private, never called. | Found | Review identifies FormatCurrency method is unused and marked as private |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | Review identifies IsWithinDailyLimit method needs testing |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Review identifies ObfuscateAccount method is unused and marked as private |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | Review identifies ToTitleCase method is unused and marked as private |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review identifies JoinWithSeparator method is duplicated by JoinWithSeparatorFixed |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | Review identifies _auditLog and _requestCount are static fields that could cause race conditions |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Review identifies JoinWithSeparator method uses string concatenation inside a loop which is O(n²) |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review identifies JoinWithSeparator method uses string concatenation in loop which is O(n²) |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Missed | _(ungrounded: no matching sentence in review)_ |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Missed | _(ungrounded: no matching sentence in review)_ |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | Review identifies GetOpenConnection method opens connection but caller must remember to dispose it |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies hardcoded JWT secret key in appsettings.json |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Review identifies Log level set to Debug for production namespaces |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies ValidateLifetime = false in JWT configuration |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review identifies HTTPS redirection commented out |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review identifies UseDeveloperExceptionPage called unconditionally in production code |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review identifies Overly permissive CORS policy allowing any origin/method/header |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Review identifies missing environment-specific config overrides like appsettings.Production.json |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results | Missed | Review does not address the aggregate topic of missing unit tests; it only provides individual test suggestions for specific methods but does not acknowledge the lack of any test project or coverage.
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | **no** | **MIS-CREDIT** |
| R3 | Found | `GenerateJwtToken` | yes | - |
| E7 | Missed | `rate limit` | **no** | - |
| N3 | Found | `SmtpPort` | yes | - |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Found | `TableExists` | **no** | **MIS-CREDIT** |
| D4 | Found | `ExecuteQueryWithParams` | **no** | **MIS-CREDIT** |
| D5 | Found | `BuildHtmlTemplate` | **no** | **MIS-CREDIT** |
| D6 | Found | `SendWelcomeEmailHtml` | yes | - |
| D7 | Found | `FormatCurrency` | **no** | **MIS-CREDIT** |
| D8 | Found | `IsWithinDailyLimit` | yes | - |
| D9 | Found | `ObfuscateAccount` | **no** | **MIS-CREDIT** |
| D10 | Found | `ToTitleCase` | **no** | **MIS-CREDIT** |
| D11 | Found | `JoinWithSeparatorFixed` | yes | - |
| CF9 | Found | `appsettings.Production` | yes | - |

**Adjusted Found: 50 of 70** (57 reported, less 7 mis-credited).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3-Coder-30B-imatrix:Q3_K_M` |
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
| Grounding downgrades | `12` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 00111c5` |
