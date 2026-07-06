# AI Review Scorecard

> **Branch:** `Qwen3.6-27B` &nbsp;·&nbsp; **Commit:** `54a9e33`

Total: **59 Found / 0 Partial / 11 Missed** out of **70** issues.

Total: 59 Found / 0 Partial / 11 Missed out of 70 issues.

## Critical Security Vulnerabilities
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string‑interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | “AuthService.cs | ~30 | SQL query built with string interpolation (`SELECT * FROM Users WHERE Username = '{username}' …`) – vulnerable to SQL injection.” |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | “AuthService.cs | ~12 | Hard‑coded admin bypass password (`SuperAdmin2024`).” |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow‑table and credential‑stuffing attacks. | Found | “AuthService.cs | ~20 | Passwords hashed with MD5 – weak, unsalted cryptography.” |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string‑interpolated into UPDATE/DELETE statements. | Found | “UserService.cs | ~70 | `UpdateUser` builds raw SQL with interpolated `email`/`username`.” |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | “UserService.cs | ~100 | `SearchUsers` builds raw SQL with interpolated `query`.” |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, and `amount` all concatenated into UPDATE statements. | Found | “TransactionService.cs | ~30 | `Transfer` updates balances with interpolated values (`UPDATE Users SET Balance = {newFromBalance} …`).” |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | “TransactionService.cs | ~70 | `RecordTransaction` inserts raw values (`{description}`) via string interpolation – `description` may be null.” |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | “appsettings.json | ~8 | JWT secret key (`mysecretkey`) is short, predictable, and stored in source.” |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | “Program.cs | ~30 | JWT validation disables lifetime check (`ValidateLifetime = false`).” |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Missed |  |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Missed |  |

## Logic Errors
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero‑value transfers** (`amount == 0`). Should be `amount <= 0`. | Missed |  |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. | Found | “TransactionService.cs | ~20 | Balance check uses `fromBalance >= amount` but fee is deducted later (`totalDebit = amount + fee`).” |
| L3 | **Off‑by‑one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. | Found | “UserService.cs | ~30 | Pagination offset calculated as `page * pageSize` (off‑by‑one).” |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5 %) instead of intended `0.01m` (1 %). | Found | “TransactionService.cs | ~30 | Interest bonus rate (`0.05m`) is hard‑coded.” |
| L5 | **Self‑transfer allowed** — no check that `fromUserId != request.ToUserId`. | Found | “TransactionService.cs | ~10 | No check prevents transferring to oneself (`fromUserId == toUserId`).” |

## Refactoring Opportunities
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | Duplicated validation — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Missed |  |
| R2 | Loop string concatenation — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | “StringHelper.cs | ~20 | `JoinWithSeparator` builds a string with `+=` inside a loop (O(n²)).” |
| R3 | Overly long `GenerateJwtToken` — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Missed |  |

## Error Handling Inconsistencies
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | “UserService.cs | ~100 | `SearchUsers` catches all exceptions and returns empty list, hiding failures.” |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | “EmailService.cs | ~45 | `SendWelcomeEmail` catches generic `Exception` and only logs; caller assumes success.” |
| E3 | No database transaction around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | “Updates to two accounts are performed without a DB transaction – risk of partial update.” |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | “Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response.” |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Missed |  |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | “DatabaseHelper.cs | ~44 | `ExecuteNonQuery` creates `SqlConnection` and `SqlCommand` without disposing them (only `Close`).” |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Missed |  |

## Resource Leaks
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | “AuthService.cs | ~25 | `SqlConnection`, `SqlCommand`, `SqlDataReader` are never disposed.” |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | “DatabaseHelper.cs | ~12 | `GetOpenConnection` returns an open `SqlConnection` that callers often never dispose.” |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | “DatabaseHelper.cs | ~44 | `ExecuteNonQuery` creates `SqlConnection` and `SqlCommand` without disposing them (only `Close`).” |
| RL4 | `SmtpClient` held as an instance field on a non‑disposable service — underlying socket never released. | Found | “EmailService.cs | ~15 | `_smtpClient` is a long‑lived `SmtpClient` (IDisposable) never disposed.” |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | “EmailService.cs | ~30 | `MailMessage` instances are never disposed after sending.” |

## Missing Null Checks
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | “AuthService.cs | ~45 | `_config["Jwt:SecretKey"]` may be null; `Encoding.UTF8.GetBytes(null)` throws.” |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | “TransactionService.cs | ~20 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count`.” |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | “EmailService.cs | ~15 | Config values (`SmtpHost`, `SmtpPort`, `Username`, `Password`) may be null, causing runtime errors.” |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | “EmailService.cs | ~68 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`.” |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | “StringHelper.cs | ~5 & ~13 | `IsValidEmail` accesses `email.Length` without null guard.” |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null)` throws `ArgumentNullException`. | Found | “TransactionController.cs | ~9 | `User.FindFirst(... )` may return null; `int.Parse(userIdClaim!)` will throw.” |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | “UserController.cs | ~13 | `UpdateUserRequest` body may be null, causing NRE.” |

## Magic Strings & Numbers
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source‑code constants — should be in configuration. | Found | “TransactionService.cs | ~10 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` – magic fee rate.” |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | “TransactionService.cs | ~30 | Deposit amount upper bound `1000000`.” |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | “EmailService.cs | ~10 | Hard‑coded email addresses (`notifications@company.com`, `support@company.com`).” |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | “StringHelper.cs | ~14,24 | `254`, `3`, `20` used as bare literals.” |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | “UserService.cs | ~69 | `50` as the page size upper bound is unnamed.” |

## Dead Code
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | “AuthService.cs | ~55 | `HashPasswordSha1` is never called.” |
| D2 | Unreachable code after `return` in `ValidateToken`. | Found | “AuthService.cs | ~70 | `ValidateToken` returns early; the code after `return` is never executed.” |
| D3 | `TableExists` — never called from any service or controller. | Found | “DatabaseHelper.cs | ~70 | `TableExists` never called.” |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | “DatabaseHelper.cs | ~70 | `ExecuteQueryWithParams` is marked `[Obsolete]` and never called.” |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | “EmailService.cs | ~70 | `BuildHtmlTemplate` is never used.” |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Missed |  |
| D7 | `FormatCurrency` — private, never called. | Found | “TransactionService.cs | ~80 | `FormatCurrency` is never used.” |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | “TransactionService.cs | ~50 | `IsWithinDailyLimit` is defined but never invoked.” |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | “StringHelper.cs | ~45 | `ObfuscateAccount` is never referenced.” |
| D10 | `ToTitleCase` — “experimental utility never integrated”, never called. | Found | “StringHelper.cs | ~45 | `ToTitleCase` is never referenced.” |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Missed |  |

## Anti‑patterns
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread‑safe. | Found | “UserService.cs | ~5 | Static mutable fields `_auditLog` and `_requestCount` … not thread‑safe.” |
| A2 | **Regex compiled per‑call** — `new Regex(...)` inside instance methods allocates and JIT‑compiles a new automaton on every call. Should be `static readonly`. | Found | “StringHelper.cs | ~5 & ~13 | New `Regex` compiled on every call.” |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | “StringHelper.cs | ~20 | `JoinWithSeparator` builds a string with `+=` inside a loop (O(n²)).” |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread‑safe and should be created per‑send, not held as a field. | Found | “EmailService.cs | ~15 | `_smtpClient` is a long‑lived `SmtpClient` (IDisposable) never disposed.” |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Missed |  |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti‑pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | “DatabaseHelper.cs | ~12 | `GetOpenConnection` returns an open `SqlConnection` that callers often never dispose.” |

## Configuration Issues
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | “appsettings.json | ~8 | JWT secret key (`mysecretkey`) is short, predictable, and stored in source.” |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | “appsettings.json | ~20 | Logging level set to `Debug` for all categories.” |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | “Program.cs | ~30 | JWT validation disables lifetime check (`ValidateLifetime = false`).” |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | “Program.cs | ~42 | HTTPS redirection is commented out.” |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | “Program.cs | ~40 | `UseDeveloperExceptionPage()` runs in all environments.” |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | “Program.cs | ~38 | CORS policy `AllowAnyOrigin/AllowAnyMethod/AllowAnyHeader`.” |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | “SampleBankingApp.csproj | ~9 | `DebugSymbols = true` and `DebugType = full` for production.” |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Missed |  |
| CF9 | **No `appsettings.Production.json`** — no environment‑specific overrides; production uses the same unsafe defaults. | Found | “appsettings.json | – | No environment‑specific files (`appsettings.Development.json`, `appsettings.Production.json`).” |

## Missing Unit Tests
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, and controller action results. | Found | “The review notes that there is no test project and lists the areas that need tests.”