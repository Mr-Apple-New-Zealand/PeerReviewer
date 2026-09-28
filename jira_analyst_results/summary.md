# Jira Analyst Leaderboard

| Setting | Value |
|---|---|
| generated | 2026-09-28T16:11:01 |
| models | 6 |
| cases_sha | ec04f03cff34 |
| judge | Qwen3.8-27B-imatrix:Q4_K_S |
| judge_effort | high |
| judge_prompt_sha | 1f643fa31d52 |
| analyst_prompt_sha | 39810e7146ae |
| temperature | 0.3 |
| system_prompt | file |
| cases | C01, C02, C03, C04, C05, C06, C07, C08, C09, C10, C11, C12, C13, C14, C15, C16, C17, C18 |

## Headline

- **Best quality:** Qwen3-VL-8B-Instruct-imatrix:Q3_K_M at 49.7/100.
- **Best value** (smallest memory within 5 points of the best): Qwen3-VL-8B-Instruct-imatrix:Q3_K_M at 49.7/100, 9.4 GB resident, 7.3s per case.
- **Pareto front** (nothing else is better on both quality and memory; time is excluded because the server is shared): Qwen3-VL-8B-Instruct-imatrix:Q3_K_M, Qwen2.5-VL-7B-Instruct-imatrix:Q4_K_S, Qwen2.5-VL-3B-Instruct-imatrix:Q4_K_M.

## Ranking

| # | Model | Quality | Coverage | Traps hit | Invented keys | Unsupported | Resident GB | On GPU | Cold load | Time / case | Out tok/s | Out tok / case | Pareto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Qwen3-VL-8B-Instruct-imatrix:Q3_K_M | 49.7 (48-52) | 63% | 19/162 | 1 | 67 | 9.4 | 100% | 2.9s | 7.3s | 137.4 | 815 | yes |
| 2 | Qwen2.5-VL-32B-Instruct:Q5_K_M | 49.2 (49-50) | 54% | 7/162 | 0 | 37 | 32.5 | 100% | 5.7s | 33.9s | 28.5 | 887 |  |
| 3 | Qwen3-VL-8B-Thinking-imatrix:Q4_K_M | 47.3 (46-49) | 64% | 6/114 | 0 | 42 | 13.0 | 100% | 3.4s | 53.1s | 116.1 | 5244 |  |
| 4 | Qwen2.5-VL-72B-Instruct:Q4_K_S | 45.6 (45-47) | 48% | 8/162 | 0 | 15 | 56.3 | 100% | 7.8s | 55.2s | 14.7 | 480 |  |
| 5 | Qwen2.5-VL-7B-Instruct-imatrix:Q4_K_S | 24.5 (23-25) | 31% | 17/162 | 0 | 39 | 7.1 | 100% | 2.9s | 4.4s | 135.1 | 541 | yes |
| 6 | Qwen2.5-VL-3B-Instruct-imatrix:Q4_K_M | 14.4 (12-18) | 26% | 20/162 | 1 | 100 | 4.1 | 100% | 2.8s | 2.4s | 225.4 | 489 | yes |

## Runs

Resident GB includes the KV cache at each run's own num_ctx, so it reads higher for a model run at a larger context.

| Model | Run | Started | num_ctx | num_predict | Repeats | Harness | Folder |
|---|---|---|---|---|---|---|---|
| Qwen3-VL-8B-Instruct-imatrix:Q3_K_M | 41 | 2026-09-27T19:46:50 | 32768 | 8192 | 3 | ea239b2 | jira_analyst_results/Qwen3-VL-8B-Instruct-imatrix_Q3_K_M |
| Qwen2.5-VL-32B-Instruct:Q5_K_M | 40 | 2026-09-27T17:26:10 | 32768 | 8192 | 3 | 044571b | jira_analyst_results/Qwen2.5-VL-32B-Instruct_Q5_K_M |
| Qwen3-VL-8B-Thinking-imatrix:Q4_K_M | 42 | 2026-09-27T22:19:01 | 49152 | 16384 | 3 | ad65a3d | jira_analyst_results/Qwen3-VL-8B-Thinking-imatrix_Q4_K_M |
| Qwen2.5-VL-72B-Instruct:Q4_K_S | 36 | 2026-09-27T05:35:07 | 32768 | 8192 | 3 | 980b243 | jira_analyst_results/Qwen2.5-VL-72B-Instruct_Q4_K_S |
| Qwen2.5-VL-7B-Instruct-imatrix:Q4_K_S | 39 | 2026-09-27T10:11:04 | 32768 | 8192 | 3 | 044571b | jira_analyst_results/Qwen2.5-VL-7B-Instruct-imatrix_Q4_K_S |
| Qwen2.5-VL-3B-Instruct-imatrix:Q4_K_M | 38 | 2026-09-27T08:35:06 | 32768 | 8192 | 3 | dde479a | jira_analyst_results/Qwen2.5-VL-3B-Instruct-imatrix_Q4_K_M |

## Not ranked

- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M in `jira_analyst_results/Qwen3-VL-8B-Thinking-imatrix_Q4_K_M-v2` (run 43): different temperature 1.0 (ranked runs: 0.3)

## Score per case

| Model | C01 | C02 | C03 | C04 | C05 | C06 | C07 | C08 | C09 | C10 | C11 | C12 | C13 | C14 | C15 | C16 | C17 | C18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-VL-8B-Instruct-imatrix:Q3_K_M | 71 | 69 | 64 | 58 | 72 | 52 | 76 | 56 | 75 | 4 | 40 | 69 | 45 | 37 | 59 | 35 | 1 | 9 |
| Qwen2.5-VL-32B-Instruct:Q5_K_M | 86 | 62 | 60 | 50 | 72 | 52 | 69 | 67 | 67 | 75 | 38 | 48 | 43 | 18 | 28 | 38 | 1 | 12 |
| Qwen3-VL-8B-Thinking-imatrix:Q4_K_M | 81 | 75 | 64 | 75 | 67 | 62 | 79 | 58 | 83 | 50 | 50 | 48 | 10 | 4 | 11 | 28 | 0 | 6 |
| Qwen2.5-VL-72B-Instruct:Q4_K_S | 83 | 58 | 52 | 56 | 69 | 38 | 81 | 64 | 50 | 75 | 50 | 52 | 33 | 18 | 2 | 27 | 0 | 12 |
| Qwen2.5-VL-7B-Instruct-imatrix:Q4_K_S | 74 | 46 | 10 | 36 | 42 | 31 | 40 | 28 | 28 | 33 | 21 | 29 | 17 | 0 | 0 | 3 | 0 | 3 |
| Qwen2.5-VL-3B-Instruct-imatrix:Q4_K_M | 40 | 40 | 2 | 0 | 19 | 21 | 38 | 25 | 31 | 12 | 5 | 17 | 2 | 3 | 0 | 0 | 0 | 3 |

Cases: C01 Well-specified bug: double debit on transfer retry; C02 Vague bug: is it ready for development?; C03 Story with conflicting scope decisions; C04 Closed as fixed, but QA says it still fails; C05 Duplicate detection across four tickets; C06 Release risk from an overdue external dependency; C07 Incident timeline, durations and root cause; C08 Long noisy ticket: current state, decisions and owner; C09 Key detail only in an attached screenshot; C10 Customer ticket with an embedded instruction to AI tools; C11 Error text only in an attached screenshot, and the screenshot is provided; C12 Annotated screenshot is the whole specification; C13 Wordless markup: a circle and an arrow asking for a control to move; C14 Triage a production pod log: real faults, routine noise, and what the log cannot say; C15 The reporter read the log and picked the wrong line; C16 Two logs, one regression: quantify it without over-claiming the cause; C17 A Sentry event whose headline error is the symptom, not the fault; C18 Eight Sentry issues, four causes: group them and prioritise by impact

## Warnings

- Qwen2.5-VL-32B-Instruct:Q5_K_M: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S); timings may be contended.
- Qwen2.5-VL-3B-Instruct-imatrix:Q4_K_M: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S); timings may be contended.
- Qwen2.5-VL-3B-Instruct-imatrix:Q4_K_M: judge had 1 ungrounded and 0 omitted verdicts (downgraded / defaulted).
- Qwen2.5-VL-72B-Instruct:Q4_K_S: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S, nomic-embed-text:latest); timings may be contended.
- Qwen2.5-VL-7B-Instruct-imatrix:Q4_K_S: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S); timings may be contended.
- Qwen2.5-VL-7B-Instruct-imatrix:Q4_K_S: judge had 1 ungrounded and 0 omitted verdicts (downgraded / defaulted).
- Qwen3-VL-8B-Instruct-imatrix:Q3_K_M: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S); timings may be contended.
- Qwen3-VL-8B-Instruct-imatrix:Q3_K_M: judge had 2 ungrounded and 0 omitted verdicts (downgraded / defaulted).
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M: C15.r1: empty content
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M: C18.r1: empty content
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M: C17.r2: empty content
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M: C18.r2: empty content
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M: C10.r3: empty content
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M: C14.r3: empty content
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M: C15.r3: empty content
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M: C16.r3: empty content
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M: C17.r3: empty content
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C15: output hit num_predict
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C15: empty content (thinking 80398 chars)
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C18: output hit num_predict
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C18: empty content (thinking 61924 chars)
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C17: output hit num_predict
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C17: empty content (thinking 72036 chars)
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C18: output hit num_predict
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C18: empty content (thinking 57995 chars)
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C10: output hit num_predict
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C10: empty content (thinking 72082 chars)
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C14: output hit num_predict
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C14: empty content (thinking 79073 chars)
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C15: output hit num_predict
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C15: empty content (thinking 69281 chars)
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C16: output hit num_predict
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C16: empty content (thinking 45760 chars)
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C17: output hit num_predict
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M C17: empty content (thinking 80681 chars)
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S); timings may be contended.
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M: judge had 4 ungrounded and 1 omitted verdicts (downgraded / defaulted).

## How to read this

- **Quality** = mean case score. Each case: (points found + 0.5 x partial - penalties) / points, floored at 0. Penalties: 1 per trap asserted, 1 per invented ticket key (max 3), 0.5 per other unsupported claim (max 2).
- **Coverage** ignores penalties: the share of answer-key points the analysis made.
- **Resident GB / On GPU** come from Ollama's /api/ps after the first case, at this run's num_ctx.
- **Time / case** is Ollama's server-side duration minus load time. Cloud models report none.
- With ~10 cases, differences under ~5 points are within judge and sampling noise. Use --repeats to measure it.
