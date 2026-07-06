### File: SampleBankingApp/Services/AuthService.cs
```
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

    public AuthService(DatabaseHelper db, IConfiguration config)
    {
        _db = db;
        _config = config;
    }

    /// <summary>
    /// Authenticates a user and returns a User on success, or null on failure.
    /// </summary>
    public User? Login(string username, string password)
    {
        // Use SHA256 for hashing (still not ideal but far better than MD5)
        string hashedPassword = HashPasswordSha256(password);

        const string sql = @"SELECT Id, Username, Email, Role, Balance, IsActive
                             FROM Users
                             WHERE Username = @Username AND Password = @Password AND IsActive = 1";

        using var connection = new SqlConnection(_config.GetConnectionString("DefaultConnection"));
        connection.Open();

        using var command = new SqlCommand(sql, connection);
        command.Parameters.AddWithValue("@Username", username);
        command.Parameters.AddWithValue("@Password", hashedPassword);

        using var reader = command.ExecuteReader();
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

        // No back‑door admin bypass – authentication must be via DB record only
        return null;
    }

    private static string HashPasswordSha256(string password)
    {
        using var sha256 = SHA256.Create();
        byte[] bytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(password));
        return Convert.ToHexString(bytes).ToLowerInvariant();
    }

    public string GenerateJwtToken(User user)
    {
        var secret = _config["Jwt:SecretKey"];
        if (string.IsNullOrWhiteSpace(secret))
            throw new InvalidOperationException("JWT secret key is not configured.");

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secret));
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

    public bool ValidateToken(string token)
    {
        if (string.IsNullOrWhiteSpace(token))
            return false;

        var handler = new JwtSecurityTokenHandler();
        try
        {
            var jwt = handler.ReadJwtToken(token);
            return jwt.ValidTo > DateTime.UtcNow;
        }
        catch
        {
            return false;
        }
    }
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;
using System.Data;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const decimal DepositInterestRate = 0.01m; // 1% interest on deposits
    private const decimal DepositCap = 1_000_000m;

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
        if (amount <= 0)
            return (false, "Amount must be greater than zero");

        if (fromUserId == toUserId)
            return (false, "Self‑transfer is not allowed");

        // Load both users in a single transaction to guarantee consistency
        using var connection = _db.GetOpenConnection();
        using var transaction = connection.BeginTransaction();

        try
        {
            var fromUser = GetUserById(connection, transaction, fromUserId);
            var toUser = GetUserById(connection, transaction, toUserId);

            if (fromUser == null || toUser == null)
                return (false, "One or both users not found");

            decimal fee = Math.Round(amount * TransactionFeeRate, 2);
            decimal totalDebit = amount + fee;

            if (fromUser.Balance < totalDebit)
                return (false, "Insufficient funds (including transaction fee)");

            // Perform balance updates
            UpdateUserBalance(connection, transaction, fromUserId, fromUser.Balance - totalDebit);
            UpdateUserBalance(connection, transaction, toUserId, toUser.Balance + amount);

            // Record transaction
            RecordTransaction(connection, transaction, fromUserId, toUserId, amount, "Transfer", description);

            transaction.Commit();

            // Send notification – swallow any email errors so the transfer still succeeds
            try
            {
                _emailService.SendTransferNotification(
                    fromUser.Email,
                    amount,
                    toUser.Username);
            }
            catch
            {
                // Log internally if needed; do not surface to caller
            }

            return (true, "Transfer successful");
        }
        catch
        {
            transaction.Rollback();
            return (false, "Transfer failed due to an internal error");
        }
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > DepositCap)
            return (false, "Invalid deposit amount");

        decimal interestBonus = Math.Round(amount * DepositInterestRate, 2);

        using var connection = _db.GetOpenConnection();
        using var transaction = connection.BeginTransaction();

        try
        {
            var user = GetUserById(connection, transaction, userId);
            if (user == null)
                return (false, "User not found");

            UpdateUserBalance(connection, transaction, userId, user.Balance + amount + interestBonus);
            RecordTransaction(connection, transaction, 0, userId, amount, "Deposit", null);

            transaction.Commit();
            return (true, "Deposit successful");
        }
        catch
        {
            transaction.Rollback();
            return (false, "Deposit failed due to an internal error");
        }
    }

    private User? GetUserById(SqlConnection connection, SqlTransaction transaction, int userId)
    {
        const string sql = "SELECT Id, Username, Email, Balance FROM Users WHERE Id = @Id";
        using var cmd = new SqlCommand(sql, connection, transaction);
        cmd.Parameters.AddWithValue("@Id", userId);
        using var reader = cmd.ExecuteReader();
        if (!reader.Read())
            return null;

        return new User
        {
            Id = (int)reader["Id"],
            Username = (string)reader["Username"],
            Email = (string)reader["Email"],
            Balance = (decimal)reader["Balance"]
        };
    }

    private void UpdateUserBalance(SqlConnection connection, SqlTransaction transaction, int userId, decimal newBalance)
    {
        const string sql = "UPDATE Users SET Balance = @Balance WHERE Id = @Id";
        using var cmd = new SqlCommand(sql, connection, transaction);
        cmd.Parameters.AddWithValue("@Balance", newBalance);
        cmd.Parameters.AddWithValue("@Id", userId);
        cmd.ExecuteNonQuery();
    }

    private void RecordTransaction(SqlConnection connection, SqlTransaction transaction,
        int fromId, int toId, decimal amount, string type, string? description)
    {
        const string sql = @"INSERT INTO Transactions
                            (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                            VALUES (@FromId, @ToId, @Amount, @Type, 'Completed', @Description, GETDATE())";

        using var cmd = new SqlCommand(sql, connection, transaction);
        cmd.Parameters.AddWithValue("@FromId", fromId);
        cmd.Parameters.AddWithValue("@ToId", toId);
        cmd.Parameters.AddWithValue("@Amount", amount);
        cmd.Parameters.AddWithValue("@Type", type);
        cmd.Parameters.AddWithValue("@Description", (object?)description ?? DBNull.Value);
        cmd.ExecuteNonQuery();
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
    private readonly List<string> _auditLog = new();
    private int _requestCount = 0;

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    private void ValidateUserId(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1_000_000)
            throw new ArgumentException("User ID out of range");
    }

    public User? GetUserById(int id)
    {
        ValidateUserId(id);
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
        ValidateUserId(id);
        _auditLog.Add($"UpdateUser called for id={id}, email={email}");

        const string sql = @"UPDATE Users SET Email = @Email, Username = @Username WHERE Id = @Id";
        _db.ExecuteNonQuerySafe(sql, new Dictionary<string, object>
        {
            { "@Email", email },
            { "@Username", username },
            { "@Id", id }
        });
        return true;
    }

    public bool DeleteUser(int id)
    {
        ValidateUserId(id);
        _requestCount++;

        const string sql = @"DELETE FROM Users WHERE Id = @Id";
        _db.ExecuteNonQuerySafe(sql, new Dictionary<string, object> { { "@Id", id } });

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        const int MaxPageSize = 50;
        if (pageSize > MaxPageSize) pageSize = MaxPageSize;
        if (page < 1) page = 1;

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
        var sb = new StringBuilder();
        foreach (var entry in _auditLog)
            sb.AppendLine(entry);
        return sb.ToString();
    }

    public List<User> SearchUsers(string query)
    {
        const string sql = @"SELECT * FROM Users WHERE Username LIKE @Pattern";
        var parameters = new Dictionary<string, object>
        {
            { "@Pattern", $"%{query}%" }
        };
        var table = _db.ExecuteQuerySafe(sql, parameters);
        var users = new List<User>();
        foreach (System.Data.DataRow row in table.Rows)
            users.Add(MapRowToUser(row));
        return users;
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

### File: SampleBankingApp/Data/DatabaseHelper.cs
```
using System.Data;
using System.Data.SqlClient;

namespace SampleBankingApp.Data;

/// <summary>
/// Provides raw ADO.NET database access helpers.
/// </summary>
public class DatabaseHelper
{
    private readonly string _connectionString;

    public DatabaseHelper(IConfiguration configuration)
    {
        _connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? "Server=localhost;Database=BankingDB;User Id=sa;Password=Admin1234!;";
    }

    public SqlConnection GetOpenConnection()
    {
        var connection = new SqlConnection(_connectionString);
        connection.Open();
        return connection;
    }

    public DataTable ExecuteQuery(string tableName, string whereClause)
    {
        using var connection = GetOpenConnection();
        using var command = new SqlCommand($"SELECT * FROM {tableName} WHERE {whereClause}", connection);
        using var adapter = new SqlDataAdapter(command);
        var table = new DataTable();
        adapter.Fill(table);
        return table;
    }

    public DataTable ExecuteQuerySafe(string sql, Dictionary<string, object> parameters)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand(sql, connection);
        foreach (var (key, value) in parameters)
            command.Parameters.AddWithValue(key, value);

        using var adapter = new SqlDataAdapter(command);
        var table = new DataTable();
        adapter.Fill(table);
        return table;
    }

    public int ExecuteNonQuery(string sql)
    {
        using var connection = GetOpenConnection();
        using var command = new SqlCommand(sql, connection);
        return command.ExecuteNonQuery();
    }

    public int ExecuteNonQuerySafe(string sql, Dictionary<string, object> parameters)
    {
        using var connection = GetOpenConnection();
        using var command = new SqlCommand(sql, connection);
        foreach (var (key, value) in parameters)
            command.Parameters.AddWithValue(key, value);
        return command.ExecuteNonQuery();
    }
}
```

### File: SampleBankingApp/Helpers/StringHelper.cs
```
using System.Text;
using System.Text.RegularExpressions;

namespace SampleBankingApp.Helpers;

/// <summary>
/// General-purpose string utilities.
/// </summary>
public static class StringHelper
{
    private const int MaxEmailLength = 254;
    private const int MinUsernameLength = 3;
    private const int MaxUsernameLength = 20;

    private static readonly Regex EmailRegex = new(@"^[^@\s]+@[^@\s]+\.[^@\s]+$", RegexOptions.Compiled);
    private static readonly Regex UsernameRegex = new(@"^[a-zA-Z0-9_]+$", RegexOptions.Compiled);

    public static bool IsValidEmail(string email)
    {
        if (email == null) return false;
        if (email.Length > MaxEmailLength) return false;
        return EmailRegex.IsMatch(email);
    }

    public static bool IsValidUsername(string username)
    {
        if (username == null) return false;
        if (username.Length < MinUsernameLength || username.Length > MaxUsernameLength) return false;
        return UsernameRegex.IsMatch(username);
    }

    public static string JoinWithSeparator(IEnumerable<string> items, string separator)
    {
        return string.Join(separator, items);
    }

    public static string MaskAccountNumber(string accountNumber)
    {
        if (accountNumber == null) return string.Empty;
        if (accountNumber.Length <= 4) return accountNumber;

        var sb = new StringBuilder();
        sb.Append(new string('*', accountNumber.Length - 4));
        sb.Append(accountNumber.Substring(accountNumber.Length - 4));
        return sb.ToString();
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
    private const string WelcomeSubject = "Welcome to BankingApp!";

    private const string NotificationEmail = "notifications@company.com";
    private const string SupportEmail = "support@company.com";

    private const int MaxRetries = 3;
    private const int SmtpTimeoutMs = 5000;

    public EmailService(IConfiguration config)
    {
        _config = config;
    }

    public void SendTransferNotification(string toEmail, decimal amount, string recipientName)
    {
        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";

        using var message = new MailMessage(NotificationEmail, toEmail, TransferSubject, body);
        SendWithRetries(message);
    }

    public void SendWelcomeEmail(string toEmail, string username)
    {
        var body = $"Welcome, {username?.ToUpperInvariant()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   $"For support, email us at {SupportEmail}";

        using var message = new MailMessage(NotificationEmail, toEmail, WelcomeSubject, body);
        SendWithRetries(message);
    }

    private void SendWithRetries(MailMessage message)
    {
        int attempt = 0;
        while (attempt < MaxRetries)
        {
            try
            {
                using var smtp = new SmtpClient(_config["Email:SmtpHost"])
                {
                    Port = int.TryParse(_config["Email:SmtpPort"], out var p) ? p : 25,
                    Credentials = new NetworkCredential(
                        _config["Email:Username"],
                        _config["Email:Password"]
                    ),
                    EnableSsl = false,
                    Timeout = SmtpTimeoutMs
                };
                smtp.Send(message);
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
}
```

### File: SampleBankingApp/Program.cs
```
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using SampleBankingApp.Data;
using SampleBankingApp.Services;
using System.Text;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddSingleton<DatabaseHelper>();
builder.Services.AddScoped<UserService>();
builder.Services.AddScoped<AuthService>();
builder.Services.AddScoped<TransactionService>();
builder.Services.AddScoped<EmailService>();

var jwtSecret = builder.Configuration["Jwt:SecretKey"];
if (string.IsNullOrWhiteSpace(jwtSecret))
    throw new InvalidOperationException("JWT secret key must be configured.");

builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true, // enforce token expiration
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret))
        };
    });

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}
else
{
    // In production, use generic error handling
    app.UseExceptionHandler("/error");
    app.UseHsts();
}

// Enforce HTTPS
app.UseHttpsRedirection();

// Restrictive CORS – adjust origins as needed
app.UseCors(policy => policy
    .WithOrigins("https://localhost:5001")
    .AllowAnyMethod()
    .AllowAnyHeader());

app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

### File: SampleBankingApp/appsettings.json
```
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=__SET_VIA_ENV__;Database=BankingDB;User Id=__SET_VIA_ENV__;Password=__SET_VIA_ENV__;TrustServerCertificate=True;"
  },
  "Jwt": {
    "SecretKey": "__SET_VIA_ENV__",
    "Issuer": "BankingApp",
    "Audience": "BankingApp"
  },
  "Email": {
    "SmtpHost": "__SET_VIA_ENV__",
    "SmtpPort": "__SET_VIA_ENV__",
    "Username": "__SET_VIA_ENV__",
    "Password": "__SET_VIA_ENV__"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft": "Warning",
      "System": "Warning"
    }
  },
  "AllowedHosts": "*"
}
```

### File: SampleBankingApp/Controllers/UserController.cs
```
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
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
        if (request == null)
            return BadRequest("Request body is required.");

        var callerId = int.Parse(User.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? "0");
        var callerRole = User.FindFirst(ClaimTypes.Role)?.Value ?? string.Empty;

        if (callerId != id && !callerRole.Equals("Admin", StringComparison.OrdinalIgnoreCase))
            return Forbid();

        try
        {
            _userService.UpdateUser(id, request.Email, request.Username);
            return NoContent();
        }
        catch (ArgumentException ex)
        {
            return BadRequest(ex.Message);
        }
        catch (Exception)
        {
            // Do not expose internal details
            return StatusCode(500, "An internal error occurred.");
        }
    }

    [HttpDelete("{id}")]
    public IActionResult DeleteUser(int id)
    {
        var callerId = int.Parse(User.FindFirst(ClaimTypes.NameIdentifier)?.Value ?? "0");
        var callerRole = User.FindFirst(ClaimTypes.Role)?.Value ?? string.Empty;

        if (callerId != id && !callerRole.Equals("Admin", StringComparison.OrdinalIgnoreCase))
            return Forbid();

        try
        {
            _userService.DeleteUser(id);
            return NoContent();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting user {Id}", id);
            return StatusCode(500, "An error occurred while deleting the user.");
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
```
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
        if (request == null)
            return BadRequest("Request body is required.");

        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (!int.TryParse(userIdClaim, out var fromUserId))
            return Unauthorized();

        var (success, message) = _transactionService.Transfer(fromUserId, request.ToUserId, request.Amount, request.Description);

        if (success)
            return Ok(new { message });

        return BadRequest(new { message });
    }

    [HttpPost("deposit")]
    public IActionResult Deposit([FromBody] DepositRequest request)
    {
        if (request == null)
            return BadRequest("Request body is required.");

        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (!int.TryParse(userIdClaim, out var userId))
            return Unauthorized();

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
    }
}
```

### File: SampleBankingApp/Controllers/AuthController.cs
```
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
        if (request == null)
            return BadRequest("Request body is required.");

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