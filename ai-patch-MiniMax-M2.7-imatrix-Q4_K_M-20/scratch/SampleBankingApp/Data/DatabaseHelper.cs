using System.Data;
using System.Data.SqlClient;

namespace SampleBankingApp.Data;

/// <summary>
/// Provides raw ADO.NET database access helpers.
/// </summary>
public class DatabaseHelper
{
    private readonly string _connectionString;

    public DatabaseHelper(IConfiguration configuration)
    {
        _connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("Database connection string is not configured.");
    }

    public DataTable ExecuteQuerySafe(string sql, Dictionary<string, object> parameters)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand(sql, connection);
        foreach (var (key, value) in parameters)
            command.Parameters.AddWithValue(key, value);

        using var reader = command.ExecuteReader();
        var table = new DataTable();
        table.Load(reader);
        return table;
    }

    public int ExecuteNonQuery(string sql, Dictionary<string, object>? parameters = null)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand(sql, connection);
        if (parameters != null)
        {
            foreach (var (key, value) in parameters)
                command.Parameters.AddWithValue(key, value);
        }
        return command.ExecuteNonQuery();
    }

    public int ExecuteInTransaction(params (string sql, Dictionary<string, object>? parameters)[] commands)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var transaction = connection.BeginTransaction();
        
        try
        {
            int totalRowsAffected = 0;
            foreach (var (sql, parameters) in commands)
            {
                using var command = new SqlCommand(sql, connection, transaction);
                if (parameters != null)
                {
                    foreach (var (key, value) in parameters)
                        command.Parameters.AddWithValue(key, value);
                }
                totalRowsAffected += command.ExecuteNonQuery();
            }
            transaction.Commit();
            return totalRowsAffected;
        }
        catch
        {
            transaction.Rollback();
            throw;
        }
    }
}
