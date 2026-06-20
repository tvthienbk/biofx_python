#!/usr/bin/env python3
"""Heuristic lint for deck specs: flag slides whose text is likely to overflow
the slide, since we can't render to images in this environment. Operates on the
content modules (the source of truth), not the rendered pptx.

Thresholds are deliberately conservative; warnings are advisory.
"""
from __future__ import annotations

import importlib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def _seg_len(seg) -> int:
    if isinstance(seg, str):
        return len(seg)
    if isinstance(seg, tuple):  # (text, level) or (text, opts)
        return len(seg[0]) if isinstance(seg[0], str) else 0
    if isinstance(seg, list):   # list of runs
        return sum(len(t) for t, _ in seg)
    return 0


def lint_week(week: dict) -> list[str]:
    warns: list[str] = []
    n = week["number"]
    for i, s in enumerate(week["deck"]):
        t = s.get("type")
        where = f"W{n:02d} slide {i} [{t}]"
        if t == "content":
            bl = s.get("bullets", [])
            if len(bl) > 7:
                warns.append(f"{where}: {len(bl)} bullets (>7 may overflow)")
            for b in bl:
                L = _seg_len(b)
                if L > 130:
                    warns.append(f"{where}: bullet {L} chars (>130)")
            note = s.get("note")
            if note and len(note.get("body", "")) > 230:
                warns.append(f"{where}: note body {len(note['body'])} chars (>230)")
        elif t == "compare":
            cols = s.get("columns", [])
            if len(cols) > 3:
                warns.append(f"{where}: {len(cols)} columns (>3)")
            for c in cols:
                if len(c.get("points", [])) > 6:
                    warns.append(f"{where}: column '{c.get('head')}' "
                                 f"{len(c['points'])} points (>6)")
                for p in c.get("points", []):
                    if _seg_len(p) > 90:
                        warns.append(f"{where}: compare point {_seg_len(p)} "
                                     f"chars (>90)")
        elif t == "table":
            rows = s.get("rows", [])
            if len(rows) > 7:
                warns.append(f"{where}: {len(rows)} rows (>7 may overflow)")
            if s.get("headers") and len(s["headers"]) > 4:
                warns.append(f"{where}: {len(s['headers'])} columns (>4)")
        elif t == "steps":
            st = s.get("steps", [])
            if len(st) > 6:
                warns.append(f"{where}: {len(st)} steps (>6)")
        elif t == "agenda":
            if len(s.get("items", [])) > 8:
                warns.append(f"{where}: {len(s['items'])} agenda items (>8)")
        elif t == "statement":
            if len(s.get("quote", "")) > 170:
                warns.append(f"{where}: quote {len(s['quote'])} chars (>170)")
    return warns


def main(weeks):
    wanted = weeks or list(range(1, 16))
    total = 0
    for n in wanted:
        try:
            mod = importlib.import_module(f"coursegen.content.week{n:02d}")
        except ModuleNotFoundError:
            continue
        importlib.reload(mod)
        ws = lint_week(mod.WEEK)
        for w in ws:
            print("  ⚠ " + w)
        total += len(ws)
    print(f"\n{total} overflow warning(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main([int(a) for a in sys.argv[1:]]))
