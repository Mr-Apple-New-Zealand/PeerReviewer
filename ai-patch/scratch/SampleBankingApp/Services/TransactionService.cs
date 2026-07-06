using System.Data;
using SampleBankingApp.Data;
using SampleBankingApp.Models;
namespace SampleBankingApp.Services;
public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;
    private readonly ILogger<TransactionService> _logger;
    private readonly decimal _transactionFeeRate;
    private readonly int _maxTransactionsPerDay;
    private readonly decimal _maxDepositAmount;
    private readonly decimal _depositBonusRate;
    public TransactionService(
        DatabaseHelper db,
        EmailService emailService,
        IConfiguration config,
        ILogger<TransactionService> logger)
    {
        _db = db;
        _emailService = emailService;
        _logger = logger;
        _transactionFeeRate = config.GetValue<decimal>("Transaction:FeeRate", 0.015m);
        _maxTransactionsPerDay = config.GetValue<int>("Transaction:MaxPerDay", 10);
        _maxDepositAmount = config.GetValue<decimal>("Transaction:MaxDepositAmount", 1_000_000m);
        _depositBonusRate = config.GetValue<decimal>("Transaction:DepositBonusRate", 0.01m);
    }
    public (bool Success, string Message) Transfer(int fromUserId, int toUserId, decimal amount, string? description)
    {
        if (amount <= 0)
            return (false, "Amount must be positive");
        if (!IsWithinDailyLimit(fromUserId))
            return (false, "Daily transaction limit reached");
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
        var toBalance = (decimal)toUserTable.Rows[0]["Balance"];
        decimal fee = Math.Round(amount * _transactionFeeRate, 2);
        decimal totalDebit = amount + fee;
        if (fromBalance < totalDebit)
            return (false, "Insufficient funds");
        decimal newFromBalance = fromBalance - totalDebit;
        decimal newToBalance = toBalance + amount;
        const string insertSql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                                   VALUES (@FromUserId, @ToUserId, @Amount, @Type, 'Completed', @Description, GETDATE())";
        var batchCommands = new List<(string Sql, Dictionary<string, object?>? Parameters)>
        {
            (
                "UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                new Dictionary<string, object?> { { "@Balance", newFromBalance }, { "@Id", fromUserId } }
            ),
            (
                "UPDATE Users SET Balance = @Balance WHERE Id = @Id",
                new Dictionary<string, object?> { { "@Balance", newToBalance }, { "@Id", toUserId } }
            ),
            (
                insertSql,
                new Dictionary<string, object?>
                {
                    { "@FromUserId", fromUserId },
                    { "@ToUserId", toUserId },
                    { "@Amount", amount },
                    { "@Type", "Transfer" },
                    { "@Description", (object?)description ?? DBNull.Value }
                }
            )
        };
        _db.ExecuteNonQueryBatch(batchCommands);
        try
        {
            _emailService.SendTransferNotification(
                (string)fromUserTable.Rows[0]["Email"],
                amount,
                (string)toUserTable.Rows[0]["Username"]);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Transfer notification failed for user {UserId}; transfer itself succeeded", fromUserId);
        }
        return (true, "Transfer successful");
    }
    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > _maxDepositAmount)
            return (false, "Invalid deposit amount");
        decimal interestBonus = Math.Round(amount * _depositBonusRate, 2);
        _db.ExecuteNonQuery(
            "UPDATE Users SET Balance = Balance + @Amount WHERE Id = @UserId",
            new Dictionary<string, object?> { { "@Amount", amount + interestBonus }, { "@UserId", userId } });
        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }
    private bool IsWithinDailyLimit(int userId)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT COUNT(*) AS TxCount FROM Transactions WHERE FromUserId = @Id AND CAST(CreatedAt AS DATE) = CAST(GETDATE() AS DATE)",
            new Dictionary<string, object> { { "@Id", userId } });
        int count = (int)table.Rows[0]["TxCount"];
        return count < _maxTransactionsPerDay;
    }
    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        const string sql = @"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                              VALUES (@FromUserId, @ToUserId, @Amount, @Type, 'Completed', @Description, GETDATE())";
        _db.ExecuteNonQuery(sql, new Dictionary<string, object?>
        {
            { "@FromUserId", fromId },
            { "@ToUserId", toId },
            { "@Amount", amount },
            { "@Type", type },
            { "@Description", (object?)description ?? DBNull.Value }
        });
    }
    public void RefundTransaction(int transactionId)
    {
        throw new NotImplementedException();
    }
}
