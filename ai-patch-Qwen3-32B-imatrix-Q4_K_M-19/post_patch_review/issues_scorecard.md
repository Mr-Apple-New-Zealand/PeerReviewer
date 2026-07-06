# AI Review Scorecard

> **Branch:** `Qwen3-32B` &nbsp;·&nbsp; **Commit:** `52391af`

Total: 19 Found / 3 Partial / 48 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query. | Missed | The review mentions MD5 and hardcoded credentials but does not identify SQL injection in `Login`. |
| C2 | Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Missed | The review mentions hardcoded credentials generally but does not name `AdminBypassPassword` or the backdoor logic. |
| C3 | Broken password hashing — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "Uses MD5 for password hashing, which is cryptographically broken." and "Passwords are hashed without a salt..." |
| C4 | SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Missed | No mention of SQL injection in `UserService` or specific methods. |
| C5 | SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Missed | No mention of SQL injection in `SearchUsers`. |
| C6 | SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Missed | No mention of SQL injection in `TransactionService`. |
| C7 | SQL Injection (RecordTransaction) — `description` is interpolated; a malicious description can inject arbitrary SQL. | Missed | No mention of SQL injection in `RecordTransaction`. |
| C8 | Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed to source control. | Partial | "Hardcoded fallback credentials in connection string" and "JWT secret key is loaded from config" touch on secrets but don't explicitly flag `appsettings.json` as containing committed production secrets for all services. |
| C9 | JWT lifetime validation disabled (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Missed | The review mentions JWT secret validation but not `ValidateLifetime = false`. |
| C10 | Broken Access Control — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Missed | The review mentions `GetUser` lacks ownership checks (C10 is about `UpdateUser`/PUT). It does not mention `UpdateUser` access control. |
| C11 | Missing Authorization — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Missed | No mention of missing authorization on `DELETE /api/user/{id}`. |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Missed | No mention of zero-value transfer logic error. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Missed | The review mentions fee deduction recording but not the balance check logic error allowing negative balances. |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Missed | No mention of pagination off-by-one error. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Missed | The review mentions interest bonus recording but not the incorrect rate value. |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Missed | No mention of self-transfer logic error. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Missed | The review mentions `ValidateUserId` throws exception but not the duplication/refactoring opportunity. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "String concatenation in a loop is O(n²)." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | No mention of `GenerateJwtToken` being overly long or needing refactoring. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Missed | No mention of `SearchUsers` swallowing exceptions. |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Missed | The review mentions `SmtpException` handling but not broad `Exception` catch in `SendWelcomeEmail`. |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | "Multiple database queries are executed separately instead of using a single transaction." |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Missed | No mention of email failure propagating after commit. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Missed | No mention of exposing `ex.Message` to clients. |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Missed | No mention of `ExecuteNonQuery` connection closing logic. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed | No mention of rate limiting or brute force protection. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Missed | No mention of resource leaks in `Login`. |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "`GetOpenConnection` returns an open connection without disposing it, leaking resources." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Missed | No mention of `ExecuteNonQuery` disposal issues. |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "`SmtpClient` is not disposed if an exception occurs before `Send`." and "Shared mutable `SmtpClient`" |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Missed | The review mentions `MailMessage` disposal in `finally` but doesn't flag it as a leak in the specific methods named. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | "`_config["Jwt:SecretKey"]` can be null, causing `GetBytes` to throw." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Missed | No mention of `Rows[0]` access without count check. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | "`_config["Email:SmtpPort"]` can be null, causing `int.Parse` to throw." |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | No mention of `username.ToUpper()` null check. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Missed | No mention of null guards for `Length` access. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "`userIdClaim` can be null, causing `int.Parse` to throw `NullReferenceException`." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Missed | No mention of null request body checks. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Partial | "Fee rate and max deposit are read from config but not validated or documented." (Contradicts reference saying they are source-code constants, but addresses the config concern). |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Missed | No mention of hardcoded deposit cap. |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Missed | No mention of hardcoded email addresses. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Missed | No mention of bare literals in `StringHelper`. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "Page size limit of 50 is hardcoded." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Missed | No mention of `HashPasswordSha1`. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Missed | No mention of unreachable code in `ValidateToken`. |
| D3 | `TableExists` — never called from any service or controller. | Missed | No mention of `TableExists`. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Missed | No mention of `ExecuteQueryWithParams`. |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Missed | No mention of `BuildHtmlTemplate`. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Missed | No mention of `SendWelcomeEmailHtml`. |
| D7 | `FormatCurrency` — private, never called. | Missed | No mention of `FormatCurrency`. |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Missed | No mention of `IsWithinDailyLimit`. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | "`ObfuscateAccount` is a duplicate of `MaskAccountNumber` and is never called." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Missed | No mention of `ToTitleCase`. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "`JoinWithSeparatorFixed` is a duplicate of `string.Join` and is never called." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Missed | No mention of mutable static state. |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "`new Regex` is created on every call, causing performance issues." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "String concatenation in a loop is O(n²)." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "Shared mutable `SmtpClient`" |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "`IsBlank` duplicates `string.IsNullOrWhiteSpace` and is never called." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "`GetOpenConnection` returns an open connection without disposing it, leaking resources." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Partial | "Hardcoded fallback credentials in connection string" and "JWT secret key is loaded from config" touch on secrets but don't explicitly flag `appsettings.json` as containing committed production secrets for all services. |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Missed | No mention of log level configuration. |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Missed | No mention of `ValidateLifetime = false`. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Missed | No mention of HTTPS redirection. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Missed | No mention of developer exception page. |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "CORS policy allows any method and header, which is overly permissive." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Missed | No mention of debug symbols in release builds. |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | "`Newtonsoft.Json` version 12.0.3 is outdated and may have vulnerabilities." |
| CF9 | *(missing)* | — | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Missed | No mention of missing production config file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, Controller action results. | Found | "No test project exists for the application." and specific mentions of testing financial calculations, login/token logic, and user CRUD/pagination. |