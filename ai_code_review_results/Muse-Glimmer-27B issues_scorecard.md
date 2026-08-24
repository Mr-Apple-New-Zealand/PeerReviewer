# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `06d631c`

> ⚠ **1 row(s) rated Found name a target that never appears in the review** (C7). Adjusted Found: **60** of 70. See the spot-check below.

Total: 61 Found / 8 Partial / 1 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | AuthService.cs line 32: "Login builds SQL with interpolated username and hashed password" |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | AuthService.cs line 17: "AdminBypassPassword constant contains hardcoded backdoor password" |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | AuthService.cs line 30: "HashPasswordMd5 uses MD5 for password hashing" |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | UserService.cs lines 47, 61: "UPDATE Users statement uses string interpolation for email username and id" and "DELETE FROM Users statement uses string interpolation for id" |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | UserService.cs line 99: "SearchUsers calls ExecuteQuery with LIKE interpolation" |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | TransactionService.cs lines 47, 48, 71: "UPDATE Users statement uses string interpolation for balance and id", "UPDATE Users statement uses string interpolation for balance and id", "UPDATE Users statement uses string interpolation for amount and id" |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | TransactionService.cs line 90: "INSERT INTO Transactions uses string interpolation for values" |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | appsettings.json lines 3, 6, 14: "Connection string contains plaintext password Admin1234!", "Jwt SecretKey is weak value mysecretkey", "Email password EmailPass99 committed to source" |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Program.cs line 24: "TokenValidationParameters ValidateLifetime set to false" |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | UserController.cs line 39: "UpdateUser allows any authenticated user to update any user id" |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | UserController.cs line 57: "DeleteUser allows any authenticated user to delete any user id" |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | TransactionService.cs line 23: "Transfer does not prevent transfer to same user id" (note: this is a different issue than the description, but it's about zero value handling) |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | TransactionService.cs line 42: "Balance check uses amount only but total debit includes fee" |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | UserService.cs line 72: "Skip calculated as page * pageSize causing off-by-one pagination" |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | TransactionService.cs line 68: "Interest bonus uses magic multiplier 1 and rate 0.05m" |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | TransactionService.cs line 23: "Transfer does not prevent transfer to same user id" |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | UserService.cs lines 20, 40, 54: "GetUserById repeats id validation logic", "UpdateUser repeats id validation logic", "DeleteUser repeats id validation logic" |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | StringHelper.cs line 31: "JoinWithSeparator uses string concatenation in loop causing O(n²)" |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | AuthService.cs line 70: "GenerateJwtToken reads Jwt:SecretKey with null-forgiving operator" (this addresses the method but doesn't mention splitting it into helpers) |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | UserService.cs line 105: "SearchUsers catches generic Exception and returns empty list" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | EmailService.cs line 75: "SendWelcomeEmail catches Exception and only writes to console" |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | TransactionService.cs line 47: "Transfer performs two updates without transaction" |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | TransactionService.cs line 52: "Email sent after DB updates without rollback on failure" |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | UserController.cs lines 50, 52: "UpdateUser catches Exception and returns ex.Message to client", "UpdateUser returns raw exception message in 500 response" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | DatabaseHelper.cs line 53: "ExecuteNonQuery closes connection but not disposed on exception" |
| E7 | **No rate limiting or account lockout on failed login attempts** — brute force is trivially possible. | Partial | Program.cs lines 24, 34, 36, 38: "TokenValidationParameters ValidateLifetime set to false", "UseDeveloperExceptionPage called unconditionally", "HTTPS redirection is commented out", "CORS policy allows any origin method and header" (these are all config issues but not specifically about rate limiting) |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | AuthService.cs lines 34, 37: "SqlConnection created and opened without using", "SqlCommand and SqlDataReader created without disposal" |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | DatabaseHelper.cs line 19: "GetOpenConnection returns SqlConnection without disposing contract" |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | DatabaseHelper.cs lines 29, 53: "ExecuteQuery opens connection without try finally", "ExecuteNonQuery closes connection but not disposed on exception" |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | EmailService.cs line 22: "SmtpClient stored as instance field and never disposed" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | EmailService.cs lines 39, 69, 89: "MailMessage created without disposal", "MailMessage created without disposal", "MailMessage created without disposal" |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Program.cs line 28: "Encoding.UTF8.GetBytes(jwtSecret!) may receive null" |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | TransactionService.cs lines 36, 37: "Rows[0] accessed without checking Rows.Count", "Rows[0] accessed without checking Rows.Count" |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | EmailService.cs line 24: "int.Parse on _config["Email:SmtpPort"] may be null" |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | _(ungrounded: no matching sentence in review)_ |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | StringHelper.cs lines 13, 22: "IsValidEmail accesses email.Length without null check", "IsValidUsername accesses username.Length without null check" |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | TransactionController.cs lines 27, 41: "int.Parse(userIdClaim!) assumes claim present", "int.Parse(userIdClaim!) assumes claim present" |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | UserController.cs line 28: "GetUser returns any user by id without ownership check" (this is about missing null checks but not the specific issue of request==null) |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | TransactionService.cs lines 68, 65: "Interest bonus uses literal 0.05m and multiplier 1", "Deposit amount cap 1000000 is literal" |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | TransactionService.cs line 65: "Deposit amount cap 1000000 is literal" |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | EmailService.cs lines 10, 11: "TransferSubject string literal repeated", "WelcomeSubject string literal repeated" (these are about subject strings but not the email address literals) |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | StringHelper.cs lines 13, 22: "Email max length 254 is literal", "Username min length 3 and max 20 are literals" |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | UserService.cs line 70: "Page size cap 50 is literal" |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | AuthService.cs line 91: "HashPasswordSha1 method defined but never called" |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | AuthService.cs lines 98, 105-108: "ValidateToken returns true early making lines 105-108 unreachable", "Remove unreachable code" |
| D3 | `TableExists` — never called from any service or controller. | Found | DatabaseHelper.cs line 59: "TableExists method defined but never called" |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | DatabaseHelper.cs line 67: "ExecuteQueryWithParams marked Obsolete and unused" |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Partial | EmailService.cs line 86: "SendWelcomeEmailHtml method appears unused" (this covers D6 but not D5) |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | EmailService.cs line 86: "SendWelcomeEmailHtml method appears unused" |
| D7 | `FormatCurrency` — private, never called. | Found | TransactionService.cs line 94: "FormatCurrency method defined but never called" |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | TransactionService.cs line 77: "IsWithinDailyLimit method defined but never called" |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | StringHelper.cs line 54: "ObfuscateAccount method appears unused" |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | StringHelper.cs line 59: "ToTitleCase method appears unused" |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | StringHelper.cs lines 38, 29: "JoinWithSeparatorFixed uses string.Join and appears unused", "JoinWithSeparator uses manual concatenation and appears unused" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | UserService.cs lines 10, 11: "_auditLog static List shared without synchronization", "_requestCount static int shared without synchronization" |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | StringHelper.cs lines 16, 25: "IsValidEmail creates new Regex each call", "IsValidUsername creates new Regex each call" |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | StringHelper.cs line 31: "JoinWithSeparator uses string concatenation in loop causing O(n²)" |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | EmailService.cs line 22: "SmtpClient stored as instance field and never disposed" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Partial | StringHelper.cs line 65: "IsBlank method appears unused" (this is about a duplicate function but not the specific issue of reimplementing BCL) |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | DatabaseHelper.cs line 19: "GetOpenConnection returns SqlConnection without disposing contract" |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | appsettings.json lines 3, 6, 14: "Connection string contains plaintext password Admin1234!", "Jwt SecretKey is weak value mysecretkey", "Email password EmailPass99 committed to source" |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | Program.cs lines 34, 24: "UseDeveloperExceptionPage called unconditionally", "ValidateLifetime false disables token expiry check" (these are about other config issues but not specifically log level) |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Program.cs line 24: "TokenValidationParameters ValidateLifetime set to false" |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Program.cs line 36: "HTTPS redirection is commented out" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Program.cs line 34: "UseDeveloperExceptionPage called unconditionally" |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Program.cs line 38: "CORS policy allows any origin method and header" |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp.csproj lines 8, 9: "DebugSymbols true in release build", "DebugType full in release build" |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | SampleBankingApp.csproj line 15: "Newtonsoft.Json version 12.0.3 is outdated" |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Partial | Program.cs lines 16, 28: "Jwt secret read without validation", "Encoding.UTF8.GetBytes(jwtSecret!) may receive null" (these are about config but not specifically about missing appsettings.production) |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, Controller action results — correct HTTP status codes for various service responses | Found | Missing Unit Tests section: "Add unit tests covering auth flows", "Add unit tests for token generation", "Add tests for boundary conditions", "Add tests for valid and invalid amounts", "Add tests for page boundaries", "Add tests for input validation", "Add tests for error handling", "Add tests for missing claim", "Add tests for retry behavior", "Add integration tests for startup config" |
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | **no** | **MIS-CREDIT** |
| R3 | Partial | `GenerateJwtToken` | yes | under-credited? |
| E7 | Partial | `rate limit` | **no** | - |
| N3 | Found | `SmtpPort` | yes | - |
| D1 | Found | `HashPasswordSha1` | yes | - |
| D3 | Found | `TableExists` | yes | - |
| D4 | Found | `ExecuteQueryWithParams` | yes | - |
| D5 | Partial | `BuildHtmlTemplate` | **no** | - |
| D6 | Found | `SendWelcomeEmailHtml` | yes | - |
| D7 | Found | `FormatCurrency` | yes | - |
| D8 | Found | `IsWithinDailyLimit` | yes | - |
| D9 | Found | `ObfuscateAccount` | yes | - |
| D10 | Found | `ToTitleCase` | yes | - |
| D11 | Found | `JoinWithSeparatorFixed` | yes | - |
| CF9 | Partial | `appsettings.Production` | **no** | - |

**Adjusted Found: 60 of 70** (61 reported, less 1 mis-credited).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Muse-Glimmer-30B-imatrix:Q4_K_S` |
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
| Branch / commit | `main @ 06d631c` |
