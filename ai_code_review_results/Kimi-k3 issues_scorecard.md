# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `00111c5`

> **70 Found, zero Partial.** The spot-check below found no mis-credited watchlist rows, but a zero-Partial sheet is worth a second look.

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | `Services/AuthService.cs` ~35 **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | AuthService.cs line 32: `Login` interpolates `username` and `hashedPassword` into SQL, allowing auth bypass via `' OR '1'='1`. |
| C2 | `Services/AuthService.cs` ~49 **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | AuthService.cs line 17: Hardcoded backdoor credential `AdminBypassPassword = "SuperAdmin2024"` is committed to source. |
| C3 | `Services/AuthService.cs` ~56 **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | AuthService.cs line 30, 61-66: `HashPasswordMd5` uses unsalted MD5 for password verification. |
| C4 | `Services/UserService.cs` ~45, 60 **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | UserService.cs line 47: `UpdateUser` interpolates `email` and `username` into an UPDATE statement. |
| C5 | `Services/UserService.cs` ~88 **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | UserService.cs line 99: `SearchUsers` interpolates `query` into a LIKE clause. |
| C6 | `Services/TransactionService.cs` ~50, 53 **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | TransactionService.cs line 47: Sender balance UPDATE is built by interpolation. |
| C7 | `Services/TransactionService.cs` ~82 **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | TransactionService.cs line 89-90: `RecordTransaction` interpolates `description` (user-controlled) into an INSERT. |
| C8 | `appsettings.json` all **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | appsettings.json line 3: Production SQL `sa` password `Admin1234!` is committed to source control. |
| C9 | `Program.cs` ~30 **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Program.cs line 24: `ValidateLifetime = false` means expired JWTs are accepted. |
| C10 | `Controllers/UserController.cs` ~53 **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | UserController.cs line 22: `GetUser` has no ownership or role check, so any authenticated user can read any account (IDOR). |
| C11 | `Controllers/UserController.cs` ~67 **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | UserController.cs line 57: `DeleteUser` lets any authenticated user delete any account. |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `Services/TransactionService.cs` ~25 `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | TransactionService.cs line 25: `amount < 0` permits zero-amount transfers (fee churn, spam notifications). |
| L2 | `Services/TransactionService.cs` ~43 **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | TransactionService.cs line 42: Balance check `fromBalance >= amount` ignores the fee, but `amount + fee` is debited, allowing a negative balance. |
| L3 | `Services/UserService.cs` ~73 **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | UserService.cs line 72: `skip = page * pageSize` is off by one — page 1 skips the first `pageSize` rows. |
| L4 | `Services/TransactionService.cs` ~60 **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | TransactionService.cs line 68: `Deposit` adds a 5% bonus (`amount * 0.05m * 1`) on every deposit — almost certainly the wrong rate and freely abusable. |
| L5 | `Controllers/TransactionController.cs` ~26 **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | TransactionService.cs line 42-48: No self-transfer check: when `fromUserId == toUserId` the second UPDATE overwrites with `toBalance + amount`, creating money from nothing. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | `Services/UserService.cs` ~20, 38, 54 **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | UserService.cs line 20-23: The `id <= 0` / `id > 1000000` validation block is duplicated in `GetUserById`. |
| R2 | `Helpers/StringHelper.cs` ~28 **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | StringHelper.cs line 31-35: `JoinWithSeparator` concatenates strings in a loop (O(n²)) and reimplements `string.Join` incorrectly. |
| R3 | `Services/AuthService.cs` ~71 **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | AuthService.cs line 84: `GenerateJwtToken` issues tokens valid for 30 days. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `Services/UserService.cs` ~83 `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | UserService.cs line 105-108: `SearchUsers` catches broad `Exception` and returns an empty list, so callers cannot distinguish errors from no results. |
| E2 | `Services/EmailService.cs` ~63 `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | EmailService.cs line 75-78: `SendWelcomeEmail` swallows all exceptions with only `Console.WriteLine`. |
| E3 | `Services/TransactionService.cs` ~55 **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | TransactionService.cs line 47-50: `Transfer` performs two UPDATEs plus an INSERT with no transaction, so a mid-failure loses money. |
| E4 | `Services/TransactionService.cs` ~59 Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | TransactionService.cs line 52-55: The notification email is sent after the DB writes commit, and a rethrown `SmtpException` surfaces as a 500 even though the transfer succeeded. |
| E5 | `Controllers/UserController.cs` ~58 `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | UserController.cs line 52: 500 response returns raw `ex.Message` to the client. |
| E6 | `Data/DatabaseHelper.cs` ~44 `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | DatabaseHelper.cs line 52-55: `ExecuteNonQuery` skips `connection.Close()` whenever `ExecuteNonQuery` throws. |
| E7 | `Controllers/AuthController.cs` ~20 No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | AuthController.cs line 34-38: Login endpoint has no rate limiting or account lockout, enabling brute force. |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `Services/AuthService.cs` ~37–38 `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | AuthService.cs line 34-35: `Login` opens a `SqlConnection` that is never closed or disposed on any path. |
| RL2 | `Data/DatabaseHelper.cs` ~26 `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | DatabaseHelper.cs line 19-24: `GetOpenConnection` hands an open connection to callers with no ownership contract, and every caller leaks it. |
| RL3 | `Data/DatabaseHelper.cs` ~44 `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | DatabaseHelper.cs line 52-55: `ExecuteNonQuery` skips `connection.Close()` whenever `ExecuteNonQuery` throws. |
| RL4 | `Services/EmailService.cs` ~36 `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | EmailService.cs line 16: `SmtpClient` is held as an instance field — it is not thread-safe and its socket is never released. |
| RL5 | `Services/EmailService.cs` ~49, 72 `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | EmailService.cs line 39-43: `MailMessage` in `SendTransferNotification` is never disposed. |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `Services/AuthService.cs` ~72 `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Program.cs line 16, 28: `jwtSecret` may be null, and `Encoding.UTF8.GetBytes(jwtSecret!)` then throws at startup. |
| N2 | `Services/TransactionService.cs` ~35–36 `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | TransactionService.cs line 36: `fromUserTable.Rows[0]` is accessed without checking `Rows.Count`, throwing `IndexOutOfRangeException` for an unknown sender. |
| N3 | `Services/EmailService.cs` ~46 `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | EmailService.cs line 24: `int.Parse` on `Email:SmtpPort` throws `FormatException` if the value is non-numeric. |
| N4 | `Services/EmailService.cs` ~68 `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | EmailService.cs line 65: `username.ToUpper()` is called before any null check. |
| N5 | `Helpers/StringHelper.cs` ~14, 24 `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | StringHelper.cs line 13: `email.Length` is read before any null check. |
| N6 | `Controllers/TransactionController.cs` ~19, 31 `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | TransactionController.cs line 26-27: `User.FindFirst(...)?.Value` can be null, and `int.Parse(userIdClaim!)` then throws. |
| N7 | `Controllers/UserController.cs` ~28 `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | UserController.cs line 43: `request.Email`/`request.Username` can be null from JSON. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `Services/TransactionService.cs` ~13–14 `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | TransactionService.cs line 68: Interest rate `0.05m` (and the no-op `* 1`) is an inline literal. |
| M2 | `Services/TransactionService.cs` ~60 `1_000_000` deposit cap hardcoded inline — no named constant. | Found | TransactionService.cs line 65: Deposit cap `1000000` is an inline literal. |
| M3 | `Services/EmailService.cs` ~14–15, 49, 72 Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | EmailService.cs line 40: Sender address `notifications@company.com` hardcoded in `SendTransferNotification`. |
| M4 | `Helpers/StringHelper.cs` ~14, 24 `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | StringHelper.cs line 13: Email length limit `254` is an inline literal. |
| M5 | `Services/UserService.cs` ~69 `50` as the page size upper bound is unnamed and undocumented. | Found | UserService.cs line 70: Max page size `50` is an inline literal. |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `Services/AuthService.cs` ~80 `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | AuthService.cs line 91-96: `HashPasswordSha1` has no callers. |
| D2 | `Services/AuthService.cs` ~87–92 Unreachable code after `return true` in `ValidateToken`. | Found | AuthService.cs line 105-107: Code after the unconditional `return true;` in `ValidateToken` is unreachable. |
| D3 | `Data/DatabaseHelper.cs` ~49 `TableExists` — never called from any service or controller. | Found | DatabaseHelper.cs line 59-65: `TableExists` has no callers anywhere in the source. |
| D4 | `Data/DatabaseHelper.cs` ~56 `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | DatabaseHelper.cs line 67-78: `ExecuteQueryWithParams` is `[Obsolete]` and has no callers. |
| D5 | `Services/EmailService.cs` ~79 `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | EmailService.cs line 81-84: `BuildHtmlTemplate` is only called by the dead `SendWelcomeEmailHtml`, making it transitively dead. |
| D6 | `Services/EmailService.cs` ~85 `SendWelcomeEmailHtml` — public method, never registered or called. | Found | EmailService.cs line 86-92: `SendWelcomeEmailHtml` has no callers. |
| D7 | `Services/TransactionService.cs` ~91 `FormatCurrency` — private, never called. | Found | TransactionService.cs line 94-97: `FormatCurrency` has no callers. |
| D8 | `Services/TransactionService.cs` ~72 `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | TransactionService.cs line 77-85: `IsWithinDailyLimit` has no callers, so the daily limit is never enforced. |
| D9 | `Helpers/StringHelper.cs` ~49 `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | StringHelper.cs line 54-57: `ObfuscateAccount` has no callers and duplicates `MaskAccountNumber`. |
| D10 | `Helpers/StringHelper.cs` ~54 `ToTitleCase` — "experimental utility never integrated", never called. | Found | StringHelper.cs line 59-63: `ToTitleCase` has no callers. |
| D11 | `Helpers/StringHelper.cs` ~37 `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | StringHelper.cs line 38-41: `JoinWithSeparatorFixed` has no callers. |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | `Services/UserService.cs` ~15–16 **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | UserService.cs line 10: `_auditLog` is shared mutable static state (a `List<string>`) mutated from requests with no synchronization and unbounded growth. |
| A2 | `Helpers/StringHelper.cs` ~14, 24 **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | StringHelper.cs line 16: `new Regex(...)` is constructed on every `IsValidEmail` call. |
| A3 | `Helpers/StringHelper.cs` ~29 **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | StringHelper.cs line 31-35: `JoinWithSeparator` concatenates strings in a loop (O(n²)) and reimplements `string.Join` incorrectly. |
| A4 | `Services/EmailService.cs` ~34 **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | EmailService.cs line 16: `SmtpClient` is held as an instance field — it is not thread-safe and its socket is never released. |
| A5 | `Helpers/StringHelper.cs` ~60 **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | StringHelper.cs line 65-71: `IsBlank` reimplements `string.IsNullOrWhiteSpace`. |
| A6 | `Data/DatabaseHelper.cs` ~26 **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | DatabaseHelper.cs line 19-24: `GetOpenConnection` is a helper designed to leak resource ownership to callers with no documented contract. |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | `appsettings.json` all **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | appsettings.json line 3: Production SQL `sa` password `Admin1234!` is committed to source control. |
| CF2 | `appsettings.json` ~16–20 **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | appsettings.json line 18-20: `Debug` log level is set for `Default`, `Microsoft`, and `System` in what is effectively production config. |
| CF3 | `Program.cs` ~29 **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Program.cs line 24: `ValidateLifetime = false` means expired JWTs are accepted. |
| CF4 | `Program.cs` ~33 **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Program.cs line 36: `app.UseHttpsRedirection()` is commented out. |
| CF5 | `Program.cs` ~26 **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Program.cs line 34: `UseDeveloperExceptionPage()` is called unconditionally. |
| CF6 | `Program.cs` ~37 **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Program.cs line 38: Overly permissive CORS (`AllowAnyOrigin` + `AllowAnyMethod` + `AllowAnyHeader`). |
| CF7 | `SampleBankingApp.csproj` ~7–10 **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp.csproj line 8-9: `DebugSymbols`/`DebugType full` ship full debug symbols in release builds. |
| CF8 | `SampleBankingApp.csproj` ~14 **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | SampleBankingApp.csproj line 15: `Newtonsoft.Json` 12.0.3 is outdated and affected by a known DoS advisory fixed in 13.0.1, and nothing in the source uses it. |
| CF9 | `(project root)` **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Repository: No `appsettings.Production.json` or other environment-specific override files exist. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `TransactionService.Transfer`, `UserService.GetUsersPage`, etc. | Found | No test project exists in the repository; the following are the most critical methods and scenarios to cover. |
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
| Review model | `kimi-k3:cloud` |
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
