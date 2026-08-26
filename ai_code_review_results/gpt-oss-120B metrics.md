# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `15dbff8` &nbsp;·&nbsp; **Run:** #194


## Score
Total: 65 Found / 0 Partial / 5 Missed out of 70 issues (92.9% Found)

> **⚠ Spot-check: 7 row(s) rated Found (N3, CF9, L3, E5, N4, M2, A1) name a target absent from the review. Adjusted: 58 Found (82.9%).**

Scorer grounding: enforce mode, 1 row(s) downgraded for unsupported evidence (CF8)

## Review Performance
**Model:** `gpt-oss:120B`

| Metric | Value |
|--------|-------|
| Total time | 1m 34s |
| Model load time | 11.5s |
| Inference time | 1m 23s |
| Sampler | temp 0.0, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 10,531 |
| Output tokens | 8,511 of 40,000 limit |
| Answer / reasoning split | 27,795 chars answer, 9,669 chars reasoning |
| Output speed | 104.6 tok/s |
| Prompt speed | 6983.9 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 29.1% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 35.2s |
| Model load time | 3.1s |
| Prompt tokens | 12,069 |
| Output tokens | 4,577 |
| Output speed | 148.2 tok/s |
| Prompt speed | 10661.0 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 2m 10s |
