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

Four runs have been measured on the full eighteen cases with the judge of
record. Everything earlier is superseded — see below.

| Model | Quant | Quality | C01–C13 | C14–C18 | Traps hit | Unsupported | Resident GB |
|---|---|---|---|---|---|---|---|
| **Qwen2.5-VL-32B-Instruct** | Q5_K_M | **49.2 (49–50)** | **60.6** | **19.5** | 7/162 | 37 | 32.5 |
| Qwen2.5-VL-72B-Instruct | Q4_K_S | 45.6 (45–47) | 58.7 | 11.7 | 8/162 | 15 | 56.3 |
| Qwen2.5-VL-7B-Instruct-imatrix | Q4_K_S | 24.5 (23–25) | 33.4 | 1.3 | 17/162 | 39 | 7.1 |
| Qwen2.5-VL-3B-Instruct-imatrix | Q4_K_M | 14.4 (12–18) | 19.5 | 1.1 | 20/162 | 100 | 4.1 |

All judged by `Qwen3.8-27B-imatrix:Q4_K_S`, 18 cases, 3 repeats, num_ctx 32768 /
num_predict 8192. Judge grounding was clean throughout: 0, 0, 1 and 1 ungrounded,
0 omitted.

The 72B run (harness `980b243`) records `judge_num_predict` 16384 rather than the
40960 `JUDGE_DEFAULTS` specifies, because at that commit the table could not
override an argparse default; fixed in `826515e`. It had no judge failures, so its
scores stand.

### The 32B beats the 72B, and the quant is why that is not conclusive

The 32B leads on every quality measure — Quality, both case groups, traps tripped —
at **58% of the memory**. It is also the first model to make real progress on the
telemetry cases, at 19.5 against the 72B's 11.7.

**But the 32B is Q5_K_M and the 72B is Q4_K_S, so the smaller model carries the
more generous quantization.** Nothing here separates "a 32B is better at this job
than a 72B" from "Q5_K_M is better than Q4_K_S". Both readings fit the data. To
settle it, one of the two needs rebuilding to match the other - the 72B at Q5_K_M
would be ~70 GB resident at 32768, which the server can hold.

Either way the practical conclusion stands: **the 32B is the model to use**, and
24 GB of memory bought nothing.

### Unsupported claims fall with size, but not smoothly

| Model | GB | C01–C13 | Unsupported per analysis | Traps |
|---|---|---|---|---|
| 3B | 4.1 | 19.5 | 1.85 | 20 |
| 7B | 7.1 | 33.4 | 0.72 | 17 |
| 32B | 32.5 | 60.6 | 0.69 | 7 |
| 72B | 56.3 | 58.7 | 0.28 | 8 |

The direction holds - a 3B asserts something the tickets do not support roughly
twice per analysis, the 72B once every four - but the 7B and 32B are level at about
0.7 despite 27 points of quality between them. So unsupported claims track size
rather than competence: the 32B is far more useful than the 7B while being no more
careful about what it asserts. Traps tell the cleaner story, falling 20 → 17 → 7.

### The telemetry cases only open up above 30 GB

C14–C18 scores: **1.1, 1.3, 19.5, 11.7** for the 3B, 7B, 32B and 72B. The two small
models are indistinguishable from zero; the two large ones are merely poor. Reading
logs and Sentry exports does not degrade gracefully with size - below some threshold
it is absent, and the threshold sits between 7 GB and 32 GB.

### Memory buys nothing above 32 GB, on this evidence

3 GB (4.1 → 7.1) adds 14 points of C01–C13. The next 25 GB adds 27 points. The 24 GB
after that **loses** 2 points. The curve flattens and then turns over, though the
quant difference at the top is the obvious alternative explanation.

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
