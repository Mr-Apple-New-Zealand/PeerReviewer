## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 28 | `ExecuteQuery` concatenates user input into SQL string, enabling SQL injection. | Use parameterized queries exclusively; remove or deprecate this method. |
| DatabaseHelper.cs | 16 | Hardcoded fallback credentials (`sa`/`Admin1234!`) in constructor. | Throw an exception if connection string is missing; never fallback to hardcoded secrets. |
| AuthService.cs | 48 | Passwords hashed with SHA-256 without salt, vulnerable to rainbow table attacks. | Use ASP.NET Core Identity or a dedicated library like BCrypt/Argon2. |
| AuthService.cs | 48 | Storing/verifying passwords in application logic rather than using a secure identity provider. | Integrate ASP.NET Core Identity for secure password handling. |
| TransactionController.cs | 53 | Refund endpoint lacks authorization checks, allowing any authenticated user to refund any transaction. | Add `[Authorize]` and validate ownership or admin role before processing. |
| UserController.cs | 46 | `UpdateUser` allows any authenticated user to update any user if they are not Admin, but logic is flawed (see Logic Errors). | Ensure strict ownership verification or admin-only updates. |
| UserController.cs | 78 | `DeleteUser` allows any Admin to delete any user without audit trail or soft-delete. | Implement soft-delete and log deletion attempts for auditability. |
| Program.cs | 23 | JWT secret key read directly from config without validation for empty/null in production. | Validate presence of secret key at startup; fail fast if missing. |
| Program.cs | 38 | CORS policy allows any method and header, which may be overly permissive. | Restrict allowed methods and headers to only those required. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 68 | `Transfer` checks balance against `amount + fee` but only deducts `fee` from sender and adds `amount` to receiver, losing the fee amount. | Ensure fee is deducted from sender and either added to receiver or removed from system correctly. |
| TransactionService.cs | 68 | Race condition: Balance check and update are not atomic; concurrent requests can lead to overdrafts. | Use database-level transactions with isolation levels or optimistic concurrency tokens. |
| TransactionService.cs | 108 | `Deposit` adds interest bonus to balance but does not record the interest amount separately in transaction log. | Record interest as a separate transaction or include it in the deposit description. |
| TransactionService.cs | 115 | `IsWithinDailyLimit` is defined but never called in `Transfer` or `Deposit`. | Integrate daily limit checks into transaction flow. |
| UserService.cs | 58 | `UpdateUser` does not validate if email/username already exists, allowing duplicates. | Add uniqueness checks before updating. |
| UserService.cs | 75 | `GetUsersPage` uses `OFFSET`/`FETCH` which can be slow on large tables; no total count returned for pagination. | Return total count for proper pagination UI; consider keyset pagination for performance. |
| AuthService.cs | 85 | `ValidateToken` only checks expiry, not signature or issuer, making it insecure. | Use `JwtSecurityTokenHandler.ValidateToken` for full validation. |
| TransactionController.cs | 25 | `Transfer` does not validate `request.ToUserId` or `request.Amount` for null/negative values. | Add model validation attributes or manual checks for request fields. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 53 | `Refund` catches `NotImplementedException` and returns 500, leaking implementation details. | Return 501 Not Implemented or handle gracefully without exposing stack traces. |
| UserController.cs | 58 | `UpdateUser` catches `Exception` and returns generic 500, potentially hiding specific errors. | Log detailed error internally; return generic message to client. |
| EmailService.cs | 48 | `SendTransferNotification` retries on `SmtpException` but does not handle network timeouts or other exceptions. | Catch broader exceptions or implement exponential backoff. |
| EmailService.cs | 72 | `SendWelcomeEmail` swallows `SmtpException` silently, losing error visibility. | Log the exception for monitoring and alerting. |
| TransactionService.cs | 75 | `Transfer` catches `Exception` in transaction block and re-throws, but does not log the error. | Log the exception before re-throwing for debugging. |
| DatabaseHelper.cs | 35 | `ExecuteQuerySafe` does not handle SQL exceptions, propagating raw errors to callers. | Wrap in try-catch and throw custom application exceptions. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 22 | `CreateConnection` returns `SqlConnection` without disposing; caller must manage disposal. | Use `using` statements or ensure callers dispose connections. |
| TransactionService.cs | 70 | `connection` opened in `Transfer` but not disposed if exception occurs before `using` block ends. | Ensure `using` statement covers entire transaction scope. |
| EmailService.cs | 35 | `SmtpClient` created per call; not thread-safe and may leak sockets if not disposed properly. | Use `using` statement for `SmtpClient` (already done, but verify no reuse). |
| DatabaseHelper.cs | 35 | `SqlDataAdapter` and `DataTable` not explicitly disposed; rely on GC. | Use `using` for `SqlDataAdapter` if possible; `DataTable` is not disposable. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 23 | `table.Rows[0]` accessed without checking `Rows.Count > 0` in `Login`. | Add null/empty check before accessing row. |
| TransactionService.cs | 62 | `fromUserTable.Rows[0]` accessed without checking count. | Add null/empty check before accessing row. |
| TransactionService.cs | 65 | `toUserTable.Rows[0]` accessed without checking count. | Add null/empty check before accessing row. |
| UserService.cs | 45 | `table.Rows[0]` accessed in `GetUserById` without checking count. | Add null/empty check before accessing row. |
| UserService.cs | 82 | `MapRowToUser` casts columns directly; may throw if column is null. | Use `DBNull.Value` checks or nullable casts. |
| Program.cs | 23 | `jwtSecret` used with `!` null-forgiving operator; may cause runtime error if null. | Validate `jwtSecret` is not null before use. |
| EmailService.cs | 35 | `_config["Email:SmtpHost"]` may be null, causing `SmtpClient` constructor to fail. | Validate config values before use. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 115 | `IsWithinDailyLimit` method is defined but never called. | Remove or integrate into transaction flow. |
| TransactionService.cs | 130 | `RecordTransaction` overload with connection/transaction is used, but the other overload is also present. | Ensure only necessary overloads are kept; remove unused ones. |
| StringHelper.cs | 28 | `JoinWithSeparator` duplicates `string.Join` functionality. | Remove redundant method. |
| AuthService.cs | 85 | `ValidateToken` is defined but not used anywhere. | Remove if unused or integrate into authentication flow. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 12 | `DefaultTransactionFeeRate` hardcoded; should be configurable. | Move to configuration file. |
| TransactionService.cs | 13 | `DefaultMaxTransactionsPerDay` hardcoded; should be configurable. | Move to configuration file. |
| TransactionService.cs | 14 | `MaxDepositAmount` hardcoded; should be configurable. | Move to configuration file. |
| TransactionService.cs | 15 | `DepositInterestRate` hardcoded; should be configurable. | Move to configuration file. |
| EmailService.cs | 12 | `TransferSubject` and `WelcomeSubject` hardcoded; should be configurable. | Move to configuration file. |
| EmailService.cs | 18 | `NotificationEmail` and `SupportEmail` hardcoded; should be configurable. | Move to configuration file. |
| UserService.cs | 10 | `MaxUserId` and `MaxPageSize` hardcoded; should be configurable. | Move to configuration file. |
| DatabaseHelper.cs | 16 | Fallback connection string contains hardcoded server/database names. | Remove fallback; require explicit configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 35 | `ExecuteQuerySafe` uses `AddWithValue` which can cause type inference issues. | Use `Add` with explicit `SqlDbType`. |
| TransactionService.cs | 70 | `using var transaction = connection.BeginTransaction()` does not dispose transaction on rollback. | Ensure transaction is disposed in `finally` block. |
| EmailService.cs | 48 | Retry logic uses `Console.WriteLine` instead of logging. | Use `ILogger` for production logging. |
| EmailService.cs | 72 | `Console.WriteLine` used for error logging. | Use `ILogger` for production logging. |
| UserService.cs | 58 | `UpdateUser` does not return success/failure status clearly; always returns true. | Return boolean based on actual update success. |
| TransactionService.cs | 130 | Duplicate `RecordTransaction` methods; one with transaction, one without. | Consolidate or clarify usage. |
| Program.cs | 10 | `DatabaseHelper` registered as Singleton; may hold state or connections improperly. | Ensure thread-safety or register as Scoped. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 45 | `UseDeveloperExceptionPage()` only in development, but no custom error page for production. | Add custom error handling for production. |
| Program.cs | 38 | CORS policy allows any method/header; may be too permissive. | Restrict to specific methods/headers. |
| appsettings.json | 1 | `AllowedHosts` set to `*`; may be too permissive for production. | Restrict to specific hosts in production. |
| SampleBankingApp.csproj | 10 | `TreatWarningsAsErrors` set to false; may hide potential issues. | Set to true for stricter compilation. |
| Program.cs | 23 | JWT secret key not validated for strength or length. | Validate secret key meets security requirements. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| All Services | - | No test project exists; critical business logic untested. | Create unit tests for `AuthService`, `TransactionService`, `UserService`. |
| TransactionService.cs | 68 | `Transfer` logic for fee calculation and balance updates needs testing. | Test fee deduction, balance updates, and transaction recording. |
| AuthService.cs | 48 | Password hashing and JWT generation need testing. | Test password hashing, token generation, and validation. |
| UserService.cs | 75 | Pagination logic needs testing. | Test page size limits, offset calculation, and result mapping. |
| DatabaseHelper.cs | 35 | SQL execution helpers need testing with mock data. | Mock database calls to test query execution and error handling. |