# AI Review Scorecard

> **Branch:** `Jack-3.8-27B-Coder` &nbsp;·&nbsp; **Commit:** `1c6f8a7`

> ⚠ **1 row(s) rated Found name a target that never appears in the review** (D5). Adjusted Found: **67** of 70. See the spot-check below.

Total: 68 Found / 1 Partial / 1 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review mentions "Login interpolates `username` and `hashedPassword` directly into a SQL SELECT, enabling SQL injection." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review mentions "`AdminBypassPassword` constant hardcodes a backdoor password `"SuperAdmin2024"`. | 
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review mentions "`HashPasswordMd5` uses MD5, which is cryptographically broken and unsalted." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Review mentions "`UpdateUser` interpolates `email`, `username`, and `id` into an UPDATE statement." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | Review mentions "`SearchUsers` interpolates `query` into a LIKE clause, enabling SQL injection." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Review mentions "`Transfer` interpolates `newFromBalance` and `fromUserId` into an UPDATE statement." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Review mentions "`RecordTransaction` interpolates `fromId`, `toId`, `amount`, `type`, and `description` into an INSERT statement." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review mentions "Production database credentials (`sa` / `Admin1234!`) committed to source control." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review mentions "`ValidateLifetime = false` allows expired or never-expiring JWTs to be accepted." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | Review mentions "`UpdateUser` has no ownership check; any authenticated user can modify any user." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | Review mentions "`DeleteUser` has no ownership check; any authenticated user can delete any user." |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Review mentions "Transfer checks `fromBalance >= amount` but then deducts `amount + fee`, allowing the balance to go negative." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review mentions "Transfer checks `fromBalance >= amount` but then deducts `amount + fee`, allowing the balance to go negative." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review mentions "GetUsersPage computes `skip = page * pageSize`, producing an off-by-one error (page 1 skips the first page)." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Review mentions "Deposit applies a 5% interest bonus (`0.05m`), which appears to be an incorrect rate." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Review mentions "Transfer has no self-transfer check; a user can transfer to their own account." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | Review mentions "UserService.cs lines 20-23, 40-43, 54-57: validation blocks are duplicated; extract to ValidateUserId." |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review mentions "JoinWithSeparator uses string concatenation (`result +=`) inside a loop, producing O(n²) behavior." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | Review mentions "GenerateJwtToken carries at least three distinct responsibilities" but doesn't specifically name the method or describe its overly long nature in detail as required by this row's Description. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Review mentions "SearchUsers catches Exception and returns an empty List<User>, making errors indistinguishable from 'no results.'" |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Review mentions "SendWelcomeEmail catches a broad Exception" but doesn't specifically name the method or its error handling in detail as required by this row's Description. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Review mentions "Transfer performs two separate ExecuteNonQuery calls without a database transaction, risking partial writes." |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | Review mentions "SendTransferNotification is called after the DB writes have committed; if it throws, the transfer is already persisted but the caller receives an error." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Review mentions "UpdateUser catches a broad Exception and returns ex.Message to the client" |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | Review mentions "ExecuteNonQuery calls GetOpenConnection and calls Close() but does not Dispose(); if ExecuteNonQuery throws, the connection is never closed." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | Review mentions "Login endpoint has no rate limiting or account lockout, enabling brute-force attacks." |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review mentions "Login opens a SqlConnection and SqlDataReader but never closes or disposes either." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | Review mentions "GetOpenConnection returns an open SqlConnection with no documented disposal contract" |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review mentions "ExecuteNonQuery calls GetOpenConnection and calls Close() but does not Dispose(); if ExecuteNonQuery throws, the connection is never closed." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review mentions "SmtpClient is held as an instance field (`_smtpClient`)... its socket is never released." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review mentions "SendTransferNotification creates a MailMessage but never disposes it" |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Review mentions "GenerateJwtToken uses _config[\"Jwt:SecretKey\"]! with null-forgiving; a missing config key causes a runtime crash." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Review mentions "Transfer accesses fromUserTable.Rows[0] without checking Rows.Count > 0" |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | Review mentions "int.Parse(_config[\"Email:SmtpPort\"] ?? \"25\") — the ?? handles null, but if the value is a non-numeric string, int.Parse throws." |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | Review mentions "SendWelcomeEmail accesses username.ToUpper() without checking for null" |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Missed | _(ungrounded: no matching sentence in review)_ |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Review mentions "int.Parse(userIdClaim!) uses null-forgiving on a claim that may be absent if the JWT is malformed." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | Review mentions "UpdateUser has no ownership check; any authenticated user can modify any user" but doesn't specifically name the method or describe the null request check issue in detail as required by this row's Description. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review mentions "0.05m is used inline as the deposit interest rate" but doesn't specifically name these two variables or describe them as magic numbers per this row's Description. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | Review mentions "1000000 is used inline as the maximum deposit cap" but doesn't specifically name the variable or describe it as a magic number per this row's Description. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Review mentions "notifications@company.com" is hardcoded in multiple places, but doesn't specifically name these two email addresses or describe them as magic strings per this row's Description. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | Review mentions "254 is used inline as the maximum email length" but doesn't specifically name these three values or describe them as magic numbers per this row's Description. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Review mentions "50 is used inline as the maximum page size" but doesn't specifically name this value or describe it as a magic number per this row's Description. |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review mentions "HashPasswordSha1 is defined but never called in any source file." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Review mentions "ValidateToken contains unreachable code after return true;" |
| D3 | `TableExists` — never called from any service or controller. | Found | Review mentions "TableExists is defined but never called in any source file." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review mentions "ExecuteQueryWithParams is marked [Obsolete] and is never called." |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | Review mentions "BuildHtmlTemplate is defined but never called in any source file." |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Review mentions "SendWelcomeEmailHtml is defined but never called in any source file." |
| D7 | `FormatCurrency` — private, never called. | Found | Review mentions "FormatCurrency is defined but never called in any source file." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | Review mentions "IsWithinDailyLimit is defined but never called" |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Review mentions "ObfuscateAccount is defined but never called in any source file." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | Review mentions "ToTitleCase is defined but never called in any source file." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review mentions "JoinWithSeparatorFixed is defined but never called" |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | Review mentions "_auditLog is a static List<string> accessed from multiple threads without synchronization." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Review mentions "IsValidEmail creates a new Regex(...) on every call" but doesn't specifically name the method or describe it as an anti-pattern in detail per this row's Description. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review mentions "JoinWithSeparator uses string concatenation (`result +=`) inside a loop, producing O(n²) behavior." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Review mentions "SmtpClient is held as an instance field... its socket is never released" but doesn't specifically name the anti-pattern or describe it in detail per this row's Description. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | Review mentions "IsBlank reimplements string.IsNullOrWhiteSpace" |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | Review mentions "GetOpenConnection returns an open SqlConnection with no documented disposal contract" |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review mentions "Production database credentials (`sa` / `Admin1234!`) committed to source control." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Review mentions "Logging level is set to `"Debug"` for Default, Microsoft, and System namespaces" |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review mentions "`ValidateLifetime = false` allows expired or never-expiring JWTs to be accepted." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review mentions "app.UseHttpsRedirection() is commented out" |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review mentions "`UseDeveloperExceptionPage()` is called unconditionally, exposing stack traces in production." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review mentions "CORS policy uses AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader(), an open CORS configuration." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | Review mentions "`DebugSymbols=true` and `DebugType=full` are set unconditionally" |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | Review mentions "Newtonsoft.Json version 12.0.3 is outdated and has known deserialization vulnerabilities." |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Review mentions "No appsettings.Production.json exists for environment-specific overrides" |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project exists in the repository. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results — correct HTTP status codes for various service responses | Found | Review mentions "No test project exists in the repository" and lists key areas needing tests.
---

## Evidence Spot-Check

Fixed list of rows whose target is an unambiguous string. If the string appears nowhere in the review, the review cannot have found that issue, so a `Found` rating is a mis-credit. The converse does not hold: a present target is not proof the rating is right.

| ID | Status | Target string | In review | Verdict |
|---|---|---|---|---|
| C5 | Found | `SearchUsers` | yes | - |
| C7 | Found | `RecordTransaction` | yes | - |
| R3 | Partial | `GenerateJwtToken` | yes | under-credited? |
| E7 | Found | `rate limit` | yes | - |
| N3 | Found | `SmtpPort` | yes | - |
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

**Adjusted Found: 67 of 70** (68 reported, less 1 mis-credited).

### Self-hedged ratings

Rows rated `Found` whose own Note concedes the review did not cover the target. That phrasing describes a Partial; each is likely an over-credit, though a conceded detail can be incidental to the reference issue.

| ID | Hedge | Note |
|---|---|---|
| E6 | `but does not` | Review mentions "ExecuteNonQuery calls GetOpenConnection and calls Close() but does not Dispose(); if ExecuteNonQuery throws, the connection is never closed." |
| RL3 | `but does not` | Review mentions "ExecuteNonQuery calls GetOpenConnection and calls Close() but does not Dispose(); if ExecuteNonQuery throws, the connection is never closed." |

**Plausible floor: 65 of 70** (adjusted 67, less 2 self-hedged).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `hf.co/JackAgentLead/Jack-3.8-27B-Coder-16GB-VRAM:latest` |
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
| Branch / commit | `Jack-3.8-27B-Coder @ 1c6f8a7` |
