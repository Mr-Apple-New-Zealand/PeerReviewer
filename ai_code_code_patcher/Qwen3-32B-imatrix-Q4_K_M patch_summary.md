# AI Patch + Peer Review Summary

- **Patcher model:** `Qwen3-32B-imatrix:Q4_K_M`
- **Reviewer model:** `Qwen3.6-27B:Q4_K_S`
- **Scorer model:** `Qwen3.6-27B:Q4_K_S`
- **Files the patcher rewrote:** 8
- **Rejected paths** (outside source root or invalid): 0

## Score comparison

| Stage | Found | Partial | Missed | Total | % Found |
|-------|-------|---------|--------|-------|---------|
| Baseline (before patch) | 55 | 3 | 12 | 70 | 78.6% |
| Post-patch | 19 | 3 | 48 | 70 | 27.1% |

> **How to read this table.** `%Found` is the peer reviewer's *recall*, not the patcher's success. A patch that removes bugs makes them undetectable, so those IDs move into `Missed` — that's the column to watch. `Found` and `Partial` can even shift *upwards* post-patch when the reviewer gets a cleaner view of the bugs that weren't fixed.

## Verdict

- **Issues resolved: 36** (51.4% of all seeded bugs). Computed as `post_missed - baseline_missed` — bugs that were detectable before the patch but the reviewer can no longer name afterwards.
- Reviewer still detects **22** of the 70 seeded issues, down from **58** before the patch.

## Patcher performance

| Metric | Value |
|--------|-------|
| Total time | 2m 29s |
| Prompt tokens | 10,017 |
| Output tokens | 4,042 |
| Output speed | 28.8 tok/s |
| Prompt speed | 2099.6 tok/s |
| Completed naturally | Yes |

## Files patched

- `SampleBankingApp/Controllers/UserController.cs`
- `SampleBankingApp/Data/DatabaseHelper.cs`
- `SampleBankingApp/Program.cs`
- `SampleBankingApp/Services/AuthService.cs`
- `SampleBankingApp/Services/EmailService.cs`
- `SampleBankingApp/Services/TransactionService.cs`
- `SampleBankingApp/Services/UserService.cs`
- `SampleBankingApp/appsettings.json`

