## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 30 | SQL Injection: Username and password are interpolated directly into the SQL query string. | Use parameterized queries via `ExecuteQuerySafe` or `SqlCommand.Parameters`. |
| SampleBankingApp/Services/AuthService.cs | 45 | Hardcoded Backdoor: Admin user can bypass authentication with a hardcoded password. | Remove the hardcoded bypass logic entirely. |
| SampleBankingApp/Services/AuthService.cs | 54 | Weak Cryptography: Passwords are hashed using MD5, which is cryptographically broken. | Use a secure algorithm like PBKDF2, bcrypt, or Argon2. |
| SampleBankingApp/Services/AuthService.cs | 78 | Dead Code: Unused SHA1 hashing method exists, indicating potential confusion or legacy weak crypto. | Remove the unused `HashPasswordSha1` method. |
| SampleBankingApp/Program.cs | 28 | JWT Misconfiguration: `ValidateLifetime` is set to `false`, allowing expired tokens to be valid. | Set `ValidateLifetime` to `true` and configure a reasonable expiration time. |
| SampleBankingApp/Program.cs | 37 | Developer Exception Page: `UseDeveloperExceptionPage()` is enabled, leaking stack traces. | Wrap in `if (env.IsDevelopment())` or remove for production. |
| SampleBankingApp/Program.cs | 41 | HTTPS Disabled: HTTPS redirection is commented out, allowing unencrypted traffic. | Uncomment `app.UseHttpsRedirection()`. |
| SampleBankingApp/Program.cs | 43 | Open CORS Policy: `AllowAnyOrigin` combined with `AllowAnyMethod` creates a security risk. | Restrict origins and methods to specific, trusted values. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | SQL Injection: `ExecuteQuery` allows raw table names and where clauses to be injected. | Validate table names against a whitelist and use parameters for values. |
| SampleBankingApp/Services/TransactionService.cs | 47 | SQL Injection: `RecordTransaction` interpolates values directly into the SQL string. | Use parameterized queries for all values in `RecordTransaction`. |
| SampleBankingApp/Services/UserService.cs | 39 | SQL Injection: `UpdateUser` interpolates email and username directly into the SQL string. | Use parameterized queries for all user input fields. |
| SampleBankingApp/Services/UserService.cs | 53 | SQL Injection: `DeleteUser` interpolates the ID directly into the SQL string. | Use parameterized queries for the ID. |
| SampleBankingApp/Services/UserService.cs | 86 | SQL Injection: `SearchUsers` uses `ExecuteQuery` with a raw `LIKE` clause. | Use `ExecuteQuerySafe` with a parameter for the search term. |
| SampleBankingApp/appsettings.json | 4 | Hardcoded Credentials: Database connection string contains plaintext password. | Use environment variables or a secrets manager for credentials. |
| SampleBankingApp/appsettings.json | 10 | Hardcoded Credentials: JWT Secret Key is hardcoded in source control. | Move to environment variables or secure configuration store. |
| SampleBankingApp/appsettings.json | 18 | Hardcoded Credentials: SMTP password is hardcoded in source control. | Move to environment variables or secure configuration store. |
| SampleBankingApp/Services/AuthService.cs | 16 | Hardcoded Credentials: `AdminBypassPassword` is a hardcoded backdoor. | Remove this constant and the associated logic. |
| SampleBankingApp/Services/EmailService.cs | 24 | Weak Encryption: `EnableSsl` is set to `false` for SMTP, sending credentials in plaintext. | Set `EnableSsl` to `true` and use a secure port (e.g., 587 or 465). |
| SampleBankingApp/Services/TransactionService.cs | 63 | Broken Access Control: `RefundTransaction` is not implemented but exposed via API. | Implement the logic securely or remove the endpoint. |
| SampleBankingApp/Controllers/UserController.cs | 63 | Broken Access Control: `GetAuditLog` exposes internal audit logs to any authenticated user. | Restrict this endpoint to admin roles only. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 43 | Logic Error: Balance check compares `fromBalance >= amount` but deducts `amount + fee`. | Change check to `fromBalance >= totalDebit`. |
| SampleBankingApp/Services/TransactionService.cs | 53 | Logic Error: `RecordTransaction` is called after DB updates, risking inconsistency if email fails. | Ensure atomicity or handle email failure gracefully without rolling back DB. |
| SampleBankingApp/Services/TransactionService.cs | 60 | Logic Error: `Deposit` adds `amount + interestBonus` but `interestBonus` calculation is hardcoded to 1 year. | Clarify interest logic or make it configurable. |
| SampleBankingApp/Services/UserService.cs | 62 | Off-by-one Error: Pagination uses `page * pageSize` instead of `(page - 1) * pageSize`. | Change calculation to `(page - 1) * pageSize`. |
| SampleBankingApp/Services/UserService.cs | 22 | Logic Error: `GetUserById` throws for `id > 1000000`, which is an arbitrary and likely incorrect limit. | Remove arbitrary upper bound or make it configurable. |
| SampleBankingApp/Services/UserService.cs | 32 | Logic Error: `UpdateUser` throws for `id > 1000000`, which is an arbitrary and likely incorrect limit. | Remove arbitrary upper bound or make it configurable. |
| SampleBankingApp/Services/UserService.cs | 46 | Logic Error: `DeleteUser` throws for `id > 1000000`, which is an arbitrary and likely incorrect limit. | Remove arbitrary upper bound or make it configurable. |
| SampleBankingApp/Controllers/TransactionController.cs | 22 | Logic Error: `Transfer` does not check if `fromUserId` equals `toUserId`. | Add a check to prevent self-transfers. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Logic Error: `Deposit` does not validate if `amount` is positive before calling service. | Add validation for `amount > 0` in the controller or service. |
| SampleBankingApp/Services/TransactionService.cs | 28 | Logic Error: `Transfer` does not check if `fromUserId` equals `toUserId`. | Add a check to prevent self-transfers. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/UserController.cs | 44 | Error Handling: Returns raw `ex.Message` to the client, potentially leaking internal details. | Return a generic error message and log the full exception. |
| SampleBankingApp/Controllers/UserController.cs | 55 | Error Handling: Returns generic "An error occurred" without logging the full stack trace. | Log the full exception details before returning the generic message. |
| SampleBankingApp/Controllers/TransactionController.cs | 47 | Error Handling: Catches `NotImplementedException` and returns 500, masking the lack of implementation. | Implement the feature or return 501 Not Implemented. |
| SampleBankingApp/Services/UserService.cs | 84 | Error Handling: `SearchUsers` swallows all exceptions and returns an empty list. | Log the exception and rethrow or return a specific error response. |
| SampleBankingApp/Services/TransactionService.cs | 53 | Error Handling: Email sending failure is not handled; it throws and leaves DB state inconsistent. | Wrap email sending in a try-catch and log the failure without rolling back DB. |
| SampleBankingApp/Services/EmailService.cs | 48 | Error Handling: `SendTransferNotification` retries but logs to `Console.WriteLine` instead of a logger. | Use `ILogger` for logging instead of `Console.WriteLine`. |
| SampleBankingApp/Services/EmailService.cs | 64 | Error Handling: `SendWelcomeEmail` swallows exceptions and logs to `Console.WriteLine`. | Use `ILogger` and consider rethrowing or handling the failure gracefully. |
| SampleBankingApp/Services/AuthService.cs | 36 | Error Handling: `Login` does not handle SQL exceptions, potentially crashing the app. | Wrap database calls in try-catch blocks and log errors. |
| SampleBankingApp/Services/AuthService.cs | 82 | Error Handling: `ValidateToken` returns `true` immediately, ignoring the actual token validation logic below. | Remove the early return or implement the validation logic correctly. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 18 | Resource Leak: `GetOpenConnection` returns an open connection that the caller must close. | Return a `using` statement or ensure the caller disposes the connection. |
| SampleBankingApp/Data/DatabaseHelper.cs | 23 | Resource Leak: `ExecuteQuery` opens a connection but never closes it. | Use `using` statements for `SqlConnection` and `SqlCommand`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 40 | Resource Leak: `ExecuteNonQuery` opens a connection but relies on `Close()` which may not be called on exception. | Use `using` statements for `SqlConnection` and `SqlCommand`. |
| SampleBankingApp/Services/AuthService.cs | 29 | Resource Leak: `Login` opens a `SqlConnection` but never closes or disposes it. | Use `using` statements for `SqlConnection` and `SqlCommand`. |
| SampleBankingApp/Services/EmailService.cs | 19 | Resource Leak: `SmtpClient` is held as an instance field and never disposed. | Implement `IDisposable` on `EmailService` to dispose `SmtpClient`. |
| SampleBankingApp/Services/EmailService.cs | 35 | Resource Leak: `MailMessage` is created but never disposed. | Wrap `MailMessage` in a `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 58 | Resource Leak: `MailMessage` is created but never disposed. | Wrap `MailMessage` in a `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 72 | Resource Leak: `MailMessage` is created but never disposed. | Wrap `MailMessage` in a `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 21 | Null Reference: `userIdClaim` is force-unwrapped with `!` before parsing. | Add a null check and return 401 Unauthorized if missing. |
| SampleBankingApp/Controllers/TransactionController.cs | 33 | Null Reference: `userIdClaim` is force-unwrapped with `!` before parsing. | Add a null check and return 401 Unauthorized if missing. |
| SampleBankingApp/Services/AuthService.cs | 32 | Null Reference: `reader["Id"]` access assumes the row exists and column is not null. | Check `reader.Read()` result and handle nulls explicitly. |
| SampleBankingApp/Services/TransactionService.cs | 38 | Null Reference: `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing the first row. |
| SampleBankingApp/Services/TransactionService.cs | 41 | Null Reference: `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing the first row. |
| SampleBankingApp/Services/UserService.cs | 28 | Null Reference: `table.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing the first row. |
| SampleBankingApp/Services/UserService.cs | 96 | Null Reference: `row["Id"]` and other fields accessed without null checks. | Add null checks or use `Convert` methods that handle nulls. |
| SampleBankingApp/Program.cs | 24 | Null Reference: `jwtSecret` is force-unwrapped with `!` before use. | Add a null check and fail gracefully if the key is missing. |
| SampleBankingApp/Services/AuthService.cs | 66 | Null Reference: `_config["Jwt:SecretKey"]` is force-unwrapped with `!`. | Add a null check and fail gracefully if the key is missing. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 78 | Dead Code: `HashPasswordSha1` method is defined but never called. | Remove the unused method. |
| SampleBankingApp/Services/AuthService.cs | 82 | Dead Code: Code after `return true` in `ValidateToken` is unreachable. | Remove the unreachable code or fix the logic. |
| SampleBankingApp/Services/TransactionService.cs | 72 | Dead Code: `FormatCurrency` method is defined but never called. | Remove the unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 28 | Dead Code: `JoinWithSeparator` method is defined but never called. | Remove the unused method. |
| SampleBankingApp/Data/DatabaseHelper.cs | 53 | Dead Code: `ExecuteQueryWithParams` is marked `[Obsolete]` but still present. | Remove the obsolete method or update callers. |
| SampleBankingApp/Services/EmailService.cs | 68 | Dead Code: `BuildHtmlTemplate` method is defined but never called. | Remove the unused method. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 16 | Magic Number: `MaxTransactionsPerDay` is hardcoded as 10. | Move to configuration or a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 15 | Magic Number: `TransactionFeeRate` is hardcoded as 0.015m. | Move to configuration or a named constant. |
| SampleBankingApp/Services/UserService.cs | 22 | Magic Number: `1000000` is used as an arbitrary user ID limit. | Remove or move to configuration. |
| SampleBankingApp/Services/UserService.cs | 32 | Magic Number: `1000000` is used as an arbitrary user ID limit. | Remove or move to configuration. |
| SampleBankingApp/Services/UserService.cs | 46 | Magic Number: `1000000` is used as an arbitrary user ID limit. | Remove or move to configuration. |
| SampleBankingApp/Services/UserService.cs | 59 | Magic Number: `50` is hardcoded as the max page size. | Move to configuration or a named constant. |
| SampleBankingApp/Services/EmailService.cs | 13 | Magic Number: `MaxRetries` is hardcoded as 3. | Move to configuration or a named constant. |
| SampleBankingApp/Services/EmailService.cs | 14 | Magic Number: `SmtpTimeoutMs` is hardcoded as 5000. | Move to configuration or a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 60 | Magic Number: `0.05m` is hardcoded as interest rate. | Move to configuration or a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 60 | Magic Number: `1` is hardcoded as the interest period. | Move to configuration or a named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | Magic Number: `254` is hardcoded as max email length. | Move to a named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 17 | Magic Number: `3` and `20` are hardcoded as username length limits. | Move to named constants. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 24 | Anti-pattern: String concatenation in a loop (`result += item`) is O(n²). | Use `string.Join` or `StringBuilder`. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | Anti-pattern: `Regex` is instantiated inside the method, causing performance overhead. | Make `Regex` static and readonly. |
| SampleBankingApp/Helpers/StringHelper.cs | 19 | Anti-pattern: `Regex` is instantiated inside the method, causing performance overhead. | Make `Regex` static and readonly. |
| SampleBankingApp/Services/UserService.cs | 13 | Anti-pattern: Static mutable state (`_auditLog`, `_requestCount`) is shared across instances. | Use instance fields or a dedicated logging service. |
| SampleBankingApp/Services/UserService.cs | 74 | Anti-pattern: String concatenation in a loop (`report += entry`) is O(n²). | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/EmailService.cs | 19 | Anti-pattern: `SmtpClient` is held as an instance field, which is not thread-safe. | Create a new instance per request or use `IHttpClientFactory` pattern. |
| SampleBankingApp/Services/AuthService.cs | 16 | Anti-pattern: Hardcoded backdoor password is a severe anti-pattern. | Remove the backdoor logic. |
| SampleBankingApp/Services/TransactionService.cs | 47 | Anti-pattern: `RecordTransaction` uses string interpolation for SQL, risking injection. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 39 | Anti-pattern: `UpdateUser` uses string interpolation for SQL, risking injection. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 53 | Anti-pattern: `DeleteUser` uses string interpolation for SQL, risking injection. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 86 | Anti-pattern: `SearchUsers` uses `ExecuteQuery` with raw SQL, risking injection. | Use parameterized queries. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 28 | Configuration Issue: `ValidateLifetime` is set to `false` in JWT configuration. | Set `ValidateLifetime` to `true`. |
| SampleBankingApp/Program.cs | 37 | Configuration Issue: `UseDeveloperExceptionPage()` is called unconditionally. | Wrap in `if (env.IsDevelopment())`. |
| SampleBankingApp/Program.cs | 41 | Configuration Issue: HTTPS redirection is commented out. | Uncomment `app.UseHttpsRedirection()`. |
| SampleBankingApp/Program.cs | 43 | Configuration Issue: CORS policy allows any origin and method. | Restrict to specific origins and methods. |
| SampleBankingApp/SampleBankingApp.csproj | 10 | Configuration Issue: `DebugSymbols` and `DebugType` are set to `full` in release builds. | Set to `portable` or remove for production. |
| SampleBankingApp/SampleBankingApp.csproj | 13 | Configuration Issue: `TreatWarningsAsErrors` is set to `false`. | Set to `true` to enforce code quality. |
| SampleBankingApp/SampleBankingApp.csproj | 18 | Configuration Issue: `Newtonsoft.Json` version 12.0.3 is outdated and may have vulnerabilities. | Update to the latest stable version. |
| SampleBankingApp/appsettings.json | 4 | Configuration Issue: Production secrets are committed to `appsettings.json`. | Use environment variables or a secrets manager. |
| SampleBankingApp/appsettings.json | 10 | Configuration Issue: JWT secret is hardcoded in `appsettings.json`. | Use environment variables or a secrets manager. |
| SampleBankingApp/appsettings.json | 18 | Configuration Issue: SMTP password is hardcoded in `appsettings.json`. | Use environment variables or a secrets manager. |
| SampleBankingApp/appsettings.json | 22 | Configuration Issue: Logging level is set to `Debug` for all namespaces. | Set to `Information` or `Warning` for production. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 28 | Missing Test: `Transfer` method lacks tests for insufficient funds, self-transfer, and fee calculation. | Add unit tests for boundary conditions and financial calculations. |
| SampleBankingApp/Services/TransactionService.cs | 60 | Missing Test: `Deposit` method lacks tests for interest calculation and invalid amounts. | Add unit tests for interest logic and validation. |
| SampleBankingApp/Services/UserService.cs | 62 | Missing Test: `GetUsersPage` lacks tests for pagination logic (off-by-one errors). | Add unit tests for pagination boundaries. |
| SampleBankingApp/Services/AuthService.cs | 28 | Missing Test: `Login` method lacks tests for SQL injection, invalid credentials, and backdoor bypass. | Add unit tests for authentication flows and security. |
| SampleBankingApp/Services/UserService.cs | 86 | Missing Test: `SearchUsers` lacks tests for SQL injection and empty results. | Add unit tests for search functionality and security. |
| SampleBankingApp/Controllers/TransactionController.cs | 21 | Missing Test: `Transfer` endpoint lacks tests for missing claims and invalid user IDs. | Add integration tests for controller endpoints. |
| SampleBankingApp/Controllers/UserController.cs | 63 | Missing Test: `GetAuditLog` lacks tests for access control. | Add unit tests for role-based access control. |
| SampleBankingApp/Services/EmailService.cs | 35 | Missing Test: `SendTransferNotification` lacks tests for retry logic and failure handling. | Add unit tests for email service reliability. |
| SampleBankingApp/Services/AuthService.cs | 66 | Missing Test: `GenerateJwtToken` lacks tests for token generation and validation. | Add unit tests for JWT token lifecycle. |
| SampleBankingApp/Services/UserService.cs | 13 | Missing Test: Static state in `UserService` makes testing difficult and requires isolation. | Refactor to use instance state or dependency injection for testing. |