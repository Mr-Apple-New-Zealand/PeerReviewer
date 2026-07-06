## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| appsettings.json | 3 | Production database credentials and SMTP passwords are hardcoded in source control. | Use environment variables or a secrets manager; remove from repo. |
| Program.cs | 28 | JWT lifetime validation is disabled (`ValidateLifetime = false`), allowing tokens to never expire. | Set `ValidateLifetime = true` and configure appropriate expiration times. |
| Program.cs | 38 | CORS policy allows any origin, method, and header, exposing the API to cross-site attacks. | Restrict CORS to specific trusted origins and methods. |
| Program.cs | 35 | HTTPS redirection is commented out, allowing unencrypted traffic in production. | Uncomment `app.UseHttpsRedirection()` and enforce HTTPS. |
| DatabaseHelper.cs | 26 | `ExecuteQuery` concatenates user input directly into SQL strings, enabling SQL injection. | Use parameterized queries exclusively; remove or deprecate this method. |
| TransactionService.cs | 48 | `ExecuteNonQuery` is called with string interpolation for `UPDATE` statements, enabling SQL injection. | Use parameterized queries via `ExecuteQuerySafe` or similar safe methods. |
| TransactionService.cs | 82 | `RecordTransaction` uses string interpolation for `INSERT` statements, enabling SQL injection. | Use parameterized queries for all data modifications. |
| UserService.cs | 38 | `UpdateUser` constructs SQL via string interpolation, enabling SQL injection. | Use parameterized queries for all data modifications. |
| UserService.cs | 50 | `DeleteUser` constructs SQL via string interpolation, enabling SQL injection. | Use parameterized queries for all data modifications. |
| UserService.cs | 88 | `SearchUsers` passes raw query input to `ExecuteQuery`, enabling SQL injection via LIKE clause. | Use parameterized queries with proper escaping for LIKE clauses. |
| AuthService.cs | 48 | Passwords are hashed using SHA-256 without salt, which is vulnerable to rainbow table attacks. | Use a dedicated password hashing algorithm like BCrypt or Argon2. |
| TransactionController.cs | 48 | `Refund` endpoint lacks ownership checks, allowing any authenticated user to refund any transaction. | Verify the requesting user owns the transaction or has admin privileges. |
| UserController.cs | 33 | `GetUser` lacks ownership checks, allowing any authenticated user to view any user's data. | Verify the requesting user matches the requested ID or has admin privileges. |
| UserController.cs | 45 | `UpdateUser` lacks ownership checks, allowing any authenticated user to update any user's data. | Verify the requesting user matches the requested ID or has admin privileges. |
| UserController.cs | 58 | `DeleteUser` lacks ownership checks, allowing any authenticated user to delete any user. | Verify the requesting user matches the requested ID or has admin privileges. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserService.cs | 73 | Pagination logic uses `page * pageSize` for skip, causing page 1 to skip the first `pageSize` records. | Use `(page - 1) * pageSize` for the skip calculation. |
| TransactionService.cs | 44 | Balance check compares `fromBalance >= amount` but deducts `amount + fee`, potentially causing negative balances. | Check if `fromBalance >= totalDebit` (amount + fee). |
| TransactionService.cs | 63 | Deposit interest calculation multiplies by `0.05m * 1`, which is redundant and confusing. | Simplify to `amount * 0.05m` or clarify the intent. |
| TransactionService.cs | 63 | Deposit interest is applied to the principal amount, not clearly defined as a bonus vs. interest rate. | Clarify business logic for deposit bonuses/interest. |
| TransactionService.cs | 28 | `Transfer` does not check if `fromUserId` equals `toUserId`, allowing self-transfers. | Add a check to prevent transfers to the same user. |
| TransactionService.cs | 36 | `Transfer` accesses `Rows[0]` without checking if the user exists, risking an exception. | Check `Rows.Count > 0` before accessing data. |
| TransactionService.cs | 37 | `Transfer` accesses `Rows[0]` for the recipient without checking existence. | Check `Rows.Count > 0` before accessing data. |
| TransactionService.cs | 72 | `IsWithinDailyLimit` is defined but never called in `Transfer` or `Deposit`. | Integrate daily limit checks into transaction flows. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserService.cs | 90 | `SearchUsers` catches all exceptions and returns an empty list, hiding errors from callers. | Log the exception and return an error response or rethrow. |
| TransactionController.cs | 49 | `Refund` catches `NotImplementedException` and returns 500, leaking implementation details. | Return a more generic "Feature not available" message or 501. |
| UserController.cs | 48 | `UpdateUser` returns `ex.Message` to the client, potentially leaking internal details. | Return a generic error message and log the details. |
| EmailService.cs | 58 | `SendWelcomeEmail` catches exceptions and prints to console, failing silently in production. | Log the error properly and consider retrying or notifying admins. |
| AuthService.cs | 85 | `ValidateToken` catches all exceptions and returns false, hiding potential validation issues. | Log specific exceptions for debugging and security monitoring. |
| TransactionService.cs | 48 | Database updates in `Transfer` are not wrapped in a transaction, risking partial updates. | Wrap balance updates and transaction recording in a database transaction. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 18 | `GetOpenConnection` returns an open connection without disposing it, leaking resources. | Use `using` statements or ensure callers dispose the connection. |
| DatabaseHelper.cs | 26 | `ExecuteQuery` opens a connection but does not dispose it or the command/adapter. | Wrap connection, command, and adapter in `using` statements. |
| DatabaseHelper.cs | 38 | `ExecuteQuerySafe` opens a connection but does not dispose the adapter. | Wrap the `SqlDataAdapter` in a `using` statement. |
| DatabaseHelper.cs | 48 | `ExecuteNonQuery` opens a connection but does not dispose the command. | Wrap the `SqlCommand` in a `using` statement. |
| DatabaseHelper.cs | 58 | `TableExists` opens a connection but does not dispose it. | Wrap the connection in a `using` statement. |
| EmailService.cs | 28 | `MailMessage` is not disposed after sending, potentially leaking resources. | Wrap `MailMessage` in a `using` statement. |
| EmailService.cs | 52 | `MailMessage` in `SendWelcomeEmail` is not disposed. | Wrap `MailMessage` in a `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 22 | `jwtSecret` is accessed without null check, risking `NullReferenceException` if config is missing. | Add null check or use `??` with a default/error handling. |
| AuthService.cs | 70 | `_config["Jwt:SecretKey"]` is accessed with `!` operator, risking null reference if missing. | Add null check or use `??` with a default/error handling. |
| AuthService.cs | 71 | `_config["Jwt:Issuer"]` and `_config["Jwt:Audience"]` are accessed without null checks. | Add null checks or use `??` with defaults. |
| EmailService.cs | 65 | `_config["Email:SmtpHost"]` is passed to `SmtpClient` constructor without null check. | Add null check or use `??` with a default. |
| EmailService.cs | 66 | `_config["Email:SmtpPort"]` is parsed without null check, risking `FormatException` if missing. | Add null check or use `??` with a default. |
| EmailService.cs | 68 | `_config["Email:Username"]` and `_config["Email:Password"]` are accessed without null checks. | Add null checks or use `??` with defaults. |
| TransactionService.cs | 36 | `fromUserTable.Rows[0]` is accessed without checking `Rows.Count`, risking exception if user not found. | Check `Rows.Count > 0` before accessing. |
| TransactionService.cs | 37 | `toUserTable.Rows[0]` is accessed without checking `Rows.Count`, risking exception if user not found. | Check `Rows.Count > 0` before accessing. |
| UserService.cs | 32 | `table.Rows[0]` is accessed without checking `Rows.Count`, risking exception if user not found. | Check `Rows.Count > 0` before accessing. |
| UserService.cs | 78 | `table.Rows` is iterated without checking if table is null or empty. | Add null/empty checks for the table. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| StringHelper.cs | 28 | `JoinWithSeparator` is a duplicate of `JoinWithSeparatorFixed` and `string.Join`. | Remove one of the duplicate methods. |
| StringHelper.cs | 32 | `JoinWithSeparatorFixed` is a duplicate of `JoinWithSeparator` and `string.Join`. | Remove one of the duplicate methods. |
| StringHelper.cs | 58 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove `IsBlank` and use `string.IsNullOrWhiteSpace` directly. |
| TransactionService.cs | 88 | `FormatCurrency` is defined but never called. | Remove the unused method. |
| TransactionService.cs | 72 | `IsWithinDailyLimit` is defined but never called. | Remove the unused method or integrate it. |
| TransactionService.cs | 92 | `RefundTransaction` throws `NotImplementedException` and is not fully implemented. | Implement the method or remove the endpoint if not needed. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 28 | `TransactionFeeRate` is hardcoded as `0.015m`. | Move to configuration or a named constant with documentation. |
| TransactionService.cs | 29 | `MaxTransactionsPerDay` is hardcoded as `10`. | Move to configuration. |
| TransactionService.cs | 63 | Deposit limit `1000000` is hardcoded. | Move to configuration or a named constant. |
| TransactionService.cs | 63 | Interest rate `0.05m` is hardcoded. | Move to configuration or a named constant. |
| UserService.cs | 70 | Page size limit `50` is hardcoded. | Move to configuration or a named constant. |
| EmailService.cs | 12 | Email subjects are hardcoded as constants. | Move to configuration or resource files for localization. |
| EmailService.cs | 28 | Sender email `notifications@company.com` is hardcoded. | Move to configuration. |
| EmailService.cs | 52 | Sender email `notifications@company.com` is hardcoded. | Move to configuration. |
| DatabaseHelper.cs | 12 | Default connection string fallback is hardcoded. | Use environment variables or configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserService.cs | 82 | `GetAuditReport` uses string concatenation in a loop, leading to O(n²) performance. | Use `StringBuilder` or `string.Join`. |
| UserService.cs | 12 | `_auditLog` and `_requestCount` are static mutable state, causing thread-safety issues. | Use thread-safe collections or remove static state. |
| DatabaseHelper.cs | 26 | `ExecuteQuery` uses string interpolation for SQL, encouraging unsafe practices. | Remove or deprecate this method; use parameterized queries only. |
| TransactionService.cs | 48 | SQL statements are constructed via string interpolation, bypassing parameterization. | Use parameterized queries exclusively. |
| UserService.cs | 38 | SQL statements are constructed via string interpolation, bypassing parameterization. | Use parameterized queries exclusively. |
| EmailService.cs | 28 | `SmtpClient` is created inside a loop, potentially causing socket exhaustion. | Reuse `SmtpClient` or ensure proper disposal. |
| Program.cs | 10 | `DatabaseHelper` is registered as `Singleton`, but it holds state (connection string) and may leak connections. | Register as `Scoped` or `Transient` if it manages connections. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 35 | `UseDeveloperExceptionPage()` is called unconditionally, exposing errors in production. | Wrap in `if (app.Environment.IsDevelopment())`. |
| Program.cs | 38 | CORS policy is overly permissive (`AllowAnyOrigin`, `AllowAnyMethod`, `AllowAnyHeader`). | Restrict to specific origins, methods, and headers. |
| Program.cs | 35 | HTTPS redirection is commented out. | Uncomment and enforce HTTPS. |
| appsettings.json | 11 | Logging level is set to `Debug` for all namespaces, which is verbose for production. | Set `Default` to `Information` or `Warning` in production. |
| SampleBankingApp.csproj | 10 | `Newtonsoft.Json` version `12.0.3` is outdated and may have vulnerabilities. | Update to the latest stable version. |
| SampleBankingApp.csproj | 11 | `System.Data.SqlClient` is deprecated; use `Microsoft.Data.SqlClient`. | Replace with `Microsoft.Data.SqlClient`. |
| appsettings.json | 3 | Production database credentials are stored in `appsettings.json`. | Use environment variables or a secrets manager. |
| appsettings.json | 15 | SMTP password is stored in `appsettings.json`. | Use environment variables or a secrets manager. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create a test project and add tests for critical logic. |
| TransactionService.cs | 28 | `Transfer` method lacks tests for balance checks, fee calculations, and SQL injection prevention. | Add unit tests mocking the database helper. |
| TransactionService.cs | 63 | `Deposit` method lacks tests for interest calculation and limits. | Add unit tests mocking the database helper. |
| UserService.cs | 70 | `GetUsersPage` lacks tests for pagination logic and boundary conditions. | Add unit tests mocking the database helper. |
| AuthService.cs | 28 | `Login` method lacks tests for authentication flow and password hashing. | Add unit tests mocking the database helper. |
| AuthService.cs | 68 | `GenerateJwtToken` lacks tests for token generation and claims. | Add unit tests for token generation. |
| StringHelper.cs | 12 | `StringHelper` methods lack tests for validation and formatting. | Add unit tests for all helper methods. |
| EmailService.cs | 28 | `EmailService` methods lack tests for email sending and retry logic. | Add unit tests mocking the SMTP client. |