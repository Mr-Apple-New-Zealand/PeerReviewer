## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 28 | Hardcoded database credentials in fallback connection string. | Remove hardcoded credentials; fail fast if config is missing. |
| AuthService.cs | 48 | Passwords hashed using MD5, which is cryptographically broken. | Use a strong hashing algorithm like PBKDF2, BCrypt, or Argon2. |
| AuthService.cs | 48 | Passwords stored/hashed without a salt. | Implement salting for all password hashing operations. |
| TransactionController.cs | 43 | Refund endpoint lacks authorization checks, allowing any authenticated user to trigger refunds. | Add `[Authorize]` with specific role requirements or ownership validation. |
| UserController.cs | 68 | `SearchUsers` endpoint lacks authorization, exposing user data to unauthenticated users. | Add `[Authorize]` attribute to the controller or specific action. |
| UserController.cs | 74 | `GetAuditLog` endpoint lacks authorization, exposing internal audit data. | Add `[Authorize(Roles = "Admin")]` to restrict access. |
| Program.cs | 38 | JWT secret key retrieved via indexer without null check, risking runtime exception if missing. | Validate configuration presence during startup or use `GetRequiredValue`. |
| EmailService.cs | 33 | SMTP credentials retrieved from config without validation; potential for empty/null credentials. | Validate SMTP credentials are present and non-empty before use. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 58 | Transaction fee is deducted from sender but not added to receiver or bank, creating money loss. | Clarify fee handling; either add fee to receiver, bank account, or document loss. |
| TransactionService.cs | 58 | `totalDebit` calculation includes fee, but receiver only gets `amount`, causing imbalance. | Ensure accounting logic balances debits and credits including fees. |
| TransactionService.cs | 82 | Email notification sent outside transaction scope; failure does not rollback DB changes. | Move email sending to background job or accept eventual consistency; do not tie to DB transaction. |
| UserService.cs | 68 | `GetUsersPage` uses `OFFSET`/`FETCH` but does not handle empty result sets gracefully in caller. | Ensure callers handle empty lists; verify pagination logic for edge cases (page=0). |
| UserService.cs | 22 | `ValidateUserId` throws exception for `id > 1000000`, which is an arbitrary business limit. | Remove arbitrary limit or make it configurable; validate against actual DB constraints. |
| TransactionController.cs | 16 | `int.Parse` on `userIdClaim` can throw if claim is not a valid integer. | Use `int.TryParse` and return `BadRequest` if parsing fails. |
| TransactionController.cs | 28 | `int.Parse` on `userIdClaim` can throw if claim is not a valid integer. | Use `int.TryParse` and return `BadRequest` if parsing fails. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 45 | Catches `NotImplementedException` specifically, exposing internal implementation details. | Catch general `Exception` or return `501 Not Implemented` without revealing internals. |
| UserController.cs | 62 | Catches broad `Exception` and returns generic 500 error, hiding specific errors from logs. | Log the exception details and return a generic error message to client. |
| UserService.cs | 85 | Catches `Exception` in `SearchUsers` and returns empty list, masking errors from caller. | Log the exception and rethrow or return a structured error response. |
| EmailService.cs | 48 | Catches `SmtpException` and retries, but swallows other exceptions silently. | Catch specific exceptions and log all failures appropriately. |
| EmailService.cs | 75 | Catches `Exception` in `SendWelcomeEmail` and prints to console, losing error context. | Use proper logging framework instead of `Console.WriteLine`. |
| TransactionService.cs | 88 | Catches `Exception` in transfer logic and rolls back, but does not log the error. | Log the exception before rolling back for debugging purposes. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 25 | `GetOpenConnection` returns an open `SqlConnection` without disposing it. | Use `using` statements or ensure callers dispose the connection. |
| DatabaseHelper.cs | 33 | `ExecuteQuery` opens a connection but does not dispose it or the `SqlCommand`. | Wrap `SqlConnection` and `SqlCommand` in `using` blocks. |
| DatabaseHelper.cs | 58 | `ExecuteNonQuery` opens a connection but does not dispose it or the `SqlCommand`. | Wrap `SqlConnection` and `SqlCommand` in `using` blocks. |
| DatabaseHelper.cs | 75 | `TableExists` opens a connection but does not dispose it. | Wrap `SqlConnection` in a `using` block. |
| AuthService.cs | 35 | `SqlConnection` opened but not disposed if `reader.Read()` fails or throws. | Wrap `SqlConnection` in a `using` block. |
| TransactionService.cs | 65 | `GetOpenConnection()` used to begin transaction; connection not disposed if exception occurs. | Ensure connection is disposed in `finally` block or use `using`. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 16 | `userIdClaim` could be null, causing `int.Parse` to throw. | Add null check before parsing. |
| TransactionController.cs | 28 | `userIdClaim` could be null, causing `int.Parse` to throw. | Add null check before parsing. |
| UserController.cs | 55 | `userIdClaim` could be null, causing `int.Parse` to throw. | Add null check before parsing. |
| UserController.cs | 68 | `query` parameter could be null, causing issues in `SearchUsers`. | Add null check or default value for `query`. |
| AuthService.cs | 35 | `reader["Id"]` could throw if column is null or missing. | Check for `DBNull` before casting. |
| AuthService.cs | 36 | `reader["Username"]` could throw if column is null or missing. | Check for `DBNull` before casting. |
| AuthService.cs | 37 | `reader["Email"]` could throw if column is null or missing. | Check for `DBNull` before casting. |
| AuthService.cs | 38 | `reader["Role"]` could throw if column is null or missing. | Check for `DBNull` before casting. |
| AuthService.cs | 39 | `reader["Balance"]` could throw if column is null or missing. | Check for `DBNull` before casting. |
| AuthService.cs | 40 | `reader["IsActive"]` could throw if column is null or missing. | Check for `DBNull` before casting. |
| UserService.cs | 38 | `row["Id"]` could throw if column is null or missing. | Check for `DBNull` before casting. |
| UserService.cs | 39 | `row["Username"]` could throw if column is null or missing. | Check for `DBNull` before casting. |
| UserService.cs | 40 | `row["Email"]` could throw if column is null or missing. | Check for `DBNull` before casting. |
| UserService.cs | 41 | `row["Role"]` could throw if column is null or missing. | Check for `DBNull` before casting. |
| UserService.cs | 42 | `row["Balance"]` could throw if column is null or missing. | Check for `DBNull` before casting. |
| UserService.cs | 43 | `row["IsActive"]` could throw if column is null or missing. | Check for `DBNull` before casting. |
| UserService.cs | 44 | `row["CreatedAt"]` could throw if column is null or missing. | Check for `DBNull` before casting. |
| TransactionService.cs | 52 | `fromUserTable.Rows[0]["Balance"]` could throw if column is null. | Check for `DBNull` before casting. |
| TransactionService.cs | 53 | `toUserTable.Rows[0]["Balance"]` could throw if column is null. | Check for `DBNull` before casting. |
| TransactionService.cs | 82 | `fromUserTable.Rows[0]["Email"]` could throw if column is null. | Check for `DBNull` before casting. |
| TransactionService.cs | 83 | `toUserTable.Rows[0]["Username"]` could throw if column is null. | Check for `DBNull` before casting. |
| EmailService.cs | 33 | `_config["Email:SmtpHost"]` could be null, causing `SmtpClient` constructor to throw. | Add null check or default value. |
| EmailService.cs | 35 | `_config["Email:SmtpPort"]` could be null, causing `int.Parse` to throw. | Add null check or default value. |
| EmailService.cs | 36 | `_config["Email:Username"]` could be null, causing `NetworkCredential` to throw. | Add null check. |
| EmailService.cs | 37 | `_config["Email:Password"]` could be null, causing `NetworkCredential` to throw. | Add null check. |
| EmailService.cs | 68 | `_config["Email:SmtpHost"]` could be null, causing `SmtpClient` constructor to throw. | Add null check or default value. |
| EmailService.cs | 70 | `_config["Email:SmtpPort"]` could be null, causing `int.Parse` to throw. | Add null check or default value. |
| EmailService.cs | 71 | `_config["Email:Username"]` could be null, causing `NetworkCredential` to throw. | Add null check. |
| EmailService.cs | 72 | `_config["Email:Password"]` could be null, causing `NetworkCredential` to throw. | Add null check. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| StringHelper.cs | 45 | `JoinWithSeparator` duplicates `string.Join` functionality. | Remove method; use `string.Join` directly. |
| StringHelper.cs | 63 | `IsBlank` duplicates `string.IsNullOrWhiteSpace` functionality. | Remove method; use `string.IsNullOrWhiteSpace` directly. |
| TransactionService.cs | 95 | `RefundTransaction` throws `NotImplementedException` and is not fully implemented. | Implement the method or remove it if not needed. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 28 | Hardcoded connection string fallback. | Remove fallback; require configuration. |
| AuthService.cs | 35 | Hardcoded SQL query string. | Extract to constant or configuration. |
| TransactionService.cs | 48 | Hardcoded SQL query string. | Extract to constant or configuration. |
| TransactionService.cs | 51 | Hardcoded SQL query string. | Extract to constant or configuration. |
| TransactionService.cs | 68 | Hardcoded SQL query string. | Extract to constant or configuration. |
| TransactionService.cs | 73 | Hardcoded SQL query string. | Extract to constant or configuration. |
| TransactionService.cs | 90 | Hardcoded SQL query string. | Extract to constant or configuration. |
| UserService.cs | 32 | Hardcoded SQL query string. | Extract to constant or configuration. |
| UserService.cs | 48 | Hardcoded SQL query string. | Extract to constant or configuration. |
| UserService.cs | 58 | Hardcoded SQL query string. | Extract to constant or configuration. |
| UserService.cs | 68 | Hardcoded SQL query string. | Extract to constant or configuration. |
| UserService.cs | 82 | Hardcoded SQL query string. | Extract to constant or configuration. |
| UserController.cs | 68 | Hardcoded role names "Admin" and "SuperAdmin". | Extract to constants or configuration. |
| EmailService.cs | 12 | Hardcoded email subject strings. | Extract to constants or configuration. |
| EmailService.cs | 28 | Hardcoded email body text. | Extract to constants or configuration. |
| EmailService.cs | 62 | Hardcoded email body text. | Extract to constants or configuration. |
| TransactionService.cs | 12 | Hardcoded transaction fee rate. | Extract to configuration. |
| TransactionService.cs | 13 | Hardcoded max transactions per day. | Extract to configuration. |
| TransactionService.cs | 14 | Hardcoded max deposit amount. | Extract to configuration. |
| TransactionService.cs | 15 | Hardcoded deposit interest rate. | Extract to configuration. |
| UserService.cs | 66 | Hardcoded page size limit of 50. | Extract to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserService.cs | 75 | String concatenation in loop for audit report. | Use `StringBuilder` or `string.Join`. |
| UserService.cs | 10 | Static mutable state `_auditLog` and `_requestCount` shared across instances. | Remove static state; use instance variables or external storage. |
| DatabaseHelper.cs | 33 | `ExecuteQuery` uses string interpolation for SQL, risking injection. | Use parameterized queries exclusively. |
| TransactionService.cs | 90 | String interpolation for SQL, risking injection. | Use parameterized queries exclusively. |
| AuthService.cs | 35 | String interpolation for SQL, risking injection. | Use parameterized queries exclusively. |
| EmailService.cs | 48 | Console logging used instead of proper logging framework. | Use `ILogger` for logging. |
| EmailService.cs | 75 | Console logging used instead of proper logging framework. | Use `ILogger` for logging. |
| TransactionController.cs | 45 | Specific exception handling for `NotImplementedException`. | Handle generally or remove if not needed. |
| UserController.cs | 62 | Broad exception handling without logging. | Log exceptions before returning generic error. |
| UserService.cs | 85 | Broad exception handling without logging. | Log exceptions before returning empty list. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 38 | JWT secret key retrieved without validation. | Validate configuration presence during startup. |
| Program.cs | 48 | CORS policy allows any method and header for specific origin. | Restrict methods and headers to necessary ones. |
| SampleBankingApp.csproj | 10 | `TreatWarningsAsErrors` set to false. | Set to true to enforce code quality. |
| SampleBankingApp.csproj | 11 | `DebugSymbols` and `DebugType` set for release builds. | Remove or conditionally set for debug builds only. |
| SampleBankingApp.csproj | 15 | `Newtonsoft.Json` version 12.0.3 is outdated. | Update to latest stable version. |
| appsettings.json | 3 | Hardcoded connection string with placeholder password. | Use environment variables for sensitive data. |
| appsettings.json | 7 | Hardcoded JWT secret key placeholder. | Use environment variables for sensitive data. |
| appsettings.json | 12 | Hardcoded SMTP credentials placeholder. | Use environment variables for sensitive data. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create unit tests for all services and controllers. |
| AuthService.cs | 25 | Login logic not tested. | Test login with valid/invalid credentials. |
| AuthService.cs | 48 | Password hashing not tested. | Test MD5 hashing (though it should be replaced). |
| AuthService.cs | 55 | JWT token generation not tested. | Test token generation and validation. |
| TransactionService.cs | 45 | Transfer logic not tested. | Test transfer with sufficient/insufficient funds. |
| TransactionService.cs | 85 | Deposit logic not tested. | Test deposit with valid/invalid amounts. |
| UserService.cs | 25 | User retrieval not tested. | Test getting user by ID. |
| UserService.cs | 45 | User update not tested. | Test updating user details. |
| UserService.cs | 55 | User deletion not tested. | Test deleting a user. |
| UserService.cs | 65 | Pagination not tested. | Test pagination with various page sizes. |
| UserService.cs | 80 | Search functionality not tested. | Test search with various queries. |