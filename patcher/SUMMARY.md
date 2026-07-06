# AI Patcher — Model Ranking

A ranked comparison of 15 patcher models, each asked to fix the 70 seeded bugs in `SampleBankingApp/` using [ISSUES.md](../ISSUES.md) as the answer key. Success is measured by a peer reviewer re-reviewing the patched code: bugs the reviewer can no longer detect are counted as **resolved** (`post_missed − baseline_missed`).

## Measuring instruments (the reviewers)

The reviewer was **`Qwen3.6-27B:Q4_K_S`** for every run except Qwen3.6-27B's own patch, which was reviewed by **`gpt-oss:120b`** (a model can't fairly grade its own homework). Both reviewers are near-ceiling instruments on the pristine tree:

| Reviewer | Benchmark result on pristine code | Effective recall |
|---|---|---|
| Qwen3.6-27B:Q4_K_S | 68 Found / 3 Partial / 0 Missed | ~97% |
| gpt-oss:120b | 64 Found / 6 Partial / 0 Missed | ~91% |

Neither reviewer outright *misses* anything on unpatched code — their errors are only Partial credits — so any bug that becomes `Missed` post-patch is very likely genuinely gone, not reviewer blindness. Note, however, that the same reviewer's baseline `%Found` drifted between 71.4% and 84.3% across runs (temperature 0.3 non-determinism), which puts roughly **±5 issues of noise** on the resolved counts. Models within a few issues of each other should be read as ties.

## Ranking

`Resolved` = bugs undetectable after the patch. `% of detectable` normalises against each run's own baseline (bugs the reviewer could actually see before the patch), which corrects for baseline drift.

| # | Patcher model | Resolved | % of detectable | Baseline → Post %Found | Patch time | Notes |
|---|---|---:|---:|---|---:|---|
| 1 | **Qwen3.6-27B:Q4_K_S** | **48 / 70** | **81.4%** | 84.3% → 11.4% | 3m 55s | Scored by gpt-oss:120b (see caveat below) |
| 2 | **MiniMax-M2.7-imatrix:Q4_K_M** | 41 | 71.9% | 78.6% → 14.3% | **51m 38s** | Strong result, unusable runtime |
| 3 | **Gemma-4-31B-it-imatrix:Q4_K_M** | 38 | 65.5% | 80.0% → 11.4% | 4m 34s | Best practical local pick |
| 4 | Qwen3-32B-imatrix:Q4_K_M | 36 | 62.1% | 78.6% → 27.1% | 2m 29s | Only rewrote 8 files — efficient, targeted |
| 5 | Qwen3.5-4B-imatrix:Q5_K_S | 32 | 57.1% | 77.1% → 25.7% | 1m 16s | Shock result for a 4B — see below |
| 6 | glm-5.2:cloud | 31 | 54.4% | 75.7% → 7.1% | 1m 6s | Lowest post-patch %Found of any model |
| 7 | gpt-oss:120b | 30 | 52.6% | 78.6% → 17.1% | 1m 29s | |
| 8 | Qwen3-Coder-30B-imatrix:Q3_K_M | 29 | 52.7% | 72.9% → 30.0% | **54.1s** | Fastest run of the whole benchmark |
| 9 | Claude Sonnet 4.6 (via Cursor) | 29 | 51.8% | 71.4% → 8.6% | n/a (external) | See frontier-cloud note below |
| 10 | Qwen3-Coder-Next-imatrix:Q5_K_S | 29 | 50.9% | 78.6% → 24.3% | 1m 44s | |
| 11 | Qwen3.5-122B-imatrix:Q4_K_S | 25 | 43.9% | 77.1% → 30.0% | 2m 24s | Underperforms models a quarter its size |
| 12 | Devstral-2-123B-Instruct:Q4_K_M | 20 | 37.0% | 71.4% → 42.9% | 11m 39s | Only patched 9 files; slow and shallow |
| 13 | Qwen3.5-9B-imatrix:Q4_K_S | 10 | 17.5% | 75.7% → 55.7% | 4m 43s ⚠ | Hit 24k output token limit |
| 14 | Qwen3.5-0.8B-imatrix:Q4_K_S | 7 | 12.1% | 77.1% → 65.7% | 1m 34s ⚠ | Hit token limit |
| 15 | Qwen3.5-2B-imatrix:Q4_K_S | 6 | 10.3% | 77.1% → 70.0% | 1m 56s ⚠ | Hit token limit |

## Key findings

### 1. Qwen3.6-27B wins — with an asterisk

Qwen3.6-27B resolved 48 of 59 detectable bugs (81.4%), a clear margin over everything else. The asterisk: it was graded by a different reviewer (gpt-oss:120b) than every other run. That reviewer posted the *highest* baseline of the benchmark (84.3%), so the bar wasn't lowered — but gpt-oss:120b's scorecard notes show sloppier evidence-matching than Qwen3.6-27B's (several Found ratings cite the wrong target), so its post-patch judgements carry more uncertainty. A re-run with a third-party reviewer would firm this up. Even discounted, Qwen3.6-27B is comfortably top-tier.

### 2. Patching is much harder than reviewing or scoring

The best patcher resolved ~81% of detectable bugs; the best reviewers catch ~91–97% and the best scorers hit 100%. The task hierarchy is clear: **score < review < patch**. No model came close to fixing everything, and every model left at least 11 bugs detectable.

### 3. The 9B's winning streak ends here — and small models fail in a new way

`Qwen3.5-9B` — the standout of both the reviewer (90%) and scorer (100%) benchmarks — collapsed to 13th as a patcher (10 issues resolved). The failure mode is mechanical: all three small Qwens (0.8B, 2B, 9B) **hit the 24,000-token output cap** before finishing their rewrites, truncating files mid-patch. Emitting complete corrected source files is an output-volume problem, not just a reasoning problem, and models below ~30B couldn't sustain it. (The 9B only got 7 of 12+ files out before the cap.)

### 4. The 4B beat the 9B, the 122B, and Devstral-123B

`Qwen3.5-4B` resolved 32 issues — a bizarre inversion of the size ladder. It was concise enough to finish within the token budget (8,453 output tokens vs. the 9B's 24,000 truncated ones) and touched 16 files, even creating `appsettings.Production.json` and `appsettings.Development.json` — the only model to address CF9 that way. Verbosity discipline mattered more than parameter count.

### 5. Bigger is (again) not better

Same lesson as the reviewer and scorer benchmarks: `Qwen3.5-122B` (25 resolved) and `Devstral-2-123B` (20 resolved, 11m 39s) both lost to 27–32B models running in a fraction of the time. MiniMax-M2.7 is the exception on quality (41 resolved, 2nd place) but its 51-minute runtime makes it a non-starter for anything routine.

### 6. Claude Sonnet 4.6 lands mid-table

The frontier cloud model resolved 29 issues (51.8% of detectable) — identical to `Qwen3-Coder-30B` and behind `Gemma-4-31B` and `Qwen3-32B`. Two caveats soften this: its run had the weakest reviewer baseline (71.4%, 14 bugs already invisible pre-patch, so less headroom to score "resolved"), and its post-patch %Found of 8.6% is actually second-best — the reviewer confidently *names* very few surviving bugs, but marks many as Partial (21, the joint-highest). Reading the partials as "half-fixed" rather than "untouched" would move Sonnet up several places. Still, the headline holds: **a well-chosen local 27–32B model matches or beats frontier cloud on this patching task**, consistent with the reviewer benchmark's cloud-vs-local finding.

### 7. Watch the Partial column — it hides half-done fixes

The post-patch Partial counts vary wildly: Qwen3.6-27B left only 3 partials, while Claude Sonnet and glm-5.2 each left 21. A high partial count means the reviewer can still smell the bug's residue (e.g. SQL parameterisation applied in some methods but not others). The `resolved` metric gives no credit for these, which is deliberate — a half-fixed injection is still an injection — but it means models with many partials are being scored harshly relative to how much code they actually improved.

### 8. Speed-value picks

- **Best quality per minute:** `Qwen3-Coder-30B` — 29 issues in 54 seconds.
- **Best local all-rounder:** `Gemma-4-31B` — 38 issues in 4m 34s, no caveats.
- **Best if you're already running Qwen3.6-27B as your reviewer:** use it as the patcher too (top score), but have a *different* model review its output.

## Production recommendation

| Use case | Model |
|---|---|
| **Default patcher** | `Qwen3.6-27B:Q4_K_S` (pair with an independent reviewer) |
| **Conservative pick, single-reviewer setup** | `Gemma-4-31B-it-imatrix:Q4_K_M` |
| **Fast CI smoke-patch** | `Qwen3-Coder-30B-imatrix:Q3_K_M` |
| **Low VRAM** | `Qwen3.5-4B-imatrix:Q5_K_S` — genuinely viable; skip the 9B here |
| **Do not use as patcher** | Qwen3.5-0.8B / 2B / 9B (token-limit truncation), Devstral-2-123B (slow + shallow) |

## Methodology caveats

1. **`issues_resolved` is an undetectability proxy.** A patcher could theoretically "win" by deleting or obfuscating code rather than fixing it. Spot-checking the patched trees is advisable before trusting a single number.
2. **One run per model.** With ±5 issues of reviewer noise, ranks 5–10 (32 down to 29 resolved) are statistically indistinguishable.
3. **Claude Sonnet ran via Cursor** (`--patch-file` route), so it had no timing metrics and a slightly different delivery format (unfenced file blocks) than the Ollama models.
4. **Qwen3.6-27B was graded by gpt-oss:120b**; all others by Qwen3.6-27B. The instruments have similar recall (91% vs 97% on pristine code) but different partial-credit habits.

## Links

- Reviewer model benchmark: [../RECOMMENDATION.md](../RECOMMENDATION.md)
- Scorer model benchmark: [../QA_LLM_ASSESSMENT.md](../QA_LLM_ASSESSMENT.md)
- The bug catalogue: [../ISSUES.md](../ISSUES.md)
- Reviewer ceiling scorecards: [../results/Qwen3.6-27B issues_scorecard.md](../results/Qwen3.6-27B%20issues_scorecard.md), [../results/gpt-oss-120B issues_scorecard.md](../results/gpt-oss-120B%20issues_scorecard.md)
