## Review Categories

### 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 40-42, 57-63 | Hardcoded credentials in source files (`AdminBypassPassword`) | Move hardcoded credentials to a secure configuration source or environment variable. |
| DatabaseHelper.cs | 11 | Hardcoded connection string in source file | Move connection string to a secure configuration source or environment variable. |
| AuthService.cs | 68-72 | Weak cryptography (MD5) | Replace MD5 with a stronger hashing algorithm like SHA-256 or bcrypt. |
| Program.cs | 14-19 | JWT misconfiguration (`ValidateLifetime = false`) | Enable token lifetime validation to prevent replay attacks. |
| Program.cs | 23 | Open CORS policy | Limit allowed origins, methods, and headers to minimize cross-site scripting (XSS) and cross-site request forgery (CSRF) risks. |
| Program.cs | 7-8 | Developer exception pages in production | Disable `UseDeveloperExceptionPage()` in production to prevent sensitive information leakage. |
| Program.cs | 12 | HTTPS disabled | Enable HTTPS redirection or enforce it through infrastructure settings. |
| Program.cs | 32 | Debug symbols in release builds | Remove debug symbols from release builds to prevent sensitive information leakage. |
| EmailService.cs | 50-54 | Production secrets committed to source control (SMTP credentials) | Move SMTP credentials to a secure configuration source or environment variable. |

### 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserService.cs | 35 | Off-by-one error in pagination (`page * pageSize`) | Use `(page - 1) * pageSize` to correctly skip rows. |
| TransactionService.cs | 46-47 | Incorrect boundary condition (`amount <= 0` instead of `amount < 0`) | Change the condition to `amount < 0` to prevent negative transfers. |
| TransactionService.cs | 59-61 | Incorrect rates or constants (interest rate applied as 5% instead of 1%) | Correct the interest rate calculation to apply 0.05 instead of 5. |
| TransactionService.cs | 83-84 | Missing self-referential check (transferring to yourself) | Add a check to prevent transfers to the same account. |
| AuthService.cs | 91-92 | Balance or fee calculations that exclude a component (fee not included in total debit) | Include the fee in the total debit calculation. |

### 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserController.cs | 27-31, 40-45 | Methods that catch broad `Exception` and swallow it silently | Catch specific exceptions and handle them appropriately or rethrow unhandled exceptions. |
| AuthController.cs | 19-23 | Catch blocks that return empty collections (`null` user) | Return a meaningful error message or status code instead of an empty collection. |
| TransactionController.cs | 15-18, 26-29 | Operations that lack a database transaction (multiple writes) | Wrap the database operations in a transaction to ensure consistency. |
| EmailService.cs | 30-41 | Side effects (email sending) that can throw after a DB write has already committed | Move the email sending logic outside of the database transaction or handle email failures appropriately. |
| AuthController.cs | 21 | Raw `ex.Message` returned to HTTP clients | Return a generic error message instead of the raw exception message to prevent information leakage. |

### 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 16-20, 30-34, 51-57 | `SqlConnection`, `SqlDataReader`, and `SqlCommand` opened but never closed or disposed | Use `using` blocks to ensure resources are properly disposed of. |
| EmailService.cs | 20-38 | `SmtpClient` held as an instance field (not thread-safe, socket never released) | Create a new `SmtpClient` instance for each email send operation or use a thread-safe alternative. |
| EmailService.cs | 46-51 | `MailMessage` created but never disposed | Dispose of the `MailMessage` object after sending the email. |

### 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 9-10 | Configuration values read with `_config["key"]` passed directly to methods that cannot accept null (`Encoding.UTF8.GetBytes`) | Check for null or empty configuration values before using them. |
| UserService.cs | 42-43, 59-60 | `DataTable.Rows[0]` accessed without first checking `Rows.Count > 0` | Check the row count before accessing the row to prevent null reference exceptions. |
| StringHelper.cs | 37-38 | `?.Value` result passed to `int.Parse` without null guard | Add a null guard before parsing the value to prevent null reference exceptions. |
| AuthController.cs | 12-13 | Method parameters used (`.ToUpper()`, `.Length`, etc.) before a null check | Add a null check for method parameters before using them. |
| UserController.cs | 10-14, 20-25 | Model-bound request objects used in controller actions without a null check | Add a null check for model-bound request objects before using them. |

### 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 45-50 | Obsolete method (`ExecuteQueryWithParams`) that is still present | Remove the obsolete method or update it to match the current implementation. |
| TransactionService.cs | 108-110 | Unreachable code after an unconditional `return` statement | Remove the unreachable code or correct the logic to ensure the `return` statement is reached. |
| TransactionService.cs | 95-104 | `throw new NotImplementedException()` in non-stub code | Implement the missing functionality or remove the exception throw. |

### 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 12, 49, 68 | Numeric literals used inline (fee rates, deposit caps) | Define numeric constants for fee rates, deposit caps, and other magic numbers to improve readability and maintainability. |
| EmailService.cs | 10-11 | String literals for email addresses, subject lines, and body text repeated in multiple places | Define string constants for email addresses, subject lines, and body text to improve readability and maintainability. |
| AuthService.cs | 16-23 | Hardcoded SQL query strings with inline values | Use parameterized queries or stored procedures to prevent SQL injection attacks and improve performance. |
| DatabaseHelper.cs | 9-10, 51-57 | Hardcoded connection string and table names in source files | Move connection strings, table names, and other configuration values to a secure configuration source or environment variable. |

### 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 21-27 | String concatenation inside a loop (O(n²) — use `StringBuilder` or `string.Join`) | Replace string concatenation with `StringBuilder` or `string.Join` to improve performance. |
| AuthService.cs | 48-50, 76-78 | `new Regex(...)` inside a method called repeatedly (should be `static readonly`) | Make the regular expression object `static readonly` to improve performance and thread safety. |
| UserService.cs | 19-20, 32-33 | Shared mutable static state accessed from multiple threads without synchronization (`_auditLog`, `_requestCount`) | Use thread-safe data structures or synchronization mechanisms to ensure thread safety. |
| StringHelper.cs | 31-35 | Reimplementing standard library methods that already exist (`IsBlank`) | Use the existing `string.IsNullOrWhiteSpace` method instead of reimplementing it. |
| DatabaseHelper.cs | 26-34 | Helper method designed to leak resource ownership to callers with no documented contract (`GetOpenConnection`) | Document the expected usage of the helper method and ensure resources are properly disposed of by the caller. |
| UserService.cs | 79-87 | Duplicated validation logic that should be extracted to a shared method (`MapRowToUser`) | Extract the validation logic to a shared method to improve code reuse and maintainability. |

### 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 7-8 | `UseDeveloperExceptionPage()` called unconditionally | Disable `UseDeveloperExceptionPage()` in production to prevent sensitive information leakage. |
| Program.cs | 14-19 | JWT misconfiguration (`ValidateLifetime = false`) | Enable token lifetime validation to prevent replay attacks. |
| Program.cs | 12 | HTTPS redirection commented out | Enable HTTPS redirection or enforce it through infrastructure settings. |
| Program.cs | 23 | Overly permissive CORS policy (`AllowAnyOrigin()`, `AllowAnyMethod()`, `AllowAnyHeader()`) | Limit allowed origins, methods, and headers to minimize cross-site scripting (XSS) and cross-site request forgery (CSRF) risks. |
| Program.cs | 32 | Debug log levels set for production namespaces | Set appropriate log levels for production namespaces to prevent sensitive information leakage. |
| SampleBankingApp.csproj | 17-19 | Outdated or vulnerable NuGet packages (`System.Data.SqlClient`, `Newtonsoft.Json`) | Update the NuGet packages to the latest secure versions. |
| appsettings.json | N/A | Missing environment-specific config overrides (`appsettings.Production.json`) | Create environment-specific configuration files to override default settings for different environments. |

### 10. Missing Unit Tests

No test project exists. The following methods and scenarios are most critical to test:

- `AuthService.Login`: Test with valid and invalid credentials, including edge cases like empty strings and SQL injection attempts.
- `TransactionService.Transfer`: Test with positive and negative amounts, insufficient funds, and self-transfers.
- `TransactionService.Deposit`: Test with valid and invalid deposit amounts.
- `UserService.GetUserById`: Test with valid and invalid user IDs, including edge cases like zero and out-of-range values.
- `UserService.UpdateUser`: Test with valid and invalid user IDs, email addresses, and usernames.
- `UserService.DeleteUser`: Test with valid and invalid user IDs.
- `UserService.GetUsersPage`: Test with different page sizes and edge cases like zero and negative values.
- `UserService.SearchUsers`: Test with valid and invalid search queries, including edge cases like empty strings and SQL injection attempts.
- `EmailService.SendTransferNotification`: Test with valid and invalid email addresses and edge cases like empty strings and SMTP server errors.