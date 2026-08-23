<workspace_state>
Milestone: Peer code review of branch 'Jack-3.8-27B-Coder' commit 1c6f8a7a5126467d81f469b8f52b22faf242261f.
Files under review: AuthController.cs, TransactionController.cs, UserController.cs, DatabaseHelper.cs, StringHelper.cs, Transaction.cs, User.cs, Program.cs, SampleBankingApp.csproj, AuthService.cs, EmailService.cs, TransactionService.cs, UserService.cs, appsettings.json.
Active objective: Produce a 10-category Markdown report covering Security, Logic Errors, Error Handling, Resource Leaks, Null Reference Risks, Dead Code, Magic Strings/Numbers, Anti-patterns, Configuration Issues, and Missing Unit Tests.
Unresolved: None — all source is available and fully readable.
</workspace_state>
<grounded_source>
All 14 source files provided in the user message constitute the complete evidence base. No external context is required or assumed.
</grounded_source>
<anchor_fact ID="FILE_COUNT">14 source files in SampleBankingApp project (net8.0, ASP.NET Core Web API)</anchor_fact>
<anchor_fact ID="TEST_PROJECT">No test project exists in the provided source files</anchor_fact>
<anchor_fact ID="DB_HELPER_CONNECTION_LEAK">DatabaseHelper.GetOpenConnection returns an open SqlConnection with no disposal contract; ExecuteQuery and TableExists never close it</anchor_fact>
<anchor_fact ID="PAGINATION_FORMULA">UserService.GetUsersPage line 72: int skip = page * pageSize (off-by-one; should be (page-1)*pageSize)</anchor_fact>
<anchor_fact ID="BALANCE_CHECK_MISMATCH">TransactionService.Transfer line 42 checks fromBalance >= amount, but line 44 deducts amount + fee, allowing negative balance</anchor_fact>
<pitfall_check>
Independent Falsification Check: What does the evidence actually support?
Requested Outcome: A thorough 10-category code review report with per-occurrence rows.
Independent Evidence: All 14 files are fully present and readable. Every issue cited below is directly observable in the provided source text.
Observed Configuration: A single-branch ASP.NET Core 8.0 Web API with ADO.NET data access, JWT auth, SMTP email, and no test project.
Proposed Configuration: N/A — this is a static review, not a counterfactual system change.
Counterfactual Gap: None applicable.
Unstated Premise / Falsifiable Crux: The review assumes the provided files constitute the entire codebase (no other callers exist outside these files). If external callers exist, dead-code findings could be invalidated.
Evidence Classification: SUPPORTED — every finding is directly grounded in the visible source text.
Primary Failure Mode: None — the task is enumeration, not inference.
Calibration Rule: Report only issues directly observable in the provided source; do not speculate about files not shown.
</pitfall_check>

FINAL ANSWER:

# Code Review Report — Branch `Jack-3.8-27B-Coder` (commit `1c6f8a7a5126467d81f469b8f52b22faf242261f`)

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 29 | `ExecuteQuery` builds SQL via string interpolation of `tableName` and `whereClause`, enabling SQL injection. | Use parameterized queries or a whitelist of allowed table names. |
| AuthService.cs | 32 | `Login` interpolates `username` and `hashedPassword` directly into a SQL SELECT, enabling SQL injection. | Use a parameterized query with `@Username` and `@Password` parameters. |
| TransactionService.cs | 47 | `Transfer` interpolates `newFromBalance` and `fromUserId` into an UPDATE statement. | Use a parameterized query via `ExecuteQuerySafe` or a new parameterized non-query helper. |
| TransactionService.cs | 48 | `Transfer` interpolates `newToBalance` and `toUserId` into a second UPDATE statement. | Use a parameterized query. |
| TransactionService.cs | 71 | `Deposit` interpolates `amount + interestBonus` and `userId` into an UPDATE statement. | Use a parameterized query. |
| TransactionService.cs | 89-90 | `RecordTransaction` interpolates `fromId`, `toId`, `amount`, `type`, and `description` into an INSERT statement. | Use a parameterized query. |
| UserService.cs | 47 | `UpdateUser` interpolates `email`, `username`, and `id` into an UPDATE statement. | Use a parameterized query. |
| UserService.cs | 61 | `DeleteUser` interpolates `id` into a DELETE statement. | Use a parameterized query. |
| UserService.cs | 99 | `SearchUsers` interpolates `query` into a LIKE clause, enabling SQL injection. | Use a parameterized query with `LIKE @Pattern` and build the pattern safely. |
| DatabaseHelper.cs | 16 | Fallback connection string hardcodes `sa` / `Admin1234!` credentials in source. | Remove the fallback; fail fast if no connection string is configured. |
| AuthService.cs | 17 | `AdminBypassPassword` constant hardcodes a backdoor password `"SuperAdmin2024"`. | Remove the bypass entirely; authenticate via the normal path. |
| AuthService.cs | 53 | `Login` grants a `SuperAdmin` user (Id=0) when username is `"admin"` and password matches the bypass constant. | Remove the admin bypass logic. |
| appsettings.json | 3 | Production database credentials (`sa` / `Admin1234!`) committed to source control. | Use a secrets manager or environment variable; remove from VCS. |
| appsettings.json | 6 | JWT secret key `"mysecretkey"` is a trivially guessable value committed to source control. | Use a strong, randomly generated key stored in a secrets manager. |
| appsettings.json | 14 | SMTP password `"EmailPass99"` committed to source control. | Move to a secrets manager or environment variable. |
| AuthService.cs | 61-66 | `HashPasswordMd5` uses MD5, which is cryptographically broken and unsalted. | Use a salted adaptive hash such as BCrypt, Argon2, or PBKDF2. |
| AuthService.cs | 91-96 | `HashPasswordSha1` uses SHA1, which is deprecated and unsalted. | Remove entirely (dead code) or replace with a strong KDF. |
| Program.cs | 24 | `ValidateLifetime = false` allows expired or never-expiring JWTs to be accepted. | Set `ValidateLifetime = true` and configure `ClockSkew`. |
| Program.cs | 38 | CORS policy uses `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`, an open CORS configuration. | Restrict to specific origins, methods, and headers appropriate for the API. |
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, exposing stack traces in production. | Gate behind `app.Environment.IsDevelopment()`. |
| Program.cs | 36 | `app.UseHttpsRedirection()` is commented out, allowing plaintext HTTP. | Uncomment and ensure HSTS is configured. |
| EmailService.cs | 29 | `EnableSsl = false` transmits email credentials and content in plaintext. | Set `EnableSsl = true` and use port 587 or 465. |
| UserController.cs | 39 | `UpdateUser` has no ownership check; any authenticated user can modify any user. | Verify the requesting user's Id matches the target Id or require an admin role. |
| UserController.cs | 57 | `DeleteUser` has no ownership check; any authenticated user can delete any user. | Verify ownership or require an admin role. |
| UserController.cs | 22 | `GetUser` has no ownership check; any authenticated user can read any user's data. | Verify ownership or require an admin role. |
| TransactionController.cs | 49 | `Refund` has no ownership check on the transaction; any authenticated user can refund any transaction. | Verify the transaction belongs to the requesting user. |
| UserController.cs | 79 | `GetAuditLog` has no role restriction; any authenticated user can read the audit trail. | Add `[Authorize(Roles = "Admin")]` or similar. |
| SampleBankingApp.csproj | 8-9 | `DebugSymbols=true` and `DebugType=full` are set unconditionally, shipping debug symbols in release builds. | Gate behind a `Debug` conditional or remove for release. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserService.cs | 72 | `GetUsersPage` computes `skip = page * pageSize`, producing an off-by-one error (page 1 skips the first page). | Change to `skip = (page - 1) * pageSize`. |
| TransactionService.cs | 42 | `Transfer` checks `fromBalance >= amount` but then deducts `amount + fee`, allowing the balance to go negative. | Change the check to `fromBalance >= totalDebit` (i.e., `amount + fee`). |
| TransactionService.cs | 23 | `Transfer` has no self-transfer check; a user can transfer to their own account. | Add `if (fromUserId == toUserId) return (false, "Cannot transfer to yourself");`. |
| TransactionService.cs | 68 | `Deposit` applies a 5% interest bonus (`0.05m`), which appears to be an incorrect rate (likely intended 0.5% or 1%). | Confirm the intended rate with stakeholders and use the correct constant. |
| TransactionService.cs | 68 | `Deposit` multiplies by a redundant `* 1`, obscuring intent. | Remove the `* 1` or replace with a named multiplier. |
| TransactionService.cs | 77-85 | `IsWithinDailyLimit` is defined but never called, so the 10-transaction daily limit is never enforced. | Call `IsWithinDailyLimit(fromUserId)` at the top of `Transfer` and reject if the limit is exceeded. |
| TransactionService.cs | 65 | `Deposit` rejects `amount <= 0` but the upper bound `1000000` is a magic number with no named constant. | Extract to a named constant such as `MaxDepositAmount`. |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserController.cs | 50 | `UpdateUser` catches a broad `Exception` and returns `ex.Message` to the client. | Catch specific exceptions; return a generic error message and log the detail server-side. |
| UserController.cs | 48 | `UpdateUser` returns `ex.Message` from an `ArgumentException` catch directly to the HTTP client. | Return a sanitized message; log the full exception server-side. |
| UserController.cs | 64 | `DeleteUser` catches a broad `Exception`. | Catch specific exceptions (e.g., `SqlException`, `ArgumentException`). |
| UserService.cs | 105 | `SearchUsers` catches `Exception` and returns an empty `List<User>`, making errors indistinguishable from "no results." | Rethrow or return a result object with an error flag; log the exception. |
| TransactionService.cs | 47-48 | `Transfer` performs two separate `ExecuteNonQuery` calls without a database transaction, risking partial writes. | Wrap both updates in a `SqlTransaction` or use a stored procedure with atomicity. |
| TransactionService.cs | 52 | `SendTransferNotification` is called after the DB writes have committed; if it throws, the transfer is already persisted but the caller receives an error. | Move email sending to an outbox pattern or a background queue after the transaction commits. |
| AuthController.cs | 20 | `Login` endpoint has no rate limiting or account lockout, enabling brute-force attacks. | Add rate limiting (e.g., `Microsoft.AspNetCore.RateLimiting`) and temporary account lockout after N failures. |
| TransactionController.cs | 51-59 | `Refund` catches `NotImplementedException` and returns a 500 status, but the method is wired to a live endpoint. | Remove the endpoint until implemented, or return `501 Not Implemented`. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 19-24 | `GetOpenConnection` returns an open `SqlConnection` with no documented disposal contract; callers may leak it. | Change to a `using` pattern internally, or document that the caller must dispose; better: remove the public method. |
| DatabaseHelper.cs | 26-34 | `ExecuteQuery` calls `GetOpenConnection` but never closes or disposes the connection or command. | Wrap in `using` blocks or use a single `using` scope. |
| DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` calls `GetOpenConnection` and calls `Close()` but does not `Dispose()`; if `ExecuteNonQuery` throws, the connection is never closed. | Use `using` blocks for both connection and command. |
| DatabaseHelper.cs | 59-65 | `TableExists` opens a connection but never closes or disposes it. | Wrap in a `using` block. |
| AuthService.cs | 34-38 | `Login` opens a `SqlConnection` and `SqlDataReader` but never closes or disposes either. | Wrap in `using` blocks. |
| EmailService.cs | 16 | `SmtpClient` is held as an instance field (`_smtpClient`), is not thread-safe, and its socket is never released. | Create the `SmtpClient` per-send inside a `using` block, or use a thread-safe mail library. |
| EmailService.cs | 39 | `SendTransferNotification` creates a `MailMessage` but never disposes it. | Wrap in a `using` block. |
| EmailService.cs | 69 | `SendWelcomeEmail` creates a `MailMessage` but never disposes it. | Wrap in a `using` block. |
| EmailService.cs | 89 | `SendWelcomeEmailHtml` creates a `MailMessage` but never disposes it. | Wrap in a `using` block. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 28 | `jwtSecret!` uses the null-forgiving operator on a config value that may be null at startup. | Validate the config value at startup and fail fast if null. |
| AuthService.cs | 70 | `GenerateJwtToken` uses `_config["Jwt:SecretKey"]!` with null-forgiving; a missing config key causes a runtime crash. | Validate at startup or handle null explicitly. |
| AuthService.cs | 34 | `Login` passes `_config.GetConnectionString("DefaultConnection")` to `SqlConnection`; if null, the constructor throws. | Validate the connection string at startup. |
| TransactionService.cs | 36 | `Transfer` accesses `fromUserTable.Rows[0]` without checking `Rows.Count > 0`; a missing user causes an `IndexOutOfRangeException`. | Check `Rows.Count > 0` and return an error if the user does not exist. |
| TransactionService.cs | 37 | `Transfer` accesses `toUserTable.Rows[0]` without checking `Rows.Count > 0`. | Check `Rows.Count > 0` and return an error if the user does not exist. |
| TransactionService.cs | 83 | `IsWithinDailyLimit` accesses `table.Rows[0]` without checking `Rows.Count > 0`. | Add a count check (though COUNT(*) always returns one row, defensive coding is prudent). |
| TransactionController.cs | 27 | `int.Parse(userIdClaim!)` uses null-forgiving on a claim that may be absent if the JWT is malformed. | Check for null and return 401 if the claim is missing. |
| TransactionController.cs | 41 | `int.Parse(userIdClaim!)` has the same null-claim risk as line 27. | Check for null and return 401. |
| EmailService.cs | 22 | `_config["Email:SmtpHost"]` may be null and is passed directly to the `SmtpClient` constructor. | Validate the config value or provide a default. |
| EmailService.cs | 24 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — the `??` handles null, but if the value is a non-numeric string, `int.Parse` throws. | Use `int.TryParse` with a fallback. |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 59 | `TableExists` is defined but never called in any source file. | Remove or wire it into a migration/health-check flow. |
| DatabaseHelper.cs | 68 | `ExecuteQueryWithParams` is marked `[Obsolete]` and is never called. | Remove it. |
| StringHelper.cs | 11 | `IsValidEmail` is defined but never called in any source file. | Remove or integrate into user registration/update validation. |
| StringHelper.cs | 20 | `IsValidUsername` is defined but never called in any source file. | Remove or integrate into user registration/update validation. |
| StringHelper.cs | 29 | `JoinWithSeparator` is defined but never called (the broken O(n²) version). | Remove it. |
| StringHelper.cs | 38 | `JoinWithSeparatorFixed` is defined but never called. | Remove it (or replace `JoinWithSeparator` and keep one). |
| StringHelper.cs | 43 | `MaskAccountNumber` is defined but never called in any source file. | Remove or wire into a display layer. |
| StringHelper.cs | 54 | `ObfuscateAccount` is defined but never called in any source file. | Remove or wire into a display layer. |
| StringHelper.cs | 59 | `ToTitleCase` is defined but never called in any source file. | Remove. |
| StringHelper.cs | 65 | `IsBlank` is defined but never called in any source file. | Remove. |
| AuthService.cs | 91 | `HashPasswordSha1` is defined but never called in any source file. | Remove it. |
| AuthService.cs | 98 | `ValidateToken` is defined but never called in any source file. | Remove it. |
| AuthService.cs | 103 | `ValidateToken` contains unreachable code after `return true;` (lines 105-107). | Remove the dead code or fix the method. |
| EmailService.cs | 63 | `SendWelcomeEmail` is defined but never called in any source file. | Remove or wire into a registration flow. |
| EmailService.cs | 86 | `SendWelcomeEmailHtml` is defined but never called in any source file. | Remove or wire into a registration flow. |
| TransactionService.cs | 77 | `IsWithinDailyLimit` is defined but never called, so the daily limit is never enforced. | Call it in `Transfer` or remove it. |
| TransactionService.cs | 94 | `FormatCurrency` is defined but never called in any source file. | Remove it. |
| TransactionService.cs | 99 | `RefundTransaction` contains `throw new NotImplementedException()` in code wired to a live controller endpoint. | Implement the method or remove the endpoint. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 65 | `1000000` is used inline as the maximum deposit cap. | Extract to a named constant such as `MaxDepositAmount`. |
| TransactionService.cs | 68 | `0.05m` is used inline as the deposit interest rate. | Extract to a named constant such as `DepositInterestRate`. |
| UserService.cs | 22 | `1000000` is used inline as the maximum user ID. | Extract to a shared named constant. |
| UserService.cs | 42 | `1000000` is repeated as the maximum user ID in `UpdateUser`. | Use the same shared constant. |
| UserService.cs | 56 | `1000000` is repeated as the maximum user ID in `DeleteUser`. | Use the same shared constant. |
| UserService.cs | 70 | `50` is used inline as the maximum page size. | Extract to a named constant such as `MaxPageSize`. |
| StringHelper.cs | 13 | `254` is used inline as the maximum email length. | Extract to a named constant. |
| StringHelper.cs | 22 | `3` and `20` are used inline as username length bounds. | Extract to named constants. |
| AuthService.cs | 84 | `30` is used inline as the JWT expiry in days. | Extract to a named constant or config value. |
| EmailService.cs | 40 | `"notifications@company.com"` is hardcoded as the sender address. | Move to configuration. |
| EmailService.cs | 67 | `"support@company.com"` is hardcoded in the welcome email body. | Move to configuration. |
| EmailService.cs | 69 | `"notifications@company.com"` is repeated as the sender in `SendWelcomeEmail`. | Use a shared constant or config value. |
| EmailService.cs | 89 | `"notifications@company.com"` is repeated again in `SendWelcomeEmailHtml`. | Use the same shared constant or config value. |
| AuthService.cs | 53 | `"admin"` is a hardcoded string literal for the bypass username. | Remove the bypass entirely. |
| AuthService.cs | 55 | `"admin"` and `"SuperAdmin"` are hardcoded role/username literals. | Remove the bypass entirely. |
| TransactionService.cs | 90 | `'Completed'` is a hardcoded status string in the INSERT. | Use a named constant or enum. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 31-33 | `JoinWithSeparator` uses string concatenation (`result +=`) inside a loop, producing O(n²) behavior. | Replace with `string.Join(separator, items)` or `StringBuilder`. |
| UserService.cs | 87-91 | `GetAuditReport` uses string concatenation (`report +=`) inside a loop. | Use `string.Join("\n", _auditLog)` or `StringBuilder`. |
| StringHelper.cs | 16 | `IsValidEmail` creates a `new Regex(...)` on every call. | Cache as a `private static readonly Regex`. |
| StringHelper.cs | 25 | `IsValidUsername` creates a `new Regex(...)` on every call. | Cache as a `private static readonly Regex`. |
| UserService.cs | 10 | `_auditLog` is a `static List<string>` accessed from multiple threads without synchronization. | Use `ConcurrentQueue<string>` or add a lock. |
| UserService.cs | 11 | `_requestCount` is a `static int` incremented without synchronization. | Use `Interlocked.Increment` or `ConcurrentBag`. |
| StringHelper.cs | 65-71 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Replace with the standard library method. |
| StringHelper.cs | 38-41 | `JoinWithSeparatorFixed` reimplements `string.Join`. | Remove it and call `string.Join` directly. |
| DatabaseHelper.cs | 19-24 | `GetOpenConnection` leaks resource ownership to callers with no documented disposal contract. | Remove the public method; encapsulate connection lifecycle internally. |
| UserService.cs | 20-23 | `GetUserById` repeats the `id <= 0` / `id > 1000000` validation block. | Extract to a shared `ValidateUserId(int id)` private method. |
| UserService.cs | 40-43 | `UpdateUser` repeats the same `id <= 0` / `id > 1000000` validation block. | Use the shared `ValidateUserId` method. |
| UserService.cs | 54-57 | `DeleteUser` repeats the same `id <= 0` / `id > 1000000` validation block. | Use the shared `ValidateUserId` method. |
| TransactionService.cs | 23-61 | `Transfer` carries at least four distinct responsibilities: input validation, balance/fee calculation, dual DB writes, and email notification. | Split into `ValidateTransfer`, `ExecuteTransferWrites`, and `NotifyTransfer` private helpers. |
| AuthService.cs | 28-59 | `Login` carries at least three distinct responsibilities: password hashing, SQL query execution, and admin-bypass logic. | Split into `AuthenticateUser` and remove the bypass. |
| EmailService.cs | 34-61 | `SendTransferNotification` carries message construction, retry-loop logic, and SMTP sending. | Split into `BuildTransferMessage` and `SendWithRetry`. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally regardless of environment. | Gate behind `if (app.Environment.IsDevelopment())`. |
| Program.cs | 24 | `ValidateLifetime = false` on JWT token validation parameters. | Set to `true` and configure `ClockSkew`. |
| Program.cs | 36 | `app.UseHttpsRedirection()` is commented out. | Uncomment it. |
| Program.cs | 38 | CORS uses `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`, an overly permissive policy. | Define named policies with specific origins and methods. |
| appsettings.json | 18-20 | Logging level is set to `"Debug"` for `Default`, `Microsoft`, and `System` namespaces, which is inappropriate for production. | Set to `"Information"` or `"Warning"` in production config. |
| SampleBankingApp.csproj | 14 | `System.Data.SqlClient` version 4.8.6 is the legacy, unsupported package. | Migrate to `Microsoft.Data.SqlClient` (latest stable). |
| SampleBankingApp.csproj | 15 | `Newtonsoft.Json` version 12.0.3 is outdated and has known deserialization vulnerabilities. | Upgrade to 13.0.3+ or use `System.Text.Json`. |
| SampleBankingApp.csproj | 16 | `System.IdentityModel.Tokens.Jwt` version 7.0.0 is outdated. | Upgrade to 7.0.3+ or align with the `Microsoft.AspNetCore.Authentication.JwtBearer` version. |
| SampleBankingApp.csproj | — | No `appsettings.Production.json` exists for environment-specific overrides. | Add a production config file with appropriate log levels and no debug settings. |
| appsettings.json | 12 | `SmtpPort` is a JSON number (`25`) but the code reads it as a string via `IConfiguration`. | Store as a string `"25"` or use `IConfiguration.GetSection("Email").Get<T>()` with a typed options class. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|------|------|-------|-----|
| (project) | — | No test project exists in the repository. | Create a `SampleBankingApp.Tests` xUnit or NUnit project. |
| TransactionService.cs | 23 | `Transfer` has no tests for boundary conditions: balance exactly equals amount, balance equals amount + fee − ε, negative amount, self-transfer. | Write tests covering all boundary and error paths. |
| TransactionService.cs | 39 | Fee calculation (`amount * 0.015m`) has no test verifying rounding behavior at decimal boundaries. | Add tests for amounts that produce repeating decimals. |
| TransactionService.cs | 63 | `Deposit` has no tests for boundary values: amount = 0, amount = 1, amount = 1000000, amount = 1000001. | Add boundary tests. |
| TransactionService.cs | 68 | Interest bonus calculation has no test verifying the 5% rate is applied correctly. | Add a test asserting the exact credited amount. |
| UserService.cs | 68 | `GetUsersPage` has no tests for pagination: page 1, page 2, page beyond total, pageSize = 50, pageSize = 51. | Add pagination tests verifying the OFFSET/FETCH logic. |
| AuthService.cs | 28 | `Login` has no tests for valid credentials, invalid credentials, null/empty username, and the admin bypass path. | Add auth-flow tests (remove the bypass test after removing the feature). |
| AuthService.cs | 68 | `GenerateJwtToken` has no tests verifying token structure, claims, issuer, audience, and expiry. | Add token-structure tests. |
| TransactionController.cs | 24 | `Transfer` endpoint has no tests for missing auth claim, malformed claim, and successful transfer. | Add controller integration tests. |
| StringHelper.cs | 11 | `IsValidEmail` has no tests for boundary emails (254 chars, 255 chars, missing @, multiple @). | Add validation-boundary tests. |
| StringHelper.cs | 20 | `IsValidUsername` has no tests for boundary lengths (2, 3, 20, 21 chars) and invalid characters. | Add validation-boundary tests. |