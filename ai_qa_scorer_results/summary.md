# Scorer Benchmark Summary

> **Run:** #16 &nbsp;·&nbsp; **Generated:** 2026-08-27 07:05

> Scorer prompt SHA `2b79baa02b94` &nbsp;·&nbsp; num_ctx 65,536 &nbsp;·&nbsp; num_predict 40,000 &nbsp;·&nbsp; temperature 0.0

## Methodology

| Review | Purpose | Expected output |
|--------|---------|-----------------|
| **Perfect** | Explicitly names every planted bug by file, symbol, and behaviour | All 70 Found |
| **Null** | Generic positive review — nothing specific mentioned | All 70 Missed |
| **Decoy** | Genuine findings for the 16 Critical and Logic issues only | 16 Found, 54 Missed |

- **TPR** (sensitivity): Found / 70 on the perfect review
- **TNR** (specificity): Missed / 70 on the null review
- **Decoy specificity**: of the 54 issues the decoy review says nothing about, the share the scorer correctly declined to credit
- **Score**: harmonic mean of all three — a scorer that aces one test but fails another is penalised, and any outright zero scores zero

The decoy test is the one that matters most in practice. `perfect` and `null` bracket the
extremes, and a scorer passes both by being uniformly generous or uniformly strict. The decoy
supplies real evidence for 16 issues and none for the rest, so every credit it awards beyond
those 16 is produced by association with a nearby finding — the failure that inflated ten of
the twenty review scorecards in the model benchmark.

The current production scorer is `Qwen3-Coder-30B-imatrix:Q3_K_M`.

## Ranked Results

`raw` is the scorer's unmodified output. `processed` applies the same
post-processing production does — duplicate removal, downgrading Notes that
cannot be matched to the review, and mis-credit detection. Production ships
`processed`, so that is the column to rank on.

| # | Model | TPR | TNR | Decoy spec. | Score | False credits | Perfect time | Truncated? |
|---|-------|----:|----:|------------:|------:|--------------:|--------------|------------|
| 1 | Qwen3.8-27B-imatrix:Q4_K_S | 100.0% | 100.0% | — | **0.0%** | — | 3m 38s | No |

## Detail — Perfect Review (sensitivity)

A good scorer should return close to 70 Found.
Missed = issues the scorer failed to recognise despite being clearly stated.

| Model | Found | Partial | Missed | Total | Time | Speed |
|-------|-------|---------|--------|-------|------|-------|
| Qwen3.8-27B-imatrix:Q4_K_S | 70 | 0 | 0 | 70 | 3m 38s | 38.9 t/s |

## Detail — Null Review (specificity)

A good scorer should return 0 Found and 0 Partial.
Found or Partial = false positives (the scorer invented matches that aren't there).

| Model | Found | Partial | Missed | Total | Time | Speed |
|-------|-------|---------|--------|-------|------|-------|
| Qwen3.8-27B-imatrix:Q4_K_S | 0 | 0 | 70 | 70 | 1m 9s | 39.8 t/s |

## Detail — Decoy Review (discrimination)

The decoy names 16 issues explicitly and is silent on the other 54.
A calibrated scorer returns 16 Found. Anything it credits among the other
54 is a false credit — evidence borrowed from an unrelated finding.

| Model | Genuine found | False credits | Falsely credited IDs |
|-------|---------------|---------------|----------------------|
| Qwen3.8-27B-imatrix:Q4_K_S | — | ERROR | — |
