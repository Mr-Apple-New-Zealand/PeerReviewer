# AI Patch + Peer Review Summary

- **Patcher model:** `Qwen3.5-122B-imatrix:Q4_K_S`
- **Reviewer model:** `Qwen3.6-27B:Q4_K_S`
- **Scorer model:** `Qwen3.6-27B:Q4_K_S`
- **Files the patcher rewrote:** 12
- **Rejected paths** (outside source root or invalid): 0

## Score comparison

| Stage | Found | Partial | Missed | Total | % Found |
|-------|-------|---------|--------|-------|---------|
| Baseline (before patch) | 54 | 3 | 13 | 70 | 77.1% |
| Post-patch | 21 | 11 | 38 | 70 | 30.0% |

> **How to read this table.** `%Found` is the peer reviewer's *recall*, not the patcher's success. A patch that removes bugs makes them undetectable, so those IDs move into `Missed` — that's the column to watch. `Found` and `Partial` can even shift *upwards* post-patch when the reviewer gets a cleaner view of the bugs that weren't fixed.

## Verdict

- **Issues resolved: 25** (35.7% of all seeded bugs). Computed as `post_missed - baseline_missed` — bugs that were detectable before the patch but the reviewer can no longer name afterwards.
- Reviewer still detects **32** of the 70 seeded issues, down from **57** before the patch.

## Patcher performance

| Metric | Value |
|--------|-------|
| Total time | 2m 24s |
| Prompt tokens | 10,867 |
| Output tokens | 7,741 |
| Output speed | 59.5 tok/s |
| Prompt speed | 1734.6 tok/s |
| Completed naturally | Yes |

## Files patched

- `SampleBankingApp/Controllers/AuthController.cs`
- `SampleBankingApp/Controllers/TransactionController.cs`
- `SampleBankingApp/Controllers/UserController.cs`
- `SampleBankingApp/Data/DatabaseHelper.cs`
- `SampleBankingApp/Helpers/StringHelper.cs`
- `SampleBankingApp/Program.cs`
- `SampleBankingApp/SampleBankingApp.csproj`
- `SampleBankingApp/Services/AuthService.cs`
- `SampleBankingApp/Services/EmailService.cs`
- `SampleBankingApp/Services/TransactionService.cs`
- `SampleBankingApp/Services/UserService.cs`
- `SampleBankingApp/appsettings.json`

