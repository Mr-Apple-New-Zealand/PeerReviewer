# Scorer Benchmark — Results Summary

Twenty-one models were tested as *scorers* — the component that grades a code review against
`ISSUES.md` — rather than as reviewers. Each was given three synthetic reviews with known
correct answers and asked to produce a scorecard. Every model received an identical prompt,
system prompt and sampler settings; the harness records both digests and the decoy definition
in each run’s `results.json`, and all twenty-one share the same values.

The companion document for the review benchmark is
[../ai_code_review_results/SUMMARY.md](../ai_code_review_results/SUMMARY.md).

---

## Executive Summary

**Twelve of the twenty-one scored a perfect 100.0%, so the headline Score does not rank them.**
The number that separates a good scorer from a bad one is **Ungrounded** — rows the scorer
rated Found or Partial with nothing in the review to support them. That column runs from 0 to
84 across a field whose Scores run from 100.0% to 98.9%.

**Keep `Qwen3-Coder-30B-imatrix:Q3_K_M`, the incumbent.** It scores 100.0% with a single
ungrounded row, reproduces the reference descriptions verbatim, and is the fastest local
model at **30 seconds**. Nothing measured beats it on the combination, and no defect was
found that would justify a change.

**Three models credit almost everything and must not be used.** `MiniMax-M2.7` rated **70 of
70** issues Found on a review that names sixteen; `Codestral-22B` rated 68; `Devstral-2-123B`
rated 63. The grounding check stripped 52, 49 and 58 unsupported rows respectively, so all
three still *score* 98.9–100%. Without that check they would silently inflate every review
they graded.

**Three more fail outright at 0.0%,** by two different mechanisms. `Qwen3.5-0.8B` and
`Qwen3.5-2B` cannot produce a usable scorecard — the 0.8B returned unparseable output on two
of three reviews and credited 69 of 70 on a review saying nothing; the 2B rated 56 of 70 as
*Partial* on a review naming every defect, citing text that did not exist. `Qwen3-32B` is
different again: flawless on two reviews, then returned output on the third that contained no
scorecard at all.

**For a 32GB laptop, `Qwen3.5-9B` grades at 99.5% in 41 seconds using 5.4GB.** Its only miss
is `UT`, the one reference issue written as prose rather than a table row. Combined with its
review result, the same 5.4GB model can both write and grade a review on a corporate laptop.

**Cost is the only argument against the hosted models.** `glm-5.2` is the fastest scorer
measured at **25.6 seconds** with zero ungrounded rows, and `claude-sonnet-5`, `claude-opus-5`
and `kimi-k3` are all clean. They are per-call charges against a local model that is free and
comparable.

---

## How to read these scores

Each scorer was given three reviews with known answers:

| Review | Contains | A correct scorer returns |
|---|---|---|
| **Perfect** | every one of the 70 defects, named explicitly | 70 Found |
| **Null** | a generic positive review naming nothing | 70 Missed |
| **Decoy** | genuine findings for 16 Critical/Logic issues, silent on the rest | 16 Found, 52 Missed |

**Score** is the harmonic mean of sensitivity (perfect), specificity (null) and the decoy term
— itself the harmonic mean of recall over the 16 named issues and specificity over the 52
silent ones. Any outright zero scores zero.

**Ungrounded** counts rows the scorer credited with a quotation the review does not contain.
These are removed before scoring, so a high count does **not** lower the Score. It is
nonetheless the most informative column in the table: a scorer needing 52 corrections is
wholly dependent on the grounding check holding, where one needing none is not.

**Misaligned** counts rows whose Description no longer matches `ISSUES.md`. In every case
inspected this was benign — the scorer summarising rather than copying — but it makes a
scorecard harder to audit by eye, since the Description column is how a reader knows which
issue a row is about.

`CF1` and `CF3` are excluded from the decoy's silent set: `ISSUES.md` records them twice under
different categories, so the decoy describes them via `C8` and `C9` and crediting them is
correct.

---

## Full ranking

| # | Scorer | Score | Ungrounded | Decoy credited | Misaligned | Perfect time | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | **glm-5.2** | 100.0% | **0** | 16/70 | 16 | **25.6s** | Fastest measured |
| 2 | **Qwen3-Coder-30B** | 100.0% | 1 | 19/70 | **0** | 30.0s | **Incumbent — keep** |
| 3 | Claude-Sonnet-5 | 100.0% | **0** | 16/70 | 17 | 43.9s | Clean, hosted |
| 4 | Claude-Opus-5 | 100.0% | **0** | 18/70 | 19 | 63.7s | Clean, hosted |
| 5 | gpt-oss-120B | 100.0% | **0** | 18/70 | 36 | 74.6s | Clean |
| 6 | **glm-5.3** | 100.0% | **0** | 18/70 | 8 | 81.7s ◊ | Duplicated every row — see notes |
| 7 | Kimi-k3 | 100.0% | **0** | 18/70 | 11 | 145.2s | Clean, hosted |
| 8 | Qwen3.8-27B | 100.0% | **0** | 18/70 | 47 | 201.0s | Clean but slow |
| 9 | Gemma-4-31B | 100.0% | **0** | 16/70 | 52 | 229.9s | Clean but slow |
| 10 | **Muse-Glimmer-30B** | 100.0% | **0** | 16/70 | **0** | 266.1s | Flawless, slow |
| 11 | **Qwen3.6-27B** | 100.0% | **0** | 16/70 | **0** | 268.3s | Flawless, slow |
| 12 | MiniMax-M2.7 | 100.0% | **52** | **70/70** | 0 | 554.1s | **Credits everything** |
| 13 | **Qwen3.5-9B** | 99.5% | **0** | 18/70 | **0** | 41.1s | **Best laptop scorer** |
| 14 | Codestral-22B | 99.2% | **49** | **68/70** | 2 | 102.9s | **Credits everything** |
| 15 | Qwen3-Coder-Next | 98.5% | 3 | 21/70 | **0** | 57.3s | Under-sensitive |
| 16 | Qwen3.5-122B | 98.0% | 4 | 18/70 | 30 | 66.2s | Fabricates on perfect |
| 17 | Qwen3.5-4B | 97.2% | 1 | 16/70 | 138 | 34.3s | Heavy paraphrase |
| 18 | Devstral-2-123B | 92.0% | **58** | **63/70** | 0 | 679.1s | **Credits everything** |
| 19= | Qwen3.5-0.8B | **0.0%** | 69 | 0/70 | 127 | 12.9s | **Unusable** |
| 19= | Qwen3.5-2B | **0.0%** | 84 | 7/70 | 1 | 17.8s | **Unusable** |
| 19= | Qwen3-32B | **0.0%** | 0 | 0/70 | 0 | 355.6s | **Decoy unparseable** |

*Decoy credited = issues rated Found or Partial on a review that names 16. Times are Ollama
generation time; `claude-*` figures are wall clock and include the network round trip.*
◊ *Emitted 140 rows on two of the three reviews — every issue twice. The figures shown are
post-processing, after duplicate removal; see* The scorer that graded everything twice.*

---

## Notes

### The incumbent

`Qwen3-Coder-30B-imatrix:Q3_K_M` scores 100.0% on all three tests with one ungrounded row
across the set, zero misalignment, and the fastest local time at 30 seconds. It reproduces
the reference Description column verbatim, which keeps its scorecards auditable.

It was benchmarked against `Qwen3.8-27B`, which matched it exactly but took 201 seconds and
summarises descriptions instead of copying them. No candidate offered a measurable
improvement, so the incumbent stays.

The scorer benchmark also retroactively supports the review results: the instrument that
graded all twenty-one reviews grades correctly here.

### The three that credit everything

| Scorer | Decoy: credited of 70 | Ungrounded |
|---|---|---|
| MiniMax-M2.7 | **70** | 52 |
| Codestral-22B | 68 | 49 |
| Devstral-2-123B | 63 | 58 |

`MiniMax-M2.7` is the clearest case. It handled the perfect and null reviews flawlessly —
correctly declining everything on a review with no evidence, so it is not simply generous.
Given sixteen real findings it credited all seventy. That is association, not recognition,
and it is exactly the failure the decoy test was built to expose. On the two original tests it
would have been indistinguishable from Claude Opus.

All three still score 98.9–100% because grounding removes the unsupported rows before scoring.
Read the Ungrounded column, not the Score.

### The scorer that graded everything twice

`glm-5.3` grades correctly and is the second-fastest hosted scorer at 81.7 seconds, with zero
ungrounded rows and only 8 misaligned descriptions — cleaner on both counts than
`Qwen3.8-27B` (47 misaligned) or `Gemma-4-31B` (52).

It also emitted **140 rows instead of 70** on the null and decoy reviews, listing every issue
twice. It is the only scorer in the field to produce more rows than the reference; every other
deviation was a model failing to produce rows at all. The `perfect` review came back at 70, so
the duplication is intermittent within a single run.

The duplicates agreed with each other, so `drop_duplicate_ids` halved the sheet cleanly —
36F/104M became 18F/52M, and the graded result is correct. But had the two copies of a row
disagreed on Status, the first would have won arbitrarily. A scorer whose correctness depends
on the harness repairing its output belongs in the same category as the models that credit
everything and rely on the grounding check to clean up after them.

It also needs `think: false` and a raised `num_predict`; with reasoning on by default it spends
its whole budget deliberating and returns nothing. See the patcher summary for the full
sequence.

### The three that fail

`Qwen3.5-0.8B` and `Qwen3.5-2B` fail in opposite directions. The 0.8B produced unparseable
output on the perfect and decoy reviews and credited 69 of 70 on the null review, with every
ID in its misaligned list — it is not reproducing `ISSUES.md` at all. The 2B parses correctly
but rated **56 of 70 as Partial** on a review naming every defect, and 64 of its notes cited
text the review does not contain, leaving 4 Found after grounding.

`Qwen3-32B` is a different failure and worth a second look. Its perfect and null reviews were
both flawless — 70/70 and 0/70 — and then the decoy returned 4,894 tokens containing no
parseable scorecard. Its scorecards were not archived, so what defeated the parser is not
recoverable. A re-run keeping the full output directory would settle it.

### Where scorers differ without failing

`Qwen3-Coder-Next` is the least sensitive working scorer, missing 2 and partialling 1 on a
review that names everything. `Qwen3.5-122B` is one of only three models to fabricate evidence
on the *perfect* review — four rows cited text that is not there. `Qwen3.5-4B` rewrote 138
Description cells, by far the most, and missed 2 of the 16 decoy issues.

None of these is disqualifying, but all three are measurably behind the leaders.

---

## Recommendation

**Production: keep `Qwen3-Coder-30B-imatrix:Q3_K_M`.** Fastest local scorer, effectively
clean, verbatim descriptions, and already in place.

**Laptop or low-RAM: `Qwen3.5-9B-imatrix:Q4_K_S`.** 99.5% at 41 seconds in 5.4GB, with zero
ungrounded and zero misaligned rows — one of only four scorers with a completely clean sheet.
Its single miss is `UT`, the one reference issue written as prose. Paired with its review
performance, one 5.4GB model does both jobs on a 32GB machine.

**If a hosted call is acceptable: `glm-5.2`.** Fastest of everything measured at 25.6 seconds
with zero ungrounded rows. Its successor `glm-5.3` grades just as cleanly and keeps far more of
the reference Descriptions intact (8 misaligned against glm-5.2's 16), but takes three times as
long, duplicates rows, and will not run at this benchmark's defaults.

**Never use as a scorer:** `MiniMax-M2.7`, `Codestral-22B`, `Devstral-2-123B` — all credit
almost everything. `Qwen3.5-0.8B`, `Qwen3.5-2B`, `Qwen3-32B` — all fail outright.

---

## Methodology

- **Task:** grade a review against `ISSUES.md`, producing Found / Partial / Missed per issue
  with a supporting quotation.
- **Reviews:** three synthetic ones generated from `ISSUES.md` itself, in the markdown table
  format every real model review uses, so the scoring pipeline behaves as it does in
  production.
- **Post-processing:** each scorecard passes through the same eight checks production applies
  — duplicate-ID removal, invented-ID rejection, note grounding, self-declared absence, row
  alignment, the evidence spot-check, unsupported Partials and citation validity. The reported
  figures are post-processing, because that is what production ships.
- **Settings:** temperature 0, 65,536 context, 40,000 output tokens, identical system prompt.
  Models that spend their budget on internal reasoning were run with `think: false`; the
  effective value is recorded in every run.
- **Comparability:** every run records the harness commit, both prompt digests, the
  `ISSUES.md` digest and the decoy definition. All twenty-one share the same inputs.
- **Per-model settings:** [../docs/CONFIG_SETTINGS.md](../docs/CONFIG_SETTINGS.md).

---

## Known limitations

**The Score alone is not a ranking.** Eleven scorers tie at 100.0%, including one that
credited every issue on the decoy. The Score answers "is this scorer broken?"; the Ungrounded
column answers "is it any good?".

**Synthetic reviews are not real ones.** The incumbent scores 100% here, yet on real reviews
it produced ten sheets with zero Partial ratings that manual reading knocked 6–9 points off
each. Generated text is unambiguous in a way real prose is not, so these tests cannot detect
the over-crediting that happens at the margins of a genuine review.

**Single runs.** Each scorer was measured once. Temperature 0 is deterministic only within a
backend session — across a restart the same input can produce different output.

**`Qwen3-32B` is unexplained.** Two flawless reviews and one that produced no scorecard, with
no archived output to diagnose it.

**Timing is not like-for-like.** Ollama figures are the server's own generation time; hosted
models are wall clock and include the network round trip.
