**Code Review Report – Branch `gpt-oss-120B` (commit 3345fac8)**  

---

## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 22 | SQL query built with string interpolation → SQL injection risk. | Use parameterised `SqlCommand` with `@Username` and `@Password`. |
| AuthService.cs | 24 | Password hashed with MD5 – weak, unsalted. | Switch to a strong algorithm (e.g., PBKDF2, BCrypt, Argon2) with a per‑user salt. |
| AuthService.cs | 30 | Hard‑coded admin bypass password. | Remove back‑door; enforce normal authentication only. |
| Program.cs | 30 | `ValidateLifetime = false` disables JWT expiry validation. | Set `ValidateLifetime = true` and configure reasonable clock skew. |
| Program.cs | 12 | `UseDeveloperExceptionPage()` always enabled – exposes stack traces. | Enable only in Development environment (`if (app.Environment.IsDevelopment())`). |
| Program.cs | 15 | HTTPS redirection commented out – traffic may be plain HTTP. | Uncomment `app.UseHttpsRedirection();`. |
| Program.cs | 17 | CORS policy `AllowAnyOrigin/Method/Header` – overly permissive. | Restrict origins to known clients and limit methods/headers. |
| appsettings.json | 3 | Connection string contains hard‑coded SA password. | Move credentials to a secret store / environment variable; never commit passwords. |
| appsettings.json | 12 | JWT secret key hard‑coded in source. | Store secret in a secure vault or environment variable. |
| appsettings.json | 18 | Email SMTP credentials hard‑coded. | Move to secret store; enable TLS (`EnableSsl = true`). |
| EmailService.cs | 13 | `EnableSsl = false` – sends credentials in clear text. | Set `EnableSsl = true` and use STARTTLS/SMTPS. |
| DatabaseHelper.cs | 22 | `ExecuteQuery` builds SQL from `tableName` and `whereClause` via interpolation → injection. | Validate identifiers and use parameters for `whereClause`. |
| DatabaseHelper.cs | 33 | `ExecuteNonQuery` uses interpolated SQL → injection. | Use parameterised commands. |
| TransactionService.cs | 30 | `Transfer` updates balances with interpolated SQL → injection. | Use parameters for new balances and IDs. |
| TransactionService.cs | 61 | `Deposit` updates balance with interpolated SQL → injection. | Use parameters. |
| UserService.cs | 45 | `UpdateUser` builds SQL with interpolated email/username → injection. | Use parameters and validate inputs. |
| UserService.cs | 58 | `DeleteUser` builds SQL with interpolated ID → injection. | Use parameters. |
| UserService.cs | 84 | `SearchUsers` builds raw `LIKE` clause with user input → injection. | Use parameterised query (`WHERE Username LIKE @q`). |
| TransactionService.cs | 84 | `RecordTransaction` inserts `description` directly → injection & null handling. | Parameterise all fields; handle null safely. |
| AuthService.cs | 84 | `ValidateToken` returns `true` before any validation – token bypass. | Remove early `return`; perform proper validation. |
| EmailService.cs | 9‑10 | `SmtpClient` stored as a field (not thread‑safe) and never disposed. | Create a new `SmtpClient` per send or wrap in `using`; dispose after use. |
| DatabaseHelper.cs | 12 | Fallback connection string contains hard‑coded credentials. | Remove fallback or load from secure source. |

---

## 2. Logic Errors
| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 27 | Fee not included in balance check (`fromBalance >= amount`). | Check `fromBalance >= totalDebit`. |
| TransactionService.cs | 22 | Allows zero or negative amount (`amount < 0` only). | Change to `if (amount <= 0)`. |
| TransactionService.cs | 84 | `description` may be `null`; inserted as literal `null` string in SQL. | Pass `DBNull.Value` or use parameter with nullable handling. |
| TransactionService.cs | 44 | Interest bonus calculation multiplies by `1` unnecessarily. | Simplify to `amount * 0.05m`. |
| UserService.cs | 30 | Pagination offset calculated as `page * pageSize` (off‑by‑one). | Use `int skip = (page - 1) * pageSize;`. |
| UserService.cs | 30 | No validation that `page` is ≥ 1; negative pages produce large skips. | Clamp `page` to minimum 1. |
| AuthService.cs | 30 | Admin bypass password grants unrestricted access. | Remove bypass; enforce normal credential check. |
| TransactionService.cs | 24 | No check for self‑transfer (`fromUserId == toUserId`). | Reject or treat as no‑op. |
| TransactionService.cs | 24 | Does not enforce `MaxTransactionsPerDay`. | Call `IsWithinDailyLimit` before proceeding. |
| TransactionService.cs | 24 | Does not verify that `toUserId` exists before debit. | Ensure `toUserTable.Rows.Count > 0` and handle missing target. |
| AuthService.cs | 84 | Unreachable validation code after early `return`. | Remove dead code and implement proper validation. |
| UserService.cs | 84 | `SearchUsers` may throw if `query` contains `'` or is null. | Escape input or use parameterised query; validate null. |
| UserService.cs | 45 | No validation of `email`/`username` format before update. | Validate with `StringHelper.IsValidEmail/Username`. |
| UserService.cs | 58 | No check that user exists before delete; may silently succeed. | Verify existence and return appropriate status. |

---

## 3. Error Handling
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 22‑30 | `SqlConnection`, `SqlCommand`, `SqlDataReader` not wrapped in `using`; exceptions bubble up. | Wrap in `using` blocks and log/return a generic error. |
| TransactionService.cs | 30‑70 | No `try/catch` around DB updates; any failure returns 500 without context. | Add exception handling, log, and return a controlled error response. |
| EmailService.cs | 38‑45 | `SendTransferNotification` re‑throws after max retries – controller may not handle. | Return a result indicating failure; log appropriately. |
| EmailService.cs | 55‑60 | `SendWelcomeEmail` catches generic `Exception` and only writes to console. | Log via `ILogger`, propagate or return status. |
| EmailService.cs | 71‑76 | `SendWelcomeEmailHtml` has no exception handling. | Wrap send in `try/catch` and log failures. |
| UserService.cs | 84‑92 | `SearchUsers` catches generic `Exception` and returns empty list, hiding errors. | Log the exception and return appropriate error code. |
| DatabaseHelper.cs | 22‑28 | `ExecuteQuery` opens connection and never disposes it. | Use `using` for connection, command, and adapter. |
| DatabaseHelper.cs | 33‑38 | `ExecuteNonQuery` opens connection, closes it, but does not dispose. | Use `using` for connection and command. |
| Program.cs | 12 | `UseDeveloperExceptionPage` always enabled – leaks internal errors to clients. | Enable only in Development environment. |
| AuthService.cs | 84 | Early `return true` bypasses token validation; errors not reported. | Remove early return and perform proper validation. |
| EmailService.cs | 13 | Uses `Console.WriteLine` for error output instead of structured logging. | Inject `ILogger<EmailService>` and log errors. |

---

## 4. Resource Leaks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 22‑30 | `SqlConnection`, `SqlCommand`, `SqlDataReader` never disposed. | Wrap each in `using`. |
| DatabaseHelper.cs | 12‑14 | `GetOpenConnection` returns an open connection; callers do not dispose. | Return a closed connection or provide a `using` pattern; ensure callers dispose. |
| DatabaseHelper.cs | 22‑28 | `ExecuteQuery` leaves connection open. | Use `using` for connection/command/adapter. |
| DatabaseHelper.cs | 33‑38 | `ExecuteNonQuery` leaves connection undisposed. | Use `using`. |
| EmailService.cs | 9‑15 | `SmtpClient` stored as a field and never disposed. | Dispose in `Dispose` method or create per‑send with `using`. |
| EmailService.cs | 38‑45 | `MailMessage` created but not disposed. | Wrap in `using`. |
| EmailService.cs | 55‑60 | `MailMessage` in `SendWelcomeEmail` not disposed. | Wrap in `using`. |
| EmailService.cs | 71‑76 | `MailMessage` in `SendWelcomeEmailHtml` not disposed. | Wrap in `using`. |
| TransactionService.cs | 30‑70 | Calls to `ExecuteNonQuery` (which leaks connections) for balance updates. | Ensure `ExecuteNonQuery` disposes its connection or use `using` directly. |
| TransactionService.cs | 84‑90 | `RecordTransaction` uses `ExecuteNonQuery` → connection leak. | Same as above. |

---

## 5. Null Reference Risks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionController.cs | 23 | `userIdClaim` may be `null`; `int.Parse(userIdClaim!)` will throw. | Validate claim existence and return `Unauthorized` if missing. |
| TransactionController.cs | 38 | Same issue for deposit endpoint. | Same fix. |
| AuthService.cs | 71 | `_config["Jwt:SecretKey"]!` may be `null` → `ArgumentNullException`. | Validate and throw a clear configuration error. |
| EmailService.cs | 38‑45 | `toEmail` could be `null`; `MailMessage` constructor will throw. | Validate email before sending. |
| EmailService.cs | 55‑60 | `username` may be `null`; `.ToUpper()` throws. | Guard against null or use `?.ToUpper()`. |
| UserService.cs | 84‑92 | `query` may be `null`; string interpolation creates `LIKE '%null%'`. | Return empty result or treat null as empty string. |
| StringHelper.cs | 31‑33 | `IsBlank` checks `value == ""` before `Trim`; fine but could be simplified. | No immediate NRE, but could be streamlined. |
| EmailService.cs | 71‑76 | `toEmail` may be `null` in HTML email method. | Validate before creating `MailMessage`. |

---

## 6. Dead Code
| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 84‑92 | `ValidateToken` returns before any validation; remaining code unreachable. | Remove dead code and implement proper validation. |
| DatabaseHelper.cs | 55‑66 | `ExecuteQueryWithParams` marked `[Obsolete]` but still compiled; not used anywhere. | Delete or replace with `ExecuteQuerySafe`. |
| TransactionService.cs | 20‑22 | `IsWithinDailyLimit` never called. | Either use it in `Transfer` or remove. |
| TransactionService.cs | 98‑101 | `FormatCurrency` never used. | Remove or expose if needed. |
| StringHelper.cs | 31‑38 | `JoinWithSeparator` (inefficient) not referenced anywhere. | Delete or replace calls with `JoinWithSeparatorFixed`. |
| Program.cs | 15 | HTTPS redirection line commented out. | Either enable or remove comment. |
| TransactionService.cs | 108‑112 | `RefundTransaction` throws `NotImplementedException`; controller catches and returns generic 500. | Implement refund logic or return `NotImplemented` status (501). |

---

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
|------|------|-------|-----|
| DatabaseHelper.cs | 12 | Fallback connection string hard‑coded with credentials. | Move to secure configuration. |
| AuthService.cs | 30 | Hard‑coded admin bypass password. | Remove; use proper auth. |
| EmailService.cs | 9‑12 | Email subjects, from address, support address hard‑coded. | Store in configuration. |
| Program.cs | 17 | CORS policy `AllowAnyOrigin/Method/Header`. | Replace with named policy and configurable origins. |
| UserService.cs | 30 | Page size limit `50` hard‑coded. | Move to a constant or config. |
| EmailService.cs | 13‑15 | `MaxRetries = 3`, `SmtpTimeoutMs = 5000`. | Move to config if needed. |
| TransactionService.cs | 13 | `TransactionFeeRate = 0.015m`. | Move to config/constant with comment. |
| TransactionService.cs | 14 | `MaxTransactionsPerDay = 10`. | Move to config. |
| TransactionService.cs | 44 | Interest bonus rate `0.05m`. | Move to config. |
| AuthService.cs | 71 | JWT secret key, issuer, audience read from config but defaults are hard‑coded in `appsettings.json`. | Store secrets in environment/secret manager. |
| Program.cs | 30 | JWT token expiry `AddDays(30)`. | Make configurable. |
| appsettings.json | 5‑7 | Logging levels set to `Debug` for all categories. | Use `Information` or `Warning` for production. |

---

## 8. Anti‑patterns and Code Quality
| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 31‑38 | `JoinWithSeparator` builds string via repeated concatenation (O(n²)). | Use `string.Join` or `StringBuilder`. |
| StringHelper.cs | 13‑15, 19‑21 | `new Regex` created on each call. | Cache compiled regex as `static readonly`. |
| AuthService.cs | 24 | MD5 hashing for passwords. | Replace with a strong password‑hashing algorithm. |
| AuthService.cs | 22‑30 | Raw SQL built with string interpolation. | Use parameterised queries. |
| DatabaseHelper.cs | 22‑38 | Many methods open connections without `using`. | Refactor to `using` or async equivalents. |
| TransactionService.cs | 30‑70 | Direct SQL string interpolation for updates. | Parameterise. |
| UserService.cs | 45‑58 | Direct SQL interpolation for updates/deletes. | Parameterise. |
| UserService.cs | 5‑6 | Static mutable lists (`_auditLog`, `_requestCount`) – not thread‑safe. | Use concurrent collections or remove static state. |
| EmailService.cs | 9‑15 | `SmtpClient` stored as a field (not thread‑safe) and never disposed. | Create per‑send or wrap in `using`. |
| EmailService.cs | 38‑45, 55‑60, 71‑76 | Uses `Console.WriteLine` for error reporting. | Inject `ILogger<EmailService>` and log. |
| TransactionService.cs | 84‑90 | `RecordTransaction` builds SQL with string interpolation, including nullable `description`. | Parameterise and handle nulls. |
| Program.cs | 12 | `UseDeveloperExceptionPage` enabled in all environments. | Guard with environment check. |
| All services | – | No async/await usage for I/O‑bound DB/email calls. | Implement async APIs (`ExecuteNonQueryAsync`, etc.). |
| All services | – | No input validation before DB writes (e.g., email format, username). | Centralise validation (e.g., `StringHelper`). |
| All services | – | No unit‑testable separation; business logic tightly coupled to ADO.NET. | Introduce repository interfaces and mockable abstractions. |

---

## 9. Configuration Issues
| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 12 | `UseDeveloperExceptionPage()` always on – leaks details. | Enable only in Development (`if (app.Environment.IsDevelopment())`). |
| Program.cs | 30 | `ValidateLifetime = false` disables JWT expiry checks. | Set to `true`. |
| Program.cs | 17 | CORS policy `AllowAnyOrigin/Method/Header` – insecure. | Define a named policy with allowed origins. |
| Program.cs | 15 | HTTPS redirection commented out. | Uncomment to enforce HTTPS. |
| appsettings.json | 3‑7 | Database credentials, JWT secret, email password stored in plain text. | Move to secret manager / environment variables; never commit. |
| appsettings.json | 11‑13 | Logging level set to `Debug` for all categories. | Use `Information`/`Warning` for production. |
| appsettings.json | – | No `appsettings.Production.json` override. | Add environment‑specific config files. |
| Program.cs | – | No rate‑limiting or lockout on authentication endpoints. | Add middleware (e.g., `AspNetCoreRateLimit`). |
| Program.cs | – | No HSTS header configuration. | Add `app.UseHsts();` in production. |
| Program.cs | – | No health‑check endpoint configured. | Add `app.MapHealthChecks("/health")`. |

---

## 10. Missing Unit Tests
| Area | Reason | Suggested Tests |
|------|--------|-----------------|
| **AuthService.Login** | Critical authentication path; contains SQL & password logic. | Valid credentials succeed; invalid credentials fail; SQL injection attempt is rejected; admin bypass removed. |
| **AuthService.GenerateJwtToken / ValidateToken** | JWT creation and validation. | Token contains correct claims; expired token rejected; malformed token rejected; `ValidateLifetime` enforced. |
| **TransactionService.Transfer** | Money movement, fee calculation, balance checks. | Successful transfer updates balances correctly (including fee); insufficient funds rejected; self‑transfer rejected; daily‑limit enforcement; negative/zero amount rejected; SQL injection attempts blocked. |
| **TransactionService.Deposit** | Deposit with interest bonus. | Valid deposit updates balance with bonus; amount limits enforced; negative/zero amount rejected. |
| **TransactionService.IsWithinDailyLimit** | Daily transaction cap logic. | Returns false after reaching limit; true otherwise. |
| **UserService.GetUsersPage** | Pagination logic. | Correct number of items returned; off‑by‑one offset fixed; pageSize capped at 50; negative page handled gracefully. |
| **UserService.SearchUsers** | Search with user‑supplied input. | Proper results returned; SQL injection attempt does not break; empty query returns all or none as defined. |
| **StringHelper.IsValidEmail / IsValidUsername** | Input validation. | Accepts valid formats; rejects invalid ones; edge‑case lengths. |
| **EmailService.SendTransferNotification & SendWelcomeEmail** | Email sending flow and error handling. | Successful send; SMTP failure retries; exception handling does not crash service; TLS enabled. |
| **DatabaseHelper.ExecuteQuerySafe / ExecuteNonQuery** | Parameterised query handling. | Queries return expected data; injection attempts fail; connections disposed. |
| **Overall API Controllers** | End‑to‑end request handling. | Authentication required for protected routes; proper status codes for success/failure; model validation errors return 400. |

*No test project was found in the repository; creating a dedicated `SampleBankingApp.Tests` project with the above test cases is strongly recommended.*