## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | Null-assertion on userIdClaim without verifying existence risks parsing null. | Check if userIdClaim is not null before parsing. |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | Null-assertion on userIdClaim without verifying existence risks parsing null. | Check if userIdClaim is not null before parsing. |
| SampleBankingApp/Controllers/UserController.cs | 48 | Returning raw exception message to client exposes internal error details. | Return a generic error message instead of the exception message. |
| SampleBankingApp/Controllers/UserController.cs | 52 | Returning raw exception message to client exposes internal error details. | Return a generic error message instead of the exception message. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded database credentials in constructor fallback. | Remove hardcoded credentials and require configuration. |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password in source code. | Remove hardcoded password and enforce database authentication. |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection vulnerability via string interpolation in WHERE clause. | Use parameterized queries instead of string interpolation. |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin bypass logic allows unauthorized access. | Remove hardcoded admin bypass logic. |
| SampleBankingApp/Services/EmailService.cs | 26 | Hardcoded email credentials in configuration access. | Ensure configuration values are not hardcoded in source. |
| SampleBankingApp/Services/EmailService.cs | 27 | Hardcoded email credentials in configuration access. | Ensure configuration values are not hardcoded in source. |
| SampleBankingApp/Services/TransactionService.cs | 47 | SQL injection vulnerability via string interpolation in UPDATE statement. | Use parameterized queries instead of string interpolation. |
| SampleBankingApp/Services/TransactionService.cs | 48 | SQL injection vulnerability via string interpolation in UPDATE statement. | Use parameterized queries instead of string interpolation. |
| SampleBankingApp/Services/TransactionService.cs | 90 | SQL injection vulnerability via string interpolation in INSERT statement. | Use parameterized queries instead of string interpolation. |
| SampleBankingApp/Services/UserService.cs | 47 | SQL injection vulnerability via string interpolation in UPDATE statement. | Use parameterized queries instead of string interpolation. |
| SampleBankingApp/Services/UserService.cs | 61 | SQL injection vulnerability via string interpolation in DELETE statement. | Use parameterized queries instead of string interpolation. |
| SampleBankingApp/Services/UserService.cs | 99 | SQL injection vulnerability via string interpolation in LIKE clause. | Use parameterized queries instead of string interpolation. |
| SampleBankingApp/appsettings.json | 3 | Hardcoded database password in configuration file. | Use environment variables or a secrets manager for production. |
| SampleBankingApp/appsettings.json | 14 | Hardcoded email password in configuration file. | Use environment variables or a secrets manager for production. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check excludes the transaction fee, allowing overdrafts. | Check if balance is greater than or equal to amount plus fee. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Interest bonus calculation uses incorrect multiplier logic. | Correct the interest bonus calculation formula. |
| SampleBankingApp/Services/UserService.cs | 72 | Pagination offset calculation uses `page * pageSize` instead of `(page - 1) * pageSize`. | Change offset calculation to `(page - 1) * pageSize`. |
| SampleBankingApp/Services/UserService.cs | 99 | Search query is directly interpolated into SQL without parameterization. | Use parameterized queries for the search query. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Catching NotImplementedException and returning a 500 status code. | Remove the catch block and let the exception propagate. |
| SampleBankingApp/Controllers/UserController.cs | 46 | Catching ArgumentException and returning the raw message to the client. | Return a generic error message instead of the exception message. |
| SampleBankingApp/Controllers/UserController.cs | 50 | Catching broad Exception and returning raw message to client. | Catch specific exceptions and return generic error messages. |
| SampleBankingApp/Services/AuthService.cs | 98 | ValidateToken method returns true without validating the token. | Implement actual token validation logic. |
| SampleBankingApp/Services/EmailService.cs | 56 | Logging exception message to console instead of structured logging. | Use ILogger for logging exceptions. |
| SampleBankingApp/Services/EmailService.cs | 77 | Logging exception message to console instead of structured logging. | Use ILogger for logging exceptions. |
| SampleBankingApp/Services/UserService.cs | 105 | Catching broad Exception and returning empty list instead of propagating error. | Propagate the exception or return a specific error response. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 21 | SqlConnection is opened but never closed or disposed. | Use a `using` statement to ensure disposal. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | SqlConnection returned from helper method is not disposed by caller. | Ensure callers dispose of the returned connection. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | SqlConnection is opened but never closed or disposed. | Use a `using` statement to ensure disposal. |
| SampleBankingApp/Services/EmailService.cs | 16 | SmtpClient is held as an instance field and never disposed. | Dispose of SmtpClient when it is no longer needed. |
| SampleBankingApp/Services/EmailService.cs | 39 | MailMessage is created but not disposed after sending. | Use a `using` statement for MailMessage. |
| SampleBankingApp/Services/EmailService.cs | 69 | MailMessage is created but not disposed after sending. | Use a `using` statement for MailMessage. |
| SampleBankingApp/Services/EmailService.cs | 89 | MailMessage is created but not disposed after sending. | Use a `using` statement for MailMessage. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | Null-assertion on userIdClaim without verifying existence. | Check if userIdClaim is not null before parsing. |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | Null-assertion on userIdClaim without verifying existence. | Check if userIdClaim is not null before parsing. |
| SampleBankingApp/Services/AuthService.cs | 70 | Null-assertion on Jwt:SecretKey without checking for null. | Check if Jwt:SecretKey is not null before using. |
| SampleBankingApp/Services/EmailService.cs | 24 | Null-assertion on SmtpPort configuration value. | Check if SmtpPort configuration value is not null. |
| SampleBankingApp/Services/EmailService.cs | 26 | Null-assertion on Email:Username configuration value. | Check if Email:Username configuration value is not null. |
| SampleBankingApp/Services/EmailService.cs | 27 | Null-assertion on Email:Password configuration value. | Check if Email:Password configuration value is not null. |
| SampleBankingApp/Services/TransactionService.cs | 53 | Null-assertion on Email configuration value. | Check if Email configuration value is not null. |
| SampleBankingApp/Services/TransactionService.cs | 55 | Null-assertion on Email configuration value. | Check if Email configuration value is not null. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | JoinWithSeparatorFixed is never called by any method. | Remove the unused method. |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 is never called by any method. | Remove the unused method. |
| SampleBankingApp/Services/AuthService.cs | 98 | ValidateToken is never called by any method. | Remove the unused method. |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency is never called by any method. | Remove the unused method. |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction is never called by any method. | Remove the unused method. |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport is never called by any method. | Remove the unused method. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | Magic number 254 used for email length limit. | Define a constant for the maximum email length. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | Magic numbers 3 and 20 used for username length limits. | Define constants for minimum and maximum username lengths. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | Magic number 4 used for account number masking. | Define a constant for the number of masked digits. |
| SampleBankingApp/Services/AuthService.cs | 84 | Magic number 30 used for JWT expiration. | Define a constant for JWT expiration duration. |
| SampleBankingApp/Services/EmailService.cs | 13 | Magic number 3 used for maximum email retries. | Define a constant for maximum email retries. |
| SampleBankingApp/Services/EmailService.cs | 14 | Magic number 5000 used for SMTP timeout. | Define a constant for SMTP timeout duration. |
| SampleBankingApp/Services/TransactionService.cs | 11 | Magic number 0.015 used for transaction fee rate. | Define a constant for transaction fee rate. |
| SampleBankingApp/Services/TransactionService.cs | 12 | Magic number 10 used for maximum transactions per day. | Define a constant for maximum transactions per day. |
| SampleBankingApp/Services/TransactionService.cs | 65 | Magic number 1000000 used for maximum deposit amount. | Define a constant for maximum deposit amount. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Magic number 0.05 used for interest bonus rate. | Define a constant for interest bonus rate. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Magic number 1 used in interest bonus calculation. | Define a constant for interest bonus multiplier. |
| SampleBankingApp/Services/UserService.cs | 70 | Magic number 50 used for maximum page size. | Define a constant for maximum page size. |
| SampleBankingApp/Services/UserService.cs | 1000000 | Magic number 1000000 used for user ID range limit. | Define a constant for maximum user ID. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 31 | String concatenation in a loop for joining items. | Use `string.Join` instead of string concatenation. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | Regex created inside method called repeatedly. | Make Regex static and readonly. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | Regex created inside method called repeatedly. | Make Regex static and readonly. |
| SampleBankingApp/Services/AuthService.cs | 63 | MD5 used for password hashing. | Use bcrypt or Argon2 for password hashing. |
| SampleBankingApp/Services/AuthService.cs | 93 | SHA1 used for password hashing. | Use bcrypt or Argon2 for password hashing. |
| SampleBankingApp/Services/EmailService.cs | 56 | Console.WriteLine used for logging. | Use ILogger for logging. |
| SampleBankingApp/Services/EmailService.cs | 77 | Console.WriteLine used for logging. | Use ILogger for logging. |
| SampleBankingApp/Services/TransactionService.cs | 47 | SQL injection vulnerability via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 48 | SQL injection vulnerability via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 90 | SQL injection vulnerability via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 47 | SQL injection vulnerability via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 61 | SQL injection vulnerability via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 99 | SQL injection vulnerability via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method has three distinct responsibilities. | Split into separate methods for logging and reporting. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 34 | UseDeveloperExceptionPage is called unconditionally. | Remove UseDeveloperExceptionPage in production. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out. | Enable HTTPS redirection in production. |
| SampleBankingApp/Program.cs | 38 | CORS policy allows any origin, method, and header. | Restrict CORS policy to specific origins and methods. |
| SampleBankingApp/Program.cs | 24 | ValidateLifetime is set to false on JWT. | Set ValidateLifetime to true. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | DebugSymbols is set to true. | Set DebugSymbols to false in release builds. |
| SampleBankingApp/SampleBankingApp.csproj | 9 | DebugType is set to full. | Set DebugType to portable in release builds. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | Newtonsoft.Json version 12.0.3 is outdated. | Update to a newer version of Newtonsoft.Json. |
| SampleBankingApp/appsettings.json | 18 | Default log level is set to Debug. | Set Default log level to Information or Warning. |
| SampleBankingApp/appsettings.json | 19 | Microsoft log level is set to Debug. | Set Microsoft log level to Information or Warning. |
| SampleBankingApp/appsettings.json | 20 | System log level is set to Debug. | Set System log level to Information or Warning. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 23 | Transfer method lacks unit tests for insufficient funds scenario. | Add unit tests for insufficient funds scenario. |
| SampleBankingApp/Services/TransactionService.cs | 23 | Transfer method lacks unit tests for fee calculation. | Add unit tests for fee calculation. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit method lacks unit tests for maximum deposit amount. | Add unit tests for maximum deposit amount. |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method lacks unit tests for daily limit. | Add unit tests for daily limit. |
| SampleBankingApp/Services/UserService.cs | 68 | GetUsersPage method lacks unit tests for pagination. | Add unit tests for pagination. |
| SampleBankingApp/Services/AuthService.cs | 28 | Login method lacks unit tests for admin bypass. | Add unit tests for admin bypass. |
| SampleBankingApp/Services/AuthService.cs | 68 | GenerateJwtToken method lacks unit tests for token generation. | Add unit tests for token generation. |
| SampleBankingApp/Controllers/TransactionController.cs | 23 | Transfer endpoint lacks unit tests for authorization. | Add unit tests for authorization. |
| SampleBankingApp/Controllers/UserController.cs | 38 | UpdateUser endpoint lacks unit tests for validation. | Add unit tests for validation. |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint lacks unit tests for authorization. | Add unit tests for authorization. |