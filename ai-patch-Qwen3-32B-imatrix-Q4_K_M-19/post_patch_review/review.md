## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 15 | Hardcoded fallback credentials in connection string. | Remove hardcoded credentials and require environment variables. |
| AuthService.cs | 68 | Uses MD5 for password hashing, which is cryptographically broken. | Use a modern hashing algorithm like BCrypt or Argon2. |
| AuthService.cs | 68 | Passwords are hashed without a salt, making them vulnerable to rainbow table attacks. | Implement salted hashing using a library like BCrypt.Net. |
| TransactionController.cs | 38 | Refund endpoint lacks ownership verification, allowing any authenticated user to refund any transaction. | Add logic to verify the requesting user owns the transaction or is an Admin. |
| UserController.cs | 38 | `GetUser` endpoint lacks ownership checks, allowing users to view other users' data. | Add authorization logic to restrict access to own data or Admin role. |
| Program.cs | 38 | JWT secret key is loaded from config but not validated for minimum length or strength. | Validate JWT secret length and complexity in startup configuration. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 58 | Transaction fee is deducted from balance but not recorded in the transaction log. | Update `RecordTransaction` to include fee or log fee separately. |
| TransactionService.cs | 88 | Deposit interest bonus is added to balance but not reflected in the transaction record amount. | Ensure transaction record reflects the total credited amount including interest. |
| UserService.cs | 12 | `ValidateUserId` throws exception for IDs > 1,000,000, which is an arbitrary and likely incorrect limit. | Remove or increase the upper bound check based on actual database constraints. |
| TransactionController.cs | 14 | `int.Parse` on `userIdClaim` will throw if claim is missing or non-numeric, causing a 500 error. | Add null/empty checks and use `int.TryParse` with appropriate error handling. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 48 | Catches broad `Exception` and returns null, masking database errors during login. | Log the exception and return a generic failure message without exposing details. |
| TransactionService.cs | 78 | Catches broad `Exception` and returns generic error, hiding specific transaction failures. | Log the exception and return a more specific error code or message. |
| EmailService.cs | 32 | Catches `SmtpException` and prints to console, which is not persistent or observable in production. | Use a proper logging framework to record email failures. |
| TransactionController.cs | 39 | Catches `NotImplementedException` specifically, which is poor practice for error handling. | Remove the try-catch block and implement the feature or return a proper 501 status. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 19 | `GetOpenConnection` returns an open connection without disposing it, leaking resources. | Use `using` statements or ensure callers dispose the connection. |
| TransactionService.cs | 55 | Opens a new connection for transaction updates while previous queries used separate connections. | Reuse the same connection instance for all operations within a transaction. |
| EmailService.cs | 28 | `MailMessage` is disposed in `finally`, but `SmtpClient` is not disposed if an exception occurs before `Send`. | Wrap `SmtpClient` in a `using` statement to ensure disposal. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 14 | `userIdClaim` can be null, causing `int.Parse` to throw `NullReferenceException`. | Add null check before parsing the claim value. |
| TransactionController.cs | 27 | `userIdClaim` can be null, causing `int.Parse` to throw `NullReferenceException`. | Add null check before parsing the claim value. |
| AuthService.cs | 78 | `_config["Jwt:SecretKey"]` can be null, causing `GetBytes` to throw. | Add null check or use `GetValue<string>` with a default. |
| EmailService.cs | 29 | `_config["Email:SmtpPort"]` can be null, causing `int.Parse` to throw. | Add null check or use `GetValue<int>` with a default. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| StringHelper.cs | 38 | `JoinWithSeparatorFixed` is a duplicate of `string.Join` and is never called. | Remove the method as it adds no value. |
| StringHelper.cs | 56 | `ObfuscateAccount` is a duplicate of `MaskAccountNumber` and is never called. | Remove the method to avoid confusion. |
| StringHelper.cs | 66 | `IsBlank` duplicates `string.IsNullOrWhiteSpace` and is never called. | Remove the method and use the standard library equivalent. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 52 | Fee rate and max deposit are read from config but not validated or documented. | Define constants or configuration keys with clear documentation. |
| UserService.cs | 45 | Page size limit of 50 is hardcoded. | Move to configuration or define a constant. |
| AuthService.cs | 75 | Token expiration of 30 days is hardcoded. | Move to configuration for flexibility. |
| DatabaseHelper.cs | 15 | Default connection string contains hardcoded server and database names. | Move to configuration or environment variables. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| StringHelper.cs | 28 | `new Regex` is created on every call, causing performance issues. | Use `static readonly Regex` for pattern matching. |
| StringHelper.cs | 33 | String concatenation in a loop is O(n²). | Use `string.Join` or `StringBuilder`. |
| TransactionService.cs | 55 | Multiple database queries are executed separately instead of using a single transaction. | Combine queries into a single transaction for atomicity. |
| AuthService.cs | 68 | MD5 hashing is implemented manually instead of using a library. | Use a established library like BCrypt.Net. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 38 | JWT secret key is not validated for presence or strength. | Add validation to ensure secret key is present and secure. |
| Program.cs | 48 | CORS policy allows any method and header, which is overly permissive. | Restrict allowed methods and headers to only those needed. |
| SampleBankingApp.csproj | 10 | `TreatWarningsAsErrors` is set to false, reducing code quality enforcement. | Set to true to enforce stricter compilation standards. |
| SampleBankingApp.csproj | 15 | `Newtonsoft.Json` version 12.0.3 is outdated and may have vulnerabilities. | Update to the latest stable version. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists for the application. | Create a test project with unit tests for all service methods. |
| TransactionService.cs | N/A | Financial calculations for transfers and deposits are not tested. | Add tests for balance updates, fee calculations, and interest bonuses. |
| AuthService.cs | N/A | Login and token generation logic are not tested. | Add tests for successful/failed logins and token validity. |
| UserService.cs | N/A | User CRUD operations and pagination are not tested. | Add tests for user retrieval, updates, deletions, and pagination. |