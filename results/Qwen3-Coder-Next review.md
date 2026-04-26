## Review Report

### 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded fallback connection string with plaintext password | Remove fallback; throw if config missing |
| SampleBankingApp/Data/DatabaseHelper.cs | 33 | SQL injection via `tableName` and `whereClause` in `ExecuteQuery` | Use parameterized queries or whitelist table/column names |
| SampleBankingApp/Services/AuthService.cs | 22 | Hardcoded admin bypass password in source | Remove hardcoded password; use config or external auth |
| SampleBankingApp/Services/AuthService.cs | 35 | SQL injection in login query via string interpolation | Use parameterized query for `username` and `hashedPassword` |
| SampleBankingApp/Services/AuthService.cs | 31 | MD5 hashing used for passwords | Replace with bcrypt/Argon2/scrypt |
| SampleBankingApp/Services/AuthService.cs | 93 | `ValidateToken` returns true unconditionally (dead code after return) | Implement actual validation logic |
| SampleBankingApp/Program.cs | 28 | `ValidateLifetime = false` on JWT | Set `ValidateLifetime = true` |
| SampleBankingApp/Program.cs | 35 | `UseDeveloperExceptionPage()` called unconditionally | Wrap in `app.Environment.IsDevelopment()` |
| SampleBankingApp/Program.cs | 38 | HTTPS redirection commented out | Uncomment or explicitly disable in production config |
| SampleBankingApp/Program.cs | 40 | Overly permissive CORS (`AllowAnyOrigin`, `AllowAnyMethod`, `AllowAnyHeader`) | Restrict origins/methods; avoid `AllowAnyOrigin` with authentication |
| SampleBankingApp/Services/EmailService.cs | 27 | SMTP credentials read from config without null guard | Add null checks before using config values |
| SampleBankingApp/appsettings.json | 3 | Production connection string with plaintext password | Use secrets manager or environment variables |
| SampleBankingApp/appsettings.json | 14 | JWT secret key is weak ("mysecretkey") | Use cryptographically secure random key (≥32 bytes) |
| SampleBankingApp/appsettings.json | 22 | SMTP password in plaintext | Use secrets manager or environment variables |
| SampleBankingApp/Services/UserService.cs | 11 | Static `_auditLog` list shared across requests (thread-safety issue) | Use thread-safe collection or per-request logging |
| SampleBankingApp/Services/UserService.cs | 12 | Static `_requestCount` shared across requests (thread-safety issue) | Use `Interlocked.Increment` or remove static state |
| SampleBankingApp/Services/TransactionService.cs | 51 | SQL injection in `RecordTransaction` via string interpolation | Use parameterized query for all values |
| SampleBankingApp/Services/TransactionService.cs | 45 | SQL injection in `Transfer` via string interpolation | Use parameterized queries for balance updates |
| SampleBankingApp/Services/TransactionService.cs | 64 | SQL injection in `Deposit` via string interpolation | Use parameterized query |
| SampleBankingApp/Services/UserService.cs | 76 | SQL injection in `SearchUsers` via `ExecuteQuery` | Use `ExecuteQuerySafe` with parameterized `LIKE` clause |
| SampleBankingApp/Services/UserService.cs | 76 | SQL injection in `SearchUsers` via `ExecuteQuery` | Use `ExecuteQuerySafe` with parameterized `LIKE` clause |

### 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/UserService.cs | 88 | Pagination offset uses `page * pageSize` instead of `(page-1) * pageSize` | Change to `(page - 1) * pageSize` |
| SampleBankingApp/Services/TransactionService.cs | 43 | Transfer checks `fromBalance >= amount` but deducts `amount + fee`, risking negative balance | Check `fromBalance >= totalDebit` before proceeding |
| SampleBankingApp/Services/TransactionService.cs | 62 | Deposit interest bonus calculated as `amount * 0.05m * 1` (redundant `* 1`) | Remove `* 1` or clarify intent |
| SampleBankingApp/Services/TransactionService.cs | 46 | No check for self-transfer (`fromUserId == toUserId`) | Add guard clause to prevent self-transfers |
| SampleBankingApp/Services/TransactionService.cs | 43 | No check for `toUserId` existence before using `toUserTable.Rows[0]` | Validate `toUserTable.Rows.Count > 0` before access |
| SampleBankingApp/Services/UserService.cs | 105 | `GetAuditReport()` concatenates strings inefficiently | Use `string.Join("\n", _auditLog)` |
| SampleBankingApp/Services/UserService.cs | 105 | `GetAuditReport()` does not handle null entries in `_auditLog` | Filter nulls or use `string.Join` with `Where` |

### 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/UserService.cs | 120 | `SearchUsers` catches `Exception` and returns empty list | Log exception; rethrow or return null with clear contract |
| SampleBankingApp/Services/TransactionService.cs | 101 | `RecordTransaction` lacks transaction scope for atomicity | Wrap in `SqlTransaction` with `Commit/Rollback` |
| SampleBankingApp/Services/TransactionService.cs | 45 | Balance updates lack transaction scope | Use `SqlTransaction` for atomic balance changes |
| SampleBankingApp/Services/TransactionService.cs | 46 | Email sent after DB updates — if email fails, state is inconsistent | Move email sending after DB commit or use outbox pattern |
| SampleBankingApp/Services/AuthService.cs | 41 | `Login` returns null without distinguishing between "user not found" and "inactive user" | Return structured result with reason |
| SampleBankingApp/Services/UserService.cs | 105 | `GetAuditReport()` does not handle null entries in `_auditLog` | Filter nulls or use `string.Join` with `Where` |
| SampleBankingApp/Services/TransactionService.cs | 101 | `RecordTransaction` lacks transaction scope for atomicity | Wrap in `SqlTransaction` with `Commit/Rollback` |
| SampleBankingApp/Services/TransactionService.cs | 45 | Balance updates lack transaction scope | Use `SqlTransaction` for atomic balance changes |
| SampleBankingApp/Services/TransactionService.cs | 46 | Email sent after DB updates — if email fails, state is inconsistent | Move email sending after DB commit or use outbox pattern |

### 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 36 | `SqlConnection`, `SqlCommand`, `SqlDataReader` not disposed | Wrap in `using` statements |
| SampleBankingApp/Data/DatabaseHelper.cs | 21 | `GetOpenConnection()` returns open connection without disposal contract | Document ownership and disposal responsibility |
| SampleBankingApp/Data/DatabaseHelper.cs | 33 | `ExecuteQuery` does not dispose `SqlDataAdapter`/`SqlCommand`/`SqlConnection` | Wrap in `using` blocks |
| SampleBankingApp/Data/DatabaseHelper.cs | 55 | `ExecuteNonQuery` does not dispose `SqlCommand`/`SqlConnection` | Wrap in `using` blocks |
| SampleBankingApp/Services/EmailService.cs | 27 | `_smtpClient` held as instance field (not thread-safe, socket leak risk) | Use `using` for each send or implement `IDisposable` |
| SampleBankingApp/Services/EmailService.cs | 44 | `MailMessage` not disposed in `SendTransferNotification` | Wrap in `using` |
| SampleBankingApp/Services/EmailService.cs | 62 | `MailMessage` not disposed in `SendWelcomeEmail` | Wrap in `using` |
| SampleBankingApp/Services/EmailService.cs | 74 | `MailMessage` not disposed in `SendWelcomeEmailHtml` | Wrap in `using` |

### 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/TransactionController.cs | 23 | `userIdClaim!` used without null check | Add null check and return `Unauthorized` if missing |
| SampleBankingApp/Controllers/TransactionController.cs | 37 | `userIdClaim!` used without null check | Add null check and return `Unauthorized` if missing |
| SampleBankingApp/Controllers/UserController.cs | 52 | `ex.Message` returned directly to client | Return generic error message; log details |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | `_connectionString` may be null if config missing | Guard with null-coalescing or throw |
| SampleBankingApp/Services/AuthService.cs | 62 | `_config["Jwt:SecretKey"]!` used without null check | Add null check and throw if missing |
| SampleBankingApp/Services/AuthService.cs | 35 | `username` and `hashedPassword` interpolated without null check | Guard against null |
| SampleBankingApp/Services/TransactionService.cs | 43 | `fromUserTable.Rows[0]` accessed without `Rows.Count > 0` check | Validate row count before access |
| SampleBankingApp/Services/TransactionService.cs | 44 | `toUserTable.Rows[0]` accessed without `Rows.Count > 0` check | Validate row count before access |
| SampleBankingApp/Services/UserService.cs | 43 | `table.Rows[0]` accessed without `Rows.Count > 0` check | Already handled correctly (see line 44) — no issue |
| SampleBankingApp/Services/UserService.cs | 105 | `_auditLog` may contain null entries | Filter nulls or use `string.Join` with `Where` |
| SampleBankingApp/Services/UserService.cs | 120 | `query` passed to `ExecuteQuery` without null check | Guard against null |
| SampleBankingApp/Services/EmailService.cs | 27 | `_config["Email:Username"]` and `_config["Email:Password"]` used without null check | Add null checks before creating `NetworkCredential` |

### 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 88 | `ValidateToken` has unreachable code after `return true` | Remove dead code or implement validation |
| SampleBankingApp/Services/AuthService.cs | 22 | `AdminBypassPassword` constant unused in production (only in dev) | Remove or document as dev-only |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `JoinWithSeparator` duplicated by `JoinWithSeparatorFixed` | Remove `JoinWithSeparator` |
| SampleBankingApp/Services/TransactionService.cs | 101 | `RefundTransaction` throws `NotImplementedException` | Remove or implement |
| SampleBankingApp/Services/UserService.cs | 105 | `GetAuditReport()` uses inefficient string concatenation | Replace with `string.Join` |
| SampleBankingApp/Services/UserService.cs | 105 | `GetAuditReport()` does not handle null entries in `_auditLog` | Filter nulls or use `string.Join` with `Where` |

### 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 17 | `TransactionFeeRate = 0.015m` hardcoded | Move to config |
| SampleBankingApp/Services/TransactionService.cs | 18 | `MaxTransactionsPerDay = 10` hardcoded | Move to config |
| SampleBankingApp/Services/TransactionService.cs | 62 | `amount > 1000000` deposit cap hardcoded | Move to config |
| SampleBankingApp/Services/TransactionService.cs | 62 | `0.05m` interest bonus rate hardcoded | Move to config |
| SampleBankingApp/Services/UserService.cs | 32 | `pageSize > 50` limit hardcoded | Move to config |
| SampleBankingApp/Services/UserService.cs | 105 | `"\n"` line separator hardcoded | Use `Environment.NewLine` |
| SampleBankingApp/Services/EmailService.cs | 16 | `"notifications@company.com"` hardcoded in multiple places | Extract to constant |
| SampleBankingApp/Services/EmailService.cs | 17 | `"support@company.com"` hardcoded | Extract to constant |
| SampleBankingApp/Services/AuthService.cs | 22 | `"SuperAdmin2024"` hardcoded | Move to config or remove |
| SampleBankingApp/Services/AuthService.cs | 31 | `"md5"` algorithm hardcoded | Use constant or config |
| SampleBankingApp/Services/AuthService.cs | 83 | `"SuperAdmin"` role hardcoded | Use constant |
| SampleBankingApp/Services/UserService.cs | 105 | `"\n"` line separator hardcoded | Use `Environment.NewLine` |
| SampleBankingApp/Services/UserService.cs | 105 | `"\n"` line separator hardcoded | Use `Environment.NewLine` |

### 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 37 | `result += item + separator` in loop (O(n²)) | Use `string.Join` |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | `new Regex(...)` created per call | Make `static readonly` |
| SampleBankingApp/Services/UserService.cs | 11 | Static `_auditLog` list (mutable shared state) | Use thread-safe collection or per-request logging |
| SampleBankingApp/Services/UserService.cs | 12 | Static `_requestCount` (mutable shared state) | Use `Interlocked.Increment` or remove static state |
| SampleBankingApp/Services/UserService.cs | 105 | Inefficient string concatenation in `GetAuditReport` | Use `string.Join` |
| SampleBankingApp/Services/UserService.cs | 105 | Inefficient string concatenation in `GetAuditReport` | Use `string.Join` |
| SampleBankingApp/Services/UserService.cs | 105 | Inefficient string concatenation in `GetAuditReport` | Use `string.Join` |
| SampleBankingApp/Services/UserService.cs | 105 | Inefficient string concatenation in `GetAuditReport` | Use `string.Join` |

### 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Program.cs | 35 | `UseDeveloperExceptionPage()` called unconditionally | Wrap in `app.Environment.IsDevelopment()` |
| SampleBankingApp/Program.cs | 38 | HTTPS redirection commented out | Uncomment or explicitly disable in production config |
| SampleBankingApp/Program.cs | 40 | Overly permissive CORS | Restrict origins/methods |
| SampleBankingApp/SampleBankingApp.csproj | 10 | `<DebugType>full</DebugType>` in release builds | Use `portable` or `embedded` for production |
| SampleBankingApp/SampleBankingApp.csproj | 9 | `<DebugSymbols>true</DebugSymbols>` in release builds | Set to `false` for production |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `<TreatWarningsAsErrors>false</TreatWarningsAsErrors>` | Set to `true` for CI builds |
| SampleBankingApp/appsettings.json | 12 | JWT secret key is weak | Use cryptographically secure key |
| SampleBankingApp/appsettings.json | 16 | SMTP port 25 (insecure) | Use 587 (submission) or 465 (SMTPS) |
| SampleBankingApp/appsettings.json | 20 | SMTP password in plaintext | Use secrets manager |
| SampleBankingApp/appsettings.json | 26 | Log level set to `Debug` for all namespaces | Use `Information` or `Warning` in production |

### 10. Missing Unit Tests

| File | Issue | Fix |
|------|-------|-----|
| N/A | No test project exists. Critical methods to test: `AuthService.Login` (SQL injection, MD5, bypass), `TransactionService.Transfer` (balance checks, self-transfer, fee calculation), `TransactionService.Deposit` (cap, interest), `UserService.GetUsersPage` (pagination offset), `StringHelper.IsValidEmail` (edge cases), `AuthService.ValidateToken` (dead code). | Add xunit/nunit test project; cover auth flows, financial calculations, pagination, input validation, and edge cases. |