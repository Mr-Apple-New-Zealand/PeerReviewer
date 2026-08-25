# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `74c6567` &nbsp;·&nbsp; **Run:** #186


## Score
Total: 50 Found / 17 Partial / 3 Missed out of 70 issues (71.4% Found)

> **⚠ Spot-check: 2 row(s) rated Found (C7, D9) name a target absent from the review. Adjusted: 48 Found (68.6%).**

Scorer grounding: enforce mode, 0 row(s) downgraded for unsupported evidence

## Review Performance
**Model:** `Qwen3.5-9B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 2m 12s |
| Model load time | 2.4s |
| Inference time | 2m 10s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think medium |
| Prompt tokens | 11,859 |
| Output tokens | 7,296 of 40,000 limit |
| Answer / reasoning split | 26,907 chars answer, 4,919 chars reasoning |
| Output speed | 56.8 tok/s |
| Prompt speed | 8107.0 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 29.2% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 45.6s |
| Model load time | 12.6s |
| Prompt tokens | 11,073 |
| Output tokens | 4,706 |
| Output speed | 151.2 tok/s |
| Prompt speed | 6082.8 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 2m 58s |
