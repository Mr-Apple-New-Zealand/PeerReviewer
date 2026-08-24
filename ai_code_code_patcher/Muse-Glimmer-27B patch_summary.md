# AI Patch + Peer Review Summary

- **Patcher model:** `Muse-Glimmer-30B-imatrix:Q4_K_S`
- **Reviewer model:** `Qwen3.6-27B:Q4_K_S`
- **Scorer model:** `Qwen3.6-27B:Q4_K_S`
- **Files the patcher rewrote:** 12
- **Rejected paths** (outside source root or invalid): 0

## Score comparison

| Stage | Found | Partial | Missed | Total | % Found |
|-------|-------|---------|--------|-------|---------|
| Baseline (before patch) | 42 | 1 | 27 | 70 | 60.0% |
| Post-patch | 11 | 4 | 55 | 70 | 15.7% |

> **How to read this table.** `%Found` is the peer reviewer's *recall*, not the patcher's success. A patch that removes bugs makes them undetectable, so those IDs move into `Missed` — that's the column to watch. `Found` and `Partial` can even shift *upwards* post-patch when the reviewer gets a cleaner view of the bugs that weren't fixed.

## Verdict

- **Issues resolved: 28** (40.0% of all seeded bugs). Computed as `post_missed - baseline_missed` — bugs that were detectable before the patch but the reviewer can no longer name afterwards.
- Reviewer still detects **15** of the 70 seeded issues, down from **43** before the patch.

## Patcher performance

| Metric | Value |
|--------|-------|
| Total time | 10m 60s |
| Prompt tokens | 13,063 |
| Output tokens | 25,721 |
| Output speed | 39.6 tok/s |
| Prompt speed | 3094.5 tok/s |
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


## Mechanical patch verification

Direct inspection of the patched source for 41 of the 69 seeded issues — those with an unambiguous textual marker. Independent of the peer reviewer, so it is not affected by review recall or scorer mis-attribution.

**38 fixed / 3 still present** (of 41 checked).

| ID | File | Still present |
|---|---|---|
| A6 | `Data/DatabaseHelper.cs` | raw tableName/whereClause helper still accepts SQL fragments |
| RL2 | `Data/DatabaseHelper.cs` | connection-leaking helper still exported |
| CF9 | `appsettings.Production.json` | no environment-specific config file |

A marker proves the bug's *shape* is gone, not that the replacement is correct — read this next to the peer review, not instead of it.

