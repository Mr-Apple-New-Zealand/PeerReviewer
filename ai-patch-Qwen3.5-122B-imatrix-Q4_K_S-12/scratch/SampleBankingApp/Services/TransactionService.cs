using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;
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
            return (false, "Self-transfers are not allowed");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        if (fromUserTable.Rows.Count == 0 || toUserTable.Rows.Count == 0)
            return (false, "User not found");

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal feeRate = decimal.Parse(_config["Transaction:FeeRate"] ?? "0.015");
        decimal fee = Math.Round(amount * feeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance < totalDebit)
        {
            return (false, "Insufficient funds");
        }

        try
        {
            _db.ExecuteNonQuery("BEGIN TRANSACTION");
            
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance   = toBalance + amount;

            _db.ExecuteNonQuery("UPDATE Users SET Balance = @Balance WHERE Id = @Id", 
                new Dictionary<string, object> { { "@Balance", newFromBalance }, { "@Id", fromUserId } });
            
            _db.ExecuteNonQuery("UPDATE Users SET Balance = @Balance WHERE Id = @Id", 
                new Dictionary<string, object> { { "@Balance", newToBalance }, { "@Id", toUserId } });

            RecordTransaction(fromUserId, toUserId, amount, "Transfer", description);

            _db.ExecuteNonQuery("COMMIT TRANSACTION");

            try
            {
                _emailService.SendTransferNotification(
                    (string)fromUserTable.Rows[0]["Email"],
                    amount,
                    (string)toUserTable.Rows[0]["Username"]);
            }
            catch (Exception)
            {
                // Email failure should not rollback the transaction, just log it
            }

            return (true, "Transfer successful");
        }
        catch (Exception)
        {
            _db.ExecuteNonQuery("ROLLBACK TRANSACTION");
            return (false, "Transaction failed");
        }
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > 1_000_000)
            return (false, "Invalid deposit amount");

        decimal interestRate = decimal.Parse(_config["Transaction:InterestRate"] ?? "0.01");
        decimal interestBonus = amount * interestRate;

        _db.ExecuteNonQuery(
            "UPDATE Users SET Balance = Balance + @Amount WHERE Id = @Id",
            new Dictionary<string, object> { { "@Amount", amount + interestBonus }, { "@Id", userId } });

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        string sql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES (@FromId, @ToId, @Amount, @Type, 'Completed', @Description, GETDATE())";
        
        _db.ExecuteNonQuery(sql, new Dictionary<string, object> 
        { 
            { "@FromId", fromId }, 
            { "@ToId", toId }, 
            { "@Amount", amount }, 
            { "@Type", type }, 
            { "@Description", description ?? string.Empty } 
        });
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}
