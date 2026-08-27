## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin backdoor password `AdminBypassPassword` allows unauthenticated admin access. | Remove the backdoor entirely; never embed bypass credentials in source. |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection via string interpolation of `username` and `hashedPassword` in `Login`. | Use parameterized queries with `@Username` and `@Password` parameters. |
| SampleBankingApp/Services/AuthService.cs | 61 | Passwords hashed with MD5, which is cryptographically broken. | Use a modern hashing algorithm such as PBKDF2, bcrypt, or Argon2 with a per-user salt. |
| SampleBankingApp/Services/AuthService.cs | 63 | No salt is used when hashing the password with MD5. | Generate and store a unique salt per user and combine it with the password before hashing. |
| SampleBankingApp/Services/AuthService.cs | 91 | SHA1 hashing method present, which is also cryptographically broken. | Remove this method and use a modern password hashing algorithm. |
| SampleBankingApp/Services/AuthService.cs | 98 | `ValidateToken` always returns `true` for any non-empty token, bypassing validation. | Remove the early `return true` and implement proper token validation. |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables JWT expiration validation, allowing expired tokens. | Set `ValidateLifetime = true`. |
| SampleBankingApp/Program.cs | 28 | JWT secret key read from config with `!` null-forgiving operator; if missing, `Encoding.UTF8.GetBytes` throws. | Validate the secret is present and sufficiently long at startup. |
| SampleBankingApp/appsettings.json | 6 | JWT secret key is `mysecretkey`, far too short and weak for HMAC-SHA256. | Use a cryptographically random secret of at least 256 bits stored in a secrets vault. |
| SampleBankingApp/appsettings.json | 3 | Production database credentials with `sa` account and password committed to source control. | Move secrets to environment variables or a secrets manager; never use `sa` in production. |
| SampleBankingApp/appsettings.json | 14 | SMTP password committed to source control in plaintext. | Store SMTP credentials in a secrets manager or environment variables. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded fallback connection string with `sa` credentials in source code. | Remove the fallback; throw if the connection string is not configured. |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` called unconditionally, leaking stack traces in production. | Gate behind `if (app.Environment.IsDevelopment())`. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out, allowing plaintext traffic. | Uncomment `app.UseHttpsRedirection()`. |
| SampleBankingApp/Program.cs | 38 | CORS policy allows any origin, any method, and any header. | Restrict to known origins and only the methods/headers required. |
| SampleBankingApp/Controllers/UserController.cs | 38 | `UpdateUser` endpoint has no authorization check that the caller owns the user being updated. | Verify the authenticated user's ID matches the route `id` or has an admin role. |
| SampleBankingApp/Controllers/UserController.cs | 56 | `DeleteUser` endpoint has no authorization check that the caller owns or can delete the user. | Add ownership or admin-role authorization before deleting. |
| SampleBankingApp/Controllers/UserController.cs | 21 | `GetUser` returns any user by ID with no ownership or role check. | Verify the caller is the same user or has an admin role. |
| SampleBankingApp/Controllers/UserController.cs | 78 | `GetAuditLog` endpoint has no authorization restricting it to admins. | Add an `[Authorize(Roles="Admin")]` attribute. |
| SampleBankingApp/Controllers/TransactionController.cs | 48 | `Refund` endpoint has no authorization check; any authenticated user can refund any transaction. | Restrict to admin role and verify transaction ownership. |
| SampleBankingApp/Services/UserService.cs | 47 | SQL injection via string interpolation of `email` and `username` in `UpdateUser`. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 61 | SQL injection via string interpolation of `id` in `DeleteUser`. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 99 | SQL injection via string interpolation of `query` in `SearchUsers` LIKE clause. | Use parameterized queries with `@Query`. |
| SampleBankingApp/Services/TransactionService.cs | 47 | SQL injection via string interpolation of `newFromBalance` and `fromUserId` in `Transfer`. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 48 | SQL injection via string interpolation of `newToBalance` and `toUserId` in `Transfer`. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 71 | SQL injection via string interpolation of `amount + interestBonus` and `userId` in `Deposit`. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 89 | SQL injection via string interpolation of `fromId`, `toId`, `amount`, `type`, and `description` in `RecordTransaction`. | Use parameterized queries. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | `ExecuteQuery` accepts raw `tableName` and `whereClause` strings, enabling SQL injection. | Remove this method or refactor to use a safe allow-list and parameterized WHERE clauses. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `ExecuteNonQuery` accepts raw SQL with no parameters, enabling injection by callers. | Remove or refactor to require parameterized SQL. |
| SampleBankingApp/Controllers/AuthController.cs | 19 | No rate limiting or account lockout on the login endpoint, enabling brute-force attacks. | Add rate limiting and account lockout after repeated failures. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `DebugSymbols` set to `true` in the project file, shipping debug symbols in release builds. | Set `DebugSymbols` to `false` or conditionally enable only in Debug configuration. |
| SampleBankingApp/SampleBankingApp.csproj | 9 | `DebugType` set to `full`, shipping full debug info in all builds. | Set `DebugType` to `none` or `portable` for release. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check uses `fromBalance >= amount` but the actual debit is `amount + fee`, allowing negative balances. | Change the check to `fromBalance >= totalDebit`. |
| SampleBankingApp/Services/TransactionService.cs | 25 | `amount < 0` is rejected but `amount == 0` is allowed, producing a zero-dollar transfer with a fee. | Change to `amount <= 0`. |
| SampleBankingApp/Services/TransactionService.cs | 23 | No check preventing a transfer from a user to themselves. | Add a guard: if `fromUserId == toUserId`, return an error. |
| SampleBankingApp/Services/TransactionService.cs | 36 | `fromUserTable.Rows[0]` is accessed without checking `Rows.Count > 0`, causing an `IndexOutOfRangeException` if the user does not exist. | Check `Rows.Count` before accessing row 0. |
| SampleBankingApp/Services/TransactionService.cs | 37 | `toUserTable.Rows[0]` is accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing row 0. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Interest bonus is `amount * 0.05m * 1`; the `* 1` is a no-op suggesting an intended multiplier was omitted. | Clarify the intended interest rate and remove the no-op. |
| SampleBankingApp/Services/UserService.cs | 72 | Pagination uses `skip = page * pageSize` instead of `(page - 1) * pageSize`, skipping the first page's worth of records on page 1. | Use `(page - 1) * pageSize` for the offset. |
| SampleBankingApp/Services/UserService.cs | 68 | `GetUsersPage` does not validate that `page` or `pageSize` are positive. | Add guards for `page <= 0` and `pageSize <= 0`. |
| SampleBankingApp/Services/TransactionService.cs | 77 | `IsWithinDailyLimit` is defined but never called in `Transfer`, so daily limits are not enforced. | Call `IsWithinDailyLimit` before processing a transfer. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `IsValidEmail` accesses `email.Length` before checking for null, throwing if `email` is null. | Add a null check before accessing `Length`. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `IsValidUsername` accesses `username.Length` before checking for null. | Add a null check before accessing `Length`. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `MaskAccountNumber` accesses `accountNumber.Length` before checking for null. | Add a null check before accessing `Length`. |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | `ObfuscateAccount` uses `account[^4..]` which throws on strings shorter than 4 characters. | Add a length check before slicing. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/UserService.cs | 105 | `SearchUsers` catches `Exception` and returns an empty list, hiding errors from the caller. | Let the exception propagate or return a discriminated result indicating failure. |
| SampleBankingApp/Services/EmailService.cs | 75 | `SendWelcomeEmail` catches broad `Exception` and swallows it silently via `Console.WriteLine`. | Log properly and consider whether the failure should propagate. |
| SampleBankingApp/Controllers/UserController.cs | 50 | `UpdateUser` catches broad `Exception` and returns `ex.Message` to the client, leaking internals. | Return a generic message and log the exception. |
| SampleBankingApp/Controllers/UserController.cs | 46 | `UpdateUser` returns `ex.Message` from `ArgumentException` directly to the client. | Return a sanitized error message. |
| SampleBankingApp/Services/TransactionService.cs | 47 | Two balance updates in `Transfer` are not wrapped in a database transaction, risking inconsistency on partial failure. | Wrap both updates and the transaction record in a single DB transaction. |
| SampleBankingApp/Services/TransactionService.cs | 50 | `RecordTransaction` is called after balance updates without a transaction, so a failure leaves balances changed with no record. | Include `RecordTransaction` inside the same transaction. |
| SampleBankingApp/Services/TransactionService.cs | 52 | `SendTransferNotification` is called after DB writes commit; if email throws, the operation appears failed but the transfer already occurred. | Send the email outside the transaction or use an outbox pattern. |
| SampleBankingApp/Services/EmailService.cs | 56 | Retry logic uses `Console.WriteLine` for logging instead of an `ILogger`. | Inject and use `ILogger<EmailService>`. |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | `Refund` catches `NotImplementedException` and returns HTTP 500, masking a stub as a server error. | Return `501 Not Implemented` or remove the endpoint until implemented. |
| SampleBankingApp/Controllers/AuthController.cs | 20 | `Login` does not handle null `request` from model binding, risking a `NullReferenceException`. | Add a null check on `request`. |
| SampleBankingApp/Controllers/TransactionController.cs | 24 | `Transfer` does not handle null `request` from model binding. | Add a null check on `request`. |
| SampleBankingApp/Controllers/TransactionController.cs | 38 | `Deposit` does not handle null `request` from model binding. | Add a null check on `request`. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 34 | `SqlConnection` created and opened but never disposed if `reader.Read()` returns false or an exception occurs. | Wrap the connection in a `using` statement. |
| SampleBankingApp/Services/AuthService.cs | 37 | `SqlCommand` is never disposed. | Wrap in a `using` statement. |
| SampleBankingApp/Services/AuthService.cs | 38 | `SqlDataReader` is never closed or disposed. | Wrap in a `using` statement. |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | `GetOpenConnection` returns an open connection, but callers like `ExecuteQuery` and `ExecuteNonQuery` do not always dispose it on exception paths. | Return a `Disposable` wrapper or refactor callers to use `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | `ExecuteQuery` creates a connection via `GetOpenConnection` but does not dispose it if `adapter.Fill` throws. | Use a `using` statement for the connection. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | `SqlCommand` in `ExecuteQuery` is never disposed. | Wrap in a `using` statement. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | `ExecuteNonQuery` closes the connection but does not dispose it or the command on exception paths. | Use `using` statements for both. |
| SampleBankingApp/Services/EmailService.cs | 16 | `SmtpClient` is held as an instance field, which is not thread-safe and the socket is never released. | Create and dispose `SmtpClient` per send, or use a proper pooled client. |
| SampleBankingApp/Services/EmailService.cs | 39 | `MailMessage` in `SendTransferNotification` is never disposed. | Wrap in a `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 69 | `MailMessage` in `SendWelcomeEmail` is never disposed. | Wrap in a `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 89 | `MailMessage` in `SendWelcomeEmailHtml` is never disposed. | Wrap in a `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/TransactionController.cs | 27 | `userIdClaim!` uses null-forgiving operator; if the claim is missing, `int.Parse` throws. | Check for null before parsing. |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | `userIdClaim!` uses null-forgiving operator; if the claim is missing, `int.Parse` throws. | Check for null before parsing. |
| SampleBankingApp/Program.cs | 28 | `jwtSecret!` is passed to `Encoding.UTF8.GetBytes` with null-forgiving operator; if config is missing, this throws. | Validate the secret is non-null before use. |
| SampleBankingApp/Services/AuthService.cs | 70 | `_config["Jwt:SecretKey"]!` passed to `Encoding.UTF8.GetBytes` without null guard. | Validate the key is non-null and sufficiently long. |
| SampleBankingApp/Services/AuthService.cs | 81 | `_config["Jwt:Issuer"]` may return null, which is passed as `issuer` to the token constructor. | Read into a local variable and validate. |
| SampleBankingApp/Services/AuthService.cs | 82 | `_config["Jwt:Audience"]` may return null, which is passed as `audience` to the token constructor. | Read into a local variable and validate. |
| SampleBankingApp/Services/EmailService.cs | 22 | `_config["Email:SmtpHost"]` may return null, causing `SmtpClient` constructor to throw. | Validate the host is non-null. |
| SampleBankingApp/Services/EmailService.cs | 26 | `_config["Email:Username"]` and `_config["Email:Password"]` may return null, creating null credentials. | Validate before use. |
| SampleBankingApp/Services/TransactionService.cs | 36 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` first. |
| SampleBankingApp/Services/TransactionService.cs | 37 | `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` first. |
| SampleBankingApp/Services/TransactionService.cs | 53 | `fromUserTable.Rows[0]["Email"]` cast without null check. | Validate the row and column exist. |
| SampleBankingApp/Services/TransactionService.cs | 55 | `toUserTable.Rows[0]["Username"]` cast without null check. | Validate the row and column exist. |
| SampleBankingApp/Services/EmailService.cs | 65 | `username.ToUpper()` called without null check on the parameter. | Add a null guard. |
| SampleBankingApp/Controllers/UserController.cs | 39 | `request` is model-bound without a null check before accessing `request.Email` and `request.Username`. | Add a null check on `request`. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `email.Length` accessed without null check in `IsValidEmail`. | Add a null check. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `username.Length` accessed without null check in `IsValidUsername`. | Add a null check. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `accountNumber.Length` accessed without null check in `MaskAccountNumber`. | Add a null check. |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | `account[^4..]` in `ObfuscateAccount` throws on null or short input. | Add null and length checks. |

## 6. Dead Code

| File | Line | Method | Status |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 91 | `HashPasswordSha1` | No callers found in any source file. |
| SampleBankingApp/Services/AuthService.cs | 98 | `ValidateToken` | No callers found in any source file. |
| SampleBankingApp/Services/TransactionService.cs | 77 | `IsWithinDailyLimit` | No callers found in any source file. |
| SampleBankingApp/Services/TransactionService.cs | 94 | `FormatCurrency` | No callers found in any source file. |
| SampleBankingApp/Services/TransactionService.cs | 99 | `RefundTransaction` | Only called by the controller which catches `NotImplementedException`; effectively dead stub code. |
| SampleBankingApp/Services/EmailService.cs | 81 | `BuildHtmlTemplate` | Only called by `SendWelcomeEmailHtml`; see next row. |
| SampleBankingApp/Services/EmailService.cs | 86 | `SendWelcomeEmailHtml` | No callers found in any source file. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `JoinWithSeparator` | No callers found in any source file. |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | `JoinWithSeparatorFixed` | No callers found in any source file. |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | `MaskAccountNumber` | No callers found in any source file. |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | `ObfuscateAccount` | No callers found in any source file. |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | `ToTitleCase` | No callers found in any source file. |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | `IsBlank` | No callers found in any source file. |
| SampleBankingApp/Data/DatabaseHelper.cs | 67 | `ExecuteQueryWithParams` | Marked `[Obsolete]` and no callers found; should be removed. |
| SampleBankingApp/Data/DatabaseHelper.cs | 59 | `TableExists` | No callers found in any source file. |
| SampleBankingApp/Services/AuthService.cs | 105 | Code after `return true` in `ValidateToken` is unreachable. | Remove the unreachable code or fix the method. |
| SampleBankingApp/Services/EmailService.cs | 63 | `SendWelcomeEmail` | No callers found in any source file. |
| SampleBankingApp/Services/EmailService.cs | 34 | `SendTransferNotification` | Called by `TransactionService.Transfer`; not dead. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 11 | `TransactionFeeRate = 0.015m` is a named constant but `0.015m` is a magic number with no documentation of its origin. | Add a comment or move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 65 | `1000000` deposit cap is a magic number inline. | Extract to a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 68 | `0.05m` interest rate is a magic number inline. | Extract to a named constant. |
| SampleBankingApp/Services/UserService.cs | 22 | `1000000` max user ID is a magic number repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. | Extract to a named constant. |
| SampleBankingApp/Services/UserService.cs | 70 | `50` max page size is a magic number inline. | Extract to a named constant. |
| SampleBankingApp/Services/AuthService.cs | 84 | `30` days token expiry is a magic number inline. | Extract to a named constant or configuration value. |
| SampleBankingApp/Services/EmailService.cs | 40 | `"notifications@company.com"` from address is a magic string repeated on lines 40, 69, and 89. | Extract to a constant or configuration. |
| SampleBankingApp/Services/EmailService.cs | 67 | `"support@company.com"` is a magic string inline. | Extract to a constant or configuration. |
| SampleBankingApp/Services/AuthService.cs | 53 | `"admin"` username and `"SuperAdmin"` role are magic strings. | Extract to named constants. |
| SampleBankingApp/Services/AuthService.cs | 55 | `"SuperAdmin"` role string is a magic string. | Extract to a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 90 | `'Completed'` status string is a magic string inline. | Extract to a constant or enum. |
| SampleBankingApp/Services/TransactionService.cs | 73 | `"Deposit"` type string is a magic string inline. | Extract to a constant or enum. |
| SampleBankingApp/Services/TransactionService.cs | 50 | `"Transfer"` type string is a magic string inline. | Extract to a constant or enum. |
| SampleBankingApp/Program.cs | 16 | `"Jwt:SecretKey"` config key is a magic string repeated in `Program.cs` and `AuthService.cs`. | Extract to a shared constant. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 31 | `JoinWithSeparator` uses string concatenation in a loop, O(n²). | Use `string.Join` as done in `JoinWithSeparatorFixed`. |
| SampleBankingApp/Services/UserService.cs | 87 | `GetAuditReport` uses string concatenation in a loop, O(n²). | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | `new Regex(...)` created on every call to `IsValidEmail`. | Make the regex `static readonly`. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | `new Regex(...)` created on every call to `IsValidUsername`. | Make the regex `static readonly`. |
| SampleBankingApp/Services/UserService.cs | 10 | `_auditLog` is a shared mutable static `List<string>` accessed from multiple requests without synchronization. | Use a thread-safe collection or protect with a lock. |
| SampleBankingApp/Services/UserService.cs | 11 | `_requestCount` is a shared mutable static int accessed from multiple threads without synchronization. | Use `Interlocked.Increment`. |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Replace with `string.IsNullOrWhiteSpace(value)`. |
| SampleBankingApp/Services/UserService.cs | 38 | `UpdateUser` duplicates the ID validation logic from `GetUserById`. | Extract ID validation to a shared private method. |
| SampleBankingApp/Services/UserService.cs | 52 | `DeleteUser` duplicates the same ID validation logic. | Extract ID validation to a shared private method. |
| SampleBankingApp/Services/UserService.cs | 18 | `GetUserById` duplicates the same ID validation logic. | Extract ID validation to a shared private method. |
| SampleBankingApp/Services/EmailService.cs | 16 | `SmtpClient` held as instance field is an anti-pattern; it is not thread-safe and sockets leak. | Create per-use or use a factory. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `Transfer` has three responsibilities: validation, balance updates, and notification, which should be split. | Extract into `ValidateTransfer`, `ExecuteTransfer`, and `NotifyTransfer` helpers. |
| SampleBankingApp/Services/UserService.cs | 38 | `UpdateUser` mixes validation, audit logging, and data access in one method. | Split into `ValidateUserId`, `LogAudit`, and `PersistUserUpdate` helpers. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` mixes authentication, SQL query construction, user mapping, and backdoor logic. | Split into `FetchUser`, `MapUser`, and remove the backdoor. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `JoinWithSeparator` is a broken duplicate of `JoinWithSeparatorFixed`. | Remove the broken version. |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | `GetOpenConnection` leaks resource ownership to callers with no documented contract. | Document the disposal contract or return a disposed-managed wrapper. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` called unconditionally regardless of environment. | Gate behind `app.Environment.IsDevelopment()`. |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables JWT lifetime validation. | Set to `true`. |
| SampleBankingApp/Program.cs | 36 | `UseHttpsRedirection` is commented out. | Uncomment it. |
| SampleBankingApp/Program.cs | 38 | CORS allows any origin, method, and header. | Restrict to known origins. |
| SampleBankingApp/appsettings.json | 18 | Log level set to `Debug` for all namespaces including `Microsoft` and `System`. | Use `Information` or `Warning` for production. |
| SampleBankingApp/appsettings.json | 1 | No `appsettings.Production.json` override file exists. | Add production-specific overrides for logging, secrets, and connection strings. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | `Newtonsoft.Json` version `12.0.3` is outdated and has known vulnerabilities. | Upgrade to the latest 13.x version or remove if unused. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `DebugSymbols` enabled unconditionally. | Condition on Debug configuration. |
| SampleBankingApp/SampleBankingApp.csproj | 9 | `DebugType` set to `full` unconditionally. | Condition on Debug configuration. |
| SampleBankingApp/appsettings.json | 3 | `TrustServerCertificate=True` disables certificate validation for the database connection. | Use a proper server certificate. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp | N/A | No test project exists in the solution. | Add a `SampleBankingApp.Tests` project. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `Transfer` has no tests for the insufficient-funds boundary where balance equals `amount` but not `amount + fee`. | Add a test verifying the fee is included in the balance check. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `Transfer` has no test for self-transfer. | Add a test verifying a self-transfer is rejected. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `Deposit` has no tests for boundary amounts (0, 1, 1000000, 1000001). | Add boundary tests. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `Deposit` has no test verifying the interest bonus calculation. | Add a test verifying the bonus is correctly applied. |
| SampleBankingApp/Services/UserService.cs | 68 | `GetUsersPage` has no test for the off-by-one pagination bug. | Add a test verifying page 1 returns the first `pageSize` records. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` has no tests for invalid credentials, disabled users, or SQL injection attempts. | Add auth flow tests. |
| SampleBankingApp/Services/AuthService.cs | 68 | `GenerateJwtToken` has no test verifying token claims and expiry. | Add a test asserting claims and expiration. |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | `IsValidEmail` has no tests for null, empty, and malformed inputs. | Add parameterized tests. |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | `MaskAccountNumber` has no tests for short and null inputs. | Add boundary tests. |
| SampleBankingApp/Services/UserService.cs | 38 | `UpdateUser` has no tests for SQL injection via email or username. | Add injection-prevention tests. |