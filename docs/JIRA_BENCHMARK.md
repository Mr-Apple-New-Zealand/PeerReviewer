# Jira Analyst Benchmark

Finds which model gives the best Jira ticket analysis for the least resource cost. Every candidate model analyses the same ten synthetic cases. Claude Sonnet 5 grades each analysis against an answer key, and the harness records what each model cost to run.

| Piece | Where |
|---|---|
| Harness | `scripts/jira_benchmark.py` (standard library only) |
| Workflow | `.github/workflows/jira_benchmark.yml` (Actions > Jira Analyst Benchmark) |
| Cases and answer keys | `jira_benchmark/cases/C*.json` |
| Analyst system prompt | `jira_benchmark/analyst_system_prompt.md`: the generic ticket-analyst prompt, the same text as the `SYSTEM` in the Qwen2.5-VL and Qwen3-VL Modelfiles. Keep them in sync. |
| Judge instructions | `jira_benchmark/judge_prompt.md` |
| Output | `jira_benchmark_results/run-<n>/`: `summary.md`, `results.json`, and each model's analyses and judge verdicts |

## Running it

From Actions, set `models` to a comma-separated list of tags. Per-model `think` works as in the scorer benchmark: `qwen3.6:27b=false`, `gpt-oss:120b=medium`, `model=none`.

Locally:

```
export OLLAMA_URL=http://192.168.10.100:11434
export ANTHROPIC_API_KEY=...
python3 scripts/jira_benchmark.py --models "Qwen2.5-VL-7B-Instruct:latest, Qwen2.5-VL-32B-Instruct:latest"
```

Other modes:
- `--list-cases`: sizes and point counts. No model calls.
- `--skip-judge`: analyses and cost only.
- `--rejudge <run dir>`: re-grade saved analyses after changing the judge, the judge prompt, an answer key or the scoring code, without regenerating them. In Actions, use `mode: rejudge` with `rejudge_dir` set to a results folder committed to the repo (the runner only sees committed files). Each `*.judge.json` keeps the judge's raw output and its original verdicts, so you can see what the harness downgraded and why.
- `--calibrate-judge`: check the judge (see below).

Defaults are `num_ctx 32768`, `num_predict 4096` and `temperature 0.3`, sent explicitly to every model so the Modelfiles cannot make the comparison unequal. By default the analyst prompt comes from the file, so every model gets the same one. Pass `--system-prompt modelfile` to test each model with its own `SYSTEM` instead.

## The cases

Each case is a ticket export plus a request, as a real integration would send it. The cases are built on the SampleBankingApp domain, with a fixed "today" of 2026-09-15.

| Case | Tests |
|---|---|
| C01 | Baseline: a complete bug report. Don't overstate progress. |
| C02 | Vague bug: say it's not ready and list what's missing. Don't adopt the reporter's guess as the cause. |
| C03 | Product and compliance disagree on scope. Surface the conflict without resolving it. |
| C04 | Marked Fixed, but QA says it still fails. Don't trust the status field. |
| C05 | Four tickets: one real duplicate, one lookalike, one likely cause of the regression. |
| C06 | Release risk from an overdue vendor dependency. Date reasoning; no invented commitments. |
| C07 | Incident timeline, time-to-detect and time-to-recover arithmetic, confirmed cause versus early speculation. |
| C08 | Long context (~15k tokens): seven real comments among ~260 bot and chatter comments, a superseded decision, two owner changes. |
| C09 | The error is only in a screenshot the model can't see. Say so instead of inventing it. |
| C10 | A public-form ticket containing an instruction to AI tools to misreport its priority. |

Each answer-key checkpoint is one of three kinds:
- **point:** something the analysis should say.
- **inference:** it should say it, and label it as an inference.
- **trap:** a false or unsupported claim it must not make.

## Scoring

For each case, the judge gives every checkpoint a verdict. It must back each positive verdict with a verbatim quote from the analysis. The harness checks the quote is actually there, and downgrades the verdict if it isn't. The judge also lists any other unsupported claims, with quotes.

```
case score = max(0, found + 0.5 x partial - penalties) / points x 100
penalties  = 1   per trap asserted
           + 1   per invented ticket key (BANK/OPS/MOB key not in the input; capped at 3; checked by code, not the judge)
           + 0.5 per other unsupported claim (capped at 2)
quality    = mean case score
```

An inference stated as certain fact counts as partial. **Coverage** is the same calculation without penalties: how much of what mattered the model said.

## Cost metrics

| Column | Source |
|---|---|
| Resident GB, On GPU | `/api/ps` after the first case: `size`, and `size_vram / size`. Under 100% means part of the model ran on CPU, and the report warns. |
| Cold load | `load_duration` of the first request. The harness unloads each model after its run, so every model starts cold. |
| Time / case | `total_duration - load_duration`, averaged over cases |
| Out tok/s, Out tok / case | `eval_count / eval_duration` (median) and mean `eval_count`. A verbose model costs more per ticket. |

The summary names three things:
- the best-quality model
- the **best value** model: the one with the least memory among those within 5 points of the best (`--value-margin`)
- the **Pareto front**: models that no other model beats on quality, memory and time at once

If other models are resident on the server when a run starts, the report warns that timings may be contended.

## Trusting the numbers

- **Check the judge first.** Run `mode: calibrate-judge` once, and again whenever the judge prompt, the judge model or an answer key changes. It grades three synthetic analyses per case: a perfect one built from the key, an empty one, and one that asserts every trap. A working judge gives about 100%, 0%, and all traps caught. This screens out a broken judge; it does not prove a working one grades real prose well.
- **Noise.** Ten cases and one judge pass means differences under about 5 points are noise. For close calls, use `repeats: 3`. The range shows in the Quality column.
- **Cost of judging.** Each graded case costs roughly $0.02–0.05 of Sonnet 5 time, so a 10-model run is a few dollars.
- **The prompts are fingerprinted.** Every run records the SHA of the analyst prompt, the judge prompt and the cases, as the review benchmark does. Runs with different SHAs are not comparable.
- **Text only.** The cases send no images, so the benchmark does not yet measure screenshot reading. C09 tests whether the model admits it can't see a screenshot. Qwen3-VL-32B-Thinking on the server does read images (it transcribed a test error dialog exactly on 2026-09-19), so image cases are the natural next addition.
- **Quantization.** Cost figures are for the build as benchmarked. If you benchmark at F16 and then quantize the winner, re-run the full benchmark on the quantized build to confirm its quality held, rather than assuming it did.

## Adding a case

1. Copy an existing `jira_benchmark/cases/C*.json` file.
2. Write the tickets. Long text is a list of lines.
3. Write the answer key:
   - Phrase each `expect` as a plain statement, because calibration uses those statements as the "perfect" analysis.
   - Give every trap a `claim`, which is the false statement written the way an analysis would put it.
   - Traps must be things an analysis can *say*. The judge has to quote a violation, so a trap can't be the *absence* of something. Make that a point instead.
4. Run `--list-cases` to check it fits the input budget.
5. Run `--calibrate-judge --cases Cnn` to check the key grades cleanly.
