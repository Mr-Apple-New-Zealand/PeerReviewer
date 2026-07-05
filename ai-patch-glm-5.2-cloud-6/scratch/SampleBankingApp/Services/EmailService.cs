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
    private const int DefaultSmtpPort = 587;

    private static readonly string NotificationEmail = "notifications@company.com";
    private static readonly string SupportEmail = "support@company.com";

    public EmailService(IConfiguration config)
    {
        _config = config;
    }

    private SmtpClient CreateSmtpClient()
    {
        var portString = _config["Email:SmtpPort"];
        int port = int.TryParse(portString, out int parsedPort) ? parsedPort : DefaultSmtpPort;

        return new SmtpClient(_config["Email:SmtpHost"])
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

        using var client = CreateSmtpClient();
        
        int attempt = 0;
        while (attempt < MaxRetries)
        {
            try
            {
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
        var body = $"Welcome, {username?.ToUpper() ?? "USER"}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   $"For support, email us at {SupportEmail}";

        using var message = new MailMessage(NotificationEmail, toEmail, WelcomeSubject, body);
        using var client = CreateSmtpClient();

        try
        {
            client.Send(message);
        }
        catch (SmtpException ex)
        {
            Console.WriteLine("Welcome email failed: " + ex.Message);
        }
    }
}
