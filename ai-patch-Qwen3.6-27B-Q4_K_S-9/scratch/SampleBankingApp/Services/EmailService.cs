using System.Net;
using System.Net.Mail;

namespace SampleBankingApp.Services;

public class EmailService
{
    private readonly IConfiguration _config;

    private const string TransferSubject = "Transfer Notification - BankingApp";
    private const string WelcomeSubject  = "Welcome to BankingApp!";
    private const string DefaultFromAddress = "notifications@company.com";
    private const string SupportAddress = "support@company.com";

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

        using var message = new MailMessage(
            from: DefaultFromAddress,
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
                // Log instead of Console.WriteLine
                if (attempt >= MaxRetries)
                    throw;
            }
        }
    }

    public void SendWelcomeEmail(string toEmail, string username)
    {
        if (string.IsNullOrEmpty(username))
            throw new ArgumentException("Username cannot be null or empty", nameof(username));

        var body = $"Welcome, {username.ToUpper()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   $"For support, email us at {SupportAddress}";

        using var message = new MailMessage(DefaultFromAddress, toEmail, WelcomeSubject, body);
        using var client = CreateSmtpClient();

        try
        {
            client.Send(message);
        }
        catch (SmtpException ex)
        {
            // Log specific SMTP error
            throw;
        }
        catch (Exception ex)
        {
            // Log general error
            throw;
        }
    }

    private SmtpClient CreateSmtpClient()
    {
        var host = _config["Email:SmtpHost"];
        var portStr = _config["Email:SmtpPort"];
        var username = _config["Email:Username"];
        var password = _config["Email:Password"];

        int port = 25;
        if (!string.IsNullOrEmpty(portStr))
        {
            int.TryParse(portStr, out port);
        }

        return new SmtpClient(host)
        {
            Port = port,
            Credentials = new NetworkCredential(username, password),
            EnableSsl = true, // Default to true for security, or read from config
            Timeout = SmtpTimeoutMs
        };
    }
}
