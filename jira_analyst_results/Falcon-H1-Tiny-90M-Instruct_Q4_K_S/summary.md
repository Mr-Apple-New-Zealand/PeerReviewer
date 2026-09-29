# Jira Analyst Benchmark - run 50

| Setting | Value |
|---|---|
| started | 2026-09-29T03:37:37 |
| harness_commit | bddb236 |
| num_ctx | 24576 |
| num_predict | 2048 |
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

- **Best quality:** Falcon-H1-Tiny-90M-Instruct:Q4_K_S at 1.0/100.
- **Best value** (smallest memory within 5 points of the best): Falcon-H1-Tiny-90M-Instruct:Q4_K_S at 1.0/100, 0.4 GB resident, 27.6s per case.
- **Pareto front** (nothing else is better on both quality and memory; time is excluded because the server is shared): Falcon-H1-Tiny-90M-Instruct:Q4_K_S.

## Ranking

| # | Model | Quality | Coverage | Traps hit | Invented keys | Unsupported | Resident GB | On GPU | Cold load | Time / case | Out tok/s | Out tok / case | Pareto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Falcon-H1-Tiny-90M-Instruct:Q4_K_S | 1.0 (0-2) | 7% | 7/144 | 0 | 134 | 0.4 | 100% | 0.8s | 27.6s | 8.5 | 259 | yes |

## Score per case

| Model | C01 | C02 | C03 | C04 | C05 | C06 | C07 | C08 | C09 | C10 | C11 | C12 | C13 | C14 | C15 | C16 | C17 | C18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Falcon-H1-Tiny-90M-Instruct:Q4_K_S | 2 | 8 | 0 | 0 | 0 | 5 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

Cases: C01 Well-specified bug: double debit on transfer retry; C02 Vague bug: is it ready for development?; C03 Story with conflicting scope decisions; C04 Closed as fixed, but QA says it still fails; C05 Duplicate detection across four tickets; C06 Release risk from an overdue external dependency; C07 Incident timeline, durations and root cause; C08 Long noisy ticket: current state, decisions and owner; C09 Key detail only in an attached screenshot; C10 Customer ticket with an embedded instruction to AI tools; C11 Error text only in an attached screenshot, and the screenshot is provided; C12 Annotated screenshot is the whole specification; C13 Wordless markup: a circle and an arrow asking for a control to move; C14 Triage a production pod log: real faults, routine noise, and what the log cannot say; C15 The reporter read the log and picked the wrong line; C16 Two logs, one regression: quantify it without over-claiming the cause; C17 A Sentry event whose headline error is the symptom, not the fault; C18 Eight Sentry issues, four causes: group them and prioritise by impact

## Warnings

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

## How to read this

- **Quality** = mean case score. Each case: (points found + 0.5 x partial - penalties) / points, floored at 0. Penalties: 1 per trap asserted, 1 per invented ticket key (max 3), 0.5 per other unsupported claim (max 2).
- **Coverage** ignores penalties: the share of answer-key points the analysis made.
- **Resident GB / On GPU** come from Ollama's /api/ps after the first case, at this run's num_ctx.
- **Time / case** is Ollama's server-side duration minus load time. Cloud models report none.
- With ~10 cases, differences under ~5 points are within judge and sampling noise. Use --repeats to measure it.
