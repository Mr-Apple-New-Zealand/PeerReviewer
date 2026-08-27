# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22`

Total: 32 Found / 28 Partial / 10 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review identifies SQL injection vulnerability in `Login` method due to string interpolation. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review identifies hardcoded admin bypass password. |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review identifies weak cryptography using MD5 for password hashing. |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Partial | Review mentions SQL injection in UserService but doesn't name specific methods UpdateUser/DeleteUser. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Partial | Review identifies SQL injection in SearchUsers method but doesn't name the specific method. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Partial | Review mentions SQL injection in TransactionService but doesn't name specific methods Transfer/Deposit. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Partial | Review identifies SQL injection in RecordTransaction but doesn't name the specific method. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review identifies hardcoded credentials in fallback connection string. |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review identifies `ValidateLifetime` set to false in JWT configuration. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Missed | _(ungrounded: no matching sentence in review)_ |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Missed | _(ungrounded: no matching sentence in review)_ |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Missed | _(ungrounded: no matching sentence in review)_ |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review identifies incorrect boundary condition: checks `fromBalance >= amount` but should check `fromBalance >= totalDebit`. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review identifies off-by-one error in pagination: `skip = page * pageSize` should be `(page - 1) * pageSize`. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | Review identifies incorrect interest rate calculation but doesn't name specific method or variable. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Partial | Review mentions self-transfer but doesn't name the specific method or condition. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Missed | _(ungrounded: no matching sentence in review)_ |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review identifies string concatenation inside loop in `JoinWithSeparator` and suggests using `StringBuilder` or `string.Join`. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | _(ungrounded: no matching sentence in review)_ |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Partial | Review identifies SQL injection in SearchUsers but doesn't name the specific method or error handling issue. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Review identifies broad exception catching in `SendWelcomeEmail`. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Review identifies database updates not wrapped in a transaction. |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Missed | _(ungrounded: no matching sentence in review)_ |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Missed | _(ungrounded: no matching sentence in review)_ |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Partial | Review mentions connection handling but doesn't name specific method or issue. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | Review mentions login security but doesn't name specific missing check. |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review identifies `SqlConnection` and `SqlCommand` not properly disposed in `Login` method. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | Review identifies `SqlConnection` opened but not disposed in `GetOpenConnection`. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Partial | Review mentions connection handling but doesn't name specific method or issue. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review identifies `SmtpClient` held as an instance field, which is not thread-safe and may leak sockets. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Partial | Review mentions email handling but doesn't name specific methods or issue. |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Review identifies `_config["Jwt:SecretKey"]` could be null, leading to null reference in `GetBytes`. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Review identifies `table.Rows[0]` accessed without checking `Rows.Count > 0`. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | Review mentions configuration issues but doesn't name specific method or variable. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | Review mentions null reference risks but doesn't name specific method or variable. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | Review mentions null reference risks but doesn't name specific method or variable. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Review identifies `userIdClaim` could be null, leading to null reference in `int.Parse`. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | Review mentions null reference risks but doesn't name specific method or variable. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review identifies magic number `0.015m` for transaction fee rate. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Partial | Review mentions magic numbers but doesn't name specific method or variable. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | Review mentions hardcoded values but doesn't name specific email addresses. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Partial | Review mentions magic numbers but doesn't name specific method or variable. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Review identifies magic number `50` for maximum page size. |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review identifies `HashPasswordSha1` method defined but never called. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Missed | _(ungrounded: no matching sentence in review)_ |
| D3 | `TableExists` — never called from any service or controller. | Partial | Review mentions dead code but doesn't name specific method or scenario. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review identifies `ExecuteQueryWithParams` method marked as obsolete and unused. |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Partial | Review mentions dead code but doesn't name specific method or scenario. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Partial | Review mentions dead code but doesn't name specific method or scenario. |
| D7 | `FormatCurrency` — private, never called. | Found | Review identifies `FormatCurrency` method defined but never called. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Partial | Review mentions dead code but doesn't name specific method or scenario. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Partial | Review mentions dead code but doesn't name specific method or scenario. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Partial | Review mentions dead code but doesn't name specific method or scenario. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review identifies `JoinWithSeparator` method defined but `JoinWithSeparatorFixed` is used instead. |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | Review mentions shared mutable static state but doesn't name specific variables or issue. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Review identifies `new Regex(...)` created inside method called repeatedly and suggests making it static readonly. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review identifies string concatenation inside loop in `JoinWithSeparator` and suggests using `StringBuilder` or `string.Join`. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Review identifies `SmtpClient` held as an instance field, which is not thread-safe and may leak sockets. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | Review identifies reimplementation of `string.IsNullOrWhiteSpace` in `IsBlank`. |
| A6 | `GetOpenConnection()` — leaking connection — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Partial | Review mentions connection handling but doesn't name specific method or issue. |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies hardcoded credentials in fallback connection string. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies `ValidateLifetime` set to false in JWT configuration. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review identifies HTTPS redirection commented out. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review identifies `UseDeveloperExceptionPage` called unconditionally. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review identifies overly permissive CORS policy allowing any origin, method, and header. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | Review mentions configuration issues but doesn't name specific package or vulnerability. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | Review mentions configuration issues but doesn't name specific missing file or setting. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results | Found | Review identifies absence of test project and lists critical methods needing unit tests. |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Partial | `SearchUsers` | yes | under-credited? |
| C7 | Partial | `RecordTransaction` | **no** | **UNSUPPORTED** |
| R3 | Missed | `GenerateJwtToken` | yes | under-credited? |
| E7 | Partial | `rate limit` | **no** | **UNSUPPORTED** |
| N3 | Partial | `SmtpPort` | **no** | **UNSUPPORTED** |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Partial | `TableExists` | yes | under-credited? |
| D4 | Found | `ExecuteQueryWithParams` | yes | - |
| D5 | Partial | `BuildHtmlTemplate` | **no** | **UNSUPPORTED** |
| D6 | Partial | `SendWelcomeEmailHtml` | **no** | **UNSUPPORTED** |
| D7 | Found | `FormatCurrency` | yes | - |
| D8 | Partial | `IsWithinDailyLimit` | **no** | **UNSUPPORTED** |
| D9 | Partial | `ObfuscateAccount` | **no** | **UNSUPPORTED** |
| D10 | Partial | `ToTitleCase` | **no** | **UNSUPPORTED** |
| D11 | Found | `JoinWithSeparatorFixed` | yes | - |
| CF9 | Partial | `appsettings.Production` | **no** | **UNSUPPORTED** |
| UT | Found | `Tests.csproj` | yes | - |
| C2 | Found | `SuperAdmin2024` | yes | - |
| C3 | Found | `MD5` | yes | - |
| C9 | Found | `ValidateLifetime` | yes | - |
| L3 | Found | `GetUsersPage` | yes | - |
| L4 | Partial | `0.05` | yes | under-credited? |
| E1 | Partial | `SearchUsers` | yes | under-credited? |
| E5 | Missed | `ex.Message` | yes | under-credited? |
| RL4 | Found | `SmtpClient` | yes | - |
| RL5 | Partial | `MailMessage` | **no** | **UNSUPPORTED** |
| N2 | Found | `Rows[0]` | yes | - |
| N4 | Partial | `ToUpper` | **no** | **UNSUPPORTED** |
| M1 | Found | `TransactionFeeRate` | yes | - |
| M2 | Partial | `1000000` | **no** | **UNSUPPORTED** |
| D2 | Missed | `ValidateToken` | **no** | - |
| A1 | Partial | `_auditLog` | yes | under-credited? |
| A2 | Found | `Regex` | yes | - |
| A5 | Found | `IsBlank` | yes | - |
| CF3 | Found | `ValidateLifetime` | yes | - |
| CF4 | Found | `UseHttpsRedirection` | yes | - |
| CF5 | Found | `UseDeveloperExceptionPage` | yes | - |
| CF6 | Found | `AllowAnyOrigin` | yes | - |
| CF7 | Missed | `DebugType` | **no** | - |
| CF8 | Partial | `Newtonsoft` | **no** | **UNSUPPORTED** |

No mis-credits detected in the watchlist.

> **13 row(s) rated `Partial` whose target string appears NOWHERE in the review** (C7, E7, N3, D5, D6, D8, D9, D10, CF9, RL5, N4, M2, CF8). A Partial on an unmentioned issue is a Missed; the reported Missed count is correspondingly understated.

> **7 row(s) rated `Partial`/`Missed` whose target string IS present in the review** (C5, R3, D3, L4, E1, E5, A1). The score is left as the scorer rated it; read these rows before trusting the Missed count.

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Devstral-2-123B-Instruct-2512:Q4_K_M` |
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
| Grounding downgrades | `10` |
| Self-declared-absent downgrades | `0` |
| Rows misaligned with ISSUES.md | `0` |
| Review citations past end of file | `0 of 63` |
| Precision (checkable Found rows) | `100% (18 of 18)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 67ece22` |
