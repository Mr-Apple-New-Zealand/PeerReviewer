# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `46d4dd3` &nbsp;·&nbsp; **Run:** #167


## Score
Total: 19 Found / 37 Partial / 14 Missed out of 70 issues (27.1% Found)

> **⚠ Spot-check: 3 row(s) rated Found (D3, D6, D8) name a target absent from the review. Adjusted: 16 Found (22.9%).**

Scorer grounding: enforce mode, 14 row(s) downgraded for unsupported evidence (E6, RL2, RL3, N2, M1, M2, M5, A2, A3, A5, A6, CF5, CF7, CF8)

## Review Performance
**Model:** `Qwen3.5-2B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 32.5s |
| Model load time | 7.0s |
| Inference time | 25.5s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think medium |
| Prompt tokens | 11,862 |
| Output tokens | 6,517 of 40,000 limit |
| Answer / reasoning split | 19,918 chars answer, 6,519 chars reasoning |
| Output speed | 260.7 tok/s |
| Prompt speed | 24230.5 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 28.0% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 35.8s |
| Model load time | 4.1s |
| Prompt tokens | 9,958 |
| Output tokens | 4,651 |
| Output speed | 154.7 tok/s |
| Prompt speed | 6105.9 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 1m 8s |
