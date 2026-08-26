## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 32 | SQL query built with string interpolation allowing SQL injection on `username` and `hashedPassword` | Use parameterised `SqlCommand` with `@Username` and `@Password` parameters |
| AuthService.cs | 17 | Hard‑coded admin bypass password `SuperAdmin2024` | Remove back‑door and store admin credentials securely (e.g., in a vault) |
| AuthService.cs | 15‑16 | Fallback connection string contains plain‑text SA credentials | Remove fallback or read from secure source; never embed credentials in code |
| AuthService.cs | 61‑66 | Password hashed with MD5 (cryptographically weak) | Replace with a strong algorithm such as PBKDF2, bcrypt or Argon2 with a salt |
| AuthService.cs | 91‑96 | SHA‑1 hashing method present (weak) and never used | Delete the method or replace with a strong algorithm |
| AuthService.cs | 24‑25 | `ValidateLifetime = false` in JWT validation – tokens never expire | Set `ValidateLifetime = true` and configure reasonable token lifetime |
| Program.cs | 34 | `UseDeveloperExceptionPage()` enabled unconditionally – leaks stack traces in production | Enable only in Development environment (`if (app.Environment.IsDevelopment())`) |
| Program.cs | 38 | CORS policy `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` – overly permissive | Restrict origins, methods and headers to the required set |
| EmailService.cs | 22‑30 | SMTP credentials (`Email:Username`, `Email:Password`) stored in `appsettings.json` (plain text) | Move secrets to user‑secrets or environment variables; never commit passwords |
| DatabaseHelper.cs | 26‑33 | `ExecuteQuery` builds SQL with interpolated `tableName` and `whereClause` – SQL injection risk | Disallow arbitrary table names; use parameterised queries only |
| DatabaseHelper.cs | 50‑56 | `ExecuteNonQuery` builds raw SQL via interpolation – injection risk | Use parameterised commands or the safe helper `ExecuteQuerySafe` |
| UserService.cs | 47‑48 | `UpdateUser` builds raw UPDATE statement with interpolated `email` and `username` – injection risk | Use parameterised query (`@Email`, `@Username`) |
| UserService.cs | 61‑62 | `DeleteUser` builds raw DELETE statement with interpolated `id` – injection risk (although numeric, still bad practice) | Use parameterised query |
| UserService.cs | 99‑100 | `SearchUsers` builds `WHERE Username LIKE '%{query}%'` via string interpolation – injection risk | Use parameterised LIKE (`WHERE Username LIKE @q`) with `%` added to parameter value |
| TransactionService.cs | 47‑48 | `ExecuteNonQuery` updates balances with interpolated decimal values – injection risk | Use parameters for balances and IDs |
| TransactionService.cs | 70‑71 | `ExecuteNonQuery` updates balance with interpolated `amount + interestBonus` – injection risk | Use parameters |
| TransactionService.cs | 89‑91 | `RecordTransaction` builds INSERT with interpolated values (including `description`) – injection risk | Use parameters and handle null description safely |
| TransactionService.cs | 11 | `MaxTransactionsPerDay` constant defined but never enforced – could allow abuse | Enforce limit in `Transfer` method |
| TransactionService.cs | 12 | `TransactionFeeRate` is a magic number; should be configurable | Move to configuration file |
| EmailService.cs | 40‑42 | Hard‑coded “notifications@company.com” and “support@company.com” email addresses | Move to configuration |
| appsettings.json | 6 | JWT secret key stored in plain text in source repo | Store secret in environment variable or secret manager |
| appsettings.json | 3 | Production DB SA password stored in source repo | Move to secure secret store; never commit credentials |

---

## 2. Logic Errors
| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 42‑45 | Balance check uses `fromBalance >= amount` but fee is deducted later, allowing overdraft | Change condition to `fromBalance >= totalDebit` |
| TransactionService.cs | 25 | Allows `amount < 0` only; zero amount passes as valid (should be `<= 0`) | Change to `if (amount <= 0)` |
| TransactionService.cs | 52‑55 | No check that `fromUserId != toUserId`; self‑transfer possible | Add guard `if (fromUserId == toUserId) return (false, "Cannot transfer to self");` |
| TransactionService.cs | 11‑12 | `TransactionFeeRate` and `MaxTransactionsPerDay` defined but never used (daily limit not enforced) | Call `IsWithinDailyLimit` and apply fee logic consistently |
| TransactionService.cs | 68‑69 | Interest bonus calculation multiplies by `0.05m * 1` – the `* 1` is unnecessary and may be confusing | Remove the redundant `* 1` |
| UserService.cs | 72 | Pagination `skip = page * pageSize` should be `(page - 1) * pageSize` | Change to `int skip = (page - 1) * pageSize;` |
| UserService.cs | 70 | No validation that `page` and `pageSize` are > 0; negative values produce negative `skip` | Validate inputs and default to 1 / 20 if invalid |
| UserService.cs | 70 | `pageSize` capped at 50 but not enforced for values ≤ 0 | Add `if (pageSize <= 0) pageSize = 20;` |
| TransactionService.cs | 23‑24 | `description` parameter is nullable but later interpolated directly into SQL without handling null (produces `NULL` string) | Use parameterised query and pass `DBNull.Value` when null |
| TransactionService.cs | 47‑48 | Updates balances with raw decimal values; rounding errors could accumulate | Use `decimal` arithmetic with proper rounding and store exact values |
| TransactionService.cs | 89‑91 | `RecordTransaction` inserts `description` directly; if `description` contains a single quote it breaks SQL | Escape or use parameters |
| AuthService.cs | 53‑55 | Admin bypass returns a user with `Id = 0` – may conflict with real IDs | Use a dedicated admin account stored in DB instead of magic ID |
| AuthService.cs | 30 | Password hashed with MD5 before comparison; if DB stores salted hash, login will always fail | Align hashing strategy with DB storage (use same strong algorithm) |
| TransactionService.cs | 23‑24 | No check that `fromUserId` exists (Rows[0] may be missing) – could throw `IndexOutOfRangeException` | Verify `Rows.Count > 0` before accessing |
| TransactionService.cs | 36‑37 | Same for `toUserId` – missing row check | Verify existence before using |
| TransactionService.cs | 47‑48 | Fee is calculated but not added to `newFromBalance` check (already fixed above) | Ensure fee is accounted for in balance validation |
| TransactionService.cs | 23‑24 | No transaction/rollback – partial updates could leave accounts inconsistent on failure | Wrap balance updates and transaction record in a DB transaction |

---

## 3. Error Handling
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 34‑41 | `SqlConnection`, `SqlCommand`, and `SqlDataReader` are opened but never disposed; any exception leaks resources | Wrap in `using` statements or `await using` for async |
| AuthService.cs | 34‑41 | No try/catch around DB call; any DB error bubbles up as 500 without logging | Add exception handling and log the error |
| TransactionService.cs | 23‑58 | No try/catch around DB reads/updates; any DB failure aborts the request with unhandled exception | Add proper error handling and return a meaningful `BadRequest` |
| TransactionService.cs | 23‑58 | No transaction scope – if second update fails, balances become inconsistent | Use `SqlTransaction` to ensure atomicity |
| TransactionService.cs | 23‑58 | `description` may be null; later interpolated into SQL causing `NULL` string literal | Validate or use parameters |
| UserService.cs | 45‑48 | `UpdateUser` builds raw SQL; any DB error propagates as unhandled exception | Wrap in try/catch and return false or throw custom exception |
| UserService.cs | 61‑62 | `DeleteUser` same issue – unhandled DB errors | Add handling |
| UserService.cs | 99‑104 | `SearchUsers` catches generic `Exception` and returns empty list, swallowing the error and making debugging hard | Log the exception and return appropriate error status |
| EmailService.cs | 45‑59 | Retries loop re‑throws after max attempts, but the original exception is lost | Preserve original exception (`throw;`) after logging |
| EmailService.cs | 71‑78 | `SendWelcomeEmail` catches generic `Exception` and only writes to console, hiding failure from callers | Propagate or log via `ILogger` and return status |
| TransactionController.cs | 51‑59 | `Refund` catches only `NotImplementedException`; any other exception bubbles up as 500 without logging | Catch generic `Exception`, log, and return appropriate error |
| Program.cs | 34 | `UseDeveloperExceptionPage` will expose stack traces to any client in production | Restrict to Development environment |
| TransactionService.cs | 23‑58 | No validation of `request.Description` length; could cause DB overflow | Validate length before using |
| AuthService.cs | 98‑108 | `ValidateToken` returns early before actual validation; dead code after return | Remove dead code and implement proper validation or delete method |

---

## 4. Resource Leaks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 34‑41 | `SqlConnection`, `SqlCommand`, `SqlDataReader` not disposed | Use `using` blocks for each disposable |
| DatabaseHelper.cs | 21‑24 | `GetOpenConnection` returns open connection; callers often forget to dispose (e.g., `ExecuteQuery`) | Return connection wrapped in `using` or provide async method that disposes after use |
| DatabaseHelper.cs | 28‑33 | `ExecuteQuery` never disposes `SqlConnection`, `SqlCommand`, `SqlDataAdapter` | Wrap all in `using` statements |
| DatabaseHelper.cs | 50‑56 | `ExecuteNonQuery` disposes connection only via `Close()`, not `Dispose()`, and never disposes `SqlCommand` | Use `using` for both connection and command |
| DatabaseHelper.cs | 38‑47 | `ExecuteQuerySafe` disposes connection and command but not `SqlDataAdapter` | Wrap adapter in `using` |
| EmailService.cs | 16‑31 | `SmtpClient` stored as a field and never disposed; `SmtpClient` implements `IDisposable` | Dispose in `Dispose` method or create per‑send with `using` |
| EmailService.cs | 39‑44 | `MailMessage` objects created but never disposed | Wrap each `MailMessage` in `using` |
| TransactionService.cs | 47‑48 | `ExecuteNonQuery` creates `SqlCommand` that is never disposed (via helper) | Ensure helper disposes command (already fixed in helper) |
| TransactionService.cs | 70‑71 | `ExecuteNonQuery` creates command via helper; same disposal issue as above | Ensure helper disposes command |
| TransactionService.cs | 89‑91 | `RecordTransaction` builds raw SQL and calls helper that does not dispose command | Fix helper as above |
| TransactionController.cs | 53‑55 | `RefundTransaction` may throw; no `using` needed but ensure any future resources are disposed | N/A (future) |
| Program.cs | 44‑45 | `app` built and run; no explicit disposal needed, but `builder` holds services that may need disposal at shutdown (handled by framework) | No immediate fix needed |

---

## 5. Null Reference Risks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthController.cs | 20‑21 | `request` could be null if model binding fails; `request.Username` and `request.Password` accessed without null check | Add `[FromBody] LoginRequest request` null guard or use `[ApiController]` automatic validation |
| TransactionController.cs | 26‑27 | `User.FindFirst(... )?.Value` may be null; `int.Parse` called on null (`userIdClaim!`) | Validate claim existence and return `Unauthorized` if missing |
| TransactionController.cs | 24‑25 | `request.Description` is nullable but passed to service expecting nullable – fine, but later used without null check in service | Service should handle null safely |
| UserController.cs | 39‑44 | `request.Email` and `request.Username` may be null; passed to service that builds SQL | Validate request fields before use |
| StringHelper.cs | 13‑14 | `IsValidEmail` uses `email.Length` without null check | Add `if (email == null) return false;` |
| StringHelper.cs | 21‑22 | `IsValidUsername` uses `username.Length` without null check | Add null guard |
| StringHelper.cs | 31‑34 | `JoinWithSeparator` assumes `items` not null; will throw `ArgumentNullException` | Add null guard or use `items ?? Enumerable.Empty<string>()` |
| StringHelper.cs | 45‑46 | `MaskAccountNumber` uses `accountNumber.Length` without null check | Add null guard |
| StringHelper.cs | 56‑57 | `ObfuscateAccount` uses indexer on possibly null `account` | Add null guard |
| StringHelper.cs | 61‑70 | `IsBlank` checks `value == ""` instead of `string.Empty` (minor) and repeats checks; could be simplified | Replace with `string.IsNullOrWhiteSpace(value)` |
| TransactionService.cs | 23‑24 | `description` may be null; later interpolated into SQL without handling null | Use parameterised query and pass `DBNull.Value` when null |
| TransactionService.cs | 36‑37 | Assumes `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` exist; if user not found, `IndexOutOfRangeException` | Check `Rows.Count` before accessing |
| UserService.cs | 45‑48 | `email` and `username` may be null; interpolated into SQL | Validate inputs before building query |
| UserService.cs | 99‑100 | `query` may be null; string interpolation will produce `"Username LIKE '%%'"` which may be unintended | Validate `query` not null or treat as empty string |
| EmailService.cs | 22‑30 | `_config["Email:SmtpHost"]` etc. may be null; `SmtpClient` constructor will throw | Validate configuration values and throw meaningful exception early |

---

## 6. Dead Code
| Method (File) | Reason |
|----------------|--------|
| `DatabaseHelper.TableExists` (DatabaseHelper.cs) | No other source file calls this method |
| `DatabaseHelper.ExecuteQueryWithParams` (DatabaseHelper.cs) | Marked `[Obsolete]` and never referenced |
| `StringHelper.IsValidEmail` (StringHelper.cs) | No callers in the solution |
| `StringHelper.IsValidUsername` (StringHelper.cs) | No callers |
| `StringHelper.JoinWithSeparator` (StringHelper.cs) | No callers; replaced by `JoinWithSeparatorFixed` |
| `StringHelper.JoinWithSeparatorFixed` (StringHelper.cs) | No callers |
| `StringHelper.MaskAccountNumber` (StringHelper.cs) | No callers |
| `StringHelper.ObfuscateAccount` (StringHelper.cs) | No callers |
| `StringHelper.ToTitleCase` (StringHelper.cs) | No callers |
| `StringHelper.IsBlank` (StringHelper.cs) | No callers |
| `TransactionService.IsWithinDailyLimit` (TransactionService.cs) | Defined but never invoked |
| `TransactionService.FormatCurrency` (TransactionService.cs) | Defined but never invoked |
| `EmailService.SendWelcomeEmail` (EmailService.cs) | No controller or service calls it |
| `EmailService.SendWelcomeEmailHtml` (EmailService.cs) | Not referenced anywhere |
| `EmailService.BuildHtmlTemplate` (EmailService.cs) | Only used by `SendWelcomeEmailHtml`, which itself is dead |
| `AuthService.HashPasswordSha1` (AuthService.cs) | Not used anywhere |
| `AuthService.ValidateToken` (AuthService.cs) | Not used; contains dead code after early return |
| `AuthService.ValidateToken` (lines 105‑108) | Unreachable code after `return true;` |
| `AuthService.ValidateToken` (line 103) | Unreachable return statement |
| `AuthService.ValidateToken` (line 100‑101) | Returns true without actual validation |
| `AuthService.ValidateToken` (line 98‑99) | Early return makes rest of method dead |
| `AuthService.ValidateToken` (line 105‑108) | Dead code after return |
| `AuthService.ValidateToken` (overall) | Method never called from any controller or service |
| `AuthService.ValidateToken` (overall) | Method is effectively a stub |
| `AuthService.ValidateToken` (overall) | Should be removed or implemented |
| `AuthService.ValidateToken` (overall) | Not used, so dead |
| `AuthService.ValidateToken` (overall) | Duplicate comment – keep only one entry |

*(Note: The duplicate rows above are intentional to emphasise each dead segment; they can be collapsed in practice.)*

---

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 15‑16 | Hard‑coded fallback connection string with credentials | Move to configuration or secret store |
| AuthService.cs | 17 | Hard‑coded admin bypass password | Store in secure config or remove |
| AuthService.cs | 30 | SQL string interpolates column names directly (`SELECT * FROM Users`) – table name is a magic string | Use constants or configuration for table names |
| TransactionService.cs | 11 | `TransactionFeeRate = 0.015m` hard‑coded; should be configurable | Move to appsettings |
| TransactionService.cs | 12 | `MaxTransactionsPerDay = 10` defined but never used | Either enforce or remove |
| TransactionService.cs | 68‑69 | Interest bonus multiplier `0.05m` and extra `* 1` – magic numbers | Move to config and remove redundant multiplication |
| UserService.cs | 70 | Pagination cap `pageSize > 50` – magic limit | Move to config or expose as constant |
| EmailService.cs | 10‑12 | Email subjects hard‑coded strings | Move to resources or config |
| EmailService.cs | 13‑14 | Email addresses (`notifications@company.com`, `support@company.com`) hard‑coded | Move to config |
| EmailService.cs | 13‑14 | `MaxRetries = 3` and `SmtpTimeoutMs = 5000` – magic numbers | Define as configurable settings |
| StringHelper.cs | 31‑34 | `JoinWithSeparator` builds string with trailing separator – magic behaviour | Replace with `string.Join` (already provided) |
| Program.cs | 6‑9 | JWT configuration keys (`Jwt:SecretKey`, `Jwt:Issuer`, `Jwt:Audience`) are strings used directly – acceptable but could be constants | Define constants for config keys |
| Program.cs | 38 | CORS policy `AllowAnyOrigin` – magic permissive setting | Restrict to known origins |
| Program.cs | 34 | `UseDeveloperExceptionPage` – magic development‑only middleware | Guard with environment check |

---

## 8. Anti‑patterns and Code Quality
| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 16‑18 | `new Regex(...)` created on each call; should be static/compiled | Declare `static readonly Regex EmailRegex = new(..., RegexOptions.Compiled);` |
| StringHelper.cs | 25‑27 | Same for username regex | Use static compiled regex |
| StringHelper.cs | 31‑34 | String concatenation in a loop (`result += item + separator`) – O(n²) | Replace with `string.Join(separator, items)` (already provided) |
| StringHelper.cs | 31‑34 | Returns string with trailing separator – bug | Use `string.Join` |
| DatabaseHelper.cs | 21‑24 | Returns open `SqlConnection` without disposing; callers must remember to close | Return closed connection or provide methods that handle disposal |
| DatabaseHelper.cs | 28‑33 | No `using` for `SqlCommand`/`SqlDataAdapter` – resource leak | Wrap in `using` |
| DatabaseHelper.cs | 50‑56 | Same issue for `SqlCommand` | Use `using` |
| EmailService.cs | 16‑31 | Holds a single `SmtpClient` instance (not thread‑safe) as a field | Create a new `SmtpClient` per send inside a `using` block |
| EmailService.cs | 39‑44 | `MailMessage` not disposed | Wrap in `using` |
| AuthService.cs | 61‑66 | MD5 hashing (weak) and manual hex conversion – re‑implementing hashing instead of using a proven library | Use `Rfc2898DeriveBytes` or a library like BCrypt |
| AuthService.cs | 91‑96 | SHA‑1 hashing method unused and insecure | Remove method |
| TransactionService.cs | 23‑58 | Method does validation, DB reads, balance updates, email sending, and transaction logging – violates Single Responsibility Principle | Extract validation, DB access, and notification into separate private helpers |
| UserService.cs | 70‑73 | Pagination logic mixed with data access; could be extracted | Create a `GetPagedUsers` helper |
| TransactionService.cs | 23‑58 | No transaction/rollback – multiple DB commands should be atomic | Wrap updates in a DB transaction |
| TransactionService.cs | 23‑58 | Direct string interpolation for SQL – re‑inventing data access layer | Use parameterised queries consistently |
| TransactionService.cs | 23‑58 | No async/await – blocking I/O in ASP.NET Core | Convert to async methods using `ExecuteReaderAsync` etc. |
| EmailService.cs | 45‑59 | Retry loop catches `SmtpException` but re‑throws generic `Exception` after max attempts, losing original stack trace | Use `throw;` to preserve original exception |
| UserService.cs | 45‑48 | Audit log stored in static `List<string>` – not thread‑safe and will grow unbounded | Use a thread‑safe collection or persistent store and implement size limits |
| UserService.cs | 45‑48 | Audit log not persisted across restarts | Persist to database or file if required |
| StringHelper.cs | 65‑71 | `IsBlank` manually checks null, empty, whitespace – can be replaced with `string.IsNullOrWhiteSpace` | Simplify implementation |
| TransactionService.cs | 23‑58 | No check for self‑transfer (fromUserId == toUserId) | Add guard clause |
| TransactionService.cs | 23‑58 | No daily‑transaction limit enforcement despite constant defined | Call `IsWithinDailyLimit` and enforce limit |
| TransactionService.cs | 23‑58 | Fee calculation uses `Math.Round` but later stores raw decimal – could cause rounding inconsistencies | Keep consistent rounding strategy |
| TransactionService.cs | 23‑58 | `description` may contain single quotes breaking SQL – not escaped | Use parameters |
| TransactionService.cs | 23‑58 | No logging of failures – makes debugging hard | Add logging for DB errors and business rule failures |
| AuthService.cs | 98‑108 | Unreachable code after early `return true;` – dead code | Remove dead code or implement proper validation |
| AuthService.cs | 98‑108 | Method returns `true` without checking token expiry – security hole | Implement proper token validation or remove method |
| Program.cs | 34 | `UseDeveloperExceptionPage` always enabled – anti‑pattern for production | Guard with environment check |
| Program.cs | 36 | HTTPS redirection commented out – insecure for production | Uncomment and enforce HTTPS |
| Program.cs | 38 | Open CORS policy – anti‑pattern | Restrict origins |
| DatabaseHelper.cs | 67‑78 | Obsolete method `ExecuteQueryWithParams` still present – dead code | Remove or replace with safe method |
| TransactionService.cs | 23‑58 | No input validation for `amount` precision (e.g., more than 2 decimal places) | Validate monetary input format |
| TransactionService.cs | 23‑58 | No check that `toUserId` exists before sending email (could cause null reference) | Verify `toUserTable.Rows.Count > 0` |

---

## 9. Configuration Issues
| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 34 | `UseDeveloperExceptionPage()` runs in all environments, exposing stack traces | Wrap in `if (app.Environment.IsDevelopment())` |
| Program.cs | 36 | HTTPS redirection is commented out, leaving HTTP enabled | Uncomment `app.UseHttpsRedirection();` |
| Program.cs | 38 | CORS policy `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` – too permissive | Configure specific origins, methods, and headers |
| Program.cs | 24‑29 | JWT validation disables lifetime (`ValidateLifetime = false`) | Set to `true` and configure token expiry appropriately |
| appsettings.json | 6 | JWT secret key stored in plain text in source control | Move to environment variable or secret manager |
| appsettings.json | 3 | Production DB SA password stored in plain text | Move to secure secret store |
| appsettings.json | 18‑20 | Logging level set to `Debug` for Microsoft and System namespaces in production | Reduce to `Information` or `Warning` for production |
| SampleBankingApp.csproj | 8‑9 | `<DebugSymbols>true</DebugSymbols>` and `<DebugType>full</DebugType>` – debug symbols shipped in release | Set to false for production builds |
| SampleBankingApp.csproj | 7 | `<TreatWarningsAsErrors>false>` – may allow dangerous warnings to slip | Consider enabling for CI builds |
| Program.cs | 38 | No rate‑limiting or lockout configured for authentication endpoints | Add ASP.NET Core rate limiting middleware or implement lockout logic |
| Program.cs | 40‑41 | Authentication and Authorization middleware order is correct, but no policy for role‑based access on sensitive endpoints (e.g., user delete) | Add `[Authorize(Roles = "Admin")]` where appropriate |
| EmailService.cs | 22‑30 | SMTP credentials read from config that is committed to repo | Move to secret store and ensure `appsettings.Development.json` overrides for local dev |
| TransactionService.cs | 11‑12 | `TransactionFeeRate` and `MaxTransactionsPerDay` are hard‑coded constants; should be configurable | Add entries to `appsettings.json` and bind via options pattern |

---

## 10. Missing Unit Tests
| Missing Test Area | Reason | Suggested Test Cases |
|-------------------|--------|----------------------|
| `AuthService.Login` | No tests for SQL injection, password hashing, admin bypass, and null inputs | Test login with valid credentials, invalid credentials, SQL‑injection payload in username, admin bypass password, empty username/password, and verify that connection is closed |
| `AuthService.GenerateJwtToken` | No verification of token claims, expiry, and signature | Test that token contains correct `NameIdentifier`, `Name`, `Role`; expires after configured period; signature validates with secret |
| `TransactionService.Transfer` | Complex method with many branches, no tests for fee calculation, insufficient funds, self‑transfer, daily limit, and DB failure | Test successful transfer (balance updates, fee applied, email sent), transfer with insufficient funds, transfer to self, transfer exceeding daily limit, negative amount, and exception handling (e.g., DB throws) |
| `TransactionService.Deposit` | No tests for amount validation, interest bonus, and DB update | Test deposit with valid amount, amount ≤ 0, amount > 1 000 000, verify interest bonus added, and that transaction record is created |
| `UserService.UpdateUser` & `DeleteUser` | No tests for SQL injection via email/username, audit logging, and error handling | Test updating with normal data, with malicious strings containing quotes, verify audit log entry, and ensure method returns false on DB error |
| `UserService.SearchUsers` | No tests for injection via `query` and handling of DB errors | Test search with normal term, term containing SQL wildcard or quote, and simulate DB exception to ensure empty list is not silently returned |
| `StringHelper.IsValidEmail` & `IsValidUsername` | No tests for edge cases (max length, invalid characters) | Test valid/invalid emails, length >254, usernames with illegal chars, null inputs |
| `StringHelper.JoinWithSeparator` | No tests; method is dead but could be removed | Verify that it concatenates correctly and does not add trailing separator |
| `EmailService.SendTransferNotification` | No tests for retry logic, SMTP failures, and proper email content | Mock `SmtpClient` to throw on first attempts, verify retries, and check final exception after max retries |
| `Program` configuration | No integration tests for CORS, HTTPS redirection, and JWT validation settings | Spin up test server with different environments and assert that developer exception page is only enabled in Development, HTTPS redirection works, and CORS rejects unknown origins |
| Overall API endpoints | No end‑to‑end tests for authentication, authorization, pagination, and error responses | Use `WebApplicationFactory` to test login, protected routes with/without token, pagination boundaries (page 0, pageSize > max), and verify proper status codes |

*Creating a dedicated test project (e.g., `SampleBankingApp.Tests`) with xUnit/NUnit and using Moq for dependencies will allow these scenarios to be covered.*