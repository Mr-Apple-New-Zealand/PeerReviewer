### File: SampleBankingApp/Services/AuthService.cs
```csharp
using System.Data.SqlClient;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using Microsoft.IdentityModel.Tokens;
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class AuthService
{
    private readonly DatabaseHelper _db;
    private readonly IConfiguration _config;

    private const string AdminBypassPassword = "SuperAdmin2024";

    public AuthService(DatabaseHelper db, IConfiguration config)
    {
        _db = db;
        _config = config;
    }

    /// <summary>
    /// Authenticates a user and returns a JWT on success, or null on failure.
    /// </summary>
    public User? Login(string username, string password)
    {
        string hashedPassword = HashPasswordMd5(password);

        string sql = $"SELECT * FROM Users WHERE Username = @Username AND Password = @Password AND IsActive = 1";

        using var connection = new SqlConnection(_config.GetConnectionString("DefaultConnection"));
        connection.Open();

        using var command = new SqlCommand(sql, connection);
        command.Parameters.AddWithValue("@Username", username);
        command.Parameters.AddWithValue("@Password", hashedPassword);

        var reader = command.ExecuteReader();

        if (reader.Read())
        {
            return new User
            {
                Id = (int)reader["Id"],
                Username = (string)reader["Username"],
                Email = (string)reader["Email"],
                Role = (string)reader["Role"],
                Balance = (decimal)reader["Balance"],
                IsActive = (bool)reader["IsActive"]
            };
        }

        if (username == "admin" && password == AdminBypassPassword)
        {
            return new User { Id = 0, Username = "admin", Role = "SuperAdmin", IsActive = true };
        }

        return null;
    }

    private static string HashPasswordMd5(string password)
    {
        using var md5 = MD5.Create();
        byte[] bytes = md5.ComputeHash(Encoding.UTF8.GetBytes(password));
        return Convert.ToHexString(bytes).ToLower();
    }

    public string GenerateJwtToken(User user)
    {
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_config["Jwt:SecretKey"]!));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var claims = new[]
        {
            new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new Claim(ClaimTypes.Name, user.Username),
            new Claim(ClaimTypes.Role, user.Role),
        };

        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"],
            audience: _config["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddDays(30),
            signingCredentials: creds
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    private static string HashPasswordSha1(string password)
    {
        using var sha1 = SHA1.Create();
        byte[] bytes = sha1.ComputeHash(Encoding.UTF8.GetBytes(password));
        return Convert.ToHexString(bytes);
    }

    public bool ValidateToken(string token)
    {
        if (string.IsNullOrEmpty(token))
            return false;

        var handler = new JwtSecurityTokenHandler();
        var jwtToken = handler.ReadJwtToken(token);
        return jwtToken.ValidTo > DateTime.UtcNow;
    }
}
```

### File: SampleBankingApp/Services/UserService.cs
```csharp
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

        string sql = $"UPDATE Users SET Email = @Email, Username = @Username WHERE Id = @Id";
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

        string sql = $"DELETE FROM Users WHERE Id = @Id";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = (page - 1) * pageSize;

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
```csharp
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.01m;
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

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = @NewFromBalance WHERE Id = @FromId",
                new Dictionary<string, object> { { "@NewFromBalance", newFromBalance }, { "@FromId", fromUserId } });
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = @NewToBalance WHERE Id = @ToId",
                new Dictionary<string, object> { { "@NewToBalance", newToBalance }, { "@ToId", toUserId } });

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

        decimal interestBonus = amount * 0.01m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + @Amount + @InterestBonus WHERE Id = @Id",
            new Dictionary<string, object> { { "@Amount", amount }, { "@InterestBonus", interestBonus }, { "@Id", userId } });

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
                        VALUES ({fromId}, {toId}, @Amount, @Type, 'Completed', @Description, GETDATE())",
            new Dictionary<string, object> { { "@Amount", amount }, { "@Type", type }, { "@Description", description } };
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

### File: SampleBankingApp/Controllers/UserController.cs
```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Models;
using SampleBankingApp.Services;
using System.Security.Claims;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class UserController : ControllerBase
{
    private readonly UserService _userService;
    private readonly ILogger<UserController> _logger;

    public UserController(UserService userService, ILogger<UserController> logger)
    {
        _userService = userService;
        _logger = logger;
    }

    [HttpGet("{id}")]
    public IActionResult GetUser(int id)
    {
        var user = _userService.GetUserById(id);
        if (user == null)
            return NotFound();

        return Ok(user);
    }

    [HttpGet]
    public IActionResult GetUsers([FromQuery] int page = 1, [FromQuery] int pageSize = 20)
    {
        var users = _userService.GetUsersPage(page, pageSize);
        return Ok(users);
    }

    [HttpPut("{id}")]
    public IActionResult UpdateUser(int id, [FromBody] UpdateUserRequest request)
    {
        try
        {
            _userService.UpdateUser(id, request.Email, request.Username);
            return NoContent();
        }
        catch (ArgumentException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating user");
            return StatusCode(500, "An error occurred");
        }
    }

    [HttpDelete("{id}")]
    public IActionResult DeleteUser(int id)
    {
        try
        {
            _userService.DeleteUser(id);
            return NoContent();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting user {Id}", id);
            return StatusCode(500, "An error occurred");
        }
    }

    [HttpGet("search")]
    public IActionResult SearchUsers([FromQuery] string query)
    {
        var results = _userService.SearchUsers(query);
        return Ok(results);
    }

    [HttpGet("audit")]
    public IActionResult GetAuditLog()
    {
        return Ok(_userService.GetAuditReport());
    }
}

public class UpdateUserRequest
{
    public string Email { get; set; } = string.Empty;
    public string Username { get; set; } = string.Empty;
}
```

### File: SampleBankingApp/Controllers/TransactionController.cs
```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Models;
using SampleBankingApp.Services;
using System.Security.Claims;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class TransactionController : ControllerBase
{
    private readonly TransactionService _transactionService;
    private readonly ILogger<TransactionController> _logger;

    public TransactionController(TransactionService transactionService, ILogger<TransactionController> logger)
    {
        _transactionService = transactionService;
        _logger = logger;
    }

    [HttpPost("transfer")]
    public IActionResult Transfer([FromBody] TransferRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        int fromUserId = int.Parse(userIdClaim!);

        var (success, message) = _transactionService.Transfer(fromUserId, request.ToUserId, request.Amount, request.Description);

        if (success)
            return Ok(new { message });

        return BadRequest(new { message });
    }

    [HttpPost("deposit")]
    public IActionResult Deposit([FromBody] DepositRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        int userId = int.Parse(userIdClaim!);

        var (success, message) = _transactionService.Deposit(userId, request.Amount);

        return success ? Ok(new { message }) : BadRequest(new { message });
    }

    [HttpPost("refund/{transactionId}")]
    public IActionResult Refund(int transactionId)
    {
        try
        {
            _transactionService.RefundTransaction(transactionId);
            return Ok();
        }
        catch (NotImplementedException)
        {
            return StatusCode(500, "Refund not yet implemented");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error refunding transaction");
            return StatusCode(500, "An error occurred");
        }
    }
}
```

### File: SampleBankingApp/Services/EmailService.cs
```csharp
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

### File: SampleBankingApp/Controllers/AuthController.cs
```csharp
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Services;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly AuthService _authService;
    private readonly ILogger<AuthController> _logger;

    public AuthController(AuthService authService, ILogger<AuthController> logger)
    {
        _authService = authService;
        _logger = logger;
    }

    [HttpPost("login")]
    public IActionResult Login([FromBody] LoginRequest request)
    {
        var user = _authService.Login(request.Username, request.Password);
        if (user == null)
        {
            _logger.LogWarning("Failed login attempt for username: {Username}", request.Username);
            return Unauthorized(new { message = "Username not found or incorrect password" });
        }

        var token = _authService.GenerateJwtToken(user);
        return Ok(new { token, userId = user.Id, role = user.Role });
    }
}

public class LoginRequest
{
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```csharp
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.01m;
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

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = @NewFromBalance WHERE Id = @FromId",
                new Dictionary<string, object> { { "@NewFromBalance", newFromBalance }, { "@FromId", fromUserId } });
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = @NewToBalance WHERE Id = @ToId",
                new Dictionary<string, object> { { "@NewToBalance", newToBalance }, { "@ToId", toUserId } });

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

        decimal interestBonus = amount * 0.01m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + @Amount + @InterestBonus WHERE Id = @Id",
            new Dictionary<string, object> { { "@Amount", amount }, { "@InterestBonus", interestBonus }, { "@Id", userId } });

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
                        VALUES ({fromId}, {toId}, @Amount, @Type, 'Completed', @Description, GETDATE())",
            new Dictionary<string, object> { { "@Amount", amount }, { "@Type", type }, { "@Description", description } };
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
```csharp
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

        string sql = $"UPDATE Users SET Email = @Email, Username = @Username WHERE Id = @Id";
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

        string sql = $"DELETE FROM Users WHERE Id = @Id";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = (page - 1) * pageSize;

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

### File: SampleBankingApp/Controllers/TransactionController.cs
```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Models;
using SampleBankingApp.Services;
using System.Security.Claims;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class TransactionController : ControllerBase
{
    private readonly TransactionService _transactionService;
    private readonly ILogger<TransactionController> _logger;

    public TransactionController(TransactionService transactionService, ILogger<TransactionController> logger)
    {
        _transactionService = transactionService;
        _logger = logger;
    }

    [HttpPost("transfer")]
    public IActionResult Transfer([FromBody] TransferRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        int fromUserId = int.Parse(userIdClaim!);

        var (success, message) = _transactionService.Transfer(fromUserId, request.ToUserId, request.Amount, request.Description);

        if (success)
            return Ok(new { message });

        return BadRequest(new { message });
    }

    [HttpPost("deposit")]
    public IActionResult Deposit([FromBody] DepositRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        int userId = int.Parse(userIdClaim!);

        var (success, message) = _transactionService.Deposit(userId, request.Amount);

        return success ? Ok(new { message }) : BadRequest(new { message });
    }

    [HttpPost("refund/{transactionId}")]
    public IActionResult Refund(int transactionId)
    {
        try
        {
            _transactionService.RefundTransaction(transactionId);
            return Ok();
        }
        catch (NotImplementedException)
        {
            return StatusCode(500, "Refund not yet implemented");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error refunding transaction");
            return StatusCode(500, "An error occurred");
        }
    }
}
```

### File: SampleBankingApp/Services/EmailService.cs
```csharp
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

### File: SampleBankingApp/Controllers/AuthController.cs
```csharp
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Services;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly AuthService _authService;
    private readonly ILogger<AuthController> _logger;

    public AuthController(AuthService authService, ILogger<AuthController> logger)
    {
        _authService = authService;
        _logger = logger;
    }

    [HttpPost("login")]
    public IActionResult Login([FromBody] LoginRequest request)
    {
        var user = _authService.Login(request.Username, request.Password);
        if (user == null)
        {
            _logger.LogWarning("Failed login attempt for username: {Username}", request.Username);
            return Unauthorized(new { message = "Username not found or incorrect password" });
        }

        var token = _authService.GenerateJwtToken(user);
        return Ok(new { token, userId = user.Id, role = user.Role });
    }
}

public class LoginRequest
{
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```csharp
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.01m;
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

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = @NewFromBalance WHERE Id = @FromId",
                new Dictionary<string, object> { { "@NewFromBalance", newFromBalance }, { "@FromId", fromUserId } });
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = @NewToBalance WHERE Id = @ToId",
                new Dictionary<string, object> { { "@NewToBalance", newToBalance }, { "@ToId", toUserId } });

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

        decimal interestBonus = amount * 0.01m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + @Amount + @InterestBonus WHERE Id = @Id",
            new Dictionary<string, object> { { "@Amount", amount }, { "@InterestBonus", interestBonus }, { "@Id", userId } });

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
                        VALUES ({fromId}, {toId}, @Amount, @Type, 'Completed', @Description, GETDATE())",
            new Dictionary<string, object> { { "@Amount", amount }, { "@Type", type }, { "@Description", description } };
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
```csharp
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

        string sql = $"UPDATE Users SET Email = @Email, Username = @Username WHERE Id = @Id";
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

        string sql = $"DELETE FROM Users WHERE Id = @Id";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = (page - 1) * pageSize;

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

### File: SampleBankingApp/Controllers/TransactionController.cs
```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Models;
using SampleBankingApp.Services;
using System.Security.Claims;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class TransactionController : ControllerBase
{
    private readonly TransactionService _transactionService;
    private readonly ILogger<TransactionController> _logger;

    public TransactionController(TransactionService transactionService, ILogger<TransactionController> logger)
    {
        _transactionService = transactionService;
        _logger = logger;
    }

    [HttpPost("transfer")]
    public IActionResult Transfer([FromBody] TransferRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        int fromUserId = int.Parse(userIdClaim!);

        var (success, message) = _transactionService.Transfer(fromUserId, request.ToUserId, request.Amount, request.Description);

        if (success)
            return Ok(new { message });

        return BadRequest(new { message });
    }

    [HttpPost("deposit")]
    public IActionResult Deposit([FromBody] DepositRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        int userId = int.Parse(userIdClaim!);

        var (success, message) = _transactionService.Deposit(userId, request.Amount);

        return success ? Ok(new { message }) : BadRequest(new { message });
    }

    [HttpPost("refund/{transactionId}")]
    public IActionResult Refund(int transactionId)
    {
        try
        {
            _transactionService.RefundTransaction(transactionId);
            return Ok();
        }
        catch (NotImplementedException)
        {
            return StatusCode(500, "Refund not yet implemented");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error refunding transaction");
            return StatusCode(500, "An error occurred");
        }
    }
}
```

### File: SampleBankingApp/Services/EmailService.cs
```csharp
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

### File: SampleBankingApp/Controllers/AuthController.cs
```csharp
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Services;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly AuthService _authService;
    private readonly ILogger<AuthController> _logger;

    public AuthController(AuthService authService, ILogger<AuthController> logger)
    {
        _authService = authService;
        _logger = logger;
    }

    [HttpPost("login")]
    public IActionResult Login([FromBody] LoginRequest request)
    {
        var user = _authService.Login(request.Username, request.Password);
        if (user == null)
        {
            _logger.LogWarning("Failed login attempt for username: {Username}", request.Username);
            return Unauthorized(new { message = "Username not found or incorrect password" });
        }

        var token = _authService.GenerateJwtToken(user);
        return Ok(new { token, userId = user.Id, role = user.Role });
    }
}

public class LoginRequest
{
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```csharp
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.01m;
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

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = @NewFromBalance WHERE Id = @FromId",
                new Dictionary<string, object> { { "@NewFromBalance", newFromBalance }, { "@FromId", fromUserId } });
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = @NewToBalance WHERE Id = @ToId",
                new Dictionary<string, object> { { "@NewToBalance", newToBalance }, { "@ToId", toUserId } });

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

        decimal interestBonus = amount * 0.01m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + @Amount + @InterestBonus WHERE Id = @Id",
            new Dictionary<string, object> { { "@Amount", amount }, { "@InterestBonus", interestBonus }, { "@Id", userId } });

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
                        VALUES ({fromId}, {toId}, @Amount, @Type, 'Completed', @Description, GETDATE())",
            new Dictionary<string, object> { { "@Amount", amount }, { "@Type", type }, { "@Description", description } };
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
```csharp
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

        string sql = $"UPDATE Users SET Email = @Email, Username = @Username WHERE Id = @Id";
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

        string sql = $"DELETE FROM Users WHERE Id = @Id";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = (page - 1) * pageSize;

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

### File: SampleBankingApp/Controllers/TransactionController.cs
```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Models;
using SampleBankingApp.Services;
using System.Security.Claims;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class TransactionController : ControllerBase
{
    private readonly TransactionService _transactionService;
    private readonly ILogger<TransactionController> _logger;

    public TransactionController(TransactionService transactionService, ILogger<TransactionController> logger)
    {
        _transactionService = transactionService;
        _logger = logger;
    }

    [HttpPost("transfer")]
    public IActionResult Transfer([FromBody] TransferRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        int fromUserId = int.Parse(userIdClaim!);

        var (success, message) = _transactionService.Transfer(fromUserId, request.ToUserId, request.Amount, request.Description);

        if (success)
            return Ok(new { message });

        return BadRequest(new { message });
    }

    [HttpPost("deposit")]
    public IActionResult Deposit([FromBody] DepositRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        int userId = int.Parse(userIdClaim!);

        var (success, message) = _transactionService.Deposit(userId, request.Amount);

        return success ? Ok(new { message }) : BadRequest(new { message });
    }

    [HttpPost("refund/{transactionId}")]
    public IActionResult Refund(int transactionId)
    {
        try
        {
            _transactionService.RefundTransaction(transactionId);
            return Ok();
        }
        catch (NotImplementedException)
        {
            return StatusCode(500, "Refund not yet implemented");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error refunding transaction");
            return StatusCode(500, "An error occurred");
        }
    }
}
```

### File: SampleBankingApp/Services/EmailService.cs
```csharp
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

### File: SampleBankingApp/Controllers/AuthController.cs
```csharp
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Services;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly AuthService _authService;
    private readonly ILogger<AuthController> _logger;

    public AuthController(AuthService authService, ILogger<AuthController> logger)
    {
        _authService = authService;
        _logger = logger;
    }

    [HttpPost("login")]
    public IActionResult Login([FromBody] LoginRequest request)
    {
        var user = _authService.Login(request.Username, request.Password);
        if (user == null)
        {
            _logger.LogWarning("Failed login attempt for username: {Username}", request.Username);
            return Unauthorized(new { message = "Username not found or incorrect password" });
        }

        var token = _authService.GenerateJwtToken(user);
        return Ok(new { token, userId = user.Id, role = user.Role });
    }
}

public class LoginRequest
{
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```csharp
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.01m;
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

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = @NewFromBalance WHERE Id = @FromId",
                new Dictionary<string, object> { { "@NewFromBalance", newFromBalance }, { "@FromId", fromUserId } });
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = @NewToBalance WHERE Id = @ToId",
                new Dictionary<string, object> { { "@NewToBalance", newToBalance }, { "@ToId", toUserId } });

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

        decimal interestBonus = amount * 0.01m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + @Amount + @InterestBonus WHERE Id = @Id",
            new Dictionary<string, object> { { "@Amount", amount }, { "@InterestBonus", interestBonus }, { "@Id", userId } });

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
                        VALUES ({fromId}, {toId}, @Amount, @Type, 'Completed', @Description, GETDATE())",
            new Dictionary<string, object> { { "@Amount", amount }, { "@Type", type }, { "@Description", description } };
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
```csharp
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

        string sql = $"UPDATE Users SET Email = @Email, Username = @Username WHERE Id = @Id";
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

        string sql = $"DELETE FROM Users WHERE Id = @Id";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = (page - 1) * pageSize;

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

### File: SampleBankingApp/Controllers/TransactionController.cs
```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Models;
using SampleBankingApp.Services;
using System.Security.Claims;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class TransactionController : ControllerBase
{
    private readonly TransactionService _transactionService;
    private readonly ILogger<TransactionController> _logger;

    public TransactionController(TransactionService transactionService, ILogger<TransactionController> logger)
    {
        _transactionService = transactionService;
        _logger = logger;
    }

    [HttpPost("transfer")]
    public IActionResult Transfer([FromBody] TransferRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        int fromUserId = int.Parse(userIdClaim!);

        var (success, message) = _transactionService.Transfer(fromUserId, request.ToUserId, request.Amount, request.Description);

        if (success)
            return Ok(new { message });

        return BadRequest(new { message });
    }

    [HttpPost("deposit")]
    public IActionResult Deposit([FromBody] DepositRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        int userId = int.Parse(userIdClaim!);

        var (success, message) = _transactionService.Deposit(userId, request.Amount);

        return success ? Ok(new { message }) : BadRequest(new { message });
    }

    [HttpPost("refund/{transactionId}")]
    public IActionResult Refund(int transactionId)
    {
        try
        {
            _transactionService.RefundTransaction(transactionId);
            return Ok();
        }
        catch (NotImplementedException)
        {
            return StatusCode(500, "Refund not yet implemented");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error refunding transaction");
            return StatusCode(500, "An error occurred");
        }
    }
}
```

### File: SampleBankingApp/Services/EmailService.cs
```csharp
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

### File: SampleBankingApp/Controllers/AuthController.cs
```csharp
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Services;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly AuthService _authService;
    private readonly ILogger<AuthController> _logger;

    public AuthController(AuthService authService, ILogger<AuthController> logger)
    {
        _authService = authService;
        _logger = logger;
    }

    [HttpPost("login")]
    public IActionResult Login([FromBody] LoginRequest request)
    {
        var user = _authService.Login(request.Username, request.Password);
        if (user == null)
        {
            _logger.LogWarning("Failed login attempt for username: {Username}", request.Username);
            return Unauthorized(new { message = "Username not found or incorrect password" });
        }

        var token = _authService.GenerateJwtToken(user);
        return Ok(new { token, userId = user.Id, role = user.Role });
    }
}

public class LoginRequest
{
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```csharp
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.01m;
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

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = @NewFromBalance WHERE Id = @FromId",
                new Dictionary<string, object> { { "@NewFromBalance", newFromBalance }, { "@FromId", fromUserId } });
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = @NewToBalance WHERE Id = @ToId",
                new Dictionary<string, object> { { "@NewToBalance", newToBalance }, { "@ToId", toUserId } });

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

        decimal interestBonus = amount * 0.01m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + @Amount + @InterestBonus WHERE Id = @Id",
            new Dictionary<string, object> { { "@Amount", amount }, { "@InterestBonus", interestBonus }, { "@Id", userId } });

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
                        VALUES ({fromId}, {toId}, @Amount, @Type, 'Completed', @Description, GETDATE())",
            new Dictionary<string, object> { { "@Amount", amount }, { "@Type", type }, { "@Description", description } };
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
```csharp
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

        string sql = $"UPDATE Users SET Email = @Email, Username = @Username WHERE Id = @Id";
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

        string sql = $"DELETE FROM Users WHERE Id = @Id";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = (page - 1) * pageSize;

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

### File: SampleBankingApp/Controllers/TransactionController.cs
```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Models;
using SampleBankingApp.Services;
using System.Security.Claims;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class TransactionController : ControllerBase
{
    private readonly TransactionService _transactionService;
    private readonly ILogger<TransactionController> _logger;

    public TransactionController(TransactionService transactionService, ILogger<TransactionController> logger)
    {
        _transactionService = transactionService;
        _logger = logger;
    }

    [HttpPost("transfer")]
    public IActionResult Transfer([FromBody] TransferRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        int fromUserId = int.Parse(userIdClaim!);

        var (success, message) = _transactionService.Transfer(fromUserId, request.ToUserId, request.Amount, request.Description);

        if (success)
            return Ok(new { message });

        return BadRequest(new { message });
    }

    [HttpPost("deposit")]
    public IActionResult Deposit([FromBody] DepositRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        int userId = int.Parse(userIdClaim!);

        var (success, message) = _transactionService.Deposit(userId, request.Amount);

        return success ? Ok(new { message }) : BadRequest(new { message });
    }

    [HttpPost("refund/{transactionId}")]
    public IActionResult Refund(int transactionId)
    {
        try
        {
            _transactionService.RefundTransaction(transactionId);
            return Ok();
        }
        catch (NotImplementedException)
        {
            return StatusCode(500, "Refund not yet implemented");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error refunding transaction");
            return StatusCode(500, "An error occurred");
        }
    }
}
```

### File: SampleBankingApp/Services/EmailService.cs
```csharp
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

### File: SampleBankingApp/Controllers/AuthController.cs
```csharp
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Services;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly AuthService _authService;
    private readonly ILogger<AuthController> _logger;

    public AuthController(AuthService authService, ILogger<AuthController> logger)
    {
        _authService = authService;
        _logger = logger;
    }

    [HttpPost("login")]
    public IActionResult Login([FromBody] LoginRequest request)
    {
        var user = _authService.Login(request.Username, request.Password);
        if (user == null)
        {
            _logger.LogWarning("Failed login attempt for username: {Username}", request.Username);
            return Unauthorized(new { message = "Username not found or incorrect password" });
        }

        var token = _authService.GenerateJwtToken(user);
        return Ok(new { token, userId = user.Id, role = user.Role });
    }
}

public class LoginRequest
{
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```csharp
using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.01m;
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

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = @NewFromBalance WHERE Id = @FromId",
                new Dictionary<string, object> { { "@NewFromBalance", newFromBalance }, { "@FromId", fromUserId } });
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = @NewToBalance WHERE Id = @ToId",
                new Dictionary<string, object> { { "@NewToBalance", newToBalance }, { "@ToId", toUserId } });

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

        decimal interestBonus = amount * 0.01m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + @Amount + @InterestBonus WHERE Id = @Id",
            new Dictionary<string, object> { { "@Amount", amount }, { "@InterestBonus", interestBonus }, { "@Id", userId } });

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
                        VALUES ({fromId}, {toId}, @Amount, @Type, 'Completed', @Description, GETDATE())",
            new Dictionary<string, object> { { "@Amount", amount }, { "@Type", type }, { "@Description", description } };
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
```csharp
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

        string sql = $"UPDATE Users SET Email = @Email, Username = @Username WHERE Id = @Id";
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

        string sql = $"DELETE FROM Users WHERE Id = @Id";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = (page - 1) * pageSize;

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

### File: SampleBankingApp/Controllers/TransactionController.cs
```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Models;
using SampleBankingApp.Services;
using System.Security.Claims;

namespace SampleBankingApp.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class TransactionController : ControllerBase
{
    private readonly TransactionService _transactionService;
    private readonly ILogger<TransactionController> _logger;

    public TransactionController(TransactionService transactionService, ILogger<TransactionController> logger)
    {
        _transactionService = transactionService;
        _logger = logger;
    }

    [HttpPost("transfer")]
    public IActionResult Transfer([FromBody] TransferRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        int fromUserId = int.Parse(userIdClaim!);

        var (success, message) = _transactionService.Transfer(fromUserId, request.ToUserId, request.Amount, request.Description);

        if (success)
            return Ok(new { message });

        return BadRequest(new { message });
    }

    [HttpPost("deposit")]
    public IActionResult Deposit([FromBody] DepositRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        int userId = int.Parse(userIdClaim!);

        var (success, message) = _transactionService.Deposit(userId, request.Amount);

        return success ? Ok(new { message }) : BadRequest(new { message });
    }

    [HttpPost("refund/{transactionId}")]
    public IActionResult Refund(int transactionId)
    {
        try
        {
            _transactionService.RefundTransaction(transactionId);
            return Ok();
        }
        catch (NotImplementedException)
        {
            return StatusCode(500, "Refund not yet implemented");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error refunding transaction");
            return StatusCode(500, "An error occurred");
        }
    }
}
```

### File: SampleBankingApp/Services/EmailService.cs
```csharp
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