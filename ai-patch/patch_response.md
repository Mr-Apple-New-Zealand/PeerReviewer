### File: SampleBankingApp/appsettings.json
{
  "ConnectionStrings": {
    "DefaultConnection": "__SET_VIA_ENV__"
  },
  "Jwt": {
    "SecretKey": "__SET_VIA_ENV__",
    "Issuer": "BankingApp",
    "Audience": "BankingApp"
  },
  "Email": {
    "SmtpHost": "__SET_VIA_ENV__",
    "SmtpPort": 587,
    "Username": "__SET_VIA_ENV__",
    "Password": "__SET_VIA_ENV__",
    "FromAddress": "notifications@company.com",
    "SupportAddress": "support@company.com"
  },
  "Cors": {
    "AllowedOrigins": [ "__SET_VIA_ENV__" ]
  },
  "Transaction": {
    "FeeRate": 0.015,
    "MaxPerDay": 10,
    "MaxDepositAmount": 1000000,
    "DepositBonusRate": 0.01
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
### File: SampleBankingApp/Program.cs
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.IdentityModel.Tokens;
using SampleBankingApp.Data;
using SampleBankingApp.Services;
using System.Text;
using System.Threading.RateLimiting;
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();
builder.Services.AddSingleton<DatabaseHelper>();
builder.Services.AddScoped<UserService>();
builder.Services.AddScoped<AuthService>();
builder.Services.AddScoped<TransactionService>();
builder.Services.AddScoped<EmailService>();
var jwtSecret = builder.Configuration["Jwt:SecretKey"]
    ?? throw new InvalidOperationException("Jwt:SecretKey is not configured.");
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret))
        };
    });
var allowedOrigins = builder.Configuration
    .GetSection("Cors:AllowedOrigins")
    .Get<string[]>() ?? Array.Empty<string>();
builder.Services.AddCors(options =>
{
    options.AddPolicy("BankingPolicy", policy =>
        policy.WithOrigins(allowedOrigins)
              .AllowAnyMethod()
              .AllowAnyHeader());
});
builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("login", limiterOptions =>
    {
        limiterOptions.PermitLimit = 5;
        limiterOptions.Window = TimeSpan.FromMinutes(1);
        limiterOptions.QueueProcessingOrder = QueueProcessingOrder.OldestFirst;
        limiterOptions.QueueLimit = 0;
    });
    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
});
var app = builder.Build();
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}
app.UseHttpsRedirection();
app.UseRateLimiter();
app.UseCors("BankingPolicy");
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.Run();
### File: SampleBankingApp/SampleBankingApp.csproj
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>false</TreatWarningsAsErrors>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="8.0.0" />
    <PackageReference Include="System.Data.SqlClient" Version="4.8.6" />
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
    <PackageReference Include="System.IdentityModel.Tokens.Jwt" Version="7.0.0" />
  </ItemGroup>
</Project>
### File: SampleBankingApp/Controllers/AuthController.cs
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;
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
    [EnableRateLimiting("login")]
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
### File: SampleBankingApp/Controllers/TransactionController.cs
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
        if (!int.TryParse(User.FindFirst(ClaimTypes.NameIdentifier)?.Value, out int fromUserId))
            return Unauthorized();
        if (fromUserId == request.ToUserId)
            return BadRequest(new { message = "Cannot transfer to yourself" });
        var (success, message) = _transactionService.Transfer(fromUserId, request.ToUserId, request.Amount, request.Description);
        if (success)
            return Ok(new { message });
        return BadRequest(new { message });
    }
    [HttpPost("deposit")]
    public IActionResult Deposit([FromBody] DepositRequest request)
    {
        if (!int.TryParse(User.FindFirst(ClaimTypes.NameIdentifier)?.Value, out int userId))
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
### File: SampleBankingApp/Controllers/UserController.cs
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
    public IActionResult UpdateUser(int id, [FromBody] UpdateUserRequest? request)
    {
        if (request == null)
            return BadRequest();
        if (!int.TryParse(User.FindFirst(ClaimTypes.NameIdentifier)?.Value, out int callerId))
            return Unauthorized();
        var callerRole = User.FindFirst(ClaimTypes.Role)?.Value;
        if (callerId != id && callerRole != "Admin")
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
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating user {Id}", id);
            return StatusCode(500, "An error occurred");
        }
    }
    [HttpDelete("{id}")]
    [Authorize(Roles = "Admin")]
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
### File: SampleBankingApp/Data/DatabaseHelper.cs
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
            ?? throw new InvalidOperationException("DefaultConnection is not configured.");
    }
    /// <summary>
    /// Executes a SELECT query with a raw WHERE clause. The tableName and whereClause
    /// must come from trusted internal sources — never from user input.
    /// </summary>
    public DataTable ExecuteQuery(string tableName, string whereClause)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand($"SELECT * FROM {tableName} WHERE {whereClause}", connection);
        var adapter = new SqlDataAdapter(command);
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
        var adapter = new SqlDataAdapter(command);
        var table = new DataTable();
        adapter.Fill(table);
        return table;
    }
    public int ExecuteNonQuery(string sql, Dictionary<string, object?>? parameters = null)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand(sql, connection);
        if (parameters != null)
            foreach (var (key, value) in parameters)
                command.Parameters.AddWithValue(key, value ?? DBNull.Value);
        return command.ExecuteNonQuery();
    }
    /// <summary>
    /// Executes multiple SQL statements inside a single database transaction.
    /// Rolls back all statements if any one fails.
    /// </summary>
    public void ExecuteNonQueryBatch(IEnumerable<(string Sql, Dictionary<string, object?>? Parameters)> commands)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var transaction = connection.BeginTransaction();
        try
        {
            foreach (var (sql, parameters) in commands)
            {
                using var command = new SqlCommand(sql, connection, transaction);
                if (parameters != null)
                    foreach (var (key, value) in parameters)
                        command.Parameters.AddWithValue(key, value ?? DBNull.Value);
                command.ExecuteNonQuery();
            }
            transaction.Commit();
        }
        catch
        {
            transaction.Rollback();
            throw;
        }
    }
}
### File: SampleBankingApp/Helpers/StringHelper.cs
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
    private static readonly Regex EmailRegex =
        new(@"^[^@\s]+@[^@\s]+\.[^@\s]+$", RegexOptions.Compiled);
    private static readonly Regex UsernameRegex =
        new(@"^[a-zA-Z0-9_]+$", RegexOptions.Compiled);
    public static bool IsValidEmail(string? email)
    {
        if (email == null) return false;
        if (email.Length > MaxEmailLength) return false;
        return EmailRegex.IsMatch(email);
    }
    public static bool IsValidUsername(string? username)
    {
        if (username == null) return false;
        if (username.Length < MinUsernameLength || username.Length > MaxUsernameLength)
            return false;
        return UsernameRegex.IsMatch(username);
    }
    public static string JoinWithSeparator(IEnumerable<string> items, string separator)
    {
        return string.Join(separator, items);
    }
    public static string MaskAccountNumber(string accountNumber)
    {
        if (accountNumber.Length <= 4)
            return accountNumber;
        var sb = new StringBuilder();
        sb.Append(new string('*', accountNumber.Length - 4));
        sb.Append(accountNumber.Substring(accountNumber.Length - 4));
        return sb.ToString();
    }
}
### File: SampleBankingApp/Services/AuthService.cs
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
    public User? Login(string username, string password)
    {
        const string sql = "SELECT * FROM Users WHERE Username = @Username AND IsActive = 1";
        var table = _db.ExecuteQuerySafe(sql, new Dictionary<string, object> { { "@Username", username } });
        if (table.Rows.Count == 0)
            return null;
        var row = table.Rows[0];
        var storedHash = (string)row["Password"];
        if (!VerifyPassword(password, username, storedHash))
            return null;
        return new User
        {
            Id = (int)row["Id"],
            Username = (string)row["Username"],
            Email = (string)row["Email"],
            Role = (string)row["Role"],
            Balance = (decimal)row["Balance"],
            IsActive = (bool)row["IsActive"]
        };
    }
    /// <summary>
    /// Hashes a password using SHA-256 with the username as a per-user salt.
    /// </summary>
    private static string HashPassword(string password, string username)
    {
        using var sha256 = SHA256.Create();
        var saltedInput = $"{username.ToLowerInvariant()}:{password}";
        byte[] bytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(saltedInput));
        return Convert.ToHexString(bytes).ToLower();
    }
    private static bool VerifyPassword(string inputPassword, string username, string storedHash)
    {
        var computed = HashPassword(inputPassword, username);
        return string.Equals(computed, storedHash, StringComparison.OrdinalIgnoreCase);
    }
    public string GenerateJwtToken(User user)
    {
        var secretKey = _config["Jwt:SecretKey"]
            ?? throw new InvalidOperationException("Jwt:SecretKey is not configured.");
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);
        var claims = BuildClaims(user);
        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"],
            audience: _config["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddHours(8),
            signingCredentials: creds
        );
        return new JwtSecurityTokenHandler().WriteToken(token);
    }
    private static IEnumerable<Claim> BuildClaims(User user) =>
    [
        new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
        new Claim(ClaimTypes.Name, user.Username),
        new Claim(ClaimTypes.Role, user.Role),
    ];
    public bool ValidateToken(string token)
    {
        if (string.IsNullOrEmpty(token))
            return false;
        var handler = new JwtSecurityTokenHandler();
        var jwtToken = handler.ReadJwtToken(token);
        return jwtToken.ValidTo > DateTime.UtcNow;
    }
}
### File: SampleBankingApp/Services/EmailService.cs
using System.Net;
using System.Net.Mail;
namespace SampleBankingApp.Services;
public class EmailService
{
    private readonly IConfiguration _config;
    private readonly ILogger<EmailService> _logger;
    private const string TransferSubject = "Transfer Notification - BankingApp";
    private const string WelcomeSubject = "Welcome to BankingApp!";
    private const int MaxRetries = 3;
    private const int SmtpTimeoutMs = 5000;
    public EmailService(IConfiguration config, ILogger<EmailService> logger)
    {
        _config = config;
        _logger = logger;
    }
    public void SendTransferNotification(string toEmail, decimal amount, string recipientName)
    {
        var fromAddress = _config["Email:FromAddress"] ?? "notifications@company.com";
        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";
        using var message = new MailMessage(
            from: fromAddress,
            to: toEmail,
            subject: TransferSubject,
            body: body);
        int attempt = 0;
        while (attempt < MaxRetries)
        {
            try
            {
                using var smtpClient = CreateSmtpClient();
                smtpClient.Send(message);
                return;
            }
            catch (SmtpException ex)
            {
                attempt++;
                _logger.LogWarning(ex, "Transfer notification attempt {Attempt} of {Max} failed", attempt, MaxRetries);
                if (attempt >= MaxRetries)
                    throw;
            }
        }
    }
    public void SendWelcomeEmail(string toEmail, string username)
    {
        if (username == null) throw new ArgumentNullException(nameof(username));
        var fromAddress = _config["Email:FromAddress"] ?? "notifications@company.com";
        var supportAddress = _config["Email:SupportAddress"] ?? "support@company.com";
        var body = $"Welcome, {username.ToUpper()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   $"For support, email us at {supportAddress}";
        using var message = new MailMessage(fromAddress, toEmail, WelcomeSubject, body);
        try
        {
            using var smtpClient = CreateSmtpClient();
            smtpClient.Send(message);
        }
        catch (SmtpException ex)
        {
            _logger.LogError(ex, "Failed to send welcome email to {Email}", toEmail);
        }
    }
    private SmtpClient CreateSmtpClient()
    {
        return new SmtpClient(_config["Email:SmtpHost"])
        {
            Port = int.Parse(_config["Email:SmtpPort"] ?? "587"),
            Credentials = new NetworkCredential(
                _config["Email:Username"],
                _config["Email:Password"]),
            EnableSsl = true,
            Timeout = SmtpTimeoutMs
        };
    }
}
### File: SampleBankingApp/Services/TransactionService.cs
using System.Data;
using SampleBankingApp.Data;
using SampleBankingApp.Models;
namespace SampleBankingApp.Services;
public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;
    private readonly ILogger<TransactionService> _logger;
    private readonly decimal _transactionFeeRate;
    private readonly int _maxTransactionsPerDay;
    private readonly decimal _maxDepositAmount;
    private readonly decimal _depositBonusRate;
    public TransactionService(
        DatabaseHelper db,
        EmailService emailService,
        IConfiguration config,
        ILogger<TransactionService> logger)
    {
        _db = db;
        _emailService = emailService;
        _logger = logger;
        _transactionFeeRate = config.GetValue<decimal>("Transaction:FeeRate", 0.015m);
        _maxTransactionsPerDay = config.GetValue<int>("Transaction:MaxPerDay", 10);
        _maxDepositAmount = config.GetValue<decimal>("Transaction:MaxDepositAmount", 1_000_000m);
        _depositBonusRate = config.GetValue<decimal>("Transaction:DepositBonusRate", 0.01m);
    }
    public (bool Success, string Message) Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount <= 0)
            return (false, "Amount must be positive");
        if (!IsWithinDailyLimit(fromUserId))
            return (false, "Daily transaction limit reached");
        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });
        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });
        if (fromUserTable.Rows.Count == 0)
            return (false, "Sender account not found");
        if (toUserTable.Rows.Count == 0)
            return (false, "Recipient account not found");
        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance = (decimal)toUserTable.Rows[0]["Balance"];
        decimal fee = Math.Round(amount * _transactionFeeRate, 2);
        decimal totalDebit = amount + fee;
        if (fromBalance < totalDebit)
            return (false, "Insufficient funds");
        decimal newFromBalance = fromBalance - totalDebit;
        decimal newToBalance = toBalance + amount;
        const string insertSql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                                   VALUES (@FromUserId, @ToUserId, @Amount, @Type, 'Completed', @Description, GETDATE())";
        var batchCommands = new List<(string Sql, Dictionary<string, object?>? Parameters)>
        {
            (
                "UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                new Dictionary<string, object?> { { "@Balance", newFromBalance }, { "@Id", fromUserId } }
            ),
            (
                "UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                new Dictionary<string, object?> { { "@Balance", newToBalance }, { "@Id", toUserId } }
            ),
            (
                insertSql,
                new Dictionary<string, object?>
                {
                    { "@FromUserId", fromUserId },
                    { "@ToUserId", toUserId },
                    { "@Amount", amount },
                    { "@Type", "Transfer" },
                    { "@Description", (object?)description ?? DBNull.Value }
                }
            )
        };
        _db.ExecuteNonQueryBatch(batchCommands);
        try
        {
            _emailService.SendTransferNotification(
                (string)fromUserTable.Rows[0]["Email"],
                amount,
                (string)toUserTable.Rows[0]["Username"]);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Transfer notification failed for user {UserId}; transfer itself succeeded", fromUserId);
        }
        return (true, "Transfer successful");
    }
    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > _maxDepositAmount)
            return (false, "Invalid deposit amount");
        decimal interestBonus = Math.Round(amount * _depositBonusRate, 2);
        _db.ExecuteNonQuery(
            "UPDATE Users SET Balance = Balance + @Amount WHERE Id = @UserId",
            new Dictionary<string, object?> { { "@Amount", amount + interestBonus }, { "@UserId", userId } });
        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }
    private bool IsWithinDailyLimit(int userId)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT COUNT(*) AS TxCount FROM Transactions WHERE FromUserId = @Id AND CAST(CreatedAt AS DATE) = CAST(GETDATE() AS DATE)",
            new Dictionary<string, object> { { "@Id", userId } });
        int count = (int)table.Rows[0]["TxCount"];
        return count < _maxTransactionsPerDay;
    }
    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        const string sql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                              VALUES (@FromUserId, @ToUserId, @Amount, @Type, 'Completed', @Description, GETDATE())";
        _db.ExecuteNonQuery(sql, new Dictionary<string, object?>
        {
            { "@FromUserId", fromId },
            { "@ToUserId", toId },
            { "@Amount", amount },
            { "@Type", type },
            { "@Description", (object?)description ?? DBNull.Value }
        });
    }
    public void RefundTransaction(int transactionId)
    {
        throw new NotImplementedException();
    }
}
### File: SampleBankingApp/Services/UserService.cs
using SampleBankingApp.Data;
using SampleBankingApp.Models;
namespace SampleBankingApp.Services;
public class UserService
{
    private readonly DatabaseHelper _db;
    private readonly ILogger<UserService> _logger;
    private const int MaxUserId = 1_000_000;
    private const int MaxPageSize = 50;
    private readonly List<string> _auditLog = new();
    public UserService(DatabaseHelper db, ILogger<UserService> logger)
    {
        _db = db;
        _logger = logger;
    }
    public User? GetUserById(int id)
    {
        ValidateUserId(id);
        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", id } });
        if (table.Rows.Count == 0)
            return null;
        return MapRowToUser(table.Rows[0]);
    }
    public bool UpdateUser(int id, string email, string username)
    {
        ValidateUserId(id);
        _auditLog.Add($"UpdateUser called for id={id}, email={email}");
        _db.ExecuteNonQuery(
            "UPDATE Users SET Email = @Email, Username = @Username WHERE Id = @Id",
            new Dictionary<string, object?> { { "@Email", email }, { "@Username", username }, { "@Id", id } });
        return true;
    }
    public bool DeleteUser(int id)
    {
        ValidateUserId(id);
        _db.ExecuteNonQuery(
            "DELETE FROM Users WHERE Id = @Id",
            new Dictionary<string, object?> { { "@Id", id } });
        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }
    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > MaxPageSize) pageSize = MaxPageSize;
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
        return string.Join("\n", _auditLog);
    }
    public List<User> SearchUsers(string query)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Username LIKE @Query",
            new Dictionary<string, object> { { "@Query", $"%{query}%" } });
        var users = new List<User>();
        foreach (System.Data.DataRow row in table.Rows)
            users.Add(MapRowToUser(row));
        return users;
    }
    private static void ValidateUserId(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > MaxUserId)
            throw new ArgumentException("User ID out of range");
    }
    private static User MapRowToUser(System.Data.DataRow row)
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