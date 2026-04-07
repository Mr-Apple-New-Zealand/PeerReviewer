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

    public SqlConnection GetOpenConnection()
    {
        var connection = new SqlConnection(_connectionString);
        connection.Open();
        return connection;
    }

    public DataTable ExecuteQuery(string tableName, string whereClause)
    {
        var connection = GetOpenConnection();
        var command = new SqlCommand($"SELECT * FROM {tableName} WHERE {whereClause}", connection);
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

    public int ExecuteNonQuery(string sql)
    {
        var connection = GetOpenConnection();
        var command = new SqlCommand(sql, connection);
        int rows = command.ExecuteNonQuery();
        connection.Close();
        return rows;
    }

    public bool TableExists(string tableName)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        var result = connection.GetSchema("Tables", new[] { null, null, tableName, "BASE TABLE" });
        return result.Rows.Count > 0;
    }

    [Obsolete("Use ExecuteQuerySafe instead")]
    public DataTable ExecuteQueryWithParams(string sql, SqlParameter[] parameters)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand(sql, connection);
        command.Parameters.AddRange(parameters);
        var adapter = new SqlDataAdapter(command);
        var table = new DataTable();
        adapter.Fill(table);
        return table;
    }
}
