# Code Review Report - Branch 'main' (Commit 67ece22980b87505c9e6a0bc95962632ab91b998)

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 32 | SQL injection via string interpolation in Login: `sql = $"SELECT * FROM Users WHERE Username = '{username}' AND Password = '{hashedPassword}' AND IsActive = 1"` | Use parameterized queries via ExecuteQuerySafe |
| AuthService.cs | 17 | Hardcoded admin bypass password constant: `AdminBypassPassword = "SuperAdmin2024"` | Remove backdoor; enforce proper authentication |
| AuthService.cs | 61-66 | MD5 hashing used for password storage (broken cryptography) | Use bcrypt, PBKDF2, or Argon2 |
| AuthService.cs | 91-96 | SHA1 hashing method exists but is weak | Remove or upgrade to secure algorithm |
| Program.cs | 24 | JWT ValidateLifetime set to false | Set to true to enforce token expiration |
| Program.cs | 38 | CORS policy allows any origin, method, and header | Restrict to specific origins in production |
| Program.cs | 34 | UseDeveloperExceptionPage called unconditionally | Conditionally enable based on environment |
| appsettings.json | 3 | Hardcoded production database password | Use environment variables or secrets manager |
| appsettings.json | 6 | Weak JWT secret key: "mysecretkey" | Use cryptographically random key (32+ bytes) |
| appsettings.json | 14 | Hardcoded email password | Use environment variables or secrets manager |
| SampleBankingApp.csproj | 8-9 | Debug symbols enabled in project file | Disable for release builds |
| UserController.cs | 38-54 | UpdateUser endpoint missing authorization attribute | Add [Authorize] attribute |
| UserController.cs | 56-69 | DeleteUser endpoint missing authorization attribute | Add [Authorize] attribute |
| UserController.cs | 71-76 | SearchUsers endpoint missing authorization attribute | Add [Authorize] attribute |
| UserController.cs | 78-82 | GetAuditLog endpoint missing authorization attribute | Add [Authorize] attribute |
| UserController.cs | 38-54 | UpdateUser has no ownership verification | Check that requesting user owns the profile |
| UserController.cs | 56-69 | DeleteUser has no ownership verification | Check that requesting user owns the profile |
| TransactionController.cs | 48-60 | Refund endpoint accessible to any authenticated user | Add admin role check |
| DatabaseHelper.cs | 29 | ExecuteQuery concatenates tableName and whereClause directly into SQL | Use only safe query methods with parameters |
| TransactionService.cs | 47-48 | SQL injection via string interpolation in balance updates | Use parameterized queries |
| TransactionService.cs | 89-91 | SQL injection via string interpolation in RecordTransaction | Use parameterized queries |
| UserService.cs | 47 | SQL injection via string interpolation in UpdateUser | Use parameterized queries |
| UserService.cs | 61 | SQL injection via string interpolation in DeleteUser | Use parameterized queries |
| UserService.cs | 99 | Uses vulnerable ExecuteQuery with LIKE clause | Use ExecuteQuerySafe with parameters |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserService.cs | 72 | Off-by-one error in pagination: `skip = page * pageSize` should be `(page - 1) * pageSize` | Change to `(page - 1) * pageSize` |
| TransactionService.cs | 42 | Balance check uses `fromBalance >= amount` but deduction is `amount + fee` | Check `fromBalance >= totalDebit` |
| TransactionService.cs | 23-61 | No validation that fromUserId != toUserId | Add self-transfer prevention check |
| TransactionService.cs | 25 | Only checks `amount < 0` but should also reject zero | Add `amount <= 0` check |
| UserService.cs | 70 | No validation for pageSize <= 0 | Add check for pageSize > 0 minimum |
| TransactionService.cs | 42-44 | Transfer can result in negative balance when fromBalance is between amount and totalDebit | Use proper balance check |
| UserService.cs | 85-93 | Audit report uses string concatenation in loop | Use StringBuilder for efficiency |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| UserController.cs | 50-53 | Catches broad Exception and returns ex.Message to HTTP client | Return generic error message; log details |
| UserController.cs | 52 | Raw exception message exposed to client | Return "An error occurred" and log exception |
| UserService.cs | 105-108 | Catches all exceptions and returns empty list | Distinguish error from no results; log exception |
| TransactionService.cs | 47-48 | Two separate ExecuteNonQuery calls without transaction wrapping | Wrap in database transaction |
| TransactionService.cs | 52-55 | Email sending occurs after DB write with no rollback on failure | Send email before commit or use outbox pattern |
| AuthService.cs | 34-38 | SqlConnection opened but never closed or disposed | Wrap in using statement or dispose |
| AuthService.cs | 34-58 | Connection and reader not disposed on all code paths | Use try-finally or using blocks |
| AuthController.cs | 19-31 | No rate limiting on login endpoint | Add rate limiting middleware |
| AuthController.cs | 19-31 | No account lockout after failed attempts | Implement lockout after N failures |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| AuthService.cs | 34 | SqlConnection created but never disposed | Wrap in using statement |
| AuthService.cs | 38 | SqlDataReader not closed/disposed | Use using statement or explicit close |
| DatabaseHelper.cs | 19-24 | GetOpenConnection returns connection caller must dispose with no contract | Document ownership transfer or return IDisposable |
| DatabaseHelper.cs | 26-34 | ExecuteQuery creates connection via GetOpenConnection but never disposes it | Use using or refactor to return DataTable with proper disposal |
| DatabaseHelper.cs | 50-57 | ExecuteNonQuery creates connection via GetOpenConnection but never disposes it | Use using or refactor to return DataTable with proper disposal |
| EmailService.cs | 16 | SmtpClient held as instance field (not thread-safe, socket not released) | Create SmtpClient per send or use proper disposal |
| EmailService.cs | 39-43 | MailMessage created but never disposed | Wrap in using statement |
| EmailService.cs | 69 | MailMessage created but never disposed | Wrap in using statement |
| EmailService.cs | 89 | MailMessage created but never disposed | Wrap in using statement |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 36-37 | fromUserTable.Rows[0] and toUserTable.Rows[0] accessed without checking Rows.Count > 0 | Add count check before access |
| UserService.cs | 83 | table.Rows[0]["TxCount"] accessed without count check | Add count check before access |
| Program.cs | 16 | jwtSecret used with ! but no runtime null guard | Add null check with proper exception |
| AuthService.cs | 70 | _config["Jwt:SecretKey"]! used without null check | Add explicit null check |
| EmailService.cs | 22-31 | SmtpClient constructed with potentially null config values | Add null checks for all config values |
| UserService.cs | 31-32 | Returns null but caller may not check | Document nullability or throw instead |
| TransactionService.cs | 28-37 | No check if fromUserTable.Rows.Count == 0 before accessing Rows[0] | Add validation before row access |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 29-36 | JoinWithSeparator method never called | Remove or add unit tests to verify usage |
| StringHelper.cs | 54-57 | ObfuscateAccount method never called | Remove or add unit tests to verify usage |
| StringHelper.cs | 59-63 | ToTitleCase method never called | Remove or add unit tests to verify usage |
| StringHelper.cs | 65-71 | IsBlank method never called | Remove or add unit tests to verify usage |
| AuthService.cs | 91-96 | HashPasswordSha1 method never called | Remove or add unit tests to verify usage |
| AuthService.cs | 98-108 | ValidateToken method never called | Remove or add unit tests to verify usage |
| AuthService.cs | 103 | Unconditional return true before actual validation code | Remove dead code after return |
| TransactionService.cs | 94-97 | FormatCurrency method never called | Remove or add unit tests to verify usage |
| EmailService.cs | 81-84 | BuildHtmlTemplate method never called | Remove or add unit tests to verify usage |
| EmailService.cs | 86-92 | SendWelcomeEmailHtml method never called | Remove or add unit tests to verify usage |
| DatabaseHelper.cs | 67-78 | ExecuteQueryWithParams marked [Obsolete] but still exists | Remove obsolete method |
| UserService.cs | 10-11 | Static _auditLog and _requestCount not read externally except in GetAuditReport | Verify if audit tracking is actually used |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| TransactionService.cs | 11 | Transaction fee rate 0.015m hardcoded | Extract to configuration |
| TransactionService.cs | 12 | MaxTransactionsPerDay = 10 hardcoded | Extract to configuration |
| TransactionService.cs | 65 | Deposit cap 1000000 hardcoded | Extract to configuration |
| TransactionService.cs | 68 | Interest bonus rate 0.05m hardcoded | Extract to named constant |
| UserService.cs | 70 | Max page size 50 hardcoded | Extract to configuration |
| UserService.cs | 22 | User ID range 1000000 hardcoded | Extract to named constant |
| AuthService.cs | 84 | Token expiry 30 days hardcoded | Extract to configuration |
| EmailService.cs | 13 | MaxRetries = 3 hardcoded | Extract to configuration |
| EmailService.cs | 14 | SmtpTimeoutMs = 5000 hardcoded | Extract to configuration |
| AuthService.cs | 17 | Admin bypass password string repeated | Remove backdoor entirely |
| EmailService.cs | 40 | "notifications@company.com" hardcoded in multiple places | Extract to configuration |
| TransactionService.cs | 89 | Transaction type strings "Transfer", "Deposit" hardcoded | Use constants or enums |
| TransactionService.cs | 90 | Status "Completed" hardcoded | Use constant or enum |
| UserService.cs | 45 | Audit log format string hardcoded | Use constant or structured logging |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| StringHelper.cs | 29-36 | String concatenation in loop (O(n²)) | Use string.Join or StringBuilder |
| UserService.cs | 87-91 | String concatenation in loop for audit report | Use StringBuilder |
| StringHelper.cs | 16 | new Regex created inside IsValidEmail method | Make regex static readonly field |
| StringHelper.cs | 25 | new Regex created inside IsValidUsername method | Make regex static readonly field |
| UserService.cs | 10-11 | Static mutable fields _auditLog and _requestCount without synchronization | Use thread-safe collection or remove |
| StringHelper.cs | 65-71 | IsBlank duplicates string.IsNullOrWhiteSpace | Remove duplicate method |
| StringHelper.cs | 29-36 | JoinWithSeparator duplicates string.Join | Remove duplicate method |
| DatabaseHelper.cs | 19-24 | GetOpenConnection returns SqlConnection with no documented ownership contract | Document that caller must dispose or return IDisposable |
| UserService.cs | 18-23 | GetUserById and UpdateUser share identical ID validation block | Extract to shared private method |
| UserService.cs | 18-23 | GetUserById and DeleteUser share identical ID validation block | Extract to shared private method |
| TransactionService.cs | 23-61 | Transfer method handles multiple responsibilities (validation, balance check, debit, credit, recording, emailing) | Split into focused methods |
| EmailService.cs | 34-61 | SendTransferNotification handles business logic and retry loop | Separate retry logic into helper |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| Program.cs | 34 | UseDeveloperExceptionPage called unconditionally | Wrap in if (app.Environment.IsDevelopment()) |
| Program.cs | 24 | ValidateLifetime = false on JWT | Set to true for production |
| Program.cs | 36 | HTTPS redirection commented out | Uncomment or ensure SSL termination at load balancer |
| Program.cs | 38 | CORS allows any origin, method, header | Restrict to known origins in production |
| appsettings.json | 17-21 | Debug log level set for production | Set to Warning or Error for production |
| SampleBankingApp.csproj | 15 | Newtonsoft.Json 12.0.3 is outdated with known vulnerabilities | Upgrade to latest stable version |
| SampleBankingApp.csproj | 14 | System.Data.SqlClient 4.8.6 - newer Microsoft.Data.SqlClient recommended | Migrate to Microsoft.Data.SqlClient |
| appsettings.json | N/A | No appsettings.Production.json override | Add environment-specific configuration |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|------|------|-------|-----|
| N/A | N/A | No test project exists in provided files | Create test project with comprehensive coverage |

### Critical Methods/Scenarios Requiring Tests:

| File | Line | Scenario | Priority |
|------|------|----------|----------|
| UserService.cs | 72 | Pagination off-by-one: verify page 1 returns first records, page 2 skips first pageSize | High |
| TransactionService.cs | 42 | Transfer with balance >= amount but < amount+fee (should fail) | High |
| TransactionService.cs | 23-61 | Transfer to self should be rejected | High |
| TransactionService.cs | 68 | Deposit interest calculation: verify 5% bonus applied correctly | High |
| AuthService.cs | 28-59 | Login with admin bypass password | High |
| AuthService.cs | 61-66 | Password hashing verification | High |
| AuthService.cs | 98-108 | Token validation with expired token | High |
| UserService.cs | 99 | SQL injection via SearchUsers query parameter | High |
| UserService.cs | 38-54 | UpdateUser authorization: verify users can only update own profile | High |
| UserService.cs | 56-69 | DeleteUser authorization: verify users can only delete own profile | High |
| TransactionService.cs | 47-48 | Transfer atomicity: verify no partial transfers on failure | High |
| EmailService.cs | 34-61 | Email retry logic: verify retries up to MaxRetries | Medium |
| UserService.cs | 70 | PageSize boundary: verify behavior at 0, 1, 50, 51 | Medium |
| TransactionService.cs | 65 | Deposit boundary: verify rejection of 0 and > 1000000 | Medium |