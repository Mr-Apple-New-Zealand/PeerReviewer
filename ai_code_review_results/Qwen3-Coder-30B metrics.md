# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22` &nbsp;·&nbsp; **Run:** #215


## Score
Total: 36 Found / 27 Partial / 7 Missed out of 70 issues (51.4% Found)

> **⚠ Spot-check: 2 row(s) rated Found (D11, N4) name a target absent from the review. Adjusted: 34 Found (48.6%).**

Scorer grounding: enforce mode, 7 row(s) downgraded for unsupported evidence (R1, R3, E2, E7, A2, A5, CF8)

## Review Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 6m 10s |
| Model load time | 4.1s |
| Inference time | 6m 6s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 11,097 |
| Output tokens | 40,000 of 40,000 limit |
| Answer / reasoning split | 200,309 chars answer, 0 chars reasoning |
| Output speed | 110.0 tok/s |
| Prompt speed | 5791.1 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 78.0% |
| Content truncated | No |
| Completed naturally | No ⚠ (hit token limit) |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 40.6s |
| Model load time | 0.1s |
| Prompt tokens | 27,485 |
| Output tokens | 3,715 |
| Output speed | 113.0 tok/s |
| Prompt speed | 4932.4 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 6m 50s |
