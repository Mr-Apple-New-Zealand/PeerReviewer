using System.Net;
using System.Net.Mail;

namespace SampleBankingApp.Services;

public class EmailService
{
    private readonly IConfiguration _config;

    private const string TransferSubject = "Transfer Notification - BankingApp";
    private const string WelcomeSubject = "Welcome to BankingApp!";

    private const int MaxRetries = 3;
    private const int SmtpTimeoutMs = 5000;

    public EmailService(IConfiguration config)
    {
        _config = config;

        var smtpHost = _config["Email:SmtpHost"] ?? "smtp.company.com";
        var smtpPort = int.Parse(_config["Email:SmtpPort"] ?? "587");
        var username = _config["Email:Username"] ?? "notifications@company.com";
        var password = _config["Email:Password"] ?? "EmailPass99";

        _smtpClient = new SmtpClient(smtpHost)
        {
            Port = smtpPort,
            Credentials = new NetworkCredential(username, password),
            EnableSsl = true,
            Timeout = SmtpTimeoutMs
        };
    }

    public void SendTransferNotification(string toEmail, decimal amount, string recipientName)
    {
        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";

        var message = new MailMessage(
            from: "notifications@company.com",
            to: toEmail,
            subject: TransferSubject,
            body: body);

        int attempt = 0;
        while (attempt < MaxRetries)
        {
            try
            {
                using var smtp = new SmtpClient(_config["Email:SmtpHost"] ?? "smtp.company.com")
                {
                    Port = int.Parse(_config["Email:SmtpPort"] ?? "587"),
                    Credentials = new NetworkCredential(
                        _config["Email:Username"] ?? "notifications@company.com",
                        _config["Email:Password"] ?? "EmailPass99"),
                    EnableSsl = true,
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

    public void SendWelcomeEmail(string toEmail, string username)
    {
        var body = $"Welcome, {username}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   "For support, email us at support@company.com";

        var message = new MailMessage("notifications@company.com", toEmail, WelcomeSubject, body);

        try
        {
            using var smtp = new SmtpClient(_config["Email:SmtpHost"] ?? "smtp.company.com")
            {
                Port = int.Parse(_config["Email:SmtpPort"] ?? "587"),
                Credentials = new NetworkCredential(
                    _config["Email:Username"] ?? "notifications@company.com",
                    _config["Email:Password"] ?? "EmailPass99"),
                EnableSsl = true,
                Timeout = SmtpTimeoutMs
            };
            smtp.Send(message);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Welcome email failed: " + ex.Message);
        }
    }
}
