# Jack-27B — Overall Assessment

`hf.co/JackAgentLead/Jack-3.8-27B-Coder-16GB-VRAM:latest`, measured in all three roles the
benchmark covers: finding defects, grading a review, and fixing code. Compared throughout
against `Qwen3.8-27B-imatrix:Q4_K_S`, which its name suggests it derives from, and placed
against the twenty models already tested.

Detail: [REVIEWER_SUMMARY.md](REVIEWER_SUMMARY.md) ·
[SCORER_SUMMARY.md](SCORER_SUMMARY.md) · [PATCHER_SUMMARY.md](PATCHER_SUMMARY.md)

---

## At a glance

| Role | Result | Against Qwen3.8-27B | Rank in field |
|---|---|---|---|
| **Reviewer** | 68 adjusted (66 floor) | **+6** (62) | **5th of 21** — best local |
| **Scorer** | 100.0%, 0 ungrounded, 4 misaligned | **beats it on both differentiators** | joint 1st on score; ~7th on speed |
| **Patcher** | 39/41, **build fails** | **−2 markers, and it doesn't compile** | 7th on markers, outside the compiling set |

It is the strongest all-round local model tested, and it wins no role outright.

---

## What it is better at

**Finding defects — clearly.** 68 adjusted against Qwen3.8-27B's 62, and it claims all 70
where the incumbent misses 8 outright. Zero grounding downgrades against 8: every note it
wrote traced back to its own review text. It found 8 distinct SQL-injection sites, 16 dead
methods, and the `Transfer` balance check that excludes the fee, each with file and line.

**Producing auditable scorecards.** 4 misaligned rows against Qwen3.8-27B's 47. A misaligned
row is one where the scorer paraphrased the issue instead of reproducing it, and paraphrase is
what makes a scorecard hard to check by eye. This is the specific reason Qwen3.8-27B was never
adopted as scorer; Jack removes the objection.

**Throughput, in every role.**

```
patching   44.9 tok/s   against 23.8    — 8m 30s vs 12m 9s despite more output
scoring    47.5 tok/s   against 38.9    — 2m 48s vs 3m 21s
reviewing  46.2 tok/s   against 38.2    — same wall clock, more tokens
```

**Memory, if the name is accurate.** Qwen3.8-27B needs ~33GB at 64k context. A model of this
quality inside 16GB would be the most useful result here — but see Considerations.

---

## What it is worse at

**Patching. It does not compile.** One error, and a characteristic one:

```
CS0103  AuthService.cs:98  The name 'KeyDerivation' does not exist in the current context
```

It replaced the MD5 hashing with ASP.NET Core's PBKDF2 helper — a better fix than most of the
field attempted — without adding the package reference or the `using`. Right idea, half
applied. It also left `CF7` (debug symbols in Release) and `R3` (`GenerateJwtToken` unsplit),
both of which Qwen3.8-27B fixed, and never touched `AuthController.cs`.

**Review precision.** 95% against 100% — two genuine mis-credits, both verified against its
own text. `N3` concerns `SmtpPort`; Jack discusses `SmtpHost` and never the port. `D5` is
`BuildHtmlTemplate`; Jack names `SendWelcomeEmailHtml` and never the helper. In both cases the
scorer credited a near neighbour.

**Speed as a scorer, against the model that matters.** It is faster than Qwen3.8-27B but 5.6×
slower than the incumbent: 2m 48s against 30s. The scorer runs twice per patch evaluation, so
a twenty-model sweep becomes 100 minutes instead of 20.

---

## Considerations

**One run in each role.** Everything here rests on three measurements. The benchmark has shown
repeatedly that this is thin: Qwen3.8-27B produced two materially different patches across
backend restarts, one compiling and one not; repeat runs of a single patcher varied by 7
points on the review delta.

**The zero-Partial signature on its review.** Jack returned 70 Found / 0 Partial / 0 Missed.
The review benchmark documents ten earlier sheets with that shape losing 6–9 points on manual
reading. The automated checks caught 2 mis-credits and 2 hedges, but they only audit the 40
rows with an unambiguous target string — 30 are unchecked. Reading found one more the checks
missed: `A1` credited on evidence belonging to `A3`. **Read its review score as 66–68, not 70.**

**The 16GB claim is unverified.** It comes from the model name. Nothing in this benchmark
measured its footprint, and the review-benchmark RAM figures were computed from weights and KV
cache for the other models, not for this one. If it does fit in 16GB the practical case
strengthens considerably; that needs measuring before it is relied on.

**The patcher failure is one line.** Adding `Microsoft.AspNetCore.Cryptography.KeyDerivation`
would likely give 39/41 with a clean build — fifth in the patcher field, level with
`Muse-Glimmer-30B` and faster. Worth a re-run before concluding it cannot patch.

---

## Global perspective

**As a reviewer** it is the best local model tested, and only the four cloud models beat it:

| # | Model | Adjusted | | # | Model | Adjusted |
|---|---|---|---|---|---|---|
| 1= | claude-opus-5 / sonnet-5 / kimi-k3 / glm-5.2 | 69 | | 6 | Qwen3.5-122B | 66 |
| **5** | **Jack-27B** | **68** | | 7 | Qwen3.6-27B | 65 |
| | | | | 9 | Qwen3.8-27B | 62 |

At its floor of 66 it still matches a 122B model.

**As a scorer** it joins the eleven models that score 100.0%, with a clean sheet (0
ungrounded) and near-perfect alignment. On speed it would sit around seventh — between
`kimi-k3` (145s) and `Qwen3.8-27B` (201s), far behind `glm-5.2` (25.6s) and the incumbent
`Qwen3-Coder-30B` (30s). The score does not separate this group; speed and alignment do, and
Jack is good on one and middling on the other.

**As a patcher** its 39/41 ties `Muse-Glimmer-30B`, `glm-5.2` and `MiniMax-M2.7`, behind only
the two 27B leaders (41/41) and `claude-opus-5`/`kimi-k3` (40/41). But seven models produced
code that builds and Jack is not among them, which in this benchmark is the line that matters:

```
compiles:  Qwen3.8-27B 41 · Qwen3.6-27B 41 · claude-opus-5 40 · kimi-k3 40
           Muse-Glimmer 39 · glm-5.2 39 · Gemma-4-31B 37
fails:     Jack-27B 39 · MiniMax-M2.7 39 · Qwen3.5-122B 37 · …
```

---

## Recommendation

**Adopt it as the reviewer, replacing Qwen3.8-27B** — after one confirming run and a read of
its scorecard against its review. Six points adjusted, four at the floor, same wall clock,
cleaner grounding. Qwen3.8-27B's only advantage is precision, and it buys that by declining
eight issues rather than judging them.

**Do not adopt it as the scorer.** `Qwen3-Coder-30B` grades identically in a fifth of the
time. Keep Jack in mind for a second opinion on a contested scorecard, where its 4-versus-47
alignment advantage over Qwen3.8-27B makes it the better of the two to read.

**Do not adopt it as the patcher yet.** Fix the `KeyDerivation` import and re-run; if it then
compiles at 39/41 it becomes a serious option, particularly given the speed and the memory
claim. As measured, the two 27B leaders produce working code and it does not.

**The broader point.** Jack is the only model tested that is credible in all three roles at
once — top-five reviewer, flawless scorer, near-top patcher. Every other model is strong in
one and mediocre in another: `Qwen3-Coder-30B` is the best scorer and a poor reviewer (34
adjusted); `Qwen3.8-27B` is the best patcher and the weakest of the strong reviewers. If a
single local model has to fill every seat, this is the first serious candidate — and the
qualifier is that "credible in three roles" is being inferred from one run in each.
