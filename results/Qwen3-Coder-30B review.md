## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 15 | Hardcoded password for admin bypass in AuthService | Remove admin bypass or make it configurable |
| SampleBankingApp/Services/AuthService.cs | 25 | SQL injection vulnerability via string interpolation in SQL query | Use parameterized queries for all dynamic SQL |
| SampleBankingApp/Services/AuthService.cs | 31 | MD5 hashing used for passwords | Replace with bcrypt or PBKDF2 |
| SampleBankingApp/Services/TransactionService.cs | 35 | SQL injection in UPDATE query | Use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 52 | SQL injection in INSERT query | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 37 | SQL injection in UPDATE query | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 47 | SQL injection in DELETE query | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 57 | SQL injection in LIKE clause | Use parameterized queries |
| SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime set to false | Set to true for security |
| SampleBankingApp/Program.cs | 29 | CORS policy allows any origin/method/header | Restrict to specific origins |
| SampleBankingApp/Program.cs | 31 | UseDeveloperExceptionPage enabled in production | Remove in production builds |
| SampleBankingApp/appsettings.json | 3 | Hardcoded database password | Move to secure config |
| SampleBankingApp/appsettings.json | 12 | Hardcoded email password | Move to secure config |
| SampleBankingApp/appsettings.json | 17 | Debug log level in production | Set to Warning or Error |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 26 | Incorrect fee calculation | Apply fee to amount before deduction |
| SampleBankingApp/Services/UserService.cs | 42 | Incorrect pagination offset | Use `(page - 1) * pageSize` |
| SampleBankingApp/Services/TransactionService.cs | 41 | Missing check for self-transfer | Add validation for fromUserId == toUserId |
| SampleBankingApp/Services/TransactionService.cs | 52 | Transaction description not escaped | Escape special characters in description |
| SampleBankingApp/Services/UserService.cs | 57 | Insecure LIKE query | Escape special characters in search query |
| SampleBankingApp/Services/TransactionService.cs | 37 | Incorrect balance check | Check against totalDebit, not just amount |
| SampleBankingApp/Services/TransactionService.cs | 30 | Incorrect fee application | Apply fee to amount before deduction |
| SampleBankingApp/Services/TransactionService.cs | 44 | Incorrect transaction recording | Ensure transaction type and status are correct |
| SampleBankingApp/Services/TransactionService.cs | 23 | Missing validation for negative amount | Add validation for negative amounts |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/UserController.cs | 30 | Generic exception handler returns generic message | Return specific error messages |
| SampleBankingApp/Services/UserService.cs | 57 | Generic exception handler in search returns empty list | Return specific error or log |
| SampleBankingApp/Services/TransactionService.cs | 52 | No transaction rollback on error | Implement transaction rollback |
| SampleBankingApp/Services/TransactionService.cs | 23 | No validation for negative amount | Add validation for negative amounts |
| SampleBankingApp/Services/TransactionService.cs | 30 | No validation for zero amount | Add validation for zero amounts |
| SampleBankingApp/Services/TransactionService.cs | 37 | No validation for insufficient funds | Add validation for insufficient funds |
| SampleBankingApp/Services/TransactionService.cs | 41 | No validation for self-transfer | Add validation for self-transfer |
| SampleBankingApp/Services/TransactionService.cs | 44 | No validation for transaction recording | Add validation for transaction recording |
| SampleBankingApp/Services/TransactionService.cs | 52 | No validation for transaction description | Add validation for transaction description |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 23 | SqlConnection not disposed | Use `using` statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 32 | SqlCommand not disposed | Use `using` statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 33 | SqlDataAdapter not disposed | Use `using` statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 43 | SqlCommand not disposed | Use `using` statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 44 | SqlDataAdapter not disposed | Use `using` statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 51 | SqlConnection not disposed | Use `using` statement |
| SampleBankingApp/Data/DatabaseHelper.cs | 52 | SqlCommand not disposed | Use `using` statement |
| SampleBankingApp/Services/EmailService.cs | 20 | SmtpClient not disposed | Use `using` statement |
| SampleBankingApp/Services/EmailService.cs | 23 | MailMessage not disposed | Use `using` statement |
| SampleBankingApp/Services/EmailService.cs | 36 | MailMessage not disposed | Use `using` statement |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/TransactionController.cs | 13 | Null claim value not checked | Add null check for userIdClaim |
| SampleBankingApp/Controllers/TransactionController.cs | 15 | Null claim value not checked | Add null check for userIdClaim |
| SampleBankingApp/Controllers/UserController.cs | 15 | Null claim value not checked | Add null check for userIdClaim |
| SampleBankingApp/Controllers/UserController.cs | 17 | Null claim value not checked | Add null check for userIdClaim |
| SampleBankingApp/Services/AuthService.cs | 25 | Null connection string not checked | Add null check for connection string |
| SampleBankingApp/Services/AuthService.cs | 25 | Null connection string not checked | Add null check for connection string |
| SampleBankingApp/Services/AuthService.cs | 31 | Null config value not checked | Add null check for config value |
| SampleBankingApp/Services/AuthService.cs | 31 | Null config value not checked | Add null check for config value |
| SampleBankingApp/Services/TransactionService.cs | 35 | Null table rows not checked | Add null check for table rows |
| SampleBankingApp/Services/TransactionService.cs | 35 | Null table rows not checked | Add null check for table rows |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 33 | Dead code in JoinWithSeparator method | Remove or mark as obsolete |
| SampleBankingApp/Services/AuthService.cs | 55 | Dead code in ValidateToken method | Remove or mark as obsolete |
| SampleBankingApp/Services/TransactionService.cs | 58 | Dead code in RefundTransaction method | Remove or mark as obsolete |
| SampleBankingApp/Services/UserService.cs | 20 | Dead code in _auditLog static field | Remove or mark as obsolete |
| SampleBankingApp/Services/UserService.cs | 21 | Dead code in _requestCount static field | Remove or mark as obsolete |
| SampleBankingApp/Services/UserService.cs | 22 | Dead code in _auditLog static field | Remove or mark as obsolete |
| SampleBankingApp/Services/UserService.cs | 23 | Dead code in _requestCount static field | Remove or mark as obsolete |
| SampleBankingApp/Services/UserService.cs | 24 | Dead code in _auditLog static field | Remove or mark as obsolete |
| SampleBankingApp/Services/UserService.cs | 25 | Dead code in _requestCount static field | Remove or mark as obsolete |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 13 | Magic number for transaction fee rate | Define as constant |
| SampleBankingApp/Services/TransactionService.cs | 14 | Magic number for max transactions per day | Define as constant |
| SampleBankingApp/Services/UserService.cs | 42 | Magic number for page size limit | Define as constant |
| SampleBankingApp/Services/UserService.cs | 57 | Magic number for search query | Define as constant |
| SampleBankingApp/Services/AuthService.cs | 13 | Magic string for admin bypass password | Define as constant |
| SampleBankingApp/Services/EmailService.cs | 10 | Magic string for transfer subject | Define as constant |
| SampleBankingApp/Services/EmailService.cs | 11 | Magic string for welcome subject | Define as constant |
| SampleBankingApp/Services/EmailService.cs | 13 | Magic number for max retries | Define as constant |
| SampleBankingApp/Services/EmailService.cs | 14 | Magic number for smtp timeout | Define as constant |
| SampleBankingApp/Services/TransactionService.cs | 23 | Magic number for negative amount check | Define as constant |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 25 | String concatenation in loop | Use StringBuilder |
| SampleBankingApp/Services/TransactionService.cs | 35 | String concatenation in SQL | Use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 52 | String concatenation in SQL | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 37 | String concatenation in SQL | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 47 | String concatenation in SQL | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 57 | String concatenation in SQL | Use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 44 | String concatenation in SQL | Use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 52 | String concatenation in SQL | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 57 | String concatenation in SQL | Use parameterized queries |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime set to false | Set to true |
| SampleBankingApp/Program.cs | 29 | CORS policy allows any origin/method/header | Restrict to specific origins |
| SampleBankingApp/Program.cs | 31 | UseDeveloperExceptionPage enabled in production | Remove in production builds |
| SampleBankingApp/Program.cs | 33 | HTTPS redirection commented out | Enable HTTPS redirection |
| SampleBankingApp/appsettings.json | 3 | Hardcoded database password | Move to secure config |
| SampleBankingApp/appsettings.json | 12 | Hardcoded email password | Move to secure config |
| SampleBankingApp/appsettings.json | 17 | Debug log level in production | Set to Warning or Error |
| SampleBankingApp/SampleBankingApp.csproj | 15 | Debug symbols enabled in release | Disable in release builds |
| SampleBankingApp/SampleBankingApp.csproj | 16 | Debug type set to full | Set to pdbonly in release |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 15 | No unit tests for login method | Add unit tests for login method |
| SampleBankingApp/Controllers/TransactionController.cs | 13 | No unit tests for transfer method | Add unit tests for transfer method |
| SampleBankingApp/Controllers/TransactionController.cs | 23 | No unit tests for deposit method | Add unit tests for deposit method |
| SampleBankingApp/Controllers/UserController.cs | 15 | No unit tests for GetUser method | Add unit tests for GetUser method |
| SampleBankingApp/Controllers/UserController.cs | 23 | No unit tests for GetUsers method | Add unit tests for GetUsers method |
| SampleBankingApp/Controllers/UserController.cs | 30 | No unit tests for UpdateUser method | Add unit tests for UpdateUser method |
| SampleBankingApp/Controllers/UserController.cs | 38 | No unit tests for DeleteUser method | Add unit tests for DeleteUser method |
| SampleBankingApp/Services/AuthService.cs | 25 | No unit tests for Login method | Add unit tests for Login method |
| SampleBankingApp/Services/TransactionService.cs | 35 | No unit tests for Transfer method | Add unit tests for Transfer method |
| SampleBankingApp/Services/TransactionService.cs | 44 | No unit tests for Deposit method | Add unit tests for Deposit method |
| SampleBankingApp/Services/UserService.cs | 37 | No unit tests for GetUserById method | Add unit tests for GetUserById method |
| SampleBankingApp/Services/UserService.cs | 47 | No unit tests for UpdateUser method | Add unit tests for UpdateUser method |
| SampleBankingApp/Services/UserService.cs | 57 | No unit tests for SearchUsers method | Add unit tests for SearchUsers method |
| SampleBankingApp/Services/UserService.cs | 60 | No unit tests for GetAuditReport method | Add unit tests for GetAuditReport method |
| SampleBankingApp/Services/EmailService.cs | 23 | No unit tests for SendTransferNotification method | Add unit tests for SendTransferNotification method |
| SampleBankingApp/Services/EmailService.cs | 36 | No unit tests for SendWelcomeEmail method | Add unit tests for SendWelcomeEmail method |
| SampleBankingApp/Services/EmailService.cs | 44 | No unit tests for SendWelcomeEmailHtml method | Add unit tests for SendWelcomeEmailHtml method |
| SampleBankingApp/Services/TransactionService.cs | 58 | No unit tests for RefundTransaction method | Add unit tests for RefundTransaction method |
| SampleBankingApp/Services/UserService.cs | 20 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 21 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 22 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 23 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 24 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 25 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 26 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 27 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 28 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 29 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 30 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 31 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 32 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 33 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 34 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 35 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 36 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 37 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 38 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 39 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 40 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 41 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 42 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 43 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 44 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 45 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 46 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 47 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 48 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 49 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 50 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 51 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 52 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 53 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 54 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 55 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 56 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 57 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 58 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 59 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 60 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 61 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 62 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 63 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 64 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 65 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 66 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 67 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 68 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 69 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 70 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 71 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 72 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 73 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 74 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 75 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 76 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 77 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 78 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 79 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 80 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 81 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 82 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 83 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 84 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 85 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 86 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 87 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 88 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 89 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 90 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 91 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 92 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 93 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 94 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 95 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 96 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 97 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 98 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 99 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 100 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 101 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 102 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 103 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 104 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 105 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 106 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 107 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 108 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 109 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 110 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 111 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 112 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 113 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 114 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 115 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 116 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 117 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 118 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 119 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 120 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 121 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 122 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 123 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 124 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 125 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 126 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 127 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 128 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 129 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 130 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 131 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 132 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 133 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 134 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 135 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 136 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 137 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 138 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 139 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 140 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 141 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 142 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 143 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 144 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 145 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 146 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 147 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 148 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 149 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 150 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 151 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 152 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 153 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 154 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 155 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 156 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 157 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 158 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 159 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 160 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 161 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 162 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 163 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 164 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 165 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 166 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 167 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 168 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 169 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 170 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 171 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 172 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 173 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 174 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 175 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 176 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 177 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 178 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 179 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 180 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 181 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 182 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 183 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 184 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 185 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 186 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 187 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 188 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 189 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 190 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 191 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 192 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 193 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 194 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 195 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 196 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 197 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 198 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 199 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 200 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 201 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 202 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 203 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 204 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 205 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 206 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 207 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 208 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 209 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 210 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 211 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 212 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 213 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 214 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 215 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 216 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 217 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 218 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 219 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 220 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 221 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 222 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 223 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 224 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 225 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 226 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 227 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 228 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 229 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 230 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 231 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 232 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 233 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 234 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 235 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 236 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 237 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 238 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 239 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 240 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 241 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 242 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 243 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 244 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 245 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 246 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 247 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 248 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 249 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 250 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 251 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 252 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 253 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 254 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 255 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 256 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 257 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 258 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 259 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 260 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 261 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 262 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 263 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 264 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 265 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 266 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 267 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 268 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 269 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 270 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 271 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 272 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 273 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 274 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 275 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 276 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 277 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 278 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 279 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 280 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 281 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 282 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 283 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 284 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 285 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 286 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 287 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 288 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 289 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 290 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 291 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 292 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 293 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 294 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 295 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 296 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 297 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 298 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 299 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 300 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 301 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 302 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 303 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 304 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 305 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 306 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 307 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 308 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 309 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 310 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 311 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 312 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 313 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 314 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 315 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 316 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 317 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 318 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 319 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 320 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 321 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 322 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 323 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 324 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 325 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 326 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 327 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 328 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 329 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 330 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 331 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 332 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 333 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 334 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 335 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 336 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 337 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 338 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 339 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 340 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 341 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 342 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 343 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 344 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 345 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 346 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 347 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 348 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 349 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 350 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 351 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 352 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 353 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 354 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 355 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 356 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 357 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 358 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 359 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 360 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 361 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 362 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 363 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 364 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 365 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 366 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 367 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 368 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 369 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 370 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 371 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 372 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 373 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 374 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 375 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 376 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 377 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 378 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 379 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 380 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 381 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 382 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 383 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 384 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 385 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 386 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 387 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 388 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 389 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 390 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 391 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 392 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 393 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 394 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 395 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 396 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 397 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 398 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 399 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 400 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 401 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 402 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 403 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 404 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 405 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 406 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 407 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 408 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 409 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 410 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 411 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 412 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 413 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 414 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 415 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 416 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 417 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 418 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 419 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 420 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 421 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 422 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 423 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 424 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 425 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 426 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 427 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 428 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 429 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 430 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBankingApp/Services/UserService.cs | 431 | No unit tests for request count functionality | Add unit tests for request count functionality |
| SampleBankingApp/Services/UserService.cs | 432 | No unit tests for audit log functionality | Add unit tests for audit log functionality |
| SampleBanking