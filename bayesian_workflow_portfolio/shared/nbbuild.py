"""Helpers for authoring Jupyter notebooks programmatically.

Notebooks in this portfolio are authored via ``nbformat`` rather than by hand.
This guarantees the emitted ``.ipynb`` is valid JSON with a correct schema, which
removes the single most common class of notebook "bugs": malformed JSON, missing
cell metadata, or inconsistent ``nbformat`` versions.

Typical usage in a project's ``build_notebook.py``::

    from shared.nbbuild import NotebookBuilder

    nb = NotebookBuilder(title="Project 01")
    nb.md("# Title", "Some explanation.")
    nb.code("import pymc as pm")
    nb.save("notebook.ipynb")
"""
from __future__ import annotations

import os
from typing import Iterable

import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook


class NotebookBuilder:
    """Accumulate markdown/code cells and emit a validated notebook."""

    def __init__(self, title: str | None = None, kernel: str = "python3") -> None:
        self.cells: list = []
        self.kernel = kernel
        self.title = title

    def md(self, *blocks: str) -> "NotebookBuilder":
        """Add a markdown cell. Multiple args are joined with blank lines."""
        self.cells.append(new_markdown_cell("\n\n".join(b.rstrip() for b in blocks)))
        return self

    def code(self, *lines: str) -> "NotebookBuilder":
        """Add a code cell. Multiple args are joined with newlines."""
        self.cells.append(new_code_cell("\n".join(lines)))
        return self

    def codeblock(self, block: str) -> "NotebookBuilder":
        """Add a code cell from a single (possibly multi-line) string."""
        self.cells.append(new_code_cell(block.strip("\n")))
        return self

    def extend(self, cells: Iterable) -> "NotebookBuilder":
        self.cells.extend(cells)
        return self

    def build(self) -> nbformat.NotebookNode:
        nb = new_notebook(cells=self.cells)
        nb.metadata["kernelspec"] = {
            "display_name": "Python 3",
            "language": "python",
            "name": self.kernel,
        }
        nb.metadata["language_info"] = {"name": "python", "version": "3.11"}
        nbformat.validate(nb)
        return nb

    def save(self, path: str) -> str:
        nb = self.build()
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            nbformat.write(nb, fh)
        return path
