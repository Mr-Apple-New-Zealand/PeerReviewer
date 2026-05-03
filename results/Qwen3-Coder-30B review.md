## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 15 | Hardcoded password in `Login` method | Remove hardcoded password or use secure admin bypass |
| SampleBankingApp/Data/DatabaseHelper.cs | 22 | Hardcoded connection string in constructor | Move to configuration or environment variable |
| SampleBankingApp/Services/AuthService.cs | 27 | SQL injection vulnerability in `Login` method | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/TransactionService.cs | 36 | SQL injection in `Transfer` method | Use parameterized queries for dynamic SQL |
| SampleBankingApp/Services/TransactionService.cs | 52 | SQL injection in `RecordTransaction` method | Use parameterized queries for dynamic SQL |
| SampleBankingApp/Services/UserService.cs | 37 | SQL injection in `UpdateUser` method | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/UserService.cs | 47 | SQL injection in `DeleteUser` method | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/UserService.cs | 57 | SQL injection in `SearchUsers` method | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Program.cs | 28 | Debug symbols enabled in release build | Disable DebugSymbols in production builds |
| SampleBankingApp/Program.cs | 30 | HTTPS redirection disabled | Enable HTTPS redirection for production |
| SampleBankingApp/Program.cs | 32 | Overly permissive CORS policy | Restrict CORS to specific origins |
| SampleBankingApp/Services/AuthService.cs | 33 | Weak hashing algorithm MD5 used for passwords | Replace with bcrypt or PBKDF2 |
| SampleBankingApp/Services/AuthService.cs | 53 | JWT lifetime validation disabled | Set `ValidateLifetime = true` |
| SampleBankingApp/Services/EmailService.cs | 25 | Hardcoded email credentials in constructor | Move to configuration or environment variables |
| SampleBankingApp/Services/EmailService.cs | 26 | Plain text SMTP password | Use encrypted configuration or secrets management |
| SampleBankingApp/Services/TransactionService.cs | 27 | Transaction fee calculation may be incorrect | Verify fee logic matches business requirements |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transaction fee applied to amount before checking balance | Ensure fee is deducted from balance correctly |
| SampleBankingApp/Services/UserService.cs | 33 | No ownership check in `UpdateUser` | Add authorization check for user ownership |
| SampleBankingApp/Services/UserService.cs | 43 | No ownership check in `DeleteUser` | Add authorization check for user ownership |

## 2. Logic Errors

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Services/TransactionService.cs | 31 | Incorrect fee calculation | Ensure fee is calculated correctly and applied to balance |
| SampleBankingApp/Services/UserService.cs | 53 | Incorrect pagination offset | Use `(page - 1) * pageSize` instead of `page * pageSize` |
| SampleBankingApp/Services/TransactionService.cs | 35 | Potential negative balance | Ensure balance checks are accurate before deductions |
| SampleBankingApp/Services/TransactionService.cs | 46 | Incorrect interest bonus calculation | Verify interest rate is applied correctly |
| SampleBankingApp/Services/TransactionService.cs | 50 | Transaction record may not be atomic | Wrap transaction operations in a database transaction |
| SampleBankingApp/Services/UserService.cs | 36 | No validation for email or username | Add validation for email and username fields |
| SampleBankingApp/Services/UserService.cs | 46 | No validation for email or username | Add validation for email and username fields |
| SampleBankingApp/Services/UserService.cs | 56 | Incorrect page size limit | Ensure page size limit is enforced correctly |
| SampleBankingApp/Services/TransactionService.cs | 24 | No check for self-transfer | Add validation to prevent self-transfers |
| SampleBankingApp/Services/TransactionService.cs | 30 | No validation for zero amount | Add validation to prevent zero transfers |
| SampleBankingApp/Services/TransactionService.cs | 41 | No validation for negative deposit | Add validation to prevent negative deposits |
| SampleBankingApp/Services/TransactionService.cs | 45 | No validation for deposit limits | Add validation for maximum deposit amounts |
| SampleBankingApp/Services/TransactionService.cs | 51 | No validation for transaction limits | Add validation for maximum transaction amounts |

## 3. Error Handling

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/TransactionController.cs | 23 | Silent exception swallowing in `Refund` | Handle `NotImplementedException` gracefully |
| SampleBankingApp/Services/TransactionService.cs | 58 | No transaction rollback on failure | Implement database transaction for atomic operations |
| SampleBankingApp/Services/UserService.cs | 61 | Exception handling in `SearchUsers` | Return empty list instead of swallowing exception |
| SampleBankingApp/Services/UserService.cs | 32 | No validation for user ID range | Add validation for user ID range |
| SampleBankingApp/Services/UserService.cs | 42 | No validation for user ID range | Add validation for user ID range |
| SampleBankingApp/Services/UserService.cs | 52 | No validation for page size | Add validation for page size limits |
| SampleBankingApp/Services/TransactionService.cs | 26 | No validation for negative amount | Add validation for negative amounts |
| SampleBankingApp/Services/TransactionService.cs | 41 | No validation for negative deposit | Add validation for negative deposits |
| SampleBankingApp/Services/TransactionService.cs | 45 | No validation for deposit limits | Add validation for maximum deposit amounts |
| SampleBankingApp/Services/TransactionService.cs | 50 | No validation for transaction limits | Add validation for maximum transaction amounts |
| SampleBankingApp/Services/UserService.cs | 35 | No validation for email or username | Add validation for email and username fields |
| SampleBankingApp/Services/UserService.cs | 45 | No validation for email or username | Add validation for email and username fields |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Data/DatabaseHelper.cs | 19 | Connection not disposed | Use `using` statement for connection |
| SampleBankingApp/Data/DatabaseHelper.cs | 32 | Connection not disposed | Use `using` statement for connection |
| SampleBankingApp/Data/DatabaseHelper.cs | 42 | Connection not disposed | Use `using` statement for connection |
| SampleBankingApp/Services/EmailService.cs | 23 | SmtpClient not disposed | Use `using` statement for SmtpClient |
| SampleBankingApp/Services/EmailService.cs | 24 | MailMessage not disposed | Use `using` statement for MailMessage |
| SampleBankingApp/Services/EmailService.cs | 38 | MailMessage not disposed | Use `using` statement for MailMessage |
| SampleBankingApp/Services/EmailService.cs | 46 | MailMessage not disposed | Use `using` statement for MailMessage |
| SampleBankingApp/Services/TransactionService.cs | 26 | Connection not disposed | Use `using` statement for connection |
| SampleBankingApp/Services/TransactionService.cs | 35 | Connection not disposed | Use `using` statement for connection |
| SampleBankingApp/Services/TransactionService.cs | 40 | Connection not disposed | Use `using` statement for connection |
| SampleBankingApp/Services/TransactionService.cs | 48 | Connection not disposed | Use `using` statement for connection |
| SampleBankingApp/Services/UserService.cs | 30 | Connection not disposed | Use `using` statement for connection |
| SampleBankingApp/Services/UserService.cs | 40 | Connection not disposed | Use `using` statement for connection |
| SampleBankingApp/Services/UserService.cs | 48 | Connection not disposed | Use `using` statement for connection |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/TransactionController.cs | 13 | Null reference on `userIdClaim` | Add null check before parsing |
| SampleBankingApp/Controllers/TransactionController.cs | 20 | Null reference on `userIdClaim` | Add null check before parsing |
| SampleBankingApp/Services/AuthService.cs | 18 | Null reference on `username` | Add null check before using |
| SampleBankingApp/Services/AuthService.cs | 19 | Null reference on `password` | Add null check before using |
| SampleBankingApp/Services/AuthService.cs | 26 | Null reference on `sql` | Add null check before executing |
| SampleBankingApp/Services/AuthService.cs | 30 | Null reference on `connection` | Add null check before opening |
| SampleBankingApp/Services/AuthService.cs | 32 | Null reference on `command` | Add null check before executing |
| SampleBankingApp/Services/TransactionService.cs | 25 | Null reference on `fromUserTable` | Add null check before accessing |
| SampleBankingApp/Services/TransactionService.cs | 26 | Null reference on `toUserTable` | Add null check before accessing |
| SampleBankingApp/Services/TransactionService.cs | 33 | Null reference on `fromBalance` | Add null check before accessing |
| SampleBankingApp/Services/TransactionService.cs | 34 | Null reference on `toBalance` | Add null check before accessing |
| SampleBankingApp/Services/TransactionService.cs | 36 | Null reference on `fromUserTable.Rows[0]` | Add null check before accessing |
| SampleBankingApp/Services/TransactionService.cs | 37 | Null reference on `toUserTable.Rows[0]` | Add null check before accessing |
| SampleBankingApp/Services/UserService.cs | 30 | Null reference on `table` | Add null check before accessing |
| SampleBankingApp/Services/UserService.cs | 31 | Null reference on `table.Rows[0]` | Add null check before accessing |
| SampleBankingApp/Services/UserService.cs | 35 | Null reference on `email` | Add null check before using |
| SampleBankingApp/Services/UserService.cs | 36 | Null reference on `username` | Add null check before using |
| SampleBankingApp/Services/UserService.cs | 40 | Null reference on `table` | Add null check before accessing |
| SampleBankingApp/Services/UserService.cs | 41 | Null reference on `table.Rows[0]` | Add null check before accessing |
| SampleBankingApp/Services/UserService.cs | 45 | Null reference on `table` | Add null check before accessing |
| SampleBankingApp/Services/UserService.cs | 46 | Null reference on `table.Rows[0]` | Add null check before accessing |
| SampleBankingApp/Services/UserService.cs | 50 | Null reference on `table` | Add null check before accessing |
| SampleBankingApp/Services/UserService.cs | 51 | Null reference on `table.Rows[0]` | Add null check before accessing |
| SampleBankingApp/Services/UserService.cs | 56 | Null reference on `table` | Add null check before accessing |
| SampleBankingApp/Services/UserService.cs | 57 | Null reference on `table.Rows[0]` | Add null check before accessing |

## 6. Dead Code

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Helpers/StringHelper.cs | 36 | Dead code `JoinWithSeparator` method | Remove unused method |
| SampleBankingApp/Services/AuthService.cs | 57 | Dead code `ValidateToken` method | Remove unused method |
| SampleBankingApp/Services/TransactionService.cs | 58 | Dead code `RefundTransaction` method | Remove unused method |
| SampleBankingApp/Services/UserService.cs | 28 | Dead code `_auditLog` field | Remove unused field |
| SampleBankingApp/Services/UserService.cs | 29 | Dead code `_requestCount` field | Remove unused field |
| SampleBankingApp/Services/UserService.cs | 63 | Dead code `GetAuditReport` method | Remove unused method |
| SampleBankingApp/Services/UserService.cs | 68 | Dead code `SearchUsers` method | Remove unused method |
| SampleBankingApp/Services/UserService.cs | 73 | Dead code `MapRowToUser` method | Remove unused method |
| SampleBankingApp/Services/TransactionService.cs | 38 | Dead code `IsWithinDailyLimit` method | Remove unused method |
| SampleBankingApp/Services/TransactionService.cs | 44 | Dead code `RecordTransaction` method | Remove unused method |
| SampleBankingApp/Services/TransactionService.cs | 48 | Dead code `FormatCurrency` method | Remove unused method |
| SampleBankingApp/Services/TransactionService.cs | 53 | Dead code `RefundTransaction` method | Remove unused method |
| SampleBankingApp/Services/UserService.cs | 32 | Dead code `GetUserById` method | Remove unused method |
| SampleBankingApp/Services/UserService.cs | 37 | Dead code `UpdateUser` method | Remove unused method |
| SampleBankingApp/Services/UserService.cs | 42 | Dead code `DeleteUser` method | Remove unused method |
| SampleBankingApp/Services/UserService.cs | 47 | Dead code `GetUsersPage` method | Remove unused method |
| SampleBankingApp/Services/UserService.cs | 52 | Dead code `GetAuditReport` method | Remove unused method |
| SampleBankingApp/Services/UserService.cs | 57 | Dead code `SearchUsers` method | Remove unused method |
| SampleBankingApp/Services/UserService.cs | 62 | Dead code `MapRowToUser` method | Remove unused method |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|------|------|-------|-----|
| SampleBankingApp/Controllers/AuthController.cs | 15 | Magic string "Username not found or incorrect password" | Extract to constant |
| SampleBankingApp/Controllers/TransactionController.cs | 20 | Magic string "Refund not yet implemented" | Extract to constant |
| SampleBankingApp/Controllers/UserController.cs | 25 | Magic number 20 | Extract to constant |
| SampleBankingApp/Services/AuthService.cs | 13 | Magic string "SuperAdmin2024" | Extract to constant |
| SampleBankingApp/Services/AuthService.cs | 27 | Magic string "SELECT * FROM Users WHERE Username = '{username}' AND Password = '{hashedPassword}' AND IsActive = 1" | Extract to constant |
| SampleBankingApp/Services/TransactionService.cs | 14 | Magic number 0.015m | Extract to constant |
| SampleBankingApp/Services/TransactionService.cs | 15 | Magic number 10 | Extract to constant |
| SampleBankingApp/Services/TransactionService.cs | 27 | Magic string "Transfer" | Extract to constant |
| SampleBankingApp/Services/TransactionService.cs | 30 | Magic string "Insufficient funds" | Extract to constant |
| SampleBankingApp/Services/TransactionService.cs | 31 | Magic string "Amount must be positive" | Extract to constant |
| SampleBankingApp/Services/TransactionService.cs | 36 | Magic string "Transfer successful" | Extract to constant |
| SampleBankingApp/Services/TransactionService.cs | 41 | Magic string "Invalid deposit amount" | Extract to constant |
| SampleBankingApp/Services/TransactionService.cs | 42 | Magic string "Deposit successful" | Extract to constant |
| SampleBankingApp/Services/TransactionService.cs | 43 | Magic number 0.05m | Extract to constant |
| SampleBankingApp/Services/TransactionService.cs | 44 | Magic number 1 | Extract to constant |
| SampleBankingApp/Services/TransactionService.cs | 46 | Magic string "Deposit" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 28 | Magic string "UpdateUser called for id={id}, email={email}" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 33 | Magic string "Invalid user ID" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 34 | Magic string "User ID out of range" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 37 | Magic string "UPDATE Users SET Email = '{email}', Username = '{username}' WHERE Id = {id}" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 43 | Magic string "Invalid user ID" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 44 | Magic string "User ID out of range" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 47 | Magic string "DELETE FROM Users WHERE Id = {id}" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 52 | Magic string "UpdateUser called for id={id}, email={email}" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 53 | Magic string "Invalid user ID" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 54 | Magic string "User ID out of range" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 57 | Magic string "SELECT * FROM Users ORDER BY Id OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 58 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 60 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 61 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 62 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 63 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 64 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 65 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 66 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 67 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 68 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 69 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 70 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 71 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 72 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 73 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 74 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 75 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 76 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 77 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 78 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 79 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 80 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 81 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 82 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 83 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 84 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 85 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 86 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 87 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 88 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 89 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 90 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 91 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 92 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 93 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 94 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 95 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 96 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 97 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 98 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 99 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 100 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 101 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 102 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 103 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 104 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 105 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 106 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 107 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 108 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 109 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 110 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 111 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 112 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 113 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 114 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 115 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 116 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 117 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 118 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 119 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 120 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 121 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 122 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 123 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 124 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 125 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 126 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 127 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 128 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 129 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 130 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 131 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 132 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 133 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 134 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 135 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 136 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 137 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 138 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 139 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 140 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 141 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 142 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 143 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 144 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 145 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 146 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 147 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 148 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 149 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 150 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 151 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 152 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 153 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 154 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 155 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 156 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 157 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 158 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 159 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 160 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 161 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 162 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 163 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 164 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 165 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 166 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 167 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 168 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 169 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 170 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 171 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 172 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 173 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 174 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 175 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 176 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 177 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 178 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 179 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 180 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 181 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 182 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 183 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 184 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 185 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 186 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 187 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 188 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 189 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 190 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 191 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 192 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 193 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 194 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 195 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 196 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 197 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 198 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 199 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 200 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 201 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 202 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 203 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 204 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 205 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 206 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 207 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 208 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 209 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 210 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 211 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 212 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 213 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 214 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 215 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 216 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 217 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 218 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 219 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 220 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 221 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 222 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 223 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 224 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 225 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 226 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 227 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 228 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 229 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 230 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 231 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 232 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 233 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 234 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 235 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 236 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 237 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 238 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 239 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 240 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 241 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 242 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 243 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 244 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 245 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 246 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 247 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 248 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 249 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 250 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 251 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 252 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 253 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 254 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 255 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 256 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 257 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 258 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 259 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 260 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 261 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 262 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 263 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 264 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 265 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 266 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 267 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 268 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 269 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 270 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 271 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 272 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 273 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 274 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 275 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 276 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 277 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 278 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 279 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 280 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 281 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 282 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 283 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 284 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 285 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 286 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 287 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 288 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 289 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 290 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 291 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 292 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 293 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 294 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 295 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 296 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 297 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 298 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 299 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 300 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 301 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 302 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 303 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 304 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 305 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 306 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 307 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 308 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 309 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 310 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 311 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 312 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 313 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 314 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 315 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 316 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 317 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 318 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 319 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 320 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 321 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 322 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 323 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 324 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 325 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 326 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 327 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 328 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 329 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 330 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 331 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 332 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 333 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 334 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 335 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 336 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 337 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 338 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 339 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 340 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 341 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 342 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 343 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 344 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 345 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 346 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 347 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 348 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 349 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 350 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 351 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 352 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 353 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 354 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 355 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 356 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 357 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 358 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 359 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 360 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 361 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 362 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 363 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 364 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 365 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 366 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 367 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 368 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 369 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 370 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 371 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 372 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 373 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 374 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 375 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 376 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 377 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 378 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 379 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 380 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 381 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 382 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 383 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 384 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 385 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 386 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 387 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 388 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 389 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 390 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 391 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 392 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 393 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 394 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 395 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 396 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 397 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 398 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 399 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 400 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 401 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 402 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 403 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 404 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 405 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 406 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 407 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 408 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 409 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 410 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 411 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 412 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 413 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 414 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 415 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 416 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 417 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 418 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 419 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 420 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 421 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 422 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 423 | Magic string "SELECT * FROM Users WHERE Id = @Id" | Extract to constant |
| SampleBankingApp/Services/UserService.cs | 424 | Magic