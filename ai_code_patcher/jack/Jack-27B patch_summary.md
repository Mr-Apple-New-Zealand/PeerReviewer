# AI Patch + Peer Review Summary

- **Patcher model:** `hf.co/JackAgentLead/Jack-3.8-27B-Coder-16GB-VRAM:latest`
- **Reviewer model:** `Gemma-4-31B-it-imatrix:Q4_K_M`
- **Scorer model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`
- **Files the patcher rewrote:** 12
- **Rejected paths** (outside source root or invalid): 0

## Score comparison

| Stage | Found | Partial | Missed | Total | % Found |
|-------|-------|---------|--------|-------|---------|
| Baseline (before patch) | 48 | 17 | 5 | 70 | 68.6% |
| Post-patch | 1 | 16 | 53 | 70 | 1.4% |

> **How to read this table.** `%Found` is the peer reviewer's *recall*, not the patcher's success. A patch that removes bugs makes them undetectable, so those IDs move into `Missed` — that's the column to watch. `Found` and `Partial` can even shift *upwards* post-patch when the reviewer gets a cleaner view of the bugs that weren't fixed.

## Verdict

- **Issues resolved: 54** (77.1% of all seeded bugs). Bugs the reviewer named before the patch and cannot name after. Rows the scorer credited without support in the review are excluded from both sides — unverifiable `Found` ratings and `Partial` ratings alike.
- Reviewer still detects **6** of the 70 seeded issues, down from **60** before the patch.
- Taking the scorer's columns at face value would give **48**. 5 baseline and 11 post-patch rows were credited with evidence the review does not contain, and are excluded. Baseline fabrications matter most: they invent bugs the reviewer never detected, each of which then counts as resolved.

## Patcher performance

| Metric | Value |
|--------|-------|
| Total time | 8m 32s |
| Prompt tokens | 18,421 |
| Output tokens | 22,420 |
| Output speed | 44.9 tok/s |
| Prompt speed | 2274.8 tok/s |
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
- `SampleBankingApp/appsettings.Production.json`
- `SampleBankingApp/appsettings.json`


## Build check

**The patched tree does not compile — 1 new error(s).** The pristine tree compiles cleanly.

Read every figure above in this light. A resolved-issues count measures whether the reviewer can still name each bug, and code that does not build can score well on that while being unusable.

| Error | File | Line | Message |
|---|---|---|---|
| `CS0103` | `AuthService.cs` | 98 | The name 'KeyDerivation' does not exist in the current context |

## Run Configuration

Values as actually used, so this run can be re-dispatched exactly. Blank sampler entries mean the request omitted them and the model's own Modelfile applied.

| Setting | Value |
|---|---|
| **Patcher** |  |
| Model | `hf.co/JackAgentLead/Jack-3.8-27B-Coder-16GB-VRAM:latest` |
| Provider | `ollama` |
| Temperature | `0` |
| num_ctx / num_predict | `65536` / `40000` |
| Reasoning / `think` | (model default) / `medium` |
| Effort (Anthropic only) | (n/a) |
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
| Branch / commit | `main @ 9cd8172` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| Review prompt SHA-256 | `82bd5f768ca9` |


## Mechanical patch verification

Direct inspection of the patched source for 41 of the 69 seeded issues — those with an unambiguous textual marker. Independent of the peer reviewer, so it is not affected by review recall or scorer mis-attribution.

**39 fixed / 2 still present** (of 41 checked).

| ID | File | Still present |
|---|---|---|
| R3 | `Services/AuthService.cs` | GenerateJwtToken still over 12 lines — not split into helpers |
| CF7 | `SampleBankingApp.csproj` | debug symbols still emitted in Release builds |

A marker proves the bug's *shape* is gone, not that the replacement is correct — read this next to the peer review, not instead of it.

