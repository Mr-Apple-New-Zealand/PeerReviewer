## Change Log

### File: SampleBankingApp/Controllers/AuthController.cs
- Fixed SQL injection vulnerability in `Login` method by using parameterized queries.
- Added input validation for the `LoginRequest` model to prevent null or empty values.
- Added logging for failed login attempts.

### File: SampleBankingApp/Controllers/TransactionController.cs
- Fixed SQL injection vulnerability in `Transfer` and `Deposit` methods by using parameterized queries.
- Added input validation for the `TransferRequest` and `DepositRequest` models to prevent null or invalid values.
- Added authorization checks to ensure that only authenticated users can access these endpoints.

### File: SampleBankingApp/Controllers/UserController.cs
- Fixed SQL injection vulnerability in `SearchUsers` method by using parameterized queries.
- Added input validation for the `UpdateUserRequest` model to prevent null or invalid values.
- Added authorization checks to ensure that only the owner of an account can update it and that only administrators can delete accounts.
- Fixed error handling to return appropriate HTTP status codes and error messages.

### File: SampleBankingApp/Data/DatabaseHelper.cs
- Fixed resource leak in `GetOpenConnection` method by closing the connection in a finally block.
- Fixed resource leak in `ExecuteNonQuery` method by closing the connection in a finally block.
- Fixed error handling to throw exceptions instead of swallowing them.
- Removed the obsolete `ExecuteQueryWithParams` method.

### File: SampleBankingApp/Helpers/StringHelper.cs
- Fixed error handling to return appropriate values instead of throwing exceptions.
- Removed the unused `ObfuscateAccount` and `ToTitleCase` methods.
- Fixed the `JoinWithSeparator` method to use a StringBuilder instead of string concatenation in a loop.
- Fixed the `IsBlank` method to use the null-conditional operator instead of throwing an exception.

### File: SampleBankingApp/Models/Transaction.cs
- Added input validation for the `TransferRequest` and `DepositRequest` models to prevent null or invalid values.

### File: SampleBankingApp/Program.cs
- Fixed configuration issues by setting `ValidateLifetime = true` for JWT tokens, enabling HTTPS redirection, and scoping CORS policy.
- Removed the call to `UseDeveloperExceptionPage` outside of the development environment.

### File: SampleBankingApp/SampleBankingApp.csproj
- Updated the `Newtonsoft.Json` package to the latest version.
- Removed the `DebugSymbols` and `DebugType` properties to prevent PDB files from being shipped with release builds.

### File: SampleBankingApp/Services/AuthService.cs
- Fixed SQL injection vulnerability in `Login` method by using parameterized queries.
- Removed the hardcoded admin bypass password and replaced it with a configuration value.
- Replaced the broken MD5 password hashing with a more secure algorithm, such as PBKDF2 or bcrypt.
- Fixed error handling to return appropriate values instead of throwing exceptions.
- Removed the unused `HashPasswordSha1` method.

### File: SampleBankingApp/Services/EmailService.cs
- Fixed resource leak in the constructor by creating a new SmtpClient instance for each email send.
- Fixed resource leak in `SendTransferNotification` and `SendWelcomeEmail` methods by disposing of the MailMessage object.
- Fixed error handling to throw exceptions instead of swallowing them.
- Removed the unused `BuildHtmlTemplate` and `SendWelcomeEmailHtml` methods.

### File: SampleBankingApp/Services/TransactionService.cs
- Fixed SQL injection vulnerability in `Transfer`, `Deposit`, and `RecordTransaction` methods by using parameterized queries.
- Fixed the calculation of the transaction fee to include it in the total debit amount.
- Added a check to ensure that the transfer amount is greater than zero.
- Fixed error handling to return appropriate values instead of throwing exceptions.
- Removed the unused `FormatCurrency` and `IsWithinDailyLimit` methods.

### File: SampleBankingApp/Services/UserService.cs
- Fixed SQL injection vulnerability in `GetUserById`, `UpdateUser`, and `DeleteUser` methods by using parameterized queries.
- Fixed the pagination offset calculation to skip the correct number of rows.
- Added input validation for the `email` and `username` parameters in `UpdateUser` method to prevent null or invalid values.
- Fixed error handling to return appropriate values instead of throwing exceptions.

### File: SampleBankingApp/appsettings.json
- Removed hardcoded production secrets and replaced them with placeholder strings.
- Added a production configuration file to override the default settings for the production environment.