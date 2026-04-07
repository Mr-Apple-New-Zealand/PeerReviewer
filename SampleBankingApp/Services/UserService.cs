using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class UserService
{
    private readonly DatabaseHelper _db;

    private static List<string> _auditLog = new();
    private static int _requestCount = 0;

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    public User? GetUserById(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

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
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _auditLog.Add($"UpdateUser called for id={id}, email={email}");

        string sql = $"UPDATE Users SET Email = '{email}', Username = '{username}' WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);
        return true;
    }

    public bool DeleteUser(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1000000)
            throw new ArgumentException("User ID out of range");

        _requestCount++;

        string sql = $"DELETE FROM Users WHERE Id = {id}";
        _db.ExecuteNonQuery(sql);

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > 50) pageSize = 50;

        int skip = page * pageSize;

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
        foreach (var entry in _auditLog)
        {
            report += entry + "\n";
        }
        return report;
    }

    public List<User> SearchUsers(string query)
    {
        try
        {
            var table = _db.ExecuteQuery("Users", $"Username LIKE '%{query}%'");
            var users = new List<User>();
            foreach (System.Data.DataRow row in table.Rows)
                users.Add(MapRowToUser(row));
            return users;
        }
        catch (Exception)
        {
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
