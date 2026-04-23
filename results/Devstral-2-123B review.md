# Code Review Report

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 16 | Hardcoded fallback connection string with credentials | Remove hardcoded credentials and throw exception if config missing |
| DatabaseHelper.cs | 22 | SQL injection via string interpolation in `ExecuteQuery` | Use parameterized queries only |
| AuthService.cs | 20 | SQL injection via string interpolation in `Login` | Use `ExecuteQuerySafe` with parameters |
| AuthService.cs | 40 | MD5 hashing is cryptographically broken | Use bcrypt or PBKDF2 with salt |
| AuthService.cs | 16 | Hardcoded admin bypass password | Remove backdoor or use secure config |
| AuthService.cs | 58 | SHA1 hashing method present (weak) | Remove unused method |
| Program.cs | 20 | `ValidateLifetime = false` on JWT | Set to `true` for production |
| Program.cs | 22 | Weak JWT secret key in config | Use strong, randomly generated key |
| Program.cs | 26 | `UseDeveloperExceptionPage` unconditionally | Only enable in development environment |
| Program.cs | 28 | HTTPS redirection commented out | Uncomment for production |
| Program.cs | 30 | Overly permissive CORS policy | Restrict to specific origins |
| UserService.cs | 40 | SQL injection via string interpolation in `UpdateUser` | Use parameterized queries |
| UserService.cs | 50 | SQL injection via string interpolation in `DeleteUser` | Use parameterized queries |
| TransactionService.cs | 36 | SQL injection via string interpolation in balance updates | Use parameterized queries |
| TransactionService.cs | 48 | SQL injection via string interpolation in `RecordTransaction` | Use parameterized queries |
| UserService.cs | 58 | SQL injection via string interpolation in `SearchUsers` | Use parameterized queries |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 20 | Fee calculation excludes minimum fee check | Add minimum fee validation |
| TransactionService.cs | 26 | Balance check only verifies >= amount, not totalDebit | Check `fromBalance >= totalDebit` |
| TransactionService.cs | 44 | Interest rate applied as 5% instead of 0.5% | Change `0.05m * 1` to `0.005m` |
| TransactionService.cs | 22 | No self-transfer check | Add `fromUserId != toUserId` validation |
| UserService.cs | 32 | Pagination uses `page * pageSize` (off-by-one) | Use `(page-1) * pageSize` |
| UserService.cs | 58 | Search query doesn't validate input length | Add max length validation |
| AuthService.cs | 50 | `ValidateToken` has unreachable code after return | Remove dead code |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserService.cs | 59 | Catches broad `Exception` and returns empty list | Log error and rethrow specific exception |
| EmailService.cs | 44 | Swallows exception in `SendWelcomeEmail` | Log and propagate exception |
| TransactionController.cs | 36 | Catches `NotImplementedException` and returns 500 | Return 501 Not Implemented |
| UserController.cs | 32 | Catches broad `Exception` and returns 500 with message | Log error and return generic message |
| UserController.cs | 42 | Catches broad `Exception` and returns generic error | Log specific error details |
| DatabaseHelper.cs | 22 | Connection not disposed in `ExecuteQuery` | Use `using` statement |
| DatabaseHelper.cs | 34 | Connection not disposed if exception occurs | Use `using` statement |
| TransactionService.cs | 36 | No transaction for atomic balance updates | Wrap in database transaction |
| EmailService.cs | 28 | Email sent after database commit | Send email before commit or use transactional outbox |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 16 | Connection not disposed in `GetOpenConnection` | Implement `IDisposable` or use `using` |
| DatabaseHelper.cs | 22 | Connection and command not disposed in `ExecuteQuery` | Use `using` statements |
| DatabaseHelper.cs | 34 | Connection not disposed in `ExecuteNonQuery` | Use `using` statement |
| AuthService.cs | 22 | Connection and reader not disposed | Use `using` statements |
| EmailService.cs | 18 | `SmtpClient` as instance field (not thread-safe) | Create new instance per send |
| EmailService.cs | 28 | `MailMessage` not disposed | Use `using` statement |
| EmailService.cs | 44 | `MailMessage` not disposed | Use `using` statement |
| EmailService.cs | 54 | `MailMessage` not disposed | Use `using` statement |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionController.cs | 14 | `userIdClaim` could be null | Add null check before `int.Parse` |
| UserController.cs | 14 | No null check for `UpdateUserRequest` | Add `[Required]` attributes or null check |
| StringHelper.cs | 30 | `account[^4..]` could throw if null | Add null check |
| UserService.cs | 24 | No null check for `email` parameter | Add null/empty validation |
| UserService.cs | 24 | No null check for `username` parameter | Add null/empty validation |
| DatabaseHelper.cs | 12 | Config value passed directly without null check | Add null check |
| AuthService.cs | 22 | Config value passed directly without null check | Add null check |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 46 | `[Obsolete]` method still present | Remove method |
| StringHelper.cs | 18 | `JoinWithSeparator` has broken implementation | Remove in favor of `JoinWithSeparatorFixed` |
| AuthService.cs | 50 | Unreachable code in `ValidateToken` | Remove dead code |
| AuthService.cs | 58 | `HashPasswordSha1` never called | Remove unused method |
| UserService.cs | 8 | Static `_requestCount` never used | Remove unused field |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 12 | Fee rate hardcoded as 0.015m | Move to configuration |
| TransactionService.cs | 13 | Max transactions hardcoded as 10 | Move to configuration |
| TransactionService.cs | 44 | Interest rate hardcoded as 0.05m | Move to configuration |
| UserService.cs | 34 | Page size limit hardcoded as 50 | Move to configuration |
| UserService.cs | 20 | User ID range limits hardcoded | Move to configuration |
| AuthService.cs | 16 | Admin bypass password hardcoded | Move to secure configuration |
| EmailService.cs | 12 | Transfer subject hardcoded | Move to configuration |
| EmailService.cs | 13 | Welcome subject hardcoded | Move to configuration |
| EmailService.cs | 14 | Max retries hardcoded as 3 | Move to configuration |
| EmailService.cs | 15 | SMTP timeout hardcoded as 5000 | Move to configuration |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 18 | String concatenation in loop | Use `StringBuilder` properly |
| StringHelper.cs | 10 | `new Regex` created on each call | Make `static readonly` |
| StringHelper.cs | 17 | `new Regex` created on each call | Make `static readonly` |
| StringHelper.cs | 38 | Reimplements `string.IsNullOrWhiteSpace` | Use built-in method |
| UserService.cs | 52 | String concatenation in loop | Use `string.Join` |
| DatabaseHelper.cs | 8 | Shared mutable connection string | Make readonly |
| UserService.cs | 7 | Shared mutable static state | Use thread-safe collection |
| UserService.cs | 8 | Shared mutable static state | Use thread-safe counter |
| TransactionService.cs | 44 | String interpolation in SQL | Use parameterized queries |
| UserService.cs | 40 | String interpolation in SQL | Use parameterized queries |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 20 | `ValidateLifetime = false` | Set to `true` for production |
| Program.cs | 26 | `UseDeveloperExceptionPage` unconditionally | Conditionally enable based on environment |
| Program.cs | 28 | HTTPS redirection commented out | Enable for production |
| Program.cs | 30 | Overly permissive CORS | Restrict to specific origins |
| appsettings.json | 8 | Debug log level for production | Use environment-specific config |
| appsettings.json | 10 | Weak JWT secret | Use strong, randomly generated key |
| SampleBankingApp.csproj | 10 | Debug symbols in release | Set `<DebugSymbols>false</DebugSymbols>` for release |

## 10. Missing Unit Tests

No test project found. Critical methods needing tests:
- `AuthService.Login` (authentication flow)
- `TransactionService.Transfer` (boundary conditions, fee calculation)
- `TransactionService.Deposit` (interest calculation)
- `UserService.GetUsersPage` (pagination logic)
- `UserService.SearchUsers` (SQL injection prevention)
- `StringHelper.IsValidEmail` (edge cases)
- `StringHelper.IsValidUsername` (edge cases)
- `EmailService.SendTransferNotification` (retry logic)
- `UserController.UpdateUser` (authorization checks)
- `UserController.DeleteUser` (authorization checks)