## Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 32 | SQL injection via string interpolation in login query | Use parameterized queries with `ExecuteQuerySafe` |
| AuthService.cs | 61-66 | MD5 hashing is cryptographically broken and insecure | Use PBKDF2, bcrypt, or Argon2 for password hashing |
| AuthService.cs | 17 | Hardcoded admin bypass password in source code | Remove backdoor; enforce proper authentication |
| DatabaseHelper.cs | 29 | SQL injection via `ExecuteQuery` method with raw WHERE clause | Deprecate and remove this method; use only parameterized queries |
| DatabaseHelper.cs | 54 | SQL injection via `ExecuteNonQuery` with raw SQL string | Use parameterized queries exclusively |
| TransactionService.cs | 47-48 | SQL injection in UPDATE statements using string interpolation | Use parameterized queries with `ExecuteNonQuerySafe` |
| TransactionService.cs | 90 | SQL injection in INSERT statement for recording transactions | Use parameterized query with safe helper method |
| UserService.cs | 47 | SQL injection via string interpolation in UPDATE statement | Use parameterized query with `ExecuteNonQuerySafe` |
| UserService.cs | 61 | SQL injection via string interpolation in DELETE statement | Use parameterized query with `ExecuteNonQuerySafe` |
| UserService.cs | 99 | SQL injection via LIKE clause with raw user input | Use parameterized query with safe helper method |
| Program.cs | 38 | Overly permissive CORS policy allows any origin, method, and header | Restrict to specific origins and methods required by the application |
| Program.cs | 34 | Developer exception page enabled unconditionally | Conditionally enable only in Development environment |
| Program.cs | 36 | HTTPS redirection commented out | Uncomment and enforce HTTPS in production |
| EmailService.cs | 25-28 | SMTP credentials potentially hardcoded in configuration | Use secure secret management (Azure Key Vault, AWS Secrets Manager) |

## Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 42 | Incorrect boundary condition: checks `fromBalance >= amount` but should check `fromBalance >= totalDebit` | Change condition to `if (fromBalance >= totalDebit)` |
| TransactionService.cs | 68 | Interest bonus calculation applies 5% for 1 unit of time without clear context | Define and use a named constant with clear time period |
| UserService.cs | 72 | Off-by-one error in pagination: uses `page * pageSize` instead of `(page-1) * pageSize` | Change to `int skip = (page - 1) * pageSize;` |
| AuthService.cs | 53-56 | Admin backdoor allows authentication without proper credential verification | Remove this fallback path entirely |

## Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionController.cs | 29 | No transaction scope around transfer operation (two DB writes) | Wrap in a database transaction to ensure atomicity |
| TransactionService.cs | 47-56 | Email sending after DB commit can fail, leaving inconsistent state | Move email send inside the same transaction or use outbox pattern |
| UserController.cs | 50 | Catches broad `Exception` and returns raw message to client | Catch specific exceptions and return safe error messages |
| UserController.cs | 72-76 | SearchUsers catches all exceptions and returns empty list, hiding errors | Log the exception and return appropriate status code |
| EmailService.cs | 53-60 | Retry loop for SMTP sends can exhaust resources without backoff | Implement exponential backoff in retry logic |
| AuthService.cs | 104-108 | Unreachable code after `return true` in ValidateToken method | Remove dead code after the early return |

## Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 21-23 | SqlConnection opened but not disposed if exception occurs before Close() | Use `using` statement to ensure disposal |
| AuthService.cs | 34-38 | SqlConnection and SqlCommand not properly disposed in Login method | Wrap in `using` statements or use DatabaseHelper safe methods |
| EmailService.cs | 16 | SmtpClient held as instance field is not thread-safe and leaks sockets | Create and dispose SmtpClient per send operation |

## Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionController.cs | 27 | `userIdClaim?.Value` parsed without null check after null-conditional | Add explicit null check before `int.Parse` |
| UserController.cs | 41-53 | UpdateUser parameters used without null checks | Validate email and username are not null/empty |
| StringHelper.cs | 65-71 | IsBlank method can be simplified using existing framework methods | Use `string.IsNullOrWhiteSpace(value)` directly |

## Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 68-78 | ExecuteQueryWithParams is marked Obsolete and unused | Remove this method entirely |
| StringHelper.cs | 29-36 | JoinWithSeparator has a broken implementation (trailing separator) | Remove in favor of JoinWithSeparatorFixed |
| AuthService.cs | 91-96 | HashPasswordSha1 is defined but never called | Remove this unused method |
| TransactionService.cs | 94-97 | FormatCurrency is defined but never called | Remove this unused method |

## Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 17 | Hardcoded admin bypass password string | Remove entirely; no safe alternative exists |
| TransactionService.cs | 11 | Hardcoded transaction fee rate (0.015m) | Move to configuration file |
| TransactionService.cs | 12 | Hardcoded max transactions per day (10) | Move to configuration file |
| UserService.cs | 70 | Hardcoded max page size (50) | Move to configuration file |
| EmailService.cs | 10-14 | Multiple hardcoded email constants | Consolidate into configuration or named constants in one place |

## Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 32-35 | String concatenation in loop creates O(n²) performance | Use `string.Join` as shown in fixed version |
| StringHelper.cs | 16,25 | Regex objects created inside methods called repeatedly | Make regex fields `static readonly` |
| UserService.cs | 10-11 | Shared mutable static state (_auditLog, _requestCount) not thread-safe | Use thread-local storage or instance fields with proper synchronization |
| DatabaseHelper.cs | 15-17 | Hardcoded fallback connection string in constructor | Fail fast if configuration is missing |
| UserService.cs | 86-93 | Manual string concatenation in GetAuditReport | Use `string.Join(Environment.NewLine, _auditLog)` |

## Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 24 | ValidateLifetime set to false for JWT tokens | Set to true and configure appropriate clock skew |
| appsettings.json | 6 | Weak JWT secret key ("mysecretkey") | Use a strong, randomly generated key of sufficient length |
| EmailService.cs | 29 | EnableSsl set to false in SMTP client | Enable SSL/TLS for email transmission security |

## Missing Unit Tests

No test project exists. Critical methods needing tests include:
- AuthService.Login (boundary conditions, SQL injection resistance)
- TransactionService.Transfer (sufficient funds, fee calculation, atomicity)
- UserService.GetUsersPage (pagination boundaries, empty results)
- EmailService.SendTransferNotification (retry logic, error handling)

The project should add a test project with xUnit or NUnit and implement tests for these core functionalities, especially focusing on security, financial calculations, and error conditions.