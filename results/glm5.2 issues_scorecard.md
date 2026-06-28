# AI Review Scorecard

> **Branch:** `glm5.2` &nbsp;·&nbsp; **Commit:** `7b8e1bb`

Total: 60 Found / 5 Partial / 5 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | SampleBankingApp/Services/AuthService.cs line 34: "SQL injection vulnerability in `Login` method via interpolated username and password." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | SampleBankingApp/Services/AuthService.cs line 30: "Hardcoded backdoor admin password." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | SampleBankingApp/Services/AuthService.cs line 50: "Weak cryptography using MD5 for password hashing without salt." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | SampleBankingApp/Services/UserService.cs line 31: "SQL injection in `UpdateUser` via interpolated email and username." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | SampleBankingApp/Services/UserService.cs line 83: "SQL injection in `SearchUsers` via interpolated query string." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | SampleBankingApp/Services/TransactionService.cs line 41: "SQL injection in `Transfer` via interpolated balance and user ID." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | SampleBankingApp/Services/TransactionService.cs line 86: "SQL injection in `RecordTransaction` via interpolated values." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | SampleBankingApp/appsettings.json line 3: "Production database credentials committed to source control." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | SampleBankingApp/Program.cs line 19: "JWT `ValidateLifetime` set to false." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | SampleBankingApp/Controllers/UserController.cs line 34: "Broken access control allowing any user to update any other user." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | SampleBankingApp/Controllers/UserController.cs line 49: "Broken access control allowing any user to delete any other user." |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | SampleBankingApp/Services/TransactionService.cs line 23: "Missing self-referential check allows transferring to yourself." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | SampleBankingApp/Services/TransactionService.cs line 38: "Balance check excludes the transaction fee, allowing negative balances." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | SampleBankingApp/Services/UserService.cs line 56: "Pagination off-by-one error skips the first page." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | SampleBankingApp/Services/TransactionService.cs line 61: "Deposit applies a 5% interest bonus which is likely unintended." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | SampleBankingApp/Controllers/TransactionController.cs line 21: "int.Parse(userIdClaim!) will throw if the claim is missing." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | SampleBankingApp/Services/UserService.cs line 25: "Max user ID of `1000000` is hardcoded." |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Helpers/StringHelper.cs line 29: "JoinWithSeparator is broken and duplicated by `JoinWithSeparatorFixed`." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed |  |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | SampleBankingApp/Services/UserService.cs line 79: "`SearchUsers` catches broad `Exception` and returns empty list, hiding errors." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | SampleBankingApp/Services/EmailService.cs line 51: "SendWelcomeEmail calls `username.ToUpper()` without null check." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | SampleBankingApp/Services/TransactionService.cs line 33: "Transfer lacks a database transaction, risking inconsistent balances." |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response.** | Found | SampleBankingApp/Services/TransactionService.cs line 48: "Email sending side effect occurs after DB writes and can throw unhandled." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | SampleBankingApp/Controllers/UserController.cs line 38: "`UpdateUser` catches broad `Exception` and returns raw `ex.Message` to client." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 40: "ExecuteNonQuery leaks `SqlConnection` and `SqlCommand` resources." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | SampleBankingApp/Controllers/AuthController.cs line 21: "Missing rate limiting or account lockout on login endpoint." |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | SampleBankingApp/Services/AuthService.cs line 34: "`SqlConnection` and `SqlCommand` in `Login` are never disposed." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 28: "`ExecuteQuery` leaks `SqlConnection` and `SqlCommand` resources." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 40: "ExecuteNonQuery leaks `SqlConnection` and `SqlCommand` resources." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | SampleBankingApp/Services/EmailService.cs line 16: "`SmtpClient` is held as an instance field and never disposed." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | SampleBankingApp/Services/EmailService.cs line 33: "`MailMessage` objects are never disposed." |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | SampleBankingApp/Program.cs line 21: "jwtSecret is passed to `Encoding.UTF8.GetBytes` with a null-forgiving operator but could be null." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | SampleBankingApp/Services/TransactionService.cs line 29: "`fromUserTable.Rows[0]` is accessed without checking if rows exist." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | SampleBankingApp/Services/EmailService.cs line 14: "_config["Email:SmtpHost"] could be null and passed to `SmtpClient` constructor." |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | SampleBankingApp/Services/EmailService.cs line 51: "SendWelcomeEmail calls `username.ToUpper()` without null check." |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | SampleBankingApp/Helpers/StringHelper.cs line 11: "IsValidEmail calls `.Length` on parameter without null check." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | SampleBankingApp/Controllers/TransactionController.cs line 21: "int.Parse(userIdClaim!) will throw if the claim is missing." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | SampleBankingApp/Controllers/UserController.cs line 34: "Broken access control allowing any user to update any other user." |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | SampleBankingApp/Services/TransactionService.cs line 60: "Deposit cap of `1000000` is hardcoded." |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | SampleBankingApp/Services/TransactionService.cs line 60: "Deposit cap of `1000000` is hardcoded." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | SampleBankingApp/Services/EmailService.cs line 33: "\"notifications@company.com\" is hardcoded in multiple places." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | SampleBankingApp/Helpers/StringHelper.cs line 11: "IsValidEmail calls `.Length` on parameter without null check." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | SampleBankingApp/Services/UserService.cs line 55: "Max page size of `50` is hardcoded." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | SampleBankingApp/Services/AuthService.cs line 66: "`HashPasswordSha1` is never called." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | SampleBankingApp/Services/AuthService.cs line 71: "Unreachable code after unconditional `return true;` in `ValidateToken`." |
| D3 | `TableExists` — never called from any service or controller. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 57: "`ExecuteQueryWithParams` is marked obsolete and never called." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 57: "`ExecuteQueryWithParams` is marked obsolete and never called." |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Missed |  |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Missed |  |
| D7 | `FormatCurrency` — private, never called. | Found | SampleBankingApp/Services/TransactionService.cs line 94: "`FormatCurrency` is never called." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | SampleBankingApp/Services/TransactionService.cs line 72: "`IsWithinDailyLimit` is never called." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Missed |  |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Missed |  |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | SampleBankingApp/Helpers/StringHelper.cs line 29: "JoinWithSeparator is broken and duplicated by `JoinWithSeparatorFixed`." |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | SampleBankingApp/Services/UserService.cs line 9: "Shared mutable static state `_auditLog` and `_requestCount` accessed without synchronization." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | SampleBankingApp/Helpers/StringHelper.cs line 13: "`new Regex(...)` is instantiated inside methods called repeatedly." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | SampleBankingApp/Services/UserService.cs line 66: "GetAuditReport uses string concatenation in a loop." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | SampleBankingApp/Services/EmailService.cs line 16: "`SmtpClient` is held as an instance field and never disposed." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Partial | SampleBankingApp/Helpers/StringHelper.cs line 60: "Reimplementing BCL" |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | SampleBankingApp/Data/DatabaseHelper.cs line 19: "GetOpenConnection leaks resource ownership to callers with no documented contract." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | SampleBankingApp/appsettings.json line 3: "Production database credentials committed to source control." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | SampleBankingApp/appsettings.json line 21: "Debug log levels set for production namespaces." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | SampleBankingApp/Program.cs line 19: "JWT `ValidateLifetime` set to false." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | SampleBankingApp/Program.cs line 31: "HTTPS redirection is commented out." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | SampleBankingApp/Program.cs line 27: "`UseDeveloperExceptionPage()` called unconditionally." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | SampleBankingApp/Program.cs line 29: "Overly permissive CORS policy." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | SampleBankingApp/SampleBankingApp.csproj line 9: "Debug symbols set to full for release builds." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | SampleBankingApp/SampleBankingApp.csproj line 8: "Outdated or vulnerable NuGet package `Newtonsoft.Json` 12.0.3." |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | SampleBankingApp/appsettings.json line N/A: "Missing environment-specific config overrides." |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | **No test project** — the project contains no test files or test project at all. Key areas that need tests include: `AuthService.Login`, `TransactionService.Transfer`, `UserService.GetUsersPage`, etc. | Found | SampleBankingApp/SampleBankingApp.csproj line N/A: "No test project exists." |