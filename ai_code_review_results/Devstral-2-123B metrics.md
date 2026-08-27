# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22` &nbsp;·&nbsp; **Run:** #219


## Score
Total: 32 Found / 28 Partial / 10 Missed out of 70 issues (45.7% Found)


Scorer grounding: enforce mode, 10 row(s) downgraded for unsupported evidence (C10, C11, L1, R1, R3, E4, E5, D2, CF2, CF7)

## Review Performance
**Model:** `Devstral-2-123B-Instruct-2512:Q4_K_M`

| Metric | Value |
|--------|-------|
| Total time | 5m 27s |
| Model load time | 15.9s |
| Inference time | 5m 11s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 11,701 |
| Output tokens | 1,916 of 40,000 limit |
| Answer / reasoning split | 7,588 chars answer, 0 chars reasoning |
| Output speed | 6.7 tok/s |
| Prompt speed | 482.3 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 20.8% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 30.2s |
| Model load time | 6.1s |
| Prompt tokens | 7,166 |
| Output tokens | 3,784 |
| Output speed | 165.1 tok/s |
| Prompt speed | 6112.6 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 5m 57s |
