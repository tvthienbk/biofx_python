#!/usr/bin/env python3
"""Static bug-checker for every notebook in the portfolio.

Runs two checks on each ``*.ipynb`` found under the portfolio root:

1. **Schema validation** via ``nbformat.validate`` — catches malformed JSON,
   missing required fields, and version mismatches.
2. **Syntax compilation** of every code cell via ``compile(..., "exec")`` —
   catches Python syntax errors (the most common runtime-blocking notebook bug)
   without needing to execute heavy MCMC sampling.

IPython magics (``%``/``%%``) and shell escapes (``!``) are stripped before
compilation so they do not register as syntax errors.

Usage::

    python shared/validate_notebooks.py            # validate all
    python shared/validate_notebooks.py path.ipynb # validate one

Exit code is non-zero if any notebook fails, so this doubles as a CI gate.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parent.parent
MAGIC = re.compile(r"^\s*[%!]")
LINE_MAGIC_ASSIGN = re.compile(r"^(\s*\w+\s*=\s*)[%!].*$")


def _strip_magics(src: str) -> str:
    out = []
    for line in src.splitlines():
        if MAGIC.match(line):
            out.append("pass  # magic")
        elif LINE_MAGIC_ASSIGN.match(line):
            out.append(LINE_MAGIC_ASSIGN.sub(r"\1None  # magic", line))
        else:
            out.append(line)
    return "\n".join(out)


def check_notebook(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        nb = nbformat.read(path, as_version=4)
    except Exception as exc:  # noqa: BLE001
        return [f"unreadable / invalid JSON: {exc}"]
    try:
        nbformat.validate(nb)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"schema invalid: {exc}")
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        src = _strip_magics(cell.source)
        try:
            compile(src, f"{path.name}:cell{i}", "exec")
        except SyntaxError as exc:
            errors.append(f"cell {i} syntax error: {exc.msg} (line {exc.lineno})")
        else:
            # Also AST-parse to catch a few non-syntax structural issues.
            try:
                ast.parse(src)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"cell {i} parse error: {exc}")
    return errors


def main(argv: list[str]) -> int:
    if len(argv) > 1:
        targets = [Path(a) for a in argv[1:]]
    else:
        targets = sorted(ROOT.glob("**/*.ipynb"))
    if not targets:
        print("No notebooks found.")
        return 0
    failures = 0
    for nb_path in targets:
        nb_path = nb_path.resolve()
        errs = check_notebook(nb_path)
        rel = nb_path.relative_to(ROOT) if ROOT in nb_path.parents else nb_path
        if errs:
            failures += 1
            print(f"FAIL  {rel}")
            for e in errs:
                print(f"        - {e}")
        else:
            print(f"ok    {rel}")
    print(f"\n{len(targets) - failures}/{len(targets)} notebooks passed.")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
