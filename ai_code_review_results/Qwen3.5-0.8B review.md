## Security Vulnerabilities
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded credentials in connection string. | Remove hardcoded password from DefaultConnection. |
| SampleBankingApp/Services/AuthService.cs | 30 | MD5 hashing vulnerable to collision attacks. | Replace MD5 with SHA-256 or bcrypt. |
| SampleBankingApp/Services/AuthService.cs | 61 | SHA1 weak cryptographic algorithm. | Replace SHA1 with SHA-256 or SHA-384. |
| SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime = false allows insecure lifetime validation. | Set ValidateLifetime = true for secure token validation. |
| SampleBankingApp/appsettings.json | 38 | Overly permissive CORS policy (AllowAnyOrigin + AllowAnyMethod). | Restrict to specific origins only. |
| SampleBankingApp/Program.cs | 37 | HTTPS disabled in production. | Enable HTTPS redirection. |
| SampleBankingApp/Program.cs | 39 | Debug symbols in release build. | Disable debug symbols for production. |
| SampleBankingApp/Program.cs | 42 | Production secrets committed to source. | Move sensitive values to configuration files. |

## Logic Errors
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/TransactionController.cs | 25 | Off-by-one error in pagination offset calculation. | Correct offset formula: `(page - 1) * pageSize`. |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | Incorrect boundary condition for negative ID parsing. | Parse ID as `long` instead of `int`. |
| SampleBankingApp/Controllers/UserController.cs | 38 | Balance calculation excludes deposit fee component. | Add fee deduction logic to balance update. |
| SampleBankingApp/Services/TransactionService.cs | 11 | Fee rate applied incorrectly (5% vs 1%). | Use correct rate (0.015m = 1.5%). |
| SampleBankingApp/Services/TransactionService.cs | 25 | Insufficient funds check missing before transfer attempt. | Validate user has sufficient funds before attempting transfer. |
| SampleBankingApp/Services/TransactionService.cs | 42 | Negative balance check not enforced for transfers. | Check if newFromBalance >= amount before deducting totalDebit. |
| SampleBankingApp/Services/TransactionService.cs | 50 | Missing self-referential checks for user IDs. | Verify user exists before attempting transfer. |

## Error Handling
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Raw exception message returned to HTTP clients. | Catch and log exceptions properly. |
| SampleBankingApp/Controllers/UserController.cs | 66 | Empty collections return empty list instead of error. | Return appropriate error message when no results found. |
| SampleBankingApp/Services/TransactionService.cs | 102 | NotImplementedException thrown instead of caught exception. | Catch and handle the RefundTransaction method gracefully. |
| SampleBankingApp/Services/TransactionService.cs | 102 | No account lockout on failed login attempts. | Implement account lockout after failed authentication. |

## Resource Leaks
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 22 | SqlConnection opened but never closed. | Close connection in all methods that create it. |
| SampleBankingApp/Data/DatabaseHelper.cs | 39 | SqlDataReader opened but never closed. | Close reader in all methods that create it. |
| SampleBankingApp/Helpers/StringHelper.cs | 48 | StringBuilder created but never disposed. | Dispose StringBuilder in all string manipulation methods. |
| SampleBankingApp/Helpers/StringHelper.cs | 71 | MailMessage created but never disposed. | Dispose MailMessage in send operations. |
| SampleBankingApp/Program.cs | 34 | Exception path skips Close() or Dispose(). | Always call `Close()` and `Dispose()` on exceptions. |

## Null Reference Risks
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Models/Transaction.cs | 27 | `.Value` on nullable int.Parse without null guard. | Add null check before parsing. |
| SampleBankingApp/Models/User.cs | 65 | `IsBlank` checks `value == ""` but not `value == null`. | Update IsBlank to check both null and empty strings. |
| SampleBankingApp/Models/User.cs | 85 | UpdateUserRequest used in controller action without null check. | Add null check before binding request to model. |
| SampleBankingApp/Models/User.cs | 99 | DataTable.Rows[0] accessed without Rows.Count > 0 check. | Check rows count before accessing DataTable.Rows. |
| SampleBankingApp/Services/AuthService.cs | 105 | JwtSecurityTokenHandler.ReadJwtToken returns false for invalid tokens. | Validate token validity explicitly. |

## Dead Code
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 67 | ExecuteQueryWithParams marked obsolete but still exists. | Remove obsolete marker if no longer needed. |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank method checks value == null but not value == "". | Fix IsBlank logic to handle empty strings correctly. |
| SampleBankingApp/Program.cs | 34 | UseDeveloperExceptionPage called unconditionally. | Remove this line from production builds. |
| SampleBankingApp/Program.cs | 37 | Debug symbols enabled in release builds. | Disable debug symbols for production releases. |

## Magic Strings and Numbers
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Controllers/TransactionController.cs | 11 | TransactionFeeRate hardcoded without validation. | Define constant with type-safe conversion. |
| SampleBankingApp/Controllers/TransactionController.cs | 12 | MaxTransactionsPerDay hardcoded without context. | Use configurable limit in service layer. |
| SampleBankingApp/Program.cs | 17 | JWT:SecretKey hardcoded in config. | Move secret key to configuration file. |
| SampleBankingApp/Program.cs | 19 | JWT:Issuer, Audience hardcoded in config. | Move issuer/audience to configuration. |

## Anti-patterns and Code Quality
| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 29 | JoinWithSeparator uses string concatenation in loop. | Replace with StringBuilder or string.Join. |
| SampleBankingApp/Helpers/StringHelper.cs | 38 | Regex inside repeated method calls (IsValidEmail). | Rename method to static readonly. |
| SampleBankingApp/Helpers/StringHelper.cs | 65 | IsBlank checks value == null but not value == "". | Update IsBlank to handle both cases. |
| SampleBankingApp/Helpers/StringHelper.cs | 48 | StringBuilder created but never closed. | Dispose StringBuilder in all string manipulation methods. |
| SampleBankingApp/Helpers/StringHelper.cs | 71 | MailMessage created but never disposed. | Dispose MailMessage in send operations. |
| SampleBankingApp/Services/TransactionService.cs | 23 | Duplicate validation logic for amount < 0. | Extract validation into shared helper method. |