using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;
    private const int DepositCap = 1000000;

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

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        if (fromUserTable.Rows.Count == 0 || toUserTable.Rows.Count == 0)
            return (false, "Invalid user ID");

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= totalDebit)
        {
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance   = toBalance + amount;

            using var transaction = _db.GetOpenConnection().BeginTransaction();
            try
            {
                _db.ExecuteNonQuery(
                    "UPDATE Users SET Balance = @NewFromBalance WHERE Id = @FromUserId",
                    new Dictionary<string, object> { { "@NewFromBalance", newFromBalance }, { "@FromUserId", fromUserId } });

                _db.ExecuteNonQuery(
                    "UPDATE Users SET Balance = @NewToBalance WHERE Id = @ToUserId",
                    new Dictionary<string, object> { { "@NewToBalance", newToBalance }, { "@ToUserId", toUserId } });

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
                throw;
            }
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > DepositCap)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.01m * 1;

        _db.ExecuteNonQuery(
            "UPDATE Users SET Balance = Balance + @Amount WHERE Id = @UserId",
            new Dictionary<string, object> { { "@Amount", amount + interestBonus }, { "@UserId", userId } });

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description, System.Data.SqlClient.SqlTransaction? transaction = null)
    {
        string sql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES (@FromId, @ToId, @Amount, @Type, 'Completed', @Description, GETDATE())";
        if (transaction != null)
        {
            _db.ExecuteNonQuery(sql, new Dictionary<string, object>
            {
                { "@FromId", fromId },
                { "@ToId", toId },
                { "@Amount", amount },
                { "@Type", type },
                { "@Description", description }
            }, transaction);
        }
        else
        {
            _db.ExecuteNonQuery(sql, new Dictionary<string, object>
            {
                { "@FromId", fromId },
                { "@ToId", toId },
                { "@Amount", amount },
                { "@Type", type },
                { "@Description", description }
            });
        }
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}
