using System.Data;
using System.Data.SqlClient;

namespace SampleBankingApp.Data;

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

    public int ExecuteNonQuery(string sql, Dictionary<string, object> parameters)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand(sql, connection);
        foreach (var (key, value) in parameters)
            command.Parameters.AddWithValue(key, value);

        return command.ExecuteNonQuery();
    }

    public int ExecuteNonQuery(string sql)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        using var command = new SqlCommand(sql, connection);
        return command.ExecuteNonQuery();
    }

    public bool TableExists(string tableName)
    {
        using var connection = new SqlConnection(_connectionString);
        connection.Open();
        var result = connection.GetSchema("Tables", new[] { null, null, tableName, "BASE TABLE" });
        return result.Rows.Count > 0;
    }
}
