# Intentional Issues Reference

This file documents every deliberate flaw in `SampleBankingApp` for use as a peer-review agent test.
Issues are tagged by category, file, and approximate line numbers.

---

## Critical Security Vulnerabilities

| # | File | Lines | Description |
|---|------|-------|-------------|
| C1 | `Services/AuthService.cs` | ~35 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. |
| C2 | `Services/AuthService.cs` | ~49 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. |
| C3 | `Services/AuthService.cs` | ~56 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. |
| C4 | `Services/UserService.cs` | ~45, 60 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. |
| C5 | `Services/UserService.cs` | ~88 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. |
| C6 | `Services/TransactionService.cs` | ~50, 53 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. |
| C7 | `Services/TransactionService.cs` | ~82 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. |
| C8 | `appsettings.json` | all | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. |
| C9 | `Program.cs` | ~30 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. |
| C10 | `Controllers/UserController.cs` | ~53 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. |
| C11 | `Controllers/UserController.cs` | ~67 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. |

---

## Logic Errors

| # | File | Lines | Description |
|---|------|-------|-------------|
| L1 | `Services/TransactionService.cs` | ~25 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. |
| L2 | `Services/TransactionService.cs` | ~43 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. |
| L3 | `Services/UserService.cs` | ~73 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. |
| L4 | `Services/TransactionService.cs` | ~60 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. |
| L5 | `Controllers/TransactionController.cs` | ~26 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. |

---

## Refactoring Opportunities

| # | File | Lines | Description |
|---|------|-------|-------------|
| R1 | `Services/UserService.cs` | ~20, 38, 54 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. |
| R2 | `Helpers/StringHelper.cs` | ~28 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. |
| R3 | `Services/AuthService.cs` | ~71 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. |

---

## Error Handling Inconsistencies

| # | File | Lines | Description |
|---|------|-------|-------------|
| E1 | `Services/UserService.cs` | ~83 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". |
| E2 | `Services/EmailService.cs` | ~63 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. |
| E3 | `Services/TransactionService.cs` | ~55 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. |
| E4 | `Services/TransactionService.cs` | ~59 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. |
| E5 | `Controllers/UserController.cs` | ~58 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. |
| E6 | `Data/DatabaseHelper.cs` | ~44 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. |
| E7 | `Controllers/AuthController.cs` | ~20 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. |

---

## Resource Leaks

| # | File | Lines | Description |
|---|------|-------|-------------|
| RL1 | `Services/AuthService.cs` | ~37–38 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. |
| RL2 | `Data/DatabaseHelper.cs` | ~26 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. |
| RL3 | `Data/DatabaseHelper.cs` | ~44 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. |
| RL4 | `Services/EmailService.cs` | ~36 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. |
| RL5 | `Services/EmailService.cs` | ~49, 72 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. |

---

## Missing Null Checks

| # | File | Lines | Description |
|---|------|-------|-------------|
| N1 | `Services/AuthService.cs` | ~72 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. |
| N2 | `Services/TransactionService.cs` | ~35–36 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. |
| N3 | `Services/EmailService.cs` | ~46 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. |
| N4 | `Services/EmailService.cs` | ~68 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. |
| N5 | `Helpers/StringHelper.cs` | ~14, 24 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. |
| N6 | `Controllers/TransactionController.cs` | ~19, 31 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. |
| N7 | `Controllers/UserController.cs` | ~28 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. |

---

## Magic Strings & Numbers

| # | File | Lines | Description |
|---|------|-------|-------------|
| M1 | `Services/TransactionService.cs` | ~13–14 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. |
| M2 | `Services/TransactionService.cs` | ~60 | `1_000_000` deposit cap hardcoded inline — no named constant. |
| M3 | `Services/EmailService.cs` | ~14–15, 49, 72 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. |
| M4 | `Helpers/StringHelper.cs` | ~14, 24 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). |
| M5 | `Services/UserService.cs` | ~69 | `50` as the page size upper bound is unnamed and undocumented. |

---

## Dead Code

| # | File | Lines | Description |
|---|------|-------|-------------|
| D1 | `Services/AuthService.cs` | ~80 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. |
| D2 | `Services/AuthService.cs` | ~87–92 | Unreachable code after `return true` in `ValidateToken`. |
| D3 | `Data/DatabaseHelper.cs` | ~49 | `TableExists` — never called from any service or controller. |
| D4 | `Data/DatabaseHelper.cs` | ~56 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. |
| D5 | `Services/EmailService.cs` | ~79 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. |
| D6 | `Services/EmailService.cs` | ~85 | `SendWelcomeEmailHtml` — public method, never registered or called. |
| D7 | `Services/TransactionService.cs` | ~91 | `FormatCurrency` — private, never called. |
| D8 | `Services/TransactionService.cs` | ~72 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. |
| D9 | `Helpers/StringHelper.cs` | ~49 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. |
| D10 | `Helpers/StringHelper.cs` | ~54 | `ToTitleCase` — "experimental utility never integrated", never called. |
| D11 | `Helpers/StringHelper.cs` | ~37 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. |

---

## Anti-patterns

| # | File | Lines | Description |
|---|------|-------|-------------|
| A1 | `Services/UserService.cs` | ~15–16 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. |
| A2 | `Helpers/StringHelper.cs` | ~14, 24 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. |
| A3 | `Helpers/StringHelper.cs` | ~29 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. |
| A4 | `Services/EmailService.cs` | ~34 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. |
| A5 | `Helpers/StringHelper.cs` | ~60 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. |
| A6 | `Data/DatabaseHelper.cs` | ~26 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. |

---

## Configuration Issues

| # | File | Lines | Description |
|---|------|-------|-------------|
| CF1 | `appsettings.json` | all | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. |
| CF2 | `appsettings.json` | ~16–20 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. |
| CF3 | `Program.cs` | ~29 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. |
| CF4 | `Program.cs` | ~33 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. |
| CF5 | `Program.cs` | ~26 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. |
| CF6 | `Program.cs` | ~37 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. |
| CF7 | `SampleBankingApp.csproj` | ~7–10 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. |
| CF8 | `SampleBankingApp.csproj` | ~14 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. |
| CF9 | *(missing)* | — | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. |

---

## Missing Unit Tests

The project contains **no test project** and **no test files** whatsoever. Key areas that need tests include:

- `AuthService.Login` — SQL injection boundary cases, correct vs. incorrect password
- `AuthService.GenerateJwtToken` — claims mapping, expiry
- `TransactionService.Transfer` — zero amount, self-transfer, fee deduction, insufficient funds (with fee)
- `TransactionService.Deposit` — interest rate correctness
- `UserService.GetUsersPage` — pagination offset correctness (the off-by-one)
- `StringHelper` — null inputs, boundary lengths, separator trailing character
- Controller action results — correct HTTP status codes for various service responses
