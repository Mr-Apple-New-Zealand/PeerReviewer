# Jira Analyst Benchmark - run 52

| Setting | Value |
|---|---|
| started | 2026-09-29T06:01:13 |
| harness_commit | b1c29df |
| num_ctx | 49152 |
| num_predict | 16384 |
| temperature | 1.0 |
| seed | None |
| repeats | 3 |
| system_prompt | file |
| analyst_prompt_sha | 39810e7146ae |
| judge | Qwen3.8-27B-imatrix:Q4_K_S |
| judge_effort | high |
| judge_prompt_sha | 1f643fa31d52 |
| cases_sha | ec04f03cff34 |
| cases | C01, C02, C03, C04, C05, C06, C07, C08, C09, C10, C11, C12, C13, C14, C15, C16, C17, C18 |

## Headline

- **Best quality:** Gemma-4-31B-it-imatrix:Q4_K_M at 66.7/100.
- **Best value** (smallest memory within 5 points of the best): Gemma-4-31B-it-imatrix:Q4_K_M at 66.7/100, 22.7 GB resident, 4m 51s per case.
- **Pareto front** (nothing else is better on both quality and memory; time is excluded because the server is shared): Gemma-4-31B-it-imatrix:Q4_K_M.

## Ranking

| # | Model | Quality | Coverage | Traps hit | Invented keys | Unsupported | Resident GB | On GPU | Cold load | Time / case | Out tok/s | Out tok / case | Pareto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Gemma-4-31B-it-imatrix:Q4_K_M | 66.7 (65-69) | 68% | 3/162 | 0 | 11 | 22.7 | 91% | 8.0s | 4m 51s | 5.3 | 1230 | yes |

## Score per case

| Model | C01 | C02 | C03 | C04 | C05 | C06 | C07 | C08 | C09 | C10 | C11 | C12 | C13 | C14 | C15 | C16 | C17 | C18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Gemma-4-31B-it-imatrix:Q4_K_M | 90 | 81 | 64 | 89 | 81 | 74 | 86 | 83 | 80 | 79 | 50 | 64 | 57 | 42 | 50 | 63 | 24 | 41 |

Cases: C01 Well-specified bug: double debit on transfer retry; C02 Vague bug: is it ready for development?; C03 Story with conflicting scope decisions; C04 Closed as fixed, but QA says it still fails; C05 Duplicate detection across four tickets; C06 Release risk from an overdue external dependency; C07 Incident timeline, durations and root cause; C08 Long noisy ticket: current state, decisions and owner; C09 Key detail only in an attached screenshot; C10 Customer ticket with an embedded instruction to AI tools; C11 Error text only in an attached screenshot, and the screenshot is provided; C12 Annotated screenshot is the whole specification; C13 Wordless markup: a circle and an arrow asking for a control to move; C14 Triage a production pod log: real faults, routine noise, and what the log cannot say; C15 The reporter read the log and picked the wrong line; C16 Two logs, one regression: quantify it without over-claiming the cause; C17 A Sentry event whose headline error is the symptom, not the fault; C18 Eight Sentry issues, four causes: group them and prioritise by impact

## Warnings

- Gemma-4-31B-it-imatrix:Q4_K_M: only 91% on GPU - part of the model ran on CPU, so its times reflect spill, not the model.
- Gemma-4-31B-it-imatrix:Q4_K_M: other models were resident at start (Qwen3-VL-2B-Instruct-imatrix:Q4_K_M, Qwen3.8-27B-imatrix:Q4_K_S); timings may be contended.

## How to read this

- **Quality** = mean case score. Each case: (points found + 0.5 x partial - penalties) / points, floored at 0. Penalties: 1 per trap asserted, 1 per invented ticket key (max 3), 0.5 per other unsupported claim (max 2).
- **Coverage** ignores penalties: the share of answer-key points the analysis made.
- **Resident GB / On GPU** come from Ollama's /api/ps after the first case, at this run's num_ctx.
- **Time / case** is Ollama's server-side duration minus load time. Cloud models report none.
- With ~10 cases, differences under ~5 points are within judge and sampling noise. Use --repeats to measure it.
