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
            ?? throw new InvalidOperationException("DefaultConnection is not configured.");
    }
    /// <summary>
    /// Executes a SELECT query with a raw WHERE clause. The tableName and whereClause
    /// must come from trusted internal sources — never from user input.
    /// </summary>
    public DataTable ExecuteQuery(string tableName, string whereClause)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand($"SELECT * FROM {tableName} WHERE {whereClause}", connection);
        var adapter = new SqlDataAdapter(command);
        var table = new DataTable();
        adapter.Fill(table);
        return table;
    }
    public DataTable ExecuteQuerySafe(string sql, Dictionary<string, object> parameters)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand(sql, connection);
        foreach (var (key, value) in parameters)
            command.Parameters.AddWithValue(key, value);
        var adapter = new SqlDataAdapter(command);
        var table = new DataTable();
        adapter.Fill(table);
        return table;
    }
    public int ExecuteNonQuery(string sql, Dictionary<string, object?>? parameters = null)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand(sql, connection);
        if (parameters != null)
            foreach (var (key, value) in parameters)
                command.Parameters.AddWithValue(key, value ?? DBNull.Value);
        return command.ExecuteNonQuery();
    }
    /// <summary>
    /// Executes multiple SQL statements inside a single database transaction.
    /// Rolls back all statements if any one fails.
    /// </summary>
    public void ExecuteNonQueryBatch(IEnumerable<(string Sql, Dictionary<string, object?>? Parameters)> commands)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var transaction = connection.BeginTransaction();
        try
        {
            foreach (var (sql, parameters) in commands)
            {
                using var command = new SqlCommand(sql, connection, transaction);
                if (parameters != null)
                    foreach (var (key, value) in parameters)
                        command.Parameters.AddWithValue(key, value ?? DBNull.Value);
                command.ExecuteNonQuery();
            }
            transaction.Commit();
        }
        catch
        {
            transaction.Rollback();
            throw;
        }
    }
}
