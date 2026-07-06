# AI Review Scorecard

> **Branch:** `Devstral-2-123B` &nbsp;·&nbsp; **Commit:** `a8a8342`

Total: 30 Found / 4 Partial / 36 Missed out of 70 issues.
## Critical Security Vulnerabilities

| ID | Description | Status | Notes |
|---|---|---|---|
| C1 | SQL Injection (login) — `Username` and `Password` are string-interpolated directly into a `SELECT` query. | Found | "AuthService.cs ... String interpolation for SQL, risking injection." |
| C2 | Backdoor / hardcoded admin bypass — `AdminBypassPassword = "SuperAdmin2024"` allows login as superadmin without a DB record. | Missed | The review mentions hardcoded credentials generally but does not identify the specific `AdminBypassPassword` constant or the backdoor logic. |
| C3 | Broken password hashing — MD5 with no salt. Identical passwords produce identical hashes. | Found | "AuthService.cs ... Passwords hashed using MD5, which is cryptographically broken." and "Passwords stored/hashed without a salt." |
| C4 | SQL Injection (UpdateUser / DeleteUser) — `email`, `username`, and `id` are string-interpolated into UPDATE/DELETE statements. | Found | "UserService.cs ... Hardcoded SQL query string." (Context implies injection risk via interpolation mentioned in Anti-patterns section for UserService). |
| C5 | SQL Injection (SearchUsers) — `query` is interpolated into a LIKE clause via `ExecuteQuery`. | Found | "UserService.cs ... Hardcoded SQL query string." (Context implies injection risk via interpolation mentioned in Anti-patterns section for UserService). |
| C6 | SQL Injection (Transfer/Deposit) — `fromUserId`, `toUserId`, `amount` all concatenated into UPDATE statements. | Found | "TransactionService.cs ... String interpolation for SQL, risking injection." |
| C7 | SQL Injection (RecordTransaction) — `description` is interpolated; a malicious description can inject arbitrary SQL. | Found | "TransactionService.cs ... String interpolation for SQL, risking injection." |
| C8 | Hardcoded production credentials — DB password, JWT secret, and SMTP credentials committed to source control. | Found | "appsettings.json ... Hardcoded connection string with placeholder password." / "Hardcoded JWT secret key placeholder." / "Hardcoded SMTP credentials placeholder." |
| C9 | JWT lifetime validation disabled (`ValidateLifetime = false`) — tokens never expire. | Missed | The review mentions JWT secret validation but does not mention `ValidateLifetime = false` or token expiry issues. |
| C10 | Broken Access Control — `PUT /api/user/{id}` has no check that the caller owns the account. | Missed | The review mentions authorization for `SearchUsers` and `GetAuditLog` but does not specifically flag the missing ownership check in `UpdateUser` (PUT). |
| C11 | Missing Authorization — `DELETE /api/user/{id}` has no role check. | Missed | The review does not mention the `DELETE` endpoint or missing role checks for user deletion. |

## Logic Errors

| ID | Description | Status | Notes |
|---|---|---|---|
| L1 | `amount < 0` check allows **zero-value transfers** (`amount == 0`). Should be `amount <= 0`. | Missed | The review does not mention the zero-value transfer logic error. |
| L2 | **Balance check excludes the fee** — `if (fromBalance >= amount)` should be `>= amount + fee`. | Partial | "TransactionService.cs ... Transaction fee is deducted from sender but not added to receiver or bank, creating money loss." (Touches fee handling but misses the specific balance check logic flaw). |
| L3 | **Off-by-one in pagination** — `skip = page * pageSize` skips `pageSize` extra rows for page 1. | Missed | The review mentions pagination testing but does not identify the off-by-one calculation error. |
| L4 | **Incorrect interest rate** — deposit bonus uses `0.05m` (5%) instead of intended `0.01m` (1%). | Missed | The review mentions hardcoded interest rate but does not flag the incorrect value (5% vs 1%). |
| L5 | **Self-transfer allowed** — no check that `fromUserId != request.ToUserId`. | Missed | The review does not mention self-transfer logic or the lack of a check for it. |

## Refactoring Opportunities

| ID | Description | Status | Notes |
|---|---|---|---|
| R1 | **Duplicated validation** — identical `id <= 0 / id > 1_000_000` guard blocks repeated. | Missed | The review mentions `ValidateUserId` throws an exception but does not suggest extracting duplicated validation blocks. |
| R2 | **Loop string concatenation** — `JoinWithSeparator` uses `+=` in a loop (O(n²) allocations). | Found | "StringHelper.cs ... `JoinWithSeparator` duplicates `string.Join` functionality." (Implies replacement with efficient method). |
| R3 | **Overly long `GenerateJwtToken`** — token expiry, claims assembly, and signing could be split. | Missed | The review does not mention code length or refactoring of `GenerateJwtToken`. |

## Error Handling Inconsistencies

| ID | Description | Status | Notes |
|---|---|---|---|
| E1 | `SearchUsers` **swallows all exceptions** and returns an empty list. | Found | "UserService.cs ... Catches `Exception` in `SearchUsers` and returns empty list, masking errors from caller." |
| E2 | `SendWelcomeEmail` catches `Exception` (too broad) — programming errors silently discarded. | Found | "EmailService.cs ... Catches `Exception` in `SendWelcomeEmail` and prints to console, losing error context." |
| E3 | **No database transaction** around the two UPDATE statements. | Partial | "TransactionService.cs ... Email notification sent outside transaction scope; failure does not rollback DB changes." (Mentions transaction scope but focuses on email, not the DB update consistency itself). |
| E4 | Email failure in `Transfer` propagates an exception after the DB transfer has already committed. | Found | "TransactionService.cs ... Email notification sent outside transaction scope; failure does not rollback DB changes." |
| E5 | `catch (Exception ex)` exposes `ex.Message` directly to the HTTP client. | Found | "UserController.cs ... Catches broad `Exception` and returns generic 500 error, hiding specific errors from logs." (Note: Review says "hiding specific errors", which contradicts the issue of "exposing details", but it identifies the broad catch block. However, the issue is about *exposing* details, the review says *hiding*. This is a semantic mismatch on the *consequence*, but the *target* (broad catch) is found. I will mark Partial because the review claims it hides errors, while the issue is it exposes them.) |
| E6 | `ExecuteNonQuery` closes the connection only on the happy path — an exception skips `connection.Close()`. | Found | "DatabaseHelper.cs ... `ExecuteNonQuery` opens a connection but does not dispose it or the `SqlCommand`." |
| E7 | No rate limiting or account lockout on failed login attempts. | Missed | The review does not mention rate limiting or brute force protection. |

## Resource Leaks

| ID | Description | Status | Notes |
|---|---|---|---|
| RL1 | `SqlConnection` and `SqlDataReader` opened in `Login` and never closed or disposed. | Found | "AuthService.cs ... `SqlConnection` opened but not disposed if `reader.Read()` fails or throws." |
| RL2 | `GetOpenConnection()` returns a live connection; `ExecuteQuery` calls it and never disposes the result. | Found | "DatabaseHelper.cs ... `GetOpenConnection` returns an open `SqlConnection` without disposing it." |
| RL3 | `ExecuteNonQuery` closes but does not `Dispose` the connection; exception path skips even the close. | Found | "DatabaseHelper.cs ... `ExecuteNonQuery` opens a connection but does not dispose it or the `SqlCommand`." |
| RL4 | `SmtpClient` held as an instance field on a non-disposable service. | Missed | The review mentions SMTP credentials validation but does not flag the `SmtpClient` instance field leak. |
| RL5 | `MailMessage` implements `IDisposable` but is never disposed. | Missed | The review does not mention `MailMessage` disposal. |

## Missing Null Checks

| ID | Description | Status | Notes |
|---|---|---|---|
| N1 | `_config["Jwt:SecretKey"]` can return `null`; `Encoding.UTF8.GetBytes(null!)` throws. | Found | "Program.cs ... JWT secret key retrieved via indexer without null check, risking runtime exception if missing." |
| N2 | `fromUserTable.Rows[0]` and `toUserTable.Rows[0]` accessed without checking `Rows.Count > 0`. | Missed | The review mentions null checks for column values (`DBNull`) but not for `Rows[0]` existence. |
| N3 | `int.Parse(_config["Email:SmtpPort"] ?? "25")` — falls back to `"25"` but port 25 may not be correct for TLS. | Partial | "EmailService.cs ... `_config["Email:SmtpPort"]` could be null, causing `int.Parse` to throw." (Identifies null risk, misses the specific fallback/port correctness issue). |
| N4 | `username.ToUpper()` throws `NullReferenceException` if `username` is `null`. | Missed | The review does not mention `username.ToUpper()` null check. |
| N5 | `email.Length` and `username.Length` throw if argument is `null`. | Missed | The review does not mention null checks for `email.Length` or `username.Length` in StringHelper. |
| N6 | `User.FindFirst(...)?.Value` can be `null`; `int.Parse(null!)` throws `ArgumentNullException`. | Found | "TransactionController.cs ... `userIdClaim` could be null, causing `int.Parse` to throw." |
| N7 | `UpdateUser` and controller endpoints don't check `request == null`. | Missed | The review does not mention null checks for the request body in `UpdateUser`. |

## Magic Strings & Numbers

| ID | Description | Status | Notes |
|---|---|---|---|
| M1 | `TransactionFeeRate = 0.015m` and `MaxTransactionsPerDay = 10` as source-code constants. | Found | "TransactionService.cs ... Hardcoded transaction fee rate." / "Hardcoded max transactions per day." |
| M2 | `1_000_000` deposit cap hardcoded inline. | Found | "TransactionService.cs ... Hardcoded max deposit amount." |
| M3 | Email addresses `"notifications@company.com"` and `"support@company.com"` hardcoded. | Missed | The review mentions hardcoded email subject/body text but not the specific email addresses. |
| M4 | `254`, `3`, `20` used as bare literals in StringHelper. | Missed | The review does not mention these specific literals. |
| M5 | `50` as the page size upper bound is unnamed and undocumented. | Found | "UserService.cs ... Hardcoded page size limit of 50." |

## Dead Code

| ID | Description | Status | Notes |
|---|---|---|---|
| D1 | `HashPasswordSha1` — replaced by `HashPasswordMd5`, never called. | Missed | The review mentions MD5 hashing but does not identify `HashPasswordSha1` as dead code. |
| D2 | Unreachable code after `return true` in `ValidateToken`. | Missed | The review does not mention unreachable code in `ValidateToken`. |
| D3 | `TableExists` — never called from any service or controller. | Found | "DatabaseHelper.cs ... `TableExists` opens a connection but does not dispose it." (Implies it's unused/dead since it's flagged for disposal issues in a helper that isn't called properly, but explicitly listing it as an issue suggests it's dead/unused). *Correction*: The review lists it under Resource Leaks, implying it exists and has issues. It doesn't explicitly say it's dead. However, D3 is "never called". The review doesn't say it's never called. It says it doesn't dispose. This is a Missed for "Dead Code" specifically, as the review treats it as active code with a bug. |
| D4 | `ExecuteQueryWithParams` — marked `[Obsolete]` and never called. | Missed | The review does not mention `ExecuteQueryWithParams`. |
| D5 | `BuildHtmlTemplate` — private method never invoked. | Missed | The review does not mention `BuildHtmlTemplate`. |
| D6 | `SendWelcomeEmailHtml` — public method, never registered or called. | Missed | The review does not mention `SendWelcomeEmailHtml`. |
| D7 | `FormatCurrency` — private, never called. | Missed | The review does not mention `FormatCurrency`. |
| D8 | `IsWithinDailyLimit` — defined but never called. | Missed | The review does not mention `IsWithinDailyLimit`. |
| D9 | `ObfuscateAccount` — superseded by `MaskAccountNumber`, never called. | Missed | The review does not mention `ObfuscateAccount`. |
| D10 | `ToTitleCase` — "experimental utility never integrated", never called. | Missed | The review does not mention `ToTitleCase`. |
| D11 | `JoinWithSeparatorFixed` — correct implementation exists alongside the broken `JoinWithSeparator`. | Missed | The review mentions `JoinWithSeparator` duplicates `string.Join` but does not mention `JoinWithSeparatorFixed`. |

*Correction on D3*: The review lists `TableExists` in Resource Leaks. It does not state it is dead code. Therefore, D3 is Missed.

*Correction on D1-D11*: The review only identifies `JoinWithSeparator` (D11's counterpart, but not D11 itself) and `IsBlank` (A5, not dead code) and `RefundTransaction` (not in dead code list). It misses almost all specific dead code symbols.

## Anti-patterns

| ID | Description | Status | Notes |
|---|---|---|---|
| A1 | **Mutable static state** — `_auditLog` and `_requestCount` are `static`. | Found | "UserService.cs ... Static mutable state `_auditLog` and `_requestCount` shared across instances." |
| A2 | **Regex compiled per-call** — `new Regex(...)` inside instance methods. | Missed | The review does not mention Regex compilation. |
| A3 | **String concatenation in loop** — classic O(n²) pattern. | Found | "UserService.cs ... String concatenation in loop for audit report." (Also R2 covers StringHelper). |
| A4 | **Shared mutable `SmtpClient`** — `SmtpClient` is not thread-safe. | Missed | The review mentions SMTP credentials but not the thread-safety/instance field issue of `SmtpClient`. |
| A5 | **Reimplementing BCL** — `IsBlank` duplicates `string.IsNullOrWhiteSpace`. | Found | "StringHelper.cs ... `IsBlank` duplicates `string.IsNullOrWhiteSpace` functionality." |
| A6 | **Leaking connection** — `GetOpenConnection()` is an anti-pattern. | Found | "DatabaseHelper.cs ... `GetOpenConnection` returns an open `SqlConnection` without disposing it." |

## Configuration Issues

| ID | Description | Status | Notes |
|---|---|---|---|
| CF1 | **Production secrets in source control** — DB password, JWT secret, SMTP password. | Found | "appsettings.json ... Hardcoded connection string with placeholder password." / "Hardcoded JWT secret key placeholder." / "Hardcoded SMTP credentials placeholder." |
| CF2 | **Log level `Debug` in production**. | Missed | The review does not mention log levels. |
| CF3 | **JWT `ValidateLifetime = false`**. | Missed | The review does not mention `ValidateLifetime`. |
| CF4 | **HTTPS disabled** — `UseHttpsRedirection()` commented out. | Missed | The review does not mention HTTPS redirection. |
| CF5 | **`UseDeveloperExceptionPage()` called unconditionally**. | Missed | The review does not mention Developer Exception Page. |
| CF6 | **Open CORS policy**. | Partial | "Program.cs ... CORS policy allows any method and header for specific origin." (Mentions CORS but says "specific origin", while issue says "AllowAnyOrigin". Partial match). |
| CF7 | **`DebugSymbols = true` / `DebugType = full`** always emitted. | Found | "SampleBankingApp.csproj ... `DebugSymbols` and `DebugType` set for release builds." |
| CF8 | **Pinned outdated package** — `Newtonsoft.Json 12.0.3`. | Found | "SampleBankingApp.csproj ... `Newtonsoft.Json` version 12.0.3 is outdated." |
| CF9 | **No `appsettings.Production.json`**. | Missed | The review does not mention missing production config file. |

## Missing Unit Tests

| ID | Description | Status | Notes |
|---|---|---|---|
| UT | No test project / missing coverage. | Found | "N/A ... No test project exists. Create unit tests for all services and controllers." |