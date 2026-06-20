"""coursegen — reproducible generator for the Causal Inference course.

Turns one structured ``WEEK`` dict per week into three deliverables:
a self-study packet (.docx), a lecture deck (.pptx) and a practice
notebook (.ipynb).
"""
from .packet import build_packet
from .deck import build_deck
from .notebook import build_notebook
from .schema import validate_week

__all__ = ["build_packet", "build_deck", "build_notebook", "validate_week"]
