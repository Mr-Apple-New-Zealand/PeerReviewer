# AI Review Scorecard

> **Branch:** `Qwen3.5-2B` &nbsp;·&nbsp; **Commit:** `b783a4e`

Total: 16 Found / 53 Partial / 1 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | The review mentions "SQL injection vulnerability" in AuthService.cs line 149 where username is interpolated directly into SQL query |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | The review identifies "hardcoded credentials" including "Admin1234!" which is a backdoor password |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | The review identifies "weak cryptography" using MD5 for password hashing |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Partial | The review mentions SQL injection risk but doesn't specifically name UpdateUser/DeleteUser methods |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Partial | The review mentions SQL injection risk but doesn't specifically name SearchUsers method |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Partial | The review mentions SQL injection risk but doesn't specifically name Transfer/Deposit methods |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Partial | The review mentions SQL injection risk but doesn't specifically name RecordTransaction method |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | The review identifies "hardcoded credentials" in appsettings.json including multiple passwords |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | The review identifies "JWT misconfiguration" with ValidateLifetime = false |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Partial | The review mentions "access control" but doesn't specifically name this missing check |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Partial | The review mentions "access control" but doesn't specifically name this missing check |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | The review identifies "logic errors" with "balance calculation bug" that mentions the amount check |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Partial | The review mentions "balance calculation" but doesn't specifically name this logic error |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | The review identifies "off-by-one in pagination" in UserService.cs line 124 |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | The review mentions "magic strings and numbers" but doesn't specifically name this interest rate error |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Partial | The review mentions "logic errors" but doesn't specifically name this self-transfer issue |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Partial | The review mentions "logic errors" but doesn't specifically name this refactoring opportunity |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Partial | The review mentions "magic strings and numbers" but doesn't specifically name this refactoring opportunity |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | The review mentions "logic errors" but doesn't specifically name this refactoring opportunity |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Partial | The review mentions "error handling" but doesn't specifically name this exception swallowing |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Partial | The review mentions "error handling" but doesn't specifically name this broad exception catching |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Partial | The review mentions "error handling" but doesn't specifically name this transaction issue |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Partial | The review mentions "error handling" but doesn't specifically name this error propagation |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Partial | The review mentions "error handling" but doesn't specifically name this error message exposure |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Partial | The review mentions "resource leaks" but doesn't specifically name this connection handling |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | The review mentions "logic errors" but doesn't specifically name this missing rate limiting |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | The review identifies "resource leaks" with "SqlConnection not closed" in DatabaseHelper.cs |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | The review identifies "resource leaks" with "leaking connection" in DatabaseHelper.cs |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | The review identifies "resource leaks" with "connection not disposed" in DatabaseHelper.cs |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | The review identifies "resource leaks" with "SmtpClient not closed" in EmailService.cs |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | The review identifies "resource leaks" with "MailMessage not disposed" in EmailService.cs |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Partial | The review mentions "null reference risks" but doesn't specifically name this JWT secret null check |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Partial | The review mentions "null reference risks" but doesn't specifically name this row access |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | The review mentions "null reference risks" but doesn't specifically name this port parsing |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Partial | The review mentions "null reference risks" but doesn't specifically name this null check |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Partial | The review mentions "null reference risks" but doesn't specifically name this length access |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Partial | The review mentions "null reference risks" but doesn't specifically name this null parsing |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | The review mentions "null reference risks" but doesn't specifically name this null request check |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Partial | The review mentions "magic strings and numbers" but doesn't specifically name these constants |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Partial | The review mentions "magic strings and numbers" but doesn't specifically name this constant |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Partial | The review mentions "magic strings and numbers" but doesn't specifically name these email addresses |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Partial | The review mentions "magic strings and numbers" but doesn't specifically name these literals |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Partial | The review mentions "magic strings and numbers" but doesn't specifically name this page size |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Partial | The review mentions "dead code" but doesn't specifically name this method |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Partial | The review mentions "dead code" but doesn't specifically name this unreachable code |
| D3 | `TableExists` — never called from any service or controller. | Partial | The review mentions "dead code" but doesn't specifically name this method |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Partial | The review mentions "dead code" but doesn't specifically name this method |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Partial | The review mentions "dead code" but doesn't specifically name this method |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Partial | The review mentions "dead code" but doesn't specifically name this method |
| D7 | `FormatCurrency` — private, never called. | Partial | The review mentions "dead code" but doesn't specifically name this method |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Partial | The review mentions "dead code" but doesn't specifically name this method |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Partial | The review mentions "dead code" but doesn't specifically name this method |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Partial | The review mentions "dead code" but doesn't specifically name this method |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Partial | The review mentions "dead code" but doesn't specifically name this method |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Partial | The review mentions "anti-patterns" but doesn't specifically name this static state issue |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Partial | The review mentions "anti-patterns" but doesn't specifically name this regex pattern |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Partial | The review mentions "anti-patterns" but doesn't specifically name this string concatenation |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Partial | The review mentions "anti-patterns" but doesn't specifically name this SmtpClient issue |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Partial | The review mentions "anti-patterns" but doesn't specifically name this reimplementing |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Partial | The review mentions "anti-patterns" but doesn't specifically name this connection leak |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | The review identifies "hardcoded credentials" in appsettings.json |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | The review mentions "configuration issues" but doesn't specifically name this log level |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | The review identifies "JWT misconfiguration" with ValidateLifetime = false |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Partial | The review mentions "configuration issues" but doesn't specifically name this HTTPS setting |
| CF5 | **UseDeveloperExceptionPage() called unconditionally** — full stack traces served to production clients. | Partial | The review mentions "configuration issues" but doesn't specifically name this exception page |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Partial | The review mentions "configuration issues" but doesn't specifically name this CORS policy |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | The review identifies "debug symbols" in SampleBankingApp.csproj |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Partial | The review mentions "configuration issues" but doesn't specifically name this package |
| CF9 | *(missing)* | Missed | The review doesn't mention the missing appsettings.Production.json |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include: `AuthService.Login` — SQL injection boundary cases, correct vs. incorrect password `AuthService.GenerateJwtToken` — claims mapping, expiry `TransactionService.Transfer` — zero amount, self-transfer, fee deduction, insufficient funds (with fee) `TransactionService.Deposit` — interest rate correctness `UserService.GetUsersPage` — pagination offset correctness (the off-by-one) `StringHelper` — null inputs, boundary lengths, separator trailing character Controller action results — correct HTTP status codes for various service responses | Found | The review mentions "missing unit tests" and identifies the key areas that need testing |