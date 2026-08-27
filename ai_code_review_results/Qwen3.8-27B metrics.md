# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22` &nbsp;·&nbsp; **Run:** #210


## Score
Total: 62 Found / 0 Partial / 8 Missed out of 70 issues (88.6% Found)

> Zero Partial ratings — spot-check found no mis-credits, but worth a second look.

Scorer grounding: enforce mode, 8 row(s) downgraded for unsupported evidence (C8, R2, R3, E6, RL3, N5, M1, M3)

## Review Performance
**Model:** `Qwen3.8-27B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 5m 31s |
| Model load time | 3.5s |
| Inference time | 5m 27s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think medium |
| Prompt tokens | 11,860 |
| Output tokens | 12,312 of 40,000 limit |
| Answer / reasoning split | 27,268 chars answer, 19,547 chars reasoning |
| Output speed | 38.2 tok/s |
| Prompt speed | 2499.6 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 36.9% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 34.2s |
| Model load time | 2.7s |
| Prompt tokens | 12,597 |
| Output tokens | 4,310 |
| Output speed | 147.1 tok/s |
| Prompt speed | 5839.0 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 6m 5s |
