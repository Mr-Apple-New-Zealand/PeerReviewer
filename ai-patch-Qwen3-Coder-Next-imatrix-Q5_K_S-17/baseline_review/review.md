## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 38-42 | SQL Injection via string interpolation in `Login` query. | Use parameterized queries or an ORM. |
| AuthService.cs | 52-55 | Hardcoded admin backdoor password allows bypassing authentication. | Remove the hardcoded bypass logic entirely. |
| AuthService.cs | 63-67 | Passwords hashed using MD5, which is cryptographically broken. | Use a strong hashing algorithm like PBKDF2, bcrypt, or Argon2. |
| AuthService.cs | 89-93 | SHA1 used in `HashPasswordSha1`, which is cryptographically weak. | Remove unused weak hashing methods or upgrade to secure alternatives. |
| TransactionService.cs | 48-49 | SQL Injection in `Transfer` via string interpolation in `UPDATE` statements. | Use parameterized queries for all database writes. |
| TransactionService.cs | 68 | SQL Injection in `Deposit` via string interpolation in `UPDATE` statement. | Use parameterized queries for all database writes. |
| TransactionService.cs | 88-90 | SQL Injection in `RecordTransaction` via string interpolation in `INSERT` statement. | Use parameterized queries for all database writes. |
| UserService.cs | 38 | SQL Injection in `UpdateUser` via string interpolation in `UPDATE` statement. | Use parameterized queries for all database writes. |
| UserService.cs | 48 | SQL Injection in `DeleteUser` via string interpolation in `DELETE` statement. | Use parameterized queries for all database writes. |
| UserService.cs | 76 | SQL Injection in `SearchUsers` via string interpolation in `LIKE` clause. | Use parameterized queries with proper escaping for LIKE clauses. |
| DatabaseHelper.cs | 13 | Hardcoded fallback connection string with credentials in source code. | Remove hardcoded credentials; fail securely if config is missing. |
| DatabaseHelper.cs | 26 | `ExecuteQuery` allows raw SQL injection via `tableName` and `whereClause`. | Validate table names against a whitelist and use parameters for clauses. |
| Program.cs | 28 | JWT `ValidateLifetime` set to `false`, allowing expired tokens to remain valid. | Set `ValidateLifetime` to `true` and configure appropriate token expiration. |
| Program.cs | 38 | `UseDeveloperExceptionPage()` enabled, exposing stack traces in production. | Wrap in `if (app.Environment.IsDevelopment())` check. |
| Program.cs | 42 | CORS policy allows any origin, method, and header, enabling CSRF/XSS risks. | Restrict CORS to specific trusted origins and methods. |
| appsettings.json | 3 | Production database credentials committed to source control. | Use environment variables or a secure secret manager. |
| appsettings.json | 13 | JWT secret key is weak and committed to source control. | Use a strong, randomly generated key stored in secure configuration. |
| appsettings.json | 18 | SMTP credentials committed to source control. | Use environment variables or a secure secret manager. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 46 | Balance check uses `amount` but deducts `amount + fee`, allowing negative balances. | Check if `fromBalance >= totalDebit` (amount + fee). |
| TransactionService.cs | 46 | No check to prevent users from transferring funds to themselves. | Add validation to ensure `fromUserId != toUserId`. |
| UserService.cs | 62 | Pagination offset calculation `page * pageSize` is incorrect for 1-based indexing. | Use `(page - 1) * pageSize` for correct offset. |
| UserService.cs | 62 | No validation for `page < 1` or `pageSize < 1` in pagination. | Add validation to ensure positive page and page size values. |
| AuthService.cs | 52 | Admin backdoor returns a user with `Id = 0`, which may cause issues in downstream logic. | Ensure admin user has a valid, unique ID. |
| TransactionService.cs | 68 | Deposit interest bonus calculation `amount * 0.05m * 1` is redundant and unclear. | Simplify to `amount * 0.05m` and document the interest rate. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 38-41 | `Refund` endpoint catches `NotImplementedException` and returns 500, hiding implementation status. | Return 501 Not Implemented or remove the endpoint until implemented. |
| UserController.cs | 38-41 | `UpdateUser` returns raw exception messages to clients, leaking internal details. | Return generic error messages and log details server-side. |
| UserController.cs | 42-45 | `UpdateUser` catches broad `Exception` and returns raw message to clients. | Return generic error messages and log details server-side. |
| UserService.cs | 78-81 | `SearchUsers` swallows all exceptions and returns empty list, masking errors. | Log exceptions and return appropriate error response or status. |
| EmailService.cs | 58-62 | `SendWelcomeEmail` swallows exceptions, failing silently without logging. | Log exceptions and consider retry logic or notification of failure. |
| TransactionService.cs | 48-52 | Database updates in `Transfer` are not atomic; failure between updates causes inconsistency. | Wrap database operations in a transaction. |
| TransactionService.cs | 68-70 | Database update in `Deposit` is not atomic with transaction recording. | Wrap database operations in a transaction. |
| AuthService.cs | 42-48 | `Login` does not dispose `SqlConnection` or `SqlDataReader` on success or failure. | Use `using` statements or try-finally blocks to ensure disposal. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 20-23 | `GetOpenConnection` returns open connection without disposing, leaking resources. | Return connection wrapped in `using` or ensure caller disposes it. |
| DatabaseHelper.cs | 26-33 | `ExecuteQuery` does not dispose `SqlConnection`, `SqlCommand`, or `SqlDataAdapter`. | Use `using` statements for all disposable objects. |
| DatabaseHelper.cs | 48-53 | `ExecuteNonQuery` does not dispose `SqlCommand` or `SqlDataAdapter`. | Use `using` statements for all disposable objects. |
| AuthService.cs | 42-48 | `Login` does not dispose `SqlConnection` or `SqlDataReader`. | Use `using` statements for all disposable objects. |
| EmailService.cs | 18-28 | `SmtpClient` stored as instance field, not thread-safe, and never disposed. | Create `SmtpClient` per send operation or implement proper disposal. |
| EmailService.cs | 38-42 | `MailMessage` created but never disposed in `SendTransferNotification`. | Wrap `MailMessage` in `using` statement. |
| EmailService.cs | 54-58 | `MailMessage` created but never disposed in `SendWelcomeEmail`. | Wrap `MailMessage` in `using` statement. |
| EmailService.cs | 68-70 | `MailMessage` created but never disposed in `SendWelcomeEmailHtml`. | Wrap `MailMessage` in `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 22 | `int.Parse(userIdClaim!)` throws if claim is null, despite null-conditional operator. | Add null check before parsing or use `int.TryParse`. |
| TransactionController.cs | 33 | `int.Parse(userIdClaim!)` throws if claim is null, despite null-conditional operator. | Add null check before parsing or use `int.TryParse`. |
| TransactionService.cs | 40-41 | Accessing `Rows[0]` without checking `Rows.Count > 0` throws if user not found. | Check `Rows.Count > 0` before accessing rows. |
| TransactionService.cs | 44-45 | Accessing `Rows[0]` without checking `Rows.Count > 0` throws if user not found. | Check `Rows.Count > 0` before accessing rows. |
| UserService.cs | 28-32 | `GetUserById` accesses `Rows[0]` without checking `Rows.Count > 0` in some paths. | Ensure `Rows.Count > 0` check before accessing rows. |
| UserService.cs | 76 | `SearchUsers` accesses `table.Rows` without checking if query succeeded. | Validate query result before iterating rows. |
| Program.cs | 22 | `Encoding.UTF8.GetBytes(jwtSecret!)` throws if config key is null. | Add null check for JWT secret key. |
| EmailService.cs | 20 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` may throw if config value is not a valid int. | Use `int.TryParse` for safe parsing. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 89-93 | `HashPasswordSha1` is defined but never called. | Remove unused method. |
| AuthService.cs | 95-103 | `ValidateToken` has unreachable code after `return true`. | Remove unreachable code or fix logic. |
| DatabaseHelper.cs | 55-64 | `ExecuteQueryWithParams` marked `[Obsolete]` but still present. | Remove obsolete method if no longer used. |
| StringHelper.cs | 33-38 | `JoinWithSeparator` is inefficient and likely unused given `JoinWithSeparatorFixed`. | Remove unused method. |
| StringHelper.cs | 53-57 | `ObfuscateAccount` duplicates functionality of `MaskAccountNumber`. | Remove duplicate method. |
| StringHelper.cs | 59-63 | `ToTitleCase` duplicates standard library functionality. | Remove or use `System.Globalization` directly. |
| StringHelper.cs | 65-70 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove and use standard library method. |
| TransactionService.cs | 92-94 | `FormatCurrency` is defined but never called. | Remove unused method. |
| TransactionService.cs | 96-99 | `RefundTransaction` throws `NotImplementedException` and is not implemented. | Implement or remove the method. |
| EmailService.cs | 64-66 | `BuildHtmlTemplate` is private and only used by `SendWelcomeEmailHtml`. | Consider inlining or removing if not needed. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 15 | Hardcoded admin bypass password "SuperAdmin2024". | Remove hardcoded credentials. |
| TransactionService.cs | 12 | Magic number `0.015m` for transaction fee rate. | Define as named constant or configuration value. |
| TransactionService.cs | 13 | Magic number `10` for max transactions per day. | Define as named constant or configuration value. |
| TransactionService.cs | 68 | Magic number `1000000` for deposit limit. | Define as named constant or configuration value. |
| TransactionService.cs | 68 | Magic number `0.05m` for interest bonus rate. | Define as named constant or configuration value. |
| UserService.cs | 60 | Magic number `50` for max page size. | Define as named constant or configuration value. |
| UserService.cs | 15-16 | Static mutable state `_auditLog` and `_requestCount` without synchronization. | Use thread-safe collections or remove static state. |
| EmailService.cs | 10-11 | Magic strings for email subjects. | Define as named constants or configuration values. |
| EmailService.cs | 13-14 | Magic numbers for retry count and timeout. | Define as named constants or configuration values. |
| StringHelper.cs | 12 | Magic number `254` for email length limit. | Define as named constant. |
| StringHelper.cs | 20-21 | Magic numbers `3` and `20` for username length limits. | Define as named constants. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| StringHelper.cs | 33-38 | String concatenation in loop causes O(n²) performance. | Use `StringBuilder` or `string.Join`. |
| StringHelper.cs | 15-17 | `new Regex(...)` created on every call, causing performance issues. | Use `static readonly Regex` fields. |
| StringHelper.cs | 23-25 | `new Regex(...)` created on every call, causing performance issues. | Use `static readonly Regex` fields. |
| UserService.cs | 70-75 | String concatenation in loop for audit report causes O(n²) performance. | Use `StringBuilder` or `string.Join`. |
| TransactionService.cs | 48-49 | SQL queries built via string interpolation, prone to injection and errors. | Use parameterized queries or an ORM. |
| TransactionService.cs | 68 | SQL query built via string interpolation, prone to injection and errors. | Use parameterized queries or an ORM. |
| TransactionService.cs | 88-90 | SQL query built via string interpolation, prone to injection and errors. | Use parameterized queries or an ORM. |
| UserService.cs | 38 | SQL query built via string interpolation, prone to injection and errors. | Use parameterized queries or an ORM. |
| UserService.cs | 48 | SQL query built via string interpolation, prone to injection and errors. | Use parameterized queries or an ORM. |
| UserService.cs | 76 | SQL query built via string interpolation, prone to injection and errors. | Use parameterized queries or an ORM. |
| DatabaseHelper.cs | 26 | Raw SQL execution without parameterization encourages injection. | Enforce parameterized queries only. |
| Program.cs | 10 | `DatabaseHelper` registered as Singleton, but holds non-thread-safe state. | Register as Scoped or ensure thread safety. |
| EmailService.cs | 18 | `SmtpClient` stored as instance field, not thread-safe. | Create per-request or implement thread-safe access. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 38 | `UseDeveloperExceptionPage()` enabled unconditionally. | Wrap in `if (app.Environment.IsDevelopment())`. |
| Program.cs | 28 | JWT `ValidateLifetime` set to `false`. | Set to `true` and configure expiration. |
| Program.cs | 40 | HTTPS redirection commented out. | Uncomment and enable HTTPS redirection. |
| Program.cs | 42 | CORS policy allows any origin, method, and header. | Restrict to specific trusted origins and methods. |
| appsettings.json | 21-25 | Debug log levels set for production namespaces. | Set appropriate log levels for production. |
| SampleBankingApp.csproj | 12 | `Newtonsoft.Json` version 12.0.3 is outdated and vulnerable. | Update to latest stable version. |
| SampleBankingApp.csproj | 13 | `System.IdentityModel.Tokens.Jwt` version 7.0.0 may be incompatible with .NET 8. | Ensure compatibility with .NET 8 or use built-in JWT support. |
| SampleBankingApp.csproj | 8 | `DebugSymbols` and `DebugType` set for release builds. | Configure appropriately for release builds. |
| appsettings.json | 1 | Production database connection string committed to source control. | Use environment variables or secure secret manager. |
| appsettings.json | 13 | JWT secret key committed to source control. | Use environment variables or secure secret manager. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 30-58 | No tests for login logic, including SQL injection prevention and password hashing. | Add unit tests for login scenarios, including invalid inputs and security checks. |
| TransactionService.cs | 26-56 | No tests for transfer logic, including balance checks, fee calculations, and atomicity. | Add unit tests for transfer scenarios, including edge cases and error handling. |
| TransactionService.cs | 62-72 | No tests for deposit logic, including interest calculation and limits. | Add unit tests for deposit scenarios, including edge cases and error handling. |
| UserService.cs | 18-34 | No tests for user retrieval, including pagination and search functionality. | Add unit tests for user retrieval, including pagination, search, and error handling. |
| UserService.cs | 36-44 | No tests for user update and delete operations, including SQL injection prevention. | Add unit tests for update and delete scenarios, including validation and error handling. |
| DatabaseHelper.cs | 26-33 | No tests for database helper methods, including parameterized queries. | Add unit tests for database operations, including mock database interactions. |
| EmailService.cs | 36-46 | No tests for email sending, including retry logic and error handling. | Add unit tests for email sending, including mock SMTP client interactions. |
| StringHelper.cs | 11-18 | No tests for string validation methods, including edge cases. | Add unit tests for string validation, including invalid and boundary inputs. |
| Program.cs | 1-45 | No integration tests for API endpoints, including authentication and authorization. | Add integration tests for API endpoints, including auth flows and error responses. |
| TransactionController.cs | 18-26 | No tests for transfer endpoint, including authorization and input validation. | Add unit tests for controller actions, including mock service interactions. |