## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/AuthController.cs | 20 | `Login` accepts a model-bound `LoginRequest` without checking `request` for null before dereferencing it. | Add a null guard or rely on `[ApiController]` plus explicit `if (request is null) return BadRequest();`. |
| SampleBankingApp/Controllers/AuthController.cs | 22 | `Login` has no rate limiting or account lockout on the authentication endpoint. | Add ASP.NET Core rate limiting and progressive lockout/failed-attempt tracking. |
| SampleBankingApp/Controllers/TransactionController.cs | 24 | `Transfer` accepts a model-bound `TransferRequest` without checking `request` for null before dereferencing it. | Add a null guard or explicit `if (request is null) return BadRequest();`. |
| SampleBankingApp/Controllers/TransactionController.cs | 38 | `Deposit` accepts a model-bound `DepositRequest` without checking `request` for null before dereferencing it. | Add a null guard or explicit `if (request is null) return BadRequest();`. |
| SampleBankingApp/Controllers/TransactionController.cs | 49 | `Refund` is protected only by `[Authorize]` and has no role/ownership check before refunding an arbitrary `transactionId`. | Add an admin/role policy and verify the caller owns or is authorized for the transaction. |
| SampleBankingApp/Controllers/UserController.cs | 22 | `GetUser` allows any authenticated user to read any user record by id, including balance, email, and role. | Enforce self-access or an admin policy with an ownership check. |
| SampleBankingApp/Controllers/UserController.cs | 32 | `GetUsers` allows any authenticated user to enumerate all users. | Restrict with an admin/auditor authorization policy. |
| SampleBankingApp/Controllers/UserController.cs | 39 | `UpdateUser` has no ownership check, so any authenticated user can update any other user by id. | Compare the route id to the JWT `NameIdentifier` claim or require an admin policy. |
| SampleBankingApp/Controllers/UserController.cs | 57 | `DeleteUser` has no ownership check, so any authenticated user can delete any other user by id. | Compare the route id to the JWT `NameIdentifier` claim or require an admin policy. |
| SampleBankingApp/Controllers/UserController.cs | 72 | `SearchUsers` allows any authenticated user to search all users. | Restrict with an appropriate authorization policy and return a safe DTO. |
| SampleBankingApp/Controllers/UserController.cs | 79 | `GetAuditLog` allows any authenticated user to read the in-memory audit log. | Restrict with an admin/auditor authorization policy. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | `DatabaseHelper` contains a hardcoded fallback SQL Server `sa` password `Admin1234!`. | Remove the fallback credential and fail startup when the connection string is missing. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | `ExecuteQuery` accepts raw `tableName` and `whereClause` fragments and interpolates them into `SELECT * FROM {tableName} WHERE {whereClause}`. | Replace with a typed repository method that uses a fixed table name and parameterized predicates. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `ExecuteNonQuery` accepts arbitrary raw SQL and executes it without parameters. | Replace with parameterized command helpers for each specific write operation. |
| SampleBankingApp/Data/DatabaseHelper.cs | 68 | `ExecuteQueryWithParams` accepts arbitrary raw SQL and is still present despite being obsolete. | Delete the obsolete method and expose only constrained parameterized helpers. |
| SampleBankingApp/Program.cs | 24 | JWT validation sets `ValidateLifetime = false`, so expired tokens are accepted. | Set `ValidateLifetime = true` and configure `ClockSkew` explicitly. |
| SampleBankingApp/Program.cs | 28 | `Encoding.UTF8.GetBytes(jwtSecret!)` uses a null-forgiving secret that can be null and is currently only `mysecretkey`. | Validate a strong secret at startup and load it from a secure secret store. |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally and can expose stack traces in production. | Call it only when `app.Environment.IsDevelopment()` and use `UseExceptionHandler` otherwise. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out. | Enable `app.UseHttpsRedirection()` and enforce HTTPS/HSTS. |
| SampleBankingApp/Program.cs | 38 | CORS uses `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` for a banking API. | Define a named policy with an explicit allowed origin list, methods, and headers. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `DebugSymbols` is `true` for all builds. | Set debug symbols only for Debug or use a portable symbol setting controlled by CI. |
| SampleBankingApp/SampleBankingApp.csproj | 9 | `DebugType` is `full` for all builds. | Use `DebugType=portable` in Debug and disable full debug output in Release. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | `Newtonsoft.Json` `12.0.3` is outdated and has known vulnerability history. | Upgrade to a current patched version or remove it if unused. |
| SampleBankingApp/SampleBankingApp.csproj | 16 | `System.IdentityModel.Tokens.Jwt` `7.0.0` is older than the ASP.NET Core 8 JWT bearer stack. | Align to a current patched 8.x-compatible version or remove the direct reference. |
| SampleBankingApp/Services/AuthService.cs | 17 | `AdminBypassPassword` is a hardcoded backdoor credential. | Remove the bypass and use normal seeded admin accounts with hashed passwords and MFA. |
| SampleBankingApp/Services/AuthService.cs | 30 | `Login` hashes passwords with unsalted MD5 via `HashPasswordMd5`. | Use a slow password KDF such as PBKDF2, bcrypt, scrypt, or Argon2id with per-user salts. |
| SampleBankingApp/Services/AuthService.cs | 32 | `Login` interpolates `username` and `hashedPassword` directly into the SQL `WHERE` clause. | Use `SqlParameter` values for username and password hash. |
| SampleBankingApp/Services/AuthService.cs | 53 | `Login` grants a `SuperAdmin` user when `admin` plus `AdminBypassPassword` is supplied. | Delete the hardcoded bypass branch entirely. |
| SampleBankingApp/Services/AuthService.cs | 70 | `GenerateJwtToken` reads `Jwt:SecretKey` with `!` and uses the weak configured value. | Validate a high-entropy secret at startup and obtain it from a secret manager. |
| SampleBankingApp/Services/AuthService.cs | 84 | `GenerateJwtToken` issues tokens valid for 30 days. | Reduce token lifetime and use refresh tokens with rotation. |
| SampleBankingApp/Services/AuthService.cs | 91 | `HashPasswordSha1` implements unsalted SHA-1 password hashing. | Remove it and migrate to a modern password hashing scheme. |
| SampleBankingApp/Services/AuthService.cs | 98 | `ValidateToken` returns `true` for any non-empty token without verifying signature, issuer, audience, or lifetime. | Use `JwtSecurityTokenHandler.ValidateToken` with the same `TokenValidationParameters` as startup. |
| SampleBankingApp/Services/EmailService.cs | 29 | `EmailService` sets `EnableSsl = false` while sending authenticated SMTP credentials. | Enable TLS/SSL and use a secure SMTP port. |
| SampleBankingApp/Services/EmailService.cs | 40 | `SendTransferNotification` hardcodes `notifications@company.com` as the sender. | Move the sender address into configuration. |
| SampleBankingApp/Services/EmailService.cs | 69 | `SendWelcomeEmail` hardcodes `notifications@company.com` as the sender. | Move the sender address into configuration. |
| SampleBankingApp/Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` hardcodes `notifications@company.com` as the sender. | Move the sender address into configuration. |
| SampleBankingApp/Services/TransactionService.cs | 47 | `Transfer` interpolates `newFromBalance` and `fromUserId` into an `UPDATE` statement. | Use parameterized SQL and perform the debit inside a transaction. |
| SampleBankingApp/Services/TransactionService.cs | 48 | `Transfer` interpolates `newToBalance` and `toUserId` into an `UPDATE` statement. | Use parameterized SQL and perform the credit inside a transaction. |
| SampleBankingApp/Services/TransactionService.cs | 71 | `Deposit` interpolates `amount + interestBonus` and `userId` into an `UPDATE` statement. | Use parameterized SQL and validate the user exists. |
| SampleBankingApp/Services/TransactionService.cs | 90 | `RecordTransaction` interpolates `type` and `description` into an `INSERT` statement, enabling SQL injection through `description`. | Use `SqlParameter` values for every column value. |
| SampleBankingApp/Services/UserService.cs | 47 | `UpdateUser` interpolates `email`, `username`, and `id` into an `UPDATE` statement. | Use parameterized SQL and validate email/username format. |
| SampleBankingApp/Services/UserService.cs | 61 | `DeleteUser` interpolates `id` into a `DELETE` statement. | Use parameterized SQL and consider soft deletion with authorization. |
| SampleBankingApp/Services/UserService.cs | 99 | `SearchUsers` interpolates `query` into `Username LIKE '%{query}%'` through `ExecuteQuery`. | Use a parameterized `LIKE @Query` query with escaped wildcard characters. |
| SampleBankingApp/appsettings.json | 3 | Production connection string commits the SQL Server `sa` password `Admin1234!`. | Remove the secret from source control and use managed identity or a secret store. |
| SampleBankingApp/appsettings.json | 6 | JWT `SecretKey` is the weak committed value `mysecretkey`. | Replace with a high-entropy secret stored outside source control. |
| SampleBankingApp/appsettings.json | 14 | SMTP password `EmailPass99` is committed to source control. | Remove it and load it from a secret store or managed identity. |
| SampleBankingApp/appsettings.json | 23 | `AllowedHosts` is `"*"` for all environments. | Restrict allowed hosts per environment. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/TransactionController.cs | 27 | `Transfer` parses `userIdClaim` with `int.Parse` even though the claim may be missing or non-numeric. | Use `int.TryParse` and return `Unauthorized` or `BadRequest` on failure. |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | `Deposit` parses `userIdClaim` with `int.Parse` even though the claim may be missing or non-numeric. | Use `int.TryParse` and return `Unauthorized` or `BadRequest` on failure. |
| SampleBankingApp/Controllers/UserController.cs | 32 | `GetUsers` accepts `page = 0` or negative values without validation. | Validate `page >= 1` and `pageSize >= 1` before calling the service. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `JoinWithSeparator` appends the separator after the final item, unlike `string.Join`. | Use `string.Join(separator, items)` or trim the trailing separator. |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | `ObfuscateAccount` uses `account[^4..]` and throws for strings shorter than four characters. | Guard the length and return a safe masked value for short inputs. |
| SampleBankingApp/Services/AuthService.cs | 98 | `ValidateToken` always returns `true` for any non-empty token, making validation meaningless. | Perform full signature, issuer, audience, and lifetime validation. |
| SampleBankingApp/Services/TransactionService.cs | 25 | `Transfer` rejects `amount < 0` but allows `amount == 0`, producing a zero-value transfer and transaction record. | Require `amount > 0`. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `Transfer` does not reject `fromUserId == toUserId`, allowing a self-transfer that debits only the fee and credits the amount. | Return a validation error when source and destination ids match. |
| SampleBankingApp/Services/TransactionService.cs | 42 | `Transfer` checks `fromBalance >= amount` but debits `amount + fee`, which can create a negative balance. | Check `fromBalance >= totalDebit` before applying the debit. |
| SampleBankingApp/Services/TransactionService.cs | 44 | `Transfer` computes `newFromBalance` from a stale read instead of an atomic conditional update. | Use a transaction with locking or `UPDATE ... WHERE Balance >= @TotalDebit`. |
| SampleBankingApp/Services/TransactionService.cs | 45 | `Transfer` computes `newToBalance` from a stale read and can overwrite concurrent credits. | Use an atomic `UPDATE Users SET Balance = Balance + @Amount`. |
| SampleBankingApp/Services/TransactionService.cs | 50 | `Transfer` records the transaction after balance updates without checking that both updates affected one row. | Verify affected row counts and roll back if either update fails. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `Deposit` credits `amount + interestBonus` but records only `amount` in `Transactions`. | Record both the deposit amount and bonus separately or remove the bonus. |
| SampleBankingApp/Services/TransactionService.cs | 68 | `Deposit` applies a hardcoded `0.05m * 1` interest bonus, effectively a 5% instant bonus on every deposit. | Remove the bonus or move an explicitly approved rate and accrual rule into configuration. |
| SampleBankingApp/Services/TransactionService.cs | 71 | `Deposit` updates `Users` without verifying that `userId` exists. | Check the affected row count and fail when no user was updated. |
| SampleBankingApp/Services/TransactionService.cs | 77 | `IsWithinDailyLimit` is never called by `Transfer` or `Deposit`, so `MaxTransactionsPerDay` is not enforced. | Call the limit check before processing a transfer and include the check in the transaction. |
| SampleBankingApp/Services/TransactionService.cs | 90 | `RecordTransaction` inserts a null `description` as the SQL literal `'{description}'`, producing an empty string or invalid SQL semantics. | Use `DBNull.Value` through a parameter when the description is null. |
| SampleBankingApp/Services/UserService.cs | 68 | `GetUsersPage` computes `skip = page * pageSize`, so page 1 skips the first page of results. | Use `(page - 1) * pageSize` after validating `page >= 1`. |
| SampleBankingApp/Services/UserService.cs | 70 | `GetUsersPage` caps only the upper bound of `pageSize` and allows zero or negative values. | Clamp or reject `pageSize <= 0` and validate `page >= 1`. |
| SampleBankingApp/Services/UserService.cs | 95 | `SearchUsers` returns an empty list on any exception, so callers cannot distinguish no matches from a database failure. | Let the exception propagate or return a result type containing an error state. |
| SampleBankingApp/Services/UserService.cs | 111 | `MapRowToUser` omits `Password`, `LastLoginAt`, and other fields from `SELECT *` results. | Map all required fields explicitly or project a safe DTO instead of `SELECT *`. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/TransactionController.cs | 56 | `Refund` catches `NotImplementedException` and returns a 500 for a known unimplemented feature. | Return `501 Not Implemented` or remove the endpoint until implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | `UpdateUser` returns raw `ex.Message` from `ArgumentException` to the HTTP client. | Return a stable validation problem response and log the exception. |
| SampleBankingApp/Controllers/UserController.cs | 50 | `UpdateUser` catches broad `Exception` and returns raw `ex.Message` with status 500. | Catch only expected exceptions, log unexpected ones, and return a generic error. |
| SampleBankingApp/Controllers/UserController.cs | 64 | `DeleteUser` catches broad `Exception` and converts all failures to a generic 500. | Catch specific data/validation exceptions and let unexpected failures reach centralized exception handling. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `ExecuteNonQuery` closes the connection only on the success path because `Close()` is after `ExecuteNonQuery()`. | Wrap connection and command in `using` blocks so all exception paths dispose them. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` opens a reader and returns from inside `if (reader.Read())` without closing the command, reader, or connection. | Use `using` blocks for connection, command, and reader. |
| SampleBankingApp/Services/EmailService.cs | 75 | `SendWelcomeEmail` catches broad `Exception` and silently writes to `Console`, swallowing delivery failures. | Log through `ILogger` and return or throw a typed delivery result. |
| SampleBankingApp/Services/TransactionService.cs | 47 | `Transfer` performs two balance writes and a transaction insert without a database transaction. | Execute all three writes in one `SqlTransaction` with rollback on failure. |
| SampleBankingApp/Services/TransactionService.cs | 52 | `Transfer` sends email after the balance writes have committed, so an SMTP failure returns an error even though money moved. | Use an outbox pattern or send the notification asynchronously after commit with retry. |
| SampleBankingApp/Services/TransactionService.cs | 71 | `Deposit` performs a balance update and `RecordTransaction` without a database transaction. | Wrap both writes in one transaction and roll back if either fails. |
| SampleBankingApp/Services/UserService.cs | 105 | `SearchUsers` catches broad `Exception` and returns an empty collection, hiding errors from callers. | Remove the catch or return an explicit failure result. |
| SampleBankingApp/Controllers/AuthController.cs | 19 | `Login` has no rate limiting or account lockout handling for repeated failed authentication. | Add rate limiting and lockout responses such as 429 or 423. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | `GetOpenConnection` returns an opened `SqlConnection` whose ownership is transferred to callers with no documented disposal contract. | Avoid returning open connections or return a disposable wrapper with a documented ownership contract. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | `ExecuteQuery` obtains `connection` from `GetOpenConnection()` and never disposes it. | Use `using var connection = new SqlConnection(...)` inside the method. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | `ExecuteQuery` creates `SqlCommand` without disposing it. | Use `using var command = ...`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 30 | `ExecuteQuery` creates `SqlDataAdapter` without disposing it. | Use `using var adapter = ...`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 44 | `ExecuteQuerySafe` creates `SqlDataAdapter` without disposing it. | Use `using var adapter = ...`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | `ExecuteNonQuery` obtains `connection` from `GetOpenConnection()` and skips `Close()` when `ExecuteNonQuery()` throws. | Use `using` for the connection and command. |
| SampleBankingApp/Data/DatabaseHelper.cs | 53 | `ExecuteNonQuery` creates `SqlCommand` without disposing it. | Use `using var command = ...`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 63 | `TableExists` assigns the `DataTable` returned by `GetSchema` without disposing it. | Use `using var result = connection.GetSchema(...)`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 74 | `ExecuteQueryWithParams` creates `SqlDataAdapter` without disposing it. | Use `using var adapter = ...` or delete the obsolete method. |
| SampleBankingApp/Services/AuthService.cs | 34 | `Login` creates `SqlConnection` without a `using` block. | Use `using var connection = ...`. |
| SampleBankingApp/Services/AuthService.cs | 37 | `Login` creates `SqlCommand` without a `using` block. | Use `using var command = ...`. |
| SampleBankingApp/Services/AuthService.cs | 38 | `Login` creates `SqlDataReader` without a `using` block. | Use `using var reader = command.ExecuteReader()`. |
| SampleBankingApp/Services/EmailService.cs | 16 | `EmailService` holds `SmtpClient` as an instance field, which is not thread-safe and keeps sockets alive. | Create and dispose `SmtpClient` per send or use a thread-safe mail abstraction. |
| SampleBankingApp/Services/EmailService.cs | 39 | `SendTransferNotification` creates `MailMessage` without disposing it. | Use `using var message = new MailMessage(...)`. |
| SampleBankingApp/Services/EmailService.cs | 69 | `SendWelcomeEmail` creates `MailMessage` without disposing it. | Use `using var message = new MailMessage(...)`. |
| SampleBankingApp/Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` creates `MailMessage` without disposing it. | Use `using var message = new MailMessage(...)`. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/AuthController.cs | 22 | `Login` dereferences `request.Username` and `request.Password` without checking `request` for null. | Add `if (request is null) return BadRequest();`. |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | `Transfer` passes `userIdClaim!` to `int.Parse`, which throws if the claim is missing. | Use `int.TryParse(userIdClaim, out var fromUserId)` and handle failure. |
| SampleBankingApp/Controllers/TransactionController.cs | 29 | `Transfer` dereferences `request.ToUserId`, `request.Amount`, and `request.Description` without checking `request` for null. | Add `if (request is null) return BadRequest();`. |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | `Deposit` passes `userIdClaim!` to `int.Parse`, which throws if the claim is missing. | Use `int.TryParse(userIdClaim, out var userId)` and handle failure. |
| SampleBankingApp/Controllers/TransactionController.cs | 43 | `Deposit` dereferences `request.Amount` without checking `request` for null. | Add `if (request is null) return BadRequest();`. |
| SampleBankingApp/Controllers/UserController.cs | 43 | `UpdateUser` dereferences `request.Email` and `request.Username` without checking `request` for null. | Add `if (request is null) return BadRequest();`. |
| SampleBankingApp/Controllers/UserController.cs | 72 | `SearchUsers` passes `query` to `SearchUsers` without a null guard. | Validate `query` with `string.IsNullOrWhiteSpace` before calling the service. |
| SampleBankingApp/Data/DatabaseHelper.cs | 15 | `DatabaseHelper` falls back to a hardcoded connection string when `GetConnectionString("DefaultConnection")` returns null. | Throw `InvalidOperationException` when configuration is missing. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `IsValidEmail` calls `email.Length` before checking for null. | Return false when `email is null` or use `string.IsNullOrWhiteSpace`. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `IsValidUsername` calls `username.Length` before checking for null. | Return false when `username is null`. |
| SampleBankingApp/Helpers/StringHelper.cs | 32 | `JoinWithSeparator` enumerates `items` without checking for null. | Throw `ArgumentNullException` or return an empty string after an explicit null check. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `MaskAccountNumber` calls `accountNumber.Length` before checking for null. | Return a safe value or throw `ArgumentNullException` after an explicit null check. |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | `ObfuscateAccount` uses `account[^4..]` without checking for null or length. | Add null and length guards before slicing. |
| SampleBankingApp/Program.cs | 28 | `Encoding.UTF8.GetBytes(jwtSecret!)` can receive null when `Jwt:SecretKey` is missing. | Validate `jwtSecret` is non-empty and sufficiently long before calling `GetBytes`. |
| SampleBankingApp/Services/AuthService.cs | 34 | `Login` passes `_config.GetConnectionString("DefaultConnection")` directly to `SqlConnection`, which can be null. | Validate the connection string before constructing `SqlConnection`. |
| SampleBankingApp/Services/AuthService.cs | 70 | `GenerateJwtToken` passes `_config["Jwt:SecretKey"]!` to `Encoding.UTF8.GetBytes`. | Validate the secret before use and fail fast at startup. |
| SampleBankingApp/Services/EmailService.cs | 22 | `EmailService` passes `_config["Email:SmtpHost"]` directly to `SmtpClient`. | Validate `SmtpHost` is non-empty before constructing the client. |
| SampleBankingApp/Services/EmailService.cs | 26 | `EmailService` passes `_config["Email:Username"]` and `_config["Email:Password"]` to `NetworkCredential`. | Validate both values or use default credentials/managed identity. |
| SampleBankingApp/Services/EmailService.cs | 65 | `SendWelcomeEmail` calls `username.ToUpper()` without checking for null. | Validate `username` before formatting the body. |
| SampleBankingApp/Services/EmailService.cs | 83 | `BuildHtmlTemplate` interpolates `title` and `body` without null checks. | Validate inputs or use null-coalescing defaults. |
| SampleBankingApp/Services/TransactionService.cs | 36 | `Transfer` accesses `fromUserTable.Rows[0]` without checking `Rows.Count > 0`. | Return a not-found error when the source user does not exist. |
| SampleBankingApp/Services/TransactionService.cs | 37 | `Transfer` accesses `toUserTable.Rows[0]` without checking `Rows.Count > 0`. | Return a not-found error when the destination user does not exist. |
| SampleBankingApp/Services/TransactionService.cs | 53 | `Transfer` casts `fromUserTable.Rows[0]["Email"]` to `string` without checking for `DBNull`. | Use a safe column reader that handles `DBNull.Value`. |
| SampleBankingApp/Services/TransactionService.cs | 55 | `Transfer` casts `toUserTable.Rows[0]["Username"]` to `string` without checking for `DBNull`. | Use a safe column reader that handles `DBNull.Value`. |
| SampleBankingApp/Services/TransactionService.cs | 83 | `IsWithinDailyLimit` accesses `table.Rows[0]["TxCount"]` without checking `Rows.Count > 0`. | Check `Rows.Count` and handle `DBNull` before casting. |
| SampleBankingApp/Services/UserService.cs | 95 | `SearchUsers` passes a potentially null `query` into string interpolation. | Validate `query` before building the predicate. |
| SampleBankingApp/Services/UserService.cs | 115 | `MapRowToUser` casts `row["Id"]` without checking for `DBNull`. | Use a typed null-safe column accessor. |
| SampleBankingApp/Services/UserService.cs | 116 | `MapRowToUser` casts `row["Username"]` without checking for `DBNull`. | Use a typed null-safe column accessor. |
| SampleBankingApp/Services/UserService.cs | 117 | `MapRowToUser` casts `row["Email"]` without checking for `DBNull`. | Use a typed null-safe column accessor. |
| SampleBankingApp/Services/UserService.cs | 118 | `MapRowToUser` casts `row["Role"]` without checking for `DBNull`. | Use a typed null-safe column accessor. |
| SampleBankingApp/Services/UserService.cs | 119 | `MapRowToUser` casts `row["Balance"]` without checking for `DBNull`. | Use a typed null-safe column accessor. |
| SampleBankingApp/Services/UserService.cs | 120 | `MapRowToUser` casts `row["IsActive"]` without checking for `DBNull`. | Use a typed null-safe column accessor. |
| SampleBankingApp/Services/UserService.cs | 121 | `MapRowToUser` casts `row["CreatedAt"]` without checking for `DBNull`. | Use a typed null-safe column accessor. |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/AuthController.cs | 13 | `AuthController.AuthController` is a constructor and has no explicit caller in the provided source because framework activation is external. | Keep it because ASP.NET Core DI invokes it. |
| SampleBankingApp/Controllers/AuthController.cs | 20 | `AuthController.Login` has no explicit caller in the provided source because routing invokes it externally. | Keep it because ASP.NET Core routing invokes it. |
| SampleBankingApp/Controllers/TransactionController.cs | 17 | `TransactionController.TransactionController` is a constructor and has no explicit caller in the provided source because framework activation is external. | Keep it because ASP.NET Core DI invokes it. |
| SampleBankingApp/Controllers/TransactionController.cs | 24 | `TransactionController.Transfer` has no explicit caller in the provided source because routing invokes it externally. | Keep it because ASP.NET Core routing invokes it. |
| SampleBankingApp/Controllers/TransactionController.cs | 38 | `TransactionController.Deposit` has no explicit caller in the provided source because routing invokes it externally. | Keep it because ASP.NET Core routing invokes it. |
| SampleBankingApp/Controllers/TransactionController.cs | 49 | `TransactionController.Refund` has no explicit caller in the provided source because routing invokes it externally. | Keep it because ASP.NET Core routing invokes it. |
| SampleBankingApp/Controllers/UserController.cs | 15 | `UserController.UserController` is a constructor and has no explicit caller in the provided source because framework activation is external. | Keep it because ASP.NET Core DI invokes it. |
| SampleBankingApp/Controllers/UserController.cs | 22 | `UserController.GetUser` has no explicit caller in the provided source because routing invokes it externally. | Keep it because ASP.NET Core routing invokes it. |
| SampleBankingApp/Controllers/UserController.cs | 32 | `UserController.GetUsers` has no explicit caller in the provided source because routing invokes it externally. | Keep it because ASP.NET Core routing invokes it. |
| SampleBankingApp/Controllers/UserController.cs | 39 | `UserController.UpdateUser` has no explicit caller in the provided source because routing invokes it externally. | Keep it because ASP.NET Core routing invokes it. |
| SampleBankingApp/Controllers/UserController.cs | 57 | `UserController.DeleteUser` has no explicit caller in the provided source because routing invokes it externally. | Keep it because ASP.NET Core routing invokes it. |
| SampleBankingApp/Controllers/UserController.cs | 72 | `UserController.SearchUsers` has no explicit caller in the provided source because routing invokes it externally. | Keep it because ASP.NET Core routing invokes it. |
| SampleBankingApp/Controllers/UserController.cs | 79 | `UserController.GetAuditLog` has no explicit caller in the provided source because routing invokes it externally. | Keep it because ASP.NET Core routing invokes it. |
| SampleBankingApp/Data/DatabaseHelper.cs | 13 | `DatabaseHelper.DatabaseHelper` is called by DI registration in `Program.cs` line 10. | Keep it. |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | `DatabaseHelper.GetOpenConnection` is called by `ExecuteQuery` line 28 and `ExecuteNonQuery` line 52. | Keep it but replace with internally scoped disposal. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | `DatabaseHelper.ExecuteQuery` is called by `UserService.SearchUsers` line 99. | Keep it but replace with a safe parameterized search method. |
| SampleBankingApp/Data/DatabaseHelper.cs | 36 | `DatabaseHelper.ExecuteQuerySafe` is called by `UserService.GetUserById`, `UserService.GetUsersPage`, `TransactionService.Transfer`, and `TransactionService.IsWithinDailyLimit`. | Keep it. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `DatabaseHelper.ExecuteNonQuery` is called by `TransactionService.Transfer`, `TransactionService.Deposit`, `TransactionService.RecordTransaction`, `UserService.UpdateUser`, and `UserService.DeleteUser`. | Keep it but parameterize callers. |
| SampleBankingApp/Data/DatabaseHelper.cs | 59 | `DatabaseHelper.TableExists` appears only at its own definition and has no caller in the provided source. | Remove it or add a startup schema-check caller. |
| SampleBankingApp/Data/DatabaseHelper.cs | 68 | `DatabaseHelper.ExecuteQueryWithParams` is marked `[Obsolete]` and appears only at its own definition. | Delete the obsolete unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | `StringHelper.IsValidEmail` appears only at its own definition and has no caller in the provided source. | Remove it or call it from `UpdateUser` validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | `StringHelper.IsValidUsername` appears only at its own definition and has no caller in the provided source. | Remove it or call it from `UpdateUser` validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `StringHelper.JoinWithSeparator` appears only at its own definition and has no caller in the provided source. | Delete the broken implementation. |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | `StringHelper.JoinWithSeparatorFixed` appears only at its own definition and has no caller in the provided source. | Delete it or use it to replace `JoinWithSeparator`. |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | `StringHelper.MaskAccountNumber` appears only at its own definition and has no caller in the provided source. | Remove it or use it when returning account data. |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | `StringHelper.ObfuscateAccount` appears only at its own definition and has no caller in the provided source. | Remove it or consolidate with `MaskAccountNumber`. |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | `StringHelper.ToTitleCase` appears only at its own definition and has no caller in the provided source. | Remove it or use it in a named formatting path. |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | `StringHelper.IsBlank` appears only at its own definition and has no caller in the provided source. | Delete it and use `string.IsNullOrWhiteSpace`. |
| SampleBankingApp/Services/AuthService.cs | 19 | `AuthService.AuthService` is called by DI registration in `Program.cs` line 12. | Keep it. |
| SampleBankingApp/Services/AuthService.cs | 28 | `AuthService.Login` is called by `AuthController.Login` line 22. | Keep it. |
| SampleBankingApp/Services/AuthService.cs | 61 | `AuthService.HashPasswordMd5` is called by `AuthService.Login` line 30. | Replace it with a secure password verifier. |
| SampleBankingApp/Services/AuthService.cs | 68 | `AuthService.GenerateJwtToken` is called by `AuthController.Login` line 29. | Keep it. |
| SampleBankingApp/Services/AuthService.cs | 91 | `AuthService.HashPasswordSha1` appears only at its own definition and has no caller in the provided source. | Delete the unused weak hash method. |
| SampleBankingApp/Services/AuthService.cs | 98 | `AuthService.ValidateToken` appears only at its own definition and has no caller in the provided source. | Remove it or implement and use it in a real validation path. |
| SampleBankingApp/Services/AuthService.cs | 103 | `AuthService.ValidateToken` has unreachable code after an unconditional `return true` on line 103. | Remove the unreachable handler code or remove the early return. |
| SampleBankingApp/Services/EmailService.cs | 18 | `EmailService.EmailService` is called by DI registration in `Program.cs` line 14. | Keep it. |
| SampleBankingApp/Services/EmailService.cs | 34 | `EmailService.SendTransferNotification` is called by `TransactionService.Transfer` line 52. | Keep it. |
| SampleBankingApp/Services/EmailService.cs | 63 | `EmailService.SendWelcomeEmail` appears only at its own definition and has no caller in the provided source. | Remove it or call it from a registration workflow. |
| SampleBankingApp/Services/EmailService.cs | 81 | `EmailService.BuildHtmlTemplate` is called by `SendWelcomeEmailHtml` line 88. | Keep it if the HTML email path is retained. |
| SampleBankingApp/Services/EmailService.cs | 86 | `EmailService.SendWelcomeEmailHtml` appears only at its own definition and has no caller in the provided source. | Remove it or call it from a registration workflow. |
| SampleBankingApp/Services/TransactionService.cs | 14 | `TransactionService.TransactionService` is called by DI registration in `Program.cs` line 13. | Keep it. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `TransactionService.Transfer` is called by `TransactionController.Transfer` line 29. | Keep it. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `TransactionService.Deposit` is called by `TransactionController.Deposit` line 43. | Keep it. |
| SampleBankingApp/Services/TransactionService.cs | 77 | `TransactionService.IsWithinDailyLimit` appears only at its own definition and has no caller in the provided source. | Call it from `Transfer` and `Deposit` or remove the constant and method. |
| SampleBankingApp/Services/TransactionService.cs | 87 | `TransactionService.RecordTransaction` is called by `Transfer` line 50 and `Deposit` line 73. | Keep it. |
| SampleBankingApp/Services/TransactionService.cs | 94 | `TransactionService.FormatCurrency` appears only at its own definition and has no caller in the provided source. | Remove it or use it in notification formatting. |
| SampleBankingApp/Services/TransactionService.cs | 99 | `TransactionService.RefundTransaction` is called by `TransactionController.Refund` line 53 but contains `throw new NotImplementedException()` in non-stub production code. | Implement the refund workflow or remove the endpoint and method. |
| SampleBankingApp/Services/UserService.cs | 13 | `UserService.UserService` is called by DI registration in `Program.cs` line 11. | Keep it. |
| SampleBankingApp/Services/UserService.cs | 18 | `UserService.GetUserById` is called by `UserController.GetUser` line 24. | Keep it. |
| SampleBankingApp/Services/UserService.cs | 38 | `UserService.UpdateUser` is called by `UserController.UpdateUser` line 43. | Keep it. |
| SampleBankingApp/Services/UserService.cs | 52 | `UserService.DeleteUser` is called by `UserController.DeleteUser` line 61. | Keep it. |
| SampleBankingApp/Services/UserService.cs | 68 | `UserService.GetUsersPage` is called by `UserController.GetUsers` line 34. | Keep it. |
| SampleBankingApp/Services/UserService.cs | 85 | `UserService.GetAuditReport` is called by `UserController.GetAuditLog` line 81. | Keep it. |
| SampleBankingApp/Services/UserService.cs | 95 | `UserService.SearchUsers` is called by `UserController.SearchUsers` line 74. | Keep it. |
| SampleBankingApp/Services/UserService.cs | 111 | `UserService.MapRowToUser` is called by `GetUserById`, `GetUsersPage`, and `SearchUsers`. | Keep it. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `JoinWithSeparator` is a broken duplicate implementation alongside the fixed `JoinWithSeparatorFixed`, and neither is called. | Delete the broken method and keep one correct implementation only if needed. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/UserController.cs | 32 | `GetUsers` hardcodes default `page = 1` and `pageSize = 20`. | Define named paging defaults in configuration or constants. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | `DatabaseHelper` hardcodes `Server=localhost`, `Database=BankingDB`, `User Id=sa`, and a password. | Remove the fallback and require configured connection settings. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `IsValidEmail` hardcodes the maximum email length `254`. | Define a named `MaxEmailLength` constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `IsValidUsername` hardcodes minimum length `3` and maximum length `20`. | Define named `MinUsernameLength` and `MaxUsernameLength` constants. |
| SampleBankingApp/Program.cs | 16 | `Program` repeats the config key `"Jwt:SecretKey"` already used in `AuthService`. | Centralize JWT option binding in a typed settings class. |
| SampleBankingApp/Program.cs | 26 | `Program` repeats config keys `"Jwt:Issuer"` and `"Jwt:Audience"` already used in `AuthService`. | Bind `JwtOptions` once and inject it into both places. |
| SampleBankingApp/Services/AuthService.cs | 17 | `AdminBypassPassword` hardcodes a privileged password in source. | Remove the backdoor entirely. |
| SampleBankingApp/Services/AuthService.cs | 53 | `Login` hardcodes the username `"admin"` and role `"SuperAdmin"`. | Remove the bypass or use configured role constants and seeded identities. |
| SampleBankingApp/Services/AuthService.cs | 84 | `GenerateJwtToken` hardcodes a `30`-day token lifetime. | Move token lifetime into `JwtOptions` configuration. |
| SampleBankingApp/Services/EmailService.cs | 10 | `TransferSubject` hardcodes the product name `"BankingApp"` in an email subject. | Move subject templates into configuration or resources. |
| SampleBankingApp/Services/EmailService.cs | 11 | `WelcomeSubject` hardcodes the product name `"BankingApp"` in an email subject. | Move subject templates into configuration or resources. |
| SampleBankingApp/Services/EmailService.cs | 14 | `SmtpTimeoutMs` hardcodes `5000` milliseconds. | Move the timeout into `EmailOptions` configuration. |
| SampleBankingApp/Services/EmailService.cs | 24 | `EmailService` hardcodes fallback SMTP port `"25"`. | Require a configured port and validate it. |
| SampleBankingApp/Services/EmailService.cs | 40 | `SendTransferNotification` hardcodes `notifications@company.com`. | Move the sender into `EmailOptions`. |
| SampleBankingApp/Services/EmailService.cs | 67 | `SendWelcomeEmail` hardcodes `support@company.com`. | Move the support address into configuration. |
| SampleBankingApp/Services/EmailService.cs | 69 | `SendWelcomeEmail` hardcodes `notifications@company.com`. | Move the sender into `EmailOptions`. |
| SampleBankingApp/Services/EmailService.cs | 88 | `SendWelcomeEmailHtml` hardcodes `"Welcome!"` and `"BankingApp"` in the body. | Move templates into resources or configuration. |
| SampleBankingApp/Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` hardcodes `notifications@company.com`. | Move the sender into `EmailOptions`. |
| SampleBankingApp/Services/TransactionService.cs | 11 | `TransactionFeeRate` hardcodes `0.015m` in source. | Move the fee rate into configuration with versioned rules. |
| SampleBankingApp/Services/TransactionService.cs | 12 | `MaxTransactionsPerDay` hardcodes `10` in source. | Move the daily limit into configuration. |
| SampleBankingApp/Services/TransactionService.cs | 50 | `Transfer` hardcodes transaction type `"Transfer"`. | Use a `TransactionType` enum or constants. |
| SampleBankingApp/Services/TransactionService.cs | 65 | `Deposit` hardcodes deposit cap `1000000`. | Move the cap into configuration and define a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 68 | `Deposit` hardcodes `0.05m` and `* 1` for an interest bonus. | Remove the bonus or move the approved rate and period into configuration. |
| SampleBankingApp/Services/TransactionService.cs | 73 | `Deposit` hardcodes transaction type `"Deposit"`. | Use a `TransactionType` enum or constants. |
| SampleBankingApp/Services/TransactionService.cs | 90 | `RecordTransaction` hardcodes status `'Completed'`. | Use a `TransactionStatus` enum or constants. |
| SampleBankingApp/Services/UserService.cs | 22 | `GetUserById` hardcodes upper user id bound `1000000`. | Remove the arbitrary bound or define a named validated range constant. |
| SampleBankingApp/Services/UserService.cs | 42 | `UpdateUser` repeats the upper user id bound `1000000`. | Extract shared id validation into one helper. |
| SampleBankingApp/Services/UserService.cs | 56 | `DeleteUser` repeats the upper user id bound `1000000`. | Extract shared id validation into one helper. |
| SampleBankingApp/Services/UserService.cs | 70 | `GetUsersPage` hardcodes maximum page size `50`. | Move the maximum page size into configuration or a named constant. |
| SampleBankingApp/appsettings.json | 3 | `DefaultConnection` embeds production host, database, user, and password directly in base configuration. | Use environment-specific overrides and secret storage. |
| SampleBankingApp/appsettings.json | 6 | `SecretKey` embeds a production JWT secret in base configuration. | Use a secret store and environment-specific override. |
| SampleBankingApp/appsettings.json | 14 | `Password` embeds a production SMTP password in base configuration. | Use a secret store and environment-specific override. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | `GetOpenConnection` leaks resource ownership to callers with no documented disposal contract. | Keep connection creation private and expose methods that fully dispose resources. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | `ExecuteQuery` accepts raw SQL fragments and encourages unsafe dynamic query construction. | Replace with a specific `SearchUsers` method using parameters. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `ExecuteNonQuery` accepts raw SQL and encourages callers to build unsafe statements. | Replace with parameterized insert/update/delete helpers. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | `IsValidEmail` constructs `new Regex(...)` inside a method that may be called repeatedly. | Use a `static readonly Regex` with a timeout. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | `IsValidUsername` constructs `new Regex(...)` inside a method that may be called repeatedly. | Use a `static readonly Regex` with a timeout. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `JoinWithSeparator` concatenates strings inside a loop, producing O(n²) behavior. | Use `string.Join(separator, items)` or `StringBuilder`. |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Replace calls with `string.IsNullOrWhiteSpace` and delete the helper. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` mixes password hashing, SQL construction, connection management, user mapping, and a backdoor branch in one method. | Split into `VerifyCredentials`, `FindActiveUser`, `MapUser`, and `IssueToken` helpers. |
| SampleBankingApp/Services/EmailService.cs | 34 | `SendTransferNotification` mixes body construction, `MailMessage` creation, retry logic, and SMTP sending. | Split into `BuildTransferMessage`, `SendWithRetry`, and `DisposeMessage` helpers. |
| SampleBankingApp/Services/EmailService.cs | 63 | `SendWelcomeEmail` mixes body construction, message creation, sending, and swallowed exception handling. | Split into `BuildWelcomeMessage`, `Send`, and typed error handling helpers. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `Transfer` mixes validation, two user lookups, fee calculation, balance updates, transaction recording, and email notification. | Split into `ValidateTransfer`, `LoadAccounts`, `ApplyLedgerWrites`, `RecordTransaction`, and `NotifyTransfer`. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `Deposit` mixes validation, bonus calculation, balance update, and transaction recording. | Split into `ValidateDeposit`, `ApplyCredit`, and `RecordTransaction` helpers. |
| SampleBankingApp/Services/TransactionService.cs | 87 | `RecordTransaction` mixes SQL string construction and execution with unescaped user input. | Split into a parameterized command builder and an executor. |
| SampleBankingApp/Services/UserService.cs | 10 | `_auditLog` is shared mutable static state accessed without synchronization. | Use a thread-safe collection, a scoped audit service, or a database-backed audit table. |
| SampleBankingApp/Services/UserService.cs | 11 | `_requestCount` is shared mutable static state incremented without synchronization. | Use `Interlocked.Increment` or remove the unused counter. |
| SampleBankingApp/Services/UserService.cs | 18 | `GetUserById` repeats the same id validation block used in `UpdateUser` and `DeleteUser`. | Extract `ValidateUserId` and call it from all three methods. |
| SampleBankingApp/Services/UserService.cs | 38 | `UpdateUser` repeats the same id validation block used in `GetUserById` and `DeleteUser`. | Extract `ValidateUserId` and call it from all three methods. |
| SampleBankingApp/Services/UserService.cs | 52 | `DeleteUser` repeats the same id validation block used in `GetUserById` and `UpdateUser`. | Extract `ValidateUserId` and call it from all three methods. |
| SampleBankingApp/Services/UserService.cs | 85 | `GetAuditReport` concatenates strings inside a loop, producing O(n²) behavior. | Use `string.Join(Environment.NewLine, _auditLog)` or `StringBuilder`. |
| SampleBankingApp/Services/UserService.cs | 95 | `SearchUsers` mixes unsafe query construction, row mapping, and broad exception swallowing. | Split into `BuildSearchParameters`, `ExecuteSearch`, and `MapUsers` helpers. |
| SampleBankingApp/Controllers/UserController.cs | 39 | `UpdateUser` mixes service invocation, argument-error translation, broad exception handling, and raw message exposure. | Use centralized exception-handling middleware and a validation filter. |
| SampleBankingApp/Controllers/UserController.cs | 57 | `DeleteUser` mixes service invocation, broad exception handling, logging, and response shaping. | Use centralized exception-handling middleware. |
| SampleBankingApp/Program.cs | 16 | `Program` reads JWT settings inline instead of using the options pattern. | Bind a validated `JwtOptions` class and inject it. |
| SampleBankingApp/Services/EmailService.cs | 18 | `EmailService` reads email settings inline instead of using the options pattern. | Bind a validated `EmailOptions` class and inject it. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables JWT expiration validation. | Set `ValidateLifetime = true`. |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally. | Wrap it in `if (app.Environment.IsDevelopment())`. |
| SampleBankingApp/Program.cs | 36 | `app.UseHttpsRedirection()` is commented out. | Enable HTTPS redirection and HSTS for non-development environments. |
| SampleBankingApp/Program.cs | 38 | CORS uses `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`. | Use a named policy with explicit origins, methods, and headers. |
| SampleBankingApp/SampleBankingApp.csproj | 7 | `TreatWarningsAsErrors` is `false`, allowing compiler warnings to ship silently. | Enable warnings as errors in CI or at least for nullable and security analyzers. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `DebugSymbols` is `true` without a Debug condition. | Condition it to Debug builds. |
| SampleBankingApp/SampleBankingApp.csproj | 9 | `DebugType` is `full` without a Debug condition. | Use `portable` for Debug and avoid full symbols in Release. |
| SampleBankingApp/SampleBankingApp.csproj | 14 | `System.Data.SqlClient` `4.8.6` is a legacy ADO.NET provider for a new .NET 8 app. | Prefer `Microsoft.Data.SqlClient` and keep it patched. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | `Newtonsoft.Json` `12.0.3` is outdated and unused in the provided source. | Remove it or upgrade to a current patched version. |
| SampleBankingApp/SampleBankingApp.csproj | 16 | `System.IdentityModel.Tokens.Jwt` `7.0.0` is outdated relative to the .NET 8 stack. | Align versions with `Microsoft.AspNetCore.Authentication.JwtBearer` 8.x. |
| SampleBankingApp/appsettings.json | 3 | Base `appsettings.json` contains a production connection string with credentials. | Move production values to secure environment configuration. |
| SampleBankingApp/appsettings.json | 6 | Base `appsettings.json` contains a weak JWT secret. | Move the secret to a secret store and rotate it. |
| SampleBankingApp/appsettings.json | 14 | Base `appsettings.json` contains an SMTP password. | Move the password to a secret store. |
| SampleBankingApp/appsettings.json | 18 | `Default` log level is `Debug`. | Use `Information` or `Warning` in production. |
| SampleBankingApp/appsettings.json | 19 | `Microsoft` log level is `Debug`. | Use `Warning` in production. |
| SampleBankingApp/appsettings.json | 20 | `System` log level is `Debug`. | Use `Warning` in production. |
| SampleBankingApp/appsettings.json | 23 | `AllowedHosts` is `"*"`. | Configure an explicit host allowlist. |
| SampleBankingApp/appsettings.json | 1 | No `appsettings.Production.json` or environment-specific override file is present. | Add environment-specific overrides and keep secrets out of source control. |
| SampleBankingApp/appsettings.json | 1 | No `appsettings.Development.json` is present to isolate developer settings. | Add a development override for local non-secret settings. |
| SampleBankingApp/Services/EmailService.cs | 29 | `EnableSsl = false` is hardcoded rather than configured. | Bind `EnableSsl` from `EmailOptions` and require TLS in production. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/SampleBankingApp.csproj | 1 | No test project or test package references exist in the provided source. | Add an xUnit or NUnit test project referencing `SampleBankingApp`. |
| SampleBankingApp/Services/AuthService.cs | 28 | `AuthService.Login` lacks tests for valid credentials, wrong password, inactive user, SQL-injection username, and removal of the admin bypass. | Add service tests with a mocked database helper and assert no bypass path exists. |
| SampleBankingApp/Services/AuthService.cs | 68 | `AuthService.GenerateJwtToken` lacks tests for claims, issuer, audience, signing key, and short token lifetime. | Add token tests that validate the generated token with the same parameters. |
| SampleBankingApp/Services/AuthService.cs | 98 | `AuthService.ValidateToken` lacks tests for empty, expired, wrong-signature, wrong-issuer, and valid tokens. | Add tests after implementing real validation or remove the method. |
| SampleBankingApp/Controllers/AuthController.cs | 20 | `AuthController.Login` lacks tests for null request, unauthorized response, successful token response, and lockout/rate-limit behavior. | Add controller integration tests with a mocked `AuthService`. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `TransactionService.Transfer` lacks boundary tests for zero amount, negative amount, self-transfer, missing source user, missing destination user, exact balance with fee, and insufficient balance with fee. | Add parameterized tests asserting balances and transaction records for each boundary. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `TransactionService.Transfer` lacks atomicity tests for a failed second update, failed transaction insert, and failed email send after commit. | Add tests with a fake database that fails each write and assert rollback or outbox behavior. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `TransactionService.Deposit` lacks tests for zero, negative, exactly `1000000`, above cap, bonus calculation, and missing user. | Add parameterized tests asserting the credited amount and recorded transaction. |
| SampleBankingApp/Services/TransactionService.cs | 77 | `TransactionService.IsWithinDailyLimit` lacks tests for 9, 10, and 11 daily transactions and date boundaries. | Add tests with a fake clock and transaction counts. |
| SampleBankingApp/Services/TransactionService.cs | 99 | `TransactionService.RefundTransaction` lacks tests because it is unimplemented. | Implement refunds and test authorization, idempotency, and balance reversal. |
| SampleBankingApp/Controllers/TransactionController.cs | 24 | `TransactionController.Transfer` lacks tests for missing `NameIdentifier`, non-numeric claim, null request, success, and failure responses. | Add controller tests with a constructed `ClaimsPrincipal`. |
| SampleBankingApp/Controllers/TransactionController.cs | 38 | `TransactionController.Deposit` lacks tests for missing `NameIdentifier`, non-numeric claim, null request, success, and failure responses. | Add controller tests with a constructed `ClaimsPrincipal`. |
| SampleBankingApp/Controllers/TransactionController.cs | 49 | `TransactionController.Refund` lacks tests for unauthenticated, unauthorized, and unimplemented responses. | Add integration tests asserting the correct status code and authorization policy. |
| SampleBankingApp/Services/UserService.cs | 68 | `UserService.GetUsersPage` lacks pagination tests for page 1, page 2, page 0, negative page, zero page size, negative page size, and page size above 50. | Add tests asserting generated `@Skip` and `@PageSize` values. |
| SampleBankingApp/Services/UserService.cs | 95 | `UserService.SearchUsers` lacks tests for wildcard characters, quote characters, empty query, null query, and database exceptions. | Add tests using a parameterized fake database helper. |
| SampleBankingApp/Services/UserService.cs | 18 | `UserService.GetUserById` lacks tests for id 0, id 1, id 1000000, id 1000001, missing row, and `DBNull` columns. | Add tests with a fake `DatabaseHelper` and row fixtures. |
| SampleBankingApp/Services/UserService.cs | 38 | `UserService.UpdateUser` lacks tests for invalid ids, valid update, SQL-injection email, SQL-injection username, and audit log behavior. | Add tests with a fake database helper and assert parameterized commands. |
| SampleBankingApp/Services/UserService.cs | 52 | `UserService.DeleteUser` lacks tests for invalid ids, valid delete, missing user, and audit log behavior. | Add tests with a fake database helper. |
| SampleBankingApp/Controllers/UserController.cs | 22 | `UserController.GetUser` lacks authorization tests for self-access, other-user access, admin access, and not-found responses. | Add integration tests with multiple `ClaimsPrincipal` roles. |
| SampleBankingApp/Controllers/UserController.cs | 39 | `UserController.UpdateUser` lacks authorization tests for self-access, other-user access, null request, validation errors, and generic error masking. | Add controller integration tests with mocked `UserService`. |
| SampleBankingApp/Controllers/UserController.cs | 57 | `UserController.DeleteUser` lacks authorization tests for self-access, other-user access, admin access, and error masking. | Add controller integration tests with mocked `UserService`. |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | `StringHelper.IsValidEmail` lacks tests for null, empty, 254 characters, 255 characters, and malformed addresses. | Add parameterized helper tests or remove the unused helper. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | `StringHelper.IsValidUsername` lacks tests for null, 2 characters, 3 characters, 20 characters, 21 characters, and invalid symbols. | Add parameterized helper tests or remove the unused helper. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `StringHelper.JoinWithSeparator` lacks tests for empty input, one item, multiple items, and trailing separator behavior. | Add tests after replacing it with `string.Join`. |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | `StringHelper.ObfuscateAccount` lacks tests for null, empty, 3-character, 4-character, and long account numbers. | Add tests after adding null and length guards. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | `DatabaseHelper.ExecuteQuery` lacks tests proving that table names and where clauses cannot inject SQL. | Replace with a typed method and add parameterization tests. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `DatabaseHelper.ExecuteNonQuery` lacks tests for disposal on success and exception paths. | Add tests with a failing fake command or refactor to injectable ADO.NET abstractions. |
| SampleBankingApp/Services/EmailService.cs | 34 | `EmailService.SendTransferNotification` lacks tests for retry count, final failure, message disposal, and SMTP TLS configuration. | Add tests with an injectable mail sender abstraction. |
| SampleBankingApp/Program.cs | 17 | JWT bearer configuration lacks tests for expired token rejection, wrong issuer, wrong audience, wrong signature, and valid token acceptance. | Add WebApplicationFactory integration tests against a test configuration. |