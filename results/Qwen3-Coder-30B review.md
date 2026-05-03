## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 14 | Login method uses string interpolation in SQL query | Use parameterized queries for all SQL operations |
| SampleBankingApp/Services/AuthService.cs | 29 | SQL injection vulnerability in Login method | Replace string interpolation with parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 34 | SQL injection in Transfer method | Use parameterized queries for all SQL operations |
| SampleBankingApp/Services/TransactionService.cs | 52 | SQL injection in RecordTransaction method | Use parameterized queries for all SQL operations |
| SampleBankingApp/Services/UserService.cs | 34 | SQL injection in UpdateUser method | Use parameterized queries for all SQL operations |
| SampleBankingApp/Services/UserService.cs | 45 | SQL injection in DeleteUser method | Use parameterized queries for all SQL operations |
| SampleBankingApp/Services/UserService.cs | 57 | SQL injection in SearchUsers method | Use parameterized queries for all SQL operations |
| SampleBankingApp/Program.cs | 25 | Hardcoded JWT secret key in appsettings.json | Move secret to secure environment variable |
| SampleBankingApp/Program.cs | 29 | Hardcoded email password in appsettings.json | Move password to secure environment variable |
| SampleBankingApp/Services/AuthService.cs | 18 | Hardcoded admin bypass password | Remove or secure this bypass mechanism |
| SampleBankingApp/Services/AuthService.cs | 37 | Uses MD5 hashing for passwords | Replace with bcrypt or PBKDF2 |
| SampleBankingApp/Services/AuthService.cs | 47 | JWT ValidateLifetime set to false | Enable lifetime validation |
| SampleBankingApp/Controllers/UserController.cs | 28 | Missing authorization check on PUT endpoint | Add [Authorize(Roles = "Admin")] attribute |
| SampleBankingApp/Controllers/UserController.cs | 37 | Missing authorization check on DELETE endpoint | Add [Authorize(Roles = "Admin")] attribute |
| SampleBankingApp/Program.cs | 19 | UseDeveloperExceptionPage called unconditionally | Remove in production builds |
| SampleBankingApp/Program.cs | 22 | Overly permissive CORS policy | Restrict origins to specific domains |
| SampleBankingApp/Program.cs | 24 | HTTPS redirection commented out | Enable HTTPS in production |
| SampleBankingApp/Program.cs | 26 | Debug symbols enabled in release build | Disable debug symbols in production |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 27 | Incorrect fee calculation | Ensure fee is calculated correctly before balance check |
| SampleBankingApp/Services/TransactionService.cs | 34 | Incorrect balance update logic | Verify that totalDebit includes fee |
| SampleBankingApp/Services/UserService.cs | 49 | Incorrect pagination logic | Use `(page - 1) * pageSize` instead of `page * pageSize` |
| SampleBankingApp/Services/TransactionService.cs | 41 | Potential negative balance | Ensure sufficient funds before deduction |
| SampleBankingApp/Services/TransactionService.cs | 52 | Transaction description not sanitized | Sanitize user input before inserting into DB |
| SampleBankingApp/Services/UserService.cs | 30 | No validation for email or username | Add validation for email and username formats |
| SampleBankingApp/Services/UserService.cs | 30 | No validation for user ID range | Add validation for valid ID ranges |
| SampleBankingApp/Services/UserService.cs | 43 | No validation for user ID range | Add validation for valid ID ranges |
| SampleBankingApp/Services/UserService.cs | 52 | No validation for page size limit | Add validation for valid page size |
| SampleBankingApp/Services/TransactionService.cs | 22 | No check for user self-transfer | Add check to prevent self-transfers |
| SampleBankingApp/Services/TransactionService.cs | 30 | No check for zero amount | Add validation for zero or negative amounts |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/TransactionController.cs | 24 | Silent exception handling in Transfer method | Add logging and proper error responses |
| SampleBankingApp/Services/TransactionService.cs | 52 | No transaction rollback on failure | Implement transaction scope for atomic operations |
| SampleBankingApp/Services/UserService.cs | 57 | No transaction handling for pagination | Ensure consistent data access |
| SampleBankingApp/Services/TransactionService.cs | 45 | Email sending after DB write | Move email sending to transaction commit phase |
| SampleBankingApp/Services/UserService.cs | 62 | Exception swallowing in SearchUsers | Return empty list instead of swallowing |
| SampleBankingApp/Services/TransactionService.cs | 49 | No exception handling for email sending | Wrap email sending in try-catch |
| SampleBankingApp/Services/UserService.cs | 30 | No validation for invalid user ID | Add validation before processing |
| SampleBankingApp/Services/UserService.cs | 43 | No validation for invalid user ID | Add validation before processing |
| SampleBankingApp/Services/TransactionService.cs | 20 | No validation for negative amount | Add validation before processing |
| SampleBankingApp/Services/TransactionService.cs | 30 | No validation for zero amount | Add validation before processing |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 25 | SqlConnection not disposed | Use `using` statement for connection |
| SampleBankingApp/Data/DatabaseHelper.cs | 32 | SqlCommand not disposed | Use `using` statement for command |
| SampleBankingApp/Data/DatabaseHelper.cs | 33 | SqlDataAdapter not disposed | Use `using` statement for adapter |
| SampleBankingApp/Data/DatabaseHelper.cs | 41 | SqlCommand not disposed | Use `using` statement for command |
| SampleBankingApp/Data/DatabaseHelper.cs | 42 | SqlDataAdapter not disposed | Use `using` statement for adapter |
| SampleBankingApp/Services/EmailService.cs | 22 | SmtpClient not disposed | Use `using` statement for SmtpClient |
| SampleBankingApp/Services/EmailService.cs | 28 | MailMessage not disposed | Use `using` statement for MailMessage |
| SampleBankingApp/Services/EmailService.cs | 43 | MailMessage not disposed | Use `using` statement for MailMessage |
| SampleBankingApp/Services/EmailService.cs | 49 | MailMessage not disposed | Use `using` statement for MailMessage |
| SampleBankingApp/Services/TransactionService.cs | 33 | SqlCommand not disposed | Use `using` statement for command |
| SampleBankingApp/Services/TransactionService.cs | 52 | SqlCommand not disposed | Use `using` statement for command |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 14 | User claim value not null-checked | Add null check before parsing |
| SampleBankingApp/Controllers/TransactionController.cs | 24 | User claim value not null-checked | Add null check before parsing |
| SampleBankingApp/Controllers/UserController.cs | 24 | User claim value not null-checked | Add null check before parsing |
| SampleBankingApp/Services/AuthService.cs | 29 | Connection string not null-checked | Add null check before using |
| SampleBankingApp/Services/AuthService.cs | 37 | JWT secret not null-checked | Add null check before using |
| SampleBankingApp/Services/AuthService.cs | 47 | JWT issuer not null-checked | Add null check before using |
| SampleBankingApp/Services/AuthService.cs | 48 | JWT audience not null-checked | Add null check before using |
| SampleBankingApp/Services/EmailService.cs | 19 | Email config values not null-checked | Add null checks before using |
| SampleBankingApp/Services/EmailService.cs | 20 | Email config values not null-checked | Add null checks before using |
| SampleBankingApp/Services/EmailService.cs | 21 | Email config values not null-checked | Add null checks before using |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 37 | Obsolete method ExecuteQueryWithParams | Remove or mark as obsolete |
| SampleBankingApp/Services/TransactionService.cs | 58 | Unimplemented RefundTransaction method | Implement or remove |
| SampleBankingApp/Services/AuthService.cs | 53 | Unreachable code after return | Remove unreachable code |
| SampleBankingApp/Services/TransactionService.cs | 20 | Unused private method FormatCurrency | Remove or mark as obsolete |
| SampleBankingApp/Services/UserService.cs | 22 | Unused static fields | Remove unused fields |
| SampleBankingApp/Services/UserService.cs | 23 | Unused static fields | Remove unused fields |
| SampleBankingApp/Services/UserService.cs | 24 | Unused static fields | Remove unused fields |
| SampleBankingApp/Services/UserService.cs | 25 | Unused static fields | Remove unused fields |
| SampleBankingApp/Services/UserService.cs | 26 | Unused static fields | Remove unused fields |
| SampleBankingApp/Services/UserService.cs | 27 | Unused static fields | Remove unused fields |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 11 | Magic number for transaction fee rate | Define as constant |
| SampleBankingApp/Services/TransactionService.cs | 12 | Magic number for max transactions per day | Define as constant |
| SampleBankingApp/Services/UserService.cs | 49 | Magic number for page size limit | Define as constant |
| SampleBankingApp/Services/UserService.cs | 57 | Magic number for page size limit | Define as constant |
| SampleBankingApp/Services/TransactionService.cs | 45 | Magic string for transaction type | Define as constant |
| SampleBankingApp/Services/TransactionService.cs | 46 | Magic string for transaction status | Define as constant |
| SampleBankingApp/Services/EmailService.cs | 10 | Magic string for transfer subject | Define as constant |
| SampleBankingApp/Services/EmailService.cs | 11 | Magic string for welcome subject | Define as constant |
| SampleBankingApp/Services/EmailService.cs | 12 | Magic number for max retries | Define as constant |
| SampleBankingApp/Services/EmailService.cs | 13 | Magic number for smtp timeout | Define as constant |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 24 | String concatenation in loop | Use StringBuilder or string.Join |
| SampleBankingApp/Services/TransactionService.cs | 34 | String concatenation in SQL | Use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 52 | String concatenation in SQL | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 34 | String concatenation in SQL | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 45 | String concatenation in SQL | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 57 | String concatenation in SQL | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 62 | String concatenation in SQL | Use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 20 | Reimplementing standard library | Use existing string methods |
| SampleBankingApp/Services/TransactionService.cs | 20 | Reimplementing standard library | Use existing string methods |
| SampleBankingApp/Services/TransactionService.cs | 20 | Reimplementing standard library | Use existing string methods |
| SampleBankingApp/Services/TransactionService.cs | 20 | Reimplementing standard library | Use existing string methods |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Program.cs | 19 | UseDeveloperExceptionPage called unconditionally | Remove in production |
| SampleBankingApp/Program.cs | 22 | Overly permissive CORS policy | Restrict origins to specific domains |
| SampleBankingApp/Program.cs | 24 | HTTPS redirection commented out | Enable in production |
| SampleBankingApp/Program.cs | 26 | Debug symbols enabled in release build | Disable in production |
| SampleBankingApp/Program.cs | 29 | JWT ValidateLifetime set to false | Enable in production |
| SampleBankingApp/appsettings.json | 10 | Hardcoded database password | Move to secure environment |
| SampleBankingApp/appsettings.json | 15 | Hardcoded JWT secret key | Move to secure environment |
| SampleBankingApp/appsettings.json | 20 | Hardcoded email password | Move to secure environment |
| SampleBankingApp/appsettings.json | 25 | Debug log levels in production | Reduce log levels |
| SampleBankingApp/appsettings.json | 10 | Hardcoded database connection string | Move to secure environment |
| SampleBankingApp/appsettings.json | 15 | Hardcoded JWT issuer | Move to secure environment |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 18 | No unit tests for Login method | Add tests for valid/invalid login |
| SampleBankingApp/Services/AuthService.cs | 37 | No unit tests for GenerateJwtToken method | Add tests for token generation |
| SampleBankingApp/Services/TransactionService.cs | 20 | No unit tests for Transfer method | Add tests for valid/invalid transfers |
| SampleBankingApp/Services/TransactionService.cs | 30 | No unit tests for Deposit method | Add tests for valid/invalid deposits |
| SampleBankingApp/Services/TransactionService.cs | 58 | No unit tests for RefundTransaction method | Add tests for refund functionality |
| SampleBankingApp/Services/UserService.cs | 30 | No unit tests for GetUserById method | Add tests for valid/invalid user IDs |
| SampleBankingApp/Services/UserService.cs | 34 | No unit tests for UpdateUser method | Add tests for valid/invalid updates |
| SampleBankingApp/Services/UserService.cs | 45 | No unit tests for DeleteUser method | Add tests for valid/invalid deletions |
| SampleBankingApp/Services/UserService.cs | 57 | No unit tests for GetUsersPage method | Add tests for pagination |
| SampleBankingApp/Services/UserService.cs | 62 | No unit tests for SearchUsers method | Add tests for search functionality |