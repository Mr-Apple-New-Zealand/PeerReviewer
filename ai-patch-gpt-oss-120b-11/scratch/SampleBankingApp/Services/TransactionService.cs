using SampleBankingApp.Data;
using SampleBankingApp.Models;
using System.Data;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const decimal DepositInterestRate = 0.01m; // 1% interest on deposits
    private const decimal DepositCap = 1_000_000m;

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
            return (false, "Amount must be greater than zero");

        if (fromUserId == toUserId)
            return (false, "Self‑transfer is not allowed");

        // Load both users in a single transaction to guarantee consistency
        using var connection = _db.GetOpenConnection();
        using var transaction = connection.BeginTransaction();

        try
        {
            var fromUser = GetUserById(connection, transaction, fromUserId);
            var toUser = GetUserById(connection, transaction, toUserId);

            if (fromUser == null || toUser == null)
                return (false, "One or both users not found");

            decimal fee = Math.Round(amount * TransactionFeeRate, 2);
            decimal totalDebit = amount + fee;

            if (fromUser.Balance < totalDebit)
                return (false, "Insufficient funds (including transaction fee)");

            // Perform balance updates
            UpdateUserBalance(connection, transaction, fromUserId, fromUser.Balance - totalDebit);
            UpdateUserBalance(connection, transaction, toUserId, toUser.Balance + amount);

            // Record transaction
            RecordTransaction(connection, transaction, fromUserId, toUserId, amount, "Transfer", description);

            transaction.Commit();

            // Send notification – swallow any email errors so the transfer still succeeds
            try
            {
                _emailService.SendTransferNotification(
                    fromUser.Email,
                    amount,
                    toUser.Username);
            }
            catch
            {
                // Log internally if needed; do not surface to caller
            }

            return (true, "Transfer successful");
        }
        catch
        {
            transaction.Rollback();
            return (false, "Transfer failed due to an internal error");
        }
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > DepositCap)
            return (false, "Invalid deposit amount");

        decimal interestBonus = Math.Round(amount * DepositInterestRate, 2);

        using var connection = _db.GetOpenConnection();
        using var transaction = connection.BeginTransaction();

        try
        {
            var user = GetUserById(connection, transaction, userId);
            if (user == null)
                return (false, "User not found");

            UpdateUserBalance(connection, transaction, userId, user.Balance + amount + interestBonus);
            RecordTransaction(connection, transaction, 0, userId, amount, "Deposit", null);

            transaction.Commit();
            return (true, "Deposit successful");
        }
        catch
        {
            transaction.Rollback();
            return (false, "Deposit failed due to an internal error");
        }
    }

    private User? GetUserById(SqlConnection connection, SqlTransaction transaction, int userId)
    {
        const string sql = "SELECT Id, Username, Email, Balance FROM Users WHERE Id = @Id";
        using var cmd = new SqlCommand(sql, connection, transaction);
        cmd.Parameters.AddWithValue("@Id", userId);
        using var reader = cmd.ExecuteReader();
        if (!reader.Read())
            return null;

        return new User
        {
            Id = (int)reader["Id"],
            Username = (string)reader["Username"],
            Email = (string)reader["Email"],
            Balance = (decimal)reader["Balance"]
        };
    }

    private void UpdateUserBalance(SqlConnection connection, SqlTransaction transaction, int userId, decimal newBalance)
    {
        const string sql = "UPDATE Users SET Balance = @Balance WHERE Id = @Id";
        using var cmd = new SqlCommand(sql, connection, transaction);
        cmd.Parameters.AddWithValue("@Balance", newBalance);
        cmd.Parameters.AddWithValue("@Id", userId);
        cmd.ExecuteNonQuery();
    }

    private void RecordTransaction(SqlConnection connection, SqlTransaction transaction,
        int fromId, int toId, decimal amount, string type, string? description)
    {
        const string sql = @"INSERT INTO Transactions
                            (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                            VALUES (@FromId, @ToId, @Amount, @Type, 'Completed', @Description, GETDATE())";

        using var cmd = new SqlCommand(sql, connection, transaction);
        cmd.Parameters.AddWithValue("@FromId", fromId);
        cmd.Parameters.AddWithValue("@ToId", toId);
        cmd.Parameters.AddWithValue("@Amount", amount);
        cmd.Parameters.AddWithValue("@Type", type);
        cmd.Parameters.AddWithValue("@Description", (object?)description ?? DBNull.Value);
        cmd.ExecuteNonQuery();
    }

    public void RefundTransaction(int transactionId)
    {
        // TODO: implement
        throw new NotImplementedException();
    }
}
