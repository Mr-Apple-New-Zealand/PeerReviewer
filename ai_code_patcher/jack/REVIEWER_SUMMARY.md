# Jack-27B vs Qwen3.8-27B — Reviewer Comparison

`hf.co/JackAgentLead/Jack-3.8-27B-Coder-16GB-VRAM:latest` against
`Qwen3.8-27B-imatrix:Q4_K_S` on the peer-review benchmark: find the 70 seeded defects in
`SampleBankingApp/`. Same review prompt (`82bd5f768ca9`), same `ISSUES.md` (`4b57cc34a7bb`),
same scorer (`Qwen3-Coder-30B-imatrix:Q3_K_M`), both at temperature 0 with `think: medium`.

Companion comparisons for the same model: [PATCHER_SUMMARY.md](PATCHER_SUMMARY.md) and
[SCORER_SUMMARY.md](SCORER_SUMMARY.md). Full reviewer field:
[../../ai_code_review_results/SUMMARY.md](../../ai_code_review_results/SUMMARY.md).

---

## Verdict

**Jack beats Qwen3.8-27B as a reviewer, by 6 points adjusted — and would be the best local
model in the field.** At 68 adjusted it places fifth overall, behind only the four cloud
models on 69 and ahead of `Qwen3.5-122B` (66) and `Qwen3.6-27B` (65).

**But its sheet has the zero-Partial signature**, and on ten previous occasions that pattern
cost 6–9 points on manual reading. Treat 68 as the optimistic end and 66 as the defensible
figure. Even at 66 it beats Qwen3.8-27B.

---

## Head to head

| | Jack-27B | Qwen3.8-27B |
|---|---|---|
| Raw | **70F / 0P / 0M** | 62F / 0P / 8M |
| **Adjusted Found** | **68** | 62 |
| Plausible floor | **66** | 62 |
| Precision | 95% (38 of 40) | **100% (38 of 38)** |
| Mis-credits | `N3`, `D5` | **none** |
| Self-hedged rows | `E6`, `RL3` | none |
| Grounding downgrades | **0** | 8 |
| Misaligned rows | **0** | **0** |
| Citations past EOF | **0 of 192** | **0 of 220** |
| Review time | 5m 26s | **5m 31s** |
| Output tokens | 14,529 | 12,312 |
| Answer / reasoning | 30,912 / 24,366 chars | 27,268 / 19,547 chars |

The two models are near-identical on cost — five and a half minutes, roughly 40 tok/s, no
truncation. The difference is entirely in what they found.

---

## Where Jack gains

**It claims all 70.** Qwen3.8-27B missed 8 outright. Even after the harness strips two
mis-credits and discounts two self-hedged rows, Jack is 4 ahead at its floor and 6 ahead
adjusted.

**Its grounding is cleaner.** Zero grounding downgrades against Qwen3.8-27B's 8 — every Note
Jack wrote could be matched back to its own review text. That is the check that catches a
scorer inventing evidence, and Jack gave it nothing to strip.

**It is genuinely thorough on the hard categories.** It identified 8 distinct SQL-injection
sites (including `DatabaseHelper.ExecuteQuery` as an injection vector for any caller), 16 dead
methods, and the `Transfer` balance check excluding the fee — with file and line for each.
192 citations, none past end of file.

---

## Where Jack loses

**Two genuine mis-credits**, both confirmed against its review text:

- `N3` — the reference issue is `SmtpPort` falling back to `"25"`. Jack's review discusses
  `new SmtpClient(_config["Email:SmtpHost"])` and the null risk on the *host*, never the port.
- `D5` — `BuildHtmlTemplate` is dead transitively via `SendWelcomeEmailHtml`. Jack found
  `SendWelcomeEmailHtml` and never named `BuildHtmlTemplate`.

In both cases the scorer credited a near neighbour. Qwen3.8-27B had none of these, which is
why its precision is 100% against Jack's 95%.

**Two self-hedged rows.** `E6` and `RL3` are both rated Found on a Note that reads *"calls
`connection.Close()` but does not `Dispose()`"* — the phrasing concedes a partial finding. The
harness flags these and sets the plausible floor at 66.

**One misattributed row worth noting.** `A1` (mutable static `_auditLog`) is credited on a
Note about `GetAuditReport` using `+=` in a loop — that is `A3`/string concatenation, not
static state. The review *does* separately identify `_auditLog` as unsynchronised static
state, so the finding is real; the scorer attached the wrong evidence to it.

---

## The zero-Partial caveat

Jack returned **70 Found, 0 Partial, 0 Missed**. That is the pattern the review benchmark
documents as the main source of inflation:

> *"On real reviews it produced ten sheets with zero Partial ratings that manual reading
> knocked 6–9 points off each."*

The harness caught 2 mis-credits and 2 hedges here, which is fewer corrections than a
70/0/0 sheet usually attracts — but the spot-check only covers the 40 rows with an
unambiguous target string, leaving 30 unaudited. `A1`'s misattribution was found by reading,
not by the automated checks, and there may be more of that kind.

Qwen3.8-27B's sheet is also zero-Partial, but it declined 8 issues outright rather than
crediting everything, which is the more conservative failure.

**Read Jack's result as 66–68, not 70.** At either end it beats Qwen3.8-27B's 62.

---

## Where this puts Jack in the field

| # | Model | Adjusted | Raw | Precision |
|---|---|---|---|---|
| 1= | claude-opus-5 | 69 | 69/0/1 | 100% (39) |
| 1= | claude-sonnet-5 | 69 | 70/0/0 | 98% (40) |
| 1= | kimi-k3 | 69 | 70/0/0 | 98% (40) |
| 1= | glm-5.2 | 69 | 70/0/0 | 98% (40) |
| **5** | **Jack-27B** | **68** | **70/0/0** | **95% (40)** |
| 6 | Qwen3.5-122B | 66 | 69/0/1 | 92% (39) |
| 7 | Qwen3.6-27B | 65 | 70/0/0 | 88% (40) |
| 8 | Muse-Glimmer-30B | 64 | 69/0/1 | 87% (39) |
| 9 | Qwen3.8-27B | 62 | 62/0/8 | 100% (38) |

At its floor of 66 it still places sixth, level with `Qwen3.5-122B` — a 122B model — on a
16GB-VRAM footprint.

---

## Recommendation

**As a reviewer, Jack replaces Qwen3.8-27B.** Six points adjusted, four at the floor, the same
runtime, cleaner grounding, and it fits in far less memory. The only column where Qwen3.8-27B
wins is precision, and it buys that by missing eight issues outright.

**Verify before adopting.** One run each, and Jack's zero-Partial sheet has 30 rows the
spot-check cannot audit. Reading its scorecard against the review — as was done for the
original twenty — would settle whether 68 or 66 is nearer the truth. The `A1` misattribution
turned up on the first pass through, which suggests a full reading would find more.

**Across all three roles**, Jack is now: best local **reviewer** (68 adjusted, this document),
a viable **scorer** but slower than the incumbent ([SCORER_SUMMARY.md](SCORER_SUMMARY.md)),
and a near-miss **patcher** at 39/41 with one missing package reference
([PATCHER_SUMMARY.md](PATCHER_SUMMARY.md)). Reviewing is where it is strongest.
