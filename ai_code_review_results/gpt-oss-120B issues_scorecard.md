# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `15dbff8`

> ⚠ **7 row(s) rated Found name a target that never appears in the review** (N3, CF9, L3, E5, N4, M2, A1). Adjusted Found: **58** of 70. See the spot-check below.

Total: 65 Found / 0 Partial / 5 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | AuthService.cs line 32: "SQL query built with string interpolation allowing SQL injection on `username` and `hashedPassword`" |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | AuthService.cs line 17: "Hard‑coded admin bypass password `SuperAdmin2024`" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | AuthService.cs line 61‑66: "Password hashed with MD5 (cryptographically weak)" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | UserService.cs lines 47‑48: "UpdateUser builds raw UPDATE statement with interpolated `email` and `username` – injection risk" |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | UserService.cs lines 99‑100: "SearchUsers builds `WHERE Username LIKE '%{query}%'` via string interpolation – injection risk" |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | TransactionService.cs lines 47‑48: "ExecuteNonQuery updates balances with interpolated decimal values – injection risk" |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | TransactionService.cs lines 89‑91: "RecordTransaction builds INSERT with interpolated values (including `description`) – injection risk" |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | EmailService.cs lines 22‑30: "SMTP credentials (`Email:Username`, `Email:Password`) stored in `appsettings.json` (plain text)" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Program.cs line 24‑29: "JWT validation disables lifetime (`ValidateLifetime = false`)" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Missed | Review does not specifically name this access control issue in the UserController context |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Missed | Review does not specifically name this authorization issue in the UserController context |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | TransactionService.cs lines 25‑26: "Allows `amount < 0` only; zero amount passes as valid (should be `<= 0`)" |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | TransactionService.cs lines 42‑45: "Balance check uses `fromBalance >= amount` but fee is deducted later, allowing overdraft" |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | UserService.cs lines 72: "Pagination `skip = page * pageSize` should be `(page - 1) * pageSize`" |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | TransactionService.cs lines 68‑69: "Interest bonus calculation multiplies by `0.05m * 1` – the `* 1` is unnecessary and may be confusing" |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | TransactionService.cs lines 52‑55: "No check that `fromUserId != toUserId`; self‑transfer possible" |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Missed | Review does not specifically name this duplicated validation issue |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | StringHelper.cs lines 31‑34: "String concatenation in a loop (`result += item + separator`) – O(n²)" |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | Review does not specifically name this refactoring opportunity |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | UserService.cs lines 99‑104: "SearchUsers catches generic `Exception` and returns empty list, swallowing the error and making debugging hard" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | EmailService.cs lines 71‑78: "SendWelcomeEmail catches generic `Exception` and only writes to console, hiding failure from callers" |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | TransactionService.cs lines 23‑58: "No transaction scope – if second update fails, balances become inconsistent" |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | TransactionService.cs lines 23‑58: "Email failure in `Transfer` propagates an exception after the DB transfer has already committed" |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | TransactionController.cs lines 51‑59: "Refund catches only `NotImplementedException`; any other exception bubbles up as 500 without logging" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | DatabaseHelper.cs lines 50‑56: "ExecuteNonQuery disposes connection only via `Close()`, not `Dispose()`, and never disposes `SqlCommand`" |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | Program.cs line 38: "No rate‑limiting or lockout configured for authentication endpoints" |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | AuthService.cs lines 34‑41: "SqlConnection, SqlCommand, and SqlDataReader are opened but never disposed; any exception leaks resources" |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | DatabaseHelper.cs lines 21‑24: "GetOpenConnection returns open connection; callers often forget to dispose (e.g., ExecuteQuery)" |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | DatabaseHelper.cs lines 50‑56: "ExecuteNonQuery disposes connection only via `Close()`, not `Dispose()`, and never disposes `SqlCommand`" |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | EmailService.cs lines 16‑31: "SmtpClient stored as a field and never disposed; SmtpClient implements IDisposable" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | EmailService.cs lines 39‑44: "MailMessage objects created but never disposed" |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | AuthService.cs lines 53‑55: "Admin bypass returns a user with `Id = 0` – may conflict with real IDs" |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | TransactionService.cs lines 36‑37: "Same for `toUserId` – missing row check" |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | EmailService.cs lines 22‑30: "SMTP credentials (`Email:Username`, `Email:Password`) stored in `appsettings.json` (plain text)" |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | StringHelper.cs lines 56‑57: "ObfuscateAccount uses indexer on possibly null `account`" |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | StringHelper.cs lines 13‑14: "IsValidEmail uses `email.Length` without null check" |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | TransactionController.cs lines 26‑27: "User.FindFirst(... )?.Value may be null; `int.Parse` called on null (`userIdClaim!`)" |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | AuthController.cs lines 20‑21: "request could be null if model binding fails; `request.Username` and `request.Password` accessed without null check" |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | TransactionService.cs lines 11‑12: "TransactionFeeRate and MaxTransactionsPerDay defined but never used (daily limit not enforced)" |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | TransactionService.cs lines 68‑69: "Interest bonus calculation multiplies by `0.05m * 1` – the `* 1` is unnecessary and may be confusing" |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | EmailService.cs lines 13‑14: "Email addresses (`notifications@company.com`, `support@company.com`) hard‑coded" |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | StringHelper.cs lines 31‑34: "JoinWithSeparator builds string with trailing separator – magic behaviour" |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | UserService.cs lines 70: "pageSize capped at 50 but not enforced for values ≤ 0" |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | AuthService.cs lines 91‑96: "SHA‑1 hashing method present (weak) and never used" |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | AuthService.cs lines 98‑108: "ValidateToken returns early before actual validation; dead code after return" |
| D3 | `TableExists` — never called from any service or controller. | Found | DatabaseHelper.cs lines 49: "DatabaseHelper.TableExists (DatabaseHelper.cs) – No other source file calls this method" |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | DatabaseHelper.cs lines 56: "DatabaseHelper.ExecuteQueryWithParams (DatabaseHelper.cs) – Marked `[Obsolete]` and never referenced" |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | EmailService.cs lines 79: "EmailService.BuildHtmlTemplate – Only used by SendWelcomeEmailHtml, which itself is dead" |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | EmailService.cs lines 85: "EmailService.SendWelcomeEmailHtml – Not referenced anywhere" |
| D7 | `FormatCurrency` — private, never called. | Found | TransactionService.cs lines 91: "TransactionService.FormatCurrency – Defined but never invoked" |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | TransactionService.cs lines 72: "IsWithinDailyLimit defined but never invoked" |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | StringHelper.cs lines 49: "StringHelper.ObfuscateAccount – No callers" |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | StringHelper.cs lines 54: "StringHelper.ToTitleCase – No callers" |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | StringHelper.cs lines 37: "StringHelper.JoinWithSeparatorFixed – No callers" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | UserService.cs lines 45‑48: "Audit log stored in static List<string> – not thread-safe and will grow unbounded" |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | StringHelper.cs lines 16‑18: "new Regex(...) created on each call; should be static/compiled" |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | StringHelper.cs lines 31‑34: "String concatenation in a loop (`result += item + separator`) – O(n²)" |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | EmailService.cs lines 16‑31: "Holds a single SmtpClient instance (not thread‑safe) as a field" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | StringHelper.cs lines 65‑71: "IsBlank manually checks null, empty, whitespace – can be replaced with string.IsNullOrWhiteSpace" |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | DatabaseHelper.cs lines 21‑24: "Returns open SqlConnection without disposing; callers must remember to close" |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | appsettings.json line 6: "JWT secret key stored in plain text in source repo" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | appsettings.json lines 18‑20: "Logging level set to `Debug` for Microsoft and System namespaces in production" |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Program.cs line 24‑29: "JWT validation disables lifetime (`ValidateLifetime = false`)" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Program.cs line 36: "HTTPS redirection is commented out, leaving HTTP enabled" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Program.cs line 34: "UseDeveloperExceptionPage() runs in all environments, exposing stack traces" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Program.cs line 38: "CORS policy AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader() – overly permissive" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp.csproj lines 8‑9: "DebugSymbols>true</DebugSymbols> and DebugType>full</DebugType> – debug symbols shipped in release" |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | (project root) line 0: "No appsettings.Production.json – no environment-specific overrides" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results | Found | Missing Unit Tests section: "No tests for SQL injection, password hashing, admin bypass, and null inputs" |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Missed | `GenerateJwtToken` | yes | under-credited? |
| E7 | Found | `rate limit` | yes | - |
| N3 | Found | `SmtpPort` | **no** | **MIS-CREDIT** |
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
| CF9 | Found | `appsettings.Production` | **no** | **MIS-CREDIT** |
| UT | Found | `Tests.csproj` | yes | - |
| C2 | Found | `SuperAdmin2024` | yes | - |
| C3 | Found | `MD5` | yes | - |
| C9 | Found | `ValidateLifetime` | yes | - |
| L3 | Found | `GetUsersPage` | **no** | **MIS-CREDIT** |
| L4 | Found | `0.05` | yes | - |
| E1 | Found | `SearchUsers` | yes | - |
| E5 | Found | `ex.Message` | **no** | **MIS-CREDIT** |
| RL4 | Found | `SmtpClient` | yes | - |
| RL5 | Found | `MailMessage` | yes | - |
| N2 | Found | `Rows[0]` | yes | - |
| N4 | Found | `ToUpper` | **no** | **MIS-CREDIT** |
| M1 | Found | `TransactionFeeRate` | yes | - |
| M2 | Found | `1000000` | **no** | **MIS-CREDIT** |
| D2 | Found | `ValidateToken` | yes | - |
| A1 | Found | `_auditLog` | **no** | **MIS-CREDIT** |
| A2 | Found | `Regex` | yes | - |
| A5 | Found | `IsBlank` | yes | - |
| CF3 | Found | `ValidateLifetime` | yes | - |
| CF4 | Found | `UseHttpsRedirection` | yes | - |
| CF5 | Found | `UseDeveloperExceptionPage` | yes | - |
| CF6 | Found | `AllowAnyOrigin` | yes | - |
| CF7 | Found | `DebugType` | yes | - |
| CF8 | Missed | `Newtonsoft` | **no** | - |

**Adjusted Found: 58 of 70** (65 reported, less 7 mis-credited).

> **1 row(s) rated `Partial`/`Missed` whose target string IS present in the review** (R3). The score is left as the scorer rated it; read these rows before trusting the Missed count.

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
| Grounding downgrades | `1` |
| Self-declared-absent downgrades | `0` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 15dbff8` |
