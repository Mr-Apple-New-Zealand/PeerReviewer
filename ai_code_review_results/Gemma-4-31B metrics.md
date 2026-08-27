# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `67ece22` &nbsp;·&nbsp; **Run:** #212


## Score
Total: 55 Found / 3 Partial / 12 Missed out of 70 issues (78.6% Found)

> **⚠ Spot-check: 1 row(s) rated Found (E5) name a target absent from the review. Adjusted: 54 Found (77.1%).**

Scorer grounding: enforce mode, 12 row(s) downgraded for unsupported evidence (L5, R1, R3, E7, N4, N5, N7, M4, D5, A6, CF7, CF9)

## Review Performance
**Model:** `Gemma-4-31B-it-imatrix:Q4_K_M`

| Metric | Value |
|--------|-------|
| Total time | 3m 16s |
| Model load time | 5.8s |
| Inference time | 3m 10s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 12,226 |
| Output tokens | 5,574 of 40,000 limit |
| Answer / reasoning split | 10,518 chars answer, 9,903 chars reasoning |
| Output speed | 30.2 tok/s |
| Prompt speed | 2302.6 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 27.2% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 30.3s |
| Model load time | 3.8s |
| Prompt tokens | 7,909 |
| Output tokens | 4,073 |
| Output speed | 161.9 tok/s |
| Prompt speed | 6231.4 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 3m 46s |
