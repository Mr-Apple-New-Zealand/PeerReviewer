# AI Model Performance Metrics

> **Branch:** `main` &nbsp;·&nbsp; **Commit:** `53beb17` &nbsp;·&nbsp; **Run:** #152


## Score
Total: 60 Found / 1 Partial / 9 Missed out of 70 issues (85.7% Found)


Scorer grounding: enforce mode, 9 row(s) downgraded for unsupported evidence (C10, C11, R3, E5, E7, N4, CF2, CF7, CF8)

## Review Performance
**Model:** `gpt-oss:120B`

| Metric | Value |
|--------|-------|
| Total time | 32m 2s |
| Model load time | 17.9s |
| Inference time | 31m 44s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think (model default) |
| Prompt tokens | 10,504 |
| Output tokens | 40,000 of 40,000 limit |
| Answer / reasoning split | 135,654 chars answer, 31,938 chars reasoning |
| Output speed | 21.1 tok/s |
| Prompt speed | 1275.1 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 77.1% |
| Content truncated | No |
| Completed naturally | No ⚠ (hit token limit) |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 55.6s |
| Model load time | 6.4s |
| Prompt tokens | 33,691 |
| Output tokens | 4,282 |
| Output speed | 102.2 tok/s |
| Prompt speed | 4660.8 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 32m 57s |
