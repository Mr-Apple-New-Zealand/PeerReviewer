# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `00111c5` &nbsp;·&nbsp; **Run:** #175


## Score
Total: 47 Found / 0 Partial / 23 Missed out of 70 issues (67.1% Found)

> **⚠ Spot-check: 1 row(s) rated Found (CF9) name a target absent from the review. Adjusted: 46 Found (65.7%).**

Scorer grounding: enforce mode, 23 row(s) downgraded for unsupported evidence (C10, L2, L4, R1, R3, E2, E6, E7, RL1, RL2, RL3, RL5, N3, N4, N5, M2, D3, D8, D9, D10, A2, A5, UT)

## Review Performance
**Model:** `Qwen3.5-122B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 2m 47s |
| Model load time | 1m 21s |
| Inference time | 1m 26s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 11,857 |
| Output tokens | 6,795 of 40,000 limit |
| Answer / reasoning split | 27,214 chars answer, 0 chars reasoning |
| Output speed | 83.0 tok/s |
| Prompt speed | 3062.3 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 28.5% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 36.8s |
| Model load time | 8.7s |
| Prompt tokens | 12,032 |
| Output tokens | 3,900 |
| Output speed | 149.5 tok/s |
| Prompt speed | 5904.8 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 3m 24s |
