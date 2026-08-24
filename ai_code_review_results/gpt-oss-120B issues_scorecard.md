# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `53beb17`

Total: 60 Found / 1 Partial / 9 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review identifies "SQL built by string interpolation with raw `username` and `hashedPassword` – SQL injection risk" in AuthService.cs line 32 |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review identifies "Hard‑coded admin bypass password" in AuthService.cs line 17 |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review identifies "Password hashed with MD5 – weak, fast hash" in AuthService.cs line 30 |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Review identifies "UpdateUser builds raw UPDATE with interpolated `email` and `username` – injection" in UserService.cs line 47 |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | Review identifies "SearchUsers builds raw LIKE clause with interpolated `query` – injection" in UserService.cs line 99 |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Review identifies "Balance updates built via interpolation – injection" in TransactionService.cs line 47 |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Review identifies "RecordTransaction builds INSERT via interpolation (including `description`) – injection" in TransactionService.cs line 90 |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review identifies "Connection string contains hard‑coded DB password", "JWT secret key stored in plain text", and "Email SMTP username/password stored in plain text" in appsettings.json |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review identifies "ValidateLifetime = false – JWT expiration not checked" in Program.cs line 24 |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Missed | _(ungrounded: no matching sentence in review)_ |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Missed | _(ungrounded: no matching sentence in review)_ |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Review identifies "amount of zero is allowed (passes `amount < 0` check) – likely unintended" in TransactionService.cs line 23 |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review identifies "Insufficient‑funds check ignores transaction fee (`totalDebit` should be used)" in TransactionService.cs line 42 |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review identifies "Pagination offset calculated as `page * pageSize` (off‑by‑one)" in UserService.cs line 72 |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Review identifies "Interest bonus rate `0.05m` (magic) – move to config" in TransactionService.cs line 68 |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Review identifies "Self‑transfer (`fromUserId == toUserId`) allowed" in TransactionService.cs line 23 |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | Review identifies "Validation duplicated across methods" in UserService.cs line 20 |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review identifies "String concatenation in loop" and recommends using `string.Join` or `StringBuilder` |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | _(ungrounded: no matching sentence in review)_ |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Review identifies "SearchUsers catches generic Exception and returns empty list – hides errors" in UserService.cs line 99 |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Review identifies "Catches only SmtpException; other exceptions...are not caught" in EmailService.cs line 45 |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Review identifies "No DB transaction – balances could become inconsistent if one UPDATE succeeds and the other fails" in TransactionService.cs line 23 |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | Review identifies "No handling of email send failure after DB commit – could leave inconsistent state" in TransactionService.cs line 23 |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Missed | _(ungrounded: no matching sentence in review)_ |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | Review identifies "ExecuteNonQuery does not dispose connection/command" in DatabaseHelper.cs line 52 |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed | _(ungrounded: no matching sentence in review)_ |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review identifies "SqlConnection, SqlCommand, SqlDataReader opened but never disposed" in AuthService.cs line 34 |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | Review identifies "GetOpenConnection returns an open SqlConnection that callers may forget to dispose" in DatabaseHelper.cs line 21 |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review identifies "ExecuteNonQuery opens connection via GetOpenConnection and never disposes command/connection (connection closed but not disposed)" in DatabaseHelper.cs line 52 |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review identifies "SMTP client stored as field – not thread-safe" in EmailService.cs line 16 |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review identifies "MailMessage objects not disposed" in EmailService.cs line 39 |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Review identifies "jwtSecret may be null; Encoding.UTF8.GetBytes(jwtSecret!) will NRE" in Program.cs line 16 |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Review identifies "fromUserTable.Rows[0] assumes at least one row; if user not found, IndexOutOfRangeException" in TransactionService.cs line 28 |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | Review identifies "int.Parse(_config["Email:SmtpPort"] ?? "25") may throw if non‑numeric" in EmailService.cs line 24 |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | _(ungrounded: no matching sentence in review)_ |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | Review identifies "email.Length will NRE if email is null" in StringHelper.cs line 13 |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Review identifies "userIdClaim may be null; int.Parse(userIdClaim!) will throw" in TransactionController.cs line 27 |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | Review identifies "request can be null; accessing request.Email may NRE" in UserController.cs line 40 |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review identifies "Transaction fee rate `0.015m` (magic) – move to config" and "Max transactions per day `10` (magic) – move to config" |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | Review identifies "Deposit upper limit `1000000` (magic) – move to config" in TransactionService.cs line 65 |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Review identifies "From address \"notifications@company.com\" hard‑coded" and "Support email \"support@company.com\" hard‑coded" |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | Review identifies "Email length limit `254` (magic) – keep as constant or config", "Username length limits `3` and `20` (magic)" |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Review identifies "Page size capped at `50` (magic number) – make configurable" |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review identifies "AuthService.HashPasswordSha1 – no callers; method never used" |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Review identifies "ValidateToken returns true before any validation – always authorises if called" |
| D3 | `TableExists` — never called from any service or controller. | Found | Review identifies "DatabaseHelper.TableExists – no references in the solution" |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review identifies "DatabaseHelper.ExecuteQueryWithParams – marked [Obsolete] and never called" |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | Review identifies "EmailService.BuildHtmlTemplate – only used by SendWelcomeEmailHtml, which itself is unused" |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Review identifies "EmailService.SendWelcomeEmailHtml – no callers" |
| D7 | `FormatCurrency` — private, never called. | Found | Review identifies "TransactionService.FormatCurrency – defined but never invoked" |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | Review identifies "IsWithinDailyLimit method defined but not called" |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Review identifies "StringHelper.ObfuscateAccount – no callers" |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | Review identifies "StringHelper.ToTitleCase – no callers" |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review identifies "StringHelper.JoinWithSeparatorFixed – no callers" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | Review identifies "Audit log stored in static List<string> without synchronization – race conditions" |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Review identifies "new Regex(...) created on each call – costly" in StringHelper.cs line 16 |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review identifies "JoinWithSeparator builds string via += in a loop → O(n²)" in StringHelper.cs line 31 |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Review identifies "SMTP client stored as field – not thread-safe" in EmailService.cs line 16 |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | Review identifies "IsBlank performs three separate checks – can be simplified to string.IsNullOrWhiteSpace" |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | Review identifies "GetOpenConnection returns an open SqlConnection that callers may forget to dispose" |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies "Connection string contains hard‑coded DB password", "JWT secret key stored in plain text", and "Email SMTP username/password stored in plain text" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies "ValidateLifetime = false – JWT expiration not checked" in Program.cs line 24 |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review identifies "HTTPS redirection commented out (magic omission)" in Program.cs line 36 |
| CF5 | **UseDeveloperExceptionPage called unconditionally** — full stack traces served to production clients. | Found | Review identifies "Developer exception page always on – leaks stack traces" in Program.cs line 34 |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review identifies "CORS policy AllowAnyOrigin/AllowAnyMethod/AllowAnyHeader – open to any site" in Program.cs line 38 |
| CF7 | **DebugSymbols = true** / **DebugType = full** always emitted — PDB files shipped with release builds. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | Review doesn't specifically mention missing production settings file |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results | Found | Review identifies "No unit tests for fee calculation, daily limit, self-transfer" and mentions missing tests in general terms |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Missed | `GenerateJwtToken` | yes | under-credited? |
| E7 | Missed | `rate limit` | yes | under-credited? |
| N3 | Found | `SmtpPort` | yes | - |
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
| Review model | `gpt-oss:120B` |
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
| Grounding downgrades | `9` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 53beb17` |
