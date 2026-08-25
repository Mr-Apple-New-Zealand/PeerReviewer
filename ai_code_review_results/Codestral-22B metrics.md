# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `2b77eff` &nbsp;·&nbsp; **Run:** #180


## Score
Total: 24 Found / 39 Partial / 7 Missed out of 70 issues (34.3% Found)

> **⚠ Spot-check: 2 row(s) rated Found (D6, D11) name a target absent from the review. Adjusted: 22 Found (31.4%).**

Scorer grounding: enforce mode, 7 row(s) downgraded for unsupported evidence (C5, C7, L5, RL2, RL5, N2, A5)

## Review Performance
**Model:** `Codestral-22B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 1m 20s |
| Model load time | 3.5s |
| Inference time | 1m 16s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 12,977 |
| Output tokens | 2,977 of 40,000 limit |
| Answer / reasoning split | 10,869 chars answer, 0 chars reasoning |
| Output speed | 41.3 tok/s |
| Prompt speed | 2966.5 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 24.3% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 30.3s |
| Model load time | 3.8s |
| Prompt tokens | 8,040 |
| Output tokens | 4,083 |
| Output speed | 162.5 tok/s |
| Prompt speed | 6286.4 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 1m 50s |
