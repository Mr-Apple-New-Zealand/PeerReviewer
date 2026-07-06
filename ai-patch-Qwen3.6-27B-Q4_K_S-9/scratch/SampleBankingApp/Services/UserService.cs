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
        if (id > 1_000_000)
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
        var parameters = new Dictionary<string, object>
        {
            { "@Email", email },
            { "@Username", username },
            { "@Id", id }
        };
        
        // Note: DatabaseHelper.ExecuteNonQuery doesn't support parameters directly in current signature, 
        // but we must fix SQL Injection. We will use ExecuteQuerySafe logic or modify call.
        // Since we cannot change DatabaseHelper signature easily without breaking other things, 
        // and ExecuteQuerySafe returns DataTable, we can't use it for UPDATE.
        // However, looking at DatabaseHelper, ExecuteNonQuery takes raw SQL. 
        // To fix SQL injection here, we MUST use parameters. 
        // The prompt says "Do not refactor unrelated code... keep namespaces, class names, and method signatures the same".
        // But DatabaseHelper.ExecuteNonQuery(string sql) is vulnerable.
        // We must assume we can use the safe method if available or fix the helper.
        // Actually, DatabaseHelper has ExecuteQuerySafe. It does NOT have ExecuteNonQuerySafe.
        // We must fix DatabaseHelper to support parameterized non-query or use a workaround.
        // Let's fix DatabaseHelper in its own file. Here we will call a new method or use the existing one if we fix it.
        // For now, let's assume we fix DatabaseHelper to have a parameterized ExecuteNonQuery.
        
        // Since I am patching DatabaseHelper separately, I will assume a method `ExecuteNonQuerySafe` exists or is added.
        // If I cannot add methods to DatabaseHelper, I am stuck. 
        // Rule 1: "Fix EVERY issue... Do not refactor unrelated code". 
        // Adding a method to DatabaseHelper is necessary to fix SQL Injection in UserService and TransactionService.
        
        // Let's proceed assuming DatabaseHelper is fixed to support parameters for non-query commands.
        // If not, I will have to inline the connection logic here, which is bad.
        // I will add `ExecuteNonQuerySafe` to DatabaseHelper.
        
        _db.ExecuteNonQuerySafe(sql, parameters);
        return true;
    }

    public bool DeleteUser(int id)
    {
        ValidateUserId(id);

        string sql = "DELETE FROM Users WHERE Id = @Id";
        var parameters = new Dictionary<string, object> { { "@Id", id } };
        _db.ExecuteNonQuerySafe(sql, parameters);
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

    public List<User> SearchUsers(string query)
    {
        try
        {
            string sql = "SELECT * FROM Users WHERE Username LIKE @Query";
            var parameters = new Dictionary<string, object> { { "@Query", $"%{query}%" } };
            var table = _db.ExecuteQuerySafe(sql, parameters);
            
            var users = new List<User>();
            foreach (System.Data.DataRow row in table.Rows)
                users.Add(MapRowToUser(row));
            return users;
        }
        catch (Exception ex)
        {
            // Log exception in real app, rethrow or handle specifically. 
            // Swallowing is bad (E1). Let's rethrow as a specific service exception or just let it bubble up to controller.
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
