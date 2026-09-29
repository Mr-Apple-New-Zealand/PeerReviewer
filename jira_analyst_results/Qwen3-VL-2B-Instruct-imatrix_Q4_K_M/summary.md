# Jira Analyst Benchmark - run 51

| Setting | Value |
|---|---|
| started | 2026-09-29T05:43:55 |
| harness_commit | bddb236 |
| num_ctx | 32768 |
| num_predict | 8192 |
| temperature | 0.3 |
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

- **Best quality:** Qwen3-VL-2B-Instruct-imatrix:Q4_K_M at 25.3/100.
- **Best value** (smallest memory within 5 points of the best): Qwen3-VL-2B-Instruct-imatrix:Q4_K_M at 25.3/100, 5.4 GB resident, 28.6s per case.
- **Pareto front** (nothing else is better on both quality and memory; time is excluded because the server is shared): Qwen3-VL-2B-Instruct-imatrix:Q4_K_M.

## Ranking

| # | Model | Quality | Coverage | Traps hit | Invented keys | Unsupported | Resident GB | On GPU | Cold load | Time / case | Out tok/s | Out tok / case | Pareto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Qwen3-VL-2B-Instruct-imatrix:Q4_K_M | 25.3 (21-31) | 40% | 30/162 | 1 | 114 | 5.4 | 100% | 2.6s | 28.6s | 289.4 | 1946 | yes |

## Score per case

| Model | C01 | C02 | C03 | C04 | C05 | C06 | C07 | C08 | C09 | C10 | C11 | C12 | C13 | C14 | C15 | C16 | C17 | C18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Qwen3-VL-2B-Instruct-imatrix:Q4_K_M | 71 | 19 | 29 | 0 | 39 | 55 | 31 | 36 | 44 | 29 | 21 | 40 | 19 | 6 | 0 | 13 | 0 | 2 |

Cases: C01 Well-specified bug: double debit on transfer retry; C02 Vague bug: is it ready for development?; C03 Story with conflicting scope decisions; C04 Closed as fixed, but QA says it still fails; C05 Duplicate detection across four tickets; C06 Release risk from an overdue external dependency; C07 Incident timeline, durations and root cause; C08 Long noisy ticket: current state, decisions and owner; C09 Key detail only in an attached screenshot; C10 Customer ticket with an embedded instruction to AI tools; C11 Error text only in an attached screenshot, and the screenshot is provided; C12 Annotated screenshot is the whole specification; C13 Wordless markup: a circle and an arrow asking for a control to move; C14 Triage a production pod log: real faults, routine noise, and what the log cannot say; C15 The reporter read the log and picked the wrong line; C16 Two logs, one regression: quantify it without over-claiming the cause; C17 A Sentry event whose headline error is the symptom, not the fault; C18 Eight Sentry issues, four causes: group them and prioritise by impact

## Warnings

- Qwen3-VL-2B-Instruct-imatrix:Q4_K_M C14: output hit num_predict
- Qwen3-VL-2B-Instruct-imatrix:Q4_K_M C16: output hit num_predict
- Qwen3-VL-2B-Instruct-imatrix:Q4_K_M C17: output hit num_predict
- Qwen3-VL-2B-Instruct-imatrix:Q4_K_M C17: output hit num_predict
- Qwen3-VL-2B-Instruct-imatrix:Q4_K_M C13: output hit num_predict
- Qwen3-VL-2B-Instruct-imatrix:Q4_K_M C14: output hit num_predict
- Qwen3-VL-2B-Instruct-imatrix:Q4_K_M C16: output hit num_predict
- Qwen3-VL-2B-Instruct-imatrix:Q4_K_M: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S, Falcon-H1-Tiny-90M-Instruct:Q4_K_S); timings may be contended.
- Qwen3-VL-2B-Instruct-imatrix:Q4_K_M: judge had 2 ungrounded and 0 omitted verdicts (downgraded / defaulted).

## How to read this

- **Quality** = mean case score. Each case: (points found + 0.5 x partial - penalties) / points, floored at 0. Penalties: 1 per trap asserted, 1 per invented ticket key (max 3), 0.5 per other unsupported claim (max 2).
- **Coverage** ignores penalties: the share of answer-key points the analysis made.
- **Resident GB / On GPU** come from Ollama's /api/ps after the first case, at this run's num_ctx.
- **Time / case** is Ollama's server-side duration minus load time. Cloud models report none.
- With ~10 cases, differences under ~5 points are within judge and sampling noise. Use --repeats to measure it.
