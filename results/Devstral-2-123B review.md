# Code Review Report

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 16 | SQL injection vulnerability in `ExecuteQuery` method | Use parameterized queries |
| DatabaseHelper.cs | 18 | Hardcoded fallback connection string with credentials | Remove hardcoded credentials |
| AuthService.cs | 20 | SQL injection vulnerability in `Login` method | Use `ExecuteQuerySafe` with parameters |
| AuthService.cs | 20 | MD5 hashing is insecure | Use bcrypt or PBKDF2 |
| AuthService.cs | 28 | Hardcoded admin bypass password | Remove backdoor or secure properly |
| AuthService.cs | 48 | SHA1 hashing method is insecure | Remove unused method |
| Program.cs | 18 | `ValidateLifetime = false` on JWT | Set to `true` for production |
| Program.cs | 22 | `UseDeveloperExceptionPage` unconditionally called | Wrap in environment check |
| Program.cs | 24 | HTTPS redirection commented out | Uncomment for production |
| Program.cs | 25 | Overly permissive CORS policy | Restrict to specific origins |
| EmailService.cs | 16 | SMTP credentials not using secure protocol | Enable SSL/TLS |
| EmailService.cs | 22 | Hardcoded email sender address | Move to configuration |
| UserService.cs | 50 | SQL injection in `UpdateUser` method | Use parameterized queries |
| UserService.cs | 60 | SQL injection in `DeleteUser` method | Use parameterized queries |
| TransactionService.cs | 36 | SQL injection in balance update queries | Use parameterized queries |
| TransactionService.cs | 44 | SQL injection in `RecordTransaction` method | Use parameterized queries |
| appsettings.json | 3 | Production password in source control | Use secret manager or environment variables |
| appsettings.json | 8 | Weak JWT secret key | Use strong, randomly generated key |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 28 | Fee calculation doesn't verify sufficient funds for total debit | Check `fromBalance >= totalDebit` |
| TransactionService.cs | 36 | No transaction for atomic balance updates | Use database transaction |
| TransactionService.cs | 44 | No check for self-transfer (fromUserId == toUserId) | Add validation |
| TransactionService.cs | 52 | Interest rate appears incorrect (5% instead of expected) | Verify business requirements |
| UserService.cs | 36 | Off-by-one error in pagination (`page * pageSize`) | Use `(page-1) * pageSize` |
| UserService.cs | 50 | No ownership check on user update | Verify user owns account |
| UserService.cs | 60 | No ownership check on user deletion | Verify user owns account |
| AuthService.cs | 48 | `ValidateToken` has unreachable code after early return | Remove dead code |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserService.cs | 68 | Swallows all exceptions in `SearchUsers` | Log error and return specific status |
| EmailService.cs | 40 | Swallows exception in `SendWelcomeEmail` | Propagate or log properly |
| TransactionController.cs | 34 | Catches `NotImplementedException` specifically | Use more general exception handling |
| UserController.cs | 32 | Catches broad `Exception` and returns message | Don't expose internal details |
| UserController.cs | 44 | Catches broad `Exception` and returns generic message | Log specific error details |
| TransactionService.cs | 24 | No transaction rollback if email fails | Use transaction scope |
| DatabaseHelper.cs | 28 | No disposal of connection in `ExecuteNonQuery` | Use `using` statement |
| AuthService.cs | 24 | No disposal of connection and reader | Use `using` statements |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 16 | Connection not disposed in `GetOpenConnection` | Return wrapped in `using` or document ownership |
| DatabaseHelper.cs | 28 | Connection not properly disposed in error cases | Use `using` statement |
| AuthService.cs | 22 | Connection and reader not disposed | Use `using` statements |
| EmailService.cs | 14 | `SmtpClient` as instance field (not thread-safe) | Create per-method or use dependency injection |
| EmailService.cs | 22 | `MailMessage` not disposed | Use `using` statement |
| EmailService.cs | 40 | `MailMessage` not disposed | Use `using` statement |
| EmailService.cs | 48 | `MailMessage` not disposed | Use `using` statement |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionController.cs | 14 | `userIdClaim` could be null | Add null check |
| TransactionController.cs | 24 | `userIdClaim` could be null | Add null check |
| UserService.cs | 32 | No null check on `email` parameter | Add validation |
| UserService.cs | 32 | No null check on `username` parameter | Add validation |
| StringHelper.cs | 30 | No null check before `account[^4..]` | Add null guard |
| AuthService.cs | 26 | No null check on connection string | Add validation |
| Program.cs | 10 | No null check on `jwtSecret` | Add validation |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 44 | `ExecuteQueryWithParams` marked obsolete but present | Remove method |
| StringHelper.cs | 22 | `JoinWithSeparator` has broken implementation | Remove in favor of fixed version |
| AuthService.cs | 48 | `HashPasswordSha1` never called | Remove method |
| AuthService.cs | 56 | `ValidateToken` has unreachable code | Remove dead code |
| TransactionController.cs | 30 | `Refund` method throws NotImplementedException | Remove or implement |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 14 | Magic number for fee rate (0.015m) | Move to configuration |
| TransactionService.cs | 15 | Magic number for max transactions (10) | Move to configuration |
| TransactionService.cs | 52 | Magic number for interest (0.05m) | Move to configuration |
| UserService.cs | 36 | Magic number for max page size (50) | Move to configuration |
| UserService.cs | 24 | Magic number for max user ID (1000000) | Move to configuration |
| StringHelper.cs | 6 | Magic number for email length (254) | Use named constant |
| StringHelper.cs | 12 | Magic numbers for username length (3, 20) | Use named constants |
| AuthService.cs | 18 | Magic string for admin bypass | Move to configuration |
| EmailService.cs | 10 | Magic strings for email subjects | Use named constants |
| EmailService.cs | 12 | Magic numbers for retries and timeout | Move to configuration |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 22 | String concatenation in loop | Use `StringBuilder` properly |
| StringHelper.cs | 4 | `Regex` created in method (performance) | Make static readonly |
| StringHelper.cs | 11 | `Regex` created in method (performance) | Make static readonly |
| StringHelper.cs | 38 | Reimplements `string.IsNullOrWhiteSpace` | Use built-in method |
| UserService.cs | 12 | Shared mutable static state | Use thread-safe alternative |
| UserService.cs | 68 | String concatenation in loop | Use `StringBuilder` |
| DatabaseHelper.cs | 16 | Leaks connection ownership | Document or change pattern |
| EmailService.cs | 14 | `SmtpClient` as instance field | Create per-method |
| UserService.cs | 68 | Returns empty collection on error | Return null or throw |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 18 | `UseDeveloperExceptionPage` in production | Wrap in environment check |
| Program.cs | 24 | Overly permissive CORS | Restrict to specific origins |
| Program.cs | 22 | HTTPS redirection commented out | Enable for production |
| appsettings.json | 12 | Debug log level for production | Use environment-specific config |
| SampleBankingApp.csproj | 10 | Debug symbols in release | Set to false for production |
| Program.cs | 10 | No environment-specific config files | Add `appsettings.Production.json` |

## 10. Missing Unit Tests

No test project found. Critical methods needing tests:
- `AuthService.Login` (authentication flow)
- `TransactionService.Transfer` (boundary conditions, fee calculation)
- `TransactionService.Deposit` (interest calculation)
- `UserService.GetUsersPage` (pagination logic)
- `UserService.UpdateUser` (validation, ownership)
- `UserService.DeleteUser` (validation, ownership)
- `StringHelper.IsValidEmail` (edge cases)
- `StringHelper.IsValidUsername` (edge cases)
- `TransactionController.Transfer` (authorization)
- `UserController.UpdateUser` (authorization)