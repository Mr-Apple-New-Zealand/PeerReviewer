# Code Review Report

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 16 | SQL injection vulnerability in `ExecuteQuery` method | Use parameterized queries instead of string concatenation |
| DatabaseHelper.cs | 14 | Hardcoded credentials in fallback connection string | Remove hardcoded credentials and rely on configuration |
| AuthService.cs | 18 | SQL injection vulnerability in `Login` method | Use `ExecuteQuerySafe` with parameters |
| AuthService.cs | 30 | MD5 hashing is insecure | Use PBKDF2, bcrypt, or Argon2 for password hashing |
| AuthService.cs | 30 | Hardcoded admin bypass password | Remove backdoor or secure it properly |
| AuthService.cs | 58 | SHA1 hashing is insecure | Remove unused method or replace with secure algorithm |
| AuthService.cs | 66 | `ValidateToken` method returns true without validation | Implement proper JWT validation |
| Program.cs | 16 | `ValidateLifetime = false` on JWT | Set to true for production |
| Program.cs | 20 | `UseDeveloperExceptionPage` unconditionally called | Conditionally enable only in development |
| Program.cs | 22 | HTTPS redirection commented out | Uncomment for production |
| Program.cs | 24 | Overly permissive CORS policy | Restrict to specific origins and methods |
| appsettings.json | 2 | Production password in source control | Move to secure secrets management |
| appsettings.json | 8 | Weak JWT secret key | Use a strong, randomly generated key |
| SampleBankingApp.csproj | 10 | Debug symbols enabled in release build | Set `DebugSymbols` to false for release |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 20 | Fee calculation excludes minimum fee check | Add minimum fee validation |
| TransactionService.cs | 26 | Balance check doesn't account for fee | Check `fromBalance >= totalDebit` instead |
| TransactionService.cs | 34 | No transaction for fee deduction | Record fee as separate transaction |
| TransactionService.cs | 42 | Interest rate applied as 5% instead of 1% | Correct the interest rate constant |
| UserService.cs | 28 | Pagination uses `page * pageSize` (off-by-one) | Use `(page - 1) * pageSize` |
| UserService.cs | 60 | Search uses string interpolation for SQL | Use parameterized query |
| TransactionController.cs | 14 | No self-transfer check | Add validation to prevent transferring to oneself |
| TransactionService.cs | 16 | No daily limit check before transfer | Call `IsWithinDailyLimit` before processing |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserController.cs | 34 | Broad exception catch returns 500 with message | Log error and return generic message |
| UserController.cs | 46 | Broad exception catch swallows error details | Return specific error messages |
| EmailService.cs | 42 | Email failure silently caught | Propagate or log exception properly |
| UserService.cs | 62 | Empty list returned on error | Return null or throw exception |
| DatabaseHelper.cs | 22 | Connection not disposed in `ExecuteQuery` | Use `using` statement |
| DatabaseHelper.cs | 34 | Connection not disposed if exception occurs | Use `using` statement |
| TransactionService.cs | 36 | Email send after DB commit | Move email send before commit or use transaction |
| AuthService.cs | 24 | Connection not disposed if exception occurs | Use `using` statement |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 12 | Connection not disposed in `GetOpenConnection` | Document ownership transfer or use `using` |
| DatabaseHelper.cs | 22 | Connection and command not disposed | Use `using` statements |
| DatabaseHelper.cs | 34 | Connection not disposed in error path | Use `using` statement |
| EmailService.cs | 18 | `SmtpClient` as instance field (not thread-safe) | Create new instance per send |
| EmailService.cs | 30 | `MailMessage` not disposed | Use `using` statement |
| EmailService.cs | 42 | `MailMessage` not disposed | Use `using` statement |
| EmailService.cs | 52 | `MailMessage` not disposed | Use `using` statement |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionController.cs | 14 | `userIdClaim` could be null | Add null check before `int.Parse` |
| UserController.cs | 14 | No null check for `UpdateUserRequest` | Add `[Required]` attributes or null check |
| UserController.cs | 24 | No null check for `query` parameter | Add validation |
| DatabaseHelper.cs | 11 | Configuration key might be null | Add null check |
| AuthService.cs | 20 | Configuration might be null | Add null check |
| TransactionService.cs | 18 | No check for empty result set | Check `Rows.Count > 0` |
| UserService.cs | 22 | No check for empty result set | Check `Rows.Count > 0` |
| StringHelper.cs | 34 | No null check before `Length` | Add null guard |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 42 | `ExecuteQueryWithParams` marked obsolete | Remove method |
| StringHelper.cs | 24 | `JoinWithSeparator` has broken implementation | Remove in favor of `JoinWithSeparatorFixed` |
| AuthService.cs | 58 | `HashPasswordSha1` unused | Remove method |
| AuthService.cs | 66 | `ValidateToken` has unreachable code | Fix return statement |
| TransactionController.cs | 32 | `Refund` throws NotImplementedException | Remove or implement properly |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 12 | Fee rate as magic number | Move to configuration |
| TransactionService.cs | 13 | Max transactions as magic number | Move to configuration |
| TransactionService.cs | 42 | Interest rate as magic number | Move to configuration |
| UserService.cs | 20 | ID range limits as magic numbers | Move to constants |
| UserService.cs | 28 | Page size limit as magic number | Move to constant |
| UserService.cs | 34 | Email address as magic string | Move to constant |
| EmailService.cs | 8-9 | Email subjects as magic strings | Move to constants |
| EmailService.cs | 10 | Max retries as magic number | Move to configuration |
| EmailService.cs | 11 | Timeout as magic number | Move to configuration |
| StringHelper.cs | 6 | Email length limit as magic number | Move to constant |
| StringHelper.cs | 14 | Username length limits as magic numbers | Move to constants |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 24 | String concatenation in loop | Use `StringBuilder` properly |
| StringHelper.cs | 28 | Duplicate of `JoinWithSeparatorFixed` | Remove broken version |
| StringHelper.cs | 38 | Duplicate of `ObfuscateAccount` | Remove one implementation |
| StringHelper.cs | 46 | Reimplements `string.IsNullOrWhiteSpace` | Use built-in method |
| UserService.cs | 8 | Shared mutable static state | Use thread-safe collection |
| UserService.cs | 9 | Shared mutable static state | Use thread-safe counter |
| UserService.cs | 56 | String concatenation in loop | Use `StringBuilder` |
| DatabaseHelper.cs | 42 | Obsolete method still present | Remove method |
| EmailService.cs | 18 | `SmtpClient` as instance field | Create per send |
| TransactionService.cs | 50 | String interpolation in SQL | Use parameterized query |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 16 | `UseDeveloperExceptionPage` unconditionally | Conditionally enable |
| Program.cs | 22 | Overly permissive CORS | Restrict to specific origins |
| Program.cs | 24 | HTTPS redirection commented | Enable for production |
| appsettings.json | 12 | Debug log level for production | Use environment-specific config |
| SampleBankingApp.csproj | 10 | Debug symbols in release | Disable for release builds |
| appsettings.json | 8 | Weak JWT secret | Use strong secret |
| Program.cs | 4 | No environment check for JWT config | Add validation |
| Program.cs | 16 | No validation for JWT secret | Add null/empty check |

## 10. Missing Unit Tests

No test project found. Critical methods needing tests:
- `AuthService.Login` (authentication flow)
- `TransactionService.Transfer` (boundary conditions, fee calculation)
- `TransactionService.Deposit` (interest calculation)
- `UserService.GetUsersPage` (pagination logic)
- `UserService.SearchUsers` (SQL injection prevention)
- `StringHelper.IsValidEmail` (edge cases)
- `EmailService.SendTransferNotification` (retry logic)
- `DatabaseHelper.ExecuteQuerySafe` (parameter handling)
- `UserController.UpdateUser` (authorization checks)
- `TransactionController.Transfer` (self-transfer prevention)