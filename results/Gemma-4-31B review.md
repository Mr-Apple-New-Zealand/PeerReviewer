## Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 31 | SQL injection via string interpolation in ExecuteQuery | Use parameterized queries |
| AuthService.cs | 34 | SQL injection via string interpolation in Login | Use parameterized queries |
| AuthService.cs | 58 | Weak MD5 hashing algorithm used for passwords | Use BCrypt or Argon2 |
| AuthService.cs | 21 | Hardcoded admin bypass password | Remove bypass or move to secure vault |
| TransactionService.cs | 44 | SQL injection via string interpolation in balance updates | Use parameterized queries |
| TransactionService.cs | 45 | SQL injection via string interpolation in balance updates | Use parameterized queries |
| TransactionService.cs | 79 | SQL injection via string interpolation in RecordTransaction | Use parameterized queries |
| UserService.cs | 48 | SQL injection via string interpolation in UpdateUser | Use parameterized queries |
| UserService.cs | 63 | SQL injection via string interpolation in DeleteUser | Use parameterized queries |
| UserService.cs | 98 | SQL injection via string interpolation in SearchUsers | Use parameterized queries |
| Program.cs | 25 | JWT token lifetime validation is disabled | Set ValidateLifetime to true |
| Program.cs | 37 | Overly permissive CORS policy allowing any origin | Restrict to known trusted domains |
| appsettings.json | 4 | Production database credentials stored in plain text | Use Environment Variables or Key Vault |
| appsettings.json | 10 | JWT secret key stored in plain text | Use Environment Variables or Key Vault |
| appsettings.json | 16 | Email password stored in plain text | Use Environment Variables or Key Vault |
| UserController.cs | 43 | Missing ownership check on UpdateUser endpoint | Verify current user ID matches target ID |
| UserController.cs | 57 | Missing ownership check on DeleteUser endpoint | Verify current user ID matches target ID |

## Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 40 | Balance check ignores the transaction fee | Check if balance is greater than amount plus fee |
| UserService.cs | 76 | Pagination skip calculation is off-by-one | Use (page - 1) * pageSize |
| TransactionService.cs | 63 | Redundant multiplication by 1 in interest calculation | Remove the multiplication by 1 |
| TransactionService.cs | 31 | No check to prevent transferring funds to oneself | Add check to ensure fromUserId != toUserId |

## Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserService.cs | 105 | Broad Exception caught and swallowed in SearchUsers | Catch specific exceptions and log them |
| TransactionService.cs | 44 | Multiple DB writes performed without a transaction | Wrap balance updates in a SqlTransaction |
| UserController.cs | 52 | Raw exception message returned to HTTP client | Return a generic error message |
| EmailService.cs | 86 | Broad Exception caught and only written to Console | Use a proper logging framework |

## Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 24 | SqlConnection returned by GetOpenConnection is not disposed | Use using statements in calling methods |
| DatabaseHelper.cs | 32 | SqlCommand and SqlDataAdapter not disposed in ExecuteQuery | Wrap in using statements |
| AuthService.cs | 37 | SqlConnection and SqlCommand not disposed in Login | Wrap in using statements |
| EmailService.cs | 23 | SmtpClient held as instance field and never disposed | Implement IDisposable or use a factory |
| EmailService.cs | 46 | MailMessage object not disposed | Wrap in using statement |

## Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 31 | Potential null reference when parsing userIdClaim | Add null check before calling int.Parse |
| TransactionController.cs | 43 | Potential null reference when parsing userIdClaim | Add null check before calling int.Parse |
| TransactionService.cs | 35 | Accessing Rows[0] without checking if table has rows | Check if Rows.Count > 0 first |
| TransactionService.cs | 36 | Accessing Rows[0] without checking if table has rows | Check if Rows.Count > 0 first |
| Program.cs | 28 | Potential null reference if Jwt:SecretKey is missing | Add null check or throw descriptive error |
| EmailService.cs | 25 | Potential null reference if Email:SmtpHost is missing | Add null check for configuration value |

## Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 88 | HashPasswordSha1 method is never used | Remove the method |
| AuthService.cs | 96 | Unreachable code after return statement in ValidateToken | Remove the return true statement |
| DatabaseHelper.cs | 66 | Obsolete method ExecuteQueryWithParams still present | Remove the obsolete method |
| StringHelper.cs | 26 | JoinWithSeparator is a duplicate of JoinWithSeparatorFixed | Remove the inefficient implementation |

## Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 11 | Hardcoded transaction fee rate | Move to appsettings.json |
| TransactionService.cs | 12 | Hardcoded daily transaction limit | Move to appsettings.json |
| UserService.cs | 21 | Hardcoded maximum user ID limit | Move to a named constant or config |
| UserService.cs | 74 | Hardcoded maximum page size | Move to a named constant or config |
| EmailService.cs | 48 | Hardcoded sender email address | Move to appsettings.json |

## Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| StringHelper.cs | 28 | String concatenation used inside a loop | Use StringBuilder or string.Join |
| StringHelper.cs | 14 | Regex object instantiated on every method call | Use a static readonly Regex object |
| StringHelper.cs | 19 | Regex object instantiated on every method call | Use a static readonly Regex object |
| UserService.cs | 12 | Static mutable state used in a scoped service | Move state to a database or distributed cache |
| UserService.cs | 88 | String concatenation used inside a loop | Use StringBuilder |
| StringHelper.cs | 65 | Manual implementation of IsBlank | Use string.IsNullOrWhiteSpace |

## Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 33 | Developer exception page enabled unconditionally | Wrap in if (app.Environment.IsDevelopment()) |
| Program.cs | 35 | HTTPS redirection is commented out | Uncomment app.UseHttpsRedirection() |
| appsettings.json | 20 | Log levels set to Debug for production | Change to Information or Warning |

## Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists in the solution | Create a XUnit or NUnit test project |
| TransactionService.cs | 31 | Transfer logic lacks tests for balance and fees | Add tests for insufficient funds and fee calc |
| UserService.cs | 73 | Pagination logic lacks boundary tests | Add tests for page 1 and empty results |
| AuthService.cs | 31 | Login logic lacks tests for invalid credentials | Add tests for wrong password and non-existent user |
| TransactionService.cs | 61 | Deposit logic lacks tests for amount limits | Add tests for negative and excessive deposits |