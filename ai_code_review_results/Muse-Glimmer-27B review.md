## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded fallback connection string contains SA password. | Remove hardcoded credentials and require configuration. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | ExecuteQuery builds SQL by interpolating tableName and whereClause enabling injection. | Use parameterized queries and whitelist table names. |
| SampleBankingApp/Data/DatabaseHelper.cs | 53 | ExecuteNonQuery executes raw SQL string without parameters allowing injection. | Use parameterized commands. |
| SampleBankingApp/Services/AuthService.cs | 17 | AdminBypassPassword constant creates a backdoor account. | Remove backdoor and use proper role based auth. |
| SampleBankingApp/Services/AuthService.cs | 32 | Login builds SQL with interpolated username and hashed password enabling injection. | Use parameterized query. |
| SampleBankingApp/Services/AuthService.cs | 30 | Password hashed with MD5 which is cryptographically broken. | Use salted strong hash like PBKDF2 or bcrypt. |
| SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection opened without using causing leak and no disposal on error. | Use using statement for connection. |
| SampleBankingApp/Program.cs | 34 | UseDeveloperExceptionPage enabled unconditionally exposing errors in production. | Enable only in Development environment. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out disabling HTTPS enforcement. | Uncomment and enforce HTTPS. |
| SampleBankingApp/Program.cs | 38 | CORS policy allows any origin method and header. | Restrict origins to trusted domains. |
| SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime is false allowing expired tokens. | Set ValidateLifetime to true. |
| SampleBankingApp/Program.cs | 28 | Encoding.UTF8.GetBytes called with jwtSecret! assuming non null. | Validate secret presence at startup. |
| SampleBankingApp/appsettings.json | 3 | Production connection string contains hardcoded SA password. | Move secret to secure vault and use environment variables. |
| SampleBankingApp/appsettings.json | 14 | Email password is hardcoded in source control. | Store secret securely outside source. |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser returns any user by id without ownership check. | Enforce user can only access own data or require admin role. |
| SampleBankingApp/Controllers/UserController.cs | 43 | UpdateUser allows updating any user id without authorization check. | Verify caller owns resource or has admin role. |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser allows deleting any user without ownership check. | Add authorization check. |
| SampleBankingApp/Services/TransactionService.cs | 47 | UPDATE statement built with string interpolation enabling SQL injection. | Use parameterized query. |
| SampleBankingApp/Services/TransactionService.cs | 48 | UPDATE statement built with string interpolation enabling SQL injection. | Use parameterized query. |
| SampleBankingApp/Services/TransactionService.cs | 71 | Deposit UPDATE built with string interpolation enabling SQL injection. | Use parameterized query. |
| SampleBankingApp/Services/TransactionService.cs | 89 | RecordTransaction builds INSERT with interpolated values enabling SQL injection. | Use parameterized query. |
| SampleBankingApp/Services/UserService.cs | 47 | UpdateUser builds UPDATE with interpolated email and username enabling SQL injection. | Use parameterized query. |
| SampleBankingApp/Services/UserService.cs | 61 | DeleteUser builds DELETE with interpolated id enabling SQL injection. | Use parameterized query. |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers calls ExecuteQuery with interpolated LIKE clause enabling SQL injection. | Use parameterized query. |

## 2. Logic Errors
| File | Line | Issue | Fix |
| SampleBankingApp/Services/UserService.cs | 72 | Pagination skip calculated as page * pageSize causing off by one. | Use (page-1)*pageSize. |
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check compares to amount not totalDebit allowing negative balance after fee. | Compare to totalDebit. |
| SampleBankingApp/Services/TransactionService.cs | 25 | Transfer allows zero amount. | Require amount >0. |
| SampleBankingApp/Services/TransactionService.cs | 36 | Rows[0] accessed without checking Rows.Count leading to exception. | Validate rows exist before access. |
| SampleBankingApp/Services/TransactionService.cs | 37 | Rows[0] accessed without checking Rows.Count. | Validate rows exist before access. |
| SampleBankingApp/Services/TransactionService.cs | 53 | Rows[0] accessed without checking Rows.Count. | Validate rows exist before access. |
| SampleBankingApp/Services/TransactionService.cs | 55 | Rows[0] accessed without checking Rows.Count. | Validate rows exist before access. |
| SampleBankingApp/Services/TransactionService.cs | 24 | Transfer does not prevent self transfer. | Reject when fromUserId equals toUserId. |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit interest bonus uses magic multiplier 1. | Clarify rate with named constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | IsValidEmail accesses Length without null check causing NullReference. | Add null guard. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | IsValidUsername accesses Length without null check. | Add null guard. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | MaskAccountNumber accesses Length without null check. | Add null guard. |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | ObfuscateAccount uses range operator without length check. | Validate length before slicing. |
| SampleBankingApp/Services/TransactionService.cs | 83 | Rows[0] accessed without checking Rows.Count in IsWithinDailyLimit. | Validate rows exist. |

## 3. Error Handling
| File | Line | Issue | Fix |
| SampleBankingApp/Services/UserService.cs | 105 | Catch block swallows exception and returns empty list hiding errors. | Log and propagate or return error. |
| SampleBankingApp/Services/EmailService.cs | 75 | Catch block swallows exception after console logging. | Log properly and consider retry. |
| SampleBankingApp/Services/AuthService.cs | 100 | ValidateToken returns true early making validation unreachable. | Remove early return. |
| SampleBankingApp/Controllers/UserController.cs | 52 | Returns raw exception message to client leaking internals. | Return generic error. |
| SampleBankingApp/Controllers/UserController.cs | 50 | Catches generic Exception. | Catch specific exceptions. |
| SampleBankingApp/Services/TransactionService.cs | 47 | Two separate UPDATEs without transaction risk partial update. | Wrap in transaction. |
| SampleBankingApp/Services/TransactionService.cs | 52 | Email sent after DB writes without rollback on failure. | Use transaction and send email after commit. |
| SampleBankingApp/Data/DatabaseHelper.cs | 21 | GetOpenConnection returns connection without using pattern risking leak. | Return using or require caller dispose. |
| SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection opened without using risking leak on exception. | Use using. |

## 4. Resource Leaks
| File | Line | Issue | Fix |
| SampleBankingApp/Data/DatabaseHelper.cs | 21 | GetOpenConnection returns SqlConnection without disposal contract. | Use using or implement disposable pattern. |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | ExecuteQuery opens connection via GetOpenConnection and never closes. | Use using. |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | ExecuteNonQuery opens connection and closes only on success path. | Use using. |
| SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection created and opened without using causing leak. | Use using. |
| SampleBankingApp/Services/AuthService.cs | 38 | SqlCommand and SqlDataReader not disposed. | Use using. |
| SampleBankingApp/Services/EmailService.cs | 22 | SmtpClient stored as instance field never disposed. | Create per use and dispose. |
| SampleBankingApp/Services/EmailService.cs | 39 | MailMessage created without using causing resource leak. | Use using. |
| SampleBankingApp/Services/EmailService.cs | 69 | MailMessage created without using. | Use using. |
| SampleBankingApp/Services/EmailService.cs | 89 | MailMessage created without using. | Use using. |

## 5. Null Reference Risks
| File | Line | Issue | Fix |
| SampleBankingApp/Program.cs | 16 | jwtSecret read from config may be null causing NullReference later. | Validate config at startup. |
| SampleBankingApp/Program.cs | 28 | Encoding.UTF8.GetBytes called with jwtSecret! assuming non null. | Null check before use. |
| SampleBankingApp/Services/EmailService.cs | 22 | SmtpClient constructed with config value that may be null. | Validate config. |
| SampleBankingApp/Services/EmailService.cs | 26 | NetworkCredential constructed with config values that may be null. | Validate config. |
| SampleBankingApp/Services/AuthService.cs | 70 | SecretKey read from config with ! operator risking NullReference. | Validate config. |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim! used without null check causing NullReference. | Validate claim presence. |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | userIdClaim! used without null check. | Validate claim presence. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | email.Length accessed without null check. | Guard null. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | username.Length accessed without null check. | Guard null. |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | accountNumber.Length accessed without null check. | Guard null. |
| SampleBankingApp/Services/TransactionService.cs | 36 | Rows[0] accessed without checking Rows.Count. | Check count first. |
| SampleBankingApp/Services/TransactionService.cs | 83 | Rows[0] accessed without checking Rows.Count. | Check count first. |

## 6. Dead Code
| File | Line | Issue | Fix |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | Method JoinWithSeparator has no callers. | Remove or use. |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | Method JoinWithSeparatorFixed has no callers. | Remove or use. |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | Method ObfuscateAccount has no callers. | Remove or use. |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | Method ToTitleCase has no callers. | Remove or use. |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | Method IsBlank has no callers. | Remove or use. |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | Method IsValidEmail has no callers. | Remove or use. |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | Method IsValidUsername has no callers. | Remove or use. |
| SampleBankingApp/Data/DatabaseHelper.cs | 59 | Method TableExists has no callers. | Remove or use. |
| SampleBankingApp/Data/DatabaseHelper.cs | 68 | Method ExecuteQueryWithParams is obsolete and unused. | Remove. |
| SampleBankingApp/Services/AuthService.cs | 91 | Method HashPasswordSha1 has no callers. | Remove. |
| SampleBankingApp/Services/AuthService.cs | 98 | Method ValidateToken has no callers and contains unreachable code. | Remove. |
| SampleBankingApp/Services/EmailService.cs | 63 | Method SendWelcomeEmail has no callers. | Remove or use. |
| SampleBankingApp/Services/EmailService.cs | 86 | Method SendWelcomeEmailHtml has no callers. | Remove or use. |
| SampleBankingApp/Services/EmailService.cs | 81 | Method BuildHtmlTemplate is only used by dead SendWelcomeEmailHtml. | Remove or use. |
| SampleBankingApp/Services/TransactionService.cs | 77 | Method IsWithinDailyLimit has no callers. | Remove or use. |
| SampleBankingApp/Services/TransactionService.cs | 94 | Method FormatCurrency has no callers. | Remove or use. |
| SampleBankingApp/Services/AuthService.cs | 105 | Code after unconditional return in ValidateToken is unreachable. | Remove dead code. |

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
| SampleBankingApp/Services/TransactionService.cs | 68 | Magic number 0.05m used for interest rate. | Define named constant. |
| SampleBankingApp/Services/UserService.cs | 70 | Magic number 50 used for max page size. | Define constant. |
| SampleBankingApp/Services/UserService.cs | 22 | Magic number 0 used for id validation. | Use named constant. |
| SampleBankingApp/Services/UserService.cs | 23 | Magic number 1000000 used for id upper bound. | Define constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | Magic number 254 used for email length limit. | Define constant. |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | Magic numbers 3 and 20 used for username length. | Define constants. |
| SampleBankingApp/Services/EmailService.cs | 40 | Hardcoded sender email notifications@company.com. | Move to config. |
| SampleBankingApp/Services/EmailService.cs | 69 | Hardcoded sender email repeated. | Use config. |
| SampleBankingApp/Services/EmailService.cs | 89 | Hardcoded sender email repeated. | Use config. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded connection string with password. | Use config only. |
| SampleBankingApp/appsettings.json | 3 | Connection string contains password. | Use secret management. |
| SampleBankingApp/appsettings.json | 14 | Email password hardcoded. | Use secret management. |

## 8. Anti-patterns and Code Quality
| File | Line | Issue | Fix |
| SampleBankingApp/Helpers/StringHelper.cs | 31 | String concatenation in loop causes O(n²) performance. | Use StringBuilder or string.Join. |
| SampleBankingApp/Services/UserService.cs | 88 | String concatenation in loop for audit report causes O(n²). | Use StringBuilder. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | new Regex instantiated per call causing allocation overhead. | Use static readonly Regex. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | new Regex instantiated per call. | Use static readonly Regex. |
| SampleBankingApp/Services/UserService.cs | 10 | Static mutable List _auditLog accessed without synchronization. | Use thread safe collection. |
| SampleBankingApp/Services/UserService.cs | 11 | Static mutable int _requestCount accessed without synchronization. | Use Interlocked or lock. |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | GetOpenConnection leaks resource ownership to caller. | Return using or manage internally. |
| SampleBankingApp/Services/UserService.cs | 20 | Duplicate id validation logic repeated across methods. | Extract to private method. |
| SampleBankingApp/Services/TransactionService.cs | 23 | Transfer method has multiple responsibilities validation DB email. | Split into smaller methods. |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank reimplements string.IsNullOrWhiteSpace. | Use built in. |

## 9. Configuration Issues
| File | Line | Issue | Fix |
| SampleBankingApp/Program.cs | 34 | UseDeveloperExceptionPage called unconditionally. | Enable only in Development. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out. | Enable HTTPS redirection. |
| SampleBankingApp/Program.cs | 38 | CORS allows any origin method header. | Restrict origins. |
| SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime is false. | Enable lifetime validation. |
| SampleBankingApp/SampleBankingApp.csproj | 8 | DebugSymbols true in release build. | Set false for Release. |
| SampleBankingApp/SampleBankingApp.csproj | 15 | Newtonsoft.Json version 12.0.3 is outdated. | Update package. |
| SampleBankingApp/appsettings.json | 18 | LogLevel Default set to Debug for production. | Set to Information or Warning. |

## 10. Missing Unit Tests
| File | Line | Issue | Fix |
| N/A | N/A | No test project exists. | Create test project. |
| SampleBankingApp/Services/AuthService.cs | 28 | Login with MD5 and SQL injection needs boundary tests. | Add unit tests for auth flows. |
| SampleBankingApp/Services/TransactionService.cs | 23 | Transfer balance and fee calculation needs tests. | Add tests for financial calculations. |
| SampleBankingApp/Services/UserService.cs | 68 | GetUsersPage pagination off by one needs tests. | Add tests for pagination boundaries. |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit amount validation and interest needs tests. | Add tests for deposit edge cases. |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser authorization missing needs tests. | Add tests for access control.