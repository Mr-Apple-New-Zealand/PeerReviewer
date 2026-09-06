# Model Benchmark — Overall Summary

Twenty-two models were measured in three distinct roles against the same deliberately-flawed
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
builds. `Qwen3.8-27B` writes the best patch of any model and ranks tenth as a reviewer. Pick a
model per role, not a model.

**Grading is the easy job. Fixing is the hard one.** Thirteen of twenty-two score a perfect
100.0% as scorers. Nine of twenty-two produce a patch that compiles. The floor differs too:
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
not run at this benchmark's defaults at all.

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

**Reading the columns.** Precision is the share of independently checkable findings that
survived verification, with sample size in brackets — `100% (13)` is much weaker evidence than
`100% (40)`. Ungrounded counts rows a scorer credited with a quotation the review does not
contain; it does not lower the Score, and it is the column that separates a scorer which grades
from one that guesses. The patcher's peer-review Resolved column is deliberately omitted here
because it is not comparable across rows — see *Things to be aware of*.

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
(25.6s) measured anywhere in the benchmark, and the fastest of the nine patchers that compile
(2m 16s).

**Handle `glm-5.3` with care.** It needs `think: false` and `num_predict: 128000`; at the
defaults it returns nothing, and at 64,000 it returns a truncated patch that looks complete on
every metric except `done_reason`.

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
a file the model never reached is recorded as unfixed. `claude-opus-5` and `glm-5.3` both hit
this, and `kimi-k3` came within 1,073 tokens of it. Only `done_reason` distinguishes the two
cases, and the right output ceiling is not knowable in advance.

**`think` unset does not mean off.** Several models spend their entire output budget on internal
reasoning and return nothing in the answer field unless `think: false` is passed explicitly.
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
crediting a near-miss to recording a clean Missed. Eleven of the twenty-two review sheets
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
