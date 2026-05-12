# Peer Code Review Report

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 24 | SQL injection vulnerability in Login method using string interpolation | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/AuthService.cs | 24 | MD5 used for password hashing which is insecure | Replace with stronger password hashing algorithm like bcrypt |
| SampleBankingApp/Services/AuthService.cs | 37 | Hardcoded admin bypass password in source code | Remove hardcoded credentials and use secure authentication mechanism |
| SampleBankingApp/Services/AuthService.cs | 63 | JWT ValidateLifetime set to false allowing token reuse after expiration | Set ValidateLifetime to true for proper token expiration enforcement |
| SampleBankingApp/Services/AuthService.cs | 63 | Weak JWT secret key "mysecretkey" used in configuration | Use a cryptographically secure random key for JWT signing |
| SampleBankingApp/Services/TransactionService.cs | 28 | SQL injection risk in Transfer method using string interpolation for updates | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/TransactionService.cs | 39 | SQL injection risk in RecordTransaction method using string interpolation | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/UserService.cs | 37 | SQL injection vulnerability in SearchUsers method using LIKE clause | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Program.cs | 22 | Developer exception page enabled unconditionally | Only enable UseDeveloperExceptionPage in development environment |
| SampleBankingApp/Program.cs | 24 | HTTPS redirection is commented out | Uncomment and enable HTTPS redirection for security |
| SampleBankingApp/Program.cs | 26 | Overly permissive CORS policy allowing any origin, method, and header | Restrict CORS policy to specific trusted origins and required methods/headers |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 22 | Missing self-referential check for transferring to oneself | Add validation to prevent users from transferring to their own account |
| SampleBankingApp/Services/TransactionService.cs | 25 | Potential NullReferenceException if fromUserTable or toUserTable has no rows | Add null/empty checks before accessing Rows[0] |
| SampleBankingApp/Services/TransactionService.cs | 42 | Fee calculation may cause insufficient funds error | Adjust logic to check if fromBalance >= totalDebit (amount + fee) instead of just amount |
| SampleBankingApp/Services/TransactionService.cs | 45 | Potential negative balance if multiple transfers happen concurrently | Add transaction isolation or locking mechanism to prevent race conditions |
| SampleBankingApp/Services/TransactionService.cs | 57 | Missing validation for deposit amount limits | Add validation for minimum and maximum deposit amounts |
| SampleBankingApp/Services/TransactionService.cs | 59 | Interest bonus calculation uses hardcoded multiplier | Extract interest rate to configuration or constant |
| SampleBankingApp/Services/TransactionService.cs | 61 | SQL injection risk in Deposit method using string interpolation | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/UserService.cs | 26 | Inconsistent error handling for invalid user IDs | Return consistent error responses instead of throwing exceptions |
| SampleBankingApp/Services/UserService.cs | 45 | SQL injection vulnerability in UpdateUser method using string interpolation | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/UserService.cs | 58 | SQL injection vulnerability in DeleteUser method | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/UserService.cs | 66 | Pagination calculation uses page * pageSize which may skip records | Use (page - 1) * pageSize for correct pagination offset |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 42 | Potential NullReferenceException if reader has no rows | Add null/empty check before accessing reader fields |
| SampleBankingApp/Services/TransactionService.cs | 25 | Missing error handling for database query failures | Add try/catch blocks and proper error handling |
| SampleBankingApp/Services/TransactionService.cs | 45 | Missing transaction scope for balance updates | Wrap balance updates in a database transaction |
| SampleBankingApp/Services/TransactionService.cs | 51 | Email sending is a side effect after database update | Move email sending inside transaction or handle failures properly |
| SampleBankingApp/Services/TransactionService.cs | 69 | Exception swallowed in RefundTransaction method | Add proper error handling and logging |
| SampleBankingApp/Services/UserService.cs | 68 | Exception swallowed in SearchUsers method | Add proper error handling and logging |
| SampleBankingApp/Services/UserService.cs | 70 | Returns empty list on error without distinction from actual results | Return appropriate error response instead of empty list |
| SampleBankingApp/Controllers/TransactionController.cs | 38 | Raw exception message returned to client | Return generic error message instead of exposing internal details |
| SampleBankingApp/Controllers/UserController.cs | 35 | Exception swallowed in UpdateUser method | Add proper error handling and logging |
| SampleBankingApp/Controllers/UserController.cs | 41 | Raw exception message returned to client | Return generic error message instead of exposing internal details |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 24 | SqlConnection opened but not properly disposed | Use using statement or ensure proper disposal |
| SampleBankingApp/Data/DatabaseHelper.cs | 33 | SqlConnection opened but not properly disposed | Use using statement or ensure proper disposal |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | SqlConnection opened but not properly disposed | Use using statement or ensure proper disposal |
| SampleBankingApp/Data/DatabaseHelper.cs | 50 | SqlDataReader not properly disposed | Use using statement or ensure proper disposal |
| SampleBankingApp/Data/DatabaseHelper.cs | 66 | SqlConnection opened but not properly disposed | Use using statement or ensure proper disposal |
| SampleBankingApp/Services/EmailService.cs | 24 | SmtpClient instance held as field (not thread-safe) | Create SmtpClient instance per use instead of holding as field |
| SampleBankingApp/Services/EmailService.cs | 29 | MailMessage not properly disposed | Use using statement or ensure proper disposal |
| SampleBankingApp/Services/EmailService.cs | 48 | MailMessage not properly disposed | Use using statement or ensure proper disposal |
| SampleBankingApp/Services/EmailService.cs | 66 | MailMessage not properly disposed | Use using statement or ensure proper disposal |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 42 | Potential NullReferenceException if reader has no rows | Add null/empty check before accessing reader fields |
| SampleBankingApp/Services/TransactionService.cs | 25 | Potential NullReferenceException if fromUserTable or toUserTable has no rows | Add null/empty checks before accessing Rows[0] |
| SampleBankingApp/Services/TransactionService.cs | 28 | Potential NullReferenceException if fromUserTable or toUserTable has no rows | Add null/empty checks before accessing Rows[0] |
| SampleBankingApp/Services/TransactionService.cs | 31 | Potential NullReferenceException if fromUserTable or toUserTable has no rows | Add null/empty checks before accessing Rows[0] |
| SampleBankingApp/Services/TransactionService.cs | 33 | Potential NullReferenceException if fromUserTable or toUserTable has no rows | Add null/empty checks before accessing Rows[0] |
| SampleBankingApp/Services/TransactionService.cs | 47 | Potential NullReferenceException if fromUserTable or toUserTable has no rows | Add null/empty checks before accessing Rows[0] |
| SampleBankingApp/Services/TransactionService.cs | 51 | Potential NullReferenceException if fromUserTable or toUserTable has no rows | Add null/empty checks before accessing Rows[0] |
| SampleBankingApp/Services/TransactionService.cs | 53 | Potential NullReferenceException if fromUserTable or toUserTable has no rows | Add null/empty checks before accessing Rows[0] |
| SampleBankingApp/Services/UserService.cs | 40 | Potential NullReferenceException if table has no rows | Add null/empty check before accessing Rows[0] |
| SampleBankingApp/Services/UserService.cs | 42 | Potential NullReferenceException if table has no rows | Add null/empty check before accessing Rows[0] |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 66 | Obsolete method marked with [Obsolete] but still present | Remove obsolete method |
| SampleBankingApp/Services/AuthService.cs | 66 | Unused HashPasswordSha1 method | Remove unused method |
| SampleBankingApp/Services/AuthService.cs | 69 | Unused ValidateToken method | Remove unused method |
| SampleBankingApp/Helpers/StringHelper.cs | 19 | Duplicate implementation with JoinWithSeparatorFixed | Remove duplicate implementation |
| SampleBankingApp/Services/TransactionService.cs | 71 | NotImplementedException in RefundTransaction | Implement functionality or remove placeholder |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 11 | Magic number for transaction fee rate | Extract to named constant or configuration |
| SampleBankingApp/Services/TransactionService.cs | 12 | Magic number for max transactions per day | Extract to named constant or configuration |
| SampleBankingApp/Services/TransactionService.cs | 58 | Magic number for deposit amount limit | Extract to named constant or configuration |
| SampleBankingApp/Services/TransactionService.cs | 59 | Magic number for interest rate | Extract to named constant or configuration |
| SampleBankingApp/Services/UserService.cs | 26 | Magic number for user ID validation | Extract to named constants or configuration |
| SampleBankingApp/Services/UserService.cs | 27 | Magic number for user ID validation | Extract to named constants or configuration |
| SampleBankingApp/Services/AuthService.cs | 24 | Magic string for SQL query | Extract to constant or use parameterized queries |
| SampleBankingApp/Services/AuthService.cs | 37 | Hardcoded admin username | Extract to configuration |
| SampleBankingApp/Services/TransactionService.cs | 28 | Magic string for SQL update | Extract to constant or use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 39 | Magic string for SQL insert | Extract to constant or use parameterized queries |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 22 | String concatenation in loop (O(n²)) | Use string.Join instead |
| SampleBankingApp/Services/EmailService.cs | 24 | Regex created inside method called repeatedly | Make Regex static readonly |
| SampleBankingApp/Services/TransactionService.cs | 61 | String interpolation for SQL queries | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 68 | String concatenation for audit report | Use StringBuilder for better performance |
| SampleBankingApp/Services/AuthService.cs | 24 | Reimplementing string.IsNullOrWhiteSpace | Use built-in method |
| SampleBankingApp/Services/TransactionService.cs | 28 | Reimplementing string.IsNullOrWhiteSpace | Use built-in method |
| SampleBankingApp/Services/TransactionService.cs | 39 | Reimplementing string.IsNullOrWhiteSpace | Use built-in method |
| SampleBankingApp/Services/UserService.cs | 40 | Reimplementing string.IsNullOrWhiteSpace | Use built-in method |
| SampleBankingApp/Services/UserService.cs | 42 | Reimplementing string.IsNullOrWhiteSpace | Use built-in method |
| SampleBankingApp/Services/TransactionService.cs | 28 | Shared mutable static state without synchronization | Replace with thread-safe collection or instance-based approach |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 22 | UseDeveloperExceptionPage called unconditionally | Only enable in development environment |
| SampleBankingApp/Program.cs | 24 | HTTPS redirection commented out | Uncomment and enable HTTPS redirection |
| SampleBankingApp/Program.cs | 26 | Overly permissive CORS policy | Restrict to specific origins, methods, and headers |
| SampleBankingApp/appsettings.json | 1 | Hardcoded production secrets in source control | Remove sensitive data from source control and use secure secret management |
| SampleBankingApp/appsettings.json | 14 | Debug log level set for production | Set appropriate log levels for production environment |
| SampleBankingApp/SampleBankingApp.csproj | 1 | Missing environment-specific config overrides | Add appsettings.Production.json for production configuration |
| SampleBankingApp/SampleBankingApp.csproj | 1 | Outdated NuGet packages | Check for package updates and security advisories |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 1 | No unit tests for authentication logic | Implement tests for login, JWT generation, and password validation |
| SampleBankingApp/Services/TransactionService.cs | 1 | No unit tests for financial operations | Implement tests for transfer, deposit, and refund operations |
| SampleBankingApp/Services/TransactionService.cs | 1 | No boundary condition tests for transaction limits | Implement tests for max transactions per day and amount limits |
| SampleBankingApp/Controllers/TransactionController.cs | 1 | No unit tests for transaction endpoints | Implement tests for transfer, deposit, and refund endpoints |
| SampleBankingApp/Controllers/AuthController.cs | 1 | No unit tests for authentication endpoints | Implement tests for login endpoint and error scenarios |
| SampleBankingApp/Services/UserService.cs | 1 | No unit tests for user management | Implement tests for user creation, update, delete, and search |
| SampleBankingApp/Services/TransactionService.cs | 1 | No unit tests for pagination logic | Implement tests for transaction history pagination |
| SampleBankingApp/Services/TransactionService.cs | 1 | No unit tests for error handling | Implement tests for error scenarios and exception handling |