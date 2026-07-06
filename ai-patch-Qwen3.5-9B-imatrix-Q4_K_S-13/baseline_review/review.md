## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 38 | SQL injection via string interpolation in `Login` query. | Use parameterized queries (`@username`, `@password`). |
| SampleBankingApp/Services/AuthService.cs | 38 | Passwords stored/hashed using MD5, which is cryptographically broken. | Use bcrypt, PBKDF2, or Argon2. |
| SampleBankingApp/Services/AuthService.cs | 52 | Hardcoded admin bypass password allows authentication without DB check. | Remove backdoor; enforce standard auth flow. |
| SampleBankingApp/Services/TransactionService.cs | 42 | SQL injection in `Transfer` via string interpolation for `UPDATE` statements. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 68 | SQL injection in `Deposit` via string interpolation for `UPDATE` statement. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 92 | SQL injection in `RecordTransaction` via string interpolation for `INSERT`. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 43 | SQL injection in `UpdateUser` via string interpolation for `UPDATE`. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 55 | SQL injection in `DeleteUser` via string interpolation for `DELETE`. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 88 | SQL injection in `SearchUsers` via string interpolation in `LIKE` clause. | Use parameterized queries. |
| SampleBankingApp/Controllers/UserController.cs | 33 | Broken Access Control: `GetUser` allows any authenticated user to view any user's data. | Add authorization check to ensure user owns the resource or is admin. |
| SampleBankingApp/Controllers/UserController.cs | 47 | Broken Access Control: `UpdateUser` allows any authenticated user to update any user's data. | Add authorization check to ensure user owns the resource or is admin. |
| SampleBankingApp/Controllers/UserController.cs | 61 | Broken Access Control: `DeleteUser` allows any authenticated user to delete any user. | Add authorization check to ensure user owns the resource or is admin. |
| SampleBankingApp/Program.cs | 33 | JWT `ValidateLifetime` is set to `false`, allowing tokens to never expire. | Set `ValidateLifetime` to `true`. |
| SampleBankingApp/Program.cs | 43 | `UseDeveloperExceptionPage()` is enabled, exposing stack traces in production. | Wrap in `if (app.Environment.IsDevelopment())`. |
| SampleBankingApp/Program.cs | 46 | CORS policy allows any origin, method, and header, increasing attack surface. | Restrict to specific trusted origins and methods. |
| SampleBankingApp/appsettings.json | 2 | Production database credentials (sa/Admin1234!) are hardcoded in source control. | Use environment variables or a secrets manager. |
| SampleBankingApp/appsettings.json | 11 | JWT secret key is weak and hardcoded in source control. | Use a strong, random secret stored in environment variables. |
| SampleBankingApp/appsettings.json | 15 | SMTP credentials are hardcoded in source control. | Use environment variables or a secrets manager. |
| SampleBankingApp/Data/DatabaseHelper.cs | 18 | Fallback connection string contains hardcoded credentials if config is missing. | Remove fallback or use secure environment variables. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 40 | Balance check `fromBalance >= amount` ignores the transaction fee, allowing negative balances. | Check `fromBalance >= amount + fee`. |
| SampleBankingApp/Services/UserService.cs | 75 | Pagination offset calculation `page * pageSize` is incorrect for 1-based indexing. | Use `(page - 1) * pageSize`. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit interest calculation `amount * 0.05m * 1` is redundant and potentially misleading. | Clarify intent or remove redundant multiplication. |
| SampleBankingApp/Services/AuthService.cs | 52 | Admin bypass returns a user with `Id = 0`, which may cause issues in downstream services expecting valid IDs. | Return a valid admin user from the database or handle ID=0 explicitly. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/UserService.cs | 95 | `SearchUsers` catches `Exception` and returns an empty list, hiding errors from callers. | Log the exception and rethrow or return a specific error result. |
| SampleBankingApp/Controllers/UserController.cs | 53 | `UpdateUser` returns raw `ex.Message` to the client, leaking internal details. | Return a generic error message and log the exception. |
| SampleBankingApp/Controllers/UserController.cs | 57 | `UpdateUser` catches broad `Exception` and returns `ex.Message` in 500 response. | Return a generic error message and log the exception. |
| SampleBankingApp/Services/EmailService.cs | 58 | `SendWelcomeEmail` catches `Exception` and only writes to console, failing silently. | Log the error properly and consider rethrowing or notifying admin. |
| SampleBankingApp/Services/TransactionService.cs | 42 | `Transfer` performs multiple DB writes without a transaction, risking partial updates. | Wrap DB operations in a transaction. |
| SampleBankingApp/Services/TransactionService.cs | 68 | `Deposit` performs DB write without a transaction. | Wrap DB operations in a transaction. |
| SampleBankingApp/Services/AuthService.cs | 38 | `Login` opens a connection but does not dispose it if an exception occurs after `Open()`. | Use `using` statement for `SqlConnection` and `SqlCommand`. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 38 | `SqlConnection` and `SqlCommand` are not disposed in `Login`. | Use `using` statements for `SqlConnection`, `SqlCommand`, and `SqlDataReader`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 22 | `GetOpenConnection` returns an open connection, shifting disposal responsibility to caller. | Document disposal requirement or change API to accept action. |
| SampleBankingApp/Data/DatabaseHelper.cs | 30 | `ExecuteQuery` opens a connection but does not dispose it or the command. | Use `using` statements for `SqlConnection` and `SqlCommand`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 48 | `ExecuteNonQuery` opens a connection but does not dispose the command. | Use `using` statements for `SqlConnection` and `SqlCommand`. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` is held as an instance field, which is not thread-safe and may leak sockets. | Create `SmtpClient` per request or use a thread-safe wrapper. |
| SampleBankingApp/Services/EmailService.cs | 38 | `MailMessage` is not disposed after sending. | Use `using` statement for `MailMessage`. |
| SampleBankingApp/Services/EmailService.cs | 55 | `MailMessage` is not disposed after sending. | Use `using` statement for `MailMessage`. |
| SampleBankingApp/Services/EmailService.cs | 72 | `MailMessage` is not disposed after sending. | Use `using` statement for `MailMessage`. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 22 | `int.Parse(userIdClaim!)` will throw if `userIdClaim` is null. | Add null check before parsing. |
| SampleBankingApp/Controllers/TransactionController.cs | 35 | `int.Parse(userIdClaim!)` will throw if `userIdClaim` is null. | Add null check before parsing. |
| SampleBankingApp/Services/TransactionService.cs | 35 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/TransactionService.cs | 36 | `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/UserService.cs | 35 | `table.Rows[0]` accessed without checking `Rows.Count > 0` in `GetUserById`. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/UserService.cs | 85 | `table.Rows[0]` accessed without checking `Rows.Count > 0` in `IsWithinDailyLimit`. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Program.cs | 23 | `jwtSecret` could be null, causing `GetBytes` to throw. | Add null check or use `??` with a secure default. |
| SampleBankingApp/Services/AuthService.cs | 68 | `_config["Jwt:SecretKey"]!` could be null, causing `GetBytes` to throw. | Add null check. |
| SampleBankingApp/Services/EmailService.cs | 24 | `_config["Email:SmtpHost"]` could be null, causing `SmtpClient` constructor to throw. | Add null check. |
| SampleBankingApp/Services/EmailService.cs | 26 | `_config["Email:SmtpPort"]` could be null, causing `int.Parse` to throw. | Add null check or use `int.TryParse`. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 78 | `HashPasswordSha1` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/AuthService.cs | 85 | `ValidateToken` has unreachable code after `return true`. | Remove unreachable code or fix logic. |
| SampleBankingApp/Helpers/StringHelper.cs | 28 | `JoinWithSeparator` is inefficient and likely unused if `JoinWithSeparatorFixed` exists. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 34 | `JoinWithSeparatorFixed` duplicates `string.Join` and may be unused. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 40 | `MaskAccountNumber` and `ObfuscateAccount` are similar; one may be unused. | Remove unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 50 | `ToTitleCase` may be unused. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 55 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove if unused. |
| SampleBankingApp/Data/DatabaseHelper.cs | 58 | `ExecuteQueryWithParams` is marked `[Obsolete]` but still present. | Remove if no longer used. |
| SampleBankingApp/Services/TransactionService.cs | 98 | `FormatCurrency` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/EmailService.cs | 65 | `BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml`, which may be unused. | Remove if unused. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 10 | `TransactionFeeRate` (0.015m) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 11 | `MaxTransactionsPerDay` (10) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit limit (1000000) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Interest rate (0.05m) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 73 | Page size limit (50) is hardcoded. | Move to configuration. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | Email length limit (254) is hardcoded. | Move to configuration or constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | Username length limits (3, 20) are hardcoded. | Move to configuration or constant. |
| SampleBankingApp/Services/AuthService.cs | 15 | Admin bypass password is hardcoded. | Remove backdoor. |
| SampleBankingApp/Services/EmailService.cs | 10 | Email subjects are hardcoded. | Move to configuration or resource file. |
| SampleBankingApp/Services/EmailService.cs | 13 | `MaxRetries` (3) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 14 | `SmtpTimeoutMs` (5000) is hardcoded. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 28 | String concatenation in loop in `JoinWithSeparator` is O(n²). | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | `new Regex(...)` created on every call in `IsValidEmail`. | Use `static readonly Regex`. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | `new Regex(...)` created on every call in `IsValidUsername`. | Use `static readonly Regex`. |
| SampleBankingApp/Services/UserService.cs | 10 | `_auditLog` is a static mutable list, causing thread-safety issues. | Use a thread-safe collection or database logging. |
| SampleBankingApp/Services/UserService.cs | 11 | `_requestCount` is a static mutable int, causing thread-safety issues. | Use `Interlocked` or remove if unnecessary. |
| SampleBankingApp/Services/UserService.cs | 82 | String concatenation in loop in `GetAuditReport` is O(n²). | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` is not thread-safe and is used as a singleton. | Create per-request or use a thread-safe wrapper. |
| SampleBankingApp/Program.cs | 10 | `DatabaseHelper` is registered as `Singleton`, but it opens connections per call. | Ensure thread-safety or register as `Scoped`. |
| SampleBankingApp/Services/AuthService.cs | 38 | Raw ADO.NET used instead of ORM, increasing boilerplate and error risk. | Consider using Entity Framework or Dapper. |
| SampleBankingApp/Services/TransactionService.cs | 42 | SQL injection via string interpolation is a severe anti-pattern. | Use parameterized queries. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 43 | `UseDeveloperExceptionPage()` is enabled unconditionally. | Wrap in `if (app.Environment.IsDevelopment())`. |
| SampleBankingApp/Program.cs | 33 | JWT `ValidateLifetime` is `false`. | Set to `true`. |
| SampleBankingApp/Program.cs | 45 | HTTPS redirection is commented out. | Uncomment `app.UseHttpsRedirection()`. |
| SampleBankingApp/Program.cs | 46 | CORS policy is overly permissive. | Restrict origins, methods, and headers. |
| SampleBankingApp/appsettings.json | 18 | Logging level is set to `Debug` for all namespaces. | Set to `Information` or `Warning` for production. |
| SampleBankingApp/SampleBankingApp.csproj | 12 | `Newtonsoft.Json` version 12.0.3 is outdated and vulnerable. | Update to latest version. |
| SampleBankingApp/SampleBankingApp.csproj | 11 | `System.Data.SqlClient` is outdated; use `Microsoft.Data.SqlClient`. | Update package. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `TreatWarningsAsErrors` is `false`. | Set to `true` to enforce code quality. |
| SampleBankingApp/SampleBankingApp.csproj | 9 | `DebugSymbols` and `DebugType` are set for release builds. | Remove or conditionally set for debug only. |
| SampleBankingApp/appsettings.json | 2 | Production secrets are in `appsettings.json`. | Use environment variables or secrets manager. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create a test project with xUnit/NUnit. |
| SampleBankingApp/Services/TransactionService.cs | 25 | `Transfer` logic needs tests for balance checks, fees, and SQL injection prevention. | Add unit tests mocking DB calls. |
| SampleBankingApp/Services/TransactionService.cs | 65 | `Deposit` logic needs tests for limits and interest calculation. | Add unit tests mocking DB calls. |
| SampleBankingApp/Services/AuthService.cs | 25 | `Login` needs tests for SQL injection prevention and password hashing. | Add unit tests mocking DB calls. |
| SampleBankingApp/Services/UserService.cs | 70 | `GetUsersPage` needs tests for pagination logic. | Add unit tests mocking DB calls. |
| SampleBankingApp/Services/UserService.cs | 88 | `SearchUsers` needs tests for SQL injection prevention. | Add unit tests mocking DB calls. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | `IsValidEmail` and `IsValidUsername` need tests for regex patterns. | Add unit tests. |
| SampleBankingApp/Helpers/StringHelper.cs | 28 | `JoinWithSeparator` needs tests for performance and correctness. | Add unit tests. |
| SampleBankingApp/Controllers/AuthController.cs | 15 | `Login` endpoint needs integration tests for auth flow. | Add integration tests. |
| SampleBankingApp/Controllers/TransactionController.cs | 20 | `Transfer` endpoint needs integration tests for authorization and validation. | Add integration tests. |