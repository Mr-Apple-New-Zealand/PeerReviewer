## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 12 | Hardcoded fallback credentials (`sa`/`Admin1234!`) in source code. | Remove hardcoded credentials; fail fast if config is missing. |
| DatabaseHelper.cs | 28 | `ExecuteQuery` concatenates raw `whereClause` into SQL string, enabling SQL injection. | Remove this method or enforce parameterized queries only. |
| AuthService.cs | 43 | Passwords hashed using MD5, which is cryptographically broken and unsalted. | Use `BCrypt`, `Argon2`, or `PBKDF2` with salt. |
| AuthService.cs | 43 | Passwords stored/hashed in plaintext-equivalent format without salt. | Implement proper salting and hashing algorithm. |
| TransactionController.cs | 38 | `Refund` endpoint lacks authorization check for ownership or admin role. | Add `[Authorize]` and verify user owns transaction or is Admin. |
| UserController.cs | 68 | `GetAuditLog` exposes internal audit data to any authenticated user. | Restrict access to Admin role only. |
| Program.cs | 38 | JWT secret key read from config without validation; could be empty/weak. | Validate secret length and complexity at startup. |
| Program.cs | 53 | CORS policy allows credentials with specific origin but `AllowAnyMethod/Header` is broad. | Restrict allowed methods and headers to minimum required. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 58 | `RecordTransaction` called inside transaction but `ExecuteNonQuery` doesn't accept transaction param in overload used. | Ensure `ExecuteNonQuery` overload accepts and uses the `SqlTransaction`. |
| TransactionService.cs | 58 | Email sent inside database transaction; if email fails, transaction rolls back, losing financial record. | Move email sending to after `transaction.Commit()` or use outbox pattern. |
| TransactionService.cs | 82 | Deposit interest calculation `amount * 0.01m * 1` is redundant and potentially confusing. | Simplify to `amount * 0.01m` or clarify intent. |
| TransactionService.cs | 82 | Deposit adds interest bonus to balance but doesn't record interest separately in transaction log. | Log interest as separate transaction or include in description. |
| UserService.cs | 76 | `SearchUsers` catches all exceptions and returns empty list, hiding errors. | Log exception and return error status or specific error message. |
| UserService.cs | 92 | `ValidateUserId` rejects IDs > 1,000,000 arbitrarily, potentially blocking valid users. | Remove arbitrary upper limit or increase significantly. |
| TransactionController.cs | 15 | `int.Parse` on `userIdClaim` can throw if claim is missing or non-numeric. | Use `int.TryParse` and return `Unauthorized` if invalid. |
| UserController.cs | 38 | `UpdateUser` checks `callerId != id` but doesn't check if user is Admin. | Allow Admins to update any user profile. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 38 | `Refund` catches `NotImplementedException` and returns 500, exposing internal state. | Return 501 Not Implemented or 404 if feature unavailable. |
| UserController.cs | 52 | `UpdateUser` returns `ex.Message` to client, leaking internal details. | Return generic error message; log full exception. |
| EmailService.cs | 48 | `SendWelcomeEmail` catches `Exception` and prints to console, swallowing errors. | Log error properly and consider failing fast or retrying. |
| EmailService.cs | 35 | `SendTransferNotification` retries on `SmtpException` but doesn't handle other exceptions. | Catch broader exceptions or handle network errors specifically. |
| AuthService.cs | 78 | `ValidateToken` catches all exceptions and returns false, hiding validation errors. | Log exceptions and distinguish between invalid token and system error. |
| TransactionService.cs | 58 | `Transfer` catches all exceptions in transaction block, rolls back, then re-throws. | Ensure specific exceptions are handled; avoid swallowing stack traces. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 22 | `GetOpenConnection` returns open connection; caller must dispose, risking leaks. | Return `SqlConnection` in `using` block or use `IDbConnection` factory. |
| TransactionService.cs | 58 | `GetOpenConnection().BeginTransaction()` creates transaction; connection not disposed if exception occurs before `using`. | Wrap connection creation in `using` block. |
| DatabaseHelper.cs | 28 | `ExecuteQuery` creates `SqlConnection` but doesn't dispose if exception occurs during `Open()`. | Use `using` statement for connection. |
| EmailService.cs | 28 | `SmtpClient` created per call; not disposed if exception occurs before `Send()`. | Wrap `SmtpClient` in `using` block. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 15 | `User.FindFirst(...)?.Value` can be null; `int.Parse` throws `ArgumentNullException`. | Add null check before parsing. |
| UserController.cs | 38 | `User.FindFirst(...)?.Value` can be null; `int.Parse` throws `ArgumentNullException`. | Add null check before parsing. |
| AuthService.cs | 68 | `_config["Jwt:SecretKey"]` can be null; `GetBytes` throws if null. | Add null check or use `??` with default. |
| EmailService.cs | 28 | `_config["Email:SmtpHost"]` can be null; `SmtpClient` constructor may fail. | Add null check or default value. |
| TransactionService.cs | 58 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0` in some paths. | Ensure row exists before accessing. |
| UserService.cs | 76 | `SearchUsers` returns empty list on exception; caller may assume no results. | Return error status or log exception. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 68 | `ExecuteQueryWithParams` marked `[Obsolete]` but still present. | Remove obsolete method. |
| StringHelper.cs | 28 | `JoinWithSeparator` duplicates `string.Join`. | Remove method; use `string.Join` directly. |
| TransactionService.cs | 98 | `RefundTransaction` throws `NotImplementedException`. | Implement or remove stub. |
| AuthService.cs | 78 | `ValidateToken` method defined but never called. | Remove if unused or integrate into auth flow. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 12 | `TransactionFeeRate` (0.015m) hardcoded. | Move to configuration. |
| TransactionService.cs | 13 | `MaxTransactionsPerDay` (10) hardcoded. | Move to configuration. |
| TransactionService.cs | 14 | `DepositCap` (1,000,000) hardcoded. | Move to configuration. |
| UserService.cs | 92 | `ValidateUserId` upper limit (1,000,000) hardcoded. | Move to configuration or remove. |
| EmailService.cs | 12 | Email subjects hardcoded. | Move to configuration or resource file. |
| EmailService.cs | 15 | `MaxRetries` (3) hardcoded. | Move to configuration. |
| EmailService.cs | 16 | `SmtpTimeoutMs` (5000) hardcoded. | Move to configuration. |
| Program.cs | 53 | CORS origin `"https://bankingapp.com"` hardcoded. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| StringHelper.cs | 15 | `new Regex(...)` created per call; should be static readonly. | Cache regex as static readonly field. |
| StringHelper.cs | 22 | `new Regex(...)` created per call; should be static readonly. | Cache regex as static readonly field. |
| UserService.cs | 12 | `_auditLog` and `_requestCount` are static mutable state; thread-unsafe. | Use thread-safe collections or remove static state. |
| UserService.cs | 82 | String concatenation in loop for audit report. | Use `StringBuilder` or `string.Join`. |
| DatabaseHelper.cs | 28 | `ExecuteQuery` uses string interpolation for SQL. | Use parameterized queries only. |
| TransactionService.cs | 58 | Transaction logic mixed with business logic; hard to test. | Separate transaction management from business logic. |
| AuthService.cs | 43 | MD5 hashing used for passwords; insecure. | Use secure hashing algorithm. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 38 | JWT secret key not validated for strength. | Validate secret length and complexity. |
| Program.cs | 53 | CORS policy allows any method/header with credentials. | Restrict methods and headers. |
| appsettings.json | 1 | Connection string contains placeholder `__SET_VIA_ENV__`. | Ensure environment variables are set; fail if missing. |
| appsettings.json | 1 | Email password contains placeholder `__SET_VIA_ENV__`. | Ensure environment variables are set; fail if missing. |
| SampleBankingApp.csproj | 8 | `DebugSymbols` and `DebugType` set to false in development. | Enable debug symbols for development builds. |
| Program.cs | 45 | `UseDeveloperExceptionPage()` only in development; good practice. | No issue. |
| Program.cs | 50 | `UseExceptionHandler("/error")` in production; ensure endpoint exists. | Verify `/error` endpoint is implemented. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create test project with unit tests. |
| TransactionService.cs | 28 | `Transfer` method lacks tests for balance checks, fees, and transactions. | Add tests for successful/failed transfers, insufficient funds, self-transfer. |
| TransactionService.cs | 78 | `Deposit` method lacks tests for cap and interest calculation. | Add tests for deposit limits and interest bonus. |
| AuthService.cs | 28 | `Login` method lacks tests for valid/invalid credentials. | Add tests for login success/failure. |
| UserService.cs | 28 | `GetUsersPage` lacks tests for pagination boundaries. | Add tests for page size limits and offset calculation. |
| UserService.cs | 76 | `SearchUsers` lacks tests for SQL injection prevention. | Add tests for query sanitization. |
| DatabaseHelper.cs | 28 | `ExecuteQuery` lacks tests for SQL injection vulnerability. | Add tests to verify parameterized queries only. |
| EmailService.cs | 28 | `SendTransferNotification` lacks tests for retry logic. | Add tests for retry behavior on failure. |