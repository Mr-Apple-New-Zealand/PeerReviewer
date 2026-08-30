# AI Code Review Benchmark — Results Summary

Twenty-one models were asked to review the same deliberately-flawed C# application
(`SampleBankingApp/`) and their reviews were scored against 70 known, seeded defects
recorded in `ISSUES.md`. Every model received an identical prompt, an identical system
prompt, and identical sampler settings. Full per-model settings are in
[docs/CONFIG_SETTINGS.md](../docs/CONFIG_SETTINGS.md); the Ollama build definitions are in
[modelfiles/](../modelfiles/).

---

## Executive Summary

**Five models found essentially everything: `claude-sonnet-5`, `claude-opus-5`, `kimi-k3`,
`glm-5.2` and `glm-5.3`, all scoring 69 of 70.** They are separated by nothing meaningful — one
mis-credited row between them — and all five are hosted services rather than local models.

**The headline result is that Claude Sonnet 5 matched Claude Opus 5.** Both scored 69
adjusted; Sonnet used fewer output tokens (19,751 vs 23,932) and finished in 2m53s against
4m20s. At roughly 40% of Opus's price this is the clear value choice for hosted review, and
there is no evidence in this benchmark for paying the Opus premium on this task.

**The best local model is `Qwen3.8-27B` — but for a reason the raw score hides.** It scored
62, below `Qwen3.6-27B` at 65 and `Muse-Glimmer-30B` at 64. However it is one of only three
models in the entire fleet to achieve **100% precision on a full-size sample**: every one of
the 38 findings we could independently verify was genuinely supported by its review. The two
models above it scored higher partly by claiming issues their reviews never actually raised.
Read the two together and Qwen3.8-27B is the local model whose output you can trust without
checking it.

**For a 32GB corporate laptop, run `Qwen3.5-9B`.** It scored 41 — well short of the leaders —
but it is the only laptop-viable model with 100% precision, it needs about 14GB with a 64k
context, and it completes a full review in **42 seconds**. If more RAM is genuinely free,
`Muse-Glimmer-30B` roughly doubles the findings (64) for around 20GB, though at 87% precision
you should expect to verify its claims.

**Size does not predict quality.** `Devstral-2-123B` (75GB) scored 32 — less than
`Qwen3.5-4B` (3GB) at 55. `MiniMax-M2.7` (99GB) scored 57, below a 27B model. Three of the
four bottom-ranked models are among the largest tested. Architecture, training and output
discipline mattered far more than parameter count.

---

## How to read these scores

**Adjusted Found** is the headline number: issues the model was credited with finding, minus
those where an automated check proved the review never mentioned the subject. It runs 0–70.

**Precision** is the share of *independently checkable* findings that survived verification,
with the sample size in brackets. `100% (38)` is much stronger evidence than `100% (13)` —
the second is measured on a third as many rows. A model can score well on Adjusted Found
while having low precision, and that combination means the score is inflated.

The scorer is itself a model (`Qwen3-Coder-30B` at temperature 0) and it has a consistent
bias: it rarely records a clean "Missed", preferring to credit the nearest plausible sentence.
Eight automated checks were built to catch this, but they cannot detect a quotation that is
genuine yet attached to the wrong issue. **Where a sheet shows zero Partial ratings, treat
Adjusted Found as an upper bound.** Manual inspection of several such sheets found a further
6–9 points of over-crediting each; those cases are called out in the notes below.

---

## Full ranking

| # | Model | Adjusted | Raw F/P/M | Precision | Fabricated cites | Notes |
|---|---|---|---|---|---|---|
| 1= | **claude-opus-5** | **69** | 69/0/1 | **100% (39)** | 0 / 374 | Clean on every check |
| 1= | **claude-sonnet-5** | **69** | 70/0/0 | 98% (40) | 0 / 201 | Matches Opus at lower cost |
| 1= | **kimi-k3** | **69** | 70/0/0 | 98% (40) | 0 / 312 | Cloud-hosted |
| 1= | **glm-5.2** | **69** | 70/0/0 | 98% (40) | 0 / 154 | Cloud-hosted; fastest at 47s |
| 1= | **glm-5.3** | **69** | 70/0/0 | 98% (40) | 0 / 66 | Reasoning inlined in the review — see notes |
| 6 | Qwen3.5-122B | 66 | 69/0/1 | 92% (39) | 0 / 141 | Reading found ~6 further over-credits |
| 7 | Qwen3.6-27B | 65 | 70/0/0 | 88% (40) | 0 / 72 | Reading found ~9 further over-credits |
| 8 | Muse-Glimmer-30B | 64 | 69/0/1 | 87% (39) | 0 / 110 | Strong for its RAM footprint |
| 9 | **Qwen3.8-27B** | 62 | 62/0/8 | **100% (38)** | 0 / 220 | **Best local model — see notes** |
| 10= | gpt-oss-120B | 58 | 62/0/8 | 89% (35) | 1 / 55 | |
| 10= | Qwen3-Coder-Next | 58 | 63/0/7 | 86% (35) | 0 / 126 | Reading found ~7 further over-credits |
| 12 | MiniMax-M2.7 | 57 | 58/7/5 | 97% (32) | 0 / 176 | 99GB for a mid-table result |
| 13 | Qwen3.5-4B | 55 | 60/9/1 | 86% (35) | 0 / 285 | Remarkable for 3GB |
| 14 | Gemma-4-31B | 54 | 55/3/12 | 97% (33) | 0 / 87 | Honest scoring, few false claims |
| 15 | **Qwen3.5-9B** | 41 | 41/28/1 | **100% (24)** | 1 / 97 | **Best laptop model — see notes** |
| 16 | Qwen3-Coder-30B | 34 | 36/27/7 | 88% (17) | 0 / 1039 | Truncated; 90% of rows were test filler |
| 17 | Devstral-2-123B | 32 | 32/28/10 | 100% (18) | 0 / 63 | 75GB, shallowest review of any model |
| 18 | Qwen3-32B | 25 | 29/11/30 | 78% (18) | 0 / 44 | 2 rows scored against the wrong issue |
| 19= | Qwen3.5-2B | 22 | 22/36/12 | 100% (13) | 0 / 143 | Thin but honest |
| 19= | Codestral-22B | 22 | 23/46/1 | 93% (14) | 0 / 79 | Under-credited; ~26 on reading |
| 21 | Qwen3.5-0.8B | 19 | 21/10/39 | 82% (11) | **4 / 902** | Hit token limit at 14m41s |

*Fabricated cites = review references to source lines that do not exist in the file.*

---

## Model notes

### The five leaders

`claude-opus-5` is the only model with a perfect precision score on the largest sample: all
39 checkable findings verified, 374 source citations all valid, no misaligned rows, no
unsupported claims. `claude-sonnet-5`, `kimi-k3`, `glm-5.2` and `glm-5.3` each carry a single
mis-credited row and are otherwise equally clean. The difference between 69 and 69 is noise.

`glm-5.2` deserves a specific mention for speed — 47 seconds for a 69-point review, against
5m22s for `kimi-k3` at the same score.

### glm-5.3 — a leading review inside a working notebook

It scores with the leaders: 70/0/0 raw, 69 adjusted on one mis-credit (`N4`, `ToUpper`), 66
citations all in range, no grounding downgrades. It is also the only review in the field that
is mostly not a review.

`glm-5.3:cloud` writes its reasoning into the answer. With `think: false` it produced 139,263
characters, of which **102,642 — 74% — are working-out**: two complete draft passes over all
ten categories, a line-number verification list, and then `Alright. Writing final answer.`
before the report proper. The report is the last 35,501 characters.

The harness did not strip it. `strip_thinking` matches `<think>…</think>`, and this output
carries a closing `</think>` with **no opening tag**, so the regex found nothing to remove.
Everything downstream — the scorer, the evidence spot-check, the citation count — read all
three passes as the review.

Re-running the spot-check against the final report alone:

```
watchlist rows                     40
  target in the final report       38
  only in the discarded drafts      1   N3 (SmtpPort)
  absent from both                  1   N4 (already deducted)
```

So the contamination is real but small: one row, `N3`, is credited on a sentence the model
wrote and then dropped. **Read it as 68, not 69** — which still places it among the leaders.

Two operating notes. It needs `think: false` and a raised `num_predict`; at the benchmark
defaults it spends its whole budget reasoning and returns nothing, and an earlier attempt at
`num_predict: 40000` stopped mid-row in section 8 while still scoring 70/70 — the same
inlined reasoning hid the truncation from every check. This run finished at 34,275 tokens
against a 128,000 limit with `done_reason: stop`. And at 3m 12s it is four times slower than
`glm-5.2` for the same score, because three quarters of what it generates is discarded.

### Qwen3.8-27B — the local recommendation

62 findings, and **every checkable one verified**. No fabricated citations across 220 source
references, no unsupported Partial ratings, no misaligned rows, no self-hedged claims. It is
the only local model that produced a clean sheet on every integrity check.

By contrast `Qwen3.6-27B` and `Muse-Glimmer-30B` rank above it on Adjusted Found but at 88%
and 87% precision. Manual inspection of the Qwen3.6 sheet found around nine additional
over-credits beyond those the automated checks caught, putting its realistic figure near 56 —
below Qwen3.8. **If you need a local model whose findings can be acted on without
verification, Qwen3.8-27B is the choice.**

Note that Qwen3.6 and Qwen3.8 are architecturally identical here (27.3B parameters, 65
layers, 15.8GB); they differ in training and chat template.

### Qwen3.5-9B — the laptop recommendation

100% precision across 24 checkable findings, one stray citation in 97, a complete ten-section
review in **42 seconds using 3,875 output tokens**. It finds substantially less than the
leaders — 41 against 69 — but nothing it reports is invented.

It carries 28 Partial ratings of which 10 have no supporting text, so its true "Missed" count
is higher than the sheet states. That is a scorer artefact rather than a model failure.

**Important:** this model must be run with `think: false`. With reasoning enabled at
temperature 0 it consumed the entire 40,000-token budget on internal reasoning and returned
no review at all, twice in succession. The same applies to the 0.8B, 2B and 4B.

### Qwen3.5-4B — the surprise

55 adjusted from a 3GB model, ahead of `Gemma-4-31B`, `MiniMax-M2.7` (99GB) and
`Devstral-2-123B` (75GB). 285 source citations, none fabricated. Precision at 86% is middling
so its claims need checking, but as a demonstration that small models can do real work on
this task it is the standout result.

### Where large models disappointed

`Devstral-2-123B` (75GB) produced 7,588 characters and stopped naturally after 1,916 output
tokens — a shallower review than models a twentieth its size. Its precision is 100% but on
only 18 checkable rows, so the sample is weak. It reviewed at file granularity rather than
per-defect, which is a legitimate style but cannot distinguish between the seeded issues.

`Qwen3-Coder-30B` hit the token ceiling with 1,059 rows covering just 91 distinct source
locations — **91% redundancy**. 957 of those rows were unit-test suggestions, one per method
per imaginable scenario, which consumed the entire budget before the review could finish.

`Qwen3.5-0.8B` is not usable for this task. It ran for 14m41s, hit the token limit, and
**four of its citations point past the end of the file they name**. Its 19 points should not
be treated as a real score.

`Qwen3-32B` is the only model whose scorecard contains rows scored against the wrong
reference issue (`RL2`, `A6`), so even its low figure carries an asterisk.

---

## Running on a 32GB corporate laptop

A Windows 11 laptop running Chrome, Teams and Outlook typically has **20GB or less actually
free**. The figures below are model weights plus KV cache at the benchmark's 64k context.

| Model | Weights | KV @64k | Total @64k | Fits in 20GB? | Adjusted | Precision |
|---|---|---|---|---|---|---|
| **Qwen3.5-9B** | 5.4 GB | 8.6 GB | **14.0 GB** | **Yes, comfortably** | 41 | **100% (24)** |
| Qwen3.5-4B | 3.0 GB | 8.6 GB | 11.6 GB | Yes, comfortably | 55 | 86% (35) |
| Qwen3.5-2B | 1.2 GB | 3.2 GB | 4.4 GB | Yes, trivially | 22 | 100% (13) |
| **Muse-Glimmer-30B** | 16.1 GB | 3.5 GB | **19.6 GB** | **Yes, tight** | 64 | 87% (39) |
| Gemma-4-31B | 18.7 GB | small ¹ | ~20 GB | Marginal | 54 | 97% (33) |
| Qwen3-Coder-30B | 14.7 GB | 6.4 GB | 21.1 GB | Marginal | 34 | 88% (17) |
| Codestral-22B | 12.7 GB | 15.0 GB | 27.7 GB | No | 22 | 93% (14) |
| Qwen3.8-27B | 15.8 GB | 17.4 GB | 33.2 GB | No ² | 62 | 100% (38) |
| Qwen3.6-27B | 15.8 GB | 17.4 GB | 33.2 GB | No ² | 65 | 88% (40) |
| Qwen3-32B | 19.8 GB | 17.2 GB | 37.0 GB | No | 25 | 78% (18) |
| Qwen3.5-0.8B | 0.5 GB | 3.2 GB | 3.7 GB | Yes — but see notes | 19 | 82% (11) |

¹ Gemma-4 uses sliding-window attention (window 1024), which caps KV independently of context
length. Its KV is far smaller than 60 layers would suggest but is not derivable from the
published metadata.

² Reducing context to 16k brings both 27B models to roughly 20GB and they become marginally
viable. The benchmark prompt is only about 10k tokens, so 16k is sufficient for this workload
— but it leaves no headroom for larger codebases.

### Laptop recommendation

**Default choice: `Qwen3.5-9B`.** 14GB total, 42-second reviews, and 100% precision — it
finds less than the big models but does not invent findings, which matters far more when
nobody is checking its output. It leaves 6GB of headroom on a 20GB budget, so it will
co-exist with a normal corporate desktop load.

**If you can free 20GB: `Muse-Glimmer-30B`.** 64 adjusted is a 56% improvement in findings
over the 9B and puts it seventh overall, ahead of every other laptop-viable option. Its
unusually small KV cache (3.5GB, from 2 KV heads) is what makes a 16GB model fit where 27B
models do not. The trade-off is 87% precision — roughly one claim in eight will not hold up,
so treat its output as a list of leads rather than confirmed defects.

**If you want the 27B quality: reduce context to 16k.** `Qwen3.8-27B` at 16k needs about
20GB and delivers 62 findings at 100% precision. This is the best quality-per-gigabyte
available on a 32GB machine, but with no headroom for anything larger than the benchmark
codebase.

**Avoid on a laptop:** `Codestral-22B` and `Qwen3-32B` need more than 27GB while scoring in
the low twenties. `Qwen3.5-0.8B` fits in 4GB but fabricates source locations and should not
be used.

---

## Methodology

- **Task:** review `SampleBankingApp/` and report defects in ten fixed categories.
- **Ground truth:** 70 seeded issues in `ISSUES.md`, spanning SQL injection, broken access
  control, logic errors, resource leaks, null-safety, dead code, anti-patterns, configuration
  problems and missing tests.
- **Scoring:** each review is graded by `Qwen3-Coder-30B-imatrix:Q3_K_M` at temperature 0
  against `ISSUES.md`, producing Found / Partial / Missed per issue with a supporting quote.
- **Settings:** all models ran at temperature 0, 65,536 context, 40,000 max output tokens,
  with an identical system prompt. Per-model `think` settings and any deviations are recorded
  in [docs/CONFIG_SETTINGS.md](../docs/CONFIG_SETTINGS.md), and every scorecard reprints the
  exact values used for that run.
- **Model definitions:** Ollama build files for the local models are in
  [modelfiles/](../modelfiles/). Model identity was verified against `general.basename` in
  the GGUF metadata rather than trusting tag names.

### Automated integrity checks

Each scorecard is validated by eight checks before its score is reported:

| Check | Catches |
|---|---|
| Duplicate ID removal | The same issue scored twice |
| Unknown ID rejection | Rows invented by the scorer that are not in `ISSUES.md` |
| Row alignment | Rows scored against a different issue after a renumbering |
| Note grounding | Supporting quotes that do not appear in the review |
| Self-declared absence | Rows credited whose own note says the review never mentioned it |
| Evidence spot-check | 40 rows whose subject can be verified by name **or by source location** |
| Unsupported Partials | Partial credit for issues with no supporting text |
| Citation validity | Review references to source lines that do not exist |

---

## Known limitations

**The scorer is the weakest component.** It is a model, not a parser, and it consistently
prefers crediting a near-miss over recording a clean Missed. Ten of the twenty-one sheets contain
zero Partial ratings, which is not credible on a 70-issue task. The automated checks recover
much of this — they made 15 to 17 corrections on some sheets — but they verify that evidence
*exists*, not that it is *relevant*. Manual reading of several sheets found a further 6–9
over-credits each.

**Scoring is not perfectly reproducible.** Temperature 0 makes a model deterministic only
within a single backend session. Across a server restart the same input can produce different
output; one model scored 67 on one run and 22 on the next from an identical review. Treat
differences of fewer than about five points as ties.

**Precision samples vary in size.** The spot-check can verify between 11 and 40 findings
depending on which issues a model claimed. A 100% score on 13 rows is far weaker evidence
than the same score on 40, and the sample size is shown throughout for that reason.

**Single runs.** Each model was measured once. Given the variance above, the ranking is
reliable in its broad bands — leaders, strong mid-table, weak — but not to the individual
place.

**Inlined reasoning is graded as review text.** The harness strips `<think>…</think>` blocks,
which requires both tags. `glm-5.3` emitted 102,642 characters of drafting with a closing tag
and no opening one, and every downstream check read it as the review. Where a model reasons in
the open, the score covers what it considered as well as what it concluded — see the `glm-5.3`
note. The reviews were not otherwise inspected for this, so it is not known whether any other
sheet is affected.

**One benchmark, one codebase.** These results describe performance on a single C# web API
with deliberately seeded defects. They should not be read as a general ranking of model
capability.
