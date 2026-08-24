# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `9e0947e` &nbsp;·&nbsp; **Run:** #168


## Score
Total: 34 Found / 7 Partial / 26 Missed out of 67 issues (50.7% Found)

> **⚠ Spot-check: 1 row(s) rated Found (E7) name a target absent from the review. Adjusted: 33 Found (49.3%).**

Scorer grounding: enforce mode, 26 row(s) downgraded for unsupported evidence (E3, E4, RL5, N1, N3, N4, N5, N6, N7, M1, M2, M3, M4, M5, D1, D3, D4, D5, D6, D7, D8, D9, D10, D11, A1, UT)

## Review Performance
**Model:** `Qwen3.5-4B-imatrix:Q5_K_S`

| Metric | Value |
|--------|-------|
| Total time | 5m 11s |
| Model load time | 11.8s |
| Inference time | 4m 59s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think medium |
| Prompt tokens | 11,867 |
| Output tokens | 40,000 of 40,000 limit |
| Answer / reasoning split | 150,833 chars answer, 15,737 chars reasoning |
| Output speed | 134.3 tok/s |
| Prompt speed | 11473.4 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 79.1% |
| Content truncated | No |
| Completed naturally | No ⚠ (hit token limit) |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 58.3s |
| Model load time | 4.1s |
| Prompt tokens | 30,679 |
| Output tokens | 5,103 |
| Output speed | 106.3 tok/s |
| Prompt speed | 5072.6 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 6m 9s |
