# Code Review — SampleBankingApp (main @ 74c6567)

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/AuthService.cs | 32 | `Login` builds the authentication SQL by interpolating `username` and `hashedPassword`, allowing full authentication bypass with `' OR '1'='1`. | Use a parameterised `SqlCommand` with `@Username`/`@Password` parameters. |
| Services/AuthService.cs | 17 | `AdminBypassPassword` is a hardcoded credential constant compiled into the binary. | Delete the constant entirely. |
| Services/AuthService.cs | 53-56 | `Login` contains a hardcoded backdoor granting `SuperAdmin` role to `admin`/`SuperAdmin2024` with `Id = 0`. | Remove the backdoor branch and rely solely on the database lookup. |
| Services/AuthService.cs | 61-66 | `HashPasswordMd5` uses unsalted MD5, which is broken and trivially reversible via rainbow tables. | Replace with PBKDF2 (`Rfc2898DeriveBytes`), bcrypt, or Argon2 with a per-user salt. |
| Services/AuthService.cs | 91-96 | `HashPasswordSha1` uses unsalted SHA-1, another broken hash for passwords. | Delete the method; it is both insecure and unused. |
| Services/AuthService.cs | 84 | `GenerateJwtToken` issues tokens valid for 30 days with no refresh mechanism, widening the stolen-token window. | Reduce to 15-60 minutes and add a refresh-token flow. |
| Services/AuthService.cs | 98-108 | `ValidateToken` returns `true` for any non-empty string without verifying signature, issuer or expiry. | Delete the method or implement real validation via `JwtSecurityTokenHandler.ValidateToken`. |
| Services/AuthService.cs | 34 | `Login` opens its own `SqlConnection` from config, bypassing `DatabaseHelper` and duplicating credential handling. | Route the query through `DatabaseHelper.ExecuteQuerySafe`. |
| Services/UserService.cs | 47 | `UpdateUser` interpolates `email`, `username` and `id` directly into an `UPDATE` statement (SQL injection). | Use `@Email`, `@Username`, `@Id` parameters via a parameterised non-query helper. |
| Services/UserService.cs | 61 | `DeleteUser` interpolates `id` into a `DELETE FROM Users` statement. | Parameterise the `Id` value. |
| Services/UserService.cs | 99 | `SearchUsers` interpolates `query` into a `LIKE '%...%'` clause passed to the unsafe `ExecuteQuery` helper. | Use a parameterised `LIKE @Query` with escaped `%`, `_` and `[` wildcards. |
| Services/TransactionService.cs | 47 | `Transfer` interpolates `newFromBalance` and `fromUserId` into an `UPDATE Users` statement. | Parameterise, and prefer a relative `Balance = Balance - @Amount` update. |
| Services/TransactionService.cs | 48 | `Transfer` interpolates `newToBalance` and `toUserId` into an `UPDATE Users` statement. | Parameterise the values. |
| Services/TransactionService.cs | 71 | `Deposit` interpolates the amount and `userId` into an `UPDATE Users` statement. | Parameterise the values. |
| Services/TransactionService.cs | 89-90 | `RecordTransaction` interpolates the user-controlled `description` into an `INSERT`, permitting SQL injection from the transfer endpoint body. | Parameterise all seven column values. |
| Data/DatabaseHelper.cs | 26-34 | `ExecuteQuery` accepts a raw `tableName` and `whereClause` and concatenates them, making injection unavoidable for every caller. | Remove the method and force callers onto `ExecuteQuerySafe`. |
| Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` accepts a fully-formed raw SQL string, so every write path in the app is an injection vector. | Add a parameterised overload `ExecuteNonQuery(string sql, Dictionary<string, object> parameters)` and delete the raw variant. |
| Data/DatabaseHelper.cs | 16 | The constructor falls back to a hardcoded `sa` connection string with password `Admin1234!`. | Throw `InvalidOperationException` when `DefaultConnection` is missing instead of defaulting. |
| appsettings.json | 3 | A production connection string with the `sa` account and password `Admin1234!` is committed to source control. | Move to user secrets / Key Vault / environment variables and rotate the password. |
| appsettings.json | 3 | `TrustServerCertificate=True` disables TLS certificate validation on the SQL connection. | Remove it and install a valid certificate on the database server. |
| appsettings.json | 6 | The JWT signing key is the committed literal `mysecretkey`, which is far below the 256-bit minimum for HMAC-SHA256. | Generate a 32+ byte random key and store it outside source control. |
| appsettings.json | 14 | The SMTP account password `EmailPass99` is committed to source control. | Move to a secret store and rotate the credential. |
| Program.cs | 24 | `ValidateLifetime = false` means expired tokens are accepted forever. | Set `ValidateLifetime = true` and configure a small `ClockSkew`. |
| Program.cs | 34 | `UseDeveloperExceptionPage()` is called unconditionally, leaking stack traces and SQL text in production. | Wrap in `if (app.Environment.IsDevelopment())` and add `UseExceptionHandler` for production. |
| Program.cs | 36 | `app.UseHttpsRedirection()` is commented out, so bearer tokens and passwords can travel in cleartext. | Uncomment it and add `app.UseHsts()`. |
| Program.cs | 38 | CORS is configured with `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` on a banking API. | Restrict to an explicit allow-list of origins and methods. |
| Controllers/UserController.cs | 38-54 | `UpdateUser` has no ownership or role check, so any authenticated user can change any other user's email and username (IDOR). | Compare `id` against the `NameIdentifier` claim or require an admin role. |
| Controllers/UserController.cs | 56-69 | `DeleteUser` has no ownership or role check, so any authenticated user can delete any account. | Add `[Authorize(Roles = "Admin")]` plus an ownership check. |
| Controllers/UserController.cs | 21-29 | `GetUser` lets any authenticated user read any other user's email, role and balance. | Restrict to self or admin. |
| Controllers/UserController.cs | 78-82 | `GetAuditLog` exposes the internal audit trail to every authenticated user with no role restriction. | Add `[Authorize(Roles = "Admin")]`. |
| Controllers/UserController.cs | 31-36 | `GetUsers` enumerates every user account (including balances) for any authenticated caller. | Restrict to admins and project to a DTO that omits `Balance`. |
| Controllers/UserController.cs | 52 | `UpdateUser` returns raw `ex.Message` to the client, leaking SQL and schema details. | Log the exception and return a generic message. |
| Controllers/AuthController.cs | 19-31 | `Login` has no rate limiting, CAPTCHA or account lockout, allowing unlimited credential stuffing. | Add ASP.NET Core rate limiting and a failed-attempt lockout counter. |
| Controllers/AuthController.cs | 26 | The response message "Username not found or incorrect password" hints at user enumeration semantics. | Return a single generic "Invalid credentials" message. |
| Services/EmailService.cs | 29 | `EnableSsl = false` sends the SMTP username and password over an unencrypted connection. | Set `EnableSsl = true` and use port 587 with STARTTLS. |
| Services/EmailService.cs | 83 | `BuildHtmlTemplate` interpolates untrusted `username` into HTML without encoding, enabling HTML/script injection in email clients. | HTML-encode all interpolated values with `WebUtility.HtmlEncode`. |
| SampleBankingApp.csproj | 8-9 | `DebugSymbols=true` and `DebugType=full` are set unconditionally, shipping full PDBs in Release builds. | Move these into a `Debug`-only `PropertyGroup` and use `portable` for Release. |
| SampleBankingApp.csproj | 15 | `Newtonsoft.Json` 12.0.3 is affected by the CVE-2024-21907 denial-of-service advisory. | Upgrade to 13.0.3 or remove the reference, which is unused. |
| SampleBankingApp.csproj | 14 | `System.Data.SqlClient` 4.8.6 is the deprecated legacy driver that no longer receives feature or security fixes. | Migrate to `Microsoft.Data.SqlClient` 5.x. |
| Program.cs | 40-41 | No global authorisation fallback policy is set, so any newly added controller without `[Authorize]` is anonymous by default. | Configure `AuthorizationOptions.FallbackPolicy` to require an authenticated user. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/UserService.cs | 72 | `GetUsersPage` computes `skip = page * pageSize`, so the default `page = 1` silently skips the first page of users. | Use `(page - 1) * pageSize`. |
| Services/UserService.cs | 68-72 | `GetUsersPage` never validates that `page >= 1`, so a negative page produces a negative `OFFSET` and a SQL error. | Clamp `page` to a minimum of 1. |
| Services/UserService.cs | 70 | `GetUsersPage` clamps `pageSize` at an upper bound of 50 but has no lower bound, so `pageSize = 0` or negative reaches the query. | Clamp `pageSize` into the range 1-50. |
| Services/TransactionService.cs | 25 | `Transfer` rejects only `amount < 0`, so a zero-amount transfer is accepted and recorded. | Change the guard to `amount <= 0`. |
| Services/TransactionService.cs | 42 | `Transfer` checks `fromBalance >= amount` but then debits `totalDebit = amount + fee`, allowing a negative balance. | Check `fromBalance >= totalDebit`. |
| Services/TransactionService.cs | 23-61 | `Transfer` has no self-transfer guard, so `fromUserId == toUserId` runs two sequential updates and the second overwrites the first, effectively crediting the sender the fee-free amount. | Return an error when `fromUserId == toUserId`. |
| Services/TransactionService.cs | 36-37 | `Transfer` reads `Rows[0]` for both users without verifying the recipient exists, so an unknown `toUserId` throws instead of returning a friendly error. | Check `Rows.Count > 0` for both tables and return "Recipient not found". |
| Services/TransactionService.cs | 42-58 | `Transfer` never checks `IsActive` on either account, permitting transfers to and from disabled accounts. | Validate `IsActive` for both parties before moving funds. |
| Services/TransactionService.cs | 50 | `Transfer` records only `amount` in the ledger and never records the `fee`, so the books do not reconcile with the balance change. | Record the fee as a separate transaction row or store it in a `Fee` column. |
| Services/TransactionService.cs | 77-85 | `IsWithinDailyLimit` is never invoked, so `MaxTransactionsPerDay` is not enforced anywhere. | Call it at the top of `Transfer` and reject when the limit is exceeded. |
| Services/TransactionService.cs | 68 | `Deposit` adds a 5% "interest bonus" (`amount * 0.05m`) to every deposit, which mints money on each call and is almost certainly meant to be 1% or nothing. | Remove the bonus or move the correct rate into configuration. |
| Services/TransactionService.cs | 68 | The `* 1` multiplier in `amount * 0.05m * 1` is a no-op that suggests an incomplete term (e.g. a period count) was dropped. | Remove the redundant factor and clarify the intended formula. |
| Services/TransactionService.cs | 71-73 | `Deposit` credits `amount + interestBonus` but records only `amount` in the transaction table, so the ledger disagrees with the balance. | Record the bonus as its own transaction row. |
| Services/TransactionService.cs | 73 | `Deposit` records `fromId = 0`, which collides with the backdoor admin's `Id = 0` and with any real user row of id 0. | Use a sentinel such as `NULL` or a dedicated system account id. |
| Services/AuthService.cs | 55 | The backdoor user is constructed with `Id = 0`, and `UserService.GetUserById(0)` throws `ArgumentException`, so this identity breaks every downstream lookup. | Remove the backdoor. |
| Services/AuthService.cs | 40-51 | `Login` never updates `LastLoginAt` even though the model exposes it, leaving the field permanently at default. | Issue an update on successful authentication or drop the field. |
| Services/AuthService.cs | 42-50 | `Login` does not populate `CreatedAt` or `LastLoginAt` on the returned `User`, so callers see `DateTime.MinValue`. | Map all columns or return a dedicated DTO. |
| Services/AuthService.cs | 103 | `ValidateToken` unconditionally returns `true` before the real expiry check, so every non-empty string validates. | Delete the early return and use full token validation. |
| Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` appends the separator after the final element, producing a trailing separator. | Delete it in favour of `JoinWithSeparatorFixed`. |
| Helpers/StringHelper.cs | 56 | `ObfuscateAccount` indexes `account[^4..]` without a length check, throwing `ArgumentOutOfRangeException` for accounts shorter than four characters. | Guard the length as `MaskAccountNumber` does, or delete the duplicate. |
| Helpers/StringHelper.cs | 62 | `ToTitleCase` uses `CurrentCulture`, so Turkish locales mangle dotted/dotless I in usernames. | Use `CultureInfo.InvariantCulture`. |
| Services/UserService.cs | 22-23 | `GetUserById` rejects ids above the arbitrary constant 1,000,000, which will silently break once the table grows past a million rows. | Remove the ceiling or derive it from a configured maximum. |
| Services/UserService.cs | 38-50 | `UpdateUser` performs no validation of `email` or `username` even though `StringHelper.IsValidEmail`/`IsValidUsername` exist. | Validate both inputs and throw `ArgumentException` on failure. |
| Services/UserService.cs | 49 / 65 | `UpdateUser` and `DeleteUser` always return `true` regardless of whether any row was affected, so a missing id looks like success. | Return `ExecuteNonQuery`'s affected-row count compared with 1. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/UserService.cs | 105-108 | `SearchUsers` catches broad `Exception` and returns an empty list, so callers cannot distinguish "no matches" from "database down". | Let the exception propagate or wrap it in a domain exception after logging. |
| Services/EmailService.cs | 75-78 | `SendWelcomeEmail` catches broad `Exception` and merely writes to the console, silently swallowing all failures. | Catch `SmtpException` specifically and log via `ILogger<EmailService>`. |
| Services/EmailService.cs | 56 | `SendTransferNotification` reports failures with `Console.WriteLine` rather than the logging pipeline. | Inject and use `ILogger<EmailService>`. |
| Services/EmailService.cs | 77 | `SendWelcomeEmail` reports failures with `Console.WriteLine` rather than the logging pipeline. | Inject and use `ILogger<EmailService>`. |
| Services/EmailService.cs | 45-60 | The retry loop in `SendTransferNotification` retries immediately with no backoff, hammering the SMTP server three times in microseconds. | Add exponential backoff (e.g. Polly) between attempts. |
| Services/EmailService.cs | 53 | `SendTransferNotification` catches only `SmtpException`, so `InvalidOperationException` or `IOException` from the shared `SmtpClient` escape unretried. | Broaden the retry filter to the transient exception types actually thrown. |
| Services/EmailService.cs | 86-92 | `SendWelcomeEmailHtml` has no error handling at all, so a transient SMTP failure becomes an unhandled exception. | Wrap in the same retry/log pattern used elsewhere. |
| Services/TransactionService.cs | 47-50 | `Transfer` performs two `UPDATE`s plus an `INSERT` with no database transaction, so a failure between them destroys or duplicates money. | Wrap the whole sequence in a single `SqlTransaction` with the reads under an appropriate isolation level. |
| Services/TransactionService.cs | 70-73 | `Deposit` performs an `UPDATE` and an `INSERT` with no transaction, so the balance can change without a ledger entry. | Wrap both writes in a single transaction. |
| Services/TransactionService.cs | 52-55 | `Transfer` sends the notification email after the balances are already committed, so an SMTP failure throws out of a successful transfer. | Move notification outside the critical path (outbox/queue) and never let it fail the operation. |
| Services/TransactionService.cs | 28-37 | `Transfer` reads balances outside any transaction or lock, creating a lost-update race under concurrent transfers. | Read and write inside one serialisable transaction or use `UPDATE ... WHERE Balance >= @Total`. |
| Controllers/UserController.cs | 50-53 | `UpdateUser` catches broad `Exception` and returns `ex.Message` in the 500 body. | Log the exception and return a fixed message. |
| Controllers/UserController.cs | 64-68 | `DeleteUser` catches broad `Exception`, so an `ArgumentException` for a bad id is reported as a 500 instead of a 400. | Add a specific `catch (ArgumentException)` returning `BadRequest`. |
| Controllers/TransactionController.cs | 23-35 | `Transfer` has no try/catch, so any SQL or SMTP exception surfaces through the developer exception page with a stack trace. | Add exception handling or a global exception-handling middleware. |
| Controllers/TransactionController.cs | 37-46 | `Deposit` has no try/catch for the same reason. | Same as above. |
| Controllers/TransactionController.cs | 56-59 | `Refund` catches `NotImplementedException` and returns a 500 rather than a `501 Not Implemented`. | Return `StatusCode(StatusCodes.Status501NotImplemented)` or remove the endpoint until implemented. |
| Controllers/AuthController.cs | 19-31 | `Login` has no try/catch and no rate limiting or lockout on repeated failures. | Add rate limiting middleware and a failed-attempt counter with temporary lockout. |
| Services/AuthService.cs | 34-51 | `Login` has no error handling, so a SQL failure leaves the connection and reader unclosed and propagates to the client. | Wrap in `using` declarations and a try/catch that logs. |
| Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` calls `connection.Close()` only on the success path, so an exception during execution leaks the connection. | Use `using var connection = ...` so disposal happens on all paths. |
| Program.cs | 32-42 | No `UseExceptionHandler` or `ProblemDetails` middleware is registered, so unhandled exceptions have no consistent, safe response shape. | Add `app.UseExceptionHandler("/error")` for non-development environments. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection` returns an open `SqlConnection` and transfers disposal responsibility to callers with no documented contract. | Make it private and expose only self-contained execute methods. |
| Data/DatabaseHelper.cs | 28-33 | `ExecuteQuery` never disposes the `SqlConnection`, `SqlCommand` or `SqlDataAdapter`, leaking a pooled connection on every call. | Wrap all three in `using` declarations. |
| Data/DatabaseHelper.cs | 52-55 | `ExecuteNonQuery` never disposes the `SqlCommand` and only closes the connection on the success path. | Use `using` declarations for both the connection and the command. |
| Data/DatabaseHelper.cs | 44 | `ExecuteQuerySafe` creates a `SqlDataAdapter` that is never disposed. | Wrap it in `using var adapter = new SqlDataAdapter(command);`. |
| Data/DatabaseHelper.cs | 74 | `ExecuteQueryWithParams` creates a `SqlDataAdapter` that is never disposed. | Delete the obsolete method, or dispose the adapter. |
| Services/AuthService.cs | 34-38 | `Login` creates a `SqlConnection`, `SqlCommand` and `SqlDataReader` and never closes or disposes any of them, leaking on every login attempt. | Use `using` declarations, or route through `DatabaseHelper.ExecuteQuerySafe`. |
| Services/AuthService.cs | 42-51 | `Login` returns from inside the `if (reader.Read())` block, guaranteeing the reader and connection are abandoned on the success path. | Same as above — `using` declarations make the early return safe. |
| Services/EmailService.cs | 16, 22 | `_smtpClient` is a mutable `SmtpClient` instance field on a scoped service; `SmtpClient` is not thread-safe and is never disposed, so its socket is never released. | Create and dispose the client per send, or switch to MailKit with a pooled `IEmailSender` abstraction. |
| Services/EmailService.cs | 6-93 | `EmailService` holds an `IDisposable` field but does not implement `IDisposable`, so the DI container can never release it. | Implement `IDisposable`/`IAsyncDisposable` and dispose `_smtpClient`. |
| Services/EmailService.cs | 39-43 | The `MailMessage` created in `SendTransferNotification` is never disposed, leaking attachments and stream handles. | Wrap in `using var message = new MailMessage(...)`. |
| Services/EmailService.cs | 69 | The `MailMessage` created in `SendWelcomeEmail` is never disposed. | Wrap in a `using` declaration. |
| Services/EmailService.cs | 89 | The `MailMessage` created in `SendWelcomeEmailHtml` is never disposed. | Wrap in a `using` declaration. |
| Services/UserService.cs | 99 | `SearchUsers` calls `ExecuteQuery`, inheriting its leaked connection on every search request. | Switch to `ExecuteQuerySafe` after parameterising the `LIKE`. |
| Services/TransactionService.cs | 47-48, 71, 91 | Every call to `_db.ExecuteNonQuery` from `Transfer`, `Deposit` and `RecordTransaction` leaks the `SqlCommand` and leaks the connection whenever the statement throws. | Fix `ExecuteNonQuery` disposal as described above. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| Program.cs | 28 | `Encoding.UTF8.GetBytes(jwtSecret!)` throws `ArgumentNullException` at startup if `Jwt:SecretKey` is absent, and the `!` hides it from the compiler. | Validate the value and throw a descriptive `InvalidOperationException` if it is null or too short. |
| Services/AuthService.cs | 70 | `GenerateJwtToken` passes `_config["Jwt:SecretKey"]!` straight to `Encoding.UTF8.GetBytes`, which cannot accept null. | Read the key once into a validated field in the constructor. |
| Services/AuthService.cs | 81-82 | `GenerateJwtToken` passes potentially null `Jwt:Issuer` and `Jwt:Audience` while `Program.cs` validates them, producing tokens that can never validate. | Validate both settings at startup. |
| Controllers/TransactionController.cs | 26-27 | `Transfer` does `int.Parse(userIdClaim!)` where `FindFirst(...)?.Value` can be null, throwing `ArgumentNullException`. | Use `int.TryParse` and return `Unauthorized()` when the claim is missing or malformed. |
| Controllers/TransactionController.cs | 40-41 | `Deposit` has the same unguarded `int.Parse(userIdClaim!)`. | Same fix as above. |
| Controllers/TransactionController.cs | 24, 29 | `Transfer` dereferences `request.ToUserId` with no null check, so a JSON body of `null` causes a `NullReferenceException`. | Add `if (request is null) return BadRequest();` or use `[FromBody] required` model validation. |
| Controllers/TransactionController.cs | 38, 43 | `Deposit` dereferences `request.Amount` with no null check on the model-bound object. | Same fix as above. |
| Controllers/UserController.cs | 39, 43 | `UpdateUser` dereferences `request.Email` and `request.Username` without a null check. | Add a null guard returning `BadRequest`. |
| Controllers/UserController.cs | 72-74 | `SearchUsers` declares a non-nullable `string query` that can arrive null from the query string and is then interpolated into SQL. | Mark it `string?` and reject null/whitespace before querying. |
| Controllers/AuthController.cs | 20, 22 | `Login` dereferences `request.Username` and `request.Password` without a null check. | Add a null guard returning `BadRequest`. |
| Services/TransactionService.cs | 36 | `Transfer` reads `fromUserTable.Rows[0]["Balance"]` without checking `Rows.Count > 0`, throwing `IndexOutOfRangeException` for an unknown sender. | Check `Rows.Count` before indexing. |
| Services/TransactionService.cs | 37 | `Transfer` reads `toUserTable.Rows[0]["Balance"]` without checking `Rows.Count > 0`. | Check `Rows.Count` before indexing. |
| Services/TransactionService.cs | 53-55 | `Transfer` casts `Rows[0]["Email"]` and `Rows[0]["Username"]` to `string`, throwing `InvalidCastException` when the column is `DBNull`. | Use `row.Field<string>(...)` with a null check. |
| Services/TransactionService.cs | 83 | `IsWithinDailyLimit` indexes `table.Rows[0]["TxCount"]` without a `Rows.Count` guard. | Add the guard or use `ExecuteScalar`. |
| Services/UserService.cs | 111-123 | `MapRowToUser` hard-casts `Username`, `Email`, `Role`, `Balance`, `IsActive` and `CreatedAt`, throwing `InvalidCastException` on any nullable column. | Use `DataRow.Field<T>()` with null-coalescing defaults. |
| Services/AuthService.cs | 44-49 | `Login` hard-casts `reader["Email"]`, `reader["Role"]` etc., throwing `InvalidCastException` when a column is `DBNull`. | Guard with `reader.IsDBNull(ordinal)` or use `Field<T>` semantics. |
| Services/EmailService.cs | 22 | `new SmtpClient(_config["Email:SmtpHost"])` throws `ArgumentNullException` when the setting is missing. | Validate the host with a fallback or a startup check. |
| Services/EmailService.cs | 24 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` throws `FormatException` for a non-numeric configured port. | Use `int.TryParse` with a default. |
| Services/EmailService.cs | 65 | `SendWelcomeEmail` calls `username.ToUpper()` before any null check on the parameter. | Add `ArgumentNullException.ThrowIfNull(username)` at the top. |
| Services/EmailService.cs | 88 | `SendWelcomeEmailHtml` interpolates `username` with no null check. | Add the same guard. |
| Services/EmailService.cs | 34-39 | `SendTransferNotification` passes `toEmail` to `MailMessage`, which throws `ArgumentNullException` for null. | Validate `toEmail` before constructing the message. |
| Helpers/StringHelper.cs | 13 | `IsValidEmail` calls `email.Length` before any null check. | Return `false` for null input. |
| Helpers/StringHelper.cs | 22 | `IsValidUsername` calls `username.Length` before any null check. | Return `false` for null input. |
| Helpers/StringHelper.cs | 45 | `MaskAccountNumber` calls `accountNumber.Length` before any null check. | Add a null guard. |
| Helpers/StringHelper.cs | 56 | `ObfuscateAccount` indexes `account[^4..]` on a possibly null or short string. | Add null and length guards. |
| Helpers/StringHelper.cs | 32 | `JoinWithSeparator` enumerates `items` with no null check. | Add `ArgumentNullException.ThrowIfNull(items)`. |
| Data/DatabaseHelper.cs | 41 | `ExecuteQuerySafe` enumerates `parameters` without a null check. | Accept an optional dictionary and default to empty. |

## 6. Dead Code

Full method inventory and caller search results:

| File | Line | Issue | Fix |
|---|---|---|---|
| Data/DatabaseHelper.cs | 59-65 | `TableExists` is defined but never called from any file in the repository. | Delete it or cover it with tests if it is a planned API. |
| Data/DatabaseHelper.cs | 67-78 | `ExecuteQueryWithParams` is marked `[Obsolete]` and has no callers anywhere. | Delete it. |
| Helpers/StringHelper.cs | 11-18 | `IsValidEmail` has no callers; `UserService.UpdateUser` should use it but does not. | Wire it into `UpdateUser` validation or delete it. |
| Helpers/StringHelper.cs | 20-27 | `IsValidUsername` has no callers. | Wire it into `UpdateUser` validation or delete it. |
| Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` has no callers and is the broken sibling of `JoinWithSeparatorFixed`. | Delete it. |
| Helpers/StringHelper.cs | 38-41 | `JoinWithSeparatorFixed` has no callers; it is the "fixed" duplicate that nothing uses. | Delete it and call `string.Join` directly at the use site. |
| Helpers/StringHelper.cs | 43-52 | `MaskAccountNumber` has no callers. | Delete it or use it when returning account data. |
| Helpers/StringHelper.cs | 54-57 | `ObfuscateAccount` has no callers and duplicates `MaskAccountNumber`. | Delete this duplicate implementation. |
| Helpers/StringHelper.cs | 59-63 | `ToTitleCase` has no callers. | Delete it. |
| Helpers/StringHelper.cs | 65-71 | `IsBlank` has no callers and reimplements `string.IsNullOrWhiteSpace`. | Delete it. |
| Helpers/StringHelper.cs | 9-72 | The entire `StringHelper` class is unreachable — no file references the `SampleBankingApp.Helpers` namespace. | Remove the file or start using it. |
| Services/AuthService.cs | 91-96 | `HashPasswordSha1` is private and never invoked, producing an unused-member warning. | Delete it. |
| Services/AuthService.cs | 98-108 | `ValidateToken` is public but never called by any controller, service or middleware. | Delete it. |
| Services/AuthService.cs | 105-107 | The three statements after the unconditional `return true;` in `ValidateToken` are unreachable. | Remove the early return or delete the whole method. |
| Services/EmailService.cs | 63-79 | `SendWelcomeEmail` is never called from any registration or user-creation path. | Delete it or invoke it when a user is created. |
| Services/EmailService.cs | 86-92 | `SendWelcomeEmailHtml` is never called. | Delete it or consolidate with `SendWelcomeEmail`. |
| Services/EmailService.cs | 81-84 | `BuildHtmlTemplate` is only called by the dead `SendWelcomeEmailHtml`, so it is transitively dead. | Delete it together with its only caller. |
| Services/EmailService.cs | 11 | `WelcomeSubject` is referenced only by the two dead welcome-email methods. | Remove with them. |
| Services/TransactionService.cs | 77-85 | `IsWithinDailyLimit` is defined but never called, so the daily transaction cap is unenforced. | Call it from `Transfer` and `Deposit`. |
| Services/TransactionService.cs | 12 | `MaxTransactionsPerDay` is read only by the unused `IsWithinDailyLimit`, so it is effectively dead. | Becomes live once `IsWithinDailyLimit` is wired in. |
| Services/TransactionService.cs | 94-97 | `FormatCurrency` is defined but never called; `SendTransferNotification` formats currency inline instead. | Delete it or use it consistently. |
| Services/TransactionService.cs | 99-103 | `RefundTransaction` is a `throw new NotImplementedException()` stub exposed through a live HTTP route. | Implement it or remove the endpoint and the method. |
| Services/UserService.cs | 11, 25, 59 | `_requestCount` is incremented in `GetUserById` and `DeleteUser` but never read anywhere. | Remove the field or expose it through a real metrics counter. |
| Controllers/TransactionController.cs | 15, 17-21 | `_logger` is injected and assigned but never used in any action of `TransactionController`. | Use it for failure logging or remove the dependency. |
| Data/DatabaseHelper.cs | 26 vs 36 | `ExecuteQuery` (unsafe) coexists with `ExecuteQuerySafe`, and `UserService.SearchUsers` still calls the unsafe one. | Delete `ExecuteQuery` and migrate `SearchUsers`. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| Services/UserService.cs | 23 | `GetUserById` compares against the bare literal `1000000` for the id ceiling. | Extract a `MaxUserId` constant or drop the check. |
| Services/UserService.cs | 43 | `UpdateUser` repeats the same `1000000` literal. | Reuse the shared constant via a `ValidateUserId` helper. |
| Services/UserService.cs | 57 | `DeleteUser` repeats the same `1000000` literal a third time. | Reuse the shared constant. |
| Services/UserService.cs | 70 | `GetUsersPage` hardcodes the maximum page size `50`. | Extract `MaxPageSize` and move it to configuration. |
| Controllers/UserController.cs | 32 | `GetUsers` hardcodes default `page = 1` and `pageSize = 20`, which disagrees with the service's 50 cap. | Bind both defaults from a `PagingOptions` config section. |
| Services/TransactionService.cs | 65 | `Deposit` hardcodes the deposit cap `1000000`. | Extract `MaxDepositAmount` and move it to configuration. |
| Services/TransactionService.cs | 68 | `Deposit` hardcodes the interest rate `0.05m` and a stray `* 1`. | Extract a named, configurable `InterestBonusRate`. |
| Services/TransactionService.cs | 39 | `Math.Round(amount * TransactionFeeRate, 2)` hardcodes the rounding precision `2`. | Extract a `CurrencyDecimalPlaces` constant and specify `MidpointRounding`. |
| Services/TransactionService.cs | 50 | The transaction type literal `"Transfer"` is inline. | Introduce a `TransactionTypes` static class or enum. |
| Services/TransactionService.cs | 73 | The transaction type literal `"Deposit"` is inline. | Same as above. |
| Services/TransactionService.cs | 90 | The status literal `'Completed'` is embedded in the SQL of `RecordTransaction`. | Introduce a `TransactionStatus` enum and parameterise it. |
| Services/TransactionService.cs | 11 | `TransactionFeeRate = 0.015m` is a compile-time constant for a business rate that changes. | Move to `appsettings.json` bound via `IOptions`. |
| Services/AuthService.cs | 84 | `GenerateJwtToken` hardcodes `AddDays(30)` for token lifetime. | Read `Jwt:ExpiryMinutes` from configuration. |
| Services/AuthService.cs | 53 | `Login` hardcodes the username literal `"admin"`. | Remove with the backdoor. |
| Services/AuthService.cs | 55 | `Login` hardcodes the role literal `"SuperAdmin"`. | Define role names in a shared `Roles` static class. |
| Services/AuthService.cs | 70 / Program.cs 16 | The config key `"Jwt:SecretKey"` is repeated in two files. | Bind a strongly-typed `JwtOptions` class once. |
| Services/AuthService.cs | 81-82 / Program.cs 26-27 | The `"Jwt:Issuer"` and `"Jwt:Audience"` keys are duplicated across two files. | Same `JwtOptions` fix. |
| Services/AuthService.cs | 34 / DatabaseHelper.cs 15 | The connection-string name `"DefaultConnection"` is repeated in two files. | Centralise in a constant or remove the duplicate access in `AuthService`. |
| Services/EmailService.cs | 40 | `SendTransferNotification` hardcodes the sender address `notifications@company.com`. | Read `Email:FromAddress` from configuration. |
| Services/EmailService.cs | 69 | `SendWelcomeEmail` repeats the same hardcoded sender address. | Same as above. |
| Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` repeats the sender address a third time. | Same as above. |
| Services/EmailService.cs | 67 | `SendWelcomeEmail` hardcodes the support address `support@company.com` in the body. | Move to configuration. |
| Services/EmailService.cs | 24 | The default SMTP port `"25"` is a string literal fallback. | Move the default into typed options. |
| Services/EmailService.cs | 14 | `SmtpTimeoutMs = 5000` is a constant that belongs in configuration. | Bind from `Email:TimeoutMs`. |
| Services/EmailService.cs | 13 | `MaxRetries = 3` is a constant that belongs in configuration. | Bind from `Email:MaxRetries`. |
| Services/EmailService.cs | 36 | The body template and `${amount:F2}` format are inline in the method. | Move templates to resource files or configuration. |
| Data/DatabaseHelper.cs | 16 | The fallback connection string is a hardcoded literal in source. | Remove the fallback entirely. |
| Data/DatabaseHelper.cs | 63 | `TableExists` hardcodes the `"BASE TABLE"` and `"Tables"` schema literals. | Extract named constants if the method is retained. |
| Helpers/StringHelper.cs | 13 | `IsValidEmail` hardcodes the maximum length `254`. | Extract `MaxEmailLength`. |
| Helpers/StringHelper.cs | 22 | `IsValidUsername` hardcodes `3` and `20` as length bounds. | Extract `MinUsernameLength`/`MaxUsernameLength`. |
| Helpers/StringHelper.cs | 45, 49, 50 | `MaskAccountNumber` repeats the literal `4` three times. | Extract `VisibleAccountDigits`. |
| Helpers/StringHelper.cs | 56 | `ObfuscateAccount` repeats the same magic `4` and a literal `"****"` mask. | Derive both from the shared constant. |
| Services/UserService.cs, TransactionService.cs, AuthService.cs | multiple | The table names `Users` and `Transactions` are repeated as literals across at least eight SQL strings. | Centralise SQL text in a repository or constants class. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| Helpers/StringHelper.cs | 31-34 | `JoinWithSeparator` concatenates strings inside a loop, giving O(n²) behaviour. | Use `string.Join` (as `JoinWithSeparatorFixed` already does). |
| Services/UserService.cs | 87-92 | `GetAuditReport` concatenates strings inside a loop over an unbounded list, giving O(n²) behaviour. | Use `string.Join(Environment.NewLine, _auditLog)` or a `StringBuilder`. |
| Helpers/StringHelper.cs | 16 | `IsValidEmail` constructs a new `Regex` on every call instead of caching it. | Make it a `private static readonly Regex` with `RegexOptions.Compiled`, or use `[GeneratedRegex]`. |
| Helpers/StringHelper.cs | 25 | `IsValidUsername` constructs a new `Regex` on every call. | Same fix as above. |
| Services/UserService.cs | 10 | `_auditLog` is a shared mutable `static List<string>` mutated from `UpdateUser` and `DeleteUser` with no synchronisation, risking corruption under concurrent requests. | Replace with a persisted audit table or a thread-safe logger. |
| Services/UserService.cs | 10 | `_auditLog` grows without bound for the lifetime of the process, a slow memory leak. | Persist entries and cap in-memory retention. |
| Services/UserService.cs | 11, 25, 59 | `_requestCount++` on a shared static int is not atomic and will lose increments under concurrency. | Use `Interlocked.Increment` or, better, a proper metrics counter. |
| Helpers/StringHelper.cs | 65-71 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`. | Delete it and call the BCL method. |
| Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection` leaks resource ownership to callers with no XML-doc contract stating who disposes it. | Make it private, or document and enforce the contract via a wrapper type. |
| Data/DatabaseHelper.cs | 26 | `ExecuteQuery` is a helper whose signature (`tableName`, `whereClause`) makes safe use impossible. | Delete the method. |
| Data/DatabaseHelper.cs | 50 | `ExecuteNonQuery(string sql)` accepts a raw SQL fragment with no parameter support, encouraging injection at every call site. | Add a parameterised overload and remove the raw one. |
| Services/UserService.cs | 20-23 | The `id <= 0` / `id > 1000000` validation block in `GetUserById` is duplicated verbatim. | Extract a private `ValidateUserId(int id)` helper. |
| Services/UserService.cs | 40-43 | The same validation block is repeated verbatim in `UpdateUser`. | Call the extracted `ValidateUserId`. |
| Services/UserService.cs | 54-57 | The same validation block is repeated verbatim a third time in `DeleteUser`. | Call the extracted `ValidateUserId`. |
| Services/TransactionService.cs | 23-61 | `Transfer` carries at least five responsibilities: input validation, loading both accounts, fee computation, persisting balances and the ledger row, and sending notification email. | Split into `ValidateTransferRequest`, `LoadAccounts`, `CalculateFee`, `ApplyTransfer` (transactional) and an event-driven notification. |
| Services/AuthService.cs | 28-59 | `Login` carries three distinct responsibilities: password hashing, raw ADO.NET query and row mapping, and the backdoor credential check. | Extract `IPasswordHasher`, a `UserRepository.FindActiveByCredentials`, and delete the backdoor. |
| Services/TransactionService.cs | 63-75 | `Deposit` mixes validation, interest calculation and two unrelated persistence operations. | Extract `ValidateDepositAmount` and `CalculateInterestBonus` helpers. |
| Services/EmailService.cs | 34-61 | `SendTransferNotification` mixes body composition, message construction and retry orchestration. | Extract `BuildTransferBody` and a generic `SendWithRetry(MailMessage)`. |
| Services/EmailService.cs | 16-32 | `SmtpClient` is a long-lived field on a scoped service; `System.Net.Mail.SmtpClient` is also documented by Microsoft as obsolete for new development. | Move to MailKit behind an `IEmailSender` interface. |
| Program.cs | 10-14 | Services are registered as concrete classes (`UserService`, `AuthService`, `TransactionService`, `EmailService`, `DatabaseHelper`) with no interfaces, making unit testing with mocks impossible. | Introduce `IUserService`, `IAuthService`, `ITransactionService`, `IEmailSender` and `IDbAccessor` abstractions. |
| Services/UserService.cs, TransactionService.cs, AuthService.cs | all | Every database call is synchronous in an ASP.NET Core request pipeline, blocking thread-pool threads. | Convert to `async`/`await` with `ExecuteReaderAsync`/`ExecuteNonQueryAsync`. |
| Services/UserService.cs | 111-123 | `MapRowToUser` uses stringly-typed column indexers with hard casts and no `DBNull` handling. | Use `DataRow.Field<T>()` or move to a micro-ORM such as Dapper. |
| Services/UserService.cs | 49, 65 | `UpdateUser` and `DeleteUser` return a `bool` that is always `true`, a meaningless contract. | Return the affected-row count or `void`. |
| Services/TransactionService.cs | 23, 63 | `Transfer` and `Deposit` return `(bool, string)` tuples with free-text messages that the controller pattern-matches on. | Return a typed `Result` object with an error enum. |
| Controllers/UserController.cs | 28, 34 | `GetUser` and `GetUsers` return the `User` entity (including `Balance` and `Role`) directly rather than a DTO. | Introduce a `UserResponse` DTO. |
| Controllers/AuthController.cs | 30 | `Login` returns an anonymous object as the API contract, which cannot be documented or versioned. | Return a declared `LoginResponse` type. |
| Controllers/TransactionController.cs | 15 | The injected `_logger` field is dead weight because no action logs anything. | Add failure logging in `Transfer`, `Deposit` and `Refund`. |
| Models/Transaction.cs, User.cs | all | Request models have no `[Required]`, `[Range]` or `[EmailAddress]` data annotations, so `[ApiController]` automatic model validation does nothing. | Annotate `TransferRequest.Amount`, `DepositRequest.Amount`, `UpdateUserRequest.Email` and `LoginRequest`. |
| Models/User.cs | 7 | The `User` entity exposes a `Password` property that flows through the same object returned from controllers. | Remove it from the response model or use a separate persistence entity. |
| SampleBankingApp.csproj | 7 | `TreatWarningsAsErrors=false` lets unused-private-member and nullable warnings (e.g. `HashPasswordSha1`, unreachable code in `ValidateToken`) accumulate unnoticed. | Set it to `true` for CI builds. |
| Data/DatabaseHelper.cs | 9 | `DatabaseHelper` is a static-style utility registered as a singleton rather than a repository abstraction, so every service reimplements SQL. | Replace with per-aggregate repositories (`IUserRepository`, `ITransactionRepository`). |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| Program.cs | 34 | `app.UseDeveloperExceptionPage()` is called unconditionally for all environments. | Guard with `app.Environment.IsDevelopment()`. |
| Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry checking. | Set to `true` and add `ClockSkew = TimeSpan.FromSeconds(30)`. |
| Program.cs | 36 | `app.UseHttpsRedirection()` is commented out. | Uncomment and add `app.UseHsts()` for production. |
| Program.cs | 38 | The CORS policy allows any origin, method and header on a financial API. | Configure a named policy with a specific origin list. |
| Program.cs | 38 | An inline anonymous CORS policy is used rather than a named policy registered via `AddCors`. | Register `AddCors(o => o.AddPolicy("Api", ...))` and reference it by name. |
| Program.cs | 9-30 | No rate limiting is configured even though .NET 8 ships `AddRateLimiter`, leaving `/api/auth/login` unprotected. | Add `builder.Services.AddRateLimiter(...)` and `app.UseRateLimiter()`. |
| Program.cs | 9 | No global authorisation fallback policy is registered. | Add `AddAuthorization(o => o.FallbackPolicy = ...RequireAuthenticatedUser())`. |
| Program.cs | 32-42 | No `UseExceptionHandler`, health checks, or Swagger/OpenAPI registration exists. | Add production exception handling and health endpoints. |
| appsettings.json | 3, 6, 14 | Production database, JWT and SMTP secrets are all committed to source control. | Move to user secrets locally and environment variables / Key Vault in production, and rotate all three. |
| appsettings.json | 18-20 | `Default`, `Microsoft` and `System` log levels are all set to `Debug`, which will flood production logs and can leak SQL text. | Use `Information` for `Default` and `Warning` for framework namespaces. |
| appsettings.json | 23 | `AllowedHosts` is `*`, disabling host-header filtering. | Restrict to the known public hostnames. |
| appsettings.json | 12 | SMTP port 25 with `EnableSsl = false` in code means plaintext mail submission. | Use port 587 with TLS. |
| (repository root) | — | There is no `appsettings.Development.json` or `appsettings.Production.json`, so environment-specific overrides are impossible. | Add both files and keep only non-secret defaults in the base file. |
| SampleBankingApp.csproj | 8-9 | `DebugSymbols=true` and `DebugType=full` apply to every configuration including Release. | Move to a `Condition="'$(Configuration)'=='Debug'"` property group. |
| SampleBankingApp.csproj | 15 | `Newtonsoft.Json` 12.0.3 is both outdated (CVE-2024-21907) and entirely unreferenced by the code. | Remove the package reference. |
| SampleBankingApp.csproj | 14 | `System.Data.SqlClient` 4.8.6 is the deprecated driver with no ongoing security support. | Migrate to `Microsoft.Data.SqlClient` 5.2.x. |
| SampleBankingApp.csproj | 16 | `System.IdentityModel.Tokens.Jwt` 7.0.0 is behind the current 7.x/8.x security patch line. | Update to the latest 7.x or 8.x release. |
| SampleBankingApp.csproj | 13 | `Microsoft.AspNetCore.Authentication.JwtBearer` 8.0.0 is the initial 8.0 release and is missing subsequent patches. | Update to the latest 8.0.x patch. |
| SampleBankingApp.csproj | 3-10 | No `UserSecretsId` is declared, so there is no supported local secret store. | Add `<UserSecretsId>` and run `dotnet user-secrets init`. |
| SampleBankingApp.csproj | 3-10 | No `Directory.Packages.props` or `<ManagePackageVersionsCentrally>`, and no NuGet audit setting. | Add `<NuGetAudit>true</NuGetAudit>` to surface vulnerable dependencies at build time. |

## 10. Missing Unit Tests

No test project exists in the repository — there is no `*.Tests.csproj`, no solution file referencing one, and no test framework package reference in `SampleBankingApp.csproj`. The following are the highest-value tests to add.

| File | Line | Issue | Fix |
|---|---|---|---|
| (repository root) | — | No test project of any kind exists for a financial application. | Add an xUnit project with `Microsoft.AspNetCore.Mvc.Testing`, `Moq` and `FluentAssertions`, plus interfaces to make the services mockable. |
| Services/UserService.cs | 68-83 | `GetUsersPage` has no test proving the offset for `page = 1` starts at row 0. | Add tests for `page=1`, `page=2`, `page=0` and `page=-1` asserting the computed `@Skip` value. |
| Services/UserService.cs | 70 | `GetUsersPage` page-size clamping is untested at the boundaries. | Test `pageSize = 49, 50, 51, 0, -1` and assert the clamped result. |
| Services/TransactionService.cs | 42-44 | `Transfer` has no test proving a balance exactly equal to `amount` is rejected when a fee applies. | Test balance == amount, balance == amount + fee - 0.01, and balance == amount + fee. |
| Services/TransactionService.cs | 25 | `Transfer` has no test for `amount = 0` and `amount = -1`. | Assert both are rejected with "Amount must be positive". |
| Services/TransactionService.cs | 23 | `Transfer` has no test for `fromUserId == toUserId`. | Assert a self-transfer is rejected and no balance changes. |
| Services/TransactionService.cs | 39 | `Transfer` fee rounding at 0.015 is untested for half-cent cases. | Test amounts such as 0.33, 1.00, 33.34 and assert the rounded fee. |
| Services/TransactionService.cs | 36-37 | `Transfer` has no test for a non-existent sender or recipient id. | Assert a friendly failure rather than `IndexOutOfRangeException`. |
| Services/TransactionService.cs | 47-50 | `Transfer` has no test proving atomicity when the second `UPDATE` fails. | Add an integration test with a failing second write and assert the first is rolled back. |
| Services/TransactionService.cs | 52-55 | `Transfer` has no test for the case where the notification email throws after the debit committed. | Assert the transfer still reports success and the failure is logged. |
| Services/TransactionService.cs | 65-68 | `Deposit` has no test for the cap boundary or the interest bonus. | Test 0, 1, 1000000, 1000001 and assert the resulting credited amount. |
| Services/TransactionService.cs | 77-85 | `IsWithinDailyLimit` has no test at counts 9, 10 and 11. | Add boundary tests and wire the method into `Transfer`. |
| Services/AuthService.cs | 28-59 | `Login` has no test proving a SQL-injection payload in `username` cannot authenticate. | Add a test with `' OR '1'='1' --` asserting `null` is returned. |
| Services/AuthService.cs | 53-56 | The admin backdoor branch has no test documenting or forbidding its existence. | Add a regression test asserting `admin`/`SuperAdmin2024` is rejected after removal. |
| Services/AuthService.cs | 68-89 | `GenerateJwtToken` has no test asserting claims, issuer, audience and expiry. | Assert `NameIdentifier`, `Name`, `Role` and that `ValidTo` matches the configured lifetime. |
| Services/AuthService.cs | 98-108 | `ValidateToken` has no test, and would currently pass any garbage string. | Test expired, tampered-signature and well-formed tokens. |
| Services/UserService.cs | 20-23 | `GetUserById` id validation has no boundary tests. | Test `-1`, `0`, `1`, `1000000` and `1000001`. |
| Services/UserService.cs | 95-109 | `SearchUsers` has no test proving that a database failure is not indistinguishable from zero results. | Assert an exception surfaces rather than an empty list. |
| Services/UserService.cs | 95-109 | `SearchUsers` has no test for wildcard-injection input such as `%` or `'`. | Assert the query is escaped and does not return all rows. |
| Controllers/UserController.cs | 38-69 | `UpdateUser` and `DeleteUser` have no tests asserting that a non-owner is rejected. | Add tests with a mismatched `NameIdentifier` claim asserting 403. |
| Controllers/UserController.cs | 78-82 | `GetAuditLog` has no test asserting a non-admin receives 403. | Add role-based authorisation tests. |
| Controllers/TransactionController.cs | 26-27, 40-41 | `Transfer` and `Deposit` have no test for a token missing the `NameIdentifier` claim. | Assert `401` rather than an unhandled `ArgumentNullException`. |
| Controllers/AuthController.cs | 19-31 | `Login` has no test for repeated failed attempts triggering lockout or rate limiting. | Add a test asserting `429` after N failures once rate limiting is added. |
| Helpers/StringHelper.cs | 11-27 | `IsValidEmail` and `IsValidUsername` have no tests despite being pure, trivially testable validators. | Add table-driven tests including null, empty, 254/255-character and boundary-length inputs. |
| Helpers/StringHelper.cs | 43-57 | `MaskAccountNumber` and `ObfuscateAccount` have no tests for strings of length 0, 3, 4 and 5. | Add boundary tests and delete whichever implementation fails. |
| Data/DatabaseHelper.cs | 36-48 | `ExecuteQuerySafe` has no test verifying parameters are bound rather than concatenated. | Add an integration test against LocalDB or a Testcontainers SQL Server instance. |

---

### Summary of the most urgent items

1. **Authentication bypass** — `AuthService.Login` (line 32) is injectable and (line 53) contains a hardcoded `SuperAdmin` backdoor.
2. **Money loss** — `TransactionService.Transfer` (lines 42-48) permits negative balances, has no self-transfer guard, and performs three writes with no transaction.
3. **Money creation** — `TransactionService.Deposit` (line 68) credits an unearned 5% bonus on every deposit.
4. **Committed production secrets** — `appsettings.json` lines 3, 6 and 14 must be rotated immediately after removal.
5. **Broken access control** — `UserController.UpdateUser`/`DeleteUser`/`GetAuditLog` allow any authenticated user to act on any account.