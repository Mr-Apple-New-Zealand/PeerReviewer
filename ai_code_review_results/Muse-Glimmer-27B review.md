## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
| DatabaseHelper.cs | 16 | Hardcoded fallback connection string contains password Admin1234! | Remove hardcoded credentials and require config |
| DatabaseHelper.cs | 29 | ExecuteQuery builds SQL with string interpolation for tableName and whereClause | Use parameterized queries |
| DatabaseHelper.cs | 53 | ExecuteNonQuery executes raw sql string without parameters | Use parameterized commands |
| AuthService.cs | 17 | AdminBypassPassword constant contains hardcoded backdoor password | Remove backdoor or secure via config |
| AuthService.cs | 30 | HashPasswordMd5 uses MD5 for password hashing | Use salted strong hash like PBKDF2 |
| AuthService.cs | 32 | Login builds SQL with interpolated username and hashed password | Use parameterized query |
| Program.cs | 24 | TokenValidationParameters ValidateLifetime set to false | Enable lifetime validation |
| Program.cs | 34 | UseDeveloperExceptionPage called unconditionally | Restrict to development environment |
| Program.cs | 36 | HTTPS redirection is commented out | Enable HTTPS redirection |
| Program.cs | 38 | CORS policy allows any origin method and header | Restrict CORS to trusted origins |
| appsettings.json | 3 | Connection string contains plaintext password Admin1234! | Move secret to secure store |
| appsettings.json | 6 | Jwt SecretKey is weak value mysecretkey | Use strong random secret |
| appsettings.json | 14 | Email password EmailPass99 committed to source | Remove secret from source |
| TransactionService.cs | 47 | UPDATE Users statement uses string interpolation for balance and id | Use parameterized query |
| TransactionService.cs | 48 | UPDATE Users statement uses string interpolation for balance and id | Use parameterized query |
| TransactionService.cs | 71 | UPDATE Users statement uses string interpolation for amount and id | Use parameterized query |
| TransactionService.cs | 90 | INSERT INTO Transactions uses string interpolation for values | Use parameterized query |
| UserService.cs | 47 | UPDATE Users statement uses string interpolation for email username and id | Use parameterized query |
| UserService.cs | 61 | DELETE FROM Users statement uses string interpolation for id | Use parameterized query |
| UserService.cs | 99 | SearchUsers calls ExecuteQuery with LIKE interpolation | Use parameterized query |
| UserController.cs | 39 | UpdateUser allows any authenticated user to update any user id | Check ownership or admin role |
| UserController.cs | 57 | DeleteUser allows any authenticated user to delete any user id | Check ownership or admin role |
| UserController.cs | 22 | GetUser returns any user by id without ownership check | Restrict access to owner or admin |
| Program.cs | 28 | IssuerSigningKey built from jwtSecret! without null check | Validate config presence |
| AuthService.cs | 70 | GenerateJwtToken reads Jwt:SecretKey with null-forgiving operator | Validate config and fail fast |

## 2. Logic Errors
| File | Line | Issue | Fix |
| UserService.cs | 72 | Skip calculated as page * pageSize causing off-by-one pagination | Use (page-1) * pageSize |
| TransactionService.cs | 42 | Balance check uses amount only but total debit includes fee | Check balance >= amount + fee |
| TransactionService.cs | 23 | Transfer does not prevent transfer to same user id | Add self-transfer guard |
| TransactionService.cs | 68 | Interest bonus uses magic multiplier 1 and rate 0.05m | Define named constants for rate |
| TransactionService.cs | 42 | New from balance can become negative if fee exceeds available amount | Ensure total debit check prevents negative |
| UserService.cs | 20 | GetUserById throws for id <=0 but boundary may be off | Clarify valid id range |
| AuthService.cs | 103 | ValidateToken returns true unconditionally making later code unreachable | Remove early return and implement validation |
| TransactionService.cs | 36 | Rows[0] accessed without checking Rows.Count | Check count before access |

## 3. Error Handling
| File | Line | Issue | Fix |
| UserService.cs | 105 | SearchUsers catches generic Exception and returns empty list | Log error and propagate or return error |
| EmailService.cs | 75 | SendWelcomeEmail catches Exception and only writes to console | Log properly and handle failure |
| UserController.cs | 50 | UpdateUser catches Exception and returns ex.Message to client | Return generic error and log details |
| UserController.cs | 52 | UpdateUser returns raw exception message in 500 response | Avoid leaking internal details |
| TransactionService.cs | 47 | Transfer performs two updates without transaction | Wrap updates in database transaction |
| TransactionService.cs | 52 | Email sent after DB updates without rollback on failure | Send email after commit or use outbox pattern |
| AuthService.cs | 34 | SqlConnection opened without using or try finally | Ensure disposal on exception |
| DatabaseHelper.cs | 29 | ExecuteQuery opens connection without try finally | Ensure connection closed on error |
| DatabaseHelper.cs | 53 | ExecuteNonQuery closes connection but not disposed on exception | Use using for connection and command |

## 4. Resource Leaks
| File | Line | Issue | Fix |
| DatabaseHelper.cs | 19 | GetOpenConnection returns SqlConnection without disposing contract | Return using or require caller to dispose |
| DatabaseHelper.cs | 29 | ExecuteQuery uses GetOpenConnection and never closes connection | Close and dispose connection |
| DatabaseHelper.cs | 53 | ExecuteNonQuery uses GetOpenConnection and closes but does not dispose | Use using for connection and command |
| AuthService.cs | 34 | SqlConnection created and opened without using | Wrap in using |
| AuthService.cs | 37 | SqlCommand and SqlDataReader created without disposal | Wrap in using |
| EmailService.cs | 22 | SmtpClient stored as instance field and never disposed | Dispose client or use per operation |
| EmailService.cs | 39 | MailMessage created without disposal | Wrap MailMessage in using |
| EmailService.cs | 69 | MailMessage created without disposal | Wrap MailMessage in using |
| EmailService.cs | 89 | MailMessage created without disposal | Wrap MailMessage in using |

## 5. Null Reference Risks
| File | Line | Issue | Fix |
| Program.cs | 28 | Encoding.UTF8.GetBytes(jwtSecret!) may receive null | Validate jwtSecret before use |
| AuthService.cs | 70 | _config["Jwt:SecretKey"]! passed to Encoding.UTF8.GetBytes without null check | Validate config value |
| TransactionController.cs | 27 | int.Parse(userIdClaim!) assumes claim present | Check claim existence before parsing |
| TransactionController.cs | 41 | int.Parse(userIdClaim!) assumes claim present | Check claim existence before parsing |
| StringHelper.cs | 13 | IsValidEmail accesses email.Length without null check | Check for null before length |
| StringHelper.cs | 22 | IsValidUsername accesses username.Length without null check | Check for null before length |
| StringHelper.cs | 45 | MaskAccountNumber accesses accountNumber.Length without null check | Check for null before length |
| EmailService.cs | 22 | _config["Email:SmtpHost"] may be null | Validate config values |
| EmailService.cs | 24 | int.Parse on _config["Email:SmtpPort"] may be null | Validate and parse safely |
| TransactionService.cs | 36 | fromUserTable.Rows[0] accessed without checking Rows.Count | Check count before access |
| TransactionService.cs | 37 | toUserTable.Rows[0] accessed without checking Rows.Count | Check count before access |
| UserService.cs | 99 | SearchUsers query parameter may be null causing LIKE interpolation | Validate query before use |

## 6. Dead Code
| File | Line | Issue | Fix |
| AuthService.cs | 91 | HashPasswordSha1 method defined but never called | Remove unused method |
| AuthService.cs | 98 | ValidateToken returns true early making lines 105-108 unreachable | Remove unreachable code |
| DatabaseHelper.cs | 67 | ExecuteQueryWithParams marked Obsolete and unused | Remove obsolete method |
| DatabaseHelper.cs | 59 | TableExists method defined but never called | Remove or use |
| StringHelper.cs | 29 | JoinWithSeparator uses manual concatenation and appears unused | Remove or replace with JoinWithSeparatorFixed |
| StringHelper.cs | 38 | JoinWithSeparatorFixed uses string.Join and appears unused | Remove if unused |
| StringHelper.cs | 54 | ObfuscateAccount method appears unused | Remove if unused |
| StringHelper.cs | 43 | MaskAccountNumber method appears unused | Remove if unused |
| StringHelper.cs | 59 | ToTitleCase method appears unused | Remove if unused |
| StringHelper.cs | 65 | IsBlank method appears unused | Remove if unused |
| TransactionService.cs | 77 | IsWithinDailyLimit method defined but never called | Remove or integrate |
| TransactionService.cs | 94 | FormatCurrency method defined but never called | Remove if unused |
| EmailService.cs | 86 | SendWelcomeEmailHtml method appears unused | Remove if unused |

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
| TransactionService.cs | 68 | Interest bonus uses literal 0.05m and multiplier 1 | Define named constants |
| TransactionService.cs | 65 | Deposit amount cap 1000000 is literal | Define constant |
| UserService.cs | 70 | Page size cap 50 is literal | Define constant |
| UserService.cs | 20 | Id lower bound 0 is literal | Define constant |
| UserService.cs | 22 | Id upper bound 1000000 is literal | Define constant |
| StringHelper.cs | 13 | Email max length 254 is literal | Define constant |
| StringHelper.cs | 22 | Username min length 3 and max 20 are literals | Define constants |
| EmailService.cs | 10 | TransferSubject string literal repeated | Centralize constant |
| EmailService.cs | 11 | WelcomeSubject string literal repeated | Centralize constant |
| EmailService.cs | 13 | MaxRetries literal 3 | Define constant |
| EmailService.cs | 14 | SmtpTimeoutMs literal 5000 | Define constant |
| appsettings.json | 11 | SmtpHost value smtp.company.com hardcoded in config | Move to environment specific config |

## 8. Anti-patterns and Code Quality
| File | Line | Issue | Fix |
| StringHelper.cs | 31 | JoinWithSeparator uses string concatenation in loop causing O(n²) | Use StringBuilder or string.Join |
| StringHelper.cs | 16 | IsValidEmail creates new Regex each call | Use static readonly Regex |
| StringHelper.cs | 25 | IsValidUsername creates new Regex each call | Use static readonly Regex |
| UserService.cs | 10 | _auditLog static List shared without synchronization | Use thread-safe collection or scoped service |
| UserService.cs | 11 | _requestCount static int shared without synchronization | Use thread-safe counter |
| DatabaseHelper.cs | 19 | GetOpenConnection leaks resource ownership to caller | Document ownership or return using |
| UserService.cs | 20 | GetUserById repeats id validation logic | Extract shared validation method |
| UserService.cs | 40 | UpdateUser repeats id validation logic | Extract shared validation method |
| UserService.cs | 54 | DeleteUser repeats id validation logic | Extract shared validation method |
| TransactionService.cs | 23 | Transfer method mixes validation DB access balance calc updates and email | Split into smaller helpers |
| AuthService.cs | 28 | Login method mixes hashing query mapping and backdoor | Split responsibilities |

## 9. Configuration Issues
| File | Line | Issue | Fix |
| Program.cs | 34 | UseDeveloperExceptionPage enabled unconditionally | Enable only in Development |
| Program.cs | 24 | ValidateLifetime false disables token expiry check | Set ValidateLifetime true |
| Program.cs | 36 | HTTPS redirection commented out | Enable HTTPS redirection |
| Program.cs | 38 | CORS allows any origin method and header | Restrict to specific origins |
| appsettings.json | 3 | Connection string with password committed | Remove secret from source control |
| appsettings.json | 6 | Jwt SecretKey weak and committed | Use strong secret from environment |
| appsettings.json | 14 | Email password committed | Remove secret from source control |
| SampleBankingApp.csproj | 8 | DebugSymbols true in release build | Disable for production |
| SampleBankingApp.csproj | 9 | DebugType full in release build | Use portable symbols for production |
| SampleBankingApp.csproj | 15 | Newtonsoft.Json version 12.0.3 is outdated | Update to supported version |
| Program.cs | 16 | Jwt secret read without validation | Validate presence at startup |

## 10. Missing Unit Tests
| File | Line | Issue | Fix |
| AuthService.cs | 28 | Login method lacks unit tests for success failure and backdoor | Add unit tests covering auth flows |
| AuthService.cs | 68 | GenerateJwtToken lacks tests for claims and expiry | Add unit tests for token generation |
| TransactionService.cs | 23 | Transfer method lacks tests for fee calculation and insufficient funds | Add tests for boundary conditions |
| TransactionService.cs | 63 | Deposit method lacks tests for cap and interest calculation | Add tests for valid and invalid amounts |
| UserService.cs | 68 | GetUsersPage pagination off-by-one needs tests | Add tests for page boundaries |
| UserService.cs | 38 | UpdateUser validation and SQL injection risk needs tests | Add tests for input validation |
| UserService.cs | 95 | SearchUsers swallows exceptions needs tests | Add tests for error handling |
| TransactionController.cs | 24 | Transfer endpoint parses claim without null check needs tests | Add tests for missing claim |
| EmailService.cs | 34 | SendTransferNotification retries logic needs tests | Add tests for retry behavior |
| Program.cs | 17 | JWT configuration validation missing tests | Add integration tests for startup config |