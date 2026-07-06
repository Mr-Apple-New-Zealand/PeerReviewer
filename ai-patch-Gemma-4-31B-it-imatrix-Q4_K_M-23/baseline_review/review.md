## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 38 | SQL Injection via string interpolation in `Login` method. | Use parameterized queries. |
| SampleBankingApp/Services/AuthService.cs | 56 | Hardcoded admin backdoor password allows bypassing authentication. | Remove hardcoded credentials and backdoor logic. |
| SampleBankingApp/Services/AuthService.cs | 66 | MD5 is cryptographically broken and unsuitable for password hashing. | Use bcrypt, Argon2, or PBKDF2. |
| SampleBankingApp/Services/TransactionService.cs | 43 | SQL Injection in `Transfer` via string interpolation in `ExecuteNonQuery`. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 63 | SQL Injection in `Deposit` via string interpolation in `ExecuteNonQuery`. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 88 | SQL Injection in `RecordTransaction` via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 35 | SQL Injection in `UpdateUser` via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 48 | SQL Injection in `DeleteUser` via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 78 | SQL Injection in `SearchUsers` via `ExecuteQuery` with raw `LIKE` clause. | Use parameterized queries. |
| SampleBankingApp/Data/DatabaseHelper.cs | 15 | Hardcoded fallback connection string with plaintext credentials. | Remove hardcoded credentials; fail securely if config is missing. |
| SampleBankingApp/appsettings.json | 2 | Production database credentials committed to source control. | Use environment variables or secret management. |
| SampleBankingApp/appsettings.json | 13 | Email service password committed to source control. | Use environment variables or secret management. |
| SampleBankingApp/Controllers/UserController.cs | 36 | Missing authorization check allows any authenticated user to update/delete any user. | Add ownership verification or admin role check. |
| SampleBankingApp/Controllers/UserController.cs | 58 | Missing authorization check allows any authenticated user to delete any user. | Add ownership verification or admin role check. |
| SampleBankingApp/Controllers/UserController.cs | 72 | Missing authorization check allows any authenticated user to view audit logs. | Restrict to Admin role. |
| SampleBankingApp/Program.cs | 28 | JWT lifetime validation is disabled (`ValidateLifetime = false`). | Set `ValidateLifetime = true`. |
| SampleBankingApp/Program.cs | 39 | Developer exception page enabled in production configuration. | Wrap in `if (app.Environment.IsDevelopment())`. |
| SampleBankingApp/Program.cs | 42 | HTTPS redirection is commented out. | Uncomment `app.UseHttpsRedirection()`. |
| SampleBankingApp/Program.cs | 44 | Overly permissive CORS policy allows any origin, method, and header. | Restrict to specific trusted origins. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 40 | Balance check uses `amount` but deducts `amount + fee`, allowing negative balances. | Check `fromBalance >= totalDebit`. |
| SampleBankingApp/Services/TransactionService.cs | 40 | No check prevents users from transferring funds to themselves. | Add check `if (fromUserId == toUserId)`. |
| SampleBankingApp/Services/UserService.cs | 65 | Pagination offset calculation is incorrect (`page * pageSize` instead of `(page - 1) * pageSize`). | Change to `(page - 1) * pageSize`. |
| SampleBankingApp/Services/AuthService.cs | 95 | `ValidateToken` always returns `true` due to early return before validation logic. | Remove early `return true;` or fix logic flow. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit interest calculation multiplies by `1`, making the bonus equal to the full amount instead of 5%. | Remove `* 1` or clarify intent. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/UserController.cs | 41 | Raw exception message returned to client in `UpdateUser`. | Return generic error message; log details. |
| SampleBankingApp/Controllers/UserController.cs | 44 | Raw exception message returned to client in `UpdateUser`. | Return generic error message; log details. |
| SampleBankingApp/Services/UserService.cs | 83 | `SearchUsers` swallows all exceptions and returns empty list, hiding errors. | Log exception and return error status or empty list with warning. |
| SampleBankingApp/Services/EmailService.cs | 58 | `SendWelcomeEmail` swallows exceptions silently. | Log exception properly. |
| SampleBankingApp/Services/TransactionService.cs | 43 | Database writes in `Transfer` are not atomic; failure after debit causes data inconsistency. | Wrap in database transaction. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Database writes in `Deposit` are not atomic with transaction recording. | Wrap in database transaction. |
| SampleBankingApp/Controllers/TransactionController.cs | 33 | `Refund` endpoint catches `NotImplementedException` but returns 500, misleading client. | Return 501 Not Implemented or 503 Service Unavailable. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 22 | `GetOpenConnection` returns open connection without disposing; caller must dispose. | Use `using` blocks or `IDisposable` pattern in callers. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | `ExecuteQuery` opens connection but never closes/disposes it on success or error. | Wrap connection in `using` block. |
| SampleBankingApp/Data/DatabaseHelper.cs | 48 | `ExecuteNonQuery` opens connection but does not dispose command or connection on exception. | Wrap in `using` blocks. |
| SampleBankingApp/Services/AuthService.cs | 41 | `SqlConnection` and `SqlDataReader` in `Login` are never disposed. | Wrap in `using` blocks. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` is instantiated once and reused; it is not thread-safe and may leak sockets. | Instantiate per request or use a thread-safe wrapper. |
| SampleBankingApp/Services/EmailService.cs | 38 | `MailMessage` in `SendTransferNotification` is not disposed. | Wrap in `using` block. |
| SampleBankingApp/Services/EmailService.cs | 52 | `MailMessage` in `SendWelcomeEmail` is not disposed. | Wrap in `using` block. |
| SampleBankingApp/Services/EmailService.cs | 72 | `MailMessage` in `SendWelcomeEmailHtml` is not disposed. | Wrap in `using` block. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 20 | `int.Parse` on `userIdClaim` may throw if claim is null or invalid format. | Use `int.TryParse` with null check. |
| SampleBankingApp/Controllers/TransactionController.cs | 30 | `int.Parse` on `userIdClaim` may throw if claim is null or invalid format. | Use `int.TryParse` with null check. |
| SampleBankingApp/Services/TransactionService.cs | 35 | Accessing `Rows[0]` without checking `Rows.Count` throws if user not found. | Check `Rows.Count > 0`. |
| SampleBankingApp/Services/TransactionService.cs | 39 | Accessing `Rows[0]` without checking `Rows.Count` throws if user not found. | Check `Rows.Count > 0`. |
| SampleBankingApp/Services/UserService.cs | 30 | Accessing `Rows[0]` without checking `Rows.Count` throws if user not found. | Check `Rows.Count > 0`. |
| SampleBankingApp/Services/UserService.cs | 70 | Accessing `Rows[0]` in `IsWithinDailyLimit` assumes row exists. | Check `Rows.Count > 0`. |
| SampleBankingApp/Program.cs | 24 | `jwtSecret` may be null, causing `GetBytes` to throw. | Add null check or default value. |
| SampleBankingApp/Services/AuthService.cs | 78 | `_config["Jwt:SecretKey"]` may be null, causing `GetBytes` to throw. | Add null check. |
| SampleBankingApp/Services/EmailService.cs | 25 | `_config["Email:SmtpHost"]` may be null, causing `SmtpClient` constructor to throw. | Add null check. |
| SampleBankingApp/Services/EmailService.cs | 26 | `_config["Email:SmtpPort"]` may be null, causing `int.Parse` to throw. | Add null check or default. |
| SampleBankingApp/Services/EmailService.cs | 28 | `_config["Email:Username"]` may be null. | Add null check. |
| SampleBankingApp/Services/EmailService.cs | 29 | `_config["Email:Password"]` may be null. | Add null check. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 27 | `JoinWithSeparator` is inefficient and likely unused given `JoinWithSeparatorFixed` exists. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 33 | `JoinWithSeparatorFixed` duplicates `string.Join`; likely unused. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 48 | `ObfuscateAccount` duplicates functionality of `MaskAccountNumber`. | Remove duplicate. |
| SampleBankingApp/Helpers/StringHelper.cs | 53 | `ToTitleCase` duplicates standard library functionality. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 58 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove if unused. |
| SampleBankingApp/Services/AuthService.cs | 90 | `HashPasswordSha1` is defined but never called. | Remove dead code. |
| SampleBankingApp/Services/TransactionService.cs | 83 | `FormatCurrency` is defined but never called. | Remove dead code. |
| SampleBankingApp/Services/EmailService.cs | 66 | `BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml`, which is likely unused. | Remove if unused. |
| SampleBankingApp/Data/DatabaseHelper.cs | 58 | `ExecuteQueryWithParams` is marked `[Obsolete]` but still present. | Remove obsolete code. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 10 | `TransactionFeeRate` (0.015) is hardcoded; should be configurable. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 11 | `MaxTransactionsPerDay` (10) is hardcoded; should be configurable. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 61 | Deposit limit (1000000) is hardcoded; should be configurable. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 62 | Interest rate (0.05) is hardcoded; should be configurable. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 62 | Page size limit (50) is hardcoded; should be configurable. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 22 | User ID range limit (1000000) is hardcoded; should be configurable. | Move to configuration. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | Email length limit (254) is hardcoded; should be configurable or constant. | Define as constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 17 | Username length limits (3, 20) are hardcoded; should be configurable. | Define as constants. |
| SampleBankingApp/Services/AuthService.cs | 15 | Admin bypass password is hardcoded magic string. | Remove entirely. |
| SampleBankingApp/Services/EmailService.cs | 10 | Email subjects are hardcoded; should be configurable. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 12 | Max retries (3) is hardcoded; should be configurable. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 13 | SMTP timeout (5000) is hardcoded; should be configurable. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 27 | String concatenation in loop causes O(n²) performance. | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | `new Regex` created on every call; should be static readonly. | Cache regex instance. |
| SampleBankingApp/Helpers/StringHelper.cs | 19 | `new Regex` created on every call; should be static readonly. | Cache regex instance. |
| SampleBankingApp/Services/UserService.cs | 12 | Static mutable state `_auditLog` shared across threads without synchronization. | Use thread-safe collection or DI-scoped service. |
| SampleBankingApp/Services/UserService.cs | 13 | Static mutable state `_requestCount` shared across threads without synchronization. | Use thread-safe counter or DI-scoped service. |
| SampleBankingApp/Services/UserService.cs | 75 | String concatenation in loop for audit report causes O(n²) performance. | Use `StringBuilder`. |
| SampleBankingApp/Services/AuthService.cs | 38 | Raw SQL string interpolation instead of parameterized queries. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 43 | Raw SQL string interpolation instead of parameterized queries. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 35 | Raw SQL string interpolation instead of parameterized queries. | Use parameterized queries. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | `ExecuteQuery` constructs SQL via interpolation, enabling injection. | Use parameterized queries. |
| SampleBankingApp/Program.cs | 10 | `DatabaseHelper` registered as Singleton, but holds non-thread-safe state implicitly via connections. | Ensure thread-safety or use Scoped. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` is not thread-safe; shared instance causes race conditions. | Instantiate per request. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 39 | `UseDeveloperExceptionPage()` enabled unconditionally. | Wrap in `IsDevelopment()` check. |
| SampleBankingApp/Program.cs | 28 | JWT `ValidateLifetime` set to `false`. | Set to `true`. |
| SampleBankingApp/Program.cs | 42 | HTTPS redirection commented out. | Uncomment. |
| SampleBankingApp/Program.cs | 44 | CORS allows any origin, method, and header. | Restrict to specific origins. |
| SampleBankingApp/appsettings.json | 18 | Debug log level set for production namespaces. | Set to `Information` or `Warning` for production. |
| SampleBankingApp/SampleBankingApp.csproj | 10 | `Newtonsoft.Json` version 12.0.3 is outdated and vulnerable. | Update to latest stable version. |
| SampleBankingApp/SampleBankingApp.csproj | 11 | `System.IdentityModel.Tokens.Jwt` version 7.0.0 may conflict with ASP.NET Core 8.0. | Align versions with framework. |
| SampleBankingApp/SampleBankingApp.csproj | 6 | `TreatWarningsAsErrors` is false. | Set to `true` for production builds. |
| SampleBankingApp/SampleBankingApp.csproj | 7 | `DebugSymbols` enabled in project file; may leak in release. | Ensure release build strips symbols. |
| SampleBankingApp/appsettings.json | 1 | Production connection string committed to source control. | Use environment variables. |
| SampleBankingApp/appsettings.json | 13 | Email credentials committed to source control. | Use environment variables. |
| SampleBankingApp/appsettings.json | 2 | JWT secret key committed to source control. | Use environment variables. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create test project. |
| SampleBankingApp/Services/TransactionService.cs | 25 | `Transfer` logic lacks tests for balance checks, fees, and SQL injection prevention. | Add unit tests for transfer scenarios. |
| SampleBankingApp/Services/TransactionService.cs | 58 | `Deposit` logic lacks tests for limits, interest, and SQL injection prevention. | Add unit tests for deposit scenarios. |
| SampleBankingApp/Services/AuthService.cs | 25 | `Login` logic lacks tests for SQL injection, password hashing, and backdoor removal. | Add unit tests for authentication. |
| SampleBankingApp/Services/UserService.cs | 20 | `GetUserById` lacks tests for boundary conditions and SQL injection. | Add unit tests for user retrieval. |
| SampleBankingApp/Services/UserService.cs | 60 | `GetUsersPage` lacks tests for pagination logic and SQL injection. | Add unit tests for pagination. |
| SampleBankingApp/Services/UserService.cs | 70 | `SearchUsers` lacks tests for SQL injection and error handling. | Add unit tests for search. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | `IsValidEmail` lacks tests for regex edge cases. | Add unit tests for validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 17 | `IsValidUsername` lacks tests for regex edge cases. | Add unit tests for validation. |
| SampleBankingApp/Controllers/AuthController.cs | 15 | `Login` endpoint lacks integration tests for auth flow. | Add integration tests. |
| SampleBankingApp/Controllers/TransactionController.cs | 15 | `Transfer` endpoint lacks integration tests for authorization and validation. | Add integration tests. |