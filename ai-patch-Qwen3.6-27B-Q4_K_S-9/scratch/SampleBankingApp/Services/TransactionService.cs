using System.Data;
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
            return (false, "Cannot transfer to yourself");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        if (fromUserTable.Rows.Count == 0)
            return (false, "Sender not found");

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        if (toUserTable.Rows.Count == 0)
            return (false, "Recipient not found");

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= totalDebit)
        {
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance   = toBalance + amount;

            // Use Transaction for atomicity
            using var transaction = _db.BeginTransaction();
            try
            {
                string updateFromSql = "UPDATE Users SET Balance = @Balance WHERE Id = @Id";
                var fromParams = new Dictionary<string, object> { { "@Balance", newFromBalance }, { "@Id", fromUserId } };
                _db.ExecuteNonQuerySafe(updateFromSql, fromParams, transaction);

                string updateToSql = "UPDATE Users SET Balance = @Balance WHERE Id = @Id";
                var toParams = new Dictionary<string, object> { { "@Balance", newToBalance }, { "@Id", toUserId } };
                _db.ExecuteNonQuerySafe(updateToSql, toParams, transaction);

                RecordTransaction(fromUserId, toUserId, amount, "Transfer", description, transaction);

                transaction.Commit();

                // Send email, but don't fail transaction if email fails (E4)
                try
                {
                    _emailService.SendTransferNotification(
                        (string)fromUserTable.Rows[0]["Email"],
                        amount,
                        (string)toUserTable.Rows[0]["Username"]);
                }
                catch
                {
                    // Log email failure, but transfer succeeded
                }

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
        if (amount <= 0 || amount > MaxDepositAmount)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * DepositInterestRate;

        string sql = "UPDATE Users SET Balance = Balance + @TotalAmount WHERE Id = @Id";
        var parameters = new Dictionary<string, object> 
        { 
            { "@TotalAmount", amount + interestBonus }, 
            { "@Id", userId } 
        };
        
        _db.ExecuteNonQuerySafe(sql, parameters);

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description, IDbTransaction? transaction = null)
    {
        string sql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                      VALUES (@FromId, @ToId, @Amount, @Type, 'Completed', @Description, GETDATE())";
        
        var parameters = new Dictionary<string, object>
        {
            { "@FromId", fromId },
            { "@ToId", toId },
            { "@Amount", amount },
            { "@Type", type },
            { "@Description", description ?? (object)DBNull.Value }
        };

        _db.ExecuteNonQuerySafe(sql, parameters, transaction);
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}
