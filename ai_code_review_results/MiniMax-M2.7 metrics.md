# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22` &nbsp;·&nbsp; **Run:** #213


## Score
Total: 58 Found / 7 Partial / 5 Missed out of 70 issues (82.9% Found)

> **⚠ Spot-check: 1 row(s) rated Found (D11) name a target absent from the review. Adjusted: 57 Found (81.4%).**

Scorer grounding: enforce mode, 5 row(s) downgraded for unsupported evidence (R3, E2, N4, N5, M4)

## Review Performance
**Model:** `MiniMax-M2.7:Q3_K_S`

| Metric | Value |
|--------|-------|
| Total time | 7m 46s |
| Model load time | 19.2s |
| Inference time | 7m 27s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 10,532 |
| Output tokens | 6,777 of 40,000 limit |
| Answer / reasoning split | 14,386 chars answer, 13,012 chars reasoning |
| Output speed | 16.1 tok/s |
| Prompt speed | 413.6 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 26.4% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 37.7s |
| Model load time | 13.6s |
| Prompt tokens | 8,834 |
| Output tokens | 3,634 |
| Output speed | 160.3 tok/s |
| Prompt speed | 6148.8 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 8m 24s |
