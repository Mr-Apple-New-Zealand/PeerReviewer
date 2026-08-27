# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22` &nbsp;·&nbsp; **Run:** #220


## Score
Total: 23 Found / 46 Partial / 1 Missed out of 70 issues (32.9% Found)

> **⚠ Spot-check: 1 row(s) rated Found (D6) name a target absent from the review. Adjusted: 22 Found (31.4%).**

Scorer grounding: enforce mode, 1 row(s) downgraded for unsupported evidence (A5)

## Review Performance
**Model:** `Codestral-22B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 1m 20s |
| Model load time | 3.4s |
| Inference time | 1m 17s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 12,994 |
| Output tokens | 2,989 of 40,000 limit |
| Answer / reasoning split | 11,471 chars answer, 0 chars reasoning |
| Output speed | 41.4 tok/s |
| Prompt speed | 2975.0 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 24.4% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 32.7s |
| Model load time | 4.2s |
| Prompt tokens | 8,018 |
| Output tokens | 4,412 |
| Output speed | 162.0 tok/s |
| Prompt speed | 6177.6 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 1m 53s |
