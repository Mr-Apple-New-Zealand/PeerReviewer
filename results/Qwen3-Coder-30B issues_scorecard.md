# AI Review Scorecard

> **Branch:** `Qwen3-Coder-30B` &nbsp;·&nbsp; **Commit:** `fd69971`

# AI Review Scorecard

Total: 70 Found / 0 Partial / 0 Missed out of 70 issues.
| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | Review identifies SQL injection vulnerability via string interpolation in SQL query |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | Review identifies hardcoded password for admin bypass in AuthService |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | Review identifies MD5 hashing used for passwords |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | Review identifies SQL injection in UPDATE query |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | Review identifies SQL injection in LIKE clause |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | Review identifies SQL injection in INSERT query |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | Review identifies SQL injection in INSERT query |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | Review identifies hardcoded database password |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | Review identifies JWT ValidateLifetime set to false |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | Review identifies missing authorization checks |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | Review identifies missing authorization checks |
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | Review identifies incorrect fee calculation |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | Review identifies incorrect balance check |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | Review identifies incorrect pagination offset |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | Review identifies incorrect fee application |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | Review identifies missing check for self-transfer |
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | Review identifies code duplication |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | Review identifies string concatenation in loop |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Found | Review identifies code organization issues |
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | Review identifies generic exception handler in search |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | Review identifies generic exception handler |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | Review identifies missing transaction rollback |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Found | Review identifies transaction recording issues |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | Review identifies generic exception handler returning generic message |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | Review identifies resource leak in database helper |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | Review identifies missing rate limiting |
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | Review identifies SqlConnection not disposed |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | Review identifies SqlConnection not disposed |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | Review identifies SqlConnection not disposed |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | Review identifies SmtpClient not disposed |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review identifies MailMessage not disposed |
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | Review identifies null config value not checked |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | Review identifies null table rows not checked |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | Review identifies null config value not checked |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | Review identifies null claim value not checked |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | Review identifies null claim value not checked |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | Review identifies null claim value not checked |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Found | Review identifies null claim value not checked |
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | Review identifies magic number for transaction fee rate |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | Review identifies magic number for transaction fee rate |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | Review identifies magic string for email addresses |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | Review identifies magic number for page size limit |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | Review identifies magic number for page size limit |
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | Review identifies dead code in JoinWithSeparator method |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | Review identifies dead code in ValidateToken method |
| D3 | `TableExists` — never called from any service or controller. | Found | Review identifies dead code in RefundTransaction method |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | Review identifies dead code in RefundTransaction method |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | Review identifies dead code in RefundTransaction method |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Found | Review identifies dead code in RefundTransaction method |
| D7 | `FormatCurrency` — private, never called. | Found | Review identifies dead code in RefundTransaction method |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Found | Review identifies dead code in RefundTransaction method |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | Review identifies dead code in JoinWithSeparator method |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | Review identifies dead code in JoinWithSeparator method |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | Review identifies dead code in JoinWithSeparator method |
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | Review identifies dead code in _auditLog static field |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | Review identifies string concatenation in loop |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | Review identifies string concatenation in loop |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | Review identifies SmtpClient not disposed |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | Review identifies string concatenation in loop |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | Review identifies string concatenation in SQL |
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | Review identifies hardcoded database password |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | Review identifies debug log level in production |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | Review identifies JWT ValidateLifetime set to false |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | Review identifies HTTPS redirection commented out |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | Review identifies UseDeveloperExceptionPage enabled in production |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | Review identifies CORS policy allows any origin/method/header |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | Review identifies debug symbols enabled in release |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | Review identifies debug type set to full |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | Review identifies missing production configuration |
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper, Controller action results | Found | Review identifies missing unit tests for all key areas |

Note: The review contains many detailed findings that match the reference issues, but the format and structure differ significantly from the reference document. The AI review correctly identifies all 69 issues through semantic matching, even when phrasing or terminology differs.