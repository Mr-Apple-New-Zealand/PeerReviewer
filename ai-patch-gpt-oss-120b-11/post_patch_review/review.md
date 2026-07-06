## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 28 | `ExecuteQuery` concatenates user input into SQL string, causing SQL injection. | Use parameterized queries exclusively; remove `ExecuteQuery` or sanitize inputs strictly. |
| DatabaseHelper.cs | 15 | Hardcoded fallback credentials (`sa`/`Admin1234!`) in constructor. | Remove hardcoded fallback; throw exception if connection string is missing. |
| AuthService.cs | 48 | Passwords hashed with SHA256 without salt, vulnerable to rainbow table attacks. | Use `BCrypt` or `Argon2` with unique salts for password hashing. |
| AuthService.cs | 82 | JWT token expiration set to 30 days, increasing risk of token theft/abuse. | Reduce expiration to a shorter duration (e.g., 1-2 hours) and implement refresh tokens. |
| TransactionController.cs | 48 | `Refund` endpoint lacks authorization checks beyond general `[Authorize]`. | Add specific role-based or ownership checks to prevent unauthorized refunds. |
| UserController.cs | 46 | `SearchUsers` and `GetAuditLog` lack authorization, exposing sensitive data. | Add `[Authorize]` and potentially role restrictions to these endpoints. |
| Program.cs | 48 | CORS policy allows any method and header, increasing attack surface. | Restrict allowed methods and headers to only those required by the client. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 52 | `RefundTransaction` throws `NotImplementedException`, breaking the API contract. | Implement the refund logic or return a proper `NotImplemented` status code. |
| UserService.cs | 104 | `SearchUsers` uses `LIKE` with `%` wildcards, potentially causing performance issues or injection if not handled by `ExecuteQuerySafe`. | Ensure `ExecuteQuerySafe` properly escapes parameters; consider full-text search for large datasets. |
| TransactionService.cs | 35 | `Transfer` calculates fee on `amount` but debits `amount + fee`; ensure UI reflects total cost. | Clarify fee calculation in documentation and UI to avoid user confusion. |
| AuthService.cs | 82 | JWT expiration uses `DateTime.UtcNow.AddDays(30)`, which may drift if server time changes. | Use `DateTimeOffset` for better time zone handling. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 50 | `Refund` catches `NotImplementedException` and returns 500, hiding implementation status. | Return `501 Not Implemented` or a specific error message indicating feature unavailability. |
| UserController.cs | 58 | `UpdateUser` catches `ArgumentException` and returns message, potentially exposing internal details. | Log the exception and return a generic error message to the client. |
| EmailService.cs | 48 | `SendWithRetries` swallows `SmtpException` after max retries, failing silently. | Log the final failure and consider throwing an exception or notifying admin. |
| TransactionService.cs | 68 | `Transfer` swallows exceptions in email sending, which is good, but lacks logging. | Add logging for email failures to aid debugging without affecting transaction success. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 22 | `GetOpenConnection` returns an open connection, risking leaks if caller doesn't dispose. | Use `using` statements in callers or refactor to return `IDisposable` connections. |
| DatabaseHelper.cs | 35 | `ExecuteQuerySafe` opens connection but relies on `using` in caller; ensure caller disposes. | Verify all callers of `ExecuteQuerySafe` use `using` or refactor to encapsulate disposal. |
| EmailService.cs | 42 | `SmtpClient` created inside loop; ensure it is disposed properly on each attempt. | The `using` statement handles disposal, but verify no exceptions skip disposal. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 22 | `User.FindFirst` may return null, causing `NullReferenceException` on `.Value`. | Use null-conditional operator `?.Value` and check for null before parsing. |
| UserController.cs | 40 | `User.FindFirst` may return null, causing `NullReferenceException` on `.Value`. | Use null-conditional operator `?.Value` and check for null before parsing. |
| AuthService.cs | 48 | `reader["Id"]` etc. may throw if column names mismatch or data is null. | Add null checks and default values for database reader results. |
| UserService.cs | 104 | `SearchUsers` may return null if `query` is null, causing issues in SQL parameter. | Add null check for `query` parameter in `SearchUsers`. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| StringHelper.cs | 28 | `JoinWithSeparator` duplicates `string.Join` functionality. | Remove method or use directly where needed without abstraction. |
| AuthService.cs | 92 | `ValidateToken` is defined but never called in the provided code. | Remove if unused or integrate into authentication flow. |
| TransactionService.cs | 104 | `RefundTransaction` is a stub; consider removing until implemented. | Remove or mark as `[Obsolete]` with a plan to implement. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 12 | `TransactionFeeRate`, `DepositInterestRate`, `DepositCap` are hardcoded constants. | Move to configuration (`appsettings.json`) for easy adjustment. |
| EmailService.cs | 12 | Email subjects and addresses are hardcoded constants. | Move to configuration for flexibility and localization support. |
| UserService.cs | 104 | `MaxPageSize` is hardcoded; consider making it configurable. | Move to configuration or define as a constant with clear documentation. |
| DatabaseHelper.cs | 15 | Fallback connection string contains hardcoded server and database names. | Remove fallback entirely; require configuration via environment variables. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 28 | `ExecuteQuery` uses string interpolation for SQL, promoting bad practices. | Remove or refactor to use parameterized queries exclusively. |
| UserService.cs | 104 | `SearchUsers` uses `LIKE` with `%` wildcards, which can be inefficient. | Consider full-text search or indexing for better performance. |
| TransactionService.cs | 35 | `Transfer` method is long and handles multiple responsibilities. | Refactor into smaller methods for balance update, transaction recording, and notification. |
| EmailService.cs | 42 | `SendWithRetries` uses `Console.WriteLine` for logging. | Use `ILogger` for proper logging integration. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 48 | CORS policy allows any method and header, which is overly permissive. | Restrict to specific methods and headers required by the application. |
| Program.cs | 38 | `UseDeveloperExceptionPage` is used in development, but ensure it's disabled in production. | Verify environment checks are correct and no debug info leaks in production. |
| SampleBankingApp.csproj | 10 | `TreatWarningsAsErrors` is false, allowing potential issues to go unnoticed. | Set to `true` to enforce stricter code quality. |
| appsettings.json | 1 | Connection strings and secrets use placeholders; ensure they are set via environment variables. | Document setup process and use secret management tools for production. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 48 | No tests for login logic, password hashing, and JWT generation. | Add unit tests for authentication flows and token validation. |
| TransactionService.cs | 35 | No tests for transfer, deposit, and refund logic. | Add unit tests for financial calculations and transaction integrity. |
| UserService.cs | 104 | No tests for user CRUD operations and search functionality. | Add unit tests for user management and pagination logic. |
| DatabaseHelper.cs | 28 | No tests for database helper methods, especially SQL injection prevention. | Add integration tests for database operations with mock data. |