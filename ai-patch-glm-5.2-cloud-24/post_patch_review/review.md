## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 15 | Hardcoded fallback database credentials in source code. | Remove hardcoded credentials and require configuration. |
| AuthService.cs | 56 | Passwords hashed with unsalted SHA-256, which is cryptographically weak for storage. | Use a dedicated password hashing library like BCrypt or Argon2. |
| TransactionController.cs | 58 | Refund endpoint lacks authorization checks, allowing any authenticated user to trigger refunds. | Add `[Authorize]` and validate ownership or admin rights. |
| UserController.cs | 58 | `UpdateUser` allows updating any user if the caller is Admin, but lacks audit logging for privilege escalation. | Ensure all privileged updates are logged and validated strictly. |
| Program.cs | 46 | CORS policy allows any method and header, which increases attack surface. | Restrict allowed methods and headers to only those required. |
| EmailService.cs | 68 | SMTP credentials read from config without validation, potentially allowing empty credentials. | Validate SMTP credentials are present before creating client. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 108 | `Deposit` method adds interest bonus to balance but records only the base amount in transaction log. | Record the total deposited amount including interest or clarify accounting logic. |
| TransactionService.cs | 108 | `Deposit` method does not check for daily transaction limits or sufficient funds (though deposits usually don't need funds). | Ensure deposit logic aligns with business rules for limits. |
| UserService.cs | 85 | `SearchUsers` uses `LIKE @Query` with `%{query}%`, which is vulnerable to SQL injection if not parameterized correctly (though parameters are used, the pattern is constructed in code). | Ensure the parameter is passed correctly without concatenation. |
| AuthService.cs | 23 | `Login` method returns user object including balance, which might expose sensitive data. | Consider returning only necessary claims or tokens. |
| TransactionService.cs | 45 | `Transfer` method checks balance before deducting fee, but race conditions could occur without proper locking. | Use database-level locking or transactions to prevent race conditions. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 60 | `Refund` endpoint catches `NotImplementedException` and returns 500, which is misleading. | Return a more appropriate status code like 501 Not Implemented. |
| UserController.cs | 68 | `UpdateUser` catches `Exception` and returns generic error message, hiding specific issues. | Log detailed errors and return user-friendly messages. |
| EmailService.cs | 45 | `SendTransferNotification` swallows `SmtpException` after retries, potentially losing critical notifications. | Log failures and consider retrying with exponential backoff. |
| TransactionService.cs | 95 | `Transfer` method swallows email notification exceptions, which might hide delivery issues. | Log email failures for monitoring and alerting. |
| AuthService.cs | 85 | `ValidateToken` does not validate issuer or audience, only expiration. | Validate all token claims including issuer and audience. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 75 | `SqlConnection` opened but not disposed if an exception occurs before `using` block ends. | Ensure `SqlConnection` is disposed in all paths, including exceptions. |
| DatabaseHelper.cs | 22 | `SqlConnection` opened but not explicitly closed if `ExecuteQuerySafe` throws. | Use `using` statement for `SqlConnection` to ensure disposal. |
| EmailService.cs | 65 | `SmtpClient` created but not disposed if `Send` throws. | Use `using` statement for `SmtpClient`. |
| TransactionService.cs | 75 | `SqlTransaction` not disposed if an exception occurs. | Use `using` statement for `SqlTransaction`. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 28 | `table.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing rows. |
| UserService.cs | 35 | `table.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing rows. |
| TransactionService.cs | 48 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing rows. |
| TransactionService.cs | 51 | `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing rows. |
| EmailService.cs | 35 | `toEmail` parameter not validated for null or empty. | Validate `toEmail` before sending. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 115 | `RefundTransaction` method throws `NotImplementedException` and is not fully implemented. | Implement the method or remove it if not needed. |
| StringHelper.cs | 35 | `JoinWithSeparator` method duplicates `string.Join` functionality. | Remove redundant method. |
| UserService.cs | 10 | `_auditLog` and `_requestCount` are instance fields but not used effectively for auditing. | Consider using a proper logging framework instead. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 10 | `TransactionFeeRate`, `MaxTransactionsPerDay`, etc., are hardcoded constants. | Move to configuration files. |
| EmailService.cs | 10 | `TransferSubject`, `WelcomeSubject`, etc., are hardcoded strings. | Move to configuration files. |
| UserService.cs | 10 | `MaxUserId`, `MaxPageSize` are hardcoded constants. | Move to configuration files. |
| AuthService.cs | 80 | Token expiry is hardcoded to 30 days. | Move to configuration files. |
| Program.cs | 15 | JWT secret key validation is hardcoded. | Ensure configuration is validated at startup. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 75 | Manual transaction management with `SqlConnection` and `SqlCommand`. | Use an ORM or higher-level abstraction for database operations. |
| DatabaseHelper.cs | 22 | Raw SQL queries with parameters are used, which is error-prone. | Consider using an ORM or parameterized query builder. |
| EmailService.cs | 45 | Retry logic is implemented manually with a loop. | Use a retry policy library like Polly. |
| UserService.cs | 85 | `SearchUsers` uses `LIKE` with `%` wildcards, which can be inefficient. | Consider using full-text search or indexing. |
| AuthService.cs | 56 | Password hashing is implemented manually. | Use a dedicated password hashing library. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 30 | `UseDeveloperExceptionPage()` is used in development, which is correct, but ensure it's not enabled in production. | Ensure environment-specific configurations are applied. |
| Program.cs | 46 | CORS policy allows any method and header, which is overly permissive. | Restrict allowed methods and headers. |
| appsettings.json | 1 | Connection string contains placeholder `__SET_VIA_ENV__`, which might not be replaced in all environments. | Ensure environment variables are set correctly. |
| Program.cs | 15 | JWT secret key is read from configuration, but not validated for strength. | Validate JWT secret key strength. |
| SampleBankingApp.csproj | 10 | `TreatWarningsAsErrors` is set to `false`, which might hide potential issues. | Set to `true` to enforce stricter compilation. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 23 | `Login` method lacks unit tests for valid and invalid credentials. | Add unit tests for login scenarios. |
| TransactionService.cs | 30 | `Transfer` method lacks unit tests for successful and failed transfers. | Add unit tests for transfer scenarios. |
| UserService.cs | 25 | `GetUserById` method lacks unit tests for existing and non-existing users. | Add unit tests for user retrieval. |
| EmailService.cs | 30 | `SendTransferNotification` method lacks unit tests for email sending. | Add unit tests for email sending scenarios. |
| DatabaseHelper.cs | 22 | `ExecuteQuerySafe` method lacks unit tests for query execution. | Add unit tests for database helper methods. |