"""
filtering_pipeline.py — Shared multi-layer in-silico filter for de novo protein design.

Used by every project's 03_filter_and_rank.ipynb so students learn ONE filtering API.
Implements the 4-layer filter from MASTER_BLUEPRINT.md §0 / validation-ref:

    Layer 1  self-consistency   (AF2/ESMFold scRMSD, pLDDT, pAE)        [fast, mandatory]
    Layer 2  orthogonal check   (second predictor agrees)              [recommended]
    Layer 3  physics            (solubility/aggregation, energy)        [leads]
    Layer 4  dynamics           (short MD stability)                    [optional, expensive]

Design philosophy: keep heavy tools (AF2, Rosetta, OpenMM) BEHIND clean function
boundaries. Students plug in predictions; this module scores, filters, ranks, reports.

NOTE: scRMSD here is a backbone (Cα) RMSD after superposition — a teaching-grade
implementation. For publication, use the alignment in the original design papers.

Dependencies: numpy, pandas, matplotlib, biopython.  (No GPU needed for scoring.)
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Optional
import numpy as np
import pandas as pd


# --------------------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------------------
@dataclass
class Design:
    """One designed protein (monomer, binder complex, enzyme, ...)."""
    design_id: str
    sequence: str
    design_type: str = "monomer"          # monomer | binder | enzyme | antibody | oligomer
    # populated by the student's prediction step (notebook 01/02):
    designed_pdb: Optional[str] = None     # path to the designed backbone
    predicted_pdb: Optional[str] = None    # path to AF2/ESMFold prediction of the sequence
    plddt: Optional[float] = None          # mean pLDDT (functional region if relevant)
    plddt_catalytic: Optional[float] = None
    pae_interaction: Optional[float] = None
    scrmsd: Optional[float] = None         # filled by self_consistency() if not provided
    scrmsd_orthogonal: Optional[float] = None
    tm_to_pdb: Optional[float] = None      # novelty: <0.5 == novel fold
    solubility: Optional[float] = None     # e.g. CamSol-style score
    rosetta_dG: Optional[float] = None     # interface energy for binders (REU)
    shape_complementarity: Optional[float] = None
    md_rmsd: Optional[float] = None        # mean backbone RMSD over a short MD
    catalytic_geom_rmsd: Optional[float] = None  # vs theozyme, for enzymes
    extra: dict = field(default_factory=dict)
    # filled by the pipeline:
    layers_passed: int = 0
    score: Optional[float] = None
    notes: list = field(default_factory=list)


# --------------------------------------------------------------------------------------
# Geometry helper: backbone Cα RMSD after Kabsch superposition
# --------------------------------------------------------------------------------------
def ca_rmsd(pdb_a: str, pdb_b: str) -> float:
    """Cα RMSD (Å) between two PDBs after optimal superposition. Teaching-grade."""
    from Bio.PDB import PDBParser, Superimposer
    p = PDBParser(QUIET=True)
    a = p.get_structure("a", pdb_a)
    b = p.get_structure("b", pdb_b)
    ca_a = [r["CA"] for r in a.get_residues() if "CA" in r]
    ca_b = [r["CA"] for r in b.get_residues() if "CA" in r]
    n = min(len(ca_a), len(ca_b))
    if n == 0:
        raise ValueError("No Cα atoms found / length mismatch.")
    sup = Superimposer()
    sup.set_atoms(ca_a[:n], ca_b[:n])
    return float(sup.rms)


# --------------------------------------------------------------------------------------
# Cutoffs by design type (from MASTER_BLUEPRINT / validation-ref). Override per project.
# --------------------------------------------------------------------------------------
DEFAULT_CUTOFFS = {
    "monomer":   dict(scrmsd=2.0, plddt=85, pae=None),
    "binder":    dict(scrmsd=2.5, plddt=80, pae=10, rosetta_dG=-30, sc=0.6),
    "enzyme":    dict(scrmsd=2.0, plddt=85, plddt_cat=90, cat_geom=0.5),
    "antibody":  dict(scrmsd=3.0, plddt=70, pae=12),
    "oligomer":  dict(scrmsd=2.5, plddt=80, pae=10),
}


# --------------------------------------------------------------------------------------
# Layer 1 — self-consistency (mandatory)
# --------------------------------------------------------------------------------------
def self_consistency(d: Design, cutoffs: dict) -> bool:
    """scRMSD + pLDDT (+ pAE for complexes). Computes scRMSD if PDBs are present."""
    if d.scrmsd is None and d.designed_pdb and d.predicted_pdb:
        d.scrmsd = ca_rmsd(d.designed_pdb, d.predicted_pdb)
    ok = True
    if cutoffs.get("scrmsd") is not None:
        ok &= (d.scrmsd is not None and d.scrmsd <= cutoffs["scrmsd"])
    if cutoffs.get("plddt") is not None:
        ok &= (d.plddt is not None and d.plddt >= cutoffs["plddt"])
    if cutoffs.get("plddt_cat") is not None:
        ok &= (d.plddt_catalytic is not None and d.plddt_catalytic >= cutoffs["plddt_cat"])
    if cutoffs.get("pae") is not None:
        ok &= (d.pae_interaction is not None and d.pae_interaction <= cutoffs["pae"])
    if cutoffs.get("cat_geom") is not None:
        ok &= (d.catalytic_geom_rmsd is not None and d.catalytic_geom_rmsd <= cutoffs["cat_geom"])
    if ok:
        d.layers_passed = max(d.layers_passed, 1)
    else:
        d.notes.append("failed L1 self-consistency")
    return ok


# --------------------------------------------------------------------------------------
# Layer 2 — orthogonal prediction agreement
# --------------------------------------------------------------------------------------
def orthogonal_check(d: Design, max_scrmsd: float = 2.5) -> bool:
    """A second predictor (ESMFold/Boltz) should agree with the design."""
    ok = (d.scrmsd_orthogonal is not None and d.scrmsd_orthogonal <= max_scrmsd)
    if ok:
        d.layers_passed = max(d.layers_passed, 2)
    else:
        d.notes.append("failed L2 orthogonal")
    return ok


# --------------------------------------------------------------------------------------
# Layer 3 — physics-based checks
# --------------------------------------------------------------------------------------
def physics_filter(d: Design, cutoffs: dict, min_solubility: float = -1.0) -> bool:
    """Solubility/aggregation + (for binders) interface energy & shape complementarity."""
    ok = True
    if d.solubility is not None:
        ok &= d.solubility >= min_solubility
    if cutoffs.get("rosetta_dG") is not None and d.rosetta_dG is not None:
        ok &= d.rosetta_dG <= cutoffs["rosetta_dG"]
    if cutoffs.get("sc") is not None and d.shape_complementarity is not None:
        ok &= d.shape_complementarity >= cutoffs["sc"]
    if ok:
        d.layers_passed = max(d.layers_passed, 3)
    else:
        d.notes.append("failed L3 physics")
    return ok


# --------------------------------------------------------------------------------------
# Layer 4 — dynamics (optional)
# --------------------------------------------------------------------------------------
def dynamics_filter(d: Design, max_md_rmsd: float = 3.0) -> bool:
    """Structure should not drift far from the design over a short MD run."""
    ok = (d.md_rmsd is not None and d.md_rmsd <= max_md_rmsd)
    if ok:
        d.layers_passed = max(d.layers_passed, 4)
    else:
        d.notes.append("failed L4 dynamics")
    return ok


# --------------------------------------------------------------------------------------
# Ranking
# --------------------------------------------------------------------------------------
def rank_designs(designs: list[Design]) -> list[Design]:
    """Composite score (higher = better). Tune weights per project in the notebook."""
    for d in designs:
        s = 0.0
        if d.plddt is not None:
            s += d.plddt / 100.0
        if d.scrmsd is not None:
            s += max(0.0, 2.5 - d.scrmsd)            # reward low scRMSD
        if d.pae_interaction is not None:
            s += max(0.0, (12 - d.pae_interaction) / 12.0)
        if d.rosetta_dG is not None:
            s += max(0.0, (-d.rosetta_dG) / 50.0)    # reward more-negative dG
        s += 0.25 * d.layers_passed                  # reward passing more layers
        d.score = round(s, 4)
    return sorted(designs, key=lambda x: (x.layers_passed, x.score or 0), reverse=True)


# --------------------------------------------------------------------------------------
# Orchestration + report
# --------------------------------------------------------------------------------------
def run_pipeline(designs: list[Design], design_type: str = "monomer",
                 cutoffs: Optional[dict] = None, use_layers=(1, 2, 3)) -> pd.DataFrame:
    """Run the chosen layers, rank, and return a tidy DataFrame. Records survival counts."""
    cutoffs = cutoffs or DEFAULT_CUTOFFS.get(design_type, DEFAULT_CUTOFFS["monomer"])
    survival = {f"L{i}": 0 for i in use_layers}
    for d in designs:
        d.design_type = design_type
        passed = True
        if 1 in use_layers:
            passed = self_consistency(d, cutoffs);            survival["L1"] += int(passed)
        if passed and 2 in use_layers:
            passed = orthogonal_check(d);                      survival["L2"] += int(passed)
        if passed and 3 in use_layers:
            passed = physics_filter(d, cutoffs);               survival["L3"] += int(passed)
        if passed and 4 in use_layers:
            passed = dynamics_filter(d);                       survival["L4"] = survival.get("L4", 0) + int(passed)
    ranked = rank_designs(designs)
    df = pd.DataFrame([asdict(d) for d in ranked])
    df.attrs["survival"] = survival
    df.attrs["n_total"] = len(designs)
    return df


def report(df: pd.DataFrame, top_n: int = 20, save_prefix: Optional[str] = None):
    """Print hit-rate accounting + survival-at-each-layer figure; return the top-N table."""
    import matplotlib.pyplot as plt
    n_total = df.attrs.get("n_total", len(df))
    survival = df.attrs.get("survival", {})
    print(f"Total designs: {n_total}")
    for layer, n in survival.items():
        print(f"  {layer} survivors: {n}  ({100*n/max(n_total,1):.1f}%)")
    if survival:
        fig, ax = plt.subplots(figsize=(5, 3))
        labels = ["total"] + list(survival.keys())
        vals = [n_total] + list(survival.values())
        ax.bar(labels, vals)
        ax.set_ylabel("designs surviving")
        ax.set_title("Survival at each filter layer")
        for i, v in enumerate(vals):
            ax.text(i, v, str(v), ha="center", va="bottom", fontsize=9)
        plt.tight_layout()
        if save_prefix:
            plt.savefig(f"{save_prefix}_survival.png", dpi=200)
        plt.show()
    cols = [c for c in ["design_id", "design_type", "layers_passed", "score",
                        "scrmsd", "plddt", "pae_interaction", "rosetta_dG", "tm_to_pdb"]
            if c in df.columns]
    top = df.head(top_n)[cols]
    if save_prefix:
        df.to_csv(f"{save_prefix}_ranked.csv", index=False)
    return top


if __name__ == "__main__":
    # Smoke test with EXAMPLE_DATA (clearly synthetic — never present as real results).
    rng = np.random.default_rng(0)
    demo = [Design(design_id=f"EXAMPLE_DATA_{i}", sequence="M",
                   scrmsd=float(rng.uniform(0.8, 4.0)),
                   plddt=float(rng.uniform(60, 95)),
                   scrmsd_orthogonal=float(rng.uniform(0.8, 4.0)),
                   solubility=float(rng.uniform(-2, 1))) for i in range(200)]
    out = run_pipeline(demo, design_type="monomer")
    print(report(out, top_n=5))
