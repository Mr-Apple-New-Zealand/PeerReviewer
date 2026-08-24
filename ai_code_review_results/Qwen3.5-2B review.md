## Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 25 | `_logger.LogWarning("Failed login attempt for username: {Username}", request.Username);` - Logs sensitive data in production logs | Use `LogLevel.Information` instead of `LogWarning` or filter username before logging |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded password constant `AdminBypassPassword = "SuperAdmin2024"` | Move to configuration file or use environment variable |
| SampleBankingApp/Services/AuthService.cs | 30 | MD5 hashing function using `MD5.Create()` - Weak cryptographic algorithm | Replace with SHA-256 or stronger hash function |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection via string interpolation: `SELECT * FROM Users WHERE Username = '{username}' AND Password = '{hashedPassword}'` | Use parameterized queries with `ExecuteQuerySafe` |
| SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection created directly without proper transaction handling | Wrap in transaction scope with BeginTransaction/Commit/Rollback |
| SampleBankingApp/Services/AuthService.cs | 61 | SHA1 hashing function using `SHA1.Create()` - Weak cryptographic algorithm | Replace with SHA-256 or stronger hash function |
| SampleBankingApp/Services/AuthService.cs | 68 | JWT expiration set to 30 days - Acceptable but consider shorter default | Consider reducing to 7 days by default |
| SampleBankingApp/Services/AuthService.cs | 70 | JWT secret key hardcoded in code: `builder.Configuration["Jwt:SecretKey"]!` | Use environment variable from appsettings.json |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | `int.Parse(userIdClaim!)` - Could throw exception on invalid ID format | Use `long.Parse` or validate against allowed range |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | `int.Parse(userIdClaim!)` - Same issue as above | Use `long.Parse` or validate against allowed range |
| SampleBankingApp/Controllers/TransactionController.cs | 53-59 | Catch block swallowing exceptions and returning empty response | Log error details instead of silently returning empty response |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | `throw new NotImplementedException();` - Production error should return proper status code | Return appropriate HTTP status code (e.g., 500) |
| SampleBankingApp/Controllers/UserController.cs | 48 | `return BadRequest(ex.Message);` - Exposes full exception message to client | Log internally and return generic error message |
| SampleBankingApp/Controllers/UserController.cs | 52 | `return StatusCode(500, ex.Message);` - Exposes full exception message to client | Log internally and return generic error message |
| SampleBankingApp/Controllers/UserController.cs | 66 | `_logger.LogError(ex, "Error deleting user {Id}", id);` - Logs sensitive data | Use `LogLevel.Information` or filter before logging |
| SampleBankingApp/Controllers/AuthController.cs | 25 | `_logger.LogWarning("Failed login attempt for username: {Username}", request.Username);` | Filter username before logging if possible |
| SampleBankingApp/Controllers/AuthController.cs | 30 | `return Ok(new { token, userId = user.Id, role = user.Role });` - No validation that token is valid | Add token validation call after generation |

## Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 72 | Balance update: `Balance + amount + interestBonus` - Should be `Balance + amount` | Remove duplicate `+ interestBonus` calculation |
| SampleBankingApp/Services/TransactionService.cs | 71 | Interest bonus calculated as `amount * 0.05m * 1` - Rate appears correct but logic unclear | Verify rate intent; consider using constant from config |
| SampleBankingApp/Services/UserService.cs | 36 | Row access without null check: `row["Email"]` - Could throw NullReferenceException | Add null guard before accessing row properties |
| SampleBankingApp/Services/UserService.cs | 72 | Page offset calculation: `skip = page * pageSize` - Correct formula | Keep as-is (this is correct) |
| SampleBankingApp/Services/UserService.cs | 76 | SQL query uses `OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY` - Syntax may not work in all databases | Use standard OFFSET/FETCH syntax with parameterized values |
| SampleBankingApp/Services/UserService.cs | 99 | SQL injection via string interpolation: `VALUES ({fromId}, {toId}, ...)` | Use parameterized query with ExecuteQuerySafe |
| SampleBankingApp/Services/UserService.cs | 101 | Row iteration without null check: `row["Username"]` - Could throw NullReferenceException | Add null guard before accessing row properties |
| SampleBankingApp/Services/UserService.cs | 111-123 | MapRowToUser method - No null check on row properties | Add null checks before accessing row properties |
| SampleBankingApp/Controllers/TransactionController.cs | 26 | `int.Parse(userIdClaim!)` - Could throw exception on invalid ID format | Use `long.Parse` or validate against allowed range |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | `int.Parse(userIdClaim!)` - Same issue as above | Use `long.Parse` or validate against allowed range |
| SampleBankingApp/Controllers/AuthController.cs | 26 | `_logger.LogWarning("Failed login attempt for username: {Username}", request.Username);` - Logs sensitive data | Filter username before logging if possible |

## Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/TransactionController.cs | 53-59 | Catch block swallowing exceptions and returning empty response | Log error details instead of silently returning empty response |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | `throw new NotImplementedException();` - Production error should return proper status code | Return appropriate HTTP status code (e.g., 500) |
| SampleBankingApp/Controllers/UserController.cs | 48 | `return BadRequest(ex.Message);` - Exposes full exception message to client | Log internally and return generic error message |
| SampleBankingApp/Controllers/UserController.cs | 52 | `return StatusCode(500, ex.Message);` - Exposes full exception message to client | Log internally and return generic error message |
| SampleBankingApp/Controllers/AuthController.cs | 25 | `_logger.LogWarning("Failed login attempt for username: {Username}", request.Username);` | Filter username before logging if possible |
| SampleBankingApp/Controllers/AuthController.cs | 30 | `return Ok(new { token, userId = user.Id, role = user.Role });` - No validation that token is valid | Add token validation call after generation |

## Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 25 | `_logger.LogWarning("Failed login attempt for username: {Username}", request.Username);` - Logs sensitive data | Filter username before logging if possible |
| SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection created directly without proper transaction handling | Wrap in transaction scope with BeginTransaction/Commit/Rollback |
| SampleBankingApp/Services/AuthService.cs | 61 | SHA1 hashing function using `SHA1.Create()` - Weak cryptographic algorithm | Replace with SHA-256 or stronger hash function |
| SampleBankingApp/Services/AuthService.cs | 70 | JWT secret key hardcoded in code: `builder.Configuration["Jwt:SecretKey"]!` | Use environment variable from appsettings.json |
| SampleBankingApp/Services/EmailService.cs | 16 | SmtpClient instance field - Not thread-safe, socket never released | Use static singleton or dispose properly in finally block |
| SampleBankingApp/Services/EmailService.cs | 22 | Configuration value for SMTP host - Could be better to use Environment variable | Use Environment variable |
| SampleBankingApp/Services/EmailService.cs | 25-27 | NetworkCredential from config - Security concern | Use secure credential storage |
| SampleBankingApp/Services/EmailService.cs | 39-43 | MailMessage created but not disposed | Add using statement for IDisposable |
| SampleBankingApp/Services/EmailService.cs | 69 | MailMessage created but not disposed | Add using statement for IDisposable |
| SampleBankingApp/Services/EmailService.cs | 89 | MailMessage created but not disposed | Add using statement for IDisposable |
| SampleBankingApp/Services/UserService.cs | 10 | Static audit log collection - Not thread-safe | Use lock or thread-safe collection |
| SampleBankingApp/Services/UserService.cs | 11 | Static request counter - Not thread-safe | Use lock or thread-safe collection |
| SampleBankingApp/Controllers/TransactionController.cs | 53-59 | Catch block swallowing exceptions and returning empty response | Log error details instead of silently returning empty response |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | `throw new NotImplementedException();` - Production error should return proper status code | Return appropriate HTTP status code (e.g., 500) |

## Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/UserService.cs | 36 | Row access without null check: `row["Email"]` - Could throw NullReferenceException | Add null guard before accessing row properties |
| SampleBankingApp/Services/UserService.cs | 72 | Page offset calculation: `skip = page * pageSize` - Correct formula | Keep as-is (this is correct) |
| SampleBankingApp/Services/UserService.cs | 76 | SQL query uses `OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY` - Syntax may not work in all databases | Use standard OFFSET/FETCH syntax with parameterized values |
| SampleBankingApp/Services/UserService.cs | 99 | SQL injection via string interpolation: `VALUES ({fromId}, {toId}, ...)` | Use parameterized query with ExecuteQuerySafe |
| SampleBankingApp/Services/UserService.cs | 101 | Row iteration without null check: `row["Username"]` - Could throw NullReferenceException | Add null guard before accessing row properties |
| SampleBankingApp/Services/UserService.cs | 111-123 | MapRowToUser method - No null check on row properties | Add null checks before accessing row properties |
| SampleBankingApp/Controllers/TransactionController.cs | 26 | `int.Parse(userIdClaim!)` - Could throw exception on invalid ID format | Use `long.Parse` or validate against allowed range |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | `int.Parse(userIdClaim!)` - Same issue as above | Use `long.Parse` or validate against allowed range |
| SampleBankingApp/Controllers/AuthController.cs | 25 | `_logger.LogWarning("Failed login attempt for username: {Username}", request.Username);` - Logs sensitive data | Filter username before logging if possible |
| SampleBankingApp/Controllers/AuthController.cs | 30 | `return Ok(new { token, userId = user.Id, role = user.Role });` - No validation that token is valid | Add token validation call after generation |

## Dead Code

### Methods defined but never called:

| Method Name | Location |
|-------------|----------|
| `HashPasswordMd5` | AuthService.cs |
| `HashPasswordSha1` | AuthService.cs |
| `GetOpenConnection` | DatabaseHelper.cs |
| `ExecuteQueryWithParams` | DatabaseHelper.cs |
| `IsValidEmail` | StringHelper.cs |
| `IsValidUsername` | StringHelper.cs |
| `JoinWithSeparator` | StringHelper.cs |
| `JoinWithSeparatorFixed` | StringHelper.cs |
| `MaskAccountNumber` | StringHelper.cs |
| `ObfuscateAccount` | StringHelper.cs |
| `ToTitleCase` | StringHelper.cs |
| `IsBlank` | StringHelper.cs |
| `GenerateJwtToken` | AuthService.cs |
| `ValidateToken` | AuthService.cs |
| `Transfer` | TransactionService.cs |
| `Deposit` | TransactionService.cs |
| `RefundTransaction` | TransactionService.cs |
| `GetAuditReport` | UserService.cs |
| `SearchUsers` | UserService.cs |
| `MapRowToUser` | UserService.cs |

## Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 25 | `_logger.LogWarning("Failed login attempt for username: {Username}", request.Username);` - Logs sensitive data | Filter username before logging if possible |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded password constant `AdminBypassPassword = "SuperAdmin2024"` | Move to configuration file or use environment variable |
| SampleBankingApp/Services/AuthService.cs | 61 | SHA1 hashing function using `SHA1.Create()` - Weak cryptographic algorithm | Replace with SHA-256 or stronger hash function |
| SampleBankingApp/Services/AuthService.cs | 70 | JWT secret key hardcoded in code: `builder.Configuration["Jwt:SecretKey"]!` | Use environment variable from appsettings.json |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | `int.Parse(userIdClaim!)` - Could throw exception on invalid ID format | Use `long.Parse` or validate against allowed range |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | `int.Parse(userIdClaim!)` - Same issue as above | Use `long.Parse` or validate against allowed range |
| SampleBankingApp/Controllers/UserController.cs | 48 | `return BadRequest(ex.Message);` - Exposes full exception message to client | Log internally and return generic error message |
| SampleBankingApp/Controllers/UserController.cs | 52 | `return StatusCode(500, ex.Message);` - Exposes full exception message to client | Log internally and return generic error message |
| SampleBankingApp/Controllers/AuthController.cs | 25 | `_logger.LogWarning("Failed login attempt for username: {Username}", request.Username);` | Filter username before logging if possible |
| SampleBankingApp/Controllers/AuthController.cs | 30 | `return Ok(new { token, userId = user.Id, role = user.Role });` - No validation that token is valid | Add token validation call after generation |
| SampleBankingApp/Services/EmailService.cs | 10 | `TransferSubject = "Transfer Notification - BankingApp";` - Magic string literal | Use constant from config |
| SampleBankingApp/Services/EmailService.cs | 11 | `WelcomeSubject  = "Welcome to BankingApp!";` - Magic string literal | Use constant from config |
| SampleBankingApp/Services/EmailService.cs | 39-43 | MailMessage created but not disposed | Add using statement for IDisposable |
| SampleBankingApp/Services/EmailService.cs | 69 | MailMessage created but not disposed | Add using statement for IDisposable |
| SampleBankingApp/Services/EmailService.cs | 89 | MailMessage created but not disposed | Add using statement for IDisposable |
| SampleBankingApp/Services/UserService.cs | 10 | Static audit log collection - Not thread-safe | Use lock or thread-safe collection |
| SampleBankingApp/Services/UserService.cs | 11 | Static request counter - Not thread-safe | Use lock or thread-safe collection |
| SampleBankingApp/Controllers/TransactionController.cs | 53-59 | Catch block swallowing exceptions and returning empty response | Log error details instead of silently returning empty response |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | `throw new NotImplementedException();` - Production error should return proper status code | Return appropriate HTTP status code (e.g., 500) |

## Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/UserService.cs | 72 | Page offset calculation: `skip = page * pageSize` - Correct formula | Keep as-is (this is correct) |
| SampleBankingApp/Services/UserService.cs | 76 | SQL query uses `OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY` - Syntax may not work in all databases | Use standard OFFSET/FETCH syntax with parameterized values |
| SampleBankingApp/Services/UserService.cs | 99 | SQL injection via string interpolation: `VALUES ({fromId}, {toId}, ...)` | Use parameterized query with ExecuteQuerySafe |
| SampleBankingApp/Services/UserService.cs | 101 | Row iteration without null check: `row["Username"]` - Could throw NullReferenceException | Add null guard before accessing row properties |
| SampleBankingApp/Services/UserService.cs | 111-123 | MapRowToUser method - No null check on row properties | Add null checks before accessing row properties |
| SampleBankingApp/Controllers/TransactionController.cs | 26 | `int.Parse(userIdClaim!)` - Could throw exception on invalid ID format | Use `long.Parse` or validate against allowed range |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | `int.Parse(userIdClaim!)` - Same issue as above | Use `long.Parse` or validate against allowed range |
| SampleBankingApp/Controllers/AuthController.cs | 25 | `_logger.LogWarning("Failed login attempt for username: {Username}", request.Username);` - Logs sensitive data | Filter username before logging if possible |
| SampleBankingApp/Controllers/AuthController.cs | 30 | `return Ok(new { token, userId = user.Id, role = user.Role });` - No validation that token is valid | Add token validation call after generation |
| SampleBankingApp/Services/EmailService.cs | 10 | `TransferSubject = "Transfer Notification - BankingApp";` - Magic string literal | Use constant from config |
| SampleBankingApp/Services/EmailService.cs | 11 | `WelcomeSubject  = "Welcome to BankingApp!";` - Magic string literal | Use constant from config |
| SampleBankingApp/Services/EmailService.cs | 39-43 | MailMessage created but not disposed | Add using statement for IDisposable |
| SampleBankingApp/Services/EmailService.cs | 69 | MailMessage created but not disposed | Add using statement for IDisposable |
| SampleBankingApp/Services/EmailService.cs | 89 | MailMessage created but not disposed | Add using statement for IDisposable |
| SampleBankingApp/Services/UserService.cs | 10 | Static audit log collection - Not thread-safe | Use lock or thread-safe collection |
| SampleBankingApp/Services/UserService.cs | 11 | Static request counter - Not thread-safe | Use lock or thread-safe collection |

## Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/appsettings.json | 3 | Hardcoded connection string with password in production environment | Move to configuration file or use environment variable |
| SampleBankingApp/appsettings.json | 6 | JWT secret key hardcoded in source code | Use environment variable from appsettings.json |
| SampleBankingApp/appsettings.json | 16 | Logging level set to Debug for production namespaces | Set to Information or Production in production |
| SampleBankingApp/appsettings.json | 38 | CORS policy overly permissive: `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` | Restrict to specific origins and methods |
| SampleBankingApp/appsettings.json | 40 | Authentication middleware configured - OK | Keep as-is |
| SampleBankingApp/appsettings.json | 41 | Authorization middleware configured - OK | Keep as-is |
| SampleBankingApp/appsettings.json | 42 | Controllers mapped - OK | Keep as-is |

## Missing Unit Tests

No test project found. Critical tests needed:

| Category | Method | Scenario |
|----------|--------|----------|
| AuthController | Login | Valid credentials, invalid username/password, admin bypass |
| AuthService | Login | Null username, null password, inactive user |
| AuthService | GenerateJwtToken | Null user, expired token, invalid claims |
| TransactionService | Transfer | Insufficient funds, negative amount, duplicate transaction |
| UserService | GetUserById | Invalid ID, non-existent user |
| UserService | UpdateUser | Invalid ID, null values |
| UserService | DeleteUser | Non-existent user, out of range ID |
| UserService | SearchUsers | Empty results, partial match, SQL error |
| TransactionService | Deposit | Zero amount, maximum limit exceeded |
| TransactionService | RefundTransaction | Transaction ID not found |
| EmailService | SendTransferNotification | No SMTP server, network error |