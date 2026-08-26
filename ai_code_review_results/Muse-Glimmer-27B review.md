## 1. Security Vulnerabilities
| File | Line | Issue | Fix |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded fallback connection string with password Admin1234! | Remove hardcoded credentials and require configuration |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | ExecuteQuery interpolates tableName and whereClause enabling SQL injection | Use parameterized queries and whitelist identifiers |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | GetOpenConnection returns open SqlConnection without disposal contract | Document ownership or use using |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password SuperAdmin2024 creates backdoor | Remove backdoor and enforce proper authentication |
| SampleBankingApp/Services/AuthService.cs | 30 | HashPasswordMd5 uses MD5 which is cryptographically broken | Use salted strong password hashing |
| SampleBankingApp/Services/AuthService.cs | 32 | Login builds SQL with string interpolation enabling SQL injection | Use parameterized query |
| SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection opened but never closed or disposed | Use using for connection and reader |
| SampleBankingApp/Services/AuthService.cs | 53 | Admin bypass allows login with hardcoded credentials without DB check | Remove bypass logic |
| SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime set to false allowing expired tokens | Set ValidateLifetime to true |
| SampleBankingApp/Program.cs | 28 | IssuerSigningKey created from jwtSecret without null check | Validate config value and fail fast |
| SampleBankingApp/Program.cs | 34 | UseDeveloperExceptionPage called unconditionally exposing stack traces | Enable only in Development environment |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out allowing HTTP traffic | Enable HTTPS redirection |
| SampleBankingApp/Program.cs | 38 | CORS policy allows any origin method and header | Restrict origins to trusted domains |
| SampleBankingApp/appsettings.json | 3 | Connection string contains plaintext password committed to source | Store secrets in environment variables or secret manager |
| SampleBankingApp/appsettings.json | 14 | Email password EmailPass99 committed to source | Remove secret from source control |
| SampleBankingApp/appsettings.json | 6 | JWT secret mysecretkey is weak and committed to source | Use strong random secret from secure store |
| SampleBankingApp/Services/TransactionService.cs | 47 | UPDATE statement built with string interpolation enabling SQL injection | Use parameterized query |
| SampleBankingApp/Services/TransactionService.cs | 48 | UPDATE statement built with string interpolation enabling SQL injection | Use parameterized query |
| SampleBankingApp/Services/TransactionService.cs | 71 | UPDATE statement built with string interpolation enabling SQL injection | Use parameterized query |
| SampleBankingApp/Services/TransactionService.cs | 89 | RecordTransaction builds INSERT with interpolation enabling SQL injection | Use parameterized query |
| SampleBankingApp/Services/UserService.cs | 47 | UPDATE statement built with string interpolation enabling SQL injection | Use parameterized query |
| SampleBankingApp/Services/UserService.cs | 61 | DELETE statement built with string interpolation enabling SQL injection | Use parameterized query |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers uses ExecuteQuery with interpolated LIKE enabling SQL injection | Use parameterized query |
| SampleBankingApp/Controllers/UserController.cs | 24 | GetUser returns any user by id without ownership check | Verify current user can access requested id |
| SampleBankingApp/Controllers/UserController.cs | 43 | UpdateUser allows updating any user without ownership check | Restrict to own user or require admin role |
| SampleBankingApp/Controllers/UserController.cs | 57 | DeleteUser allows deleting any user without ownership check | Restrict to authorized users only |
| SampleBankingApp/Services/EmailService.cs | 22 | SmtpClient stored as instance field is not thread safe and never disposed | Create and dispose per use or manage lifecycle properly |
| SampleBankingApp/Controllers/UserController.cs | 52 | Returns raw exception message to client leaking information | Return generic error message and log details |

## 2. Logic Errors
| File | Line | Issue | Fix |
| SampleBankingApp/Services/UserService.cs | 72 | Pagination skip calculated as page * pageSize causing off-by-one | Use (page-1) * pageSize with page >=1 validation |
| SampleBankingApp/Services/TransactionService.cs | 42 | Balance check compares fromBalance >= amount but deducts amount + fee | Check fromBalance >= totalDebit |
| SampleBankingApp/Services/TransactionService.cs | 36 | Accesses fromUserTable.Rows[0] without verifying Rows.Count | Check count before access |
| SampleBankingApp/Services/TransactionService.cs | 37 | Accesses toUserTable.Rows[0] without verifying Rows.Count | Check count before access |
| SampleBankingApp/Services/TransactionService.cs | 25 | Transfer allows amount zero | Reject amount <=0 |
| SampleBankingApp/Services/TransactionService.cs | 23 | Missing self-transfer check | Reject when fromUserId == toUserId |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | int.Parse(userIdClaim!) throws if claim missing | Validate claim presence and return Unauthorized |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | int.Parse(userIdClaim!) throws if claim missing | Validate claim presence and return Unauthorized |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | IsValidEmail accesses email.Length without null check | Guard against null |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | IsValidUsername accesses username.Length without null check | Guard against null |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | MaskAccountNumber accesses accountNumber.Length without null check | Guard against null |

## 3. Error Handling
| File | Line | Issue | Fix |
| SampleBankingApp/Services/UserService.cs | 105 | Catch Exception returns empty list silently hiding errors | Log error and propagate or return error status |
| SampleBankingApp/Services/EmailService.cs | 75 | Catch Exception swallows welcome email failure silently | Log error and consider retry |
| SampleBankingApp/Controllers/UserController.cs | 52 | Returns raw ex.Message to client | Return generic message and log details |
| SampleBankingApp/Controllers/UserController.cs | 48 | Returns raw ArgumentException message | Return generic validation error |
| SampleBankingApp/Services/TransactionService.cs | 23 | Transfer performs two UPDATEs without transaction risking partial update | Wrap in database transaction |
| SampleBankingApp/Services/TransactionService.cs | 52 | Email sent after DB updates committed risking inconsistency | Send email within transaction or use outbox pattern |
| SampleBankingApp/Services/AuthService.cs | 103 | ValidateToken returns true early swallowing validation | Remove early return and implement validation |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Catches NotImplementedException and returns 500 with message | Return proper 501 Not Implemented |

## 4. Resource Leaks
| File | Line | Issue | Fix |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | GetOpenConnection returns SqlConnection without disposal | Return using or require caller dispose |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | ExecuteQuery uses GetOpenConnection without closing | Use using for connection and command |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | ExecuteNonQuery uses GetOpenConnection and closes but not dispose | Use using |
| SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection opened and never closed | Use using for connection and reader |
| SampleBankingApp/Services/AuthService.cs | 38 | SqlCommand and SqlDataReader not disposed | Use using |
| SampleBankingApp/Services/EmailService.cs | 22 | SmtpClient held as instance field never disposed | Dispose in Dispose pattern |
| SampleBankingApp/Services/EmailService.cs | 39 | MailMessage created without using | Use using for MailMessage |
| SampleBankingApp/Services/EmailService.cs | 69 | MailMessage created without using | Use using for MailMessage |

## 5. Null Reference Risks
| File | Line | Issue | Fix |
| SampleBankingApp/Program.cs | 16 | jwtSecret read from config may be null | Validate config and fail fast |
| SampleBankingApp/Program.cs | 26 | ValidIssuer may be null | Validate config |
| SampleBankingApp/Program.cs | 27 | ValidAudience may be null | Validate config |
| SampleBankingApp/Services/EmailService.cs | 22 | _config["Email:SmtpHost"] may be null | Validate config |
| SampleBankingApp/Services/EmailService.cs | 26 | _config["Email:Username"] may be null | Validate config |
| SampleBankingApp/Services/EmailService.cs | 27 | _config["Email:Password"] may be null | Validate config |
| SampleBankingApp/Services/AuthService.cs | 70 | _config["Jwt:SecretKey"]! may be null | Validate config |
| SampleBankingApp/Services/TransactionService.cs | 36 | Rows[0] access without count check | Check Rows.Count |
| SampleBankingApp/Services/TransactionService.cs | 37 | Rows[0] access without count check | Check Rows.Count |
| SampleBankingApp/Services/TransactionService.cs | 53 | Rows[0] access without count check | Check Rows.Count |
| SampleBankingApp/Services/TransactionService.cs | 55 | Rows[0] access without count check | Check Rows.Count |
| SampleBankingApp/Services/UserService.cs | 83 | Rows[0] access in IsWithinDailyLimit without count check | Check Rows.Count |
| SampleBankingApp/Helpers/StringHelper.cs | 13 | email.Length without null check | Guard null |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | username.Length without null check | Guard null |
| SampleBankingApp/Helpers/StringHelper.cs | 45 | accountNumber.Length without null check | Guard null |
| SampleBankingApp/Helpers/StringHelper.cs | 56 | account[^4..] assumes length >=4 | Guard length |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | userIdClaim! may be null | Check null before parse |
| SampleBankingApp/Controllers/TransactionController.cs | 41 | userIdClaim! may be null | Check null before parse |

## 6. Dead Code
| File | Line | Issue | Fix |
| SampleBankingApp/Data/DatabaseHelper.cs | 68 | ExecuteQueryWithParams marked Obsolete and unused | Remove or use |
| SampleBankingApp/Services/AuthService.cs | 91 | HashPasswordSha1 defined but never called | Remove |
| SampleBankingApp/Services/AuthService.cs | 98 | ValidateToken defined but never called with unreachable code | Remove or implement |
| SampleBankingApp/Services/TransactionService.cs | 77 | IsWithinDailyLimit defined but never called | Remove or use |
| SampleBankingApp/Services/TransactionService.cs | 94 | FormatCurrency defined but never called | Remove |
| SampleBankingApp/Services/EmailService.cs | 86 | SendWelcomeEmailHtml defined but never called | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator defined but never called | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | JoinWithSeparatorFixed defined but never called | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 54 | ObfuscateAccount defined but never called | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 59 | ToTitleCase defined but never called | Remove |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank defined but never called | Remove |
| SampleBankingApp/Data/DatabaseHelper.cs | 59 | TableExists defined but never called | Remove |
| SampleBankingApp/Services/AuthService.cs | 105 | Code after unconditional return is unreachable | Remove unreachable code |

## 7. Magic Strings and Numbers
| File | Line | Issue | Fix |
| SampleBankingApp/appsettings.json | 3 | Connection string password Admin1234! hardcoded | Move to secret store |
| SampleBankingApp/appsettings.json | 14 | Email password EmailPass99 hardcoded | Move to secret store |
| SampleBankingApp/appsettings.json | 6 | JWT secret mysecretkey hardcoded | Use strong secret from secure store |
| SampleBankingApp/Services/TransactionService.cs | 68 | Interest bonus uses literal 0.05m | Define constant |
| SampleBankingApp/Services/UserService.cs | 70 | Page size cap literal 50 | Define constant |
| SampleBankingApp/Services/UserService.cs | 22 | User ID upper bound literal 1000000 | Define constant |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit cap literal 1000000 | Define constant |
| SampleBankingApp/Services/EmailService.cs | 10 | TransferSubject literal | Use config |
| SampleBankingApp/Services/EmailService.cs | 11 | WelcomeSubject literal | Use config |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Fallback connection string contains password | Remove hardcoded credentials |

## 8. Anti-patterns and Code Quality
| File | Line | Issue | Fix |
| SampleBankingApp/Helpers/StringHelper.cs | 32 | result += item + separator in loop O(n²) | Use StringBuilder or string.Join |
| SampleBankingApp/Services/UserService.cs | 88 | report += entry + "\n" in loop O(n²) | Use StringBuilder |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | new Regex created each call | Make static readonly |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | new Regex created each call | Make static readonly |
| SampleBankingApp/Services/UserService.cs | 10 | static List _auditLog shared mutable without synchronization | Use thread-safe collection |
| SampleBankingApp/Services/UserService.cs | 11 | static int _requestCount shared mutable | Use thread-safe counter |
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | GetOpenConnection leaks resource ownership | Return connection via using |
| SampleBankingApp/Services/UserService.cs | 20 | Validation duplicated across methods | Extract shared validation method |
| SampleBankingApp/Services/TransactionService.cs | 23 | Transfer does validation DB reads writes email multiple responsibilities | Split into smaller methods |
| SampleBankingApp/Services/AuthService.cs | 28 | Login does hashing query mapping bypass multiple responsibilities | Split into smaller methods |

## 9. Configuration Issues
| File | Line | Issue | Fix |
| SampleBankingApp/Program.cs | 34 | UseDeveloperExceptionPage enabled unconditionally | Enable only in Development |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out | Enable HTTPS redirection |
| SampleBankingApp/Program.cs | 38 | CORS allows any origin method header | Restrict CORS to trusted origins |
| SampleBankingApp/Program.cs | 24 | ValidateLifetime false | Set ValidateLifetime to true |
| SampleBankingApp/SampleBankingApp.csproj | 8 | DebugSymbols true in release build | Disable for release |
| SampleBankingApp/SampleBankingApp.csproj | 13 | Newtonsoft.Json 12.0.3 outdated | Update to supported version |
| SampleBankingApp/appsettings.json | 18 | LogLevel Default Debug for production | Set to Warning or Error |
| SampleBankingApp/appsettings.json | 23 | AllowedHosts "*" overly permissive | Restrict hosts |

## 10. Missing Unit Tests
| File | Line | Issue | Fix |
| SampleBankingApp/Services/AuthService.cs | 28 | No unit tests for Login authentication and admin bypass | Add tests for valid/invalid credentials and bypass removal |
| SampleBankingApp/Services/TransactionService.cs | 23 | No unit tests for Transfer balance and fee calculation | Add tests for insufficient funds fee deduction self-transfer |
| SampleBankingApp/Services/UserService.cs | 68 | No unit tests for pagination off-by-one | Add tests for page 1 2 boundary |
| SampleBankingApp/Services/UserService.cs | 38 | No unit tests for UpdateUser SQL injection | Add tests with malicious input |
| SampleBankingApp/Controllers/UserController.cs | 24 | No unit tests for authorization enforcement | Add tests for unauthorized access |
| SampleBankingApp/Services/EmailService.cs | 34 | No unit tests for SendTransferNotification retry logic | Add tests for SMTP failures |
| SampleBankingApp/Helpers/StringHelper.cs | 11 | No unit tests for IsValidEmail null handling | Add tests for null and edge cases |
| SampleBankingApp/Program.cs | 24 | No unit tests for JWT validation configuration | Add integration tests for token expiry |