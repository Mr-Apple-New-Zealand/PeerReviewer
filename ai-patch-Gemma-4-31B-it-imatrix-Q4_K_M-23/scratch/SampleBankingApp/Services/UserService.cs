using SampleBankingApp.Data;
using SampleBankingApp.Models;
using System.Collections.Concurrent;

namespace SampleBankingApp.Services;

public class UserService
{
    private readonly DatabaseHelper _db;
    private const int MaxUserId = 1_000_000;
    private const int MaxPageSize = 50;

    private static readonly ConcurrentBag<string> _auditLog = new();
    private static long _requestCount = 0;

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    private void ValidateUserId(int id)
    {
        if (id <= 0 || id > MaxUserId)
            throw new ArgumentException("User ID out of range");
    }

    public User? GetUserById(int id)
    {
        ValidateUserId(id);
        Interlocked.Increment(ref _requestCount);

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
            new Dictionary<string, object> { { "@Email", email }, { "@Username", username }, { "@Id", id } });
        return true;
    }

    public bool DeleteUser(int id)
    {
        ValidateUserId(id);
        Interlocked.Increment(ref _requestCount);

        _db.ExecuteNonQuery(
            "DELETE FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", id } });

        _auditLog.Add($"DeleteUser: {id}");
        return true;
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize > MaxPageSize) pageSize = MaxPageSize;
        if (page < 1) page = 1;

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
            // Log the exception here
            throw new ApplicationException("An error occurred while searching users.", ex);
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
