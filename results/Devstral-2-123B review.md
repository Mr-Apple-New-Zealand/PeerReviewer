# Code Review Report

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 16 | SQL injection vulnerability in `ExecuteQuery` method | Use parameterized queries |
| DatabaseHelper.cs | 17 | Hardcoded fallback connection string with credentials | Remove hardcoded credentials |
| AuthService.cs | 20 | SQL injection vulnerability in `Login` method | Use `ExecuteQuerySafe` with parameters |
| AuthService.cs | 20 | MD5 hashing is insecure | Use bcrypt or PBKDF2 |
| AuthService.cs | 28 | Hardcoded admin bypass password | Remove backdoor or secure properly |
| AuthService.cs | 56 | JWT `ValidateLifetime` set to false | Set to true for production |
| Program.cs | 18 | Developer exception page enabled | Conditionally enable only in development |
| Program.cs | 20 | HTTPS redirection commented out | Uncomment for production |
| Program.cs | 21 | Overly permissive CORS policy | Restrict to specific origins |
| AuthService.cs | 52 | Weak JWT secret key | Use a strong, randomly generated key |
| UserService.cs | 48 | SQL injection in `UpdateUser` method | Use parameterized queries |
| UserService.cs | 58 | SQL injection in `DeleteUser` method | Use parameterized queries |
| TransactionService.cs | 38 | SQL injection in balance update queries | Use parameterized queries |
| TransactionService.cs | 50 | SQL injection in `RecordTransaction` method | Use parameterized queries |
| EmailService.cs | 22 | SMTP credentials not encrypted | Store securely in configuration |
| appsettings.json | 6 | Plaintext database password | Use secret manager or environment variables |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 28 | Fee calculation doesn't check if user can afford fee | Verify totalDebit <= fromBalance |
| TransactionService.cs | 47 | Interest rate appears incorrect (5% instead of expected) | Verify correct rate with business requirements |
| UserService.cs | 38 | Pagination uses `page * pageSize` (off-by-one) | Use `(page-1) * pageSize` |
| TransactionService.cs | 24 | No self-transfer check | Add `fromUserId != toUserId` validation |
| UserService.cs | 38 | No upper bound check on page parameter | Add validation for maximum page value |
| TransactionService.cs | 24 | No check for maximum transfer amount | Add maximum transfer limit |
| UserService.cs | 48 | No validation that email/username are different from current | Add change detection |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserController.cs | 38 | Broad exception catch returns raw message | Log error and return generic message |
| UserController.cs | 50 | Broad exception catch returns raw message | Log error and return generic message |
| EmailService.cs | 46 | Email failure silently caught | Log and consider retry mechanism |
| UserService.cs | 68 | Empty list returned on error | Log error and return appropriate status |
| TransactionService.cs | 20 | No transaction for atomic balance updates | Wrap in database transaction |
| EmailService.cs | 26 | Email sent after DB commit (side effect) | Move email sending before commit or use transactional outbox |
| AuthController.cs | 14 | Raw error message in response | Return generic message to client |
| TransactionController.cs | 28 | Raw error message in response | Return generic message to client |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 12 | Connection not disposed in `GetOpenConnection` | Implement IDisposable or use `using` |
| DatabaseHelper.cs | 17 | Connection not disposed in `ExecuteQuery` | Use `using` statement |
| DatabaseHelper.cs | 28 | Command not disposed in `ExecuteNonQuery` | Use `using` statement |
| AuthService.cs | 23 | Connection and reader not properly disposed | Use `using` statements |
| EmailService.cs | 16 | SmtpClient as instance field (not thread-safe) | Create per-method or use dependency injection |
| EmailService.cs | 26 | MailMessage not disposed | Use `using` statement |
| EmailService.cs | 42 | MailMessage not disposed | Use `using` statement |
| EmailService.cs | 50 | MailMessage not disposed | Use `using` statement |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionController.cs | 14 | `userIdClaim` could be null | Add null check before parsing |
| UserController.cs | 14 | No null check on request body | Add `[Required]` attributes or null check |
| UserService.cs | 24 | No null check on email/username parameters | Add null validation |
| StringHelper.cs | 38 | No null check on accountNumber parameter | Add null validation |
| StringHelper.cs | 43 | No null check on account parameter | Add null validation |
| TransactionService.cs | 26 | No check if fromUserTable has rows | Add `Rows.Count > 0` check |
| TransactionService.cs | 27 | No check if toUserTable has rows | Add `Rows.Count > 0` check |
| UserService.cs | 69 | No check if table has rows before accessing | Add `Rows.Count > 0` check |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 42 | Obsolete method still present | Remove `ExecuteQueryWithParams` |
| StringHelper.cs | 18 | Broken `JoinWithSeparator` (use fixed version) | Remove broken implementation |
| AuthService.cs | 52 | Unused `HashPasswordSha1` method | Remove if not needed |
| AuthService.cs | 62 | Unreachable code in `ValidateToken` | Remove dead code after early return |
| UserService.cs | 8 | Static audit log with no thread safety | Remove or make thread-safe |
| UserService.cs | 9 | Static request counter with no thread safety | Remove or make thread-safe |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 14 | Magic number for fee rate (0.015) | Move to configuration |
| TransactionService.cs | 15 | Magic number for max transactions (10) | Move to configuration |
| UserService.cs | 12 | Magic number for ID validation (1000000) | Move to constant |
| UserService.cs | 38 | Magic number for page size limit (50) | Move to configuration |
| TransactionService.cs | 47 | Magic number for interest rate (0.05) | Move to configuration |
| TransactionService.cs | 47 | Magic number for interest multiplier (1) | Use named constant |
| UserService.cs | 13 | Magic number for ID validation (1000000) | Move to constant |
| StringHelper.cs | 3 | Magic number for email length (254) | Use named constant |
| StringHelper.cs | 9 | Magic numbers for username length (3, 20) | Use named constants |
| EmailService.cs | 12 | Magic number for max retries (3) | Move to configuration |
| EmailService.cs | 13 | Magic number for SMTP timeout (5000) | Move to configuration |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 18 | String concatenation in loop | Use `StringBuilder` properly or `string.Join` |
| StringHelper.cs | 10 | Regex created in method (performance) | Make static readonly |
| StringHelper.cs | 16 | Regex created in method (performance) | Make static readonly |
| StringHelper.cs | 33 | Duplicate account masking logic | Remove one implementation |
| UserService.cs | 68 | String concatenation in loop | Use `StringBuilder` |
| DatabaseHelper.cs | 42 | Obsolete method with no replacement guidance | Document replacement or remove |
| UserService.cs | 8 | Shared mutable static state | Remove or make thread-safe |
| UserService.cs | 9 | Shared mutable static state | Remove or make thread-safe |
| TransactionService.cs | 54 | String formatting not used consistently | Use `FormatCurrency` method |
| StringHelper.cs | 33 | Reimplements `string.IsNullOrWhiteSpace` | Use built-in method |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 18 | Developer exception page unconditional | Conditionally enable based on environment |
| Program.cs | 20 | HTTPS redirection commented out | Enable for production |
| Program.cs | 21 | Overly permissive CORS | Restrict to specific origins |
| Program.cs | 4 | No environment-specific config files | Add `appsettings.Production.json` |
| SampleBankingApp.csproj | 8 | Debug symbols in release build | Set to false for production |
| appsettings.json | 2 | No environment-specific overrides | Add production-specific settings |
| appsettings.json | 6 | Logging level set to Debug | Set to Warning/Error for production |
| Program.cs | 15 | JWT secret not validated for null | Add null check |
| EmailService.cs | 17 | SMTP port hardcoded fallback | Remove hardcoded fallback |

## 10. Missing Unit Tests

No test project found. Critical methods needing tests:
- `AuthService.Login` (authentication flow)
- `TransactionService.Transfer` (boundary conditions, fee calculation)
- `UserService.GetUsersPage` (pagination logic)
- `TransactionService.Deposit` (interest calculation)
- `UserService.UpdateUser` (validation scenarios)
- `StringHelper.IsValidEmail` (edge cases)
- `TransactionService.IsWithinDailyLimit` (boundary conditions)
- `UserService.SearchUsers` (SQL injection prevention)
- `AuthService.GenerateJwtToken` (token validation)
- `TransactionService.RecordTransaction` (data integrity)