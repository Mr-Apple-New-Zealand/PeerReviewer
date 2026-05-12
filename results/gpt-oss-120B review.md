**Code Review Report – branch `gpt-oss-120B` (commit `ccc6a3d5cfe4eae99739eb196fd8b8374fa5d30e`)**

---

## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `AuthService.cs` | 31 | SQL built with string interpolation using raw `username` → SQL injection risk | Use parameterized query (`@username`) with `SqlCommand.Parameters` |
| `AuthService.cs` | 31 | Password hashed with MD5 – weak, fast hash | Replace with a strong password hash (e.g., PBKDF2, Argon2, BCrypt) |
| `AuthService.cs` | 23 | Hard‑coded admin bypass password | Remove backdoor; enforce normal authentication only |
| `AuthService.cs` | 71 | `ValidateLifetime = false` disables token expiry validation | Set `ValidateLifetime = true` and configure reasonable token lifetime |
| `Program.cs` | 30 | JWT secret key read from config but stored in plain text in `appsettings.json` | Move secret to environment variable or secret manager |
| `Program.cs` | 38 | `UseDeveloperExceptionPage()` enabled unconditionally → detailed errors in production | Enable only in Development environment |
| `Program.cs` | 41 | HTTPS redirection commented out → traffic may be plain HTTP | Uncomment `app.UseHttpsRedirection();` |
| `Program.cs` | 44 | CORS policy `AllowAnyOrigin/Method/Header` → open to CSRF | Restrict origins, methods, and headers to required set |
| `DatabaseHelper.cs` | 13 | Fallback connection string contains hard‑coded DB credentials | Remove fallback or load credentials securely |
| `appsettings.json` | 5‑9 | Database password, JWT secret, and email credentials stored in source control | Move all secrets to environment variables or secret store |
| `EmailService.cs` | 15‑18 | SMTP credentials (username/password) read from config in plain text | Secure via secret manager; avoid storing in repo |
| `EmailService.cs` | 23 | `EnableSsl = false` – sends credentials in clear text | Set `EnableSsl = true` and use TLS |
| `UserService.cs` | 55 | SQL built with string interpolation for `email` and `username` → injection | Use parameterized queries |
| `UserService.cs` | 84 | SQL built with string interpolation for `DELETE` → injection | Use parameterized query |
| `UserService.cs` | 100 | `ExecuteQuery` used with raw `WHERE` clause containing user input → injection | Replace with `ExecuteQuerySafe` and parameters |
| `TransactionService.cs` | 31‑33 | `ExecuteNonQuery` called with interpolated balances → injection if values tampered | Use parameters for all SQL statements |
| `TransactionService.cs` | 71 | No check that `fromUserId != toUserId` → self‑transfer may be abused | Add guard against self‑transfer |
| `TransactionService.cs` | 78 | Fee not considered in balance check (`fromBalance >= amount` instead of `>= totalDebit`) → possible overdraft | Compare against `totalDebit` |
| `TransactionService.cs` | 86 | No daily‑transaction limit enforcement (`IsWithinDailyLimit` never called) | Call `IsWithinDailyLimit` before proceeding |
| `TransactionService.cs` | 115 | `description` inserted directly into SQL without escaping → injection if contains `'` | Parameterize `description` field |
| `TransactionService.cs` | 124 | `RefundTransaction` throws `NotImplementedException` but endpoint returns 500 with generic message | Implement proper handling or return 501 Not Implemented |
| `StringHelper.cs` | 13‑16 | `Regex` compiled on each call → potential DoS via complex patterns | Cache compiled regex as `static readonly` |
| `StringHelper.cs` | 23‑27 | `JoinWithSeparator` builds string via repeated concatenation → O(n²) | Replace with `string.Join` (already provided) and remove this method |
| `EmailService.cs` | 9‑11 | `SmtpClient` is a disposable field never disposed → resource leak & possible socket exhaustion | Dispose `SmtpClient` (e.g., via `IAsyncDisposable` or create per‑send) |
| `EmailService.cs` | 31‑34 | `MailMessage` objects not disposed | Wrap in `using` statements |
| `DatabaseHelper.cs` | 23‑28 | `ExecuteQuery` opens connection and never disposes it | Use `using` for `SqlConnection`, `SqlCommand`, and `SqlDataAdapter` |
| `DatabaseHelper.cs` | 41‑45 | `ExecuteNonQuery` opens connection via `GetOpenConnection` but never disposes connection/command | Use `using` and dispose both |
| `DatabaseHelper.cs` | 55‑61 | `ExecuteQuerySafe` does not dispose `SqlDataAdapter` | Wrap adapter in `using` |
| `AuthService.cs` | 45‑53 | `SqlConnection`, `SqlCommand`, and `SqlDataReader` not disposed | Use `using` statements |
| `AuthService.cs` | 66‑71 | `ValidateToken` returns `true` before any validation, making token validation ineffective | Remove early `return true;` and implement proper validation |

---

## 2. Logic Errors
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `TransactionService.cs` | 78‑80 | Balance check ignores transaction fee (`fromBalance >= amount`); fee can cause negative balance | Change condition to `fromBalance >= totalDebit` |
| `TransactionService.cs` | 71‑73 | No guard against transferring to self (`fromUserId == toUserId`) | Add `if (fromUserId == toUserId) return (false, "Cannot transfer to yourself");` |
| `TransactionService.cs` | 84‑86 | Daily transaction limit (`IsWithinDailyLimit`) defined but never used | Call `IsWithinDailyLimit` before performing transfer |
| `UserService.cs` | 108‑110 | Pagination offset calculated as `page * pageSize` (0‑based) → skips first page | Compute `skip = (page - 1) * pageSize` and validate `page >= 1` |
| `AuthService.cs` | 71‑78 | `ValidateToken` returns `true` for any non‑empty token, bypassing expiry check | Remove early return and evaluate `jwtToken.ValidTo` |
| `AuthService.cs` | 23‑27 | Admin bypass password grants full access without hashing or audit | Remove backdoor; enforce normal login flow |
| `TransactionService.cs` | 115‑119 | `description` may be `null`; inserted into SQL as `'null'` string → possible data inconsistency | Pass `NULL` via parameter when description is null |
| `TransactionService.cs` | 124‑128 | `RefundTransaction` not implemented but controller catches `NotImplementedException` and returns 500 → misleading error | Implement refund logic or return 501 Not Implemented |
| `UserService.cs` | 55‑57 | `GetUserById` throws `ArgumentException` for invalid IDs; API returns 500 instead of 400 | Return `BadRequest` from controller or avoid throwing |
| `UserService.cs` | 71‑73 | `_requestCount` incremented but never used → unnecessary state | Remove or expose for monitoring |
| `UserService.cs` | 84‑86 | `_auditLog` is static but not thread‑safe; concurrent writes may corrupt list | Use concurrent collection (`ConcurrentBag`) or lock |
| `EmailService.cs` | 23‑27 | `SmtpClient` reused across calls without synchronization; not thread‑safe | Create a new `SmtpClient` per send or protect with lock |
| `StringHelper.cs` | 23‑27 | `JoinWithSeparator` adds trailing separator and is O(n²) | Replace with `string.Join(separator, items)` (already provided) |
| `TransactionService.cs` | 108‑110 | `interestBonus = amount * 0.05m * 1` – the `* 1` is redundant and may confuse readers | Remove unnecessary multiplication |
| `TransactionService.cs` | 112‑113 | Deposit adds `amount + interestBonus` directly; no check for overflow or daily limit | Validate resulting balance and enforce limits |

---

## 3. Error Handling
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `AuthService.cs` | 45‑53 | Database objects opened but not wrapped in try/catch; exceptions bubble and connections stay open | Use `using` and catch `SqlException` to return null or proper error |
| `TransactionService.cs` | 31‑84 | No transaction scope; two `UPDATE` statements can leave accounts inconsistent on failure | Wrap updates in a DB transaction (`BEGIN TRANSACTION` / `COMMIT`) |
| `TransactionService.cs` | 31‑84 | No catch for database errors; unhandled exceptions return 500 without context | Add try/catch, log error, return appropriate `BadRequest` |
| `TransactionService.cs` | 115‑119 | `description` may be null; inserting directly may cause SQL error | Parameterize and allow null values |
| `EmailService.cs` | 31‑44 | Swallows `SmtpException` after max retries and rethrows generic exception; controller returns 500 with no details | Return a specific error object or status code (e.g., 503 Service Unavailable) |
| `EmailService.cs` | 55‑61 | Catches generic `Exception` and only writes to console; error lost to caller | Propagate exception or return result indicating failure |
| `UserService.cs` | 100‑108 | `SearchUsers` catches all exceptions and returns empty list, hiding failures | Log exception and return appropriate error response |
| `UserService.cs` | 55‑57 | Throws `ArgumentException` for invalid IDs; controller does not handle, leading to 500 | Validate inputs in controller and return `BadRequest` |
| `AuthService.cs` | 71‑78 | `ValidateToken` returns early, making later validation unreachable (logic error) | Remove early return and handle validation properly |
| `Program.cs` | 38‑40 | JWT configuration missing `ValidateLifetime`; tokens never expire, increasing risk if stolen | Set `ValidateLifetime = true` and configure reasonable clock skew |
| `DatabaseHelper.cs` | 23‑28 | `ExecuteQuery` does not catch SQL errors; caller may receive empty table without knowing why | Add try/catch, log, and rethrow or return error indicator |
| `DatabaseHelper.cs` | 41‑45 | `ExecuteNonQuery` returns rows affected but does not handle exceptions | Wrap in try/catch and log failures |

---

## 4. Resource Leaks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `AuthService.cs` | 45‑53 | `SqlConnection`, `SqlCommand`, `SqlDataReader` never disposed | Use `using` statements for all three |
| `DatabaseHelper.cs` | 23‑28 | Connection opened, never closed/disposed | Wrap connection, command, and adapter in `using` |
| `DatabaseHelper.cs` | 41‑45 | `ExecuteNonQuery` returns open connection without disposing it | Dispose connection and command via `using` |
| `DatabaseHelper.cs` | 55‑61 | `SqlDataAdapter` not disposed | Wrap in `using` |
| `EmailService.cs` | 15‑23 | `SmtpClient` stored as field and never disposed | Implement `IDisposable` on `EmailService` and dispose client, or create per‑send |
| `EmailService.cs` | 31‑34, 55‑61 | `MailMessage` objects not disposed | Use `using (var message = new MailMessage(...))` |
| `UserService.cs` | 100‑108 | `ExecuteQuery` leaks connection (see above) | Fix in `DatabaseHelper` |
| `Program.cs` | 38‑40 | `JwtBearer` options create `SymmetricSecurityKey` each request; not a leak but could be cached | Cache the key if performance is a concern |
| `TransactionService.cs` | 31‑84 | No transaction scope; if one `UPDATE` succeeds and the other fails, DB resources stay locked | Use `SqlTransaction` and ensure disposal |

---

## 5. Null Reference Risks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `AuthService.cs` | 31 | `username` or `password` could be null, leading to `HashPasswordMd5(null)` → exception | Validate inputs before use |
| `AuthService.cs` | 71 | `_config["Jwt:SecretKey"]!` assumes non‑null; missing key throws `ArgumentNullException` | Add null check and fallback error |
| `TransactionService.cs` | 71‑73 | `fromUserTable.Rows[0]` accessed without verifying `Rows.Count > 0` → possible `IndexOutOfRangeException` | Check `Rows.Count` before accessing |
| `TransactionService.cs` | 71‑73 | `toUserTable.Rows[0]` same risk | Add guard |
| `TransactionService.cs` | 84‑86 | `description` may be null; passed to `RecordTransaction` which builds SQL string with `'null'` → may cause error | Parameterize and allow null |
| `TransactionService.cs` | 95‑99 | Email address retrieved from DB may be null; passed to `SendTransferNotification` → `MailMessage` throws | Validate email before sending |
| `EmailService.cs` | 15‑18 | Config values (`Email:SmtpHost`, `Email:SmtpPort`, etc.) may be null; `int.Parse(null)` throws | Validate config and provide defaults or error |
| `UserService.cs` | 55‑57 | `id` validated but `email` and `username` may be null; SQL string will contain `null` literal | Validate parameters before building query |
| `UserService.cs` | 100‑108 | `query` could be null; `ExecuteQuery` builds `LIKE '%{query}%'` → results in `LIKE '%null%'` | Guard against null or treat as empty string |
| `StringHelper.cs` | 45‑48 | `accountNumber` may be null; `accountNumber.Length` throws | Add null check |
| `StringHelper.cs` | 55‑58 | `account` may be null; `account[^4..]` throws | Validate before slicing |
| `StringHelper.cs` | 61‑63 | `input` may be null; `input.ToLower()` throws | Add null guard |
| `StringHelper.cs` | 71‑75 | `value` may be null; `value.Trim()` throws if not checked earlier | Already checks null, but `value == ""` could be replaced with `string.IsNullOrWhiteSpace` |

---

## 6. Dead Code
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `AuthService.cs` | 71‑78 | `return true;` makes subsequent token validation unreachable | Remove early return and keep validation logic |
| `TransactionService.cs` | 108‑110 | `IsWithinDailyLimit` defined but never called | Either call it where needed or remove it |
| `TransactionService.cs` | 124‑126 | `FormatCurrency` never used | Remove or use in responses |
| `DatabaseHelper.cs` | 71‑81 | `ExecuteQueryWithParams` marked `[Obsolete]` but still present and unused | Delete method or replace all callers with `ExecuteQuerySafe` |
| `AuthService.cs` | 64‑66 | `HashPasswordSha1` never used | Remove method |
| `EmailService.cs` | 71‑73 | `BuildHtmlTemplate` used only by `SendWelcomeEmailHtml`; if that method is never called, the helper is dead | Verify usage; if unused, remove |
| `Program.cs` | 41‑44 | CORS policy defined but may be overridden elsewhere; not dead but could be refined | No immediate action needed |
| `StringHelper.cs` | 23‑27 | `JoinWithSeparator` is inefficient and not used elsewhere (fixed version exists) | Delete method |

---

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `DatabaseHelper.cs` | 13 | Fallback connection string hard‑codes DB password | Move to secure config |
| `AuthService.cs` | 23 | `AdminBypassPassword` hard‑coded | Remove backdoor |
| `AuthService.cs` | 71 | JWT secret key read from config but key length is short (`mysecretkey`) | Use a longer, randomly generated secret |
| `EmailService.cs` | 9‑11 | Email subjects and from address hard‑coded | Move to config or constants |
| `TransactionService.cs` | 13 | `TransactionFeeRate = 0.015m` magic fee rate | Define as configurable setting |
| `TransactionService.cs` | 14 | `MaxTransactionsPerDay = 10` magic limit | Move to config |
| `UserService.cs` | 108 | Page size capped at 50 (magic) | Expose as configurable constant |
| `Program.cs` | 44 | CORS `AllowAnyOrigin/Method/Header` magic permissive settings | Restrict to known origins |
| `Program.cs` | 38‑40 | JWT `ValidateLifetime = false` (magic) | Set to true |
| `StringHelper.cs` | 13‑16 | Email regex pattern hard‑coded | Consider moving to constant if reused |
| `StringHelper.cs` | 20‑23 | Username regex pattern hard‑coded | Same as above |
| `appsettings.json` | 5‑9 | Database password, JWT secret, email credentials hard‑coded | Store in environment variables or secret manager |
| `appsettings.json` | 12‑14 | JWT `Issuer` and `Audience` hard‑coded strings | Keep but ensure they match production values |
| `appsettings.json` | 19‑22 | Email SMTP host/port hard‑coded | Move to secure config if varies per environment |

---

## 8. Anti‑patterns and Code Quality
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `StringHelper.cs` | 23‑27 | Concatenates strings in a loop → O(n²) | Use `string.Join` (already provided) or `StringBuilder` |
| `StringHelper.cs` | 13‑16, 20‑23 | Compiles new `Regex` on each call | Cache compiled regex as `static readonly` |
| `DatabaseHelper.cs` | 23‑28, 41‑45 | Direct string interpolation for SQL → injection risk & no disposal | Use parameterized queries and `using` |
| `DatabaseHelper.cs` | 55‑61 | `ExecuteQuerySafe` creates `SqlDataAdapter` without disposing | Wrap in `using` |
| `AuthService.cs` | 45‑53 | Manual ADO.NET handling instead of async/EF Core | Consider using async EF Core for readability and safety |
| `TransactionService.cs` | 31‑84 | No transaction scope; two separate `UPDATE`s can leave data inconsistent | Use `SqlTransaction` or `TransactionScope` |
| `UserService.cs` | 55‑86 | Static mutable `_auditLog` and `_requestCount` not thread‑safe | Replace with thread‑safe collections or lock |
| `EmailService.cs` | 15‑23 | Reuses non‑thread‑safe `SmtpClient` across requests | Create per‑send or protect with lock |
| `Program.cs` | 38‑40 | JWT validation disables lifetime check | Configure correctly |
| `Program.cs` | 41‑44 | Open CORS policy | Restrict origins |
| `AuthService.cs` | 23‑27 | Hard‑coded admin bypass – security anti‑pattern | Remove |
| `TransactionService.cs` | 115‑119 | Inserts raw `description` into SQL without sanitization | Parameterize |
| `UserService.cs` | 100‑108 | Swallows all exceptions in `SearchUsers` and returns empty list | Log and propagate appropriate error |
| `TransactionService.cs` | 108‑110 | `IsWithinDailyLimit` never used – dead code | Remove or integrate |

---

## 9. Configuration Issues
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `Program.cs` | 38 | `UseDeveloperExceptionPage()` enabled for all environments | Wrap in `if (app.Environment.IsDevelopment())` |
| `Program.cs` | 41 | `ValidateLifetime = false` in JWT options | Set to `true` |
| `Program.cs` | 44 | CORS policy `AllowAnyOrigin/Method/Header` – overly permissive | Restrict to specific origins and methods |
| `Program.cs` | 41 | HTTPS redirection commented out | Uncomment `app.UseHttpsRedirection();` |
| `appsettings.json` | 5‑9 | Secrets (DB password, JWT secret, email password) stored in source control | Move to environment variables or secret manager |
| `appsettings.json` | 12‑14 | JWT `Issuer`/`Audience` hard‑coded but may differ per environment | Use per‑environment config files |
| `appsettings.json` | 19‑22 | Email SMTP credentials in plain text | Secure via secret store |
| `SampleBankingApp.csproj` | 13‑15 | `DebugSymbols=true` and `DebugType=full` in production build | Set to `false` for Release |
| `SampleBankingApp.csproj` | 13‑15 | `TreatWarningsAsErrors=false` – may hide important warnings | Consider enabling for CI |
| `SampleBankingApp.csproj` | 13‑15 | `Nullable=enable` – good, but ensure all code respects nullability | Review warnings |
| `Program.cs` | 38‑40 | Logging level set to `Debug` for all categories in `appsettings.json` | Reduce to `Information` or `Warning` for production |
| `Program.cs` | 38‑40 | No rate‑limiting or lockout on login endpoint | Add ASP.NET Core rate limiting middleware |
| `Program.cs` | 38‑40 | No HSTS header configuration | Add `app.UseHsts();` for production |

---

## 10. Missing Unit Tests
| File | Line | Issue | Fix |
|------|------|-------|-----|
| (entire project) | – | No test project present in the solution | Add an xUnit/NUnit/MSTest project `SampleBankingApp.Tests` |
| `AuthService.cs` | 31‑53 | Login logic (SQL injection, password hashing, admin bypass) needs tests for valid/invalid credentials, injection attempts, and admin path | Write unit tests covering success, failure, and security edge cases |
| `AuthService.cs` | 71‑78 | `ValidateToken` always returns true – test token validation, expiry, and signature | Add tests for valid, expired, and tampered tokens |
| `TransactionService.cs` | 31‑84 | Transfer flow – balance checks, fee calculation, self‑transfer guard, daily limit, atomicity | Unit tests for sufficient/insufficient funds, fee deduction, self‑transfer rejection, and transaction limit |
| `TransactionService.cs` | 95‑103 | Deposit – amount bounds, interest bonus, balance update | Tests for valid deposit, exceeding max amount, and negative amount |
| `UserService.cs` | 108‑110 | Pagination – correct `skip` calculation, page size cap, empty result handling | Tests for first page, middle page, page beyond range |
| `UserService.cs` | 100‑108 | SearchUsers – SQL injection risk, empty query handling | Tests ensuring query is escaped/parameterized and that null/empty queries behave correctly |
| `StringHelper.cs` | 13‑16, 20‑23 | Email and username validation regexes – valid and invalid inputs | Parameterized tests for edge cases |
| `StringHelper.cs` | 23‑27 | `JoinWithSeparator` inefficiency (optional) – correctness of output | Test that result matches `string.Join` |
| `EmailService.cs` | 31‑44, 55‑61 | Email sending – retry logic, exception handling, proper disposal | Mock `SmtpClient` and verify retries and disposal |
| `DatabaseHelper.cs` | 23‑28, 41‑45 | ExecuteQuery / ExecuteNonQuery – proper disposal and error handling | Integration tests with an in‑memory DB or mock to ensure connections close |
| `Program.cs` | 38‑40 | JWT configuration – token lifetime validation, CORS policy | Tests that middleware is configured as expected (can be done via integration test) |

*All critical paths (authentication, transaction processing, user management, and configuration) should have unit/integration tests covering success, failure, and security edge cases.*