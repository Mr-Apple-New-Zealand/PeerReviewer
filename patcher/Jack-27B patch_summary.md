# AI Patch + Peer Review Summary

- **Patcher model:** `hf.co/JackAgentLead/Jack-3.8-27B-Coder-16GB-VRAM:latest`
- **Reviewer model:** `gpt-oss:120b`
- **Scorer model:** `gpt-oss:120b`
- **Files the patcher rewrote:** 13
- **Rejected paths** (outside source root or invalid): 0

## Score comparison

| Stage | Found | Partial | Missed | Total | % Found |
|-------|-------|---------|--------|-------|---------|
| Baseline (before patch) | 21 | 1 | 48 | 70 | 30.0% |
| Post-patch | 2 | 0 | 68 | 70 | 2.9% |

> **How to read this table.** `%Found` is the peer reviewer's *recall*, not the patcher's success. A patch that removes bugs makes them undetectable, so those IDs move into `Missed` — that's the column to watch. `Found` and `Partial` can even shift *upwards* post-patch when the reviewer gets a cleaner view of the bugs that weren't fixed.

## Verdict

- **Issues resolved: 20** (28.6% of all seeded bugs). Computed as `post_missed - baseline_missed` — bugs that were detectable before the patch but the reviewer can no longer name afterwards.
- Reviewer still detects **2** of the 70 seeded issues, down from **22** before the patch.

## Patcher performance

| Metric | Value |
|--------|-------|
| Total time | 7m 41s |
| Prompt tokens | 18,400 |
| Output tokens | 20,446 |
| Output speed | 45.1 tok/s |
| Prompt speed | 2787.5 tok/s |
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
- `SampleBankingApp/appsettings.Production.json`
- `SampleBankingApp/appsettings.json`


## Mechanical patch verification

Direct inspection of the patched source for 41 of the 69 seeded issues — those with an unambiguous textual marker. Independent of the peer reviewer, so it is not affected by review recall or scorer mis-attribution.

**38 fixed / 3 still present** (of 41 checked).

| ID | File | Still present |
|---|---|---|
| A6 | `Data/DatabaseHelper.cs` | raw tableName/whereClause helper still accepts SQL fragments |
| A5 | `Helpers/StringHelper.cs` | IsBlank still reimplements the BCL |
| CF7 | `SampleBankingApp.csproj` | debug symbols emitted unconditionally |

A marker proves the bug's *shape* is gone, not that the replacement is correct — read this next to the peer review, not instead of it.

