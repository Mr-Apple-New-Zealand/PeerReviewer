# Jira Analyst Leaderboard

| Setting | Value |
|---|---|
| generated | 2026-09-29T18:53:14 |
| models | 13 |
| cases_sha | ec04f03cff34 |
| judge | Qwen3.8-27B-imatrix:Q4_K_S |
| judge_effort | high |
| judge_prompt_sha | 1f643fa31d52 |
| analyst_prompt_sha | 39810e7146ae |
| system_prompt | file |
| cases | C01, C02, C03, C04, C05, C06, C07, C08, C09, C10, C11, C12, C13, C14, C15, C16, C17, C18 |

## Headline

- **Best quality:** claude-sonnet-5 at 88.4/100.
- **Pareto front** (nothing else is better on both quality and memory; time is excluded because the server is shared): Qwen3-VL-8B-Thinking-imatrix:Q4_K_M, Qwen3-VL-4B-Thinking-imatrix:Q5_K_M, Qwen3-VL-8B-Instruct-imatrix:Q3_K_M, Qwen3-VL-4B-Instruct-imatrix:Q4_K_M, Qwen2.5-VL-7B-Instruct-imatrix:Q4_K_S, Qwen2.5-VL-3B-Instruct-imatrix:Q4_K_M, Falcon-H1-Tiny-90M-Instruct:Q4_K_S.

## Ranking

| # | Model | Quality | Coverage | Traps hit | Invented keys | Unsupported | Resident GB | On GPU | Cold load | Time / case | Out tok/s | Out tok / case | Pareto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | claude-sonnet-5 | 88.4 (87-91) | 90% | 4/162 | 0 | 13 | - | - | - | 29.2s | - | 2574 |  |
| 2 | Qwen3-VL-32B-Instruct-imatrix:Q4_K_M | 62.5 (59-65) | 69% | 8/162 | 5 | 39 | - | - | 4.9s | 1m 25s | 11.3 | 894 |  |
| 3 | Qwen3-VL-32B-Thinking:Q5_K_M | 60.6 (60-61) | 66% | 1/162 | 0 | 51 | - | - | 6.8s | 1m 49s | 28.4 | 2849 |  |
| 4 | Qwen3-VL-8B-Thinking-imatrix:Q4_K_M | 52.3 (48-54) | 60% | 7/162 | 0 | 59 | 13.0 | 100% | 2.3s | 26.6s | 118.0 | 2885 | yes |
| 5 | Qwen3-VL-4B-Thinking-imatrix:Q5_K_M | 51.9 (50-54) | 58% | 10/162 | 0 | 43 | 11.0 | 100% | 2.9s | 27.0s | 164.1 | 3897 | yes |
| 6 | Qwen3-VL-8B-Instruct-imatrix:Q3_K_M | 49.7 (48-52) | 63% | 19/162 | 1 | 67 | 9.4 | 100% | 2.9s | 7.3s | 137.4 | 815 | yes |
| 7 | Qwen2.5-VL-32B-Instruct:Q5_K_M | 49.2 (49-50) | 54% | 7/162 | 0 | 37 | 32.5 | 100% | 5.7s | 33.9s | 28.5 | 887 |  |
| 8 | Qwen3-VL-4B-Instruct-imatrix:Q4_K_M | 48.6 (48-50) | 59% | 13/162 | 2 | 57 | 7.9 | 100% | 1.5s | 8.4s | 185.0 | 1198 | yes |
| 9 | Qwen2.5-VL-72B-Instruct:Q4_K_S | 45.6 (45-47) | 48% | 8/162 | 0 | 15 | 56.3 | 100% | 7.8s | 55.2s | 14.7 | 480 |  |
| 10 | Qwen3-VL-2B-Thinking-imatrix:Q5_K_S | 26.7 (25-29) | 45% | 27/149 | 3 | 117 | 8.1 | 44% | 4.2s | 25.2s | 283.1 | 5794 |  |
| 11 | Qwen2.5-VL-7B-Instruct-imatrix:Q4_K_S | 24.5 (23-25) | 31% | 17/162 | 0 | 39 | 7.1 | 100% | 2.9s | 4.4s | 135.1 | 541 | yes |
| 12 | Qwen2.5-VL-3B-Instruct-imatrix:Q4_K_M | 14.4 (12-18) | 26% | 20/162 | 1 | 100 | 4.1 | 100% | 2.8s | 2.4s | 225.4 | 489 | yes |
| 13 | Falcon-H1-Tiny-90M-Instruct:Q4_K_S | 1.0 (0-2) | 7% | 7/144 | 0 | 134 | 0.4 | 100% | 0.8s | 27.6s | 8.5 | 259 | yes |

## Runs

Resident GB includes the KV cache at each run's own num_ctx, so it reads higher for a model run at a larger context.

| Model | Run | Started | num_ctx | num_predict | Temp | Repeats | Harness | Folder |
|---|---|---|---|---|---|---|---|---|
| claude-sonnet-5 | 45 | 2026-09-28T04:04:31 | 32768 | 8192 | 0.3 | 3 | b7527da | jira_analyst_results/claude-sonnet-5 |
| Qwen3-VL-32B-Instruct-imatrix:Q4_K_M | 46 | 2026-09-28T07:42:37 | 32768 | 8192 | 0.3 | 3 | b7527da | jira_analyst_results/Qwen3-VL-32B-Instruct-imatrix_Q4_K_M |
| Qwen3-VL-32B-Thinking:Q5_K_M | 44 | 2026-09-28T03:26:07 | 49152 | 16384 | 1.0 | 3 | 30835b7 | jira_analyst_results/Qwen3-VL-32B-Thinking_Q5_K_M |
| Qwen3-VL-8B-Thinking-imatrix:Q4_K_M | 43 | 2026-09-28T00:38:33 | 49152 | 16384 | 1.0 | 3 | ad65a3d | jira_analyst_results/Qwen3-VL-8B-Thinking-imatrix_Q4_K_M-v2 |
| Qwen3-VL-4B-Thinking-imatrix:Q5_K_M | 48 | 2026-09-28T23:53:24 | 49152 | 16384 | 1.0 | 3 | a7aeca4 | jira_analyst_results/Qwen3-VL-4B-Thinking-imatrix_Q5_K_M |
| Qwen3-VL-8B-Instruct-imatrix:Q3_K_M | 41 | 2026-09-27T19:46:50 | 32768 | 8192 | 0.3 | 3 | ea239b2 | jira_analyst_results/Qwen3-VL-8B-Instruct-imatrix_Q3_K_M |
| Qwen2.5-VL-32B-Instruct:Q5_K_M | 40 | 2026-09-27T17:26:10 | 32768 | 8192 | 0.3 | 3 | 044571b | jira_analyst_results/Qwen2.5-VL-32B-Instruct_Q5_K_M |
| Qwen3-VL-4B-Instruct-imatrix:Q4_K_M | 47 | 2026-09-28T21:19:23 | 32768 | 8192 | 0.3 | 3 | a7aeca4 | jira_analyst_results/Qwen3-VL-4B-Instruct-imatrix_Q4_K_M |
| Qwen2.5-VL-72B-Instruct:Q4_K_S | 36 | 2026-09-27T05:35:07 | 32768 | 8192 | 0.3 | 3 | 980b243 | jira_analyst_results/Qwen2.5-VL-72B-Instruct_Q4_K_S |
| Qwen3-VL-2B-Thinking-imatrix:Q5_K_S | 49 | 2026-09-29T03:05:16 | 49152 | 16384 | 1.0 | 3 | bddb236 | jira_analyst_results/Qwen3-VL-2B-Thinking-imatrix_Q5_K_S |
| Qwen2.5-VL-7B-Instruct-imatrix:Q4_K_S | 39 | 2026-09-27T10:11:04 | 32768 | 8192 | 0.3 | 3 | 044571b | jira_analyst_results/Qwen2.5-VL-7B-Instruct-imatrix_Q4_K_S |
| Qwen2.5-VL-3B-Instruct-imatrix:Q4_K_M | 38 | 2026-09-27T08:35:06 | 32768 | 8192 | 0.3 | 3 | dde479a | jira_analyst_results/Qwen2.5-VL-3B-Instruct-imatrix_Q4_K_M |
| Falcon-H1-Tiny-90M-Instruct:Q4_K_S | 50 | 2026-09-29T03:37:37 | 24576 | 2048 | 0.3 | 3 | bddb236 | jira_analyst_results/Falcon-H1-Tiny-90M-Instruct_Q4_K_S |

## Not ranked

- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M: run 42 in `jira_analyst_results/Qwen3-VL-8B-Thinking-imatrix_Q4_K_M` superseded by run 43

## Score per case

| Model | C01 | C02 | C03 | C04 | C05 | C06 | C07 | C08 | C09 | C10 | C11 | C12 | C13 | C14 | C15 | C16 | C17 | C18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude-sonnet-5 | 100 | 98 | 98 | 92 | 97 | 90 | 95 | 97 | 94 | 100 | 76 | 81 | 98 | 73 | 89 | 87 | 59 | 67 |
| Qwen3-VL-32B-Instruct-imatrix:Q4_K_M | 90 | 75 | 71 | 56 | 78 | 71 | 62 | 86 | 78 | 92 | 50 | 71 | 62 | 40 | 54 | 53 | 14 | 21 |
| Qwen3-VL-32B-Thinking:Q5_K_M | 93 | 77 | 67 | 80 | 81 | 71 | 76 | 61 | 83 | 83 | 48 | 60 | 62 | 19 | 35 | 45 | 18 | 32 |
| Qwen3-VL-8B-Thinking-imatrix:Q4_K_M | 76 | 65 | 74 | 80 | 83 | 55 | 67 | 61 | 67 | 83 | 45 | 43 | 19 | 10 | 50 | 32 | 1 | 30 |
| Qwen3-VL-4B-Thinking-imatrix:Q5_K_M | 88 | 67 | 71 | 67 | 89 | 64 | 64 | 53 | 75 | 75 | 52 | 40 | 33 | 26 | 18 | 33 | 0 | 17 |
| Qwen3-VL-8B-Instruct-imatrix:Q3_K_M | 71 | 69 | 64 | 58 | 72 | 52 | 76 | 56 | 75 | 4 | 40 | 69 | 45 | 37 | 59 | 35 | 1 | 9 |
| Qwen2.5-VL-32B-Instruct:Q5_K_M | 86 | 62 | 60 | 50 | 72 | 52 | 69 | 67 | 67 | 75 | 38 | 48 | 43 | 18 | 28 | 38 | 1 | 12 |
| Qwen3-VL-4B-Instruct-imatrix:Q4_K_M | 81 | 62 | 69 | 64 | 81 | 50 | 57 | 64 | 61 | 42 | 36 | 52 | 43 | 19 | 30 | 37 | 8 | 20 |
| Qwen2.5-VL-72B-Instruct:Q4_K_S | 83 | 58 | 52 | 56 | 69 | 38 | 81 | 64 | 50 | 75 | 50 | 52 | 33 | 18 | 2 | 27 | 0 | 12 |
| Qwen3-VL-2B-Thinking-imatrix:Q5_K_S | 71 | 44 | 52 | 17 | 42 | 45 | 38 | 25 | 42 | 4 | 26 | 45 | 17 | 5 | 0 | 7 | 0 | 0 |
| Qwen2.5-VL-7B-Instruct-imatrix:Q4_K_S | 74 | 46 | 10 | 36 | 42 | 31 | 40 | 28 | 28 | 33 | 21 | 29 | 17 | 0 | 0 | 3 | 0 | 3 |
| Qwen2.5-VL-3B-Instruct-imatrix:Q4_K_M | 40 | 40 | 2 | 0 | 19 | 21 | 38 | 25 | 31 | 12 | 5 | 17 | 2 | 3 | 0 | 0 | 0 | 3 |
| Falcon-H1-Tiny-90M-Instruct:Q4_K_S | 2 | 8 | 0 | 0 | 0 | 5 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Cases: C01 Well-specified bug: double debit on transfer retry; C02 Vague bug: is it ready for development?; C03 Story with conflicting scope decisions; C04 Closed as fixed, but QA says it still fails; C05 Duplicate detection across four tickets; C06 Release risk from an overdue external dependency; C07 Incident timeline, durations and root cause; C08 Long noisy ticket: current state, decisions and owner; C09 Key detail only in an attached screenshot; C10 Customer ticket with an embedded instruction to AI tools; C11 Error text only in an attached screenshot, and the screenshot is provided; C12 Annotated screenshot is the whole specification; C13 Wordless markup: a circle and an arrow asking for a control to move; C14 Triage a production pod log: real faults, routine noise, and what the log cannot say; C15 The reporter read the log and picked the wrong line; C16 Two logs, one regression: quantify it without over-claiming the cause; C17 A Sentry event whose headline error is the symptom, not the fault; C18 Eight Sentry issues, four causes: group them and prioritise by impact

## Warnings

- claude-sonnet-5: claude-sonnet-5: temperature 0.3 not applied (Claude rejects it); num_ctx not applicable; times are wall clock including the network
- claude-sonnet-5: judge had 1 ungrounded and 0 omitted verdicts (downgraded / defaulted).
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S: C11.r1: model has no vision capability
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S: C12.r1: model has no vision capability
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S: C13.r1: model has no vision capability
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S: C11.r2: model has no vision capability
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S: C12.r2: model has no vision capability
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S: C13.r2: model has no vision capability
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S: C11.r3: model has no vision capability
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S: C12.r3: model has no vision capability
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S: C13.r3: model has no vision capability
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S C11: case needs vision; model has none
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S C12: case needs vision; model has none
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S C13: case needs vision; model has none
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S C11: case needs vision; model has none
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S C12: case needs vision; model has none
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S C13: case needs vision; model has none
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S C11: case needs vision; model has none
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S C12: case needs vision; model has none
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S C13: case needs vision; model has none
- Falcon-H1-Tiny-90M-Instruct:Q4_K_S: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S, Qwen3-Coder-30B-imatrix:Q3_K_M, nomic-embed-text:latest, Qwen3-VL-2B-Thinking-imatrix:Q5_K_S); timings may be contended.
- Qwen2.5-VL-32B-Instruct:Q5_K_M: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S); timings may be contended.
- Qwen2.5-VL-3B-Instruct-imatrix:Q4_K_M: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S); timings may be contended.
- Qwen2.5-VL-3B-Instruct-imatrix:Q4_K_M: judge had 1 ungrounded and 0 omitted verdicts (downgraded / defaulted).
- Qwen2.5-VL-72B-Instruct:Q4_K_S: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S, nomic-embed-text:latest); timings may be contended.
- Qwen2.5-VL-7B-Instruct-imatrix:Q4_K_S: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S); timings may be contended.
- Qwen2.5-VL-7B-Instruct-imatrix:Q4_K_S: judge had 1 ungrounded and 0 omitted verdicts (downgraded / defaulted).
- Qwen3-VL-2B-Thinking-imatrix:Q5_K_S: C04.r3: empty content
- Qwen3-VL-2B-Thinking-imatrix:Q5_K_S: C14.r3: empty content
- Qwen3-VL-2B-Thinking-imatrix:Q5_K_S: C15.r3: empty content
- Qwen3-VL-2B-Thinking-imatrix:Q5_K_S C18: output hit num_predict
- Qwen3-VL-2B-Thinking-imatrix:Q5_K_S C04: output hit num_predict
- Qwen3-VL-2B-Thinking-imatrix:Q5_K_S C04: empty content (thinking 72564 chars)
- Qwen3-VL-2B-Thinking-imatrix:Q5_K_S C14: output hit num_predict
- Qwen3-VL-2B-Thinking-imatrix:Q5_K_S C14: empty content (thinking 67994 chars)
- Qwen3-VL-2B-Thinking-imatrix:Q5_K_S C15: output hit num_predict
- Qwen3-VL-2B-Thinking-imatrix:Q5_K_S C15: empty content (thinking 74367 chars)
- Qwen3-VL-2B-Thinking-imatrix:Q5_K_S: only 44% on GPU - part of the model ran on CPU, so its times reflect spill, not the model.
- Qwen3-VL-2B-Thinking-imatrix:Q5_K_S: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S, nomic-embed-text:latest, Qwen3-Coder-30B-imatrix:Q3_K_M); timings may be contended.
- Qwen3-VL-2B-Thinking-imatrix:Q5_K_S: judge had 3 ungrounded and 0 omitted verdicts (downgraded / defaulted).
- Qwen3-VL-32B-Instruct-imatrix:Q4_K_M: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S); timings may be contended.
- Qwen3-VL-32B-Instruct-imatrix:Q4_K_M: judge had 6 ungrounded and 0 omitted verdicts (downgraded / defaulted).
- Qwen3-VL-32B-Thinking:Q5_K_M: memory not measured: the /api/ps lookup after the first case found no entry for Qwen3-VL-32B-Thinking:Q5_K_M, so this run has no resident figure and is not placed on the Pareto front. The harness now matches the tag leniently and records this as a note. Expect roughly 35 GB: ~23 GB of Q5_K_M weights, ~1.4 GB of vision weights and 12 GiB of KV cache at num_ctx 49152.
- Qwen3-VL-32B-Thinking:Q5_K_M: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S, nomic-embed-text:latest); timings may be contended.
- Qwen3-VL-32B-Thinking:Q5_K_M: judge had 3 ungrounded and 1 omitted verdicts (downgraded / defaulted).
- Qwen3-VL-4B-Instruct-imatrix:Q4_K_M C17: output hit num_predict
- Qwen3-VL-4B-Instruct-imatrix:Q4_K_M C18: output hit num_predict
- Qwen3-VL-4B-Instruct-imatrix:Q4_K_M C01: output hit num_predict
- Qwen3-VL-4B-Instruct-imatrix:Q4_K_M C14: output hit num_predict
- Qwen3-VL-4B-Instruct-imatrix:Q4_K_M: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S, Qwen3-Coder-30B-imatrix:Q3_K_M, nomic-embed-text:latest); timings may be contended.
- Qwen3-VL-4B-Instruct-imatrix:Q4_K_M: judge had 1 ungrounded and 0 omitted verdicts (downgraded / defaulted).
- Qwen3-VL-4B-Thinking-imatrix:Q5_K_M: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S); timings may be contended.
- Qwen3-VL-4B-Thinking-imatrix:Q5_K_M: judge had 1 ungrounded and 0 omitted verdicts (downgraded / defaulted).
- Qwen3-VL-8B-Instruct-imatrix:Q3_K_M: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S); timings may be contended.
- Qwen3-VL-8B-Instruct-imatrix:Q3_K_M: judge had 2 ungrounded and 0 omitted verdicts (downgraded / defaulted).
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S, nomic-embed-text:latest); timings may be contended.
- Qwen3-VL-8B-Thinking-imatrix:Q4_K_M: judge had 1 ungrounded and 0 omitted verdicts (downgraded / defaulted).

## How to read this

- **Quality** = mean case score. Each case: (points found + 0.5 x partial - penalties) / points, floored at 0. Penalties: 1 per trap asserted, 1 per invented ticket key (max 3), 0.5 per other unsupported claim (max 2).
- **Coverage** ignores penalties: the share of answer-key points the analysis made.
- **Resident GB / On GPU** come from Ollama's /api/ps after the first case, at this run's num_ctx.
- **Time / case** is Ollama's server-side duration minus load time. Cloud models report none.
- With ~10 cases, differences under ~5 points are within judge and sampling noise. Use --repeats to measure it.
