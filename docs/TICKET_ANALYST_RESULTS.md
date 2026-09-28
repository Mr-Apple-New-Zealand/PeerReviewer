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

Ten models have been measured on the full eighteen cases with the judge of
record. Everything earlier is superseded — see below.

| Model | Quant | Temp | Quality | Coverage | C01–C13 | C14–C18 | Traps hit | Invented | Unsup | GB |
|---|---|---|---|---|---|---|---|---|---|---|
| **claude-sonnet-5** ¹ | — | n/a | **88.4 (87–91)** | **90%** | **93.6** | **74.9** | 4/162 | 0 | **13** | — |
| **Qwen3-VL-32B-Instruct-imatrix** | Q4_K_M | 0.3 | **62.5 (59–65)** | **69%** | **72.5** | **36.4** | 8/162 | **5** | 39 | — ² |
| Qwen3-VL-32B-Thinking | Q5_K_M | 1.0 | 60.6 (60–61) | 66% | 72.5 | 29.8 | **1/162** | 0 | 51 | — ² |
| Qwen3-VL-8B-Thinking-imatrix | Q4_K_M | 1.0 | 52.3 (48–54) | 60% | 62.9 | 24.7 | 7/162 | 0 | 59 | 13.0 |
| Qwen3-VL-8B-Instruct-imatrix | Q3_K_M | 0.3 | 49.7 (48–52) | 63% | 57.9 | 28.4 | 19/162 | 1 | 67 | **9.4** |
| Qwen2.5-VL-32B-Instruct | Q5_K_M | 0.3 | 49.2 (49–50) | 54% | 60.6 | 19.5 | 7/162 | 0 | 37 | 32.5 |
| **Qwen3-VL-4B-Instruct-imatrix** | Q4_K_M | 0.3 | 48.6 (48–50) | 59% | 58.6 | 22.6 | 13/162 | 2 | 57 | **7.9** |
| Qwen2.5-VL-72B-Instruct | Q4_K_S | 0.3 | 45.6 (45–47) | 48% | 58.7 | 11.7 | 8/162 | 0 | 15 | 56.3 |
| Qwen2.5-VL-7B-Instruct-imatrix | Q4_K_S | 0.3 | 24.5 (23–25) | 31% | 33.4 | 1.3 | 17/162 | 0 | 39 | 7.1 |
| Qwen2.5-VL-3B-Instruct-imatrix | Q4_K_M | 0.3 | 14.4 (12–18) | 26% | 19.5 | 1.1 | 20/162 | 1 | 100 | 4.1 |

All judged by `Qwen3.8-27B-imatrix:Q4_K_S`, 18 cases, 3 repeats. Judge grounding
stayed acceptable: 0–6 ungrounded, 0–1 omitted.

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

### The 4B is the value result of the whole benchmark

`Qwen3-VL-4B-Instruct` scores **48.6 at 7.9 GB resident** — and that number only
means something next to what it is level with:

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

### Reasoning does not pay at 32B — the size-matched comparison

This is the run that settles a question the board could not answer before, and it
reverses what the previous write-up concluded from an unmatched pair. Same family,
same size, same cases, same judge:

| | 32B-Instruct | 32B-Thinking |
|---|---|---|
| Quality | **62.5** | 60.6 |
| C01–C13 (prose) | **72.50** | 72.47 |
| C14–C18 (telemetry) | **36.4** | 29.8 |
| Coverage | **69%** | 66% |
| Found / partial / missed | **193 / 160 / 70** | 180 / 155 / 88 |
| Traps tripped | 8/162 | **1/162** |
| Invented ticket keys | **5** | **0** |
| Unsupported per analysis | **0.72** | 0.94 |
| Output tokens a case | **894** | 2,849 |
| Time a case | **84.9s** | 1m 49s |

**On prose the two are indistinguishable — 72.50 against 72.47.** Not close:
identical to two decimal places over 13 cases and 3 repeats. Whatever the
reasoning track is doing, it is not helping this model read a ticket.

**On telemetry the Instruct build wins by 6.6, using a third of the tokens.** The
earlier claim in this file that "reasoning pays at 32B" compared the 32B-Thinking
against the *8B*-Instruct, so it was measuring size, not reasoning. With size held
constant the effect disappears and then reverses.

**But the telemetry gain splits by case type, and that is the real finding:**

| Case | Instruct | Thinking | Diff |
|---|---|---|---|
| C14 log triage | **39.8** | 19.2 | **+20.6** |
| C15 log, wrong hypothesis | **53.7** | 35.2 | **+18.5** |
| C16 two logs, one regression | **53.3** | 45.0 | +8.3 |
| C17 Sentry event, symptom vs fault | 14.1 | **17.9** | −3.8 |
| C18 Sentry, group and prioritise | 21.2 | **31.8** | −10.6 |

The three **log** cases go heavily to the direct model; both **Sentry** cases go to
the reasoning one. That is a coherent split rather than noise: log triage rewards
exhaustive extraction — find every fault, name every handler, notice what is
routine — while C17 and C18 are inference problems, working out that the headline
error is a symptom, or that eight issues share four causes. Reasoning helps where
the work is deduction and hurts where the work is enumeration.

**The Instruct build pays for its recall in trustworthiness.** It invented **five
ticket keys** — `BANK-376`, `BANK-378`, `BANK-399`, `BANK-499`, `BANK-500`, on
C03, C04 and C18 — the worst record in the field. These are not obvious
placeholders; they look exactly like the real keys in the cases, which makes them
more dangerous than a wrong fact. It also trips 8 traps against the Thinking
build's 1.

So the size-matched answer is: **reasoning buys carefulness, not accuracy.** Pick
the Instruct build for recall and speed, the Thinking build if a confident false
statement is expensive.

### The gap to the ceiling

Sonnet scores **88.4 against 62.5** — 25.9 points, down from 36.1 when the 8B led.
The composition still differs in kind:

| | Sonnet | 32B-Instruct | 32B-Thinking | 8B-Thinking |
|---|---|---|---|---|
| Found (full credit) | **343 (81%)** | 193 (46%) | 180 (43%) | 147 (35%) |
| Partial (half credit) | 58 (14%) | 160 (38%) | 155 (37%) | 166 (39%) |
| Missed | **22 (5%)** | 70 (17%) | 88 (21%) | 110 (26%) |

Every local model's score is carried by partial credit; Sonnet's is carried by
points it actually made. The local leader gets full credit on 46% of checkpoints
against Sonnet's 81%.

**Sonnet is also the most trustworthy, not merely the most thorough.** 13
unsupported claims against 39 and 51, no invented keys, and 4 traps. Per genuine
finding the gap is starker: 0.04 unsupported claims per point found, against 0.20
for the 32B-Instruct and 0.28 for the 32B-Thinking. The usual recall-against-trust
trade-off does not appear — it finds more *and* asserts less that is unsupported.

### The telemetry cases are still the gap

C14–C18: **36.4** against Sonnet's 74.9. On the prose cases the spread is 93.6
against 72.5, a factor of 1.3; on logs and Sentry exports it is a factor of 2.1 —
down from 2.5, but still the widest part of the board.

C17 remains the hardest case in the suite for everything: 14.1 for the local
leader, 17.9 for the Thinking build, and Sonnet only reaches 58.9.

Vision is a wash between the two 32Bs — C09/C11/C12/C13 at 77.8/50.0/71.4/61.9 for
the Instruct build against 83.3/47.6/59.5/61.9 — and neither is close to Sonnet's
94.5/76.2/80.9/97.6.

### Temperature 1.0 is confirmed at two sizes

The Thinking builds' empty-content failures at temperature 0.3 were a
low-temperature artefact. Both builds, same change:

| | 8B at 0.3 | 8B at 1.0 | 32B at 0.3 | 32B at 1.0 |
|---|---|---|---|---|
| Empty-content runs | **9 of 54** | **0** | **3 of 54** | **0** |
| Quality (delivered) | 47.3 | 52.3 | 64.8 ³ | **60.6** |
| Output tokens a case | 5,244 | 2,885 | — | 2,849 |
| Time a case | 53.1s | 26.6s | — | 109.1s |

³ judged by `Qwen3-Coder-30B`, which produced 39 ungrounded verdicts. **Not
comparable** with the 60.6 beside it — see Superseded measurements. The 0.3 column
is listed for the failure count only.

At 1.0 both builds answer every case. On the 8B, where a clean before-and-after
exists, prose was unchanged (63.6 → 62.9) and the whole gain was telemetry plus no
longer forfeiting nine runs. Raising `num_predict` is the wrong lever: more budget
buys more looping.

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

### Memory: flat from 8 GB to 56 GB

Ordered by measured memory: 4.1 GB → 14.4, 7.1 GB → 24.5, **7.9 GB → 48.6**,
9.4 GB → 49.7, 13.0 GB → **52.3**, 32.5 GB → 49.2, 56.3 GB → 45.6.

The curve rises very steeply to about 8 GB and is then **flat or falling all the
way to 56 GB**. Everything from the 4B to the 72B — a 7× span in memory and an
18× span in parameters — lands between 45.6 and 52.3, which is barely wider than
a single model's run-to-run range. The 4B result is what makes this sharp: it is
not that big models disappoint, it is that a 7.9 GB model reaches the same plateau.

**Two exceptions sit above the plateau and neither has been measured.** The 32B
Instruct and Thinking builds score 62.5 and 60.6, roughly 10 points clear of
everything else, and both are missing their `/api/ps` figure. If their estimates
(~29 GB and ~35 GB) hold, the real shape is a plateau from 8–13 GB and a second
step up at ~30 GB — which is a different recommendation from "8 GB is enough".
That distinction rests entirely on two numbers nobody has read off the server, so
re-running those two to capture memory remains the highest-value small task.

**Read the two case groups separately.** C01–C13 are prose ticket analysis;
C14–C18 attach logs and Sentry telemetry. The headline Quality is a mean over both
and moves mostly with the telemetry cases, so it is not a good single number for
"can this model read a ticket". Quote the two columns.

## Runs still to do

Five of the eight Qwen3-VL Modelfiles (2B/4B/8B/32B × Instruct and Thinking) now
have usable scores; the 4B-Thinking and both 2B builds remain. Two things still limit what the
fleet can show:

- **Quantization.** The Instruct track is matched at Q4_K_M imatrix apart from the
  8B at Q3_K_M. The Thinking track runs three quants and the 32B has no imatrix,
  so no size has a quant-matched Instruct/Thinking pair. The 32B comparison above
  is the closest available — Q4_K_M imatrix against Q5_K_M plain — and note the
  direction: the Thinking build carries the *higher* quant, so quantization does
  not explain its loss.
- **Context per family.** Qwen2.5-VL runs at 32768 / 8192, Qwen3-VL Instruct at
  32768 / 8192 and Qwen3-VL Thinking at 49152 / 16384. The trained-window guard
  refuses a run above the model's own window.

Priorities, in order: **re-run the two 32B builds to capture their memory**, since
the whole value story now hangs on unmeasured numbers; then the 4B pair, which is
where a usable size curve would start to show.

---

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
| Falcon-H1-Tiny-90M-Instruct | 3.2 | 10 | Sonnet | Pre-C14, fewer cases |
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
8B lost 9; at 1.0 both lost none. Such a case is recorded as an error and scored 0,
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
