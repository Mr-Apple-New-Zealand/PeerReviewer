# Jack-27B vs Qwen3.8-27B — Patcher Comparison

`hf.co/JackAgentLead/Jack-3.8-27B-Coder-16GB-VRAM:latest` against the incumbent
`Qwen3.8-27B-imatrix:Q4_K_S`, on the same task, the same reviewer
(`Gemma-4-31B-it-imatrix:Q4_K_M`) and the same scorer (`Qwen3-Coder-30B-imatrix:Q3_K_M`),
both at temperature 0 with `think: medium`.

The full field is in [../SUMMARY.md](../SUMMARY.md).

---

## Verdict

**Qwen3.8-27B stays.** Jack is faster and works harder, but its patch does not compile and it
leaves two defects the incumbent fixes. The gap is small and the direction is clear.

| | Jack-27B | Qwen3.8-27B |
|---|---|---|
| **Build** | **fails — 1 × `CS0103`** | **compiles** |
| **Mechanical** | 39/41 | **41/41** |
| Still present | `CF7`, `R3` | none |
| Resolved | 54/60 (90%) | 58/62 (94%) |
| Output tokens | **22,420** | 17,064 |
| Speed | **44.9 tok/s** | 23.8 tok/s |
| Time | **8m 30s** | 12m 9s |
| Files rewritten | 12 | 13 |

---

## Where Jack loses

**It does not compile.** One error, and it is the characteristic one:

```
CS0103  AuthService.cs:98  The name 'KeyDerivation' does not exist in the current context
```

Jack replaced the password hashing with a call to `KeyDerivation` — the ASP.NET Core PBKDF2
helper — without adding the `Microsoft.AspNetCore.Cryptography.KeyDerivation` package or its
`using`. The intent is right and better than a hand-rolled hash; the change is half-applied.
That is the single most common failure across the twenty-model sweep, and it is what separates
a usable patch from an unusable one.

**It leaves two defects the incumbent fixes:**

- `CF7` — debug symbols still emitted in Release builds. Jack rewrote `SampleBankingApp.csproj`
  and did not fix it.
- `R3` — `GenerateJwtToken` still over 12 lines, not split into helpers.

**It never touched `AuthController.cs`.** That is the only file the incumbent rewrote and Jack
did not. Everything else in the two patches covers the same twelve files.

---

## Where Jack wins

**It is nearly twice as fast per token and finishes 30% sooner** — 44.9 tok/s against 23.8,
8m 30s against 12m 9s — while producing *more* output (22,420 tokens against 17,064). For a
model advertised at 16GB VRAM that is the interesting result: it is doing more work per second
on smaller hardware.

**Its coverage is genuinely close.** 39 of 41 markers puts it level with `Muse-Glimmer-30B`
and `MiniMax-M2.7`, and ahead of everything else in the field bar the two 27B leaders and
`claude-opus-5`/`kimi-k3`. Both defects it leaves are in the tail the whole field found hard.

---

## How to read the resolved figures

Jack's 54 and Qwen3.8's 58 are **not directly comparable as counts** — the reviewer's baseline
differed between the runs (60 for Jack, 62 for Qwen3.8), which is normal drift for this
harness rather than anything about the patches. As ratios they are 90% and 94%.

Both figures should be treated as corroboration only. Across the sweep the review delta swung
by 30 points on one fixed patch depending on which model reviewed it, and repeat runs of a
single patcher varied by 7. A 4-point difference is inside that noise. **The mechanical count
and the build result are the columns that decide this comparison**, and both favour the
incumbent.

---

## If you want a rematch

Qwen3.8-27B does not reproduce its own patch across backend restarts — five runs produced one
patch that failed to build, one produced a different patch that passed. Jack has been run
once. A single comparison at this margin is thin, so if the choice matters, run each three
times and compare the build pass rate rather than one result each.

Fixing the `KeyDerivation` import would likely put Jack at 39/41 with a clean build, which
would place it fifth in the field — behind the two 27B leaders and `claude-opus-5`/`kimi-k3`,
level with `Muse-Glimmer-30B` but faster.
