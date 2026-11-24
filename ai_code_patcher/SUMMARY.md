# AI Code Patcher Benchmark — Results Summary

Twenty-five models were asked to *fix* the 70 seeded defects in `SampleBankingApp/`, rather than
find them. Each received the same source listing and the same issue list, and returned
rewritten files. Every patch was then measured three ways: a peer review scored against
`ISSUES.md`, a direct inspection of the patched source, and a compiler.

The companion documents are [../ai_code_review_results/SUMMARY.md](../ai_code_review_results/SUMMARY.md)
(finding defects) and [../ai_qa_scorer_results/SUMMARY.md](../ai_qa_scorer_results/SUMMARY.md)
(grading reviews).

---

## Executive Summary

**Eleven of twenty-five produced code that compiles.** That is the finding. Fourteen models
returned patches that a C# compiler rejects — inventing methods that do not exist, deleting a
class while still referencing it, dropping a `using` directive, or in one case emitting a
project file that is not valid XML. A patch that does not build is not a patch, however many
defects it appears to remove.

**The two 27B local models are the recommendation: `Qwen3.8-27B` and `Qwen3.6-27B`.** Both
cleared all 41 mechanical markers, both compile, and both run on hardware you already have.
Nothing hosted beat them on ground truth.

**`claude-opus-5`, `kimi-k3.1-pro`, `kimi-k3`, `glm-5.3` and `MiniMax-M3` are next, at 40 of 41
with clean builds.** Opus was the only model to solve two of the hardest defects by *adding* files — an
`AuditLogService` and a `LoginAttemptTracker` — rather than patching around them. The first
four leave only `D8`, an unenforced daily transaction limit. `MiniMax-M3` clears `D8` and
leaves `L5` instead — the missing self-transfer guard, and the only marker in the field that no
other serious patcher missed.

**`glm-5.3` will not run at this benchmark's defaults**, which is a finding in its own right —
see below. Once configured it is the best of the hosted models bar Opus, and a clear
improvement on `glm-5.2`.

**`inkling-2-small` is the fast one.** It cleared 39 of 41 markers and compiles, in **43
seconds** — three times quicker than `glm-5.2`, the next-fastest patch that builds, and eleven
times quicker than `Muse-Glimmer-30B` for the same marker count. It needed no special settings.

**`hy4` is the near miss.** It cleared 39 of 41 markers in 41 seconds, faster than anything
that fixed more than a handful of defects — and its tree fails to build on one missing `using`
directive. Like `glm-5.3`, it returns nothing at the defaults.

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
| 4 | **kimi-k3.1-pro** | 40/41 | **compiles** | 60/61 | 98% | 57,789 | 10m 35s § |
| 5 | **kimi-k3** | 40/41 | **compiles** | 54/61 | 89% | 38,927 | 6m 33s |
| 6 | **glm-5.3** | 40/41 | **compiles** | 52/62 | 84% | 63,652 | 4m 35s ◊ |
| 7 | **MiniMax-M3** | 40/41 | **compiles** | 31/61 | n/c ‡ | 41,834 | 5m 30s |
| 8 | **Muse-Glimmer-30B** | 39/41 | **compiles** | 61/61 | 100% | 18,637 | 8m 0s |
| 9 | **glm-5.2** | 39/41 | **compiles** | 47/53 | 89% | 19,922 | 2m 16s |
| 10 | **inkling-2-small** | 39/41 | **compiles** | 51/65 | n/c ※ | 36,859 | 43s |
| 11 | **Gemma-4-31B** | 37/41 | **compiles** | 47/64 | n/c ‡ | 7,245 | 4m 16s |
| 12 | hy4 | 39/41 | 1 × CS | 38/62 | 61% | 8,419 | 41s ‖ |
| 13 | MiniMax-M2.7 | 39/41 | 3 × CS | 37/61 | 61% | 9,427 | 10m 57s |
| 14 | claude-sonnet-5 | 37/41 | 1 × CS | 20/56 | 36% | 55,820 | 7m 7s |
| 15 | Codestral-22B | 37/41 | 1 × CS | 28/51 | 55% | 8,270 | 3m 44s |
| 16 | Qwen3.5-122B | 37/41 | 2 × CS | 31/62 | 50% | 10,902 | 2m 30s |
| 17 | Qwen3-32B | 36/41 | 3 × CS | 58/61 | 95% | 6,543 | 4m 6s |
| 18 | gpt-oss-120B | 32/41 | 1 × CS | 45/61 | 74% | 7,301 | 1m 25s |
| 19 | Qwen3-Coder-30B | 31/41 | **MSB4025** | 34/58 | 59% | 7,134 | 58s |
| 20 | Devstral-2-123B | 31/41 | 1 × CS | 36/53 | 68% | 5,875 | 16m 16s |
| 21 | Qwen3.5-4B | 30/41 | 10 × CS | 24/62 | 39% | 8,924 | 1m 4s |
| 22 | Qwen3-Coder-Next | 29/41 | NU1902 ¶ | 20/61 | 33% | 7,837 | 1m 17s |
| 23 | Qwen3.5-9B | 26/41 | 4 × CS | 34/62 | 55% | 9,161 | 1m 31s |
| 24 | Qwen3.5-2B | 9/41 | 5 × CS | 10/62 | 16% | 6,286 | 28s |
| 25 | Qwen3.5-0.8B | 0/41 | no patch | — | — | 1,203 | 4s |

† Its patched tree was large enough to truncate the reviewer's input, so 98% is an upper bound.
‡ Reviewed by Muse-Glimmer, not Gemma — the figure is not comparable (see Limitations). Applies
to `Gemma-4-31B`, which cannot review its own patch, and to `MiniMax-M3`.
¶ Its C# compiles; it set `TreatWarningsAsErrors` and tripped over a pre-existing package
advisory it never touched.
◊ Required `think: false` and `num_predict: 128000`; it will not run at this benchmark's
defaults. See *The glm-5.2 → 5.3 regression*.
§ Required `num_predict: 64000`; at the default 40,000 the patch is cut off after 7 of 13
files. See *kimi-k3.1-pro*.
‖ Required `think: false`; at the defaults it spends the whole 40,000-token budget on reasoning
and returns no patch. See *hy4*.
※ The post-patch scorecard was cut off: the pinned scorer stopped on its 24,000-token cap, where
it normally needs about 4,100, so the post-patch counts — and Resolved with them — are not
reliable. Its mechanical and build results do not involve the scorer. See *inkling-2-small*.

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

### MiniMax-M3 — 40/41, and the only model to miss `L5`

M3 rewrote 13 files, compiles clean, and clears 40 of the 41 markers including all five of the
defects the field found hardest — `CF9`, `R3`, `E7`, `A6`/`RL2` and `D8`. It is the only patcher
above `Qwen3.5-2B` to leave `L5`, the missing self-transfer guard in `Transfer`. Every other
model in the top seven fixed `L5`; the four that also cleared 40 of 41 — `claude-opus-5`,
`kimi-k3.1-pro`, `kimi-k3` and `glm-5.3` — left `D8` instead. Adding a `fromUserId == toUserId` check is a
one-line fix, so this reads as an oversight rather than a capability limit.

At 41,834 output tokens in 5m 30s it is the fifth-heaviest patch in the sweep, behind
`glm-5.3`, `kimi-k3.1-pro`, `claude-sonnet-5` and `claude-opus-5`, and it finished naturally against a 64,000
ceiling — no truncation, and 22,000 tokens of headroom.

**Its Resolved figure is not comparable.** This run was peer-reviewed by `Muse-Glimmer-30B`
rather than the pinned `Gemma-4-31B`, the same substitution that makes `Gemma-4-31B`'s own row
incomparable. Muse resolves far fewer issues than Gemma on identical patches (31 against 56 on
one fixed tree) and has been observed to invert the ranking outright, so the 31/61 shown above
should not be read against any other row. Its mechanical and build results are unaffected —
neither involves a reviewer. Re-running M3 under Gemma would settle it.

Also worth noting against its predecessor: `MiniMax-M2.7` cleared 39 markers but did not
compile, because it replaced MD5 with a call to a `HashAlgorithmNames` type that does not
exist. M3 clears more and builds.

### Where the hosted models landed

`claude-opus-5` is the only model to fix defects by adding well-structured new files rather
than patching in place, which is why it cleared both `A1` (mutable static audit log) and `E7`
(no rate limiting) where most models left them. It also produced the largest patched tree in
the sweep, which is what pushed the reviewer past its input budget.

`claude-sonnet-5` emitted 55,820 output tokens, the most of any model — it would have been
silently truncated under the original 40,000-token ceiling. Its patch is sound on markers
(37/41) and fails on a single missing `using System.Net.Mail;`.

`kimi-k3` and `glm-5.2` both build cleanly with high coverage, and glm-5.2, at 2m 16s, is the
fastest of the eleven that compile after `inkling-2-small`.

### kimi-k3.1-pro — the same patch as kimi-k3, for half as much again

`kimi-k3.1-pro` rewrote the same 13 files as `kimi-k3`, compiles clean, and clears the same 40
of 41 markers with the same single miss, `D8`. On ground truth the two are indistinguishable.

Its Resolved figure is higher — 60/61 against 54/61 — and that gap should not be read as an
improvement. Both runs started from 61 detectable defects under the same pinned reviewer; the
whole difference is six rows Gemma rated Partial after `kimi-k3`'s patch and none after this
one. Six points is inside the 7-point spread that repeat runs of a single patcher produce
under Gemma (see Limitations).

What did change is the cost: 57,789 output tokens in 10m 35s against 38,927 in 6m 33s — 48%
more tokens and 62% longer.

**It will not complete at the default output ceiling.** The first attempt, at
`num_predict: 40000`, stopped on `length` with 7 of 13 files written and `AuthService.cs` cut
off mid-method. The text that arrived was 22,480 bytes — a small fraction of 40,000 tokens —
so most of the budget was spent before the answer began; the likely cause is reasoning, which
`think` unset leaves on, though the thinking output was not captured to confirm it. That
fragment scored 24 resolved with three compiler errors, all in `UserService.cs` and
`TransactionService.cs`: the model had changed `DatabaseHelper`'s method signatures and was
cut off before reaching the callers. At 64,000 it finished naturally, at 90% of the ceiling.

### hy4 — 39 of 41 in 41 seconds, and one missing `using`

`hy4` rewrote 13 files in 40.8 seconds on 8,419 output tokens. Only `Qwen3.5-2B` and
`Qwen3.5-0.8B` were quicker, and they fixed 9 markers and none. It cleared 39 of 41, leaving
`R3` — `GenerateJwtToken` is still one long method — and `D8`, the unenforced daily limit. Both
are among the five defects the field found hardest.

**It does not compile.** `TransactionService.cs` line 143 catches `SmtpException`, and the file
has no `using System.Net.Mail;` — one `CS0246`, the only new error the compiler reported. It is
the same one-line failure as `claude-sonnet-5`, and it puts a patch that would otherwise sit
beside `Muse-Glimmer-30B`, `glm-5.2` and `inkling-2-small` below the line.

Its Resolved figure is 38 of 62, or 61%: Gemma could name 62 defects before the patch and 24
after. That is level with `MiniMax-M2.7`, which also cleared 39 markers and also failed to
build.

**It will not run at the defaults.** The first attempt, with `think` unset and
`num_predict: 40000`, spent all 40,000 tokens on reasoning, stopped on `length`, and returned
no file blocks at all. With `think: false` it finished naturally on 8,419 tokens — a fifth of
the default cap. The recorded run also raised `num_predict` to 100,000, which turned out not to
be needed.

### inkling-2-small — 39 of 41 in 43 seconds, and it builds

`inkling-2-small` rewrote 13 files in 43.1 seconds on 36,859 output tokens and compiles clean,
with no new errors. It cleared 39 of 41 markers, leaving the same two as `hy4`: `R3`,
`GenerateJwtToken` still one long method, and `D8`, the unenforced daily limit. Of the eleven
patches that build it is by some distance the quickest — `glm-5.2` took 2m 16s and
`Muse-Glimmer-30B`, the other 39-marker local patch, 8 minutes.

It is not a short patch produced quickly. At 36,859 tokens it is the heaviest of the 39-marker
patches, and it arrived at 855 tokens a second. It ran with `think` unset, which leaves
reasoning to the model, and finished naturally. It was given a 100,000-token cap; 36,859 would have fitted
the default 40,000, at 92% of it.

**Its Resolved figure is not usable.** Gemma reviewed the patched tree normally — 5,253 output
tokens, a natural stop — but the pinned scorer then ran to its 24,000-token cap grading that
review, against about 4,100 on every other run, and stopped on `length`. It is the only
truncated scorecard in the sweep. The 51/65 it produced (1 Found, 24 Partial, 45 Missed after the
patch) may count rows the scorer never reached as Missed, which would inflate Resolved, and the
raw output was not kept to tell. Re-scoring the archived review would settle it.

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

Fourteen models emitted code a compiler rejects, and the failures are strikingly similar. The
most common is rewriting one file and breaking a reference from another:

| model | what broke |
|---|---|
| Qwen3-32B | deleted `UpdateUserRequest` while rewriting `UserController.cs` |
| Devstral-2-123B | removed the `_auditLog` field, left a use of it |
| Codestral-22B | rewrote `Models/User.cs`; `TransactionService` can no longer find `User` |
| gpt-oss-120B | replaced string concatenation with `StringBuilder`, no `using System.Text;` |
| hy4 | caught `SmtpException` in `TransactionService.cs`, no `using System.Net.Mail;` |
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

Across the twenty-three models that produced a patch:

| defect | survived | |
|---|---|---|
| `R3` | 14/23 | `GenerateJwtToken` left as one long method |
| `CF9` | 13/23 | no `appsettings.Production.json` created |
| `E7` | 12/23 | no rate limiting or account lockout |
| `D8` | 11/23 | daily transaction limit never enforced |
| `A6` / `RL2` | 10/23 | connection-leaking `GetOpenConnection` retained |

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
model that added new files where the fix required them. `kimi-k3`, `glm-5.3` and `MiniMax-M3`
match it on coverage for less money — but budget `num_predict: 128000` and `think: false` for
glm-5.3, which will otherwise return nothing usable, and note that M3's peer-review figure was
measured against a different reviewer and cannot be compared with the rest of the table.
`kimi-k3.1-pro` matches them too, but prefer `kimi-k3`: the same markers and the same miss for
two-thirds of the tokens, and it completes at the default ceiling where 3.1-pro needs
`num_predict: 64000`.

**When the turnaround matters: `inkling-2-small`.** 39 of 41 with a clean build in 43 seconds,
at the default settings — two markers behind the two 27B leaders, in under a tenth of their time.

**Never use for patching:** `Qwen3.5-2B` and `Qwen3.5-0.8B` — one fixes almost nothing, the
other fabricates having done so.

**Always run the build check.** Five of the fourteen failures cost one line — a missing `using`,
a dropped field. Without a compiler in the loop, all fourteen would have been scored as
successful patches, and five of them would have ranked in the top half.

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
  for the Anthropic models, `MiniMax-M3` and `kimi-k3.1-pro`; 128,000 for `glm-5.3`; 100,000
  with `think: false` for `hy4`; 100,000 for `inkling-2-small`. Recorded per run in `config`.
- **Per-model settings:** [../docs/CONFIG_SETTINGS.md](../docs/CONFIG_SETTINGS.md) and the
  `modelfiles/` directory.
- **Provenance:** every run records its harness commit, all three prompt digests and the
  `ISSUES.md` digest. Runs span commits `83ba9c8`–`afe34f0`; the changes in that range affect
  reporting, diagnostics and input budgeting, not scoring.

---

## Known limitations

**The peer review delta is noisy, and the reviewer dominates it.** One fixed patch
(Qwen3.6-27B, byte-identical across runs) was reviewed by three models:

```
Qwen3.8-27B reviewer   resolved 26      Muse-Glimmer   resolved 31      Gemma   resolved 56
```

Worse than the spread, Muse-Glimmer *inverted* the ranking — it scored a 37/41 patch 25 points
above a 41/41 one. That is why the sweep pinned Gemma throughout, and why the two rows reviewed
by Muse — `Gemma-4-31B`, which cannot review itself, and `MiniMax-M3` — carry no comparable
figure. Six repeat runs of one patcher under Gemma gave 53–60, so differences under about 7
points are not meaningful.

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
`claude-opus-5`, `glm-5.3` and `kimi-k3.1-pro` all hit this, and `kimi-k3` came within 1,073
tokens of it. Every run now records `delta.patch_truncated`, but four of the twenty-five
needed a raised `num_predict` to produce a valid measurement at all, and the right ceiling is not knowable in
advance.

**The scorer can be cut off too, and nothing flags it.** `delta.patch_truncated` covers the
patcher only. `inkling-2-small`'s post-patch scorecard stopped on the scorer's 24,000-token cap
and was reported as an ordinary result; the truncation shows only in
`post_patch.scoring.done_reason`. Its Resolved figure is marked not comparable for that reason.

**Three models needed non-default settings to run.** `glm-5.3`, `hy4` and `Gemma-4-31B` all have
reasoning enabled by default and spend their entire output budget on it, returning nothing in
the answer field; all three need `think: false`. `think` unset does not mean off — it means the
model decides. Per-model settings are in
[../docs/CONFIG_SETTINGS.md](../docs/CONFIG_SETTINGS.md).

**Single runs.** Every model was patched once. Temperature 0 is deterministic only within a
backend session — Qwen3.8-27B produced two materially different patches across restarts, one
of which compiled and one of which did not.
