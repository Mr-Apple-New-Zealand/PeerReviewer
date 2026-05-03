## Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 33 | SQL injection via string interpolation in Login query | Use parameterized queries |
| AuthService.cs | 31 | Weak MD5 hashing algorithm used for passwords | Use BCrypt or Argon2 |
| AuthService.cs | 21 | Hardcoded admin bypass password backdoor | Remove bypass or move to secure config |
| UserService.cs | 48 | SQL injection via string interpolation in UpdateUser | Use parameterized queries |
| UserService.cs | 63 | SQL injection via string interpolation in DeleteUser | Use parameterized queries |
| UserService.cs | 98 | SQL injection via string interpolation in SearchUsers | Use parameterized queries |
| TransactionService.cs | 43 | SQL injection via string interpolation in balance updates | Use parameterized queries |
| TransactionService.cs | 64 | SQL injection via string interpolation in Deposit update | Use parameterized queries |
| TransactionService.cs | 82 | SQL injection via string interpolation in RecordTransaction | Use parameterized queries |
| DatabaseHelper.cs | 30 | SQL injection via string interpolation in ExecuteQuery | Use parameterized queries |
| DatabaseHelper.cs | 18 | Hardcoded database credentials in fallback string | Move all credentials to secure secrets manager |
| appsettings.json | 4 | Production database password stored in plain text | Use environment variables or Key Vault |
| appsettings.json | 8 | JWT secret key stored in plain text | Use environment variables or Key Vault |
| appsettings.json | 14 | Email password stored in plain text | Use environment variables or Key Vault |
| Program.cs | 38 | Overly permissive CORS policy allowing any origin | Restrict to known trusted domains |
| Program.cs | 35 | Developer exception page enabled in production | Wrap in environment check for Development |
| UserController.cs | 41 | Missing ownership check on UpdateUser endpoint | Verify current user ID matches target ID |
| UserController.cs | 56 | Missing ownership check on DeleteUser endpoint | Verify current user ID matches target ID |
| UserController.cs | 75 | Missing role authorization for GetAuditLog | Add Authorize attribute for Admin role |

## Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserService.cs | 78 | Pagination off-by-one error in skip calculation | Use (page - 1) * pageSize |
| TransactionService.cs | 38 | Balance check ignores transaction fee | Check if balance is greater than amount plus fee |
| TransactionService.cs | 34 | No check to prevent transferring funds to self | Add check to ensure fromUserId != toUserId |
| TransactionService.cs | 61 | Redundant multiplication by 1 in interest calculation | Remove the multiplication by 1 |

## Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserService.cs | 105 | Broad Exception catch swallows errors in SearchUsers | Catch specific exceptions and log them |
| TransactionService.cs | 41 | Multiple DB writes and email send lack atomicity | Wrap database operations in a TransactionScope |
| UserController.cs | 51 | Internal exception message returned to HTTP client | Return a generic error message |
| EmailService.cs | 77 | Broad Exception catch swallows errors in SendWelcomeEmail | Implement proper logging and error propagation |
| TransactionController.cs | 54 | NotImplementedException caught and returned as 500 | Implement the method or return 501 Not Implemented |

## Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 23 | SqlConnection returned by GetOpenConnection is not disposed | Use using statements in calling methods |
| AuthService.cs | 36 | SqlConnection and SqlCommand not disposed in Login | Wrap in using statements |
| EmailService.cs | 22 | SmtpClient held as field and never disposed | Implement IDisposable or use a factory |
| EmailService.cs | 44 | MailMessage object not disposed | Wrap in using statement |

## Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 27 | Potential null reference when parsing userIdClaim | Add null check before calling int.Parse |
| TransactionService.cs | 31 | Accessing Rows[0] without checking if table is empty | Check if Rows.Count > 0 before access |
| AuthService.cs | 68 | Potential null reference from config key in GenerateJwtToken | Add null guard for the secret key |
| EmailService.cs | 24 | Potential null reference from config key in SmtpClient | Add null guard for SmtpHost |
| StringHelper.cs | 11 | Potential null reference when accessing email.Length | Add null check at start of method |
| StringHelper.cs | 18 | Potential null reference when accessing username.Length | Add null check at start of method |

## Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 87 | HashPasswordSha1 method is never used | Remove the method |
| AuthService.cs | 96 | Unreachable code after return true in ValidateToken | Remove the return true statement |
| StringHelper.cs | 26 | JoinWithSeparator is a duplicate of JoinWithSeparatorFixed | Remove the redundant method |
| TransactionService.cs | 88 | FormatCurrency method is never called | Remove the method |

## Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 11 | Transaction fee rate hardcoded as literal | Move to configuration file |
| TransactionService.cs | 12 | Daily transaction limit hardcoded as literal | Move to configuration file |
| UserService.cs | 21 | User ID range limit hardcoded as 1000000 | Move to configuration file |
| UserService.cs | 76 | Max page size hardcoded as 50 | Move to configuration file |
| EmailService.cs | 45 | Notification email address hardcoded | Move to configuration file |
| TransactionService.cs | 61 | Interest bonus rate hardcoded as 0.05m | Move to configuration file |

## Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| StringHelper.cs | 28 | String concatenation in loop creates O(n2) complexity | Use StringBuilder or string.Join |
| StringHelper.cs | 14 | Regex object instantiated on every method call | Use a static readonly Regex instance |
| UserService.cs | 11 | Static mutable state used in scoped service | Move state to a database or distributed cache |
| UserService.cs | 89 | String concatenation in loop for audit report | Use StringBuilder |
| StringHelper.cs | 56 | Manual implementation of IsBlank | Use string.IsNullOrWhiteSpace |

## Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 35 | UseDeveloperExceptionPage called unconditionally | Wrap in environment check |
| Program.cs | 37 | HttpsRedirection is commented out | Uncomment UseHttpsRedirection |
| Program.cs | 26 | JWT ValidateLifetime set to false | Set ValidateLifetime to true |
| Program.cs | 38 | CORS policy allows any origin | Define a whitelist of allowed origins |
| appsettings.json | 18 | Log levels set to Debug for production | Change to Information or Warning |

## Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists in the solution | Create a XUnit or NUnit test project |
| TransactionService.cs | 23 | Transfer logic lacks tests for insufficient funds | Add test for balance < amount + fee |
| TransactionService.cs | 23 | Transfer logic lacks tests for self-transfer | Add test for fromUserId == toUserId |
| UserService.cs | 75 | GetUsersPage lacks tests for pagination boundaries | Add tests for page 1 and empty pages |
| AuthService.cs | 28 | Login lacks tests for invalid credentials | Add tests for wrong password and non-existent user |