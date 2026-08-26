# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `72b5896`

> ⚠ **3 row(s) rated Found name a target that never appears in the review** (D5, L3, N4). Adjusted Found: **58** of 70. See the spot-check below.

Total: 61 Found / 7 Partial / 2 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | SampleBankingApp/Services/AuthService.cs | 32 | Login builds SQL with string interpolation enabling SQL injection | Use parameterized query |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | SampleBankingApp/Services/AuthService.cs | 53 | Admin bypass allows login with hardcoded credentials without DB check | Remove bypass logic |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 uses MD5 which is cryptographically broken | Use salted strong password hashing |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | SampleBankingApp/Services/UserService.cs | 47 | UPDATE statement built with string interpolation enabling SQL injection | Use parameterized query |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | SampleBankingApp/Services/UserService.cs | 99 | SearchUsers uses ExecuteQuery with interpolated LIKE enabling SQL injection | Use parameterized query |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | SampleBankingApp/Services/TransactionService.cs | 47 | UPDATE statement built with string interpolation enabling SQL injection | Use parameterized query |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | SampleBankingApp/Services/TransactionService.cs | 89 | RecordTransaction builds INSERT with interpolation enabling SQL injection | Use parameterized query |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | SampleBankingApp/appsettings.json | 3 | Connection string contains plaintext password committed to source | Store secrets in environment variables or secret manager |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime set to false allowing expired tokens | Set ValidateLifetime to true |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | SampleBankingApp/Controllers/UserController.cs | 43 | UpdateUser allows updating any user without ownership check | Restrict to own user or require admin role |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | SampleBankingApp/Controllers/UserController.cs | 57 | DeleteUser allows deleting any user without ownership check | Restrict to authorized users only |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | SampleBankingApp/Services/TransactionService.cs | 25 | Transfer allows amount zero | Reject amount <=0 |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | SampleBankingApp/Services/TransactionService.cs | 42 | Balance check compares fromBalance >= amount but deducts amount + fee | Check fromBalance >= totalDebit |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | SampleBankingApp/Services/UserService.cs | 72 | Pagination skip calculated as page * pageSize causing off-by-one | Use (page-1) * pageSize with page >=1 validation |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | SampleBankingApp/Services/TransactionService.cs | 68 | Interest bonus uses literal 0.05m | Define constant |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | SampleBankingApp/Services/TransactionService.cs | 23 | Missing self-transfer check | Reject when fromUserId == toUserId |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | SampleBankingApp/Services/UserService.cs | 20 | Validation duplicated across methods | Extract shared validation method |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs | 32 | result += item + separator in loop O(n²) | Use StringBuilder or string.Join |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | SampleBankingApp/Services/AuthService.cs | 28 | Login does hashing query mapping bypass multiple responsibilities | Split into smaller methods |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | SampleBankingApp/Services/UserService.cs | 105 | Catch Exception returns empty list silently hiding errors | Log error and propagate or return error status |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | SampleBankingApp/Services/EmailService.cs | 75 | Catch Exception swallows welcome email failure silently | Log error and consider retry |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | SampleBankingApp/Services/TransactionService.cs | 23 | Transfer performs two UPDATEs without transaction risking partial update | Wrap in database transaction |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | SampleBankingApp/Services/TransactionService.cs | 52 | Email sent after DB updates committed risking inconsistency | Send email within transaction or use outbox pattern |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | SampleBankingApp/Controllers/UserController.cs | 52 | Returns raw exception message to client leaking information | Return generic error message and log details |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | SampleBankingApp/Data/DatabaseHelper.cs | 52 | ExecuteNonQuery uses GetOpenConnection and closes but not dispose | Use using |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed | _(ungrounded: no matching sentence in review)_ |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection opened but never closed or disposed | Use using for connection and reader |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | SampleBankingApp/Data/DatabaseHelper.cs | 19 | GetOpenConnection returns open SqlConnection without disposal contract | Document ownership or use using |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | SampleBankingApp/Data/DatabaseHelper.cs | 52 | ExecuteNonQuery uses GetOpenConnection and closes but not dispose | Use using |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | SampleBankingApp/Services/EmailService.cs | 22 | SmtpClient stored as instance field is not thread safe and never disposed | Create and dispose per use or manage lifecycle properly |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | SampleBankingApp/Services/EmailService.cs | 39 | MailMessage created without using | Use using for MailMessage |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | SampleBankingApp/Program.cs | 16 | jwtSecret read from config may be null | Validate config and fail fast |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | SampleBankingApp/Services/TransactionService.cs | 36 | Accesses fromUserTable.Rows[0] without verifying Rows.Count | Check count before access |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | SampleBankingApp/Services/EmailService.cs | 26 | _config["Email:Username"] may be null | Validate config |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | SampleBankingApp/Services/EmailService.cs | 69 | MailMessage created without using | Use using for MailMessage |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | SampleBankingApp/Helpers/StringHelper.cs | 13 | IsValidEmail accesses email.Length without null check | Guard against null |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | SampleBankingApp/Controllers/TransactionController.cs | 27 | int.Parse(userIdClaim!) throws if claim missing | Validate claim presence and return Unauthorized |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | SampleBankingApp/Controllers/UserController.cs | 24 | GetUser returns any user by id without ownership check | Verify current user can access requested id |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Partial | SampleBankingApp/Services/TransactionService.cs | 68 | Interest bonus uses literal 0.05m | Define constant |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | SampleBankingApp/Services/TransactionService.cs | 65 | Deposit cap literal 1000000 | Define constant |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | SampleBankingApp/Services/EmailService.cs | 10 | TransferSubject literal | Use config |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | SampleBankingApp/Helpers/StringHelper.cs | 45 | MaskAccountNumber accesses accountNumber.Length without null check | Guard against null |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | SampleBankingApp/Services/UserService.cs | 70 | Page size cap literal 50 | Define constant |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 defined but never called | Remove |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | SampleBankingApp/Services/AuthService.cs | 105 | Code after unconditional return is unreachable | Remove unreachable code |
| D3 | `TableExists` — never called from any service or controller. | Found | SampleBankingApp/Data/DatabaseHelper.cs | 59 | TableExists defined but never called | Remove |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | SampleBankingApp/Data/DatabaseHelper.cs | 68 | ExecuteQueryWithParams marked Obsolete and unused | Remove or use |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml defined but never called | Remove |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml defined but never called | Remove |
| D7 | `FormatCurrency` — private, never called. | Found | SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency defined but never called | Remove |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit defined but never called | Remove or use |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount defined but never called | Remove |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase defined but never called | Remove |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | SampleBankingApp/Helpers/StringHelper.cs | 38 | JoinWithSeparatorFixed defined but never called | Remove |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | SampleBankingApp/Services/UserService.cs | 10 | static List _auditLog shared mutable without synchronization | Use thread-safe collection |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | SampleBankingApp/Helpers/StringHelper.cs | 16 | new Regex created each call | Make static readonly |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs | 32 | result += item + separator in loop O(n²) | Use StringBuilder or string.Join |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | SampleBankingApp/Services/EmailService.cs | 22 | SmtpClient stored as instance field is not thread safe and never disposed | Create and dispose per use or manage lifecycle properly |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank defined but never called | Remove |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | SampleBankingApp/Data/DatabaseHelper.cs | 19 | GetOpenConnection leaks resource ownership | Return connection via using |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | SampleBankingApp/appsettings.json | 3 | Connection string contains plaintext password committed to source | Store secrets in environment variables or secret manager |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | SampleBankingApp/appsettings.json | 18 | LogLevel Default Debug for production | Set to Warning or Error |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime set to false allowing expired tokens | Set ValidateLifetime to true |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out allowing HTTP traffic | Enable HTTPS redirection |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | SampleBankingApp/Program.cs | 34 | UseDeveloperExceptionPage called unconditionally exposing stack traces | Enable only in Development environment |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | SampleBankingApp/Program.cs | 38 | CORS policy allows any origin method and header | Restrict origins to trusted domains |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp/SampleBankingApp.csproj | 8 | DebugSymbols true in release build | Disable for release |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | SampleBankingApp/SampleBankingApp.csproj | 13 | Newtonsoft.Json 12.0.3 outdated | Update to supported version |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Missed | _(ungrounded: no matching sentence in review)_ |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results. | Found | SampleBankingApp/Services/AuthService.cs | 28 | No unit tests for Login authentication and admin bypass | Add tests for valid/invalid credentials and bypass removal |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Partial | `GenerateJwtToken` | **no** | **UNSUPPORTED** |
| E7 | Missed | `rate limit` | **no** | - |
| N3 | Partial | `SmtpPort` | **no** | **UNSUPPORTED** |
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
| CF9 | Missed | `appsettings.Production` | **no** | - |
| UT | Found | `Tests.csproj` | yes | - |
| C2 | Found | `SuperAdmin2024` | yes | - |
| C3 | Found | `MD5` | yes | - |
| C9 | Found | `ValidateLifetime` | yes | - |
| L3 | Found | `GetUsersPage` | **no** | **MIS-CREDIT** |
| L4 | Partial | `0.05` | yes | under-credited? |
| E1 | Found | `SearchUsers` | yes | - |
| E5 | Found | `ex.Message` | yes | - |
| RL4 | Found | `SmtpClient` | yes | - |
| RL5 | Found | `MailMessage` | yes | - |
| N2 | Found | `Rows[0]` | yes | - |
| N4 | Found | `ToUpper` | **no** | **MIS-CREDIT** |
| M1 | Partial | `TransactionFeeRate` | **no** | **UNSUPPORTED** |
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

**Adjusted Found: 58 of 70** (61 reported, less 3 mis-credited).

> **3 row(s) rated `Partial` whose target string appears NOWHERE in the review** (R3, N3, M1). A Partial on an unmentioned issue is a Missed; the reported Missed count is correspondingly understated.

> **1 row(s) rated `Partial`/`Missed` whose target string IS present in the review** (L4). The score is left as the scorer rated it; read these rows before trusting the Missed count.

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Muse-Glimmer-30B-imatrix:Q4_K_S` |
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
| Grounding downgrades | `2` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 72b5896` |
