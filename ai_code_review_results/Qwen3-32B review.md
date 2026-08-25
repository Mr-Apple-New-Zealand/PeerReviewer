# Peer Code Review Report

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection via string interpolation in query construction | Use parameterized queries instead of string interpolation |
| SampleBankingApp/Services/AuthService.cs | 61 | Hardcoded admin password `SuperAdmin2024` | Remove hardcoded credentials and use secure authentication mechanism |
| SampleBankingApp/Services/AuthService.cs | 61-65 | Weak MD5 hashing for passwords | Use stronger password hashing algorithm like bcrypt or Argon2 |
| SampleBankingApp/Services/TransactionService.cs | 47 | SQL injection via string interpolation in UPDATE statement | Use parameterized queries instead of string interpolation |
| SampleBankingApp/Services/TransactionService.cs | 90 | SQL injection via string interpolation in INSERT statement | Use parameterized queries instead of string interpolation |
| SampleBankingApp/Services/UserService.cs | 99-103 | SQL injection via `ExecuteQuery` with raw LIKE clause | Use parameterized queries instead of string interpolation |
| SampleBankingApp/Program.cs | 24 | JWT token lifetime validation disabled (`ValidateLifetime = false`) | Set `ValidateLifetime = true` for proper token expiration validation |
| SampleBankingApp/Services/AuthService.cs | 91-96 | Unused SHA1 hash implementation | Remove unused code or mark as obsolete |
| SampleBankingApp/Data/DatabaseHelper.cs | 28-34 | SQL injection via string interpolation in SELECT statement | Use parameterized queries instead of string interpolation |
| SampleBankingApp/Data/DatabaseHelper.cs | 52-56 | SQL injection via string interpolation in EXECUTE statement | Use parameterized queries instead of string interpolation |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 42 | Missing self-transfer check (user transferring to themselves) | Add validation to prevent self-transfers |
| SampleBankingApp/Services/TransactionService.cs | 68 | Incorrect interest rate calculation (5% instead of 1%) | Fix the interest bonus calculation to use 0.01m instead of 0.05m |
| SampleBankingApp/Services/TransactionService.cs | 70 | SQL injection in deposit amount calculation | Use parameterized queries instead of string interpolation |
| SampleBankingApp/Services/UserService.cs | 72 | Off-by-one error in pagination (page * pageSize vs (page-1)*pageSize) | Change `int skip = page * pageSize;` to `int skip = (page - 1) * pageSize;` |
| SampleBankingApp/Services/TransactionService.cs | 39 | Transaction fee calculation should be based on total amount including fee | The fee calculation is correct, but it's worth noting that the fee is applied on the transfer amount, not the total amount |
| SampleBankingApp/Services/TransactionService.cs | 40 | Fee is added to the amount being deducted from sender | This is correct as the fee should be paid by the sender |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/UserService.cs | 97-110 | Catches broad Exception and returns empty list | Differentiate between no results and errors, log exceptions properly |
| SampleBankingApp/Controllers/TransactionController.cs | 51-60 | Catches NotImplementedException but doesn't handle other exceptions | Add proper error handling for all possible exceptions |
| SampleBankingApp/Services/TransactionService.cs | 47 | No transaction scope for multiple database updates | Wrap related operations in a transaction scope |
| SampleBankingApp/Controllers/UserController.cs | 41-54 | Returns raw exception messages to clients | Use standardized error responses instead of exposing raw exception messages |
| SampleBankingApp/Services/AuthService.cs | 103-105 | Dead code that doesn't execute (always returns true) | Remove the dead code or implement proper token validation logic |
| SampleBankingApp/Controllers/UserController.cs | 46-53 | Missing rate limiting on update endpoint | Add rate limiting to prevent abuse of the API |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection` returns open connection without ensuring it's closed | Implement proper connection management with using statements |
| SampleBankingApp/Services/EmailService.cs | 16 | `SmtpClient` is instance field (not thread-safe) | Create SmtpClient on demand or use a thread-safe implementation |
| SampleBankingApp/Services/EmailService.cs | 39-44 | `MailMessage` not disposed after use | Use using statement to ensure proper disposal of MailMessage |
| SampleBankingApp/Services/TransactionService.cs | 28-30 | Connection opened but not properly disposed | Ensure connections are properly disposed after use |
| SampleBankingApp/Services/TransactionService.cs | 47 | No exception handling for database operations | Add proper error handling and ensure resources are released |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/TransactionController.cs | 26-27 | No null check for `User.FindFirst` result | Add null check before parsing the userIdClaim |
| SampleBankingApp/Services/TransactionService.cs | 36 | No null check for `fromUserTable.Rows[0]` | Check if table has rows before accessing Rows[0] |
| SampleBankingApp/Services/TransactionService.cs | 37-38 | No null checks for data access from DataRow | Add null checks for all data accesses from DataRow |
| SampleBankingApp/Services/TransactionService.cs | 53 | No null check for email conversion | Add null check before casting to string |
| SampleBankingApp/Controllers/AuthController.cs | 22 | No null check for _authService.Login result | Add null check for the returned user object |
| SampleBankingApp/Services/UserService.cs | 99-103 | No null checks when accessing query results | Add null checks for all data accesses from DataRow |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` is unused and inefficient | Remove or mark as obsolete |
| SampleBankingApp/Services/AuthService.cs | 91-96 | `HashPasswordSha1` is never called | Remove or mark as obsolete |
| SampleBankingApp/Services/EmailService.cs | 81-85 | `BuildHtmlTemplate` is unused | Remove or mark as obsolete |
| SampleBankingApp/Services/EmailService.cs | 86-92 | `SendWelcomeEmailHtml` is never called | Remove or mark as obsolete |
| SampleBankingApp/Data/DatabaseHelper.cs | 67-78 | `ExecuteQueryWithParams` marked obsolete but still exists | Remove the obsolete method |
| SampleBankingApp/Services/TransactionService.cs | 94-97 | `FormatCurrency` is unused | Remove or mark as obsolete |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 11 | Magic number `0.015m` for transaction fee rate | Create a named constant for the transaction fee rate |
| SampleBankingApp/Services/TransactionService.cs | 12 | Magic number `10` for max transactions per day | Create a named constant for the daily transaction limit |
| SampleBankingApp/Services/UserService.cs | 70 | Magic number `50` for page size limit | Create a named constant for the maximum page size |
| SampleBankingApp/Services/TransactionService.cs | 68 | Magic number `0.05m` for interest rate | Create a named constant for the interest rate |
| SampleBankingApp/Models/User.cs | 7-13 | Hardcoded role names in User class | Consider using an enum or configuration for roles |
| SampleBankingApp/Services/AuthService.cs | 61 | Hardcoded "SuperAdmin" role name | Use a configuration value instead of hardcoding |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 31-35 | String concatenation in loop (O(n²)) | Replace with `string.Join` or `StringBuilder` |
| SampleBankingApp/Data/DatabaseHelper.cs | 26 | Repeated query execution logic | Extract common query execution to a helper method |
| SampleBankingApp/Services/UserService.cs | 89-91 | String concatenation for audit report | Use `StringBuilder` for better performance |
| SampleBankingApp/Services/TransactionService.cs | 47, 48 | Multiple responsibilities in Transfer method | Split into validation, database update, and notification methods |
| SampleBankingApp/Services/UserService.cs | 10-16 | Shared mutable static state `_auditLog` and `_requestCount` | Replace with thread-safe alternatives or use dependency injection |
| SampleBankingApp/Services/TransactionService.cs | 23-61 | Transfer method has multiple responsibilities | Split into validation, database update, and notification methods |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` called unconditionally | Wrap in `if (app.Environment.IsDevelopment())` block |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out | Uncomment and configure HTTPS redirection |
| SampleBankingApp/Program.cs | 38 | Overly permissive CORS policy | Restrict origins, methods, and headers appropriately |
| SampleBankingApp/Services/AuthService.cs | 70-89 | JWT secret key from configuration without fallback | Add proper error handling for missing configuration values |
| SampleBankingApp/appsettings.json | 16-21 | Debug log levels set for production | Set appropriate log levels for production environment |
| SampleBankingApp/SampleBankingApp.csproj | N/A | Missing environment-specific config overrides | Add `appsettings.Production.json` and other environment-specific files |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---|---|---|
| N/A | N/A | No test project found | Create a test project with tests for: | Create a test project |
| N/A | N/A | Boundary conditions in pagination (UserService.GetUsersPage) | Test edge cases like page=0, large page sizes | Add unit tests |
| N/A | N/A | Authentication flow (AuthController.Login) | Test successful login, invalid credentials, etc. | Add unit tests |
| N/A | N/A | Financial calculations (TransactionService.Transfer, Deposit) | Test various amounts, fees, and edge cases | Add unit tests |
| N/A | N/A | Authorization in controllers | Verify that unauthorized access is properly handled | Add integration tests |
| N/A | N/A | Error handling scenarios | Test error paths and ensure proper responses | Add unit tests |
| N/A | N/A | String validation helpers (StringHelper.IsValidEmail, etc.) | Test various valid/invalid inputs | Add unit tests |
| N/A | N/A | Database operations | Test CRUD operations and edge cases | Add integration tests |