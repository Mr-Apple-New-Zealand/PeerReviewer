using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;
    private const decimal DepositCap = 1_000_000m;
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

        using var connection = new SqlConnection(_db.GetOpenConnection().ConnectionString);
        connection.Open();

        using var transaction = connection.BeginTransaction();
        try
        {
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
                decimal newFromBalance = fromBalance - totalDebit;
                decimal newToBalance = toBalance + amount;

                using var cmd1 = new SqlCommand(
                    "UPDATE Users SET Balance = @Balance WHERE Id = @Id", connection, transaction);
                cmd1.Parameters.AddWithValue("@Balance", newFromBalance);
                cmd1.Parameters.AddWithValue("@Id", fromUserId);
                cmd1.ExecuteNonQuery();

                using var cmd2 = new SqlCommand(
                    "UPDATE Users SET Balance = @Balance WHERE Id = @Id", connection, transaction);
                cmd2.Parameters.AddWithValue("@Balance", newToBalance);
                cmd2.Parameters.AddWithValue("@Id", toUserId);
                cmd2.ExecuteNonQuery();

                RecordTransaction(fromUserId, toUserId, amount, "Transfer", description, connection, transaction);

                try
                {
                    _emailService.SendTransferNotification(
                        (string)fromUserTable.Rows[0]["Email"],
                        amount,
                        (string)toUserTable.Rows[0]["Username"]);
                }
                catch
                {
                    // Log and continue; transfer already committed
                }

                transaction.Commit();
                return (true, "Transfer successful");
            }

            transaction.Rollback();
            return (false, "Insufficient funds");
        }
        catch
        {
            transaction.Rollback();
            return (false, "Transfer failed");
        }
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > DepositCap)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * DepositInterestRate;

        using var connection = new SqlConnection(_db.GetOpenConnection().ConnectionString);
        connection.Open();

        using var transaction = connection.BeginTransaction();
        try
        {
            using var cmd = new SqlCommand(
                "UPDATE Users SET Balance = Balance + @Amount + @Interest WHERE Id = @Id", connection, transaction);
            cmd.Parameters.AddWithValue("@Amount", amount);
            cmd.Parameters.AddWithValue("@Interest", interestBonus);
            cmd.Parameters.AddWithValue("@Id", userId);
            cmd.ExecuteNonQuery();

            RecordTransaction(0, userId, amount, "Deposit", null, connection, transaction);
            transaction.Commit();
            return (true, "Deposit successful");
        }
        catch
        {
            transaction.Rollback();
            return (false, "Deposit failed");
        }
    }

    private bool IsWithinDailyLimit(int userId)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT COUNT(*) AS TxCount FROM Transactions WHERE FromUserId = @Id AND CAST(CreatedAt AS DATE) = CAST(GETDATE() AS DATE)",
            new Dictionary<string, object> { { "@Id", userId } });

        if (table.Rows.Count == 0)
            return true;

        int count = (int)table.Rows[0]["TxCount"];
        return count < MaxTransactionsPerDay;
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description, SqlConnection connection, SqlTransaction transaction)
    {
        using var cmd = new SqlCommand(
            @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
              VALUES (@FromId, @ToId, @Amount, @Type, 'Completed', @Description, GETDATE())", connection, transaction);
        cmd.Parameters.AddWithValue("@FromId", fromId);
        cmd.Parameters.AddWithValue("@ToId", toId);
        cmd.Parameters.AddWithValue("@Amount", amount);
        cmd.Parameters.AddWithValue("@Type", type);
        cmd.Parameters.AddWithValue("@Description", description ?? string.Empty);
        cmd.ExecuteNonQuery();
    }

    private string FormatCurrency(decimal amount)
    {
        return $"${amount:F2}";
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}

