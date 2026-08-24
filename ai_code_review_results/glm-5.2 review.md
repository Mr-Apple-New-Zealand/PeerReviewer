## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded fallback connection string with credentials in `DatabaseHelper` constructor. | Remove the fallback and throw an exception if the configuration value is missing. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | SQL injection vulnerability in `ExecuteQuery` via interpolated `tableName` and `whereClause`. | Use parameterized queries or whitelist table names and parameterize the where clause. |
| SampleBankingApp/Data/DatabaseHelper.cs | 53 | SQL injection vulnerability in `ExecuteNonQuery` via interpolated `sql` string. | Change the method to accept parameters and use `SqlParameter` objects. |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password `AdminBypassPassword` allows backdoor access. | Remove the backdoor completely and use standard authentication for admins. |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection vulnerability in `Login` method via interpolated `username` and `hashedPassword`. | Use parameterized queries with `SqlParameter` to check credentials. |
| SampleBankingApp/Services/AuthService.cs | 61 | Weak cryptography using `MD5` for password hashing in `HashPasswordMd5`. | Use a strong hashing algorithm like PBKDF2, BCrypt, or Argon2 with a salt. |
| SampleBankingApp/Services/AuthService.cs | 91 | Weak cryptography using `SHA1` for password hashing in `HashPasswordSha1`. | Remove this method and use a strong hashing algorithm with a salt. |
| SampleBankingApp/Program.cs | 24 | JWT misconfiguration with `ValidateLifetime = false` allowing expired tokens. | Set `ValidateLifetime = true` to enforce token expiration. |
| SampleBankingApp/Program.cs | 28 | Weak JWT secret `mysecretkey` passed to `Encoding.UTF8.GetBytes` without length validation. | Use a cryptographically random secret of at least 256 bits stored securely in environment variables. |
| SampleBankingApp/Program.cs | 34 | Developer exception page called unconditionally in `Program.cs`. | Only call `UseDeveloperExceptionPage()` when in the Development environment. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out. | Uncomment `app.UseHttpsRedirection()` to enforce secure transport. |
| SampleBankingApp/Program.cs | 38 | Open CORS policy allowing any origin, method, and header. | Configure CORS to only allow specific trusted origins and required methods. |
| SampleBankingApp/Controllers/UserController.cs | 38 | Broken access control in `UpdateUser` endpoint missing ownership checks. | Verify the authenticated user matches the `id` being updated or has an admin role. |
| SampleBankingApp/Controllers/UserController.cs | 56 | Broken access control in `DeleteUser` endpoint missing ownership checks. | Verify the authenticated user matches the `id` being deleted or has an admin role. |
| SampleBankingApp/Controllers/TransactionController.cs | 48 | Broken access control in `Refund` endpoint allowing any authenticated user to refund. | Add an authorization policy to restrict refunds to administrative roles. |
| SampleBankingApp/appsettings.json | 3 | Production database connection string with credentials committed to source control. | Move secrets to environment variables or a secure secret manager like Azure Key Vault. |
| SampleBankingApp/appsettings.json | 6 | Weak JWT secret committed to source control. | Store the JWT secret in environment variables or a secure secret manager. |
| SampleBankingApp/appsettings.json | 14 | Email server password committed to source control. | Move email credentials to environment variables or a secure secret manager. |
| SampleBankingApp/Services/TransactionService.cs | 47 | SQL injection in `Transfer` method via interpolated `newFromBalance` and `fromUserId`. | Use parameterized queries for the UPDATE statement. |
| SampleBankingApp/Services/TransactionService.cs | 48 | SQL injection in `Transfer` method via interpolated `newToBalance` and `toUserId`. | Use parameterized queries for the UPDATE statement. |
| SampleBankingApp/Services/TransactionService.cs | 71 | SQL injection in `Deposit` method via interpolated `amount + interestBonus` and `userId`. | Use parameterized queries for the UPDATE statement. |
| SampleBankingApp/Services/TransactionService.cs | 89 | SQL injection in `RecordTransaction` method via interpolated values. | Use parameterized queries for the INSERT statement. |
| SampleBankingApp/Services/UserService.cs | 47 | SQL injection in `UpdateUser` method via interpolated `email`, `username`, and `id`. | Use parameterized queries for the UPDATE statement. |
| SampleBankingApp/Services/UserService.cs | 61 | SQL injection in `DeleteUser` method via interpolated `id`. | Use parameterized queries for the DELETE statement. |
| SampleBankingApp/Services/UserService.cs | 99 | SQL injection in `SearchUsers` method via interpolated `query` in LIKE clause. | Use parameterized queries with `@Query` parameter for the LIKE clause. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | Debug symbols enabled in release builds via `<DebugSymbols>true</DebugSymbols>`. | Set to false or remove for release builds to avoid leaking debug information. |
| SampleBankingApp/SampleBankingApp.csproj | 9 | Full debug type specified in release builds via `<DebugType>full</DebugType>`. | Set to `none` or `pdbonly` for release builds. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 25 | `amount < 0` check allows zero-amount transfers which are nonsensical. | Change the condition to `amount <= 0`. |
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check `fromBalance >= amount` excludes the fee, but `totalDebit` is deducted, causing negative balances. | Change the condition to `fromBalance >= totalDebit`. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Interest bonus applied as 5% via `0.05m * 1` which may be an incorrect rate or redundant constant. | Verify the intended interest rate and use a named constant. |
| SampleBankingApp/Services/TransactionService.cs | 23 | Missing self-referential check allowing a user to transfer funds to themselves. | Add a check to return an error if `fromUserId == toUserId`. |
| SampleBankingApp/Services/UserService.cs | 72 | Off-by-one error in pagination where `page * pageSize` skips the first page's worth of items. | Change the calculation to `(page - 1) * pageSize`. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/UserService.cs | 105 | `SearchUsers` catches broad `Exception` and swallows it silently, returning an empty list. | Log the exception and consider returning a specific error result instead of an empty list. |
| SampleBankingApp/Services/TransactionService.cs | 47 | Missing database transaction wrapping the two balance updates and transaction record in `Transfer`. | Wrap the writes in a `SqlTransaction` to ensure atomicity. |
| SampleBankingApp/Services/TransactionService.cs | 52 | Side effect `SendTransferNotification` can throw after DB writes have committed in `Transfer`. | Move email sending outside the transaction or use an outbox pattern to handle failures gracefully. |
| SampleBankingApp/Controllers/UserController.cs | 52 | Raw `ex.Message` returned to HTTP clients in the `UpdateUser` catch block. | Return a generic error message and log the exception details internally. |
| SampleBankingApp/Controllers/AuthController.cs | 19 | Missing rate limiting or account lockout on the `Login` endpoint. | Implement rate limiting and account lockout policies to prevent brute-force attacks. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | `SqlConnection` opened in `ExecuteQuery` but never disposed. | Wrap the connection in a `using` block. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | `SqlConnection` opened in `ExecuteNonQuery` but only closed, not disposed. | Wrap the connection in a `using` block instead of calling `Close()`. |
| SampleBankingApp/Services/AuthService.cs | 34 | `SqlConnection` opened in `Login` but never closed or disposed. | Wrap the connection in a `using` block. |
| SampleBankingApp/Services/EmailService.cs | 16 | `SmtpClient` held as an instance field, which is not thread-safe and never disposed. | Create `SmtpClient` inside a `using` block for each send operation. |
| SampleBankingApp/Services/EmailService.cs | 39 | `MailMessage` created in `SendTransferNotification` but never disposed. | Wrap the `MailMessage` in a `using` block. |
| SampleBankingApp/Services/EmailService.cs | 69 | `MailMessage` created in `SendWelcomeEmail` but never disposed. | Wrap the `MailMessage` in a `using` block. |
| SampleBankingApp/Services/EmailService.cs | 89 | `MailMessage` created in `SendWelcomeEmailHtml` but never disposed. | Wrap the `MailMessage` in a `using` block. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 28 | `_config["Jwt:SecretKey"]` passed to `Encoding.UTF8.GetBytes` with null-forgiving operator but no actual null check. | Check for null or empty string and throw an exception during startup if missing. |
| SampleBankingApp/Services/AuthService.cs | 70 | `_config["Jwt:SecretKey"]` passed to `Encoding.UTF8.GetBytes` with null-forgiving operator but no actual null check. | Validate the configuration value before using it. |
| SampleBankingApp/Services/TransactionService.cs | 36 | `fromUserTable.Rows[0]` accessed without first checking `Rows.Count > 0`. | Check the row count and return an error if the user is not found. |
| SampleBankingApp/Services/TransactionService.cs | 37 | `toUserTable.Rows[0]` accessed without first checking `Rows.Count > 0`. | Check the row count and return an error if the user is not found. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `email.Length` accessed before a null check in `IsValidEmail`. | Add a null check at the beginning of the method. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `username.Length` accessed before a null check in `IsValidUsername`. | Add a null check at the beginning of the method. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `accountNumber.Length` accessed before a null check in `MaskAccountNumber`. | Add a null check at the beginning of the method. |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | `account` accessed before a null check in `ObfuscateAccount`. | Add a null check at the beginning of the method. |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | `userIdClaim` passed to `int.Parse` with null-forgiving operator but no null check. | Check if `userIdClaim` is null and return `Unauthorized` if so. |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | `userIdClaim` passed to `int.Parse` with null-forgiving operator but no null check. | Check if `userIdClaim` is null and return `Unauthorized` if so. |
| SampleBankingApp/Services/EmailService.cs | 65 | `username.ToUpper()` called before a null check in `SendWelcomeEmail`. | Add a null check before calling `ToUpper()`. |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 59 | `TableExists` method is defined but never called. | Remove the method if not needed. |
| SampleBankingApp/Data/DatabaseHelper.cs | 68 | `ExecuteQueryWithParams` method is marked obsolete and never called. | Remove the method. |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | `IsValidEmail` method is defined but never called. | Remove the method or use it for validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | `IsValidUsername` method is defined but never called. | Remove the method or use it for validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | `JoinWithSeparator` method is defined but never called. | Remove the method. |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | `JoinWithSeparatorFixed` method is defined but never called. | Remove the method. |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | `MaskAccountNumber` method is defined but never called. | Remove the method. |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | `ObfuscateAccount` method is defined but never called. | Remove the method. |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | `ToTitleCase` method is defined but never called. | Remove the method. |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | `IsBlank` method is defined but never called. | Remove the method. |
| SampleBankingApp/Services/AuthService.cs | 91 | `HashPasswordSha1` method is defined but never called. | Remove the method. |
| SampleBankingApp/Services/AuthService.cs | 98 | `ValidateToken` method is defined but never called. | Remove the method. |
| SampleBankingApp/Services/AuthService.cs | 104 | Code after unconditional `return true;` in `ValidateToken` is unreachable. | Remove the unreachable code. |
| SampleBankingApp/Services/EmailService.cs | 63 | `SendWelcomeEmail` method is defined but never called. | Remove the method. |
| SampleBankingApp/Services/EmailService.cs | 86 | `SendWelcomeEmailHtml` method is defined but never called. | Remove the method. |
| SampleBankingApp/Services/TransactionService.cs | 77 | `IsWithinDailyLimit` method is defined but never called. | Remove the method or implement the limit check. |
| SampleBankingApp/Services/TransactionService.cs | 94 | `FormatCurrency` method is defined but never called. | Remove the method. |
| SampleBankingApp/Services/TransactionService.cs | 99 | `RefundTransaction` throws `NotImplementedException` in non-stub code. | Implement the method or remove the endpoint. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded connection string fallback in `DatabaseHelper` constructor. | Remove the magic string and require configuration. |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password string. | Remove the backdoor. |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded username "admin" and role "SuperAdmin" strings. | Remove the backdoor logic. |
| SampleBankingApp/Services/TransactionService.cs | 65 | `1000000` deposit cap is an inline magic number. | Extract to a named constant like `MaxDepositAmount`. |
| SampleBankingApp/Services/TransactionService.cs | 68 | `0.05m` interest rate is an inline magic number. | Extract to a named constant like `DepositInterestRate`. |
| SampleBankingApp/Services/UserService.cs | 22 | `1000000` user ID limit is an inline magic number. | Extract to a named constant like `MaxUserId`. |
| SampleBankingApp/Services/UserService.cs | 70 | `50` page size limit is an inline magic number. | Extract to a named constant like `MaxPageSize`. |
| SampleBankingApp/Services/EmailService.cs | 40 | `"notifications@company.com"` hardcoded email address. | Move to configuration in `appsettings.json`. |
| SampleBankingApp/Services/EmailService.cs | 67 | `"support@company.com"` hardcoded email address. | Move to configuration in `appsettings.json`. |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` hardcoded configuration. | Set to `true` or bind from configuration. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `254` email length limit is an inline magic number. | Extract to a named constant like `MaxEmailLength`. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `3` and `20` username length limits are inline magic numbers. | Extract to named constants like `MinUsernameLength` and `MaxUsernameLength`. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 31 | String concatenation inside a loop in `JoinWithSeparator` is O(n²). | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | `new Regex(...)` inside `IsValidEmail` method called repeatedly. | Make the Regex instance `static readonly`. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | `new Regex(...)` inside `IsValidUsername` method called repeatedly. | Make the Regex instance `static readonly`. |
| SampleBankingApp/Services/UserService.cs | 10 | Shared mutable static state `_auditLog` accessed from multiple threads without synchronization. | Use a thread-safe collection like `ConcurrentQueue` or lock access. |
| SampleBankingApp/Services/UserService.cs | 11 | Shared mutable static state `_requestCount` accessed from multiple threads without synchronization. | Use `Interlocked.Increment` or lock access. |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | `IsBlank` reimplements standard library method `string.IsNullOrWhiteSpace`. | Remove the method and use the standard library. |
| SampleBankingApp/Services/UserService.cs | 87 | String concatenation inside a loop in `GetAuditReport` is O(n²). | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/UserService.cs | 20 | Duplicated validation logic for user ID in `GetUserById`, `UpdateUser`, and `DeleteUser`. | Extract the validation to a shared private method. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `Transfer` method carries multiple responsibilities (fetch users, calculate fee, update balances, record transaction, send email). | Split into named private helpers like `CalculateFee`, `UpdateBalances`, and `NotifyUser`. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` called unconditionally. | Only call it in the Development environment. |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` on JWT. | Set to `true` to enforce token expiration. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out. | Uncomment `app.UseHttpsRedirection()`. |
| SampleBankingApp/Program.cs | 38 | Overly permissive CORS policy. | Restrict to specific origins and methods. |
| SampleBankingApp/appsettings.json | 18 | Debug log levels set for production namespaces. | Set to `Information` or `Warning` for production. |
| SampleBankingApp/appsettings.json | 19 | Debug log levels set for Microsoft namespace. | Set to `Information` or `Warning` for production. |
| SampleBankingApp/appsettings.json | 20 | Debug log levels set for System namespace. | Set to `Information` or `Warning` for production. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | Outdated or vulnerable NuGet package `Newtonsoft.Json 12.0.3`. | Update to the latest version or switch to `System.Text.Json`. |
| SampleBankingApp/appsettings.json | 1 | Missing environment-specific config overrides like `appsettings.Production.json`. | Add a production configuration file to override debug settings and secrets. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp | 1 | No test project exists in the solution. | Add a unit test project to cover critical business logic. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `Transfer` method lacks tests for boundary conditions, negative balances, and self-transfers. | Add tests for zero amounts, insufficient funds, self-transfers, and successful transfers. |
| SampleBankingApp/Services/TransactionService.cs | 63 | `Deposit` method lacks tests for zero, negative, and maximum cap amounts. | Add tests for boundary values around `0` and `1000000`. |
| SampleBankingApp/Services/UserService.cs | 68 | `GetUsersPage` method lacks tests for pagination off-by-one errors. | Add tests for page 1, page 2, and edge cases. |
| SampleBankingApp/Services/AuthService.cs | 28 | `Login` method lacks tests for auth flows and the admin bypass. | Add tests for valid users, invalid passwords, inactive users, and the backdoor. |