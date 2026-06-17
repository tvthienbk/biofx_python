"""Stage 6: construct registry and gene-order preparation.

The protocol insists on a registry mapping each construct to its design ID,
sequence, predicted metrics, and intended catalytic residues, and on a few
pre-synthesis sequence checks (free surface cysteines, internal restriction
sites, length).  This module provides a typed record, those checks, and CSV
round-tripping so the full design table — *including the denominator*, not just
hits — can be archived (reproducibility checklist).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Sequence

__all__ = [
    "DesignRecord",
    "ConstructRegistry",
    "restriction_sites",
    "free_cysteines",
    "RegistryError",
]

# A few common cloning enzymes and their recognition sites (DNA).
DEFAULT_ENZYMES: Dict[str, str] = {
    "NdeI": "CATATG",
    "XhoI": "CTCGAG",
    "BamHI": "GGATCC",
    "EcoRI": "GAATTC",
    "BsaI": "GGTCTC",
    "BsmBI": "CGTCTC",
}

_AA = set("ACDEFGHIKLMNPQRSTVWY")


class RegistryError(ValueError):
    pass


def restriction_sites(dna: str, enzymes: Optional[Dict[str, str]] = None) -> Dict[str, List[int]]:
    """Return ``{enzyme: [0-based positions]}`` for sites found on ``dna``.

    Checks both strands (site or its reverse complement).
    """
    enzymes = enzymes or DEFAULT_ENZYMES
    seq = dna.upper()
    comp = str.maketrans("ACGT", "TGCA")
    out: Dict[str, List[int]] = {}
    for name, site in enzymes.items():
        rc = site.translate(comp)[::-1]
        hits: List[int] = []
        for pattern in {site, rc}:
            start = 0
            while True:
                idx = seq.find(pattern, start)
                if idx == -1:
                    break
                hits.append(idx)
                start = idx + 1
        if hits:
            out[name] = sorted(set(hits))
    return out


def free_cysteines(protein: str) -> List[int]:
    """1-based positions of cysteines (candidates for removal unless functional)."""
    return [i + 1 for i, aa in enumerate(protein.upper()) if aa == "C"]


@dataclass
class DesignRecord:
    design_id: str
    protein_seq: str
    catalytic_residues: List[str] = field(default_factory=list)
    cluster: str = ""
    score: Optional[float] = None
    motif_ca_rmsd: Optional[float] = None
    plddt: Optional[float] = None
    worst_preorg: Optional[float] = None
    dna_seq: str = ""
    notes: str = ""

    def __post_init__(self) -> None:
        bad = set(self.protein_seq.upper()) - _AA
        if bad:
            raise RegistryError(
                f"{self.design_id}: non-standard residues in sequence: {sorted(bad)}"
            )

    def pre_synthesis_warnings(
        self, enzymes: Optional[Dict[str, str]] = None
    ) -> List[str]:
        """Flag issues to resolve before ordering (Stage 6, step 15)."""
        warns: List[str] = []
        cys = free_cysteines(self.protein_seq)
        if cys:
            warns.append(f"free cysteine(s) at {cys} (remove unless functional)")
        if self.dna_seq:
            sites = restriction_sites(self.dna_seq, enzymes)
            if sites:
                warns.append(f"internal restriction site(s): {sites}")
            if len(self.dna_seq) % 3 != 0:
                warns.append("DNA length not a multiple of 3")
        return warns


_LIST_FIELDS = {"catalytic_residues"}


class ConstructRegistry:
    """An ordered collection of :class:`DesignRecord` with CSV I/O."""

    def __init__(self) -> None:
        self._records: Dict[str, DesignRecord] = {}

    def add(self, record: DesignRecord) -> None:
        if record.design_id in self._records:
            raise RegistryError(f"duplicate design_id {record.design_id!r}")
        self._records[record.design_id] = record

    def get(self, design_id: str) -> DesignRecord:
        return self._records[design_id]

    def __len__(self) -> int:
        return len(self._records)

    def __iter__(self):
        return iter(self._records.values())

    def records(self) -> List[DesignRecord]:
        return list(self._records.values())

    def panel(self, design_ids: Sequence[str]) -> "ConstructRegistry":
        """Return a sub-registry for the chosen experimental panel."""
        sub = ConstructRegistry()
        for did in design_ids:
            sub.add(self._records[did])
        return sub

    # -- CSV ----------------------------------------------------------------
    def to_csv(self, path: str) -> None:
        cols = list(asdict(next(iter(self._records.values()))).keys()) if self._records else []
        with open(path, "w", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=cols)
            writer.writeheader()
            for rec in self._records.values():
                row = asdict(rec)
                for lf in _LIST_FIELDS:
                    row[lf] = ";".join(row[lf])
                writer.writerow(row)

    @classmethod
    def from_csv(cls, path: str) -> "ConstructRegistry":
        reg = cls()
        with open(path, newline="") as fh:
            for row in csv.DictReader(fh):
                kwargs = dict(row)
                for lf in _LIST_FIELDS:
                    raw = (kwargs.get(lf) or "").strip()
                    kwargs[lf] = raw.split(";") if raw else []
                for fl in ("score", "motif_ca_rmsd", "plddt", "worst_preorg"):
                    raw = (kwargs.get(fl) or "").strip()
                    kwargs[fl] = float(raw) if raw else None
                reg.add(DesignRecord(**kwargs))  # type: ignore[arg-type]
        return reg
