using SampleBankingApp.Data;
using SampleBankingApp.Models;
using System.Data.SqlClient;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;
    private const decimal DepositInterestRate = 0.01m;
    private const decimal MaxDepositAmount = 1_000_000m;

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
            return (false, "Cannot transfer funds to your own account");

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

        if (fromBalance < totalDebit)
        {
            return (false, "Insufficient funds");
        }

        decimal newFromBalance = fromBalance - totalDebit;
        decimal newToBalance   = toBalance + amount;

        using var connection = new SqlConnection(_db.GetConnectionString());
        connection.Open();
        using var transaction = connection.BeginTransaction();

        try
        {
            using (var debitCmd = new SqlCommand("UPDATE Users SET Balance = @Balance WHERE Id = @Id", connection, transaction))
            {
                debitCmd.Parameters.AddWithValue("@Balance", newFromBalance);
                debitCmd.Parameters.AddWithValue("@Id", fromUserId);
                debitCmd.ExecuteNonQuery();
            }

            using (var creditCmd = new SqlCommand("UPDATE Users SET Balance = @Balance WHERE Id = @Id", connection, transaction))
            {
                creditCmd.Parameters.AddWithValue("@Balance", newToBalance);
                creditCmd.Parameters.AddWithValue("@Id", toUserId);
                creditCmd.ExecuteNonQuery();
            }

            using (var recordCmd = new SqlCommand("INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt) VALUES (@FromUserId, @ToUserId, @Amount, @Type, @Status, @Description, GETDATE())", connection, transaction))
            {
                recordCmd.Parameters.AddWithValue("@FromUserId", fromUserId);
                recordCmd.Parameters.AddWithValue("@ToUserId", toUserId);
                recordCmd.Parameters.AddWithValue("@Amount", amount);
                recordCmd.Parameters.AddWithValue("@Type", "Transfer");
                recordCmd.Parameters.AddWithValue("@Status", "Completed");
                recordCmd.Parameters.AddWithValue("@Description", (object?)description ?? DBNull.Value);
                recordCmd.ExecuteNonQuery();
            }

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
            // Swallow email notification failure so the committed transfer succeeds
        }

        return (true, "Transfer successful");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > MaxDepositAmount)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * DepositInterestRate;

        _db.ExecuteNonQuery(
            "UPDATE Users SET Balance = Balance + @Amount WHERE Id = @Id",
            new Dictionary<string, object> 
            { 
                { "@Amount", amount + interestBonus }, 
                { "@Id", userId } 
            });

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        string sql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES (@FromUserId, @ToUserId, @Amount, @Type, @Status, @Description, GETDATE())";
        
        _db.ExecuteNonQuery(sql, new Dictionary<string, object>
        {
            { "@FromUserId", fromId },
            { "@ToUserId", toId },
            { "@Amount", amount },
            { "@Type", type },
            { "@Status", "Completed" },
            { "@Description", (object?)description ?? DBNull.Value }
        });
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}
