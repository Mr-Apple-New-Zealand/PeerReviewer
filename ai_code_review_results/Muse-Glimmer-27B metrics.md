# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `72b5896` &nbsp;·&nbsp; **Run:** #192


## Score
Total: 61 Found / 7 Partial / 2 Missed out of 70 issues (87.1% Found)

> **⚠ Spot-check: 3 row(s) rated Found (D5, L3, N4) name a target absent from the review. Adjusted: 58 Found (82.9%).**

Scorer grounding: enforce mode, 2 row(s) downgraded for unsupported evidence (E7, CF9)

## Review Performance
**Model:** `Muse-Glimmer-30B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 6m 33s |
| Model load time | 3.8s |
| Inference time | 6m 29s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 10,475 |
| Output tokens | 12,756 of 40,000 limit |
| Answer / reasoning split | 16,281 chars answer, 45,140 chars reasoning |
| Output speed | 33.1 tok/s |
| Prompt speed | 3083.0 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 35.4% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 39.6s |
| Model load time | 4.2s |
| Prompt tokens | 9,119 |
| Output tokens | 5,313 |
| Output speed | 156.7 tok/s |
| Prompt speed | 6233.0 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 7m 12s |
