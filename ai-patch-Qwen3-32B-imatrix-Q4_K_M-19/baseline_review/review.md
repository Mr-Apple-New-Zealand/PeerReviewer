## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 38 | SQL injection via string interpolation in `Login` method. | Use parameterized queries. |
| SampleBankingApp/Services/AuthService.cs | 58 | Hardcoded admin backdoor password allows bypassing authentication. | Remove backdoor logic entirely. |
| SampleBankingApp/Services/AuthService.cs | 66 | MD5 used for password hashing is cryptographically broken. | Use bcrypt, Argon2, or PBKDF2. |
| SampleBankingApp/Services/TransactionService.cs | 44 | SQL injection in `Transfer` via string interpolation in `ExecuteNonQuery`. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 63 | SQL injection in `Deposit` via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 83 | SQL injection in `RecordTransaction` via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 33 | SQL injection in `UpdateUser` via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 45 | SQL injection in `DeleteUser` via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 73 | SQL injection in `SearchUsers` via `ExecuteQuery` with raw WHERE clause. | Use parameterized queries. |
| SampleBankingApp/Controllers/UserController.cs | 28 | Missing authorization check allows any authenticated user to view any user's data. | Add `[Authorize]` with ownership validation or role-based access. |
| SampleBankingApp/Controllers/UserController.cs | 42 | Missing authorization check allows any authenticated user to update any user. | Add ownership validation or admin role requirement. |
| SampleBankingApp/Controllers/UserController.cs | 56 | Missing authorization check allows any authenticated user to delete any user. | Add admin role requirement. |
| SampleBankingApp/Program.cs | 28 | JWT `ValidateLifetime` is set to `false`, allowing expired tokens to remain valid. | Set `ValidateLifetime = true`. |
| SampleBankingApp/Program.cs | 37 | `UseDeveloperExceptionPage()` is enabled unconditionally, exposing stack traces in production. | Wrap in `if (app.Environment.IsDevelopment())`. |
| SampleBankingApp/Program.cs | 41 | CORS policy allows any origin, method, and header, increasing attack surface. | Restrict to specific trusted origins. |
| SampleBankingApp/appsettings.json | 2 | Production database credentials and SMTP passwords are hardcoded in source control. | Use environment variables or secret management. |
| SampleBankingApp/Data/DatabaseHelper.cs | 15 | Fallback connection string contains hardcoded credentials. | Remove fallback or use secure config. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 40 | Balance check uses `amount` but deducts `amount + fee`, allowing negative balances. | Check `fromBalance >= totalDebit`. |
| SampleBankingApp/Services/TransactionService.cs | 40 | No check prevents a user from transferring funds to themselves. | Add `if (fromUserId == toUserId)` check. |
| SampleBankingApp/Services/UserService.cs | 63 | Pagination skip calculation uses `page * pageSize` instead of `(page - 1) * pageSize`. | Change to `(page - 1) * pageSize`. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Interest bonus calculation multiplies by `1`, making the `0.05m` rate effectively 5% instead of intended logic. | Clarify intent or remove redundant `* 1`. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/UserController.cs | 48 | `ex.Message` is returned to the client, leaking internal implementation details. | Return generic error message. |
| SampleBankingApp/Controllers/UserController.cs | 51 | `ex.Message` is returned to the client in catch block. | Return generic error message. |
| SampleBankingApp/Services/UserService.cs | 78 | `SearchUsers` catches all exceptions and returns empty list, hiding errors from caller. | Log error and rethrow or return specific error status. |
| SampleBankingApp/Services/EmailService.cs | 58 | `SendWelcomeEmail` swallows exceptions silently, failing silently on email delivery. | Log error and consider retry or alert. |
| SampleBankingApp/Services/TransactionService.cs | 44 | Database updates in `Transfer` are not wrapped in a transaction, risking partial updates. | Wrap DB operations in `SqlTransaction`. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Database update in `Deposit` is not wrapped in a transaction. | Wrap DB operations in `SqlTransaction`. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 39 | `SqlConnection` opened in `Login` is never closed or disposed. | Wrap in `using` statement. |
| SampleBankingApp/Services/AuthService.cs | 41 | `SqlDataReader` is never closed or disposed. | Wrap in `using` statement. |
| SampleBankingApp/Data/DatabaseHelper.cs | 22 | `GetOpenConnection` returns an open connection, shifting disposal responsibility to caller without guarantee. | Return `using` scope or document contract strictly. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | `ExecuteQuery` opens connection but does not close it on exception paths. | Wrap in `using` or try/finally. |
| SampleBankingApp/Data/DatabaseHelper.cs | 48 | `ExecuteNonQuery` opens connection but does not close it on exception paths. | Wrap in `using` or try/finally. |
| SampleBankingApp/Services/EmailService.cs | 18 | `SmtpClient` is held as an instance field; it is not thread-safe and may leak sockets. | Create new instance per send or use thread-safe wrapper. |
| SampleBankingApp/Services/EmailService.cs | 35 | `MailMessage` is not disposed after sending. | Wrap `MailMessage` in `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/TransactionController.cs | 20 | `userIdClaim` may be null, causing `int.Parse` to throw. | Add null check before parsing. |
| SampleBankingApp/Controllers/TransactionController.cs | 33 | `userIdClaim` may be null, causing `int.Parse` to throw. | Add null check before parsing. |
| SampleBankingApp/Services/TransactionService.cs | 36 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check count before access. |
| SampleBankingApp/Services/TransactionService.cs | 40 | `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check count before access. |
| SampleBankingApp/Services/UserService.cs | 30 | `table.Rows[0]` accessed without checking `Rows.Count > 0` in `GetUserById`. | Check count before access. |
| SampleBankingApp/Services/UserService.cs | 68 | `table.Rows[0]` accessed without checking `Rows.Count > 0` in `IsWithinDailyLimit`. | Check count before access. |
| SampleBankingApp/Program.cs | 18 | `jwtSecret` from config may be null, causing `GetBytes` to throw. | Add null check or default value. |
| SampleBankingApp/Services/EmailService.cs | 20 | `_config["Email:SmtpHost"]` may be null, causing `SmtpClient` constructor to throw. | Add null check. |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 88 | `HashPasswordSha1` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/AuthService.cs | 93 | `ValidateToken` has unreachable code after `return true`. | Remove dead code or fix logic. |
| SampleBankingApp/Helpers/StringHelper.cs | 33 | `JoinWithSeparator` is inefficient and likely unused given `JoinWithSeparatorFixed`. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 39 | `JoinWithSeparatorFixed` duplicates `string.Join` functionality. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 55 | `ObfuscateAccount` duplicates `MaskAccountNumber` logic. | Remove duplicate. |
| SampleBankingApp/Helpers/StringHelper.cs | 61 | `ToTitleCase` duplicates standard library functionality. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 67 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove if unused. |
| SampleBankingApp/Data/DatabaseHelper.cs | 56 | `ExecuteQueryWithParams` is marked `[Obsolete]` but still present. | Remove obsolete code. |
| SampleBankingApp/Services/TransactionService.cs | 88 | `FormatCurrency` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/EmailService.cs | 66 | `BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml` which is likely unused. | Verify usage or remove. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 10 | `TransactionFeeRate` (0.015m) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 11 | `MaxTransactionsPerDay` (10) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 61 | Deposit limit `1000000` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Interest rate `0.05m` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 58 | Page size limit `50` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/AuthService.cs | 15 | Admin bypass password is hardcoded. | Remove or secure in config. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | Email length limit `254` is hardcoded. | Define as constant or config. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | Username length limits `3` and `20` are hardcoded. | Define as constants. |
| SampleBankingApp/Services/EmailService.cs | 10 | Email subjects are hardcoded. | Move to configuration or resource files. |
| SampleBankingApp/Services/EmailService.cs | 13 | `MaxRetries` (3) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 14 | `SmtpTimeoutMs` (5000) is hardcoded. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 12 | `new Regex` created on every call in `IsValidEmail`. | Make `static readonly`. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | `new Regex` created on every call in `IsValidUsername`. | Make `static readonly`. |
| SampleBankingApp/Helpers/StringHelper.cs | 27 | String concatenation in loop in `JoinWithSeparator`. | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/UserService.cs | 75 | String concatenation in loop in `GetAuditReport`. | Use `StringBuilder`. |
| SampleBankingApp/Services/UserService.cs | 10 | `_auditLog` is static mutable state, causing memory leak and thread safety issues. | Use thread-safe collection or external storage. |
| SampleBankingApp/Services/UserService.cs | 11 | `_requestCount` is static mutable state, not thread-safe. | Use `Interlocked` or remove. |
| SampleBankingApp/Services/EmailService.cs | 43 | `Console.WriteLine` used for logging instead of `ILogger`. | Use injected logger. |
| SampleBankingApp/Services/EmailService.cs | 58 | `Console.WriteLine` used for logging instead of `ILogger`. | Use injected logger. |
| SampleBankingApp/Program.cs | 10 | `DatabaseHelper` registered as `Singleton` but holds non-thread-safe state or connections. | Review thread safety or use `Scoped`. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 37 | `UseDeveloperExceptionPage()` enabled unconditionally. | Wrap in `IsDevelopment` check. |
| SampleBankingApp/Program.cs | 28 | JWT `ValidateLifetime = false` disables token expiration. | Set to `true`. |
| SampleBankingApp/Program.cs | 39 | HTTPS redirection is commented out. | Uncomment and enable. |
| SampleBankingApp/Program.cs | 41 | CORS allows any origin, method, and header. | Restrict to specific origins. |
| SampleBankingApp/appsettings.json | 12 | Logging level set to `Debug` for all namespaces. | Set to `Information` or `Warning` for production. |
| SampleBankingApp/SampleBankingApp.csproj | 12 | `Newtonsoft.Json` version 12.0.3 is outdated and vulnerable. | Update to latest stable version. |
| SampleBankingApp/SampleBankingApp.csproj | 14 | `System.Data.SqlClient` is legacy; use `Microsoft.Data.SqlClient`. | Update package reference. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `DebugSymbols` and `DebugType` set to full in project file. | Remove or set via build configuration. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---|---|---|
| N/A | N/A | No test project exists. | Create test project. |
| SampleBankingApp/Services/TransactionService.cs | 25 | `Transfer` logic for balance deduction and fee calculation needs testing. | Add unit tests for success, failure, and edge cases. |
| SampleBankingApp/Services/TransactionService.cs | 58 | `Deposit` logic for interest bonus needs testing. | Add unit tests for deposit limits and interest. |
| SampleBankingApp/Services/AuthService.cs | 25 | `Login` SQL injection and backdoor bypass need security testing. | Add integration tests for auth flows. |
| SampleBankingApp/Services/UserService.cs | 55 | `GetUsersPage` pagination logic needs testing. | Add unit tests for pagination boundaries. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | Validation helpers need testing for edge cases. | Add unit tests for email/username validation. |