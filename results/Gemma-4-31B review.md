## Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 33 | SQL injection via string interpolation in Login method | Use parameterized queries |
| AuthService.cs | 22 | Hardcoded administrative bypass password | Remove bypass or move to secure configuration |
| AuthService.cs | 56 | Use of MD5 for password hashing is cryptographically broken | Use Argon2 or BCrypt |
| DatabaseHelper.cs | 31 | SQL injection via string interpolation in ExecuteQuery | Use parameterized queries |
| DatabaseHelper.cs | 56 | SQL injection via string interpolation in ExecuteNonQuery | Use parameterized queries |
| UserService.cs | 47 | SQL injection via string interpolation in UpdateUser | Use parameterized queries |
| UserService.cs | 63 | SQL injection via string interpolation in DeleteUser | Use parameterized queries |
| UserService.cs | 98 | SQL injection via string interpolation in SearchUsers | Use parameterized queries |
| TransactionService.cs | 44 | SQL injection via string interpolation in balance updates | Use parameterized queries |
| TransactionService.cs | 45 | SQL injection via string interpolation in balance updates | Use parameterized queries |
| TransactionService.cs | 78 | SQL injection via string interpolation in RecordTransaction | Use parameterized queries |
| Program.cs | 25 | JWT ValidateLifetime is set to false | Set ValidateLifetime to true |
| Program.cs | 36 | CORS policy allows any origin, method, and header | Restrict to known trusted origins |
| appsettings.json | 4 | Production database credentials committed to source control | Use environment variables or Key Vault |
| appsettings.json | 8 | Weak JWT secret key committed to source control | Use a strong, randomly generated secret |
| appsettings.json | 14 | Email account password committed to source control | Use environment variables or Key Vault |
| UserController.cs | 42 | Missing ownership check on UpdateUser endpoint | Verify the authenticated user owns the account |
| UserController.cs | 57 | Missing ownership check on DeleteUser endpoint | Verify the authenticated user owns the account |

## Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 38 | Balance check ignores the transaction fee | Check if balance is greater than or equal to amount plus fee |
| UserService.cs | 76 | Pagination skip calculation is off-by-one | Use (page - 1) * pageSize |
| TransactionService.cs | 30 | No check to prevent transferring funds to the same account | Add a check to ensure fromUserId is not equal to toUserId |

## Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserService.cs | 103 | Broad Exception catch in SearchUsers swallows all errors | Catch specific exceptions and log them |
| TransactionService.cs | 44 | Multiple database writes performed without a transaction | Wrap balance updates and record in a SqlTransaction |
| UserController.cs | 52 | Raw exception message returned to the HTTP client | Return a generic error message and log the detail |
| TransactionController.cs | 54 | NotImplementedException caught and returned as 500 | Implement the method or return 501 Not Implemented |

## Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 24 | SqlConnection returned by GetOpenConnection is never disposed | Use using blocks or dispose the connection in the caller |
| DatabaseHelper.cs | 30 | SqlCommand and SqlDataAdapter not disposed in ExecuteQuery | Wrap in using blocks |
| DatabaseHelper.cs | 55 | SqlCommand not disposed in ExecuteNonQuery | Wrap in using block |
| EmailService.cs | 21 | SmtpClient held as a field is never disposed | Implement IDisposable or use a factory |
| EmailService.cs | 40 | MailMessage is IDisposable but not disposed | Wrap MailMessage in a using block |

## Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 31 | Potential null reference when parsing userIdClaim | Add a null check for the claim value |
| TransactionController.cs | 44 | Potential null reference when parsing userIdClaim | Add a null check for the claim value |
| TransactionService.cs | 32 | Accessing Rows[0] without checking if table has rows | Check if Rows.Count > 0 before access |
| TransactionService.cs | 33 | Accessing Rows[0] without checking if table has rows | Check if Rows.Count > 0 before access |
| Program.cs | 28 | Potential null reference if Jwt:SecretKey is missing | Use a guard clause or required configuration |
| EmailService.cs | 23 | Potential null reference if Email:SmtpHost is missing | Add a null check or default value |

## Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 86 | HashPasswordSha1 is never called | Remove the method |
| AuthService.cs | 93 | ValidateToken returns true immediately, making logic unreachable | Remove the early return |
| DatabaseHelper.cs | 68 | ExecuteQueryWithParams is marked Obsolete and unused | Remove the method |
| StringHelper.cs | 26 | JoinWithSeparator is a duplicate of JoinWithSeparatorFixed | Remove the inefficient implementation |

## Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 11 | Transaction fee rate hardcoded as literal | Move to a named constant or configuration |
| TransactionService.cs | 12 | Max transactions per day hardcoded as literal | Move to a named constant or configuration |
| TransactionService.cs | 61 | Interest bonus rate hardcoded as literal | Move to a named constant or configuration |
| UserService.cs | 21 | User ID upper bound hardcoded as literal | Move to a named constant or configuration |
| UserService.cs | 74 | Max page size hardcoded as literal | Move to a named constant or configuration |
| EmailService.cs | 41 | From email address hardcoded as literal | Move to configuration |

## Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserService.cs | 88 | String concatenation used in loop for audit report | Use StringBuilder |
| UserService.cs | 13 | Static mutable state used for audit log and request count | Use a database or a thread-safe singleton service |
| StringHelper.cs | 28 | String concatenation used in loop for joining items | Use string.Join or StringBuilder |
| StringHelper.cs | 15 | Regex object instantiated on every method call | Use a static readonly Regex instance |
| StringHelper.cs | 19 | Regex object instantiated on every method call | Use a static readonly Regex instance |
| StringHelper.cs | 65 | IsBlank reimplements string.IsNullOrWhiteSpace | Use string.IsNullOrWhiteSpace |

## Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 33 | UseDeveloperExceptionPage called unconditionally | Wrap in an environment check for Development |
| Program.cs | 35 | HttpsRedirection is commented out | Uncomment UseHttpsRedirection |
| appsettings.json | 18 | LogLevel set to Debug for production namespaces | Set to Information or Warning for production |
| SampleBankingApp.csproj | 18 | Newtonsoft.Json version 12.0.3 is outdated | Update to the latest stable version |

## Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists in the solution | Create a XUnit or NUnit test project |
| TransactionService.cs | 30 | Transfer logic lacks tests for insufficient funds and fees | Add tests for boundary balance conditions |
| AuthService.cs | 31 | Login logic lacks tests for invalid credentials | Add tests for failed authentication scenarios |
| UserService.cs | 75 | GetUsersPage lacks tests for pagination offsets | Add tests for page 1 and subsequent pages |
| StringHelper.cs | 12 | Email and Username validation lack edge case tests | Add tests for various invalid string formats |