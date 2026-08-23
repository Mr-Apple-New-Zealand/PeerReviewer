# AI Peer Reviewer — Model Ranking

A ranked comparison of **19 review models**, each asked to review the deliberately-broken `SampleBankingApp/` .NET project and report what it found. Every review was then scored against [ISSUES.md](../ISSUES.md) — a fixed catalogue of **70 seeded bugs** — by an independent scorer model.

Each model was given the same 10-category prompt and asked to check for:

1. Security vulnerabilities
2. Logic errors
3. Error handling
4. Resource leaks
5. Null reference risks
6. Dead code
7. Magic strings and numbers
8. Anti-patterns and code quality
9. Configuration issues
10. Missing unit tests

## TL;DR

- **Best local model:** `Qwen3.6-27B:Q4_K_S` — 95.8%, ~16–20 GB VRAM. Its successor `Qwen3.8-27B` matches it at 95.7%, but only once reasoning is enabled and the token budget raised (finding 7).
- **Best value:** `Qwen3.5-9B-imatrix:Q4_K_S` — 90.0% at ~5.5 GB. The standout finding of the benchmark.
- **Best accuracy-per-second (if you have the VRAM):** `gpt-oss:120b` — 91.4% in 1m 23s.
- **Fastest usable review:** `Qwen3-Coder-Next-imatrix:Q5_K_S` — 80.0% in 47.7s.
- **Cloud is not meaningfully ahead.** Claude Opus 4.7 scored 91.4% — *behind* a 27B model running locally.
- **The harness has since been revised.** Results measured under it live in [Second-generation harness](#second-generation-harness-august-2026) and are **not comparable** with the ranking below. `Muse-Glimmer-30B` is the first model measured there: **82.9%**.

## How to read the score

`Found` means the review named the same specific file, method, or symbol as the reference answer. `Partial` means it flagged the surrounding code but stopped short of the specific target. `Missed` means it never came near it. Only `Found` counts toward the headline percentage, so the scoring is deliberately strict — a model that says "there are SQL injection risks" without naming `AuthService.Login` earns a Partial, not a Found.

## Ranking

> All 19 rows below were measured with the **original** prompt and scorer. Runs produced after August 2026 use a revised harness and belong in [their own table](#second-generation-harness-august-2026) — the two sets of numbers cannot be placed side by side.

| # | Model | Found % | Found / Partial / Missed | Review time | Speed | VRAM | Verdict |
|---|---|---:|---|---:|---:|---|---|
| 1 | **kimi-k3:cloud** | 97.1% | 68 / 2 / 0 | n/a | n/a | cloud | Highest raw score, and the evidence quality holds up — every Found cites a file and line. Cloud-only, so your source leaves the building. |
| 2 | **Qwen3.6-27B:Q4_K_S** | 95.8%\* | 68 / 3 / 0 | 3m 30s | 33 t/s | ~16–20 GB | **Best local model in the test.** Slower than the sub-minute models but the most accurate thing you can run on a single 24 GB card. |
| 3 | **Qwen3.8-27B-imatrix:Q4_K_S** | 95.7% | 67 / 3 / 0 | ~3m† | 38 t/s | ~16–20 GB | Only reaches this with **reasoning enabled** — see finding 7. Three Founds (D3, D9, D10) are mis-credited dead-code rows; discounting them gives **91.4%**. |
| 3= | ⚠️ Qwen2.5-7B-1M:Q4_K_M | 95.7% | 67 / 3 / 0 | 1m 53s | 12 t/s | ~5 GB | **Score is not real — see the scorer-inflation note below.** Do not pick this on the headline number. |
| 5 | **gpt-oss:120b** | 91.4% | 64 / 6 / 0 | 1m 23s | 98 t/s | ~80 GB | Best accuracy-per-second if the VRAM is available. Fastest top-tier result by a wide margin. |
| 5= | Claude Opus 4.7 | 91.4% | 64 / 4 / 2 | n/a | n/a | cloud | Frontier cloud baseline. Ties gpt-oss-120B, loses to Qwen3.6-27B. |
| 5= | Qwen3.5-122B-imatrix:Q4_K_S | 91.4% | 64 / 6 / 0 | 7m 10s ⚠ | 58 t/s | ~80 GB | Same accuracy as gpt-oss-120B at 5× the latency and the same VRAM. Hit the 24,000-token output cap. No reason to pick this over gpt-oss-120B. |
| 8 | **Qwen3.5-9B-imatrix:Q4_K_S** | 90.0% | 63 / 7 / 0 | 1m 45s | 93 t/s | ~5.5 GB | **Best-value model in the benchmark.** 90% from a 9B is the headline finding — production default for anything cost- or VRAM-sensitive. |
| 8= | MiniMax-M2.7:Q3_K_S | 90.0% | 63 / 7 / 0 | 3m 19s | 9 t/s | varies | High accuracy, painfully slow output, and the loosest evidence matching of any top-tier model (6 issues credited to one generic quote). |
| 10 | glm-5.2:cloud | 85.7% | 60 / 5 / 5 | 27.5s | n/a | cloud | Fastest review of the whole benchmark. The only model with outright misses at this tier — all 5 are dead-code and refactoring items it simply doesn't look for. |
| 11 | Qwen3-Coder-Next-imatrix:Q5_K_S | 80.0% | 56 / 13 / 1 | 47.7s | 86 t/s | ~16 GB | Fastest top-half model. Sub-minute at 80% — the sweet spot for a pre-commit or pre-push hook. |
| 11= | Devstral-2-123B-Instruct:Q4_K_M | 80.0% | 56 / 14 / 0 | 4m 29s | 9 t/s | ~80 GB | Same accuracy as Coder-Next at 5.6× the time and 5× the VRAM. Hard to justify. |
| 13 | Qwen3-32B-imatrix:Q4_K_M | 64.3% | 45 / 25 / 0 | 1m 56s | 30 t/s | ~20 GB | Middle of the pack. Nothing it does is better done by Qwen3.6-27B in the same VRAM budget. |
| 14 | Gemma-4-31B-it-imatrix:Q4_K_M | 62.9% | 44 / 26 / 0 | 2m 15s | 30 t/s | ~20 GB | Solid mid-tier option, but 26 Partials means it sees the problems without pinning them down. |
| 15 | ⚠️ Qwen3.5-0.8B-imatrix:Q4_K_S | 54.3% | 38 / 32 / 0 | 1m 33s ⚠ | 307 t/s | ~0.6 GB | **Rubbish.** The review claims the controllers have "no obvious security issues" — catastrophically wrong. Hit the token cap with repeated lines; the score is largely accidental. Useful only as a "this is what too small looks like" baseline. |
| 16 | Qwen3-Coder-30B-imatrix:Q3_K_M | 48.6% | 34 / 35 / 1 | 25.6s | 137 t/s | ~16 GB | Fastest reliable local model, but the strict scorer punishes its terse summary style — 35 Partials. Better than the number suggests if you like concise reviews. |
| 17 | Qwen3.5-4B-imatrix:Q5_K_S | 42.9% | 30 / 40 / 0 | 28.4s | 127 t/s | ~3 GB | The smallest model that still produces a coherent, structured review. Acceptable floor for resource-constrained setups. |
| 18 | Codestral-22B-imatrix:Q4_K_S | 28.6% | 20 / 50 / 0 | 57.4s | 44 t/s | ~14 GB | Significantly underperforms its weight class — a 4B beats it on Found-rate at a fifth of the size. Avoid. |
| 19 | ⚠️ Qwen3.5-2B-imatrix:Q4_K_S | 22.9% | 16 / 53 / 1 | 1m 54s ⚠ | 235 t/s | ~1.5 GB | **Rubbish.** Even with a loop-breaking Modelfile template it can't sustain a 10-section structured review. Do not deploy. |

\* Qwen3.6-27B was scored against 71 rows rather than 70 (a duplicated entry in that run's scorecard). The difference is within a rounding error of the others and does not change its rank.

† `metrics.md` was not captured for the Qwen3.8-27B run that produced this score. Comparable runs of the same model and settings measured 3m 8s at 38.2 tok/s.

⚠ = hit the 24,000-token output cap, or the score needs a caveat (see below).

## Key findings

### 1. Two scores in this table are not what they look like

The scorer (`Qwen3-Coder-30B-imatrix:Q3_K_M`) awards a `Found` when it believes the review named the right target. Counting how many *distinct* pieces of evidence it quoted across all the Founds exposes where it was too generous:

| Model | Found | Distinct evidence quotes | Worst single quote reused |
|---|---:|---:|---:|
| Claude Opus 4.7 | 64 | 64 | 1× |
| Qwen3.5-9B | 63 | 62 | 2× |
| kimi-k3 | 68 | 61 | 2× |
| gpt-oss-120B | 64 | 56 | 3× |
| Qwen3.6-27B | 68 | 54 | 3× |
| Qwen3.8-27B | 67 | 55 | 3× |
| **MiniMax-M2.7** | **63** | **38** | **6×** |
| **Qwen2.5-7B-1M** | **67** | **16** | **11×** |

`Qwen2.5-7B-1M` produced a **897-token** review — about 13 tokens per issue it was credited with. The scorer stretched sixteen generic observations across 67 issues: "Hardcoded credentials for SMTP in `appsettings.json`" was accepted as evidence for the MD5 hashing bug *and* the admin backdoor, and "Missing boundary condition check for `pageSize`" was accepted for both broken-access-control findings. Its true score is somewhere near the 4B's. **Treat rank 3 as void.** MiniMax-M2.7's 90% is milder but softened by the same effect.

Everything else in the top tier holds up: `Qwen3.6-27B`, `gpt-oss-120B`, `Qwen3.5-9B` and `kimi-k3` all cite specific files and line numbers for nearly every Found.

### 2. A 9B model gets 90%

`Qwen3.5-9B-imatrix:Q4_K_S` found 63 of 70 seeded bugs with essentially clean evidence (62 distinct quotes for 63 Founds) in 1m 45s, from a ~5.5 GB footprint. It ties MiniMax-M2.7 — a model many times its size — and sits 1.4 points behind both a 120B and a frontier cloud model. This is the single most useful result in the benchmark: **the quality/size curve flattens hard around 9B for this task.**

### 3. Bigger is not better

`Qwen3.5-122B` (91.4%, 7m 10s, ~80 GB) is beaten on every axis by `gpt-oss-120B` at the same VRAM, and on accuracy by a 27B at a quarter of the memory. `Devstral-2-123B` (80.0%) ties a 30B-class model while taking 5.6× as long. Below the top tier, `Codestral-22B` (28.6%) is outscored by a 4B. Parameter count predicts almost nothing here — architecture, quantisation quality, and output discipline predict a lot.

### 4. Local matches cloud

Claude Opus 4.7 returned 91.4% — a clean, well-evidenced review, but *behind* `Qwen3.6-27B`'s 95.8% and level with `gpt-oss-120B`. Its two outright misses were the "split `GenerateJwtToken` into helpers" refactor and the dead `ToTitleCase` helper; its partials were near-misses where it flagged the surrounding code without naming the exact symbol. `glm-5.2:cloud` came in below both at 85.7%.

On a focused review against a known rubric, **a properly configured local model is genuinely competitive with the best hosted models — and your source code never leaves the building.**

### 5. The output token cap is the biggest configuration lever

Three runs hit the 24,000-token ceiling (`Qwen3.5-122B`, `0.8B`, `2B`). For the 122B this only truncated the tail of section 8 and the score stands. For the 0.8B and 2B, **the truncation *is* the content** — the cap filled with repeated lines, and their scores are artefacts of that repetition rather than real findings. Earlier in the project, `gpt-oss-120B` and `Qwen3-Coder-30B` were both hitting a lower cap that cut their reviews mid-response; raising it changed their results completely. Check this before you blame the model.

### 6. Partials are where the mid-tier lives

`Gemma-4-31B` (26 Partials), `Qwen3-Coder-30B` (35), `Qwen3.5-4B` (40) and `Codestral-22B` (50) all *see* far more than their Found-rate suggests — they describe the right area of code without naming the specific method the answer key wants. If you read the reviews yourself rather than gating a pipeline on an exact-match score, these models are more useful than their ranking implies. If you're automating, the strict score is the number that matters.

### 7. Qwen3.8-27B needs reasoning enabled — and it costs 16,000 tokens of budget to get it

`Qwen3.8-27B-imatrix:Q4_K_S` will not produce a review at all under the benchmark's standard configuration. It consumes the **entire 24,000-token output budget inside its reasoning block** and emits zero answer tokens — `done_reason: length`, `eval_count: 24000`, `content: 0 chars`, `thinking: 99,888 chars`. Ollama ≥ 0.9 returns reasoning in a separate `message.thinking` field, so the harness sees an empty response and fails.

It needs roughly **30,000 tokens of reasoning before it writes a word**. Making that possible took two changes, not one:

| Setting | Benchmark default | Required for Qwen3.8-27B |
|---|---:|---:|
| `num_predict` | 24,000 | **40,000** |
| `num_ctx` | 49,152 | **65,536** |

The context bump is the non-obvious half. This harness computes the source-listing budget as `num_ctx − num_predict`, so raising `num_predict` alone would have cut the code sent to the model from 27,534 to 16,237 chars — silently reviewing 60% of the codebase.

**What it scores at each reasoning level** (same prompt, same model, same day):

| `think` | Output tokens | Time | Raw Found % |
|---|---:|---:|---:|
| `false` | 3,771 | 2m 1s | 71.4% |
| `low` | 7,291 | 3m 22s | 95.7% |
| `medium` | 6,827 | 3m 8s | 98.6% |
| `true` | ~29,000 | ~12m | 100% |

Reasoning is the difference between a mid-table model and a top-tier one — 71.4% to ~96% — but `low` and `medium` are indistinguishable in output volume, so the gap between those two runs is scorer variance, not the effort level doing work. Full reasoning costs 4× the wall clock for gains that stayed inside that same variance.

**Read the headline numbers with care.** Across five runs this model scored 95.7%, 98.6%, 100%, 100% and 95.7% — while the *reviews* were of similar quality throughout. An evidence audit over each scorecard explains the spread: the scorer repeatedly credits `Found` on quotes belonging to a different row. In the run recorded in the table above, three dead-code rows are mis-credited — D3 (`TableExists`) to a quote about `ExecuteQueryWithParams`, and D9 (`ObfuscateAccount`) and D10 (`ToTitleCase`) both to the *same* quote about `JoinWithSeparator`. None of those three symbols appears anywhere in the review. Discounting them gives **64 Found / 3 Partial / 3 Missed = 91.4%**.

**Where that leaves it:** with reasoning on, Qwen3.8-27B is genuinely competitive with `Qwen3.6-27B` — 95.7% vs 95.8% raw, in comparable time, at the same size and VRAM. It is not clearly better, and it is materially more fragile: the token budget must be raised, and the model intermittently ends its turn after reasoning without writing anything at all (`done_reason: stop`, empty content, budget untouched), which needs a retry to survive. `Qwen3.6-27B:Q4_K_S` remains the safer default; Qwen3.8-27B is the pick if you want its ceiling and can tolerate the configuration.

## Second-generation harness (August 2026)

Every row in the ranking above was produced by the original prompt and scorer. Both have since
been substantially revised, and **scores from the two harnesses are not interchangeable** — the
changes push in both directions, so the difference is not a constant you can subtract.

| Change | Direction |
|---|---|
| Dead-code category now specifies a *procedure* — enumerate every method defined in the source, then search for callers — instead of asking the model to notice unused code | **Raises.** D1–D11 were the largest systematic gap in the original results |
| Refactoring opportunities added to the prompt (the original 10 categories never asked for them, so R1/R3 were unreachable) | **Raises** |
| Source listing carries line numbers (`nl -ba`) | **Raises** slightly — line citations used to be guesses |
| "Compact table, one sentence maximum" replaced by per-*cell* brevity plus an explicit instruction not to stop a section early | **Raises.** Models were satisficing at ~7 rows per category while leaving 70% of the output budget unused |
| Scorer must quote the review; Notes that cannot be matched against review text are downgraded to `Missed` automatically | **Lowers.** Seven rows were downgraded in the run below |
| Curated spot-check flags any `Found` whose target string appears nowhere in the review, and a second check flags Notes that concede the gap in their own wording | **Lowers** |
| `ISSUES.md` D5 corrected — `BuildHtmlTemplate` is reachable from `SendWelcomeEmailHtml`, so it is dead *transitively*, not uninvoked | Neutral |
| Token budgets fixed at 65,536 / 40,000 for every model | Removes the Qwen3.8-27B exception in finding 7 |

Every scorecard now ends with a **Run Configuration** appendix recording the review-prompt and
`ISSUES.md` SHA-256 alongside the sampler and budgets, so runs from different harness generations
can be told apart without guesswork.

### Results

| Model | Reported | Adjusted | Found / Partial / Missed | Review time | Speed | VRAM |
|---|---:|---:|---|---:|---:|---|
| **Muse-Glimmer-30B-imatrix:Q4_K_S** | 84.3% | **82.9%** | 59 / 4 / 7 | 3m 34s | 39.9 t/s | ~15 GB |

Prompt SHA `941b3fe4530e`, `ISSUES.md` SHA `69240e52f3d9`, temperature 0.3, sampler from the
model's own Modelfile, reasoning at the Modelfile default.

**Muse-Glimmer-30B.** A 30B multimodal model whose card claims 76% on SWE-Bench Verified. On this
task it lands mid-tier. The adjusted figure removes one mis-credit — C7 was rated `Found` on a
quote that never mentions `RecordTransaction`. Seven further Notes could not be matched to any
sentence in the review and were downgraded automatically, which makes this **the first run in the
project to produce genuine `Missed` ratings** rather than a wall of Partials concealing them.

Its consistent blind spots across eight runs were `E7` (no rate limiting on login), `N3`
(`SmtpPort`), `CF9` (missing `appsettings.Production.json`), `D5` (`BuildHtmlTemplate`) and `R3`
(splitting `GenerateJwtToken`) — absence-shaped problems, where the answer is that something
*isn't* there.

Two configuration experiments came back negative and are worth recording so they are not repeated:

- **The model card's recommended `temperature = 1.0`** scored 53 against 54 at the benchmark's 0.3
  — inside the run-to-run spread, so no evidence either way. Keep 0.3.
- **`Reasoning strength: xhigh`** produced 15% more reasoning, a *shorter* answer, and 13% more wall
  clock for no score movement. Two runs at the Modelfile default bracketed the xhigh run's reasoning
  volume (56k and 76k characters against its 65k), so the level knob is swamped by ordinary variance.

### On measurement noise

Repeat runs made the harness's own precision measurable, and it is worse than the original
methodology assumed:

- **Review side, ±4 issues.** Two runs at byte-identical configuration scored 54 and 50.
- **Reasoning volume, ±35%.** The same configuration produced between 56,000 and 76,000 characters
  of reasoning, and wall clock varied from 3m 34s to 8m 4s as a result.
- **Scorer side, one-directional.** On two occasions the scorer returned a full sheet of `Found`
  with zero `Partial`; both contained mis-attributions verifiable by grep. It inflates, never
  deflates, so **every score in this document is an upper bound.**

Treat any single headline number as ±6 issues. Differences smaller than that — which includes most
of the top of the ranking above — are not measuring anything.

## Recommended locally-hosted models

Everything below runs entirely on your own hardware. Cloud entries (kimi-k3, glm-5.2, Claude Opus 4.7) are excluded — they're benchmarks, not recommendations.

### If you have an AI server

| VRAM available | Pick | Found % | Review time | Why |
|---|---|---:|---:|---|
| **~80 GB** | `gpt-oss:120b` | 91.4% | 1m 23s | Best accuracy-per-second at this tier. Skip Qwen3.5-122B and Devstral-2-123B — same memory, worse results. |
| **~24 GB (single card)** | `Qwen3.6-27B:Q4_K_S` | **95.8%** | 3m 30s | Highest local accuracy, and it works at the default settings. The safe default. |
| **~24 GB, if you'll tune it** | `Qwen3.8-27B-imatrix:Q4_K_S` | 95.7% | ~3m | Statistically level with Qwen3.6-27B, but only with reasoning enabled and `num_predict`/`num_ctx` raised — and it needs retry handling. See finding 7. |
| **~16 GB, latency-sensitive** | `Qwen3-Coder-Next-imatrix:Q5_K_S` | 80.0% | 47.7s | Sub-minute reviews. Right choice for a hook that runs on every commit. |
| **~8 GB** | `Qwen3.5-9B-imatrix:Q4_K_S` | 90.0% | 1m 45s | 90% from 5.5 GB. Best value in the entire test. |

### If you're on a corporate laptop

A laptop without a discrete GPU runs inference on CPU using system RAM — **5–20× slower** than the GPU numbers above. And after Outlook, Chrome and Teams, a 32 GB machine realistically has 4–8 GB free. Every model ranked in the top tier except the 9B is too large to fit; the smallest of them (`Gemma-4-31B`) needs ~20 GB.

| Model | RAM (Q4–Q5) | Found % | GPU time | Est. CPU time | Recommendation |
|---|---|---:|---:|---|---|
| `Qwen3.5-9B-imatrix:Q4_K_S` | ~5.5 GB | 90.0% | 1m 45s | 8–20 min | **Top pick** if 8 GB is genuinely free. Real review quality. |
| `Qwen3.5-4B-imatrix:Q5_K_S` | ~3 GB | 42.9% | 28s | 1–3 min | Pragmatic fallback when the 9B is too slow or only 4–5 GB is free. |
| ⚠️ `Qwen3.5-2B-imatrix:Q4_K_S` | ~1.5 GB | 22.9% | 1m 54s | 30–60s | Loops to the 24K cap producing junk. Don't deploy. |
| ⚠️ `Qwen3.5-0.8B-imatrix:Q4_K_S` | ~0.6 GB | 54.3% | 1m 33s | 30–45s | Score is accidental; the review misses every planted security bug. Don't deploy. |

**Practical laptop setup — run both:**

- **Pre-commit hook → `Qwen3.5-4B`** for fast catch-the-obvious-stuff feedback (1–3 min).
- **Pre-push hook → `Qwen3.5-9B`** for a thorough check before the code leaves the machine.

The 9B's 90% as a pre-push gate is genuinely useful; the 4B's 42.9% as a pre-commit warning is better than nothing, provided a stronger model is running server-side as a backstop.

### What to avoid

- **`Qwen3.5-2B` and `Qwen3.5-0.8B`** — both loop to the token cap; their scores are artefacts.
- **`Qwen2.5-7B-1M`** — its 95.7% is a scoring artefact, not review quality. The 9B is the same size class and actually earns its number.
- **`Codestral-22B`** — 28.6% for 14 GB. A 3 GB model beats it.
- **Lower-quant versions of bigger models** (e.g. `Qwen3-Coder-30B` at Q2_K to squeeze it into 8 GB) — quality drops sharply below Q3, and you'd get worse output than the native-quant 9B.
- **Anything 14B+ on laptop CPU** — even if it fits via aggressive quantisation, expect 30–90 minutes per review.

## A note on model selection

All models tested were carefully selected quantised builds, including imatrix variants (e.g. `Qwen3.6-27B-imatrix:Q3_K_M`, `Q3_K_S`). Quantisation shrinks a model's memory footprint by compressing its weights — think lossless vs. lossy audio. The **imatrix** variant applies importance sampling on top, preserving accuracy in the parts of the model that matter most for code analysis. The imatrix files here were built from 4000+ chunk analyses over a coding-specific data collection. Final selections balanced speed, RAM, and accuracy.

## Methodology

Every model received the identical 10-category review prompt against the `SampleBankingApp/` source tree. A separate scorer model — `Qwen3-Coder-30B-imatrix:Q3_K_M` for every run — then compared each review against the 70 known bugs in [ISSUES.md](../ISSUES.md), awarding a `Found` only when the review named the same specific file or function as the reference answer.

| Parameter | Value | Why |
|---|---|---|
| Context window | 49,152 tokens (**65,536** for Qwen3.8-27B) | Fits instructions, full source, and output in one pass. No model saw a truncated codebase. |
| Output token cap | 24,000 tokens (**40,000** for Qwen3.8-27B) | The single most important setting in the experiment — see findings 5 and 7. |
| Temperature | 0.3 (0.6 for small Qwen3.5 variants) | Near-deterministic enumeration, not creative prose. Raised for the small models to stop them looping. |
| Reasoning (`think`) | Model default — **`medium` for Qwen3.8-27B** | Qwen3.8-27B returns no content at all unless reasoning is both enabled and given room; see finding 7. |
| Truncation safety factor | 2.5 | Conservative chars-per-token estimate so the source is never clipped as the codebase grows. |

**Caveats.** One run per model, so small gaps are noise — treat anything inside ~2 issues as a tie. `Qwen3.8-27B` is the one row not measured under the common configuration: it cannot run at the default token budget at all, so its context and output cap were raised (see finding 7). The scorer is a single 30B model and, as findings 1 and 7 show, it can be fooled by vague reviews and will credit a `Found` using a quote that belongs to a different row; the evidence-uniqueness check and the per-row symbol audit are partial corrections, not fixes. Five repeat runs of one model spanned 95.7%–100% on review quality that barely changed, so **treat any single headline score as ±3 issues.** `kimi-k3` and `Claude Opus 4.7` were run outside the Ollama harness, so no timing or throughput metrics were captured for them. VRAM figures are typical footprints for the listed quantisation, not measured allocations.

## Links

- Patcher model benchmark (can these models *fix* what they find?): [../patcher/SUMMARY.md](../patcher/SUMMARY.md)
- The bug catalogue: [../ISSUES.md](../ISSUES.md)
- Project and example git hook: https://github.com/geoffmunn/PeerReviewer/
- Quantised models used: https://huggingface.co/geoffmunn/PeerReviewers/tree/main
- Imatrix files: https://huggingface.co/geoffmunn/iMatrix/tree/main
