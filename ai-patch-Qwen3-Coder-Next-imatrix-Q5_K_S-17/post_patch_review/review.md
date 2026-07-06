## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 33 | `ExecuteQuery` concatenates user input into SQL string, causing SQL injection. | Use parameterized queries exclusively; remove or deprecate `ExecuteQuery`. |
| DatabaseHelper.cs | 14 | Hardcoded fallback credentials (`sa`/`Admin1234!`) in constructor. | Remove hardcoded credentials; fail fast if connection string is missing. |
| AuthService.cs | 46 | Passwords hashed with SHA-256 without salt, vulnerable to rainbow table attacks. | Use ASP.NET Core Identity or BCrypt/PBKDF2 with unique salts. |
| AuthService.cs | 82 | JWT signing key falls back to a hardcoded weak secret if env var is missing. | Fail application startup if `JWT_SECRET_KEY` is not configured securely. |
| TransactionController.cs | 53 | `Refund` endpoint lacks ownership/admin checks, allowing any authenticated user to refund any transaction. | Add authorization logic to verify the caller owns the transaction or is an Admin. |
| UserController.cs | 73 | `SearchUsers` and `GetAuditLog` lack `[Authorize]` or specific role restrictions. | Add `[Authorize]` and restrict `GetAuditLog` to Admins only. |
| Program.cs | 42 | CORS policy allows any method and header, potentially increasing attack surface. | Restrict `AllowAnyMethod`/`AllowAnyHeader` to specific required methods/headers. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 48 | `Transfer` uses a new connection for updates instead of the transaction-scoped connection, breaking atomicity. | Pass the existing `connection` and `transaction` objects to update commands. |
| TransactionService.cs | 48 | `Transfer` reads balances outside the transaction lock, risking race conditions (TOCTOU). | Read balances within the transaction scope or use `SELECT ... WITH (UPDLOCK)`. |
| TransactionService.cs | 108 | `Deposit` adds interest bonus to balance but records only the principal amount in `Transactions`. | Record the total credited amount or separate interest line item for audit accuracy. |
| TransactionService.cs | 108 | `Deposit` does not check `IsWithinDailyLimit` before processing. | Call `IsWithinDailyLimit(userId)` before executing deposit logic. |
| UserService.cs | 88 | `GetUsersPage` calculates `skip` using `(page - 1) * pageSize`, but doesn't validate `page < 1`. | Add validation to ensure `page >= 1` to prevent negative skip values. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionController.cs | 54 | `Refund` catches `NotImplementedException` and returns 500, leaking implementation details. | Return 501 Not Implemented or handle gracefully without exposing internal exceptions. |
| UserService.cs | 128 | `SearchUsers` catches `Exception`, logs to Console, and re-throws, potentially exposing stack traces. | Log to ILogger and return a generic error or empty list depending on policy. |
| EmailService.cs | 56 | `SendWelcomeEmail` catches `SmtpException` and writes to Console, swallowing errors silently. | Log via ILogger and consider failing the operation or notifying admin. |
| TransactionService.cs | 78 | `Transfer` catches broad `Exception` and returns generic "Transfer failed", hiding root causes. | Log the exception details internally for debugging while returning generic message to client. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| DatabaseHelper.cs | 23 | `GetOpenConnection` returns an open `SqlConnection` without disposing it, leaking connections. | Return `SqlConnection` wrapped in `using` by caller or change signature to accept `Action<SqlConnection>`. |
| TransactionService.cs | 48 | `Transfer` creates a new `SqlConnection` from string but doesn't dispose it in all paths. | Wrap `connection` in `using` statement or ensure disposal in `finally` block. |
| TransactionService.cs | 95 | `Deposit` creates a new `SqlConnection` but doesn't dispose it in all paths. | Wrap `connection` in `using` statement. |
| UserService.cs | 68 | `UpdateUser` creates a new `SqlConnection` but doesn't dispose it in all paths. | Wrap `connection` in `using` statement. |
| UserService.cs | 82 | `DeleteUser` creates a new `SqlConnection` but doesn't dispose it in all paths. | Wrap `connection` in `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| AuthService.cs | 82 | `GetSigningKey` uses `Environment.GetEnvironmentVariable` which can return null, passed to `GetBytes`. | Add null check or provide a secure default fallback. |
| AuthService.cs | 92 | `_config["Jwt:Issuer"]` and `_config["Jwt:Audience"]` can be null, passed to `JwtSecurityToken`. | Validate configuration values are present before creating token. |
| UserService.cs | 115 | `SearchUsers` passes `query` to SQL without checking for SQL injection characters, though parameterized. | Ensure `query` is validated/sanitized if used in dynamic contexts, though parameterization mitigates SQLi. |
| TransactionController.cs | 15 | `User.FindFirst(...)?.Value` can be null, but `int.TryParse` handles it; however, `request` null check is after token check. | Move `request == null` check before token validation to fail fast on malformed requests. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| StringHelper.cs | 28 | `JoinWithSeparatorFixed` is a duplicate of `JoinWithSeparator` and is never called. | Remove `JoinWithSeparatorFixed`. |
| StringHelper.cs | 48 | `ObfuscateAccount` duplicates logic of `MaskAccountNumber` and is never called. | Remove `ObfuscateAccount`. |
| StringHelper.cs | 56 | `ToTitleCase` is never called anywhere in the codebase. | Remove `ToTitleCase`. |
| StringHelper.cs | 61 | `IsBlank` duplicates `string.IsNullOrWhiteSpace` and is never called. | Remove `IsBlank`. |
| TransactionService.cs | 138 | `FormatCurrency` is defined but never used. | Remove `FormatCurrency`. |
| DatabaseHelper.cs | 58 | `ExecuteQueryWithParams` is marked `[Obsolete]` but still present. | Remove obsolete method if no longer used. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| TransactionService.cs | 12 | `TransactionFeeRate`, `MaxTransactionsPerDay`, `DepositCap`, `DepositInterestRate` are hardcoded. | Move to `appsettings.json` or configuration class. |
| EmailService.cs | 13 | Email subjects and addresses are hardcoded constants. | Move to configuration. |
| UserService.cs | 26 | `ValidateUserId` uses magic number `1_000_000` for max ID. | Define as constant or config value. |
| AuthService.cs | 76 | JWT expiration `AddDays(30)` is hardcoded. | Move to configuration. |
| UserController.cs | 42 | Default `pageSize` 20 and max 50 in `GetUsersPage` are hardcoded. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| UserService.cs | 10 | `AuditLog` and `RequestCount` are static mutable state, not thread-safe for production metrics. | Use a proper logging framework and distributed tracing/metrics. |
| DatabaseHelper.cs | 10 | `DatabaseHelper` implements `IDisposable` but doesn't dispose underlying resources. | Remove `IDisposable` if no resources are held, or implement correctly. |
| TransactionService.cs | 48 | `Transfer` mixes ADO.NET commands with helper methods, leading to inconsistent transaction handling. | Refactor to use a consistent data access pattern (e.g., Dapper or EF Core). |
| EmailService.cs | 38 | `SendEmailWithRetry` uses `Console.WriteLine` for logging. | Use `ILogger` for structured logging. |
| UserService.cs | 128 | `SearchUsers` uses `Console.WriteLine` for error logging. | Use `ILogger` for structured logging. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| Program.cs | 32 | `UseDeveloperExceptionPage()` is enabled only in Development, which is correct, but ensure it's not in Prod. | Verify environment detection is correct. |
| Program.cs | 42 | CORS policy uses `SetIsOriginAllowedToAllowWildcardSubdomains()`, which can be overly permissive. | Restrict to specific trusted origins. |
| SampleBankingApp.csproj | 8 | `DebugSymbols` and `DebugType` are set to `false`/`none`, hindering debugging in dev. | Set to `portable` or `full` for development builds. |
| appsettings.json | 1 | Connection strings and secrets use placeholders `__SET_VIA_ENV__`, which may fail if env vars are missing. | Ensure environment variables are set or use User Secrets for dev. |
| Program.cs | 15 | `DatabaseHelper` is registered as `Singleton`, but it holds no state; however, it creates connections per call. | Consider `Scoped` or `Transient` if it holds per-request state, or keep Singleton if stateless. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| N/A | N/A | No test project exists. | Create test project. |
| TransactionService.cs | 25 | `Transfer` logic (fees, balance checks, atomicity) needs unit tests with mocked DB. | Mock `DatabaseHelper` and test success/failure paths. |
| TransactionService.cs | 90 | `Deposit` logic (interest, caps) needs unit tests. | Mock `DatabaseHelper` and test deposit calculations. |
| AuthService.cs | 25 | `Login` and `GenerateJwtToken` need tests for valid/invalid credentials and token structure. | Mock `DatabaseHelper` and config; verify token claims. |
| UserService.cs | 45 | `GetUsersPage` pagination logic needs tests. | Mock `DatabaseHelper` and verify skip/take calculations. |
| UserController.cs | 35 | `UpdateUser` ownership check needs integration tests. | Test that non-owners cannot update other users. |