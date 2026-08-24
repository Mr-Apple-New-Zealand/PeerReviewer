# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `3d4ff91` &nbsp;·&nbsp; **Run:** #157


## Score
Total: 69 Found / 0 Partial / 1 Missed out of 70 issues (98.6% Found)

> **⚠ Spot-check: 1 row(s) rated Found (N3) name a target absent from the review. Adjusted: 68 Found (97.1%).**

Scorer grounding: enforce mode, 1 row(s) downgraded for unsupported evidence (N4)

## Review Performance
**Model:** `Qwen3.8-27B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 50m 16s |
| Model load time | 0.3s |
| Inference time | 50m 16s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think medium |
| Prompt tokens | 11,866 |
| Output tokens | 11,739 of 40,000 limit |
| Answer / reasoning split | 26,348 chars answer, 19,314 chars reasoning |
| Output speed | 3.9 tok/s |
| Prompt speed | 18611.4 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 36.0% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 39.4s |
| Model load time | 3.9s |
| Prompt tokens | 12,258 |
| Output tokens | 4,924 |
| Output speed | 147.1 tok/s |
| Prompt speed | 6029.3 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 50m 55s |
