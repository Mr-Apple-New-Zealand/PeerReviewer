# AI Patch + Peer Review Summary

- **Patcher model:** `Qwen3.5-4B-imatrix:Q5_K_S`
- **Reviewer model:** `Gemma-4-31B-it-imatrix:Q4_K_M`
- **Scorer model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`
- **Files the patcher rewrote:** 14
- **Rejected paths** (outside source root or invalid): 0

## Score comparison

| Stage | Found | Partial | Missed | Total | % Found |
|-------|-------|---------|--------|-------|---------|
| Baseline (before patch) | 54 | 13 | 3 | 70 | 77.1% |
| Post-patch | 1 | 51 | 18 | 70 | 1.4% |

> **How to read this table.** `%Found` is the peer reviewer's *recall*, not the patcher's success. A patch that removes bugs makes them undetectable, so those IDs move into `Missed` — that's the column to watch. `Found` and `Partial` can even shift *upwards* post-patch when the reviewer gets a cleaner view of the bugs that weren't fixed.

## Verdict

- **Issues resolved: 24** (34.3% of all seeded bugs). Bugs the reviewer named before the patch and cannot name after. Rows the scorer credited without support in the review are excluded from both sides — unverifiable `Found` ratings and `Partial` ratings alike.
- Reviewer still detects **38** of the 70 seeded issues, down from **62** before the patch.
- Taking the scorer's columns at face value would give **15**. 5 baseline and 14 post-patch rows were credited with evidence the review does not contain, and are excluded. Baseline fabrications matter most: they invent bugs the reviewer never detected, each of which then counts as resolved.

## Patcher performance

| Metric | Value |
|--------|-------|
| Total time | 1m 4s |
| Prompt tokens | 14,699 |
| Output tokens | 8,924 |
| Output speed | 145.7 tok/s |
| Prompt speed | 11402.7 tok/s |
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
- `SampleBankingApp/appsettings.json`


## Build check

**The patched tree does not compile — 10 new error(s).** The pristine tree compiles cleanly.

Read every figure above in this light. A resolved-issues count measures whether the reviewer can still name each bug, and code that does not build can score well on that while being unusable.

| Error | File | Line | Message |
|---|---|---|---|
| `CS1061` | `StringHelper.cs` | 25 | 'Regex' does not contain a definition for 'EmailPattern' and no accessible extension method 'EmailPattern' accepting a first argument of type 'Regex' could be found (are you missing a using directive or an assembly reference?) |
| `CS0246` | `UserService.cs` | 49 | The type or namespace name 'SqlCommand' could not be found (are you missing a using directive or an assembly reference?) |
| `CS1061` | `StringHelper.cs` | 37 | 'Regex' does not contain a definition for 'UsernamePattern' and no accessible extension method 'UsernamePattern' accepting a first argument of type 'Regex' could be found (are you missing a using directive or an assembly reference?) |
| `CS0103` | `UserController.cs` | 46 | The name 'ClaimTypes' does not exist in the current context |
| `CS0103` | `UserService.cs` | 94 | The name '_auditLog' does not exist in the current context |
| `CS0103` | `UserService.cs` | 119 | The name '_logger' does not exist in the current context |
| `CS0103` | `EmailService.cs` | 30 | The name 'DefaultSmtpPort' does not exist in the current context |
| `CS0118` | `EmailService.cs` | 42 | 'Timeout' is a type but is used like a variable |
| `CS1061` | `Program.cs` | 53 | 'CorsPolicyBuilder' does not contain a definition for 'AllowMethods' and no accessible extension method 'AllowMethods' accepting a first argument of type 'CorsPolicyBuilder' could be found (are you missing a using directive or an assembly reference?) |
| `CS0246` | `TransactionService.cs` | 53 | The type or namespace name 'SqlCommand' could not be found (are you missing a using directive or an assembly reference?) |

## Run Configuration

Values as actually used, so this run can be re-dispatched exactly. Blank sampler entries mean the request omitted them and the model's own Modelfile applied.

| Setting | Value |
|---|---|
| **Patcher** |  |
| Model | `Qwen3.5-4B-imatrix:Q5_K_S` |
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

**30 fixed / 11 still present** (of 41 checked).

| ID | File | Still present |
|---|---|---|
| A6 | `Data/DatabaseHelper.cs` | connection-leaking GetOpenConnection still present |
| C3 | `Services/AuthService.cs` | MD5 password hashing |
| C11 | `Controllers/UserController.cs` | DeleteUser performs no role check |
| E7 | `(tree)` | no rate limiting or lockout anywhere on the login path |
| RL2 | `Data/DatabaseHelper.cs` | connection-leaking helper still exported |
| R3 | `Services/AuthService.cs` | GenerateJwtToken still over 12 lines — not split into helpers |
| D3 | `Data/DatabaseHelper.cs` | unused TableExists |
| D4 | `Data/DatabaseHelper.cs` | obsolete method retained |
| D6 | `Services/EmailService.cs` | uncalled public method |
| D8 | `Services/TransactionService.cs` | daily limit never enforced |
| CF9 | `appsettings.Production.json` | no environment-specific config file |

A marker proves the bug's *shape* is gone, not that the replacement is correct — read this next to the peer review, not instead of it.

