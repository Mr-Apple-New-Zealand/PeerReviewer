# AI Patch + Peer Review Summary

- **Patcher model:** `Qwen3.5-9B-imatrix:Q4_K_S`
- **Reviewer model:** `Qwen3.6-27B:Q4_K_S`
- **Scorer model:** `Qwen3.6-27B:Q4_K_S`
- **Files the patcher rewrote:** 7
- **Rejected paths** (outside source root or invalid): 0

## Score comparison

| Stage | Found | Partial | Missed | Total | % Found |
|-------|-------|---------|--------|-------|---------|
| Baseline (before patch) | 53 | 4 | 13 | 70 | 75.7% |
| Post-patch | 39 | 8 | 23 | 70 | 55.7% |

> **How to read this table.** `%Found` is the peer reviewer's *recall*, not the patcher's success. A patch that removes bugs makes them undetectable, so those IDs move into `Missed` — that's the column to watch. `Found` and `Partial` can even shift *upwards* post-patch when the reviewer gets a cleaner view of the bugs that weren't fixed.

## Verdict

- **Issues resolved: 10** (14.3% of all seeded bugs). Computed as `post_missed - baseline_missed` — bugs that were detectable before the patch but the reviewer can no longer name afterwards.
- Reviewer still detects **47** of the 70 seeded issues, down from **57** before the patch.

## Patcher performance

| Metric | Value |
|--------|-------|
| Total time | 4m 43s |
| Prompt tokens | 10,906 |
| Output tokens | 24,000 |
| Output speed | 88.7 tok/s |
| Prompt speed | 5866.4 tok/s |
| Completed naturally | No (hit token limit) |

## Files patched

- `SampleBankingApp/Controllers/AuthController.cs`
- `SampleBankingApp/Controllers/TransactionController.cs`
- `SampleBankingApp/Controllers/UserController.cs`
- `SampleBankingApp/Data/DatabaseHelper.cs`
- `SampleBankingApp/Helpers/StringHelper.cs`
- `SampleBankingApp/Services/AuthService.cs`
- `SampleBankingApp/Services/EmailService.cs`

