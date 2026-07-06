using System.Text;
using System.Text.RegularExpressions;

namespace SampleBankingApp.Helpers;

/// <summary>
/// General-purpose string utilities.
/// </summary>
public static class StringHelper
{
    public const int MaxEmailLength = 254;
    public const int MinUsernameLength = 3;
    public const int MaxUsernameLength = 20;
    public const int DefaultSmtpPort = 587;

    public static bool IsValidEmail(string? email)
    {
        if (string.IsNullOrEmpty(email))
            return false;

        if (email.Length > MaxEmailLength)
            return false;

        var regex = RegexCache.EmailPattern;
        return regex.IsMatch(email);
    }

    public static bool IsValidUsername(string? username)
    {
        if (string.IsNullOrEmpty(username))
            return false;

        if (username.Length < MinUsernameLength || username.Length > MaxUsernameLength)
            return false;

        var regex = RegexCache.UsernamePattern;
        return regex.IsMatch(username);
    }

    public static string JoinWithSeparator(IEnumerable<string> items, string separator)
    {
        return string.Join(separator, items);
    }

    public static string MaskAccountNumber(string accountNumber)
    {
        if (accountNumber.Length <= 4)
            return accountNumber;

        var sb = new StringBuilder();
        sb.Append(new string('*', accountNumber.Length - 4));
        sb.Append(accountNumber.Substring(accountNumber.Length - 4));
        return sb.ToString();
    }

    private static readonly Regex RegexCache = new(@"^[^@\s]+@[^@\s]+\.[^@\s]+$", RegexOptions.Compiled);
    private static readonly Regex UsernameRegexCache = new(@"^[a-zA-Z0-9_]+$", RegexOptions.Compiled);
}
