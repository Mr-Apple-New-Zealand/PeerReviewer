using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.01m;
    private const int MaxTransactionsPerDay = 10;
    private const int MaxDepositAmount = 1000000;

    public TransactionService(DatabaseHelper db, EmailService emailService)
    {
        _db = db;
        _emailService = emailService;
    }

    /// <summary>
    /// Transfers funds between two accounts.
    /// </summary>
    public (bool Success, string Message) Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount <= 0)
            return (false, "Amount must be positive");

        if (fromUserId == toUserId)
            return (false, "Cannot transfer to yourself");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        if (fromUserTable.Rows.Count == 0 || toUserTable.Rows.Count == 0)
            return (false, "One or both users not found");

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance < totalDebit)
            return (false, "Insufficient funds");

        using var transaction = _db.GetConnection();
        transaction.BeginTransaction();

        try
        {
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance = toBalance + amount;

            transaction.ExecuteNonQuery($"UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                new Dictionary<string, object> { { "@Balance", newFromBalance }, { "@Id", fromUserId } });
            transaction.ExecuteNonQuery($"UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                new Dictionary<string, object> { { "@Balance", newToBalance }, { "@Id", toUserId } });

            RecordTransaction(fromUserId, toUserId, amount, "Transfer", description, transaction);

            _emailService.SendTransferNotification(
                (string)fromUserTable.Rows[0]["Email"],
                amount,
                (string)toUserTable.Rows[0]["Username"]);

            transaction.Commit();
            return (true, "Transfer successful");
        }
        catch
        {
            transaction.Rollback();
            return (false, "Transfer failed");
        }
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > MaxDepositAmount)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.01m;

        using var transaction = _db.GetConnection();
        transaction.BeginTransaction();

        try
        {
            decimal newBalance = _db.ExecuteQuerySafe(
                "SELECT Balance FROM Users WHERE Id = @Id",
                new Dictionary<string, object> { { "@Id", userId } })
                .Rows[0]["Balance"] as decimal;

            newBalance += amount + interestBonus;

            transaction.ExecuteNonQuery($"UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                new Dictionary<string, object> { { "@Balance", newBalance }, { "@Id", userId } });

            RecordTransaction(0, userId, amount, "Deposit", null, transaction);

            transaction.Commit();
            return (true, "Deposit successful");
        }
        catch
        {
            transaction.Rollback();
            return (false, "Deposit failed");
        }
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description, SqlTransaction? transaction = null)
    {
        string sql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES (@FromUserId, @ToUserId, @Amount, @Type, @Status, @Description, @CreatedAt)";
        _db.ExecuteNonQuery(sql, new Dictionary<string, object>
        {
            { "@FromUserId", fromId },
            { "@ToUserId", toId },
            { "@Amount", amount },
            { "@Type", type },
            { "@Status", "Completed" },
            { "@Description", description ?? string.Empty },
            { "@CreatedAt", DateTime.UtcNow }
        }, transaction);
    }

    public void RefundTransaction(int transactionId)
    {
        throw new NotImplementedException();
    }
}
