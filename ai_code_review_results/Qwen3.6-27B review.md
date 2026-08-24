# Code Review Report

**Branch:** `main` | **Commit:** `363e42f93d3bd87df50d57d2f6f3a3d4d3fe5ca6`

---

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 32 | `Login` builds SQL via string interpolation of `username` and `hashedPassword`, enabling SQL injection. | Use parameterized query with `@Username` and `@Password` parameters. |
| TransactionService.cs | 47 | `Transfer` interpolates `newFromBalance` and `fromUserId` directly into an UPDATE statement. | Use parameterized query via `ExecuteQuerySafe` or a new parameterized `ExecuteNonQuery`. |
| TransactionService.cs | 48 | `Transfer` interpolates `newToBalance` and `toUserId` directly into an UPDATE statement. | Use parameterized query. |
| TransactionService.cs | 71 | `Deposit` interpolates `amount + interestBonus` and `userId` into an UPDATE statement. | Use parameterized query. |
| TransactionService.cs | 89–90 | `RecordTransaction` interpolates `fromId`, `toId`, `amount`, `type`, and `description` into an INSERT statement. | Use parameterized query. |
| UserService.cs | 47 | `UpdateUser` interpolates `email`, `username`, and `id` into an UPDATE statement. | Use parameterized query. |
| UserService.cs | 61 | `DeleteUser` interpolates `id` into a DELETE statement. | Use parameterized query. |
| UserService.cs | 99 | `SearchUsers` passes user-supplied `query` into a `LIKE '%{query}%'` clause via `ExecuteQuery`, enabling SQL injection. | Use a parameterized LIKE query with `@Pattern` parameter. |
| DatabaseHelper.cs | 29 | `ExecuteQuery` accepts raw `tableName` and `whereClause` strings that are concatenated into SQL, allowing injection from any caller. | Remove this method or validate/whitelist table names and require parameterized where-clauses. |
| DatabaseHelper.cs | 16 | Fallback connection string contains hardcoded `sa` credentials (`Password=Admin1234!`). | Remove the fallback; fail fast if no connection string is configured. |
| appsettings.json | 3 | Production database credentials (`sa` / `Admin1234!`) are committed to source control. | Move to a secrets manager or environment variable; remove from VCS. |
| appsettings.json | 6 | JWT secret key `"mysecretkey"` is hardcoded and trivially guessable. | Use a cryptographically random 256-bit key stored in a secrets manager. |
| appsettings.json | 14 | SMTP password `"EmailPass99"` is committed to source control. | Move to environment variable or secrets manager. |
| AuthService.cs | 17 | Hardcoded admin bypass password `"SuperAdmin2024"` allows backdoor access. | Remove the bypass entirely; authenticate admin through the normal flow. |
| AuthService.cs | 61–66 | `HashPasswordMd5` uses unsalted MD5, which is cryptographically broken. | Use PBKDF2, bcrypt, or Argon2 with a per-user salt. |
| AuthService.cs | 91–96 | `HashPasswordSha1` uses unsalted SHA-1, which is deprecated for password hashing. | Remove; use a modern adaptive hash function. |
| Program.cs | 24 | `ValidateLifetime = false` means expired JWTs are never rejected. | Set `ValidateLifetime = true`. |
| Program.cs | 38 | CORS policy allows any origin, any method, and any header simultaneously. | Restrict to specific origins, methods, and headers. |
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, exposing stack traces in production. | Guard with `if (app.Environment.IsDevelopment())`. |
| Program.cs | 36 | `UseHttpsRedirection()` is commented out, allowing plaintext HTTP. | Uncomment and enforce HTTPS. |
| UserController.cs | 39 | `UpdateUser` has no ownership check; any authenticated user can modify any user's record. | Verify `id` matches the current user's ID or require an admin role. |
| UserController.cs | 57 | `DeleteUser` has no ownership check; any authenticated user can delete any user. | Verify `id` matches the current user or require admin role. |
| UserController.cs | 22 | `GetUser` has no ownership or role check; any authenticated user can read any user's PII. | Restrict to self or admin role. |
| UserController.cs | 32 | `GetUsers` has no role check; any authenticated user can enumerate all users. | Require admin role. |
| UserController.cs | 72 | `SearchUsers` has no role check; any authenticated user can search all users. | Require admin role. |
| UserController.cs | 79 | `GetAuditLog` has no role check; any authenticated user can read the audit log. | Require admin role. |
| AuthController.cs | 19–31 | No rate limiting or account lockout on the login endpoint, enabling brute-force attacks. | Add rate limiting middleware and lockout after N failed attempts. |
| EmailService.cs | 29 | `EnableSsl = false` sends SMTP credentials in plaintext. | Set `EnableSsl = true` and use port 587 with STARTTLS. |

---

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserService.cs | 72 | `GetUsersPage` computes `skip = page * pageSize`, so page 1 skips the first `pageSize` rows (off-by-one). | Change to `skip = (page - 1) * pageSize`. |
| TransactionService.cs | 42 | `Transfer` checks `fromBalance >= amount` but then deducts `amount + fee`, so a balance between `amount` and `amount + fee` produces a negative balance. | Change the check to `fromBalance >= totalDebit` (i.e., `amount + fee`). |
| TransactionService.cs | 25 | `Transfer` rejects `amount < 0` but allows `amount == 0`, permitting a zero-value transfer that still incurs a fee. | Change to `amount <= 0`. |
| TransactionService.cs | 23 | `Transfer` has no self-transfer check; a user can transfer to their own account. | Add `if (fromUserId == toUserId) return (false, "Cannot transfer to yourself");`. |
| TransactionService.cs | 68 | `Deposit` computes `interestBonus = amount * 0.05m * 1`; the `* 1` is a no-op that obscures intent, and the 5% rate is unexplained. | Remove the `* 1` and extract the rate to a named constant or config value. |
| TransactionService.cs | 65 | `Deposit` caps at `1000000` but the cap is a magic number with no named constant. | Extract to a `const decimal MaxDepositAmount`. |

---

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 47–50 | `Transfer` performs two separate `ExecuteNonQuery` calls (debit and credit) without a database transaction; a failure between them leaves balances inconsistent. | Wrap both updates and the INSERT in a single `SqlTransaction`. |
| TransactionService.cs | 70–73 | `Deposit` performs an UPDATE and an INSERT without a transaction. | Wrap in a `SqlTransaction`. |
| TransactionService.cs | 52–55 | `Transfer` sends an email after DB writes have committed; if `SendTransferNotification` throws, the caller receives a 500 even though the transfer succeeded. | Wrap the email call in a try-catch and log the failure, or use an outbox pattern. |
| UserService.cs | 105–108 | `SearchUsers` catches a broad `Exception` and returns an empty list, making it impossible for the caller to distinguish "no results" from a database error. | Catch specific exceptions, log them, and rethrow or return an error indicator. |
| UserController.cs | 48 | `UpdateUser` returns `ex.Message` (an `ArgumentException`) directly to the HTTP client, potentially leaking internal details. | Return a generic error message; log the exception server-side. |
| UserController.cs | 52 | `UpdateUser` returns `ex.Message` from a catch-all `Exception` to the client, potentially exposing stack-trace details. | Return a generic 500 message; log the full exception. |
| TransactionController.cs | 27 | `int.Parse(userIdClaim!)` will throw `FormatException` or `ArgumentNullException` if the claim is missing or non-numeric, producing an unhandled 500. | Use `int.TryParse` and return 401 on failure. |
| TransactionController.cs | 41 | `int.Parse(userIdClaim!)` has the same unguarded parse as `Transfer`. | Use `int.TryParse` and return 401 on failure. |
| AuthController.cs | 22 | `request` is used without a null check; if the body is missing, `request.Username` throws `NullReferenceException`. | Add `[FromBody] LoginRequest? request` and null-check, or rely on model validation with `[Required]`. |
| EmailService.cs | 75–78 | `SendWelcomeEmail` catches a broad `Exception` and only writes to `Console.WriteLine`, silently swallowing the failure. | Log via `ILogger` and consider whether the caller needs to know. |
| TransactionController.cs | 48–59 | `Refund` catches only `NotImplementedException`; any other exception (DB error, etc.) propagates as an unhandled 500 with stack trace. | Add a general catch or handle via middleware. |

---

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 21–23 | `GetOpenConnection` returns an open `SqlConnection` with no `using` contract; callers like `ExecuteQuery` and `ExecuteNonQuery` may not dispose it. | Return a `DbConnection` wrapped in a `using` at the call site, or encapsulate the open/close within each method. |
| DatabaseHelper.cs | 28–33 | `ExecuteQuery` calls `GetOpenConnection` but never closes or disposes the connection, command, or adapter. | Wrap connection, command, and adapter in `using` statements. |
| DatabaseHelper.cs | 52–56 | `ExecuteNonQuery` calls `GetOpenConnection`, closes the connection, but does not dispose the `SqlCommand`; if `ExecuteNonQuery` throws, the connection is never closed. | Use `using` for both connection and command. |
| DatabaseHelper.cs | 44 | `ExecuteQuerySafe` creates a `SqlDataAdapter` that is never disposed. | Wrap the adapter in a `using` statement. |
| DatabaseHelper.cs | 74 | `ExecuteQueryWithParams` creates a `SqlDataAdapter` that is never disposed. | Wrap the adapter in a `using` statement. |
| AuthService.cs | 34–38 | `Login` creates `SqlConnection`, `SqlCommand`, and `SqlDataReader` without any `using` or `Close()`/`Dispose()` calls. | Wrap all three in `using` statements. |
| EmailService.cs | 16 | `SmtpClient` is held as an instance field; `SmtpClient` is not thread-safe and the underlying socket is never released. | Create a new `SmtpClient` per send operation and dispose it, or use a thread-safe wrapper. |
| EmailService.cs | 39–43 | `SendTransferNotification` creates a `MailMessage` (which implements `IDisposable`) but never disposes it. | Wrap in a `using` statement. |
| EmailService.cs | 69 | `SendWelcomeEmail` creates a `MailMessage` but never disposes it. | Wrap in a `using` statement. |
| EmailService.cs | 89 | `SendWelcomeEmailHtml` creates a `MailMessage` but never disposes it. | Wrap in a `using` statement. |

---

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 28 | `Encoding.UTF8.GetBytes(jwtSecret!)` will throw `ArgumentNullException` if the config key is missing; the `!` only suppresses the compiler warning. | Null-check `jwtSecret` and throw a clear configuration error at startup. |
| AuthService.cs | 34 | `_config.GetConnectionString("DefaultConnection")` can return `null`, which is passed directly to the `SqlConnection` constructor. | Null-check and throw a descriptive exception. |
| AuthService.cs | 70 | `_config["Jwt:SecretKey"]!` will throw if the key is absent. | Null-check and fail fast. |
| TransactionController.cs | 27 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Null-check `userIdClaim` before parsing. |
| TransactionController.cs | 41 | Same unguarded `int.Parse(userIdClaim!)` as in `Transfer`. | Null-check before parsing. |
| TransactionService.cs | 36 | `fromUserTable.Rows[0]` is accessed without checking `Rows.Count > 0`; if the user does not exist, this throws `IndexOutOfRangeException`. | Check `Rows.Count == 0` and return an error. |
| TransactionService.cs | 37 | `toUserTable.Rows[0]` is accessed without a row-count check. | Check `Rows.Count == 0` and return an error. |
| TransactionService.cs | 53 | `fromUserTable.Rows[0]["Email"]` is cast to `string` without a null guard; if the column is NULL in the DB, this throws. | Use `Convert.ToString` or a null-coalescing cast. |
| TransactionService.cs | 55 | `toUserTable.Rows[0]["Username"]` has the same null-cast risk. | Use a safe cast. |
| EmailService.cs | 22 | `_config["Email:SmtpHost"]` can be `null`, passed to the `SmtpClient` constructor. | Null-check and throw a configuration error. |
| EmailService.cs | 26–27 | `_config["Email:Username"]` and `_config["Email:Password"]` can be `null`, passed to `NetworkCredential`. | Null-check both values. |
| AuthController.cs | 22 | `request` (model-bound) is used without a null check; a missing body makes `request.Username` throw. | Add a null check or use `[Required]` attributes. |
| TransactionController.cs | 29 | `request` in `Transfer` is used without a null check. | Add a null check. |
| TransactionController.cs | 43 | `request` in `Deposit` is used without a null check. | Add a null check. |
| UserController.cs | 43 | `request` in `UpdateUser` is used without a null check. | Add a null check. |
| UserController.cs | 74 | `query` parameter in `SearchUsers` is a non-nullable `string` but can arrive as `null` from the query string. | Use `string? query` and handle null, or add `[Required]`. |

---

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 59 | `TableExists` is never called anywhere in the codebase. | Remove the method. |
| DatabaseHelper.cs | 68 | `ExecuteQueryWithParams` is marked `[Obsolete]` and is never called. | Remove the method. |
| StringHelper.cs | 11 | `IsValidEmail` is never called by any code in the project. | Remove or wire it into validation. |
| StringHelper.cs | 20 | `IsValidUsername` is never called by any code in the project. | Remove or wire it into validation. |
| StringHelper.cs | 29 | `JoinWithSeparator` (the broken O(n²) version) is never called. | Remove; keep only the fixed version. |
| StringHelper.cs | 38 | `JoinWithSeparatorFixed` is never called by any code in the project. | Remove or rename to `JoinWithSeparator` and use it. |
| StringHelper.cs | 43 | `MaskAccountNumber` is never called by any code in the project. | Remove or wire into response serialization. |
| StringHelper.cs | 54 | `ObfuscateAccount` is never called by any code in the project. | Remove or consolidate with `MaskAccountNumber`. |
| StringHelper.cs | 59 | `ToTitleCase` is never called by any code in the project. | Remove. |
| StringHelper.cs | 65 | `IsBlank` is never called by any code in the project. | Remove. |
| AuthService.cs | 91 | `HashPasswordSha1` is never called by any code in the project. | Remove. |
| AuthService.cs | 98 | `ValidateToken` is never called by any code in the project. | Remove. |
| AuthService.cs | 105–107 | Code after `return true;` in `ValidateToken` is unreachable. | Remove the dead lines (or fix the method to actually validate). |
| EmailService.cs | 63 | `SendWelcomeEmail` is never called by any code in the project. | Remove or wire into a registration flow. |
| EmailService.cs | 86 | `SendWelcomeEmailHtml` is never called by any code in the project. | Remove. |
| EmailService.cs | 81 | `BuildHtmlTemplate` is only called by the dead `SendWelcomeEmailHtml`. | Remove along with its caller. |
| TransactionService.cs | 77 | `IsWithinDailyLimit` is never called by any code in the project. | Remove or wire into `Transfer`. |
| TransactionService.cs | 94 | `FormatCurrency` is never called by any code in the project. | Remove. |
| TransactionService.cs | 99 | `RefundTransaction` contains `throw new NotImplementedException()` in production code. | Implement the method or remove the endpoint. |

---

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 65 | Deposit cap `1000000` is an inline literal. | Extract to `const decimal MaxDepositAmount = 1_000_000m`. |
| TransactionService.cs | 68 | Interest rate `0.05m` is an inline literal. | Extract to `const decimal DepositInterestRate = 0.05m`. |
| TransactionService.cs | 68 | The `* 1` multiplier is an unexplained magic number. | Remove it or replace with a named constant. |
| UserService.cs | 22 | User ID upper bound `1000000` is an inline literal. | Extract to a named constant. |
| UserService.cs | 42 | Same `1000000` literal repeated in `UpdateUser`. | Use the shared constant. |
| UserService.cs | 56 | Same `1000000` literal repeated in `DeleteUser`. | Use the shared constant. |
| UserService.cs | 70 | Max page size `50` is an inline literal. | Extract to `const int MaxPageSize = 50`. |
| StringHelper.cs | 13 | Email max length `254` is an inline literal. | Extract to `const int MaxEmailLength = 254`. |
| StringHelper.cs | 22 | Username min length `3` and max length `20` are inline literals. | Extract to named constants. |
| StringHelper.cs | 45 | Account number mask threshold `4` is an inline literal. | Extract to `const int VisibleDigits = 4`. |
| EmailService.cs | 40 | Sender address `"notifications@company.com"` is hardcoded. | Read from configuration. |
| EmailService.cs | 67 | Support address `"support@company.com"` is hardcoded. | Read from configuration. |
| EmailService.cs | 89 | Sender address `"notifications@company.com"` is repeated. | Use the same config-driven constant. |
| AuthService.cs | 53 | Admin username `"admin"` is a hardcoded string literal. | Extract to a constant or configuration. |
| AuthService.cs | 55 | Role `"SuperAdmin"` is a hardcoded string literal. | Extract to a constant or configuration. |
| DatabaseHelper.cs | 16 | Entire connection string with credentials is a hardcoded fallback. | Remove; require configuration. |

---

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 31–34 | `JoinWithSeparator` uses `+=` string concatenation inside a loop (O(n²)). | Replace with `string.Join` (as `JoinWithSeparatorFixed` already does) and remove the broken version. |
| StringHelper.cs | 16 | `IsValidEmail` creates a `new Regex(...)` on every call. | Make the regex a `private static readonly` field. |
| StringHelper.cs | 25 | `IsValidUsername` creates a `new Regex(...)` on every call. | Make the regex a `private static readonly` field. |
| StringHelper.cs | 65–71 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Replace the body with `return string.IsNullOrWhiteSpace(value);`. |
| UserService.cs | 10 | `static List<string> _auditLog` is shared mutable state accessed from multiple threads without synchronization. | Use a `ConcurrentBag<string>` or protect with a lock; better yet, persist to the database. |
| UserService.cs | 11 | `static int _requestCount` is incremented without `Interlocked` or a lock, causing race conditions. | Use `Interlocked.Increment` or remove if not needed. |
| DatabaseHelper.cs | 19–24 | `GetOpenConnection` leaks resource ownership to callers with no documented disposal contract. | Remove the method; encapsulate connection lifecycle within each data method. |
| UserService.cs | 20–23 | `GetUserById` contains the same `id <= 0` / `id > 1000000` validation block. | Extract to a shared `ValidateUserId(int id)` private method. |
| UserService.cs | 40–43 | `UpdateUser` repeats the same `id <= 0` / `id > 1000000` validation block. | Call the shared `ValidateUserId` method. |
| UserService.cs | 54–57 | `DeleteUser` repeats the same `id <= 0` / `id > 1000000` validation block. | Call the shared `ValidateUserId` method. |
| UserService.cs | 87–92 | `GetAuditReport` uses `+=` string concatenation in a loop. | Use `StringBuilder` or `string.Join("\n", _auditLog)`. |
| TransactionService.cs | 23–61 | `Transfer` carries at least five distinct responsibilities: input validation, fetching both users, balance/fee calculation, executing two updates, recording the transaction, and sending email. | Split into `ValidateTransfer`, `ExecuteTransfer` (transactional), `RecordTransaction`, and `NotifyTransfer` private helpers. |
| TransactionService.cs | 63–75 | `Deposit` mixes validation, interest calculation, balance update, and transaction recording. | Split into `ValidateDeposit`, `CalculateInterest`, and `ExecuteDeposit`. |

---

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, exposing full stack traces in production. | Wrap in `if (app.Environment.IsDevelopment())`. |
| Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry enforcement. | Set to `true`. |
| Program.cs | 36 | `UseHttpsRedirection()` is commented out. | Uncomment the call. |
| Program.cs | 38 | CORS allows `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`. | Restrict to specific origins, methods, and headers. |
| appsettings.json | 18–20 | Log level is set to `Debug` for `Default`, `Microsoft`, and `System` namespaces. | Set to `Information` or `Warning` for production. |
| appsettings.json | 3 | Production database connection string with `sa` credentials is committed to source. | Remove from VCS; use environment variables or a secrets manager. |
| appsettings.json | 6 | JWT secret `"mysecretkey"` is committed and trivially guessable. | Use a strong random key from a secrets manager. |
| appsettings.json | 14 | SMTP password is committed to source. | Move to environment variable or secrets manager. |
| SampleBankingApp.csproj | 14 | `System.Data.SqlClient` 4.8.6 is the legacy, unsupported package. | Migrate to `Microsoft.Data.SqlClient` (latest stable). |
| SampleBankingApp.csproj | 15 | `Newtonsoft.Json` 12.0.3 is outdated and has known CVEs. | Upgrade to 13.0.x or remove if System.Text.Json suffices. |
| SampleBankingApp.csproj | 8–9 | `DebugSymbols` and `DebugType` are set unconditionally, shipping debug symbols in release builds. | Move inside `<PropertyGroup Condition="'$(Configuration)'=='Debug'">`. |
| (missing) | — | No `appsettings.Production.json` exists to override debug settings for production. | Create one with `Information` log level and no secrets. |

---

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|------|------|-------|-----|
| (project) | — | No test project exists in the repository. | Create a `SampleBankingApp.Tests` xUnit/NUnit project. |
| TransactionService.cs | 23 | `Transfer` has no tests for boundary conditions: balance exactly equal to `amount`, balance equal to `amount + fee - 0.01`, zero amount, negative amount, self-transfer. | Write tests covering each boundary and the self-transfer guard. |
| TransactionService.cs | 63 | `Deposit` has no tests for boundary conditions: `amount = 0`, `amount = 1`, `amount = 1_000_000`, `amount = 1_000_001`. | Write parameterized tests for the valid/invalid range. |
| UserService.cs | 68 | `GetUsersPage` has no tests for pagination: page 1 (skip 0), page 2 (skip pageSize), page beyond data, `pageSize > 50` clamping. | Write tests verifying correct OFFSET for each page number. |
| AuthService.cs | 28 | `Login` has no tests for: valid credentials, wrong password, SQL injection payload in username, admin bypass path, inactive user. | Write tests including an injection attempt (`' OR 1=1 --`). |
| AuthService.cs | 68 | `GenerateJwtToken` has no tests verifying token structure, correct claims, and expiry date. | Write a test that decodes the token and asserts claims and `exp`. |
| StringHelper.cs | 11 | `IsValidEmail` has no tests for boundary cases: empty string, 254-char valid email, 255-char string, missing `@`, multiple `@`. | Write parameterized tests. |
| StringHelper.cs | 20 | `IsValidUsername` has no tests for boundary cases: 2-char, 3-char, 20-char, 21-char, special characters. | Write parameterized tests. |
| StringHelper.cs | 43 | `MaskAccountNumber` has no tests for: 4-char input (returned as-is), 5-char input, very long input. | Write tests for each length boundary. |
| TransactionService.cs | 23 | `Transfer` has no test verifying that the fee is correctly deducted from the sender and the full amount is credited to the receiver. | Write a test asserting exact balance deltas. |
| TransactionService.cs | 63 | `Deposit` has no test verifying the interest bonus calculation. | Write a test asserting `newBalance = oldBalance + amount + amount * rate`. |