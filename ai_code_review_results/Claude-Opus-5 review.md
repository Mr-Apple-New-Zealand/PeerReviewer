# Code Review — SampleBankingApp (main @ 67ece22)

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/AuthService.cs | 32 | `Login` builds the authentication query by interpolating `username` and `hashedPassword` directly into SQL, allowing full authentication bypass via `' OR 1=1--`. | Use a parameterised `SqlCommand` with `@Username`/`@Password` parameters. |
| Services/AuthService.cs | 17, 53-56 | A hardcoded backdoor credential `AdminBypassPassword = "SuperAdmin2024"` grants `SuperAdmin` role with `Id = 0` to anyone who knows it. | Delete the constant and the bypass branch entirely. |
| Services/AuthService.cs | 30, 61-66 | `HashPasswordMd5` uses unsalted MD5, which is broken and trivially reversible via rainbow tables. | Replace with PBKDF2/BCrypt/Argon2 via `Rfc2898DeriveBytes` or ASP.NET Core `PasswordHasher<T>`. |
| Services/AuthService.cs | 91-96 | `HashPasswordSha1` uses unsalted SHA-1, also cryptographically broken. | Remove the method (it is unused) and standardise on a modern KDF. |
| Services/AuthService.cs | 84 | JWT lifetime of 30 days is far too long for a banking application and cannot be revoked. | Issue short-lived (15–60 minute) access tokens with a refresh-token flow. |
| Services/AuthService.cs | 98-107 | `ValidateToken` returns `true` for any non-empty string, so if it is ever wired up it accepts forged tokens. | Delete it or implement real validation with `JwtSecurityTokenHandler.ValidateToken`. |
| Services/UserService.cs | 47 | `UpdateUser` interpolates `email` and `username` into an `UPDATE` statement, permitting SQL injection and mass row updates. | Use `ExecuteQuerySafe`-style parameterised commands for the update. |
| Services/UserService.cs | 61 | `DeleteUser` interpolates `id` into a `DELETE` statement instead of parameterising it. | Parameterise the `DELETE` with `@Id`. |
| Services/UserService.cs | 99 | `SearchUsers` passes `$"Username LIKE '%{query}%'"` into a raw where-clause helper, an unauthenticated-input SQL injection point. | Use a parameterised query with `@Query` and escape LIKE wildcards. |
| Services/TransactionService.cs | 47 | `Transfer` interpolates `newFromBalance` and `fromUserId` into an `UPDATE` statement. | Parameterise the balance update. |
| Services/TransactionService.cs | 48 | `Transfer` interpolates `newToBalance` and `toUserId` into a second `UPDATE` statement. | Parameterise the balance update. |
| Services/TransactionService.cs | 71 | `Deposit` interpolates the computed amount and `userId` into an `UPDATE` statement. | Parameterise the deposit update. |
| Services/TransactionService.cs | 89-90 | `RecordTransaction` interpolates the user-supplied `description` and `type` into an `INSERT`, allowing stored SQL injection. | Parameterise the `INSERT` statement. |
| Data/DatabaseHelper.cs | 26-34 | `ExecuteQuery(tableName, whereClause)` concatenates raw SQL fragments supplied by callers and is inherently injectable. | Remove the method and force callers through `ExecuteQuerySafe`. |
| Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery(string sql)` accepts an arbitrary raw SQL string with no parameter support, which is why every writer interpolates. | Add a parameterised overload `ExecuteNonQuery(string sql, Dictionary<string,object> parameters)` and delete the raw variant. |
| Data/DatabaseHelper.cs | 15-16 | Hardcoded fallback connection string embeds the `sa` account and password `Admin1234!` in source control. | Throw on missing configuration instead of falling back to a literal credential. |
| appsettings.json | 3 | Production connection string with `sa` account, password `Admin1234!`, and `TrustServerCertificate=True` is committed to the repository. | Move to environment variables/Key Vault and use least-privilege, integrated auth with certificate validation. |
| appsettings.json | 6 | JWT signing key `"mysecretkey"` is weak (below 256 bits for HMAC-SHA256) and committed to source control. | Generate a 32+ byte random key and supply it from a secret store. |
| appsettings.json | 14 | SMTP password `EmailPass99` is committed to source control. | Move to a secret store and rotate the credential. |
| Services/EmailService.cs | 29 | `EnableSsl = false` sends SMTP credentials and customer transaction data in cleartext. | Set `EnableSsl = true` and use port 587/465. |
| Program.cs | 24 | `ValidateLifetime = false` means expired tokens are accepted forever. | Set `ValidateLifetime = true` and configure `ClockSkew`. |
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, exposing stack traces and connection details in production. | Guard with `if (app.Environment.IsDevelopment())` and add `UseExceptionHandler` otherwise. |
| Program.cs | 36 | `app.UseHttpsRedirection()` is commented out, allowing tokens and credentials over plain HTTP. | Uncomment it and add HSTS. |
| Program.cs | 38 | CORS policy allows any origin, any method and any header, enabling cross-site API abuse. | Restrict to a named allow-list of trusted origins and required methods. |
| Controllers/UserController.cs | 38-54 | `UpdateUser` has no ownership or role check, so any authenticated user can change any other user's email/username (account takeover). | Compare `id` against the `NameIdentifier` claim or require an admin role. |
| Controllers/UserController.cs | 56-69 | `DeleteUser` has no ownership or role check, so any authenticated user can delete any account. | Require `[Authorize(Roles = "Admin")]` plus an ownership check. |
| Controllers/UserController.cs | 21-29 | `GetUser` lets any authenticated user read any other user's email and balance. | Enforce that the caller owns the record or is an administrator. |
| Controllers/UserController.cs | 71-76 | `SearchUsers` exposes the full user table (including balances) to any authenticated caller. | Restrict to admins and project only non-sensitive fields. |
| Controllers/UserController.cs | 78-82 | `GetAuditLog` returns the whole audit trail with no role restriction. | Add `[Authorize(Roles = "Admin")]`. |
| Controllers/TransactionController.cs | 48-60 | `Refund` has no ownership check on `transactionId`, so any user could refund any transaction once implemented. | Verify the transaction belongs to the caller or require an admin role. |
| Controllers/AuthController.cs | 19-31 | `Login` has no rate limiting, CAPTCHA, or account lockout, permitting unlimited credential stuffing against MD5 hashes. | Add ASP.NET Core rate limiting plus failed-attempt lockout. |
| Controllers/AuthController.cs | 26 | The failure message "Username not found or incorrect password" hints at user enumeration semantics. | Return a single generic message such as "Invalid credentials". |
| SampleBankingApp.csproj | 8-9 | `DebugSymbols=true` and `DebugType=full` apply to Release builds, shipping full PDBs and easing reverse engineering. | Move these to a Debug-only `PropertyGroup` and use `portable`/`none` for Release. |
| SampleBankingApp.csproj | 15 | `Newtonsoft.Json 12.0.3` has known advisories (e.g. CVE-2024-21907 deep-recursion DoS) and is not even referenced by any code. | Remove the package or upgrade to 13.0.3+. |
| SampleBankingApp.csproj | 14 | `System.Data.SqlClient 4.8.6` is the legacy, maintenance-mode provider with prior TLS/security advisories. | Migrate to `Microsoft.Data.SqlClient` (latest patch). |
| appsettings.json | 23 | `AllowedHosts: "*"` disables host filtering, enabling host-header attacks. | List the concrete public hostnames. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/UserService.cs | 72 | `GetUsersPage` computes `skip = page * pageSize`, so page 1 skips the first page and the first `pageSize` records are unreachable. | Use `skip = (page - 1) * pageSize`. |
| Services/UserService.cs | 68-72 | `GetUsersPage` never validates that `page >= 1` or `pageSize >= 1`, so a negative page produces a negative `OFFSET` and a SQL error. | Clamp `page` to a minimum of 1 and `pageSize` to the range 1–50. |
| Services/TransactionService.cs | 42 | `Transfer` checks `fromBalance >= amount` but debits `totalDebit = amount + fee`, so a balance between `amount` and `amount+fee` goes negative. | Compare against `totalDebit` instead of `amount`. |
| Services/TransactionService.cs | 25 | `Transfer` rejects only `amount < 0`, allowing a zero-value transfer that still writes rows and sends email. | Change the guard to `amount <= 0`. |
| Services/TransactionService.cs | 23-61 | `Transfer` has no self-transfer check, and because both balances are read before either write, `fromUserId == toUserId` silently corrupts the balance. | Return an error when `fromUserId == toUserId`. |
| Services/TransactionService.cs | 39-50 | The `fee` is deducted from the sender but never credited to a fee/GL account nor recorded on the transaction row, so money vanishes and cannot be reconciled. | Record the fee on the transaction and post it to a fee account. |
| Services/TransactionService.cs | 68 | `Deposit` credits an "interest bonus" of 5% (`amount * 0.05m * 1`) on every deposit, which is almost certainly meant to be 1% or nothing at all. | Correct the rate, move it to configuration, and drop the meaningless `* 1`. |
| Services/TransactionService.cs | 71-73 | `Deposit` credits `amount + interestBonus` but records only `amount` in the `Transactions` table, so ledger and balance disagree. | Record the bonus as its own transaction row. |
| Services/TransactionService.cs | 63-75 | `Deposit` never verifies the user exists, so a bogus id silently updates zero rows and still returns "Deposit successful". | Check the affected row count returned by `ExecuteNonQuery`. |
| Services/TransactionService.cs | 77-85 | `IsWithinDailyLimit` is never invoked, so `MaxTransactionsPerDay` is not enforced anywhere. | Call it from `Transfer` (and `Deposit`) before performing writes. |
| Services/TransactionService.cs | 36-37 | `Transfer` indexes `Rows[0]` for both accounts, so a non-existent `toUserId` throws instead of returning "recipient not found". | Check `Rows.Count == 0` and return a friendly failure. |
| Services/UserService.cs | 47-49 | `UpdateUser` returns `true` regardless of rows affected, reporting success for a non-existent id. | Return `ExecuteNonQuery(...) > 0` and surface a 404 from the controller. |
| Services/UserService.cs | 61-65 | `DeleteUser` likewise returns `true` even when no row was deleted. | Return the affected row count and map zero to `NotFound`. |
| Services/UserService.cs | 38-50 | `UpdateUser` performs no email/username validation despite `StringHelper.IsValidEmail`/`IsValidUsername` existing. | Validate both inputs before writing. |
| Services/AuthService.cs | 98-107 | `ValidateToken` returns `true` immediately, making lines 105-107 unreachable and the expiry check ineffective. | Remove the early `return true` and implement real validation. |
| Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` appends the separator after the final element, producing a trailing separator. | Use `string.Join` (as `JoinWithSeparatorFixed` already does). |
| Helpers/StringHelper.cs | 56 | `ObfuscateAccount` uses `account[^4..]` with no length check, throwing `ArgumentOutOfRangeException` for accounts shorter than 4 characters. | Guard on `account.Length >= 4` as `MaskAccountNumber` does. |
| Helpers/StringHelper.cs | 13-17 | `IsValidEmail` accepts an empty local/domain of any shape below 254 chars and rejects nothing else, e.g. `a@b.c` variants with control characters. | Use `MailAddress` parsing or a stricter, well-tested pattern. |
| Services/AuthService.cs | 53-56 | The admin bypass is evaluated only after a failed DB lookup, so a real disabled `admin` row is silently overridden by a synthetic `SuperAdmin` user. | Remove the bypass. |
| Services/AuthService.cs | 44-49 | `Login` does not populate `CreatedAt`/`LastLoginAt` and never updates `LastLoginAt`, so the field on `User` is always default. | Update the last-login timestamp on successful authentication. |
| Services/UserService.cs | 22, 42, 56 | The `id > 1000000` ceiling is an arbitrary business rule that will reject legitimate users once the table exceeds a million rows. | Remove the ceiling or drive it from configuration. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/UserService.cs | 105-108 | `SearchUsers` catches all exceptions and returns an empty `List<User>`, so callers cannot distinguish "no matches" from "database down". | Log the exception and rethrow or return an explicit result type. |
| Services/EmailService.cs | 75-78 | `SendWelcomeEmail` swallows every exception and writes to `Console`, so failures are invisible to monitoring. | Log via `ILogger` and propagate or return a failure status. |
| Services/EmailService.cs | 56 | `SendTransferNotification` logs retry failures with `Console.WriteLine` rather than the logging pipeline. | Inject `ILogger<EmailService>` and log there. |
| Services/TransactionService.cs | 47-50 | `Transfer` performs two `UPDATE`s plus an `INSERT` with no database transaction, so a crash between them loses or duplicates money. | Wrap all three writes in a single `SqlTransaction` with an appropriate isolation level. |
| Services/TransactionService.cs | 52-55 | `SendTransferNotification` is called after the balances are already committed and rethrows after 3 retries, turning a successful transfer into a 500 for the caller. | Move notification onto a background queue/outbox after the transaction commits. |
| Services/TransactionService.cs | 70-73 | `Deposit` updates the balance and inserts the ledger row without a transaction. | Wrap both writes in one transaction. |
| Controllers/UserController.cs | 52 | `UpdateUser` returns raw `ex.Message` in a 500 response, leaking SQL/server details to clients. | Log the exception and return a generic message. |
| Controllers/UserController.cs | 48 | `UpdateUser` returns `ex.Message` from `ArgumentException`, which is acceptable text today but couples internal wording to the API contract. | Return a structured validation `ProblemDetails` payload. |
| Controllers/UserController.cs | 41-53 | `UpdateUser` catches broad `Exception` without logging, so failures are never recorded. | Log with `_logger.LogError(ex, ...)` before returning 500. |
| Controllers/TransactionController.cs | 51-59 | `Refund` catches `NotImplementedException` and hides an unimplemented feature behind a 500 instead of a 501. | Return `StatusCode(501)` or remove the endpoint until implemented. |
| Controllers/TransactionController.cs | 23-35 | `Transfer` has no exception handling around the service call, so a `SqlException` surfaces as a developer-exception page. | Add a global exception-handling middleware/filter. |
| Controllers/AuthController.cs | 19-31 | `Login` lacks rate limiting or account lockout on repeated failures. | Add `AddRateLimiter` policies and lockout after N failed attempts. |
| Data/DatabaseHelper.cs | 26-57 | No method wraps ADO.NET calls in error handling, so raw `SqlException` text (schema names, server names) escapes to the API layer. | Catch, log and translate to a domain-level exception. |
| Services/UserService.cs | 45, 64 | Audit entries are appended to an in-memory list rather than a durable store, so audit evidence is lost on restart. | Persist audit entries to the database. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/AuthService.cs | 34-51 | `Login` opens a `SqlConnection` that is never closed or disposed on any path, leaking a pooled connection per login attempt. | Wrap the connection in `using`. |
| Services/AuthService.cs | 37 | The `SqlCommand` in `Login` is never disposed. | Declare it with `using`. |
| Services/AuthService.cs | 38 | The `SqlDataReader` in `Login` is never closed, holding the connection open even after the early `return`. | Use `using var reader = command.ExecuteReader();`. |
| Data/DatabaseHelper.cs | 28-33 | `ExecuteQuery` obtains a connection from `GetOpenConnection` and never closes it; the command and adapter are also undisposed. | Use `using` for connection, command and adapter. |
| Data/DatabaseHelper.cs | 52-56 | `ExecuteNonQuery` calls `connection.Close()` only on the success path, so a thrown `SqlException` leaks the connection; the command is never disposed. | Replace with `using` declarations. |
| Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection` hands an open connection to callers with no documented ownership contract, which is exactly why the two callers leak. | Remove it or rename/document it and return a wrapper the caller must dispose. |
| Data/DatabaseHelper.cs | 44 | The `SqlDataAdapter` in `ExecuteQuerySafe` is not disposed. | Wrap it in `using`. |
| Data/DatabaseHelper.cs | 74 | The `SqlDataAdapter` in `ExecuteQueryWithParams` is not disposed. | Wrap it in `using`. |
| Services/EmailService.cs | 16, 22-31 | `SmtpClient` is held as an instance field on a scoped service, so a new client (and socket) is created per request and never disposed. | Create and dispose an `SmtpClient` per send, or migrate to `MailKit` with a pooled, injected client. |
| Services/EmailService.cs | 6 | `EmailService` holds an `IDisposable` (`SmtpClient`) but does not implement `IDisposable`, so the DI container can never release it. | Implement `IDisposable`/`IAsyncDisposable` and dispose `_smtpClient`. |
| Services/EmailService.cs | 39-43 | The `MailMessage` in `SendTransferNotification` is never disposed, leaking attachment/stream handles. | Wrap in `using`. |
| Services/EmailService.cs | 69 | The `MailMessage` in `SendWelcomeEmail` is never disposed. | Wrap in `using`. |
| Services/EmailService.cs | 89 | The `MailMessage` in `SendWelcomeEmailHtml` is never disposed. | Wrap in `using`. |
| Services/TransactionService.cs | 28-48 | Each `Transfer` opens four separate connections (two queries, two updates) with no shared connection or transaction scope, exhausting the pool under load. | Perform the whole operation on one connection inside one transaction. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| Program.cs | 16, 28 | `jwtSecret` is read from configuration and null-forgiven into `Encoding.UTF8.GetBytes`, throwing `ArgumentNullException` at startup if the key is missing. | Validate with a null check and fail fast with a clear message. |
| Services/AuthService.cs | 70 | `GenerateJwtToken` passes `_config["Jwt:SecretKey"]!` to `Encoding.UTF8.GetBytes` with no null guard. | Read the key once into a validated field in the constructor. |
| Services/AuthService.cs | 81-82 | `_config["Jwt:Issuer"]` and `_config["Jwt:Audience"]` may be null, producing tokens without issuer/audience that then fail validation. | Validate both at startup. |
| Controllers/TransactionController.cs | 26-27 | `Transfer` passes `User.FindFirst(...)?.Value!` straight into `int.Parse`, throwing if the claim is absent or non-numeric. | Use `int.TryParse` on the claim and return `Unauthorized()` when it fails. |
| Controllers/TransactionController.cs | 40-41 | `Deposit` has the same unguarded `int.Parse(userIdClaim!)` pattern. | Use `int.TryParse` and return `Unauthorized()`. |
| Controllers/TransactionController.cs | 24 | `request` is used without a null check, so an empty or `null` JSON body throws an NRE at `request.ToUserId`. | Add `if (request is null) return BadRequest();` and `[ApiController]` model validation attributes. |
| Controllers/TransactionController.cs | 38 | `Deposit` dereferences `request.Amount` without a null check on the model-bound object. | Add a null guard. |
| Controllers/UserController.cs | 39-43 | `UpdateUser` dereferences `request.Email` and `request.Username` without a null check. | Add a null guard and `[Required]` attributes. |
| Controllers/AuthController.cs | 20-22 | `Login` dereferences `request.Username`/`request.Password` without a null check. | Add a null guard on `request`. |
| Controllers/UserController.cs | 72-74 | `SearchUsers` declares `string query` as non-nullable but model binding can pass null, which then flows into the SQL fragment. | Mark it `string?` and reject null/blank input. |
| Services/TransactionService.cs | 36 | `Transfer` accesses `fromUserTable.Rows[0]` without checking `Rows.Count > 0`. | Guard with a row-count check and return a failure result. |
| Services/TransactionService.cs | 37 | `Transfer` accesses `toUserTable.Rows[0]` without checking `Rows.Count > 0`. | Guard with a row-count check. |
| Services/TransactionService.cs | 53, 55 | `Transfer` casts `Rows[0]["Email"]` and `Rows[0]["Username"]` to `string`, throwing `InvalidCastException` if the column is `DBNull`. | Use `row.IsNull(...)` or `Convert.ToString` with a fallback. |
| Services/TransactionService.cs | 83 | `IsWithinDailyLimit` accesses `table.Rows[0]["TxCount"]` without a row-count check. | Guard the access. |
| Services/UserService.cs | 111-123 | `MapRowToUser` hard-casts every column, so a `DBNull` in `Email`, `Role`, `Balance` or `CreatedAt` throws `InvalidCastException`. | Use `DataRow.Field<T>()` with null handling and defaults. |
| Services/AuthService.cs | 44-49 | `Login` hard-casts reader columns, so a `NULL` `Email`/`Role`/`Balance` throws `InvalidCastException`. | Check `reader.IsDBNull(ordinal)` before casting. |
| Services/EmailService.cs | 22 | `new SmtpClient(_config["Email:SmtpHost"])` throws `ArgumentNullException` when the host is unconfigured. | Validate the host at construction and fail with a descriptive message. |
| Services/EmailService.cs | 65 | `SendWelcomeEmail` calls `username.ToUpper()` before any null check. | Add a null/empty guard on `username`. |
| Helpers/StringHelper.cs | 13 | `IsValidEmail` dereferences `email.Length` with no null check on a non-nullable-annotated parameter. | Return `false` for null input. |
| Helpers/StringHelper.cs | 22 | `IsValidUsername` dereferences `username.Length` with no null check. | Return `false` for null input. |
| Helpers/StringHelper.cs | 45 | `MaskAccountNumber` dereferences `accountNumber.Length` with no null check. | Guard against null. |
| Helpers/StringHelper.cs | 56 | `ObfuscateAccount` indexes `account[^4..]` with no null check. | Guard against null and short strings. |
| Helpers/StringHelper.cs | 32 | `JoinWithSeparator` enumerates `items` with no null check. | Guard with `ArgumentNullException.ThrowIfNull`. |

## 6. Dead Code

Every method defined in the source set was enumerated and each name searched across all files. Confirmed *used*: `DatabaseHelper.GetOpenConnection`, `ExecuteQuery`, `ExecuteQuerySafe`, `ExecuteNonQuery`; `AuthService.Login`, `HashPasswordMd5`, `GenerateJwtToken`; `EmailService.SendTransferNotification`, `BuildHtmlTemplate` (only from a dead caller); `TransactionService.Transfer`, `Deposit`, `RecordTransaction`, `RefundTransaction`; `UserService.GetUserById`, `UpdateUser`, `DeleteUser`, `GetUsersPage`, `GetAuditReport`, `SearchUsers`, `MapRowToUser`; all controller actions. The following have no caller anywhere:

| File | Line | Issue | Fix |
|---|---|---|---|
| Data/DatabaseHelper.cs | 59-65 | `TableExists` is defined but never called from any file. | Delete it or move it to a migration/diagnostics tool. |
| Data/DatabaseHelper.cs | 67-78 | `ExecuteQueryWithParams` is marked `[Obsolete]` and has no callers, yet remains in the codebase. | Delete the method. |
| Helpers/StringHelper.cs | 11-18 | `IsValidEmail` has no callers even though `UserService.UpdateUser` should be using it. | Wire it into `UpdateUser` or delete it. |
| Helpers/StringHelper.cs | 20-27 | `IsValidUsername` has no callers. | Wire it into `UpdateUser` or delete it. |
| Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` has no callers and is the broken variant kept alongside the fixed one. | Delete it. |
| Helpers/StringHelper.cs | 38-41 | `JoinWithSeparatorFixed` is the "fixed" duplicate of `JoinWithSeparator`, and it too has no callers. | Delete both and call `string.Join` directly at the (future) call site. |
| Helpers/StringHelper.cs | 43-52 | `MaskAccountNumber` has no callers. | Delete it or use it when returning account data. |
| Helpers/StringHelper.cs | 54-57 | `ObfuscateAccount` has no callers and duplicates `MaskAccountNumber`. | Delete one of the two duplicates. |
| Helpers/StringHelper.cs | 59-63 | `ToTitleCase` has no callers. | Delete it. |
| Helpers/StringHelper.cs | 65-71 | `IsBlank` has no callers and reimplements `string.IsNullOrWhiteSpace`. | Delete it. |
| Services/AuthService.cs | 91-96 | `HashPasswordSha1` has no callers and is a second, unused hashing scheme. | Delete it. |
| Services/AuthService.cs | 98-108 | `ValidateToken` has no callers; the JWT middleware performs validation instead. | Delete it. |
| Services/AuthService.cs | 105-107 | Lines after `return true;` in `ValidateToken` are unreachable code. | Remove the dead statements (compiler warning CS0162 is being ignored). |
| Services/AuthService.cs | 14 | The `_db` field is assigned in the constructor but never read, since `Login` builds its own connection. | Use `_db` for the query or remove the dependency. |
| Services/EmailService.cs | 63-79 | `SendWelcomeEmail` has no callers — no registration flow exists. | Delete it or wire it to a registration endpoint. |
| Services/EmailService.cs | 86-92 | `SendWelcomeEmailHtml` has no callers and duplicates `SendWelcomeEmail`. | Delete one variant. |
| Services/EmailService.cs | 81-84 | `BuildHtmlTemplate` is only referenced by the dead `SendWelcomeEmailHtml`, making it transitively dead. | Delete it with its only caller. |
| Services/TransactionService.cs | 77-85 | `IsWithinDailyLimit` has no callers, so `MaxTransactionsPerDay` is dead configuration too. | Call it from `Transfer`. |
| Services/TransactionService.cs | 94-97 | `FormatCurrency` has no callers. | Delete it or use it in `SendTransferNotification`'s body construction. |
| Services/TransactionService.cs | 99-103 | `RefundTransaction` is a `throw new NotImplementedException()` stub exposed through a live HTTP endpoint. | Implement it or remove both the method and the `POST /refund/{id}` route. |
| Services/UserService.cs | 11, 25, 59 | `_requestCount` is incremented in two methods but never read anywhere — write-only dead state. | Remove it or expose it via proper metrics. |
| Models/User.cs | 7 | The `Password` property is never populated or used by any mapper, and holding it on the DTO is a leak risk. | Remove it from the API-facing model. |
| Models/Transaction.cs | 3-13 | The `Transaction` class is never instantiated or mapped anywhere; transactions are written via raw SQL. | Use it in `RecordTransaction`/a query API or delete it. |
| Models/User.cs | 13 | `LastLoginAt` is never set or read by any code path. | Populate it on login or remove it. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/TransactionService.cs | 65 | The deposit cap `1000000` is an inline literal in `Deposit`. | Extract to a named constant sourced from configuration. |
| Services/TransactionService.cs | 68 | The interest rate `0.05m` (and the no-op `* 1`) is an inline literal in `Deposit`. | Extract to a configured `DepositBonusRate`. |
| Services/TransactionService.cs | 39 | The rounding precision `2` in `Math.Round` is an inline literal. | Define a `CurrencyDecimals` constant. |
| Services/TransactionService.cs | 50 | The transaction type string `"Transfer"` is a magic string. | Use an enum or a `TransactionTypes` constants class. |
| Services/TransactionService.cs | 73 | The transaction type string `"Deposit"` is a magic string. | Use the same enum/constants class. |
| Services/TransactionService.cs | 90 | The status literal `'Completed'` is embedded in the SQL of `RecordTransaction`. | Use a `TransactionStatus` constant/enum. |
| Services/TransactionService.cs | 73 | The sentinel `0` for "no source user" in the `Deposit` call to `RecordTransaction` is unexplained. | Use a named constant such as `SystemUserId` or a nullable column. |
| Services/UserService.cs | 22, 42, 56 | The literal `1000000` id ceiling is repeated in `GetUserById`, `UpdateUser` and `DeleteUser`. | Extract to a single named constant. |
| Services/UserService.cs | 70 | The maximum page size `50` is an inline literal in `GetUsersPage`. | Extract to `MaxPageSize` in configuration. |
| Controllers/UserController.cs | 32 | The default `pageSize = 20` is hardcoded in the action signature, separate from the service's cap of 50. | Centralise paging defaults in a shared options class. |
| Services/AuthService.cs | 84 | The token lifetime `AddDays(30)` is hardcoded. | Move to `Jwt:ExpiryMinutes` in configuration. |
| Services/AuthService.cs | 53, 55 | The literals `"admin"` and `"SuperAdmin"` are hardcoded role/username strings. | Remove the backdoor and define role names as constants. |
| Services/EmailService.cs | 40, 69, 89 | The sender address `"notifications@company.com"` is repeated in three methods. | Read it once from `Email:FromAddress` configuration. |
| Services/EmailService.cs | 67 | The support address `"support@company.com"` is hardcoded in the email body. | Move to configuration or a template file. |
| Services/EmailService.cs | 24 | The default SMTP port `"25"` is a magic string fallback. | Define a named constant and validate the configured value. |
| Services/EmailService.cs | 36-37, 65-67 | Email body text is hardcoded in C# string interpolation. | Move bodies to resource files or a templating engine. |
| Helpers/StringHelper.cs | 13 | The maximum email length `254` is an inline literal. | Extract to `MaxEmailLength`. |
| Helpers/StringHelper.cs | 22 | The username bounds `3` and `20` are inline literals. | Extract to `MinUsernameLength`/`MaxUsernameLength`. |
| Helpers/StringHelper.cs | 45, 49, 50, 56 | The "last 4 digits" value `4` is repeated across `MaskAccountNumber` and `ObfuscateAccount`. | Extract to a `VisibleAccountDigits` constant. |
| Data/DatabaseHelper.cs | 15 | The configuration key `"DefaultConnection"` is a magic string also repeated in `AuthService.Login`. | Define a shared constant. |
| Services/AuthService.cs | 34 | `"DefaultConnection"` is repeated here, duplicating `DatabaseHelper`'s knowledge of the key. | Reuse `DatabaseHelper` rather than re-reading the connection string. |
| Program.cs | 16, 26, 27 | The configuration keys `"Jwt:SecretKey"`, `"Jwt:Issuer"` and `"Jwt:Audience"` are magic strings duplicated in `AuthService`. | Bind a strongly-typed `JwtOptions` via `IOptions<T>`. |
| Data/DatabaseHelper.cs | 63 | The schema literals `"Tables"` and `"BASE TABLE"` are inline in `TableExists`. | Extract to constants if the method is retained. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| Helpers/StringHelper.cs | 31-34 | `JoinWithSeparator` concatenates strings inside a loop, giving O(n²) allocation behaviour. | Use `string.Join` or `StringBuilder`. |
| Services/UserService.cs | 87-91 | `GetAuditReport` concatenates the entire audit log with `+=` inside a loop. | Use `string.Join("\n", _auditLog)`. |
| Helpers/StringHelper.cs | 16 | `IsValidEmail` constructs a `new Regex(...)` on every call. | Promote to a `static readonly Regex` or use `[GeneratedRegex]`. |
| Helpers/StringHelper.cs | 25 | `IsValidUsername` constructs a `new Regex(...)` on every call. | Promote to a `static readonly Regex` or use `[GeneratedRegex]`. |
| Services/UserService.cs | 10, 45, 64 | `_auditLog` is a shared mutable `static List<string>` mutated from concurrent requests without synchronisation, risking corruption and unbounded growth. | Persist audit entries to the database, or use a thread-safe bounded structure. |
| Services/UserService.cs | 11, 25, 59 | `_requestCount` is a shared mutable static `int` incremented non-atomically from multiple threads. | Use `Interlocked.Increment` or a proper metrics counter. |
| Helpers/StringHelper.cs | 65-71 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Delete it and call the BCL method. |
| Helpers/StringHelper.cs | 29-41 | `JoinWithSeparator` and `JoinWithSeparatorFixed` are duplicate implementations where the fixed one sits beside the broken one. | Keep one (or neither) implementation. |
| Helpers/StringHelper.cs | 43-57 | `MaskAccountNumber` and `ObfuscateAccount` are duplicate masking implementations with different, inconsistent output. | Consolidate into a single masking helper. |
| Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection` leaks resource ownership to callers with no documented disposal contract, and both callers get it wrong. | Remove it in favour of self-contained, `using`-scoped methods. |
| Services/UserService.cs | 20-23, 40-43, 54-57 | The `id <= 0` / `id > 1000000` validation block is duplicated verbatim in `GetUserById`, `UpdateUser` and `DeleteUser`. | Extract to a private `ValidateUserId(int id)` helper. |
| Services/UserService.cs | 40-43 | `UpdateUser` repeats the same id-validation block (second occurrence). | Call the shared `ValidateUserId` helper. |
| Services/UserService.cs | 54-57 | `DeleteUser` repeats the same id-validation block (third occurrence). | Call the shared `ValidateUserId` helper. |
| Controllers/TransactionController.cs | 26-27, 40-41 | The claim-extraction and parse block is duplicated in `Transfer` and `Deposit`. | Extract to a `TryGetCurrentUserId(out int)` base-controller helper. |
| Services/AuthService.cs | 42-50 | Reader-to-`User` mapping duplicates `UserService.MapRowToUser` logic in a second place. | Centralise mapping in one shared mapper. |
| Services/TransactionService.cs | 23-61 | `Transfer` mixes validation, two account lookups, fee calculation, two balance updates, ledger insert and email notification — six responsibilities in one method. | Split into `ValidateTransfer`, `LoadAccounts`, `CalculateFee`, `ApplyTransfer` (transactional) and `NotifySender`. |
| Services/AuthService.cs | 28-59 | `Login` mixes password hashing, connection management, SQL construction, row mapping and the backdoor check. | Split into `HashPassword`, `FindActiveUser` (repository) and `MapUser`, and delete the backdoor. |
| Services/EmailService.cs | 34-61 | `SendTransferNotification` mixes body composition, message construction and retry/backoff policy. | Extract `BuildTransferBody` and a reusable `SendWithRetry(MailMessage)` helper (or use Polly). |
| Services/EmailService.cs | 18-32 | The constructor performs configuration parsing, credential construction and client configuration with no validation. | Bind an `IOptions<EmailOptions>` and validate it at startup. |
| Services/UserService.cs | 68-83 | `GetUsersPage` mixes page-size clamping, offset arithmetic, querying and row mapping, and returns no total count. | Extract `NormalisePaging` and return a `PagedResult<User>` with a total. |
| Services/EmailService.cs | 83 | `BuildHtmlTemplate` interpolates untrusted values into HTML without encoding, an HTML/email-injection vector. | HTML-encode `title` and `body` before interpolation. |
| Services/EmailService.cs | 46-60 | The retry loop has no backoff delay, so all three attempts fire within milliseconds. | Add exponential backoff, ideally via Polly. |
| Program.cs | 10-14 | `DatabaseHelper` is a singleton while services are scoped; the class is stateless today but the mixed lifetime is fragile. | Register `DatabaseHelper` as scoped alongside its consumers. |
| Services/*, Controllers/* | all | The entire stack is synchronous (`ExecuteReader`, `Fill`, `Send`), blocking thread-pool threads on I/O. | Convert to `async`/`await` with `ExecuteReaderAsync`, `SendMailAsync` and async actions. |
| Services/TransactionService.cs | 23, 63 | Returning `(bool Success, string Message)` tuples pushes error semantics into string comparison. | Return a typed `Result`/`OperationOutcome` with an error code. |
| Controllers/UserController.cs | 13 | `_logger` is injected but unused in `GetUser`, `GetUsers`, `SearchUsers` and `GetAuditLog`. | Log meaningful events or remove the unused dependency. |
| Services/EmailService.cs | 56, 77 | `Console.WriteLine` is used instead of the injected logging abstraction. | Inject and use `ILogger<EmailService>`. |
| Services/UserService.cs | 79, 101, 111 | Fully-qualified `System.Data.DataRow` is used inline instead of a `using` directive, and the service exposes ADO.NET types internally. | Add `using System.Data;` and introduce a repository abstraction. |
| Controllers/UserController.cs | 81 | `GetAuditLog` returns a newline-joined string as an API response rather than a structured collection. | Return a typed list of audit entries. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally for all environments. | Wrap in `if (app.Environment.IsDevelopment())`. |
| Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry validation. | Set to `true`. |
| Program.cs | 36 | `app.UseHttpsRedirection()` is commented out. | Re-enable it and add `app.UseHsts()` for production. |
| Program.cs | 38 | CORS is configured with `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()`. | Define a named policy with an explicit origin allow-list. |
| Program.cs | 38 | `UseCors` is called after the exception page but the pipeline lacks `UseRouting`/`UseExceptionHandler` ordering for production. | Establish an explicit, environment-aware middleware pipeline. |
| Program.cs | 16-30 | JWT settings are read via magic string indexers rather than the options pattern, with no startup validation. | Use `builder.Services.AddOptions<JwtOptions>().Bind(...).ValidateOnStart()`. |
| appsettings.json | 17-21 | Log levels are set to `Debug` for `Default`, `Microsoft` and `System`, which is excessive and leaks internals in production. | Use `Information`/`Warning` in the base file and `Debug` only in `appsettings.Development.json`. |
| appsettings.json | 3, 6, 14 | Production secrets (DB password, JWT key, SMTP password) live in a committed config file. | Move all three to user secrets/environment variables/Key Vault. |
| appsettings.json | 23 | `AllowedHosts: "*"` accepts any Host header. | Specify the concrete hostnames. |
| Repository root | — | There is no `appsettings.Development.json` or `appsettings.Production.json`, so one file serves every environment. | Add environment-specific overrides and keep secrets out of all of them. |
| SampleBankingApp.csproj | 7 | `TreatWarningsAsErrors=false` lets real defects (e.g. CS0162 unreachable code in `ValidateToken`) ship silently. | Enable `TreatWarningsAsErrors` for CI builds. |
| SampleBankingApp.csproj | 8-9 | `DebugSymbols`/`DebugType=full` are set unconditionally, including Release. | Scope them to a `'$(Configuration)'=='Debug'` `PropertyGroup`. |
| SampleBankingApp.csproj | 15 | `Newtonsoft.Json 12.0.3` is outdated, has known advisories, and is entirely unreferenced by the code. | Remove the reference. |
| SampleBankingApp.csproj | 14 | `System.Data.SqlClient 4.8.6` is the deprecated legacy provider. | Switch to `Microsoft.Data.SqlClient` latest. |
| SampleBankingApp.csproj | 16 | `System.IdentityModel.Tokens.Jwt 7.0.0` is an early 7.x release superseded by many security/bug fixes. | Upgrade to the latest 7.x/8.x patch. |
| SampleBankingApp.csproj | 13 | `Microsoft.AspNetCore.Authentication.JwtBearer 8.0.0` is the initial 8.0 release with subsequent security patches available. | Upgrade to the latest 8.0.x. |
| SampleBankingApp.csproj | 1-17 | There is no `Directory.Packages.props`/`NuGet.config` lock or vulnerability audit setting. | Enable `NuGetAudit` and central package management. |

## 10. Missing Unit Tests

No test project exists anywhere in the solution (no `*.Tests.csproj`, no test files). The following should be covered first.

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/UserService.cs | 68-83 | `GetUsersPage` off-by-one has no test proving page 1 returns the first record. | Add tests for page=1, page=2, page=0, page=-1, pageSize=0 and pageSize=1000 (clamped to 50). |
| Services/TransactionService.cs | 42-44 | The balance-vs-fee check in `Transfer` is untested at the boundary where `balance == amount`. | Test balance exactly equal to `amount`, to `amount+fee`, and one cent below each. |
| Services/TransactionService.cs | 25 | `Transfer`'s amount guard is untested for zero and negative values. | Test `amount = 0`, `-0.01`, and `decimal.MaxValue`. |
| Services/TransactionService.cs | 23 | Self-transfer behaviour (`fromUserId == toUserId`) is untested. | Add a test asserting a self-transfer is rejected and balances are unchanged. |
| Services/TransactionService.cs | 39 | Fee rounding via `Math.Round(amount * 0.015m, 2)` has no test for half-way values. | Test amounts producing `.005` remainders to pin down banker's rounding. |
| Services/TransactionService.cs | 63-75 | `Deposit` boundary conditions (`0`, `1000000`, `1000000.01`) and the interest bonus are untested. | Add boundary tests and a test asserting the exact credited amount. |
| Services/TransactionService.cs | 47-50 | Atomicity of the two balance updates plus the ledger insert is untested. | Add an integration test that forces a failure between writes and asserts a rollback. |
| Services/TransactionService.cs | 52-55 | Failure of `SendTransferNotification` after a committed transfer is untested. | Test that an SMTP failure does not roll back or double-apply the transfer. |
| Services/TransactionService.cs | 77-85 | `IsWithinDailyLimit` has no test at count = 9, 10 and 11. | Add boundary tests once the method is wired into `Transfer`. |
| Services/AuthService.cs | 28-59 | `Login` success, wrong-password, inactive-user and unknown-user paths are untested. | Add one test per path, including a test asserting the admin backdoor no longer exists. |
| Services/AuthService.cs | 32 | SQL-injection resistance of `Login` is untested. | Add a test passing `' OR '1'='1` as username and asserting authentication fails. |
| Services/AuthService.cs | 68-89 | `GenerateJwtToken` claim contents and expiry are untested. | Assert `NameIdentifier`, `Name`, `Role`, issuer, audience and expiry are correct. |
| Services/UserService.cs | 18-36 | `GetUserById` guard clauses (`id = 0`, `-1`, `1000001`) and the not-found path are untested. | Add tests for each guard and for a null return on missing rows. |
| Services/UserService.cs | 95-109 | `SearchUsers` swallow-and-return-empty behaviour is untested. | Test that a database error surfaces rather than yielding an empty list. |
| Services/UserService.cs | 111-123 | `MapRowToUser` behaviour with `DBNull` columns is untested. | Add tests covering null `Email`, `Role` and `CreatedAt`. |
| Controllers/UserController.cs | 38-69 | Authorisation on `UpdateUser`/`DeleteUser` is untested — nothing proves a non-owner is rejected. | Add tests asserting 403 when the caller is neither the owner nor an admin. |
| Controllers/TransactionController.cs | 26-27, 40-41 | Missing/malformed `NameIdentifier` claim handling is untested. | Add tests asserting 401 rather than an unhandled parse exception. |
| Helpers/StringHelper.cs | 11-27 | `IsValidEmail` and `IsValidUsername` have no tests for null, empty, boundary lengths or invalid characters. | Add table-driven tests covering 2/3/20/21-character usernames and 254/255-character emails. |
| Helpers/StringHelper.cs | 43-57 | `MaskAccountNumber`/`ObfuscateAccount` are untested for strings shorter than four characters. | Add tests for lengths 0, 3, 4 and 5. |
| Data/DatabaseHelper.cs | 26-57 | Connection disposal behaviour on the exception path in `ExecuteQuery`/`ExecuteNonQuery` is untested. | Add tests asserting the pool does not leak when a command throws. |

---

### Summary of the most urgent items
The three changes to make before anything else are: remove the `AdminBypassPassword` backdoor and the interpolated login SQL in `AuthService.Login`; fix `Transfer` so the balance check covers `amount + fee` and both updates run inside one transaction; and correct `GetUsersPage`'s `page * pageSize` offset. Close behind are the committed production secrets in `appsettings.json`, the unconditional developer exception page, `ValidateLifetime = false`, the wide-open CORS policy, and the missing ownership checks on `PUT /api/user/{id}` and `DELETE /api/user/{id}`.