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
        if (userIdClaim == null)
            return Unauthorized(new { message = "Authentication required" });

        int fromUserId;
        try
        {
            fromUserId = int.Parse(userIdClaim);
        }
        catch (FormatException)
        {
            return BadRequest(new { message = "Invalid user ID format" });
        }

        var (success, message) = _transactionService.Transfer(fromUserId, request.ToUserId, request.Amount, request.Description);

        if (success)
            return Ok(new { message });

        return BadRequest(new { message });
    }

    [HttpPost("deposit")]
    public IActionResult Deposit([FromBody] DepositRequest request)
    {
        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (userIdClaim == null)
            return Unauthorized(new { message = "Authentication required" });

        int userId;
        try
        {
            userId = int.Parse(userIdClaim);
        }
        catch (FormatException)
        {
            return BadRequest(new { message = "Invalid user ID format" });
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
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error processing refund for transaction {TransactionId}", transactionId);
            return StatusCode(500, "An error occurred during refund processing");
        }
    }
}
```

### File: SampleBankingApp/Controllers/UserController.cs
```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using SampleBankingApp.Services;

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
            return BadRequest(new { message = "Request body is required" });

        if (id <= 0)
            return BadRequest(new { message = "Invalid user ID" });

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
            return StatusCode(500, "An error occurred while updating user");
        }
    }

    [HttpDelete("{id}")]
    public IActionResult DeleteUser(int id)
    {
        if (id <= 0)
            return BadRequest(new { message = "Invalid user ID" });

        try
        {
            _userService.DeleteUser(id);
            return NoContent();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting user {Id}", id);
            return StatusCode(500, "An error occurred while deleting user");
        }
    }

    [HttpGet("search")]
    public IActionResult SearchUsers([FromQuery] string query)
    {
        if (string.IsNullOrWhiteSpace(query))
            return BadRequest(new { message = "Search query is required" });

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
            ?? "Server=localhost;Database=BankingDB;User Id=sa;Password=Admin1234!;TrustServerCertificate=True;";
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

    public int ExecuteNonQuery(string sql)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand(sql, connection);
        return command.ExecuteNonQuery();
    }

    public bool TableExists(string tableName)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        var result = connection.GetSchema("Tables", new[] { null, null, tableName, "BASE TABLE" });
        return result.Rows.Count > 0;
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
    public const int MaxEmailLength = 254;
    public const int MinUsernameLength = 3;
    public const int MaxUsernameLength = 20;
    public const int DefaultSmtpPort = 587;

    public static bool IsValidEmail(string? email)
    {
        if (string.IsNullOrEmpty(email))
            return false;

        if (email.Length > MaxEmailLength)
            return false;

        var regex = RegexCache.EmailPattern;
        return regex.IsMatch(email);
    }

    public static bool IsValidUsername(string? username)
    {
        if (string.IsNullOrEmpty(username))
            return false;

        if (username.Length < MinUsernameLength || username.Length > MaxUsernameLength)
            return false;

        var regex = RegexCache.UsernamePattern;
        return regex.IsMatch(username);
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

    private static readonly Regex RegexCache = new(@"^[^@\s]+@[^@\s]+\.[^@\s]+$", RegexOptions.Compiled);
    private static readonly Regex UsernameRegexCache = new(@"^[a-zA-Z0-9_]+$", RegexOptions.Compiled);
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

var jwtSecret = builder.Configuration["Jwt:SecretKey"] ?? "DefaultSecretKey";
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"] ?? "BankingApp",
            ValidAudience = builder.Configuration["Jwt:Audience"] ?? "BankingApp",
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
    app.UseHttpsRedirection();
    app.UseExceptionHandler("/error");
}

app.UseCors(policy => policy
    .AllowAnyOrigin()
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
    <DebugSymbols>false</DebugSymbols>
    <DebugType>pdbonly</DebugType>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="8.0.0" />
    <PackageReference Include="System.Data.SqlClient" Version="4.8.6" />
    <PackageReference Include="System.IdentityModel.Tokens.Jwt" Version="7.0.0" />
  </ItemGroup>

</Project>
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
        string hashedPassword = HashPasswordMd5(password);

        string sql = "SELECT * FROM Users WHERE Username = @Username AND Password = @Password AND IsActive = 1";

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
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_config["Jwt:SecretKey"] ?? "DefaultSecretKey"));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var claims = new[]
        {
            new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new Claim(ClaimTypes.Name, user.Username),
            new Claim(ClaimTypes.Role, user.Role),
        };

        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"] ?? "BankingApp",
            audience: _config["Jwt:Audience"] ?? "BankingApp",
            claims: claims,
            expires: DateTime.UtcNow.AddDays(30),
            signingCredentials: creds
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    public bool ValidateToken(string token)
    {
        if (string.IsNullOrEmpty(token))
            return false;

        try
        {
            var handler = new JwtSecurityTokenHandler();
            var jwtToken = handler.ReadJwtToken(token);
            return jwtToken.ValidTo > DateTime.UtcNow;
        }
        catch
        {
            return false;
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
    private const string WelcomeSubject = "Welcome to BankingApp!";

    private const int MaxRetries = 3;
    private const int SmtpTimeoutMs = 5000;

    public EmailService(IConfiguration config)
    {
        _config = config;

        var smtpHost = _config["Email:SmtpHost"] ?? "smtp.company.com";
        var smtpPort = int.Parse(_config["Email:SmtpPort"] ?? "587");
        var username = _config["Email:Username"] ?? "notifications@company.com";
        var password = _config["Email:Password"] ?? "EmailPass99";

        _smtpClient = new SmtpClient(smtpHost)
        {
            Port = smtpPort,
            Credentials = new NetworkCredential(username, password),
            EnableSsl = true,
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
                using var smtp = new SmtpClient(_config["Email:SmtpHost"] ?? "smtp.company.com")
                {
                    Port = int.Parse(_config["Email:SmtpPort"] ?? "587"),
                    Credentials = new NetworkCredential(
                        _config["Email:Username"] ?? "notifications@company.com",
                        _config["Email:Password"] ?? "EmailPass99"),
                    EnableSsl = true,
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

    public void SendWelcomeEmail(string toEmail, string username)
    {
        var body = $"Welcome, {username}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   "For support, email us at support@company.com";

        var message = new MailMessage("notifications@company.com", toEmail, WelcomeSubject, body);

        try
        {
            using var smtp = new SmtpClient(_config["Email:SmtpHost"] ?? "smtp.company.com")
            {
                Port = int.Parse(_config["Email:SmtpPort"] ?? "587"),
                Credentials = new NetworkCredential(
                    _config["Email:Username"] ?? "notifications@company.com",
                    _config["Email:Password"] ?? "EmailPass99"),
                EnableSsl = true,
                Timeout = SmtpTimeoutMs
            };
            smtp.Send(message);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Welcome email failed: " + ex.Message);
        }
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
    private const int MaxDepositAmount = 1000000;

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
            return (false, "Cannot transfer to yourself");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        if (fromUserTable.Rows.Count == 0 || toUserTable.Rows.Count == 0)
            return (false, "One or both users not found");

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance < totalDebit)
            return (false, "Insufficient funds");

        using var transaction = _db.GetConnection();
        transaction.BeginTransaction();

        try
        {
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance = toBalance + amount;

            transaction.ExecuteNonQuery($"UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                new Dictionary<string, object> { { "@Balance", newFromBalance }, { "@Id", fromUserId } });
            transaction.ExecuteNonQuery($"UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                new Dictionary<string, object> { { "@Balance", newToBalance }, { "@Id", toUserId } });

            RecordTransaction(fromUserId, toUserId, amount, "Transfer", description, transaction);

            _emailService.SendTransferNotification(
                (string)fromUserTable.Rows[0]["Email"],
                amount,
                (string)toUserTable.Rows[0]["Username"]);

            transaction.Commit();
            return (true, "Transfer successful");
        }
        catch
        {
            transaction.Rollback();
            return (false, "Transfer failed");
        }
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > MaxDepositAmount)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.01m;

        using var transaction = _db.GetConnection();
        transaction.BeginTransaction();

        try
        {
            decimal newBalance = _db.ExecuteQuerySafe(
                "SELECT Balance FROM Users WHERE Id = @Id",
                new Dictionary<string, object> { { "@Id", userId } })
                .Rows[0]["Balance"] as decimal;

            newBalance += amount + interestBonus;

            transaction.ExecuteNonQuery($"UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                new Dictionary<string, object> { { "@Balance", newBalance }, { "@Id", userId } });

            RecordTransaction(0, userId, amount, "Deposit", null, transaction);

            transaction.Commit();
            return (true, "Deposit successful");
        }
        catch
        {
            transaction.Rollback();
            return (false, "Deposit failed");
        }
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description, SqlTransaction? transaction = null)
    {
        string sql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES (@FromUserId, @ToUserId, @Amount, @Type, @Status, @Description, @CreatedAt)";
        _db.ExecuteNonQuery(sql, new Dictionary<string, object>
        {
            { "@FromUserId", fromId },
            { "@ToUserId", toId },
            { "@Amount", amount },
            { "@Type", type },
            { "@Status", "Completed" },
            { "@Description", description ?? string.Empty },
            { "@CreatedAt", DateTime.UtcNow }
        }, transaction);
    }

    public void RefundTransaction(int transactionId)
    {
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

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    private static bool ValidateUserId(int id)
    {
        return id > 0 && id <= 1000000;
    }

    public User? GetUserById(int id)
    {
        if (!ValidateUserId(id))
            throw new ArgumentException("Invalid user ID");

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
        if (!ValidateUserId(id))
            throw new ArgumentException("Invalid user ID");

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
        if (!ValidateUserId(id))
            throw new ArgumentException("Invalid user ID");

        string sql = "DELETE FROM Users WHERE Id = @Id";
        _db.ExecuteNonQuery(sql, new Dictionary<string, object> { { "@Id", id } });
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
        return report;
    }

    public List<User> SearchUsers(string query)
    {
        if (string.IsNullOrWhiteSpace(query))
            return new List<User>();

        try
        {
            var table = _db.ExecuteQuerySafe(
                "SELECT * FROM Users WHERE Username LIKE @Query",
                new Dictionary<string, object> { { "@Query", $"%{query}%" } });

            var users = new List<User>();
            foreach (System.Data.DataRow row in table.Rows)
                users.Add(MapRowToUser(row));
            return users;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error searching users");
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

### File: SampleBankingApp/appsettings.json
```json
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
    "SmtpPort": 587,
    "Username": "__SET_VIA_ENV__",
    "Password": "__SET_VIA_ENV__"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Warning",
      "Microsoft": "Warning",
      "System": "Warning"
    }
  },
  "AllowedHosts": "*"
}
```

### File: SampleBankingApp/appsettings.Production.json
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=prod-db.internal;Database=BankingDB;User Id=prod_user;Password=__SET_VIA_ENV__;TrustServerCertificate=True;"
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
  "Logging": {
    "LogLevel": {
      "Default": "Warning",
      "Microsoft": "Warning",
      "System": "Warning"
    }
  },
  "AllowedHosts": "prod.internal"
}
```

### File: SampleBankingApp/appsettings.Development.json
```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=BankingDB;User Id=sa;Password=Admin1234!;TrustServerCertificate=True;"
  },
  "Jwt": {
    "SecretKey": "dev-secret-key-for-development-only",
    "Issuer": "BankingApp",
    "Audience": "BankingApp"
  },
  "Email": {
    "SmtpHost": "localhost",
    "SmtpPort": 587,
    "Username": "dev@company.com",
    "Password": "dev-password"
  },
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft": "Debug",
      "System": "Debug"
    }
  },
  "AllowedHosts": "localhost"
}
```