using System.Net;
using System.Net.Mail;

namespace SampleBankingApp.Services;

public class EmailService
{
    private readonly IConfiguration _config;

    private const string TransferSubject = "Transfer Notification - BankingApp";
    private const string WelcomeSubject  = "Welcome to BankingApp!";
    private const string NotificationEmail = "notifications@company.com";
    private const string SupportEmail = "support@company.com";

    private const int MaxRetries = 3;
    private const int SmtpTimeoutMs = 5000;

    public EmailService(IConfiguration config)
    {
        _config = config;
    }

    private SmtpClient CreateSmtpClient()
    {
        var host = _config["Email:SmtpHost"] ?? throw new InvalidOperationException("SmtpHost missing");
        var portStr = _config["Email:SmtpPort"];
        if (!int.TryParse(portStr, out int port)) port = 587;

        return new SmtpClient(host)
        {
            Port = port,
            Credentials = new NetworkCredential(
                _config["Email:Username"],
                _config["Email:Password"]
            ),
            EnableSsl = true,
            Timeout = SmtpTimeoutMs
        };
    }

    public void SendTransferNotification(string toEmail, decimal amount, string recipientName)
    {
        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";

        using var message = new MailMessage(
            from: NotificationEmail,
            to: toEmail,
            subject: TransferSubject,
            body: body);

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
                if (attempt >= MaxRetries) throw;
            }
        }
    }

    public void SendWelcomeEmail(string toEmail, string username)
    {
        if (username == null) return;

        var body = $"Welcome, {username.ToUpper()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   $"For support, email us at {SupportEmail}";

        using var message = new MailMessage(NotificationEmail, toEmail, WelcomeSubject, body);

        try
        {
            using var client = CreateSmtpClient();
            client.Send(message);
        }
        catch (SmtpException ex)
        {
            Console.WriteLine("Welcome email failed: " + ex.Message);
        }
    }
}
