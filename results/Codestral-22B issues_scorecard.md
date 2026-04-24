# AI Review Scorecard

> **Branch:** `Codestral-22B` &nbsp;·&nbsp; **Commit:** `2637958`

# AI Review Scorecard

Total: 55 Found / 15 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "DatabaseHelper.cs | 14-58 | SQL injection risks in ExecuteQuery and ExecuteQueryWithParams methods | Use parameterized queries or stored procedures to prevent SQL injection attacks." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "AuthService.cs | 36-45 | Hardcoded credentials in source file | Move the admin bypass password to a secure configuration source." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "AuthService.cs | 70-72 | Weak cryptography (MD5) for password hashing | Use a stronger hashing algorithm like SHA-256 or bcrypt with a salt." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "UserService.cs | 62, 73 | SQL injection risks in ExecuteQuery calls | Use parameterized queries or stored procedures to prevent SQL injection attacks." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "DatabaseHelper.cs | 14-58 | SQL injection risks in ExecuteQuery and ExecuteQueryWithParams methods | Use parameterized queries or stored procedures to prevent SQL injection attacks." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "DatabaseHelper.cs | 14-58 | SQL injection risks in ExecuteQuery and ExecuteQueryWithParams methods | Use parameterized queries or stored procedures to prevent SQL injection attacks." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "DatabaseHelper.cs | 14-58 | SQL injection risks in ExecuteQuery and ExecuteQueryWithParams methods | Use parameterized queries or stored procedures to prevent SQL injection attacks." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "AuthService.cs | 36-45 | Hardcoded credentials in source file | Move the admin bypass password to a secure configuration source." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "Program.cs | 19-24 | JWT misconfiguration (ValidateLifetime set to false) | Set ValidateLifetime to true to ensure token expiration is enforced." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Partial | "TransactionService.cs | 17-19, 43-45 | Incorrect boundary conditions for amount validation | Check if the amount is greater than or equal to 0 instead of just greater than 0." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Partial | "TransactionService.cs | 17-19, 43-45 | Incorrect boundary conditions for amount validation | Check if the amount is greater than or equal to 0 instead of just greater than 0." |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | "TransactionService.cs | 17-19, 43-45 | Incorrect boundary conditions for amount validation | Check if the amount is greater than or equal to 0 instead of just greater than 0." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "TransactionService.cs | 17-19, 43-45 | Incorrect boundary conditions for amount validation | Check if the amount is greater than or equal to 0 instead of just greater than 0." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "UserService.cs | 26 | Off-by-one error in pagination | Use `(page - 1) * pageSize` instead of `page * pageSize` to calculate the correct offset." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Partial | "TransactionService.cs | 10, 32, 45 | Magic numbers used for transaction fee rate and maximum deposit amount | Use named constants or configuration values instead of magic numbers." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Partial | "TransactionService.cs | 17-19, 43-45 | Incorrect boundary conditions for amount validation | Check if the amount is greater than or equal to 0 instead of just greater than 0." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | "UserService.cs | 50-52, 62-64 | Duplicated validation logic for user ID | Extract the validation logic to a shared method to avoid duplication." |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "StringHelper.cs | 16-20 | String concatenation inside a loop can lead to performance issues | Use StringBuilder or string.Join to improve performance." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | "AuthService.cs | 70-72 | Weak cryptography (MD5) for password hashing | Use a stronger hashing algorithm like SHA-256 or bcrypt with a salt." |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "DatabaseHelper.cs | 14-58 | SQL injection risks in ExecuteQuery and ExecuteQueryWithParams methods | Use parameterized queries or stored procedures to prevent SQL injection attacks." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | "AuthController.cs | 20-24 | Method catches broad Exception and swallows it silently | Catch specific exceptions and log or rethrow them appropriately." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | "EmailService.cs | 29-40 | Email sending is not transactional with the database update | Wrap the email sending logic in a transaction with the database update to ensure consistency." |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Found | "EmailService.cs | 51-53 | Email sending can throw after a DB write has already committed | Handle email sending failures gracefully and consider implementing a retry mechanism or a dead letter queue." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client — internal error details leaked. | Found | "UserController.cs | 35-37, 41-43, 46-48 | Methods catch broad Exception and return a generic error message | Catch specific exceptions and log or rethrow them appropriately." |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | "DatabaseHelper.cs | 16-20, 28-32, 40-44, 51-55 | SqlConnection and SqlDataAdapter are not disposed properly | Use using blocks or try-finally blocks to ensure resources are disposed of properly." |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Partial | "AuthController.cs | 20-24 | Method catches broad Exception and swallows it silently | Catch specific exceptions and log or rethrow them appropriately." |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "DatabaseHelper.cs | 16-20, 28-32, 40-44, 51-55 | SqlConnection and SqlDataAdapter are not disposed properly | Use using blocks or try-finally blocks to ensure resources are disposed of properly." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "DatabaseHelper.cs | 16-20, 28-32, 40-44, 51-55 | SqlConnection and SqlDataAdapter are not disposed properly | Use using blocks or try-finally blocks to ensure resources are disposed of properly." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "DatabaseHelper.cs | 16-20, 28-32, 40-44, 51-55 | SqlConnection and SqlDataAdapter are not disposed properly | Use using blocks or try-finally blocks to ensure resources are disposed of properly." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service — underlying socket never released. | Found | "EmailService.cs | 17-39 | SmtpClient is held as an instance field | Dispose the SmtpClient in the constructor or use a using block to ensure the socket is released." |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "EmailService.cs | 17-39 | SmtpClient is held as an instance field | Dispose the SmtpClient in the constructor or use a using block to ensure the socket is released." |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | "DatabaseHelper.cs | 14 | Configuration value for connection string can be null | Use null coalescing operator (`??`) or null guard to provide a default value." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "TransactionController.cs | 13-15, 22-24 | UserIdClaim can be null or empty | Use null coalescing operator (`?.`) or null guard to handle potential null values." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Partial | "StringHelper.cs | 20-22, 30-32, 38-40 | Input strings can be null or empty | Use null guards or null coalescing operators to handle potential null values." |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | "StringHelper.cs | 20-22, 30-32, 38-40 | Input strings can be null or empty | Use null guards or null coalescing operators to handle potential null values." |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | "StringHelper.cs | 20-22, 30-32, 38-40 | Input strings can be null or empty | Use null guards or null coalescing operators to handle potential null values." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "TransactionController.cs | 13-15, 22-24 | UserIdClaim can be null or empty | Use null coalescing operator (`?.`) or null guard to handle potential null values." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` — model binding can produce null body. | Partial | "UserController.cs | 35-37, 41-43, 46-48 | Methods catch broad Exception and return a generic error message | Catch specific exceptions and log or rethrow them appropriately." |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants — should be in configuration. | Found | "TransactionService.cs | 10, 32, 45 | Magic numbers used for transaction fee rate and maximum deposit amount | Use named constants or configuration values instead of magic numbers." |
| M2 | `1_000_000` deposit cap hardcoded inline — no named constant. | Found | "TransactionService.cs | 10, 32, 45 | Magic numbers used for transaction fee rate and maximum deposit amount | Use named constants or configuration values instead of magic numbers." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | "EmailService.cs | 12, 13, 46 | Magic strings used for email subjects and welcome message | Use named constants or configuration values instead of magic strings." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | "StringHelper.cs | 20-22, 30-32, 38-40 | Input strings can be null or empty | Use null guards or null coalescing operators to handle potential null values." |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "UserController.cs | 17-18 | Magic numbers used for default page size and maximum page size | Use named constants or configuration values instead of magic numbers." |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Found | "AuthService.cs | 73-81 | Obsolete HashPasswordSha1 method is still present | Remove the obsolete method from the codebase." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Partial | "AuthService.cs | 70-72 | Weak cryptography (MD5) for password hashing | Use a stronger hashing algorithm like SHA-256 or bcrypt with a salt." |
| D3 | `TableExists` — never called from any service or controller. | Found | "DatabaseHelper.cs | 46-50 | Obsolete ExecuteQueryWithParams method is still present | Remove the obsolete method from the codebase." |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called; should be removed. | Found | "DatabaseHelper.cs | 46-50 | Obsolete ExecuteQueryWithParams method is still present | Remove the obsolete method from the codebase." |
| D5 | `BuildHtmlTemplate` — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Partial | "EmailService.cs | 17-39 | SmtpClient is held as an instance field | Dispose the SmtpClient in the constructor or use a using block to ensure the socket is released." |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Partial | "EmailService.cs | 17-39 | SmtpClient is held as an instance field | Dispose the SmtpClient in the constructor or use a using block to ensure the socket is released." |
| D7 | `FormatCurrency` — private, never called. | Partial | "TransactionService.cs | 72-74 | NotImplementedException thrown in RefundTransaction method | Implement the refund transaction logic or remove the method if it's not needed." |
| D8 | `IsWithinDailyLimit` — defined but never called; daily limit is therefore never enforced. | Partial | "TransactionService.cs | 72-74 | NotImplementedException thrown in RefundTransaction method | Implement the refund transaction logic or remove the method if it's not needed." |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Found | "StringHelper.cs | 49 | ObfuscateAccount — superseded by MaskAccountNumber, never called | Remove the obsolete method from the codebase." |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Found | "StringHelper.cs | 49 | ObfuscateAccount — superseded by MaskAccountNumber, never called | Remove the obsolete method from the codebase." |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "StringHelper.cs | 16-20 | String concatenation inside a loop can lead to performance issues | Use StringBuilder or string.Join to improve performance." |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | "UserService.cs | 10-13, 21-23, 58-60 | Shared mutable static state accessed from multiple threads without synchronization | Use thread-safe data structures or synchronization mechanisms to ensure thread safety." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "StringHelper.cs | 24-26 | Regex object is created inside a method called repeatedly | Create the Regex object as a static readonly field to improve performance." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "StringHelper.cs | 16-20 | String concatenation inside a loop can lead to performance issues | Use StringBuilder or string.Join to improve performance." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "EmailService.cs | 17-39 | SmtpClient is held as an instance field | Dispose the SmtpClient in the constructor or use a using block to ensure the socket is released." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "StringHelper.cs | 44-46 | Reimplementing System.Globalization.CultureInfo.CurrentCulture.TextInfo.ToTitleCase | Use the built-in method directly instead of reimplementing it." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "DatabaseHelper.cs | 38-44 | ExecuteQuerySafe method leaks resource ownership to callers without a documented contract | Document the expected behavior and handle resource disposal in the calling code." |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "AuthService.cs | 36-45 | Hardcoded credentials in source file | Move the admin bypass password to a secure configuration source." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Partial | "Program.cs | 27 | UseDeveloperExceptionPage() called unconditionally | Remove or conditionally call UseDeveloperExceptionPage() based on the environment." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "Program.cs | 19-24 | JWT misconfiguration (ValidateLifetime set to false) | Set ValidateLifetime to true to ensure token expiration is enforced." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "Program.cs | 30 | HTTPS disabled | Enable HTTPS redirection in production." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "Program.cs | 27 | UseDeveloperExceptionPage() called unconditionally | Remove or conditionally call UseDeveloperExceptionPage() based on the environment." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "Program.cs | 32 | Overly permissive CORS policy | Limit allowed origins, methods, and headers based on your application's requirements." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Partial | "SampleBankingApp.csproj | 12-15 | Outdated or vulnerable NuGet packages (System.Data.SqlClient, Newtonsoft.Json) | Update to the latest secure versions of these packages." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | "SampleBankingApp.csproj | 12-15 | Outdated or vulnerable NuGet packages (System.Data.SqlClient, Newtonsoft.Json) | Update to the latest secure versions of these packages." |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | "appsettings.json | N/A | Missing environment-specific config overrides (appsettings.Production.json) | Create environment-specific configuration files to override default settings in production." |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | No test project found. The following methods and scenarios are most critical to test: AuthService.Login, TransactionService.Transfer, TransactionService.Deposit, UserService.GetUserById, UserService.UpdateUser, UserService.DeleteUser, UserService.SearchUsers, EmailService.SendTransferNotification, EmailService.SendWelcomeEmail. These tests should cover boundary conditions, auth flows, financial calculations, and pagination scenarios. | Found | "Missing Unit Tests" section mentions "No test project found" and lists critical test scenarios." |