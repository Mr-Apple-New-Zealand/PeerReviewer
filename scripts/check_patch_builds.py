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

import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
IN_ACTIONS = os.environ.get("GITHUB_ACTIONS", "").lower() == "true"


def annotate(level: str, title: str, message: str) -> None:
    """Surface something on the run summary page.

    continue-on-error means this step is green whatever happens, so without an
    annotation a check that reached no verdict looks identical to one that
    passed -- and would stay invisible across a twenty-model sweep.
    """
    if IN_ACTIONS:
        one_line = " ".join(message.split())
        print(f"::{level} title={title}::{one_line}")
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


def note_skipped(result_dir: Path, reason: str) -> None:
    """Say why no verdict was reached, in the run's own JSON.

    Otherwise build_skipped_reason keeps whatever the in-process check wrote --
    "disabled (AI_PATCH_BUILD_CHECK=0)" -- which describes a different decision
    and hides the fact that this step ran and could not do its job.
    """
    path = result_dir / "patch_summary.json"
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        data.setdefault("delta", {}).update({
            "build_compiles": None,
            "build_new_errors": None,
            "build_skipped_reason": reason,
        })
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except (OSError, json.JSONDecodeError):
        pass
    _replace_md_section(result_dir / "patch_summary.md",
                        build_check.render({"ran": False, "reason": reason}))


def record(result_dir: Path, new_errors: list, baseline_errors: int = 0) -> None:
    """Write the verdict back into the run's patch_summary.json.

    The workflow leaves build_compiles null because the check is disabled there,
    so without this the compile column exists only in this script's stdout and a
    summary built from the JSON would have a hole in it. Writing it back means one
    file per model still answers every question.
    """
    path = result_dir / "patch_summary.json"
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    delta = data.setdefault("delta", {})
    delta["build_compiles"] = not new_errors
    delta["build_new_errors"] = len(new_errors)
    delta["build_skipped_reason"] = None
    delta["build_errors"] = [
        {k: e[k] for k in ("code", "file", "line", "message")} for e in new_errors[:15]
    ]
    delta["build_checked_by"] = "scripts/check_patch_builds.py"
    try:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    except OSError:
        pass
    _rewrite_md_section(result_dir / "patch_summary.md", new_errors, baseline_errors)


def _replace_md_section(md_path: Path, section: str) -> None:
    """Swap the '## Build check' block for `section`, leaving the rest alone."""
    if not md_path.is_file():
        return
    try:
        md = md_path.read_text(encoding="utf-8")
    except OSError:
        return
    start = md.find("## Build check")
    if start < 0:
        return
    nxt = md.find("\n## ", start + 1)
    end = len(md) if nxt < 0 else nxt + 1
    try:
        md_path.write_text(md[:start] + section + "\n" + md[end:], encoding="utf-8")
    except OSError:
        pass


def _rewrite_md_section(md_path: Path, new_errors: list, baseline_errors: int) -> None:
    """Replace the '## Build check' section so the prose matches the JSON.

    The workflow writes that section before this runs, and with the in-process
    check disabled it says "Not run". Leaving it would put a summary claiming the
    build was never checked next to a JSON recording the compiler error, and the
    markdown is what a person reads.
    """
    _replace_md_section(md_path, build_check.render({
        "ran": True,
        "baseline_errors": baseline_errors,
        "new_errors": new_errors,
        "compiles": not new_errors,
    }))
def main(argv: list[str]) -> int:
    # In CI the verdict belongs in the JSON, not in the step's exit status: a
    # patcher that writes non-compiling code is a finding about that model, not a
    # failure of the run that measured it. Interactively the non-zero exit is
    # useful for gating, so it stays the default.
    gate = "--no-gate" not in argv
    argv = [a for a in argv if a != "--no-gate"]
    dotnet = build_check.find_dotnet()
    if not dotnet:
        reason = ("no .NET SDK on the machine that ran the check — not on PATH "
                  "and not at any default install location")
        print(f"No .NET SDK found. {reason}. Set AI_PATCH_DOTNET to override.",
              file=sys.stderr)
        for d in find_result_dirs(argv):
            note_skipped(d, reason)
        annotate("error", "Build check reached no verdict",
                 f"{reason}. Install dotnet-sdk-8.0 on the runner, or set "
                 "AI_PATCH_DOTNET. Whether this patch compiles is unknown.")
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
    # A restore failure on the pristine tree invalidates the whole comparison:
    # with no packages, the compiler never runs on either tree, both produce zero
    # CS diagnostics, and the difference is zero -- indistinguishable from a
    # patch that compiles cleanly.
    restore_failed = sorted({e["code"] for e in base["errors"]
                             if e["code"].startswith("NU")})
    if restore_failed:
        reason = ("the pristine tree could not restore its packages (%s), so the "
                  "compiler did not run and no verdict is possible" %
                  ", ".join(restore_failed))
        print(f"Refusing to compare: {reason}.", file=sys.stderr)
        for d in dirs:
            note_skipped(d, reason)
        annotate("error", "Build check reached no verdict",
                 f"{reason}. The runner most likely cannot reach api.nuget.org.")
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
        record(d, new, len(base['errors']))

    width = max([len("result")] + [len(r[0]) for r in rows])
    print(f"{'result':<{width}}  {'build':<12}  first new error")
    print(f"{'-' * width}  {'-' * 12}  {'-' * 30}")
    for name, status, detail in rows:
        print(f"{name:<{width}}  {status:<12}  {detail}")

    print(f"\n{len(rows) - broken} of {len(rows)} patched trees compile.")
    for name, status, detail in rows:
        if status.startswith("FAILS"):
            annotate("notice", f"{name}: patched tree does not compile", detail)
        elif status == "?":
            annotate("error", f"{name}: build check reached no verdict", detail)
    return 1 if (broken and gate) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
