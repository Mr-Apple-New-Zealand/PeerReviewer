# AI Code Patcher Benchmark — Results Summary

Twenty-one models were asked to *fix* the 70 seeded defects in `SampleBankingApp/`, rather than
find them. Each received the same source listing and the same issue list, and returned
rewritten files. Every patch was then measured three ways: a peer review scored against
`ISSUES.md`, a direct inspection of the patched source, and a compiler.

The companion documents are [../ai_code_review_results/SUMMARY.md](../ai_code_review_results/SUMMARY.md)
(finding defects) and [../ai_qa_scorer_results/SUMMARY.md](../ai_qa_scorer_results/SUMMARY.md)
(grading reviews).

`Jack-27B` was measured later as a head-to-head against `Qwen3.8-27B` rather than as part of
this field, and is written up separately in [jack/](jack/) — 39 of 41 markers, one missing
package reference short of a clean build.

---

## Executive Summary

**Eight of twenty-one produced code that compiles.** That is the finding. Thirteen models
returned patches that a C# compiler rejects — inventing methods that do not exist, deleting a
class while still referencing it, dropping a `using` directive, or in one case emitting a
project file that is not valid XML. A patch that does not build is not a patch, however many
defects it appears to remove.

**The two 27B local models are the recommendation: `Qwen3.8-27B` and `Qwen3.6-27B`.** Both
cleared all 41 mechanical markers, both compile, and both run on hardware you already have.
Nothing hosted beat them on ground truth.

**`claude-opus-5`, `kimi-k3` and `glm-5.3` are next, at 40 of 41 with clean builds.** Opus was
the only model to solve two of the hardest defects by *adding* files — an `AuditLogService` and
a `LoginAttemptTracker` — rather than patching around them. All three leave only `D8`, an
unenforced daily transaction limit.

**`glm-5.3` will not run at this benchmark's defaults**, which is a finding in its own right —
see below. Once configured it is the best of the hosted models bar Opus, and a clear
improvement on `glm-5.2`.

**Model size predicts almost nothing.** `Devstral-2-123B` (75GB) cleared 31 markers in 16
minutes and did not compile. `Qwen3.5-122B` managed 37 and did not compile. Meanwhile
`Muse-Glimmer-30B` cleared 39 and built cleanly. Below about 9B the task collapses entirely:
`Qwen3.5-2B` fixed 9 of 41, and `Qwen3.5-0.8B` returned a change log describing fixes it never
made, several of which describe *re-introducing* the vulnerability.

**Do not rank on the peer review alone.** It disagrees with ground truth often enough to
mislead. `Qwen3-32B` scores 95% on the review delta and fixes 36 of 41 markers with three
compiler errors; `claude-sonnet-5` scores 36% and fixes 37 with one. The review delta is
useful as corroboration and unreliable as a ranking.

---

## How to read these scores

Each model is measured three ways. Only two of them are trustworthy on their own.

**Mechanical (`n/41`)** — direct inspection of the patched source for each seeded defect that
has an unambiguous textual marker. No model is involved, so it is unaffected by review recall
or scorer behaviour. It proves the *shape* of a bug is gone, not that the replacement works.
The 41 markers cover 40 distinct defects: `A6` and `RL2` both test `GetOpenConnection`, which
`ISSUES.md` itself records twice under different categories.

**Build** — the patched tree is compiled and compared against the pristine one, so only newly
introduced errors count. `n × CS` means C# compiler errors. `MSB4025` means the project file
would not load at all. `NU1902` means the code compiled but the build failed on package policy.

**Resolved (`x/y`)** — defects the peer reviewer could name before the patch and cannot name
after, out of the number it genuinely detected beforehand. Rows the scorer credited without
support in the review are excluded from both sides. Report it as the **ratio**, never the raw
count: the baseline ceiling ranged from 51 to 64 across runs, so an unadjusted 34 could be
55% or 59% depending on which day it ran.

---

## Full ranking

Ordered by whether the patch builds, then by mechanical coverage.

| # | Patcher | Mech | Build | Resolved | Ratio | Tokens | Time |
|---|---|---|---|---|---|---|---|
| 1 | **Qwen3.8-27B** | **41/41** | **compiles** | 58/62 | 94% | 17,064 | 12m 9s |
| 2 | **Qwen3.6-27B** | **41/41** | **compiles** | 56/62 | 90% | 21,615 | 9m 52s |
| 3 | **claude-opus-5** | 40/41 | **compiles** | 55/56 | 98% † | 42,406 | 6m 17s |
| 4 | **kimi-k3** | 40/41 | **compiles** | 54/61 | 89% | 38,927 | 6m 33s |
| 5 | **glm-5.3** | 40/41 | **compiles** | 52/62 | 84% | 63,652 | 4m 35s ◊ |
| 6 | **Muse-Glimmer-30B** | 39/41 | **compiles** | 61/61 | 100% | 18,637 | 8m 0s |
| 7 | **glm-5.2** | 39/41 | **compiles** | 47/53 | 89% | 19,922 | 2m 16s |
| 8 | **Gemma-4-31B** | 37/41 | **compiles** | 47/64 | n/c ‡ | 7,245 | 4m 16s |
| 9 | MiniMax-M2.7 | 39/41 | 3 × CS | 37/61 | 61% | 9,427 | 10m 57s |
| 10 | claude-sonnet-5 | 37/41 | 1 × CS | 20/56 | 36% | 55,820 | 7m 7s |
| 11 | Codestral-22B | 37/41 | 1 × CS | 28/51 | 55% | 8,270 | 3m 44s |
| 12 | Qwen3.5-122B | 37/41 | 2 × CS | 31/62 | 50% | 10,902 | 2m 30s |
| 13 | Qwen3-32B | 36/41 | 3 × CS | 58/61 | 95% | 6,543 | 4m 6s |
| 14 | gpt-oss-120B | 32/41 | 1 × CS | 45/61 | 74% | 7,301 | 1m 25s |
| 15 | Qwen3-Coder-30B | 31/41 | **MSB4025** | 34/58 | 59% | 7,134 | 58s |
| 16 | Devstral-2-123B | 31/41 | 1 × CS | 36/53 | 68% | 5,875 | 16m 16s |
| 17 | Qwen3.5-4B | 30/41 | 10 × CS | 24/62 | 39% | 8,924 | 1m 4s |
| 18 | Qwen3-Coder-Next | 29/41 | NU1902 ¶ | 20/61 | 33% | 7,837 | 1m 17s |
| 19 | Qwen3.5-9B | 26/41 | 4 × CS | 34/62 | 55% | 9,161 | 1m 31s |
| 20 | Qwen3.5-2B | 9/41 | 5 × CS | 10/62 | 16% | 6,286 | 28s |
| 21 | Qwen3.5-0.8B | 0/41 | no patch | — | — | 1,203 | 4s |

† Its patched tree was large enough to truncate the reviewer's input, so 98% is an upper bound.
‡ Reviewed by Muse-Glimmer, not Gemma — the figure is not comparable (see Limitations).
¶ Its C# compiles; it set `TreatWarningsAsErrors` and tripped over a pre-existing package
advisory it never touched.
◊ Required `think: false` and `num_predict: 128000`; it will not run at this benchmark's
defaults. See *The glm-5.2 → 5.3 regression*.

---

## Model notes

### The two 27B leaders

`Qwen3.8-27B` and `Qwen3.6-27B` are the only models to clear all 41 markers with a tree that
builds. They spend the most effort of any local model — 17,000 and 21,600 output tokens over
roughly ten minutes — and it shows in the completeness.

One caveat on Qwen3.8-27B. It does not reproduce its own patch: five runs produced 36,091
bytes and one produced 37,687, and the build verdict flipped from failing to passing between
them. Its entry here is the passing run. Qwen3.6-27B produced a byte-identical patch on every
run, days apart, and is the more predictable of the two.

### Where the hosted models landed

`claude-opus-5` is the only model to fix defects by adding well-structured new files rather
than patching in place, which is why it cleared both `A1` (mutable static audit log) and `E7`
(no rate limiting) where most models left them. It also produced the largest patched tree in
the sweep, which is what pushed the reviewer past its input budget.

`claude-sonnet-5` emitted 55,820 output tokens, the most of any model — it would have been
silently truncated under the original 40,000-token ceiling. Its patch is sound on markers
(37/41) and fails on a single missing `using System.Net.Mail;`.

`kimi-k3` and `glm-5.2` both build cleanly with high coverage, and glm-5.2 is the fastest of the
eight that compile, at 2m 16s.

### The glm-5.2 → 5.3 regression

`glm-5.3` writes a better patch than `glm-5.2` — 40 of 41 markers against 39, both compiling —
and it took four attempts to get a valid measurement out of it. Every failure was a
configuration trap that `glm-5.2` did not have:

| `num_predict` | emitted | stop | outcome |
|---|---|---|---|
| 40,000 | 40,000 | `length` | thinking on by default; no file blocks at all |
| 64,000 | — | — | input starved by the harness's own budget arithmetic |
| 64,000 | 64,000 | `length` | 10 of 14 files; scored 37/41 on a truncated patch |
| **128,000** | **63,652** | `stop` | **12 of 14 files, 40/41, compiles** |

Two settings are mandatory and neither is the default. **`think: false`** — 5.3 has reasoning
on by default and spends the entire output budget on it, returning nothing in the answer
field. **`num_predict: 128000`** — it emits ~63,700 tokens for this task against glm-5.2's
19,922, better than three times as much for one extra marker.

The third row is worth dwelling on. At 64,000 it produced a patch that scored **37/41 with a
clean build** and looked like a respectable mid-table result. Two of those four "still present"
markers, `C8` and `CF9`, live in `appsettings.json` and `appsettings.Production.json` — files
the response never reached. The model had not failed them; the patch was cut off first. Only
`done_reason: length` distinguished that run from a complete one, and it was recorded where a
summary would not look. The harness now carries `delta.patch_truncated` and leads the summary
with a warning, because a truncated patch reads as a finished one on every other figure.

`glm-5.3` at 63,652 tokens is also uncomfortably close to the 64,000 that truncated the
previous attempt — same model, same settings, same prompt. Keep the ceiling at 128,000.

### The compiler is the discriminator

Thirteen models emitted code a compiler rejects, and the failures are strikingly similar. The
most common is rewriting one file and breaking a reference from another:

| model | what broke |
|---|---|
| Qwen3-32B | deleted `UpdateUserRequest` while rewriting `UserController.cs` |
| Devstral-2-123B | removed the `_auditLog` field, left a use of it |
| Codestral-22B | rewrote `Models/User.cs`; `TransactionService` can no longer find `User` |
| gpt-oss-120B | replaced string concatenation with `StringBuilder`, no `using System.Text;` |
| MiniMax-M2.7 | replaced MD5 with a call to `HashAlgorithmNames`, which does not exist |
| Qwen3-Coder-30B | emitted a `.csproj` that is not valid XML — nothing compiles at all |

`Qwen3.5-4B` produced ten errors from one pass, referencing constants and fields it never
declared. `Qwen3.5-9B` rewrote call sites to use `ExecuteNonQuery(sql, params)` and
`BeginTransaction()` without adding either to `DatabaseHelper` — the intent was right and the
change half-applied, which is worse than not attempting it.

### The bottom of the field

`Qwen3.5-2B` fixed 9 of 41 in 28 seconds, leaving every SQL injection, the MD5 hashing, the
committed password and both authorization gaps. `Qwen3.5-0.8B` produced no code at all: 1,203
tokens of change log claiming twenty-plus fixes, several of which describe re-introducing the
defect — *"Enabled CORS policy using `AllowAnyOrigin()`"*, *"Updated package reference to
Newtonsoft.Json 12.0.3 (known vulnerability)"*. It is not a model that tried and failed; it is
one that reported success without attempting the work.

### What the field found hardest

Across the nineteen models that produced a patch:

| defect | survived | |
|---|---|---|
| `CF9` | 13/19 | no `appsettings.Production.json` created |
| `R3` | 12/19 | `GenerateJwtToken` left as one long method |
| `E7` | 12/19 | no rate limiting or account lockout |
| `A6` / `RL2` | 10/19 | connection-leaking `GetOpenConnection` retained |
| `D8` | 8/19 | daily transaction limit never enforced |

The pattern is consistent: models fix what is visibly wrong in a line of code and skip what
requires adding something that is not there. Every one of these five needs new code rather
than a corrected expression.

---

## Running on a 32GB corporate laptop

Assume ~20GB usable after Chrome, Teams and Outlook. Weights and KV figures are from the
review benchmark's measurements at 64k context.

| Model | Weights | Total @64k | Fits in 20GB? | Mech | Build |
|---|---|---|---|---|---|
| **Muse-Glimmer-30B** | 16.1 GB | **19.6 GB** | **Yes, tight** | **39/41** | **compiles** |
| Gemma-4-31B | 18.7 GB | ~20 GB | Marginal | 37/41 | compiles |
| Qwen3-Coder-30B | 14.7 GB | 21.1 GB | Marginal | 31/41 | MSB4025 |
| Qwen3.5-4B | 3.0 GB | 11.6 GB | Yes, comfortably | 30/41 | 10 × CS |
| Qwen3.5-9B | 5.4 GB | 14.0 GB | Yes, comfortably | 26/41 | 4 × CS |
| Qwen3.5-2B | 1.2 GB | 4.4 GB | Yes, trivially | 9/41 | 5 × CS |
| Qwen3.8-27B / Qwen3.6-27B | 15.8 GB | 33.2 GB | No | 41/41 | compiles |

**On a 32GB laptop, use `Muse-Glimmer-30B`.** It is the only model that both fits and produces
code that compiles — 39 of 41 markers, leaving `E7` and `CF9`. It is tight at 19.6GB, so close
what you can spare.

**Below that, patching is not viable.** Neither `Qwen3.5-9B` nor `Qwen3.5-4B` produced a tree
that builds, and both left a quarter to a third of the defects in place. They are respectable
*reviewers* at that size — `Qwen3.5-9B` is the laptop recommendation in the review benchmark —
but writing correct C# is a different task and the gap is stark.

**If you can reach a server, use it.** The 27B models need 33GB and are the only local option
that clears every marker.

---

## Recommendation

**Production, local: `Qwen3.8-27B-imatrix:Q4_K_S` or `Qwen3.6-27B:Q4_K_S`.** All 41 markers,
clean builds, ~10 minutes. Prefer Qwen3.6 if reproducibility matters — it produces an
identical patch every run, where Qwen3.8 does not.

**Laptop: `Muse-Glimmer-30B-imatrix:Q4_K_S`.** The only sub-20GB model whose output compiles.

**If a hosted call is acceptable: `claude-opus-5`.** 40 of 41 with a clean build, and the only
model that added new files where the fix required them. `kimi-k3` and `glm-5.3` match it on
coverage for less money — but budget `num_predict: 128000` and `think: false` for glm-5.3, which
will otherwise return nothing usable.

**Never use for patching:** `Qwen3.5-2B` and `Qwen3.5-0.8B` — one fixes almost nothing, the
other fabricates having done so.

**Always run the build check.** Four of the thirteen failures cost one line — a missing `using`,
a dropped field. Without a compiler in the loop, all thirteen would have been scored as
successful patches, and four of them would have ranked in the top half.

---

## Methodology

- **Task:** given the full source and `ISSUES.md`, return rewritten files fixing the seeded
  defects, as `### File: <path>` blocks.
- **Peer review:** every patch was reviewed by `Gemma-4-31B-it-imatrix:Q4_K_M` at temperature
  0 and scored by `Qwen3-Coder-30B-imatrix:Q3_K_M`, both pinned for the whole sweep. The one
  exception is Gemma's own patch, which cannot be reviewed by itself.
- **Mechanical verification:** 41 markers checked directly against the patched source, no
  model involved. Covers 40 distinct defects of the 69 in `ISSUES.md`.
- **Build check:** both trees compiled with `dotnet build`; only errors absent from the
  pristine tree are attributed to the patcher. `NU1605` is suppressed — the sample project has
  a pre-existing package downgrade, and an unresolved restore stops compilation before any C#
  diagnostic appears.
- **Settings:** temperature 0, 65,536 context, 40,000 output tokens for local models; 64,000
  for the Anthropic models, which need it. Recorded per run in `config`.
- **Per-model settings:** [../docs/CONFIG_SETTINGS.md](../docs/CONFIG_SETTINGS.md) and the
  `modelfiles/` directory.
- **Provenance:** every run records its harness commit, all three prompt digests and the
  `ISSUES.md` digest. Runs span commits `83ba9c8`–`2915add`; the changes in that range affect
  reporting and diagnostics, not scoring.

---

## Known limitations

**The peer review delta is noisy, and the reviewer dominates it.** One fixed patch
(Qwen3.6-27B, byte-identical across runs) was reviewed by three models:

```
Qwen3.8-27B reviewer   resolved 26      Muse-Glimmer   resolved 31      Gemma   resolved 56
```

Worse than the spread, Muse-Glimmer *inverted* the ranking — it scored a 37/41 patch 25 points
above a 41/41 one. That is why the sweep pinned Gemma throughout, and why Gemma's own row
carries no comparable figure. Six repeat runs of one patcher under Gemma gave 53–60, so
differences under about 7 points are not meaningful.

**The baseline ceiling drifted from 51 to 64** across runs, with the same reviewer on the same
pristine tree. The ratio column corrects for it; the raw count does not.

**A marker proves a bug's shape is gone, not that the replacement is correct.** MiniMax-M2.7
and Muse-Glimmer both cleared 39 of 41, but MiniMax's replacement for the MD5 hashing calls a
type that does not exist. The build check is what separates them.

**`Qwen3-Coder-30B` was scored by itself.** It is the pinned scorer and also a patcher. The
scorer sees only the review and `ISSUES.md`, never the code, so the conflict is weaker than
reviewer-as-patcher — but it is not zero.

**Opus's review delta was measured on a truncated view.** Its patched tree exceeded the
reviewer's input budget, the only run where that happened. Its 98% is an upper bound; its
mechanical and build results are unaffected.

**The output ceiling silently invalidates a run.** A patcher cut off mid-response still
returns parseable file blocks, so the harness applies them and scores a fragment as though it
were finished — and a defect in a file the model never reached is recorded as unfixed.
`claude-opus-5` and `glm-5.3` both hit this, and `kimi-k3` came within 1,073 tokens of it.
Every run now records `delta.patch_truncated`, but three of the twenty-one needed a raised
`num_predict` to produce a valid measurement at all, and the right ceiling is not knowable in
advance.

**Two models needed non-default settings to run.** `glm-5.3` and `Gemma-4-31B` both have
reasoning enabled by default and spend their entire output budget on it, returning nothing in
the answer field; both need `think: false`. `think` unset does not mean off — it means the
model decides. Per-model settings are in
[../docs/CONFIG_SETTINGS.md](../docs/CONFIG_SETTINGS.md).

**Single runs.** Every model was patched once. Temperature 0 is deterministic only within a
backend session — Qwen3.8-27B produced two materially different patches across restarts, one
of which compiled and one of which did not.
