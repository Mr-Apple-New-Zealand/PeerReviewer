# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `00111c5`

> ⚠ **1 row(s) rated Found name a target that never appears in the review** (CF9). Adjusted Found: **46** of 70. See the spot-check below.

Total: 47 Found / 0 Partial / 23 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | The review identifies SQL injection in the Login method via string interpolation with username input. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | The review identifies the hardcoded backdoor password SuperAdmin2024 in AuthService.cs. |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | The review identifies MD5 hashing as cryptographically broken in AuthService.cs. |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | The review identifies SQL injection risks in UserService.cs UpdateUser and DeleteUser methods via string interpolation. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | The review identifies SQL injection in SearchUsers method via string interpolation with query parameter. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | The review identifies SQL injection risks in TransactionService.cs Transfer method via string concatenation. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | The review identifies SQL injection in RecordTransaction method via string interpolation with description parameter. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | The review identifies hardcoded credentials in appsettings.json including DB password, JWT secret, and email password. |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | The review identifies ValidateLifetime = false in Program.cs as a security vulnerability. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Missed | _(ungrounded: no matching sentence in review)_ |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | The review identifies missing authorization checks in UserController.cs DeleteUser method. |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | The review identifies logic error in Transfer method where amount check doesn't account for zero values. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Missed | _(ungrounded: no matching sentence in review)_ |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | The review identifies the off-by-one error in UserService.cs pagination logic. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Missed | _(ungrounded: no matching sentence in review)_ |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | The review identifies missing self-transfer validation in TransactionController.cs Transfer endpoint. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Missed | _(ungrounded: no matching sentence in review)_ |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | The review identifies inefficient string concatenation in JoinWithSeparator method that should use string.Join. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | _(ungrounded: no matching sentence in review)_ |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | The review identifies SearchUsers method catching broad Exception and returning empty list without proper error indication. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Missed | _(ungrounded: no matching sentence in review)_ |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | The review identifies missing database transaction in Transfer method for balance updates. |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | The review identifies email failure handling issue where transaction commits before email is sent. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | The review identifies UpdateUser method exposing raw exception messages to clients. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Missed | _(ungrounded: no matching sentence in review)_ |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed | _(ungrounded: no matching sentence in review)_ |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Missed | _(ungrounded: no matching sentence in review)_ |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Missed | _(ungrounded: no matching sentence in review)_ |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Missed | _(ungrounded: no matching sentence in review)_ |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | The review identifies SmtpClient field usage causing resource leaks in EmailService.cs. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Missed | _(ungrounded: no matching sentence in review)_ |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | The review identifies potential null reference in GenerateJwtToken method when accessing JWT secret. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | The review identifies missing null/empty row checks in TransactionService.cs Transfer method. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Missed | _(ungrounded: no matching sentence in review)_ |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | _(ungrounded: no matching sentence in review)_ |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Missed | _(ungrounded: no matching sentence in review)_ |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | The review identifies potential null parsing issues in TransactionController.cs Transfer method. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | The review identifies missing null checks in UserController.cs UpdateUser method. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | The review identifies hardcoded TransactionFeeRate and MaxTransactionsPerDay values in TransactionService.cs. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Missed | _(ungrounded: no matching sentence in review)_ |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | The review identifies hardcoded email addresses in EmailService.cs methods. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | The review identifies hardcoded values 254, 3, and 20 in StringHelper.cs. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | The review identifies hardcoded page size limit 50 in UserService.cs. |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | The review identifies HashPasswordSha1 method as dead code in AuthService.cs. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | The review identifies unreachable code block in ValidateToken method in AuthService.cs. |
| D3 | `TableExists` — never called from any service or controller. | Missed | _(ungrounded: no matching sentence in review)_ |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | The review identifies ExecuteQueryWithParams method as obsolete and dead code. |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | The review identifies BuildHtmlTemplate method as dead code in EmailService.cs. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | The review identifies SendWelcomeEmailHtml method as dead code in EmailService.cs. |
| D7 | `FormatCurrency` — private, never called. | Found | The review identifies FormatCurrency method as dead code in TransactionService.cs. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Missed | _(ungrounded: no matching sentence in review)_ |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Missed | _(ungrounded: no matching sentence in review)_ |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Missed | _(ungrounded: no matching sentence in review)_ |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | The review identifies JoinWithSeparatorFixed method as unused in StringHelper.cs. |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | The review identifies static fields in UserService.cs as mutable static state anti-pattern. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Missed | _(ungrounded: no matching sentence in review)_ |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | The review identifies string concatenation in loop in JoinWithSeparator method. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | The review identifies shared SmtpClient field usage in EmailService.cs. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Missed | _(ungrounded: no matching sentence in review)_ |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | The review identifies GetOpenConnection method as anti-pattern for connection management. |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | The review identifies production secrets in appsettings.json including DB password, JWT secret, and email password. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | The review identifies Debug log level configuration in Program.cs for production. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | The review identifies ValidateLifetime = false setting in Program.cs JWT configuration. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | The review identifies UseHttpsRedirection() commented out in Program.cs. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | The review identifies UseDeveloperExceptionPage() called unconditionally in Program.cs. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | The review identifies overly permissive CORS policy in Program.cs. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | The review identifies DebugSymbols=true and DebugType=full in SampleBankingApp.csproj. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | The review identifies outdated Newtonsoft.Json version 12.0.3 in SampleBankingApp.csproj. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | The review identifies missing appsettings.Production.json file for environment-specific configuration. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login` — SQL injection boundary cases, correct vs. incorrect password; `AuthService.GenerateJwtToken` — claims mapping, expiry; `TransactionService.Transfer` — zero amount, self-transfer, fee deduction, insufficient funds (with fee); `TransactionService.Deposit` — interest rate correctness; `UserService.GetUsersPage` — pagination offset correctness (the off-by-one); `StringHelper` — null inputs, boundary lengths, separator trailing character; Controller action results — correct HTTP status codes for various service responses | Missed | _(ungrounded: no matching sentence in review)_ |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Missed | `GenerateJwtToken` | yes | under-credited? |
| E7 | Missed | `rate limit` | **no** | - |
| N3 | Missed | `SmtpPort` | **no** | - |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Missed | `TableExists` | **no** | - |
| D4 | Found | `ExecuteQueryWithParams` | yes | - |
| D5 | Found | `BuildHtmlTemplate` | yes | - |
| D6 | Found | `SendWelcomeEmailHtml` | yes | - |
| D7 | Found | `FormatCurrency` | yes | - |
| D8 | Missed | `IsWithinDailyLimit` | **no** | - |
| D9 | Missed | `ObfuscateAccount` | **no** | - |
| D10 | Missed | `ToTitleCase` | **no** | - |
| D11 | Found | `JoinWithSeparatorFixed` | yes | - |
| CF9 | Found | `appsettings.Production` | **no** | **MIS-CREDIT** |

**Adjusted Found: 46 of 70** (47 reported, less 1 mis-credited).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3.5-122B-imatrix:Q4_K_S` |
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
| Grounding downgrades | `23` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 00111c5` |
