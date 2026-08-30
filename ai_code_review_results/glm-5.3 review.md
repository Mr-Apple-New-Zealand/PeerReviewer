Let me work through this code review methodically. I have the full source of a small ASP.NET Core banking app. Let me enumerate all files:

1. Controllers/AuthController.cs
2. Controllers/TransactionController.cs
3. Controllers/UserController.cs
4. Data/DatabaseHelper.cs
5. Helpers/StringHelper.cs
6. Models/Transaction.cs
7. Models/User.cs
8. Program.cs
9. SampleBankingApp.csproj
10. Services/AuthService.cs
11. Services/EmailService.cs
12. Services/TransactionService.cs
13. Services/UserService.cs
14. appsettings.json

Let me go category by category.

### 1. Security Vulnerabilities

**SQL Injection:**
- `AuthService.Login` (line 32): `string sql = $"SELECT * FROM Users WHERE Username = '{username}' AND Password = '{hashedPassword}' AND IsActive = 1";` — SQL injection via username (and password hash). Classic.
- `DatabaseHelper.ExecuteQuery` (line 26-34): accepts `tableName` and `whereClause` raw — SQL injection by design.
- `UserService.UpdateUser` (line 47): `string sql = $"UPDATE Users SET Email = '{email}', Username = '{username}' WHERE Id = {id}";` — injection via email/username.
- `UserService.DeleteUser` (line 61): `string sql = $"DELETE FROM Users WHERE Id = {id}";` — id is int so less exploitable, but still string interpolation pattern; id is validated int so it's parameterizable. Still report as pattern.
- `UserService.SearchUsers` (line 99): `_db.ExecuteQuery("Users", $"Username LIKE '%{query}%'")` — injection via query, also LIKE wildcard injection.
- `TransactionService.Transfer` (lines 47-48): `UPDATE Users SET Balance = {newFromBalance} WHERE Id = {fromUserId}` — interpolated UPDATE. Values are decimals/ints computed internally, but still pattern; also decimal.ToString culture issues could break SQL. Report.
- `TransactionService.Deposit` (line 70-71): interpolated UPDATE.
- `TransactionService.RecordTransaction` (lines 89-91): interpolated INSERT with `'{description}'` — description comes from user request → direct SQL injection. Also `'{type}'` internal. This is the big one: description is user-controlled.
- `DatabaseHelper.ExecuteNonQuery` accepts raw SQL — helper accepting raw SQL fragments.

**Hardcoded credentials:**
- `DatabaseHelper` constructor line 16: fallback connection string with `sa` / `Admin1234!` hardcoded.
- `AuthService.AdminBypassPassword = "SuperAdmin2024"` — hardcoded backdoor password. Also the bypass at line 53-56 is a backdoor: `if (username == "admin" && password == AdminBypassPassword)` returns a SuperAdmin user. This is a backdoor.
- appsettings.json: production DB connection string with sa password `Admin1234!` committed.
- appsettings.json: Email password `EmailPass99` committed.
- appsettings.json: JWT SecretKey `mysecretkey` — weak secret committed to source control.

**Weak crypto:**
- `HashPasswordMd5` — MD5, unsalted, for passwords.
- `HashPasswordSha1` — SHA1, unsalted (also dead code).

**JWT misconfiguration:**
- Program.cs line 24: `ValidateLifetime = false` — expired tokens accepted.
- JWT secret "mysecretkey" is weak/short.
- Token expiry 30 days (line 84 AuthService) — long-lived tokens.
- `ValidateToken` in AuthService returns true unconditionally (dead code after return, but also a security issue if used).

**Broken access control:**
- `UserController.UpdateUser` (PUT) — no ownership check; any authenticated user can update any user's email/username.
- `UserController.DeleteUser` (DELETE) — no ownership/admin check; any authenticated user can delete any user.
- `UserController.GetUser` — any authenticated user can view any user (IDOR), including balance. Report.
- `UserController.GetUsers` — lists all users to any authenticated user; no admin restriction. Report.
- `UserController.GetAuditLog` — audit report exposed to any authenticated user, no admin role check. Report.
- `TransactionController.Refund` — no ownership check on transactionId; any user could refund any transaction (once implemented). Report.
- `AuthController.Login` — no rate limiting / lockout (also error handling category).
- Missing `[Authorize]` on... AuthController is intentionally anonymous (login). All other controllers have `[Authorize]`. But no role-based `[Authorize(Roles=...)]` anywhere — admin endpoints unprotected. Report under missing authorization attributes.

**CORS:**
- Program.cs line 38: `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` — open CORS.

**Developer exception page:**
- Program.cs line 34: `app.UseDeveloperExceptionPage()` unconditionally (no env check).

**HTTPS disabled:**
- Program.cs line 36: `// app.UseHttpsRedirection();` commented out.

**Debug symbols:**
- csproj: `<DebugSymbols>true</DebugSymbols>` and `<DebugType>full</DebugType>` — debug symbols in release builds.

**Production secrets committed:**
- appsettings.json contains prod DB creds, email creds, JWT secret.

Also `TrustServerCertificate=True` in connection string — minor security issue (MITM). Could report.

Also `EnableSsl = false` in EmailService — credentials sent over unencrypted SMTP. Report.

### 2. Logic Errors

- `UserService.GetUsersPage` line 72: `int skip = page * pageSize;` — off-by-one; should be `(page - 1) * pageSize`. Page 1 skips 20 rows.
- `TransactionService.Transfer` line 42: `if (fromBalance >= amount)` but then deducts `amount + fee` — balance check excludes fee; can produce negative balance. Report.
- `TransactionService.Transfer` line 25: `if (amount < 0)` — should be `<= 0`; zero-amount transfers allowed. Report.
- `TransactionService.Transfer`: no self-transfer check (fromUserId == toUserId). Report.
- `TransactionService.Deposit` line 68: `decimal interestBonus = amount * 0.05m * 1;` — 5% "interest bonus" on every deposit; the `* 1` is meaningless; likely intended 1% or monthly rate. Report as incorrect constant (5% bonus on deposit) and the `* 1` no-op.
- `TransactionService.Deposit`: no check that user exists — UPDATE affects 0 rows silently, still records transaction and returns success. Report.
- `TransactionService.Transfer`: no check that fromUser/toUser rows exist — `Rows[0]` would throw IndexOutOfRange if user not found. That's null-reference/error handling, but also logic: transfer to nonexistent user. Report under null reference risks.
- `TransactionService.Transfer`: no concurrency control — balance read then updated (race condition / TOCTOU). Could report under logic or error handling (missing transaction). The two UPDATEs are not atomic — missing DB transaction. Report under error handling.
- `IsWithinDailyLimit` is never called — MaxTransactionsPerDay never enforced. That's dead code (category 6) but also a logic gap: daily limit not enforced. Report in logic errors too? The instruction says report all issues. I'll mention in dead code primarily, and maybe logic: transfer/deposit don't enforce daily limit. I'll add a row.
- `UserService.GetUserById`: `id > 1000000` throws ArgumentException — arbitrary boundary; controller GetUser doesn't catch ArgumentException → 500. Actually GetUser doesn't have try/catch, so ArgumentException → 500 unhandled. That's error handling. Also the boundary check itself is a magic number.
- `AuthService.Login` bypass user has Id = 0 — NameIdentifier claim "0"; int.Parse fine; transfers from user 0 would fail at Rows[0]. Minor.
- `StringHelper.JoinWithSeparator` appends separator after last item — trailing separator bug (also duplicate of string.Join). Report in logic or anti-patterns. It's a logic error: result has trailing separator. Report in logic errors.
- `StringHelper.ObfuscateAccount`: `account[^4..]` throws IndexOutOfRange for strings shorter than 4 chars. Report in null reference/logic. Also duplicates MaskAccountNumber. Report.
- `EmailService.SendTransferNotification` retry loop: if all retries fail it throws — but also `while (attempt < MaxRetries)` with `return` on success; if SmtpException not thrown... fine. Actually there's a subtle bug: if the loop exits normally (attempt reaches MaxRetries without throw — can't happen since throw at >= MaxRetries). OK.
- `TransactionService.Transfer`: fee is charged but not recorded anywhere (fee money vanishes) — the recipient gets amount, sender loses amount+fee, fee not credited to any account. Report as logic error.
- `Deposit` records `RecordTransaction(0, userId, ...)` — FromUserId 0 sentinel. Minor.
- `GetUsersPage`: no validation of page < 1 — negative page produces negative skip → SQL error. `page = 0` → skip 0, same as page 1. Report boundary condition.
- `GetUsersPage`: pageSize not validated for <= 0 — pageSize 0 or negative → FETCH NEXT 0/negative rows error. Report.
- `AuthService.ValidateToken`: returns true always — logic error (token validation always passes). Report (also dead code).
- `UserService.UpdateUser` returns true always even if user doesn't exist (0 rows affected). Report.
- `UserService.DeleteUser` same — returns true even if no rows. Report.
- `TransactionController.Refund` catches NotImplementedException and returns 500 — fine-ish.
- `EmailService` constructor: `int.Parse(_config["Email:SmtpPort"] ?? "25")` — has null-coalesce, OK. But `_config["Email:Username"]` could be null → NetworkCredential(null, null). Minor.
- `Program.cs`: `jwtSecret` could be null → `Encoding.UTF8.GetBytes(jwtSecret!)` — null ref risk (category 5).
- `AuthService.Login` reads connection string directly rather than using DatabaseHelper — inconsistent, but not a bug per se.
- `TransactionService.Transfer`: `amount` decimal interpolated into SQL — decimal.ToString() with current culture could produce comma as decimal separator in some cultures → SQL error or injection-ish. Minor; mention in SQL injection/format issues.
- `StringHelper.IsValidEmail`/`IsValidUsername`: `email.Length` without null check → NRE if null. Category 5.
- `MaskAccountNumber` fine.
- `ToTitleCase` fine.
- `IsBlank` reimplements `string.IsNullOrWhiteSpace`. Category 8.

### 3. Error Handling

- `UserService.SearchUsers` (lines 97-108): catches `Exception` and returns empty list — swallows errors, callers can't distinguish no results from error. Report.
- `EmailService.SendWelcomeEmail` (lines 71-78): catches Exception, logs to Console, swallows. Report.
- `EmailService.SendTransferNotification`: called after DB writes in Transfer — email failure throws after balances committed; no transaction; user gets error but transfer succeeded. Report: side effect after DB write.
- `TransactionService.Transfer`: two UPDATEs + INSERT not wrapped in a transaction — partial failure leaves inconsistent state. Report.
- `TransactionService.Deposit`: UPDATE + INSERT not atomic. Report.
- `UserController.UpdateUser` line 50-52: `catch (Exception ex) return StatusCode(500, ex.Message)` — leaks internal error message to client. Report.
- `UserController.UpdateUser` line 46-48: `catch (ArgumentException ex) return BadRequest(ex.Message)` — returns raw exception message; less severe but still internal info. Report maybe.
- `AuthController.Login`: no rate limiting or account lockout. Report.
- `AuthService.Login`: no error handling for DB failures — SqlException propagates as 500. Minor; maybe skip or report.
- `TransactionController.Transfer`: `int.Parse(userIdClaim!)` — if claim missing, NullReferenceException/FormatException → 500. Category 5 mostly.
- `UserService.GetUserById` throws ArgumentException for invalid ids; `UserController.GetUser` has no try/catch → unhandled 500 with stack trace (developer exception page shows details). Report.
- `EmailService.SendTransferNotification` retry: no delay between retries. Minor quality issue — could report in anti-patterns.
- `Console.WriteLine` used instead of ILogger in EmailService. Report in anti-patterns or error handling. I'll put in anti-patterns/quality.
- `TransactionController.Refund` catches NotImplementedException → 500 "Refund not yet implemented" — acceptable but the endpoint exists; report under dead code/NotImplementedException.
- `AuthService.Login`: connection/reader not closed on exception (resource leak category).
- `UserService.GetAuditReport` — no error handling needed.
- Missing global exception handler — developer exception page leaks stack traces. Covered in security.

### 4. Resource Leaks

- `DatabaseHelper.ExecuteQuery` (lines 28-33): connection from GetOpenConnection never disposed/closed (SqlDataAdapter doesn't dispose connection); command and adapter not disposed. Report.
- `DatabaseHelper.ExecuteNonQuery` (lines 50-57): connection closed but not disposed (Close without using); command not disposed; if ExecuteNonQuery throws, Close is skipped. Report both.
- `DatabaseHelper.GetOpenConnection`: returns open connection; callers (ExecuteQuery, ExecuteNonQuery) don't dispose — ownership leak contract. Report.
- `AuthService.Login` (lines 34-38): SqlConnection, SqlCommand, SqlDataReader never closed/disposed, even on success path. Report.
- `EmailService._smtpClient`: SmtpClient held as instance field, never disposed; not thread-safe; socket exhaustion. Report.
- `EmailService.SendTransferNotification`: MailMessage never disposed (created each call, not using). Report.
- `EmailService.SendWelcomeEmail`: MailMessage never disposed. Report.
- `EmailService.SendWelcomeEmailHtml`: MailMessage never disposed. Report.
- `DatabaseHelper.ExecuteQuerySafe`: uses `using var` for connection and command — OK. SqlDataAdapter not disposed but that's minor; adapter doesn't hold unmanaged... Actually SqlDataAdapter implements IDisposable; Fill opens/closes connection itself if closed. Minor — could report adapter not disposed. I'll mention lightly or skip. I'll include for completeness? The prompt says report all issues no matter how minor. I'll include a row for SqlDataAdapter not disposed in ExecuteQuerySafe and ExecuteQueryWithParams. Hmm, that might be overkill but thoroughness is valued. I'll include.
- `DatabaseHelper.ExecuteQueryWithParams`: uses statements — fine except adapter.

### 5. Null Reference Risks

- `Program.cs` line 16/28: `builder.Configuration["Jwt:SecretKey"]` → `Encoding.UTF8.GetBytes(jwtSecret!)` — if config missing, null → ArgumentNullException at startup. Report.
- `AuthService.GenerateJwtToken` line 70: `_config["Jwt:SecretKey"]!` — same null risk. Report.
- `TransactionController.Transfer` line 27: `int.Parse(userIdClaim!)` — null-forgiving on possibly-null claim. Report.
- `TransactionController.Deposit` line 41: same. Report.
- `TransactionService.Transfer` lines 36-37: `fromUserTable.Rows[0]` / `toUserTable.Rows[0]` without Count check → IndexOutOfRangeException if user missing. Report both.
- `TransactionService.IsWithinDailyLimit` line 83: `table.Rows[0]["TxCount"]` — COUNT(*) always returns a row, so OK actually. Skip or note it's fine. Skip.
- `UserService.GetUserById`: checks Rows.Count — good.
- `StringHelper.IsValidEmail` line 13: `email.Length` — no null check; parameter non-nullable declared but callers may pass null. Report.
- `StringHelper.IsValidUsername` line 22: same. Report.
- `StringHelper.MaskAccountNumber` line 45: `accountNumber.Length` no null check. Report.
- `StringHelper.ObfuscateAccount` line 56: `account[^4..]` throws for length < 4; no null check. Report.
- `EmailService` constructor: `_config["Email:Username"]`/`Password` may be null → NetworkCredential with nulls; `int.Parse` has ?? "25" so OK. Report username/password null risk.
- `UserController.UpdateUser`: `request` model-bound — if body invalid/missing, [ApiController] handles null? With [ApiController], model binding ensures non-null for reference types? Actually for [FromBody] with ApiController attribute, null body results in 400 automatically? No — [ApiController] infers validation but a null JSON body ("null") can produce null request. Actually with [ApiController], if body can't be bound, it returns 400. But `null` literal JSON would bind to null request. Then request.Email → NRE. The prompt explicitly mentions "model-bound request objects used in controller actions without a null check". Report for UpdateUser, Transfer (request.ToUserId), Deposit, Login. Hmm — Login uses request.Username. I'll report the pattern for each action: Login, Transfer, Deposit, UpdateUser. Maybe one row each. Let me include them.
- `TransactionService.Transfer`: `description` interpolated into SQL — if null, `'{null}'` becomes `''`... actually `$"{description}"` with null gives empty string. Fine.
- `UserService.MapRowToUser`: doesn't map LastLoginAt — minor, not null ref.
- `AuthService.Login` reader indexing — if columns null... skip.

### 6. Dead Code

Step 1: List every method defined:

**AuthController:** Login (action).
**TransactionController:** Transfer, Deposit, Refund (actions).
**UserController:** GetUser, GetUsers, UpdateUser, DeleteUser, SearchUsers, GetAuditLog.
**DatabaseHelper:** ctor, GetOpenConnection, ExecuteQuery, ExecuteQuerySafe, ExecuteNonQuery, TableExists, ExecuteQueryWithParams.
**StringHelper:** IsValidEmail, IsValidUsername, JoinWithSeparator, JoinWithSeparatorFixed, MaskAccountNumber, ObfuscateAccount, ToTitleCase, IsBlank.
**AuthService:** ctor, Login, HashPasswordMd5 (private), GenerateJwtToken, HashPasswordSha1 (private), ValidateToken.
**EmailService:** ctor, SendTransferNotification, SendWelcomeEmail, BuildHtmlTemplate (private), SendWelcomeEmailHtml.
**TransactionService:** ctor, Transfer, Deposit, IsWithinDailyLimit (private), RecordTransaction (private), FormatCurrency (private), RefundTransaction.
**UserService:** ctor, GetUserById, UpdateUser, DeleteUser, GetUsersPage, GetAuditReport, SearchUsers, MapRowToUser (private).

Step 2: scan for callers:

- AuthController.Login — endpoint, called via routing. Used.
- TransactionController.Transfer/Deposit/Refund — endpoints. Used.
- UserController methods — endpoints. Used.
- DatabaseHelper.GetOpenConnection — called by ExecuteQuery (line 28) and ExecuteNonQuery (line 52). Used.
- DatabaseHelper.ExecuteQuery — called by UserService.SearchUsers line 99. Used.
- DatabaseHelper.ExecuteQuerySafe — called by TransactionService (Transfer x2, IsWithinDailyLimit), UserService (GetUserById, GetUsersPage). Used.
- DatabaseHelper.ExecuteNonQuery — called by TransactionService (Transfer x2, Deposit, RecordTransaction), UserService (UpdateUser, DeleteUser). Used.
- DatabaseHelper.TableExists — search... no calls anywhere. DEAD. Report.
- DatabaseHelper.ExecuteQueryWithParams — [Obsolete], no callers. DEAD. Report.
- StringHelper.IsValidEmail — search: no calls (UserService.UpdateUser doesn't validate email!). DEAD. Report. (Also a bug: email never validated.)
- StringHelper.IsValidUsername — no calls. DEAD. Report.
- StringHelper.JoinWithSeparator — no calls. DEAD (and broken — trailing separator). Report.
- StringHelper.JoinWithSeparatorFixed — no calls. DEAD. Report.
- StringHelper.MaskAccountNumber — no calls. DEAD. Report.
- StringHelper.ObfuscateAccount — no calls. DEAD. Report.
- StringHelper.ToTitleCase — no calls. DEAD. Report.
- StringHelper.IsBlank — no calls. DEAD. Report.
- So the entire StringHelper class is unused. Report each method.
- AuthService.Login — called by AuthController. Used.
- HashPasswordMd5 — called by Login. Used.
- GenerateJwtToken — called by AuthController. Used.
- HashPasswordSha1 — no calls. DEAD. Report.
- ValidateToken — no calls. DEAD. Report (also broken: returns true unconditionally, code after return unreachable).
- EmailService.SendTransferNotification — called by TransactionService.Transfer. Used.
- EmailService.SendWelcomeEmail — no calls. DEAD. Report.
- EmailService.BuildHtmlTemplate — called by SendWelcomeEmailHtml. Used (but only by dead code — transitively dead). Report? It's called by SendWelcomeEmailHtml which itself is dead. I'll note SendWelcomeEmailHtml dead; BuildHtmlTemplate only called from dead code — transitively dead. Report as transitively unused.
- EmailService.SendWelcomeEmailHtml — no calls. DEAD. Report.
- TransactionService.Transfer — used by controller. Used.
- Deposit — used. Used.
- IsWithinDailyLimit — no calls. DEAD. Report (daily limit never enforced).
- RecordTransaction — called by Transfer and Deposit. Used.
- FormatCurrency — no calls. DEAD. Report.
- RefundTransaction — called by controller Refund. Used (but throws NotImplementedException).
- UserService.GetUserById — used. UpdateUser — used. DeleteUser — used. GetUsersPage — used. GetAuditReport — used (GetAuditLog). SearchUsers — used. MapRowToUser — used.

Also:
- Code after unconditional return: AuthService.ValidateToken lines 105-107 unreachable. Report.
- [Obsolete] ExecuteQueryWithParams still present. Report.
- throw new NotImplementedException in RefundTransaction (non-stub code — it's a live endpoint). Report.
- Duplicate implementations: JoinWithSeparator (broken) vs JoinWithSeparatorFixed — both dead though. MaskAccountNumber vs ObfuscateAccount duplicates. Report as duplicates.
- `AdminBypassPassword` const — used in Login. Used.
- `MaxTransactionsPerDay` — used only in dead IsWithinDailyLimit. Const, not method. Mention.
- `WelcomeSubject`, `TransferSubject` used. `MaxRetries`, `SmtpTimeoutMs` used.
- `TransactionFeeRate` used.
- `HashPasswordSha1` dead.
- `_requestCount` in UserService — incremented but never read. Dead field. Report.
- `EmailService._config` — used in ctor only. Fine.
- `Models`: Transaction class — is it used anywhere? Transaction model is never referenced (RecordTransaction writes raw SQL; no mapping to Transaction). Search: "Transaction" as type — TransactionService uses TransferRequest, DepositRequest. The `Transaction` class itself is never instantiated/used. DEAD type. Report.
- `User.LastLoginAt` — never set/read (MapRowToUser doesn't map it; AuthService doesn't update it). Dead property. Report maybe.
- `Transaction.Type/Status` etc. — part of dead class.
- `LoginRequest` used. `UpdateUserRequest` used. `TransferRequest`, `DepositRequest` used.

### 7. Magic Strings and Numbers

- `DatabaseHelper` line 16: hardcoded fallback connection string with credentials (also security). Magic/config value.
- `AuthService` line 17: `AdminBypassPassword = "SuperAdmin2024"` — hardcoded (security).
- `AuthService.Login` line 53: `username == "admin"` magic string; `"SuperAdmin"` role magic string (line 55).
- `AuthService.GenerateJwtToken` line 84: `DateTime.UtcNow.AddDays(30)` — 30-day token lifetime magic number.
- `TransactionService` line 11: TransactionFeeRate 0.015 — actually a named const, good. But fee rate hardcoded rather than config — borderline. The prompt says values that belong in configuration. I could report fee rate should be config. Eh, it's a named constant; I'll note it as config candidate lightly. Maybe skip to avoid noise? The category says "numeric literals used inline without a named constant" — TransactionFeeRate is named. Skip. But `0.05m * 1` in Deposit line 68 is inline magic — 5% interest rate inline. Report.
- `TransactionService.Deposit` line 65: `amount > 1000000` — deposit cap inline magic number. Report.
- `MaxTransactionsPerDay = 10` — named const, fine (but unused).
- `UserService.GetUserById` lines 22-23: `1000000` magic number for ID range. Report.
- `UserService.UpdateUser` lines 42-43: `1000000` again. Report.
- `UserService.DeleteUser` lines 56-57: `1000000` again. Report.
- `UserService.GetUsersPage` line 70: `pageSize > 50` → 50 magic number (max page size). Report.
- `StringHelper.IsValidEmail` line 13: `254` magic number (max email length). Report.
- `StringHelper.IsValidUsername` line 22: `3` and `20` magic numbers. Report.
- `StringHelper.MaskAccountNumber` line 45: `4` magic number (visible digits). Report.
- `StringHelper.ObfuscateAccount` line 56: `4` and `"****"` magic. Report.
- `EmailService` line 40, 67, 69, 89: `"notifications@company.com"` repeated 4 times — magic string repeated. Report (one row per occurrence or one row noting repetition? Prompt says each occurrence its own row. I'll list each line).
- `EmailService` line 67: `"support@company.com"` inline. Report.
- `EmailService` line 24: `?? "25"` default port magic. Report.
- Role names: `"SuperAdmin"` (AuthService line 55); role checks nowhere else. `"Completed"` status in RecordTransaction line 90 magic string. `"Transfer"`, `"Deposit"` type strings lines 50, 73. Report.
- Config keys: `"Jwt:SecretKey"` appears in Program.cs line 16 and AuthService line 70 — repeated config key strings. Report.
- `"DefaultConnection"` in DatabaseHelper line 15 and AuthService line 34 — repeated. Report.
- `Email:SmtpHost` etc. — used once each. Fine.
- `TransactionService.Deposit` line 73: `RecordTransaction(0, userId, ...)` — 0 sentinel magic number. Report.
- `Program.cs` — nothing numeric.
- `appsettings.json` — secrets (covered elsewhere).

### 8. Anti-patterns and Code Quality

- `StringHelper.JoinWithSeparator` lines 31-34: string concatenation in loop O(n²). Report.
- `UserService.GetAuditReport` lines 87-92: string concatenation in loop. Report.
- `StringHelper.IsValidEmail` line 16: `new Regex` inside method — should be static readonly/compiled. Report.
- `StringHelper.IsValidUsername` line 25: same. Report.
- `UserService` lines 10-11: `static List<string> _auditLog` and `static int _requestCount` — shared mutable static state without lock; also unbounded growth (memory leak). Report both.
- `StringHelper.IsBlank` lines 65-71: reimplements `string.IsNullOrWhiteSpace`. Report.
- `StringHelper.JoinWithSeparatorFixed` duplicates `string.Join`. Report.
- `StringHelper.ObfuscateAccount` duplicates `MaskAccountNumber`. Report.
- `DatabaseHelper.GetOpenConnection`: leaks resource ownership to callers with no documented contract. Report.
- `EmailService`: `Console.WriteLine` instead of ILogger (lines 56, 77). Report.
- `EmailService` retry loop: no backoff delay between retries. Report.
- `EmailService.SendWelcomeEmailHtml`: HTML injection — username inserted into HTML unescaped (BuildHtmlTemplate). Report (security-ish; XSS in email). Could put in security. I'll put in security or anti-patterns. It's HTML injection in email body — I'll add to security as minor.
- Duplicated validation logic: the `id <= 0` / `id > 1000000` block repeated in GetUserById, UpdateUser, DeleteUser — report once per method (3 rows). Prompt: "report it once per method that repeats the block, naming each."
- Duplicated user-fetch-by-id logic in TransactionService.Transfer (two identical ExecuteQuerySafe calls) — could be extracted. Report as refactoring.
- `AuthService.Login` builds its own SqlConnection instead of using DatabaseHelper — duplication/inconsistency. Report.
- `UserService.GetUsersPage` uses `System.Data.DataRow` fully qualified instead of using directive — style. Minor; maybe skip. Could mention.
- Refactoring opportunities (3+ responsibilities):
  - `TransactionService.Transfer`: responsibilities — validate input, load users, compute fee, check balance, persist two updates, record transaction, send email. Should be split. Report.
  - `AuthService.Login`: DB auth + bypass backdoor + user mapping. Report.
  - `EmailService.SendTransferNotification`: message construction + retry loop + sending. Report.
  - `UserService.SearchUsers`: query + mapping + swallow. Eh.
  - `Program.cs` — fine.
- `TransactionController.Refund` catches NotImplementedException — swallowing pattern. Report in error handling maybe.
- `UserService._requestCount` incremented but never used — dead field (category 6).
- `TreatWarningsAsErrors false` — minor; skip or mention in config.
- `Newtonsoft.Json 12.0.3` package — is it even used? No using Newtonsoft anywhere. Unused package reference + outdated/vulnerable (12.0.3 has known vulns CVE-2020-11608? Actually 12.0.3 fixed some; 13.0.1 fixed CVE-2021-40257? There are known vulns in Newtonsoft < 13.0.1). Report in config/packages: unused + vulnerable.
- `System.IdentityModel.Tokens.Jwt 7.0.0` vs JwtBearer 8.0.0 — version mismatch (JwtBearer 8.0.0 depends on 7.x actually; JwtBearer 8.0.0 depends on System.IdentityModel.Tokens.Jwt 7.0.3). Explicit 7.0.0 pin could conflict. Report as potential version conflict.
- `System.Data.SqlClient 4.8.6` — deprecated package (Microsoft.Data.SqlClient is successor). Report in config.
- `DebugType full` — config category.

### 9. Configuration Issues

- Program.cs line 34: `UseDeveloperExceptionPage()` unconditional. Report.
- Program.cs line 24: `ValidateLifetime = false`. Report (also security; keep in both? The prompt lists it under security too. I'll include in security and config — better to include in both since categories overlap; the instructions say work every category. I'll include in both.)
- Program.cs line 36: HTTPS redirection commented out. Report.
- Program.cs line 38: permissive CORS AllowAnyOrigin/Method/Header. Report (also security).
- appsettings.json Logging: Debug level for Default/Microsoft/System — debug log levels in production config (no appsettings.Production.json override). Report.
- Missing `appsettings.Production.json`. Report.
- appsettings.json: production connection string `prod-db.internal` with sa credentials committed. Report (also security).
- csproj: DebugSymbols true, DebugType full. Report.
- csproj: Newtonsoft.Json 12.0.3 — outdated, known vulnerabilities, and unused. Report.
- csproj: System.Data.SqlClient 4.8.6 — legacy/deprecated package. Report.
- csproj: System.IdentityModel.Tokens.Jwt 7.0.0 pinned alongside JwtBearer 8.0.0 — version mismatch. Report.
- csproj: TreatWarningsAsErrors false — minor. Report maybe.
- No CORS policy named/registered via AddCors — using inline app.UseCors with policy lambda; works but unusual. Skip.
- JWT secret "mysecretkey" in config — weak secret (also security). Report in config too.
- Email EnableSsl false with port 25 — credentials in cleartext. Report (security/config).
- `AllowedHosts: "*"` — permissive. Minor. Report.

### 10. Missing Unit Tests

No test project in the source files (no .csproj for tests). List critical methods/scenarios:
- TransactionService.Transfer: boundary conditions (amount 0, negative, exactly balance, balance vs balance+fee, self-transfer, nonexistent users), fee calculation.
- TransactionService.Deposit: 0, negative, cap boundary 1000000, interest bonus math.
- UserService.GetUsersPage: pagination off-by-one (page 1, page 2, pageSize 0, negative).
- AuthService.Login: valid/invalid credentials, SQL injection attempts, bypass backdoor, inactive user.
- AuthService.GenerateJwtToken: claims, expiry.
- StringHelper methods: email/username validation boundaries, masking.
- UserService.GetUserById: id boundaries (0, 1, 1000000, 1000001).
- UpdateUser/DeleteUser: validation, non-existent user.
- SearchUsers: normal, error path (currently swallowed).

I'll present as a table with rows per method/scenario.

Now let me also double-check some line numbers:

**AuthController.cs:**
- Line 22: Login action calls service. Line 26: returns Unauthorized with message. No rate limiting — line 19-31.

**TransactionController.cs:**
- Line 27: `int.Parse(userIdClaim!)`.
- Line 41: `int.Parse(userIdClaim!)`.
- Line 49-59: Refund.

**UserController.cs:**
- Line 22-29 GetUser: no ownership check (line 21-29).
- Line 32-36 GetUsers.
- Line 38-54 UpdateUser: no ownership check; line 48 `BadRequest(ex.Message)`; line 52 `StatusCode(500, ex.Message)`.
- Line 56-69 DeleteUser: no ownership check.
- Line 71-76 SearchUsers.
- Line 78-82 GetAuditLog: no admin check.

**DatabaseHelper.cs:**
- Line 15-17: fallback connection string.
- Line 19-24: GetOpenConnection.
- Line 26-34: ExecuteQuery — injection; connection leak (line 28).
- Line 36-48: ExecuteQuerySafe — OK-ish; adapter not disposed (line 44).
- Line 50-57: ExecuteNonQuery — raw SQL; connection not disposed; Close skipped on exception (line 54-55).
- Line 59-65: TableExists — dead.
- Line 67-78: ExecuteQueryWithParams — obsolete, dead; adapter not disposed (line 74).

**StringHelper.cs:**
- Line 11-18 IsValidEmail: null risk line 13; regex line 16; magic 254 line 13.
- Line 20-27 IsValidUsername: null risk line 22; magic 3/20 line 22; regex line 25.
- Line 29-36 JoinWithSeparator: O(n²) line 33; trailing separator; dead.
- Line 38-41 JoinWithSeparatorFixed: dead; duplicates string.Join.
- Line 43-52 MaskAccountNumber: dead; null risk line 45; magic 4.
- Line 54-57 ObfuscateAccount: dead; range error for short strings line 56; duplicate of MaskAccountNumber.
- Line 59-63 ToTitleCase: dead.
- Line 65-71 IsBlank: dead; reimplements IsNullOrWhiteSpace.

**AuthService.cs:**
- Line 17: AdminBypassPassword const.
- Line 28-59 Login: SQL injection line 32; connection/reader leak lines 34-38; MD5 line 30/61-66; backdoor lines 53-56; no lockout.
- Line 61-66 HashPasswordMd5.
- Line 68-89 GenerateJwtToken: null secret line 70; 30-day expiry line 84.
- Line 91-96 HashPasswordSha1: dead, SHA1.
- Line 98-108 ValidateToken: dead; unconditional return true line 103; unreachable code lines 105-107.

**EmailService.cs:**
- Line 16: SmtpClient field.
- Line 22-31: ctor — SmtpClient as field, EnableSsl false line 29, null config line 26-27, port default line 24.
- Line 34-61 SendTransferNotification: MailMessage not disposed line 39; retry no backoff; Console.WriteLine line 56.
- Line 63-79 SendWelcomeEmail: dead; MailMessage not disposed line 69; catch swallow lines 75-78; Console.WriteLine line 77.
- Line 81-84 BuildHtmlTemplate: HTML injection (unescaped interpolation) line 83; transitively dead.
- Line 86-92 SendWelcomeEmailHtml: dead; MailMessage not disposed line 89; HTML injection via username.

**TransactionService.cs:**
- Line 11: TransactionFeeRate const (fine).
- Line 23-61 Transfer: amount < 0 line 25 (should be <= 0); Rows[0] lines 36-37; balance check line 42 excludes fee; no self-transfer check; interpolated UPDATEs lines 47-48; no transaction; email after commit line 52; fee not recorded.
- Line 63-75 Deposit: cap 1000000 line 65; 5% bonus line 68; interpolated UPDATE line 70-71; no existence check; no transaction; FromUserId 0 line 73.
- Line 77-85 IsWithinDailyLimit: dead; daily limit not enforced.
- Line 87-92 RecordTransaction: SQL injection via description line 90; type/status magic strings.
- Line 94-97 FormatCurrency: dead.
- Line 99-103 RefundTransaction: NotImplementedException.

**UserService.cs:**
- Line 10-11: static mutable state.
- Line 18-36 GetUserById: magic 1000000 lines 22-23; _requestCount line 25.
- Line 38-50 UpdateUser: SQL injection line 47; magic 1000000 lines 42-43; no email/username validation (IsValidEmail unused); returns true regardless.
- Line 52-66 DeleteUser: SQL line 61; magic 1000000; returns true regardless.
- Line 68-83 GetUsersPage: off-by-one line 72; magic 50 line 70; no page/pageSize lower-bound validation.
- Line 85-93 GetAuditReport: concat in loop line 90.
- Line 95-109 SearchUsers: SQL injection line 99; catch swallow lines 105-108.
- Line 111-123 MapRowToUser: doesn't map LastLoginAt (minor).

**Program.cs:**
- Line 16: jwtSecret possibly null.
- Line 24: ValidateLifetime = false.
- Line 28: GetBytes(jwtSecret!).
- Line 34: UseDeveloperExceptionPage.
- Line 36: HTTPS commented.
- Line 38: CORS.

**csproj:**
- Lines 8-9: DebugSymbols/DebugType.
- Line 15: Newtonsoft 12.0.3.
- Line 14: SqlClient 4.8.6.
- Line 16: Jwt 7.0.0.

**appsettings.json:**
- Line 3: prod connection string with creds.
- Line 6: weak JWT secret.
- Lines 13-14: email creds.
- Lines 17-21: Debug log levels.

Now, the output format: Markdown report, one `##` section per category, tables with columns | File | Line | Issue | Fix |. Each cell one sentence. Each occurrence its own row.

Let me now write the report carefully. I need to be thorough but each cell one sentence.

Let me draft each section.

### 1. Security Vulnerabilities

Rows:
1. AuthService.cs | 32 | SQL injection in `Login` — username and hashed password interpolated directly into the SELECT statement. | Use parameterized queries via ExecuteQuerySafe with @Username/@Password parameters.
2. AuthService.cs | 53-56 | Hardcoded backdoor: username "admin" with const password "SuperAdmin2024" grants a SuperAdmin user. | Remove the bypass entirely and authenticate only against the database.
3. AuthService.cs | 17 | Hardcoded credential `AdminBypassPassword = "SuperAdmin2024"` in source. | Delete the constant and any code that references it.
4. AuthService.cs | 30, 61-66 | Passwords hashed with unsalted MD5. | Use a modern KDF such as PBKDF2/ASP.NET Core's PasswordHasher with salt and iterations.
5. AuthService.cs | 91-96 | `HashPasswordSha1` uses unsalted SHA1. | Remove it (it is unused) and never use SHA1 for passwords.
6. Program.cs | 24 | `ValidateLifetime = false` means expired JWTs are accepted forever. | Set ValidateLifetime = true.
7. Program.cs | 28 | JWT signing key read from config with null-forgiving `!` and the configured secret "mysecretkey" is trivially short/weak. | Enforce a minimum 256-bit secret from a secret store and fail startup if missing.
8. appsettings.json | 6 | Weak JWT secret "mysecretkey" committed to source control. | Move to environment/secret manager and rotate.
9. appsettings.json | 3 | Production DB connection string with sa account and password committed. | Remove secrets from the repo, use managed identity or env vars, rotate credentials.
10. appsettings.json | 14 | SMTP password "EmailPass99" committed. | Move to secret storage and rotate.
11. DatabaseHelper.cs | 16 | Fallback connection string hardcodes sa credentials "Admin1234!". | Remove the fallback and throw if the connection string is missing.
12. DatabaseHelper.cs | 26-29 | `ExecuteQuery` builds SQL by interpolating `tableName` and `whereClause` — injection by design. | Remove the method or rewrite to accept a fixed table name and parameterized filters.
13. DatabaseHelper.cs | 50-53 | `ExecuteNonQuery` executes arbitrary raw SQL strings. | Change to accept parameterized SQL with a parameters dictionary.
14. UserService.cs | 47 | SQL injection in `UpdateUser` — email and username interpolated into UPDATE. | Use ExecuteQuerySafe-style parameters.
15. UserService.cs | 61 | `DeleteUser` interpolates id into DELETE (int-typed today, but the pattern invites injection). | Use a parameterized command.
16. UserService.cs | 99 | SQL injection in `SearchUsers` — query interpolated into LIKE clause, also allows wildcard injection. | Use a parameterized LIKE with escaped wildcards.
17. TransactionService.cs | 47 | `Transfer` interpolates balances and ids into UPDATE SQL. | Use parameterized UPDATE statements.
18. TransactionService.cs | 48 | Second interpolated UPDATE for recipient balance. | Parameterize.
19. TransactionService.cs | 70-71 | `Deposit` interpolates amount into UPDATE. | Parameterize.
20. TransactionService.cs | 89-91 | `RecordTransaction` interpolates user-supplied `description` into INSERT — direct SQL injection from the transfer endpoint. | Use a parameterized INSERT.
21. UserController.cs | 38-54 | `UpdateUser` (PUT) has no ownership or role check — any authenticated user can modify any account. | Compare the route id to the NameIdentifier claim or require an admin role.
22. UserController.cs | 56-69 | `DeleteUser` has no ownership/admin check — any user can delete any account. | Require admin role and verify ownership.
23. UserController.cs | 21-29 | `GetUser` lets any authenticated user read any other user's record including balance (IDOR). | Restrict to self or admin.
24. UserController.cs | 31-36 | `GetUsers` exposes the full user list to any authenticated user with no admin restriction. | Add [Authorize(Roles = "Admin")].
25. UserController.cs | 78-82 | `GetAuditLog` exposes audit data to any authenticated user. | Restrict to admin role.
26. TransactionController.cs | 48-59 | `Refund` performs no ownership check on transactionId. | Verify the transaction belongs to the caller (or admin) before refunding.
27. Program.cs | 38 | CORS allows any origin, method, and header. | Restrict to known origins with a named policy.
28. Program.cs | 34 | `UseDeveloperExceptionPage()` called unconditionally — stack traces leak in production. | Gate on app.Environment.IsDevelopment().
29. Program.cs | 36 | HTTPS redirection commented out. | Re-enable app.UseHttpsRedirection().
30. SampleBankingApp.csproj | 8-9 | DebugSymbols and full DebugType enabled for all builds. | Set to embedded/portable and only in Debug.
31. EmailService.cs | 29 | EnableSsl = false sends SMTP credentials in cleartext. | Enable SSL and use port 587.
32. EmailService.cs | 83 | `BuildHtmlTemplate` interpolates title/body into HTML unescaped — HTML injection via username. | HTML-encode all interpolated values.
33. AuthController.cs | 19-31 | Login endpoint has no rate limiting or account lockout — enables brute force. | Add rate limiting middleware and temporary lockout after failures.
34. appsettings.json | 3 | TrustServerCertificate=True disables DB TLS validation. | Use a trusted certificate and remove the flag.

That's a good list. Maybe also: no role-based authorization anywhere (covered by rows 21-25). Also `AuthService.ValidateToken` always returns true — but it's dead code; mention in security? It's dead so not exploitable via current call graph. I'll cover in dead code and logic.

### 2. Logic Errors

1. UserService.cs | 72 | `GetUsersPage` computes `skip = page * pageSize` — page 1 skips the first pageSize rows (off-by-one). | Use (page - 1) * pageSize.
2. TransactionService.cs | 42-44 | Balance check `fromBalance >= amount` ignores the fee, but `totalDebit = amount + fee` is deducted — can drive balance negative. | Check fromBalance >= totalDebit.
3. TransactionService.cs | 25 | `amount < 0` allows zero-amount transfers. | Use amount <= 0.
4. TransactionService.cs | 23 | No check that fromUserId != toUserId — self-transfers double-charge the fee. | Reject self-transfers.
5. TransactionService.cs | 68 | Deposit grants a 5% "interestBonus" on every deposit (`amount * 0.05m * 1`) — the `* 1` is a no-op and 5% per deposit is almost certainly the wrong rate. | Remove or correct the bonus rate and compute it in one clear expression.
6. TransactionService.cs | 39-48 | The fee is deducted from the sender but never recorded or credited anywhere — money disappears from the system. | Record the fee on the transaction row or credit a fee account.
7. TransactionService.cs | 63-75 | `Deposit` never verifies the user exists — UPDATE affects 0 rows but a transaction is still recorded and success returned. | Check rows affected and fail if the user is missing.
8. TransactionService.cs | 23-61 | `Transfer` never verifies from/to users exist before `Rows[0]` access. | Check table.Rows.Count before indexing.
9. TransactionService.cs | 77-85 | `IsWithinDailyLimit` is never called, so MaxTransactionsPerDay is not enforced. | Call it in Transfer (and Deposit) and reject when over limit.
10. UserService.cs | 68-76 | `GetUsersPage` does not validate page >= 1 or pageSize >= 1 — page 0 duplicates page 1 and negative values produce invalid SQL. | Clamp page and pageSize to minimums.
11. AuthService.cs | 98-108 | `ValidateToken` returns true unconditionally without inspecting the token. | Remove the early return and validate signature and expiry.
12. StringHelper.cs | 29-36 | `JoinWithSeparator` appends the separator after the final item, producing a trailing separator. | Use string.Join.
13. StringHelper.cs | 56 | `ObfuscateAccount` uses `account[^4..]` which throws for strings shorter than 4 characters. | Guard length <= 4 first.
14. UserService.cs | 38-50 | `UpdateUser` returns true even when the id matches no row. | Check rows affected and return false when 0.
15. UserService.cs | 52-66 | `DeleteUser` returns true even when nothing was deleted. | Check rows affected.
16. TransactionService.cs | 36-37 | Transfer reads balances then writes them back with no locking — concurrent transfers can lose updates (race). | Use optimistic concurrency or SELECT ... WITH (UPDLOCK) inside a transaction.
17. AuthService.cs | 55 | Backdoor user has Id = 0, which cannot match any real account, so its tokens reference a nonexistent user. | (Remove the backdoor — see security.)
18. UserService.cs | 111-123 | `MapRowToUser` never maps LastLoginAt and nothing updates it on login. | Update LastLoginAt on successful login and map it.

Hmm, 17 is a consequence of the backdoor; keep it brief. Also maybe: `GetUsersPage` clamps pageSize > 50 but not the default 20 — fine.

Also `TransactionController.Refund` returns 500 for NotImplementedException — that's error handling.

Also `EmailService` retry loop — if attempt reaches MaxRetries it throws; fine.

Also `Deposit` cap: `amount > 1000000` — boundary fine.

Also `GetUserById` id > 1000000 throws — arbitrary; magic number category.

### 3. Error Handling

1. UserService.cs | 97-108 | `SearchUsers` catches all exceptions and returns an empty list — callers cannot distinguish "no results" from "database down". | Let exceptions propagate or return a result type with status.
2. EmailService.cs | 71-78 | `SendWelcomeEmail` catches Exception and only Console.WriteLine — failures vanish. | Log via ILogger and surface or queue failures.
3. EmailService.cs | 56 | Retry logging uses Console.WriteLine instead of ILogger. | Inject and use ILogger<EmailService>.
4. TransactionService.cs | 47-55 | The two balance UPDATEs and the INSERT are not wrapped in a transaction — a failure between them leaves inconsistent balances. | Wrap in a single SqlTransaction.
5. TransactionService.cs | 70-73 | Deposit's UPDATE and RecordTransaction INSERT are not atomic. | Same transaction.
6. TransactionService.cs | 50-55 | `SendTransferNotification` runs after the DB writes — if email throws, the client gets an error although the transfer committed. | Send email after responding (background queue) or make it non-throwing.
7. UserController.cs | 50-52 | `UpdateUser` catch-all returns ex.Message to the client — leaks internals. | Return a generic message and log the exception.
8. UserController.cs | 46-48 | `UpdateUser` returns raw ArgumentException messages to clients. | Map validation errors to model validation instead.
9. UserController.cs | 21-29 | `GetUser` has no try/catch, so the ArgumentException thrown by GetUserById becomes an unhandled 500 (with developer page details). | Validate input in the controller and return 400/404.
10. AuthController.cs | 19-31 | No rate limiting or lockout on login. | (Also listed in security — keep here too? It's listed in both categories' checklists. I'll include in both.)
11. TransactionController.cs | 27 | `int.Parse(userIdClaim!)` — a malformed/missing claim throws FormatException/NullReferenceException and returns an unhandled 500. | Use int.TryParse and return 401.
12. TransactionController.cs | 41 | Same for Deposit. | Same fix.
13. TransactionController.cs | 56-58 | Refund maps NotImplementedException to a 500 — a permanent "not implemented" should be 501 or the endpoint removed. | Return 501 Not Implemented or remove the route.
14. AuthService.cs | 28-59 | `Login` has no handling for SqlException — DB outages surface as raw 500s. | Catch SqlException and return a generic 503.
15. EmailService.cs | 45-60 | Retry loop has no delay between attempts, hammering the SMTP server. | Add exponential backoff between retries.

### 4. Resource Leaks

1. DatabaseHelper.cs | 28-33 | `ExecuteQuery` never closes or disposes the SqlConnection, SqlCommand, or SqlDataAdapter returned from GetOpenConnection. | Wrap all three in using statements.
2. DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` calls Close but never Dispose, and Close is skipped if ExecuteNonQuery throws. | Use `using` on connection and command.
3. DatabaseHelper.cs | 19-24 | `GetOpenConnection` hands an open connection to callers with no disposal contract. | Return a connection the caller must dispose, or make the helper own it.
4. AuthService.cs | 34-38 | `Login` creates SqlConnection, SqlCommand, and SqlDataReader that are never closed or disposed on any path. | Wrap in using statements.
5. EmailService.cs | 16, 22 | SmtpClient held as an instance field for the service lifetime — never disposed and not thread-safe. | Create SmtpClient per send in a using block, or use a pooled/factory approach.
6. EmailService.cs | 39-43 | MailMessage in `SendTransferNotification` is never disposed. | using var message = ...
7. EmailService.cs | 69 | MailMessage in `SendWelcomeEmail` never disposed. | using.
8. EmailService.cs | 89 | MailMessage in `SendWelcomeEmailHtml` never disposed. | using.
9. DatabaseHelper.cs | 44 | SqlDataAdapter in `ExecuteQuerySafe` is not disposed. | Wrap the adapter in using.
10. DatabaseHelper.cs | 74 | SqlDataAdapter in `ExecuteQueryWithParams` not disposed. | using.

### 5. Null Reference Risks

1. Program.cs | 16, 28 | `jwtSecret` from configuration passed to Encoding.UTF8.GetBytes with `!` — null if the key is missing, crashing startup with an opaque error. | Validate at startup and fail fast with a clear message.
2. AuthService.cs | 70 | `GenerateJwtToken` uses `_config["Jwt:SecretKey"]!` — same null risk. | Same fix.
3. TransactionController.cs | 26-27 | `User.FindFirst(...)?.Value` then `int.Parse(userIdClaim!)` — null claim causes NullReferenceException. | int.TryParse with 401 on failure.
4. TransactionController.cs | 40-41 | Same pattern in Deposit. | Same fix.
5. TransactionService.cs | 36 | `fromUserTable.Rows[0]` accessed without checking Rows.Count — throws IndexOutOfRangeException when the sender does not exist. | Check Rows.Count == 0 and return a "user not found" failure.
6. TransactionService.cs | 37 | Same for `toUserTable.Rows[0]`. | Same fix.
7. StringHelper.cs | 13 | `IsValidEmail` dereferences `email.Length` with no null check. | Add a null guard or make the parameter nullable-checked.
8. StringHelper.cs | 22 | `IsValidUsername` dereferences `username.Length` with no null check. | Same.
9. StringHelper.cs | 45 | `MaskAccountNumber` dereferences `accountNumber.Length` with no null check. | Same.
10. StringHelper.cs | 56 | `ObfuscateAccount` indexes `account[^4..]` without a null or length check. | Guard null and length < 4.
11. EmailService.cs | 25-27 | `_config["Email:Username"]` and Password may be null and are passed to NetworkCredential. | Validate config at startup.
12. UserController.cs | 39 | `UpdateUser` uses `request.Email`/`request.Username` without a null check on the model-bound body. | Add [Required] attributes and null-check.
13. AuthController.cs | 20-22 | `Login` uses `request.Username`/`request.Password` without a null check on the bound request. | Add [Required] and validate.
14. TransactionController.cs | 24-29 | `Transfer` uses request.ToUserId/Amount/Description without a null check on the request object. | Add [Required] and validate.
15. TransactionController.cs | 38-43 | `Deposit` uses request.Amount without a null check on the request object. | Same.

Hmm, for [ApiController], null JSON body → request null? Actually with [ApiController], a missing body gives 400 automatically. A body of "null" gives... For reference types, "null" JSON binds to null and [ApiController] doesn't reject unless nullable validation... In .NET 8, non-nullable reference types on models are treated as required by default in minimal APIs but for MVC controllers, [ApiController] enforces non-null model state? Actually ASP.NET Core 9 added disallow null for non-nullable. In .NET 8 MVC, a JSON "null" body results in null model without error. So it's a legit risk. Keep rows.

### 6. Dead Code

I need to list every method and report unused ones. Let me present the working list briefly then the table. The output format says within each section use a table. I can add a short preamble sentence maybe. The instructions say "Within each section use a Markdown table" — I can include a brief note plus the table. I'll keep it mostly table.

Unused methods:
1. DatabaseHelper.TableExists — no callers.
2. DatabaseHelper.ExecuteQueryWithParams — [Obsolete], no callers.
3. StringHelper.IsValidEmail — no callers (and email is never validated in UpdateUser).
4. StringHelper.IsValidUsername — no callers.
5. StringHelper.JoinWithSeparator — no callers.
6. StringHelper.JoinWithSeparatorFixed — no callers.
7. StringHelper.MaskAccountNumber — no callers.
8. StringHelper.ObfuscateAccount — no callers.
9. StringHelper.ToTitleCase — no callers.
10. StringHelper.IsBlank — no callers.
11. AuthService.HashPasswordSha1 — no callers.
12. AuthService.ValidateToken — no callers.
13. EmailService.SendWelcomeEmail — no callers.
14. EmailService.SendWelcomeEmailHtml — no callers.
15. EmailService.BuildHtmlTemplate — only called by dead SendWelcomeEmailHtml (transitively dead).
16. TransactionService.IsWithinDailyLimit — no callers.
17. TransactionService.FormatCurrency — no callers.
18. TransactionService.RefundTransaction — called, but throws NotImplementedException (report as non-stub NotImplemented).
19. Models/Transaction class — never referenced.
20. UserService._requestCount — incremented, never read.
21. User.LastLoginAt — never assigned or read.
22. AuthService.ValidateToken lines 105-107 — unreachable code after unconditional return.
23. Duplicate implementations: JoinWithSeparator vs JoinWithSeparatorFixed; MaskAccountNumber vs ObfuscateAccount — both pairs dead.
24. MaxTransactionsPerDay const only referenced by dead IsWithinDailyLimit — effectively dead.

Also `EmailService._config` — used in ctor. Fine.

Also `DatabaseHelper.ExecuteQuery` — used by SearchUsers. Used.

Also check `GetOpenConnection` — used internally. Fine.

Also `LoginRequest`, `UpdateUserRequest`, `TransferRequest`, `DepositRequest` — used.

Also `User.Password` property — set nowhere except default; Login doesn't map Password. It's mapped? Login's user mapping doesn't include Password. User.Password is never set from DB. Dead-ish property but it's a model property; skip or mention. I'll mention LastLoginAt only. Actually Password property never populated — could note. I'll skip to avoid over-reach; or include as minor. I'll include LastLoginAt and skip Password... Actually Password being never populated is notable: any code that relied on user.Password would get empty. But no code uses it. I'll add a row for User.Password too? Hmm. MapRowToUser doesn't map Password or LastLoginAt. I'll add one row noting both unmapped properties. Let me do: User.cs | 7, 13 | Password and LastLoginAt are never populated by any mapping code. That merges two — better separate rows per prompt ("Give every occurrence its own row"). I'll do two rows.

### 7. Magic Strings and Numbers

1. DatabaseHelper.cs | 16 | Hardcoded fallback connection string (belongs in configuration, and contains credentials). | Remove.
2. AuthService.cs | 17 | Backdoor password constant in source. | Remove.
3. AuthService.cs | 53 | Magic string "admin" for the bypass username. | Remove backdoor.
4. AuthService.cs | 55 | Magic role string "SuperAdmin". | Use a shared role constants class.
5. AuthService.cs | 84 | Token lifetime 30 days hardcoded via AddDays(30). | Move to configuration.
6. TransactionService.cs | 65 | Deposit cap 1000000 inline. | Named constant MaxDepositAmount in config.
7. TransactionService.cs | 68 | Interest rate 0.05m inline (with meaningless `* 1`). | Named constant/config DepositBonusRate.
8. TransactionService.cs | 73 | Sentinel FromUserId = 0 inline. | Named constant SystemUserId.
9. TransactionService.cs | 90 | Status literal 'Completed' inline. | Named constant or enum.
10. TransactionService.cs | 50, 73 | Type literals "Transfer"/"Deposit" inline. | TransactionType enum.
11. UserService.cs | 22-23 | Magic number 1000000 for max user id in GetUserById. | Named const MaxUserId shared.
12. UserService.cs | 42-43 | Same 1000000 in UpdateUser. | Same.
13. UserService.cs | 56-57 | Same in DeleteUser. | Same.
14. UserService.cs | 70 | Max page size 50 inline. | Named const MaxPageSize.
15. StringHelper.cs | 13 | Email max length 254 inline. | Named const MaxEmailLength.
16. StringHelper.cs | 22 | Username min 3 / max 20 inline. | Named constants.
17. StringHelper.cs | 45 | Visible digits count 4 inline. | Named const.
18. StringHelper.cs | 56 | "****" prefix and 4-char slice inline. | Named const.
19. EmailService.cs | 40 | "notifications@company.com" literal (first occurrence). | Named const or config SenderAddress.
20. EmailService.cs | 67 | "support@company.com" inline. | Config.
21. EmailService.cs | 69 | "notifications@company.com" repeated. | Same const.
22. EmailService.cs | 89 | "notifications@company.com" repeated again. | Same const.
23. EmailService.cs | 24 | Default SMTP port 25 inline. | Named const/config.
24. Program.cs | 16 / AuthService.cs | 70 | Config key "Jwt:SecretKey" duplicated as a string in two files. | Centralize in a constants/options class.
25. DatabaseHelper.cs | 15 / AuthService.cs | 34 | Connection string name "DefaultConnection" duplicated. | Centralize.
26. TransactionService.cs | 11 | Fee rate 1.5% hardcoded in source rather than configuration. | Move to appsettings. (It is a named const, but a business rate that changes; I'll include as config candidate.)

Hmm, TransactionFeeRate is a named constant — the category says "numeric literals used inline without a named constant" — it's named. But "values that belong in configuration but are hardcoded in source" — a transaction fee rate is a business/config value. I'll include it.

### 8. Anti-patterns and Code Quality

1. StringHelper.cs | 31-34 | `JoinWithSeparator` builds strings with += in a loop — O(n²). | Use string.Join.
2. UserService.cs | 87-92 | `GetAuditReport` concatenates in a loop — O(n²). | Use string.Join or StringBuilder.
3. StringHelper.cs | 16 | `new Regex` inside `IsValidEmail` on every call. | static readonly Regex or source-generated.
4. StringHelper.cs | 25 | `new Regex` inside `IsValidUsername` on every call. | Same.
5. UserService.cs | 10 | `static List<string> _auditLog` shared across requests with no synchronization and unbounded growth. | Use a thread-safe persistent audit store.
6. UserService.cs | 11 | `static int _requestCount` incremented from multiple threads without Interlocked. | Remove (never read) or use Interlocked.
7. StringHelper.cs | 65-71 | `IsBlank` reimplements string.IsNullOrWhiteSpace. | Delete and use the BCL method.
8. StringHelper.cs | 38-41 | `JoinWithSeparatorFixed` duplicates string.Join. | Delete.
9. StringHelper.cs | 54-57 | `ObfuscateAccount` duplicates `MaskAccountNumber` with different edge behavior. | Keep one implementation.
10. DatabaseHelper.cs | 19-24 | `GetOpenConnection` leaks ownership of an open connection to callers with no documented contract. | Have helpers own the connection lifetime.
11. EmailService.cs | 56, 77 | Console.WriteLine used for logging instead of ILogger. | Inject ILogger.
12. EmailService.cs | 45-60 | Retry loop retries immediately with no backoff. | Add delay/backoff.
13. UserService.cs | 20-23 | ID validation block (id <= 0 / id > 1000000) duplicated in GetUserById. | Extract shared ValidateUserId method.
14. UserService.cs | 40-43 | Same duplicated block in UpdateUser. | Same.
15. UserService.cs | 54-57 | Same duplicated block in DeleteUser. | Same.
16. AuthService.cs | 34 | `Login` builds its own SqlConnection instead of using the injected DatabaseHelper — two data-access paths. | Route through DatabaseHelper.
17. TransactionService.cs | 28-34 | Transfer duplicates the same load-user query twice inline. | Extract a private GetUserById helper.
18. TransactionService.cs | 23-61 | `Transfer` carries 7 responsibilities: validate, load users, compute fee, check funds, persist balances, record transaction, send email. | Split into ValidateRequest, LoadUsers, ApplyBalances (transactional), and Notify.
19. AuthService.cs | 28-59 | `Login` mixes DB authentication, backdoor check, and row mapping. | Extract MapUser(reader) and remove the backdoor.
20. EmailService.cs | 34-61 | `SendTransferNotification` mixes message construction, retry policy, and sending. | Extract BuildMessage and a SendWithRetry helper.
21. UserService.cs | 95-109 | `SearchUsers` mixes data access, mapping, and exception suppression. | Let exceptions propagate and reuse the mapping loop.
22. EmailService.cs | 81-84 | `BuildHtmlTemplate` builds HTML by string interpolation without encoding. | Use an HTML encoder or templating library. (Also in security — fine.)
23. TransactionController.cs | 51-59 | try/catch around NotImplementedException is a control-flow anti-pattern. | Remove endpoint until implemented.

Also `UserService.cs` line 79/101: `System.Data.DataRow` fully qualified — minor style; skip? I could add. I'll skip; enough rows.

Also `TreatWarningsAsErrors` false — config.

### 9. Configuration Issues

1. Program.cs | 34 | UseDeveloperExceptionPage unconditional. | Gate on environment.
2. Program.cs | 24 | ValidateLifetime = false. | true.
3. Program.cs | 36 | UseHttpsRedirection commented out. | Re-enable.
4. Program.cs | 38 | AllowAnyOrigin/AllowAnyMethod/AllowAnyHeader CORS. | Named policy with allowed origins.
5. appsettings.json | 17-21 | Debug log levels for Default, Microsoft, and System in the only config file. | Information/Warning in production.
6. (missing) | — | No appsettings.Production.json override exists. | Add environment-specific file.
7. appsettings.json | 3 | Production DB host (prod-db.internal) referenced in the base config with credentials. | Environment-specific config + secrets store.
8. SampleBankingApp.csproj | 8-9 | DebugSymbols true / DebugType full in the project (applies to release). | Condition on Debug configuration.
9. SampleBankingApp.csproj | 15 | Newtonsoft.Json 12.0.3 is outdated with known advisories and is not referenced by any code. | Remove the package (or upgrade to 13.0.3 if needed).
10. SampleBankingApp.csproj | 14 | System.Data.SqlClient 4.8.6 is the legacy package. | Migrate to Microsoft.Data.SqlClient.
11. SampleBankingApp.csproj | 13, 16 | JwtBearer 8.0.0 with an explicitly pinned System.IdentityModel.Tokens.Jwt 7.0.0 risks version conflicts. | Remove the explicit pin and let JwtBearer bring its dependency.
12. appsettings.json | 23 | AllowedHosts "*" permits any host header. | Restrict to expected hosts.
13. appsettings.json | 6 | JWT secret stored in plain config. | Secret store/environment variable.
14. Program.cs | 16 | No startup validation that required config (JWT, email, connection string) exists. | Validate with IOptions/ValidateOnStart.

### 10. Missing Unit Tests

No test project exists. Table of critical methods/scenarios:

Rows (File | Line | Issue | Fix) — I'll adapt: Issue = method/scenario needing tests; Fix = suggested test cases.

1. TransactionService.cs | 23 | `Transfer` untested — boundary: amount 0, negative, exactly balance, balance vs balance+fee. | Add tests asserting zero/negative rejected and fee-inclusive check.
2. TransactionService.cs | 23 | `Transfer` self-transfer and nonexistent recipient scenarios. | Tests for fromUserId == toUserId and missing users.
3. TransactionService.cs | 39 | Fee calculation rounding (Math.Round to 2 decimals) untested. | Test 0.015 rate on amounts that round differently (e.g., 0.01 → 0.00 fee).
4. TransactionService.cs | 63 | `Deposit` boundaries: 0, negative, 1000000, 1000000.01. | Table-driven tests.
5. TransactionService.cs | 68 | Interest bonus math untested. | Test the bonus formula once corrected.
6. UserService.cs | 68 | `GetUsersPage` pagination off-by-one untested. | Test page 1 returns first rows and page 2 skips correctly.
7. UserService.cs | 68 | pageSize clamping (50) and invalid page values untested. | Test pageSize 51 → 50, page 0/negative.
8. UserService.cs | 18 | `GetUserById` boundary ids 0, 1, 1000000, 1000001. | Tests for ArgumentException boundaries.
9. AuthService.cs | 28 | `Login` success, wrong password, inactive user, and injection payloads. | Integration tests with parameterized queries.
10. AuthService.cs | 68 | `GenerateJwtToken` claims and expiry. | Assert NameIdentifier, Role claims and expiry.
11. StringHelper.cs | 11 | Email validation boundaries (null, empty, 254/255 chars, valid/invalid). | Unit tests.
12. StringHelper.cs | 20 | Username validation boundaries (2, 3, 20, 21 chars, invalid chars). | Unit tests.
13. UserService.cs | 95 | `SearchUsers` error path currently swallowed. | Test that DB failure is distinguishable from empty results after fix.
14. AuthController.cs | 19 | Login endpoint auth flow (lockout/rate limit once added). | Integration tests.

Also mention: no test project exists at all — first row maybe: "No test project (.csproj) exists in the repository." I'll add as first row with File "—" or "(repository)". The table needs File/Line — I'll use "SampleBankingApp.sln/—" hmm. I'll write File: "(solution)" Line "—". That's acceptable.

Now, formatting: "Keep each CELL to one sentence". OK.

Also the instruction: "Complete all 10 sections before adding any additional commentary." So minimal commentary after. Maybe a brief closing note is allowed after sections, but safer to end after section 10 or add a very short summary. The instruction says complete all 10 sections before adding any additional commentary — implying commentary may follow. I'll add a brief 2-3 sentence summary of top priorities. Keep it short.

Let me double check a few line numbers:

AuthController.cs:
- Login action lines 19-31. request.Username line 22. No rate limiting — line 19.

TransactionController.cs:
- line 26-27 userIdClaim/int.Parse. line 40-41 Deposit. Refund 48-59. Transfer request usage line 29.

UserController.cs:
- GetUser 21-29. GetUsers 31-36. UpdateUser 38-54 (catch ArgumentException 46-49, catch Exception 50-53). DeleteUser 56-69. SearchUsers 71-76. GetAuditLog 78-82.

DatabaseHelper.cs:
- ctor 13-17, fallback line 16.
- GetOpenConnection 19-24.
- ExecuteQuery 26-34; SQL line 29; connection line 28.
- ExecuteQuerySafe 36-48; adapter line 44.
- ExecuteNonQuery 50-57.
- TableExists 59-65.
- ExecuteQueryWithParams 67-78; Obsolete line 67.

StringHelper.cs:
- IsValidEmail 11-18; length line 13; regex line 16.
- IsValidUsername 20-27; line 22; regex 25.
- JoinWithSeparator 29-36.
- JoinWithSeparatorFixed 38-41.
- MaskAccountNumber 43-52; line 45.
- ObfuscateAccount 54-57; line 56.
- ToTitleCase 59-63.
- IsBlank 65-71.

AuthService.cs:
- const line 17.
- Login 28-59; SQL line 32; connection 34-35; reader 38; backdoor 53-56.
- HashPasswordMd5 61-66.
- GenerateJwtToken 68-89; key line 70; expiry line 84.
- HashPasswordSha1 91-96.
- ValidateToken 98-108; return true line 103; unreachable 105-107.

EmailService.cs:
- fields 10-16.
- ctor 18-32; SmtpClient 22-31; port 24; creds 25-28; EnableSsl 29.
- SendTransferNotification 34-61; message 39-43; retry 45-60; Console 56.
- SendWelcomeEmail 63-79; message 69; catch 75-78; Console 77.
- BuildHtmlTemplate 81-84.
- SendWelcomeEmailHtml 86-92; message 89.

TransactionService.cs:
- consts 11-12.
- Transfer 23-61; amount check 25; queries 28-34; Rows[0] 36-37; fee 39; balance check 42; updates 47-48; record 50; email 52-55.
- Deposit 63-75; check 65; bonus 68; update 70-71; record 73.
- IsWithinDailyLimit 77-85.
- RecordTransaction 87-92; SQL 89-90.
- FormatCurrency 94-97.
- RefundTransaction 99-103.

UserService.cs:
- statics 10-11.
- GetUserById 18-36; checks 20-23; count 25.
- UpdateUser 38-50; checks 40-43; audit add 45; SQL 47.
- DeleteUser 52-66; checks 54-57; count 59; SQL 61; audit 64.
- GetUsersPage 68-83; clamp 70; skip 72.
- GetAuditReport 85-93.
- SearchUsers 95-109; ExecuteQuery 99; catch 105-108.
- MapRowToUser 111-123.

Program.cs:
- jwtSecret 16; ValidateLifetime 24; GetBytes 28; dev page 34; https 36; cors 38.

appsettings.json:
- conn 3; jwt 5-9 (secret 6); email 10-15 (password 14); logging 16-22; allowedhosts 23.

csproj:
- DebugSymbols 8; DebugType 9; packages 13-16.

Now write the final report. I should be careful about the "one sentence per cell" rule. Keep cells concise.

For section 6, the prompt wants me to show the working: "Step 1: list EVERY method..." — the output format says use a table. I think I can include a brief method inventory before the table, or just the table with rows for each unused method. The output format is strict: "Within each section use a Markdown table with columns..." — I'll include a one-line note plus the table. Maybe I can add a short paragraph listing the full method inventory to demonstrate the search was done. That seems valuable and aligned with the category instructions. But it might conflict with "use a Markdown table" — I think a brief preamble plus table is fine; the format requirement is about issue rows. I'll add a compact inventory paragraph. Actually, to be safe and thorough, I'll include the inventory as a short list in prose (one line) then the table. Hmm, "no nested bullets" applies to cells. A preamble paragraph should be OK. Let me include a concise sentence: "Method inventory checked: ..." listing all methods. That's a long sentence but fine.

Let me now also reconsider: `DatabaseHelper.ExecuteQuery` is used by SearchUsers — yes. `TableExists` — no callers, confirmed. `ExecuteQueryWithParams` — no callers, confirmed.

`EmailService.SendWelcomeEmail` — search all files: only definition. Confirmed dead. `SendWelcomeEmailHtml` — only definition. `BuildHtmlTemplate` — called at line 88 inside SendWelcomeEmailHtml (dead). Transitively dead.

`TransactionService.FormatCurrency` — only definition. Dead.

`IsWithinDailyLimit` — only definition. Dead.

`AuthService.HashPasswordSha1` — only definition. Dead.

`ValidateToken` — only definition. Dead.

StringHelper — all 8 methods: only definitions. Dead.

`RefundTransaction` — called from controller. Not dead but NotImplemented.

`Transaction` model class — never referenced anywhere (TransactionService uses raw SQL; no mapping). Dead type.

`User.LastLoginAt` — never read/written. `User.Password` — never written (Login mapping omits it). Dead properties.

`_requestCount` — written, never read. Dead field.

`MaxTransactionsPerDay` — referenced only inside dead IsWithinDailyLimit. Effectively dead.

Also `EmailService._config` — used in ctor. Fine.

Also `DatabaseHelper._connectionString` — used. Fine.

OK. Also check `LoginRequest`/`UpdateUserRequest`/`TransferRequest`/`DepositRequest` — used.

Now, one more check on security: "missing authorization attributes" — AuthController has no [Authorize] but that's correct for login. However, no [AllowAnonymous] explicitly — with no global auth filter, it's fine. Controllers have [Authorize]. But no role-based attributes anywhere — covered by IDOR rows.

Also "open CORS" — covered.

Also potential: `app.UseCors` after `UseDeveloperExceptionPage` — order fine.

One more: `builder.Services.AddSingleton<DatabaseHelper>()` — singleton with IConfiguration — fine.

`EmailService` registered scoped but holds SmtpClient field — since scoped, a new SmtpClient per request scope; still never disposed. Covered.

Also `UserService` registered scoped but has static state — covered.

Now let me think about whether `TransactionService.Transfer` line 42 `fromBalance >= amount` — also note that when fromBalance is exactly amount, newFromBalance = -fee → negative. Covered by row 2.

Also `Deposit` — `amount <= 0 || amount > 1000000` — fine boundaries.

`GetUsersPage` — `if (pageSize > 50) pageSize = 50;` — no lower clamp. Covered.

Also `GetUsers` controller default page=1, pageSize=20 — with skip = page*pageSize, page 1 skips 20. Covered.

Also `SearchUsers` — `query` could be null from [FromQuery] if not provided → `'%{null}%'` → actually `$"%{query}%"` with null gives "%%" — matches all. Not a crash. But null query unvalidated — could add to null risks? `query` null → LIKE '%%' returns all users. Minor logic issue: searching with no query returns all users. I could add a row in logic: SearchUsers with null/empty query returns all users instead of empty. I'll add.

Also `UserController.SearchUsers` returns full user objects including... MapRowToUser doesn't include Password — good. But includes Balance, Email — data exposure. Covered by GetUsers row? I'll add a row for SearchUsers exposing all user data without restriction. Actually the IDOR row for GetUser covers reading any user; SearchUsers lets any authenticated user enumerate users by username — similar. I'll add a row.

Also `GetUser` returns `user` which includes... MapRowToUser doesn't set Password — good, Password stays empty. OK.

Let me also consider `AuthService.Login` — returns User without Password — fine.

`GenerateJwtToken` for backdoor user Id=0 — claim "0". Covered in logic.

Now, `TransactionService.Transfer` — `description` null → `'{description}'` → `''`? In C#, `$"{null}"` → "". So SQL gets `''`. Fine.

`RecordTransaction` — `amount` decimal interpolated — culture issue: in de-DE, `(100.50m).ToString()` → "100,50" → SQL syntax error/injection. Worth a row in logic or quality: decimal interpolation is culture-sensitive. I'll add to logic errors or anti-patterns. I'll add to logic: culture-sensitive decimal formatting in SQL. Actually it fits "any operation that can produce a nonsensical result". I'll add a row in Logic.

Also `newFromBalance`/`newToBalance` same issue.

OK, also `EmailService.SendTransferNotification` — `recipientName` from toUser Username — fine.

Let me also check `Program.cs` — no `app.UseRouting()` — fine with minimal hosting. `UseCors` before `UseAuthentication` — fine.

`AddControllers` — fine.

No `AddCors` in services but `app.UseCors(policy => ...)` — works.

One more security: JWT `ValidIssuer`/`ValidAudience` from config — fine.

`JwtSecurityToken` expires 30 days — long. Covered.

Now compile the report. I'll aim for comprehensive tables. Let me count rows per section:

Section 1: ~34 rows. Section 2: ~18. Section 3: ~15. Section 4: ~10. Section 5: ~15. Section 6: ~25. Section 7: ~26. Section 8: ~23. Section 9: ~14. Section 10: ~14.

That's a lot but the prompt says thoroughness matters more than length.

Let me be careful to keep each cell one sentence and reasonably short.

For File column, use relative paths like `Services/AuthService.cs`.

Let me write it.

Section 6 preamble: I'll include a compact inventory. Something like:

"Step 1 inventory — AuthController: Login; TransactionController: Transfer, Deposit, Refund; UserController: GetUser, GetUsers, UpdateUser, DeleteUser, SearchUsers, GetAuditLog; DatabaseHelper: GetOpenConnection, ExecuteQuery, ExecuteQuerySafe, ExecuteNonQuery, TableExists, ExecuteQueryWithParams; StringHelper: IsValidEmail, IsValidUsername, JoinWithSeparator, JoinWithSeparatorFixed, MaskAccountNumber, ObfuscateAccount, ToTitleCase, IsBlank; AuthService: Login, HashPasswordMd5, GenerateJwtToken, HashPasswordSha1, ValidateToken; EmailService: SendTransferNotification, SendWelcomeEmail, BuildHtmlTemplate, SendWelcomeEmailHtml; TransactionService: Transfer, Deposit, IsWithinDailyLimit, RecordTransaction, FormatCurrency, RefundTransaction; UserService: GetUserById, UpdateUser, DeleteUser, GetUsersPage, GetAuditReport, SearchUsers, MapRowToUser. Step 2 scanned all files for calls; rows below are names that appear only at their definition."

That's good — demonstrates the work.

Now write everything. Also note in section 6: "code after an unconditional return" — ValidateToken lines 105-107. "[Obsolete] still present" — ExecuteQueryWithParams. "duplicate implementations where a fixed version exists alongside a broken one but only the broken one is called" — hmm: JoinWithSeparator (broken) vs JoinWithSeparatorFixed (fixed) — neither is called. MaskAccountNumber vs ObfuscateAccount — neither called. So the "only broken one called" scenario doesn't apply; both dead. I'll note both dead and duplicates.

"throw new NotImplementedException() in non-stub code" — RefundTransaction, exposed via live endpoint.

Let me also double check `Transaction` model usage: TransactionService.Transfer returns tuple; RecordTransaction raw SQL; no `new Transaction` anywhere; no `List<Transaction>`. Confirmed dead. Also `Transaction.Type`, `Status`, `Description`, `CreatedAt` — part of the dead class; one row for the class.

Also `User.Password` — never assigned in MapRowToUser or Login mapping. Row.

`User.LastLoginAt` — never assigned. Row.

Also `DepositRequest`/`TransferRequest` used. `LoginRequest` used.

Also `EmailService` consts TransferSubject/WelcomeSubject used within the class. Fine.

`SmtpTimeoutMs`, `MaxRetries` used. Fine.

`TransactionFeeRate` used. `MaxTransactionsPerDay` only in dead method — row.

`AdminBypassPassword` used in Login. Not dead (but should be removed).

OK, also section 8 refactoring: name methods with 3+ responsibilities:
- TransactionService.Transfer — validate input, load both users, compute fee, check funds, execute two updates, record transaction, send notification. Split: ValidateTransferRequest, LoadUser, Debit/Credit within transaction, RecordTransaction (exists), NotifyUser.
- AuthService.Login — open connection, authenticate, backdoor check, map row. Split: MapUser(reader) + remove backdoor.
- EmailService.SendTransferNotification — build body, construct message, retry loop, send. Split: BuildTransferBody, SendWithRetry.
- UserService.SearchUsers — data access, mapping, swallow. 
- Program.cs — fine.
- UserService.UpdateUser — validation, audit, SQL. Could mention. I'll include Transfer, Login, SendTransferNotification, SearchUsers, and maybe Deposit. Deposit: validate, compute bonus, update, record — 4 responsibilities. Include.

Alright. Also section 8: "helper methods designed to leak resource ownership to callers with no documented contract" — GetOpenConnection. Row.

Also duplicated validation logic — the id range block in 3 methods (3 rows). Also the "load user by id" duplication in Transfer (2 identical queries) — row.

Also `MapRowToUser` vs AuthService's inline reader mapping — duplicated user mapping logic (two implementations). Row.

OK, writing now.

For Section 9, also "missing environment-specific config overrides" — no appsettings.Production.json. Row with File "(missing) appsettings.Production.json" — I'll write File as `appsettings.Production.json` and Line "—".

For Section 10, File column: I'll use the method's file, Line its line, Issue "No tests exist for X scenario", Fix "Add test...".

Also first row: "No test project exists in the repository." File: "(solution root)".

Let me also make sure I don't miss: "missing rate limiting or account lockout on authentication endpoints" — in section 3 checklist. I have it in section 1; add to section 3 too. Yes I planned row 10 in section 3.

Also section 3: "raw ex.Message or stack traces returned to HTTP clients" — UpdateUser 500 ex.Message (row), BadRequest ex.Message (row). Also developer exception page leaks stack traces — that's config/security; covered.

Also "operations that lack a database transaction where two or more writes must be atomic" — Transfer (row), Deposit (row).

Also "side effects (email) that can throw after DB write committed" — Transfer row.

Also "catch blocks that return empty collections" — SearchUsers row.

Also "methods that catch broad Exception and swallow it silently" — SearchUsers (returns empty), SendWelcomeEmail (Console.WriteLine). Rows.

OK. Also for section 2, "missing self-referential checks (transferring to yourself)" — row 4. Good.

Also "incorrect boundary conditions (e.g. `< 0` when `<= 0` is needed)" — Transfer amount < 0 row. Good.

Also "incorrect rates or constants (interest rate applied as 5% instead of 1%)" — Deposit 5% row. Good.

Also "balance or fee calculations that exclude a component" — row 2. Good.

Also "off-by-one in pagination" — row 1. Good.

Also "any operation that can produce a negative balance" — row 2 covers; also mention explicitly.

Additional logic: `GetUsersPage` — `page` default 1 in controller; with skip = page*pageSize, page 1 → skip 20 (skips first page). Yes.

Also `UserService.GetUserById` id > 1000000 throws — but controller GetUser doesn't handle → 500. In error handling row 9.

Also `TransactionController.Refund` — catches only NotImplementedException; other exceptions unhandled. Minor; skip or add. I'll add: Refund has no handling for other exceptions. Eh — keep. I'll add a row.

Also `AuthController.Login` — `_authService.Login` may throw SqlException → 500 unhandled. Row in error handling (I have row 14).

Now — one thing about `EmailService` ctor: `int.Parse(_config["Email:SmtpPort"] ?? "25")` — has fallback, fine, but if config value is non-numeric → FormatException at startup. Minor; skip.

`NetworkCredential(_config["Email:Username"], _config["Email:Password"])` — nulls → NetworkCredential(null, null) — actually NetworkCredential accepts null username? It sets empty. Not a crash. But null risk row is fine as "may be null".

OK — also `Program.cs` line 16: `builder.Configuration["Jwt:SecretKey"]` — if null, `Encoding.UTF8.GetBytes(jwtSecret!)` at line 28 throws ArgumentNullException. Row.

Also `AuthService.GenerateJwtToken` line 70 same. Row.

Alright, let me also verify `StringHelper.IsValidEmail` null risk: parameter declared `string email` non-nullable — but callers could pass null; since no callers at all, it's dead code anyway. Still report null risk per checklist ("method parameters used before a null check"). Yes.

Now writing the final answer. I'll keep the intro minimal — maybe one line stating commit reviewed. Then the 10 sections. Then a short prioritized summary (allowed after all 10 sections).

Format check: "Produce a Markdown report with one ## section per category." Use `## 1. Security Vulnerabilities` etc.

Each table: `| File | Line | Issue | Fix |` with separator row.

Let me write concisely but completely.

One more consideration for Section 1 — "missing authorization attributes": I'll frame rows as missing role-based authorization on admin-ish endpoints (GetUsers, GetAuditLog, DeleteUser, Refund). Already have rows.

Also "backdoors" — the admin bypass. Have it.

Also "production secrets committed to source control" — appsettings rows. Have.

Also "debug symbols in release builds" — csproj row. Have.

Also "HTTPS disabled" — row. Have.

Also "developer exception pages in production" — row. Have.

Also "open CORS policy" — row. Have.

Also "broken or weak cryptography (MD5, SHA1, no salt)" — rows. Have.

Also "JWT misconfiguration (ValidateLifetime, weak secrets)" — rows. Have.

Also "broken access control (missing ownership checks on PUT/DELETE)" — rows. Have.

Also "SQL injection (including ... helper methods that accept raw SQL fragments)" — ExecuteQuery, ExecuteNonQuery rows. Have.

Good. Writing now.

For the dead code section, let me make sure each row names the method explicitly.

Rows:
1. Data/DatabaseHelper.cs | 59 | `TableExists` is defined but never called anywhere in the codebase. | Delete it or use it in a startup schema check.
2. Data/DatabaseHelper.cs | 67-78 | `ExecuteQueryWithParams` is marked [Obsolete] and has no callers. | Delete it.
3. Helpers/StringHelper.cs | 11 | `IsValidEmail` has no callers — email is never validated anywhere. | Wire it into UpdateUser/registration or delete.
4. Helpers/StringHelper.cs | 20 | `IsValidUsername` has no callers. | Wire into UpdateUser or delete.
5. Helpers/StringHelper.cs | 29 | `JoinWithSeparator` has no callers. | Delete (broken anyway).
6. Helpers/StringHelper.cs | 38 | `JoinWithSeparatorFixed` has no callers. | Delete.
7. Helpers/StringHelper.cs | 43 | `MaskAccountNumber` has no callers. | Delete or use for account display.
8. Helpers/StringHelper.cs | 54 | `ObfuscateAccount` has no callers. | Delete.
9. Helpers/StringHelper.cs | 59 | `ToTitleCase` has no callers. | Delete.
10. Helpers/StringHelper.cs | 65 | `IsBlank` has no callers. | Delete.
11. Services/AuthService.cs | 91 | `HashPasswordSha1` has no callers. | Delete.
12. Services/AuthService.cs | 98 | `ValidateToken` has no callers. | Delete (or fix and use it).
13. Services/EmailService.cs | 63 | `SendWelcomeEmail` has no callers. | Delete or call it from a registration flow.
14. Services/EmailService.cs | 86 | `SendWelcomeEmailHtml` has no callers. | Delete.
15. Services/EmailService.cs | 81 | `BuildHtmlTemplate` is only called by the dead `SendWelcomeEmailHtml`, so it is transitively dead. | Delete both together.
16. Services/TransactionService.cs | 77 | `IsWithinDailyLimit` has no callers, so the daily limit is never enforced. | Call it from Transfer/Deposit or delete.
17. Services/TransactionService.cs | 94 | `FormatCurrency` has no callers. | Delete or use it in messages.
18. Services/TransactionService.cs | 99 | `RefundTransaction` throws NotImplementedException but is reachable from the live refund endpoint. | Implement it or remove the endpoint.
19. Services/TransactionService.cs | 12 | `MaxTransactionsPerDay` is referenced only inside the dead `IsWithinDailyLimit`. | Remove with the method or enforce it.
20. Models/Transaction.cs | 3 | The `Transaction` class is never instantiated or referenced by any code. | Delete or use it in RecordTransaction/read paths.
21. Models/User.cs | 7 | `User.Password` is never populated by any mapping code. | Remove the property or map it (never serialize it).
22. Models/User.cs | 13 | `User.LastLoginAt` is never read or written. | Update it on login or remove.
23. Services/UserService.cs | 11 | `_requestCount` is incremented but never read. | Delete the field.
24. Services/AuthService.cs | 105-107 | Code after the unconditional `return true` in `ValidateToken` is unreachable. | Remove the early return or the dead block.
25. Helpers/StringHelper.cs | 29 vs 38 | Duplicate join implementations (broken and fixed) both exist and neither is called. | Keep only string.Join usage.
26. Helpers/StringHelper.cs | 43 vs 54 | `MaskAccountNumber` and `ObfuscateAccount` duplicate each other. | Keep one.

Good.

Now Section 7 rows — let me finalize (with the "notifications@company.com" occurrences at lines 40, 69, 89):

Also "support@company.com" line 67.

Also config keys "Jwt:SecretKey" at Program.cs:16 and AuthService.cs:70; "DefaultConnection" at DatabaseHelper.cs:15 and AuthService.cs:34.

Also role name "SuperAdmin" line 55.

Also "Completed" line 90, "Transfer" line 50, "Deposit" line 73.

Also 1000000 at UserService 22, 42, 56 (three rows). 50 at line 70. 254 line 13. 3/20 line 22. 4 at lines 45, 49-50, 56. 30 days line 84. 1000000 deposit cap line 65. 0.05m line 68. 0 sentinel line 73. Port 25 line 24. Fallback conn string line 16. AdminBypassPassword line 17. "admin" line 53.

Fee rate line 11 (config candidate).

That's ~26 rows. Fine.

Section 8 rows finalized above (~23).

Section 9 rows (~14).

Section 10 rows (~14).

Alright, let me also sanity-check the claim about `Newtonsoft.Json 12.0.3` vulnerabilities: Newtonsoft.Json before 13.0.1 had CVE-2021-40257? Actually that's a different one. Known: Newtonsoft.Json 12.0.3 — there were advisories about improper handling of high-nesting JSON (CVE-2024-21907? no that's...). Hmm. To be safe, I'll say "outdated (12.x) and unused by any code in this repo; upgrade to 13.x if retained" — avoid claiming specific CVEs. Actually there is a known advisory: GHSA for Newtonsoft.Json < 13.0.1 — "Newtonsoft.Json before 13.0.1 allows... high nesting" — yes, CVE-2021-40257? No... Let me recall: High severity vulnerability in Newtonsoft.Json versions before 13.0.1 — improper handling of high-nested JSON (DoS). I believe there's GHSA-5crp-9r3c-p9vr for Newtonsoft.Json 13.0.1 fixing high-nesting DoS. I'll phrase generically: "outdated with known advisories against pre-13.0.1 versions". That's accurate enough.

System.Data.SqlClient 4.8.6 — 4.8.6 is actually the latest of that package line; it's deprecated/maintenance-only; Microsoft.Data.SqlClient is the successor. I'll phrase as "legacy, maintenance-only package".

System.IdentityModel.Tokens.Jwt 7.0.0 explicit pin alongside JwtBearer 8.0.0 — JwtBearer 8.0.0 depends on System.IdentityModel.Tokens.Jwt >= 7.0.3 (I believe 8.0.0 → Microsoft.IdentityModel 7.0.3? Actually JwtBearer 8.0.0 depends on Microsoft.IdentityModel.Protocols.OpenIdConnect 7.0.3? Hmm. JwtBearer 8.0.0 references System.IdentityModel.Tokens.Jwt 7.0.3? I think JwtBearer 8.0.0 depends on Microsoft.IdentityModel.JsonWebTokens 7.0.3... not 100% sure. The explicit 7.0.0 pin may downgrade or conflict. I'll phrase cautiously: "explicitly pins 7.0.0 alongside JwtBearer 8.0.0, which can conflict with the version JwtBearer resolves". Safe.

Also `TreatWarningsAsErrors false` — minor; I'll include in section 9? It's a quality setting. I'll include as a row: allows warnings (like CS0618 obsolete usage) to slip through. Eh — fine, include.

Also missing `<InvariantGlobalization>` etc. — skip.

Also `DebugType full` — row.

Now Section 5 — also `UserService.SearchUsers` query null → returns all users (logic) — I put in logic. Also `request` null checks — rows for Login, Transfer, Deposit, UpdateUser.

Also `TransactionService.Transfer` — `description` is `string?` and passed to RecordTransaction which interpolates — null → empty string, fine.

Also `EmailService.SendTransferNotification(toEmail, ...)` — toEmail from DB, fine.

Also `MapRowToUser` — row["X"] casts — if DB nulls, InvalidCast. Skip.

OK, also one more null risk: `UserController.GetUser` — fine.

`TransactionController.Refund(int transactionId)` — route param, fine.

Let me now also think about Section 2 row for culture-sensitive decimal interpolation:

TransactionService.cs | 47-48, 70-71, 90 | Decimal values interpolated into SQL use current culture — in comma-decimal cultures the SQL breaks or misparses. | Use parameters (also fixes injection).

I'll add as one row (or per method). The prompt wants each occurrence... These are within Transfer/Deposit/RecordTransaction. I'll fold into the SQL injection rows in section 1? The injection rows already say "parameterize". I'll add one logic row for the culture issue referencing the three methods. Actually to respect "each occurrence its own row", I'll add rows for Transfer (47-48), Deposit (70-71), RecordTransaction (90). Hmm, that inflates. I'll do one row per method — 3 rows in section 2. OK.

Actually wait — is it really a "logic error"? It produces wrong behavior in some locales — yes, nonsensical result. Fine.

Also Section 2: `SearchUsers` null/empty query returns all users — row.

Let me finalize Section 2 rows:

1. UserService.cs | 72 | GetUsersPage off-by-one.
2. TransactionService.cs | 42-44 | Balance check excludes fee → negative balance.
3. TransactionService.cs | 25 | amount < 0 allows zero.
4. TransactionService.cs | 23 | No self-transfer check.
5. TransactionService.cs | 68 | 5% bonus with no-op * 1.
6. TransactionService.cs | 39-48 | Fee deducted but never recorded/credited.
7. TransactionService.cs | 63-75 | Deposit doesn't verify user exists.
8. TransactionService.cs | 36-37 | Transfer doesn't verify users exist (also null-risk section; keep here as logic gap? I have it in section 5. To avoid duplication I'll keep in section 5 only. Hmm — but it's a logic gap too. The prompt allows overlap; I'll keep in 5 and not duplicate in 2. Actually I listed it in both drafts. I'll keep it in section 5 (Rows[0] without count check) and drop from 2.)
9. TransactionService.cs | 77-85 | Daily limit never enforced (dead IsWithinDailyLimit).
10. UserService.cs | 68-76 | page/pageSize not lower-bounded.
11. AuthService.cs | 98-108 | ValidateToken always true.
12. StringHelper.cs | 29-36 | Trailing separator.
13. StringHelper.cs | 56 | ObfuscateAccount short-string crash.
14. UserService.cs | 38-50 | UpdateUser returns true for nonexistent id.
15. UserService.cs | 52-66 | DeleteUser returns true for nonexistent id.
16. TransactionService.cs | 36-48 | Race condition on balance read/write (no locking/transaction).
17. AuthService.cs | 55 | Backdoor user Id = 0.
18. UserService.cs | 111-123 | LastLoginAt never updated (also dead code — keep in dead code; drop here? It's a functional gap: login doesn't record last login. I'll keep in dead code only.)
19. UserService.cs | 95-99 | SearchUsers with null/empty query matches all users.
20. TransactionService.cs | 47-48 | Culture-sensitive decimal interpolation.
21. TransactionService.cs | 70-71 | Same in Deposit.
22. TransactionService.cs | 90 | Same in RecordTransaction.

OK ~19 rows.

Now Section 3 rows:

1. UserService.cs | 105-108 | SearchUsers swallows all exceptions, returns empty list.
2. EmailService.cs | 75-78 | SendWelcomeEmail swallows Exception with Console.WriteLine.
3. EmailService.cs | 56 | Console.WriteLine for retry failures instead of ILogger.
4. TransactionService.cs | 44-50 | Transfer's two updates + insert not in a transaction.
5. TransactionService.cs | 70-73 | Deposit's update + insert not atomic.
6. TransactionService.cs | 50-55 | Email sent after DB writes; throw gives client error though transfer committed.
7. UserController.cs | 50-52 | UpdateUser returns ex.Message in 500.
8. UserController.cs | 46-48 | UpdateUser returns raw ArgumentException message.
9. UserController.cs | 21-29 | GetUser lacks try/catch; ArgumentException from service becomes unhandled 500.
10. AuthController.cs | 19-31 | No rate limiting/lockout on login.
11. TransactionController.cs | 26-27 | int.Parse on claim without TryParse → unhandled 500.
12. TransactionController.cs | 40-41 | Same in Deposit.
13. TransactionController.cs | 48-59 | Refund only catches NotImplementedException; other exceptions unhandled.
14. AuthService.cs | 32-38 | Login has no SqlException handling → raw 500 on DB outage.
15. EmailService.cs | 45-60 | Retry loop has no backoff delay.

Section 4 rows (10):

1. DatabaseHelper.cs | 28-33 | ExecuteQuery leaks connection/command/adapter.
2. DatabaseHelper.cs | 50-57 | ExecuteNonQuery: Close without Dispose; skipped on throw.
3. DatabaseHelper.cs | 19-24 | GetOpenConnection ownership leak.
4. AuthService.cs | 34-38 | Login never disposes connection/command/reader.
5. EmailService.cs | 16 | SmtpClient instance field never disposed, not thread-safe.
6. EmailService.cs | 39 | MailMessage not disposed in SendTransferNotification.
7. EmailService.cs | 69 | MailMessage not disposed in SendWelcomeEmail.
8. EmailService.cs | 89 | MailMessage not disposed in SendWelcomeEmailHtml.
9. DatabaseHelper.cs | 44 | SqlDataAdapter not disposed in ExecuteQuerySafe.
10. DatabaseHelper.cs | 74 | SqlDataAdapter not disposed in ExecuteQueryWithParams.

Section 5 rows (15):

1. Program.cs | 16, 28 | jwtSecret null → GetBytes throws.
2. AuthService.cs | 70 | SecretKey null-forgiving.
3. TransactionController.cs | 26-27 | userIdClaim null → NRE.
4. TransactionController.cs | 40-41 | same.
5. TransactionService.cs | 36 | fromUserTable.Rows[0] unchecked.
6. TransactionService.cs | 37 | toUserTable.Rows[0] unchecked.
7. StringHelper.cs | 13 | email.Length no null check.
8. StringHelper.cs | 22 | username.Length no null check.
9. StringHelper.cs | 45 | accountNumber.Length no null check.
10. StringHelper.cs | 56 | account[^4..] no null/length guard.
11. EmailService.cs | 25-27 | Email:Username/Password may be null into NetworkCredential.
12. AuthController.cs | 20-22 | request used without null check.
13. TransactionController.cs | 24-29 | request used without null check.
14. TransactionController.cs | 38-43 | request used without null check.
15. UserController.cs | 39-43 | request used without null check.

Section 7 rows — finalize:

1. DatabaseHelper.cs | 16 | Fallback connection string hardcoded.
2. AuthService.cs | 17 | AdminBypassPassword constant.
3. AuthService.cs | 53 | "admin" magic string.
4. AuthService.cs | 55 | "SuperAdmin" magic role string.
5. AuthService.cs | 84 | AddDays(30) token lifetime.
6. TransactionService.cs | 11 | Fee rate in source not config.
7. TransactionService.cs | 65 | 1000000 deposit cap inline.
8. TransactionService.cs | 68 | 0.05m rate inline.
9. TransactionService.cs | 73 | 0 sentinel.
10. TransactionService.cs | 50 | "Transfer" type literal.
11. TransactionService.cs | 73 | "Deposit" type literal.
12. TransactionService.cs | 90 | 'Completed' status literal.
13. UserService.cs | 22-23 | 1000000 in GetUserById.
14. UserService.cs | 42-43 | 1000000 in UpdateUser.
15. UserService.cs | 56-57 | 1000000 in DeleteUser.
16. UserService.cs | 70 | 50 page-size cap inline.
17. StringHelper.cs | 13 | 254 email length.
18. StringHelper.cs | 22 | 3 and 20 username bounds.
19. StringHelper.cs | 45 | 4 visible digits.
20. StringHelper.cs | 56 | "****" and 4.
21. EmailService.cs | 40 | "notifications@company.com" (SendTransferNotification).
22. EmailService.cs | 67 | "support@company.com".
23. EmailService.cs | 69 | "notifications@company.com" (SendWelcomeEmail).
24. EmailService.cs | 89 | "notifications@company.com" (SendWelcomeEmailHtml).
25. EmailService.cs | 24 | default port 25 inline.
26. Program.cs:16 + AuthService.cs:70 | "Jwt:SecretKey" key duplicated.
27. DatabaseHelper.cs:15 + AuthService.cs:34 | "DefaultConnection" duplicated.

For rows 26-27, File column can list both files. OK.

Section 8 rows — finalize (~23):

1. StringHelper.cs | 31-34 | += in loop.
2. UserService.cs | 87-92 | += in loop in GetAuditReport.
3. StringHelper.cs | 16 | new Regex per call (IsValidEmail).
4. StringHelper.cs | 25 | new Regex per call (IsValidUsername).
5. UserService.cs | 10 | static _auditLog unsynchronized + unbounded.
6. UserService.cs | 11 | static _requestCount unsynchronized.
7. StringHelper.cs | 65-71 | IsBlank reimplements IsNullOrWhiteSpace.
8. StringHelper.cs | 38-41 | JoinWithSeparatorFixed duplicates string.Join.
9. StringHelper.cs | 54-57 | ObfuscateAccount duplicates MaskAccountNumber.
10. DatabaseHelper.cs | 19-24 | GetOpenConnection ownership leak (no contract).
11. EmailService.cs | 56, 77 | Console.WriteLine instead of ILogger.
12. EmailService.cs | 45-60 | No backoff between retries.
13. UserService.cs | 20-23 | Duplicated id validation in GetUserById.
14. UserService.cs | 40-43 | Duplicated in UpdateUser.
15. UserService.cs | 54-57 | Duplicated in DeleteUser.
16. AuthService.cs | 34 | Login bypasses DatabaseHelper, builds own connection.
17. TransactionService.cs | 28-34 | Duplicate load-user query in Transfer.
18. AuthService.cs | 40-50 vs UserService.cs | 111-123 | Two different user-mapping implementations.
19. TransactionService.cs | 23-61 | Transfer has 7 responsibilities — split.
20. AuthService.cs | 28-59 | Login mixes auth, backdoor, mapping — split.
21. EmailService.cs | 34-61 | SendTransferNotification mixes build/retry/send — split.
22. UserService.cs | 95-109 | SearchUsers mixes access/mapping/suppression — split.
23. TransactionService.cs | 63-75 | Deposit mixes validation, bonus math, persistence — split.
24. TransactionController.cs | 51-59 | Catching NotImplementedException as control flow.

Section 9 rows:

1. Program.cs | 34 | Dev exception page unconditional.
2. Program.cs | 24 | ValidateLifetime = false.
3. Program.cs | 36 | HTTPS redirection commented out.
4. Program.cs | 38 | Permissive CORS.
5. appsettings.json | 17-21 | Debug log levels.
6. appsettings.Production.json | — | Missing.
7. appsettings.json | 3 | Prod DB referenced in base config with creds.
8. SampleBankingApp.csproj | 8-9 | DebugSymbols/DebugType full.
9. SampleBankingApp.csproj | 15 | Newtonsoft.Json 12.0.3 outdated and unused.
10. SampleBankingApp.csproj | 14 | System.Data.SqlClient legacy.
11. SampleBankingApp.csproj | 13, 16 | Jwt 7.0.0 pin vs JwtBearer 8.0.0.
12. SampleBankingApp.csproj | 7 | TreatWarningsAsErrors false.
13. appsettings.json | 23 | AllowedHosts "*".
14. appsettings.json | 6 | JWT secret in plain config.
15. Program.cs | 16 | No startup validation of required config.

Section 10 rows:

1. (no test project) | — | No test project exists. | Add xUnit project referencing SampleBankingApp.
2. TransactionService.cs | 25 | Transfer amount boundaries 0/negative.
3. TransactionService.cs | 42 | Balance vs balance+fee boundary.
4. TransactionService.cs | 23 | Self-transfer.
5. TransactionService.cs | 36-37 | Nonexistent sender/recipient.
6. TransactionService.cs | 39 | Fee rounding.
7. TransactionService.cs | 65 | Deposit boundaries 0, 1000000, 1000000.01.
8. TransactionService.cs | 68 | Bonus math.
9. UserService.cs | 72 | Pagination off-by-one.
10. UserService.cs | 70 | pageSize clamp and invalid page.
11. UserService.cs | 20-23 | GetUserById id boundaries.
12. AuthService.cs | 28 | Login success/failure/inactive/injection.
13. AuthService.cs | 68 | Token claims/expiry.
14. StringHelper.cs | 11-27 | Validation boundaries.
15. UserService.cs | 95 | SearchUsers error vs empty.

Good.

Now write the final report. Keep cells one sentence each. Use concise file paths.

I'll write File as e.g. `Services/AuthService.cs`.

Let me write the final output now. I'll add a one-line header noting the commit. Then sections. Then a brief prioritized note (short).

Double-check line numbers once more for accuracy in key rows:

- AuthService SQL: line 32. ✓
- Backdoor: lines 53-56. ✓
- MD5: line 30 (call), 61-66 (method). ✓
- ValidateLifetime: Program.cs line 24. ✓
- CORS: line 38. ✓
- Dev page: line 34. ✓
- HTTPS: line 36. ✓
- GetBytes: line 28. ✓
- DatabaseHelper fallback: line 16. ✓
- ExecuteQuery: 26-34, SQL at 29. ✓
- ExecuteNonQuery: 50-57. ✓
- UpdateUser SQL: UserService line 47. ✓
- DeleteUser SQL: line 61. ✓
- SearchUsers: line 99. ✓
- Transfer updates: 47-48. ✓
- Deposit update: 70-71. ✓
- RecordTransaction: 89-91. ✓
- GetUsersPage skip: line 72. ✓
- amount < 0: line 25. ✓
- balance check: line 42. ✓
- bonus: line 68. ✓
- deposit cap: line 65. ✓
- IsWithinDailyLimit: 77-85. ✓
- FormatCurrency: 94-97. ✓
- RefundTransaction: 99-103. ✓
- _auditLog: line 10. ✓
- _requestCount: line 11. ✓
- GetAuditReport: 85-93. ✓
- MapRowToUser: 111-123. ✓
- EmailService SmtpClient field: line 16. ✓
- ctor: 18-32. ✓
- SendTransferNotification: 34-61; message 39-43. ✓
- SendWelcomeEmail: 63-79. ✓
- BuildHtmlTemplate: 81-84. ✓
- SendWelcomeEmailHtml: 86-92. ✓
- ValidateToken: 98-108; return true 103; unreachable 105-107. ✓
- HashPasswordSha1: 91-96. ✓
- GenerateJwtToken: 68-89; key 70; expiry 84. ✓
- Login connection: 34-38. ✓
- StringHelper lines verified. ✓
- UserController: UpdateUser 38-54; catches 46-53. DeleteUser 56-69. GetAuditLog 78-82. GetUsers 31-36. GetUser 21-29. SearchUsers 71-76. ✓
- TransactionController: parse 27 and 41; Refund 48-60. ✓
- appsettings lines: conn 3, secret 6, email password 14, logging 17-21, allowedhosts 23. ✓
- csproj: TreatWarnings 7, DebugSymbols 8, DebugType 9, packages 13-16. ✓

Alright. Writing final answer. I'll keep the preamble to one sentence.</think># Code Review Report — branch `main`, commit `8797593`

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/AuthService.cs | 32 | `Login` interpolates `username` and `hashedPassword` directly into the SELECT — classic SQL injection on the login endpoint. | Rewrite using `ExecuteQuerySafe` with `@Username`/`@Password` parameters. |
| Services/AuthService.cs | 53-56 | Hardcoded backdoor: username `"admin"` with the const password grants a `SuperAdmin` user. | Delete the bypass branch entirely and authenticate only against the database. |
| Services/AuthService.cs | 17 | Hardcoded credential `AdminBypassPassword = "SuperAdmin2024"` in source. | Remove the constant and rotate any credentials ever protected by it. |
| Services/AuthService.cs | 30, 61-66 | Passwords are hashed with unsalted MD5 via `HashPasswordMd5`. | Use a modern KDF such as PBKDF2 or ASP.NET Core's `PasswordHasher` with per-user salt. |
| Services/AuthService.cs | 91-96 | `HashPasswordSha1` uses unsalted SHA1. | Delete the method (it is unused) and never use SHA1 for passwords. |
| Program.cs | 24 | `ValidateLifetime = false` means expired JWTs are accepted indefinitely. | Set `ValidateLifetime = true`. |
| Program.cs | 28 | `Encoding.UTF8.GetBytes(jwtSecret!)` uses a null-forgiving operator on a config value that is the weak string `"mysecretkey"`. | Fail startup if the secret is missing and enforce a minimum 256-bit key from a secret store. |
| appsettings.json | 6 | Weak JWT secret `"mysecretkey"` committed to source control. | Move to environment/secret manager and rotate the key. |
| appsettings.json | 3 | Production DB connection string with `sa` account and password `Admin1234!` committed. | Remove from the repo, use environment variables or a secret store, and rotate the password. |
| appsettings.json | 14 | SMTP password `EmailPass99` committed to source control. | Move to secret storage and rotate. |
| Data/DatabaseHelper.cs | 16 | Fallback connection string hardcodes `sa` credentials `Admin1234!`. | Remove the fallback and throw a clear exception when the connection string is missing. |
| Data/DatabaseHelper.cs | 26-29 | `ExecuteQuery` builds SQL by interpolating `tableName` and `whereClause` — SQL injection by design. | Delete the method or restrict it to a fixed table name with parameterized filters. |
| Data/DatabaseHelper.cs | 50-53 | `ExecuteNonQuery` executes arbitrary raw SQL strings passed by callers. | Change the signature to accept parameterized SQL plus a parameters dictionary. |
| Services/UserService.cs | 47 | `UpdateUser` interpolates `email` and `username` into the UPDATE — SQL injection from the PUT endpoint. | Use a parameterized command. |
| Services/UserService.cs | 61 | `DeleteUser` interpolates `id` into the DELETE statement. | Use a parameterized command. |
| Services/UserService.cs | 99 | `SearchUsers` interpolates `query` into a LIKE clause — SQL injection plus LIKE wildcard injection. | Use a parameterized LIKE with escaped wildcards. |
| Services/TransactionService.cs | 47 | `Transfer` interpolates `newFromBalance` and `fromUserId` into an UPDATE. | Use a parameterized UPDATE. |
| Services/TransactionService.cs | 48 | `Transfer` interpolates `newToBalance` and `toUserId` into the second UPDATE. | Use a parameterized UPDATE. |
| Services/TransactionService.cs | 70-71 | `Deposit` interpolates the computed amount into an UPDATE. | Use a parameterized UPDATE. |
| Services/TransactionService.cs | 89-91 | `RecordTransaction` interpolates user-supplied `description` into the INSERT — direct SQL injection from the transfer endpoint. | Use a parameterized INSERT. |
| Controllers/UserController.cs | 38-54 | `UpdateUser` (PUT) has no ownership or role check — any authenticated user can modify any account. | Compare the route id to the `NameIdentifier` claim or require an admin role. |
| Controllers/UserController.cs | 56-69 | `DeleteUser` has no ownership or admin check — any authenticated user can delete any account. | Require an admin role and verify authorization before deleting. |
| Controllers/UserController.cs | 21-29 | `GetUser` lets any authenticated user read any other user's record including balance (IDOR). | Restrict to self or admin. |
| Controllers/UserController.cs | 31-36 | `GetUsers` exposes the full user list to any authenticated user with no admin restriction. | Add `[Authorize(Roles = "Admin")]`. |
| Controllers/UserController.cs | 71-76 | `SearchUsers` lets any authenticated user enumerate all users by username fragments. | Restrict to admin or self-matching results. |
| Controllers/UserController.cs | 78-82 | `GetAuditLog` exposes audit data to any authenticated user with no role check. | Restrict to admin role. |
| Controllers/TransactionController.cs | 48-59 | `Refund` performs no ownership check on `transactionId`. | Verify the transaction belongs to the caller (or is admin) before refunding. |
| Program.cs | 38 | CORS policy allows any origin, any method, and any header. | Define a named policy restricted to known origins. |
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, leaking stack traces in production. | Gate it on `app.Environment.IsDevelopment()`. |
| Program.cs | 36 | HTTPS redirection is commented out. | Re-enable `app.UseHttpsRedirection()`. |
| SampleBankingApp.csproj | 8-9 | `DebugSymbols` and full `DebugType` are enabled for all builds including release. | Condition both on the Debug configuration. |
| Services/EmailService.cs | 29 | `EnableSsl = false` sends SMTP credentials in cleartext. | Enable SSL and use port 587. |
| Services/EmailService.cs | 83 | `BuildHtmlTemplate` interpolates `title`/`body` into HTML unescaped — HTML injection via username. | HTML-encode all interpolated values. |
| Controllers/AuthController.cs | 19-31 | The login endpoint has no rate limiting or account lockout, enabling brute-force attacks. | Add rate-limiting middleware and temporary lockout after repeated failures. |
| appsettings.json | 3 | `TrustServerCertificate=True` disables TLS certificate validation for the database connection. | Use a properly trusted certificate and remove the flag. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/UserService.cs | 72 | `GetUsersPage` computes `skip = page * pageSize`, so page 1 skips the first `pageSize` rows — off-by-one. | Use `(page - 1) * pageSize`. |
| Services/TransactionService.cs | 42-44 | `Transfer` checks `fromBalance >= amount` but deducts `amount + fee`, so the balance can go negative. | Check `fromBalance >= totalDebit`. |
| Services/TransactionService.cs | 25 | `Transfer` rejects `amount < 0` but allows zero-amount transfers. | Use `amount <= 0`. |
| Services/TransactionService.cs | 23 | `Transfer` has no check that `fromUserId != toUserId`, so a self-transfer silently burns the fee. | Reject self-transfers explicitly. |
| Services/TransactionService.cs | 68 | `Deposit` grants a 5% bonus via `amount * 0.05m * 1` — the `* 1` is a no-op and 5% per deposit is almost certainly the wrong rate. | Remove or correct the rate and drop the meaningless `* 1`. |
| Services/TransactionService.cs | 39-48 | The fee is deducted from the sender but never recorded on the transaction or credited anywhere — money vanishes from the system. | Persist the fee on the transaction row or credit a fee account. |
| Services/TransactionService.cs | 63-75 | `Deposit` never verifies the user exists — the UPDATE affects 0 rows but a transaction is still recorded and success returned. | Check rows affected and fail when the user is missing. |
| Services/TransactionService.cs | 77-85 | `IsWithinDailyLimit` is never called, so `MaxTransactionsPerDay` is not enforced anywhere. | Invoke it in `Transfer` (and `Deposit`) and reject when over the limit. |
| Services/UserService.cs | 68-76 | `GetUsersPage` never validates `page >= 1` or `pageSize >= 1` — page 0 duplicates page 1 and negative values produce invalid SQL. | Clamp both parameters to sensible minimums. |
| Services/AuthService.cs | 98-108 | `ValidateToken` returns `true` unconditionally without inspecting the token. | Remove the early return and actually validate signature and expiry. |
| Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` appends the separator after the final item, producing a trailing separator. | Use `string.Join`. |
| Helpers/StringHelper.cs | 56 | `ObfuscateAccount` uses `account[^4..]`, which throws for strings shorter than 4 characters. | Guard `length <= 4` before slicing. |
| Services/UserService.cs | 38-50 | `UpdateUser` returns `true` even when the id matches no row. | Check rows affected and return `false` when zero. |
| Services/UserService.cs | 52-66 | `DeleteUser` returns `true` even when nothing was deleted. | Check rows affected and return `false` when zero. |
| Services/TransactionService.cs | 36-48 | `Transfer` reads balances and writes them back with no locking or transaction — concurrent transfers can lose updates. | Use a transaction with `UPDLOCK` or optimistic concurrency on the balance column. |
| Services/AuthService.cs | 55 | The backdoor user is created with `Id = 0`, so its tokens reference a user that cannot exist in any table. | Remove the backdoor (see security section). |
| Services/UserService.cs | 95-99 | `SearchUsers` with a null or empty `query` produces `LIKE '%%'`, which matches and returns every user. | Return an empty result or reject empty queries. |
| Services/TransactionService.cs | 47-48 | `Transfer` interpolates `decimal` values into SQL using current culture — in comma-decimal locales the SQL breaks or misparses. | Use parameters, which also fixes injection. |
| Services/TransactionService.cs | 70-71 | `Deposit` has the same culture-sensitive decimal interpolation. | Use parameters. |
| Services/TransactionService.cs | 90 | `RecordTransaction` interpolates the `amount` decimal with the same culture risk. | Use parameters. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/UserService.cs | 105-108 | `SearchUsers` catches all exceptions and returns an empty list — callers cannot distinguish "no results" from "database down". | Let exceptions propagate or return a result type carrying status. |
| Services/EmailService.cs | 75-78 | `SendWelcomeEmail` catches broad `Exception` and only writes to the console — failures vanish silently. | Log via `ILogger` and surface or queue the failure. |
| Services/EmailService.cs | 56 | Retry failures in `SendTransferNotification` are logged with `Console.WriteLine` instead of `ILogger`. | Inject and use `ILogger<EmailService>`. |
| Services/TransactionService.cs | 44-50 | `Transfer`'s two balance UPDATEs and the INSERT are not wrapped in a database transaction — a mid-sequence failure leaves inconsistent balances. | Wrap all three statements in a single `SqlTransaction`. |
| Services/TransactionService.cs | 70-73 | `Deposit`'s UPDATE and `RecordTransaction` INSERT are not atomic. | Wrap both in a single transaction. |
| Services/TransactionService.cs | 50-55 | `SendTransferNotification` runs after the DB writes — if email throws, the client receives an error although the transfer already committed. | Queue the email for background sending or make it non-throwing after commit. |
| Controllers/UserController.cs | 50-52 | `UpdateUser`'s catch-all returns `ex.Message` in a 500 — internal details leak to the client. | Log the exception and return a generic message. |
| Controllers/UserController.cs | 46-48 | `UpdateUser` returns the raw `ArgumentException.Message` to HTTP clients. | Use model validation instead of relaying exception text. |
| Controllers/UserController.cs | 21-29 | `GetUser` has no try/catch, so the `ArgumentException` thrown by `GetUserById` becomes an unhandled 500 (with developer-page detail). | Validate the id in the controller and return 400/404. |
| Controllers/AuthController.cs | 19-31 | No rate limiting or account lockout protects the login endpoint. | Add rate limiting and lockout after repeated failures. |
| Controllers/TransactionController.cs | 26-27 | `int.Parse(userIdClaim!)` throws `NullReferenceException`/`FormatException` on a missing or malformed claim, producing an unhandled 500. | Use `int.TryParse` and return 401 on failure. |
| Controllers/TransactionController.cs | 40-41 | `Deposit` repeats the unguarded `int.Parse(userIdClaim!)` pattern. | Same `int.TryParse` fix. |
| Controllers/TransactionController.cs | 48-59 | `Refund` only catches `NotImplementedException`; any other exception is unhandled. | Add a general handler that logs and returns a generic 500. |
| Services/AuthService.cs | 32-38 | `Login` has no handling for `SqlException` — a DB outage surfaces as a raw 500. | Catch `SqlException` and return a generic 503. |
| Services/EmailService.cs | 45-60 | The retry loop retries immediately with no delay, hammering the SMTP server on failure. | Add exponential backoff between attempts. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| Data/DatabaseHelper.cs | 28-33 | `ExecuteQuery` never closes or disposes the `SqlConnection`, `SqlCommand`, or `SqlDataAdapter` obtained from `GetOpenConnection`. | Wrap all three in `using` statements. |
| Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` calls `Close()` but never `Dispose()`, and `Close()` is skipped entirely if `ExecuteNonQuery` throws. | Use `using` on the connection and command. |
| Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection` returns an open connection to callers with no disposal contract — every current caller leaks it. | Have the helper own the connection lifetime internally. |
| Services/AuthService.cs | 34-38 | `Login` creates a `SqlConnection`, `SqlCommand`, and `SqlDataReader` that are never closed or disposed on any path, success or failure. | Wrap connection, command, and reader in `using` blocks. |
| Services/EmailService.cs | 16, 22-31 | `SmtpClient` is held as an instance field for the service's lifetime — never disposed and not thread-safe. | Create it per send inside a `using` block. |
| Services/EmailService.cs | 39-43 | The `MailMessage` in `SendTransferNotification` is never disposed. | Use `using var message = ...`. |
| Services/EmailService.cs | 69 | The `MailMessage` in `SendWelcomeEmail` is never disposed. | Use `using var message = ...`. |
| Services/EmailService.cs | 89 | The `MailMessage` in `SendWelcomeEmailHtml` is never disposed. | Use `using var message = ...`. |
| Data/DatabaseHelper.cs | 44 | The `SqlDataAdapter` in `ExecuteQuerySafe` is not disposed. | Wrap the adapter in `using`. |
| Data/DatabaseHelper.cs | 74 | The `SqlAdapter` in `ExecuteQueryWithParams` is not disposed. | Wrap the adapter in `using`. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| Program.cs | 16, 28 | `jwtSecret` read from config is passed to `Encoding.UTF8.GetBytes(jwtSecret!)` — null if the key is missing, crashing startup with an opaque `ArgumentNullException`. | Validate the secret at startup and fail fast with a clear message. |
| Services/AuthService.cs | 70 | `GenerateJwtToken` uses `_config["Jwt:SecretKey"]!` with the same null risk. | Same startup validation fix. |
| Controllers/TransactionController.cs | 26-27 | `User.FindFirst(...)?.Value` is followed by `int.Parse(userIdClaim!)` — a null claim causes `NullReferenceException`. | Use `int.TryParse` and return 401 when the claim is missing. |
| Controllers/TransactionController.cs | 40-41 | `Deposit` repeats the `int.Parse(userIdClaim!)` null-forgiving pattern. | Same fix. |
| Services/TransactionService.cs | 36 | `fromUserTable.Rows[0]` is indexed without checking `Rows.Count` — throws `IndexOutOfRangeException` when the sender does not exist. | Check `Rows.Count == 0` and return a "user not found" failure. |
| Services/TransactionService.cs | 37 | `toUserTable.Rows[0]` is indexed without any count check for the recipient. | Same check. |
| Helpers/StringHelper.cs | 13 | `IsValidEmail` dereferences `email.Length` with no null check. | Add a null guard. |
| Helpers/StringHelper.cs | 22 | `IsValidUsername` dereferences `username.Length` with no null check. | Add a null guard. |
| Helpers/StringHelper.cs | 45 | `MaskAccountNumber` dereferences `accountNumber.Length` with no null check. | Add a null guard. |
| Helpers/StringHelper.cs | 56 | `ObfuscateAccount` slices `account[^4..]` with no null or length guard. | Guard null and length < 4. |
| Services/EmailService.cs | 25-27 | `_config["Email:Username"]` and `_config["Email:Password"]` may be null and are passed straight into `NetworkCredential`. | Validate email config at startup. |
| Controllers/AuthController.cs | 20-22 | `Login` uses `request.Username`/`request.Password` without a null check on the model-bound body. | Add `[Required]` attributes and a null guard. |
| Controllers/TransactionController.cs | 24-29 | `Transfer` uses `request.ToUserId`/`Amount`/`Description` without a null check on the request object. | Add `[Required]` and validate. |
| Controllers/TransactionController.cs | 38-43 | `Deposit` uses `request.Amount` without a null check on the request object. | Add `[Required]` and validate. |
| Controllers/UserController.cs | 39-43 | `UpdateUser` uses `request.Email`/`request.Username` without a null check on the bound body. | Add `[Required]` attributes and a null guard. |

## 6. Dead Code

Method inventory checked (Step 1): AuthController.Login; TransactionController.Transfer, Deposit, Refund; UserController.GetUser, GetUsers, UpdateUser, DeleteUser, SearchUsers, GetAuditLog; DatabaseHelper.GetOpenConnection, ExecuteQuery, ExecuteQuerySafe, ExecuteNonQuery, TableExists, ExecuteQueryWithParams; StringHelper.IsValidEmail, IsValidUsername, JoinWithSeparator, JoinWithSeparatorFixed, MaskAccountNumber, ObfuscateAccount, ToTitleCase, IsBlank; AuthService.Login, HashPasswordMd5, GenerateJwtToken, HashPasswordSha1, ValidateToken; EmailService.SendTransferNotification, SendWelcomeEmail, BuildHtmlTemplate, SendWelcomeEmailHtml; TransactionService.Transfer, Deposit, IsWithinDailyLimit, RecordTransaction, FormatCurrency, RefundTransaction; UserService.GetUserById, UpdateUser, DeleteUser, GetUsersPage, GetAuditReport, SearchUsers, MapRowToUser. Each name was then searched across all files (Step 2); rows below are names that appear only at their definition (Step 3).

| File | Line | Issue | Fix |
|---|---|---|---|
| Data/DatabaseHelper.cs | 59-65 | `TableExists` is defined but never called anywhere. | Delete it or use it in a startup schema check. |
| Data/DatabaseHelper.cs | 67-78 | `ExecuteQueryWithParams` is marked `[Obsolete]` and has no callers. | Delete it. |
| Helpers/StringHelper.cs | 11-18 | `IsValidEmail` has no callers — email is never validated anywhere in the app. | Wire it into `UpdateUser`/registration or delete it. |
| Helpers/StringHelper.cs | 20-27 | `IsValidUsername` has no callers. | Wire it into `UpdateUser` or delete it. |
| Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` has no callers. | Delete it (it is also broken). |
| Helpers/StringHelper.cs | 38-41 | `JoinWithSeparatorFixed` has no callers. | Delete it. |
| Helpers/StringHelper.cs | 43-52 | `MaskAccountNumber` has no callers. | Delete it or use it wherever account numbers are displayed. |
| Helpers/StringHelper.cs | 54-57 | `ObfuscateAccount` has no callers. | Delete it. |
| Helpers/StringHelper.cs | 59-63 | `ToTitleCase` has no callers. | Delete it. |
| Helpers/StringHelper.cs | 65-71 | `IsBlank` has no callers. | Delete it. |
| Services/AuthService.cs | 91-96 | `HashPasswordSha1` has no callers. | Delete it. |
| Services/AuthService.cs | 98-108 | `ValidateToken` has no callers. | Delete it, or fix and use it for token validation. |
| Services/EmailService.cs | 63-79 | `SendWelcomeEmail` has no callers. | Delete it or call it from a registration flow. |
| Services/EmailService.cs | 86-92 | `SendWelcomeEmailHtml` has no callers. | Delete it. |
| Services/EmailService.cs | 81-84 | `BuildHtmlTemplate` is only called by the dead `SendWelcomeEmailHtml`, making it transitively dead. | Delete it together with `SendWelcomeEmailHtml`. |
| Services/TransactionService.cs | 77-85 | `IsWithinDailyLimit` has no callers. | Call it from `Transfer`/`Deposit` or delete it. |
| Services/TransactionService.cs | 94-97 | `FormatCurrency` has no callers. | Delete it or use it in notification messages. |
| Services/TransactionService.cs | 99-103 | `RefundTransaction` throws `NotImplementedException` yet is reachable from the live refund endpoint — non-stub code. | Implement it or remove the endpoint. |
| Services/TransactionService.cs | 12 | `MaxTransactionsPerDay` is referenced only inside the dead `IsWithinDailyLimit`. | Remove it with the method or actually enforce it. |
| Models/Transaction.cs | 3-13 | The `Transaction` class is never instantiated or referenced by any code. | Delete it or use it in `RecordTransaction` and read paths. |
| Models/User.cs | 7 | `User.Password` is never populated by any mapping code (`MapRowToUser` and `Login` both omit it). | Remove the property or map it (and never serialize it). |
| Models/User.cs | 13 | `User.LastLoginAt` is never read or written anywhere. | Update it on successful login or remove it. |
| Services/UserService.cs | 11 | `_requestCount` is incremented but never read. | Delete the field. |
| Services/AuthService.cs | 105-107 | Code after the unconditional `return true` in `ValidateToken` is unreachable. | Remove the early return or the dead block. |
| Helpers/StringHelper.cs | 29 vs 38 | Duplicate join implementations (broken `JoinWithSeparator` and fixed `JoinWithSeparatorFixed`) coexist and neither is called. | Keep only direct `string.Join` usage. |
| Helpers/StringHelper.cs | 43 vs 54 | `MaskAccountNumber` and `ObfuscateAccount` are duplicate implementations of the same masking behavior. | Keep exactly one. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| Data/DatabaseHelper.cs | 16 | Hardcoded fallback connection string embedded in source instead of configuration. | Remove the fallback entirely. |
| Services/AuthService.cs | 17 | Backdoor password constant `AdminBypassPassword` hardcoded in source. | Remove it (see security). |
| Services/AuthService.cs | 53 | Magic string `"admin"` for the bypass username. | Remove the backdoor. |
| Services/AuthService.cs | 55 | Magic role string `"SuperAdmin"`. | Use a shared role-constants class. |
| Services/AuthService.cs | 84 | Token lifetime of 30 days hardcoded via `AddDays(30)`. | Move the lifetime to configuration. |
| Services/TransactionService.cs | 11 | The 1.5% fee rate is a source constant rather than a configurable business value. | Move `TransactionFeeRate` to `appsettings.json`. |
| Services/TransactionService.cs | 65 | Deposit cap `1000000` used inline. | Named constant `MaxDepositAmount` (ideally in config). |
| Services/TransactionService.cs | 68 | Interest rate `0.05m` used inline. | Named constant `DepositBonusRate` in config. |
| Services/TransactionService.cs | 73 | Sentinel `FromUserId = 0` used inline. | Named constant such as `SystemUserId`. |
| Services/TransactionService.cs | 50 | Transaction type literal `"Transfer"` used inline. | Introduce a `TransactionType` enum. |
| Services/TransactionService.cs | 73 | Transaction type literal `"Deposit"` used inline. | Same enum. |
| Services/TransactionService.cs | 90 | Status literal `'Completed'` used inline. | Named constant or `TransactionStatus` enum. |
| Services/UserService.cs | 22-23 | Magic number `1000000` for max user id in `GetUserById`. | Shared named constant `MaxUserId`. |
| Services/UserService.cs | 42-43 | The same `1000000` magic number repeated in `UpdateUser`. | Same shared constant. |
| Services/UserService.cs | 56-57 | The same `1000000` magic number repeated a third time in `DeleteUser`. | Same shared constant. |
| Services/UserService.cs | 70 | Max page size `50` used inline. | Named constant `MaxPageSize`. |
| Helpers/StringHelper.cs | 13 | Email max length `254` used inline. | Named constant `MaxEmailLength`. |
| Helpers/StringHelper.cs | 22 | Username bounds `3` and `20` used inline. | Named constants `MinUsernameLength`/`MaxUsernameLength`. |
| Helpers/StringHelper.cs | 45 | Visible-digits count `4` used inline. | Named constant `VisibleAccountDigits`. |
| Helpers/StringHelper.cs | 56 | Mask prefix `"****"` and slice length `4` used inline. | Named constants. |
| Services/EmailService.cs | 40 | Sender address `"notifications@company.com"` hardcoded (first of three occurrences). | Named constant or `Email:SenderAddress` config key. |
| Services/EmailService.cs | 67 | Support address `"support@company.com"` hardcoded in the welcome body. | Move to configuration. |
| Services/EmailService.cs | 69 | `"notifications@company.com"` repeated in `SendWelcomeEmail`. | Same shared constant. |
| Services/EmailService.cs | 89 | `"notifications@company.com"` repeated a third time in `SendWelcomeEmailHtml`. | Same shared constant. |
| Services/EmailService.cs | 24 | Default SMTP port `25` inline in the null-coalesce. | Named constant or config-only value. |
| Program.cs / Services/AuthService.cs | 16 / 70 | Config key string `"Jwt:SecretKey"` duplicated in two files. | Centralize config keys in a constants or options class. |
| Data/DatabaseHelper.cs / Services/AuthService.cs | 15 / 34 | Connection-string name `"DefaultConnection"` duplicated in two files. | Centralize the name. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| Helpers/StringHelper.cs | 31-34 | `JoinWithSeparator` builds strings with `+=` inside a loop — O(n²). | Use `string.Join` or `StringBuilder`. |
| Services/UserService.cs | 87-92 | `GetAuditReport` concatenates with `+=` inside a loop — O(n²). | Use `string.Join` or `StringBuilder`. |
| Helpers/StringHelper.cs | 16 | `new Regex(...)` is constructed on every `IsValidEmail` call. | Make it a `static readonly Regex` (or source-generated). |
| Helpers/StringHelper.cs | 25 | `new Regex(...)` is constructed on every `IsValidUsername` call. | Same `static readonly` fix. |
| Services/UserService.cs | 10 | `static List<string> _auditLog` is shared mutable static state with no synchronization and unbounded growth. | Replace with a thread-safe persistent audit store. |
| Services/UserService.cs | 11 | `static int _requestCount` is mutated from multiple threads without `Interlocked`. | Remove it (never read) or use `Interlocked.Increment`. |
| Helpers/StringHelper.cs | 65-71 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Delete it and call the BCL method. |
| Helpers/StringHelper.cs | 38-41 | `JoinWithSeparatorFixed` duplicates `string.Join`. | Delete it. |
| Helpers/StringHelper.cs | 54-57 | `ObfuscateAccount` duplicates `MaskAccountNumber` with different edge-case behavior. | Keep one implementation. |
| Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection` leaks resource ownership to callers with no documented contract. | Have helpers own the connection lifetime and document it. |
| Services/EmailService.cs | 56, 77 | `Console.WriteLine` is used for logging instead of `ILogger`. | Inject `ILogger<EmailService>`. |
| Services/EmailService.cs | 45-60 | The retry loop has no backoff strategy between attempts. | Add a delay with exponential backoff. |
| Services/UserService.cs | 20-23 | The id validation block (`id <= 0` / `id > 1000000`) is duplicated in `GetUserById`. | Extract a shared `ValidateUserId` method. |
| Services/UserService.cs | 40-43 | The same validation block is duplicated in `UpdateUser`. | Same shared method. |
| Services/UserService.cs | 54-57 | The same validation block is duplicated a third time in `DeleteUser`. | Same shared method. |
| Services/AuthService.cs | 34 | `Login` builds its own `SqlConnection` instead of using the injected `DatabaseHelper`, creating two data-access paths. | Route all data access through `DatabaseHelper`. |
| Services/TransactionService.cs | 28-34 | `Transfer` issues the identical load-user query twice inline. | Extract a private `GetUserById` helper. |
| Services/AuthService.cs / Services/UserService.cs | 40-50 / 111-123 | Two separate user-mapping implementations exist (reader-based in `Login`, DataRow-based in `MapRowToUser`). | Consolidate into one mapping path. |
| Services/TransactionService.cs | 23-61 | `Transfer` carries seven responsibilities: validate input, load both users, compute fee, check funds, persist two updates, record the transaction, and send email. | Split into `ValidateTransfer`, `LoadUser`, a transactional `ApplyBalances`, and a `Notify` step. |
| Services/AuthService.cs | 28-59 | `Login` mixes DB authentication, the backdoor check, and row mapping. | Extract `MapUser(reader)` and remove the backdoor. |
| Services/EmailService.cs | 34-61 | `SendTransferNotification` mixes message construction, retry policy, and sending. | Extract `BuildTransferMessage` and a `SendWithRetry` helper. |
| Services/TransactionService.cs | 63-75 | `Deposit` mixes validation, bonus computation, persistence, and transaction recording. | Split into validation, calculation, and transactional persistence helpers. |
| Services/UserService.cs | 95-109 | `SearchUsers` mixes data access, result mapping, and exception suppression. | Let exceptions propagate and reuse a shared mapping loop. |
| Controllers/TransactionController.cs | 51-59 | Catching `NotImplementedException` as HTTP control flow is an anti-pattern. | Remove the endpoint until the feature is implemented. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally regardless of environment. | Gate on `app.Environment.IsDevelopment()`. |
| Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry validation. | Set it to `true`. |
| Program.cs | 36 | `app.UseHttpsRedirection()` is commented out. | Re-enable it. |
| Program.cs | 38 | CORS is configured inline with `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`. | Register a named policy in services restricted to known origins. |
| appsettings.json | 17-21 | Debug log levels are set for `Default`, `Microsoft`, and `System` in the only config file. | Use `Information`/`Warning` and override per environment. |
| appsettings.Production.json | — | No `appsettings.Production.json` exists to override the development-oriented settings. | Add environment-specific configuration files. |
| appsettings.json | 3 | The base config references the production host `prod-db.internal` with embedded credentials. | Move environment-specific values out of the base file and into secret storage. |
| SampleBankingApp.csproj | 8-9 | `DebugSymbols=true` and `DebugType=full` apply to all builds including release. | Condition both on the Debug configuration. |
| SampleBankingApp.csproj | 15 | `Newtonsoft.Json 12.0.3` is outdated (pre-13.0.x has known advisories) and is not referenced by any code in the repo. | Remove the package, or upgrade to 13.0.3 if it is actually needed. |
| SampleBankingApp.csproj | 14 | `System.Data.SqlClient 4.8.6` is the legacy, maintenance-only data provider. | Migrate to `Microsoft.Data.SqlClient`. |
| SampleBankingApp.csproj | 13, 16 | `System.IdentityModel.Tokens.Jwt 7.0.0` is explicitly pinned alongside `JwtBearer 8.0.0`, which can conflict with the transitive version. | Remove the explicit pin and let JwtBearer resolve its dependency. |
| SampleBankingApp.csproj | 7 | `TreatWarningsAsErrors` is set to false, letting warnings (including obsolete-usage CS0618) slip through builds. | Enable it and fix the warnings. |
| appsettings.json | 23 | `AllowedHosts: "*"` permits any host header. | Restrict to the expected hostnames. |
| appsettings.json | 6 | The JWT signing secret is stored as plaintext in the shared config file. | Move to a secret store or environment variable. |
| Program.cs | 16 | No startup validation confirms required configuration (JWT secret, email settings, connection string) is present. | Use the options pattern with `ValidateOnStart`. |

## 10. Missing Unit Tests

No test project exists anywhere in the repository — there is no test `.csproj`, no test directory, and no test framework reference.

| File | Line | Issue | Fix |
|---|---|---|---|
| (solution root) | — | No test project exists for the entire application. | Add an xUnit/NUnit test project referencing `SampleBankingApp`. |
| Services/TransactionService.cs | 25 | `Transfer` amount boundary behavior (zero, negative, positive) is untested. | Add tests asserting zero and negative amounts are rejected. |
| Services/TransactionService.cs | 42 | The balance-vs-balance-plus-fee boundary is untested — the current negative-balance bug would be caught here. | Add tests for balance exactly equal to amount and to amount plus fee. |
| Services/TransactionService.cs | 23 | Self-transfer behavior is untested. | Add a test asserting self-transfers are rejected. |
| Services/TransactionService.cs | 36-37 | Transfers with a nonexistent sender or recipient are untested. | Add tests asserting a clean failure instead of `IndexOutOfRangeException`. |
| Services/TransactionService.cs | 39 | Fee rounding (`Math.Round` to 2 decimals) is untested. | Add tests for amounts where rounding matters (e.g., $0.01 yielding a $0.00 fee). |
| Services/TransactionService.cs | 65 | Deposit boundaries (0, negative, 1000000, 1000000.01) are untested. | Add table-driven boundary tests. |
| Services/TransactionService.cs | 68 | The deposit bonus calculation is untested. | Add tests pinning the intended rate once corrected. |
| Services/UserService.cs | 72 | The pagination off-by-one is untested — page 1 currently skips the first page. | Add tests asserting page 1 returns the first rows and page 2 skips correctly. |
| Services/UserService.cs | 70 | `pageSize` clamping and invalid `page`/`pageSize` values are untested. | Add tests for pageSize 51, 0, and negative, and page 0 and negative. |
| Services/UserService.cs | 20-23 | `GetUserById` id boundaries (0, 1, 1000000, 1000001) are untested. | Add tests asserting the exact `ArgumentException` boundaries. |
| Services/AuthService.cs | 28 | `Login` success, wrong password, inactive user, and injection payloads are untested. | Add integration tests with a parameterized query and a seeded user table. |
| Services/AuthService.cs | 68 | `GenerateJwtToken` claims and expiry are untested. | Assert the `NameIdentifier`, `Name`, and `Role` claims and the expiry value. |
| Helpers/StringHelper.cs | 11-27 | Email and username validation boundaries (null, empty, 254/255 chars, 2/3/20/21 chars, invalid characters) are untested. | Add boundary-focused unit tests. |
| Services/UserService.cs | 95 | `SearchUsers` error path is untested — the current swallow makes "error" and "empty" indistinguishable. | Add a test asserting DB failures are distinguishable from empty results after the fix. |

---

**Priority summary:** fix the SQL injection in `Login`/`RecordTransaction`/`UpdateUser`/`SearchUsers`, remove the admin backdoor and hardcoded credentials, replace MD5 password hashing, restore `ValidateLifetime` and HTTPS, add ownership/role checks to the user endpoints, wrap `Transfer` in a database transaction with a fee-inclusive balance check, and correct the pagination off-by-one — these are the defects most likely to cause financial loss or a breach in production.