# Jack-27B vs Qwen3.8-27B — Scorer Comparison

`hf.co/JackAgentLead/Jack-3.8-27B-Coder-16GB-VRAM:latest` against
`Qwen3.8-27B-imatrix:Q4_K_S` on the scorer benchmark: three synthetic reviews with known
answers, same prompt digest (`2b79baa02b94`), same `ISSUES.md` (`4b57cc34a7bb`), both at
temperature 0 with `think: medium`.

The full scorer field is in [../../ai_qa_scorer_results/SUMMARY.md](../../ai_qa_scorer_results/SUMMARY.md).
The patcher comparison for the same model is in [PATCHER_SUMMARY.md](PATCHER_SUMMARY.md).

---

## Verdict

**Jack beats Qwen3.8-27B as a scorer, on both of the things that separated Qwen3.8-27B from
the incumbent.** It is 17% faster and produces 4 misaligned rows where Qwen3.8-27B produces 47.

**It still does not displace the incumbent.** `Qwen3-Coder-30B-imatrix:Q3_K_M` grades the same
reviews in 30 seconds against Jack's 2m 48s — 5.6× faster — with the same perfect scores.

---

## Head to head

Every scoring metric is identical. Both are flawless.

| | Jack-27B | Qwen3.8-27B |
|---|---|---|
| Score | **100.0%** | **100.0%** |
| Perfect review (TPR) | 70/70 | 70/70 |
| Null review (TNR) | 0 credited of 70 | 0 credited of 70 |
| Decoy recall | **16/16** | **16/16** |
| Decoy false credits | **0 / 52** | **0 / 52** |
| Ungrounded notes | **0** | **0** |
| **Misaligned rows** | **4** | **47** |
| Perfect-review time | **2m 48s** | 3m 21s |
| Throughput | **47.5–48.6 t/s** | 38.9–39.8 t/s |

Both handled the decoy perfectly — 16 genuine findings recognised, nothing credited among the
52 the review is silent about. That is the test most scorers fail: three models in the field
credited 63–70 of 70 on it.

---

## The one real difference

**Misalignment: 4 against 47.** A misaligned row is one whose Description no longer matches
`ISSUES.md` — the scorer summarised the issue instead of reproducing it. It does not change
the grade, but the Description column is how a reader knows which issue a row refers to, so a
scorecard full of paraphrase is markedly harder to audit by eye.

```
                perfect   null   decoy   total
Jack-27B              0      4       0       4
Qwen3.8-27B          16     11      20      47
```

This matters because it is precisely why Qwen3.8-27B was not adopted. From the scorer
benchmark: *"benchmarked as a replacement and matched it exactly (100/100/100), but is ~6x
slower and summarises the Description column rather than reproducing it, so the incumbent was
kept."* Jack removes that objection almost entirely.

Jack also self-declared `CF3` as absent on the decoy, which the harness correctly downgraded
— 16F/2P became 16F/1P after processing. Qwen3.8-27B needed no such correction. A minor point
against Jack, and the only one.

---

## Against the incumbent

The decision-relevant comparison is not Qwen3.8-27B but the scorer actually in production.

| | Jack-27B | Qwen3-Coder-30B *(incumbent)* |
|---|---|---|
| Score | 100.0% | 100.0% |
| Decoy credited (of 70) | **17** | 19 |
| Ungrounded | **0** | 1 |
| Misaligned | 4 | **0** |
| Perfect-review time | 2m 48s | **30s** |
| Throughput | 47.5 t/s | **159.9 t/s** |

Jack is marginally *better* on grading — one fewer ungrounded note, two fewer decoy credits —
and marginally worse on alignment. Those differences are within the noise of a single run.

The gap that is not within noise is speed: **30 seconds against 2m 48s**. The scorer runs
twice per patch evaluation, so across a twenty-model sweep that is roughly 20 minutes against
100. Nothing in Jack's grading justifies that.

---

## Recommendation

**Keep `Qwen3-Coder-30B-imatrix:Q3_K_M` as the production scorer.** Jack does not grade better
in any way that survives a single run's noise, and costs 5.6× the time.

**If you ever need a second opinion on a contested scorecard, use Jack rather than
Qwen3.8-27B.** Same grades, 17% faster, and a scorecard you can actually read — 4 paraphrased
rows instead of 47.

**Caveat: one run each.** Both models were measured once, and the scorer benchmark uses
generated reviews that are unambiguous in a way real ones are not. The incumbent scores 100%
here too, yet on real reviews it produced ten sheets with zero Partial ratings that manual
reading knocked 6–9 points off. A perfect score on this benchmark means "not broken", not
"good".
