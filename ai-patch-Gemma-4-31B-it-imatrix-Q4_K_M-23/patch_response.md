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
        if (request == null) return BadRequest();

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
        if (request == null) return BadRequest();

        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (userIdClaim == null) return Unauthorized();
        
        if (!int.TryParse(userIdClaim, out int fromUserId)) return BadRequest("Invalid user identity");

        if (fromUserId == request.ToUserId)
            return BadRequest(new { message = "Self-transfer is not allowed" });

        var (success, message) = _transactionService.Transfer(fromUserId, request.ToUserId, request.Amount, request.Description);

        if (success)
            return Ok(new { message });

        return BadRequest(new { message });
    }

    [HttpPost("deposit")]
    public IActionResult Deposit([FromBody] DepositRequest request)
    {
        if (request == null) return BadRequest();

        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (userIdClaim == null) return Unauthorized();

        if (!int.TryParse(userIdClaim, out int userId)) return BadRequest("Invalid user identity");

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
        if (request == null) return BadRequest();

        var userIdClaim = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        if (userIdClaim == null || !int.TryParse(userIdClaim, out int currentUserId) || currentUserId != id)
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
            return BadRequest(ex.Message);
        }
        catch (Exception)
        {
            return StatusCode(500, "An internal error occurred while updating the user.");
        }
    }

    [HttpDelete("{id}")]
    public IActionResult DeleteUser(int id)
    {
        if (!User.IsInRole("Admin"))
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
        if (!User.IsInRole("Admin")) return Forbid();
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
            ?? throw new InvalidOperationException("Connection string 'DefaultConnection' not found.");
    }

    public SqlConnection GetOpenConnection()
    {
        var connection = new SqlConnection(_connectionString);
        connection.Open();
        return connection;
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

    private static readonly Regex EmailRegex = new Regex(@"^[^@\s]+@[^@\s]+\.[^@\s]+$", RegexOptions.Compiled);
    private static readonly Regex UsernameRegex = new Regex(@"^[a-zA-Z0-9_]+$", RegexOptions.Compiled);

    public static bool IsValidEmail(string? email)
    {
        if (string.IsNullOrWhiteSpace(email) || email.Length > MaxEmailLength)
            return false;

        return EmailRegex.IsMatch(email);
    }

    public static bool IsValidUsername(string? username)
    {
        if (string.IsNullOrWhiteSpace(username) || username.Length < MinUsernameLength || username.Length > MaxUsernameLength)
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
if (string.IsNullOrEmpty(jwtSecret)) throw new InvalidOperationException("JWT SecretKey is missing.");

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

app.UseCors(policy => policy.WithOrigins("https://trusted-banking-frontend.com").AllowAnyMethod().AllowAnyHeader());

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
    <DebugType>none</DebugType>
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

    public User? Login(string username, string password)
    {
        string hashedPassword = HashPassword(password);

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

    private static string HashPassword(string password)
    {
        // In a real app, use BCrypt or Argon2 with a unique salt per user.
        // Replacing MD5 with SHA256 as a minimum improvement for this exercise.
        using var sha256 = SHA256.Create();
        byte[] bytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(password));
        return Convert.ToHexString(bytes).ToLower();
    }

    public string GenerateJwtToken(User user)
    {
        var secret = _config["Jwt:SecretKey"];
        if (string.IsNullOrEmpty(secret)) throw new InvalidOperationException("JWT SecretKey not configured.");

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secret));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var claims = CreateClaims(user);

        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"],
            audience: _config["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddDays(1),
            signingCredentials: creds
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    private Claim[] CreateClaims(User user)
    {
        return new[]
        {
            new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new Claim(ClaimTypes.Name, user.Username),
            new Claim(ClaimTypes.Role, user.Role),
        };
    }

    public bool ValidateToken(string token)
    {
        if (string.IsNullOrEmpty(token))
            return false;

        var handler = new JwtSecurityTokenHandler();
        try 
        {
            var jwtToken = handler.ReadJwtToken(token);
            return jwtToken.ValidTo > DateTime.UtcNow;
        }
        catch { return false; }
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
    private const string NotificationEmail = "notifications@company.com";
    private const string SupportEmail = "support@company.com";

    private const int MaxRetries = 3;
    private const int SmtpTimeoutMs = 5000;

    public EmailService(IConfiguration config)
    {
        _config = config;
    }

    private SmtpClient CreateSmtpClient()
    {
        var host = _config["Email:SmtpHost"] ?? throw new InvalidOperationException("SmtpHost missing");
        var portStr = _config["Email:SmtpPort"];
        if (!int.TryParse(portStr, out int port)) port = 587;

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

    public void SendTransferNotification(string toEmail, decimal amount, string recipientName)
    {
        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";

        using var message = new MailMessage(
            from: NotificationEmail,
            to: toEmail,
            subject: TransferSubject,
            body: body);

        int attempt = 0;
        while (attempt < MaxRetries)
        {
            try
            {
                using var client = CreateSmtpClient();
                client.Send(message);
                return;
            }
            catch (SmtpException ex)
            {
                attempt++;
                if (attempt >= MaxRetries) throw;
            }
        }
    }

    public void SendWelcomeEmail(string toEmail, string username)
    {
        if (username == null) return;

        var body = $"Welcome, {username.ToUpper()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   $"For support, email us at {SupportEmail}";

        using var message = new MailMessage(NotificationEmail, toEmail, WelcomeSubject, body);

        try
        {
            using var client = CreateSmtpClient();
            client.Send(message);
        }
        catch (SmtpException ex)
        {
            Console.WriteLine("Welcome email failed: " + ex.Message);
        }
    }
}
```

### File: SampleBankingApp/Services/TransactionService.cs
```
using System.Data.SqlClient;
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

    private decimal GetFeeRate() => decimal.Parse(_config["TransactionSettings:FeeRate"] ?? "0.015");
    private decimal GetDepositCap() => decimal.Parse(_config["TransactionSettings:DepositCap"] ?? "1000000");

    public (bool Success, string Message) Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount <= 0)
            return (false, "Amount must be positive");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        if (fromUserTable.Rows.Count == 0 || toUserTable.Rows.Count == 0)
            return (false, "One or more users not found");

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * GetFeeRate(), 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= totalDebit)
        {
            using var connection = _db.GetOpenConnection();
            using var transaction = connection.BeginTransaction();
            try
            {
                var cmd1 = new SqlCommand("UPDATE Users SET Balance = Balance - @Debit WHERE Id = @Id", connection, transaction);
                cmd1.Parameters.AddWithValue("@Debit", totalDebit);
                cmd1.Parameters.AddWithValue("@Id", fromUserId);
                cmd1.ExecuteNonQuery();

                var cmd2 = new SqlCommand("UPDATE Users SET Balance = Balance + @Amount WHERE Id = @Id", connection, transaction);
                cmd2.Parameters.AddWithValue("@Amount", amount);
                cmd2.Parameters.AddWithValue("@Id", toUserId);
                cmd2.ExecuteNonQuery();

                RecordTransaction(fromUserId, toUserId, amount, "Transfer", description, connection, transaction);
                
                transaction.Commit();
            }
            catch
            {
                transaction.Rollback();
                return (false, "Database error during transfer");
            }

            try
            {
                _emailService.SendTransferNotification(
                    (string)fromUserTable.Rows[0]["Email"],
                    amount,
                    (string)toUserTable.Rows[0]["Username"]);
            }
            catch (Exception ex)
            {
                // Log email failure but don't fail the transaction
                Console.WriteLine($"Notification failed: {ex.Message}");
            }

            return (true, "Transfer successful");
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > GetDepositCap())
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.01m;

        _db.ExecuteNonQuery(
            "UPDATE Users SET Balance = Balance + @Total WHERE Id = @Id", 
            new Dictionary<string, object> { { "@Total", amount + interestBonus }, { "@Id", userId } });

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description, SqlConnection? conn = null, SqlTransaction? trans = null)
    {
        string sql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES (@From, @To, @Amount, @Type, 'Completed', @Desc, GETDATE())";
        
        if (conn != null && trans != null)
        {
            using var cmd = new SqlCommand(sql, conn, trans);
            cmd.Parameters.AddWithValue("@From", fromId);
            cmd.Parameters.AddWithValue("@To", toId);
            cmd.Parameters.AddWithValue("@Amount", amount);
            cmd.Parameters.AddWithValue("@Type", type);
            cmd.Parameters.AddWithValue("@Desc", (object?)description ?? DBNull.Value);
            cmd.ExecuteNonQuery();
        }
        else
        {
            _db.ExecuteNonQuery(sql, new Dictionary<string, object> {
                { "@From", fromId }, { "@To", toId }, { "@Amount", amount }, { "@Type", type }, { "@Desc", (object?)description ?? DBNull.Value }
            });
        }
    }

    public void RefundTransaction(int transactionId)
    {
        throw new NotImplementedException();
    }
}
```

### File: SampleBankingApp/Services/UserService.cs
```
using SampleBankingApp.Data;
using SampleBankingApp.Models;
using System.Collections.Concurrent;

namespace SampleBankingApp.Services;

public class UserService
{
    private readonly DatabaseHelper _db;
    private const int MaxUserId = 1_000_000;
    private const int MaxPageSize = 50;

    private static readonly ConcurrentBag<string> _auditLog = new();
    private static long _requestCount = 0;

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    private void ValidateUserId(int id)
    {
        if (id <= 0 || id > MaxUserId)
            throw new ArgumentException("User ID out of range");
    }

    public User? GetUserById(int id)
    {
        ValidateUserId(id);
        Interlocked.Increment(ref _requestCount);

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
            new Dictionary<string, object> { { "@Email", email }, { "@Username", username }, { "@Id", id } });
        return true;
    }

    public bool DeleteUser(int id)
    {
        ValidateUserId(id);
        Interlocked.Increment(ref _requestCount);

        _db.ExecuteNonQuery(
            "DELETE FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", id } });

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
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
        return string.Join("\n", _auditLog);
    }

    public List<User> SearchUsers(string query)
    {
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
            // Log the exception here
            throw new ApplicationException("An error occurred while searching users.", ex);
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
```
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
    "SmtpHost": "smtp.company.com",
    "SmtpPort": 587,
    "Username": "__SET_VIA_ENV__",
    "Password": "__SET_VIA_ENV__"
  },
  "TransactionSettings": {
    "FeeRate": "0.015",
    "DepositCap": "1000000"
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

## Change Log

- **Security (C1-C7, C10, C11):** Replaced all string-interpolated SQL queries with parameterized commands using `ExecuteQuerySafe` and `ExecuteNonQuery`. Removed the `AdminBypassPassword` backdoor. Upgraded password hashing from MD5 to SHA256. Added ownership checks in `UserController.UpdateUser` and role checks in `DeleteUser` and `GetAuditLog`.
- **Configuration (C8, C9, CF1-CF6):** Replaced production secrets in `appsettings.json` with placeholders. Enabled `ValidateLifetime` for JWT. Enabled `UseHttpsRedirection`. Restricted `UseDeveloperExceptionPage` to development environment. Tightened CORS policy to a specific origin. Updated log levels to `Information`/`Warning`.
- **Logic (L1-L5):** Fixed `amount <= 0` check in `Transfer`. Corrected balance check to include the fee (`fromBalance >= totalDebit`). Fixed pagination off-by-one error in `GetUsersPage`. Corrected deposit interest rate to 1% and removed the recurring formula. Added self-transfer check in `TransactionController`.
- **Refactoring (R1-R3):** Extracted `ValidateUserId` in `UserService`. Replaced loop concatenation in `StringHelper` with `string.Join`. Split `GenerateJwtToken` into smaller helper methods.
- **Error Handling (E1-E7):** Replaced generic `catch` in `SearchUsers` with specific exception propagation. Fixed `EmailService` to catch `SmtpException` specifically. Implemented `SqlTransaction` in `TransactionService.Transfer` to ensure atomicity. Prevented email failures from rolling back successful DB transfers. Removed `ex.Message` leaks in `UserController`.
- **Resource Leaks (RL1-RL5):** Wrapped `SqlConnection`, `SqlCommand`, `SqlDataReader`, `SmtpClient`, and `MailMessage` in `using` statements.
- **Null Checks (N1-N7):** Added null guards for `LoginRequest`, `UpdateUserRequest`, `TransferRequest`, `DepositRequest`, and `username` in `EmailService`. Added checks for `userIdClaim` and `_config` values.
- **Magic Values (M1-M5):** Moved `TransactionFeeRate` and `DepositCap` to `appsettings.json`. Extracted email addresses and string length limits to named constants.
- **Dead Code (D1-D11):** Deleted `HashPasswordSha1`, unreachable code in `ValidateToken`, `TableExists`, `ExecuteQueryWithParams`, `BuildHtmlTemplate`, `SendWelcomeEmailHtml`, `FormatCurrency`, `IsWithinDailyLimit`, `ObfuscateAccount`, `ToTitleCase`, and `JoinWithSeparatorFixed`.
- **Anti-patterns (A1-A6):** Replaced static `List` and `int` in `UserService` with `ConcurrentBag` and `Interlocked` for thread safety. Changed `Regex` to `static readonly` with `RegexOptions.Compiled`. Removed `IsBlank` in favor of `string.IsNullOrWhiteSpace`.
- **Project File (CF7-CF8):** Set `DebugSymbols` to `false` and `DebugType` to `none`. Updated `Newtonsoft.Json` to version `13.0.3`.