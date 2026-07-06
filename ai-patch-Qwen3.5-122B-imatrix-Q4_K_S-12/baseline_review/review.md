## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `SampleBankingApp/Services/AuthService.cs` | 38 | SQL injection via string interpolation in `Login` method. | Use parameterized queries (`ExecuteQuerySafe`). |
| `SampleBankingApp/Services/AuthService.cs` | 48 | Hardcoded admin backdoor password bypasses authentication. | Remove the hardcoded bypass logic entirely. |
| `SampleBankingApp/Services/AuthService.cs` | 56 | MD5 is cryptographically broken and unsuitable for password hashing. | Use `BCrypt` or `Argon2`. |
| `SampleBankingApp/Services/TransactionService.cs` | 44 | SQL injection in `Transfer` via string interpolation in `ExecuteNonQuery`. | Use parameterized queries. |
| `SampleBankingApp/Services/TransactionService.cs` | 63 | SQL injection in `Deposit` via string interpolation. | Use parameterized queries. |
| `SampleBankingApp/Services/TransactionService.cs` | 85 | SQL injection in `RecordTransaction` via string interpolation. | Use parameterized queries. |
| `SampleBankingApp/Services/UserService.cs` | 42 | SQL injection in `UpdateUser` via string interpolation. | Use parameterized queries. |
| `SampleBankingApp/Services/UserService.cs` | 52 | SQL injection in `DeleteUser` via string interpolation. | Use parameterized queries. |
| `SampleBankingApp/Services/UserService.cs` | 85 | SQL injection in `SearchUsers` via `ExecuteQuery` with raw string. | Use parameterized queries with `LIKE`. |
| `SampleBankingApp/Data/DatabaseHelper.cs` | 22 | Hardcoded fallback credentials in constructor. | Remove hardcoded credentials; fail securely if config is missing. |
| `SampleBankingApp/appsettings.json` | 3 | Production database credentials committed to source control. | Use environment variables or secret management. |
| `SampleBankingApp/appsettings.json` | 13 | Email SMTP password committed to source control. | Use environment variables or secret management. |
| `SampleBankingApp/Program.cs` | 23 | JWT lifetime validation is disabled (`ValidateLifetime = false`). | Set `ValidateLifetime = true`. |
| `SampleBankingApp/Program.cs` | 33 | Developer exception page enabled unconditionally. | Wrap in `if (app.Environment.IsDevelopment())`. |
| `SampleBankingApp/Program.cs` | 35 | HTTPS redirection is commented out. | Uncomment `app.UseHttpsRedirection()`. |
| `SampleBankingApp/Program.cs` | 37 | Overly permissive CORS policy allows any origin/method/header. | Restrict to specific trusted origins and methods. |
| `SampleBankingApp/Controllers/UserController.cs` | 33 | Missing authorization check; any authenticated user can view any user. | Add `[Authorize]` with role/ownership check. |
| `SampleBankingApp/Controllers/UserController.cs` | 47 | Missing authorization check; any authenticated user can update any user. | Add ownership verification or admin role check. |
| `SampleBankingApp/Controllers/UserController.cs` | 62 | Missing authorization check; any authenticated user can delete any user. | Add ownership verification or admin role check. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `SampleBankingApp/Services/TransactionService.cs` | 40 | Balance check uses `amount` but deducts `amount + fee`, allowing negative balances. | Check `fromBalance >= totalDebit`. |
| `SampleBankingApp/Services/TransactionService.cs` | 36 | No check to prevent users from transferring funds to themselves. | Add `if (fromUserId == toUserId) return (false, "Cannot transfer to self");`. |
| `SampleBankingApp/Services/UserService.cs` | 73 | Pagination offset calculation is incorrect (`page * pageSize` instead of `(page - 1) * pageSize`). | Change to `int skip = (page - 1) * pageSize;`. |
| `SampleBankingApp/Services/AuthService.cs` | 92 | `ValidateToken` returns `true` immediately, ignoring actual token validation. | Remove early return and implement proper validation. |
| `SampleBankingApp/Services/TransactionService.cs` | 63 | Deposit interest calculation multiplies by `1`, making the bonus equal to the amount (100% interest). | Verify intended interest rate constant. |

## 3. Error Handling

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `SampleBankingApp/Services/UserService.cs` | 88 | `SearchUsers` catches `Exception` and returns empty list, hiding errors. | Log the exception and return empty list or rethrow. |
| `SampleBankingApp/Controllers/UserController.cs` | 50 | `UpdateUser` returns raw `ex.Message` to client, leaking internal details. | Return generic error message. |
| `SampleBankingApp/Controllers/UserController.cs` | 54 | `UpdateUser` returns raw `ex.Message` for 500 errors. | Return generic error message. |
| `SampleBankingApp/Services/EmailService.cs` | 68 | `SendWelcomeEmail` swallows exceptions silently. | Log the exception. |
| `SampleBankingApp/Services/TransactionService.cs` | 95 | `RefundTransaction` throws `NotImplementedException` without handling. | Implement logic or return appropriate error response. |
| `SampleBankingApp/Services/TransactionService.cs` | 33 | `Transfer` lacks database transaction for atomic balance updates. | Wrap DB operations in a transaction. |

## 4. Resource Leaks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `SampleBankingApp/Data/DatabaseHelper.cs` | 28 | `GetOpenConnection` returns open connection without disposal contract. | Return `SqlConnection` in `using` block or document disposal. |
| `SampleBankingApp/Data/DatabaseHelper.cs` | 36 | `ExecuteQuery` opens connection but never closes/disposes it. | Wrap connection in `using` statement. |
| `SampleBankingApp/Data/DatabaseHelper.cs` | 58 | `ExecuteNonQuery` opens connection but may leak on exception before `Close()`. | Wrap connection in `using` statement. |
| `SampleBankingApp/Services/AuthService.cs` | 41 | `SqlConnection` opened in `Login` but never closed/disposed. | Wrap connection in `using` statement. |
| `SampleBankingApp/Services/EmailService.cs` | 22 | `SmtpClient` held as instance field; not thread-safe and may leak sockets. | Create new `SmtpClient` per send or use `using`. |
| `SampleBankingApp/Services/EmailService.cs` | 42 | `MailMessage` created but never disposed. | Wrap `MailMessage` in `using` statement. |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `SampleBankingApp/Controllers/TransactionController.cs` | 23 | `int.Parse` on `userIdClaim` may throw if claim is null. | Add null check or use `int.TryParse`. |
| `SampleBankingApp/Controllers/TransactionController.cs` | 35 | `int.Parse` on `userIdClaim` may throw if claim is null. | Add null check or use `int.TryParse`. |
| `SampleBankingApp/Services/TransactionService.cs` | 40 | Accessing `Rows[0]` without checking `Rows.Count > 0`. | Check `Rows.Count` before access. |
| `SampleBankingApp/Services/TransactionService.cs` | 44 | Accessing `Rows[0]` without checking `Rows.Count > 0`. | Check `Rows.Count` before access. |
| `SampleBankingApp/Services/UserService.cs` | 36 | Accessing `Rows[0]` without checking `Rows.Count > 0` (though checked later, risk remains if logic changes). | Ensure check precedes access. |
| `SampleBankingApp/Services/EmailService.cs` | 26 | `int.Parse` on config value may throw if null/invalid. | Use `int.TryParse` with default. |
| `SampleBankingApp/Program.cs` | 20 | `jwtSecret` may be null, causing `GetBytes` to throw. | Add null check or default value. |

## 6. Dead Code

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `SampleBankingApp/Helpers/StringHelper.cs` | 33 | `JoinWithSeparator` is inefficient and likely unused; `JoinWithSeparatorFixed` exists. | Remove `JoinWithSeparator`. |
| `SampleBankingApp/Helpers/StringHelper.cs` | 45 | `ObfuscateAccount` duplicates `MaskAccountNumber` functionality. | Remove one implementation. |
| `SampleBankingApp/Helpers/StringHelper.cs` | 57 | `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Remove method. |
| `SampleBankingApp/Services/AuthService.cs` | 85 | `HashPasswordSha1` is defined but never called. | Remove method. |
| `SampleBankingApp/Services/TransactionService.cs` | 90 | `FormatCurrency` is defined but never called. | Remove method. |
| `SampleBankingApp/Services/EmailService.cs` | 76 | `BuildHtmlTemplate` is only used by `SendWelcomeEmailHtml` which is likely unused. | Verify usage or remove. |
| `SampleBankingApp/Data/DatabaseHelper.cs` | 68 | `ExecuteQueryWithParams` is marked `[Obsolete]` but still present. | Remove obsolete code. |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `SampleBankingApp/Services/TransactionService.cs` | 12 | `TransactionFeeRate` is hardcoded. | Move to configuration. |
| `SampleBankingApp/Services/TransactionService.cs` | 13 | `MaxTransactionsPerDay` is hardcoded. | Move to configuration. |
| `SampleBankingApp/Services/TransactionService.cs` | 63 | Deposit limit `1000000` is hardcoded. | Move to configuration. |
| `SampleBankingApp/Services/TransactionService.cs` | 63 | Interest rate `0.05m` is hardcoded. | Move to configuration. |
| `SampleBankingApp/Services/UserService.cs` | 71 | Page size limit `50` is hardcoded. | Move to configuration. |
| `SampleBankingApp/Services/AuthService.cs` | 15 | Admin bypass password is hardcoded. | Remove entirely. |
| `SampleBankingApp/Helpers/StringHelper.cs` | 11 | Email length limit `254` is hardcoded. | Define as constant. |
| `SampleBankingApp/Helpers/StringHelper.cs` | 19 | Username length limits `3` and `20` are hardcoded. | Define as constants. |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `SampleBankingApp/Helpers/StringHelper.cs` | 25 | `new Regex` created on every call; should be static readonly. | Cache regex instances. |
| `SampleBankingApp/Helpers/StringHelper.cs` | 33 | String concatenation in loop is O(n²). | Use `string.Join` or `StringBuilder`. |
| `SampleBankingApp/Services/UserService.cs` | 80 | String concatenation in loop for audit report. | Use `StringBuilder`. |
| `SampleBankingApp/Services/UserService.cs` | 12 | Static mutable state `_auditLog` and `_requestCount` are not thread-safe. | Use thread-safe collections or remove static state. |
| `SampleBankingApp/Services/EmailService.cs` | 55 | `Console.WriteLine` used for logging. | Use `ILogger`. |
| `SampleBankingApp/Services/EmailService.cs` | 68 | `Console.WriteLine` used for logging. | Use `ILogger`. |
| `SampleBankingingApp/Program.cs` | 12 | `DatabaseHelper` registered as Singleton, holding state/connection. | Register as Scoped or Transient. |

## 9. Configuration Issues

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| `SampleBankingApp/Program.cs` | 33 | `UseDeveloperExceptionPage` called unconditionally. | Wrap in `IsDevelopment` check. |
| `SampleBankingApp/Program.cs` | 35 | HTTPS redirection commented out. | Uncomment. |
| `SampleBankingApp/Program.cs` | 37 | CORS allows any origin/method/header. | Restrict policies. |
| `SampleBankingApp/appsettings.json` | 15 | Debug log levels set for production namespaces. | Set to `Information` or `Warning` for production. |
| `SampleBankingApp/SampleBankingApp.csproj` | 10 | `Newtonsoft.Json` version `12.0.3` is outdated/vulnerable. | Update to latest stable version. |
| `SampleBankingApp/SampleBankingApp.csproj` | 8 | `DebugSymbols` and `DebugType` set in project file. | Remove; let build configuration handle this. |
| `SampleBankingApp/appsettings.json` | 1 | Production secrets in config file. | Use environment variables. |

## 10. Missing Unit Tests

No test project exists. Critical areas to test:
1.  **TransactionService.Transfer**: Verify balance checks, fee calculation, and atomic updates.
2.  **TransactionService.Deposit**: Verify interest calculation and limits.
3.  **UserService.GetUsersPage**: Verify pagination offset calculation.
4.  **AuthService.Login**: Verify SQL injection prevention and password hashing.
5.  **StringHelper**: Verify regex validation and string manipulation.
6.  **DatabaseHelper**: Verify parameterized query execution.