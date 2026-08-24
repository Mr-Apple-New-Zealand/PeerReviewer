## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthController.cs | 22 | Login endpoint lacks rate limiting or account lockout on failed attempts. | Implement rate limiting middleware. |
| DatabaseHelper.cs | 29 | Method accepts raw whereClause string allowing SQL injection. | Use parameterized queries instead. |
| AuthService.cs | 32 | Method uses string interpolation for SQL query causing injection. | Use parameterized queries. |
| AuthService.cs | 53 | Method contains hardcoded admin bypass password. | Remove hardcoded bypass logic. |
| AuthService.cs | 63 | Method uses MD5 algorithm for password hashing. | Use bcrypt or Argon2. |
| AuthService.cs | 98 | Method returns true without validating token signature. | Implement proper token validation. |
| Program.cs | 34 | UseDeveloperExceptionPage is enabled unconditionally exposing stack traces. | Remove in production builds. |
| Program.cs | 38 | CorsPolicy allows any origin, method, and header. | Restrict to specific origins and methods. |
| Program.cs | 24 | JwtBearer configuration disables ValidateLifetime setting. | Enable ValidateLifetime. |
| appsettings.json | 3 | Database password is hardcoded in configuration file. | Use environment variables. |
| appsettings.json | 14 | Email password is hardcoded in configuration file. | Use environment variables. |
| appsettings.json | 18 | LogLevel is set to Debug for all namespaces. | Set to Information or Warning. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 42 | Method checks balance >= amount but deducts amount + fee. | Check balance >= amount + fee. |
| TransactionService.cs | 68 | Method calculates interest bonus with redundant multiplication. | Simplify interest calculation logic. |
| UserService.cs | 72 | Method calculates skip as page * pageSize instead of offset. | Use (page - 1) * pageSize. |
| UserService.cs | 70 | Method does not validate page is greater than zero. | Add validation for page parameter. |
| UserService.cs | 107 | Method returns empty list on exception instead of error. | Propagate exception to caller. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserController.cs | 48 | Method returns raw exception message to client. | Log error and return generic message. |
| UserController.cs | 67 | Method returns generic error message without details. | Log error and return standard error response. |
| UserController.cs | 107 | Method catches broad Exception and returns empty list. | Catch specific exceptions or propagate. |
| TransactionController.cs | 58 | Method catches NotImplementedException and returns 500. | Remove catch block and throw. |
| EmailService.cs | 77 | Method swallows exceptions and logs to console. | Log to file or propagate exception. |
| AuthService.cs | 103 | Method returns true without validation logic. | Implement proper validation. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 21 | Method returns SqlConnection without disposal. | Use using statement or return disposable wrapper. |
| EmailService.cs | 16 | SmtpClient is held as instance field and never disposed. | Dispose SmtpClient in using block or singleton with disposal. |
| EmailService.cs | 39 | Method creates MailMessage without disposing. | Use using statement for MailMessage. |
| EmailService.cs | 89 | Method creates MailMessage without disposing. | Use using statement for MailMessage. |
| DatabaseHelper.cs | 31 | Method creates DataTable without disposing. | Use using statement for DataTable. |
| DatabaseHelper.cs | 53 | Method creates SqlCommand without disposing. | Use using statement for SqlCommand. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 27 | Method calls int.Parse on potentially null userIdClaim. | Check for null claim before parsing. |
| TransactionController.cs | 41 | Method calls int.Parse on potentially null userIdClaim. | Check for null claim before parsing. |
| DatabaseHelper.cs | 36 | Method accesses Rows[0] without checking count. | Check Rows.Count before accessing. |
| DatabaseHelper.cs | 53 | Method accesses Rows[0] without checking count. | Check Rows.Count before accessing. |
| DatabaseHelper.cs | 83 | Method accesses Rows[0] without checking count. | Check Rows.Count before accessing. |
| UserService.cs | 34 | Method accesses Rows[0] without checking count. | Check Rows.Count before accessing. |
| UserService.cs | 101 | Method accesses Rows without checking count. | Check Rows.Count before accessing. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 91 | Method is defined but never called by any code. | Remove unused method. |
| StringHelper.cs | 29 | Method is defined but JoinWithSeparatorFixed exists. | Remove JoinWithSeparator or mark as obsolete. |
| TransactionService.cs | 99 | Method throws NotImplementedException. | Implement functionality or remove method. |
| AuthService.cs | 103 | Method contains unreachable code after return. | Remove unreachable code block. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 11 | TransactionFeeRate is hardcoded as 0.015m. | Move to configuration or named constant. |
| TransactionService.cs | 68 | Interest rate is hardcoded as 0.05m. | Move to configuration or named constant. |
| EmailService.cs | 14 | SmtpTimeoutMs is hardcoded as 5000. | Move to configuration. |
| EmailService.cs | 13 | MaxRetries is hardcoded as 3. | Move to configuration. |
| UserService.cs | 70 | Max pageSize is hardcoded as 50. | Move to configuration. |
| DatabaseHelper.cs | 16 | Fallback connection string is hardcoded. | Remove fallback or use config. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| StringHelper.cs | 32 | Method uses string concatenation in loop. | Use StringBuilder or string.Join. |
| StringHelper.cs | 16 | Method creates new Regex instance every call. | Make Regex static readonly. |
| StringHelper.cs | 25 | Method creates new Regex instance every call. | Make Regex static readonly. |
| EmailService.cs | 36 | Method uses string concatenation for body. | Use StringBuilder or string interpolation. |
| EmailService.cs | 83 | Method uses string concatenation for body. | Use StringBuilder or string interpolation. |
| DatabaseHelper.cs | 29 | Method uses string concatenation for SQL. | Use parameterized queries. |
| DatabaseHelper.cs | 90 | Method uses string concatenation for SQL. | Use parameterized queries. |
| UserService.cs | 90 | Method uses string concatenation in loop. | Use StringBuilder or string.Join. |
| UserService.cs | 10 | Static mutable state is used for audit log. | Use thread-safe collection or remove static. |
| AuthService.cs | 103 | Method has unreachable code after return. | Remove unreachable code block. |
| TransactionService.cs | 47 | Method performs multiple DB operations without transaction. | Wrap in database transaction. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 34 | UseDeveloperExceptionPage is called unconditionally. | Remove in production. |
| Program.cs | 36 | UseHttpsRedirection is commented out. | Uncomment for security. |
| Program.cs | 38 | CorsPolicy allows any origin and method. | Restrict to specific origins. |
| Program.cs | 24 | Configuration disables ValidateLifetime setting. | Enable ValidateLifetime. |
| appsettings.json | 3 | Database password is hardcoded. | Use environment variables. |
| appsettings.json | 14 | Email password is hardcoded. | Use environment variables. |
| appsettings.json | 18 | LogLevel is set to Debug. | Set to Information or Warning. |
| SampleBankingApp.csproj | 8 | DebugSymbols is set to true. | Set to false for release. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp | N/A | No test project exists in the repository. | Create a test project. |
| AuthService.cs | 28 | Login needs tests for SQL injection and admin bypass. | Add unit tests. |
| TransactionService.cs | 23 | Transfer needs tests for fee calculation and balance checks. | Add unit tests. |
| UserService.cs | 68 | GetUsersPage needs tests for pagination logic. | Add unit tests. |
| DatabaseHelper.cs | 26 | ExecuteQuery needs tests for SQL injection. | Add unit tests. |