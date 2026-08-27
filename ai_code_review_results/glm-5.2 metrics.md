# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22` &nbsp;·&nbsp; **Run:** #223


## Score
Total: 70 Found / 0 Partial / 0 Missed out of 70 issues (100.0% Found)

> **⚠ Spot-check: 1 row(s) rated Found (N3) name a target absent from the review. Adjusted: 69 Found (98.6%).**

Scorer grounding: enforce mode, 0 row(s) downgraded for unsupported evidence

## Review Performance
**Model:** `glm-5.2:cloud`

| Metric | Value |
|--------|-------|
| Total time | 47.5s |
| Model load time | 0.0s |
| Inference time | 47.5s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 10,230 |
| Output tokens | 6,767 of 40,000 limit |
| Answer / reasoning split | 27,381 chars answer, 43 chars reasoning |
| Output speed | 0.0 tok/s |
| Prompt speed | 0.0 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 25.9% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 36.6s |
| Model load time | 0.1s |
| Prompt tokens | 12,294 |
| Output tokens | 5,064 |
| Output speed | 146.8 tok/s |
| Prompt speed | 10106.1 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 1m 24s |
