# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22`

> **62 Found, zero Partial.** The spot-check below found no mis-credited watchlist rows, but a zero-Partial sheet is worth a second look.

Total: 62 Found / 0 Partial / 8 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | The review identifies SQL injection in `Login` via string interpolation with `username` and `hashedPassword`. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | The review identifies the hardcoded admin backdoor password `"SuperAdmin2024"` in `AuthService.cs`. |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | The review identifies that `HashPasswordMd5` uses MD5 which is cryptographically broken and unsalted. |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | The review identifies SQL injection in `UpdateUser` via string interpolation with `email`, `username`, and `id`. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | The review identifies SQL injection in `SearchUsers` via string interpolation with `query`. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | The review identifies SQL injection in `Transfer` via string interpolation with `newFromBalance` and `fromUserId`. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | The review identifies SQL injection in `RecordTransaction` via string interpolation with `description`. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Missed | _(ungrounded: no matching sentence in review)_ |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | The review identifies that `ValidateLifetime = false` disables JWT expiry validation. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | The review identifies that `UpdateUser` has no ownership or role check, allowing any authenticated user to modify any user. |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | The review identifies that `DeleteUser` has no ownership or role check, allowing any authenticated user to delete any user. |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | The review identifies that `Transfer` rejects `amount < 0` but allows `amount == 0`, permitting a zero-value transfer. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | The review identifies that `Transfer` checks `fromBalance >= amount` but then deducts `amount + fee`, so a user with exactly `amount` ends up with a negative balance. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | The review identifies that `GetUsersPage` computes `skip = page * pageSize`, so page 1 skips the first `pageSize` rows (off-by-one). |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | The review identifies that `Deposit` computes `amount * 0.05m * 1`, where the trailing `* 1` suggests a missing multiplier. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | The review identifies that `Transfer` has no check for `fromUserId == toUserId`, allowing a user to "transfer" to themselves and lose the fee. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | The review identifies that the validation block is duplicated in `GetUserById`, `UpdateUser`, and `DeleteUser` and suggests extracting it to a helper. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Missed | _(ungrounded: no matching sentence in review)_ |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | _(ungrounded: no matching sentence in review)_ |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | The review identifies that `SearchUsers` catches a broad `Exception` and returns an empty list. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | The review identifies that `SendWelcomeEmail` catches a broad `Exception` and only writes to `Console`. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | The review identifies that two separate `ExecuteNonQuery` calls update balances without a transaction. |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | The review identifies that `SendTransferNotification` is called after the DB writes have committed; if it throws, the transfer is persisted but the caller receives a 500. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | The review identifies that `UpdateUser` returns `ex.Message` directly to the HTTP client. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Missed | _(ungrounded: no matching sentence in review)_ |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | The review identifies that no rate limiting or account lockout is implemented on the login endpoint. |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | The review identifies that `SqlConnection`, `SqlCommand`, and `SqlDataReader` in `Login` are never closed or disposed on any code path. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | The review identifies that `GetOpenConnection` returns an open `SqlConnection` with no documented ownership contract. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Missed | _(ungrounded: no matching sentence in review)_ |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | The review identifies that `SmtpClient` is stored as an instance field and is not thread-safe. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | The review identifies that `MailMessage` in `SendTransferNotification` and `SendWelcomeEmail` are never disposed. |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | The review identifies that `_config["Jwt:SecretKey"]!` can be null at runtime and suggests null-checking before use. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | The review identifies that `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` are accessed without checking `Rows.Count > 0`. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | The review identifies that `int.Parse(_config["Email:SmtpPort"] ?? "25")` throws `FormatException` if the value is non-numeric. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | The review identifies that `username.ToUpper()` in `SendWelcomeEmail` throws `NullReferenceException` if `username` is null. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Missed | _(ungrounded: no matching sentence in review)_ |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | The review identifies that `int.Parse(userIdClaim!)` will throw `NullReferenceException` if the claim is absent. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | The review identifies that `request` in `Login` is a model-bound body; if the client sends no body, `request` is null. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Missed | _(ungrounded: no matching sentence in review)_ |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | The review identifies that `1000000` is an inline literal for the maximum deposit amount. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Missed | _(ungrounded: no matching sentence in review)_ |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | The review identifies that `254`, `3`, and `20` are inline literals for email length, username min/max length. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | The review identifies that `50` is an inline literal for the maximum page size. |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | The review identifies that `HashPasswordSha1` is defined but never called. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | The review identifies that code after the unconditional `return true;` on line 103 is unreachable. |
| D3 | `TableExists` — never called from any service or controller. | Found | The review identifies that `TableExists` is defined but never called anywhere in the codebase. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | The review identifies that `ExecuteQueryWithParams` is marked `[Obsolete]` and has no callers. |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | The review identifies that `BuildHtmlTemplate` is only called by the dead `SendWelcomeEmailHtml`. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | The review identifies that `SendWelcomeEmailHtml` is defined but never called. |
| D7 | `FormatCurrency` — private, never called. | Found | The review identifies that `FormatCurrency` is defined but never called. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | The review identifies that `IsWithinDailyLimit` is defined but never called. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | The review identifies that `ObfuscateAccount` is defined but never called. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | The review identifies that `ToTitleCase` is defined but never called. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | The review identifies that `JoinWithSeparatorFixed` is defined but never called. |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | The review identifies that `_auditLog` and `_requestCount` are static and shared across threads without synchronization. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | The review identifies that `IsValidEmail` and `IsValidUsername` create `new Regex(...)` on every call. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | The review identifies that `JoinWithSeparator` uses O(n²) string concatenation in a loop. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | The review identifies that `SmtpClient` is stored as an instance field and is not thread-safe. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | The review identifies that `IsBlank` reimplements `string.IsNullOrWhiteSpace`. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | The review identifies that `GetOpenConnection` returns an open connection with no documented ownership contract. |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | The review identifies that production secrets are committed to source control. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | The review identifies that log level is set to `Debug` for `Default`, `Microsoft`, and `System` namespaces. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | The review identifies that `ValidateLifetime = false` disables JWT expiry validation. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | The review identifies that `UseHttpsRedirection()` is commented out. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | The review identifies that `UseDeveloperExceptionPage()` is called unconditionally. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | The review identifies that CORS allows `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | The review identifies that `DebugSymbols=true` and `DebugType=full` are set unconditionally in the main `<PropertyGroup>`. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | The review identifies that `Newtonsoft.Json` 12.0.3 has known CVEs and should be upgraded. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | The review identifies that there is no `appsettings.Production.json` to override debug-level logging and development connection string. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project exists in the repository. The following methods and scenarios are the highest priority for unit and integration tests: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper` methods, Controller action results. | Found | The review identifies that no test project exists in the repository and lists key areas that need tests. |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Missed | `GenerateJwtToken` | yes | under-credited? |
| E7 | Found | `rate limit` | yes | - |
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
| CF9 | Found | `appsettings.Production` | yes | - |
| UT | Found | `Tests.csproj` | yes | - |
| C2 | Found | `SuperAdmin2024` | yes | - |
| C3 | Found | `MD5` | yes | - |
| C9 | Found | `ValidateLifetime` | yes | - |
| L3 | Found | `GetUsersPage` | yes | - |
| L4 | Found | `0.05` | yes | - |
| E1 | Found | `SearchUsers` | yes | - |
| E5 | Found | `ex.Message` | yes | - |
| RL4 | Found | `SmtpClient` | yes | - |
| RL5 | Found | `MailMessage` | yes | - |
| N2 | Found | `Rows[0]` | yes | - |
| N4 | Found | `ToUpper` | yes | - |
| M1 | Missed | `TransactionFeeRate` | yes | under-credited? |
| M2 | Found | `1000000` | yes | - |
| D2 | Found | `ValidateToken` | yes | - |
| A1 | Found | `_auditLog` | yes | - |
| A2 | Found | `Regex` | yes | - |
| A5 | Found | `IsBlank` | yes | - |
| CF3 | Found | `ValidateLifetime` | yes | - |
| CF4 | Found | `UseHttpsRedirection` | yes | - |
| CF5 | Found | `UseDeveloperExceptionPage` | yes | - |
| CF6 | Found | `AllowAnyOrigin` | yes | - |
| CF7 | Found | `DebugType` | yes | - |
| CF8 | Found | `Newtonsoft` | yes | - |

No mis-credits detected in the watchlist.

> **2 row(s) rated `Partial`/`Missed` whose target string IS present in the review** (R3, M1). The score is left as the scorer rated it; read these rows before trusting the Missed count.

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3.8-27B-imatrix:Q4_K_S` |
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
| Grounding downgrades | `8` |
| Self-declared-absent downgrades | `0` |
| Rows misaligned with ISSUES.md | `0` |
| Review citations past end of file | `0 of 220` |
| Precision (checkable Found rows) | `100% (38 of 38)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 67ece22` |
