# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `15dbff8`

> ⚠ **2 row(s) rated Found name a target that never appears in the review** (L3, CF7). Adjusted Found: **13** of 70. See the spot-check below.

Total: 15 Found / 1 Partial / 54 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "SQL injection via string interpolation `{username}` in query" |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "Hardcoded credentials in code" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "MD5 hashing used without salt" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Missed | _(ungrounded: no matching sentence in review)_ |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Missed | _(ungrounded: no matching sentence in review)_ |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Missed | _(ungrounded: no matching sentence in review)_ |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Missed | _(ungrounded: no matching sentence in review)_ |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "Production secrets committed to source" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "JWT ValidateLifetime = false" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | "Missing ownership checks on PUT/DELETE endpoints" |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Missed | _(ungrounded: no matching sentence in review)_ |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | "Incorrect boundary conditions" |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "Balance calculation excludes fee" |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "Off-by-one error in pagination" |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | "Fee calculation incorrect" |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Missed | _(ungrounded: no matching sentence in review)_ |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Missed | No mention of duplicated validation or method extraction |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Missed | _(ungrounded: no matching sentence in review)_ |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | No mention of JWT token generation or refactoring |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Missed | _(ungrounded: no matching sentence in review)_ |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Missed | _(ungrounded: no matching sentence in review)_ |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Missed | _(ungrounded: no matching sentence in review)_ |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Missed | _(ungrounded: no matching sentence in review)_ |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Missed | _(ungrounded: no matching sentence in review)_ |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Missed | _(ungrounded: no matching sentence in review)_ |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed | _(ungrounded: no matching sentence in review)_ |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Missed | _(ungrounded: no matching sentence in review)_ |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Missed | _(ungrounded: no matching sentence in review)_ |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Missed | _(ungrounded: no matching sentence in review)_ |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Missed | _(ungrounded: no matching sentence in review)_ |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Missed | _(ungrounded: no matching sentence in review)_ |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Missed | _(ungrounded: no matching sentence in review)_ |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Missed | _(ungrounded: no matching sentence in review)_ |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Missed | _(ungrounded: no matching sentence in review)_ |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | _(ungrounded: no matching sentence in review)_ |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Missed | _(ungrounded: no matching sentence in review)_ |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Missed | _(ungrounded: no matching sentence in review)_ |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Missed | _(ungrounded: no matching sentence in review)_ |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Missed | _(ungrounded: no matching sentence in review)_ |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Missed | _(ungrounded: no matching sentence in review)_ |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Missed | _(ungrounded: no matching sentence in review)_ |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Missed | _(ungrounded: no matching sentence in review)_ |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Missed | _(ungrounded: no matching sentence in review)_ |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Missed | _(ungrounded: no matching sentence in review)_ |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Missed | _(ungrounded: no matching sentence in review)_ |
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
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Missed | _(ungrounded: no matching sentence in review)_ |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Missed | _(ungrounded: no matching sentence in review)_ |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Missed | _(ungrounded: no matching sentence in review)_ |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Missed | _(ungrounded: no matching sentence in review)_ |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Missed | _(ungrounded: no matching sentence in review)_ |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Missed | _(ungrounded: no matching sentence in review)_ |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "Production secrets committed to source" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | Mentions configuration but doesn't name specific log levels |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "JWT ValidateLifetime = false" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "HTTPS disabled" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "Overly permissive CORS" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | "Debug symbols in release builds" |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Missed | _(ungrounded: no matching sentence in review)_ |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, controller action results. | Missed | _(ungrounded: no matching sentence in review)_ |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Missed | `SearchUsers` | **no** | - |
| C7 | Missed | `RecordTransaction` | **no** | - |
| R3 | Missed | `GenerateJwtToken` | **no** | - |
| E7 | Missed | `rate limit` | **no** | - |
| N3 | Missed | `SmtpPort` | **no** | - |
| D1 | Missed | `HashPasswordSha1` | **no** | - |
| D3 | Missed | `TableExists` | **no** | - |
| D4 | Missed | `ExecuteQueryWithParams` | **no** | - |
| D5 | Missed | `BuildHtmlTemplate` | **no** | - |
| D6 | Missed | `SendWelcomeEmailHtml` | **no** | - |
| D7 | Missed | `FormatCurrency` | **no** | - |
| D8 | Missed | `IsWithinDailyLimit` | **no** | - |
| D9 | Missed | `ObfuscateAccount` | **no** | - |
| D10 | Missed | `ToTitleCase` | **no** | - |
| D11 | Missed | `JoinWithSeparatorFixed` | **no** | - |
| CF9 | Missed | `appsettings.Production` | yes | under-credited? |
| UT | Missed | `Tests.csproj` | **no** | - |
| C2 | Found | `SuperAdmin2024` | yes | - |
| C3 | Found | `MD5` | yes | - |
| C9 | Found | `ValidateLifetime` | yes | - |
| L3 | Found | `GetUsersPage` | **no** | **MIS-CREDIT** |
| L4 | Found | `0.05` | yes | - |
| E1 | Missed | `SearchUsers` | **no** | - |
| E5 | Missed | `ex.Message` | **no** | - |
| RL4 | Missed | `SmtpClient` | **no** | - |
| RL5 | Missed | `MailMessage` | **no** | - |
| N2 | Missed | `Rows[0]` | **no** | - |
| N4 | Missed | `ToUpper` | **no** | - |
| M1 | Missed | `TransactionFeeRate` | **no** | - |
| M2 | Missed | `1000000` | **no** | - |
| D2 | Missed | `ValidateToken` | **no** | - |
| A1 | Missed | `_auditLog` | **no** | - |
| A2 | Missed | `Regex` | **no** | - |
| A5 | Missed | `IsBlank` | **no** | - |
| CF3 | Found | `ValidateLifetime` | yes | - |
| CF4 | Found | `UseHttpsRedirection` | yes | - |
| CF5 | Missed | `UseDeveloperExceptionPage` | **no** | - |
| CF6 | Found | `AllowAnyOrigin` | yes | - |
| CF7 | Found | `DebugType` | **no** | **MIS-CREDIT** |
| CF8 | Missed | `Newtonsoft` | **no** | - |

**Adjusted Found: 13 of 70** (15 reported, less 2 mis-credited).

> **1 row(s) rated `Partial`/`Missed` whose target string IS present in the review** (CF9). The score is left as the scorer rated it; read these rows before trusting the Missed count.

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3.5-0.8B-imatrix:Q4_K_S` |
| Reasoning strength (system prompt) | (model default) |
| System prompt | `You are an expert computer programmer with an eye for detail, who loves to provide high quality answers.` |
| Ollama `think` | `medium` |
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
| Grounding downgrades | `52` |
| Self-declared-absent downgrades | `0` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 15dbff8` |
