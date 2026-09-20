#!/usr/bin/env python3
"""Print what a GGUF file is, without loading the model.

Use it on Ollama's blobs to tell which one is the language model and which is
the vision projector, and to confirm a quantized build really is quantized:

  ollama show Qwen3-VL-32B-Instruct:q4_K_M --modelfile | grep '^FROM'
  python3 scripts/gguf_info.py /san/models/blobs/sha256-...

Standard library only. Reads the header, so it is instant on a 60 GB file.
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

# GGUF metadata value types (gguf spec)
UINT8, INT8, UINT16, INT16, UINT32, INT32, FLOAT32, BOOL, STRING, ARRAY, UINT64, INT64, FLOAT64 = range(13)
FIXED = {UINT8: "<B", INT8: "<b", UINT16: "<H", INT16: "<h", UINT32: "<I", INT32: "<i",
         FLOAT32: "<f", BOOL: "<?", UINT64: "<Q", INT64: "<q", FLOAT64: "<d"}

# ggml tensor types, by the numbers used in the file
GGML_TYPES = {0: "F32", 1: "F16", 2: "Q4_0", 3: "Q4_1", 6: "Q5_0", 7: "Q5_1", 8: "Q8_0", 9: "Q8_1",
              10: "Q2_K", 11: "Q3_K", 12: "Q4_K", 13: "Q5_K", 14: "Q6_K", 15: "Q8_K",
              16: "IQ2_XXS", 17: "IQ2_XS", 18: "IQ3_XXS", 19: "IQ1_S", 20: "IQ4_NL", 21: "IQ3_S",
              22: "IQ2_S", 23: "IQ4_XS", 24: "I8", 25: "I16", 26: "I32", 27: "I64", 28: "F64",
              29: "IQ1_M", 30: "BF16", 39: "MXFP4"}

# general.file_type, the overall quantization label
FILE_TYPES = {0: "F32", 1: "F16", 2: "Q4_0", 3: "Q4_1", 7: "Q8_0", 8: "Q5_0", 9: "Q5_1",
              10: "Q2_K", 11: "Q3_K_S", 12: "Q3_K_M", 13: "Q3_K_L", 14: "Q4_K_S", 15: "Q4_K_M",
              16: "Q5_K_S", 17: "Q5_K_M", 18: "Q6_K", 32: "BF16"}


class Reader:
    def __init__(self, f):
        self.f = f

    def take(self, n: int) -> bytes:
        b = self.f.read(n)
        if len(b) != n:
            raise EOFError("file ended early - truncated or not a GGUF")
        return b

    def fixed(self, t: int):
        fmt = FIXED[t]
        return struct.unpack(fmt, self.take(struct.calcsize(fmt)))[0]

    def string(self) -> str:
        return self.take(self.fixed(UINT64)).decode("utf-8", "replace")

    def value(self, t: int):
        if t == STRING:
            return self.string()
        if t == ARRAY:
            et = self.fixed(UINT32)
            n = self.fixed(UINT64)
            if et == STRING:  # token lists are huge; skip past them
                for _ in range(n):
                    self.take(self.fixed(UINT64))
                return f"<{n} strings>"
            if et == ARRAY:
                return f"<{n} arrays>"
            vals = [self.fixed(et) for _ in range(n)]
            return vals if n <= 8 else f"<{n} values: {vals[:4]}...>"
        return self.fixed(t)


def read(path: Path) -> dict:
    with open(path, "rb") as f:
        r = Reader(f)
        if r.take(4) != b"GGUF":
            raise ValueError("not a GGUF file (bad magic)")
        version = r.fixed(UINT32)
        n_tensors = r.fixed(UINT64)
        n_kv = r.fixed(UINT64)
        kv = {}
        for _ in range(n_kv):
            key = r.string()
            kv[key] = r.value(r.fixed(UINT32))
        tensors = {}
        for _ in range(n_tensors):
            name = r.string()
            dims = [r.fixed(UINT64) for _ in range(r.fixed(UINT32))]
            ttype = r.fixed(UINT32)
            r.fixed(UINT64)  # offset
            tensors[name] = (GGML_TYPES.get(ttype, f"type{ttype}"), dims)
    return {"version": version, "kv": kv, "tensors": tensors}


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for arg in sys.argv[1:]:
        path = Path(arg)
        print(f"== {path}")
        try:
            g = read(path)
        except (ValueError, EOFError, OSError) as e:
            print(f"   ERROR: {e}")
            continue
        kv, tensors = g["kv"], g["tensors"]
        arch = kv.get("general.architecture", "?")
        ft = kv.get("general.file_type")
        counts = {}
        for t, _ in tensors.values():
            counts[t] = counts.get(t, 0) + 1
        vision = [k for k in kv if k.startswith(("vision.", "clip."))]
        print(f"   size          {path.stat().st_size / 1e9:.2f} GB, GGUF v{g['version']}")
        print(f"   architecture  {arch}" + (f"  (type: {kv['general.type']})" if "general.type" in kv else ""))
        print(f"   file_type     {FILE_TYPES.get(ft, ft)}")
        print(f"   tensors       {len(tensors)}: " +
              ", ".join(f"{n}x{t}" for t, n in sorted(counts.items(), key=lambda x: -x[1])))
        for key in ("general.name", "general.size_label", "general.parameter_count",
                    f"{arch}.context_length", f"{arch}.block_count"):
            if key in kv:
                print(f"   {key:<28} {kv[key]}")
        if vision:
            print(f"   vision keys   {len(vision)} (this file carries the image side"
                  f"{', it is the projector' if arch == 'clip' else ''})")
        else:
            print("   vision keys   none (text only)")
        print(f"   chat template {'yes' if 'tokenizer.chat_template' in kv else 'no'}")


if __name__ == "__main__":
    main()
