# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `363e42f`

> ⚠ **1 row(s) rated Found name a target that never appears in the review** (N3). Adjusted Found: **68** of 70. See the spot-check below.

Total: 69 Found / 0 Partial / 1 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review identifies SQL injection in Login method via "Login builds SQL via string interpolation of username and hashedPassword" |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review identifies hardcoded admin bypass password with "Hardcoded admin bypass password \"SuperAdmin2024\" allows backdoor access" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review identifies broken password hashing in HashPasswordMd5 method via "HashPasswordMd5 uses unsalted MD5, which is cryptographically broken" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Review identifies SQL injection in UpdateUser/DeleteUser methods via "UpdateUser interpolates email, username, and id into an UPDATE statement" |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | Review identifies SQL injection in SearchUsers method via "SearchUsers passes user-supplied query into a LIKE '%{query}%' clause" |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Review identifies SQL injection in Transfer/Deposit methods via "Transfer interpolates newFromBalance and fromUserId directly into an UPDATE statement" |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Review identifies SQL injection in RecordTransaction method via "RecordTransaction interpolates fromId, toId, amount, type, and description into an INSERT statement" |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review identifies hardcoded production credentials with "Production database credentials (sa / Admin1234!) are committed to source control" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review identifies JWT lifetime validation disabled via "ValidateLifetime = false means expired JWTs are never rejected" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | Review identifies broken access control in UpdateUser endpoint via "UpdateUser has no ownership check; any authenticated user can modify any user's record" |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | Review identifies missing authorization in DeleteUser endpoint via "DeleteUser has no ownership check; any authenticated user can delete any user" |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Review identifies zero amount transfer issue via "Transfer rejects amount < 0 but allows amount == 0" |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review identifies balance check issue via "Transfer checks fromBalance >= amount but then deducts amount + fee" |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review identifies off-by-one error via "GetUsersPage computes skip = page * pageSize, so page 1 skips the first pageSize rows" |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Review identifies incorrect interest rate via "Deposit computes interestBonus = amount * 0.05m * 1" |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Review identifies self-transfer issue via "Transfer has no self-transfer check; a user can transfer to their own account" |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | Review identifies duplicated validation via "GetUserById contains the same id <= 0 / id > 1000000 validation block" |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review identifies O(n²) string concatenation via "JoinWithSeparator uses += string concatenation inside a loop" |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | _(ungrounded: no matching sentence in review)_ |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Review identifies exception swallowing in SearchUsers via "SearchUsers catches a broad Exception and returns an empty list" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Review identifies broad exception catching in SendWelcomeEmail via "SendWelcomeEmail catches a broad Exception and only writes to Console.WriteLine" |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Review identifies missing database transactions via "Transfer performs two separate ExecuteNonQuery calls without a database transaction" |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | Review identifies email failure propagation issue via "Transfer sends an email after DB writes have committed; if SendTransferNotification throws, the caller receives a 500" |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Review identifies message exposure in UserController via "UpdateUser returns ex.Message (an ArgumentException) directly to the HTTP client" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | Review identifies connection closing issue via "ExecuteNonQuery calls GetOpenConnection, closes the connection, but does not dispose the SqlCommand" |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | Review identifies missing rate limiting in AuthController via "No rate limiting or account lockout on the login endpoint, enabling brute-force attacks" |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review identifies resource leak in Login method via "Login creates SqlConnection, SqlCommand, and SqlDataReader without any using or Close()/Dispose() calls" |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | Review identifies resource leak in DatabaseHelper via "GetOpenConnection returns an open SqlConnection with no using contract" |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review identifies resource leak in ExecuteNonQuery via "ExecuteNonQuery calls GetOpenConnection, closes the connection, but does not dispose the SqlCommand" |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review identifies SmtpClient resource leak via "SmtpClient is held as an instance field; SmtpClient is not thread-safe and the underlying socket is never released" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review identifies MailMessage resource leak via "SendTransferNotification creates a MailMessage (which implements IDisposable) but never disposes it" |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Review identifies null check issue via "Encoding.UTF8.GetBytes(jwtSecret!) will throw ArgumentNullException if the config key is missing" |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Review identifies null check issue via "fromUserTable.Rows[0] is accessed without checking Rows.Count > 0" |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | Review identifies null check issue via "_config[\"Email:SmtpHost\"] can be null, passed to the SmtpClient constructor" |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | Review identifies null check issue via "username.ToUpper() throws NullReferenceException if username is null" |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | Review identifies null check issue via "_config[\"Email:Username\"] can be null, passed to NetworkCredential" |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Review identifies null check issue via "User.FindFirst(...)?.Value can be null; int.Parse(null!) throws ArgumentNullException" |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | Review identifies null check issue via "request is used without a null check; if the body is missing, request.Username throws NullReferenceException" |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review identifies magic numbers via "Deposit cap 1000000 is an inline literal" |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | Review identifies magic number issue via "Deposit cap 1000000 is an inline literal" |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Review identifies magic strings via "Sender address \"notifications@company.com\" is hardcoded" |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | Review identifies magic numbers via "Email max length 254 is an inline literal" |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Review identifies magic number issue via "Max page size 50 is an inline literal" |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review identifies dead code via "HashPasswordSha1 is never called by any code in the project" |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Review identifies unreachable code via "Code after return true; in ValidateToken is unreachable" |
| D3 | `TableExists` — never called from any service or controller. | Found | Review identifies dead code via "TableExists is never called anywhere in the codebase" |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review identifies dead code via "ExecuteQueryWithParams is marked [Obsolete] and is never called" |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | Review identifies dead code via "BuildHtmlTemplate is only called by the dead SendWelcomeEmailHtml" |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Review identifies dead code via "SendWelcomeEmailHtml is never called by any code in the project" |
| D7 | `FormatCurrency` — private, never called. | Found | Review identifies dead code via "FormatCurrency is never called by any code in the project" |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | Review identifies dead code via "IsWithinDailyLimit is never called by any code in the project" |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Review identifies dead code via "ObfuscateAccount is never called by any code in the project" |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | Review identifies dead code via "ToTitleCase is never called by any code in the project" |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review identifies dead code via "JoinWithSeparatorFixed is never called by any code in the project" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | Review identifies mutable static state via "static List<string> _auditLog is shared mutable state accessed from multiple threads without synchronization" |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Review identifies regex compilation issue via "IsValidEmail creates a new Regex(...) on every call" |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review identifies string concatenation issue via "JoinWithSeparator uses += string concatenation inside a loop (O(n²))" |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Review identifies shared SmtpClient issue via "SmtpClient is held as an instance field; SmtpClient is not thread-safe" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | Review identifies reimplemented BCL via "IsBlank reimplements string.IsNullOrWhiteSpace" |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | Review identifies leaking connection issue via "GetOpenConnection leaks resource ownership to callers with no documented disposal contract" |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies production secrets issue via "Production database credentials (sa / Admin1234!) are committed to source control" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Review identifies log level configuration issue via "Log level is set to Debug for Default, Microsoft, and System namespaces" |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies JWT lifetime validation issue via "ValidateLifetime = false means expired JWTs are never rejected" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review identifies HTTPS configuration issue via "UseHttpsRedirection() is commented out, allowing plaintext HTTP" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review identifies exception page configuration issue via "UseDeveloperExceptionPage() is called unconditionally, exposing stack traces in production" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review identifies CORS configuration issue via "CORS policy allows any origin, any method, and any header simultaneously" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | Review identifies debug symbol configuration issue via "DebugSymbols and DebugType are set unconditionally, shipping debug symbols in release builds" |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | Review identifies outdated package issue via "Newtonsoft.Json 12.0.3 is outdated and has known CVEs" |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Review identifies missing production settings via "No appsettings.Production.json exists to override debug settings for production" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project exists in the repository. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results | Found | Review identifies missing unit tests via "No test project exists in the repository"
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
| CF9 | Found | `appsettings.Production` | yes | - |

**Adjusted Found: 68 of 70** (69 reported, less 1 mis-credited).

### Self-hedged ratings

Rows rated `Found` whose own Note concedes the review did not cover the target. That phrasing describes a Partial; each is likely an over-credit, though a conceded detail can be incidental to the reference issue.

| ID | Hedge | Note |
|---|---|---|
| E6 | `but does not` | Review identifies connection closing issue via "ExecuteNonQuery calls GetOpenConnection, closes the connection, but does not dispose the SqlCommand" |
| RL3 | `but does not` | Review identifies resource leak in ExecuteNonQuery via "ExecuteNonQuery calls GetOpenConnection, closes the connection, but does not dispose the SqlCommand" |

**Plausible floor: 66 of 70** (adjusted 68, less 2 self-hedged).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3.6-27B:Q4_K_S` |
| Reasoning strength (system prompt) | (model default) |
| Ollama `think` | `medium` |
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
| Grounding downgrades | `1` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 363e42f` |
