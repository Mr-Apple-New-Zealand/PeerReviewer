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

Eight models have been measured on the full eighteen cases with the judge of
record. Everything earlier is superseded — see below.

| Model | Quant | Temp | Quality | Coverage | C01–C13 | C14–C18 | Traps hit | Unsup | GB |
|---|---|---|---|---|---|---|---|---|---|
| **claude-sonnet-5** ¹ | — | n/a | **88.4 (87–91)** | **90%** | **93.6** | **74.9** | 4/162 | **13** | — |
| **Qwen3-VL-32B-Thinking** | Q5_K_M | 1.0 | **60.6 (60–61)** | 66% | 72.5 | 29.8 | **1/162** | 51 | — ² |
| Qwen3-VL-8B-Thinking-imatrix | Q4_K_M | 1.0 | 52.3 (48–54) | 60% | 62.9 | 24.7 | 7/162 | 59 | 13.0 |
| Qwen3-VL-8B-Instruct-imatrix | Q3_K_M | 0.3 | 49.7 (48–52) | 63% | 57.9 | 28.4 | 19/162 | 67 | **9.4** |
| Qwen2.5-VL-32B-Instruct | Q5_K_M | 0.3 | 49.2 (49–50) | 54% | 60.6 | 19.5 | 7/162 | 37 | 32.5 |
| Qwen2.5-VL-72B-Instruct | Q4_K_S | 0.3 | 45.6 (45–47) | 48% | 58.7 | 11.7 | 8/162 | 15 | 56.3 |
| Qwen2.5-VL-7B-Instruct-imatrix | Q4_K_S | 0.3 | 24.5 (23–25) | 31% | 33.4 | 1.3 | 17/162 | 39 | 7.1 |
| Qwen2.5-VL-3B-Instruct-imatrix | Q4_K_M | 0.3 | 14.4 (12–18) | 26% | 19.5 | 1.1 | 20/162 | 100 | 4.1 |

All judged by `Qwen3.8-27B-imatrix:Q4_K_S`, 18 cases, 3 repeats. Judge grounding
stayed acceptable: 0–3 ungrounded, 0–1 omitted.

¹ Hosted, so it has no resident GB and is outside the Pareto front, which needs
memory. Temperature is not sent (Claude rejects it) and `num_ctx` does not apply;
its times are wall clock including the network. It is a **reference ceiling**, not
a value comparison.

² **Not measured, and it should have been.** The `/api/ps` lookup after the first
case found no entry matching the tag, so run 44 has no footprint and is excluded
from the Pareto front. The harness now matches the tag case-insensitively and
records a note when the lookup misses, so this cannot recur silently — but the
figure for this run is simply lost. Expect roughly **35 GB**: ~23 GB of Q5_K_M
weights, ~1.4 GB of vision weights and 12 GiB of KV cache at `num_ctx` 49152.
Confirm it on the next run rather than quoting that estimate.

### A local model clears 60, and it is the most careful model on the board

`Qwen3-VL-32B-Thinking` at temperature 1.0 scores **60.6**, eight points above the
previous local best and the first local model to pass 60. Two things about it are
more interesting than the headline.

**It trips one trap in 162 — the best record of any model measured, Sonnet
included.** This is the first metric on which anything local has beaten the
reference:

| | 32B-Thinking | Sonnet | 8B-Thinking | 8B-Instruct |
|---|---|---|---|---|
| Traps tripped | **1/162** | 4/162 | 7/162 | 19/162 |
| Unsupported per analysis | 0.94 | **0.24** | 1.09 | 1.24 |

**Do not read that as trustworthiness.** The traps are deliberate invitations to
assert something the tickets do not support, and this model almost never takes
one. It still makes 51 unsupported claims — four times Sonnet's rate per analysis.
It is disciplined about the specific wrong answers the cases bait it with, and
ordinary about volunteering things it cannot support.

**Its run-to-run range is 60.2–60.9** — 0.7 points across three repeats, against
6.3 for the 8B-Thinking and 4.3 for Sonnet. That is a surprisingly tight spread
for a run at temperature 1.0 and worth a second look rather than a boast: with
three repeats it could be coincidence, and it is the kind of number that also
appears when repeats are not actually varying.

**It is not more verbose than the 8B.** 2,849 output tokens a case against the
8B-Thinking's 2,885 — the same reasoning budget, eight points better. The gain is
the quality of the thinking, not the amount.

**It is slow.** 109.1s a case at 28.4 tok/s, four times the 8B-Thinking's 26.6s,
and a full 54-case run takes about 100 minutes before judging. Against the 8B it
buys 8 points of quality and six fewer traps for 4× the time.

### The gap to the ceiling has closed by a quarter, and is still the story

Sonnet scores **88.4 against 60.6** — 27.8 points, down from 36.1 when the 8B led.
The composition still differs in kind, not degree:

| | Sonnet | 32B-Thinking | 8B-Thinking |
|---|---|---|---|
| Found (full credit) | **343 (81%)** | 180 (43%) | 147 (35%) |
| Partial (half credit) | 58 (14%) | 155 (37%) | 166 (39%) |
| Missed | **22 (5%)** | 88 (21%) | 110 (26%) |

The local leader's score is still carried by partial credit — it gestures at the
right answer more often than it makes it. But it misses a fifth fewer checkpoints
than the 8B (88 against 110) and makes 33 more outright (180 against 147), so the
gain is real points, not just more hedged ones.

### The telemetry cases are still the gap

C14–C18: **29.8** against Sonnet's 74.9. On the prose cases the spread is 93.6
against 72.5, a factor of 1.3; on logs and Sentry exports it is a factor of 2.5.
Reading machine output remains where the local fleet falls furthest behind, and
the 32B-Thinking's advance is mostly on prose — it adds 9.6 points on C01–C13 over
the 8B-Thinking and 5.1 on C14–C18.

C17 (a Sentry event whose headline error is the symptom, not the fault) is the
hardest case in the suite for everything: **17.9** here, 1.3 for the 8B-Thinking,
0–1 for the older fleet, and even Sonnet only reaches 58.9.

**Vision is now this model's weakest prose group**, not its strongest: C11 47.6,
C12 59.5, C13 61.9, against 72.5 across C01–C13. The 8B-Thinking scored 19.1 on
C13; at 32B that becomes 61.9, so the wordless-markup case scales with size — but
Sonnet's 97.6 shows how much is still on the table.

### Temperature 1.0 is confirmed at two sizes

The 8B-Thinking's empty-content failures at temperature 0.3 were a low-temperature
artefact, and the 32B run settles it. Both builds, same change:

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
longer forfeiting nine runs. The looping is a low-temperature artefact, exactly as
Qwen's guidance says, and raising `num_predict` is the wrong lever: more budget
buys more looping.

**Runs at different temperatures are now ranked together**, with the temperature
shown in its own column here and in the generated Runs table. `--compare` no longer
treats temperature as a comparability key. That is a deliberate loosening: a single
fleet temperature cannot suit both tracks, since the cards ask 0.7 on Instruct and
1.0 on Thinking, and 0.3 is below both. Read the Temp column before comparing two
rows closely — it is a real difference in what the model was asked to do, not a
free variable like `num_ctx`.

### Reasoning pays at 32B and not at 8B

With both Thinking builds at their card temperature, the reasoning track only earns
its cost at the larger size:

| | 8B-Instruct | 8B-Thinking | 32B-Thinking |
|---|---|---|---|
| Quality | 49.7 | 52.3 | **60.6** |
| C01–C13 | 57.9 | 62.9 | **72.5** |
| C14–C18 | **28.4** | 24.7 | 29.8 |
| Traps | 19/162 | 7/162 | **1/162** |
| Time a case | **7.3s** | 26.6s | 109.1s |

At 8B, reasoning buys 5 points of prose and *loses* 3.7 on telemetry for 3.6× the
time — the Instruct sibling is still the better model at that size for most uses.
At 32B it buys 14.6 points of prose over the 8B-Instruct and finally edges ahead on
telemetry too, for 15× the time.

**No comparison here isolates reasoning.** The quants differ at every size, and no
size has a quant-matched Instruct/Thinking pair — the 32B Instruct has not been
measured at all since its tag was found to hold Q3_K_M weights. Size, quant and
reasoning move together in this table.

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
right about more of it. **Choose on what sits behind the model.** For a pipeline
with a verification step, take the 8B's recall. For output a human reads and acts
on directly, take the 32B — a trap tripped is a confident false statement about a
ticket, and the 8B makes nearly three times as many.

### Memory has stopped predicting anything

Ordered by memory: 4.1 GB → 14.4, 7.1 GB → 24.5, 9.4 GB → **49.7**, 13.0 GB →
52.3, 32.5 GB → 49.2, 56.3 GB → 45.6. The curve rises steeply to about 13 GB and
is flat or falling above it.

The new leader would sit at roughly 35 GB if the estimate holds, which — if
confirmed — puts the first real quality gain above 13 GB on the board. Until it is
measured, the honest statement is unchanged: **nothing between 13 GB and 56 GB has
been shown to beat a 13 GB model**, and the run that might have is the one whose
footprint was not captured. Measuring it is the single cheapest thing that would
sharpen this section.

**Read the two case groups separately.** C01–C13 are prose ticket analysis;
C14–C18 attach logs and Sentry telemetry. The headline Quality is a mean over both
and moves mostly with the telemetry cases, so it is not a good single number for
"can this model read a ticket". Quote the two columns.

## Runs still to do

Of the eight Qwen3-VL Modelfiles (2B/4B/8B/32B × Instruct and Thinking), three now
have usable scores. Two things are worth settling before the rest, because they
decide whether the results can be compared with each other:

- **Quantization.** The Instruct track is nearly matched at Q4_K_M imatrix, with
  only the 8B at Q3_K_M. The Thinking track runs three different quants and the
  32B has no imatrix, so no Thinking size curve is available and no size has a
  quant-matched Instruct/Thinking pair. Standardising on Q4_K_M imatrix would
  fix both.
- **Context per family.** Qwen2.5-VL runs at 32768 / 8192, Qwen3-VL at 49152 /
  16384. The trained-window guard now refuses a run above the model's own
  window, so the 32768-window mistake that voided two runs cannot recur
  silently.

The **Qwen3-VL-32B-Instruct** run is the most valuable one outstanding: it is the
only way to tell how much of the leader's 60.6 is size and how much is reasoning,
and it should be quick by comparison — the 8B-Instruct runs in a tenth of the
Thinking build's time. Run the Thinking builds at temperature 1.0 and the Instruct
builds at 0.3.

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
| **`Qwen3.8-27B`** | **+1.0, −1.3** | 0–3 per run | 0–1 | **Judge of record** |
| `Gemma-4-31B` | +1.3 | 2 | 0 | Passes; no speed gain |
| `Qwen3.6-27B` | +8.8 | 0 | 9 | Lenient; runaway thinking |
| `Qwen3.5-9B` | +7.9 | **58** | 26 | Fabricates quotes |
| `Qwen3-Coder-30B` | — | **39** | 0 | Fabricates quotes |
| `minimax-m3:cloud` | — | 0 | — | Never completed a clean run |
| `Muse-Glimmer-30B` | — | — | — | Errors immediately |

The two Δ figures for Qwen3.8 are from independent runs (the Qwen3-VL-32B and
the Qwen2.5-VL-72B), both within about a point of Sonnet on the same 13 cases.

Its worst run so far is the Qwen3-VL-32B-Thinking at **3 ungrounded and 1
omitted** out of 423 checkpoints — under 1%, and an order of magnitude below the
judges that were rejected, but no longer the clean sheet the earlier runs showed.
Watch the per-run figure in the warnings list rather than assuming it.

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
| Qwen3-VL-32B-Instruct-imatrix | — | 18 | — | Judging failed twice; also Q3_K_M weights under a Q4_K_M tag |

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
decide on and read the range, not the midpoint. The 32B-Thinking's 0.7-point
range is the exception in the field and has not been explained.

**Time is not a property of the model.** The runner is shared, and a long run
usually overlaps with something else. The same 72B build measured 28s a case
idle and 55.2s with a judge and an embedding model resident, at an identical
56.31 GB. Memory holds up under contention; time does not, which is why time is
not a Pareto axis. Check the `On GPU` column: under 100% means the timings
measure spill.

**Memory can go unmeasured, and a run then leaves the Pareto front.** Run 44 has
no footprint because the `/api/ps` lookup found no entry for its tag. The lookup
is now case-insensitive and records a note when it misses, and the note appears in
the generated warnings — but check for a `GB` figure before treating a run as
complete. There is deliberately no fallback that assumes the only loaded model is
the one under test: that would report the judge's footprint as the analyst's.

**Thinking builds can return nothing.** Reasoning counts against `num_predict`,
and a model that runs out returns empty content with the text stranded in
`message.thinking`. At temperature 0.3 the 32B lost 3 of 54 cases that way and the
8B lost 9; at 1.0 both lost none. Such a case is recorded as an error and scored 0,
and is **not** retried — so a run can look complete while cases are missing. Read
the warnings list first, and run Thinking builds at the card's temperature.

**The telemetry cases are where the field separates.** Every local model is far
below the ceiling on C14–C18 — 29.8 at best against 74.9 — and C17 defeats
everything measured, Sonnet included at 58.9. That is what those cases were
written to do, and it means a model that looks mid-table on C01–C13 may be much
further behind on log and Sentry analysis.
