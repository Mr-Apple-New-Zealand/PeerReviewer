# AI Review Scorecard

> **Branch:** `Claude-Opus-4.7` &nbsp;·&nbsp; **Commit:** `(local)`

Total: 64 Found / 4 Partial / 2 Missed out of 70 issues.

## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | AuthService.cs:32 — "SQL injection via string interpolation of `username`/`hashedPassword` into the login query." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | AuthService.cs:17 — "Hardcoded backdoor `AdminBypassPassword = \"SuperAdmin2024\"` grants `SuperAdmin` role to anyone who knows it." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | AuthService.cs:30 — "Passwords hashed with unsalted MD5 — broken cryptography." (recommends PBKDF2/Argon2/bcrypt with per-user salt). |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | UserService.cs:47 & :61 — "`UpdateUser` interpolates `email`, `username`, `id` into UPDATE — SQL injection" and "`DeleteUser` interpolates `id` into DELETE — SQL injection". |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | UserService.cs:99 — "`SearchUsers` passes raw `query` into a `LIKE '%...%'` clause via `ExecuteQuery` — SQL injection." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | TransactionService.cs:47-48 & :70 — "Balance UPDATE statements built via string interpolation — SQL injection" and "Deposit UPDATE built via string interpolation." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | TransactionService.cs:89-91 — "`RecordTransaction` interpolates `description` (user-controlled) and other fields into INSERT — SQL injection." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | appsettings.json:3,6,14 — DB connection with `Admin1234!`, JWT key `"mysecretkey"`, and SMTP password `EmailPass99` all flagged as committed to source. |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Program.cs:24 — "`ValidateLifetime = false` — expired JWTs are accepted indefinitely." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | UserController.cs:38 — "`UpdateUser` PUT has no ownership/role check — any authenticated user can edit any account." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | UserController.cs:56 — "`DeleteUser` DELETE has no ownership/role check." |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | TransactionService.cs:25 — "`amount < 0` allows `amount == 0` to proceed as a valid transfer." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | TransactionService.cs:42 — "Balance check uses `fromBalance >= amount` but the debit is `amount + fee` — can drive balance negative by the fee amount." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | UserService.cs:72 — "Pagination uses `page * pageSize` — page 1 skips the first page entirely (off-by-one). Use `(page - 1) * pageSize`." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | TransactionService.cs:68 — "`interestBonus = amount * 0.05m * 1` — applies a 5% \"bonus\" to every deposit, so users gain 5% free money each call." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | TransactionService.cs:23 — "No self-transfer check — user can `fromUserId == toUserId`, paying fees to themselves and losing money." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | UserService.cs:20-23 — "Duplicated `id <= 0` / `id > 1_000_000` validation copied to three methods. Extract `ValidateUserId(int)`." |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | StringHelper.cs:31-34 — "`result += item + separator` inside a loop — O(n²) string concat. Use `string.Join` (as the \"Fixed\" sibling does)." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed |  |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | UserService.cs:105-108 — "`SearchUsers` catches `Exception` and returns an empty list — caller cannot distinguish 'no results' from 'DB failure'." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | EmailService.cs:75-78 — "`SendWelcomeEmail` swallows all exceptions silently via `Console.WriteLine`." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | TransactionService.cs:42-57 — "Two `UPDATE` statements + `RecordTransaction` are not in a transaction — partial failure leaves the system inconsistent (money debited, credit lost)." |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | TransactionService.cs:52-55 — "`SendTransferNotification` runs after the DB writes commit; if SMTP throws... the controller returns `BadRequest` even though money already moved." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | UserController.cs:52 — "Returns raw `ex.Message` to HTTP client — leaks internals." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | DatabaseHelper.cs:50-57 — "`ExecuteNonQuery` calls `connection.Close()` only on the happy path — any exception leaks the open connection and undisposed command." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | AuthController.cs:19 — "`[HttpPost(\"login\")]` has no rate limiting or account lockout — brute-force friendly." |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | AuthService.cs:34-51 — "`Login` opens `SqlConnection`, `SqlCommand`, and `SqlDataReader` — none disposed; any throw leaks all three." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | DatabaseHelper.cs:19-34 — "`GetOpenConnection()` returns an open `SqlConnection` with no documented disposal contract" and "`ExecuteQuery` opens a connection, `SqlCommand`, and `SqlDataAdapter` but disposes none." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | DatabaseHelper.cs:50-57 — "`ExecuteNonQuery` calls `connection.Close()` only on the happy path — any exception leaks the open connection and undisposed command. Use `using` blocks." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | EmailService.cs:16 — "`SmtpClient` held as instance field — not thread-safe and connection never released." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | EmailService.cs:39 & :69 — "`MailMessage` instances are never disposed. Wrap each `MailMessage` in `using`." |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | AuthService.cs:70 — "`Encoding.UTF8.GetBytes(_config[\"Jwt:SecretKey\"]!)` — will NRE if config key missing; `!` only suppresses warning." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | TransactionService.cs:36-37 — "`fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — NRE/`IndexOutOfRangeException` when user id is invalid." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | EmailService.cs:24 — Review references the exact `int.Parse(_config["Email:SmtpPort"] ?? "25")` line but explicitly calls it "ok" and pivots to `NetworkCredential`; the missing-config-key concern is not flagged. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | EmailService.cs:65 — "`username.ToUpper()` — NRE if `username` is null." |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | StringHelper.cs:13 & :22 — "`IsValidEmail` reads `email.Length` without null check" and "`IsValidUsername` reads `username.Length` without null check." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | TransactionController.cs:27 — "`int.Parse(userIdClaim!)` — `userIdClaim` could be null. `TryParse` and 401 on failure." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | AuthController.cs:20 & TransactionController.cs:24 — model-bound `request` null guards flagged on Login and Transfer endpoints, but `UpdateUser` is not specifically called out as missing the request-null check. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Partial | TransactionService.cs:39 references `TransactionFeeRate` but only as context for criticizing the inline `2` decimal-places literal; it does not say the fee rate / daily-limit constants belong in configuration. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | TransactionService.cs:65 — "Deposit cap `1000000` hardcoded inline. Extract to a named constant or config value." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | EmailService.cs:40 & :67 — "`\"notifications@company.com\"` from-address duplicated in three places" and "`\"support@company.com\"` hardcoded in body text." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | StringHelper.cs:13 & :22 — "Email max length `254` literal. Name as constant `MaxEmailLength`" and "Username bounds `3` and `20` literal. Extract as `MinUsernameLength`/`MaxUsernameLength`." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | UserService.cs:70 — "Max `pageSize` of `50` hardcoded inline. Extract to a named constant." |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | AuthService.cs:91-96 — "`HashPasswordSha1` is never called. Delete." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | AuthService.cs:103-107 — "Code after the unconditional `return true;` on line 103 is unreachable, and the method is itself never called." |
| D3 | `TableExists` — never called from any service or controller. | Found | DatabaseHelper.cs:59-65 — "`TableExists` is never called. Delete or document usage." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | DatabaseHelper.cs:67-78 — "`ExecuteQueryWithParams` is `[Obsolete]` and unused. Delete." |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | EmailService.cs:81-92 — "`BuildHtmlTemplate` and `SendWelcomeEmailHtml` are never called." (names `BuildHtmlTemplate` explicitly). |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | EmailService.cs:81-92 — same sentence explicitly names `SendWelcomeEmailHtml` as never called. |
| D7 | `FormatCurrency` — private, never called. | Found | TransactionService.cs:94-97 — "`FormatCurrency` is never used. Remove." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | TransactionService.cs:77-85 — "`IsWithinDailyLimit` is never invoked. Either wire it into transfer/deposit or remove." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | StringHelper.cs:43-52 — "`MaskAccountNumber` and `ObfuscateAccount` are duplicate implementations; neither appears to be called." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Missed |  |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Partial | StringHelper.cs:29-36 — review names both methods and the duplication but identifies the broken `JoinWithSeparator` as the dead one to delete, not the unused `JoinWithSeparatorFixed`. |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | UserService.cs:10-11 — "`_auditLog` and `_requestCount` are mutable static state mutated from a Scoped service — race conditions across requests." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | StringHelper.cs:16 & :25 — "`new Regex(...)` inside `IsValidEmail` is recompiled every call. `static readonly Regex` (and add `RegexOptions.Compiled`)." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | StringHelper.cs:31-34 — "`result += item + separator` inside a loop — O(n²) string concat. Use `string.Join`." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | EmailService.cs:16 — "`SmtpClient` held as instance field — not thread-safe and connection never released... Create `SmtpClient` per send inside a `using`." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | StringHelper.cs:65-71 — "`IsBlank` reimplements `string.IsNullOrWhiteSpace`. Delete and call the BCL method." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | DatabaseHelper.cs:19-24 — "`GetOpenConnection()` leaks resource ownership to callers with no documented contract — direct cause of the resource leaks in §4." |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | appsettings.json:3,6,14 — DB password `Admin1234!`, JWT key `mysecretkey`, and SMTP password `EmailPass99` each flagged as "committed to source control" / "hardcoded in config." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | appsettings.json:18-20 — "Default, Microsoft, and System log levels all set to `Debug` — verbose & PII risk in prod." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Program.cs:24 — "`ValidateLifetime = false` on JWT. Enable lifetime validation." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Program.cs:36 — "HTTPS redirection commented out. Enable." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Program.cs:34 — "`UseDeveloperExceptionPage()` always on. Gate with `app.Environment.IsDevelopment()`." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Program.cs:38 — "CORS `AllowAnyOrigin + AllowAnyMethod + AllowAnyHeader`. Lock down." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp.csproj:8-9 — "`DebugSymbols=true` + `DebugType=full` applied unconditionally (including Release)." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | SampleBankingApp.csproj:15 — "`Newtonsoft.Json 12.0.3` has known CVEs (e.g. denial-of-service in deep JSON) and is well out of date." |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Program.cs/SampleBankingApp/ — "No `appsettings.Production.json` / environment-specific override files present. Add per-environment configuration." |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | **Missing Unit Tests** — no test project / test files anywhere; key coverage gaps include `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer/Deposit`, `UserService.GetUsersPage`, `StringHelper`, and controller action results. | Found | Section 10 of the review opens with "No test project is present in the repository (no `*.Tests.csproj`, no `tests/` folder, no test references in the only `.csproj`)" and then enumerates priority targets across `Transfer`, `Deposit`, `Login`, `GenerateJwtToken`, `GetUsersPage`, `SearchUsers`, controller authorization, `StringHelper`, and `SendTransferNotification` — matching the aggregate UT scope. |
