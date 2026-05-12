**## 1. Security Vulnerabilities**

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 12 | Fallback connection string contains hard‑coded SA credentials. | Remove fallback or read from secure store; never commit credentials. |
| appsettings.json | 5 | Plain‑text DB password (`Admin1234!`). | Move secrets to Azure Key Vault / user‑secrets; never store in repo. |
| AuthService.cs | 31 | Uses MD5 for password hashing – insecure and unsalted. | Switch to a strong algorithm (e.g., PBKDF2, BCrypt, Argon2) with a per‑user salt. |
| AuthService.cs | 27 | `AdminBypassPassword` is hard‑coded backdoor. | Remove backdoor; enforce normal authentication. |
| AuthService.cs | 38‑44 | SQL built with string interpolation using `username` → SQL injection. | Use parameterised query (`@username`) via `ExecuteQuerySafe`. |
| AuthService.cs | 61‑66 | `SqlConnection`, `SqlCommand`, `SqlDataReader` not disposed. | Wrap in `using` statements or `await using`. |
| TransactionService.cs | 27‑30 | `ExecuteNonQuery` called with interpolated balances – possible SQL injection if IDs are tampered. | Use parameterised queries. |
| TransactionService.cs | 70‑73 | `ExecuteNonQuery` called with interpolated values for `UPDATE Users …`. | Use parameters. |
| TransactionService.cs | 84‑86 | `ExecuteNonQuery` called with interpolated values for `INSERT INTO Transactions …`. | Use parameters; also sanitise `description`. |
| UserService.cs | 71‑73 | `UPDATE Users SET Email = '{email}', Username = '{username}' …` – SQL injection. | Use parameters. |
| UserService.cs | 84‑86 | `DELETE FROM Users WHERE Id = {id}` – SQL injection. | Use parameters. |
| UserService.cs | 108‑110 | `ExecuteQuery("Users", $"Username LIKE '%{query}%'")` – injection. | Use `ExecuteQuerySafe` with parameters. |
| Program.cs | 27‑31 | `ValidateLifetime = false` disables JWT expiration validation. | Set to `true` and enforce token expiry. |
| Program.cs | 33‑35 | `UseDeveloperExceptionPage()` always enabled – leaks stack traces in prod. | Enable only in Development environment. |
| Program.cs | 38 | HTTPS redirection commented out – traffic may be plain HTTP. | Uncomment `app.UseHttpsRedirection();`. |
| Program.cs | 40‑42 | CORS policy `AllowAnyOrigin/AnyMethod/AnyHeader` – overly permissive. | Restrict origins, methods, and headers as needed. |
| EmailService.cs | 15‑19 | SMTP credentials (`Email:Password`) stored in plain text. | Move to secret store; consider using OAuth2. |
| EmailService.cs | 23 | `EnableSsl = false` – email sent unencrypted. | Set `EnableSsl = true` and use TLS. |
| EmailService.cs | 27‑31 | `SmtpClient` held as a singleton field – not thread‑safe and never disposed. | Create per‑use `SmtpClient` inside `using` or inject a factory. |
| EmailService.cs | 44‑48 | `MailMessage` not disposed after send. | Wrap in `using`. |
| EmailService.cs | 61‑66 | `MailMessage` not disposed in `SendWelcomeEmail`. | Wrap in `using`. |
| EmailService.cs | 78‑82 | `MailMessage` not disposed in `SendWelcomeEmailHtml`. | Wrap in `using`. |
| StringHelper.cs | 12‑14 | `new Regex(...)` created on each call – potential DoS if called repeatedly. | Cache compiled regex as `static readonly`. |
| StringHelper.cs | 24‑28 | `JoinWithSeparator` uses string concatenation in a loop (O(n²)). | Replace with `string.Join` or `StringBuilder`. |
| DatabaseHelper.cs | 22‑26 | `ExecuteQuery` builds SQL from `tableName` and `whereClause` without sanitisation – injection risk. | Remove; use only parameterised methods. |
| DatabaseHelper.cs | 38‑44 | `ExecuteNonQuery` opens connection via `GetOpenConnection()` but never disposes it. | Use `using` or `await using`. |
| DatabaseHelper.cs | 46‑48 | `ExecuteNonQuery` does not use parameters – vulnerable to injection. | Provide overload that accepts parameters. |
| DatabaseHelper.cs | 58‑62 | `ExecuteQuerySafe` creates `SqlDataAdapter` without disposing it. | Wrap in `using`. |
| DatabaseHelper.cs | 70‑73 | `ExecuteQueryWithParams` marked `[Obsolete]` but still present – may be used inadvertently. | Remove or replace with safe method. |
| AuthService.cs | 84‑88 | `ValidateToken` returns early, leaving dead code that attempts to read token. | Remove dead code or implement proper validation. |
| AuthService.cs | 90‑92 | `ValidateToken` does not actually validate token expiry or signature. | Implement full validation using `TokenValidationParameters`. |
| AuthService.cs | 100‑102 | `HashPasswordSha1` present but never used; SHA‑1 is insecure. | Remove or replace with strong hash if needed. |
| AuthService.cs | 108‑110 | `ValidateToken` returns `true` for any non‑empty token. | Fix to perform real validation. |
| AuthService.cs | 115‑117 | `Jwt:SecretKey` in `appsettings.json` is a weak static secret. | Use a strong, randomly generated secret stored securely. |
| AuthService.cs | 119‑121 | `Jwt:Issuer` and `Jwt:Audience` are static strings – may be acceptable but should be configurable per environment. | Move to environment‑specific config. |
| EmailService.cs | 31‑33 | `Timeout = 5000` ms may be too low for slow SMTP servers, causing failures. | Adjust timeout based on environment. |
| TransactionService.cs | 15‑16 | `TransactionFeeRate` and `MaxTransactionsPerDay` are magic numbers; no config. | Move to configuration. |
| UserService.cs | 13‑14 | Static mutable `_auditLog` and `_requestCount` are not thread‑safe. | Use concurrent collections or lock. |
| UserService.cs | 31‑33 | `GetUserById` throws `ArgumentException` for invalid IDs – may expose internal details. | Return null or a proper error result. |
| UserService.cs | 84‑86 | `UpdateUser` does not validate `email` or `username` format. | Validate inputs before DB update. |
| UserService.cs | 108‑110 | `SearchUsers` catches generic `Exception` and returns empty list, hiding errors. | Log exception and return appropriate error response. |
| Program.cs | 45‑47 | Logging level set to `Debug` for all categories in production. | Reduce to `Information` or `Warning` in prod. |
| SampleBankingApp.csproj | 13‑15 | `DebugSymbols` and `DebugType` enabled – may expose PDBs in production. | Disable for Release builds. |
| SampleBankingApp.csproj | 16‑18 | `TreatWarningsAsErrors=false` may allow unchecked warnings. | Consider enabling in CI. |

---

**## 2. Logic Errors**

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 33‑35 | Checks `fromBalance >= amount` but ignores transaction fee, allowing overdraft after fee. | Check `fromBalance >= totalDebit`. |
| TransactionService.cs | 55‑57 | `ExecuteNonQuery` updates balances without a transaction – partial updates possible on failure. | Wrap both updates in a DB transaction. |
| TransactionService.cs | 71‑73 | `RecordTransaction` inserts `description` directly; if `null` it becomes the string `"null"` in DB. | Use `DBNull.Value` when description is null. |
| TransactionService.cs | 84‑86 | `Deposit` adds `interestBonus` unconditionally (5% of amount) – may be unintended business rule. | Clarify requirement; make rate configurable. |
| TransactionService.cs | 86‑87 | `Deposit` adds `amount + interestBonus` in a single statement without transaction – race condition possible. | Use transaction or atomic update. |
| TransactionService.cs | 94‑96 | `IsWithinDailyLimit` is never called, so daily limit is not enforced. | Call method in `Transfer` and `Deposit`. |
| UserService.cs | 57‑59 | Pagination `skip = page * pageSize` should be `(page - 1) * pageSize`; first page skips `pageSize` rows. | Change to `int skip = (page - 1) * pageSize;`. |
| UserService.cs | 57‑58 | No validation that `page` is >= 1; negative pages cause negative skip. | Clamp `page` to minimum 1. |
| UserService.cs | 71‑73 | `UpdateUser` does not verify that the user exists before updating. | Check affected rows and return appropriate result. |
| UserService.cs | 84‑86 | `DeleteUser` does not verify existence; may report success even if no row deleted. | Check rows affected. |
| AuthService.cs | 27‑31 | `Login` returns a `User` without the `Password` field populated; later code may assume it exists. | Ensure password is never exposed; remove from returned object. |
| AuthService.cs | 38‑44 | `Login` opens a connection but never disposes it; also no transaction for login check. | Use `using`. |
| AuthService.cs | 70‑71 | `GenerateJwtToken` sets expiration to 30 days; with `ValidateLifetime = false` token never expires. | Enable lifetime validation. |
| AuthService.cs | 84‑88 | `ValidateToken` returns `true` for any non‑empty token; logic after `return true` is unreachable. | Implement proper validation or remove method. |
| EmailService.cs | 45‑49 | `SendTransferNotification` retries on `SmtpException` but re‑uses same `MailMessage` which may be in an invalid state after failure. | Recreate `MailMessage` each attempt or reset. |
| EmailService.cs | 71‑73 | `SendWelcomeEmail` catches generic `Exception` and only logs to console; caller cannot know failure. | Propagate exception or return status. |
| TransactionController.cs | 15‑17 | `int fromUserId = int.Parse(userIdClaim!);` will throw if claim missing or not an int. | Validate claim existence and parse safely with `int.TryParse`. |
| TransactionController.cs | 27‑29 | Same issue for `userId` in Deposit. | Validate claim. |
| TransactionController.cs | 38‑44 | `Refund` catches only `NotImplementedException`; other errors return 500 without logging. | Catch generic exceptions and log. |
| UserController.cs | 23‑25 | `GetUser` returns `NotFound` but does not log missing user. | Optionally log for audit. |
| UserController.cs | 31‑33 | `GetUsers` does not validate `page`/`pageSize` bounds; could cause huge queries. | Clamp values. |
| UserController.cs | 45‑49 | `UpdateUser` catches `ArgumentException` and returns its message directly – may expose internal details. | Return generic error. |
| UserController.cs | 55‑59 | `DeleteUser` catches generic `Exception` and returns generic message, but logs error – acceptable. | No change needed. |
| UserController.cs | 71‑73 | `SearchUsers` passes raw `query` to `ExecuteQuery` which is vulnerable; also no null/empty check. | Validate query length and use safe method. |

---

**## 3. Error Handling**

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 38‑44 | `SqlConnection`, `SqlCommand`, `SqlDataReader` not wrapped in try/catch; any DB error bubbles up as unhandled exception. | Add proper exception handling and return null or error result. |
| TransactionService.cs | 55‑57 | No transaction; if first `UPDATE` succeeds and second fails, balances become inconsistent. | Use `BEGIN TRANSACTION`/`COMMIT` or `SqlTransaction`. |
| TransactionService.cs | 70‑73 | `RecordTransaction` may throw on DB error; not caught, causing 500. | Wrap in try/catch and log. |
| TransactionService.cs | 84‑86 | `Deposit` may throw on DB error; not caught. | Add error handling. |
| TransactionService.cs | 94‑96 | `IsWithinDailyLimit` not used; daily limit logic missing – not an error but a missing feature. | Call method and handle limit exceeded. |
| UserService.cs | 71‑73 | `UpdateUser` builds SQL with string interpolation; any DB error propagates as unhandled exception. | Catch DB exceptions, log, and return false. |
| UserService.cs | 84‑86 | `DeleteUser` same issue; unhandled DB errors. | Add try/catch. |
| UserService.cs | 108‑110 | `SearchUsers` catches generic `Exception` and returns empty list, hiding failures. | Log exception and return appropriate error response. |
| UserController.cs | 45‑49 | `UpdateUser` catches `ArgumentException` and returns its message directly – may expose internal validation details. | Return generic validation error. |
| UserController.cs | 55‑59 | `DeleteUser` catches generic `Exception` and returns generic message – acceptable but could include logging. | Already logs; fine. |
| TransactionController.cs | 15‑17 | `int.Parse` on claim may throw `FormatException`. No try/catch. | Use `int.TryParse` and return Unauthorized if invalid. |
| TransactionController.cs | 27‑29 | Same for Deposit. | Same fix. |
| TransactionController.cs | 38‑44 | `Refund` catches only `NotImplementedException`; other exceptions bubble up as 500 without logging. | Catch generic `Exception`, log, and return appropriate status. |
| EmailService.cs | 44‑48 | `SendTransferNotification` retries but re‑throws after max attempts, causing unhandled exception in controller. | Return status or handle at higher level. |
| EmailService.cs | 61‑66 | `SendWelcomeEmail` catches generic `Exception` and only writes to console; caller cannot know failure. | Propagate or return bool. |
| Program.cs | 33‑35 | `ValidateLifetime = false` disables token expiry validation – not an error handling issue but a security mis‑config. | Set to true. |
| AuthService.cs | 84‑88 | `ValidateToken` returns early; dead code after return never executed. | Remove dead code. |
| AuthService.cs | 90‑92 | `ValidateToken` does not actually validate token; any non‑empty token is accepted. | Implement proper validation. |
| DatabaseHelper.cs | 38‑44 | `ExecuteNonQuery` does not catch DB errors; caller must handle. | Document contract or add try/catch. |
| DatabaseHelper.cs | 22‑26 | `ExecuteQuery` does not catch errors; may leak connection. | Use try/finally to ensure disposal. |
| DatabaseHelper.cs | 58‑62 | `ExecuteQuerySafe` does not catch errors; may leak adapter. | Add error handling. |
| StringHelper.cs | 24‑28 | `JoinWithSeparator` silently returns empty string on empty collection – may be unexpected. | Document behavior or return empty. |

---

**## 4. Resource Leaks**

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 38‑44 | `SqlConnection`, `SqlCommand`, `SqlDataReader` opened without `using`. | Wrap each in `using`. |
| DatabaseHelper.cs | 22‑26 | `SqlConnection`, `SqlCommand`, `SqlDataAdapter` not disposed. | Use `using` for all. |
| DatabaseHelper.cs | 38‑44 | `SqlConnection` from `GetOpenConnection()` not disposed. | Return `using` or let caller dispose. |
| DatabaseHelper.cs | 58‑62 | `SqlDataAdapter` not disposed. | Wrap in `using`. |
| DatabaseHelper.cs | 38‑44 | `ExecuteNonQuery` opens connection but never disposes it. | Use `using`. |
| EmailService.cs | 44‑48 | `MailMessage` created and sent without disposal. | Wrap in `using`. |
| EmailService.cs | 61‑66 | `MailMessage` in `SendWelcomeEmail` not disposed. | Wrap in `using`. |
| EmailService.cs | 78‑82 | `MailMessage` in `SendWelcomeEmailHtml` not disposed. | Wrap in `using`. |
| EmailService.cs | 23‑31 | `_smtpClient` is a field never disposed; may hold socket indefinitely. | Implement `IDisposable` on `EmailService` and dispose client, or create per‑use. |
| TransactionService.cs | 55‑57 | Two separate `ExecuteNonQuery` calls; each opens a connection that is not disposed. | Ensure `ExecuteNonQuery` disposes its connection (fix in helper). |
| TransactionService.cs | 70‑73 | `RecordTransaction` builds SQL and calls `ExecuteNonQuery` which leaks connection. | Fix in helper. |
| TransactionController.cs | 15‑17 | `int.Parse(userIdClaim!)` may throw; no disposal needed but claim parsing may cause exception before any resource use. | Use safe parsing. |
| UserService.cs | 71‑73 | `ExecuteQuerySafe` returns `DataTable`; underlying connection is disposed, but `DataTable` holds data – acceptable. | No leak. |
| Program.cs | 33‑35 | `Jwt:SecretKey` read via `_config["Jwt:SecretKey"]!` – if null, `Encoding.UTF8.GetBytes` will throw; not a leak. | Validate config. |

---

**## 5. Null Reference Risks**

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthController.cs | 15‑16 | `request` could be null if body missing; accessing `request.Username` would NRE. | Add `[FromBody]` null check and return BadRequest. |
| TransactionController.cs | 15‑17 | `User.FindFirst(...)?` may return null; `userIdClaim!` forces non‑null, causing NRE on `int.Parse`. | Validate claim existence and format. |
| TransactionController.cs | 27‑29 | Same issue for Deposit. | Same fix. |
| TransactionService.cs | 70‑73 | `description` may be null; interpolated into SQL as `'null'`. | Pass `DBNull.Value` or handle null. |
| EmailService.cs | 23‑31 | `_config["Email:SmtpHost"]` etc. may be null; `SmtpClient` constructor will throw. | Validate config values and throw meaningful error. |
| EmailService.cs | 44‑48 | `toEmail` may be null; `MailMessage` constructor will NRE. | Validate parameters. |
| EmailService.cs | 61‑66 | `toEmail` may be null. | Validate. |
| EmailService.cs | 78‑82 | `toEmail` may be null. | Validate. |
| StringHelper.cs | 34‑38 | `accountNumber` may be null; `accountNumber.Length` throws. | Add null guard. |
| StringHelper.cs | 40‑44 | `account` may be null; `account[^4..]` throws. | Add null guard. |
| UserService.cs | 108‑110 | `query` may be null; string interpolation in `ExecuteQuery` will produce `"Username LIKE '%'+null+'%'"` causing SQL error. | Validate `query` not null/empty. |
| UserService.cs | 71‑73 | `email` and `username` may be null; interpolated into SQL causing syntax error. | Validate before use. |
| UserService.cs | 84‑86 | `id` may be invalid; but method checks earlier. | No issue. |
| Program.cs | 27‑31 | `_config["Jwt:SecretKey"]!` may be null; `Encoding.UTF8.GetBytes(null)` throws. | Validate secret key presence. |
| AuthService.cs | 84‑88 | `ValidateToken` returns early; later code uses `jwtToken` which could be null if token malformed. | Remove dead code. |
| TransactionService.cs | 94‑96 | `IsWithinDailyLimit` reads `CreatedAt` cast; if DB returns null, cast fails. | Ensure column not null. |

---

**## 6. Dead Code**

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 84‑88 | `ValidateToken` returns before any validation; the code after `return true` is unreachable. | Remove dead code or implement proper validation. |
| AuthService.cs | 100‑102 | `HashPasswordSha1` is never used. | Remove if not needed. |
| DatabaseHelper.cs | 70‑73 | `ExecuteQueryWithParams` marked `[Obsolete]` but still present; not used anywhere. | Delete or replace with safe method. |
| StringHelper.cs | 24‑28 | `JoinWithSeparator` is never called; inefficient implementation. | Remove or make private. |
| TransactionService.cs | 94‑96 | `IsWithinDailyLimit` is defined but never invoked. | Call it in `Transfer`/`Deposit` or remove. |
| TransactionService.cs | 108‑110 | `RefundTransaction` throws `NotImplementedException`; controller catches it and returns 500. | Implement or return proper NotImplemented response. |
| TransactionService.cs | 112‑114 | `FormatCurrency` is never used. | Remove or use in responses. |
| Program.cs | 38 | `app.UseHttpsRedirection();` is commented out. | Uncomment or remove comment if not needed. |
| SampleBankingApp.csproj | 16‑18 | `TreatWarningsAsErrors=false` may hide important warnings. | Consider enabling in CI. |

---

**## 7. Magic Strings and Numbers**

| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 12‑14 | Fallback connection string hard‑codes server, DB, user, password. | Remove fallback; use secure config. |
| AuthService.cs | 15 | `AdminBypassPassword = "SuperAdmin2024"` hard‑coded backdoor. | Remove. |
| AuthService.cs | 84‑88 | `ValidateToken` returns `true` for any non‑empty token – magic logic. | Implement proper validation. |
| AuthService.cs | 115‑117 | JWT secret key, issuer, audience are hard‑coded in `appsettings.json`. | Move to secure secret store. |
| EmailService.cs | 15‑19 | Email subjects are hard‑coded strings. | Move to resources or config if needed. |
| EmailService.cs | 23‑31 | SMTP host, port, username, password are read from config but defaults may be missing. | Validate and document. |
| TransactionService.cs | 15‑16 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` are magic constants. | Move to configuration. |
| TransactionService.cs | 84‑86 | Interest bonus multiplier `0.05m * 1` is a magic number. | Define as constant or config. |
| UserService.cs | 57‑58 | `pageSize` capped at 50 – magic limit. | Define as constant or config. |
| UserService.cs | 57‑58 | `skip = page * pageSize` uses magic pagination formula (incorrect). | Use proper formula. |
| StringHelper.cs | 12‑14 | Regex patterns are hard‑coded strings. | Cache as static readonly. |
| Program.cs | 33‑35 | `ValidateLifetime = false` is a magic security setting. | Set to true. |
| Program.cs | 40‑42 | CORS policy `AllowAnyOrigin/AnyMethod/AnyHeader` – magic permissive values. | Restrict to known origins. |
| Program.cs | 45‑47 | Logging levels set to `Debug` for all categories. | Use environment‑specific levels. |
| SampleBankingApp.csproj | 13‑15 | `DebugSymbols = true`, `DebugType = full` – debug build settings in production. | Adjust for Release. |

---

**## 8. Anti‑patterns and Code Quality**

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 24‑28 | `JoinWithSeparator` uses string concatenation in a loop (O(n²)). | Replace with `string.Join` or `StringBuilder`. |
| StringHelper.cs | 12‑14 | New `Regex` created on each call; costly. | Cache compiled regex as static readonly. |
| StringHelper.cs | 34‑38 | `MaskAccountNumber` does not check for null; could NRE. | Add null guard. |
| StringHelper.cs | 40‑44 | `ObfuscateAccount` does not check for null; could NRE. | Add null guard. |
| DatabaseHelper.cs | 22‑26 | `ExecuteQuery` builds SQL from raw strings – SQL injection risk. | Remove; use parameterised queries only. |
| DatabaseHelper.cs | 38‑44 | `ExecuteNonQuery` opens connection without `using`. | Use `using`. |
| DatabaseHelper.cs | 58‑62 | `ExecuteQuerySafe` creates `SqlDataAdapter` without disposing. | Use `using`. |
| EmailService.cs | 23‑31 | `_smtpClient` stored as a field and reused across threads – not thread‑safe. | Create per‑use or protect with lock. |
| EmailService.cs | 44‑48 | `MailMessage` not disposed. | Wrap in `using`. |
| EmailService.cs | 61‑66 | Same for welcome email. | Wrap in `using`. |
| EmailService.cs | 78‑82 | Same for HTML email. | Wrap in `using`. |
| UserService.cs | 13‑14 | Static mutable `_auditLog` and `_requestCount` accessed without synchronization – race conditions. | Use `ConcurrentBag`/`Interlocked.Increment`. |
| UserService.cs | 71‑73 | `UpdateUser` builds SQL via interpolation – re‑implements ORM poorly. | Use parameterised queries. |
| UserService.cs | 84‑86 | `DeleteUser` same issue. | Use parameters. |
| TransactionService.cs | 55‑57 | Two separate `UPDATE` statements without transaction – violates atomicity. | Wrap in DB transaction. |
| TransactionService.cs | 70‑73 | `RecordTransaction` builds raw SQL with string interpolation – risk of injection and formatting errors. | Use parameters. |
| AuthService.cs | 84‑88 | `ValidateToken` contains dead code after early return. | Remove dead code. |
| AuthService.cs | 100‑102 | `HashPasswordSha1` unused and insecure. | Delete. |
| Program.cs | 33‑35 | `ValidateLifetime = false` disables a core security feature. | Set to true. |
| Program.cs | 38 | HTTPS redirection disabled – anti‑pattern for production APIs. | Enable HTTPS. |
| Program.cs | 40‑42 | Open CORS policy – anti‑pattern. | Restrict origins. |
| SampleBankingApp.csproj | 16‑18 | `DebugSymbols` enabled in production build. | Disable for Release. |

---

**## 9. Configuration Issues**

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 33‑35 | `ValidateLifetime = false` disables JWT expiration checks. | Set to `true`. |
| Program.cs | 27‑31 | `UseDeveloperExceptionPage()` always enabled – exposes stack traces. | Guard with `if (app.Environment.IsDevelopment())`. |
| Program.cs | 38 | HTTPS redirection commented out – app may serve HTTP. | Uncomment `app.UseHttpsRedirection();`. |
| Program.cs | 40‑42 | CORS policy `AllowAnyOrigin/AnyMethod/AnyHeader` – too permissive. | Restrict to known origins and methods. |
| appsettings.json | 5‑7 | JWT secret key (`mysecretkey`) is weak and stored in source control. | Use a strong random key stored in secret manager. |
| appsettings.json | 5‑7 | JWT issuer/audience are static strings; may be okay but should be environment‑specific. | Move to environment‑specific config. |
| appsettings.json | 2‑4 | DB connection string contains plain password. | Store in secret store or use integrated security. |
| appsettings.json | 12‑14 | Email SMTP credentials stored in plain text. | Move to secret store. |
| appsettings.json | 16‑18 | Logging level set to `Debug` for all categories – noisy in production. | Set to `Information` or `Warning` for prod. |
| SampleBankingApp.csproj | 13‑15 | `DebugSymbols=true` and `DebugType=full` – releases will ship symbols. | Set to false for Release configuration. |
| SampleBankingApp.csproj | 16‑18 | `TreatWarningsAsErrors=false` – may allow problematic code to compile. | Consider enabling in CI. |
| SampleBankingApp.csproj | 12‑14 | No explicit package version lock for `System.Data.SqlClient` (v4.8.6) – may have known vulnerabilities. | Verify latest secure version or switch to `Microsoft.Data.SqlClient`. |
| SampleBankingApp.csproj | 12‑14 | `Newtonsoft.Json` version 12.0.3 – outdated; known CVEs. | Upgrade to latest stable version. |
| SampleBankingApp.csproj | 12‑14 | `System.IdentityModel.Tokens.Jwt` version 7.0.0 – check for updates. | Upgrade if newer secure version exists. |
| Program.cs | 45‑47 | Logging configuration not environment‑aware; same Debug level in all envs. | Use `appsettings.Development.json` and `appsettings.Production.json`. |
| Program.cs | 45‑47 | No rate‑limiting or lockout on login endpoint. | Add ASP.NET Core rate limiting middleware. |

---

**## 10. Missing Unit Tests**

| File | Line | Issue | Fix |
|------|------|-------|-----|
| *No test project found* | – | The repository contains no unit‑test project. | Add a test project (e.g., `SampleBankingApp.Tests`). |
| AuthService.cs | 27‑44 | `Login` logic (password hashing, DB lookup, admin bypass). | Write tests for successful login, failed login, admin bypass, and SQL injection attempts. |
| AuthService.cs | 84‑88 | `GenerateJwtToken` token creation and claims. | Test token contains correct claims and expiration. |
| AuthService.cs | 84‑88 | `ValidateToken` (once fixed). | Test valid and expired tokens. |
| TransactionService.cs | 33‑77 | `Transfer` – fee calculation, balance checks, atomicity, email notification. | Test successful transfer, insufficient funds, fee deduction, and that both balances update atomically. |
| TransactionService.cs | 84‑86 | `Deposit` – amount validation, interest bonus, balance update. | Test valid deposit, invalid amounts, and correct bonus applied. |
| TransactionService.cs | 94‑96 | `IsWithinDailyLimit` – daily transaction count enforcement. | Test limit reached and under limit scenarios. |
| UserService.cs | 71‑73 | `GetUserById` – null handling, invalid IDs. | Test valid ID, non‑existent ID, and invalid ID exceptions. |
| UserService.cs | 71‑73 | `UpdateUser` – SQL injection protection, input validation. | Test successful update, injection attempt, and invalid inputs. |
| UserService.cs | 84‑86 | `DeleteUser` – deletion of existing and non‑existing users. | Test deletion success and handling of missing user. |
| UserService.cs | 108‑110 | `SearchUsers` – correct LIKE query and injection safety. | Test search returns expected users and rejects malicious input. |
| UserController.cs | 15‑17 | `GetUser` endpoint returns correct status codes. | Integration tests for 200, 404. |
| TransactionController.cs | 15‑17 | `Transfer` endpoint parses claims safely and returns proper responses. | Test with valid/invalid JWT, insufficient funds, and successful transfer. |
| TransactionController.cs | 38‑44 | `Refund` endpoint returns 500 for unimplemented method. | Verify proper error handling. |
| EmailService.cs | 44‑48 | `SendTransferNotification` – email composition and retry logic. | Mock `SmtpClient` and verify retries and message content. |
| Program.cs | 33‑35 | JWT validation settings affect authentication. | Integration test with expired token when `ValidateLifetime` is true. |
| Configuration | – | Ensure secrets are not loaded from source control. | Test that app fails to start when required secrets are missing. |

*All critical paths should have unit and integration tests covering success, failure, boundary conditions, and security aspects.*