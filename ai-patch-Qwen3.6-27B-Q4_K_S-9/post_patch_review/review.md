## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 9‑13 | Fallback connection string contains hard‑coded SA credentials. | Remove fallback; require connection string via configuration only. |
| AuthService.cs | 45‑48 | Passwords hashed with plain SHA‑256 and no salt, making them vulnerable to rainbow‑table attacks. | Use a salted password hash algorithm such as PBKDF2, bcrypt or Argon2. |
| AuthService.cs | 78‑84 | `ValidateToken` only checks `ValidTo`; it does **not** validate signature, issuer, audience or expiration tolerance. | Use `TokenValidationParameters` with `ValidateIssuerSigningKey`, `ValidateIssuer`, `ValidateAudience`, and proper `ClockSkew`. |
| EmailService.cs | 5‑7 | Default “from” and support email addresses are hard‑coded. | Move addresses to configuration (e.g., `Email:FromAddress`, `Email:SupportAddress`). |
| Program.cs | 31‑33 | CORS policy allows any method and any header (overly permissive). | Restrict allowed methods/headers to only those required by the client. |
| User.cs | 4‑5 | `Password` stored as plain string; unclear if hashed, and no salting. | Store only salted hash; rename property to `PasswordHash` and never store raw passwords. |
| AuthController.cs | 15‑18 | No null‑check for `request`; a null body causes `NullReferenceException`. | Validate `request` and return `BadRequest` if null. |
| TransactionService.cs | 5‑8 | Constants for fee rate, max deposit, interest rate are hard‑coded in source. | Move these values to configuration (e.g., `AppSettings:Transaction:FeeRate`). |
| UserService.cs | 70‑71 | `MaxTransactionsPerDay` constant defined but never used (potentially missing enforcement). | Either implement the limit or remove the dead constant. |
| EmailService.cs | 9‑11 | `MaxRetries` and `SmtpTimeoutMs` are magic numbers; not configurable. | Expose via configuration. |

---

## 2. Logic Errors
| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserService.cs | 71‑73 | `GetUsersPage` does not validate `page >= 1`; negative `skip` can be passed to SQL. | Clamp `page` to a minimum of 1 or return `BadRequest` for invalid values. |
| TransactionService.cs | 119‑124 | `Deposit` updates balance without first confirming the user exists; `ExecuteNonQuerySafe` may affect 0 rows silently. | Verify the user exists (e.g., SELECT) before updating, or check rows‑affected count. |
| UserService.cs | 100‑104 | `SearchUsers` allows `query` to be null, resulting in `LIKE '%%'` which returns all users unintentionally. | Return empty result or `BadRequest` when `query` is null/empty. |
| UserService.cs | 45‑49 | `UpdateUser` always returns `true` even if no rows were updated. | Return `rowsAffected > 0` or throw if user not found. |
| UserService.cs | 55‑58 | `DeleteUser` always returns `true` regardless of outcome. | Return `rowsAffected > 0` or handle “not found”. |
| AuthController.cs | 15‑18 | Missing null‑check for `request` (see Security). | Add `if (request == null) return BadRequest();`. |
| TransactionService.cs | 5‑8 | `MaxTransactionsPerDay` constant never used, allowing unlimited transfers per day. | Implement a daily‑transfer count check or remove the constant. |
| TransactionService.cs | 140‑144 | `RefundTransaction` throws `NotImplementedException`; controller returns generic 500. | Implement refund logic or return a clear “Not Implemented” status (501). |
| TransactionService.cs | 84‑88 | Fee is rounded to 2 decimals, but total debit may exceed balance due to rounding edge cases. | Compute fee with higher precision or ensure balance check uses the same rounding. |
| TransactionService.cs | 106‑108 | Email send failure after retries bubbles up as exception; transaction already committed. | Swallow or log the exception after retries (already done) – ensure no re‑throw. |

---

## 3. Error Handling
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthController.cs | 15‑18 | Null `request` leads to unhandled `NullReferenceException`. | Validate and return `BadRequest`. |
| TransactionService.cs | 71‑92 | Generic `catch` re‑throws the exception after rollback, exposing stack trace to the controller. | Return a structured error result instead of re‑throwing. |
| TransactionService.cs | 124‑131 | No try‑catch around `ExecuteNonQuerySafe` for `Deposit`; DB errors propagate as 500. | Wrap in try‑catch and return `BadRequest` with a friendly message. |
| EmailService.cs | 30‑38 | `SendTransferNotification` re‑throws after max retries; caller may treat it as fatal. | Log the failure and swallow after retries (already done in controller). |
| EmailService.cs | 55‑63 | `SendWelcomeEmail` catches `SmtpException` and generic `Exception` then re‑throws without logging. | Log the exception before re‑throwing or convert to a domain‑specific error. |
| UserService.cs | 101‑108 | Catches generic `Exception` then re‑throws, losing original stack trace context. | Log the exception and either wrap in a custom exception or let it bubble. |
| TransactionService.cs | 30‑34 | `BeginTransaction` opens a connection that is never disposed if the caller forgets to dispose the transaction. | Return a wrapper that disposes both transaction and connection, or use `using` in caller. |
| AuthService.cs | 78‑84 | `ValidateToken` catches all exceptions and returns `false`, hiding parsing errors. | Log the exception for diagnostics. |
| TransactionService.cs | 146‑150 | `RefundTransaction` throws `NotImplementedException`; controller catches but returns generic 500. | Return `NotImplemented` (501) or a clear message. |
| UserService.cs | 45‑49 | Comment mentions fixing SQL injection but the method already uses `ExecuteNonQuerySafe`; comment is misleading. | Remove outdated comment. |

---

## 4. Resource Leaks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 30‑34 | `BeginTransaction` opens a `SqlConnection` that is never disposed; the returned `IDbTransaction` does not close the connection. | Return a disposable wrapper that disposes both transaction and connection, or expose a method that accepts an `Action<IDbTransaction>` and disposes internally. |
| EmailService.cs | 24‑27 | `MailMessage` and `SmtpClient` are correctly disposed via `using`; no leak. *(No issue – listed for completeness.)* |
| AuthService.cs | 55‑62 | `SqlConnection`, `SqlCommand`, and `SqlDataReader` are wrapped in `using`; no leak. *(No issue – listed for completeness.)* |
| TransactionService.cs | 71‑92 | Uses `DatabaseHelper.BeginTransaction` without explicit disposal of the transaction’s connection (covered above). | Ensure `using var transaction = _db.BeginTransaction();` also disposes the underlying connection (fix in DatabaseHelper). |

---

## 5. Null Reference Risks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthController.cs | 15‑18 | `request` may be null; accessing `request.Username` causes `NullReferenceException`. | Add null check and return `BadRequest`. |
| TransactionController.cs | 22‑26 | `User.FindFirst(... )?.Value` may be null; `int.TryParse` handles it, but subsequent code assumes non‑null email. | Validate email existence before using. |
| EmailService.cs | 30‑33 | `toEmail` may be null; `MailMessage` constructor will throw. | Validate `toEmail` and return/log error if null. |
| TransactionService.cs | 84‑88 | `description` can be null; passed to `RecordTransaction` which handles null via `DBNull.Value`. No risk. *(No issue.)* |
| UserService.cs | 100‑104 | `query` may be null; string interpolation yields empty string, resulting in `LIKE '%%'`. Not a null reference but may be unintended. | Return empty list or `BadRequest` when `query` is null/empty. |
| UserService.cs | 45‑49 | `email` and `username` may be null; passed to DB as parameters, potentially causing `NULL` insert. | Validate inputs before DB call. |
| AuthService.cs | 55‑62 | Casting DB columns directly (e.g., `(string)reader["Username"]`) will throw if column is `DBNull`. | Use `reader.GetString` after `IsDBNull` check or `as string`. |
| User.cs | 4‑5 | `Password` property may be null; hashing functions assume non‑null. | Ensure password is never null; store only hashed value. |
| TransactionService.cs | 119‑124 | `userId` not validated for existence before `UPDATE`. | Verify user exists or check rows‑affected. |

---

## 6. Dead Code
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 78‑84 | `ValidateToken` is never called anywhere in the project. | Remove method or integrate it into authentication pipeline. |
| TransactionService.cs | 5‑8 | `MaxTransactionsPerDay` constant is defined but never used. | Implement daily‑limit logic or delete the constant. |
| UserService.cs | 45‑49 | Comment about fixing SQL injection is outdated; method already uses parameterised query. | Remove or update comment. |
| TransactionService.cs | 146‑150 | `RefundTransaction` throws `NotImplementedException`; controller catches it but no real implementation. | Either implement refund logic or expose a proper “Not Implemented” API (501). |
| Program.cs | 24‑26 | `builder.Services.AddSingleton<DatabaseHelper>();` registers a singleton that holds a connection string with fallback credentials (see Security). While not dead, the fallback is unused in production. | Remove fallback or ensure it’s not compiled in production. |

---

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 9‑13 | Hard‑coded fallback connection string with user `sa` and password. | Move to configuration or eliminate fallback. |
| UserService.cs | 71‑73 | Page size capped at 50 via literal. | Store max page size in configuration. |
| AuthService.cs | 70‑73 | JWT expiration set to `AddDays(1)` (hard‑coded). | Make expiration configurable. |
| EmailService.cs | 5‑7 | Email subjects and addresses are literal strings. | Move to configuration (`Email:TransferSubject`, etc.). |
| UserController.cs | 30‑31, 55‑56 | Role string `"Admin"` is hard‑coded. | Use a constant or enum, optionally from config. |
| TransactionService.cs | 5‑8 | Fee rate, max deposit, interest rate are literals. | Externalise to configuration. |
| StringHelper.cs | 4‑5 | Regex patterns are literal strings. | Keep as constants (acceptable) or load from config if needed. |
| Program.cs | 30‑33 | CORS allowed origin is a literal URL. | Move to configuration (`Cors:AllowedOrigins`). |
| EmailService.cs | 9‑11 | `MaxRetries` and `SmtpTimeoutMs` are magic numbers. | Configurable via `Email:MaxRetries`, `Email:TimeoutMs`. |
| TransactionService.cs | 5‑8 | `MaxTransactionsPerDay` defined but never used (dead magic number). | Remove or implement. |

---

## 8. Anti‑patterns and Code Quality
| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 30‑34 | `BeginTransaction` leaks the underlying `SqlConnection`. | Return a disposable wrapper that disposes both transaction and connection, or use `using` in caller. |
| UserService.cs | 45‑49 | Returns `bool` always `true` without checking rows affected. | Return the actual rows‑affected count or a meaningful status. |
| UserService.cs | 55‑58 | Same issue for `DeleteUser`. | Same fix as above. |
| UserService.cs | 101‑108 | Catches generic `Exception` then re‑throws, losing original stack trace context. | Log and re‑throw preserving stack (`throw;`). |
| TransactionService.cs | 71‑92 | Generic catch re‑throws after rollback, causing 500 with stack trace. | Return a domain error object instead of re‑throwing. |
| EmailService.cs | 55‑63 | Catches exceptions, logs nothing, and re‑throws. | Add proper logging before re‑throwing. |
| TransactionService.cs | 5‑8 | Unused constant `MaxTransactionsPerDay`. | Remove or implement limit. |
| UserService.cs | 45‑49 | Comment about fixing SQL injection is misleading. | Update comment to reflect current implementation. |
| TransactionService.cs | 84‑88 | Fee rounding may cause off‑by‑cent errors; better to calculate with higher precision. | Use `Math.Round` with `MidpointRounding.AwayFromZero` or store fee in cents. |
| All services | (multiple) | Synchronous DB calls block thread pool; no async/await usage. | Convert to async ADO.NET (`ExecuteReaderAsync`, etc.) for scalability. |
| StringHelper.cs | 13‑15 | `JoinWithSeparator` simply forwards to `string.Join`; method adds no value. | Remove or make it an extension method if needed. |

---

## 9. Configuration Issues
| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 31‑33 | CORS policy permits any method and any header, which may be broader than needed. | Restrict to required methods (`GET,POST,PUT,DELETE`) and headers. |
| Program.cs | 24‑26 | `UseDeveloperExceptionPage()` is only enabled in Development – good, but no fallback for Production logging. | Ensure production uses a proper error handling middleware (e.g., `UseExceptionHandler`). |
| appsettings.json | 2‑4 | Connection string, JWT secret, email credentials are placeholders (`__SET_VIA_ENV__`). If not replaced at runtime, app will fail. | Validate presence at startup and fail fast with clear message. |
| appsettings.json | 23‑25 | `AllowedHosts` set to `"*"` – permits any host header. | Restrict to known hostnames or remove if not needed. |
| Program.cs | 27‑29 | No HSTS (`UseHsts()`) is configured for production. | Add `app.UseHsts();` when not in Development. |
| EmailService.cs | 9‑12 | SMTP host, port, username, password are read from config but not validated; missing values cause runtime errors. | Validate config values on startup and log missing settings. |
| TransactionService.cs | 5‑8 | Business constants (fee rate, interest, max deposit) are hard‑coded; cannot be tuned without recompiling. | Move to configuration (`Transaction:FeeRate`, etc.). |
| DatabaseHelper.cs | 9‑13 | Fallback connection string with credentials may be used inadvertently in production. | Remove fallback; enforce required config. |
| csproj | 9‑12 | `DebugSymbols` set to `false` and `DebugType` to `none`; makes debugging harder. | Enable symbols for development builds (`DebugSymbols` true in Debug config). |
| csproj | 7‑9 | No explicit package version for `Microsoft.AspNetCore.Authentication.JwtBearer` beyond 8.0.0; may miss security patches. | Periodically update NuGet packages and enable Dependabot. |

---

## 10. Missing Unit Tests
| File | Line | Issue | Fix |
|------|------|-------|-----|
| (none) | – | No test project exists in the repository. | Add a test project (e.g., `SampleBankingApp.Tests`) targeting .NET 8. |
| AuthService.cs | – | Critical methods `Login`, `GenerateJwtToken`, `ValidateToken` lack unit tests for success, failure, and edge cases (e.g., invalid credentials, expired token). | Write tests covering valid/invalid login, token generation, token validation, and error handling. |
| TransactionService.cs | – | `Transfer`, `Deposit`, `RefundTransaction` have no tests for balance checks, fee calculation, insufficient funds, and exception paths. | Add tests for successful transfer, self‑transfer rejection, fee correctness, insufficient balance, max‑deposit limit, and refund not implemented. |
| UserService.cs | – | `GetUserById`, `UpdateUser`, `DeleteUser`, `GetUsersPage`, `SearchUsers` lack tests for pagination boundaries, non‑existent users, validation errors, and SQL injection safety. | Write tests covering valid/invalid IDs, page‑size limits, empty search, and ensuring parameterised queries are used. |
| EmailService.cs | – | `SendTransferNotification` and `SendWelcomeEmail` have no tests for SMTP success, retries, and failure handling. | Mock `SmtpClient` and verify retry logic and exception propagation. |
| StringHelper.cs | – | Validation helpers `IsValidEmail`, `IsValidUsername`, and `MaskAccountNumber` are untested for edge cases (max length, invalid formats, short account numbers). | Add unit tests for various valid/invalid inputs. |
| Controllers (AuthController, TransactionController, UserController) | – | No integration tests for HTTP endpoints, model binding, authorization, and error responses. | Use `WebApplicationFactory` to test routes, authentication, and response codes. |
| Configuration validation | – | No tests ensure required configuration values are present and correctly parsed. | Add tests that load configuration and assert required keys exist. |

*All listed methods and scenarios should be covered with both positive and negative test cases to ensure robustness.*