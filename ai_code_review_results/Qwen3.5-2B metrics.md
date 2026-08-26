# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `19b916c` &nbsp;·&nbsp; **Run:** #202


## Score
Total: 22 Found / 36 Partial / 12 Missed out of 70 issues (31.4% Found)


Scorer grounding: enforce mode, 12 row(s) downgraded for unsupported evidence (R2, RL2, N5, M4, D3, D9, D10, D11, A2, A3, A5, A6)

## Review Performance
**Model:** `Qwen3.5-2B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 22.9s |
| Model load time | 3.2s |
| Inference time | 19.7s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think False |
| Prompt tokens | 11,863 |
| Output tokens | 5,002 of 40,000 limit |
| Answer / reasoning split | 20,609 chars answer, 0 chars reasoning |
| Output speed | 260.8 tok/s |
| Prompt speed | 23990.1 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 25.7% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 43.8s |
| Model load time | 4.1s |
| Prompt tokens | 10,203 |
| Output tokens | 5,778 |
| Output speed | 152.0 tok/s |
| Prompt speed | 6208.1 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 1m 7s |
