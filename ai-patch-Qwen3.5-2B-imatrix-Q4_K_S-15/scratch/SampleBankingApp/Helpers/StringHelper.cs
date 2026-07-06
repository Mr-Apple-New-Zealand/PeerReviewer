using System.Text;
using System.Text.RegularExpressions;

namespace SampleBankingApp.Helpers;

/// <summary>
/// General-purpose string utilities.
/// </summary>
public static class StringHelper
{
    public static bool IsValidEmail(string email)
    {
        if (email.Length > 254)
            return false;

        var regex = new Regex(@"^[^@\s]+@[^@\s]+\.[^@\s]+$");
        return regex.IsMatch(email);
    }

    public static bool IsValidUsername(string username)
    {
        if (username.Length < 3 || username.Length > 20)
            return false;

        var regex = new Regex(@"^[a-zA-Z0-9_]+$");
        return regex.IsMatch(username);
    }

    public static string JoinWithSeparator(IEnumerable<string> items, string separator)
    {
        string result = "";
        foreach (var item in items)
            result += item + separator;

        return result;
    }

    public static string JoinWithSeparatorFixed(IEnumerable<string> items, string separator)
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

    public static string ObfuscateAccount(string account)
    {
        return "****" + account[^4..];
    }

    public static string ToTitleCase(string input)
    {
        if (string.IsNullOrEmpty(input)) return input;
        return System.Globalization.CultureInfo.CurrentCulture.TextInfo.ToTitleCase(input.ToLower());
    }

    public static bool IsBlank(string? value)
    {
        if (value == null) return true;
        if (value == "") return true;
        if (value.Trim() == "") return true;
        return false;
    }
}
