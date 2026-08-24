# Scorer Benchmark Summary

> **Run:** #15 &nbsp;·&nbsp; **Generated:** 2026-08-24 02:34

> Scorer prompt SHA `2b79baa02b94` &nbsp;·&nbsp; num_ctx 65,536 &nbsp;·&nbsp; num_predict 40,000 &nbsp;·&nbsp; temperature 0.3

## Methodology

| Review | Purpose | Expected output |
|--------|---------|-----------------|
| **Perfect** | Explicitly names every planted bug by file, symbol, and behaviour | All 70 Found |
| **Null** | Generic positive review — nothing specific mentioned | All 70 Missed |

- **TPR** (sensitivity): Found / 70 on the perfect review
- **TNR** (specificity): Missed / 70 on the null review
- **Score**: harmonic mean of TPR and TNR — a model that aces one but fails the other is penalised

The current production scorer is `Qwen3-Coder-30B-imatrix:Q3_K_M`.

## Ranked Results

`raw` is the scorer's unmodified output. `processed` applies the same
post-processing production does — duplicate removal, downgrading Notes that
cannot be matched to the review, and mis-credit detection. Production ships
`processed`, so that is the column to rank on.

| # | Model | TPR raw | TPR proc | TNR raw | TNR proc | Score proc | Perfect time | Null time | Truncated? |
|---|-------|--------:|---------:|--------:|---------:|-----------:|--------------|-----------|------------|
| 1 | gpt-oss:120b | 100.0% | **100.0%** | 100.0% | **100.0%** | **100.0%** | 1m 35s | 26.4s | No |

## Detail — Perfect Review (sensitivity)

A good scorer should return close to 70 Found.
Missed = issues the scorer failed to recognise despite being clearly stated.

| Model | Found | Partial | Missed | Total | Time | Speed |
|-------|-------|---------|--------|-------|------|-------|
| gpt-oss:120b | 70 | 0 | 0 | 70 | 1m 35s | 106.0 t/s |

## Detail — Null Review (specificity)

A good scorer should return 0 Found and 0 Partial.
Found or Partial = false positives (the scorer invented matches that aren't there).

| Model | Found | Partial | Missed | Total | Time | Speed |
|-------|-------|---------|--------|-------|------|-------|
| gpt-oss:120b | 0 | 0 | 70 | 70 | 26.4s | 110.1 t/s |
