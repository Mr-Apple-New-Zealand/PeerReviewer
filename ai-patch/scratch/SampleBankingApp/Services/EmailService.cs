using System.Net;
using System.Net.Mail;
namespace SampleBankingApp.Services;
public class EmailService
{
    private readonly IConfiguration _config;
    private readonly ILogger<EmailService> _logger;
    private const string TransferSubject = "Transfer Notification - BankingApp";
    private const string WelcomeSubject = "Welcome to BankingApp!";
    private const int MaxRetries = 3;
    private const int SmtpTimeoutMs = 5000;
    public EmailService(IConfiguration config, ILogger<EmailService> logger)
    {
        _config = config;
        _logger = logger;
    }
    public void SendTransferNotification(string toEmail, decimal amount, string recipientName)
    {
        var fromAddress = _config["Email:FromAddress"] ?? "notifications@company.com";
        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";
        using var message = new MailMessage(
            from: fromAddress,
            to: toEmail,
            subject: TransferSubject,
            body: body);
        int attempt = 0;
        while (attempt < MaxRetries)
        {
            try
            {
                using var smtpClient = CreateSmtpClient();
                smtpClient.Send(message);
                return;
            }
            catch (SmtpException ex)
            {
                attempt++;
                _logger.LogWarning(ex, "Transfer notification attempt {Attempt} of {Max} failed", attempt, MaxRetries);
                if (attempt >= MaxRetries)
                    throw;
            }
        }
    }
    public void SendWelcomeEmail(string toEmail, string username)
    {
        if (username == null) throw new ArgumentNullException(nameof(username));
        var fromAddress = _config["Email:FromAddress"] ?? "notifications@company.com";
        var supportAddress = _config["Email:SupportAddress"] ?? "support@company.com";
        var body = $"Welcome, {username.ToUpper()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   $"For support, email us at {supportAddress}";
        using var message = new MailMessage(fromAddress, toEmail, WelcomeSubject, body);
        try
        {
            using var smtpClient = CreateSmtpClient();
            smtpClient.Send(message);
        }
        catch (SmtpException ex)
        {
            _logger.LogError(ex, "Failed to send welcome email to {Email}", toEmail);
        }
    }
    private SmtpClient CreateSmtpClient()
    {
        return new SmtpClient(_config["Email:SmtpHost"])
        {
            Port = int.Parse(_config["Email:SmtpPort"] ?? "587"),
            Credentials = new NetworkCredential(
                _config["Email:Username"],
                _config["Email:Password"]),
            EnableSsl = true,
            Timeout = SmtpTimeoutMs
        };
    }
}
