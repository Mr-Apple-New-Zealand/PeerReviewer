## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 29 | Hardcoded backdoor password `SuperAdmin2024` allows unauthorized admin access. | Remove the hardcoded check and enforce standard authentication for all users. |
| SampleBankingApp/Services/AuthService.cs | 33 | SQL Injection vulnerability via string interpolation in the `Login` query. | Use parameterized queries exclusively for all database interactions. |
| SampleBankingApp/Services/AuthService.cs | 54 | Weak cryptography using MD5 for password hashing. | Replace MD5 with a secure algorithm like PBKDF2, bcrypt, or Argon2. |
| SampleBankingApp/Services/AuthService.cs | 86 | Unused SHA1 hashing method indicates weak crypto practices. | Remove the `HashPasswordSha1` method entirely. |
| SampleBankingApp/Program.cs | 28 | JWT `ValidateLifetime` is set to `false`, allowing expired tokens to be accepted. | Set `ValidateLifetime` to `true` to enforce token expiration. |
| SampleBankingApp/Program.cs | 36 | `UseDeveloperExceptionPage()` is enabled, exposing stack traces in production. | Wrap in `if (app.Environment.IsDevelopment())` or remove for production. |
| SampleBankingApp/Program.cs | 40 | CORS policy allows any origin and method, exposing the API to CSRF and data theft. | Restrict CORS to specific trusted origins and methods. |
| SampleBankingApp/Services/EmailService.cs | 26 | SSL is disabled (`EnableSsl = false`) for SMTP, risking credential interception. | Enable SSL/TLS for SMTP connections. |
| SampleBankingApp/Services/EmailService.cs | 23 | SMTP credentials are read from config but hardcoded in `appsettings.json`. | Move secrets to environment variables or a secure secret manager. |
| SampleBankingApp/Data/DatabaseHelper.cs | 17 | Hardcoded database credentials in the fallback connection string. | Remove hardcoded credentials and rely solely on secure configuration. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | SQL Injection via `tableName` and `whereClause` string interpolation. | Validate table names against a whitelist and use parameters for values. |
| SampleBankingApp/Services/UserService.cs | 104 | SQL Injection via `query` parameter in `SearchUsers` method. | Use parameterized queries for the `LIKE` clause instead of string interpolation. |
| SampleBankingApp/Services/TransactionService.cs | 72 | SQL Injection in `RecordTransaction` via string interpolation of values. | Use parameterized queries for all `INSERT` statements. |
| SampleBankingApp/Services/TransactionService.cs | 56 | SQL Injection in `Transfer` method via string interpolation of balances. | Use parameterized queries for `UPDATE` statements. |
| SampleBankingApp/Services/UserService.cs | 50 | SQL Injection in `UpdateUser` via string interpolation of email and username. | Use parameterized queries for `UPDATE` statements. |
| SampleBankingApp/Services/UserService.cs | 64 | SQL Injection in `DeleteUser` via string interpolation of ID. | Use parameterized queries for `DELETE` statements. |
| SampleBankingApp/Controllers/UserController.cs | 64 | Missing authorization check on `GetAuditLog` endpoint exposes internal logs. | Add `[Authorize(Roles = "Admin")]` or similar restriction. |
| SampleBankingApp/Controllers/UserController.cs | 46 | Missing authorization check on `UpdateUser` allows any authenticated user to modify others. | Verify that the `id` in the URL matches the authenticated user's ID or enforce admin role. |
| SampleBankingApp/Controllers/UserController.cs | 58 | Missing authorization check on `DeleteUser` allows any authenticated user to delete others. | Verify ownership or enforce admin role before deletion. |
| SampleBankingApp/Services/AuthService.cs | 33 | Passwords are stored in plain text or weak hash, not salted. | Implement salting and use a strong hashing algorithm. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 58 | Balance check `fromBalance >= amount` ignores the transaction fee, causing overdrafts. | Change condition to `fromBalance >= (amount + fee)`. |
| SampleBankingApp/Services/TransactionService.cs | 62 | `RecordTransaction` is called after DB updates, risking inconsistent state if email fails. | Ensure atomicity or handle email failure without rolling back DB. |
| SampleBankingApp/Services/TransactionService.cs | 76 | Deposit logic adds `amount + interestBonus` but does not verify if `amount` is valid before calculation. | Validate `amount` before calculating interest. |
| SampleBankingApp/Services/TransactionService.cs | 86 | `IsWithinDailyLimit` is defined but never called in `Transfer`. | Call `IsWithinDailyLimit` before processing the transfer. |
| SampleBankingApp/Services/UserService.cs | 80 | Pagination logic uses `page * pageSize` instead of `(page - 1) * pageSize`, skipping the first page. | Change calculation to `(page - 1) * pageSize`. |
| SampleBankingApp/Services/UserService.cs | 104 | `SearchUsers` returns an empty list on any exception, masking real errors. | Log the exception and rethrow or return a specific error response. |
| SampleBankingApp/Controllers/TransactionController.cs | 22 | `int.Parse` on `userIdClaim` throws if claim is missing or invalid, causing 500 error. | Add null check and validation before parsing. |
| SampleBankingApp/Controllers/TransactionController.cs | 35 | `int.Parse` on `userIdClaim` throws if claim is missing or invalid, causing 500 error. | Add null check and validation before parsing. |
| SampleBankingApp/Services/AuthService.cs | 33 | `Login` method returns `null` if user not found, but also returns a hardcoded admin user if credentials match backdoor. | Remove backdoor logic to prevent logic bypass. |
| SampleBankingApp/Services/TransactionService.cs | 45 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`, risking `IndexOutOfRangeException`. | Check `Rows.Count` before accessing index 0. |
| SampleBankingApp/Services/TransactionService.cs | 48 | `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`, risking `IndexOutOfRangeException`. | Check `Rows.Count` before accessing index 0. |
| SampleBankingApp/Services/UserService.cs | 32 | `table.Rows[0]` accessed without checking `Rows.Count > 0` in `GetUserById`. | Check `Rows.Count` before accessing index 0. |
| SampleBankingApp/Services/UserService.cs | 112 | `MapRowToUser` casts `row["Id"]` to `int` without checking if the value is null or DBNull. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 113 | `MapRowToUser` casts `row["Username"]` to `string` without checking for null/DBNull. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 114 | `MapRowToUser` casts `row["Email"]` to `string` without checking for null/DBNull. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 115 | `MapRowToUser` casts `row["Role"]` to `string` without checking for null/DBNull. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 116 | `MapRowToUser` casts `row["Balance"]` to `decimal` without checking for null/DBNull. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 117 | `MapRowToUser` casts `row["IsActive"]` to `bool` without checking for null/DBNull. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 118 | `MapRowToUser` casts `row["CreatedAt"]` to `DateTime` without checking for null/DBNull. | Check for `DBNull.Value` before casting. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/UserController.cs | 52 | Catch block returns `ex.Message` directly to client, potentially leaking stack traces. | Log the full exception and return a generic error message to the client. |
| SampleBankingApp/Controllers/UserController.cs | 60 | Catch block returns generic "An error occurred" without logging the specific exception details. | Log the exception details before returning the generic message. |
| SampleBankingApp/Controllers/TransactionController.cs | 48 | Catch block for `NotImplementedException` returns 500, but the method always throws this. | Remove the try-catch and let the exception propagate or implement the method. |
| SampleBankingApp/Services/UserService.cs | 104 | Catch block swallows all exceptions and returns an empty list, hiding failures. | Log the exception and rethrow or return a specific error code. |
| SampleBankingApp/Services/TransactionService.cs | 62 | Email sending occurs after DB updates; if email fails, the transaction is committed but user not notified. | Wrap DB and Email operations in a transaction or handle email failure gracefully. |
| SampleBankingApp/Services/EmailService.cs | 48 | Catch block logs to `Console.WriteLine` instead of using the logger. | Use `_logger` for consistent logging. |
| SampleBankingApp/Services/EmailService.cs | 63 | Catch block swallows exceptions and logs to `Console.WriteLine`, hiding failures. | Use `_logger` and rethrow or handle the error appropriately. |
| SampleBankingApp/Services/AuthService.cs | 33 | `Login` method opens a connection but does not dispose it if an exception occurs. | Use `using` statements for `SqlConnection` and `SqlCommand`. |
| SampleBankingApp/Services/AuthService.cs | 33 | `Login` method does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/AuthService.cs | 86 | `ValidateToken` method returns `true` immediately, ignoring the actual token validation logic below. | Remove the early return or implement the validation logic correctly. |
| SampleBankingApp/Services/TransactionService.cs | 72 | `RecordTransaction` does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/TransactionService.cs | 86 | `IsWithinDailyLimit` does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/UserService.cs | 32 | `GetUserById` does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/UserService.cs | 50 | `UpdateUser` does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/UserService.cs | 64 | `DeleteUser` does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/UserService.cs | 80 | `GetUsersPage` does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/UserService.cs | 104 | `SearchUsers` catches all exceptions and returns an empty list, hiding failures. | Log the exception and rethrow or return a specific error code. |
| SampleBankingApp/Services/UserService.cs | 112 | `MapRowToUser` does not handle exceptions during casting. | Add null checks and handle `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 113 | `MapRowToUser` does not handle exceptions during casting. | Add null checks and handle `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 114 | `MapRowToUser` does not handle exceptions during casting. | Add null checks and handle `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 115 | `MapRowToUser` does not handle exceptions during casting. | Add null checks and handle `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 116 | `MapRowToUser` does not handle exceptions during casting. | Add null checks and handle `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 117 | `MapRowToUser` does not handle exceptions during casting. | Add null checks and handle `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 118 | `MapRowToUser` does not handle exceptions during casting. | Add null checks and handle `DBNull.Value` before casting. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 33 | `SqlConnection` and `SqlCommand` are opened but never closed or disposed. | Wrap `SqlConnection` and `SqlCommand` in `using` statements. |
| SampleBankingApp/Services/AuthService.cs | 33 | `SqlDataReader` is not disposed after use. | Wrap `SqlDataReader` in a `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 23 | `SmtpClient` is held as an instance field, which is not thread-safe and may leak sockets. | Create a new `SmtpClient` per request or use `IHttpClientFactory` equivalent for SMTP. |
| SampleBankingApp/Services/EmailService.cs | 40 | `MailMessage` is created but never disposed. | Wrap `MailMessage` in a `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 58 | `MailMessage` is created but never disposed. | Wrap `MailMessage` in a `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 72 | `MailMessage` is created but never disposed. | Wrap `MailMessage` in a `using` statement. |
| SampleBankingApp/Data/DatabaseHelper.cs | 22 | `GetOpenConnection` returns an open connection that the caller must close, risking leaks. | Return a `using`-wrapped connection or manage disposal internally. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | `ExecuteQuery` opens a connection but does not dispose it if an exception occurs. | Wrap `SqlConnection` and `SqlCommand` in `using` statements. |
| SampleBankingApp/Data/DatabaseHelper.cs | 42 | `ExecuteNonQuery` opens a connection but does not dispose it if an exception occurs. | Wrap `SqlConnection` and `SqlCommand` in `using` statements. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | `TableExists` opens a connection but does not dispose it if an exception occurs. | Wrap `SqlConnection` in a `using` statement. |
| SampleBankingApp/Data/DatabaseHelper.cs | 60 | `ExecuteQueryWithParams` opens a connection but does not dispose it if an exception occurs. | Wrap `SqlConnection` and `SqlCommand` in `using` statements. |
| SampleBankingApp/Services/TransactionService.cs | 45 | `fromUserTable` is a `DataTable` that is not disposed. | `DataTable` does not implement `IDisposable`, but ensure it is not held in memory unnecessarily. |
| SampleBankingApp/Services/TransactionService.cs | 48 | `toUserTable` is a `DataTable` that is not disposed. | `DataTable` does not implement `IDisposable`, but ensure it is not held in memory unnecessarily. |
| SampleBankingApp/Services/UserService.cs | 32 | `table` is a `DataTable` that is not disposed. | `DataTable` does not implement `IDisposable`, but ensure it is not held in memory unnecessarily. |
| SampleBankingApp/Services/UserService.cs | 50 | `table` is a `DataTable` that is not disposed. | `DataTable` does not implement `IDisposable`, but ensure it is not held in memory unnecessarily. |
| SampleBankingApp/Services/UserService.cs | 64 | `table` is a `DataTable` that is not disposed. | `DataTable` does not implement `IDisposable`, but ensure it is not held in memory unnecessarily. |
| SampleBankingApp/Services/UserService.cs | 80 | `table` is a `DataTable` that is not disposed. | `DataTable` does not implement `IDisposable`, but ensure it is not held in memory unnecessarily. |
| SampleBankingApp/Services/UserService.cs | 104 | `table` is a `DataTable` that is not disposed. | `DataTable` does not implement `IDisposable`, but ensure it is not held in memory unnecessarily. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/AuthController.cs | 22 | `request.Username` and `request.Password` are used without null checks. | Add null checks for `request.Username` and `request.Password`. |
| SampleBankingApp/Controllers/TransactionController.cs | 22 | `userIdClaim` is accessed with `?.Value` but then `int.Parse` is called on a potentially null string. | Add a null check before calling `int.Parse`. |
| SampleBankingApp/Controllers/TransactionController.cs | 35 | `userIdClaim` is accessed with `?.Value` but then `int.Parse` is called on a potentially null string. | Add a null check before calling `int.Parse`. |
| SampleBankingApp/Controllers/UserController.cs | 22 | `request.Email` and `request.Username` are used without null checks. | Add null checks for `request.Email` and `request.Username`. |
| SampleBankingApp/Controllers/UserController.cs | 64 | `query` parameter is used without null check. | Add a null check for `query`. |
| SampleBankingApp/Services/AuthService.cs | 33 | `username` and `password` are used without null checks. | Add null checks for `username` and `password`. |
| SampleBankingApp/Services/AuthService.cs | 54 | `password` is used without null check. | Add a null check for `password`. |
| SampleBankingApp/Services/AuthService.cs | 62 | `_config["Jwt:SecretKey"]` is accessed with `!` operator, risking null reference. | Add a null check before using the value. |
| SampleBankingApp/Services/AuthService.cs | 62 | `_config["Jwt:Issuer"]` is accessed without null check. | Add a null check before using the value. |
| SampleBankingApp/Services/AuthService.cs | 62 | `_config["Jwt:Audience"]` is accessed without null check. | Add a null check before using the value. |
| SampleBankingApp/Services/AuthService.cs | 86 | `token` is used without null check. | Add a null check for `token`. |
| SampleBankingApp/Services/EmailService.cs | 23 | `_config["Email:SmtpHost"]` is accessed without null check. | Add a null check before using the value. |
| SampleBankingApp/Services/EmailService.cs | 23 | `_config["Email:SmtpPort"]` is accessed without null check. | Add a null check before using the value. |
| SampleBankingApp/Services/EmailService.cs | 23 | `_config["Email:Username"]` is accessed without null check. | Add a null check before using the value. |
| SampleBankingApp/Services/EmailService.cs | 23 | `_config["Email:Password"]` is accessed without null check. | Add a null check before using the value. |
| SampleBankingApp/Services/EmailService.cs | 40 | `toEmail` is used without null check. | Add a null check for `toEmail`. |
| SampleBankingApp/Services/EmailService.cs | 58 | `toEmail` is used without null check. | Add a null check for `toEmail`. |
| SampleBankingApp/Services/EmailService.cs | 72 | `toEmail` is used without null check. | Add a null check for `toEmail`. |
| SampleBankingApp/Services/TransactionService.cs | 45 | `fromUserTable.Rows[0]` is accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing index 0. |
| SampleBankingApp/Services/TransactionService.cs | 48 | `toUserTable.Rows[0]` is accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing index 0. |
| SampleBankingApp/Services/TransactionService.cs | 62 | `fromUserTable.Rows[0]["Email"]` is cast to `string` without null check. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/TransactionService.cs | 62 | `toUserTable.Rows[0]["Username"]` is cast to `string` without null check. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 32 | `table.Rows[0]` is accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing index 0. |
| SampleBankingApp/Services/UserService.cs | 50 | `email` and `username` are used without null checks. | Add null checks for `email` and `username`. |
| SampleBankingApp/Services/UserService.cs | 104 | `query` is used without null check. | Add a null check for `query`. |
| SampleBankingApp/Services/UserService.cs | 112 | `row["Id"]` is cast to `int` without checking for null/DBNull. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 113 | `row["Username"]` is cast to `string` without checking for null/DBNull. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 114 | `row["Email"]` is cast to `string` without checking for null/DBNull. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 115 | `row["Role"]` is cast to `string` without checking for null/DBNull. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 116 | `row["Balance"]` is cast to `decimal` without checking for null/DBNull. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 117 | `row["IsActive"]` is cast to `bool` without checking for null/DBNull. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 118 | `row["CreatedAt"]` is cast to `DateTime` without checking for null/DBNull. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | `email.Length` is accessed without null check. | Add a null check for `email`. |
| SampleBankingApp/Helpers/StringHelper.cs | 19 | `username.Length` is accessed without null check. | Add a null check for `username`. |
| SampleBankingApp/Helpers/StringHelper.cs | 36 | `accountNumber.Length` is accessed without null check. | Add a null check for `accountNumber`. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `account[^4..]` is accessed without null check. | Add a null check for `account`. |
| SampleBankingApp/Helpers/StringHelper.cs | 51 | `input` is used without null check. | Add a null check for `input`. |
| SampleBankingApp/Helpers/StringHelper.cs | 58 | `value` is used without null check. | Add a null check for `value`. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 86 | `ValidateToken` method returns `true` immediately, making the rest of the method unreachable. | Remove the early return or implement the validation logic correctly. |
| SampleBankingApp/Services/AuthService.cs | 86 | `ValidateToken` method has unreachable code after `return true`. | Remove the unreachable code. |
| SampleBankingApp/Services/AuthService.cs | 54 | `HashPasswordSha1` method is never called. | Remove the unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 30 | `JoinWithSeparator` method is never called. | Remove the unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 36 | `JoinWithSeparatorFixed` method is never called. | Remove the unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `ObfuscateAccount` method is never called. | Remove the unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 51 | `ToTitleCase` method is never called. | Remove the unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 58 | `IsBlank` method is never called. | Remove the unused method. |
| SampleBankingApp/Services/TransactionService.cs | 86 | `IsWithinDailyLimit` method is never called. | Call the method in `Transfer` or remove it. |
| SampleBankingApp/Services/TransactionService.cs | 92 | `FormatCurrency` method is never called. | Remove the unused method. |
| SampleBankingApp/Services/TransactionService.cs | 96 | `RefundTransaction` method throws `NotImplementedException`. | Implement the method or remove it. |
| SampleBankingApp/Services/EmailService.cs | 68 | `BuildHtmlTemplate` method is never called. | Remove the unused method. |
| SampleBankingApp/Services/EmailService.cs | 72 | `SendWelcomeEmailHtml` method is never called. | Remove the unused method. |
| SampleBankingApp/Data/DatabaseHelper.cs | 60 | `ExecuteQueryWithParams` method is marked `[Obsolete]` but still present. | Remove the obsolete method. |
| SampleBankingApp/Controllers/TransactionController.cs | 48 | `Refund` method catches `NotImplementedException` and returns 500, but the method always throws. | Remove the try-catch and let the exception propagate or implement the method. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 17 | `TransactionFeeRate` is hardcoded as `0.015m`. | Move to configuration or a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 18 | `MaxTransactionsPerDay` is hardcoded as `10`. | Move to configuration or a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 76 | `0.05m` interest rate is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 76 | `1` multiplier for interest is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 86 | `MaxTransactionsPerDay` is hardcoded as `10`. | Move to configuration or a named constant. |
| SampleBankingApp/Services/UserService.cs | 26 | `1000000` is hardcoded as a max user ID. | Move to configuration or a named constant. |
| SampleBankingApp/Services/UserService.cs | 44 | `1000000` is hardcoded as a max user ID. | Move to configuration or a named constant. |
| SampleBankingApp/Services/UserService.cs | 58 | `1000000` is hardcoded as a max user ID. | Move to configuration or a named constant. |
| SampleBankingApp/Services/UserService.cs | 76 | `50` is hardcoded as a max page size. | Move to configuration or a named constant. |
| SampleBankingApp/Services/EmailService.cs | 17 | `MaxRetries` is hardcoded as `3`. | Move to configuration or a named constant. |
| SampleBankingApp/Services/EmailService.cs | 18 | `SmtpTimeoutMs` is hardcoded as `5000`. | Move to configuration or a named constant. |
| SampleBankingApp/Services/EmailService.cs | 23 | `25` is hardcoded as a default SMTP port. | Move to configuration or a named constant. |
| SampleBankingApp/Services/EmailService.cs | 40 | `"notifications@company.com"` is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/EmailService.cs | 58 | `"notifications@company.com"` is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/EmailService.cs | 72 | `"notifications@company.com"` is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/EmailService.cs | 72 | `"support@company.com"` is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/AuthService.cs | 17 | `AdminBypassPassword` is hardcoded. | Remove the hardcoded password. |
| SampleBankingApp/Services/AuthService.cs | 62 | `"Jwt:SecretKey"` is hardcoded as a config key. | Move to configuration or a named constant. |
| SampleBankingApp/Services/AuthService.cs | 62 | `"Jwt:Issuer"` is hardcoded as a config key. | Move to configuration or a named constant. |
| SampleBankingApp/Services/AuthService.cs | 62 | `"Jwt:Audience"` is hardcoded as a config key. | Move to configuration or a named constant. |
| SampleBankingApp/Services/AuthService.cs | 62 | `30` days is hardcoded for token expiration. | Move to configuration or a named constant. |
| SampleBankingApp/Services/AuthService.cs | 33 | `"Users"` table name is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 45 | `"Users"` table name is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 48 | `"Users"` table name is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 72 | `"Transactions"` table name is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/UserService.cs | 32 | `"Users"` table name is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/UserService.cs | 50 | `"Users"` table name is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/UserService.cs | 64 | `"Users"` table name is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/UserService.cs | 80 | `"Users"` table name is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/UserService.cs | 104 | `"Users"` table name is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | `"Users"` table name is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | `"Tables"` schema name is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | `"BASE TABLE"` table type is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | `254` is hardcoded as a max email length. | Move to configuration or a named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 19 | `3` and `20` are hardcoded as min/max username lengths. | Move to configuration or a named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 36 | `4` is hardcoded as a min account number length. | Move to configuration or a named constant. |
| SampleBankingApp/Program.cs | 28 | `false` is hardcoded for `ValidateLifetime`. | Move to configuration or a named constant. |
| SampleBankingApp/Program.cs | 36 | `UseDeveloperExceptionPage()` is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Program.cs | 40 | `AllowAnyOrigin()` is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Program.cs | 40 | `AllowAnyMethod()` is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Program.cs | 40 | `AllowAnyHeader()` is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/appsettings.json | 1 | `"DefaultConnection"` is hardcoded as a connection string key. | Move to configuration or a named constant. |
| SampleBankingApp/appsettings.json | 5 | `"Jwt:SecretKey"` is hardcoded as a config key. | Move to configuration or a named constant. |
| SampleBankingApp/appsettings.json | 5 | `"Jwt:Issuer"` is hardcoded as a config key. | Move to configuration or a named constant. |
| SampleBankingApp/appsettings.json | 5 | `"Jwt:Audience"` is hardcoded as a config key. | Move to configuration or a named constant. |
| SampleBankingApp/appsettings.json | 9 | `"Email:SmtpHost"` is hardcoded as a config key. | Move to configuration or a named constant. |
| SampleBankingApp/appsettings.json | 9 | `"Email:SmtpPort"` is hardcoded as a config key. | Move to configuration or a named constant. |
| SampleBankingApp/appsettings.json | 9 | `"Email:Username"` is hardcoded as a config key. | Move to configuration or a named constant. |
| SampleBankingApp/appsettings.json | 9 | `"Email:Password"` is hardcoded as a config key. | Move to configuration or a named constant. |
| SampleBankingApp/appsettings.json | 13 | `"Default"` is hardcoded as a log level key. | Move to configuration or a named constant. |
| SampleBankingApp/appsettings.json | 13 | `"Microsoft"` is hardcoded as a log level key. | Move to configuration or a named constant. |
| SampleBankingApp/appsettings.json | 13 | `"System"` is hardcoded as a log level key. | Move to configuration or a named constant. |
| SampleBankingApp/appsettings.json | 17 | `"*"` is hardcoded as `AllowedHosts`. | Move to configuration or a named constant. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 26 | String concatenation in a loop (`result += item + separator`) is O(n²). | Use `string.Join` or `StringBuilder`. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | `new Regex(...)` is created inside a method called repeatedly. | Make the regex `static readonly`. |
| SampleBankingApp/Helpers/StringHelper.cs | 19 | `new Regex(...)` is created inside a method called repeatedly. | Make the regex `static readonly`. |
| SampleBankingApp/Services/UserService.cs | 14 | `_auditLog` is a static mutable list accessed from multiple threads without synchronization. | Use `ConcurrentBag` or lock the list. |
| SampleBankingApp/Services/UserService.cs | 15 | `_requestCount` is a static mutable int accessed from multiple threads without synchronization. | Use `Interlocked.Increment` or a lock. |
| SampleBankingApp/Services/UserService.cs | 104 | `SearchUsers` reimplements validation logic that should be extracted. | Extract validation logic to a shared method. |
| SampleBankingApp/Services/UserService.cs | 112 | `MapRowToUser` reimplements mapping logic that should be extracted. | Extract mapping logic to a shared method. |
| SampleBankingApp/Services/TransactionService.cs | 62 | `RecordTransaction` is called after DB updates, risking inconsistent state if email fails. | Ensure atomicity or handle email failure without rolling back DB. |
| SampleBankingApp/Services/TransactionService.cs | 72 | `RecordTransaction` does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/TransactionService.cs | 86 | `IsWithinDailyLimit` does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/TransactionService.cs | 92 | `FormatCurrency` is never called. | Remove the unused method. |
| SampleBankingApp/Services/TransactionService.cs | 96 | `RefundTransaction` throws `NotImplementedException`. | Implement the method or remove it. |
| SampleBankingApp/Services/EmailService.cs | 68 | `BuildHtmlTemplate` is never called. | Remove the unused method. |
| SampleBankingApp/Services/EmailService.cs | 72 | `SendWelcomeEmailHtml` is never called. | Remove the unused method. |
| SampleBankingApp/Services/AuthService.cs | 86 | `ValidateToken` method returns `true` immediately, making the rest of the method unreachable. | Remove the early return or implement the validation logic correctly. |
| SampleBankingApp/Services/AuthService.cs | 86 | `ValidateToken` method has unreachable code after `return true`. | Remove the unreachable code. |
| SampleBankingApp/Services/AuthService.cs | 54 | `HashPasswordSha1` method is never called. | Remove the unused method. |
| SampleBankingApp/Data/DatabaseHelper.cs | 60 | `ExecuteQueryWithParams` method is marked `[Obsolete]` but still present. | Remove the obsolete method. |
| SampleBankingApp/Controllers/TransactionController.cs | 48 | `Refund` method catches `NotImplementedException` and returns 500, but the method always throws. | Remove the try-catch and let the exception propagate or implement the method. |
| SampleBankingApp/Controllers/UserController.cs | 52 | Catch block returns `ex.Message` directly to client, potentially leaking stack traces. | Log the full exception and return a generic error message to the client. |
| SampleBankingApp/Controllers/UserController.cs | 60 | Catch block returns generic "An error occurred" without logging the specific exception details. | Log the exception details before returning the generic message. |
| SampleBankingApp/Controllers/UserController.cs | 64 | Missing authorization check on `GetAuditLog` endpoint exposes internal logs. | Add `[Authorize(Roles = "Admin")]` or similar restriction. |
| SampleBankingApp/Controllers/UserController.cs | 46 | Missing authorization check on `UpdateUser` allows any authenticated user to modify others. | Verify that the `id` in the URL matches the authenticated user's ID or enforce admin role. |
| SampleBankingApp/Controllers/UserController.cs | 58 | Missing authorization check on `DeleteUser` allows any authenticated user to delete others. | Verify ownership or enforce admin role before deletion. |
| SampleBankingApp/Controllers/TransactionController.cs | 22 | `int.Parse` on `userIdClaim` throws if claim is missing or invalid, causing 500 error. | Add null check and validation before parsing. |
| SampleBankingApp/Controllers/TransactionController.cs | 35 | `int.Parse` on `userIdClaim` throws if claim is missing or invalid, causing 500 error. | Add null check and validation before parsing. |
| SampleBankingApp/Services/AuthService.cs | 33 | `Login` method opens a connection but does not dispose it if an exception occurs. | Use `using` statements for `SqlConnection` and `SqlCommand`. |
| SampleBankingApp/Services/AuthService.cs | 33 | `Login` method does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/AuthService.cs | 86 | `ValidateToken` method returns `true` immediately, ignoring the actual token validation logic below. | Remove the early return or implement the validation logic correctly. |
| SampleBankingApp/Services/TransactionService.cs | 72 | `RecordTransaction` does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/TransactionService.cs | 86 | `IsWithinDailyLimit` does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/UserService.cs | 32 | `GetUserById` does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/UserService.cs | 50 | `UpdateUser` does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/UserService.cs | 64 | `DeleteUser` does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/UserService.cs | 80 | `GetUsersPage` does not handle exceptions during SQL execution. | Wrap SQL execution in a try-catch block. |
| SampleBankingApp/Services/UserService.cs | 104 | `SearchUsers` catches all exceptions and returns an empty list, hiding failures. | Log the exception and rethrow or return a specific error code. |
| SampleBankingApp/Services/UserService.cs | 112 | `MapRowToUser` does not handle exceptions during casting. | Add null checks and handle `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 113 | `MapRowToUser` does not handle exceptions during casting. | Add null checks and handle `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 114 | `MapRowToUser` does not handle exceptions during casting. | Add null checks and handle `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 115 | `MapRowToUser` does not handle exceptions during casting. | Add null checks and handle `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 116 | `MapRowToUser` does not handle exceptions during casting. | Add null checks and handle `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 117 | `MapRowToUser` does not handle exceptions during casting. | Add null checks and handle `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 118 | `MapRowToUser` does not handle exceptions during casting. | Add null checks and handle `DBNull.Value` before casting. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 28 | `UseDeveloperExceptionPage()` is enabled, exposing stack traces in production. | Wrap in `if (app.Environment.IsDevelopment())` or remove for production. |
| SampleBankingApp/Program.cs | 36 | `UseHttpsRedirection()` is commented out, disabling HTTPS. | Enable HTTPS redirection. |
| SampleBankingApp/Program.cs | 40 | CORS policy allows any origin and method, exposing the API to CSRF and data theft. | Restrict CORS to specific trusted origins and methods. |
| SampleBankingApp/Program.cs | 28 | `ValidateLifetime` is set to `false`, allowing expired tokens to be accepted. | Set `ValidateLifetime` to `true` to enforce token expiration. |
| SampleBankingApp/appsettings.json | 1 | Hardcoded database credentials in `DefaultConnection`. | Move secrets to environment variables or a secure secret manager. |
| SampleBankingApp/appsettings.json | 5 | Hardcoded JWT secret key. | Move secrets to environment variables or a secure secret manager. |
| SampleBankingApp/appsettings.json | 9 | Hardcoded SMTP credentials. | Move secrets to environment variables or a secure secret manager. |
| SampleBankingApp/appsettings.json | 13 | Debug log level set for production namespaces. | Set log level to `Information` or `Warning` for production. |
| SampleBankingApp/appsettings.json | 17 | `AllowedHosts` is set to `"*"`, allowing any host. | Restrict `AllowedHosts` to specific domains. |
| SampleBankingApp/SampleBankingApp.csproj | 10 | `TreatWarningsAsErrors` is set to `false`, allowing warnings to be ignored. | Set `TreatWarningsAsErrors` to `true`. |
| SampleBankingApp/SampleBankingApp.csproj | 11 | `DebugSymbols` is set to `true`, exposing debug symbols in release builds. | Set `DebugSymbols` to `false` for release builds. |
| SampleBankingApp/SampleBankingApp.csproj | 12 | `DebugType` is set to `full`, exposing debug info in release builds. | Set `DebugType` to `none` for release builds. |
| SampleBankingApp/SampleBankingApp.csproj | 16 | `Newtonsoft.Json` version `12.0.3` is outdated and may have vulnerabilities. | Update to the latest version. |
| SampleBankingApp/SampleBankingApp.csproj | 17 | `System.IdentityModel.Tokens.Jwt` version `7.0.0` is outdated and may have vulnerabilities. | Update to the latest version. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | `System.Data.SqlClient` version `4.8.6` is outdated and may have vulnerabilities. | Update to the latest version. |
| SampleBankingApp/SampleBankingApp.csproj | 14 | `Microsoft.AspNetCore.Authentication.JwtBearer` version `8.0.0` is outdated and may have vulnerabilities. | Update to the latest version. |
| SampleBankingApp/Program.cs | 28 | `ValidateLifetime` is set to `false`, allowing expired tokens to be accepted. | Set `ValidateLifetime` to `true` to enforce token expiration. |
| SampleBankingApp/Program.cs | 36 | `UseHttpsRedirection()` is commented out, disabling HTTPS. | Enable HTTPS redirection. |
| SampleBankingApp/Program.cs | 40 | CORS policy allows any origin and method, exposing the API to CSRF and data theft. | Restrict CORS to specific trusted origins and methods. |
| SampleBankingApp/Program.cs | 28 | `UseDeveloperExceptionPage()` is enabled, exposing stack traces in production. | Wrap in `if (app.Environment.IsDevelopment())` or remove for production. |
| SampleBankingApp/appsettings.json | 1 | Hardcoded database credentials in `DefaultConnection`. | Move secrets to environment variables or a secure secret manager. |
| SampleBankingApp/appsettings.json | 5 | Hardcoded JWT secret key. | Move secrets to environment variables or a secure secret manager. |
| SampleBankingApp/appsettings.json | 9 | Hardcoded SMTP credentials. | Move secrets to environment variables or a secure secret manager. |
| SampleBankingApp/appsettings.json | 13 | Debug log level set for production namespaces. | Set log level to `Information` or `Warning` for production. |
| SampleBankingApp/appsettings.json | 17 | `AllowedHosts` is set to `"*"`, allowing any host. | Restrict `AllowedHosts` to specific domains. |
| SampleBankingApp/SampleBankingApp.csproj | 10 | `TreatWarningsAsErrors` is set to `false`, allowing warnings to be ignored. | Set `TreatWarningsAsErrors` to `true`. |
| SampleBankingApp/SampleBankingApp.csproj | 11 | `DebugSymbols` is set to `true`, exposing debug symbols in release builds. | Set `DebugSymbols` to `false` for release builds. |
| SampleBankingApp/SampleBankingApp.csproj | 12 | `DebugType` is set to `full`, exposing debug info in release builds. | Set `DebugType` to `none` for release builds. |
| SampleBankingApp/SampleBankingApp.csproj | 16 | `Newtonsoft.Json` version `12.0.3` is outdated and may have vulnerabilities. | Update to the latest version. |
| SampleBankingApp/SampleBankingApp.csproj | 17 | `System.IdentityModel.Tokens.Jwt` version `7.0.0` is outdated and may have vulnerabilities. | Update to the latest version. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | `System.Data.SqlClient` version `4.8.6` is outdated and may have vulnerabilities. | Update to the latest version. |
| SampleBankingApp/SampleBankingApp.csproj | 14 | `Microsoft.AspNetCore.Authentication.JwtBearer` version `8.0.0` is outdated and may have vulnerabilities. | Update to the latest version. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 29 | No tests for the backdoor password logic. | Add unit tests to verify the backdoor is removed. |
| SampleBankingApp/Services/AuthService.cs | 33 | No tests for SQL injection vulnerability. | Add unit tests to verify parameterized queries are used. |
| SampleBankingApp/Services/AuthService.cs | 54 | No tests for MD5 hashing. | Add unit tests to verify secure hashing is used. |
| SampleBankingApp/Services/AuthService.cs | 86 | No tests for `ValidateToken` method. | Add unit tests to verify token validation logic. |
| SampleBankingApp/Services/TransactionService.cs | 58 | No tests for balance check logic. | Add unit tests to verify balance check includes fee. |
| SampleBankingApp/Services/TransactionService.cs | 62 | No tests for email sending after DB updates. | Add unit tests to verify email sending is handled correctly. |
| SampleBankingApp/Services/TransactionService.cs | 76 | No tests for deposit interest calculation. | Add unit tests to verify interest calculation. |
| SampleBankingApp/Services/TransactionService.cs | 86 | No tests for daily limit check. | Add unit tests to verify daily limit check is called. |
| SampleBankingApp/Services/UserService.cs | 80 | No tests for pagination logic. | Add unit tests to verify pagination logic. |
| SampleBankingApp/Services/UserService.cs | 104 | No tests for search logic. | Add unit tests to verify search logic. |
| SampleBankingApp/Services/UserService.cs | 112 | No tests for row mapping logic. | Add unit tests to verify row mapping logic. |
| SampleBankingApp/Services/EmailService.cs | 40 | No tests for email sending logic. | Add unit tests to verify email sending logic. |
| SampleBankingApp/Services/EmailService.cs | 58 | No tests for welcome email logic. | Add unit tests to verify welcome email logic. |
| SampleBankingApp/Services/EmailService.cs | 72 | No tests for HTML email logic. | Add unit tests to verify HTML email logic. |
| SampleBankingApp/Controllers/AuthController.cs | 22 | No tests for login logic. | Add unit tests to verify login logic. |
| SampleBankingApp/Controllers/TransactionController.cs | 22 | No tests for transfer logic. | Add unit tests to verify transfer logic. |
| SampleBankingApp/Controllers/TransactionController.cs | 35 | No tests for deposit logic. | Add unit tests to verify deposit logic. |
| SampleBankingApp/Controllers/TransactionController.cs | 48 | No tests for refund logic. | Add unit tests to verify refund logic. |
| SampleBankingApp/Controllers/UserController.cs | 22 | No tests for user retrieval logic. | Add unit tests to verify user retrieval logic. |
| SampleBankingApp/Controllers/UserController.cs | 46 | No tests for user update logic. | Add unit tests to verify user update logic. |
| SampleBankingApp/Controllers/UserController.cs | 58 | No tests for user deletion logic. | Add unit tests to verify user deletion logic. |
| SampleBankingApp/Controllers/UserController.cs | 64 | No tests for audit log logic. | Add unit tests to verify audit log logic. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | No tests for email validation logic. | Add unit tests to verify email validation logic. |
| SampleBankingApp/Helpers/StringHelper.cs | 19 | No tests for username validation logic. | Add unit tests to verify username validation logic. |
| SampleBankingApp/Helpers/StringHelper.cs | 26 | No tests for string joining logic. | Add unit tests to verify string joining logic. |
| SampleBankingApp/Helpers/StringHelper.cs | 36 | No tests for account masking logic. | Add unit tests to verify account masking logic. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | No tests for account obfuscation logic. | Add unit tests to verify account obfuscation logic. |
| SampleBankingApp/Helpers/StringHelper.cs | 51 | No tests for title case logic. | Add unit tests to verify title case logic. |
| SampleBankingApp/Helpers/StringHelper.cs | 58 | No tests for blank check logic. | Add unit tests to verify blank check logic. |
| SampleBankingApp/Data/DatabaseHelper.cs | 22 | No tests for database helper logic. | Add unit tests to verify database helper logic. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | No tests for query execution logic. | Add unit tests to verify query execution logic. |
| SampleBankingApp/Data/DatabaseHelper.cs | 42 | No tests for non-query execution logic. | Add unit tests to verify non-query execution logic. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | No tests for table existence logic. | Add unit tests to verify table existence logic. |
| SampleBankingApp/Data/DatabaseHelper.cs | 60 | No tests for parameterized query logic. | Add unit tests to verify parameterized query logic. |
| SampleBankingApp/Program.cs | 28 | No tests for JWT configuration. | Add unit tests to verify JWT configuration. |
| SampleBankingApp/Program.cs | 36 | No tests for HTTPS redirection. | Add unit tests to verify HTTPS redirection. |
| SampleBankingApp/Program.cs | 40 | No tests for CORS configuration. | Add unit tests to verify CORS configuration. |
| SampleBankingApp/appsettings.json | 1 | No tests for configuration loading. | Add unit tests to verify configuration loading. |
| SampleBankingApp/appsettings.json | 5 | No tests for JWT configuration. | Add unit tests to verify JWT configuration. |
| SampleBankingApp/appsettings.json | 9 | No tests for email configuration. | Add unit tests to verify email configuration. |
| SampleBankingApp/appsettings.json | 13 | No tests for logging configuration. | Add unit tests to verify logging configuration. |
| SampleBankingApp/appsettings.json | 17 | No tests for allowed hosts configuration. | Add unit tests to verify allowed hosts configuration. |
| SampleBankingApp/SampleBankingApp.csproj | 10 | No tests for warning as error configuration. | Add unit tests to verify warning as error configuration. |
| SampleBankingApp/SampleBankingApp.csproj | 11 | No tests for debug symbols configuration. | Add unit tests to verify debug symbols configuration. |
| SampleBankingApp/SampleBankingApp.csproj | 12 | No tests for debug type configuration. | Add unit tests to verify debug type configuration. |
| SampleBankingApp/SampleBankingApp.csproj | 16 | No tests for package version configuration. | Add unit tests to verify package version configuration. |
| SampleBankingApp/SampleBankingApp.csproj | 17 | No tests for package version configuration. | Add unit tests to verify package version configuration. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | No tests for package version configuration. | Add unit tests to verify package version configuration. |
| SampleBankingApp/SampleBankingApp.csproj | 14 | No tests for package version configuration. | Add unit tests to verify package version configuration. |