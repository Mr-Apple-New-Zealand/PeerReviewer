### File: SampleBankingApp/Helpers/EmailHelper.cs
```
using System.Net.Mail;

namespace SampleTransferHelper;

public class EmailHelper
{
    private readonly IConfiguration _config;

    private const string TransferSubject = "Transfer Notification - BankingApp";
    private const string WelcomeSubject  = "Welcome to BankingApp!";

    private const int MaxRetries = 3;
    private const int SmtpTimeoutMs = 5000;

    private readonly SmtpClient _smtpClient;

    public EmailHelper(IConfiguration config)
    {
        _config = config;

        _smtpClient = new SmtpClient(_config["Email:SmtpHost"])
        {
            Port = int.Parse(_config["Email:SmtpPort"] ?? "25"),
            Credentials = new NetworkCredential(
                _config["Email:Username"],
                _config["Email:Password"]
            ),
            EnableSsl = false,
            Timeout = SmtpTimeoutMs
        };
    }

    public void SendTransferNotification(string toEmail, decimal amount, string recipientName)
    {
        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";

        var message = new MailMessage(
            from: "notifications@company.com",
            to: toEmail,
            subject: TransferSubject,
            body: body);

        int attempt = 0;
        while (attempt < MaxRetries)
        {
            try
            {
                _smtpClient.Send(message);
                return;
            }
            catch (SmtpException ex)
            {
                attempt++;
                Console.WriteLine($"Email attempt {attempt} failed: {ex.Message}");
                if (attempt >= MaxRetries)
                    throw;
            }
        }
    }

    public void SendWelcomeEmail(string toEmail, string username)
    {
        var body = $"Welcome, {username.ToUpper()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   "For support, email us at support@company.com";

        var message = new MailMessage("notifications@company.com", toEmail, WelcomeSubject, body);

        try
        {
            _smtpClient.Send(message);
        }
        catch (Exception ex)
        emailservice.SendWelcomeEmail(username);
    }

    private string BuildHtmlTemplate(string title, string body)
    {
        return $"<html><body><h1>{title}</h1><p>{body}</p></body></html>";
    }

    public void SendWelcomeEmailHtml(string toEmail, string username)
    {
        var htmlBody = BuildHtmlTemplate("Welcome!", $"Hello {username}, welcome to BankingApp.");
        var message = new MailMessage("notifications@company.com", toEmail, WelcomeSubject, htmlBody);
        message.IsBodyHtml = true;
        _smtpClient.Send(message);
    }
}
```

### File: SampleBankingApp/Services/EmailService.cs
```
using System.Net;
using System.Net.Mail;

namespace SampleBankingApp.Services;

public class EmailService
{
    private readonly IConfiguration _config;

    private const string TransferSubject = "Transfer Notification - BankingApp";
    private const string WelcomeSubject  = "Welcome to BankingApp!";

    private const int MaxRetries = 3;
    private const int SmtpTimeoutMs = 5000;

    private readonly SmtpClient _smtpClient;

    public EmailService(IConfiguration config)
    EmailService
    {
        _config = config;

        _smtpClient = new SmtpClient(_config["Email:SmtpHost"])
        {
            Port = int.Parse(_config["Email:SmtpPort"] ?? "25"),
            Credentials = new NetworkCredential(
                _config["Email:Username"],
                _config["Email:Password"]
            ),
            EnableSsl = false,
            Timeout = SmtpTimeoutMs
        };
    }

    public void SendTransferNotification(string toEmail, decimal amount, string recipientName)
    {
        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";

        var message = new MailMessage(
            from: "notifications@company.com",
            to: toEmail,
            subject: TransferSubject,
            body: body);

        int attempt = 0;
        while (attempt < MaxRetries)
        {
            try
            {
                _smtpClient.Send(message);
                return;
            }
            catch (SmtpException ex)
            {
                attempt++;
                Console.WriteLine($"Email attempt {attempt} failed: {ex.Message}");
                if (attempt >= MaxRetries)
                    throw;
            }
        }
    }

    public void SendWelcomeEmail(string toEmail, string username)
    {
        var body = $"Welcome, {username.ToUpper()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   "For support, email us at support@company.com";

        var message = new MailMessage("notifications@company.com", toEmail, WelcomeSubject, body);

        try
        {
            _smtpClient.Send(message);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Welcome email failed: " + ex.Message);
        }
    }

    private string BuildHtmlTemplate(string title, string body)
    {
        return $"<html><body><h1>{title}</h1><p>{body}</p></body></html>";
    }

    public void SendWelcomeEmailHtml(string toEmail, string username)
    {
        var htmlBody = BuildHtmlTemplate("Welcome!", $"Hello {username}, welcome to BankingApp.");
        var message = new MailMessage("notifications@company.com", toEmail, WelcomeSubject, htmlBody);
        message.IsBodyHtml = true;
        _smtpClient.Send(message);
    }
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace Sample TransferService;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;

    public TransactionService(DatabaseHelper db, EmailService emailService)
    {
        _db = db;
        _emailService = emailService;
    }

    /// <summary>
    /// Transfers funds between two accounts.
    /// </summary>
    public (bool Success, string Message) Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount < 0)
            return (false, "Amount must be positive");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= amount)
        {
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance   = toBalance + amount;

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newFromBalance} WHERE Id = {fromUserId}");
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newToBalance} WHERE Id = {toUserId}");

            RecordTransaction(fromUserId, toUserId, amount, "Transfer", description);

            _emailService.SendTransferNotification(
                (string)fromUserTable.Rows[0]["Email"],
                amount,
                (string)toUserTable.Rows[0]["Username"]);

            return (true, "Transfer successful");
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > 1000000)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.05m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + {amount + interestBonus} WHERE Id = {userId}");

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private bool IsWithinDailyLimit(int userId)
    1000000)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT COUNT(*) AS TxCount FROM Transactions WHERE FromUserId = @Id AND CAST(CreatedAt AS DATE) = CAST(GETDATE() AS DATE)",
            new Dictionary<string, object> { { "@Id", userId } });

        int count = (int)table.Rows[0]["TxCount"];
        return count < MaxTransactionsPerDay;
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        string sql = $@"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES ({fromId}, {toId}, {amount}, '{type}', 'Completed', '{description}', GETDATE())";
        _db.ExecuteNonQuery(sql);
    }

    private string FormatCurrency(decimal amount)
    {
        return $"${amount:F2}";
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}
```

### File: SampleBankingApp/Services/UserService.cs
```
using SampleBankingApp.Data;
using SampleBank UserController;

namespace SampleBankingApp.Services;

public class UserService
{
    private readonly DatabaseHelper _db;

    private static List<string> _auditLog = new();
    private static int _requestCount = 0;

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    public User? GetUserById(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", id } });

        if (table.Rows.Count == 0)
            return null;

        var row = table.Rows[0];
        return MapRowToUser(row);
    }

    public bool UpdateUser(int id, string email, string username)
   
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _auditLog.Add($"UpdateUser called for id={id}, email={email}");

        string sql = $"UPDATE Users SET Email = '{email}', Username = '{username}' WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);
        return true;
    }

    public bool DeleteUser(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id >  ty
        {
            _requestCount++;

            string sql = $"DELETE FROM Users WHERE Id = {id}";
            _db.ExecuteNonQuery(sql);

            _auditLog.Add($"DeleteUser: {id}");
            return true;
        }
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = page * pageSize;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users ORDER BY Id OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY",
            new Dictionary<string, object> { { "@Skip", skip }, { "@PageSize", pageSize } });

        var users = new List<User>();
        foreach (System.Data.DataRow row in table.Rows)
            users.Add(MapRowToUser(row));

        return users;
    }

    public string GetAuditReport()
    {
        string report = "";
        foreach (var entry in _auditLog)
        {
            report += entry + "\n";
        }
        return report;
    }

    public List<User> SearchUsers(string query)
    {
        try
       
        {
            var table = _db.ExecuteQuery("Users", $"Username LIKE '%{query}%'");
            var users = new List<User>();
            foreach (System.Data.DataRow row in table.Rows)
                users.Add(MapRowToUser(row));
            return users;
        }
        catch (Exception)
        {
            return new List<User>();
        }
    }

    private User MapRowToUser(System.Data.DataRow row)
    {
        return new User
        {
            Id = (int)row["Id"],
            Username = (string)row["Username"],
            Email = (string)row["Email"],
            Role = (string)row["Role"],
            Balance = (decimal)row["Balance"],
            IsActive = (bool)row["IsActive"],
            CreatedAt = (DateTime)row["CreatedAt"],
        };
    }
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;

    public TransactionService(DatabaseHelper db, EmailService emailService)
    Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount < 0)
            return (false, "Amount must be positive");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= amount)
        {
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance   = toBalance + amount;

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newFromBalance} WHERE Id = {fromUserId}");
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newToBalance} WHERE Id = {toUserId}");

            RecordTransaction(fromUserId, toUserId, amount, "Transfer", description);

            _emailService.SendTransferNotification(
                (string)fromUserTable.Rows[0]["Email"],
                amount,
                (string)toUserTable.Rows[0]["Username"]);

            return (true, "Transfer successful");
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > 1000000)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.05m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + {amount + interestBonus} WHERE Id = {userId}");

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private bool IsWithinDailyLimit(int userId)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT COUNT(*) AS TxCount FROM Transactions WHERE FromUserId = @Id AND CAST(CreatedAt AS DATE) = CAST(GETDATE() AS DATE)",
            new Dictionary<string, object> { { "@Id", userId } });

        int count = (int)table.Rows[0]["TxCount"];
        return count < MaxTransactionsPerDay;
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        string sql = $@"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES ({fromId}, {toId}, {amount}, '{type}', 'Completed', '{description}', GETDATE())";
        _db.ExecuteNonQuery(sql);
    }

    private string FormatCurrency(decimal amount)
    {
        return $"${amount:F2}";
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}
```

### File: SampleBankingApp/Services/UserService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class UserService
{
    private readonly DatabaseHelper _db;

    private static List<string> _auditLog = new();
    private static int _requestCount =  code;

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    public User? GetUserById(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", id } });

        if (table.Rows.Count == 0)
            return null;

        var row = table.Rows[0];
        return MapRowToUser(row);
    }

    public bool UpdateUser(int id, string email, string username)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _auditLog.Add($"UpdateUser called for id={id}, email={email}");

        string sql = $"UPDATE Users SET Email = '{email}', Username = '{username}' WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);
        return true;
    }

    public bool DeleteUser(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        string sql = $"DELETE FROM Users WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = page * pageSize;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users ORDER BY Id OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY",
            new Dictionary<string, object> { { "@Skip", skip }, { "@PageSize", pageSize } });

        var users = new List<User>();
        foreach (System.Data.DataRow row in table.Rows)
            users.Add(MapRowToUser(row));

        return users;
    }

    public string GetAuditReport()
    {
        string report = "";
        foreach (var entry in _auditLog)
        {
            report += entry + "\n";
        }
        return report;
    }

    public List<User> SearchUsers(string query)
    {
        try
        {
            var table = _db.ExecuteQuery("Users", $"Username LIKE '%{query}%'");
            var users = new List<User>();
            foreach (System.Data.DataRow row in table.Rows)
                users.Add(MapRowToUser(row));
            return users;
        }
        catch (Exception)
       
        {
            return new List<User>();
        }
    }

    private User MapRowToUser(System.Data.DataRow row)
    {
        return new User
        {
            Id = (int)row["Id"],
            Username = (string)row["Username"],
            Email = (string)row["Email"],
            Role = (string)row["Role"],
            Balance = (decimal)row["Balance"],
            IsActive = (bool)row["IsActive"],
            CreatedAt = (DateTime)row["CreatedAt"],
        };
    }
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;

    public TransactionService(DatabaseHelper db, EmailService emailService)
    {
        _db = db;
        _emailService = emailService;
    }

    /// <summary>
    /// Transfers funds between two accounts.
    /// </summary>
    public (bool Success, string Message) Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount < 0)
            return (false, "Amount must be positive");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= amount)
        {
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance   = toBalance + amount;

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newFromBalance} WHERE Id = {fromUserId}");
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newToBalance} WHERE Id = {toUserId}");

            RecordTransaction(fromUserId, toUserId, amount, "Transfer", description);

            _emailService.SendTransferNotification(
                (string)fromUserTable.Rows[0]["Email"],
                amount,
                (string)toUserTable.Rows[0]["Username"]);

            return (true, "Transfer successful");
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > 1000000)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.05m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + {amount + interestBonus} WHERE Id = {userId}");

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private bool IsWithinDailyLimit(int userId)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT COUNT(*) AS TxCount FROM Transactions WHERE FromUserId = @Id AND CAST(CreatedAt AS DATE) = CAST(GETDATE() AS DATE)",
            new Dictionary<string, object> { { "@Id", userId } });

        int count = (int)table.Rows[0]["TxCount"];
        return count < MaxTransactionsPerDay;
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        string sql = $@"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES ({fromId}, {toId}, {amount}, '{type}', 'Completed', '{description}', GETDATE())";
        _db.ExecuteNonQuery(sql);
    }

    private string FormatCurrency(decimal amount)
    {
        return $"${amount:F2}";
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}
```

### File: SampleBankingApp/Services/UserService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class UserService
{
    private readonly DatabaseHelper _db;

    private static List<string> _auditLog = new();
    private static int _requestCount = 0;

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    public User? GetUserById(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", id } });

        if (table.Rows.Count == 0)
            return null;

        var row = table.Rows[0];
        return MapRowToUser(row);
    }

    public bool UpdateUser(int id, string email, string username)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _auditLog.Add($"UpdateUser called for id={id}, email={email}");

        string sql = $"UPDATE Users SET Email = '{email}', Username = '{username}' WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);
        return true;
    }

    public bool DeleteUser(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        string sql = $"DELETE FROM Users WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = page * pageSize;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users ORDER BY Id OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY",
            new Dictionary<string, object> { { "@Skip", skip }, { "@PageSize", pageSize } });

        var users = new List<User>();
        foreach (System.Data.DataRow row in table.Rows)
            users.Add(MapRowToUser(row));

        return users;
    }

    public string GetAuditReport()
    {
        string report = "";
        foreach (var entry in _auditLog)
        {
            report += entry + "\n";
        }
        return report;
    }

    public List<User> SearchUsers(string query)
    {
        try
        {
            var table = _db.ExecuteQuery("Users", $"Username LIKE '%{query}%'");
            var users = new List<User>();
            foreach (System.Data.DataRow row in table.Rows)
                users.Add(MapRowToUser(row));
            return users;
        }
        catch (Exception)
        {
            return new List<User>();
        }
    }

    private User MapRowToUser(System.Data.DataRow row)
    {
        return new User
        {
            Id = (int)row["Id"],
            Username = (string)row["Username"],
            Email = (string)row["Email"],
            Role = (string)row["Role"],
            Balance = (decimal)row["Balance"],
            IsActive = (bool)row["IsActive"],
            CreatedAt = (DateTime)row["CreatedAt"],
        };
    }
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;

    public TransactionService(DatabaseHelper db, EmailService emailService)
    {
        _db = db;
        _emailService = emailService;
    }

    /// <summary>
    /// Transfers funds between two accounts.
    /// </summary>
    public (bool Success, string Message) Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount <  logic errors
        {
            if (amount < 0)
                return (false, "Amount must be positive");

            var fromUserTable = _db.ExecuteQuerySafe(
                "SELECT * FROM Users WHERE Id = @Id",
                new Dictionary<string, object> { { "@Id", fromUserId } });

            var toUserTable = _db.ExecuteQuerySafe(
                "SELECT * FROM Users WHERE Id = @Id",
                new Dictionary<string, object> { { "@Id", toUserId } });

            var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
            var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

            decimal fee = Math.Round(amount * TransactionFeeRate, 2);
            decimal totalDebit = amount + fee;

            if (fromBalance >= amount)
            {
                decimal newFromBalance = fromBalance - totalDebit;
                decimal newToBalance   = toBalance + amount;

                _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newFromBalance} WHERE Id = {fromUserId}");
                _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newToBalance} WHERE Id = {toUserId}");

                RecordTransaction(fromUserId, toUserId, amount, "Transfer", description);

                _emailService.SendTransferNotification(
                    (string)fromUserTable.Rows[0]["Email"],
                    amount,
                    (string)toUserTable.Rows[0]["Username"]);

                return (true, "Transfer successful");
            }

            return (false, "Insufficient funds");
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > 1000000)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.05m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + {amount + interestBonus} WHERE Id = {userId}");

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private bool IsWithinDailyLimit(int userId)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT COUNT(*) AS TxCount FROM Transactions WHERE FromUserId = @Id AND CAST(CreatedAt AS DATE) = CAST(GETDATE() AS DATE)",
            new Dictionary<string, object> { { "@Id", userId } });

        int count = (int)table.Rows[0]["TxCount"];
        return count < MaxTransactionsPerDay;
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        string sql = $@"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES ({fromId}, {toId}, {amount}, '{type}', 'Completed', '{description}', GETDATE())";
        _db.ExecuteNonQuery(sql);
    }

    private string FormatCurrency(decimal amount)
    {
        return $"${amount:F2}";
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}
```

### File: SampleBankingApp/Services/UserService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class UserService
{
    private readonly DatabaseHelper _db;

    private static List<string> _auditLog = new();
    private static int _requestCount = 0;

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    public User? GetUserById(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", id } });

        if (table.Rows.Count == 0)
            return null;

        var row = table.Rows[0];
        return MapRowToUser(row);
    }

    public bool UpdateUser(int id, string email, string username)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _auditLog.Add($"UpdateUser called for id={id}, email={email}");

        string sql = $"UPDATE Users SET Email = '{email}', Username = '{username}' WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);
        return true;
    }

    public bool DeleteUser(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        string sql = $"DELETE FROM Users WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = page * pageSize;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users ORDER BY Id OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY",
            new Dictionary<string, object> { { "@Skip", skip }, { "@PageSize", pageSize } });

        var users = new List<User>();
        foreach (System.Data.DataRow row in table.Rows)
            users.Add(MapRowToUser(row));

        return users;
    }

    public string GetAuditReport()
    {
        string report = "";
        foreach (var entry in _auditLog)
        {
            report += entry + "\n";
        }
        return report;
    }

    public List<User> SearchUsers(string query)
    {
        try
        {
            var table = _db.ExecuteQuery("Users", $"Username LIKE '%{query}%'");
            var users = new List<User>();
            foreach (System.Data.DataRow row in table.Rows)
                users.Add(MapRowToUser(row));
            return users;
        }
        catch (Exception)
        {
            return new List<User>();
        }
    }

    private User MapRowToUser(System.Data.DataRow row)
    {
        return new User
        {
            Id = (int)row["Id"],
            Username = (string)row["Username"],
            Email = (string)row["Email"],
            Role = (string)row["Role"],
            Balance = (decimal)row["Balance"],
            IsActive = (bool)row["IsActive"],
            CreatedAt = (DateTime)row["CreatedAt"],
        };
    }
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;

    public TransactionService(DatabaseHelper db, EmailService emailService)
    Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount < 0)
            return (false, "Amount must be positive");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= amount)
        {
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance   = toBalance + amount;

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newFromBalance} WHERE Id = {fromUserId}");
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newToBalance} WHERE Id = {toUserId}");

            RecordTransaction(fromUserId, toUserId, amount, "Transfer", description);

            _emailService.SendTransferNotification(
                (string)fromUserTable.Rows[0]["Email"],
                amount,
                (string)toUserTable.Rows[0]["Username"]);

            return (true, "Transfer successful");
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > 1000000)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.05m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + {amount + interestBonus} WHERE Id = {userId}");

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private bool IsWithinDailyLimit(int userId)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT COUNT(*) AS TxCount FROM Transactions WHERE FromUserId = @Id AND CAST(CreatedAt AS DATE) = CAST(GETDATE() AS DATE)",
            new Dictionary<string, object> { { "@Id", userId } });

        int count = (int)table.Rows[0]["TxCount"];
        return count < MaxTransactionsPerDay;
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        string sql = $@"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES ({fromId}, {toId}, {amount}, '{type}', 'Completed', '{description}', GETDATE())";
        _db.ExecuteNonQuery(sql);
    }

    private string FormatCurrency(decimal amount)
    {
        return $"${amount:F2}";
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}
```

### File: SampleBankingApp/Services/UserService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class UserService
{
    private readonly DatabaseHelper _db;

    private static List<string> _auditLog = new();
    private static int _requestCount = 0;

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    public User? GetUserById(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", id } });

        if (table.Rows.Count == 0)
            return null;

        var row = table.Rows[0];
        return MapRowToUser(row);
    }

    public bool UpdateUser(int id, string email, string username)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _auditLog.Add($"UpdateUser called for id={id}, email={email}");

        string sql = $"UPDATE Users SET Email = '{email}', Username = '{username}' WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);
        return true;
    }

    public bool DeleteUser(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        string sql = $"DELETE FROM Users WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = page * pageSize;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users ORDER BY Id OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY",
            new Dictionary<string, object> { { "@Skip", skip }, { "@PageSize", pageSize } });

        var users = new List<User>();
        foreach (System.Data.DataRow row in table.Rows)
            users.Add(MapRowToUser(row));

        return users;
    }

    public string GetAuditReport()
    {
        string report = "";
        foreach (var entry in _auditLog)
        {
            report += entry + "\n";
        }
        return report;
    }

    public List<User> SearchUsers(string query)
    {
        try
        {
            var table = _db.ExecuteQuery("Users", $"Username LIKE '%{query}%'");
            var users = new List<User>();
            foreach (System.Data.DataRow row in table.Rows)
                users.Add(MapRowToUser(row));
            return users;
        }
        catch (Exception)
        {
            return new List<User>();
        }
    }

    private User MapRowToUser(System.Data.DataRow row)
    {
        return new User
        {
            Id = (int)row["Id"],
            Username = (string)row["Username"],
            Email = (string)row["Email"],
            Role = (string)row["Role"],
            Balance = (decimal)row["Balance"],
            IsActive = (bool)row["IsActive"],
            CreatedAt = (DateTime)row["CreatedAt"],
        };
    }
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;

    public TransactionService(DatabaseHelper db, EmailService emailService)
    Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount < 0)
            return (false, "Amount must be positive");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= amount)
        {
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance   = toBalance + amount;

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newFromBalance} WHERE Id = {fromUserId}");
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newToBalance} WHERE Id = {toUserId}");

            RecordTransaction(fromUserId, toUserId, amount, "Transfer", description);

            _emailService.SendTransferNotification(
                (string)fromUserTable.Rows[0]["Email"],
                amount,
                (string)toUserTable.Rows[0]["Username"]);

            return (true, "Transfer successful");
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > 1000000)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.05m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + {amount + interestBonus} WHERE Id = {userId}");

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private bool IsWithinDailyLimit(int userId)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT COUNT(*) AS TxCount FROM Transactions WHERE FromUserId = @Id AND CAST(CreatedAt AS DATE) = CAST(GETDATE() AS DATE)",
            new Dictionary<string, object> { { "@Id", userId } });

        int count = (int)table.Rows[0]["TxCount"];
        return count < MaxTransactionsPerDay;
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        string sql = $@"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES ({fromId}, {toId}, {amount}, '{type}', 'Completed', '{description}', GETDATE())";
        _db.ExecuteNonQuery(sql);
    }

    private string FormatCurrency(decimal amount)
    {
        return $"${amount:F2}";
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}
```

### File: SampleBankingApp/Services/UserService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class UserService
{
    private readonly DatabaseHelper _db;

    private static List<string> _auditLog = new();
    private static int _requestCount = 0;

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    public User? GetUserById(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", id } });

        if (table.Rows.Count == 0)
            return null;

        var row = table.Rows[0];
        return MapRowToUser(row);
    }

    public bool UpdateUser(int id, string email, string username)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _auditLog.Add($"UpdateUser called for id={id}, email={email}");

        string sql = $"UPDATE Users SET Email = '{email}', Username = '{username}' WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);
        return true;
    }

    public bool DeleteUser(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of null reference risks
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        string sql = $"DELETE FROM Users WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = page * pageSize;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users ORDER BY Id OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY",
            new Dictionary<string, object> { { "@Skip", skip }, { "@PageSize", pageSize } });

        var users = new List<User>();
        foreach (System.Data.DataRow row in table.Rows)
            users.Add(MapRowToUser(row));

        return users;
    }

    public string GetAuditReport()
    {
        string report = "";
        foreach (var entry in _auditLog)
        {
            report += entry + "\n";
        }
        return report;
    }

    public List<User> SearchUsers(string query)
    {
        try
        {
            var table = _db.ExecuteQuery("Users", $"Username LIKE '%{query}%'");
            var users = new List<User>();
            foreach (System.Data.DataRow row in table.Rows)
                users.Add(MapRowToUser(row));
            return users;
        }
        catch (Exception)
        {
            return new List<User>();
        }
    }

    private User MapRowToUser(System.Data.DataRow row)
    {
        return new User
        {
            Id = (int)row["Id"],
            Username = (string)row["Username"],
            Email = (string)row["Email"],
            Role = (string)row["Role"],
            Balance = (decimal)row["Balance"],
            IsActive = (bool)row["IsActive"],
            CreatedAt = (DateTime)row["CreatedAt"],
        };
    }
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;

    public TransactionService(DatabaseHelper db, EmailService emailService)
    {
        _db = db;
        _emailService = emailService;
    }

    /// <summary>
    /// Transfers funds between two accounts.
    /// </summary>
    public (bool Success, string Message) Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount < 0)
            return (false, "Amount must be positive");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= amount)
        {
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance   = toBalance + amount;

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newFromBalance} WHERE Id = {fromUserId}");
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newToBalance} WHERE Id = {toUserId}");

            RecordTransaction(fromUserId, toUserId, amount, "Transfer", description);

            _emailService.SendTransferNotification(
                (string)fromUserTable.Rows[0]["Email"],
                amount,
                (string)toUserTable.Rows[0]["Username"]);

            return (true, "Transfer successful");
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > 1000000)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.05m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + {amount + interestBonus} WHERE Id = {userId}");

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private bool IsWithinDailyLimit(int userId)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT COUNT(*) AS TxCount FROM Transactions WHERE FromUserId = @Id AND CAST(CreatedAt AS DATE) = CAST(GETDATE() AS DATE)",
            new Dictionary<string, object> { { "@Id", userId } });

        int count = (int)table.Rows[0]["TxCount"];
        return count < MaxTransactionsPerDay;
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        string sql = $@"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES ({fromId}, {toId}, {amount}, '{type}', 'Completed', '{description}', GETDATE())";
        _db.ExecuteNonQuery(sql);
    }

    private string FormatCurrency(decimal amount)
    {
        return $"${amount:F2}";
    }

    public void RefundTransaction(int transactionId)
    TODO: implement
        throw new NotImplementedException();
    }
}
```

### File: SampleBankingApp/Services/UserService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class UserService
{
    private readonly DatabaseHelper _db;

    private static List<string> _auditLog = new();
    private static int _requestCount = 0;

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    public User? GetUserById(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", id } });

        if (table.Rows.Count == 0)
            return null;

        var row = table.Rows[0];
        return MapRowToUser(row);
    }

    public bool UpdateUser(int id, string email, string username)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _auditLog.Add($"UpdateUser called for id={id}, email={email}");

        string sql = $"UPDATE Users SET Email = '{email}', Username = '{username}' WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);
        return true;
    }

    public bool DeleteUser(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        string sql = $"DELETE FROM Users WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = page * pageSize;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users ORDER BY Id OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY",
            new Dictionary<string, object> { { "@Skip", skip }, { "@PageSize", pageSize } });

        var users = new List<User>();
        foreach (System.Data.DataRow row in table.Rows)
            users.Add(MapRowToUser(row));

        return users;
    }

    public string GetAuditReport()
    {
        string report = "";
        foreach (var entry in _auditLog)
        {
            report += entry + "\n";
        }
        return report;
    }

    public List<User> SearchUsers(string query)
    {
        try
        {
            var table = _db.ExecuteQuery("Users", $"Username LIKE '%{query}%'");
            var users = new List<User>();
            foreach (System.Data.DataRow row in table.Rows)
                users.Add(MapRowToUser(row));
            return users;
        }
        catch (Exception)
        {
            return new List<User>();
        }
    }

    private User MapRowToUser(System.Data.DataRow row)
    {
        return new User
        {
            Id = (int)row["Id"],
            Username = (string)row["Username"],
            Email = (string)row["Email"],
            Role = (string)row["Role"],
            Balance = (decimal)row["Balance"],
            IsActive = (bool)row["IsActive"],
            CreatedAt = (DateTime)row["CreatedAt"],
        };
    }
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;

    public TransactionService(DatabaseHelper db, EmailService emailService)
    Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount < 0)
            return (false, "Amount must be positive");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= amount)
        {
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance   = toBalance + amount;

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newFromBalance} WHERE Id = {fromUserId}");
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newToBalance} WHERE Id = {toUserId}");

            RecordTransaction(fromUserId, toUserId, amount, "Transfer", description);

            _emailService.SendTransferNotification(
                (string)fromUserTable.Rows[0]["Email"],
                amount,
                (string)toUserTable.Rows[0]["Username"]);

            return (true, "Transfer successful");
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > 1000000)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.05m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + {amount + interestBonus} WHERE Id = {userId}");

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private bool IsWithinDailyLimit(int userId)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT COUNT(*) AS TxCount FROM Transactions WHERE FromUserId = @Id AND CAST(CreatedAt AS DATE) = CAST(GETDATE() AS DATE)",
            new Dictionary<string, object> { { "@Id", userId } });

        int count = (int)table.Rows[0]["TxCount"];
        return count < MaxTransactionsPerDay;
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        string sql = $@"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES ({fromId}, {toId}, {amount}, '{type}', 'Completed', '{description}', GETDATE())";
        _db.ExecuteNonQuery(sql);
    }

    private string FormatCurrency(decimal amount)
    {
        return $"${amount:F2}";
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}
```

### File: SampleBankingApp/Services/UserService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class UserService
{
    private readonly DatabaseHelper _db;

    private static List<string> _auditLog = new();
    private static int _requestCount = 0;

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    public User? GetUserById(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", id } });

        if (table.Rows.Count == 0)
            return null;

        var row = table.Rows[0];
        return MapRowToUser(row);
    }

    public bool UpdateUser(int id, string email, string username)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _auditLog.Add($"UpdateUser called for id={id}, email={email}");

        string sql = $"UPDATE Users SET Email = '{email}', Username = '{username}' WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);
        return true;
    }

    public bool DeleteUser(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        string sql = $"DELETE FROM Users WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = page * pageSize;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users ORDER BY Id OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY",
            new Dictionary<string, object> { { "@Skip", skip }, { "@PageSize", pageSize } });

        var users = new List<User>();
        foreach (System.Data.DataRow row in table.Rows)
            users.Add(MapRowToUser(row));

        return users;
    }

    public string GetAuditReport()
    {
        string report = "";
        foreach (var entry in _auditLog)
        {
            report += entry + "\n";
        }
        return report;
    }

    public List<User> SearchUsers(string query)
    {
        try
        {
            var table = _db.ExecuteQuery("Users", $"Username LIKE '%{query}%'");
            var users = new List<User>();
            foreach (System.Data.DataRow row in table.Rows)
                users.Add(MapRowToUser(row));
            return users;
        }
        catch (Exception)
        {
            return new List<User>();
        }
    }

    private User MapRowToUser(System.Data.DataRow row)
    {
        return new User
        {
            Id = (int)row["Id"],
            Username = (string)row["Username"],
            Email = (string)row["Email"],
            Role = (string)row["Role"],
            Balance = (decimal)row["Balance"],
            IsActive = (bool)row["IsActive"],
            CreatedAt = (DateTime)row["CreatedAt"],
        };
    }
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;

    public TransactionService(DatabaseHelper db, EmailService emailService)
    Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount < 0)
            return (false, "Amount must be positive");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= amount)
        {
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance   = toBalance + amount;

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newFromBalance} WHERE Id = {fromUserId}");
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newToBalance} WHERE Id = {toUserId}");

            RecordTransaction(fromUserId, toUserId, amount, "Transfer", description);

            _emailService.SendTransferNotification(
                (string)fromUserTable.Rows[0]["Email"],
                amount,
                (string)toUserTable.Rows[0]["Username"]);

            return (true, "Transfer successful");
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > 1000000)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.05m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + {amount + interestBonus} WHERE Id = {userId}");

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private bool IsWithinDailyLimit(int userId)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT COUNT(*) AS TxCount FROM Transactions WHERE FromUserId = @Id AND CAST(CreatedAt AS DATE) = CAST(GETDATE() AS DATE)",
            new Dictionary<string, object> { { "@Id", userId } });

        int count = (int)table.Rows[0]["TxCount"];
        return count < MaxTransactionsPerDay;
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        string sql = $@"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES ({fromId}, {toId}, {amount}, '{type}', 'Completed', '{description}', GETDATE())";
        _db.ExecuteNonQuery(sql);
    }

    private string FormatCurrency(decimal amount)
    {
        return $"${amount:F2}";
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}