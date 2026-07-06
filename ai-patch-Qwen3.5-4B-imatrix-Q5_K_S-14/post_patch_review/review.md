## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/AuthService.cs | 48 | MD5 is cryptographically broken and unsuitable for password hashing. | Use BCrypt, Argon2, or PBKDF2. |
| Services/AuthService.cs | 23 | Passwords are compared directly in SQL without verifying hash strength or salting. | Ensure passwords are salted and hashed securely before storage/comparison. |
| Data/DatabaseHelper.cs | 15 | Hardcoded fallback credentials (`sa`/`Admin1234!`) in source code. | Remove hardcoded credentials; fail securely if config is missing. |
| Services/EmailService.cs | 22 | Hardcoded fallback SMTP credentials in source code. | Remove hardcoded credentials; fail securely if config is missing. |
| Program.cs | 38 | CORS policy allows any origin, method, and header, enabling cross-site attacks. | Restrict CORS to specific trusted origins and methods. |
| Controllers/UserController.cs | 24 | `GetUser` lacks authorization check for ownership, allowing any authenticated user to view any user's data. | Add `[Authorize]` with role checks or verify `userId` matches claim. |
| Controllers/UserController.cs | 42 | `UpdateUser` lacks authorization check, allowing any user to update any other user's data. | Verify the requesting user owns the resource or has admin privileges. |
| Controllers/UserController.cs | 58 | `DeleteUser` lacks authorization check, allowing any user to delete any other user. | Verify the requesting user owns the resource or has admin privileges. |
| Controllers/TransactionController.cs | 35 | `Transfer` does not verify that the `fromUserId` in the request matches the authenticated user's ID. | Validate that `fromUserId` equals `User.FindFirst(ClaimTypes.NameIdentifier)?.Value`. |
| Controllers/TransactionController.cs | 55 | `Deposit` does not verify that the `userId` in the request matches the authenticated user's ID. | Validate that `userId` equals `User.FindFirst(ClaimTypes.NameIdentifier)?.Value`. |
| Services/AuthService.cs | 85 | JWT token expiration is set to 30 days, which is excessively long for security. | Reduce expiration to a reasonable timeframe (e.g., 1-24 hours) and use refresh tokens. |
| Program.cs | 15 | JWT secret key falls back to a hardcoded string if configuration is missing. | Fail application startup if JWT secret is not configured securely. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/TransactionService.cs | 58 | `Deposit` calculates interest bonus but does not validate if the user exists before accessing `Rows[0]`. | Check `Rows.Count > 0` before accessing the balance. |
| Services/TransactionService.cs | 58 | `Deposit` uses `as decimal` on a database value which may return null or wrong type, causing runtime errors. | Use explicit casting with null checks or `Convert.ToDecimal`. |
| Services/TransactionService.cs | 100 | `RecordTransaction` is called without a transaction context in `Deposit` if `transaction` is null, but `ExecuteNonQuery` signature implies it might need it. | Ensure `RecordTransaction` handles null transactions correctly or always passes one. |
| Services/UserService.cs | 68 | `GetUsersPage` does not validate `page` or `pageSize` for negative values, potentially causing SQL errors or unexpected results. | Add validation to ensure `page >= 1` and `pageSize > 0`. |
| Services/UserService.cs | 22 | `ValidateUserId` caps ID at 1,000,000, which is an arbitrary and likely incorrect business constraint. | Remove or increase the upper bound based on actual database constraints. |
| Controllers/TransactionController.cs | 18 | `Transfer` parses `userIdClaim` as int but doesn't handle `OverflowException` if the claim is too large. | Catch `OverflowException` or use `int.TryParse`. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/UserService.cs | 85 | `SearchUsers` catches `Exception` and returns an empty list, hiding errors from the caller. | Log the error and rethrow or return a specific error response. |
| Services/EmailService.cs | 58 | `SendWelcomeEmail` catches `Exception` and prints to console, silently failing in production. | Log the error properly and consider retrying or notifying admin. |
| Services/TransactionService.cs | 75 | `Transfer` catches all exceptions and returns a generic "Transfer failed" message, hiding specific errors. | Log the specific exception and return a more descriptive error or status code. |
| Services/TransactionService.cs | 95 | `Deposit` catches all exceptions and returns a generic "Deposit failed" message. | Log the specific exception and return a more descriptive error or status code. |
| Controllers/AuthController.cs | 18 | `Login` returns `Unauthorized` for both invalid username and password, leaking existence of usernames. | Return a generic "Invalid credentials" message. |
| Services/AuthService.cs | 95 | `ValidateToken` catches all exceptions and returns false, hiding potential security issues. | Log the exception for debugging while maintaining security. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/EmailService.cs | 15 | `SmtpClient` is instantiated in the constructor but never disposed, holding socket resources. | Implement `IDisposable` and dispose `_smtpClient`. |
| Services/EmailService.cs | 35 | `MailMessage` is created but not disposed in `SendTransferNotification`. | Wrap `MailMessage` in a `using` statement. |
| Services/EmailService.cs | 52 | `MailMessage` is created but not disposed in `SendWelcomeEmail`. | Wrap `MailMessage` in a `using` statement. |
| Data/DatabaseHelper.cs | 25 | `SqlDataAdapter` and `DataTable` are created but not explicitly disposed, though `using` on connection/command helps. | Ensure `SqlDataAdapter` is disposed if it holds unmanaged resources. |
| Services/TransactionService.cs | 50 | `SqlTransaction` is used but not explicitly disposed in `Transfer` and `Deposit`. | Wrap `SqlTransaction` in a `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/TransactionService.cs | 58 | `Deposit` accesses `Rows[0]["Balance"]` without checking `Rows.Count > 0`. | Add a check for `Rows.Count > 0` before accessing. |
| Services/TransactionService.cs | 68 | `Transfer` accesses `fromUserTable.Rows[0]["Email"]` and `toUserTable.Rows[0]["Username"]` without null checks. | Ensure rows exist and columns are not null before casting. |
| Services/UserService.cs | 35 | `GetUserById` accesses `table.Rows[0]` without checking `Rows.Count > 0` (though checked earlier, it's fragile). | Ensure the check is robust and close to the access. |
| Services/AuthService.cs | 35 | `Login` casts `reader["Id"]`, `reader["Username"]`, etc., without checking for DBNull. | Use `reader.IsDBNull()` checks before casting. |
| Controllers/TransactionController.cs | 18 | `User.FindFirst(...)?.Value` is parsed as int, but `Value` could be null if claim exists but value is null. | Add null check before parsing. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/UserService.cs | 75 | `GetAuditReport` returns an empty string and is likely unused. | Remove or implement the audit report functionality. |
| Services/TransactionService.cs | 105 | `RefundTransaction` throws `NotImplementedException` and is not fully implemented. | Implement the refund logic or remove the endpoint if not needed. |
| Helpers/StringHelper.cs | 25 | `JoinWithSeparator` simply wraps `string.Join`, adding no value. | Remove and use `string.Join` directly. |
| Helpers/StringHelper.cs | 30 | `MaskAccountNumber` is defined but not used anywhere in the codebase. | Remove if unused or integrate into display logic. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/TransactionService.cs | 12 | `TransactionFeeRate` (0.01m) is hardcoded. | Move to configuration. |
| Services/TransactionService.cs | 13 | `MaxTransactionsPerDay` (10) is hardcoded. | Move to configuration. |
| Services/TransactionService.cs | 14 | `MaxDepositAmount` (1000000) is hardcoded. | Move to configuration. |
| Services/TransactionService.cs | 58 | Interest bonus rate (0.01m) is hardcoded in `Deposit`. | Move to configuration or constant. |
| Services/UserService.cs | 65 | `pageSize` limit (50) is hardcoded. | Move to configuration. |
| Services/UserService.cs | 22 | User ID upper bound (1000000) is hardcoded. | Move to configuration or remove. |
| Services/EmailService.cs | 10 | Email subjects are hardcoded. | Move to configuration or resource files. |
| Services/EmailService.cs | 12 | `MaxRetries` (3) is hardcoded. | Move to configuration. |
| Services/EmailService.cs | 13 | `SmtpTimeoutMs` (5000) is hardcoded. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Services/EmailService.cs | 15 | `SmtpClient` is not thread-safe and is held as an instance field. | Create new `SmtpClient` instances per send operation. |
| Data/DatabaseHelper.cs | 25 | `ExecuteQuerySafe` uses `AddWithValue` which can cause performance issues and type inference problems. | Use `Add` with explicit `SqlDbType`. |
| Services/AuthService.cs | 23 | SQL query is hardcoded in the service layer. | Use a repository pattern or ORM for better separation of concerns. |
| Services/TransactionService.cs | 45 | SQL queries are hardcoded in the service layer. | Use a repository pattern or ORM. |
| Services/UserService.cs | 28 | SQL queries are hardcoded in the service layer. | Use a repository pattern or ORM. |
| Helpers/StringHelper.cs | 20 | `Regex` is instantiated in a static field but not marked `static readonly` correctly in all contexts. | Ensure `RegexCache` is `static readonly`. |
| Controllers/UserController.cs | 42 | `UpdateUser` catches `ArgumentException` and returns `BadRequest`, mixing error handling with business logic. | Use model validation attributes or global exception handling. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 25 | `UseDeveloperExceptionPage()` is used in development, which is correct, but ensure it's not in production. | Verify environment checks are robust. |
| Program.cs | 38 | CORS policy is overly permissive (`AllowAnyOrigin`, `AllowAnyMethod`, `AllowAnyHeader`). | Restrict to specific origins and methods. |
| appsettings.Development.json | 1 | Hardcoded database credentials in development config. | Use environment variables or user secrets. |
| appsettings.json | 1 | Hardcoded placeholders for secrets in base config. | Ensure secrets are managed via environment variables or secure vaults. |
| SampleBankingApp.csproj | 10 | `TreatWarningsAsErrors` is false, allowing potential issues to be ignored. | Set to `true` to enforce code quality. |
| SampleBankingApp.csproj | 11 | `DebugSymbols` is false, which may hinder debugging in development. | Set to `true` for development builds. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create a test project with unit tests for services and controllers. |
| Services/TransactionService.cs | 20 | `Transfer` logic is complex and lacks tests for balance checks, fees, and transactions. | Write tests for successful transfer, insufficient funds, self-transfer, and fee calculation. |
| Services/TransactionService.cs | 50 | `Deposit` logic lacks tests for interest calculation and max amount validation. | Write tests for successful deposit, max amount exceeded, and interest bonus. |
| Services/AuthService.cs | 20 | `Login` logic lacks tests for valid/invalid credentials and JWT generation. | Write tests for successful login, failed login, and token generation. |
| Services/UserService.cs | 25 | `GetUserById` and `UpdateUser` lack tests for validation and database interaction. | Write tests for valid/invalid IDs, update success/failure, and pagination. |
| Controllers/AuthController.cs | 15 | `Login` endpoint lacks integration tests for HTTP responses. | Write integration tests for login success, failure, and token validation. |
| Controllers/TransactionController.cs | 15 | `Transfer` and `Deposit` endpoints lack integration tests for authorization and validation. | Write integration tests for unauthorized access, invalid inputs, and successful transactions. |