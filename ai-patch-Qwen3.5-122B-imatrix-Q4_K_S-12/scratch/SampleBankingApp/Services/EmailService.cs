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
        if (string.IsNullOrEmpty(toEmail)) return;

        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";

        var fromAddress = _config["Email:FromAddress"] ?? "notifications@company.com";

        using var message = new MailMessage(fromAddress, toEmail, TransferSubject, body);

        using var smtpClient = new SmtpClient(_config["Email:SmtpHost"])
        {
            Port = int.Parse(_config["Email:SmtpPort"] ?? "25"),
            Credentials = new NetworkCredential(
                _config["Email:Username"] ?? string.Empty,
                _config["Email:Password"] ?? string.Empty
            ),
            EnableSsl = true,
            Timeout = SmtpTimeoutMs
        };

        int attempt = 0;
        while (attempt < MaxRetries)
        {
            try
            {
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
        if (string.IsNullOrEmpty(toEmail) || string.IsNullOrEmpty(username)) return;

        var body = $"Welcome, {username.ToUpper()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   "For support, email us at support@company.com";

        var fromAddress = _config["Email:FromAddress"] ?? "notifications@company.com";

        using var message = new MailMessage(fromAddress, toEmail, WelcomeSubject, body);

        using var smtpClient = new SmtpClient(_config["Email:SmtpHost"])
        {
            Port = int.Parse(_config["Email:SmtpPort"] ?? "25"),
            Credentials = new NetworkCredential(
                _config["Email:Username"] ?? string.Empty,
                _config["Email:Password"] ?? string.Empty
            ),
            EnableSsl = true,
            Timeout = SmtpTimeoutMs
        };

        try
        {
            smtpClient.Send(message);
        }
        catch (SmtpException ex)
        {
            Console.WriteLine("Welcome email failed: " + ex.Message);
        }
        catch (Exception ex)
        {
            // Log specific programming errors but do not expose to caller
            Console.WriteLine("Unexpected error sending email: " + ex.GetType().Name);
        }
    }
}
