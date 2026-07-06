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

    private readonly SmtpClient _smtpClient;

    public EmailService(IConfiguration config)
    {
        _config = config;

        _smtpClient = new SmtpClient(_config["Email:SmtpHost"])
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
                _smtpClient.Send(message);
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
        var body = $"Welcome, {username.ToUpper()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   "For support, email us at support@company.com";

        var message = new MailMessage("notifications@company.com", toEmail, WelcomeSubject, body);

        try
        {
            _smtpClient.Send(message);
        }
        catch (Exception ex)
        {
            Console.WriteLine("Welcome email failed: " + ex.Message);
        }
    }

    private string BuildHtmlTemplate(string title, string body)
    {
        return $"<html><body><h1>{title}</h1><p>{body}</p></body></html>";
    }

    public void SendWelcomeEmailHtml(string toEmail, string username)
    {
        var htmlBody = BuildHtmlTemplate("Welcome!", $"Hello {username}, welcome to BankingApp.");
        var message = new MailMessage("notifications@company.com", toEmail, WelcomeSubject, htmlBody);
        message.IsBodyHtml = true;
        _smtpClient.Send(message);
    }
}
