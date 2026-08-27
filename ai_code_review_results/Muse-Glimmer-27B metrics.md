# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `1224407` &nbsp;·&nbsp; **Run:** #225


## Score
Total: 69 Found / 0 Partial / 1 Missed out of 70 issues (98.6% Found)

> **⚠ Spot-check: 5 row(s) rated Found (N3, D5, CF9, N4, M1) name a target absent from the review. Adjusted: 64 Found (91.4%).**

Scorer grounding: enforce mode, 1 row(s) downgraded for unsupported evidence (E7)

## Review Performance
**Model:** `Muse-Glimmer-30B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 4m 37s |
| Model load time | 5.1s |
| Inference time | 4m 32s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 10,473 |
| Output tokens | 10,696 of 40,000 limit |
| Answer / reasoning split | 15,533 chars answer, 34,921 chars reasoning |
| Output speed | 39.9 tok/s |
| Prompt speed | 3073.7 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 32.3% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 33.3s |
| Model load time | 3.8s |
| Prompt tokens | 8,877 |
| Output tokens | 4,459 |
| Output speed | 158.8 tok/s |
| Prompt speed | 6230.5 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 5m 10s |
