# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `00111c5` &nbsp;·&nbsp; **Run:** #178


## Score
Total: 38 Found / 11 Partial / 21 Missed out of 70 issues (54.3% Found)

> **⚠ Spot-check: 2 row(s) rated Found (C5, C7) name a target absent from the review. Adjusted: 36 Found (51.4%).**

Scorer grounding: enforce mode, 21 row(s) downgraded for unsupported evidence (C8, L2, R1, R3, E4, E6, RL1, RL3, N3, N4, N7, M2, M3, M4, D9, D11, A1, A2, CF4, CF7, CF8)

## Review Performance
**Model:** `Qwen3-32B-imatrix:Q4_K_M`

| Metric | Value |
|--------|-------|
| Total time | 1m 38s |
| Model load time | 5.0s |
| Inference time | 1m 33s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 11,095 |
| Output tokens | 2,583 of 40,000 limit |
| Answer / reasoning split | 10,770 chars answer, 0 chars reasoning |
| Output speed | 29.3 tok/s |
| Prompt speed | 2124.1 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 20.9% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 29.6s |
| Model load time | 3.8s |
| Prompt tokens | 7,965 |
| Output tokens | 3,991 |
| Output speed | 163.0 tok/s |
| Prompt speed | 6290.2 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 2m 8s |
