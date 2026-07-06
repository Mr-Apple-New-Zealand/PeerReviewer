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

        using var connection = new SqlConnection(_config.GetConnectionString("DefaultConnection"));
        connection.Open();

        using var command = new SqlCommand("SELECT * FROM Users WHERE Username = @Username AND Password = @Password AND IsActive = 1", connection);
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

    private static string HashPasswordSha256(string password)
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

        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"],
            audience: _config["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddDays(30),
            signingCredentials: creds
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    private static SymmetricSecurityKey GetSigningKey()
    {
        var secretKey = Environment.GetEnvironmentVariable("JWT_SECRET_KEY") ?? "REPLACE_WITH_SECURE_KEY";
        return new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey));
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

    public bool ValidateToken(string token)
    {
        if (string.IsNullOrEmpty(token))
            return false;

        try
        {
            var handler = new JwtSecurityTokenHandler();
            var validationParameters = new TokenValidationParameters
            {
                ValidateIssuer = true,
                ValidateAudience = true,
                ValidateLifetime = true,
                ValidateIssuerSigningKey = true,
                ValidIssuer = _config["Jwt:Issuer"],
                ValidAudience = _config["Jwt:Audience"],
                IssuerSigningKey = GetSigningKey()
            };

            var principal = handler.ValidateToken(token, validationParameters, out var validatedToken);
            return validatedToken.ValidTo > DateTime.UtcNow;
        }
        catch
        {
            return false;
        }
    }
}

