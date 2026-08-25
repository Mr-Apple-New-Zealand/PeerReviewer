# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `74c6567`

> **69 Found, zero Partial.** The spot-check below found no mis-credited watchlist rows, but a zero-Partial sheet is worth a second look.

Total: 69 Found / 0 Partial / 1 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review identifies "Login builds the authentication SQL by interpolating `username` and `hashedPassword`, allowing full authentication bypass with `' OR '1'='1`." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review identifies "AdminBypassPassword is a hardcoded credential constant compiled into the binary" and "Login contains a hardcoded backdoor granting `SuperAdmin` role to `admin`/`SuperAdmin2024` with `Id = 0`." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review identifies "HashPasswordMd5 uses unsalted MD5, which is broken and trivially reversible via rainbow tables" and "HashPasswordSha1 uses unsalted SHA-1, another broken hash for passwords." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Review identifies "UpdateUser interpolates `email`, `username` and `id` directly into an `UPDATE` statement (SQL injection)" and "DeleteUser interpolates `id` into a `DELETE FROM Users` statement." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | Review identifies "SearchUsers interpolates `query` into a `LIKE '%...%'` clause passed to the unsafe `ExecuteQuery` helper" and "ExecuteQuery accepts a raw `tableName` and `whereClause` and concatenates them, making injection unavoidable for every caller." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Review identifies "Transfer interpolates `newFromBalance` and `fromUserId` into an `UPDATE Users` statement" and "Transfer interpolates `newToBalance` and `toUserId` into an `UPDATE Users` statement" and "Deposit interpolates the amount and `userId` into an `UPDATE Users` statement." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Review identifies "RecordTransaction interpolates the user-controlled `description` into an `INSERT`, permitting SQL injection from the transfer endpoint body" and "ExecuteNonQuery accepts a fully-formed raw SQL string, so every write path in the app is an injection vector." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review identifies "A production connection string with the `sa` account and password `Admin1234!` is committed to source control" and "The JWT signing key is the committed literal `mysecretkey`, which is far below the 256-bit minimum for HMAC-SHA256" and "The SMTP account password `EmailPass99` is committed to source control." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review identifies "ValidateLifetime = false means expired tokens are accepted forever" and "GenerateJwtToken issues tokens valid for 30 days with no refresh mechanism, widening the stolen-token window." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | Review identifies "UpdateUser has no ownership or role check, so any authenticated user can change any other user's email and username (IDOR)" |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | Review identifies "DeleteUser has no ownership or role check, so any authenticated user can delete any account" |

## Logic Errors

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Review identifies "Transfer rejects only `amount < 0`, so a zero-amount transfer is accepted and recorded" |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review identifies "Transfer checks `fromBalance >= amount` but then debits `totalDebit = amount + fee`, allowing a negative balance" |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review identifies "GetUsersPage computes `skip = page * pageSize`, so the default `page = 1` silently skips the first page of users" |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Review identifies "Deposit adds a 5% 'interest bonus' (`amount * 0.05m`) to every deposit, which mints money on each call and is almost certainly meant to be 1% or nothing" |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Review identifies "Transfer has no self-transfer guard, so `fromUserId == toUserId` runs two sequential updates and the second overwrites the first, effectively crediting the sender the fee-free amount" |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | Review identifies "GetUserById" and "UpdateUser" and "DeleteUser" all have the same validation block duplicated verbatim |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review identifies "JoinWithSeparator appends the separator after the final element, producing a trailing separator" and "JoinWithSeparator concatenates strings inside a loop, giving O(n²) behaviour" |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | Review identifies "GenerateJwtToken issues tokens valid for 30 days with no refresh mechanism, widening the stolen-token window" |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Review identifies "SearchUsers catches broad `Exception` and returns an empty list, so callers cannot distinguish 'no matches' from 'database down'" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Review identifies "SendWelcomeEmail catches broad `Exception` and merely writes to the console, silently swallowing all failures" |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Review identifies "Transfer performs two `UPDATE`s plus an `INSERT` with no database transaction, so a failure between them destroys or duplicates money" |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | Review identifies "Transfer sends the notification email after the balances are already committed, so an SMTP failure throws out of a successful transfer" |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Review identifies "UpdateUser catches broad `Exception` and returns `ex.Message` in the 500 body" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | Review identifies "ExecuteNonQuery calls `connection.Close()` only on the success path, so an exception during execution leaks the connection" |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | Review identifies "Login has no rate limiting, CAPTCHA or account lockout, allowing unlimited credential stuffing" |

## Resource Leaks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review identifies "Login creates a `SqlConnection`, `SqlCommand` and `SqlDataReader` and never closes or disposes any of them, leaking on every login attempt" |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | Review identifies "GetOpenConnection returns an open `SqlConnection` and transfers disposal responsibility to callers with no documented contract" |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review identifies "ExecuteNonQuery never disposes the `SqlCommand` and only closes the connection on the success path" |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review identifies "_smtpClient is a mutable `SmtpClient` instance field on a scoped service; `SmtpClient` is not thread-safe and is never disposed, so its socket is never released" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review identifies "The `MailMessage` created in `SendTransferNotification` is never disposed, leaking attachments and stream handles" |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Review identifies "Encoding.UTF8.GetBytes(jwtSecret!) throws `ArgumentNullException` at startup if `Jwt:SecretKey` is absent, and the `!` hides it from the compiler" |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Review identifies "Transfer reads `Rows[0]` for both users without verifying the recipient exists, so an unknown `toUserId` throws instead of returning a friendly error" |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | Review identifies "int.Parse(_config["Email:SmtpPort"] ?? "25") throws `FormatException` for a non-numeric configured port" |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | Review identifies "SendWelcomeEmail calls `username.ToUpper()` before any null check on the parameter" |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | Review identifies "IsValidEmail calls `email.Length` before any null check" |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Review identifies "Transfer does `int.Parse(userIdClaim!)` where `FindFirst(...)?.Value` can be null, throwing `ArgumentNullException`" |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | Review identifies "Transfer dereferences `request.ToUserId` with no null check, so a JSON body of `null` causes a `NullReferenceException`" |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review identifies "TransactionFeeRate = 0.015m is a compile-time constant for a business rate that changes" |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | Review identifies "Deposit hardcodes the deposit cap `1000000`" |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Review identifies "SendTransferNotification hardcodes the sender address `notifications@company.com`" |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | Review identifies "IsValidEmail hardcodes the maximum length `254`" |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Review identifies "GetUsersPage hardcodes the maximum page size `50`" |

## Dead Code

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review identifies "HashPasswordSha1 is private and never invoked, producing an unused-member warning" |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Review identifies "The three statements after the unconditional `return true;` in `ValidateToken` are unreachable" |
| D3 | `TableExists` — never called from any service or controller. | Found | Review identifies "TableExists is defined but never called from any file in the repository" |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review identifies "ExecuteQueryWithParams is marked `[Obsolete]` and has no callers anywhere" |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | Review identifies "BuildHtmlTemplate is only called by the dead `SendWelcomeEmailHtml`, so it is transitively dead" |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Review identifies "SendWelcomeEmailHtml is never called" |
| D7 | `FormatCurrency` — private, never called. | Found | Review identifies "FormatCurrency is defined but never called" |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | Review identifies "IsWithinDailyLimit is defined but never called, so the daily transaction cap is unenforced" |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Review identifies "ObfuscateAccount has no callers and duplicates `MaskAccountNumber`" |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | Review identifies "ToTitleCase has no callers" |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review identifies "JoinWithSeparatorFixed has no callers; it is the 'fixed' duplicate that nothing uses" |

## Anti-patterns

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | Review identifies "_auditLog is a shared mutable `static List<string>` mutated from `UpdateUser` and `DeleteUser` with no synchronisation" |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Review identifies "IsValidEmail constructs a new `Regex` on every call instead of caching it" |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review identifies "JoinWithSeparator concatenates strings inside a loop, giving O(n²) behaviour" |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Review identifies "_smtpClient is a mutable `SmtpClient` instance field on a scoped service; `SmtpClient` is not thread-safe and is never disposed" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | Review identifies "IsBlank reimplements `string.IsNullOrWhiteSpace`" |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | Review identifies "GetOpenConnection returns an open `SqlConnection` and transfers disposal responsibility to callers with no documented contract" |

## Configuration Issues

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies "Production database, JWT and SMTP secrets are all committed to source control" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Review identifies "Default, Microsoft and System log levels are all set to Debug, which will flood production logs" |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies "ValidateLifetime = false disables JWT expiry checking" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review identifies "app.UseHttpsRedirection() is commented out, so bearer tokens and passwords can travel in cleartext" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review identifies "UseDeveloperExceptionPage() is called unconditionally for all environments" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review identifies "CORS is configured with `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` on a banking API" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | Review identifies "DebugSymbols=true and DebugType=full are set unconditionally, shipping full PDBs in Release builds" |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | Review identifies "Newtonsoft.Json 12.0.3 is affected by the CVE-2024-21907 denial-of-service advisory" |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Review identifies "There is no `appsettings.Development.json` or `appsettings.Production.json`, so environment-specific overrides are impossible" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| UT | No test project exists in the repository — there is no `*.Tests.csproj`, no solution file referencing one, and no test framework package reference in `SampleBankingApp.csproj`. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results | Missed | Review does not address the aggregate topic of missing unit tests. It discusses specific test scenarios but does not summarize or evaluate the overall lack of a test project.
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

No mis-credits detected in the watchlist.

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
| Effort (Anthropic only) | `xhigh` |
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
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 74c6567` |
