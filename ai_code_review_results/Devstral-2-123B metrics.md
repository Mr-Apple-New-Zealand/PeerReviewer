# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `2b77eff` &nbsp;·&nbsp; **Run:** #179


## Score
Total: 52 Found / 0 Partial / 18 Missed out of 70 issues (74.3% Found)

> **⚠ Spot-check: 3 row(s) rated Found (C7, N3, D9) name a target absent from the review. Adjusted: 49 Found (70.0%).**

Scorer grounding: enforce mode, 0 row(s) downgraded for unsupported evidence

## Review Performance
**Model:** `Devstral-2-123B-Instruct-2512:Q4_K_M`

| Metric | Value |
|--------|-------|
| Total time | 6m 41s |
| Model load time | 1m 42s |
| Inference time | 4m 59s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 11,685 |
| Output tokens | 1,841 of 40,000 limit |
| Answer / reasoning split | 7,714 chars answer, 0 chars reasoning |
| Output speed | 6.7 tok/s |
| Prompt speed | 480.1 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 20.6% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 28.4s |
| Model load time | 6.4s |
| Prompt tokens | 7,130 |
| Output tokens | 3,467 |
| Output speed | 166.2 tok/s |
| Prompt speed | 6166.4 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 7m 10s |
