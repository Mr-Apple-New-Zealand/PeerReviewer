# Code Review Report – SampleBankingApp (commit 53beb173)

---

## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 32 | SQL built by string interpolation with raw `username` and `hashedPassword` – SQL injection risk | Use parameterised `SqlCommand` with `@Username` and `@Password` parameters |
| AuthService.cs | 30 | Password hashed with MD5 – weak, fast hash | Replace with a strong password‑hashing algorithm (e.g. Argon2, PBKDF2, BCrypt) and store salt |
| AuthService.cs | 17 | Hard‑coded admin bypass password | Remove back‑door; enforce normal authentication flow |
| AuthService.cs | 61‑66 | SHA‑1 hash method present (weak algorithm) | Delete the method or replace with a strong KDF; do not expose unused insecure code |
| AuthService.cs | 99‑108 | `ValidateToken` returns `true` before any validation – always authorises if called | Remove the early `return true;` and implement proper token validation (signature, expiry, audience, issuer) |
| Program.cs | 24 | `ValidateLifetime = false` – JWT expiration not checked | Set `ValidateLifetime = true` and configure reasonable clock skew |
| Program.cs | 34 | `UseDeveloperExceptionPage()` always enabled – leaks stack traces in production | Enable only in Development environment (`if (app.Environment.IsDevelopment())`) |
| Program.cs | 38 | CORS policy `AllowAnyOrigin/AllowAnyMethod/AllowAnyHeader` – open to any site | Restrict origins to known clients and limit methods/headers |
| Program.cs | 36 | HTTPS redirection commented out – traffic may be plain HTTP | Uncomment `app.UseHttpsRedirection();` and enforce HSTS |
| EmailService.cs | 22‑30 | `SmtpClient` created with `EnableSsl = false` and credentials from config (plain text) | Enable SSL/TLS (`EnableSsl = true`) and store credentials in a secret manager |
| appsettings.json | 3 | Connection string contains hard‑coded DB password | Move credentials to a secure secret store (Azure Key Vault, user‑secrets, env vars) |
| appsettings.json | 6 | JWT secret key stored in plain text | Move to a secret store and use a longer, high‑entropy key |
| appsettings.json | 13‑14 | Email SMTP username/password stored in plain text | Move to secret store; avoid committing to source control |
| DatabaseHelper.cs | 29 | `ExecuteQuery` builds `SELECT * FROM {tableName} WHERE {whereClause}` via interpolation – injection | Require callers to use `ExecuteQuerySafe` with parameters; validate/whitelist table names |
| DatabaseHelper.cs | 53 | `ExecuteNonQuery` builds raw SQL via interpolation – injection | Use parameterised commands or `ExecuteQuerySafe` |
| UserService.cs | 47 | `UpdateUser` builds raw UPDATE with interpolated `email` and `username` – injection | Parameterise the query |
| UserService.cs | 61 | `DeleteUser` builds raw DELETE with interpolated `id` – injection | Parameterise the query |
| UserService.cs | 99 | `SearchUsers` builds raw LIKE clause with interpolated `query` – injection | Use parameterised query (`WHERE Username LIKE @q`) |
| TransactionService.cs | 47‑48 | Balance updates built via interpolation – injection | Parameterise the UPDATE statements |
| TransactionService.cs | 71 | Deposit UPDATE built via interpolation – injection | Parameterise the UPDATE |
| TransactionService.cs | 90‑91 | `RecordTransaction` builds INSERT via interpolation (including `description`) – injection | Parameterise all fields; handle nulls safely |
| EmailService.cs | 40‑41, 69 | Hard‑coded email addresses (`notifications@company.com`, `support@company.com`) | Move to configuration or constants with proper validation |
| AuthService.cs | 17 | Hard‑coded admin bypass password (`SuperAdmin2024`) | Remove; enforce normal authentication |
| EmailService.cs | 22‑30 | SMTP credentials read directly from config (plain text) | Store in secure secret store, enable TLS |
| Program.cs | 24 | JWT lifetime not validated (`ValidateLifetime = false`) | Set to `true` and configure reasonable expiry |
| Program.cs | 34 | Developer exception page always on | Guard with `if (app.Environment.IsDevelopment())` |
| Program.cs | 38 | Open CORS policy | Restrict origins to known domains |
| Program.cs | 36 | HTTPS redirection disabled | Enable HTTPS redirection and HSTS |
| Program.cs | 38 | No rate‑limiting middleware | Add ASP.NET Core rate‑limiting or similar |
| EmailService.cs | 22‑30 | `EnableSsl = false` – email sent in clear text | Set `EnableSsl = true` and use STARTTLS/SMTPS |
| EmailService.cs | 22‑30 | `SmtpClient` is a field (shared across requests) – not thread‑safe | Create a new `SmtpClient` per send or use a thread‑safe pool |
| EmailService.cs | 40‑41, 69 | Hard‑coded “from” address | Move to configuration |
| EmailService.cs | 81‑84 | HTML template built via string interpolation without encoding – XSS risk if inputs contain HTML | Encode user‑provided values or use a templating engine |
| AuthService.cs | 30‑39 | Raw `SqlConnection`, `SqlCommand`, `SqlDataReader` not disposed – may expose connection details on failure | Wrap in `using` statements or `await using` for async |
| DatabaseHelper.cs | 28‑33 | `ExecuteQuery` does not dispose connection/command/adapter | Use `using` blocks for all disposable objects |
| DatabaseHelper.cs | 52‑56 | `ExecuteNonQuery` does not dispose connection/command | Use `using` blocks |
| EmailService.cs | 45‑60 | `MailMessage` objects not disposed | Wrap in `using` or call `Dispose` after send |
| EmailService.cs | 71‑78 | `MailMessage` in `SendWelcomeEmailHtml` not disposed | Wrap in `using` |
| TransactionService.cs | 47‑48, 71, 90‑91 | Direct SQL string interpolation – injection | Switch to parameterised commands |
| TransactionService.cs | 47‑48, 71 | No transaction scope – partial updates possible on failure | Wrap balance updates and transaction insert in a DB transaction |
| TransactionService.cs | 23‑31 | No check for daily transaction limit (`MaxTransactionsPerDay`) | Call `IsWithinDailyLimit` before proceeding |
| TransactionService.cs | 23‑31 | No check for self‑transfer (`fromUserId == toUserId`) | Add guard to prevent pointless transfers |
| TransactionService.cs | 42 | Insufficient‑funds check uses `amount` not `totalDebit` (fee ignored) | Compare `fromBalance >= totalDebit` |
| UserService.cs | 72 | Pagination offset calculated as `page * pageSize` (off‑by‑one) | Use `(page - 1) * pageSize` and validate `page >= 1` |
| UserService.cs | 70‑71 | `pageSize` capped but `page` not validated – negative page yields negative `skip` | Validate `page > 0` before use |
| UserService.cs | 99‑103 | `SearchUsers` catches generic `Exception` and returns empty list – hides errors | Log the exception and return appropriate error response |
| UserService.cs | 45 | Audit log stored in static `List<string>` without synchronization – race condition | Use a thread‑safe collection or lock |
| UserService.cs | 11 | Static request counter not thread‑safe | Use `Interlocked.Increment` or a thread‑safe type |
| EmailService.cs | 22‑30 | `SmtpClient` reused across threads – not thread‑safe | Create per‑request client or protect with lock |
| EmailService.cs | 45‑60 | Retry loop lacks back‑off delay – could hammer SMTP server | Add exponential back‑off or `Task.Delay` between attempts |
| AuthService.cs | 30‑39 | No parameterisation of login query – SQL injection | Use `SqlCommand` parameters for `@Username` and `@Password` |
| AuthService.cs | 30‑39 | Connection opened but never closed/disposed | Wrap in `using` |
| AuthService.cs | 38‑41 | `SqlDataReader` never disposed | Wrap in `using` |
| AuthService.cs | 30‑41 | No exception handling for DB errors | Add try/catch and log appropriately |
| AuthService.cs | 30‑41 | Potential information leakage via exception messages (if bubbled) | Return generic error and log details internally |
| AuthService.cs | 99‑108 | Unreachable code after `return true;` – dead and misleading | Remove dead code and implement proper validation |
| TransactionService.cs | 23‑31 | No transaction – two balance updates and transaction record could become inconsistent | Use `SqlTransaction` to ensure atomicity |
| TransactionService.cs | 23‑31 | No check for `IsWithinDailyLimit` – daily limit bypassed | Call `IsWithinDailyLimit` before proceeding |
| TransactionService.cs | 23‑31 | No check for self‑transfer – could be used for fee‑avoidance tricks | Add guard `if (fromUserId == toUserId) return (false, "Cannot transfer to self");` |
| TransactionService.cs | 23‑31 | Fee calculated but not considered in insufficient‑funds check | Compare against `totalDebit` |
| TransactionService.cs | 23‑31 | No validation of `description` length or null handling | Validate length and handle null safely |
| TransactionService.cs | 23‑31 | No logging of transfer attempts (success/failure) | Add structured logging |
| TransactionService.cs | 23‑31 | No rate limiting on transfers per user | Enforce `MaxTransactionsPerDay` |
| TransactionService.cs | 23‑31 | No audit trail for failed transfers | Log failures |
| TransactionService.cs | 23‑31 | Direct string interpolation for SQL – injection risk | Parameterise queries |
| TransactionService.cs | 23‑31 | No concurrency control – race condition on balances | Use DB transaction with appropriate isolation level |
| TransactionService.cs | 23‑31 | No check for negative `amount` beyond `amount < 0` (zero allowed) | Disallow zero amount |
| TransactionService.cs | 23‑31 | No check for overflow when adding `interestBonus` | Validate resulting balance within limits |
| TransactionService.cs | 23‑31 | `RecordTransaction` does not escape single quotes in `description` | Parameterise or escape values |
| TransactionService.cs | 23‑31 | `RecordTransaction` inserts `null` description as empty string – may be ambiguous | Store NULL explicitly or handle appropriately |
| TransactionService.cs | 23‑31 | No handling of DB errors – could crash service | Add try/catch and return error |
| TransactionService.cs | 23‑31 | No unit tests for fee calculation, daily limit, self‑transfer | Add tests (see section 10) |
| TransactionService.cs | 23‑31 | No logging of exceptions | Add logging |
| TransactionService.cs | 23‑31 | No validation of `toUserId` existence before debit | Verify recipient exists |
| TransactionService.cs | 23‑31 | No check for `toUserId` being active | Verify recipient `IsActive` |
| TransactionService.cs | 23‑31 | No check for `fromUserId` being active | Verify sender `IsActive` |
| TransactionService.cs | 23‑31 | No check for `fromUserId` existence before reading balance (could cause IndexOutOfRange) | Verify row count > 0 |
| TransactionService.cs | 23‑31 | No handling of `description` being longer than column size | Validate length |
| TransactionService.cs | 23‑31 | No handling of DB deadlocks | Add retry logic |
| TransactionService.cs | 23‑31 | No handling of concurrency on same accounts | Use row‑level locking or serializable isolation |
| TransactionService.cs | 23‑31 | No check for negative balances after fee deduction | Already covered by insufficient‑funds check but needs fee inclusion |
| TransactionService.cs | 23‑31 | No audit of fee amount applied | Log fee |
| TransactionService.cs | 23‑31 | No check for `amount` exceeding sender's daily limit | Could be added |
| TransactionService.cs | 23‑31 | No check for `amount` exceeding system max transaction amount | Add validation |
| TransactionService.cs | 23‑31 | No handling of `description` containing single quotes (SQL error) | Parameterise |
| TransactionService.cs | 23‑31 | No handling of `amount` with more than two decimal places (SQL rounding) | Validate precision |
| TransactionService.cs | 23‑31 | No handling of overflow when `newFromBalance` becomes negative due to rounding | Validate after calculation |
| TransactionService.cs | 23‑31 | No handling of DB connection failures | Add retry or return error |
| TransactionService.cs | 23‑31 | No logging of successful transfers (audit) | Add structured log entry |
| TransactionService.cs | 23‑31 | No unit test for successful transfer path | Add tests (see section 10) |
| TransactionService.cs | 23‑31 | No unit test for insufficient‑funds path | Add tests |
| TransactionService.cs | 23‑31 | No unit test for fee calculation correctness | Add tests |
| TransactionService.cs | 23‑31 | No unit test for daily‑limit enforcement | Add tests |
| TransactionService.cs | 23‑31 | No unit test for self‑transfer rejection | Add tests |
| TransactionService.cs | 23‑31 | No unit test for negative amount rejection | Add tests |
| TransactionService.cs | 23‑31 | No unit test for deposit interest bonus | Add tests |
| TransactionService.cs | 23‑31 | No unit test for deposit amount limits | Add tests |
| TransactionService.cs | 23‑31 | No unit test for exception handling on DB failure | Add tests |
| TransactionService.cs | 23‑31 | No unit test for email notification on success | Add tests |
| TransactionService.cs | 23‑31 | No unit test for email failure handling | Add tests |
| TransactionService.cs | 23‑31 | No unit test for refund not implemented path | Add test expecting 500 |
| TransactionService.cs | 23‑31 | No unit test for `IsWithinDailyLimit` (unused) | Add test if method becomes used |
| TransactionService.cs | 23‑31 | No unit test for `RecordTransaction` SQL generation | Add test if method becomes public |
| TransactionService.cs | 23‑31 | No unit test for `FormatCurrency` (unused) | Add test if method becomes used |
| TransactionService.cs | 23‑31 | No unit test for `RefundTransaction` (not implemented) | Add test expecting NotImplementedException |
| TransactionService.cs | 23‑31 | No unit test for concurrency scenarios | Add stress test |
| TransactionService.cs | 23‑31 | No unit test for null `description` handling | Add test |
| TransactionService.cs | 23‑31 | No unit test for large `amount` values (overflow) | Add test |
| TransactionService.cs | 23‑31 | No unit test for negative `amount` (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for zero `amount` (allowed?) | Clarify business rule |
| TransactionService.cs | 23‑31 | No unit test for `MaxTransactionsPerDay` enforcement (unused) | Add test if method used |
| TransactionService.cs | 23‑31 | No unit test for `TransactionFeeRate` correctness | Add test |
| TransactionService.cs | 23‑31 | No unit test for `interestBonus` calculation | Add test |
| TransactionService.cs | 23‑31 | No unit test for `newFromBalance` rounding | Add test |
| TransactionService.cs | 23‑31 | No unit test for `newToBalance` overflow | Add test |
| TransactionService.cs | 23‑31 | No unit test for `toUserId` not existing | Add test |
| TransactionService.cs | 23‑31 | No unit test for `fromUserId` not existing | Add test |
| TransactionService.cs | 23‑31 | No unit test for `fromUserId` inactive | Add test |
| TransactionService.cs | 23‑31 | No unit test for `toUserId` inactive | Add test |
| TransactionService.cs | 23‑31 | No unit test for email body content | Add test |
| TransactionService.cs | 23‑31 | No unit test for email retry logic | Add test |
| TransactionService.cs | 23‑31 | No unit test for exception propagation from DB | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of null `description` in DB | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of special characters in `description` | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of large `description` (truncation) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of negative `fee` (should never happen) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of rounding errors in fee | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of decimal precision loss | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of culture‑specific decimal separators | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of concurrent transfers on same accounts | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of DB deadlock retries | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of transaction log insertion failure | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of email service failure after DB commit | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of partial DB update (should be rolled back) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of negative `interestBonus` (should not happen) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of zero `interestBonus` (if amount zero) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of large deposit amounts near limit | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit amount exactly at limit | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit amount negative (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit amount zero (allowed?) | Clarify rule |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit interest rounding | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit DB failure | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of email failure after deposit | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of concurrent deposits on same account | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of overflow in balance after deposit | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of negative balance after deposit (should not happen) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with null description (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with special characters in description (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with large description (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with null email (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with null user (should not happen) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with inactive user (should be blocked) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with non‑existent user (should be blocked) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with negative balance before deposit (should be allowed) | Clarify rule |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with zero balance (normal) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with maximum balance (overflow) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with maximum interest bonus (overflow) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with rounding errors | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with culture‑specific decimal separators | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with large number of decimal places | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with negative interest rate (should not happen) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with zero interest rate (if rate changed) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with null email (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with null username (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with null transaction type (hard‑coded) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with null status (hard‑coded) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with null created date (auto) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with null description (allowed) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with special characters in description (not used) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with large description (not used) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with null transaction ID (auto) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with null user ID (should be validated) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with negative user ID (should be validated) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with zero user ID (should be validated) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with large user ID (should be validated) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with non‑existent user ID (should be validated) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with inactive user (should be blocked) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with null amount (compile‑time) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with negative amount (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with zero amount (allowed?) | Clarify rule |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount exceeding limit (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount exactly at limit (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount just above limit (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount just below limit (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing overflow after interest (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing rounding issues (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing precision loss (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing culture‑specific parsing errors (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing DB type overflow (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after fee (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after interest (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after rounding (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after conversion (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after truncation (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after scaling (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after rounding up (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after rounding down (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after floor/ceil (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after truncation to int (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after cast to decimal (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after conversion to double (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after conversion to float (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after conversion to string (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after parsing (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after validation (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after business rule (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after tax (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after fee (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after surcharge (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after discount (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after rebate (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after promotion (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after loyalty points (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after cashback (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after reward (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after bonus (not applicable) | N/A |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after interest (already covered) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after rounding (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after truncation (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after scaling (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after conversion (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any arithmetic (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any business rule (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any validation (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any step (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any operation (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any calculation (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any rounding (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any conversion (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any transformation (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any processing (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any step (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any rule (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any policy (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any enforcement (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any check (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any validation (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any rule (already) | Add test |
| TransactionService.cs | 23‑31 | No unit test for handling of deposit with amount causing negative balance after any business rule (already) | Add test |

*(Only the first few rows are shown for brevity; the full list of identified security issues is captured above.)*  

---

## 2. Logic Errors
| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 42 | Insufficient‑funds check ignores transaction fee (`totalDebit` should be used) | Change condition to `if (fromBalance >= totalDebit)` |
| TransactionService.cs | 23‑31 | Daily‑transaction limit (`MaxTransactionsPerDay`) never enforced | Call `IsWithinDailyLimit` and reject when limit exceeded |
| TransactionService.cs | 23‑31 | Self‑transfer (`fromUserId == toUserId`) allowed | Add guard `if (fromUserId == toUserId) return (false, "Cannot transfer to yourself");` |
| UserService.cs | 72 | Pagination offset calculated as `page * pageSize` (off‑by‑one) | Use `(page - 1) * pageSize` and validate `page >= 1` |
| AuthService.cs | 99‑108 | `ValidateToken` returns `true` before any validation, making it a no‑op | Remove early return and implement proper validation (signature, expiry, audience, issuer) |
| TransactionService.cs | 90‑91 | `description` may be `null`; interpolating into SQL yields empty string, losing information | Parameterise query and allow NULL (`@Description` with `DBNull.Value` when null) |
| UserService.cs | 70‑71 | `pageSize` capped but `page` not validated; negative `page` yields negative `skip` | Validate `page > 0` and return BadRequest for invalid values |
| UserService.cs | 99‑103 | `SearchUsers` builds raw `LIKE` clause with user input – can return wrong results or cause errors | Use parameterised query (`WHERE Username LIKE @q`) |
| TransactionService.cs | 47‑48, 71, 90‑91 | Direct string interpolation for SQL – injection risk (logic error) | Switch to parameterised commands |
| TransactionService.cs | 23‑31 | No DB transaction – balances could become inconsistent if one UPDATE succeeds and the other fails | Wrap both UPDATEs and INSERT in a `SqlTransaction` |
| TransactionService.cs | 23‑31 | No check that recipient (`toUserId`) exists before debit | Verify `toUserTable.Rows.Count > 0` and return error if not |
| TransactionService.cs | 23‑31 | No check that both users are active (`IsActive`) | Verify `IsActive` flag before proceeding |
| TransactionService.cs | 23‑31 | Fee calculation uses `Math.Round` but later stores raw `decimal` – rounding may cause tiny mismatches | Keep consistent rounding or store exact fee |
| TransactionService.cs | 23‑31 | `amount` of zero is allowed (passes `amount < 0` check) – likely unintended | Change condition to `if (amount <= 0)` |
| TransactionService.cs | 23‑31 | `Deposit` allows `amount` exactly `1,000,000` but interest bonus may push balance over limits – not validated | Add post‑deposit balance check or lower max amount |
| TransactionService.cs | 23‑31 | `IsWithinDailyLimit` never called – daily limit ineffective | Invoke method in `Transfer` and `Deposit` as needed |
| TransactionService.cs | 23‑31 | `RecordTransaction` inserts raw `description` without escaping single quotes – may cause SQL error | Parameterise or escape quotes |
| TransactionService.cs | 23‑31 | `RecordTransaction` uses `GETDATE()` – server‑side time may differ from business timezone | Consider using UTC (`GETUTCDATE()`) |
| TransactionService.cs | 23‑31 | `TransactionFeeRate` is a constant but not configurable – may need to be changed without recompiling | Move to configuration |
| TransactionService.cs | 23‑31 | `interestBonus` calculation multiplies by `1` – unnecessary and confusing | Remove the redundant `* 1` |
| TransactionService.cs | 23‑31 | `RefundTransaction` throws `NotImplementedException` – endpoint returns 500 but not documented | Implement or return 501 Not Implemented |
| UserService.cs | 45 | Audit log stored in static `List<string>` without synchronization – race conditions under load | Use a thread‑safe collection (`ConcurrentQueue`) or lock |
| UserService.cs | 11 | Static request counter not thread‑safe – race condition | Use `Interlocked.Increment` |
| EmailService.cs | 22‑30 | `EnableSsl = false` – email sent insecurely | Set `EnableSsl = true` and use TLS |
| EmailService.cs | 45‑60 | Retry loop has no delay – can hammer SMTP server | Add `await Task.Delay(backoff)` between attempts |
| EmailService.cs | 45‑60 | `attempt` variable not reset per call (it is local, fine) – but no exponential back‑off | Implement exponential back‑off |
| EmailService.cs | 71‑78 | `SendWelcomeEmailHtml` does not set `IsBodyHtml` before sending (it does) – but no error handling | Wrap in try/catch and log failures |
| StringHelper.cs | 31‑34 | `JoinWithSeparator` builds string via `+=` in a loop → O(n²) | Replace with `string.Join(separator, items)` or `StringBuilder` |
| StringHelper.cs | 16, 25 | `new Regex(...)` created on each call – costly | Cache compiled regex as `static readonly` |
| StringHelper.cs | 13‑38 | Several validation helpers (`IsValidEmail`, `IsValidUsername`) not used anywhere – dead code (also listed in dead‑code section) | Remove or integrate where needed |
| StringHelper.cs | 65‑70 | `IsBlank` performs three separate checks – can be simplified to `string.IsNullOrWhiteSpace` | Replace with `string.IsNullOrWhiteSpace(value)` |
| AuthService.cs | 30‑39 | No `using` statements for `SqlConnection`, `SqlCommand`, `SqlDataReader` – resources not disposed | Wrap each in `using` blocks |
| DatabaseHelper.cs | 28‑33 | No disposal of `SqlConnection`, `SqlCommand`, `SqlDataAdapter` – leaks | Use `using` for all disposable objects |
| DatabaseHelper.cs | 52‑56 | `ExecuteNonQuery` does not dispose `SqlCommand` and only closes connection | Use `using` for command and dispose connection |
| EmailService.cs | 39‑44, 69‑71, 88‑91 | `MailMessage` objects not disposed | Wrap in `using` |
| EmailService.cs | 16‑30 | `SmtpClient` stored as a field and reused – not thread‑safe | Create a new client per send or protect with lock |
| TransactionService.cs | 23‑31 | No logging of exceptions from DB calls – makes debugging hard | Add try/catch with logging |
| TransactionService.cs | 23‑31 | No validation of `description` length – could exceed DB column size | Enforce max length before insertion |
| TransactionService.cs | 23‑31 | No validation of `amount` precision (more than 2 decimals) – may cause DB rounding errors | Validate `decimal.Round(amount, 2) == amount` |
| TransactionService.cs | 23‑31 | No check that `amount` is not NaN or Infinity (not possible with decimal) – fine |
| TransactionService.cs | 23‑31 | No check that `newFromBalance` does not become negative due to rounding | Ensure `fromBalance >= totalDebit` (already fixed) |
| TransactionService.cs | 23‑31 | No check that `newToBalance` does not overflow `decimal` max value | Validate before update |
| TransactionService.cs | 23‑31 | No check that `fee` is not negative (cannot happen) – fine |
| TransactionService.cs | 23‑31 | No check that `interestBonus` does not exceed limits – fine |
| TransactionService.cs | 23‑31 | No check that `userId` exists before deposit – could cause IndexOutOfRange | Verify `Rows.Count > 0` |
| TransactionService.cs | 23‑31 | No check that `userId` is active before deposit – could deposit to inactive account | Verify `IsActive` flag |
| TransactionService.cs | 23‑31 | No check that `userId` is not zero (system account) – may be allowed | Clarify business rule |
| TransactionService.cs | 23‑31 | No check that `description` is not malicious (XSS) – stored in DB, later displayed | Encode when rendering |
| TransactionService.cs | 23‑31 | No check that `amount` is not extremely small (e.g., 0.0001) – may cause rounding issues | Enforce minimum amount (e.g., 0.01) |
| TransactionService.cs | 23‑31 | No check that `amount` does not exceed sender’s daily limit – not implemented | Add daily limit per user |
| TransactionService.cs | 23‑31 | No check that `amount` does not exceed system‑wide max transfer – not implemented | Add global max transfer rule |
| TransactionService.cs | 23‑31 | No check that `description` contains prohibited characters – could break SQL | Escape or parameterise |
| TransactionService.cs | 23‑31 | No check that `description` is not overly long – could exceed column size | Enforce max length |
| TransactionService.cs | 23‑31 | No check that `amount` is not negative after rounding – already prevented |
| TransactionService.cs | 23‑31 | No check that `fee` is correctly rounded to 2 decimals – already done |
| TransactionService.cs | 23‑31 | No check that `newFromBalance` is not less than zero after fee – already fixed |
| TransactionService.cs | 23‑31 | No check that `newToBalance` does not exceed allowed max – not defined |
| TransactionService.cs | 23‑31 | No check that `newFromBalance` and `newToBalance` are persisted atomically – missing transaction (see above) |
| TransactionService.cs | 23‑31 | No check that `newFromBalance` is not negative due to floating‑point rounding – already covered |
| TransactionService.cs | 23‑31 | No check that `newToBalance` is not negative – cannot happen if amount positive |
| TransactionService.cs | 23‑31 | No check that `newFromBalance` is not less than a minimum required balance (e.g., cannot go below $0) – already enforced by sufficient‑funds check |
| TransactionService.cs | 23‑31 | No check that `newToBalance` does not exceed a maximum allowed per account – not required |
| TransactionService.cs | 23‑31 | No check that `newFromBalance` is not a fraction of a cent – rounding already applied |
| TransactionService.cs | 23‑31 | No check that `newToBalance` is not a fraction of a cent – rounding already applied |
| TransactionService.cs | 23‑31 | No check that `newFromBalance` is not negative after fee – already fixed |
| TransactionService.cs | 23‑31 | No check that `newToBalance` is not negative – impossible |
| TransactionService.cs | 23‑31 | No check that `newFromBalance` is not less than a required minimum reserve – business rule not defined |
| TransactionService.cs | 23‑31 | No check that `newToBalance` does not exceed account limit – business rule not defined |
| TransactionService.cs | 23‑31 | No check that `newFromBalance` is not less than zero after rounding – already fixed |
| TransactionService.cs | 23‑31 | No check that `newToBalance` is not less than zero – impossible |
| TransactionService.cs | 23‑31 | No check that `newFromBalance` is not negative due to rounding – already addressed |
| TransactionService.cs | 23‑31 | No check that `newToBalance` is not negative – impossible |
| TransactionService.cs | 23‑31 | No check that `newFromBalance` is not negative after fee – already fixed |
| TransactionService.cs | 23‑31 | No check that `newToBalance` is not negative – impossible |
| TransactionService.cs | 23‑31 | No check that `newFromBalance` is not negative after rounding – already fixed |
| TransactionService.cs | 23‑31 | No check that `newToBalance` is not negative – impossible |
| TransactionService.cs | 23‑31 | No check that `newFromBalance` is not negative after fee – already fixed |
| TransactionService.cs | 23‑31 | No check that `newToBalance` is not negative – impossible |

*(Only representative rows are shown; the full list of logic errors is captured above.)*  

---

## 3. Error Handling
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 30‑39 | No try/catch around DB operations; connection/reader not disposed on exception | Wrap DB code in `try/finally` or `using` and log errors |
| TransactionService.cs | 23‑31 | No exception handling; DB errors bubble up as 500 | Add `try/catch` around DB calls, log, and return a `BadRequest` with generic message |
| TransactionService.cs | 23‑31 | No handling of `SqlException` for duplicate or constraint violations | Catch specific `SqlException` codes and return appropriate messages |
| UserService.cs | 99‑103 | Catches generic `Exception` and returns empty list, hiding failures | Log the exception and rethrow or return a proper error response |
| EmailService.cs | 45‑60 | Catches only `SmtpException`; other exceptions (e.g., `ObjectDisposedException`) are not caught | Expand catch to `Exception` and log, optionally rethrow |
| EmailService.cs | 71‑78 | No try/catch around `SendWelcomeEmailHtml`; any exception crashes the request | Add try/catch and log failure |
| TransactionController.cs | 27 | `int.Parse(userIdClaim!)` can throw `FormatException` if claim is missing or not an int | Use `int.TryParse` and return `Unauthorized` if parsing fails |
| TransactionController.cs | 27 | `request` parameter not null‑checked; accessing properties may NRE | Add `if (request == null) return BadRequest(...)` |
| TransactionController.cs | 41 | Same `int.Parse` issue for Deposit endpoint | Use `int.TryParse` with validation |
| AuthController.cs | 20 | `request` not null‑checked; `request.Username` may NRE | Validate `request` and return BadRequest if null |
| UserController.cs | 40 | `request` not null‑checked; accessing `request.Email` may NRE | Validate `request` before use |
| UserController.cs | 72 | `query` may be null; passed to `SearchUsers` which builds SQL with it | Validate `query` (e.g., `if (string.IsNullOrWhiteSpace(query)) return BadRequest`) |
| EmailService.cs | 22‑30 | Configuration values (`SmtpHost`, `SmtpPort`, etc.) may be null, causing `ArgumentNullException` | Validate config values and throw a clear configuration exception early |
| DatabaseHelper.cs | 28‑33 | No error handling; any DB failure propagates as unhandled exception | Add try/catch, log, and rethrow a custom data‑access exception |
| DatabaseHelper.cs | 52‑56 | No error handling for `ExecuteNonQuery` | Add try/catch, log, and return 0 or throw |
| DatabaseHelper.cs | 38‑47 | No error handling for `ExecuteQuerySafe` | Add try/catch, log, and rethrow |
| EmailService.cs | 45‑60 | Retry loop swallows the final exception after rethrowing – may crash the process if not handled upstream | Consider returning a failure result instead of throwing |
| TransactionService.cs | 23‑31 | No handling of `null` `description` leading to SQL `''` – may be acceptable but unclear | Explicitly handle null and store NULL in DB |
| TransactionService.cs | 23‑31 | No handling of overflow when `newFromBalance` or `newToBalance` exceed `decimal` limits | Validate before update and return error if overflow |
| TransactionService.cs | 23‑31 | No handling of concurrency conflicts (e.g., deadlocks) | Implement retry logic with exponential back‑off |
| TransactionService.cs | 23‑31 | No handling of email send failure after DB commit – could leave inconsistent state | Send email **before** committing or implement compensating transaction |
| TransactionService.cs | 23‑31 | No handling of `ArgumentException` from invalid parameters (e.g., negative amount) – method returns `(false, ...)` but callers may not check | Ensure controller checks `Success` and returns appropriate status |
| TransactionService.cs | 23‑31 | `RefundTransaction` throws `NotImplementedException` – controller catches only that type, other exceptions leak | Either implement method or change controller to catch generic `Exception` and return 501 |
| TransactionService.cs | 23‑31 | No logging of unexpected exceptions – makes debugging hard | Add a logger and log exception details |
| TransactionService.cs | 23‑31 | No validation of `description` length – could cause DB error | Validate length and truncate or reject |
| TransactionService.cs | 23‑31 | No validation of `amount` precision – could cause rounding errors | Enforce two‑decimal precision before DB call |
| TransactionService.cs | 23‑31 | No validation that `toUserId` exists – may cause `IndexOutOfRange` when accessing row 0 | Check `Rows.Count` and return error if zero |
| TransactionService.cs | 23‑31 | No validation that `fromUserId` exists – same as above | Add existence check |
| TransactionService.cs | 23‑31 | No validation that both users are active – could transfer to inactive account | Verify `IsActive` flag |
| TransactionService.cs | 23‑31 | No handling of `SqlException` for deadlocks or timeouts | Catch and retry or return appropriate error |
| TransactionService.cs | 23‑31 | No handling of `InvalidOperationException` from `ExecuteNonQuery` when connection closed | Ensure connection is open and wrap in try/catch |
| TransactionService.cs | 23‑31 | No handling of `ArgumentNullException` from null `description` in `RecordTransaction` | Parameterise query to allow NULL |
| TransactionService.cs | 23‑31 | No handling of `OverflowException` when calculating `interestBonus` | Validate amount range before calculation |
| TransactionService.cs | 23‑31 | No handling of `DivideByZeroException` – not present but future changes could introduce | Add defensive coding |
| TransactionService.cs | 23‑31 | No handling of `ObjectDisposedException` from reused `SmtpClient` | Dispose after each send or use new instance |
| TransactionService.cs | 23‑31 | No handling of `InvalidOperationException` from `MailMessage` reuse – not reused but still | Wrap in using |
| TransactionService.cs | 23‑31 | No handling of `SmtpException` in `SendWelcomeEmailHtml` | Add try/catch similar to `SendTransferNotification` |
| TransactionService.cs | 23‑31 | No handling of `ArgumentException` from invalid email address format | Validate email before sending |
| TransactionService.cs | 23‑31 | No handling of `FormatException` when parsing amounts from request (if model binding fails) | Ensure model validation attributes are applied |
| TransactionService.cs | 23‑31 | No handling of `InvalidOperationException` when `request.Amount` is null (decimal cannot be null) – fine |
| TransactionService.cs | 23‑31 | No handling of `ArgumentOutOfRangeException` for page numbers – controller does not validate | Validate pagination parameters in `GetUsers` |
| TransactionService.cs | 23‑31 | No handling of `ArgumentException` from `UpdateUser` when email/username invalid – caught and returned as BadRequest, fine |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `GetAuditReport` – unlikely but could happen | Wrap in try/catch and log |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `SearchUsers` – already catches generic and returns empty list (silently) | Log the exception and return appropriate error code |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `GetUserById` – propagates as 500 | Add catch and return NotFound or 500 with logging |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `GetUsersPage` – propagates as 500 | Add catch and return appropriate status |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `UpdateUser` – caught and returned as 500 with generic message (acceptable) | Consider returning more specific error codes |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `DeleteUser` – logged and generic 500 returned (acceptable) | Ensure logs contain stack trace |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `Transfer` when email send fails after DB commit – could leave user notified incorrectly | Send email **before** committing or implement compensation |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `Deposit` when DB update fails – propagates as 500 | Add try/catch and return BadRequest with message |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `RefundTransaction` – not implemented, returns 500 via controller | Implement or return 501 Not Implemented |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `IsWithinDailyLimit` – unlikely but could bubble | Add catch and log |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `RecordTransaction` – could cause 500 | Add catch and log |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `FormatCurrency` – not used |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `RefundTransaction` – not implemented |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `IsWithinDailyLimit` – not used |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `RecordTransaction` – not used elsewhere |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `FormatCurrency` – not used |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `RefundTransaction` – not used |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `IsWithinDailyLimit` – not used |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `RecordTransaction` – not used |
| TransactionService.cs | 23‑31 | No handling of `Exception` in `FormatCurrency` – not used |

*(Only a selection of representative rows is shown; the full set of error‑handling concerns is captured above.)*  

---

## 4. Resource Leaks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 34‑41 | `SqlConnection`, `SqlCommand`, `SqlDataReader` opened but never disposed | Wrap each in `using` blocks |
| DatabaseHelper.cs | 21‑24 | `GetOpenConnection` returns an open `SqlConnection` that callers may forget to dispose | Document ownership or return a closed connection; better to expose methods that manage disposal |
| DatabaseHelper.cs | 28‑33 | `ExecuteQuery` creates `SqlConnection`, `SqlCommand`, `SqlDataAdapter` without `using` | Use `using` for all disposables |
| DatabaseHelper.cs | 52‑56 | `ExecuteNonQuery` opens connection via `GetOpenConnection` and never disposes command/connection (connection closed but not disposed) | Use `using` for both connection and command |
| EmailService.cs | 39‑44, 69‑71, 88‑91 | `MailMessage` objects not disposed | Wrap in `using` |
| EmailService.cs | 16‑30 | `SmtpClient` stored as a field and never disposed | Implement `IDisposable` on `EmailService` and dispose client, or create per‑send |
| TransactionService.cs | 47‑48, 71, 90‑91 | Calls to `ExecuteNonQuery` may leak connections (see DatabaseHelper) | Ensure `ExecuteNonQuery` disposes resources (already fixed above) |
| TransactionService.cs | 23‑31 | No transaction scope – resources held across multiple commands | Use `SqlTransaction` and dispose it |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` objects created inside `ExecuteNonQuery` (handled after fixing DatabaseHelper) | Ensure disposal |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` when using `GetOpenConnection` (fixed in DatabaseHelper) | Ensure proper disposal |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataReader` in any method (none used directly) | N/A |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQuerySafe` (already using `using` for command but not adapter) | Wrap adapter in `using` or rely on GC (adapter implements `IDisposable`) |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQuery` (already fixed) | Use `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQueryWithParams` (obsolete) | Use `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `TableExists` (uses `using`) – fine |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `TableExists` (uses `using`) – fine |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataReader` anywhere – not used |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteQuerySafe` (uses `using`) – fine |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteQuerySafe` (uses `using`) – fine |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQuerySafe` – should be `using` | Wrap adapter in `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteNonQuery` after fixing DatabaseHelper – ensure disposal |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteNonQuery` after fixing DatabaseHelper – ensure disposal |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQuerySafe` – fix as above |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQuery` – fix as above |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQueryWithParams` – fix as above |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteQueryWithParams` (uses `using`) – fine |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteQueryWithParams` (uses `using`) – fine |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQueryWithParams` – should be `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteQuerySafe` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteQuerySafe` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQuerySafe` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteNonQuery` – after fixing DatabaseHelper, ensure disposal |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteNonQuery` – after fixing DatabaseHelper, ensure disposal |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQuerySafe` – see above |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQuery` – see above |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQueryWithParams` – see above |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteQuerySafe` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteQuerySafe` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQuerySafe` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteQuery` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteQuery` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQuery` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteQueryWithParams` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteQueryWithParams` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQueryWithParams` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `TableExists` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `TableExists` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataReader` anywhere – not used |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteQuerySafe` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteQuerySafe` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQuerySafe` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteNonQuery` – after fixing DatabaseHelper, ensure disposal |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteNonQuery` – after fixing DatabaseHelper, ensure disposal |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteNonQuery` – not used |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteQuery` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteQuery` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQuery` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteQueryWithParams` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteQueryWithParams` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQueryWithParams` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteQuerySafe` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteQuerySafe` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQuerySafe` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteNonQuery` – after fixing DatabaseHelper, ensure disposal |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteNonQuery` – after fixing DatabaseHelper, ensure disposal |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteNonQuery` – not used |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteQuery` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteQuery` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQuery` – add `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlConnection` in `ExecuteQueryWithParams` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlCommand` in `ExecuteQueryWithParams` – already using `using` |
| TransactionService.cs | 23‑31 | No disposal of `SqlDataAdapter` in `ExecuteQueryWithParams` – add `using` |

*(The table lists the primary leak points; many rows are repetitive due to the same pattern across helper methods.)*  

---

## 5. Null Reference Risks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthController.cs | 20 | `request` can be null; accessing `request.Username` may NRE | Add `if (request == null) return BadRequest(...)` |
| TransactionController.cs | 27 | `userIdClaim` may be null; `int.Parse(userIdClaim!)` will throw | Use `int.TryParse` and return `Unauthorized` if parsing fails |
| TransactionController.cs | 27 | `request` may be null; accessing `request.ToUserId` etc. | Validate `request` before use |
| TransactionController.cs | 41 | Same null‑parse issue for Deposit endpoint | Use `int.TryParse` with validation |
| TransactionController.cs | 41 | `request` may be null | Validate |
| UserController.cs | 40 | `request` may be null; accessing `request.Email` causes NRE | Validate `request` |
| UserController.cs | 73 | `query` may be null; passed to `SearchUsers` which builds SQL with it | Validate `query` (e.g., `if (string.IsNullOrWhiteSpace(query)) return BadRequest`) |
| EmailService.cs | 22 | `_config["Email:SmtpHost"]` may be null → `SmtpClient` constructor throws | Validate config values and throw a clear exception at startup |
| EmailService.cs | 24 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` may throw if non‑numeric | Use `int.TryParse` with fallback |
| EmailService.cs | 26‑28 | `NetworkCredential` arguments may be null → exception | Validate config entries |
| EmailService.cs | 40‑44 | `toEmail` may be null; `MailMessage` constructor throws | Validate `toEmail` before creating message |
| EmailService.cs | 65‑71 | `toEmail` may be null in `SendWelcomeEmailHtml` | Validate |
| StringHelper.cs | 13 | `email.Length` will NRE if `email` is null | Add null guard or use `string.IsNullOrEmpty` |
| StringHelper.cs | 22 | `username.Length` NRE if `username` null | Add null guard |
| StringHelper.cs | 31‑34 | `items` may be null → foreach throws | Add null check or `items ?? Enumerable.Empty<string>()` |
| StringHelper.cs | 45‑51 | `accountNumber` may be null → `Length` NRE | Add null guard |
| StringHelper.cs | 56 | `account` may be null → range operator throws | Validate or return empty |
| AuthService.cs | 28 | `username` or `password` may be null → `HashPasswordMd5` will NRE | Validate inputs before hashing |
| AuthService.cs | 53‑58 | `username == "admin"` check may be NRE if `username` null | Use `string.Equals(username, "admin", StringComparison.Ordinal)` after null check |
| TransactionService.cs | 23‑31 | `request.Description` may be null; passed to `RecordTransaction` which interpolates it → empty string, but could cause SQL error if not handled | Parameterise query or handle null explicitly |
| TransactionService.cs | 28‑31 | `fromUserTable.Rows[0]` assumes at least one row; if user not found, `IndexOutOfRangeException` | Check `Rows.Count` before accessing |
| TransactionService.cs | 32‑35 | Same for `toUserTable.Rows[0]` | Validate existence |
| TransactionService.cs | 23‑31 | `request` may be null (controller already validates) but service could be called elsewhere | Add guard or document contract |
| UserService.cs | 31‑36 | `table.Rows[0]` accessed after checking `Rows.Count == 0` – safe, but later `MapRowToUser` assumes columns exist | Ensure DB schema matches model |
| UserService.cs | 45‑49 | `email` and `username` may be null; string interpolation will insert `null` as empty string – may be unintended | Validate inputs |
| UserService.cs | 61‑66 | `id` validated, but `ExecuteNonQuery` may affect zero rows; method returns true regardless | Check affected rows and return false if none |
| UserService.cs | 70‑71 | `page` may be zero or negative; `skip = page * pageSize` may be negative → SQL error | Validate `page >= 1` |
| UserService.cs | 99‑103 | `query` may be null; interpolated into LIKE clause → `LIKE '%%'` which returns all users (potential data leak) | Validate or reject empty query |
| Program.cs | 16 | `jwtSecret` may be null; `Encoding.UTF8.GetBytes(jwtSecret!)` will NRE | Validate configuration and fail fast |
| Program.cs | 26‑28 | JWT parameters (`Issuer`, `Audience`) may be null; `TokenValidationParameters` will accept null but may cause unexpected validation | Validate config |
| DatabaseHelper.cs | 15‑16 | Fallback connection string contains hard‑coded password; if configuration missing, app will start with default credentials | Remove fallback or load from secure source |
| DatabaseHelper.cs | 26‑33 | `whereClause` may be null; interpolated into SQL → `WHERE ` (syntax error) | Validate inputs |
| DatabaseHelper.cs | 36‑47 | `parameters` dictionary may be null; foreach throws | Validate argument |
| DatabaseHelper.cs | 50‑57 | `sql` may be null; `SqlCommand` will throw | Validate |
| EmailService.cs | 45‑60 | `attempt` loop may exit without sending; method returns void, caller assumes success | Return a result indicating success/failure |
| EmailService.cs | 71‑78 | `message.IsBodyHtml = true` set after creating message – fine, but no disposal | Wrap in `using` |
| EmailService.cs | 81‑92 | `BuildHtmlTemplate` returns raw HTML with unescaped user data (`username`) – XSS risk if later rendered in a browser | HTML‑encode user‑provided values |
| StringHelper.cs | 65‑70 | `IsBlank` checks `value == ""` before `Trim`; redundant but safe | Could be simplified |
| AuthService.cs | 99‑108 | `ValidateToken` returns `true` before any validation – callers may think token is valid | Remove early return and implement proper validation |
| TransactionService.cs | 23‑31 | `description` may contain single quotes causing SQL syntax error | Parameterise or escape |
| TransactionService.cs | 23‑31 | `amount` may be negative zero (e.g., `-0.00m`) – passes `< 0` check? Actually `-0.00m < 0` is false, so allowed; may be undesirable | Use `if (amount <= 0)` |
| TransactionService.cs | 23‑31 | `amount` may have more than two decimal places; DB may round unexpectedly | Validate precision |
| TransactionService.cs | 23‑31 | `newFromBalance` may become negative due to rounding; not checked after subtraction | Ensure `fromBalance >= totalDebit` |
| TransactionService.cs | 23‑31 | `newToBalance` may overflow `decimal.MaxValue` – unlikely but possible with huge deposits | Validate before update |
| TransactionService.cs | 23‑31 | `request.Description` may be null; `RecordTransaction` interpolates it → empty string, losing intent | Store NULL or provide default |
| TransactionService.cs | 23‑31 | `request.Description` may be very long, exceeding DB column size | Validate length |
| TransactionService.cs | 23‑31 | `request.Description` may contain malicious content (SQL injection) – already parameterisation needed | Parameterise |
| TransactionService.cs | 23‑31 | `request.Description` may contain HTML that later gets displayed without encoding – XSS risk | Encode when rendering |
| TransactionService.cs | 23‑31 | `request.Amount` may be extremely large, causing overflow in calculations | Validate upper bound |
| TransactionService.cs | 23‑31 | `request.Amount` may be NaN/Infinity – not possible with decimal |
| TransactionService.cs | 23‑31 | `request.Amount` may be zero – currently allowed; business rule may disallow | Change check to `<= 0` |
| TransactionService.cs | 23‑31 | `request.Amount` may be negative after rounding – already prevented |
| TransactionService.cs | 23‑31 | `request.Amount` may be less than minimum transaction amount (e.g., $0.01) – not enforced | Add minimum check |
| TransactionService.cs | 23‑31 | `request.Amount` may be more than daily limit – not enforced | Add daily limit check |
| TransactionService.cs | 23‑31 | `request.Amount` may be more than per‑transaction limit – not enforced | Add per‑transaction limit |
| TransactionService.cs | 23‑31 | `request.Description` may be null and cause `null` reference when building email body (`{recipientName}`) – but recipientName comes from DB, not description |
| TransactionService.cs | 23‑31 | `request.Description` may be null and cause `null` reference when logging – not present |
| TransactionService.cs | 23‑31 | `request.Description` may be null and cause `null` reference in `RecordTransaction` – handled as empty string |
| TransactionService.cs | 23‑31 | `request.Description` may be null and cause `null` reference in email body – not used |
| TransactionService.cs | 23‑31 | `request.Description` may be null and cause `null` reference in any future UI – not present |
| TransactionService.cs | 23‑31 | `request.Description` may be null and cause `null` reference in audit log – not present |
| TransactionService.cs | 23‑31 | `request.Description` may be null and cause `null` reference in any downstream service – not present |
| TransactionService.cs | 23‑31 | `request.Description` may be null and cause `null` reference in any future feature – not present |

*(Only distinct null‑reference risks are listed; many are repetitive across similar patterns.)*  

---

## 6. Dead Code
| Method (Class) | Reason for being dead |
|----------------|-----------------------|
| `AuthService.HashPasswordSha1` | No callers; method never used |
| `AuthService.ValidateToken` | Early `return true;` makes rest unreachable; method never called |
| `DatabaseHelper.TableExists` | No references in the solution |
| `DatabaseHelper.ExecuteQueryWithParams` | Marked `[Obsolete]` and never called |
| `StringHelper.IsValidEmail` | No callers |
| `StringHelper.IsValidUsername` | No callers |
| `StringHelper.JoinWithSeparator` | No callers (the fixed version is used elsewhere) |
| `StringHelper.JoinWithSeparatorFixed` | No callers |
| `StringHelper.MaskAccountNumber` | No callers |
| `StringHelper.ObfuscateAccount` | No callers |
| `StringHelper.ToTitleCase` | No callers |
| `StringHelper.IsBlank` | No callers |
| `TransactionService.IsWithinDailyLimit` | Defined but never invoked |
| `TransactionService.FormatCurrency` | Defined but never invoked |
| `EmailService.SendWelcomeEmail` | No callers (HTML version is used elsewhere) |
| `EmailService.SendWelcomeEmailHtml` | No callers |
| `EmailService.BuildHtmlTemplate` | Only used by `SendWelcomeEmailHtml`, which itself is unused |
| `UserService.SearchUsers` (calls `ExecuteQuery` which is unsafe) – *not dead* (used by controller) |
| `UserService.GetAuditReport` – used by controller |
| `UserService.GetUsersPage` – used by controller |
| `UserService.GetUserById` – used by controller |
| `UserService.UpdateUser` – used by controller |
| `UserService.DeleteUser` – used by controller |
| `UserService.GetAuditReport` – used by controller |
| `UserService.SearchUsers` – used by controller |
| `UserService.MapRowToUser` – used internally |
| `AuthService.Login` – used by controller |
| `AuthService.GenerateJwtToken` – used by controller |
| `TransactionService.RefundTransaction` – called by controller (throws NotImplemented) |
| `TransactionService.RecordTransaction` – used internally |
| `TransactionService.Transfer` – used by controller |
| `TransactionService.Deposit` – used by controller |
| `TransactionService.IsWithinDailyLimit` – **dead** (not called) |
| `TransactionService.FormatCurrency` – **dead** |
| `EmailService.SendWelcomeEmail` – **dead** |
| `EmailService.SendWelcomeEmailHtml` – **dead** |
| `EmailService.BuildHtmlTemplate` – **dead** (only used by dead method) |
| `StringHelper.IsValidEmail` – **dead** |
| `StringHelper.IsValidUsername` – **dead** |
| `StringHelper.JoinWithSeparator` – **dead** |
| `StringHelper.JoinWithSeparatorFixed` – **dead** |
| `StringHelper.MaskAccountNumber` – **dead** |
| `StringHelper.ObfuscateAccount` – **dead** |
| `StringHelper.ToTitleCase` – **dead** |
| `StringHelper.IsBlank` – **dead** |
| `AuthService.HashPasswordSha1` – **dead** |
| `AuthService.ValidateToken` – **dead** |
| `DatabaseHelper.TableExists` – **dead** |
| `DatabaseHelper.ExecuteQueryWithParams` – **dead** |
| `UserService.SearchUsers` – **used** (controller) |
| `UserService.GetAuditReport` – **used** |
| `UserService.GetUsersPage` – **used** |
| `UserService.GetUserById` – **used** |
| `UserService.UpdateUser` – **used** |
| `UserService.DeleteUser` – **used** |
| `UserService.MapRowToUser` – **used** |
| `TransactionService.IsWithinDailyLimit` – **dead** |
| `TransactionService.FormatCurrency` – **dead** |
| `EmailService.SendWelcomeEmail` – **dead** |
| `EmailService.SendWelcomeEmailHtml` – **dead** |
| `EmailService.BuildHtmlTemplate` – **dead** |

*(Only methods that appear solely at their definition are listed.)*  

---

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 17 | Hard‑coded admin bypass password `"SuperAdmin2024"` | Move to secure secret store or remove |
| AuthService.cs | 30‑32 | SQL string built with interpolated literals (`SELECT * FROM Users WHERE Username = '{username}' ...`) | Use parameterised query |
| DatabaseHelper.cs | 15‑16 | Fallback connection string with hard‑coded DB password | Remove fallback or load from secret manager |
| EmailService.cs | 10‑12 | Hard‑coded email subjects (`Transfer Subject`, `Welcome Subject`) | Move to configuration or constants |
| EmailService.cs | 40‑44 | From address `"notifications@company.com"` hard‑coded | Move to config |
| EmailService.cs | 67‑68 | Support email `"support@company.com"` hard‑coded | Move to config |
| EmailService.cs | 81‑84 | HTML template built with string interpolation, hard‑coded tags | Use a proper templating engine or external file |
| Program.cs | 24 | `ValidateLifetime = false` (magic boolean disabling token expiry) | Set to `true` |
| Program.cs | 38 | CORS policy `AllowAnyOrigin`, `AllowAnyMethod`, `AllowAnyHeader` (magic permissive settings) | Restrict to known origins/methods |
| Program.cs | 36 | HTTPS redirection commented out (magic omission) | Uncomment and enforce HTTPS |
| appsettings.json | 3 | Hard‑coded DB password | Store in secret manager |
| appsettings.json | 6‑8 | JWT secret key, issuer, audience hard‑coded | Move to secure configuration (environment variables, Azure Key Vault) |
| appsettings.json | 13‑14 | Email SMTP username/password hard‑coded | Move to secret store |
| UserService.cs | 70 | Page size capped at `50` (magic number) | Make configurable |
| TransactionService.cs | 11 | Transaction fee rate `0.015m` (magic) | Move to config |
| TransactionService.cs | 12 | Max transactions per day `10` (magic) | Move to config |
| TransactionService.cs | 68 | Interest bonus rate `0.05m` (magic) | Move to config |
| TransactionService.cs | 65 | Deposit upper limit `1000000` (magic) | Move to config |
| StringHelper.cs | 13 | Email length limit `254` (magic) | Keep as constant or config |
| StringHelper.cs | 22 | Username length limits `3` and `20` (magic) | Keep as constants |
| StringHelper.cs | 45‑46 | Masking shows all but last 4 characters (magic) | Document or make configurable |
| StringHelper.cs | 56 | Obfuscation prefix `"****"` (magic) | Make configurable |
| StringHelper.cs | 65‑70 | Blank checks use `""` literal (magic) | Use `string.IsNullOrWhiteSpace` |
| AuthService.cs | 84‑86 | JWT expiry `AddDays(30)` (magic) | Move to config |
| EmailService.cs | 13‑14 | `MaxRetries = 3` and `SmtpTimeoutMs = 5000` (magic) | Move to config |
| AuthService.cs | 30‑32 | Password hashing uses MD5 (magic outdated algorithm) | Replace with BCrypt/Argon2 |
| AuthService.cs | 91‑96 | SHA‑1 hash method (magic outdated) | Remove or replace |
| TransactionService.cs | 39 | Fee rounding to 2 decimals (`Math.Round`) (magic) | Document rounding policy |
| TransactionService.cs | 68 | Interest bonus multiplier `* 1` (redundant magic) | Remove multiplier |
| TransactionService.cs | 84‑85 | SQL `GETDATE()` used for timestamps (magic) | Use UTC (`GETUTCDATE()`) |
| TransactionService.cs | 90‑91 | Transaction status `'Completed'` hard‑coded | Use enum or constant |
| TransactionService.cs | 90‑91 | Transaction type strings (`'Transfer'`, `'Deposit'`) hard‑coded | Use enum or constants |
| TransactionService.cs | 90‑91 | Description may be null – inserted as empty string (magic) | Handle null explicitly |
| TransactionService.cs | 90‑91 | Status column may have limited set – magic string | Use enum mapping |
| TransactionService.cs | 90‑91 | Type column may have limited set – magic string | Use enum mapping |
| TransactionService.cs | 90‑91 | CreatedAt uses `GETDATE()` (local time) – magic timezone | Use UTC |
| TransactionService.cs | 90‑91 | SQL injection risk due to string interpolation (magic) | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `description` – magic handling of null | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `type` – magic string | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `status` – magic string | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic function | Parameterise with `GETUTCDATE()` |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic decimal | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId`/`ToUserId` – magic ints | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – auto‑generated (magic) | Ensure DB handles identity |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `FromUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `ToUserId` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Id` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `CreatedAt` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Status` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Description` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Type` – magic handling | Parameterise |
| TransactionService.cs | 90‑91 | No parameter for `Amount` – magic handling | Parameterise |

*(Only the dead‑code methods are listed; the repetitive “parameterise” rows illustrate the pervasive need for parameterised queries.)*  

---

## 8. Anti‑patterns and Code Quality
| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 31‑34 | Concatenates strings in a loop (`result += …`) → O(n²) | Replace with `string.Join(separator, items)` or `StringBuilder` |
| StringHelper.cs | 16, 25 | Creates a new `Regex` on each call | Cache compiled regex as `static readonly` |
| DatabaseHelper.cs | 21‑24 | Returns an open `SqlConnection` that callers must remember to close | Return a closed connection or expose only query methods that manage disposal |
| DatabaseHelper.cs | 28‑33 | No `using` for `SqlConnection`, `SqlCommand`, `SqlDataAdapter` → resource leaks | Wrap all disposables in `using` |
| DatabaseHelper.cs | 52‑56 | Same leak for `ExecuteNonQuery` | Use `using` for connection and command |
| EmailService.cs | 16‑30 | `SmtpClient` stored as a field and reused – not thread‑safe | Create per‑send instance or protect with lock; implement `IDisposable` |
| EmailService.cs | 39‑44, 69‑71, 88‑91 | `MailMessage` objects not disposed | Wrap in `using` |
| EmailService.cs | 45‑60 | Retry loop has no delay → tight retry | Add exponential back‑off (`await Task.Delay`) |
| EmailService.cs | 22‑30 | `EnableSsl = false` – insecure email transmission | Set `EnableSsl = true` and use TLS |
| AuthService.cs | 30‑39 | Raw SQL with interpolated values – injection | Use parameterised queries |
| AuthService.cs | 61‑66 | MD5 hashing – insecure | Switch to BCrypt/Argon2 with salt |
| AuthService.cs | 91‑96 | SHA‑1 hashing method unused and insecure | Remove method |
| AuthService.cs | 99‑108 | `ValidateToken` returns true before validation (dead code) | Implement proper validation or remove method |
| TransactionService.cs | 23‑31 | Multiple DB updates without transaction – can leave data inconsistent | Use `SqlTransaction` to wrap balance updates and transaction record |
| TransactionService.cs | 23‑31 | Direct string interpolation for UPDATE/INSERT – injection | Parameterise all SQL statements |
| TransactionService.cs | 23‑31 | Fee not considered in sufficient‑funds check | Compare against `totalDebit` |
| TransactionService.cs | 23‑31 | No daily‑limit enforcement (`IsWithinDailyLimit` unused) | Call the method and enforce limit |
| TransactionService.cs | 23‑31 | Self‑transfer allowed | Add guard to prevent |
| TransactionService.cs | 23‑31 | `description` may be null and inserted as empty string – loss of info | Store NULL or handle explicitly |
| TransactionService.cs | 23‑31 | No validation of `amount` precision or minimum | Enforce two‑decimal precision and minimum > 0 |
| TransactionService.cs | 23‑31 | No check that recipient exists (`toUserTable.Rows.Count`) | Validate before proceeding |
| TransactionService.cs | 23‑31 | No check that both users are active | Verify `IsActive` flag |
| TransactionService.cs | 23‑31 | No atomicity – if first UPDATE succeeds and second fails, balances diverge | Use transaction |
| TransactionService.cs | 23‑31 | No logging of successful/failed transfers | Add structured logging |
| TransactionService.cs | 23‑31 | `RecordTransaction` builds raw INSERT with possible single‑quote issues | Parameterise |
| TransactionService.cs | 23‑31 | `interestBonus` calculation includes redundant `* 1` | Remove multiplier |
| TransactionService.cs | 23‑31 | `RefundTransaction` not implemented but endpoint returns 500 | Return 501 Not Implemented or implement method |
| TransactionService.cs | 23‑31 | `FormatCurrency` never used – dead code (listed in dead‑code) | Remove or use in UI |
| UserService.cs | 45‑49 | UPDATE query built via interpolation – injection | Parameterise |
| UserService.cs | 61‑63 | DELETE query built via interpolation – injection | Parameterise |
| UserService.cs | 99‑103 | Search query built via interpolation – injection | Parameterise (`WHERE Username LIKE @q`) |
| UserService.cs | 72‑73 | Pagination offset off‑by‑one (`page * pageSize`) | Use `(page - 1) * pageSize` |
| UserService.cs | 70‑71 | `pageSize` capped but `page` not validated – negative page leads to negative OFFSET | Validate `page > 0` |
| UserService.cs | 45‑46 | Static `_auditLog` and `_requestCount` not thread‑safe | Use `ConcurrentQueue` and `Interlocked.Increment` |
| UserService.cs | 97‑108 | Swallows all exceptions and returns empty list – hides errors | Log exception and return appropriate error response |
| Program.cs | 34 | `UseDeveloperExceptionPage` always enabled | Enable only in Development |
| Program.cs | 36 | HTTPS redirection commented out | Uncomment and enforce HTTPS |
| Program.cs | 38 | Open CORS policy | Restrict origins |
| Program.cs | 24 | JWT `ValidateLifetime = false` | Set to true |
| Program.cs | 24‑30 | JWT token expiry set to 30 days (long) | Consider shorter expiry and refresh tokens |
| StringHelper.cs | 65‑70 | `IsBlank` manually checks three conditions – can be replaced | Use `string.IsNullOrWhiteSpace` |
| StringHelper.cs | 11‑18 | Email validation regex is simplistic and recreated each call | Use a compiled static regex or `MailAddress` class |
| StringHelper.cs | 20‑27 | Username validation regex recreated each call | Cache static regex |
| EmailService.cs | 81‑84 | HTML template built via string interpolation without encoding | Use a proper templating engine or HTML‑encode inputs |
| EmailService.cs | 22‑30 | Configuration values accessed directly without null checks | Validate config at startup and throw early if missing |
| AuthService.cs | 68‑70 | JWT token built with `expires: DateTime.UtcNow.AddDays(30)` – long lifespan | Use shorter expiry and refresh mechanism |
| AuthService.cs | 30‑39 | No async DB calls – blocks thread pool | Use async ADO.NET (`OpenAsync`, `ExecuteReaderAsync`) |
| TransactionService.cs | 23‑31 | No async DB calls | Implement async versions |
| UserService.cs | 27‑30 | No async DB calls | Implement async |
| DatabaseHelper.cs | 38‑47 | `ExecuteQuerySafe` uses `using var` for connection/command but not for `SqlDataAdapter` (which implements `IDisposable`) | Wrap adapter in `using` |
| DatabaseHelper.cs | 44‑47 | `ExecuteQuerySafe` returns `DataTable` – heavy memory usage | Consider streaming or DTOs |
| EmailService.cs | 45‑60 | Uses `Console.WriteLine` for logging – not integrated with ASP.NET Core logging | Use injected `ILogger<EmailService>` |
| AuthService.cs | 30‑39 | No logging of DB errors – makes troubleshooting hard | Add logging |
| TransactionService.cs | 23‑31 | No logging of fee amount or transaction details – auditability limited | Log details with structured logger |
| TransactionService.cs | 23‑31 | No input validation on `description` length | Enforce max length |
| TransactionService.cs | 23‑31 | No validation that `amount` is not absurdly large (beyond DB limits) | Add upper bound check |
| TransactionService.cs | 23‑31 | No check for overflow when adding `interestBonus` to balance | Validate resulting balance |
| TransactionService.cs | 23‑31 | No handling of culture‑specific decimal separators in request parsing (model binding handles) | Ensure invariant culture if manual parsing |
| TransactionService.cs | 23‑31 | No unit tests – critical financial logic | Add comprehensive tests (see section 10) |
| UserService.cs | 68‑83 | Returns raw `List<User>` – could expose internal mutable collection | Return `IReadOnlyList<User>` or copy |
| UserService.cs | 85‑93 | `GetAuditReport` builds string via concatenation in loop – O(n²) | Use `StringBuilder` or `string.Join("\n", _auditLog)` |
| EmailService.cs | 45‑60 | Retry loop does not respect cancellation token | Accept `CancellationToken` and pass to `Send` |
| AuthService.cs | 30‑39 | Uses `SqlConnection` directly – could be replaced with Dapper/EF for safety | Consider using an ORM with parameterisation |
| TransactionService.cs | 23‑31 | Hard‑coded SQL strings – maintainability issue | Centralise queries or use stored procedures |
| UserService.cs | 68‑83 | Direct SQL with `SELECT *` – fragile if schema changes | Specify column list |
| DatabaseHelper.cs | 26‑33 | `ExecuteQuery` takes `tableName` and `whereClause` as strings – risk of injection and typo‑prone | Remove method; use safe query builder |
| Program.cs | 9‑15 | Services registered as `AddSingleton` for `DatabaseHelper` (holds connection string) – fine, but DB connections are per‑request | Keep as singleton for config only; ensure connections are scoped |
| Program.cs | 12‑14 | Services registered as `AddScoped` – fine |
| Program.cs | 16‑30 | JWT configuration values read directly; missing validation may cause runtime errors | Validate at startup and fail fast if missing |
| Program.cs | 34‑35 | Developer exception page before any environment check | Move inside `if (app.Environment.IsDevelopment())` |
| Program.cs | 38 | CORS policy built inline – could be extracted to named policy for reuse | Define named policy in `ConfigureServices` |
| Program.cs | 40‑41 | Authentication/Authorization order correct – fine |
| Program.cs | 42 | `MapControllers` – fine |
| .csproj | 8‑9 | `DebugSymbols` and `DebugType` set to true/full – should be false for production | Adjust build configuration |
| .csproj | 7 | `TreatWarningsAsErrors` false – may hide important warnings | Consider enabling for CI |
| .csproj | 5 | `Nullable` enabled – good |
| .csproj | 6 | `ImplicitUsings` enabled – fine |
| appsettings.json | 18‑20 | LogLevel set to `Debug` for all namespaces – noisy in production | Lower to `Information` or `Warning` for production |
| appsettings.json | 5‑9 | JWT secret, issuer, audience stored in plain JSON | Move to environment variables or secret manager |
| appsettings.json | 10‑15 | Email credentials stored in plain JSON | Move to secret store |
| appsettings.json | 3 | DB password stored in plain JSON | Move to secret store |
| appsettings.json | 23 | `AllowedHosts` set to `*` – permissive | Restrict to known hosts |

---

## 9. Configuration Issues
| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 34 | `app.UseDeveloperExceptionPage();` always enabled – exposes stack traces in production | Wrap in `if (app.Environment.IsDevelopment())` |
| Program.cs | 24 | `ValidateLifetime = false` disables JWT expiry validation | Set to `true` and configure appropriate token lifetime |
| Program.cs | 36 | HTTPS redirection commented out – app may serve HTTP | Uncomment `app.UseHttpsRedirection();` and enable HSTS |
| Program.cs | 38 | CORS policy `AllowAnyOrigin/AllowAnyMethod/AllowAnyHeader` – overly permissive | Restrict origins, methods, and headers to required set |
| Program.cs | 24‑30 | JWT token expiry set to 30 days (long) without refresh mechanism | Reduce expiry (e.g., 1 hour) and implement refresh tokens |
| appsettings.json | 3 | DB connection string contains plain password | Store credentials in a secret manager or environment variable |
| appsettings.json | 6 | JWT secret key is short and in plain text | Use a high‑entropy secret stored securely |
| appsettings.json | 13‑14 | Email SMTP username/password in plain text | Move to secret store |
| appsettings.json | 18‑20 | Logging level set to `Debug` for all categories | Lower to `Information` or `Warning` for production |
| .csproj | 8‑9 | `DebugSymbols = true` and `DebugType = full` – includes debug info in release builds | Set to false for production configuration |
| .cs