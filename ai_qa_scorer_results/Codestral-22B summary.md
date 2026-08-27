# Scorer Benchmark Summary

> **Run:** #27 &nbsp;·&nbsp; **Generated:** 2026-08-27 09:36

> Scorer prompt SHA `2b79baa02b94` &nbsp;·&nbsp; num_ctx 65,536 &nbsp;·&nbsp; num_predict 40,000 &nbsp;·&nbsp; temperature 0.0

## Methodology

| Review | Purpose | Expected output |
|--------|---------|-----------------|
| **Perfect** | Explicitly names every planted bug by file, symbol, and behaviour | All 70 Found |
| **Null** | Generic positive review — nothing specific mentioned | All 70 Missed |
| **Decoy** | Genuine findings for the 16 Critical and Logic issues only | 16 Found, 52 Missed |

2 further issues (CF1, CF3) are excluded from the silent set: ISSUES.md records them twice under different categories, so the decoy describes them via their twin and crediting them is correct.

- **TPR** (sensitivity): Found / 70 on the perfect review
- **TNR** (specificity): Missed / 70 on the null review
- **Decoy specificity**: of the 52 issues the decoy review says nothing about, the share the scorer correctly declined to credit
- **Score**: harmonic mean of all three — a scorer that aces one test but fails another is penalised, and any outright zero scores zero

The decoy test is the one that matters most in practice. `perfect` and `null` bracket the
extremes, and a scorer passes both by being uniformly generous or uniformly strict. The decoy
supplies real evidence for 16 issues and none for the other 52, so every credit
it awards beyond those 16 is produced by association with a nearby finding — the failure
that inflated ten of the twenty review scorecards in the model benchmark.

Note the limit of these tests: two scorers known to differ on real reviews both scored
100/100/100 here. They screen out a broken scorer; they do not rank good ones.

The production scorer is `Qwen3-Coder-30B-imatrix:Q3_K_M`. Qwen3.8-27B-imatrix:Q4_K_S
was benchmarked as a replacement and matched it exactly (100/100/100), but is ~6x slower
(201s against 30s on the perfect review) and summarises the Description column rather than
reproducing it, so the incumbent was kept.

## Ranked Results

`raw` is the scorer's unmodified output. `processed` applies the same
post-processing production does — duplicate removal, downgrading Notes that
cannot be matched to the review, and mis-credit detection. Production ships
`processed`, so that is the column to rank on.

| # | Model | TPR | TNR | Decoy spec. | Score | False credits | Perfect time | Truncated? |
|---|-------|----:|----:|------------:|------:|--------------:|--------------|------------|
| 1 | Codestral-22B-imatrix:Q4_K_S | 98.6% | 100.0% | 98.1% | **98.9%** | 1 / 52 | 1m 43s | No |

## Detail — Perfect Review (sensitivity)

A good scorer should return close to 70 Found.
Missed = issues the scorer failed to recognise despite being clearly stated.

| Model | Found | Partial | Missed | Total | Time | Speed |
|-------|-------|---------|--------|-------|------|-------|
| Codestral-22B-imatrix:Q4_K_S | 69 | 1 | 0 | 70 | 1m 43s | 42.9 t/s |

## Detail — Null Review (specificity)

A good scorer should return 0 Found and 0 Partial.
Found or Partial = false positives (the scorer invented matches that aren't there).

| Model | Found | Partial | Missed | Total | Time | Speed |
|-------|-------|---------|--------|-------|------|-------|
| Codestral-22B-imatrix:Q4_K_S | 0 | 0 | 70 | 70 | 45.0s | 46.0 t/s |

## Detail — Decoy Review (discrimination)

The decoy names 16 issues explicitly and is silent on the other 52.
A calibrated scorer returns 16 Found. Anything it credits among the other
52 is a false credit — evidence borrowed from an unrelated finding.

| Model | Genuine found | False credits | Falsely credited IDs |
|-------|---------------|---------------|----------------------|
| Codestral-22B-imatrix:Q4_K_S | 16 / 16 | **1 / 52** | CF9 |

## Run Configuration — Codestral-22B-imatrix:Q4_K_S

Values as actually sent for this run. Blank sampler entries mean the
request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Scorer model | `Codestral-22B-imatrix:Q4_K_S` |
| Ollama `think` | (unset) |
| Reasoning strength (system prompt) | (model default) |
| System prompt | `You are an expert computer programmer with an eye for detail, who loves to provide high quality answers.` |
| Temperature | `0.0` |
| top_p | (model default) |
| top_k | (model default) |
| Effort (Anthropic only) | (n/a) |
| num_ctx | `65536` |
| num_predict | `40000` |
| Scorer prompt SHA-256 | `2b79baa02b94` |
| ISSUES.md SHA-256 | `4b57cc34a7bb` |
| Reference issues | `70` (69 rows + UT) |
| Decoy coverage | `16` issues named, `52` silent |
| Branch / commit | `main @ 877206f` |

| Review | Output tokens | Duration | Stop reason | Thinking chars |
|---|---|---|---|---|
| perfect | 4125 | 1m 43s | stop | 0 |
| null | 2010 | 45.0s | stop | 0 |
| decoy | 4673 | 1m 46s | stop | 0 |
