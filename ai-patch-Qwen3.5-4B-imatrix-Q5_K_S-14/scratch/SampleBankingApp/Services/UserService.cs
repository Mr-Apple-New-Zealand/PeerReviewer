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
