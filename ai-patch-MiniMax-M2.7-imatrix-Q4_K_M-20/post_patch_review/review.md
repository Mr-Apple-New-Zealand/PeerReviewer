## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/AuthService.cs | 58 | Passwords are hashed using SHA-256 without a salt, making them vulnerable to rainbow table attacks. | Use a dedicated password hashing algorithm like PBKDF2, BCrypt, or Argon2. |
| Services/AuthService.cs | 108 | JWT expiration is hardcoded to 30 days, which is excessively long for a security token. | Reduce expiration to a reasonable duration (e.g., 1-24 hours) and implement refresh tokens. |
| Controllers/AuthController.cs | 28 | Failed login attempts are logged but not rate-limited, enabling brute-force attacks. | Implement rate limiting or account lockout mechanisms after multiple failed attempts. |
| Controllers/UserController.cs | 43 | `GetUser` endpoint lacks authorization checks, allowing any authenticated user to view any other user's data. | Add `[Authorize]` and verify the requesting user owns the resource or is an Admin. |
| Controllers/UserController.cs | 73 | `SearchUsers` endpoint lacks authorization, potentially exposing user data via enumeration. | Add `[Authorize]` and restrict access to Admins or implement strict result filtering. |
| Services/TransactionService.cs | 45 | Balance checks and updates are not atomic within a single transaction scope for the read-check-write pattern. | Perform the balance check and update within the same database transaction to prevent race conditions. |
| Data/DatabaseHelper.cs | 22 | `AddWithValue` is used for parameters, which can lead to SQL injection or performance issues due to type inference. | Use `Add` with explicit `SqlDbType` and size parameters. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/TransactionService.cs | 68 | Deposit logic adds interest bonus to the balance but records only the principal amount in the transaction log. | Ensure the transaction log reflects the total credited amount or separate the interest entry. |
| Services/TransactionService.cs | 68 | Deposit does not verify if the user exists before attempting to update the balance. | Add a check to ensure the user ID exists before executing the update. |
| Services/TransactionService.cs | 68 | Deposit does not wrap the balance update and transaction recording in a transaction. | Use `ExecuteInTransaction` to ensure atomicity of balance update and log insertion. |
| Services/UserService.cs | 65 | `GetUsersPage` does not validate that `page` is greater than 0, potentially causing negative skip values. | Add validation to ensure `page >= 1`. |
| Services/UserService.cs | 115 | `SearchUsers` constructs LIKE pattern manually (`%{query}%`) which may allow SQL injection if not properly parameterized (though parameters are used, wildcards are embedded). | Ensure the parameter value is properly escaped or rely on the ORM/DB driver's handling of wildcards in parameters. |
| Controllers/TransactionController.cs | 38 | `Transfer` does not validate that `request.ToUserId` is positive or valid. | Add validation for `ToUserId` similar to `fromUserId`. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Controllers/UserController.cs | 58 | `ArgumentException` message is returned directly to the client, leaking internal implementation details. | Return a generic error message and log the specific exception. |
| Services/EmailService.cs | 52 | `SmtpException` in `SendWelcomeEmail` is caught and printed to console, failing silently to the caller. | Log the error properly and consider whether to throw or return a status to the caller. |
| Services/TransactionService.cs | 82 | Email failure is caught and ignored, which is acceptable, but the generic `catch` block swallows all other exceptions. | Log the specific exception in the generic catch block for debugging. |
| Controllers/TransactionController.cs | 52 | `Refund` catches `NotImplementedException` and returns 500, but the method always throws it. | Remove the try-catch and return `NotImplemented` (501) or implement the feature. |
| Data/DatabaseHelper.cs | 48 | `ExecuteInTransaction` catches all exceptions, rolls back, and re-throws, but does not log the error. | Log the exception before re-throwing to aid in debugging transaction failures. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Data/DatabaseHelper.cs | 22 | `DataTable.Load(reader)` is used, but `DataTable` is not disposed, though `reader` is disposed via `using`. | `DataTable` does not implement `IDisposable`, so this is safe, but ensure no other resources are leaked. |
| Services/EmailService.cs | 35 | `MailMessage` is disposed via `using`, which is correct. | No issue. |
| Services/EmailService.cs | 48 | `SmtpClient` is disposed via `using`, which is correct. | No issue. |
| Data/DatabaseHelper.cs | 15 | `SqlConnection` is disposed via `using`, which is correct. | No issue. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/AuthService.cs | 45 | Casting `row["Id"]` to `int` will throw if the value is null or not an integer. | Use `Convert.ToInt32` or check for `DBNull`. |
| Services/AuthService.cs | 46 | Casting `row["Username"]` to `string` will throw if the value is null. | Check for `DBNull` before casting. |
| Services/UserService.cs | 125 | Casting `row["Id"]` to `int` will throw if the value is null. | Use `Convert.ToInt32` or check for `DBNull`. |
| Controllers/TransactionController.cs | 22 | `User.FindFirst` may return null, and `.Value` is accessed without null check. | Use null-conditional operator `?.Value` and check for null before parsing. |
| Controllers/UserController.cs | 48 | `User.FindFirst` may return null, and `.Value` is accessed without null check. | Use null-conditional operator `?.Value` and check for null before parsing. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/TransactionService.cs | 95 | `RefundTransaction` throws `NotImplementedException` and is not implemented. | Implement the method or remove it if not needed. |
| Helpers/StringHelper.cs | 28 | `JoinWithSeparator` simply wraps `string.Join`, adding no value. | Remove the method and use `string.Join` directly. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/TransactionService.cs | 65 | Interest rate `0.01m` is hardcoded. | Move to configuration. |
| Services/TransactionService.cs | 98 | Default fee rate `0.015m` is hardcoded. | Move to configuration. |
| Services/TransactionService.cs | 103 | Default deposit cap `1_000_000m` is hardcoded. | Move to configuration. |
| Services/UserService.cs | 63 | Max page size `50` is hardcoded. | Move to configuration. |
| Services/UserService.cs | 110 | User ID max range `1_000_000` is hardcoded. | Move to configuration or remove if not needed. |
| Services/EmailService.cs | 10 | Email subjects are hardcoded. | Move to configuration. |
| Services/EmailService.cs | 12 | Max retries `3` is hardcoded. | Move to configuration. |
| Services/EmailService.cs | 13 | SMTP timeout `5000` is hardcoded. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/UserService.cs | 10 | `AuditLog` is a static list, which can grow indefinitely and cause memory leaks. | Use a proper logging framework or database for audit logs. |
| Services/UserService.cs | 11 | `AuditLock` is used for thread safety, but static state is generally discouraged in web apps. | Use a scoped or transient service for audit logging. |
| Data/DatabaseHelper.cs | 22 | `AddWithValue` is used, which can lead to performance issues and incorrect type inference. | Use `Add` with explicit `SqlDbType`. |
| Services/EmailService.cs | 52 | `Console.WriteLine` is used for logging, which is not appropriate for production. | Use `ILogger` for logging. |
| Services/TransactionService.cs | 82 | Empty catch block swallows exceptions without logging. | Log the exception. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 38 | JWT secret is read from configuration, but if it's missing, the app throws at startup. | Ensure the secret is always provided via environment variables. |
| Program.cs | 52 | CORS policy allows any method and header, which is overly permissive. | Restrict allowed methods and headers to only those needed. |
| Program.cs | 52 | CORS origins are read from configuration, but if empty, it allows no origins. | Ensure at least one origin is configured or handle the empty case gracefully. |
| SampleBankingApp.csproj | 10 | `TreatWarningsAsErrors` is set to `false`, which can hide potential issues. | Set to `true` to enforce code quality. |
| appsettings.json | 2 | Connection string is set to `__SET_VIA_ENV__`, which is a placeholder. | Ensure the actual connection string is provided via environment variables. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create a test project and add unit tests for all services and controllers. |
| Services/TransactionService.cs | 20 | `Transfer` method has complex logic including balance checks, fees, and transactions. | Add unit tests for successful transfer, insufficient funds, self-transfer, and system errors. |
| Services/TransactionService.cs | 60 | `Deposit` method has logic for interest and caps. | Add unit tests for valid deposit, invalid amount, and cap exceeded. |
| Services/AuthService.cs | 25 | `Login` method has logic for password hashing and user lookup. | Add unit tests for valid login, invalid password, and inactive user. |
| Services/UserService.cs | 20 | `GetUserById` and `UpdateUser` have validation logic. | Add unit tests for valid and invalid user IDs. |
| Controllers/AuthController.cs | 15 | `Login` endpoint has validation logic. | Add integration tests for login flow. |
| Controllers/TransactionController.cs | 15 | `Transfer` endpoint has validation logic. | Add integration tests for transfer flow. |