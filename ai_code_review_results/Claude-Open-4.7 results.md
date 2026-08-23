# SampleBankingApp Peer Review

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| [appsettings.json](SampleBankingApp/appsettings.json#L3) | 3 | Production DB connection string with `sa` account and password `Admin1234!` committed to source control. | Move secrets to user-secrets, environment variables, or a secret manager; never commit prod credentials. |
| [appsettings.json](SampleBankingApp/appsettings.json#L6) | 6 | JWT signing key `"mysecretkey"` is short, low-entropy, and source-controlled — trivially forgeable tokens. | Generate a 256-bit random key and store outside the repo. |
| [appsettings.json](SampleBankingApp/appsettings.json#L14) | 14 | SMTP password `EmailPass99` hardcoded in config. | Read from secret store / env vars. |
| [Program.cs](SampleBankingApp/Program.cs#L24) | 24 | `ValidateLifetime = false` — expired JWTs are accepted indefinitely. | Set `ValidateLifetime = true`. |
| [Program.cs](SampleBankingApp/Program.cs#L34) | 34 | `UseDeveloperExceptionPage()` called unconditionally — leaks stack traces in production. | Gate behind `app.Environment.IsDevelopment()`. |
| [Program.cs](SampleBankingApp/Program.cs#L36) | 36 | `UseHttpsRedirection()` commented out — traffic served over HTTP. | Enable HTTPS redirection. |
| [Program.cs](SampleBankingApp/Program.cs#L38) | 38 | CORS `AllowAnyOrigin + AllowAnyMethod + AllowAnyHeader` — open to any site. | Restrict to known origins and methods. |
| [AuthService.cs](SampleBankingApp/Services/AuthService.cs#L17) | 17 | Hardcoded backdoor `AdminBypassPassword = "SuperAdmin2024"` grants `SuperAdmin` role to anyone who knows it. | Remove the bypass entirely. |
| [AuthService.cs](SampleBankingApp/Services/AuthService.cs#L30) | 30 | Passwords hashed with unsalted MD5 — broken cryptography. | Use PBKDF2/Argon2/bcrypt with per-user salt. |
| [AuthService.cs](SampleBankingApp/Services/AuthService.cs#L32) | 32 | SQL injection via string interpolation of `username`/`hashedPassword` into the login query. | Use parameterized `SqlCommand` with `@Username`. |
| [AuthService.cs](SampleBankingApp/Services/AuthService.cs#L84) | 84 | JWT lifetime of 30 days is excessive for a banking app. | Reduce to minutes and pair with refresh tokens. |
| [AuthService.cs](SampleBankingApp/Services/AuthService.cs#L91) | 91 | `HashPasswordSha1` helper present (SHA1 is broken). | Remove the method. |
| [AuthController.cs](SampleBankingApp/Controllers/AuthController.cs#L19) | 19 | `[HttpPost("login")]` has no rate limiting or account lockout — brute-force friendly. | Add lockout/rate-limit middleware. |
| [AuthController.cs](SampleBankingApp/Controllers/AuthController.cs#L26) | 26 | Error message discloses whether the username exists vs. password incorrect. | Use a generic "Invalid credentials" response. |
| [DatabaseHelper.cs](SampleBankingApp/Data/DatabaseHelper.cs#L16) | 16 | Fallback connection string contains `sa` credentials. | Fail fast on missing connection string. |
| [DatabaseHelper.cs](SampleBankingApp/Data/DatabaseHelper.cs#L29) | 29 | `ExecuteQuery` concatenates `tableName` and `whereClause` directly into SQL — SQL injection. | Remove the method or rebuild on whitelisted identifiers + parameterized predicates. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L47-L48) | 47-48 | Balance UPDATE statements built via string interpolation — SQL injection (and decimal-format/locale risk). | Use parameterized queries. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L70) | 70 | Deposit UPDATE built via string interpolation. | Parameterize. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L89-L91) | 89-91 | `RecordTransaction` interpolates `description` (user-controlled) and other fields into INSERT — SQL injection. | Parameterize all values. |
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L47) | 47 | `UpdateUser` interpolates `email`, `username`, `id` into UPDATE — SQL injection. | Parameterize. |
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L61) | 61 | `DeleteUser` interpolates `id` into DELETE — SQL injection (also low-risk because int, but pattern is unsafe). | Parameterize. |
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L99) | 99 | `SearchUsers` passes raw `query` into a `LIKE '%...%'` clause via `ExecuteQuery` — SQL injection. | Parameterize and escape `%`, `_`, `[`. |
| [UserController.cs](SampleBankingApp/Controllers/UserController.cs#L38) | 38 | `UpdateUser` PUT has no ownership/role check — any authenticated user can edit any account. | Verify caller `id` matches the route or is admin. |
| [UserController.cs](SampleBankingApp/Controllers/UserController.cs#L56) | 56 | `DeleteUser` DELETE has no ownership/role check. | Add `[Authorize(Roles="Admin")]` or ownership verification. |
| [UserController.cs](SampleBankingApp/Controllers/UserController.cs#L78) | 78 | `GetAuditLog` endpoint exposes audit data without any role check. | Restrict to admins. |
| [SampleBankingApp.csproj](SampleBankingApp/SampleBankingApp.csproj#L9) | 8-9 | Debug symbols (`DebugType=full`) shipped — extra reverse-engineering surface in release. | Use `portable` or `embedded` only in Debug. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L29) | 29 | `EnableSsl = false` — SMTP credentials sent in plaintext. | Set `EnableSsl = true` and use port 587. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L25) | 25 | `amount < 0` allows `amount == 0` to proceed as a valid transfer. | Use `amount <= 0`. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L42) | 42 | Balance check uses `fromBalance >= amount` but the debit is `amount + fee` — can drive balance negative by the fee amount. | Check `fromBalance >= totalDebit`. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L23) | 23 | No self-transfer check — user can `fromUserId == toUserId`, paying fees to themselves and losing money. | Reject when ids match. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L68) | 68 | `interestBonus = amount * 0.05m * 1` — applies a 5% "bonus" to every deposit, so users gain 5% free money each call. | Remove the bonus or move interest to a scheduled job at the correct rate. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L77) | 77 | `IsWithinDailyLimit` exists but is never called — daily limit is not enforced. | Call it from `Transfer`/`Deposit`. |
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L72) | 72 | Pagination uses `page * pageSize` — page 1 skips the first page entirely (off-by-one). | Use `(page - 1) * pageSize` and validate `page >= 1`. |
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L70) | 70 | `pageSize` is clamped to 50 but not floored — negative or zero `pageSize` produces malformed SQL. | Clamp to `[1, 50]`. |
| [TransactionController.cs](SampleBankingApp/Controllers/TransactionController.cs#L29) | 29 | Caller can specify any `request.ToUserId` but not validated against existing accounts before debit — relies on row 0 access. | Validate target user exists before debiting. |
| [AuthService.cs](SampleBankingApp/Services/AuthService.cs#L55) | 55 | Backdoor admin user has `Id = 0` — any subsequent DB lookups for `Id = 0` produce broken state. | Remove the backdoor. |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L105-L108) | 105-108 | `SearchUsers` catches `Exception` and returns an empty list — caller cannot distinguish "no results" from "DB failure". | Let exceptions propagate or wrap with typed error. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L42-L57) | 42-57 | Two `UPDATE` statements + `RecordTransaction` are not in a transaction — partial failure leaves the system inconsistent (money debited, credit lost). | Wrap in a `SqlTransaction`/`TransactionScope`. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L52-L55) | 52-55 | `_emailService.SendTransferNotification` runs after the DB writes commit; if SMTP throws (and `MaxRetries` exhausted), the controller returns `BadRequest` even though money already moved. | Move email out of the transactional path (queue / fire-and-forget) and catch failures here. |
| [UserController.cs](SampleBankingApp/Controllers/UserController.cs#L52) | 52 | Returns raw `ex.Message` to HTTP client — leaks internals. | Return generic message and log details. |
| [TransactionController.cs](SampleBankingApp/Controllers/TransactionController.cs#L51-L59) | 51-59 | Refund catches `NotImplementedException` and returns `500` but no logging; any other exception is unhandled. | Log all exceptions; remove dead `NotImplementedException` handling once implemented. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L75-L78) | 75-78 | `SendWelcomeEmail` swallows all exceptions silently via `Console.WriteLine`. | Use `ILogger` and propagate or report through a dead-letter channel. |
| [AuthController.cs](SampleBankingApp/Controllers/AuthController.cs#L19) | 19 | No rate limiting or account lockout — repeated failed logins are unrestricted. | Add ASP.NET rate limiter or Identity lockout. |
| [AuthController.cs](SampleBankingApp/Controllers/AuthController.cs#L20) | 20 | `request` not null-checked; a body of `null` would NRE in `request.Username`. | Validate request and required fields. |
| [TransactionController.cs](SampleBankingApp/Controllers/TransactionController.cs#L27) | 27 | `int.Parse(userIdClaim!)` throws on missing claim — uncaught, becomes 500. | Use `int.TryParse` and return 401/400. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| [DatabaseHelper.cs](SampleBankingApp/Data/DatabaseHelper.cs#L19-L24) | 19-24 | `GetOpenConnection()` returns an open `SqlConnection` with no documented disposal contract; many callers do not dispose. | Replace with `using`-scoped pattern or return `IDisposable` wrapper with clear ownership. |
| [DatabaseHelper.cs](SampleBankingApp/Data/DatabaseHelper.cs#L26-L34) | 26-34 | `ExecuteQuery` opens a connection, `SqlCommand`, and `SqlDataAdapter` but disposes none. | Use `using` for connection, command, and adapter. |
| [DatabaseHelper.cs](SampleBankingApp/Data/DatabaseHelper.cs#L36-L48) | 44-47 | `ExecuteQuerySafe` does not dispose `SqlDataAdapter`. | Wrap adapter in `using`. |
| [DatabaseHelper.cs](SampleBankingApp/Data/DatabaseHelper.cs#L50-L57) | 50-57 | `ExecuteNonQuery` calls `connection.Close()` only on the happy path — any exception leaks the open connection and undisposed command. | Use `using` blocks. |
| [DatabaseHelper.cs](SampleBankingApp/Data/DatabaseHelper.cs#L67-L78) | 67-78 | `ExecuteQueryWithParams` does not dispose `SqlDataAdapter`. | Wrap in `using`. |
| [AuthService.cs](SampleBankingApp/Services/AuthService.cs#L34-L51) | 34-51 | `Login` opens `SqlConnection`, `SqlCommand`, and `SqlDataReader` — none disposed; any throw leaks all three. | Use `using` for connection/command/reader. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L16) | 16 | `SmtpClient` held as instance field — not thread-safe and connection never released; also `EmailService` is `Scoped` so a new client is created per request, fragmenting sockets. | Create `SmtpClient` per send inside a `using`, or register a thread-safe abstraction. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L39) | 39 | `MailMessage` instances are never disposed. | Wrap each `MailMessage` in `using`. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L69) | 69 | Same — `MailMessage` not disposed. | Wrap in `using`. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L89) | 89 | Same — `MailMessage` not disposed. | Wrap in `using`. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| [Program.cs](SampleBankingApp/Program.cs#L28) | 28 | `Encoding.UTF8.GetBytes(jwtSecret!)` will NRE if config key missing; `!` only suppresses warning. | Validate and throw a clear startup exception when `Jwt:SecretKey` is null. |
| [AuthService.cs](SampleBankingApp/Services/AuthService.cs#L70) | 70 | `Encoding.UTF8.GetBytes(_config["Jwt:SecretKey"]!)` — same risk. | Resolve once with explicit null check. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L22) | 22 | `new SmtpClient(_config["Email:SmtpHost"])` — passes possibly-null host to constructor. | Throw if host is missing. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L24) | 24 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` ok; but `Credentials = new NetworkCredential(username, password)` accepts nulls silently and breaks auth. | Validate non-null. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L65) | 65 | `username.ToUpper()` — NRE if `username` is null. | Null-check parameter. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L36-L37) | 36-37 | `fromUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — NRE/`IndexOutOfRangeException` when user id is invalid. | Guard with `Rows.Count == 0` early return. |
| [TransactionController.cs](SampleBankingApp/Controllers/TransactionController.cs#L24) | 24 | `request` not null-checked before reading `request.ToUserId`. | Add null guard. |
| [TransactionController.cs](SampleBankingApp/Controllers/TransactionController.cs#L27) | 27 | `int.Parse(userIdClaim!)` — `userIdClaim` could be null. | `TryParse` and 401 on failure. |
| [TransactionController.cs](SampleBankingApp/Controllers/TransactionController.cs#L41) | 41 | Same NRE risk on the claim. | `TryParse`. |
| [AuthController.cs](SampleBankingApp/Controllers/AuthController.cs#L20) | 20 | `request` not validated; if body missing, `request.Username` throws NRE. | `if (request is null) return BadRequest();` |
| [StringHelper.cs](SampleBankingApp/Helpers/StringHelper.cs#L13) | 13 | `IsValidEmail` reads `email.Length` without null check. | Null-guard the parameter. |
| [StringHelper.cs](SampleBankingApp/Helpers/StringHelper.cs#L22) | 22 | `IsValidUsername` reads `username.Length` without null check. | Null-guard. |
| [StringHelper.cs](SampleBankingApp/Helpers/StringHelper.cs#L45) | 45 | `MaskAccountNumber` reads `accountNumber.Length` without null check. | Null-guard. |
| [StringHelper.cs](SampleBankingApp/Helpers/StringHelper.cs#L56) | 56 | `account[^4..]` will NRE/IndexOutOfRange if `account` is null/short. | Null-guard and length check. |
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L115-L121) | 115-121 | `MapRowToUser` casts every column without `DBNull` checks — NRE/cast exception if any column is null. | Use `row.IsNull` / `Convert.ToString` etc. |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| [AuthService.cs](SampleBankingApp/Services/AuthService.cs#L91-L96) | 91-96 | `HashPasswordSha1` is never called. | Delete. |
| [AuthService.cs](SampleBankingApp/Services/AuthService.cs#L98-L108) | 103-107 | Code after the unconditional `return true;` on line 103 is unreachable, and the method is itself never called. | Delete the method (real validation is in the JWT middleware). |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L77-L85) | 77-85 | `IsWithinDailyLimit` is never invoked. | Either wire it into transfer/deposit or remove. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L94-L97) | 94-97 | `FormatCurrency` is never used. | Remove. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L99-L103) | 99-103 | `RefundTransaction` is `throw new NotImplementedException()` in non-stub code, wired into a controller. | Implement or remove the endpoint. |
| [DatabaseHelper.cs](SampleBankingApp/Data/DatabaseHelper.cs#L67-L78) | 67-78 | `ExecuteQueryWithParams` is `[Obsolete]` and unused. | Delete. |
| [DatabaseHelper.cs](SampleBankingApp/Data/DatabaseHelper.cs#L59-L65) | 59-65 | `TableExists` is never called. | Delete or document usage. |
| [StringHelper.cs](SampleBankingApp/Helpers/StringHelper.cs#L29-L36) | 29-36 | `JoinWithSeparator` is a broken duplicate of `JoinWithSeparatorFixed`; only the latter should remain. | Delete `JoinWithSeparator`. |
| [StringHelper.cs](SampleBankingApp/Helpers/StringHelper.cs#L43-L52) | 43-52 | `MaskAccountNumber` and `ObfuscateAccount` are duplicate implementations; neither appears to be called. | Consolidate into one and remove the other. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L81-L92) | 81-92 | `BuildHtmlTemplate` and `SendWelcomeEmailHtml` are never called. | Remove or wire up. |
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L11) | 11 | `_requestCount` is incremented but never read. | Delete. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L65) | 65 | Deposit cap `1000000` hardcoded inline. | Extract to a named constant or config value. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L68) | 68 | `0.05m * 1` interest bonus literal — both the rate and the meaningless `* 1` are magic. | Extract to a named constant in config (and fix the value — see §2). |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L39) | 39 | `Math.Round(amount * TransactionFeeRate, 2)` — `2` decimal places hardcoded. | Add a `CurrencyDecimals` constant or use a currency type. |
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L22-L23) | 22-23 | `id > 1000000` upper bound is duplicated in three methods. | Extract to a `MaxUserId` constant in one place. |
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L70) | 70 | Max `pageSize` of `50` hardcoded inline. | Extract to a named constant. |
| [UserController.cs](SampleBankingApp/Controllers/UserController.cs#L32) | 32 | Default `pageSize = 20` hardcoded in the attribute. | Use shared constant or config. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L40) | 40 | `"notifications@company.com"` from-address duplicated in three places. | Centralize as a config-driven constant. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L67) | 67 | `"support@company.com"` hardcoded in body text. | Move to config. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L24) | 24 | Default port `"25"` literal. | Extract or require explicit config. |
| [StringHelper.cs](SampleBankingApp/Helpers/StringHelper.cs#L13) | 13 | Email max length `254` literal. | Name as constant `MaxEmailLength`. |
| [StringHelper.cs](SampleBankingApp/Helpers/StringHelper.cs#L22) | 22 | Username bounds `3` and `20` literal. | Extract as `MinUsernameLength`/`MaxUsernameLength`. |
| [StringHelper.cs](SampleBankingApp/Helpers/StringHelper.cs#L45-L50) | 45-50 | The `4`-digit visible-tail length is repeated in two methods. | Extract to a constant. |
| [AuthService.cs](SampleBankingApp/Services/AuthService.cs#L84) | 84 | Token lifetime `AddDays(30)` is a magic literal. | Extract; also see §1 — lifetime is too long. |
| [AuthService.cs](SampleBankingApp/Services/AuthService.cs#L53-L55) | 53-55 | Hardcoded role string `"SuperAdmin"` and username `"admin"`. | Use role constants and remove backdoor. |
| [appsettings.json](SampleBankingApp/appsettings.json#L7-L8) | 7-8 | `"BankingApp"` repeated in Issuer/Audience and in other places implicitly. | Centralize. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| [StringHelper.cs](SampleBankingApp/Helpers/StringHelper.cs#L31-L34) | 31-34 | `result += item + separator` inside a loop — O(n²) string concat. | Use `string.Join` (as the "Fixed" sibling does). |
| [StringHelper.cs](SampleBankingApp/Helpers/StringHelper.cs#L16) | 16 | `new Regex(...)` inside `IsValidEmail` is recompiled every call. | `static readonly Regex` (and add `RegexOptions.Compiled`). |
| [StringHelper.cs](SampleBankingApp/Helpers/StringHelper.cs#L25) | 25 | Same problem in `IsValidUsername`. | `static readonly Regex`. |
| [StringHelper.cs](SampleBankingApp/Helpers/StringHelper.cs#L65-L71) | 65-71 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Delete and call the BCL method. |
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L10-L11) | 10-11 | `_auditLog` and `_requestCount` are mutable static state mutated from a Scoped service — race conditions across requests. | Use a proper logger/store or `Interlocked`/`ConcurrentBag`. |
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L85-L93) | 85-93 | `GetAuditReport` builds a string with `+=` in a loop. | `string.Join("\n", _auditLog)`. |
| [DatabaseHelper.cs](SampleBankingApp/Data/DatabaseHelper.cs#L19-L24) | 19-24 | `GetOpenConnection()` leaks resource ownership to callers with no documented contract — direct cause of the resource leaks in §4. | Replace with a using-scoped API or `IDbContextFactory`-style pattern. |
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L20-L23) | 20-23 | Duplicated `id <= 0` / `id > 1_000_000` validation copied to three methods. | Extract `ValidateUserId(int)`. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L56) | 56 | `Console.WriteLine` used for logging in a webapp. | Inject `ILogger<EmailService>`. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L83) | 83 | `BuildHtmlTemplate` interpolates user input into HTML — XSS in the unused `SendWelcomeEmailHtml`. | HTML-encode inputs, or use a templating system. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L90) | 90 | INSERT interpolates `decimal` and `DateTime` directly — culture-dependent formatting. | Parameterize. |
| [System.Data.SqlClient](SampleBankingApp/SampleBankingApp.csproj#L14) | 14 | `System.Data.SqlClient` is deprecated in favor of `Microsoft.Data.SqlClient`. | Migrate package. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| [Program.cs](SampleBankingApp/Program.cs#L34) | 34 | `UseDeveloperExceptionPage()` always on. | Gate with `app.Environment.IsDevelopment()`; add `UseExceptionHandler` for prod. |
| [Program.cs](SampleBankingApp/Program.cs#L36) | 36 | HTTPS redirection commented out. | Enable. |
| [Program.cs](SampleBankingApp/Program.cs#L38) | 38 | CORS `AllowAnyOrigin + AllowAnyMethod + AllowAnyHeader`. | Lock down. |
| [Program.cs](SampleBankingApp/Program.cs#L24) | 24 | `ValidateLifetime = false` on JWT. | Enable lifetime validation. |
| [appsettings.json](SampleBankingApp/appsettings.json#L18-L20) | 18-20 | Default, Microsoft, and System log levels all set to `Debug` — verbose & PII risk in prod. | Use `Information` or `Warning`; override per environment. |
| [appsettings.json](SampleBankingApp/appsettings.json#L23) | 23 | `AllowedHosts: "*"` accepts any Host header. | Specify your domains. |
| [SampleBankingApp/](SampleBankingApp/) | n/a | No `appsettings.Production.json` / environment-specific override files present. | Add per-environment configuration. |
| [SampleBankingApp.csproj](SampleBankingApp/SampleBankingApp.csproj#L14) | 14 | `System.Data.SqlClient 4.8.6` is in maintenance mode. | Switch to `Microsoft.Data.SqlClient`. |
| [SampleBankingApp.csproj](SampleBankingApp/SampleBankingApp.csproj#L15) | 15 | `Newtonsoft.Json 12.0.3` has known CVEs (e.g. denial-of-service in deep JSON) and is well out of date. | Upgrade to current `Newtonsoft.Json` or use `System.Text.Json`. |
| [SampleBankingApp.csproj](SampleBankingApp/SampleBankingApp.csproj#L16) | 16 | `System.IdentityModel.Tokens.Jwt 7.0.0` is mismatched with `Microsoft.AspNetCore.Authentication.JwtBearer 8.0.0` and predates fixes in the 7.x series. | Align versions and update. |
| [SampleBankingApp.csproj](SampleBankingApp/SampleBankingApp.csproj#L8-L9) | 8-9 | `DebugSymbols=true` + `DebugType=full` applied unconditionally (including Release). | Use `<DebugType Condition="'$(Configuration)'=='Debug'">portable</DebugType>` or remove. |

## 10. Missing Unit Tests

No test project is present in the repository (no `*.Tests.csproj`, no `tests/` folder, no test references in the only `.csproj`). The following are the highest-priority targets to cover.

| File | Line | Issue | Fix |
|------|------|-------|-----|
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L23) | 23 | `Transfer` — boundary cases: amount of `0` and negative; insufficient funds at exactly `amount` vs `amount + fee`; self-transfer; non-existent `toUserId`; partial-failure (second UPDATE fails). | Add unit and integration tests covering each. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L63) | 63 | `Deposit` — boundaries `0`, `1`, `1_000_000`, `1_000_001`; verify the interest-bonus regression doesn't reappear. | Add boundary tests. |
| [TransactionService.cs](SampleBankingApp/Services/TransactionService.cs#L77) | 77 | `IsWithinDailyLimit` — at `MaxTransactionsPerDay-1`, `=`, and `+1`. | Tests once it's wired into Transfer. |
| [AuthService.cs](SampleBankingApp/Services/AuthService.cs#L28) | 28 | `Login` — valid creds, wrong password, missing user, inactive user, SQL-injection inputs, and a regression test asserting the admin backdoor is gone. | Add full coverage. |
| [AuthService.cs](SampleBankingApp/Services/AuthService.cs#L68) | 68 | `GenerateJwtToken` — claims present, lifetime correct, signing key honored. | Add. |
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L68) | 68 | `GetUsersPage` — page 1 returns rows 1..N (off-by-one regression), negative/zero `pageSize`, `pageSize > 50`. | Add. |
| [UserService.cs](SampleBankingApp/Services/UserService.cs#L95) | 95 | `SearchUsers` — special LIKE characters (`%`, `_`, `[`), empty query, error path (should not swallow). | Add. |
| [UserController.cs](SampleBankingApp/Controllers/UserController.cs#L38) | 38 | `UpdateUser`/`DeleteUser` — caller is not owner/not admin → must be 403. | Integration tests on auth. |
| [StringHelper.cs](SampleBankingApp/Helpers/StringHelper.cs#L11) | 11 | `IsValidEmail`/`IsValidUsername`/`MaskAccountNumber` — null inputs, boundary lengths (`254`, `255`, `3`, `2`, `20`, `21`), and inputs shorter than 4 for masking. | Add. |
| [EmailService.cs](SampleBankingApp/Services/EmailService.cs#L34) | 34 | `SendTransferNotification` — retry behavior (succeeds on attempt 3; fails after `MaxRetries`). | Add with `SmtpClient` abstracted. |

---

**Overall:** the codebase exhibits multiple critical security defects (SQL injection in nearly every data path, hardcoded admin backdoor, broken auth, open CORS, plaintext SMTP, source-controlled prod credentials, JWT misconfiguration), a financially impactful logic bug (deposit "interest bonus" inflates balances by 5% per call) plus a pagination off-by-one, systemic resource leaks via `DatabaseHelper.GetOpenConnection`, and no test coverage. Recommend blocking merge until at least the security and financial-correctness items are resolved.
