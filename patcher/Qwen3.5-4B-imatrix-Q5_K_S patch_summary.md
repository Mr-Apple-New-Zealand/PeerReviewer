# AI Patch + Peer Review Summary

- **Patcher model:** `Qwen3.5-4B-imatrix:Q5_K_S`
- **Reviewer model:** `Qwen3.6-27B:Q4_K_S`
- **Scorer model:** `Qwen3.6-27B:Q4_K_S`
- **Files the patcher rewrote:** 16
- **Rejected paths** (outside source root or invalid): 0

## Score comparison

| Stage | Found | Partial | Missed | Total | % Found |
|-------|-------|---------|--------|-------|---------|
| Baseline (before patch) | 54 | 2 | 14 | 70 | 77.1% |
| Post-patch | 18 | 6 | 46 | 70 | 25.7% |

> **How to read this table.** `%Found` is the peer reviewer's *recall*, not the patcher's success. A patch that removes bugs makes them undetectable, so those IDs move into `Missed` — that's the column to watch. `Found` and `Partial` can even shift *upwards* post-patch when the reviewer gets a cleaner view of the bugs that weren't fixed.

## Verdict

- **Issues resolved: 32** (45.7% of all seeded bugs). Computed as `post_missed - baseline_missed` — bugs that were detectable before the patch but the reviewer can no longer name afterwards.
- Reviewer still detects **24** of the 70 seeded issues, down from **56** before the patch.

## Patcher performance

| Metric | Value |
|--------|-------|
| Total time | 1m 16s |
| Prompt tokens | 10,906 |
| Output tokens | 8,453 |
| Output speed | 121.8 tok/s |
| Prompt speed | 7533.7 tok/s |
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
- `SampleBankingApp/appsettings.Development.json`
- `SampleBankingApp/appsettings.Production.json`
- `SampleBankingApp/appsettings.json`

