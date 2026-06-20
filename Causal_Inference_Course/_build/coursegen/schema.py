"""Validate a WEEK content dict before building, so a missing field fails
loudly here instead of producing a broken document downstream.
"""
from __future__ import annotations

_TOP = ["number", "slug", "title", "block", "subtitle", "packet_intro",
        "one_sentence", "objectives_heading", "objectives", "reading_intro",
        "readings", "concept_intro", "concept_sections", "problem_set",
        "lab", "self_check", "next_week", "deck", "notebook"]


def validate_week(week: dict) -> list[str]:
    """Return a list of human-readable problems (empty == OK)."""
    errs: list[str] = []
    n = week.get("number", "?")

    for k in _TOP:
        if k not in week:
            errs.append(f"week {n}: missing top-level key '{k}'")

    if len(week.get("objectives", [])) < 4:
        errs.append(f"week {n}: need >= 4 objectives")
    if len(week.get("readings", [])) < 2:
        errs.append(f"week {n}: need >= 2 core readings")
    for r in week.get("readings", []):
        if "text" not in r or "look_for" not in r:
            errs.append(f"week {n}: reading needs 'text' and 'look_for'")
    if len(week.get("concept_sections", [])) < 2:
        errs.append(f"week {n}: need >= 2 concept sections")

    ps = week.get("problem_set", {})
    for k in ("label", "title", "intro", "problems"):
        if k not in ps:
            errs.append(f"week {n}: problem_set missing '{k}'")
    if len(ps.get("problems", [])) < 4:
        errs.append(f"week {n}: need >= 4 problems")
    for p in ps.get("problems", []):
        for k in ("title", "prompt", "solution_title", "solution"):
            if k not in p:
                errs.append(f"week {n}: problem missing '{k}'")

    lab = week.get("lab", {})
    for k in ("label", "title", "goal", "steps"):
        if k not in lab:
            errs.append(f"week {n}: lab missing '{k}'")

    deck = week.get("deck", [])
    if len(deck) < 20:
        errs.append(f"week {n}: deck has only {len(deck)} slides (want >= 20)")
    if deck and deck[0].get("type") != "title":
        errs.append(f"week {n}: first deck slide must be type 'title'")
    valid_types = {"title", "section", "content", "compare", "table",
                   "statement", "steps", "agenda"}
    for i, s in enumerate(deck):
        if s.get("type") not in valid_types:
            errs.append(f"week {n}: deck slide {i} bad type {s.get('type')!r}")

    nb = week.get("notebook", [])
    if len(nb) < 8:
        errs.append(f"week {n}: notebook has only {len(nb)} cells (want >= 8)")
    if not any("code" in c for c in nb):
        errs.append(f"week {n}: notebook has no code cells")

    nxt = week.get("next_week", {})
    for k in ("heading", "teaser"):
        if k not in nxt:
            errs.append(f"week {n}: next_week missing '{k}'")

    return errs
