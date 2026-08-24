## 1. Security Vulnerabilities

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Controllers/AuthController.cs | 22 | Login method passes raw request data to service without validation. | Validate input parameters before passing to service. |
| SampleBankingApp/Controllers/TransactionController.cs | 27 | User ID parsed from claim without null check or validation. | Add null check and type validation for userIdClaim. |
| SampleBankingApp/Controllers/UserController.cs | 48 | Returns raw exception message string to client. | Return standardized error response instead of ex.Message. |
| SampleBankingApp/Controllers/UserController.cs | 52 | Returns raw exception message string to client. | Return standardized error response instead of ex.Message. |
| SampleBankingApp/Data/DatabaseHelper.cs | 16 | Hardcoded database password in fallback connection string. | Remove hardcoded password and enforce configuration. |
| SampleBankingApp/Data/DatabaseHelper.cs | 29 | SQL query constructed using string interpolation for table name. | Use parameterized queries to prevent SQL injection. |
| SampleBankingApp/Data/DatabaseHelper.cs | 53 | SQL query constructed using string interpolation for table name. | Use parameterized queries to prevent SQL injection. |
| SampleBankingApp/Data/DatabaseHelper.cs | 53 | SQL query constructed using string interpolation for WHERE clause. | Use parameterized queries to prevent SQL injection. |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL query constructed using string interpolation for table name. | Use parameterized queries to prevent SQL injection. |
| SampleBankingApp/Services/AuthService.cs | 32 | SQL query constructed using string interpolation for WHERE clause. | Use parameterized queries to prevent SQL injection. |
| SampleBankingApp/Services/AuthService.cs | 53 | Hardcoded admin bypass password allows unauthorized access. | Remove hardcoded password and enforce role-based access. |
| SampleBankingApp/Services/AuthService.cs | 63 | Password hashing uses MD5 which is cryptographically broken. | Use BCrypt or Argon2 for password hashing. |
| SampleBankingApp/Services/AuthService.cs | 103 | ValidateToken method returns true unconditionally. | Implement proper token validation logic. |
| SampleBankingApp/Program.cs | 34 | Developer exception page enabled in production. | Remove UseDeveloperExceptionPage or set to false. |
| SampleBankingApp/Program.cs | 36 | HTTPS redirection is commented out. | Uncomment UseHttpsRedirection for production. |
| SampleBankingApp/Program.cs | 38 | CORS policy allows any origin and method. | Restrict allowed origins and methods to specific values. |
| SampleBankingApp/Program.cs | 24 | JWT ValidateLifetime is set to false. | Set ValidateLifetime to true to enforce token expiration. |
| SampleBankingApp/appsettings.json | 3 | Hardcoded database password in configuration file. | Move secrets to environment variables or secure vault. |
| SampleBankingApp/appsettings.json | 6 | Hardcoded JWT secret key in configuration file. | Use environment variables or secure vault for secrets. |
| SampleBankingApp/Services/EmailService.cs | 29 | SMTP client has SSL disabled. | Enable SSL for secure email transmission. |
| SampleBankingApp/Services/EmailService.cs | 22 | SMTP client instance field is not thread-safe. | Use singleton pattern or lock for SMTP client access. |

## 2. Logic Errors

| File | Line | Issue | Fix |
| :--- | :--- | :--- | :--- |
| SampleBankingApp/Services/TransactionService.cs | 42 | Transfer checks balance against amount but deducts fee. | Check balance against totalDebit (amount + fee). |
| SampleBankingApp/Services/TransactionService.cs | 68 | Deposit interest calculation multiplies by 1 unnecessarily. | Remove redundant multiplication operator. |
| SampleBankingApp/Services/TransactionService.cs | 90 | RecordTransaction uses string interpolation for SQL. | Use parameterized queries to prevent SQL injection. |
| SampleBankingApp/Services/TransactionService.cs | 99 | RefundTransaction throws NotImplementedException. | Implement refund logic or remove method. |
| SampleBankingApp/Services/UserService.cs | 72 | Pagination skip calculation is off by one. | Change to (page - 1) * pageSize. |
| SampleBankingApp/Services/UserService.cs | 34 | GetUserById accesses row without checking count. | Check Rows.Count > 0 before accessing row. |
| SampleBankingApp/Services/UserService.cs | 45 | UpdateUser adds to audit log without transaction. | Ensure audit log is atomic with database write. |
| SampleBankingApp/Services/UserService.cs | 64 | DeleteUser adds to audit log without transaction. | Ensure audit log is atomic with database write. |
| SampleBankingApp/Services/UserService.cs | 99 | SearchUsers swallows exceptions and returns empty list. | Return meaningful error or handle exception properly. |
| SampleBankingApp/Services/UserService.cs | 31 | GetUserById returns null without throwing. | Throw exception for invalid ID to match contract. |
| SampleBankingApp/Services/UserService.cs | 40 | UpdateUser throws ArgumentException for invalid ID. | Ensure ID validation is consistent with DeleteUser. |
| SampleBankingApp/Services/UserService.cs | 54 | DeleteUser throws ArgumentException for invalid ID. | Ensure ID validation is consistent with UpdateUser. |
| SampleBankingApp/Services/TransactionService.cs | 25 | Transfer allows negative amount check. | Add check for amount > 0. |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit allows amount <= 0. | Add check for amount > 0. |
| SampleBankingApp/Services/TransactionService.cs | 65 | Deposit allows amount > 1000000. | Add check for amount < 1000000. |
| SampleBankingApp/Helpers/StringHelper.cs | 16 | Regex created inside method called repeatedly. | Move regex to static readonly field. |
| SampleBankingApp/Helpers/StringHelper.cs | 25 | Regex created inside method called repeatedly. | Move regex to static readonly field. |
| SampleBankingApp/Helpers/StringHelper.cs | 31 | JoinWithSeparator uses string concatenation in loop. | Use StringBuilder or string.Join. |
| SampleBankingApp/Helpers/StringHelper.cs | 61 | ToTitleCase calls ToTitleCase on lowercased string. | Use System.Globalization.CultureInfo.TextInfo.ToTitleCase directly. |
| SampleBankingApp/Controllers/TransactionController.cs | 56 | Refund catches NotImplementedException specifically. | Catch all exceptions or remove try-catch block. |
| SampleBankingApp/Controllers/UserController.cs | 26 | GetUser returns NotFound for null user. | Ensure null check is consistent with business logic. |
| SampleBankingApp/Controllers/UserController.cs | 74 | SearchUsers returns list without error details. | Return error details if search fails. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok without validation. | Add authorization check for audit log access. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized for failed login. | Ensure consistent error response format. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token and user data. | Ensure token is returned securely. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest for failure. | Ensure consistent error response format. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest for failure. | Ensure consistent error response format. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report. | Ensure report is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 26 | Login returns Unauthorized with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/AuthController.cs | 30 | Login returns Ok with token. | Ensure token is not exposed in logs. |
| SampleBankingApp/Controllers/TransactionController.cs | 34 | Transfer returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 45 | Deposit returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/TransactionController.cs | 54 | Refund returns Ok without status. | Return appropriate status code for success. |
| SampleBankingApp/Controllers/TransactionController.cs | 58 | Refund returns StatusCode 500 for NotImplementedException. | Return 400 or 501 for not implemented. |
| SampleBankingApp/Controllers/UserController.cs | 48 | UpdateUser returns BadRequest with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 52 | UpdateUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 67 | DeleteUser returns StatusCode 500 with message. | Ensure message is sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 75 | SearchUsers returns Ok with results. | Ensure results are sanitized. |
| SampleBankingApp/Controllers/UserController.cs | 81 | GetAuditLog returns Ok with report