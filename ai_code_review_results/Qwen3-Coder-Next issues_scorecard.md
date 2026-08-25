# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `00111c5`

> ⚠ **2 row(s) rated Found name a target that never appears in the review** (C5, D9). Adjusted Found: **42** of 70. See the spot-check below.

Total: 44 Found / 21 Partial / 5 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review identifies SQL injection via string interpolation in login query (`{username}`, `{hashedPassword}`) |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review identifies hardcoded admin bypass password `SuperAdmin2024` in source code |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review identifies weak MD5 hashing used for password hashing |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Review identifies SQL injection via string interpolation in UPDATE statement (`{email}`, `{username}`, `{id}`) |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | Review identifies SQL injection via `ExecuteQuery("Users", $"Username LIKE '%{query}%'")` |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Review identifies SQL injection via string interpolation in UPDATE statement (`{newFromBalance}`, `{fromUserId}`) |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Review identifies SQL injection via string interpolation in INSERT statement (`{fromId}`, `{toId}`, etc.) |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review identifies production connection string contains plaintext password `Admin1234!` |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review identifies JWT `ValidateLifetime = false` allows expired tokens |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Partial | Review mentions admin bypass allows login without password validation but does not specifically name the PUT endpoint or missing access control |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Partial | Review identifies admin bypass allows login without password validation but does not specifically name the DELETE endpoint or missing authorization |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Partial | Review identifies missing self-transfer check but does not specifically name the zero-value transfer issue |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review identifies balance check uses `fromBalance >= amount` but deducts `amount + fee`, allowing negative balance if `fromBalance == amount` |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review identifies pagination off-by-one: `skip = page * pageSize` should be `(page - 1) * pageSize` |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | Review identifies hardcoded interest bonus calculation but does not specifically name the incorrect rate |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Review identifies missing self-transfer check (`fromUserId == toUserId`) |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | Review mentions duplicated validation but does not specifically name the ValidateUserId method |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review identifies `JoinWithSeparator` uses string concatenation in loop (`result += ...`) — O(n²) |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | _(ungrounded: no matching sentence in review)_ |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Review identifies catches broad `Exception` and returns empty list |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Missed | _(ungrounded: no matching sentence in review)_ |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Partial | Review identifies email sent after DB writes but does not specifically name missing database transaction |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Found | Review identifies email sent *after* DB writes — if email fails, transaction is committed but user not notified |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Review identifies returns raw `ex.Message` to client (potential info leak) |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Partial | Review mentions ExecuteNonQuery but does not specifically name this resource leak issue |
| E7 | **No rate limiting or account lockout on failed login attempts** — brute force is trivially possible. | Found | Review identifies no rate limiting on login endpoint — vulnerable to brute-force attacks |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review identifies `SqlConnection`, `SqlCommand`, `SqlDataReader` created but never disposed |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Partial | Review mentions GetOpenConnection but does not specifically name this resource leak |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review identifies `ExecuteNonQuery` opens connection but does not wrap in `using`; relies on `Close()` only — fails if exception before `Close()` |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review identifies `_smtpClient` held as instance field — not thread-safe; sockets may leak if exceptions occur |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review identifies `MailMessage` created but never disposed |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Review identifies `_config["Jwt:SecretKey"]!` used with null-forgiving operator; if missing, `Encoding.UTF8.GetBytes(null)` throws |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Review identifies no null check before accessing `Rows[0]`; throws if user not found |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | Review mentions SMTP config but does not specifically name this null check issue |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | Review mentions username handling but does not specifically name this null check issue |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | Review mentions null checks but does not specifically name this length access issue |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Review identifies `userIdClaim!` used with null-forgiving operator; if claim missing, `int.Parse(null)` throws |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | Review mentions null checks but does not specifically name this request null check |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review identifies `TransactionFeeRate = 0.015m` — fee rate should be configurable |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Partial | Review mentions hardcoded values but does not specifically name this deposit cap |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Review identifies hardcoded `"notifications@company.com"` as sender |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Missed | _(ungrounded: no matching sentence in review)_ |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Review identifies hardcoded `pageSize > 50` clamp |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review identifies unused SHA1 hashing method (dead code) |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Review identifies `ValidateToken` method has unreachable code after `return true;` — logic never executes |
| D3 | `TableExists` — never called from any service or controller. | Partial | Review mentions dead code but does not specifically name TableExists |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review identifies `ExecuteQueryWithParams` marked `[Obsolete]`, and no callers found in codebase |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | Review identifies `BuildHtmlTemplate` defined but only called by `SendWelcomeEmailHtml` |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Review identifies `SendWelcomeEmailHtml` defined but never called anywhere (no callers found) |
| D7 | `FormatCurrency` — private, never called. | Partial | Review mentions dead code but does not specifically name FormatCurrency |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Partial | Review mentions dead code but does not specifically name IsWithinDailyLimit |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Review identifies `JoinWithSeparator` uses string concatenation in loop (`result += ...`) — O(n²) |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Partial | Review mentions dead code but does not specifically name ToTitleCase |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review identifies `JoinWithSeparator` uses string concatenation in loop (`result += ...`) — O(n²) |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | Review identifies static mutable fields `_auditLog`, `_requestCount` — not thread-safe, causes data corruption in multi-user scenarios |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Review identifies `new Regex(...)` created on every call to `IsValidEmail`/`IsValidUsername` |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review identifies `JoinWithSeparator` uses string concatenation in loop (`result += ...`) — O(n²) |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Review identifies `_smtpClient` held as instance field — not thread-safe; sockets may leak if exceptions occur |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Partial | Review mentions anti-patterns but does not specifically name IsBlank |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | Review identifies `GetOpenConnection()` returns open `SqlConnection` without documentation that caller must dispose |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies production connection string contains plaintext password `Admin1234!` |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies JWT `ValidateLifetime = false` allows expired tokens |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Partial | Review mentions HTTPS but does not specifically name this configuration issue |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review identifies `UseDeveloperExceptionPage()` called unconditionally in production |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review identifies overly permissive CORS policy (`AllowAnyOrigin`, `AllowAnyMethod`, `AllowAnyHeader`) |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Partial | Review mentions debug symbols but does not specifically name this configuration issue |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | Review mentions missing configuration files but does not specifically name this issue |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | **Missing Unit Tests** — The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `TransactionService.Transfer`, etc. | Found | Review identifies no test project exists in the provided source files |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | **no** | **MIS-CREDIT** |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Missed | `GenerateJwtToken` | yes | under-credited? |
| E7 | Found | `rate limit` | yes | - |
| N3 | Partial | `SmtpPort` | **no** | - |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Partial | `TableExists` | **no** | - |
| D4 | Found | `ExecuteQueryWithParams` | yes | - |
| D5 | Found | `BuildHtmlTemplate` | yes | - |
| D6 | Found | `SendWelcomeEmailHtml` | yes | - |
| D7 | Partial | `FormatCurrency` | **no** | - |
| D8 | Partial | `IsWithinDailyLimit` | **no** | - |
| D9 | Found | `ObfuscateAccount` | **no** | **MIS-CREDIT** |
| D10 | Partial | `ToTitleCase` | **no** | - |
| D11 | Found | `JoinWithSeparatorFixed` | yes | - |
| CF9 | Partial | `appsettings.Production` | **no** | - |

**Adjusted Found: 42 of 70** (44 reported, less 2 mis-credited).

### Self-hedged ratings

Rows rated `Found` whose own Note concedes the review did not cover the target. That phrasing describes a Partial; each is likely an over-credit, though a conceded detail can be incidental to the reference issue.

| ID | Hedge | Note |
|---|---|---|
| RL3 | `but does not` | Review identifies `ExecuteNonQuery` opens connection but does not wrap in `using`; relies on `Close()` only — fails if exception before `Close()` |

**Plausible floor: 41 of 70** (adjusted 42, less 1 self-hedged).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3-Coder-Next-imatrix:Q5_K_S` |
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
| Grounding downgrades | `5` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 00111c5` |
