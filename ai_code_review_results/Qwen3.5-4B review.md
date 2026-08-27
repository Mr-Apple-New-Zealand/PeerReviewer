## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 22 | Login endpoint passes user input directly to AuthService without validation or sanitization. | Add input validation and sanitize request data before passing to service. |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | `int.Parse(userIdClaim!)` throws exception if claim is null or non-numeric, causing unhandled exceptions. | Add null check and try-catch around `int.Parse` to return 400 Bad Request. |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | `int.Parse(userIdClaim!)` throws exception if claim is null or non-numeric, causing unhandled exceptions. | Add null check and try-catch around `int.Parse` to return 400 Bad Request. |
| SampleBankingApp/Controllers/UserController.cs | 48 | Returns raw `ex.Message` which may expose internal stack traces or sensitive data. | Return generic error message like "Invalid input" instead of exception message. |
| SampleBankingApp/Controllers/UserController.cs | 52 | Returns raw `ex.Message` which may expose internal stack traces or sensitive data. | Return generic error message like "Internal server error" instead of exception message. |
| SampleBankingApp/Controllers/UserController.cs | 67 | Returns generic message but logs full exception which may leak sensitive data. | Log only non-sensitive parts of exception or use structured logging. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded database credentials in constructor fallback string. | Remove hardcoded credentials and ensure configuration always provides valid connection string. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | SQL injection vulnerability via string interpolation in WHERE clause. | Use parameterized queries instead of string interpolation for dynamic table names and conditions. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52-55 | Connection opened but never disposed in `ExecuteNonQuery` method. | Use `using` statement or ensure connection is closed in finally block. |
| SampleBankingApp/Data/DatabaseHelper.cs | 63 | Table existence check uses `GetSchema` which may return unexpected results. | Use `SELECT EXISTS` query with proper parameterization for better reliability. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | Regex created inline instead of cached static readonly for repeated use. | Move regex to static readonly field and instantiate once. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | Regex created inline instead of cached static readonly for repeated use. | Move regex to static readonly field and instantiate once. |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` allows expired JWT tokens to be accepted. | Set `ValidateLifetime = true` and configure appropriate token expiration. |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` enabled in production environment. | Remove or conditionally enable based on environment setting. |
| SampleBankingApp/Program.cs | 38 | CORS policy allows any origin, method, and header without restrictions. | Restrict allowed origins, methods, and headers to specific values. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out, leaving app vulnerable to MITM attacks. | Uncomment and enable HTTPS redirection in production. |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection vulnerability via string interpolation in login query. | Use parameterized queries instead of string interpolation. |
| SampleBankingApp/Services/AuthService.cs | 34-38 | Connection opened but never disposed in `Login` method. | Use `using` statement or ensure connection is closed in finally block. |
| SampleBankingApp/Services/AuthService.cs | 53-55 | Hardcoded admin bypass password creates backdoor authentication. | Remove hardcoded bypass and implement proper admin authentication flow. |
| SampleBankingApp/Services/AuthService.cs | 63 | MD5 hashing used for password storage which is cryptographically weak. | Use bcrypt, Argon2, or PBKDF2 for password hashing. |
| SampleBankingApp/Services/AuthService.cs | 91 | SHA1 hashing used for password storage which is cryptographically weak. | Use bcrypt, Argon2, or PBKDF2 for password hashing. |
| SampleBankingApp/Services/AuthService.cs | 103 | `ValidateToken` method returns true unconditionally without actually validating token. | Implement proper token validation logic before returning true. |
| SampleBankingApp/Services/EmailService.cs | 29 | SSL disabled on SMTP client which may expose credentials in transit. | Enable SSL/TLS on SMTP client for secure communication. |
| SampleBankingApp/Services/EmailService.cs | 22-31 | SMTP client created without proper disposal and may leak resources. | Use `using` statement or ensure client is disposed in finally block. |
| SampleBankingApp/Services/TransactionService.cs | 47-48 | SQL injection vulnerability via string interpolation in UPDATE statements. | Use parameterized queries instead of string interpolation. |
| SampleBankingApp/Services/TransactionService.cs | 90 | SQL injection vulnerability via string interpolation in INSERT statement. | Use parameterized queries instead of string interpolation. |
| SampleBankingApp/Services/TransactionService.cs | 91 | Connection opened but never disposed in `RecordTransaction` method. | Use `using` statement or ensure connection is closed in finally block. |
| SampleBankingApp/Services/UserService.cs | 47 | SQL injection vulnerability via string interpolation in UPDATE statement. | Use parameterized queries instead of string interpolation. |
| SampleBankingApp/Services/UserService.cs | 61 | SQL injection vulnerability via string interpolation in DELETE statement. | Use parameterized queries instead of string interpolation. |
| SampleBankingApp/Services/UserService.cs | 99 | SQL injection vulnerability via LIKE clause with user input. | Use parameterized queries instead of string interpolation. |
| SampleBankingApp/Services/UserService.cs | 105-108 | Catch-all exception returns empty list which masks real errors. | Return appropriate error response or log error properly. |
| SampleBankingApp/Services/UserService.cs | 10 | Static `_auditLog` list shared across all instances without synchronization. | Use thread-safe collection or remove static state. |
| SampleBankingApp/Services/UserService.cs | 11 | Static `_requestCount` shared across all instances without synchronization. | Use thread-safe counter or remove static state. |
| SampleBankingApp/appsettings.json | 6 | Hardcoded JWT secret key in configuration file. | Use environment variables or secret management service for secrets. |
| SampleBankingApp/appsettings.json | 14 | Hardcoded email password in configuration file. | Use environment variables or secret management service for secrets. |
| SampleBankingApp/appsettings.json | 3 | Hardcoded database password in configuration file. | Use environment variables or secret management service for secrets. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check uses `>= amount` but deduction uses `amount + fee`, potentially allowing transfer with insufficient funds. | Change condition to `>= totalDebit` or adjust logic to check against totalDebit. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Interest bonus calculation multiplies by 1 which is redundant and may indicate incorrect formula. | Remove redundant multiplication or verify formula is correct. |
| SampleBankingApp/Services/TransactionService.cs | 72 | Interest bonus added to balance without checking if user has sufficient balance first. | Add balance check before applying interest bonus. |
| SampleBankingApp/Services/TransactionService.cs | 84 | Daily transaction limit check doesn't verify if user actually has transactions to count. | Add null check for table rows before accessing TxCount. |
| SampleBankingApp/Services/TransactionService.cs | 90 | Transaction description is interpolated directly into SQL without sanitization. | Use parameterized queries or sanitize description input. |
| SampleBankingApp/Services/UserService.cs | 20-23 | User ID validation allows IDs <= 0 and > 1000000 which may not match actual database constraints. | Align validation with actual database constraints or remove arbitrary limits. |
| SampleBankingApp/Services/UserService.cs | 72 | Pagination skip calculation uses `page * pageSize` instead of `(page-1) * pageSize`. | Change to `(page - 1) * pageSize` for correct pagination. |
| SampleBankingApp/Services/UserService.cs | 70 | Page size capped at 50 but no minimum validation which may allow empty results. | Add minimum page size validation or handle edge cases. |
| SampleBankingApp/Services/UserService.cs | 89-90 | Transaction description interpolated directly into SQL without sanitization. | Use parameterized queries or sanitize description input. |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 25 | Logs warning but doesn't handle potential exceptions from logger. | Add try-catch around logging or use structured logging. |
| SampleBankingApp/Controllers/TransactionController.cs | 56-59 | Catches NotImplementedException and returns 500 which masks real implementation issues. | Return 404 or 410 Not Implemented instead of 500. |
| SampleBankingApp/Controllers/UserController.cs | 46-49 | Catches ArgumentException and returns raw message which may expose internal details. | Return generic error message like "Invalid input". |
| SampleBankingApp/Controllers/UserController.cs | 50-53 | Catches all exceptions and returns raw message which may expose internal details. | Return generic error message like "Internal server error". |
| SampleBankingApp/Controllers/UserController.cs | 64-68 | Catches all exceptions and logs full exception which may leak sensitive data. | Log only non-sensitive parts of exception. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28-34 | No exception handling for database operations which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Data/DatabaseHelper.cs | 38-48 | No exception handling for database operations which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52-57 | No exception handling for database operations which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Helpers/StringHelper.cs | 13-18 | No null check on email parameter before length validation. | Add null check before accessing email.Length. |
| SampleBankingApp/Helpers/StringHelper.cs | 22-27 | No null check on username parameter before length validation. | Add null check before accessing username.Length. |
| SampleBankingApp/Helpers/StringHelper.cs | 45-52 | No null check on accountNumber parameter before length validation. | Add null check before accessing accountNumber.Length. |
| SampleBankingApp/Services/AuthService.cs | 30-59 | No exception handling for database operations which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Services/AuthService.cs | 70-89 | No exception handling for JWT token generation which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Services/EmailService.cs | 46-61 | No exception handling for SMTP operations which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Services/EmailService.cs | 71-79 | No exception handling for SMTP operations which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Services/TransactionService.cs | 23-61 | No exception handling for database operations which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Services/TransactionService.cs | 63-75 | No exception handling for database operations which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Services/TransactionService.cs | 77-85 | No exception handling for database operations which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Services/TransactionService.cs | 87-92 | No exception handling for database operations which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Services/UserService.cs | 18-36 | No exception handling for database operations which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Services/UserService.cs | 38-50 | No exception handling for database operations which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Services/UserService.cs | 52-66 | No exception handling for database operations which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Services/UserService.cs | 68-83 | No exception handling for database operations which may crash application. | Add try-catch blocks with proper error handling. |
| SampleBankingApp/Services/UserService.cs | 95-109 | Catches all exceptions and returns empty list which masks real errors. | Return appropriate error response or log error properly. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 20-24 | Connection opened but never disposed in `GetOpenConnection` method. | Use `using` statement or ensure connection is closed in finally block. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28-34 | Connection opened but never disposed in `ExecuteQuery` method. | Use `using` statement or ensure connection is closed in finally block. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52-57 | Connection opened but never disposed in `ExecuteNonQuery` method. | Use `using` statement or ensure connection is closed in finally block. |
| SampleBankingApp/Services/AuthService.cs | 34-38 | Connection opened but never disposed in `Login` method. | Use `using` statement or ensure connection is closed in finally block. |
| SampleBankingApp/Services/EmailService.cs | 16-32 | SmtpClient created as instance field and never disposed, causing socket leaks. | Use `using` statement or ensure client is disposed in finally block. |
| SampleBankingApp/Services/TransactionService.cs | 89-92 | Connection opened but never disposed in `RecordTransaction` method. | Use `using` statement or ensure connection is closed in finally block. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 22 | `request.Username` and `request.Password` may be null causing NullReferenceException. | Add null checks before using request properties. |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | `userIdClaim!` null-conditional operator may throw if claim is null. | Add null check before parsing userIdClaim. |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | `userIdClaim!` null-conditional operator may throw if claim is null. | Add null check before parsing userIdClaim. |
| SampleBankingApp/Controllers/UserController.cs | 43 | `request.Email` and `request.Username` may be null causing NullReferenceException. | Add null checks before using request properties. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | `_connectionString` may be null if configuration fails. | Add null check or provide default connection string. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `email.Length` accessed without null check on email parameter. | Add null check before accessing email.Length. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `username.Length` accessed without null check on username parameter. | Add null check before accessing username.Length. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `accountNumber.Length` accessed without null check on accountNumber parameter. | Add null check before accessing accountNumber.Length. |
| SampleBankingApp/Program.cs | 16 | `jwtSecret!` null-conditional operator may throw if configuration fails. | Add null check before using jwtSecret. |
| SampleBankingApp/Program.cs | 28 | `jwtSecret!` null-conditional operator may throw if configuration fails. | Add null check before using jwtSecret. |
| SampleBankingApp/Services/AuthService.cs | 30 | `HashPasswordMd5(password)` may throw if password is null. | Add null check before calling HashPasswordMd5. |
| SampleBankingApp/Services/AuthService.cs | 70 | `_config["Jwt:SecretKey"]!` null-conditional operator may throw if config fails. | Add null check before using jwtSecret. |
| SampleBankingApp/Services/EmailService.cs | 22 | `_config["Email:SmtpHost"]` may be null causing NullReferenceException. | Add null check before using SmtpHost. |
| SampleBankingApp/Services/EmailService.cs | 24 | `_config["Email:SmtpPort"]` may be null causing NullReferenceException. | Add null check before using SmtpPort. |
| SampleBankingApp/Services/EmailService.cs | 26 | `_config["Email:Password"]` may be null causing NullReferenceException. | Add null check before using EmailPassword. |
| SampleBankingApp/Services/TransactionService.cs | 28-34 | `fromUserTable.Rows[0]` accessed without checking if table has rows. | Add null check before accessing table rows. |
| SampleBankingApp/Services/TransactionService.cs | 32-37 | `toUserTable.Rows[0]` accessed without checking if table has rows. | Add null check before accessing table rows. |
| SampleBankingApp/Services/TransactionService.cs | 53 | `fromUserTable.Rows[0]["Email"]` accessed without checking if table has rows. | Add null check before accessing table rows. |
| SampleBankingApp/Services/TransactionService.cs | 55 | `toUserTable.Rows[0]["Username"]` accessed without checking if table has rows. | Add null check before accessing table rows. |
| SampleBankingApp/Services/UserService.cs | 27-35 | `table.Rows[0]` accessed without checking if table has rows. | Add null check before accessing table rows. |
| SampleBankingApp/Services/UserService.cs | 47 | `email` and `username` parameters may be null causing NullReferenceException. | Add null checks before using email and username. |
| SampleBankingApp/Services/UserService.cs | 99 | `query` parameter may be null causing NullReferenceException in LIKE clause. | Add null check before using query parameter. |
| SampleBankingApp/Services/UserService.cs | 116-121 | `row["Username"]`, `row["Email"]`, etc. accessed without checking if row exists. | Add null check before accessing row properties. |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 38-41 | `JoinWithSeparatorFixed` method exists but `JoinWithSeparator` is used instead. | Remove `JoinWithSeparatorFixed` or ensure it's called somewhere. |
| SampleBankingApp/Services/AuthService.cs | 91-96 | `HashPasswordSha1` method exists but `HashPasswordMd5` is used instead. | Remove `HashPasswordSha1` or ensure it's called somewhere. |
| SampleBankingApp/Services/EmailService.cs | 81-84 | `BuildHtmlTemplate` method exists but `SendWelcomeEmailHtml` uses string interpolation. | Remove `BuildHtmlTemplate` or ensure it's called somewhere. |
| SampleBankingApp/Services/TransactionService.cs | 94-97 | `FormatCurrency` method exists but is not called anywhere. | Remove `FormatCurrency` or ensure it's called somewhere. |
| SampleBankingApp/Services/UserService.cs | 85-93 | `GetAuditReport` method exists but is not called anywhere. | Remove `GetAuditReport` or ensure it's called somewhere. |
| SampleBankingApp/Services/UserService.cs | 95-109 | `SearchUsers` method exists but is not called anywhere. | Remove `SearchUsers` or ensure it's called somewhere. |
| SampleBankingApp/Services/UserService.cs | 111-123 | `MapRowToUser` method exists but is called from multiple places. | Keep `MapRowToUser` as it's used. |
| SampleBankingApp/Controllers/TransactionController.cs | 48-60 | `Refund` method exists but throws NotImplementedException. | Remove `Refund` method or implement the functionality. |
| SampleBankingApp/Services/TransactionService.cs | 99-103 | `RefundTransaction` method exists but throws NotImplementedException. | Remove `RefundTransaction` method or implement the functionality. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/TransactionController.cs | 24 | Magic number 20 for default page size. | Define constant `DefaultPageSize = 20`. |
| SampleBankingApp/Controllers/UserController.cs | 32 | Magic number 20 for default page size. | Define constant `DefaultPageSize = 20`. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | Magic number 254 for email length limit. | Define constant `MaxEmailLength = 254`. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | Magic numbers 3 and 20 for username length limits. | Define constants `MinUsernameLength = 3` and `MaxUsernameLength = 20`. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | Magic number 4 for account masking. | Define constant `MaskLength = 4`. |
| SampleBankingApp/Services/EmailService.cs | 10 | Magic string "Transfer Notification - BankingApp". | Define constant `TransferSubject = "Transfer Notification - BankingApp"`. |
| SampleBankingApp/Services/EmailService.cs | 11 | Magic string "Welcome to BankingApp!". | Define constant `WelcomeSubject = "Welcome to BankingApp!"`. |
| SampleBankingApp/Services/EmailService.cs | 13 | Magic number 3 for max retries. | Define constant `MaxRetries = 3`. |
| SampleBankingApp/Services/EmailService.cs | 14 | Magic number 5000 for SMTP timeout. | Define constant `SmtpTimeoutMs = 5000`. |
| SampleBankingApp/Services/TransactionService.cs | 11 | Magic number 0.015 for transaction fee rate. | Define constant `TransactionFeeRate = 0.015m`. |
| SampleBankingApp/Services/TransactionService.cs | 12 | Magic number 10 for max transactions per day. | Define constant `MaxTransactionsPerDay = 10`. |
| SampleBankingApp/Services/TransactionService.cs | 65 | Magic number 1000000 for max deposit amount. | Define constant `MaxDepositAmount = 1000000m`. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Magic number 0.05 for interest rate. | Define constant `InterestRate = 0.05m`. |
| SampleBankingApp/Services/UserService.cs | 22 | Magic number 1000000 for max user ID. | Define constant `MaxUserId = 1000000`. |
| SampleBankingApp/Services/UserService.cs | 70 | Magic number 50 for max page size. | Define constant `MaxPageSize = 50`. |
| SampleBankingApp/Services/UserService.cs | 10 | Magic string "UpdateUser called for id=" in audit log. | Define constant for audit log format. |
| SampleBankingApp/Services/UserService.cs | 11 | Magic string "DeleteUser:" in audit log. | Define constant for audit log format. |
| SampleBankingApp/Services/UserService.cs | 107 | Magic string "Users" in search query. | Define constant for table name. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 31-35 | String concatenation in loop instead of StringBuilder or string.Join. | Use `string.Join(separator, items)` instead of loop concatenation. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | Regex created inline instead of static readonly. | Move regex to static readonly field. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | Regex created inline instead of static readonly. | Move regex to static readonly field. |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` called unconditionally. | Remove or conditionally enable based on environment. |
| SampleBankingApp/Program.cs | 38 | `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is overly permissive. | Restrict allowed origins, methods, and headers. |
| SampleBankingApp/Services/AuthService.cs | 30-59 | Multiple responsibilities in `Login` method (validation, hashing, DB access, admin bypass). | Split into separate methods for validation, hashing, and authentication. |
| SampleBankingApp/Services/EmailService.cs | 34-61 | Multiple responsibilities in `SendTransferNotification` (retry logic, exception handling). | Split into separate methods for sending and retry logic. |
| SampleBankingApp/Services/EmailService.cs | 63-79 | Multiple responsibilities in `SendWelcomeEmail` (validation, sending, exception handling). | Split into separate methods for sending and exception handling. |
| SampleBankingApp/Services/TransactionService.cs | 23-61 | Multiple responsibilities in `Transfer` (validation, DB access, email sending). | Split into separate methods for validation, DB operations, and email sending. |
| SampleBankingApp/Services/TransactionService.cs | 63-75 | Multiple responsibilities in `Deposit` (validation, DB access, transaction recording). | Split into separate methods for validation, DB operations, and transaction recording. |
| SampleBankingApp/Services/TransactionService.cs | 77-85 | Multiple responsibilities in `IsWithinDailyLimit` (DB access, counting). | Split into separate methods for counting and limit checking. |
| SampleBankingApp/Services/TransactionService.cs | 87-92 | Multiple responsibilities in `RecordTransaction` (SQL construction, execution). | Split into separate methods for SQL construction and execution. |
| SampleBankingApp/Services/UserService.cs | 18-36 | Multiple responsibilities in `GetUserById` (validation, DB access, mapping). | Split into separate methods for validation, DB access, and mapping. |
| SampleBankingApp/Services/UserService.cs | 38-50 | Multiple responsibilities in `UpdateUser` (validation, DB access, audit logging). | Split into separate methods for validation, DB operations, and audit logging. |
| SampleBankingApp/Services/UserService.cs | 52-66 | Multiple responsibilities in `DeleteUser` (validation, DB access, audit logging). | Split into separate methods for validation, DB operations, and audit logging. |
| SampleBankingApp/Services/UserService.cs | 68-83 | Multiple responsibilities in `GetUsersPage` (validation, DB access, mapping). | Split into separate methods for validation, DB operations, and mapping. |
| SampleBankingApp/Services/UserService.cs | 95-109 | Multiple responsibilities in `SearchUsers` (validation, DB access, error handling). | Split into separate methods for validation, DB operations, and error handling. |
| SampleBankingApp/Services/UserService.cs | 10 | Static `_auditLog` list without synchronization. | Use thread-safe collection or remove static state. |
| SampleBankingApp/Services/UserService.cs | 11 | Static `_requestCount` without synchronization. | Use thread-safe counter or remove static state. |
| SampleBankingApp/Services/UserService.cs | 111-123 | `MapRowToUser` has multiple responsibilities (mapping, validation). | Split into separate methods for mapping and validation. |
| SampleBankingApp/Controllers/TransactionController.cs | 23-35 | Multiple responsibilities in `Transfer` (user ID parsing, service call, response). | Split into separate methods for user ID parsing and response handling. |
| SampleBankingApp/Controllers/TransactionController.cs | 37-46 | Multiple responsibilities in `Deposit` (user ID parsing, service call, response). | Split into separate methods for user ID parsing and response handling. |
| SampleBankingApp/Controllers/UserController.cs | 21-29 | Multiple responsibilities in `GetUser` (validation, service call, response). | Split into separate methods for validation and response handling. |
| SampleBankingApp/Controllers/UserController.cs | 31-36 | Multiple responsibilities in `GetUsers` (validation, service call, response). | Split into separate methods for validation and response handling. |
| SampleBankingApp/Controllers/UserController.cs | 38-54 | Multiple responsibilities in `UpdateUser` (validation, service call, error handling). | Split into separate methods for validation and error handling. |
| SampleBankingApp/Controllers/UserController.cs | 56-69 | Multiple responsibilities in `DeleteUser` (validation, service call, error handling). | Split into separate methods for validation and error handling. |
| SampleBankingApp/Controllers/UserController.cs | 71-76 | Multiple responsibilities in `SearchUsers` (validation, service call, response). | Split into separate methods for validation and response handling. |
| SampleBankingApp/Controllers/UserController.cs | 78-82 | Multiple responsibilities in `GetAuditLog` (validation, service call, response). | Split into separate methods for validation and response handling. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` on JWT configuration. | Set `ValidateLifetime = true` and configure appropriate expiration. |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` called unconditionally. | Remove or conditionally enable based on environment. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out. | Uncomment and enable HTTPS redirection in production. |
| SampleBankingApp/Program.cs | 38 | `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is overly permissive. | Restrict allowed origins, methods, and headers. |
| SampleBankingApp/Program.cs | 36 | Debug symbols enabled in release build. | Set `DebugSymbols` to false in release configuration. |
| SampleBankingApp/Program.cs | 36 | Debug type set to full in release build. | Set `DebugType` to portable or none in release configuration. |
| SampleBankingApp/Services/EmailService.cs | 29 | `EnableSsl = false` on SMTP client. | Enable SSL/TLS on SMTP client for secure communication. |
| SampleBankingApp/appsettings.json | 3 | Hardcoded database password in configuration file. | Use environment variables or secret management service. |
| SampleBankingApp/appsettings.json | 6 | Hardcoded JWT secret key in configuration file. | Use environment variables or secret management service. |
| SampleBankingApp/appsettings.json | 14 | Hardcoded email password in configuration file. | Use environment variables or secret management service. |
| SampleBankingApp/appsettings.json | 18-21 | Debug log level set for production namespaces. | Set appropriate log levels for production environment. |
| SampleBankingApp/appsettings.json | 23 | `AllowedHosts` set to "*" which is overly permissive. | Restrict allowed hosts to specific values. |
| SampleBankingApp/appsettings.json | 12 | Missing environment-specific configuration overrides. | Add `appsettings.Production.json` with environment-specific settings. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 19-31 | Login endpoint lacks unit tests for authentication flow. | Add tests for valid login, invalid credentials, and admin bypass. |
| SampleBankingApp/Controllers/TransactionController.cs | 23-35 | Transfer endpoint lacks unit tests for balance validation. | Add tests for sufficient funds, insufficient funds, and fee calculation. |
| SampleBankingApp/Controllers/TransactionController.cs | 37-46 | Deposit endpoint lacks unit tests for deposit validation. | Add tests for valid deposits, invalid amounts, and interest calculation. |
| SampleBankingApp/Controllers/TransactionController.cs | 48-60 | Refund endpoint lacks unit tests for implementation. | Add tests for refund functionality once implemented. |
| SampleBankingApp/Controllers/UserController.cs | 21-29 | GetUser endpoint lacks unit tests for user retrieval. | Add tests for valid user retrieval and not found scenarios. |
| SampleBankingApp/Controllers/UserController.cs | 31-36 | GetUsers endpoint lacks unit tests for pagination. | Add tests for pagination with correct skip and limit calculations. |
| SampleBankingApp/Controllers/UserController.cs | 38-54 | UpdateUser endpoint lacks unit tests for validation. | Add tests for valid updates, invalid inputs, and error handling. |
| SampleBankingApp/Controllers/UserController.cs | 56-69 | DeleteUser endpoint lacks unit tests for deletion. | Add tests for successful deletion and error scenarios. |
| SampleBankingApp/Controllers/UserController.cs | 71-76 | SearchUsers endpoint lacks unit tests for search functionality. | Add tests for search with various query patterns. |
| SampleBankingApp/Services/AuthService.cs | 28-59 | Login method lacks unit tests for authentication. | Add tests for valid login, invalid credentials, and admin bypass. |
| SampleBankingApp/Services/AuthService.cs | 68-89 | GenerateJwtToken method lacks unit tests for token generation. | Add tests for valid token generation and expiration. |
| SampleBankingApp/Services/AuthService.cs | 98-108 | ValidateToken method lacks unit tests for token validation. | Add tests for valid and invalid token scenarios. |
| SampleBankingApp/Services/EmailService.cs | 34-61 | SendTransferNotification method lacks unit tests for email sending. | Add tests for successful sending, retries, and failures. |
| SampleBankingApp/Services/EmailService.cs | 63-79 | SendWelcomeEmail method lacks unit tests for email sending. | Add tests for successful sending and failure scenarios. |
| SampleBankingApp/Services/TransactionService.cs | 23-61 | Transfer method lacks unit tests for transaction logic. | Add tests for balance validation, fee calculation, and transaction recording. |
| SampleBankingApp/Services/TransactionService.cs | 63-75 | Deposit method lacks unit tests for deposit logic. | Add tests for valid deposits, invalid amounts, and interest calculation. |
| SampleBankingApp/Services/TransactionService.cs | 77-85 | IsWithinDailyLimit method lacks unit tests for limit checking. | Add tests for daily transaction limit validation. |
| SampleBankingApp/Services/TransactionService.cs | 87-92 | RecordTransaction method lacks unit tests for transaction recording. | Add tests for successful transaction recording. |
| SampleBankingApp/Services/UserService.cs | 18-36 | GetUserById method lacks unit tests for user retrieval. | Add tests for valid user retrieval and not found scenarios. |
| SampleBankingApp/Services/UserService.cs | 38-50 | UpdateUser method lacks unit tests for user updates. | Add tests for valid updates and error scenarios. |
| SampleBankingApp/Services/UserService.cs | 52-66 | DeleteUser method lacks unit tests for user deletion. | Add tests for successful deletion and error scenarios. |
| SampleBankingApp/Services/UserService.cs | 68-83 | GetUsersPage method lacks unit tests for pagination. | Add tests for pagination with correct skip and limit calculations. |
| SampleBankingApp/Services/UserService.cs | 95-109 | SearchUsers method lacks unit tests for search functionality. | Add tests for search with various query patterns. |