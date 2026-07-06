# AI Patch + Peer Review Summary

- **Patcher model:** `external (file: claude_sonnet_patch.md)`
- **Reviewer model:** `Qwen3.6-27B:Q4_K_S`
- **Scorer model:** `Qwen3.6-27B:Q4_K_S`
- **Files the patcher rewrote:** 12
- **Rejected paths** (outside source root or invalid): 0

## Score comparison

| Stage | Found | Partial | Missed | Total | % Found |
|-------|-------|---------|--------|-------|---------|
| Baseline (before patch) | 50 | 6 | 14 | 70 | 71.4% |
| Post-patch | 6 | 21 | 43 | 70 | 8.6% |

> **How to read this table.** `%Found` is the peer reviewer's *recall*, not the patcher's success. A patch that removes bugs makes them undetectable, so those IDs move into `Missed` — that's the column to watch. `Found` and `Partial` can even shift *upwards* post-patch when the reviewer gets a cleaner view of the bugs that weren't fixed.

## Verdict

- **Issues resolved: 29** (41.4% of all seeded bugs). Computed as `post_missed - baseline_missed` — bugs that were detectable before the patch but the reviewer can no longer name afterwards.
- Reviewer still detects **27** of the 70 seeded issues, down from **56** before the patch.

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

