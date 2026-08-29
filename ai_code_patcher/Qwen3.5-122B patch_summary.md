# AI Patch + Peer Review Summary

- **Patcher model:** `Qwen3.5-122B-imatrix:Q4_K_S`
- **Reviewer model:** `Gemma-4-31B-it-imatrix:Q4_K_M`
- **Scorer model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`
- **Files the patcher rewrote:** 14
- **Rejected paths** (outside source root or invalid): 0

## Score comparison

| Stage | Found | Partial | Missed | Total | % Found |
|-------|-------|---------|--------|-------|---------|
| Baseline (before patch) | 54 | 13 | 3 | 70 | 77.1% |
| Post-patch | 16 | 29 | 25 | 70 | 22.9% |

> **How to read this table.** `%Found` is the peer reviewer's *recall*, not the patcher's success. A patch that removes bugs makes them undetectable, so those IDs move into `Missed` — that's the column to watch. `Found` and `Partial` can even shift *upwards* post-patch when the reviewer gets a cleaner view of the bugs that weren't fixed.

## Verdict

- **Issues resolved: 31** (44.3% of all seeded bugs). Bugs the reviewer named before the patch and cannot name after. Rows the scorer credited without support in the review are excluded from both sides — unverifiable `Found` ratings and `Partial` ratings alike.
- Reviewer still detects **31** of the 70 seeded issues, down from **62** before the patch.
- Taking the scorer's columns at face value would give **22**. 5 baseline and 14 post-patch rows were credited with evidence the review does not contain, and are excluded. Baseline fabrications matter most: they invent bugs the reviewer never detected, each of which then counts as resolved.

## Patcher performance

| Metric | Value |
|--------|-------|
| Total time | 2m 30s |
| Prompt tokens | 14,697 |
| Output tokens | 10,902 |
| Output speed | 81.8 tok/s |
| Prompt speed | 3031.2 tok/s |
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

**The patched tree does not compile — 2 new error(s).** The pristine tree compiles cleanly.

Read every figure above in this light. A resolved-issues count measures whether the reviewer can still name each bug, and code that does not build can score well on that while being unusable.

| Error | File | Line | Message |
|---|---|---|---|
| `CS0246` | `TransactionService.cs` | 61 | The type or namespace name 'SqlConnection' could not be found (are you missing a using directive or an assembly reference?) |
| `CS0246` | `TransactionService.cs` | 67 | The type or namespace name 'SqlCommand' could not be found (are you missing a using directive or an assembly reference?) |

## Run Configuration

Values as actually used, so this run can be re-dispatched exactly. Blank sampler entries mean the request omitted them and the model's own Modelfile applied.

| Setting | Value |
|---|---|
| **Patcher** |  |
| Model | `Qwen3.5-122B-imatrix:Q4_K_S` |
| Temperature | `0` |
| num_ctx / num_predict | `65536` / `40000` |
| Reasoning / `think` | (model default) / (unset) |
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

**37 fixed / 4 still present** (of 41 checked).

| ID | File | Still present |
|---|---|---|
| C3 | `Services/AuthService.cs` | MD5 password hashing |
| E7 | `(tree)` | no rate limiting or lockout anywhere on the login path |
| R3 | `Services/AuthService.cs` | GenerateJwtToken still over 12 lines — not split into helpers |
| CF9 | `appsettings.Production.json` | no environment-specific config file |

A marker proves the bug's *shape* is gone, not that the replacement is correct — read this next to the peer review, not instead of it.

