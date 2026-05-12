## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 47 | SQL injection via string interpolation in login query. | Use parameterized queries. |
| SampleBankingApp/Services/AuthService.cs | 50 | Hardcoded admin bypass password in source code. | Remove hardcoded bypass logic; enforce auth. |
| SampleBankingApp/Services/AuthService.cs | 60 | MD5 hashing for passwords is cryptographically broken. | Use BCrypt or Argon2. |
| SampleBankingApp/Services/AuthService.cs | 114 | JWT `ValidateLifetime` is set to false. | Set `ValidateLifetime = true`. |
| SampleBankingApp/Program.cs | 15 | `UseDeveloperExceptionPage()` enabled for production. | Remove or conditionally enable in dev. |
| SampleBankingApp/Program.cs | 22 | `AllowAnyOrigin` and `AllowAnyMethod` in CORS policy. | Restrict origins and methods. |
| SampleBankingApp/Services/TransactionService.cs | 104 | SQL injection in `RecordTransaction` via string formatting. | Use parameterized queries. |
| SampleBankingApp/Program.cs | 24 | `EnableSsl` is false in SMTP configuration. | Enable SSL/TLS for SMTP. |
| SampleBankingApp/Program.cs | 20 | Debug symbols enabled in `DebugType=full`. | Use `DebugType=portable` or `skipped`. |
| SampleBankingApp/Services/UserService.cs | 69 | SQL injection in `UpdateUser` via string formatting. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 80 | SQL injection in `DeleteUser` via string formatting. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 93 | SQL injection in `SearchUsers` via string formatting. | Use parameterized queries. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded SQL credentials in fallback string. | Remove fallback; use config only. |
| SampleBankingApp/Data/DatabaseHelper.cs | 23 | `GetOpenConnection` returns connection without `using`. | Return `using` scope or dispose caller. |
| SampleBankingApp/Services/EmailService.cs | 29 | `EnableSsl` is false in constructor. | Enable SSL in constructor. |

## 2. Logic Errors
| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 71 | Balance check `>= amount` but deduction includes fee. | Check `>= amount + fee`. |
| SampleBankingApp/Services/TransactionService.cs | 76 | `fromBalance - totalDebit` can result in negative if logic is flawed. | Ensure `totalDebit` logic is correct. |
| SampleBankingApp/Services/UserService.cs | 20 | `id <= 0` check is correct, but `id > 1000000` is arbitrary magic. | Define valid ID range constant. |
| SampleBankingApp/Services/UserService.cs | 38 | `id > 1000000` check is arbitrary magic. | Define valid ID range constant. |
| SampleBankingApp/Services/UserService.cs | 50 | `id > 1000000` check is arbitrary magic. | Define valid ID range constant. |
| SampleBankingApp/Services/UserService.cs | 62 | `id > 1000000` check is arbitrary magic. | Define valid ID range constant. |
| SampleBankingApp/Services/UserService.cs | 74 | `id > 1000000` check is arbitrary magic. | Define valid ID range constant. |
| SampleBankingApp/Services/UserService.cs | 83 | `id > 1000000` check is arbitrary magic. | Define valid ID range constant. |
| SampleBankingApp/Services/UserService.cs | 90 | `id > 1000000` check is arbitrary magic. | Define valid ID range constant. |

## 3. Error Handling
| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/TransactionController.cs | 40 | `catch (NotImplementedException)` returns hardcoded string. | Return proper `NotImplementedException` status. |
| SampleBankingApp/Controllers/UserController.cs | 54 | `catch (Exception)` returns raw `ex.Message`. | Log error and return generic message. |
| SampleBankingApp/Controllers/UserController.cs | 63 | `catch (Exception)` returns raw `ex.Message`. | Log error and return generic message. |
| SampleBankingApp/Services/AuthService.cs | 59 | Connection opened but never disposed in `Login`. | Use `using` block for connection. |
| SampleBankingApp/Services/TransactionService.cs | 105 | `RecordTransaction` has no transaction rollback on failure. | Wrap in `TransactionScope`. |
| SampleBankingApp/Services/EmailService.cs | 58 | `SendTransferNotification` swallows `SmtpException` in loop. | Re-throw or handle gracefully. |
| SampleBankingApp/Services/EmailService.cs | 75 | `SendWelcomeEmail` swallows exceptions silently. | Log error and return status. |
| SampleBankingApp/Services/TransactionService.cs | 112 | `RecordTransaction` inserts without transaction context. | Wrap in transaction. |

## 4. Resource Leaks
| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 59 | `SqlConnection` opened but not disposed. | Use `using` block. |
| SampleBankingApp/Services/TransactionService.cs | 105 | `ExecuteNonQuery` called without transaction context. | Use `TransactionScope`. |
| SampleBankingApp/Services/EmailService.cs | 29 | `SmtpClient` instance field not disposed. | Add `Dispose` override. |
| SampleBankingApp/Services/EmailService.cs | 75 | `MailMessage` created but not disposed. | Use `using` block. |

## 5. Null Reference Risks
| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 15 | `UseDeveloperExceptionPage()` called unconditionally. | Guard with `IsDevelopment`. |
| SampleBankingApp/Services/AuthService.cs | 47 | `configuration.GetConnectionString` may return null. | Use `??` or check null. |
| SampleBankingApp/Services/AuthService.cs | 60 | `jwtSecret` passed directly to `GetBytes` without null check. | Use `jwtSecret!` or check null. |
| SampleBankingApp/Services/AuthService.cs | 73 | `jwtSecret` passed directly to `GetBytes` without null check. | Use `jwtSecret!` or check null. |
| SampleBankingApp/Services/EmailService.cs | 29 | `SmtpPort` parsed from null config without check. | Use `?? "25"`. |
| SampleBankingApp/Services/TransactionService.cs | 71 | `fromUserTable.Rows[0]` accessed without count check. | Check `Rows.Count > 0`. |
| SampleBankingApp/Services/TransactionService.cs | 72 | `toUserTable.Rows[0]` accessed without count check. | Check `Rows.Count > 0`. |
| SampleBankingApp/Services/UserService.cs | 69 | `table.Rows[0]` accessed without count check. | Check `Rows.Count > 0`. |

## 6. Dead Code
| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 114 | `ValidateToken` returns `true` immediately, ignoring logic. | Fix logic to validate token. |
| SampleBankingApp/Helpers/StringHelper.cs | 37 | `JoinWithSeparator` is unreachable; `JoinWithSeparatorFixed` exists. | Remove `JoinWithSeparator`. |
| SampleBankingApp/Services/TransactionService.cs | 112 | `RefundTransaction` throws `NotImplementedException`. | Implement or remove method. |

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 33 | `0.015m` fee rate is magic. | Define constant `TransactionFeeRate`. |
| SampleBankingApp/Services/TransactionService.cs | 34 | `10` transactions limit is magic. | Define constant `MaxTransactionsPerDay`. |
| SampleBankingApp/Services/TransactionService.cs | 61 | `0.05m` interest rate is magic. | Define constant `InterestRate`. |
| SampleBankingApp/Services/TransactionService.cs | 62 | `1` multiplier is magic. | Remove or define constant. |
| SampleBankingApp/Services/TransactionService.cs | 67 | `1000000` deposit cap is magic. | Define constant `MaxDepositAmount`. |
| SampleBankingApp/Services/UserService.cs | 20 | `1000000` ID limit is magic. | Define constant `MaxUserId`. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | `254` email length limit is magic. | Define constant `MaxEmailLength`. |
| SampleBankingApp/Helpers/StringHelper.cs | 18 | `3` and `20` username limits are magic. | Define constants. |

## 8. Anti-patterns and Code Quality
| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | String concatenation in loop. | Use `StringBuilder`. |
| SampleBankingApp/Helpers/StringHelper.cs | 28 | Regex created inside method. | Make static readonly. |
| SampleBankingApp/Services/TransactionService.cs | 104 | SQL injection in `RecordTransaction`. | Use parameterized queries. |
| SampleBankingApp/Services/TransactionService.cs | 112 | SQL injection in `RecordTransaction`. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 69 | SQL injection in `UpdateUser`. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 80 | SQL injection in `DeleteUser`. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 93 | SQL injection in `SearchUsers`. | Use parameterized queries. |
| SampleBankingApp/Services/UserService.cs | 108 | String concatenation in `GetAuditReport`. | Use `StringBuilder`. |

## 9. Configuration Issues
| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Program.cs | 15 | `UseDeveloperExceptionPage()` enabled unconditionally. | Guard with `IsDevelopment`. |
| SampleBankingApp/Program.cs | 22 | `AllowAnyOrigin` and `AllowAnyMethod` in CORS. | Restrict origins/methods. |
| SampleBankingApp/Program.cs | 20 | `EnableSsl` is false in SMTP config. | Enable SSL. |
| SampleBankingApp/appsettings.json | 4 | Hardcoded `TrustServerCertificate=True`. | Remove for security. |
| SampleBankingApp/appsettings.json | 9 | `SecretKey` is too short. | Use stronger key. |
| SampleBankingApp/appsettings.json | 13 | `LogLevel` set to Debug for production. | Set to Warning/Information. |
| SampleBankingApp/appsettings.json | 18 | `AllowedHosts` is wildcard. | Restrict hosts. |

## 10. Missing Unit Tests
| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/AuthService.cs | 47 | SQL injection in login query needs test. | Add test for injection. |
| SampleBankingApp/Services/AuthService.cs | 60 | MD5 hashing needs test for collision. | Add test for weak hash. |
| SampleBankingApp/Services/TransactionService.cs | 71 | Balance check logic needs test. | Add test for insufficient funds. |
| SampleBankingApp/Services/TransactionService.cs | 104 | SQL injection in `RecordTransaction` needs test. | Add test for injection. |
| SampleBankingApp/Services/UserService.cs | 69 | SQL injection in `UpdateUser` needs test. | Add test for injection. |
| SampleBankingApp/Services/UserService.cs | 93 | SQL injection in `SearchUsers` needs test. | Add test for injection. |
| SampleBankingApp/Services/UserService.cs | 108 | Audit log string concatenation needs test. | Add test for performance. |