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
