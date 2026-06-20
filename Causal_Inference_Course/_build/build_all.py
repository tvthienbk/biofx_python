#!/usr/bin/env python3
"""Build every week's materials from its content module.

Usage:
    python build_all.py            # build all weeks that have a content module
    python build_all.py 1 2 3      # build only the listed weeks

For each week N it imports ``coursegen.content.week{NN}`` (which must expose a
``WEEK`` dict), validates it, and writes the packet (.docx), deck (.pptx) and
practice notebook (.ipynb) into ``WeekNN_<Title>/`` plus a short README.
"""
from __future__ import annotations

import importlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)          # Causal_Inference_Course/
sys.path.insert(0, HERE)

from coursegen import build_packet, build_deck, build_notebook, validate_week  # noqa: E402


def folder_name(week: dict) -> str:
    title = re.sub(r"[^0-9A-Za-z ]+", "", week["title"]).strip()
    camel = "_".join(w for w in title.split())
    return f"Week{week['number']:02d}_{camel}"


def file_stub(week: dict) -> str:
    title = re.sub(r"[^0-9A-Za-z ]+", "", week["title"]).strip()
    return f"Week{week['number']:02d}_" + "_".join(title.split())


README = """# Week {n} — {title}

**{block}**

{subtitle}

## Contents of this folder

| File | What it is |
|------|------------|
| `{stub}_Self_Study_Packet.docx` | Readings, concept refresher, problem set (+ full solutions), the lab, and a self-check. Work through it after lecture (~5–7 h). |
| `{stub}_Lecture.pptx` | The ~{nslides}-slide lecture deck. |
| `{stub}_Practice.ipynb` | Runnable Jupyter notebook: worked examples + graded-style exercises with solutions. All data is simulated with a known ground truth. |

## This week in one sentence

{one_sentence}

## Deliverable

{deliverable}
"""


def build_week(week: dict) -> None:
    errs = validate_week(week)
    if errs:
        raise SystemExit("VALIDATION FAILED:\n  " + "\n  ".join(errs))

    out_dir = os.path.join(ROOT, folder_name(week))
    os.makedirs(out_dir, exist_ok=True)
    stub = file_stub(week)

    build_packet(week, os.path.join(out_dir, f"{stub}_Self_Study_Packet.docx"))
    build_deck(week, os.path.join(out_dir, f"{stub}_Lecture.pptx"))
    build_notebook(week, os.path.join(out_dir, f"{stub}_Practice.ipynb"))

    with open(os.path.join(out_dir, "README.md"), "w") as fh:
        fh.write(README.format(
            n=week["number"], title=week["title"], block=week["block"],
            subtitle=week["subtitle"], stub=stub,
            nslides=len([s for s in week["deck"] if s["type"] not in ("title",)]),
            one_sentence=week["one_sentence"],
            deliverable=week.get("deliverable", week["lab"]["title"]),
        ))
    print(f"  ✓ Week {week['number']:>2}: {folder_name(week)}  "
          f"({len(week['deck'])} slides, {len(week['notebook'])+2} nb cells)")


def main(argv):
    wanted = [int(a) for a in argv] if argv else list(range(1, 16))
    built = 0
    for n in wanted:
        mod_name = f"coursegen.content.week{n:02d}"
        try:
            mod = importlib.import_module(mod_name)
        except ModuleNotFoundError:
            if argv:
                print(f"  · Week {n:>2}: no content module ({mod_name}) — skipped")
            continue
        importlib.reload(mod)
        build_week(mod.WEEK)
        built += 1
    print(f"\nBuilt {built} week(s).")


if __name__ == "__main__":
    main(sys.argv[1:])
