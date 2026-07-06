using System.Text;
using System.Text.RegularExpressions;

namespace SampleBankingApp.Helpers;

/// <summary>
/// General-purpose string utilities.
/// </summary>
public static class StringHelper
{
    private static readonly Regex EmailRegex = new(@"^[^@\s]+@[^@\s]+\.[^@\s]+$");
    private static readonly Regex UsernameRegex = new(@"^[a-zA-Z0-9_]+$");

    private const int MaxEmailLength = 254;
    private const int MinUsernameLength = 3;
    private const int MaxUsernameLength = 20;

    public static bool IsValidEmail(string email)
    {
        if (email == null)
            return false;

        if (email.Length > MaxEmailLength)
            return false;

        return EmailRegex.IsMatch(email);
    }

    public static bool IsValidUsername(string username)
    {
        if (username == null)
            return false;

        if (username.Length < MinUsernameLength || username.Length > MaxUsernameLength)
            return false;

        return UsernameRegex.IsMatch(username);
    }

    public static string JoinWithSeparator(IEnumerable<string> items, string separator)
    {
        return string.Join(separator, items);
    }

    public static string MaskAccountNumber(string accountNumber)
    {
        if (accountNumber == null)
            return string.Empty;

        if (accountNumber.Length <= 4)
            return accountNumber;

        var sb = new StringBuilder();
        sb.Append(new string('*', accountNumber.Length - 4));
        sb.Append(accountNumber.Substring(accountNumber.Length - 4));
        return sb.ToString();
    }

    public static bool IsBlank(string? value)
    {
        return string.IsNullOrWhiteSpace(value);
    }
}

