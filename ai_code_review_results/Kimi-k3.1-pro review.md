## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---:|---|---|
| Data/DatabaseHelper.cs | 15–16 | The fallback connection string contains a hardcoded `sa` password and silently uses it when configuration is missing. | Remove the fallback, fail fast on missing configuration, and obtain credentials from a secret store or managed identity. |
| appsettings.json | 2–4 | A production-looking database login and password are committed to source control. | Rotate the credentials immediately and replace them with environment-specific secrets or managed identity. |
| appsettings.json | 3 | `TrustServerCertificate=True` disables proper database server certificate validation. | Require encryption and set `TrustServerCertificate=False` with a correctly trusted certificate. |
| appsettings.json | 5–8 | The JWT signing secret is the short, committed value `mysecretkey`. | Rotate it and use a cryptographically random secret of at least 256 bits from a secret provider. |
| appsettings.json | 10–15 | The SMTP username and password are committed to source control. | Rotate the SMTP password and inject credentials through environment-specific secret storage. |
| Services/AuthService.cs | 17 | `AdminBypassPassword` embeds a reusable administrative password in source code. | Remove the constant and rotate any matching real credential. |
| Services/AuthService.cs | 53–56 | The hardcoded `admin` bypass creates a `SuperAdmin` identity without normal database authentication. | Remove the backdoor and authenticate every principal through the same strong credential-verification path. |
| Services/AuthService.cs | 32 | `Login` interpolates `username` directly into SQL, allowing authentication bypass and other SQL injection. | Use a parameterized `SqlCommand` for both username and password hash. |
| Services/AuthService.cs | 30, 61–65 | Passwords are hashed with fast, unsalted MD5, making stored hashes inexpensive to crack. | Migrate to a salted, per-user password hash such as Argon2id, bcrypt, scrypt, or PBKDF2 with verification and rehash support. |
| Services/AuthService.cs | 91–96 | `HashPasswordSha1` retains another weak password-hashing implementation, although it is currently unused. | Delete it and use one audited password-hashing implementation. |
| Program.cs | 24 | `ValidateLifetime = false` allows expired JWTs to remain valid indefinitely. | Enable lifetime validation and use a small, deliberate clock-skew allowance. |
| Services/AuthService.cs | 84 | Access tokens last 30 days, which greatly increases the impact of token theft. | Use short-lived access tokens and a secure refresh-token or reauthentication flow. |
| Services/AuthService.cs | 98–107 | `ValidateToken` accepts every nonempty token, and its unreachable code would check only expiry without validating the signature. | Remove it or replace it with `JwtSecurityTokenHandler.ValidateToken` using the complete validation parameters. |
| Data/DatabaseHelper.cs | 26–33 | `ExecuteQuery` inserts raw `tableName` and `whereClause` fragments into SQL. | Remove raw fragments and use fixed SQL with parameters and an allowlist for any genuinely dynamic identifiers. |
| Services/UserService.cs | 95–100 | `SearchUsers` places the user-controlled LIKE value into `ExecuteQuery`, permitting SQL injection. | Use a parameterized LIKE query and escape LIKE wildcard characters when literal matching is intended. |
| Services/UserService.cs | 47–48 | `UpdateUser` interpolates `email` and `username` into an UPDATE statement, permitting SQL injection. | Parameterize both values and the user ID. |
| Services/UserService.cs | 61–62 | `DeleteUser` bypasses parameterization in a DELETE statement; `id` is currently an integer, so this is fragile raw SQL rather than direct string injection. | Parameterize the ID and use the same safe command API as other queries. |
| Data/DatabaseHelper.cs | 50–56 | `ExecuteNonQuery` accepts only raw SQL and provides no parameter overload, encouraging unsafe callers. | Replace it with a parameterized command API and remove the raw-SQL entry point. |
| Services/TransactionService.cs | 47 | The sender balance UPDATE interpolates values into SQL; the typed values prevent straightforward string injection today, but the statement is culture-sensitive and unsafe to extend. | Use typed SQL parameters for the balance and user ID. |
| Services/TransactionService.cs | 48 | The recipient balance UPDATE repeats the unparameterized, culture-sensitive SQL pattern. | Use typed SQL parameters for the balance and user ID. |
| Services/TransactionService.cs | 70–71 | `Deposit` interpolates the credit amount and user ID into SQL instead of using parameters. | Parameterize the statement and use invariant typed values rather than decimal string formatting. |
| Services/TransactionService.cs | 87–91 | `RecordTransaction` interpolates the user-controlled `description` into an INSERT statement, permitting SQL injection and statement batching. | Parameterize every column, including description, type, status, amounts, and IDs. |
| Controllers/UserController.cs | 21–29 | `GetUser` lets any authenticated user retrieve any other user's profile, role, and balance by changing `id`. | Require the matching user ID or an explicit administrative authorization policy and return a limited DTO. |
| Controllers/UserController.cs | 31–36 | `GetUsers` exposes the complete paginated user directory to every authenticated user. | Restrict it to an administrative policy and return only necessary fields. |
| Controllers/UserController.cs | 38–54 | `UpdateUser` has no ownership or administrator check, so any authenticated user can modify any account. | Authorize the target ID before updating and audit the actor and change. |
| Controllers/UserController.cs | 56–69 | `DeleteUser` has no ownership or administrator check, allowing arbitrary account deletion. | Restrict deletion to an explicit administrative policy and validate the target before executing it. |
| Controllers/UserController.cs | 71–76 | `SearchUsers` permits unrestricted user enumeration by any authenticated caller. | Require an administrative policy, validate the query, and paginate results. |
| Controllers/UserController.cs | 78–82 | `GetAuditLog` exposes audit entries containing user IDs and email addresses to every authenticated user. | Restrict audit access to authorized auditors and minimize or redact personal data. |
| Controllers/TransactionController.cs | 48–59 | `Refund` accepts any transaction ID without an ownership or administrator check, creating an IDOR as soon as refunds are implemented. | Require an administrative policy or verify that the caller owns the transaction before refunding it. |
| Program.cs | 34 | The developer exception page is enabled unconditionally and can disclose stack traces, SQL, and configuration details. | Enable it only in development and use a sanitized production exception handler. |
| Program.cs | 36 | HTTPS redirection is commented out, allowing credentials, tokens, and banking data to travel over HTTP. | Enable HTTPS redirection and production HSTS with correctly configured HTTPS endpoints. |
| Program.cs | 38 | CORS allows every origin, method, and header. | Allow only trusted origins and the specific methods and headers required by the application. |
| Services/EmailService.cs | 29 | SMTP SSL is disabled while credentials and financial notifications are sent. | Require secure SMTP transport and validate the mail server certificate. |
| SampleBankingApp.csproj | 8–9 | Full debug symbols are emitted unconditionally, including Release builds, increasing disclosure if PDB files are published. | Make symbol generation configuration-specific and avoid deploying full PDBs publicly. |
| appsettings.json | 23 | `AllowedHosts` is `*`, disabling meaningful host filtering. | Configure the expected public host names. |
| Models/User.cs | 7 | `User` contains `Password` and is returned directly by user endpoints, creating a future hash-disclosure risk if mapping changes. | Separate persistence entities from response DTOs and never include password material in API models. |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---:|---|---|
| Services/TransactionService.cs | 25–26 | `Transfer` rejects only negative amounts, so zero-value transfers create transaction records and send notifications. | Change the guard to reject `amount <= 0`. |
| Services/TransactionService.cs | 23–48 | `Transfer` does not reject self-transfers, and the second absolute balance update overwrites the first so the account ends with its original balance plus the transfer amount. | Reject `fromUserId == toUserId` before reading or writing balances. |
| Services/TransactionService.cs | 39–44 | The balance check compares `fromBalance` with `amount` but deducts `amount + fee`, allowing a negative balance. | Require `fromBalance >= totalDebit` and enforce that condition in an atomic database update. |
| Services/TransactionService.cs | 36–37 | Missing sender or recipient accounts are not converted into validation failures before their first rows are consumed. | Check both result counts and return a controlled “account not found” result. |
| Services/TransactionService.cs | 28–37 | `Transfer` reads accounts without checking `IsActive`, allowing transfers involving deactivated accounts. | Validate that both accounts exist and are eligible to transact. |
| Services/TransactionService.cs | 23–61, 77–85 | The daily transaction limit is never enforced because `IsWithinDailyLimit` is never called. | Enforce the limit inside the same transaction as the transfer or remove the misleading limit. |
| Services/TransactionService.cs | 28–48 | Balance checks and absolute balance updates are not atomic, so concurrent transfers can both pass and cause lost updates or unbacked credits. | Use a database transaction with appropriate locking or atomic conditional updates and retry serialization conflicts. |
| Services/TransactionService.cs | 50, 87–91 | The transaction record stores only `amount`, omitting the fee and total debit needed to reconcile balances. | Persist the fee and total debit in a durable transaction ledger. |
| Services/TransactionService.cs | 63–74 | `Deposit` is a self-service balance credit with no external payment confirmation, allowing any authenticated user to create funds. | Credit funds only from a verified payment or privileged administrative operation. |
| Services/TransactionService.cs | 68 | `Deposit` adds an undocumented 5% bonus, over-crediting by four percentage points if the intended rate is 1%. | Confirm the business rule and use the specified named rate, such as `0.01m` for 1%. |
| Services/TransactionService.cs | 70–74 | `Deposit` ignores the balance UPDATE row count and can record or report success for a nonexistent user when no foreign key stops the insert. | Verify the account exists and require exactly one updated row before recording the deposit. |
| Services/TransactionService.cs | 68–73 | The balance credit includes `interestBonus`, but the transaction record stores only the original amount. | Record the bonus and total credit explicitly so the ledger matches the balance change. |
| Services/UserService.cs | 72 | `GetUsersPage` calculates `skip` as `page * pageSize`, so page 1 skips the first page. | Validate one-based pages and calculate `(page - 1) * pageSize`. |
| Services/UserService.cs | 70–76 | `GetUsersPage` accepts zero or negative pages and page sizes, and large values can also overflow the skip calculation. | Require `page >= 1`, constrain `pageSize` to 1–50, and use checked arithmetic. |
| Services/UserService.cs | 47–49 | `UpdateUser` returns `true` even when no user matches the ID. | Check the affected-row count and return a not-found result when it is zero. |
| Services/UserService.cs | 61–65 | `DeleteUser` returns `true` and writes an audit entry even when no user was deleted. | Check the affected-row count before reporting success or writing a successful-deletion audit entry. |
| Services/UserService.cs | 38–49 | `UpdateUser` accepts empty, malformed, or overlong email addresses and usernames despite validation helpers existing. | Apply shared validation rules before persistence and return field-specific validation errors. |
| Services/UserService.cs | 95–103 | A missing or empty search query becomes `LIKE '%%'`, and the unpaged query can return every user. | Require a nonempty bounded query and paginate the results. |
| Helpers/StringHelper.cs | 31–35 | `JoinWithSeparator` appends a separator after the final item, producing output such as `a,b,`. | Replace the loop with `string.Join`. |
| Helpers/StringHelper.cs | 54–56 | `ObfuscateAccount` throws for non-null strings shorter than four characters instead of returning a masked value. | Add the same length guard as `MaskAccountNumber` or consolidate both methods into one safe implementation. |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---:|---|---|
| Services/UserService.cs | 97–108 | `SearchUsers` catches every exception and returns an empty list, making database failures indistinguishable from no matches. | Log the failure and propagate it or return an explicit error result. |
| Services/EmailService.cs | 71–78 | `SendWelcomeEmail` catches every exception, writes to the console, and hides delivery failure from its caller. | Use structured logging and return a failure result or delegate delivery to a durable queue. |
| Services/TransactionService.cs | 47–50 | `Transfer` performs two balance updates and a transaction insert without a shared database transaction. | Execute all three writes on one connection and transaction, rolling back every write on failure. |
| Services/TransactionService.cs | 70–73 | `Deposit` updates the balance and inserts its transaction record without atomicity. | Wrap both writes in one database transaction and commit only after both succeed. |
| Services/TransactionService.cs | 47–57 | `Transfer` sends email after financial writes, so an SMTP failure can produce an HTTP error after money has already moved and encourage a duplicate retry. | Record an outbox message in the same transaction and send notifications asynchronously after commit. |
| Controllers/UserController.cs | 50–53 | `UpdateUser` returns raw `ex.Message` to HTTP clients, potentially exposing SQL and server internals. | Log the exception server-side and return a generic production `ProblemDetails` response. |
| Controllers/AuthController.cs | 19–31 | `Login` has no rate limiting, throttling, or account lockout, enabling password spraying and brute force. | Add per-account and per-IP throttling, backoff, monitoring, and a carefully designed lockout policy. |
| Controllers/UserController.cs | 21–29 | `GetUser` does not handle the service's `ArgumentException`, so an invalid route ID becomes a server error rather than a client error. | Validate the ID in the action or map validation exceptions to HTTP 400. |
| Controllers/UserController.cs | 56–68 | `DeleteUser` converts invalid-ID `ArgumentException` instances into HTTP 500 through its broad catch. | Handle validation separately as HTTP 400 and reserve HTTP 500 for unexpected failures. |
| Services/EmailService.cs | 45–59 | `SendTransferNotification` retries immediately without backoff, and an ambiguous SMTP failure can cause duplicate notifications. | Use bounded exponential backoff with jitter and an idempotent queued delivery mechanism. |
| Program.cs | 32–42 | No production exception-handling middleware is configured, so unexpected failures lack a consistent safe response. | Add environment-aware `UseExceptionHandler` middleware and standardized `ProblemDetails`. |
| Controllers/TransactionController.cs | 48–59 | `Refund` exposes an unimplemented operation and reports `NotImplementedException` as a generic HTTP 500. | Disable the endpoint until implemented or return HTTP 501 with a documented contract. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---:|---|---|
| Data/DatabaseHelper.cs | 19–24 | `GetOpenConnection` does not dispose the connection if `Open` throws. | Dispose the connection on the open-failure path and document ownership of successfully returned connections. |
| Data/DatabaseHelper.cs | 28–33 | `ExecuteQuery` never closes or disposes its connection on success or failure. | Create the connection in a `using` declaration. |
| Data/DatabaseHelper.cs | 29 | `ExecuteQuery` never disposes its `SqlCommand`. | Create the command in a `using` declaration. |
| Data/DatabaseHelper.cs | 30–32 | `ExecuteQuery` never disposes its `SqlDataAdapter`. | Create the adapter in a `using` declaration. |
| Data/DatabaseHelper.cs | 52–55 | `ExecuteNonQuery` skips `Close` when command execution throws and never explicitly disposes the connection. | Use `using` for the connection so every exception path releases it. |
| Data/DatabaseHelper.cs | 53 | `ExecuteNonQuery` never disposes its `SqlCommand`. | Create the command in a `using` declaration. |
| Data/DatabaseHelper.cs | 44–46 | `ExecuteQuerySafe` disposes its connection and command but not its adapter. | Dispose the adapter with `using`. |
| Data/DatabaseHelper.cs | 74–76 | `ExecuteQueryWithParams` leaves its adapter undisposed. | Dispose the adapter with `using`, or remove the obsolete method. |
| Services/AuthService.cs | 34–58 | `Login` never disposes its `SqlConnection`, including both successful and backdoor return paths. | Use a `using` declaration for the connection. |
| Services/AuthService.cs | 37 | `Login` never disposes its `SqlCommand`. | Use a `using` declaration for the command. |
| Services/AuthService.cs | 38–58 | `Login` never disposes its `SqlDataReader`, and the early user return leaves it open. | Use a `using` declaration and complete mapping before returning. |
| Services/EmailService.cs | 16, 22–31 | A single `SmtpClient` is retained as an instance field, never disposed, and shared through a service even though the client is not thread-safe. | Create and dispose a client per send operation or replace it with a supported mail library and managed delivery service. |
| Services/EmailService.cs | 39–60 | `SendTransferNotification` never disposes its `MailMessage`, including retry and exception paths. | Create the message in a `using` declaration. |
| Services/EmailService.cs | 69–78 | `SendWelcomeEmail` never disposes its `MailMessage`. | Create the message in a `using` declaration. |
| Services/EmailService.cs | 89–91 | `SendWelcomeEmailHtml` never disposes its `MailMessage`. | Create the message in a `using` declaration. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---:|---|---|
| Program.cs | 16, 28 | `jwtSecret!` suppresses nullable analysis but does not prevent `Encoding.UTF8.GetBytes` from receiving null. | Validate JWT options at startup and throw a clear configuration exception when the secret is absent. |
| Services/AuthService.cs | 70 | `GenerateJwtToken` repeats the same null-forgiving JWT secret access and can fail at runtime. | Inject validated JWT options containing a guaranteed non-null key. |
| Services/AuthService.cs | 34 | `Login` passes a potentially null connection string directly to `SqlConnection`. | Resolve and validate the connection string during startup. |
| Controllers/AuthController.cs | 20–22 | `Login` assumes a valid request, and JSON `null` can bypass the password property initializer before hashing. | Add request and field validation, reject null or empty credentials, and return HTTP 400. |
| Controllers/TransactionController.cs | 26–29 | `Transfer` passes a possibly missing or nonnumeric name-identifier claim to `int.Parse`. | Use `int.TryParse` and reject an absent or invalid principal claim without throwing. |
| Controllers/TransactionController.cs | 40–43 | `Deposit` repeats the unsafe claim parsing pattern. | Use the same guarded claim-extraction helper as `Transfer`. |
| Controllers/TransactionController.cs | 24–29 | `Transfer` dereferences the model-bound request and uses its fields without explicit request validation. | Add null guards and validation attributes for recipient, amount, and description. |
| Controllers/TransactionController.cs | 38–43 | `Deposit` assumes the model-bound request is non-null and valid. | Add request validation and return HTTP 400 for malformed input. |
| Controllers/UserController.cs | 39–43 | `UpdateUser` dereferences the request without an explicit null or field validation guard. | Validate the request, email, and username before invoking the service. |
| Services/TransactionService.cs | 36 | `Transfer` accesses `fromUserTable.Rows[0]` without checking that the sender exists. | Check `Rows.Count` and return a controlled sender-not-found result. |
| Services/TransactionService.cs | 37 | `Transfer` accesses `toUserTable.Rows[0]` without checking that the recipient exists. | Check `Rows.Count` and return a controlled recipient-not-found result. |
| Services/TransactionService.cs | 52–55 | Direct email and username casts can fail on `DBNull` after the financial writes have already completed. | Validate required account fields before any write and use null-safe typed accessors. |
| Helpers/StringHelper.cs | 11–16 | `IsValidEmail` reads `email.Length` before checking for null. | Return false for null or whitespace input before reading its length. |
| Helpers/StringHelper.cs | 20–25 | `IsValidUsername` reads `username.Length` before checking for null. | Return false for null or whitespace input before reading its length. |
| Helpers/StringHelper.cs | 43–50 | `MaskAccountNumber` dereferences `accountNumber` without a null guard. | Validate the argument or define an explicit null-input result. |
| Helpers/StringHelper.cs | 54–56 | `ObfuscateAccount` dereferences null input and also throws on strings shorter than four characters. | Delegate to one null-safe, length-safe masking method. |
| Services/EmailService.cs | 63–69 | `SendWelcomeEmail` calls `username.ToUpper()` before any null check. | Validate `username` and `toEmail` before constructing the message. |
| Services/EmailService.cs | 22–24 | The SMTP host can be null and a present but malformed port value causes `int.Parse` to throw during service construction. | Bind validated email options with a required host and a parsed port range. |
| Services/UserService.cs | 111–122 | `MapRowToUser` directly casts every database value, so nullable columns or schema drift produce unhandled cast exceptions. | Enforce a non-null schema and use explicit null-safe column conversion with clear data errors. |
| Services/AuthService.cs | 44–49 | `Login` directly casts reader values and will fail on unexpected `DBNull` values. | Select required columns explicitly and use null-safe typed accessors. |

## 6. Dead Code

The caller scan covered all 54 explicit constructors, controller actions, and helper methods, with dependency-injection constructors and framework-routed actions treated as application entry points.

| File | Line | Issue | Fix |
|---|---:|---|---|
| Data/DatabaseHelper.cs | 59–65 | `TableExists` has no caller in any supplied source file. | Remove it or add a tested caller if schema inspection is genuinely required. |
| Data/DatabaseHelper.cs | 67–78 | `ExecuteQueryWithParams` has no caller and remains present despite being marked `[Obsolete]`. | Remove the obsolete implementation after confirming no external consumers. |
| Helpers/StringHelper.cs | 11–18 | `IsValidEmail` has no caller in the supplied source. | Wire it into shared user validation or remove it. |
| Helpers/StringHelper.cs | 20–27 | `IsValidUsername` has no caller in the supplied source. | Wire it into shared user validation or remove it. |
| Helpers/StringHelper.cs | 29–36 | `JoinWithSeparator` has no caller and is the broken duplicate implementation. | Delete it in favor of `string.Join`. |
| Helpers/StringHelper.cs | 38–41 | `JoinWithSeparatorFixed` also has no caller, so the fixed duplicate is unused as well. | Remove it or make it the single used implementation. |
| Helpers/StringHelper.cs | 43–52 | `MaskAccountNumber` has no caller in the supplied source. | Remove it or use it wherever account numbers are displayed. |
| Helpers/StringHelper.cs | 54–57 | `ObfuscateAccount` has no caller in the supplied source. | Remove it and retain one safe masking implementation if needed. |
| Helpers/StringHelper.cs | 59–63 | `ToTitleCase` has no caller in the supplied source. | Remove it or add a demonstrated use and tests. |
| Helpers/StringHelper.cs | 65–71 | `IsBlank` has no caller in the supplied source. | Remove it and use `string.IsNullOrWhiteSpace` at call sites. |
| Services/AuthService.cs | 91–96 | `HashPasswordSha1` has no caller. | Delete the weak unused implementation. |
| Services/AuthService.cs | 98–108 | `ValidateToken` has no caller. | Remove it or implement real validation and integrate it with a tested authentication flow. |
| Services/EmailService.cs | 63–79 | `SendWelcomeEmail` has no caller. | Remove it or invoke it from a real registration workflow. |
| Services/EmailService.cs | 86–92 | `SendWelcomeEmailHtml` has no caller. | Remove it or integrate it into the registration workflow. |
| Services/EmailService.cs | 81–84 | `BuildHtmlTemplate` is called only by the unused `SendWelcomeEmailHtml`, making the entire HTML path transitively unreachable. | Remove the path together with its unused caller or integrate and test it. |
| Services/TransactionService.cs | 77–85 | `IsWithinDailyLimit` has no caller, and `MaxTransactionsPerDay` consequently provides no enforcement. | Invoke it as part of atomic transfer validation or remove the unused limit code. |
| Services/TransactionService.cs | 94–97 | `FormatCurrency` has no caller. | Remove it or use one shared currency formatter where needed. |
| Services/AuthService.cs | 103–107 | The token-reading code after unconditional `return true` is unreachable. | Remove the unreachable code and implement actual validation if the method is retained. |
| Services/TransactionService.cs | 99–103 | `RefundTransaction` is non-stub application code that consists only of `NotImplementedException`. | Implement it atomically or remove the service and endpoint until the feature exists. |
| Services/AuthService.cs | 14, 19–22 | `_db` is injected and assigned but never used because `Login` creates its own connection. | Remove the dependency or route data access through it safely. |
| Controllers/TransactionController.cs | 15, 17–20 | `_logger` is injected and assigned but never used. | Remove it or use it for structured, non-sensitive operational logging. |
| Services/UserService.cs | 11, 25, 59 | `_requestCount` is incremented but never read. | Remove it or expose a meaningful metric using atomic increments. |
| Models/Transaction.cs | 3–13 | The `Transaction` model is never referenced because transaction persistence uses raw SQL instead. | Remove it or use it in a typed transaction repository and ledger mapping. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---:|---|---|
| Program.cs | 16 | The raw `Jwt:SecretKey` configuration key is repeated in `AuthService`. | Bind a validated `JwtOptions` object instead of repeating configuration keys. |
| Services/AuthService.cs | 70 | `GenerateJwtToken` repeats the raw `Jwt:SecretKey` key used in `Program`. | Inject the bound JWT options. |
| Program.cs | 26 | The raw `Jwt:Issuer` key is repeated during token creation. | Include the issuer in the shared bound JWT options. |
| Services/AuthService.cs | 81 | `GenerateJwtToken` repeats the raw `Jwt:Issuer` key. | Read the issuer from injected JWT options. |
| Program.cs | 27 | The raw `Jwt:Audience` key is repeated during token creation. | Include the audience in the shared bound JWT options. |
| Services/AuthService.cs | 82 | `GenerateJwtToken` repeats the raw `Jwt:Audience` key. | Read the audience from injected JWT options. |
| Data/DatabaseHelper.cs | 15 | `DefaultConnection` is duplicated as a raw configuration key in `AuthService`. | Use one shared connection-options binding or named constant. |
| Services/AuthService.cs | 34 | `Login` repeats the raw `DefaultConnection` key instead of sharing database configuration. | Inject the same validated database options used by `DatabaseHelper`. |
| Data/DatabaseHelper.cs | 16 | An entire fallback connection string is embedded in source rather than configuration. | Remove the fallback and require explicit configuration. |
| Services/AuthService.cs | 53 | The literal username `admin` is embedded in authentication logic. | Remove the bypass rather than converting the username into another constant. |
| Services/AuthService.cs | 55 | The synthetic backdoor identity repeats the inline `admin` username. | Remove the synthetic identity. |
| Services/AuthService.cs | 55 | `SuperAdmin` is introduced as an inline role outside any shared authorization policy. | Remove the backdoor and define legitimate roles in centralized authorization policies. |
| Services/AuthService.cs | 84 | The 30-day token lifetime is an inline numeric policy value. | Move a much shorter lifetime to validated JWT configuration. |
| Helpers/StringHelper.cs | 13 | The email length limit `254` is an unnamed inline literal. | Introduce a named validation constant shared with request validation. |
| Helpers/StringHelper.cs | 22 | Username limits `3` and `20` are embedded directly in the validation method. | Define shared named limits and reuse them in model validation. |
| Helpers/StringHelper.cs | 45, 49–50 | The visible account suffix length `4` is repeated throughout `MaskAccountNumber`. | Define one named `VisibleAccountDigits` constant. |
| Helpers/StringHelper.cs | 56 | `ObfuscateAccount` separately hardcodes `****` and another suffix length of four. | Consolidate masking around one named suffix-length policy. |
| Services/TransactionService.cs | 65 | The deposit cap `1000000` is an inline financial limit. | Move it to a named, validated transaction-limit setting. |
| Services/TransactionService.cs | 68 | The bonus rate `0.05m` and redundant multiplier `1` are embedded in the calculation. | Use a named configured rate and remove the redundant multiplier. |
| Services/TransactionService.cs | 50 | The transaction type `Transfer` is an inline string. | Use a transaction-type enum with explicit database mapping. |
| Services/TransactionService.cs | 73 | The transaction type `Deposit` is an inline string. | Use the same transaction-type enum as transfers. |
| Services/TransactionService.cs | 73 | Sender ID `0` is an undocumented magic system-account identifier. | Use a nullable sender or an explicitly defined system-account identifier. |
| Services/TransactionService.cs | 90 | Transaction status `Completed` is an inline string. | Use a transaction-status enum with constrained persistence values. |
| Services/UserService.cs | 22 | `GetUserById` uses an unexplained maximum user ID of `1000000`. | Remove the arbitrary cap or define a documented shared identifier rule. |
| Services/UserService.cs | 42 | `UpdateUser` repeats the inline maximum user ID of `1000000`. | Centralize the identifier validation rule. |
| Services/UserService.cs | 56 | `DeleteUser` repeats the inline maximum user ID of `1000000`. | Centralize the identifier validation rule. |
| Services/UserService.cs | 70 | The maximum page size `50` is embedded in the service. | Use a named pagination constant or validated pagination options. |
| Controllers/UserController.cs | 32 | Pagination defaults `1` and `20` are embedded in the action signature. | Define shared pagination defaults and keep them consistent with service limits. |
| Services/EmailService.cs | 24 | SMTP port fallback `25` is an inline string that also commonly implies unsecured delivery. | Use a validated integer email option with a secure default. |
| Services/EmailService.cs | 40 | `notifications@company.com` is hardcoded as the transfer sender. | Use a configured, verified sender address. |
| Services/EmailService.cs | 69 | `SendWelcomeEmail` repeats the hardcoded notification sender. | Read the sender from shared email options. |
| Services/EmailService.cs | 89 | `SendWelcomeEmailHtml` repeats the hardcoded notification sender. | Read the sender from shared email options. |
| Services/EmailService.cs | 67 | `support@company.com` is embedded in an email body. | Move the support address to configuration or a template settings object. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---:|---|---|
| Helpers/StringHelper.cs | 29–36 | `JoinWithSeparator` performs string concatenation in a loop, causing repeated allocations and quadratic behavior for large inputs. | Replace the entire loop with `string.Join`. |
| Services/UserService.cs | 85–93 | `GetAuditReport` concatenates strings in a loop, causing quadratic allocation behavior as the audit log grows. | Use `string.Join` or `StringBuilder`, and preferably page a persistent audit query. |
| Helpers/StringHelper.cs | 16 | `IsValidEmail` constructs a new `Regex` on every call. | Use a static readonly or generated regex with an appropriate match timeout. |
| Helpers/StringHelper.cs | 25 | `IsValidUsername` constructs a new `Regex` on every call. | Use a static readonly or generated regex with an appropriate match timeout. |
| Services/UserService.cs | 10, 45, 64 | `_auditLog` is a shared mutable static `List` accessed by multiple scoped service instances without synchronization, and it grows without bound. | Replace it with a durable audit store or, at minimum, synchronized bounded access. |
| Services/UserService.cs | 85–92 | `GetAuditReport` enumerates `_auditLog` while other requests may modify it, which can throw or produce inconsistent output. | Query a durable store or enumerate a synchronized snapshot. |
| Services/UserService.cs | 25 | `GetUserById` increments static `_requestCount` with a non-atomic operation. | Remove the unused counter or use `Interlocked.Increment`. |
| Services/UserService.cs | 59 | `DeleteUser` repeats the non-atomic static counter increment. | Remove the unused counter or use `Interlocked.Increment`. |
| Helpers/StringHelper.cs | 65–71 | `IsBlank` manually reimplements `string.IsNullOrWhiteSpace`. | Replace the method body or call sites with the framework method. |
| Data/DatabaseHelper.cs | 19–24 | `GetOpenConnection` transfers ownership of an open connection to callers without documenting that contract, and both callers handle it incorrectly. | Prefer self-contained `using`-based query methods or explicitly document and enforce caller ownership. |
| Services/UserService.cs | 20–23 | `GetUserById` contains the first copy of the two-part user-ID validation block. | Extract a shared `ValidateUserId` helper or use a validated value object. |
| Services/UserService.cs | 40–43 | `UpdateUser` duplicates the same user-ID validation block. | Call the shared identifier validator. |
| Services/UserService.cs | 54–57 | `DeleteUser` duplicates the same user-ID validation block. | Call the shared identifier validator. |
| Data/DatabaseHelper.cs | 41–42 | `ExecuteQuerySafe` uses `AddWithValue`, which infers SQL types and can cause implicit conversions, parameter-size problems, and poor query-plan reuse. | Add parameters with explicit `SqlDbType`, size, precision, and null handling. |
| Services/EmailService.cs | 53–57 | `SendTransferNotification` uses `Console.WriteLine` instead of structured application logging. | Inject `ILogger<EmailService>` and log sanitized delivery failures with retry metadata. |
| Services/EmailService.cs | 75–78 | `SendWelcomeEmail` also uses console output and string concatenation for exception logging. | Use structured logging and an explicit delivery-failure policy. |
| Helpers/StringHelper.cs | 29–41 | Broken and fixed separator-joining implementations coexist, and neither is called. | Delete both wrappers or retain only a tested `string.Join`-based implementation. |
| Helpers/StringHelper.cs | 43–57 | Two account-masking implementations coexist with different short-input behavior. | Retain one null-safe, length-safe masking method. |
| Controllers/TransactionController.cs | 26–27 | `Transfer` contains one copy of the claim lookup and parse logic. | Extract a guarded current-user-ID helper shared by transaction actions. |
| Controllers/TransactionController.cs | 40–41 | `Deposit` duplicates the claim lookup and parse logic. | Use the same guarded current-user-ID helper. |
| Services/TransactionService.cs | 68 | Multiplying the interest bonus by `1` is redundant and obscures the intended rate. | Remove the multiplier and name the actual rate. |
| Services/AuthService.cs | 25–28 | The `Login` documentation says it returns a JWT, but the method returns a `User` or null. | Correct the documentation to describe authentication and let `GenerateJwtToken` own token creation. |
| Services/AuthService.cs | 42–50 | `Login` hand-maps user columns while `UserService.MapRowToUser` repeats nearly the same mapping. | Move user lookup and mapping into one shared repository. |
| Services/AuthService.cs | 28–59 | `Login` combines password hashing, SQL construction and execution, user mapping, and backdoor authentication policy. | Separate password verification, user lookup and mapping, and authentication policy, while removing the backdoor. |
| Services/TransactionService.cs | 23–61 | `Transfer` combines request and account validation, fee calculation, balance persistence, ledger recording, and notification delivery. | Extract validation, fee calculation, atomic transfer persistence, and post-commit notification dispatch into named helpers. |
| Services/TransactionService.cs | 63–75 | `Deposit` combines amount validation, bonus calculation, balance mutation, and ledger recording. | Extract validation, bonus calculation, and atomic deposit persistence with ledger recording. |
| Services/EmailService.cs | 34–61 | `SendTransferNotification` combines message construction, retry policy, SMTP transport, and failure logging. | Extract a message factory, retry executor, and mail transport. |
| Services/UserService.cs | 38–50 | `UpdateUser` combines identifier validation, audit writing, SQL construction, and persistence. | Extract shared validation, an audit writer, and a parameterized user repository update. |
| Services/UserService.cs | 52–66 | `DeleteUser` combines identifier validation, persistence, request counting, and audit writing. | Extract shared validation and separate repository deletion from audit and metrics concerns. |
| Services/UserService.cs | 95–109 | `SearchUsers` combines search-query construction, data access and mapping, and an exception-suppression policy. | Separate the search specification, repository execution, and controller-level error policy. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---:|---|---|
| Program.cs | 34 | `UseDeveloperExceptionPage` is unconditional rather than environment-specific. | Call it only when `app.Environment.IsDevelopment()` and configure production exception handling. |
| Program.cs | 24 | JWT lifetime validation is explicitly disabled. | Set `ValidateLifetime = true` and test expired-token rejection. |
| Program.cs | 36 | HTTPS redirection is disabled and no production HSTS setup is present. | Restore HTTPS redirection and configure HSTS outside development. |
| Program.cs | 38 | The CORS policy is fully permissive for every environment. | Define environment-specific named policies with explicit trusted origins. |
| appsettings.json | 18 | The default log level is `Debug`, which is inappropriate as a production baseline. | Use `Information` or a stricter production level and enable debug only temporarily. |
| appsettings.json | 19 | Microsoft framework logging is set to `Debug`, potentially producing sensitive and excessive production logs. | Use an appropriate production level such as `Warning` or `Information`. |
| appsettings.json | 20 | System logging is also set to `Debug`. | Override it to a production-appropriate level. |
| SampleBankingApp.csproj | 8 | `DebugSymbols` is unconditionally true for every build configuration. | Condition symbol generation by configuration and control PDB publication. |
| SampleBankingApp.csproj | 9 | `DebugType` is unconditionally `full`, including Release builds. | Use the desired Release symbol setting and avoid deploying full debugging artifacts. |
| SampleBankingApp.csproj | 7 | `TreatWarningsAsErrors` is false, allowing nullable and obsolete-code warnings to pass unnoticed. | Enable warnings-as-errors in CI, at least for nullable and security-relevant warnings. |
| SampleBankingApp.csproj | 13 | `Microsoft.AspNetCore.Authentication.JwtBearer` is pinned to the unpatched 8.0.0 baseline. | Upgrade to a current supported servicing release and run a NuGet vulnerability audit. |
| SampleBankingApp.csproj | 14 | `System.Data.SqlClient` is the legacy SQL client and should not be the basis for new development. | Migrate to a supported `Microsoft.Data.SqlClient` release and audit the dependency. |
| SampleBankingApp.csproj | 15 | `Newtonsoft.Json` 12.0.3 is an old release with known advisories affecting older versions and is unused in the supplied source. | Remove it if unused or upgrade to a currently patched release. |
| SampleBankingApp.csproj | 16 | `System.IdentityModel.Tokens.Jwt` 7.0.0 is an old baseline that can miss later security and compatibility fixes. | Upgrade to a supported patched version aligned with the JWT bearer package. |
| Repository | N/A | No `appsettings.Production.json` or equivalent environment-specific override is supplied, so the base file applies everywhere. | Add non-secret production overrides and inject all credentials through deployment secrets. |
| appsettings.json | 2–4 | Production database credentials are stored in the shared base configuration. | Remove and rotate them, then use deployment-specific secret injection. |
| appsettings.json | 5–8 | The JWT signing secret is stored in the shared base configuration. | Remove and rotate it, then use a validated secret provider. |
| appsettings.json | 10–15 | The SMTP password is stored in the shared base configuration. | Remove and rotate it, then use deployment-specific secret injection. |
| appsettings.json | 3 | Database certificate validation is relaxed in the committed configuration. | Require encryption and normal certificate validation in production. |
| appsettings.json | 23 | Host filtering is disabled with a wildcard. | Configure explicit allowed production hosts. |
| Program.cs | 16–29 | JWT settings are read loosely without startup validation for required values, key strength, issuer, or audience. | Use options validation with `ValidateOnStart` and fail before accepting requests when settings are invalid. |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---:|---|---|
| Repository | N/A | No test project is present in the supplied source. | Add a unit-test project plus database integration tests for authentication, authorization, financial writes, and pagination. |
| Services/AuthService.cs | 28–59 | `Login` lacks tests for valid and invalid credentials, inactive users, null input, SQL-injection usernames, and removal of the administrative bypass. | Add authentication tests proving only valid active users succeed and injection or backdoor credentials never bypass normal verification. |
| Services/AuthService.cs | 61–65 | Password hashing lacks tests for salt uniqueness, verification, malformed hashes, and migration from legacy hashes. | After replacing MD5, add vectors and property tests for the new password hasher and verifier. |
| Controllers/AuthController.cs | 19–31 | The login endpoint lacks tests for malformed requests, generic failure responses, throttling, and lockout behavior. | Add controller and integration tests covering HTTP 400, HTTP 401, rate limits, and non-enumerating error messages. |
| Services/AuthService.cs | 68–89 | JWT generation and middleware validation lack tests for claims, expiry, invalid signatures, issuer, audience, and missing configuration. | Add token tests proving valid tokens succeed and expired, altered, misissued, or misconfigured tokens fail. |
| Services/AuthService.cs | 98–108 | `ValidateToken` has no tests demonstrating that arbitrary nonempty strings must be rejected. | If retained, test empty, malformed, unsigned, wrongly signed, and expired tokens against real validation. |
| Services/TransactionService.cs | 23–61 | `Transfer` lacks boundary tests for negative amounts, zero, self-transfers, and very small amounts subject to fee rounding. | Add parameterized tests proving invalid transfers make no writes and valid rounding follows the business rule. |
| Services/TransactionService.cs | 39–44 | The fee logic lacks tests for exact balance, balance equal to total debit, and balance between amount and amount plus fee. | Add tests proving no result can produce a negative balance and the fee is deducted exactly once. |
| Services/TransactionService.cs | 28–37 | Account validation lacks tests for missing sender, missing recipient, inactive accounts, and null required fields. | Add tests proving each case returns a controlled failure without modifying either balance. |
| Services/TransactionService.cs | 47–50 | Transfer persistence lacks failure-injection tests for the first update, second update, and transaction insert. | Add integration tests proving every failure rolls back all financial and ledger writes. |
| Services/TransactionService.cs | 28–48 | Concurrent transfer behavior and daily-limit enforcement are untested. | Add concurrent integration tests proving balances cannot be lost or overdrawn and the daily limit is atomic. |
| Services/TransactionService.cs | 52–57 | Notification failure after a successful transfer is untested. | Add tests proving SMTP failure does not change the committed transfer result or cause duplicate financial retries. |
| Services/TransactionService.cs | 63–75 | `Deposit` lacks tests for zero, negative values, exactly one million, values above the cap, and the intended bonus rate. | Add boundary tests asserting the exact credited amount and ledger amount for each case. |
| Services/TransactionService.cs | 70–74 | Deposit behavior for nonexistent users, unconfirmed funding, and ledger-insert failure is untested. | Add integration tests proving only verified deposits succeed and every accepted deposit is atomic. |
| Services/UserService.cs | 68–83 | `GetUsersPage` lacks tests for first-page offset, later pages, empty pages, invalid inputs, and the page-size cap. | Add tests proving page 1 skips zero rows, page 2 skips one page, and invalid values are rejected before SQL execution. |
| Controllers/UserController.cs | 38–69 | Update and delete authorization lacks tests for self-access, other-user access, anonymous access, and administrative access. | Add endpoint tests proving horizontal privilege escalation is impossible. |
| Services/UserService.cs | 38–66 | Update and delete lack tests for invalid IDs, nonexistent rows, malformed user fields, and affected-row counts. | Add tests proving invalid input is rejected and nonexistent targets return not found rather than success. |
| Services/UserService.cs | 95–109 | `SearchUsers` lacks tests for injection payloads, empty queries, wildcard handling, result limits, and database failures. | Add tests proving parameterized literal searches and ensuring database errors are not returned as empty success results. |
| Controllers/UserController.cs | 21–36, 71–82 | Read, list, search, and audit endpoints lack authorization and data-exposure tests. | Add tests proving only permitted roles or owners can access each resource and responses contain no sensitive fields. |
| Helpers/StringHelper.cs | 11–27 | Email and username validators lack null, empty, minimum-length, maximum-length, and over-limit tests. | Add boundary-focused parameterized tests before reusing the validators. |
| Helpers/StringHelper.cs | 29–57 | Joining and masking helpers lack tests for empty sequences, single items, null input, and account strings of zero through four characters. | Add tests that expose the trailing separator and short-account range failures. |
| Services/EmailService.cs | 34–61 | SMTP retry behavior lacks tests for transient failure, permanent failure, retry exhaustion, and ambiguous delivery. | Add fake-transport tests proving bounded retries, backoff, disposal, and no unintended duplicate delivery. |
| Services/TransactionService.cs | 99–103 | Refund behavior has no specification or tests beyond the current exception stub. | Define ownership, amount, status, idempotency, and atomic-reversal tests before enabling the endpoint. |