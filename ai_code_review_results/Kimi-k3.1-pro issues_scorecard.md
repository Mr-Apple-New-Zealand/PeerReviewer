# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `55a4ec7`

> ⚠ **1 row(s) rated Found concede in their own Note that the review fell short** (N1). Plausible floor: **68** of 70. See the spot-check below.

Total: 69 Found / 1 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Services/AuthService.cs:32 | `Login` interpolates `username` directly into SQL, allowing authentication bypass and other SQL injection. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Services/AuthService.cs:53–56 | The hardcoded `admin` bypass creates a `SuperAdmin` identity without normal database authentication. |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Services/AuthService.cs:30, 61–65 | Passwords are hashed with fast, unsalted MD5, making stored hashes inexpensive to crack. |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Services/UserService.cs:47–48 | `UpdateUser` interpolates `email` and `username` into an UPDATE statement, permitting SQL injection. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | Services/UserService.cs:95–100 | `SearchUsers` places the user-controlled LIKE value into `ExecuteQuery`, permitting SQL injection. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Services/TransactionService.cs:47 | The sender balance UPDATE interpolates values into SQL; the typed values prevent straightforward string injection today, but the statement is culture-sensitive and unsafe to extend. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Services/TransactionService.cs:87–91 | `RecordTransaction` interpolates the user-controlled `description` into an INSERT statement, permitting SQL injection and statement batching. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | appsettings.json:2–4 | A production-looking database login and password are committed to source control. |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Program.cs:24 | `ValidateLifetime = false` allows expired JWTs to remain valid indefinitely. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | Controllers/UserController.cs:38–54 | `UpdateUser` has no ownership or administrator check, so any authenticated user can modify any account. |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | Controllers/UserController.cs:56–69 | `DeleteUser` has no ownership or administrator check, allowing arbitrary account deletion. |

## Logic Errors

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Services/TransactionService.cs:25–26 | `Transfer` rejects only negative amounts, so zero-value transfers create transaction records and send notifications. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Services/TransactionService.cs:39–44 | The balance check compares `fromBalance` with `amount` but deducts `amount + fee`, allowing a negative balance. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Services/UserService.cs:72 | `GetUsersPage` calculates `skip` as `page * pageSize`, so page 1 skips the first page. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Services/TransactionService.cs:68 | `Deposit` adds an undocumented 5% bonus, over-crediting by four percentage points if the intended rate is 1%. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Services/TransactionService.cs:23–48 | `Transfer` does not reject self-transfers, and the second absolute balance update overwrites the first so the account ends with its original balance plus the transfer amount. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | Services/UserService.cs:20, 38, 54 | The first copy of the two-part user-ID validation block is in `GetUserById`. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Helpers/StringHelper.cs:29 | `JoinWithSeparator` performs string concatenation in a loop, causing repeated allocations and quadratic behavior for large inputs. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | Services/AuthService.cs:68–89 | JWT generation and middleware validation lack tests for claims, expiry, invalid signatures, issuer, audience, and missing configuration. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Services/UserService.cs:97–108 | `SearchUsers` catches every exception and returns an empty list, making database failures indistinguishable from no matches. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Services/EmailService.cs:71–78 | `SendWelcomeEmail` catches every exception, writes to the console, and hides delivery failure from its caller. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Services/TransactionService.cs:47–50 | `Transfer` performs two balance updates and a transaction insert without a shared database transaction. |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | Services/TransactionService.cs:47–57 | `Transfer` sends email after financial writes, so an SMTP failure can produce an HTTP error after money has already moved and encourage a duplicate retry. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Controllers/UserController.cs:50–53 | `UpdateUser` returns raw `ex.Message` to HTTP clients, potentially exposing SQL and server internals. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | Data/DatabaseHelper.cs:52–55 | `ExecuteNonQuery` skips `Close` when command execution throws and never explicitly disposes the connection. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | Controllers/AuthController.cs:19–31 | `Login` has no rate limiting, throttling, or account lockout, enabling password spraying and brute force. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Services/AuthService.cs:34–58 | `Login` never disposes its `SqlConnection`, including both successful and backdoor return paths. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | Data/DatabaseHelper.cs:28–33 | `ExecuteQuery` never closes or disposes its connection on success or failure. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Data/DatabaseHelper.cs:52–55 | `ExecuteNonQuery` skips `Close` when command execution throws and never explicitly disposes the connection. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Services/EmailService.cs:16, 22–31 | A single `SmtpClient` is retained as an instance field, never disposed, and shared through a service even though the client is not thread-safe. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Services/EmailService.cs:39–60 | `SendTransferNotification` never disposes its `MailMessage`, including retry and exception paths. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Program.cs:16, 28 | `jwtSecret!` suppresses nullable analysis but does not prevent `Encoding.UTF8.GetBytes` from receiving null. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Services/TransactionService.cs:36 | `Transfer` accesses `fromUserTable.Rows[0]` without checking that the sender exists. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | Services/EmailService.cs:22–24 | The SMTP host can be null and a present but malformed port value causes `int.Parse` to throw during service construction. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | Services/EmailService.cs:63–69 | `SendWelcomeEmail` calls `username.ToUpper()` before any null check. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | Helpers/StringHelper.cs:11–16 | `IsValidEmail` reads `email.Length` before checking for null. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Controllers/TransactionController.cs:26–29 | `Transfer` passes a possibly missing or nonnumeric name-identifier claim to `int.Parse`. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | Controllers/UserController.cs:39–43 | `UpdateUser` dereferences the request without an explicit null or field validation guard. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Services/TransactionService.cs:65 | The deposit cap `1000000` is an inline financial limit. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | Services/TransactionService.cs:65 | The deposit cap `1000000` is an inline financial limit. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Services/EmailService.cs:40, 69, 89 | `notifications@company.com` is hardcoded as the transfer sender. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | Helpers/StringHelper.cs:13, 22 | The email length limit `254` is an unnamed inline literal. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Services/UserService.cs:70 | The maximum page size `50` is embedded in the service. |

## Dead Code

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Services/AuthService.cs:91–96 | `HashPasswordSha1` retains another weak password-hashing implementation, although it is currently unused. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Services/AuthService.cs:103–107 | The token-reading code after unconditional `return true` is unreachable. |
| D3 | `TableExists` — never called from any service or controller. | Found | Data/DatabaseHelper.cs:59–65 | `TableExists` has no caller in any supplied source file. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Data/DatabaseHelper.cs:67–78 | `ExecuteQueryWithParams` has no caller and remains present despite being marked `[Obsolete]`. |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | Services/EmailService.cs:81–84 | `BuildHtmlTemplate` is called only by the unused `SendWelcomeEmailHtml`, making the entire HTML path transitively unreachable. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Services/EmailService.cs:86–92 | `SendWelcomeEmailHtml` has no caller. |
| D7 | `FormatCurrency` — private, never called. | Found | Services/TransactionService.cs:94–97 | `FormatCurrency` has no caller. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | Services/TransactionService.cs:77–85 | `IsWithinDailyLimit` has no caller, and `MaxTransactionsPerDay` consequently provides no enforcement. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Helpers/StringHelper.cs:54–57 | `ObfuscateAccount` has no caller in the supplied source. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | Helpers/StringHelper.cs:59–63 | `ToTitleCase` has no caller in the supplied source. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Helpers/StringHelper.cs:38–41 | `JoinWithSeparatorFixed` also has no caller, so the fixed duplicate is unused as well. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | Services/UserService.cs:10, 45, 64 | `_auditLog` is a shared mutable static `List` accessed by multiple scoped service instances without synchronization, and it grows without bound. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Helpers/StringHelper.cs:16 | `IsValidEmail` constructs a new `Regex` on every call. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Helpers/StringHelper.cs:29 | `JoinWithSeparator` performs string concatenation in a loop, causing repeated allocations and quadratic behavior for large inputs. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Services/EmailService.cs:34 | `SmtpClient` is not thread-safe and should be created per-send, not held as a field. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | Helpers/StringHelper.cs:65–71 | `IsBlank` manually reimplements `string.IsNullOrWhiteSpace`. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | Data/DatabaseHelper.cs:19–24 | `GetOpenConnection` transfers ownership of an open connection to callers without documenting that contract, and both callers handle it incorrectly. |

## Configuration Issues

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | appsettings.json:2–4 | A production-looking database login and password are committed to source control. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | appsettings.json:18 | The default log level is `Debug`, which is inappropriate as a production baseline. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Program.cs:24 | JWT lifetime validation is explicitly disabled. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Program.cs:36 | HTTPS redirection is disabled and no production HSTS setup is present. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Program.cs:34 | `UseDeveloperExceptionPage` is unconditional rather than environment-specific. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Program.cs:38 | The CORS policy is fully permissive for every environment. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp.csproj:8 | Full debug symbols are emitted unconditionally, including Release builds, increasing disclosure if PDB files are published. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | SampleBankingApp.csproj:15 | `Newtonsoft.Json` 12.0.3 is an old release with known advisories affecting older versions and is unused in the supplied source. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Repository | No `appsettings.Production.json` or equivalent environment-specific override is supplied, so the base file applies everywhere. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| UT | No test project is present in the supplied source. | Found | No test project is present in the supplied source. |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Partial | `GenerateJwtToken` | yes | under-credited? |
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

> **1 row(s) rated `Partial`/`Missed` whose target string IS present in the review** (R3). The score is left as the scorer rated it; read these rows before trusting the Missed count.

### Self-hedged ratings

Rows rated `Found` whose own Note concedes the review did not cover the target. That phrasing describes a Partial; each is likely an over-credit, though a conceded detail can be incidental to the reference issue.

| ID | Hedge | Note |
|---|---|---|
| N1 | `but does not` | Program.cs:16, 28 \| `jwtSecret!` suppresses nullable analysis but does not prevent `Encoding.UTF8.GetBytes` from receiving null. |

**Plausible floor: 68 of 70** (adjusted 69, less 1 self-hedged).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `kimi-k3.1-pro:cloud` |
| Reasoning strength (system prompt) | (model default) |
| System prompt | `You are an expert computer programmer with an eye for detail, who loves to provide high quality answers.` |
| Ollama `think` | (unset) |
| Temperature | `0.0` |
| top_p | (model default) |
| top_k | (model default) |
| Effort (Anthropic only) | (n/a) |
| num_ctx | `65536` |
| num_predict | `100000` |
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
| Review citations past end of file | `0 of 399` |
| Precision (checkable Found rows) | `100% (39 of 39)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 55a4ec7` |
