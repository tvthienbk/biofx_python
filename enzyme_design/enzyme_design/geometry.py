"""Minimal PDB parsing and structural superposition for motif Cα-RMSD.

Stage 5(a) of the protocol requires comparing a *predicted* structure to the
*design* model and reporting (i) backbone RMSD, (ii) the stricter motif /
catalytic Cα-RMSD, and (iii) ligand RMSD.  This module provides a dependency-
light PDB ATOM/HETATM reader and a Kabsch superposition so those numbers can be
computed without a full structural-biology stack.

Only the columns needed for RMSD are parsed (record, serial, atom name, resName,
chain, resSeq, x/y/z).  NumPy is used for the superposition math.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "Atom",
    "Structure",
    "parse_pdb",
    "kabsch_rmsd",
    "motif_ca_rmsd",
    "ligand_rmsd",
]


@dataclass(frozen=True)
class Atom:
    record: str  # "ATOM" or "HETATM"
    serial: int
    name: str
    res_name: str
    chain: str
    res_seq: int
    x: float
    y: float
    z: float

    @property
    def xyz(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)

    @property
    def res_key(self) -> str:
        return f"{self.chain}{self.res_seq}"


@dataclass
class Structure:
    atoms: List[Atom]

    def __iter__(self):
        return iter(self.atoms)

    def __len__(self) -> int:
        return len(self.atoms)

    def select(
        self,
        names: Optional[Sequence[str]] = None,
        records: Optional[Sequence[str]] = None,
        chain: Optional[str] = None,
        res_names: Optional[Sequence[str]] = None,
    ) -> List[Atom]:
        out = []
        for a in self.atoms:
            if names is not None and a.name not in names:
                continue
            if records is not None and a.record not in records:
                continue
            if chain is not None and a.chain != chain:
                continue
            if res_names is not None and a.res_name not in res_names:
                continue
            out.append(a)
        return out

    def ca_by_residue(self) -> Dict[str, Atom]:
        """Map ``"A84" -> Cα atom`` for protein residues."""
        out: Dict[str, Atom] = {}
        for a in self.atoms:
            if a.record == "ATOM" and a.name == "CA":
                out[a.res_key] = a
        return out


def parse_pdb(text: str) -> Structure:
    """Parse PDB ATOM/HETATM records using fixed-column slicing."""
    atoms: List[Atom] = []
    for line in text.splitlines():
        rec = line[0:6].strip()
        if rec not in ("ATOM", "HETATM"):
            continue
        try:
            serial = int(line[6:11])
        except ValueError:
            serial = 0
        name = line[12:16].strip()
        res_name = line[17:20].strip()
        chain = line[21:22].strip() or "A"
        try:
            res_seq = int(line[22:26])
        except ValueError:
            continue
        try:
            x = float(line[30:38])
            y = float(line[38:46])
            z = float(line[46:54])
        except ValueError:
            continue
        atoms.append(Atom(rec, serial, name, res_name, chain, res_seq, x, y, z))
    return Structure(atoms)


def _coords(atoms: Sequence[Atom]) -> np.ndarray:
    return np.array([[a.x, a.y, a.z] for a in atoms], dtype=float)


def kabsch_rmsd(p: np.ndarray, q: np.ndarray, superpose: bool = True) -> float:
    """RMSD between paired point sets ``p`` and ``q`` (N x 3).

    With ``superpose=True`` (default) ``p`` is optimally rotated/translated onto
    ``q`` first via the Kabsch algorithm; otherwise the raw RMSD is returned.
    """
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    if p.shape != q.shape:
        raise ValueError(f"point sets differ in shape: {p.shape} vs {q.shape}")
    if p.shape[0] == 0:
        raise ValueError("cannot compute RMSD over zero points")
    if not superpose:
        diff = p - q
        return float(np.sqrt((diff * diff).sum() / p.shape[0]))

    # center
    pc = p - p.mean(axis=0)
    qc = q - q.mean(axis=0)
    # covariance + SVD
    h = pc.T @ qc
    u, _s, vt = np.linalg.svd(h)
    d = np.sign(np.linalg.det(vt.T @ u.T))
    correction = np.diag([1.0, 1.0, d])
    rot = vt.T @ correction @ u.T
    p_rot = pc @ rot.T
    diff = p_rot - qc
    return float(np.sqrt((diff * diff).sum() / p.shape[0]))


def motif_ca_rmsd(
    design: Structure,
    predicted: Structure,
    residues: Sequence[str],
    superpose: bool = True,
) -> float:
    """Cα-RMSD over ``residues`` (e.g. ``['A84','A85',...]``) between two models.

    Both structures must contain a Cα for every requested residue.  This is the
    strictest Stage-5 criterion: predicted catalytic-residue placement.
    """
    d_ca = design.ca_by_residue()
    p_ca = predicted.ca_by_residue()
    missing = [r for r in residues if r not in d_ca or r not in p_ca]
    if missing:
        raise ValueError(f"missing Cα for residues: {missing}")
    p = _coords([d_ca[r] for r in residues])
    q = _coords([p_ca[r] for r in residues])
    return kabsch_rmsd(p, q, superpose=superpose)


def ligand_rmsd(
    design: Structure,
    predicted: Structure,
    lig_code: str,
    superpose: bool = False,
) -> float:
    """RMSD over the ligand heavy atoms (matched by atom name).

    By default ``superpose=False`` so the value reflects ligand displacement in
    the *common protein frame* (the structures are assumed already aligned);
    pass ``superpose=True`` to align on the ligand itself.
    """
    d_lig = {a.name: a for a in design.select(records=["HETATM"], res_names=[lig_code])}
    p_lig = {a.name: a for a in predicted.select(records=["HETATM"], res_names=[lig_code])}
    common = [n for n in d_lig if n in p_lig]
    if not common:
        raise ValueError(f"no shared ligand ({lig_code}) atoms to compare")
    p = _coords([d_lig[n] for n in common])
    q = _coords([p_lig[n] for n in common])
    return kabsch_rmsd(p, q, superpose=superpose)
