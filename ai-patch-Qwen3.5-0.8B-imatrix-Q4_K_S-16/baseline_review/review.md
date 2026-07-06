## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 33 | SQL Injection via string interpolation in `Login` query. | Use parameterized queries or an ORM. |
| SampleBankingApp/Services/AuthService.cs | 15 | Hardcoded admin bypass password (`SuperAdmin2024`). | Remove backdoor; enforce standard auth flow. |
| SampleBankingApp/Services/AuthService.cs | 58 | Weak cryptography: MD5 used for password hashing. | Use bcrypt, Argon2, or PBKDF2. |
| SampleBankingApp/Services/TransactionService.cs | 42 | SQL Injection in `Transfer` via string interpolation in `UPDATE`. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 63 | SQL Injection in `Deposit` via string interpolation in `UPDATE`. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 83 | SQL Injection in `RecordTransaction` via string interpolation in `INSERT`. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 38 | SQL Injection in `UpdateUser` via string interpolation in `UPDATE`. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 49 | SQL Injection in `DeleteUser` via string interpolation in `DELETE`. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 79 | SQL Injection in `SearchUsers` via `ExecuteQuery` with raw `LIKE` clause. | Use parameterized queries with proper escaping. |
| SampleBankingApp/Data/DatabaseHelper.cs | 13 | Hardcoded fallback connection string with credentials. | Remove hardcoded credentials; fail securely if config missing. |
| SampleBankingApp/appsettings.json | 2 | Production database credentials committed to source control. | Use environment variables or secret management. |
| SampleBankingApp/appsettings.json | 13 | JWT secret key is weak and committed to source control. | Use a strong, random secret stored in secure config. |
| SampleBankingApp/appsettings.json | 18 | SMTP credentials committed to source control. | Use environment variables or secret management. |
| SampleBankingApp/Controllers/TransactionController.cs | 26 | Missing ownership check on `Transfer` (user can transfer from any ID). | Validate `fromUserId` matches authenticated user. |
| SampleBankingApp/Controllers/UserController.cs | 38 | Missing authorization check on `UpdateUser` (any user can update any user). | Add `[Authorize(Roles="Admin")]` or ownership check. |
| SampleBankingApp/Controllers/UserController.cs | 49 | Missing authorization check on `DeleteUser` (any user can delete any user). | Add `[Authorize(Roles="Admin")]` or ownership check. |
| SampleBankingApp/Controllers/UserController.cs | 63 | Missing authorization on `GetAuditLog` (exposes sensitive audit data). | Add `[Authorize(Roles="Admin")]`. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 38 | Balance check uses `amount` but deducts `amount + fee`, allowing negative balances. | Check `fromBalance >= totalDebit`. |
| SampleBankingApp/Services/TransactionService.cs | 38 | Missing check for self-transfer (`fromUserId == toUserId`). | Add validation to prevent self-transfers. |
| SampleBankingApp/Services/UserService.cs | 66 | Pagination offset calculation `page * pageSize` is off-by-one for 1-based pages. | Use `(page - 1) * pageSize`. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit interest bonus calculation `amount * 0.05m * 1` is redundant and unclear. | Clarify intent or remove redundant `* 1`. |
| SampleBankingApp/Controllers/TransactionController.cs | 15 | `int.Parse` on `userIdClaim` can throw if claim is missing or non-numeric. | Add null/parse validation before parsing. |
| SampleBankingApp/Controllers/TransactionController.cs | 28 | `int.Parse` on `userIdClaim` can throw if claim is missing or non-numeric. | Add null/parse validation before parsing. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/UserService.cs | 85 | `SearchUsers` catches `Exception` and returns empty list, hiding errors. | Log error and return empty list, or propagate exception. |
| SampleBankingApp/Controllers/UserController.cs | 43 | `UpdateUser` returns raw `ex.Message` to client, leaking internal details. | Return generic error message; log details. |
| SampleBankingApp/Controllers/UserController.cs | 46 | `UpdateUser` returns raw `ex.Message` for general exceptions. | Return generic error message; log details. |
| SampleBankingApp/Services/EmailService.cs | 63 | `SendWelcomeEmail` catches `Exception` and prints to console, swallowing errors. | Log error properly; consider propagating or handling gracefully. |
| SampleBankingApp/Services/TransactionService.cs | 42 | `Transfer` lacks database transaction for atomic balance updates. | Wrap balance updates and record transaction in a DB transaction. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `Deposit` lacks database transaction for atomic balance update and record. | Wrap balance update and record transaction in a DB transaction. |
| SampleBankingApp/Services/TransactionService.cs | 42 | Side effect (email) occurs after DB writes; if email fails, transaction is already committed. | Consider sending email asynchronously or within transaction scope if critical. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 20 | `GetOpenConnection` returns open connection; caller must dispose. | Document disposal responsibility or use `using` in caller. |
| SampleBankingApp/Data/DatabaseHelper.cs | 25 | `ExecuteQuery` opens connection but never closes/disposes it. | Wrap connection in `using` statement. |
| SampleBankingApp/Data/DatabaseHelper.cs | 38 | `ExecuteQuerySafe` opens connection but `SqlDataAdapter` may not close it on error. | Ensure connection is disposed in `finally` or `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 48 | `ExecuteNonQuery` opens connection; if `ExecuteNonQuery` throws, connection leaks. | Wrap connection in `using` statement. |
| SampleBankingApp/Services/AuthService.cs | 36 | `SqlConnection` opened but never closed/disposed in `Login`. | Wrap connection in `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 18 | `SmtpClient` held as instance field; not thread-safe and may leak sockets. | Create `SmtpClient` per send or use a thread-safe wrapper. |
| SampleBankingApp/Services/EmailService.cs | 38 | `MailMessage` not disposed after sending. | Wrap `MailMessage` in `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 58 | `MailMessage` not disposed after sending. | Wrap `MailMessage` in `using` statement. |
| SampleBankingApp/Services/EmailService.cs | 73 | `MailMessage` not disposed after sending. | Wrap `MailMessage` in `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 35 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/TransactionService.cs | 36 | `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Check `Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/UserService.cs | 28 | `table.Rows[0]` accessed without checking `Rows.Count > 0` (though checked earlier, race condition possible). | Ensure check is immediate before access. |
| SampleBankingApp/Services/UserService.cs | 79 | `SearchUsers` may throw if `ExecuteQuery` returns null or empty. | Validate result before iterating. |
| SampleBankingApp/Program.cs | 22 | `jwtSecret` used without null check; `GetBytes` may throw if null. | Add null check or default value. |
| SampleBankingApp/Services/AuthService.cs | 68 | `_config["Jwt:SecretKey"]` used without null check. | Add null check or default value. |
| SampleBankingApp/Services/EmailService.cs | 22 | `_config["Email:SmtpHost"]` used without null check. | Add null check or default value. |
| SampleBankingApp/Services/EmailService.cs | 23 | `_config["Email:SmtpPort"]` used without null check (has default, but host may be null). | Add null check for host. |
| SampleBankingApp/Services/EmailService.cs | 24 | `_config["Email:Username"]` used without null check. | Add null check. |
| SampleBankingApp/Services/EmailService.cs | 25 | `_config["Email:Password"]` used without null check. | Add null check. |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 25 | `JoinWithSeparator` is inefficient and likely unused; `JoinWithSeparatorFixed` exists. | Remove `JoinWithSeparator` if unused. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `ObfuscateAccount` duplicates `MaskAccountNumber` functionality. | Remove duplicate method. |
| SampleBankingApp/Helpers/StringHelper.cs | 55 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove method; use standard library. |
| SampleBankingApp/Services/AuthService.cs | 78 | `HashPasswordSha1` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/AuthService.cs | 85 | `ValidateToken` has unreachable code after `return true`. | Remove unreachable code or fix logic. |
| SampleBankingApp/Services/TransactionService.cs | 89 | `FormatCurrency` is defined but never called. | Remove unused method. |
| SampleBankingApp/Services/TransactionService.cs | 93 | `RefundTransaction` throws `NotImplementedException`. | Implement or remove endpoint. |
| SampleBankingApp/Data/DatabaseHelper.cs | 58 | `ExecuteQueryWithParams` is marked `[Obsolete]` but still present. | Remove obsolete method. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 10 | `TransactionFeeRate` (0.015m) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 11 | `MaxTransactionsPerDay` (10) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit limit (1000000) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Interest rate (0.05m) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 64 | Page size limit (50) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 18 | User ID range limit (1000000) is hardcoded. | Move to configuration. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | Email length limit (254) is hardcoded. | Define as constant or config. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | Username length limits (3, 20) are hardcoded. | Define as constants or config. |
| SampleBankingApp/Services/EmailService.cs | 10 | Email subjects are hardcoded. | Move to configuration or resources. |
| SampleBankingApp/Services/EmailService.cs | 13 | `MaxRetries` (3) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 14 | `SmtpTimeoutMs` (5000) is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 38 | Sender email ("notifications@company.com") is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 58 | Sender email ("notifications@company.com") is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 73 | Sender email ("notifications@company.com") is hardcoded. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 12 | `new Regex(...)` created on every call; should be static readonly. | Cache regex as static readonly field. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | `new Regex(...)` created on every call; should be static readonly. | Cache regex as static readonly field. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | String concatenation in loop (`result += item`). | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/UserService.cs | 75 | String concatenation in loop (`report += entry`). | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/UserService.cs | 13 | Static mutable state `_auditLog` and `_requestCount` shared across instances. | Use thread-safe collection or DI-scoped state. |
| SampleBankingApp/Services/EmailService.cs | 18 | `SmtpClient` is not thread-safe; shared instance causes race conditions. | Create per-request or use thread-safe wrapper. |
| SampleBankingApp/Services/EmailService.cs | 45 | `Console.WriteLine` used for logging; should use `ILogger`. | Inject and use `ILogger`. |
| SampleBankingApp/Services/EmailService.cs | 63 | `Console.WriteLine` used for logging; should use `ILogger`. | Inject and use `ILogger`. |
| SampleBankingApp/Program.cs | 10 | `DatabaseHelper` registered as `Singleton`; may hold open connections. | Register as `Scoped` or ensure thread safety. |
| SampleBankingApp/Program.cs | 11 | `EmailService` registered as `Scoped`; but uses non-thread-safe `SmtpClient`. | Ensure `SmtpClient` is created per scope or is thread-safe. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 28 | `UseDeveloperExceptionPage()` enabled unconditionally. | Only enable in Development environment. |
| SampleBankingApp/Program.cs | 30 | `UseHttpsRedirection()` is commented out. | Uncomment for production security. |
| SampleBankingApp/Program.cs | 32 | CORS allows any origin, method, and header. | Restrict to specific origins and methods. |
| SampleBankingApp/Program.cs | 18 | `ValidateLifetime = false` on JWT validation. | Set to `true` to enforce token expiration. |
| SampleBankingApp/appsettings.json | 22 | Debug log level set for all namespaces. | Set to `Information` or `Warning` for production. |
| SampleBankingApp/SampleBankingApp.csproj | 10 | `Newtonsoft.Json` version 12.0.3 is outdated and vulnerable. | Update to latest stable version. |
| SampleBankingApp/SampleBankingApp.csproj | 6 | `DebugSymbols` and `DebugType` set for release builds. | Remove or conditionally set for Debug only. |
| SampleBankingApp/SampleBankingApp.csproj | 5 | `TreatWarningsAsErrors` is false. | Set to `true` for better code quality. |
| SampleBankingApp/appsettings.json | 1 | No environment-specific config files (e.g., `appsettings.Production.json`). | Add environment-specific overrides. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---|---|---|
| N/A | N/A | No test project exists. | Create unit tests for critical services. |
| SampleBankingApp/Services/TransactionService.cs | 25 | `Transfer` logic (balance check, fee calculation, SQL injection risks) needs testing. | Test boundary conditions, insufficient funds, self-transfer. |
| SampleBankingApp/Services/TransactionService.cs | 60 | `Deposit` logic (limits, interest, SQL injection risks) needs testing. | Test invalid amounts, max limits, interest calculation. |
| SampleBankingApp/Services/AuthService.cs | 25 | `Login` logic (SQL injection, weak hashing, backdoor) needs testing. | Test valid/invalid credentials, backdoor bypass. |
| SampleBankingApp/Services/UserService.cs | 15 | `GetUserById` and pagination logic needs testing. | Test invalid IDs, pagination offsets, empty results. |
| SampleBankingApp/Services/UserService.cs | 35 | `UpdateUser` and `DeleteUser` SQL injection risks need testing. | Test with malicious input to ensure parameterization. |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | Validation methods (`IsValidEmail`, `IsValidUsername`) need testing. | Test boundary lengths, invalid characters. |
| SampleBankingApp/Controllers/AuthController.cs | 15 | `Login` endpoint needs integration testing. | Test HTTP responses, token generation, error cases. |
| SampleBankingApp/Controllers/TransactionController.cs | 15 | `Transfer` and `Deposit` endpoints need integration testing. | Test authorization, request validation, error handling. |