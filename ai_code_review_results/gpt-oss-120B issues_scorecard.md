# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `1224407`

> ⚠ **4 row(s) rated Found name a target that never appears in the review** (D3, L4, E5, M2). Adjusted Found: **58** of 70. See the spot-check below.

Total: 62 Found / 0 Partial / 8 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | AuthService.cs line 32: "SQL query built with string interpolation allows SQL injection on `username` and `hashedPassword`." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | AuthService.cs line 17: "Hard‑coded admin bypass password (`SuperAdmin2024`) is a backdoor." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | AuthService.cs line 30: "Passwords are hashed with MD5, which is cryptographically weak." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | UserService.cs lines 47-48: "UPDATE statement built with string interpolation allows SQL injection on `email` and `username`." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | UserService.cs lines 99-100: "`ExecuteQuery` builds raw `WHERE` clause with user‑supplied `query`, enabling SQL injection." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | TransactionService.cs lines 47-48: "UPDATE statements built with string interpolation allow SQL injection on `newFromBalance`, `newToBalance`, `fromUserId`, `toUserId`." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | TransactionService.cs lines 70-71: "INSERT statement built with string interpolation allows SQL injection on `description` and other fields." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | appsettings.json line 3: "Connection string contains hard‑coded SA password (`Admin1234!`).", appsettings.json line 6: "JWT secret key is stored in plain text.", appsettings.json lines 13-14: "SMTP username/password are stored in plain text." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Program.cs line 24: "`ValidateLifetime = false` disables token expiration validation.", Program.cs line 34: "UseDeveloperExceptionPage() is enabled for all environments, leaking stack traces." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Missed | _(ungrounded: no matching sentence in review)_ |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Missed | _(ungrounded: no matching sentence in review)_ |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | TransactionService.cs line 23-24: "No verification that `amount` is greater than zero (only `< 0` is checked). Zero‑amount transfers are allowed." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | TransactionService.cs line 42: "Funds check uses `fromBalance >= amount` but ignores the transaction fee, allowing negative balances." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | UserService.cs line 72: "Pagination offset is calculated as `page * pageSize` instead of `(page‑1) * pageSize`, skipping the first page." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | TransactionService.cs line 60: "Deposit adds `interestBonus` but does not enforce daily limit or fee logic; may allow unlimited deposits." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | TransactionService.cs line 23-24: "No check prevents a user from transferring to themselves (`fromUserId == toUserId`).", TransactionService.cs line 23-24: "No check that `amount` is not excessively large (e.g., > balance). Zero amount allowed." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | UserService.cs line 38-50: "UpdateUser repeats the same ID validation logic as DeleteUser." |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | StringHelper.cs line 31-34: "Concatenating strings in a loop creates many temporary strings (O(n²) cost)." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | AuthService.cs line 68-86: "JWT token is issued for 30 days while `ValidateLifetime` is set to `false`; tokens never expire." |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | UserService.cs line 97-108: "`SearchUsers` catches generic `Exception` and returns an empty list, hiding the failure reason." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | EmailService.cs line 71-78: "`SendWelcomeEmail` catches generic `Exception` and only writes to console, swallowing the error." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | TransactionService.cs line 23-24: "No transaction is wrapped in a database transaction; partial updates could leave data inconsistent." |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | TransactionService.cs line 63-64: "`Deposit` does not catch DB errors; could expose stack trace." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Program.cs line 34: "`UseDeveloperExceptionPage()` is enabled for all environments, leaking stack traces." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | DatabaseHelper.cs line 50-55: "`ExecuteNonQuery` opens a connection and creates a command without disposing." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed | _(ungrounded: no matching sentence in review)_ |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | AuthService.cs lines 34-41: "`SqlConnection`, `SqlCommand` and `SqlDataReader` are never disposed, exposing credentials and increasing attack surface." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | DatabaseHelper.cs line 26-33: "`GetOpenConnection` returns an open `SqlConnection` that callers often never close." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | DatabaseHelper.cs line 50-55: "`ExecuteNonQuery` opens a connection and creates a command without disposing." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | EmailService.cs lines 16-31: "`SmtpClient` is stored as a field and never disposed." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | EmailService.cs lines 39-44, 69-70, 88-91: "`MailMessage` objects are created but never disposed." |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Missed | _(ungrounded: no matching sentence in review)_ |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Missed | _(ungrounded: no matching sentence in review)_ |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Missed | _(ungrounded: no matching sentence in review)_ |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | EmailService.cs line 68: "`username.ToUpper()` throws `NullReferenceException` if `username` is `null`." |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | StringHelper.cs lines 14, 24: "`email.Length` and `username.Length` throw if argument is `null`." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | TransactionController.cs line 19-20: "`User.FindFirst(... )?.Value` may be `null`; `int.Parse` on `null` throws." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | Controllers/UserController.cs line 28: "UpdateUser and controller endpoints don't check `request == null`." |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | TransactionService.cs line 11: "Transaction fee rate `0.015m` is a magic number." |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | TransactionService.cs line 60: "Deposit adds `interestBonus` but does not enforce daily limit or fee logic; may allow unlimited deposits." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | EmailService.cs lines 40, 69, 90: "From address `"notifications@company.com`" is hard‑coded." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | StringHelper.cs lines 16, 25: "Email regex pattern is a magic string." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | UserService.cs line 70: "Page size limit `50` is a magic number." |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | AuthService.cs lines 91-96: "`HashPasswordSha1` uses SHA‑1, a broken hash algorithm, and is never used." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | AuthService.cs lines 98-108: "`ValidateToken` returns `true` before any validation; dead code after `return`." |
| D3 | `TableExists` — never called from any service or controller. | Found | DatabaseHelper.cs line 49: "`TableExists` is never called from any service or controller." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | DatabaseHelper.cs lines 56: "`ExecuteQueryWithParams` is marked `[Obsolete]` and never referenced." |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | EmailService.cs lines 81-84: "`BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml`, which itself is never called." |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | EmailService.cs lines 86-92: "`SendWelcomeEmailHtml` is never invoked." |
| D7 | `FormatCurrency` — private, never called. | Found | TransactionService.cs lines 94-98: "`FormatCurrency` is never used." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | TransactionService.cs lines 77-85: "`IsWithinDailyLimit` is defined but never used." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | StringHelper.cs lines 43-52: "`MaskAccountNumber` is never used." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | StringHelper.cs lines 54-57: "`ToTitleCase` is never used." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | StringHelper.cs lines 38-41: "`JoinWithSeparatorFixed` is never used." |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | UserService.cs lines 10-11: "Static fields `_auditLog` and `_requestCount` are only used for logging/counting but never exposed outside the class except via `GetAuditReport`." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | StringHelper.cs lines 16, 25: "New `Regex` objects are created on each call; they are not cached." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | StringHelper.cs line 31-34: "Concatenating strings in a loop creates many temporary strings (O(n²) cost)." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | EmailService.cs lines 16-31: "`SmtpClient` is stored as a field and reused across threads; it is not thread‑safe." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | StringHelper.cs lines 65-71: "`IsBlank` manually checks null, empty, and whitespace; `string.IsNullOrWhiteSpace` already does this." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | DatabaseHelper.cs line 26-33: "`GetOpenConnection` returns an open `SqlConnection` that callers often never close." |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | appsettings.json line 3: "Connection string contains hard‑coded SA password (`Admin1234!`).", appsettings.json line 6: "JWT secret key is stored in plain text.", appsettings.json lines 13-14: "SMTP username/password are stored in plain text." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Program.cs line 18-20: "Logging levels set to `Debug` for all categories, which is too verbose for production." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Program.cs line 24: "`ValidateLifetime = false` disables token expiration validation." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Program.cs line 36: "HTTPS redirection is commented out, leaving HTTP enabled." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Program.cs line 34: "`UseDeveloperExceptionPage()` is enabled for all environments, leaking stack traces." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Program.cs line 38: "CORS policy uses `AllowAnyOrigin`, `AllowAnyMethod`, `AllowAnyHeader`." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp.csproj lines 8-9: "`DebugSymbols` and `DebugType` are enabled, leaking symbol information in release builds." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Missed | _(ungrounded: no matching sentence in review)_ |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results | Found | (No test project) – "The repository contains no unit‑test project, leaving core business logic unverified." |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Found | `GenerateJwtToken` | yes | - |
| E7 | Missed | `rate limit` | **no** | - |
| N3 | Missed | `SmtpPort` | yes | under-credited? |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Found | `TableExists` | **no** | **MIS-CREDIT** |
| D4 | Found | `ExecuteQueryWithParams` | yes | - |
| D5 | Found | `BuildHtmlTemplate` | yes | - |
| D6 | Found | `SendWelcomeEmailHtml` | yes | - |
| D7 | Found | `FormatCurrency` | yes | - |
| D8 | Found | `IsWithinDailyLimit` | yes | - |
| D9 | Found | `ObfuscateAccount` | yes | - |
| D10 | Found | `ToTitleCase` | yes | - |
| D11 | Found | `JoinWithSeparatorFixed` | yes | - |
| CF9 | Missed | `appsettings.Production` | **no** | - |
| UT | Found | `Tests.csproj` | yes | - |
| C2 | Found | `SuperAdmin2024` | yes | - |
| C3 | Found | `MD5` | yes | - |
| C9 | Found | `ValidateLifetime` | yes | - |
| L3 | Found | `GetUsersPage` | yes | - |
| L4 | Found | `0.05` | **no** | **MIS-CREDIT** |
| E1 | Found | `SearchUsers` | yes | - |
| E5 | Found | `ex.Message` | **no** | **MIS-CREDIT** |
| RL4 | Found | `SmtpClient` | yes | - |
| RL5 | Found | `MailMessage` | yes | - |
| N2 | Missed | `Rows[0]` | **no** | - |
| N4 | Found | `ToUpper` | yes | - |
| M1 | Found | `TransactionFeeRate` | yes | - |
| M2 | Found | `1000000` | **no** | **MIS-CREDIT** |
| D2 | Found | `ValidateToken` | yes | - |
| A1 | Found | `_auditLog` | yes | - |
| A2 | Found | `Regex` | yes | - |
| A5 | Found | `IsBlank` | yes | - |
| CF3 | Found | `ValidateLifetime` | yes | - |
| CF4 | Found | `UseHttpsRedirection` | yes | - |
| CF5 | Found | `UseDeveloperExceptionPage` | yes | - |
| CF6 | Found | `AllowAnyOrigin` | yes | - |
| CF7 | Found | `DebugType` | yes | - |
| CF8 | Missed | `Newtonsoft` | **no** | - |

**Adjusted Found: 58 of 70** (62 reported, less 4 mis-credited).

> **1 row(s) rated `Partial`/`Missed` whose target string IS present in the review** (N3). The score is left as the scorer rated it; read these rows before trusting the Missed count.

### Self-hedged ratings

Rows rated `Found` whose own Note concedes the review did not cover the target. That phrasing describes a Partial; each is likely an over-credit, though a conceded detail can be incidental to the reference issue.

| ID | Hedge | Note |
|---|---|---|
| L4 | `but does not` | TransactionService.cs line 60: "Deposit adds `interestBonus` but does not enforce daily limit or fee logic; may allow unlimited deposits." |
| M2 | `but does not` | TransactionService.cs line 60: "Deposit adds `interestBonus` but does not enforce daily limit or fee logic; may allow unlimited deposits." |

**Plausible floor: 58 of 70** (adjusted 58, less 0 self-hedged).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `gpt-oss:120B` |
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
| Grounding downgrades | `8` |
| Self-declared-absent downgrades | `0` |
| Rows misaligned with ISSUES.md | `0` |
| Review citations past end of file | `1 of 55` |
| Precision (checkable Found rows) | `89% (31 of 35)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 1224407` |
