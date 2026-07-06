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
