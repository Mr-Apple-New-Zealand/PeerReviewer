## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
|---|---|---|---|
| DatabaseHelper.cs | 30 | String interpolation builds raw SQL queries vulnerable to injection. | Use parameterized queries exclusively via `ExecuteQuerySafe`. |
| AuthService.cs | 35 | Login query uses string interpolation for credentials and bypasses hashing for admin. | Replace with parameterized queries and remove hardcoded admin bypass. |
| TransactionService.cs | 40 | Balance updates and transaction inserts use string interpolation. | Switch to parameterized commands to prevent SQL injection. |
| UserService.cs | 40 | User updates and deletions concatenate unsanitized input into SQL. | Use parameterized queries for all data modifications. |
| DatabaseHelper.cs | 12 | Fallback connection string contains hardcoded production credentials. | Remove fallback credentials and enforce config presence via validation. |
| appsettings.json | 5 | Database and email passwords are committed in plaintext. | Move secrets to environment variables or a secure secret manager. |
| AuthService.cs | 55 | Passwords are hashed using unsalted MD5 and SHA1 algorithms. | Migrate to bcrypt, Argon2, or PBKDF2 with proper salting. |
| Program.cs | 22 | JWT validation disables lifetime checks and uses a weak secret. | Enable `ValidateLifetime` and rotate to a cryptographically strong key. |
| UserController.cs | 35 | PUT and DELETE endpoints lack ownership verification. | Add authorization checks to ensure users can only modify their own records. |
| Program.cs | 30 | CORS policy allows any origin, method, and header globally. | Restrict CORS to trusted domains and required HTTP methods. |
| Program.cs | 28 | Developer exception page is enabled unconditionally. | Wrap in `app.Environment.IsDevelopment()` check. |
| Program.cs | 31 | HTTPS redirection is commented out. | Uncomment and enforce HTTPS in all environments. |

## 2. Logic Errors
| File | Line | Issue | Fix |
|---|---|---|---|
| UserService.cs | 65 | Pagination skip calculation uses `page * pageSize` instead of `(page-1) * pageSize`. | Adjust formula to `(page - 1) * pageSize` for correct zero-based offset. |
| TransactionService.cs | 45 | Balance check compares against `amount` but deducts `amount + fee`. | Change condition to `fromBalance >= totalDebit` to prevent negative balances. |
| TransactionService.cs | 35 | Transfer logic allows users to send funds to themselves. | Add validation to reject requests where `fromUserId == toUserId`. |
| TransactionService.cs | 40 | Code accesses `Rows[0]` without verifying the query returned results. | Check `Rows.Count > 0` before casting or reading data. |
| TransactionService.cs | 70 | Daily transaction limit method is defined but never invoked. | Call `IsWithinDailyLimit` before processing transfers or deposits. |
| TransactionService.cs | 55 | Deposit interest calculation multiplies by `1` unnecessarily. | Remove the redundant `* 1` multiplier for clarity. |
| UserService.cs | 60 | Page size is capped at 50 but negative or zero values are not rejected. | Add validation to ensure `page >= 1` and `pageSize > 0`. |

## 3. Error Handling
| File | Line | Issue | Fix |
|---|---|---|---|
| UserService.cs | 90 | Search method catches all exceptions and returns an empty list. | Log the exception and return a proper error response or retry. |
| EmailService.cs | 65 | Welcome email failure is silently swallowed with console output. | Use injected `ILogger` and propagate or handle failures appropriately. |
| TransactionService.cs | 40 | Multiple database writes occur without a transaction wrapper. | Wrap balance updates and transaction recording in a `SqlTransaction`. |
| TransactionService.cs | 50 | Email notification is sent after database commits without rollback handling. | Move email sending to a background job or handle failures gracefully. |
| UserController.cs | 45 | Internal server error response exposes raw exception messages to clients. | Return a generic error message and log the full details server-side. |
| AuthController.cs | 20 | Login endpoint lacks rate limiting or account lockout mechanisms. | Implement rate limiting middleware or failed attempt tracking. |

## 4. Resource Leaks
| File | Line | Issue | Fix |
|---|---|---|---|
| AuthService.cs | 35 | `SqlConnection` and `SqlDataReader` are opened but never disposed. | Wrap connection and reader in `using` statements. |
| DatabaseHelper.cs | 30 | `ExecuteQuery` returns an open connection that the caller rarely closes. | Dispose connections internally or document strict ownership transfer. |
| DatabaseHelper.cs | 45 | `ExecuteNonQuery` closes the connection but skips `Dispose()`. | Use `using` blocks to guarantee deterministic disposal. |
| EmailService.cs | 15 | `SmtpClient` is stored as a mutable instance field across requests. | Instantiate per-request or use a thread-safe connection pool. |
| EmailService.cs | 40 | `MailMessage` objects are created without disposal. | Wrap `MailMessage` in `using` blocks to release unmanaged resources. |
| DatabaseHelper.cs | 35 | `SqlDataAdapter` and `DataTable` are not disposed after use. | Add `using` statements for disposable ADO.NET objects. |

## 5. Null Reference Risks
| File | Line | Issue | Fix |
|---|---|---|---|
| TransactionController.cs | 25 | `User.FindFirst` may return null, causing `int.Parse` to throw. | Add null checks before parsing claim values. |
| TransactionController.cs | 35 | Deposit endpoint repeats the same unguarded claim parsing logic. | Extract claim parsing to a shared, null-safe helper method. |
| TransactionService.cs | 40 | Direct row access assumes query results always exist. | Validate `Rows.Count > 0` before casting database values. |
| Program.cs | 18 | JWT secret configuration value is force-unpacked without validation. | Throw a startup exception if the secret key is missing or empty. |
| EmailService.cs | 20 | SMTP host configuration may be null when passed to constructor. | Validate configuration values during service initialization. |
| AuthService.cs | 40 | Database reader casts assume columns are never null or missing. | Use `reader.IsDBNull()` checks before casting values. |

## 6. Dead Code
| File | Line | Issue | Fix |
|---|---|---|---|
| DatabaseHelper.cs | 65 | Obsolete method remains in the codebase despite deprecation warning. | Remove the obsolete method and update any lingering references. |
| AuthService.cs | 80 | `HashPasswordSha1` is defined but never called anywhere. | Delete the unused method to reduce maintenance burden. |
| AuthService.cs | 85 | `ValidateToken` returns early, leaving validation logic unreachable. | Remove the premature return or implement the intended validation. |
| TransactionService.cs | 70 | Daily limit check method is never invoked in the transaction flow. | Integrate the method into transfer/deposit logic or remove it. |
| TransactionService.cs | 85 | Currency formatting helper is defined but unused. | Delete the method or apply it to user-facing outputs. |
| StringHelper.cs | 25 | `JoinWithSeparator` uses inefficient concatenation and is likely unused. | Remove in favor of `string.Join` or the fixed variant. |
| EmailService.cs | 75 | HTML welcome email method is never called by any controller. | Remove the unused endpoint or wire it into the registration flow. |

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
|---|---|---|---|
| TransactionService.cs | 15 | Fee rate, daily limits, and deposit caps are hardcoded literals. | Extract to configuration or named constants with clear documentation. |
| UserService.cs | 60 | Page size limit and user ID bounds are hardcoded numbers. | Move thresholds to app settings or strongly-typed configuration classes. |
| AuthService.cs | 85 | Token expiration days and admin bypass credentials are inline strings. | Configure expiration via settings and remove hardcoded credentials. |
| EmailService.cs | 15 | SMTP timeouts, retry counts, and fallback ports are magic numbers. | Define as named constants or read from configuration. |
| StringHelper.cs | 10 | Email and username length limits are hardcoded integers. | Extract to configuration or well-named constants. |
| TransactionService.cs | 40 | SQL table and column names are repeated inline strings. | Centralize table/column names in a constants class or ORM mappings. |

## 8. Anti-patterns and Code Quality
| File | Line | Issue | Fix |
|---|---|---|---|
| StringHelper.cs | 25 | String concatenation inside a loop causes O(n²) performance degradation. | Replace with `string.Join` or `StringBuilder`. |
| StringHelper.cs | 10 | Regex objects are instantiated on every method call. | Cache as `static readonly` fields for reuse. |
| UserService.cs | 10 | Static audit log and request counter lack thread synchronization. | Use `ConcurrentBag` or lock statements for thread safety. |
| StringHelper.cs | 55 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Replace with the built-in framework method. |
| DatabaseHelper.cs | 20 | Helper returns open connections without clear disposal contracts. | Return `IDbConnection` wrapped in `using` or manage lifecycle internally. |
| UserService.cs | 35 | User ID validation logic is duplicated across three methods. | Extract to a shared validation attribute or helper method. |
| EmailService.cs | 60 | Console output is used for logging instead of dependency injection. | Inject `ILogger` and use structured logging throughout. |

## 9. Configuration Issues
| File | Line | Issue | Fix |
|---|---|---|---|
| Program.cs | 28 | Developer exception page is enabled unconditionally. | Guard with `app.Environment.IsDevelopment()`. |
| Program.cs | 22 | JWT lifetime validation is explicitly disabled. | Set `ValidateLifetime = true` and configure expiration. |
| Program.cs | 31 | HTTPS redirection is commented out. | Uncomment and enforce secure transport. |
| Program.cs | 30 | CORS policy is globally permissive. | Define specific allowed origins and methods. |
| appsettings.json | 15 | Logging levels are set to Debug for all namespaces. | Set Default to Information and restrict Debug to development. |
| SampleBankingApp.csproj | 12 | Newtonsoft.Json 12.0.3 contains known vulnerabilities. | Upgrade to version 13.0.1 or later. |
| SampleBankingApp.csproj | 13 | System.Data.SqlClient is deprecated and lacks modern security fixes. | Migrate to Microsoft.Data.SqlClient. |
| appsettings.json | 5 | Production secrets are stored in plaintext configuration. | Use Azure Key Vault, AWS Secrets Manager, or environment variables. |

## 10. Missing Unit Tests
| File | Line | Issue | Fix |
|---|---|---|---|
| N/A | N/A | No test project exists for the solution. | Create an xUnit or NUnit test project targeting critical services. |
| AuthService.cs | 35 | Login flow lacks tests for SQL injection, weak hashing, and admin bypass. | Add tests verifying parameterization, secure hashing, and credential validation. |
| TransactionService.cs | 35 | Transfer logic lacks tests for balance deductions, fee calculations, and concurrency. | Implement tests covering insufficient funds, fee application, and transaction rollbacks. |
| TransactionService.cs | 55 | Deposit endpoint lacks tests for limits, interest bonuses, and invalid amounts. | Add boundary tests for max deposit, zero/negative amounts, and interest application. |
| UserService.cs | 65 | Pagination lacks tests for off-by-one errors and boundary conditions. | Verify skip/offset calculations and page size caps with mock data. |
| DatabaseHelper.cs | 30 | Raw query execution lacks tests for parameterization and resource disposal. | Mock `SqlConnection` to verify parameter binding and `Dispose` calls. |
| StringHelper.cs | 10 | Validation helpers lack tests for edge cases and regex performance. | Add unit tests for max lengths, invalid characters, and regex caching. |
| Program.cs | 20 | JWT configuration lacks tests for token generation and validation parameters. | Verify issuer, audience, lifetime, and signing key configuration in integration tests. |