## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 38 | SQL injection via string interpolation in `Login` query. | Use parameterized queries or an ORM. |
| SampleBankingApp/Services/AuthService.cs | 56 | Hardcoded admin backdoor password allows bypassing authentication. | Remove the hardcoded bypass logic entirely. |
| SampleBankingApp/Services/AuthService.cs | 66 | MD5 is cryptographically broken and unsuitable for password hashing. | Use a modern hashing algorithm like PBKDF2, BCrypt, or Argon2. |
| SampleBankingApp/Services/TransactionService.cs | 43 | SQL injection in `Transfer` via string interpolation in `ExecuteNonQuery`. | Use parameterized queries for all database writes. |
| SampleBankingApp/Services/TransactionService.cs | 63 | SQL injection in `Deposit` via string interpolation in `ExecuteNonQuery`. | Use parameterized queries for all database writes. |
| SampleBankingApp/Services/TransactionService.cs | 85 | SQL injection in `RecordTransaction` via string interpolation. | Use parameterized queries for all database writes. |
| SampleBankingApp/Services/UserService.cs | 38 | SQL injection in `UpdateUser` via string interpolation. | Use parameterized queries for all database writes. |
| SampleBankingApp/Services/UserService.cs | 52 | SQL injection in `DeleteUser` via string interpolation. | Use parameterized queries for all database writes. |
| SampleBankingApp/Services/UserService.cs | 88 | SQL injection in `SearchUsers` via string interpolation in `ExecuteQuery`. | Use parameterized queries or safe LIKE clause handling. |
| SampleBankingApp/Data/DatabaseHelper.cs | 14 | Hardcoded fallback connection string with credentials in source code. | Remove hardcoded credentials; fail securely if config is missing. |
| SampleBankingApp/appsettings.json | 2 | Production database credentials committed to source control. | Use environment variables or a secrets manager for credentials. |
| SampleBankingApp/appsettings.json | 13 | Weak JWT secret key ("mysecretkey") committed to source control. | Use a strong, randomly generated secret stored in secure configuration. |
| SampleBankingApp/appsettings.json | 17 | SMTP password committed to source control. | Use environment variables or a secrets manager for credentials. |
| SampleBankingApp/Controllers/TransactionController.cs | 28 | Missing ownership check; any authenticated user can transfer from any account. | Verify `fromUserId` matches the authenticated user's ID. |
| SampleBankingApp/Controllers/UserController.cs | 38 | Missing ownership check; any authenticated user can update any user. | Verify the authenticated user has permission to update the target ID. |
| SampleBankingApp/Controllers/UserController.cs | 52 | Missing ownership check; any authenticated user can delete any user. | Verify the authenticated user has permission to delete the target ID. |
| SampleBankingApp/Program.cs | 38 | `ValidateLifetime = false` disables JWT expiration validation. | Set `ValidateLifetime = true` to enforce token expiration. |
| SampleBankingApp/Program.cs | 46 | `UseDeveloperExceptionPage()` exposes stack traces in production. | Use conditional middleware for development vs. production environments. |
| SampleBankingApp/Program.cs | 50 | Overly permissive CORS policy allows any origin, method, and header. | Restrict CORS to specific trusted origins and methods. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 40 | Balance check uses `amount` but deducts `amount + fee`, allowing negative balances. | Check if `fromBalance >= totalDebit` (amount + fee). |
| SampleBankingApp/Services/TransactionService.cs | 40 | No check prevents a user from transferring funds to themselves. | Add a check to ensure `fromUserId != toUserId`. |
| SampleBankingApp/Services/UserService.cs | 75 | Pagination offset calculation `page * pageSize` is incorrect for 1-based indexing. | Use `(page - 1) * pageSize` for correct offset. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit interest calculation `amount * 0.05m * 1` is redundant and potentially misleading. | Clarify intent or remove the redundant multiplication. |
| SampleBankingApp/Services/AuthService.cs | 95 | `ValidateToken` returns `true` immediately without validating the token. | Remove the early return and implement actual validation logic. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/UserService.cs | 90 | `SearchUsers` catches `Exception` and returns an empty list, hiding errors. | Log the exception and return an error response or rethrow. |
| SampleBankingApp/Services/EmailService.cs | 63 | `SendWelcomeEmail` catches `Exception` and logs to console, swallowing errors. | Log via `ILogger` and consider propagating the error if critical. |
| SampleBankingApp/Controllers/UserController.cs | 42 | `UpdateUser` returns raw `ex.Message` to the client, leaking internal details. | Return a generic error message and log the exception details. |
| SampleBankingApp/Controllers/UserController.cs | 46 | `UpdateUser` catches broad `Exception` and returns raw message. | Return a generic error message and log the exception details. |
| SampleBankingApp/Services/TransactionService.cs | 43 | Database writes in `Transfer` are not atomic; failure after debit leaves inconsistent state. | Wrap database operations in a transaction. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Database writes in `Deposit` are not atomic. | Wrap database operations in a transaction. |
| SampleBankingApp/Services/TransactionService.cs | 85 | `RecordTransaction` is not part of the same transaction as balance updates. | Include transaction recording in the same database transaction. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 22 | `GetOpenConnection` returns an open connection without disposing it. | Return a `using` connection or ensure callers dispose it. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | `ExecuteQuery` opens a connection but never closes or disposes it. | Wrap connection in `using` statement. |
| SampleBankingApp/Data/DatabaseHelper.cs | 48 | `ExecuteNonQuery` opens a connection but only calls `Close()`, not `Dispose()`. | Wrap connection in `using` statement. |
| SampleBankingApp/Services/AuthService.cs | 41 | `SqlConnection` in `Login` is opened but never closed or disposed. | Wrap connection in `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` is held as an instance field, which is not thread-safe. | Create a new `SmtpClient` per send operation or use a thread-safe wrapper. |
| SampleBankingApp/Services/EmailService.cs | 38 | `MailMessage` in `SendTransferNotification` is not disposed. | Wrap `MailMessage` in `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 58 | `MailMessage` in `SendWelcomeEmail` is not disposed. | Wrap `MailMessage` in `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 75 | `MailMessage` in `SendWelcomeEmailHtml` is not disposed. | Wrap `MailMessage` in `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 25 | `int.Parse` on `userIdClaim` can throw if claim is null. | Add null check before parsing. |
| SampleBankingApp/Controllers/TransactionController.cs | 38 | `int.Parse` on `userIdClaim` can throw if claim is null. | Add null check before parsing. |
| SampleBankingApp/Services/TransactionService.cs | 38 | Accessing `Rows[0]` without checking `Rows.Count > 0` can throw. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/TransactionService.cs | 42 | Accessing `Rows[0]` without checking `Rows.Count > 0` can throw. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/UserService.cs | 33 | Accessing `Rows[0]` without checking `Rows.Count > 0` can throw. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/UserService.cs | 78 | Accessing `Rows[0]` in `IsWithinDailyLimit` without checking `Rows.Count > 0` can throw. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/AuthService.cs | 45 | Casting `reader["Id"]` etc. can throw if column is null or missing. | Use `IsDBNull` checks or nullable casts. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | `email.Length` can throw if `email` is null. | Add null check or use `string.IsNullOrEmpty`. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | `username.Length` can throw if `username` is null. | Add null check or use `string.IsNullOrEmpty`. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 95 | `ValidateToken` method is unreachable after early return. | Remove the method or fix the logic. |
| SampleBankingApp/Services/AuthService.cs | 88 | `HashPasswordSha1` is defined but never called. | Remove the unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 30 | `JoinWithSeparator` is inefficient and likely unused if `JoinWithSeparatorFixed` exists. | Remove the inefficient method. |
| SampleBankingApp/Helpers/StringHelper.cs | 36 | `JoinWithSeparatorFixed` duplicates `string.Join`. | Remove the redundant method. |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | `ObfuscateAccount` duplicates functionality of `MaskAccountNumber`. | Remove the duplicate method. |
| SampleBankingApp/Helpers/StringHelper.cs | 60 | `ToTitleCase` duplicates standard library functionality. | Remove the redundant method. |
| SampleBankingApp/Helpers/StringHelper.cs | 66 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove the redundant method. |
| SampleBankingApp/Services/TransactionService.cs | 81 | `FormatCurrency` is defined but never called. | Remove the unused method. |
| SampleBankingApp/Services/TransactionService.cs | 85 | `RefundTransaction` throws `NotImplementedException`. | Implement the method or remove it. |
| SampleBankingApp/Data/DatabaseHelper.cs | 58 | `ExecuteQueryWithParams` is marked `[Obsolete]` but still present. | Remove the obsolete method. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 12 | `TransactionFeeRate` is a magic number. | Define as a named constant or configuration value. |
| SampleBankingApp/Services/TransactionService.cs | 13 | `MaxTransactionsPerDay` is a magic number. | Define as a named constant or configuration value. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit limit `1000000` is a magic number. | Define as a named constant or configuration value. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Interest rate `0.05m` is a magic number. | Define as a named constant or configuration value. |
| SampleBankingApp/Services/UserService.cs | 72 | Page size limit `50` is a magic number. | Define as a named constant or configuration value. |
| SampleBankingApp/Services/UserService.cs | 28 | User ID range `1000000` is a magic number. | Define as a named constant or configuration value. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | Email length limit `254` is a magic number. | Define as a named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | Username length limits `3` and `20` are magic numbers. | Define as named constants. |
| SampleBankingApp/Services/EmailService.cs | 12 | `MaxRetries` and `SmtpTimeoutMs` are magic numbers. | Define as named constants or configuration values. |
| SampleBankingApp/Services/EmailService.cs | 38 | Email subject and body strings are hardcoded. | Move to configuration or resource files. |
| SampleBankingApp/Services/EmailService.cs | 58 | Email subject and body strings are hardcoded. | Move to configuration or resource files. |
| SampleBankingApp/Services/EmailService.cs | 75 | Email subject and body strings are hardcoded. | Move to configuration or resource files. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 27 | String concatenation in loop is O(n²). | Use `string.Join` or `StringBuilder`. |
| SampleBankingApp/Helpers/StringHelper.cs | 14 | `new Regex` created on every call. | Use `static readonly Regex` for performance. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `new Regex` created on every call. | Use `static readonly Regex` for performance. |
| SampleBankingApp/Services/UserService.cs | 12 | `_auditLog` is static mutable state, not thread-safe. | Use a thread-safe collection or external logging. |
| SampleBankingApp/Services/UserService.cs | 13 | `_requestCount` is static mutable state, not thread-safe. | Use a thread-safe counter or remove if unused. |
| SampleBankingApp/Services/UserService.cs | 83 | String concatenation in loop for audit report is O(n²). | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` is not thread-safe. | Create a new instance per request or use a thread-safe wrapper. |
| SampleBankingApp/Services/EmailService.cs | 48 | `Console.WriteLine` used for logging. | Use `ILogger` for structured logging. |
| SampleBankingApp/Services/EmailService.cs | 63 | `Console.WriteLine` used for logging. | Use `ILogger` for structured logging. |
| SampleBankingApp/Program.cs | 12 | `DatabaseHelper` registered as `Singleton` but holds non-thread-safe state. | Register as `Scoped` or ensure thread safety. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 38 | `ValidateLifetime = false` disables JWT expiration. | Set `ValidateLifetime = true`. |
| SampleBankingApp/Program.cs | 46 | `UseDeveloperExceptionPage()` is unconditional. | Use conditional middleware for development only. |
| SampleBankingApp/Program.cs | 48 | HTTPS redirection is commented out. | Uncomment `UseHttpsRedirection()` for production. |
| SampleBankingApp/Program.cs | 50 | CORS policy allows any origin, method, and header. | Restrict to specific trusted origins and methods. |
| SampleBankingApp/appsettings.json | 20 | Debug log level set for production namespaces. | Set log level to `Information` or `Warning` for production. |
| SampleBankingApp/SampleBankingApp.csproj | 10 | `Newtonsoft.Json` version 12.0.3 is outdated and vulnerable. | Update to the latest stable version. |
| SampleBankingApp/SampleBankingApp.csproj | 12 | `System.Data.SqlClient` is deprecated. | Use `Microsoft.Data.SqlClient` instead. |
| SampleBankingApp/SampleBankingApp.csproj | 7 | `TreatWarningsAsErrors` is false. | Set to `true` to enforce code quality. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `DebugSymbols` and `DebugType` are set for release builds. | Remove or conditionally set for debug builds only. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create a test project with unit tests for critical services. |
| SampleBankingApp/Services/TransactionService.cs | 28 | `Transfer` method lacks tests for balance checks, fees, and SQL injection. | Add unit tests mocking database calls. |
| SampleBankingApp/Services/TransactionService.cs | 58 | `Deposit` method lacks tests for amount validation and interest calculation. | Add unit tests mocking database calls. |
| SampleBankingApp/Services/UserService.cs | 26 | `GetUsersPage` lacks tests for pagination logic. | Add unit tests for pagination edge cases. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` method lacks tests for authentication and SQL injection. | Add unit tests mocking database calls. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | `IsValidEmail` and `IsValidUsername` lack tests. | Add unit tests for validation logic. |
| SampleBankingApp/Controllers/TransactionController.cs | 24 | `Transfer` endpoint lacks tests for authorization and ownership checks. | Add integration tests for API endpoints. |
| SampleBankingApp/Controllers/UserController.cs | 36 | `UpdateUser` endpoint lacks tests for authorization and ownership checks. | Add integration tests for API endpoints. |