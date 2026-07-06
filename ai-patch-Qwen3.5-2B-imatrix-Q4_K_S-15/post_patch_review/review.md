## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| `DatabaseHelper.cs` | 14 | Hardcoded database credentials in fallback connection string. | Remove hardcoded credentials; require config or fail securely. |
| `DatabaseHelper.cs` | 29 | SQL Injection via string interpolation in `ExecuteQuery`. | Use parameterized queries exclusively; remove `ExecuteQuery`. |
| `AuthService.cs` | 15 | Hardcoded admin bypass password (`SuperAdmin2024`). | Remove backdoor; enforce standard authentication for all users. |
| `AuthService.cs` | 48 | Admin bypass logic allows login without DB check or password hash. | Remove the `if (username == "admin" ...)` block entirely. |
| `AuthService.cs` | 56 | MD5 used for password hashing (cryptographically broken). | Use bcrypt, Argon2, or PBKDF2 with salt. |
| `AuthService.cs` | 92 | SHA1 used for password hashing (cryptographically weak). | Remove `HashPasswordSha1`; use secure hashing algorithm. |
| `Program.cs` | 24 | JWT `ValidateLifetime` set to `false`. | Set `ValidateLifetime = true` and configure token expiration. |
| `Program.cs` | 36 | `UseDeveloperExceptionPage()` enabled unconditionally. | Wrap in `if (app.Environment.IsDevelopment())`. |
| `Program.cs` | 38 | HTTPS redirection commented out. | Uncomment `app.UseHttpsRedirection()`. |
| `Program.cs` | 40 | CORS policy allows any origin, method, and header. | Restrict CORS to specific trusted origins and methods. |
| `TransactionController.cs` | 27 | Missing authorization check for transfer ownership. | Verify `fromUserId` matches the authenticated user's ID. |
| `TransactionController.cs` | 37 | Missing authorization check for deposit ownership. | Verify `userId` matches the authenticated user's ID. |
| `UserController.cs` | 28 | Missing authorization check for user retrieval. | Ensure user can only view their own data or has admin role. |
| `UserController.cs` | 42 | Missing authorization check for user update. | Ensure user can only update their own data or has admin role. |
| `UserController.cs` | 56 | Missing authorization check for user deletion. | Ensure user can only delete their own data or has admin role. |
| `UserController.cs` | 70 | Missing authorization check for audit log access. | Restrict access to admin roles only. |
| `appsettings.json` | 3 | Production database credentials committed to source control. | Use environment variables or secret management tools. |
| `appsettings.json` | 13 | JWT secret key is weak and committed to source control. | Use a strong, randomly generated key stored in secrets. |
| `appsettings.json` | 18 | SMTP password committed to source control. | Use environment variables or secret management tools. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| `TransactionService.cs` | 38 | Balance check uses `amount` but deducts `amount + fee`. | Change condition to `fromBalance >= totalDebit`. |
| `TransactionService.cs` | 38 | No check for self-transfer (`fromUserId == toUserId`). | Add validation to prevent transferring to oneself. |
| `TransactionService.cs` | 38 | No check if `toUserTable` has rows before accessing `Rows[0]`. | Check `toUserTable.Rows.Count > 0` before access. |
| `TransactionService.cs` | 38 | No check if `fromUserTable` has rows before accessing `Rows[0]`. | Check `fromUserTable.Rows.Count > 0` before access. |
| `TransactionService.cs` | 52 | `ExecuteNonQuery` called with raw SQL string, not parameterized. | Use `ExecuteQuerySafe` or parameterized helper. |
| `TransactionService.cs` | 54 | `ExecuteNonQuery` called with raw SQL string, not parameterized. | Use `ExecuteQuerySafe` or parameterized helper. |
| `TransactionService.cs` | 73 | `ExecuteNonQuery` called with raw SQL string, not parameterized. | Use `ExecuteQuerySafe` or parameterized helper. |
| `TransactionService.cs` | 87 | `ExecuteQuerySafe` used but SQL contains `GETDATE()` which may cause issues. | Ensure date handling is consistent and parameterized if needed. |
| `TransactionService.cs` | 95 | `RecordTransaction` uses string interpolation for IDs, risking SQL injection. | Use parameterized queries for all values. |
| `UserService.cs` | 38 | `ExecuteQuery` used for search, vulnerable to SQL injection. | Use parameterized query with `LIKE` parameter. |
| `UserService.cs` | 38 | `SearchUsers` catches all exceptions and returns empty list. | Log error and return empty list or throw specific exception. |
| `UserService.cs` | 56 | `UpdateUser` does not pass parameters to `ExecuteNonQuery`. | Use parameterized query helper. |
| `UserService.cs` | 68 | `DeleteUser` does not pass parameters to `ExecuteNonQuery`. | Use parameterized query helper. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| `TransactionController.cs` | 45 | `Refund` catches `NotImplementedException` and returns 500. | Return 501 Not Implemented or handle gracefully. |
| `TransactionController.cs` | 49 | `Refund` catches broad `Exception` and logs, but returns generic 500. | Consider specific error handling or logging details. |
| `UserController.cs` | 45 | `UpdateUser` catches `ArgumentException` and returns message. | Return standardized error response. |
| `UserController.cs` | 50 | `UpdateUser` catches broad `Exception` and logs. | Consider specific error handling. |
| `UserController.cs` | 60 | `DeleteUser` catches broad `Exception` and logs. | Consider specific error handling. |
| `EmailService.cs` | 45 | `SendTransferNotification` retries on `SmtpException` but throws after max retries. | Consider logging and returning failure status instead of throwing. |
| `EmailService.cs` | 62 | `SendWelcomeEmail` catches `Exception` and prints to console. | Use proper logging framework instead of `Console.WriteLine`. |
| `EmailService.cs` | 75 | `SendWelcomeEmailHtml` does not handle exceptions. | Add try-catch block with proper logging. |
| `AuthService.cs` | 32 | `Login` does not handle exceptions from DB operations. | Add try-catch block with proper logging. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| `DatabaseHelper.cs` | 21 | `GetOpenConnection` returns open connection without disposal. | Ensure callers dispose connection or use `using` statement. |
| `DatabaseHelper.cs` | 29 | `ExecuteQuery` opens connection but does not dispose it. | Use `using` statement for connection and command. |
| `DatabaseHelper.cs` | 45 | `ExecuteQuerySafe` uses `using` for connection and command. | No issue; properly disposed. |
| `DatabaseHelper.cs` | 58 | `ExecuteNonQuery` opens connection but does not use `using`. | Use `using` statement for connection and command. |
| `DatabaseHelper.cs` | 68 | `TableExists` uses `using` for connection. | No issue; properly disposed. |
| `DatabaseHelper.cs` | 76 | `ExecuteQueryWithParams` uses `using` for connection and command. | No issue; properly disposed. |
| `EmailService.cs` | 15 | `SmtpClient` held as instance field, not thread-safe. | Create new `SmtpClient` per send or use thread-safe alternative. |
| `EmailService.cs` | 35 | `MailMessage` created but not disposed. | Use `using` statement for `MailMessage`. |
| `EmailService.cs` | 58 | `MailMessage` created but not disposed. | Use `using` statement for `MailMessage`. |
| `EmailService.cs` | 72 | `MailMessage` created but not disposed. | Use `using` statement for `MailMessage`. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| `TransactionController.cs` | 26 | `userIdClaim` may be null, causing `int.Parse` to throw. | Add null check before parsing. |
| `TransactionController.cs` | 36 | `userIdClaim` may be null, causing `int.Parse` to throw. | Add null check before parsing. |
| `TransactionService.cs` | 38 | `fromUserTable.Rows[0]` accessed without checking count. | Check `Rows.Count > 0` before access. |
| `TransactionService.cs` | 38 | `toUserTable.Rows[0]` accessed without checking count. | Check `Rows.Count > 0` before access. |
| `TransactionService.cs` | 87 | `table.Rows[0]` accessed without checking count. | Check `Rows.Count > 0` before access. |
| `UserService.cs` | 32 | `table.Rows[0]` accessed without checking count in `GetUserById`. | Check `Rows.Count > 0` before access. |
| `AuthService.cs` | 32 | `reader["Id"]` etc. accessed without checking if reader has data. | Ensure `reader.Read()` returns true before access. |
| `Program.cs` | 18 | `jwtSecret` may be null, causing `GetBytes` to throw. | Add null check or default value. |
| `EmailService.cs` | 18 | `_config["Email:SmtpHost"]` may be null. | Add null check or default value. |
| `EmailService.cs` | 19 | `_config["Email:SmtpPort"]` may be null, causing `int.Parse` to throw. | Add null check or default value. |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| `DatabaseHelper.cs` | 76 | `ExecuteQueryWithParams` marked `[Obsolete]` but still present. | Remove obsolete method if not used. |
| `StringHelper.cs` | 28 | `JoinWithSeparator` is inefficient and likely unused. | Remove if not used; use `JoinWithSeparatorFixed`. |
| `StringHelper.cs` | 34 | `JoinWithSeparatorFixed` duplicates `string.Join`. | Remove if not used; use `string.Join` directly. |
| `StringHelper.cs` | 42 | `MaskAccountNumber` and `ObfuscateAccount` are similar. | Consolidate into one method. |
| `StringHelper.cs` | 56 | `ToTitleCase` duplicates standard library functionality. | Remove if not used; use `TextInfo.ToTitleCase`. |
| `StringHelper.cs` | 62 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove if not used; use `string.IsNullOrWhiteSpace`. |
| `AuthService.cs` | 92 | `HashPasswordSha1` is unused. | Remove unused method. |
| `AuthService.cs` | 98 | `ValidateToken` is unused. | Remove unused method. |
| `TransactionService.cs` | 99 | `FormatCurrency` is unused. | Remove unused method. |
| `EmailService.cs` | 68 | `BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml`. | Keep if used; otherwise remove. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| `DatabaseHelper.cs` | 14 | Hardcoded connection string fallback. | Use configuration or fail securely. |
| `AuthService.cs` | 15 | Hardcoded admin bypass password. | Remove backdoor. |
| `AuthService.cs` | 56 | MD5 hashing algorithm hardcoded. | Use configurable secure hashing. |
| `AuthService.cs` | 92 | SHA1 hashing algorithm hardcoded. | Remove unused method. |
| `TransactionService.cs` | 10 | `TransactionFeeRate` hardcoded. | Move to configuration. |
| `TransactionService.cs` | 11 | `MaxTransactionsPerDay` hardcoded. | Move to configuration. |
| `TransactionService.cs` | 73 | Interest bonus rate hardcoded. | Move to configuration. |
| `UserService.cs` | 28 | User ID range limit hardcoded. | Move to configuration. |
| `UserService.cs` | 48 | Page size limit hardcoded. | Move to configuration. |
| `EmailService.cs` | 10 | `TransferSubject` hardcoded. | Move to configuration. |
| `EmailService.cs` | 11 | `WelcomeSubject` hardcoded. | Move to configuration. |
| `EmailService.cs` | 13 | `MaxRetries` hardcoded. | Move to configuration. |
| `EmailService.cs` | 14 | `SmtpTimeoutMs` hardcoded. | Move to configuration. |
| `appsettings.json` | 13 | JWT secret key is weak. | Use strong, randomly generated key. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| `StringHelper.cs` | 28 | String concatenation in loop. | Use `StringBuilder` or `string.Join`. |
| `StringHelper.cs` | 15 | `new Regex` inside method. | Use `static readonly` regex. |
| `StringHelper.cs` | 22 | `new Regex` inside method. | Use `static readonly` regex. |
| `UserService.cs` | 10 | Static mutable state `_auditLog`. | Use thread-safe collection or external storage. |
| `UserService.cs` | 11 | Static mutable state `_requestCount`. | Use thread-safe counter or remove. |
| `DatabaseHelper.cs` | 29 | Raw SQL string interpolation. | Use parameterized queries. |
| `TransactionService.cs` | 52 | Raw SQL string interpolation. | Use parameterized queries. |
| `TransactionService.cs` | 54 | Raw SQL string interpolation. | Use parameterized queries. |
| `TransactionService.cs` | 73 | Raw SQL string interpolation. | Use parameterized queries. |
| `TransactionService.cs` | 95 | Raw SQL string interpolation. | Use parameterized queries. |
| `UserService.cs` | 38 | Raw SQL string interpolation. | Use parameterized queries. |
| `UserService.cs` | 56 | Raw SQL string interpolation. | Use parameterized queries. |
| `UserService.cs` | 68 | Raw SQL string interpolation. | Use parameterized queries. |
| `EmailService.cs` | 45 | `Console.WriteLine` for logging. | Use proper logging framework. |
| `EmailService.cs` | 62 | `Console.WriteLine` for logging. | Use proper logging framework. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| `Program.cs` | 36 | `UseDeveloperExceptionPage()` enabled unconditionally. | Wrap in `if (app.Environment.IsDevelopment())`. |
| `Program.cs` | 24 | JWT `ValidateLifetime` set to `false`. | Set `ValidateLifetime = true`. |
| `Program.cs` | 38 | HTTPS redirection commented out. | Uncomment `app.UseHttpsRedirection()`. |
| `Program.cs` | 40 | CORS policy allows any origin, method, and header. | Restrict CORS to specific trusted origins. |
| `appsettings.json` | 3 | Production database credentials committed. | Use environment variables or secret management. |
| `appsettings.json` | 13 | JWT secret key is weak. | Use strong, randomly generated key. |
| `appsettings.json` | 18 | SMTP password committed. | Use environment variables or secret management. |
| `appsettings.json` | 22 | Debug log levels set for production. | Set appropriate log levels for production. |
| `SampleBankingApp.csproj` | 10 | `TreatWarningsAsErrors` set to `false`. | Set to `true` for better code quality. |
| `SampleBankingApp.csproj` | 11 | `DebugSymbols` set to `true` in release. | Set to `false` for release builds. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---|---|---|
| N/A | N/A | No test project exists. | Create test project with unit tests for critical methods. |
| `AuthService.cs` | 28 | `Login` method lacks tests. | Add tests for valid/invalid credentials, admin bypass. |
| `AuthService.cs` | 56 | `HashPasswordMd5` lacks tests. | Add tests for password hashing. |
| `AuthService.cs` | 62 | `GenerateJwtToken` lacks tests. | Add tests for token generation and validation. |
| `TransactionService.cs` | 28 | `Transfer` method lacks tests. | Add tests for successful/failed transfers, balance checks. |
| `TransactionService.cs` | 68 | `Deposit` method lacks tests. | Add tests for valid/invalid deposits, interest calculation. |
| `TransactionService.cs` | 82 | `IsWithinDailyLimit` lacks tests. | Add tests for daily transaction limit checks. |
| `UserService.cs` | 26 | `GetUserById` lacks tests. | Add tests for valid/invalid user IDs. |
| `UserService.cs` | 38 | `UpdateUser` lacks tests. | Add tests for valid/invalid updates. |
| `UserService.cs` | 56 | `DeleteUser` lacks tests. | Add tests for valid/invalid deletions. |
| `UserService.cs` | 68 | `GetUsersPage` lacks tests. | Add tests for pagination logic. |
| `UserService.cs` | 82 | `SearchUsers` lacks tests. | Add tests for search functionality. |
| `StringHelper.cs` | 15 | `IsValidEmail` lacks tests. | Add tests for email validation. |
| `StringHelper.cs` | 22 | `IsValidUsername` lacks tests. | Add tests for username validation. |
| `StringHelper.cs` | 42 | `MaskAccountNumber` lacks tests. | Add tests for account number masking. |
| `StringHelper.cs` | 56 | `ToTitleCase` lacks tests. | Add tests for title case conversion. |
| `StringHelper.cs` | 62 | `IsBlank` lacks tests. | Add tests for blank string detection. |