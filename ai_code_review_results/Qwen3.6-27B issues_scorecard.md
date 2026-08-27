# AI Review Scorecard

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22`

> ⚠ **5 row(s) rated Found name a target that never appears in the review** (N3, D9, D10, CF9, N4). Adjusted Found: **65** of 70. See the spot-check below.

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | The review identifies that the `Login` method constructs SQL queries using string interpolation, allowing SQL injection via the `username` and `password` parameters. |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | The review identifies that a hardcoded backdoor password `SuperAdmin2024` allows bypassing authentication for the admin user. |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | The review identifies that the `HashPasswordMd5` method uses MD5, which is cryptographically broken and unsuitable for password hashing. |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | The review identifies that the `UpdateUser` method constructs SQL update statements using string interpolation, allowing SQL injection via `email` and `username`. |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | The review identifies that the `SearchUsers` method passes user input directly to `ExecuteQuery`, which uses string interpolation for the WHERE clause. |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | The review identifies that the `Transfer` method constructs SQL update statements using string interpolation, allowing SQL injection via `fromUserId`. |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | The review identifies that the `RecordTransaction` method constructs SQL insert statements using string interpolation, allowing SQL injection via `description`. |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | The review identifies that production database credentials are hardcoded in the configuration file committed to source control. |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | The review identifies that JWT validation is configured with `ValidateLifetime = false`, meaning tokens never expire. |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | The review identifies that the `DeleteUser` endpoint lacks an ownership check, allowing any authenticated user to delete any other user. |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | The review identifies that the `DeleteUser` endpoint lacks an ownership check, allowing any authenticated user to delete any other user. |

## Logic Errors

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | The review identifies that the balance check verifies `fromBalance >= amount` but deducts `amount + fee`, potentially resulting in a negative balance. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | The review identifies that the balance check verifies `fromBalance >= amount` but deducts `amount + fee`, potentially resulting in a negative balance. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | The review identifies that the pagination logic calculates `skip = page * pageSize`, causing the first page of results to be skipped. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | The review identifies that the deposit interest calculation multiplies by `0.05m * 1`, where the `* 1` is redundant and confusing. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | The review identifies that the `Transfer` method does not check if `fromUserId` equals `toUserId`, allowing users to transfer funds to themselves. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | The review identifies that the `UpdateUser` method constructs SQL update statements using string interpolation, allowing SQL injection via `email` and `username`. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | The review identifies that the `JoinWithSeparator` method uses string concatenation in a loop, resulting in O(n²) performance. |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | The review identifies that the `GenerateJwtToken` method uses the null-forgiving operator `!` on the config key, risking a NullReferenceException if the key is missing. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | The review identifies that the `SearchUsers` method catches all exceptions and returns an empty list, masking errors from the caller. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | The review identifies that the `SendWelcomeEmail` method creates a `MailMessage` but never disposes of it. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | The review identifies that the `Transfer` method performs two separate database updates without a transaction, risking data inconsistency if the second fails. |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | The review identifies that the `Transfer` method sends an email notification after the database commit, meaning a failure here leaves the user in an inconsistent state regarding notification. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | The review identifies that the `UpdateUser` catch block returns `ex.Message` to the client, leaking internal implementation details. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | The review identifies that the `ExecuteNonQuery` method accepts a raw SQL string, which callers populate via string interpolation, enabling SQL injection. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | The review identifies that the `Login` endpoint lacks rate limiting or account lockout mechanisms, making it vulnerable to brute-force attacks. |

## Resource Leaks

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | The review identifies that the `Login` method opens a `SqlConnection` but never closes or disposes of it, leading to connection pool exhaustion. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | The review identifies that the `GetOpenConnection` method returns an open connection, shifting disposal responsibility to the caller without documentation. |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | The review identifies that the `ExecuteNonQuery` method accepts a raw SQL string, which callers populate via string interpolation, enabling SQL injection. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | The review identifies that the `_smtpClient` is stored as an instance field, which is not thread-safe and can lead to socket leaks in a web environment. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | The review identifies that the `SendTransferNotification` method creates a `MailMessage` but never disposes of it. |

## Missing Null Checks

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | The review identifies that the `GenerateJwtToken` method uses the null-forgiving operator `!` on the config key, risking a NullReferenceException if the key is missing. |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | The review identifies that the `Transfer` method accesses `fromUserTable.Rows[0]` without checking if `Rows.Count > 0`, risking an IndexOutOfRangeException. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | The review identifies that the `SendWelcomeEmail` method creates a `MailMessage` but never disposes of it. |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | The review identifies that the `SendWelcomeEmail` method creates a `MailMessage` but never disposes of it. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | The review identifies that the `SendWelcomeEmail` method creates a `MailMessage` but never disposes of it. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | The review identifies that the `Transfer` method uses the null-forgiving operator `!` on `userIdClaim`, risking a NullReferenceException if the claim is missing. |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | The review identifies that the `UpdateUser` catch block returns `ex.Message` to the client, leaking internal implementation details. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | The review identifies that the fee rate `0.015m` is hardcoded inline. |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | The review identifies that the limit `1000000` is hardcoded for max deposit amount. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | The review identifies that the string "admin" is hardcoded to check for the admin username. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | The review identifies that the limits `3` and `20` are hardcoded for username length validation. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | The review identifies that the limit `50` is hardcoded for page size. |

## Dead Code

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | The review identifies that the `HashPasswordSha1` method is defined but never called anywhere in the codebase. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | The review identifies that the code following `return true` in `ValidateToken` is unreachable. |
| D3 | `TableExists` — never called from any service or controller. | Found | The review identifies that the `TableExists` method is defined but never called anywhere in the codebase. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | The review identifies that the `ExecuteQueryWithParams` method is marked `[Obsolete]` but remains in the codebase. |
| D5 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Found | The review identifies that the `BuildHtmlTemplate` method is defined but never called anywhere in the codebase. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | The review identifies that the `SendWelcomeEmailHtml` method is defined but never called anywhere in the codebase. |
| D7 | `FormatCurrency` — private, never called. | Found | The review identifies that the `FormatCurrency` method is defined but never called anywhere in the codebase. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | The review identifies that the `IsWithinDailyLimit` method is defined but never called anywhere in the codebase. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | The review identifies that the `JoinWithSeparatorFixed` method is defined but never called anywhere in the codebase. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | The review identifies that the `JoinWithSeparator` method is defined but never called anywhere in the codebase. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | The review identifies that the `JoinWithSeparatorFixed` method is defined but never called anywhere in the codebase. |

## Anti-patterns

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | The review identifies that the `_auditLog` and `_requestCount` fields are static mutable state, risking thread safety issues. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | The review identifies that the `IsValidEmail` method creates a new `Regex` instance on every call, causing performance overhead. |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | The review identifies that the `JoinWithSeparator` method uses string concatenation in a loop, resulting in O(n²) performance. |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | The review identifies that the `_smtpClient` is stored as an instance field, which is not thread-safe and can lead to socket leaks in a web environment. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | The review identifies that the `IsBlank` method reimplements logic already provided by `string.IsNullOrWhiteSpace`. |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | The review identifies that the `GetOpenConnection` method returns an open connection, shifting disposal responsibility to the caller without documentation. |

## Configuration Issues

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | The review identifies that production database credentials are hardcoded in the configuration file committed to source control. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | The review identifies that the logging level is set to "Debug" for all namespaces, which is excessive for production. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | The review identifies that JWT validation is configured with `ValidateLifetime = false`, meaning tokens never expire. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | The review identifies that HTTPS redirection is commented out, allowing traffic to be transmitted over unencrypted HTTP. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | The review identifies that `UseDeveloperExceptionPage()` is enabled unconditionally, exposing stack traces in production. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | The review identifies that the CORS policy allows any origin, method, and header, exposing the API to cross-site request forgery and data theft. |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | The review identifies that `DebugSymbols` is set to true, which is inappropriate for production builds. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | The review identifies that the `Newtonsoft.Json` package version 12.0.3 is outdated and may contain known vulnerabilities. |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | The review identifies that no test project exists in the repository. |

## Missing Unit Tests

| ID | Description | Status | Notes |
| :--- | :--- | :--- | :--- |
| UT | No test project exists in the repository. | Found | The review identifies that no test project exists in the repository. |
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
| D9 | Found | `ObfuscateAccount` | **no** | **MIS-CREDIT** |
| D10 | Found | `ToTitleCase` | **no** | **MIS-CREDIT** |
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
| N2 | Found | `Rows[0]` | yes | - |
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
| CF8 | Found | `Newtonsoft` | yes | - |

**Adjusted Found: 65 of 70** (70 reported, less 5 mis-credited).

---

## Run Configuration

Values as actually sent to Ollama for this run. Blank sampler entries mean the request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Review model | `Qwen3.6-27B:Q4_K_S` |
| Reasoning strength (system prompt) | (model default) |
| System prompt | `You are an expert computer programmer with an eye for detail, who loves to provide high quality answers.` |
| Ollama `think` | `medium` |
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
| Review citations past end of file | `0 of 72` |
| Precision (checkable Found rows) | `88% (35 of 40)` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Branch / commit | `main @ 67ece22` |
