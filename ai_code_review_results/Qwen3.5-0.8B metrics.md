# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `1224407` &nbsp;·&nbsp; **Run:** #227


## Score
Total: 21 Found / 10 Partial / 39 Missed out of 70 issues (30.0% Found)

> **⚠ Spot-check: 2 row(s) rated Found (C5, L4) name a target absent from the review. Adjusted: 19 Found (27.1%).**

Scorer grounding: enforce mode, 38 row(s) downgraded for unsupported evidence (C10, C11, L5, R1, R2, R3, E3, N2, N3, N4, N6, N7, M1, M2, M3, M4, M5, D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11, A1, A2, A3, A4, A5, A6, CF7, CF8, CF9, UT)

## Review Performance
**Model:** `Qwen3.5-0.8B-imatrix:Q4_K_S`

| Metric | Value |
|--------|-------|
| Total time | 14m 41s |
| Model load time | 3.4s |
| Inference time | 14m 38s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think False |
| Prompt tokens | 11,862 |
| Output tokens | 40,000 of 40,000 limit |
| Answer / reasoning split | 162,710 chars answer, 0 chars reasoning |
| Output speed | 45.7 tok/s |
| Prompt speed | 6032.4 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 79.1% |
| Content truncated | No |
| Completed naturally | No ⚠ (hit token limit) |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 44.6s |
| Model load time | 3.9s |
| Prompt tokens | 31,782 |
| Output tokens | 3,627 |
| Output speed | 105.6 tok/s |
| Prompt speed | 5035.5 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 15m 26s |
