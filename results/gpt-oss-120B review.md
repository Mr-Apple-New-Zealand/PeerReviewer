**Code Review Report – branch `gpt-oss-120B` (commit `4d1f610bf64339e3abaab7c71df0dfe8b569681e`)**

---

## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `AuthService.cs` | 23 | Hard‑coded admin bypass password (`SuperAdmin2024`). | Move to secure secret store or remove; require normal authentication. |
| `DatabaseHelper.cs` | 13 | Fallback connection string contains plain‑text SA password. | Remove fallback; obtain connection string from secure configuration only. |
| `appsettings.json` | 9‑13 | Plain‑text DB password, JWT secret, and email password committed to source. | Store secrets in environment variables or a secret manager; never commit them. |
| `Program.cs` | 31 | `ValidateLifetime = false` disables JWT expiration checks. | Set `ValidateLifetime = true` and use reasonable token lifetimes. |
| `Program.cs` | 38 | `UseDeveloperExceptionPage()` always enabled (exposes stack traces). | Enable only in Development environment (`if (app.Environment.IsDevelopment())`). |
| `Program.cs` | 41 | CORS policy `AllowAnyOrigin/AllowAnyMethod/AllowAnyHeader` is overly permissive. | Restrict origins, methods, and headers to required values. |
| `AuthService.cs` | 30‑33 | SQL injection: username and hashed password interpolated into raw SQL. | Use parameterised queries (`@Username`, `@Password`). |
| `AuthService.cs` | 45‑48 | MD5 used for password hashing (weak, unsalted). | Replace with a strong algorithm (e.g., PBKDF2, Argon2, BCrypt). |
| `TransactionService.cs` | 45‑48 | `ExecuteNonQuery` with interpolated balances allows SQL injection if values are tampered. | Use parameterised UPDATE statements. |
| `TransactionService.cs` | 71‑73 | `RecordTransaction` builds INSERT with raw description, possible injection. | Parameterise all fields, especially `description`. |
| `UserService.cs` | 57‑60 | `UpdateUser` builds UPDATE with raw email/username strings. | Parameterise query. |
| `UserService.cs` | 71‑74 | `DeleteUser` builds DELETE with raw id (safe) but still raw SQL; use parameters for consistency. | Parameterise. |
| `UserService.cs` | 92‑95 | `SearchUsers` builds WHERE clause with raw `query` → SQL injection. | Use parameterised LIKE (`WHERE Username LIKE @q`). |
| `EmailService.cs` | 20‑23 | `EnableSsl = false` and credentials stored in config – insecure email transmission. | Enable SSL/TLS and protect credentials. |
| `EmailService.cs` | 24‑27 | `SmtpClient` stored as a singleton field (not thread‑safe). | Create a new `SmtpClient` per send or use a thread‑safe pool. |
| `StringHelper.cs` | 12‑14 | `IsValidEmail` does not check for null before `email.Length`. | Add null guard. |
| `StringHelper.cs` | 20‑22 | `IsValidUsername` does not check for null before `username.Length`. | Add null guard. |
| `StringHelper.cs` | 28‑30 | `MaskAccountNumber` does not check for null before `accountNumber.Length`. | Add null guard. |
| `StringHelper.cs` | 34‑36 | `ObfuscateAccount` assumes `account` length ≥ 4; may throw on short strings. | Validate length or handle safely. |

---

## 2. Logic Errors
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `TransactionService.cs` | 38‑44 | Fee is added to debit but balance check uses only `amount`, allowing overdraft after fee. | Check `fromBalance >= totalDebit`. |
| `TransactionService.cs` | 57‑58 | `newFromBalance` may become negative if fee > available balance. | Ensure sufficient funds for amount + fee. |
| `TransactionService.cs` | 68‑70 | `interestBonus = amount * 0.05m * 1` – extra `* 1` is unnecessary but harmless. | Simplify to `amount * 0.05m`. |
| `UserService.cs` | 106‑108 | Pagination offset calculated as `page * pageSize`; should be `(page‑1) * pageSize`. | Change to `int skip = (page - 1) * pageSize;`. |
| `AuthService.cs` | 84‑90 | `ValidateToken` returns `true` before any validation; unreachable code below. | Remove early return; perform proper JWT validation (expiry, signature). |
| `TransactionService.cs` | 52‑55 | `IsWithinDailyLimit` is never called, so daily‑limit rule is ineffective. | Invoke the method before processing a transfer. |
| `UserService.cs` | 124‑128 | `SearchUsers` catches all exceptions and returns empty list, hiding errors. | Log the exception and return appropriate error response. |
| `TransactionService.cs` | 78‑80 | `RecordTransaction` inserts `description` directly; if `null` it becomes the string `"null"` in DB. | Pass `NULL` to SQL when description is null (parameterised). |
| `AuthService.cs` | 30‑33 | Password hash compared with stored hash, but stored passwords may be MD5‑hashed without salt – insecure and may cause mismatches if migration occurs. | Migrate to salted hash algorithm. |
| `TransactionService.cs` | 84‑86 | `Deposit` adds `interestBonus` without checking daily transaction limit. | Apply limit check if required. |
| `AuthService.cs` | 45‑48 | No check for `reader.HasRows` before `reader.Read()`. If no rows, `Read()` returns false and code proceeds to admin bypass. | Return null when no rows; avoid bypass path unless intended. |

---

## 3. Error Handling
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `AuthService.cs` | 30‑48 | `SqlConnection` and `SqlCommand` are never disposed; any exception leaks resources. | Wrap in `using` statements or `await using`. |
| `AuthService.cs` | 84‑90 | Unreachable code after `return true;` – intended validation never runs. | Remove early return and implement proper validation. |
| `TransactionService.cs` | 38‑84 | No try/catch around DB updates; any failure bubbles up as 500. | Add transaction scope and catch `SqlException` to return meaningful error. |
| `TransactionService.cs` | 86‑92 | Email send failures are not caught; could cause unhandled exception after DB commit. | Send email before committing or wrap in try/catch and rollback on failure. |
| `EmailService.cs` | 41‑53 | `MailMessage` objects are not disposed. | Wrap each `MailMessage` in `using`. |
| `EmailService.cs` | 61‑68 | Generic `catch (Exception)` logs to console and swallows error. | Propagate or log via structured logger; consider retry policy. |
| `UserService.cs` | 124‑128 | `SearchUsers` catches generic `Exception` and returns empty list, losing error context. | Log exception and return appropriate HTTP error from controller. |
| `DatabaseHelper.cs` | 21‑27 | `ExecuteQuery` opens connection and never disposes `SqlCommand`/`SqlDataAdapter`. | Use `using` for all disposable objects. |
| `DatabaseHelper.cs` | 33‑38 | `ExecuteNonQuery` disposes connection but not `SqlCommand`. | Dispose command as well. |
| `DatabaseHelper.cs` | 45‑50 | `TableExists` uses `using` for connection but not for `DataTable`; fine, but could be wrapped. | Optional: dispose DataTable if large. |
| `Program.cs` | 38 | `app.UseDeveloperExceptionPage()` may expose internal errors to clients in production. | Guard with environment check. |
| `TransactionController.cs` | 24‑27 | `int.Parse(userIdClaim!)` will throw if claim missing; no error handling. | Validate claim existence and return 401 if absent. |
| `TransactionController.cs` | 38‑41 | Same issue for deposit endpoint. | Same fix. |

---

## 4. Resource Leaks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `DatabaseHelper.cs` | 21‑27 | `SqlConnection`, `SqlCommand`, `SqlDataAdapter` not disposed in `ExecuteQuery`. | Use `using` for each. |
| `DatabaseHelper.cs` | 33‑38 | `SqlCommand` not disposed in `ExecuteNonQuery`. | Wrap in `using`. |
| `DatabaseHelper.cs` | 45‑50 | `SqlDataAdapter` not disposed in `ExecuteQuerySafe`. | Wrap in `using`. |
| `AuthService.cs` | 30‑48 | `SqlConnection` and `SqlCommand` not disposed. | Use `using`. |
| `EmailService.cs` | 31‑34 | `SmtpClient` stored as field and never disposed. | Implement `IDisposable` on `EmailService` and dispose client, or create per‑send. |
| `EmailService.cs` | 44‑48, 61‑66, 78‑82 | `MailMessage` instances not disposed. | Wrap each in `using`. |
| `TransactionService.cs` | 45‑48, 71‑73 | DataTables returned from helper are not disposed (acceptable for short‑lived use) but could be wrapped if large. | Optionally dispose after use. |
| `Program.cs` | 38 | `UseDeveloperExceptionPage` may allocate diagnostic resources in production; not a leak but unnecessary. | Guard with environment. |

---

## 5. Null Reference Risks
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `StringHelper.cs` | 12‑14 | `IsValidEmail` accesses `email.Length` without null check. | Return `false` if `email` is null. |
| `StringHelper.cs` | 20‑22 | `IsValidUsername` accesses `username.Length` without null check. | Add null guard. |
| `StringHelper.cs` | 28‑30 | `MaskAccountNumber` accesses `accountNumber.Length` without null check. | Add null guard. |
| `StringHelper.cs` | 34‑36 | `ObfuscateAccount` assumes `account` length ≥ 4; may throw on short strings. | Validate length or return original. |
| `TransactionController.cs` | 24‑27 | `User.FindFirst(...)?` may be null; `int.Parse` on null throws. | Return 401 if claim missing. |
| `TransactionController.cs` | 38‑41 | Same issue for deposit endpoint. | Same fix. |
| `AuthService.cs` | 30‑48 | If query returns no rows, `reader.Read()` returns false; code proceeds to admin bypass. | Return null when no rows. |
| `AuthService.cs` | 45‑48 | Admin bypass uses plain password; if username null, earlier code may throw. | Validate inputs. |
| `TransactionService.cs` | 45‑48 | `fromUserTable.Rows[0]` assumes a row exists; if user not found, throws. | Check `Rows.Count` before accessing. |
| `TransactionService.cs` | 71‑73 | Same for `toUserTable`. | Same fix. |
| `UserService.cs` | 57‑60 | `UpdateUser` receives `email` and `username` which could be null from caller; interpolated into SQL. | Validate non‑null before use. |
| `UserService.cs` | 92‑95 | `SearchUsers` builds WHERE clause with `query` that may be null, resulting in `LIKE '%null%'`. | Guard against null or treat as empty. |
| `Program.cs` | 31 | `builder.Configuration["Jwt:SecretKey"]` may be null; `Encoding.UTF8.GetBytes` would throw. | Validate and fail fast with clear message. |

---

## 6. Dead Code
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `AuthService.cs` | 71‑78 | `HashPasswordSha1` never called. | Remove if not needed. |
| `AuthService.cs` | 84‑90 | Code after `return true;` is unreachable. | Delete unreachable block. |
| `DatabaseHelper.cs` | 57‑66 | `ExecuteQueryWithParams` marked `[Obsolete]` but still present; not used anywhere. | Remove or replace all callers with `ExecuteQuerySafe`. |
| `TransactionService.cs` | 94‑98 | `IsWithinDailyLimit` defined but never invoked. | Call it in `Transfer`/`Deposit` or delete. |
| `TransactionService.cs` | 106‑108 | `FormatCurrency` never used. | Remove or expose if needed. |
| `Program.cs` | 41 | `app.UseHttpsRedirection();` commented out. | Either enable or remove comment with explanation. |
| `EmailService.cs` | 71‑73 | `BuildHtmlTemplate` only used by `SendWelcomeEmailHtml`; acceptable but could be inlined. | No action needed unless simplifying. |
| `UserService.cs` | 124‑128 | `catch (Exception)` returns empty list, effectively swallowing errors (logic, not dead code). | Not dead but should be handled properly. |

---

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `DatabaseHelper.cs` | 13 | Fallback connection string hard‑coded with password. | Remove fallback; read from config only. |
| `AuthService.cs` | 24 | `AdminBypassPassword` hard‑coded. | Move to secure config. |
| `AuthService.cs` | 84‑90 | JWT token expiry set to 30 days inline. | Store as configurable value. |
| `TransactionService.cs` | 14‑15 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` hard‑coded. | Consider moving to config if business rules may change. |
| `EmailService.cs` | 13‑14 | Email subjects hard‑coded. | Move to resources or config. |
| `EmailService.cs` | 17‑20 | `MaxRetries = 3`, `SmtpTimeoutMs = 5000` hard‑coded. | Configurable. |
| `UserService.cs` | 106‑108 | Page size capped at 50 inline. | Define constant or config. |
| `UserService.cs` | 106‑108 | Pagination offset calculated with `page * pageSize`. | Use constant for page start index. |
| `Program.cs` | 38 | `UseDeveloperExceptionPage()` always enabled. | Guard with environment. |
| `Program.cs` | 41 | `AllowAnyOrigin/Method/Header` – magic permissive strings. | Replace with specific origins. |
| `StringHelper.cs` | 12‑14, 20‑22 | Regex patterns hard‑coded. | Cache compiled regex as static readonly. |
| `StringHelper.cs` | 28‑30 | Mask character `'*'` hard‑coded. | Define constant if needed. |
| `appsettings.json` | 9‑13 | DB password, JWT secret, email password in plain text. | Move to secret store. |

---

## 8. Anti‑patterns and Code Quality
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `StringHelper.cs` | 28‑31 | `JoinWithSeparator` builds string via repeated concatenation (O(n²)). | Replace with `string.Join(separator, items)` (already provided in `JoinWithSeparatorFixed`). |
| `StringHelper.cs` | 12‑14, 20‑22 | New `Regex` created on each call. | Cache compiled regex as `static readonly`. |
| `UserService.cs` | 5‑7 | Static mutable fields `_auditLog` and `_requestCount` are not thread‑safe. | Use concurrent collections or lock. |
| `EmailService.cs` | 24‑27 | `SmtpClient` stored as field (not thread‑safe). | Create per‑send or protect with lock. |
| `AuthService.cs` | 30‑48 | Raw SQL with string interpolation (SQL injection risk). | Use parameterised queries. |
| `TransactionService.cs` | 45‑48, 71‑73 | Raw SQL interpolation for balance updates and inserts. | Parameterise. |
| `UserService.cs` | 57‑60, 71‑74 | Raw SQL interpolation for updates/deletes/search. | Parameterise. |
| `Program.cs` | 38 | `UseDeveloperExceptionPage()` unconditional – development‑only feature. | Guard with environment. |
| `Program.cs` | 41 | `AllowAnyOrigin` – anti‑pattern for production. | Restrict origins. |
| `AuthService.cs` | 84‑90 | Unreachable code after early return. | Remove dead code. |
| `TransactionService.cs` | 94‑98 | `IsWithinDailyLimit` never used – dead logic. | Either use or delete. |
| `TransactionService.cs` | 106‑108 | `FormatCurrency` unused. | Remove. |
| `AuthService.cs` | 71‑78 | `HashPasswordSha1` unused. | Remove. |
| `DatabaseHelper.cs` | 57‑66 | `ExecuteQueryWithParams` obsolete and unused. | Delete. |
| `TransactionService.cs` | 84‑86 | No transaction scope for two balance updates – possible inconsistency. | Wrap updates in a DB transaction. |
| `TransactionService.cs` | 86‑92 | Email sent after DB commit; if email fails, user sees success but no notification. | Send email before commit or implement compensation. |
| `TransactionService.cs` | 71‑73 | No check for `fromUserTable.Rows.Count` before accessing row. | Validate existence. |
| `UserService.cs` | 124‑128 | Swallowing exceptions in `SearchUsers`. | Propagate or log appropriately. |

---

## 9. Configuration Issues
| File | Line | Issue | Fix |
|------|------|-------|-----|
| `Program.cs` | 38 | `UseDeveloperExceptionPage()` always enabled (exposes stack traces). | Enable only in Development (`if (app.Environment.IsDevelopment())`). |
| `Program.cs` | 31 | `ValidateLifetime = false` disables JWT expiration validation. | Set to `true`. |
| `Program.cs` | 41 | CORS policy `AllowAnyOrigin/AllowAnyMethod/AllowAnyHeader`. | Restrict to known origins/methods. |
| `Program.cs` | 42 | HTTPS redirection commented out. | Uncomment or enforce HTTPS via middleware. |
| `Program.cs` | 45‑48 | Logging level set to `Debug` for all categories in production. | Use `Information` or lower in Production. |
| `appsettings.json` | 9‑13 | Production DB password, JWT secret, and email password stored in plain text. | Move to environment variables or secret manager. |
| `appsettings.json` | 23‑27 | JWT `SecretKey` is a short, low‑entropy string (`mysecretkey`). | Use a strong, randomly generated key (256‑bit). |
| `appsettings.json` | 31‑34 | `AllowedHosts` set to `*`. | Restrict to specific hostnames. |
| No rate‑limiting or account‑lockout configured for login endpoint. | N/A | Add ASP.NET Core rate limiting middleware or implement lockout logic. |
| No `appsettings.Development.json` or `Production.json` overrides present. | N/A | Provide environment‑specific configs, especially for secrets. |

---

## 10. Missing Unit Tests
| File | Line | Issue | Fix |
|------|------|-------|-----|
| **No test project found** | N/A | Critical business logic lacks automated verification. | Add a test project (e.g., `SampleBankingApp.Tests`) covering: <br>• `AuthService.Login` – valid/invalid credentials, SQL injection attempt, admin bypass. <br>• `AuthService.GenerateJwtToken` – claims, expiry, signature. <br>• `AuthService.ValidateToken` – expired token, malformed token. <br>• `TransactionService.Transfer` – successful transfer, insufficient funds, fee handling, daily‑limit enforcement, null users, SQL injection safety. <br>• `TransactionService.Deposit` – amount limits, interest bonus, daily limit. <br>• `TransactionService.IsWithinDailyLimit` – boundary at max transactions. <br>• `UserService.GetUserById` – valid/invalid IDs, not‑found case. <br>• `UserService.UpdateUser` – email/username validation, SQL injection safety. <br>• `UserService.DeleteUser` – successful delete, error handling. <br>• `UserService.GetUsersPage` – pagination offsets, page‑size limits, empty result. <br>• `UserService.SearchUsers` – injection attempts, empty query. <br>• `StringHelper` methods – null handling, regex correctness, `JoinWithSeparator` performance. <br>• `EmailService` – successful send, retry logic, exception handling (mock `SmtpClient`). |

--- 

*All identified issues should be addressed before the code is considered production‑ready.*