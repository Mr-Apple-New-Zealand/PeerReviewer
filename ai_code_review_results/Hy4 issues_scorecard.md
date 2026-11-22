# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `e2bc209`

> **70 Found, zero Partial.** The spot-check below found no mis-credited watchlist rows, but a zero-Partial sheet is worth a second look.

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | SampleBankingApp/Services/AuthService.cs line 32: `Login` interpolates `username` and `hashedPassword` directly into the SQL `WHERE` clause. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | SampleBankingApp/Services/AuthService.cs line 17: `AdminBypassPassword` is a hardcoded backdoor credential. |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | SampleBankingApp/Services/AuthService.cs line 30: `Login` hashes passwords with unsalted MD5 via `HashPasswordMd5`. |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | SampleBankingApp/Services/UserService.cs line 47: `UpdateUser` interpolates `email`, `username`, and `id` into an `UPDATE` statement. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | SampleBankingApp/Services/UserService.cs line 99: `SearchUsers` interpolates `query` into `Username LIKE '%{query}%'` through `ExecuteQuery`. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | SampleBankingApp/Services/TransactionService.cs line 47: `Transfer` interpolates `newFromBalance` and `fromUserId` into an `UPDATE` statement. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | SampleBankingApp/Services/TransactionService.cs line 90: `RecordTransaction` interpolates `type` and `description` into an `INSERT` statement, enabling SQL injection through `description`. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | SampleBankingApp/appsettings.json line 3: Production connection string commits the SQL Server `sa` password `Admin1234!`. |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | SampleBankingApp/Program.cs line 24: JWT validation sets `ValidateLifetime = false`, so expired tokens are accepted. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | SampleBankingApp/Controllers/UserController.cs line 39: `UpdateUser` has no ownership check, so any authenticated user can update any other user by id. |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | SampleBankingApp/Controllers/UserController.cs line 57: `DeleteUser` has no ownership check, so any authenticated user can delete any other user by id. |

## Logic Errors

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | SampleBankingApp/Services/TransactionService.cs line 25: `Transfer` rejects `amount < 0` but allows `amount == 0`, producing a zero-value transfer and transaction record. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | SampleBankingApp/Services/TransactionService.cs line 42: `Transfer` checks `fromBalance >= amount` but debits `amount + fee`, which can create a negative balance. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | SampleBankingApp/Services/UserService.cs line 68: `GetUsersPage` computes `skip = page * pageSize`, so page 1 skips the first page of results. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | SampleBankingApp/Services/TransactionService.cs line 68: `Deposit` applies a hardcoded `0.05m * 1` interest bonus, effectively a 5% instant bonus on every deposit. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | SampleBankingApp/Services/TransactionService.cs line 23: `Transfer` does not reject `fromUserId == toUserId`, allowing a self-transfer that debits only the fee and credits the amount. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | SampleBankingApp/Services/UserService.cs line 18: `GetUserById` repeats the same id validation block used in `UpdateUser` and `DeleteUser`. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs line 29: `JoinWithSeparator` appends the separator after the final item, unlike `string.Join`. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | SampleBankingApp/Services/AuthService.cs line 68: `GenerateJwtToken` reads `Jwt:SecretKey` with `!` and uses the weak configured value. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | SampleBankingApp/Services/UserService.cs line 95: `SearchUsers` returns an empty list on any exception, so callers cannot distinguish no matches from a database failure. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | SampleBankingApp/Services/EmailService.cs line 63: `SendWelcomeEmail` catches broad `Exception` and silently writes to `Console`, swallowing delivery failures. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | SampleBankingApp/Services/TransactionService.cs line 47: `Transfer` performs two balance writes and a transaction insert without a database transaction. |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | SampleBankingApp/Services/TransactionService.cs line 52: `Transfer` sends email after the balance writes have committed, so an SMTP failure returns an error even though money moved. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | SampleBankingApp/Controllers/UserController.cs line 48: `UpdateUser` returns raw `ex.Message` from `ArgumentException` to the HTTP client. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 50: `ExecuteNonQuery` closes the connection only on the success path because `Close()` is after `ExecuteNonQuery()`. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | SampleBankingApp/Controllers/AuthController.cs line 22: `Login` has no rate limiting or account lockout handling for repeated failed authentication. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | SampleBankingApp/Services/AuthService.cs line 34: `Login` creates `SqlConnection` without a `using` block. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 28: `ExecuteQuery` obtains `connection` from `GetOpenConnection()` and never disposes it. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 52: `ExecuteNonQuery` obtains `connection` from `GetOpenConnection()` and skips `Close()` when `ExecuteNonQuery()` throws. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | SampleBankingApp/Services/EmailService.cs line 16: `EmailService` holds `SmtpClient` as an instance field, which is not thread-safe and keeps sockets alive. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | SampleBankingApp/Services/EmailService.cs line 39: `SendTransferNotification` creates `MailMessage` without disposing it. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | SampleBankingApp/Program.cs line 28: `Encoding.UTF8.GetBytes(jwtSecret!)` can receive null when `Jwt:SecretKey` is missing. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | SampleBankingApp/Services/TransactionService.cs line 36: `Transfer` accesses `fromUserTable.Rows[0]` without checking `Rows.Count > 0`. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | SampleBankingApp/Services/EmailService.cs line 24: `EmailService` passes `_config["Email:Username"]` and `_config["Email:Password"]` to `NetworkCredential`. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | SampleBankingApp/Services/EmailService.cs line 65: `SendWelcomeEmail` calls `username.ToUpper()` without checking for null. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | SampleBankingApp/Helpers/StringHelper.cs line 13: `IsValidEmail` calls `email.Length` before checking for null. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | SampleBankingApp/Controllers/TransactionController.cs line 27: `Transfer` passes `userIdClaim!` to `int.Parse`, which throws if the claim is missing. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | SampleBankingApp/Controllers/UserController.cs line 43: `UpdateUser` dereferences `request.Email` and `request.Username` without checking `request` for null. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | SampleBankingApp/Services/TransactionService.cs line 11: `TransactionFeeRate` hardcodes `0.015m` in source. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | SampleBankingApp/Services/TransactionService.cs line 65: `Deposit` hardcodes deposit cap `1000000`. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | SampleBankingApp/Services/EmailService.cs line 40: `SendTransferNotification` hardcodes `notifications@company.com` as the sender. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | SampleBankingApp/Helpers/StringHelper.cs line 13: `IsValidEmail` hardcodes the maximum email length `254`. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | SampleBankingApp/Services/UserService.cs line 70: `GetUsersPage` hardcodes maximum page size `50`. |

## Dead Code

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | SampleBankingApp/Services/AuthService.cs line 91: `HashPasswordSha1` appears only at its own definition and has no caller in the provided source. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | SampleBankingApp/Services/AuthService.cs line 103: `ValidateToken` has unreachable code after an unconditional `return true` on line 103. |
| D3 | `TableExists` — never called from any service or controller. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 59: `TableExists` appears only at its own definition and has no caller in the provided source. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 68: `ExecuteQueryWithParams` is marked `[Obsolete]` and appears only at its own definition. |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | SampleBankingApp/Services/EmailService.cs line 81: `BuildHtmlTemplate` is called by `SendWelcomeEmailHtml` line 88. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | SampleBankingApp/Services/EmailService.cs line 86: `SendWelcomeEmailHtml` appears only at its own definition and has no caller in the provided source. |
| D7 | `FormatCurrency` — private, never called. | Found | SampleBankingApp/Services/TransactionService.cs line 94: `FormatCurrency` appears only at its own definition and has no caller in the provided source. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | SampleBankingApp/Services/TransactionService.cs line 77: `IsWithinDailyLimit` appears only at its own definition and has no caller in the provided source. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | SampleBankingApp/Helpers/StringHelper.cs line 54: `ObfuscateAccount` appears only at its own definition and has no caller in the provided source. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | SampleBankingApp/Helpers/StringHelper.cs line 59: `ToTitleCase` appears only at its own definition and has no caller in the provided source. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | SampleBankingApp/Helpers/StringHelper.cs line 38: `JoinWithSeparatorFixed` appears only at its own definition and has no caller in the provided source. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | SampleBankingApp/Services/UserService.cs line 10: `_auditLog` is shared mutable static state accessed without synchronization. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | SampleBankingApp/Helpers/StringHelper.cs line 16: `IsValidEmail` constructs `new Regex(...)` inside a method that may be called repeatedly. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs line 29: `JoinWithSeparator` concatenates strings inside a loop, producing O(n²) behavior. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | SampleBankingApp/Services/EmailService.cs line 16: `EmailService` holds `SmtpClient` as an instance field, which is not thread-safe and keeps sockets alive. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | SampleBankingApp/Helpers/StringHelper.cs line 65: `IsBlank` reimplements `string.IsNullOrWhiteSpace`. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 19: `GetOpenConnection` returns an opened `SqlConnection` whose ownership is transferred to callers with no documented disposal contract. |

## Configuration Issues

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | SampleBankingApp/appsettings.json line 3: Production connection string commits the SQL Server `sa` password `Admin1234!`. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | SampleBankingApp/appsettings.json line 18: `Default` log level is `Debug`. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | SampleBankingApp/Program.cs line 24: JWT validation sets `ValidateLifetime = false`, so expired tokens are accepted. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | SampleBankingApp/Program.cs line 36: HTTPS redirection is commented out. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | SampleBankingApp/Program.cs line 34: `UseDeveloperExceptionPage()` is called unconditionally and can expose stack traces in production. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | SampleBankingApp/Program.cs line 38: CORS uses `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` for a banking API. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp/SampleBankingApp.csproj line 8: `DebugSymbols` is `true` for all builds. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | SampleBankingApp/SampleBankingApp.csproj line 15: `Newtonsoft.Json` `12.0.3` is outdated and has known vulnerability history. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | SampleBankingApp/appsettings.json line 1: No `appsettings.Production.json` or environment-specific override file is present. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, Controller action results — correct HTTP status codes for various service responses | Found | SampleBankingApp/SampleBankingApp.csproj line 1: No test project or test package references exist in the provided source. |
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
| Review model | `hy4:cloud` |
| Reasoning strength (system prompt) | (model default) |
| System prompt | `You are an expert computer programmer with an eye for detail, who loves to provide high quality answers.` |
| Ollama `think` | `False` |
| Temperature | `0.3` |
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
| Review citations past end of file | `0 of 290` |
| Precision (checkable Found rows) | `100% (40 of 40)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ e2bc209` |
