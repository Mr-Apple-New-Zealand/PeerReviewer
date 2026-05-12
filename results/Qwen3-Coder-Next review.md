## Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded fallback connection string with plaintext password | Remove fallback; throw if config missing |
| SampleBankingApp/Data/DatabaseHelper.cs | 32 | SQL injection via string interpolation in `ExecuteQuery` | Use parameterized queries; remove unsafe method |
| SampleBankingApp/Services/AuthService.cs | 25 | Hardcoded admin bypass password in source | Remove hardcoded credentials; use config or external secret store |
| SampleBankingApp/Services/AuthService.cs | 34 | SQL injection in login query via string interpolation | Use parameterized query with `@Username`, `@Password` |
| SampleBankingApp/Services/AuthService.cs | 40 | Weak password hashing using MD5 | Replace MD5 with PBKDF2 or BCrypt |
| SampleBankingApp/Services/AuthService.cs | 72 | `ValidateLifetime = false` in JWT config | Set `ValidateLifetime = true` |
| SampleBankingApp/Program.cs | 30 | `UseDeveloperExceptionPage()` called unconditionally | Wrap in `if (app.Environment.IsDevelopment())` |
| SampleBankingApp/Program.cs | 34 | HTTPS redirection commented out | Uncomment and enable in production |
| SampleBankingApp/Program.cs | 36 | Overly permissive CORS (`AllowAnyOrigin`, `AllowAnyMethod`, `AllowAnyHeader`) | Restrict to known origins/methods; avoid `AllowAnyOrigin` with authentication |
| SampleBankingApp/appsettings.json | 3 | Production connection string with plaintext password | Move to user secrets or secure vault; use integrated auth where possible |
| SampleBankingApp/appsettings.json | 7 | Weak JWT secret key ("mysecretkey") | Use cryptographically secure random key (≥256 bits) |
| SampleBankingApp/appsettings.json | 15 | SMTP password in plaintext | Use user secrets or secure vault |
| SampleBankingApp/Services/EmailService.cs | 29 | SMTP credentials read from config without null guard | Add null checks before creating `NetworkCredential` |
| SampleBankingApp/Services/EmailService.cs | 31 | `EnableSsl = false` | Set `EnableSsl = true` in production |

## Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/UserService.cs | 77 | Pagination offset calculation: `page * pageSize` should be `(page - 1) * pageSize` | Use `(page - 1) * pageSize` |
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check uses `fromBalance >= amount` but deducts `amount + fee`, allowing negative balance | Check `fromBalance >= totalDebit` |
| SampleBankingApp/Services/TransactionService.cs | 45 | No self-transfer check (`fromUserId == toUserId`) | Add guard clause to prevent self-transfers |
| SampleBankingApp/Services/TransactionService.cs | 53 | `RecordTransaction` uses string interpolation for SQL (SQL injection risk) | Use parameterized query |
| SampleBankingApp/Services/TransactionService.cs | 64 | Deposit interest bonus applied even for zero/negative amounts (though amount validation exists) | Move interest logic after validation; ensure `amount > 0` |
| SampleBankingApp/Services/UserService.cs | 63 | `SearchUsers` uses unsafe `ExecuteQuery` with string interpolation | Replace with parameterized query |
| SampleBankingApp/Services/UserService.cs | 103 | `_auditLog` and `_requestCount` are static mutable shared state (thread-unsafe) | Use thread-safe collections or remove static state |

## Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 58 | `ValidateToken` returns `true` unconditionally due to unreachable code after `return true` | Remove early return; implement actual validation |
| SampleBankingApp/Services/UserService.cs | 103 | `SearchUsers` catches all exceptions and returns empty list | Log exception; rethrow or return null with clear contract |
| SampleBankingApp/Services/TransactionService.cs | 45 | No transaction scope around balance updates; partial failure possible | Wrap in `TransactionScope` or use database transaction |
| SampleBankingApp/Services/EmailService.cs | 52 | Email sending may fail after DB write committed (side effect after persistence) | Use outbox pattern or handle failures asynchronously |
| SampleBankingApp/Services/UserService.cs | 63 | `SearchUsers` swallows exceptions silently | Log and rethrow or return error indicator |
| SampleBankingApp/Controllers/UserController.cs | 52 | `ex.Message` returned directly to client | Return generic error message; log details |

## Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 20 | `GetOpenConnection()` returns undisposed `SqlConnection` | Return `IDisposable` and document caller responsibility; prefer `using` |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | `ExecuteQuery` uses `GetOpenConnection()` without disposal | Use `using` for connection/command/adapter |
| SampleBankingApp/Services/AuthService.cs | 36 | `SqlConnection`, `SqlCommand`, `SqlDataReader` opened but never disposed | Wrap in `using` statements |
| SampleBankingApp/Services/EmailService.cs | 26 | `_smtpClient` held as instance field (not thread-safe, socket leak risk) | Use `using` for each send operation or inject `SmtpClient` per request |
| SampleBankingApp/Services/EmailService.cs | 42, 62, 72 | `MailMessage` created but never disposed | Wrap in `using` statement |
| SampleBankingApp/Services/UserService.cs | 39, 51, 63, 79 | `DataTable` returned from `_db.ExecuteQuerySafe` not disposed | Ensure caller disposes; prefer `using` in helper |

## Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/TransactionController.cs | 25 | `userIdClaim!` used without null check | Validate claim exists before parsing |
| SampleBankingApp/Controllers/TransactionController.cs | 39 | Same issue with `userIdClaim!` | Validate claim exists before parsing |
| SampleBankingApp/Services/AuthService.cs | 34 | `_config.GetConnectionString("DefaultConnection")` used without null check | Guard against null; throw meaningful exception |
| SampleBankingApp/Services/AuthService.cs | 72 | `jwtSecret!` used without null check | Validate config value exists |
| SampleBankingApp/Services/EmailService.cs | 29 | `_config["Email:SmtpHost"]` passed to `SmtpClient` without null check | Add null check |
| SampleBankingApp/Services/EmailService.cs | 31 | `_config["Email:Username"]`, `_config["Email:Password"]` used without null check | Add null checks |
| SampleBankingApp/Services/UserService.cs | 39 | `table.Rows[0]` accessed without `Rows.Count > 0` check | Guard with `if (table.Rows.Count == 0)` |
| SampleBankingApp/Services/UserService.cs | 63 | `_db.ExecuteQuery` returns `DataTable` with no null check on `Rows` | Guard before accessing rows |
| SampleBankingApp/Services/TransactionService.cs | 32 | `fromUserTable.Rows[0]` accessed without `Rows.Count > 0` check | Guard before accessing rows |
| SampleBankingApp/Services/TransactionService.cs | 35 | Same for `toUserTable.Rows[0]` | Guard before accessing rows |
| SampleBankingApp/Services/TransactionService.cs | 47 | `(string)fromUserTable.Rows[0]["Email"]` cast without null check | Guard against null |
| SampleBankingApp/Services/TransactionService.cs | 48 | `(string)toUserTable.Rows[0]["Username"]` cast without null check | Guard against null |

## Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 25 | `AdminBypassPassword` constant unused in production (security risk) | Remove or secure via config |
| SampleBankingApp/Services/AuthService.cs | 81 | `HashPasswordSha1` method defined but never called | Remove or use if intended |
| SampleBankingApp/Services/AuthService.cs | 89 | `ValidateToken` has unreachable code after `return true` | Remove dead code |
| SampleBankingApp/Helpers/StringHelper.cs | 40 | `JoinWithSeparator` is O(n²) and unused; `JoinWithSeparatorFixed` exists | Remove `JoinWithSeparator` |
| SampleBankingApp/Services/TransactionService.cs | 103 | `RefundTransaction` throws `NotImplementedException` | Remove or implement |
| SampleBankingApp/Services/UserService.cs | 103 | `_auditLog` and `_requestCount` static fields never read | Remove or use |

## Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded fallback password `Admin1234!` | Remove; use config only |
| SampleBankingApp/Services/AuthService.cs | 25 | Hardcoded admin password `SuperAdmin2024` | Move to config or remove |
| SampleBankingApp/Services/TransactionService.cs | 13 | `TransactionFeeRate = 0.015m` should be configurable | Move to config |
| SampleBankingApp/Services/TransactionService.cs | 14 | `MaxTransactionsPerDay = 10` should be configurable | Move to config |
| SampleBankingApp/Services/TransactionService.cs | 64 | `0.05m` interest bonus rate hardcoded | Move to config |
| SampleBankingApp/Services/UserService.cs | 24 | `pageSize > 50` limit hardcoded | Move to config |
| SampleBankingApp/Services/UserService.cs | 17, 29, 42 | `id > 1000000` limit hardcoded | Move to config or remove |
| SampleBankingApp/Services/EmailService.cs | 15, 16 | Email subjects hardcoded | Move to config |
| SampleBankingApp/Services/EmailService.cs | 22 | `SmtpTimeoutMs = 5000` hardcoded | Move to config |
| SampleBankingApp/Services/EmailService.cs | 23 | `MaxRetries = 3` hardcoded | Move to config |
| SampleBankingApp/Helpers/StringHelper.cs | 10 | `254` max email length hardcoded | Define constant |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | Username length limits `3`, `20` hardcoded | Define constants |
| SampleBankingApp/Services/UserService.cs | 103 | `_auditLog` entries include raw values (security risk) | Sanitize or remove sensitive data |

## Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 32 | `result += item + separator` in loop (O(n²)) | Use `string.Join` (already have `JoinWithSeparatorFixed`) |
| SampleBankingApp/Helpers/StringHelper.cs | 12 | `new Regex(...)` created per call | Make `static readonly` |
| SampleBankingApp/Services/UserService.cs | 103 | Static `_auditLog` and `_requestCount` accessed without synchronization | Use `ConcurrentBag` or remove static state |
| SampleBankingApp/Services/UserService.cs | 63 | `ExecuteQuery` leaks SQL injection risk | Replace with parameterized query |
| SampleBankingApp/Services/UserService.cs | 103 | `GetAuditReport` concatenates strings inefficiently | Use `StringBuilder` or `string.Join` |
| SampleBankingApp/Services/TransactionService.cs | 45 | `RecordTransaction` uses string interpolation for SQL | Use parameterized query |
| SampleBankingApp/Services/UserService.cs | 51 | `UpdateUser` and `DeleteUser` lack ownership verification | Check `userIdClaim` matches `id` |
| SampleBankingApp/Services/UserService.cs | 79 | `GetUsersPage` pagination uses unsafe `ExecuteQuerySafe` but offset calculation is wrong | Fix offset and ensure parameterization |
| SampleBankingApp/Services/TransactionService.cs | 45 | Email sent after DB write without transaction | Use outbox pattern |

## Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Program.cs | 30 | `UseDeveloperExceptionPage()` called unconditionally | Wrap in `if (app.Environment.IsDevelopment())` |
| SampleBankingApp/Program.cs | 34 | HTTPS redirection commented out | Uncomment and enable in production |
| SampleBankingApp/Program.cs | 36 | Overly permissive CORS | Restrict origins/methods |
| SampleBankingApp/appsettings.json | 3 | Production connection string with plaintext password | Use user secrets/vault |
| SampleBankingApp/appsettings.json | 7 | Weak JWT secret key | Use strong random key |
| SampleBankingApp/appsettings.json | 15 | SMTP password in plaintext | Use user secrets/vault |
| SampleBankingApp/appsettings.json | 20-22 | Logging level set to `Debug` for all | Set to `Information` or higher in production |
| SampleBankingApp/SampleBankingApp.csproj | 10 | `<DebugSymbols>true</DebugSymbols>` and `<DebugType>full</DebugType>` | Set to `false`/`portable` for release builds |
| SampleBankingApp/SampleBankingApp.csproj | 9 | `<TreatWarningsAsErrors>false</TreatWarningsAsErrors>` | Set to `true` for CI builds |

## Missing Unit Tests

No issues found.

**Test Project Status:** No test project exists in the provided source files.

**Critical Scenarios to Test:**
- `AuthService.Login`: SQL injection resistance, MD5 replacement, admin bypass removal, JWT token generation with correct claims
- `TransactionService.Transfer`: Balance validation (including fee), self-transfer prevention, transaction atomicity, pagination boundary
- `TransactionService.Deposit`: Amount validation (positive, max cap), interest calculation correctness
- `UserService.GetUsersPage`: Pagination offset calculation (`(page-1)*pageSize`), max page size enforcement
- `UserController.UpdateUser/DeleteUser`: Ownership verification (ensure user can only modify own account)
- `StringHelper.IsValidEmail/Username`: Boundary conditions (length limits, special characters)
- `EmailService`: SSL enabled, credential null handling, retry logic
- JWT validation: `ValidateLifetime = true`, secret key strength, issuer/audience validation