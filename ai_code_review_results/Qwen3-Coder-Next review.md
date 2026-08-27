## Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded fallback connection string with plaintext password `Admin1234!` | Remove hardcoded fallback; throw if config value missing |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | SQL injection via string interpolation in `ExecuteQuery(tableName, whereClause)` | Use parameterized queries or whitelist table/column names |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection in login query using interpolated username and hashed password | Use parameterized query with `@Username` and `@Password` parameters |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password `SuperAdmin2024` | Remove backdoor; use proper role-based access control |
| SampleBankingApp/Services/AuthService.cs | 63 | Weak MD5 hashing for passwords | Replace with bcrypt, PBKDF2, or Argon2 |
| SampleBankingApp/Program.cs | 24 | JWT `ValidateLifetime = false` allows expired tokens | Set `ValidateLifetime = true` |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` called unconditionally in production | Wrap in `app.Environment.IsDevelopment()` check |
| SampleBankingApp/Program.cs | 38 | Overly permissive CORS policy (`AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`) | Restrict to known origins and methods |
| SampleBankingApp/Services/AuthService.cs | 28 | No rate limiting or account lockout on login attempts | Implement rate limiting (e.g., IP/user-based throttling) |
| SampleBankingApp/Services/AuthService.cs | 53 | Bypass password allows admin access without DB lookup | Remove bypass logic entirely |
| SampleBankingApp/appsettings.json | 3 | Production connection string with plaintext password `Admin1234!` | Use environment variables or managed identity; never commit secrets |
| SampleBankingApp/appsettings.json | 6 | Weak JWT secret key `"mysecretkey"` | Use a cryptographically secure random key (≥256 bits) |
| SampleBankingApp/appsettings.json | 14 | SMTP password `EmailPass99` committed in plaintext | Move to environment variable or Azure Key Vault |
| SampleBankingApp/Services/EmailService.cs | 29 | `EnableSsl = false` for SMTP connection | Set `EnableSsl = true` and use port 587 or 465 |

## Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/UserService.cs | 72 | Pagination offset calculation uses `page * pageSize` instead of `(page - 1) * pageSize` | Change to `int skip = (page - 1) * pageSize;` |
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check uses `fromBalance >= amount` but deducts `amount + fee`, allowing negative balance | Check `fromBalance >= totalDebit` before proceeding |
| SampleBankingApp/Services/TransactionService.cs | 36-37 | No null guard for `Rows[0]` when user not found (should return error) | Check `table.Rows.Count == 0` and return failure |
| SampleBankingApp/Services/TransactionService.cs | 47-48 | SQL injection in UPDATE statements via interpolated values | Use parameterized queries with `@Balance`, `@UserId` |
| SampleBankingApp/Services/TransactionService.cs | 90 | SQL injection in `RecordTransaction` via string interpolation | Use parameterized INSERT query |
| SampleBankingApp/Services/UserService.cs | 47,61 | SQL injection in UPDATE/DELETE queries via string interpolation | Use parameterized queries with `@Email`, `@Username`, `@Id` |
| SampleBankingApp/Services/UserService.cs | 99 | SQL injection in `SearchUsers` via interpolated query in `ExecuteQuery` | Use parameterized LIKE clause (`Username LIKE @Query`) |
| SampleBankingApp/Services/AuthService.cs | 32 | No check for self-transfer (fromUserId == toUserId) | Add guard clause returning `"Cannot transfer to yourself"` |
| SampleBankingApp/Services/TransactionService.cs | 68 | Hardcoded interest bonus calculation `amount * 0.05m * 1` — unclear meaning of `* 1` | Remove redundant `* 1`; document rate and period; consider extracting constant |

## Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/UserService.cs | 105-108 | Catches broad `Exception` and returns empty list — callers cannot distinguish error from no results | Log exception; rethrow or return null with explicit error indicator |
| SampleBankingApp/Controllers/UserController.cs | 52 | Returns raw `ex.Message` to client (potential info leak) | Return generic message; log full details server-side |
| SampleBankingApp/Services/AuthService.cs | 103-108 | `ValidateToken` returns `true` unconditionally due to unreachable code after early `return true` | Remove early return; implement actual validation |
| SampleBankingApp/Services/EmailService.cs | 75-78 | Catches `Exception` silently in `SendWelcomeEmail` — swallows errors | Log exception; consider throwing or returning status |
| SampleBankingApp/Controllers/TransactionController.cs | 27,41 | No null check on `userIdClaim!` before `int.Parse` — throws if claim missing | Add null check and return `Unauthorized()` |
| SampleBankingApp/Services/UserService.cs | 36,83 | No null guard for `table.Rows[0]` when no rows returned | Check `Rows.Count > 0` before indexing |
| SampleBankingApp/Services/TransactionService.cs | 36-37 | No null guard for `Rows[0]["Balance"]` — throws if user not found | Validate row count first |
| SampleBankingApp/Services/UserService.cs | 115-122 | No null guard for `row["Role"]`, `row["CreatedAt"]` — may be DBNull | Use safe casting with `row.Field<T>()` or check `DBNull.Value` |

## Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection()` returns undisposed `SqlConnection` — caller must dispose | Return `IDisposable` and document ownership transfer; or use `using` internally |
| SampleBankingApp/Data/DatabaseHelper.cs | 28-34 | `ExecuteQuery(tableName, whereClause)` opens connection but never disposes `SqlDataReader`, `SqlCommand`, or `SqlDataAdapter` | Wrap in `using` blocks |
| SampleBankingApp/Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` opens connection but does not dispose `SqlCommand` or close connection on exception | Use `using` for command/connection; wrap in try/finally |
| SampleBankingApp/Services/AuthService.cs | 34-38 | Opens `SqlConnection` and `SqlCommand` without disposal; `SqlDataReader` not disposed | Use `using` blocks for all disposable resources |
| SampleBankingApp/Services/EmailService.cs | 16 | `_smtpClient` held as instance field — not thread-safe; sockets may leak on disposal | Make static readonly or ensure proper disposal via `IDisposable` implementation |
| SampleBankingApp/Services/EmailService.cs | 39-43,69,89 | `MailMessage` created without `using` — not disposed after send | Wrap in `using` block |
| SampleBankingApp/Data/DatabaseHelper.cs | 26-48 | `ExecuteQuerySafe` returns `DataTable` but does not dispose underlying `SqlDataReader` (via `SqlDataAdapter.Fill`) — safe for now, but risky pattern | Document that caller must dispose if reusing connection; consider returning `List<T>` instead |

## Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Program.cs | 28 | `jwtSecret!` used without null check — throws if config key missing | Add null check and throw descriptive exception |
| SampleBankingApp/Services/AuthService.cs | 70 | `_config["Jwt:SecretKey"]!` used without null check | Guard with null-coalescing or throw |
| SampleBankingApp/Services/EmailService.cs | 22,24-28 | `_config["Email:..."]` values passed directly to `SmtpClient`, `NetworkCredential` — may be null | Validate all config keys exist; use fallbacks or throw |
| SampleBankingApp/Services/UserService.cs | 115-122 | `row["Role"]`, `row["CreatedAt"]` cast without null/DBNull check | Use `row.Field<T>()` or check `row.IsNull()` |
| SampleBankingApp/Controllers/TransactionController.cs | 27,41 | `userIdClaim!` dereferenced before null check — throws if claim missing | Add null check: `if (userIdClaim is null) return Unauthorized();` |
| SampleBankingApp/Services/UserService.cs | 36,83 | `table.Rows[0]` accessed without checking `Rows.Count > 0` | Guard with `if (table.Rows.Count == 0)` |
| SampleBankingApp/Services/TransactionService.cs | 36-37 | `fromUserTable.Rows[0]["Balance"]` — no check for empty table | Validate row count before indexing |
| SampleBankingApp/Services/UserService.cs | 101 | `table.Rows` iterated without checking `Rows.Count > 0` | Safe in foreach, but add guard if using indexers elsewhere |

## Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 91-96 | `HashPasswordSha1` method defined but never called | Remove or use for migration (document purpose) |
| SampleBankingApp/Services/AuthService.cs | 98-108 | `ValidateToken` method has unreachable code after early `return true` | Fix logic or remove |
| SampleBankingApp/Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` duplicates `string.Join` functionality and is unused | Remove; use `string.Join` directly |
| SampleBankingApp/Services/EmailService.cs | 81-84 | `BuildHtmlTemplate` method defined but only called by `SendWelcomeEmailHtml` — could be inlined or made private static | Consider inlining if simple, or keep if reused (currently only once) |
| SampleBankingApp/Services/UserService.cs | 94-97 | `FormatCurrency` method defined but never used | Remove |
| SampleBankingApp/Services/UserService.cs | 123 | `MapRowToUser` method defined but never called — actually used in lines 35,80,102 | Not dead code — included for completeness |

## Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded fallback password `Admin1234!` | Move to config or throw |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password `SuperAdmin2024` | Remove entirely |
| SampleBankingApp/Services/TransactionService.cs | 11-12 | `TransactionFeeRate = 0.015m`, `MaxTransactionsPerDay = 10` — should be configurable | Move to `appsettings.json` |
| SampleBankingApp/Services/TransactionService.cs | 68 | Hardcoded interest rate `0.05m` and multiplier `* 1` | Extract constants: `InterestRate = 0.05m`, `Period = 1` |
| SampleBankingApp/Services/UserService.cs | 70 | Hardcoded `pageSize > 50` limit | Extract to constant or config |
| SampleBankingApp/Services/UserService.cs | 22,42,56 | Hardcoded `id > 1000000` range check | Extract to constant `MaxUserId = 1_000_000` |
| SampleBankingApp/Helpers/StringHelper.cs | 13,22 | Email max length `254`, username length limits `3-20` | Extract to constants (`MaxEmailLength`, `MinUsernameLength`, `MaxUsernameLength`) |
| SampleBankingApp/Services/EmailService.cs | 13-14 | `MaxRetries = 3`, `SmtpTimeoutMs = 5000` — should be configurable | Move to config |
| SampleBankingApp/appsettings.json | 12 | SMTP port `25` (insecure) | Use `587` or `465`; move to config |
| SampleBankingApp/Services/UserService.cs | 90 | Hardcoded SQL `GETDATE()` — platform-specific | Use `DateTime.UtcNow` in code and parameterize |

## Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 31-35 | `JoinWithSeparator` uses string concatenation in loop (O(n²)) | Replace with `string.Join` (already exists as `JoinWithSeparatorFixed`) |
| SampleBankingApp/Helpers/StringHelper.cs | 16,25 | `new Regex(...)` created on every call — should be `static readonly` | Make `static readonly Regex` fields |
| SampleBankingApp/Services/UserService.cs | 10-11 | Static mutable `_auditLog` and `_requestCount` — not thread-safe | Use `ConcurrentBag<string>` or lock; or remove static state |
| SampleBankingApp/Services/UserService.cs | 87-92 | `GetAuditReport` uses string concatenation in loop (O(n²)) | Use `StringBuilder` or `string.Join("\n", _auditLog)` |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL query built via interpolation — violates separation of concerns | Use parameterized queries; extract to repository pattern |
| SampleBankingApp/Services/UserService.cs | 47,61,99 | SQL queries built via interpolation — violates separation of concerns | Use parameterized queries; extract to repository pattern |
| SampleBankingApp/Services/TransactionService.cs | 47-48,90 | SQL queries built via interpolation — violates separation of concerns | Use parameterized queries; extract to repository pattern |
| SampleBankingApp/Services/UserService.cs | 105-108 | Catches `Exception` and returns empty list — masks errors | Log and rethrow or return error status |
| SampleBankingApp/Controllers/UserController.cs | 52 | Returns raw exception message to client | Return generic error; log details |
| SampleBankingApp/Services/AuthService.cs | 103-108 | `ValidateToken` has unreachable code — likely copy-paste error | Fix logic or remove |

## Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` called unconditionally | Wrap in `if (app.Environment.IsDevelopment())` |
| SampleBankingApp/Program.cs | 24 | JWT `ValidateLifetime = false` | Set to `true` |
| SampleBankingApp/Program.cs | 38 | Overly permissive CORS policy | Restrict origins/methods |
| SampleBankingApp/appsettings.json | 17-21 | Log level set to `Debug` for all namespaces — excessive in production | Use `Information` or `Warning` for production |
| SampleBankingApp/SampleBankingApp.csproj | 8-9 | `<DebugSymbols>true</DebugSymbols>` and `<DebugType>full</DebugType>` — should be conditional on build config | Remove or wrap in `Condition="'$(Configuration)' == 'Debug'"` |
| SampleBankingApp/appsettings.json | 3 | Production connection string with embedded password | Use environment variables or managed identity |
| SampleBankingApp/appsettings.json | 6 | Weak JWT secret key `"mysecretkey"` | Use cryptographically secure random key |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out | Uncomment and enable in production |

## Missing Unit Tests

| File | Line | Issue | Fix |
|------|------|-------|-----|
| N/A | N/A | No test project exists (no `*.Test.csproj` or `xunit` references found) | Create test project; add tests for: |
|  |  |  | - `AuthService.Login`: valid/invalid credentials, bypass password removal, MD5 deprecation |
|  |  |  | - `TransactionService.Transfer`: insufficient funds, self-transfer, fee calculation, SQL injection prevention |
|  |  |  | - `UserService.GetUsersPage`: pagination boundary (`page=0`, `pageSize=0`, `pageSize>50`) |
|  |  |  | - `UserController` endpoints: authorization checks, null user claims, error handling |
|  |  |  | - `StringHelper.IsValidEmail/Username`: edge cases (empty, null, max length) |
|  |  |  | - `DatabaseHelper` methods: parameterized query safety, resource disposal |

---