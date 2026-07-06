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
