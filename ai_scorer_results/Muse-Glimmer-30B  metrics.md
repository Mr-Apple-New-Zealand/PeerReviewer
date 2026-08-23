# AI Model Performance Metrics

> **Branch:** `Muse-Glimmer-30B` &nbsp;·&nbsp; **Commit:** `6bda8e7` &nbsp;·&nbsp; **Run:** #142


## Score
Total: 59 Found / 4 Partial / 7 Missed out of 70 issues (84.3% Found)

> **⚠ Spot-check: 1 row(s) rated Found (C7) name a target absent from the review. Adjusted: 58 Found (82.9%).**

Scorer grounding: enforce mode, 7 row(s) downgraded for unsupported evidence (R3, E2, E7, N3, N4, N7, M4)

## Review Performance
**Model:** `Muse-Glimmer-30B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 3m 34s |
| Model load time | 0.3s |
| Inference time | 3m 33s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 10,470 |
| Output tokens | 8,355 of 40,000 limit |
| Answer / reasoning split | 12,605 chars answer, 25,552 chars reasoning |
| Output speed | 39.9 tok/s |
| Prompt speed | 3095.7 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 28.7% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 31.9s |
| Model load time | 4.1s |
| Prompt tokens | 8,193 |
| Output tokens | 4,269 |
| Output speed | 161.7 tok/s |
| Prompt speed | 6296.1 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 4m 5s |
