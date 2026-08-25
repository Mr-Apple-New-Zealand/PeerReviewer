# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `00111c5` &nbsp;·&nbsp; **Run:** #176


## Score
Total: 44 Found / 21 Partial / 5 Missed out of 70 issues (62.9% Found)

> **⚠ Spot-check: 2 row(s) rated Found (C5, D9) name a target absent from the review. Adjusted: 42 Found (60.0%).**

Scorer grounding: enforce mode, 5 row(s) downgraded for unsupported evidence (R3, E2, M4, CF2, CF8)

## Review Performance
**Model:** `Qwen3-Coder-Next-imatrix:Q5_K_S`

| Metric | Value |
|--------|-------|
| Total time | 1m 16s |
| Model load time | 39.4s |
| Inference time | 37.0s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 11,095 |
| Output tokens | 4,255 of 40,000 limit |
| Answer / reasoning split | 16,533 chars answer, 0 chars reasoning |
| Output speed | 123.4 tok/s |
| Prompt speed | 4481.4 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 23.4% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 28.8s |
| Model load time | 3.1s |
| Prompt tokens | 9,637 |
| Output tokens | 3,895 |
| Output speed | 157.3 tok/s |
| Prompt speed | 10720.4 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 1m 45s |
