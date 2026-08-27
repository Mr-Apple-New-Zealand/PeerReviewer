## Security Vulnerabilities
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | SQL injection vulnerability in ExecuteQuery method using string interpolation | Replace with parameterized queries using ExecuteQuerySafe |
| SampleBankingApp/Data/DatabaseHelper.cs | 15 | Hardcoded default connection string with password "Admin1234!" | Remove hardcoded credentials and use configuration only |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL injection vulnerability in Login method using string interpolation | Replace with parameterized query |
| SampleBankingApp/Services/AuthService.cs | 61 | Weak MD5 hashing used for password storage | Use stronger algorithm like bcrypt or Argon2 |
| SampleBankingApp/Services/AuthService.cs | 17 | Hardcoded admin bypass password "SuperAdmin2024" | Remove hardcoded credentials and use secure authentication flow |
| SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime set to false allowing infinite token validity | Set ValidateLifetime = true for proper token expiration |
| SampleBankingApp/appsettings.json | 6 | Weak JWT secret key "mysecretkey" | Use strong random key with at least 256 bits of entropy |

## Logic Errors
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/UserService.cs | 72 | Pagination off-by-one error using page * pageSize instead of (page-1) * pageSize | Change skip calculation to (page-1) * pageSize |
| SampleBankingApp/Services/TransactionService.cs | 42 | Insufficient funds check missing transaction fee in Transfer method | Update condition to fromBalance >= totalDebit (amount + fee) |

## Error Handling
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/UserController.cs | 48 | Exposing raw exception messages to clients | Return generic error message instead of ex.Message |
| SampleBankingApp/Controllers/UserController.cs | 52 | Exposing raw exception messages to clients | Return generic error message instead of ex.Message |
| SampleBankingApp/Services/TransactionService.cs | 47-49 | No transaction for multiple database updates in Transfer method | Wrap both UPDATE statements in a transaction |
| SampleBankingApp/Services/UserService.cs | 98-102 | Swallowing exceptions in SearchUsers returns empty list | Propagate exceptions or return appropriate error response |

## Resource Leaks
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | SqlConnection not properly disposed in GetOpenConnection | Use using statement or ensure proper disposal |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | Connection opened but not guaranteed to be closed | Ensure connection is properly disposed even on exceptions |
| SampleBankingApp/Services/AuthService.cs | 34 | SqlConnection not properly disposed in Login method | Use using statement for connection and reader |
| SampleBankingApp/Services/AuthService.cs | 38 | SqlDataReader not properly disposed in Login method | Use using statement for connection and reader |

## Null Reference Risks
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/TransactionController.cs | 27 | No null check before int.Parse on userIdClaim | Add null check before parsing |
| SampleBankingApp/Controllers/TransactionController.cs | 40 | No null check before int.Parse on userIdClaim | Add null check before parsing |
| SampleBankingApp/Data/DatabaseHelper.cs | 36 | No null check before accessing DataTable.Rows[0] | Add Rows.Count > 0 check before accessing index 0 |

## Dead Code
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 29-36 | JoinWithSeparator not used anywhere in codebase | Remove unused method |
| SampleBankingApp/Data/DatabaseHelper.cs | 67-78 | Obsolete ExecuteQueryWithParams still present | Remove obsolete method |
| SampleBankingApp/Services/UserService.cs | 10 | Static _requestCount field never used | Remove unused field |
| SampleBankingApp/Services/TransactionService.cs | 102-103 | NotImplementedException in RefundTransaction | Implement functionality or remove placeholder |

## Magic Strings and Numbers
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 11 | Hardcoded transaction fee rate 0.015m | Move to configuration or named constant |
| SampleBankingApp/Services/TransactionService.cs | 12 | Hardcoded max transactions per day 10 | Move to configuration or named constant |
| SampleBankingApp/Services/TransactionService.cs | 68 | Hardcoded interest bonus rate 0.05m * 1 | Move to configuration or named constant |
| SampleBankingApp/Models/User.cs | 9 | Hardcoded "User" role in model | Use configuration or enum for role names |

## Anti-patterns and Code Quality
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 29-36 | String concatenation in loop (O(n²)) | Replace with string.Join |
| SampleBankingApp/Services/EmailService.cs | 16 | SmtpClient as instance field (not thread-safe) | Create per-use instance or use dependency injection |
| SampleBankingApp/Services/TransactionService.cs | 47-49 | String interpolation for SQL in ExecuteNonQuery | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 88-92 | String concatenation for audit report | Use StringBuilder for better performance |
| SampleBankingApp/Services/AuthService.cs | 16 | Reimplementing string.IsNullOrWhiteSpace | Replace with String.IsNullOrWhiteSpace |

## Configuration Issues
| File | Line | Line | Issue | Fix |
|---|---|---|---|---|
| SampleBankingApp/Program.cs | 34 | UseDeveloperExceptionPage called unconditionally | Wrap in #if DEBUG or environment check |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection commented out | Uncomment and enable HTTPS |
| SampleBankingApp/Program.cs | 38 | Overly permissive CORS policy | Restrict origins, methods, and headers |
| SampleBankingApp/appsettings.json | N/A | Missing environment-specific config overrides | Add appsettings.Production.json |
| SampleBankingApp/SampleBankingApp.csproj | N/A | Outdated NuGet packages | Update System.Data.SqlClient to latest version |

## Missing Unit Tests
| File | Line | Issue | Fix |
|---|---|---|---|
| N/A | N/A | No test project exists | Create xUnit/NUnit test project for: |
| N/A | N/A | | - AuthController Login boundary conditions (valid/invalid users) |
| N/A | N/A | | - TransactionService Transfer with insufficient funds |
| N/A | N/A | | - TransactionService Deposit with max amount |
| N/A | N/A | | - UserService pagination edge cases (page=0, large page sizes) |
| N/A | N/A | | - AuthService JWT token validation scenarios |