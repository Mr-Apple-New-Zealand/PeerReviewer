# Peer Code Review Report

## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 23 | SQL injection vulnerability in Login method due to string interpolation | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/AuthService.cs | 23 | MD5 used for password hashing which is insecure | Replace with secure password hashing algorithm like bcrypt |
| SampleBankingApp/Services/AuthService.cs | 44 | Hardcoded admin password "SuperAdmin2024" in source code | Remove hardcoded credentials and use secure authentication mechanism |
| SampleBankingApp/Program.cs | 23 | JWT ValidateLifetime set to false allowing token reuse after expiration | Set ValidateLifetime to true for proper token expiration enforcement |
| SampleBankingApp/Program.cs | 25 | Developer exception page enabled in production | Remove UseDeveloperExceptionPage() in production environment |
| SampleBankingApp/Program.cs | 27 | Overly permissive CORS policy allowing any origin, method, and header | Restrict CORS to specific trusted origins and required methods |
| SampleBankingApp/Services/TransactionService.cs | 44 | SQL injection vulnerability in UPDATE statements | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/TransactionService.cs | 47 | SQL injection vulnerability in INSERT statement | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/UserService.cs | 49 | SQL injection vulnerability in DELETE statement | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/UserService.cs | 68 | SQL injection vulnerability in UPDATE statement | Use parameterized queries instead of string concatenation |
| SampleBankingApp/Services/UserService.cs | 100 | SQL injection vulnerability in ExecuteQuery call | Use parameterized queries instead of string interpolation |
| SampleBankingApp/appsettings.json | 8 | Weak JWT secret key "mysecretkey" | Use a cryptographically secure random key |
| SampleBankingApp/Data/DatabaseHelper.cs | 14 | Hardcoded database password "Admin1234!" in source code | Remove default connection string and use secure configuration management |

## 2. Logic Errors

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 31 | Transaction fee calculation is missing from the fromBalance check | Add fee to totalDebit and check if fromBalance >= totalDebit |
| SampleBankingApp/Services/TransactionService.cs | 31 | Transaction fee is not being applied correctly | Add fee to totalDebit and ensure it's subtracted from the sender's balance |
| SampleBankingApp/Services/TransactionService.cs | 37 | Missing self-transfer check | Add validation to prevent transferring to oneself |
| SampleBankingApp/Services/TransactionService.cs | 55 | Deposit method applies interest bonus without validation | Add validation for interest bonus calculation |
| SampleBankingApp/Services/TransactionService.cs | 55 | No validation for interest bonus rate | Add validation for interest bonus rate |
| SampleBankingApp/Services/UserService.cs | 58 | Missing self-transfer check in UpdateUser | Add validation to prevent updating own user account |
| SampleBankingApp/Services/UserService.cs | 82 | Missing self-transfer check in DeleteUser | Add validation to prevent deleting own user account |
| SampleBankingApp/Services/UserService.cs | 31 | Pagination calculation uses page * pageSize which skips first page | Change to (page - 1) * pageSize for correct pagination |
| SampleBankingApp/Services/TransactionService.cs | 18 | No validation for transaction amount being zero | Add validation to ensure amount > 0 |
| SampleBankingApp/Services/TransactionService.cs | 104 | No validation for transactionId parameter | Add validation to ensure transactionId is valid |

## 3. Error Handling

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 34 | No transaction scope for database operations | Wrap database operations in a transaction |
| SampleBankingApp/Services/AuthService.cs | 34 | No error handling for database operations | Add proper error handling and logging |
| SampleBankingApp/Services/TransactionService.cs | 44 | No transaction scope for balance updates | Wrap balance updates in a transaction |
| SampleBankingApp/Services/TransactionService.cs | 44 | No error handling for database operations | Add proper error handling and logging |
| SampleBankingApp/Services/TransactionService.cs | 47 | No transaction scope for transaction recording | Wrap transaction recording in a transaction |
| SampleBankingApp/Services/TransactionService.cs | 47 | No error handling for database operations | Add proper error handling and logging |
| SampleBankingApp/Services/UserService.cs | 49 | No transaction scope for database operations | Wrap database operations in a transaction |
| SampleBankingApp/Services/UserService.cs | 49 | No error handling for database operations | Add proper error handling and logging |
| SampleBankingApp/Services/UserService.cs | 68 | No transaction scope for database operations | Wrap database operations in a transaction |
| SampleBankingApp/Services/UserService.cs | 68 | No error handling for database operations | Add proper error handling and logging |
| SampleBankingApp/Services/UserService.cs | 100 | No error handling for database operations | Add proper error handling and logging |
| SampleBankingApp/Controllers/TransactionController.cs | 36 | Catching general Exception and returning generic message | Log exception details and return appropriate error code |
| SampleBankingApp/Controllers/TransactionController.cs | 36 | No transaction scope for refund operation | Wrap refund operation in a transaction |
| SampleBankingApp/Controllers/UserController.cs | 39 | Catching general Exception and returning ex.Message | Log exception details and return appropriate error code |
| SampleBankingApp/Controllers/UserController.cs | 39 | No transaction scope for update operations | Wrap update operations in a transaction |

## 4. Resource Leaks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 22 | GetOpenConnection returns open connection without ensuring disposal | Return connection using using statement or ensure proper disposal |
| SampleBankingApp/Data/DatabaseHelper.cs | 22 | Connection is opened but not properly disposed | Implement proper connection management |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | Connection is opened but not properly disposed | Implement proper connection management |
| SampleBankingApp/Data/DatabaseHelper.cs | 28 | Command is created but not properly disposed | Implement proper command management |
| SampleBankingApp/Data/DatabaseHelper.cs | 53 | Connection is opened but not properly disposed | Implement proper connection management |
| SampleBankingApp/Data/DatabaseHelper.cs | 53 | Command is created but not properly disposed | Implement proper command management |
| SampleBankingApp/Services/EmailService.cs | 27 | SmtpClient is created as instance field (not thread-safe) | Create SmtpClient on demand or use dependency injection |
| SampleBankingApp/Services/EmailService.cs | 33 | MailMessage is created but not properly disposed | Implement proper disposal of MailMessage |
| SampleBankingApp/Services/EmailService.cs | 62 | MailMessage is created but not properly disposed | Implement proper disposal of MailMessage |
| SampleBankingApp/Services/EmailService.cs | 77 | MailMessage is created but not properly disposed | Implement proper disposal of MailMessage |

## 5. Null Reference Risks

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 34 | No null check for reader | Add null check after ExecuteReader |
| SampleBankingApp/Services/AuthService.cs | 34 | No check for reader.HasRows | Add HasRows check before reading |
| SampleBankingApp/Services/TransactionService.cs | 27 | No null check for fromUserTable | Add null check after database query |
| SampleBankingApp/Services/TransactionService.cs | 27 | No check for fromUserTable.Rows.Count > 0 | Add count check before accessing rows |
| SampleBankingApp/Services/TransactionService.cs | 28 | No null check for toUserTable | Add null check after database query |
| SampleBankingApp/Services/TransactionService.cs | 28 | No check for toUserTable.Rows.Count > 0 | Add count check before accessing rows |
| SampleBankingApp/Services/UserService.cs | 49 | No null check for table | Add null check after database query |
| SampleBankingApp/Services/UserService.cs | 49 | No check for table.Rows.Count > 0 | Add count check before accessing rows |
| SampleBankingApp/Services/UserService.cs | 68 | No null check for table | Add null check after database query |
| SampleBankingApp/Services/UserService.cs | 68 | No check for table.Rows.Count > 0 | Add count check before accessing rows |
| SampleBankingApp/Services/UserService.cs | 100 | No null check for table | Add null check after database query |
| SampleBankingApp/Services/UserService.cs | 100 | No check for table.Rows.Count > 0 | Add count check before accessing rows |

## 6. Dead Code

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Data/DatabaseHelper.cs | 65 | Method marked [Obsolete] but still present | Remove obsolete method |
| SampleBankingApp/Controllers/TransactionController.cs | 31 | NotImplementedException in non-stub code | Implement refund functionality or remove placeholder |
| SampleBankingApp/Services/AuthService.cs | 53 | Unused HashPasswordSha1 method | Remove unused method |
| SampleBankingApp/Services/AuthService.cs | 56 | Unused ValidateToken method | Remove unused method |
| SampleBankingApp/Helpers/StringHelper.cs | 22 | Duplicate JoinWithSeparator method | Remove duplicate method |
| SampleBankingApp/Helpers/StringHelper.cs | 33 | ObfuscateAccount is a duplicate of MaskAccountNumber | Remove duplicate method |
| SampleBankingApp/Services/TransactionService.cs | 104 | RefundTransaction throws NotImplementedException | Implement refund functionality or remove placeholder |

## 7. Magic Strings and Numbers

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/TransactionService.cs | 13 | Magic number 0.015m for transaction fee | Create a named constant for transaction fee rate |
| SampleBankingApp/Services/TransactionService.cs | 14 | Magic number 10 for max transactions per day | Create a named constant for max transactions per day |
| SampleBankingApp/Services/TransactionService.cs | 55 | Magic number 0.05m for interest bonus | Create a named constant for interest bonus rate |
| SampleBankingApp/Services/TransactionService.cs | 55 | Magic number 1 for interest bonus multiplier | Create a named constant for interest bonus multiplier |
| SampleBankingApp/Services/TransactionService.cs | 55 | Magic number 1000000 for deposit limit | Create a named constant for deposit limit |
| SampleBankingApp/Services/UserService.cs | 31 | Magic number 50 for max page size | Create a named constant for max page size |
| SampleBankingApp/Services/AuthService.cs | 23 | Hardcoded "Users" table name | Extract to a configuration or constant |
| SampleBankingApp/Services/AuthService.cs | 23 | Hardcoded "Id" column name | Extract to a configuration or constant |
| SampleBankingApp/Services/AuthService.cs | 23 | Hardcoded "Username" column name | Extract to a configuration or constant |
| SampleBankingApp/Services/AuthService.cs | 23 | Hardcoded "Password" column name | Extract to a configuration or constant |

## 8. Anti-patterns and Code Quality

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Helpers/StringHelper.cs | 17 | String concatenation in loop (JoinWithSeparator) | Replace with string.Join |
| SampleBankingApp/Services/EmailService.cs | 27 | SmtpClient created as instance field (not thread-safe) | Create SmtpClient on demand or use dependency injection |
| SampleBankingApp/Services/TransactionService.cs | 44 | String concatenation for SQL queries | Use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 47 | String concatenation for SQL queries | Use parameterized queries |
| SampleBankingApp/Services/TransactionService.cs | 104 | String concatenation for SQL queries | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 49 | String concatenation for SQL queries | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 68 | String concatenation for SQL queries | Use parameterized queries |
| SampleBankingApp/Services/UserService.cs | 100 | String concatenation for SQL queries | Use parameterized queries |
| SampleBankingApp/Services/AuthService.cs | 23 | String concatenation for SQL queries | Use parameterized queries |
| SampleBankingApp/Services/AuthService.cs | 23 | Reimplementing string.IsNullOrEmpty | Use string.IsNullOrEmpty instead |

## 9. Configuration Issues

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Program.cs | 13 | HTTPS redirection is commented out | Uncomment HTTPS redirection for security |
| SampleBankingApp/Program.cs | 23 | JWT ValidateLifetime is set to false | Set ValidateLifetime to true for proper token expiration |
| SampleBankingApp/Program.cs | 25 | Developer exception page enabled | Remove UseDeveloperExceptionPage() in production |
| SampleBankingApp/Program.cs | 27 | Overly permissive CORS policy | Restrict CORS to specific trusted origins |
| SampleBankingApp/Program.cs | 10 | Missing environment-specific configuration overrides | Add appsettings.Production.json for production settings |
| SampleBankingApp/SampleBankingApp.csproj | 10 | Debug symbols enabled for release builds | Set DebugSymbols to false in release configuration |
| SampleBankingApp/appsettings.json | 16 | Debug log level set for production | Set production log level to "Information" or higher |

## 10. Missing Unit Tests

| File | Line | Issue | Fix |
|---|---|---|---|
| SampleBankingApp/Services/AuthService.cs | 23 | No unit tests for Login method | Add tests for successful login, failed login, and admin bypass |
| SampleBankingApp/Services/TransactionService.cs | 18 | No unit tests for Transfer method | Add tests for successful transfer, insufficient funds, and self-transfer |
| SampleBankingApp/Services/TransactionService.cs | 55 | No unit tests for Deposit method | Add tests for valid deposit, invalid deposit, and deposit limits |
| SampleBankingApp/Services/UserService.cs | 31 | No unit tests for GetUsersPage | Add tests for pagination, edge cases, and large page sizes |
| SampleBankingApp/Controllers/AuthController.cs | 18 | No unit tests for Login endpoint | Add tests for successful login, failed login, and error handling |
| SampleBankingApp/Controllers/TransactionController.cs | 18 | No unit tests for Transfer endpoint | Add tests for successful transfer, insufficient funds, and error handling |
| SampleBankingApp/Controllers/TransactionController.cs | 31 | No unit tests for Refund endpoint | Add tests for successful refund, error handling, and validation |
| SampleBankingApp/Controllers/UserController.cs | 18 | No unit tests for GetUser endpoint | Add tests for existing user, non-existent user, and error handling |
| SampleBankingApp/Controllers/UserController.cs | 31 | No unit tests for UpdateUser endpoint | Add tests for successful update, validation errors, and error handling |
| SampleBankingApp/Controllers/UserController.cs | 44 | No unit tests for DeleteUser endpoint | Add tests for successful deletion, validation errors, and error handling |