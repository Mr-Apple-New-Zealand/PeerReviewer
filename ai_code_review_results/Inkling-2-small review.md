# Code Review Report — SampleBankingApp (branch `main`, commit afe34f08dc676290cc331e30ca6b1793da6a02a2)

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection in `Login`: username and password hash are interpolated directly into the query string. | Use parameterized queries (`SqlParameter`) or `ExecuteQuerySafe`. |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded backdoor credential `AdminBypassPassword = "SuperAdmin2024"` committed to source. | Remove the backdoor entirely; authenticate only against the database. |
| SampleBankingApp/Services/AuthService.cs | 53-56 | Admin bypass grants a `SuperAdmin` identity (Id=0) without any database verification when username is "admin". | Delete the bypass branch; enforce role checks via claims from a real user record. |
| SampleBankingApp/Services/AuthService.cs | 30, 61-66 | Passwords hashed with unsalted MD5 (`HashPasswordMd5`), trivially reversible via rainbow tables. | Use a salted, adaptive algorithm such as PBKDF2, bcrypt, or Argon2 (e.g., `PasswordHasher<T>`). |
| SampleBankingApp/Services/AuthService.cs | 91-96 | `HashPasswordSha1` uses unsalted SHA1, also cryptographically broken. | Remove the method; use a modern password hasher. |
| SampleBankingApp/Services/AuthService.cs | 84 | JWT lifetime set to 30 days, far too long for a banking token. | Use short-lived access tokens (e.g., 15–60 minutes) with refresh tokens. |
| SampleBankingApp/Services/AuthService.cs | 98-108 | `ValidateToken` unconditionally returns `true`, so any token string is accepted as valid. | Implement real validation with `TokenValidationParameters` or delete the method. |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry validation entirely. | Set `ValidateLifetime = true`. |
| SampleBankingApp/Program.cs | 28 | `Encoding.UTF8.GetBytes(jwtSecret!)` uses a null-forgiving operator on a possibly-missing config value and a weak secret. | Fail fast with a clear error if the secret is missing and require a strong (≥256-bit) secret from a vault/env var. |
| SampleBankingApp/appsettings.json | 6 | Weak, hardcoded JWT secret `"mysecretkey"` committed to source control. | Generate a strong random secret and store it in user-secrets/environment variables, never in the repo. |
| SampleBankingApp/appsettings.json | 3 | Production connection string with `sa` password `Admin1234!` committed to source control. | Move secrets to environment variables or a secret store; rotate the exposed password immediately. |
| SampleBankingApp/appsettings.json | 14 | SMTP password `EmailPass99` committed to source control. | Move to environment variables/secret store and rotate. |
| SampleBankingApp/appsettings.json | 3 | `TrustServerCertificate=True` disables TLS certificate validation for the database connection. | Remove it and install a valid certificate, or use `Encrypt=True` with proper trust. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded fallback connection string containing `sa` password `Admin1234!` if config is missing. | Fail fast when the connection string is missing; never embed credentials in code. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | `ExecuteQuery` builds `SELECT * FROM {tableName} WHERE {whereClause}` from raw fragments — SQL injection by design. | Remove the method or require parameterized input only. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | `SELECT *` returns all columns including password hashes to callers. | Select only the columns needed. |
| SampleBankingApp/Services/UserService.cs | 47 | `UpdateUser` interpolates `email` and `username` directly into the UPDATE statement — SQL injection. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 61 | `DeleteUser` interpolates `id` into DELETE (int-typed, but still unparameterized and inconsistent). | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 47 | `UPDATE Users SET Balance = {newFromBalance} ...` uses interpolated SQL instead of parameters. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 48 | Same interpolated-SQL problem for the recipient balance update. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 71 | `Deposit` interpolates the computed amount into the UPDATE statement. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 89-90 | `RecordTransaction` interpolates user-controlled `description` (and `type`) into INSERT — SQL injection. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 99 | `SearchUsers` builds `LIKE '%{query}%'` from raw input — SQL injection and wildcard injection. | Parameterize and escape `%`/`_` in the pattern. |
| SampleBankingApp/Program.cs | 38 | CORS policy allows any origin, any method, any header (`AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`). | Restrict to known origins, methods, and headers. |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, leaking stack traces and internals in production. | Gate it behind `app.Environment.IsDevelopment()` and use `UseExceptionHandler` otherwise. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out, so traffic may flow over plain HTTP. | Re-enable `app.UseHttpsRedirection()` and add HSTS. |
| SampleBankingApp/Controllers/UserController.cs | 22-29 | `GetUser` lets any authenticated user read any other user's profile/balance (IDOR) — no ownership or role check. | Enforce ownership (`id == callerId`) or an admin role. |
| SampleBankingApp/Controllers/UserController.cs | 31-36 | `GetUsers` exposes the full user list to any authenticated user with no admin check. | Require an admin role for listing all users. |
| SampleBankingApp/Controllers/UserController.cs | 38-54 | `UpdateUser` has no ownership or admin check — any user can change any account's email/username. | Enforce ownership or admin role before updating. |
| SampleBankingApp/Controllers/UserController.cs | 56-69 | `DeleteUser` has no ownership or admin check — any authenticated user can delete any account. | Require admin role (or ownership) for deletion. |
| SampleBankingApp/Controllers/UserController.cs | 78-83 | `GetAuditLog` exposes the internal audit log to any authenticated user. | Restrict to an admin role. |
| SampleBankingApp/Controllers/TransactionController.cs | 48-60 | `Refund` has no role check — any authenticated user could trigger refunds once implemented. | Require an admin/finance role. |
| SampleBankingApp/Controllers/AuthController.cs | 19-31 | Login endpoint has no rate limiting or account lockout — brute-force and credential-stuffing are unimpeded. | Add rate limiting (e.g., `AddRateLimiter`) and lockout/backoff after failed attempts. |
| SampleBankingApp/Services/EmailService.cs | 29 | `EnableSsl = false` sends SMTP credentials and mail in cleartext. | Set `EnableSsl = true` and use port 587/465. |
| SampleBankingApp/Controllers/UserController.cs | 48, 52 | Raw `ex.Message` returned to HTTP clients in `UpdateUser`, leaking internals. | Return a generic message and log the exception server-side. |
| SampleBankingApp/Controllers/TransactionController.cs | 27, 41 | `int.Parse(userIdClaim!)` throws on missing/malformed claim, producing 500s and potential log noise. | Validate the claim and return 401/400 if missing or unparsable. |
| SampleBankingApp/appsettings.json | 17-21 | `Debug` log level for `Default`, `Microsoft`, and `System` in the committed (production) config. | Use `Information`/`Warning` in production and environment-specific overrides. |
| SampleBankingApp/appsettings.json | 23 | `AllowedHosts: "*"` accepts any Host header (host-header attacks). | Restrict to known hostnames. |
| SampleBankingApp/SampleBankingApp.csproj | 8-9 | `DebugSymbols=true` and `DebugType=full` ship full debug symbols in release builds. | Set `DebugType=none`/`pdbonly` and `DebugSymbols=false` for Release. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | Newtonsoft.Json 12.0.3 has known vulnerabilities (fixed in 13.0.1+). | Upgrade to 13.0.3 or later. |
| SampleBankingApp/SampleBankingApp.csproj | 13 | Microsoft.AspNetCore.Authentication.JwtBearer 8.0.0 is an unpatched initial release with known advisories. | Upgrade to the latest 8.0.x patch. |
| SampleBankingApp/SampleBankingApp.csproj | 16 | System.IdentityModel.Tokens.Jwt 7.0.0 is an initial release with known vulnerabilities. | Upgrade to the latest 7.x/8.x patch. |
| SampleBankingApp/SampleBankingApp.csproj | 14 | System.Data.SqlClient 4.8.6 should be reviewed against current advisories; prefer Microsoft.Data.SqlClient. | Migrate to Microsoft.Data.SqlClient (latest). |
| SampleBankingApp/Services/AuthService.cs | 32 | `SELECT *` in the login query pulls the full row including the password hash into memory unnecessarily. | Select only the needed columns. |
| SampleBankingApp/Services/EmailService.cs | 56 | `Console.WriteLine` of exception details instead of structured logging can leak sensitive data to stdout. | Use `ILogger` with appropriate levels. |
| SampleBankingApp/Services/AuthService.cs | 55 | Admin bypass returns `Id = 0`, a sentinel that could collide with real data or bypass ownership checks downstream. | Remove the bypass; never fabricate identities. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 25 | `if (amount < 0)` allows zero-amount transfers; message says "must be positive". | Use `amount <= 0`. |
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check `fromBalance >= amount` ignores the fee, so `amount + fee` can drive the balance negative. | Check `fromBalance >= totalDebit`. |
| SampleBankingApp/Services/TransactionService.cs | 23-61 | No self-transfer check — a user can transfer to themselves, burning the fee for nothing. | Reject `fromUserId == toUserId`. |
| SampleBankingApp/Services/TransactionService.cs | 36-37 | `Rows[0]` accessed without checking `Rows.Count` — crashes with `IndexOutOfRangeException` when either user does not exist. | Check `Rows.Count == 0` and return a failure result. |
| SampleBankingApp/Services/TransactionService.cs | 68 | `amount * 0.05m * 1` applies a 5% deposit bonus (likely wrong rate, e.g., should be 1%) and contains a redundant `* 1`. | Use the intended rate constant and drop the `* 1`. |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit cap of 1,000,000 is a magic boundary with no named constant or config. | Extract to a named constant or configuration value. |
| SampleBankingApp/Services/UserService.cs | 72 | `int skip = page * pageSize` is off by one page — page 1 skips the first `pageSize` rows; should be `(page - 1) * pageSize`. | Use `(page - 1) * pageSize`. |
| SampleBankingApp/Services/UserService.cs | 68-83 | No validation that `page >= 1` or `pageSize >= 1`; zero/negative values produce invalid OFFSET/FETCH and SQL errors. | Clamp or reject `page < 1` and `pageSize < 1`. |
| SampleBankingApp/Services/UserService.cs | 70 | `pageSize` is capped at 50 but never floored — `pageSize = 0` or negative reaches SQL. | Enforce a minimum page size of 1. |
| SampleBankingApp/Services/UserService.cs | 72 | `page * pageSize` can overflow `int` for very large page values. | Use `long` arithmetic or validate upper bounds. |
| SampleBankingApp/Services/AuthService.cs | 103 | `ValidateToken` returns `true` unconditionally, making every token "valid". | Implement real validation or remove the method. |
| SampleBankingApp/Services/TransactionService.cs | 77-85 | `IsWithinDailyLimit` is never called, so the 10-transactions/day limit is never enforced. | Call it in `Transfer` (and `Deposit` if applicable) or remove it. |
| SampleBankingApp/Services/TransactionService.cs | 63-75 | `Deposit` never verifies the user exists; the UPDATE affects 0 rows yet returns success. | Check rows affected or verify the user first. |
| SampleBankingApp/Services/TransactionService.cs | 47-48 | Two separate UPDATE statements with no transaction — a failure between them loses or duplicates money. | Wrap debit/credit/insert in a single DB transaction. |
| SampleBankingApp/Services/TransactionService.cs | 50 | `RecordTransaction` runs after the balance updates with no transaction — a failure leaves balances changed with no audit row. | Include the insert in the same transaction. |
| SampleBankingApp/Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` appends the separator after the last item, producing a trailing separator. | Use `string.Join` or trim the trailing separator. |
| SampleBankingApp/Helpers/StringHelper.cs | 54-57 | `ObfuscateAccount` uses `account[^4..]` with no length check — strings shorter than 4 chars throw `ArgumentOutOfRangeException`. | Guard `account.Length < 4` like `MaskAccountNumber` does. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `IsValidEmail` dereferences `email.Length` with no null check. | Add `string.IsNullOrWhiteSpace` guard. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `IsValidUsername` dereferences `username.Length` with no null check. | Add a null/empty guard. |
| SampleBankingApp/Services/EmailService.cs | 65 | `username.ToUpper()` throws `NullReferenceException` when `username` is null. | Guard against null/empty username. |
| SampleBankingApp/Controllers/TransactionController.cs | 27, 41 | `int.Parse(userIdClaim!)` throws on missing or non-numeric claim instead of returning 401/400. | Use `int.TryParse` and handle failure. |
| SampleBankingApp/Services/TransactionService.cs | 73 | `RecordTransaction(0, userId, ...)` uses `0` as a sentinel `FromUserId` for deposits, polluting the audit trail. | Use a nullable `FromUserId` or a dedicated system account constant. |
| SampleBankingApp/Services/AuthService.cs | 55 | Admin bypass fabricates `Id = 0`, which can collide with real rows or bypass ownership checks. | Remove the bypass. |
| SampleBankingApp/Services/TransactionService.cs | 36 | `(decimal)fromUserTable.Rows[0]["Balance"]` throws `InvalidCastException` if the column is `DBNull`. | Use `Convert.ToDecimal` with a null check. |
| SampleBankingApp/Services/UserService.cs | 22, 42, 56 | Arbitrary upper bound `id > 1000000` rejects legitimate IDs and is duplicated in three methods. | Remove the arbitrary cap or make it a named, justified constant. |
| SampleBankingApp/Services/AuthService.cs | 84 | 30-day token expiry is effectively "never expires" for a banking app. | Use short-lived tokens with refresh. |
| SampleBankingApp/Services/TransactionService.cs | 39 | Fee is rounded to 2 decimals but never validated against the sender's balance together with the amount (see line 42). | Validate `fromBalance >= amount + fee`. |
| SampleBankingApp/Services/UserService.cs | 68-83 | `GetUsersPage` returns page 0 results identical to page 1 when `page = 0` (skip = 0), masking invalid input. | Reject `page < 1`. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/UserService.cs | 105-108 | `SearchUsers` catches broad `Exception` and returns an empty list — callers cannot distinguish "no results" from "database down". | Let the exception propagate or return a result type that carries the error. |
| SampleBankingApp/Services/TransactionService.cs | 47-50 | No database transaction around debit, credit, and audit insert — partial failure corrupts balances. | Wrap in `SqlTransaction` (or use EF Core with a transaction). |
| SampleBankingApp/Services/TransactionService.cs | 52-55 | Email is sent after the DB writes commit; if SMTP fails, the exception propagates and the client sees an error even though the transfer succeeded. | Send email after commit inside a try/catch that logs but does not fail the request, or use an outbox. |
| SampleBankingApp/Services/TransactionService.cs | 63-75 | `Deposit` performs an UPDATE and an INSERT with no transaction — a crash between them loses the audit record. | Wrap both in a transaction. |
| SampleBankingApp/Services/EmailService.cs | 75-79 | `SendWelcomeEmail` catches broad `Exception` and only writes to console — failures are silently swallowed. | Log via `ILogger` and decide whether to rethrow or record the failure. |
| SampleBankingApp/Services/EmailService.cs | 46-60 | Retry loop has no delay/backoff between attempts and reuses the same `MailMessage`; final failure rethrows without context. | Add backoff, dispose the message, and wrap the final exception with context. |
| SampleBankingApp/Controllers/UserController.cs | 50-53 | `catch (Exception ex)` returns `StatusCode(500, ex.Message)` — raw exception text leaks to clients. | Return a generic message; log the exception server-side. |
| SampleBankingApp/Controllers/UserController.cs | 46-49 | `BadRequest(ex.Message)` returns the raw exception message to the client. | Return a sanitized, user-safe message. |
| SampleBankingApp/Controllers/UserController.cs | 64-68 | `catch (Exception)` returns 500 with a generic message (acceptable) but performs no specific handling or retry semantics. | Keep generic message but add structured logging and consider specific exception types. |
| SampleBankingApp/Controllers/TransactionController.cs | 56-59 | `catch (NotImplementedException)` used as control flow to return 500 for an unimplemented feature. | Return `501 Not Implemented` or implement the feature; don't catch `NotImplementedException`. |
| SampleBankingApp/Services/AuthService.cs | 34-38 | No try/catch around connection open/query — any DB failure becomes an unhandled 500 (with developer exception page enabled). | Catch, log, and return a controlled error response. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` closes the connection only on the success path; an exception leaks the connection. | Use `using` for the connection and command. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26-34 | `ExecuteQuery` has no exception handling and leaks connection/command on any failure. | Use `using` blocks and let exceptions propagate with proper disposal. |
| SampleBankingApp/Controllers/AuthController.cs | 19-31 | No rate limiting or lockout on the login endpoint — unlimited password guessing. | Add rate limiting and account lockout/backoff. |
| SampleBankingApp/Services/UserService.cs | 18-36 | `GetUserById` throws `ArgumentException` for bad IDs but `UserController.GetUser` never catches it — unhandled 500. | Catch in the controller or return a result type. |
| SampleBankingApp/Services/TransactionService.cs | 36-37 | `Rows[0]` on an empty table throws `IndexOutOfRangeException`, unhandled anywhere. | Check `Rows.Count` and return a failure result. |
| SampleBankingApp/Services/EmailService.cs | 86-92 | `SendWelcomeEmailHtml` has no try/catch — any SMTP failure propagates to the caller. | Add error handling consistent with the other send methods. |
| SampleBankingApp/Services/UserService.cs | 38-50 | `UpdateUser` returns `true` even when 0 rows were affected (user not found) — silent failure. | Check rows affected and return false/throw when 0. |
| SampleBankingApp/Services/UserService.cs | 52-66 | `DeleteUser` returns `true` even when 0 rows were affected. | Check rows affected and report not-found. |
| SampleBankingApp/Program.cs | 32-44 | No global exception handler (`UseExceptionHandler`) for production — unhandled exceptions surface as developer pages or empty 500s. | Add `app.UseExceptionHandler(...)` for non-development environments. |
| SampleBankingApp/Controllers/UserController.cs | 31-36 | `GetUsers` passes unvalidated `page`/`pageSize` to SQL — invalid values produce 500s. | Validate and clamp inputs; return 400 on invalid values. |
| SampleBankingApp/Services/AuthService.cs | 98-108 | `ValidateToken` contains unreachable code after `return true;` and never validates anything. | Remove the dead code and implement real validation. |
| SampleBankingApp/Services/EmailService.cs | 46-60 | Retry loop logs via `Console.WriteLine` instead of `ILogger`, losing structured context. | Inject `ILogger<EmailService>` and log properly. |
| SampleBankingApp/Services/TransactionService.cs | 99-103 | `RefundTransaction` throws `NotImplementedException` from production code reached by a live endpoint. | Implement the refund or return 501 and hide the endpoint. |
| SampleBankingApp/Services/UserService.cs | 95-109 | `SearchUsers` swallows all exceptions including SQL syntax errors from injection attempts, hiding attacks. | Log the exception and return an error result. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 34-38 | `SqlConnection` created in `Login` is never closed or disposed. | Wrap in `using`. |
| SampleBankingApp/Services/AuthService.cs | 37 | `SqlCommand` is never disposed. | Wrap in `using`. |
| SampleBankingApp/Services/AuthService.cs | 38 | `SqlDataReader` is never closed or disposed — the connection cannot return to the pool. | Wrap in `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection` returns an open connection with no documented ownership contract; callers routinely leak it. | Document that callers must dispose, or return a `using`-scoped abstraction. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28-33 | `ExecuteQuery` never closes/disposes the connection, command, or adapter. | Use `using` for all three. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` closes the connection only on success; exceptions leak it; the command is never disposed. | Use `using` for connection and command. |
| SampleBankingApp/Data/DatabaseHelper.cs | 44 | `ExecuteQuerySafe` does not dispose the `SqlDataAdapter`. | Wrap the adapter in `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 74 | `ExecuteQueryWithParams` does not dispose the `SqlDataAdapter`. | Wrap the adapter in `using`. |
| SampleBankingApp/Services/EmailService.cs | 16 | `_smtpClient` is an instance field; `EmailService` is not `IDisposable`, so the SMTP socket is never released; `SmtpClient` is also not thread-safe. | Implement `IDisposable` and dispose the client, or create/dispose per send. |
| SampleBankingApp/Services/EmailService.cs | 39-43 | `MailMessage` in `SendTransferNotification` is never disposed. | Wrap in `using`. |
| SampleBankingApp/Services/EmailService.cs | 69 | `MailMessage` in `SendWelcomeEmail` is never disposed. | Wrap in `using`. |
| SampleBankingApp/Services/EmailService.cs | 89 | `MailMessage` in `SendWelcomeEmailHtml` is never disposed. | Wrap in `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52-56 | `connection.Close()` instead of `Dispose()` — the connection is not reliably returned to the pool on all paths. | Use `using var connection = ...`. |
| SampleBankingApp/Services/UserService.cs | 99 | `SearchUsers` calls `ExecuteQuery`, inheriting its connection/command leak. | Fix `ExecuteQuery` or migrate callers to `ExecuteQuerySafe`. |
| SampleBankingApp/Services/AuthService.cs | 34-38 | If `connection.Open()` or `ExecuteReader()` throws, the connection (and any partially opened resources) are never released. | Use `using` blocks so disposal happens on all paths. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | `SqlCommand` created in `ExecuteQuery` is never disposed. | Wrap in `using`. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 28 | `Encoding.UTF8.GetBytes(jwtSecret!)` throws `ArgumentNullException` at startup if `Jwt:SecretKey` is missing. | Validate configuration at startup and fail with a clear message. |
| SampleBankingApp/Services/AuthService.cs | 70 | `_config["Jwt:SecretKey"]!` is null-forgiving; missing key → `GetBytes(null)` throws. | Check for null and throw a descriptive configuration exception. |
| SampleBankingApp/Services/AuthService.cs | 81-82 | `_config["Jwt:Issuer"]` / `_config["Jwt:Audience"]` may be null; token validation then fails or behaves unexpectedly. | Validate these settings at startup. |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | `int.Parse(userIdClaim!)` throws `ArgumentNullException` when the `NameIdentifier` claim is absent. | Use `int.TryParse` and return 401/400 on failure. |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | Same unguarded `int.Parse(userIdClaim!)` in `Deposit`. | Use `int.TryParse` and return 401/400 on failure. |
| SampleBankingApp/Services/TransactionService.cs | 36 | `fromUserTable.Rows[0]` throws `IndexOutOfRangeException` when the sender does not exist. | Check `Rows.Count` first. |
| SampleBankingApp/Services/TransactionService.cs | 37 | `toUserTable.Rows[0]` throws `IndexOutOfRangeException` when the recipient does not exist. | Check `Rows.Count` first. |
| SampleBankingApp/Services/TransactionService.cs | 53-55 | `(string)fromUserTable.Rows[0]["Email"]` throws `InvalidCastException` on `DBNull`. | Use `Convert.ToString` with null handling. |
| SampleBankingApp/Services/UserService.cs | 111-123 | `MapRowToUser` casts `row["Username"]`, `row["Email"]`, etc. directly — `DBNull` values throw `InvalidCastException`. | Use `Convert.ToString`/`row.IsNull(...)` checks. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `email.Length` throws `NullReferenceException` when `email` is null. | Add `string.IsNullOrWhiteSpace(email)` guard. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `username.Length` throws `NullReferenceException` when `username` is null. | Add a null guard. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `accountNumber.Length` throws `NullReferenceException` when null. | Add a null guard. |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | `account[^4..]` throws `NullReferenceException` on null and `ArgumentOutOfRangeException` on strings shorter than 4 chars. | Guard null and length. |
| SampleBankingApp/Services/EmailService.cs | 65 | `username.ToUpper()` throws `NullReferenceException` when `username` is null. | Guard against null/empty. |
| SampleBankingApp/Services/EmailService.cs | 22 | `_config["Email:SmtpHost"]` may be null; `new SmtpClient(null)` throws `ArgumentNullException`. | Validate SMTP settings at startup. |
| SampleBankingApp/Services/EmailService.cs | 24 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` throws `FormatException` on non-numeric config. | Use `int.TryParse` with a fallback and a clear error. |
| SampleBankingApp/Services/AuthService.cs | 44-49 | `(int)reader["Id"]`, `(string)reader["Username"]`, etc. throw on `DBNull` or type mismatch. | Use `reader.IsDBNull(...)` checks or `Convert`. |
| SampleBankingApp/Controllers/UserController.cs | 72 | `query` is not marked required; a missing query string arrives as null and flows into the SQL builder. | Mark `[FromQuery] string query` as required or validate for null/whitespace. |
| SampleBankingApp/Services/EmailService.cs | 34 | `toEmail` and `recipientName` are not null-checked; `MailMessage` throws `ArgumentNullException` on null `to`. | Validate arguments at method entry. |
| SampleBankingApp/Services/TransactionService.cs | 23 | `description` is nullable and flows into `RecordTransaction`'s interpolated SQL (becomes empty string, but the pattern is unsafe). | Parameterize and handle null explicitly. |
| SampleBankingApp/Services/UserService.cs | 79 | `foreach (System.Data.DataRow row in table.Rows)` is safe, but `MapRowToUser(row)` inside it can throw on `DBNull` (see above). | Harden `MapRowToUser`. |
| SampleBankingApp/Services/TransactionService.cs | 83 | `(int)table.Rows[0]["TxCount"]` assumes the COUNT column is non-null and exactly `int`; provider-dependent typing can throw. | Use `Convert.ToInt32`. |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 59-65 | `TableExists` is defined but never called anywhere. | Delete it or use it. |
| SampleBankingApp/Data/DatabaseHelper.cs | 67-78 | `ExecuteQueryWithParams` is marked `[Obsolete]` and has no callers. | Delete the obsolete method. |
| SampleBankingApp/Helpers/StringHelper.cs | 11-18 | `IsValidEmail` is never called. | Delete it or wire it into validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 20-27 | `IsValidUsername` is never called. | Delete it or wire it into validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` is never called (and is buggy). | Delete it; use `string.Join`. |
| SampleBankingApp/Helpers/StringHelper.cs | 38-41 | `JoinWithSeparatorFixed` is never called and merely reimplements `string.Join`. | Delete it; call `string.Join` directly. |
| SampleBankingApp/Helpers/StringHelper.cs | 43-52 | `MaskAccountNumber` is never called. | Delete it or use it for display masking. |
| SampleBankingApp/Helpers/StringHelper.cs | 54-57 | `ObfuscateAccount` is never called (and crashes on short input). | Delete it or fix and use it. |
| SampleBankingApp/Helpers/StringHelper.cs | 59-63 | `ToTitleCase` is never called. | Delete it. |
| SampleBankingApp/Helpers/StringHelper.cs | 65-71 | `IsBlank` is never called and reimplements `string.IsNullOrWhiteSpace`. | Delete it; use the BCL method. |
| SampleBankingApp/Services/AuthService.cs | 91-96 | `HashPasswordSha1` is never called. | Delete it. |
| SampleBankingApp/Services/AuthService.cs | 98-108 | `ValidateToken` is never called. | Delete it or implement real validation and use it. |
| SampleBankingApp/Services/AuthService.cs | 105-107 | Unreachable code after `return true;` in `ValidateToken`. | Remove the unreachable statements. |
| SampleBankingApp/Services/EmailService.cs | 63-79 | `SendWelcomeEmail` is never called. | Delete it or wire it into registration. |
| SampleBankingApp/Services/EmailService.cs | 81-84 | `BuildHtmlTemplate` is called only by the dead `SendWelcomeEmailHtml`, so it is effectively dead too. | Delete both or wire them in. |
| SampleBankingApp/Services/EmailService.cs | 86-92 | `SendWelcomeEmailHtml` is never called. | Delete it or wire it into registration. |
| SampleBankingApp/Services/TransactionService.cs | 77-85 | `IsWithinDailyLimit` is never called — the daily transaction limit is never enforced. | Call it in `Transfer`/`Deposit` or delete it. |
| SampleBankingApp/Services/TransactionService.cs | 94-97 | `FormatCurrency` is never called. | Delete it. |
| SampleBankingApp/Services/TransactionService.cs | 99-103 | `RefundTransaction` throws `NotImplementedException` in non-stub production code reached by a live endpoint. | Implement it or remove the endpoint. |
| SampleBankingApp/Services/UserService.cs | 11 | `_requestCount` is incremented (lines 25, 59) but never read anywhere. | Remove the field and its increments. |
| SampleBankingApp/Helpers/StringHelper.cs | 29-41 | Duplicate implementations: broken `JoinWithSeparator` vs `JoinWithSeparatorFixed` — both unused. | Keep neither; use `string.Join`. |
| SampleBankingApp/Helpers/StringHelper.cs | 43-57 | Duplicate implementations: `MaskAccountNumber` vs `ObfuscateAccount` — both unused. | Keep one correct implementation or delete both. |
| SampleBankingApp/Services/AuthService.cs | 61-66, 91-96 | Duplicate weak-hash helpers `HashPasswordMd5` (used) and `HashPasswordSha1` (unused). | Delete both; use a modern hasher. |
| SampleBankingApp/Services/EmailService.cs | 63-92 | Duplicate welcome-email implementations (`SendWelcomeEmail`, `SendWelcomeEmailHtml`) — both unused. | Keep one or delete both. |
| SampleBankingApp/Data/DatabaseHelper.cs | 67 | `[Obsolete]` attribute present on `ExecuteQueryWithParams`, which is still compiled into the assembly. | Remove the obsolete method entirely. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 68 | `0.05m` deposit bonus rate is an inline magic number (and likely the wrong rate). | Extract to a named constant or configuration value. |
| SampleBankingApp/Services/TransactionService.cs | 65 | `1000000` deposit cap is an inline magic number. | Extract to a named constant or configuration value. |
| SampleBankingApp/Services/TransactionService.cs | 11 | `TransactionFeeRate = 0.015m` is a named constant but belongs in configuration, not code. | Move to `appsettings.json`. |
| SampleBankingApp/Services/TransactionService.cs | 12 | `MaxTransactionsPerDay = 10` is a named constant but belongs in configuration. | Move to `appsettings.json`. |
| SampleBankingApp/Services/UserService.cs | 70 | `50` page-size cap is an inline magic number. | Extract to a named constant or configuration value. |
| SampleBankingApp/Services/UserService.cs | 22, 42, 56 | `1000000` max user ID is repeated inline in three methods. | Extract to a single named constant. |
| SampleBankingApp/Services/UserService.cs | 20, 40, 54 | `0` lower bound for user ID is repeated inline in three methods. | Extract to a named constant or share a validation helper. |
| SampleBankingApp/Services/AuthService.cs | 84 | `AddDays(30)` — 30-day token lifetime is an inline magic number. | Extract to a named constant or configuration value. |
| SampleBankingApp/Services/AuthService.cs | 17 | `"SuperAdmin2024"` hardcoded credential. | Remove entirely (see Security). |
| SampleBankingApp/Services/AuthService.cs | 55 | `Id = 0` sentinel for the fabricated admin user. | Remove the bypass. |
| SampleBankingApp/Services/TransactionService.cs | 73 | `0` sentinel `FromUserId` for deposits. | Use a named constant or nullable column. |
| SampleBankingApp/Services/EmailService.cs | 40, 69, 89 | `"notifications@company.com"` sender address repeated three times. | Extract to a constant or configuration value. |
| SampleBankingApp/Services/EmailService.cs | 67 | `"support@company.com"` hardcoded support address in the email body. | Move to configuration. |
| SampleBankingApp/Services/EmailService.cs | 24 | `"25"` default SMTP port inline. | Extract to a named constant or require config. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `254` max email length inline. | Extract to a named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `3` and `20` username length limits inline. | Extract to named constants. |
| SampleBankingApp/Helpers/StringHelper.cs | 16, 25 | Regex patterns inline in methods (also a performance issue). | Extract to `static readonly` fields. |
| SampleBankingApp/Helpers/StringHelper.cs | 49, 56 | `4` (visible trailing digits) repeated in `MaskAccountNumber` and `ObfuscateAccount`. | Extract to a named constant. |
| SampleBankingApp/Controllers/UserController.cs | 32 | `page = 1, pageSize = 20` defaults inline in the action signature. | Extract to named constants or configuration. |
| SampleBankingApp/Services/TransactionService.cs | 89-90 | `'Completed'`, `'Transfer'`, `'Deposit'` magic status/type strings in SQL. | Extract to constants or an enum mapped to strings. |
| SampleBankingApp/Services/AuthService.cs | 32 | `IsActive = 1` magic boolean-as-int in SQL. | Use a named constant or parameter. |
| SampleBankingApp/Services/UserService.cs | 75 | Table name `"Users"` and column names (`Id`, `Balance`, …) repeated across files as string literals. | Centralize schema names or use an ORM. |
| SampleBankingApp/Services/EmailService.cs | 36 | `"${amount:F2}"` currency format inline (duplicated in `TransactionService.FormatCurrency`). | Extract to a shared constant/helper. |
| SampleBankingApp/Services/TransactionService.cs | 96 | `"${amount:F2}"` duplicated currency format. | Extract to a shared constant/helper. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Fallback connection string with credentials hardcoded in source. | Remove the fallback; require configuration. |
| SampleBankingApp/Helpers/StringHelper.cs | 49 | `'*'` mask character inline. | Extract to a named constant. |
| SampleBankingApp/Services/EmailService.cs | 13-14 | `MaxRetries = 3` and `SmtpTimeoutMs = 5000` are named constants but belong in configuration. | Move to `appsettings.json`. |
| SampleBankingApp/Services/TransactionService.cs | 11 | `TransactionFeeRate` named constant but not configurable per environment. | Move to configuration. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 31-35 | String concatenation inside a loop in `JoinWithSeparator` — O(n²) allocations. | Use `StringBuilder` or `string.Join`. |
| SampleBankingApp/Services/UserService.cs | 87-92 | String concatenation inside a loop in `GetAuditReport` — O(n²). | Use `StringBuilder` or `string.Join("\n", _auditLog)`. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | `new Regex(...)` created on every call to `IsValidEmail`. | Use `static readonly Regex` with `RegexOptions.Compiled`. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | `new Regex(...)` created on every call to `IsValidUsername`. | Use `static readonly Regex` with `RegexOptions.Compiled`. |
| SampleBankingApp/Services/UserService.cs | 10 | `static List<string> _auditLog` is shared mutable state with no synchronization — race conditions and unbounded memory growth. | Use a thread-safe collection with a cap, or persist audit entries to the database. |
| SampleBankingApp/Services/UserService.cs | 11 | `static int _requestCount` is shared mutable state incremented without synchronization and never read. | Remove it or use `Interlocked` and actually consume it. |
| SampleBankingApp/Helpers/StringHelper.cs | 65-71 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Delete and use the BCL method. |
| SampleBankingApp/Helpers/StringHelper.cs | 38-41 | `JoinWithSeparatorFixed` reimplements `string.Join`. | Delete and use `string.Join`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection` leaks resource ownership to callers with no documented contract — callers don't know they must dispose. | Document the contract or return a disposable wrapper/`using` scope. |
| SampleBankingApp/Services/UserService.cs | 20-23, 40-43, 54-57 | Identical id-validation block (`id <= 0` / `id > 1000000`) duplicated in `GetUserById`, `UpdateUser`, and `DeleteUser`. | Extract a shared `ValidateUserId(int id)` helper. |
| SampleBankingApp/Controllers/TransactionController.cs | 26-27, 40-41 | Identical claim-extraction and `int.Parse` block duplicated in `Transfer` and `Deposit`. | Extract a shared `GetCurrentUserId()` helper. |
| SampleBankingApp/Services/EmailService.cs | 40, 69, 89 | Sender address `"notifications@company.com"` duplicated three times. | Extract to a constant or configuration value. |
| SampleBankingApp/Services/EmailService.cs | 36 | Currency format `"${amount:F2}"` duplicated with `TransactionService.FormatCurrency`. | Extract a shared formatting helper. |
| SampleBankingApp/Services/UserService.cs | 111-123 | Row→User mapping duplicated inline in `AuthService.Login` (lines 42-50) instead of reusing `MapRowToUser`. | Share a single mapping method. |
| SampleBankingApp/Services/TransactionService.cs | 23-61 | `Transfer` carries five responsibilities: input validation, balance check, fee calculation, two DB updates, audit insert, and email notification — split into named helpers (`ValidateTransfer`, `DebitAccount`, `CreditAccount`, `RecordAndNotify`). | Extract private helpers per responsibility. |
| SampleBankingApp/Services/AuthService.cs | 28-59 | `Login` mixes hashing, SQL access, row mapping, and a backdoor branch — split into `VerifyCredentials`, `MapUser`, and remove the bypass. | Extract helpers and remove the bypass. |
| SampleBankingApp/Services/EmailService.cs | 34-61 | `SendTransferNotification` builds the body, creates the message, and implements retry — split into `BuildTransferBody`, `SendWithRetry`. | Extract helpers. |
| SampleBankingApp/Services/UserService.cs | 68-83 | `GetUsersPage` mixes validation, querying, and mapping — extract `ValidatePaging` and reuse `MapRowToUser` (already used). | Extract a validation helper. |
| SampleBankingApp/Services/EmailService.cs | 16 | `_smtpClient` instance field is not thread-safe and never disposed (also a resource leak). | Create/dispose per send or implement `IDisposable`. |
| SampleBankingApp/Services/EmailService.cs | 56, 77 | `Console.WriteLine` used instead of `ILogger`. | Inject `ILogger<EmailService>`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 41-42 | `AddWithValue` infers parameter types, causing implicit conversions and potential index scans. | Use explicit `SqlParameter` types and sizes. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Redundant `* 1` in the interest calculation. | Remove it. |
| SampleBankingApp/Services/AuthService.cs | 103-107 | Unreachable code after `return true;` in `ValidateToken`. | Remove the dead statements. |
| SampleBankingApp/Services/UserService.cs | 25, 59 | `_requestCount++` incremented but never read — dead state mutation. | Remove the field and increments. |
| SampleBankingApp/Helpers/StringHelper.cs | 59-63 | `ToTitleCase` uses `CurrentCulture`, producing culture-dependent output. | Use `InvariantCulture` or an explicit culture. |
| SampleBankingApp/Services/TransactionService.cs | 47-48 | Interpolated SQL instead of parameters (also a security issue). | Parameterize. |
| SampleBankingApp/Services/UserService.cs | 47, 61 | Interpolated SQL instead of parameters. | Parameterize. |
| SampleBankingApp/Services/TransactionService.cs | 89-90 | Interpolated SQL instead of parameters. | Parameterize. |
| SampleBankingApp/Services/UserService.cs | 99 | Interpolated LIKE pattern instead of parameters. | Parameterize and escape wildcards. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | Interpolated SQL fragments by design. | Remove or parameterize. |
| SampleBankingApp/Services/EmailService.cs | 46-60 | Retry loop with no delay/backoff between attempts. | Add exponential backoff and jitter. |
| SampleBankingApp/Services/UserService.cs | 10 | `_auditLog` grows unboundedly — memory leak in a long-running process. | Cap the list or persist to the database. |
| SampleBankingApp/Services/UserService.cs | 45 | `_auditLog.Add(...)` without a lock — concurrent adds can corrupt the list. | Use `lock` or a thread-safe collection. |
| SampleBankingApp/Services/TransactionService.cs | 94-97 | `FormatCurrency` duplicates inline formatting used elsewhere and is itself unused. | Delete it or centralize formatting. |
| SampleBankingApp/Services/UserService.cs | 85-93 | `GetAuditReport` builds a report by repeated concatenation and exposes raw internal log lines. | Use `StringBuilder` and sanitize output. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, exposing stack traces in production. | Gate behind `IsDevelopment()`; use `UseExceptionHandler` otherwise. |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry validation. | Set to `true`. |
| SampleBankingApp/Program.cs | 36 | `app.UseHttpsRedirection()` is commented out. | Re-enable it and add `UseHsts()`. |
| SampleBankingApp/Program.cs | 38 | CORS allows any origin, method, and header. | Configure a named policy with explicit origins/methods/headers. |
| SampleBankingApp/appsettings.json | 17-21 | `Debug` log level for `Default`, `Microsoft`, and `System` in the committed config. | Use `Information`/`Warning` for production; override per environment. |
| SampleBankingApp/appsettings.json | — | No `appsettings.Production.json` or environment-specific overrides exist. | Add environment-specific config files and use `ASPNETCORE_ENVIRONMENT`. |
| SampleBankingApp/appsettings.json | 3 | Production connection string with `sa` credentials committed to the repo. | Move to environment variables/secret store; rotate the password. |
| SampleBankingApp/appsettings.json | 6 | Weak JWT secret `"mysecretkey"` committed to the repo. | Use a strong secret from a secret store. |
| SampleBankingApp/appsettings.json | 14 | SMTP password committed to the repo. | Move to a secret store; rotate. |
| SampleBankingApp/appsettings.json | 23 | `AllowedHosts: "*"` permits any Host header. | Restrict to known hostnames. |
| SampleBankingApp/appsettings.json | 3 | `TrustServerCertificate=True` disables TLS validation for the database. | Remove it; use a valid certificate. |
| SampleBankingApp/SampleBankingApp.csproj | 8-9 | `DebugSymbols=true` and `DebugType=full` ship full debug symbols in release builds. | Set `DebugType=none`/`pdbonly` for Release. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | Newtonsoft.Json 12.0.3 has known vulnerabilities. | Upgrade to 13.0.3+. |
| SampleBankingApp/SampleBankingApp.csproj | 13 | JwtBearer 8.0.0 is an unpatched initial release. | Upgrade to the latest 8.0.x patch. |
| SampleBankingApp/SampleBankingApp.csproj | 16 | System.IdentityModel.Tokens.Jwt 7.0.0 is an unpatched initial release. | Upgrade to the latest patch. |
| SampleBankingApp/SampleBankingApp.csproj | 14 | System.Data.SqlClient 4.8.6 is outdated; Microsoft recommends Microsoft.Data.SqlClient. | Migrate to Microsoft.Data.SqlClient (latest). |
| SampleBankingApp/SampleBankingApp.csproj | 7 | `TreatWarningsAsErrors=false` lets warnings (including nullable and obsolete-API warnings) slide. | Set to `true` and fix the warnings. |
| SampleBankingApp/Program.cs | 32-44 | No `UseExceptionHandler` for production — unhandled exceptions surface raw. | Add a production exception handler. |
| SampleBankingApp/Program.cs | 32-44 | No HSTS (`UseHsts`) configured. | Add `app.UseHsts()` in production. |
| SampleBankingApp/Program.cs | 16 | `jwtSecret` read without null check; app starts with a null key and fails later at first token use. | Validate all required config at startup (e.g., with `ValidateOnStart`). |
| SampleBankingApp/Services/EmailService.cs | 29 | `EnableSsl = false` in code — SMTP credentials sent in cleartext. | Enable SSL and use port 587/465. |
| SampleBankingApp/appsettings.json | 12 | `SmtpPort: 25` — plaintext SMTP submission port. | Use 587 (STARTTLS) or 465 (implicit TLS). |
| SampleBankingApp/Program.cs | 38 | CORS policy is inline and not driven by configuration, so it cannot differ per environment. | Define named policies per environment in config. |
| SampleBankingApp/appsettings.json | — | No logging overrides for production namespaces (e.g., `Microsoft.AspNetCore`). | Add environment-specific `Logging` sections. |

## 10. Missing Unit Tests

No test project exists in the solution. The following methods and scenarios are the most critical to cover, prioritized by risk:

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 28-59 | `Login` has no tests: valid login, wrong password, unknown user, inactive user, SQL-injection input, and the admin-bypass path are all unverified. | Add tests for each path, including injection attempts and the bypass (which should be removed). |
| SampleBankingApp/Services/AuthService.cs | 68-89 | `GenerateJwtToken` is untested: claims, issuer/audience, expiry, and signature validation are unverified. | Add tests asserting claims, lifetime, and that the token validates with the configured key. |
| SampleBankingApp/Services/AuthService.cs | 98-108 | `ValidateToken` always returns true — a test would immediately catch this. | Add tests for expired, tampered, and valid tokens. |
| SampleBankingApp/Services/TransactionService.cs | 23-61 | `Transfer` is untested: insufficient funds, fee-vs-balance boundary (`balance == amount` vs `balance == amount + fee`), zero/negative amount, self-transfer, nonexistent sender/recipient, and daily-limit enforcement. | Add boundary and failure-path tests for each scenario. |
| SampleBankingApp/Services/TransactionService.cs | 23-61 | No test verifies atomicity — that a failure mid-transfer does not debit without crediting. | Add a test with a failing second update and assert rollback. |
| SampleBankingApp/Services/TransactionService.cs | 63-75 | `Deposit` is untested: amount = 0, negative, exactly 1,000,000, above 1,000,000, and the 5% bonus calculation. | Add boundary tests for the cap and the bonus math. |
| SampleBankingApp/Services/TransactionService.cs | 99-103 | `RefundTransaction` throws `NotImplementedException` with no test documenting the gap. | Add a test asserting the current behavior or implement and test the refund. |
| SampleBankingApp/Services/UserService.cs | 68-83 | `GetUsersPage` pagination is untested — the off-by-one (`page * pageSize`) would be caught immediately. | Add tests for page 1, page 2, pageSize cap at 50, page 0, and negative inputs. |
| SampleBankingApp/Services/UserService.cs | 18-36 | `GetUserById` boundary tests missing: id = 0, negative, 1,000,000, 1,000,001, and nonexistent id. | Add boundary tests for the validation rules. |
| SampleBankingApp/Services/UserService.cs | 38-50 | `UpdateUser` untested: invalid id, SQL-injection payloads in email/username, and 0-rows-affected behavior. | Add tests for validation, injection, and not-found. |
| SampleBankingApp/Services/UserService.cs | 52-66 | `DeleteUser` untested: invalid id, nonexistent id, and verification the row is actually deleted. | Add tests for validation and deletion. |
| SampleBankingApp/Services/UserService.cs | 95-109 | `SearchUsers` untested: injection payloads, empty result vs. exception (currently indistinguishable), and wildcard handling. | Add tests for injection and error propagation. |
| SampleBankingApp/Helpers/StringHelper.cs | 11-18 | `IsValidEmail` untested: null, empty, missing `@`, missing domain, >254 chars, valid addresses. | Add boundary and null tests. |
| SampleBankingApp/Helpers/StringHelper.cs | 20-27 | `IsValidUsername` untested: null, length 2/3/20/21, invalid characters. | Add boundary tests. |
| SampleBankingApp/Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` untested — a test would catch the trailing-separator bug. | Add tests for empty, single, and multiple items. |
| SampleBankingApp/Helpers/StringHelper.cs | 43-57 | `MaskAccountNumber`/`ObfuscateAccount` untested: null, length < 4, exactly 4, and long inputs. | Add boundary tests. |
| SampleBankingApp/Data/DatabaseHelper.cs | 36-48 | `ExecuteQuerySafe` untested: parameter binding, null values, and type inference via `AddWithValue`. | Add integration tests against a test database. |
| SampleBankingApp/Services/EmailService.cs | 34-61 | `SendTransferNotification` retry logic untested: succeeds first try, succeeds on retry, fails after 3 attempts. | Add tests with a mocked/fake SMTP client. |
| SampleBankingApp/Controllers/AuthController.cs | 19-31 | Login endpoint untested: 401 on bad credentials, 200 with token on success, and behavior under missing claims. | Add controller/integration tests. |
| SampleBankingApp/Controllers/TransactionController.cs | 23-60 | Transfer/Deposit/Refund endpoints untested: missing claim, malformed claim, unauthorized access, and validation failures. | Add controller tests with mocked services. |
| SampleBankingApp/Controllers/UserController.cs | 21-83 | User endpoints untested: IDOR (accessing another user's data), missing ownership checks, and invalid paging parameters. | Add authorization and boundary tests. |
| SampleBankingApp/Services/TransactionService.cs | 77-85 | `IsWithinDailyLimit` untested — and currently never called, so the limit is unenforced. | Add tests and wire the check into `Transfer`. |
| SampleBankingApp/Services/UserService.cs | 85-93 | `GetAuditReport` untested: empty log, multiple entries, and thread-safety of `_auditLog`. | Add tests including concurrent access. |
| SampleBankingApp/Program.cs | 16-30 | No integration test verifies the app starts with valid config and fails fast with missing/invalid JWT settings. | Add a startup/configuration smoke test. |

---

**Summary of the most critical findings:** the application has a hardcoded admin backdoor (`AuthService.cs:17,53-56`), unsalted MD5 password hashing, SQL injection in `Login`, `SearchUsers`, `UpdateUser`, and `RecordTransaction`, a JWT lifetime validation disabled (`ValidateLifetime = false`), a balance check that ignores the transfer fee (allowing negative balances), an off-by-one pagination bug, and no test project at all. These should be addressed before any deployment.