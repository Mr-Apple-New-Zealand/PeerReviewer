## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/UserController.cs | 52 | The `UpdateUser` method returns the raw exception message (`ex.Message`) to the client, potentially leaking stack traces or internal logic details. | Return a generic error message to the client and log the full exception details server-side. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | The `ExecuteQuery` method constructs a SQL query using string interpolation with `tableName` and `whereClause`, creating a severe SQL injection vulnerability. | Use parameterized queries for all inputs or restrict `tableName` to a whitelist of allowed values. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | The `ExecuteNonQuery` method accepts raw SQL and opens a connection that is not disposed in a `using` block, risking connection leaks and potential SQL injection if called with unsanitized input. | Wrap the connection and command in `using` blocks and ensure all SQL inputs are parameterized. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | The `DatabaseHelper` constructor contains a hardcoded fallback connection string with a plaintext password (`Admin1234!`). | Remove hardcoded credentials and rely strictly on configuration injection. |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, exposing detailed stack traces and internal errors to any client in any environment. | Wrap this call in `if (app.Environment.IsDevelopment()) { ... }`. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out, allowing traffic to potentially run over unencrypted HTTP. | Uncomment `app.UseHttpsRedirection()` and ensure it runs before authentication. |
| SampleBankingApp/Program.cs | 38 | CORS policy allows `AllowAnyOrigin` combined with `AllowAnyMethod`, which is overly permissive and can lead to CSRF attacks. | Restrict CORS to specific trusted origins and methods. |
| SampleBankingApp/Program.cs | 24 | JWT validation has `ValidateLifetime = false`, allowing expired tokens to be accepted indefinitely. | Set `ValidateLifetime = true` to enforce token expiration. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | Debug symbols (`DebugType: full`) are enabled in the project file, which can leak sensitive metadata if the build is deployed to production. | Set `DebugType` to `portable` or `none` for release builds. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | The project references `Newtonsoft.Json` version 12.0.3, which is outdated and may contain known vulnerabilities. | Update to the latest stable version of `Newtonsoft.Json`. |
| SampleBankingApp/Services/AuthService.cs | 17 | A hardcoded backdoor password (`SuperAdmin2024`) allows authentication as a SuperAdmin without a database record. | Remove the hardcoded backdoor logic entirely. |
| SampleBankingApp/Services/AuthService.cs | 30 | Passwords are hashed using MD5 (`HashPasswordMd5`), which is cryptographically broken and unsuitable for password storage. | Use a strong hashing algorithm like PBKDF2, bcrypt, or Argon2. |
| SampleBankingApp/Services/AuthService.cs | 32 | The `Login` method constructs a SQL query using string interpolation with user input (`username`), enabling SQL injection. | Use parameterized queries for the login check. |
| SampleBankingApp/Services/AuthService.cs | 91 | The `HashPasswordSha1` method uses SHA1, which is cryptographically weak and deprecated for password hashing. | Remove this method and ensure all password hashing uses secure algorithms. |
| SampleBankingApp/Services/AuthService.cs | 103 | The `ValidateToken` method returns `true` immediately without actually validating the token structure or signature. | Implement actual token validation logic using `JwtSecurityTokenHandler`. |
| SampleBankingApp/Services/EmailService.cs | 29 | `EnableSsl` is set to `false` for the SMTP client, transmitting credentials and email content in plaintext. | Set `EnableSsl = true` and ensure the SMTP server supports it. |
| SampleBankingApp/Services/EmailService.cs | 22 | The SMTP client is instantiated in the constructor and stored as a field, which is not thread-safe and can lead to socket exhaustion under load. | Use `IHttpClientFactory` pattern or create a new `SmtpClient` per request, or use `System.Net.Mail.SmtpClient` carefully with disposal. |
| SampleBankingApp/appsettings.json | 3 | The `appsettings.json` file contains a production database connection string with a plaintext password (`Admin1234!`). | Remove secrets from source control and use environment variables or a secret manager. |
| SampleBankingApp/appsettings.json | 6 | The JWT `SecretKey` is hardcoded in the configuration file (`mysecretkey`), which is weak and exposed in source control. | Use a strong, random secret key and store it in a secure secret manager. |
| SampleBankingApp/appsettings.json | 14 | The email password (`EmailPass99`) is hardcoded in the configuration file. | Move email credentials to environment variables or a secret manager. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | The code casts a potentially null `userIdClaim` to `int` using `int.Parse` with the null-forgiving operator `!`, which will throw an exception if the claim is missing. | Add a null check for `userIdClaim` and return a 401/403 error if the user identity is missing. |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | Similar to line 27, `int.Parse` is used on a potentially null claim without validation. | Add a null check for `userIdClaim` before parsing. |
| SampleBankingApp/Services/TransactionService.cs | 42 | The balance check `fromBalance >= amount` fails to account for the transaction fee, allowing a transfer that results in a negative balance after the fee is deducted. | Change the condition to `fromBalance >= totalDebit` where `totalDebit` includes the fee. |
| SampleBankingApp/Services/TransactionService.cs | 47 | The `UPDATE` statement for the sender's balance is constructed via string interpolation, which is a logic error regarding SQL injection safety, not just security. | Use parameterized queries for the update statement. |
| SampleBankingApp/Services/TransactionService.cs | 48 | The `UPDATE` statement for the receiver's balance is constructed via string interpolation. | Use parameterized queries for the update statement. |
| SampleBankingApp/Services/TransactionService.cs | 71 | The deposit logic adds `amount + interestBonus` to the balance, but the `interestBonus` calculation `amount * 0.05m * 1` implies a 5% bonus which may be unintended or hardcoded incorrectly. | Verify the business logic for deposit bonuses and parameterize the rate. |
| SampleBankingApp/Services/TransactionService.cs | 89 | The `RecordTransaction` method constructs an `INSERT` statement using string interpolation, risking SQL injection and logic errors if `description` contains quotes. | Use parameterized queries for the insert statement. |
| SampleBankingApp/Services/UserService.cs | 72 | The pagination logic uses `page * pageSize` instead of `(page - 1) * pageSize`, causing the first page (page 1) to skip the first `pageSize` records. | Change the calculation to `(page - 1) * pageSize`. |
| SampleBankingApp/Services/UserService.cs | 99 | The `SearchUsers` method constructs a SQL query using string interpolation with the `query` parameter, enabling SQL injection. | Use parameterized queries for the search logic. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | The `Refund` endpoint catches `NotImplementedException` and returns a 500 error, but the underlying service throws this exception, indicating incomplete functionality exposed to the client. | Return a 501 Not Implemented status code or remove the endpoint until implemented. |
| SampleBankingApp/Controllers/UserController.cs | 50 | The `UpdateUser` method catches a broad `Exception` and returns the raw message, which can leak internal details. | Catch specific exceptions or return a generic error message. |
| SampleBankingApp/Controllers/UserController.cs | 64 | The `DeleteUser` method catches a broad `Exception` and returns a generic message, but the logging is correct; however, the broad catch hides specific errors. | Catch specific exceptions relevant to the operation. |
| SampleBankingApp/Services/TransactionService.cs | 47-48 | The `Transfer` method performs two database updates without a transaction, meaning if the second update fails, the first persists, leading to data inconsistency. | Wrap the balance updates and transaction record in a database transaction. |
| SampleBankingApp/Services/TransactionService.cs | 52 | The `Transfer` method sends an email after the database updates; if the email fails, the transaction is already committed, leaving the user with a debited balance but no notification. | Handle email failures gracefully or ensure the email is sent before the transaction commits (with retry logic). |
| SampleBankingApp/Services/UserService.cs | 105 | The `SearchUsers` method catches a broad `Exception` and returns an empty list, making it impossible for the caller to distinguish between "no results" and "database error". | Log the exception and rethrow or return a specific error indicator. |
| SampleBankingApp/Services/EmailService.cs | 53 | The `SendTransferNotification` method catches `SmtpException` and retries, but the retry loop logic is flawed: it increments `attempt` and throws if `attempt >= MaxRetries`, but the loop condition is `attempt < MaxRetries`, meaning it might throw on the last attempt without retrying properly. | Refactor the retry logic to ensure it retries the correct number of times before throwing. |
| SampleBankingApp/Services/EmailService.cs | 75 | The `SendWelcomeEmail` method catches a broad `Exception` and swallows it, logging only to console, which prevents the caller from knowing the email failed. | Log the exception properly and consider rethrowing or returning a failure status. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | The `GetOpenConnection` method returns an open `SqlConnection` that the caller must close, but the caller often does not dispose of it, leading to connection leaks. | Return a `using` block or ensure the caller disposes the connection, or use `ExecuteQuerySafe` pattern. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | The `ExecuteQuery` method calls `GetOpenConnection` but never closes or disposes the returned connection. | Wrap the connection in a `using` block within the method. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | The `ExecuteNonQuery` method calls `GetOpenConnection` and closes it manually, but if an exception occurs before `Close()`, the connection remains open. | Wrap the connection in a `using` block. |
| SampleBankingApp/Services/AuthService.cs | 34 | The `Login` method creates a `SqlConnection` and opens it but never closes or disposes it, causing a connection leak. | Wrap the connection in a `using` block. |
| SampleBankingApp/Services/AuthService.cs | 38 | The `Login` method creates a `SqlDataReader` but never closes or disposes it. | Wrap the reader in a `using` block. |
| SampleBankingApp/Services/EmailService.cs | 16 | The `EmailService` holds a `SmtpClient` as a field, which is not thread-safe and holds sockets open, leading to resource exhaustion under concurrent load. | Create a new `SmtpClient` per request or use a thread-safe alternative. |
| SampleBankingApp/Services/EmailService.cs | 39 | The `SendTransferNotification` method creates a `MailMessage` but never disposes it, potentially leaking GDI handles or network resources. | Wrap the `MailMessage` in a `using` block. |
| SampleBankingApp/Services/EmailService.cs | 69 | The `SendWelcomeEmail` method creates a `MailMessage` but never disposes it. | Wrap the `MailMessage` in a `using` block. |
| SampleBankingApp/Services/EmailService.cs | 89 | The `SendWelcomeEmailHtml` method creates a `MailMessage` but never disposes it. | Wrap the `MailMessage` in a `using` block. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | `int.Parse(userIdClaim!)` will throw a `FormatException` if `userIdClaim` is null (despite the `!` operator) or not a valid integer. | Add a null check and validate the string format before parsing. |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | `int.Parse(userIdClaim!)` will throw a `FormatException` if `userIdClaim` is null or invalid. | Add a null check and validate the string format before parsing. |
| SampleBankingApp/Services/AuthService.cs | 36 | `reader.Read()` is called, but if it returns false, the code proceeds to check the backdoor, but the `reader` is not disposed, and if the query returns null, the code might access `reader["Id"]` if logic were different. | Ensure `reader` is disposed and handle the case where no rows are returned. |
| SampleBankingApp/Services/AuthService.cs | 44 | The code casts `reader["Id"]` to `int` without checking if the column exists or is null, which could throw an exception. | Use `reader.IsDBNull` or `TryGetValue` to safely access columns. |
| SampleBankingApp/Services/TransactionService.cs | 36 | The code casts `fromUserTable.Rows[0]["Balance"]` to `decimal` without checking if `Rows.Count > 0`, which will throw an `IndexOutOfRangeException` if the user is not found. | Check `Rows.Count` before accessing the first row. |
| SampleBankingApp/Services/TransactionService.cs | 37 | Similar to line 36, accessing `toUserTable.Rows[0]` without checking `Rows.Count` risks an exception. | Check `Rows.Count` before accessing the first row. |
| SampleBankingApp/Services/TransactionService.cs | 53 | The code casts `fromUserTable.Rows[0]["Email"]` to `string` without null checks, which could throw if the column is null. | Use safe casting or null-coalescing operators. |
| SampleBankingApp/Services/TransactionService.cs | 55 | The code casts `toUserTable.Rows[0]["Username"]` to `string` without null checks. | Use safe casting or null-coalescing operators. |
| SampleBankingApp/Services/UserService.cs | 34 | The code accesses `table.Rows[0]` without checking `Rows.Count`, which will throw if the user is not found (though the method returns null earlier, the logic is fragile). | Ensure `Rows.Count` is checked before accessing the row. |
| SampleBankingApp/Services/UserService.cs | 115 | The `MapRowToUser` method casts `row["Id"]` to `int` without checking for null or type mismatch. | Use safe casting or `Convert.ToInt32` with error handling. |
| SampleBankingApp/Services/UserService.cs | 116 | The `MapRowToUser` method casts `row["Username"]` to `string` without null checks. | Use safe casting or null-coalescing operators. |
| SampleBankingApp/Services/UserService.cs | 117 | The `MapRowToUser` method casts `row["Email"]` to `string` without null checks. | Use safe casting or null-coalescing operators. |
| SampleBankingApp/Services/UserService.cs | 118 | The `MapRowToUser` method casts `row["Role"]` to `string` without null checks. | Use safe casting or null-coalescing operators. |
| SampleBankingApp/Services/UserService.cs | 119 | The `MapRowToUser` method casts `row["Balance"]` to `decimal` without null checks. | Use safe casting or `Convert.ToDecimal`. |
| SampleBankingApp/Services/UserService.cs | 120 | The `MapRowToUser` method casts `row["IsActive"]` to `bool` without null checks. | Use safe casting or `Convert.ToBoolean`. |
| SampleBankingApp/Services/UserService.cs | 121 | The `MapRowToUser` method casts `row["CreatedAt"]` to `DateTime` without null checks. | Use safe casting or `Convert.ToDateTime`. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Data/DatabaseHelper.cs | 67 | The `ExecuteQueryWithParams` method is marked `[Obsolete]` but is still defined and could be called if not removed. | Remove the method entirely if it is obsolete. |
| SampleBankingApp/Helpers/StringHelper.cs | 31 | The `JoinWithSeparator` method uses inefficient string concatenation in a loop and is shadowed by `JoinWithSeparatorFixed`. | Remove `JoinWithSeparator` and use `JoinWithSeparatorFixed` or `string.Join`. |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | The `IsBlank` method reimplements logic available in `string.IsNullOrWhiteSpace`. | Replace calls to `IsBlank` with `string.IsNullOrWhiteSpace`. |
| SampleBankingApp/Services/AuthService.cs | 91 | The `HashPasswordSha1` method is defined but never called. | Remove the method. |
| SampleBankingApp/Services/AuthService.cs | 105 | The code after the `return true;` statement in `ValidateToken` is unreachable. | Remove the unreachable code block. |
| SampleBankingApp/Services/TransactionService.cs | 94 | The `FormatCurrency` method is defined but never called. | Remove the method. |
| SampleBankingApp/Services/TransactionService.cs | 99 | The `RefundTransaction` method throws `NotImplementedException` and is called by the controller, but the implementation is missing. | Implement the method or remove the endpoint. |
| SampleBankingApp/Services/EmailService.cs | 81 | The `BuildHtmlTemplate` method is defined but never called. | Remove the method. |
| SampleBankingApp/Services/EmailService.cs | 86 | The `SendWelcomeEmailHtml` method is defined but never called. | Remove the method or implement its usage. |
| SampleBankingApp/Services/UserService.cs | 11 | The `_requestCount` static field is incremented but never read or used. | Remove the field and the increment logic. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/UserController.cs | 32 | The `pageSize` default value of `20` is hardcoded; it should be configurable. | Move the default page size to configuration. |
| SampleBankingApp/Controllers/UserController.cs | 32 | The `page` default value of `1` is hardcoded; it should be validated. | Validate that `page` is at least 1. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | The email length limit `254` is hardcoded. | Define as a constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | The username length limits `3` and `20` are hardcoded. | Define as constants. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | The account number mask length `4` is hardcoded. | Define as a constant. |
| SampleBankingApp/Services/TransactionService.cs | 11 | The `TransactionFeeRate` of `0.015m` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 12 | The `MaxTransactionsPerDay` of `10` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 65 | The deposit limit `1000000` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/TransactionService.cs | 68 | The interest bonus rate `0.05m` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 22 | The user ID range limit `1000000` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 42 | The user ID range limit `1000000` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 56 | The user ID range limit `1000000` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/UserService.cs | 70 | The `pageSize` limit `50` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 13 | The `MaxRetries` of `3` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 14 | The `SmtpTimeoutMs` of `5000` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 24 | The default SMTP port `25` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 40 | The sender email `notifications@company.com` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 67 | The support email `support@company.com` is hardcoded. | Move to configuration. |
| SampleBankingApp/Services/AuthService.cs | 17 | The backdoor password `SuperAdmin2024` is hardcoded. | Remove the backdoor logic. |
| SampleBankingApp/Services/AuthService.cs | 84 | The JWT expiration `30` days is hardcoded. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 31 | The `JoinWithSeparator` method uses string concatenation in a loop (`result += ...`), which is O(n²) and inefficient. | Use `string.Join` or `StringBuilder`. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | The `IsValidEmail` method creates a new `Regex` instance on every call, which is inefficient. | Make the `Regex` instance `static readonly`. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | The `IsValidUsername` method creates a new `Regex` instance on every call. | Make the `Regex` instance `static readonly`. |
| SampleBankingApp/Services/UserService.cs | 88 | The `GetAuditReport` method uses string concatenation in a loop to build the report string. | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/TransactionService.cs | 47 | The `Transfer` method performs two separate database updates without a transaction, violating atomicity. | Wrap the updates in a transaction. |
| SampleBankingApp/Services/TransactionService.cs | 89 | The `RecordTransaction` method constructs SQL via string interpolation, mixing logic and data access. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 10 | The `_auditLog` and `_requestCount` are static fields, creating shared mutable state that is not thread-safe. | Remove static state or use thread-safe collections. |
| SampleBankingApp/Services/UserService.cs | 11 | The `_requestCount` static field is unused and serves no purpose. | Remove the field. |
| SampleBankingApp/Services/UserService.cs | 18 | The `GetUserById` method has three responsibilities: validation, database access, and mapping. | Split into private helper methods for validation and mapping. |
| SampleBankingApp/Services/UserService.cs | 38 | The `UpdateUser` method has three responsibilities: validation, database access, and audit logging. | Split into private helper methods. |
| SampleBankingApp/Services/UserService.cs | 52 | The `DeleteUser` method has three responsibilities: validation, database access, and audit logging. | Split into private helper methods. |
| SampleBankingApp/Services/UserService.cs | 68 | The `GetUsersPage` method has three responsibilities: validation, database access, and mapping. | Split into private helper methods. |
| SampleBankingApp/Services/UserService.cs | 95 | The `SearchUsers` method has three responsibilities: database access, mapping, and error handling. | Split into private helper methods. |
| SampleBankingApp/Services/EmailService.cs | 36 | The `SendTransferNotification` method constructs the email body via string concatenation. | Use `StringBuilder` or string interpolation. |
| SampleBankingApp/Services/EmailService.cs | 65 | The `SendWelcomeEmail` method constructs the email body via string concatenation. | Use `StringBuilder` or string interpolation. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, exposing errors in production. | Wrap in `if (app.Environment.IsDevelopment())`. |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` is set in JWT configuration, ignoring token expiration. | Set `ValidateLifetime = true`. |
| SampleBankingApp/Program.cs | 36 | `UseHttpsRedirection` is commented out, allowing unencrypted traffic. | Uncomment and ensure it runs before authentication. |
| SampleBankingApp/Program.cs | 38 | CORS policy allows `AllowAnyOrigin` and `AllowAnyMethod`, which is insecure. | Restrict to specific origins and methods. |
| SampleBankingApp/appsettings.json | 18 | The logging level is set to `Debug` for all namespaces, which is too verbose for production. | Set logging levels to `Information` or `Warning` for production. |
| SampleBankingApp/appsettings.json | 3 | The `appsettings.json` contains production secrets (DB password, JWT secret, email password). | Remove secrets and use environment variables or secret manager. |
| SampleBankingApp/SampleBankingApp.csproj | 7 | `TreatWarningsAsErrors` is set to `false`, allowing warnings to be ignored. | Set to `true` to enforce code quality. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `DebugSymbols` is set to `true`, which may leak debug info in production builds. | Set to `false` for release builds. |
| SampleBankingApp/SampleBankingApp.csproj | 9 | `DebugType` is set to `full`, which includes full PDB information. | Set to `portable` or `none` for release builds. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 23 | The `Transfer` method lacks unit tests for boundary conditions (e.g., insufficient funds, negative amounts, self-transfer). | Add unit tests for `Transfer` covering all edge cases. |
| SampleBankingApp/Services/TransactionService.cs | 63 | The `Deposit` method lacks unit tests for invalid amounts and interest calculation. | Add unit tests for `Deposit` covering boundary conditions. |
| SampleBankingApp/Services/UserService.cs | 18 | The `GetUserById` method lacks unit tests for invalid IDs and null results. | Add unit tests for `GetUserById` covering edge cases. |
| SampleBankingApp/Services/UserService.cs | 68 | The `GetUsersPage` method lacks unit tests for pagination logic (off-by-one errors). | Add unit tests for `GetUsersPage` covering pagination. |
| SampleBankingApp/Services/AuthService.cs | 28 | The `Login` method lacks unit tests for valid/invalid credentials and backdoor logic. | Add unit tests for `Login` covering authentication flows. |
| SampleBankingApp/Services/AuthService.cs | 68 | The `GenerateJwtToken` method lacks unit tests for token generation and claims. | Add unit tests for `GenerateJwtToken`. |
| SampleBankingApp/Controllers/TransactionController.cs | 23 | The `Transfer` endpoint lacks integration tests for authentication and authorization. | Add integration tests for the `Transfer` endpoint. |
| SampleBankingApp/Controllers/UserController.cs | 21 | The `GetUser` endpoint lacks tests for authorization and user existence. | Add integration tests for the `GetUser` endpoint. |
| SampleBankingApp/Controllers/UserController.cs | 31 | The `GetUsers` endpoint lacks tests for pagination parameters. | Add integration tests for the `GetUsers` endpoint. |
| SampleBankingApp/Services/EmailService.cs | 34 | The `SendTransferNotification` method lacks unit tests for email sending logic and retry behavior. | Add unit tests for `SendTransferNotification`. |