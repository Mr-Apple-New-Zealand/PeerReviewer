using System.Net;
using System.Net.Mail;

namespace SampleBankingApp.Services;

public class EmailService
{
    private readonly IConfiguration _config;

    private const string TransferSubject = "Transfer Notification - BankingApp";
    private const string WelcomeSubject  = "Welcome to BankingApp!";

    private const int MaxRetries = 3;
    private const int SmtpTimeoutMs = 5000;
    private const int DefaultSmtpPort = 25;

    private const string NotificationsAddress = "notifications@company.com";
    private const string SupportAddress = "support@company.com";

    public EmailService(IConfiguration config)
    {
        _config = config;
    }

    public void SendTransferNotification(string toEmail, decimal amount, string recipientName)
    {
        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";

        using var message = new MailMessage(NotificationsAddress, toEmail, TransferSubject, body);

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

    public void SendWelcomeEmail(string toEmail, string username)
    {
        var body = $"Welcome, {(username ?? string.Empty).ToUpper()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   $"For support, email us at {SupportAddress}";

        using var message = new MailMessage(NotificationsAddress, toEmail, WelcomeSubject, body);

        try
        {
            using var smtpClient = CreateSmtpClient();
            smtpClient.Send(message);
        }
        catch (SmtpException ex)
        {
            Console.WriteLine("Welcome email failed: " + ex.Message);
        }
    }

    private SmtpClient CreateSmtpClient()
    {
        var portString = _config["Email:SmtpPort"];
        int port = int.TryParse(portString, out var parsedPort) ? parsedPort : DefaultSmtpPort;

        return new SmtpClient(_config["Email:SmtpHost"] ?? string.Empty)
        {
            Port = port,
            Credentials = new NetworkCredential(
                _config["Email:Username"] ?? string.Empty,
                _config["Email:Password"] ?? string.Empty
            ),
            EnableSsl = false,
            Timeout = SmtpTimeoutMs
        };
    }
}
