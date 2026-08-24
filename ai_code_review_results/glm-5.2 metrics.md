# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `00111c5` &nbsp;·&nbsp; **Run:** #173


## Score
Total: 70 Found / 0 Partial / 0 Missed out of 70 issues (100.0% Found)

> **⚠ Spot-check: 3 row(s) rated Found (R3, N3, D5) name a target absent from the review. Adjusted: 67 Found (95.7%).**

Scorer grounding: enforce mode, 0 row(s) downgraded for unsupported evidence

## Review Performance
**Model:** `glm-5.2:cloud`

| Metric | Value |
|--------|-------|
| Total time | 50.5s |
| Model load time | 0.0s |
| Inference time | 50.5s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 10,210 |
| Output tokens | 7,747 of 40,000 limit |
| Answer / reasoning split | 19,883 chars answer, 12,258 chars reasoning |
| Output speed | 0.0 tok/s |
| Prompt speed | 0.0 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 27.4% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 32.9s |
| Model load time | 0.1s |
| Prompt tokens | 10,281 |
| Output tokens | 4,721 |
| Output speed | 153.9 tok/s |
| Prompt speed | 12162.6 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 1m 23s |
