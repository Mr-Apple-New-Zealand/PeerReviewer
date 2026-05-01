## Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 31 | SQL injection via string interpolation in ExecuteQuery | Use parameterized queries |
| DatabaseHelper.cs | 52 | SQL injection via raw SQL string in ExecuteNonQuery | Use parameterized queries |
| AuthService.cs | 32 | SQL injection via string interpolation in Login | Use parameterized queries |
| AuthService.cs | 23 | Hardcoded administrative backdoor password | Remove bypass password and use DB roles |
| AuthService.cs | 55 | Use of broken MD5 hashing algorithm | Use BCrypt or Argon2 |
| AuthService.cs | 78 | Use of broken SHA1 hashing algorithm | Use BCrypt or Argon2 |
| UserService.cs | 46 | SQL injection via string interpolation in UpdateUser | Use parameterized queries |
| UserService.cs | 61 | SQL injection via string interpolation in DeleteUser | Use parameterized queries |
| UserService.cs | 98 | SQL injection via string interpolation in SearchUsers | Use parameterized queries |
| TransactionService.cs | 48 | SQL injection via string interpolation in Transfer | Use parameterized queries |
| TransactionService.cs | 49 | SQL injection via string interpolation in Transfer | Use parameterized queries |
| TransactionService.cs | 64 | SQL injection via string interpolation in Deposit | Use parameterized queries |
| TransactionService.cs | 84 | SQL injection via string interpolation in RecordTransaction | Use parameterized queries |
| appsettings.json | 4 | Production database credentials committed to source | Move secrets to Key Vault or User Secrets |
| appsettings.json | 8 | JWT secret key committed to source | Move secret to a secure configuration provider |
| appsettings.json | 14 | Email password committed to source | Move secret to a secure configuration provider |
| Program.cs | 36 | Overly permissive CORS policy allowing any origin | Restrict to known trusted domains |
| Program.cs | 33 | Developer exception page enabled unconditionally | Wrap in environment check for Development |
| Program.cs | 35 | HTTPS redirection is commented out | Enable UseHttpsRedirection |
| UserController.cs | 43 | Missing ownership check on UpdateUser endpoint | Verify current user ID matches target ID |
| UserController.cs | 57 | Missing ownership check on DeleteUser endpoint | Verify current user ID matches target ID |

## Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserService.cs | 74 | Pagination off-by-one error in skip calculation | Use (page - 1) * pageSize |
| TransactionService.cs | 41 | Balance check ignores the transaction fee | Check if balance is greater than or equal to amount plus fee |
| TransactionService.cs | 32 | No check to prevent transferring money to oneself | Add check to ensure fromUserId is not equal to toUserId |
| TransactionService.cs | 61 | Interest bonus calculation uses a redundant multiplier | Remove the multiplication by 1 |

## Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserService.cs | 104 | Broad Exception caught and swallowed in SearchUsers | Catch specific exceptions and log them |
| TransactionService.cs | 47 | Multiple DB writes performed without a transaction | Wrap transfer operations in a SqlTransaction |
| TransactionService.cs | 51 | Side effect email sent after DB commit without error handling | Wrap email call in try-catch or use an outbox pattern |
| UserController.cs | 52 | Internal exception message returned to HTTP client | Return a generic error message |
| AuthController.cs | 25 | No rate limiting on login endpoint | Implement rate limiting or account lockout |

## Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 24 | SqlConnection returned from GetOpenConnection is not disposed | Use using statements in calling methods |
| AuthService.cs | 35 | SqlConnection, SqlCommand, and SqlDataReader not disposed | Wrap in using statements |
| EmailService.cs | 21 | SmtpClient held as instance field and never disposed | Use using statement or IDisposable |
| EmailService.cs | 41 | MailMessage object not disposed | Wrap in using statement |
| EmailService.cs | 66 | MailMessage object not disposed | Wrap in using statement |
| EmailService.cs | 81 | MailMessage object not disposed | Wrap in using statement |

## Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 27 | Potential null reference if Jwt:SecretKey is missing | Add null check or throw descriptive exception |
| TransactionService.cs | 36 | Accessing Rows[0] without checking if table has rows | Check if Rows.Count > 0 before access |
| TransactionService.cs | 37 | Accessing Rows[0] without checking if table has rows | Check if Rows.Count > 0 before access |
| TransactionController.cs | 30 | Potential null reference when parsing userIdClaim | Use int.TryParse and handle null claim |
| TransactionController.cs | 42 | Potential null reference when parsing userIdClaim | Use int.TryParse and handle null claim |

## Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 77 | HashPasswordSha1 method is never called | Remove unused method |
| AuthService.cs | 88 | Unreachable code after return statement in ValidateToken | Remove the return true statement |
| DatabaseHelper.cs | 68 | Obsolete method ExecuteQueryWithParams still present | Remove the obsolete method |
| StringHelper.cs | 26 | JoinWithSeparator is a redundant implementation of string.Join | Remove the method |

## Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 11 | Hardcoded transaction fee rate | Move to configuration file |
| TransactionService.cs | 12 | Hardcoded daily transaction limit | Move to configuration file |
| TransactionService.cs | 61 | Hardcoded interest bonus rate | Move to configuration file |
| TransactionService.cs | 58 | Hardcoded deposit limit | Move to configuration file |
| UserService.cs | 72 | Hardcoded max page size | Move to configuration file |
| UserService.cs | 21 | Hardcoded user ID range limit | Move to configuration file |
| EmailService.cs | 42 | Hardcoded sender email address | Move to configuration file |
| AuthService.cs | 23 | Hardcoded admin username and role | Move to configuration or DB roles |

## Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| StringHelper.cs | 28 | String concatenation in loop creates O(n2) complexity | Use StringBuilder or string.Join |
| StringHelper.cs | 16 | Regex object instantiated on every method call | Use a static readonly Regex instance |
| StringHelper.cs | 21 | Regex object instantiated on every method call | Use a static readonly Regex instance |
| UserService.cs | 12 | Static shared state for audit log and request count | Use a database or thread-safe service |
| UserService.cs | 88 | String concatenation in loop for report generation | Use StringBuilder |
| StringHelper.cs | 56 | Custom IsBlank method reimplements string.IsNullOrWhiteSpace | Use string.IsNullOrWhiteSpace |

## Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 23 | JWT ValidateLifetime set to false | Set ValidateLifetime to true |
| Program.cs | 33 | Developer exception page enabled in all environments | Use app.Environment.IsDevelopment() check |
| appsettings.json | 18 | Debug log level set for production namespaces | Change log level to Information or Warning |
| SampleBankingApp.csproj | 16 | Using outdated System.Data.SqlClient package | Upgrade to Microsoft.Data.SqlClient |

## Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists in the solution | Create a XUnit or NUnit test project |
| TransactionService.cs | 31 | Transfer logic lacks tests for insufficient funds and fees | Implement boundary tests for balance |
| UserService.cs | 71 | Pagination logic lacks tests for page offsets | Implement tests for page 1 and page N |
| AuthService.cs | 30 | Login logic lacks tests for invalid credentials | Implement authentication flow tests |
| StringHelper.cs | 12 | Email and Username validation lack edge case tests | Implement tests for various invalid formats |