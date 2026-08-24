# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `9e0947e` &nbsp;·&nbsp; **Run:** #169


## Score
Total: 21 Found / 27 Partial / 22 Missed out of 70 issues (30.0% Found)


Scorer grounding: enforce mode, 19 row(s) downgraded for unsupported evidence (C4, C6, C7, C10, C11, L1, L5, E6, RL2, RL5, N7, M2, M4, D7, D9, A5, CF4, CF8, CF9)

## Review Performance
**Model:** `Qwen3.5-9B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 1m 46s |
| Model load time | 24.1s |
| Inference time | 1m 22s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think medium |
| Prompt tokens | 11,867 |
| Output tokens | 8,736 of 40,000 limit |
| Answer / reasoning split | 8,582 chars answer, 26,827 chars reasoning |
| Output speed | 108.8 tok/s |
| Prompt speed | 8127.3 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 31.4% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 30.8s |
| Model load time | 3.8s |
| Prompt tokens | 7,445 |
| Output tokens | 4,209 |
| Output speed | 163.5 tok/s |
| Prompt speed | 6317.7 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 2m 17s |
