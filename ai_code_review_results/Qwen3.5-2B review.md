# Code Review Report

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 25 | Hardcoded username in logger message | Replace with parameterized string or use `request.Username` directly |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password in constructor | Remove hardcoded value; rely on database authentication only |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection via string interpolation in query | Use parameterized query or executeQuerySafe method |
| SampleBankingApp/Services/AuthService.cs | 53-56 | Hardcoded admin bypass logic bypasses authorization checks | Remove inline check; ensure `Login` returns null for invalid credentials |
| SampleBankingApp/Services/AuthService.cs | 61 | MD5 hashing of passwords (weak cryptography) | Switch to SHA256 or stronger algorithm |
| SampleBankingApp/Services/AuthService.cs | 68 | JWT token expiration set to 30 days but no validation logic enforced | Ensure `ValidateToken` is called before using token and handles expired tokens |
| SampleBankingApp/Program.cs | 16 | Hardcoded JWT secret key in source code | Move to `.env` file or configuration management system |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables token expiration enforcement | Set to `true` to enforce token validity period |
| SampleBankingApp/Program.cs | 38 | CORS allows any origin (`AllowAnyOrigin`) | Restrict to specific trusted origins |
| SampleBankingApp/Program.cs | 39 | CORS allows any method (`AllowAnyMethod`) | Restrict to POST, PUT, DELETE methods |
| SampleBankingApp/Program.cs | 40 | CORS allows any header (`AllowAnyHeader`) | Restrict to specific headers if needed |
| SampleBankingApp/Program.cs | 34 | Developer exception page enabled in production | Disable `UseDeveloperExceptionPage()` in production environment |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out | Enable `app.UseHttpsRedirection();` |
| SampleBankingApp/Controllers/UserController.cs | 56 | Delete endpoint lacks ownership check | Add `[Authorize(Roles = "SuperAdmin")]` or similar permission check |
| SampleBankingApp/Controllers/UserController.cs | 66 | Error message contains sensitive data | Sanitize error messages to remove stack traces or internal IDs |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Catch-all exception handler returns generic error | Log detailed exceptions instead of swallowing them |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/TransactionController.cs | 27 | Integer parsing without null check on userIdClaim | Add null check: `int fromUserId = int.Parse(userIdClaim!);` |
| SampleBankingApp/Services/TransactionService.cs | 36 | Accessing row index without checking count first | Add `if (table.Rows.Count == 0)` before accessing `Rows[0]` |
| SampleBankingApp/Services/TransactionService.cs | 37 | Same issue with toUserTable access | Add null check for `toUserTable.Rows.Count` |
| SampleBankingApp/Services/TransactionService.cs | 42-45 | Balance calculation logic excludes fee deduction | Ensure `totalDebit` is subtracted from both balances correctly |
| SampleBankingApp/Services/TransactionService.cs | 68 | Interest bonus calculated as 5% but not applied to total balance update | Verify interest is added to the correct balance field |
| SampleBankingApp/Services/UserService.cs | 72 | SQL injection via string interpolation in UPDATE statement | Use parameterized query or executeQuerySafe |
| SampleBankingApp/Services/UserService.cs | 105 | Exception caught and swallowed silently | Log exception details; do not return empty list |
| SampleBankingApp/Services/UserService.cs | 109 | SearchUsers returns empty list on exception instead of throwing | Throw exception to allow caller to handle gracefully |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 25 | Logger logs username but doesn't log failure reason | Add specific error code or message |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Generic catch-all returns 500 without context | Implement proper error response |
| SampleBankingApp/Controllers/UserController.cs | 50 | Exception message returned to client may contain internal details | Sanitize error messages |
| SampleBankingApp/Controllers/UserController.cs | 66 | Error message contains sensitive data | Remove stack trace or internal IDs |
| SampleBankingApp/Services/UserService.cs | 105 | Broad Exception caught and ignored | Log and return meaningful error |
| SampleBankingApp/Services/UserService.cs | 109 | Catch-all returns empty list | Return non-empty list with error details |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 22 | No explicit handling of authentication result | Ensure token generation succeeds |
| SampleBankingApp/Controllers/TransactionController.cs | 29 | Transfer method does not dispose resources | Wrap in try-finally or use async/await |
| SampleBankingApp/Controllers/TransactionController.cs | 39 | Deposit method does not dispose resources | Wrap in try-finally or use async/await |
| SampleBankingApp/Controllers/UserController.cs | 43 | UpdateUser does not dispose resources | Wrap in try-finally or use async/await |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser does not dispose resources | Wrap in try-finally or use async/await |
| SampleBankingApp/Services/EmailService.cs | 16 | `_smtpClient` instance field never disposed | Dispose after successful send or wrap in try-finally |
| SampleBankingApp/Services/EmailService.cs | 73 | `SendWelcomeEmail` catches exceptions but doesn't close connection | Ensure connection is closed on exception |
| SampleBankingApp/Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` creates MailMessage but doesn't dispose | Ensure MailMessage is disposed |
| SampleBankingApp/Services/EmailService.cs | 91 | Connection not explicitly closed after Send | Use using statement for SmtpClient |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 22 | LoginRequest passed directly without null check | Add null check: `if (request == null) return BadRequest();` |
| SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection opened without null check on config | Add null check: `var connectionString = _config.GetConnectionString("DefaultConnection");` |
| SampleBankingApp/Services/AuthService.cs | 38 | SqlCommand created without null check | Add null check before creating command |
| SampleBankingApp/Services/AuthService.cs | 44 | Direct access to reader properties without null check | Add null check: `if (!reader.Read()) return null;` |
| SampleBankingApp/Services/AuthService.cs | 53-56 | Hardcoded admin bypass logic bypasses authorization checks | Remove inline check; ensure `Login` returns null for invalid credentials |
| SampleBankingApp/Services/AuthService.cs | 60 | No null check on username parameter | Add null check: `if (string.IsNullOrEmpty(username)) return null;` |
| SampleBankingApp/Services/TransactionService.cs | 28 | ExecuteQuerySafe called without null check on tableName | Add null check: `if (string.IsNullOrEmpty(tableName)) throw new ArgumentException();` |
| SampleBankingApp/Services/TransactionService.cs | 30 | Dictionary key "@" used without null check | Add null check: `if (id <= 0 || id > 1000000) throw new ArgumentException();` |
| SampleBankingApp/Services/UserService.cs | 27 | ExecuteQuerySafe called without null check on sql | Add null check: `if (string.IsNullOrEmpty(sql)) throw new ArgumentException();` |
| SampleBankingApp/Services/UserService.cs | 29 | Dictionary key "@" used without null check | Add null check: `if (id <= 0 || id > 1000000) throw new ArgumentException();` |
| SampleBankingApp/Services/UserService.cs | 31 | Rows.Count checked but row index accessed without null check | Add null check: `if (table.Rows.Count == 0) return null;` |
| SampleBankingApp/Services/UserService.cs | 34 | Row index accessed without null check | Add null check: `if (table.Rows.Count == 0) return null;` |
| SampleBankingApp/Services/UserService.cs | 47 | SQL injection via string interpolation in UPDATE statement | Use parameterized query or executeQuerySafe |
| SampleBankingApp/Services/UserService.cs | 59 | RequestCount incremented without null check | Add null check: `if (id <= 0 || id > 1000000) throw new ArgumentException();` |
| SampleBankingApp/Services/UserService.cs | 61 | DELETE executed without null check | Add null check: `if (id <= 0 || id > 1000000) throw new ArgumentException();` |
| SampleBankingApp/Services/UserService.cs | 74 | RecordTransaction called without null check | Add null check: `if (fromId <= 0 || toId <= 0 || amount <= 0) throw new ArgumentException();` |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 22-31 | No explicit handling of authentication result | Ensure token generation succeeds |
| SampleBankingApp/Controllers/TransactionController.cs | 29-35 | Transfer method does not dispose resources | Wrap in try-finally or use async/await |
| SampleBankingApp/Controllers/TransactionController.cs | 39-46 | Deposit method does not dispose resources | Wrap in try-finally or use async/await |
| SampleBankingApp/Controllers/UserController.cs | 43-54 | UpdateUser does not dispose resources | Wrap in try-finally or use async/await |
| SampleBankingApp/Controllers/UserController.cs | 56-69 | DeleteUser does not dispose resources | Wrap in try-finally or use async/await |
| SampleBankingApp/Services/EmailService.cs | 16 | `_smtpClient` instance field never disposed | Dispose after successful send or wrap in try-finally |
| SampleBankingApp/Services/EmailService.cs | 73 | `SendWelcomeEmail` catches exceptions but doesn't close connection | Ensure connection is closed on exception |
| SampleBankingApp/Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` creates MailMessage but doesn't dispose | Ensure MailMessage is disposed |
| SampleBankingApp/Services/EmailService.cs | 91 | Connection not explicitly closed after Send | Use using statement for SmtpClient |
| SampleBankingApp/Services/TransactionService.cs | 99-103 | RefundTransaction throws NotImplementedException | Implement actual refund logic |
| SampleBankingApp/Services/UserService.cs | 105 | Exception caught and swallowed silently | Log exception details; do not return empty list |
| SampleBankingApp/Services/UserService.cs | 109 | Catch-all returns empty list | Return non-empty list with error details |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 26 | Hardcoded message text in Unauthorized response | Use constant or configuration |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Hardcoded message text in BadRequest response | Use constant or configuration |
| SampleBankingApp/Controllers/UserController.cs | 48 | Hardcoded error message format | Use constant or configuration |
| SampleBankingApp/Controllers/UserController.cs | 67 | Hardcoded error message format | Use constant or configuration |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password | Remove hardcoded value |
| SampleBankingApp/Services/AuthService.cs | 61 | MD5 hashing of passwords (weak cryptography) | Switch to SHA256 or stronger algorithm |
| SampleBankingApp/Services/AuthService.cs | 68 | JWT token expiration set to 30 days but no validation logic enforced | Ensure `ValidateToken` is called before using token |
| SampleBankingApp/Program.cs | 16 | Hardcoded JWT secret key in source code | Move to `.env` file or configuration management system |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables token expiration enforcement | Set to `true` to enforce token validity period |
| SampleBankingApp/Program.cs | 34 | Developer exception page enabled in production | Disable `UseDeveloperExceptionPage()` in production environment |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out | Enable `app.UseHttpsRedirection();` |
| SampleBankingApp/Program.cs | 38 | CORS allows any origin (`AllowAnyOrigin`) | Restrict to specific trusted origins |
| SampleBankingApp/Program.cs | 39 | CORS allows any method (`AllowAnyMethod`) | Restrict to POST, PUT, DELETE methods |
| SampleBankingApp/Program.cs | 40 | CORS allows any header (`AllowAnyHeader`) | Restrict to specific headers if needed |
| SampleBankingApp/Controllers/UserController.cs | 56 | Delete endpoint lacks ownership check | Add `[Authorize(Roles = "SuperAdmin")]` or similar permission check |
| SampleBankingApp/Controllers/UserController.cs | 66 | Error message contains sensitive data | Sanitize error messages to remove stack traces or internal IDs |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Catch-all exception handler returns generic error | Implement proper error response |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 22-31 | No explicit handling of authentication result | Ensure token generation succeeds |
| SampleBankingApp/Controllers/TransactionController.cs | 29-35 | Transfer method does not dispose resources | Wrap in try-finally or use async/await |
| SampleBankingApp/Controllers/TransactionController.cs | 39-46 | Deposit method does not dispose resources | Wrap in try-finally or use async/await |
| SampleBankingApp/Controllers/UserController.cs | 43-54 | UpdateUser does not dispose resources | Wrap in try-finally or use async/await |
| SampleBankingApp/Controllers/UserController.cs | 56-69 | DeleteUser does not dispose resources | Wrap in try-finally or use async/await |
| SampleBankingApp/Services/EmailService.cs | 16 | `_smtpClient` instance field never disposed | Dispose after successful send or wrap in try-finally |
| SampleBankingApp/Services/EmailService.cs | 73 | `SendWelcomeEmail` catches exceptions but doesn't close connection | Ensure connection is closed on exception |
| SampleBankingApp/Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` creates MailMessage but doesn't dispose | Ensure MailMessage is disposed |
| SampleBankingApp/Services/EmailService.cs | 91 | Connection not explicitly closed after Send | Use using statement for SmtpClient |
| SampleBankingApp/Services/TransactionService.cs | 99-103 | RefundTransaction throws NotImplementedException | Implement actual refund logic |
| SampleBankingApp/Services/UserService.cs | 105 | Exception caught and swallowed silently | Log exception details; do not return empty list |
| SampleBankingApp/Services/UserService.cs | 109 | Catch-all returns empty list | Return non-empty list with error details |
| SampleBankingApp/Services/UserService.cs | 111-123 | MapRowToUser has no null checks | Add null checks for all properties |
| SampleBankingApp/Services/UserService.cs | 111-123 | MapRowToUser has no null checks | Add null checks for all properties |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Program.cs | 16 | Hardcoded JWT secret key in source code | Move to `.env` file or configuration management system |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables token expiration enforcement | Set to `true` to enforce token validity period |
| SampleBankingApp/Program.cs | 34 | Developer exception page enabled in production | Disable `UseDeveloperExceptionPage()` in production environment |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out | Enable `app.UseHttpsRedirection();` |
| SampleBankingApp/Program.cs | 38 | CORS allows any origin (`AllowAnyOrigin`) | Restrict to specific trusted origins |
| SampleBankingApp/Program.cs | 39 | CORS allows any method (`AllowAnyMethod`) | Restrict to POST, PUT, DELETE methods |
| SampleBankingApp/Program.cs | 40 | CORS allows any header (`AllowAnyHeader`) | Restrict to specific headers if needed |
| SampleBankingApp/Controllers/AuthController.cs | 25 | Hardcoded username in logger message | Replace with parameterized string or use `request.Username` directly |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Catch-all exception handler returns generic error | Implement proper error response |
| SampleBankingApp/Controllers/UserController.cs | 56 | Delete endpoint lacks ownership check | Add `[Authorize(Roles = "SuperAdmin")]` or similar permission check |
| SampleBankingApp/Controllers/UserController.cs | 66 | Error message contains sensitive data | Sanitize error messages to remove stack traces or internal IDs |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Catch-all exception handler returns generic error | Implement proper error response |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password | Remove hardcoded value; rely on database authentication only |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection via string interpolation in query | Use parameterized query or executeQuerySafe method |
| SampleBankingApp/Services/AuthService.cs | 53-56 | Hardcoded admin bypass logic bypasses authorization checks | Remove inline check; ensure `Login` returns null for invalid credentials |
| SampleBankingApp/Services/AuthService.cs | 61 | MD5 hashing of passwords (weak cryptography) | Switch to SHA256 or stronger algorithm |
| SampleBankingApp/Services/AuthService.cs | 68 | JWT token expiration set to 30 days but no validation logic enforced | Ensure `ValidateToken` is called before using token and handles expired tokens |
| SampleBankingApp/Program.cs | 16 | Hardcoded JWT secret key in source code | Move to `.env` file or configuration management system |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables token expiration enforcement | Set to `true` to enforce token validity period |
| SampleBankingApp/Program.cs | 34 | Developer exception page enabled in production | Disable `UseDeveloperExceptionPage()` in production environment |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out | Enable `app.UseHttpsRedirection();` |
| SampleBankingApp/Program.cs | 38 | CORS allows any origin (`AllowAnyOrigin`) | Restrict to specific trusted origins |
| SampleBankingApp/Program.cs | 39 | CORS allows any method (`AllowAnyMethod`) | Restrict to POST, PUT, DELETE methods |
| SampleBankingApp/Program.cs | 40 | CORS allows any header (`AllowAnyHeader`) | Restrict to specific headers if needed |
| SampleBankingApp/Controllers/UserController.cs | 56 | Delete endpoint lacks ownership check | Add `[Authorize(Roles = "SuperAdmin")]` or similar permission check |
| SampleBankingApp/Controllers/UserController.cs | 66 | Error message contains sensitive data | Sanitize error messages to remove stack traces or internal IDs |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Catch-all exception handler returns generic error | Implement proper error response |

## 10. Missing Unit Tests

| File | Issue | Fix |
|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | No tests for login flow | Create unit tests for `Login`, `GenerateJwtToken`, `ValidateToken` |
| SampleBankingApp/Controllers/TransactionController.cs | No tests for transfer/deposit/refund | Create unit tests for `Transfer`, `Deposit`, `RefundTransaction` |
| SampleBankingApp/Controllers/UserController.cs | No tests for CRUD operations | Create unit tests for `GetUser`, `UpdateUser`, `DeleteUser`, `GetUsers` |
| SampleBankingApp/Services/AuthService.cs | No tests for password hashing | Create unit tests for `HashPasswordMd5`, `HashPasswordSha1` |
| SampleBankingApp/Services/EmailService.cs | No tests for email sending | Create unit tests for `SendTransferNotification`, `SendWelcomeEmail`, `BuildHtmlTemplate` |
| SampleBankingApp/Services/TransactionService.cs | No tests for transaction logic | Create unit tests for `Transfer`, `Deposit`, `RecordTransaction`, `RefundTransaction` |
| SampleBankingApp/Services/UserService.cs | No tests for user management | Create unit tests for `GetUserById`, `UpdateUser`, `DeleteUser`, `SearchUsers`, `GetAuditReport` |