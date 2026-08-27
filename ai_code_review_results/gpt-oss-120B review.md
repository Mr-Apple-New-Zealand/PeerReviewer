## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 32 | SQL query built with string interpolation allows SQL injection on `username` and `hashedPassword`. | Use parameterised `SqlCommand` with `@Username` and `@Password` parameters. |
| AuthService.cs | 30 | Passwords are hashed with MD5, which is cryptographically weak. | Replace MD5 with a strong algorithm such as PBKDF2, bcrypt or Argon2 and store a salt. |
| AuthService.cs | 17 | Hard‑coded admin bypass password (`SuperAdmin2024`) is a backdoor. | Remove the bypass and enforce normal authentication. |
| AuthService.cs | 34‑41 | `SqlConnection`, `SqlCommand` and `SqlDataReader` are never disposed, exposing credentials and increasing attack surface. | Wrap them in `using` statements or `await using` async equivalents. |
| AuthService.cs | 68‑86 | JWT token is issued for 30 days while `ValidateLifetime` is set to `false`; tokens never expire. | Set `ValidateLifetime = true` and keep a reasonable expiration (e.g., 15 min). |
| Program.cs | 24 | `ValidateLifetime = false` disables token expiration validation. | Change to `ValidateLifetime = true`. |
| Program.cs | 34 | `UseDeveloperExceptionPage()` is enabled for all environments, leaking stack traces. | Enable it only in Development (`if (app.Environment.IsDevelopment())`). |
| Program.cs | 38 | CORS policy allows any origin, any method, any header – overly permissive. | Restrict origins to known clients and limit methods. |
| Program.cs | 36 | HTTPS redirection is commented out, allowing plain‑http traffic. | Uncomment `app.UseHttpsRedirection();`. |
| Program.cs | 16‑28 | JWT secret key is read from configuration that contains a hard‑coded value (`mysecretkey`). | Move secret to a secure store (Azure Key Vault, environment variable) and use a strong random key. |
| appsettings.json | 3 | Connection string contains hard‑coded SA password (`Admin1234!`). | Use a limited‑privilege account and store credentials securely (e.g., Azure Key Vault). |
| appsettings.json | 6 | JWT secret key is stored in plain text. | Store secret in a protected location, not in source‑controlled JSON. |
| appsettings.json | 13‑14 | SMTP username/password are stored in plain text. | Move to secret manager or environment variables. |
| EmailService.cs | 29 | `EnableSsl = false` sends credentials in clear text. | Set `EnableSsl = true` and use TLS. |
| EmailService.cs | 22‑31 | `SmtpClient` is kept as a singleton field and never disposed, which can leak sockets and expose credentials. | Create a new `SmtpClient` per send inside a `using` block or use `MailKit` with proper disposal. |
| TransactionService.cs | 47‑48 | UPDATE statements built with string interpolation allow SQL injection on `newFromBalance`, `newToBalance`, `fromUserId`, `toUserId`. | Use parameterised queries via `ExecuteQuerySafe` or a proper ORM. |
| TransactionService.cs | 70‑71 | INSERT statement built with string interpolation allows SQL injection on `description` and other fields. | Parameterise the INSERT and handle nulls safely. |
| UserService.cs | 47‑48 | UPDATE statement built with string interpolation allows SQL injection on `email` and `username`. | Use parameterised query (`ExecuteQuerySafe`). |
| UserService.cs | 61‑62 | DELETE statement built with string interpolation allows SQL injection on `id`. | Use parameterised query. |
| UserService.cs | 99‑100 | `ExecuteQuery` builds raw `WHERE` clause with user‑supplied `query`, enabling SQL injection. | Use parameterised LIKE (`WHERE Username LIKE @q`) and escape wildcards. |
| DatabaseHelper.cs | 29 | Table name and WHERE clause are concatenated directly into SQL, enabling injection. | Restrict table names to known constants and parameterise the WHERE clause. |
| DatabaseHelper.cs | 50‑55 | Non‑parameterised `ExecuteNonQuery` concatenates raw SQL, opening injection vector. | Use parameterised commands or `ExecuteQuerySafe`. |
| DatabaseHelper.cs | 15‑16 | Fallback connection string contains hard‑coded SA credentials. | Remove fallback or use a safe default without credentials. |
| AuthService.cs | 91‑96 | `HashPasswordSha1` uses SHA‑1, a broken hash algorithm, and is never used. | Remove the method or replace with a strong KDF if needed. |
| EmailService.cs | 81‑84 | HTML template built with string interpolation can lead to XSS if `title` or `body` contain malicious markup. | Encode user‑provided values or use a proper templating engine. |

---

## 2. Logic Errors
| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 42 | Funds check uses `fromBalance >= amount` but ignores the transaction fee, allowing negative balances. | Compare against `totalDebit` (`fromBalance >= totalDebit`). |
| TransactionService.cs | 23‑24 | No check prevents a user from transferring to themselves (`fromUserId == toUserId`). | Add a guard that returns error when `fromUserId == toUserId`. |
| TransactionService.cs | 23‑24 | Daily transaction limit (`IsWithinDailyLimit`) is never called, so limit can be bypassed. | Call `IsWithinDailyLimit` before processing and return error if exceeded. |
| TransactionService.cs | 70‑71 | Deposit adds `interestBonus` but does not enforce daily limit or fee logic; may allow unlimited deposits. | Apply the same daily‑limit check as transfers and ensure business rules are respected. |
| UserService.cs | 72 | Pagination offset is calculated as `page * pageSize` instead of `(page‑1) * pageSize`, skipping the first page. | Change to `int skip = (page - 1) * pageSize;`. |
| UserService.cs | 70 | No validation that `page` is ≥ 1, allowing negative offsets. | Clamp `page` to a minimum of 1. |
| AuthService.cs | 98‑108 | `ValidateToken` returns `true` before any validation; dead code after `return`. | Remove the early return and implement proper token validation (`handler.ValidateToken`). |
| TransactionService.cs | 90‑91 | `description` may be `null`; interpolating it into SQL results in the literal string `'null'`. | Pass `DBNull.Value` or handle null separately in the INSERT. |
| TransactionService.cs | 89‑91 | SQL string interpolation does not escape single quotes in `description`, causing syntax errors or injection. | Parameterise the INSERT statement. |
| TransactionService.cs | 47‑48 | Fee is calculated but not considered when checking `fromBalance`; also fee rounding may cause rounding errors. | Use `Math.Round` consistently and include fee in balance check. |
| TransactionService.cs | 23‑24 | No verification that `amount` is greater than zero (only `< 0` is checked). Zero‑amount transfers are allowed. | Change condition to `if (amount <= 0)`. |
| TransactionService.cs | 23‑24 | No verification that `toUserId` exists; could transfer to non‑existent account. | Verify existence of destination user before proceeding. |
| UserService.cs | 45 | `_auditLog` is a static mutable list accessed without synchronization; concurrent requests may corrupt it. | Protect with a lock or use a thread‑safe collection (`ConcurrentBag`). |
| UserService.cs | 11 | `_requestCount` is a static mutable int accessed without synchronization; race conditions possible. | Use `Interlocked.Increment`. |
| UserService.cs | 70‑71 | `GetUsersPage` caps `pageSize` at 50 but does not enforce a minimum; `pageSize` could be zero causing division by zero elsewhere. | Validate `pageSize >= 1`. |
| UserService.cs | 99‑100 | `SearchUsers` builds a `LIKE '%{query}%'` clause without escaping `%` or `_`, leading to unexpected matches. | Escape wildcard characters or use parameterised LIKE. |
| EmailService.cs | 36‑38 | Transfer notification body uses `$"{amount:F2}"` but does not enforce culture‑invariant formatting; could produce commas in some locales. | Use `CultureInfo.InvariantCulture`. |
| AuthService.cs | 30 | `hashedPassword` is computed before checking admin bypass; admin can bypass even with wrong password hash. | Perform admin bypass check before hashing or remove bypass entirely. |
| TransactionService.cs | 23‑24 | No transaction is wrapped in a database transaction; partial updates could leave data inconsistent. | Use a SQL transaction (`BEGIN TRANSACTION` / `COMMIT`). |
| TransactionService.cs | 47‑48 | Two separate `UPDATE` statements are executed; if the second fails, balances become inconsistent. | Execute both updates within a single transaction. |
| TransactionService.cs | 23‑24 | No concurrency control; simultaneous transfers could cause race conditions on balances. | Use row‑level locking or optimistic concurrency (e.g., `WHERE Balance = @expected`). |
| UserService.cs | 27‑30 | `GetUserById` increments `_requestCount` without thread safety. | Use `Interlocked.Increment`. |
| UserService.cs | 45 | `UpdateUser` does not validate email format or username length before persisting. | Reuse `StringHelper.IsValidEmail` / `IsValidUsername` for validation. |
| UserService.cs | 61 | `DeleteUser` does not check for related transactions; orphaned records may remain. | Add cascade delete or check constraints before deletion. |

---

## 3. Error Handling
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 34‑41 | `SqlConnection`, `SqlCommand`, and `SqlDataReader` are opened without `try/finally` or `using`; exceptions leak resources. | Wrap them in `using` blocks and log errors. |
| TransactionService.cs | 23‑24 | No `try/catch` around database calls; any DB failure bubbles up as 500 without a friendly message. | Add exception handling that logs the error and returns a controlled `BadRequest`. |
| TransactionService.cs | 70‑71 | `RecordTransaction` may throw if `description` contains a single quote; exception not caught. | Parameterise the INSERT and handle exceptions. |
| TransactionService.cs | 63‑64 | `Deposit` does not catch DB errors; could expose stack trace. | Add `try/catch` and return appropriate error response. |
| UserService.cs | 27‑30 | `GetUserById` does not catch DB exceptions; they propagate to controller as 500. | Catch and log, then return `null` or a proper error. |
| UserService.cs | 45‑48 | `UpdateUser` does not catch DB errors; may expose internal details. | Wrap in `try/catch` and return false on failure. |
| UserService.cs | 61‑63 | `DeleteUser` does not catch DB errors; may expose internal details. | Wrap in `try/catch` and log. |
| UserService.cs | 97‑108 | `SearchUsers` catches generic `Exception` and returns an empty list, hiding the failure reason. | Log the exception and return a proper error status (e.g., 500). |
| EmailService.cs | 45‑60 | Retry loop catches `SmtpException` but re‑throws after max attempts without logging the final failure. | Log the final failure before re‑throwing or return a failure result. |
| EmailService.cs | 71‑78 | `SendWelcomeEmail` catches generic `Exception` and only writes to console, swallowing the error. | Use `ILogger` to log and propagate or return a result indicating failure. |
| EmailService.cs | 22‑31 | Constructor creates `SmtpClient` with potentially null configuration values; may throw `ArgumentNullException`. | Validate configuration values and throw a clear configuration exception. |
| Program.cs | 34 | `UseDeveloperExceptionPage()` will expose stack traces to clients if an exception occurs. | Restrict to Development environment. |
| TransactionService.cs | 99‑102 | `RefundTransaction` throws `NotImplementedException`; controller catches and returns 500, leaking internal state. | Implement the method or return a proper 501 Not Implemented response. |
| TransactionService.cs | 23‑24 | No validation that `description` is within acceptable length; could cause DB errors. | Validate length before using it. |
| AuthService.cs | 98‑108 | `ValidateToken` returns early, making the rest of the method unreachable and hiding potential errors. | Remove the early return and implement proper validation. |

---

## 4. Resource Leaks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 34‑41 | `SqlConnection`, `SqlCommand`, and `SqlDataReader` are never disposed. | Use `using` statements for each disposable. |
| DatabaseHelper.cs | 21‑24 | `GetOpenConnection` returns an open `SqlConnection` that callers often never close. | Return a closed connection or provide a `using` wrapper; callers should dispose. |
| DatabaseHelper.cs | 28‑33 | `ExecuteQuery` opens a connection and creates `SqlCommand`/`SqlDataAdapter` without disposing them. | Wrap connection, command, and adapter in `using`. |
| DatabaseHelper.cs | 50‑55 | `ExecuteNonQuery` opens a connection and creates a command without disposing. | Use `using` for connection and command. |
| EmailService.cs | 16‑31 | `SmtpClient` is stored as a field and never disposed. | Dispose it when the service is disposed or create per‑send inside a `using`. |
| EmailService.cs | 39‑44 | `MailMessage` objects are created but never disposed. | Wrap each `MailMessage` in a `using` block. |
| EmailService.cs | 69‑70 | `MailMessage` in `SendWelcomeEmail` is not disposed. | Use `using`. |
| EmailService.cs | 88‑91 | `MailMessage` in `SendWelcomeEmailHtml` is not disposed. | Use `using`. |
| TransactionService.cs | 47‑48 | Two `ExecuteNonQuery` calls each open a connection that is never disposed (via `DatabaseHelper.ExecuteNonQuery`). | Refactor `ExecuteNonQuery` to use `using` or expose a method that returns a disposable transaction. |
| TransactionService.cs | 70‑71 | `RecordTransaction` builds a SQL string and calls `ExecuteNonQuery` which leaks the connection. | Ensure `ExecuteNonQuery` disposes its connection. |
| UserService.cs | 27‑30 | `ExecuteQuerySafe` returns a `DataTable` but the underlying `SqlConnection` is disposed correctly; however, the `DataTable` is not disposed by callers. | Caller should dispose or use `using` when appropriate. |
| StringHelper.cs | 31‑34 | `JoinWithSeparator` builds a string via repeated concatenation, creating many intermediate strings (memory pressure). | Use `StringBuilder` or `string.Join`. |
| Program.cs | 34 | `UseDeveloperExceptionPage()` may allocate detailed error pages that are never released in production. | Limit to Development environment. |

---

## 5. Null Reference Risks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionController.cs | 26‑27 | `User.FindFirst(... )?.Value` may be `null`; `int.Parse` on `null` throws. | Validate the claim and return `Unauthorized` if missing. |
| StringHelper.cs | 13‑15 | `IsValidEmail` accesses `email.Length` without null check. | Return `false` if `email` is `null`. |
| StringHelper.cs | 22‑24 | `IsValidUsername` accesses `username.Length` without null check. | Return `false` if `username` is `null`. |
| EmailService.cs | 22‑31 | Configuration values (`Email:SmtpHost`, `SmtpPort`, `Username`, `Password`) may be `null`, causing `ArgumentNullException`. | Validate each config value and throw a clear configuration exception. |
| EmailService.cs | 65‑66 | `SendWelcomeEmail` calls `username.ToUpper()` without null check. | Guard against `null` or require non‑null argument. |
| EmailService.cs | 81‑84 | `BuildHtmlTemplate` interpolates `title` and `body` which could be `null`. | Use `title ?? string.Empty` etc. |
| TransactionService.cs | 53‑55 | `description` may be `null`; passed to `RecordTransaction` which inserts it as a string literal `'null'`. | Handle `null` separately or pass `DBNull.Value`. |
| AuthService.cs | 30‑31 | `hashedPassword` is computed even when `username` is `"admin"` and bypass password is used; not a null issue but unnecessary work. | Move admin bypass before hashing. |
| TransactionService.cs | 70‑71 | `description` may contain single quotes, breaking the SQL string. | Parameterise the query. |
| UserService.cs | 45‑48 | `email` and `username` are used directly in SQL; if either is `null` the generated SQL will contain `NULL` literals causing syntax errors. | Validate inputs before building query or use parameters. |
| UserService.cs | 99‑100 | `query` may be `null`; string interpolation results in empty string, which may be unintended. | Guard against `null` and return empty result or error. |
| TransactionController.cs | 40‑41 | `userIdClaim` may be `null`; `int.Parse` will throw. | Validate claim existence before parsing. |
| TransactionController.cs | 41‑42 | Same as above for deposit endpoint. | Same fix. |

---

## 6. Dead Code
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 98‑108 | `ValidateToken` is never called anywhere in the solution. | Remove the method or integrate it into authentication pipeline. |
| TransactionService.cs | 77‑85 | `IsWithinDailyLimit` is defined but never used. | Either call it from `Transfer`/`Deposit` or delete it. |
| TransactionService.cs | 94‑98 | `FormatCurrency` is never used. | Remove or expose it for UI formatting. |
| EmailService.cs | 81‑84 | `BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml`, which itself is never called. | Remove both methods or expose them via a public API. |
| EmailService.cs | 86‑92 | `SendWelcomeEmailHtml` is never invoked. | Remove or add usage in a welcome flow. |
| EmailService.cs | 63‑78 | `SendWelcomeEmail` is never invoked. | Remove or integrate into user‑registration flow. |
| DatabaseHelper.cs | 68‑78 | `ExecuteQueryWithParams` is marked `[Obsolete]` and never referenced. | Delete the method. |
| StringHelper.cs | 31‑36 | `JoinWithSeparator` is never used. | Delete or replace calls with `string.Join`. |
| StringHelper.cs | 38‑41 | `JoinWithSeparatorFixed` is never used. | Delete or use where appropriate. |
| StringHelper.cs | 43‑52 | `MaskAccountNumber` is never used. | Delete if not needed. |
| StringHelper.cs | 54‑57 | `ObfuscateAccount` is never used. | Delete if not needed. |
| StringHelper.cs | 59‑63 | `ToTitleCase` is never used. | Delete if not needed. |
| StringHelper.cs | 65‑71 | `IsBlank` is never used. | Delete or replace with `string.IsNullOrWhiteSpace`. |
| AuthService.cs | 91‑96 | `HashPasswordSha1` is never called. | Remove the method. |
| TransactionService.cs | 99‑102 | `RefundTransaction` is only a stub that throws; controller catches it but no real implementation exists. | Implement refund logic or return a proper 501 response. |
| UserService.cs | 10‑11 | Static fields `_auditLog` and `_requestCount` are only used for logging/counting but never exposed outside the class except via `GetAuditReport`. | Consider removing or persisting these values elsewhere. |
| Program.cs | 36 | HTTPS redirection line is commented out and never executed. | Uncomment if HTTPS is required. |

---

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 15‑16 | Fallback connection string hard‑codes server, DB, user, and password. | Remove fallback or read from secure configuration. |
| AuthService.cs | 17 | Hard‑coded admin bypass password (`SuperAdmin2024`). | Remove backdoor and store admin credentials securely. |
| TransactionService.cs | 11 | Transaction fee rate `0.015m` is a magic number. | Move to a configurable setting or constant with a descriptive name. |
| TransactionService.cs | 12 | Max daily transactions `10` is a magic number. | Move to configuration. |
| UserService.cs | 70 | Page size limit `50` is a magic number. | Define a constant or configuration value. |
| UserController.cs | 32 | Default `pageSize = 20` is a magic number. | Use a constant or configuration. |
| UserController.cs | 32 | Default `page = 1` is a magic number. | Use a constant. |
| EmailService.cs | 10‑12 | Email subjects are hard‑coded strings. | Store in resources or configuration. |
| EmailService.cs | 14 | Max retry count `3` is a magic number. | Define a constant with a clear name. |
| EmailService.cs | 15 | SMTP timeout `5000` ms is a magic number. | Define a constant or read from config. |
| EmailService.cs | 40, 69, 90 | From address `"notifications@company.com"` is hard‑coded. | Move to configuration. |
| EmailService.cs | 67 | Support address `"support@company.com"` is hard‑coded. | Move to configuration. |
| StringHelper.cs | 16 | Email regex pattern is a magic string. | Store as a compiled static readonly field. |
| StringHelper.cs | 25 | Username regex pattern is a magic string. | Store as a compiled static readonly field. |
| Program.cs | 84 | JWT token expiration `30` days is a magic number. | Move to configuration. |
| Program.cs | 24 | `ValidateLifetime = false` disables a security feature (not a magic number but a misconfiguration). | Set to `true`. |
| appsettings.json | 3 | Connection string contains hard‑coded SA password. | Use a secret manager. |
| appsettings.json | 6 | JWT secret key is a plain string. | Store securely. |
| appsettings.json | 13‑14 | SMTP credentials are plain strings. | Store securely. |
| Program.cs | 18‑20 | Logging levels set to `Debug` for all categories. | Reduce to `Information` or `Warning` for production. |

---

## 8. Anti‑patterns and Code Quality
| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 31‑34 | Concatenating strings in a loop creates many temporary strings (O(n²) cost). | Use `StringBuilder` or `string.Join`. |
| StringHelper.cs | 16, 25 | New `Regex` objects are created on each call; they are not cached. | Declare static readonly compiled regexes. |
| AuthService.cs | 30‑41 | Direct ADO.NET usage without `using` leads to resource leaks and verbose code. | Switch to an ORM (e.g., Dapper) or wrap in helper methods with `using`. |
| AuthService.cs | 61‑66 | MD5 hashing is insecure. | Replace with a strong password‑hashing algorithm (PBKDF2, bcrypt). |
| AuthService.cs | 91‑96 | SHA‑1 hashing method is unused and insecure. | Remove it. |
| EmailService.cs | 16‑31 | `SmtpClient` is stored as a field and reused across threads; it is not thread‑safe. | Create a new client per send inside a `using` block or use a thread‑safe library. |
| EmailService.cs | 39‑44, 69‑70, 88‑91 | `MailMessage` objects are not disposed. | Wrap each in a `using` statement. |
| EmailService.cs | 45‑60 | Uses `Console.WriteLine` for logging instead of `ILogger`. | Replace with injected `ILogger<EmailService>`. |
| TransactionService.cs | 23‑24 | Method does validation, DB reads, fee calculation, DB updates, email sending, and transaction recording – multiple responsibilities. | Extract validation, DB update, and notification into separate private methods. |
| TransactionService.cs | 63‑71 | Deposit method mixes business logic, DB update, and transaction recording. | Split into `ValidateDeposit`, `UpdateBalance`, and `RecordDeposit`. |
| UserService.cs | 68‑71 | Pagination logic, DB query, and mapping are all in one method. | Separate mapping (`MapRowToUser`) is already present; keep pagination logic separate from data access. |
| UserService.cs | 38‑50 | `UpdateUser` repeats the same ID validation logic as `DeleteUser`. | Extract ID validation into a private helper. |
| UserService.cs | 52‑66 | `DeleteUser` repeats ID validation; same as above. | Use shared validation helper. |
| UserService.cs | 45‑48 | `_auditLog` is a static mutable list accessed without synchronization. | Replace with a thread‑safe collection or lock. |
| UserService.cs | 11‑12 | `_requestCount` is a static mutable int accessed without synchronization. | Use `Interlocked.Increment`. |
| DatabaseHelper.cs | 26‑33 | `ExecuteQuery` builds raw SQL with interpolated table name and where clause – high risk of injection. | Remove this method or enforce safe usage with parameters. |
| DatabaseHelper.cs | 50‑55 | `ExecuteNonQuery` builds raw SQL via interpolation – injection risk. | Replace with parameterised version. |
| DatabaseHelper.cs | 68‑78 | `[Obsolete]` method `ExecuteQueryWithParams` still present but unused. | Delete it. |
| TransactionService.cs | 89‑91 | SQL string interpolation includes `description` directly, risking injection and syntax errors. | Parameterise the INSERT. |
| TransactionService.cs | 47‑48 | Two separate UPDATE statements without a transaction – can leave data inconsistent. | Wrap both updates in a single transaction. |
| TransactionService.cs | 23‑24 | No concurrency control on balance updates – race conditions possible. | Use row‑level locking or optimistic concurrency. |
| TransactionService.cs | 23‑24 | No check for self‑transfer. | Add guard. |
| TransactionService.cs | 23‑24 | No daily‑limit check. | Call `IsWithinDailyLimit`. |
| TransactionService.cs | 23‑24 | No verification that destination user exists. | Query and verify `toUserId`. |
| TransactionService.cs | 23‑24 | No exception handling around DB calls. | Add try/catch and proper logging. |
| TransactionService.cs | 23‑24 | Returns generic `bool`/`string` tuple; callers cannot differentiate between validation failures and system errors. | Use a result type with error codes. |
| UserService.cs | 99‑108 | `SearchUsers` catches generic `Exception` and returns empty list, hiding errors. | Log the exception and return appropriate HTTP error. |
| UserService.cs | 45‑48 | Direct string interpolation for UPDATE – injection risk. | Use parameterised query. |
| UserService.cs | 61‑63 | Direct string interpolation for DELETE – injection risk. | Use parameterised query. |
| UserService.cs | 99‑100 | Direct string interpolation for LIKE clause – injection risk. | Parameterise the LIKE clause. |
| Program.cs | 34 | `UseDeveloperExceptionPage` is enabled globally – not suitable for production. | Guard with environment check. |
| Program.cs | 38 | `AllowAnyOrigin` CORS policy is overly permissive. | Restrict to known origins. |
| Program.cs | 36 | HTTPS redirection is commented out. | Enable it. |
| Program.cs | 18‑20 | Logging set to `Debug` for all categories in production. | Lower log level. |
| Program.cs | 8‑10 | Debug symbols are enabled in release builds. | Disable in production. |
| StringHelper.cs | 65‑71 | `IsBlank` manually checks null, empty, and whitespace; `string.IsNullOrWhiteSpace` already does this. | Replace with `string.IsNullOrWhiteSpace`. |
| StringHelper.cs | 59‑63 | `ToTitleCase` creates a new `CultureInfo` each call; could be cached. | Cache `TextInfo` or use static helper. |
| EmailService.cs | 81‑84 | HTML template built via string interpolation without sanitisation – XSS risk. | Encode inputs or use a templating engine. |
| EmailService.cs | 36‑38 | Amount formatted with `$` sign; culture‑dependent formatting may cause issues. | Use invariant culture. |
| TransactionService.cs | 23‑24 | No transaction scope; partial updates can leave system inconsistent. | Use `SqlTransaction`. |
| TransactionService.cs | 23‑24 | No explicit error handling; DB errors bubble up as 500. | Add try/catch and return domain‑specific errors. |
| TransactionService.cs | 23‑24 | Method does too many things – violates Single Responsibility Principle. | Split into validation, persistence, notification. |
| UserService.cs | 68‑71 | Pagination uses `OFFSET @Skip ROWS` but `skip` may be negative if `page` is 0. | Validate `page >= 1`. |
| UserService.cs | 70‑71 | `pageSize` capped at 50 but not validated for minimum; zero pageSize leads to division by zero in SQL. | Enforce `pageSize >= 1`. |
| UserService.cs | 45‑48 | No email format validation before updating. | Reuse `StringHelper.IsValidEmail`. |
| UserService.cs | 45‑48 | No username validation before updating. | Reuse `StringHelper.IsValidUsername`. |
| UserService.cs | 45‑48 | Direct string interpolation for UPDATE – injection risk. | Use parameters. |
| UserService.cs | 61‑63 | Direct string interpolation for DELETE – injection risk. | Use parameters. |
| UserService.cs | 99‑100 | Direct string interpolation for LIKE – injection risk. | Use parameters. |
| UserService.cs | 45‑48 | `_auditLog` grows unbounded; could exhaust memory. | Implement size limit or persist to storage. |
| UserService.cs | 10‑11 | `_requestCount` is never used outside the class. | Remove if unnecessary. |
| TransactionService.cs | 23‑24 | `description` may be null; string interpolation will produce `'null'`. | Handle null separately. |
| TransactionService.cs | 23‑24 | No check that `amount` is not excessively large (e.g., > balance). | Already checks balance but not fee; adjust. |
| TransactionService.cs | 23‑24 | No check for negative `amount` (only `< 0`). Zero amount allowed. | Change to `<= 0`. |
| TransactionService.cs | 23‑24 | No check for overflow when calculating `newFromBalance`. | Use checked arithmetic or validate. |
| TransactionService.cs | 23‑24 | No audit logging of transfers. | Add audit entry. |
| TransactionService.cs | 23‑24 | No unit‑of‑work pattern; DB calls are scattered. | Consolidate. |

---

## 9. Configuration Issues
| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 34 | `UseDeveloperExceptionPage()` is always enabled, exposing stack traces in production. | Wrap in `if (app.Environment.IsDevelopment())`. |
| Program.cs | 24 | `ValidateLifetime = false` disables JWT expiration validation. | Set to `true`. |
| Program.cs | 38 | CORS policy uses `AllowAnyOrigin`, `AllowAnyMethod`, `AllowAnyHeader`. | Restrict origins, methods, and headers to required values. |
| Program.cs | 36 | HTTPS redirection is commented out, leaving HTTP enabled. | Uncomment `app.UseHttpsRedirection();`. |
| Program.cs | 18‑20 | Logging levels are set to `Debug` for all categories, which is too verbose for production. | Change to `Information` or `Warning`. |
| SampleBankingApp.csproj | 8‑9 | `DebugSymbols` and `DebugType` are enabled, leaking symbol information in release builds. | Set to `false` for production builds. |
| appsettings.json | 3 | Connection string contains hard‑coded SA password. | Move credentials to a secret store. |
| appsettings.json | 6 | JWT secret key is stored in plain text. | Store in a secure vault or environment variable. |
| appsettings.json | 13‑14 | SMTP credentials are stored in plain text. | Store securely. |
| appsettings.json | 18‑20 | LogLevel set to `Debug` for Microsoft and System namespaces. | Reduce to `Warning` or `Error`. |
| EmailService.cs | 29 | `EnableSsl = false` disables encryption for SMTP. | Set to `true` and ensure the server supports TLS. |
| EmailService.cs | 22‑31 | Configuration values are accessed without validation; missing values cause runtime errors. | Validate and throw a clear configuration exception if missing. |
| AuthService.cs | 30‑41 | Raw SQL built with string interpolation; should be moved to parameterised queries or ORM. | Refactor to use parameters. |
| TransactionService.cs | 23‑24 | No transaction scope for multiple updates; could leave data inconsistent. | Wrap updates in a DB transaction. |
| TransactionService.cs | 23‑24 | No daily‑limit enforcement; business rule missing. | Add check using `IsWithinDailyLimit`. |
| TransactionService.cs | 23‑24 | No check for self‑transfer. | Add guard. |
| UserService.cs | 70‑71 | Pagination `skip` can become negative; no validation of `page`. | Validate `page >= 1`. |
| UserService.cs | 70‑71 | No maximum for `_auditLog` size; could grow indefinitely. | Implement rotation or persistence. |
| UserService.cs | 10‑11 | `_requestCount` is never exposed; may be unnecessary. | Remove if not needed. |
| Program.cs | 38 | CORS policy is defined inline; no named policy for reuse. | Define a named policy in `ConfigureServices`. |
| Program.cs | 34 | No `app.UseHsts()` for production. | Add HSTS middleware. |
| Program.cs | 34 | No `app.UseExceptionHandler("/error")` for production. | Add generic error handling middleware. |

---

## 10. Missing Unit Tests
| File | Line | Issue | Fix |
|------|------|-------|-----|
| (No test project) | – | The repository contains no unit‑test project, leaving core business logic unverified. | Add an xUnit/NUnit/MSTest project targeting .NET 8. |
| AuthService.cs | 28‑59 | `Login` logic (SQL query, admin bypass, password hashing) needs tests for successful login, failed login, admin bypass, and SQL‑injection resistance. | Write tests covering valid credentials, invalid credentials, admin bypass, and injection attempts. |
| AuthService.cs | 68‑86 | `GenerateJwtToken` should be tested for correct claims, expiration, and signature. | Add tests that decode the token and verify claims and expiry. |
| AuthService.cs | 98‑108 | `ValidateToken` (currently dead) – once implemented – needs tests for valid, expired, and malformed tokens. | Add tests for each scenario. |
| TransactionService.cs | 23‑58 | `Transfer` contains balance checks, fee calculation, self‑transfer guard, daily‑limit, and DB updates. | Write tests for successful transfer, insufficient funds, self‑transfer, fee correctness, and daily‑limit enforcement. |
| TransactionService.cs | 63‑71 | `Deposit` should be tested for amount validation, interest bonus calculation, and balance update. | Add tests for valid deposit, zero/negative amount, amount > 1 000 000, and bonus correctness. |
| TransactionService.cs | 77‑85 | `IsWithinDailyLimit` (currently unused) needs tests for limit enforcement. | Add tests for user under limit and over limit. |
| TransactionService.cs | 89‑92 | `RecordTransaction` should be tested for correct SQL generation and handling of null description. | Use a mock DB helper to verify parameters. |
| UserService.cs | 18‑36 | `GetUserById` needs tests for valid ID, invalid ID, non‑existent user, and request‑count increment. | Add tests covering each branch. |
| UserService.cs | 38‑50 | `UpdateUser` needs tests for successful update, SQL injection protection, and validation of email/username. | Add tests with valid/invalid inputs and ensure proper exception handling. |
| UserService.cs | 52‑66 | `DeleteUser` needs tests for successful deletion and handling of invalid IDs. | Add tests for normal and error paths. |
| UserService.cs | 68‑83 | `GetUsersPage` needs pagination tests (first page, middle page, pageSize limits, negative page). | Add tests verifying correct `skip` calculation and max page size enforcement. |
| UserService.cs | 85‑93 | `GetAuditReport` should be tested for correct aggregation and handling of large logs. | Add tests that populate `_auditLog` and verify output. |
| UserService.cs | 95‑108 | `SearchUsers` needs tests for normal search, empty result, and SQL‑injection resistance. | Add tests with normal queries and malicious input. |
| EmailService.cs | 34‑61 | `SendTransferNotification` should be tested for retry logic and proper handling of `SmtpException`. | Mock `SmtpClient` to throw on first attempts and succeed on retry. |
| EmailService.cs | 63‑78 | `SendWelcomeEmail` and `SendWelcomeEmailHtml` need tests for successful send and exception handling. | Mock `SmtpClient` and verify that exceptions are logged. |
| StringHelper.cs | 13‑18 | `IsValidEmail` needs tests for valid, invalid, overly long, and null emails. | Add unit tests covering edge cases. |
| StringHelper.cs | 20‑27 | `IsValidUsername` needs tests for length limits, allowed characters, and null. | Add tests. |
| StringHelper.cs | 31‑36 | `JoinWithSeparator` should be tested for correct joining and performance (optional). | Add tests comparing to `string.Join`. |
| StringHelper.cs | 43‑52 | `MaskAccountNumber` needs tests for various lengths (≤4, >4). | Add tests. |
| StringHelper.cs | 54‑57 | `ObfuscateAccount` needs tests for short and long strings. | Add tests. |
| StringHelper.cs | 59‑63 | `ToTitleCase` needs tests for culture‑specific strings and null/empty input. | Add tests. |
| Overall | – | Configuration loading (e.g., missing JWT secret) should be validated at startup. | Add integration tests that start the host with missing config and assert graceful failure. |
| Overall | – | CORS policy should be verified that only allowed origins are accepted. | Add integration test using TestServer. |
| Overall | – | Authorization attributes on controllers should be verified (e.g., `[Authorize]` on protected endpoints). | Add tests that unauthenticated requests receive 401. |

*All listed methods and scenarios should be covered by unit or integration tests to ensure correctness, security, and resilience.*