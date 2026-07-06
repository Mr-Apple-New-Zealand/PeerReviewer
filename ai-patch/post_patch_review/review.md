## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Data/DatabaseHelper.cs | 24 | `ExecuteQuery` accepts raw `whereClause` string, enabling SQL injection if called with user input. | Remove method or enforce strict allow-listing of clauses; use parameterized queries exclusively. |
| Services/AuthService.cs | 48 | Password hashing uses SHA-256 with username as salt, which is cryptographically weak and vulnerable to rainbow tables. | Use a dedicated password hashing algorithm like BCrypt, Argon2, or PBKDF2. |
| Services/AuthService.cs | 88 | `ValidateToken` checks expiration manually without verifying the signature or issuer/audience. | Use `JwtSecurityTokenHandler.ValidateToken` with proper validation parameters. |
| Controllers/UserController.cs | 58 | `SearchUsers` allows unauthenticated access to user data via `LIKE` query. | Add `[Authorize]` attribute and implement role-based access control. |
| Controllers/UserController.cs | 64 | `GetAuditLog` exposes internal audit logs to any authenticated user. | Restrict access to Admin role only. |
| Program.cs | 42 | JWT secret is loaded from config but not validated for minimum length or entropy. | Validate secret length (e.g., >32 chars) at startup. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/TransactionService.cs | 108 | `Deposit` adds interest bonus to balance but records only the principal amount in the transaction log. | Record the total amount (principal + bonus) or separate the bonus as a distinct transaction type. |
| Services/TransactionService.cs | 108 | `Deposit` does not check if the user exists before updating balance. | Verify user existence before executing the update. |
| Services/TransactionService.cs | 122 | `IsWithinDailyLimit` uses `GETDATE()` which may vary slightly between calls; consider using a consistent time source. | Use `DateTime.UtcNow.Date` for consistent daily boundary checks. |
| Controllers/TransactionController.cs | 22 | `Transfer` returns `Unauthorized` if user ID parsing fails, but doesn't distinguish between missing token and invalid format. | Return `BadRequest` for invalid format and `Unauthorized` for missing token. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Controllers/UserController.cs | 45 | `UpdateUser` returns `ex.Message` to the client, leaking internal implementation details. | Return a generic error message and log the exception. |
| Controllers/TransactionController.cs | 38 | `Refund` catches `NotImplementedException` and returns 500, but the feature is explicitly unimplemented. | Return `501 Not Implemented` or remove the endpoint until implemented. |
| Services/EmailService.cs | 48 | `SendWelcomeEmail` swallows `SmtpException` silently, providing no feedback on failure. | Log the error and consider returning a failure status to the caller. |
| Services/TransactionService.cs | 85 | `Transfer` logs email failure but continues execution, which is correct, but the log message is misleading if the transfer itself failed. | Ensure logging only occurs on successful transfers. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Data/DatabaseHelper.cs | 24 | `ExecuteQuery` creates `SqlConnection` and `SqlCommand` but relies on `using` for disposal; however, `SqlDataAdapter` is not disposed. | Wrap `SqlDataAdapter` in a `using` statement. |
| Data/DatabaseHelper.cs | 38 | `ExecuteQuerySafe` does not dispose `SqlDataAdapter`. | Wrap `SqlDataAdapter` in a `using` statement. |
| Data/DatabaseHelper.cs | 52 | `ExecuteNonQuery` does not dispose `SqlDataAdapter` (if used) or ensure command disposal on exception. | Ensure `SqlCommand` is disposed via `using`. |
| Services/EmailService.cs | 30 | `SmtpClient` is created per call, which is correct, but `MailMessage` is not disposed if `Send` throws. | Wrap `MailMessage` in a `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/AuthService.cs | 35 | `row["Password"]` cast to string may throw if column is null. | Use `as string` or null-coalescing operator. |
| Services/TransactionService.cs | 75 | `fromUserTable.Rows[0]["Balance"]` cast may throw if column is null. | Use `as decimal?` or null-coalescing. |
| Services/UserService.cs | 25 | `row["Id"]` cast may throw if column is null. | Use safe casting or null checks. |
| Controllers/AuthController.cs | 18 | `request.Username` and `request.Password` are not validated for null/empty before use. | Add model validation attributes or manual checks. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Helpers/StringHelper.cs | 28 | `JoinWithSeparator` duplicates `string.Join` functionality. | Remove method and use `string.Join` directly. |
| Services/TransactionService.cs | 130 | `RefundTransaction` throws `NotImplementedException` and is not used elsewhere. | Remove method or implement functionality. |
| Data/DatabaseHelper.cs | 24 | `ExecuteQuery` is not called anywhere in the codebase. | Remove method if unused. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/TransactionService.cs | 108 | Hardcoded `0.015m` fee rate and `1_000_000m` max deposit. | Use configuration values consistently. |
| Services/AuthService.cs | 75 | Hardcoded `8` hours for token expiration. | Move to configuration. |
| Controllers/UserController.cs | 18 | Hardcoded `20` for default page size. | Move to configuration or constant. |
| Services/UserService.cs | 10 | Hardcoded `1_000_000` for max user ID. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Data/DatabaseHelper.cs | 24 | Raw SQL string concatenation in `ExecuteQuery`. | Use parameterized queries exclusively. |
| Services/AuthService.cs | 48 | Custom password hashing implementation. | Use established libraries like BCrypt. |
| Services/EmailService.cs | 30 | `SmtpClient` created per call, which is inefficient. | Consider using a singleton or connection pooling. |
| Controllers/UserController.cs | 45 | Exception handling returns `ex.Message` to client. | Log exception and return generic error. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 42 | JWT secret loaded from config without validation. | Validate secret length and entropy. |
| Program.cs | 50 | CORS policy allows any method and header. | Restrict to specific methods and headers. |
| Program.cs | 60 | `UseDeveloperExceptionPage()` is used in development, which is correct, but ensure it's not enabled in production. | Verify environment checks. |
| SampleBankingApp.csproj | 10 | `TreatWarningsAsErrors` is false. | Set to true to enforce code quality. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/AuthService.cs | 20 | No tests for login logic, password hashing, and token generation. | Add unit tests for authentication flows. |
| Services/TransactionService.cs | 25 | No tests for transfer, deposit, and refund logic. | Add unit tests for transaction scenarios. |
| Services/UserService.cs | 15 | No tests for user CRUD operations and pagination. | Add unit tests for user management. |
| Controllers/AuthController.cs | 10 | No integration tests for login endpoint. | Add integration tests for API endpoints. |