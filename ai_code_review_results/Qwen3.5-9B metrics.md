# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `04c7dd4` &nbsp;·&nbsp; **Run:** #209


## Score
Total: 41 Found / 28 Partial / 1 Missed out of 70 issues (58.6% Found)


Scorer grounding: enforce mode, 1 row(s) downgraded for unsupported evidence (UT)

## Review Performance
**Model:** `Qwen3.5-9B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 42.4s |
| Model load time | 5.7s |
| Inference time | 36.7s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think False |
| Prompt tokens | 11,860 |
| Output tokens | 3,875 of 40,000 limit |
| Answer / reasoning split | 15,981 chars answer, 0 chars reasoning |
| Output speed | 110.2 tok/s |
| Prompt speed | 8045.8 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 24.0% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 32.5s |
| Model load time | 3.0s |
| Prompt tokens | 9,111 |
| Output tokens | 4,413 |
| Output speed | 157.9 tok/s |
| Prompt speed | 6103.5 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 1m 15s |
