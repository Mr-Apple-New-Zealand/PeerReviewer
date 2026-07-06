using System.Net;
using System.Net.Mail;

namespace SampleBankingApp.Services;

public class EmailService : IDisposable
{
    private readonly IConfiguration _config;
    private bool _disposed = false;

    private const string TransferSubject = "Transfer Notification - BankingApp";
    private const string WelcomeSubject = "Welcome to BankingApp!";
    private const string NotificationsEmail = "notifications@company.com";
    private const string SupportEmail = "support@company.com";

    private const int MaxRetries = 3;
    private const int SmtpTimeoutMs = 5000;

    public EmailService(IConfiguration config)
    {
        _config = config;
    }

    public void SendTransferNotification(string toEmail, decimal amount, string recipientName)
    {
        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";

        using var message = new MailMessage(NotificationsEmail, toEmail, TransferSubject, body);

        SendEmailWithRetry(message);
    }

    public void SendWelcomeEmail(string toEmail, string? username)
    {
        if (string.IsNullOrEmpty(username))
            username = "User";

        var body = $"Welcome, {username.ToUpperInvariant()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   "For support, email us at support@company.com";

        using var message = new MailMessage(NotificationsEmail, toEmail, WelcomeSubject, body);

        try
        {
            SendEmailWithRetry(message);
        }
        catch (SmtpException ex)
        {
            Console.WriteLine($"Welcome email failed: {ex.Message}");
        }
    }

    private void SendEmailWithRetry(MailMessage message)
    {
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
                Console.WriteLine($"Email attempt {attempt} failed: {ex.Message}");
                if (attempt >= MaxRetries)
                    throw;
            }
        }
    }

    private SmtpClient CreateSmtpClient()
    {
        var smtpHost = _config["Email:SmtpHost"] ?? "smtp.company.com";
        var smtpPort = int.TryParse(_config["Email:SmtpPort"], out int port) ? port : 587;
        var smtpUser = _config["Email:Username"] ?? "notifications@company.com";
        var smtpPass = _config["Email:Password"] ?? "__SET_VIA_ENV__";

        return new SmtpClient(smtpHost)
        {
            Port = smtpPort,
            Credentials = new NetworkCredential(smtpUser, smtpPass),
            EnableSsl = true,
            Timeout = SmtpTimeoutMs
        };
    }

    public void Dispose()
    {
        if (!_disposed)
        {
            _disposed = true;
        }
    }
}

