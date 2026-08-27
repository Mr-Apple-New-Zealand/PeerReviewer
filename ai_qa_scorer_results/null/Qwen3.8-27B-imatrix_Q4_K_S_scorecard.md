# Scorer: Qwen3.8-27B-imatrix:Q4_K_S
# Review type: null

# AI Review Scorecard

Total: 0 Found / 0 Partial / 70 Missed out of 70 issues.

## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) — `Username` and `Password` string-interpolated into SELECT in `AuthService.Login` | Missed | |
| C2 | Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` in `AuthService` | Missed | |
| C3 | Broken password hashing — MD5 with no salt in `AuthService` | Missed | |
| C4 | SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, `id` interpolated in `UserService` | Missed | |
| C5 | SQL Injection (SearchUsers) — `query` interpolated into LIKE clause in `UserService` | Missed | |
| C6 | SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` concatenated in `TransactionService` | Missed | |
| C7 | SQL Injection (RecordTransaction) — `description` interpolated in `TransactionService` | Missed | |
| C8 | Hardcoded production credentials in `appsettings.json` | Missed | |
| C9 | JWT lifetime validation disabled (`ValidateLifetime = false`) in `Program.cs` | Missed | |
| C10 | Broken Access Control — `PUT /api/user/{id}` has no ownership check in `UserController` | Missed | |
| C11 | Missing Authorization — `DELETE /api/user/{id}` has no role check in `UserController` | Missed | |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows zero-value transfers in `TransactionService.Transfer` | Missed | |
| L2 | Balance check excludes the fee in `TransactionService.Transfer` | Missed | |
| L3 | Off-by-one in pagination — `skip = page * pageSize` in `UserService.GetUsersPage` | Missed | |
| L4 | Incorrect interest rate `0.05m` instead of `0.01m` in `TransactionService.Deposit` | Missed | |
| L5 | Self-transfer allowed — no `fromUserId != ToUserId` check in `TransactionController` | Missed | |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | Duplicated validation in `GetUserById`, `UpdateUser`, `DeleteUser` in `UserService` | Missed | |
| R2 | Loop string concatenation in `JoinWithSeparator` in `StringHelper` | Missed | |
| R3 | Overly long `GenerateJwtToken` in `AuthService` | Missed | |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` swallows all exceptions and returns empty list in `UserService` | Missed | |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) in `EmailService` | Missed | |
| E3 | No database transaction around two UPDATE statements in `TransactionService.Transfer` | Missed | |
| E4 | Email failure in `Transfer` propagates exception after DB commit in `TransactionService` | Missed | |
| E5 | `catch (Exception ex)` exposes `ex.Message` to HTTP client in `UserController` | Missed | |
| E6 | `ExecuteNonQuery` closes connection only on happy path in `DatabaseHelper` | Missed | |
| E7 | No rate limiting or account lockout on failed login in `AuthController` | Missed | |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` never closed/disposed in `AuthService.Login` | Missed | |
| RL2 | `GetOpenConnection()` returns live connection; `ExecuteQuery` never disposes in `DatabaseHelper` | Missed | |
| RL3 | `ExecuteNonQuery` closes but does not Dispose; exception path skips close in `DatabaseHelper` | Missed | |
| RL4 | `SmtpClient` held as instance field on non-disposable service in `EmailService` | Missed | |
| RL5 | `MailMessage` never disposed in `SendTransferNotification` or `SendWelcomeEmail` in `EmailService` | Missed | |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return null in `AuthService.GenerateJwtToken` | Missed | |
| N2 | `fromUserTable.Rows[0]` / `toUserTable.Rows[0]` accessed without count check in `TransactionService` | Missed | |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` hides missing config key in `EmailService` | Missed | |
| N4 | `username.ToUpper()` throws NRE if null in `EmailService` | Missed | |
| N5 | `email.Length` / `username.Length` throw if null in `StringHelper` | Missed | |
| N6 | `User.FindFirst(...)?.Value` can be null; `int.Parse(null!)` throws in `TransactionController` | Missed | |
| N7 | `UpdateUser` and controller endpoints don't check `request == null` in `UserController` | Missed | |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source constants in `TransactionService` | Missed | |
| M2 | `1_000_000` deposit cap hardcoded inline in `TransactionService.Deposit` | Missed | |
| M3 | Email addresses hardcoded as literals in `EmailService` | Missed | |
| M4 | `254`, `3`, `20` as bare literals in `StringHelper` | Missed | |
| M5 | `50` as page size upper bound unnamed in `UserService` | Missed | |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called in `AuthService` | Missed | |
| D2 | Unreachable code after `return true` in `ValidateToken` in `AuthService` | Missed | |
| D3 | `TableExists` — never called in `DatabaseHelper` | Missed | |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]`, never called in `DatabaseHelper` | Missed | |
| D5 | `BuildHtmlTemplate` — private, dead transitively in `EmailService` | Missed | |
| D6 | `SendWelcomeEmailHtml` — public, never called in `EmailService` | Missed | |
| D7 | `FormatCurrency` — private, never called in `TransactionService` | Missed | |
| D8 | `IsWithinDailyLimit` — defined but never called in `TransactionService` | Missed | |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called in `StringHelper` | Missed | |
| D10 | `ToTitleCase` — never called in `StringHelper` | Missed | |
| D11 | `JoinWithSeparatorFixed` — correct implementation never used in `StringHelper` | Missed | |

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | Mutable static state `_auditLog` / `_requestCount` in `UserService` | Missed | |
| A2 | Regex compiled per-call in `StringHelper` | Missed | |
| A3 | String concatenation in loop in `StringHelper.JoinWithSeparator` | Missed | |
| A4 | Shared mutable `SmtpClient` field in `EmailService` | Missed | |
| A5 | `IsBlank` duplicates `string.IsNullOrWhiteSpace` in `StringHelper` | Missed | |
| A6 | `GetOpenConnection()` leaking connection anti-pattern in `DatabaseHelper` | Missed | |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | Production secrets in source control in `appsettings.json` | Missed | |
| CF2 | Log level `Debug` in production in `appsettings.json` | Missed | |
| CF3 | JWT `ValidateLifetime = false` in `Program.cs` | Missed | |
| CF4 | HTTPS disabled — `UseHttpsRedirection()` commented out in `Program.cs` | Missed | |
| CF5 | `UseDeveloperExceptionPage()` called unconditionally in `Program.cs` | Missed | |
| CF6 | Open CORS policy in `Program.cs` | Missed | |
| CF7 | `DebugSymbols = true` / `DebugType = full` always emitted in `.csproj` | Missed | |
| CF8 | Pinned outdated `Newtonsoft.Json 12.0.3` in `.csproj` | Missed | |
| CF9 | No `appsettings.Production.json` for environment-specific overrides | Missed | |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project or test files exist; key areas needing coverage include AuthService, TransactionService, UserService pagination, StringHelper, and controller actions | Missed | |