"""Does the patched tree still compile?

Every other check in this harness asks whether the *shape* of a bug is gone. None
of them asks whether the result builds, and a patcher can satisfy all of them
while emitting code the compiler rejects.

That is not hypothetical. The Qwen3.8-27B run scored 95.7% resolved with 41 of 41
markers clear, and its CORS fix reads:

    policy.WithOrigins(allowedOrigins)
          .AllowMethods("GET", "POST", "PUT", "DELETE")
          .AllowHeaders("Content-Type", "Authorization")

`CorsPolicyBuilder` has no `AllowMethods` or `AllowHeaders` -- they are
`WithMethods` and `WithHeaders`. The dangerous `AllowAnyOrigin` was genuinely
removed and the replacement invented, so the marker cleared and the project no
longer compiles. Inventing a plausible API is a characteristic LLM failure, and
it is invisible to a text marker.

DIFFERENTIAL, not absolute. SampleBankingApp does not build cleanly to begin with
-- it pins System.IdentityModel.Tokens.Jwt 7.0.0 against a transitive 7.0.3 and
NU1605 makes that an error. Both trees are compiled and only errors present in
the patched tree and absent from the pristine one are reported, so a pre-existing
failure is not charged to the patcher. NU1605 is additionally suppressed by
default because a failed restore stops compilation before any CS diagnostic is
produced, which would hide exactly what this check exists to find.

Signatures deliberately exclude line numbers: a patch shifts lines, and the same
pre-existing error at a new line is still pre-existing.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

# NU1605 (package downgrade) fails restore on the pristine tree, and without a
# restore the compiler never runs. Overridable for a different sample project.
DEFAULT_NOWARN = os.environ.get("AI_PATCH_BUILD_NOWARN", "NU1605").strip()

_ERROR = re.compile(
    r"^(?P<path>.*?)(?:\((?P<line>\d+),\d+\))?\s*:\s*"
    r"error\s+(?P<code>[A-Z]+\d+)\s*:\s*(?P<msg>.*?)\s*(?:\[[^\]]*\])?$",
    re.MULTILINE,
)


def _signature(m: re.Match) -> tuple[str, str, str]:
    """(code, file basename, message) — stable across the two trees.

    The absolute path differs between pristine and patched by construction, and
    the line number moves whenever the patch adds a line above the error, so
    neither can appear in the key.
    """
    base = (m.group("path") or "").replace("\\", "/").rsplit("/", 1)[-1].strip()
    msg = re.sub(r"[A-Za-z]:[\\/][^\s'\"]+", "<path>", m.group("msg") or "").strip()
    return (m.group("code"), base, msg)


def find_dotnet() -> str | None:
    """Locate the SDK, falling back to the default install paths.

    PATH alone is not enough. A GitHub Actions service account on Windows does
    not inherit the interactive user's PATH, so the first sweep reported "dotnet
    not on PATH" on a machine with 10.0.400 installed -- and silently skipped the
    one check that catches a non-compiling patch. Set AI_PATCH_DOTNET to override.
    """
    override = os.environ.get("AI_PATCH_DOTNET", "").strip()
    if override:
        return override if Path(override).exists() else None

    found = shutil.which("dotnet")
    if found:
        return found

    candidates = [
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "dotnet" / "dotnet.exe",
        Path(os.environ.get("ProgramW6432", r"C:\Program Files")) / "dotnet" / "dotnet.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "dotnet" / "dotnet.exe",
        Path("/usr/share/dotnet/dotnet"),
        Path("/usr/local/share/dotnet/dotnet"),
        Path("/usr/lib/dotnet/dotnet"),
        Path("/usr/bin/dotnet"),
        Path.home() / ".dotnet" / "dotnet",
    ]
    for c in candidates:
        try:
            if c.is_file():
                return str(c)
        except OSError:
            continue
    return None


def build(source_root: str | Path, timeout: int = 240) -> dict:
    """Compile one tree. Output goes to a temp dir so no obj/ or bin/ is left behind."""
    root = Path(source_root).resolve()
    proj = next(iter(sorted(root.glob("*.csproj"))), None)
    if proj is None:
        return {"ran": False, "reason": f"no .csproj under {root}", "errors": []}

    dotnet = find_dotnet()
    if not dotnet:
        return {"ran": False, "errors": [], "reason":
                "no .NET SDK found — not on PATH and not at any default install "
                "location. Set AI_PATCH_DOTNET to the dotnet executable"}

    with tempfile.TemporaryDirectory(prefix="pr_build_") as tmp:
        cmd = [
            dotnet, "build", str(proj), "-v", "q", "--nologo",
            f"-p:NoWarn={DEFAULT_NOWARN}",
            # One worker, and no surviving MSBuild nodes. The default keeps worker
            # processes alive for reuse, which on a self-hosted runner shared with a
            # resident 27B model means extra processes competing for RAM after the
            # build returns.
            "-m:1", "-nodereuse:false",
            # Keep every artefact out of the source tree: the pristine tree is the
            # user's repo, and a stray obj/ would show up as untracked noise.
            f"-p:BaseIntermediateOutputPath={Path(tmp) / 'obj'}{os.sep}",
            f"-p:BaseOutputPath={Path(tmp) / 'bin'}{os.sep}",
        ]
        env = dict(os.environ)
        env.update({
            "DOTNET_CLI_TELEMETRY_OPTOUT": "1",
            "DOTNET_NOLOGO": "1",
            "DOTNET_SKIP_FIRST_TIME_EXPERIENCE": "1",
            # A first run otherwise pauses to populate the package cache.
            "DOTNET_CLI_UI_LANGUAGE": "en",
        })
        try:
            res = subprocess.run(cmd, capture_output=True, text=True,
                                 timeout=timeout, cwd=str(root), env=env)
        except subprocess.TimeoutExpired:
            return {"ran": False, "reason": f"build timed out after {timeout}s",
                    "errors": []}
        except OSError as exc:
            return {"ran": False, "reason": f"could not run dotnet: {exc}", "errors": []}
        except Exception as exc:                      # never take the run down
            return {"ran": False, "reason": f"build check failed: {exc}", "errors": []}

    out = (res.stdout or "") + "\n" + (res.stderr or "")
    seen, errors = set(), []
    for m in _ERROR.finditer(out):
        sig = _signature(m)
        if sig in seen:
            continue                      # MSBuild prints each error twice
        seen.add(sig)
        errors.append({"code": sig[0], "file": sig[1], "message": sig[2],
                       "line": m.group("line")})
    return {"ran": True, "reason": "", "exit_code": res.returncode, "errors": errors}


def compare(pristine_root, patched_root, timeout: int = 240) -> dict:
    """Build both trees and attribute only the newly-introduced errors."""
    before = build(pristine_root, timeout)
    after = build(patched_root, timeout)
    if not before["ran"] or not after["ran"]:
        return {"ran": False,
                "reason": before.get("reason") or after.get("reason"),
                "before": before, "after": after, "new_errors": []}

    old = {(e["code"], e["file"], e["message"]) for e in before["errors"]}
    new = [e for e in after["errors"]
           if (e["code"], e["file"], e["message"]) not in old]
    return {
        "ran": True,
        "reason": "",
        "before": before,
        "after": after,
        "baseline_errors": len(before["errors"]),
        "patched_errors": len(after["errors"]),
        "new_errors": new,
        "compiles": not new,
    }


def render(result: dict) -> str:
    """Markdown section for patch_summary.md."""
    lines = ["## Build check", ""]
    if not result.get("ran"):
        lines += [
            f"Not run — {result.get('reason') or 'unavailable'}. "
            "Whether the patched tree compiles is therefore unknown; the figures "
            "above describe the code's shape, not its validity.",
            "",
        ]
        return "\n".join(lines)

    base_n, new = result["baseline_errors"], result["new_errors"]
    baseline_note = (
        f" The pristine tree already fails with {base_n} error(s), which are "
        "excluded rather than charged to the patcher."
        if base_n else " The pristine tree compiles cleanly."
    )

    if not new:
        lines += [
            f"**The patched tree compiles.** No compiler error appears that was not "
            f"already present before the patch.{baseline_note}",
            "",
        ]
        return "\n".join(lines)

    lines += [
        f"**The patched tree does not compile — {len(new)} new error(s).**"
        f"{baseline_note}",
        "",
        "Read every figure above in this light. A resolved-issues count measures "
        "whether the reviewer can still name each bug, and code that does not "
        "build can score well on that while being unusable.",
        "",
        "| Error | File | Line | Message |",
        "|---|---|---|---|",
    ]
    for e in new[:15]:
        msg = e["message"].replace("|", "\\|")
        lines.append(f"| `{e['code']}` | `{e['file']}` | {e['line'] or '—'} | {msg} |")
    if len(new) > 15:
        lines.append(f"| … | | | {len(new) - 15} further error(s) not listed |")
    lines.append("")
    return "\n".join(lines)
