# Ticket Analyst — Results

Which model to use for ticket analysis, and what has actually been measured.
[JIRA_BENCHMARK.md](JIRA_BENCHMARK.md) covers how the benchmark works; this file
records what it found.

**The comparison table is generated, not hand-written.** Run:

```
python3 scripts/jira_benchmark.py --compare jira_analyst_results --out jira_analyst_results
```

That writes `jira_analyst_results/summary.md` (the leaderboard: headline picks,
ranking, per-case scores, and a Runs table giving each row's provenance) and
`leaderboard.json`. It reads the committed run folders only, and needs no GPU
and no judge. Regenerate it after committing a run, and keep the notes below in
step with it.

---

## Current standing

Seventeen models have been measured on the full eighteen cases with the judge of
record. Everything earlier is superseded — see below.

| Model | Quant | Temp | Quality | Coverage | C01–C13 | C14–C18 | Traps hit | Invented | Unsup | GB |
|---|---|---|---|---|---|---|---|---|---|---|
| **claude-sonnet-5** ¹ | — | n/a | **88.4 (87–91)** | **90%** | **93.6** | **74.9** | 4/162 | 0 | **13** | — |
| Qwen3.8-27B-imatrix-vision ⁵ | Q4_K_S | 1.0 | 84.8 (82–87) | **90%** | 88.4 | **75.5** | 3/157 | 0 | 42 | 20.0 |
| **Muse-Glimmer-30B-imatrix** | Q4_K_S | 1.0 | **82.8 (82–84)** | **84%** | **89.3** | **65.9** | **1/162** | 0 | **13** | **16.7** |
| Gemma-4-31B-it-imatrix | Q4_K_M | 1.0 | 66.7 (65–69) | 68% | 75.3 | 44.2 | 3/162 | 0 | **11** | 22.7 |
| Qwen3-VL-32B-Instruct-imatrix | Q4_K_M | 0.3 | 62.5 (59–65) | **69%** | 72.5 | 36.4 | 8/162 | **5** | 39 | — ² |
| Qwen3-VL-32B-Thinking | Q5_K_M | 1.0 | 60.6 (60–61) | 66% | 72.5 | 29.8 | **1/162** | 0 | 51 | — ² |
| Qwen3-VL-8B-Thinking-imatrix | Q4_K_M | 1.0 | 52.3 (48–54) | 60% | 62.9 | 24.7 | 7/162 | 0 | 59 | 13.0 |
| Qwen3-VL-8B-Instruct-imatrix | Q3_K_M | 0.3 | 49.7 (48–52) | 63% | 57.9 | 28.4 | 19/162 | 1 | 67 | **9.4** |
| **Qwen3-VL-4B-Thinking-imatrix** | Q5_K_M | 1.0 | 51.9 (50–54) | 58% | 64.6 | 18.8 | 10/162 | 0 | 43 | 11.0 |
| Qwen2.5-VL-32B-Instruct | Q5_K_M | 0.3 | 49.2 (49–50) | 54% | 60.6 | 19.5 | 7/162 | 0 | 37 | 32.5 |
| **Qwen3-VL-4B-Instruct-imatrix** | Q4_K_M | 0.3 | 48.6 (48–50) | 59% | 58.6 | 22.6 | 13/162 | 2 | 57 | **7.9** |
| Qwen2.5-VL-72B-Instruct | Q4_K_S | 0.3 | 45.6 (45–47) | 48% | 58.7 | 11.7 | 8/162 | 0 | 15 | 56.3 |
| Qwen3-VL-2B-Thinking-imatrix ³ | Q5_K_S | 1.0 | 26.7 (25–29) | 45% | 36.0 | 2.4 | 27/149 | 3 | 117 | 8.1 |
| Qwen3-VL-2B-Instruct-imatrix | Q4_K_M | 0.3 | 25.3 (21–31) | 40% | 33.4 | 4.2 | 30/162 | 1 | 114 | 5.4 |
| Qwen2.5-VL-7B-Instruct-imatrix | Q4_K_S | 0.3 | 24.5 (23–25) | 31% | 33.4 | 1.3 | 17/162 | 0 | 39 | 7.1 |
| Qwen2.5-VL-3B-Instruct-imatrix | Q4_K_M | 0.3 | 14.4 (12–18) | 26% | 19.5 | 1.1 | 20/162 | 1 | 100 | 4.1 |
| Falcon-H1-Tiny-90M-Instruct ⁴ | Q4_K_S | 0.3 | 1.0 (0–2) | 7% | 1.4 | 0.0 | 7/144 | 0 | 134 | **0.4** |

All judged by `Qwen3.8-27B-imatrix:Q4_K_S`, 18 cases, 3 repeats. Judge grounding
stayed acceptable: 0–6 ungrounded, 0–1 omitted. The Gemma-4 run was the judge's
first perfect sheet in a while — 0 ungrounded, 0 omitted.

¹ Hosted, so it has no resident GB and is outside the Pareto front, which needs
memory. Temperature is not sent (Claude rejects it) and `num_ctx` does not apply;
its times are wall clock including the network. It is a **reference ceiling**, not
a value comparison.

² **Neither 32B run has a memory figure**, so neither can be placed on the Pareto
front. In both, the `/api/ps` lookup after the first case found no entry matching
the tag. It is now specifically the two 32B builds that miss it and no others,
which looks like how those tags are spelled on the server rather than bad luck.
The harness was changed after both runs (`a773284`) to match the tag
case-insensitively, normalise `:latest` and record a note when the lookup fails —
that fix has not yet been exercised by a real run. Expect roughly **29 GB** for
the Instruct build (~19.8 GB weights, ~1.4 GB vision, 8 GiB KV at 32768) and
**35 GB** for the Thinking build (~23 GB weights, ~1.4 GB vision, 12 GiB KV at
49152). Both are estimates. Measuring them is the most useful small thing left
to do.

³ **Lost 3 of 54 cases to runaway reasoning and ran at 44% on GPU.** Its trap
count is out of 149 rather than 162 because the lost cases take their traps with
them, and its times measure CPU spill, not the model. See the 2B section below —
both are findings, not accidents.

⁴ **Text-only**, so C11, C12 and C13 scored 0 with "model has no vision
capability" — 9 of its 54 runs, and why its traps are out of 144 rather than 162.
That is the guard working as intended, not instability. It is the floor marker for
the board.

⁵ **Self-judged, and measurably inflated.** The judge of record is this same
model. The identical 54 analyses graded by `claude-sonnet-5` score **79.8**, so
read this row as ~80. It ranks above Muse-Glimmer here; on Sonnet's scale it does
not. The run also lost C15.r3 to a `judge_json` bug, hence traps out of 157. The
measurement is in the section below.

### A local model gets within 6 points of the ceiling, at 16.7 GB

`Muse-Glimmer-30B` scores **82.8**, sixteen points clear of the next best local
model and **5.6 short of claude-sonnet-5**. It does this at **16.67 GB, entirely
on GPU**, in 51 seconds a case. Nothing else on this board is close to that
combination.

| | Sonnet | Muse-Glimmer-30B | Gemma-4-31B |
|---|---|---|---|
| Quality | **88.4** | 82.8 | 66.7 |
| Coverage | **90%** | 84% | 68% |
| Prose C01–C13 | **93.6** | 89.3 | 75.3 |
| Telemetry C14–C18 | **74.9** | 65.9 | 44.2 |
| Traps tripped | 4/162 | **1/162** | 3/162 |
| Unsupported | **13** | **13** | 11 |
| Found / missed | **343 / 22** | 285 / 26 | 189 / 69 |
| Resident | — | **16.7 GB** | 22.7 GB |
| Time a case | 29.2s | 51.2s | 4m 51s |

**It misses almost nothing.** 26 of 423 checkpoints against Sonnet's 22 — within
four. What separates them is conversion, not recall: Sonnet turns 81% of
checkpoints into full credit where Muse manages 67%, with 112 partials against
Sonnet's 58. Muse sees nearly everything Sonnet sees and states it less
definitively.

**It ties Sonnet on unsupported claims and beats it on traps** — 13 each, and
1/162 against 4/162. It is the second local model to beat the reference on
trustworthiness and the first to do so while also covering 84% of the answer key.
The caution that applied to the 32B-Thinking's 1/162 does not apply here: that
model earned its trap record by saying little, and this one did not.

**It dominates Gemma-4 outright** — better on quality and memory both, so Gemma
leaves the Pareto front after one run on it. It is also **5.7× faster**: a full
54-case run takes about 46 minutes against Gemma's 4.4 hours, and it stays at
100% on GPU where Gemma spilled to 91%.

**Telemetry is where the result is most surprising.** 65.9 on C14–C18 against the
previous local best of 44.2. C15 reaches **93**, C16 77, and even C17 — the case
that defeats everything, where no other local model exceeded 24 — reaches 40.
Sonnet's 58.9 on C17 is no longer far off.

#### Two things to be honest about

**This needs confirming with a different judge.** A 16-point jump is larger than
anything else on this board, and it was graded by a local judge. The judge's own
sheet was clean for this run (2 ungrounded, 0 omitted), and traps and invented
keys are computed independently of it, so there is no visible anomaly. But the
protocol this file already recommends for a surprising result is
`mode: rejudge` against `claude-sonnet-5` on the committed folder — cheap, since
it does not re-run the analyst. **Treat 82.8 as provisional until that is done.**

**The memory prediction in its Modelfile was too high.** It estimated ~20–21 GB
(16.1 GB weights + ~3.6 GB vision encoder + 0.69 GiB KV); measured **16.67 GB**.
The KV arithmetic is probably sound — it was computed from the card's own head
counts — so the vision encoder is much smaller than the card's ~1.8B ViT-G/14
implies at F16, or the language weights are smaller than the GGUF size suggests.
This also supersedes the 19.6 GB figure in CONFIG_SETTINGS, which predates the
projector and has no recorded `num_ctx`.

### Qwen3.8-27B, and what a self-judge is worth

`Qwen3.8-27B-imatrix-vision:Q4_K_S` has now been graded twice on the **same 54
analyses**: once by `claude-sonnet-5` (run 54) and once by the judge of record,
which is this same model (run 56). That makes it the only run on the board with a
direct measurement of judge effect, and the only one where the judge is the model
under test.

| | judged by Sonnet | judged by itself | diff |
|---|---|---|---|
| Quality | **79.8** | **84.8** | **+5.0** |
| Coverage | 89.8% | 89.8% | **0.0** |
| Found (share of checkpoints) | 80.9% | 79.5% | −1.4 |
| Missed | 4.3% | 3.1% | −1.2 |
| Unsupported per analysis | 1.25 | 0.79 | **−0.46** |
| Traps | 5/148 | 3/157 | — |
| Prose C01–C13 | 83.8 | 88.4 | +4.6 |
| Telemetry C14–C18 | 69.6 | 75.5 | +5.9 |

**The two judges agree exactly on what the analyses found** — coverage is 89.8%
both times, and the self-judge credits a slightly *smaller* share of checkpoints at
full marks. The entire +5.0 comes from penalties: 42 unsupported claims against 65,
and 3 traps against 5.

So the bias is not "it likes its own writing". It is narrower and worse: **the
self-judge forgives exactly the failure this model is worst at.** Under Sonnet,
1.25 unsupported claims per analysis is the loosest figure in the top tier by five
times. Under its own judging that becomes 0.79 and the row climbs above
Muse-Glimmer.

**It is not blanket generosity either.** It marked itself *down* on C11 (−4.8),
C13 (−4.8), C01 (−2.4) and C15 (−0.9) — cases where penalties are not the
deciding factor. The leniency concentrates where over-assertion is scored: C12
+19.0, C05 +11.1, C14 +10.3, C03 +9.5, C18 +9.1.

**Read the row as ~80, not 84.8.** It sits at rank 2 mechanically, because 84.8 is
comparable with the sixteen other Qwen3.8-judged rows by every key `--compare`
checks. It should not be read as beating Muse-Glimmer's 82.8. The fair comparison
does not exist yet — it needs Muse re-judged by Sonnet.

#### What this does and does not say about the other sixteen rows

**It does not invalidate them.** The effect measured here is *same-model*, not
same-family, and the board argues against family favouritism: the two non-Qwen
analysts scored **highest** under a Qwen judge — Muse-Glimmer 82.8 and Gemma-4
66.7, against a Qwen3-VL ceiling of 62.5. A judge tilted toward its own vendor
would have suppressed them, not crowned them.

**But it sets a floor on how finely the board can be read.** A judge capable of a
5-point swing on penalty-heavy analyses means gaps of a few points between adjacent
rows carry less weight than the confidence intervals suggest — particularly
between models with very different unsupported-claim rates.

#### Two harness findings from these runs

**C17 came back.** Run 54 lost two of three C17 repeats to the Claude judge's fixed
16,000-token `max_tokens`; the re-judge scored all three (61.5 against 53.8 on the
single repeat). That path now honours `--judge-num-predict` and defaults to 32,768
for a Claude judge.

**A `judge_json` bug was destroying valid verdicts.** Run 56 lost C15.r3 to
`judge returned no JSON object` on 6,621 characters of *correct* JSON. The recovery
logic stripped markdown fences before trying to parse, and the judge had quoted a
fenced SMTP stack trace inside a `"quote"` value — so the fence regex matched a
triple-backtick pair *inside* a JSON string and extracted the middle of it. The raw
reply is now tried unmodified before any fence recovery, with the other seven
recovery paths covered by tests. Any judge quoting a fenced code block was exposed
to this, which is most of C14–C18.

### The 4B is the best value under 10 GB

`Qwen3-VL-4B-Instruct` scores **48.6 at 7.9 GB resident**. Muse-Glimmer has since
taken the overall value crown at 16.7 GB, so this is now the sub-10 GB pick rather
than the board's best return — but within that bracket it is still the clear one:

| Model | Quality | Resident | Time / case |
|---|---|---|---|
| Qwen3-VL-8B-Instruct | 49.7 (48–52) | 9.4 GB | 7.3s |
| Qwen2.5-VL-32B-Instruct | 49.2 (49–50) | 32.5 GB | 33.9s |
| **Qwen3-VL-4B-Instruct** | **48.6 (48–50)** | **7.9 GB** | **8.4s** |
| Qwen2.5-VL-72B-Instruct | 45.6 (45–47) | 56.3 GB | 55.2s |

It **ties a 32B at a quarter of the memory and beats a 72B at a seventh of it**,
and its range overlaps both. Against its own 8B sibling the 1.1-point difference
sits inside both confidence intervals — statistically a tie, for 1.5 GB less and
at 185 output tok/s, the fastest capable model on the board.

It earns its Pareto place honestly rather than by being small: nothing measured
does better on both quality and memory.

**What it gives up is precision, not recall.** Coverage 59% against the 8B's 63%,
but 13 traps against 19, and 1.06 unsupported claims per analysis against 1.24.
Per point actually found it is the loosest capable model in the field — 0.40
unsupported claims per point, against 0.20 for the 32B-Instruct and 0.04 for
Sonnet. Its checkpoint mix is the most hedged of any model measured: 33% found,
42% partial, 25% missed.

So it is a first-pass triage model, not an output-to-a-human model. At 8.4s a
case, running it three times and comparing is still cheaper than one 32B pass.

**Its Thinking sibling is the better 4B if you have the memory.** 51.9 against
48.6, at 11.0 GB against 7.9 and 27.0s a case against 8.4 — and it is tidier on
every trust measure (10 traps against 13, no invented keys against 2, 43
unsupported against 57). The two 4B builds bracket the 8B-Instruct, which sits
between them on quality at 9.4 GB. Below 8B, reasoning is worth its memory; see
the next section.

### The 2B tier does not work, in either build

`Qwen3-VL-2B-Thinking` is the first model in the benchmark that fails on its own
terms rather than merely scoring badly, and it fails in three ways at once.

**It runs away at the card temperature.** Temperature 1.0 fixed the 8B (9 lost
cases → 0) and the 32B (3 → 0). It does not fix the 2B: 4 runs hit the 16,384
cap and **3 returned empty content**, after 60,035, 67,994 and 72,564 characters
of thinking. So the temperature fix has a size floor. Runaway reasoning is not
purely a sampling artefact — below some size the model cannot terminate a chain
of thought regardless of temperature, and there is no setting that rescues it.
`Modelfile.Qwen3-VL-2B-Thinking` called this in advance ("THIS IS THE BUILD MOST
EXPOSED TO RUNAWAY THINKING IN THE WHOLE FLEET"); the prediction was right.

**It costs more memory than a model twice its size that scores twice as well.**

| | 2B-Thinking | 4B-Instruct |
|---|---|---|
| Quality | 26.7 | **48.6** |
| Resident | 8.1 GB | **7.9 GB** |
| Output tokens a case | 5,794 | **1,198** |

At `num_ctx` 49152 the KV cache is several times the weights of a 2B, so
shrinking the model barely shrinks the footprint — the Thinking track's context
requirement sets a floor of about 8 GB no matter how small the model is. The
4B-Instruct **dominates it outright** on the Pareto definition: better on quality
*and* memory. It is the only model on the board that another model strictly
dominates.

**It is the least trustworthy model measured.** 27 traps in 149 (18.1%, against
the 3B's 12.3% and the 4B-Instruct's 8.0%), 117 unsupported claims — 2.3 per
delivered analysis — and 3 invented keys. It also writes more than any other
model in the benchmark at 5,794 output tokens a case. More output, less signal:
it misses 43% of checkpoints, the worst rate on the board.

On telemetry it is at the floor: **2.4** on C14–C18, with C15, C17 and C18 all
scoring exactly 0.

**Its Instruct sibling is no better.** 25.3 against 26.7, and it has its own
failure mode: 7 of 54 runs truncated at `num_predict` (13%, the worst rate in the
benchmark) and a 10.3-point spread across repeats, also the widest. The whole 2B
tier is unusable — one build cannot stop thinking, the other cannot stop writing.

| | 2B-Instruct | 2B-Thinking | 4B-Instruct |
|---|---|---|---|
| Quality | 25.3 | 26.7 | **48.6** |
| Resident | **5.4 GB** | 8.1 GB | 7.9 GB |
| Traps | 30/162 (18.5%) | 27/149 (18.1%) | **13/162 (8.0%)** |

The conclusion for the fleet is simple. **Do not run Thinking builds below 4B**,
and do not expect anything at 2B to be usable at all. The 4B-Instruct costs 2.5 GB
more than the 2B-Instruct and is worth 23 more points; that is the best marginal
return anywhere on this board.

The 2B-Instruct does reach the Pareto front at 5.4 GB — it displaced the
Qwen2.5-VL-7B, which now uses more memory for a lower score — but being on the
front is not a recommendation at 25.3. See the note on the front's weakness under
the Falcon result.

### The floor, and two things it exposes

`Falcon-H1-Tiny-90M` was run to find where the curve bottoms out. It scores
**1.0** with **6.6% coverage**, non-zero on only 4 of 18 cases (C01 2, C02 8,
C06 5, C09 3) and **exactly 0.0 across all five telemetry cases**. The curve does
not taper toward zero — it falls off a cliff somewhere between 90M and 2B, and
90M is already past it. That is the useful result, and it is the only one.

Two things it exposes are worth more than the score.

**Small does not mean fast.** At 8.5 output tok/s it is the *slowest* generator on
the board — slower than the 72B at 14.7, and 26× slower than the 3B at 225.4,
despite being 33× smaller:

| Model | Params | Resident | Output tok/s |
|---|---|---|---|
| Qwen2.5-VL-3B | 3B | 4.1 GB | **225.4** |
| Qwen2.5-VL-72B | 72B | 56.3 GB | 14.7 |
| **Falcon-H1-Tiny-90M** | **0.09B** | **0.4 GB** | **8.5** |

Falcon-H1 is a hybrid Mamba/attention architecture, and on this evidence the
runtime has no optimised path for it — the whole "tiny model, instant answers"
assumption fails. If a Falcon-H1 at a useful size is ever considered, benchmark
its throughput before assuming the family is cheap to run.

**It is on the Pareto front, and that is a flaw in the headline.** Nothing uses
less than 0.4 GB, so nothing can dominate it, and `--compare` lists it alongside
the 4B and 8B builds as though it were a sensible choice. **Being the smallest
makes a model Pareto-optimal no matter how badly it scores.** The best-value pick
is unaffected, because `--value-margin 5.0` requires a model to be within 5 points
of the best. Read the front with that in mind, or add a quality floor to it.

**It also writes the most unsupported claims in the benchmark** — 134, or 3.0 per
delivered analysis, while covering 6.6% of the answer key. That combination is the
signature of fluent nonsense: it produces confident ticket-analysis-shaped prose
that is almost entirely untethered. Its 7 traps look low only because it rarely
says anything specific enough to trip one, which is the same caution that applies
to reading the 32B-Thinking's 1/162.

### What reasoning actually buys, measured at four sizes

The Qwen3-VL fleet is complete: four size-matched Instruct/Thinking pairs, same
cases, same judge. Δ is Thinking minus Instruct, so positive means reasoning
helped.

| Size | Prose (C01–C13) Δ | Telemetry (C14–C18) Δ | Overall Δ | Trap rate, I → T |
|---|---|---|---|---|
| 2B | +2.7 | −1.9 | +1.4 | 18.5% → 18.1% |
| 4B | **+6.0** | −3.8 | **+3.3** | 8.0% → 6.2% |
| 8B | **+5.0** | −3.7 | +2.6 | 11.7% → **4.3%** |
| 32B | −0.0 | **−6.6** | **−1.9** | 4.9% → **0.6%** |

**The telemetry penalty is universal.** Negative at all four sizes, and it grows
with the model: −1.9, −3.8, −3.7, −6.6. Logs and Sentry exports reward exhaustive
extraction and the reasoning budget does not buy more of it, at any scale.

**The prose benefit is an inverted U, not a trend.** +2.7 at 2B, peaking at +6.0
and +5.0 for the 4B and 8B, then vanishing at 32B. Reasoning is a **substitute for
parameters** — but it needs enough parameters to work with. A 2B is too weak to
reason its way to much; a 32B does not need to.

**The trap reduction has a floor, which corrects an earlier claim here.** This
file previously said reasoning "always reduces traps, monotonically" on the
strength of three pairs. The 2B pair breaks it: 18.5% against 18.1% is no
difference at all. The effect is real from 4B upward and absent below it.

So the net flips twice across the range. **Below 4B neither build is usable**;
between 4B and 8B the Thinking build is better and more careful; at 32B the
Instruct build wins and the only reason to prefer reasoning is its 0.6% trap rate.

**The confound, and which way it cuts.** No pair is quant-matched, and in all four
the *Thinking* build carries the higher quant (Q4→Q5, Q4→Q5, Q3→Q4, Q4→Q5). The
telemetry penalty is therefore **robust and probably understated** — the reasoning
builds lose despite a quantization advantage — while the prose gains are upper
bounds. It is not simply proportional to the quant gap: the 8B pair has the widest
gap and a smaller prose gain than the 4B.

Temperature also differs by track (0.3 Instruct, 1.0 Thinking) by design, since the
cards ask for different values. On the 8B, where both were measured, prose was
unchanged (63.6 → 62.9), so temperature is not driving the prose column.

Standardising the Thinking track on Q4_K_M imatrix would remove the confound for
~0.2 GB a build, and is the one change that would make this table conclusive rather
than strongly indicative.

### Temperature 0.3 is wrong for the small Instruct builds

The 4B-Instruct raised this and the 2B settles it. Runs that hit `num_predict`,
Qwen3-VL Instruct track, all at temperature 0.3:

| Model | Truncated runs | Rate |
|---|---|---|
| 2B-Instruct | **7 of 54** | 13.0% |
| 4B-Instruct | 4 of 54 | 7.4% |
| 8B-Instruct | 0 of 54 | 0% |
| 32B-Instruct | 0 of 54 | 0% |

No Qwen2.5-VL build ever hit the cap, so this is specific to the small Qwen3-VL
Instruct builds, and it scales cleanly with size. The card asks for 0.7; the fleet
runs 0.3, and below 8B that costs real points.

**It costs the 2B roughly 1.5–2 points of its 25.3.** C16 lost two of its three
repeats to truncation, scoring 0 twice against a ~40 on the surviving run, which
alone drags the case mean from ~40 to 13.3. Its overall range of **10.3 points**
(20.6–30.9) is the widest in the benchmark, which is the same instability seen from
the other end. For the 4B the equivalent cost was only 0.21 points.

**No re-run is planned.** Both 2B builds sit 22+ points below the 4B-Instruct, so
moving the 2B from 25.3 to perhaps 27 changes no decision. The finding is recorded
for the next small Instruct build that matters: **run it at 0.7, not 0.3.**

### The gap to the ceiling

Sonnet scores **88.4 against 82.8** — 5.6 points, down from 36.1 when the 8B led.
The composition of that remaining gap is narrow and specific:

| | Sonnet | Muse-Glimmer | Gemma-4 | Qwen3-VL-32B-I |
|---|---|---|---|---|
| Found (full credit) | **343 (81%)** | 285 (67%) | 189 (45%) | 193 (46%) |
| Partial (half credit) | 58 (14%) | 112 (26%) | 165 (39%) | 160 (38%) |
| Missed | **22 (5%)** | 26 (6%) | 69 (16%) | 70 (17%) |

**The "local models live on partial credit" reading no longer holds generally.**
It is still true of everything below Muse — Gemma and the Qwen 32Bs convert
under half their checkpoints to full credit. But Muse misses only four more
checkpoints than Sonnet out of 423. Its deficit is conversion: 26% partials
against Sonnet's 14%. It finds the material and hedges on it.

**Sonnet is no longer the most trustworthy model on the board either.** Muse ties
it on unsupported claims (13 each) and beats it on traps (1 against 4). Per point
found Sonnet is still ahead — 0.038 unsupported per point against Muse's 0.046 —
but that margin is now within the noise of two runs, where against the Qwen 32Bs
(0.20 and 0.28) it was an order of magnitude.

What is left of the gap is **telemetry and definiteness**: 9.0 points on C14–C18
against 4.3 on the prose cases, and a 12-point spread in full-credit conversion.

### The telemetry cases are still the gap

C14–C18: **65.9** against Sonnet's 74.9. On the prose cases the spread is 93.6
against 72.5, a factor of 1.3; on logs and Sentry exports it is a factor of 2.1 —
down from 2.5, but still the widest part of the board.

C17 remains the hardest case in the suite for everything: 14.1 for the local
leader, 17.9 for the Thinking build, and Sonnet only reaches 58.9.

Vision is a wash between the two 32Bs — C09/C11/C12/C13 at 77.8/50.0/71.4/61.9 for
the Instruct build against 83.3/47.6/59.5/61.9 — and neither is close to Sonnet's
94.5/76.2/80.9/97.6.

### Temperature 1.0 fixes the Thinking track down to 4B, and no further

The Thinking builds' empty-content failures at temperature 0.3 were a
low-temperature artefact. The two builds measured at both temperatures:

| | 8B at 0.3 | 8B at 1.0 | 32B at 0.3 | 32B at 1.0 |
|---|---|---|---|---|
| Empty-content runs | **9 of 54** | **0** | **3 of 54** | **0** |
| Quality (delivered) | 47.3 | 52.3 | 64.8 ³ | **60.6** |
| Output tokens a case | 5,244 | 2,885 | — | 2,849 |
| Time a case | 53.1s | 26.6s | — | 109.1s |

³ judged by `Qwen3-Coder-30B`, which produced 39 ungrounded verdicts. **Not
comparable** with the 60.6 beside it — see Superseded measurements. The 0.3 column
is listed for the failure count only.

At 1.0 the 8B, 32B and 4B Thinking builds answer every case. The **4B-Thinking**
recorded **0 errors and 0 flags** while generating 3,897 output tokens a case,
more than either larger Thinking build, without once reaching the 16,384 cap.

**The 2B is the exception, and it sets the floor.** At the same temperature 1.0 it
hit the cap on 4 runs and returned empty content on 3, after 60k–74k characters of
thinking. So temperature is not a universal fix: below about 4B the model cannot
reliably terminate a chain of thought at any setting. Raising `num_predict` would
not help either — 16,384 tokens is already more than four times what the working
Thinking builds use.

On the 8B, where a clean before-and-after exists, prose was unchanged
(63.6 → 62.9) and the whole gain was telemetry plus no longer forfeiting nine runs.
Raising `num_predict` is the wrong lever: more budget buys more looping.

**The mirror image is now visible on the Instruct track.** The 4B-Instruct at 0.3
hit `num_predict` on 4 of 54 runs, the first Instruct build ever to do so — see the
caveats. Its Thinking sibling at 1.0 hit it zero times while generating three times
as many tokens. The fleet's 0.3 is below every card in it, and 4B is where that
starts to bite.

**Runs at different temperatures are ranked together**, with the temperature shown
in its own column here and in the generated Runs table. `--compare` does not treat
temperature as a comparability key. That is deliberate: a single fleet temperature
cannot suit both tracks, since the cards ask 0.7 on Instruct and 1.0 on Thinking.
It does mean the 32B Instruct-versus-Thinking comparison above holds temperature
as well as quant constant only loosely — see the caveat there.

### The mid-table tie still holds

49.7 against 49.2, with overlapping ranges, is a tie between the 8B-Instruct and
the Qwen2.5-VL-32B. The composition is not the same:

| | Qwen3-VL-8B | Qwen2.5-VL-32B |
|---|---|---|
| Coverage | **63%** | 54% |
| Traps tripped | 19/162 | **7/162** |
| Unsupported per analysis | 1.24 | **0.69** |
| C14–C18 | **28.4** | 19.5 |

The 8B finds substantially more and is wrong more often; the 32B finds less and is
right about more of it. For a pipeline with a verification step, take the 8B's
recall. For output a human reads and acts on directly, take the 32B.

### Memory: it predicts nothing, and the best model is mid-range

Ordered by measured memory: 0.4 GB → 1.0, 4.1 GB → 14.4, 5.4 GB → 25.3,
7.1 GB → 24.5, **7.9 GB → 48.6**, 8.1 GB → 26.7, 9.4 GB → 49.7,
**11.0 GB → 51.9**, 13.0 GB → 52.3, **16.7 GB → 82.8**, 22.7 GB → 66.7,
32.5 GB → 49.2, 56.3 GB → 45.6.

**The peak is at 16.7 GB, and the curve falls on both sides of it.** The best
local model uses less memory than the 22.7 GB model that scores 16 points lower,
less than half of what the 32.5 GB model uses for 33 points less, and under a
third of the 56.3 GB model's for 37 points less.

That kills the framing earlier versions of this file used. There is no plateau, no
step function and no threshold worth quoting. The useful statements are narrower:

- **Below about 8 GB, size still binds.** 5.4 GB → 7.9 GB is worth 23 points, the
  steepest step on the board, and the 2B tier does not work at all.
- **Between 8 and 13 GB the Qwen fleet sits on a shelf** at 48.6–52.3, spanning a
  7× range in parameters for four points.
- **Above 13 GB, memory tells you nothing.** 16.7 GB → 82.8, 22.7 GB → 66.7,
  32.5 GB → 49.2, 56.3 GB → 45.6. Architecture, generation and training dominate
  so completely that footprint is not a useful proxy for anything.

The practical consequence: **stop sizing this job by memory.** A 16.7 GB model
scores within 6 points of a frontier API model, and the three larger models
measured are all worse. Spending more than about 17 GB has no evidence behind it.

The 8.1 GB entry is the 2B-Thinking, the one point far below its neighbours — 22
points under a model using less memory. See the 2B section.

**Read the two case groups separately.** C01–C13 are prose ticket analysis;
C14–C18 attach logs and Sentry telemetry. The headline Quality is a mean over both
and moves mostly with the telemetry cases, so it is not a good single number for
"can this model read a ticket". Quote the two columns.

## Runs still to do

Every model that was queued has now been run: the eight Qwen3-VL builds, the four
Qwen2.5-VL builds, Falcon-H1-Tiny as a floor, and both non-Qwen candidates. What
remains is verification, not coverage.

**1. Re-judge Muse-Glimmer with Sonnet.** Now the single most important run
outstanding: it is the only way to know whether Muse or Qwen3.8-27B is the better
local model, and the self-judge measurement above shows the question cannot be
settled on the current numbers. It confirms or
corrects the 82.8 headline, *and* it is the only way to compare Muse with the
Qwen3.8-27B run, which is already Sonnet-judged - the two strongest local models
measured currently sit on different scales. `mode: rejudge`,
`results_dir: jira_analyst_results/Muse-Glimmer-30B-imatrix_Q4_K_S`,
`judge: claude-sonnet-5`. Worth doing now that the Claude judge's token budget is
fixed; before that it would have lost C17 the same way run 54 did.

**2. Re-run the two Qwen3-VL 32B builds to capture memory.** Both lost their
`/api/ps` figures, so neither can be placed on the Pareto front. Lower priority
now — Muse dominates both on quality by 20+ points, so their footprints no longer
affect any recommendation. Worth doing only to close the gap in the table.

**2a. Re-judge Qwen3.8-27B once more** to recover C15.r3, now that the
`judge_json` fence bug is fixed. Cheap, and it makes run 56 a complete
54-analysis set rather than 53.

**3. A second Qwen3.8-27B run at `=low`.** The most informative single run still
available. It would hold weights, quant, size, temperature and judge all constant
and vary only reasoning effort - the clean test no Instruct/Thinking pair could
give. The board's evidence predicts `low` should win: reasoning cost the
size-matched 32B pair 6.6 points on telemetry and gained nothing on prose, and
this model's specific weakness is over-assertion, which less reasoning may reduce.

**3a. Qwen3.6-27B as an analyst.** Also a vision-language model, also now with a
projector step in its Modelfile. Lower value than the 3.8 was: its card documents
no reasoning-effort control, so the `=medium` that made the 3.8 run cleanly has
nothing to bind to, and unbounded thinking is exactly how it failed as a judge.
If it is tried, disable thinking entirely.

**4. The analyst prompt A/B**, still unstarted. The prompt is written for prose
ticket grooming and a third of the cases are not that; the capable models fill
"acceptance criteria" on C14–C18 regardless. Worth testing on C14–C18 from a
branch before rebuilding the board, and now cheaper to justify than it was, since
Muse's 65.9 on those cases shows there is real headroom to recover.

Still unresolved from the fleet itself: no Instruct/Thinking pair is
quant-matched, so the reasoning table remains strongly indicative rather than
conclusive. Standardising the Thinking track on Q4_K_M imatrix would fix it for
~0.2 GB a build.

## The judge

**Judge of record: `Qwen3.8-27B-imatrix:Q4_K_S`**, applied automatically when
the workflow's `judge` input is blank, with `think=medium` and
`num_predict 40960` supplied by `JUDGE_DEFAULTS`. Without `think=medium` it
reasons at xhigh and returns empty content.

`claude-sonnet-5` remains the reference and is still selectable. It is about
four times faster per call and uses no GPU, which matters when the model under
test is large: a 72B plus a local judge roughly doubled per-case time.

### Why this one, and what the others did

Six candidates were tried. The column that separates them is **ungrounded** —
verdicts credited with a quotation the analysis does not contain. Agreement is
measured against Sonnet on the cases both judges graded.

| Judge | Δ vs Sonnet | Ungrounded | Omitted | Verdict |
|---|---|---|---|---|
| `claude-sonnet-5` | reference | 0 over 5 runs | 0 | Reference |
| **`Qwen3.8-27B`** | **+1.0, −1.3** | 0–6 per run | 0–1 | **Judge of record** |
| `Gemma-4-31B` | +1.3 | 2 | 0 | Passes; no speed gain |
| `Qwen3.6-27B` | +8.8 | 0 | 9 | Lenient; runaway thinking |
| `Qwen3.5-9B` | +7.9 | **58** | 26 | Fabricates quotes |
| `Qwen3-Coder-30B` | — | **39** | 0 | Fabricates quotes |
| `minimax-m3:cloud` | — | 0 | — | Never completed a clean run |
| `Muse-Glimmer-30B` | — | — | — | Errors immediately |

The two Δ figures for Qwen3.8 are from independent runs (the Qwen3-VL-32B and
the Qwen2.5-VL-72B), both within about a point of Sonnet on the same 13 cases.

**Its ungrounded count is drifting up.** The clean sheets came from the early runs;
the 32B-Thinking produced 3 and the 32B-Instruct 6, out of 423 checkpoints. Still
under 1.5%, and an order of magnitude below the judges that were rejected, but it
is no longer the clean sheet the first runs showed. Watch the per-run figure in the
warnings list rather than assuming it, and if it keeps climbing, re-qualify the
judge against Sonnet on a committed run.

### Calibration has a blind spot

`mode: calibrate-judge` grades three synthetic analyses per case and screens out
a judge that is broken. It **cannot** detect a judge that quotes the answer key
back instead of the analysis, because the perfect synthetic analysis is built
from the key's own wording — so those quotes ground successfully and the judge
scores a clean sheet.

`Qwen3-Coder-30B` and `Qwen3.5-9B` both pass that way and were caught only on
real prose, at 39 and 58 ungrounded. **To qualify a new judge, follow
calibration with `mode: rejudge` of a run already graded by another judge, and
compare per case.** That needs the run folder committed, since the runner only
sees committed files.

---

## What makes two runs comparable

`--compare` ranks runs side by side only if they share the cases, judge, judge
effort, judge prompt, analyst prompt and system-prompt mode. Anything else is
listed under "Not ranked" with the reason. `num_ctx`, `num_predict`, `repeats`
and **temperature** may differ; temperature is shown in its own column so the
difference is visible in the ranking rather than hidden behind an exclusion.

Changing the judge rescales every score, so a mixed-judge table is not a
ranking. After a judge or case change, bring older runs up to date with
`mode: rejudge` rather than re-running the analyst.

**The analyst system prompt is a comparability key**, so revising it un-ranks every
run in this file. It is written for prose ticket grooming — it enumerates
screenshots but not log or export attachments, and its mandatory section 3 asks for
steps to reproduce and acceptance criteria, which a third of the cases do not have.
The capable local models fill those headings anyway on C14–C18 (the Qwen2.5-VL 32B
and 72B do it in 15 of 15 analyses; Sonnet in 8 of 15). Any revision should be
A/B'd on C14–C18 from a branch before the board is rebuilt.

## Superseded measurements

These were taken before C14–C18 existed, or with a judge that failed. **None is
comparable with the table above** — kept only so the history is not lost. Their
result folders are no longer committed.

| Model | Quality | Cases | Judge | Why superseded |
|---|---|---|---|---|
| Qwen2.5-VL-72B-Instruct:Q4_K_S | 60.0 | 13 | Sonnet | Pre-C14; re-measured above |
| Qwen2.5-VL-32B-Instruct:Q5_K_M | 59.6 | 13 | Sonnet | Pre-C14; re-measured above |
| Qwen2.5-VL-7B-Instruct-imatrix:Q4_K_S | 30.9 | 13 | Sonnet | Pre-C14 |
| Qwen2.5-VL-3B-Instruct-imatrix:Q4_K_M | 16.0 | 18 | Sonnet | Was filed under a model name that does not exist (`...-2B-...`); re-measured above |
| Falcon-H1-Tiny-90M-Instruct | 3.2 | 10 | Sonnet | Pre-C14, fewer cases; re-measured above at 1.0 |
| Qwen3-VL-32B-Thinking:Q5_K_M | 64.8 | 18 | Qwen3-Coder-30B | Judge produced 39 ungrounded verdicts; also temp 0.3, losing 3 of 54 cases. Re-measured above at 60.6 |
| Qwen3-VL-8B-Thinking-imatrix:Q4_K_M | 47.3 | 18 | Qwen3.8-27B | Temp 0.3; lost 9 of 54 cases to runaway reasoning. Re-measured above at 52.3 |
| Qwen3-VL-32B-Instruct-imatrix | — | 18 | — | Judging failed twice; also Q3_K_M weights under a Q4_K_M tag. Rebuilt and re-measured above at 62.5 |

**The 64.8 is not evidence that the 32B-Thinking got worse.** A judge that
fabricates 39 quotations scores high because ungrounded verdicts default to
credit. The 60.6 is the trustworthy figure, and it is over 54 completed cases
rather than 51.

Two further Qwen2.5-VL-32B runs were made at num_ctx 49152 and 65536, above that
model's 32768 trained window. Their judge verdicts are valid but their analyst
scores are not, and they are not listed.

---

## Caveats specific to these results

**Per-case variance is 15–25 points** at temperature 0.3, measured across 3
repeats. The aggregate averages most of it out — quality ranges come in at ±2–3
— but a single case score means little. Use `repeats: 3` for anything you will
decide on and read the range, not the midpoint. The 32B-Thinking's 0.7-point range
is the exception in the field and has not been explained; its Instruct sibling
spreads 5.5 points at the same repeat count.

**Time is not a property of the model, and one figure here looks wrong.** The
runner is shared, and a long run usually overlaps with something else. The
32B-Instruct returned **11.3 output tok/s against the 32B-Thinking's 28.4** —
backwards, since the Instruct build carries the *lower* quant and should be the
faster of the two. The likeliest explanation is partial CPU offload, which would
show as `On GPU` under 100% — and that is exactly the column its missing `/api/ps`
snapshot would have filled. Treat its 84.9s a case as unreliable; the quality
figures are unaffected.

**Memory can go unmeasured, and a run then leaves the Pareto front.** Both 32B runs
have no footprint because the `/api/ps` lookup found no entry for their tags. The
lookup is now case-insensitive, normalises `:latest` and records a note when it
misses, but that fix postdates both runs and has not been exercised. Check for a
`GB` figure before treating a run as complete. There is deliberately no fallback
that assumes the only loaded model is the one under test: that would report the
judge's footprint as the analyst's.

**Low temperature strains the small Instruct builds too, and 4B is where it
starts.** The 4B-Instruct hit `num_predict` on 4 of 54 runs — the first Instruct
build in the benchmark ever to do so; no other, from the 3B to the 72B, has hit
the cap once. It is sporadic rather than case-specific: it happened on C01, the
shortest and best-specified case in the suite, as well as on C14, C17 and C18.
The cost is small, because the analysis is written before the model starts
rambling — three of the four scored at or above their case average, and only
C17.r1 was destroyed, worth **0.21 points** of overall quality. But the direction
matches the Thinking track exactly: the fleet runs 0.3, this build's card asks
0.7, and the smaller the model the less margin it has. If the 2B-Instruct shows
the same thing more severely, the Instruct track's 0.3 needs revisiting rather
than patching per model.

**Thinking builds can return nothing.** Reasoning counts against `num_predict`,
and a model that runs out returns empty content with the text stranded in
`message.thinking`. At temperature 0.3 the 32B lost 3 of 54 cases that way and the
8B lost 9; at 1.0 both lost none, and so did the 4B. **The 2B lost 3 at 1.0**, so
treat temperature as a fix that works down to 4B and not below. Such a case is recorded as an error and scored 0,
and is **not** retried — so a run can look complete while cases are missing. Read
the warnings list first, and run Thinking builds at the card's temperature.

**Invented ticket keys are the trust failure to watch.** The 32B-Instruct produced
five, all shaped exactly like the real keys in the cases. The detector only flags
prefixes it has seen in the cases or in the analyst's own instructions, so a
fabricated key using an unrelated prefix would still pass. Read the
`invented_keys` list in a run's results.json, not just the count.

**The telemetry cases are where the field separates.** Every local model is far
below the ceiling on C14–C18 — 36.4 at best against 74.9 — and C17 defeats
everything measured, Sonnet included at 58.9. That is what those cases were
written to do, and it means a model that looks mid-table on C01–C13 may be much
further behind on log and Sentry analysis.
