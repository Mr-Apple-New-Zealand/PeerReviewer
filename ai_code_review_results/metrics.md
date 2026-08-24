# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `53beb17` &nbsp;·&nbsp; **Run:** #154


## Score
Total: 69 Found / 0 Partial / 1 Missed out of 70 issues (98.6% Found)

> **⚠ Spot-check: 1 row(s) rated Found (N3) name a target absent from the review. Adjusted: 68 Found (97.1%).**

Scorer grounding: enforce mode, 1 row(s) downgraded for unsupported evidence (R3)

## Review Performance
**Model:** `Qwen3.6-27B:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 13m 28s |
| Model load time | 4.8s |
| Inference time | 13m 23s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 11,903 |
| Output tokens | 29,568 of 40,000 limit |
| Answer / reasoning split | 29,043 chars answer, 93,310 chars reasoning |
| Output speed | 37.0 tok/s |
| Prompt speed | 2558.1 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 63.3% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 41.8s |
| Model load time | 9.3s |
| Prompt tokens | 12,181 |
| Output tokens | 4,493 |
| Output speed | 148.0 tok/s |
| Prompt speed | 5956.9 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 14m 9s |
