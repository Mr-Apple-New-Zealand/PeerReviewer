# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `00111c5`

> ⚠ **3 row(s) rated Found name a target that never appears in the review** (R3, N3, D5). Adjusted Found: **67** of 70. See the spot-check below.

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | SampleBankingApp/Services/AuthService.cs:32 - SQL injection vulnerability in `Login` method via interpolated `username` and `hashedPassword`. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | SampleBankingApp/Services/AuthService.cs:17 - Hardcoded admin bypass password `AdminBypassPassword` allows backdoor access. |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | SampleBankingApp/Services/AuthService.cs:61 - Weak cryptography using `MD5` for password hashing in `HashPasswordMd5`. |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | SampleBankingApp/Services/UserService.cs:47 - SQL injection in `UpdateUser` method via interpolated `email`, `username`, and `id`. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | SampleBankingApp/Services/UserService.cs:99 - SQL injection in `SearchUsers` method via interpolated `query` in LIKE clause. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | SampleBankingApp/Services/TransactionService.cs:47 - SQL injection in `Transfer` method via interpolated `newFromBalance` and `fromUserId`. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | SampleBankingApp/Services/TransactionService.cs:89 - SQL injection in `RecordTransaction` method via interpolated values. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | SampleBankingApp/appsettings.json:3 - Production database connection string with credentials committed to source control. |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | SampleBankingApp/Program.cs:24 - JWT misconfiguration with `ValidateLifetime = false` allowing expired tokens. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | SampleBankingApp/Controllers/UserController.cs:38 - Broken access control in `UpdateUser` endpoint missing ownership checks. |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | SampleBankingApp/Controllers/UserController.cs:56 - Broken access control in `DeleteUser` endpoint missing ownership checks. |

## Logic Errors

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | SampleBankingApp/Services/TransactionService.cs:25 - `amount < 0` check allows zero-amount transfers which are nonsensical. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | SampleBankingApp/Services/TransactionService.cs:42 - Balance check `fromBalance >= amount` excludes the fee, but `totalDebit` is deducted, causing negative balances. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | SampleBankingApp/Services/UserService.cs:72 - Off-by-one error in pagination where `page * pageSize` skips the first page's worth of items. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | SampleBankingApp/Services/TransactionService.cs:68 - Interest bonus applied as 5% via `0.05m * 1` which may be an incorrect rate or redundant constant. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | SampleBankingApp/Services/TransactionService.cs:23 - Missing self-referential check allowing a user to transfer funds to themselves. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | SampleBankingApp/Services/UserService.cs:20 - Duplicated validation logic for user ID in `GetUserById`, `UpdateUser`, and `DeleteUser`. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs:31 - String concatenation inside a loop in `JoinWithSeparator` is O(n²). |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | SampleBankingApp/Services/AuthService.cs:98 - Code after unconditional `return true;` in `ValidateToken` is unreachable. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | SampleBankingApp/Services/UserService.cs:105 - `SearchUsers` catches broad `Exception` and swallows it silently, returning an empty list. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | SampleBankingApp/Services/EmailService.cs:63 - `SendWelcomeEmail` method is defined but never called. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | SampleBankingApp/Services/TransactionService.cs:47 - Missing database transaction wrapping the two balance updates and transaction record in `Transfer`. |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | SampleBankingApp/Services/TransactionService.cs:52 - Side effect `SendTransferNotification` can throw after DB writes have committed in `Transfer`. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | SampleBankingApp/Controllers/UserController.cs:52 - Raw `ex.Message` returned to HTTP clients in the `UpdateUser` catch block. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | SampleBankingApp/Data/DatabaseHelper.cs:52 - `SqlConnection` opened in `ExecuteNonQuery` but only closed, not disposed. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | SampleBankingApp/Controllers/AuthController.cs:19 - Missing rate limiting or account lockout on the `Login` endpoint. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | SampleBankingApp/Services/AuthService.cs:34 - `SqlConnection` opened in `Login` but never closed or disposed. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | SampleBankingApp/Data/DatabaseHelper.cs:28 - `SqlConnection` opened in `ExecuteQuery` but never disposed. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | SampleBankingApp/Data/DatabaseHelper.cs:52 - `SqlConnection` opened in `ExecuteNonQuery` but only closed, not disposed. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | SampleBankingApp/Services/EmailService.cs:16 - `SmtpClient` held as an instance field, which is not thread-safe and never disposed. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | SampleBankingApp/Services/EmailService.cs:39 - `MailMessage` created in `SendTransferNotification` but never disposed. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | SampleBankingApp/Program.cs:28 - `_config["Jwt:SecretKey"]` passed to `Encoding.UTF8.GetBytes` with null-forgiving operator but no actual null check. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | SampleBankingApp/Services/TransactionService.cs:36 - `fromUserTable.Rows[0]` accessed without first checking `Rows.Count > 0`. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | SampleBankingApp/Services/EmailService.cs:40 - `"notifications@company.com"` hardcoded email address. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | SampleBankingApp/Services/EmailService.cs:65 - `username.ToUpper()` called before a null check in `SendWelcomeEmail`. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | SampleBankingApp/Helpers/StringHelper.cs:13 - `email.Length` accessed before a null check in `IsValidEmail`. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | SampleBankingApp/Controllers/TransactionController.cs:27 - `userIdClaim` passed to `int.Parse` with null-forgiving operator but no null check. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | SampleBankingApp/Controllers/UserController.cs:56 - Broken access control in `DeleteUser` endpoint missing ownership checks. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | SampleBankingApp/Services/TransactionService.cs:65 - `1000000` deposit cap is an inline magic number. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | SampleBankingApp/Services/TransactionService.cs:65 - `1000000` deposit cap is an inline magic number. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | SampleBankingApp/Services/EmailService.cs:40 - `"notifications@company.com"` hardcoded email address. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | SampleBankingApp/Helpers/StringHelper.cs:13 - `254` email length limit is an inline magic number. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | SampleBankingApp/Services/UserService.cs:70 - `50` page size limit is an inline magic number. |

## Dead Code

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | SampleBankingApp/Services/AuthService.cs:91 - `HashPasswordSha1` method is defined but never called. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | SampleBankingApp/Services/AuthService.cs:104 - Code after unconditional `return true;` in `ValidateToken` is unreachable. |
| D3 | `TableExists` — never called from any service or controller. | Found | SampleBankingApp/Data/DatabaseHelper.cs:59 - `TableExists` method is defined but never called. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | SampleBankingApp/Data/DatabaseHelper.cs:68 - `ExecuteQueryWithParams` method is marked obsolete and never called. |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | SampleBankingApp/Services/EmailService.cs:86 - `SendWelcomeEmailHtml` method is defined but never called. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | SampleBankingApp/Services/EmailService.cs:86 - `SendWelcomeEmailHtml` method is defined but never called. |
| D7 | `FormatCurrency` — private, never called. | Found | SampleBankingApp/Services/TransactionService.cs:94 - `FormatCurrency` method is defined but never called. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | SampleBankingApp/Services/TransactionService.cs:77 - `IsWithinDailyLimit` method is defined but never called. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | SampleBankingApp/Helpers/StringHelper.cs:54 - `ObfuscateAccount` method is defined but never called. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | SampleBankingApp/Helpers/StringHelper.cs:59 - `ToTitleCase` method is defined but never called. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | SampleBankingApp/Helpers/StringHelper.cs:38 - `JoinWithSeparatorFixed` method is defined but never called. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | SampleBankingApp/Services/UserService.cs:10 - Shared mutable static state `_auditLog` accessed from multiple threads without synchronization. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | SampleBankingApp/Helpers/StringHelper.cs:16 - `new Regex(...)` inside `IsValidEmail` method called repeatedly. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs:31 - String concatenation inside a loop in `JoinWithSeparator` is O(n²). |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | SampleBankingApp/Services/EmailService.cs:16 - `SmtpClient` held as an instance field, which is not thread-safe and never disposed. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | SampleBankingApp/Helpers/StringHelper.cs:65 - `IsBlank` reimplements standard library method `string.IsNullOrWhiteSpace`. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | SampleBankingApp/Data/DatabaseHelper.cs:26 - `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. |

## Configuration Issues

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | SampleBankingApp/appsettings.json:3 - Production database connection string with credentials committed to source control. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | SampleBankingApp/appsettings.json:18 - Debug log levels set for production namespaces. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | SampleBankingApp/Program.cs:24 - JWT misconfiguration with `ValidateLifetime = false` allowing expired tokens. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | SampleBankingApp/Program.cs:36 - HTTPS redirection is commented out. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | SampleBankingApp/Program.cs:34 - `UseDeveloperExceptionPage()` called unconditionally in `Program.cs`. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | SampleBankingApp/Program.cs:38 - Open CORS policy allowing any origin, method, and header. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp/SampleBankingApp.csproj:8 - Debug symbols enabled in release builds via `<DebugSymbols>true</DebugSymbols>`. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | SampleBankingApp/SampleBankingApp.csproj:15 - Outdated or vulnerable NuGet package `Newtonsoft.Json 12.0.3`. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | SampleBankingApp/appsettings.json:1 - Missing environment-specific config overrides like `appsettings.Production.json`. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| UT | No test project exists in the solution. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results. | Found | SampleBankingApp | 1 - No test project exists in the solution. |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Found | `GenerateJwtToken` | **no** | **MIS-CREDIT** |
| E7 | Found | `rate limit` | yes | - |
| N3 | Found | `SmtpPort` | **no** | **MIS-CREDIT** |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Found | `TableExists` | yes | - |
| D4 | Found | `ExecuteQueryWithParams` | yes | - |
| D5 | Found | `BuildHtmlTemplate` | **no** | **MIS-CREDIT** |
| D6 | Found | `SendWelcomeEmailHtml` | yes | - |
| D7 | Found | `FormatCurrency` | yes | - |
| D8 | Found | `IsWithinDailyLimit` | yes | - |
| D9 | Found | `ObfuscateAccount` | yes | - |
| D10 | Found | `ToTitleCase` | yes | - |
| D11 | Found | `JoinWithSeparatorFixed` | yes | - |
| CF9 | Found | `appsettings.Production` | yes | - |

**Adjusted Found: 67 of 70** (70 reported, less 3 mis-credited).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `glm-5.2:cloud` |
| Reasoning strength (system prompt) | (model default) |
| Ollama `think` | (unset) |
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
| Grounding downgrades | `0` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 00111c5` |
