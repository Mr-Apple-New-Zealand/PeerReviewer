# Code Review Report

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthController.cs | 30 | Returns userId and role in response which may leak sensitive information | Remove userId and role from response or mask them |
| TransactionController.cs | 27 | Null-conditional operator with ! forces null reference exception if claim is missing | Add null check before parsing userIdClaim |
| TransactionController.cs | 41 | Null-conditional operator with ! forces null reference exception if claim is missing | Add null check before parsing userIdClaim |
| TransactionController.cs | 56 | Catches NotImplementedException and returns 500 instead of proper error handling | Remove catch block for NotImplementedException in production |
| TransactionController.cs | 53 | Refund endpoint lacks ownership verification allowing anyone to refund any transaction | Add authorization attribute to verify user owns the transaction |
| UserController.cs | 48 | Returns exception message directly to client exposing internal errors | Return generic error message instead of ex.Message |
| UserController.cs | 52 | Returns exception message directly to client exposing internal errors | Return generic error message instead of ex.Message |
| UserController.cs | 43 | UpdateUser endpoint lacks ownership verification allowing anyone to update any user | Add authorization attribute to verify user owns the account |
| UserController.cs | 61 | DeleteUser endpoint lacks ownership verification allowing anyone to delete any user | Add authorization attribute to verify user owns the account |
| DatabaseHelper.cs | 16 | Hardcoded database credentials in constructor fallback | Remove hardcoded credentials and require configuration |
| DatabaseHelper.cs | 29 | SQL injection vulnerability via tableName parameter in interpolated query | Use parameterized query for tableName or validate against whitelist |
| DatabaseHelper.cs | 40 | SQL injection vulnerability via parameters.AddWith method | Use proper parameter binding with SqlCommand |
| DatabaseHelper.cs | 52 | GetOpenConnection returns connection that caller never disposes | Return using statement or require caller to dispose |
| DatabaseHelper.cs | 67 | Obsolete method still present in codebase | Remove obsolete method or keep for backward compatibility with deprecation notice |
| StringHelper.cs | 16 | Regex object created on each call instead of being static readonly | Make Regex static readonly field |
| StringHelper.cs | 25 | Regex object created on each call instead of being static readonly | Make Regex static readonly field |
| User.cs | 7 | Password stored in plain text in model class | Implement password hashing and never store plain text passwords |
| Program.cs | 34 | UseDeveloperExceptionPage enabled in production | Conditionally enable based on environment or disable in production |
| Program.cs | 36 | HTTPS redirection is commented out | Uncomment and enable HTTPS redirection |
| Program.cs | 38 | Overly permissive CORS policy allows any origin, method, and header | Configure specific allowed origins and methods based on requirements |
| Program.cs | 16 | JWT secret retrieved from configuration without null check | Add null check for jwtSecret before using it |
| Program.cs | 28 | JWT secret used directly without null check | Add null check for jwtSecret before using it |
| SampleBankingApp.csproj | 14 | System.Data.SqlClient package is outdated and vulnerable | Upgrade to System.Data.SqlClient or use modern alternatives |
| SampleBankingApp.csproj | 15 | Newtonsoft.Json 12.0.3 has known security vulnerabilities | Upgrade to latest stable version |
| AuthService.cs | 17 | Hardcoded admin bypass password in source code | Remove hardcoded password and use secure authentication |
| AuthService.cs | 30 | MD5 password hashing provides weak security | Use bcrypt or Argon2 for password hashing |
| AuthService.cs | 32 | SQL injection vulnerability via username and password interpolation | Use parameterized queries for all database operations |
| AuthService.cs | 53 | Hardcoded admin bypass logic bypasses authentication | Remove hardcoded admin bypass and use proper role-based access |
| AuthService.cs | 61 | HashPasswordMd5 method uses weak cryptography | Remove and use strong password hashing algorithm |
| AuthService.cs | 70 | JwtSecret configuration value used without null check | Add null check before using jwtSecret |
| AuthService.cs | 98 | ValidateToken method always returns true after null check | Implement proper JWT validation logic |
| EmailService.cs | 16 | SmtpClient held as instance field causing thread safety issues | Create SmtpClient per request or use thread-safe configuration |
| EmailService.cs | 22 | Email credentials stored in configuration without validation | Validate email credentials and use secure storage |
| EmailService.cs | 36 | Email body contains sensitive information | Remove sensitive information from email body |
| EmailService.cs | 56 | Exception message logged to console exposing internal errors | Log generic error message instead of exception details |
| EmailService.cs | 77 | Exception message logged to console exposing internal errors | Log generic error message instead of exception details |
| EmailService.cs | 91 | MailMessage not disposed causing resource leak | Use using statement for MailMessage |
| TransactionService.cs | 36 | Accessing Rows[0] without checking count causes null reference | Check Rows.Count before accessing first row |
| TransactionService.cs | 37 | Accessing Rows[0] without checking count causes null reference | Check Rows.Count before accessing first row |
| TransactionService.cs | 47 | SQL injection vulnerability via interpolated balance values | Use parameterized queries for all database operations |
| TransactionService.cs | 48 | SQL injection vulnerability via interpolated balance values | Use parameterized queries for all database operations |
| TransactionService.cs | 71 | SQL injection vulnerability via interpolated balance values | Use parameterized queries for all database operations |
| TransactionService.cs | 83 | Accessing Rows[0] without checking count causes null reference | Check Rows.Count before accessing first row |
| TransactionService.cs | 89 | SQL injection vulnerability via interpolated values | Use parameterized queries for all database operations |
| TransactionService.cs | 102 | NotImplementedException in production code | Implement the method or remove from production |
| UserService.cs | 47 | SQL injection vulnerability via interpolated values | Use parameterized queries for all database operations |
| UserService.cs | 61 | SQL injection vulnerability via interpolated values | Use parameterized queries for all database operations |
| UserService.cs | 99 | SQL injection vulnerability via LIKE clause interpolation | Use parameterized queries for all database operations |
| UserService.cs | 105 | Catch-all Exception returns empty list preventing error detection | Return specific error or propagate exception |
| appsettings.json | 3 | Hardcoded database credentials in configuration file | Use environment variables or secure vault |
| appsettings.json | 6 | Hardcoded JWT secret in configuration file | Use environment variables or secure vault |
| appsettings.json | 14 | Hardcoded email password in configuration file | Use environment variables or secure vault |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionController.cs | 27 | Null-conditional operator with ! forces exception when claim is missing | Add null check before parsing |
| TransactionController.cs | 41 | Null-conditional operator with ! forces exception when claim is missing | Add null check before parsing |
| TransactionService.cs | 42 | Checks balance >= amount but deducts amount + fee causing insufficient funds error | Check balance >= amount + fee before deducting |
| TransactionService.cs | 68 | Interest calculation multiplies by 0.05m * 1 which is redundant | Remove redundant multiplication |
| UserService.cs | 72 | Pagination uses page * pageSize instead of (page - 1) * pageSize | Change to (page - 1) * pageSize |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionController.cs | 56 | Catches NotImplementedException instead of letting it propagate | Remove catch block for NotImplementedException |
| UserController.cs | 46 | Catches ArgumentException and returns message to client | Return generic error message instead of ex.Message |
| UserController.cs | 50 | Catches broad Exception and returns message to client | Catch specific exceptions or log and return generic error |
| UserService.cs | 105 | Catches broad Exception and returns empty list | Return specific error or propagate exception |
| AuthService.cs | 98 | ValidateToken method always returns true after null check | Implement proper JWT validation logic |
| EmailService.cs | 71 | Catch-all Exception logs to console instead of proper error handling | Use structured logging with appropriate log level |
| DatabaseHelper.cs | 28 | GetOpenConnection never closes connection on exception | Use using statement for connection |
| DatabaseHelper.cs | 52 | GetOpenConnection never closes connection on exception | Use using statement for connection |
| DatabaseHelper.cs | 61 | TableExists never closes connection on exception | Use using statement for connection |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 21 | SqlConnection created but never disposed | Use using statement for connection |
| DatabaseHelper.cs | 28 | SqlConnection returned from method never disposed by caller | Return using statement or require caller to dispose |
| DatabaseHelper.cs | 38 | SqlConnection opened but never closed in ExecuteQuerySafe | Use using statement for connection |
| DatabaseHelper.cs | 40 | SqlCommand created but never disposed | Use using statement for command |
| DatabaseHelper.cs | 44 | SqlDataAdapter created but never disposed | Use using statement for adapter |
| DatabaseHelper.cs | 52 | SqlConnection never closed in ExecuteNonQuery | Use using statement for connection |
| DatabaseHelper.cs | 53 | SqlCommand created but never disposed | Use using statement for command |
| DatabaseHelper.cs | 61 | SqlConnection opened but never closed in TableExists | Use using statement for connection |
| DatabaseHelper.cs | 70 | SqlConnection opened but never closed in ExecuteQueryWithParams | Use using statement for connection |
| DatabaseHelper.cs | 72 | SqlCommand created but never disposed | Use using statement for command |
| DatabaseHelper.cs | 74 | SqlDataAdapter created but never disposed | Use using statement for adapter |
| StringHelper.cs | 16 | Regex object created on each call instead of being static | Make Regex static readonly |
| StringHelper.cs | 25 | Regex object created on each call instead of being static | Make Regex static readonly |
| EmailService.cs | 16 | SmtpClient held as instance field causing socket never released | Create SmtpClient per request or use thread-safe configuration |
| EmailService.cs | 39 | MailMessage created but never disposed | Use using statement for MailMessage |
| EmailService.cs | 69 | MailMessage created but never disposed | Use using statement for MailMessage |
| EmailService.cs | 89 | MailMessage created but never disposed | Use using statement for MailMessage |
| EmailService.cs | 91 | MailMessage not disposed causing resource leak | Use using statement for MailMessage |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthController.cs | 22 | LoginRequest properties could be null despite nullable reference types | Add null checks or use required properties |
| TransactionController.cs | 27 | userIdClaim could be null causing null reference with ! operator | Add null check before parsing |
| TransactionController.cs | 41 | userIdClaim could be null causing null reference with ! operator | Add null check before parsing |
| DatabaseHelper.cs | 15 | GetConnectionString could return null causing null reference | Add null check for connection string |
| DatabaseHelper.cs | 16 | Fallback connection string uses hardcoded credentials | Remove hardcoded credentials |
| DatabaseHelper.cs | 36 | Parameters dictionary could contain null values | Validate parameters before adding |
| DatabaseHelper.cs | 63 | GetSchema could return empty result causing null reference | Check result before accessing Rows |
| AuthService.cs | 15 | IConfiguration could be null in constructor | Add null check for configuration |
| AuthService.cs | 34 | GetConnectionString could return null causing null reference | Add null check for connection string |
| AuthService.cs | 70 | jwtSecret configuration value could be null | Add null check before using jwtSecret |
| AuthService.cs | 81 | Jwt:Issuer configuration value could be null | Add null check for issuer |
| AuthService.cs | 82 | Jwt:Audience configuration value could be null | Add null check for audience |
| EmailService.cs | 22 | SmtpHost configuration value could be null | Add null check for SmtpHost |
| EmailService.cs | 24 | SmtpPort configuration value could be null | Add null check for SmtpPort |
| EmailService.cs | 26 | Email:Username configuration value could be null | Add null check for Username |
| EmailService.cs | 27 | Email:Password configuration value could be null | Add null check for Password |
| TransactionService.cs | 28 | ExecuteQuerySafe could return empty table causing null reference | Check Rows.Count before accessing |
| TransactionService.cs | 32 | ExecuteQuerySafe could return empty table causing null reference | Check Rows.Count before accessing |
| TransactionService.cs | 36 | fromUserTable could be empty causing null reference | Check Rows.Count before accessing |
| TransactionService.cs | 37 | toUserTable could be empty causing null reference | Check Rows.Count before accessing |
| TransactionService.cs | 83 | table could be empty causing null reference | Check Rows.Count before accessing |
| UserService.cs | 27 | ExecuteQuerySafe could return empty table causing null reference | Check Rows.Count before accessing |
| UserService.cs | 34 | table could be empty causing null reference | Check Rows.Count before accessing |
| UserService.cs | 99 | ExecuteQuery could return empty table causing null reference | Check Rows.Count before accessing |
| UserService.cs | 101 | table could be empty causing null reference | Check Rows.Count before accessing |
| UserService.cs | 111 | MapRowToUser assumes row exists | Add null check before mapping |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 67-78 | ExecuteQueryWithParams is marked obsolete but still present | Remove obsolete method or keep for backward compatibility |
| StringHelper.cs | 38-41 | JoinWithSeparatorFixed is duplicate implementation | Remove duplicate method or rename one |
| StringHelper.cs | 31-36 | JoinWithSeparator is inefficient and unused | Remove inefficient method or use StringBuilder |
| AuthService.cs | 61-66 | HashPasswordSha1 is unused method | Remove unused method |
| AuthService.cs | 98-108 | ValidateToken method always returns true | Remove or implement proper validation |
| TransactionService.cs | 94-97 | FormatCurrency is unused method | Remove unused method |
| TransactionService.cs | 99-103 | RefundTransaction throws NotImplementedException | Remove or implement the method |
| EmailService.cs | 81-84 | BuildHtmlTemplate is unused method | Remove unused method |
| EmailService.cs | 86-92 | SendWelcomeEmailHtml is unused method | Remove unused method |
| UserService.cs | 111-123 | MapRowToUser is private method used only internally | Keep as is since it's used internally |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 16 | Hardcoded database credentials in fallback | Remove hardcoded credentials |
| AuthService.cs | 17 | Hardcoded admin bypass password | Remove hardcoded password |
| AuthService.cs | 84 | JWT expiration hardcoded to 30 days | Use configuration value |
| EmailService.cs | 10 | TransferSubject is hardcoded string | Use configuration value |
| EmailService.cs | 11 | WelcomeSubject is hardcoded string | Use configuration value |
| EmailService.cs | 13 | MaxRetries is hardcoded to 3 | Use configuration value |
| EmailService.cs | 14 | SmtpTimeoutMs is hardcoded to 5000 | Use configuration value |
| EmailService.cs | 40 | From email hardcoded to notifications@company.com | Use configuration value |
| EmailService.cs | 67 | Support email hardcoded to support@company.com | Use configuration value |
| EmailService.cs | 83 | HTML template structure is hardcoded | Use configuration or template file |
| TransactionService.cs | 11 | TransactionFeeRate is hardcoded to 0.015m | Use configuration value |
| TransactionService.cs | 12 | MaxTransactionsPerDay is hardcoded to 10 | Use configuration value |
| TransactionService.cs | 40 | Fee calculation uses hardcoded rate | Use configuration value |
| TransactionService.cs | 66 | Deposit amount limit hardcoded to 1000000 | Use configuration value |
| TransactionService.cs | 68 | Interest bonus rate hardcoded to 0.05m | Use configuration value |
| TransactionService.cs | 84 | Daily limit check uses hardcoded constant | Use configuration value |
| UserService.cs | 22 | User ID range limit hardcoded to 1000000 | Use configuration value |
| UserService.cs | 42 | User ID range limit hardcoded to 1000000 | Use configuration value |
| UserService.cs | 56 | User ID range limit hardcoded to 1000000 | Use configuration value |
| UserService.cs | 70 | Page size limit hardcoded to 50 | Use configuration value |
| appsettings.json | 3 | Connection string has hardcoded password | Use environment variable |
| appsettings.json | 6 | JWT secret is hardcoded | Use environment variable |
| appsettings.json | 14 | Email password is hardcoded | Use environment variable |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 29 | String interpolation in SQL query | Use parameterized queries |
| DatabaseHelper.cs | 40 | String interpolation in SQL query | Use parameterized queries |
| DatabaseHelper.cs | 53 | String interpolation in SQL query | Use parameterized queries |
| DatabaseHelper.cs | 72 | String interpolation in SQL query | Use parameterized queries |
| DatabaseHelper.cs | 73 | command.Parameters.AddRange with SqlParameter array | Use proper parameter binding |
| StringHelper.cs | 16 | Regex created inside method instead of static readonly | Make Regex static readonly |
| StringHelper.cs | 25 | Regex created inside method instead of static readonly | Make Regex static readonly |
| StringHelper.cs | 31-36 | String concatenation in loop instead of StringBuilder | Use StringBuilder or string.Join |
| StringHelper.cs | 38-41 | Duplicate implementation of JoinWithSeparator | Remove duplicate method |
| AuthService.cs | 32 | String interpolation in SQL query | Use parameterized queries |
| AuthService.cs | 70 | String interpolation for jwtSecret | Add null check |
| AuthService.cs | 81 | String interpolation for Jwt:Issuer | Add null check |
| AuthService.cs | 82 | String interpolation for Jwt:Audience | Add null check |
| EmailService.cs | 36 | String concatenation for email body | Use StringBuilder or string interpolation |
| EmailService.cs | 65 | Uppercase conversion on username | Use string.IsNullOrEmpty check first |
| EmailService.cs | 69 | String concatenation for email body | Use StringBuilder or string interpolation |
| EmailService.cs | 83 | String interpolation for HTML template | Use StringBuilder or string interpolation |
| TransactionService.cs | 29 | String interpolation in SQL query | Use parameterized queries |
| TransactionService.cs | 33 | String interpolation in SQL query | Use parameterized queries |
| TransactionService.cs | 47 | String interpolation in SQL query | Use parameterized queries |
| TransactionService.cs | 48 | String interpolation in SQL query | Use parameterized queries |
| TransactionService.cs | 71 | String interpolation in SQL query | Use parameterized queries |
| TransactionService.cs | 80 | String interpolation in SQL query | Use parameterized queries |
| TransactionService.cs | 89 | String interpolation in SQL query | Use parameterized queries |
| UserService.cs | 28 | String interpolation in SQL query | Use parameterized queries |
| UserService.cs | 47 | String interpolation in SQL query | Use parameterized queries |
| UserService.cs | 61 | String interpolation in SQL query | Use parameterized queries |
| UserService.cs | 75 | String interpolation in SQL query | Use parameterized queries |
| UserService.cs | 99 | String interpolation in SQL query | Use parameterized queries |
| UserService.cs | 111 | MapRowToUser assumes row exists | Add null check before mapping |
| Program.cs | 16 | String interpolation for jwtSecret | Add null check |
| Program.cs | 26 | String interpolation for Jwt:Issuer | Add null check |
| Program.cs | 27 | String interpolation for Jwt:Audience | Add null check |
| SampleBankingApp.csproj | 14 | System.Data.SqlClient is outdated package | Upgrade to modern alternative |
| SampleBankingApp.csproj | 15 | Newtonsoft.Json 12.0.3 is outdated | Upgrade to latest version |
| appsettings.json | 3 | Connection string has hardcoded password | Use environment variable |
| appsettings.json | 6 | JWT secret is hardcoded | Use environment variable |
| appsettings.json | 14 | Email password is hardcoded | Use environment variable |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 34 | UseDeveloperExceptionPage enabled unconditionally | Conditionally enable based on environment |
| Program.cs | 36 | HTTPS redirection is commented out | Uncomment and enable HTTPS redirection |
| Program.cs | 38 | CORS policy allows any origin, method, and header | Configure specific allowed origins and methods |
| SampleBankingApp.csproj | 8 | DebugSymbols set to true | Set to false for production builds |
| SampleBankingApp.csproj | 9 | DebugType set to full | Set to portable or disable for production |
| SampleBankingApp.csproj | 7 | TreatWarningsAsErrors is false | Set to true for better code quality |
| appsettings.json | 18 | Default log level is Debug | Set to Information or Warning for production |
| appsettings.json | 19 | Microsoft log level is Debug | Set to Information or Warning for production |
| appsettings.json | 20 | System log level is Debug | Set to Information or Warning for production |
| appsettings.json | 23 | AllowedHosts is set to wildcard | Configure specific allowed hosts |
| appsettings.json | 3 | Connection string has hardcoded password | Use environment variable |
| appsettings.json | 6 | JWT secret is hardcoded | Use environment variable |
| appsettings.json | 14 | Email password is hardcoded | Use environment variable |
| appsettings.json | 12 | SmtpPort is hardcoded to 25 | Use configuration value |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/ | N/A | No test project exists | Create test project with unit tests |
| AuthController.cs | 20 | Login method needs tests for invalid credentials | Add tests for invalid username/password combinations |
| AuthController.cs | 20 | Login method needs tests for valid credentials | Add tests for successful login scenarios |
| TransactionController.cs | 24 | Transfer method needs tests for insufficient funds | Add tests for insufficient balance scenarios |
| TransactionController.cs | 24 | Transfer method needs tests for self-transfer | Add tests for transferring to same user |
| TransactionController.cs | 38 | Deposit method needs tests for invalid amounts | Add tests for negative and zero amounts |
| TransactionController.cs | 38 | Deposit method needs tests for maximum amounts | Add tests for amounts exceeding limits |
| UserController.cs | 22 | GetUserById needs tests for invalid IDs | Add tests for negative and zero IDs |
| UserController.cs | 22 | GetUserById needs tests for non-existent users | Add tests for users that don't exist |
| UserController.cs | 32 | GetUsers needs tests for pagination boundaries | Add tests for page 1 and large page numbers |
| UserController.cs | 39 | UpdateUser needs tests for ownership verification | Add tests for unauthorized update attempts |
| UserController.cs | 57 | DeleteUser needs tests for ownership verification | Add tests for unauthorized delete attempts |
| UserService.cs | 18 | GetUserById needs tests for ID range validation | Add tests for ID range boundary conditions |
| UserService.cs | 68 | GetUsersPage needs tests for page size limits | Add tests for page size exceeding limits |
| UserService.cs | 95 | SearchUsers needs tests for SQL injection prevention | Add tests for special characters in query |
| UserService.cs | 95 | SearchUsers needs tests for empty results | Add tests for search returning no results |
| TransactionService.cs | 23 | Transfer needs tests for fee calculation | Add tests for fee calculation accuracy |
| TransactionService.cs | 63 | Deposit needs tests for interest calculation | Add tests for interest bonus calculation |
| TransactionService.cs | 77 | IsWithinDailyLimit needs tests for transaction count | Add tests for daily transaction limits |
| AuthService.cs | 28 | Login needs tests for admin bypass | Add tests for admin bypass scenarios |
| AuthService.cs | 68 | GenerateJwtToken needs tests for token expiration | Add tests for token expiration scenarios |
| EmailService.cs | 34 | SendTransferNotification needs tests for retry logic | Add tests for email sending failures |
| EmailService.cs | 63 | SendWelcomeEmail needs tests for null username | Add tests for null username handling |
| DatabaseHelper.cs | 26 | ExecuteQuery needs tests for SQL injection | Add tests for SQL injection prevention |
| DatabaseHelper.cs | 36 | ExecuteQuerySafe needs tests for parameter binding | Add tests for parameter binding scenarios |
| DatabaseHelper.cs | 59 | TableExists needs tests for table name validation | Add tests for table name validation |
| StringHelper.cs | 11 | IsValidEmail needs tests for edge cases | Add tests for email validation edge cases |
| StringHelper.cs | 20 | IsValidUsername needs tests for boundary conditions | Add tests for username length boundaries |
| StringHelper.cs | 43 | MaskAccountNumber needs tests for short accounts | Add tests for account numbers with 4 or fewer digits |
| StringHelper.cs | 59 | ToTitleCase needs tests for empty input | Add tests for empty and null input |