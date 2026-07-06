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
            ?? "Server=localhost;Database=BankingDB;User Id=sa;Password=Admin1234!;";
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

    public int ExecuteNonQuerySafe(string sql, Dictionary<string, object> parameters, IDbTransaction? transaction = null)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand(sql, connection);
        
        if (transaction != null)
        {
            command.Transaction = (SqlTransaction)transaction;
        }

        foreach (var (key, value) in parameters)
            command.Parameters.AddWithValue(key, value);

        return command.ExecuteNonQuery();
    }

    public IDbTransaction BeginTransaction()
    {
        var connection = new SqlConnection(_connectionString);
        connection.Open();
        return connection.BeginTransaction();
    }
}
