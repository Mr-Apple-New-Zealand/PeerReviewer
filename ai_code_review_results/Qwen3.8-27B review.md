# Code Review Report

**Branch:** `main` | **Commit:** `67ece22980b87505c9e6a0bc95962632ab91b998`

---

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 32 | `Login` builds SQL via string interpolation with `username` and `hashedPassword`, enabling SQL injection. | Use parameterized query: `WHERE Username = @Username AND Password = @Hash`. |
| DatabaseHelper.cs | 29 | `ExecuteQuery` interpolates `tableName` and `whereClause` directly into SQL, allowing injection of arbitrary statements. | Validate `tableName` against a whitelist and require callers to use `ExecuteQuerySafe` with parameters. |
| TransactionService.cs | 47 | `Transfer` interpolates `newFromBalance` and `fromUserId` into an UPDATE statement. | Use `ExecuteQuerySafe` with `@Balance` and `@Id` parameters. |
| TransactionService.cs | 48 | `Transfer` interpolates `newToBalance` and `toUserId` into a second UPDATE statement. | Use `ExecuteQuerySafe` with parameters. |
| TransactionService.cs | 71 | `Deposit` interpolates `amount + interestBonus` and `userId` into an UPDATE statement. | Use `ExecuteQuerySafe` with `@Amount` and `@Id` parameters. |
| TransactionService.cs | 89–90 | `RecordTransaction` interpolates `fromId`, `toId`, `amount`, `type`, and `description` into an INSERT. | Use `ExecuteQuerySafe` with named parameters for every value. |
| UserService.cs | 47 | `UpdateUser` interpolates `email`, `username`, and `id` into an UPDATE statement. | Use `ExecuteQuerySafe` with `@Email`, `@Username`, `@Id` parameters. |
| UserService.cs | 61 | `DeleteUser` interpolates `id` into a DELETE statement. | Use `ExecuteQuerySafe` with `@Id` parameter. |
| UserService.cs | 99 | `SearchUsers` interpolates `query` into a `LIKE '%...%'` clause, enabling SQL injection. | Use `ExecuteQuerySafe` with `WHERE Username LIKE @Pattern` and pass `"%" + query + "%"`. |
| DatabaseHelper.cs | 16 | Fallback connection string hardcodes `sa` / `Admin1234!` credentials in source. | Remove the fallback; fail fast if the config key is missing. |
| appsettings.json | 3 | Production database credentials (`sa` / `Admin1234!`) are committed to source control. | Use a secrets manager or environment variable; remove from VCS. |
| appsettings.json | 6 | JWT signing key `"mysecretkey"` is trivially guessable and committed to source. | Generate a ≥ 256-bit random key and store in a secrets manager. |
| appsettings.json | 14 | SMTP password `"EmailPass99"` is committed to source control. | Move to a secrets manager or environment variable. |
| AuthService.cs | 61–66 | `HashPasswordMd5` uses MD5, which is cryptographically broken and unsalted. | Use PBKDF2, bcrypt, or Argon2 with a per-user salt. |
| AuthService.cs | 91–96 | `HashPasswordSha1` uses SHA-1, which is deprecated and unsalted. | Remove the method; use a modern KDF. |
| AuthService.cs | 17, 53–56 | Hardcoded admin backdoor: password `"SuperAdmin2024"` grants `SuperAdmin` role bypassing the DB. | Remove the bypass entirely; enforce all auth through the database. |
| Program.cs | 24 | `ValidateLifetime = false` means issued JWTs never expire. | Set `ValidateLifetime = true` and enforce a reasonable `ClockSkew`. |
| Program.cs | 38 | CORS policy allows any origin, any method, and any header simultaneously. | Restrict to specific origins, methods, and headers required by the client. |
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, exposing stack traces in production. | Gate behind `if (app.Environment.IsDevelopment())`. |
| Program.cs | 36 | `UseHttpsRedirection()` is commented out, allowing plaintext HTTP. | Uncomment and ensure a valid TLS certificate is configured. |
| AuthController.cs | 19–31 | No rate limiting or account lockout on the login endpoint. | Add ASP.NET Core rate-limiting middleware and a lockout counter. |
| UserController.cs | 39 | `UpdateUser` has no ownership or role check; any authenticated user can modify any user. | Add `[Authorize(Roles="Admin")]` or verify `id == User.Identity.Name`. |
| UserController.cs | 57 | `DeleteUser` has no ownership or role check; any authenticated user can delete any user. | Add `[Authorize(Roles="Admin")]` or verify ownership. |
| UserController.cs | 22 | `GetUser` has no ownership check; any authenticated user can read any user's data. | Restrict to self or add `[Authorize(Roles="Admin")]`. |
| EmailService.cs | 29 | `EnableSsl = false` sends SMTP credentials and email bodies in plaintext. | Set `EnableSsl = true` and use port 587 with STARTTLS. |
| Models/User.cs | 7 | `Password` property on the `User` model can be serialized to JSON responses. | Add `[JsonIgnore]` or remove the property from the model returned to clients. |

---

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserService.cs | 72 | `GetUsersPage` computes `skip = page * pageSize`, so page 1 skips the first `pageSize` rows (off-by-one). | Change to `skip = (page - 1) * pageSize`. |
| UserService.cs | 68 | `GetUsersPage` does not validate that `page >= 1`; a negative page produces a negative `skip` and a SQL error. | Add `if (page < 1) page = 1;` or return a 400. |
| UserService.cs | 68 | `GetUsersPage` does not validate that `pageSize >= 1`; zero or negative values cause a SQL error. | Add `if (pageSize < 1) pageSize = 1;`. |
| TransactionService.cs | 42 | `Transfer` checks `fromBalance >= amount` but then deducts `amount + fee`, so a user with exactly `amount` in their account ends up with a negative balance. | Change the guard to `fromBalance >= totalDebit`. |
| TransactionService.cs | 25 | `Transfer` rejects `amount < 0` but allows `amount == 0`, permitting a zero-value transfer that still records a transaction row. | Change to `amount <= 0`. |
| TransactionService.cs | 23 | `Transfer` has no check for `fromUserId == toUserId`, allowing a user to "transfer" to themselves and lose the fee. | Add `if (fromUserId == toUserId) return (false, "Cannot transfer to yourself");`. |
| TransactionService.cs | 68 | `Deposit` computes `amount * 0.05m * 1`; the trailing `* 1` is a no-op that suggests a missing multiplier (e.g., a tier factor). | Remove the `* 1` or replace with the intended variable. |
| TransactionService.cs | 65 | `Deposit` uses a hardcoded cap of `1000000` with no named constant, making the business rule invisible. | Extract to `private const decimal MaxDepositAmount = 1_000_000m;`. |
| TransactionService.cs | 23 | `Transfer` does not validate that `toUserId > 0`; a zero or negative target ID will silently match no row or corrupt data. | Add `if (toUserId <= 0) return (false, "Invalid recipient");`. |

---

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 47–50 | Two separate `ExecuteNonQuery` calls update balances without a transaction; if the second fails, the first is already committed. | Wrap both updates and `RecordTransaction` in a single `SqlTransaction`. |
| TransactionService.cs | 52–55 | `SendTransferNotification` is called after the DB writes have committed; if it throws, the transfer is persisted but the caller receives a 500. | Send email in a `try/catch` after the commit, or use an outbox pattern. |
| AuthService.cs | 34–51 | `Login` opens a connection, command, and reader with no `try/finally` or `using`; any exception leaks all three resources. | Wrap in `using` blocks or a `try/finally` that disposes all three. |
| UserService.cs | 97–108 | `SearchUsers` catches a broad `Exception` and returns an empty `List<User>`, making it impossible for the caller to distinguish "no matches" from a database error. | Log the exception and rethrow, or return a typed result with an error flag. |
| UserController.cs | 52 | `UpdateUser` returns `ex.Message` directly to the HTTP client, potentially leaking internal details (table names, constraint names). | Return a generic message and log the full exception server-side. |
| EmailService.cs | 75–78 | `SendWelcomeEmail` catches a broad `Exception` and only writes to `Console`, silently swallowing the failure. | Log via `ILogger` and consider a retry or dead-letter queue. |
| AuthController.cs | 19–31 | No rate limiting or account lockout on the login endpoint, enabling brute-force attacks. | Add `Microsoft.AspNetCore.RateLimiting` and a per-username failure counter. |
| TransactionService.cs | 47–50 | No transaction wraps the balance updates and the `RecordTransaction` INSERT; a crash between them leaves inconsistent state. | Use a single `SqlTransaction` for all three writes. |
| TransactionController.cs | 51–59 | `Refund` catches only `NotImplementedException`; any other exception (DB error, null ref) propagates as an unhandled 500 with stack trace. | Add a general `catch (Exception)` that logs and returns a safe 500. |

---

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 34–51 | `SqlConnection`, `SqlCommand`, and `SqlDataReader` in `Login` are never closed or disposed on any code path. | Wrap each in a `using` statement. |
| DatabaseHelper.cs | 19–24 | `GetOpenConnection` returns an open `SqlConnection` with no documented ownership contract; callers may forget to dispose. | Remove the method or document that the caller must dispose; prefer `using` at every call site. |
| DatabaseHelper.cs | 26–34 | `ExecuteQuery` calls `GetOpenConnection()` but never closes the connection; `SqlCommand` and `SqlDataAdapter` are also not disposed. | Use `using` for connection, command, and adapter. |
| DatabaseHelper.cs | 50–57 | `ExecuteNonQuery` calls `GetOpenConnection()`; if `ExecuteNonQuery` throws, `connection.Close()` is skipped and the `SqlCommand` is never disposed. | Use `using` for both connection and command. |
| DatabaseHelper.cs | 36–48 | `ExecuteQuerySafe` does not dispose the `SqlDataAdapter`. | Add `using` around the adapter. |
| DatabaseHelper.cs | 68–78 | `ExecuteQueryWithParams` does not dispose the `SqlDataAdapter`. | Add `using` around the adapter. |
| EmailService.cs | 16 | `SmtpClient` is stored as an instance field; it is not thread-safe and its underlying socket is never released. | Create a new `SmtpClient` per send (or use a thread-safe pool) and dispose after use. |
| EmailService.cs | 39 | `MailMessage` in `SendTransferNotification` is never disposed. | Wrap in `using` (MailMessage implements IDisposable in .NET 8). |
| EmailService.cs | 69 | `MailMessage` in `SendWelcomeEmail` is never disposed. | Wrap in `using`. |
| EmailService.cs | 89 | `MailMessage` in `SendWelcomeEmailHtml` is never disposed. | Wrap in `using`. |

---

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 28 | `jwtSecret!` uses the null-forgiving operator; if the config key is absent, `Encoding.UTF8.GetBytes(null)` throws `ArgumentNullException`. | Check for null and throw a descriptive `InvalidOperationException` at startup. |
| AuthService.cs | 34 | `_config.GetConnectionString("DefaultConnection")` can return null, which is passed to the `SqlConnection` constructor. | Null-check and throw a clear configuration error. |
| AuthService.cs | 70 | `_config["Jwt:SecretKey"]!` can be null at runtime if the key is missing. | Null-check before use. |
| AuthService.cs | 81 | `_config["Jwt:Issuer"]` can be null, producing a JWT with a null issuer. | Null-check and fail fast. |
| AuthService.cs | 82 | `_config["Jwt:Audience"]` can be null, producing a JWT with a null audience. | Null-check and fail fast. |
| TransactionService.cs | 36 | `fromUserTable.Rows[0]` is accessed without checking `Rows.Count > 0`; a non-existent user causes `IndexOutOfRangeException`. | Guard with `if (fromUserTable.Rows.Count == 0) return (false, "Sender not found");`. |
| TransactionService.cs | 37 | `toUserTable.Rows[0]` is accessed without checking `Rows.Count > 0`. | Guard with a row-count check. |
| TransactionService.cs | 53 | `fromUserTable.Rows[0]["Email"]` is cast to `string` without a null check; a NULL email column causes a `NullReferenceException` in `SendTransferNotification`. | Check `row["Email"] != DBNull.Value` before use. |
| TransactionService.cs | 55 | `toUserTable.Rows[0]["Username"]` is cast to `string` without a null check. | Check for `DBNull.Value`. |
| TransactionController.cs | 27 | `int.Parse(userIdClaim!)` will throw `NullReferenceException` if the claim is absent (e.g., malformed token). | Null-check `userIdClaim` and return 401. |
| TransactionController.cs | 41 | `int.Parse(userIdClaim!)` in `Deposit` has the same unguarded null risk. | Null-check and return 401. |
| EmailService.cs | 24 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` throws `FormatException` if the value is non-numeric. | Use `int.TryParse` with a fallback. |
| EmailService.cs | 65 | `username.ToUpper()` in `SendWelcomeEmail` throws `NullReferenceException` if `username` is null. | Add a null guard or use `username?.ToUpper() ?? ""`. |
| StringHelper.cs | 13 | `IsValidEmail` accesses `email.Length` before any null check; a null argument throws. | Add `if (email is null) return false;` at the top. |
| StringHelper.cs | 22 | `IsValidUsername` accesses `username.Length` before any null check. | Add a null guard. |
| StringHelper.cs | 45 | `MaskAccountNumber` accesses `accountNumber.Length` without a null check. | Add a null guard. |
| StringHelper.cs | 56 | `ObfuscateAccount` uses `account[^4..]` which throws `ArgumentOutOfRangeException` if `account` is null or shorter than 4 characters. | Add null and length guards. |
| UserController.cs | 72 | `SearchUsers` accepts `[FromQuery] string query` with no `[Required]`; a missing query parameter passes null to `UserService.SearchUsers`. | Add `[Required]` or null-check in the controller. |
| AuthController.cs | 22 | `request` in `Login` is a model-bound body; if the client sends no body, `request` is null and `request.Username` throws. | Add a null check or use `[FromBody, Required]`. |

---

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 59–65 | `TableExists(string)` is defined but never called anywhere in the codebase. | Remove the method. |
| DatabaseHelper.cs | 67–78 | `ExecuteQueryWithParams(string, SqlParameter[])` is marked `[Obsolete]` and has no callers. | Remove the method. |
| StringHelper.cs | 11–18 | `IsValidEmail(string)` is defined but never called. | Remove the method. |
| StringHelper.cs | 20–27 | `IsValidUsername(string)` is defined but never called. | Remove the method. |
| StringHelper.cs | 29–36 | `JoinWithSeparator(IEnumerable<string>, string)` is defined but never called; it is also the broken O(n²) duplicate. | Remove the method. |
| StringHelper.cs | 38–41 | `JoinWithSeparatorFixed(IEnumerable<string>, string)` is defined but never called. | Remove the method. |
| StringHelper.cs | 43–52 | `MaskAccountNumber(string)` is defined but never called. | Remove the method. |
| StringHelper.cs | 54–57 | `ObfuscateAccount(string)` is defined but never called; it duplicates `MaskAccountNumber`. | Remove the method. |
| StringHelper.cs | 59–63 | `ToTitleCase(string)` is defined but never called. | Remove the method. |
| StringHelper.cs | 65–71 | `IsBlank(string?)` is defined but never called. | Remove the method. |
| AuthService.cs | 91–96 | `HashPasswordSha1(string)` is defined but never called. | Remove the method. |
| AuthService.cs | 98–108 | `ValidateToken(string)` is defined but never called. | Remove the method. |
| AuthService.cs | 105–107 | Code after the unconditional `return true;` on line 103 is unreachable. | Remove the dead lines. |
| EmailService.cs | 63–79 | `SendWelcomeEmail(string, string)` is defined but never called. | Remove the method. |
| EmailService.cs | 86–92 | `SendWelcomeEmailHtml(string, string)` is defined but never called. | Remove the method. |
| EmailService.cs | 81–84 | `BuildHtmlTemplate(string, string)` is only called by the dead `SendWelcomeEmailHtml`. | Remove the method. |
| TransactionService.cs | 77–85 | `IsWithinDailyLimit(int)` is defined but never called; the daily limit is never enforced. | Either call it in `Transfer` or remove it. |
| TransactionService.cs | 94–97 | `FormatCurrency(decimal)` is defined but never called. | Remove the method. |
| TransactionService.cs | 99–103 | `RefundTransaction(int)` contains only `throw new NotImplementedException()`; it is a non-stub placeholder in production code. | Implement the refund logic or remove the endpoint. |
| StringHelper.cs | 29–41 | `JoinWithSeparator` (broken) and `JoinWithSeparatorFixed` (correct) are duplicate implementations; neither is called. | Remove both; use `string.Join` inline where needed. |
| StringHelper.cs | 43–57 | `MaskAccountNumber` and `ObfuscateAccount` are duplicate implementations of the same masking logic; neither is called. | Remove both. |

---

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 65 | `1000000` is an inline literal for the maximum deposit amount. | Extract to `private const decimal MaxDepositAmount = 1_000_000m;`. |
| TransactionService.cs | 68 | `0.05m` is an inline literal for the deposit interest rate. | Extract to `private const decimal DepositInterestRate = 0.05m;`. |
| TransactionService.cs | 68 | `* 1` is an unexplained inline multiplier with no named constant. | Remove or replace with a named constant explaining the factor. |
| UserService.cs | 22 | `1000000` is an inline literal for the maximum valid user ID. | Extract to a named constant or configuration value. |
| UserService.cs | 42 | `1000000` is repeated in `UpdateUser` as the max user ID. | Reuse the same named constant. |
| UserService.cs | 56 | `1000000` is repeated in `DeleteUser` as the max user ID. | Reuse the same named constant. |
| UserService.cs | 70 | `50` is an inline literal for the maximum page size. | Extract to `private const int MaxPageSize = 50;`. |
| AuthService.cs | 84 | `30` is an inline literal for JWT expiry in days. | Extract to a named constant or read from configuration. |
| AuthService.cs | 17 | `"SuperAdmin2024"` is a hardcoded password string. | Remove entirely (see security section). |
| AuthService.cs | 53 | `"admin"` is a hardcoded username literal. | Remove with the backdoor. |
| AuthService.cs | 55 | `"SuperAdmin"` is a hardcoded role string. | Remove with the backdoor. |
| EmailService.cs | 40 | `"notifications@company.com"` is hardcoded as the sender address. | Read from configuration (`Email:FromAddress`). |
| EmailService.cs | 69 | `"notifications@company.com"` is hardcoded again in `SendWelcomeEmail`. | Use the same configuration value. |
| EmailService.cs | 89 | `"notifications@company.com"` is hardcoded a third time in `SendWelcomeEmailHtml`. | Use the same configuration value. |
| EmailService.cs | 67 | `"support@company.com"` is a hardcoded email address in the welcome body. | Read from configuration. |
| StringHelper.cs | 13 | `254` is an inline literal for the maximum email length (RFC 5321). | Extract to `private const int MaxEmailLength = 254;`. |
| StringHelper.cs | 22 | `3` and `20` are inline literals for username min/max length. | Extract to named constants. |
| StringHelper.cs | 45, 49–50 | `4` is an inline literal for the number of visible trailing characters in masking. | Extract to `private const int VisibleTailLength = 4;`. |
| DatabaseHelper.cs | 16 | The entire fallback connection string is a hardcoded literal in source. | Remove the fallback; require the config key. |

---

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 31–35 | `JoinWithSeparator` uses `result += item + separator` inside a loop, producing O(n²) string allocation. | Replace with `string.Join(separator, items)` (or remove the method entirely). |
| StringHelper.cs | 16 | `IsValidEmail` creates a `new Regex(...)` on every call. | Make the pattern a `private static readonly Regex`. |
| StringHelper.cs | 25 | `IsValidUsername` creates a `new Regex(...)` on every call. | Make the pattern a `private static readonly Regex`. |
| UserService.cs | 10 | `static List<string> _auditLog` is shared mutable state accessed from multiple threads without synchronization. | Use a `ConcurrentQueue<string>` or protect with a lock; or persist to the database. |
| UserService.cs | 11 | `static int _requestCount` is incremented with `++` from multiple threads without atomicity. | Use `Interlocked.Increment` or remove the counter. |
| UserService.cs | 87–92 | `GetAuditReport` builds a string with `report += entry + "\n"` in a loop (O(n²)). | Use `string.Join("\n", _auditLog)` or a `StringBuilder`. |
| StringHelper.cs | 65–71 | `IsBlank` reimplements `string.IsNullOrWhiteSpace` with three manual checks. | Replace the body with `return string.IsNullOrWhiteSpace(value);`. |
| StringHelper.cs | 29–41 | `JoinWithSeparator` (broken) and `JoinWithSeparatorFixed` (correct) are duplicate implementations of the same function. | Remove both; call `string.Join` directly. |
| StringHelper.cs | 43–57 | `MaskAccountNumber` and `ObfuscateAccount` are duplicate implementations of account masking. | Remove both or keep one. |
| UserService.cs | 20–23, 40–43, 54–57 | The validation block `if (id <= 0) throw …; if (id > 1000000) throw …;` is duplicated in `GetUserById`, `UpdateUser`, and `DeleteUser`. | Extract to a private `ValidateUserId(int id)` helper. |
| AuthService.cs | 28–59 | `Login` carries four distinct responsibilities: password hashing, DB query, user mapping, and admin-bypass check. | Split into `HashPassword`, `FetchUser`, `MapUser`, and remove the bypass. |
| TransactionService.cs | 23–61 | `Transfer` carries five distinct responsibilities: input validation, balance retrieval, fee calculation, dual balance update, and email notification. | Split into `ValidateTransfer`, `ComputeFee`, `ExecuteBalanceUpdate`, and `NotifyRecipient`. |
| DatabaseHelper.cs | 19–24 | `GetOpenConnection` returns an open connection with no documented ownership contract, leaking disposal responsibility to callers. | Remove the method or document `[CallerMustDispose]`; prefer internal `using` in each public method. |
| EmailService.cs | 16 | `SmtpClient` is a shared instance field; `SmtpClient` is not thread-safe and concurrent `Send` calls will corrupt state. | Create a new `SmtpClient` per call or use a thread-safe wrapper. |

---

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, exposing full stack traces in production. | Wrap in `if (app.Environment.IsDevelopment())`. |
| Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry validation. | Set to `true`. |
| Program.cs | 36 | `UseHttpsRedirection()` is commented out. | Uncomment and configure a valid TLS certificate. |
| Program.cs | 38 | CORS allows `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`, an overly permissive policy. | Restrict to specific origins, methods, and headers. |
| appsettings.json | 18–20 | Log level is set to `Debug` for `Default`, `Microsoft`, and `System` namespaces. | Set to `Information` or `Warning` for production. |
| SampleBankingApp.csproj | 14 | `System.Data.SqlClient` 4.8.6 is the legacy, unsupported package. | Migrate to `Microsoft.Data.SqlClient` ≥ 5.0. |
| SampleBankingApp.csproj | 15 | `Newtonsoft.Json` 12.0.3 has known CVEs (e.g., CVE-2019-13059). | Upgrade to ≥ 13.0.3 or remove if unused. |
| SampleBankingApp.csproj | 16 | `System.IdentityModel.Tokens.Jwt` 7.0.0 is outdated. | Upgrade to ≥ 7.6.0. |
| SampleBankingApp.csproj | 8–9 | `DebugSymbols=true` and `DebugType=full` are set unconditionally in the main `<PropertyGroup>`, shipping debug symbols in release builds. | Move into a `<PropertyGroup Condition="'$(Configuration)'=='Debug'">` block. |
| (project root) | — | No `appsettings.Production.json` exists to override the debug-level logging and development connection string. | Add an `appsettings.Production.json` with `Information` log level and a placeholder connection string. |
| appsettings.json | 3 | The default (non-environment-specific) connection string points to `prod-db.internal` with real credentials. | Use a local/dev connection string in `appsettings.json` and the production one in `appsettings.Production.json` or a secrets manager. |
| appsettings.json | 6 | JWT `SecretKey` is `"mysecretkey"`, a trivially guessable value. | Generate a cryptographically random ≥ 256-bit key. |

---

## 10. Missing Unit Tests

No test project exists in the repository. The following methods and scenarios are the highest priority for unit and integration tests:

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 23–61 | `Transfer` has no tests for: balance exactly equal to amount (fee causes negative balance), self-transfer, zero/negative amount, non-existent sender/recipient, fee rounding. | Create a test class covering all boundary conditions with a mocked `DatabaseHelper`. |
| TransactionService.cs | 63–75 | `Deposit` has no tests for: amount = 0, amount = 1, amount = 1 000 000, amount = 1 000 001, interest bonus calculation. | Add boundary-value tests for the deposit cap and interest formula. |
| UserService.cs | 68–83 | `GetUsersPage` has no tests for: page = 1 (should return first page, not skip), page = 0, page = -1, pageSize = 0, pageSize = 51 (clamped to 50). | Add pagination tests verifying the correct `OFFSET` value. |
| AuthService.cs | 28–59 | `Login` has no tests for: valid credentials, wrong password, inactive user, SQL injection payload in username, admin bypass. | Add tests with a mocked DB; verify the admin bypass is removed. |
| AuthService.cs | 68–89 | `GenerateJwtToken` has no tests for: correct claims, correct issuer/audience, expiry date, null config values. | Add tests verifying token structure and that null config throws. |
| StringHelper.cs | 11–18 | `IsValidEmail` has no tests for: null input, empty string, 254-char email, 255-char email, missing TLD, multiple @ signs. | Add boundary and edge-case tests. |
| StringHelper.cs | 20–27 | `IsValidUsername` has no tests for: null, 2-char, 3-char, 20-char, 21-char, special characters. | Add boundary tests. |
| StringHelper.cs | 43–52 | `MaskAccountNumber` has no tests for: null, 4-char, 5-char, 10-char inputs. | Add tests for short and long account numbers. |
| EmailService.cs | 34–61 | `SendTransferNotification` has no tests for: successful send, retry on `SmtpException`, all 3 retries exhausted. | Mock `SmtpClient` and verify retry count and final throw. |
| TransactionService.cs | 77–85 | `IsWithinDailyLimit` has no tests for: 0 transactions, exactly 10 transactions, 11 transactions. | Add boundary tests at the `MaxTransactionsPerDay` threshold. |
| UserController.cs | 39–54 | `UpdateUser` has no tests for: unauthorized user updating another user, invalid email, SQL injection in email/username fields. | Add authorization and injection tests. |
| AuthController.cs | 19–31 | `Login` endpoint has no tests for: missing body, empty username/password, rate-limiting behavior. | Add integration tests for the login flow. |