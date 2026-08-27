## Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 26-34 | SQL injection vulnerability in `ExecuteQuery` method due to string interpolation. | Use parameterized queries with `ExecuteQuerySafe`. |
| DatabaseHelper.cs | 15-17 | Hardcoded credentials in the fallback connection string. | Remove hardcoded credentials and ensure configuration is secure. |
| AuthService.cs | 32 | SQL injection vulnerability in `Login` method due to string interpolation. | Use parameterized queries with `ExecuteQuerySafe`. |
| AuthService.cs | 61-66 | Weak cryptography using MD5 for password hashing. | Use a stronger hashing algorithm like bcrypt or PBKDF2. |
| Program.cs | 34 | Developer exception page enabled unconditionally. | Conditionally enable based on environment. |
| Program.cs | 36 | HTTPS redirection commented out. | Uncomment and ensure HTTPS is enforced in production. |
| Program.cs | 38 | Overly permissive CORS policy allowing any origin, method, and header. | Restrict CORS to specific origins and methods. |
| AuthService.cs | 17 | Hardcoded admin bypass password. | Remove hardcoded backdoor credentials. |
| AuthService.cs | 24 | `ValidateLifetime` set to false in JWT configuration. | Set `ValidateLifetime` to true for production. |
| EmailService.cs | 30 | SMTP client configured with SSL disabled. | Enable SSL for secure email transmission. |

## Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 42 | Incorrect boundary condition: checks `fromBalance >= amount` but should check `fromBalance >= totalDebit`. | Update condition to `fromBalance >= totalDebit`. |
| UserService.cs | 72 | Off-by-one error in pagination: `skip = page * pageSize` should be `(page - 1) * pageSize`. | Correct the pagination logic. |
| TransactionService.cs | 68 | Incorrect interest rate calculation: `amount * 0.05m * 1` is unclear and potentially incorrect. | Use a named constant for clarity and accuracy. |
| UserService.cs | 99 | SQL injection vulnerability in `SearchUsers` method due to string interpolation. | Use parameterized queries with `ExecuteQuerySafe`. |

## Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 34-38 | `SqlConnection` and `SqlCommand` not properly disposed in `Login` method. | Use `using` statements to ensure disposal. |
| TransactionController.cs | 56-59 | Catches `NotImplementedException` and returns a generic error message. | Remove try-catch block or handle more specifically. |
| UserController.cs | 50-53 | Catches broad `Exception` and returns raw exception message to client. | Log the error and return a generic error message. |
| EmailService.cs | 75-78 | Catches broad `Exception` and swallows it silently in `SendWelcomeEmail`. | Log the error and consider rethrowing or handling appropriately. |
| TransactionService.cs | 47-48 | Database updates not wrapped in a transaction, risking inconsistent state. | Use a transaction to ensure atomicity. |

## Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 21-23 | `SqlConnection` opened but not disposed in `GetOpenConnection`. | Use `using` statement or ensure caller disposes the connection. |
| AuthService.cs | 34-38 | `SqlConnection` and `SqlCommand` not properly disposed in `Login` method. | Use `using` statements to ensure disposal. |
| EmailService.cs | 22-31 | `SmtpClient` held as an instance field, which is not thread-safe and may leak sockets. | Create and dispose `SmtpClient` per operation. |

## Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionController.cs | 27 | `userIdClaim` could be null, leading to null reference in `int.Parse`. | Add null check before parsing. |
| UserService.cs | 31 | `table.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing. |
| AuthService.cs | 70 | `_config["Jwt:SecretKey"]` could be null, leading to null reference in `GetBytes`. | Add null check or ensure configuration is present. |

## Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 67-78 | `ExecuteQueryWithParams` method marked as obsolete and unused. | Remove the method. |
| AuthService.cs | 91-96 | `HashPasswordSha1` method defined but never called. | Remove the method. |
| StringHelper.cs | 30-36 | `JoinWithSeparator` method defined but `JoinWithSeparatorFixed` is used instead. | Remove `JoinWithSeparator`. |
| TransactionService.cs | 94-97 | `FormatCurrency` method defined but never called. | Remove the method. |

## Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 16 | Hardcoded fallback connection string with credentials. | Remove hardcoded values and use configuration. |
| AuthService.cs | 17 | Hardcoded admin bypass password. | Remove hardcoded backdoor credentials. |
| TransactionService.cs | 11 | Magic number `0.015m` for transaction fee rate. | Define as a named constant in configuration. |
| TransactionService.cs | 12 | Magic number `10` for max transactions per day. | Define as a named constant in configuration. |
| UserService.cs | 70 | Magic number `50` for maximum page size. | Define as a named constant in configuration. |

## Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 31-36 | String concatenation inside loop in `JoinWithSeparator`. | Use `StringBuilder` or `string.Join`. |
| StringHelper.cs | 25 | `new Regex(...)` created inside method called repeatedly. | Make `Regex` static readonly. |
| UserService.cs | 10-11 | Shared mutable static state `_auditLog` and `_requestCount` accessed from multiple threads without synchronization. | Use thread-safe collections or synchronization. |
| StringHelper.cs | 65-71 | Reimplementation of `string.IsNullOrWhiteSpace` in `IsBlank`. | Use standard library method. |
| UserService.cs | 86-93 | String concatenation inside loop in `GetAuditReport`. | Use `StringBuilder` or `string.Join`. |

## Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 34 | `UseDeveloperExceptionPage` called unconditionally. | Conditionally enable based on environment. |
| Program.cs | 36 | HTTPS redirection commented out. | Uncomment and ensure HTTPS is enforced in production. |
| Program.cs | 38 | Overly permissive CORS policy. | Restrict CORS to specific origins and methods. |
| appsettings.json | 6 | Weak JWT secret key. | Use a strong, randomly generated key. |
| SampleBankingApp.csproj | 7 | `TreatWarningsAsErrors` set to false. | Set to true for production code. |

## Missing Unit Tests

No test project exists. Critical methods and scenarios that need unit tests include:

- **AuthService.Login**: Test with valid and invalid credentials, SQL injection attempts.
- **AuthService.GenerateJwtToken**: Test token generation and validation.
- **TransactionService.Transfer**: Test with sufficient and insufficient funds, boundary conditions for amount.
- **TransactionService.Deposit**: Test with valid and invalid deposit amounts.
- **UserService.GetUserById**: Test with valid and invalid user IDs.
- **UserService.UpdateUser**: Test with valid and invalid user data.
- **UserService.DeleteUser**: Test with valid and invalid user IDs.
- **UserService.GetUsersPage**: Test pagination logic and boundary conditions.
- **UserService.SearchUsers**: Test with various search queries, including SQL injection attempts.