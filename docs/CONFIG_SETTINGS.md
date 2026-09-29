# Configuration settings

Per-model settings and footprints for the PeerReviewer benchmark.

## Model footprints

Weights are the on-disk size reported by the Ollama host. Resident is weights
plus the KV cache at `num_ctx: 65536`, computed from each model's own
architecture metadata rather than estimated - the calculation reproduces the two
figures that were measured by hand (`Qwen3.5-9B` and `Muse-Glimmer-30B`) to
within 0.1 GB.

The GGUF column is the source file each Ollama model was built `FROM`; the tag
is what you actually pull and run.


| Model              | Source GGUF                                   | Ollama tag                             | Weights | Resident @64k | Cloud hosted |
| ------------------ | --------------------------------------------- | -------------------------------------- | ------- | ------------- | ------------ |
| `MiniMax-M3`       | n/a - hosted API                              | `minimax-m3:cloud`                     | n/a     | n/a           | yes          |
| `claude-opus-5`    | n/a - hosted API                              | `claude-opus-5`                        | n/a     | n/a           | yes          |
| `claude-sonnet-5`  | n/a - hosted API                              | `claude-sonnet-5`                      | n/a     | n/a           | yes          |
| `kimi-k3`          | n/a - hosted API                              | `kimi-k3`                              | n/a     | n/a           | yes          |
| `glm-5.2`          | n/a - hosted API                              | `glm-5.2`                              | n/a     | n/a           | yes          |
| `glm-5.3`          | n/a - hosted API                              | `glm-5.3:cloud`                        | n/a     | n/a           | yes          |
| `Qwen3.5-122B`     | Qwen3.5-122B-A10B-f16-imatrix:Q4_K_S.gguf     | `Qwen3.5-122B-imatrix:Q4_K_S`          | 69.7 GB | 76.1 GB       | no           |
| `Qwen3.6-27B`      | Qwen3.6-27B-f16:Q4_K_S.gguf                   | `Qwen3.6-27B:Q4_K_S`                   | 15.8 GB | 33.3 GB       | no           |
| `Muse-Glimmer-30B` | Muse-Glimmer-30B-imatrix:Q4_K_S               | `Muse-Glimmer-30B-imatrix:Q4_K_S`      | 16.1 GB | **19.6 GB**   | no           |
| `Qwen3.8-27B`      | Qwen3.8-27B-f16-imatrix:Q4_K_S.gguf           | `Qwen3.8-27B-imatrix:Q4_K_S`           | 15.8 GB | 33.3 GB       | no           |
| `gpt-oss-120B`     | gpt-oss-120B-f16.gguf                         | `gpt-oss:120b`                         | 65.4 GB | 70.2 GB       | no           |
| `Qwen3-Coder-Next` | Qwen3-Coder-Next-f16-imatrix:Q5_K_S.gguf      | `Qwen3-Coder-Next-imatrix:Q5_K_S`      | 55.0 GB | 61.4 GB       | no           |
| `MiniMax-M2.7`     | MiniMax-M2.7-bf16:Q3_K_S.gguf                 | `MiniMax-M2.7:Q3_K_S`                  | 98.7 GB | 115.3 GB      | no           |
| `Qwen3.5-4B`       | Qwen3.5-4B-f16-imatrix:Q5_K_S.gguf            | `Qwen3.5-4B-imatrix:Q5_K_S`            | 3.0 GB  | 11.6 GB       | no           |
| `Gemma-4-31B`      | Gemma-4-31B-it-f16-imatrix:Q4_K_M.gguf        | `Gemma-4-31B-it-imatrix:Q4_K_M`        | 18.7 GB | **22.7** ¹    | no           |
| `Qwen3.5-9B`       | Qwen3.5-9B-f16-imatrix:Q4_K_S.gguf            | `Qwen3.5-9B-imatrix:Q4_K_S`            | 5.4 GB  | **14.0 GB**   | no           |
| `Qwen3-Coder-30B`  | Qwen3-Coder-30B-imatrix:Q3_K_M                | `Qwen3-Coder-30B-imatrix:Q3_K_M`       | 14.7 GB | 21.2 GB       | no           |
| `Devstral-2-123B`  | Devstral-2-123B-Instruct-2512-f16:Q4_K_M.gguf | `Devstral-2-123B-Instruct-2512:Q4_K_M` | 74.9 GB | 98.5 GB       | no           |
| `Qwen3-32B`        | Qwen3-32B-f16-imatrix:Q4_K_M.gguf             | `Qwen3-32B-imatrix:Q4_K_M`             | 19.8 GB | 36.9 GB       | no           |
| `Qwen3.5-2B`       | Qwen3.5-2B-f16-imatrix:Q4_K_S.gguf            | `Qwen3.5-2B-imatrix:Q4_K_S`            | 1.2 GB  | 4.4 GB        | no           |
| `Codestral-22B`    | Codestral-22B-f16-imatrix:Q4_K_S.gguf         | `Codestral-22B-imatrix:Q4_K_S`         | 12.7 GB | 27.7 GB       | no           |
| `Qwen3.5-0.8B`     | Qwen3.5-0.8B-f16-imatrix:Q4_K_S.gguf          | `Qwen3.5-0.8B-imatrix:Q4_K_S`          | 0.5 GB  | 3.7 GB        | no           |


**Bold** figures were measured directly; the rest are computed.

¹ `Gemma-4-31B` uses sliding-window attention with a 1,024-token window, and its
metadata reports no `head_count_kv`, so the formula above does not apply. Its KV
cache does not grow with context the way the others do, and the real figure will
be well below what a naive calculation gives. It needs measuring by loading the
model and reading `/api/ps`.

**Now measured: 22.68 GB at num_ctx 49152**, with the vision projector imported
(run 52, 2026-09-29). Weights are 18.7 GB and the vision encoder ~1.1 GB, so cache
and overhead come to roughly 2.9 GB — against the ~14 GiB a uniform 60-layer model
would need at that context. The prediction that the real figure would be far below
a naive calculation was right, by a factor of about five. The figure in the table
is at 49152, not the 65536 the rest of the column uses; the difference is small
here because only the global layers hold a context-length cache.

Confirmed from `ollama show` on 2026-09-29: architecture `gemma4`, 30.7B
parameters, **context length 262144** — so no benchmark setting will come near its
trained window. Its capabilities are `completion`, `tools` and `thinking`, and
**not `vision`**. That is fine for the judge role, which never receives images, but
as an analyst it would score 0 on C11, C12 and C13 — 35 of 195 checkpoints. Adding
vision would mean rebuilding with the mmproj projector as a second `FROM` line, the
way the Qwen3-VL Modelfiles do.

### What the numbers show

**The KV cache, not the weights, decides what fits.** `Muse-Glimmer-30B` and
`Qwen3.8-27B` have almost identical weights - 16.1 GB against 15.8 GB - and
differ by **13.7 GB** resident, because Muse needs 3.5 GB of KV cache at 64k
where Qwen3.8 needs 17.4 GB. That single fact is why Muse-Glimmer is the only
sub-20GB model in the benchmark that produced a patch which compiles.

**Small models are dominated by their cache.** `Qwen3.5-4B` is 3.0 GB of weights
and 11.6 GB resident; `Qwen3.5-0.8B` is 0.5 GB and 3.7 GB. Below about 9B, the
context window costs more than the model does.

**Halving the context roughly halves the gap.** The 27B Qwen models need ~33 GB
at 64k and about 20 GB at 16k. Where a review fits in 16k, that is the difference
between a server and a laptop.

## Sampler settings

Every model received `num_ctx: 65536`, `num_predict: 40000` and `temperature: 0`.
`think` is blank where the request omitted it, so the model's own Modelfile
applied.

```text
Model name                           | num_ctx | num_predict | think  | temperature
------------------------------------------------------------------------------------------------------------------
claude-opus-5                        | 65536   | 40000       | blank  | 0          
claude-sonnet-5                      | 65536   | 40000       | blank  | 0          
Codestral-22B-imatrix:Q4_K_S         | 65536   | 40000       | blank  | 0          
Devstral-2-123B-Instruct-2512:Q4_K_M | 65536   | 40000       | blank  | 0          
Gemma-4-31B-it-imatrix:Q4_K_M        | 65536   | 40000       | blank  | 0          
glm-5.2                              | 65536   | 40000       | blank  | 0        
gpt-oss:120B                         | 65536   | 40000       | blank  | 0          
Kimi-k3                              | 65536   | 40000       | blank  | 0        
MiniMax-M2.7:Q3_K_S                  | 65536   | 40000       | blank  | 0          
minimax-m3:cloud                     | 65536   | 40000       | blank  | 0          
Muse-Glimmer-30B-imatrix:Q4_K_S      | 65536   | 40000       | blank  | 0          
Qwen3-32B-imatrix:Q4_K_M             | 65536   | 40000       | blank  | 0          
Qwen3-Coder-30B-imatrix:Q3_K_M       | 65536   | 40000       | blank  | 0          
Qwen3-Coder-Next-imatrix:Q5_K_S      | 65536   | 40000       | blank  | 0          
Qwen3.5-0.8B-imatrix:Q4_K_S          | 65536   | 40000       | false  | 0          
Qwen3.5-2B-imatrix:Q4_K_S            | 65536   | 40000       | false  | 0          
Qwen3.5-4B-imatrix:Q5_K_S            | 65536   | 40000       | false  | 0          
Qwen3.5-9B-imatrix:Q4_K_S            | 65536   | 40000       | false  | 0          
Qwen3.5-122B-imatrix:Q4_K_S          | 65536   | 40000       | blank  | 0          
Qwen3.6-27B:Q4_K_S                   | 65536   | 40000       | medium | 0          
Qwen3.8-27B-imatrix:Q4_K_S           | 65536   | 40000       | medium | 0          
```



# Jira ticket analyst config details

Temperature is per track, not per fleet: the Instruct cards ask 0.7 and the
Thinking cards 1.0, and a single value cannot suit both. **Thinking builds run at
1.0** - at 0.3 they loop until `num_predict` runs out and return empty content,
which cost the 8B 9 of 54 cases and the 32B 3 of 54. **Instruct builds run at
0.3**, where no such failure has been seen. `--compare` ranks runs at different
temperatures side by side and shows the value in its own column.

```text
Model name                              | num_ctx | num_predict | temperature | repeats
Qwen2.5-VL-72B-Instruct:Q4_K_S          | 32768   | 8192        | 0.3         | 3
Qwen2.5-VL-32B-Instruct:Q5_K_M          | 32768   | 8192        | 0.3         | 3
Qwen2.5-VL-7B-Instruct-imatrix:Q4_K_S   | 32768   | 8192        | 0.3         | 3
Qwen2.5-VL-3B-Instruct-imatrix:Q4_K_M   | 32768   | 8192        | 0.3         | 3
Qwen3-VL-32B-Instruct-imatrix:Q4_K_M    | 32768   | 8192        | 0.3         | 3
Qwen3-VL-8B-Instruct-imatrix:Q3_K_M     | 32768   | 8192        | 0.3         | 3
Qwen3-VL-4B-Instruct-imatrix:Q4_K_M     | 32768   | 8192        | 0.3         | 3
Qwen3-VL-2B-Instruct-imatrix:Q4_K_M     | 32768   | 8192        | 0.3         | 3
Qwen3-VL-32B-Thinking:Q5_K_M            | 49152   | 16384       | 1.0         | 3
Qwen3-VL-8B-Thinking-imatrix:Q4_K_M     | 49152   | 16384       | 1.0         | 3
Qwen3-VL-4B-Thinking-imatrix:Q5_K_M     | 49152   | 16384       | 1.0         | 3
Qwen3-VL-2B-Thinking-imatrix:Q5_K_S     | 49152   | 16384       | 1.0         | 3
claude-sonnet-5                         | n/a     | 8192        | not sent    | 3
```

The judge is hardcoded to `Qwen3.8-27B-imatrix:Q4_K_S` with `think=medium` and
`num_predict 40960`, supplied by `JUDGE_DEFAULTS` when the workflow's `judge`
input is blank. Results and the reasoning behind that choice are in
[TICKET_ANALYST_RESULTS.md](TICKET_ANALYST_RESULTS.md).
