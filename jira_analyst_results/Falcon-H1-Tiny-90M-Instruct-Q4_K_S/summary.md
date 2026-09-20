# Jira Analyst Benchmark - run 7

| Setting | Value |
|---|---|
| started | 2026-09-19T22:26:47 |
| harness_commit | 7c67a2c |
| num_ctx | 49152 |
| num_predict | 16384 |
| temperature | 0.3 |
| seed | None |
| repeats | 1 |
| system_prompt | file |
| analyst_prompt_sha | 28a068655527 |
| judge | claude-sonnet-5 |
| judge_effort | high |
| judge_prompt_sha | 1f643fa31d52 |
| cases_sha | 0d562c11c9a3 |
| cases | C01, C02, C03, C04, C05, C06, C07, C08, C09, C10 |

## Headline

- **Best quality:** Falcon-H1-Tiny-90M-Instruct:latest at 3.2/100.
- **Best value** (smallest memory within 5 points of the best): Falcon-H1-Tiny-90M-Instruct:latest at 3.2/100, 0.9 GB resident, 20.2s per case.
- **Pareto front** (nothing else is better on quality, memory and time at once): Falcon-H1-Tiny-90M-Instruct:latest.

## Ranking

| # | Model | Quality | Coverage | Traps hit | Invented keys | Unsupported | Resident GB | On GPU | Cold load | Time / case | Out tok/s | Out tok / case | Pareto |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Falcon-H1-Tiny-90M-Instruct:latest | 3.2 | 10% | 0/19 | 0 | 27 | 0.9 | 100% | 0.8s | 20.2s | 10.6 | 220 | yes |

## Score per case

| Model | C01 | C02 | C03 | C04 | C05 | C06 | C07 | C08 | C09 | C10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Falcon-H1-Tiny-90M-Instruct:latest | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 25 |

Cases: C01 Well-specified bug: double debit on transfer retry; C02 Vague bug: is it ready for development?; C03 Story with conflicting scope decisions; C04 Closed as fixed, but QA says it still fails; C05 Duplicate detection across four tickets; C06 Release risk from an overdue external dependency; C07 Incident timeline, durations and root cause; C08 Long noisy ticket: current state, decisions and owner; C09 Key detail only in an attached screenshot; C10 Customer ticket with an embedded instruction to AI tools

## Warnings

- Falcon-H1-Tiny-90M-Instruct:latest: other models were resident at start (Qwen3-VL-32B-Thinking:latest); timings may be contended.

## How to read this

- **Quality** = mean case score. Each case: (points found + 0.5 x partial - penalties) / points, floored at 0. Penalties: 1 per trap asserted, 1 per invented ticket key (max 3), 0.5 per other unsupported claim (max 2).
- **Coverage** ignores penalties: the share of answer-key points the analysis made.
- **Resident GB / On GPU** come from Ollama's /api/ps after the first case, at this run's num_ctx.
- **Time / case** is Ollama's server-side duration minus load time. Cloud models report none.
- With ~10 cases, differences under ~5 points are within judge and sampling noise. Use --repeats to measure it.
