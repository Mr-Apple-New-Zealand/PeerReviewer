# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22`

> **69 Found, zero Partial.** The spot-check below found no mis-credited watchlist rows, but a zero-Partial sheet is worth a second look.

Total: 69 Found / 0 Partial / 1 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review identifies "Login builds the authentication query by interpolating `username` and `hashedPassword` directly into SQL, allowing full authentication bypass via `' OR 1=1--`" |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review identifies "A hardcoded backdoor credential `AdminBypassPassword = "SuperAdmin2024"` grants `SuperAdmin` role with `Id = 0` to anyone who knows it" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review identifies "HashPasswordMd5 uses unsalted MD5, which is broken and trivially reversible via rainbow tables" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Review identifies "UpdateUser interpolates `email` and `username` into an `UPDATE` statement, permitting SQL injection" |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | Review identifies "SearchUsers passes `$"Username LIKE '%{query}%'"` into a raw where-clause helper, an unauthenticated-input SQL injection point" |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Review identifies "Transfer interpolates `newFromBalance` and `fromUserId` into an `UPDATE` statement" |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Review identifies "RecordTransaction interpolates the user-supplied `description` and `type` into an `INSERT`, allowing stored SQL injection" |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review identifies "Production connection string with `sa` account, password `Admin1234!`, and `TrustServerCertificate=True` is committed to the repository" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review identifies "ValidateLifetime = false means expired tokens are accepted forever" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | Review identifies "UpdateUser has no ownership or role check, so any authenticated user can change any other user's email/username" |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | Review identifies "DeleteUser has no ownership or role check, so any authenticated user can delete any account" |

## Logic Errors

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Review identifies "Transfer rejects only `amount < 0`, allowing a zero-value transfer that still writes rows and sends email" |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review identifies "Transfer checks `fromBalance >= amount` but debits `totalDebit = amount + fee`, so a balance between `amount` and `amount+fee` goes negative" |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review identifies "GetUsersPage computes `skip = page * pageSize`, so page 1 skips the first page and the first `pageSize` records are unreachable" |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Review identifies "Deposit credits an "interest bonus" of 5% (`amount * 0.05m * 1`) on every deposit, which is almost certainly meant to be 1% or nothing at all" |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Review identifies "Transfer has no self-transfer check, and because both balances are read before either write, `fromUserId == toUserId` silently corrupts the balance" |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | Review identifies "The `id <= 0` / `id > 1000000` validation block is duplicated verbatim in `GetUserById`, `UpdateUser` and `DeleteUser`" |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review identifies "JoinWithSeparator appends the separator after the final element, producing a trailing separator" |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | Review identifies "GenerateJwtToken claim contents and expiry are untested" |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Review identifies "SearchUsers catches all exceptions and returns an empty `List<User>`, so callers cannot distinguish "no matches" from "database down"" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Review identifies "SendWelcomeEmail swallows every exception and writes to `Console`, so failures are invisible to monitoring" |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Review identifies "Transfer performs two `UPDATE`s plus an `INSERT` with no database transaction, so a crash between them loses or duplicates money" |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | Review identifies "SendTransferNotification is called after the balances are already committed and rethrows after 3 retries, turning a successful transfer into a 500 for the caller" |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Review identifies "UpdateUser returns raw `ex.Message` in a 500 response, leaking SQL/server details to clients" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | Review identifies "ExecuteNonQuery calls `connection.Close()` only on the success path, so a thrown `SqlException` leaks the connection" |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | Review identifies "Login has no rate limiting, CAPTCHA, or account lockout, permitting unlimited credential stuffing against MD5 hashes" |

## Resource Leaks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review identifies "Login opens a `SqlConnection` that is never closed or disposed on any path, leaking a pooled connection per login attempt" |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | Review identifies "ExecuteQuery obtains a connection from `GetOpenConnection` and never closes it" |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review identifies "ExecuteNonQuery calls `connection.Close()` only on the success path, so a thrown `SqlException` leaks the connection" |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review identifies "SmtpClient is held as an instance field on a scoped service, so a new client (and socket) is created per request and never disposed" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review identifies "The `MailMessage` in `SendTransferNotification` is never disposed, leaking attachment/stream handles" |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Review identifies "jwtSecret is read from configuration and null-forgiven into `Encoding.UTF8.GetBytes`, throwing `ArgumentNullException` at startup if the key is missing" |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Review identifies "Transfer accesses `fromUserTable.Rows[0]` without checking `Rows.Count > 0`" |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | Review identifies "The default SMTP port `"25"` is a magic string fallback" |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | Review identifies "SendWelcomeEmail calls `username.ToUpper()` before any null check" |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | Review identifies "IsValidEmail dereferences `email.Length` with no null check on a non-nullable-annotated parameter" |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Review identifies "Transfer passes `User.FindFirst(...)?.Value!` straight into `int.Parse`, throwing if the claim is absent or non-numeric" |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | Review identifies "request is used without a null check, so an empty or `null` JSON body throws an NRE at `request.ToUserId`" |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review identifies "The transaction type string `"Transfer"` is a magic string" |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | Review identifies "The deposit cap `1000000` is an inline literal in `Deposit`" |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Review identifies "The sender address `"notifications@company.com"` is repeated in three methods" |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | Review identifies "The maximum email length `254` is an inline literal" |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Review identifies "The maximum page size `50` is an inline literal in `GetUsersPage`" |

## Dead Code

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review identifies "HashPasswordSha1 has no callers and is a second, unused hashing scheme" |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Review identifies "Lines after `return true;` in `ValidateToken` are unreachable code" |
| D3 | `TableExists` — never called from any service or controller. | Found | Review identifies "TableExists is defined but never called from any file" |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review identifies "ExecuteQueryWithParams is marked `[Obsolete]` and has no callers, yet remains in the codebase" |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | Review identifies "BuildHtmlTemplate is only referenced by the dead `SendWelcomeEmailHtml`, making it transitively dead" |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Review identifies "SendWelcomeEmailHtml has no callers and duplicates `SendWelcomeEmail`" |
| D7 | `FormatCurrency` — private, never called. | Found | Review identifies "FormatCurrency has no callers" |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | Review identifies "IsWithinDailyLimit has no callers, so `MaxTransactionsPerDay` is dead configuration too" |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Review identifies "ObfuscateAccount has no callers and duplicates `MaskAccountNumber`" |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | Review identifies "ToTitleCase has no callers" |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review identifies "JoinWithSeparatorFixed is the "fixed" duplicate of `JoinWithSeparator`, and it too has no callers" |

## Anti-patterns

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | Review identifies "_auditLog is a shared mutable `static List<string>` mutated from concurrent requests without synchronisation" |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Review identifies "IsValidEmail constructs a `new Regex(...)` on every call" |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review identifies "JoinWithSeparator concatenates strings inside a loop, giving O(n²) allocation behaviour" |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Review identifies "SmtpClient is held as an instance field on a scoped service, so a new client (and socket) is created per request and never disposed" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | Review identifies "IsBlank reimplements `string.IsNullOrWhiteSpace`" |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | Review identifies "GetOpenConnection leaks resource ownership to callers with no documented disposal contract" |

## Configuration Issues

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies "Production secrets (DB password, JWT key, SMTP password) live in a committed config file" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Review identifies "Log levels are set to `Debug` for `Default`, `Microsoft` and `System`, which is excessive" |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies "ValidateLifetime = false disables JWT expiry validation" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review identifies "app.UseHttpsRedirection() is commented out, allowing tokens and credentials over plain HTTP" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review identifies "UseDeveloperExceptionPage() is called unconditionally for all environments" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review identifies "CORS is configured with `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | Review identifies "`DebugSymbols=true` and `DebugType=full` apply to Release builds, shipping full PDBs" |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | Review identifies "Newtonsoft.Json 12.0.3 is outdated, has known advisories, and is entirely unreferenced by the code" |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Review identifies "There is no `appsettings.Development.json` or `appsettings.Production.json`, so one file serves every environment" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| UT | No test project exists anywhere in the solution (no `*.Tests.csproj`, no test files). The following should be covered first. | Missed | Review does not address the aggregate topic of missing unit tests; it instead provides detailed coverage of specific areas that need testing, but does not acknowledge or comment on the absence of a test project itself.
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Found | `GenerateJwtToken` | yes | - |
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
| UT | Missed | `Tests.csproj` | yes | under-credited? |
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
| M1 | Found | `TransactionFeeRate` | yes | - |
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

> **1 row(s) rated `Partial`/`Missed` whose target string IS present in the review** (UT). The score is left as the scorer rated it; read these rows before trusting the Missed count.

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `claude-opus-5` |
| Reasoning strength (system prompt) | (model default) |
| System prompt | `You are an expert computer programmer with an eye for detail, who loves to provide high quality answers.` |
| Ollama `think` | (unset) |
| Temperature | (unknown) |
| top_p | (model default) |
| top_k | (model default) |
| Effort (Anthropic only) | `high` |
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
| Grounding downgrades | `0` |
| Self-declared-absent downgrades | `0` |
| Rows misaligned with ISSUES.md | `0` |
| Review citations past end of file | `0 of 374` |
| Precision (checkable Found rows) | `100% (39 of 39)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 67ece22` |
