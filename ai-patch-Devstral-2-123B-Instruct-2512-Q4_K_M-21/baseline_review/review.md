## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 38 | SQL Injection in login query via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin backdoor password allows bypassing authentication. | Remove hardcoded credentials and backdoor logic. |
| SampleBankingApp/Services/AuthService.cs | 63 | MD5 used for password hashing is cryptographically broken. | Use bcrypt, Argon2, or PBKDF2. |
| SampleBankingApp/Services/TransactionService.cs | 46 | SQL Injection in balance update via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 65 | SQL Injection in deposit update via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 89 | SQL Injection in transaction recording via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 43 | SQL Injection in user update via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 55 | SQL Injection in user deletion via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 88 | SQL Injection in user search via string interpolation in LIKE clause. | Use parameterized queries. |
| SampleBankingApp/Controllers/UserController.cs | 40 | Broken Access Control: Any authenticated user can update/delete any user. | Add authorization checks to ensure user owns the resource. |
| SampleBankingApp/Program.cs | 28 | JWT lifetime validation is disabled, allowing tokens to never expire. | Set `ValidateLifetime = true`. |
| SampleBankingApp/Program.cs | 38 | Open CORS policy allows any origin, method, and header. | Restrict CORS to specific trusted origins. |
| SampleBankingApp/appsettings.json | 2 | Production database credentials and SMTP passwords are hardcoded in config. | Use environment variables or a secrets manager. |
| SampleBankingApp/Data/DatabaseHelper.cs | 18 | Fallback connection string contains hardcoded SA credentials. | Remove hardcoded fallback credentials. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check only verifies `amount`, ignoring the `fee`, allowing negative balances. | Check if `fromBalance >= amount + fee`. |
| SampleBankingApp/Services/UserService.cs | 73 | Pagination skip calculation uses `page * pageSize` instead of `(page - 1) * pageSize`. | Change to `(page - 1) * pageSize`. |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit interest bonus calculation multiplies by 1, making the bonus equal to the full 5% amount incorrectly. | Clarify intent; likely should be a smaller rate or removed. |
| SampleBankingApp/Controllers/TransactionController.cs | 15 | `int.Parse` on `userIdClaim` can throw if claim is missing or non-numeric. | Add null/parse validation before parsing. |
| SampleBankingApp/Services/AuthService.cs | 98 | `ValidateToken` always returns true due to early return before validation logic. | Remove early return or fix logic flow. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/UserController.cs | 48 | Raw exception message returned to client in 500 response. | Return generic error message; log details internally. |
| SampleBankingApp/Services/UserService.cs | 95 | Catch block swallows exception and returns empty list, hiding errors. | Log the exception and rethrow or return error status. |
| SampleBankingApp/Services/TransactionService.cs | 46 | Multiple DB writes (debit, credit, record) lack atomic transaction scope. | Wrap operations in a database transaction. |
| SampleBankingApp/Services/EmailService.cs | 58 | Exception caught and logged to Console, then silently ignored. | Log properly and consider retry or fail-fast strategy. |
| SampleBankingApp/Services/AuthService.cs | 38 | `SqlConnection` and `SqlDataReader` opened but never closed/disposed. | Use `using` statements for connection and reader. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 22 | `GetOpenConnection` returns open connection without disposing; caller must manage it. | Return `SqlConnection` wrapped in `using` or change contract. |
| SampleBankingApp/Data/DatabaseHelper.cs | 30 | `ExecuteQuery` opens connection but does not close/dispose it on success or error. | Wrap connection in `using` block. |
| SampleBankingApp/Data/DatabaseHelper.cs | 48 | `ExecuteNonQuery` opens connection but does not dispose command or adapter. | Use `using` for command and adapter. |
| SampleBankingApp/Services/EmailService.cs | 18 | `SmtpClient` is not thread-safe and held as instance field; sockets may leak. | Create new `SmtpClient` per send or use thread-safe alternative. |
| SampleBankingApp/Services/EmailService.cs | 38 | `MailMessage` is `IDisposable` but never disposed. | Wrap `MailMessage` in `using` block. |
| SampleBankingApp/Services/AuthService.cs | 38 | `SqlConnection` created in `Login` is never closed or disposed. | Use `using` statement for connection. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 15 | `userIdClaim` may be null; `int.Parse` will throw `NullReferenceException`. | Add null check before parsing. |
| SampleBankingApp/Services/TransactionService.cs | 38 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check row count before accessing. |
| SampleBankingApp/Services/TransactionService.cs | 42 | `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check row count before accessing. |
| SampleBankingApp/Services/UserService.cs | 38 | `table.Rows[0]` accessed without checking `Rows.Count > 0` in `GetUserById`. | Check row count before accessing. |
| SampleBankingApp/Services/EmailService.cs | 22 | `_config["Email:SmtpHost"]` may be null, passed to `SmtpClient` constructor. | Add null check or default value. |
| SampleBankingApp/Program.cs | 22 | `jwtSecret` may be null, passed to `Encoding.UTF8.GetBytes`. | Add null check or configuration validation. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 28 | `JoinWithSeparator` is inefficient and likely unused; `JoinWithSeparatorFixed` exists. | Remove `JoinWithSeparator` if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 48 | `ObfuscateAccount` duplicates functionality of `MaskAccountNumber`. | Remove duplicate method. |
| SampleBankingApp/Helpers/StringHelper.cs | 58 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Remove method; use standard library. |
| SampleBankingApp/Services/TransactionService.cs | 94 | `FormatCurrency` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/EmailService.cs | 68 | `BuildHtmlTemplate` is private and only used by `SendWelcomeEmailHtml`. | Keep if used, but verify usage. |
| SampleBankingApp/Services/EmailService.cs | 72 | `SendWelcomeEmailHtml` is public but may be unused. | Verify usage; remove if dead. |
| SampleBankingApp/Data/DatabaseHelper.cs | 58 | `ExecuteQueryWithParams` is marked `[Obsolete]` but still present. | Remove obsolete code. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 12 | `TransactionFeeRate` (0.015) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 13 | `MaxTransactionsPerDay` (10) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit limit (1000000) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 65 | Interest rate (0.05) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 71 | Page size limit (50) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/AuthService.cs | 15 | Admin bypass password is hardcoded. | Remove entirely; do not hardcode secrets. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | Email length limit (254) is hardcoded. | Move to configuration or constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | Username length limits (3, 20) are hardcoded. | Move to configuration or constant. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 28 | String concatenation in loop is O(n²). | Use `string.Join` or `StringBuilder`. |
| SampleBankingApp/Helpers/StringHelper.cs | 14 | `new Regex` created on every call. | Use `static readonly Regex`. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `new Regex` created on every call. | Use `static readonly Regex`. |
| SampleBankingApp/Services/UserService.cs | 12 | Static mutable state `_auditLog` and `_requestCount` shared across threads. | Use thread-safe collections or remove static state. |
| SampleBankingApp/Services/UserService.cs | 82 | String concatenation in loop for audit report. | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/EmailService.cs | 58 | `Console.WriteLine` used for logging. | Use `ILogger`. |
| SampleBankingApp/Services/AuthService.cs | 63 | MD5 hashing is insecure and slow for verification. | Use modern hashing algorithm. |
| SampleBankingApp/Controllers/UserController.cs | 40 | Try-catch block catches `Exception` and returns raw message. | Catch specific exceptions; return generic error. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 35 | `UseDeveloperExceptionPage()` enabled unconditionally. | Only enable in Development environment. |
| SampleBankingApp/Program.cs | 37 | HTTPS redirection is commented out. | Uncomment `UseHttpsRedirection()`. |
| SampleBankingApp/Program.cs | 38 | CORS allows any origin, method, and header. | Restrict to specific origins and methods. |
| SampleBankingApp/appsettings.json | 15 | Debug log level set for all namespaces in production config. | Set to Warning or Information for production. |
| SampleBankingApp/SampleBankingApp.csproj | 10 | `DebugSymbols` and `DebugType` set to full in release-like config. | Disable debug symbols for release builds. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | `Newtonsoft.Json` version 12.0.3 is outdated and vulnerable. | Update to latest stable version. |
| SampleBankingApp/SampleBankingApp.csproj | 14 | `System.Data.SqlClient` is legacy; use `Microsoft.Data.SqlClient`. | Update package reference. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create unit tests for all services. |
| SampleBankingApp/Services/TransactionService.cs | 25 | Critical financial logic (transfer, deposit) lacks tests. | Test balance updates, fee calculations, and error cases. |
| SampleBankingApp/Services/AuthService.cs | 25 | Authentication and JWT generation lack tests. | Test login success/failure, token generation, and validation. |
| SampleBankingApp/Services/UserService.cs | 25 | User CRUD and pagination lack tests. | Test pagination logic, search, and update/delete operations. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | String validation helpers lack tests. | Test email and username validation edge cases. |
| SampleBankingApp/Controllers/AuthController.cs | 10 | Controller actions lack integration tests. | Test HTTP endpoints for correct status codes and responses. |