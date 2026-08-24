## Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 32 | SQL injection via string interpolation in Login method. | Use parameterized queries. |
| AuthService.cs | 17 | Hardcoded administrative bypass password. | Remove bypass and use secure identity management. |
| AuthService.cs | 61 | Use of weak MD5 hashing algorithm for passwords. | Use Argon2 or BCrypt. |
| AuthService.cs | 91 | Use of weak SHA1 hashing algorithm for passwords. | Use Argon2 or BCrypt. |
| TransactionService.cs | 47 | SQL injection via interpolation in Transfer update. | Use parameterized queries. |
| TransactionService.cs | 48 | SQL injection via interpolation in Transfer update. | Use parameterized queries. |
| TransactionService.cs | 71 | SQL injection via interpolation in Deposit update. | Use parameterized queries. |
| TransactionService.cs | 89 | SQL injection via interpolation in RecordTransaction. | Use parameterized queries. |
| UserService.cs | 47 | SQL injection via interpolation in UpdateUser. | Use parameterized queries. |
| UserService.cs | 61 | SQL injection via interpolation in DeleteUser. | Use parameterized queries. |
| UserService.cs | 99 | SQL injection via interpolation in SearchUsers. | Use parameterized queries. |
| DatabaseHelper.cs | 29 | SQL injection via interpolation in ExecuteQuery. | Use parameterized queries. |
| DatabaseHelper.cs | 53 | SQL injection via interpolation in ExecuteNonQuery. | Use parameterized queries. |
| DatabaseHelper.cs | 16 | Hardcoded database credentials in fallback connection string. | Move credentials to a secure secret manager. |
| appsettings.json | 3 | Production database credentials stored in plain text. | Use environment variables or Azure Key Vault. |
| appsettings.json | 6 | Weak JWT secret key used for signing. | Use a long, random cryptographically secure key. |
| appsettings.json | 14 | Email account password stored in plain text. | Use a secure secret manager. |
| Program.cs | 24 | JWT lifetime validation is disabled. | Set ValidateLifetime to true. |
| Program.cs | 38 | CORS policy allows any origin. | Restrict to known trusted domains. |
| UserController.cs | 39 | Missing ownership check on UpdateUser endpoint. | Verify the authenticated user owns the account being updated. |
| UserController.cs | 57 | Missing ownership check on DeleteUser endpoint. | Verify the authenticated user has permission to delete the account. |

## Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 42 | Balance check only verifies amount but deducts amount plus fee. | Check if balance is greater than or equal to totalDebit. |
| UserService.cs | 72 | Pagination skip calculation is off-by-one. | Use (page - 1) * pageSize. |
| TransactionService.cs | 68 | Interest bonus calculation contains a redundant multiplication by 1. | Remove the multiplication by 1. |
| AuthService.cs | 53 | Admin bypass allows login without verifying account status in DB. | Remove the hardcoded bypass logic. |

## Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserService.cs | 105 | Broad Exception catch swallows errors and returns empty list. | Catch specific exceptions and log the error. |
| TransactionService.cs | 47 | Multiple database writes in Transfer are not wrapped in a transaction. | Use SqlTransaction to ensure atomicity. |
| TransactionService.cs | 52 | Email notification is sent after DB commit and may fail. | Move email sending to a background queue after transaction commit. |
| UserController.cs | 52 | Raw exception message is returned to the HTTP client. | Return a generic error message and log the details. |
| UserController.cs | 48 | Raw exception message is returned to the HTTP client. | Return a generic error message and log the details. |

## Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 28 | SqlConnection from GetOpenConnection is never disposed in ExecuteQuery. | Wrap the connection in a using block. |
| DatabaseHelper.cs | 52 | SqlConnection from GetOpenConnection is closed but not disposed. | Wrap the connection in a using block. |
| AuthService.cs | 34 | SqlConnection is opened but never closed or disposed. | Wrap the connection in a using block. |
| AuthService.cs | 37 | SqlCommand is created but not disposed. | Wrap the command in a using block. |
| AuthService.cs | 38 | SqlDataReader is created but not disposed. | Wrap the reader in a using block. |
| EmailService.cs | 16 | SmtpClient held as instance field is not thread-safe and not disposed. | Create and dispose SmtpClient per request. |
| EmailService.cs | 39 | MailMessage is created but not disposed. | Wrap the message in a using block. |
| EmailService.cs | 69 | MailMessage is created but not disposed. | Wrap the message in a using block. |
| EmailService.cs | 89 | MailMessage is created but not disposed. | Wrap the message in a using block. |

## Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 27 | Parse will throw if NameIdentifier claim is missing. | Use TryParse and return Unauthorized if missing. |
| TransactionController.cs | 41 | Parse will throw if NameIdentifier claim is missing. | Use TryParse and return Unauthorized if missing. |
| TransactionService.cs | 36 | Accesses Rows[0] without checking if the table has rows. | Check if Rows.Count > 0 before access. |
| TransactionService.cs | 37 | Accesses Rows[0] without checking if the table has rows. | Check if Rows.Count > 0 before access. |
| TransactionService.cs | 83 | Accesses Rows[0] without checking if the table has rows. | Check if Rows.Count > 0 before access. |
| Program.cs | 28 | GetBytes will throw if Jwt:SecretKey is missing from config. | Add a null check or throw a descriptive configuration exception. |
| EmailService.cs | 22 | SmtpHost configuration value may be null. | Add a null check for the configuration value. |

## Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 59 | TableExists method is never called. | Remove the method. |
| DatabaseHelper.cs | 68 | ExecuteQueryWithParams method is never called. | Remove the method. |
| StringHelper.cs | 11 | IsValidEmail method is never called. | Remove the method. |
| StringHelper.cs | 20 | IsValidUsername method is never called. | Remove the method. |
| StringHelper.cs | 29 | JoinWithSeparator method is never called. | Remove the method. |
| StringHelper.cs | 38 | JoinWithSeparatorFixed method is never called. | Remove the method. |
| StringHelper.cs | 43 | MaskAccountNumber method is never called. | Remove the method. |
| StringHelper.cs | 54 | ObfuscateAccount method is never called. | Remove the method. |
| StringHelper.cs | 59 | ToTitleCase method is never called. | Remove the method. |
| StringHelper.cs | 65 | IsBlank method is never called. | Remove the method. |
| AuthService.cs | 91 | HashPasswordSha1 method is never called. | Remove the method. |
| AuthService.cs | 98 | ValidateToken method is never called. | Remove the method. |
| EmailService.cs | 63 | SendWelcomeEmail method is never called. | Remove the method. |
| EmailService.cs | 86 | SendWelcomeEmailHtml method is never called. | Remove the method. |
| TransactionService.cs | 77 | IsWithinDailyLimit method is never called. | Remove the method. |
| TransactionService.cs | 94 | FormatCurrency method is never called. | Remove the method. |
| TransactionService.cs | 102 | RefundTransaction throws NotImplementedException in production code. | Implement the logic or remove the endpoint. |

## Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 11 | Hardcoded fee rate 0.015m. | Move to configuration. |
| TransactionService.cs | 12 | Hardcoded daily limit 10. | Move to configuration. |
| TransactionService.cs | 65 | Hardcoded deposit cap 1000000. | Move to configuration. |
| TransactionService.cs | 68 | Hardcoded interest bonus 0.05m. | Move to configuration. |
| UserService.cs | 22 | Hardcoded ID range limit 1000000. | Move to a named constant. |
| UserService.cs | 43 | Hardcoded ID range limit 1000000. | Move to a named constant. |
| UserService.cs | 57 | Hardcoded ID range limit 1000000. | Move to a named constant. |
| UserService.cs | 70 | Hardcoded page size limit 50. | Move to configuration. |
| EmailService.cs | 40 | Hardcoded sender email address. | Move to configuration. |
| EmailService.cs | 67 | Hardcoded support email address. | Move to configuration. |
| EmailService.cs | 69 | Hardcoded sender email address. | Move to configuration. |
| EmailService.cs | 89 | Hardcoded sender email address. | Move to configuration. |

## Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| StringHelper.cs | 33 | String concatenation inside a loop. | Use StringBuilder or string.Join. |
| StringHelper.cs | 16 | Regex object instantiated inside a method. | Use a static readonly Regex. |
| StringHelper.cs | 25 | Regex object instantiated inside a method. | Use a static readonly Regex. |
| UserService.cs | 10 | Shared mutable static state in _auditLog. | Use a thread-safe collection or a database. |
| UserService.cs | 11 | Shared mutable static state in _requestCount. | Use Interlocked.Increment. |
| UserService.cs | 90 | String concatenation inside a loop. | Use StringBuilder. |
| StringHelper.cs | 65 | IsBlank reimplements string.IsNullOrWhiteSpace. | Use string.IsNullOrWhiteSpace. |
| TransactionService.cs | 23 | Transfer method has too many responsibilities. | Split into validation, processing, and notification helpers. |

## Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 34 | Developer exception page enabled unconditionally. | Wrap in an environment check for Development. |
| Program.cs | 36 | HTTPS redirection is commented out. | Enable UseHttpsRedirection. |
| Program.cs | 38 | CORS policy allows any origin. | Define a specific allowed origins list. |
| appsettings.json | 18 | Log level set to Debug for production. | Set to Information or Warning for production. |
| SampleBankingApp.csproj | 15 | Outdated Newtonsoft.Json version 12.0.3. | Update to the latest stable version. |

## Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists in the solution. | Create a XUnit or NUnit test project. |
| TransactionService.cs | 23 | Transfer method lacks tests for insufficient funds. | Add test case for balance < totalDebit. |
| TransactionService.cs | 23 | Transfer method lacks tests for fee calculation. | Add test case verifying total debit amount. |
| UserService.cs | 68 | GetUsersPage lacks tests for pagination boundaries. | Add test cases for page 1 and empty pages. |
| AuthService.cs | 28 | Login method lacks tests for invalid credentials. | Add test case for incorrect password. |
| TransactionService.cs | 63 | Deposit method lacks tests for maximum limit. | Add test case for amount > 1000000. |