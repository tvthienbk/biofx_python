"""
enzyme_tools.py — theozyme → scaffold → sequence → catalytic-geometry helpers for Project 18
(De Novo Kemp Eliminase). This is the ENZYME-FAMILY TEMPLATE: Projects 19–21 and 24 reuse this
shape (theozyme construction, motif scaffolding, catalytic-residue-fixed sequence design,
catalytic-geometry RMSD, substrate docking) and swap in their own reaction/active-site.

DESIGN NOTE FOR STUDENTS
------------------------
The real backends (RFdiffusion2 / Riff-Diff scaffolding, LigandMPNN, AutoDock Vina, OpenMM) are
heavy, GPU/A100-bound, and environment-specific. So every function here ships a deterministic
`mock` backend that runs anywhere with NO GPU and NO heavy installs — it lets you build and unit-
test the *plumbing* (theozyme spec, file bookkeeping, geometry scoring, aggregation) before you
spend A100 time. The real backends are written as clearly-marked TODOs you wire up on Colab/HPC.

EVERY number the mock backend returns is SYNTHETIC by construction (seeded hash of the inputs).
Never present a mock value as a real result — flag it `SYNTHETIC` / `EXAMPLE_DATA` in any figure.

Realistic expectations (read MASTER_BLUEPRINT §0, §3): de novo enzyme design hit rates are LOW —
often <1% active *without* directed evolution, and recent methods, while much better, still need
screening. Preserving the catalytic geometry in silico does NOT guarantee catalysis; only a
kinetic assay can. This module triages; it does not promise an enzyme.

Import-safe: this file imports with only the standard library. `numpy` is imported lazily inside
the one function that needs it. Run `python enzyme_tools.py` for a no-GPU smoke test.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field, asdict
from typing import Optional


# --------------------------------------------------------------------------------------- #
# Determinism helper — turn any string into a stable pseudo-random stream (no numpy needed).
# --------------------------------------------------------------------------------------- #
def _seed_from(*parts) -> int:
    key = "|".join(str(p) for p in parts).encode()
    return int(hashlib.sha256(key).hexdigest(), 16)


def _unit(seed: int, salt: str) -> float:
    """Deterministic float in [0, 1) from a seed + a salt label."""
    h = hashlib.sha256(f"{seed}:{salt}".encode()).hexdigest()
    return (int(h[:8], 16) % 1_000_000) / 1_000_000.0


# --------------------------------------------------------------------------------------- #
# Data model: a theozyme (the "theoretical enzyme" — the catalytic functional groups + the
# geometry they must hold around the transition state).
# --------------------------------------------------------------------------------------- #
@dataclass
class FunctionalGroup:
    """One catalytic functional group placed relative to the bound transition state (TS)."""
    role: str                 # e.g. "catalytic_base", "pi_stack", "h_bond_donor"
    residue: str              # candidate amino acid (e.g. "ASP"/"GLU", "TRP"/"TYR", "SER"/"THR")
    atom: str                 # the key atom that contacts the TS (e.g. "OD2", "ring", "OG")
    target_distance: float    # ideal distance (Å) from `atom` to the TS contact point
    target_angle: Optional[float] = None  # ideal angle (deg), where geometry-defining
    note: str = ""


@dataclass
class Theozyme:
    """A minimal active-site definition: the reaction, the TS contact, and the functional groups."""
    reaction: str
    substrate: str
    ts_description: str
    functional_groups: list = field(default_factory=list)
    provenance: str = "TEMPLATE — student fills geometry from literature/QM (see data/inputs/theozyme_def.txt)"

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    def catalytic_residue_ids(self) -> list:
        """Roles whose residues must be FIXED during sequence design."""
        return [fg.role for fg in self.functional_groups]


# --------------------------------------------------------------------------------------- #
# build_theozyme(reaction) → a functional-group geometry spec.
# --------------------------------------------------------------------------------------- #
def build_theozyme(reaction: str = "kemp_elimination") -> Theozyme:
    """Construct a teaching theozyme for the given reaction.

    For the Kemp elimination of 5-nitrobenzisoxazole, the canonical minimal motif is:
      - a catalytic BASE (Asp or Glu carboxylate) that abstracts the benzisoxazole C3 proton,
      - an aromatic PI-STACK (Trp/Tyr/Phe) that binds and orients the planar substrate and
        helps delocalize developing negative charge in the TS,
      - an H-BOND DONOR (Ser/Thr/backbone amide) that stabilizes the developing phenolate/
        nitro oxygen as the isoxazole ring opens.

    The exact distances/angles below are TEMPLATE PLACEHOLDERS. Students MUST replace them with
    values built from the literature (Röthlisberger 2008; KE07/KE70/HG3 lineage) and/or a QM
    transition-state calculation. This function is the family-template hook: Projects 19/21
    (Ser-His-Asp triad + oxyanion hole), 20 (Zn-His3-OH), 24 (cofactor coordination) override the
    `functional_groups` list with their own catalytic motif.
    """
    reaction = reaction.lower()
    if reaction not in ("kemp_elimination", "kemp"):
        raise NotImplementedError(
            f"build_theozyme only ships the Kemp motif as a template; got {reaction!r}. "
            "Override functional_groups for your reaction (see docstring).")
    fgs = [
        FunctionalGroup(role="catalytic_base", residue="ASP", atom="OD2",
                        target_distance=2.8, target_angle=120.0,
                        note="PLACEHOLDER geometry — carboxylate O abstracts C3-H; GLU is the alt."),
        FunctionalGroup(role="pi_stack", residue="TRP", atom="ring",
                        target_distance=3.8, target_angle=None,
                        note="PLACEHOLDER — aromatic face stacks the planar benzisoxazole; TYR/PHE alt."),
        FunctionalGroup(role="h_bond_donor", residue="SER", atom="OG",
                        target_distance=3.0, target_angle=150.0,
                        note="PLACEHOLDER — stabilizes developing phenolate/nitro O; backbone amide alt."),
    ]
    return Theozyme(
        reaction="Kemp elimination (base-catalysed ring opening of benzisoxazole)",
        substrate="5-nitrobenzisoxazole (chromogenic; product 2-hydroxy-5-nitrobenzonitrile, UV-readable)",
        ts_description="TEMPLATE — deprotonation at C3 concerted with N–O bond cleavage; "
                       "fill the TS contact geometry from QM/literature.",
        functional_groups=fgs,
    )


# --------------------------------------------------------------------------------------- #
# scaffold_motif(theozyme, n, method) → candidate backbones holding the motif.
# --------------------------------------------------------------------------------------- #
def scaffold_motif(theozyme: Theozyme, n: int = 8, method: str = "mock",
                   out_dir: str = "results/scaffolds") -> list:
    """Generate `n` candidate backbones that present the theozyme motif.

    Real backends (wire up on an A100 / HPC — scaffolding is the A100-bound step):
      method="rfdiffusion2"  → RFdiffusion2 all-atom motif scaffolding (Dauparas 2025);
                               VERIFY the current public release/repo at generation time.
      method="riffdiff"      → Riff-Diff theozyme-to-enzyme scaffolding (Schnettler 2025, Nature);
                               VERIFY the current public release/repo at generation time.
      method="rfdiffusion"   → classic RFdiffusion motif scaffolding (RosettaCommons/RFdiffusion),
                               a smaller free-tier demo; good for the P1 hello-world.

    The mock backend returns deterministic placeholder records so the pipeline runs with no GPU.
    Each record's `motif_rmsd` etc. are SYNTHETIC.

    >>> A100 NOTE: scaffolding 1000s of backbones is the compute bottleneck. Free Colab T4 can do a
        small RFdiffusion motif-scaffolding DEMO (tens of backbones); the real campaign (1000s,
        RFdiffusion2/Riff-Diff) wants an A100 (Colab Pro+) or an HPC GPU. Plan batch sizes around it.
    """
    os.makedirs(out_dir, exist_ok=True)
    method = method.lower()
    real = {"rfdiffusion2", "riffdiff", "rfdiffusion"}
    if method in real:
        # TODO(student): call the chosen scaffolding backend here on Colab/HPC.
        #   - export the theozyme as the tool's motif/constraint format (contigs + ligand/TS),
        #   - run N backbones (1000s for the real campaign — A100),
        #   - return one record per written backbone PDB.
        raise NotImplementedError(
            f"Wire up the real '{method}' scaffolding backend (A100/HPC). "
            "See the docstring; verify the current RFdiffusion2/Riff-Diff release at generation time.")
    if method != "mock":
        raise ValueError(f"unknown method {method!r}; options: mock | {' | '.join(sorted(real))}")

    base = _seed_from(theozyme.reaction, theozyme.substrate, n)
    records = []
    for i in range(n):
        s = base ^ _seed_from("scaffold", i)
        rec = {
            "design_id": f"EXAMPLE_DATA_scaffold_{i:03d}",
            "method": "mock",
            "backbone_pdb": None,  # real backend writes a PDB path here
            "length": 110 + int(_unit(s, "len") * 80),       # 110–190 aa, SYNTHETIC
            "motif_rmsd": round(0.2 + _unit(s, "motif") * 1.2, 3),   # Å, SYNTHETIC
            "catalytic_residues": theozyme.catalytic_residue_ids(),
            "synthetic": True,
        }
        records.append(rec)
    with open(os.path.join(out_dir, "scaffolds_mock.json"), "w") as fh:
        json.dump(records, fh, indent=2)
    return records


# --------------------------------------------------------------------------------------- #
# ligandmpnn_fix_catalytic(backbone, catalytic_residues, n) → sequences with the motif FIXED.
# --------------------------------------------------------------------------------------- #
def ligandmpnn_fix_catalytic(backbone: dict, catalytic_residues: list, n: int = 8,
                             tool: str = "mock") -> list:
    """Design `n` sequences for one backbone, FIXING the catalytic residues (the whole point).

    Real backend (CPU-fast — this step is cheap, unlike scaffolding):
      tool="ligandmpnn" → LigandMPNN (https://github.com/dauparas/LigandMPNN). Pass the ligand/TS
                          context and a fixed-positions list so the catalytic base / pi-stack /
                          H-bond donor are NOT redesigned. This ligand-awareness is exactly why
                          LigandMPNN (not vanilla ProteinMPNN) is the right tool for enzymes.

    The mock backend returns deterministic placeholder sequences (the catalytic positions are
    annotated as fixed). All scores are SYNTHETIC.
    """
    tool = tool.lower()
    if tool == "ligandmpnn":
        # TODO(student): run LigandMPNN with --fixed_residues (or the JSON fixed-positions spec)
        #   covering every catalytic residue, plus the ligand/TS context PDB. Parse the FASTA out.
        raise NotImplementedError(
            "Wire up LigandMPNN (CPU-fast): pass the ligand/TS context + a fixed-positions list for "
            "the catalytic residues so they are preserved. https://github.com/dauparas/LigandMPNN")
    if tool != "mock":
        raise ValueError(f"unknown tool {tool!r}; options: mock | ligandmpnn")

    bid = backbone.get("design_id", "bb")
    length = int(backbone.get("length", 140))
    seqs = []
    aa = "ACDEFGHIKLMNPQRSTVWY"
    for j in range(n):
        s = _seed_from(bid, "ligandmpnn", j)
        # Deterministic pseudo-sequence (SYNTHETIC; not a real design).
        seq = "".join(aa[(_seed_from(bid, j, k) >> 3) % 20] for k in range(length))
        seqs.append({
            "design_id": f"{bid}_seq{j:02d}",
            "sequence": seq,
            "fixed_catalytic_roles": list(catalytic_residues),
            "mpnn_score": round(0.8 + _unit(s, "mpnn") * 0.6, 3),  # SYNTHETIC (lower ~ more confident)
            "tool": "mock",
            "synthetic": True,
        })
    return seqs


# --------------------------------------------------------------------------------------- #
# catalytic_geometry_rmsd(predicted_pdb, theozyme) → the KEY enzyme metric.
# --------------------------------------------------------------------------------------- #
def catalytic_geometry_rmsd(predicted_pdb: Optional[str], theozyme: Theozyme) -> float:
    """RMSD (Å) of the predicted catalytic functional-group atoms vs the theozyme target geometry.

    This is THE enzyme metric: catalytic-geometry RMSD < 0.5 Å vs the theozyme is the pass bar
    (DEFAULT_CUTOFFS['enzyme']['cat_geom'] in the shared filter). A design can fold beautifully
    (high pLDDT) yet present the catalytic atoms in the wrong place — only this metric catches that.

    Real implementation (wire up with the AF2/predicted PDB):
      - parse the predicted structure (Biopython),
      - extract the catalytic atoms (the `atom` of each FunctionalGroup at the designed positions),
      - superpose onto the theozyme target placement and return the RMSD over those atoms.
    A teaching-grade Cα/atom superposition helper already exists in shared/filtering_pipeline.ca_rmsd;
    here you need an ATOM-level (not Cα) RMSD over just the catalytic atoms.

    The mock path (predicted_pdb is None or missing) returns a deterministic SYNTHETIC value seeded
    by the theozyme + path, so the filtering plumbing runs with no real structure.
    """
    if predicted_pdb and os.path.exists(predicted_pdb):
        # TODO(student): real atom-level RMSD over the catalytic functional-group atoms.
        raise NotImplementedError(
            "Implement atom-level RMSD over the catalytic atoms vs the theozyme target placement "
            "(parse with Biopython; superpose on the catalytic atoms only).")
    s = _seed_from(theozyme.reaction, str(predicted_pdb))
    # SYNTHETIC: spread around the 0.5 Å cutoff so the demo filter both passes and fails designs.
    return round(0.15 + _unit(s, "catgeom") * 0.9, 3)


# --------------------------------------------------------------------------------------- #
# dock_substrate(pocket, substrate, tool) → does the substrate fit the designed pocket?
# --------------------------------------------------------------------------------------- #
def dock_substrate(pocket: Optional[str], substrate: str = "5-nitrobenzisoxazole",
                   tool: str = "mock") -> dict:
    """Dock the substrate into the designed pocket as a fit/orientation sanity check.

    Real backend:
      tool="vina" → AutoDock Vina (https://github.com/ccsb-scripps/AutoDock-Vina). Prepare the
                    receptor (designed pocket) + the substrate ligand (PDBQT), define the box around
                    the active site, run, and read the top binding score + pose. Docking checks the
                    substrate physically fits and is oriented for catalysis — it is NOT an affinity
                    or activity measurement.

    Mock path returns a deterministic SYNTHETIC score + a placeholder pose flag.
    """
    tool = tool.lower()
    if tool == "vina":
        # TODO(student): receptor/ligand prep (PDBQT) → define box at the active site → run Vina →
        #   parse the best score + pose; check the substrate is oriented toward the catalytic base.
        raise NotImplementedError(
            "Wire up AutoDock Vina: prep receptor+ligand PDBQT, box the active site, run, parse the "
            "top score/pose. https://github.com/ccsb-scripps/AutoDock-Vina")
    if tool != "mock":
        raise ValueError(f"unknown tool {tool!r}; options: mock | vina")
    s = _seed_from(str(pocket), substrate)
    return {
        "substrate": substrate,
        "vina_score": round(-4.0 - _unit(s, "dock") * 4.0, 2),  # kcal/mol-ish, SYNTHETIC
        "pose_in_pocket": _unit(s, "pose") > 0.25,               # SYNTHETIC
        "tool": "mock",
        "synthetic": True,
    }


# --------------------------------------------------------------------------------------- #
# active_site_md(...) — optional short MD of active-site stability (OpenMM). Mock stub.
# --------------------------------------------------------------------------------------- #
def active_site_md(predicted_pdb: Optional[str], ns: float = 10.0, tool: str = "mock") -> dict:
    """Short MD to check the active site doesn't collapse/drift (OpenMM). Mock returns SYNTHETIC.

    Real backend: OpenMM (https://github.com/openmm/openmm) — solvate, minimize, short NPT run
    (10–50 ns feasible for small systems on a T4; long MD → HPC). Report catalytic-atom RMSF /
    mean backbone RMSD over the trajectory. (For metal sites in Projects 20/24, classical force
    fields are a known caveat — note it.)
    """
    tool = tool.lower()
    if tool == "openmm":
        # TODO(student): build system, minimize, equilibrate, run `ns`, compute active-site RMSF/RMSD.
        raise NotImplementedError(
            "Wire up OpenMM: solvate/minimize/equilibrate, run a short trajectory, report "
            "active-site RMSF + mean backbone RMSD. https://github.com/openmm/openmm")
    if tool != "mock":
        raise ValueError(f"unknown tool {tool!r}; options: mock | openmm")
    s = _seed_from(str(predicted_pdb), ns)
    return {
        "ns": ns,
        "md_rmsd": round(0.8 + _unit(s, "md") * 2.6, 3),          # Å, SYNTHETIC
        "catalytic_rmsf": round(0.3 + _unit(s, "rmsf") * 1.4, 3), # Å, SYNTHETIC
        "tool": "mock",
        "synthetic": True,
    }


if __name__ == "__main__":
    # No-GPU smoke test: theozyme → scaffold → LigandMPNN(fixed) → geometry → docking → MD.
    print("== enzyme_tools.py smoke test (mock backend; ALL NUMBERS SYNTHETIC) ==")
    theo = build_theozyme("kemp_elimination")
    print("theozyme:", theo.reaction)
    for fg in theo.functional_groups:
        print(f"  - {fg.role:14s} {fg.residue}/{fg.atom}  d={fg.target_distance}Å  {fg.note[:48]}")
    scaffolds = scaffold_motif(theo, n=3)
    print(f"scaffolds: {len(scaffolds)} (mock)  e.g. {scaffolds[0]['design_id']} "
          f"len={scaffolds[0]['length']} motif_rmsd={scaffolds[0]['motif_rmsd']}Å")
    seqs = ligandmpnn_fix_catalytic(scaffolds[0], theo.catalytic_residue_ids(), n=2)
    print(f"sequences for {scaffolds[0]['design_id']}: {len(seqs)} (catalytic roles fixed: "
          f"{seqs[0]['fixed_catalytic_roles']})")
    cg = catalytic_geometry_rmsd(None, theo)
    print(f"catalytic_geometry_rmsd (mock) = {cg} Å  (pass if < 0.5)")
    dock = dock_substrate(None)
    print(f"dock_substrate (mock): score={dock['vina_score']} in_pocket={dock['pose_in_pocket']}")
    md = active_site_md(None, ns=10.0)
    print(f"active_site_md (mock): md_rmsd={md['md_rmsd']}Å catalytic_rmsf={md['catalytic_rmsf']}Å")
    print("OK — plumbing runs with no GPU. Switch backends to rfdiffusion2/riffdiff/ligandmpnn/"
          "vina/openmm on Colab/HPC. NONE of these numbers are real.")
