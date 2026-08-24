# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `3d4ff91`

> ⚠ **1 row(s) rated Found name a target that never appears in the review** (N3). Adjusted Found: **68** of 70. See the spot-check below.

Total: 69 Found / 0 Partial / 1 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | AuthService.cs line 32: "Login builds SQL via string interpolation with `username` and `hashedPassword`, enabling SQL injection." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | AuthService.cs lines 53–56: "Hardcoded admin backdoor: any request with username `"admin"` and password `"SuperAdmin2024"` bypasses the DB and returns a SuperAdmin user." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | AuthService.cs lines 61–66: "HashPasswordMd5 uses MD5 (unsalted, broken) for password hashing." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | UserService.cs line 47: "UpdateUser builds an UPDATE via string interpolation with `email` and `username`." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | UserService.cs line 99: "SearchUsers passes user input directly into a `LIKE '%{query}%'` clause via `ExecuteQuery`." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | TransactionService.cs lines 47–48: "Transfer builds UPDATE statements via string interpolation with computed balance values." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | TransactionService.cs lines 89–90: "RecordTransaction builds an INSERT via string interpolation including `description` (user-supplied)." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | appsettings.json line 3: "Production database credentials (`User Id=sa;Password=Admin1234!`) committed to source control." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Program.cs line 24: "ValidateLifetime = false means issued JWTs never expire." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | UserController.cs lines 39–54: "UpdateUser has no ownership check; any authenticated user can update any user by ID." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | UserController.cs lines 56–69: "DeleteUser has no ownership check; any authenticated user can delete any user." |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | TransactionService.cs line 25: "Transfer rejects `amount < 0` but allows `amount == 0`, permitting a zero-value transfer that still incurs a fee and a DB write." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | TransactionService.cs line 42: "Transfer checks `fromBalance >= amount` but then deducts `amount + fee` (totalDebit), so a user with exactly `amount` in balance will go negative." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | UserService.cs line 72: "GetUsersPage computes `skip = page * pageSize`, so page 1 skips 20 rows instead of 0 (off-by-one)." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | TransactionService.cs line 68: "Deposit computes `amount * 0.05m * 1`; the `* 1` is a no-op and the 5% rate appears incorrect (likely meant to be 1% or a configurable rate)." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | TransactionService.cs line 23–61: "Transfer has no self-transfer check; a user can transfer to their own ID." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | UserService.cs lines 20, 38, 54: "UserService has duplicated validation logic across GetUserById, UpdateUser, DeleteUser." |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | StringHelper.cs line 31: "JoinWithSeparator uses string concatenation (`+=`) inside a loop, producing O(n²) allocations." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | AuthService.cs lines 28–59: "Login carries at least three distinct responsibilities: password hashing, DB query + row mapping, and admin-bypass logic." |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | UserService.cs lines 97–108: "SearchUsers catches a broad `Exception` and returns an empty `List<User>`." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | EmailService.cs line 71: "SendWelcomeEmail catches a broad `Exception` and only writes to `Console.WriteLine`, silently swallowing the failure." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | TransactionService.cs lines 47–50: "Transfer executes two separate `ExecuteNonQuery` calls (debit and credit) without a database transaction; if the second fails, the first is already committed." |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Found | TransactionService.cs lines 52–55: "Transfer sends an email after the DB writes have committed; if SendTransferNotification throws, the transfer is already persisted but the caller receives an error." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | UserController.cs line 52: "UpdateUser returns `ex.Message` directly to the HTTP client, potentially leaking internal details." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | DatabaseHelper.cs lines 50–57: "ExecuteNonQuery calls GetOpenConnection() and only calls `connection.Close()`; if ExecuteNonQuery throws, Close() is never reached." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | AuthController.cs lines 19–31: "No rate limiting or account lockout on the login endpoint; an attacker can brute-force credentials indefinitely." |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | AuthService.cs lines 34–38: "Login creates a `SqlConnection` and `SqlDataReader` without `using`; neither is closed or disposed on any code path." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | DatabaseHelper.cs lines 19–24: "GetOpenConnection returns an open `SqlConnection` with no documented contract that the caller must dispose it." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | DatabaseHelper.cs lines 50–57: "ExecuteNonQuery calls GetOpenConnection() and only calls `connection.Close()`; if ExecuteNonQuery throws, Close() is never reached." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | EmailService.cs line 16: "SmtpClient is stored as an instance field; SmtpClient is not thread-safe and the underlying socket is never released." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | EmailService.cs lines 39, 69: "SendTransferNotification creates a `MailMessage` that is never disposed." |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Program.cs line 28: "jwtSecret! uses null-forgiving; if `"Jwt:SecretKey"` is missing from config, `Encoding.UTF8.GetBytes(null)` throws." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | TransactionService.cs lines 36–37: "Accesses fromUserTable.Rows[0] and toUserTable.Rows[0] without verifying Rows.Count > 0." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | EmailService.cs line 24: "_config[\"Email:SmtpPort\"] can be null and is passed directly to the SmtpClient constructor." |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | _(ungrounded: no matching sentence in review)_ |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | StringHelper.cs lines 14, 24: "email.Length and username.Length throw if argument is null — no null guard before Length access." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | TransactionController.cs lines 19, 31: "userIdClaim! uses null-forgiving; if the NameIdentifier claim is absent, int.Parse(null) throws ArgumentNullException." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | UserController.cs line 72: "UpdateUser uses request.Email and request.Username without a null check on request itself." |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | TransactionService.cs line 12: "MaxTransactionsPerDay = 10 is a constant but should be configurable per deployment." |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | TransactionService.cs line 65: "1000000 (max deposit) is a magic number with no named constant." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | EmailService.cs lines 40, 67, 89: "Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | StringHelper.cs lines 13, 22: "254 (max email length), 3 and 20 (username min/max length) are magic numbers." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | UserService.cs line 70: "50 (max page size) is a magic number." |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | AuthService.cs lines 91–96: "HashPasswordSha1 is defined but never called anywhere in the codebase." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | AuthService.cs lines 105–107: "ValidateToken contains unreachable code after an unconditional return true; on line 103." |
| D3 | `TableExists` — never called from any service or controller. | Found | DatabaseHelper.cs lines 59–65: "TableExists is defined but never called anywhere in the codebase." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | DatabaseHelper.cs lines 67–78: "ExecuteQueryWithParams is marked [Obsolete] and is never called." |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | EmailService.cs lines 81–84: "BuildHtmlTemplate is only called by the dead SendWelcomeEmailHtml and is itself never called from live code." |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | EmailService.cs lines 86–92: "SendWelcomeEmailHtml is defined but never called anywhere in the codebase." |
| D7 | `FormatCurrency` — private, never called. | Found | TransactionService.cs lines 94–97: "FormatCurrency is defined but never called anywhere in the codebase." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | TransactionService.cs lines 77–85: "IsWithinDailyLimit is defined but never called anywhere in the codebase." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | StringHelper.cs lines 54–57: "ObfuscateAccount is defined but never called anywhere in the codebase." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | StringHelper.cs lines 59–63: "ToTitleCase is defined but never called anywhere in the codebase." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | StringHelper.cs lines 38–41: "JoinWithSeparatorFixed is defined but never called anywhere in the codebase." |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | UserService.cs lines 10, 11: "_auditLog is a static List<string> mutated from multiple threads without synchronization." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | StringHelper.cs lines 16, 25: "IsValidEmail creates a new Regex(...) on every call." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | StringHelper.cs line 31: "JoinWithSeparator uses string concatenation (`+=`) inside a loop, producing O(n²) allocations." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | EmailService.cs line 16: "SmtpClient is stored as an instance field; SmtpClient is not thread-safe." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | StringHelper.cs lines 65–71: "IsBlank reimplements string.IsNullOrWhiteSpace with three separate checks." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | DatabaseHelper.cs lines 19–24: "GetOpenConnection leaks resource ownership to callers with no documented contract for disposal." |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | appsettings.json lines 3, 6, 14: "Production database credentials (`User Id=sa;Password=Admin1234!`) committed to source control." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | appsettings.json lines 18–20: "Log level is `"Debug"` for Default, Microsoft, and System namespaces." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Program.cs line 24: "ValidateLifetime = false means issued JWTs never expire." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Program.cs line 36: "app.UseHttpsRedirection() is commented out." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Program.cs line 34: "UseDeveloperExceptionPage() is called unconditionally without an environment check." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Program.cs line 38: "CORS allows AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader() simultaneously." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp.csproj lines 8–9: "DebugSymbols=true and DebugType=full are set in the unconditional PropertyGroup." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | SampleBankingApp.csproj line 15: "Newtonsoft.Json 12.0.3 has known CVEs (e.g., CVE-2019-13059)." |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | appsettings.json lines 1–24: "No appsettings.Production.json exists for environment-specific overrides (connection strings, log levels, secrets)." |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project exists in the repository; zero unit or integration tests are present. Key areas that need tests include: AuthService.Login — SQL injection boundary cases, correct vs. incorrect password; AuthService.GenerateJwtToken — claims mapping, expiry; TransactionService.Transfer — zero amount, self-transfer, fee deduction, insufficient funds (with fee); TransactionService.Deposit — interest rate correctness; UserService.GetUsersPage — pagination offset correctness (the off-by-one); StringHelper — null inputs, boundary lengths, separator trailing character; Controller action results — correct HTTP status codes for various service responses | Found | Missing Unit Tests row: "No test project exists in the repository; zero unit or integration tests are present." |
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

**Adjusted Found: 68 of 70** (69 reported, less 1 mis-credited).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3.8-27B-imatrix:Q4_K_S` |
| Reasoning strength (system prompt) | (model default) |
| Ollama `think` | `medium` |
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
| Branch / commit | `main @ 3d4ff91` |
