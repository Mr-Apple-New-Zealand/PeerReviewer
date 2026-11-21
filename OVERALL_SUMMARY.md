# Model Benchmark — Overall Summary

Twenty-three models were measured in three distinct roles against the same deliberately-flawed
C# application (`SampleBankingApp/`) and the same 70 seeded defects (`ISSUES.md`):

| Role | Question it answers | Detail |
|---|---|---|
| **Reviewer** | Can the model *find* the defects? | [ai_code_review_results/SUMMARY.md](ai_code_review_results/SUMMARY.md) |
| **Patcher** | Can it *fix* them, and does the result compile? | [ai_code_patcher/SUMMARY.md](ai_code_patcher/SUMMARY.md) |
| **Scorer** | Can it *grade* a review honestly? | [ai_qa_scorer_results/SUMMARY.md](ai_qa_scorer_results/SUMMARY.md) |

Every model received identical prompts, an identical system prompt and identical sampler
settings (temperature 0, 65,536 context). Per-model deviations are in
[docs/CONFIG_SETTINGS.md](docs/CONFIG_SETTINGS.md).

---

## Headline findings

**The three roles are different skills, and performance in one does not predict the others.**
`Qwen3-32B` grades two of three test reviews flawlessly and then fails outright, writes a patch
that clears 36 of 41 markers but does not compile, and produces one of the weakest reviews in
the field. `Qwen3.5-9B` is a near-perfect scorer at 5.4GB and cannot write a C# file that
builds. `Qwen3.8-27B` writes the best patch of any model and ranks eleventh as a reviewer. Pick a
model per role, not a model.

**Grading is the easy job. Fixing is the hard one.** Thirteen of twenty-three score a perfect
100.0% as scorers. Ten of twenty-three produce a patch that compiles. The floor differs too:
usable grading starts around 5GB, usable reviewing around 3GB, and reliable patching does not
begin until about 16GB.

**Size predicts almost nothing.** `Devstral-2-123B` (75GB) sits in the bottom third of all three
tables — 32 as a reviewer, a patch that does not build, and a scorer that credits 63 of 70
issues on a review naming 16. `Qwen3.5-4B` (3GB) out-reviews it by 23 points. `MiniMax-M2.7`
(99GB) is mid-table as a reviewer and unusable as a scorer.

**Generation matters far more than parameter count.** The largest single improvement measured
anywhere in this benchmark is `MiniMax-M2.7` to `MiniMax-M3`:

```
reviewer   57 adjusted, 97% precision   ->   70 adjusted, 100% precision  (the only clean 70)
scorer     credits 70 of 70 on a decoy  ->   credits exactly the 16 named
patcher    39/41 but does not compile   ->   40/41 and compiles
```

The effect runs the other way too: `Qwen3.6-27B` to `Qwen3.8-27B` *loses* three review points
while gaining 12 points of precision, and `glm-5.2` to `glm-5.3` writes a better patch but will
not run at this benchmark's defaults at all. `kimi-k3` to `kimi-k3.1-pro` is a step sideways at
a higher price: the same 69 as a reviewer and the same 40 of 41 as a patcher for roughly half
as much output again, a drop from 100.0% to 97.0% as a scorer, and it will not complete a
review or a patch at the default output cap.

**Every layer needed a check that is not a model.** The compiler rejected thirteen patches the
peer review scored as successes, four of them for a single missing line. The grounding and
spot-check machinery corrected up to 17 rows on a single scorecard. The decoy test exposed three
scorers that pass every other test while crediting almost everything. Remove any one of those
checks and the corresponding ranking inverts.

---

## The whole field, all three roles

Sorted by review score.

| Model | Hosted | Review adj/70 | Precision | Patch mech/41 | Build | Scorer | Ungrounded |
|---|---|---|---|---|---|---|---|
| **MiniMax-M3** | yes | **70** | **100% (40)** | 40/41 | **compiles** | 100.0% | **0** |
| claude-opus-5 | yes | 69 | **100% (39)** | 40/41 | **compiles** | 100.0% | **0** |
| kimi-k3.1-pro | yes | 69 | **100% (39)** | 40/41 | **compiles** | 97.0% ² | 5 |
| claude-sonnet-5 | yes | 69 | 98% (40) | 37/41 | 1 × CS | 100.0% | **0** |
| kimi-k3 | yes | 69 | 98% (40) | 40/41 | **compiles** | 100.0% | **0** |
| glm-5.2 | yes | 69 | 98% (40) | 39/41 | **compiles** | 100.0% | **0** |
| glm-5.3 | yes | 69 ¹ | 98% (40) | 40/41 | **compiles** | 100.0% | **0** |
| Qwen3.5-122B | no | 66 | 92% (39) | 37/41 | 2 × CS | 98.0% | 4 |
| Qwen3.6-27B | no | 65 | 88% (40) | **41/41** | **compiles** | 100.0% | **0** |
| Muse-Glimmer-30B | no | 64 | 87% (39) | 39/41 | **compiles** | 100.0% | **0** |
| **Qwen3.8-27B** | no | 62 | **100% (38)** | **41/41** | **compiles** | 100.0% | **0** |
| gpt-oss-120B | no | 58 | 89% (35) | 32/41 | 1 × CS | 100.0% | **0** |
| Qwen3-Coder-Next | no | 58 | 86% (35) | 29/41 | NU1902 | 98.5% | 3 |
| MiniMax-M2.7 | no | 57 | 97% (32) | 39/41 | 3 × CS | 100.0% | **52** |
| Qwen3.5-4B | no | 55 | 86% (35) | 30/41 | 10 × CS | 97.2% | 1 |
| Gemma-4-31B | no | 54 | 97% (33) | 37/41 | **compiles** | 100.0% | **0** |
| **Qwen3.5-9B** | no | 41 | **100% (24)** | 26/41 | 4 × CS | 99.5% | **0** |
| Qwen3-Coder-30B | no | 34 | 88% (17) | 31/41 | MSB4025 | 100.0% | 1 |
| Devstral-2-123B | no | 32 | 100% (18) | 31/41 | 1 × CS | 92.0% | **58** |
| Qwen3-32B | no | 25 | 78% (18) | 36/41 | 3 × CS | **0.0%** | 0 |
| Qwen3.5-2B | no | 22 | 100% (13) | 9/41 | 5 × CS | **0.0%** | **84** |
| Codestral-22B | no | 22 | 93% (14) | 37/41 | 1 × CS | 99.2% | **49** |
| Qwen3.5-0.8B | no | 19 | 82% (11) | 0/41 | no patch | **0.0%** | 69 |

¹ `glm-5.3` wrote 102,642 characters of unmarked reasoning into its answer, and one credited row
came from a draft it discarded. Read it as 68.
² `kimi-k3.1-pro` graded every row correctly. The five ungrounded rows are genuine findings whose
notes paraphrase the review instead of quoting it, which the grounding check removes.

**Reading the columns.** Precision is the share of independently checkable findings that
survived verification, with sample size in brackets — `100% (13)` is much weaker evidence than
`100% (40)`. Ungrounded counts rows a scorer credited with a quotation the review does not
contain; it does not lower the Score, and it is the column that separates a scorer which grades
from one that guesses. The patcher's peer-review Resolved column is deliberately omitted here
because it is not comparable across rows — see *Things to be aware of*.

---

## Best model for each role

Read down the role you need. Every figure is from that role's own benchmark, so a
model's position here does not carry across the three tables.

### Reviewer — can it find the defects?

| # | Model | Adjusted /70 | Precision | Hosted | Why this one |
|---|---|---|---|---|---|
| 1 | **`MiniMax-M3`** | **70** | **100% (40)** | yes | The only clean sweep in the field, and economical with it: 12,497 output tokens in 1m 55s |
| 2 | **`claude-opus-5`** | 69 | **100% (39)** | yes | Clean on every integrity check, on the largest sample measured — 374 citations, all valid |
| 3 | **`glm-5.2`** | 69 | 98% (40) | yes | The same score in **47 seconds**, the fastest review measured anywhere |
| 4 | **`Qwen3.6-27B`** | 65 | 88% (40) | no | Best local recall. Treat its findings as leads: reading found ~9 further over-credits |
| 5 | **`Qwen3.8-27B`** | 62 | **100% (38)** | no | Best local *precision*. Finds less, but what it reports can be acted on without checking |

The choice between the two local models is recall against trust. `Qwen3.6-27B` claims all 70
and is right about 88% of the time; `Qwen3.8-27B` declines eight outright and is right about all
of them. For a pipeline with a verification stage behind it, take the recall. For a human
reading the output directly, take the precision.

**For a 32GB laptop:** `Qwen3.5-9B` at 14GB, 41/70 but **100% precision** on 24 checkable
findings, in 42 seconds.

### Patcher — can it fix them, and does the result build?

| # | Model | Markers /41 | Build | Hosted | Why this one |
|---|---|---|---|---|---|
| 1 | **`Qwen3.8-27B`** | **41/41** | **compiles** | no | One of only two perfect mechanical scores with a tree that builds. Free and local |
| 2 | **`Qwen3.6-27B`** | **41/41** | **compiles** | no | The same result, and byte-identical across runs days apart — the only model that reproduced exactly |
| 3 | **`claude-opus-5`** | 40/41 | **compiles** | yes | The only model that fixed defects by *adding* well-structured files rather than patching around them |
| 4 | **`kimi-k3`** | 40/41 | **compiles** | yes | Equivalent result, roughly the same time |
| 5 | **`glm-5.2`** | 39/41 | **compiles** | yes | Two markers short but by far the fastest that compiles, at **2m 16s** |

**Build status is the column that matters.** Thirteen of twenty-three patches were scored as
successes by the peer reviewer and then failed to compile, four of them for a single missing
line. A model with a high marker count and a failing build has not fixed anything.

### Scorer — can it grade a review honestly?

| # | Model | Score | Ungrounded | Decoy | Time | Why this one |
|---|---|---|---|---|---|---|
| 1 | **`Qwen3-Coder-30B`** | 100.0% | 1 | 19/70 | **30.0s** | Free, local, fast, and reproduces reference wording verbatim so its sheets stay auditable |
| 2 | **`glm-5.2`** | 100.0% | **0** | 16/70 | **25.6s** | Fastest measured, and a perfect decoy result |
| 3 | **`MiniMax-M3`** | 100.0% | **0** | **16/70** | 44.0s | Perfect decoy with only 5 misaligned rows — the cleanest sheet of any fast scorer |
| 4 | **`Qwen3.5-9B`** | 99.5% | **0** | 18/70 | 41.1s | 5.4GB. Zero ungrounded and zero misaligned; the best laptop scorer by a distance |
| 5 | **`Muse-Glimmer-30B`** | 100.0% | **0** | 16/70 | 266.1s | Flawless but slow. Only worth it when the grading itself is in question |

**The headline Score does not rank scorers** — thirteen models tie at 100.0%. The two columns
that separate them are Ungrounded, which counts rows credited with a quotation the review does
not contain, and the decoy result, where a correct answer is 16–18 and three models credit
essentially everything.

---

## The patcher field in full

Patching is the most demanding of the three roles and the only one with an independent verdict
attached, so the whole table is worth having. Mech is mechanical markers cleared; Build is a
differential compile of the patched tree against the pristine one; Resolved is the peer
reviewer's own count, which is **not comparable between rows** and is included only for
completeness.

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
| 10 | **Gemma-4-31B** | 37/41 | **compiles** | 47/64 | n/c ‡ | 7,245 | 4m 16s |
| 11 | MiniMax-M2.7 | 39/41 | 3 × CS | 37/61 | 61% | 9,427 | 10m 57s |
| 12 | claude-sonnet-5 | 37/41 | 1 × CS | 20/56 | 36% | 55,820 | 7m 7s |
| 13 | Codestral-22B | 37/41 | 1 × CS | 28/51 | 55% | 8,270 | 3m 44s |
| 14 | Qwen3.5-122B | 37/41 | 2 × CS | 31/62 | 50% | 10,902 | 2m 30s |
| 15 | Qwen3-32B | 36/41 | 3 × CS | 58/61 | 95% | 6,543 | 4m 6s |
| 16 | gpt-oss-120B | 32/41 | 1 × CS | 45/61 | 74% | 7,301 | 1m 25s |
| 17 | Qwen3-Coder-30B | 31/41 | **MSB4025** | 34/58 | 59% | 7,134 | 58s |
| 18 | Devstral-2-123B | 31/41 | 1 × CS | 36/53 | 68% | 5,875 | 16m 16s |
| 19 | Qwen3.5-4B | 30/41 | 10 × CS | 24/62 | 39% | 8,924 | 1m 4s |
| 20 | Qwen3-Coder-Next | 29/41 | NU1902 ¶ | 20/61 | 33% | 7,837 | 1m 17s |
| 21 | Qwen3.5-9B | 26/41 | 4 × CS | 34/62 | 55% | 9,161 | 1m 31s |
| 22 | Qwen3.5-2B | 9/41 | 5 × CS | 10/62 | 16% | 6,286 | 28s |
| 23 | Qwen3.5-0.8B | 0/41 | no patch | — | — | 1,203 | 4s |

† Opus was peer-reviewed against a smaller detectable baseline, so its ratio is flattering.
‡ `Gemma-4-31B` and `MiniMax-M3` were peer-reviewed by `Muse-Glimmer-30B` rather than the pinned
reviewer, and Muse has been observed to invert a ranking outright. Their Resolved figures are
not comparable with any other row; their Mech and Build results are unaffected.
¶ Its C# compiles; it set `TreatWarningsAsErrors` and tripped over a pre-existing package
◊ `glm-5.3` needs `think: false` and `num_predict: 128000`. At the defaults it returns nothing;
at 64,000 it returns a truncated patch that looks complete on every metric except `done_reason`.
§ `kimi-k3.1-pro` needs `num_predict: 64000`. At the default 40,000 it is cut off after 7 of 13
files and the fragment does not compile.

**Ten of twenty-three produce a tree that builds.** The line between rank 10 and rank 11 is the
only one in this benchmark that is not a matter of degree: above it the patch can be applied,
below it the repository does not compile. Note that `MiniMax-M2.7` at rank 11 clears more
markers than four models above it and still fails, and that `Qwen3-32B` at rank 15 has one of
the highest Resolved ratios in the table on a patch that does not build — which is exactly why
the peer-review column cannot be read on its own.

---

## Recommendations

### If a hosted call is acceptable

**`MiniMax-M3` is the best all-round result in the benchmark.** First as a reviewer with the
only clean 70 of 70, joint-first as a scorer with a perfect decoy result and the cleanest
Descriptions of any fast scorer, and 40 of 41 markers with a compiling patch. It is economical
about it too — 12,497 output tokens for the review against Opus's 23,932, in 1m 55s.

**`claude-opus-5` is the alternative, and it does one thing nothing else does.** It is the only
model that fixed defects by *adding* well-structured files — an `AuditLogService` and a
`LoginAttemptTracker` — rather than patching around them. Where a fix requires new code rather
than a corrected expression, that behaviour is worth the premium.

**`claude-sonnet-5` for review only.** It matches Opus at 69 for roughly 40% of the price in two
thirds of the time. Do not use it to patch: it emitted the most output tokens of any model and
still shipped a file missing a `using`.

**`glm-5.2` when latency matters.** It is the fastest reviewer (47s) and the fastest scorer
(25.6s) measured anywhere in the benchmark, and the fastest of the ten patchers that compile
(2m 16s).

**Handle `glm-5.3` with care.** It needs `think: false` and `num_predict: 128000`; at the
defaults it returns nothing, and at 64,000 it returns a truncated patch that looks complete on
every metric except `done_reason`.

**Prefer `kimi-k3` to `kimi-k3.1-pro`.** The newer model matches its predecessor as a reviewer
(69) and as a patcher (40 of 41, compiles, the same single miss), and is worse as a scorer
(97.0% against 100.0%). It costs 72% more output tokens for the review and 48% more for the
patch, and needs a raised `num_predict` for both — 100,000 and 64,000 — where `kimi-k3` runs at
the defaults. Nothing measured here justifies the upgrade.

### If you have a server (33GB+ of free RAM)

**`Qwen3.8-27B-imatrix:Q4_K_S`** is the best local model overall. It is one of only two models
in the whole field to clear all 41 markers with a tree that builds, and the only local model to
produce a clean sheet on every review integrity check — 100% precision across 38 checkable
findings, so what it reports can be acted on without checking it first.

**`Qwen3.6-27B:Q4_K_S`** if reproducibility matters more than precision. It produced a
byte-identical patch on every run days apart; Qwen3.8 did not, and one of its runs failed to
build. It finds more issues on paper (65 against 62) but at 88% precision rather than 100%.

Both need ~33GB at 64k context, or ~20GB at 16k.

### On a 32GB corporate laptop (~20GB actually free)

| Job | Model | Footprint | Result |
|---|---|---|---|
| **Reviewing** | `Qwen3.5-9B-imatrix:Q4_K_S` | 14.0 GB | 41/70 at **100% precision**, 42-second reviews |
| **Grading** | `Qwen3.5-9B-imatrix:Q4_K_S` | same model | 99.5%, 0 ungrounded, 0 misaligned, 41s |
| **Patching** | `Muse-Glimmer-30B-imatrix:Q4_K_S` | 19.6 GB | 39/41, the **only** sub-20GB patch that compiles |

One 5.4GB model does both the reviewing and the grading. If you can free 20GB,
`Muse-Glimmer-30B` roughly doubles the review findings (64) and is the only laptop-viable
patcher — but at 87% review precision, treat its output as leads rather than confirmed defects.

**Patching below 16GB does not work.** Neither `Qwen3.5-9B` nor `Qwen3.5-4B` produced a tree
that builds, and both left a quarter to a third of the defects in place.

### For the grading pipeline itself

**Keep `Qwen3-Coder-30B-imatrix:Q3_K_M`.** Free, local, the fastest local scorer at 30 seconds,
and it
reproduces reference Descriptions verbatim, which keeps its scorecards auditable. Nothing
measured justifies replacing it. Reach for `MiniMax-M3` or `glm-5.2` only when the grading
itself is what is being questioned.

### Never use

| Model | Why |
|---|---|
| `Qwen3.5-0.8B` | Fabricates source locations; produced no patch at all; unusable as a scorer |
| `Qwen3.5-2B` | 9 of 41 markers; rates 56 of 70 Partial on a review naming every defect |
| `MiniMax-M2.7`, `Codestral-22B`, `Devstral-2-123B` | **As scorers only** — all three credit nearly every issue on a review that names 16 |
| `Qwen3-32B` | Returns unparseable output as a scorer, with no diagnosis available |

The `MiniMax-M2.7` objection does **not** carry to `MiniMax-M3`, which is among the best
measured in every role.

---

## Things to be aware of

**Verify with something that is not a model.** This is the most transferable result here. A
compiler caught thirteen bad patches the peer reviewer had scored as successes. A decoy review
caught three scorers that pass every conventional test. Automated grounding checks corrected up
to 17 rows on a single sheet. Wherever a model grades a model, budget for an independent check.

**A patch that looks finished may be truncated.** A model cut off mid-response still returns
parseable output, so the harness applies a fragment and scores it as complete — and a defect in
a file the model never reached is recorded as unfixed. `claude-opus-5`, `glm-5.3` and
`kimi-k3.1-pro` all hit this, and `kimi-k3` came within 1,073 tokens of it. Only `done_reason` distinguishes the two
cases, and the right output ceiling is not knowable in advance.

**`think` unset does not mean off.** Several models spend their entire output budget on internal
reasoning and return nothing in the answer field unless `think: false` is passed explicitly.
`kimi-k3.1-pro` does the same at the default output cap — 184,944 characters of reasoning and
no review — and was run with a raised cap instead, which is why it is the slowest of the
leading reviewers.
Worse, `glm-5.3` wrote its reasoning into the *answer* with a closing `</think>` and no opening
tag, so the harness's stripper found nothing to remove and every downstream check graded its
working-out as review text. That check has not been applied retrospectively to the other
reviews, so it is not known whether any other sheet is affected.

**Scoring is not perfectly reproducible.** Temperature 0 is deterministic only within a single
backend session. Across a server restart the same input produced 67 on one run and 22 on the
next. Treat review differences under about five points, and patcher peer-review differences
under about seven, as ties.

**Neither is patching.** `Qwen3.8-27B` produced two materially different patches across
restarts — 36,091 bytes and 37,687 bytes — and the build verdict flipped from failing to passing
between them.

**The scorer over-credits on real prose.** It scores 100% on synthetic reviews and still prefers
crediting a near-miss to recording a clean Missed. Eleven of the twenty-three review sheets
contain zero Partial ratings, which is not credible on a 70-issue task; manual reading of
several found a further 6–9 over-credits each. Where a sheet shows zero Partials, treat its
score as an upper bound — including `MiniMax-M3`'s 70.

**Precision sample sizes vary from 11 to 40.** A 100% precision score is only as strong as the
number in brackets beside it. `Devstral-2-123B` and `Qwen3.5-2B` both show 100%, on 18 and 13
rows, because they claimed so little that there was little to check.

**Two patcher rows were peer-reviewed by a different model.** `Gemma-4-31B` (which cannot review
its own patch) and `MiniMax-M3` were reviewed by `Muse-Glimmer-30B` rather than the pinned
`Gemma-4-31B`. Muse has been observed to invert the ranking outright — it scored a 37/41 patch
25 points above a 41/41 one — so those two Resolved figures cannot be compared with any other
row. Their mechanical and build results are unaffected, because neither involves a reviewer.

**Markers prove shape, not correctness.** A mechanical marker confirms the defect's textual
signature is gone, not that the replacement works. `MiniMax-M2.7` cleared 39 of 41 while
replacing MD5 with a call to a type that does not exist.

**Timing is not like-for-like.** Ollama figures are the server's own generation time; hosted
figures are wall clock and include the network round trip. Hosted model sizes are also unknown,
so the "size predicts nothing" finding is drawn from the local models, where weights are
measurable.

**Single runs, one codebase, seeded defects.** Every model was measured once, on one C# web API
with deliberately planted bugs of known shape. The rankings are reliable in their broad bands —
leaders, strong mid-table, weak — but not to the individual place, and they should not be read
as a general ranking of model capability.
