## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 14 | Hardcoded fallback database credentials in source code. | Remove the fallback string and throw if configuration is missing. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | SQL injection vulnerability in `ExecuteQuery` via interpolated table and where clause. | Use parameterized queries or an ORM instead of raw string interpolation. |
| SampleBankingApp/Data/DatabaseHelper.cs | 40 | SQL injection vulnerability in `ExecuteNonQuery` accepting raw SQL. | Remove this method or enforce parameterized commands. |
| SampleBankingApp/Services/AuthService.cs | 30 | Hardcoded backdoor admin password. | Remove the backdoor immediately. |
| SampleBankingApp/Services/AuthService.cs | 34 | SQL injection vulnerability in `Login` method via interpolated username and password. | Use parameterized queries for the authentication lookup. |
| SampleBankingApp/Services/AuthService.cs | 50 | Weak cryptography using MD5 for password hashing without salt. | Use a strong hashing algorithm like Argon2 or PBKDF2 with a salt. |
| SampleBankingApp/Services/TransactionService.cs | 41 | SQL injection in `Transfer` via interpolated balance and user ID. | Use parameterized queries for the UPDATE statements. |
| SampleBankingApp/Services/TransactionService.cs | 64 | SQL injection in `Deposit` via interpolated amount. | Use parameterized queries for the UPDATE statement. |
| SampleBankingApp/Services/TransactionService.cs | 86 | SQL injection in `RecordTransaction` via interpolated values. | Use parameterized queries for the INSERT statement. |
| SampleBankingApp/Services/UserService.cs | 31 | SQL injection in `UpdateUser` via interpolated email and username. | Use parameterized queries for the UPDATE statement. |
| SampleBankingApp/Services/UserService.cs | 43 | SQL injection in `DeleteUser` via interpolated ID. | Use parameterized queries for the DELETE statement. |
| SampleBankingApp/Services/UserService.cs | 83 | SQL injection in `SearchUsers` via interpolated query string. | Use parameterized queries for the LIKE clause. |
| SampleBankingApp/Controllers/UserController.cs | 34 | Broken access control allowing any user to update any other user. | Add ownership or role checks before updating. |
| SampleBankingApp/Controllers/UserController.cs | 49 | Broken access control allowing any user to delete any other user. | Add authorization checks and restrict to admins. |
| SampleBankingApp/Program.cs | 19 | JWT `ValidateLifetime` set to false. | Set `ValidateLifetime` to true. |
| SampleBankingApp/Program.cs | 27 | Developer exception page enabled unconditionally. | Only enable developer exception page in development environment. |
| SampleBankingApp/Program.cs | 29 | Open CORS policy allowing any origin, method, and header. | Restrict CORS to known origins and required methods. |
| SampleBankingApp/Program.cs | 31 | HTTPS redirection is commented out. | Uncomment `app.UseHttpsRedirection()`. |
| SampleBankingApp/appsettings.json | 3 | Production database credentials committed to source control. | Use environment variables or user secrets for credentials. |
| SampleBankingApp/appsettings.json | 7 | Weak JWT secret key committed to source control. | Use a strong, randomly generated secret stored securely. |
| SampleBankingApp/appsettings.json | 13 | SMTP credentials committed to source control. | Use environment variables or secret managers for SMTP credentials. |
| SampleBankingApp/SampleBankingApp.csproj | 9 | Debug symbols set to full for release builds. | Set `DebugType` to `none` or `portable` for release. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 38 | Balance check excludes the transaction fee, allowing negative balances. | Change condition to `if (fromBalance >= totalDebit)`. |
| SampleBankingApp/Services/TransactionService.cs | 23 | Missing self-referential check allows transferring to yourself. | Add a check to ensure `fromUserId != toUserId`. |
| SampleBankingApp/Services/TransactionService.cs | 61 | Deposit applies a 5% interest bonus which is likely unintended. | Remove the interest bonus calculation. |
| SampleBankingApp/Services/UserService.cs | 56 | Pagination off-by-one error skips the first page. | Change `int skip = page * pageSize;` to `(page - 1) * pageSize`. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 33 | Transfer lacks a database transaction, risking inconsistent balances. | Wrap the balance updates and transaction record in a SQL transaction. |
| SampleBankingApp/Services/TransactionService.cs | 48 | Email sending side effect occurs after DB writes and can throw unhandled. | Wrap email sending in a try-catch or use an outbox pattern. |
| SampleBankingApp/Services/UserService.cs | 79 | `SearchUsers` catches broad `Exception` and returns empty list, hiding errors. | Let the exception propagate or log it before returning an empty list. |
| SampleBankingApp/Controllers/UserController.cs | 38 | `UpdateUser` catches broad `Exception` and returns raw `ex.Message` to client. | Log the exception and return a generic error message. |
| SampleBankingApp/Controllers/AuthController.cs | 21 | Missing rate limiting or account lockout on login endpoint. | Implement rate limiting and account lockout policies. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 34 | `SqlConnection` and `SqlCommand` in `Login` are never disposed. | Wrap connection and command in `using` statements. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | `ExecuteQuery` leaks `SqlConnection` and `SqlCommand` resources. | Use `using` statements for connection and command. |
| SampleBankingApp/Data/DatabaseHelper.cs | 40 | `ExecuteNonQuery` leaks `SqlConnection` and `SqlCommand` resources. | Use `using` statements for connection and command. |
| SampleBankingApp/Services/EmailService.cs | 33 | `MailMessage` objects are never disposed. | Wrap `MailMessage` in a `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 16 | `SmtpClient` is held as an instance field and never disposed. | Create and dispose `SmtpClient` per use or implement `IDisposable`. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 21 | `jwtSecret` is passed to `Encoding.UTF8.GetBytes` with a null-forgiving operator but could be null. | Check for null and throw if configuration is missing. |
| SampleBankingApp/Controllers/TransactionController.cs | 21 | `int.Parse(userIdClaim!)` will throw if the claim is missing. | Check if `userIdClaim` is null before parsing. |
| SampleBankingApp/Services/TransactionService.cs | 29 | `fromUserTable.Rows[0]` is accessed without checking if rows exist. | Check `Rows.Count > 0` before accessing the first row. |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | `IsValidEmail` calls `.Length` on parameter without null check. | Add a null check at the beginning of the method. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | `IsValidUsername` calls `.Length` on parameter without null check. | Add a null check at the beginning of the method. |
| SampleBankingApp/Services/EmailService.cs | 14 | `_config["Email:SmtpHost"]` could be null and passed to `SmtpClient` constructor. | Validate configuration values before using them. |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 66 | `HashPasswordSha1` is never called. | Remove the method. |
| SampleBankingApp/Services/AuthService.cs | 71 | Unreachable code after unconditional `return true;` in `ValidateToken`. | Remove the unreachable code or fix the logic. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `JoinWithSeparator` is broken and duplicated by `JoinWithSeparatorFixed`. | Remove `JoinWithSeparator`. |
| SampleBankingApp/Services/TransactionService.cs | 94 | `FormatCurrency` is never called. | Remove the method. |
| SampleBankingApp/Services/TransactionService.cs | 72 | `IsWithinDailyLimit` is never called. | Remove the method or implement the daily limit check. |
| SampleBankingApp/Data/DatabaseHelper.cs | 57 | `ExecuteQueryWithParams` is marked obsolete and never called. | Remove the method. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 60 | Deposit cap of `1000000` is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 62 | Interest bonus rate `0.05m` is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/UserService.cs | 55 | Max page size of `50` is hardcoded. | Move to configuration or a named constant. |
| SampleBankingApp/Services/UserService.cs | 25 | Max user ID of `1000000` is hardcoded. | Remove this arbitrary limit or move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 33 | `"notifications@company.com"` is hardcoded in multiple places. | Move to configuration. |
| SampleBankingApp/Services/AuthService.cs | 44 | `"SuperAdmin"` and `"admin"` are hardcoded. | Use constants or configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `new Regex(...)` is instantiated inside methods called repeatedly. | Make the Regex instances `static readonly`. |
| SampleBankingApp/Services/UserService.cs | 9 | Shared mutable static state `_auditLog` and `_requestCount` accessed without synchronization. | Use thread-safe collections or locks. |
| SampleBankingApp/Services/UserService.cs | 66 | `GetAuditReport` uses string concatenation in a loop. | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/EmailService.cs | 51 | `SendWelcomeEmail` calls `username.ToUpper()` without null check. | Add a null check before calling `.ToUpper()`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | `GetOpenConnection` leaks resource ownership to callers with no documented contract. | Return an already disposed connection or document the disposal requirement. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 27 | `UseDeveloperExceptionPage()` called unconditionally. | Wrap in `if (app.Environment.IsDevelopment())`. |
| SampleBankingApp/Program.cs | 19 | `ValidateLifetime = false` on JWT. | Set to `true` to enforce token expiration. |
| SampleBankingApp/Program.cs | 29 | HTTPS redirection commented out. | Uncomment `app.UseHttpsRedirection()`. |
| SampleBankingApp/Program.cs | 31 | Overly permissive CORS policy. | Restrict origins and methods. |
| SampleBankingApp/appsettings.json | 21 | Debug log levels set for production namespaces. | Set default log level to Information or Warning. |
| SampleBankingApp/appsettings.json | N/A | Missing environment-specific config overrides. | Add `appsettings.Production.json` for production settings. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | Outdated or vulnerable NuGet package `Newtonsoft.Json` 12.0.3. | Update to the latest version. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/SampleBankingApp.csproj | N/A | No test project exists. | Add an xUnit or NUnit test project. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `Transfer` method lacks tests for boundary conditions and financial calculations. | Test insufficient funds, self-transfer, and fee calculation. |
| SampleBankingApp/Services/AuthService.cs | 32 | `Login` method lacks tests for auth flows and backdoor. | Test valid/invalid credentials and remove backdoor. |
| SampleBankingApp/Services/UserService.cs | 54 | `GetUsersPage` lacks tests for pagination logic. | Test off-by-one errors and page size limits. |
| SampleBankingApp/Services/TransactionService.cs | 58 | `Deposit` method lacks tests for invalid amounts. | Test zero, negative, and over-limit deposits. |