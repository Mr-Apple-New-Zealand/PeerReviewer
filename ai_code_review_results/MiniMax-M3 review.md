## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection via string interpolation of username and hashedPassword in WHERE clause. | Use parameterised SqlCommand with SqlParameter objects. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | SQL injection in `ExecuteQuery` via unsanitised tableName and whereClause concatenation. | Whitelist table names and use parameterised WHERE clauses or remove the method. |
| SampleBankingApp/Services/UserService.cs | 99 | SQL injection in `SearchUsers` via `query` interpolated into LIKE clause. | Pass `query` as a SqlParameter and use `LIKE @q + '%'` syntax. |
| SampleBankingApp/Services/UserService.cs | 47 | SQL injection in `UpdateUser` via email and username interpolation. | Use SqlParameters for the SET clause values. |
| SampleBankingApp/Services/UserService.cs | 61 | SQL injection risk in `DeleteUser` via string-interpolated id despite int typing. | Use SqlCommand parameters instead of building SQL by interpolation. |
| SampleBankingApp/Services/TransactionService.cs | 89-90 | SQL injection in `RecordTransaction` via interpolated `type` and `description` strings. | Replace all interpolated values with SqlParameters. |
| SampleBankingApp/Services/TransactionService.cs | 47-48 | Transfer debit/credit SQL built by string interpolation in `ExecuteNonQuery`. | Use parameterised UPDATE statements with named parameters. |
| SampleBankingApp/Services/TransactionService.cs | 71 | Deposit UPDATE statement built by string interpolation. | Use SqlParameters for amount and userId. |
| SampleBankingApp/Services/AuthService.cs | 17,53-56 | Hardcoded admin backdoor password `"SuperAdmin2024"` grants SuperAdmin access regardless of DB credentials. | Remove the constant and bypass branch entirely. |
| SampleBankingApp/Services/AuthService.cs | 61-66 | Passwords hashed with unsalted MD5, an insecure broken algorithm. | Migrate to PBKDF2, bcrypt, or Argon2 with a per-user salt. |
| SampleBankingApp/Services/AuthService.cs | 91-96 | SHA1 password hashing routine present, also unsalted and cryptographically broken. | Delete the method and rely solely on a salted KDF. |
| SampleBankingApp/appsettings.json | 6 | JWT signing key `mysecretkey` is short and committed to source control. | Generate a 256-bit random key and load it from a secret store. |
| SampleBankingApp/appsettings.json | 3 | Production database credentials (sa / Admin1234!) committed in appsettings.json. | Move secrets to environment variables or a secret manager. |
| SampleBankingApp/appsettings.json | 14 | Email account password `EmailPass99` committed in plain text. | Store email credentials outside the repository. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded fallback SQL connection string contains SA password. | Remove the fallback and fail-fast when configuration is missing. |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry enforcement. | Set `ValidateLifetime = true` and rely on token `expires` claim. |
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` is wired unconditionally and leaks stack traces in production. | Conditionally enable only in Development environment. |
| SampleBankingApp/Program.cs | 36 | `UseHttpsRedirection()` is commented out, leaving the API HTTP-only. | Uncomment and configure HSTS for production environments. |
| SampleBankingApp/Program.cs | 38 | CORS policy allows any origin, method, and header, enabling cross-site abuse. | Restrict to a known allowlist of origins and methods. |
| SampleBankingApp/Services/EmailService.cs | 29 | `EnableSsl = false` forces SMTP traffic over plaintext. | Set `EnableSsl = true` or use STARTTLS. |
| SampleBankingApp/Controllers/UserController.cs | 21-29 | `GetUser(int id)` has no ownership check, allowing any authenticated user to read any account. | Compare `id` to the authenticated user's claim before returning. |
| SampleBankingApp/Controllers/UserController.cs | 38-54 | `UpdateUser` lacks an ownership or admin-role check, allowing arbitrary profile changes. | Verify the caller matches the target id or has Admin role. |
| SampleBankingApp/Controllers/UserController.cs | 56-69 | `DeleteUser` lacks an ownership/admin check and can be invoked by any authenticated user. | Add `[Authorize(Roles="Admin")]` or compare caller id to target. |
| SampleBankingApp/Controllers/TransactionController.cs | 23-35 | `Transfer` does not verify that `fromUserId` (from claim) actually equals the source account owner beyond using the claim. | Cross-check the recipient ownership and require an explicit source id matching the caller. |
| SampleBankingApp/Services/AuthService.cs | 84 | JWT lifetime is 30 days, allowing long-lived token replay. | Shorten expiry to minutes with a refresh token flow. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/UserService.cs | 72 | `int skip = page * pageSize;` off-by-one; page 1 returns rows 20-39 instead of 0-19. | Compute `(page - 1) * pageSize` and reject `page < 1`. |
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check `fromBalance >= amount` ignores the fee, allowing `newFromBalance` to go negative. | Compare against `totalDebit` instead of `amount`. |
| SampleBankingApp/Services/TransactionService.cs | 23-61 | `Transfer` has no self-transfer guard, allowing transfers to the same user (which double-debits under current code). | Reject `fromUserId == toUserId` up front. |
| SampleBankingApp/Services/TransactionService.cs | 23-61 | `Transfer` never validates `toUserId` existence before reading row 0 of `toUserTable`. | Confirm `toUserTable.Rows.Count > 0` before accessing. |
| SampleBankingApp/Services/TransactionService.cs | 63-75 | `Deposit` applies a 5% interest bonus via `amount * 0.05m * 1`, where the `* 1` is leftover noise. | Drop the spurious multiply and document the actual rate. |
| SampleBankingApp/Services/TransactionService.cs | 65 | `Deposit` allows `amount == 0` only if `<=` triggers; the test uses `<= 0` but the success path then runs `RecordTransaction` of zero amount. | Reject zero amounts explicitly. |
| SampleBankingApp/Services/TransactionService.cs | 87-92 | `RecordTransaction` types and descriptions are interpolated, so values like `O'Brien` corrupt the SQL. | Pass all values as SqlParameters. |
| SampleBankingApp/Services/UserService.cs | 38-50 | `UpdateUser` returns `true` regardless of whether any row matched. | Inspect rows-affected and return false when zero. |
| SampleBankingApp/Services/UserService.cs | 52-66 | `DeleteUser` returns `true` even when the id does not exist. | Return false when rows-affected is zero. |
| SampleBankingApp/Services/UserService.cs | 18-36 | `GetUserById` throws `ArgumentException` for invalid ids instead of returning null, breaking standard 404 semantics. | Replace throws with `return null` for not-found and 400 for malformed ids. |
| SampleBankingApp/Services/AuthService.cs | 40-58 | Admin bypass only triggers after `reader.Read()` returns false, so admin with wrong password fails first. | Verify the bypass path is intentional and ordered consistently. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | Regex unescapes `.` between local and domain parts, accepting emails like `a@b c`. | Escape the dot: `@"^[^@\s]+@[^@\s]+\.[^@\s]+$"` -> use `\`. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `MaskAccountNumber` treats accounts of length 4 or less as already masked, but for shorter strings no mask is applied at all. | Document and enforce a minimum length first. |
| SampleBankingApp/Services/TransactionService.cs | 39-40 | Fee is rounded to 2 dp but totalDebit isn't re-rounded, allowing sub-cent drift on very large amounts. | Round totalDebit to banker's rounding after adding fee. |
| SampleBankingApp/Controllers/UserController.cs | 71-76 | `SearchUsers` accepts negative or unbounded `query` length and feeds it straight into SQL. | Validate query length and contents before searching. |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/UserService.cs | 97-108 | `SearchUsers` catches all exceptions and silently returns an empty list, conflating error and no-match. | Let exceptions bubble or return a Result type distinguishing the two. |
| SampleBankingApp/Services/EmailService.cs | 71-78 | `SendWelcomeEmail` swallows all exceptions and only writes to Console, hiding failures. | Log via ILogger and surface failure to the caller. |
| SampleBankingApp/Services/EmailService.cs | 53-59 | `SendTransferNotification` writes to Console and rethrows after MaxRetries without logging context. | Use ILogger and add backoff between retries. |
| SampleBankingApp/Services/TransactionService.cs | 47-55 | Transfer writes two balances and inserts a transaction row without a database transaction, so partial failure corrupts state. | Wrap the three operations in a SqlTransaction. |
| SampleBankingApp/Services/TransactionService.cs | 52-55 | Email send happens after DB writes are committed, so an SMTP failure leaves the transfer done but no notification. | Move notification to an outbox table or compensating job. |
| SampleBankingApp/Controllers/UserController.cs | 48, 52 | Raw `ex.Message` returned to HTTP client in 400/500 responses. | Return generic messages and log details server-side. |
| SampleBankingApp/Controllers/AuthController.cs | 19-31 | `/login` lacks rate limiting and account lockout, allowing brute-force attacks. | Add a rate limiter middleware and lockout policy. |
| SampleBankingApp/Controllers/TransactionController.cs | 51-59 | `Refund` only catches `NotImplementedException`; any other exception returns 500 with no log. | Log and translate all exceptions to a structured ProblemDetails response. |
| SampleBankingApp/Services/AuthService.cs | 34-58 | `Login` has no try/catch and no using statements; any DB error propagates as an opaque 500. | Wrap in try/catch, dispose resources, log context. |
| SampleBankingApp/Program.cs | 34 | Unhandled exceptions surface full stack traces via developer exception page even in production. | Configure `UseExceptionHandler` with an environment check. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection` returns an opened `SqlConnection` with no contract obligating the caller to dispose it. | Return a connection owned by the caller or wrap callers in `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 26-34 | `ExecuteQuery` creates connection, command, and adapter with no using statements; nothing is disposed. | Wrap all three in `using` blocks. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` closes the connection but never disposes it or the command. | Use `using` for both connection and command. |
| SampleBankingApp/Services/AuthService.cs | 34-51 | `Login` creates connection, command, and reader without using; all three leak on the throw path. | Wrap each in `using` and dispose explicitly. |
| SampleBankingApp/Services/EmailService.cs | 16, 22-32 | `SmtpClient` is held as a singleton instance field, is not thread-safe, and is never disposed. | Create a new SmtpClient per send or inject a factory and dispose per request. |
| SampleBankingApp/Services/EmailService.cs | 39-50 | `MailMessage` in `SendTransferNotification` is never disposed, on either success or exception path. | Wrap the MailMessage in a `using` block. |
| SampleBankingApp/Services/EmailService.cs | 69-78 | `MailMessage` in `SendWelcomeEmail` is never disposed. | Wrap MailMessage in `using`. |
| SampleBankingApp/Services/EmailService.cs | 89-92 | `MailMessage` in `SendWelcomeEmailHtml` is never disposed and could leak if `Send` throws. | Wrap MailMessage in `using`. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` connection is left open if `ExecuteNonQuery` throws after the connection is opened. | Use `using` so disposal runs on the exception path too. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Program.cs | 28 | `Encoding.UTF8.GetBytes(jwtSecret!)` will throw NullReferenceException if `Jwt:SecretKey` is missing. | Validate the configuration value at startup and throw a meaningful exception. |
| SampleBankingApp/Services/AuthService.cs | 70 | `_config["Jwt:SecretKey"]!` dereferences a possibly-null config value per call. | Cache a validated key once at construction time. |
| SampleBankingApp/Services/AuthService.cs | 30 | `HashPasswordMd5(password)` accepts null and then dereferences it in `Encoding.UTF8.GetBytes`. | Validate the parameter before hashing. |
| SampleBankingApp/Services/AuthService.cs | 44-49 | `(int)reader["Id"]` and similar casts will throw `InvalidCastException` if the column is null. | Use `reader.IsDBNull` checks or `Convert.ToInt32` with default. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `email.Length` dereferences a possibly-null email parameter. | Use `string.IsNullOrEmpty(email)` before the length check. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | `username.Length` dereferences a possibly-null username parameter. | Null-check `username` first. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | `accountNumber.Length` dereferences a possibly-null accountNumber. | Null-check before reading length. |
| SampleBankingApp/Services/TransactionService.cs | 36-37 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without `Rows.Count > 0` check. | Guard with count checks before indexing. |
| SampleBankingApp/Services/TransactionService.cs | 83 | `table.Rows[0]["TxCount"]` accessed without verifying any rows returned. | Check `Rows.Count > 0` first. |
| SampleBankingApp/Services/UserService.cs | 99 | `query` could be null when interpolated into the LIKE clause. | Reject null/empty query before building the SQL. |
| SampleBankingApp/Services/EmailService.cs | 65 | `username.ToUpper()` will throw if username is null. | Null-check or use `username?.ToUpper() ?? string.Empty`. |
| SampleBankingApp/Controllers/TransactionController.cs | 27, 41 | `int.Parse(userIdClaim!)` throws if claim is null or non-numeric. | Validate the claim presence and use `TryParse`. |
| SampleBankingApp/Controllers/AuthController.cs | 22 | `request.Username`/`request.Password` can be null and are passed straight to the service. | Add null/empty guards before calling Login. |
| SampleBankingApp/Controllers/UserController.cs | 39, 43 | `UpdateUser` uses `request.Email`/`request.Username` without null validation. | Validate model state and reject nulls. |
| SampleBankingApp/Services/EmailService.cs | 24 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` falls back silently to 25 when config is missing. | Validate configuration explicitly at startup. |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 11-18 | `IsValidEmail` is defined but no caller exists in the codebase. | Delete or wire into `UserService.UpdateUser` validation. |
| SampleBankingApp/Helpers/StringHelper.cs | 20-27 | `IsValidUsername` is defined but has no callers. | Delete or invoke during registration/update flows. |
| SampleBankingApp/Helpers/StringHelper.cs | 29-36 | `JoinWithSeparator` has no callers; `JoinWithSeparatorFixed` exists alongside it. | Remove `JoinWithSeparator` and use `string.Join` directly. |
| SampleBankingApp/Helpers/StringHelper.cs | 38-41 | `JoinWithSeparatorFixed` is defined but never invoked. | Delete or replace usages of `JoinWithSeparator`. |
| SampleBankingApp/Helpers/StringHelper.cs | 43-52 | `MaskAccountNumber` has no callers; `ObfuscateAccount` exists alongside. | Delete the unused variant and keep one. |
| SampleBankingApp/Helpers/StringHelper.cs | 54-57 | `ObfuscateAccount` is defined but never called. | Delete or use in display paths. |
| SampleBankingApp/Helpers/StringHelper.cs | 59-63 | `ToTitleCase` has no callers. | Delete or use in a presentation layer. |
| SampleBankingApp/Helpers/StringHelper.cs | 65-71 | `IsBlank` duplicates `string.IsNullOrWhiteSpace` and is never called. | Delete the method. |
| SampleBankingApp/Data/DatabaseHelper.cs | 59-65 | `TableExists` is defined but no caller exists. | Delete or use in startup migrations. |
| SampleBankingApp/Data/DatabaseHelper.cs | 67-78 | `ExecuteQueryWithParams` is marked `[Obsolete]` and has no callers. | Remove the method entirely. |
| SampleBankingApp/Services/AuthService.cs | 91-96 | `HashPasswordSha1` is private and never invoked. | Delete the unused method. |
| SampleBankingApp/Services/AuthService.cs | 98-108 | `ValidateToken` has no callers and contains unreachable code after `return true`. | Delete the method or fix the logic and wire it in. |
| SampleBankingApp/Services/AuthService.cs | 105-107 | Code after an unconditional `return true` is unreachable inside `ValidateToken`. | Remove the dead block. |
| SampleBankingApp/Services/EmailService.cs | 63-79 | `SendWelcomeEmail` is defined but no caller exists. | Delete or wire into user registration. |
| SampleBankingApp/Services/EmailService.cs | 86-92 | `SendWelcomeEmailHtml` has no callers; its private `BuildHtmlTemplate` helper is only used by it. | Delete both methods. |
| SampleBankingApp/Services/TransactionService.cs | 77-85 | `IsWithinDailyLimit` is private and never called from `Transfer` or `Deposit`. | Wire the check into `Transfer` or delete. |
| SampleBankingApp/Services/TransactionService.cs | 94-97 | `FormatCurrency` is private and never invoked. | Delete the unused method. |
| SampleBankingApp/Services/TransactionService.cs | 99-103 | `RefundTransaction` is invoked by the controller but throws `NotImplementedException` in non-stub code. | Either implement the logic or hide the endpoint behind a feature flag. |
| SampleBankingApp/Services/UserService.cs | 25, 59 | `_requestCount` is incremented but never read anywhere, so the writes are dead. | Remove the counter or expose it via a metric. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 65 | Magic number `1000000` for max deposit limit. | Move to `appsettings.json` or named constant `MaxDepositAmount`. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Magic rate `0.05m` for deposit interest bonus. | Move to configuration and document intent. |
| SampleBankingApp/Services/UserService.cs | 22, 42, 56 | Magic number `1000000` for max user ID repeated in three places. | Extract to a shared constant or use `int.MaxValue`. |
| SampleBankingApp/Services/UserService.cs | 70 | Magic number `50` caps page size silently. | Move to a named constant and return 400 when exceeded. |
| SampleBankingApp/Controllers/UserController.cs | 32 | Magic number `20` default page size. | Move to configuration so clients and server agree. |
| SampleBankingApp/Services/AuthService.cs | 84 | Magic number `30` for token lifetime in days. | Move to configuration as `Jwt:ExpiryDays`. |
| SampleBankingApp/Services/EmailService.cs | 40, 69, 89 | Email address `notifications@company.com` hardcoded in three send methods. | Move to `Email:FromAddress` configuration. |
| SampleBankingApp/Services/EmailService.cs | 67 | Support email `support@company.com` hardcoded in message body. | Move to configuration. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | Magic number `254` for max email length. | Extract to a named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | Magic numbers `3` and `20` for username length. | Extract to named constants. |
| SampleBankingApp/Services/UserService.cs | 45, 64 | Audit log format strings are hardcoded inline. | Centralise audit message templates in a helper. |
| SampleBankingApp/Services/TransactionService.cs | 50 | Transaction `Type` literal `"Transfer"` hardcoded; same for `"Deposit"`. | Use an enum or shared constants class. |
| SampleBankingApp/Services/TransactionService.cs | 89 | Transaction `Status` literal `'Completed'` hardcoded in SQL. | Use an enum and parameterise. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Failure message literal `"Username not found or incorrect password"` repeated string. | Centralise auth error messages in a resource file. |
| SampleBankingApp/Services/AuthService.cs | 55 | Role literal `"SuperAdmin"` hardcoded. | Move to a `Roles` constants class. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 31-35 | `JoinWithSeparator` uses `+=` inside a loop, O(n²) string allocation. | Replace with `string.Join(separator, items)`. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | `new Regex(...)` allocated inside `IsValidEmail`, recompiled on every call. | Make the regex `static readonly`. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | `new Regex(...)` allocated inside `IsValidUsername`, recompiled on every call. | Make the regex `static readonly`. |
| SampleBankingApp/Services/UserService.cs | 10-11 | Static `_auditLog` and `_requestCount` mutated from instance methods with no synchronisation. | Make instance fields or use `ConcurrentBag`/`Interlocked`. |
| SampleBankingApp/Services/UserService.cs | 85-93 | `GetAuditReport` concatenates strings in a loop, O(n²). | Use `string.Join('\n', _auditLog)`. |
| SampleBankingApp/Helpers/StringHelper.cs | 65-71 | `IsBlank` re-implements `string.IsNullOrWhiteSpace`. | Delete and call the BCL method. |
| SampleBankingApp/Data/DatabaseHelper.cs | 19-24 | `GetOpenConnection` leaks ownership of an open connection with no documented contract. | Document the disposal requirement or return an `IDisposable` wrapper. |
| SampleBankingApp/Controllers/UserController.cs | 38-54 | Duplicated `try/catch (Exception ex)` block that returns raw `ex.Message`. | Extract a shared exception filter attribute or ProblemDetails helper. |
| SampleBankingApp/Services/TransactionService.cs | 23-61 | `Transfer` mixes validation, balance reads, two updates, transaction record insertion, and email send - 5 distinct responsibilities. | Split into `ValidateTransfer`, `ApplyTransfer`, `NotifyRecipient` helpers. |
| SampleBankingApp/Services/AuthService.cs | 28-59 | `Login` mixes SQL execution, MD5 hashing, and admin bypass logic - 3 distinct responsibilities. | Extract `VerifyCredentials` and `LookupUser` helpers. |
| SampleBankingApp/Services/EmailService.cs | 34-92 | All three `Send*` methods duplicate MailMessage creation and SMTP send logic. | Extract a single `SendAsync(MailMessage)` helper to centralise retry/cleanup. |
| SampleBankingApp/Services/UserService.cs | 18-66 | `GetUserById`, `UpdateUser`, `DeleteUser` each repeat the same id validation block. | Extract a `ValidateId(int id)` helper. |
| SampleBankingApp/Services/EmailService.cs | 34-61 | Retry loop in `SendTransferNotification` calls `Send` immediately on each attempt without backoff. | Add `Thread.Sleep` or exponential backoff between retries. |
| SampleBankingApp/Controllers/TransactionController.cs | 23-35 | `Transfer` reads the user id claim with `int.Parse` and null-forgiving operator. | Replace with a typed helper that validates the claim once. |
| SampleBankingApp/Data/DatabaseHelper.cs | 50-57 | `ExecuteNonQuery` uses raw concatenation by convention; the safer `ExecuteQuerySafe` is bypassed. | Make `ExecuteNonQuery` require parameters and remove the unsafe overload. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Program.cs | 34 | `UseDeveloperExceptionPage()` runs in every environment. | Replace with `app.UseExceptionHandler("/error")` and gate the dev page by `IsDevelopment`. |
| SampleBankingApp/Program.cs | 24 | `ValidateLifetime = false` makes JWT expiry ineffective. | Set `ValidateLifetime = true`. |
| SampleBankingApp/Program.cs | 36 | `UseHttpsRedirection()` is commented out, leaving the API on plaintext HTTP. | Uncomment and configure HSTS for production. |
| SampleBankingApp/Program.cs | 38 | CORS policy allows any origin, method, and header. | Restrict to a specific allowlist and methods list. |
| SampleBankingApp/appsettings.json | 17-21 | `LogLevel:Default`, `Microsoft`, and `System` set to `Debug` globally. | Default to `Information` and lower only in Development overrides. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | `DebugSymbols` set to `true` for release builds, shipping PDBs. | Set `DebugSymbols=false` in release configuration. |
| SampleBankingApp/SampleBankingApp.csproj | 9 | `DebugType` set to `full`, shipping detailed PDBs to production. | Use `DebugType=portable` or `none` for release. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | `Newtonsoft.Json 12.0.3` is outdated and has known CVEs. | Upgrade to the latest 13.x patch release. |
| SampleBankingApp/SampleBankingApp.csproj | 16 | `System.IdentityModel.Tokens.Jwt 7.0.0` is behind the current 8.x line. | Upgrade to the latest 8.x release. |
| SampleBankingApp | n/a | No `appsettings.Production.json` override file is present. | Add an env-specific override that tightens logging and disables dev endpoints. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Fallback hardcoded connection string bypasses configuration in any environment. | Throw if the connection string is missing instead of using a default. |

## 10. Missing Unit Tests

No test project is present in the supplied source tree. The following critical methods and scenarios should be covered first:

| Method | Scenario | Reason |
|--------|----------|--------|
| `AuthService.Login` | Verify that a SQL-injection payload in username is rejected as a normal login failure. | Confirms the parameterised query path is the only path executed. |
| `AuthService.Login` | Verify the admin bypass branch cannot be reached after it is removed. | Guards against re-introducing the hardcoded backdoor. |
| `AuthService.Login` | Verify passwords are verified with the salted hash, not MD5 of the plaintext. | Ensures the crypto migration is real. |
| `AuthService.GenerateJwtToken` | Verify the token's `exp` claim matches the configured expiry, not 30 days. | Confirms the long-lived token is fixed. |
| `TransactionService.Transfer` | Boundary: balance equals `amount + fee` should succeed; balance equals `amount` should fail. | Locks the fee-inclusive balance check. |
| `TransactionService.Transfer` | Self-transfer (`fromUserId == toUserId`) must be rejected without any DB writes. | Confirms the self-transfer guard. |
| `TransactionService.Transfer` | Verify the whole transfer (debit + credit + transaction row + email) rolls back if the email step throws. | Tests the outbox/transactional story. |
| `TransactionService.Transfer` | Verify that two concurrent transfers cannot overdraw the account (optimistic concurrency or row lock). | Race condition coverage. |
| `TransactionService.Deposit` | Boundary: amount = 0 must be rejected; amount = 1,000,001 must be rejected; amount = 1,000,000 accepted. | Locks the deposit limits. |
| `TransactionService.Deposit` | Verify the interest bonus formula matches the documented rate after the `* 1` is removed. | Catches accidental rate regressions. |
| `UserService.GetUsersPage` | Boundary: `page=1, pageSize=20` returns the first 20 rows; `page=2` returns rows 21-40; `page=0` is rejected or returns the first page. | Catches the `page * pageSize` off-by-one. |
| `UserService.GetUsersPage` | Verify `pageSize` is capped at the configured max instead of silently truncated. | Prevents silent paging changes. |
| `UserService.UpdateUser` | Boundary: id that does not exist returns false; id with invalid email returns ArgumentException. | Confirms error semantics. |
| `UserService.DeleteUser` | Boundary: id that does not exist returns false; concurrent deletes leave exactly one success. | Confirms delete semantics. |
| `UserService.SearchUsers` | Verify that single-quote and semicolon in `query` do not alter SQL. | Covers the LIKE injection fix. |
| `DatabaseHelper.ExecuteQuery` | Either remove from tests or write tests proving that injection in `whereClause` is rejected. | Pins the security story. |
| `DatabaseHelper.ExecuteNonQuery` | Verify the connection is disposed even when `ExecuteNonQuery` throws. | Locks the resource-leak fix. |
| `EmailService.SendTransferNotification` | Verify SMTP failure after MaxRetries throws and that MailMessage is disposed on every path. | Confirms the resource cleanup. |
| `EmailService.SendWelcomeEmail` | Verify it is either removed or actually invoked during registration tests. | Removes dead code path. |
| `StringHelper.IsValidEmail` / `IsValidUsername` | After wiring into the app, verify the regex rejects addresses with internal whitespace and usernames with disallowed characters. | Pins validation behaviour. |
| Auth flow tests | Verify the `[Authorize]` attribute rejects unauthenticated calls to transfer/deposit/refund endpoints. | Locks down access control. |
| Rate limiting tests | Verify the `/login` endpoint enforces rate limiting after N failed attempts. | Confirms brute-force protection. |
| `Program.cs` startup test | Verify that the application fails to start when `Jwt:SecretKey` is missing or shorter than 32 bytes. | Guards against weak signing keys. |