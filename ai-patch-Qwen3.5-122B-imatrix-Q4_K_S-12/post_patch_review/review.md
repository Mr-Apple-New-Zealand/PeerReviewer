## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `DatabaseHelper.cs` | 15 | Hardcoded fallback credentials (`sa`/`Admin1234!`) in constructor. | Remove hardcoded fallback or require explicit configuration. |
| `DatabaseHelper.cs` | 32 | `ExecuteQuery` concatenates raw `tableName` and `whereClause` into SQL string. | Use parameterized queries or strict allow-listing for table names. |
| `AuthService.cs` | 52 | Passwords hashed using MD5, which is cryptographically broken. | Use PBKDF2, bcrypt, or Argon2 for password hashing. |
| `AuthService.cs` | 52 | No salt is used in the MD5 hashing process. | Implement salted hashing algorithm. |
| `TransactionService.cs` | 48 | `Transfer` method lacks atomic database transaction wrapper for balance updates. | Wrap balance updates and transaction recording in a single DB transaction. |
| `UserController.cs` | 48 | `UpdateUser` allows any authenticated user to update any profile if ID matches claim, but logic is flawed (checks `int.Parse(userIdClaim) != id`). | Ensure ownership check is robust and prevents IDOR. |
| `UserController.cs` | 72 | `DeleteUser` allows non-admins to delete users if ID matches, but logic is inverted/weak. | Enforce strict role-based access control for deletion. |
| `Program.cs` | 38 | CORS policy allows `AllowAnyMethod()` and `AllowAnyHeader()`. | Restrict methods and headers to only those required. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `TransactionService.cs` | 48 | `Transfer` reads balances, then updates them separately without locking, risking race conditions. | Use database-level locking or transactions. |
| `TransactionService.cs` | 48 | `Transfer` calculates fee but does not deduct it from sender in the final balance update logic correctly (deducts `totalDebit` but adds only `amount` to receiver). | Ensure fee is accounted for in ledger (e.g., deducted from sender, not added to receiver). |
| `TransactionService.cs` | 78 | `Deposit` adds interest bonus to balance but records only original `amount` in transaction log. | Record the total credited amount or separate interest entry. |
| `UserService.cs` | 68 | `GetUsersPage` uses `OFFSET`/`FETCH` but does not handle pagination metadata (total count). | Return pagination metadata for client-side UI. |
| `UserController.cs` | 48 | `UpdateUser` ownership check fails if `userIdClaim` is null or parse fails, returning `Forbid` instead of `Unauthorized`. | Return `Unauthorized` if claim is missing/invalid. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `TransactionController.cs` | 45 | `Refund` catches `NotImplementedException` and returns 500, hiding implementation status. | Return 501 Not Implemented or 404 if feature is unavailable. |
| `TransactionService.cs` | 65 | `Transfer` catches broad `Exception` and rolls back, but swallows specific error details. | Log specific exception details internally. |
| `EmailService.cs` | 45 | `SendTransferNotification` retries on `SmtpException` but swallows other exceptions. | Handle or log non-SMTP exceptions appropriately. |
| `EmailService.cs` | 78 | `SendWelcomeEmail` swallows all exceptions silently. | Log errors for debugging and monitoring. |
| `UserService.cs` | 95 | `SearchUsers` catches `Exception` and returns empty list, masking errors. | Log the exception and return empty list or error status. |
| `UserController.cs` | 55 | `UpdateUser` returns `ex.Message` to client in `BadRequest`. | Return generic error message to avoid information leakage. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `DatabaseHelper.cs` | 22 | `GetOpenConnection` returns open connection without disposing, risking leaks if caller fails to dispose. | Document disposal requirement or use `using` in caller. |
| `DatabaseHelper.cs` | 32 | `ExecuteQuery` creates `SqlConnection` but does not dispose `SqlDataAdapter` or `DataTable` explicitly (though `using` on connection helps). | Ensure all `IDisposable` objects are disposed. |
| `AuthService.cs` | 35 | `Login` opens connection but does not dispose `SqlDataReader` explicitly (though `using` on command helps). | Ensure `SqlDataReader` is disposed. |
| `EmailService.cs` | 30 | `SmtpClient` is created inside method, which is correct, but `MailMessage` should be disposed. | Ensure `MailMessage` is disposed (it is, via `using`). |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `Program.cs` | 25 | `jwtSecret` from config is used without null check, passed to `GetBytes`. | Add null check or default value. |
| `AuthService.cs` | 65 | `secretKey` from config is checked, but `Issuer`/`Audience` are not. | Validate all JWT config values. |
| `TransactionService.cs` | 48 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0` in some paths (though checked earlier). | Ensure consistent checks before access. |
| `UserService.cs` | 45 | `MapRowToUser` casts `row["Id"]` etc. without null checks. | Add null checks for database columns. |
| `UserController.cs` | 48 | `User.FindFirst(...)?.Value` used, but `int.Parse` called on potentially null result. | Add null check before parsing. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `TransactionService.cs` | 98 | `RefundTransaction` throws `NotImplementedException`. | Implement or remove if not needed. |
| `StringHelper.cs` | 38 | `JoinWithSeparator` duplicates `string.Join`. | Remove redundant method. |
| `StringHelper.cs` | 52 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove redundant method. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `TransactionService.cs` | 48 | Fee rate `0.015` and interest rate `0.01` are hardcoded with fallbacks. | Move to configuration. |
| `UserService.cs` | 68 | Page size limit `50` is hardcoded. | Move to configuration. |
| `UserController.cs` | 72 | Role names `"Admin"` and `"SuperAdmin"` are hardcoded. | Move to configuration or constants. |
| `EmailService.cs` | 15 | Email subjects are hardcoded. | Move to configuration or resources. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `DatabaseHelper.cs` | 32 | `ExecuteQuery` uses string concatenation for SQL. | Use parameterized queries. |
| `TransactionService.cs` | 48 | `Transfer` uses multiple DB calls without transaction. | Use single transaction. |
| `UserService.cs` | 15 | `_auditLog` and `_requestCount` are mutable static-like state in scoped service. | Use thread-safe collections or remove if not needed. |
| `EmailService.cs` | 30 | `SmtpClient` is not thread-safe; creating new instance per call is okay but inefficient. | Consider connection pooling or async methods. |
| `Program.cs` | 38 | CORS policy is overly permissive. | Restrict origins, methods, headers. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `Program.cs` | 38 | CORS allows any method and header. | Restrict to specific methods/headers. |
| `appsettings.json` | 1 | Connection string placeholders `__SET_VIA_ENV__` may fail if not set. | Ensure environment variables are set or provide defaults. |
| `SampleBankingApp.csproj` | 10 | `DebugSymbols` and `DebugType` are disabled, hindering debugging. | Enable for development builds. |
| `SampleBankingApp.csproj` | 15 | `System.Data.SqlClient` is deprecated; use `Microsoft.Data.SqlClient`. | Update package reference. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `TransactionService.cs` | 48 | No tests for `Transfer` logic, including fee calculation and balance updates. | Add unit tests for transfer scenarios. |
| `AuthService.cs` | 35 | No tests for `Login` and JWT generation. | Add unit tests for authentication flow. |
| `UserService.cs` | 68 | No tests for pagination and search functionality. | Add unit tests for user retrieval. |
| `DatabaseHelper.cs` | 32 | No tests for SQL execution helpers. | Add integration tests for DB operations. |
| `EmailService.cs` | 30 | No tests for email sending logic. | Add unit tests with mocked SMTP client. |