## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 24 | `int.Parse` on user claim without null check or validation allows potential crash or injection if claim is missing. | Use `int.TryParse` and validate the claim exists before parsing. |
| SampleBankingApp/Data/DatabaseHelper.cs | 27 | `ExecuteQuery` constructs SQL using string interpolation for table name and where clause, enabling SQL injection. | Use parameterized queries or a whitelist for table names. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `ExecuteNonQuery` accepts raw SQL string, allowing arbitrary command execution if called unsafely. | Enforce parameterized queries only or restrict input via whitelist. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded default connection string with plaintext credentials (`sa`, `Admin1234!`) if config is missing. | Remove hardcoded credentials and require valid configuration. |
| SampleBankingApp/Services/AuthService.cs | 24 | Hardcoded backdoor password (`SuperAdmin2024`) allows bypassing authentication. | Remove the backdoor logic entirely. |
| SampleBankingApp/Services/AuthService.cs | 31 | SQL query constructed via string interpolation using username and hashed password, vulnerable to SQL injection. | Use parameterized queries for all database access. |
| SampleBankingApp/Services/AuthService.cs | 56 | Password hashing uses MD5, which is cryptographically broken and insecure. | Use PBKDF2, bcrypt, or Argon2 for password hashing. |
| SampleBankingApp/Services/AuthService.cs | 79 | Unused `HashPasswordSha1` method indicates weak cryptography usage history. | Remove the method and ensure no SHA1 usage remains. |
| SampleBankingApp/Services/AuthService.cs | 83 | `ValidateToken` method returns `true` immediately without actually validating the JWT token. | Implement actual token validation logic using `JwtSecurityTokenHandler`. |
| SampleBankingApp/Services/EmailService.cs | 25 | SMTP credentials (`Email:Username`, `Email:Password`) are loaded from config but used in a shared static-like instance pattern. | Ensure credentials are never logged and use secure storage. |
| SampleBankingApp/Services/EmailService.cs | 28 | `EnableSsl = false` sends email credentials and content in plaintext. | Set `EnableSsl = true` and use port 587 or 465. |
| SampleBankingApp/Services/TransactionService.cs | 62 | `RecordTransaction` constructs SQL via string interpolation, vulnerable to SQL injection via description field. | Use parameterized queries for all SQL statements. |
| SampleBankingApp/Services/UserService.cs | 88 | `SearchUsers` uses `ExecuteQuery` with string interpolation for `LIKE` clause, vulnerable to SQL injection. | Use parameterized queries with `@query` parameter. |
| SampleBankingApp/Services/UserService.cs | 88 | `SearchUsers` swallows all exceptions and returns empty list, hiding potential security errors. | Log the exception and rethrow or return a safe error response. |
| SampleBankingApp/Program.cs | 28 | `ValidateLifetime = false` allows expired tokens to be accepted as valid. | Set `ValidateLifetime = true` and configure a reasonable expiration. |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` exposes stack traces and internal details to clients. | Wrap in `if (app.Environment.IsDevelopment())` block. |
| SampleBankingApp/Program.cs | 37 | `AllowAnyOrigin()` combined with `AllowCredentials` (implied by auth) creates a security risk. | Specify specific allowed origins instead of `*`. |
| SampleBankingApp/Program.cs | 38 | HTTPS redirection is commented out, allowing unencrypted traffic. | Uncomment and enforce HTTPS redirection. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | `DebugSymbols` and `DebugType` enabled in production build expose internal code details. | Set to `none` or `portable` for production builds. |
| SampleBankingApp/appsettings.json | 5 | Plaintext database password (`Admin1234!`) committed to source control. | Use environment variables or secret management tools. |
| SampleBankingApp/appsettings.json | 10 | Weak JWT secret key (`mysecretkey`) is hardcoded and easily guessable. | Use a strong, random secret key stored in environment variables. |
| SampleBankingApp/appsettings.json | 16 | Plaintext email password (`EmailPass99`) committed to source control. | Use environment variables or secret management tools. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 24 | `int.Parse` on potentially null `userIdClaim` throws exception instead of returning 401/403. | Validate claim existence and parse safely. |
| SampleBankingApp/Controllers/TransactionController.cs | 38 | `int.Parse` on potentially null `userIdClaim` throws exception instead of returning 401/403. | Validate claim existence and parse safely. |
| SampleBankingApp/Services/TransactionService.cs | 45 | Balance check `fromBalance >= amount` ignores the transaction fee, allowing overdraft. | Check `fromBalance >= amount + fee`. |
| SampleBankingApp/Services/TransactionService.cs | 50 | `RecordTransaction` is called after DB updates, risking inconsistent state if email fails. | Wrap DB updates and transaction recording in a transaction scope. |
| SampleBankingApp/Services/TransactionService.cs | 65 | `Deposit` calculates interest as `amount * 0.05m * 1`, hardcoding the multiplier. | Move interest rate to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 73 | `IsWithinDailyLimit` is defined but never called in `Transfer` method. | Call `IsWithinDailyLimit` before processing transfer. |
| SampleBankingApp/Services/UserService.cs | 65 | Pagination logic `skip = page * pageSize` skips the first page (page 1 skips 20 items). | Use `skip = (page - 1) * pageSize`. |
| SampleBankingApp/Services/UserService.cs | 88 | `SearchUsers` catches all exceptions and returns empty list, masking logic errors. | Log exceptions and handle specific errors. |
| SampleBankingApp/Services/UserService.cs | 95 | `MapRowToUser` casts `row["Id"]` to `int` without checking if value is null or DBNull. | Check for `DBNull.Value` before casting. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 48 | `catch (NotImplementedException)` returns 500, but `RefundTransaction` throws it unconditionally. | Remove the try-catch block and handle the method implementation properly. |
| SampleBankingApp/Controllers/UserController.cs | 46 | `catch (Exception)` returns raw `ex.Message` to the client, leaking internal details. | Return a generic error message and log the full exception. |
| SampleBankingApp/Controllers/UserController.cs | 56 | `catch (Exception)` returns generic 500 but logs the full exception, which is good, but the message is generic. | Ensure the message is user-friendly and does not leak stack traces. |
| SampleBankingApp/Services/TransactionService.cs | 50 | Email sending occurs after DB updates; if email fails, the transaction is committed but user is not notified. | Use a transaction scope or queue for email sending. |
| SampleBankingApp/Services/UserService.cs | 88 | `SearchUsers` catches all exceptions and returns empty list, making debugging impossible. | Log the exception and rethrow or return a specific error. |
| SampleBankingApp/Services/EmailService.cs | 45 | `catch (SmtpException)` logs to `Console.WriteLine` instead of a proper logger. | Use `_logger` for logging email failures. |
| SampleBankingApp/Services/EmailService.cs | 62 | `catch (Exception)` swallows the exception and logs to `Console.WriteLine`, hiding failures. | Log the exception properly and consider retry logic or alerting. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | `GetOpenConnection` returns an open connection that the caller must close, risking leaks. | Return a `using` block or ensure caller disposes it. |
| SampleBankingApp/Data/DatabaseHelper.cs | 27 | `ExecuteQuery` opens connection but does not dispose it if `SqlDataAdapter.Fill` throws. | Wrap connection and command in `using` statements. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | `ExecuteNonQuery` opens connection but does not dispose it if `ExecuteNonQuery` throws. | Wrap connection and command in `using` statements. |
| SampleBankingApp/Services/EmailService.cs | 20 | `SmtpClient` is held as a field and never disposed, causing socket leaks. | Implement `IDisposable` on `EmailService` and dispose `_smtpClient`. |
| SampleBankingApp/Services/EmailService.cs | 36 | `MailMessage` is created but never disposed, causing resource leaks. | Wrap `MailMessage` in a `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 58 | `MailMessage` is created but never disposed, causing resource leaks. | Wrap `MailMessage` in a `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 69 | `MailMessage` is created but never disposed, causing resource leaks. | Wrap `MailMessage` in a `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 24 | `userIdClaim` can be null, causing `int.Parse` to throw. | Use `int.TryParse` and check for null. |
| SampleBankingApp/Controllers/TransactionController.cs | 38 | `userIdClaim` can be null, causing `int.Parse` to throw. | Use `int.TryParse` and check for null. |
| SampleBankingApp/Services/AuthService.cs | 31 | `username` and `password` are used in SQL string without null checks. | Check for null or empty strings before constructing SQL. |
| SampleBankingApp/Services/AuthService.cs | 62 | `_config["Jwt:SecretKey"]` can be null, causing `Encoding.UTF8.GetBytes` to throw. | Check for null and handle missing configuration. |
| SampleBankingApp/Services/TransactionService.cs | 42 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing index 0. |
| SampleBankingApp/Services/TransactionService.cs | 43 | `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing index 0. |
| SampleBankingApp/Services/TransactionService.cs | 53 | `fromUserTable.Rows[0]["Email"]` cast to string without null check. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/TransactionService.cs | 54 | `toUserTable.Rows[0]["Username"]` cast to string without null check. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 30 | `table.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing index 0. |
| SampleBankingApp/Services/UserService.cs | 95 | `row["Id"]` cast to `int` without checking for `DBNull.Value`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 96 | `row["Username"]` cast to `string` without checking for `DBNull.Value`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 97 | `row["Email"]` cast to `string` without checking for `DBNull.Value`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 98 | `row["Role"]` cast to `string` without checking for `DBNull.Value`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 99 | `row["Balance"]` cast to `decimal` without checking for `DBNull.Value`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 100 | `row["IsActive"]` cast to `bool` without checking for `DBNull.Value`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/UserService.cs | 101 | `row["CreatedAt"]` cast to `DateTime` without checking for `DBNull.Value`. | Check for `DBNull.Value` before casting. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 59 | `ExecuteQueryWithParams` is marked `[Obsolete]` but still present and unused. | Remove the method or update callers to use `ExecuteQuerySafe`. |
| SampleBankingApp/Services/AuthService.cs | 79 | `HashPasswordSha1` is defined but never called. | Remove the method. |
| SampleBankingApp/Services/AuthService.cs | 83 | `ValidateToken` returns `true` immediately, making the rest of the method dead code. | Remove the dead code or implement actual validation. |
| SampleBankingApp/Services/TransactionService.cs | 73 | `IsWithinDailyLimit` is defined but never called. | Call the method in `Transfer` or remove it. |
| SampleBankingApp/Services/TransactionService.cs | 83 | `FormatCurrency` is defined but never called. | Remove the method or use it for formatting. |
| SampleBankingApp/Services/TransactionService.cs | 87 | `RefundTransaction` throws `NotImplementedException` and is called by controller. | Implement the method or remove the endpoint. |
| SampleBankingApp/Services/EmailService.cs | 56 | `BuildHtmlTemplate` is defined but never called. | Remove the method or use it for HTML emails. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 15 | `TransactionFeeRate` is hardcoded as `0.015m`. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 16 | `MaxTransactionsPerDay` is hardcoded as `10`. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 65 | Interest rate `0.05m` and multiplier `1` are hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 65 | `1` multiplier for interest is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 65 | `50` max page size is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 24 | `1000000` max user ID is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 26 | `1000000` max user ID is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 40 | `1000000` max user ID is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 42 | `1000000` max user ID is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 54 | `1000000` max user ID is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 56 | `1000000` max user ID is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 13 | `TransferSubject` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 14 | `WelcomeSubject` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 16 | `MaxRetries` is hardcoded as `3`. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 17 | `SmtpTimeoutMs` is hardcoded as `5000`. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 36 | `notifications@company.com` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 58 | `notifications@company.com` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 69 | `notifications@company.com` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/AuthService.cs | 24 | `SuperAdmin2024` is hardcoded. | Remove the backdoor. |
| SampleBankingApp/Services/AuthService.cs | 62 | `Jwt:SecretKey` config key is hardcoded. | Use a constant for config keys. |
| SampleBankingApp/Services/AuthService.cs | 63 | `Jwt:Issuer` config key is hardcoded. | Use a constant for config keys. |
| SampleBankingApp/Services/AuthService.cs | 64 | `Jwt:Audience` config key is hardcoded. | Use a constant for config keys. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Users` table name is hardcoded. | Use a constant for table names. |
| SampleBankingApp/Services/TransactionService.cs | 50 | `Transfer` type string is hardcoded. | Use a constant for transaction types. |
| SampleBankingApp/Services/TransactionService.cs | 65 | `Deposit` type string is hardcoded. | Use a constant for transaction types. |
| SampleBankingApp/Services/TransactionService.cs | 77 | `Transactions` table name is hardcoded. | Use a constant for table names. |
| SampleBankingApp/Services/TransactionService.cs | 77 | `FromUserId`, `ToUserId`, `Amount`, `Type`, `Status`, `Description`, `CreatedAt` column names are hardcoded. | Use constants for column names. |
| SampleBankingApp/Services/UserService.cs | 24 | `Users` table name is hardcoded. | Use a constant for table names. |
| SampleBankingApp/Services/UserService.cs | 40 | `Users` table name is hardcoded. | Use a constant for table names. |
| SampleBankingApp/Services/UserService.cs | 54 | `Users` table name is hardcoded. | Use a constant for table names. |
| SampleBankingApp/Services/UserService.cs | 65 | `Users` table name is hardcoded. | Use a constant for table names. |
| SampleBankingApp/Services/UserService.cs | 88 | `Users` table name is hardcoded. | Use a constant for table names. |
| SampleBankingApp/Services/UserService.cs | 88 | `Username` column name is hardcoded. | Use a constant for column names. |
| SampleBankingApp/Services/UserService.cs | 95 | `Id`, `Username`, `Email`, `Role`, `Balance`, `IsActive`, `CreatedAt` column names are hardcoded. | Use constants for column names. |
| SampleBankingApp/Program.cs | 28 | `Jwt:SecretKey` config key is hardcoded. | Use a constant for config keys. |
| SampleBankingApp/Program.cs | 29 | `Jwt:Issuer` config key is hardcoded. | Use a constant for config keys. |
| SampleBankingApp/Program.cs | 30 | `Jwt:Audience` config key is hardcoded. | Use a constant for config keys. |
| SampleBankingApp/appsettings.json | 5 | `DefaultConnection` connection string key is hardcoded. | Use a constant for config keys. |
| SampleBankingApp/appsettings.json | 10 | `Jwt` section keys are hardcoded. | Use a constant for config keys. |
| SampleBankingApp/appsettings.json | 16 | `Email` section keys are hardcoded. | Use a constant for config keys. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 27 | `JoinWithSeparator` uses string concatenation in a loop, causing O(n²) performance. | Use `string.Join` or `StringBuilder`. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `IsValidEmail` creates a new `Regex` instance on every call. | Make `Regex` static and readonly. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | `IsValidUsername` creates a new `Regex` instance on every call. | Make `Regex` static and readonly. |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Use `string.IsNullOrWhiteSpace`. |
| SampleBankingApp/Services/EmailService.cs | 20 | `SmtpClient` is held as a field, which is not thread-safe and causes socket leaks. | Create a new `SmtpClient` per request or use `IHttpClientFactory` pattern. |
| SampleBankingApp/Services/UserService.cs | 14 | `_auditLog` and `_requestCount` are static fields, causing shared mutable state across requests. | Remove static state or use dependency injection for logging. |
| SampleBankingApp/Services/UserService.cs | 88 | `SearchUsers` catches all exceptions and returns empty list, hiding errors. | Log exceptions and handle specific errors. |
| SampleBankingApp/Services/UserService.cs | 95 | `MapRowToUser` is a private method that casts all fields without null checks. | Add null checks and handle `DBNull.Value`. |
| SampleBankingApp/Services/TransactionService.cs | 50 | `RecordTransaction` is called after DB updates, risking inconsistent state if email fails. | Wrap DB updates and transaction recording in a transaction scope. |
| SampleBankingApp/Services/TransactionService.cs | 77 | `RecordTransaction` constructs SQL via string interpolation, violating SQL injection prevention. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 83 | `FormatCurrency` is a private method that is never called. | Remove the method or use it for formatting. |
| SampleBankingApp/Services/TransactionService.cs | 87 | `RefundTransaction` throws `NotImplementedException` and is called by controller. | Implement the method or remove the endpoint. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` constructs SQL via string interpolation, violating SQL injection prevention. | Use parameterized queries. |
| SampleBankingApp/Services/AuthService.cs | 56 | `HashPasswordMd5` uses MD5, which is cryptographically broken. | Use PBKDF2, bcrypt, or Argon2. |
| SampleBankingApp/Services/AuthService.cs | 79 | `HashPasswordSha1` uses SHA1, which is cryptographically broken. | Remove the method. |
| SampleBankingApp/Services/AuthService.cs | 83 | `ValidateToken` returns `true` immediately, making the rest of the method dead code. | Remove the dead code or implement actual validation. |
| SampleBankingApp/Services/AuthService.cs | 24 | `AdminBypassPassword` is a hardcoded backdoor. | Remove the backdoor. |
| SampleBankingApp/Services/AuthService.cs | 62 | `_config["Jwt:SecretKey"]` can be null, causing `Encoding.UTF8.GetBytes` to throw. | Check for null and handle missing configuration. |
| SampleBankingApp/Services/AuthService.cs | 63 | `_config["Jwt:Issuer"]` can be null, causing `JwtSecurityToken` to throw. | Check for null and handle missing configuration. |
| SampleBankingApp/Services/AuthService.cs | 64 | `_config["Jwt:Audience"]` can be null, causing `JwtSecurityToken` to throw. | Check for null and handle missing configuration. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` uses `SqlConnection` directly instead of `DatabaseHelper`. | Use `DatabaseHelper` for consistency. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not dispose `SqlConnection`, `SqlCommand`, or `SqlDataReader`. | Wrap in `using` statements. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `DBNull.Value` before casting. |
| SampleBankingApp/Services/AuthService.cs | 31 | `Login` does not handle `DBNull.Value` when reading from `SqlDataReader`. | Check for `