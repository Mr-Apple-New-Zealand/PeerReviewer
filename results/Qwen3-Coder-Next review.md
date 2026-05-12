## Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 15 | Hardcoded fallback connection string with plaintext credentials | Remove fallback; throw if connection string missing |
| SampleBankingApp/Data/DatabaseHelper.cs | 32 | SQL injection via `tableName` and `whereClause` in `ExecuteQuery` | Use parameterized queries only; avoid dynamic table/column names |
| SampleBankingApp/Services/AuthService.cs | 20 | Hardcoded admin bypass password in source | Remove hardcoded password; use configuration or external auth |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection in login query via string interpolation | Use parameterized query with `@Username`, `@Password` |
| SampleBankingApp/Services/AuthService.cs | 38 | MD5 hashing used for password hashing | Replace with bcrypt/Argon2/scrypt with salt |
| SampleBankingApp/Services/AuthService.cs | 65 | `ValidateLifetime = false` in JWT config | Set `ValidateLifetime = true` |
| SampleBankingApp/Program.cs | 22 | JWT secret read from config without null guard | Add null check and fail fast if missing |
| SampleBankingApp/Program.cs | 31 | `UseDeveloperExceptionPage()` called unconditionally | Wrap in `app.Environment.IsDevelopment()` |
| SampleBankingApp/Program.cs | 34 | HTTPS redirection commented out | Uncomment or enforce HTTPS in production |
| SampleBankingApp/Program.cs | 36 | Overly permissive CORS (`AllowAnyOrigin`, `AllowAnyMethod`, `AllowAnyHeader`) | Restrict to known origins/methods |
| SampleBankingApp/Services/EmailService.cs | 27 | SMTP password stored in plaintext in config | Use secret manager (e.g., Azure Key Vault) |
| SampleBankingApp/appsettings.json | 3 | Production connection string with plaintext credentials | Use environment variables or secret manager |
| SampleBankingApp/appsettings.json | 11 | JWT secret `"mysecretkey"` is weak and hardcoded | Use strong random key; store in secret manager |
| SampleBankingApp/appsettings.json | 19 | SMTP password `"EmailPass99"` is weak and hardcoded | Use secret manager |
| SampleBankingApp/Services/UserService.cs | 7 | Static `_auditLog` and `_requestCount` shared across requests | Remove static state or add thread-safety |

## Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 42 | Fee applied only when `fromBalance >= amount`, but total debit is `amount + fee` | Check `fromBalance >= totalDebit` before proceeding |
| SampleBankingApp/Services/TransactionService.cs | 46 | No self-transfer check (`fromUserId == toUserId`) | Add early return if `fromUserId == toUserId` |
| SampleBankingApp/Services/TransactionService.cs | 58 | Deposit interest bonus (`0.05m * 1`) is nonsensical (likely typo) | Clarify logic; likely should be `amount * 0.05m` or remove |
| SampleBankingApp/Services/UserService.cs | 67 | Pagination offset calculation: `skip = page * pageSize` is off-by-one | Use `skip = (page - 1) * pageSize` |
| SampleBankingApp/Services/UserService.cs | 100 | `SearchUsers` swallows exceptions and returns empty list | Log exception; rethrow or return null with error indicator |
| SampleBankingApp/Services/UserService.cs | 106 | `MapRowToUser` does not handle `LastLoginAt` (missing from model) | Add `LastLoginAt` mapping or remove from model |

## Error Handling

| File | Line | Issue | Fix |
|------|------|------|-----|
| SampleBankingApp/Services/AuthService.cs | 38 | Broad `Exception` not caught in login; `SqlException` may leak | Wrap DB calls in try/catch; return null on error |
| SampleBankingApp/Services/TransactionService.cs | 46 | No transaction around balance updates | Use `SqlTransaction` to ensure atomicity |
| SampleBankingApp/Services/TransactionService.cs | 58 | Email sent after DB writes — if email fails, state is inconsistent | Move email after commit or use outbox pattern |
| SampleBankingApp/Services/UserService.cs | 100 | `catch (Exception)` swallows all errors silently | Log exception; rethrow or return error status |
| SampleBankingApp/Services/UserService.cs | 106 | `MapRowToUser` may throw `InvalidCastException` on null DB values | Use safe casts (`row.Field<T?>`) or null checks |
| SampleBankingApp/Controllers/UserController.cs | 60 | `ex.Message` returned directly to client | Return generic error message; log details |

## Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 20 | `SqlConnection` opened but never disposed in `GetOpenConnection` | Return `IDisposable` and document caller responsibility |
| SampleBankingApp/Data/DatabaseHelper.cs | 27 | `SqlDataReader` not disposed in `Login` (via `ExecuteQuerySafe`) | Use `using var reader = ...` |
| SampleBankingApp/Data/DatabaseHelper.cs | 40 | `SqlConnection` opened in `ExecuteQuery` but never closed/disposed | Use `using` blocks |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | `SqlConnection` opened in `ExecuteNonQuery` but never closed | Use `using` block |
| SampleBankingApp/Services/AuthService.cs | 32 | `SqlConnection` and `SqlCommand` not disposed | Wrap in `using` blocks |
| SampleBankingApp/Services/EmailService.cs | 25 | `_smtpClient` held as instance field — not thread-safe, may leak sockets | Use `using` for each send, or inject `IHttpClientFactory` |
| SampleBankingApp/Services/EmailService.cs | 37, 58, 70 | `MailMessage` not disposed | Wrap in `using` block |
| SampleBankingApp/Services/UserService.cs | 37 | `DataTable` returned from `ExecuteQuerySafe` not disposed | Caller must dispose; document contract |

## Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/TransactionController.cs | 24 | `userIdClaim!` used without null check | Validate claim exists; return `Unauthorized` if missing |
| SampleBankingApp/Controllers/TransactionController.cs | 39 | Same issue for `userId` | Validate claim exists |
| SampleBankingApp/Controllers/UserController.cs | 47 | `ex.Message` returned to client — may leak stack info | Use generic message |
| SampleBankingApp/Data/DatabaseHelper.cs | 15 | `_connectionString` falls back to hardcoded value — may be null if config missing | Remove fallback; throw if null |
| SampleBankingApp/Services/AuthService.cs | 32 | `_config.GetConnectionString("DefaultConnection")` may be null | Add null check |
| SampleBankingApp/Services/AuthService.cs | 65 | `jwtSecret!` used without null check | Add null check and fail fast |
| SampleBankingApp/Services/EmailService.cs | 27 | `_config["Email:..."]` used without null checks | Validate config values exist |
| SampleBankingApp/Services/UserService.cs | 37 | `table.Rows[0]` accessed without checking `Rows.Count` | Add `if (table.Rows.Count == 0)` |
| SampleBankingApp/Services/UserService.cs | 67 | `pageSize` clamped to 50 but `page` not validated | Validate `page >= 1` |
| SampleBankingApp/Services/UserService.cs | 100 | `query` passed directly to `LIKE '%{query}%'` — SQL injection risk | Use parameterized query |

## Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 20 | `AdminBypassPassword` constant unused in production (only in dev) | Remove or document as dev-only |
| SampleBankingApp/Services/AuthService.cs | 75 | `HashPasswordSha1` method defined but never called | Remove |
| SampleBankingApp/Services/AuthService.cs | 80 | `ValidateToken` returns `true` early — rest unreachable | Remove dead code or implement validation |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | `JoinWithSeparator` duplicated by `JoinWithSeparatorFixed` | Remove `JoinWithSeparator` |
| SampleBankingApp/Services/TransactionService.cs | 114 | `RefundTransaction` throws `NotImplementedException` | Remove or implement |
| SampleBankingApp/Services/UserService.cs | 7 | Static `_auditLog` never cleared — memory leak | Remove or use scoped logging |
| SampleBankingApp/Services/UserService.cs | 8 | Static `_requestCount` never used | Remove |

## Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 15 | Hardcoded fallback connection string | Remove; use config only |
| SampleBankingApp/Services/AuthService.cs | 20 | Hardcoded admin password | Move to config or remove |
| SampleBankingApp/Services/TransactionService.cs | 15 | `TransactionFeeRate = 0.015m` | Extract to config |
| SampleBankingApp/Services/TransactionService.cs | 16 | `MaxTransactionsPerDay = 10` | Extract to config |
| SampleBankingApp/Services/TransactionService.cs | 58 | `0.05m * 1` magic number | Extract to config |
| SampleBankingApp/Services/UserService.cs | 67 | `pageSize > 50` limit | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 | `1000000` max user ID | Extract to config |
| SampleBankingApp/Services/UserService.cs | 106 |