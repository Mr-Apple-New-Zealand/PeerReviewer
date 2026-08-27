# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22` &nbsp;·&nbsp; **Run:** #216


## Score
Total: 69 Found / 0 Partial / 1 Missed out of 70 issues (98.6% Found)

> **⚠ Spot-check: 3 row(s) rated Found (CF9, N2, N4) name a target absent from the review. Adjusted: 66 Found (94.3%).**

Scorer grounding: enforce mode, 1 row(s) downgraded for unsupported evidence (CF8)

## Review Performance
**Model:** `Qwen3.5-122B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 4m 24s |
| Model load time | 13.4s |
| Inference time | 4m 10s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 11,860 |
| Output tokens | 12,203 of 40,000 limit |
| Answer / reasoning split | 24,362 chars answer, 23,978 chars reasoning |
| Output speed | 50.4 tok/s |
| Prompt speed | 1447.5 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 36.7% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 49.6s |
| Model load time | 14.9s |
| Prompt tokens | 11,397 |
| Output tokens | 4,889 |
| Output speed | 149.6 tok/s |
| Prompt speed | 5874.4 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 5m 13s |
