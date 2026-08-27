# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22` &nbsp;·&nbsp; **Run:** #217


## Score
Total: 63 Found / 0 Partial / 7 Missed out of 70 issues (90.0% Found)

> **⚠ Spot-check: 5 row(s) rated Found (D8, D10, CF9, N4, A5) name a target absent from the review. Adjusted: 58 Found (82.9%).**

Scorer grounding: enforce mode, 4 row(s) downgraded for unsupported evidence (D3, D4, D9, CF8)

## Review Performance
**Model:** `Qwen3-Coder-Next-imatrix:Q5_K_S`

| Metric | Value |
|--------|-------|
| Total time | 2m 25s |
| Model load time | 10.4s |
| Inference time | 2m 14s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 11,098 |
| Output tokens | 3,911 of 40,000 limit |
| Answer / reasoning split | 15,005 chars answer, 0 chars reasoning |
| Output speed | 31.2 tok/s |
| Prompt speed | 1228.2 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 22.9% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 1m 23s |
| Model load time | 12.2s |
| Prompt tokens | 9,263 |
| Output tokens | 5,723 |
| Output speed | 83.2 tok/s |
| Prompt speed | 4354.9 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 3m 48s |
