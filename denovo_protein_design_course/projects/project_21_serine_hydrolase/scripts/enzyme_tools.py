"""
enzyme_tools.py — theozyme → scaffold → sequence → catalytic-geometry → POCKET / SUBSTRATE-SCOPE
helpers for Project 21 (De Novo Serine Hydrolase / Esterase, Green Chemistry). This follows the
ENZYME-FAMILY TEMPLATE established by Project 18 (Kemp eliminase) — theozyme construction, motif
scaffolding, catalytic-residue-fixed sequence design, catalytic-geometry RMSD, substrate docking,
short active-site MD — and swaps in this project's reaction (ester hydrolysis via a Ser-His-Asp triad
+ oxyanion hole) and EMPHASIS: a clean catalytic-geometry-filtered set, POCKET ACCESSIBILITY, and
SUBSTRATE-SCOPE reasoning (acyl-chain length), feeding a pNP-ester steady-state kinetics plan with a
catalytic-Ser→Ala "dead" mutant as the perfect negative control. The headline this reproduces is the
2025 Science de novo serine-hydrolase result (Lauko 2025).

This is the GREEN-CHEMISTRY / BIOCATALYSIS framing of the serine hydrolase: synthesis, kinetic
resolution, and detergent esterases are the industrial workhorses. (Project 19 reuses the same triad
chemistry but emphasises THERMOSTABILITY for PET degradation; Project 21 emphasises the
geometry→pocket→substrate-scope→kinetics path for a general esterase.)

DESIGN NOTE FOR STUDENTS
------------------------
The real backends (RFdiffusion2 / Riff-Diff scaffolding, LigandMPNN, AutoDock Vina, OpenMM) are
heavy, GPU/A100-bound, and environment-specific. So every function here ships a deterministic `mock`
backend that runs anywhere with NO GPU and NO heavy installs — it lets you build and unit-test the
*plumbing* (theozyme spec, file bookkeeping, geometry scoring, pocket/substrate-scope aggregation)
before you spend A100 time. The real backends are written as clearly-marked TODOs you wire up on
Colab/HPC.

EVERY number the mock backend returns is SYNTHETIC by construction (seeded hash of the inputs).
Never present a mock value as a real result — flag it `SYNTHETIC` / `EXAMPLE_DATA` in any figure, and
NEVER fabricate a kcat, a KM, or an enantiomeric excess.

Realistic expectations (read MASTER_BLUEPRINT §0, §3): de novo enzyme design hit rates are LOW —
often <5% active *without* directed evolution, and recent methods, while much better, still need
screening. Preserving the catalytic geometry in silico does NOT guarantee catalysis; only a kinetic
assay (pNP-ester steady-state kinetics) decides, and the catalytic-Ser→Ala dead mutant is what proves
any rate is real. This module triages and ranks; it does not promise an enzyme.

Import-safe: this file imports with only the standard library. `numpy` is imported lazily inside the
one function that needs it. Run `python enzyme_tools.py` for a no-GPU smoke test.
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
# geometry they must hold around the transition state / tetrahedral intermediate).
# --------------------------------------------------------------------------------------- #
@dataclass
class FunctionalGroup:
    """One catalytic functional group placed relative to the bound transition state (TS)."""
    role: str                 # e.g. "catalytic_ser", "catalytic_his", "catalytic_asp", "oxyanion_donor"
    residue: str              # candidate amino acid (e.g. "SER", "HIS", "ASP"/"GLU", "backbone-NH")
    atom: str                 # the key atom that contacts the TS (e.g. "OG", "NE2", "OD2", "N")
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
        """Roles whose residues must be FIXED during sequence design (triad + oxyanion hole)."""
        return [fg.role for fg in self.functional_groups]


# --------------------------------------------------------------------------------------- #
# build_theozyme(reaction) → a functional-group geometry spec.
# --------------------------------------------------------------------------------------- #
def build_theozyme(reaction: str = "ester_hydrolysis") -> Theozyme:
    """Construct a teaching theozyme for the given reaction.

    For ESTER HYDROLYSIS (the serine-hydrolase mechanism), the canonical minimal motif is the
    Ser-His-Asp catalytic triad + an oxyanion hole:
      - a catalytic SER (Ser-OG nucleophile) that attacks the ester carbonyl carbon,
      - a catalytic HIS (His-NE2 general base) that deprotonates Ser-OH to activate the nucleophile,
      - a catalytic ASP/GLU (carboxylate) that orients/protonates His (the charge-relay),
      - an OXYANION HOLE (two H-bond donors — typically backbone amide NHs) that stabilises the
        developing oxyanion of the tetrahedral intermediate (easy to forget, decisive for catalysis).

    The exact distances/angles below are TEMPLATE PLACEHOLDERS. Students MUST replace them with
    values built from the literature (a classic alpha/beta-hydrolase / lipase / cutinase; Lauko 2025
    de novo serine hydrolases) and/or a QM tetrahedral-intermediate calculation. This function is the
    family-template hook (cf. Project 18's Kemp motif): override the `functional_groups` list for your
    reaction's catalytic geometry.

    EMPHASIS for this project: a clean catalytic-geometry-filtered set + POCKET ACCESSIBILITY +
    SUBSTRATE-SCOPE (acyl-chain length). The triad chemistry is known; the campaign is decided by
    whether a real, open pocket holds it and admits the ester — see `dock_substrate` and
    `substrate_scope_scan`.
    """
    reaction = reaction.lower()
    if reaction not in ("ester_hydrolysis", "ester", "serine_hydrolase", "esterase"):
        raise NotImplementedError(
            f"build_theozyme only ships the serine-hydrolase (ester-hydrolysis) motif as a template; "
            f"got {reaction!r}. Override functional_groups for your reaction (see docstring).")
    fgs = [
        FunctionalGroup(role="catalytic_ser", residue="SER", atom="OG",
                        target_distance=2.9, target_angle=105.0,
                        note="PLACEHOLDER geometry — Ser-OG attacks the ester carbonyl C (Burgi-Dunitz)."),
        FunctionalGroup(role="catalytic_his", residue="HIS", atom="NE2",
                        target_distance=3.0, target_angle=120.0,
                        note="PLACEHOLDER — His-NE2 deprotonates Ser-OH (general base)."),
        FunctionalGroup(role="catalytic_asp", residue="ASP", atom="OD2",
                        target_distance=2.8, target_angle=120.0,
                        note="PLACEHOLDER — Asp/Glu orients/protonates His (charge-relay); GLU is the alt."),
        FunctionalGroup(role="oxyanion_donor_1", residue="backbone-NH", atom="N",
                        target_distance=3.0, target_angle=150.0,
                        note="PLACEHOLDER — backbone amide NH donates to the oxyanion (tetrahedral intermediate)."),
        FunctionalGroup(role="oxyanion_donor_2", residue="backbone-NH", atom="N",
                        target_distance=3.0, target_angle=150.0,
                        note="PLACEHOLDER — second oxyanion-hole donor (backbone NH or Ser-OG); FIX it too."),
    ]
    return Theozyme(
        reaction="Ester hydrolysis (serine-hydrolase Ser-His-Asp triad + oxyanion hole; general esterase)",
        substrate="chromogenic ester (fast screen: p-nitrophenyl acetate/butyrate, product pNP-olate ~405 nm; "
                  "acyl-chain scan probes substrate scope)",
        ts_description="TEMPLATE — Ser-OG nucleophilic attack on the carbonyl C forming the tetrahedral "
                       "intermediate, oxyanion stabilised by the oxyanion hole; fill the TS geometry from QM/literature.",
        functional_groups=fgs,
    )


# --------------------------------------------------------------------------------------- #
# scaffold_motif(theozyme, n, method) → candidate backbones holding the motif.
# --------------------------------------------------------------------------------------- #
def scaffold_motif(theozyme: Theozyme, n: int = 8, method: str = "mock",
                   out_dir: str = "results/scaffolds") -> list:
    """Generate `n` candidate backbones that present the theozyme motif (triad + oxyanion hole).

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
        RFdiffusion2/Riff-Diff) wants an A100 (Colab Pro+) or an HPC GPU. Bias toward compact
        alpha/beta-hydrolase-like topologies with a solvent-accessible pocket. Plan batch sizes around it.
    """
    os.makedirs(out_dir, exist_ok=True)
    method = method.lower()
    real = {"rfdiffusion2", "riffdiff", "rfdiffusion"}
    if method in real:
        # TODO(student): call the chosen scaffolding backend here on Colab/HPC.
        #   - export the theozyme as the tool's motif/constraint format (contigs + ligand/ester TS),
        #   - run N backbones (1000s for the real campaign — A100); bias toward an open, accessible pocket,
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
            "length": 200 + int(_unit(s, "len") * 100),     # 200–300 aa (alpha/beta-hydrolase-like), SYNTHETIC
            "motif_rmsd": round(0.2 + _unit(s, "motif") * 1.2, 3),   # Å, SYNTHETIC
            "catalytic_residues": theozyme.catalytic_residue_ids(),
            "synthetic": True,
        }
        records.append(rec)
    with open(os.path.join(out_dir, "scaffolds_mock.json"), "w") as fh:
        json.dump(records, fh, indent=2)
    return records


# --------------------------------------------------------------------------------------- #
# ligandmpnn_fix_catalytic(backbone, catalytic_residues, n) → sequences with the triad FIXED.
# --------------------------------------------------------------------------------------- #
def ligandmpnn_fix_catalytic(backbone: dict, catalytic_residues: list, n: int = 8,
                             tool: str = "mock") -> list:
    """Design `n` sequences for one backbone, FIXING the catalytic triad + oxyanion hole (the point).

    Real backend (CPU-fast — this step is cheap, unlike scaffolding):
      tool="ligandmpnn" → LigandMPNN (https://github.com/dauparas/LigandMPNN). Pass the ligand/ester-TS
                          context and a fixed-positions list so the catalytic Ser/His/Asp AND the
                          oxyanion-hole donors are NOT redesigned. This ligand-awareness is exactly why
                          LigandMPNN (not vanilla ProteinMPNN) is the right tool for enzymes. You MAY
                          line the pocket toward a target acyl-chain length — never touch the triad.

    The mock backend returns deterministic placeholder sequences (the catalytic positions are
    annotated as fixed). All scores are SYNTHETIC.
    """
    tool = tool.lower()
    if tool == "ligandmpnn":
        # TODO(student): run LigandMPNN with --fixed_residues (or the JSON fixed-positions spec)
        #   covering every catalytic residue (Ser, His, Asp) AND the oxyanion-hole donors, plus the
        #   ligand/ester-TS context PDB. Parse the FASTA out.
        raise NotImplementedError(
            "Wire up LigandMPNN (CPU-fast): pass the ligand/ester-TS context + a fixed-positions list "
            "for the triad AND the oxyanion-hole donors so they are preserved. "
            "https://github.com/dauparas/LigandMPNN")
    if tool != "mock":
        raise ValueError(f"unknown tool {tool!r}; options: mock | ligandmpnn")

    bid = backbone.get("design_id", "bb")
    length = int(backbone.get("length", 250))
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
# make_dead_mutant(sequence, catalytic_ser_index) → the catalytic-Ser→Ala negative control.
# --------------------------------------------------------------------------------------- #
def make_dead_mutant(sequence: str, catalytic_ser_index: int) -> str:
    """Return the catalytic-Ser→Ala 'dead' mutant sequence — the PERFECT negative control.

    Mutating the nucleophilic serine to alanine removes the OG nucleophile while changing nothing
    else (same fold, same pocket, same expression behaviour). Any activity that survives this mutation
    is NOT triad catalysis — so the dead mutant is what proves a measured rate is real (see notebook
    05's assay plan). `catalytic_ser_index` is 0-based into `sequence` (the designed Ser position).

    This is a sequence-edit helper, not a backend — it runs anywhere. It validates the index points
    at a Ser so you cannot silently make the wrong control.
    """
    if not 0 <= catalytic_ser_index < len(sequence):
        raise IndexError(f"catalytic_ser_index {catalytic_ser_index} out of range for len {len(sequence)}")
    if sequence[catalytic_ser_index] != "S":
        raise ValueError(
            f"position {catalytic_ser_index} is {sequence[catalytic_ser_index]!r}, not 'S' (Ser). "
            "Point it at the catalytic serine before making the dead mutant.")
    return sequence[:catalytic_ser_index] + "A" + sequence[catalytic_ser_index + 1:]


# --------------------------------------------------------------------------------------- #
# catalytic_geometry_rmsd(predicted_pdb, theozyme) → the KEY enzyme geometry metric.
# --------------------------------------------------------------------------------------- #
def catalytic_geometry_rmsd(predicted_pdb: Optional[str], theozyme: Theozyme) -> float:
    """RMSD (Å) of the predicted catalytic functional-group atoms vs the theozyme target geometry.

    This is THE enzyme geometry metric: catalytic-geometry RMSD < 0.5 Å vs the theozyme is the pass
    bar (DEFAULT_CUTOFFS['enzyme']['cat_geom'] in the shared filter). A design can fold beautifully
    (high pLDDT) yet present the triad / oxyanion-hole atoms in the wrong place — only this metric
    catches that. (Beyond geometry, this project then checks POCKET ACCESSIBILITY and SUBSTRATE SCOPE
    — see `dock_substrate` and `substrate_scope_scan`.)

    Real implementation (wire up with the AF2/predicted PDB):
      - parse the predicted structure (Biopython),
      - extract the catalytic atoms (Ser-OG, His-NE2, Asp-OD + the oxyanion-hole donor N/OG atoms),
      - superpose onto the theozyme target placement and return the RMSD over those atoms.
    A teaching-grade Cα/atom superposition helper exists in shared/filtering_pipeline.ca_rmsd; here
    you need an ATOM-level (not Cα) RMSD over just the catalytic atoms.

    The mock path (predicted_pdb is None or missing) returns a deterministic SYNTHETIC value seeded
    by the theozyme + path, so the filtering plumbing runs with no real structure.
    """
    if predicted_pdb and os.path.exists(predicted_pdb):
        # TODO(student): real atom-level RMSD over the catalytic atoms vs the theozyme target placement
        # (parse with Biopython; superpose on the catalytic atoms only).
        raise NotImplementedError(
            "Implement atom-level RMSD over the catalytic atoms (triad + oxyanion hole) vs the "
            "theozyme target placement (parse with Biopython; superpose on the catalytic atoms only).")
    s = _seed_from(theozyme.reaction, str(predicted_pdb))
    # SYNTHETIC: spread around the 0.5 Å cutoff so the demo filter both passes and fails designs.
    return round(0.15 + _unit(s, "catgeom") * 0.9, 3)


# --------------------------------------------------------------------------------------- #
# dock_substrate(pocket, substrate, tool) → does the ester fit the designed pocket? (ACCESSIBILITY)
# --------------------------------------------------------------------------------------- #
def dock_substrate(pocket: Optional[str], substrate: str = "p-nitrophenyl acetate",
                   tool: str = "mock") -> dict:
    """Dock the chromogenic ester into the designed pocket as a fit/orientation sanity check.

    This is one of Project 21's emphases: POCKET ACCESSIBILITY. A perfect triad geometry is useless if
    the pocket is closed or mis-oriented — docking checks the ester physically fits AND that its
    carbonyl C points at the catalytic Ser-OG.

    Real backend:
      tool="vina" → AutoDock Vina (https://github.com/ccsb-scripps/AutoDock-Vina). Prepare the receptor
                    (designed pocket) + the ester ligand (PDBQT), define the box around the active site,
                    run, and read the top binding score + pose. Docking checks fit/orientation — it is
                    NOT an affinity or activity measurement.

    Mock path returns a deterministic SYNTHETIC score + placeholder pose/orientation flags.
    """
    tool = tool.lower()
    if tool == "vina":
        # TODO(student): receptor/ligand prep (PDBQT) → define box at the active site → run Vina →
        #   parse the best score + pose; check the ester carbonyl C is oriented toward Ser-OG.
        raise NotImplementedError(
            "Wire up AutoDock Vina: prep receptor + ester ligand PDBQT, box the active site, run, parse "
            "the top score/pose; check it orients toward Ser-OG. https://github.com/ccsb-scripps/AutoDock-Vina")
    if tool != "mock":
        raise ValueError(f"unknown tool {tool!r}; options: mock | vina")
    s = _seed_from(str(pocket), substrate)
    return {
        "substrate": substrate,
        "vina_score": round(-4.0 - _unit(s, "dock") * 4.0, 2),  # kcal/mol-ish, SYNTHETIC
        "pose_in_pocket": _unit(s, "pose") > 0.25,               # SYNTHETIC (pocket accessibility)
        "oriented_to_ser": _unit(s, "orient") > 0.3,             # SYNTHETIC (carbonyl toward Ser-OG)
        "tool": "mock",
        "synthetic": True,
    }


# --------------------------------------------------------------------------------------- #
# substrate_scope_scan(pocket, acyl_lengths) → acyl-chain-length scope reasoning [extension].
# --------------------------------------------------------------------------------------- #
def substrate_scope_scan(pocket: Optional[str], acyl_lengths=(2, 4, 6, 8),
                         tool: str = "mock") -> list:
    """Probe SUBSTRATE SCOPE by docking a homologous series of p-nitrophenyl esters (C2..Cn).

    Esterase vs lipase character largely tracks the acyl-chain length the pocket accepts: a tight
    pocket prefers short acyl chains (acetate, C2 — esterase-like), a larger/hydrophobic pocket admits
    longer chains (butyrate C4, hexanoate C6, octanoate C8 — lipase-like). Scanning the pNP-ester
    series across the designed pocket is the in-silico read on which substrates a design might turn
    over — this seeds the `[extension]` substrate-scope analysis and the kinetic-assay panel choice.

    Real backend: dock each pNP-ester (varying acyl chain) with AutoDock Vina (`dock_substrate`,
    tool="vina") and read fit/orientation per chain length. (Docking is a fit proxy, NOT activity.)

    Mock path returns one deterministic SYNTHETIC record per acyl length so the scope plot runs with
    no GPU. The chain length whose ester both fits and orients is the design's predicted preference.
    """
    names = {2: "pNP-acetate (C2)", 4: "pNP-butyrate (C4)", 6: "pNP-hexanoate (C6)",
             8: "pNP-octanoate (C8)", 10: "pNP-decanoate (C10)", 12: "pNP-laurate (C12)"}
    out = []
    for c in acyl_lengths:
        sub = names.get(c, f"pNP-ester (C{c})")
        d = dock_substrate(pocket, substrate=sub, tool=tool)  # mock unless tool="vina"
        out.append({
            "acyl_length": c,
            "substrate": sub,
            "vina_score": d["vina_score"],
            "fits_and_oriented": bool(d["pose_in_pocket"] and d["oriented_to_ser"]),
            "tool": d["tool"],
            "synthetic": d.get("synthetic", True),
        })
    return out


# --------------------------------------------------------------------------------------- #
# active_site_md(...) — short MD of active-site stability (OpenMM). Mock stub.
# --------------------------------------------------------------------------------------- #
def active_site_md(predicted_pdb: Optional[str], ns: float = 10.0, tool: str = "mock") -> dict:
    """Short MD to check the active site (triad + pocket) doesn't collapse/drift (OpenMM). SYNTHETIC mock.

    Real backend: OpenMM (https://github.com/openmm/openmm) — solvate, minimize, short NPT run
    (10–50 ns feasible for small systems on a T4; long MD → HPC). Report catalytic-atom RMSF / mean
    backbone RMSD over the trajectory. A triad that drifts apart under MD will not catalyse even if the
    static prediction looks perfect.
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
    # No-GPU smoke test: theozyme → scaffold → LigandMPNN(triad fixed) → dead mutant → geometry →
    # docking (pocket accessibility) → substrate-scope scan → active-site MD.
    print("== enzyme_tools.py smoke test (Project 21; mock backend; ALL NUMBERS SYNTHETIC) ==")
    theo = build_theozyme("ester_hydrolysis")
    print("theozyme:", theo.reaction)
    for fg in theo.functional_groups:
        print(f"  - {fg.role:16s} {fg.residue}/{fg.atom:4s}  d={fg.target_distance}Å  {fg.note[:46]}")
    scaffolds = scaffold_motif(theo, n=3)
    print(f"scaffolds: {len(scaffolds)} (mock)  e.g. {scaffolds[0]['design_id']} "
          f"len={scaffolds[0]['length']} motif_rmsd={scaffolds[0]['motif_rmsd']}Å")
    seqs = ligandmpnn_fix_catalytic(scaffolds[0], theo.catalytic_residue_ids(), n=2)
    print(f"sequences for {scaffolds[0]['design_id']}: {len(seqs)} (catalytic roles fixed: "
          f"{seqs[0]['fixed_catalytic_roles']})")
    # Dead-mutant control: find a Ser in the (synthetic) sequence and knock it out.
    seq0 = seqs[0]["sequence"]
    ser_idx = seq0.find("S")
    if ser_idx >= 0:
        dead = make_dead_mutant(seq0, ser_idx)
        print(f"dead mutant: pos {ser_idx} S->A  (control sequence differs at exactly 1 position: "
              f"{sum(a != b for a, b in zip(seq0, dead)) == 1})")
    cg = catalytic_geometry_rmsd(None, theo)
    print(f"catalytic_geometry_rmsd (mock) = {cg} Å  (pass if < 0.5)")
    dock = dock_substrate(None)
    print(f"dock_substrate (mock): score={dock['vina_score']} in_pocket={dock['pose_in_pocket']} "
          f"oriented_to_ser={dock['oriented_to_ser']}")
    scope = substrate_scope_scan(None, acyl_lengths=(2, 4, 6, 8))
    pref = [r["acyl_length"] for r in scope if r["fits_and_oriented"]]
    print(f"substrate_scope_scan (mock): {[(r['acyl_length'], r['fits_and_oriented']) for r in scope]} "
          f"-> predicted-acceptable C{pref if pref else '(none in mock)'}")
    md = active_site_md(None, ns=10.0)
    print(f"active_site_md (mock): md_rmsd={md['md_rmsd']}Å catalytic_rmsf={md['catalytic_rmsf']}Å")
    print("OK — plumbing runs with no GPU. Switch backends to rfdiffusion2/riffdiff/ligandmpnn/"
          "vina/openmm on Colab/HPC. NONE of these numbers are real (no kcat, no KM, no ee).")
