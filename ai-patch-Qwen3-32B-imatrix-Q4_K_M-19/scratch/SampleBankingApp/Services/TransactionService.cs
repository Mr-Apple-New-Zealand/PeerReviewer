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

    public (bool Success, string Message) Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount <= 0)
            return (false, "Amount must be positive");

        if (fromUserId == toUserId)
            return (false, "Cannot transfer to yourself");

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

            decimal fee = Math.Round(amount * _config.GetValue<decimal>("Transaction:FeeRate"), 2);
            decimal totalDebit = amount + fee;

            if (fromBalance < totalDebit)
                return (false, "Insufficient funds");

            using var connection = _db.GetOpenConnection();
            using var transaction = connection.BeginTransaction();

            try
            {
                var newFromBalance = fromBalance - totalDebit;
                var newToBalance = toBalance + amount;

                _db.ExecuteNonQuery(
                    "UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                    new Dictionary<string, object> { 
                        { "@Balance", newFromBalance }, 
                        { "@Id", fromUserId } },
                    connection,
                    transaction);

                _db.ExecuteNonQuery(
                    "UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                    new Dictionary<string, object> { 
                        { "@Balance", newToBalance }, 
                        { "@Id", toUserId } },
                    connection,
                    transaction);

                RecordTransaction(fromUserId, toUserId, amount, "Transfer", description, connection, transaction);

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
        catch (Exception ex)
        {
            // Log exception but don't expose details
            return (false, "An error occurred during the transfer");
        }
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > _config.GetValue<decimal>("Transaction:MaxDeposit"))
            return (false, "Invalid deposit amount");

        try
        {
            var userTable = _db.ExecuteQuerySafe(
                "SELECT * FROM Users WHERE Id = @Id",
                new Dictionary<string, object> { { "@Id", userId } });

            if (userTable.Rows.Count == 0)
                return (false, "User not found");

            decimal interestBonus = amount * _config.GetValue<decimal>("Transaction:InterestRate");

            _db.ExecuteNonQuery(
                "UPDATE Users SET Balance = Balance + @Amount WHERE Id = @Id",
                new Dictionary<string, object> { 
                    { "@Amount", amount + interestBonus }, 
                    { "@Id", userId } });

            RecordTransaction(0, userId, amount, "Deposit", null);
            return (true, "Deposit successful");
        }
        catch (Exception ex)
        {
            // Log exception but don't expose details
            return (false, "An error occurred during the deposit");
        }
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description, SqlConnection? connection = null, SqlTransaction? transaction = null)
    {
        string sql = "INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt) " +
                     "VALUES (@FromUserId, @ToUserId, @Amount, @Type, @Status, @Description, GETDATE())";

        var parameters = new Dictionary<string, object>
        {
            { "@FromUserId", fromId },
            { "@ToUserId", toId },
            { "@Amount", amount },
            { "@Type", type },
            { "@Status", "Completed" },
            { "@Description", description ?? string.Empty }
        };

        if (connection != null)
        {
            _db.ExecuteNonQuery(sql, parameters, connection, transaction);
        }
        else
        {
            _db.ExecuteNonQuery(sql, parameters);
        }
    }
}
