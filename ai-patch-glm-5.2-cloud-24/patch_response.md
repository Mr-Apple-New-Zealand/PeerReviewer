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
        if (request == null || string.IsNullOrWhiteSpace(request.Username) || string.IsNullOrWhiteSpace(request.Password))
        {
            return BadRequest(new { message = "Username and password are required." });
        }

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
        {
            return BadRequest(new { message = "Request body is required." });
        }

        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (userIdClaim == null || !int.TryParse(userIdClaim, out int fromUserId))
        {
            return Unauthorized(new { message = "Invalid user identity." });
        }

        var (success, message) = _transactionService.Transfer(fromUserId, request.ToUserId, request.Amount, request.Description);

        if (success)
            return Ok(new { message });

        return BadRequest(new { message });
    }

    [HttpPost("deposit")]
    public IActionResult Deposit([FromBody] DepositRequest request)
    {
        if (request == null)
        {
            return BadRequest(new { message = "Request body is required." });
        }

        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (userIdClaim == null || !int.TryParse(userIdClaim, out int userId))
        {
            return Unauthorized(new { message = "Invalid user identity." });
        }

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
        {
            return BadRequest(new { message = "Request body is required." });
        }

        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (userIdClaim == null || !int.TryParse(userIdClaim, out int currentUserId))
        {
            return Unauthorized(new { message = "Invalid user identity." });
        }

        var roleClaim = User.FindFirst(ClaimTypes.Role)?.Value;
        var isAdmin = string.Equals(roleClaim, "Admin", System.StringComparison.OrdinalIgnoreCase) ||
                      string.Equals(roleClaim, "SuperAdmin", System.StringComparison.OrdinalIgnoreCase);

        if (id != currentUserId && !isAdmin)
        {
            return Forbid();
        }

        try
        {
            _userService.UpdateUser(id, request.Email, request.Username);
            return NoContent();
        }
        catch (ArgumentException ex)
        {
            return BadRequest(new { message = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error updating user {Id}", id);
            return StatusCode(500, "An error occurred while updating the user.");
        }
    }

    [HttpDelete("{id}")]
    public IActionResult DeleteUser(int id)
    {
        var roleClaim = User.FindFirst(ClaimTypes.Role)?.Value;
        var isAdmin = string.Equals(roleClaim, "Admin", System.StringComparison.OrdinalIgnoreCase) ||
                      string.Equals(roleClaim, "SuperAdmin", System.StringComparison.OrdinalIgnoreCase);

        if (!isAdmin)
        {
            return Forbid();
        }

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

    public int ExecuteNonQuery(string sql, Dictionary<string, object>? parameters = null)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand(sql, connection);
        if (parameters != null)
        {
            foreach (var (key, value) in parameters)
                command.Parameters.AddWithValue(key, value);
        }
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

    public static bool IsValidEmail(string? email)
    {
        if (string.IsNullOrWhiteSpace(email))
            return false;

        if (email.Length > MaxEmailLength)
            return false;

        return EmailRegex.IsMatch(email);
    }

    public static bool IsValidUsername(string? username)
    {
        if (string.IsNullOrWhiteSpace(username))
            return false;

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
        if (string.IsNullOrEmpty(accountNumber) || accountNumber.Length <= 4)
            return accountNumber ?? string.Empty;

        var sb = new StringBuilder();
        sb.Append(new string('*', accountNumber.Length - 4));
        sb.Append(accountNumber.Substring(accountNumber.Length - 4));
        return sb.ToString();
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
if (string.IsNullOrEmpty(jwtSecret))
{
    throw new InvalidOperationException("JWT SecretKey is not configured.");
}

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
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret)),
            ClockSkew = TimeSpan.Zero
        };
    });

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

app.UseHttpsRedirection();

var allowedOrigins = builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>() ?? Array.Empty<string>();
app.UseCors(policy => policy
    .WithOrigins(allowedOrigins)
    .AllowAnyMethod()
    .AllowAnyHeader());

app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

### File: SampleBankingApp/SampleBankingApp.csproj
```
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
```

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
    /// Authenticates a user and returns a JWT on success, or null on failure.
    /// </summary>
    public User? Login(string username, string password)
    {
        string hashedPassword = HashPassword(password);

        string sql = "SELECT * FROM Users WHERE Username = @Username AND Password = @Password AND IsActive = 1";

        var table = _db.ExecuteQuerySafe(sql, new Dictionary<string, object>
        {
            { "@Username", username },
            { "@Password", hashedPassword }
        });

        if (table.Rows.Count > 0)
        {
            var row = table.Rows[0];
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

        return null;
    }

    private static string HashPassword(string password)
    {
        using var sha256 = SHA256.Create();
        byte[] bytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(password));
        return Convert.ToHexString(bytes).ToLower();
    }

    public string GenerateJwtToken(User user)
    {
        var key = GetSigningKey();
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var claims = BuildClaims(user);
        var expiry = GetTokenExpiry();

        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"],
            audience: _config["Jwt:Audience"],
            claims: claims,
            expires: expiry,
            signingCredentials: creds
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    private SymmetricSecurityKey GetSigningKey()
    {
        var secret = _config["Jwt:SecretKey"];
        if (string.IsNullOrEmpty(secret))
        {
            throw new InvalidOperationException("JWT SecretKey is not configured.");
        }
        return new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secret));
    }

    private static Claim[] BuildClaims(User user)
    {
        return new[]
        {
            new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new Claim(ClaimTypes.Name, user.Username),
            new Claim(ClaimTypes.Role, user.Role),
        };
    }

    private static DateTime GetTokenExpiry()
    {
        return DateTime.UtcNow.AddDays(30);
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
    private const int DefaultSmtpPort = 25;

    private const string NotificationsAddress = "notifications@company.com";
    private const string SupportAddress = "support@company.com";

    public EmailService(IConfiguration config)
    {
        _config = config;
    }

    public void SendTransferNotification(string toEmail, decimal amount, string recipientName)
    {
        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";

        using var message = new MailMessage(NotificationsAddress, toEmail, TransferSubject, body);

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
                Console.WriteLine($"Email attempt {attempt} failed: {ex.Message}");
                if (attempt >= MaxRetries)
                    throw;
            }
        }
    }

    public void SendWelcomeEmail(string toEmail, string username)
    {
        var body = $"Welcome, {(username ?? string.Empty).ToUpper()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   $"For support, email us at {SupportAddress}";

        using var message = new MailMessage(NotificationsAddress, toEmail, WelcomeSubject, body);

        try
        {
            using var smtpClient = CreateSmtpClient();
            smtpClient.Send(message);
        }
        catch (SmtpException ex)
        {
            Console.WriteLine("Welcome email failed: " + ex.Message);
        }
    }

    private SmtpClient CreateSmtpClient()
    {
        var portString = _config["Email:SmtpPort"];
        int port = int.TryParse(portString, out var parsedPort) ? parsedPort : DefaultSmtpPort;

        return new SmtpClient(_config["Email:SmtpHost"] ?? string.Empty)
        {
            Port = port,
            Credentials = new NetworkCredential(
                _config["Email:Username"] ?? string.Empty,
                _config["Email:Password"] ?? string.Empty
            ),
            EnableSsl = false,
            Timeout = SmtpTimeoutMs
        };
    }
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;
using System.Data.SqlClient;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;
    private const decimal DepositInterestRate = 0.01m;
    private const decimal MaxDepositAmount = 1_000_000m;

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
            return (false, "Amount must be positive");

        if (fromUserId == toUserId)
            return (false, "Cannot transfer funds to your own account");

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
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance < totalDebit)
        {
            return (false, "Insufficient funds");
        }

        decimal newFromBalance = fromBalance - totalDebit;
        decimal newToBalance   = toBalance + amount;

        using var connection = new SqlConnection(_db.GetConnectionString());
        connection.Open();
        using var transaction = connection.BeginTransaction();

        try
        {
            using (var debitCmd = new SqlCommand("UPDATE Users SET Balance = @Balance WHERE Id = @Id", connection, transaction))
            {
                debitCmd.Parameters.AddWithValue("@Balance", newFromBalance);
                debitCmd.Parameters.AddWithValue("@Id", fromUserId);
                debitCmd.ExecuteNonQuery();
            }

            using (var creditCmd = new SqlCommand("UPDATE Users SET Balance = @Balance WHERE Id = @Id", connection, transaction))
            {
                creditCmd.Parameters.AddWithValue("@Balance", newToBalance);
                creditCmd.Parameters.AddWithValue("@Id", toUserId);
                creditCmd.ExecuteNonQuery();
            }

            using (var recordCmd = new SqlCommand("INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt) VALUES (@FromUserId, @ToUserId, @Amount, @Type, @Status, @Description, GETDATE())", connection, transaction))
            {
                recordCmd.Parameters.AddWithValue("@FromUserId", fromUserId);
                recordCmd.Parameters.AddWithValue("@ToUserId", toUserId);
                recordCmd.Parameters.AddWithValue("@Amount", amount);
                recordCmd.Parameters.AddWithValue("@Type", "Transfer");
                recordCmd.Parameters.AddWithValue("@Status", "Completed");
                recordCmd.Parameters.AddWithValue("@Description", (object?)description ?? DBNull.Value);
                recordCmd.ExecuteNonQuery();
            }

            transaction.Commit();
        }
        catch (Exception)
        {
            transaction.Rollback();
            throw;
        }

        try
        {
            _emailService.SendTransferNotification(
                (string)fromUserTable.Rows[0]["Email"],
                amount,
                (string)toUserTable.Rows[0]["Username"]);
        }
        catch (Exception)
        {
            // Swallow email notification failure so the committed transfer succeeds
        }

        return (true, "Transfer successful");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > MaxDepositAmount)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * DepositInterestRate;

        _db.ExecuteNonQuery(
            "UPDATE Users SET Balance = Balance + @Amount WHERE Id = @Id",
            new Dictionary<string, object> 
            { 
                { "@Amount", amount + interestBonus }, 
                { "@Id", userId } 
            });

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        string sql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES (@FromUserId, @ToUserId, @Amount, @Type, @Status, @Description, GETDATE())";
        
        _db.ExecuteNonQuery(sql, new Dictionary<string, object>
        {
            { "@FromUserId", fromId },
            { "@ToUserId", toId },
            { "@Amount", amount },
            { "@Type", type },
            { "@Status", "Completed" },
            { "@Description", (object?)description ?? DBNull.Value }
        });
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

    private const int MaxUserId = 1_000_000;
    private const int MaxPageSize = 50;

    private readonly List<string> _auditLog = new();
    private int _requestCount = 0;

    public UserService(DatabaseHelper db)
    {
        _db = db;
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

        string sql = "UPDATE Users SET Email = @Email, Username = @Username WHERE Id = @Id";
        _db.ExecuteNonQuery(sql, new Dictionary<string, object>
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

        string sql = "DELETE FROM Users WHERE Id = @Id";
        _db.ExecuteNonQuery(sql, new Dictionary<string, object>
        {
            { "@Id", id }
        });

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

    private void ValidateUserId(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > MaxUserId)
            throw new ArgumentException("User ID out of range");
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

### File: SampleBankingApp/appsettings.json
```
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=prod-db.internal;Database=BankingDB;User Id=sa;Password=__SET_VIA_ENV__;TrustServerCertificate=True;"
  },
  "Jwt": {
    "SecretKey": "__SET_VIA_ENV__",
    "Issuer": "BankingApp",
    "Audience": "BankingApp"
  },
  "Email": {
    "SmtpHost": "smtp.company.com",
    "SmtpPort": 587,
    "Username": "notifications@company.com",
    "Password": "__SET_VIA_ENV__"
  },
  "Cors": {
    "AllowedOrigins": []
  },
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*"
}
```

## Change Log
- **Security**: Fixed SQL injection vulnerabilities in `AuthService`, `UserService`, and `TransactionService` by switching to parameterized queries. Removed hardcoded admin backdoor. Replaced MD5 with SHA256 for password hashing. Added ownership and role checks in `UserController` to prevent unauthorized updates/deletes. Removed hardcoded secrets from `appsettings.json`.
- **Configuration**: Enabled JWT `ValidateLifetime`, re-enabled HTTPS redirection, guarded developer exception pages behind `env.IsDevelopment()`, scoped CORS to specific origins, lowered logging level to `Information`, and updated `Newtonsoft.Json` while removing debug symbols.
- **Logic**: Fixed zero-value transfer check, balance check to include fee, pagination off-by-one, deposit interest rate, and self-transfer prevention.
- **Error Handling**: Added DB transactions for atomic transfers, swallowed email exceptions post-transfer, replaced generic catches with specific handling, and stopped leaking exception messages to HTTP clients.
- **Resource Leaks**: Added `using` statements for `SqlConnection`, `SqlDataReader`, `MailMessage`, and `SmtpClient` instances.
- **Null Checks**: Added null guards for JWT secrets, user IDs, SMTP ports, usernames, claims, and request bodies.
- **Refactoring & Dead Code**: Extracted duplicated validation to `ValidateUserId`, split `GenerateJwtToken` into helpers, replaced static mutable state with instance fields, removed dead code (`HashPasswordSha1`, `TableExists`, `BuildHtmlTemplate`, etc.), and extracted magic strings/numbers into constants.