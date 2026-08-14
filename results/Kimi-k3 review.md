# Peer Code Review — branch `kimi-k3` (commit 4fa5892e)

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| AuthService.cs | 32 | SQL injection: username/password interpolated directly into Login query. | Use parameterized `SqlCommand` with `@Username`/`@Password`. |
| AuthService.cs | 17, 53 | Hardcoded backdoor: `admin`/`SuperAdmin2024` grants SuperAdmin bypassing the DB. | Delete the bypass block entirely. |
| AuthService.cs | 61 | Passwords hashed with unsalted MD5. | Use PBKDF2/bcrypt/ASP.NET Core Identity hasher. |
| AuthService.cs | 91 | Weak SHA1 hash helper present in source. | Remove `HashPasswordSha1`. |
| DatabaseHelper.cs | 16 | Hardcoded SA credentials (`Admin1234!`) in fallback connection string. | Remove fallback; throw if config missing. |
| DatabaseHelper.cs | 29 | `ExecuteQuery` concatenates `tableName`/`whereClause` into raw SQL. | Delete method or whitelist tables and parameterize predicates. |
| UserService.cs | 99 | SQL injection: user `query` interpolated into LIKE clause. | Parameterize with `@q` and escape `%`/`_`. |
| UserService.cs | 47 | SQL injection: email/username interpolated into UPDATE. | Parameterize the statement. |
| UserService.cs | 61 | DELETE built via string interpolation (int id is safe, but pattern is dangerous). | Parameterize for consistency. |
| TransactionService.cs | 47–48 | Balance UPDATEs built via interpolation. | Parameterize. |
| TransactionService.cs | 89–90 | SQL injection: user-controlled `description` interpolated into INSERT. | Parameterize all values. |
| TransactionService.cs | 70–71 | Deposit UPDATE built via interpolation. | Parameterize. |
| Program.cs | 24 | `ValidateLifetime = false` — expired JWTs are accepted. | Set to `true`. |
| Program.cs | 34 | `UseDeveloperExceptionPage()` unconditional — stack traces leak in production. | Call only in Development. |
| Program.cs | 36 | HTTPS redirection commented out. | Re-enable `app.UseHttpsRedirection()`. |
| Program.cs | 38 | CORS allows any origin/method/header. | Whitelist known origins and methods. |
| appsettings.json | 3 | Production SA password committed to source control. | Move to user-secrets/KeyVault/env vars. |
| appsettings.json | 6 | JWT secret `"mysecretkey"` is weak and too short for HS256 (will also throw at runtime). | Use a 32+ byte secret from configuration. |
| appsettings.json | 14 | SMTP password committed to source control. | Move to secrets store. |
| appsettings.json | 3 | `TrustServerCertificate=True` disables TLS cert validation for SQL. | Remove in production. |
| EmailService.cs | 29 | `EnableSsl = false` sends SMTP credentials in cleartext. | Enable SSL and use port 587. |
| UserController.cs | 22 | Any authenticated user can read any user by id (no ownership check). | Verify caller id or Admin role. |
| UserController.cs | 39 | Any user can update any other user's account. | Enforce ownership or Admin role. |
| UserController.cs | 57 | Any user can delete any account. | Require Admin role. |
| UserController.cs | 79 | Audit log exposed to any authenticated user. | Require Admin role. |
| UserController.cs | 32 | Full user list endpoint has no role restriction. | Require Admin role. |
| TransactionController.cs | 49 | Refund has no ownership check on `transactionId`. | Verify caller owns the transaction. |
| AuthController.cs | 20 | No rate limiting or lockout on login — brute-forceable. | Add throttling/lockout middleware. |
| AuthService.cs | 84 | 30-day JWT lifetime is excessive for a banking app. | Use short-lived tokens with refresh. |
| UserController.cs | 52 | Raw `ex.Message` returned to HTTP clients on 500. | Return generic message; log details. |
| User.cs | 7 | `Password` property on the model returned by API endpoints. | Use a DTO without credential fields. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| UserService.cs | 72 | Off-by-one: `skip = page * pageSize` skips the entire first page. | Use `(page - 1) * pageSize`. |
| TransactionService.cs | 25 | `amount < 0` allows zero-amount transfers. | Use `amount <= 0`. |
| TransactionService.cs | 42 | Balance check `fromBalance >= amount` ignores the fee, so debit of `amount + fee` can drive balance negative. | Compare against `totalDebit`. |
| TransactionService.cs | 23 | No self-transfer check; when from==to the second UPDATE overwrites the first, crediting `amount` for free. | Reject `fromUserId == toUserId`. |
| TransactionService.cs | 68 | Deposit adds a 5% bonus (`amount * 0.05m * 1`) — free money on every deposit; `* 1` suggests a broken rate. | Remove bonus or use a configured, correct rate. |
| TransactionService.cs | 39 | Fee is debited from sender but never credited anywhere — money is destroyed. | Credit a fee/revenue account. |
| TransactionService.cs | 77 | Daily transaction limit is never enforced (helper unused). | Call `IsWithinDailyLimit` in `Transfer`. |
| TransactionService.cs | 63 | Deposit "succeeds" and records a transaction even when the user doesn't exist (0 rows updated). | Check rows affected / user existence first. |
| UserService.cs | 70 | No lower-bound validation on `page`/`pageSize` — page 0 or negative values produce negative OFFSET and a SQL error. | Validate `page >= 1`, `pageSize >= 1`. |
| UserService.cs | 22 | Arbitrary `id > 1000000` cap rejects legitimate users as the table grows. | Remove the cap. |
| AuthService.cs | 103 | `ValidateToken` always returns `true` for any non-empty string. | Implement real signature/expiry validation. |
| StringHelper.cs | 33 | `JoinWithSeparator` leaves a trailing separator on the result. | Use `string.Join`. |
| StringHelper.cs | 56 | `ObfuscateAccount` throws `IndexOutOfRangeException` for accounts shorter than 4 chars. | Guard length like `MaskAccountNumber`. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| UserService.cs | 105–107 | `catch (Exception)` returns an empty list — callers can't distinguish error from no results (and it hides injection failures). | Let it throw or return a result/error type. |
| EmailService.cs | 75–78 | `SendWelcomeEmail` swallows all exceptions to `Console.WriteLine`. | Log via `ILogger` and apply a retry policy. |
| TransactionService.cs | 47–50 | Two balance UPDATEs plus INSERT are not wrapped in a transaction — a mid-operation failure loses money. | Use a single `SqlTransaction`. |
| TransactionService.cs | 52 | Email is sent after DB writes; if it throws, client gets 500 but the money already moved. | Use an outbox/queue or send after commit with compensation. |
| TransactionService.cs | 70–73 | Deposit UPDATE and transaction INSERT are not atomic. | Wrap in a transaction. |
| UserController.cs | 52 | 500 response leaks raw `ex.Message`. | Return generic message and log. |
| UserController.cs | 48 | `BadRequest(ex.Message)` leaks internal validation strings. | Return fixed, safe messages. |
| AuthController.cs | 20 | No rate limiting or account lockout on the auth endpoint. | Add throttling/lockout. |
| EmailService.cs | 56 | Retry failures logged with `Console.WriteLine` instead of a logger. | Inject `ILogger<EmailService>`. |
| TransactionController.cs | 56 | `NotImplementedException` used as control flow for the refund endpoint. | Return 501 until implemented, then implement. |
| AuthService.cs | 28 | `Login` has no exception handling; SQL errors bubble to the dev exception page. | Catch, log, and return a generic failure. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| AuthService.cs | 34–38 | `SqlConnection`, `SqlCommand`, and `SqlDataReader` never disposed; early return at line 42 skips any cleanup. | Use `using` declarations for all three. |
| DatabaseHelper.cs | 28–29 | `ExecuteQuery` never closes/disposes the connection or command. | Wrap both in `using`. |
| DatabaseHelper.cs | 52–55 | `ExecuteNonQuery`: any exception skips `connection.Close()`; command undisposed. | Use `using` blocks instead of manual `Close()`. |
| DatabaseHelper.cs | 19 | `GetOpenConnection` returns an open connection, leaking ownership to callers with no contract. | Make private; keep connections inside `using` scopes. |
| EmailService.cs | 16 | `SmtpClient` held as an instance field — not thread-safe and its socket is never released. | Create and dispose per send operation. |
| EmailService.cs | 39 | `MailMessage` in `SendTransferNotification` never disposed. | Wrap in `using`. |
| EmailService.cs | 69 | `MailMessage` in `SendWelcomeEmail` never disposed. | Wrap in `using`. |
| EmailService.cs | 89 | `MailMessage` in `SendWelcomeEmailHtml` never disposed. | Wrap in `using`. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| Program.cs | 16, 28 | `jwtSecret` may be null; `Encoding.UTF8.GetBytes(jwtSecret!)` throws at startup. | Validate required config at startup with a clear error. |
| AuthService.cs | 70 | `_config["Jwt:SecretKey"]!` null-forgiving can throw inside `GetBytes`. | Guard or validate config first. |
| TransactionController.cs | 27 | `int.Parse(userIdClaim!)` throws if the NameIdentifier claim is missing. | Use `int.TryParse` and return 401 on failure. |
| TransactionController.cs | 41 | Same `int.Parse(userIdClaim!)` risk in Deposit. | Same fix. |
| TransactionService.cs | 36–37 | `Rows[0]` accessed without checking `Rows.Count` — missing user crashes instead of returning an error. | Check `Rows.Count > 0` and return a failure tuple. |
| TransactionService.cs | 53–55 | `(string)Rows[0]["Email"]` / `["Username"]` casts throw on `DBNull`. | Null-check or use `Convert.ToString`. |
| StringHelper.cs | 13 | `email.Length` evaluated before any null check. | Guard with `IsNullOrEmpty`. |
| StringHelper.cs | 22 | `username.Length` evaluated before any null check. | Guard with `IsNullOrEmpty`. |
| EmailService.cs | 65 | `username.ToUpper()` called on a parameter with no null check. | Null-check the parameter. |
| EmailService.cs | 22 | `_config["Email:SmtpHost"]` may be null when passed to `SmtpClient`. | Validate config in constructor. |
| UserService.cs | 115–121 | `MapRowToUser` direct casts throw on `DBNull` values. | Use safe conversion helpers. |
| AuthController.cs | 22 | `request.Username`/`Password` can be JSON-null despite the initializer. | Add `[Required]` model validation. |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| AuthService.cs | 91 | `HashPasswordSha1` is never called. | Remove. |
| AuthService.cs | 98 | `ValidateToken` is never called anywhere. | Remove or wire into auth pipeline. |
| AuthService.cs | 105–107 | Unreachable code after unconditional `return true`. | Remove. |
| StringHelper.cs | 29 | Broken `JoinWithSeparator` exists alongside the fixed version and is unused. | Remove the broken one. |
| StringHelper.cs | 54 | `ObfuscateAccount` duplicates `MaskAccountNumber` and is never called. | Remove. |
| StringHelper.cs | 59 | `ToTitleCase` is never called. | Remove or use. |
| StringHelper.cs | 65 | `IsBlank` is never called. | Remove. |
| TransactionService.cs | 77 | `IsWithinDailyLimit` is never called — the daily limit is dead. | Call it in `Transfer` or remove. |
| TransactionService.cs | 94 | `FormatCurrency` is never called. | Remove. |
| TransactionService.cs | 99 | `RefundTransaction` is a `NotImplementedException` stub wired to a live endpoint. | Implement or remove the endpoint. |
| DatabaseHelper.cs | 67–68 | `[Obsolete]` `ExecuteQueryWithParams` still present. | Remove. |
| EmailService.cs | 86 | `SendWelcomeEmailHtml` is never called. | Remove or use. |
| UserService.cs | 11 | `_requestCount` is incremented but never read. | Remove or expose as a metric. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| TransactionService.cs | 65 | `1000000` deposit cap literal inline. | Named constant or config value. |
| TransactionService.cs | 68 | `0.05m` interest rate and stray `* 1` inline. | Named constant from configuration. |
| UserService.cs | 22, 42, 56 | `1000000` max-user-id literal repeated in three methods. | Single shared constant (or remove the check). |
| UserService.cs | 70 | `50` page-size cap literal. | Named constant or config. |
| StringHelper.cs | 13, 22 | `254`, `3`, `20` length limits inline. | Named constants. |
| EmailService.cs | 40, 69, 89 | `"notifications@company.com"` repeated three times. | Constant or config value. |
| EmailService.cs | 67 | `"support@company.com"` literal. | Config value. |
| EmailService.cs | 24 | `"25"` port fallback literal. | Named default constant. |
| AuthService.cs | 53 | `"admin"` / `"SuperAdmin"` literals (part of the backdoor). | Remove with the backdoor. |
| AuthService.cs | 84 | `AddDays(30)` token lifetime inline. | Move to `Jwt:ExpiryMinutes` config. |
| TransactionService.cs | 50, 73, 90 | `"Transfer"`, `"Deposit"`, `"Completed"` status/type strings inline. | Enum or constants. |
| DatabaseHelper.cs | 16 | Fallback connection string literal. | Remove; require configuration. |
| appsettings.json | 3, 6, 14 | Secrets hardcoded instead of environment-specific stores. | User secrets/KeyVault/env vars. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| StringHelper.cs | 31–33 | String concatenation inside a loop (O(n²)). | Use `string.Join`. |
| UserService.cs | 87–90 | String concatenation building the audit report in a loop. | Use `StringBuilder`. |
| StringHelper.cs | 16, 25 | `new Regex(...)` created on every call. | `static readonly` or `[GeneratedRegex]`. |
| UserService.cs | 10 | Shared mutable static `List<string>` with no synchronization and unbounded growth. | Use a thread-safe store or database table. |
| UserService.cs | 11, 25 | Static `_requestCount++` is not thread-safe. | `Interlocked.Increment` or remove. |
| StringHelper.cs | 65 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Use the BCL method. |
| DatabaseHelper.cs | 19 | Helper designed to leak open-connection ownership with no documented contract. | Keep connections internal with `using`. |
| UserService.cs | 20–23 | ID validation duplicated in three methods. | Extract a shared `ValidateUserId`. |
| EmailService.cs | 56, 77 | `Console.WriteLine` used for error reporting in a web app. | Inject `ILogger`. |
| DatabaseHelper.cs | 42 | `AddWithValue` causes type-inference pitfalls. | `Parameters.Add` with explicit `SqlDbType`. |
| UserService.cs | 28 | `SELECT *` couples code to schema. | Select explicit columns. |
| EmailService.cs | 16 | `SmtpClient` is marked obsolete by Microsoft. | Use MailKit or a mail API. |
| TransactionController.cs | 56 | Exception type used as feature-flag control flow. | Return 501 or implement. |
| User.cs | 5 | Entity with `Password` used directly as API response model. | Introduce response DTOs. |
| StringHelper.cs | 62 | `ToTitleCase` uses `CurrentCulture` — culture-dependent output. | Specify a culture explicitly. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| Program.cs | 34 | `UseDeveloperExceptionPage()` called unconditionally. | Gate on `app.Environment.IsDevelopment()`. |
| Program.cs | 24 | `ValidateLifetime = false` on JWT validation. | Set `true`. |
| Program.cs | 36 | HTTPS redirection commented out. | Uncomment. |
| Program.cs | 38 | Overly permissive CORS (`AllowAnyOrigin` + `AllowAnyMethod` + `AllowAnyHeader`). | Restrict to known origins. |
| appsettings.json | 18–20 | `Debug` log level for Default/Microsoft/System in what is effectively production config. | Use `Information`/`Warning`. |
| appsettings.json | 6 | Weak, short JWT secret committed. | Strong secret via environment. |
| appsettings.json | 3, 14 | DB and SMTP passwords committed to source control. | External secrets store. |
| appsettings.json | 3 | `TrustServerCertificate=True` in production connection string. | Remove. |
| appsettings.json | 23 | `AllowedHosts: "*"` permits host-header attacks. | List explicit hosts. |
| (repo root) | — | No `appsettings.Production.json` or environment overrides exist. | Add per-environment config files. |
| SampleBankingApp.csproj | 8–9 | `DebugSymbols=true` / `DebugType=full` ships full PDBs in release builds. | Remove or set `pdbonly`/`none` for Release. |
| SampleBankingApp.csproj | 15 | Newtonsoft.Json 12.0.3 is outdated with known high-severity vulnerabilities. | Upgrade to 13.0.3+. |
| SampleBankingApp.csproj | 14 | `System.Data.SqlClient` is legacy/deprecated. | Migrate to `Microsoft.Data.SqlClient`. |
| SampleBankingApp.csproj | 16 | `System.IdentityModel.Tokens.Jwt` 7.0.0 mismatched with JwtBearer 8.0.0. | Align both to 8.x. |
| SampleBankingApp.csproj | 7 | `TreatWarningsAsErrors=false` lets warnings (e.g., obsolete SQL injection helpers) slip through. | Set `true`. |

## 10. Missing Unit Tests

No test project exists in the branch. The following are the most critical methods and scenarios to cover:

| File | Line | Issue | Fix |
|---|---|---|---|
| TransactionServiceTests.cs (new) | — | `Transfer`: balance check must include the fee (boundary: balance == amount, balance == amount + fee). | Add tests proving negative balances are impossible. |
| TransactionServiceTests.cs (new) | — | `Transfer`: self-transfer (from == to) currently mints money. | Add test asserting rejection. |
| TransactionServiceTests.cs (new) | — | `Transfer`: zero/negative amounts and nonexistent sender/recipient. | Add boundary and `Rows.Count == 0` tests. |
| TransactionServiceTests.cs (new) | — | `Transfer`: atomicity when the second UPDATE or the email send fails. | Add rollback/outbox tests. |
| TransactionServiceTests.cs (new) | — | `Deposit`: boundaries 0, negative, 1,000,000, 1,000,001, and the erroneous 5% bonus. | Add boundary and calculation tests. |
| UserServiceTests.cs (new) | — | `GetUsersPage`: page 1 must return the first N rows (off-by-one), pageSize cap at 50, page 0/negative. | Add pagination tests. |
| AuthServiceTests.cs (new) | — | `Login`: valid/invalid credentials, inactive user, SQL-injection strings in username, and absence of the admin backdoor. | Add auth-flow tests. |
| AuthServiceTests.cs (new) | — | JWT: expired tokens must be rejected; lifetime should come from config. | Add token-validation tests. |
| UserServiceTests.cs (new) | — | `SearchUsers`: injection attempts (`' OR 1=1--`) and error-vs-empty-result behavior. | Add security and error-path tests. |
| UserServiceTests.cs (new) | — | `UpdateUser`/`DeleteUser`: id boundary validation (0, negative). | Add validation tests. |
| StringHelperTests.cs (new) | — | Email/username length boundaries (254/255, 2/3/20/21) and masking accounts shorter than 4 chars. | Add helper tests. |
| AuthControllerTests.cs (new) | — | Login endpoint: lockout/rate-limit behavior and uniform failure messages. | Add integration tests. |

---

### Additional Commentary

The most urgent items are the **admin backdoor** (AuthService.cs:53), the **self-transfer money-creation bug** (TransactionService.cs:23–48), the **fee-excluded balance check**, the **deposit 5% bonus**, and the **multiple SQL injection points** — these are actively exploitable and financially damaging. The non-atomic transfer combined with a post-commit email side effect means failures will silently corrupt balances. Recommend blocking merge until categories 1–3 are remediated, secrets are rotated (they are now in git history), and a test project covering the financial paths is added.