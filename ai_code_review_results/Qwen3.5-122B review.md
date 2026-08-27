## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | SQL Injection vulnerability in `ExecuteQuery` via string interpolation of `tableName` and `whereClause`. | Use parameterized queries or validate table names against a whitelist. |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL Injection vulnerability in `Login` via string interpolation of `username` and `hashedPassword`. | Use parameterized queries for all user input. |
| SampleBankingApp/Services/TransactionService.cs | 47 | SQL Injection vulnerability in `Transfer` via string interpolation of `newFromBalance` and `fromUserId`. | Use parameterized queries for all SQL statements. |
| SampleBankingApp/Services/TransactionService.cs | 48 | SQL Injection vulnerability in `Transfer` via string interpolation of `newToBalance` and `toUserId`. | Use parameterized queries for all SQL statements. |
| SampleBankingApp/Services/TransactionService.cs | 90 | SQL Injection vulnerability in `RecordTransaction` via string interpolation of `fromId`, `toId`, `amount`, `type`, `description`. | Use parameterized queries for all SQL statements. |
| SampleBankingApp/Services/UserService.cs | 47 | SQL Injection vulnerability in `UpdateUser` via string interpolation of `email`, `username`, and `id`. | Use parameterized queries for all SQL statements. |
| SampleBankingApp/Services/UserService.cs | 61 | SQL Injection vulnerability in `DeleteUser` via string interpolation of `id`. | Use parameterized queries for all SQL statements. |
| SampleBankingApp/Services/UserService.cs | 99 | SQL Injection vulnerability in `SearchUsers` via string interpolation of `query` in LIKE clause. | Use parameterized queries for all SQL statements. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded database credentials in fallback connection string with password "Admin1234!". | Remove hardcoded credentials and rely on configuration. |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded backdoor password "SuperAdmin2024" in `AdminBypassPassword` constant. | Remove hardcoded backdoor logic entirely. |
| SampleBankingApp/appsettings.json | 3 | Hardcoded database password "Admin1234!" in connection string. | Use environment variables or secret manager for production secrets. |
| SampleBankingApp/appsettings.json | 6 | Hardcoded JWT secret key "mysecretkey" in configuration. | Use environment variables or secret manager for production secrets. |
| SampleBankingApp/appsettings.json | 14 | Hardcoded email password "EmailPass99" in configuration. | Use environment variables or secret manager for production secrets. |
| SampleBankingApp/Services/AuthService.cs | 63 | Weak cryptography used in `HashPasswordMd5` (MD5 is broken for passwords). | Use a secure password hashing algorithm like PBKDF2, BCrypt, or Argon2. |
| SampleBankingApp/Services/AuthService.cs | 93 | Weak cryptography present in `HashPasswordSha1` (SHA1 is broken). | Remove unused weak hashing methods. |
| SampleBankingApp/Program.cs | 24 | JWT token validation disabled (`ValidateLifetime = false`). | Enable `ValidateLifetime` to prevent token replay attacks. |
| SampleBankingApp/Controllers/UserController.cs | 22 | Missing ownership check in `GetUser` allows any user to view any other user's data. | Add authorization check to ensure user can only access their own data. |
| SampleBankingApp/Controllers/UserController.cs | 39 | Missing ownership check in `UpdateUser` allows any user to modify any other user's data. | Add authorization check to ensure user can only modify their own data. |
| SampleBankingApp/Controllers/UserController.cs | 57 | Missing ownership check in `DeleteUser` allows any user to delete any other user. | Add authorization check to ensure user can only delete their own data. |
| SampleBankingApp/Program.cs | 38 | Overly permissive CORS policy (`AllowAnyOrigin` + `AllowAnyMethod`). | Restrict CORS to specific trusted origins and methods. |
| SampleBankingApp/Program.cs | 34 | Developer exception page enabled unconditionally in production. | Use `UseExceptionHandler` or conditionally enable only in development. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out. | Enable HTTPS redirection for secure communication. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | Debug symbols enabled in release builds (`DebugSymbols>true`). | Set `DebugType` to `portable` or `none` for production. |
| SampleBankingApp/SampleBankingApp.csproj | 9 | Full debug type enabled (`DebugType>full`). | Set `DebugType` to `portable` or `none` for production. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/UserService.cs | 72 | Off-by-one error in pagination calculation `page * pageSize` instead of `(page - 1) * pageSize`. | Change calculation to `(page - 1) * pageSize` to start at correct offset. |
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check `fromBalance >= amount` allows negative balance after deducting `amount + fee`. | Check `fromBalance >= amount + fee` before proceeding. |
| SampleBankingApp/Services/TransactionService.cs | 23 | Missing self-referential check in `Transfer` allows transferring funds to oneself. | Add check to ensure `fromUserId` is not equal to `toUserId`. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Hardcoded interest calculation `amount * 0.05m * 1` in `Deposit` uses magic number 1. | Use a named constant for interest multiplier or remove hardcoded logic. |
| SampleBankingApp/Services/TransactionService.cs | 12 | Hardcoded transaction limit `MaxTransactionsPerDay = 10` without configuration. | Move limit to configuration for flexibility. |
| SampleBankingApp/Services/TransactionService.cs | 11 | Hardcoded fee rate `TransactionFeeRate = 0.015m` without configuration. | Move fee rate to configuration for flexibility. |
| SampleBankingApp/Services/UserService.cs | 70 | Hardcoded page size limit `pageSize > 50` without configuration. | Move page size limit to configuration. |
| SampleBankingApp/Services/UserService.cs | 22 | Hardcoded ID range check `id > 1000000` in `GetUserById`. | Move ID range limit to configuration. |
| SampleBankingApp/Services/UserService.cs | 42 | Hardcoded ID range check `id > 1000000` in `UpdateUser`. | Move ID range limit to configuration. |
| SampleBankingApp/Services/UserService.cs | 56 | Hardcoded ID range check `id > 1000000` in `DeleteUser`. | Move ID range limit to configuration. |
| SampleBankingApp/Services/AuthService.cs | 84 | Hardcoded JWT expiry `AddDays(30)` without configuration. | Move JWT expiry duration to configuration. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/UserService.cs | 105 | `SearchUsers` catches broad `Exception` and returns empty list, hiding errors from callers. | Log the exception and rethrow or return a specific error response. |
| SampleBankingApp/Services/EmailService.cs | 75 | `SendWelcomeEmail` catches broad `Exception` and swallows it silently. | Log the exception and rethrow or handle gracefully without hiding failure. |
| SampleBankingApp/Services/TransactionService.cs | 47 | `Transfer` performs multiple DB writes without a transaction, risking data inconsistency. | Wrap DB writes in a database transaction for atomicity. |
| SampleBankingApp/Services/TransactionService.cs | 52 | `Transfer` sends email after DB commit, risking state mismatch if email fails. | Move email sending outside transaction or use a reliable outbox pattern. |
| SampleBankingApp/Services/TransactionService.cs | 70 | `Deposit` performs DB write without a transaction. | Wrap DB write in a database transaction for atomicity. |
| SampleBankingApp/Controllers/UserController.cs | 52 | `UpdateUser` returns raw `ex.Message` to client, potentially leaking stack traces. | Return a generic error message and log details server-side. |
| SampleBankingApp/Controllers/UserController.cs | 67 | `DeleteUser` returns generic message but logs `ex`, which is acceptable but could be improved. | Ensure logging includes sufficient context for debugging. |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | `Refund` catches `NotImplementedException` specifically, which is unusual for HTTP handling. | Return 501 Not Implemented status code directly without try-catch. |
| SampleBankingApp/Controllers/AuthController.cs | 20 | `Login` lacks rate limiting or account lockout mechanism. | Implement rate limiting or account lockout on authentication endpoints. |
| SampleBankingApp/Services/TransactionService.cs | 102 | `RefundTransaction` throws `NotImplementedException` which is caught by controller. | Implement the method or remove the endpoint. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 23 | `GetOpenConnection` returns open connection without ensuring disposal by caller. | Return `IDisposable` connection or use `using` pattern in caller. |
| SampleBankingApp/Data/DatabaseHelper.cs | 30 | `ExecuteQuery` creates `SqlCommand` and `SqlDataAdapter` without disposing them. | Wrap `SqlCommand` and `SqlDataAdapter` in `using` statements. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | `ExecuteNonQuery` calls `GetOpenConnection` and `Close` manually, risking leak on exception. | Use `using` statement for connection to ensure disposal on exception. |
| SampleBankingApp/Services/AuthService.cs | 35 | `Login` opens `SqlConnection` manually without `using` block, risking leak on exception. | Wrap `SqlConnection` in `using` statement. |
| SampleBankingApp/Services/AuthService.cs | 38 | `Login` creates `SqlDataReader` without disposing it. | Wrap `SqlDataReader` in `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 16 | `_smtpClient` field is never disposed, leaking sockets. | Implement `IDisposable` on `EmailService` to dispose `_smtpClient`. |
| SampleBankingApp/Services/EmailService.cs | 39 | `SendTransferNotification` creates `MailMessage` without disposing it. | Wrap `MailMessage` in `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 69 | `SendWelcomeEmail` creates `MailMessage` without disposing it. | Wrap `MailMessage` in `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` creates `MailMessage` without disposing it. | Wrap `MailMessage` in `using` statement. |
| SampleBankingApp/Data/DatabaseHelper.cs | 44 | `ExecuteQuerySafe` creates `SqlDataAdapter` without disposing it. | Wrap `SqlDataAdapter` in `using` statement. |
| SampleBankingApp/Data/DatabaseHelper.cs | 74 | `ExecuteQueryWithParams` creates `SqlDataAdapter` without disposing it. | Wrap `SqlDataAdapter` in `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 44 | `Login` casts `reader["Username"]` to `string` without checking for null DB value. | Use `reader.IsDBNull` or null-coalescing operator before casting. |
| SampleBankingApp/Services/AuthService.cs | 70 | `GenerateJwtToken` accesses `_config["Jwt:SecretKey"]!` assuming non-null. | Validate configuration key exists before use. |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | `Transfer` uses `userIdClaim!` which may be null if claim is missing. | Check for null claim before parsing or return Unauthorized. |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | `Deposit` uses `userIdClaim!` which may be null if claim is missing. | Check for null claim before parsing or return Unauthorized. |
| SampleBankingApp/Services/UserService.cs | 115 | `MapRowToUser` casts `row["Username"]` to `string` without null check. | Use `reader.IsDBNull` or null-coalescing operator before casting. |
| SampleBankingApp/Services/UserService.cs | 116 | `MapRowToUser` casts `row["Email"]` to `string` without null check. | Use `reader.IsDBNull` or null-coalescing operator before casting. |
| SampleBankingApp/Services/UserService.cs | 117 | `MapRowToUser` casts `row["Role"]` to `string` without null check. | Use `reader.IsDBNull` or null-coalescing operator before casting. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `IsValidEmail` accesses `email.Length` without null check on parameter. | Add null check at start of method. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `IsValidUsername` accesses `username.Length` without null check on parameter. | Add null check at start of method. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `JoinWithSeparator` iterates `items` which may be null. | Add null check for `items` parameter. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `MaskAccountNumber` accesses `accountNumber.Length` without null check. | Add null check at start of method. |
| SampleBankingApp/Services/EmailService.cs | 22 | `EmailService` constructor accesses `_config["Email:SmtpHost"]` without null check. | Validate configuration keys exist before use. |
| SampleBankingApp/Services/EmailService.cs | 24 | `EmailService` constructor parses `_config["Email:SmtpPort"]` without null check. | Validate configuration keys exist before use. |
| SampleBankingApp/Program.cs | 28 | `Program.cs` accesses `jwtSecret!` without null check. | Validate configuration key exists before use. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 91 | `HashPasswordSha1` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/AuthService.cs | 98 | `ValidateToken` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/AuthService.cs | 105 | `ValidateToken` contains unreachable code after unconditional `return true`. | Remove unreachable code or fix logic. |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | `IsValidEmail` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | `IsValidUsername` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `JoinWithSeparator` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | `JoinWithSeparatorFixed` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | `MaskAccountNumber` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | `ObfuscateAccount` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | `ToTitleCase` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | `IsBlank` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/TransactionService.cs | 77 | `IsWithinDailyLimit` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/TransactionService.cs | 94 | `FormatCurrency` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/TransactionService.cs | 99 | `RefundTransaction` method throws `NotImplementedException`. | Implement method or remove endpoint. |
| SampleBankingApp/Services/EmailService.cs | 63 | `SendWelcomeEmail` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/EmailService.cs | 81 | `BuildHtmlTemplate` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/EmailService.cs | 86 | `SendWelcomeEmailHtml` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Data/DatabaseHelper.cs | 59 | `TableExists` method is defined but never called. | Remove unused method. |
| SampleBankingApp/Data/DatabaseHelper.cs | 67 | `ExecuteQueryWithParams` method is marked `[Obsolete]` and never called. | Remove obsolete method. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 11 | Magic number `0.015m` used for transaction fee rate. | Define constant or move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 12 | Magic number `10` used for max transactions per day. | Define constant or move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Magic number `0.05m` used for deposit interest rate. | Define constant or move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Magic number `1` used for interest multiplier. | Define constant or move to configuration. |
| SampleBankingApp/Services/UserService.cs | 70 | Magic number `50` used for max page size. | Define constant or move to configuration. |
| SampleBankingApp/Services/UserService.cs | 22 | Magic number `1000000` used for max user ID. | Define constant or move to configuration. |
| SampleBankingApp/Services/UserService.cs | 42 | Magic number `1000000` used for max user ID. | Define constant or move to configuration. |
| SampleBankingApp/Services/UserService.cs | 56 | Magic number `1000000` used for max user ID. | Define constant or move to configuration. |
| SampleBankingApp/Services/AuthService.cs | 84 | Magic number `30` used for JWT expiry days. | Define constant or move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 13 | Magic number `3` used for max retries. | Define constant or move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 14 | Magic number `5000` used for SMTP timeout. | Define constant or move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 40 | Magic string `"notifications@company.com"` used as sender email. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 67 | Magic string `"support@company.com"` used in email body. | Move to configuration. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Magic string connection string fallback hardcoded. | Remove hardcoded fallback. |
| SampleBankingApp/appsettings.json | 6 | Magic string `"mysecretkey"` used for JWT secret. | Use environment variable. |
| SampleBankingApp/appsettings.json | 3 | Magic string `"Admin1234!"` used for DB password. | Use environment variable. |
| SampleBankingApp/appsettings.json | 14 | Magic string `"EmailPass99"` used for email password. | Use environment variable. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 31 | `JoinWithSeparator` uses string concatenation in loop causing O(n²) performance. | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | `IsValidEmail` instantiates `Regex` inside method on every call. | Make `Regex` static readonly. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | `IsValidUsername` instantiates `Regex` inside method on every call. | Make `Regex` static readonly. |
| SampleBankingApp/Services/UserService.cs | 10 | `_auditLog` is static mutable state accessed without synchronization. | Use thread-safe collection or remove static state. |
| SampleBankingApp/Services/UserService.cs | 11 | `_requestCount` is static mutable state accessed without synchronization. | Use thread-safe counter or remove static state. |
| SampleBankingApp/Services/UserService.cs | 87 | `GetAuditReport` uses string concatenation in loop. | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `Transfer` method mixes validation, DB access, and email sending responsibilities. | Split into private helper methods for validation, DB, and notification. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` method mixes authentication, DB access, and backdoor logic. | Split into private helper methods for authentication and backdoor check. |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | `GetOpenConnection` leaks resource ownership to caller without documented contract. | Document disposal requirement or use `using` pattern internally. |
| SampleBankingApp/Services/UserService.cs | 111 | `MapRowToUser` repeats casting logic for multiple fields. | Use helper method or extension for safe casting. |
| SampleBankingApp/Services/EmailService.cs | 16 | `_smtpClient` is a field which is not thread-safe if service is singleton. | Ensure service is scoped or use thread-safe email client. |
| SampleBankingApp/Services/TransactionService.cs | 89 | `RecordTransaction` uses string interpolation for SQL values. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 47 | `UpdateUser` uses string interpolation for SQL values. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 61 | `DeleteUser` uses string interpolation for SQL values. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 99 | `SearchUsers` uses string interpolation for SQL values. | Use parameterized queries. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally. | Wrap in `if (env.IsDevelopment())` check. |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry validation. | Set `ValidateLifetime = true`. |
| SampleBankingApp/Program.cs | 36 | `UseHttpsRedirection()` is commented out. | Uncomment to enforce HTTPS. |
| SampleBankingApp/Program.cs | 38 | CORS policy allows any origin and method. | Restrict to specific origins and methods. |
| SampleBankingApp/SampleBankingApp.csproj | 7 | `TreatWarningsAsErrors` is set to false. | Set to true to enforce code quality. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `DebugSymbols` is true in production build. | Set to false for production. |
| SampleBankingApp/SampleBankingApp.csproj | 9 | `DebugType` is full in production build. | Set to portable or none for production. |
| SampleBankingApp/appsettings.json | 18 | Logging level set to Debug for production. | Set to Warning or Error for production. |
| SampleBankingApp/appsettings.json | 19 | Logging level set to Debug for Microsoft namespace. | Set to Warning or Error for production. |
| SampleBankingApp/appsettings.json | 20 | Logging level set to Debug for System namespace. | Set to Warning or Error for production. |
| SampleBankingApp/appsettings.json | 23 | `AllowedHosts` set to wildcard `*`. | Restrict to specific domains. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp | N/A | No test project exists for the application. | Create a test project and add unit tests. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` method lacks tests for valid login, invalid login, and backdoor bypass. | Add unit tests for authentication logic. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `Transfer` method lacks tests for sufficient funds, insufficient funds, and fee calculation. | Add unit tests for transaction logic. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `Deposit` method lacks tests for valid deposit, invalid amount, and interest calculation. | Add unit tests for deposit logic. |
| SampleBankingApp/Services/UserService.cs | 68 | `GetUsersPage` method lacks tests for pagination boundary conditions. | Add unit tests for pagination logic. |
| SampleBankingApp/Services/UserService.cs | 38 | `UpdateUser` method lacks tests for valid update and invalid ID. | Add unit tests for update logic. |
| SampleBankingApp/Services/UserService.cs | 52 | `DeleteUser` method lacks tests for valid delete and invalid ID. | Add unit tests for delete logic. |
| SampleBankingApp/Controllers/AuthController.cs | 19 | `Login` endpoint lacks tests for success and failure responses. | Add integration tests for login endpoint. |
| SampleBankingApp/Controllers/TransactionController.cs | 23 | `Transfer` endpoint lacks tests for success and failure responses. | Add integration tests for transfer endpoint. |
| SampleBankingApp/Controllers/UserController.cs | 21 | `GetUser` endpoint lacks tests for ownership validation. | Add integration tests for user retrieval. |