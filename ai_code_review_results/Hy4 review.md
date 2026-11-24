## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/AuthController.cs | 19 | `Login` has no rate limiting or account lockout, enabling brute-force password guessing. | Add per-user and per-IP throttling plus progressive lockout backed by a durable store. |
| SampleBankingApp/Controllers/AuthController.cs | 20 | `Login` accepts a model-bound `LoginRequest` without `[Authorize]` being relevant but also without anti-automation controls such as CAPTCHA or throttling. | Apply an authentication rate-limit policy to the endpoint. |
| SampleBankingApp/Controllers/TransactionController.cs | 48 | `Refund` is protected only by `[Authorize]` and lacks an admin or ownership authorization check. | Require an admin role and verify the caller owns or is permitted to refund the transaction. |
| SampleBankingApp/Controllers/TransactionController.cs | 48 | `Refund` accepts any `transactionId` without checking that the transaction belongs to the authenticated user. | Load the transaction and compare its owner to `ClaimTypes.NameIdentifier` before refunding. |
| SampleBankingApp/Controllers/UserController.cs | 21 | `GetUser` allows any authenticated user to read any user record including `Password`, `Email`, `Role`, and `Balance`. | Restrict to self or admin and return a DTO that excludes password and sensitive fields. |
| SampleBankingApp/Controllers/UserController.cs | 31 | `GetUsers` allows any authenticated user to enumerate all users. | Add an admin-only `[Authorize(Roles = "Admin")]` policy and return a safe DTO. |
| SampleBankingApp/Controllers/UserController.cs | 38 | `UpdateUser` has no ownership or role check, so any authenticated user can modify any account. | Compare `id` to the authenticated user id or require an admin role. |
| SampleBankingApp/Controllers/UserController.cs | 56 | `DeleteUser` has no ownership or role check, so any authenticated user can delete any account. | Require admin authorization and prevent deletion of the caller's own admin account if required. |
| SampleBankingApp/Controllers/UserController.cs | 71 | `SearchUsers` allows any authenticated user to enumerate user records by arbitrary search. | Restrict to admin or return only non-sensitive directory fields. |
| SampleBankingApp/Controllers/UserController.cs | 78 | `GetAuditLog` exposes an in-memory audit trail to any authenticated user. | Restrict to admin and persist audit entries with access controls. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | `DatabaseHelper` contains a hardcoded fallback SQL Server `sa` password `Admin1234!`. | Remove the fallback and fail startup when `DefaultConnection` is missing. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | `ExecuteQuery` interpolates `tableName` and `whereClause` directly into `SELECT * FROM {tableName} WHERE {whereClause}`. | Replace with a fixed query plus parameterized predicates and a whitelist for table names. |
| SampleBankingApp/Data/DatabaseHelper.cs | 36 | `ExecuteQuerySafe` accepts arbitrary raw SQL fragments from callers, making injection possible if any caller passes untrusted SQL. | Expose typed repository methods with fixed SQL and parameter dictionaries only. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `ExecuteNonQuery` accepts arbitrary raw SQL and is used with interpolated values. | Replace with parameterized command helpers for each write operation. |
| SampleBankingApp/Data/DatabaseHelper.cs | 68 | `ExecuteQueryWithParams` is `[Obsolete]` but still accepts arbitrary raw SQL. | Remove the obsolete method or make it private with fixed SQL templates. |
| SampleBankingApp/Program.cs | 16 | `Jwt:SecretKey` is read without validation and may be null or too short for HMAC-SHA256. | Validate key length at startup and load it from a secure secret store. |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` allows expired JWTs to be accepted indefinitely. | Set `ValidateLifetime = true` and configure `ClockSkew` explicitly. |
| SampleBankingApp/Program.cs | 28 | `Encoding.UTF8.GetBytes(jwtSecret!)` uses the committed weak secret `mysecretkey`. | Replace with a high-entropy secret from environment variables or a key vault. |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` is enabled unconditionally in all environments. | Call it only when `app.Environment.IsDevelopment()`. |
| SampleBankingApp/Program.cs | 36 | `UseHttpsRedirection()` is commented out, allowing plaintext HTTP. | Enable HTTPS redirection and enforce HSTS in production. |
| SampleBankingApp/Program.cs | 38 | CORS uses `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`, an open policy. | Define a named policy with an explicit allowed origin list. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `DebugSymbols` is `true` for all builds. | Set `<DebugSymbols>false</DebugSymbols>` for Release or use a Release-only condition. |
| SampleBankingApp/SampleBankingApp.csproj | 9 | `DebugType` is `full` for all builds. | Use `portable` or `none` in Release builds. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | `Newtonsoft.Json` 12.0.3 is outdated and has known historical advisories in the 12.x line. | Upgrade to the current patched 13.x version or remove it if unused. |
| SampleBankingApp/SampleBankingApp.csproj | 16 | `System.IdentityModel.Tokens.Jwt` 7.0.0 is older than the ASP.NET Core 8 stack and may miss security fixes. | Align to the supported 8.x token package version used by the framework. |
| SampleBankingApp/Services/AuthService.cs | 17 | `AdminBypassPassword` is a hardcoded backdoor credential `SuperAdmin2024`. | Remove the bypass entirely and use normal seeded admin accounts with hashed passwords. |
| SampleBankingApp/Services/AuthService.cs | 30 | `Login` hashes passwords with unsalted MD5 via `HashPasswordMd5`. | Use PBKDF2, bcrypt, scrypt, or Argon2id with per-user salts and a migration plan. |
| SampleBankingApp/Services/AuthService.cs | 32 | `Login` interpolates `username` and `hashedPassword` into the SQL string. | Use `ExecuteQuerySafe` with `@Username` and `@Password` parameters. |
| SampleBankingApp/Services/AuthService.cs | 53 | `Login` grants a `SuperAdmin` JWT for the hardcoded admin bypass password. | Delete the bypass branch and rely on database-backed role assignment. |
| SampleBankingApp/Services/AuthService.cs | 61 | `HashPasswordMd5` uses MD5, which is cryptographically broken and unsalted. | Replace with a password hashing library and rehash existing credentials. |
| SampleBankingApp/Services/AuthService.cs | 70 | `GenerateJwtToken` reads `Jwt:SecretKey` with `!` and uses the weak committed key. | Validate configuration at startup and use a strong secret from secure configuration. |
| SampleBankingApp/Services/AuthService.cs | 84 | `GenerateJwtToken` issues tokens valid for 30 days with lifetime validation disabled. | Reduce expiry to minutes or hours and enable lifetime validation. |
| SampleBankingApp/Services/AuthService.cs | 91 | `HashPasswordSha1` uses SHA-1 without salt, which is unsuitable for passwords. | Remove it or replace it with a modern password hash. |
| SampleBankingApp/Services/AuthService.cs | 98 | `ValidateToken` returns `true` for any non-empty token without verifying signature, issuer, audience, or expiry. | Use `JwtSecurityTokenHandler.ValidateToken` with the same `TokenValidationParameters`. |
| SampleBankingApp/Services/EmailService.cs | 29 | `EnableSsl = false` sends SMTP credentials and mail without transport encryption. | Enable SSL/TLS on a secure SMTP port and validate certificates. |
| SampleBankingApp/Services/EmailService.cs | 25 | `NetworkCredential` is built from committed SMTP username and password. | Move SMTP credentials to a secret store and inject them at runtime. |
| SampleBankingApp/Services/TransactionService.cs | 47 | `Transfer` interpolates `newFromBalance` and `fromUserId` into an `UPDATE`. | Use parameterized SQL with decimal and integer parameters. |
| SampleBankingApp/Services/TransactionService.cs | 48 | `Transfer` interpolates `newToBalance` and `toUserId` into an `UPDATE`. | Use parameterized SQL with decimal and integer parameters. |
| SampleBankingApp/Services/TransactionService.cs | 71 | `Deposit` interpolates `amount + interestBonus` and `userId` into an `UPDATE`. | Use parameterized SQL with decimal and integer parameters. |
| SampleBankingApp/Services/TransactionService.cs | 89 | `RecordTransaction` interpolates `type` and `description` into an `INSERT`, allowing quote-based injection. | Use parameterized SQL and normalize `description` before persistence. |
| SampleBankingApp/Services/UserService.cs | 47 | `UpdateUser` interpolates `email`, `username`, and `id` into an `UPDATE`. | Use parameterized SQL and validate email and username before writing. |
| SampleBankingApp/Services/UserService.cs | 61 | `DeleteUser` interpolates `id` into a `DELETE`. | Use parameterized SQL with `@Id`. |
| SampleBankingApp/Services/UserService.cs | 99 | `SearchUsers` interpolates `query` into `Username LIKE '%{query}%'`. | Use a parameterized `LIKE` query with escaped wildcard characters. |
| SampleBankingApp/appsettings.json | 3 | Production SQL Server `sa` password `Admin1234!` is committed to source control. | Remove the secret, rotate the password, and use managed identity or secret configuration. |
| SampleBankingApp/appsettings.json | 6 | JWT secret `mysecretkey` is committed and far too weak. | Rotate the key, store it in a secret manager, and enforce a minimum 256-bit key. |
| SampleBankingApp/appsettings.json | 14 | SMTP password `EmailPass99` is committed to source control. | Rotate the credential and load it from a secure secret store. |
| SampleBankingApp/appsettings.json | 23 | `AllowedHosts` is `*`, permitting any Host header. | Restrict allowed hosts to the known production domains. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/TransactionController.cs | 24 | `Transfer` does not reject a null `TransferRequest` before dereferencing it. | Add `[ApiController]` model validation plus an explicit null guard. |
| SampleBankingApp/Controllers/TransactionController.cs | 38 | `Deposit` does not reject a null `DepositRequest` before dereferencing it. | Add model validation and an explicit null guard. |
| SampleBankingApp/Controllers/UserController.cs | 39 | `UpdateUser` does not reject a null `UpdateUserRequest` before dereferencing it. | Add model validation and an explicit null guard. |
| SampleBankingApp/Controllers/UserController.cs | 72 | `SearchUsers` passes an unvalidated `query` directly to a `LIKE` query. | Validate length and escape `%`, `_`, and `[` before querying. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` returns a `User` rather than a JWT despite its XML comment claiming it returns a JWT. | Correct the comment or return a token DTO from a separate method. |
| SampleBankingApp/Services/AuthService.cs | 40 | `Login` returns immediately after `reader.Read()` and never checks the admin bypass when a normal row exists. | Decide explicit precedence and remove the bypass entirely. |
| SampleBankingApp/Services/AuthService.cs | 98 | `ValidateToken` always returns `true` for any non-empty string, so invalid tokens are considered valid. | Perform full signature and claim validation. |
| SampleBankingApp/Services/AuthService.cs | 105 | Code after `return true;` in `ValidateToken` is unreachable, so expiry is never checked. | Remove the unconditional return and implement validation. |
| SampleBankingApp/Services/EmailService.cs | 34 | `SendTransferNotification` tells the sender they transferred money to the recipient, which may be acceptable but is sent only to the sender and not the recipient. | Clarify the method name or send separate sender and recipient notifications. |
| SampleBankingApp/Services/EmailService.cs | 36 | `SendTransferNotification` formats `amount` without including the fee, so the notification understates the total debit. | Include `amount`, `fee`, and `totalDebit` in the message. |
| SampleBankingApp/Services/TransactionService.cs | 25 | `Transfer` uses `amount < 0`, allowing `amount == 0` and negative-zero-like no-op transfers. | Reject `amount <= 0`. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `Transfer` does not reject `fromUserId == toUserId`, allowing a self-transfer that can create or destroy value through fee handling. | Return a validation error when the source and destination are identical. |
| SampleBankingApp/Services/TransactionService.cs | 42 | `Transfer` checks `fromBalance >= amount` but debits `amount + fee`, allowing a negative balance. | Check `fromBalance >= totalDebit` before writing. |
| SampleBankingApp/Services/TransactionService.cs | 44 | `Transfer` computes `newFromBalance` from a stale read and can overwrite concurrent balance changes. | Use a transactional conditional `UPDATE` with `Balance >= @TotalDebit` and row locking. |
| SampleBankingApp/Services/TransactionService.cs | 45 | `Transfer` computes `newToBalance` from a stale read and can overwrite concurrent credits. | Use an atomic `UPDATE Users SET Balance = Balance + @Amount`. |
| SampleBankingApp/Services/TransactionService.cs | 47 | `Transfer` writes the debit before the credit with no transaction, so a failure can lose money. | Wrap both balance updates and the transaction record in one database transaction. |
| SampleBankingApp/Services/TransactionService.cs | 50 | `Transfer` records the transaction after balance writes without a transaction, so balances can change without an audit row. | Insert the transaction row inside the same atomic transaction. |
| SampleBankingApp/Services/TransactionService.cs | 52 | `Transfer` sends email after the database writes have committed, so email failure returns an error even though money moved. | Use an outbox pattern and return success once the database transaction commits. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `Deposit` credits `amount + interestBonus` but records only `amount`, so the ledger does not match the balance. | Record both the deposit and bonus or remove the bonus. |
| SampleBankingApp/Services/TransactionService.cs | 68 | `Deposit` applies a 5% bonus via `amount * 0.05m * 1`, which appears to be an incorrect rate or unexplained constant. | Replace with a configured bonus rate or remove the bonus entirely. |
| SampleBankingApp/Services/TransactionService.cs | 65 | `Deposit` allows `amount` values with more than two decimal places, producing nonsensical currency balances. | Round or reject amounts with sub-cent precision. |
| SampleBankingApp/Services/TransactionService.cs | 39 | `Transfer` allows `amount` values with more than two decimal places and rounds only the fee. | Validate currency precision before calculating the fee. |
| SampleBankingApp/Services/TransactionService.cs | 77 | `IsWithinDailyLimit` is never called, so `MaxTransactionsPerDay` is not enforced. | Call it at the start of `Transfer` and `Deposit` inside the transaction. |
| SampleBankingApp/Services/TransactionService.cs | 80 | `IsWithinDailyLimit` counts only `FromUserId = @Id`, so deposits with `FromUserId = 0` are excluded. | Count all user-initiated transaction types with an explicit owner column. |
| SampleBankingApp/Services/TransactionService.cs | 99 | `RefundTransaction` throws `NotImplementedException` while exposed through a public HTTP endpoint. | Implement refunds or remove the endpoint until available. |
| SampleBankingApp/Services/UserService.cs | 68 | `GetUsersPage` computes `skip = page * pageSize`, so page 1 skips the first page. | Use `(page - 1) * pageSize`. |
| SampleBankingApp/Services/UserService.cs | 68 | `GetUsersPage` does not validate `page <= 0`, allowing negative `OFFSET` values. | Reject or clamp `page` to a minimum of 1. |
| SampleBankingApp/Services/UserService.cs | 68 | `GetUsersPage` does not validate `pageSize <= 0`, allowing invalid `FETCH NEXT` values. | Reject or clamp `pageSize` to a positive range. |
| SampleBankingApp/Services/UserService.cs | 38 | `UpdateUser` does not validate `email` or `username` before writing. | Use `StringHelper.IsValidEmail` and `StringHelper.IsValidUsername` or data annotations. |
| SampleBankingApp/Services/UserService.cs | 52 | `DeleteUser` hard-deletes users with transactions still referencing them, breaking ledger integrity. | Use soft deletion or block deletion when financial records exist. |
| SampleBankingApp/Services/UserService.cs | 95 | `SearchUsers` returns an empty list on any exception, making errors indistinguishable from no matches. | Let exceptions propagate or return a result type with an error state. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `JoinWithSeparator` appends a trailing separator, unlike `string.Join`. | Use `string.Join(separator, items)` or trim the trailing separator. |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | `ObfuscateAccount` uses `account[^4..]` and throws for strings shorter than four characters. | Guard the length or use `MaskAccountNumber`. |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | `ToTitleCase` uses `CultureInfo.CurrentCulture`, producing culture-dependent output. | Use an invariant or explicitly configured culture. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/AuthController.cs | 20 | `Login` has no handling for database or token-generation failures, producing unhandled 500 responses. | Add exception handling with a generic client message and server-side logging. |
| SampleBankingApp/Controllers/AuthController.cs | 19 | `Login` lacks rate limiting and account lockout on failed authentication. | Add a rate-limit policy and durable failed-attempt tracking. |
| SampleBankingApp/Controllers/TransactionController.cs | 24 | `Transfer` does not catch or translate service/database exceptions. | Add a global exception middleware or controller-level handling with safe messages. |
| SampleBankingApp/Controllers/TransactionController.cs | 38 | `Deposit` does not catch or translate service/database exceptions. | Add centralized exception handling with safe messages. |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | `Refund` catches only `NotImplementedException` and returns a raw 500 string for an expected unimplemented feature. | Return `501 Not Implemented` or remove the endpoint. |
| SampleBankingApp/Controllers/UserController.cs | 48 | `UpdateUser` returns raw `ex.Message` from `ArgumentException` to the client. | Return a validation problem details response with a curated message. |
| SampleBankingApp/Controllers/UserController.cs | 52 | `UpdateUser` returns raw `ex.Message` from a broad `Exception` to the client. | Log the exception and return a generic 500 response. |
| SampleBankingApp/Controllers/UserController.cs | 50 | `UpdateUser` catches broad `Exception` and converts all failures to 500. | Catch specific expected exceptions and use global middleware for the rest. |
| SampleBankingApp/Controllers/UserController.cs | 64 | `DeleteUser` catches broad `Exception` and hides all failures behind a generic message. | Catch specific exceptions and let unexpected failures reach global handlers. |
| SampleBankingApp/Controllers/UserController.cs | 22 | `GetUser` lets `ArgumentException` from `GetUserById` escape as an unhandled 500. | Validate the route id and return `BadRequest` or `ValidationProblem`. |
| SampleBankingApp/Controllers/UserController.cs | 32 | `GetUsers` lets invalid pagination values escape as database errors. | Validate `page` and `pageSize` before calling the service. |
| SampleBankingApp/Controllers/UserController.cs | 72 | `SearchUsers` lets a null or invalid query reach the service. | Validate the query and return `BadRequest` when invalid. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | `ExecuteQuery` has no exception handling or cleanup path for `adapter.Fill` failures. | Use `using` blocks and let exceptions propagate to a global handler. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `ExecuteNonQuery` closes the connection only on the success path. | Use `using` for connection and command so all paths dispose. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` has no exception handling around connection open or reader execution. | Use `using` resources and centralized exception handling. |
| SampleBankingApp/Services/AuthService.cs | 98 | `ValidateToken` silently treats any non-empty token as valid instead of reporting validation errors. | Return a structured validation result with failure reasons. |
| SampleBankingApp/Services/EmailService.cs | 53 | `SendTransferNotification` catches `SmtpException` and retries but rethrows after the final attempt after DB commit. | Queue the notification in an outbox and retry asynchronously. |
| SampleBankingApp/Services/EmailService.cs | 56 | `SendTransferNotification` writes SMTP exception details to `Console.WriteLine` instead of structured logging. | Inject `ILogger<EmailService>` and log with context. |
| SampleBankingApp/Services/EmailService.cs | 75 | `SendWelcomeEmail` catches broad `Exception` and swallows it silently. | Log through `ILogger` and return a result or enqueue a retry. |
| SampleBankingApp/Services/EmailService.cs | 77 | `SendWelcomeEmail` writes swallowed exception details to `Console.WriteLine`. | Use structured logging with the exception object. |
| SampleBankingApp/Services/EmailService.cs | 86 | `SendWelcomeEmailHtml` has no exception handling around `_smtpClient.Send`. | Add logging and a retry or outbox mechanism. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `Transfer` performs two balance writes, a transaction insert, and an email without a database transaction. | Use `SqlTransaction` or a unit-of-work abstraction for all database writes. |
| SampleBankingApp/Services/TransactionService.cs | 52 | `Transfer` performs an email side effect after committed writes, so a throw reports failure after success. | Persist an outbox message in the same transaction and send asynchronously. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `Deposit` performs a balance update and transaction insert without a transaction. | Wrap both writes in one database transaction. |
| SampleBankingApp/Services/TransactionService.cs | 99 | `RefundTransaction` throws `NotImplementedException` as normal runtime behavior. | Implement the method or return a typed unsupported result. |
| SampleBankingApp/Services/UserService.cs | 95 | `SearchUsers` catches broad `Exception` and returns an empty collection. | Remove the catch or return a discriminated result that distinguishes errors. |
| SampleBankingApp/Services/UserService.cs | 38 | `UpdateUser` writes to `_auditLog` before the database write, so failed updates are still audited as calls. | Log the attempt with outcome after the operation or use a durable audit transaction. |
| SampleBankingApp/Services/UserService.cs | 52 | `DeleteUser` writes the audit entry after the database write, so audit and delete are not atomic. | Persist audit entries in the same database transaction. |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage` can leak stack traces and environment details to production clients. | Use `UseExceptionHandler` in non-development environments. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | `GetOpenConnection` returns an opened `SqlConnection` with no documented ownership contract and callers may not dispose it. | Remove the helper or return a connection inside a `using`-based execution callback. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | `ExecuteQuery` obtains `connection` from `GetOpenConnection` and never closes or disposes it. | Wrap the connection in `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | `ExecuteQuery` creates `SqlCommand` and never disposes it. | Wrap the command in `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 30 | `ExecuteQuery` creates `SqlDataAdapter` and never disposes it. | Wrap the adapter in `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 36 | `ExecuteQuerySafe` creates `SqlDataAdapter` and never disposes it. | Wrap the adapter in `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `ExecuteNonQuery` obtains `connection` from `GetOpenConnection` and closes it only on the success path. | Wrap the connection in `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 53 | `ExecuteNonQuery` creates `SqlCommand` and never disposes it. | Wrap the command in `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 63 | `TableExists` creates a `DataTable` from `GetSchema` and never disposes it. | Wrap the schema table in `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 68 | `ExecuteQueryWithParams` creates `SqlDataAdapter` and never disposes it. | Wrap the adapter in `using`. |
| SampleBankingApp/Services/AuthService.cs | 34 | `Login` creates `SqlConnection` and never closes or disposes it. | Wrap the connection in `using`. |
| SampleBankingApp/Services/AuthService.cs | 37 | `Login` creates `SqlCommand` and never disposes it. | Wrap the command in `using`. |
| SampleBankingApp/Services/AuthService.cs | 38 | `Login` creates `SqlDataReader` and never closes or disposes it. | Wrap the reader in `using`. |
| SampleBankingApp/Services/AuthService.cs | 40 | `Login` returns from inside `reader.Read()` without disposing the reader, command, or connection. | Materialize the row, dispose resources, then return. |
| SampleBankingApp/Services/EmailService.cs | 16 | `_smtpClient` is held as an instance field and is not thread-safe or disposable by the service. | Create and dispose `SmtpClient` per send or use a thread-safe mail sender abstraction. |
| SampleBankingApp/Services/EmailService.cs | 39 | `SendTransferNotification` creates `MailMessage` and never disposes it. | Wrap the message in `using`. |
| SampleBankingApp/Services/EmailService.cs | 69 | `SendWelcomeEmail` creates `MailMessage` and never disposes it. | Wrap the message in `using`. |
| SampleBankingApp/Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` creates `MailMessage` and never disposes it. | Wrap the message in `using`. |
| SampleBankingApp/Services/EmailService.cs | 50 | `SendTransferNotification` reuses the same `MailMessage` across retries, which can leave stream or attachment state inconsistent. | Create a fresh `MailMessage` inside each retry attempt. |
| SampleBankingApp/Services/EmailService.cs | 18 | `EmailService` does not implement `IDisposable` even though it owns an `SmtpClient`. | Implement `IDisposable` or remove the long-lived client field. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/AuthController.cs | 22 | `Login` dereferences `request.Username` and `request.Password` without checking `request` for null. | Add `[Required]` model validation and an explicit null guard. |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | `Transfer` calls `int.Parse(userIdClaim!)` on a possibly null claim value. | Use `int.TryParse` and return `Unauthorized` when missing or invalid. |
| SampleBankingApp/Controllers/TransactionController.cs | 29 | `Transfer` dereferences `request.ToUserId`, `request.Amount`, and `request.Description` without checking `request`. | Add model validation and an explicit null guard. |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | `Deposit` calls `int.Parse(userIdClaim!)` on a possibly null claim value. | Use `int.TryParse` and return `Unauthorized` when missing or invalid. |
| SampleBankingApp/Controllers/TransactionController.cs | 43 | `Deposit` dereferences `request.Amount` without checking `request`. | Add model validation and an explicit null guard. |
| SampleBankingApp/Controllers/UserController.cs | 43 | `UpdateUser` dereferences `request.Email` and `request.Username` without checking `request`. | Add model validation and an explicit null guard. |
| SampleBankingApp/Controllers/UserController.cs | 74 | `SearchUsers` passes a possibly null `query` into string interpolation. | Add `[Required]` validation and a null guard. |
| SampleBankingApp/Data/DatabaseHelper.cs | 15 | `GetConnectionString("DefaultConnection")` may return null and is masked by a hardcoded fallback. | Throw a configuration exception when the connection string is missing. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | `ExecuteQuery` dereferences `tableName` and `whereClause` without null checks. | Validate arguments with `ArgumentNullException.ThrowIfNull`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 36 | `ExecuteQuerySafe` dereferences `sql` and `parameters` without null checks. | Validate arguments with `ArgumentNullException.ThrowIfNull`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 42 | `ExecuteQuerySafe` passes dictionary values directly to `AddWithValue`, where null becomes `DBNull` issues. | Convert null values to `DBNull.Value` explicitly. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `ExecuteNonQuery` dereferences `sql` without a null check. | Validate with `ArgumentNullException.ThrowIfNull`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 59 | `TableExists` dereferences `tableName` without a null check. | Validate with `ArgumentNullException.ThrowIfNull`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 68 | `ExecuteQueryWithParams` dereferences `sql` and `parameters` without null checks. | Validate both arguments before use. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `IsValidEmail` dereferences `email.Length` before checking for null. | Use `string.IsNullOrWhiteSpace` or throw on null. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `IsValidUsername` dereferences `username.Length` before checking for null. | Use `string.IsNullOrWhiteSpace` or throw on null. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `JoinWithSeparator` dereferences `items` and `separator` without null checks. | Validate both arguments before iterating. |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | `JoinWithSeparatorFixed` dereferences `items` and `separator` without null checks. | Validate both arguments before calling `string.Join`. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `MaskAccountNumber` dereferences `accountNumber.Length` before checking for null. | Add a null guard or use nullable annotations with validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | `ObfuscateAccount` dereferences `account` with a range operator before checking for null. | Add a null guard and length check. |
| SampleBankingApp/Program.cs | 28 | `Encoding.UTF8.GetBytes(jwtSecret!)` can throw if `Jwt:SecretKey` is missing. | Validate the secret at startup with a clear configuration error. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` dereferences `username` and `password` without null checks. | Validate both arguments before hashing and querying. |
| SampleBankingApp/Services/AuthService.cs | 34 | `new SqlConnection(_config.GetConnectionString("DefaultConnection"))` can receive a null connection string. | Use the validated `DatabaseHelper` connection string or throw on missing config. |
| SampleBankingApp/Services/AuthService.cs | 45 | `Login` casts `reader["Username"]`, `reader["Email"]`, and `reader["Role"]` to `string` without `DBNull` checks. | Use `reader.GetString` with `IsDBNull` checks or a mapper. |
| SampleBankingApp/Services/AuthService.cs | 70 | `GenerateJwtToken` calls `Encoding.UTF8.GetBytes(_config["Jwt:SecretKey"]!)` without a null guard. | Validate the secret in the constructor or startup. |
| SampleBankingApp/Services/AuthService.cs | 76 | `GenerateJwtToken` uses `user.Username` and `user.Role` without null checks. | Validate the `User` argument and required claim fields. |
| SampleBankingApp/Services/EmailService.cs | 22 | `new SmtpClient(_config["Email:SmtpHost"])` can receive a null host. | Validate `Email:SmtpHost` at startup. |
| SampleBankingApp/Services/EmailService.cs | 24 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` can throw on a malformed configured port. | Use configuration binding with validation or `int.TryParse`. |
| SampleBankingApp/Services/EmailService.cs | 26 | `NetworkCredential` receives possibly null `Email:Username` and `Email:Password` values. | Validate both settings at startup. |
| SampleBankingApp/Services/EmailService.cs | 34 | `SendTransferNotification` dereferences `recipientName` without a null check. | Validate arguments with `ArgumentNullException.ThrowIfNull`. |
| SampleBankingApp/Services/EmailService.cs | 65 | `SendWelcomeEmail` calls `username.ToUpper()` before checking for null. | Add a null guard before formatting. |
| SampleBankingApp/Services/EmailService.cs | 81 | `BuildHtmlTemplate` interpolates `title` and `body` without null checks. | Validate arguments or use nullable-safe formatting. |
| SampleBankingApp/Services/EmailService.cs | 88 | `SendWelcomeEmailHtml` dereferences `username` without a null check. | Add a null guard before building the body. |
| SampleBankingApp/Services/TransactionService.cs | 36 | `Transfer` accesses `fromUserTable.Rows[0]` without checking `Rows.Count > 0`. | Return a not-found error when the source user does not exist. |
| SampleBankingApp/Services/TransactionService.cs | 37 | `Transfer` accesses `toUserTable.Rows[0]` without checking `Rows.Count > 0`. | Return a not-found error when the destination user does not exist. |
| SampleBankingApp/Services/TransactionService.cs | 53 | `Transfer` casts `Rows[0]["Email"]` to `string` without a `DBNull` check. | Use a null-safe mapper or `IsDBNull` check. |
| SampleBankingApp/Services/TransactionService.cs | 55 | `Transfer` casts `Rows[0]["Username"]` to `string` without a `DBNull` check. | Use a null-safe mapper or `IsDBNull` check. |
| SampleBankingApp/Services/TransactionService.cs | 83 | `IsWithinDailyLimit` accesses `table.Rows[0]["TxCount"]` without checking `Rows.Count > 0`. | Use `ExecuteScalar`-style helper or check row count first. |
| SampleBankingApp/Services/TransactionService.cs | 90 | `RecordTransaction` interpolates nullable `description` directly into SQL, producing an empty string or invalid SQL for quotes. | Parameterize and convert null to `DBNull.Value`. |
| SampleBankingApp/Services/UserService.cs | 38 | `UpdateUser` dereferences `email` and `username` without null checks. | Validate both arguments before building SQL. |
| SampleBankingApp/Services/UserService.cs | 95 | `SearchUsers` dereferences `query` through interpolation without a null check. | Validate `query` before calling `ExecuteQuery`. |
| SampleBankingApp/Services/UserService.cs | 116 | `MapRowToUser` casts `row["Username"]` to `string` without a `DBNull` check. | Use a null-safe column reader. |
| SampleBankingApp/Services/UserService.cs | 117 | `MapRowToUser` casts `row["Email"]` to `string` without a `DBNull` check. | Use a null-safe column reader. |
| SampleBankingApp/Services/UserService.cs | 118 | `MapRowToUser` casts `row["Role"]` to `string` without a `DBNull` check. | Use a null-safe column reader. |
| SampleBankingApp/Services/UserService.cs | 121 | `MapRowToUser` casts `row["CreatedAt"]` to `DateTime` without a `DBNull` check. | Use a null-safe column reader or make the property nullable. |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/AuthController.cs | 13 | `AuthController.AuthController` is a constructor and has no explicit caller in the provided source, but it is framework-instantiated by DI. | No change required because ASP.NET Core activates it. |
| SampleBankingApp/Controllers/AuthController.cs | 20 | `AuthController.Login` has no explicit caller in the provided source, but it is an HTTP action invoked by routing. | No change required because ASP.NET Core routes to it. |
| SampleBankingApp/Controllers/TransactionController.cs | 17 | `TransactionController.TransactionController` is a constructor and has no explicit caller in the provided source, but it is framework-instantiated by DI. | No change required because ASP.NET Core activates it. |
| SampleBankingApp/Controllers/TransactionController.cs | 24 | `TransactionController.Transfer` has no explicit caller in the provided source, but it is an HTTP action invoked by routing. | No change required because ASP.NET Core routes to it. |
| SampleBankingApp/Controllers/TransactionController.cs | 38 | `TransactionController.Deposit` has no explicit caller in the provided source, but it is an HTTP action invoked by routing. | No change required because ASP.NET Core routes to it. |
| SampleBankingApp/Controllers/TransactionController.cs | 49 | `TransactionController.Refund` has no explicit caller in the provided source, but it is an HTTP action invoked by routing. | No change required because ASP.NET Core routes to it. |
| SampleBankingApp/Controllers/UserController.cs | 15 | `UserController.UserController` is a constructor and has no explicit caller in the provided source, but it is framework-instantiated by DI. | No change required because ASP.NET Core activates it. |
| SampleBankingApp/Controllers/UserController.cs | 22 | `UserController.GetUser` has no explicit caller in the provided source, but it is an HTTP action invoked by routing. | No change required because ASP.NET Core routes to it. |
| SampleBankingApp/Controllers/UserController.cs | 32 | `UserController.GetUsers` has no explicit caller in the provided source, but it is an HTTP action invoked by routing. | No change required because ASP.NET Core routes to it. |
| SampleBankingApp/Controllers/UserController.cs | 39 | `UserController.UpdateUser` has no explicit caller in the provided source, but it is an HTTP action invoked by routing. | No change required because ASP.NET Core routes to it. |
| SampleBankingApp/Controllers/UserController.cs | 57 | `UserController.DeleteUser` has no explicit caller in the provided source, but it is an HTTP action invoked by routing. | No change required because ASP.NET Core routes to it. |
| SampleBankingApp/Controllers/UserController.cs | 72 | `UserController.SearchUsers` has no explicit caller in the provided source, but it is an HTTP action invoked by routing. | No change required because ASP.NET Core routes to it. |
| SampleBankingApp/Controllers/UserController.cs | 79 | `UserController.GetAuditLog` has no explicit caller in the provided source, but it is an HTTP action invoked by routing. | No change required because ASP.NET Core routes to it. |
| SampleBankingApp/Data/DatabaseHelper.cs | 13 | `DatabaseHelper.DatabaseHelper` is called by DI registration in `Program.cs` line 10. | No change required. |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | `DatabaseHelper.GetOpenConnection` is called by `ExecuteQuery` line 28 and `ExecuteNonQuery` line 52. | No change required. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | `DatabaseHelper.ExecuteQuery` is called by `UserService.SearchUsers` line 99. | No change required. |
| SampleBankingApp/Data/DatabaseHelper.cs | 36 | `DatabaseHelper.ExecuteQuerySafe` is called by `AuthService` indirectly only through no call, but is called by `TransactionService` lines 28, 32, 79 and `UserService` lines 27, 74. | No change required. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `DatabaseHelper.ExecuteNonQuery` is called by `TransactionService` lines 47, 48, 70, 91 and `UserService` lines 48, 62. | No change required. |
| SampleBankingApp/Data/DatabaseHelper.cs | 59 | `DatabaseHelper.TableExists` appears only at its own definition and has no caller in the provided source. | Remove `TableExists` or add a startup schema-check caller. |
| SampleBankingApp/Data/DatabaseHelper.cs | 68 | `DatabaseHelper.ExecuteQueryWithParams` is marked `[Obsolete]` and appears only at its own definition. | Remove the obsolete unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | `StringHelper.IsValidEmail` appears only at its own definition and has no caller in the provided source. | Remove it or call it from `UpdateUser` validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | `StringHelper.IsValidUsername` appears only at its own definition and has no caller in the provided source. | Remove it or call it from `UpdateUser` validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `StringHelper.JoinWithSeparator` appears only at its own definition and has no caller in the provided source. | Remove the broken duplicate implementation. |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | `StringHelper.JoinWithSeparatorFixed` appears only at its own definition and has no caller in the provided source. | Remove it or use it wherever joining is needed. |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | `StringHelper.MaskAccountNumber` appears only at its own definition and has no caller in the provided source. | Remove it or use it in account display paths. |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | `StringHelper.ObfuscateAccount` appears only at its own definition and has no caller in the provided source. | Remove it or consolidate with `MaskAccountNumber`. |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | `StringHelper.ToTitleCase` appears only at its own definition and has no caller in the provided source. | Remove it or use it in a display formatter. |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | `StringHelper.IsBlank` appears only at its own definition and has no caller in the provided source. | Remove it and use `string.IsNullOrWhiteSpace`. |
| SampleBankingApp/Program.cs | 7 | Top-level `Program` entry point has no explicit caller in source but is the application host. | No change required. |
| SampleBankingApp/Services/AuthService.cs | 19 | `AuthService.AuthService` is called by DI registration in `Program.cs` line 12. | No change required. |
| SampleBankingApp/Services/AuthService.cs | 28 | `AuthService.Login` is called by `AuthController.Login` line 22. | No change required. |
| SampleBankingApp/Services/AuthService.cs | 61 | `AuthService.HashPasswordMd5` is called by `AuthService.Login` line 30. | No change required. |
| SampleBankingApp/Services/AuthService.cs | 68 | `AuthService.GenerateJwtToken` is called by `AuthController.Login` line 29. | No change required. |
| SampleBankingApp/Services/AuthService.cs | 91 | `AuthService.HashPasswordSha1` appears only at its own definition and has no caller in the provided source. | Remove the unused weak hash helper. |
| SampleBankingApp/Services/AuthService.cs | 98 | `AuthService.ValidateToken` appears only at its own definition and has no caller in the provided source. | Remove it or replace it with a real validator used by middleware. |
| SampleBankingApp/Services/AuthService.cs | 103 | `AuthService.ValidateToken` contains unreachable code after `return true;` at lines 105-107. | Delete the unreachable handler and expiry check. |
| SampleBankingApp/Services/EmailService.cs | 18 | `EmailService.EmailService` is called by DI registration in `Program.cs` line 14. | No change required. |
| SampleBankingApp/Services/EmailService.cs | 34 | `EmailService.SendTransferNotification` is called by `TransactionService.Transfer` line 52. | No change required. |
| SampleBankingApp/Services/EmailService.cs | 63 | `EmailService.SendWelcomeEmail` appears only at its own definition and has no caller in the provided source. | Remove it or call it from a registration flow. |
| SampleBankingApp/Services/EmailService.cs | 81 | `EmailService.BuildHtmlTemplate` is called by `SendWelcomeEmailHtml` line 88. | No change required. |
| SampleBankingApp/Services/EmailService.cs | 86 | `EmailService.SendWelcomeEmailHtml` appears only at its own definition and has no caller in the provided source. | Remove it or call it from a registration flow. |
| SampleBankingApp/Services/TransactionService.cs | 14 | `TransactionService.TransactionService` is called by DI registration in `Program.cs` line 13. | No change required. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `TransactionService.Transfer` is called by `TransactionController.Transfer` line 29. | No change required. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `TransactionService.Deposit` is called by `TransactionController.Deposit` line 43. | No change required. |
| SampleBankingApp/Services/TransactionService.cs | 77 | `TransactionService.IsWithinDailyLimit` appears only at its own definition and has no caller in the provided source. | Call it from `Transfer` and `Deposit` or remove it. |
| SampleBankingApp/Services/TransactionService.cs | 87 | `TransactionService.RecordTransaction` is called by `Transfer` line 50 and `Deposit` line 73. | No change required. |
| SampleBankingApp/Services/TransactionService.cs | 94 | `TransactionService.FormatCurrency` appears only at its own definition and has no caller in the provided source. | Remove it or use it in notification formatting. |
| SampleBankingApp/Services/TransactionService.cs | 99 | `TransactionService.RefundTransaction` is called by `TransactionController.Refund` line 53. | No change required. |
| SampleBankingApp/Services/TransactionService.cs | 102 | `TransactionService.RefundTransaction` throws `NotImplementedException` in non-stub production-facing code. | Implement the refund or remove the endpoint and method. |
| SampleBankingApp/Services/UserService.cs | 13 | `UserService.UserService` is called by DI registration in `Program.cs` line 11. | No change required. |
| SampleBankingApp/Services/UserService.cs | 18 | `UserService.GetUserById` is called by `UserController.GetUser` line 24. | No change required. |
| SampleBankingApp/Services/UserService.cs | 38 | `UserService.UpdateUser` is called by `UserController.UpdateUser` line 43. | No change required. |
| SampleBankingApp/Services/UserService.cs | 52 | `UserService.DeleteUser` is called by `UserController.DeleteUser` line 61. | No change required. |
| SampleBankingApp/Services/UserService.cs | 68 | `UserService.GetUsersPage` is called by `UserController.GetUsers` line 34. | No change required. |
| SampleBankingApp/Services/UserService.cs | 85 | `UserService.GetAuditReport` is called by `UserController.GetAuditLog` line 81. | No change required. |
| SampleBankingApp/Services/UserService.cs | 95 | `UserService.SearchUsers` is called by `UserController.SearchUsers` line 74. | No change required. |
| SampleBankingApp/Services/UserService.cs | 111 | `UserService.MapRowToUser` is called by `GetUserById` line 35, `GetUsersPage` line 80, and `SearchUsers` line 102. | No change required. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `JoinWithSeparator` is a broken duplicate alongside `JoinWithSeparatorFixed`, and neither is called. | Delete both or keep only the fixed implementation and call it. |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | `MaskAccountNumber` and `ObfuscateAccount` are duplicate masking implementations with different behavior and neither is called. | Keep one validated implementation and remove the other. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/UserController.cs | 32 | `GetUsers` hardcodes default `page = 1` and `pageSize = 20` inline. | Define named pagination defaults in configuration or constants. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | `DatabaseHelper` hardcodes a fallback connection string with server, database, user, and password. | Remove the fallback and require configuration. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `IsValidEmail` hardcodes the maximum email length `254`. | Define `MaxEmailLength` as a named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | `IsValidEmail` hardcodes an email regex pattern inline. | Use a static readonly compiled regex or `MailAddress` validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `IsValidUsername` hardcodes minimum length `3` and maximum length `20`. | Define `MinUsernameLength` and `MaxUsernameLength` constants. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | `IsValidUsername` hardcodes a username regex pattern inline. | Use a static readonly compiled regex. |
| SampleBankingApp/Helpers/StringHelper.cs | 49 | `MaskAccountNumber` hardcodes the visible digit count `4`. | Define `VisibleAccountDigits` as a named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | `ObfuscateAccount` hardcodes `"****"` and the range length `4`. | Reuse `VisibleAccountDigits` and a named mask constant. |
| SampleBankingApp/Program.cs | 38 | CORS policy is configured inline with permissive values. | Move allowed origins and methods into configuration. |
| SampleBankingApp/Services/AuthService.cs | 17 | `AdminBypassPassword` hardcodes a backdoor password string. | Remove the backdoor entirely. |
| SampleBankingApp/Services/AuthService.cs | 32 | `Login` hardcodes `IsActive = 1` and the `Users` table shape inline. | Use a repository method with a named active-user query. |
| SampleBankingApp/Services/AuthService.cs | 53 | `Login` hardcodes username `"admin"` and role `"SuperAdmin"`. | Remove the bypass and use configured role constants. |
| SampleBankingApp/Services/AuthService.cs | 55 | `Login` hardcodes `Id = 0` for the bypass admin user. | Remove the bypass user construction. |
| SampleBankingApp/Services/AuthService.cs | 84 | `GenerateJwtToken` hardcodes a 30-day token lifetime with `AddDays(30)`. | Move token lifetime into `Jwt` configuration. |
| SampleBankingApp/Services/EmailService.cs | 10 | `TransferSubject` hardcodes the product name `BankingApp` in a subject. | Move brand text into configuration or resources. |
| SampleBankingApp/Services/EmailService.cs | 11 | `WelcomeSubject` hardcodes the product name `BankingApp` in a subject. | Move brand text into configuration or resources. |
| SampleBankingApp/Services/EmailService.cs | 13 | `MaxRetries` is a named constant but still hardcodes the value `3` in source. | Move retry count into configuration. |
| SampleBankingApp/Services/EmailService.cs | 14 | `SmtpTimeoutMs` is a named constant but still hardcodes `5000` in source. | Move timeout into configuration. |
| SampleBankingApp/Services/EmailService.cs | 24 | `EmailService` hardcodes fallback SMTP port `"25"`. | Require a validated configured port. |
| SampleBankingApp/Services/EmailService.cs | 40 | `SendTransferNotification` hardcodes `notifications@company.com`. | Move the sender address into configuration. |
| SampleBankingApp/Services/EmailService.cs | 67 | `SendWelcomeEmail` hardcodes `support@company.com`. | Move the support address into configuration. |
| SampleBankingApp/Services/EmailService.cs | 69 | `SendWelcomeEmail` repeats `notifications@company.com`. | Reuse a configured sender address constant. |
| SampleBankingApp/Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` repeats `notifications@company.com`. | Reuse a configured sender address constant. |
| SampleBankingApp/Services/TransactionService.cs | 11 | `TransactionFeeRate` hardcodes `0.015m` in source. | Move the fee rate into configuration. |
| SampleBankingApp/Services/TransactionService.cs | 12 | `MaxTransactionsPerDay` hardcodes `10` in source. | Move the daily limit into configuration. |
| SampleBankingApp/Services/TransactionService.cs | 39 | `Transfer` hardcodes `Math.Round(..., 2)` currency precision. | Define a currency rounding policy constant. |
| SampleBankingApp/Services/TransactionService.cs | 50 | `Transfer` hardcodes transaction type `"Transfer"`. | Use an enum or transaction-type constants. |
| SampleBankingApp/Services/TransactionService.cs | 65 | `Deposit` hardcodes deposit cap `1000000`. | Move the cap into configuration. |
| SampleBankingApp/Services/TransactionService.cs | 68 | `Deposit` hardcodes bonus rate `0.05m` and multiplier `1`. | Move the bonus rate into configuration or remove it. |
| SampleBankingApp/Services/TransactionService.cs | 73 | `Deposit` hardcodes `FromUserId = 0` and type `"Deposit"`. | Use named constants or a dedicated system account id. |
| SampleBankingApp/Services/TransactionService.cs | 90 | `RecordTransaction` hardcodes status `'Completed'`. | Use a transaction status enum or constants. |
| SampleBankingApp/Services/TransactionService.cs | 96 | `FormatCurrency` hardcodes `"$"` and `"F2"` formatting. | Use configured culture and currency formatting. |
| SampleBankingApp/Services/UserService.cs | 22 | `GetUserById` hardcodes maximum user id `1000000`. | Move the range limit into configuration or remove it. |
| SampleBankingApp/Services/UserService.cs | 42 | `UpdateUser` repeats maximum user id `1000000`. | Extract a shared id validation helper. |
| SampleBankingApp/Services/UserService.cs | 56 | `DeleteUser` repeats maximum user id `1000000`. | Extract a shared id validation helper. |
| SampleBankingApp/Services/UserService.cs | 70 | `GetUsersPage` hardcodes maximum page size `50`. | Move the maximum page size into configuration. |
| SampleBankingApp/Services/UserService.cs | 99 | `SearchUsers` hardcodes table name `"Users"` and `LIKE '%{query}%'` pattern. | Use a repository method with a parameterized search query. |
| SampleBankingApp/appsettings.json | 3 | `TrustServerCertificate=True` is hardcoded in the production connection string. | Install a trusted certificate and remove the bypass. |
| SampleBankingApp/appsettings.json | 6 | `SecretKey`, `Issuer`, and `Audience` are environment-specific values committed in base settings. | Move secrets and environment values to production overrides or secret storage. |
| SampleBankingApp/appsettings.json | 11 | `SmtpHost`, `SmtpPort`, `Username`, and `Password` are environment-specific values committed in base settings. | Move to environment-specific configuration and secret storage. |
| SampleBankingApp/appsettings.json | 23 | `AllowedHosts` is hardcoded as `"*"`. | Configure explicit production host names. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `JoinWithSeparator` concatenates strings inside a loop, producing O(n²) allocations. | Replace the body with `string.Join(separator, items)`. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | `IsValidEmail` creates `new Regex(...)` on every call. | Use a `static readonly Regex` with `RegexOptions.Compiled`. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | `IsValidUsername` creates `new Regex(...)` on every call. | Use a `static readonly Regex` with `RegexOptions.Compiled`. |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Replace the body with `string.IsNullOrWhiteSpace(value)`. |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | `JoinWithSeparatorFixed` reimplements `string.Join` as a wrapper with no added behavior. | Remove the wrapper or add validation and documentation. |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | `MaskAccountNumber` and `ObfuscateAccount` duplicate account masking with inconsistent behavior. | Keep one implementation and delete the other. |
| SampleBankingApp/Services/UserService.cs | 10 | `_auditLog` is shared mutable static state accessed without synchronization. | Use a thread-safe collection, a lock, or a durable audit store. |
| SampleBankingApp/Services/UserService.cs | 11 | `_requestCount` is shared mutable static state incremented without synchronization. | Use `Interlocked.Increment` or remove the unused counter. |
| SampleBankingApp/Services/UserService.cs | 85 | `GetAuditReport` concatenates strings inside a loop, producing O(n²) allocations. | Use `StringBuilder` or `string.Join(Environment.NewLine, _auditLog)`. |
| SampleBankingApp/Services/UserService.cs | 18 | `GetUserById` repeats the `id <= 0` and `id > 1000000` validation block from `UpdateUser` and `DeleteUser`. | Extract `ValidateUserId(int id)` and call it from all three methods. |
| SampleBankingApp/Services/UserService.cs | 38 | `UpdateUser` repeats the `id <= 0` and `id > 1000000` validation block from `GetUserById` and `DeleteUser`. | Extract `ValidateUserId(int id)` and call it from all three methods. |
| SampleBankingApp/Services/UserService.cs | 52 | `DeleteUser` repeats the `id <= 0` and `id > 1000000` validation block from `GetUserById` and `UpdateUser`. | Extract `ValidateUserId(int id)` and call it from all three methods. |
| SampleBankingApp/Services/EmailService.cs | 34 | `SendTransferNotification` repeats sender address, message construction, and SMTP send logic found in `SendWelcomeEmail` and `SendWelcomeEmailHtml`. | Extract a private `SendMail` helper with validated arguments and disposal. |
| SampleBankingApp/Services/EmailService.cs | 63 | `SendWelcomeEmail` repeats sender address, message construction, and SMTP send logic found in `SendTransferNotification` and `SendWelcomeEmailHtml`. | Extract a private `SendMail` helper with validated arguments and disposal. |
| SampleBankingApp/Services/EmailService.cs | 86 | `SendWelcomeEmailHtml` repeats sender address, message construction, and SMTP send logic found in the other send methods. | Extract a private `SendMail` helper with validated arguments and disposal. |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | `GetOpenConnection` leaks resource ownership to callers with no documented disposal contract. | Replace with `ExecuteWithConnection` callbacks that own disposal. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | `ExecuteQuery` accepts raw SQL fragments and table names, encouraging injection-prone callers. | Replace with typed repository methods. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `ExecuteNonQuery` accepts raw SQL and encourages string-interpolated writes. | Replace with parameterized command helpers. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` bypasses `DatabaseHelper` and duplicates raw ADO.NET connection logic. | Use a repository method with parameterized SQL and shared connection management. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` carries password hashing, SQL construction, connection management, reader mapping, backdoor authentication, and user creation responsibilities. | Split into `HashPassword`, `FindActiveUserByCredentials`, `MapUser`, and `Authenticate` helpers. |
| SampleBankingApp/Services/AuthService.cs | 68 | `GenerateJwtToken` carries secret loading, key creation, claim construction, token creation, and serialization responsibilities. | Split into `GetSigningCredentials`, `BuildClaims`, and `WriteToken` helpers. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `Transfer` carries validation, user lookup, fee calculation, balance checks, two writes, ledger recording, and email notification responsibilities. | Split into `ValidateTransfer`, `LoadAccounts`, `CalculateDebit`, `CommitTransfer`, and `QueueNotification` helpers. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `Deposit` carries validation, bonus calculation, balance update, ledger recording, and success response responsibilities. | Split into `ValidateDeposit`, `CalculateCredit`, and `CommitDeposit` helpers. |
| SampleBankingApp/Services/TransactionService.cs | 87 | `RecordTransaction` builds SQL, formats nullable description, and executes a write in one method. | Split SQL construction and parameter binding from execution. |
| SampleBankingApp/Services/UserService.cs | 38 | `UpdateUser` carries id validation, audit logging, SQL construction, and execution responsibilities. | Split into `ValidateUserId`, `ValidateProfile`, `Audit`, and `ExecuteUpdate` helpers. |
| SampleBankingApp/Services/UserService.cs | 52 | `DeleteUser` carries id validation, request counting, SQL construction, execution, and audit logging responsibilities. | Split into `ValidateUserId`, `ExecuteDelete`, and `Audit` helpers. |
| SampleBankingApp/Services/UserService.cs | 68 | `GetUsersPage` carries pagination validation, offset calculation, SQL execution, and row mapping responsibilities. | Split into `NormalizePaging`, `FetchPage`, and `MapRows` helpers. |
| SampleBankingApp/Services/UserService.cs | 95 | `SearchUsers` carries query construction, execution, mapping, and broad exception swallowing responsibilities. | Split into `BuildSearchQuery`, `FetchRows`, and `MapRows` helpers. |
| SampleBankingApp/Services/EmailService.cs | 18 | `EmailService` constructor carries configuration loading, credential construction, SMTP client setup, and retry policy setup responsibilities. | Split into `LoadSmtpOptions`, `CreateCredentials`, and `CreateClient` helpers. |
| SampleBankingApp/Controllers/UserController.cs | 39 | `UpdateUser` carries model dereferencing, service invocation, validation exception mapping, and generic exception mapping responsibilities. | Move exception mapping to middleware and keep the action thin. |
| SampleBankingApp/Controllers/UserController.cs | 57 | `DeleteUser` carries service invocation, logging, and exception mapping responsibilities. | Move logging and exception mapping to middleware or a result filter. |
| SampleBankingApp/Controllers/TransactionController.cs | 24 | `Transfer` carries claim parsing, request dereferencing, service invocation, and response mapping responsibilities. | Extract claim parsing into a helper or policy-based binder. |
| SampleBankingApp/Controllers/TransactionController.cs | 38 | `Deposit` repeats claim parsing, request dereferencing, service invocation, and response mapping responsibilities. | Extract a shared `GetAuthenticatedUserId` helper. |
| SampleBankingApp/Program.cs | 7 | Top-level `Program.cs` carries service registration, JWT configuration, middleware pipeline, CORS, and host execution responsibilities. | Split into `AddApplicationServices`, `AddJwtAuthentication`, and `ConfigurePipeline` extension methods. |
| SampleBankingApp/Services/UserService.cs | 111 | `MapRowToUser` assumes every column is non-null and duplicates user mapping logic found in `AuthService.Login`. | Create one shared `UserMapper` used by both services. |
| SampleBankingApp/Services/AuthService.cs | 42 | `Login` duplicates user row mapping logic found in `UserService.MapRowToUser`. | Create one shared `UserMapper` used by both services. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally. | Wrap it in `if (app.Environment.IsDevelopment())` and add `UseExceptionHandler` otherwise. |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry validation. | Set it to `true` and configure a small `ClockSkew`. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out. | Uncomment `app.UseHttpsRedirection()` and add HSTS for production. |
| SampleBankingApp/Program.cs | 38 | CORS uses `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`. | Use a named policy with configured origins, methods, and headers. |
| SampleBankingApp/Program.cs | 16 | `Jwt:SecretKey` is loaded without startup validation. | Validate presence and minimum length before adding authentication. |
| SampleBankingApp/Program.cs | 26 | `Jwt:Issuer` is loaded without startup validation. | Validate presence and use strongly typed options binding. |
| SampleBankingApp/Program.cs | 27 | `Jwt:Audience` is loaded without startup validation. | Validate presence and use strongly typed options binding. |
| SampleBankingApp/Program.cs | 10 | `DatabaseHelper` is registered as a singleton while it stores only configuration, but its methods create undisposed connections. | Keep it stateless and fix disposal or register scoped with a connection factory. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `DebugSymbols` is enabled without a Release condition. | Condition it to Debug builds only. |
| SampleBankingApp/SampleBankingApp.csproj | 9 | `DebugType` is `full` without a Release condition. | Use `portable` for Debug and `none` or `embedded` for Release. |
| SampleBankingApp/SampleBankingApp.csproj | 7 | `TreatWarningsAsErrors` is `false`, allowing nullable and security warnings to be ignored. | Enable it after fixing warnings or at least enable nullable warnings as errors. |
| SampleBankingApp/SampleBankingApp.csproj | 13 | `Microsoft.AspNetCore.Authentication.JwtBearer` 8.0.0 may be behind the latest patched 8.x servicing release. | Upgrade to the latest patched 8.x version. |
| SampleBankingApp/SampleBankingApp.csproj | 14 | `System.Data.SqlClient` 4.8.6 is legacy compared with `Microsoft.Data.SqlClient`. | Migrate to the actively maintained `Microsoft.Data.SqlClient` package. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | `Newtonsoft.Json` 12.0.3 is outdated and unused in the provided source. | Remove it or upgrade to the latest 13.x patch. |
| SampleBankingApp/SampleBankingApp.csproj | 16 | `System.IdentityModel.Tokens.Jwt` 7.0.0 is mismatched with the .NET 8 JWT bearer stack. | Align package versions with the patched 8.x authentication packages. |
| SampleBankingApp/appsettings.json | 18 | `Default` log level is `Debug` in base configuration. | Set `Information` or `Warning` for production via override. |
| SampleBankingApp/appsettings.json | 19 | `Microsoft` log level is `Debug` in base configuration. | Set `Warning` for production via override. |
| SampleBankingApp/appsettings.json | 20 | `System` log level is `Debug` in base configuration. | Set `Warning` for production via override. |
| SampleBankingApp/appsettings.json | 3 | Production connection string is stored in base `appsettings.json`. | Move it to secure environment configuration and keep only placeholders locally. |
| SampleBankingApp/appsettings.json | 6 | JWT secret is stored in base `appsettings.json`. | Move it to a secret manager and add a non-secret placeholder only for development. |
| SampleBankingApp/appsettings.json | 14 | SMTP password is stored in base `appsettings.json`. | Move it to a secret manager and rotate the credential. |
| SampleBankingApp/appsettings.json | 23 | `AllowedHosts` is `*` in base configuration. | Set explicit hosts in the production override. |
| SampleBankingApp/appsettings.json | 1 | No `appsettings.Production.json` is present in the provided files. | Add production overrides for logging, hosts, CORS, JWT, and non-secret endpoints. |
| SampleBankingApp/appsettings.json | 1 | No `appsettings.Development.json` is present in the provided files. | Add development overrides that avoid production secrets. |
| SampleBankingApp/Services/EmailService.cs | 29 | `EnableSsl = false` is hardcoded rather than configured. | Bind `Email:EnableSsl` from configuration and require `true` in production. |
| SampleBankingApp/Services/EmailService.cs | 24 | SMTP port fallback `"25"` is hardcoded in source. | Require a validated `Email:SmtpPort` setting. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/SampleBankingApp.csproj | 1 | No test project or test package references are present in the provided source. | Add an xUnit or NUnit test project with a project reference to the app. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` lacks tests for valid credentials, wrong password, inactive user, SQL-injection username, null arguments, and admin bypass removal. | Add parameterized authentication tests with an in-memory or mocked repository. |
| SampleBankingApp/Services/AuthService.cs | 61 | `HashPasswordMd5` lacks tests proving it is replaced by a salted modern hash and that equal passwords produce different stored hashes. | Add password hashing tests after migrating to PBKDF2, bcrypt, scrypt, or Argon2id. |
| SampleBankingApp/Services/AuthService.cs | 68 | `GenerateJwtToken` lacks tests for claim contents, issuer, audience, expiry, and missing secret configuration. | Add JWT generation tests using strongly typed test configuration. |
| SampleBankingApp/Services/AuthService.cs | 98 | `ValidateToken` lacks tests for empty token, malformed token, expired token, wrong signature, wrong issuer, and wrong audience. | Add validation tests after implementing real token validation. |
| SampleBankingApp/Program.cs | 20 | JWT bearer configuration lacks integration tests for expired tokens and invalid signatures. | Add `WebApplicationFactory` tests with a test JWT setup. |
| SampleBankingApp/Controllers/AuthController.cs | 19 | `Login` lacks tests for 200 success, 401 failure, null request body, and rate-limit or lockout behavior. | Add controller integration tests with a mocked `AuthService`. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `Transfer` lacks boundary tests for zero amount, negative amount, self-transfer, missing source user, missing destination user, exact balance with fee, and balance one cent below amount plus fee. | Add table-driven transfer tests with a fake database helper. |
| SampleBankingApp/Services/TransactionService.cs | 39 | `Transfer` lacks tests for fee rounding at half-cent boundaries and sub-cent amount rejection. | Add decimal precision and rounding policy tests. |
| SampleBankingApp/Services/TransactionService.cs | 47 | `Transfer` lacks tests proving both balance updates and ledger insert commit or roll back together. | Add transactional integration tests against a test database. |
| SampleBankingApp/Services/TransactionService.cs | 52 | `Transfer` lacks tests proving email failure does not report transfer failure after commit. | Add outbox-based notification tests with a failing email sender. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `Deposit` lacks tests for zero, negative, exactly `1000000`, above `1000000`, sub-cent amounts, and bonus ledger consistency. | Add boundary and ledger reconciliation tests. |
| SampleBankingApp/Services/TransactionService.cs | 77 | `IsWithinDailyLimit` lacks tests for 9, 10, and 11 transactions and for deposits being counted. | Add daily-limit tests after wiring the method into transfer and deposit. |
| SampleBankingApp/Services/TransactionService.cs | 99 | `RefundTransaction` lacks tests for valid refund, duplicate refund, unauthorized refund, and missing transaction. | Add refund tests after implementing the method. |
| SampleBankingApp/Controllers/TransactionController.cs | 24 | `Transfer` lacks tests for missing `NameIdentifier`, non-numeric claim, null body, service failure, and service success. | Add controller tests with a mocked `TransactionService` and test principal. |
| SampleBankingApp/Controllers/TransactionController.cs | 38 | `Deposit` lacks tests for missing claim, null body, invalid amount, and successful deposit. | Add controller tests with a mocked `TransactionService`. |
| SampleBankingApp/Controllers/TransactionController.cs | 49 | `Refund` lacks tests for unauthenticated access, non-owner access, admin access, and unimplemented response. | Add authorization and endpoint behavior tests. |
| SampleBankingApp/Services/UserService.cs | 68 | `GetUsersPage` lacks tests for page 1 returning the first page, page 2 offset, zero page, negative page, zero page size, negative page size, and page size above 50. | Add pagination boundary tests with a fake query result. |
| SampleBankingApp/Services/UserService.cs | 18 | `GetUserById` lacks tests for id 0, id 1, id 1000000, id 1000001, missing row, and null database columns. | Add id-boundary and mapping tests. |
| SampleBankingApp/Services/UserService.cs | 38 | `UpdateUser` lacks tests for invalid id, null email, null username, invalid email, invalid username, SQL-injection payloads, and successful update. | Add validation and parameterized SQL tests. |
| SampleBankingApp/Services/UserService.cs | 52 | `DeleteUser` lacks tests for invalid id, missing user, existing transactions, and audit atomicity. | Add delete-policy and audit tests. |
| SampleBankingApp/Services/UserService.cs | 95 | `SearchUsers` lacks tests for null query, empty query, wildcard payloads, quote payloads, no matches, and database exceptions. | Add search validation and error-propagation tests. |
| SampleBankingApp/Services/UserService.cs | 85 | `GetAuditReport` lacks tests for empty log, one entry, many entries, and concurrent writes. | Add audit formatting and concurrency tests. |
| SampleBankingApp/Controllers/UserController.cs | 21 | `GetUser` lacks authorization tests proving users cannot read other users' password or balance fields. | Add integration tests for self, other user, admin, and anonymous access. |
| SampleBankingApp/Controllers/UserController.cs | 38 | `UpdateUser` lacks authorization tests proving users cannot update another user's profile. | Add integration tests for self, other user, admin, and anonymous access. |
| SampleBankingApp/Controllers/UserController.cs | 56 | `DeleteUser` lacks authorization tests proving non-admins cannot delete accounts. | Add integration tests for self, other user, admin, and anonymous access. |
| SampleBankingApp/Controllers/UserController.cs | 78 | `GetAuditLog` lacks authorization tests proving non-admins cannot read the audit report. | Add integration tests for admin and non-admin access. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | `ExecuteQuery` lacks tests proving table and where-clause inputs cannot inject SQL. | Replace with typed methods and add parameterization tests. |
| SampleBankingApp/Data/DatabaseHelper.cs | 36 | `ExecuteQuerySafe` lacks tests for null parameter values, missing parameters, and disposal on exceptions. | Add ADO.NET helper tests with a fake or test database. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `ExecuteNonQuery` lacks tests proving connections and commands are disposed when execution throws. | Add resource-disposal tests with a failing command. |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | `IsValidEmail` lacks tests for null, empty, whitespace, 254 characters, 255 characters, and malformed addresses. | Add table-driven validation tests. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | `IsValidUsername` lacks tests for null, 2 characters, 3 characters, 20 characters, 21 characters, and invalid symbols. | Add table-driven validation tests. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `JoinWithSeparator` lacks tests for empty input, one item, many items, and trailing separator behavior. | Add tests or remove the method in favor of `string.Join`. |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | `ObfuscateAccount` lacks tests for null, empty, 3 characters, 4 characters, and long account numbers. | Add boundary tests or consolidate with `MaskAccountNumber`. |
| SampleBankingApp/Services/EmailService.cs | 34 | `SendTransferNotification` lacks tests for retry count, final failure, message disposal, and body contents. | Add tests with a fake SMTP client abstraction. |
| SampleBankingApp/Services/EmailService.cs | 63 | `SendWelcomeEmail` lacks tests for null username, swallowed exceptions, and sender address configuration. | Add tests with a fake SMTP client and logger. |
| SampleBankingApp/Services/EmailService.cs | 86 | `SendWelcomeEmailHtml` lacks tests for HTML body, null username, and send failures. | Add tests with a fake SMTP client abstraction. |
| SampleBankingApp/Program.cs | 38 | CORS and HTTPS middleware lack integration tests for disallowed origins and HTTP-to-HTTPS redirection. | Add `WebApplicationFactory` pipeline tests. |
| SampleBankingApp/appsettings.json | 1 | Configuration lacks startup tests proving missing secrets, weak secrets, and missing production overrides fail fast. | Add configuration validation tests for each environment. |

All 10 review sections are complete. The highest-priority remediation items are removing committed secrets and the admin backdoor, parameterizing every SQL statement, enforcing authorization on user and refund endpoints, enabling JWT lifetime validation, and making financial writes transactional.