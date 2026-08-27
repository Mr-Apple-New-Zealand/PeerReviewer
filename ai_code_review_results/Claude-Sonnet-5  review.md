# Code Review Report

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 32 | `Login` builds SQL by interpolating `username` directly into the query string, allowing SQL injection. | Use a parameterized query via `SqlCommand.Parameters.AddWithValue` or `ExecuteQuerySafe`. |
| SampleBankingApp/Services/AuthService.cs | 17, 53-56 | Hardcoded backdoor password `AdminBypassPassword = "SuperAdmin2024"` grants unauthenticated SuperAdmin access bypassing the database. | Remove the backdoor entirely; all authentication must go through the normal credential store. |
| SampleBankingApp/Services/AuthService.cs | 61-66 | Passwords are hashed with unsalted MD5 (`HashPasswordMd5`), which is cryptographically broken and vulnerable to rainbow-table attacks. | Use a slow, salted hash such as bcrypt, scrypt, or PBKDF2. |
| SampleBankingApp/Services/AuthService.cs | 91-96 | Dead `HashPasswordSha1` method also uses a weak, unsalted hash algorithm. | Remove or replace with a modern salted hash if ever reused. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | `ExecuteQuery` interpolates `tableName` and `whereClause` directly into SQL, enabling SQL injection for any caller (used by `SearchUsers`). | Disallow raw fragments; require parameterized `whereClause` with parameters dictionary, or remove the method. |
| SampleBankingApp/Services/UserService.cs | 99 | `SearchUsers` passes user-supplied `query` into a LIKE clause via `ExecuteQuery`, enabling SQL injection. | Use `ExecuteQuerySafe` with a parameterized LIKE clause. |
| SampleBankingApp/Services/UserService.cs | 47 | `UpdateUser` builds an UPDATE statement by interpolating `email` and `username`, enabling SQL injection. | Use parameterized query via `ExecuteQuerySafe`/`SqlCommand.Parameters`. |
| SampleBankingApp/Services/UserService.cs | 61 | `DeleteUser` builds a DELETE statement by interpolating `id`, enabling SQL injection (id is int but pattern is unsafe as template). | Use parameterized query. |
| SampleBankingApp/Services/TransactionService.cs | 47-48 | Balance UPDATE statements are built via string interpolation of computed values and user-supplied ids. | Use parameterized queries for all writes. |
| SampleBankingApp/Services/TransactionService.cs | 89-90 | `RecordTransaction` interpolates `description` (user-controlled from `TransferRequest.Description`) directly into an INSERT statement, enabling SQL injection. | Use parameterized INSERT statement. |
| SampleBankingApp/Services/TransactionService.cs | 71 | `Deposit` interpolates `amount`/`userId` into an UPDATE statement. | Use parameterized query. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Fallback connection string hardcodes credentials (`sa`/`Admin1234!`) in source. | Remove hardcoded fallback; fail fast if configuration is missing. |
| SampleBankingApp/appsettings.json | 3, 6, 14 | Production DB password, weak JWT secret (`mysecretkey`), and email password are committed to source control in plaintext. | Move secrets to environment variables, user-secrets, or a secure vault; rotate all committed credentials. |
| SampleBankingApp/appsettings.json | 3 | `TrustServerCertificate=True` disables proper TLS certificate validation for the DB connection. | Use a valid certificate and set `TrustServerCertificate=False`. |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry enforcement, so stolen/expired tokens remain valid forever. | Set `ValidateLifetime = true`. |
| SampleBankingApp/Program.cs | 38 | CORS policy allows any origin, method, and header — fully open CORS. | Restrict to specific trusted origins/methods/headers. |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, leaking stack traces in production. | Guard with `if (app.Environment.IsDevelopment())`. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out, allowing plaintext HTTP traffic. | Uncomment `app.UseHttpsRedirection()`. |
| SampleBankingApp/SampleBankingApp.csproj | 8-9 | `DebugSymbols`/`DebugType full` apply to all configurations including Release, shipping full PDBs to production. | Scope debug symbol settings to Debug configuration only. |
| SampleBankingApp/Controllers/UserController.cs | 21-29, 38-69 | `GetUser`, `UpdateUser`, `DeleteUser` only require `[Authorize]` with no ownership/role check — any authenticated user can view/modify/delete any other user's account (broken access control). | Add ownership check (matching user id) or role-based authorization (e.g. `[Authorize(Roles="Admin")]`). |
| SampleBankingApp/Controllers/UserController.cs | 78-82 | `GetAuditLog` exposes the full audit trail to any authenticated user with no role restriction. | Restrict to admin role. |
| SampleBankingApp/Controllers/UserController.cs | 31-36 | `GetUsers` exposes all user records (including balances) to any authenticated user. | Restrict to admin role or redact sensitive fields. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/UserService.cs | 72 | `GetUsersPage` computes `skip = page * pageSize` instead of `(page - 1) * pageSize`, causing page 1 to skip a full page of results (off-by-one). | Change to `(page - 1) * pageSize` and guard `page < 1`. |
| SampleBankingApp/Services/TransactionService.cs | 39-42 | `Transfer` checks `fromBalance >= amount` but then debits `totalDebit = amount + fee`, allowing the balance to go negative when the fee pushes the debit above the checked amount. | Check `fromBalance >= totalDebit` before allowing the transfer. |
| SampleBankingApp/Services/TransactionService.cs | 25-26 | `amount < 0` check allows `amount == 0`, letting a zero-value transfer proceed and still incur logic/fee side effects. | Change to `amount <= 0`. |
| SampleBankingApp/Services/TransactionService.cs | 23-61 | `Transfer` has no check preventing `fromUserId == toUserId`, allowing a self-transfer that still deducts a fee for no economic effect. | Add an explicit check and reject self-transfers. |
| SampleBankingApp/Services/TransactionService.cs | 68 | `Deposit` grants a flat 5% "interest bonus" instantly on every deposit (`amount * 0.05m * 1`), which is an implausible/incorrect business rule (likely meant to be a much smaller rate or not applied on deposit at all). | Confirm intended rate with business rules; likely remove or correct to an appropriate small interest rate applied periodically, not per-deposit. |
| SampleBankingApp/Services/TransactionService.cs | 77-85, 12 | `MaxTransactionsPerDay` limit and `IsWithinDailyLimit` are defined but never invoked from `Transfer`, so the daily transaction limit is not enforced. | Call `IsWithinDailyLimit` inside `Transfer` and reject when exceeded. |
| SampleBankingApp/Controllers/TransactionController.cs | 48-60 | `Refund` endpoint always fails with 500 because `RefundTransaction` is unimplemented; the feature appears to be exposed to clients despite being non-functional. | Remove endpoint until implemented, or return 501 Not Implemented explicitly. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/UserService.cs | 95-109 | `SearchUsers` catches broad `Exception` and returns an empty list, making it impossible for callers to distinguish "no matches" from a DB failure. | Let the exception propagate or return a distinguishable result (e.g., a Result type or rethrow a domain exception). |
| SampleBankingApp/Controllers/UserController.cs | 38-54 | `UpdateUser` catches generic `Exception` and returns `ex.Message` directly to the HTTP client, leaking internal error details. | Log the exception and return a generic error message to the client. |
| SampleBankingApp/Services/TransactionService.cs | 42-58 | `Transfer` performs two balance UPDATEs and an INSERT without wrapping them in a database transaction; a failure between statements leaves accounts in an inconsistent state. | Wrap all writes in a single `SqlTransaction` (or use `TransactionScope`) and commit/rollback atomically. |
| SampleBankingApp/Services/TransactionService.cs | 50-56 | Email notification (`SendTransferNotification`) is sent after balance updates and transaction recording have already committed; if the email throws, the exception propagates to the controller even though the transfer itself succeeded, misleading the client. | Send the notification asynchronously/best-effort after the response, or catch and log email failures without failing the transfer response. |
| SampleBankingApp/Services/EmailService.cs | 45-60 | After `MaxRetries` failed attempts, `SendTransferNotification` rethrows `SmtpException`, which (per above) can bubble up after a successful DB commit and surface as an unrelated 500 to the transfer caller. | Catch and log at the call site, or separate notification failure handling from transaction success/failure. |
| SampleBankingApp/Controllers/AuthController.cs | 19-31 | No error handling around `_authService.Login`; a DB connectivity failure inside `Login` will propagate as an unhandled exception, and with `UseDeveloperExceptionPage()` always enabled, stack traces will be shown. | Add try/catch with generic error response, and gate developer exception page to Development only. |
| SampleBankingApp/Controllers/AuthController.cs | 19-31 | No rate limiting or account lockout on the login endpoint, allowing unlimited brute-force attempts. | Add rate limiting/lockout (e.g., ASP.NET Core rate limiting middleware or a failed-attempt counter). |
| SampleBankingApp/Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` only calls `connection.Close()` on the success path; if `ExecuteNonQuery()` throws, the connection is never closed. | Wrap in `using`/`try-finally` to guarantee disposal. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 34-38 | `Login` opens a `SqlConnection` and executes a `SqlDataReader` without ever closing or disposing either, even in the success and failure paths. | Wrap `connection`, `command`, and `reader` in `using` statements. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26-34 | `ExecuteQuery` obtains a connection via `GetOpenConnection()` but never closes/disposes it. | Wrap in `using var connection = ...`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` opens a connection without `using`; any exception during `ExecuteNonQuery()` skips `connection.Close()`, leaking the connection. | Use `using` or try/finally to guarantee closure. |
| SampleBankingApp/Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection()` returns an open connection to callers with no documented disposal contract; two internal callers (`ExecuteQuery`, `ExecuteNonQuery`) already fail to dispose it, and any external caller is equally at risk. | Either make the method `internal` with clear `using` guidance in XML doc, or refactor away from exposing raw connections. |
| SampleBankingApp/Services/EmailService.cs | 16, 22-32 | `SmtpClient` is held as a long-lived instance field, which is not thread-safe and keeps a socket/connection open for the lifetime of the (scoped) service; it is also never disposed. | Create and dispose a new `SmtpClient` per send (`using`), or use `IHttpClientFactory`-style pooled client management. |
| SampleBankingApp/Services/EmailService.cs | 39-43 | `MailMessage` created in `SendTransferNotification` is never disposed. | Wrap in `using var message = ...`. |
| SampleBankingApp/Services/EmailService.cs | 69 | `MailMessage` created in `SendWelcomeEmail` is never disposed. | Wrap in `using`. |
| SampleBankingApp/Services/EmailService.cs | 89 | `MailMessage` created in `SendWelcomeEmailHtml` is never disposed. | Wrap in `using`. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 16, 28 | `jwtSecret` from `builder.Configuration["Jwt:SecretKey"]` can be null; it's force-unwrapped with `!` before `Encoding.UTF8.GetBytes`. | Validate configuration at startup and throw a clear error if missing, rather than relying on `!`. |
| SampleBankingApp/Services/AuthService.cs | 70 | `_config["Jwt:SecretKey"]!` is force-unwrapped in `GenerateJwtToken` without a null check. | Validate the config value once at startup or guard with a clear exception message. |
| SampleBankingApp/Controllers/TransactionController.cs | 26-27 | `userIdClaim` from `User.FindFirst(...)?.Value` can be null if the claim is missing; `int.Parse(userIdClaim!)` will throw `ArgumentNullException`. | Check for null and return 401/403 instead of force-unwrapping. |
| SampleBankingApp/Controllers/TransactionController.cs | 40-41 | Same null-forgiving `int.Parse(userIdClaim!)` pattern repeated in `Deposit`. | Same fix as above (also candidates for shared helper). |
| SampleBankingApp/Controllers/AuthController.cs | 20-27 | `request` (`LoginRequest`) is used without a null check; a null JSON body could result in `request` being null, causing an NRE at `request.Username`. | Add `if (request == null) return BadRequest();` or rely on `[ApiController]` model validation with a `[Required]` attribute plus explicit check. |
| SampleBankingApp/Controllers/TransactionController.cs | 24-29, 38-43 | `request` (`TransferRequest`/`DepositRequest`) used without a null check. | Add null checks before use. |
| SampleBankingApp/Controllers/UserController.cs | 39-43 | `request` (`UpdateUserRequest`) used without a null check before accessing `request.Email`/`request.Username`. | Add null check and return `BadRequest` if null. |
| SampleBankingApp/Services/EmailService.cs | 22 | `_config["Email:SmtpHost"]` may be null and is passed directly to the `SmtpClient` constructor, which can throw. | Validate configuration value and fail fast with a descriptive error if missing. |
| SampleBankingApp/Services/TransactionService.cs | 36-37 | `fromUserTable.Rows[0]` / `toUserTable.Rows[0]` are accessed without checking `Rows.Count > 0`; a non-existent `fromUserId`/`toUserId` causes an unhandled `IndexOutOfRangeException`. | Check `Rows.Count == 0` first and return a friendly "user not found" error. |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 91-96 | `HashPasswordSha1` is never called anywhere in the codebase. | Remove the unused method. |
| SampleBankingApp/Services/AuthService.cs | 98-108 | `ValidateToken` is never called anywhere in the codebase. | Remove, or wire it into the authentication pipeline if intended for use. |
| SampleBankingApp/Services/AuthService.cs | 105-107 | Code after the unconditional `return true;` inside `ValidateToken` (handler/jwtToken logic) is unreachable. | Remove the unreachable lines or fix the logic so the real validation executes. |
| SampleBankingApp/Services/EmailService.cs | 63-79 | `SendWelcomeEmail` is never called anywhere. | Remove or wire into a user-registration flow if intended. |
| SampleBankingApp/Services/EmailService.cs | 86-92 | `SendWelcomeEmailHtml` is never called anywhere. | Remove, or use it instead of the plain-text welcome email. |
| SampleBankingApp/Services/EmailService.cs | 81-84 | `BuildHtmlTemplate` is only referenced by the also-unused `SendWelcomeEmailHtml`, making it effectively dead. | Remove alongside `SendWelcomeEmailHtml` unless the HTML flow is adopted. |
| SampleBankingApp/Services/TransactionService.cs | 77-85 | `IsWithinDailyLimit` is defined but never called. | Either invoke it from `Transfer` (see Logic Errors) or remove it. |
| SampleBankingApp/Services/TransactionService.cs | 94-97 | `FormatCurrency` is never called anywhere. | Remove or use it in notification/response formatting. |
| SampleBankingApp/Services/TransactionService.cs | 99-103 | `RefundTransaction` is a stub throwing `NotImplementedException` but is wired to a live controller endpoint — not a harmless stub. | Implement the method or remove the `Refund` endpoint until ready. |
| SampleBankingApp/Data/DatabaseHelper.cs | 59-65 | `TableExists` is never called anywhere. | Remove if unused, or use it for schema validation on startup. |
| SampleBankingApp/Data/DatabaseHelper.cs | 67-78 | `ExecuteQueryWithParams` is marked `[Obsolete]` yet remains in the codebase and is never called. | Remove the obsolete method entirely now that `ExecuteQuerySafe` replaces it. |
| SampleBankingApp/Helpers/StringHelper.cs | 11-18 | `IsValidEmail` is never called anywhere in the codebase. | Remove, or use it to validate email input in `UserController.UpdateUser`. |
| SampleBankingApp/Helpers/StringHelper.cs | 20-27 | `IsValidUsername` is never called anywhere. | Remove, or use it to validate username input in `UserController.UpdateUser`. |
| SampleBankingApp/Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` is never called anywhere (and is the broken O(n²) implementation superseded by `JoinWithSeparatorFixed`). | Remove `JoinWithSeparator`; it is dead and inferior to the fixed version. |
| SampleBankingApp/Helpers/StringHelper.cs | 38-41 | `JoinWithSeparatorFixed` is never called anywhere. | Remove if truly unused, or replace call sites that build strings manually (e.g., `GetAuditReport`) with this method. |
| SampleBankingApp/Helpers/StringHelper.cs | 43-52 | `MaskAccountNumber` is never called anywhere. | Remove, or use it wherever account numbers are surfaced to users/logs. |
| SampleBankingApp/Helpers/StringHelper.cs | 54-57 | `ObfuscateAccount` is never called anywhere and duplicates `MaskAccountNumber`'s purpose. | Remove one of the two duplicate implementations. |
| SampleBankingApp/Helpers/StringHelper.cs | 59-63 | `ToTitleCase` is never called anywhere. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 65-71 | `IsBlank` is never called anywhere. | Remove; `string.IsNullOrWhiteSpace` already covers this. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 17 | `AdminBypassPassword = "SuperAdmin2024"` is a hardcoded credential/backdoor string. | Remove entirely (see Security section). |
| SampleBankingApp/Services/TransactionService.cs | 68 | Literal `0.05m` (5% "interest bonus") is not a named constant and is unexplained. | Extract to a named constant (e.g., `DepositBonusRate`) or remove. |
| SampleBankingApp/Services/TransactionService.cs | 65 | Literal `1000000` deposit cap is inline rather than a named constant/config value. | Extract to `const decimal MaxDepositAmount = 1_000_000m;` or move to configuration. |
| SampleBankingApp/Services/UserService.cs | 22, 42-43, 56-57 | Magic number `1000000` (max user id) is repeated across `GetUserById`, `UpdateUser`, `DeleteUser`. | Extract to a shared named constant, e.g., `MaxUserId`. |
| SampleBankingApp/Services/UserService.cs | 70 | Magic number `50` (max page size) is inline. | Extract to a named constant `MaxPageSize`. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | Magic number `254` (max email length) is inline. | Extract to a named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | Magic numbers `3` and `20` (username length bounds) are inline. | Extract to named constants (`MinUsernameLength`, `MaxUsernameLength`). |
| SampleBankingApp/Helpers/StringHelper.cs | 45, 49-50, 56 | Magic number `4` (digits to reveal) repeated in `MaskAccountNumber` and `ObfuscateAccount`. | Extract to a shared named constant used by a single method. |
| SampleBankingApp/Services/EmailService.cs | 40, 69, 89 | Literal sender address `"notifications@company.com"` repeated three times. | Move to configuration and inject once. |
| SampleBankingApp/Services/EmailService.cs | 67 | Literal support address `"support@company.com"` embedded in email body text. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 24 | Fallback SMTP port `"25"` duplicates the value already present in `appsettings.json`. | Require configuration value; fail fast if missing rather than silently defaulting. |
| SampleBankingApp/Services/AuthService.cs | 84 | Magic number `30` (days) for JWT expiry is hardcoded. | Move token lifetime to configuration. |
| SampleBankingApp/Services/AuthService.cs | 55 | Hardcoded role string `"SuperAdmin"` (and elsewhere role strings like `"Admin"` implied) are magic strings without a shared constant/enum. | Define a `Roles` static class or enum for role names. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Entire hardcoded connection string is a magic literal duplicating (and conflicting with) the one in `appsettings.json`. | Remove fallback; require configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` concatenates strings in a loop — O(n²) performance; a correct version (`JoinWithSeparatorFixed`) already exists alongside it. | Delete the broken version and use `string.Join` (or the fixed helper) everywhere. |
| SampleBankingApp/Services/UserService.cs | 85-93 | `GetAuditReport` concatenates strings in a loop (`report += entry + "\n"`) — O(n²) performance. | Use `string.Join("\n", _auditLog)` or a `StringBuilder`. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | `IsValidEmail` creates a `new Regex(...)` on every call. | Make the `Regex` a `static readonly` field. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | `IsValidUsername` creates a `new Regex(...)` on every call. | Make the `Regex` a `static readonly` field. |
| SampleBankingApp/Services/UserService.cs | 10-11 | `_auditLog` and `_requestCount` are `static` mutable fields on a service registered as `Scoped`, accessed without any locking — a race condition under concurrent requests. | Make these instance fields backed by a persistent store, or add proper synchronization if truly shared state is required. |
| SampleBankingApp/Services/UserService.cs | 20-23, 40-43, 54-57 | Duplicated id-validation logic (`id <= 0` / `id > 1000000`) repeated identically in `GetUserById`, `UpdateUser`, `DeleteUser`. | Extract into a single private `ValidateUserId(int id)` helper. |
| SampleBankingApp/Services/EmailService.cs | 16 | `SmtpClient` stored as an instance field is not thread-safe and couples the service to one long-lived connection — an anti-pattern regardless of the leak issue already noted. | Instantiate/dispose per call, or use a pooled/factory-based approach. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26-34 | `ExecuteQuery(tableName, whereClause)` is a helper explicitly designed to accept raw SQL fragments with no documented safety contract, inviting injection at every call site. | Remove this API in favor of `ExecuteQuerySafe` with parameters everywhere. |
| SampleBankingApp/Helpers/StringHelper.cs | 43-57 | `MaskAccountNumber` and `ObfuscateAccount` duplicate the same "mask all but last 4 digits" behavior with two different implementations. | Consolidate into a single method. |
| SampleBankingApp/Helpers/StringHelper.cs | 65-71 | `IsBlank` reimplements the framework's `string.IsNullOrWhiteSpace`. | Remove and use `string.IsNullOrWhiteSpace` directly. |
| SampleBankingApp/Services/TransactionService.cs | 23-61 | `Transfer` mixes several responsibilities: input validation, data retrieval, fee calculation, balance mutation, transaction recording, and email notification. | Split into `ValidateTransferRequest`, `LoadAccounts`, `ApplyTransfer` (DB writes in a transaction), and `NotifyParticipants`. |
| SampleBankingApp/Services/AuthService.cs | 28-59 | `Login` mixes SQL querying, password hashing, backdoor-credential checking, and User object mapping in one method. | Split into `FindUserByCredentials`, `MapReaderToUser`, and remove the backdoor branch entirely. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` doesn't use `using`, deviating from the pattern used elsewhere in the same class (`ExecuteQuerySafe`, `TableExists`), an inconsistent resource-management style. | Standardize on `using` declarations across all methods in the class. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally for all environments. | Only call it when `app.Environment.IsDevelopment()`. |
| SampleBankingApp/Program.cs | 24 | JWT `ValidateLifetime = false` disables token expiry checks. | Set to `true`. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out. | Enable `app.UseHttpsRedirection()`. |
| SampleBankingApp/Program.cs | 38 | CORS policy uses `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`. | Define a named policy limited to specific trusted origins/methods/headers. |
| SampleBankingApp/appsettings.json | 17-21 | Logging levels are set to `Debug` for `Default`, `Microsoft`, and `System`, which is excessive for production and can leak sensitive info/verbose logs. | Set production levels to `Information`/`Warning` and use `appsettings.Development.json` for verbose debug logging. |
| SampleBankingApp/appsettings.json | 1-24 | No `appsettings.Production.json` (or environment-specific override) exists to separate secrets/config per environment. | Add environment-specific config files and remove secrets from the base file. |
| SampleBankingApp/appsettings.json | 3, 6, 14 | Secrets (DB password, JWT key, email password) committed directly to source control. | Use secret managers/environment variables/Key Vault instead of committing to `appsettings.json`. |
| SampleBankingApp/SampleBankingApp.csproj | 14 | `System.Data.SqlClient` (4.8.6) is a legacy, effectively deprecated package no longer receiving new features. | Migrate to `Microsoft.Data.SqlClient`. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | `Newtonsoft.Json` 12.0.3 is an old version with known vulnerabilities (fixed in 13.x) and appears entirely unused in the source. | Remove the unused dependency, or upgrade if actually needed. |
| SampleBankingApp/SampleBankingApp.csproj | 8-9 | `DebugSymbols`/`DebugType full` apply unconditionally (not scoped to Debug configuration), risking symbol leakage in Release/production builds. | Scope these settings to a Debug-only `PropertyGroup` condition. |

## 10. Missing Unit Tests

No test project exists anywhere in the repository. The following methods/scenarios are the highest priority to cover:

| Area | Method | Scenarios to test |
|---|---|---|
| Pagination | `UserService.GetUsersPage` | Page = 1 should skip 0 rows (currently fails due to off-by-one); page = 0 or negative; pageSize > 50 clamped to 50; pageSize <= 0. |
| Financial calc | `TransactionService.Transfer` | Balance exactly equal to amount but insufficient for fee (should fail, currently succeeds and goes negative); amount = 0 (should be rejected); negative amount; self-transfer (fromUserId == toUserId); nonexistent from/to user ids. |
| Financial calc | `TransactionService.Deposit` | Amount = 0 and negative (rejected); amount = 1,000,000 boundary; amount = 1,000,001 boundary; verify interest bonus calculation matches intended business rule. |
| Auth flow | `AuthService.Login` | Correct credentials succeed; wrong password fails; inactive user rejected; SQL-injection-style username input; ensure no backdoor path exists once removed. |
| Auth flow | `AuthService.GenerateJwtToken` / token validation | Token contains expected claims; expired token is rejected once `ValidateLifetime` is fixed. |
| Auth flow | `AuthController.Login` | Null request body handling; missing username/password fields. |
| Authorization | `UserController.UpdateUser` / `DeleteUser` | Non-owner/non-admin user attempting to modify another user's account should be forbidden (currently unguarded). |
| Boundary validation | `UserService.GetUserById` / `UpdateUser` / `DeleteUser` | id = 0, negative id, id = 1,000,000, id = 1,000,001. |
| Concurrency | `UserService` static fields (`_auditLog`, `_requestCount`) | Concurrent requests should not corrupt shared state or lose updates. |
| Error handling | `UserService.SearchUsers` | Verify behavior distinguishes "no results" from a query failure once fixed. |
| Email retry logic | `EmailService.SendTransferNotification` | Simulate `SmtpException` and verify retry count and final exception propagation behavior.