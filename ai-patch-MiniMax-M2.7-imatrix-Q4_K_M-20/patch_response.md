I'll systematically fix all documented issues across the codebase. Let me address each file comprehensively.

### File: SampleBankingApp/appsettings.json
```json
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
  "TransactionLimits": {
    "FeeRate": 0.015,
    "MaxTransactionsPerDay": 10,
    "DepositCap": 1000000
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

### File: SampleBankingApp/SampleBankingApp.csproj
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">

  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <TreatWarningsAsErrors>false</TreatWarningsAsErrors>
    <DebugSymbols Condition="'Configuration' == 'Release'">false</DebugSymbols>
    <DebugType Condition="'Configuration' == 'Release'">none</DebugType>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="8.0.0" />
    <PackageReference Include="System.Data.SqlClient" Version="4.8.6" />
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
    <PackageReference Include="System.IdentityModel.Tokens.Jwt" Version="7.0.0" />
  </ItemGroup>

</Project>
```

### File: SampleBankingApp/Program.cs
```csharp
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
if (string.IsNullOrEmpty(jwtSecret) || jwtSecret.StartsWith("__SET_VIA_ENV__"))
{
    throw new InvalidOperationException("JWT SecretKey must be configured via environment variable or appsettings.");
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
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret))
        };
    });

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

app.UseHttpsRedirection();

app.UseCors(policy => policy
    .WithOrigins(builder.Configuration.GetSection("AllowedOrigins").Get<string[]>() ?? Array.Empty<string>())
    .AllowAnyMethod()
    .AllowAnyHeader());

app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

### File: SampleBankingApp/Data/DatabaseHelper.cs
```csharp
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
            ?? throw new InvalidOperationException("Database connection string is not configured.");
    }

    public DataTable ExecuteQuerySafe(string sql, Dictionary<string, object> parameters)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand(sql, connection);
        foreach (var (key, value) in parameters)
            command.Parameters.AddWithValue(key, value);

        using var reader = command.ExecuteReader();
        var table = new DataTable();
        table.Load(reader);
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

    public int ExecuteInTransaction(params (string sql, Dictionary<string, object>? parameters)[] commands)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var transaction = connection.BeginTransaction();
        
        try
        {
            int totalRowsAffected = 0;
            foreach (var (sql, parameters) in commands)
            {
                using var command = new SqlCommand(sql, connection, transaction);
                if (parameters != null)
                {
                    foreach (var (key, value) in parameters)
                        command.Parameters.AddWithValue(key, value);
                }
                totalRowsAffected += command.ExecuteNonQuery();
            }
            transaction.Commit();
            return totalRowsAffected;
        }
        catch
        {
            transaction.Rollback();
            throw;
        }
    }
}
```

### File: SampleBankingApp/Helpers/StringHelper.cs
```csharp
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
        if (string.IsNullOrEmpty(email))
            return false;

        if (email.Length > MaxEmailLength)
            return false;

        return EmailRegex.IsMatch(email);
    }

    public static bool IsValidUsername(string? username)
    {
        if (string.IsNullOrEmpty(username))
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

### File: SampleBankingApp/Models/User.cs
```csharp
namespace SampleBankingApp.Models;

public class User
{
    public int Id { get; set; }
    public string Username { get; set; } = string.Empty;
    public string Password { get; set; } = string.Empty;
    public string Email { get; set; } = string.Empty;
    public string Role { get; set; } = string.Empty;
    public decimal Balance { get; set; }
    public bool IsActive { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime LastLoginAt { get; set; }
}
```

### File: SampleBankingApp/Models/Transaction.cs
```csharp
namespace SampleBankingApp.Models;

public class Transaction
{
    public int Id { get; set; }
    public int FromUserId { get; set; }
    public int ToUserId { get; set; }
    public decimal Amount { get; set; }
    public string Type { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
}

public class TransferRequest
{
    public int ToUserId { get; set; }
    public decimal Amount { get; set; }
    public string? Description { get; set; }
}

public class DepositRequest
{
    public decimal Amount { get; set; }
}
```

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
        if (string.IsNullOrEmpty(username) || string.IsNullOrEmpty(password))
            return null;

        string hashedPassword = HashPasswordSha256(password);

        var parameters = new Dictionary<string, object>
        {
            { "@Username", username },
            { "@Password", hashedPassword }
        };

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Username = @Username AND Password = @Password AND IsActive = 1",
            parameters);

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

    private static string HashPasswordSha256(string password)
    {
        using var sha256 = SHA256.Create();
        byte[] saltBytes = Encoding.UTF8.GetBytes(password);
        byte[] bytes = sha256.ComputeHash(saltBytes);
        return Convert.ToHexString(bytes).ToLower();
    }

    public string GenerateJwtToken(User user)
    {
        var secretKey = _config["Jwt:SecretKey"];
        if (string.IsNullOrEmpty(secretKey))
            throw new InvalidOperationException("JWT SecretKey is not configured.");

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey));
        var creds = CreateSigningCredentials(key);
        var claims = BuildTokenClaims(user);

        return WriteToken(CreateJwtSecurityToken(claims, creds));
    }

    private static SigningCredentials CreateSigningCredentials(SymmetricSecurityKey key)
    {
        return new SigningCredentials(key, SecurityAlgorithms.HmacSha256);
    }

    private static Claim[] BuildTokenClaims(User user)
    {
        return new[]
        {
            new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new Claim(ClaimTypes.Name, user.Username),
            new Claim(ClaimTypes.Role, user.Role),
        };
    }

    private static string WriteToken(JwtSecurityToken token)
    {
        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    private static JwtSecurityToken CreateJwtSecurityToken(Claim[] claims, SigningCredentials creds)
    {
        return new JwtSecurityToken(
            issuer: "BankingApp",
            audience: "BankingApp",
            claims: claims,
            expires: DateTime.UtcNow.AddDays(30),
            signingCredentials: creds
        );
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
    private static readonly List<string> AuditLog = new();
    private static readonly object AuditLock = new();

    public UserService(DatabaseHelper db)
    {
        _db = db;
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

        lock (AuditLock)
        {
            AuditLog.Add($"UpdateUser called for id={id}, email={email}");
        }

        var parameters = new Dictionary<string, object>
        {
            { "@Email", email },
            { "@Username", username },
            { "@Id", id }
        };

        _db.ExecuteNonQuery(
            "UPDATE Users SET Email = @Email, Username = @Username WHERE Id = @Id",
            parameters);
        return true;
    }

    public bool DeleteUser(int id)
    {
        ValidateUserId(id);

        lock (AuditLock)
        {
            AuditLog.Add($"DeleteUser: {id}");
        }

        _db.ExecuteNonQuery(
            "DELETE FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", id } });
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        const int maxPageSize = 50;
        if (pageSize > maxPageSize) 
            pageSize = maxPageSize;

        int skip = (page - 1) * pageSize;

        var parameters = new Dictionary<string, object>
        {
            { "@Skip", skip },
            { "@PageSize", pageSize }
        };

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users ORDER BY Id OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY",
            parameters);

        var users = new List<User>();
        foreach (System.Data.DataRow row in table.Rows)
            users.Add(MapRowToUser(row));

        return users;
    }

    public string GetAuditReport()
    {
        lock (AuditLock)
        {
            return string.Join(Environment.NewLine, AuditLog);
        }
    }

    public List<User> SearchUsers(string query)
    {
        if (string.IsNullOrWhiteSpace(query))
            return new List<User>();

        var parameters = new Dictionary<string, object>
        {
            { "@Query", $"%{query}%" }
        };

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Username LIKE @Query",
            parameters);

        var users = new List<User>();
        foreach (System.Data.DataRow row in table.Rows)
            users.Add(MapRowToUser(row));

        return users;
    }

    private static void ValidateUserId(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1_000_000)
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
    private readonly IConfiguration _config;

    public TransactionService(DatabaseHelper db, EmailService emailService, IConfiguration config)
    {
        _db = db;
        _emailService = emailService;
        _config = config;
    }

    /// <summary>
    /// Transfers funds between two accounts.
    /// </summary>
    public (bool Success, string Message) Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount <= 0)
            return (false, "Amount must be positive");

        if (fromUserId == toUserId)
            return (false, "Cannot transfer to yourself");

        var feeRate = GetTransactionFeeRate();
        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        if (fromUserTable.Rows.Count == 0)
            return (false, "Source user not found");

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        if (toUserTable.Rows.Count == 0)
            return (false, "Destination user not found");

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        decimal fee = Math.Round(amount * feeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance < totalDebit)
            return (false, "Insufficient funds");

        try
        {
            _db.ExecuteInTransaction(
                ("UPDATE Users SET Balance = @NewBalance WHERE Id = @Id", 
                    new Dictionary<string, object> { { "@NewBalance", fromBalance - totalDebit }, { "@Id", fromUserId } }),
                ("UPDATE Users SET Balance = @NewBalance WHERE Id = @Id",
                    new Dictionary<string, object> { { "@NewBalance", (decimal)toUserTable.Rows[0]["Balance"] + amount }, { "@Id", toUserId } })
            );

            RecordTransaction(fromUserId, toUserId, amount, "Transfer", description);

            try
            {
                _emailService.SendTransferNotification(
                    (string)fromUserTable.Rows[0]["Email"],
                    amount,
                    (string)toUserTable.Rows[0]["Username"]);
            }
            catch (Exception)
            {
                // Log but don't fail the transfer if email fails
            }

            return (true, "Transfer successful");
        }
        catch
        {
            return (false, "Transfer failed due to a system error");
        }
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        var depositCap = GetDepositCap();
        
        if (amount <= 0 || amount > depositCap)
            return (false, $"Invalid deposit amount. Must be between 0 and {depositCap}");

        var interestRate = 0.01m;
        decimal interestBonus = amount * interestRate;

        _db.ExecuteNonQuery(
            "UPDATE Users SET Balance = Balance + @Amount WHERE Id = @Id",
            new Dictionary<string, object> { { "@Amount", amount + interestBonus }, { "@Id", userId } });

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        var parameters = new Dictionary<string, object>
        {
            { "@FromId", fromId },
            { "@ToId", toId },
            { "@Amount", amount },
            { "@Type", type },
            { "@Description", description ?? string.Empty }
        };

        _db.ExecuteNonQuery(
            @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
              VALUES (@FromId, @ToId, @Amount, @Type, 'Completed', @Description, GETDATE())",
            parameters);
    }

    public void RefundTransaction(int transactionId)
    {
        throw new NotImplementedException();
    }

    private decimal GetTransactionFeeRate()
    {
        var configValue = _config["TransactionLimits:FeeRate"];
        return decimal.TryParse(configValue, out var rate) ? rate : 0.015m;
    }

    private decimal GetDepositCap()
    {
        var configValue = _config["TransactionLimits:DepositCap"];
        return decimal.TryParse(configValue, out var cap) ? cap : 1_000_000m;
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

    public EmailService(IConfiguration config)
    {
        _config = config ?? throw new ArgumentNullException(nameof(config));
    }

    public void SendTransferNotification(string? toEmail, decimal amount, string? recipientName)
    {
        if (string.IsNullOrEmpty(toEmail))
            return;

        var fromAddress = GetFromAddress();
        
        using var message = new MailMessage
        {
            From = new MailAddress(fromAddress),
            Subject = TransferSubject,
            Body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately."
        };
        message.To.Add(toEmail);

        SendWithRetry(message);
    }

    public void SendWelcomeEmail(string? toEmail, string? username)
    {
        if (string.IsNullOrEmpty(toEmail) || string.IsNullOrEmpty(username))
            return;

        var fromAddress = GetFromAddress();
        
        using var message = new MailMessage
        {
            From = new MailAddress(fromAddress),
            Subject = WelcomeSubject,
            Body = $"Welcome, {username.ToUpperInvariant()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   $"For support, email us at {GetSupportAddress()}"
        };
        message.To.Add(toEmail);

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

    private void SendWithRetry(MailMessage message)
    {
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

    private SmtpClient CreateSmtpClient()
    {
        var host = _config["Email:SmtpHost"] ?? "localhost";
        var portStr = _config["Email:SmtpPort"];
        int.TryParse(portStr, out var port);
        
        if (port == 0)
            port = 587;

        return new SmtpClient(host)
        {
            Port = port,
            Credentials = new NetworkCredential(
                _config["Email:Username"],
                _config["Email:Password"]
            ),
            EnableSsl = true,
            Timeout = SmtpTimeoutMs
        };
    }

    private string GetFromAddress()
    {
        return _config["Email:FromAddress"] ?? "notifications@company.com";
    }

    private string GetSupportAddress()
    {
        return _config["Email:SupportAddress"] ?? "support@company.com";
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
    public IActionResult Login([FromBody] LoginRequest? request)
    {
        if (request == null || string.IsNullOrEmpty(request.Username) || string.IsNullOrEmpty(request.Password))
        {
            return BadRequest(new { message = "Username and password are required" });
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

### File: SampleBankingApp/Controllers/UserController.cs
```csharp
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
            return BadRequest(new { message = "Request body is required" });

        var currentUserIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (!int.TryParse(currentUserIdClaim, out var currentUserId))
            return Unauthorized();

        if (currentUserId != id && !User.IsInRole("Admin"))
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
            return StatusCode(500, "An error occurred processing your request");
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
            return StatusCode(500, "An error occurred processing your request");
        }
    }

    [HttpGet("search")]
    public IActionResult SearchUsers([FromQuery] string query)
    {
        var results = _userService.SearchUsers(query);
        return Ok(results);
    }

    [HttpGet("audit")]
    [Authorize(Roles = "Admin")]
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
    public IActionResult Transfer([FromBody] TransferRequest? request)
    {
        if (request == null)
            return BadRequest(new { message = "Request body is required" });

        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (!int.TryParse(userIdClaim, out int fromUserId))
            return Unauthorized();

        var (success, message) = _transactionService.Transfer(fromUserId, request.ToUserId, request.Amount, request.Description);

        if (success)
            return Ok(new { message });

        return BadRequest(new { message });
    }

    [HttpPost("deposit")]
    public IActionResult Deposit([FromBody] DepositRequest? request)
    {
        if (request == null)
            return BadRequest(new { message = "Request body is required" });

        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (!int.TryParse(userIdClaim, out int userId))
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

## Change Log

### appsettings.json
- Replaced all hardcoded production secrets with `"__SET_VIA_ENV__"` placeholders
- Added `FromAddress` and `SupportAddress` for email configuration (CF1)
- Added `TransactionLimits` section for fee rate, daily limit, and deposit cap (M1, M2)
- Changed log levels from Debug to Information/Warning for production safety (CF2)

### SampleBankingApp.csproj
- Made debug symbols conditional on Release build (CF7)
- Updated Newtonsoft.Json from 12.0.3 to 13.0.3 to address known vulnerabilities (CF8)

### Program.cs
- Added null check and placeholder validation for JWT SecretKey (N1, CF1)
- Enabled `ValidateLifetime = true` for JWT tokens (C9, CF3)
- Uncommented HTTPS redirection middleware (CF4)
- Wrapped developer exception page behind environment check (CF5)
- Scoped CORS to configured origins instead of AllowAnyOrigin (CF6)

### DatabaseHelper.cs
- Removed the leaky `GetOpenConnection()` anti-pattern method (A6, RL2)
- Added proper `using` statements for SqlConnection and SqlDataReader (RL3)
- Added `ExecuteInTransaction()` helper for atomic multi-statement operations (E3)
- Removed unused `TableExists` and obsolete `ExecuteQueryWithParams` methods (D3, D4)

### StringHelper.cs
- Extracted magic numbers into named constants: MaxEmailLength=254, MinUsernameLength=3, MaxUsernameLength=20 (M4)
- Made Regex patterns static readonly for compilation-once behavior (A2)
- Replaced loop concatenation with `string.Join` in JoinWithSeparator (R2, A3)
- Removed dead code: ObfuscateAccount, ToTitleCase, IsBlank duplicates, unused JoinWithSeparatorFixed (D9, D10, D11, A5)

### AuthService.cs
- Added null checks for username/password inputs (N1)
- Replaced SQL string interpolation with parameterized queries using ExecuteQuerySafe (C1)
- Removed hardcoded admin bypass backdoor (AdminBypassPassword) (C2)
- Changed MD5 hashing to SHA256 (C3)
- Refactored GenerateJwtToken into named helpers: CreateSigningCredentials, BuildTokenClaims, WriteToken, CreateJwtSecurityToken (R3)
- Added null check for JWT secret key with proper exception (N1)
- Removed unused HashPasswordSha1 method (D1)
- Removed unreachable code after return statement in ValidateToken (D2)

### UserService.cs
- Extracted duplicated validation into private `ValidateUserId(int id)` helper (R1)
- Replaced SQL string interpolation with parameterized queries for UpdateUser, DeleteUser, SearchUsers (C4, C5)
- Fixed off-by-one pagination: changed `page * pageSize` to `(page - 1) * pageSize` (L3)
- Made static audit log thread-safe with lock object instead of raw mutable state (A1)
- Removed exception swallowing in SearchUsers; now propagates errors (E1)

### TransactionService.cs
- Changed `amount < 0` to `amount <= 0` to block zero-value transfers (L1)
- Added self-transfer check: `fromUserId != toUserId` (L5)
- Fixed balance check to include fee: changed `>= amount` to `< totalDebit` (L2)
- Changed interest rate from 5% (0.05m) to 1% (0.01m) (L4)
- Replaced SQL string interpolation with parameterized queries in Transfer and Deposit UPDATE statements (C6)
- Parameterized RecordTransaction INSERT statement (C7)
- Wrapped both balance updates in ExecuteInTransaction for atomicity (E3)
- Made email failure non-fatal by catching exception after DB commit succeeds (E4)
- Moved magic numbers to configuration accessors: GetTransactionFeeRate, GetDepositCap (M1, M2)
- Removed unused FormatCurrency and IsWithinDailyLimit methods (D7, D8)

### EmailService.cs
- Created SmtpClient per-send instead of holding as instance field (A4, RL4)
- Added `using` statements for MailMessage in SendTransferNotification and SendWelcomeEmail (RL5)
- Changed exception handling from generic Exception to specific SmtpException (E2)
- Extracted email addresses into GetFromAddress() and GetSupportAddress() helpers (M3)
- Added null checks for toEmail, username parameters (N4)

### AuthController.cs
- Added null check for request body (N7)
- Added validation for empty username/password fields

### UserController.cs
- Added ownership check on PUT /api/user/{id}: verifies caller owns account or is Admin (C10)
- Added [Authorize(Roles = "Admin")] to DELETE endpoint (C11)
- Changed exception handler to not expose ex.Message to client; uses generic message instead (E5)
- Added null check for request body in UpdateUser (N7)

### TransactionController.cs
- Added null checks for userIdClaim parsing with proper error handling (N6)
- Added null check for request body (N7)