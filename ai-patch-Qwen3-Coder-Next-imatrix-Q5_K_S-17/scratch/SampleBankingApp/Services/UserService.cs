using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class UserService
{
    private readonly DatabaseHelper _db;

    private static readonly object AuditLock = new();
    private static readonly List<string> AuditLog = new();
    private static int RequestCount = 0;

    public UserService(DatabaseHelper db)
    {
        _db = db;
    }

    private static void ValidateUserId(int id)
    {
        if (id <= 0)
            throw new ArgumentException("Invalid user ID");
        if (id > 1_000_000)
            throw new ArgumentException("User ID out of range");
    }

    public User? GetUserById(int id)
    {
        ValidateUserId(id);

        Interlocked.Increment(ref RequestCount);

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

        lock (AuditLock)
        {
            AuditLog.Add($"UpdateUser called for id={id}, email={email}");
        }

        using var connection = new SqlConnection(_db.GetOpenConnection().ConnectionString);
        connection.Open();

        using var transaction = connection.BeginTransaction();
        try
        {
            using var cmd = new SqlCommand(
                "UPDATE Users SET Email = @Email, Username = @Username WHERE Id = @Id", connection, transaction);
            cmd.Parameters.AddWithValue("@Email", email);
            cmd.Parameters.AddWithValue("@Username", username);
            cmd.Parameters.AddWithValue("@Id", id);
            cmd.ExecuteNonQuery();

            transaction.Commit();
            return true;
        }
        catch
        {
            transaction.Rollback();
            return false;
        }
    }

    public bool DeleteUser(int id)
    {
        ValidateUserId(id);

        Interlocked.Increment(ref RequestCount);

        using var connection = new SqlConnection(_db.GetOpenConnection().ConnectionString);
        connection.Open();

        using var transaction = connection.BeginTransaction();
        try
        {
            using var cmd = new SqlCommand("DELETE FROM Users WHERE Id = @Id", connection, transaction);
            cmd.Parameters.AddWithValue("@Id", id);
            cmd.ExecuteNonQuery();

            lock (AuditLock)
            {
                AuditLog.Add($"DeleteUser: {id}");
            }

            transaction.Commit();
            return true;
        }
        catch
        {
            transaction.Rollback();
            return false;
        }
    }

    public List<User> GetUsersPage(int page, int pageSize)
    {
        if (pageSize <= 0)
            pageSize = 20;
        if (pageSize > 50)
            pageSize = 50;

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
        lock (AuditLock)
        {
            return string.Join("\n", AuditLog);
        }
    }

    public List<User> SearchUsers(string query)
    {
        if (string.IsNullOrEmpty(query))
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
            Console.WriteLine($"SearchUsers failed: {ex.Message}");
            throw;
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

