#!/usr/bin/env python3
"""Build every project's notebooks and validate the whole portfolio.

Steps:
1. For each ``project_*/build_notebook.py``, run it (writes notebook.ipynb +
   notebook_broken.ipynb). Building via nbformat guarantees valid JSON.
2. Run the static validator over all notebooks (schema + per-cell syntax).

Usage:
    python build_all.py            # build + validate
    python build_all.py --no-build # validate only
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def build_notebooks() -> int:
    failures = 0
    for builder in sorted(ROOT.glob("project_*/build_notebook.py")):
        proj = builder.parent.name
        print(f"== building {proj} ==")
        r = subprocess.run(
            [sys.executable, "build_notebook.py"],
            cwd=builder.parent,
            capture_output=True,
            text=True,
        )
        if r.returncode != 0:
            failures += 1
            print(f"   BUILD FAILED ({proj}):\n{r.stdout}\n{r.stderr}")
        else:
            print(f"   ok ({proj})")
    return failures


def main(argv: list[str]) -> int:
    build_failures = 0
    if "--no-build" not in argv:
        build_failures = build_notebooks()
    print("\n== validating notebooks ==")
    val = subprocess.run(
        [sys.executable, str(ROOT / "shared" / "validate_notebooks.py")],
        cwd=ROOT,
    )
    return 1 if (build_failures or val.returncode) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
