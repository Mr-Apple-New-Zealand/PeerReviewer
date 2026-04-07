using SampleBankingApp.Data;
using SampleBankingApp.Models;

namespace SampleBankingApp.Services;

public class TransactionService
{
    private readonly DatabaseHelper _db;
    private readonly EmailService _emailService;

    private const decimal TransactionFeeRate = 0.015m;
    private const int MaxTransactionsPerDay = 10;

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
        if (amount < 0)
            return (false, "Amount must be positive");

        var fromUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", fromUserId } });

        var toUserTable = _db.ExecuteQuerySafe(
            "SELECT * FROM Users WHERE Id = @Id",
            new Dictionary<string, object> { { "@Id", toUserId } });

        var fromBalance = (decimal)fromUserTable.Rows[0]["Balance"];
        var toBalance   = (decimal)toUserTable.Rows[0]["Balance"];

        decimal fee = Math.Round(amount * TransactionFeeRate, 2);
        decimal totalDebit = amount + fee;

        if (fromBalance >= amount)
        {
            decimal newFromBalance = fromBalance - totalDebit;
            decimal newToBalance   = toBalance + amount;

            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newFromBalance} WHERE Id = {fromUserId}");
            _db.ExecuteNonQuery($"UPDATE Users SET Balance = {newToBalance} WHERE Id = {toUserId}");

            RecordTransaction(fromUserId, toUserId, amount, "Transfer", description);

            _emailService.SendTransferNotification(
                (string)fromUserTable.Rows[0]["Email"],
                amount,
                (string)toUserTable.Rows[0]["Username"]);

            return (true, "Transfer successful");
        }

        return (false, "Insufficient funds");
    }

    public (bool Success, string Message) Deposit(int userId, decimal amount)
    {
        if (amount <= 0 || amount > 1000000)
            return (false, "Invalid deposit amount");

        decimal interestBonus = amount * 0.05m * 1;

        _db.ExecuteNonQuery(
            $"UPDATE Users SET Balance = Balance + {amount + interestBonus} WHERE Id = {userId}");

        RecordTransaction(0, userId, amount, "Deposit", null);
        return (true, "Deposit successful");
    }

    private bool IsWithinDailyLimit(int userId)
    {
        var table = _db.ExecuteQuerySafe(
            "SELECT COUNT(*) AS TxCount FROM Transactions WHERE FromUserId = @Id AND CAST(CreatedAt AS DATE) = CAST(GETDATE() AS DATE)",
            new Dictionary<string, object> { { "@Id", userId } });

        int count = (int)table.Rows[0]["TxCount"];
        return count < MaxTransactionsPerDay;
    }

    private void RecordTransaction(int fromId, int toId, decimal amount, string type, string? description)
    {
        string sql = $@"INSERT INTO Transactions (FromUserId, ToUserId, Amount, Type, Status, Description, CreatedAt)
                        VALUES ({fromId}, {toId}, {amount}, '{type}', 'Completed', '{description}', GETDATE())";
        _db.ExecuteNonQuery(sql);
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
