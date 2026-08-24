# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `7edff07` &nbsp;·&nbsp; **Run:** #163


## Score
Total: 65 Found / 0 Partial / 5 Missed out of 70 issues (92.9% Found)

> **⚠ Spot-check: 3 row(s) rated Found (D4, D5, D6) name a target absent from the review. Adjusted: 62 Found (88.6%).**

Scorer grounding: enforce mode, 0 row(s) downgraded for unsupported evidence

## Review Performance
**Model:** `MiniMax-M2.7:Q3_K_S`

| Metric | Value |
|--------|-------|
| Total time | 6m 8s |
| Model load time | 0.2s |
| Inference time | 6m 8s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 10,533 |
| Output tokens | 5,512 of 40,000 limit |
| Answer / reasoning split | 16,875 chars answer, 6,228 chars reasoning |
| Output speed | 16.1 tok/s |
| Prompt speed | 415.8 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 24.5% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 38.6s |
| Model load time | 8.4s |
| Prompt tokens | 9,480 |
| Output tokens | 4,480 |
| Output speed | 156.5 tok/s |
| Prompt speed | 6077.3 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 6m 47s |
