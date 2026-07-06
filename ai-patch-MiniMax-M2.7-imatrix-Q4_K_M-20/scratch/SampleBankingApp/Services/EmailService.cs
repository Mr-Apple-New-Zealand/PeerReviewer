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
        _config = config ?? throw new ArgumentNullException(nameof(config));
    }

    public void SendTransferNotification(string? toEmail, decimal amount, string? recipientName)
    {
        if (string.IsNullOrEmpty(toEmail))
            return;

        var fromAddress = GetFromAddress();
        
        using var message = new MailMessage
        {
            From = new MailAddress(fromAddress),
            Subject = TransferSubject,
            Body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately."
        };
        message.To.Add(toEmail);

        SendWithRetry(message);
    }

    public void SendWelcomeEmail(string? toEmail, string? username)
    {
        if (string.IsNullOrEmpty(toEmail) || string.IsNullOrEmpty(username))
            return;

        var fromAddress = GetFromAddress();
        
        using var message = new MailMessage
        {
            From = new MailAddress(fromAddress),
            Subject = WelcomeSubject,
            Body = $"Welcome, {username.ToUpperInvariant()}!\n\n" +
                   "Thank you for joining BankingApp. Your account is now active.\n\n" +
                   $"For support, email us at {GetSupportAddress()}"
        };
        message.To.Add(toEmail);

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

    private void SendWithRetry(MailMessage message)
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
        var host = _config["Email:SmtpHost"] ?? "localhost";
        var portStr = _config["Email:SmtpPort"];
        int.TryParse(portStr, out var port);
        
        if (port == 0)
            port = 587;

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

    private string GetFromAddress()
    {
        return _config["Email:FromAddress"] ?? "notifications@company.com";
    }

    private string GetSupportAddress()
    {
        return _config["Email:SupportAddress"] ?? "support@company.com";
    }
}
