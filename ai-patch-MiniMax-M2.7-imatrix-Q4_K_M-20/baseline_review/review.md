## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 33 | SQL injection via string interpolation in `Login` method. | Use parameterized queries. |
| SampleBankingApp/Services/AuthService.cs | 50 | Hardcoded admin bypass password allows authentication without DB check. | Remove backdoor logic. |
| SampleBankingApp/Services/AuthService.cs | 62 | Passwords hashed using MD5, which is cryptographically broken. | Use bcrypt, Argon2, or PBKDF2. |
| SampleBankingApp/Services/TransactionService.cs | 43 | SQL injection via string interpolation in `Transfer` method. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 63 | SQL injection via string interpolation in `Deposit` method. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 85 | SQL injection via string interpolation in `RecordTransaction` method. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 38 | SQL injection via string interpolation in `UpdateUser` method. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 50 | SQL injection via string interpolation in `DeleteUser` method. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 78 | SQL injection via string interpolation in `SearchUsers` method. | Use parameterized queries. |
| SampleBankingApp/Data/DatabaseHelper.cs | 15 | Hardcoded fallback connection string with credentials. | Remove hardcoded credentials; fail if config is missing. |
| SampleBankingApp/appsettings.json | 2 | Production database credentials committed to source control. | Use environment variables or secret management. |
| SampleBankingApp/appsettings.json | 13 | Email SMTP password committed to source control. | Use environment variables or secret management. |
| SampleBankingApp/appsettings.json | 5 | Weak JWT secret key ("mysecretkey"). | Use a strong, randomly generated secret. |
| SampleBankingApp/Controllers/UserController.cs | 26 | Missing authorization check; any authenticated user can view any user's data. | Add `[Authorize(Policy = "Admin")]` or ownership check. |
| SampleBankingApp/Controllers/UserController.cs | 42 | Missing authorization check; any authenticated user can update any user. | Add `[Authorize(Policy = "Admin")]` or ownership check. |
| SampleBankingApp/Controllers/UserController.cs | 56 | Missing authorization check; any authenticated user can delete any user. | Add `[Authorize(Policy = "Admin")]` or ownership check. |
| SampleBankingApp/Controllers/UserController.cs | 70 | Missing authorization check; any authenticated user can search users. | Add appropriate authorization. |
| SampleBankingApp/Controllers/UserController.cs | 76 | Missing authorization check; any authenticated user can view audit logs. | Add `[Authorize(Policy = "Admin")]`. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 40 | Balance check uses `amount` but deducts `amount + fee`, allowing negative balances. | Check `fromBalance >= totalDebit`. |
| SampleBankingApp/Services/UserService.cs | 65 | Pagination offset calculation `page * pageSize` is off-by-one for 1-based pages. | Use `(page - 1) * pageSize`. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit interest calculation `amount * 0.05m * 1` is redundant and potentially misleading. | Clarify intent or remove `* 1`. |
| SampleBankingApp/Controllers/TransactionController.cs | 18 | `int.Parse` on `userIdClaim` can throw if claim is null or non-integer. | Validate claim existence and format before parsing. |
| SampleBankingApp/Controllers/TransactionController.cs | 30 | `int.Parse` on `userIdClaim` can throw if claim is null or non-integer. | Validate claim existence and format before parsing. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/UserService.cs | 82 | Catch block swallows exception and returns empty list, hiding errors. | Log error and return appropriate status or throw. |
| SampleBankingApp/Controllers/UserController.cs | 48 | Raw exception message returned to client in `UpdateUser`. | Return generic error message; log details. |
| SampleBankingApp/Controllers/UserController.cs | 52 | Raw exception message returned to client in `UpdateUser`. | Return generic error message; log details. |
| SampleBankingApp/Services/EmailService.cs | 58 | Exception swallowed in `SendWelcomeEmail`, hiding failures. | Log error instead of printing to console. |
| SampleBankingApp/Services/TransactionService.cs | 92 | `RefundTransaction` throws `NotImplementedException` without handling. | Implement logic or return specific error. |
| SampleBankingApp/Services/TransactionService.cs | 43 | No database transaction for atomic balance updates in `Transfer`. | Wrap updates in a transaction. |
| SampleBankingApp/Services/TransactionService.cs | 63 | No database transaction for deposit update. | Wrap update in a transaction. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 22 | `GetOpenConnection` returns open connection without disposal contract. | Use `using` statements or return disposable wrapper. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | `ExecuteQuery` opens connection but never closes/disposes it. | Wrap connection in `using` block. |
| SampleBankingApp/Data/DatabaseHelper.cs | 48 | `ExecuteNonQuery` closes connection but doesn't dispose command/adapter. | Use `using` statements for all disposables. |
| SampleBankingApp/Services/AuthService.cs | 35 | `SqlConnection` and `SqlDataReader` not disposed in `Login`. | Use `using` statements. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` held as instance field; not thread-safe and may leak sockets. | Create new instance per send or use proper pooling. |
| SampleBankingApp/Services/EmailService.cs | 38 | `MailMessage` not disposed in `SendTransferNotification`. | Wrap `MailMessage` in `using` block. |
| SampleBankingApp/Services/EmailService.cs | 55 | `MailMessage` not disposed in `SendWelcomeEmail`. | Wrap `MailMessage` in `using` block. |
| SampleBankingApp/Services/EmailService.cs | 75 | `MailMessage` not disposed in `SendWelcomeEmailHtml`. | Wrap `MailMessage` in `using` block. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 38 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check row count before access. |
| SampleBankingApp/Services/TransactionService.cs | 41 | `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check row count before access. |
| SampleBankingApp/Services/UserService.cs | 33 | `table.Rows[0]` accessed without checking `Rows.Count > 0` in `GetUserById`. | Check row count before access. |
| SampleBankingApp/Services/UserService.cs | 75 | `table.Rows` iterated without checking if table is null/empty in `GetUsersPage`. | Validate table result. |
| SampleBankingApp/Services/UserService.cs | 80 | `table.Rows` iterated without checking if table is null/empty in `SearchUsers`. | Validate table result. |
| SampleBankingApp/Program.cs | 20 | `jwtSecret` could be null, causing `GetBytes` to throw. | Validate configuration key existence. |
| SampleBankingApp/Services/AuthService.cs | 68 | `_config["Jwt:SecretKey"]` could be null. | Validate configuration key existence. |
| SampleBankingApp/Services/EmailService.cs | 25 | `_config["Email:SmtpHost"]` could be null. | Validate configuration key existence. |
| SampleBankingApp/Services/EmailService.cs | 26 | `_config["Email:SmtpPort"]` could be null, causing `int.Parse` to throw. | Provide default or validate. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 26 | `JoinWithSeparator` is inefficient and likely unused given `JoinWithSeparatorFixed`. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 32 | `JoinWithSeparatorFixed` duplicates `string.Join`. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `ObfuscateAccount` duplicates `MaskAccountNumber` logic. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 50 | `ToTitleCase` duplicates standard library functionality. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove if unused. |
| SampleBankingApp/Data/DatabaseHelper.cs | 58 | `ExecuteQueryWithParams` is marked `[Obsolete]` but still present. | Remove if no longer called. |
| SampleBankingApp/Services/AuthService.cs | 78 | `HashPasswordSha1` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/AuthService.cs | 86 | `ValidateToken` has unreachable code after `return true`. | Remove dead code. |
| SampleBankingApp/Services/TransactionService.cs | 89 | `FormatCurrency` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/EmailService.cs | 68 | `BuildHtmlTemplate` is only called by `SendWelcomeEmailHtml`, which is unused. | Remove if unused. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 10 | `TransactionFeeRate` (0.015) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 11 | `MaxTransactionsPerDay` (10) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit limit (1000000) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Interest rate (0.05) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 62 | Page size limit (50) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 28 | User ID range limit (1000000) is hardcoded. | Move to configuration. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | Email length limit (254) is hardcoded. | Define as constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | Username length limits (3, 20) are hardcoded. | Define as constants. |
| SampleBankingApp/Services/EmailService.cs | 22 | SMTP timeout (5000) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 22 | Max retries (3) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/AuthService.cs | 22 | Admin bypass password is hardcoded. | Remove entirely. |
| SampleBankingApp/Services/AuthService.cs | 66 | JWT expiration (30 days) is hardcoded. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 26 | String concatenation in loop (`result += item`). | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Helpers/StringHelper.cs | 14 | `new Regex` created on every call in `IsValidEmail`. | Use `static readonly Regex`. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `new Regex` created on every call in `IsValidUsername`. | Use `static readonly Regex`. |
| SampleBankingApp/Services/UserService.cs | 10 | `_auditLog` is static mutable state without synchronization. | Use thread-safe collection or remove. |
| SampleBankingApp/Services/UserService.cs | 11 | `_requestCount` is static mutable state without synchronization. | Use `Interlocked` or remove. |
| SampleBankingApp/Services/UserService.cs | 72 | String concatenation in loop for audit report. | Use `StringBuilder`. |
| SampleBankingApp/Program.cs | 15 | `DatabaseHelper` registered as `Singleton`, but holds non-thread-safe state/connections. | Register as `Scoped` or ensure thread safety. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` is not thread-safe; shared instance causes race conditions. | Create per-request or use thread-safe wrapper. |
| SampleBankingApp/Services/AuthService.cs | 33 | Raw SQL construction instead of using ORM or parameterized helpers. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 43 | Raw SQL construction instead of using ORM or parameterized helpers. | Use parameterized queries. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 28 | `UseDeveloperExceptionPage()` enabled unconditionally. | Only enable in Development environment. |
| SampleBankingApp/Program.cs | 30 | `UseHttpsRedirection()` is commented out. | Enable HTTPS redirection. |
| SampleBankingApp/Program.cs | 32 | CORS policy allows any origin, method, and header. | Restrict to specific origins/methods. |
| SampleBankingApp/Program.cs | 18 | `ValidateLifetime = false` disables JWT expiration checks. | Set to `true`. |
| SampleBankingApp/appsettings.json | 17 | Logging level set to `Debug` for all namespaces. | Set to `Information` or `Warning` for production. |
| SampleBankingApp/SampleBankingApp.csproj | 10 | `DebugSymbols` and `DebugType` set to full in project file. | Remove or set conditionally for release. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | `Newtonsoft.Json` version 12.0.3 is outdated and vulnerable. | Update to latest stable version. |
| SampleBankingApp/SampleBankingApp.csproj | 14 | `System.Data.SqlClient` is legacy; use `Microsoft.Data.SqlClient`. | Update package reference. |
| SampleBankingApp/appsettings.json | 2 | Connection string includes `TrustServerCertificate=True`. | Disable in production; use valid certs. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create test project. |
| SampleBankingApp/Services/TransactionService.cs | 20 | `Transfer` logic for balance deduction and fee calculation needs testing. | Add unit tests for success/failure cases. |
| SampleBankingApp/Services/TransactionService.cs | 60 | `Deposit` logic for interest and limits needs testing. | Add unit tests for boundary conditions. |
| SampleBankingApp/Services/UserService.cs | 60 | `GetUsersPage` pagination logic needs testing. | Add unit tests for offset calculation. |
| SampleBankingApp/Services/AuthService.cs | 25 | `Login` authentication and JWT generation need testing. | Add unit tests for valid/invalid credentials. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | Validation helpers need testing. | Add unit tests for edge cases. |
| SampleBankingApp/Controllers/TransactionController.cs | 15 | Controller actions need integration testing. | Add integration tests for API endpoints. |
| SampleBankingApp/Controllers/UserController.cs | 20 | Controller actions need integration testing. | Add integration tests for API endpoints. |