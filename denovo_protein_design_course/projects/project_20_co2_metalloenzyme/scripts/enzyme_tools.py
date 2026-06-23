"""
enzyme_tools.py — theozyme → scaffold → metal-aware sequence → metal-site-geometry helpers for
Project 20 (CO2-Fixing Metalloenzyme, Carbonic-Anhydrase-style). This follows the ENZYME-FAMILY
TEMPLATE established by Project 18 (Kemp eliminase) — theozyme construction, motif scaffolding,
catalytic-residue-fixed sequence design, catalytic-geometry RMSD, substrate docking, short MD — and
swaps in this project's reaction (CO2 hydration) and EMPHASIS: a catalytic METAL site (Zn-His3-OH)
designed and preserved with a metal-aware LigandMPNN.

WHAT IS DIFFERENT FROM PROJECT 18 (the family template)
-------------------------------------------------------
- The theozyme's catalytic motif is a METAL CENTRE: a tetrahedral Zn(II) coordinated by THREE
  histidine imidazole nitrogens (the His3 triad) plus a fourth position holding a zinc-bound
  hydroxide/water — the nucleophile that attacks CO2. This is the carbonic-anhydrase active site.
- Sequence design uses a METAL-AWARE LigandMPNN call (`ligandmpnn_metal`) that fixes the three
  His ligands AND passes the Zn atom as ligand context — vanilla ProteinMPNN cannot "see" the metal.
- The decisive geometry metric is METAL-LIGAND geometry (`metal_ligand_geometry`): the three Zn-N(His)
  distances (~2.0-2.2 A) and the N-Zn-N angles of the coordination tetrahedron, scored as an RMSD
  vs the target Zn-His3-OH placement. This maps onto `catalytic_geom_rmsd` in the shared filter.

DESIGN NOTE FOR STUDENTS
------------------------
The real backends (RFdiffusion2 / Riff-Diff scaffolding, LigandMPNN, AutoDock Vina, OpenMM MD) are
heavy, GPU/A100-bound, and environment-specific. So every function here ships a deterministic `mock`
backend that runs anywhere with NO GPU and NO heavy installs — it lets you build and unit-test the
*plumbing* (theozyme spec, file bookkeeping, metal-geometry scoring, aggregation) before you spend
A100 time. The real backends are written as clearly-marked TODOs you wire up on Colab/HPC.

EVERY number the mock backend returns is SYNTHETIC by construction (seeded hash of the inputs).
Never present a mock value as a real result — flag it `SYNTHETIC` / `EXAMPLE_DATA` in any figure, and
NEVER fabricate a kcat, a Wilbur-Anderson unit, or a metal-incorporation fraction.

Realistic expectations (read MASTER_BLUEPRINT 0, 3): de novo metalloenzyme design is HARD and hit
rates are LOW. The GRACE paradigm (Hu 2024) produced functional carbonic-anhydrase-style designs only
after generating a LARGE pool (~10k) and screening — i.e. diversity before filtering, then a real
assay. Two extra hazards for METAL sites: (1) metal INCORPORATION is uncertain (a perfect geometry
on paper does not mean Zn actually binds in the expressed protein — you must check by ICP/PAR), and
(2) classical MD force fields model a coordinated transition metal POORLY (fixed charges, no
charge transfer / polarisation), so MD here is a weak, caveated stability proxy, not ground truth.
Geometry != metal binding != activity. This module triages; it does not promise an enzyme.

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
# geometry they must hold around the transition state). For a metalloenzyme the motif is the
# METAL CENTRE: the metal ion + its coordinating ligand atoms + the reactive metal-bound species.
# --------------------------------------------------------------------------------------- #
@dataclass
class FunctionalGroup:
    """One catalytic functional group placed relative to the bound transition state / metal centre."""
    role: str                 # e.g. "metal_ion", "metal_ligand", "metal_hydroxide"
    residue: str              # candidate amino acid or species (e.g. "ZN", "HIS", "HOH/OH-")
    atom: str                 # the key atom (e.g. "ZN", "NE2"/"ND1" imidazole N, "O" of OH-)
    target_distance: float    # ideal distance (A): Zn-N(His) ~2.0-2.2; Zn-O(OH) ~1.9-2.1
    target_angle: Optional[float] = None  # ideal angle (deg) of the coordination polyhedron
    note: str = ""


@dataclass
class MetalSite:
    """The metal centre: the ion, its coordinating ligand residues, and the reactive metal species.

    For carbonic anhydrase this is Zn(II) + 3 His (imidazole N) + a Zn-bound hydroxide. We carry it
    separately from the generic Theozyme so the metal-aware functions (`ligandmpnn_metal`,
    `metal_ligand_geometry`) have a typed, explicit description of what must be preserved.
    """
    metal: str = "ZN"                 # the catalytic metal ion (Zn(II) for CA; Co(II) is a known sub)
    coordination_number: int = 4      # tetrahedral for the Zn-His3-OH carbonic-anhydrase site
    ligand_role: str = "metal_ligand"
    reactive_species: str = "metal_hydroxide"  # the Zn-OH that attacks CO2
    n_protein_ligands: int = 3        # His3
    target_metal_ligand_dist: float = 2.1   # A, Zn-N(His) target (PLACEHOLDER — verify from CA structures)
    target_ligand_metal_ligand_angle: float = 109.5  # deg, ideal tetrahedral N-Zn-N

    def ligand_atom_ids(self) -> list:
        """The protein ligand roles (the His imidazole N atoms) that LigandMPNN must FIX."""
        return [f"{self.ligand_role}_{i+1}" for i in range(self.n_protein_ligands)]


@dataclass
class Theozyme:
    """A minimal active-site definition: the reaction, the TS/metal centre, and the functional groups.

    For Project 20 the catalytic motif is a metal centre, so a `MetalSite` is attached and the
    functional_groups list is generated from it (metal ion + His ligands + the metal-bound hydroxide).
    """
    reaction: str
    substrate: str
    ts_description: str
    functional_groups: list = field(default_factory=list)
    metal_site: Optional[MetalSite] = None
    provenance: str = ("TEMPLATE — student fills metal-site geometry from carbonic-anhydrase "
                       "structures / literature (see data/inputs/metal_site_def.txt)")

    def to_dict(self) -> dict:
        d = asdict(self)
        return d

    def catalytic_residue_ids(self) -> list:
        """Roles whose residues must be FIXED during sequence design (the metal ligands)."""
        return [fg.role for fg in self.functional_groups if fg.role.startswith("metal_ligand")]


# --------------------------------------------------------------------------------------- #
# build_theozyme(reaction) → a metal-centre geometry spec for CO2 hydration.
# --------------------------------------------------------------------------------------- #
def build_theozyme(reaction: str = "co2_hydration") -> Theozyme:
    """Construct a teaching theozyme for the CO2-hydration (carbonic-anhydrase) reaction.

    Carbonic anhydrase hydrates CO2 (CO2 + H2O <-> HCO3- + H+) using a Zn(II) centre. The canonical
    catalytic motif (the metalloenzyme "theozyme") is:
      - a catalytic METAL ION: tetrahedral Zn(II);
      - THREE protein LIGANDS: histidine imidazole nitrogens (the His3 triad) coordinating the Zn;
      - a Zn-bound HYDROXIDE: the metal lowers the water pKa to ~7, so a Zn-OH- nucleophile is poised
        to attack CO2; a proton-shuttle residue (often a fourth His) then relays the proton out.

    The exact distances/angles below are TEMPLATE PLACEHOLDERS. Students MUST replace them with values
    built from carbonic-anhydrase structures (e.g. human CA II candidates 2CAB / 3KS3 — verify on
    RCSB) and/or a QM model of the Zn-OH + CO2 transition state. This function is the family-template
    hook adapted for a METAL site: where Project 18 placed a base + pi-stack + H-bond donor, Project
    20 places a metal ion + its His ligands + the reactive metal-hydroxide.
    """
    reaction = reaction.lower()
    if reaction not in ("co2_hydration", "co2", "carbonic_anhydrase", "ca"):
        raise NotImplementedError(
            f"build_theozyme only ships the CO2-hydration / Zn-His3-OH motif as a template; got "
            f"{reaction!r}. Override functional_groups/metal_site for your reaction (see docstring).")

    site = MetalSite(metal="ZN", coordination_number=4, reactive_species="metal_hydroxide",
                     n_protein_ligands=3, target_metal_ligand_dist=2.1,
                     target_ligand_metal_ligand_angle=109.5)

    fgs = [
        FunctionalGroup(role="metal_ion", residue="ZN", atom="ZN",
                        target_distance=0.0, target_angle=109.5,
                        note="PLACEHOLDER — catalytic Zn(II), tetrahedral; Co(II) is a known active "
                             "substitution (the stretch alternative-metal test)."),
        FunctionalGroup(role="metal_ligand_1", residue="HIS", atom="NE2",
                        target_distance=2.1, target_angle=109.5,
                        note="PLACEHOLDER — His imidazole N coordinates Zn; NE2 or ND1 depending on "
                             "rotamer (verify against the CA structure). FIX during sequence design."),
        FunctionalGroup(role="metal_ligand_2", residue="HIS", atom="NE2",
                        target_distance=2.1, target_angle=109.5,
                        note="PLACEHOLDER — second His ligand of the His3 triad. FIX during design."),
        FunctionalGroup(role="metal_ligand_3", residue="HIS", atom="ND1",
                        target_distance=2.1, target_angle=109.5,
                        note="PLACEHOLDER — third His ligand of the His3 triad. FIX during design."),
        FunctionalGroup(role="metal_hydroxide", residue="HOH/OH-", atom="O",
                        target_distance=1.95, target_angle=109.5,
                        note="PLACEHOLDER — the Zn-bound hydroxide nucleophile (4th coordination "
                             "site) that attacks CO2; a proton-shuttle His relays the proton out."),
    ]
    return Theozyme(
        reaction="CO2 hydration (carbonic anhydrase: CO2 + H2O <-> HCO3- + H+)",
        substrate="CO2 (gaseous/dissolved); esterase-proxy substrate p-nitrophenyl acetate (pNPA) "
                  "for a convenient chromogenic activity readout",
        ts_description="TEMPLATE — Zn-bound hydroxide performs nucleophilic attack on the CO2 carbon "
                       "(Zn-O...C=O); fill the Zn-OH + CO2 TS geometry from QM/literature.",
        functional_groups=fgs,
        metal_site=site,
    )


# --------------------------------------------------------------------------------------- #
# scaffold_motif(theozyme, n, method) → candidate backbones holding the metal-site motif.
# --------------------------------------------------------------------------------------- #
def scaffold_motif(theozyme: Theozyme, n: int = 8, method: str = "mock",
                   out_dir: str = "results/scaffolds") -> list:
    """Generate `n` candidate backbones that present the Zn-His3 metal-site motif.

    Real backends (wire up on an A100 / HPC — scaffolding is the A100-bound step):
      method="rfdiffusion2"  → RFdiffusion2 all-atom motif scaffolding (Dauparas 2025); can place the
                               metal + His ligands as an all-atom motif. VERIFY the current public
                               release/repo at generation time.
      method="riffdiff"      → Riff-Diff theozyme-to-enzyme scaffolding (Schnettler 2025, Nature);
                               VERIFY the current public release/repo at generation time.
      method="rfdiffusion"   → classic RFdiffusion motif scaffolding (RosettaCommons/RFdiffusion);
                               present the His ligands as a motif (treat the Zn as an external ligand);
                               a smaller free-tier demo, good for the P1 hello-world.

    The mock backend returns deterministic placeholder records so the pipeline runs with no GPU. Each
    record's `motif_rmsd` etc. are SYNTHETIC.

    >>> A100 NOTE: scaffolding a LARGE pool (the GRACE paradigm used ~10k) is the compute bottleneck.
        Free Colab T4 can do a small RFdiffusion motif-scaffolding DEMO (tens of backbones); the real
        campaign (1000s-10k, RFdiffusion2/Riff-Diff) wants an A100 (Colab Pro+) or an HPC GPU. Plan
        batch sizes around it. Metal-site placement is harder than a simple sidechain motif — budget
        extra backbones because many will not hold a clean tetrahedral His3 cage.
    """
    os.makedirs(out_dir, exist_ok=True)
    method = method.lower()
    real = {"rfdiffusion2", "riffdiff", "rfdiffusion"}
    if method in real:
        # TODO(student): call the chosen scaffolding backend here on Colab/HPC.
        #   - export the theozyme/metal site as the tool's motif/constraint format (contigs + the Zn
        #     ion + the 3 His ligand atoms as an all-atom motif / external ligand),
        #   - run N backbones (1000s-10k for the real campaign — A100),
        #   - return one record per written backbone PDB.
        raise NotImplementedError(
            f"Wire up the real '{method}' scaffolding backend (A100/HPC). See the docstring; verify "
            "the current RFdiffusion2/Riff-Diff release at generation time. Export the Zn + His3 "
            "as the tool's all-atom motif / external-ligand spec.")
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
            "length": 120 + int(_unit(s, "len") * 80),       # 120-200 aa, SYNTHETIC
            "motif_rmsd": round(0.2 + _unit(s, "motif") * 1.2, 3),   # A, SYNTHETIC
            "catalytic_residues": theozyme.catalytic_residue_ids(),
            "metal": theozyme.metal_site.metal if theozyme.metal_site else "ZN",
            "synthetic": True,
        }
        records.append(rec)
    with open(os.path.join(out_dir, "scaffolds_mock.json"), "w") as fh:
        json.dump(records, fh, indent=2)
    return records


# --------------------------------------------------------------------------------------- #
# ligandmpnn_metal(backbone, metal_ligands, n) → METAL-AWARE sequences with the ligands FIXED.
# This is the CENTRAL tool for this project.
# --------------------------------------------------------------------------------------- #
def ligandmpnn_metal(backbone: dict, metal_ligands: list, n: int = 8,
                     metal: str = "ZN", tool: str = "mock") -> list:
    """Design `n` sequences for one backbone with a METAL-AWARE LigandMPNN, FIXING the metal ligands.

    This is the heart of Project 20 and why LigandMPNN (not vanilla ProteinMPNN) is required: the
    three His imidazole nitrogens must coordinate the Zn, so (a) the His ligand positions are FIXED
    and (b) the Zn atom is passed as ligand context so the model designs the rest of the protein to
    accommodate (and not clash with / mis-charge) the metal centre. ProteinMPNN cannot see the metal.

    Real backend (CPU-fast — this step is cheap, unlike scaffolding):
      tool="ligandmpnn" → LigandMPNN (https://github.com/dauparas/LigandMPNN). Pass the metal as the
                          ligand/atom context (`--ligand_mpnn_use_atom_context 1`), and a
                          fixed-positions list covering all three His ligands so they are NOT
                          redesigned. The metal-conditioned checkpoint is the right one for a metal
                          site; verify the current model/flag names against the repo.

    The mock backend returns deterministic placeholder sequences (His ligand positions annotated as
    fixed) so the plumbing runs anywhere. All scores are SYNTHETIC. To make the mock realistic, the
    three fixed ligand positions are seeded as histidines ("H") in the pseudo-sequence.
    """
    tool = tool.lower()
    if tool == "ligandmpnn":
        # TODO(student): run metal-aware LigandMPNN.
        #   - pass the Zn atom as the ligand/atom context (--ligand_mpnn_use_atom_context 1),
        #   - pass --fixed_residues (or the JSON fixed-positions spec) covering ALL THREE His ligands
        #     so they are preserved (confirm the numbering matches the backbone PDB),
        #   - choose the metal-conditioned checkpoint; parse the FASTA out.
        raise NotImplementedError(
            "Wire up metal-aware LigandMPNN (CPU-fast): pass the Zn as atom/ligand context and a "
            "fixed-positions list for the three His ligands so the coordination cage is preserved. "
            "https://github.com/dauparas/LigandMPNN")
    if tool != "mock":
        raise ValueError(f"unknown tool {tool!r}; options: mock | ligandmpnn")

    bid = backbone.get("design_id", "bb")
    length = int(backbone.get("length", 150))
    n_ligands = len(metal_ligands) if metal_ligands else 3
    # Deterministically pick the (mock) fixed His ligand positions within the chain.
    seqs = []
    aa = "ACDEFGHIKLMNPQRSTVWY"
    for j in range(n):
        s = _seed_from(bid, "ligandmpnn_metal", j)
        # mock fixed-His positions, spread across the chain (SYNTHETIC indices):
        his_positions = sorted({(_seed_from(bid, "his", j, k) % max(length, 1))
                                for k in range(n_ligands)})
        chars = [aa[(_seed_from(bid, j, k) >> 3) % 20] for k in range(length)]
        for p in his_positions:
            chars[p] = "H"   # the fixed metal-ligand His residues
        seq = "".join(chars)
        seqs.append({
            "design_id": f"{bid}_seq{j:02d}",
            "sequence": seq,
            "fixed_metal_ligand_roles": list(metal_ligands),
            "fixed_his_positions": his_positions,    # 0-indexed mock positions of the His3 cage
            "metal": metal,
            "mpnn_score": round(0.8 + _unit(s, "mpnn") * 0.6, 3),  # SYNTHETIC (lower ~ more confident)
            "tool": "mock",
            "metal_aware": True,
            "synthetic": True,
        })
    return seqs


def ligandmpnn_fix_catalytic(backbone: dict, catalytic_residues: list, n: int = 8,
                             tool: str = "mock") -> list:
    """Compatibility alias to the family-template name (Project 18). For Project 20 this forwards to
    the METAL-AWARE design (`ligandmpnn_metal`) so notebooks/benchmarks that expect the template
    function name still work; the benchmark in notebook 04 contrasts this with a (metal-BLIND)
    ProteinMPNN call to show why the metal context matters.
    """
    return ligandmpnn_metal(backbone, catalytic_residues, n=n, tool=tool)


def proteinmpnn_metal_blind(backbone: dict, catalytic_residues: list, n: int = 8,
                            tool: str = "mock") -> list:
    """A metal-BLIND baseline (vanilla ProteinMPNN) for the LigandMPNN-vs-ProteinMPNN benchmark.

    ProteinMPNN has no notion of the Zn ion. Even if you fix the three His positions, the rest of the
    protein is designed WITHOUT the metal in context, so the pocket electrostatics/packing around the
    charged metal centre are not accounted for — the point of the notebook-04 benchmark. The mock
    backend marks these as `metal_aware=False` and gives them a (SYNTHETIC) systematically worse
    metal-geometry tendency downstream so the comparison has the expected shape.

    Real backend: tool="proteinmpnn" → ProteinMPNN (https://github.com/dauparas/ProteinMPNN) with a
    fixed-positions list for the His ligands but NO ligand/atom context.
    """
    tool = tool.lower()
    if tool == "proteinmpnn":
        raise NotImplementedError(
            "Wire up vanilla ProteinMPNN (metal-BLIND baseline): fix the His positions but pass NO "
            "metal/atom context. https://github.com/dauparas/ProteinMPNN")
    if tool != "mock":
        raise ValueError(f"unknown tool {tool!r}; options: mock | proteinmpnn")
    seqs = ligandmpnn_metal(backbone, catalytic_residues, n=n, tool="mock")
    for s in seqs:
        s["tool"] = "mock-proteinmpnn"
        s["metal_aware"] = False
        s["design_id"] = s["design_id"].replace("_seq", "_pmpnn_seq")
    return seqs


# --------------------------------------------------------------------------------------- #
# metal_ligand_geometry(predicted_pdb, metal_site) → the KEY metalloenzyme metric.
# --------------------------------------------------------------------------------------- #
def metal_ligand_geometry(predicted_pdb: Optional[str], metal_site: MetalSite) -> dict:
    """Metal-coordination geometry of a predicted design vs the target Zn-His3 placement.

    This is THE metalloenzyme metric, the metal analogue of Project 18's catalytic-geometry RMSD. A
    design can fold beautifully (high pLDDT) yet present the three His nitrogens at the wrong
    distances/angles to make a clean tetrahedral Zn cage — only this metric catches that. We report:
      - `metal_ligand_rmsd` : an RMSD (A) of the coordinating ligand atoms (the 3 His N) vs the
        target Zn-His3 placement. Maps onto `catalytic_geom_rmsd` in the shared filter; pass < 0.5 A.
      - `mean_zn_n_dist`     : mean Zn-N(His) distance (target ~2.0-2.2 A).
      - `mean_n_zn_n_angle`  : mean N-Zn-N angle (target ~109.5 deg for tetrahedral).
      - `coordination_ok`    : all three ligands within distance/angle tolerance (a clean cage).

    Real implementation (wire up with the AF2/predicted PDB; AF2 does not place the Zn, so you build
    the metal in from the His3 geometry or use a metal-aware predictor):
      - parse the predicted structure (Biopython),
      - extract the 3 His imidazole N atoms at the fixed ligand positions,
      - place/refine the Zn at the centroid of the would-be coordination sphere (or read it from a
        metal-aware predictor), compute the Zn-N distances and N-Zn-N angles,
      - superpose the ligand atoms onto the target Zn-His3 placement and return the RMSD.
    A teaching-grade Ca/atom superposition helper exists in shared/filtering_pipeline.ca_rmsd; here
    you need an ATOM-level RMSD over just the metal-coordinating atoms.

    The mock path (predicted_pdb is None or missing) returns deterministic SYNTHETIC values seeded by
    the metal site + path, so the filtering plumbing runs with no real structure.
    """
    if predicted_pdb and os.path.exists(predicted_pdb):
        # TODO(student): real atom-level metal-ligand geometry (Zn-N distances, N-Zn-N angles, RMSD
        #   vs the target Zn-His3 placement). Parse with Biopython; AF2 will not place the Zn, so add
        #   it from the His3 geometry or use a metal-aware predictor.
        raise NotImplementedError(
            "Implement atom-level metal-ligand geometry: extract the 3 His N atoms, place/read the "
            "Zn, compute Zn-N distances + N-Zn-N angles, and RMSD vs the target Zn-His3 placement.")
    s = _seed_from(metal_site.metal, metal_site.n_protein_ligands, str(predicted_pdb))
    # SYNTHETIC: spread the RMSD around the 0.5 A cutoff so the demo filter both passes and fails.
    rmsd = round(0.15 + _unit(s, "mlrmsd") * 0.9, 3)
    return {
        "metal_ligand_rmsd": rmsd,                                  # A, SYNTHETIC (maps to cat_geom)
        "mean_zn_n_dist": round(1.95 + _unit(s, "znn") * 0.45, 3),  # A, SYNTHETIC (target ~2.0-2.2)
        "mean_n_zn_n_angle": round(100.0 + _unit(s, "angle") * 25.0, 1),  # deg, SYNTHETIC (~109.5)
        "coordination_ok": rmsd < 0.5,                              # clean tetrahedral cage? SYNTHETIC
        "metal": metal_site.metal,
        "synthetic": True,
    }


def metal_ligand_geometry_rmsd(predicted_pdb: Optional[str], theozyme: Theozyme) -> float:
    """Convenience wrapper returning just the metal-ligand RMSD (A) for the shared filter's
    `catalytic_geom_rmsd` field. Uses the theozyme's attached MetalSite.
    """
    site = theozyme.metal_site or MetalSite()
    return metal_ligand_geometry(predicted_pdb, site)["metal_ligand_rmsd"]


# --------------------------------------------------------------------------------------- #
# dock_substrate(pocket, substrate, tool) — does CO2 / the pNPA proxy reach the metal hydroxide?
# --------------------------------------------------------------------------------------- #
def dock_substrate(pocket: Optional[str], substrate: str = "CO2", tool: str = "mock") -> dict:
    """Dock the substrate (CO2, or the pNPA esterase proxy) toward the Zn-hydroxide as a fit check.

    For carbonic anhydrase the relevant check is whether the substrate can approach the Zn-bound
    hydroxide nucleophile in the right orientation — not an affinity or activity measurement. CO2 is
    a tiny, weakly-binding substrate, so docking is a coarse orientation sanity check; the pNPA
    esterase-proxy substrate is larger and easier to pose.

    Real backend:
      tool="vina" → AutoDock Vina (https://github.com/ccsb-scripps/AutoDock-Vina). Prepare receptor
                    (designed pocket incl. the Zn) + ligand (PDBQT), box at the metal site, run, read
                    the top score + pose; check the substrate carbon sits near the Zn-OH.

    Mock path returns a deterministic SYNTHETIC score + a placeholder orientation flag.
    """
    tool = tool.lower()
    if tool == "vina":
        # TODO(student): receptor (with Zn)/ligand prep (PDBQT) → box at the metal site → run Vina →
        #   parse the best score + pose; check the substrate carbon approaches the Zn-hydroxide.
        raise NotImplementedError(
            "Wire up AutoDock Vina: prep receptor (incl. Zn) + ligand PDBQT, box the metal site, run, "
            "parse the top score/pose; check approach to the Zn-OH. "
            "https://github.com/ccsb-scripps/AutoDock-Vina")
    if tool != "mock":
        raise ValueError(f"unknown tool {tool!r}; options: mock | vina")
    s = _seed_from(str(pocket), substrate)
    return {
        "substrate": substrate,
        "vina_score": round(-3.0 - _unit(s, "dock") * 3.5, 2),  # kcal/mol-ish, SYNTHETIC (CO2 is weak)
        "approaches_metal_hydroxide": _unit(s, "pose") > 0.25,   # SYNTHETIC
        "tool": "mock",
        "synthetic": True,
    }


# --------------------------------------------------------------------------------------- #
# active_site_md(...) — short MD of metal-site stability (OpenMM). HEAVY metal-FF caveat. Mock stub.
# --------------------------------------------------------------------------------------- #
def active_site_md(predicted_pdb: Optional[str], ns: float = 10.0, tool: str = "mock") -> dict:
    """Short MD to check the metal site doesn't collapse/drift (OpenMM). Mock returns SYNTHETIC.

    >>> METAL-FF CAVEAT (state this in every report): classical, fixed-charge force fields model a
        coordinated transition metal POORLY. Standard options are a bonded model (explicit Zn-N
        bonds — stops the metal drifting but cannot break/reform coordination) or a non-bonded
        cationic-dummy model; neither captures charge transfer / polarisation / the hydroxide pKa.
        So MD here is a WEAK stability PROXY, not a faithful description of the metal centre. Treat a
        "stable" result as necessary-not-sufficient, and never present it as evidence of catalysis.

    Real backend: OpenMM (https://github.com/openmm/openmm) — solvate, minimize, short NPT run
    (10-50 ns feasible for small systems on a T4; long MD -> HPC), with a deliberate metal-site
    treatment (bonded/dummy model; cite the parameter source). Report metal-ligand-atom RMSF and
    whether the Zn-N coordination holds over the trajectory.
    """
    tool = tool.lower()
    if tool == "openmm":
        # TODO(student): build system with an explicit metal-site model (bonded or cationic-dummy;
        #   cite the parameters), minimize, equilibrate, run `ns`, compute metal-ligand RMSF and
        #   whether the Zn-N coordination is retained. STATE the classical-metal-FF limitation.
        raise NotImplementedError(
            "Wire up OpenMM with an explicit metal-site model (bonded or cationic-dummy; cite params). "
            "Report metal-ligand RMSF + coordination retention, and STATE the classical-metal-FF "
            "limitation. https://github.com/openmm/openmm")
    if tool != "mock":
        raise ValueError(f"unknown tool {tool!r}; options: mock | openmm")
    s = _seed_from(str(predicted_pdb), ns)
    return {
        "ns": ns,
        "md_rmsd": round(0.8 + _unit(s, "md") * 2.6, 3),            # A, SYNTHETIC
        "metal_ligand_rmsf": round(0.3 + _unit(s, "rmsf") * 1.4, 3),  # A, SYNTHETIC
        "coordination_retained": _unit(s, "coord") > 0.3,           # SYNTHETIC
        "metal_ff_caveat": "classical fixed-charge FF models a coordinated metal POORLY; weak proxy.",
        "tool": "mock",
        "synthetic": True,
    }


if __name__ == "__main__":
    # No-GPU smoke test: theozyme(metal) → scaffold → metal-aware LigandMPNN(His3 fixed) → geometry →
    # docking → MD. ALL NUMBERS SYNTHETIC.
    print("== enzyme_tools.py smoke test (mock backend; ALL NUMBERS SYNTHETIC) ==")
    theo = build_theozyme("co2_hydration")
    print("theozyme:", theo.reaction)
    print("metal site:", theo.metal_site.metal, "coordination", theo.metal_site.coordination_number,
          "| protein ligands:", theo.metal_site.n_protein_ligands, "His")
    for fg in theo.functional_groups:
        ang = f"{fg.target_angle}deg" if fg.target_angle is not None else "n/a"
        print(f"  - {fg.role:16s} {fg.residue}/{fg.atom:4s}  d={fg.target_distance}A  angle={ang}")
    print("metal ligands to FIX during sequence design:", theo.catalytic_residue_ids())
    scaffolds = scaffold_motif(theo, n=3)
    print(f"scaffolds: {len(scaffolds)} (mock)  e.g. {scaffolds[0]['design_id']} "
          f"len={scaffolds[0]['length']} motif_rmsd={scaffolds[0]['motif_rmsd']}A metal={scaffolds[0]['metal']}")
    seqs = ligandmpnn_metal(scaffolds[0], theo.catalytic_residue_ids(), n=2)
    print(f"metal-aware sequences for {scaffolds[0]['design_id']}: {len(seqs)} "
          f"(fixed ligand roles: {seqs[0]['fixed_metal_ligand_roles']}, metal_aware={seqs[0]['metal_aware']})")
    pm = proteinmpnn_metal_blind(scaffolds[0], theo.catalytic_residue_ids(), n=2)
    print(f"metal-BLIND ProteinMPNN baseline: {len(pm)} (metal_aware={pm[0]['metal_aware']}) — for the benchmark")
    geo = metal_ligand_geometry(None, theo.metal_site)
    print(f"metal_ligand_geometry (mock): rmsd={geo['metal_ligand_rmsd']}A  Zn-N={geo['mean_zn_n_dist']}A  "
          f"N-Zn-N={geo['mean_n_zn_n_angle']}deg  coordination_ok={geo['coordination_ok']}  (pass rmsd<0.5)")
    dock = dock_substrate(None, theo.substrate.split(";")[0])
    print(f"dock_substrate (mock): score={dock['vina_score']} approaches_OH={dock['approaches_metal_hydroxide']}")
    md = active_site_md(None, ns=10.0)
    print(f"active_site_md (mock): md_rmsd={md['md_rmsd']}A metal_ligand_rmsf={md['metal_ligand_rmsf']}A "
          f"coordination_retained={md['coordination_retained']}")
    print("  metal-FF caveat:", md["metal_ff_caveat"])
    print("OK — plumbing runs with no GPU. Switch backends to rfdiffusion2/riffdiff/ligandmpnn/"
          "vina/openmm on Colab/HPC. NONE of these numbers are real.")
