"""Run the differential build check over saved patcher results, after the fact.

The build check is the only thing that catches a patcher inventing an API that
does not exist -- one run scored 81.4% resolved with 41 of 41 markers clear on
code calling `CorsPolicyBuilder.AllowMethods`. But running it inside the workflow
proved unsafe on the self-hosted runner: two jobs died mid-run once the SDK
became findable, and a cancelled job loses the whole 15 minutes of model output,
which across a twenty-model sweep is a bad trade for a check that takes ten
seconds offline.

So run it here instead, against the scratch trees the workflow already archives.
Same code, same verdict, none of the risk.

    python scripts/check_patch_builds.py                       # every result dir
    python scripts/check_patch_builds.py ai_code_patcher/test  # just one

Exits non-zero if any patch introduced a compiler error, so it can gate a sweep.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import build_check  # noqa: E402

PRISTINE = REPO_ROOT / "SampleBankingApp"


def find_result_dirs(args: list[str]) -> list[Path]:
    """Every directory holding a patched scratch tree."""
    if args:
        roots = [Path(a).resolve() for a in args]
    else:
        roots = [REPO_ROOT / "ai_code_patcher"]
    out = []
    for root in roots:
        if (root / "scratch" / PRISTINE.name).is_dir():
            out.append(root)
        out += [p.parent.parent for p in
                sorted(root.rglob(f"scratch/{PRISTINE.name}")) if p.is_dir()]
    seen, uniq = set(), []
    for d in out:
        if d not in seen:
            seen.add(d)
            uniq.append(d)
    return uniq


def main(argv: list[str]) -> int:
    dotnet = build_check.find_dotnet()
    if not dotnet:
        print("No .NET SDK found. Set AI_PATCH_DOTNET to the dotnet executable.",
              file=sys.stderr)
        return 2
    print(f"Using {dotnet}\n")

    dirs = find_result_dirs(argv)
    if not dirs:
        print("No patched scratch trees found. Expected <dir>/scratch/SampleBankingApp/.",
              file=sys.stderr)
        return 2

    # Compile the pristine tree once; every patch is measured against it.
    base = build_check.build(PRISTINE)
    if not base["ran"]:
        print(f"Could not build the pristine tree: {base['reason']}", file=sys.stderr)
        return 2
    base_sigs = {(e["code"], e["file"], e["message"]) for e in base["errors"]}
    print(f"Pristine tree: {len(base['errors'])} pre-existing error(s)\n")

    rows, broken = [], 0
    for d in dirs:
        after = build_check.build(d / "scratch" / PRISTINE.name)
        if not after["ran"]:
            rows.append((d.name, "?", after["reason"][:60]))
            continue
        new = [e for e in after["errors"]
               if (e["code"], e["file"], e["message"]) not in base_sigs]
        if new:
            broken += 1
            first = f"{new[0]['code']} {new[0]['file']}:{new[0]['line'] or '?'}"
            rows.append((d.name, f"FAILS ({len(new)})", first))
        else:
            rows.append((d.name, "compiles", ""))

    width = max(len(r[0]) for r in rows)
    print(f"{'result':<{width}}  {'build':<12}  first new error")
    print(f"{'-' * width}  {'-' * 12}  {'-' * 30}")
    for name, status, detail in rows:
        print(f"{name:<{width}}  {status:<12}  {detail}")

    print(f"\n{len(rows) - broken} of {len(rows)} patched trees compile.")
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
