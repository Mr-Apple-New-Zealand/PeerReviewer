namespace SampleBankingApp.Models;

public class Transaction
{
    public int Id { get; set; }
    public int FromUserId { get; set; }
    public int ToUserId { get; set; }
    public decimal Amount { get; set; }
    public string Type { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
}

public class TransferRequest
{
    public int ToUserId { get; set; }
    public decimal Amount { get; set; }
    public string? Description { get; set; }
}

public class DepositRequest
{
    public decimal Amount { get; set; }
}
