## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 38 | SQL Injection via string interpolation in `Login` method. | Use parameterized queries. |
| SampleBankingApp/Services/AuthService.cs | 52 | Hardcoded admin backdoor password allows bypassing authentication. | Remove hardcoded credentials and backdoor logic. |
| SampleBankingApp/Services/AuthService.cs | 68 | Passwords hashed using weak MD5 algorithm without salt. | Use bcrypt, Argon2, or PBKDF2 with salt. |
| SampleBankingApp/Services/TransactionService.cs | 43 | SQL Injection via string interpolation in `Transfer` method. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 63 | SQL Injection via string interpolation in `Deposit` method. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 88 | SQL Injection via string interpolation in `RecordTransaction` method. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 42 | SQL Injection via string interpolation in `UpdateUser` method. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 54 | SQL Injection via string interpolation in `DeleteUser` method. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 82 | SQL Injection via string interpolation in `SearchUsers` method. | Use parameterized queries with LIKE. |
| SampleBankingApp/Data/DatabaseHelper.cs | 12 | Hardcoded fallback connection string with credentials. | Remove hardcoded credentials; fail securely if config missing. |
| SampleBankingApp/appsettings.json | 3 | Production database credentials committed to source control. | Use environment variables or secret management. |
| SampleBankingApp/appsettings.json | 13 | JWT secret key is weak and hardcoded in config. | Use a strong, randomly generated secret from secure storage. |
| SampleBankingApp/appsettings.json | 19 | SMTP password committed to source control. | Use environment variables or secret management. |
| SampleBankingApp/Controllers/TransactionController.cs | 26 | Missing ownership check on `Transfer` endpoint (any authenticated user can transfer from any ID). | Validate `fromUserId` matches the authenticated user's ID. |
| SampleBankingApp/Controllers/UserController.cs | 38 | Missing ownership check on `UpdateUser` endpoint (any authenticated user can update any user). | Validate `id` matches the authenticated user's ID or require admin role. |
| SampleBankingApp/Controllers/UserController.cs | 52 | Missing ownership check on `DeleteUser` endpoint (any authenticated user can delete any user). | Validate `id` matches the authenticated user's ID or require admin role. |
| SampleBankingApp/Program.cs | 33 | `ValidateLifetime` set to false, allowing expired tokens. | Set `ValidateLifetime` to true. |
| SampleBankingApp/Program.cs | 41 | Developer exception page enabled in production. | Use `UseDeveloperExceptionPage` only in Development environment. |
| SampleBankingApp/Program.cs | 44 | HTTPS redirection commented out. | Uncomment `UseHttpsRedirection`. |
| SampleBankingApp/Program.cs | 46 | Overly permissive CORS policy allows any origin, method, and header. | Restrict CORS to specific trusted origins and methods. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/UserService.cs | 75 | Pagination offset calculation is incorrect (`page * pageSize` instead of `(page - 1) * pageSize`). | Change to `(page - 1) * pageSize`. |
| SampleBankingApp/Services/TransactionService.cs | 40 | Balance check compares against `amount` but deducts `amount + fee`, allowing negative balances. | Check if `fromBalance >= totalDebit`. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit interest calculation multiplies by 1, effectively ignoring the bonus logic or applying it incorrectly. | Clarify intent; likely should be `amount * 0.05m` or similar. |
| SampleBankingApp/Services/AuthService.cs | 102 | `ValidateToken` method returns `true` immediately, ignoring actual token validation. | Remove early return and implement proper validation. |
| SampleBankingApp/Controllers/TransactionController.cs | 18 | `int.Parse` on `userIdClaim` can throw if claim is null or non-integer. | Use `int.TryParse` or null checks. |
| SampleBankingApp/Controllers/TransactionController.cs | 32 | `int.Parse` on `userIdClaim` can throw if claim is null or non-integer. | Use `int.TryParse` or null checks. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/UserService.cs | 92 | `SearchUsers` catches broad `Exception` and returns empty list, hiding errors. | Log the exception and return an error response or empty list with logging. |
| SampleBankingApp/Services/EmailService.cs | 58 | `SendWelcomeEmail` catches broad `Exception` and swallows it, hiding failures. | Log the exception instead of printing to console. |
| SampleBankingApp/Controllers/UserController.cs | 42 | `UpdateUser` returns raw `ex.Message` to client, leaking internal details. | Return a generic error message. |
| SampleBankingApp/Controllers/UserController.cs | 45 | `UpdateUser` returns raw `ex.Message` to client, leaking internal details. | Return a generic error message. |
| SampleBankingApp/Services/TransactionService.cs | 94 | `RefundTransaction` throws `NotImplementedException`, causing 500 error. | Implement the feature or return a proper 501/400 response. |
| SampleBankingApp/Services/TransactionService.cs | 35 | `Transfer` lacks database transaction; partial failures can corrupt balances. | Wrap DB operations in a transaction. |
| SampleBankingApp/Services/TransactionService.cs | 60 | `Deposit` lacks database transaction; side effects may occur after partial failure. | Wrap DB operations in a transaction. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 22 | `GetOpenConnection` returns open connection without disposal responsibility. | Use `using` blocks or ensure callers dispose connections. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | `ExecuteQuery` opens connection but never closes/disposes it. | Wrap connection in `using` block. |
| SampleBankingApp/Data/DatabaseHelper.cs | 43 | `ExecuteQuerySafe` opens connection but `SqlDataAdapter` may not close it properly if exception occurs. | Ensure connection is disposed via `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 55 | `ExecuteNonQuery` opens connection but may leak if `ExecuteNonQuery` throws. | Wrap connection in `using` block. |
| SampleBankingApp/Services/AuthService.cs | 40 | `SqlConnection` opened but never closed/disposed in `Login`. | Wrap connection in `using` block. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` held as instance field; not thread-safe and may leak sockets. | Create `SmtpClient` per send operation or use a thread-safe wrapper. |
| SampleBankingApp/Services/EmailService.cs | 38 | `MailMessage` created but never disposed. | Wrap `MailMessage` in `using` block. |
| SampleBankingApp/Services/EmailService.cs | 55 | `MailMessage` created but never disposed. | Wrap `MailMessage` in `using` block. |
| SampleBankingApp/Services/EmailService.cs | 72 | `MailMessage` created but never disposed. | Wrap `MailMessage` in `using` block. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 40 | `reader["Id"]` cast to `int` may throw if column is null. | Check for `DBNull` before casting. |
| SampleBankingApp/Services/AuthService.cs | 41 | `reader["Username"]` cast to `string` may throw if column is null. | Check for `DBNull` before casting. |
| SampleBankingApp/Services/AuthService.cs | 42 | `reader["Email"]` cast to `string` may throw if column is null. | Check for `DBNull` before casting. |
| SampleBankingApp/Services/AuthService.cs | 43 | `reader["Role"]` cast to `string` may throw if column is null. | Check for `DBNull` before casting. |
| SampleBankingApp/Services/AuthService.cs | 44 | `reader["Balance"]` cast to `decimal` may throw if column is null. | Check for `DBNull` before casting. |
| SampleBankingApp/Services/AuthService.cs | 45 | `reader["IsActive"]` cast to `bool` may throw if column is null. | Check for `DBNull` before casting. |
| SampleBankingApp/Services/TransactionService.cs | 38 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing. |
| SampleBankingApp/Services/TransactionService.cs | 41 | `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count` before accessing. |
| SampleBankingApp/Services/UserService.cs | 35 | `table.Rows[0]` accessed without checking `Rows.Count > 0` in `GetUserById`. | Check `Rows.Count` before accessing. |
| SampleBankingApp/Services/UserService.cs | 78 | `table.Rows` iterated without checking if table is null or empty. | Add null/empty checks. |
| SampleBankingApp/Services/UserService.cs | 90 | `table.Rows` iterated without checking if table is null or empty. | Add null/empty checks. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | `email.Length` accessed without null check. | Add null check. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | `username.Length` accessed without null check. | Add null check. |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | `accountNumber.Length` accessed without null check. | Add null check. |
| SampleBankingApp/Helpers/StringHelper.cs | 46 | `account[^4..]` accessed without null check. | Add null check. |
| SampleBankingApp/Program.cs | 20 | `jwtSecret` used without null check in `GetBytes`. | Add null check or default value. |
| SampleBankingApp/Services/EmailService.cs | 24 | `_config["Email:SmtpHost"]` passed to `SmtpClient` constructor without null check. | Add null check. |
| SampleBankingApp/Services/EmailService.cs | 25 | `_config["Email:SmtpPort"]` parsed without null check. | Add null check. |
| SampleBankingApp/Services/EmailService.cs | 27 | `_config["Email:Username"]` passed without null check. | Add null check. |
| SampleBankingApp/Services/EmailService.cs | 28 | `_config["Email:Password"]` passed without null check. | Add null check. |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 63 | `ExecuteQueryWithParams` marked `[Obsolete]` but still present. | Remove obsolete method. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | `JoinWithSeparator` is inefficient and likely unused; `JoinWithSeparatorFixed` exists. | Remove `JoinWithSeparator`. |
| SampleBankingApp/Helpers/StringHelper.cs | 30 | `JoinWithSeparatorFixed` duplicates `string.Join`. | Remove redundant method. |
| SampleBankingApp/Helpers/StringHelper.cs | 52 | `ToTitleCase` duplicates standard library functionality. | Remove redundant method. |
| SampleBankingApp/Helpers/StringHelper.cs | 57 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove redundant method. |
| SampleBankingApp/Services/AuthService.cs | 95 | `HashPasswordSha1` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/TransactionService.cs | 91 | `FormatCurrency` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/EmailService.cs | 68 | `BuildHtmlTemplate` is only called by `SendWelcomeEmailHtml`, which is unused. | Remove unused methods. |
| SampleBankingApp/Services/EmailService.cs | 71 | `SendWelcomeEmailHtml` is defined but never called. | Remove unused method. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 16 | Hardcoded admin bypass password. | Move to secure config or remove. |
| SampleBankingApp/Services/TransactionService.cs | 12 | Hardcoded transaction fee rate. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 13 | Hardcoded max transactions per day. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Hardcoded deposit limit (1000000). | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 64 | Hardcoded interest rate (0.05m). | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 73 | Hardcoded page size limit (50). | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 28 | Hardcoded user ID range limit (1000000). | Move to configuration. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | Hardcoded email length limit (254). | Move to configuration or constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | Hardcoded username length limits (3, 20). | Move to configuration or constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | Hardcoded account number mask length (4). | Move to configuration or constant. |
| SampleBankingApp/Services/EmailService.cs | 10 | Hardcoded email subjects. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 13 | Hardcoded max retries. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 14 | Hardcoded SMTP timeout. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 38 | Hardcoded sender email address. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 55 | Hardcoded sender email address. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 72 | Hardcoded sender email address. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 25 | String concatenation in loop (`result += item + separator`). | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | `new Regex` created on every call. | Use `static readonly Regex`. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | `new Regex` created on every call. | Use `static readonly Regex`. |
| SampleBankingApp/Services/UserService.cs | 12 | Static mutable state `_auditLog` shared across instances. | Use thread-safe collection or DI-scoped service. |
| SampleBankingApp/Services/UserService.cs | 13 | Static mutable state `_requestCount` shared across instances. | Use thread-safe counter or DI-scoped service. |
| SampleBankingApp/Services/UserService.cs | 85 | String concatenation in loop (`report += entry + "\n"`). | Use `StringBuilder`. |
| SampleBankingApp/Services/EmailService.cs | 58 | `Console.WriteLine` used for logging. | Use `ILogger`. |
| SampleBankingApp/Services/EmailService.cs | 48 | `Console.WriteLine` used for logging. | Use `ILogger`. |
| SampleBankingApp/Controllers/UserController.cs | 42 | Raw exception message returned to client. | Return generic error message. |
| SampleBankingApp/Controllers/UserController.cs | 45 | Raw exception message returned to client. | Return generic error message. |
| SampleBankingApp/Program.cs | 10 | `DatabaseHelper` registered as Singleton, but holds non-thread-safe state (connections). | Register as Scoped or ensure thread safety. |
| SampleBankingApp/Program.cs | 13 | `EmailService` registered as Scoped, but holds non-thread-safe `SmtpClient`. | Register as Transient or fix thread safety. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 33 | `ValidateLifetime` set to false. | Set to true. |
| SampleBankingApp/Program.cs | 41 | `UseDeveloperExceptionPage()` called unconditionally. | Use only in Development environment. |
| SampleBankingApp/Program.cs | 44 | HTTPS redirection commented out. | Uncomment `UseHttpsRedirection`. |
| SampleBankingApp/Program.cs | 46 | Overly permissive CORS policy. | Restrict to specific origins/methods. |
| SampleBankingApp/appsettings.json | 23 | Debug log levels set for production namespaces. | Set to Information or Warning for production. |
| SampleBankingApp/SampleBankingApp.csproj | 12 | `Newtonsoft.Json` version 12.0.3 is outdated and vulnerable. | Update to latest stable version. |
| SampleBankingApp/SampleBankingApp.csproj | 13 | `System.IdentityModel.Tokens.Jwt` version 7.0.0 may be incompatible with .NET 8. | Update to compatible version. |
| SampleBankingApp/SampleBankingApp.csproj | 11 | `System.Data.SqlClient` is legacy; use `Microsoft.Data.SqlClient`. | Update package. |
| SampleBankingApp/SampleBankingApp.csproj | 7 | `DebugSymbols` and `DebugType` set in project file. | Remove; let build configuration handle this. |
| SampleBankingApp/SampleBankingApp.csproj | 6 | `TreatWarningsAsErrors` set to false. | Set to true for better code quality. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---|---|---|
| N/A | N/A | No test project exists. | Create test project. |
| SampleBankingApp/Services/AuthService.cs | 30 | `Login` method lacks tests for SQL injection, weak hashing, and backdoor. | Add tests for authentication flows. |
| SampleBankingApp/Services/TransactionService.cs | 35 | `Transfer` method lacks tests for balance checks, fees, and SQL injection. | Add tests for transfer logic. |
| SampleBankingApp/Services/TransactionService.cs | 60 | `Deposit` method lacks tests for limits and interest calculation. | Add tests for deposit logic. |
| SampleBankingApp/Services/UserService.cs | 70 | `GetUsersPage` lacks tests for pagination offset calculation. | Add tests for pagination. |
| SampleBankingApp/Services/UserService.cs | 35 | `GetUserById` lacks tests for boundary conditions. | Add tests for user retrieval. |
| SampleBankingApp/Services/UserService.cs | 42 | `UpdateUser` lacks tests for SQL injection and validation. | Add tests for user update. |
| SampleBankingApp/Services/UserService.cs | 54 | `DeleteUser` lacks tests for SQL injection and validation. | Add tests for user deletion. |
| SampleBankingApp/Services/UserService.cs | 82 | `SearchUsers` lacks tests for SQL injection and error handling. | Add tests for user search. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | `IsValidEmail` lacks tests for regex patterns. | Add tests for email validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | `IsValidUsername` lacks tests for regex patterns. | Add tests for username validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | `MaskAccountNumber` lacks tests for masking logic. | Add tests for account masking. |