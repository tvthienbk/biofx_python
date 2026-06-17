"""Theozyme constraints in the Rosetta ``enzdes`` ``.cst`` format.

A *theozyme* (Stage 1 of the protocol) encodes the catalytic geometry as
distance/angle/dihedral constraints between catalytic protein atoms (residue 1)
and the substrate / transition-state model (residue 2).  Rosetta's enzyme-design
machinery reads these from a ``.cst`` file built of ``CST::BEGIN ... CST::END``
blocks, e.g.::

    CST::BEGIN
      TEMPLATE::   ATOM_MAP: 1 atom_name: OG  ,
      TEMPLATE::   ATOM_MAP: 1 residue3: SER
      TEMPLATE::   ATOM_MAP: 2 atom_name: C1  ,
      TEMPLATE::   ATOM_MAP: 2 residue3: LIG
      CONSTRAINT:: distanceAB:   2.80  0.20  100.0  0  1
      CONSTRAINT:: angle_A:    109.50  5.00   50.0  360.0  1
      CONSTRAINT:: torsion_A:    0.00 10.00   10.0  360.0  1
    CST::END

This module builds, serialises, and parses that subset.  It is faithful enough
to be read by Rosetta's ``EnzConstraintIO`` for the common single-atom-map case;
multi-atom ``ATOM_MAP`` ambiguity lists are supported on serialisation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

__all__ = [
    "AtomMap",
    "GeometricConstraint",
    "ConstraintBlock",
    "Theozyme",
    "TheozymeError",
]

# Valid enzdes constraint keywords, in canonical write order.
_CONSTRAINT_KEYS = [
    "distanceAB",
    "angle_A",
    "angle_B",
    "torsion_A",
    "torsion_AB",
    "torsion_B",
]


class TheozymeError(ValueError):
    """Raised for malformed theozyme/constraint definitions."""


@dataclass
class AtomMap:
    """One residue of a constraint pair: its atoms and its allowed identity.

    ``atoms`` lists 1-3 atom names (Rosetta uses up to three to define the local
    frame).  ``residue3`` is a list of allowed 3-letter residue codes (an
    ambiguity list, e.g. ``['ASP', 'GLU']``).
    """

    index: int  # 1 or 2
    atoms: List[str]
    residue3: List[str]

    def __post_init__(self) -> None:
        if self.index not in (1, 2):
            raise TheozymeError(f"ATOM_MAP index must be 1 or 2, got {self.index}")
        if not 1 <= len(self.atoms) <= 3:
            raise TheozymeError(
                f"ATOM_MAP {self.index}: need 1-3 atom names, got {self.atoms}"
            )
        if not self.residue3:
            raise TheozymeError(f"ATOM_MAP {self.index}: need >=1 residue3 code")

    def to_lines(self) -> List[str]:
        atoms = " ".join(self.atoms)
        res = " ".join(self.residue3)
        return [
            f"  TEMPLATE::   ATOM_MAP: {self.index} atom_name: {atoms} ,",
            f"  TEMPLATE::   ATOM_MAP: {self.index} residue3: {res}",
        ]


@dataclass
class GeometricConstraint:
    """A single ``CONSTRAINT::`` line.

    Fields mirror Rosetta: target value, tolerance (``x0``, ``xtol``), spring
    constant ``k``, ``periodicity`` (0 for distances), and ``n_samples``.
    """

    kind: str
    x0: float
    xtol: float
    k: float
    periodicity: float = 0.0
    n_samples: int = 1

    def __post_init__(self) -> None:
        if self.kind not in _CONSTRAINT_KEYS:
            raise TheozymeError(
                f"unknown constraint {self.kind!r}; expected one of {_CONSTRAINT_KEYS}"
            )
        if self.xtol < 0 or self.k < 0:
            raise TheozymeError(f"{self.kind}: tolerance and k must be >= 0")

    def to_line(self) -> str:
        return (
            f"  CONSTRAINT:: {self.kind}: {self.x0:8.2f} {self.xtol:6.2f} "
            f"{self.k:7.1f} {self.periodicity:6.1f} {self.n_samples:d}"
        )


@dataclass
class ConstraintBlock:
    """One ``CST::BEGIN ... CST::END`` block: two atom maps + constraints."""

    res1: AtomMap
    res2: AtomMap
    constraints: List[GeometricConstraint] = field(default_factory=list)
    comment: str = ""

    def __post_init__(self) -> None:
        if self.res1.index != 1 or self.res2.index != 2:
            raise TheozymeError("block must have ATOM_MAP 1 then ATOM_MAP 2")

    def to_lines(self) -> List[str]:
        lines = ["CST::BEGIN"]
        if self.comment:
            lines.append(f"  # {self.comment}")
        lines.extend(self.res1.to_lines())
        lines.extend(self.res2.to_lines())
        # write constraints in canonical order
        ordered = sorted(
            self.constraints, key=lambda c: _CONSTRAINT_KEYS.index(c.kind)
        )
        lines.extend(c.to_line() for c in ordered)
        lines.append("CST::END")
        return lines


@dataclass
class Theozyme:
    """A full theozyme: an ordered list of constraint blocks."""

    blocks: List[ConstraintBlock] = field(default_factory=list)
    title: str = "theozyme"

    def to_cst(self) -> str:
        """Serialise to enzdes ``.cst`` text."""
        out: List[str] = [f"# {self.title}"]
        for i, block in enumerate(self.blocks, start=1):
            out.append(f"# --- constraint {i} ---")
            out.extend(block.to_lines())
            out.append("")
        return "\n".join(out).rstrip() + "\n"

    def catalytic_residues(self) -> List[str]:
        """Distinct catalytic (residue-1) identities across all blocks."""
        seen: List[str] = []
        for b in self.blocks:
            for code in b.res1.residue3:
                if code not in seen:
                    seen.append(code)
        return seen

    def validate(self) -> List[str]:
        problems: List[str] = []
        if not self.blocks:
            problems.append("theozyme has no constraint blocks")
        for i, b in enumerate(self.blocks, start=1):
            kinds = [c.kind for c in b.constraints]
            if "distanceAB" not in kinds:
                problems.append(f"block {i}: missing distanceAB (the primary constraint)")
            if len(kinds) != len(set(kinds)):
                problems.append(f"block {i}: duplicate constraint keyword(s)")
        return problems


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------
_ATOM_MAP_ATOMS = re.compile(
    r"ATOM_MAP:\s*(\d+)\s+atom_name:\s*([^,]+?)\s*,?\s*$"
)
_ATOM_MAP_RES = re.compile(r"ATOM_MAP:\s*(\d+)\s+residue3:\s*(.+?)\s*$")
_CONSTRAINT = re.compile(r"CONSTRAINT::\s*(\w+):\s*(.+?)\s*$")


def parse_cst(text: str) -> Theozyme:
    """Parse enzdes ``.cst`` text into a :class:`Theozyme`."""
    blocks: List[ConstraintBlock] = []
    atoms_by_idx: dict = {}
    res_by_idx: dict = {}
    constraints: List[GeometricConstraint] = []
    in_block = False

    def _flush() -> None:
        if 1 not in atoms_by_idx or 2 not in atoms_by_idx:
            raise TheozymeError("CST block missing ATOM_MAP 1 or 2")
        res1 = AtomMap(1, atoms_by_idx[1], res_by_idx.get(1, ["ALA"]))
        res2 = AtomMap(2, atoms_by_idx[2], res_by_idx.get(2, ["LIG"]))
        blocks.append(ConstraintBlock(res1, res2, list(constraints)))

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line == "CST::BEGIN":
            in_block = True
            atoms_by_idx, res_by_idx, constraints = {}, {}, []
            continue
        if line == "CST::END":
            _flush()
            in_block = False
            continue
        if not in_block:
            continue
        m = _ATOM_MAP_ATOMS.search(line)
        if m:
            atoms_by_idx[int(m.group(1))] = m.group(2).split()
            continue
        m = _ATOM_MAP_RES.search(line)
        if m:
            res_by_idx[int(m.group(1))] = m.group(2).split()
            continue
        m = _CONSTRAINT.search(line)
        if m:
            kind = m.group(1)
            nums = [float(x) for x in m.group(2).split()]
            # pad to 5 fields: x0 xtol k periodicity n_samples
            while len(nums) < 5:
                nums.append(0.0)
            constraints.append(
                GeometricConstraint(
                    kind=kind,
                    x0=nums[0],
                    xtol=nums[1],
                    k=nums[2],
                    periodicity=nums[3],
                    n_samples=int(nums[4]),
                )
            )
            continue
    if in_block:
        raise TheozymeError("unterminated CST block (missing CST::END)")
    return Theozyme(blocks=blocks)
