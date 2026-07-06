## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 38 | SQL Injection in login query via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/AuthService.cs | 56 | Hardcoded admin backdoor password allows bypassing authentication. | Remove hardcoded credentials and backdoor logic. |
| SampleBankingApp/Services/AuthService.cs | 72 | MD5 used for password hashing, which is cryptographically broken. | Use bcrypt, Argon2, or PBKDF2. |
| SampleBankingApp/Services/TransactionService.cs | 46 | SQL Injection in balance update via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 68 | SQL Injection in deposit update via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 92 | SQL Injection in transaction recording via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 43 | SQL Injection in user update via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 55 | SQL Injection in user deletion via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 85 | SQL Injection in user search via string interpolation. | Use parameterized queries with LIKE. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | SQL Injection in ExecuteQuery via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Data/DatabaseHelper.cs | 15 | Hardcoded fallback connection string with credentials in source. | Remove hardcoded credentials; require config. |
| SampleBankingApp/appsettings.json | 3 | Production database credentials committed to source control. | Use environment variables or secret manager. |
| SampleBankingApp/appsettings.json | 13 | Weak JWT secret key committed to source control. | Use a strong, random secret from secure config. |
| SampleBankingApp/appsettings.json | 18 | Email SMTP password committed to source control. | Use environment variables or secret manager. |
| SampleBankingApp/Controllers/TransactionController.cs | 20 | Missing ownership check allows users to transfer from any account. | Verify `fromUserId` matches authenticated user. |
| SampleBankingApp/Controllers/UserController.cs | 38 | Missing ownership check allows updating any user's data. | Verify requested ID matches authenticated user. |
| SampleBankingApp/Controllers/UserController.cs | 50 | Missing ownership check allows deleting any user. | Verify requested ID matches authenticated user. |
| SampleBankingApp/Program.cs | 35 | JWT lifetime validation disabled (`ValidateLifetime = false`). | Set `ValidateLifetime = true`. |
| SampleBankingApp/Program.cs | 43 | Developer exception page enabled in production configuration. | Conditionally enable only in Development env. |
| SampleBankingApp/Program.cs | 45 | HTTPS redirection commented out. | Uncomment `app.UseHttpsRedirection()`. |
| SampleBankingApp/Program.cs | 47 | Overly permissive CORS policy allows any origin/method/header. | Restrict to specific trusted origins and methods. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check uses `amount` but deducts `amount + fee`, causing overdraft. | Check `fromBalance >= totalDebit`. |
| SampleBankingApp/Services/UserService.cs | 78 | Pagination skip calculation uses `page * pageSize` instead of `(page - 1) * pageSize`. | Change to `(page - 1) * pageSize`. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit interest calculation multiplies by `1`, making the bonus equal to the principal. | Remove `* 1` or adjust logic. |
| SampleBankingApp/Services/AuthService.cs | 98 | `ValidateToken` returns `true` immediately, ignoring actual validation logic. | Remove early return or implement validation. |
| SampleBankingApp/Controllers/TransactionController.cs | 21 | `int.Parse` on claim value may throw if claim is missing or non-integer. | Use `int.TryParse` with null check. |
| SampleBankingApp/Controllers/TransactionController.cs | 33 | `int.Parse` on claim value may throw if claim is missing or non-integer. | Use `int.TryParse` with null check. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/UserController.cs | 42 | Raw exception message returned to client in `UpdateUser`. | Return generic error message; log details. |
| SampleBankingApp/Controllers/UserController.cs | 45 | Raw exception message returned to client in `UpdateUser`. | Return generic error message; log details. |
| SampleBankingApp/Services/UserService.cs | 90 | `SearchUsers` catches all exceptions and returns empty list, hiding errors. | Log exception and return error status or specific exception. |
| SampleBankingApp/Services/EmailService.cs | 63 | `SendWelcomeEmail` swallows exceptions, failing silently. | Log exception and notify caller or retry. |
| SampleBankingApp/Services/TransactionService.cs | 50 | Database updates for transfer are not wrapped in a transaction. | Use `SqlTransaction` for atomicity. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Database update for deposit is not wrapped in a transaction. | Use `SqlTransaction` for atomicity. |
| SampleBankingApp/Services/TransactionService.cs | 92 | Transaction recording is not wrapped in a transaction with balance updates. | Include in same transaction as balance updates. |
| SampleBankingApp/Services/AuthService.cs | 38 | `SqlConnection` opened in `Login` is never closed or disposed. | Wrap in `using` statement or dispose explicitly. |
| SampleBankingApp/Services/AuthService.cs | 42 | `SqlDataReader` is never closed or disposed. | Wrap in `using` statement. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 23 | `GetOpenConnection` returns open connection; caller must dispose. | Document disposal requirement or return `using` scope. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | `ExecuteQuery` opens connection but does not dispose it or command. | Wrap connection and command in `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 48 | `ExecuteNonQuery` opens connection but does not dispose command. | Wrap command in `using`. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` is not thread-safe and held as instance field. | Create new instance per send or use lock. |
| SampleBankingApp/Services/EmailService.cs | 38 | `MailMessage` is not disposed after sending. | Wrap `MailMessage` in `using`. |
| SampleBankingApp/Services/EmailService.cs | 58 | `MailMessage` is not disposed after sending. | Wrap `MailMessage` in `using`. |
| SampleBankingApp/Services/EmailService.cs | 72 | `MailMessage` is not disposed after sending. | Wrap `MailMessage` in `using`. |
| SampleBankingApp/Services/AuthService.cs | 38 | `SqlConnection` in `Login` is never disposed. | Wrap in `using`. |
| SampleBankingApp/Services/AuthService.cs | 42 | `SqlDataReader` in `Login` is never disposed. | Wrap in `using`. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 40 | Accesses `Rows[0]` without checking `Rows.Count > 0`. | Check count before access. |
| SampleBankingApp/Services/TransactionService.cs | 44 | Accesses `Rows[0]` without checking `Rows.Count > 0`. | Check count before access. |
| SampleBankingApp/Services/UserService.cs | 35 | Accesses `Rows[0]` without checking `Rows.Count > 0` (though checked earlier, race condition possible). | Ensure check is immediate or use `FirstOrDefault`. |
| SampleBankingApp/Services/UserService.cs | 85 | `SearchUsers` passes `query` directly to SQL without null check. | Add null/empty check for query. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | `email.Length` throws if `email` is null. | Add null check. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | `username.Length` throws if `username` is null. | Add null check. |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | `accountNumber.Length` throws if `accountNumber` is null. | Add null check. |
| SampleBankingApp/Helpers/StringHelper.cs | 46 | `account[^4..]` throws if `account` is null. | Add null check. |
| SampleBankingApp/Program.cs | 28 | `jwtSecret` may be null, causing `GetBytes` to throw. | Add null check or default value. |
| SampleBankingApp/Services/EmailService.cs | 25 | `_config["Email:SmtpHost"]` may be null. | Add null check. |
| SampleBankingApp/Services/EmailService.cs | 27 | `_config["Email:SmtpPort"]` may be null, causing `int.Parse` to throw. | Add null check or default. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 95 | `HashPasswordSha1` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/AuthService.cs | 100 | `ValidateToken` logic after `return true` is unreachable. | Remove dead code or fix logic. |
| SampleBankingApp/Helpers/StringHelper.cs | 26 | `JoinWithSeparator` is inefficient and likely unused if `JoinWithSeparatorFixed` exists. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 32 | `JoinWithSeparatorFixed` duplicates `string.Join`. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 52 | `ToTitleCase` duplicates standard library functionality. | Remove if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 57 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove if unused. |
| SampleBankingApp/Services/TransactionService.cs | 98 | `FormatCurrency` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/TransactionService.cs | 103 | `RefundTransaction` throws `NotImplementedException`. | Implement or remove endpoint. |
| SampleBankingApp/Services/EmailService.cs | 68 | `BuildHtmlTemplate` is private and only used once; consider inlining. | Inline or remove if unused elsewhere. |
| SampleBankingApp/Data/DatabaseHelper.cs | 55 | `ExecuteQueryWithParams` is marked `[Obsolete]` but still present. | Remove obsolete code. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 10 | `TransactionFeeRate` is hardcoded; should be configurable. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 11 | `MaxTransactionsPerDay` is hardcoded; should be configurable. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 66 | Deposit limit `1000000` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 67 | Interest rate `0.05m` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 76 | Page size limit `50` is hardcoded. | Move to configuration. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | Email length limit `254` is hardcoded. | Define as constant or config. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | Username length limits `3` and `20` are hardcoded. | Define as constants. |
| SampleBankingApp/Services/EmailService.cs | 10 | Email subjects are hardcoded strings. | Move to configuration or resources. |
| SampleBankingApp/Services/EmailService.cs | 13 | `MaxRetries` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 14 | `SmtpTimeoutMs` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/AuthService.cs | 15 | Admin bypass password is hardcoded. | Remove entirely. |
| SampleBankingApp/Program.cs | 28 | JWT config keys are hardcoded strings. | Define as constants. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 26 | String concatenation in loop causes O(n²) performance. | Use `string.Join` or `StringBuilder`. |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | `new Regex` created on every call; should be static readonly. | Cache regex pattern. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | `new Regex` created on every call; should be static readonly. | Cache regex pattern. |
| SampleBankingApp/Services/UserService.cs | 10 | `_auditLog` is static mutable state, not thread-safe. | Use thread-safe collection or remove. |
| SampleBankingApp/Services/UserService.cs | 11 | `_requestCount` is static mutable state, not thread-safe. | Use `Interlocked` or remove. |
| SampleBankingApp/Services/UserService.cs | 80 | String concatenation in loop for audit report. | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpClient` is not thread-safe; shared instance causes issues. | Create per-request or use lock. |
| SampleBankingApp/Services/TransactionService.cs | 46 | SQL injection via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 43 | SQL injection via string interpolation. | Use parameterized queries. |
| SampleBankingApp/Services/AuthService.cs | 38 | SQL injection via string interpolation. | Use parameterized queries. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 35 | `ValidateLifetime = false` disables token expiration. | Set to `true`. |
| SampleBankingApp/Program.cs | 43 | `UseDeveloperExceptionPage()` enabled unconditionally. | Wrap in `if (env.IsDevelopment())`. |
| SampleBankingApp/Program.cs | 45 | HTTPS redirection commented out. | Uncomment `app.UseHttpsRedirection()`. |
| SampleBankingApp/Program.cs | 47 | CORS allows any origin, method, and header. | Restrict to specific origins/methods. |
| SampleBankingApp/appsettings.json | 22 | Debug log level set for production namespaces. | Set to `Information` or `Warning` for prod. |
| SampleBankingApp/SampleBankingApp.csproj | 12 | `DebugSymbols` and `DebugType` set to full in release-like config. | Disable for release builds. |
| SampleBankingApp/SampleBankingApp.csproj | 18 | `Newtonsoft.Json` version 12.0.3 is outdated and vulnerable. | Update to latest version. |
| SampleBankingApp/SampleBankingApp.csproj | 17 | `System.Data.SqlClient` is legacy; use `Microsoft.Data.SqlClient`. | Update package. |
| SampleBankingApp/appsettings.json | 3 | Connection string contains credentials. | Use environment variables. |
| SampleBankingApp/appsettings.json | 13 | JWT secret is weak and hardcoded. | Use strong secret from secure config. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create test project. |
| SampleBankingApp/Services/TransactionService.cs | 25 | Transfer logic with fees and balance checks needs testing. | Test sufficient/insufficient funds, fee calculation. |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit logic with interest and limits needs testing. | Test valid/invalid amounts, interest calculation. |
| SampleBankingApp/Services/AuthService.cs | 30 | Login logic with SQL injection risk and backdoor needs testing. | Test valid/invalid credentials, backdoor removal. |
| SampleBankingApp/Services/UserService.cs | 75 | Pagination logic needs testing. | Test page size, skip calculation, boundary conditions. |
| SampleBankingApp/Services/UserService.cs | 85 | Search logic with SQL injection risk needs testing. | Test valid/invalid queries, injection prevention. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | Email validation regex needs testing. | Test valid/invalid email formats. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | Username validation regex needs testing. | Test valid/invalid username formats. |
| SampleBankingApp/Controllers/AuthController.cs | 15 | Login endpoint needs integration testing. | Test successful/failed login, token generation. |
| SampleBankingApp/Controllers/TransactionController.cs | 15 | Transfer endpoint needs integration testing. | Test authorization, ownership checks, transfer flow. |