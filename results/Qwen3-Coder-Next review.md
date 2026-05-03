## Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded fallback connection string with plaintext password | Remove fallback; throw if connection string missing |
| SampleBankingApp/Data/DatabaseHelper.cs | 35 | SQL injection in `ExecuteQuery(tableName, whereClause)` via string interpolation | Use parameterized queries or whitelist table/column names |
| SampleBankingApp/Services/AuthService.cs | 22 | Hardcoded admin bypass password in source | Remove hardcoded credentials; use config or external auth |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection in login query via string interpolation | Use parameterized query with `@Username`, `@Password` |
| SampleBankingApp/Services/AuthService.cs | 38 | MD5 hashing used for password hashing | Replace with bcrypt/Argon2/scrypt with salt |
| SampleBankingApp/Services/AuthService.cs | 72 | `ValidateLifetime = false` in JWT config | Set `ValidateLifetime = true` |
| SampleBankingApp/Program.cs | 28 | JWT secret read from config but used with null-forgiving operator; no validation | Validate `jwtSecret` is non-null and sufficiently strong |
| SampleBankingApp/Program.cs | 36 | `UseDeveloperExceptionPage()` called unconditionally | Wrap in `if (app.Environment.IsDevelopment())` |
| SampleBankingApp/Program.cs | 40 | `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` CORS policy | Restrict origins/methods to known domains |
| SampleBankingApp/Program.cs | 42 | HTTPS redirection commented out | Uncomment or enforce HTTPS in production |
| SampleBankingApp/Program.cs | 45 | `EnableSsl = false` in EmailService SMTP config | Set `EnableSsl = true` |
| SampleBankingApp/Services/EmailService.cs | 30 | SMTP credentials read from config without null checks | Guard against null config values |
| SampleBankingApp/Services/TransactionService.cs | 38 | SQL injection in UPDATE queries via string interpolation | Use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 40 | SQL injection in UPDATE queries via string interpolation | Use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 54 | SQL injection in `RecordTransaction` via string interpolation | Use parameterized INSERT query |
| SampleBankingApp/Services/UserService.cs | 37 | SQL injection in `UpdateUser` via string interpolation | Use parameterized UPDATE query |
| SampleBankingApp/Services/UserService.cs | 52 | SQL injection in `DeleteUser` via string interpolation | Use parameterized DELETE query |
| SampleBankingApp/Services/UserService.cs | 72 | SQL injection in `SearchUsers` via `ExecuteQuery(tableName, whereClause)` | Use parameterized LIKE clause |
| SampleBankingApp/Services/UserService.cs | 72 | `ExecuteQuery` used instead of `ExecuteQuerySafe` | Replace with `ExecuteQuerySafe` and parameterized LIKE |
| SampleBankingApp/appsettings.json | 3 | Production connection string with plaintext password | Move to user-secrets or secure vault; never commit |
| SampleBankingApp/appsettings.json | 11 | Weak JWT secret ("mysecretkey") | Use cryptographically secure random string (≥32 chars) |
| SampleBankingApp/appsettings.json | 18 | SMTP password in plaintext | Move to user-secrets or secure vault |

## Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 32 | Transfer checks `fromBalance >= amount` but deducts `amount + fee` | Check `fromBalance >= totalDebit` |
| SampleBankingApp/Services/TransactionService.cs | 32 | No self-transfer check (`fromUserId == toUserId`) | Add guard clause to prevent self-transfers |
| SampleBankingApp/Services/TransactionService.cs | 44 | Deposit interest bonus calculated as `amount * 0.05m * 1` (redundant `* 1`) | Remove `* 1` or clarify intent |
| SampleBankingApp/Services/UserService.cs | 80 | Pagination offset uses `page * pageSize` instead of `(page - 1) * pageSize` | Change to `skip = (page - 1) * pageSize` |
| SampleBankingApp/Services/UserService.cs | 80 | No lower bound check on `page` (e.g., `page <= 0`) | Validate `page >= 1` |
| SampleBankingApp/Services/AuthService.cs | 32 | Login bypass for admin does not check password hash | Admin bypass should require correct password or be removed |
| SampleBankingApp/Services/TransactionService.cs | 32 | No check for `toUserId == fromUserId` before sending transfer notification | Skip notification if self-transfer (after adding guard) |

## Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 57 | `ValidateToken` returns `true` unconditionally after early return | Remove unreachable code or implement validation |
| SampleBankingApp/Services/UserService.cs | 72 | `SearchUsers` catches all exceptions and returns empty list | Log exception; rethrow or return null with error indicator |
| SampleBankingApp/Services/EmailService.cs | 55 | `SendWelcomeEmail` swallows all exceptions silently | Log exception; consider throwing or returning status |
| SampleBankingApp/Services/EmailService.cs | 66 | `SendWelcomeEmailHtml` swallows exceptions silently | Log exception; consider throwing or returning status |
| SampleBankingApp/Services/TransactionService.cs | 32 | No transaction scope around balance updates | Wrap in `TransactionScope` or use database transaction |
| SampleBankingApp/Services/TransactionService.cs | 32 | Email sent after DB updates — if email fails, state is inconsistent | Move email after commit or use outbox pattern |
| SampleBankingApp/Controllers/UserController.cs | 45 | `ex.Message` returned directly to client | Return generic error message; log full exception |
| SampleBankingApp/Controllers/TransactionController.cs | 35 | `NotImplementedException` caught and returned as 500 | Return `501 Not Implemented` or remove try/catch |

## Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 20 | `GetOpenConnection()` returns undisposed `SqlConnection` | Caller must dispose; document contract or return `IDisposable` wrapper |
| SampleBankingApp/Data/DatabaseHelper.cs | 27 | `ExecuteQuery` opens connection but never disposes `SqlDataAdapter`, `SqlCommand`, or `SqlConnection` | Wrap in `using` blocks |
| SampleBankingApp/Data/DatabaseHelper.cs | 46 | `ExecuteNonQuery` opens connection but never disposes `SqlCommand` or `SqlConnection` | Wrap in `using` blocks |
| SampleBankingApp/Services/AuthService.cs | 30 | `SqlConnection`, `SqlCommand`, `SqlDataReader` opened but never disposed | Wrap in `using` blocks |
| SampleBankingApp/Services/EmailService.cs | 25 | `_smtpClient` held as instance field — `SmtpClient` implements `IDisposable` | Implement `IDisposable` in `EmailService` and dispose `_smtpClient` |
| SampleBankingApp/Services/EmailService.cs | 37 | `MailMessage` created but never disposed | Wrap in `using` block |
| SampleBankingApp/Services/EmailService.cs | 50 | `MailMessage` created but never disposed | Wrap in `using` block |
| SampleBankingApp/Services/EmailService.cs | 64 | `MailMessage` created but never disposed | Wrap in `using` block |

## Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/TransactionController.cs | 23 | `userIdClaim!` used with null-forgiving operator; no null check | Validate claim exists before parsing |
| SampleBankingApp/Controllers/TransactionController.cs | 39 | Same issue with `userIdClaim!` | Validate claim exists before parsing |
| SampleBankingApp/Controllers/UserController.cs | 45 | `ex.Message` returned to client — could be null | Guard against null or use `ex.ToString()` |
| SampleBankingApp/Services/AuthService.cs | 32 | `_config.GetConnectionString("DefaultConnection")` used without null check | Validate connection string is non-null |
| SampleBankingApp/Services/AuthService.cs | 57 | `_config["Jwt:SecretKey"]!` used with null-forgiving operator | Validate secret key exists |
| SampleBankingApp/Services/EmailService.cs | 25 | `_config["Email:SmtpHost"]` used without null check | Validate SMTP host exists |
| SampleBankingApp/Services/EmailService.cs | 27 | `_config["Email:Username"]` and `_config["Email:Password"]` used without null check | Validate credentials exist |
| SampleBankingApp/Services/UserService.cs | 37 | `table.Rows[0]` accessed without checking `Rows.Count` | Already handled in `GetUserById`, but `UpdateUser`/`DeleteUser` lack safety |
| SampleBankingApp/Services/UserService.cs | 37 | `MapRowToUser` assumes all columns exist — no null guard on casts | Add null checks or use safe casts (`as`) |

## Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 66 | `HashPasswordSha1` method defined but never called | Remove or use if intended for legacy support |
| SampleBankingApp/Services/AuthService.cs | 72 | `ValidateToken` has unreachable code after `return true` | Remove unreachable code |
| SampleBankingApp/Helpers/StringHelper.cs | 44 | `JoinWithSeparator` is duplicated by `JoinWithSeparatorFixed` | Remove `JoinWithSeparator` |
| SampleBankingApp/Services/UserService.cs | 20 | `_auditLog` and `_requestCount` are static — shared across requests | Remove static state or make thread-safe |
| SampleBankingApp/Services/UserService.cs | 20 | `_requestCount` incremented but never used | Remove or use for metrics |
| SampleBankingApp/Services/UserService.cs | 102 | `GetAuditReport` uses manual string concatenation instead of `string.Join` | Use `string.Join("\n", _auditLog)` |
| SampleBankingApp/Services/TransactionService.cs | 86 | `RefundTransaction` throws `NotImplementedException` | Remove or implement |

## Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded fallback password `Admin1234!` | Remove fallback |
| SampleBankingApp/Services/AuthService.cs | 22 | Hardcoded admin password `SuperAdmin2024` | Remove |
| SampleBankingApp/Services/TransactionService.cs | 14 | `TransactionFeeRate = 0.015m` should be configurable | Move to config |
| SampleBankingApp/Services/TransactionService.cs | 15 | `MaxTransactionsPerDay = 10` should be configurable | Move to config |
| SampleBankingApp/Services/TransactionService.cs | 44 | `0.05m` interest bonus rate hardcoded | Move to config |
| SampleBankingApp/Services/TransactionService.cs | 44 | `1` multiplier in `amount * 0.05m * 1` is magic | Remove or clarify |
| SampleBankingApp/Services/UserService.cs | 78 | `pageSize > 50` limit hardcoded | Move to config |
| SampleBankingApp/Services/UserService.cs | 102 | `"\n"` used for line separator | Use `Environment.NewLine` or config |
| SampleBankingApp/Services/EmailService.cs | 16 | `"notifications@company.com"` repeated | Define as constant |
| SampleBankingApp/Services/EmailService.cs | 17 | `"support@company.com"` hardcoded | Move to config |
| SampleBankingApp/Services/EmailService.cs | 20 | `"EmailPass99"` hardcoded | Move to config |
| SampleBankingApp/Services/AuthService.cs | 22 | `"SuperAdmin2024"` hardcoded | Remove |
| SampleBankingApp/Services/AuthService.cs | 38 | `"admin"` username hardcoded | Use config or role-based access |
| SampleBankingApp/Services/UserService.cs | 102 | `"\n"` used for line separator | Use `Environment.NewLine` or config |

## Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 44 | `result += item + separator` in loop — O(n²) | Use `string.Join` (already exists as `JoinWithSeparatorFixed`) |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `new Regex(...)` created per call | Make `static readonly` |
| SampleBankingApp/Services/UserService.cs | 20 | Static `_auditLog` and `_requestCount` — not thread-safe | Use `ConcurrentBag` or remove static state |
| SampleBankingApp/Services/UserService.cs | 102 | Manual string concatenation in `GetAuditReport` | Use `string.Join("\n", _auditLog)` |
| SampleBankingApp/Services/AuthService.cs | 32 | Manual SQL string building instead of parameterized query | Use parameterized query |
| SampleBankingApp/Services/TransactionService.cs | 38 | Manual SQL string building instead of parameterized query | Use parameterized query |
| SampleBankingApp/Services/TransactionService.cs | 40 | Manual SQL string building instead of parameterized query | Use parameterized query |
| SampleBankingApp/Services/TransactionService.cs | 54 | Manual SQL string building instead of parameterized query | Use parameterized query |
| SampleBankingApp/Services/UserService.cs | 37 | Manual SQL string building instead of parameterized query | Use parameterized query |
| SampleBankingApp/Services/UserService.cs | 52 | Manual SQL string building instead of parameterized query | Use parameterized query |
| SampleBankingApp/Services/UserService.cs | 72 | Manual SQL string building instead of parameterized query | Use parameterized query |
| SampleBankingApp/Services/AuthService.cs | 38 | `MD5` used for password hashing — deprecated | Replace with bcrypt/Argon2 |
| SampleBankingApp/Services/AuthService.cs | 66 | `SHA1` used in unused method — deprecated | Remove or replace |

## Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Program.cs | 36 | `UseDeveloperExceptionPage()` called unconditionally | Wrap in `if (app.Environment.IsDevelopment())` |
| SampleBankingApp/Program.cs | 40 | Overly permissive CORS (`AllowAnyOrigin`, etc.) | Restrict origins/methods |
| SampleBankingApp/Program.cs | 42 | HTTPS redirection commented out | Uncomment or enforce HTTPS |
| SampleBankingApp/Program.cs | 28 | `ValidateLifetime = false` in JWT config | Set to `true` |
| SampleBankingApp/appsettings.json | 11 | Weak JWT secret (`"mysecretkey"`) | Use cryptographically secure secret |
| SampleBankingApp/appsettings.json | 18 | SMTP password in plaintext | Move to user-secrets |
| SampleBankingApp/appsettings.json | 3 | Production connection string with plaintext password | Move to user-secrets |
| SampleBankingApp/appsettings.json | 23 | Log level set to `Debug` for all namespaces | Set to `Information` or higher for production |
| SampleBankingApp/SampleBankingApp.csproj | 10 | `<DebugSymbols>true</DebugSymbols>` and `<DebugType>full</DebugType>` in release | Set `<DebugSymbols>false</DebugSymbols>` for release builds |

## Missing Unit Tests

| File | Line | Issue | Fix |
|------|------|-------|-----|
| N/A | N/A | No test project exists | Add `xunit`/` MSTest` test project with tests for: |
| | | | - `AuthService.Login` (valid/invalid credentials, admin bypass) |
| | | | - `TransactionService.Transfer` (insufficient funds, self-transfer, fee calculation) |
| | | | - `TransactionService.Deposit` (boundary values, interest calculation) |
| | | | - `UserService.GetUsersPage` (pagination edge cases: page=0, pageSize=0, max pageSize) |
| | | | - `StringHelper.IsValidEmail` (edge cases: null, long email, invalid formats) |
| | | | - `StringHelper.JoinWithSeparatorFixed` (empty collection, single item) |
| | | | - JWT token validation (expired, invalid signature) |
| | | | - Authorization attributes on controllers (unauthorized access) |
| | | | - SQL injection vectors (parameterized queries verified) |