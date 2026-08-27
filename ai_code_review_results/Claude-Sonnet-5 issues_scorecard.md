# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22`

> ⚠ **1 row(s) rated Found name a target that never appears in the review** (N4). Adjusted Found: **69** of 70. See the spot-check below.

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "SampleBankingApp/Services/AuthService.cs | 32 | `Login` builds SQL by interpolating `username` directly into the query string, allowing SQL injection." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "SampleBankingApp/Services/AuthService.cs | 17, 53-56 | Hardcoded backdoor password `AdminBypassPassword = "SuperAdmin2024"` grants unauthenticated SuperAdmin access bypassing the database." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "SampleBankingApp/Services/AuthService.cs | 61-66 | Passwords are hashed with unsalted MD5 (`HashPasswordMd5`), which is cryptographically broken and vulnerable to rainbow-table attacks." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "SampleBankingApp/Services/UserService.cs | 47 | `UpdateUser` builds an UPDATE statement by interpolating `email` and `username`, enabling SQL injection." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "SampleBankingApp/Services/UserService.cs | 99 | `SearchUsers` passes user-supplied `query` into a LIKE clause via `ExecuteQuery`, enabling SQL injection." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "SampleBankingApp/Services/TransactionService.cs | 47-48 | Balance UPDATE statements are built via string interpolation of computed values and user-supplied ids." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "SampleBankingApp/Services/TransactionService.cs | 89-90 | `RecordTransaction` interpolates `description` (user-controlled from `TransferRequest.Description`) directly into an INSERT statement, enabling SQL injection." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "SampleBankingApp/appsettings.json | 3, 6, 14 | Production DB password, weak JWT secret (`mysecretkey`), and email password are committed to source control in plaintext." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry enforcement, so stolen/expired tokens remain valid forever." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | "SampleBankingApp/Controllers/UserController.cs | 21-29, 38-69 | `GetUser`, `UpdateUser`, `DeleteUser` only require `[Authorize]` with no ownership/role check — any authenticated user can view/modify/delete any other user's account (broken access control)." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | "SampleBankingApp/Controllers/UserController.cs | 21-29, 38-69 | `GetUser`, `UpdateUser`, `DeleteUser` only require `[Authorize]` with no ownership/role check — any authenticated user can view/modify/delete any other user's account (broken access control)." |

## Logic Errors

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | "SampleBankingApp/Services/TransactionService.cs | 25-26 | `amount < 0` check allows `amount == 0`, letting a zero-value transfer proceed and still incur logic/fee side effects." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "SampleBankingApp/Services/TransactionService.cs | 39-42 | `Transfer` checks `fromBalance >= amount` but then debits `totalDebit = amount + fee`, allowing the balance to go negative when the fee pushes the debit above the checked amount." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "SampleBankingApp/Services/UserService.cs | 72 | `GetUsersPage` computes `skip = page * pageSize` instead of `(page - 1) * pageSize`, causing page 1 to skip a full page of results (off-by-one)." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | "SampleBankingApp/Services/TransactionService.cs | 68 | `Deposit` grants a flat 5% "interest bonus" instantly on every deposit (`amount * 0.05m * 1`), which is an implausible/incorrect business rule (likely meant to be a much smaller rate or not applied on deposit at all)." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | "SampleBankingApp/Services/TransactionService.cs | 23-61 | `Transfer` has no check preventing `fromUserId == toUserId`, allowing a self-transfer that still deducts a fee for no economic effect." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | "SampleBankingApp/Services/UserService.cs | 20-23, 40-43, 54-57 | Duplicated id-validation logic (`id <= 0` / `id > 1000000`) repeated identically in `GetUserById`, `UpdateUser`, `DeleteUser`. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` concatenates strings in a loop — O(n²) performance; a correct version (`JoinWithSeparatorFixed`) already exists alongside it." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | "SampleBankingApp/Services/AuthService.cs | 28-59 | `Login` mixes SQL querying, password hashing, backdoor-credential checking, and User object mapping in one method." |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "SampleBankingApp/Services/UserService.cs | 95-109 | `SearchUsers` catches broad `Exception` and returns an empty list, making it impossible for callers to distinguish "no matches" from a DB failure." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | "SampleBankingApp/Services/EmailService.cs | 45-60 | After `MaxRetries` failed attempts, `SendTransferNotification` rethrows `SmtpException`, which (per above) can bubble up after a successful DB commit and surface as an unrelated 500 to the transfer caller." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | "SampleBankingApp/Services/TransactionService.cs | 42-58 | `Transfer` performs two balance UPDATEs and an INSERT without wrapping them in a database transaction; a failure between statements leaves accounts in an inconsistent state." |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | "SampleBankingApp/Services/TransactionService.cs | 50-56 | Email notification (`SendTransferNotification`) is sent after balance updates and transaction recording have already committed; if the email throws, the exception propagates to the controller even though the transfer itself succeeded, misleading the client." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | "SampleBankingApp/Controllers/UserController.cs | 38-54 | `UpdateUser` catches generic `Exception` and returns `ex.Message` directly to the HTTP client, leaking internal error details." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` only calls `connection.Close()` on the success path; if `ExecuteNonQuery()` throws, the connection is never closed." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | "SampleBankingApp/Controllers/AuthController.cs | 19-31 | No rate limiting or account lockout on the login endpoint, allowing unlimited brute-force attempts." |

## Resource Leaks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "SampleBankingApp/Services/AuthService.cs | 34-38 | `Login` opens a `SqlConnection` and executes a `SqlDataReader` without ever closing or disposing either, even in the success and failure paths." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 26-34 | `ExecuteQuery` obtains a connection via `GetOpenConnection()` but never closes/disposes it." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` opens a connection without `using`; any exception during `ExecuteNonQuery()` skips `connection.Close()`, leaking the connection." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "SampleBankingApp/Services/EmailService.cs | 16, 22-32 | `SmtpClient` is held as a long-lived instance field, which is not thread-safe and keeps a socket/connection open for the lifetime of the (scoped) service; it is also never disposed." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "SampleBankingApp/Services/EmailService.cs | 39-43 | `MailMessage` created in `SendTransferNotification` is never disposed." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | "SampleBankingApp/Program.cs | 16, 28 | `jwtSecret` from `builder.Configuration["Jwt:SecretKey"]` can be null; it's force-unwrapped with `!` before `Encoding.UTF8.GetBytes." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "SampleBankingApp/Services/TransactionService.cs | 36-37 | `fromUserTable.Rows[0]` / `toUserTable.Rows[0]` are accessed without checking `Rows.Count > 0`; a non-existent `fromUserId`/`toUserId` causes an unhandled `IndexOutOfRangeException`." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | "SampleBankingApp/Services/EmailService.cs | 22 | `_config["Email:SmtpHost"]` may be null and is passed directly to the `SmtpClient` constructor, which can throw." |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | "SampleBankingApp/Services/EmailService.cs | 69 | `MailMessage` created in `SendWelcomeEmail` is never disposed." |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 13 | Magic number `254` (max email length) is inline." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "SampleBankingApp/Controllers/TransactionController.cs | 26-27 | `userIdClaim` from `User.FindFirst(...)?.Value` can be null if the claim is missing; `int.Parse(userIdClaim!)` will throw `ArgumentNullException`." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | "SampleBankingApp/Controllers/UserController.cs | 39-43 | `request` (`UpdateUserRequest`) used without a null check before accessing `request.Email`/`request.Username`." |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | "SampleBankingApp/Services/TransactionService.cs | 68 | Literal `0.05m` (5% "interest bonus") is not a named constant and is unexplained." |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | "SampleBankingApp/Services/TransactionService.cs | 65 | Literal `1000000` deposit cap is inline rather than a named constant/config value." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | "SampleBankingApp/Services/EmailService.cs | 40, 69, 89 | Literal sender address `"notifications@company.com"` repeated three times." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | "SampleBankingApp/Helpers/StringHelper.cs | 13 | Magic number `254` (max email length) is inline." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "SampleBankingApp/Services/UserService.cs | 70 | Magic number `50` (max page size) is inline." |

## Dead Code

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | "SampleBankingApp/Services/AuthService.cs | 91-96 | `HashPasswordSha1` is never called anywhere in the codebase." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "SampleBankingApp/Services/AuthService.cs | 105-107 | Code after the unconditional `return true;` inside `ValidateToken` (handler/jwtToken logic) is unreachable." |
| D3 | `TableExists` — never called from any service or controller. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 59-65 | `TableExists` is never called anywhere." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 67-78 | `ExecuteQueryWithParams` is marked `[Obsolete]` yet remains in the codebase and is never called." |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | "SampleBankingApp/Services/EmailService.cs | 81-84 | `BuildHtmlTemplate` is only referenced by the also-unused `SendWelcomeEmailHtml`, making it effectively dead." |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | "SampleBankingApp/Services/EmailService.cs | 86-92 | `SendWelcomeEmailHtml` is never called anywhere." |
| D7 | `FormatCurrency` — private, never called. | Found | "SampleBankingApp/Services/TransactionService.cs | 94-97 | `FormatCurrency` is never called anywhere." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | "SampleBankingApp/Services/TransactionService.cs | 77-85 | `IsWithinDailyLimit` is defined but never called." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 54-57 | `ObfuscateAccount` is never called anywhere and duplicates `MaskAccountNumber`'s purpose." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 59-63 | `ToTitleCase` is never called anywhere." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 38-41 | `JoinWithSeparatorFixed` is never called anywhere." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | "SampleBankingApp/Services/UserService.cs | 10-11 | `_auditLog` and `_requestCount` are `static` mutable fields on a service registered as `Scoped`, accessed without any locking — a race condition under concurrent requests." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 16 | `IsValidEmail` creates a `new Regex(...)` on every call." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` concatenates strings in a loop — O(n²) performance; a correct version (`JoinWithSeparatorFixed`) already exists alongside it." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "SampleBankingApp/Services/EmailService.cs | 16 | `SmtpClient` stored as an instance field is not thread-safe and couples the service to one long-lived connection — an anti-pattern regardless of the leak issue already noted." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "SampleBankingApp/Helpers/StringHelper.cs | 65-71 | `IsBlank` reimplements the framework's `string.IsNullOrWhiteSpace`." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "SampleBankingApp/Data/DatabaseHelper.cs | 26-34 | `ExecuteQuery(tableName, whereClause)` is a helper explicitly designed to accept raw SQL fragments with no documented safety contract, inviting injection at every call site." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "SampleBankingApp/appsettings.json | 3, 6, 14 | Production DB password, weak JWT secret (`mysecretkey`), and email password are committed to source control in plaintext." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | "SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally for all environments." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry enforcement, so stolen/expired tokens remain valid forever." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out, allowing plaintext HTTP traffic." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, leaking stack traces in production." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "SampleBankingApp/Program.cs | 38 | CORS policy allows any origin, method, and header — fully open CORS." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | "SampleBankingApp/SampleBankingApp.csproj | 8-9 | `DebugSymbols`/`DebugType full` apply to all configurations including Release, shipping full PDBs to production." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | "SampleBankingApp/SampleBankingApp.csproj | 15 | `Newtonsoft.Json` 12.0.3 is an old version with known vulnerabilities (fixed in 13.x) and appears entirely unused in the source." |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | "SampleBankingApp/appsettings.json | 17-21 | Logging levels are set to `Debug` for `Default`, `Microsoft`, and `System`, which is excessive for production and can leak sensitive info/verbose logs." |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `TransactionService.Transfer`, `UserService.GetUsersPage`, etc. | Found | "No test project exists anywhere in the repository. The following methods/scenarios are the highest priority to cover:" |
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
| A5 | Found | `IsBlank` | yes | - |
| CF3 | Found | `ValidateLifetime` | yes | - |
| CF4 | Found | `UseHttpsRedirection` | yes | - |
| CF5 | Found | `UseDeveloperExceptionPage` | yes | - |
| CF6 | Found | `AllowAnyOrigin` | yes | - |
| CF7 | Found | `DebugType` | yes | - |
| CF8 | Found | `Newtonsoft` | yes | - |

**Adjusted Found: 69 of 70** (70 reported, less 1 mis-credited).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `claude-sonnet-5` |
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
| Review citations past end of file | `0 of 201` |
| Precision (checkable Found rows) | `98% (39 of 40)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 67ece22` |
