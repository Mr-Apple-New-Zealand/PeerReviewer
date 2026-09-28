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

Six runs have been measured on the full eighteen cases with the judge of
record. Everything earlier is superseded — see below.

| Model | Quant | Quality | Coverage | C01–C13 | C14–C18 | Traps hit | Unsupported | GB |
|---|---|---|---|---|---|---|---|---|
| **Qwen3-VL-8B-Instruct-imatrix** | Q3_K_M | **49.7 (48–52)** | **63%** | 57.9 | **28.4** | 19/162 | 67 | **9.4** |
| Qwen2.5-VL-32B-Instruct | Q5_K_M | 49.2 (49–50) | 54% | **60.6** | 19.5 | **7/162** | 37 | 32.5 |
| Qwen3-VL-8B-Thinking-imatrix ¹ | Q4_K_M | 47.3 (46–49) | 64% | 61.6 | 9.9 | 6/114 | 42 | 13.0 |
| Qwen3-VL-8B-Thinking-imatrix ² | Q4_K_M | *52.3 (48–54)* | 60% | 62.9 | 24.7 | 7/162 | 59 | 13.0 |
| Qwen2.5-VL-72B-Instruct | Q4_K_S | 45.6 (45–47) | 48% | 58.7 | 11.7 | 8/162 | **15** | 56.3 |
| Qwen2.5-VL-7B-Instruct-imatrix | Q4_K_S | 24.5 (23–25) | 31% | 33.4 | 1.3 | 17/162 | 39 | 7.1 |
| Qwen2.5-VL-3B-Instruct-imatrix | Q4_K_M | 14.4 (12–18) | 26% | 19.5 | 1.1 | 20/162 | 100 | 4.1 |

All judged by `Qwen3.8-27B-imatrix:Q4_K_S`, 18 cases, 3 repeats. Instruct builds
ran at num_ctx 32768 / num_predict 8192, the Thinking build at 49152 / 16384,
which it requires. Judge grounding stayed clean: 0–4 ungrounded, 0–1 omitted.

² Run at **temperature 1.0**, so it is excluded from the generated leaderboard and
italicised here — see below. It is the same build as ¹, and the better one.

¹ **The Thinking build lost 9 of its 54 runs to empty content**, so its figures are
not like-for-like — see below. Its traps are out of 114 rather than 162 for the
same reason.

### Generation beats size, by a wide margin

**A Qwen3-VL 8B at Q3_K_M matches a Qwen2.5-VL 32B at Q5_K_M, using a third of
the memory and carrying the worst quantization in the fleet.** It also beats the
72B, which needs six times its memory.

That comparison is loaded against the 8B in every respect except generation:
3 bits against 5, 9.4 GB against 32.5, 8B parameters against 32B. It still wins on
coverage and on the telemetry cases. Whatever changed between Qwen2.5-VL and
Qwen3-VL is worth more than any amount of the size or quantization this benchmark
has varied.

The corollary is that **this build is under-quantized on purpose and should be
rebuilt at Q4_K_M** - Q3_K_M was only ever defensible while it was paired with the
32B at the same quant, and it is now the one build holding the Instruct track back.
Expect it to go up.

### Temperature 1.0 fixes the Thinking build, and takes it off the board

Re-running the 8B Thinking at temperature 1.0 — the card's own value, against the
fleet's 0.3 — removed the failure completely:

| | temp 0.3 | temp 1.0 |
|---|---|---|
| Empty-content runs | **9 of 54** | **0** |
| Quality (delivered) | 47.3 | **52.3** |
| C01–C13 | 63.6 † | 62.9 |
| C14–C18 | 19.9 † | **24.7** |
| Traps | 6/114 | 7/162 |
| Ungrounded | 4 | 1 |
| Output tokens a case | 5,244 | **2,885** |
| Time a case | 53.1s | **26.6s** |

† over completed runs only, since 9 produced no analysis.

So the looping was a low-temperature artefact, exactly as Qwen's guidance says. At
1.0 it answers every case, halves its output and its time, and gains 5 points of
delivered quality. Note where the gain is: prose is unchanged at 62.9 against 63.6,
so the whole improvement is telemetry plus no longer forfeiting nine runs.

**52.3 would top the leaderboard, and it cannot be put there.** Temperature changes
what a model writes, so `--compare` excludes the run with
`different temperature 1.0 (ranked runs: 0.3)`. That is the tool being right:
unlike `num_ctx`, this is not a free variable.

**The decision it forces.** A single fleet temperature cannot suit both tracks — the
cards ask for 0.7 on Instruct and 1.0 on Thinking, and 0.3 is below both. The
consistent fix is to treat temperature the way `num_ctx` is already treated: a
per-track setting, with Instruct and Thinking builds compared within their own
track and never across it. Thinking builds already cannot share the Instruct memory
column, for the same reason.

Until that is settled, read 52.3 as this build's real capability and 47.3 as what it
delivers under the fleet's current convention.

### Reasoning did not pay for itself, and it failed where it was needed most

The Thinking build at Q4_K_M went into runaway reasoning on **9 of 54 runs**,
returning empty content after exhausting `num_predict`. Eight of the nine were
telemetry cases:

```
C15 x2   C17 x2   C18 x2   C14   C16   C10
```

Those score 0 and are not retried, so the delivered figures understate the model.
Over the 45 runs that completed:

| | As delivered | Completed runs only |
|---|---|---|
| Quality | 47.3 | 56.7 |
| C01–C13 | 61.6 | 63.6 |
| C14–C18 | 9.9 | 19.9 |

**Neither number flatters it against its own Instruct sibling.** On prose it
reaches 63.6 at best against the Instruct build's 57.9 — a real gain. On telemetry
it reaches 19.9 at best against the Instruct build's **28.4**, and it only achieves
that by not answering a third of those cases. Reasoning made it better at reading
tickets and worse at reading logs, which is the opposite of what the extra budget
was for.

It is also expensive: **5,244 output tokens a case against the Instruct build's
815, and 53.1s against 7.3s** — seven times the time and six times the tokens, for
a lower delivered score.

Raising `num_predict` is the wrong lever here; Qwen warns that thinking models loop
at low temperatures, and the fleet runs at 0.3 against a card value of 1.0. If this
build is worth revisiting, raise temperature toward 1.0 first — but on this evidence
the Instruct sibling is the better model at the same size, for a seventh of the
time.

### The top two are tied, but they are not the same model

49.7 against 49.2, with overlapping ranges, is a tie. The composition is not:

| | Qwen3-VL-8B | Qwen2.5-VL-32B |
|---|---|---|
| Coverage | **63%** | 54% |
| Traps tripped | 19/162 | **7/162** |
| Unsupported per analysis | 1.24 | **0.69** |
| C14–C18 | **28.4** | 19.5 |

The 8B finds substantially more and is wrong more often; the 32B finds less and is
right about more of it. **Choose on what sits behind the model.** For a pipeline
with a verification step, take the 8B's recall. For output a human reads and acts
on directly, take the 32B - a trap tripped is a confident false statement about a
ticket, and the 8B makes nearly three times as many.

### The telemetry cases finally move

C14–C18: **1.1, 1.3, 11.7, 19.5, 28.4** for the 3B, 7B, 72B, 32B and Qwen3-VL-8B.
The best score on log and Sentry analysis now comes from the smallest capable model
in the field, and it is nearly a third of the way to the ceiling rather than the
rounding error the small Qwen2.5-VL builds produced. This is where the generational
difference shows most clearly.

### Memory has stopped predicting anything

Ordered by memory: 4.1 GB → 14.4, 7.1 GB → 24.5, 9.4 GB → **49.7**, 32.5 GB →
49.2, 56.3 GB → 45.6. The curve rises steeply to 9 GB and is flat or falling above
it. On current evidence there is no reason to spend more than about 10 GB on this
job, provided the model is a recent one.

**Read the two case groups separately.** C01–C13 are prose ticket analysis;
C14–C18 attach logs and Sentry telemetry. The 72B — the strongest model
measured — scores 58.7 on the first group and 11.7 on the second. The headline
Quality is a mean over both, so it moves mostly with the telemetry cases and is
not a good single number for "can this model read a ticket". Quote the two
columns.

## Runs still to do

The Qwen3-VL fleet has Modelfiles for eight builds (2B/4B/8B/32B × Instruct and
Thinking) and none has a usable score. Two things are worth settling first,
because they decide whether the results can be compared with each other:

- **Quantization.** The Instruct track is nearly matched at Q4_K_M imatrix, with
  only the 8B at Q3_K_M. The Thinking track runs three different quants and the
  32B has no imatrix, so no Thinking size curve is available and no size has a
  quant-matched Instruct/Thinking pair. Standardising on Q4_K_M imatrix would
  fix both.
- **Context per family.** Qwen2.5-VL runs at 32768 / 8192, Qwen3-VL at 49152 /
  16384. The trained-window guard now refuses a run above the model's own
  window, so the 32768-window mistake that voided two runs cannot recur
  silently.

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
| **`Qwen3.8-27B`** | **+1.0, −1.3** | 1, then 0 | 0 | **Judge of record** |
| `Gemma-4-31B` | +1.3 | 2 | 0 | Passes; no speed gain |
| `Qwen3.6-27B` | +8.8 | 0 | 9 | Lenient; runaway thinking |
| `Qwen3.5-9B` | +7.9 | **58** | 26 | Fabricates quotes |
| `Qwen3-Coder-30B` | — | **39** | 0 | Fabricates quotes |
| `minimax-m3:cloud` | — | 0 | — | Never completed a clean run |
| `Muse-Glimmer-30B` | — | — | — | Errors immediately |

The two Δ figures for Qwen3.8 are from independent runs (the Qwen3-VL-32B and
the Qwen2.5-VL-72B), both within about a point of Sonnet on the same 13 cases.

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
effort, judge prompt, analyst prompt, temperature and system-prompt mode.
Anything else is listed under "Not ranked" with the reason. `num_ctx`,
`num_predict` and `repeats` may differ.

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
| Qwen3-VL-32B-Thinking:Q5_K_M | 64.8 | 18 | Qwen3-Coder-30B | Judge produced 39 ungrounded verdicts |
| Qwen3-VL-32B-Instruct-imatrix | — | 18 | — | Judging failed twice; also Q3_K_M weights under a Q4_K_M tag |

Two further Qwen2.5-VL-32B runs were made at num_ctx 49152 and 65536, above that
model's 32768 trained window. Their judge verdicts are valid but their analyst
scores are not, and they are not listed.

---

## Caveats specific to these results

**Per-case variance is 15–25 points** at temperature 0.3, measured across 3
repeats. The aggregate averages most of it out — quality ranges come in at ±2–3
— but a single case score means little. Use `repeats: 3` for anything you will
decide on and read the range, not the midpoint.

**Time is not a property of the model.** The runner is shared, and a long run
usually overlaps with something else. The same 72B build measured 28s a case
idle and 55.2s with a judge and an embedding model resident, at an identical
56.31 GB. Memory holds up under contention; time does not, which is why time is
not a Pareto axis. Check the `On GPU` column: under 100% means the timings
measure spill.

**Thinking builds can return nothing.** Reasoning counts against `num_predict`,
and a model that runs out returns empty content with the text stranded in
`message.thinking`. The Qwen3-VL-32B-Thinking run lost 3 of 54 cases that way,
dropping its mean from 68.6 to 64.8. Such a case is recorded as an error and
scored 0, and is **not** retried — so a run can look complete while cases are
missing. Read the warnings list first. If it happens, raise temperature toward
the card's value rather than raising `num_predict`.

**The telemetry cases are where the field separates.** Every model measured so
far is near the floor on C14–C18, including the 72B at 11.7. That is what those
cases were written to do, and it means a model that looks mid-table on C01–C13
may be indistinguishable from the smallest build on log and Sentry analysis.
