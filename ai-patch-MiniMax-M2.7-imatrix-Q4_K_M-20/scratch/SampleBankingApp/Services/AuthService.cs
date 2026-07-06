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
