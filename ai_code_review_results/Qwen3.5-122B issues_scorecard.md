# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22`

> ⚠ **3 row(s) rated Found name a target that never appears in the review** (CF9, N2, N4). Adjusted Found: **66** of 70. See the spot-check below.

Total: 69 Found / 0 Partial / 1 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | SampleBankingApp/Services/AuthService.cs line 32: "SQL Injection vulnerability in `Login` via string interpolation of `username` and `hashedPassword`." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | SampleBankingApp/Services/AuthService.cs line 17: "Hardcoded backdoor password "SuperAdmin2024" in `AdminBypassPassword` constant." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | SampleBankingApp/Services/AuthService.cs line 63: "Weak cryptography used in `HashPasswordMd5` (MD5 is broken for passwords)." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | SampleBankingApp/Services/UserService.cs line 47: "SQL Injection vulnerability in `UpdateUser` via string interpolation of `email`, `username`, and `id`." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | SampleBankingApp/Services/UserService.cs line 99: "SQL Injection vulnerability in `SearchUsers` via string interpolation of `query` in LIKE clause." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | SampleBankingApp/Services/TransactionService.cs line 47: "SQL Injection vulnerability in `Transfer` via string interpolation of `newFromBalance` and `fromUserId`." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | SampleBankingApp/Services/TransactionService.cs line 90: "SQL Injection vulnerability in `RecordTransaction` via string interpolation of `fromId`, `toId`, `amount`, `type`, `description`." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | SampleBankingApp/appsettings.json line 3: "Hardcoded database password "Admin1234!" in connection string." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | SampleBankingApp/Program.cs line 24: "JWT token validation disabled (`ValidateLifetime = false`). |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | SampleBankingApp/Controllers/UserController.cs line 39: "Missing ownership check in `UpdateUser` allows any user to modify any other user's data." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | SampleBankingApp/Controllers/UserController.cs line 57: "Missing ownership check in `DeleteUser` allows any user to delete any other user." |

## Logic Errors

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | SampleBankingApp/Services/TransactionService.cs line 23: "Missing self-referential check in `Transfer` allows transferring funds to oneself." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | SampleBankingApp/Services/TransactionService.cs line 42: "Balance check `fromBalance >= amount` allows negative balance after deducting `amount + fee`." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | SampleBankingApp/Services/UserService.cs line 72: "Off-by-one error in pagination calculation `page * pageSize` instead of `(page - 1) * pageSize`." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | SampleBankingApp/Services/TransactionService.cs line 68: "Hardcoded interest calculation `amount * 0.05m * 1` in `Deposit` uses magic number 1." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | SampleBankingApp/Services/TransactionService.cs line 23: "Missing self-referential check in `Transfer` allows transferring funds to oneself." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | SampleBankingApp/Services/UserService.cs line 22: "Hardcoded ID range check `id > 1000000` in `GetUserById`." |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs line 31: "`JoinWithSeparator` uses string concatenation in loop causing O(n²) performance." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | SampleBankingApp/Services/AuthService.cs line 84: "Hardcoded JWT expiry `AddDays(30)` without configuration." |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | SampleBankingApp/Services/UserService.cs line 105: "`SearchUsers` catches broad `Exception` and returns empty list, hiding errors from callers." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | SampleBankingApp/Services/EmailService.cs line 75: "`SendWelcomeEmail` catches broad `Exception` and swallows it silently." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | SampleBankingApp/Services/TransactionService.cs line 47: "`Transfer` performs multiple DB writes without a transaction, risking data inconsistency." |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | SampleBankingApp/Services/TransactionService.cs line 52: "`Transfer` sends email after DB commit, risking state mismatch if email fails." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | SampleBankingApp/Controllers/UserController.cs line 52: "`UpdateUser` returns raw `ex.Message` to client, potentially leaking stack traces." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 52: "`ExecuteNonQuery` calls `GetOpenConnection` and `Close` manually, risking leak on exception." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | SampleBankingApp/Controllers/AuthController.cs line 20: "`Login` lacks rate limiting or account lockout mechanism." |

## Resource Leaks

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | SampleBankingApp/Services/AuthService.cs line 35: "`Login` opens `SqlConnection` manually without `using` block, risking leak on exception." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 23: "`GetOpenConnection` returns open connection without ensuring disposal by caller." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 52: "`ExecuteNonQuery` calls `GetOpenConnection` and `Close` manually, risking leak on exception." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | SampleBankingApp/Services/EmailService.cs line 16: "`_smtpClient` field is never disposed, leaking sockets." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | SampleBankingApp/Services/EmailService.cs line 39: "`SendTransferNotification` creates `MailMessage` without disposing it." |

## Missing Null Checks

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | SampleBankingApp/Services/AuthService.cs line 70: "`GenerateJwtToken` accesses `_config["Jwt:SecretKey"]!` assuming non-null." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | SampleBankingApp/Services/TransactionService.cs line 35: "`Login` casts `reader["Username"]` to `string` without checking for null DB value." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | SampleBankingApp/Services/EmailService.cs line 24: "`EmailService` constructor parses `_config["Email:SmtpPort"]` without null check." |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | SampleBankingApp/Services/EmailService.cs line 69: "`SendWelcomeEmail` creates `MailMessage` without disposing it." |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | SampleBankingApp/Helpers/StringHelper.cs line 13: "`IsValidEmail` accesses `email.Length` without null check on parameter." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | SampleBankingApp/Controllers/TransactionController.cs line 27: "`Transfer` uses `userIdClaim!` which may be null if claim is missing." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | SampleBankingApp/Controllers/UserController.cs line 39: "Missing ownership check in `UpdateUser` allows any user to modify any other user's data." |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | SampleBankingApp/Services/TransactionService.cs line 11: "Magic number `0.015m` used for transaction fee rate." |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | SampleBankingApp/Services/UserService.cs line 22: "Hardcoded ID range check `id > 1000000` in `GetUserById`." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | SampleBankingApp/Services/EmailService.cs line 40: "Magic string `"notifications@company.com"` used as sender email." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | SampleBankingApp/Helpers/StringHelper.cs line 14: "Magic number `3` used for max retries." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | SampleBankingApp/Services/UserService.cs line 70: "Magic number `50` used for max page size." |

## Dead Code

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | SampleBankingApp/Services/AuthService.cs line 91: "`HashPasswordSha1` method is defined but never called." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | SampleBankingApp/Services/AuthService.cs line 105: "`ValidateToken` contains unreachable code after unconditional `return true`." |
| D3 | `TableExists` — never called from any service or controller. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 59: "`TableExists` method is defined but never called." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 67: "`ExecuteQueryWithParams` method is marked `[Obsolete]` and never called." |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | SampleBankingApp/Services/EmailService.cs line 81: "`BuildHtmlTemplate` method is defined but never called." |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | SampleBankingApp/Services/EmailService.cs line 86: "`SendWelcomeEmailHtml` method is defined but never called." |
| D7 | `FormatCurrency` — private, never called. | Found | SampleBankingApp/Services/TransactionService.cs line 94: "`FormatCurrency` method is defined but never called." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | SampleBankingApp/Services/TransactionService.cs line 77: "`IsWithinDailyLimit` method is defined but never called." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | SampleBankingApp/Helpers/StringHelper.cs line 54: "`ObfuscateAccount` method is defined but never called." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | SampleBankingApp/Helpers/StringHelper.cs line 59: "`ToTitleCase` method is defined but never called." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | SampleBankingApp/Helpers/StringHelper.cs line 38: "`JoinWithSeparatorFixed` method is defined but never called." |

## Anti-patterns

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | SampleBankingApp/Services/UserService.cs line 10: "_auditLog is static mutable state accessed without synchronization." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | SampleBankingApp/Helpers/StringHelper.cs line 16: "`IsValidEmail` instantiates `Regex` inside method on every call." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs line 31: "`JoinWithSeparator` uses string concatenation in loop causing O(n²) performance." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | SampleBankingApp/Services/EmailService.cs line 16: "`_smtpClient` field is never disposed, leaking sockets." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | SampleBankingApp/Helpers/StringHelper.cs line 65: "`IsBlank` method is defined but never called." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 19: "`GetOpenConnection` leaks resource ownership to caller without documented contract." |

## Configuration Issues

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | SampleBankingApp/appsettings.json line 3: "Hardcoded database password "Admin1234!" in connection string." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | SampleBankingApp/appsettings.json line 18: "Logging level set to Debug for production." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | SampleBankingApp/Program.cs line 24: "JWT token validation disabled (`ValidateLifetime = false`). |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | SampleBankingApp/Program.cs line 36: "`UseHttpsRedirection()` is commented out." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | SampleBankingApp/Program.cs line 34: "`UseDeveloperExceptionPage()` is called unconditionally." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | SampleBankingApp/Program.cs line 38: "Overly permissive CORS policy (`AllowAnyOrigin` + `AllowAnyMethod`). |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp/SampleBankingApp.csproj line 8: "`DebugSymbols` is true in production build." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Missed | _(ungrounded: no matching sentence in review)_ |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | SampleBankingApp/appsettings.json line 23: "`AllowedHosts` set to wildcard `*`." |

## Missing Unit Tests

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| UT | No test project exists for the application. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results. | Found | SampleBankingApp | N/A: "No test project exists for the application." |
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
| N2 | Found | `Rows[0]` | **no** | **MIS-CREDIT** |
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
| CF8 | Missed | `Newtonsoft` | **no** | - |

**Adjusted Found: 66 of 70** (69 reported, less 3 mis-credited).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3.5-122B-imatrix:Q4_K_S` |
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
| Rows misaligned with ISSUES.md | `0` |
| Review citations past end of file | `0 of 141` |
| Precision (checkable Found rows) | `92% (36 of 39)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 67ece22` |
