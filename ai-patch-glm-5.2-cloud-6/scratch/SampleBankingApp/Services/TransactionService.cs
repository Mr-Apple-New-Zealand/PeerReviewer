using SampleBankingApp.Data;
using SampleBankingApp.Models;
using System.Data.SqlClient;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal DefaultTransactionFeeRate = 0.015m;
    private const int DefaultMaxTransactionsPerDay = 10;
    private const decimal MaxDepositAmount = 1_000_000m;
    private const decimal DepositInterestRate = 0.01m;

    public TransactionService(DatabaseHelper db, EmailService emailService)
    {
        _db = db;
        _emailService = emailService;
    }

    private decimal TransactionFeeRate => decimal.TryParse(_config["Transaction:FeeRate"], out decimal rate) ? rate : DefaultTransactionFeeRate;
    private int MaxTransactionsPerDay => int.TryParse(_config["Transaction:MaxPerDay"], out int max) ? max : DefaultMaxTransactionsPerDay;

    private readonly IConfiguration _config;

    public TransactionService(DatabaseHelper db, EmailService emailService, IConfiguration config)
    {
        _db = db;
        _emailService = emailService;
        _config = config;
    }

    /// <summary>
    /// Transfers funds between two accounts.
    /// </summary>
    public (bool Success, string Message) Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount <= 0)
            return (false, "Amount must be positive");

        if (fromUserId == toUserId)
            return (false, "Cannot transfer to the same account");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        if (fromUserTable.Rows.Count == 0)
            return (false, "Sender account not found");

        if (toUserTable.Rows.Count == 0)
            return (false, "Recipient account not found");

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= totalDebit)
        {
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance   = toBalance + amount;

            using var connection = _db.CreateConnection();
            connection.Open();
            using var transaction = connection.BeginTransaction();

            try
            {
                ExecuteNonQueryWithTransaction(connection, transaction,
                    "UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                    new Dictionary<string, object> { { "@Balance", newFromBalance }, { "@Id", fromUserId } });

                ExecuteNonQueryWithTransaction(connection, transaction,
                    "UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                    new Dictionary<string, object> { { "@Balance", newToBalance }, { "@Id", toUserId } });

                RecordTransaction(connection, transaction, fromUserId, toUserId, amount, "Transfer", description);

                transaction.Commit();
            }
            catch (Exception)
            {
                transaction.Rollback();
                throw;
            }

            try
            {
                _emailService.SendTransferNotification(
                    (string)fromUserTable.Rows[0]["Email"],
                    amount,
                    (string)toUserTable.Rows[0]["Username"]);
            }
            catch (Exception)
            {
                // Email failure is non-critical; transfer has already succeeded.
            }

            return (true, "Transfer successful");
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > MaxDepositAmount)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * DepositInterestRate;

        _db.ExecuteNonQuery(
            "UPDATE Users SET Balance = Balance + @Amount WHERE Id = @Id",
            new Dictionary<string, object> { { "@Amount", amount + interestBonus }, { "@Id", userId } });

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private bool IsWithinDailyLimit(int userId)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT COUNT(*) AS TxCount FROM Transactions WHERE FromUserId = @Id AND CAST(CreatedAt AS DATE) = CAST(GETDATE() AS DATE)",
            new Dictionary<string, object> { { "@Id", userId } });

        int count = (int)table.Rows[0]["TxCount"];
        return count < MaxTransactionsPerDay;
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        const string sql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                              VALUES (@FromId, @ToId, @Amount, @Type, @Status, @Description, GETDATE())";
        
        _db.ExecuteNonQuery(sql, new Dictionary<string, object>
        {
            { "@FromId", fromId },
            { "@ToId", toId },
            { "@Amount", amount },
            { "@Type", type },
            { "@Status", "Completed" },
            { "@Description", description ?? string.Empty }
        });
    }

    private void RecordTransaction(SqlConnection connection, SqlTransaction transaction, int fromId, int toId, decimal amount, string type, string? description)
    {
        const string sql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                              VALUES (@FromId, @ToId, @Amount, @Type, @Status, @Description, GETDATE())";

        using var command = new SqlCommand(sql, connection, transaction);
        command.Parameters.AddWithValue("@FromId", fromId);
        command.Parameters.AddWithValue("@ToId", toId);
        command.Parameters.AddWithValue("@Amount", amount);
        command.Parameters.AddWithValue("@Type", type);
        command.Parameters.AddWithValue("@Status", "Completed");
        command.Parameters.AddWithValue("@Description", (object?)description ?? DBNull.Value);
        command.ExecuteNonQuery();
    }

    private void ExecuteNonQueryWithTransaction(SqlConnection connection, SqlTransaction transaction, string sql, Dictionary<string, object> parameters)
    {
        using var command = new SqlCommand(sql, connection, transaction);
        foreach (var (key, value) in parameters)
            command.Parameters.AddWithValue(key, value);
        command.ExecuteNonQuery();
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}
