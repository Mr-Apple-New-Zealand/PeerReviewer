## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---:|---|---|
| DatabaseHelper.cs | 16 | Hardcoded fallback connection string contains a sa password. | Remove the fallback and require a secure configured connection string. |
| DatabaseHelper.cs | 29 | ExecuteQuery builds SQL by interpolating tableName and whereClause. | Use parameterized queries and a whitelist for table names. |
| DatabaseHelper.cs | 36 | ExecuteQuerySafe accepts an arbitrary SQL string that callers could populate with user input. | Restrict it to fixed statements or use a command builder. |
| AuthService.cs | 32 | Login interpolates username and hashed password into a SQL query. | Use a parameterized query for authentication. |
| AuthService.cs | 30 | HashPasswordMd5 uses MD5 for password hashing. | Use a modern salted algorithm such as PBKDF2, BCrypt, or Argon2. |
| AuthService.cs | 53 | Login contains a hardcoded admin bypass password. | Remove the backdoor and require normal credential validation. |
| AuthService.cs | 55 | The admin bypass creates a SuperAdmin user with Id 0. | Remove the bypass user creation. |
| AuthService.cs | 91 | HashPasswordSha1 uses weak SHA1 hashing. | Remove the unused weak hashing method. |
| Program.cs | 24 | ValidateLifetime is false so expired tokens are accepted. | Set ValidateLifetime to true. |
| Program.cs | 28 | jwtSecret is null-forgiven and can create an empty signing key. | Validate the secret at startup and fail if missing. |
| Program.cs | 38 | CORS allows any origin, method, and header. | Restrict CORS to trusted origins and required methods. |
| Program.cs | 34 | UseDeveloperExceptionPage is enabled unconditionally. | Enable it only in Development. |
| Program.cs | 36 | HTTPS redirection is commented out. | Enable HTTPS redirection. |
| SampleBankingApp.csproj | 8 | DebugSymbols is true for all build configurations. | Condition debug symbols on the Debug configuration. |
| SampleBankingApp.csproj | 9 | DebugType full is set for all build configurations. | Condition full debug types on the Debug configuration. |
| appsettings.json | 3 | The production database connection string contains a sa password. | Move credentials to a secret store or environment variables. |
| appsettings.json | 6 | The JWT secret key is weak and committed to source. | Use a strong secret from a secure store. |
| appsettings.json | 14 | The SMTP password is committed to source. | Move the SMTP password to a secure store. |
| EmailService.cs | 29 | EnableSsl is false so SMTP traffic is unencrypted. | Enable TLS for SMTP. |
| TransactionService.cs | 47 | The source balance UPDATE interpolates values into SQL. | Use a parameterized UPDATE command. |
| TransactionService.cs | 48 | The destination balance UPDATE interpolates values into SQL. | Use a parameterized UPDATE command. |
| TransactionService.cs | 90 | RecordTransaction interpolates description and other values into SQL. | Use a parameterized INSERT command. |
| UserService.cs | 47 | UpdateUser interpolates email and username into SQL. | Use a parameterized UPDATE command. |
| UserService.cs | 61 | DeleteUser interpolates the user id into SQL. | Use a parameterized DELETE command. |
| UserService.cs | 99 | SearchUsers interpolates query into a LIKE clause. | Use a parameterized LIKE query. |
| UserController.cs | 24 | GetUser allows any authenticated user to read any user. | Add ownership or admin role checks. |
| UserController.cs | 34 | GetUsers exposes all users to any authenticated user. | Restrict the endpoint to administrators. |
| UserController.cs | 43 | UpdateUser allows any authenticated user to update any user. | Add ownership or admin role checks. |
| UserController.cs | 61 | DeleteUser allows any authenticated user to delete any user. | Add ownership or admin role checks. |
| UserController.cs | 74 | SearchUsers exposes user data to any authenticated user. | Restrict the endpoint to administrators. |
| UserController.cs | 81 | GetAuditLog exposes the audit log to any authenticated user. | Restrict the endpoint to administrators. |
| TransactionController.cs | 53 | Refund allows any authenticated user to refund any transaction. | Add ownership or admin role checks. |
| User.cs | 7 | The User model exposes a Password property that can be serialized. | Remove the property or mark it non-serializable. |
| SampleBankingApp.csproj | 14 | System.Data.SqlClient 4.8.6 is a legacy package. | Replace it with Microsoft.Data.SqlClient. |
| SampleBankingApp.csproj | 15 | Newtonsoft.Json 12.0.3 is outdated. | Upgrade to a current supported version. |
| SampleBankingApp.csproj | 16 | System.IdentityModel.Tokens.Jwt 7.0.0 is outdated. | Upgrade to a current supported version. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---:|---|---|
| TransactionService.cs | 42 | Transfer checks balance against amount but deducts amount plus fee. | Check balance against totalDebit before debiting. |
| TransactionService.cs | 25 | Transfer allows zero amount because only negative values are rejected. | Require amount to be greater than zero. |
| TransactionService.cs | 23 | Transfer lacks a self-transfer check. | Reject transfers where fromUserId equals toUserId. |
| TransactionService.cs | 50 | RecordTransaction stores only amount and omits the fee. | Store fee and total debit in the transaction record. |
| TransactionService.cs | 73 | Deposit records only the principal and omits the interest bonus. | Store the bonus and final credited amount. |
| TransactionService.cs | 68 | Deposit applies a 5 percent bonus with an unclear constant. | Use a named configured rate and confirm the business rule. |
| TransactionService.cs | 70 | Deposit updates the balance without verifying the user exists. | Check the affected row count after the update. |
| UserService.cs | 72 | GetUsersPage calculates skip as page times pageSize. | Use (page - 1) times pageSize for zero-based offset. |
| UserService.cs | 68 | GetUsersPage does not validate page or pageSize boundaries. | Validate page at least 1 and pageSize positive. |
| UserService.cs | 22 | GetUserById rejects ids above an arbitrary one million limit. | Remove the arbitrary cap or make it configurable. |
| UserService.cs | 42 | UpdateUser rejects ids above an arbitrary one million limit. | Remove the arbitrary cap or make it configurable. |
| UserService.cs | 56 | DeleteUser rejects ids above an arbitrary one million limit. | Remove the arbitrary cap or make it configurable. |
| AuthService.cs | 53 | The admin bypass executes after normal authentication fails. | Remove the bypass logic entirely. |
| AuthService.cs | 103 | ValidateToken returns true before performing validation. | Remove the early return and validate the token. |
| TransactionService.cs | 77 | IsWithinDailyLimit is defined but never called. | Call the limit check inside Transfer. |
| StringHelper.cs | 33 | JoinWithSeparator appends a trailing separator after every item. | Use string.Join or remove the trailing separator. |
| StringHelper.cs | 56 | ObfuscateAccount assumes the account has at least four characters. | Guard against null or short input. |
| TransactionController.cs | 27 | Transfer parses the user claim without validating its format. | Validate the claim before parsing. |
| TransactionController.cs | 41 | Deposit parses the user claim without validating its format. | Validate the claim before parsing. |
| EmailService.cs | 46 | SendTransferNotification retries only SmtpException failures. | Catch and handle the expected failure types consistently. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---:|---|---|
| AuthController.cs | 20 | Login has no rate limiting or account lockout. | Add throttling and lockout for failed attempts. |
| AuthController.cs | 22 | Login does not handle database exceptions. | Catch exceptions and return a generic error response. |
| TransactionController.cs | 27 | Transfer can throw FormatException from int.Parse. | Wrap parsing in validation or try-catch. |
| TransactionController.cs | 41 | Deposit can throw FormatException from int.Parse. | Wrap parsing in validation or try-catch. |
| TransactionController.cs | 53 | Refund only catches NotImplementedException. | Handle service exceptions and return appropriate errors. |
| UserController.cs | 50 | UpdateUser catches broad Exception and returns ex.Message. | Log the exception and return a generic message. |
| UserController.cs | 64 | DeleteUser catches broad Exception. | Catch specific exceptions or log and return a generic message. |
| UserService.cs | 105 | SearchUsers catches Exception and returns an empty list. | Log the error and propagate a distinguishable failure. |
| EmailService.cs | 75 | SendWelcomeEmail catches Exception and swallows it. | Log the failure and decide whether to retry. |
| EmailService.cs | 53 | SendTransferNotification catches only SmtpException and logs to console. | Use a logger and handle expected exceptions. |
| EmailService.cs | 91 | SendWelcomeEmailHtml has no exception handling. | Add try-catch or let a global handler manage it. |
| TransactionService.cs | 47 | Transfer performs two balance updates and an insert without a transaction. | Wrap the writes in a database transaction. |
| TransactionService.cs | 52 | Transfer sends email after database writes have completed. | Queue the email or handle failure without undoing committed data. |
| TransactionService.cs | 70 | Deposit performs an update and insert without a transaction. | Wrap the writes in a database transaction. |
| UserService.cs | 48 | UpdateUser does not check the affected row count. | Verify that the update affected one row. |
| UserService.cs | 62 | DeleteUser does not check the affected row count. | Verify that the delete affected one row. |
| TransactionService.cs | 102 | RefundTransaction throws NotImplementedException in production. | Implement the method or disable the endpoint. |
| Program.cs | 34 | The developer exception page can expose stack traces to clients. | Use an environment-specific exception page. |
| DatabaseHelper.cs | 54 | ExecuteNonQuery does not manage exceptions or transactions. | Provide transaction support and safe disposal. |
| TransactionService.cs | 36 | Transfer assumes both user rows exist. | Validate row counts before accessing rows. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---:|---|---|
| DatabaseHelper.cs | 19 | GetOpenConnection returns an open connection with unclear ownership. | Return a disposable wrapper or require caller disposal. |
| DatabaseHelper.cs | 28 | ExecuteQuery does not dispose the connection, command, or adapter. | Use using statements for all disposable objects. |
| DatabaseHelper.cs | 52 | ExecuteNonQuery closes the connection but does not dispose it. | Use a using statement for the connection. |
| DatabaseHelper.cs | 54 | ExecuteNonQuery can leak the connection if the command throws before Close. | Use a using statement for the connection. |
| DatabaseHelper.cs | 44 | ExecuteQuerySafe does not dispose the SqlDataAdapter. | Use a using statement for the adapter. |
| DatabaseHelper.cs | 74 | ExecuteQueryWithParams does not dispose the SqlDataAdapter. | Use a using statement for the adapter. |
| AuthService.cs | 34 | Login creates a SqlConnection without using. | Wrap the connection in a using statement. |
| AuthService.cs | 37 | Login creates a SqlCommand without using. | Wrap the command in a using statement. |
| AuthService.cs | 38 | Login creates a SqlDataReader without using. | Wrap the reader in a using statement. |
| EmailService.cs | 16 | SmtpClient is stored as an instance field and never disposed. | Dispose the client or create it per send. |
| EmailService.cs | 22 | The shared SmtpClient is not thread-safe. | Create a client per operation or synchronize access. |
| EmailService.cs | 39 | SendTransferNotification creates a MailMessage without disposing it. | Use a using statement for the MailMessage. |
| EmailService.cs | 69 | SendWelcomeEmail creates a MailMessage without disposing it. | Use a using statement for the MailMessage. |
| EmailService.cs | 89 | SendWelcomeEmailHtml creates a MailMessage without disposing it. | Use a using statement for the MailMessage. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---:|---|---|
| Program.cs | 28 | jwtSecret can be null if the configuration key is missing. | Null-check the secret before creating the key. |
| AuthService.cs | 34 | GetConnectionString can return null. | Validate the connection string before creating a connection. |
| AuthService.cs | 70 | Jwt:SecretKey can be null. | Validate the configuration value before use. |
| AuthService.cs | 81 | Jwt:Issuer can be null. | Validate the configuration value before use. |
| AuthService.cs | 82 | Jwt:Audience can be null. | Validate the configuration value before use. |
| TransactionController.cs | 27 | userIdClaim can be null. | Check the claim before parsing. |
| TransactionController.cs | 41 | userIdClaim can be null. | Check the claim before parsing. |
| TransactionService.cs | 36 | fromUserTable.Rows[0] is accessed without checking row count. | Check Rows.Count before accessing the row. |
| TransactionService.cs | 37 | toUserTable.Rows[0] is accessed without checking row count. | Check Rows.Count before accessing the row. |
| TransactionService.cs | 53 | fromUserTable.Rows[0] is accessed again for email. | Reuse a validated row or check row count. |
| TransactionService.cs | 55 | toUserTable.Rows[0] is accessed again for username. | Reuse a validated row or check row count. |
| TransactionService.cs | 83 | IsWithinDailyLimit accesses Rows[0] without checking row count. | Check Rows.Count before accessing the row. |
| StringHelper.cs | 13 | IsValidEmail calls email.Length before a null check. | Add a null guard at the start. |
| StringHelper.cs | 22 | IsValidUsername calls username.Length before a null check. | Add a null guard at the start. |
| StringHelper.cs | 45 | MaskAccountNumber calls accountNumber.Length before a null check. | Add a null guard at the start. |
| StringHelper.cs | 56 | ObfuscateAccount uses account[^4..] without null or length checks. | Guard against null and short input. |
| EmailService.cs | 22 | Email:SmtpHost can be null. | Validate the SMTP host configuration. |
| EmailService.cs | 65 | SendWelcomeEmail calls username.ToUpper() without a null check. | Guard against null username. |
| EmailService.cs | 88 | SendWelcomeEmailHtml uses username without a null check. | Guard against null username. |
| UserController.cs | 74 | SearchUsers accepts a nullable query. | Default the query to an empty string. |
| UserController.cs | 43 | UpdateUser uses request without a null check. | Validate the request body. |
| TransactionController.cs | 29 | Transfer uses request without a null check. | Validate the request body. |
| TransactionController.cs | 43 | Deposit uses request without a null check. | Validate the request body. |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---:|---|---|
| DatabaseHelper.cs | 59 | TableExists has no caller in the provided source. | Remove the method or add a caller. |
| DatabaseHelper.cs | 68 | ExecuteQueryWithParams is obsolete and has no caller. | Remove the obsolete method. |
| StringHelper.cs | 11 | IsValidEmail has no caller in the provided source. | Remove the method or add a caller. |
| StringHelper.cs | 20 | IsValidUsername has no caller in the provided source. | Remove the method or add a caller. |
| StringHelper.cs | 29 | JoinWithSeparator has no caller in the provided source. | Remove the method or add a caller. |
| StringHelper.cs | 38 | JoinWithSeparatorFixed has no caller in the provided source. | Remove the duplicate helper. |
| StringHelper.cs | 43 | MaskAccountNumber has no caller in the provided source. | Remove the method or add a caller. |
| StringHelper.cs | 54 | ObfuscateAccount has no caller in the provided source. | Remove the method or add a caller. |
| StringHelper.cs | 59 | ToTitleCase has no caller in the provided source. | Remove the method or add a caller. |
| StringHelper.cs | 65 | IsBlank has no caller in the provided source. | Remove the method or add a caller. |
| AuthService.cs | 91 | HashPasswordSha1 has no caller in the provided source. | Remove the unused method. |
| AuthService.cs | 98 | ValidateToken has no caller in the provided source. | Remove the method or add a caller. |
| AuthService.cs | 105 | Code after the unconditional return in ValidateToken is unreachable. | Remove the unreachable validation code. |
| EmailService.cs | 63 | SendWelcomeEmail has no caller in the provided source. | Remove the method or add a caller. |
| EmailService.cs | 86 | SendWelcomeEmailHtml has no caller in the provided source. | Remove the method or add a caller. |
| EmailService.cs | 81 | BuildHtmlTemplate is only called by the unused SendWelcomeEmailHtml. | Remove both methods. |
| TransactionService.cs | 77 | IsWithinDailyLimit has no caller in the provided source. | Remove the method or call it in Transfer. |
| TransactionService.cs | 94 | FormatCurrency has no caller in the provided source. | Remove the method or add a caller. |
| TransactionService.cs | 99 | RefundTransaction throws NotImplementedException in non-stub code. | Implement the method or remove the endpoint. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---:|---|---|
| DatabaseHelper.cs | 16 | The fallback connection string is a hardcoded literal. | Remove the literal and require configuration. |
| AuthService.cs | 17 | AdminBypassPassword is a hardcoded credential literal. | Remove the backdoor password. |
| AuthService.cs | 32 | The login SQL contains hardcoded table and column literals. | Use constants or a query builder. |
| AuthService.cs | 53 | The admin username literal admin is hardcoded. | Remove the hardcoded admin check. |
| AuthService.cs | 55 | The SuperAdmin role literal is hardcoded. | Remove the hardcoded role assignment. |
| AuthService.cs | 84 | The token expiry uses a hardcoded 30 day value. | Use a named constant or configuration value. |
| TransactionService.cs | 65 | The deposit cap uses a hardcoded 1000000 value. | Use a named constant or configuration value. |
| TransactionService.cs | 68 | The deposit bonus uses hardcoded 0.05m and 1 values. | Use named constants or configuration values. |
| TransactionService.cs | 50 | The transaction type Transfer is a hardcoded string. | Use a named constant. |
| TransactionService.cs | 73 | The transaction type Deposit is a hardcoded string. | Use a named constant. |
| TransactionService.cs | 90 | The transaction status Completed is a hardcoded string. | Use a named constant. |
| UserService.cs | 22 | GetUserById uses a hardcoded one million id cap. | Use a named constant or configuration value. |
| UserService.cs | 42 | UpdateUser uses a hardcoded one million id cap. | Use a named constant or configuration value. |
| UserService.cs | 56 | DeleteUser uses a hardcoded one million id cap. | Use a named constant or configuration value. |
| UserService.cs | 70 | GetUsersPage uses a hardcoded page size cap of 50. | Use a named constant or configuration value. |
| StringHelper.cs | 13 | IsValidEmail uses a hardcoded 254 length limit. | Use a named constant. |
| StringHelper.cs | 22 | IsValidUsername uses hardcoded 3 and 20 length limits. | Use named constants. |
| StringHelper.cs | 45 | MaskAccountNumber uses a hardcoded 4 character mask length. | Use a named constant. |
| StringHelper.cs | 56 | ObfuscateAccount uses a hardcoded 4 character suffix length. | Use a named constant. |
| EmailService.cs | 40 | The sender address notifications@company.com is hardcoded. | Move the sender address to configuration. |
| EmailService.cs | 67 | The support address support@company.com is hardcoded. | Move the support address to configuration. |
| EmailService.cs | 69 | The sender address is hardcoded again. | Reuse a configured sender address. |
| EmailService.cs | 89 | The sender address is hardcoded again. | Reuse a configured sender address. |
| Program.cs | 16 | The configuration key Jwt:SecretKey is a repeated literal. | Use a named configuration key constant. |
| Program.cs | 26 | The configuration key Jwt:Issuer is a literal. | Use a named configuration key constant. |
| Program.cs | 27 | The configuration key Jwt:Audience is a literal. | Use a named configuration key constant. |
| Program.cs | 28 | The configuration key Jwt:SecretKey is repeated. | Use a named configuration key constant. |
| UserController.cs | 52 | The HTTP status code 500 is a literal. | Use a named status constant or ProblemDetails. |
| TransactionController.cs | 58 | The HTTP status code 500 is a literal. | Use a named status constant or ProblemDetails. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---:|---|---|
| StringHelper.cs | 33 | JoinWithSeparator uses string concatenation inside a loop. | Use string.Join for linear performance. |
| StringHelper.cs | 16 | IsValidEmail creates a Regex on every call. | Use a static readonly Regex field. |
| StringHelper.cs | 25 | IsValidUsername creates a Regex on every call. | Use a static readonly Regex field. |
| StringHelper.cs | 65 | IsBlank reimplements string.IsNullOrWhiteSpace. | Use the built-in method. |
| StringHelper.cs | 38 | JoinWithSeparatorFixed duplicates the built-in string.Join. | Remove the duplicate helper. |
| UserService.cs | 90 | GetAuditReport uses string concatenation inside a loop. | Use StringBuilder or string.Join. |
| UserService.cs | 10 | The static _auditLog list is shared mutable state without synchronization. | Use a thread-safe collection or persistent store. |
| UserService.cs | 11 | The static _requestCount integer is shared mutable state without synchronization. | Use Interlocked or remove the counter. |
| DatabaseHelper.cs | 19 | GetOpenConnection leaks resource ownership to callers. | Encapsulate connection disposal inside DatabaseHelper. |
| UserService.cs | 20 | GetUserById repeats the id validation block. | Extract a shared ValidateUserId helper. |
| UserService.cs | 40 | UpdateUser repeats the id validation block. | Extract a shared ValidateUserId helper. |
| UserService.cs | 54 | DeleteUser repeats the id validation block. | Extract a shared ValidateUserId helper. |
| AuthService.cs | 28 | Login combines hashing, querying, mapping, and admin bypass. | Split the method into focused helpers. |
| TransactionService.cs | 23 | Transfer combines validation, fetching, fee calculation, updates, recording, and email. | Split the method into focused helpers. |
| TransactionService.cs | 63 | Deposit combines validation, bonus calculation, update, and recording. | Split the method into focused helpers. |
| UserService.cs | 68 | GetUsersPage combines validation, skip calculation, querying, and mapping. | Split the method into focused helpers. |
| EmailService.cs | 34 | SendTransferNotification combines body creation, message creation, and retry logic. | Split the method into focused helpers. |
| EmailService.cs | 63 | SendWelcomeEmail combines body creation, sending, and exception handling. | Split the method into focused helpers. |
| EmailService.cs | 55 | SendTransferNotification uses Console.WriteLine for diagnostics. | Use an injected logger. |
| EmailService.cs | 77 | SendWelcomeEmail uses Console.WriteLine for diagnostics. | Use an injected logger. |
| DatabaseHelper.cs | 29 | ExecuteQuery uses SELECT * and raw SQL fragments. | Use explicit columns and parameterized queries. |
| TransactionService.cs | 47 | The balance update uses string interpolation instead of parameters. | Use a parameterized command. |
| UserService.cs | 47 | The user update uses string interpolation instead of parameters. | Use a parameterized command. |
| UserController.cs | 48 | UpdateUser returns raw exception text to the client. | Return a generic error and log details. |
| Program.cs | 38 | The CORS policy is configured inline with permissive options. | Define a named restricted policy. |
| EmailService.cs | 16 | The SmtpClient instance field is shared across requests. | Create a client per send or make it thread-safe. |
| TransactionService.cs | 12 | MaxTransactionsPerDay is an unused constant. | Remove it or use it in Transfer. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---:|---|---|
| Program.cs | 34 | UseDeveloperExceptionPage is called unconditionally. | Enable it only in the Development environment. |
| Program.cs | 24 | ValidateLifetime is set to false. | Set ValidateLifetime to true. |
| Program.cs | 36 | HTTPS redirection is commented out. | Enable HTTPS redirection. |
| Program.cs | 38 | CORS allows any origin, method, and header. | Configure a restrictive named CORS policy. |
| appsettings.json | 18 | The Default log level is Debug. | Use Information or Warning for production. |
| appsettings.json | 19 | The Microsoft log level is Debug. | Use Information or Warning for production. |
| appsettings.json | 20 | The System log level is Debug. | Use Information or Warning for production. |
| SampleBankingApp.csproj | 14 | System.Data.SqlClient 4.8.6 is outdated. | Replace it with Microsoft.Data.SqlClient. |
| SampleBankingApp.csproj | 15 | Newtonsoft.Json 12.0.3 is outdated. | Upgrade to a current supported version. |
| SampleBankingApp.csproj | 16 | System.IdentityModel.Tokens.Jwt 7.0.0 is outdated. | Upgrade to a current supported version. |
| SampleBankingApp.csproj | 8 | DebugSymbols is true for all configurations. | Condition it on the Debug configuration. |
| SampleBankingApp.csproj | 9 | DebugType full is set for all configurations. | Condition it on the Debug configuration. |
| appsettings.json | 23 | AllowedHosts uses a wildcard. | Restrict allowed hosts for production. |
| appsettings.json | 12 | The SMTP port is 25 without TLS configuration. | Use a TLS-enabled SMTP port. |
| appsettings.json | 3 | The base configuration contains a production connection string. | Move production values to appsettings.Production.json or secrets. |
| Repository | N/A | No appsettings.Production.json file is present. | Add production-specific configuration overrides. |
| Program.cs | 16 | The JWT secret is read without validation. | Validate the secret length and presence at startup. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---:|---|---|
| Repository | N/A | No test project exists in the provided source. | Add a test project for the application. |
| AuthService.cs | 28 | No test project covers Login authentication scenarios. | Add tests for valid, invalid, inactive, and injection attempts. |
| AuthService.cs | 68 | No test project covers GenerateJwtToken. | Add tests for claims, issuer, audience, and expiry. |
| AuthService.cs | 98 | No test project covers ValidateToken. | Add tests for valid, expired, and malformed tokens. |
| TransactionService.cs | 23 | No test project covers Transfer financial logic. | Add tests for fee, insufficient funds, self transfer, and zero amount. |
| TransactionService.cs | 63 | No test project covers Deposit calculations. | Add tests for zero, negative, cap, and interest bonus. |
| TransactionService.cs | 99 | No test project covers RefundTransaction. | Add tests for refund behavior once implemented. |
| UserService.cs | 18 | No test project covers GetUserById boundaries. | Add tests for invalid, out-of-range, and missing ids. |
| UserService.cs | 38 | No test project covers UpdateUser validation. | Add tests for invalid ids and malicious input. |
| UserService.cs | 52 | No test project covers DeleteUser validation. | Add tests for invalid ids and missing users. |
| UserService.cs | 68 | No test project covers GetUsersPage pagination. | Add tests for first page, second page, and page size cap. |
| UserService.cs | 95 | No test project covers SearchUsers. | Add tests for matches, no matches, and exception handling. |
| StringHelper.cs | 11 | No test project covers IsValidEmail. | Add tests for valid, invalid, null, and boundary lengths. |
| StringHelper.cs | 20 | No test project covers IsValidUsername. | Add tests for valid, invalid, null, and boundary lengths. |
| StringHelper.cs | 29 | No test project covers JoinWithSeparator. | Add tests for empty, single, and multiple items. |
| StringHelper.cs | 43 | No test project covers MaskAccountNumber. | Add tests for short, long, and null input. |
| StringHelper.cs | 54 | No test project covers ObfuscateAccount. | Add tests for short, long, and null input. |
| EmailService.cs | 34 | No test project covers SendTransferNotification retries. | Add tests for success, retry, and final failure. |
| EmailService.cs | 63 | No test project covers SendWelcomeEmail exception handling. | Add tests for success and failure. |
| DatabaseHelper.cs | 59 | No test project covers TableExists. | Add tests for existing and missing tables. |
| DatabaseHelper.cs | 36 | No test project covers ExecuteQuerySafe. | Add tests for parameter binding and empty results. |