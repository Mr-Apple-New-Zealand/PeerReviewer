## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | ~30 | SQL query built with string interpolation (`SELECT * FROM Users WHERE Username = '{username}' …`) – vulnerable to SQL injection. | Use parameterised `SqlCommand` with `@Username` and `@Password` parameters. |
| AuthService.cs | ~20 | Passwords hashed with MD5 – weak, unsalted cryptography. | Replace with a strong algorithm (e.g., BCrypt, Argon2) and store a salt. |
| AuthService.cs | ~12 | Hard‑coded admin bypass password (`SuperAdmin2024`). | Remove backdoor; enforce normal authentication. |
| DatabaseHelper.cs | ~12 | Fallback connection string contains hard‑coded SA credentials. | Remove fallback; require secure configuration (e.g., Azure Key Vault). |
| DatabaseHelper.cs | ~30 | `ExecuteQuery` concatenates `tableName` and `whereClause` into raw SQL. | Refactor to use parameterised queries or whitelist table names. |
| DatabaseHelper.cs | ~44 | `ExecuteNonQuery` executes raw SQL built via string interpolation. | Use parameters for all values. |
| UserService.cs | ~70 | `UpdateUser` builds raw SQL with interpolated `email`/`username`. | Use parameterised command. |
| UserService.cs | ~84 | `DeleteUser` builds raw SQL with interpolated `id`. | Use parameterised command. |
| UserService.cs | ~100 | `SearchUsers` builds raw SQL with interpolated `query`. | Use parameters (`@query`) and proper escaping. |
| TransactionService.cs | ~30 | `Transfer` updates balances with interpolated values (`UPDATE Users SET Balance = {newFromBalance} …`). | Use parameterised command inside a transaction. |
| TransactionService.cs | ~70 | `RecordTransaction` inserts raw values (`{description}`) via string interpolation – `description` may be null. | Use parameters and handle nulls safely. |
| Program.cs | ~30 | JWT validation disables lifetime check (`ValidateLifetime = false`). | Set `ValidateLifetime = true` and configure reasonable token expiry. |
| Program.cs | ~38 | CORS policy allows any origin, method, and header. | Restrict origins to known clients and limit methods/headers. |
| Program.cs | ~40 | `UseDeveloperExceptionPage()` is enabled unconditionally. | Enable only in Development environment. |
| Program.cs | ~42 | HTTPS redirection is commented out. | Uncomment `app.UseHttpsRedirection();`. |
| SampleBankingApp.csproj | ~9 | `DebugSymbols` and `DebugType` are enabled for production builds. | Set to `false` or use Release configuration. |
| appsettings.json | ~8 | JWT secret key (`mysecretkey`) is short, predictable, and stored in source. | Store a strong secret in a secure vault; rotate regularly. |
| appsettings.json | ~13 | Database and email credentials are stored in plain text. | Move secrets to environment variables or secret manager. |
| EmailService.cs | ~20 | `EnableSsl = false` – email sent without TLS. | Set `EnableSsl = true` and use secure ports. |
| EmailService.cs | ~15 | `SmtpClient` is a singleton field – not thread‑safe. | Create a new client per send or switch to a thread‑safe library (e.g., MailKit). |
| AuthService.cs | ~70 | `ValidateToken` returns `true` for any non‑empty token and contains dead code after `return`. | Implement proper JWT validation (signature, expiry, audience, issuer). |
| AuthService.cs | ~72 | Unreachable code after early `return`. | Remove dead code. |
| EmailService.cs | ~10 | Hard‑coded email addresses (`notifications@company.com`, `support@company.com`). | Move to configuration. |
| TransactionService.cs | ~10 | Hard‑coded fee rate (`0.015m`) and limits (`MaxTransactionsPerDay = 10`). | Externalise to configuration. |
| TransactionService.cs | ~30 | Deposit amount upper bound (`1000000`) is hard‑coded. | Externalise to configuration. |
| TransactionService.cs | ~35 | Interest bonus rate (`0.05m`) is hard‑coded. | Externalise to configuration. |

## 2. Logic Errors
| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | ~20 | Balance check uses `fromBalance >= amount` but fee is deducted later (`totalDebit = amount + fee`). | Compare against `totalDebit`. |
| TransactionService.cs | ~10 | No check prevents transferring to oneself (`fromUserId == toUserId`). | Add guard returning error if IDs match. |
| TransactionService.cs | ~10 | Daily transaction limit (`MaxTransactionsPerDay`) is never enforced. | Call `IsWithinDailyLimit` before processing. |
| TransactionService.cs | ~20 | Updates to two accounts are performed without a DB transaction – risk of partial update. | Wrap both `UPDATE` statements in a single transaction. |
| TransactionService.cs | ~70 | `RecordTransaction` inserts `description` directly; if `null` it produces `''` or SQL error. | Use parameters and handle null (`DBNull.Value`). |
| UserService.cs | ~30 | Pagination offset calculated as `page * pageSize` (off‑by‑one). | Use `(page - 1) * pageSize`. |
| UserService.cs | ~28 | No validation that `page` is ≥ 1; negative pages produce negative `OFFSET`. | Validate `page >= 1` and clamp to 1 if needed. |
| AuthService.cs | ~70 | `ValidateToken` always returns `true` – any token accepted. | Implement proper validation (signature, expiry, audience, issuer). |
| AuthService.cs | ~12 | Admin bypass allows login with a static password regardless of DB state. | Remove bypass; enforce normal credential checks. |
| TransactionService.cs | ~50 | `IsWithinDailyLimit` is defined but never used, so daily limits are ineffective. | Integrate the method into `Transfer`/`Deposit` logic. |
| TransactionService.cs | ~30 | Deposit does not verify that the target user exists before updating balance. | Check that the user row exists (`Rows.Count > 0`). |
| TransactionService.cs | ~30 | Deposit does not enforce the daily transaction limit. | Apply `IsWithinDailyLimit` check. |
| TransactionService.cs | ~20 | Fee rounding may cause a cent‑loss/gain; ensure rounding policy is consistent. | Document and centralise rounding logic. |
| TransactionService.cs | ~20 | No check that `toUserId` actually exists; missing row leads to exception. | Verify existence before proceeding. |
| TransactionService.cs | ~20 | No check that `fromUserId` exists; missing row leads to exception. | Verify existence before proceeding. |
| AuthService.cs | ~25 | `Login` does not verify that `username`/`password` are non‑null before hashing. | Add null/empty checks and return BadRequest. |
| TransactionController.cs | ~9 | `User.FindFirst(ClaimTypes.NameIdentifier)` may be missing, causing `int.Parse(null)` crash. | Validate claim existence and return Unauthorized if absent. |
| TransactionController.cs | ~12 | `TransferRequest` body may be null, leading to NRE when accessing its properties. | Add `[FromBody]` null check or model validation. |
| TransactionController.cs | ~24 | `DepositRequest` body may be null, causing NRE. | Add null check or model validation. |
| UserController.cs | ~13 | `UpdateUserRequest` body may be null, causing NRE. | Add null check or model validation. |
| StringHelper.cs | ~5 | `IsValidEmail` accesses `email.Length` without null guard. | Return `false` if `email` is null. |
| StringHelper.cs | ~13 | `IsValidUsername` accesses `username.Length` without null guard. | Return `false` if `username` is null. |
| StringHelper.cs | ~30 | `MaskAccountNumber` uses `accountNumber.Length` without null guard. | Return empty or throw ArgumentNullException. |
| StringHelper.cs | ~38 | `ObfuscateAccount` uses `account[^4..]` without null guard. | Validate `account` is not null. |
| StringHelper.cs | ~20 | `JoinWithSeparator` iterates `items` without null guard. | Return empty string if `items` is null. |
| EmailService.cs | ~15 | Config values (`SmtpHost`, `SmtpPort`, `Username`, `Password`) may be null, causing runtime errors. | Validate config on startup and throw early if missing. |
| AuthService.cs | ~45 | `GenerateJwtToken` assumes `_config["Jwt:SecretKey"]` is non‑null; `Encoding.UTF8.GetBytes(null)` throws. | Validate secret key presence and length. |
| Program.cs | ~30 | `jwtSecret` may be null; `Encoding.UTF8.GetBytes(jwtSecret!)` will throw. | Fail fast with clear message if secret missing. |

## 3. Error Handling
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | ~25 | No `try/catch`; DB errors bubble up and connection stays open. | Wrap DB calls in `using` and catch `SqlException` to return appropriate error. |
| AuthService.cs | ~30 | `SqlConnection`, `SqlCommand`, `SqlDataReader` are never disposed. | Use `using` statements for all disposable ADO.NET objects. |
| TransactionService.cs | ~20 | No exception handling around balance updates; any DB failure returns 500. | Add `try/catch`, roll back transaction on failure, return meaningful error. |
| TransactionService.cs | ~30 | `RecordTransaction` does not handle possible SQL errors. | Wrap in `try/catch` and log failures. |
| TransactionController.cs | ~12 | `Transfer` does not catch service exceptions; unhandled exceptions return generic 500. | Add `try/catch` and map to appropriate HTTP status. |
| TransactionController.cs | ~24 | `Deposit` lacks error handling. | Same as above. |
| TransactionController.cs | ~38 | `Refund` only catches `NotImplementedException`; other errors leak. | Catch generic `Exception` and return 500 with logging. |
| UserService.cs | ~100 | `SearchUsers` catches all exceptions and returns empty list, hiding failures. | Log the exception and rethrow or return an error response. |
| EmailService.cs | ~30 | `SendTransferNotification` retries and rethrows after max attempts, but caller does not handle. | Propagate a custom exception or return a result indicating failure. |
| EmailService.cs | ~45 | `SendWelcomeEmail` catches generic `Exception` and only logs; caller assumes success. | Return a status or rethrow after logging. |
| EmailService.cs | ~55 | `SendWelcomeEmailHtml` has no error handling. | Add `try/catch` and log failures. |
| DatabaseHelper.cs | ~44 | `ExecuteNonQuery` does not catch SQL errors; callers receive raw exceptions. | Wrap in `try/catch` and surface a domain‑specific error. |
| DatabaseHelper.cs | ~30 | `ExecuteQuery` does not catch exceptions; connection may stay open. | Use `using` and handle `SqlException`. |
| DatabaseHelper.cs | ~12 | `GetOpenConnection` does not handle connection failures. | Wrap in `try/catch` and return null or throw a custom exception. |
| Program.cs | ~40 | `UseDeveloperExceptionPage` exposes stack traces to clients. | Remove for production; rely on generic error handling middleware. |
| StringHelper.cs | ~5 | `IsValidEmail` will throw if `email` is null. | Return `false` for null input. |
| StringHelper.cs | ~13 | `IsValidUsername` will throw if `username` is null. | Return `false` for null input. |
| StringHelper.cs | ~30 | `MaskAccountNumber` will throw if `accountNumber` is null. | Return empty or throw ArgumentNullException. |
| StringHelper.cs | ~38 | `ObfuscateAccount` will throw if `account` is null. | Return empty or throw ArgumentNullException. |

## 4. Resource Leaks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | ~25 | `SqlConnection`, `SqlCommand`, `SqlDataReader` are never disposed. | Use `using` blocks or `await using` for async. |
| DatabaseHelper.cs | ~12 | `GetOpenConnection` returns an open `SqlConnection` that callers often never dispose. | Return a `SqlConnection` wrapped in `using` or provide async helper that disposes. |
| DatabaseHelper.cs | ~30 | `ExecuteQuery` creates `SqlConnection`, `SqlCommand`, `SqlDataAdapter` without disposing them. | Use `using` for all three objects. |
| DatabaseHelper.cs | ~44 | `ExecuteNonQuery` creates `SqlConnection` and `SqlCommand` without disposing them (only `Close`). | Use `using` and let `Dispose` close the connection. |
| EmailService.cs | ~15 | `_smtpClient` is a long‑lived `SmtpClient` (IDisposable) never disposed. | Dispose it on application shutdown or create per‑send. |
| EmailService.cs | ~30 | `MailMessage` instances are never disposed after sending. | Wrap each `MailMessage` in `using`. |
| EmailService.cs | ~45 | `SendWelcomeEmail` creates a `MailMessage` without disposing. | Use `using`. |
| EmailService.cs | ~55 | `SendWelcomeEmailHtml` creates a `MailMessage` without disposing. | Use `using`. |
| TransactionService.cs | ~20 | Calls `ExecuteNonQuery` which leaks connections (see above). | Refactor `ExecuteNonQuery` to use `using`. |
| TransactionService.cs | ~30 | Calls `ExecuteNonQuery` for balance updates – same leak. | Same fix. |
| UserService.cs | ~70 | `UpdateUser` and `DeleteUser` use `ExecuteNonQuery` – connections leak. | Same fix. |
| UserService.cs | ~100 | `SearchUsers` uses `ExecuteQuery` – connections leak. | Same fix. |
| TransactionService.cs | ~50 | `IsWithinDailyLimit` uses `ExecuteQuerySafe` (properly disposed) – no leak, but other methods still leak. | Ensure all DB helpers dispose resources. |

## 5. Null Reference Risks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthController.cs | ~13 | `request` may be null; accessing `request.Username` causes NRE. | Add `[FromBody]` null check or enable model validation (`[ApiController]` already does it, but guard anyway). |
| TransactionController.cs | ~9 | `User.FindFirst(... )` may return null; `int.Parse(userIdClaim!)` will throw. | Validate claim existence and return `Unauthorized` if missing. |
| TransactionController.cs | ~12 | `TransferRequest` body may be null; accessing its properties causes NRE. | Add null check or `[ApiController]` model validation. |
| TransactionController.cs | ~24 | `DepositRequest` body may be null; accessing `request.Amount` causes NRE. | Add null check. |
| UserController.cs | ~13 | `UpdateUserRequest` body may be null; accessing `request.Email`/`Username` causes NRE. | Add null check. |
| StringHelper.cs | ~5 | `IsValidEmail` accesses `email.Length` without null guard. | Return `false` if `email` is null. |
| StringHelper.cs | ~13 | `IsValidUsername` accesses `username.Length` without null guard. | Return `false` if `username` is null. |
| StringHelper.cs | ~30 | `MaskAccountNumber` uses `accountNumber.Length` without null guard. | Return original or throw `ArgumentNullException`. |
| StringHelper.cs | ~38 | `ObfuscateAccount` uses `account[^4..]` without null guard. | Return empty or throw if `account` is null. |
| StringHelper.cs | ~20 | `JoinWithSeparator` iterates `items` without null guard. | Return empty string if `items` is null. |
| EmailService.cs | ~15 | Config values (`SmtpHost`, `SmtpPort`, `Username`, `Password`) may be null, causing runtime errors. | Validate configuration on startup and throw early if missing. |
| AuthService.cs | ~25 | `username` or `password` may be null; `HashPasswordMd5(password)` will NRE. | Validate inputs before processing. |
| AuthService.cs | ~45 | `_config["Jwt:SecretKey"]` may be null; `Encoding.UTF8.GetBytes(null)` throws. | Validate secret key presence and length. |
| Program.cs | ~30 | `jwtSecret` may be null; `Encoding.UTF8.GetBytes(jwtSecret!)` throws. | Abort startup with clear error if secret missing. |
| TransactionService.cs | ~20 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count`. | Verify rows exist before accessing. |
| TransactionService.cs | ~30 | `Deposit` accesses `fromUserTable.Rows[0]` without existence check. | Verify row count. |
| TransactionService.cs | ~70 | `RecordTransaction` inserts `description` directly; if `null` it becomes empty string which may violate NOT NULL constraint. | Use `DBNull.Value` for nulls via parameters. |
| UserService.cs | ~100 | `SearchUsers` builds raw SQL with `query` that could be null; resulting SQL may be malformed. | Guard against null or treat as empty string. |

## 6. Dead Code
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | ~70 | `ValidateToken` returns early; the code after `return` is never executed. | Remove dead code or restructure method. |
| AuthService.cs | ~55 | `HashPasswordSha1` is never called. | Delete if not needed or replace MD5 usage. |
| TransactionService.cs | ~50 | `IsWithinDailyLimit` is defined but never invoked. | Either use it in transfer/deposit logic or remove. |
| TransactionService.cs | ~80 | `FormatCurrency` is never used. | Remove or expose if needed. |
| DatabaseHelper.cs | ~70 | `ExecuteQueryWithParams` is marked `[Obsolete]` and never called. | Delete the method. |
| StringHelper.cs | ~20 | `JoinWithSeparator` is never used (the fixed version is used instead). | Remove the inefficient version. |
| StringHelper.cs | ~45 | `IsBlank` is never referenced. | Delete it. |
| EmailService.cs | ~70 | `BuildHtmlTemplate` is never used (HTML is built inline). | Remove or integrate into `SendWelcomeEmailHtml`. |
| EmailService.cs | ~55 | `SendWelcomeEmailHtml` builds HTML manually instead of using `BuildHtmlTemplate`. | Either use the helper or delete the helper. |
| AuthService.cs | ~12 | `AdminBypassPassword` constant is a backdoor that should not exist in production. | Remove the constant and related logic. |

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | ~12 | Fallback connection string hard‑coded with credentials. | Move to secure configuration; avoid hard‑coding. |
| AuthService.cs | ~12 | `AdminBypassPassword = "SuperAdmin2024"` – magic backdoor password. | Remove; use proper admin authentication. |
| appsettings.json | ~8 | JWT `SecretKey = "mysecretkey"` – short, predictable string. | Store a strong secret in a secret manager. |
| appsettings.json | ~13 | DB and email passwords stored in plain text. | Move to environment variables or secret store. |
| TransactionService.cs | ~10 | `TransactionFeeRate = 0.015m` – magic fee rate. | Externalise to configuration. |
| TransactionService.cs | ~11 | `MaxTransactionsPerDay = 10` – magic limit. | Externalise to configuration. |
| TransactionService.cs | ~30 | Deposit amount upper bound `1000000`. | Externalise to configuration. |
| TransactionService.cs | ~35 | Interest bonus multiplier `0.05m`. | Externalise to configuration. |
| UserService.cs | ~25 | Default `pageSize = 20` and max `50`. | Externalise to configuration. |
| AuthService.cs | ~45 | JWT token expiry `AddDays(30)`. | Externalise expiry duration. |
| EmailService.cs | ~10 | Email subjects `"Transfer Notification - BankingApp"` and `"Welcome to BankingApp!"`. | Move to resources or config. |
| EmailService.cs | ~15 | `MaxRetries = 3`, `SmtpTimeoutMs = 5000`. | Externalise to config. |
| Program.cs | ~38 | CORS `AllowAnyOrigin/AllowAnyMethod/AllowAnyHeader`. | Restrict to known origins/methods. |
| Program.cs | ~30 | `ValidateLifetime = false`. | Set to `true`. |
| Program.cs | ~40 | `UseDeveloperExceptionPage()` unconditional. | Enable only in Development. |
| Program.cs | ~42 | HTTPS redirection commented out. | Enable in production. |
| SampleBankingApp.csproj | ~9 | `DebugSymbols = true`, `DebugType = full`. | Set to false for Release. |
| appsettings.json | ~20 | Logging level `"Debug"` for all categories. | Use `"Information"` or environment‑specific levels. |

## 8. Anti‑patterns and Code Quality
| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | ~20 | `JoinWithSeparator` builds a string with `+=` inside a loop (O(n²)). | Replace with `string.Join(separator, items)` or `StringBuilder`. |
| StringHelper.cs | ~5 & ~13 | New `Regex` compiled on every call. | Cache compiled regex as `static readonly`. |
| UserService.cs | ~5 | Static mutable fields `_auditLog` and `_requestCount` accessed without synchronization – not thread‑safe. | Use concurrent collections or lock, or remove static state. |
| EmailService.cs | ~15 | Singleton `SmtpClient` (IDisposable, not thread‑safe). | Create a new client per send or use a thread‑safe library. |
| DatabaseHelper.cs | ~30, ~44 | Raw SQL built via string interpolation – prone to injection and hard to maintain. | Use parameterised commands everywhere. |
| AuthService.cs | ~20 | MD5 hashing for passwords. | Switch to BCrypt/Argon2 with salt. |
| AuthService.cs | ~70 | `ValidateToken` returns true for any token. | Implement proper JWT validation. |
| AuthService.cs | ~25 | No `using` statements for `SqlConnection`, `SqlCommand`, `SqlDataReader`. | Wrap in `using`. |
| TransactionService.cs | ~20 | Multiple DB writes without a transaction – can leave data inconsistent. | Use `SqlTransaction` or a higher‑level unit of work. |
| TransactionService.cs | ~10 | Hard‑coded business constants (fee rate, limits). | Move to configuration. |
| Program.cs | ~30 | JWT lifetime validation disabled. | Enable `ValidateLifetime`. |
| Program.cs | ~38 | Open CORS policy. | Restrict origins. |
| Program.cs | ~40 | Developer exception page in production. | Guard with `if (app.Environment.IsDevelopment())`. |
| Program.cs | ~42 | HTTPS redirection disabled. | Enable it. |
| SampleBankingApp.csproj | ~9 | Debug symbols enabled for production builds. | Set `DebugType` to `pdbonly` or disable. |
| Controllers (many) | Various | No explicit model validation attributes; rely on `[ApiController]` but still access properties without null checks. | Add `[Required]` and other data‑annotations; check `ModelState.IsValid`. |
| Services (many) | Various | Synchronous I/O (ADO.NET) in ASP.NET Core – blocks thread pool. | Use async ADO.NET (`ExecuteReaderAsync`, etc.). |
| Services (many) | Various | No cancellation tokens passed to DB calls. | Accept `CancellationToken` and forward to async DB methods. |
| Services (many) | Various | Logging of sensitive data (e.g., failed login username) without masking. | Avoid logging passwords; consider masking usernames if needed. |
| EmailService.cs | ~30 | Swallowing `SmtpException` after max retries by re‑throwing generic exception. | Throw a custom domain exception with context. |
| StringHelper.cs | ~45 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove method and use built‑in. |
| TransactionService.cs | ~70 | `RecordTransaction` builds SQL with possible `null` description; risk of syntax error. | Use parameters and `DBNull.Value`. |

## 9. Configuration Issues
| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | ~40 | `UseDeveloperExceptionPage()` runs in all environments. | Wrap with `if (app.Environment.IsDevelopment())`. |
| Program.cs | ~30 | `ValidateLifetime = false` disables token expiry checks. | Set to `true`. |
| Program.cs | ~38 | CORS policy `AllowAnyOrigin/AllowAnyMethod/AllowAnyHeader`. | Restrict to specific origins and methods. |
| Program.cs | ~42 | HTTPS redirection is commented out. | Uncomment `app.UseHttpsRedirection();`. |
| SampleBankingApp.csproj | ~9 | `DebugSymbols = true` and `DebugType = full` for production. | Set to `false` or use Release configuration. |
| appsettings.json | ~8 | JWT secret key is weak and stored in source. | Move to secret store (Azure Key Vault, AWS Secrets Manager). |
| appsettings.json | ~13 | Database and email passwords are in plain text. | Store in environment variables or secret manager. |
| appsettings.json | ~20 | Logging level set to `Debug` for all categories. | Use `Information` for production; override per environment. |
| appsettings.json | – | No environment‑specific files (`appsettings.Development.json`, `appsettings.Production.json`). | Add them and keep secrets out of source. |
| appsettings.json | – | Business constants (fee rates, limits) are hard‑coded in code, not configurable. | Add them to configuration files. |
| Program.cs | – | No rate‑limiting or lock‑out configured for authentication endpoints. | Add ASP.NET Core Rate Limiting middleware or custom logic. |
| Program.cs | – | No HSTS (`UseHsts()`) configured for production. | Add `app.UseHsts();` in non‑development. |
| Program.cs | – | No health‑check endpoints configured. | Add `app.MapHealthChecks("/health")`. |
| Program.cs | – | No OpenAPI/Swagger security scheme defined (exposes endpoints). | Configure JWT bearer scheme in Swagger. |

## 10. Missing Unit Tests
| File | Line | Issue | Fix |
|------|------|-------|-----|
| – | – | No test project is present in the repository. | Add an XUnit/NUnit/MSTest project (e.g., `SampleBankingApp.Tests`). |
| AuthService.cs | ~25 | Critical authentication logic (password verification, admin bypass, token generation). | Write unit tests for successful login, failed login, admin bypass, password hashing, and JWT claims. |
| AuthService.cs | ~45 | `GenerateJwtToken` – ensure correct claims and expiry. | Test token contains expected `NameIdentifier`, `Name`, `Role`, and respects expiry. |
| AuthService.cs | ~70 | `ValidateToken` – currently always returns true. | Test that expired, malformed, and tampered tokens are rejected. |
| TransactionService.cs | ~20 | `Transfer` – fee calculation, insufficient funds, self‑transfer, daily limit, atomicity. | Write tests covering: successful transfer, insufficient balance, fee deduction, self‑transfer rejection, exceeding daily limit, and rollback on DB error (mock). |
| TransactionService.cs | ~30 | `Deposit` – amount validation, interest bonus, upper limit. | Test valid deposit, deposit exceeding limit, zero/negative amount, and correct balance update with bonus. |
| TransactionService.cs | ~50 | `IsWithinDailyLimit` – boundary condition at limit. | Test exactly at limit and just over limit. |
| UserService.cs | ~25 | `GetUsersPage` – pagination offset and page‑size cap. | Test first page, second page, page size > max, and negative page numbers. |
| UserService.cs | ~100 | `SearchUsers` – SQL injection safety and empty query handling. | Verify that special characters are escaped and that null/empty query returns appropriate results. |
| EmailService.cs | ~30 | `SendTransferNotification` – retry logic on `SmtpException`. | Mock `SmtpClient` to throw on first attempts and succeed on later; verify retry count. |
| EmailService.cs | ~45 | `SendWelcomeEmail` – exception handling does not crash caller. | Mock failure and ensure method does not throw. |
| DatabaseHelper.cs | – | All DB helper methods – ensure connections are disposed and exceptions are propagated correctly. | Use a mock `SqlConnection`/`SqlCommand` to verify `Dispose` is called. |
| StringHelper.cs | ~5 | `IsValidEmail` – null, empty, and malformed inputs. | Test null, overly long, missing `@`, etc. |
| StringHelper.cs | ~20 | `JoinWithSeparator` vs `JoinWithSeparatorFixed` – performance and correctness. | Verify both produce same output; benchmark optional. |
| Controllers (Auth, Transaction, User) | – | Model validation and error responses. | Test that invalid models return `400 BadRequest` and that successful calls return expected status codes. |
| Overall | – | Integration tests for end‑to‑end authentication + authorized transaction flow. | Use `WebApplicationFactory` to spin up in‑memory server and test full request pipeline. |

*All listed methods should be covered with both positive and negative test cases, including boundary conditions, exception paths, and security‑relevant scenarios.*