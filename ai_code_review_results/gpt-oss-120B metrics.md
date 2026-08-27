# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `1224407` &nbsp;·&nbsp; **Run:** #226


## Score
Total: 62 Found / 0 Partial / 8 Missed out of 70 issues (88.6% Found)

> **⚠ Spot-check: 4 row(s) rated Found (D3, L4, E5, M2) name a target absent from the review. Adjusted: 58 Found (82.9%).**

Scorer grounding: enforce mode, 8 row(s) downgraded for unsupported evidence (C10, C11, E7, N1, N2, N3, CF8, CF9)

## Review Performance
**Model:** `gpt-oss:120B`

| Metric | Value |
|--------|-------|
| Total time | 2m 14s |
| Model load time | 17.4s |
| Inference time | 1m 56s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 10,530 |
| Output tokens | 11,914 of 40,000 limit |
| Answer / reasoning split | 36,119 chars answer, 14,464 chars reasoning |
| Output speed | 103.7 tok/s |
| Prompt speed | 6987.7 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 34.2% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 38.6s |
| Model load time | 3.1s |
| Prompt tokens | 14,450 |
| Output tokens | 4,811 |
| Output speed | 141.0 tok/s |
| Prompt speed | 10564.8 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 2m 52s |
