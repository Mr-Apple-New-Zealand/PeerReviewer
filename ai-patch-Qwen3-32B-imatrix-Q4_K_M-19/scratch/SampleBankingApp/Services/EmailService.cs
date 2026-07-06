using System.Net;
using System.Net.Mail;

namespace SampleBankingApp.Services;

public class EmailService
{
    private readonly IConfiguration _config;

    public EmailService(IConfiguration config)
    {
        _config = config;
    }

    public void SendTransferNotification(string toEmail, decimal amount, string recipientName)
    {
        var body = $"You have successfully transferred ${amount:F2} to {recipientName}.\n\n" +
                   "If you did not initiate this transfer, contact support immediately.";

        var message = new MailMessage(
            from: _config["Email:FromAddress"],
            to: toEmail,
            subject: "Transfer Notification - BankingApp",
            body: body);

        using var smtpClient = new SmtpClient(_config["Email:SmtpHost"])
        {
            Port = int.Parse(_config["Email:SmtpPort"]!),
            Credentials = new NetworkCredential(
                _config["Email:Username"]!,
                _config["Email:Password"]!),
            EnableSsl = _config.GetValue<bool>("Email:UseSsl"),
            Timeout = 5000
        };

        try
        {
            smtpClient.Send(message);
        }
        catch (SmtpException ex)
        {
            // Log exception but don't expose details
            Console.WriteLine($"Email failed: {ex.Message}");
        }
        finally
        {
            message.Dispose();
        }
    }
}
