# AI Code Review — Model Ranking

A ranked comparison of 18 reviewer models, each asked to find the 70 seeded bugs in `SampleBankingApp/` from [review_prompt.md](../review_prompt.md) alone, then graded against [ISSUES.md](../ISSUES.md) by an independent scorer.

Claude results are excluded — those runs predate the current harness and will be redone.

---

## Executive summary

**Two 27B models are the practical ceiling.** `Qwen3.6-27B` and `Qwen3.8-27B` both score **68 of 70 adjusted** at 14.5 GiB — matching or beating every cloud model, every 120B+ model, and a 228B model nine times their size. Nothing in the local fleet comes close to their quality-per-gigabyte.

**Size predicts almost nothing.** The 122B, 123B and 228B models land at 46, 49 and 62 respectively — all beaten by a 27B. Meanwhile a 4B scores 33, above a 22B (22) and a 32B's near-neighbours. Architecture, reasoning configuration, and Modelfile hygiene matter far more than parameter count.

**Reasoning is the single strongest predictor.** Every model in the top five either has thinking enabled or reasons natively. The two 27B leaders both run `think: medium`; the project's own measurement is that Qwen3.8-27B scores 71.4% with thinking off against ~96% with it on. A model that cannot reason, or is misconfigured so it doesn't, gives up roughly 25 points.

**Three results should not be trusted at face value.** `Kimi-k3` and `glm-5.2` both returned 70/70 with **zero Partial** — the credit-everything signature the harness explicitly warns about, and `glm-5.2` carries three confirmed mis-credits. `Qwen3.5-9B`'s 21 is an unexplained outlier — it scores below a 4B, and the obvious culprit (its system prompt) is ruled out because the two top-scoring models carry the identical one.

**For a 32 GB corporate laptop, the answer is a MoE.** `Qwen3-Coder-30B-A3B` gives 27B-class memory with ~3B active parameters per token — the only model in the fleet that combines a respectable score (50) with a footprint and CPU speed a laptop can actually sustain. Full analysis at the end.

---

## How to read these numbers

**All 18 runs are strictly comparable.** Every one used:

| | |
|---|---|
| Source under review | byte-identical `SampleBankingApp/` (verified across all eight run commits) |
| Review prompt | SHA `82bd5f768ca9` |
| Answer key | `ISSUES.md` SHA `4b57cc34a7bb` |
| Scorer | `Qwen3-Coder-30B-imatrix:Q3_K_M` at temperature 0.3 |
| Budgets | `num_ctx` 65,536 / `num_predict` 40,000 |
| Sampler | temperature 0.3; `top_p`/`top_k` from each model's own Modelfile |
| Grounding | `enforce` — ungrounded Found/Partial rows downgraded to Missed |
| Scorer attempts | 1 |

**Adjusted Found is the ranking column.** Raw `Found` is what the scorer reported; `Adjusted` subtracts rows the evidence spot-check proved were mis-credited — a row rated Found whose target string appears nowhere in the review. Where no adjustment is shown, the spot-check found no mis-credits.

**Treat differences under ~6 as ties.** Two byte-identical MiniMax runs returned 51 and 57 Found. The scorer runs at temperature 0.3 and is non-deterministic, so it is part of the measured variance, not a fixed instrument.

**`Grounding downgrades` is a quality signal in its own right.** A high count means the scorer wanted to credit rows the review didn't actually support — usually a review that gestures at a defect class without naming the site.

---

## Ranking

| # | Model | Adjusted | Raw F/P/M | Size | Downgrades | Time | Output | Notes |
|---|---|---:|---|---:|---:|---:|---:|---|
| ⚠ | `kimi-k3:cloud` | **70** | 70/0/0 | cloud | 0 | 4m 07s | 22,361 tok | **Zero Partial — see caveats** |
| 1 | **`Qwen3.6-27B:Q4_K_S`** | **68** | 69/0/1 | 14.5 GiB | 1 | 4m 39s | 10,320 tok | Best local model; `think: medium` |
| 1= | **`Qwen3.8-27B-imatrix:Q4_K_S`** | **68** | 69/0/1 | 14.5 GiB | 1 | **50m 16s** | 11,739 tok | Same score, 11× slower — see below |
| ⚠ | `glm-5.2:cloud` | 67 | 70/0/0 | cloud | 0 | 50.5s | 7,747 tok | **Zero Partial + 3 mis-credits** |
| 4 | `MiniMax-M2.7:Q3_K_S` | 62 | 65/0/5 | 91.9 GiB | 0 | 6m 08s | 5,512 tok | Needed a Modelfile repair to work at all |
| 5 | `Muse-Glimmer-30B-imatrix:Q4_K_S` | 60 | 61/8/1 | 15.0 GiB | 1 | 6m 58s | 12,023 tok | 44k chars of reasoning — the most of any model |
| 5= | `gpt-oss:120b` | 60 | 60/1/9 | 60.9 GiB | 9 | **32m 02s** | 40,000 ⚠ | Hit the output cap |
| 7 | `Qwen3-Coder-30B-imatrix:Q3_K_M` | 50 | 57/0/13 | 13.7 GiB | 12 | 6m 10s | 40,000 ⚠ | MoE (A3B); also the project's scorer |
| 8 | `Devstral-2-123B-Instruct-2512:Q4_K_M` | 49 | 52/0/18 | 69.8 GiB | 0 | 6m 41s | 1,841 tok | Terse — only 7,714 chars of answer |
| 9 | `Qwen3.5-122B-imatrix:Q4_K_S` | 46 | 47/0/23 | 64.9 GiB | 23 | 2m 47s | 6,795 tok | Ran with **no reasoning at all** |
| 10 | `Gemma-4-31B-it-imatrix:Q4_K_M` | 45 | 45/25/0 | 17.4 GiB | 0 | 4m 42s | 6,249 tok | Zero downgrades — everything it claimed held up |
| 11 | `Qwen3-Coder-Next-imatrix:Q5_K_S` | 42 | 44/21/5 | 51.2 GiB | 5 | 1m 16s | 4,255 tok | Non-thinking by design |
| 12 | `Qwen3-32B-imatrix:Q4_K_M` | 36 | 38/11/21 | 18.4 GiB | 21 | 1m 38s | 2,583 tok | Thinking disabled by a pasted template |
| 13 | `Qwen3.5-4B-imatrix:Q5_K_S` | 33 | 34/7/26 | **2.8 GiB** | 26 | 5m 11s | 40,000 ⚠ | Beats models 8× its size |
| 14 | `Codestral-22B-imatrix:Q4_K_S` | 22 | 24/39/7 | 11.8 GiB | 7 | 1m 20s | 2,977 tok | 39 Partials — finds classes, names no sites |
| 15 | `Qwen3.5-9B-imatrix:Q4_K_S` | 21 | 21/27/22 | 5.0 GiB | 19 | 1m 46s | 8,736 tok | **Outlier — scores below the 4B; unexplained** |
| 16 | `Qwen3.5-2B-imatrix:Q4_K_S` | 16 | 19/37/14 | 1.1 GiB | 14 | 32.5s | 6,517 tok | |
| 17 | `Qwen3.5-0.8B-imatrix:Q4_K_S` | 6 | 6/31/33 | **0.5 GiB** | 3 | **12.1s** | 3,901 tok | Fastest run; floor of the benchmark |

`⚠` in the Output column means the run hit `num_predict` (40,000) and was truncated.

---

## What actually separates them

**Reasoning, not size.** The top five all reason. `Qwen3.5-122B` — 65 GiB, 122B parameters — produced **zero reasoning characters** and scored 46, below a 27B and barely above a 31B. Its build shipped a Qwen3-Coder chat template that stripped the `thinking` capability entirely, so Ollama rejected `think` outright. `Qwen3-32B` (36) has the same defect. Between them that is roughly 85 GiB of hardware handicapped by a copy-pasted template.

**Naming sites, not classes.** The gap between a 60-scorer and a 22-scorer is rarely "didn't find the bug" — it is "found it and didn't say where". `Codestral-22B` produced 39 Partials: it identifies SQL injection, resource leaks and dead code as *categories* but doesn't name `SearchUsers`, `ExecuteNonQuery` or `ObfuscateAccount`. [review_prompt.md](../review_prompt.md) requires per-occurrence rows naming the method, and the scorer enforces it. Grounding downgrades measure the same failure from the other side.

**Verbosity is not quality.** `gpt-oss:120b` wrote 135,654 characters and scored 60 with 9 downgrades. `Qwen3.6-27B` wrote 24,254 and scored 68 with 1. `Devstral-2-123B` wrote 7,714 and scored 49. There is no monotonic relationship — the correlation is with *specificity*, not length.

**Three models ran away.** `Qwen3-Coder-30B` (182,822 chars), `Qwen3.5-4B` (150,833) and `gpt-oss:120b` (135,654) all hit the 40,000-token cap and were truncated mid-review. Their scores are floors, not measurements. Qwen3-Coder-30B in particular produced seven mis-credits, consistent with a review that padded rather than stopped.

**Speed varies by 100×, and not with size.** `Qwen3.8-27B` took **50m 16s at 3.9 tok/s**; `Qwen3.6-27B` — same architecture, same 14.5 GiB, same score — took 4m 39s at 38.4 tok/s. A 10× throughput gap between identical-sized models on the same host is a deployment problem (KV cache spilling to CPU), not a model property. Worth investigating before reading anything into Qwen3.8's runtime.

**KV cache is the hidden cost.** At the benchmark's 65,536 context, the Qwen3.x 27B models allocate **16 GiB of KV cache** — more than their 14.5 GiB of weights. Architecture matters enormously here:

| Model | KV per token | KV @ 65,536 | KV @ 32,768 |
|---|---:|---:|---:|
| Qwen3.6 / 3.8-27B | 0.250 MiB | 16.0 GiB | 8.0 GiB |
| Codestral-22B | 0.219 MiB | 14.0 GiB | 7.0 GiB |
| Qwen3.5-4B / 9B | 0.125 MiB | 8.0 GiB | 4.0 GiB |
| Qwen3-Coder-30B | 0.094 MiB | 6.0 GiB | 3.0 GiB |
| Muse-Glimmer-30B | 0.051 MiB | 3.3 GiB | 1.6 GiB |
| Qwen3.5-2B | 0.047 MiB | 3.0 GiB | 1.5 GiB |

`Muse-Glimmer-30B` uses **five times less** KV than a Qwen 27B for the same context. `OLLAMA_KV_CACHE_TYPE=q8_0` roughly halves all of these.

---

## Recommendation: 32 GB corporate laptop

### The budget

32 GB total is not 32 GB available. Windows, Chrome with a working set of tabs, Teams and Outlook realistically hold **10–14 GiB**, leaving **18–22 GiB**. Once the OS starts paging, throughput collapses — so the target is a model whose weights *plus* KV cache fit in roughly **16 GiB**, leaving genuine headroom.

### The real constraint is speed, not memory

Most corporate laptops have integrated graphics, so inference is CPU-bound and limited by memory bandwidth. A dense 27B at Q4 moves ~14.5 GiB of weights per token. **Estimated** CPU throughput (extrapolated from active-parameter counts and typical DDR5 bandwidth — all benchmark runs above were on the GPU server, so these are not measured):

| Class | Active params/token | Est. CPU speed | Time for a ~10k-token review |
|---|---:|---:|---:|
| Dense 27–31B | 27B+ | ~1.5–3 tok/s | **1–2 hours** |
| Dense 9B | 9B | ~4–7 tok/s | ~25–40 min |
| **MoE 30B-A3B** | **~3B** | **~8–15 tok/s** | **~12–20 min** |
| Dense 4B | 4B | ~10–15 tok/s | ~12–17 min |
| Dense 2B | 2B | ~25–35 tok/s | ~5–7 min |

This is why the top-ranked models are the wrong answer for a laptop: `Qwen3.6-27B` at 65k context needs **30.5 GiB** (14.5 weights + 16.0 KV) — it does not fit — and even at 32k context (22.5 GiB) it would take one to two hours per review.

### Footprint at 32,768 context

| Model | Weights | KV | Total | Fits in ~16 GiB? | Adjusted score |
|---|---:|---:|---:|---|---:|
| `Qwen3.5-0.8B` | 0.5 | 1.5 | **2.0 GiB** | yes, trivially | 6 |
| `Qwen3.5-2B` | 1.1 | 1.5 | **2.6 GiB** | yes, trivially | 16 |
| `Qwen3.5-4B` | 2.8 | 4.0 | **6.8 GiB** | yes | 33 |
| `Qwen3.5-9B` | 5.0 | 4.0 | **9.0 GiB** | yes | 21 ⚠ |
| `Muse-Glimmer-30B` | 15.0 | 1.6 | **16.6 GiB** | marginal | 60 |
| `Qwen3-Coder-30B` | 13.7 | 3.0 | **16.7 GiB** | marginal | 50 |
| `Codestral-22B` | 11.8 | 7.0 | 18.8 GiB | no | 22 |
| `Qwen3-32B` | 18.4 | ~8 | ~26 GiB | no | 36 |
| `Qwen3.6/3.8-27B` | 14.5 | 8.0 | 22.5 GiB | no | 68 |

### The picks

**1 — Primary: `Qwen3-Coder-30B-imatrix:Q3_K_M` (13.7 GiB)**

The only model that is simultaneously respectable (50 adjusted), memory-feasible (16.7 GiB at 32k), and *fast on a CPU*. It is a 30B-A3B mixture-of-experts: 128 experts, 8 active, so roughly **3B parameters are touched per token** while all 30B sit in RAM. That gives it 4–8× the CPU throughput of a dense model of the same footprint. Its KV cache is also small (3.0 GiB at 32k).

Two caveats. It ran away to the 40,000-token cap and produced seven mis-credits, so cap `num_predict` around 16,000 and expect a tighter review. And it is currently the project's scorer — running it as reviewer *and* grader in the same pipeline means it marks its own homework.

**2 — If quality matters more than latency: `Muse-Glimmer-30B-imatrix:Q4_K_S` (15.0 GiB)**

Scores **60** — the highest of anything that fits — and has by far the most efficient KV cache in the fleet (1.6 GiB at 32k, 3.3 GiB even at 65k), so it can run full context where a Qwen 27B cannot. The catch is that it appears to be dense, so expect **1.5–3 tok/s on a CPU** and an hour-plus per review. Viable overnight, or on a laptop with a discrete GPU of 16 GiB or more.

**3 — If you need it interactive: `Qwen3.5-4B-imatrix:Q5_K_S` (2.8 GiB)**

Scores **33** — above Codestral-22B (22) and within reach of Qwen3-32B (36) — from a 2.8 GiB file. Total footprint 6.8 GiB at 32k leaves the laptop entirely usable alongside it. Genuinely surprising value, and the right pick for a pre-commit hook or an editor integration where a two-hour review is not an option.

### What would change this recommendation

**The sampler defects were real, but they do not explain the spread.** `Qwen3.5-0.8B`, `-2B`, `-4B` and `-9B` were all built with `repeat_penalty 1.3` against a card specifying 1.0, `min_p 0.05` against 0.0, and `top_p` at the non-thinking value. Corrected Modelfiles for all four are in [modelfiles/](../modelfiles/), and re-running the tier is still worthwhile.

**The system prompt is a controlled constant, not a defect.** All six Qwen3.x models on the server carry the identical block:

> *"You are an expert code reviewer. /no_think Be concise and skip chain-of-thought; produce only the final review."*

That includes `Qwen3.6-27B` and `Qwen3.8-27B`, which scored 68. Since the prompt is the same for the 68-scorers and the 21-scorer, it cannot be what separates them — and an earlier draft of this document wrongly blamed it for the 9B's result. Two details are worth keeping in mind: the `/no_think` half is inert on Qwen3.5 (the card states the soft switches are unsupported), and every one of these runs sent `think: medium`, which reinstates reasoning regardless.

**`Qwen3.5-9B` remains a genuine anomaly.** At 21 it sits *below* the 2.8 GiB 4B (33), which is backwards. Its output shape is the distinctive part: only 8,582 chars of answer against 26,827 chars of reasoning, and 42 of 90 table rows beginning literally `| Method ` with no symbol named — so 19 rows were downgraded for lack of evidence. It thought hard and then wrote almost nothing usable. Whether that reproduces is unknown; it is a single run.

**Re-run the laptop tier before committing to a choice.** The 9B is the one to watch — a 5.0 GiB model landing in the 40s would displace `Qwen3-Coder-30B` as the primary recommendation outright.

---

## Caveats

**The two 100% scores are not credible as reported.** `kimi-k3` and `glm-5.2` each returned 70 Found, 0 Partial, 0 Missed. A zero-Partial sheet across 70 rows is the scorer's credit-everything mode, which the harness warns about at [ai_code_review.yml:579-586](../.github/workflows/ai_code_review.yml#L579-L586) — and it could not re-roll, because `AI_ASSISTANT_SCORER_MAX_ATTEMPTS` defaults to 1. `glm-5.2` has three confirmed mis-credits (`R3`, `N3`, `D5`), which is direct evidence the sheet is inflated; `kimi-k3` has none detected, but the watchlist covers only 16 of 70 rows. Both should be re-scored with `AI_ASSISTANT_SCORER_MAX_ATTEMPTS=2` before being treated as a genuine ceiling.

**The scorer is inside the measurement.** Every score here is `Qwen3-Coder-30B`'s opinion, at temperature 0.3. Setting `AI_ASSISTANT_SCORER_TEMPERATURE=0` would make scoring deterministic and remove a large share of the ±6 variance — at the cost of re-baselining every number in this table.

**One model grades itself.** `Qwen3-Coder-30B` appears both as rank 7 and as the scorer for all 18 runs, its own included.

**Runs sit on different commits but the same tree.** The eight commits involved differ only in results files; `SampleBankingApp/` is byte-identical across all of them, and the prompt and answer-key SHAs match throughout.

**System prompts are uncontrolled across families.** Within the Qwen3.x family the prompt is identical, so those six are mutually comparable. Across families it is not: `Gemma-4-31B` has none at all, `Muse-Glimmer-30B` carries *"Reasoning strength: high"*, `Qwen3-Coder-30B` an expert-engineer persona, and `Qwen3.5-122B` a *"provide detailed answers"* persona. None of this is recorded in the scorecards — a Modelfile `SYSTEM` appears nowhere in the run configuration appendix — so it is an invisible variable in every cross-family comparison here. Standardising it (to none, or to one shared line) would tighten the benchmark, at the cost of rebuilding every model and re-baselining every score.

**Single runs throughout.** Every row is `n=1`. Given the ±6 spread measured between identical MiniMax runs, adjacent rows should not be read as ordered.
