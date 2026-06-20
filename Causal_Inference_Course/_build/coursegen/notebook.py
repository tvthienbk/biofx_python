"""Build a weekly practice notebook (.ipynb) from a list of cells.

We emit nbformat v4 JSON directly (no nbformat dependency required). Each week
provides a list of cells as dicts: {"md": "..."} for markdown or
{"code": "..."} for code. A standard banner and an environment-check cell are
prepended automatically so every notebook is self-contained and runnable.
"""
from __future__ import annotations

import json

from . import theme

_BANNER = """# {course}
## Week {n} — {title} · Practice Notebook

> **{block}**
>
> {subtitle}

**How to use this notebook.** Run the cells top to bottom. Sections marked
**🔧 Exercise** contain a `# TODO` for you to complete; a matching
**✅ Solution** cell follows (collapsed in spirit — try it yourself first).
Every dataset here is *simulated with a known ground truth*, so you can always
check whether your estimate recovered the right answer.

*Estimated time: 60–90 minutes. Toolkit: `numpy`, `pandas`, `statsmodels`,
`scikit-learn`, `matplotlib` — all standard.*

---
"""

_ENV = """# --- Environment check & shared setup -------------------------------------
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option("display.float_format", lambda v: f"{v:,.4f}")
plt.rcParams.update({"figure.figsize": (7, 4.2), "axes.grid": True,
                     "grid.alpha": 0.25, "font.size": 11})

RNG = np.random.default_rng(7)   # one seed for the whole notebook → reproducible
print("Environment OK — numpy", np.__version__, "| pandas", pd.__version__)"""


def _md(source: str) -> dict:
    lines = source.split("\n")
    src = [l + "\n" for l in lines[:-1]] + [lines[-1]] if lines else [""]
    return {"cell_type": "markdown", "metadata": {}, "source": src}


def _code(source: str) -> dict:
    lines = source.rstrip("\n").split("\n")
    src = [l + "\n" for l in lines[:-1]] + [lines[-1]] if lines else [""]
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": src}


def build_notebook(week: dict, out_path: str) -> str:
    cells = [
        _md(_BANNER.format(course=theme.COURSE_TITLE, n=week["number"],
                           title=week["title"], block=week["block"],
                           subtitle=week["subtitle"])),
        _code(_ENV),
    ]
    for c in week["notebook"]:
        if "md" in c:
            cells.append(_md(c["md"]))
        else:
            cells.append(_code(c["code"]))

    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python",
                           "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
            "title": f"Week {week['number']} — {week['title']}",
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    with open(out_path, "w") as fh:
        json.dump(nb, fh, indent=1, ensure_ascii=False)
    return out_path
