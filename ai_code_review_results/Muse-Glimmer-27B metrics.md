# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `06d631c` &nbsp;·&nbsp; **Run:** #155


## Score
Total: 61 Found / 8 Partial / 1 Missed out of 70 issues (87.1% Found)

> **⚠ Spot-check: 1 row(s) rated Found (C7) name a target absent from the review. Adjusted: 60 Found (85.7%).**

Scorer grounding: enforce mode, 1 row(s) downgraded for unsupported evidence (N4)

## Review Performance
**Model:** `Muse-Glimmer-30B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 6m 58s |
| Model load time | 1m 53s |
| Inference time | 5m 5s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 10,462 |
| Output tokens | 12,023 of 40,000 limit |
| Answer / reasoning split | 13,704 chars answer, 44,084 chars reasoning |
| Output speed | 39.8 tok/s |
| Prompt speed | 3002.2 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 34.3% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 38.7s |
| Model load time | 8.0s |
| Prompt tokens | 8,433 |
| Output tokens | 4,685 |
| Output speed | 159.9 tok/s |
| Prompt speed | 6257.3 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 7m 37s |
