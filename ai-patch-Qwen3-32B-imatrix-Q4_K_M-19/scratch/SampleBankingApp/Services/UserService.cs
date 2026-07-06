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
