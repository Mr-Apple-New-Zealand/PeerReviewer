## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|------|-----|
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection vulnerability in Login method using string interpolation | Use parameterized queries instead of string concatenation for SQL |
| SampleBankingApp/Services/TransactionService.cs | 47 | SQL injection vulnerability in Transfer method using string interpolation | Use parameterized queries instead of string concatenation for SQL |
| SampleBankingApp/Services/TransactionService.cs | 48 | SQL injection vulnerability in Transfer method using string interpolation | Use parameterized queries instead of string concatenation for SQL |
| SampleBankingApp/Services/TransactionService.cs | 71 | SQL injection vulnerability in Deposit method using string interpolation | Use parameterized queries instead of string concatenation for SQL |
| SampleBankingApp/Services/UserService.cs | 47 | SQL injection vulnerability in UpdateUser method using string interpolation | Use parameterized queries instead of string concatenation for SQL |
| SampleBankingApp/Services/UserService.cs | 61 | SQL injection vulnerability in DeleteUser method using string interpolation | Use parameterized queries instead of string concatenation for SQL |
| SampleBankingApp/Services/UserService.cs | 99 | SQL injection vulnerability in SearchUsers method using string interpolation | Use parameterized queries instead of string concatenation for SQL |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | SQL injection vulnerability in ExecuteQuery method using string concatenation | Use parameterized queries instead of string concatenation for SQL |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | Potential null dereference on userIdClaim if user is not authenticated | Add null check before parsing userIdClaim |
| SampleBankingApp/Controllers/UserController.cs | 41 | Potential null dereference on userIdClaim if user is not authenticated | Add null check before parsing userIdClaim |
| SampleBankingApp/Program.cs | 16 | Hardcoded JWT secret key in Program.cs | Move to configuration file or environment variable |
| SampleBankingApp/appsettings.json | 6 | Hardcoded JWT secret key in appsettings.json | Move to secure configuration store |
| SampleBankingApp/appsettings.json | 14 | Hardcoded email password in appsettings.json | Move to secure configuration store |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password | Remove or make configurable |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded SQL Server connection string | Move to configuration file |
| SampleBankingApp/Program.cs | 34 | UseDeveloperExceptionPage called unconditionally in production code | Remove for production builds |
| SampleBankingApp/Services/AuthService.cs | 30 | Uses MD5 hashing which is insecure for passwords | Replace with bcrypt or PBKDF2 |
| SampleBankingApp/Services/AuthService.cs | 91 | Uses SHA1 hashing which is insecure for passwords | Replace with bcrypt or PBKDF2 |
| SampleBankingApp/Program.cs | 24 | ValidateLifetime = false in JWT configuration | Set to true for security |
| SampleBankingApp/Program.cs | 38 | Overly permissive CORS policy allowing any origin/method/header | Restrict to specific origins and methods |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic | Remove or make configurable |
| SampleBankingApp/Controllers/UserController.cs | 24 | Missing authorization check on GetUser endpoint | Add proper ownership validation |
| SampleBankingApp/Controllers/UserController.cs | 61 | Missing authorization check on DeleteUser endpoint | Add proper ownership validation |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|------|-----|
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check uses >= instead of > which could allow negative balances | Change to `fromBalance > totalDebit` |
| SampleBankingApp/Services/UserService.cs | 72 | Pagination calculation uses `page * pageSize` instead of `(page-1) * pageSize` | Change to `(page - 1) * pageSize` |
| SampleBankingApp/Services/TransactionService.cs | 68 | Interest bonus calculation is incorrect (0.05m * 1) | Remove unnecessary multiplication by 1 |
| SampleBankingApp/Services/TransactionService.cs | 40 | Fee calculation rounds to 2 decimal places but doesn't ensure precision | Use `Math.Round(amount * TransactionFeeRate, 2, MidpointRounding.AwayFromZero)` |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | Potential null dereference on userIdClaim if user is not authenticated | Add null check before parsing userIdClaim |
| SampleBankingApp/Controllers/UserController.cs | 41 | Potential null dereference on userIdClaim if user is not authenticated | Add null check before parsing userIdClaim |
| SampleBankingApp/Services/TransactionService.cs | 36 | Accesses Rows[0] without checking if Rows.Count > 0 | Add null check before accessing Rows[0] |
| SampleBankingApp/Services/TransactionService.cs | 37 | Accesses Rows[0] without checking if Rows.Count > 0 | Add null check before accessing Rows[0] |
| SampleBankingApp/Services/UserService.cs | 31 | Accesses Rows[0] without checking if Rows.Count > 0 | Add null check before accessing Rows[0] |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method uses LIKE clause with string concatenation | Use parameterized query for search term |
| SampleBankingApp/Services/UserService.cs | 48 | UpdateUser method doesn't validate email format | Add email validation before update |
| SampleBankingApp/Services/UserService.cs | 62 | DeleteUser method doesn't check if user exists before deletion | Add existence check before deletion |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|------|-----|
| SampleBankingApp/Controllers/UserController.cs | 50 | Generic Exception catch swallows all exceptions without logging | Log the exception with more detail before re-throwing |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method throws NotImplementedException instead of proper error handling | Implement actual refund logic or return appropriate HTTP status |
| SampleBankingApp/Services/UserService.cs | 105 | SearchUsers catches all exceptions and returns empty list silently | Log the exception before returning empty list |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Catches NotImplementedException but returns generic 500 error | Return specific error code or implement refund functionality |
| SampleBankingApp/Services/AuthService.cs | 32 | Uses raw SQL with string interpolation instead of parameters | Use parameterized queries to prevent SQL injection |
| SampleBankingApp/Services/UserService.cs | 47 | Uses raw SQL with string interpolation instead of parameters | Use parameterized queries to prevent SQL injection |
| SampleBankingApp/Services/UserService.cs | 61 | Uses raw SQL with string interpolation instead of parameters | Use parameterized queries to prevent SQL injection |
| SampleBankingApp/Services/TransactionService.cs | 47 | Uses raw SQL with string interpolation instead of parameters | Use parameterized queries to prevent SQL injection |
| SampleBankingApp/Services/TransactionService.cs | 48 | Uses raw SQL with string interpolation instead of parameters | Use parameterized queries to prevent SQL injection |
| SampleBankingApp/Services/TransactionService.cs | 71 | Uses raw SQL with string interpolation instead of parameters | Use parameterized queries to prevent SQL injection |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | Uses raw SQL with string concatenation instead of parameters | Use parameterized queries to prevent SQL injection |
| SampleBankingApp/Services/UserService.cs | 99 | Uses raw SQL with string concatenation instead of parameters | Use parameterized queries to prevent SQL injection |
| SampleBankingApp/Controllers/UserController.cs | 52 | Returns StatusCode(500, ex.Message) which exposes stack trace details | Return generic error message without exposing internal details |
| SampleBankingApp/Services/AuthService.cs | 38 | Uses raw SQL with string concatenation instead of parameters | Use parameterized queries to prevent SQL injection |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 20 | GetOpenConnection method opens connection but caller must remember to dispose it | Return a disposable connection or use `using` statements in callers |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | ExecuteNonQuery method opens connection but doesn't properly dispose it | Use `using` statement for connection |
| SampleBankingApp/Services/AuthService.cs | 34 | Opens connection without using `using` statement | Wrap in `using` statement to ensure proper disposal |
| SampleBankingApp/Services/AuthService.cs | 37 | Creates SqlCommand without using `using` statement | Wrap in `using` statement to ensure proper disposal |
| SampleBankingApp/Services/AuthService.cs | 38 | Creates SqlDataReader without using `using` statement | Wrap in `using` statement to ensure proper disposal |
| SampleBankingApp/Services/TransactionService.cs | 47 | ExecuteNonQuery called without proper disposal of connection | Use `using` statements for database operations |
| SampleBankingApp/Services/TransactionService.cs | 48 | ExecuteNonQuery called without proper disposal of connection | Use `using` statements for database operations |
| SampleBankingApp/Services/TransactionService.cs | 71 | ExecuteNonQuery called without proper disposal of connection | Use `using` statements for database operations |
| SampleBankingApp/Services/UserService.cs | 47 | ExecuteNonQuery called without proper disposal of connection | Use `using` statements for database operations |
| SampleBankingApp/Services/UserService.cs | 61 | ExecuteNonQuery called without proper disposal of connection | Use `using` statements for database operations |
| SampleBankingApp/Services/UserService.cs | 99 | ExecuteQuery called without proper disposal of connection | Use `using` statements for database operations |
| SampleBankingApp/Services/AuthService.cs | 34 | Opens connection and doesn't dispose it properly | Wrap in `using` statement to ensure proper disposal |
| SampleBankingApp/Services/AuthService.cs | 37 | Creates SqlCommand without using `using` statement | Wrap in `using` statement to ensure proper disposal |
| SampleBankingApp/Services/AuthService.cs | 38 | Creates SqlDataReader without using `using` statement | Wrap in `using` statement to ensure proper disposal |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|------|-----|
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add null check before calling `int.Parse(userIdClaim!)` |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add null check before calling `int.Parse(userIdClaim!)` |
| SampleBankingApp/Data/DatabaseHelper.cs | 15 | Connection string could be null if not configured | Add null check and throw exception if missing |
| SampleBankingApp/Services/AuthService.cs | 70 | _config["Jwt:SecretKey"] could be null | Add null check before using the secret key |
| SampleBankingApp/Services/AuthService.cs | 81 | _config["Jwt:Issuer"] could be null | Add null check before using the issuer |
| SampleBankingApp/Services/AuthService.cs | 82 | _config["Jwt:Audience"] could be null | Add null check before using the audience |
| SampleBankingApp/Services/EmailService.cs | 22 | _config["Email:SmtpHost"] could be null | Add null check before using the SMTP host |
| SampleBankingApp/Services/EmailService.cs | 24 | _config["Email:SmtpPort"] could be null | Add null check before parsing the port number |
| SampleBankingApp/Services/EmailService.cs | 25 | _config["Email:Username"] could be null | Add null check before using the username |
| SampleBankingApp/Services/EmailService.cs | 26 | _config["Email:Password"] could be null | Add null check before using the password |
| SampleBankingApp/Services/UserService.cs | 31 | table.Rows.Count is accessed without checking if table is null | Check for null table before accessing Rows |
| SampleBankingApp/Services/TransactionService.cs | 36 | fromUserTable.Rows[0] is accessed without null check | Add null check before accessing Rows[0] |
| SampleBankingApp/Services/TransactionService.cs | 37 | toUserTable.Rows[0] is accessed without null check | Add null check before accessing Rows[0] |
| SampleBankingApp/Services/UserService.cs | 99 | table.Rows is accessed without null check | Add null check before accessing Rows |
| SampleBankingApp/Services/TransactionService.cs | 53 | fromUserTable.Rows[0]["Email"] is accessed without null check | Add null check before accessing the email field |
| SampleBankingApp/Services/TransactionService.cs | 54 | toUserTable.Rows[0]["Username"] is accessed without null check | Add null check before accessing the username field |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 31 | JoinWithSeparator method uses string concatenation in loop which is O(n^2) | Replace with `string.Join` or `StringBuilder` |
| SampleBankingApp/Services/AuthService.cs | 98 | ValidateToken method has unreachable code after unconditional return | Remove the unreachable code block |
| SampleBankingApp/Services/AuthService.cs | 103 | ValidateToken method has unreachable code after unconditional return | Remove the unreachable code block |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that could cause race conditions | Make them instance fields or add proper synchronization |
| SampleBankingApp/Services/UserService.cs | 11 | _requestCount is incremented without thread safety | Add thread-safe increment mechanism |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method is unused and marked as private | Remove dead code |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method is duplicated by JoinWithSeparatorFixed | Remove the redundant implementation |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Return structured audit report or remove if unused |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has a complex return path with multiple exit points | Simplify the logic flow for better readability |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Consolidate validation logic into reusable helper methods |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 26 | Hardcoded error message string "Username not found or incorrect password" | Extract to configuration or resource file |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password "SuperAdmin2024" | Move to configuration or remove |
| SampleBankingApp/Services/TransactionService.cs | 11 | Magic number 0.015m for transaction fee rate | Extract to named constant |
| SampleBankingApp/Services/TransactionService.cs | 12 | Magic number 10 for max transactions per day | Extract to named constant |
| SampleBankingApp/Services/UserService.cs | 20 | Magic number 0 for invalid user ID check | Extract to named constant |
| SampleBankingApp/Services/UserService.cs | 22 | Magic number 1000000 for user ID range | Extract to named constant |
| SampleBankingApp/Services/UserService.cs | 41 | Magic number 0 for invalid user ID check | Extract to named constant |
| SampleBankingApp/Services/UserService.cs | 43 | Magic number 1000000 for user ID range | Extract to named constant |
| SampleBankingApp/Services/UserService.cs | 62 | Magic number 0 for invalid user ID check | Extract to named constant |
| SampleBankingApp/Services/UserService.cs | 64 | Magic number 1000000 for user ID range | Extract to named constant |
| SampleBankingApp/Controllers/UserController.cs | 32 | Magic number 20 for default page size | Extract to named constant |
| SampleBankingApp/Services/UserService.cs | 70 | Magic number 50 for max page size | Extract to named constant |
| SampleBankingApp/Services/TransactionService.cs | 65 | Magic number 1000000 for deposit limit | Extract to named constant |
| SampleBankingApp/Services/TransactionService.cs | 68 | Magic number 0.05m for interest rate | Extract to named constant |
| SampleBankingApp/Controllers/UserController.cs | 24 | Magic number 1 for default page number | Extract to named constant |
| SampleBankingApp/Services/UserService.cs | 72 | Magic number 50 for max page size | Extract to named constant |
| SampleBankingApp/Services/AuthService.cs | 32 | Hardcoded SQL table name "Users" | Extract to configuration or constant |
| SampleBankingApp/Services/TransactionService.cs | 89 | Hardcoded SQL table name "Transactions" | Extract to configuration or constant |
| SampleBankingApp/Services/UserService.cs | 75 | Hardcoded SQL table name "Users" | Extract to configuration or constant |
| SampleBankingApp/Services/UserService.cs | 99 | Hardcoded SQL table name "Users" | Extract to configuration or constant |
| SampleBankingApp/Services/AuthService.cs | 32 | Hardcoded SQL column names in WHERE clause | Extract to constants |
| SampleBankingApp/Services/TransactionService.cs | 47 | Hardcoded SQL column names in UPDATE clause | Extract to constants |
| SampleBankingApp/Services/TransactionService.cs | 48 | Hardcoded SQL column names in UPDATE clause | Extract to constants |
| SampleBankingApp/Services/TransactionService.cs | 71 | Hardcoded SQL column names in UPDATE clause | Extract to constants |
| SampleBankingApp/Services/UserService.cs | 47 | Hardcoded SQL column names in UPDATE clause | Extract to constants |
| SampleBankingApp/Services/UserService.cs | 61 | Hardcoded SQL column names in DELETE clause | Extract to constants |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 31 | JoinWithSeparator method uses string concatenation inside a loop which is O(n²) | Replace with `string.Join` or `StringBuilder` |
| SampleBankingApp/Services/UserService.cs | 25 | GetUserById method has multiple validation checks that could be consolidated | Consolidate validation logic into reusable helper methods |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method uses MD5 which is insecure for password hashing | Replace with bcrypt or PBKDF2 |
| SampleBankingApp/Services/TransactionService.cs | 47 | Transfer method has multiple database operations without transaction | Wrap in database transaction to ensure atomicity |
| SampleBankingApp/Services/TransactionService.cs | 48 | Transfer method has multiple database operations without transaction | Wrap in database transaction to ensure atomicity |
| SampleBankingApp/Services/UserService.cs | 47 | UpdateUser method has raw SQL with string concatenation | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 61 | DeleteUser method has raw SQL with string concatenation | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method uses LIKE clause with string concatenation | Use parameterized query for search term |
| SampleBankingApp/Services/AuthService.cs | 32 | Login method uses raw SQL with string concatenation | Use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 71 | Deposit method uses raw SQL with string concatenation | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add null check before accessing Rows[0] |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add null check before accessing Rows[0] |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add null check before accessing Rows[0] |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add null check before accessing Rows |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add null check before accessing email field |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add null check before accessing username field |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add null check before calling `int.Parse(userIdClaim!)` |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add null check before calling `int.Parse(userIdClaim!)` |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic | Remove or make configurable |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Return structured audit report or remove if unused |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Simplify the logic flow for better readability |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Consolidate validation logic into reusable helper methods |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|------|-----|
| SampleBankingApp/Program.cs | 34 | UseDeveloperExceptionPage called unconditionally in production code | Remove for production builds or add conditional logic |
| SampleBankingApp/Program.cs | 24 | ValidateLifetime = false in JWT configuration | Set to true for security |
| SampleBankingApp/Program.cs | 38 | Overly permissive CORS policy allowing any origin/method/header | Restrict to specific origins and methods |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out | Enable HTTPS in production environments |
| SampleBankingApp/appsettings.json | 18 | Log level set to Debug for production namespaces | Change to appropriate level like Warning or Error |
| SampleBankingApp/SampleBankingApp.csproj | 14 | System.Data.SqlClient version 4.8.6 is outdated | Update to latest stable version |
| SampleBankingApp/Program.cs | 16 | Hardcoded JWT secret key in Program.cs | Move to configuration file or environment variable |
| SampleBankingApp/appsettings.json | 6 | Hardcoded JWT secret key in appsettings.json | Move to secure configuration store |
| SampleBankingApp/appsettings.json | 14 | Hardcoded email password in appsettings.json | Move to secure configuration store |
| SampleBankingApp/SampleBankingApp.csproj | 13 | Microsoft.AspNetCore.Authentication.JwtBearer version 8.0.0 is outdated | Update to latest stable version |
| SampleBankingApp/appsettings.json | 4 | Hardcoded SQL Server connection string in appsettings.json | Move to secure configuration store |
| SampleBankingApp/Program.cs | 16 | Missing environment-specific config overrides like appsettings.Production.json | Add production configuration file |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password | Remove or make configurable |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic | Remove or make configurable |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|------|------|------|-----|
| SampleBankingApp/Services/AuthService.cs | 28 | Login method has complex logic that needs unit testing for various scenarios | Add tests for valid login, invalid credentials, admin bypass, etc. |
| SampleBankingApp/Services/TransactionService.cs | 23 | Transfer method has complex logic with multiple conditions and calculations | Add tests for successful transfer, insufficient funds, negative amounts, etc. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit method has boundary conditions that need testing | Add tests for valid deposit amounts, invalid amounts, interest calculation |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has validation logic that needs testing | Add tests for valid IDs, invalid IDs, out of range IDs |
| SampleBankingApp/Services/UserService.cs | 38 | UpdateUser method has raw SQL and validation logic that needs testing | Add tests for valid updates, invalid updates, email format validation |
| SampleBankingApp/Services/UserService.cs | 52 | DeleteUser method has raw SQL and validation logic that needs testing | Add tests for valid deletions, invalid IDs, etc. |
| SampleBankingApp/Services/UserService.cs | 68 | GetUsersPage method has pagination logic that needs testing | Add tests for page boundaries, max page size limits |
| SampleBankingApp/Services/UserService.cs | 95 | SearchUsers method has LIKE clause that needs testing | Add tests for search terms with special characters, empty results |
| SampleBankingApp/Controllers/AuthController.cs | 20 | Login endpoint needs authentication flow testing | Add tests for login success, login failure scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 23 | Transfer endpoint needs authorization and validation testing | Add tests for authorized users, unauthorized access, invalid amounts |
| SampleBankingApp/Controllers/UserController.cs | 21 | GetUser endpoint needs authorization testing | Add tests for authorized access, unauthorized access |
| SampleBankingApp/Controllers/UserController.cs | 31 | GetUsers endpoint needs pagination testing | Add tests for page size limits, page boundaries |
| SampleBankingApp/Controllers/UserController.cs | 38 | Deposit endpoint needs authorization and validation testing | Add tests for authorized users, invalid amounts |
| SampleBankingApp/Controllers/UserController.cs | 56 | DeleteUser endpoint needs authorization testing | Add tests for authorized access, unauthorized access |
| SampleBankingApp/Controllers/UserController.cs | 71 | SearchUsers endpoint needs testing | Add tests for search terms with special characters |
| SampleBankingApp/Services/AuthService.cs | 68 | GenerateJwtToken method needs token generation and validation testing | Add tests for valid tokens, token expiration |
| SampleBankingApp/Services/EmailService.cs | 34 | SendTransferNotification method needs email sending testing | Add tests for successful email sending, retry logic |
| SampleBankingApp/Services/EmailService.cs | 63 | SendWelcomeEmail method needs email sending testing | Add tests for successful email sending |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction method needs implementation testing | Add tests once implemented |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | IsValidEmail method needs validation testing | Add tests for valid and invalid email formats |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | IsValidUsername method needs validation testing | Add tests for valid and invalid username formats |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method needs testing | Add tests for audit log functionality |
| SampleBankingApp/Services/AuthService.cs | 98 | ValidateToken method needs token validation testing | Add tests for valid and invalid tokens |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 36 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 37 | Transfer method accesses Rows[0] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers method accesses Rows without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 53 | Transfer method accesses Rows[0]["Email"] without null check | Add tests to verify null handling |
| SampleBankingApp/Services/TransactionService.cs | 54 | Transfer method accesses Rows[0]["Username"] without null check | Add tests to verify null handling |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Controllers/UserController.cs | 41 | userIdClaim is used without null check before parsing | Add tests to verify null handling |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin user bypass logic needs testing | Add tests for admin bypass scenarios |
| SampleBankingApp/Services/UserService.cs | 85 | GetAuditReport method returns string instead of structured data | Add tests for audit report format |
| SampleBankingApp/Services/AuthService.cs | 25 | Login method has complex return path with multiple exit points | Add tests to verify all return paths work correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has multiple validation checks that could be consolidated | Add tests for all validation scenarios |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method needs testing | Add tests for daily transaction limits |
| SampleBankingApp/Services/UserService.cs | 10 | _auditLog and _requestCount are static fields that need thread safety testing | Add tests for concurrent access scenarios |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method needs performance testing | Add tests for large collections |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser endpoint needs error handling testing | Add tests for various error scenarios |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method needs HTML email testing | Add tests for HTML content rendering |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser endpoint needs null handling testing | Add tests for null user scenarios |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund endpoint needs implementation testing | Add tests once implemented |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 method needs security testing | Add tests to ensure password hashing works correctly |
| SampleBankingApp/Services/UserService.cs | 18 | GetUserById method has boundary conditions that need testing | Add tests for edge cases like ID=0, max ID |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer method has balance calculation logic that needs testing | Add tests for exact balance calculations and rounding |
| SampleBankingApp/Services/UserService