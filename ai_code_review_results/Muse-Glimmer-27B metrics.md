# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `3601896` &nbsp;·&nbsp; **Run:** #151


## Score
Total: 55 Found / 12 Partial / 3 Missed out of 70 issues (78.6% Found)


Scorer grounding: enforce mode, 2 row(s) downgraded for unsupported evidence (E7, N4)

## Review Performance
**Model:** `Muse-Glimmer-30B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 4m 49s |
| Model load time | 5.1s |
| Inference time | 4m 44s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 10,460 |
| Output tokens | 11,188 of 40,000 limit |
| Answer / reasoning split | 16,458 chars answer, 35,483 chars reasoning |
| Output speed | 39.9 tok/s |
| Prompt speed | 3079.1 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 33.0% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 35.1s |
| Model load time | 4.1s |
| Prompt tokens | 9,324 |
| Output tokens | 4,627 |
| Output speed | 156.9 tok/s |
| Prompt speed | 6208.9 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 5m 24s |
