# AI Model Performance Metrics

> **Branch:** `Jack-3.8-27B-Coder` &nbsp;·&nbsp; **Commit:** `1c6f8a7` &nbsp;·&nbsp; **Run:** #147


## Score
Total: 68 Found / 1 Partial / 1 Missed out of 70 issues (97.1% Found)

> **⚠ Spot-check: 1 row(s) rated Found (D5) name a target absent from the review. Adjusted: 67 Found (95.7%).**

Scorer grounding: enforce mode, 1 row(s) downgraded for unsupported evidence (N5)

## Review Performance
**Model:** `hf.co/JackAgentLead/Jack-3.8-27B-Coder-16GB-VRAM:latest`

| Metric | Value |
|--------|-------|
| Total time | 4m 21s |
| Model load time | 6.6s |
| Inference time | 4m 14s |
| Sampler | temp 0.3, top_p (model default), top_k (model default) |
| Reasoning | system (model default), think medium |
| Prompt tokens | 15,575 |
| Output tokens | 11,510 of 40,000 limit |
| Answer / reasoning split | 25,589 chars answer, 18,017 chars reasoning |
| Output speed | 46.5 tok/s |
| Prompt speed | 2281.7 tok/s |
| Context window | 65,536 tokens |
| Context utilization | 41.3% |
| Content truncated | No |
| Completed naturally | Yes |

## Scoring Performance
**Model:** `Qwen3-Coder-30B-imatrix:Q3_K_M`

| Metric | Value |
|--------|-------|
| Total time | 35.4s |
| Model load time | 4.1s |
| Prompt tokens | 11,958 |
| Output tokens | 4,361 |
| Output speed | 149.1 tok/s |
| Prompt speed | 6064.7 tok/s |
| Completed naturally | Yes |

## Combined
| Metric | Value |
|--------|-------|
| Review + scoring time | 4m 56s |
