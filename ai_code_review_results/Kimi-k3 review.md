# Peer Code Review — SampleBankingApp (main @ 00111c5)

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 32 | `Login` interpolates `username` and `hashedPassword` into SQL, allowing auth bypass via `' OR '1'='1`. | Use a parameterized `SqlCommand` with `@username`/`@password`. |
| AuthService.cs | 17 | Hardcoded backdoor credential `AdminBypassPassword = "SuperAdmin2024"` is committed to source. | Delete the constant entirely. |
| AuthService.cs | 53-56 | `Login` returns a `SuperAdmin` user when `username == "admin"` and the backdoor password matches. | Remove the bypass branch. |
| AuthService.cs | 30, 61-66 | `HashPasswordMd5` uses unsalted MD5 for password verification. | Migrate to PBKDF2/bcrypt/ASP.NET Core Identity password hasher. |
| AuthService.cs | 91-96 | `HashPasswordSha1` uses weak SHA1 (also unused). | Delete the method. |
| AuthService.cs | 84 | `GenerateJwtToken` issues tokens valid for 30 days. | Use a short expiry (e.g. 15-60 minutes) with refresh tokens. |
| AuthService.cs | 98-103 | `ValidateToken` returns `true` for any non-empty string without checking signature or expiry. | Validate with `JwtSecurityTokenHandler.ValidateToken` or delete. |
| Program.cs | 24 | `ValidateLifetime = false` means expired JWTs are accepted. | Set to `true`. |
| Program.cs | 34 | `UseDeveloperExceptionPage()` runs unconditionally, leaking stack traces in production. | Call only when `app.Environment.IsDevelopment()`. |
| Program.cs | 36 | `app.UseHttpsRedirection()` is commented out. | Re-enable it. |
| Program.cs | 38 | CORS allows any origin, method, and header. | Restrict to known origins and required methods. |
| appsettings.json | 3 | Production SQL `sa` password `Admin1234!` is committed to source control. | Move to environment variables/Key Vault and rotate the password. |
| appsettings.json | 6 | JWT secret `mysecretkey` is weak, short, and committed. | Use a long random secret stored outside the repo. |
| appsettings.json | 14 | SMTP password `EmailPass99` is committed. | Move to a secret store and rotate. |
| DatabaseHelper.cs | 16 | Hardcoded fallback connection string embeds `sa` credentials. | Throw if `DefaultConnection` is missing instead of falling back. |
| DatabaseHelper.cs | 26-34 | `ExecuteQuery(tableName, whereClause)` accepts raw SQL fragments, enabling injection. | Remove it or accept only parameterized predicates. |
| UserService.cs | 47 | `UpdateUser` interpolates `email` and `username` into an UPDATE statement. | Parameterize with `@Email`, `@Username`, `@Id`. |
| UserService.cs | 61 | `DeleteUser` interpolates `id` into a DELETE statement (int-typed but unsafe pattern). | Parameterize with `@Id`. |
| UserService.cs | 99 | `SearchUsers` interpolates `query` into a LIKE clause. | Use `@q` parameter with escaped wildcards. |
| TransactionService.cs | 47 | Sender balance UPDATE is built by interpolation. | Parameterize. |
| TransactionService.cs | 48 | Recipient balance UPDATE is built by interpolation. | Parameterize. |
| TransactionService.cs | 70-71 | Deposit balance UPDATE is built by interpolation. | Parameterize. |
| TransactionService.cs | 89-90 | `RecordTransaction` interpolates `description` (user-controlled) into an INSERT. | Parameterize all values. |
| UserController.cs | 22 | `GetUser` has no ownership or role check, so any authenticated user can read any account (IDOR). | Compare `id` to the caller's claim or require Admin. |
| UserController.cs | 32 | `GetUsers` lists all users with no role restriction. | Require an Admin role. |
| UserController.cs | 39 | `UpdateUser` lets any authenticated user modify any other user's record. | Enforce ownership or Admin role. |
| UserController.cs | 57 | `DeleteUser` lets any authenticated user delete any account. | Require Admin role. |
| UserController.cs | 79 | `GetAuditLog` exposes the audit log (containing emails) to any authenticated user. | Require Admin role. |
| TransactionController.cs | 49 | `Refund` has no ownership/role check on the target transaction. | Authorize against the transaction's participants or Admin. |
| EmailService.cs | 29 | `EnableSsl = false` sends SMTP credentials and message bodies in cleartext. | Set `EnableSsl = true`. |
| SampleBankingApp.csproj | 8-9 | `DebugSymbols`/`DebugType full` ship full debug symbols in release builds. | Restrict to Debug configuration. |
| AuthController.cs | 34-38 | `LoginRequest` has no `[Required]` validation attributes. | Add data annotations. |
| UserController.cs | 85-89 | `UpdateUserRequest` has no validation attributes. | Add `[Required]`/`[EmailAddress]`/`[StringLength]`. |
| Models/Transaction.cs | 15-25 | `TransferRequest`/`DepositRequest` lack `[Range]` validation on `Amount`. | Add `[Range(0.01, ...)]`. |
| UserService.cs | 45 | Audit log stores user email PII in a plain in-memory list exposed via an endpoint. | Persist securely with access control and redaction. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserService.cs | 72 | `skip = page * pageSize` is off by one — page 1 skips the first `pageSize` rows. | Use `(page - 1) * pageSize`. |
| UserService.cs | 68-72 | `GetUsersPage` never validates `page < 1` or `pageSize <= 0`, producing a negative OFFSET SQL error. | Validate and clamp both parameters. |
| UserService.cs | 70 | `pageSize` is silently clamped to 50 instead of validated, hiding caller bugs. | Reject invalid values explicitly. |
| TransactionService.cs | 25 | `amount < 0` permits zero-amount transfers (fee churn, spam notifications). | Use `amount <= 0`. |
| TransactionService.cs | 42 | Balance check `fromBalance >= amount` ignores the fee, but `amount + fee` is debited, allowing a negative balance. | Compare against `totalDebit`. |
| TransactionService.cs | 42-48 | No self-transfer check: when `fromUserId == toUserId` the second UPDATE overwrites with `toBalance + amount`, creating money from nothing. | Reject transfers where sender equals recipient. |
| TransactionService.cs | 68 | `Deposit` adds a 5% bonus (`amount * 0.05m * 1`) on every deposit — almost certainly the wrong rate and freely abusable. | Remove or drive from configuration with a cap. |
| TransactionService.cs | 77-85 | `IsWithinDailyLimit` is never called, so `MaxTransactionsPerDay` is never enforced. | Invoke it in `Transfer` (and `Deposit` if intended). |
| TransactionService.cs | 73 | Deposit records `FromUserId = 0`, which references no real user. | Use a nullable column or a designated system account. |
| StringHelper.cs | 56 | `ObfuscateAccount` throws `ArgumentOutOfRangeException` for accounts shorter than 4 characters. | Guard with a length check. |
| StringHelper.cs | 31-35 | `JoinWithSeparator` leaves a trailing separator on the result. | Use `string.Join`. |
| AuthService.cs | 55 | The backdoor user is assigned `Id = 0`, colliding with the "system" id used in deposits. | Remove the backdoor. |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserService.cs | 105-108 | `SearchUsers` catches broad `Exception` and returns an empty list, so callers cannot distinguish errors from no results. | Log and let a 500 propagate, or return a result wrapper. |
| EmailService.cs | 75-78 | `SendWelcomeEmail` swallows all exceptions with only `Console.WriteLine`. | Log via `ILogger` and decide on retry/propagation. |
| TransactionService.cs | 47-50 | `Transfer` performs two UPDATEs plus an INSERT with no transaction, so a mid-failure loses money. | Wrap all three writes in a `SqlTransaction`. |
| TransactionService.cs | 70-73 | `Deposit` UPDATE and transaction INSERT are not atomic. | Wrap in a transaction. |
| TransactionService.cs | 52-55 | The notification email is sent after the DB writes commit, and a rethrown `SmtpException` surfaces as a 500 even though the transfer succeeded. | Queue the email out-of-band or catch and log it. |
| UserController.cs | 52 | 500 response returns raw `ex.Message` to the client. | Return a generic message and log the exception. |
| UserController.cs | 48 | 400 response returns raw `ex.Message`. | Return a sanitized validation message. |
| AuthController.cs | 20-31 | Login endpoint has no rate limiting or account lockout, enabling brute force. | Add rate-limiting middleware and lockout counters. |
| TransactionController.cs | 56-59 | `Refund` catches `NotImplementedException` and returns 500 from a live route. | Remove the route until implemented. |
| TransactionController.cs | 27 | `int.Parse(userIdClaim!)` throws an unhandled `FormatException`/`ArgumentNullException`. | Use `int.TryParse` and return 401 on failure. |
| TransactionController.cs | 41 | Same unguarded `int.Parse` in `Deposit`. | Same fix. |
| EmailService.cs | 56, 77 | Failures are written with `Console.WriteLine` instead of structured logging. | Inject and use `ILogger<EmailService>`. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 34-35 | `Login` opens a `SqlConnection` that is never closed or disposed on any path. | Wrap in `using`. |
| AuthService.cs | 37-38 | `SqlCommand` and `SqlDataReader` are never disposed, and the early `return` at line 42 leaks both plus the connection. | Use `using` declarations for all three. |
| DatabaseHelper.cs | 28 | `ExecuteQuery` never closes the connection obtained from `GetOpenConnection`. | Use `using` for the connection. |
| DatabaseHelper.cs | 29-30 | `ExecuteQuery` never disposes its `SqlCommand` or `SqlDataAdapter`. | Use `using`. |
| DatabaseHelper.cs | 52-55 | `ExecuteNonQuery` skips `connection.Close()` whenever `ExecuteNonQuery` throws. | Use `using` instead of manual `Close()`. |
| DatabaseHelper.cs | 53 | `ExecuteNonQuery` never disposes its `SqlCommand`. | Use `using`. |
| DatabaseHelper.cs | 19-24 | `GetOpenConnection` hands an open connection to callers with no ownership contract, and every caller leaks it. | Make it private and refactor callers to self-contained `using` blocks. |
| DatabaseHelper.cs | 44 | `ExecuteQuerySafe` does not dispose its `SqlDataAdapter`. | Use `using`. |
| DatabaseHelper.cs | 74 | `ExecuteQueryWithParams` does not dispose its `SqlDataAdapter`. | Use `using`. |
| DatabaseHelper.cs | 63 | `TableExists` does not dispose the schema `DataTable`. | Use `using`. |
| EmailService.cs | 16 | `SmtpClient` is held as an instance field — it is not thread-safe and its socket is never released. | Create and dispose a client per send inside a `using`. |
| EmailService.cs | 39-43 | `MailMessage` in `SendTransferNotification` is never disposed. | Use `using`. |
| EmailService.cs | 69 | `MailMessage` in `SendWelcomeEmail` is never disposed. | Use `using`. |
| EmailService.cs | 89-90 | `MailMessage` in `SendWelcomeEmailHtml` is never disposed. | Use `using`. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 16, 28 | `jwtSecret` may be null, and `Encoding.UTF8.GetBytes(jwtSecret!)` then throws at startup. | Validate configuration at startup and fail with a clear message. |
| AuthService.cs | 70 | `_config["Jwt:SecretKey"]!` may be null, throwing inside `GetBytes` on every token request. | Validate once in the constructor. |
| AuthService.cs | 34 | `GetConnectionString("DefaultConnection")` may return null, causing `Open()` to throw. | Null-check with a descriptive exception. |
| TransactionController.cs | 26-27 | `User.FindFirst(...)?.Value` can be null, and `int.Parse(userIdClaim!)` then throws. | Null-check and return 401. |
| TransactionController.cs | 40-41 | Same null-claim risk in `Deposit`. | Same fix. |
| TransactionService.cs | 36 | `fromUserTable.Rows[0]` is accessed without checking `Rows.Count`, throwing `IndexOutOfRangeException` for an unknown sender. | Check `Rows.Count == 0` and return a failure result. |
| TransactionService.cs | 37 | Same unchecked `Rows[0]` for the recipient. | Same fix. |
| TransactionService.cs | 53-55 | `(string)` casts on `Email`/`Username` throw if the columns are `DBNull`. | Use `Convert.ToString` or null-guards. |
| EmailService.cs | 22 | `_config["Email:SmtpHost"]` may be null, throwing in the `SmtpClient` constructor. | Validate configuration. |
| EmailService.cs | 24 | `int.Parse` on `Email:SmtpPort` throws `FormatException` if the value is non-numeric. | Use `int.TryParse` with a default. |
| EmailService.cs | 65 | `username.ToUpper()` is called before any null check. | Null-check the parameter first. |
| StringHelper.cs | 13 | `email.Length` is read before any null check. | Guard with `string.IsNullOrEmpty`. |
| StringHelper.cs | 22 | `username.Length` is read before any null check. | Guard first. |
| StringHelper.cs | 45 | `accountNumber.Length` is read before any null check. | Guard first. |
| StringHelper.cs | 56 | `account[^4..]` throws on null input or length under 4. | Guard null and length. |
| AuthController.cs | 22 | `request.Username`/`request.Password` can be null from JSON despite the initializers. | Add `[Required]` or explicit null checks. |
| UserController.cs | 43 | `request.Email`/`request.Username` can be null from JSON. | Add validation attributes. |
| UserService.cs | 115-121 | `MapRowToUser` direct casts throw on any `DBNull` column. | Use defensive conversion. |
| AuthService.cs | 44-49 | Reader casts throw on `DBNull` values. | Use defensive conversion. |

## 6. Dead Code

Method inventory was built across all controllers, services, helpers, and data classes, then each name was searched for callers; controller actions are route-invoked entry points and were treated as reachable.

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 59-65 | `TableExists` has no callers anywhere in the source. | Delete or wire into a startup check. |
| DatabaseHelper.cs | 67-78 | `ExecuteQueryWithParams` is `[Obsolete]` and has no callers. | Delete it. |
| StringHelper.cs | 11-18 | `IsValidEmail` has no callers. | Delete or use in request validation. |
| StringHelper.cs | 20-27 | `IsValidUsername` has no callers. | Delete or use in `UpdateUser`. |
| StringHelper.cs | 29-36 | `JoinWithSeparator` has no callers and is the broken duplicate of `JoinWithSeparatorFixed`. | Delete it. |
| StringHelper.cs | 38-41 | `JoinWithSeparatorFixed` has no callers. | Delete it. |
| StringHelper.cs | 43-52 | `MaskAccountNumber` has no callers. | Delete or use where account numbers are displayed. |
| StringHelper.cs | 54-57 | `ObfuscateAccount` has no callers and duplicates `MaskAccountNumber`. | Delete one of the pair. |
| StringHelper.cs | 59-63 | `ToTitleCase` has no callers. | Delete it. |
| StringHelper.cs | 65-71 | `IsBlank` has no callers. | Delete it. |
| AuthService.cs | 91-96 | `HashPasswordSha1` has no callers. | Delete it. |
| AuthService.cs | 98-108 | `ValidateToken` has no callers. | Delete or implement properly. |
| AuthService.cs | 105-107 | Code after the unconditional `return true;` in `ValidateToken` is unreachable. | Remove the dead lines. |
| EmailService.cs | 63-79 | `SendWelcomeEmail` has no callers. | Delete or call it from a registration flow. |
| EmailService.cs | 86-92 | `SendWelcomeEmailHtml` has no callers. | Delete it. |
| EmailService.cs | 81-84 | `BuildHtmlTemplate` is only called by the dead `SendWelcomeEmailHtml`, making it transitively dead. | Delete with its caller. |
| TransactionService.cs | 77-85 | `IsWithinDailyLimit` has no callers, so the daily limit is never enforced. | Call it from `Transfer` or delete it. |
| TransactionService.cs | 94-97 | `FormatCurrency` has no callers. | Delete it. |
| TransactionService.cs | 99-103 | `RefundTransaction` is reachable via a live route but only throws `NotImplementedException`. | Implement it or remove the route. |
| UserService.cs | 11, 25, 59 | `_requestCount` is incremented but never read anywhere. | Remove the field or expose it meaningfully. |
| DatabaseHelper.cs | 26-34 vs 36-48 | The broken `ExecuteQuery` is still the one called by `SearchUsers` while the fixed `ExecuteQuerySafe` exists alongside it. | Migrate `SearchUsers` to `ExecuteQuerySafe` and delete `ExecuteQuery`. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 65 | Deposit cap `1000000` is an inline literal. | Move to a named constant or configuration. |
| TransactionService.cs | 68 | Interest rate `0.05m` (and the no-op `* 1`) is an inline literal. | Move to configuration with a descriptive name. |
| UserService.cs | 22 | Max user id `1000000` literal in `GetUserById`. | Extract a shared constant. |
| UserService.cs | 42 | Same `1000000` literal repeated in `UpdateUser`. | Use the shared constant. |
| UserService.cs | 56 | Same `1000000` literal repeated in `DeleteUser`. | Use the shared constant. |
| UserService.cs | 70 | Max page size `50` is an inline literal. | Named constant or configuration. |
| UserController.cs | 32 | Default `pageSize = 20` is an inline literal. | Named constant. |
| StringHelper.cs | 13 | Email length limit `254` is an inline literal. | Named constant. |
| StringHelper.cs | 22 | Username bounds `3` and `20` are inline literals. | Named constants. |
| StringHelper.cs | 45-50 | Visible digit count `4` in `MaskAccountNumber`. | Named constant. |
| StringHelper.cs | 56 | Same `4` repeated in `ObfuscateAccount`. | Named constant. |
| EmailService.cs | 40 | Sender address `notifications@company.com` hardcoded in `SendTransferNotification`. | Move to configuration. |
| EmailService.cs | 69 | Same sender address repeated in `SendWelcomeEmail`. | Use the configured value. |
| EmailService.cs | 89 | Same sender address repeated in `SendWelcomeEmailHtml`. | Use the configured value. |
| EmailService.cs | 67 | Support address `support@company.com` hardcoded in the body. | Move to configuration. |
| EmailService.cs | 24 | Default port `"25"` is a string literal. | Named constant. |
| AuthService.cs | 53 | Username literal `"admin"`. | Named constant (or delete with the backdoor). |
| AuthService.cs | 55 | Role literal `"SuperAdmin"`. | Centralize role names. |
| AuthService.cs | 84 | Token lifetime `30` days is an inline literal. | Move to configuration. |
| TransactionService.cs | 50, 73, 90 | Type/status literals `"Transfer"`, `"Deposit"`, `"Completed"`. | Use an enum or constants. |
| Program.cs / AuthService.cs | 16 / 70 | Config key `"Jwt:SecretKey"` repeated in two files. | Use a shared constants class or options pattern. |
| DatabaseHelper.cs / AuthService.cs | 15 / 34 | Config key `"DefaultConnection"` repeated in two files. | Shared constant or options pattern. |
| DatabaseHelper.cs | 16 | A full fallback connection string is hardcoded instead of living only in configuration. | Remove the fallback. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 31-35 | `JoinWithSeparator` concatenates strings in a loop (O(n²)) and reimplements `string.Join` incorrectly. | Replace with `string.Join`. |
| UserService.cs | 87-91 | `GetAuditReport` concatenates strings in a loop. | Use `string.Join("\n", _auditLog)`. |
| StringHelper.cs | 16 | `new Regex(...)` is constructed on every `IsValidEmail` call. | Make it `static readonly` or use `GeneratedRegex`. |
| StringHelper.cs | 25 | Same per-call `new Regex(...)` in `IsValidUsername`. | Same fix. |
| UserService.cs | 10 | `_auditLog` is shared mutable static state (a `List<string>`) mutated from requests with no synchronization and unbounded growth. | Use a thread-safe store or a real logging/audit pipeline. |
| UserService.cs | 11, 25, 59 | `_requestCount++` on a static field is not atomic across threads. | Use `Interlocked.Increment` or remove it. |
| StringHelper.cs | 65-71 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Call the BCL method. |
| DatabaseHelper.cs | 19-24 | `GetOpenConnection` is a helper designed to leak resource ownership to callers with no documented contract. | Make it private and give each method self-contained `using` blocks. |
| UserService.cs | 20-23 | The `id <= 0` / `id > 1000000` validation block is duplicated in `GetUserById`. | Extract a shared `ValidateUserId` helper. |
| UserService.cs | 40-43 | Same validation block duplicated in `UpdateUser`. | Use the shared helper. |
| UserService.cs | 54-57 | Same validation block duplicated in `DeleteUser`. | Use the shared helper. |
| TransactionController.cs | 26-27 | Claim lookup plus `int.Parse` is duplicated in `Transfer`. | Extract a `GetCallerUserId()` helper. |
| TransactionController.cs | 40-41 | Same claim-parsing block duplicated in `Deposit`. | Use the shared helper. |
| TransactionService.cs | 23-61 | `Transfer` carries four-plus responsibilities (input validation, balance/fee math, persistence, notification) and should be split into named private helpers such as `ValidateTransfer`, `CalculateFee`, `ApplyBalanceUpdates`, and `NotifyParties`. | Split into those helpers. |
| AuthService.cs | 28-59 | `Login` mixes raw SQL access, reader-to-model mapping, and backdoor logic, and should be split into `FindUserByCredentials` and `MapReaderToUser` (with the backdoor removed). | Split and remove the backdoor. |
| EmailService.cs | 34-61 | `SendTransferNotification` mixes body construction, message creation, and retry policy, and should be split into `BuildTransferBody` and `SendWithRetry`. | Split into those helpers. |
| EmailService.cs | 56, 77 | `Console.WriteLine` is used for operational logging. | Inject `ILogger<EmailService>`. |
| AuthService.cs | 42-50 | `Login` hand-maps a reader to `User`, duplicating `UserService.MapRowToUser`. | Share one mapping helper. |
| AuthService.cs | 32 | `SELECT *` fetches columns the login flow does not need. | Project only required columns. |
| UserService.cs | 28, 75 | `SELECT *` used in `GetUserById` and `GetUsersPage`. | Project explicit columns. |
| TransactionService.cs | 29, 33 | `SELECT *` used for both balance lookups in `Transfer`. | Select only `Balance`, `Email`, `Username`. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally. | Gate on `IsDevelopment()`. |
| Program.cs | 24 | `ValidateLifetime = false` on JWT validation. | Set to `true`. |
| Program.cs | 36 | HTTPS redirection is commented out. | Re-enable. |
| Program.cs | 38 | Overly permissive CORS (`AllowAnyOrigin` + `AllowAnyMethod` + `AllowAnyHeader`). | Whitelist origins and methods. |
| appsettings.json | 18-20 | `Debug` log level is set for `Default`, `Microsoft`, and `System` in what is effectively production config. | Use `Information`/`Warning` in production. |
| appsettings.json | 3, 6, 14 | Production secrets (DB password, JWT key, SMTP password) are committed. | Use user-secrets/env vars/Key Vault. |
| appsettings.json | 6 | `SecretKey` value `mysecretkey` is too short and weak for HS256. | Use a 32+ byte random key. |
| appsettings.json | 23 | `AllowedHosts: "*"` permits any Host header. | List expected hosts. |
| SampleBankingApp.csproj | 8-9 | `DebugSymbols`/`DebugType full` apply to all configurations including Release. | Move to a Debug-only `PropertyGroup`. |
| SampleBankingApp.csproj | 15 | `Newtonsoft.Json` 12.0.3 is outdated and affected by a known DoS advisory fixed in 13.0.1, and nothing in the source uses it. | Upgrade to 13.0.3+ or remove the reference. |
| SampleBankingApp.csproj | 14 | `System.Data.SqlClient` is in maintenance mode. | Migrate to `Microsoft.Data.SqlClient`. |
| SampleBankingApp.csproj | 16 | `System.IdentityModel.Tokens.Jwt` 7.0.0 is pinned alongside JwtBearer 8.0.0, risking assembly version conflicts. | Align both to the same 8.x line. |
| SampleBankingApp.csproj | 7 | `TreatWarningsAsErrors` is false, letting nullable warnings (which flag several bugs above) pass silently. | Set to true and fix warnings. |
| Repository | — | No `appsettings.Production.json` or other environment-specific override files exist. | Add per-environment config with non-secret overrides. |

## 10. Missing Unit Tests

No test project exists in the repository; the following are the most critical methods and scenarios to cover.

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 23-61 | Test `Transfer` where `fromBalance == amount` but `< amount + fee` to prove the overdraw hole. | Add tests once a seam (interface over `DatabaseHelper`) exists. |
| TransactionService.cs | 23-61 | Test self-transfer (`fromUserId == toUserId`) to prove the money-creation bug. | Add a rejection test. |
| TransactionService.cs | 25 | Test zero and negative amounts. | Boundary tests. |
| TransactionService.cs | 36-37 | Test unknown sender/recipient ids returning a clean failure instead of `IndexOutOfRangeException`. | Add tests. |
| TransactionService.cs | 47-50 | Test that a failure on the second UPDATE rolls back the first (requires the transaction fix). | Add atomicity test. |
| TransactionService.cs | 77-85 | Test that the daily transaction limit is enforced (would have caught the uncalled method). | Add limit tests. |
| TransactionService.cs | 63-75 | Test `Deposit` boundaries at 0, 1, 1,000,000, and 1,000,001, and verify the credited amount matches the intended bonus policy. | Add boundary tests. |
| UserService.cs | 68-83 | Test `GetUsersPage` page 1 returns the first `pageSize` rows (would catch the off-by-one), plus negative page and oversized pageSize. | Add pagination tests. |
| UserService.cs | 18-66 | Test id validation boundaries (0, -1, 1,000,000, 1,000,001) for `GetUserById`, `UpdateUser`, `DeleteUser`. | Add boundary tests. |
| UserService.cs | 95-109 | Test `SearchUsers` with injection payloads and verify errors are not swallowed as empty results. | Add tests after parameterization. |
| AuthService.cs | 28-59 | Test `Login` rejects SQL injection in `username`, rejects wrong passwords, rejects inactive users, and contains no backdoor path. | Add auth tests. |
| AuthService.cs | 68-89 | Test `GenerateJwtToken` emits the expected claims and a sane expiry. | Add token tests. |
| AuthController.cs | 20-31 | Test 401 on bad credentials and 200 with a token on success. | Add controller/integration tests. |
| TransactionController.cs | 26-27, 40-41 | Test that a missing NameIdentifier claim yields 401 rather than a 500. | Add tests. |
| StringHelper.cs | 11-57 | Test email/username validators and account masking at lengths 0, 3, 4, 5 (would catch the `ObfuscateAccount` crash). | Add edge-case tests. |
| DatabaseHelper.cs | 36-48 | Test `ExecuteQuerySafe` binds parameters without concatenation. | Add data-layer tests against a test DB. |

---

### Additional commentary

The three most urgent items are the SQL injection in `AuthService.Login` (trivial authentication bypass), the hardcoded admin backdoor in `AuthService`, and the self-transfer money-creation bug combined with the fee-excluding balance check in `TransactionService.Transfer` — all four are directly exploitable for account takeover or financial loss. Closely behind are the committed production credentials, `ValidateLifetime = false`, and the missing ownership checks on every `UserController` mutation endpoint. I recommend blocking any release until Category 1 and the `Transfer` logic errors are resolved, then addressing the transaction-atomicity and resource-disposal issues, which are the next most likely to cause production incidents.