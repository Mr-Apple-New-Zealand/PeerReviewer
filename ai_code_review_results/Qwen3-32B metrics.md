# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22` &nbsp;·&nbsp; **Run:** #218


## Score
Total: 29 Found / 11 Partial / 30 Missed out of 70 issues (41.4% Found)

> **⚠ Spot-check: 4 row(s) rated Found (D6, D9, D11, CF8) name a target absent from the review. Adjusted: 25 Found (35.7%).**

Scorer grounding: enforce mode, 2 row(s) downgraded for unsupported evidence (A6, UT)

## Review Performance
**Model:** `Qwen3-32B-imatrix:Q4_K_M`

| Metric | Value |
|--------|-------|
| Total time | 1m 34s |
| Model load time | 5.0s |
| Inference time | 1m 29s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 11,097 |
| Output tokens | 2,444 of 40,000 limit |
| Answer / reasoning split | 6,704 chars answer, 3,786 chars reasoning |
| Output speed | 29.3 tok/s |
| Prompt speed | 2118.9 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 20.7% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 26.8s |
| Model load time | 4.1s |
| Prompt tokens | 6,964 |
| Output tokens | 3,589 |
| Output speed | 166.6 tok/s |
| Prompt speed | 6274.7 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 2m 0s |
