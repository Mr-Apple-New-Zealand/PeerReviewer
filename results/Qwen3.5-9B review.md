## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| **AuthController.cs** | 17-22 | No ownership check on `Login` allows any user to authenticate; no password hashing in service layer. | Implement `Authorize` attribute on `Login` and move password hashing to `AuthService`. |
| **TransactionController.cs** | 17-22 | `int.Parse(userIdClaim!)` throws if claim is missing; no validation of `toUserId` ownership. | Add null check for `userIdClaim` and validate `toUserId` exists and differs from `fromUserId`. |
| **TransactionController.cs** | 39-45 | `catch (NotImplementedException)` returns 500 with message; exposes internal implementation details. | Catch generic `Exception` and log internally without exposing stack traces or internal state. |
| **DatabaseHelper.cs** | 14-15 | Hardcoded SQL Server credentials (`sa`/`Admin1234!`) in constructor fallback. | Remove fallback credentials; require configuration or fail start if missing. |
| **DatabaseHelper.cs** | 23-26 | `ExecuteQuery` uses string interpolation for SQL, enabling SQL injection. | Replace with parameterized queries using `ExecuteQuerySafe`. |
| **DatabaseHelper.cs** | 31-38 | `ExecuteQuerySafe` uses `AddWithValue` which can cause type mismatches and injection risks. | Use explicit `SqlParameter` types instead of `AddWithValue`. |
| **DatabaseHelper.cs** | 43-48 | `ExecuteNonQuery` uses string interpolation and leaves connection open in some paths. | Use parameterized queries and ensure `using` blocks for all database objects. |
| **DatabaseHelper.cs** | 63-69 | `ExecuteQueryWithParams` is marked `[Obsolete]` but still contains string interpolation. | Remove or fully refactor to use parameters before deletion. |
| **StringHelper.cs** | 14-17 | Regex compiled inside `IsValidEmail` method; inefficient for repeated calls. | Make Regex instance `static readonly`. |
| **StringHelper.cs** | 22-25 | Regex compiled inside `IsValidUsername` method; inefficient for repeated calls. | Make Regex instance `static readonly`. |
| **StringHelper.cs** | 28-34 | String concatenation in loop inside `JoinWithSeparator` causes O(n²) performance. | Replace with `string.Join`. |
| **Models/User.cs** | 6 | Password stored in plain text model; no hashing indicated. | Hash passwords before storage and never expose plain text passwords. |
| **Program.cs** | 23 | JWT `ValidateLifetime` set to `false` allowing expired tokens. | Set `ValidateLifetime = true` to enforce expiration. |
| **Program.cs** | 30 | `UseDeveloperExceptionPage()` enabled in production code. | Remove or guard behind `app.Environment.IsDevelopment()`. |
| **Program.cs** | 33 | CORS policy allows any origin, method, and header unconditionally. | Restrict CORS to specific origins and methods required by the API. |
| **Program.cs** | 35 | HTTPS redirection is commented out, serving traffic over HTTP. | Uncomment `app.UseHttpsRedirection()`. |
| **Program.cs** | 39 | Debug symbols enabled in project file for release builds. | Set `<DebugSymbols>false</DebugSymbols>` and `<DebugType>pdbonly</DebugType>`. |
| **Services/AuthService.cs** | 22 | Hardcoded `AdminBypassPassword` bypasses authentication logic. | Remove hardcoded bypass; require valid database record for admin login. |
| **Services/AuthService.cs** | 29-38 | SQL injection vulnerability in `Login` method via string interpolation. | Use parameterized queries with `ExecuteQuerySafe`. |
| **Services/AuthService.cs** | 41-48 | MD5 hashing used for passwords; weak cryptography. | Replace MD5 with bcrypt or Argon2. |
| **Services/AuthService.cs** | 59-65 | Hardcoded JWT secret key length is weak and stored in config. | Use a cryptographically strong random key (min 32 bytes). |
| **Services/AuthService.cs** | 102-108 | `ValidateToken` returns `true` unconditionally after null check. | Complete the validation logic to check token validity. |
| **Services/AuthService.cs** | 110-116 | `HashPasswordSha1` uses SHA1; weak cryptography. | Remove unused method or replace with strong hashing. |
| **Services/EmailService.cs** | 14-21 | SMTP credentials and password hardcoded in configuration file. | Use environment variables or secure vault for credentials. |
| **Services/EmailService.cs** | 23-30 | `SmtpClient` created as instance field; socket may leak on shutdown. | Use `using` block or dispose client after sending. |
| **Services/EmailService.cs** | 48-54 | Console.WriteLine used for logging; exposes stack traces or messages. | Use `ILogger` for production logging. |
| **Services/EmailService.cs** | 61-67 | Hardcoded email addresses (`notifications@company.com`, `support@company.com`). | Use configuration values for email addresses. |
| **Services/TransactionService.cs** | 20-26 | SQL injection in `Transfer` via string interpolation for balance update. | Use parameterized queries for balance updates. |
| **Services/TransactionService.cs** | 42-48 | SQL injection in `Deposit` via string interpolation for balance update. | Use parameterized queries for balance updates. |
| **Services/TransactionService.cs** | 53-58 | SQL injection in `IsWithinDailyLimit` via string interpolation. | Use parameterized queries. |
| **Services/TransactionService.cs** | 60-66 | SQL injection in `RecordTransaction` via string interpolation. | Use parameterized queries. |
| **Services/TransactionService.cs** | 71-75 | Hardcoded transaction fee rate and daily limit constants. | Move constants to configuration or named constants. |
| **Services/UserService.cs** | 26-32 | SQL injection in `GetUserById` via string interpolation. | Use parameterized queries. |
| **Services/UserService.cs** | 40-45 | SQL injection in `UpdateUser` via string interpolation. | Use parameterized queries. |
| **Services/UserService.cs** | 51-56 | SQL injection in `DeleteUser` via string interpolation. | Use parameterized queries. |
| **Services/UserService.cs** | 64-69 | SQL injection in `GetUsersPage` via string interpolation. | Use parameterized queries. |
| **Services/UserService.cs** | 82-88 | SQL injection in `SearchUsers` via string interpolation. | Use parameterized queries. |
| **Services/UserService.cs** | 91-100 | String concatenation in `GetAuditReport` loop. | Use `StringBuilder` or `string.Join`. |
| **appsettings.json** | 3 | Hardcoded database password in connection string. | Use environment variables or a secrets manager. |
| **appsettings.json** | 10 | Hardcoded JWT secret key in config file. | Use environment variables or a secrets manager. |
| **appsettings.json** | 18 | Hardcoded email password in config file. | Use environment variables or a secrets manager. |
| **appsettings.json** | 23 | Debug logging level set for production. | Set `LogLevel` to `Information` or `Warning` for production. |
| **appsettings.json** | 26 | `AllowedHosts` set to wildcard allowing any host. | Restrict to specific allowed hosts or domains. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| **TransactionController.cs** | 17-22 | `int.Parse(userIdClaim!)` throws if claim is missing; no null check. | Add null check before parsing `userIdClaim`. |
| **TransactionController.cs** | 39-45 | `catch (NotImplementedException)` returns 500 with message; incorrect error handling. | Catch generic `Exception` and return generic error. |
| **Services/AuthService.cs** | 29-38 | `Login` returns hardcoded admin user without checking password hash. | Ensure admin login uses hashed password comparison. |
| **Services/AuthService.cs** | 102-108 | `ValidateToken` returns `true` unconditionally after null check. | Complete the validation logic to check token validity. |
| **Services/EmailService.cs** | 61-67 | Hardcoded email addresses (`notifications@company.com`, `support@company.com`). | Use configuration values for email addresses. |
| **Services/TransactionService.cs** | 20-26 | `Transfer` deducts fee from balance but checks `amount` only; logic error. | Check `fromBalance >= amount + fee` before deducting. |
| **Services/TransactionService.cs** | 42-48 | `Deposit` adds `amount` twice to balance due to `amount + interestBonus` syntax. | Correct calculation to `Balance + amount + interestBonus`. |
| **Services/TransactionService.cs** | 53-58 | `IsWithinDailyLimit` uses `GETDATE()` which is not portable across environments. | Use parameterized date comparison for portability. |
| **Services/TransactionService.cs** | 60-66 | `RecordTransaction` uses `GETDATE()` which is not portable across environments. | Use parameterized date for portability. |
| **Services/UserService.cs** | 64-69 | `GetUsersPage` calculates `skip` as `page * pageSize` instead of `(page - 1) * pageSize`. | Fix pagination calculation to `(page - 1) * pageSize`. |
| **Services/UserService.cs** | 82-88 | `GetAuditReport` uses string concatenation in loop; inefficient. | Use `StringBuilder` or `string.Join`. |
| **Services/UserService.cs** | 91-100 | `SearchUsers` catches all exceptions and returns empty list; hides errors. | Catch specific exceptions or log generic errors. |
| **Services/UserService.cs** | 100-107 | `MapRowToUser` accesses `row["IsActive"]` without checking null/missing column. | Add null check for column existence. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| **AuthController.cs** | 17-22 | No exception handling for `Login` method; potential crashes. | Wrap `Login` call in try-catch for broader exceptions. |
| **TransactionController.cs** | 17-22 | `int.Parse(userIdClaim!)` throws if claim is missing; no null check. | Add null check before parsing `userIdClaim`. |
| **TransactionController.cs** | 39-45 | `catch (NotImplementedException)` returns 500 with message; exposes internal state. | Catch generic `Exception` and return generic error. |
| **UserController.cs** | 27-34 | `catch (Exception)` returns `ex.Message` to client; exposes stack traces. | Log error internally and return generic error message. |
| **UserController.cs** | 36-41 | `catch (Exception)` returns generic error but logs full stack trace; inefficient. | Log error internally and return generic error message. |
| **UserController.cs** | 50-55 | `SearchUsers` catches all exceptions and returns empty list; hides errors. | Catch specific exceptions or log generic errors. |
| **DatabaseHelper.cs** | 23-26 | `ExecuteQuery` has no error handling for SQL failures. | Add try-catch block for SQL errors. |
| **DatabaseHelper.cs** | 31-38 | `ExecuteQuerySafe` has no error handling for SQL failures. | Add try-catch block for SQL errors. |
| **DatabaseHelper.cs** | 43-48 | `ExecuteNonQuery` has no error handling for SQL failures. | Add try-catch block for SQL errors. |
| **DatabaseHelper.cs** | 63-69 | `ExecuteQueryWithParams` has no error handling for SQL failures. | Add try-catch block for SQL errors. |
| **StringHelper.cs** | 14-17 | `IsValidEmail` has no error handling for invalid regex. | Wrap regex match in try-catch. |
| **StringHelper.cs** | 22-25 | `IsValidUsername` has no error handling for invalid regex. | Wrap regex match in try-catch. |
| **Services/AuthService.cs** | 29-38 | `Login` has no error handling for SQL failures. | Add try-catch block for SQL errors. |
| **Services/AuthService.cs** | 59-65 | `GenerateJwtToken` has no error handling for config missing. | Add null check for `Jwt:SecretKey`. |
| **Services/AuthService.cs** | 102-108 | `ValidateToken` returns `true` unconditionally after null check. | Complete the validation logic to check token validity. |
| **Services/EmailService.cs** | 48-54 | `SendTransferNotification` logs to console; exposes stack traces. | Use `ILogger` for production logging. |
| **Services/EmailService.cs** | 61-67 | `SendWelcomeEmail` logs to console; exposes stack traces. | Use `ILogger` for production logging. |
| **Services/TransactionService.cs** | 20-26 | `Transfer` has no error handling for SQL failures. | Add try-catch block for SQL errors. |
| **Services/TransactionService.cs** | 42-48 | `Deposit` has no error handling for SQL failures. | Add try-catch block for SQL errors. |
| **Services/TransactionService.cs** | 53-58 | `IsWithinDailyLimit` has no error handling for SQL failures. | Add try-catch block for SQL errors. |
| **Services/TransactionService.cs** | 60-66 | `RecordTransaction` has no error handling for SQL failures. | Add try-catch block for SQL errors. |
| **Services/UserService.cs** | 26-32 | `GetUserById` has no error handling for SQL failures. | Add try-catch block for SQL errors. |
| **Services/UserService.cs** | 40-45 | `UpdateUser` has no error handling for SQL failures. | Add try-catch block for SQL errors. |
| **Services/UserService.cs** | 51-56 | `DeleteUser` has no error handling for SQL failures. | Add try-catch block for SQL errors. |
| **Services/UserService.cs** | 64-69 | `GetUsersPage` has no error handling for SQL failures. | Add try-catch block for SQL errors. |
| **Services/UserService.cs** | 82-88 | `GetAuditReport` has no error handling for empty audit log. | Add null check for audit log. |
| **Services/UserService.cs** | 91-100 | `SearchUsers` catches all exceptions and returns empty list; hides errors. | Catch specific exceptions or log generic errors. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| **DatabaseHelper.cs** | 23-26 | `ExecuteQuery` uses `GetOpenConnection` which never closes connection. | Use `using` block for connection. |
| **DatabaseHelper.cs** | 31-38 | `ExecuteQuerySafe` uses `using` for command but not connection in some paths. | Ensure all database objects are disposed. |
| **DatabaseHelper.cs** | 43-48 | `ExecuteNonQuery` uses `GetOpenConnection` which never closes connection. | Use `using` block for connection. |
| **DatabaseHelper.cs** | 63-69 | `ExecuteQueryWithParams` uses `using` for command but not connection in some paths. | Ensure all database objects are disposed. |
| **EmailService.cs** | 23-30 | `SmtpClient` created as instance field; socket may leak on shutdown. | Use `using` block or dispose client after sending. |
| **EmailService.cs** | 48-54 | `SendTransferNotification` creates `MailMessage` but never disposes it. | Use `using` block for `MailMessage`. |
| **EmailService.cs** | 61-67 | `SendWelcomeEmail` creates `MailMessage` but never disposes it. | Use `using` block for `MailMessage`. |
| **Services/TransactionService.cs** | 20-26 | `Transfer` uses `ExecuteQuerySafe` which may leak resources. | Ensure `ExecuteQuerySafe` disposes all resources. |
| **Services/TransactionService.cs** | 42-48 | `Deposit` uses `ExecuteNonQuery` which may leak resources. | Ensure `ExecuteNonQuery` disposes all resources. |
| **Services/TransactionService.cs** | 53-58 | `IsWithinDailyLimit` uses `ExecuteQuerySafe` which may leak resources. | Ensure `ExecuteQuerySafe` disposes all resources. |
| **Services/TransactionService.cs** | 60-66 | `RecordTransaction` uses `ExecuteNonQuery` which may leak resources. | Ensure `ExecuteNonQuery` disposes all resources. |
| **Services/UserService.cs** | 26-32 | `GetUserById` uses `ExecuteQuerySafe` which may leak resources. | Ensure `ExecuteQuerySafe` disposes all resources. |
| **Services/UserService.cs** | 40-45 | `UpdateUser` uses `ExecuteNonQuery` which may leak resources. | Ensure `ExecuteNonQuery` disposes all resources. |
| **Services/UserService.cs** | 51-56 | `DeleteUser` uses `ExecuteNonQuery` which may leak resources. | Ensure `ExecuteNonQuery` disposes all resources. |
| **Services/UserService.cs** | 64-69 | `GetUsersPage` uses `ExecuteQuerySafe` which may leak resources. | Ensure `ExecuteQuerySafe` disposes all resources. |
| **Services/UserService.cs** | 82-88 | `GetAuditReport` creates `StringBuilder` but never disposes it. | Use `StringBuilder` properly or use `string.Join`. |
| **Services/UserService.cs** | 91-100 | `SearchUsers` uses `ExecuteQuery` which may leak resources. | Ensure `ExecuteQuery` disposes all resources. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| **AuthController.cs** | 17-22 | `Login` method may throw `NullReferenceException` if request is null. | Add null check for `LoginRequest`. |
| **TransactionController.cs** | 17-22 | `int.Parse(userIdClaim!)` throws if claim is missing; no null check. | Add null check before parsing `userIdClaim`. |
| **TransactionController.cs** | 39-45 | `catch (NotImplementedException)` returns 500 with message; exposes internal state. | Catch generic `Exception` and return generic error. |
| **UserController.cs** | 27-34 | `catch (Exception)` returns `ex.Message` to client; exposes stack traces. | Log error internally and return generic error message. |
| **UserController.cs** | 36-41 | `catch (Exception)` returns generic error but logs full stack trace; inefficient. | Log error internally and return generic error message. |
| **UserController.cs** | 50-55 | `SearchUsers` catches all exceptions and returns empty list; hides errors. | Catch specific exceptions or log generic errors. |
| **DatabaseHelper.cs** | 14-15 | `GetOpenConnection` may throw `NullReferenceException` if config is null. | Add null check for `configuration`. |
| **DatabaseHelper.cs** | 23-26 | `ExecuteQuery` uses `GetOpenConnection` which may throw `NullReferenceException`. | Add null check for `connectionString`. |
| **DatabaseHelper.cs** | 31-38 | `ExecuteQuerySafe` uses `AddWithValue` which may throw `NullReferenceException`. | Use explicit `SqlParameter` types. |
| **DatabaseHelper.cs** | 43-48 | `ExecuteNonQuery` uses `GetOpenConnection` which may throw `NullReferenceException`. | Add null check for `connectionString`. |
| **DatabaseHelper.cs** | 63-69 | `ExecuteQueryWithParams` uses `AddWithValue` which may throw `NullReferenceException`. | Use explicit `SqlParameter` types. |
| **StringHelper.cs** | 14-17 | `IsValidEmail` may throw `NullReferenceException` if email is null. | Add null check for `email`. |
| **StringHelper.cs** | 22-25 | `IsValidUsername` may throw `NullReferenceException` if username is null. | Add null check for `username`. |
| **StringHelper.cs** | 28-34 | `JoinWithSeparator` may throw `NullReferenceException` if items is null. | Add null check for `items`. |
| **StringHelper.cs** | 38-44 | `MaskAccountNumber` may throw `NullReferenceException` if accountNumber is null. | Add null check for `accountNumber`. |
| **StringHelper.cs** | 47-52 | `ObfuscateAccount` may throw `NullReferenceException` if account is null. | Add null check for `account`. |
| **StringHelper.cs** | 55-59 | `ToTitleCase` may throw `NullReferenceException` if input is null. | Add null check for `input`. |
| **StringHelper.cs** | 62-67 | `IsBlank` may throw `NullReferenceException` if value is null. | Add null check for `value`. |
| **Services/AuthService.cs** | 29-38 | `Login` may throw `NullReferenceException` if username or password is null. | Add null check for `username` and `password`. |
| **Services/AuthService.cs** | 59-65 | `GenerateJwtToken` may throw `NullReferenceException` if config is null. | Add null check for `Jwt:SecretKey`. |
| **Services/AuthService.cs** | 102-108 | `ValidateToken` returns `true` unconditionally after null check. | Complete the validation logic to check token validity. |
| **Services/EmailService.cs** | 14-21 | `SmtpClient` may throw `NullReferenceException` if config is null. | Add null check for `config`. |
| **Services/EmailService.cs** | 48-54 | `SendTransferNotification` may throw `NullReferenceException` if toEmail is null. | Add null check for `toEmail`. |
| **Services/EmailService.cs** | 61-67 | `SendWelcomeEmail` may throw `NullReferenceException` if toEmail is null. | Add null check for `toEmail`. |
| **Services/TransactionService.cs** | 20-26 | `Transfer` may throw `NullReferenceException` if description is null. | Add null check for `description`. |
| **Services/TransactionService.cs** | 42-48 | `Deposit` may throw `NullReferenceException` if description is null. | Add null check for `description`. |
| **Services/TransactionService.cs** | 53-58 | `IsWithinDailyLimit` may throw `NullReferenceException` if userId is null. | Add null check for `userId`. |
| **Services/TransactionService.cs** | 60-66 | `RecordTransaction` may throw `NullReferenceException` if description is null. | Add null check for `description`. |
| **Services/UserService.cs** | 26-32 | `GetUserById` may throw `NullReferenceException` if id is null. | Add null check for `id`. |
| **Services/UserService.cs** | 40-45 | `UpdateUser` may throw `NullReferenceException` if email or username is null. | Add null check for `email` and `username`. |
| **Services/UserService.cs** | 51-56 | `DeleteUser` may throw `NullReferenceException` if id is null. | Add null check for `id`. |
| **Services/UserService.cs** | 64-69 | `GetUsersPage` may throw `NullReferenceException` if page or pageSize is null. | Add null check for `page` and `pageSize`. |
| **Services/UserService.cs** | 82-88 | `GetAuditReport` may throw `NullReferenceException` if auditLog is null. | Add null check for `auditLog`. |
| **Services/UserService.cs** | 91-100 | `SearchUsers` may throw `NullReferenceException` if query is null. | Add null check for `query`. |
| **Services/UserService.cs** | 100-107 | `MapRowToUser` may throw `NullReferenceException` if row is null. | Add null check for `row`. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| **DatabaseHelper.cs** | 63-69 | `ExecuteQueryWithParams` is marked `[Obsolete]` but still present. | Remove or fully refactor to use parameters before deletion. |
| **Services/AuthService.cs** | 110-116 | `HashPasswordSha1` is unused and uses weak cryptography. | Remove unused method. |
| **Services/EmailService.cs** | 68-73 | `BuildHtmlTemplate` is unused and creates HTML template. | Remove unused method. |
| **Services/EmailService.cs** | 75-80 | `SendWelcomeEmailHtml` is unused and creates HTML email. | Remove unused method. |
| **Services/TransactionService.cs** | 71-75 | `FormatCurrency` is unused and formats currency. | Remove unused method. |
| **Services/TransactionService.cs** | 81-86 | `RefundTransaction` is unused and throws `NotImplementedException`. | Remove or implement method. |
| **Services/UserService.cs** | 91-100 | `GetAuditReport` is unused and returns audit log. | Remove or implement method. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| **StringHelper.cs** | 14-17 | Magic number `254` for email length limit; should be named constant. | Define `MAX_EMAIL_LENGTH` constant. |
| **StringHelper.cs** | 22-25 | Magic numbers `3` and `20` for username length limits; should be named constants. | Define `MIN_USERNAME_LENGTH` and `MAX_USERNAME_LENGTH` constants. |
| **StringHelper.cs** | 38-44 | Magic number `4` for account number masking; should be named constant. | Define `ACCOUNT_NUMBER_MASK_LENGTH` constant. |
| **Services/AuthService.cs** | 22 | Magic string `SuperAdmin2024` for admin bypass password. | Use configuration or remove hardcoded bypass. |
| **Services/AuthService.cs** | 65 | Magic number `30` for JWT expiration in days; should be named constant. | Define `JWT_EXPIRY_DAYS` constant. |
| **Services/EmailService.cs** | 14-21 | Magic strings `TransferSubject` and `WelcomeSubject`; should be named constants. | Define `TRANSFER_SUBJECT` and `WELCOME_SUBJECT` constants. |
| **Services/EmailService.cs** | 23-30 | Magic numbers `3` and `5000` for retry count and timeout; should be named constants. | Define `MAX_RETRIES` and `SMTP_TIMEOUT_MS` constants. |
| **Services/EmailService.cs** | 61-67 | Magic strings `notifications@company.com` and `support@company.com`; should be configuration. | Use configuration values for email addresses. |
| **Services/TransactionService.cs** | 20-26 | Magic number `0.015` for transaction fee rate; should be named constant. | Define `TRANSACTION_FEE_RATE` constant. |
| **Services/TransactionService.cs** | 27-33 | Magic number `10` for max transactions per day; should be named constant. | Define `MAX_TRANSACTIONS_PER_DAY` constant. |
| **Services/TransactionService.cs** | 42-48 | Magic number `0.05` for interest bonus rate; should be named constant. | Define `INTEREST_BONUS_RATE` constant. |
| **Services/TransactionService.cs** | 60-66 | Magic number `1000000` for deposit amount limit; should be named constant. | Define `MAX_DEPOSIT_AMOUNT` constant. |
| **Services/TransactionService.cs** | 81-86 | Magic number `0` for `fromId` in `RefundTransaction`; should be named constant. | Define `SYSTEM_USER_ID` constant. |
| **Services/UserService.cs** | 26-32 | Magic number `1000000` for user ID limit; should be named constant. | Define `MAX_USER_ID` constant. |
| **Services/UserService.cs** | 64-69 | Magic number `50` for page size limit; should be named constant. | Define `MAX_PAGE_SIZE` constant. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| **StringHelper.cs** | 14-17 | `IsValidEmail` uses regex inside method; should be `static readonly`. | Make Regex instance `static readonly`. |
| **StringHelper.cs** | 22-25 | `IsValidUsername` uses regex inside method; should be `static readonly`. | Make Regex instance `static readonly`. |
| **StringHelper.cs** | 28-34 | String concatenation in loop inside `JoinWithSeparator` causes O(n²) performance. | Replace with `string.Join`. |
| **StringHelper.cs** | 47-52 | `ObfuscateAccount` uses slicing which is inefficient for large strings. | Use `StringBuilder` for better performance. |
| **Services/AuthService.cs** | 29-38 | `Login` uses string interpolation for SQL; should use parameterized queries. | Use parameterized queries with `ExecuteQuerySafe`. |
| **Services/AuthService.cs** | 102-108 | `ValidateToken` returns `true` unconditionally after null check. | Complete the validation logic to check token validity. |
| **Services/EmailService.cs** | 48-54 | `SendTransferNotification` logs to console; should use `ILogger`. | Use `ILogger` for production logging. |
| **Services/EmailService.cs** | 61-67 | `SendWelcomeEmail` logs to console; should use `ILogger`. | Use `ILogger` for production logging. |
| **Services/TransactionService.cs** | 20-26 | `Transfer` uses string interpolation for SQL; should use parameterized queries. | Use parameterized queries with `ExecuteQuerySafe`. |
| **Services/TransactionService.cs** | 42-48 | `Deposit` uses string interpolation for SQL; should use parameterized queries. | Use parameterized queries with `ExecuteQuerySafe`. |
| **Services/TransactionService.cs** | 53-58 | `IsWithinDailyLimit` uses `GETDATE()` which is not portable across environments. | Use parameterized date comparison for portability. |
| **Services/TransactionService.cs** | 60-66 | `RecordTransaction` uses string interpolation for SQL; should use parameterized queries. | Use parameterized queries with `ExecuteQuerySafe`. |
| **Services/TransactionService.cs** | 71-75 | `FormatCurrency` is unused and formats currency. | Remove unused method. |
| **Services/TransactionService.cs** | 81-86 | `RefundTransaction` is unused and throws `NotImplementedException`. | Remove or implement method. |
| **Services/UserService.cs** | 26-32 | `GetUserById` uses string interpolation for SQL; should use parameterized queries. | Use parameterized queries with `ExecuteQuerySafe`. |
| **Services/UserService.cs** | 40-45 | `UpdateUser` uses string interpolation for SQL; should use parameterized queries. | Use parameterized queries with `ExecuteQuerySafe`. |
| **Services/UserService.cs** | 51-56 | `DeleteUser` uses string interpolation for SQL; should use parameterized queries. | Use parameterized queries with `ExecuteQuerySafe`. |
| **Services/UserService.cs** | 64-69 | `GetUsersPage` uses string interpolation for SQL; should use parameterized queries. | Use parameterized queries with `ExecuteQuerySafe`. |
| **Services/UserService.cs** | 82-88 | `GetAuditReport` uses string concatenation in loop; should use `StringBuilder`. | Use `StringBuilder` or `string.Join`. |
| **Services/UserService.cs** | 91-100 | `SearchUsers` catches all exceptions and returns empty list; hides errors. | Catch specific exceptions or log generic errors. |
| **Services/UserService.cs** | 100-107 | `MapRowToUser` accesses `row["IsActive"]` without checking null/missing column. | Add null check for column existence. |
| **appsettings.json** | 23 | Debug logging level set for production; should be `Information` or `Warning`. | Set `LogLevel` to `Information` or `Warning` for production. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| **Program.cs** | 23 | `UseDeveloperExceptionPage()` enabled in production code. | Remove or guard behind `app.Environment.IsDevelopment()`. |
| **Program.cs** | 33 | CORS policy allows any origin, method, and header unconditionally. | Restrict CORS to specific origins and methods required by the API. |
| **Program.cs** | 35 | HTTPS redirection is commented out, serving traffic over HTTP. | Uncomment `app.UseHttpsRedirection()`. |
| **Program.cs** | 39 | Debug symbols enabled in project file for release builds. | Set `<DebugSymbols>false</DebugSymbols>` and `<DebugType>pdbonly</DebugType>`. |
| **appsettings.json** | 3 | Hardcoded database password in connection string. | Use environment variables or a secrets manager. |
| **appsettings.json** | 10 | Hardcoded JWT secret key in config file. | Use environment variables or a secrets manager. |
| **appsettings.json** | 18 | Hardcoded email password in config file. | Use environment variables or a secrets manager. |
| **appsettings.json** | 23 | Debug logging level set for production. | Set `LogLevel` to `Information` or `Warning` for production. |
| **appsettings.json** | 26 | `AllowedHosts` set to wildcard allowing any host. | Restrict to specific allowed hosts or domains. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| **SampleBankingApp/Controllers/AuthController.cs** | 17-22 | No unit tests for `Login` method; boundary conditions not covered. | Add unit tests for `Login` method with valid/invalid credentials. |
| **SampleBankingApp/Controllers/TransactionController.cs** | 17-22 | No unit tests for `Transfer` method; boundary conditions not covered. | Add unit tests for `Transfer` method with valid/invalid amounts. |
| **SampleBankingApp/Controllers/TransactionController.cs** | 39-45 | No unit tests for `Refund` method; boundary conditions not covered. | Add unit tests for `Refund` method with valid/invalid transaction IDs. |
| **SampleBankingApp/Controllers/UserController.cs** | 27-34 | No unit tests for `GetUser` method; boundary conditions not covered. | Add unit tests for `GetUser` method with valid/invalid user IDs. |
| **SampleBankingApp/Controllers/UserController.cs** | 36-41 | No unit tests for `UpdateUser` method; boundary conditions not covered. | Add unit tests for `UpdateUser` method with valid/invalid user IDs. |
| **SampleBankingApp/Controllers/UserController.cs** | 50-55 | No unit tests for `SearchUsers` method; boundary conditions not covered. | Add unit tests for `SearchUsers` method with valid/invalid queries. |
| **SampleBankingApp/Services/AuthService.cs** | 29-38 | No unit tests for `Login` method; boundary conditions not covered. | Add unit tests for `Login` method with valid/invalid credentials. |
| **SampleBankingApp/Services/AuthService.cs** | 102-108 | No unit tests for `ValidateToken` method; boundary conditions not covered. | Add unit tests for `ValidateToken` method with valid/invalid tokens. |
| **SampleBankingApp/Services/EmailService.cs** | 48-54 | No unit tests for `SendTransferNotification` method; boundary conditions not covered. | Add unit tests for `SendTransferNotification` method with valid/invalid emails. |
| **SampleBankingApp/Services/EmailService.cs** | 61-67 | No unit tests for `SendWelcomeEmail` method; boundary conditions not covered. | Add unit tests for `SendWelcomeEmail` method with valid/invalid emails. |
| **SampleBankingApp/Services/TransactionService.cs** | 20-26 | No unit tests for `Transfer` method; boundary conditions not covered. | Add unit tests for `Transfer` method with valid/invalid amounts. |
| **SampleBankingApp/Services/TransactionService.cs** | 42-48 | No unit tests for `Deposit` method; boundary conditions not covered. | Add unit tests for `Deposit` method with valid/invalid amounts. |
| **SampleBankingApp/Services/TransactionService.cs** | 53-58 | No unit tests for `IsWithinDailyLimit` method; boundary conditions not covered. | Add unit tests for `IsWithinDailyLimit` method with valid/invalid user IDs. |
| **SampleBankingApp/Services/TransactionService.cs** | 60-66 | No unit tests for `RecordTransaction` method; boundary conditions not covered. | Add unit tests for `RecordTransaction` method with valid/invalid transaction IDs. |
| **SampleBankingApp/Services/UserService.cs** | 26-32 | No unit tests for `GetUserById` method; boundary conditions not covered. | Add unit tests for `GetUserById` method with valid/invalid user IDs. |
| **SampleBankingApp/Services/UserService.cs** | 40-45 | No unit tests for `UpdateUser` method; boundary conditions not covered. | Add unit tests for `UpdateUser` method with valid/invalid user IDs. |
| **SampleBankingApp/Services/UserService.cs** | 51-56 | No unit tests for `DeleteUser` method; boundary conditions not covered. | Add unit tests for `DeleteUser` method with valid/invalid user IDs. |
| **SampleBankingApp/Services/UserService.cs** | 64-69 | No unit tests for `GetUsersPage` method; boundary conditions not covered. | Add unit tests for `GetUsersPage` method with valid/invalid page sizes. |
| **SampleBankingApp/Services/UserService.cs** | 82-88 | No unit tests for `GetAuditReport` method; boundary conditions not covered. | Add unit tests for `GetAuditReport` method with valid/invalid audit logs. |
| **SampleBankingApp/Services/UserService.cs** | 91-100 | No unit tests for `SearchUsers` method; boundary conditions not covered. | Add unit tests for `SearchUsers` method with valid/invalid queries. |