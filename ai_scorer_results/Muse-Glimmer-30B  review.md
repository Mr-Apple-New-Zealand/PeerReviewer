## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Fallback connection string contains hardcoded SA password Admin1234! | Remove hardcoded credentials and require configuration |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | ExecuteQuery builds SQL with tableName and whereClause interpolation | Use parameterized queries and whitelist table names |
| SampleBankingApp/Data/DatabaseHelper.cs | 53 | ExecuteNonQuery executes raw SQL string | Require parameterized commands |
| SampleBankingApp/Services/AuthService.cs | 17 | AdminBypassPassword constant enables backdoor login | Remove backdoor credential |
| SampleBankingApp/Services/AuthService.cs | 30 | Passwords hashed with MD5 | Use salted strong hash such as PBKDF2 |
| SampleBankingApp/Services/AuthService.cs | 32 | Login SQL built with username and hashed password interpolation | Use parameterized query |
| SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime is false | Enable lifetime validation |
| SampleBankingApp/Program.cs | 34 | UseDeveloperExceptionPage called unconditionally | Enable only in development |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out | Enable HTTPS redirection |
| SampleBankingApp/Program.cs | 38 | CORS allows any origin method and header | Restrict CORS to trusted origins |
| SampleBankingApp/appsettings.json | 3 | Connection string with password committed to source | Move secret to environment or secret store |
| SampleBankingApp/appsettings.json | 14 | Email password committed to source | Move secret out of source |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser returns any user without ownership check | Enforce ownership or admin role |
| SampleBankingApp/Controllers/UserController.cs | 43 | UpdateUser updates any user without ownership check | Verify caller owns resource |
| SampleBankingApp/Controllers/UserController.cs | 61 | DeleteUser deletes any user without ownership check | Enforce authorization |
| SampleBankingApp/Services/TransactionService.cs | 47 | UPDATE Users built with string interpolation | Use parameterized query |
| SampleBankingApp/Services/TransactionService.cs | 48 | UPDATE Users built with string interpolation | Use parameterized query |
| SampleBankingApp/Services/TransactionService.cs | 71 | UPDATE Users built with string interpolation | Use parameterized query |
| SampleBankingApp/Services/TransactionService.cs | 89 | INSERT Transactions built with string interpolation | Use parameterized query |
| SampleBankingApp/Services/UserService.cs | 47 | UPDATE Users built with string interpolation | Use parameterized query |
| SampleBankingApp/Services/UserService.cs | 61 | DELETE Users built with string interpolation | Use parameterized query |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers uses LIKE with query interpolation | Use parameterized query |

## 2. Logic Errors
| File | Line | Issue | Fix |
| SampleBankingApp/Services/UserService.cs | 72 | Skip calculated as page * pageSize causing off-by-one | Use (page-1) * pageSize |
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check compares fromBalance >= amount not amount+fee | Compare against total debit including fee |
| SampleBankingApp/Services/TransactionService.cs | 25 | Transfer allows amount zero | Require amount > 0 |
| SampleBankingApp/Services/TransactionService.cs | 68 | Interest bonus uses magic *1 | Define explicit rate constant |
| SampleBankingApp/Services/TransactionService.cs | 36 | Rows[0] accessed without checking Rows.Count | Verify rows exist before access |
| SampleBankingApp/Services/TransactionService.cs | 23 | Transfer does not prevent sending to self | Add self-transfer guard |
| SampleBankingApp/Services/UserService.cs | 70 | PageSize capped to 50 with magic literal | Move limit to configuration |

## 3. Error Handling
| File | Line | Issue | Fix |
| SampleBankingApp/Services/UserService.cs | 105 | Catch Exception returns empty list hiding errors | Log error and propagate or return error |
| SampleBankingApp/Controllers/UserController.cs | 52 | Catch returns ex.Message to client | Return generic error message |
| SampleBankingApp/Controllers/UserController.cs | 48 | Catch returns ex.Message to client | Return generic error message |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | NotImplementedException mapped to 500 with static text | Return 501 Not Implemented |
| SampleBankingApp/Services/EmailService.cs | 77 | Catch Exception prints to console and swallows | Log properly and handle failure |
| SampleBankingApp/Services/AuthService.cs | 103 | ValidateToken returns true early making validation unreachable | Remove early return and implement validation |
| SampleBankingApp/Services/TransactionService.cs | 52 | Email sent after DB updates without transaction | Wrap updates and email in transaction with compensation |

## 4. Resource Leaks
| File | Line | Issue | Fix |
| SampleBankingApp/Data/DatabaseHelper.cs | 22 | GetOpenConnection returns open SqlConnection without disposal contract | Use using or document ownership |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | ExecuteQuery uses GetOpenConnection without closing | Use using for connection and command |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | ExecuteNonQuery uses GetOpenConnection without disposing command | Use using for connection and command |
| SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection opened without using | Wrap in using |
| SampleBankingApp/Services/AuthService.cs | 37 | SqlCommand not disposed | Use using |
| SampleBankingApp/Services/AuthService.cs | 38 | SqlDataReader not disposed | Use using |
| SampleBankingApp/Services/EmailService.cs | 22 | SmtpClient stored as field never disposed | Create per use and dispose |
| SampleBankingApp/Services/EmailService.cs | 39 | MailMessage created without dispose | Use using |
| SampleBankingApp/Services/EmailService.cs | 69 | MailMessage created without dispose | Use using |
| SampleBankingApp/Services/EmailService.cs | 89 | MailMessage created without dispose | Use using |

## 5. Null Reference Risks
| File | Line | Issue | Fix |
| SampleBankingApp/Program.cs | 16 | Jwt secret read may be null | Validate configuration presence |
| SampleBankingApp/Program.cs | 28 | Encoding.UTF8.GetBytes(jwtSecret!) may throw | Guard null before use |
| SampleBankingApp/Services/AuthService.cs | 70 | Encoding.UTF8.GetBytes on config value may be null | Guard null before use |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | int.Parse(userIdClaim!) assumes claim present | Validate claim and handle null |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | int.Parse(userIdClaim!) assumes claim present | Validate claim and handle null |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | email.Length accessed without null check | Check null before length |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | username.Length accessed without null check | Check null before length |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | accountNumber.Length accessed without null check | Check null before length |
| SampleBankingApp/Services/TransactionService.cs | 36 | Rows[0] accessed without count check | Check Rows.Count first |

## 6. Dead Code
| File | Line | Issue | Fix |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method has no callers | Remove or use |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method has no callers | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method has no callers | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method has no callers | Remove |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method has no callers | Remove |
| SampleBankingApp/Services/AuthService.cs | 98 | ValidateToken method has no callers and unreachable code | Remove or implement |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method has no callers | Remove or use |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method has no callers | Remove |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method has no callers | Remove |
| SampleBankingApp/Data/DatabaseHelper.cs | 68 | ExecuteQueryWithParams is obsolete and unused | Remove |
| SampleBankingApp/Data/DatabaseHelper.cs | 59 | TableExists method has no callers | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | IsValidEmail method has no callers | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | IsValidUsername method has no callers | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | JoinWithSeparatorFixed method has no callers | Remove |

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
| SampleBankingApp/Controllers/UserController.cs | 32 | Default pageSize 20 is hardcoded | Move to configuration |
| SampleBankingApp/Services/UserService.cs | 70 | PageSize cap 50 is hardcoded | Move to configuration |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit cap 1000000 is hardcoded | Move to configuration |
| SampleBankingApp/Services/TransactionService.cs | 68 | Interest rate 0.05m is hardcoded | Define named constant |
| SampleBankingApp/Services/EmailService.cs | 13 | MaxRetries 3 is hardcoded | Move to configuration |
| SampleBankingApp/Services/EmailService.cs | 14 | SmtpTimeoutMs 5000 is hardcoded | Move to configuration |
| SampleBankingApp/Services/EmailService.cs | 10 | Email subject strings are hardcoded | Centralize constants |
| SampleBankingApp/Services/AuthService.cs | 17 | AdminBypassPassword is hardcoded | Remove backdoor |
| SampleBankingApp/Services/EmailService.cs | 40 | From address notifications@company.com is hardcoded | Move to configuration |

## 8. Anti-patterns and Code Quality
| File | Line | Issue | Fix |
| SampleBankingApp/Helpers/StringHelper.cs | 32 | String concatenation in loop causes O(n²) | Use StringBuilder or string.Join |
| SampleBankingApp/Services/UserService.cs | 88 | Report built with += in loop | Use StringBuilder |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | new Regex created per call | Make static readonly |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | new Regex created per call | Make static readonly |
| SampleBankingApp/Services/UserService.cs | 10 | Static List auditLog is mutable shared state | Use thread-safe collection |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank reimplements IsNullOrWhiteSpace | Use built-in method |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | GetOpenConnection leaks resource ownership | Document contract or use using |
| SampleBankingApp/Services/UserService.cs | 20 | Id validation duplicated across methods | Extract shared validation method |
| SampleBankingApp/Services/TransactionService.cs | 23 | Transfer mixes validation DB update and email | Split into separate responsibilities |

## 9. Configuration Issues
| File | Line | Issue | Fix |
| SampleBankingApp/Program.cs | 34 | UseDeveloperExceptionPage enabled unconditionally | Enable only in Development |
| SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime false | Enable lifetime validation |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out | Enable HTTPS redirection |
| SampleBankingApp/Program.cs | 38 | CORS allows any origin method header | Restrict to trusted origins |
| SampleBankingApp/SampleBankingApp.csproj | 8 | DebugSymbols true for release | Disable for release builds |
| SampleBankingApp/SampleBankingApp.csproj | 15 | Newtonsoft.Json 12.0.3 is outdated | Update to supported version |
| SampleBankingApp/appsettings.json | 18 | LogLevel Debug for production namespaces | Set to Information for production |

## 10. Missing Unit Tests
| File | Line | Issue | Fix |
| N/A | N/A | No test project exists | Create test project |
| SampleBankingApp/Services/AuthService.cs | 28 | Login logic not tested | Add unit tests for success failure and SQL injection resistance |
| SampleBankingApp/Services/TransactionService.cs | 23 | Transfer logic not tested | Add tests for balance fee and insufficient funds |
| SampleBankingApp/Services/TransactionService.cs | 63 | Deposit logic not tested | Add tests for caps and interest |
| SampleBankingApp/Services/UserService.cs | 68 | GetUsersPage pagination not tested | Add tests for page boundaries |
| SampleBankingApp/Services/AuthService.cs | 68 | GenerateJwtToken not tested | Add tests for claims and expiry |