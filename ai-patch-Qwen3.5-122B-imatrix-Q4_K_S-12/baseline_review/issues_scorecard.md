# AI Review Scorecard

> **Branch:** `Qwen3.5-122B` &nbsp;·&nbsp; **Commit:** `c09505e`

Total: 54 Found / 3 Partial / 13 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query. | Found | "SQL injection via string interpolation in `Login` method." |
| C2 | Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "Hardcoded admin backdoor password bypasses authentication." |
| C3 | Broken password hashing — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Partial | "MD5 is cryptographically broken and unsuitable for password hashing." (Mentions MD5 weakness but omits the specific lack of salt). |
| C4 | SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "SQL injection in `UpdateUser` via string interpolation." and "SQL injection in `DeleteUser` via string interpolation." |
| C5 | SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "SQL injection in `SearchUsers` via `ExecuteQuery` with raw string." |
| C6 | SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "SQL injection in `Transfer` via string interpolation in `ExecuteNonQuery`." and "SQL injection in `Deposit` via string interpolation." |
| C7 | SQL Injection (RecordTransaction) — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "SQL injection in `RecordTransaction` via string interpolation." |
| C8 | Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "Production database credentials committed to source control." and "Email SMTP password committed to source control." |
| C9 | JWT lifetime validation disabled (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "JWT lifetime validation is disabled (`ValidateLifetime = false`)." |
| C10 | Broken Access Control — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | "Missing authorization check; any authenticated user can update any user." |
| C11 | Missing Authorization — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | "Missing authorization check; any authenticated user can delete any user." |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Missed | The review mentions balance checks and self-transfers but does not identify the zero-value transfer logic error. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "Balance check uses `amount` but deducts `amount + fee`, allowing negative balances." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "Pagination offset calculation is incorrect (`page * pageSize` instead of `(page - 1) * pageSize`)." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | "Deposit interest calculation multiplies by `1`, making the bonus equal to the amount (100% interest)." (Identifies the interest issue but mischaracterizes the specific bug as 100% interest rather than the wrong rate constant). |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | "No check to prevent users from transferring funds to themselves." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Missed | The review does not mention duplicated validation logic or the specific `ValidateUserId` extraction opportunity. |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "String concatenation in loop is O(n²)." (Referenced in Anti-patterns section for `StringHelper.cs`). |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed | The review does not mention the length or structure of `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "`SearchUsers` catches `Exception` and returns empty list, hiding errors." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | "`SendWelcomeEmail` swallows exceptions silently." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | "`Transfer` lacks database transaction for atomic balance updates." |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Missed | The review mentions the lack of DB transaction but does not specifically identify the exception propagation issue after commit in `Transfer`. |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | "`UpdateUser` returns raw `ex.Message` to client, leaking internal details." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | "`ExecuteNonQuery` opens connection but may leak on exception before `Close()`." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed | The review does not mention rate limiting or brute force protection. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "`SqlConnection` opened in `Login` but never closed/disposed." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "`GetOpenConnection` returns open connection without disposal contract." and "`ExecuteQuery` opens connection but never closes/disposes it." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "`ExecuteNonQuery` opens connection but may leak on exception before `Close()`." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "`SmtpClient` held as instance field; not thread-safe and may leak sockets." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "`MailMessage` created but never disposed." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | "`jwtSecret` may be null, causing `GetBytes` to throw." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "Accessing `Rows[0]` without checking `Rows.Count > 0`." (Referenced for `TransactionService.cs`). |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | "`int.Parse` on config value may throw if null/invalid." (Referenced for `EmailService.cs`). |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | The review does not specifically identify the null risk in `username.ToUpper()`. |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Missed | The review does not specifically identify the null risk in `StringHelper` length checks. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "`int.Parse` on `userIdClaim` may throw if claim is null." (Referenced for `TransactionController.cs`). |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Missed | The review does not specifically identify the null request body risk in `UpdateUser`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | "`TransactionFeeRate` is hardcoded." and "`MaxTransactionsPerDay` is hardcoded." |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | "Deposit limit `1000000` is hardcoded." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Missed | The review does not specifically identify the hardcoded email addresses. |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | "Email length limit `254` is hardcoded." and "Username length limits `3` and `20` are hardcoded." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "Page size limit `50` is hardcoded." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | "`HashPasswordSha1` is defined but never called." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "`ValidateToken` returns `true` immediately, ignoring actual token validation." |
| D3 | `TableExists` — never called from any service or controller. | Missed | The review does not mention `TableExists`. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | "`ExecuteQueryWithParams` is marked `[Obsolete]` but still present." |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | "`BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml` which is likely unused." |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Partial | The review mentions `BuildHtmlTemplate` usage but does not explicitly name `SendWelcomeEmailHtml` as dead/unused code itself, only implying it via the template usage. |
| D7 | `FormatCurrency` — private, never called. | Found | "`FormatCurrency` is defined but never called." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Missed | The review does not mention `IsWithinDailyLimit`. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | "`ObfuscateAccount` duplicates `MaskAccountNumber` functionality." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Missed | The review does not mention `ToTitleCase`. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "`JoinWithSeparator` is inefficient and likely unused; `JoinWithSeparatorFixed` exists." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | "Static mutable state `_auditLog` and `_requestCount` are not thread-safe." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "`new Regex` created on every call; should be static readonly." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "String concatenation in loop is O(n²)." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "`SmtpClient` held as instance field; not thread-safe and may leak sockets." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "`IsBlank` duplicates `string.IsNullOrWhiteSpace`." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "`GetOpenConnection` returns open connection without disposal contract." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "Production secrets in config file." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | "Debug log levels set for production namespaces." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "JWT lifetime validation is disabled (`ValidateLifetime = false`)." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "HTTPS redirection commented out." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "`UseDeveloperExceptionPage` called unconditionally." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "CORS allows any origin/method/header." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | "`DebugSymbols` and `DebugType` set in project file." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | "`Newtonsoft.Json` version `12.0.3` is outdated/vulnerable." |
| CF9 | *(missing)* | — | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Missed | The review does not mention the missing `appsettings.Production.json`. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login`, `AuthService.GenerateJwtToken`, `TransactionService.Transfer`, `TransactionService.Deposit`, `UserService.GetUsersPage`, `StringHelper`, Controller action results. | Found | "No test project exists. Critical areas to test: ... TransactionService.Transfer ... TransactionService.Deposit ... UserService.GetUsersPage ... AuthService.Login ... StringHelper ..." |