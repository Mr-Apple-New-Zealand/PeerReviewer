# Patched Files

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
        var user = GetValidUser(username);
        if (user == null) return null;

        if (VerifyPassword(password, user.Password))
        {
            return user;
        }

        return null;
    }

    private User? GetValidUser(string username)
    {
        try
        {
            var table = _db.ExecuteQuerySafe(
                "SELECT * FROM Users WHERE Username = @Username AND IsActive = 1",
                new Dictionary<string, object> { { "@Username", username } });

            if (table.Rows.Count == 0)
                return null;

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
        catch (Exception ex)
        {
            // Log exception but don't expose details
            return null;
        }
    }

    private bool VerifyPassword(string input, string hashed)
    {
        // In a real app, we'd use a proper password hasher like BCrypt
        return hashed == HashPasswordMd5(input);
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
    private readonly IConfiguration _config;

    public TransactionService(DatabaseHelper db, EmailService emailService, IConfiguration config)
    {
        _db = db;
        _emailService = emailService;
        _config = config;
    }

    public (bool Success, string Message) Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount <= 0)
            return (false, "Amount must be positive");

        if (fromUserId == toUserId)
            return (false, "Cannot transfer to yourself");

        try
        {
            var fromUserTable = _db.ExecuteQuerySafe(
                "SELECT * FROM Users WHERE Id = @Id",
                new Dictionary<string, object> { { "@Id", fromUserId } });

            var toUserTable = _db.ExecuteQuerySafe(
                "SELECT * FROM Users WHERE Id = @Id",
                new Dictionary<string, object> { { "@Id", toUserId } });

            if (fromUserTable.Rows.Count == 0 || toUserTable.Rows.Count == 0)
                return (false, "User not found");

            var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
            var toBalance = (decimal)toUserTable.Rows[0]["Balance"];

            decimal fee = Math.Round(amount * _config.GetValue<decimal>("Transaction:FeeRate"), 2);
            decimal totalDebit = amount + fee;

            if (fromBalance < totalDebit)
                return (false, "Insufficient funds");

            using var connection = _db.GetOpenConnection();
            using var transaction = connection.BeginTransaction();

            try
            {
                var newFromBalance = fromBalance - totalDebit;
                var newToBalance = toBalance + amount;

                _db.ExecuteNonQuery(
                    "UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                    new Dictionary<string, object> { 
                        { "@Balance", newFromBalance }, 
                        { "@Id", fromUserId } },
                    connection,
                    transaction);

                _db.ExecuteNonQuery(
                    "UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                    new Dictionary<string, object> { 
                        { "@Balance", newToBalance }, 
                        { "@Id", toUserId } },
                    connection,
                    transaction);

                RecordTransaction(fromUserId, toUserId, amount, "Transfer", description, connection, transaction);

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
                throw;
            }
        }
        catch (Exception ex)
        {
            // Log exception but don't expose details
            return (false, "An error occurred during the transfer");
        }
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > _config.GetValue<decimal>("Transaction:MaxDeposit"))
            return (false, "Invalid deposit amount");

        try
        {
            var userTable = _db.ExecuteQuerySafe(
                "SELECT * FROM Users WHERE Id = @Id",
                new Dictionary<string, object> { { "@Id", userId } });

            if (userTable.Rows.Count == 0)
                return (false, "User not found");

            decimal interestBonus = amount * _config.GetValue<decimal>("Transaction:InterestRate");

            _db.ExecuteNonQuery(
                "UPDATE Users SET Balance = Balance + @Amount WHERE Id = @Id",
                new Dictionary<string, object> { 
                    { "@Amount", amount + interestBonus }, 
                    { "@Id", userId } });

            RecordTransaction(0, userId, amount, "Deposit", null);
            return (true, "Deposit successful");
        }
        catch (Exception ex)
        {
            // Log exception but don't expose details
            return (false, "An error occurred during the deposit");
        }
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description, SqlConnection? connection = null, SqlTransaction? transaction = null)
    {
        string sql = "INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt) " +
                     "VALUES (@FromUserId, @ToUserId, @Amount, @Type, @Status, @Description, GETDATE())";

        var parameters = new Dictionary<string, object>
        {
            { "@FromUserId", fromId },
            { "@ToUserId", toId },
            { "@Amount", amount },
            { "@Type", type },
            { "@Status", "Completed" },
            { "@Description", description ?? string.Empty }
        };

        if (connection != null)
        {
            _db.ExecuteNonQuery(sql, parameters, connection, transaction);
        }
        else
        {
            _db.ExecuteNonQuery(sql, parameters);
        }
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

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    private void ValidateUserId(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");
    }

    public User? GetUserById(int id)
    {
        ValidateUserId(id);

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

        string sql = "UPDATE Users SET Email = @Email, Username = @Username WHERE Id = @Id";
        return _db.ExecuteNonQuery(sql, new Dictionary<string, object> { 
            { "@Email", email }, 
            { "@Username", username }, 
            { "@Id", id } }) > 0;
    }

    public bool DeleteUser(int id)
    {
        ValidateUserId(id);

        string sql = "DELETE FROM Users WHERE Id = @Id";
        return _db.ExecuteNonQuery(sql, new Dictionary<string, object> { { "@Id", id } }) > 0;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;
        int skip = (page - 1) * pageSize;

        var table = _db.ExecuteQuerySafe(
            "SELECT * FROM Users ORDER BY Id OFFSET @Skip ROWS FETCH NEXT @PageSize ROWS ONLY",
            new Dictionary<string, object> { 
                { "@Skip", skip }, 
                { "@PageSize", pageSize } });

        var users = new List<User>();
        foreach (System.Data.DataRow row in table.Rows)
            users.Add(MapRowToUser(row));

        return users;
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

### File: SampleBankingApp/Controllers/UserController.cs
```
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
    [Authorize(Roles = "Admin")]
    public IActionResult UpdateUser(int id, [FromBody] UpdateUserRequest request)
    {
        if (request == null)
            return BadRequest("Request body is required");

        try
        {
            if (!_userService.UpdateUser(id, request.Email, request.Username))
                return NotFound();

            return NoContent();
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
            if (!_userService.DeleteUser(id))
                return NotFound();

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
}

public class UpdateUserRequest
{
    public string Email { get; set; } = string.Empty;
    public string Username { get; set; } = string.Empty;
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
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret!))
        };
    });

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

app.UseHttpsRedirection();

app.UseCors(policy => policy
    .WithOrigins("https://localhost:5001")
    .AllowAnyMethod()
    .AllowAnyHeader());

app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.Run();
```

### File: SampleBankingApp/Services/EmailService.cs
```
using System.Net;
using System.Net.Mail;

namespace SampleBankingApp.Services;

public class EmailService
{
    private readonly IConfiguration _config;

    public EmailService(IConfiguration config)
    {
        _config = config;
    }

    public void SendTransferNotification(string toEmail, decimal amount, string recipientName)
    {
        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";

        var message = new MailMessage(
            from: _config["Email:FromAddress"],
            to: toEmail,
            subject: "Transfer Notification - BankingApp",
            body: body);

        using var smtpClient = new SmtpClient(_config["Email:SmtpHost"])
        {
            Port = int.Parse(_config["Email:SmtpPort"]!),
            Credentials = new NetworkCredential(
                _config["Email:Username"]!,
                _config["Email:Password"]!),
            EnableSsl = _config.GetValue<bool>("Email:UseSsl"),
            Timeout = 5000
        };

        try
        {
            smtpClient.Send(message);
        }
        catch (SmtpException ex)
        {
            // Log exception but don't expose details
            Console.WriteLine($"Email failed: {ex.Message}");
        }
        finally
        {
            message.Dispose();
        }
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
    "SmtpHost": "__SET_VIA_ENV__",
    "SmtpPort": "__SET_VIA_ENV__",
    "Username": "__SET_VIA_ENV__",
    "Password": "__SET_VIA_ENV__",
    "FromAddress": "notifications@company.com",
    "UseSsl": true
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

### File: SampleBankingApp/Data/DatabaseHelper.cs
```
using System.Data;
using System.Data.SqlClient;

namespace SampleBankingApp.Data;

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

    public int ExecuteNonQuery(string sql, Dictionary<string, object> parameters)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand(sql, connection);
        foreach (var (key, value) in parameters)
            command.Parameters.AddWithValue(key, value);

        return command.ExecuteNonQuery();
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