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
