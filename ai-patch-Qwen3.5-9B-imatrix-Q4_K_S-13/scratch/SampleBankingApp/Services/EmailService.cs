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

    public EmailService(IConfiguration config)
    {
        _config = config;
    }

    public void SendTransferNotification(string toEmail, decimal amount, string recipientName)
    {
        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";

        var message = new MailMessage
        {
            From = new MailAddress("notifications@company.com"),
            To = { new MailAddress(toEmail) },
            Subject = TransferSubject,
            Body = body
        };

        int attempt = 0;
        while (attempt < MaxRetries)
        {
            try
            {
                using var client = CreateSmtpClient();
                client.Send(message);
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
        if (string.IsNullOrEmpty(username))
            username = "User";

        var body = $"Welcome, {username.ToUpper()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   "For support, email us at support@company.com";

        var message = new MailMessage
        {
            From = new MailAddress("notifications@company.com"),
            To = { new MailAddress(toEmail) },
            Subject = WelcomeSubject,
            Body = body
        };

        try
        {
            using var client = CreateSmtpClient();
            client.Send(message);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Welcome email failed: " + ex.Message);
        }
    }

    private SmtpClient CreateSmtpClient()
    {
        return new SmtpClient(_config["Email:SmtpHost"])
        {
            Port = int.Parse(_config["Email:SmtpPort"] ?? "25"),
            Credentials = new NetworkCredential(
                _config["Email:Username"],
                _config["Email:Password"]
            ),
            EnableSsl = false,
            Timeout = SmtpTimeoutMs
        };
    }
}
