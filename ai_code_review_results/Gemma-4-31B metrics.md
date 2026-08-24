# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `3d4ff91` &nbsp;·&nbsp; **Run:** #158


## Score
Total: 45 Found / 25 Partial / 0 Missed out of 70 issues (64.3% Found)


Scorer grounding: enforce mode, 0 row(s) downgraded for unsupported evidence

## Review Performance
**Model:** `Gemma-4-31B-it-imatrix:Q4_K_M`

| Metric | Value |
|--------|-------|
| Total time | 4m 42s |
| Model load time | 1m 9s |
| Inference time | 3m 33s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 12,206 |
| Output tokens | 6,249 of 40,000 limit |
| Answer / reasoning split | 11,144 chars answer, 11,468 chars reasoning |
| Output speed | 30.1 tok/s |
| Prompt speed | 2305.8 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 28.2% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 33.5s |
| Model load time | 3.7s |
| Prompt tokens | 8,130 |
| Output tokens | 4,291 |
| Output speed | 151.0 tok/s |
| Prompt speed | 5923.7 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 5m 15s |
