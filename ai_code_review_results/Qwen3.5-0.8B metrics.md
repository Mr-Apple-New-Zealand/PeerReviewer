# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `15dbff8` &nbsp;·&nbsp; **Run:** #195


## Score
Total: 15 Found / 1 Partial / 54 Missed out of 70 issues (21.4% Found)

> **⚠ Spot-check: 2 row(s) rated Found (L3, CF7) name a target absent from the review. Adjusted: 13 Found (18.6%).**

Scorer grounding: enforce mode, 52 row(s) downgraded for unsupported evidence (C4, C5, C6, C7, C11, L5, R2, E1, E2, E3, E4, E5, E6, E7, RL1, RL2, RL3, RL4, RL5, N1, N2, N3, N4, N5, N6, N7, M1, M2, M3, M4, M5, D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, A1, A2, A3, A4, A5, A6, CF5, CF8, CF9, UT)

## Review Performance
**Model:** `Qwen3.5-0.8B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 2m 8s |
| Model load time | 1.7s |
| Inference time | 2m 6s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think medium |
| Prompt tokens | 11,860 |
| Output tokens | 40,000 of 40,000 limit |
| Answer / reasoning split | 154,143 chars answer, 6,829 chars reasoning |
| Output speed | 317.9 tok/s |
| Prompt speed | 45232.0 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 79.1% |
| Content truncated | No |
| Completed naturally | No ⚠ (hit token limit) |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 35.5s |
| Model load time | 0.1s |
| Prompt tokens | 31,001 |
| Output tokens | 3,453 |
| Output speed | 107.0 tok/s |
| Prompt speed | 11097.5 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 2m 43s |
