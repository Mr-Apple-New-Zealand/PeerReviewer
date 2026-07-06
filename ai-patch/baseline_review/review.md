## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 33 | SQL Injection in login query via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/AuthService.cs | 48 | Hardcoded admin backdoor password bypasses authentication. | Remove backdoor logic entirely. |
| SampleBankingApp/Services/AuthService.cs | 56 | MD5 used for password hashing, which is cryptographically broken. | Use bcrypt, Argon2, or PBKDF2. |
| SampleBankingApp/Services/TransactionService.cs | 44 | SQL Injection in balance update via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 68 | SQL Injection in deposit update via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 88 | SQL Injection in transaction record insertion via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 42 | SQL Injection in user update via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 55 | SQL Injection in user deletion via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 88 | SQL Injection in user search via string interpolation in `ExecuteQuery`. | Use parameterized queries. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | Hardcoded fallback connection string with credentials. | Remove hardcoded credentials; fail securely if config is missing. |
| SampleBankingApp/appsettings.json | 3 | Production database credentials committed to source control. | Use environment variables or secret management. |
| SampleBankingApp/appsettings.json | 13 | JWT secret key is weak and committed to source control. | Use a strong, random secret stored in secure config. |
| SampleBankingApp/appsettings.json | 18 | Email SMTP password committed to source control. | Use environment variables or secret management. |
| SampleBankingApp/Controllers/UserController.cs | 36 | Broken Access Control: Any authenticated user can update/delete any user. | Add authorization checks to ensure users only modify their own data. |
| SampleBankingApp/Controllers/TransactionController.cs | 22 | Broken Access Control: No check preventing users from transferring to/from unauthorized accounts. | Verify ownership or authorization for transfer endpoints. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 40 | Balance check excludes transaction fee, allowing negative balances. | Check `fromBalance >= amount + fee`. |
| SampleBankingApp/Services/UserService.cs | 72 | Pagination offset calculation is incorrect (off-by-one page). | Use `(page - 1) * pageSize`. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit interest calculation multiplies by 1, adding no bonus. | Remove `* 1` or adjust logic if bonus is intended. |
| SampleBankingApp/Services/AuthService.cs | 48 | Admin backdoor returns user with ID 0, which may cause DB errors. | Return a valid user object or handle admin login properly. |
| SampleBankingApp/Helpers/StringHelper.cs | 23 | `JoinWithSeparator` adds trailing separator to result. | Use `string.Join` or fix loop logic. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/UserService.cs | 92 | Catches broad `Exception` and returns empty list, hiding errors. | Log exception and return appropriate error response. |
| SampleBankingApp/Controllers/UserController.cs | 42 | Returns raw exception message to client in 500 response. | Return generic error message; log details server-side. |
| SampleBankingApp/Services/EmailService.cs | 58 | Swallows exception in `SendWelcomeEmail`, failing silently. | Log exception and consider retry or alerting. |
| SampleBankingApp/Services/TransactionService.cs | 44 | Multiple DB writes without transaction, risking partial updates. | Wrap transfer logic in a database transaction. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit DB write without transaction, risking data inconsistency. | Wrap deposit logic in a database transaction. |
| SampleBankingApp/Controllers/TransactionController.cs | 38 | Catches `NotImplementedException` but returns 500, misleading client. | Return 501 Not Implemented or handle gracefully. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 24 | `GetOpenConnection` returns open connection; caller must dispose. | Use `using` statements or return disposable wrapper. |
| SampleBankingApp/Data/DatabaseHelper.cs | 33 | `ExecuteQuery` opens connection but never closes/disposes it. | Wrap connection in `using` block. |
| SampleBankingApp/Data/DatabaseHelper.cs | 56 | `ExecuteNonQuery` opens connection but doesn't dispose command/adapter. | Use `using` statements for all disposables. |
| SampleBankingApp/Services/AuthService.cs | 36 | `SqlConnection` opened but never closed/disposed in `Login`. | Wrap connection in `using` block. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` held as instance field; not thread-safe and leaks sockets. | Create new `SmtpClient` per send or use async properly. |
| SampleBankingApp/Services/EmailService.cs | 38 | `MailMessage` not disposed after sending. | Wrap `MailMessage` in `using` block. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 22 | `int.Parse` on potentially null claim value. | Add null check before parsing. |
| SampleBankingApp/Controllers/TransactionController.cs | 33 | `int.Parse` on potentially null claim value. | Add null check before parsing. |
| SampleBankingApp/Services/TransactionService.cs | 38 | Accesses `Rows[0]` without checking `Rows.Count > 0`. | Check row count before accessing. |
| SampleBankingApp/Services/TransactionService.cs | 42 | Accesses `Rows[0]` without checking `Rows.Count > 0`. | Check row count before accessing. |
| SampleBankingApp/Services/UserService.cs | 33 | Accesses `Rows[0]` without checking `Rows.Count > 0` in `GetUserById`. | Check row count before accessing. |
| SampleBankingApp/Services/UserService.cs | 82 | Accesses `Rows[0]` without checking `Rows.Count > 0` in pagination. | Check row count before accessing. |
| SampleBankingApp/Services/UserService.cs | 90 | Accesses `Rows[0]` without checking `Rows.Count > 0` in search. | Check row count before accessing. |
| SampleBankingApp/Program.cs | 22 | `jwtSecret` used without null check, may throw if config missing. | Add null check or default value. |
| SampleBankingApp/Services/AuthService.cs | 68 | `_config["Jwt:SecretKey"]` used without null check. | Add null check or default value. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 27 | `JoinWithSeparatorFixed` is unused; duplicate of `string.Join`. | Remove unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `ObfuscateAccount` is unused. | Remove unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 50 | `ToTitleCase` is unused. | Remove unused method. |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | `IsBlank` is unused. | Remove unused method. |
| SampleBankingApp/Services/EmailService.cs | 68 | `BuildHtmlTemplate` is unused. | Remove unused method. |
| SampleBankingApp/Services/EmailService.cs | 72 | `SendWelcomeEmailHtml` is unused. | Remove unused method. |
| SampleBankingApp/Services/TransactionService.cs | 92 | `FormatCurrency` is unused. | Remove unused method. |
| SampleBankingApp/Services/AuthService.cs | 78 | `HashPasswordSha1` is unused. | Remove unused method. |
| SampleBankingApp/Services/AuthService.cs | 83 | `ValidateToken` is unused. | Remove unused method. |
| SampleBankingApp/Data/DatabaseHelper.cs | 68 | `ExecuteQueryWithParams` is marked obsolete and unused. | Remove obsolete method. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 68 | Magic number `1000000` for deposit limit. | Define as named constant. |
| SampleBankingApp/Services/UserService.cs | 22 | Magic number `1000000` for user ID range. | Define as named constant. |
| SampleBankingApp/Services/UserService.cs | 68 | Magic number `50` for page size limit. | Define as named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | Magic number `254` for email length. | Define as named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | Magic numbers `3` and `20` for username length. | Define as named constants. |
| SampleBankingApp/Services/EmailService.cs | 38 | Magic string `"notifications@company.com"` repeated. | Define as named constant or config. |
| SampleBankingApp/Services/EmailService.cs | 52 | Magic string `"notifications@company.com"` repeated. | Define as named constant or config. |
| SampleBankingApp/Services/EmailService.cs | 74 | Magic string `"notifications@company.com"` repeated. | Define as named constant or config. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 14 | `new Regex` created on every call; should be static readonly. | Cache regex as static readonly field. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | `new Regex` created on every call; should be static readonly. | Cache regex as static readonly field. |
| SampleBankingApp/Helpers/StringHelper.cs | 23 | String concatenation in loop; O(nÂ²) performance. | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/UserService.cs | 80 | String concatenation in loop; O(nÂ²) performance. | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/UserService.cs | 20 | Static mutable state `_auditLog` and `_requestCount` shared across instances. | Use thread-safe collections or remove static state. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` as instance field; not thread-safe. | Create per-request or use async properly. |
| SampleBankingApp/Services/AuthService.cs | 56 | MD5 hashing is insecure and slow for modern standards. | Use bcrypt or Argon2. |
| SampleBankingApp/Services/TransactionService.cs | 44 | Raw SQL strings instead of parameterized queries. | Use parameterized queries. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 30 | `UseDeveloperExceptionPage()` enabled unconditionally. | Only enable in Development environment. |
| SampleBankingApp/Program.cs | 32 | HTTPS redirection commented out. | Uncomment `UseHttpsRedirection()`. |
| SampleBankingApp/Program.cs | 34 | Overly permissive CORS policy (`AllowAnyOrigin`). | Restrict to specific origins. |
| SampleBankingApp/Program.cs | 18 | `ValidateLifetime = false` on JWT validation. | Set to `true` and configure expiration. |
| SampleBankingApp/appsettings.json | 22 | Debug log level set for all namespaces in production. | Set to `Information` or `Warning` for production. |
| SampleBankingApp/SampleBankingApp.csproj | 12 | `Newtonsoft.Json` version 12.0.3 is outdated and vulnerable. | Update to latest stable version. |
| SampleBankingApp/SampleBankingApp.csproj | 14 | `System.IdentityModel.Tokens.Jwt` version 7.0.0 may be incompatible. | Ensure version compatibility with ASP.NET Core 8. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `DebugSymbols` and `DebugType` set for release builds. | Remove or conditionally set for Debug only. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create unit tests for all services. |
| SampleBankingApp/Services/TransactionService.cs | 28 | Critical financial logic lacks tests for balance checks and fees. | Test transfer, deposit, and fee calculations. |
| SampleBankingApp/Services/AuthService.cs | 28 | Authentication logic lacks tests for login and token generation. | Test login success/failure and JWT generation. |
| SampleBankingApp/Services/UserService.cs | 28 | User management logic lacks tests for CRUD operations. | Test user creation, update, deletion, and pagination. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | String validation helpers lack tests. | Test email and username validation edge cases. |
| SampleBankingApp/Controllers/TransactionController.cs | 22 | Controller actions lack integration tests. | Test API endpoints with mock services. |