# AI Patch + Peer Review Summary

- **Patcher model:** `Qwen3.5-2B-imatrix:Q4_K_S`
- **Reviewer model:** `Gemma-4-31B-it-imatrix:Q4_K_M`
- **Scorer model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`
- **Files the patcher rewrote:** 13
- **Rejected paths** (outside source root or invalid): 0

## Score comparison

| Stage | Found | Partial | Missed | Total | % Found |
|-------|-------|---------|--------|-------|---------|
| Baseline (before patch) | 54 | 13 | 3 | 70 | 77.1% |
| Post-patch | 55 | 0 | 15 | 70 | 78.6% |

> **How to read this table.** `%Found` is the peer reviewer's *recall*, not the patcher's success. A patch that removes bugs makes them undetectable, so those IDs move into `Missed` — that's the column to watch. `Found` and `Partial` can even shift *upwards* post-patch when the reviewer gets a cleaner view of the bugs that weren't fixed.

## Verdict

- **Issues resolved: 10** (14.3% of all seeded bugs). Bugs the reviewer named before the patch and cannot name after. Rows the scorer credited without support in the review are excluded from both sides — unverifiable `Found` ratings and `Partial` ratings alike.
- Reviewer still detects **52** of the 70 seeded issues, down from **62** before the patch.
- Taking the scorer's columns at face value would give **12**. 5 baseline and 3 post-patch rows were credited with evidence the review does not contain, and are excluded. Baseline fabrications matter most: they invent bugs the reviewer never detected, each of which then counts as resolved.

## Patcher performance

| Metric | Value |
|--------|-------|
| Total time | 28.2s |
| Prompt tokens | 14,699 |
| Output tokens | 6,286 |
| Output speed | 258.2 tok/s |
| Prompt speed | 24546.7 tok/s |
| Completed naturally | Yes |

## Files patched

- `SampleBankingApp/Controllers/AuthController.cs`
- `SampleBankingApp/Controllers/TransactionController.cs`
- `SampleBankingApp/Controllers/UserController.cs`
- `SampleBankingApp/Data/DatabaseHelper.cs`
- `SampleBankingApp/Helpers/StringHelper.cs`
- `SampleBankingApp/Models/Transaction.cs`
- `SampleBankingApp/Models/User.cs`
- `SampleBankingApp/Program.cs`
- `SampleBankingApp/SampleBankingApp.csproj`
- `SampleBankingApp/Services/AuthService.cs`
- `SampleBankingApp/Services/EmailService.cs`
- `SampleBankingApp/Services/TransactionService.cs`
- `SampleBankingApp/Services/UserService.cs`


## Build check

**The patched tree does not compile — 5 new error(s).** The pristine tree compiles cleanly.

Read every figure above in this light. A resolved-issues count measures whether the reviewer can still name each bug, and code that does not build can score well on that while being unusable.

| Error | File | Line | Message |
|---|---|---|---|
| `CS7036` | `UserService.cs` | 45 | There is no argument given that corresponds to the required parameter 'name' of 'ConfigurationExtensions.GetConnectionString(IConfiguration, string)' |
| `CS1503` | `UserService.cs` | 51 | Argument 1: cannot convert from 'System.Data.SqlClient.SqlCommand' to 'string' |
| `CS1503` | `UserService.cs` | 82 | Argument 1: cannot convert from 'object' to 'System.Data.DataRow' |
| `CS7036` | `TransactionService.cs` | 92 | There is no argument given that corresponds to the required parameter 'name' of 'ConfigurationExtensions.GetConnectionString(IConfiguration, string)' |
| `CS1503` | `TransactionService.cs` | 95 | Argument 1: cannot convert from 'System.Data.SqlClient.SqlCommand' to 'string' |

## Run Configuration

Values as actually used, so this run can be re-dispatched exactly. Blank sampler entries mean the request omitted them and the model's own Modelfile applied.

| Setting | Value |
|---|---|
| **Patcher** |  |
| Model | `Qwen3.5-2B-imatrix:Q4_K_S` |
| Temperature | `0` |
| num_ctx / num_predict | `65536` / `40000` |
| Reasoning / `think` | (model default) / `false` |
| Source truncated | `no` |
| **Reviewer** |  |
| Model | `Gemma-4-31B-it-imatrix:Q4_K_M` |
| Temperature | `0` |
| num_ctx / num_predict | `65536` / `40000` |
| Reasoning / `think` | (model default) / (unset) |
| Source truncated | `no` |
| **Scorer** |  |
| Model | `Qwen3-Coder-30B-imatrix:Q3_K_M` |
| Temperature | `0` |
| num_predict | `24000` |
| Reasoning / `think` | (model default) / (unset) |
| Grounding mode | `enforce` |
| **Reference** |  |
| Branch / commit | `main @ eb8f66b` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| Review prompt SHA-256 | `82bd5f768ca9` |


## Mechanical patch verification

Direct inspection of the patched source for 41 of the 69 seeded issues — those with an unambiguous textual marker. Independent of the peer reviewer, so it is not affected by review recall or scorer mis-attribution.

**9 fixed / 32 still present** (of 41 checked).

| ID | File | Still present |
|---|---|---|
| C1 | `Services/AuthService.cs` | Login builds its SELECT by interpolation |
| C4 | `Services/UserService.cs` | UpdateUser/DeleteUser interpolate into UPDATE/DELETE |
| C5 | `Services/UserService.cs` | SearchUsers interpolates into a LIKE clause |
| C6 | `Services/TransactionService.cs` | Transfer/Deposit interpolate balance updates |
| C7 | `Services/TransactionService.cs` | RecordTransaction interpolates the INSERT |
| A6 | `Data/DatabaseHelper.cs` | connection-leaking GetOpenConnection still present |
| C3 | `Services/AuthService.cs` | MD5 password hashing |
| C8 | `appsettings.json` | a real DB password is still committed |
| C9 | `Program.cs` | JWT lifetime validation disabled |
| C10 | `Controllers/UserController.cs` | UpdateUser performs no ownership check |
| C11 | `Controllers/UserController.cs` | DeleteUser performs no role check |
| E7 | `(tree)` | no rate limiting or lockout anywhere on the login path |
| L5 | `(tree)` | no self-transfer guard anywhere |
| RL2 | `Data/DatabaseHelper.cs` | connection-leaking helper still exported |
| RL4 | `Services/EmailService.cs` | SmtpClient still held as an instance field |
| R1 | `Services/UserService.cs` | duplicated id validation not extracted |
| R3 | `Services/AuthService.cs` | GenerateJwtToken still over 12 lines — not split into helpers |
| D3 | `Data/DatabaseHelper.cs` | unused TableExists |
| D4 | `Data/DatabaseHelper.cs` | obsolete method retained |
| D7 | `Services/TransactionService.cs` | uncalled helper |
| D8 | `Services/TransactionService.cs` | daily limit never enforced |
| D9 | `Helpers/StringHelper.cs` | superseded helper retained |
| D10 | `Helpers/StringHelper.cs` | experimental helper retained |
| D11 | `Helpers/StringHelper.cs` | duplicate implementation retained |
| A2 | `Helpers/StringHelper.cs` | Regex still constructed per call |
| A5 | `Helpers/StringHelper.cs` | IsBlank still reimplements the BCL |
| CF4 | `Program.cs` | HTTPS redirection still commented out |
| CF5 | `Program.cs` | developer exception page still unconditional |
| CF6 | `Program.cs` | open CORS policy |
| CF7 | `SampleBankingApp.csproj` | debug symbols still emitted in Release builds |
| CF8 | `SampleBankingApp.csproj` | vulnerable Newtonsoft.Json 12.x pinned |
| CF9 | `appsettings.Production.json` | no environment-specific config file |

A marker proves the bug's *shape* is gone, not that the replacement is correct — read this next to the peer review, not instead of it.

