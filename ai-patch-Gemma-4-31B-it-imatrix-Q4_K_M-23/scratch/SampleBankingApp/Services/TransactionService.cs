using System.Data.SqlClient;
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

    private decimal GetFeeRate() => decimal.Parse(_config["TransactionSettings:FeeRate"] ?? "0.015");
    private decimal GetDepositCap() => decimal.Parse(_config["TransactionSettings:DepositCap"] ?? "1000000");

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
            return (false, "One or more users not found");

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * GetFeeRate(), 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= totalDebit)
        {
            using var connection = _db.GetOpenConnection();
            using var transaction = connection.BeginTransaction();
            try
            {
                var cmd1 = new SqlCommand("UPDATE Users SET Balance = Balance - @Debit WHERE Id = @Id", connection, transaction);
                cmd1.Parameters.AddWithValue("@Debit", totalDebit);
                cmd1.Parameters.AddWithValue("@Id", fromUserId);
                cmd1.ExecuteNonQuery();

                var cmd2 = new SqlCommand("UPDATE Users SET Balance = Balance + @Amount WHERE Id = @Id", connection, transaction);
                cmd2.Parameters.AddWithValue("@Amount", amount);
                cmd2.Parameters.AddWithValue("@Id", toUserId);
                cmd2.ExecuteNonQuery();

                RecordTransaction(fromUserId, toUserId, amount, "Transfer", description, connection, transaction);
                
                transaction.Commit();
            }
            catch
            {
                transaction.Rollback();
                return (false, "Database error during transfer");
            }

            try
            {
                _emailService.SendTransferNotification(
                    (string)fromUserTable.Rows[0]["Email"],
                    amount,
                    (string)toUserTable.Rows[0]["Username"]);
            }
            catch (Exception ex)
            {
                // Log email failure but don't fail the transaction
                Console.WriteLine($"Notification failed: {ex.Message}");
            }

            return (true, "Transfer successful");
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > GetDepositCap())
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.01m;

        _db.ExecuteNonQuery(
            "UPDATE Users SET Balance = Balance + @Total WHERE Id = @Id", 
            new Dictionary<string, object> { { "@Total", amount + interestBonus }, { "@Id", userId } });

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description, SqlConnection? conn = null, SqlTransaction? trans = null)
    {
        string sql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES (@From, @To, @Amount, @Type, 'Completed', @Desc, GETDATE())";
        
        if (conn != null && trans != null)
        {
            using var cmd = new SqlCommand(sql, conn, trans);
            cmd.Parameters.AddWithValue("@From", fromId);
            cmd.Parameters.AddWithValue("@To", toId);
            cmd.Parameters.AddWithValue("@Amount", amount);
            cmd.Parameters.AddWithValue("@Type", type);
            cmd.Parameters.AddWithValue("@Desc", (object?)description ?? DBNull.Value);
            cmd.ExecuteNonQuery();
        }
        else
        {
            _db.ExecuteNonQuery(sql, new Dictionary<string, object> {
                { "@From", fromId }, { "@To", toId }, { "@Amount", amount }, { "@Type", type }, { "@Desc", (object?)description ?? DBNull.Value }
            });
        }
    }

    public void RefundTransaction(int transactionId)
    {
        throw new NotImplementedException();
    }
}
