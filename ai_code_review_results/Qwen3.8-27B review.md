# Code Review Report

**Branch:** `main` | **Commit:** `3d4ff917762ca55f5af8e4f687f73eab201302f2`

---

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 32 | `Login` builds SQL via string interpolation with `username` and `hashedPassword`, enabling SQL injection. | Use parameterized query with `@Username` and `@Password` parameters. |
| AuthService.cs | 53–56 | Hardcoded admin backdoor: any request with username `"admin"` and password `"SuperAdmin2024"` bypasses the DB and returns a SuperAdmin user. | Remove the bypass entirely; if a service account is needed, store it in the DB with proper hashing. |
| AuthService.cs | 61–66 | `HashPasswordMd5` uses MD5 (unsalted, broken) for password hashing. | Replace with bcrypt, Argon2, or PBKDF2 with a per-user salt. |
| AuthService.cs | 91–96 | `HashPasswordSha1` uses SHA1 (broken) for password hashing. | Remove the method (dead code) or replace with a modern KDF. |
| Program.cs | 24 | `ValidateLifetime = false` means issued JWTs never expire. | Set `ValidateLifetime = true` and enforce a reasonable `ClockSkew`. |
| Program.cs | 38 | CORS policy allows any origin, any method, and any header simultaneously. | Restrict to specific origins, methods, and headers required by the frontend. |
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, exposing full stack traces to clients in production. | Guard with `if (app.Environment.IsDevelopment())` and use `UseExceptionHandler` in production. |
| Program.cs | 36 | HTTPS redirection is commented out, allowing plaintext HTTP traffic. | Uncomment and enable `app.UseHttpsRedirection()`. |
| Program.cs | 28 | `jwtSecret!` uses null-forgiving operator; if the config key is absent, `Encoding.UTF8.GetBytes(null)` throws at startup or produces an empty key. | Validate the secret at startup and fail fast with a clear message. |
| DatabaseHelper.cs | 16 | Fallback connection string contains hardcoded `sa` credentials (`Password=Admin1234!`). | Remove the fallback; require the connection string from configuration and fail if missing. |
| appsettings.json | 3 | Production database credentials (`User Id=sa;Password=Admin1234!`) committed to source control. | Move to a secrets manager (Azure Key Vault, AWS Secrets Manager) or environment variables. |
| appsettings.json | 6 | JWT secret `"mysecretkey"` is trivially guessable and committed to source control. | Use a cryptographically random 256-bit key stored in a secrets manager. |
| appsettings.json | 14 | SMTP password `"EmailPass99"` committed to source control. | Move to a secrets manager or environment variable. |
| TransactionService.cs | 47–48 | `Transfer` builds UPDATE statements via string interpolation with computed balance values. | Use parameterized queries with `@NewBalance` and `@Id`. |
| TransactionService.cs | 71 | `Deposit` builds an UPDATE via string interpolation with `amount + interestBonus`. | Use a parameterized query. |
| TransactionService.cs | 89–90 | `RecordTransaction` builds an INSERT via string interpolation including `description` (user-supplied). | Use a parameterized query. |
| UserService.cs | 47 | `UpdateUser` builds an UPDATE via string interpolation with `email` and `username`. | Use a parameterized query. |
| UserService.cs | 61 | `DeleteUser` builds a DELETE via string interpolation with `id`. | Use a parameterized query. |
| UserService.cs | 99 | `SearchUsers` passes user input directly into a `LIKE '%{query}%'` clause via `ExecuteQuery`. | Use a parameterized query with `LIKE @Pattern` and escape `%`/`_` in the input. |
| DatabaseHelper.cs | 29 | `ExecuteQuery` accepts raw `tableName` and `whereClause` strings that are interpolated into SQL. | Remove this method or require a whitelist of table names and parameterized where-clauses. |
| UserController.cs | 39–54 | `UpdateUser` has no ownership check; any authenticated user can update any user by ID. | Verify `id` matches the current user's ID or require an admin role. |
| UserController.cs | 56–69 | `DeleteUser` has no ownership check; any authenticated user can delete any user. | Verify `id` matches the current user's ID or require an admin role. |
| UserController.cs | 21–29 | `GetUser` has no ownership check; any authenticated user can read any user's data. | Restrict to own record or require admin role. |
| UserController.cs | 78–82 | `GetAuditLog` is accessible to any authenticated user with no role restriction. | Add `[Authorize(Roles = "Admin")]` or similar. |
| AuthController.cs | 19–31 | No rate limiting or account lockout on the login endpoint. | Add rate limiting (e.g., `Microsoft.AspNetCore.RateLimiting`) and progressive lockout. |
| EmailService.cs | 29 | `EnableSsl = false` sends SMTP credentials and email bodies in plaintext. | Set `EnableSsl = true` and use port 587 with STARTTLS. |
| appsettings.json | 18–20 | Log level set to `"Debug"` for all namespaces, which can log sensitive data (tokens, passwords) to output. | Set production log level to `"Information"` or `"Warning"`. |

---

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserService.cs | 72 | `GetUsersPage` computes `skip = page * pageSize`, so page 1 skips 20 rows instead of 0 (off-by-one). | Change to `skip = (page - 1) * pageSize`. |
| TransactionService.cs | 42 | `Transfer` checks `fromBalance >= amount` but then deducts `amount + fee` (totalDebit), so a user with exactly `amount` in balance will go negative. | Change the check to `fromBalance >= totalDebit`. |
| TransactionService.cs | 25 | `Transfer` rejects `amount < 0` but allows `amount == 0`, permitting a zero-value transfer that still incurs a fee and a DB write. | Change to `amount <= 0`. |
| TransactionService.cs | 23–61 | `Transfer` has no self-transfer check; a user can transfer to their own ID. | Add `if (fromUserId == toUserId) return (false, "Cannot transfer to yourself");`. |
| TransactionService.cs | 68 | `Deposit` computes `amount * 0.05m * 1`; the `* 1` is a no-op and the 5% rate appears incorrect (likely meant to be 1% or a configurable rate). | Remove the `* 1` and move the rate to a named constant or configuration value. |
| TransactionService.cs | 36–37 | `Transfer` accesses `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` without verifying `Rows.Count > 0`; a non-existent `toUserId` will throw `IndexOutOfRangeException`. | Check `Rows.Count == 0` and return an error for each. |
| TransactionService.cs | 23–61 | `Transfer` never calls `IsWithinDailyLimit`, so the daily transaction limit is never enforced. | Call `IsWithinDailyLimit(fromUserId)` before processing and reject if over limit. |
| TransactionService.cs | 65 | `Deposit` rejects `amount <= 0` but the upper bound `1000000` is a magic number with no named constant. | Extract to a `private const decimal MaxDepositAmount = 1_000_000m;`. |
| UserService.cs | 70 | `GetUsersPage` silently caps `pageSize` at 50 without informing the caller; a request for 100 items silently returns 50. | Return the effective page size in the response or reject with 400. |

---

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 34–51 | `Login` opens a connection and reader with no `using` or `try/finally`; any exception leaks the connection and reader. | Wrap in `using` statements or a `try/finally` that disposes both. |
| TransactionService.cs | 47–50 | `Transfer` executes two separate `ExecuteNonQuery` calls (debit and credit) without a database transaction; if the second fails, the first is already committed. | Wrap both updates in a single `SqlTransaction` and commit atomically. |
| TransactionService.cs | 52–55 | `Transfer` sends an email after the DB writes have committed; if `SendTransferNotification` throws, the transfer is already persisted but the caller receives an error. | Send the email in a `try/catch` that logs but does not propagate, or use an outbox pattern. |
| UserService.cs | 97–108 | `SearchUsers` catches a broad `Exception` and returns an empty `List<User>`, making it impossible for the caller to distinguish "no results" from a database error. | Log the exception and rethrow or return a typed error result. |
| UserController.cs | 52 | `UpdateUser` returns `ex.Message` directly to the HTTP client, potentially leaking internal details (SQL errors, file paths). | Return a generic error message and log the full exception server-side. |
| UserController.cs | 64 | `DeleteUser` catches a broad `Exception`; while the response is generic, the catch scope is wider than necessary. | Catch specific exceptions (e.g., `SqlException`, `ArgumentException`). |
| EmailService.cs | 71–78 | `SendWelcomeEmail` catches a broad `Exception` and only writes to `Console.WriteLine`, silently swallowing the failure. | Log via `ILogger` and consider whether the caller should be notified. |
| TransactionController.cs | 51–59 | `Refund` catches `NotImplementedException` specifically, which is a programming error, not a runtime error; this masks the fact that the feature is unimplemented. | Return `501 Not Implemented` directly without the try/catch, or implement the method. |
| AuthController.cs | 19–31 | No rate limiting or account lockout on the login endpoint; an attacker can brute-force credentials indefinitely. | Add rate limiting middleware and track failed attempts with progressive lockout. |

---

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 34–38 | `Login` creates a `SqlConnection` and `SqlDataReader` without `using`; neither is closed or disposed on any code path. | Wrap both in `using` statements. |
| DatabaseHelper.cs | 19–24 | `GetOpenConnection` returns an open `SqlConnection` with no documented contract that the caller must dispose it. | Remove this method and use `using` internally in each caller, or document the ownership contract in XML docs. |
| DatabaseHelper.cs | 26–34 | `ExecuteQuery` calls `GetOpenConnection()` but never closes or disposes the connection, command, or adapter. | Use `using` for the connection, command, and adapter. |
| DatabaseHelper.cs | 50–57 | `ExecuteNonQuery` calls `GetOpenConnection()` and only calls `connection.Close()`; if `ExecuteNonQuery` throws, `Close()` is never reached and the connection is leaked. | Use `using` for the connection and command. |
| DatabaseHelper.cs | 36–48 | `ExecuteQuerySafe` does not dispose the `SqlDataAdapter` (which is `IDisposable`). | Wrap the adapter in a `using` statement. |
| DatabaseHelper.cs | 68–78 | `ExecuteQueryWithParams` does not dispose the `SqlDataAdapter`. | Wrap the adapter in a `using` statement. |
| EmailService.cs | 16 | `SmtpClient` is stored as an instance field; `SmtpClient` is not thread-safe and the underlying socket is never released. | Create a new `SmtpClient` per send operation and dispose it, or use a thread-safe wrapper. |
| EmailService.cs | 39 | `SendTransferNotification` creates a `MailMessage` that is never disposed. | Wrap in a `using` statement. |
| EmailService.cs | 69 | `SendWelcomeEmail` creates a `MailMessage` that is never disposed. | Wrap in a `using` statement. |
| EmailService.cs | 89 | `SendWelcomeEmailHtml` creates a `MailMessage` that is never disposed. | Wrap in a `using` statement. |

---

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 28 | `jwtSecret!` uses null-forgiving; if `"Jwt:SecretKey"` is missing from config, `Encoding.UTF8.GetBytes(null)` throws `ArgumentNullException`. | Null-check and throw a descriptive `InvalidOperationException` at startup. |
| AuthService.cs | 34 | `_config.GetConnectionString("DefaultConnection")` can return `null`, which is passed directly to the `SqlConnection` constructor. | Null-check and throw a descriptive exception. |
| AuthService.cs | 70 | `_config["Jwt:SecretKey"]!` uses null-forgiving; a missing key causes a runtime crash. | Null-check and fail fast. |
| AuthService.cs | 81–82 | `_config["Jwt:Issuer"]` and `_config["Jwt:Audience"]` are passed to `JwtSecurityToken` without null checks. | Null-check both values. |
| TransactionService.cs | 36 | `fromUserTable.Rows[0]` is accessed without checking `Rows.Count > 0`; a non-existent `fromUserId` throws `IndexOutOfRangeException`. | Check `Rows.Count == 0` and return an error. |
| TransactionService.cs | 37 | `toUserTable.Rows[0]` is accessed without checking `Rows.Count > 0`. | Check `Rows.Count == 0` and return an error. |
| TransactionService.cs | 53 | `fromUserTable.Rows[0]["Email"]` is accessed again without a null/count guard. | Guard with `Rows.Count > 0` and null-check the column value. |
| TransactionService.cs | 55 | `toUserTable.Rows[0]["Username"]` is accessed without a null/count guard. | Guard with `Rows.Count > 0` and null-check the column value. |
| TransactionController.cs | 27 | `userIdClaim!` uses null-forgiving; if the `NameIdentifier` claim is absent, `int.Parse(null)` throws `ArgumentNullException`. | Null-check `userIdClaim` and return 401 if missing. |
| TransactionController.cs | 41 | Same null-forgiving pattern on `userIdClaim!` in `Deposit`. | Null-check and return 401. |
| EmailService.cs | 22 | `_config["Email:SmtpHost"]` can be `null` and is passed directly to the `SmtpClient` constructor. | Null-check and throw a descriptive exception. |
| EmailService.cs | 26–27 | `_config["Email:Username"]` and `_config["Email:Password"]` can be `null` and are passed to `NetworkCredential`. | Null-check both values. |
| UserController.cs | 72 | `SearchUsers` accepts `[FromQuery] string query` which can be `null`; it is passed to `UserService.SearchUsers` and interpolated into SQL. | Null-check and return 400 if null. |
| UserController.cs | 39 | `UpdateUser` uses `request.Email` and `request.Username` without a null check on `request` itself. | Add a null check on `request` (though `[ApiController]` may handle this, it is not guaranteed for all binding scenarios). |

---

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 59–65 | `TableExists` is defined but never called anywhere in the codebase. | Remove the method. |
| DatabaseHelper.cs | 67–78 | `ExecuteQueryWithParams` is marked `[Obsolete]` and is never called. | Remove the method. |
| StringHelper.cs | 11–18 | `IsValidEmail` is defined but never called anywhere in the codebase. | Remove the method. |
| StringHelper.cs | 20–27 | `IsValidUsername` is defined but never called anywhere in the codebase. | Remove the method. |
| StringHelper.cs | 29–36 | `JoinWithSeparator` is defined but never called anywhere in the codebase. | Remove the method. |
| StringHelper.cs | 38–41 | `JoinWithSeparatorFixed` is defined but never called anywhere in the codebase. | Remove the method. |
| StringHelper.cs | 43–52 | `MaskAccountNumber` is defined but never called anywhere in the codebase. | Remove the method. |
| StringHelper.cs | 54–57 | `ObfuscateAccount` is defined but never called anywhere in the codebase. | Remove the method. |
| StringHelper.cs | 59–63 | `ToTitleCase` is defined but never called anywhere in the codebase. | Remove the method. |
| StringHelper.cs | 65–71 | `IsBlank` is defined but never called anywhere in the codebase. | Remove the method. |
| AuthService.cs | 91–96 | `HashPasswordSha1` is defined but never called anywhere in the codebase. | Remove the method. |
| AuthService.cs | 98–108 | `ValidateToken` is defined but never called anywhere in the codebase. | Remove the method. |
| AuthService.cs | 105–107 | `ValidateToken` contains unreachable code after an unconditional `return true;` on line 103. | Remove the dead code (or the entire method). |
| EmailService.cs | 63–79 | `SendWelcomeEmail` is defined but never called anywhere in the codebase. | Remove the method. |
| EmailService.cs | 86–92 | `SendWelcomeEmailHtml` is defined but never called anywhere in the codebase. | Remove the method. |
| EmailService.cs | 81–84 | `BuildHtmlTemplate` is only called by the dead `SendWelcomeEmailHtml` and is itself never called from live code. | Remove the method. |
| TransactionService.cs | 77–85 | `IsWithinDailyLimit` is defined but never called anywhere in the codebase. | Either call it in `Transfer` or remove it. |
| TransactionService.cs | 94–97 | `FormatCurrency` is defined but never called anywhere in the codebase. | Remove the method. |
| TransactionService.cs | 99–103 | `RefundTransaction` contains `throw new NotImplementedException()` in non-stub production code. | Implement the method or remove the endpoint. |
| StringHelper.cs | 29–41 | `JoinWithSeparator` (broken O(n²) version) and `JoinWithSeparatorFixed` (correct version) are duplicate implementations of the same functionality. | Remove both (neither is called) or keep only the correct one. |
| StringHelper.cs | 43–57 | `MaskAccountNumber` and `ObfuscateAccount` are duplicate implementations of the same masking logic. | Remove both (neither is called) or keep one. |

---

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 65 | `1000000` (max deposit) is a magic number with no named constant. | Extract to `private const decimal MaxDepositAmount = 1_000_000m;`. |
| TransactionService.cs | 68 | `0.05m` (interest rate) and `1` (multiplier) are magic numbers inline. | Extract to named constants or configuration values. |
| UserService.cs | 22 | `1000000` (max user ID) is a magic number. | Extract to a shared constant. |
| UserService.cs | 42 | `1000000` (max user ID) repeated. | Use the shared constant. |
| UserService.cs | 56 | `1000000` (max user ID) repeated. | Use the shared constant. |
| UserService.cs | 70 | `50` (max page size) is a magic number. | Extract to `private const int MaxPageSize = 50;`. |
| UserController.cs | 32 | `pageSize = 20` (default page size) is a magic number in the controller signature. | Extract to a constant or configuration value. |
| StringHelper.cs | 13 | `254` (max email length) is a magic number. | Extract to a named constant. |
| StringHelper.cs | 22 | `3` and `20` (username min/max length) are magic numbers. | Extract to named constants. |
| AuthService.cs | 17 | `"SuperAdmin2024"` is a hardcoded password string. | Remove entirely (see security section). |
| AuthService.cs | 53 | `"admin"` is a hardcoded username string. | Remove with the bypass logic. |
| AuthService.cs | 84 | `30` (token expiry in days) is a magic number. | Extract to a constant or configuration value. |
| EmailService.cs | 40 | `"notifications@company.com"` is a hardcoded email address. | Move to configuration. |
| EmailService.cs | 67 | `"support@company.com"` is a hardcoded email address. | Move to configuration. |
| EmailService.cs | 89 | `"notifications@company.com"` is repeated (third occurrence across the file). | Use a single constant or config value. |
| EmailService.cs | 24 | `"25"` (default SMTP port) is a magic string. | Extract to a named constant. |
| DatabaseHelper.cs | 16 | Fallback connection string with server, database, user, and password is a hardcoded magic string. | Remove the fallback entirely. |
| TransactionService.cs | 12 | `MaxTransactionsPerDay = 10` is a constant but should be configurable per deployment. | Move to `appsettings.json`. |

---

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 31–34 | `JoinWithSeparator` uses string concatenation (`+=`) inside a loop, producing O(n²) allocations. | Use `string.Join` or `StringBuilder`. |
| StringHelper.cs | 16 | `IsValidEmail` creates a `new Regex(...)` on every call. | Make the regex a `private static readonly` field. |
| StringHelper.cs | 25 | `IsValidUsername` creates a `new Regex(...)` on every call. | Make the regex a `private static readonly` field. |
| UserService.cs | 10 | `_auditLog` is a `static List<string>` mutated from multiple threads without synchronization. | Use a `ConcurrentQueue<string>` or protect with a lock. |
| UserService.cs | 11 | `_requestCount` is a `static int` incremented from multiple threads without synchronization. | Use `Interlocked.Increment` or a `ConcurrentDictionary`. |
| StringHelper.cs | 65–71 | `IsBlank` reimplements `string.IsNullOrWhiteSpace` with three separate checks. | Replace the body with `return string.IsNullOrWhiteSpace(value);`. |
| UserService.cs | 87–92 | `GetAuditReport` uses string concatenation in a loop (O(n²)). | Use `string.Join("\n", _auditLog)` or `StringBuilder`. |
| DatabaseHelper.cs | 19–24 | `GetOpenConnection` leaks resource ownership to callers with no documented contract for disposal. | Remove the method and encapsulate connection lifecycle within each data-access method. |
| TransactionService.cs | 23–61 | `Transfer` carries at least four distinct responsibilities: input validation, balance/fee calculation, dual DB writes + transaction recording, and email notification. | Split into private helpers: `ValidateTransfer`, `ExecuteTransfer`, `NotifyTransfer`. |
| AuthService.cs | 28–59 | `Login` carries at least three distinct responsibilities: password hashing, DB query + row mapping, and admin-bypass logic. | Split into `HashPassword`, `QueryUser`, and remove the bypass. |
| UserService.cs | 18–36 | `GetUserById` mixes input validation, request counting, DB query, and row mapping. | Extract validation to a guard method and keep mapping separate. |
| TransactionService.cs | 89–91 | `RecordTransaction` builds SQL via interpolation and calls `ExecuteNonQuery` (which itself leaks a connection); the method has no error handling. | Use a parameterized query and add proper disposal. |

---

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally without an environment check. | Wrap in `if (app.Environment.IsDevelopment())` and add `app.UseExceptionHandler()` for production. |
| Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry validation. | Set to `true`. |
| Program.cs | 36 | `app.UseHttpsRedirection()` is commented out. | Uncomment and enable. |
| Program.cs | 38 | CORS allows `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` simultaneously. | Restrict to specific origins, methods, and headers. |
| appsettings.json | 18–20 | Log level is `"Debug"` for `Default`, `Microsoft`, and `System` namespaces. | Set to `"Information"` or `"Warning"` for production. |
| SampleBankingApp.csproj | 14 | `System.Data.SqlClient` 4.8.6 is the legacy package; `Microsoft.Data.SqlClient` is the supported replacement. | Migrate to `Microsoft.Data.SqlClient` (≥ 5.x). |
| SampleBankingApp.csproj | 15 | `Newtonsoft.Json` 12.0.3 has known CVEs (e.g., CVE-2019-13059). | Upgrade to ≥ 13.0.1 or remove if unused. |
| SampleBankingApp.csproj | 16 | `System.IdentityModel.Tokens.Jwt` 7.0.0 is outdated. | Upgrade to the latest 7.x or 8.x version. |
| SampleBankingApp.csproj | 8–9 | `DebugSymbols=true` and `DebugType=full` are set in the unconditional `PropertyGroup`, so debug symbols are embedded in release builds. | Move these into a `<PropertyGroup Condition="'$(Configuration)'=='Debug'">` block. |
| appsettings.json | 1–24 | No `appsettings.Production.json` exists for environment-specific overrides (connection strings, log levels, secrets). | Create `appsettings.Production.json` with production-safe defaults. |
| appsettings.json | 3 | Production DB connection string with `sa` credentials is in the default (non-environment-specific) config file. | Remove from source control; use a secrets manager. |
| appsettings.json | 6 | JWT `SecretKey` is `"mysecretkey"` — trivially guessable. | Use a cryptographically random 256-bit key from a secrets manager. |

---

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|------|------|-------|-----|
| (project) | — | No test project exists in the repository; zero unit or integration tests are present. | Create a `SampleBankingApp.Tests` project with xUnit/NUnit and cover the scenarios below. |
| TransactionService.cs | 23–61 | `Transfer` has no tests for: amount = 0, negative amount, insufficient funds (balance exactly equals amount but fee pushes it over), self-transfer, non-existent toUserId, fee calculation correctness. | Write boundary-condition tests for each scenario. |
| TransactionService.cs | 63–75 | `Deposit` has no tests for: amount = 0, amount = 1 (minimum), amount = 1000000 (maximum), amount = 1000001 (exceeds cap), interest bonus calculation. | Write boundary-condition tests. |
| UserService.cs | 68–83 | `GetUsersPage` has no tests for pagination; the off-by-one (`page * pageSize` vs `(page-1) * pageSize`) would be caught by a test asserting page 1 returns the first N rows. | Write tests for page 1, page 2, and page beyond total. |
| AuthService.cs | 28–59 | `Login` has no tests for: valid credentials, invalid password, SQL injection attempt in username, admin bypass, inactive user. | Write tests including injection payloads and the bypass path. |
| AuthService.cs | 68–89 | `GenerateJwtToken` has no tests verifying token structure, claims, expiry, and that the token can be validated by the configured `TokenValidationParameters`. | Write a round-trip test: generate → validate. |
| StringHelper.cs | 11–18 | `IsValidEmail` has no tests for: valid email, 254-char email, 255-char email, missing `@`, missing domain, multiple `@`. | Write boundary and negative tests. |
| StringHelper.cs | 20–27 | `IsValidUsername` has no tests for: 2-char (too short), 3-char (minimum), 20-char (maximum), 21-char (too long), special characters. | Write boundary tests. |
| TransactionService.cs | 23–61 | `Transfer` has no test verifying that the fee is correctly deducted (balance decreases by `amount + fee`, not just `amount`). | Write a test asserting exact post-transfer balances. |
| TransactionService.cs | 77–85 | `IsWithinDailyLimit` has no tests and is never called; if wired up, it needs tests for 0, 9, 10, and 11 transactions on the same day. | Write tests for the boundary at the limit. |
| UserController.cs | 39–54 | `UpdateUser` has no tests for: updating own record, updating another user's record (authorization), invalid email, invalid username. | Write authorization and validation tests. |