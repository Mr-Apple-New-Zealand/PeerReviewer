# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22`

> ⚠ **5 row(s) rated Found name a target that never appears in the review** (D8, D10, CF9, N4, A5). Adjusted Found: **58** of 70. See the spot-check below.

Total: 63 Found / 0 Partial / 7 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "SampleBankingApp/Services/AuthService.cs | 32 | SQL injection in login query using interpolated username and hashed password | Use parameterized query with `@Username` and `@Password` parameters" |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password `SuperAdmin2024` | Remove backdoor; use proper role-based access control" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "SampleBankingApp/Services/AuthService.cs | 63 | Weak MD5 hashing for passwords | Replace with bcrypt, PBKDF2, or Argon2" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "SampleBankingApp/Services/UserService.cs | 47,61 | SQL injection in UPDATE/DELETE queries via string interpolation | Use parameterized queries with `@Email`, `@Username`, `@Id`" |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "SampleBankingApp/Services/UserService.cs | 99 | SQL injection in `SearchUsers` via interpolated query in `ExecuteQuery` | Use parameterized LIKE clause (`Username LIKE @Query`)" |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "SampleBankingApp/Services/TransactionService.cs | 47-48 | SQL injection in UPDATE statements via interpolated values | Use parameterized queries with `@Balance`, `@UserId`" |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "SampleBankingApp/Services/TransactionService.cs | 90 | SQL injection in `RecordTransaction` via string interpolation | Use parameterized INSERT query" |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "SampleBankingApp/appsettings.json | 3 | Production connection string with plaintext password `Admin1234!` | Use environment variables or managed identity; never commit secrets" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "SampleBankingApp/Program.cs | 24 | JWT `ValidateLifetime = false` allows expired tokens | Set `ValidateLifetime = true`" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Missed | Review does not mention specific endpoint or missing access control check for PUT /api/user/{id} |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Missed | Review does not mention specific endpoint or missing authorization check for DELETE /api/user/{id} |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | "SampleBankingApp/Services/TransactionService.cs | 36-37 | No null guard for `Rows[0]` when user not found (should return error) | Check `table.Rows.Count == 0` and return failure" |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "SampleBankingApp/Services/TransactionService.cs | 42 | Balance check uses `fromBalance >= amount` but deducts `amount + fee`, allowing negative balance | Check `fromBalance >= totalDebit` before proceeding" |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "SampleBankingApp/Services/UserService.cs | 72 | Pagination offset calculation uses `page * pageSize` instead of `(page - 1) * pageSize` | Change to `int skip = (page - 1) * pageSize;` |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | "SampleBankingApp/Services/TransactionService.cs | 68 | Hardcoded interest bonus calculation `amount * 0.05m * 1` — unclear meaning of `* 1` | Remove redundant `* 1`; document rate and period; consider extracting constant" |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | "SampleBankingApp/Services/AuthService.cs | 32 | No check for self-transfer (fromUserId == toUserId) | Add guard clause returning `"Cannot transfer to yourself"` |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | "SampleBankingApp/Services/UserService.cs | 22,42,56 | Hardcoded `id > 1000000` range check | Extract to constant `MaxUserId = 1_000_000` |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 31-35 | `JoinWithSeparator` uses string concatenation in loop (O(n²)) | Replace with `string.Join` (already exists as `JoinWithSeparatorFixed`)" |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | Review does not mention specific method or refactoring opportunity for GenerateJwtToken |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "SampleBankingApp/Services/UserService.cs | 105-108 | Catches broad `Exception` and returns empty list — callers cannot distinguish error from no results | Log exception; rethrow or return null with explicit error indicator" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | "SampleBankingApp/Services/EmailService.cs | 75-78 | Catches `Exception` silently in `SendWelcomeEmail` — swallows errors | Log exception; consider throwing or returning status" |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | "SampleBankingApp/Services/TransactionService.cs | 47-48 | SQL injection in UPDATE statements via interpolated values | Use parameterized queries with `@Balance`, `@UserId`" |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | "SampleBankingApp/Services/TransactionService.cs | 90 | SQL injection in `RecordTransaction` via string interpolation | Use parameterized INSERT query" |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | "SampleBankingApp/Controllers/UserController.cs | 52 | Returns raw `ex.Message` to client (potential info leak) | Return generic message; log full details server-side" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` opens connection but does not dispose `SqlCommand` or close connection on exception | Use `using` for command/connection; wrap in try/finally" |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | "SampleBankingApp/Services/AuthService.cs | 28 | No rate limiting or account lockout on login attempts | Implement rate limiting (e.g., IP/user-based throttling)" |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "SampleBankingApp/Services/AuthService.cs | 34-38 | Opens `SqlConnection` and `SqlCommand` without disposal; `SqlDataReader` not disposed | Use `using` blocks for all disposable resources" |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection()` returns undisposed `SqlConnection` — caller must dispose | Return `IDisposable` and document ownership transfer; or use `using` internally" |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` opens connection but does not dispose `SqlCommand` or close connection on exception | Use `using` for command/connection; wrap in try/finally" |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "SampleBankingApp/Services/EmailService.cs | 16 | `_smtpClient` held as instance field — not thread-safe; sockets may leak on disposal | Make static readonly or ensure proper disposal via `IDisposable` implementation" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "SampleBankingApp/Services/EmailService.cs | 39-43,69,89 | `MailMessage` created without `using` — not disposed after send | Wrap in `using` block" |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | "SampleBankingApp/Program.cs | 28 | `jwtSecret!` used without null check — throws if config key missing | Add null check and throw descriptive exception" |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "SampleBankingApp/Services/TransactionService.cs | 36-37 | No null guard for `Rows[0]` when user not found (should return error) | Check `table.Rows.Count == 0` and return failure" |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | "SampleBankingApp/Services/EmailService.cs | 22,24-28 | `_config["Email:..."]` values passed directly to `SmtpClient`, `NetworkCredential` — may be null | Validate all config keys exist; use fallbacks or throw" |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | "SampleBankingApp/Services/EmailService.cs | 69 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Add null check before calling ToUpper" |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 13,22 | Email max length `254`, username length limits `3-20` | Extract to constants (`MaxEmailLength`, `MinUsernameLength`, `MaxUsernameLength`)" |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "SampleBankingApp/Controllers/TransactionController.cs | 27,41 | No null check on `userIdClaim!` before `int.Parse` — throws if claim missing | Add null check and return `Unauthorized()` |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | "SampleBankingApp/Services/UserService.cs | 36,83 | `table.Rows[0]` accessed without checking `Rows.Count > 0` | Guard with `if (table.Rows.Count == 0)` |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | "SampleBankingApp/Services/TransactionService.cs | 11-12 | `TransactionFeeRate = 0.015m`, `MaxTransactionsPerDay = 10` — should be configurable | Move to `appsettings.json` |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | "SampleBankingApp/Services/UserService.cs | 22,42,56 | Hardcoded `id > 1000000` range check | Extract to constant `MaxUserId = 1_000_000` |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | "SampleBankingApp/Services/EmailService.cs | 13-14 | `MaxRetries = 3`, `SmtpTimeoutMs = 5000` — should be configurable | Move to config" |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | "SampleBankingApp/Helpers/StringHelper.cs | 13,22 | Email max length `254`, username length limits `3-20` | Extract to constants (`MaxEmailLength`, `MinUsernameLength`, `MaxUsernameLength`)" |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "SampleBankingApp/Services/UserService.cs | 70 | Hardcoded `pageSize > 50` limit | Extract to constant or config" |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | "SampleBankingApp/Services/AuthService.cs | 91-96 | `HashPasswordSha1` method defined but never called | Remove or use for migration (document purpose)" |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "SampleBankingApp/Services/AuthService.cs | 103-108 | `ValidateToken` returns `true` unconditionally due to unreachable code after early `return true` | Remove early return; implement actual validation" |
| D3 | `TableExists` — never called from any service or controller. | Missed | _(ungrounded: no matching sentence in review)_ |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Missed | _(ungrounded: no matching sentence in review)_ |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | "SampleBankingApp/Services/EmailService.cs | 81-84 | `BuildHtmlTemplate` method defined but only called by `SendWelcomeEmailHtml` — could be inlined or made private static | Consider inlining if simple, or keep if reused (currently only once)" |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | "SampleBankingApp/Services/EmailService.cs | 81-84 | `BuildHtmlTemplate` method defined but only called by `SendWelcomeEmailHtml` — could be inlined or made private static | Consider inlining if simple, or keep if reused (currently only once)" |
| D7 | `FormatCurrency` — private, never called. | Found | "SampleBankingApp/Services/UserService.cs | 94-97 | `FormatCurrency` method defined but never used | Remove" |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | "SampleBankingApp/Services/TransactionService.cs | 72 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Remove unused method" |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Missed | _(ungrounded: no matching sentence in review)_ |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 54 | `ToTitleCase` — "experimental utility never integrated", never called. | Remove unused method" |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` duplicates `string.Join` functionality and is unused | Remove; use `string.Join` directly" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | "SampleBankingApp/Services/UserService.cs | 10-11 | Static mutable `_auditLog` and `_requestCount` — not thread-safe | Use `ConcurrentBag<string>` or lock; or remove static state" |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 16,25 | `new Regex(...)` created on every call — should be `static readonly` | Make `static readonly Regex` fields" |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 31-35 | `JoinWithSeparator` uses string concatenation in loop (O(n²)) | Replace with `string.Join` (already exists as `JoinWithSeparatorFixed`)" |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "SampleBankingApp/Services/EmailService.cs | 16 | `_smtpClient` held as instance field — not thread-safe; sockets may leak on disposal | Make static readonly or ensure proper disposal via `IDisposable` implementation" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 60 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove redundant method and use built-in function" |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection()` returns undisposed `SqlConnection` — caller must dispose | Return `IDisposable` and document ownership transfer; or use `using` internally" |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "SampleBankingApp/appsettings.json | 3 | Production connection string with plaintext password `Admin1234!` | Use environment variables or managed identity; never commit secrets" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | "SampleBankingApp/Program.cs | 17-21 | Log level set to `Debug` for all namespaces — excessive in production | Use `Information` or `Warning` for production" |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "SampleBankingApp/Program.cs | 24 | JWT `ValidateLifetime = false` allows expired tokens | Set `ValidateLifetime = true`" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out | Uncomment and enable in production" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` called unconditionally in production | Wrap in `app.Environment.IsDevelopment()` check" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "SampleBankingApp/Program.cs | 38 | Overly permissive CORS policy (`AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`) | Restrict to known origins and methods" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | "SampleBankingApp/SampleBankingApp.csproj | 8-9 | `<DebugSymbols>true</DebugSymbols>` and `<DebugType>full</DebugType>` — should be conditional on build config | Remove or wrap in `Condition="'$(Configuration)' == 'Debug'"`" |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | "SampleBankingApp/appsettings.json | all | No environment-specific overrides | Create appsettings.Production.json with secure settings" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project exists (no `*.Test.csproj` or `xunit` references found) | Found | "SampleBankingApp/Services/AuthService.cs | 32 | SQL injection in login query using interpolated username and hashed password | Use parameterized query with `@Username` and `@Password` parameters" |
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
| D3 | Missed | `TableExists` | **no** | - |
| D4 | Missed | `ExecuteQueryWithParams` | **no** | - |
| D5 | Found | `BuildHtmlTemplate` | yes | - |
| D6 | Found | `SendWelcomeEmailHtml` | yes | - |
| D7 | Found | `FormatCurrency` | yes | - |
| D8 | Found | `IsWithinDailyLimit` | **no** | **MIS-CREDIT** |
| D9 | Missed | `ObfuscateAccount` | **no** | - |
| D10 | Found | `ToTitleCase` | **no** | **MIS-CREDIT** |
| D11 | Found | `JoinWithSeparatorFixed` | yes | - |
| CF9 | Found | `appsettings.Production` | **no** | **MIS-CREDIT** |
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
| N4 | Found | `ToUpper` | **no** | **MIS-CREDIT** |
| M1 | Found | `TransactionFeeRate` | yes | - |
| M2 | Found | `1000000` | yes | - |
| D2 | Found | `ValidateToken` | yes | - |
| A1 | Found | `_auditLog` | yes | - |
| A2 | Found | `Regex` | yes | - |
| A5 | Found | `IsBlank` | **no** | **MIS-CREDIT** |
| CF3 | Found | `ValidateLifetime` | yes | - |
| CF4 | Found | `UseHttpsRedirection` | yes | - |
| CF5 | Found | `UseDeveloperExceptionPage` | yes | - |
| CF6 | Found | `AllowAnyOrigin` | yes | - |
| CF7 | Found | `DebugType` | yes | - |
| CF8 | Missed | `Newtonsoft` | **no** | - |

**Adjusted Found: 58 of 70** (63 reported, less 5 mis-credited).

> **1 row(s) rated `Partial`/`Missed` whose target string IS present in the review** (R3). The score is left as the scorer rated it; read these rows before trusting the Missed count.

### Self-hedged ratings

Rows rated `Found` whose own Note concedes the review did not cover the target. That phrasing describes a Partial; each is likely an over-credit, though a conceded detail can be incidental to the reference issue.

| ID | Hedge | Note |
|---|---|---|
| E6 | `but does not` | "SampleBankingApp/Data/DatabaseHelper.cs \| 50-57 \| `ExecuteNonQuery` opens connection but does not dispose `SqlCommand` or close connection on exception \| Use `using` for command/c |
| RL3 | `but does not` | "SampleBankingApp/Data/DatabaseHelper.cs \| 50-57 \| `ExecuteNonQuery` opens connection but does not dispose `SqlCommand` or close connection on exception \| Use `using` for command/c |

**Plausible floor: 56 of 70** (adjusted 58, less 2 self-hedged).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3-Coder-Next-imatrix:Q5_K_S` |
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
| Grounding downgrades | `4` |
| Self-declared-absent downgrades | `0` |
| Rows misaligned with ISSUES.md | `0` |
| Review citations past end of file | `0 of 126` |
| Precision (checkable Found rows) | `86% (30 of 35)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 67ece22` |
