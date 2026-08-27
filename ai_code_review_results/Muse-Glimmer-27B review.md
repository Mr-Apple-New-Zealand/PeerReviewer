## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Fallback connection string contains hardcoded SA password Admin1234! | Remove hardcoded credentials and require configuration |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | ExecuteQuery builds SQL by interpolating tableName and whereClause enabling SQL injection | Use parameterized queries and whitelist table names |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | ExecuteNonQuery accepts raw SQL string enabling injection | Use parameterized commands |
| SampleBankingApp/Program.cs | 34 | UseDeveloperExceptionPage called unconditionally exposing stack traces in production | Enable only in Development environment |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out allowing HTTP traffic | Enable HTTPS redirection |
| SampleBankingApp/Program.cs | 38 | CORS policy allows any origin method and header | Restrict CORS to trusted origins |
| SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime set to false allowing expired tokens | Set ValidateLifetime to true |
| SampleBankingApp/Program.cs | 28 | JWT secret passed to Encoding.UTF8.GetBytes without null check | Validate config value before use |
| SampleBankingApp/Services/AuthService.cs | 17 | Admin bypass password hardcoded as constant enabling backdoor | Remove backdoor and use proper role based access |
| SampleBankingApp/Services/AuthService.cs | 30 | Password hashed with MD5 which is cryptographically broken | Use salted strong hash like PBKDF2 or bcrypt |
| SampleBankingApp/Services/AuthService.cs | 32 | Login query built with string interpolation causing SQL injection | Use parameterized query |
| SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection opened but never closed or disposed | Use using statement |
| SampleBankingApp/Services/AuthService.cs | 70 | JWT secret read from config without null validation | Validate config presence |
| SampleBankingApp/Services/TransactionService.cs | 47 | UPDATE statement built with string interpolation causing SQL injection | Use parameterized query |
| SampleBankingApp/Services/TransactionService.cs | 48 | UPDATE statement built with string interpolation causing SQL injection | Use parameterized query |
| SampleBankingApp/Services/TransactionService.cs | 89 | INSERT statement built with string interpolation causing SQL injection | Use parameterized query |
| SampleBankingApp/Services/TransactionService.cs | 71 | UPDATE statement built with string interpolation causing SQL injection | Use parameterized query |
| SampleBankingApp/Services/UserService.cs | 47 | UPDATE statement built with string interpolation causing SQL injection | Use parameterized query |
| SampleBankingApp/Services/UserService.cs | 61 | DELETE statement built with string interpolation causing SQL injection | Use parameterized query |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers uses ExecuteQuery with interpolated LIKE clause causing SQL injection | Use parameterized query |
| SampleBankingApp/Controllers/UserController.cs | 22 | GetUser returns any user by id without ownership check | Restrict to current user or require admin role |
| SampleBankingApp/Controllers/UserController.cs | 39 | UpdateUser allows updating any user id without authorization check | Verify caller owns resource or has admin role |
| SampleBankingApp/Controllers/UserController.cs | 57 | DeleteUser allows deleting any user id without authorization check | Verify caller owns resource or has admin role |
| SampleBankingApp/appsettings.json | 3 | Production connection string contains SA password Admin1234! committed to source | Move secrets to secure vault and environment variables |
| SampleBankingApp/appsettings.json | 14 | Email password EmailPass99 committed to source | Move secrets out of source control |
| SampleBankingApp/Services/EmailService.cs | 16 | SmtpClient stored as long lived instance field is not thread safe | Create and dispose per operation |
| SampleBankingApp/appsettings.json | 6 | JWT secret is weak and short | Use strong random secret |

## 2. Logic Errors
| File | Line | Issue | Fix |
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check uses amount only but deducts amount plus fee allowing negative balance | Check balance >= totalDebit |
| SampleBankingApp/Services/TransactionService.cs | 25 | Transfer allows zero amount which may be nonsensical | Reject amount <=0 |
| SampleBankingApp/Services/TransactionService.cs | 23 | Transfer does not prevent self transfer | Add check fromUserId != toUserId |
| SampleBankingApp/Services/UserService.cs | 72 | Pagination skip calculated as page * pageSize causing off by one error | Use (page-1) * pageSize |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit interest bonus uses 5% rate which may be incorrect | Verify intended rate and use named constant |

## 3. Error Handling
| File | Line | Issue | Fix |
| SampleBankingApp/Controllers/UserController.cs | 52 | Catch block returns raw exception message to client | Return generic error and log details |
| SampleBankingApp/Controllers/UserController.cs | 48 | ArgumentException message returned directly to client | Map to generic validation error |
| SampleBankingApp/Services/UserService.cs | 105 | Catch block swallows exception and returns empty list hiding errors | Log error and propagate or return error indicator |
| SampleBankingApp/Services/EmailService.cs | 77 | Exception caught and only logged to console swallowing failure | Log properly and consider retry or notification |
| SampleBankingApp/Services/TransactionService.cs | 52 | Email sent after database updates without transaction allowing partial success | Wrap DB operations in transaction and send email after commit |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | int.Parse on userIdClaim without try catch may throw FormatException | Use int.TryParse with null check |
| SampleBankingApp/Services/AuthService.cs | 103 | ValidateToken returns true unconditionally making validation ineffective | Remove early return and implement proper validation |

## 4. Resource Leaks
| File | Line | Issue | Fix |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | GetOpenConnection returns open SqlConnection without disposal contract | Return using or manage lifetime internally |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | ExecuteQuery opens connection via GetOpenConnection and never closes it | Use using for connection and command |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | ExecuteNonQuery opens connection and closes but does not dispose command | Use using for command and connection |
| SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection opened but never disposed leading to leak | Wrap connection and command in using |
| SampleBankingApp/Services/AuthService.cs | 38 | SqlDataReader created but never closed or disposed | Use using for reader |
| SampleBankingApp/Services/EmailService.cs | 16 | SmtpClient stored as long lived instance field may leak sockets | Create per operation and dispose |
| SampleBankingApp/Services/EmailService.cs | 39 | MailMessage created but never disposed | Wrap MailMessage in using |
| SampleBankingApp/Services/EmailService.cs | 69 | MailMessage created but never disposed | Wrap MailMessage in using |
| SampleBankingApp/Services/EmailService.cs | 89 | MailMessage created but never disposed | Wrap MailMessage in using |

## 5. Null Reference Risks
| File | Line | Issue | Fix |
| SampleBankingApp/Program.cs | 28 | Encoding.UTF8.GetBytes called on jwtSecret that may be null | Validate config value before use |
| SampleBankingApp/Program.cs | 26 | ValidIssuer read from config without null check | Provide default or validate |
| SampleBankingApp/Services/AuthService.cs | 70 | Encoding.UTF8.GetBytes called on config value that may be null | Validate config |
| SampleBankingApp/Services/TransactionService.cs | 36 | Accesses Rows[0] without checking Rows.Count | Check count before access |
| SampleBankingApp/Services/TransactionService.cs | 37 | Accesses Rows[0] without checking Rows.Count | Check count before access |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | int.Parse called on userIdClaim that may be null | Use TryParse with null check |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | int.Parse called on userIdClaim that may be null | Use TryParse with null check |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | email.Length accessed without null check | Add null guard |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | username.Length accessed without null check | Add null guard |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | accountNumber.Length accessed without null check | Add null guard |
| SampleBankingApp/Services/EmailService.cs | 22 | SmtpClient constructed with config value that may be null | Validate config |

## 6. Dead Code
| File | Line | Issue | Fix |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator method has no callers | Remove or use |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | JoinWithSeparatorFixed method has no callers | Remove or use |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount method has no callers | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase method has no callers | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method has no callers | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | IsValidEmail method has no callers | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 20 | IsValidUsername method has no callers | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 43 | MaskAccountNumber method has no callers | Remove |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 method is unused | Remove |
| SampleBankingApp/Services/AuthService.cs | 98 | ValidateToken method is unused and contains unreachable code | Remove or implement |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit method is unused | Remove or integrate |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency method is unused | Remove |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml method has no callers | Remove or use |
| SampleBankingApp/Data/DatabaseHelper.cs | 59 | TableExists method has no callers | Remove |
| SampleBankingApp/Data/DatabaseHelper.cs | 68 | ExecuteQueryWithParams is obsolete and unused | Remove |
| SampleBankingApp/Services/AuthService.cs | 105 | Code after unconditional return is unreachable | Remove unreachable code |

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
| SampleBankingApp/Services/TransactionService.cs | 68 | Interest rate 0.05m is hardcoded magic number | Define named constant |
| SampleBankingApp/Services/TransactionService.cs | 90 | Status string Completed is hardcoded | Use constant |
| SampleBankingApp/Services/UserService.cs | 70 | Page size limit 50 is hardcoded | Define constant |
| SampleBankingApp/Services/UserService.cs | 22 | User ID max 1000000 is hardcoded | Define constant |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | Email max length 254 is hardcoded | Define constant |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | Username min length 3 and max 20 are hardcoded | Define constants |
| SampleBankingApp/Services/EmailService.cs | 40 | From address notifications@company.com is hardcoded | Move to config |
| SampleBankingApp/Services/EmailService.cs | 67 | Support email support@company.com is hardcoded | Move to config |
| SampleBankingApp/Controllers/UserController.cs | 32 | Default pageSize 20 is hardcoded | Define constant |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit max amount 1000000 is hardcoded | Define constant |

## 8. Anti-patterns and Code Quality
| File | Line | Issue | Fix |
| SampleBankingApp/Helpers/StringHelper.cs | 31 | JoinWithSeparator uses string concatenation in loop causing O(n²) performance | Use StringBuilder or string.Join |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | Regex instantiated per call causing allocation overhead | Use static readonly Regex |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | Regex instantiated per call causing allocation overhead | Use static readonly Regex |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank reimplements string.IsNullOrWhiteSpace | Use built in method |
| SampleBankingApp/Services/UserService.cs | 87 | GetAuditReport builds string with concatenation in loop | Use StringBuilder or string.Join |
| SampleBankingApp/Services/UserService.cs | 10 | Static mutable _auditLog shared across requests without synchronization | Use thread safe collection or scoped service |
| SampleBankingApp/Services/UserService.cs | 11 | Static mutable _requestCount shared across requests without synchronization | Use thread safe counter or scoped service |
| SampleBankingApp/Services/UserService.cs | 20 | User ID validation duplicated across methods | Extract to shared validation method |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | GetOpenConnection leaks resource ownership to caller | Document disposal contract or manage internally |
| SampleBankingApp/Services/TransactionService.cs | 23 | Transfer method has multiple responsibilities validation DB update email | Split into smaller methods |

## 9. Configuration Issues
| File | Line | Issue | Fix |
| SampleBankingApp/Program.cs | 34 | UseDeveloperExceptionPage enabled unconditionally | Enable only in Development |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out | Enable HTTPS redirection |
| SampleBankingApp/Program.cs | 38 | CORS allows any origin method and header | Restrict to specific origins |
| SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime set to false | Enable lifetime validation |
| SampleBankingApp/appsettings.json | 18 | LogLevel Default set to Debug for production | Use Information or Warning in production |
| SampleBankingApp/appsettings.json | 3 | Connection string with password committed to source | Use environment variables |
| SampleBankingApp/SampleBankingApp.csproj | 15 | Newtonsoft.Json version 12.0.3 is outdated and vulnerable | Upgrade to latest stable |
| SampleBankingApp/SampleBankingApp.csproj | 8 | DebugSymbols true may expose symbols in release | Disable for release builds |

## 10. Missing Unit Tests
| File | Line | Issue | Fix |
| SampleBankingApp/Services/AuthService.cs | 28 | No unit tests for Login authentication logic | Add tests for valid invalid credentials and admin bypass |
| SampleBankingApp/Services/AuthService.cs | 68 | No unit tests for GenerateJwtToken | Add tests for token claims and expiry |
| SampleBankingApp/Services/TransactionService.cs | 23 | No unit tests for Transfer with fee and balance checks | Add tests for success insufficient funds and self transfer |
| SampleBankingApp/Services/TransactionService.cs | 63 | No unit tests for Deposit with interest and limits | Add tests for valid invalid amounts |
| SampleBankingApp/Services/UserService.cs | 68 | No unit tests for GetUsersPage pagination | Add tests for page boundaries and off by one |
| SampleBankingApp/Services/UserService.cs | 38 | No unit tests for UpdateUser validation | Add tests for id range and SQL injection safety |
| SampleBankingApp/Controllers/UserController.cs | 22 | No unit tests for authorization on GetUser | Add tests for access control |