## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/AuthService.cs | 38 | SQL Injection via string interpolation in `Login` method. | Use parameterized queries. |
| Services/AuthService.cs | 48 | Hardcoded admin backdoor password allows bypassing authentication. | Remove hardcoded credentials and backdoor logic. |
| Services/AuthService.cs | 58 | Passwords hashed using MD5, which is cryptographically broken. | Use a strong hashing algorithm like PBKDF2, bcrypt, or Argon2. |
| Services/TransactionService.cs | 43 | SQL Injection in `Transfer` method via string interpolation for UPDATE statements. | Use parameterized queries. |
| Services/TransactionService.cs | 63 | SQL Injection in `Deposit` method via string interpolation for UPDATE statement. | Use parameterized queries. |
| Services/TransactionService.cs | 86 | SQL Injection in `RecordTransaction` method via string interpolation for INSERT statement. | Use parameterized queries. |
| Services/UserService.cs | 33 | SQL Injection in `UpdateUser` method via string interpolation for UPDATE statement. | Use parameterized queries. |
| Services/UserService.cs | 45 | SQL Injection in `DeleteUser` method via string interpolation for DELETE statement. | Use parameterized queries. |
| Services/UserService.cs | 78 | SQL Injection in `SearchUsers` method via string interpolation in `ExecuteQuery`. | Use parameterized queries. |
| Data/DatabaseHelper.cs | 28 | `ExecuteQuery` accepts raw `whereClause` leading to SQL injection if used unsafely. | Deprecate or remove; enforce parameterized queries only. |
| Program.cs | 23 | JWT secret key may be empty or weak if not set via environment variables. | Validate secret key strength and presence at startup. |
| appsettings.json | 2 | Production database credentials hardcoded in source control. | Use environment variables or a secure secrets manager. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/TransactionService.cs | 38 | Balance check `fromBalance >= amount` ignores the transaction fee, allowing negative balances. | Check `fromBalance >= totalDebit` (amount + fee). |
| Services/UserService.cs | 62 | Pagination offset calculation `page * pageSize` is off-by-one for 1-based indexing. | Use `(page - 1) * pageSize`. |
| Services/AuthService.cs | 58 | Admin backdoor returns a user with `Id = 0`, which may fail downstream ID checks. | Return a valid user object or handle admin login separately. |
| Services/TransactionService.cs | 63 | Deposit interest bonus calculation `amount * 0.05m * 1` is redundant and potentially confusing. | Simplify to `amount * 0.05m` and clarify intent. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| Controllers/UserController.cs | 33 | Raw exception message returned to client in `UpdateUser` catch block. | Return generic error message; log details internally. |
| Controllers/UserController.cs | 37 | Raw exception message returned to client in `UpdateUser` general catch block. | Return generic error message; log details internally. |
| Services/UserService.cs | 80 | `SearchUsers` catches all exceptions and returns empty list, hiding errors. | Log the exception and return an error response or empty list with logging. |
| Services/EmailService.cs | 58 | `SendWelcomeEmail` swallows exceptions, failing silently. | Log the exception and consider retry logic or alerting. |
| Services/TransactionService.cs | 91 | `RefundTransaction` throws `NotImplementedException` without handling. | Implement the feature or return a proper error response. |
| Controllers/TransactionController.cs | 33 | `Refund` endpoint catches `NotImplementedException` but returns 500, misleading client. | Return 501 Not Implemented or handle gracefully. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/AuthService.cs | 42 | `SqlConnection` opened in `Login` but never closed or disposed. | Wrap connection in `using` statement. |
| Services/AuthService.cs | 44 | `SqlDataReader` created but never closed or disposed. | Wrap reader in `using` statement. |
| Data/DatabaseHelper.cs | 24 | `GetOpenConnection` returns open connection, shifting disposal responsibility to caller. | Return connection in `using` context or document disposal contract clearly. |
| Data/DatabaseHelper.cs | 42 | `ExecuteQuerySafe` opens connection but `SqlDataAdapter.Fill` may not close it on error. | Ensure connection is disposed in `finally` or use `using`. |
| Services/EmailService.cs | 20 | `SmtpClient` stored as instance field; not thread-safe and may leak sockets. | Create new `SmtpClient` per send or use a thread-safe wrapper. |
| Services/EmailService.cs | 35 | `MailMessage` not disposed after sending. | Wrap `MailMessage` in `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| Controllers/TransactionController.cs | 18 | `userIdClaim` may be null, causing `int.Parse` to throw. | Add null check before parsing. |
| Controllers/TransactionController.cs | 30 | `userIdClaim` may be null, causing `int.Parse` to throw. | Add null check before parsing. |
| Services/TransactionService.cs | 33 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check row count before access. |
| Services/TransactionService.cs | 34 | `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check row count before access. |
| Services/UserService.cs | 28 | `table.Rows[0]` accessed without checking `Rows.Count > 0` in `GetUserById`. | Check row count before access. |
| Services/UserService.cs | 70 | `table.Rows[0]` accessed without checking `Rows.Count > 0` in `IsWithinDailyLimit`. | Check row count before access. |
| Helpers/StringHelper.cs | 10 | `email.Length` called without null check in `IsValidEmail`. | Add null check. |
| Helpers/StringHelper.cs | 17 | `username.Length` called without null check in `IsValidUsername`. | Add null check. |
| Program.cs | 23 | `jwtSecret` may be null, causing `GetBytes` to throw. | Add null check or default value. |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/AuthService.cs | 78 | `HashPasswordSha1` method is never called. | Remove unused method. |
| Services/AuthService.cs | 85 | `ValidateToken` method is never called. | Remove unused method. |
| Helpers/StringHelper.cs | 28 | `JoinWithSeparator` is inefficient and likely unused if `JoinWithSeparatorFixed` exists. | Remove if unused. |
| Helpers/StringHelper.cs | 34 | `JoinWithSeparatorFixed` duplicates `string.Join`; likely unused. | Remove if unused. |
| Helpers/StringHelper.cs | 43 | `ObfuscateAccount` duplicates `MaskAccountNumber` logic; likely unused. | Remove if unused. |
| Helpers/StringHelper.cs | 51 | `ToTitleCase` is likely unused. | Remove if unused. |
| Helpers/StringHelper.cs | 57 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`; likely unused. | Remove if unused. |
| Services/TransactionService.cs | 89 | `FormatCurrency` method is never called. | Remove unused method. |
| Services/EmailService.cs | 66 | `BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml`, which is likely unused. | Remove if unused. |
| Services/EmailService.cs | 70 | `SendWelcomeEmailHtml` is likely unused. | Remove if unused. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/TransactionService.cs | 10 | `TransactionFeeRate` is hardcoded; should be configurable. | Move to configuration. |
| Services/TransactionService.cs | 11 | `MaxTransactionsPerDay` is hardcoded; should be configurable. | Move to configuration. |
| Services/TransactionService.cs | 63 | Deposit limit `1000000` is hardcoded; should be configurable. | Move to configuration. |
| Services/TransactionService.cs | 63 | Interest rate `0.05m` is hardcoded; should be configurable. | Move to configuration. |
| Services/UserService.cs | 59 | Page size limit `50` is hardcoded; should be configurable. | Move to configuration. |
| Helpers/StringHelper.cs | 10 | Email length limit `254` is hardcoded; should be configurable. | Move to configuration. |
| Helpers/StringHelper.cs | 17 | Username length limits `3` and `20` are hardcoded; should be configurable. | Move to configuration. |
| Services/AuthService.cs | 15 | Admin bypass password is hardcoded; should be removed or configured securely. | Remove or use secure configuration. |
| Services/EmailService.cs | 10 | Email subjects are hardcoded; should be configurable. | Move to configuration. |
| Services/EmailService.cs | 12 | `MaxRetries` and `SmtpTimeoutMs` are hardcoded; should be configurable. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| Helpers/StringHelper.cs | 13 | `new Regex` created on every call; should be static readonly. | Cache regex as static readonly. |
| Helpers/StringHelper.cs | 20 | `new Regex` created on every call; should be static readonly. | Cache regex as static readonly. |
| Helpers/StringHelper.cs | 28 | String concatenation in loop is O(n²); use `StringBuilder` or `string.Join`. | Use `string.Join`. |
| Services/UserService.cs | 68 | String concatenation in loop is O(n²); use `StringBuilder`. | Use `StringBuilder`. |
| Services/UserService.cs | 10 | Static mutable state `_auditLog` and `_requestCount` are not thread-safe. | Use thread-safe collections or remove static state. |
| Data/DatabaseHelper.cs | 24 | `GetOpenConnection` leaks resource ownership to caller. | Use `using` or return disposable connection. |
| Services/EmailService.cs | 20 | `SmtpClient` is not thread-safe; shared instance causes race conditions. | Create per-request or use thread-safe wrapper. |
| Services/AuthService.cs | 58 | Admin backdoor logic is mixed with normal login flow. | Separate admin authentication logic. |
| Controllers/UserController.cs | 33 | Catching specific `ArgumentException` then general `Exception` is redundant. | Simplify exception handling. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| Program.cs | 28 | `UseDeveloperExceptionPage()` enabled unconditionally. | Use only in development environment. |
| Program.cs | 30 | HTTPS redirection is commented out. | Enable HTTPS redirection. |
| Program.cs | 32 | CORS policy allows any origin, method, and header. | Restrict to specific origins and methods. |
| appsettings.json | 10 | Logging level set to `Debug` for all namespaces. | Set to `Information` or `Warning` for production. |
| SampleBankingApp.csproj | 10 | `Newtonsoft.Json` version 12.0.3 is outdated and vulnerable. | Update to latest version. |
| SampleBankingApp.csproj | 12 | `System.Data.SqlClient` is deprecated; use `Microsoft.Data.SqlClient`. | Update package. |
| Program.cs | 23 | JWT secret key may be empty if not set via environment. | Validate configuration at startup. |
| appsettings.json | 2 | Production connection string includes credentials. | Use environment variables or secrets manager. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/AuthService.cs | 30 | No tests for login logic, including SQL injection prevention and password hashing. | Add unit tests for login scenarios. |
| Services/TransactionService.cs | 20 | No tests for transfer logic, including balance checks, fee calculations, and SQL injection prevention. | Add unit tests for transfer scenarios. |
| Services/TransactionService.cs | 55 | No tests for deposit logic, including interest calculation and limits. | Add unit tests for deposit scenarios. |
| Services/UserService.cs | 20 | No tests for user CRUD operations, including SQL injection prevention. | Add unit tests for user operations. |
| Services/UserService.cs | 55 | No tests for pagination logic, including off-by-one errors. | Add unit tests for pagination. |
| Services/UserService.cs | 75 | No tests for search functionality, including SQL injection prevention. | Add unit tests for search. |
| Helpers/StringHelper.cs | 10 | No tests for string validation helpers. | Add unit tests for validation. |
| Controllers/AuthController.cs | 15 | No integration tests for login endpoint. | Add integration tests. |
| Controllers/TransactionController.cs | 15 | No integration tests for transfer and deposit endpoints. | Add integration tests. |
| Controllers/UserController.cs | 15 | No integration tests for user CRUD endpoints. | Add integration tests. |