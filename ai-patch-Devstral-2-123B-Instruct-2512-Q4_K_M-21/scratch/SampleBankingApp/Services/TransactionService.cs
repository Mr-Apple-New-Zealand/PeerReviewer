using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;
    private const decimal MaxDepositAmount = 1_000_000m;
    private const decimal DepositInterestRate = 0.01m;

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
            return (false, "Cannot transfer to the same account");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        if (fromUserTable.Rows.Count == 0 || toUserTable.Rows.Count == 0)
            return (false, "User not found");

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= totalDebit)
        {
            using var transaction = _db.GetOpenConnection().BeginTransaction();
            try
            {
                decimal newFromBalance = fromBalance - totalDebit;
                decimal newToBalance = toBalance + amount;

                _db.ExecuteNonQuerySafe(
                    "UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                    new Dictionary<string, object> { { "@Balance", newFromBalance }, { "@Id", fromUserId } });

                _db.ExecuteNonQuerySafe(
                    "UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                    new Dictionary<string, object> { { "@Balance", newToBalance }, { "@Id", toUserId } });

                RecordTransaction(fromUserId, toUserId, amount, "Transfer", description);

                transaction.Commit();

                try
                {
                    _emailService.SendTransferNotification(
                        (string)fromUserTable.Rows[0]["Email"],
                        amount,
                        (string)toUserTable.Rows[0]["Username"]);
                }
                catch (Exception)
                {
                    // Log email failure but do not rollback the transaction
                }

                return (true, "Transfer successful");
            }
            catch (Exception)
            {
                transaction.Rollback();
                return (false, "Transfer failed");
            }
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > MaxDepositAmount)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * DepositInterestRate;

        _db.ExecuteNonQuerySafe(
            "UPDATE Users SET Balance = Balance + @Amount WHERE Id = @Id",
            new Dictionary<string, object> { { "@Amount", amount + interestBonus }, { "@Id", userId } });

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        string sql = $@"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES (@FromId, @ToId, @Amount, @Type, 'Completed', @Description, GETDATE())";
        _db.ExecuteNonQuerySafe(sql, new Dictionary<string, object>
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

