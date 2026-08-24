# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `53beb17`

> ⚠ **1 row(s) rated Found name a target that never appears in the review** (N3). Adjusted Found: **68** of 70. See the spot-check below.

Total: 69 Found / 0 Partial / 1 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | AuthService.cs line 32: "Login interpolates username and hashed password into a SQL query." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | AuthService.cs line 53: "Login contains a hardcoded admin bypass password." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | AuthService.cs line 30: "HashPasswordMd5 uses MD5 for password hashing." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | UserService.cs lines 47, 61: "UpdateUser interpolates email and username into SQL" and "DeleteUser interpolates the user id into SQL." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | UserService.cs line 99: "SearchUsers interpolates query into a LIKE clause." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | TransactionService.cs lines 47, 48: "The source balance UPDATE interpolates values into SQL" and "The destination balance UPDATE interpolates values into SQL." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | TransactionService.cs line 90: "RecordTransaction interpolates description and other values into SQL." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | appsettings.json lines 3, 6, 14: "The production database connection string contains a sa password", "The JWT secret key is weak and committed to source", "The SMTP password is committed to source." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Program.cs line 24: "ValidateLifetime is false so expired tokens are accepted." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | UserController.cs lines 43, 24: "UpdateUser allows any authenticated user to update any user" and "GetUser allows any authenticated user to read any user." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | UserController.cs line 61: "DeleteUser allows any authenticated user to delete any user." |

## Logic Errors

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | TransactionService.cs line 25: "Transfer allows zero amount because only negative values are rejected." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | TransactionService.cs line 42: "Transfer checks balance against amount but deducts amount plus fee." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | UserService.cs line 72: "GetUsersPage calculates skip as page times pageSize." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | TransactionService.cs line 68: "Deposit applies a 5 percent bonus with an unclear constant." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | TransactionService.cs line 23: "Transfer lacks a self-transfer check." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | UserService.cs lines 20, 38, 54: "GetUserById repeats the id validation block", "UpdateUser repeats the id validation block", "DeleteUser repeats the id validation block." |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | StringHelper.cs line 33: "JoinWithSeparator appends a trailing separator after every item." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | _(ungrounded: no matching sentence in review)_ |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | UserService.cs line 105: "SearchUsers catches Exception and returns an empty list." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | EmailService.cs line 75: "SendWelcomeEmail catches Exception and swallows it." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | TransactionService.cs line 47: "Transfer performs two balance updates and an insert without a transaction." |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | TransactionService.cs line 52: "Transfer sends email after database writes have completed." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | UserController.cs lines 50, 64: "UpdateUser catches broad Exception and returns ex.Message" and "DeleteUser catches broad Exception." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | DatabaseHelper.cs line 52: "ExecuteNonQuery closes the connection but does not dispose it." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | AuthController.cs line 20: "Login has no rate limiting or account lockout." |

## Resource Leaks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | AuthService.cs lines 34, 37, 38: "Login creates a SqlConnection without using", "Login creates a SqlCommand without using", "Login creates a SqlDataReader without using." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | DatabaseHelper.cs line 19: "GetOpenConnection returns an open connection with unclear ownership." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | DatabaseHelper.cs lines 52, 54: "ExecuteNonQuery closes the connection but does not dispose it" and "ExecuteNonQuery can leak the connection if the command throws before Close." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | EmailService.cs line 16: "SmtpClient is stored as an instance field and never disposed." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | EmailService.cs lines 39, 69: "SendTransferNotification creates a MailMessage without disposing it" and "SendWelcomeEmail creates a MailMessage without disposing it." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Program.cs line 28: "jwtSecret can be null if the configuration key is missing." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | TransactionService.cs lines 36, 37: "fromUserTable.Rows[0] is accessed without checking row count" and "toUserTable.Rows[0] is accessed without checking row count." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | EmailService.cs line 46: "SendTransferNotification retries only SmtpException failures." |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | EmailService.cs line 65: "SendWelcomeEmail calls username.ToUpper() without a null check." |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | StringHelper.cs lines 13, 22: "IsValidEmail calls email.Length before a null check" and "IsValidUsername calls username.Length before a null check." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | TransactionController.cs lines 27, 41: "userIdClaim can be null" and "userIdClaim can be null." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | UserController.cs line 43: "UpdateUser uses request without a null check." |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | TransactionService.cs lines 65, 68: "The deposit cap uses a hardcoded 1000000 value" and "The deposit bonus uses hardcoded 0.05m and 1 values." |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | TransactionService.cs line 65: "The deposit cap uses a hardcoded 1000000 value." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | EmailService.cs lines 40, 67, 69, 89: "The sender address notifications@company.com is hardcoded", "The support address support@company.com is hardcoded", "The sender address is hardcoded again" and "The sender address is hardcoded again." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | StringHelper.cs lines 13, 22: "IsValidEmail uses a hardcoded 254 length limit" and "IsValidUsername uses hardcoded 3 and 20 length limits." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | UserService.cs line 70: "GetUsersPage uses a hardcoded page size cap of 50." |

## Dead Code

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | AuthService.cs line 91: "HashPasswordSha1 uses weak SHA1 hashing." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | AuthService.cs line 105: "Code after the unconditional return in ValidateToken is unreachable." |
| D3 | `TableExists` — never called from any service or controller. | Found | DatabaseHelper.cs line 59: "TableExists has no caller in the provided source." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | DatabaseHelper.cs line 68: "ExecuteQueryWithParams is obsolete and has no caller." |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | EmailService.cs line 81: "BuildHtmlTemplate is only called by the unused SendWelcomeEmailHtml." |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | EmailService.cs line 86: "SendWelcomeEmailHtml has no caller in the provided source." |
| D7 | `FormatCurrency` — private, never called. | Found | TransactionService.cs line 94: "FormatCurrency has no caller in the provided source." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | TransactionService.cs line 77: "IsWithinDailyLimit has no caller in the provided source." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | StringHelper.cs line 54: "ObfuscateAccount has no caller in the provided source." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | StringHelper.cs line 59: "ToTitleCase has no caller in the provided source." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | StringHelper.cs line 38: "JoinWithSeparatorFixed has no caller in the provided source." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | UserService.cs lines 10, 11: "The static _auditLog list is shared mutable state without synchronization" and "The static _requestCount integer is shared mutable state without synchronization." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | StringHelper.cs lines 16, 25: "IsValidEmail creates a Regex on every call" and "IsValidUsername creates a Regex on every call." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | StringHelper.cs line 33: "JoinWithSeparator uses string concatenation inside a loop." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | EmailService.cs line 16: "The SmtpClient instance field is shared across requests." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | StringHelper.cs line 65: "IsBlank reimplements string.IsNullOrWhiteSpace." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | DatabaseHelper.cs line 19: "GetOpenConnection leaks resource ownership to callers." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | appsettings.json lines 3, 6, 14: "The production database connection string contains a sa password", "The JWT secret key is weak and committed to source", "The SMTP password is committed to source." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | appsettings.json lines 18, 19, 20: "The Default log level is Debug", "The Microsoft log level is Debug", "The System log level is Debug." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Program.cs line 24: "ValidateLifetime is false so expired tokens are accepted." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Program.cs line 36: "HTTPS redirection is commented out." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Program.cs line 34: "UseDeveloperExceptionPage is enabled unconditionally." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Program.cs line 38: "CORS allows any origin, method, and header." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp.csproj lines 8, 9: "DebugSymbols is true for all build configurations" and "DebugType full is set for all build configurations." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | SampleBankingApp.csproj line 15: "Newtonsoft.Json 12.0.3 is outdated." |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Repository: No appsettings.Production.json file is present. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|-------------|--------|-------|
| UT | **No test project exists in the provided source** — key areas that need tests include `AuthService.Login`, `TransactionService.Transfer`, etc. | Found | Repository: No test project exists in the provided source. |

## Summary

Total: 48 Found / 15 Partial / 7 Missed out of 70 issues.
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Missed | `GenerateJwtToken` | yes | under-credited? |
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

**Adjusted Found: 68 of 70** (69 reported, less 1 mis-credited).

### Self-hedged ratings

Rows rated `Found` whose own Note concedes the review did not cover the target. That phrasing describes a Partial; each is likely an over-credit, though a conceded detail can be incidental to the reference issue.

| ID | Hedge | Note |
|---|---|---|
| E6 | `but does not` | DatabaseHelper.cs line 52: "ExecuteNonQuery closes the connection but does not dispose it." |
| RL3 | `but does not` | DatabaseHelper.cs lines 52, 54: "ExecuteNonQuery closes the connection but does not dispose it" and "ExecuteNonQuery can leak the connection if the command throws before Close." |

**Plausible floor: 66 of 70** (adjusted 68, less 2 self-hedged).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3.6-27B:Q4_K_S` |
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
| Grounding downgrades | `1` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 53beb17` |
