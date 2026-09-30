# Jira Analyst Benchmark - run 58

| Setting | Value |
|---|---|
| started | 2026-09-30T05:45:12 |
| harness_commit | b1c29df |
| num_ctx | 49152 |
| num_predict | 16384 |
| temperature | 1.0 |
| seed | None |
| repeats | 3 |
| system_prompt | file |
| analyst_prompt_sha | 39810e7146ae |
| judge | claude-sonnet-5 |
| judge_effort | high |
| judge_prompt_sha | 1f643fa31d52 |
| cases_sha | ec04f03cff34 |
| cases | C01, C02, C03, C04, C05, C06, C07, C08, C09, C10, C11, C12, C13, C14, C15, C16, C17, C18 |

## Headline

- **Best quality:** Muse-Glimmer-30B-imatrix:Q4_K_S at 81.1/100.
- **Best value** (smallest memory within 5 points of the best): Muse-Glimmer-30B-imatrix:Q4_K_S at 81.1/100, 16.7 GB resident, 51.2s per case.
- **Pareto front** (nothing else is better on both quality and memory; time is excluded because the server is shared): Muse-Glimmer-30B-imatrix:Q4_K_S.

## Ranking

| # | Model | Quality | Coverage | Traps hit | Invented keys | Unsupported | Resident GB | On GPU | Cold load | Time / case | Out tok/s | Out tok / case | Pareto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Muse-Glimmer-30B-imatrix:Q4_K_S | 81.1 (80-82) | 84% | 5/162 | 0 | 24 | 16.7 | 100% | 5.6s | 51.2s | 40.4 | 2022 | yes |

## Score per case

| Model | C01 | C02 | C03 | C04 | C05 | C06 | C07 | C08 | C09 | C10 | C11 | C12 | C13 | C14 | C15 | C16 | C17 | C18 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Muse-Glimmer-30B-imatrix:Q4_K_S | 98 | 88 | 90 | 89 | 94 | 88 | 100 | 89 | 100 | 100 | 71 | 67 | 83 | 51 | 89 | 67 | 48 | 48 |

Cases: C01 Well-specified bug: double debit on transfer retry; C02 Vague bug: is it ready for development?; C03 Story with conflicting scope decisions; C04 Closed as fixed, but QA says it still fails; C05 Duplicate detection across four tickets; C06 Release risk from an overdue external dependency; C07 Incident timeline, durations and root cause; C08 Long noisy ticket: current state, decisions and owner; C09 Key detail only in an attached screenshot; C10 Customer ticket with an embedded instruction to AI tools; C11 Error text only in an attached screenshot, and the screenshot is provided; C12 Annotated screenshot is the whole specification; C13 Wordless markup: a circle and an arrow asking for a control to move; C14 Triage a production pod log: real faults, routine noise, and what the log cannot say; C15 The reporter read the log and picked the wrong line; C16 Two logs, one regression: quantify it without over-claiming the cause; C17 A Sentry event whose headline error is the symptom, not the fault; C18 Eight Sentry issues, four causes: group them and prioritise by impact

## Warnings

- Muse-Glimmer-30B-imatrix:Q4_K_S: other models were resident at start (Qwen3.8-27B-imatrix:Q4_K_S); timings may be contended.
- Muse-Glimmer-30B-imatrix:Q4_K_S: judge had 0 ungrounded and 1 omitted verdicts (downgraded / defaulted).

## How to read this

- **Quality** = mean case score. Each case: (points found + 0.5 x partial - penalties) / points, floored at 0. Penalties: 1 per trap asserted, 1 per invented ticket key (max 3), 0.5 per other unsupported claim (max 2).
- **Coverage** ignores penalties: the share of answer-key points the analysis made.
- **Resident GB / On GPU** come from Ollama's /api/ps after the first case, at this run's num_ctx.
- **Time / case** is Ollama's server-side duration minus load time. Cloud models report none.
- With ~10 cases, differences under ~5 points are within judge and sampling noise. Use --repeats to measure it.
