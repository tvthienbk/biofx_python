"""Stage 5(a) self-consistency metrics and hard filters.

After reprediction (ColabFold/AF2/AF3) each design has a set of numbers that are
compared back to the design model.  The protocol gives concrete thresholds:

* backbone/global RMSD  < ~2.0 Å   (< 1.5 Å strong)
* motif/catalytic Cα-RMSD < ~1.0-1.5 Å  (strictest)
* pLDDT > 80-90
* min-PAE < ~5
* ligand RMSD < ~5 Å
* pTM / iPTM > 0.8

:class:`SelfConsistency` holds the per-design values; :class:`Thresholds`
encodes the protocol defaults; :meth:`SelfConsistency.evaluate` returns which
criteria pass and a list of human-readable failure reasons.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, fields
from typing import Dict, List, Optional, Tuple

__all__ = [
    "SelfConsistency",
    "Thresholds",
    "read_metrics_csv",
]


@dataclass
class Thresholds:
    """Acceptance thresholds (protocol Stage 5a defaults)."""

    max_rmsd: float = 2.0
    max_motif_ca_rmsd: float = 1.5
    min_plddt: float = 80.0
    max_min_pae: float = 5.0
    max_ligand_rmsd: float = 5.0
    min_ptm: float = 0.8
    min_iptm: float = 0.8


@dataclass
class SelfConsistency:
    """Per-design self-consistency metrics (any may be ``None`` if not measured)."""

    design_id: str
    rmsd: Optional[float] = None
    motif_ca_rmsd: Optional[float] = None
    plddt: Optional[float] = None
    min_pae: Optional[float] = None
    ligand_rmsd: Optional[float] = None
    ptm: Optional[float] = None
    iptm: Optional[float] = None

    def evaluate(self, thr: Thresholds = Thresholds()) -> Tuple[bool, List[str]]:
        """Return ``(passes, reasons)``; ``reasons`` lists each failed criterion.

        A metric that is ``None`` is treated as *not measured* and skipped (it
        neither passes nor fails) — except that at least RMSD or motif-RMSD must
        be present, otherwise the design cannot be judged.
        """
        reasons: List[str] = []
        if self.rmsd is None and self.motif_ca_rmsd is None:
            reasons.append("no RMSD measured (cannot assess self-consistency)")
            return (False, reasons)

        def chk(val, op, lim, label):
            if val is None:
                return
            ok = val <= lim if op == "<=" else val >= lim
            if not ok:
                sym = "<=" if op == "<=" else ">="
                reasons.append(f"{label}={val:g} fails {sym}{lim:g}")

        chk(self.rmsd, "<=", thr.max_rmsd, "rmsd")
        chk(self.motif_ca_rmsd, "<=", thr.max_motif_ca_rmsd, "motif_ca_rmsd")
        chk(self.plddt, ">=", thr.min_plddt, "plddt")
        chk(self.min_pae, "<=", thr.max_min_pae, "min_pae")
        chk(self.ligand_rmsd, "<=", thr.max_ligand_rmsd, "ligand_rmsd")
        chk(self.ptm, ">=", thr.min_ptm, "ptm")
        chk(self.iptm, ">=", thr.min_iptm, "iptm")
        return (len(reasons) == 0, reasons)

    def passes(self, thr: Thresholds = Thresholds()) -> bool:
        return self.evaluate(thr)[0]


_FLOAT_FIELDS = {f.name for f in fields(SelfConsistency) if f.name != "design_id"}


def read_metrics_csv(path: str) -> List[SelfConsistency]:
    """Read a metrics CSV whose header matches :class:`SelfConsistency` fields.

    Unknown columns are ignored; blank cells become ``None``.
    """
    out: List[SelfConsistency] = []
    with open(path, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            kwargs: Dict[str, object] = {"design_id": row["design_id"].strip()}
            for key in _FLOAT_FIELDS:
                raw = (row.get(key) or "").strip()
                kwargs[key] = float(raw) if raw else None
            out.append(SelfConsistency(**kwargs))  # type: ignore[arg-type]
    return out
