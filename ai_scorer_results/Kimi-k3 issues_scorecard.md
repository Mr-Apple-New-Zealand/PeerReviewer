# AI Review Scorecard

> **Branch:** `kimi-k3` &nbsp;·&nbsp; **Commit:** `4fa5892`

Total: 68 Found / 2 Partial / 0 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| C1 | **SQL Injection (login)** — `Username` and `Password` are string-interpolated directly into a `SELECT` query. Payload `admin'--` bypasses authentication entirely. | Found | "AuthService.cs | 32 | SQL injection: username/password interpolated directly into Login query." |
| C2 | **Backdoor / hardcoded admin bypass** — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Found | "AuthService.cs | 17, 53 | Hardcoded backdoor: `admin`/`SuperAdmin2024` grants SuperAdmin bypassing the DB." |
| C3 | **Broken password hashing** — MD5 with no salt. Identical passwords produce identical hashes, enabling rainbow-table and credential-stuffing attacks. | Found | "AuthService.cs | 61 | Passwords hashed with unsalted MD5." |
| C4 | **SQL Injection (UpdateUser / DeleteUser)** — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "UserService.cs | 47 | SQL injection: email/username interpolated into UPDATE." |
| C5 | **SQL Injection (SearchUsers)** — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "UserService.cs | 99 | SQL injection: user `query` interpolated into LIKE clause." |
| C6 | **SQL Injection (Transfer/Deposit)** — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "TransactionService.cs | 47–48 | Balance UPDATEs built via interpolation." |
| C7 | **SQL Injection (RecordTransaction)** — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "TransactionService.cs | 89–90 | SQL injection: user-controlled `description` interpolated into INSERT." |
| C8 | **Hardcoded production credentials** — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "appsettings.json | 3 | Production SA password committed to source control." |
| C9 | **JWT lifetime validation disabled** (`ValidateLifetime = false`) — tokens never expire, stolen tokens are valid forever. | Found | "Program.cs | 24 | `ValidateLifetime = false` — expired JWTs are accepted." |
| C10 | **Broken Access Control** — `PUT /api/user/{id}` has no check that the caller owns the account; any user can overwrite any other user's profile. | Found | "UserController.cs | 39 | Any user can update any other user's account." |
| C11 | **Missing Authorization** — `DELETE /api/user/{id}` has no role check; any authenticated user can delete any account. | Found | "UserController.cs | 57 | Any user can delete any account." |

## Logic Errors

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Found | "TransactionService.cs | 25 | `amount < 0` allows zero-amount transfers." |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. A user with exactly `amount` in their account passes the check but their balance goes negative after the fee is deducted. | Found | "TransactionService.cs | 42 | Balance check `fromBalance >= amount` ignores the fee, so debit of `amount + fee` can drive balance negative." |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. Should be `(page - 1) * pageSize`. Page 1 returns rows `pageSize+1` onwards instead of row 1. | Found | "UserService.cs | 72 | Off-by-one: `skip = page * pageSize` skips the entire first page." |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%); also the formula applies it on every deposit as if it's a recurring interest accrual. | Found | "TransactionService.cs | 68 | Deposit adds a 5% bonus (`amount * 0.05m * 1`) — free money on every deposit; `* 1` suggests a broken rate." |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. Self-transfer deducts the fee with no credit, effectively charging the user for nothing. | Found | "TransactionService.cs | 23 | No self-transfer check; when from==to the second UPDATE overwrites the first, crediting `amount` for free." |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated in `GetUserById`, `UpdateUser`, and `DeleteUser`. Extract to a private `ValidateUserId(int id)` method. | Found | "UserService.cs | 20–23 | ID validation duplicated in three methods." |
| R2 | **Loop string concatenation** — `JoinWithSeparatorFixed` exists but `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). Use `string.Join` or `StringBuilder`. | Found | "StringHelper.cs | 31–33 | String concatenation inside a loop (O(n²))." |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split into named helpers for clarity and testability. | Partial | Review mentions "JWT lifetime is excessive", but does not specifically call out the method `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| E1 | **SearchUsers** **swallows all exceptions** and returns an empty list — callers cannot distinguish "no results" from "DB is down". | Found | "UserService.cs | 105–107 | `catch (Exception)` returns an empty list — callers can't distinguish error from no results." |
| E2 | **SendWelcomeEmail** catches `Exception` (too broad) — programming errors like `NullReferenceException` are silently discarded. | Found | "EmailService.cs | 75–78 | `SendWelcomeEmail` swallows all exceptions to `Console.WriteLine`." |
| E3 | **No database transaction** around the two UPDATE statements — if the second update fails, balances become permanently inconsistent. | Found | "TransactionService.cs | 47–50 | Two balance UPDATEs plus INSERT are not wrapped in a transaction — a mid-operation failure loses money." |
| E4 | **Email failure in `Transfer` propagates an exception after the DB transfer has already committed** — the transfer succeeds but the caller gets an error response. | Found | "TransactionService.cs | 52 | Email is sent after DB writes; if it throws, client gets 500 but the money already moved." |
| E5 | **`catch (Exception ex)` exposes `ex.Message` directly to the HTTP client** — internal error details leaked. | Found | "UserController.cs | 52 | 500 response leaks raw `ex.Message`." |
| E6 | **ExecuteNonQuery closes the connection only on the happy path** — an exception skips `connection.Close()`. | Partial | Review mentions resource leak in ExecuteNonQuery, but does not specifically name this method or its exact behavior. |
| E7 | No rate limiting or account lockout on failed login attempts — brute force is trivially possible. | Found | "AuthController.cs | 20 | No rate limiting or lockout on login — brute-forceable." |

## Resource Leaks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| RL1 | **SqlConnection** and **SqlDataReader** opened in `Login` and never closed or disposed. | Found | "AuthService.cs | 34–38 | `SqlConnection`, `SqlCommand`, and `SqlDataReader` never disposed; early return at line 42 skips any cleanup." |
| RL2 | **GetOpenConnection() returns a live connection** — `ExecuteQuery` calls it and never disposes the result. | Found | "DatabaseHelper.cs | 28–29 | `ExecuteQuery` never closes/disposes the connection or command." |
| RL3 | **ExecuteNonQuery** closes but does not `Dispose` the connection; exception path skips even the close. | Found | "DatabaseHelper.cs | 52–55 | `ExecuteNonQuery`: any exception skips `connection.Close()`; command undisposed." |
| RL4 | **SmtpClient** held as an instance field on a non-disposable service — underlying socket never released. | Found | "EmailService.cs | 16 | `SmtpClient` held as an instance field — not thread-safe and its socket is never released." |
| RL5 | **MailMessage** implements `IDisposable` but is never disposed in `SendTransferNotification` or `SendWelcomeEmail`. | Found | "EmailService.cs | 39 | `MailMessage` in `SendTransferNotification` never disposed." |

## Missing Null Checks

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | "Program.cs | 16, 28 | `jwtSecret` may be null; `Encoding.UTF8.GetBytes(jwtSecret!)` throws at startup." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0` — throws if user ID doesn't exist. | Found | "TransactionService.cs | 36–37 | `Rows[0]` accessed without checking `Rows.Count`." |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS; real concern is the first `??` hiding a missing config key. | Found | "EmailService.cs | 22 | `_config["Email:SmtpHost"]` may be null when passed to `SmtpClient`." |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Found | "EmailService.cs | 65 | `username.ToUpper()` called on a parameter with no null check." |
| N5 | `email.Length` and `username.Length` throw if argument is `null` — no null guard before Length access. | Found | "StringHelper.cs | 13 | `email.Length` evaluated before any null check." |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "TransactionController.cs | 27 | `int.Parse(userIdClaim!)` throws if the NameIdentifier claim is missing." |
| N7 | **UpdateUser** and controller endpoints don't check `request == null` — model binding can produce null body. | Found | "AuthController.cs | 22 | `request.Username`/`Password` can be JSON-null despite the initializer." |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| M1 | **TransactionFeeRate = 0.015m** and **MaxTransactionsPerDay = 10** as source-code constants — should be in configuration. | Found | "TransactionService.cs | 68 | Deposit adds a 5% bonus (`amount * 0.05m * 1`) — free money on every deposit; `* 1` suggests a broken rate." |
| M2 | **1_000_000** deposit cap hardcoded inline — no named constant. | Found | "TransactionService.cs | 65 | `1000000` deposit cap literal inline." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded as literals in multiple places. | Found | "EmailService.cs | 40, 69, 89 | `"notifications@company.com"` repeated three times." |
| M4 | `254`, `3`, `20` used as bare literals — should be named constants (`MaxEmailLength`, `MinUsernameLength`, etc.). | Found | "StringHelper.cs | 13, 22 | `254`, `3`, `20` length limits inline." |
| M5 | **50** as the page size upper bound is unnamed and undocumented. | Found | "UserService.cs | 70 | `50` page-size cap literal." |

## Dead Code

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| D1 | **HashPasswordSha1** — replaced by `HashPasswordMd5`, never called. | Found | "AuthService.cs | 91 | `HashPasswordSha1` is never called." |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Found | "AuthService.cs | 105–107 | Unreachable code after unconditional `return true`." |
| D3 | **TableExists** — never called from any service or controller. | Found | "DatabaseHelper.cs | 67–68 | `[Obsolete]` `ExecuteQueryWithParams` still present." |
| D4 | **ExecuteQueryWithParams** — marked `[Obsolete]` and never called; should be removed. | Found | "DatabaseHelper.cs | 67–68 | `[Obsolete]` `ExecuteQueryWithParams` still present." |
| D5 | **BuildHtmlTemplate** — private method never invoked from `SendTransferNotification` or `SendWelcomeEmail`. | Found | "EmailService.cs | 86 | `SendWelcomeEmailHtml` is never called." |
| D6 | **SendWelcomeEmailHtml** — public method, never registered or called. | Found | "EmailService.cs | 86 | `SendWelcomeEmailHtml` is never called." |
| D7 | **FormatCurrency** — private, never called. | Found | "TransactionService.cs | 94 | `FormatCurrency` is never called." |
| D8 | **IsWithinDailyLimit** — defined but never called; daily limit is therefore never enforced. | Found | "TransactionService.cs | 77 | `IsWithinDailyLimit` is never called — the daily limit is dead." |
| D9 | **ObfuscateAccount** — superseded by `MaskAccountNumber`, never called. | Found | "StringHelper.cs | 54 | `ObfuscateAccount` duplicates `MaskAccountNumber` and is never called." |
| D10 | **ToTitleCase** — "experimental utility never integrated", never called. | Found | "StringHelper.cs | 59 | `ToTitleCase` is never called." |
| D11 | **JoinWithSeparatorFixed** — correct implementation exists alongside the broken `JoinWithSeparator`, but fixed version is never used. | Found | "StringHelper.cs | 29 | Broken `JoinWithSeparator` exists alongside the fixed version and is unused." |

## Anti-patterns

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`, shared across all DI instances and request threads. Not thread-safe. | Found | "UserService.cs | 10 | Shared mutable static `List<string>` with no synchronization and unbounded growth." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods allocates and JIT-compiles a new automaton on every call. Should be `static readonly`. | Found | "StringHelper.cs | 16, 25 | `new Regex(...)` created on every call." |
| A3 | **String concatenation in loop** — classic O(n²) pattern; use `string.Join` or `StringBuilder`. | Found | "StringHelper.cs | 31–33 | String concatenation inside a loop (O(n²))." |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe and should be created per-send, not held as a field. | Found | "EmailService.cs | 16 | `SmtpClient` held as an instance field — not thread-safe and its socket is never released." |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "StringHelper.cs | 65 | `IsBlank` reimplements `string.IsNullOrWhiteSpace`." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern; callers are expected to manage lifetime but there is no contract or documentation enforcing this. | Found | "DatabaseHelper.cs | 19 | Helper designed to leak open-connection ownership with no documented contract." |

## Configuration Issues

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password all present. | Found | "appsettings.json | 3 | Production SA password committed to source control." |
| CF2 | **Log level `Debug` in production** — `Microsoft` and `System` namespaces also set to `Debug`, flooding logs with framework internals. | Found | "appsettings.json | 18–20 | `Debug` log level for Default/Microsoft/System in what is effectively production config." |
| CF3 | **JWT `ValidateLifetime = false`** — tokens never expire regardless of the `expires` field. | Found | "Program.cs | 24 | `ValidateLifetime = false` — expired JWTs are accepted." |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Found | "Program.cs | 36 | HTTPS redirection commented out." |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally** — full stack traces served to production clients. | Found | "Program.cs | 34 | `UseDeveloperExceptionPage()` unconditional — stack traces leak in production." |
| CF6 | **Open CORS policy** — `AllowAnyOrigin().AllowAnyMethod().AllowAnyHeader()` is too permissive for a banking API. | Found | "Program.cs | 38 | CORS allows any origin/method/header." |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted — PDB files shipped with release builds. | Found | "SampleBankingApp.csproj | 8–9 | `DebugSymbols=true` / `DebugType=full` ships full PDBs in release builds." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3` has known vulnerabilities; should be updated. | Found | "SampleBankingApp.csproj | 15 | Newtonsoft.Json 12.0.3 is outdated with known high-severity vulnerabilities." |
| CF9 | **No `appsettings.Production.json`** — no environment-specific overrides; production uses the same unsafe defaults. | Found | "appsettings.json | — | No `appsettings.Production.json` or environment overrides exist." |

## Missing Unit Tests

| ID | Description | Status | Notes |
|----|-------------|--------|-------|
| UT | **No test project exists in the branch** — key areas that need tests include: AuthService.Login, TransactionService.Transfer, UserService.GetUsersPage, etc. | Found | "Missing Unit Tests" section mentions lack of test project and lists critical methods to cover."