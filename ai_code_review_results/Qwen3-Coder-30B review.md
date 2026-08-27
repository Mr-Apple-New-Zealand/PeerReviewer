## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection vulnerability in Login method using string interpolation for SQL query | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/TransactionService.cs | 47 | SQL injection vulnerability in Transfer method using string interpolation for UPDATE statement | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/TransactionService.cs | 48 | SQL injection vulnerability in Transfer method using string interpolation for UPDATE statement | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/TransactionService.cs | 90 | SQL injection vulnerability in RecordTransaction method using string interpolation for INSERT statement | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/UserService.cs | 47 | SQL injection vulnerability in UpdateUser method using string interpolation for UPDATE statement | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/UserService.cs | 61 | SQL injection vulnerability in DeleteUser method using string interpolation for DELETE statement | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/UserService.cs | 99 | SQL injection vulnerability in SearchUsers method using string interpolation for LIKE clause | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | SQL injection vulnerability in ExecuteQuery method using string interpolation for WHERE clause | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Program.cs | 16 | Hardcoded JWT secret key "mysecretkey" in appsettings.json | Use environment-specific configuration or secure secret management |
| SampleBankingApp/Program.cs | 24 | JWT validation disabled with ValidateLifetime = false | Enable lifetime validation for security |
| SampleBankingApp/Program.cs | 34 | Developer exception page enabled in production code | Remove UseDeveloperExceptionPage() from production builds |
| SampleBankingApp/Program.cs | 38 | Overly permissive CORS policy allowing any origin, method and header | Restrict CORS to specific origins and methods |
| SampleBankingApp/appsettings.json | 4 | Hardcoded database password "Admin1234!" in connection string | Use secure configuration management |
| SampleBankingApp/appsettings.json | 14 | Hardcoded email password "EmailPass99" in configuration | Use secure secret management for credentials |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password "SuperAdmin2024" | Remove hardcoded backdoor or make it configurable |
| SampleBankingApp/Services/AuthService.cs | 30 | Weak MD5 hashing used for passwords | Replace with bcrypt, scrypt, or PBKDF2 |
| SampleBankingApp/Services/AuthService.cs | 91 | Weak SHA1 hashing used for password validation | Replace with bcrypt, scrypt, or PBKDF2 |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded SQL Server credentials in default connection string | Use secure configuration management |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 42 | Incorrect balance check - checks if balance >= amount but then deducts amount + fee | Change condition to check if balance >= (amount + fee) |
| SampleBankingApp/Services/UserService.cs | 72 | Off-by-one error in pagination calculation using page * pageSize instead of (page-1) * pageSize | Change skip = (page - 1) * pageSize |
| SampleBankingApp/Services/TransactionService.cs | 68 | Incorrect interest calculation - applies 5% bonus to entire amount instead of just the deposit | Fix interest rate application logic |
| SampleBankingApp/Services/UserService.cs | 99 | Inconsistent handling of LIKE clause in SearchUsers method | Add proper parameterization for search queries |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | No check for transferring to self in Transfer method | Add validation to prevent self-transfers |
| SampleBankingApp/Services/TransactionService.cs | 36 | Potential division by zero or incorrect fee calculation if amount is very small | Add proper boundary checks for fee calculations |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/UserController.cs | 50 | Generic Exception catch that swallows all exceptions without logging | Log the exception before re-throwing or handle specific exceptions |
| SampleBankingApp/Services/UserService.cs | 105 | Generic try-catch in SearchUsers that returns empty list silently | Return error information to caller or log the exception |
| SampleBankingApp/Services/TransactionService.cs | 101 | NotImplementedException thrown without proper handling | Implement the refund functionality or provide better error messaging |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | NotImplementedException caught but returns generic 500 status code | Return specific error message indicating feature not implemented |
| SampleBankingApp/Services/UserService.cs | 47 | No transaction handling for database updates in UpdateUser method | Wrap database operations in a transaction to ensure atomicity |
| SampleBankingApp/Services/UserService.cs | 64 | No transaction handling for database delete in DeleteUser method | Wrap database operations in a transaction to ensure atomicity |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 20 | SqlConnection not disposed properly in GetOpenConnection method | Use using statement or ensure proper disposal |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | SqlConnection not disposed in ExecuteNonQuery method | Wrap connection in using statement |
| SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection not disposed in Login method | Wrap connection in using statement |
| SampleBankingApp/Services/EmailService.cs | 16 | SmtpClient instance field not properly disposed | Use using statement or implement IDisposable pattern |
| SampleBankingApp/Services/EmailService.cs | 39 | MailMessage created but not disposed | Wrap in using statement |
| SampleBankingApp/Services/EmailService.cs | 69 | MailMessage created but not disposed | Wrap in using statement |
| SampleBankingApp/Services/EmailService.cs | 89 | MailMessage created but not disposed | Wrap in using statement |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/TransactionController.cs | 27 | User.FindFirst(ClaimTypes.NameIdentifier)?.Value could be null and passed to int.Parse without validation | Add null check before parsing |
| SampleBankingApp/Controllers/UserController.cs | 41 | User.FindFirst(ClaimTypes.NameIdentifier)?.Value could be null and passed to int.Parse without validation | Add null check before parsing |
| SampleBankingApp/Services/AuthService.cs | 70 | _config["Jwt:SecretKey"] could be null and passed to SymmetricSecurityKey constructor | Add null check for configuration value |
| SampleBankingApp/Services/AuthService.cs | 81 | _config["Jwt:Issuer"] could be null and passed to JwtSecurityToken constructor | Add null check for configuration value |
| SampleBankingApp/Services/AuthService.cs | 82 | _config["Jwt:Audience"] could be null and passed to JwtSecurityToken constructor | Add null check for configuration value |
| SampleBankingApp/Services/EmailService.cs | 22 | _config["Email:SmtpHost"] could be null and passed to SmtpClient constructor | Add null check for configuration value |
| SampleBankingApp/Services/EmailService.cs | 24 | _config["Email:SmtpPort"] could be null and passed to int.Parse without validation | Add null check before parsing |
| SampleBankingApp/Services/EmailService.cs | 25 | _config["Email:Username"] could be null and passed to NetworkCredential constructor | Add null check for configuration value |
| SampleBankingApp/Services/EmailService.cs | 26 | _config["Email:Password"] could be null and passed to NetworkCredential constructor | Add null check for configuration value |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 98 | ValidateToken method has unreachable code after unconditional return statement | Remove unreachable code or fix logic |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method uses string concatenation in loop which is inefficient | Replace with string.Join or StringBuilder |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that could cause race conditions | Make them thread-safe or remove if not needed |
| SampleBankingApp/Services/AuthService.cs | 17 | AdminBypassPassword is marked as obsolete but still used in code | Remove or properly implement bypass logic |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Consider returning a more structured audit report format |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 26 | Hardcoded error message "Username not found or incorrect password" | Extract to configuration or resource file |
| SampleBankingApp/Services/AuthService.cs | 30 | Hardcoded MD5 algorithm name in HashPasswordMd5 method | Use a more secure hashing algorithm |
| SampleBankingApp/Services/TransactionService.cs | 11 | Magic number 0.015m for transaction fee rate | Define as named constant |
| SampleBankingApp/Services/TransactionService.cs | 12 | Magic number 10 for maximum transactions per day | Define as named constant |
| SampleBankingApp/Services/UserService.cs | 70 | Magic number 50 for page size limit | Define as named constant |
| SampleBankingApp/Services/TransactionService.cs | 68 | Magic number 0.05m for interest rate | Define as named constant |
| SampleBankingApp/Services/EmailService.cs | 10 | Magic string "Transfer Notification - BankingApp" | Extract to configuration or resource file |
| SampleBankingApp/Services/EmailService.cs | 11 | Magic string "Welcome to BankingApp!" | Extract to configuration or resource file |
| SampleBankingApp/Services/EmailService.cs | 13 | Magic number 3 for MaxRetries | Define as named constant |
| SampleBankingApp/Services/EmailService.cs | 14 | Magic number 5000 for SmtpTimeoutMs | Define as named constant |
| SampleBankingApp/Controllers/UserController.cs | 32 | Magic numbers 1 and 20 for pagination defaults | Define as named constants |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 32 | String interpolation in SQL query creates SQL injection vulnerability | Use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 47 | String interpolation in SQL query creates SQL injection vulnerability | Use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 48 | String interpolation in SQL query creates SQL injection vulnerability | Use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 90 | String interpolation in SQL query creates SQL injection vulnerability | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 47 | String interpolation in SQL query creates SQL injection vulnerability | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 61 | String interpolation in SQL query creates SQL injection vulnerability | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 99 | String interpolation in SQL query creates SQL injection vulnerability | Use parameterized queries |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | Inefficient string concatenation in JoinWithSeparator method | Replace with string.Join or StringBuilder |
| SampleBankingApp/Services/UserService.cs | 85 | Static audit log that could cause race conditions | Make thread-safe or remove if not needed |
| SampleBankingApp/Services/AuthService.cs | 98 | ValidateToken method has unreachable code after unconditional return statement | Remove unreachable code |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | Direct parsing of claim value without null check | Add null check before parsing |
| SampleBankingApp/Controllers/UserController.cs | 41 | Direct parsing of claim value without null check | Add null check before parsing |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Program.cs | 24 | JWT validation disabled with ValidateLifetime = false | Enable lifetime validation for security |
| SampleBankingApp/Program.cs | 34 | Developer exception page enabled in production code | Remove UseDeveloperExceptionPage() from production builds |
| SampleBankingApp/Program.cs | 38 | Overly permissive CORS policy allowing any origin, method and header | Restrict CORS to specific origins and methods |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out | Enable HTTPS redirection for production |
| SampleBankingApp/appsettings.json | 18 | Log level set to Debug in production | Change log level to appropriate production level |
| SampleBankingApp/SampleBankingApp.csproj | 9 | Debug symbols enabled in release build | Disable debug symbols for release builds |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password | Remove or make configurable |
| SampleBankingApp/appsettings.json | 4 | Hardcoded database credentials | Use secure configuration management |
| SampleBankingApp/appsettings.json | 14 | Hardcoded email credentials | Use secure configuration management |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 28 | Login method lacks unit test coverage for authentication logic | Create tests for valid/invalid login scenarios |
| SampleBankingApp/Services/AuthService.cs | 68 | GenerateJwtToken method lacks unit test coverage for token generation | Create tests for JWT token creation |
| SampleBankingApp/Services/TransactionService.cs | 23 | Transfer method lacks unit test coverage for fund transfer logic | Create tests for successful/failed transfers |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit method lacks unit test coverage for deposit logic | Create tests for valid/invalid deposits |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method lacks unit test coverage for user retrieval | Create tests for valid/invalid user ID scenarios |
| SampleBankingApp/Services/UserService.cs | 38 | UpdateUser method lacks unit test coverage for user update logic | Create tests for successful/failed updates |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for user deletion logic | Create tests for successful/failed deletions |
| SampleBankingApp/Services/UserService.cs | 68 | GetUsersPage method lacks unit test coverage for pagination logic | Create tests for page size limits and pagination |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search functionality | Create tests for search queries |
| SampleBankingApp/Controllers/AuthController.cs | 19 | Login endpoint lacks unit test coverage for authentication flow | Create tests for login endpoint behavior |
| SampleBankingApp/Controllers/TransactionController.cs | 23 | Transfer endpoint lacks unit test coverage for transfer logic | Create tests for transfer endpoint behavior |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval | Create tests for GET user endpoint |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination | Create tests for GET users endpoint with pagination |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending | Create tests for email sending functionality |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending | Create tests for email sending functionality |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | IsValidEmail method lacks unit test coverage for email validation | Create tests for valid/invalid email addresses |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | IsValidUsername method lacks unit test coverage for username validation | Create tests for valid/invalid usernames |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing | Create tests for password hashing functionality |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily limit logic | Create tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for error handling | Create tests for search error scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 48 | Refund endpoint lacks unit test coverage for refund logic | Create tests for refund endpoint behavior |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation | Create tests for refund functionality when implemented |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit reporting | Create tests for audit report generation |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method lacks unit test coverage for string joining | Create tests for string joining functionality |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search results | Create tests for search result handling |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for deletion logic | Create tests for user deletion endpoint behavior |
| SampleBankingApp/Services/AuthService.cs | 98 | ValidateToken method lacks unit test coverage for token validation | Create tests for JWT token validation |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method lacks unit test coverage for HTML email sending | Create tests for HTML email sending functionality |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary conditions | Create tests for boundary condition validation |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary conditions | Create tests for boundary condition validation |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary conditions | Create tests for boundary condition validation |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds scenario | Create tests for insufficient funds handling |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amounts | Create tests for invalid deposit amount handling |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge cases | Create tests for pagination edge cases |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amounts | Create tests for negative amount handling |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation | Create tests for interest calculation logic |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search queries | Create tests for search endpoint behavior |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for zero amounts | Create tests for zero amount handling |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for invalid IDs | Create tests for invalid ID handling |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for invalid IDs | Create tests for invalid ID handling |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for invalid IDs | Create tests for invalid ID handling |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limits | Create tests for page size limit enforcement |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits | Create tests for daily limit logic |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search queries | Create tests for search query handling |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for not found scenarios | Create tests for user not found scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass logic | Create tests for admin bypass functionality |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer scenarios | Create tests for self-transfer handling |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for empty results | Create tests for empty search results |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for maximum deposit limits | Create tests for maximum deposit limit enforcement |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for error scenarios | Create tests for delete error handling |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending failures | Create tests for email sending failure scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending failures | Create tests for email sending failure scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report generation | Create tests for audit report generation |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking | Create tests for account number masking |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation | Create tests for account obfuscation |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion | Create tests for title case conversion |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection | Create tests for blank string detection |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing | Create tests for password hashing |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing | Create tests for password hashing |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting | Create tests for currency formatting |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search performance | Create tests for search performance |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query handling | Create tests for search query handling |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation | Create tests for refund functionality when implemented |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search error scenarios | Create tests for search error handling |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge cases | Create tests for pagination edge cases |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits | Create tests for daily limit logic |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation | Create tests for search query validation |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge cases | Create tests for user retrieval edge cases |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials | Create tests for invalid credential handling |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition validation | Create tests for boundary condition validation |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition validation | Create tests for boundary condition validation |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition validation | Create tests for boundary condition validation |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit enforcement | Create tests for page size limit enforcement |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge cases | Create tests for insufficient funds edge cases |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge cases | Create tests for invalid amount edge cases |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge cases | Create tests for negative amount edge cases |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge cases | Create tests for interest calculation edge cases |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge cases | Create tests for search query edge cases |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge cases | Create tests for self-transfer edge cases |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge cases | Create tests for search query edge cases |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error scenarios | Create tests for user retrieval error scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge cases | Create tests for admin bypass edge cases |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge cases | Create tests for currency formatting edge cases |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance scenarios | Create tests for search query performance scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge cases | Create tests for delete error edge cases |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge cases | Create tests for email sending edge cases |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge cases | Create tests for email sending edge cases |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge cases | Create tests for audit report edge cases |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge cases | Create tests for account masking edge cases |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge cases | Create tests for account obfuscation edge cases |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge cases | Create tests for title case conversion edge cases |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge cases | Create tests for blank string detection edge cases |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge cases | Create tests for password hashing edge cases |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge cases | Create tests for password hashing edge cases |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge cases | Create tests for currency formatting edge cases |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge cases | Create tests for refund implementation edge cases |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge cases | Create tests for search query performance edge cases |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge cases | Create tests for daily transaction limits edge cases |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge cases | Create tests for search query validation edge cases |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge cases | Create tests for invalid credentials edge cases |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge cases | Create tests for boundary condition edge cases |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge cases | Create tests for boundary condition edge cases |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge cases | Create tests for boundary condition edge cases |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge cases | Create tests for page size limit edge cases |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case conversion edge case scenarios | Create tests for title case conversion edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method lacks unit test coverage for blank string detection edge case scenarios | Create tests for blank string detection edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method lacks unit test coverage for password hashing edge case scenarios | Create tests for password hashing edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method lacks unit test coverage for refund implementation edge case scenarios | Create tests for refund implementation edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit test coverage for daily transaction limits edge case scenarios | Create tests for daily transaction limits edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method lacks unit test coverage for search query validation edge case scenarios | Create tests for search query validation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval edge case scenarios | Create tests for user retrieval edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for invalid credentials edge case scenarios | Create tests for invalid credentials edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 27 | GetUserById method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method lacks unit test coverage for boundary condition edge case scenarios | Create tests for boundary condition edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint lacks unit test coverage for page size limit edge case scenarios | Create tests for page size limit edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for insufficient funds edge case scenarios | Create tests for insufficient funds edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit method lacks unit test coverage for invalid amount edge case scenarios | Create tests for invalid amount edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 72 | GetUsersPage method lacks unit test coverage for pagination edge case scenarios | Create tests for pagination edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method lacks unit test coverage for negative amount edge case scenarios | Create tests for negative amount edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit method lacks unit test coverage for interest calculation edge case scenarios | Create tests for interest calculation edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method lacks unit test coverage for self-transfer edge case scenarios | Create tests for self-transfer edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query edge case scenarios | Create tests for search query edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint lacks unit test coverage for user retrieval error edge case scenarios | Create tests for user retrieval error edge case scenarios |
| SampleBankingApp/Services/AuthService.cs | 53 | Login method lacks unit test coverage for admin bypass edge case scenarios | Create tests for admin bypass edge case scenarios |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method lacks unit test coverage for currency formatting edge case scenarios | Create tests for currency formatting edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers method lacks unit test coverage for search query performance edge case scenarios | Create tests for search query performance edge case scenarios |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit test coverage for delete error edge case scenarios | Create tests for delete error edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method lacks unit test coverage for email sending edge case scenarios | Create tests for email sending edge case scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method lacks unit test coverage for audit report edge case scenarios | Create tests for audit report edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method lacks unit test coverage for account masking edge case scenarios | Create tests for account masking edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method lacks unit test coverage for account obfuscation edge case scenarios | Create tests for account obfuscation edge case scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method lacks unit test coverage for title case