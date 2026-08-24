# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `46d4dd3` &nbsp;·&nbsp; **Run:** #165


## Score
Total: 6 Found / 31 Partial / 33 Missed out of 70 issues (8.6% Found)


Scorer grounding: enforce mode, 3 row(s) downgraded for unsupported evidence (D2, D6, UT)

## Review Performance
**Model:** `Qwen3.5-0.8B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 12.1s |
| Model load time | 0.3s |
| Inference time | 11.8s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think medium |
| Prompt tokens | 11,862 |
| Output tokens | 3,901 of 40,000 limit |
| Answer / reasoning split | 6,872 chars answer, 8,724 chars reasoning |
| Output speed | 341.2 tok/s |
| Prompt speed | 38706.9 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 24.1% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 28.8s |
| Model load time | 4.1s |
| Prompt tokens | 7,038 |
| Output tokens | 3,895 |
| Output speed | 165.5 tok/s |
| Prompt speed | 6278.2 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 40.9s |
