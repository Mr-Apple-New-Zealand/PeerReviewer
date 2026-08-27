# Code Review — SampleBankingApp

The following issues were identified during review of the full source tree.


## Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Services/AuthService.cs | ~35 | SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Address as described. |
| Services/AuthService.cs | ~49 | Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Address as described. |
| Services/AuthService.cs | ~56 | Broken password hashing — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Address as described. |
| Services/UserService.cs | ~45, 60 | SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Address as described. |
| Services/UserService.cs | ~88 | SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Address as described. |
| Services/TransactionService.cs | ~50, 53 | SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Address as described. |
| Services/TransactionService.cs | ~82 | SQL Injection (RecordTransaction) — `description` is interpolated; a malicious description can inject arbitrary SQL. | Address as described. |
| appsettings.json | all | Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed to source control. | Address as described. |
| Program.cs | ~30 | JWT lifetime validation disabled (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Address as described. |
| Controllers/UserController.cs | ~53 | Broken Access Control — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Address as described. |
| Controllers/UserController.cs | ~67 | Missing Authorization — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Address as described. |

## Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Services/TransactionService.cs | ~25 | `amount < 0` check allows zero-value transfers (`amount == 0`). Should be `amount <= 0`. | Address as described. |
| Services/TransactionService.cs | ~43 | Balance check excludes the fee — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Address as described. |
| Services/UserService.cs | ~73 | Off-by-one in pagination — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Address as described. |
| Services/TransactionService.cs | ~60 | Incorrect interest rate — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Address as described. |
| Controllers/TransactionController.cs | ~26 | Self-transfer allowed — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Address as described. |

## Refactoring Opportunities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Services/UserService.cs | ~20, 38, 54 | Duplicated validation — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Address as described. |
| Helpers/StringHelper.cs | ~28 | Loop string concatenation — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Address as described. |
| Services/AuthService.cs | ~71 | Overly long `GenerateJwtToken` — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Address as described. |

## Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Services/UserService.cs | ~83 | `SearchUsers` swallows all exceptions and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Address as described. |
| Services/EmailService.cs | ~63 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Address as described. |
| Services/TransactionService.cs | ~55 | No database transaction around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Address as described. |
| Services/TransactionService.cs | ~59 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response. | Address as described. |
| Controllers/UserController.cs | ~58 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Address as described. |
| Data/DatabaseHelper.cs | ~44 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Address as described. |
| Controllers/AuthController.cs | ~20 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Address as described. |

## Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Services/AuthService.cs | ~37–38 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Address as described. |
| Data/DatabaseHelper.cs | ~26 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Address as described. |
| Data/DatabaseHelper.cs | ~44 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Address as described. |
| Services/EmailService.cs | ~36 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Address as described. |
| Services/EmailService.cs | ~49, 72 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Address as described. |

## Missing Null Checks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Services/AuthService.cs | ~72 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Address as described. |
| Services/TransactionService.cs | ~35–36 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Address as described. |
| Services/EmailService.cs | ~46 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Address as described. |
| Services/EmailService.cs | ~68 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Address as described. |
| Helpers/StringHelper.cs | ~14, 24 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Address as described. |
| Controllers/TransactionController.cs | ~19, 31 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Address as described. |
| Controllers/UserController.cs | ~28 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Address as described. |

## Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Services/TransactionService.cs | ~13–14 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Address as described. |
| Services/TransactionService.cs | ~60 | `1_000_000` deposit cap hardcoded inline — no named constant. | Address as described. |
| Services/EmailService.cs | ~14–15, 49, 72 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Address as described. |
| Helpers/StringHelper.cs | ~14, 24 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Address as described. |
| Services/UserService.cs | ~69 | `50` as the page size upper bound is unnamed and undocumented. | Address as described. |

## Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Services/AuthService.cs | ~80 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Address as described. |
| Services/AuthService.cs | ~87–92 | Unreachable code after `return true` in `ValidateToken`. | Address as described. |
| Data/DatabaseHelper.cs | ~49 | `TableExists` — never called from any service or controller. | Address as described. |
| Data/DatabaseHelper.cs | ~56 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Address as described. |
| Services/EmailService.cs | ~79 | `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked. | Address as described. |
| Services/EmailService.cs | ~85 | `SendWelcomeEmailHtml` — public method, never registered or called. | Address as described. |
| Services/TransactionService.cs | ~91 | `FormatCurrency` — private, never called. | Address as described. |
| Services/TransactionService.cs | ~72 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Address as described. |
| Helpers/StringHelper.cs | ~49 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Address as described. |
| Helpers/StringHelper.cs | ~54 | `ToTitleCase` — "experimental utility never integrated", never called. | Address as described. |
| Helpers/StringHelper.cs | ~37 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Address as described. |

## Anti-patterns

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Services/UserService.cs | ~15–16 | Mutable static state — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Address as described. |
| Helpers/StringHelper.cs | ~14, 24 | Regex compiled per-call — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Address as described. |
| Helpers/StringHelper.cs | ~29 | String concatenation in loop — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Address as described. |
| Services/EmailService.cs | ~34 | Shared mutable `SmtpClient` — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Address as described. |
| Helpers/StringHelper.cs | ~60 | Reimplementing BCL — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Address as described. |
| Data/DatabaseHelper.cs | ~26 | Leaking connection — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Address as described. |

## Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| appsettings.json | all | Production secrets in source control — DB password, JWT secret, SMTP password all present. | Address as described. |
| appsettings.json | ~16–20 | Log level `Debug` in production — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Address as described. |
| Program.cs | ~29 | JWT `ValidateLifetime = false` — tokens never expire regardless of the `expires` field. | Address as described. |
| Program.cs | ~33 | HTTPS disabled — `UseHttpsRedirection()` commented out. | Address as described. |
| Program.cs | ~26 | `UseDeveloperExceptionPage()` called unconditionally — full stack traces served to production clients. | Address as described. |
| Program.cs | ~37 | Open CORS policy — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Address as described. |
| SampleBankingApp.csproj | ~7–10 | `DebugSymbols = true` / `DebugType = full` always emitted — PDB files shipped with release builds. | Address as described. |
| SampleBankingApp.csproj | ~14 | Pinned outdated package — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Address as described. |
| (project root) | — | No `appsettings.Production.json` — no environment-specific overrides; production uses the same unsafe defaults. | Address as described. |

## Missing Unit Tests

The project contains no test project and no test files of any kind. AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper methods, and all controller actions lack any test coverage whatsoever.
