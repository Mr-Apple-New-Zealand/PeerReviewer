# Scorer Benchmark Summary

> **Run:** #46 &nbsp;·&nbsp; **Generated:** 2026-08-27 21:53

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
- **Decoy (recall/spec)**: recall is the share of the 16 named issues the scorer found; specificity is the share of the 52 silent ones it correctly declined. The Score combines them, because specificity alone rewards a scorer that credits nothing at all
- **Score**: harmonic mean of all three — a scorer that aces one test but fails another is penalised, and any outright zero scores zero
- **Ungrounded**: Notes across all three reviews that the review could not support. These are removed before scoring, so a high count does not lower the Score — but it is the number that separates a scorer which grades correctly from one that credits everything and relies on the harness to clean up after it

The decoy test is the one that matters most in practice. `perfect` and `null` bracket the
extremes, and a scorer passes both by being uniformly generous or uniformly strict. The decoy
supplies real evidence for 16 issues and none for the other 52, so every credit
it awards beyond those 16 is produced by association with a nearby finding — the failure
that inflated ten of the twenty review scorecards in the model benchmark.

These tests do discriminate, but not always through the Score. Four scorers spanning 5GB to
65GB all returned 99.5-100%, while Codestral-22B returned 98.9% having rated 65 of 70 issues
Found on a decoy that names 16 — a difference visible only in the Ungrounded column. Read both.

The production scorer is `Qwen3-Coder-30B-imatrix:Q3_K_M`. Qwen3.8-27B-imatrix:Q4_K_S
was benchmarked as a replacement and matched it exactly (100/100/100), but is ~6x slower
(201s against 30s on the perfect review) and summarises the Description column rather than
reproducing it, so the incumbent was kept.

## Ranked Results

`raw` is the scorer's unmodified output. `processed` applies the same
post-processing production does — duplicate removal, downgrading Notes that
cannot be matched to the review, and mis-credit detection. Production ships
`processed`, so that is the column to rank on.

Times for `claude-*` scorers are wall clock and include the network round trip;
Ollama figures are the server's own generation time and exclude it.

| # | Model | TPR | TNR | Decoy (recall/spec) | Score | Ungrounded | False credits | Perfect time | Truncated? |
|---|-------|----:|----:|-------------------:|------:|-----------:|--------------:|--------------|------------|
| 1 | glm-5.2:cloud | 100.0% | 100.0% | 100% / 100% | **100.0%** | 0 | 0 / 52 | 25.6s | No |

## Detail — Perfect Review (sensitivity)

A good scorer should return close to 70 Found.
Missed = issues the scorer failed to recognise despite being clearly stated.

| Model | Found | Partial | Missed | Total | Time | Speed |
|-------|-------|---------|--------|-------|------|-------|
| glm-5.2:cloud | 70 | 0 | 0 | 70 | 25.6s | 0.0 t/s |

## Detail — Null Review (specificity)

A good scorer should return 0 Found and 0 Partial.
Found or Partial = false positives (the scorer invented matches that aren't there).

| Model | Found | Partial | Missed | Total | Time | Speed |
|-------|-------|---------|--------|-------|------|-------|
| glm-5.2:cloud | 0 | 0 | 70 | 70 | 15.5s | 0.0 t/s |

## Detail — Decoy Review (discrimination)

The decoy names 16 issues explicitly and is silent on the other 52.
A calibrated scorer returns 16 Found. Anything it credits among the other
52 is a false credit — evidence borrowed from an unrelated finding.

| Model | Genuine found | False credits | Falsely credited IDs |
|-------|---------------|---------------|----------------------|
| glm-5.2:cloud | 16 / 16 | **0 / 52** | — |

## Run Configuration — glm-5.2:cloud

Values as actually sent for this run. Blank sampler entries mean the
request omitted them, so the model's own Modelfile applied.

| Setting | Value |
|---|---|
| Scorer model | `glm-5.2:cloud` |
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
| Branch / commit | `main @ 24cc4bb` |

| Review | Output tokens | Duration | Stop reason | Thinking chars |
|---|---|---|---|---|
| perfect | 4224 | 25.6s | stop | 1,818 |
| null | 2460 | 15.5s | stop | 477 |
| decoy | 3332 | 19.8s | stop | 3,943 |
