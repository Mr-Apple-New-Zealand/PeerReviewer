# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `9109360`

> ⚠ **1 row(s) rated Found name a target that never appears in the review** (N3). Adjusted Found: **69** of 70. See the spot-check below.

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | The review identifies that `Login` builds the authentication query by interpolating `username` and `hashedPassword`, allowing trivial auth bypass such as `' OR '1'='1'--`. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | The review identifies the hardcoded backdoor password constant `AdminBypassPassword = "SuperAdmin2024"` in source. |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | The review identifies that `Login` contains a backdoor that returns a `SuperAdmin` user (Id=0) for username "admin" with the hardcoded password. |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | The review identifies that `UpdateUser` interpolates `email` and `username` into an UPDATE — SQL injection. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | The review identifies that `SearchUsers` interpolates user input into a `LIKE` clause via `ExecuteQuery` — SQL injection. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | The review identifies that `Transfer` interpolates balances and ids into UPDATE statements (unsafe pattern, culture-sensitive). |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | The review identifies that `RecordTransaction` interpolates user-controlled `description` into an INSERT — SQL injection via `TransferRequest.Description`. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | The review identifies that production SQL credentials (`sa` / `Admin1234!`) committed to source control. |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | The review identifies that JWT lifetime is 30 days, and with lifetime validation disabled tokens never effectively expire. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | The review identifies that `GetUser` lets any authenticated user read any user's profile and balance — no ownership check. |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | The review identifies that `DeleteUser` has no ownership/role check — any authenticated user can delete any account. |

## Logic Errors

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | The review identifies that `Transfer` validates `amount < 0`, so zero-amount transfers are accepted, recorded, and emailed. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | The review identifies that balance check `fromBalance >= amount` ignores the fee, so deducting `amount + fee` can drive the balance negative. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | The review identifies that `GetUsersPage` computes `skip = page * pageSize`, so page 1 skips the first `pageSize` rows (off-by-one). |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | The review identifies that `Deposit` applies a 5% `interestBonus` on every deposit (likely intended 1%), handing out free money per deposit. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | The review identifies that `Transfer` has no self-transfer check; when `fromUserId == toUserId` the second UPDATE uses the stale `toBalance` and the balance increases by `amount`, creating money. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | The review identifies that `GetUserById` duplicates the id-validation block. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | The review identifies that `JoinWithSeparator` appends the separator after every item, leaving a trailing separator. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | The review identifies that `Login` carries hashing, SQL access, entity mapping, and backdoor logic and should be split into `VerifyCredentials` and `MapUser`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | The review identifies that `SearchUsers` catches all exceptions and returns an empty list, so callers cannot distinguish an error from no matches. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | The review identifies that `SendWelcomeEmail` swallows all exceptions with `Console.WriteLine`. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | The review identifies that `Transfer` performs two UPDATEs plus an INSERT with no database transaction, so a mid-way failure loses money. |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | The review identifies that `Transfer` sends the notification email after the DB writes with no try/catch, so an SMTP failure surfaces as a 500 even though the transfer committed. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | The review identifies that `UpdateUser` returns raw `ex.Message` in the 500 response. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | The review identifies that `ExecuteNonQuery` skips `connection.Close()` when `ExecuteNonQuery` throws. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | The review identifies that Login endpoint has no rate limiting or account lockout, enabling credential brute force. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | The review identifies that the `SqlConnection` in `Login` is opened but never closed or disposed on any path, including the success return. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | The review identifies that `ExecuteQuery` never closes or disposes the connection obtained from `GetOpenConnection`. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | The review identifies that `ExecuteNonQuery` closes but never disposes the connection, and the exception path skips `Close` entirely. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | The review identifies that `SmtpClient` is held as an instance field, is not thread-safe, and is never disposed. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | The review identifies that the `MailMessage` in `SendTransferNotification` is never disposed. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | The review identifies that `jwtSecret` is read from config and null-forgiven into `Encoding.UTF8.GetBytes`, so a missing key crashes startup with `ArgumentNullException`. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | The review identifies that `Transfer` reads `Rows[0]` without checking `Rows.Count`, throwing `IndexOutOfRangeException` when either user id does not exist. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | The review identifies that `_config["Email:SmtpHost"]` may be null, leaving `SmtpClient` without a host and failing at send time. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | The review identifies that `username.ToUpper()` is called before any null check. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | The review identifies that `IsValidEmail` dereferences `email.Length` with no null guard. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | The review identifies that `int.Parse(userIdClaim!)` throws when the `NameIdentifier` claim is missing or non-numeric. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | The review identifies that `Login` uses `request` without a null check; a JSON `null` body yields a `NullReferenceException`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | The review identifies that interest rate `0.05m` is an inline literal. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | The review identifies that deposit cap `1000000` is an inline literal. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | The review identifies that sender `"notifications@company.com"` literal in `SendTransferNotification`. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | The review identifies that email max length `254` literal. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | The review identifies that page-size cap `50` is an inline literal. |

## Dead Code

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | The review identifies that `HashPasswordSha1` has no callers. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | The review identifies that code after the unconditional `return true;` in `ValidateToken` is unreachable. |
| D3 | `TableExists` — never called from any service or controller. | Found | The review identifies that `TableExists` has no callers in any file. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | The review identifies that `ExecuteQueryWithParams` is marked `[Obsolete]` and has no callers. |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | The review identifies that `BuildHtmlTemplate`'s only caller is the unused `SendWelcomeEmailHtml`, making it transitively dead. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | The review identifies that `SendWelcomeEmailHtml` has no callers. |
| D7 | `FormatCurrency` — private, never called. | Found | The review identifies that `FormatCurrency` has no callers. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | The review identifies that `IsWithinDailyLimit` has no callers; the daily limit is never enforced. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | The review identifies that `ObfuscateAccount` has no callers and duplicates `MaskAccountNumber`. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | The review identifies that `ToTitleCase` has no callers. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | The review identifies that `JoinWithSeparatorFixed` has no callers. |

## Anti-patterns

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | The review identifies that mutable static `List<string> _auditLog` is shared across threads with no synchronization. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | The review identifies that `IsValidEmail` creates a `new Regex` on every call. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | The review identifies that `JoinWithSeparator` concatenates strings in a loop (O(n²)). |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | The review identifies that `SmtpClient` is held as an instance field, is not thread-safe, and is never disposed. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | The review identifies that `IsBlank` reimplements `string.IsNullOrWhiteSpace`. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | The review identifies that `GetOpenConnection` is a helper designed to leak resource ownership to callers with no documented contract. |

## Configuration Issues

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | The review identifies that production SQL credentials (`sa` / `Admin1234!`) committed to source control. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | The review identifies that `Debug` log level set for `Default`, `Microsoft`, and `System` in the base config used by production. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | The review identifies that JWT lifetime is 30 days, and with lifetime validation disabled tokens never effectively expire. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | The review identifies that HTTPS redirection is commented out. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | The review identifies that `UseDeveloperExceptionPage()` is called unconditionally. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | The review identifies that CORS allows any origin, any method, any header. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | The review identifies that `DebugSymbols=true` and `DebugType=full` ship full debug symbols in release builds. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | The review identifies that Newtonsoft.Json 12.0.3 has a known DoS vulnerability (fixed in 13.0.1) and is not referenced by any source file. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | The review identifies that no `appsettings.Production.json` or other environment-specific overrides exist. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| UT | No test project exists in the repository. The most critical methods and scenarios to cover: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results. | Found | The review identifies that no test project exists in the repository. The most critical methods and scenarios to cover include `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, and controller action results.
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Found | `GenerateJwtToken` | yes | - |
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

**Adjusted Found: 69 of 70** (70 reported, less 1 mis-credited).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `kimi-k3:cloud` |
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
| Review citations past end of file | `0 of 312` |
| Precision (checkable Found rows) | `98% (39 of 40)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 9109360` |
