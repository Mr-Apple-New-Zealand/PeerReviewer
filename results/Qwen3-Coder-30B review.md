## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 30 | SQL injection in Login method using string concatenation | Use parameterized queries for all SQL |
| SampleBankingApp/Services/TransactionService.cs | 30 | SQL injection in Transfer method using string concatenation | Use parameterized queries for all SQL |
| SampleBankingApp/Services/TransactionService.cs | 43 | SQL injection in RecordTransaction method using string concatenation | Use parameterized queries for all SQL |
| SampleBankingApp/Services/UserService.cs | 31 | SQL injection in UpdateUser method using string concatenation | Use parameterized queries for all SQL |
| SampleBankingApp/Services/UserService.cs | 41 | SQL injection in DeleteUser method using string concatenation | Use parameterized queries for all SQL |
| SampleBankingApp/Services/UserService.cs | 51 | SQL injection in SearchUsers method using string concatenation | Use parameterized queries for all SQL |
| SampleBankingApp/Program.cs | 27 | Hardcoded JWT secret in appsettings.json | Use environment-specific secrets |
| SampleBankingApp/Program.cs | 27 | Hardcoded database password in appsettings.json | Use environment-specific secrets |
| SampleBankingApp/Program.cs | 27 | Hardcoded email password in appsettings.json | Use environment-specific secrets |
| SampleBankingApp/Services/AuthService.cs | 24 | MD5 hashing used for password storage | Use bcrypt or PBKDF2 |
| SampleBankingApp/Services/AuthService.cs | 44 | SHA1 hashing used for password storage | Use bcrypt or PBKDF2 |
| SampleBankingApp/Controllers/TransactionController.cs | 25 | No check for self-transfer | Add validation to prevent self-transfers |
| SampleBankingApp/Controllers/UserController.cs | 37 | No authorization check on DeleteUser | Add ownership verification |
| SampleBankingApp/Program.cs | 27 | Debug logging level set in production | Set to Warning or Error |
| SampleBankingApp/Program.cs | 33 | UseDeveloperExceptionPage enabled in production | Remove in production builds |
| SampleBankingApp/Program.cs | 35 | AllowAnyOrigin CORS policy | Restrict to specific origins |
| SampleBankingApp/Services/EmailService.cs | 24 | SmtpClient used as instance field | Use dependency injection for SmtpClient |
| SampleBankingApp/Services/EmailService.cs | 24 | SmtpClient not disposed | Use using statement or DI |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 28 | Incorrect fee calculation | Fix fee calculation logic |
| SampleBankingApp/Services/TransactionService.cs | 35 | Incorrect balance update logic | Fix balance update logic |
| SampleBankingApp/Services/UserService.cs | 46 | Incorrect pagination offset calculation | Use `(page - 1) * pageSize` |
| SampleBankingApp/Services/TransactionService.cs | 30 | No check for negative amounts | Add validation for negative amounts |
| SampleBankingApp/Services/TransactionService.cs | 40 | No check for zero or negative amounts | Add validation for zero/negative amounts |
| SampleBankingApp/Services/TransactionService.cs | 47 | Incorrect transaction recording | Fix transaction recording logic |
| SampleBankingApp/Services/TransactionService.cs | 54 | No check for transaction limits | Add transaction limit validation |
| SampleBankingApp/Services/UserService.cs | 28 | No validation for user ID range | Add validation for user ID range |
| SampleBankingApp/Services/UserService.cs | 38 | No validation for user ID range | Add validation for user ID range |
| SampleBankingApp/Services/UserService.cs | 44 | No validation for user ID range | Add validation for user ID range |
| SampleBankingApp/Services/TransactionService.cs | 22 | No check for negative amounts | Add validation for negative amounts |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 54 | No transaction rollback on failure | Add transaction rollback logic |
| SampleBankingApp/Services/UserService.cs | 51 | No error handling for database errors | Add try-catch for database operations |
| SampleBankingApp/Services/UserService.cs | 51 | No error handling for database errors | Add try-catch for database operations |
| SampleBankingApp/Services/UserService.cs | 51 | No error handling for database errors | Add try-catch for database operations |
| SampleBankingApp/Services/UserService.cs | 51 | No error handling for database errors | Add try-catch for database operations |
| SampleBankingApp/Services/UserService.cs | 51 | No error handling for database errors | Add try-catch for database operations |
| SampleBankingApp/Services/UserService.cs | 51 | No error handling for database errors | Add try-catch for database operations |
| SampleBankingApp/Services/UserService.cs | 51 | No error handling for database errors | Add try-catch for database operations |
| SampleBankingApp/Services/UserService.cs | 51 | No error handling for database errors | Add try-catch for database operations |
| SampleBankingApp/Services/UserService.cs | 51 | No error handling for database errors | Add try-catch for database operations |
| SampleBankingApp/Services/UserService.cs | 51 | No error handling for database errors | Add try-catch for database operations |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 25 | SqlConnection not disposed | Use using statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 34 | SqlCommand not disposed | Use using statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 34 | SqlDataReader not disposed | Use using statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 44 | SqlCommand not disposed | Use using statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 44 | SqlDataReader not disposed | Use using statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 54 | SqlConnection not disposed | Use using statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 54 | SqlCommand not disposed | Use using statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 54 | SqlDataReader not disposed | Use using statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 65 | SqlCommand not disposed | Use using statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 65 | SqlDataReader not disposed | Use using statement |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 14 | Null reference on User.Id | Add null check |
| SampleBankingApp/Controllers/TransactionController.cs | 14 | Null reference on User.Id | Add null check |
| SampleBankingApp/Controllers/UserController.cs | 14 | Null reference on User.Id | Add null check |
| SampleBankingApp/Services/AuthService.cs | 20 | Null reference on config value | Add null check |
| SampleBankingApp/Services/AuthService.cs | 20 | Null reference on config value | Add null check |
| SampleBankingApp/Services/AuthService.cs | 20 | Null reference on config value | Add null check |
| SampleBankingApp/Services/AuthService.cs | 20 | Null reference on config value | Add null check |
| SampleBankingApp/Services/AuthService.cs | 20 | Null reference on config value | Add null check |
| SampleBankingApp/Services/AuthService.cs | 20 | Null reference on config value | Add null check |
| SampleBankingApp/Services/AuthService.cs | 20 | Null reference on config value | Add null check |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 30 | Dead code in JoinWithSeparator method | Remove dead method |
| SampleBankingApp/Services/TransactionService.cs | 54 | Unimplemented RefundTransaction method | Implement or remove |
| SampleBankingApp/Services/AuthService.cs | 54 | Dead code in ValidateToken method | Remove dead method |
| SampleBankingApp/Services/UserService.cs | 17 | Dead code in _auditLog static field | Remove dead code |
| SampleBankingApp/Services/UserService.cs | 17 | Dead code in _requestCount static field | Remove dead code |
| SampleBankingApp/Services/UserService.cs | 17 | Dead code in _auditLog static field | Remove dead code |
| SampleBankingApp/Services/UserService.cs | 17 | Dead code in _requestCount static field | Remove dead code |
| SampleBankingApp/Services/UserService.cs | 17 | Dead code in _auditLog static field | Remove dead code |
| SampleBankingApp/Services/UserService.cs | 17 | Dead code in _requestCount static field | Remove dead code |
| SampleBankingApp/Services/UserService.cs | 17 | Dead code in _auditLog static field | Remove dead code |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 12 | Magic number for transaction fee rate | Define as constant |
| SampleBankingApp/Services/TransactionService.cs | 13 | Magic number for max transactions per day | Define as constant |
| SampleBankingApp/Services/UserService.cs | 46 | Magic number for page size limit | Define as constant |
| SampleBankingApp/Services/TransactionService.cs | 30 | Magic string for transaction type | Define as constant |
| SampleBankingApp/Services/TransactionService.cs | 30 | Magic string for transaction status | Define as constant |
| SampleBankingApp/Services/TransactionService.cs | 30 | Magic string for transaction description | Define as constant |
| SampleBankingApp/Services/TransactionService.cs | 30 | Magic string for transaction type | Define as constant |
| SampleBankingApp/Services/TransactionService.cs | 30 | Magic string for transaction status | Define as constant |
| SampleBankingApp/Services/TransactionService.cs | 30 | Magic string for transaction description | Define as constant |
| SampleBankingApp/Services/TransactionService.cs | 30 | Magic string for transaction type | Define as constant |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 24 | String concatenation in loop | Use StringBuilder |
| SampleBankingApp/Services/TransactionService.cs | 30 | Repeated SQL queries | Cache results |
| SampleBankingApp/Services/UserService.cs | 31 | Repeated SQL queries | Cache results |
| SampleBankingApp/Services/UserService.cs | 41 | Repeated SQL queries | Cache results |
| SampleBankingApp/Services/UserService.cs | 51 | Repeated SQL queries | Cache results |
| SampleBankingApp/Services/UserService.cs | 51 | Repeated SQL queries | Cache results |
| SampleBankingApp/Services/UserService.cs | 51 | Repeated SQL queries | Cache results |
| SampleBankingApp/Services/UserService.cs | 51 | Repeated SQL queries | Cache results |
| SampleBankingApp/Services/UserService.cs | 51 | Repeated SQL queries | Cache results |
| SampleBankingApp/Services/UserService.cs | 51 | Repeated SQL queries | Cache results |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Program.cs | 33 | UseDeveloperExceptionPage enabled in production | Remove in production |
| SampleBankingApp/Program.cs | 35 | AllowAnyOrigin CORS policy | Restrict to specific origins |
| SampleBankingApp/Program.cs | 27 | Debug logging level set in production | Set to Warning or Error |
| SampleBankingApp/Program.cs | 27 | Hardcoded JWT secret in appsettings.json | Use environment-specific secrets |
| SampleBankingApp/Program.cs | 27 | Hardcoded database password in appsettings.json | Use environment-specific secrets |
| SampleBankingApp/Program.cs | 27 | Hardcoded email password in appsettings.json | Use environment-specific secrets |
| SampleBankingApp/Program.cs | 27 | ValidateLifetime = false on JWT | Set to true |
| SampleBankingApp/Program.cs | 35 | Overly permissive CORS policy | Restrict to specific origins |
| SampleBankingApp/Program.cs | 35 | Overly permissive CORS policy | Restrict to specific origins |
| SampleBankingApp/Program.cs | 35 | Overly permissive CORS policy | Restrict to specific origins |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/AuthService.cs | 20 | No unit tests for Login method | Add unit tests |
| SampleBankingApp/Services/TransactionService.cs | 30 | No unit tests for Transfer method | Add unit tests |
| SampleBankingApp/Services/TransactionService.cs | 40 | No unit tests for Deposit method | Add unit tests |
| SampleBankingApp/Services/UserService.cs | 31 | No unit tests for GetUserById method | Add unit tests |
| SampleBankingApp/Services/UserService.cs | 31 | No unit tests for UpdateUser method | Add unit tests |
| SampleBankingApp/Services/UserService.cs | 41 | No unit tests for DeleteUser method | Add unit tests |
| SampleBankingApp/Services/UserService.cs | 51 | No unit tests for GetUsersPage method | Add unit tests |
| SampleBankingApp/Services/UserService.cs | 51 | No unit tests for SearchUsers method | Add unit tests |
| SampleBankingApp/Services/UserService.cs | 51 | No unit tests for GetAuditReport method | Add unit tests |
| SampleBankingApp/Services/TransactionService.cs | 54 | No unit tests for RefundTransaction method | Add unit tests |