# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `00111c5` &nbsp;·&nbsp; **Run:** #172


## Score
Total: 57 Found / 0 Partial / 13 Missed out of 70 issues (81.4% Found)

> **⚠ Spot-check: 7 row(s) rated Found (C7, D3, D4, D5, D7, D9, D10) name a target absent from the review. Adjusted: 50 Found (71.4%).**

Scorer grounding: enforce mode, 12 row(s) downgraded for unsupported evidence (E4, E7, RL4, RL5, N4, N7, M3, M4, A4, A5, CF7, CF8)

## Review Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 6m 10s |
| Model load time | 4.4s |
| Inference time | 6m 6s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 11,128 |
| Output tokens | 40,000 of 40,000 limit |
| Answer / reasoning split | 182,822 chars answer, 0 chars reasoning |
| Output speed | 110.0 tok/s |
| Prompt speed | 5832.0 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 78.0% |
| Content truncated | No |
| Completed naturally | No ⚠ (hit token limit) |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 41.2s |
| Model load time | 0.1s |
| Prompt tokens | 29,462 |
| Output tokens | 3,587 |
| Output speed | 109.6 tok/s |
| Prompt speed | 4736.7 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 6m 51s |
