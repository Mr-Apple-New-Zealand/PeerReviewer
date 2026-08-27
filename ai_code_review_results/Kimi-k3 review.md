# Peer Code Review — SampleBankingApp (main @ 9109360)

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| AuthService.cs | 32 | `Login` builds the authentication query by interpolating `username` and `hashedPassword`, allowing trivial auth bypass such as `' OR '1'='1'--`. | Use a parameterized `SqlCommand` with `@Username`/`@Password` parameters. |
| AuthService.cs | 17 | Hardcoded backdoor password constant `AdminBypassPassword = "SuperAdmin2024"` in source. | Delete the constant entirely. |
| AuthService.cs | 53-56 | `Login` contains a backdoor that returns a `SuperAdmin` user (Id=0) for username "admin" with the hardcoded password. | Remove the backdoor branch. |
| AuthService.cs | 30, 61-66 | Passwords are hashed with unsalted MD5 via `HashPasswordMd5`, which is broken and rainbow-table vulnerable. | Use PBKDF2/BCrypt/Argon2 with per-user salt (e.g., ASP.NET Core Identity `PasswordHasher`). |
| AuthService.cs | 91-96 | `HashPasswordSha1` uses broken SHA1 (also unused). | Delete the method. |
| AuthService.cs | 98-108 | `ValidateToken` returns `true` for any non-empty string without checking signature or expiry (also unused). | Delete it or implement real validation via `JwtSecurityTokenHandler.ValidateToken`. |
| AuthService.cs | 84 | JWT lifetime is 30 days, and with lifetime validation disabled tokens never effectively expire. | Use short expiry (15-60 min) with refresh tokens. |
| Program.cs | 24 | `ValidateLifetime = false` means expired JWTs are accepted. | Set `ValidateLifetime = true`. |
| Program.cs | 34 | `UseDeveloperExceptionPage()` is unconditional, leaking stack traces in production. | Call it only when `app.Environment.IsDevelopment()`. |
| Program.cs | 36 | HTTPS redirection is commented out. | Re-enable `app.UseHttpsRedirection()`. |
| Program.cs | 38 | CORS allows any origin, any method, any header. | Restrict to known origins and required methods/headers. |
| appsettings.json | 3 | Production SQL credentials (`sa` / `Admin1234!`) committed to source control. | Remove secrets from config, use a secret store, and rotate the password. |
| appsettings.json | 3 | `TrustServerCertificate=True` disables SQL Server certificate validation, enabling MITM. | Set to `false` and deploy a trusted certificate. |
| appsettings.json | 6 | JWT secret `"mysecretkey"` is weak, committed to source, and under 128 bits so HmacSha256 key validation can fail at runtime. | Move a ≥32-byte random secret to user secrets/Key Vault. |
| appsettings.json | 14 | SMTP password `"EmailPass99"` committed to source control. | Move to a secret store and rotate. |
| DatabaseHelper.cs | 16 | Fallback connection string embeds hardcoded `sa` credentials `Admin1234!`. | Remove the fallback and fail fast when config is missing. |
| DatabaseHelper.cs | 26-34 | `ExecuteQuery` accepts raw `tableName`/`whereClause` fragments and interpolates them into SQL. | Delete it or restrict to allow-listed identifiers with parameterized filters. |
| UserService.cs | 99 | `SearchUsers` interpolates user input into a `LIKE` clause via `ExecuteQuery` — SQL injection. | Use `ExecuteQuerySafe` with a `@query` parameter and escaped wildcards. |
| UserService.cs | 47 | `UpdateUser` interpolates `email` and `username` into an UPDATE — SQL injection. | Parameterize with `SqlParameter`s. |
| UserService.cs | 61 | `DeleteUser` interpolates `id` into a DELETE (int-typed so not exploitable today, but an unsafe pattern). | Parameterize for defense in depth. |
| TransactionService.cs | 89-90 | `RecordTransaction` interpolates user-controlled `description` into an INSERT — SQL injection via `TransferRequest.Description`. | Parameterize the INSERT. |
| TransactionService.cs | 47-48 | `Transfer` interpolates balances and ids into UPDATE statements (unsafe pattern, culture-sensitive). | Parameterize both UPDATEs. |
| TransactionService.cs | 70-71 | `Deposit` interpolates the amount into an UPDATE (unsafe pattern). | Parameterize. |
| UserController.cs | 21-29 | `GetUser` lets any authenticated user read any user's profile and balance — no ownership check. | Enforce caller-id match or Admin role. |
| UserController.cs | 31-36 | `GetUsers` exposes the full user list to any authenticated user — no role check. | Require Admin role. |
| UserController.cs | 38-54 | `UpdateUser` has no ownership/role check — any authenticated user can modify any account. | Verify caller id matches route id or require Admin. |
| UserController.cs | 56-69 | `DeleteUser` has no ownership/role check — any authenticated user can delete any account. | Require Admin role or ownership check. |
| UserController.cs | 78-82 | `GetAuditLog` exposes the audit log (containing emails) to any authenticated user. | Require Admin role. |
| TransactionController.cs | 48-60 | `Refund` endpoint has no admin/ownership authorization check. | Add role/ownership validation before refunding. |
| AuthController.cs | 19-31 | Login endpoint has no rate limiting or account lockout, enabling credential brute force. | Add rate-limiting/lockout middleware. |
| EmailService.cs | 29 | `EnableSsl = false` sends SMTP credentials and message content in plaintext. | Enable SSL/TLS. |
| SampleBankingApp.csproj | 8-9 | `DebugSymbols=true` and `DebugType=full` ship full debug symbols in release builds. | Use `portable`/`none` for Release configuration. |
| User.cs | 7 | The `User` model carries a `Password` property that is serialized by API responses such as `GetUser`. | Remove `Password` from the API model or return a DTO. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| TransactionService.cs | 25 | `Transfer` validates `amount < 0`, so zero-amount transfers are accepted, recorded, and emailed. | Change to `amount <= 0`. |
| TransactionService.cs | 42 | Balance check `fromBalance >= amount` ignores the fee, so deducting `amount + fee` can drive the balance negative. | Compare `fromBalance >= totalDebit`. |
| TransactionService.cs | 23-61 | `Transfer` has no self-transfer check; when `fromUserId == toUserId` the second UPDATE uses the stale `toBalance` and the balance increases by `amount`, creating money. | Reject transfers where `fromUserId == toUserId`. |
| TransactionService.cs | 39-50 | The 1.5% fee is debited from the sender but never credited to any fee account or recorded, so it vanishes from the ledger. | Record the fee as its own transaction/ledger entry. |
| TransactionService.cs | 77-85 | `IsWithinDailyLimit` is never called, so `MaxTransactionsPerDay` is never enforced. | Invoke it in `Transfer` before debiting. |
| TransactionService.cs | 68 | `Deposit` applies a 5% `interestBonus` on every deposit (likely intended 1%), handing out free money per deposit. | Correct the rate and make it configurable. |
| TransactionService.cs | 68 | `amount * 0.05m * 1` contains a no-op `* 1`, suggesting unfinished rate logic. | Remove or replace with the intended factor. |
| TransactionService.cs | 73 | `Deposit` records only `amount` in the transaction log while crediting `amount + bonus`, so the audit trail mismatches the balance change. | Record the credited total and bonus separately. |
| TransactionService.cs | 70-74 | `Deposit` returns success even when the user id does not exist because the UPDATE's rows-affected is never checked. | Fail when `ExecuteNonQuery` returns 0. |
| UserService.cs | 72 | `GetUsersPage` computes `skip = page * pageSize`, so page 1 skips the first `pageSize` rows (off-by-one). | Use `(page - 1) * pageSize`. |
| UserService.cs | 68-76 | `GetUsersPage` does not validate `page < 1` or `pageSize < 1`, producing negative OFFSET/FETCH and a `SqlException`. | Clamp `page >= 1` and `pageSize >= 1`. |
| UserService.cs | 22, 42, 56 | The `id > 1000000` cap makes legitimate users with higher ids unreadable, uneditable, and undeletable. | Remove the arbitrary cap or validate against the real key range. |
| UserService.cs | 99 | `SearchUsers` with a null/empty query becomes `LIKE '%%'` and returns every user. | Require a non-empty query and cap result count. |
| UserService.cs | 38-50 | `UpdateUser` performs no format validation on email/username and no uniqueness check on username. | Validate formats and check for duplicates. |
| StringHelper.cs | 33 | `JoinWithSeparator` appends the separator after every item, leaving a trailing separator. | Use `string.Join` (as `JoinWithSeparatorFixed` does). |
| TransactionService.cs | 47, 48, 71, 90 | Decimals interpolated into SQL use the current culture, so a comma-decimal locale produces invalid or wrong SQL. | Parameterize (or use `InvariantCulture` at minimum). |
| TransactionController.cs | 58 | `Refund` maps `NotImplementedException` to HTTP 500 instead of 501 Not Implemented. | Return `StatusCode(501)`. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| UserService.cs | 105-108 | `SearchUsers` catches all exceptions and returns an empty list, so callers cannot distinguish an error from no matches. | Let exceptions propagate or return a result type with an error flag. |
| EmailService.cs | 75-78 | `SendWelcomeEmail` swallows all exceptions with `Console.WriteLine`. | Log via `ILogger` and/or rethrow. |
| TransactionService.cs | 47-50 | `Transfer` performs two UPDATEs plus an INSERT with no database transaction, so a mid-way failure loses money. | Wrap the writes in a `SqlTransaction` or `TransactionScope`. |
| TransactionService.cs | 52-55 | `Transfer` sends the notification email after the DB writes with no try/catch, so an SMTP failure surfaces as a 500 even though the transfer committed. | Catch/log email failures or queue the email out-of-band. |
| EmailService.cs | 57-58 | `SendTransferNotification` rethrows after retries, propagating through `Transfer` after the money has moved. | Handle at the call site or use a background queue. |
| UserController.cs | 52 | `UpdateUser` returns raw `ex.Message` in the 500 response. | Return a generic message and log the exception. |
| UserController.cs | 48 | `UpdateUser` returns `ArgumentException.Message` directly to clients (minor information leak). | Return a sanitized validation message. |
| UserController.cs | 64-68 | `DeleteUser` converts `ArgumentException` (bad id) into a 500 instead of a 400. | Catch `ArgumentException` separately and return `BadRequest`. |
| AuthController.cs | 19-31 | Login has no rate limiting or lockout on failed attempts. | Add throttling/lockout. |
| TransactionController.cs | 23-46 | `Transfer` and `Deposit` have no exception handling, so any service exception becomes an unhandled 500 (with dev-page details in production). | Add try/catch or global exception middleware. |
| DatabaseHelper.cs | 54-55 | `ExecuteNonQuery` skips `connection.Close()` when `ExecuteNonQuery` throws. | Use `using`/`finally`. |
| AuthService.cs | 34-51 | `Login` has no try/finally, so the reader and connection leak when an exception occurs mid-read. | Use `using` declarations. |
| TransactionService.cs | 99-103 | `RefundTransaction` throws `NotImplementedException` at runtime from a routed endpoint instead of failing at build time. | Implement it or remove the endpoint. |
| EmailService.cs | 56, 77 | Failures are logged with `Console.WriteLine` instead of a logger, so they are lost in production. | Inject `ILogger<EmailService>`. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| AuthService.cs | 34-35 | The `SqlConnection` in `Login` is opened but never closed or disposed on any path, including the success return. | Use a `using` declaration. |
| AuthService.cs | 37 | The `SqlCommand` in `Login` is never disposed. | Use `using`. |
| AuthService.cs | 38 | The `SqlDataReader` in `Login` is never disposed, including on the success path. | Use `using`. |
| DatabaseHelper.cs | 28 | `ExecuteQuery` never closes or disposes the connection obtained from `GetOpenConnection`. | Wrap in `using`. |
| DatabaseHelper.cs | 29-30 | `ExecuteQuery` does not dispose the `SqlCommand` or `SqlDataAdapter`. | Use `using`. |
| DatabaseHelper.cs | 52-55 | `ExecuteNonQuery` closes but never disposes the connection, and the exception path skips `Close` entirely. | Use `using var connection`. |
| DatabaseHelper.cs | 53 | `ExecuteNonQuery` never disposes the `SqlCommand`. | Use `using`. |
| DatabaseHelper.cs | 19-24 | `GetOpenConnection` returns an open connection whose disposal is left to callers, and both internal callers mishandle it. | Make helpers self-contained with `using` blocks. |
| DatabaseHelper.cs | 44 | `ExecuteQuerySafe` does not dispose the `SqlDataAdapter` (minor; the command is disposed). | Use `using` for completeness. |
| EmailService.cs | 16, 22-31 | `SmtpClient` is held as an instance field, is not thread-safe, and is never disposed. | Create and dispose `SmtpClient` per send or use a thread-safe mail library. |
| EmailService.cs | 39 | The `MailMessage` in `SendTransferNotification` is never disposed. | Use `using`. |
| EmailService.cs | 69 | The `MailMessage` in `SendWelcomeEmail` is never disposed. | Use `using`. |
| EmailService.cs | 89 | The `MailMessage` in `SendWelcomeEmailHtml` is never disposed. | Use `using`. |
| UserService.cs | 10 | Static `_auditLog` grows unboundedly for the process lifetime — a slow memory leak. | Persist audit entries to a database with retention. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| Program.cs | 16, 28 | `jwtSecret` is read from config and null-forgiven into `Encoding.UTF8.GetBytes`, so a missing key crashes startup with `ArgumentNullException`. | Validate configuration at startup with a clear error. |
| AuthService.cs | 70 | `_config["Jwt:SecretKey"]!` is null-forgiven into `GetBytes`, throwing if the key is absent. | Guard with a null check or the Options pattern. |
| AuthService.cs | 81-82 | `_config["Jwt:Issuer"]`/`["Jwt:Audience"]` may be null, producing a token without issuer/audience. | Validate config presence at startup. |
| TransactionController.cs | 26-27 | `int.Parse(userIdClaim!)` throws when the `NameIdentifier` claim is missing or non-numeric. | Use `int.TryParse` and return 401/400 on failure. |
| TransactionController.cs | 40-41 | `Deposit` repeats the same unguarded claim parse. | Same fix. |
| TransactionService.cs | 36-37 | `Transfer` reads `Rows[0]` without checking `Rows.Count`, throwing `IndexOutOfRangeException` when either user id does not exist. | Check `Rows.Count` and return a "user not found" result. |
| TransactionService.cs | 53-55 | `Transfer` re-reads `Rows[0]["Email"]`/`["Username"]` with the same missing-row risk. | Extract values after a count check. |
| EmailService.cs | 65 | `username.ToUpper()` is called before any null check. | Null-check `username` first. |
| EmailService.cs | 22 | `_config["Email:SmtpHost"]` may be null, leaving `SmtpClient` without a host and failing at send time. | Validate required config in the constructor. |
| StringHelper.cs | 13 | `IsValidEmail` dereferences `email.Length` with no null guard. | Guard with `IsNullOrEmpty`. |
| StringHelper.cs | 22 | `IsValidUsername` dereferences `username.Length` with no null guard. | Guard with `IsNullOrEmpty`. |
| StringHelper.cs | 45 | `MaskAccountNumber` dereferences `accountNumber.Length` with no null guard. | Null-check first. |
| StringHelper.cs | 56 | `ObfuscateAccount` uses `account[^4..]`, throwing for null or strings shorter than 4 characters. | Add a null/length guard. |
| AuthController.cs | 20-22 | `Login` uses `request` without a null check; a JSON `null` body yields a `NullReferenceException`. | Null-check the model or add `[Required]` validation. |
| TransactionController.cs | 24, 38 | `Transfer` and `Deposit` use `request` without null checks. | Same fix. |
| UserController.cs | 39-43 | `UpdateUser` uses `request` without a null check. | Same fix. |
| UserService.cs | 115-121 | `MapRowToUser` casts row values directly, throwing on `DBNull` for nullable columns. | Use `row.IsNull` checks or `Convert` APIs. |
| AuthService.cs | 44-49 | `Login` casts reader columns directly, throwing on `DBNull`. | Guard with `IsDBNull`. |
| UserService.cs | 83 | `IsWithinDailyLimit` reads `Rows[0]` assuming COUNT always returns a row (safe today, fragile pattern). | Use a scalar API or check `Rows.Count`. |

## 6. Dead Code

Method inventory taken across all 13 source files (controllers, services, data access, helpers); controller actions are routed entry points and were excluded; each method below appears only at its own definition. Note the entire `StringHelper` class is unreferenced.

| File | Line | Issue | Fix |
|---|---|---|---|
| DatabaseHelper.cs | 59-65 | `TableExists` has no callers in any file. | Delete it. |
| DatabaseHelper.cs | 67-78 | `ExecuteQueryWithParams` is marked `[Obsolete]` and has no callers. | Delete it. |
| StringHelper.cs | 11-18 | `IsValidEmail` has no callers (`UpdateUser` never validates email). | Wire it into `UpdateUser` or delete it. |
| StringHelper.cs | 20-27 | `IsValidUsername` has no callers. | Wire it in or delete it. |
| StringHelper.cs | 29-36 | `JoinWithSeparator` has no callers and is the broken duplicate of `JoinWithSeparatorFixed`. | Delete it. |
| StringHelper.cs | 38-41 | `JoinWithSeparatorFixed` has no callers. | Delete or use it. |
| StringHelper.cs | 43-52 | `MaskAccountNumber` has no callers. | Delete or use it. |
| StringHelper.cs | 54-57 | `ObfuscateAccount` has no callers and duplicates `MaskAccountNumber`. | Delete it. |
| StringHelper.cs | 59-63 | `ToTitleCase` has no callers. | Delete or use it. |
| StringHelper.cs | 65-71 | `IsBlank` has no callers. | Delete it (use `string.IsNullOrWhiteSpace`). |
| AuthService.cs | 91-96 | `HashPasswordSha1` has no callers. | Delete it. |
| AuthService.cs | 98-108 | `ValidateToken` has no callers. | Delete it or implement and use it. |
| AuthService.cs | 105-107 | Code after the unconditional `return true;` in `ValidateToken` is unreachable. | Remove or restructure the method. |
| EmailService.cs | 63-79 | `SendWelcomeEmail` has no callers (no registration flow exists). | Delete it or wire it into a signup flow. |
| EmailService.cs | 86-92 | `SendWelcomeEmailHtml` has no callers. | Delete it or wire it in. |
| EmailService.cs | 81-84 | `BuildHtmlTemplate`'s only caller is the unused `SendWelcomeEmailHtml`, making it transitively dead. | Delete it with its caller. |
| TransactionService.cs | 77-85 | `IsWithinDailyLimit` has no callers; the daily limit is never enforced. | Call it from `Transfer` or delete it. |
| TransactionService.cs | 94-97 | `FormatCurrency` has no callers. | Delete it. |
| TransactionService.cs | 99-103 | `RefundTransaction` contains only `throw new NotImplementedException()` in non-stub, routed code. | Implement it or remove the endpoint and method. |
| UserService.cs | 11 | `_requestCount` is incremented in two places but never read anywhere. | Remove it or expose it as a metric. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| TransactionService.cs | 65 | Deposit cap `1000000` is an inline literal. | Named constant or config value. |
| TransactionService.cs | 68 | Interest rate `0.05m` is an inline literal. | Named constant or config value. |
| TransactionService.cs | 50, 73 | Transaction type strings `"Transfer"`/`"Deposit"` are inline literals. | Use an enum or shared constants. |
| TransactionService.cs | 90 | Status string `'Completed'` is an inline literal. | Use an enum or constant. |
| TransactionService.cs | 73 | `FromUserId` `0` is a magic "system" sender id. | Introduce a named `SystemUserId` constant. |
| AuthService.cs | 84 | Token lifetime `30` (days) is an inline literal. | Move to configuration. |
| AuthService.cs | 53 | Username literal `"admin"`. | Constant or config. |
| AuthService.cs | 55 | Role literal `"SuperAdmin"`. | Shared role constants class. |
| UserService.cs | 22 | Max user id `1000000` literal in `GetUserById`. | Named constant. |
| UserService.cs | 42 | Same `1000000` literal repeated in `UpdateUser`. | Same shared constant. |
| UserService.cs | 56 | Same `1000000` literal repeated in `DeleteUser`. | Same shared constant. |
| UserService.cs | 70 | Page-size cap `50` is an inline literal. | Named constant or config. |
| UserController.cs | 32 | Default `pageSize = 20` is an inline literal. | Named constant or config. |
| EmailService.cs | 40 | Sender `"notifications@company.com"` literal in `SendTransferNotification`. | Read from config (e.g., `Email:FromAddress`). |
| EmailService.cs | 69 | Same sender literal repeated in `SendWelcomeEmail`. | Same config value. |
| EmailService.cs | 89 | Same sender literal repeated in `SendWelcomeEmailHtml`. | Same config value. |
| EmailService.cs | 67 | Support address `"support@company.com"` literal. | Move to config. |
| Program.cs / AuthService.cs | 16, 26-27 / 70, 81-82 | Config key strings `"Jwt:SecretKey"`, `"Jwt:Issuer"`, `"Jwt:Audience"` are repeated across files. | Use a strongly-typed Options class. |
| DatabaseHelper.cs | 16 | Fallback connection string literal duplicates appsettings content. | Remove the fallback. |
| StringHelper.cs | 13 | Email max length `254` literal. | Named constant. |
| StringHelper.cs | 22 | Username length bounds `3` and `20` literals. | Named constants. |
| StringHelper.cs | 45, 49-50, 56 | Visible-digit count `4` repeated across the masking methods. | Named constant. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| StringHelper.cs | 31-33 | `JoinWithSeparator` concatenates strings in a loop (O(n²)). | Use `string.Join` or `StringBuilder`. |
| UserService.cs | 87-91 | `GetAuditReport` concatenates strings in a loop (O(n²)). | Use `StringBuilder` or `string.Join`. |
| StringHelper.cs | 16 | `IsValidEmail` creates a `new Regex` on every call. | Use a `static readonly Regex` or `[GeneratedRegex]`. |
| StringHelper.cs | 25 | `IsValidUsername` creates a `new Regex` on every call. | Same fix. |
| UserService.cs | 10 | Mutable static `List<string> _auditLog` is shared across threads with no synchronization. | Use a thread-safe collection or persistent store. |
| UserService.cs | 11, 25, 59 | Static `_requestCount++` is a non-atomic read-modify-write across threads. | Use `Interlocked.Increment`. |
| StringHelper.cs | 65-71 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Call the BCL method. |
| DatabaseHelper.cs | 19-24 | `GetOpenConnection` is a helper designed to leak resource ownership to callers with no documented contract. | Return data, not open connections. |
| UserService.cs | 20-23 | `GetUserById` duplicates the id-validation block. | Extract a shared `ValidateUserId` helper. |
| UserService.cs | 40-43 | `UpdateUser` repeats the same validation block. | Use the shared helper. |
| UserService.cs | 54-57 | `DeleteUser` repeats the same validation block. | Use the shared helper. |
| AuthService.cs | 34-35 | `Login` opens its own `SqlConnection` instead of using the injected `DatabaseHelper`, bypassing the shared data-access pattern. | Use `DatabaseHelper` (with a parameterized API). |
| DatabaseHelper.cs | 42 | `ExecuteQuerySafe` uses `AddWithValue`, which can cause implicit-conversion and plan-cache problems. | Use `Parameters.Add` with explicit `SqlDbType`. |
| EmailService.cs | 50, 73, 91 | `SmtpClient.Send` blocks a request thread on network I/O. | Send asynchronously or via a background queue. |
| EmailService.cs | 56, 77 | `Console.WriteLine` is used for logging in a web application. | Inject `ILogger<EmailService>`. |
| TransactionService.cs | 23-61 | `Transfer` carries 3+ responsibilities (input validation, balance/fee math, persistence, notification) and should be split into `ValidateTransfer`, `ComputeFee`, `ApplyBalanceUpdate`, and `NotifyTransfer` helpers. | Split into named private helpers. |
| AuthService.cs | 28-59 | `Login` carries hashing, SQL access, entity mapping, and backdoor logic and should be split into `VerifyCredentials` and `MapUser` (with the backdoor removed). | Split into named private helpers. |
| EmailService.cs | 34-61 | `SendTransferNotification` mixes body templating, retry policy, and transport and should be split into `BuildTransferBody` and `SendWithRetry`. | Split into named private helpers. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally. | Gate on `IsDevelopment()`. |
| Program.cs | 24 | `ValidateLifetime = false` on JWT validation. | Set to `true`. |
| Program.cs | 36 | HTTPS redirection is commented out. | Re-enable it. |
| Program.cs | 38 | Overly permissive CORS (`AllowAnyOrigin` + `AllowAnyMethod` + `AllowAnyHeader`). | Restrict origins, methods, and headers. |
| appsettings.json | 18-20 | `Debug` log level set for `Default`, `Microsoft`, and `System` in the base config used by production. | Use `Information`/`Warning` via production overrides. |
| appsettings.json | 3, 6, 14 | Secrets (SQL password, JWT key, SMTP password) stored in committed configuration. | Use a secret store and environment-specific overrides. |
| appsettings.json | 3 | `TrustServerCertificate=True` in the production connection string. | Set to `false` with a trusted certificate. |
| appsettings.json | 23 | `AllowedHosts` is `"*"`. | Restrict to known host names. |
| (missing file) | — | No `appsettings.Production.json` or other environment-specific overrides exist. | Add per-environment config files. |
| SampleBankingApp.csproj | 8-9 | `DebugSymbols=true` and `DebugType=full` apply to all configurations. | Restrict full symbols to Debug builds. |
| SampleBankingApp.csproj | 7 | `TreatWarningsAsErrors=false` lets nullable and obsolete warnings slip through. | Enable it (at least in CI). |
| SampleBankingApp.csproj | 15 | Newtonsoft.Json 12.0.3 has a known DoS vulnerability (fixed in 13.0.1) and is not referenced by any source file. | Remove the reference or upgrade to 13.0.3+. |
| SampleBankingApp.csproj | 16 | System.IdentityModel.Tokens.Jwt 7.0.0 is outdated with published security fixes in later releases. | Upgrade to the latest stable 7.x/8.x. |
| SampleBankingApp.csproj | 13 | Microsoft.AspNetCore.Authentication.JwtBearer 8.0.0 is the unpatched GA build; later 8.0.x patches include security fixes. | Update to the latest 8.0.x patch. |
| SampleBankingApp.csproj | 14 | System.Data.SqlClient is in maintenance mode; Microsoft.Data.SqlClient is the supported path. | Migrate to Microsoft.Data.SqlClient. |

## 10. Missing Unit Tests

No test project exists in the repository. The most critical methods and scenarios to cover:

| File | Line | Issue | Fix |
|---|---|---|---|
| TransactionService.cs | 42 | Missing test that a transfer with `balance == amount` but `< amount + fee` is rejected (currently passes and goes negative). | Add boundary tests around the fee-inclusive balance check. |
| TransactionService.cs | 23-61 | Missing test that self-transfers (`fromUserId == toUserId`) are rejected (currently creates money). | Add a self-transfer test. |
| TransactionService.cs | 25 | Missing tests for zero and negative transfer amounts. | Add validation tests. |
| TransactionService.cs | 36-37 | Missing tests for nonexistent sender/recipient ids (currently throws). | Add not-found scenario tests. |
| TransactionService.cs | 39 | Missing tests for fee rounding at half-cent boundaries (`Math.Round` uses banker's rounding by default). | Add rounding tests and pin the rounding mode. |
| TransactionService.cs | 47-50 | Missing test that a failure on the second UPDATE rolls back the first (no transaction today). | Add an atomicity test once a transaction is introduced. |
| TransactionService.cs | 77-85 | Missing test that the daily transaction limit is enforced (method currently uncalled). | Add limit tests after wiring it into `Transfer`. |
| TransactionService.cs | 65-74 | Missing tests for deposit boundaries: 0, negative, 1,000,000, 1,000,001, and nonexistent user. | Add boundary and not-found tests. |
| TransactionService.cs | 68 | Missing test pinning the deposit interest rate (would catch the 5% vs 1% error). | Add a rate-correctness test. |
| AuthService.cs | 28-59 | Missing tests for valid credentials, wrong password, inactive user, and SQL-injection username payloads. | Add auth flow tests including injection strings. |
| AuthService.cs | 61-66 | Missing test asserting passwords are hashed with a salted strong algorithm (would catch MD5). | Add a hashing algorithm test. |
| AuthService.cs | 68-89 | Missing tests that generated JWTs contain the expected claims, expiry, and a valid signature. | Add token generation/validation tests. |
| AuthController.cs | 19-31 | Missing tests for login throttling/lockout behavior. | Add rate-limit tests once implemented. |
| UserService.cs | 68-83 | Missing tests that page 1 returns the first rows (off-by-one), pageSize clamps at 50, and negative page/pageSize are handled. | Add pagination boundary tests. |
| UserService.cs | 18-66 | Missing tests for id boundaries 0, -1, 1,000,000, and 1,000,001 across `GetUserById`/`UpdateUser`/`DeleteUser`. | Add boundary tests. |
| UserService.cs | 95-109 | Missing tests for injection payloads, null/empty query, and the error-vs-empty-result distinction in `SearchUsers`. | Add search tests. |
| UserService.cs | 38-50 | Missing tests for email/username format validation and duplicate usernames in `UpdateUser`. | Add validation tests. |
| StringHelper.cs | 11-27 | Missing tests for email/username validation at boundary lengths and null inputs. | Add boundary and null tests. |
| StringHelper.cs | 43-57 | Missing tests for masking methods with strings shorter than 4 characters. | Add short-input tests. |
| StringHelper.cs | 29-36 | Missing test exposing `JoinWithSeparator`'s trailing separator and empty-input behavior. | Add tests (then delete the method). |
| TransactionController.cs | 26-27, 40-41 | Missing tests that a missing or malformed `NameIdentifier` claim yields 401/400 rather than a 500. | Add claim-parsing tests. |
| UserController.cs | 21-82 | Missing authorization tests proving users cannot read, update, or delete other users' accounts and that audit/user-list endpoints require Admin. | Add ownership/role tests once checks exist. |

---

### Additional commentary

The two most urgent items are the authentication bypass chain in `AuthService.Login` (SQL injection + hardcoded SuperAdmin backdoor + unsalted MD5) and the money-integrity bugs in `TransactionService.Transfer` (fee-excluding balance check, self-transfer money creation, and no DB transaction). I would block deployment on those, then address the committed secrets (rotate all of them — SQL `sa`, JWT key, SMTP password) since they must be considered compromised. Finally, note that several planted "fixed" alternatives (`JoinWithSeparatorFixed`, `ExecuteQuerySafe`, `IsValidEmail`) already exist in the codebase — prefer wiring callers to those rather than writing new code.