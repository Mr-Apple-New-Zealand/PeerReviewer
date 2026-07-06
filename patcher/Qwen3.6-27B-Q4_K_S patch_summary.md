# AI Patch + Peer Review Summary

- **Patcher model:** `Qwen3.6-27B:Q4_K_S`
- **Reviewer model:** `gpt-oss:120b`
- **Scorer model:** `gpt-oss:120b`
- **Files the patcher rewrote:** 11
- **Rejected paths** (outside source root or invalid): 0

## Score comparison

| Stage | Found | Partial | Missed | Total | % Found |
|-------|-------|---------|--------|-------|---------|
| Baseline (before patch) | 59 | 0 | 11 | 70 | 84.3% |
| Post-patch | 8 | 3 | 59 | 70 | 11.4% |

> **How to read this table.** `%Found` is the peer reviewer's *recall*, not the patcher's success. A patch that removes bugs makes them undetectable, so those IDs move into `Missed` — that's the column to watch. `Found` and `Partial` can even shift *upwards* post-patch when the reviewer gets a cleaner view of the bugs that weren't fixed.

## Verdict

- **Issues resolved: 48** (68.6% of all seeded bugs). Computed as `post_missed - baseline_missed` — bugs that were detectable before the patch but the reviewer can no longer name afterwards.
- Reviewer still detects **11** of the 70 seeded issues, down from **59** before the patch.

## Patcher performance

| Metric | Value |
|--------|-------|
| Total time | 3m 55s |
| Prompt tokens | 10,908 |
| Output tokens | 7,382 |
| Output speed | 33.0 tok/s |
| Prompt speed | 2070.0 tok/s |
| Completed naturally | Yes |

## Files patched

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

