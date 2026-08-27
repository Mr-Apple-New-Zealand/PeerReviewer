# Code Review — SampleBankingApp

The following issues were identified during review of the full source tree.


## Security Vulnerabilities

- **`Services/AuthService.cs`** (line ~35): SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely.
- **`Services/AuthService.cs`** (line ~49): Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record.
- **`Services/AuthService.cs`** (line ~56): Broken password hashing — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks.
- **`Services/UserService.cs`** (line ~45, 60): SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements.
- **`Services/UserService.cs`** (line ~88): SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause via `ExecuteQuery`.
- **`Services/TransactionService.cs`** (line ~50, 53): SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements.
- **`Services/TransactionService.cs`** (line ~82): SQL Injection (RecordTransaction) — `description` is interpolated; a malicious description can inject arbitrary SQL.
- **`appsettings.json`** (line all): Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed to source control.
- **`Program.cs`** (line ~30): JWT lifetime validation disabled (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever.
- **`Controllers/UserController.cs`** (line ~53): Broken Access Control — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile.
- **`Controllers/UserController.cs`** (line ~67): Missing Authorization — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account.

## Logic Errors

- **`Services/TransactionService.cs`** (line ~25): `amount < 0` check allows zero-value transfers (`amount == 0`). Should be `amount <= 0`.
- **`Services/TransactionService.cs`** (line ~43): Balance check excludes the fee — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted.
- **`Services/UserService.cs`** (line ~73): Off-by-one in pagination — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1.
- **`Services/TransactionService.cs`** (line ~60): Incorrect interest rate — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual.
- **`Controllers/TransactionController.cs`** (line ~26): Self-transfer allowed — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing.

## Refactoring Opportunities

- **`Services/UserService.cs`** (line ~20, 38, 54): Duplicated validation — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method.
- **`Helpers/StringHelper.cs`** (line ~28): Loop string concatenation — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`.
- **`Services/AuthService.cs`** (line ~71): Overly long `GenerateJwtToken` — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability.

## Error Handling

- **`Services/UserService.cs`** (line ~83): `SearchUsers` swallows all exceptions and returns an empty list — callers cannot distinguish "no results" from "DB is down".
- **`Services/EmailService.cs`** (line ~63): `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded.
- **`Services/TransactionService.cs`** (line ~55): No database transaction around the two UPDATE statements — if the second update fails, balances become permanently inconsistent.
- **`Services/TransactionService.cs`** (line ~59): Email failure in `Transfer` propagates an exception after the DB transfer has already committed — the transfer succeeds but the caller gets an error response.
- **`Controllers/UserController.cs`** (line ~58): `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked.
- **`Data/DatabaseHelper.cs`** (line ~44): `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`.
- **`Controllers/AuthController.cs`** (line ~20): No rate limiting or account lockout on failed login attempts — brute force is trivially possible.

## Resource Leaks

- **`Services/AuthService.cs`** (line ~37–38): `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed.
- **`Data/DatabaseHelper.cs`** (line ~26): `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result.
- **`Data/DatabaseHelper.cs`** (line ~44): `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close.
- **`Services/EmailService.cs`** (line ~36): `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released.
- **`Services/EmailService.cs`** (line ~49, 72): `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`.

## Missing Null Checks

- **`Services/AuthService.cs`** (line ~72): `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws.
- **`Services/TransactionService.cs`** (line ~35–36): `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist.
- **`Services/EmailService.cs`** (line ~46): `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key.
- **`Services/EmailService.cs`** (line ~68): `username.ToUpper()` throws `NullReferenceException` if `username` is `null`.
- **`Helpers/StringHelper.cs`** (line ~14, 24): `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access.
- **`Controllers/TransactionController.cs`** (line ~19, 31): `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`.
- **`Controllers/UserController.cs`** (line ~28): `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body.

## Magic Strings and Numbers

- **`Services/TransactionService.cs`** (line ~13–14): `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration.
- **`Services/TransactionService.cs`** (line ~60): `1_000_000` deposit cap hardcoded inline — no named constant.
- **`Services/EmailService.cs`** (line ~14–15, 49, 72): Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places.
- **`Helpers/StringHelper.cs`** (line ~14, 24): `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.).
- **`Services/UserService.cs`** (line ~69): `50` as the page size upper bound is unnamed and undocumented.

## Dead Code

- **`Services/AuthService.cs`** (line ~80): `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called.
- **`Services/AuthService.cs`** (line ~87–92): Unreachable code after `return true` in `ValidateToken`.
- **`Data/DatabaseHelper.cs`** (line ~49): `TableExists` — never called from any service or controller.
- **`Data/DatabaseHelper.cs`** (line ~56): `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed.
- **`Services/EmailService.cs`** (line ~79): `BuildHtmlTemplate` — private method reachable only from `SendWelcomeEmailHtml` (D6), which itself has no callers; it is therefore dead transitively rather than uninvoked.
- **`Services/EmailService.cs`** (line ~85): `SendWelcomeEmailHtml` — public method, never registered or called.
- **`Services/TransactionService.cs`** (line ~91): `FormatCurrency` — private, never called.
- **`Services/TransactionService.cs`** (line ~72): `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced.
- **`Helpers/StringHelper.cs`** (line ~49): `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called.
- **`Helpers/StringHelper.cs`** (line ~54): `ToTitleCase` — "experimental utility never integrated", never called.
- **`Helpers/StringHelper.cs`** (line ~37): `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used.

## Anti-patterns

- **`Services/UserService.cs`** (line ~15–16): Mutable static state — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe.
- **`Helpers/StringHelper.cs`** (line ~14, 24): Regex compiled per-call — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`.
- **`Helpers/StringHelper.cs`** (line ~29): String concatenation in loop — classic O(n²) pattern; use `string.Join` or `StringBuilder`.
- **`Services/EmailService.cs`** (line ~34): Shared mutable `SmtpClient` — `SmtpClient` is not thread-safe and should be created per-send, not held as a field.
- **`Helpers/StringHelper.cs`** (line ~60): Reimplementing BCL — `IsBlank` duplicates `string.IsNullOrWhiteSpace`.
- **`Data/DatabaseHelper.cs`** (line ~26): Leaking connection — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this.

## Configuration Issues

- **`appsettings.json`** (line all): Production secrets in source control — DB password, JWT secret, SMTP password all present.
- **`appsettings.json`** (line ~16–20): Log level `Debug` in production — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals.
- **`Program.cs`** (line ~29): JWT `ValidateLifetime = false` — tokens never expire regardless of the `expires` field.
- **`Program.cs`** (line ~33): HTTPS disabled — `UseHttpsRedirection()` commented out.
- **`Program.cs`** (line ~26): `UseDeveloperExceptionPage()` called unconditionally — full stack traces served to production clients.
- **`Program.cs`** (line ~37): Open CORS policy — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API.
- **`SampleBankingApp.csproj`** (line ~7–10): `DebugSymbols = true` / `DebugType = full` always emitted — PDB files shipped with release builds.
- **`SampleBankingApp.csproj`** (line ~14): Pinned outdated package — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated.
- **`(project root)`** (line —): No `appsettings.Production.json` — no environment-specific overrides; production uses the same unsafe defaults.

## Missing Unit Tests

The project contains no test project and no test files of any kind. AuthService.Login, AuthService.GenerateJwtToken, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUsersPage, StringHelper methods, and all controller actions lack any test coverage whatsoever.
