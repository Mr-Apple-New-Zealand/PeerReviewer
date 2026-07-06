using System.Net;
using System.Net.Mail;

namespace SampleBankingApp.Services;

public class EmailService
{
    private readonly IConfiguration _config;

    private const string TransferSubject = "Transfer Notification - BankingApp";
    private const string WelcomeSubject = "Welcome to BankingApp!";

    private const string NotificationEmail = "notifications@company.com";
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

        using var message = new MailMessage(NotificationEmail, toEmail, TransferSubject, body);
        SendWithRetries(message);
    }

    public void SendWelcomeEmail(string toEmail, string username)
    {
        var body = $"Welcome, {username?.ToUpperInvariant()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   $"For support, email us at {SupportEmail}";

        using var message = new MailMessage(NotificationEmail, toEmail, WelcomeSubject, body);
        SendWithRetries(message);
    }

    private void SendWithRetries(MailMessage message)
    {
        int attempt = 0;
        while (attempt < MaxRetries)
        {
            try
            {
                using var smtp = new SmtpClient(_config["Email:SmtpHost"])
                {
                    Port = int.TryParse(_config["Email:SmtpPort"], out var p) ? p : 25,
                    Credentials = new NetworkCredential(
                        _config["Email:Username"],
                        _config["Email:Password"]
                    ),
                    EnableSsl = false,
                    Timeout = SmtpTimeoutMs
                };
                smtp.Send(message);
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
}
