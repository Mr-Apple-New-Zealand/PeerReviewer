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
            return (false, "Cannot transfer to yourself");

        var feeRate = GetTransactionFeeRate();
        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        if (fromUserTable.Rows.Count == 0)
            return (false, "Source user not found");

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        if (toUserTable.Rows.Count == 0)
            return (false, "Destination user not found");

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        decimal fee = Math.Round(amount * feeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance < totalDebit)
            return (false, "Insufficient funds");

        try
        {
            _db.ExecuteInTransaction(
                ("UPDATE Users SET Balance = @NewBalance WHERE Id = @Id", 
                    new Dictionary<string, object> { { "@NewBalance", fromBalance - totalDebit }, { "@Id", fromUserId } }),
                ("UPDATE Users SET Balance = @NewBalance WHERE Id = @Id",
                    new Dictionary<string, object> { { "@NewBalance", (decimal)toUserTable.Rows[0]["Balance"] + amount }, { "@Id", toUserId } })
            );

            RecordTransaction(fromUserId, toUserId, amount, "Transfer", description);

            try
            {
                _emailService.SendTransferNotification(
                    (string)fromUserTable.Rows[0]["Email"],
                    amount,
                    (string)toUserTable.Rows[0]["Username"]);
            }
            catch (Exception)
            {
                // Log but don't fail the transfer if email fails
            }

            return (true, "Transfer successful");
        }
        catch
        {
            return (false, "Transfer failed due to a system error");
        }
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        var depositCap = GetDepositCap();
        
        if (amount <= 0 || amount > depositCap)
            return (false, $"Invalid deposit amount. Must be between 0 and {depositCap}");

        var interestRate = 0.01m;
        decimal interestBonus = amount * interestRate;

        _db.ExecuteNonQuery(
            "UPDATE Users SET Balance = Balance + @Amount WHERE Id = @Id",
            new Dictionary<string, object> { { "@Amount", amount + interestBonus }, { "@Id", userId } });

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        var parameters = new Dictionary<string, object>
        {
            { "@FromId", fromId },
            { "@ToId", toId },
            { "@Amount", amount },
            { "@Type", type },
            { "@Description", description ?? string.Empty }
        };

        _db.ExecuteNonQuery(
            @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
              VALUES (@FromId, @ToId, @Amount, @Type, 'Completed', @Description, GETDATE())",
            parameters);
    }

    public void RefundTransaction(int transactionId)
    {
        throw new NotImplementedException();
    }

    private decimal GetTransactionFeeRate()
    {
        var configValue = _config["TransactionLimits:FeeRate"];
        return decimal.TryParse(configValue, out var rate) ? rate : 0.015m;
    }

    private decimal GetDepositCap()
    {
        var configValue = _config["TransactionLimits:DepositCap"];
        return decimal.TryParse(configValue, out var cap) ? cap : 1_000_000m;
    }
}
