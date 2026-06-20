"""Shared visual theme for the Causal Inference course materials.

A single source of truth for the colours, fonts and sizing used across the
self-study packets (.docx), lecture decks (.pptx) and practice notebooks so
that every week looks like it belongs to the same course.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Colour palette (hex, no leading '#'). Mirrors the Week 1 deck: a navy spine
# with blue / teal / amber accents.
# ---------------------------------------------------------------------------
NAVY = "1F2A44"        # primary dark — titles, dividers
NAVY_SOFT = "44546A"   # secondary text
BLUE = "2F6DB5"        # primary accent
BLUE_LIGHT = "5B9BD5"
TEAL = "2A9D8F"        # "treatment A" accent / positive
AMBER = "E9A23B"       # "treatment B" accent / caution
RED = "C0504D"         # warnings / "do not adjust"
GREEN = "4E8C57"       # "adjust" / good
GREY = "7F8694"        # captions
GREY_LIGHT = "ECEEF2"  # panel fills
PAPER = "FFFFFF"
INK = "222732"         # body text

# Role-based aliases used by the builders.
COLOR = {
    "navy": NAVY,
    "navy_soft": NAVY_SOFT,
    "blue": BLUE,
    "blue_light": BLUE_LIGHT,
    "teal": TEAL,
    "amber": AMBER,
    "red": RED,
    "green": GREEN,
    "grey": GREY,
    "grey_light": GREY_LIGHT,
    "paper": PAPER,
    "ink": INK,
}

# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------
FONT_HEAD = "Calibri"   # widely available; renders cleanly in PowerPoint/Word
FONT_BODY = "Calibri"
FONT_MONO = "Consolas"

COURSE_TITLE = "Causal Inference in Practice"
COURSE_TAGLINE = 'From "what is associated with what" to "what happens if we intervene."'
