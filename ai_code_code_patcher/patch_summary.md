# AI Patch + Peer Review Summary

- **Patcher model:** `gpt-oss:120b`
- **Reviewer model:** `Qwen3.6-27B:Q4_K_S`
- **Scorer model:** `Qwen3.6-27B:Q4_K_S`
- **Files the patcher rewrote:** 10
- **Rejected paths** (outside source root or invalid): 0

## Score comparison

| Stage | Found | Partial | Missed | Total | % Found |
|-------|-------|---------|--------|-------|---------|
| Baseline (before patch) | 59 | 0 | 11 | 70 | 84.3% |
| Post-patch | 12 | 7 | 51 | 70 | 17.1% |

> **How to read this table.** `%Found` is the peer reviewer's *recall*, not the patcher's success. A patch that removes bugs makes them undetectable, so those IDs move into `Missed` — that's the column to watch. `Found` and `Partial` can even shift *upwards* post-patch when the reviewer gets a cleaner view of the bugs that weren't fixed.

## Verdict

- **Issues resolved: 40** (57.1% of all seeded bugs). Computed as `post_missed - baseline_missed` — bugs that were detectable before the patch but the reviewer can no longer name afterwards.
- Reviewer still detects **19** of the 70 seeded issues, down from **59** before the patch.

## Patcher performance

| Metric | Value |
|--------|-------|
| Total time | 1m 33s |
| Prompt tokens | 13,152 |
| Output tokens | 8,124 |
| Output speed | 103.3 tok/s |
| Prompt speed | 7244.7 tok/s |
| Completed naturally | Yes |

## Files patched

- `SampleBankingApp/Controllers/TransactionController.cs`
- `SampleBankingApp/Controllers/UserController.cs`
- `SampleBankingApp/Data/DatabaseHelper.cs`
- `SampleBankingApp/Helpers/StringHelper.cs`
- `SampleBankingApp/Program.cs`
- `SampleBankingApp/Services/AuthService.cs`
- `SampleBankingApp/Services/EmailService.cs`
- `SampleBankingApp/Services/TransactionService.cs`
- `SampleBankingApp/Services/UserService.cs`
- `SampleBankingApp/appsettings.json`


## Mechanical patch verification

Direct inspection of the patched source for 41 of the 69 seeded issues — those with an unambiguous textual marker. Independent of the peer reviewer, so it is not affected by review recall or scorer mis-attribution.

**33 fixed / 8 still present** (of 41 checked).

| ID | File | Still present |
|---|---|---|
| E7 | `Controllers/AuthController.cs` | login endpoint has no rate limiting or lockout |
| RL2 | `Data/DatabaseHelper.cs` | connection-leaking helper still exported |
| R3 | `Services/AuthService.cs` | GenerateJwtToken not split into helpers |
| D8 | `Services/TransactionService.cs` | daily limit never enforced |
| A5 | `Helpers/StringHelper.cs` | IsBlank still reimplements the BCL |
| CF7 | `SampleBankingApp.csproj` | debug symbols emitted unconditionally |
| CF8 | `SampleBankingApp.csproj` | vulnerable Newtonsoft.Json 12.x pinned |
| CF9 | `appsettings.Production.json` | no environment-specific config file |

A marker proves the bug's *shape* is gone, not that the replacement is correct — read this next to the peer review, not instead of it.

