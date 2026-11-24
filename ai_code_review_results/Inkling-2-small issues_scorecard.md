# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `afe34f0`

> **70 Found, zero Partial.** The spot-check below found no mis-credited watchlist rows, but a zero-Partial sheet is worth a second look.

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | SampleBankingApp/Services/AuthService.cs:32 - "SQL injection in `Login`: username and password hash are interpolated directly into the query string." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | SampleBankingApp/Services/AuthService.cs:17 - "Hardcoded backdoor credential `AdminBypassPassword = \"SuperAdmin2024\"` committed to source." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | SampleBankingApp/Services/AuthService.cs:30,61-66 - "Passwords hashed with unsalted MD5 (`HashPasswordMd5`), trivially reversible via rainbow tables." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | SampleBankingApp/Services/UserService.cs:47 - "UpdateUser interpolates `email` and `username` directly into the UPDATE statement — SQL injection." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | SampleBankingApp/Services/UserService.cs:99 - "SearchUsers builds `LIKE '%{query}%'` from raw input — SQL injection and wildcard injection." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | SampleBankingApp/Services/TransactionService.cs:47 - "UPDATE Users SET Balance = {newFromBalance} ... uses interpolated SQL instead of parameters." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | SampleBankingApp/Services/TransactionService.cs:89-90 - "RecordTransaction interpolates user-controlled `description` (and `type`) into INSERT — SQL injection." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | SampleBankingApp/appsettings.json:3 - "Production connection string with `sa` password `Admin1234!` committed to source control." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | SampleBankingApp/Program.cs:24 - "`ValidateLifetime = false` disables JWT expiry validation entirely." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | SampleBankingApp/Controllers/UserController.cs:38-54 - "UpdateUser has no ownership or admin check — any user can change any account's email/username." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | SampleBankingApp/Controllers/UserController.cs:56-69 - "DeleteUser has no ownership or admin check — any authenticated user can delete any account." |

## Logic Errors

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | SampleBankingApp/Services/TransactionService.cs:25 - "`if (amount < 0)` allows zero-amount transfers; message says "must be positive"." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | SampleBankingApp/Services/TransactionService.cs:42 - "Balance check `fromBalance >= amount` ignores the fee, so `amount + fee` can drive the balance negative." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | SampleBankingApp/Services/UserService.cs:72 - "`int skip = page * pageSize` is off by one page — page 1 skips the first `pageSize` rows; should be `(page - 1) * pageSize`." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | SampleBankingApp/Services/TransactionService.cs:68 - "`amount * 0.05m * 1` applies a 5% deposit bonus (likely wrong rate, e.g., should be 1%) and contains a redundant `* 1`." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | SampleBankingApp/Services/TransactionService.cs:23-61 - "No self-transfer check — a user can transfer to themselves, burning the fee for nothing." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | SampleBankingApp/Services/UserService.cs:20,40,54 - "Identical id-validation block (`id <= 0` / `id > 1000000`) duplicated in `GetUserById`, `UpdateUser`, and `DeleteUser`." |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs:29-36 - "`JoinWithSeparator` appends the separator after the last item, producing a trailing separator." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | SampleBankingApp/Services/AuthService.cs:68-89 - "GenerateJwtToken is untested: claims, issuer/audience, expiry, and signature validation are unverified." |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | SampleBankingApp/Services/UserService.cs:105-108 - "SearchUsers catches broad `Exception` and returns an empty list — callers cannot distinguish "no results" from "database down"." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | SampleBankingApp/Services/EmailService.cs:75-79 - "SendWelcomeEmail catches broad `Exception` and only writes to console — failures are silently swallowed." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | SampleBankingApp/Services/TransactionService.cs:47-50 - "No database transaction around debit, credit, and audit insert — partial failure corrupts balances." |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | SampleBankingApp/Services/TransactionService.cs:52-55 - "Email is sent after the DB writes commit; if SMTP fails, the exception propagates and the client sees an error even though the transfer succeeded." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | SampleBankingApp/Controllers/UserController.cs:50-53 - "catch (Exception ex) returns StatusCode(500, ex.Message) — raw exception text leaks to clients." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | SampleBankingApp/Data/DatabaseHelper.cs:50-57 - "ExecuteNonQuery closes the connection only on success; exceptions leak it." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | SampleBankingApp/Controllers/AuthController.cs:19-31 - "Login endpoint has no rate limiting or account lockout — brute-force and credential-stuffing are unimpeded." |

## Resource Leaks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | SampleBankingApp/Services/AuthService.cs:34-38 - "SqlConnection created in `Login` is never closed or disposed." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | SampleBankingApp/Data/DatabaseHelper.cs:19-24 - "GetOpenConnection returns an open connection with no documented ownership contract; callers routinely leak it." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | SampleBankingApp/Data/DatabaseHelper.cs:50-57 - "ExecuteNonQuery closes the connection only on success; exceptions leak it; the command is never disposed." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | SampleBankingApp/Services/EmailService.cs:16 - "_smtpClient is an instance field; `EmailService` is not `IDisposable`, so the SMTP socket is never released." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | SampleBankingApp/Services/EmailService.cs:39-43 - "MailMessage in `SendTransferNotification` is never disposed." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | SampleBankingApp/Services/AuthService.cs:70 - "_config[\"Jwt:SecretKey\"]! is null-forgiving; missing key → `GetBytes(null)` throws." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | SampleBankingApp/Services/TransactionService.cs:36 - "`Rows[0]` accessed without checking `Rows.Count` — crashes with `IndexOutOfRangeException` when either user does not exist." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | SampleBankingApp/Services/EmailService.cs:24 - "`int.Parse(_config[\"Email:SmtpPort\"] ?? \"25\")` throws `FormatException` on non-numeric config." |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | SampleBankingApp/Services/EmailService.cs:65 - "username.ToUpper() throws `NullReferenceException` when `username` is null." |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | SampleBankingApp/Helpers/StringHelper.cs:13 - "email.Length throws `NullReferenceException` when `email` is null." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | SampleBankingApp/Controllers/TransactionController.cs:27 - "`int.Parse(userIdClaim!)` throws `ArgumentNullException` when the `NameIdentifier` claim is absent." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | SampleBankingApp/Controllers/UserController.cs:72 - "query is not marked required; a missing query string arrives as null and flows into the SQL builder." |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | SampleBankingApp/Services/TransactionService.cs:11-12 - "TransactionFeeRate = 0.015m" and "MaxTransactionsPerDay = 10" are named constants but belong in configuration. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | SampleBankingApp/Services/TransactionService.cs:65 - "`1000000` deposit cap is an inline magic number." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | SampleBankingApp/Services/EmailService.cs:40,69,89 - "sender address \"notifications@company.com\" duplicated three times." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | SampleBankingApp/Helpers/StringHelper.cs:13,22 - "254" max email length inline and "3" and "20" username length limits inline. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | SampleBankingApp/Services/UserService.cs:70 - "`50` page-size cap is an inline magic number." |

## Dead Code

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | SampleBankingApp/Services/AuthService.cs:91-96 - "HashPasswordSha1 is never called." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | SampleBankingApp/Services/AuthService.cs:98-108 - "Unreachable code after `return true;` in `ValidateToken`." |
| D3 | `TableExists` — never called from any service or controller. | Found | SampleBankingApp/Data/DatabaseHelper.cs:59-65 - "TableExists is defined but never called anywhere." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | SampleBankingApp/Data/DatabaseHelper.cs:67-78 - "ExecuteQueryWithParams is marked `[Obsolete]` and has no callers." |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | SampleBankingApp/Services/EmailService.cs:81-84 - "BuildHtmlTemplate is called only by the dead `SendWelcomeEmailHtml`, so it is effectively dead too." |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | SampleBankingApp/Services/EmailService.cs:86-92 - "SendWelcomeEmailHtml is never called." |
| D7 | `FormatCurrency` — private, never called. | Found | SampleBankingApp/Services/TransactionService.cs:94-97 - "FormatCurrency is never called." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | SampleBankingApp/Services/TransactionService.cs:77-85 - "IsWithinDailyLimit is never called — the daily transaction limit is never enforced." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | SampleBankingApp/Helpers/StringHelper.cs:54-57 - "ObfuscateAccount is never called (and crashes on short input)." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | SampleBankingApp/Helpers/StringHelper.cs:59-63 - "ToTitleCase is never called." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | SampleBankingApp/Helpers/StringHelper.cs:38-41 - "JoinWithSeparatorFixed is never called and merely reimplements `string.Join`." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | SampleBankingApp/Services/UserService.cs:10 - "static List<string> _auditLog is shared mutable state with no synchronization — race conditions and unbounded memory growth." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | SampleBankingApp/Helpers/StringHelper.cs:16 - "new Regex(...) created on every call to `IsValidEmail`." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs:31-35 - "String concatenation inside a loop in `JoinWithSeparator` — O(n²) allocations." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | SampleBankingApp/Services/EmailService.cs:16 - "_smtpClient instance field is not thread-safe and never disposed (also a resource leak)." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | SampleBankingApp/Helpers/StringHelper.cs:65-71 - "IsBlank reimplements `string.IsNullOrWhiteSpace`." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | SampleBankingApp/Data/DatabaseHelper.cs:19-24 - "GetOpenConnection returns an open connection with no documented ownership contract; callers routinely leak it." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | SampleBankingApp/appsettings.json:3 - "Production connection string with `sa` password `Admin1234!` committed to source control." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | SampleBankingApp/appsettings.json:17-21 - "`Debug` log level for `Default`, `Microsoft`, and `System` in the committed (production) config." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | SampleBankingApp/Program.cs:24 - "`ValidateLifetime = false` disables JWT expiry validation entirely." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | SampleBankingApp/Program.cs:36 - "HTTPS redirection is commented out, so traffic may flow over plain HTTP." |
| CF5 | **UseDeveloperExceptionPage() called unconditionally** — full stack traces served to production clients. | Found | SampleBankingApp/Program.cs:34 - "`UseDeveloperExceptionPage()` is called unconditionally, leaking stack traces and internals in production." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | SampleBankingApp/Program.cs:38 - "CORS policy allows any origin, any method, any header (`AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`)." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp/SampleBankingApp.csproj:8-9 - "`DebugSymbols=true` and `DebugType=full` ship full debug symbols in release builds." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | SampleBankingApp/SampleBankingApp.csproj:15 - "Newtonsoft.Json 12.0.3 has known vulnerabilities." |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | SampleBankingApp/appsettings.json:— - "No `appsettings.Production.json` or environment-specific overrides exist." |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| UT | No test project exists in the solution. The following methods and scenarios are the most critical to cover, prioritized by risk: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results. | Found | No test project exists in the solution. The following methods and scenarios are the most critical to cover, prioritized by risk: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, Controller action results. |
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

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `inkling-2-small:cloud` |
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
| Grounding downgrades | `0` |
| Self-declared-absent downgrades | `0` |
| Rows misaligned with ISSUES.md | `0` |
| Review citations past end of file | `0 of 431` |
| Precision (checkable Found rows) | `100% (40 of 40)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ afe34f0` |
