# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `19b916c` &nbsp;·&nbsp; **Run:** #204


## Score
Total: 60 Found / 9 Partial / 1 Missed out of 70 issues (85.7% Found)

> **⚠ Spot-check: 5 row(s) rated Found (D4, D9, D10, RL5, N4) name a target absent from the review. Adjusted: 55 Found (78.6%).**

Scorer grounding: enforce mode, 1 row(s) downgraded for unsupported evidence (CF8)

## Review Performance
**Model:** `Qwen3.5-4B-imatrix:Q5_K_S`

| Metric | Value |
|--------|-------|
| Total time | 57.0s |
| Model load time | 0.3s |
| Inference time | 56.7s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think False |
| Prompt tokens | 11,863 |
| Output tokens | 8,431 of 40,000 limit |
| Answer / reasoning split | 35,127 chars answer, 0 chars reasoning |
| Output speed | 149.1 tok/s |
| Prompt speed | 153110.5 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 31.0% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 35.3s |
| Model load time | 0.1s |
| Prompt tokens | 13,575 |
| Output tokens | 4,800 |
| Output speed | 143.5 tok/s |
| Prompt speed | 9191.9 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 1m 32s |
