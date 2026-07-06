## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 38 | SQL Injection via string interpolation in `Login` method. | Use parameterized queries. |
| SampleBankingApp/Services/AuthService.cs | 56 | Hardcoded admin backdoor password allows bypassing authentication. | Remove backdoor logic entirely. |
| SampleBankingApp/Services/AuthService.cs | 68 | Passwords hashed using MD5, which is cryptographically broken. | Use PBKDF2, BCrypt, or Argon2. |
| SampleBankingApp/Services/TransactionService.cs | 45 | SQL Injection in `Transfer` via string interpolation for UPDATE statements. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 63 | SQL Injection in `Deposit` via string interpolation for UPDATE statement. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 85 | SQL Injection in `RecordTransaction` via string interpolation for INSERT statement. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 38 | SQL Injection in `UpdateUser` via string interpolation for UPDATE statement. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 50 | SQL Injection in `DeleteUser` via string interpolation for DELETE statement. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 82 | SQL Injection in `SearchUsers` via string interpolation in `ExecuteQuery`. | Use parameterized queries. |
| SampleBankingApp/Data/DatabaseHelper.cs | 25 | Hardcoded fallback connection string with credentials in source code. | Remove hardcoded credentials; fail if config is missing. |
| SampleBankingApp/appsettings.json | 2 | Production database credentials committed to source control. | Use environment variables or secret management. |
| SampleBankingApp/appsettings.json | 13 | JWT secret key is weak and committed to source control. | Use a strong, random secret stored securely. |
| SampleBankingApp/appsettings.json | 18 | SMTP password committed to source control. | Use environment variables or secret management. |
| SampleBankingApp/Controllers/TransactionController.cs | 30 | Missing ownership check; any authenticated user can refund any transaction. | Verify the transaction belongs to the current user. |
| SampleBankingApp/Controllers/UserController.cs | 38 | Missing authorization check; any authenticated user can update any user. | Verify the user owns the resource or is an admin. |
| SampleBankingApp/Controllers/UserController.cs | 50 | Missing authorization check; any authenticated user can delete any user. | Verify the user owns the resource or is an admin. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check uses `amount` but deducts `amount + fee`, allowing negative balances. | Check if `fromBalance >= totalDebit`. |
| SampleBankingApp/Services/TransactionService.cs | 42 | No check to prevent transferring funds to oneself. | Add check `if (fromUserId == toUserId)`. |
| SampleBankingApp/Services/UserService.cs | 68 | Pagination offset calculation `page * pageSize` skips the first page of results. | Use `(page - 1) * pageSize`. |
| SampleBankingApp/Services/AuthService.cs | 92 | `ValidateToken` always returns `true` due to early return before validation logic. | Remove early return or fix logic flow. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit interest calculation `0.05m * 1` is redundant and potentially misleading. | Clarify intent or remove redundant multiplication. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/UserService.cs | 88 | `SearchUsers` catches all exceptions and returns empty list, hiding errors. | Log the exception and return an error response or specific empty result. |
| SampleBankingApp/Services/EmailService.cs | 58 | `SendWelcomeEmail` swallows exceptions, failing silently. | Log the exception and handle failure appropriately. |
| SampleBankingApp/Controllers/UserController.cs | 42 | `UpdateUser` returns raw exception message to client, leaking internal details. | Return a generic error message. |
| SampleBankingApp/Controllers/UserController.cs | 45 | `UpdateUser` returns raw exception message to client, leaking internal details. | Return a generic error message. |
| SampleBankingApp/Services/TransactionService.cs | 45 | Database updates in `Transfer` are not atomic; failure after debit leaves inconsistent state. | Wrap updates in a database transaction. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Database update in `Deposit` is not atomic with transaction recording. | Wrap updates in a database transaction. |
| SampleBankingApp/Services/EmailService.cs | 42 | `SmtpClient` is not thread-safe and shared across requests, causing potential concurrency issues. | Create `SmtpClient` per request or use a thread-safe wrapper. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | `GetOpenConnection` returns an open connection without disposing it, leaking resources. | Use `using` statements or ensure caller disposes. |
| SampleBankingApp/Data/DatabaseHelper.cs | 35 | `ExecuteQuery` opens connection but never closes/disposes it or the command. | Wrap connection and command in `using` blocks. |
| SampleBankingApp/Data/DatabaseHelper.cs | 53 | `ExecuteNonQuery` opens connection but does not dispose command or handle exceptions properly. | Wrap connection and command in `using` blocks. |
| SampleBankingApp/Services/AuthService.cs | 41 | `SqlConnection` and `SqlDataReader` in `Login` are not disposed. | Wrap in `using` statements. |
| SampleBankingApp/Services/EmailService.cs | 38 | `MailMessage` objects are not disposed after sending. | Wrap `MailMessage` in `using` statements. |
| SampleBankingApp/Services/EmailService.cs | 68 | `MailMessage` in `SendWelcomeEmailHtml` is not disposed. | Wrap `MailMessage` in `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 28 | `int.Parse` on `userIdClaim` can throw if claim is null or invalid. | Add null check and use `int.TryParse`. |
| SampleBankingApp/Controllers/TransactionController.cs | 42 | `int.Parse` on `userIdClaim` can throw if claim is null or invalid. | Add null check and use `int.TryParse`. |
| SampleBankingApp/Services/TransactionService.cs | 38 | Accessing `fromUserTable.Rows[0]` without checking if rows exist. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/TransactionService.cs | 42 | Accessing `toUserTable.Rows[0]` without checking if rows exist. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/UserService.cs | 32 | Accessing `table.Rows[0]` without checking if rows exist in `GetUserById`. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/UserService.cs | 72 | Accessing `table.Rows[0]` without checking if rows exist in `IsWithinDailyLimit`. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Helpers/StringHelper.cs | 14 | `email.Length` can throw if `email` is null. | Add null check or use `string.IsNullOrEmpty`. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `username.Length` can throw if `username` is null. | Add null check or use `string.IsNullOrEmpty`. |
| SampleBankingApp/Helpers/StringHelper.cs | 42 | `accountNumber.Length` can throw if `accountNumber` is null. | Add null check. |
| SampleBankingApp/Helpers/StringHelper.cs | 50 | `account[^4..]` can throw if `account` is null or too short. | Add null and length checks. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 95 | `HashPasswordSha1` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/TransactionService.cs | 89 | `FormatCurrency` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/EmailService.cs | 60 | `BuildHtmlTemplate` is only called by `SendWelcomeEmailHtml`, which is unused. | Remove unused methods. |
| SampleBankingApp/Helpers/StringHelper.cs | 30 | `JoinWithSeparator` is inefficient and likely unused given `JoinWithSeparatorFixed`. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 36 | `JoinWithSeparatorFixed` duplicates `string.Join`. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | `ToTitleCase` duplicates standard library functionality. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 62 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove if unused. |
| SampleBankingApp/Data/DatabaseHelper.cs | 60 | `ExecuteQueryWithParams` is marked obsolete but still present. | Remove obsolete method. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 12 | `TransactionFeeRate` is a magic number. | Define as named constant or config. |
| SampleBankingApp/Services/TransactionService.cs | 13 | `MaxTransactionsPerDay` is a magic number. | Define as named constant or config. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit limit `1000000` is a magic number. | Define as named constant or config. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Interest rate `0.05m` is a magic number. | Define as named constant or config. |
| SampleBankingApp/Services/UserService.cs | 66 | Page size limit `50` is a magic number. | Define as named constant or config. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | Email length limit `254` is a magic number. | Define as named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | Username length limits `3` and `20` are magic numbers. | Define as named constants. |
| SampleBankingApp/Services/EmailService.cs | 10 | Email subjects are hardcoded strings. | Move to configuration or constants. |
| SampleBankingApp/Services/EmailService.cs | 12 | `MaxRetries` and `SmtpTimeoutMs` are hardcoded. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 26 | String concatenation in loop is O(n²). | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Helpers/StringHelper.cs | 14 | `new Regex` created on every call. | Use `static readonly Regex`. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `new Regex` created on every call. | Use `static readonly Regex`. |
| SampleBankingApp/Services/UserService.cs | 10 | Static mutable state `_auditLog` and `_requestCount` are not thread-safe. | Use thread-safe collections or remove static state. |
| SampleBankingApp/Services/UserService.cs | 78 | String concatenation in loop for audit report. | Use `StringBuilder`. |
| SampleBankingApp/Services/EmailService.cs | 42 | `SmtpClient` is not thread-safe and shared. | Create per-request or use thread-safe wrapper. |
| SampleBankingApp/Controllers/AuthController.cs | 28 | Logging failed login attempts with username can aid enumeration attacks. | Log generic failure or rate-limit. |
| SampleBankingApp/Services/AuthService.cs | 38 | Raw SQL construction instead of using ORM or parameterized helpers. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 45 | Raw SQL construction instead of using ORM or parameterized helpers. | Use parameterized queries. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 38 | `UseDeveloperExceptionPage()` is enabled unconditionally. | Only enable in Development environment. |
| SampleBankingApp/Program.cs | 40 | HTTPS redirection is commented out. | Uncomment `UseHttpsRedirection()`. |
| SampleBankingApp/Program.cs | 42 | CORS policy allows any origin, method, and header. | Restrict to specific origins and methods. |
| SampleBankingApp/Program.cs | 28 | JWT `ValidateLifetime` is set to `false`. | Set to `true` to enforce token expiration. |
| SampleBankingApp/appsettings.json | 22 | Logging level is set to `Debug` for all namespaces. | Set to `Information` or `Warning` for production. |
| SampleBankingApp/SampleBankingApp.csproj | 11 | `Newtonsoft.Json` version 12.0.3 is outdated and potentially vulnerable. | Update to latest stable version. |
| SampleBankingApp/SampleBankingApp.csproj | 12 | `System.Data.SqlClient` is outdated; use `Microsoft.Data.SqlClient`. | Update to `Microsoft.Data.SqlClient`. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `DebugSymbols` and `DebugType` are set for release builds. | Remove or conditionally set for Debug only. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create a test project. |
| SampleBankingApp/Services/TransactionService.cs | 28 | `Transfer` logic needs tests for balance checks, fees, and SQL injection prevention. | Add unit tests for transfer scenarios. |
| SampleBankingApp/Services/TransactionService.cs | 58 | `Deposit` logic needs tests for limits and interest calculations. | Add unit tests for deposit scenarios. |
| SampleBankingApp/Services/UserService.cs | 64 | `GetUsersPage` pagination logic needs tests for offset calculation. | Add unit tests for pagination. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` needs tests for authentication and SQL injection prevention. | Add unit tests for login scenarios. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | String validation helpers need tests for boundary conditions. | Add unit tests for string helpers. |
| SampleBankingApp/Controllers/TransactionController.cs | 26 | Controller actions need integration tests for authorization and error handling. | Add integration tests for controllers. |