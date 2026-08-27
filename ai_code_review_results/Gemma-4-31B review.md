## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 32 | SQL injection via string interpolation in Login method. | Use parameterized queries. |
| AuthService.cs | 17 | Hardcoded administrative bypass password. | Remove bypass or move to secure configuration. |
| AuthService.cs | 61 | Use of weak MD5 hashing algorithm for passwords. | Use Argon2 or BCrypt. |
| AuthService.cs | 91 | Use of weak SHA1 hashing algorithm. | Use SHA256 or stronger. |
| TransactionService.cs | 47 | SQL injection via string interpolation in Transfer method. | Use parameterized queries. |
| TransactionService.cs | 48 | SQL injection via string interpolation in Transfer method. | Use parameterized queries. |
| TransactionService.cs | 71 | SQL injection via string interpolation in Deposit method. | Use parameterized queries. |
| TransactionService.cs | 89 | SQL injection via string interpolation in RecordTransaction method. | Use parameterized queries. |
| UserService.cs | 47 | SQL injection via string interpolation in UpdateUser method. | Use parameterized queries. |
| UserService.cs | 61 | SQL injection via string interpolation in DeleteUser method. | Use parameterized queries. |
| UserService.cs | 99 | SQL injection via string interpolation in SearchUsers method. | Use parameterized queries. |
| DatabaseHelper.cs | 29 | SQL injection via string interpolation in ExecuteQuery method. | Use parameterized queries. |
| DatabaseHelper.cs | 53 | SQL injection via string interpolation in ExecuteNonQuery method. | Use parameterized queries. |
| DatabaseHelper.cs | 16 | Hardcoded database credentials in fallback connection string. | Remove hardcoded credentials. |
| appsettings.json | 3 | Production database credentials committed to source control. | Use environment variables or Key Vault. |
| appsettings.json | 6 | JWT secret key committed to source control. | Use environment variables or Key Vault. |
| appsettings.json | 14 | Email password committed to source control. | Use environment variables or Key Vault. |
| Program.cs | 24 | JWT lifetime validation is disabled. | Set ValidateLifetime to true. |
| Program.cs | 38 | CORS policy allows any origin, method, and header. | Restrict to known trusted origins. |
| UserController.cs | 39 | Missing ownership check on UpdateUser endpoint. | Verify the authenticated user owns the account. |
| UserController.cs | 57 | Missing ownership check on DeleteUser endpoint. | Verify the authenticated user owns the account. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserService.cs | 72 | Pagination off-by-one error calculates skip as page * pageSize. | Use (page - 1) * pageSize. |
| TransactionService.cs | 42 | Balance check only verifies amount but deducts amount plus fee. | Check if balance is greater than or equal to totalDebit. |
| TransactionService.cs | 68 | Interest bonus calculation multiplies by 1 unnecessarily. | Remove the redundant multiplication. |
| AuthService.cs | 103 | ValidateToken returns true immediately, making validation logic unreachable. | Remove the premature return statement. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserController.cs | 50 | Broad Exception caught and raw message returned to client. | Catch specific exceptions and return generic errors. |
| UserService.cs | 105 | Broad Exception caught and swallowed, returning an empty list. | Log the exception and return a failure response. |
| TransactionService.cs | 47 | Multiple database updates performed without a transaction. | Wrap updates in a SqlTransaction. |
| TransactionService.cs | 52 | Side effect email sent before the method completes. | Move email sending after the transaction commits. |
| EmailService.cs | 75 | Broad Exception caught and written to Console. | Use a proper logging framework. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 28 | SqlConnection from GetOpenConnection is never disposed in ExecuteQuery. | Wrap the connection in a using block. |
| DatabaseHelper.cs | 52 | SqlConnection from GetOpenConnection is closed but not disposed. | Wrap the connection in a using block. |
| AuthService.cs | 34 | SqlConnection created but never closed or disposed. | Wrap the connection in a using block. |
| AuthService.cs | 37 | SqlCommand and SqlDataReader are never disposed. | Wrap both in using blocks. |
| EmailService.cs | 16 | SmtpClient held as an instance field. | Create and dispose SmtpClient per request. |
| EmailService.cs | 39 | MailMessage created but never disposed. | Wrap MailMessage in a using block. |
| EmailService.cs | 69 | MailMessage created but never disposed. | Wrap MailMessage in a using block. |
| EmailService.cs | 89 | MailMessage created but never disposed. | Wrap MailMessage in a using block. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 27 | int.Parse called on potentially null userIdClaim. | Use int.TryParse or check for null. |
| TransactionController.cs | 41 | int.Parse called on potentially null userIdClaim. | Use int.TryParse or check for null. |
| TransactionService.cs | 36 | DataTable row accessed without checking Rows.Count. | Verify Rows.Count > 0 before access. |
| TransactionService.cs | 37 | DataTable row accessed without checking Rows.Count. | Verify Rows.Count > 0 before access. |
| TransactionService.cs | 83 | DataTable row accessed without checking Rows.Count. | Verify Rows.Count > 0 before access. |
| Program.cs | 28 | Encoding.UTF8.GetBytes called on potentially null jwtSecret. | Add a null check for the secret key. |
| EmailService.cs | 24 | int.Parse called on potentially null config value. | Use int.TryParse or provide a default. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 59 | Method TableExists has no callers. | Remove the method. |
| DatabaseHelper.cs | 68 | Method ExecuteQueryWithParams has no callers. | Remove the method. |
| StringHelper.cs | 29 | Method JoinWithSeparator has no callers. | Remove the method. |
| StringHelper.cs | 38 | Method JoinWithSeparatorFixed has no callers. | Remove the method. |
| StringHelper.cs | 54 | Method ObfuscateAccount has no callers. | Remove the method. |
| StringHelper.cs | 59 | Method ToTitleCase has no callers. | Remove the method. |
| StringHelper.cs | 65 | Method IsBlank has no callers. | Remove the method. |
| AuthService.cs | 91 | Method HashPasswordSha1 has no callers. | Remove the method. |
| EmailService.cs | 63 | Method SendWelcomeEmail has no callers. | Remove the method. |
| EmailService.cs | 86 | Method SendWelcomeEmailHtml has no callers. | Remove the method. |
| TransactionService.cs | 77 | Method IsWithinDailyLimit has no callers. | Remove the method. |
| TransactionService.cs | 94 | Method FormatCurrency has no callers. | Remove the method. |
| AuthService.cs | 105 | Code after return statement is unreachable. | Remove unreachable lines. |
| TransactionService.cs | 102 | Method RefundTransaction throws NotImplementedException. | Implement the logic or remove the method. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 17 | Hardcoded admin bypass password string. | Move to secure configuration. |
| AuthService.cs | 53 | Hardcoded admin username string. | Move to configuration. |
| EmailService.cs | 40 | Hardcoded from email address. | Move to configuration. |
| EmailService.cs | 67 | Hardcoded support email address. | Move to configuration. |
| TransactionService.cs | 11 | Hardcoded transaction fee rate 0.015m. | Move to configuration. |
| TransactionService.cs | 12 | Hardcoded max transactions per day 10. | Move to configuration. |
| TransactionService.cs | 65 | Hardcoded deposit limit 1000000. | Move to configuration. |
| TransactionService.cs | 68 | Hardcoded interest bonus rate 0.05m. | Move to configuration. |
| UserService.cs | 22 | Hardcoded user ID range limit 1000000. | Move to configuration. |
| UserService.cs | 70 | Hardcoded max page size 50. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| StringHelper.cs | 33 | String concatenation used inside a loop. | Use StringBuilder. |
| StringHelper.cs | 16 | Regex object instantiated inside a method. | Use a static readonly Regex. |
| StringHelper.cs | 25 | Regex object instantiated inside a method. | Use a static readonly Regex. |
| UserService.cs | 10 | Shared mutable static list used without synchronization. | Use ConcurrentBag or locking. |
| UserService.cs | 11 | Shared mutable static integer used without synchronization. | Use Interlocked.Increment. |
| UserService.cs | 90 | String concatenation used inside a loop. | Use StringBuilder. |
| StringHelper.cs | 65 | Custom IsBlank method reimplements string.IsNullOrWhiteSpace. | Use string.IsNullOrWhiteSpace. |
| TransactionService.cs | 23 | Transfer method handles validation, DB access, and email. | Split into separate validation and notification helpers. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 34 | Developer exception page enabled unconditionally. | Wrap in an environment check. |
| Program.cs | 36 | HTTPS redirection is commented out. | Uncomment UseHttpsRedirection. |
| Program.cs | 38 | CORS policy allows any origin. | Specify allowed origins. |
| appsettings.json | 18 | Log level set to Debug for production. | Set to Information or Warning. |
| SampleBankingApp.csproj | 15 | Outdated Newtonsoft.Json version 12.0.3. | Update to latest stable version. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists in the solution. | Create a XUnit or NUnit project. |
| TransactionService.cs | 23 | Transfer logic lacks tests for insufficient funds. | Add test case for balance < totalDebit. |
| TransactionService.cs | 23 | Transfer logic lacks tests for negative amounts. | Add test case for amount < 0. |
| AuthService.cs | 28 | Login logic lacks tests for invalid credentials. | Add test case for wrong password. |
| UserService.cs | 68 | Pagination logic lacks boundary tests. | Add test cases for page 1 and empty results. |
| EmailService.cs | 46 | Email retry logic is not tested. | Mock SmtpClient to test retry loop. |