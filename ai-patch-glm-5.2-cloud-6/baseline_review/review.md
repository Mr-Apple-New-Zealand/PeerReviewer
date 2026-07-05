## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 38 | SQL Injection via string interpolation in `Login` method. | Use parameterized queries or an ORM. |
| SampleBankingApp/Services/AuthService.cs | 42 | Weak cryptography: MD5 used for password hashing. | Use bcrypt, Argon2, or PBKDF2. |
| SampleBankingApp/Services/AuthService.cs | 56 | Hardcoded admin backdoor password bypasses authentication. | Remove the hardcoded bypass logic entirely. |
| SampleBankingApp/Services/TransactionService.cs | 48 | SQL Injection in `Transfer` via string interpolation in `ExecuteNonQuery`. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 68 | SQL Injection in `Deposit` via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 92 | SQL Injection in `RecordTransaction` via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 43 | SQL Injection in `UpdateUser` via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 55 | SQL Injection in `DeleteUser` via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 88 | SQL Injection in `SearchUsers` via `ExecuteQuery` with raw string. | Use parameterized queries. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | Hardcoded fallback credentials in constructor. | Remove hardcoded credentials; fail securely if config is missing. |
| SampleBankingApp/appsettings.json | 3 | Production database credentials committed to source control. | Use environment variables or a secrets manager. |
| SampleBankingApp/appsettings.json | 13 | Email service password committed to source control. | Use environment variables or a secrets manager. |
| SampleBankingApp/Controllers/UserController.cs | 33 | Broken Access Control: `GetUser` allows any authenticated user to view any user. | Add authorization check to ensure user can only access their own data or has admin role. |
| SampleBankingApp/Controllers/UserController.cs | 53 | Broken Access Control: `UpdateUser` allows any authenticated user to update any user. | Add authorization check to ensure user can only update their own data or has admin role. |
| SampleBankingApp/Controllers/UserController.cs | 67 | Broken Access Control: `DeleteUser` allows any authenticated user to delete any user. | Add authorization check to ensure user can only delete their own data or has admin role. |
| SampleBankingApp/Controllers/TransactionController.cs | 22 | Broken Access Control: `Transfer` does not verify `fromUserId` matches the authenticated user. | Validate that `fromUserId` equals `User.FindFirst(ClaimTypes.NameIdentifier)?.Value`. |
| SampleBankingApp/Controllers/TransactionController.cs | 35 | Broken Access Control: `Deposit` does not verify `userId` matches the authenticated user. | Validate that `userId` equals `User.FindFirst(ClaimTypes.NameIdentifier)?.Value`. |
| SampleBankingApp/Program.cs | 27 | JWT `ValidateLifetime` is set to false, allowing expired tokens. | Set `ValidateLifetime` to true. |
| SampleBankingApp/Program.cs | 39 | Overly permissive CORS policy allows any origin, method, and header. | Restrict CORS to specific trusted origins and methods. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 46 | Balance check `fromBalance >= amount` ignores the transaction fee, allowing negative balances. | Check `fromBalance >= totalDebit` (amount + fee). |
| SampleBankingApp/Services/UserService.cs | 78 | Pagination offset calculation `page * pageSize` is off-by-one for 1-based indexing. | Use `(page - 1) * pageSize`. |
| SampleBankingApp/Services/AuthService.cs | 103 | `ValidateToken` returns `true` immediately without validating the token. | Remove the early return and implement actual validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 23 | `JoinWithSeparator` adds a trailing separator to the result string. | Use `string.Join` or fix the loop logic. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/UserService.cs | 90 | `SearchUsers` catches `Exception` and returns an empty list, hiding errors. | Log the exception and rethrow or return a specific error status. |
| SampleBankingApp/Services/EmailService.cs | 63 | `SendWelcomeEmail` swallows exceptions, failing silently. | Log the exception and consider rethrowing or notifying the user. |
| SampleBankingApp/Controllers/UserController.cs | 45 | `UpdateUser` returns raw `ex.Message` to the client, leaking internal details. | Return a generic error message and log the details. |
| SampleBankingApp/Controllers/UserController.cs | 48 | `UpdateUser` returns raw `ex.Message` for general exceptions. | Return a generic error message and log the details. |
| SampleBankingApp/Services/TransactionService.cs | 97 | `RefundTransaction` throws `NotImplementedException`, causing a 500 error. | Implement the feature or return a proper 501/404 response. |
| SampleBankingApp/Controllers/TransactionController.cs | 43 | `Refund` endpoint catches `NotImplementedException` but returns 500. | Return 501 Not Implemented or handle gracefully. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 24 | `GetOpenConnection` returns an open connection without disposing it. | Use `using` statements or ensure callers dispose the connection. |
| SampleBankingApp/Data/DatabaseHelper.cs | 33 | `ExecuteQuery` opens a connection but never closes or disposes it. | Wrap connection in `using` block. |
| SampleBankingApp/Data/DatabaseHelper.cs | 53 | `ExecuteNonQuery` opens a connection but may leak if `ExecuteNonQuery` throws. | Wrap connection in `using` block. |
| SampleBankingApp/Services/AuthService.cs | 43 | `Login` opens a connection and reader but never disposes them. | Wrap connection and reader in `using` blocks. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` is held as an instance field, which is not thread-safe and may leak sockets. | Create a new `SmtpClient` per send or use a thread-safe wrapper. |
| SampleBankingApp/Services/EmailService.cs | 45 | `MailMessage` is not disposed after sending. | Wrap `MailMessage` in a `using` block. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 21 | `int.Parse` on `userIdClaim` may throw if claim is null. | Add null check before parsing. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | `int.Parse` on `userIdClaim` may throw if claim is null. | Add null check before parsing. |
| SampleBankingApp/Services/TransactionService.cs | 41 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count`. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/TransactionService.cs | 42 | `toUserTable.Rows[0]` accessed without checking `Rows.Count`. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/UserService.cs | 38 | `table.Rows[0]` accessed without checking `Rows.Count` in `GetUserById`. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/UserService.cs | 83 | `table.Rows[0]` accessed without checking `Rows.Count` in `IsWithinDailyLimit`. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | `email.Length` called without null check on `email`. | Add null check or use `string.IsNullOrEmpty`. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | `username.Length` called without null check on `username`. | Add null check or use `string.IsNullOrEmpty`. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 27 | `JoinWithSeparatorFixed` is a duplicate of `string.Join` and likely unused. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 33 | `MaskAccountNumber` is duplicated by `ObfuscateAccount`. | Remove one implementation. |
| SampleBankingApp/Helpers/StringHelper.cs | 47 | `ToTitleCase` duplicates `CultureInfo.TextInfo.ToTitleCase`. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 52 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove if unused. |
| SampleBankingApp/Services/AuthService.cs | 95 | `HashPasswordSha1` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/TransactionService.cs | 95 | `FormatCurrency` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/EmailService.cs | 73 | `BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml`, which is likely unused. | Remove if `SendWelcomeEmailHtml` is unused. |
| SampleBankingApp/Data/DatabaseHelper.cs | 62 | `ExecuteQueryWithParams` is marked `[Obsolete]` but still present. | Remove obsolete code. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 10 | `TransactionFeeRate` (0.015m) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 11 | `MaxTransactionsPerDay` (10) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 66 | Deposit limit `1000000` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 67 | Interest bonus rate `0.05m` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 76 | Page size limit `50` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 26 | User ID range `1000000` is hardcoded. | Move to configuration. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | Email length limit `254` is hardcoded. | Define as constant or config. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | Username length limits `3` and `20` are hardcoded. | Define as constants or config. |
| SampleBankingApp/Services/AuthService.cs | 16 | Admin bypass password is hardcoded. | Remove entirely. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `new Regex` created on every call to `IsValidEmail`. | Use `static readonly Regex`. |
| SampleBankingApp/Helpers/StringHelper.cs | 21 | `new Regex` created on every call to `IsValidUsername`. | Use `static readonly Regex`. |
| SampleBankingApp/Helpers/StringHelper.cs | 23 | String concatenation in loop in `JoinWithSeparator`. | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/UserService.cs | 81 | String concatenation in loop in `GetAuditReport`. | Use `StringBuilder`. |
| SampleBankingApp/Services/UserService.cs | 12 | `_auditLog` is static mutable state, not thread-safe. | Use thread-safe collection or remove. |
| SampleBankingApp/Services/UserService.cs | 13 | `_requestCount` is static mutable state, not thread-safe. | Use `Interlocked` or remove. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` is not thread-safe. | Create per-request or synchronize access. |
| SampleBankingApp/Services/TransactionService.cs | 48 | `ExecuteNonQuery` called without transaction for atomic updates. | Wrap updates in a database transaction. |
| SampleBankingApp/Services/AuthService.cs | 43 | ADO.NET used directly instead of ORM or repository pattern. | Consider using Dapper or Entity Framework. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 37 | `UseDeveloperExceptionPage()` is enabled unconditionally. | Only enable in Development environment. |
| SampleBankingApp/Program.cs | 39 | HTTPS redirection is commented out. | Uncomment `UseHttpsRedirection()`. |
| SampleBankingApp/Program.cs | 41 | CORS allows any origin, method, and header. | Restrict to specific origins and methods. |
| SampleBankingApp/Program.cs | 27 | JWT `ValidateLifetime` is false. | Set to true. |
| SampleBankingApp/SampleBankingApp.csproj | 10 | `DebugSymbols` and `DebugType` are set for release builds. | Remove or conditionally set for Debug only. |
| SampleBankingApp/SampleBankingApp.csproj | 14 | `Newtonsoft.Json` version 12.0.3 is outdated and vulnerable. | Update to latest version. |
| SampleBankingApp/appsettings.json | 17 | Logging level is set to Debug for all namespaces. | Set to Information or Warning for production. |
| SampleBankingApp/appsettings.json | 1 | Production secrets are in `appsettings.json`. | Use environment variables or secrets manager. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create a test project. |
| SampleBankingApp/Services/TransactionService.cs | 25 | `Transfer` method lacks tests for balance checks, fees, and SQL injection prevention. | Add unit tests mocking the database helper. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `Deposit` method lacks tests for amount validation and interest calculation. | Add unit tests mocking the database helper. |
| SampleBankingApp/Services/AuthService.cs | 25 | `Login` method lacks tests for authentication logic and SQL injection prevention. | Add unit tests mocking the database helper. |
| SampleBankingApp/Services/UserService.cs | 23 | `GetUserById` lacks tests for null handling and ID validation. | Add unit tests mocking the database helper. |
| SampleBankingApp/Services/UserService.cs | 73 | `GetUsersPage` lacks tests for pagination logic. | Add unit tests mocking the database helper. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | `IsValidEmail` and `IsValidUsername` lack tests for regex patterns. | Add unit tests for various input cases. |
| SampleBankingApp/Controllers/AuthController.cs | 15 | `Login` endpoint lacks integration tests for HTTP responses. | Add integration tests. |
| SampleBankingApp/Controllers/TransactionController.cs | 15 | `Transfer` and `Deposit` endpoints lack integration tests. | Add integration tests. |