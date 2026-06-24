"""
enzyme_tools.py — theozyme → scaffold → sequence → catalytic-geometry → THERMOSTABILITY helpers for
Project 19 (Plastic-Degrading Active-Site Design, PETase-like). This follows the ENZYME-FAMILY
TEMPLATE established by Project 18 (Kemp eliminase) — theozyme construction, motif scaffolding,
catalytic-residue-fixed sequence design, catalytic-geometry RMSD, substrate docking — and swaps in
this project's reaction (ester hydrolysis, a Ser-His-Asp triad + oxyanion hole) and EMPHASIS
(thermostability: an MD-based ranking via RMSF + a melting-proxy, since industrial PET digestion runs
hot and wild-type IsPETase is fragile there).

DESIGN NOTE FOR STUDENTS
------------------------
The real backends (RFdiffusion2 / Riff-Diff scaffolding, LigandMPNN, AutoDock Vina, OpenMM
thermostability MD) are heavy, GPU/A100-bound, and environment-specific. So every function here ships
a deterministic `mock` backend that runs anywhere with NO GPU and NO heavy installs — it lets you
build and unit-test the *plumbing* (theozyme spec, file bookkeeping, geometry scoring,
thermostability aggregation) before you spend A100 time. The real backends are written as
clearly-marked TODOs you wire up on Colab/HPC.

EVERY number the mock backend returns is SYNTHETIC by construction (seeded hash of the inputs).
Never present a mock value as a real result — flag it `SYNTHETIC` / `EXAMPLE_DATA` in any figure, and
NEVER fabricate a kcat or a Tm.

Realistic expectations (read MASTER_BLUEPRINT §0, §3): de novo enzyme design hit rates are LOW —
often <5% active *without* directed evolution, and recent methods, while much better, still need
screening. PET hydrolases add a THERMOSTABILITY ↔ ACTIVITY trade-off. Preserving the catalytic
geometry in silico (and passing an MD stability proxy) does NOT guarantee catalysis or real
thermostability; only activity (pNP-ester / PET-film) and DSF assays can. This module triages and
ranks; it does not promise an enzyme.

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
# geometry they must hold around the transition state).
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

    For PETase-like ESTER HYDROLYSIS (the serine-hydrolase mechanism), the canonical minimal motif
    is the Ser-His-Asp catalytic triad + an oxyanion hole:
      - a catalytic SER (Ser-OG nucleophile) that attacks the ester carbonyl carbon,
      - a catalytic HIS (His-NE2 general base) that deprotonates Ser-OH to activate the nucleophile,
      - a catalytic ASP/GLU (carboxylate) that orients/protonates His (the charge-relay),
      - an OXYANION HOLE (two H-bond donors — typically backbone amide NHs) that stabilises the
        developing oxyanion of the tetrahedral intermediate (easy to forget, decisive for catalysis).

    The exact distances/angles below are TEMPLATE PLACEHOLDERS. Students MUST replace them with
    values built from the literature (Austin 2018 IsPETase; Tournier 2020 LCC; Lauko 2025 de novo
    serine hydrolases) and/or a QM tetrahedral-intermediate calculation. This function is the
    family-template hook (cf. Project 18's Kemp motif): override the `functional_groups` list for
    your reaction's catalytic geometry.

    EMPHASIS for this project: thermostability. The triad chemistry is known; the campaign is decided
    by whether the fold holding it survives industrial temperatures — see `thermostability_md`.
    """
    reaction = reaction.lower()
    if reaction not in ("ester_hydrolysis", "ester", "serine_hydrolase", "petase"):
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
        reaction="Ester hydrolysis (serine-hydrolase Ser-His-Asp triad + oxyanion hole; PET-hydrolase-like)",
        substrate="PET-mimic ester (fast screen: p-nitrophenyl ester, UV-readable; true substrate: PET-derived ester)",
        ts_description="TEMPLATE — Ser-OG nucleophilic attack on the carbonyl C forming the tetrahedral "
                       "intermediate, oxyanion stabilised by the oxyanion hole; fill the TS geometry from QM/literature.",
        functional_groups=fgs,
    )


# --------------------------------------------------------------------------------------- #
# scaffold_motif(theozyme, n, method) → candidate backbones holding the motif (in stable folds).
# --------------------------------------------------------------------------------------- #
def scaffold_motif(theozyme: Theozyme, n: int = 8, method: str = "mock",
                   track: str = "de_novo", out_dir: str = "results/scaffolds") -> list:
    """Generate `n` candidate backbones that present the theozyme motif (triad + oxyanion hole).

    `track` distinguishes the two scaffold sources this project compares (D3 `[extension]`):
      track="de_novo"            → fully de novo backbones from the diffusion model.
      track="engineered_natural" → graft the triad onto a stable natural cutinase/IsPETase scaffold.

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
        RFdiffusion2/Riff-Diff) wants an A100 (Colab Pro+) or an HPC GPU. Bias toward compact,
        thermostable (alpha/beta-hydrolase-like) topologies. Plan batch sizes around it.
    """
    os.makedirs(out_dir, exist_ok=True)
    method = method.lower()
    real = {"rfdiffusion2", "riffdiff", "rfdiffusion"}
    if method in real:
        # TODO(student): call the chosen scaffolding backend here on Colab/HPC.
        #   - export the theozyme as the tool's motif/constraint format (contigs + ligand/ester TS),
        #   - run N backbones (1000s for the real campaign — A100); bias toward stable folds,
        #   - for track="engineered_natural", graft onto a verified cutinase/IsPETase scaffold instead,
        #   - return one record per written backbone PDB.
        raise NotImplementedError(
            f"Wire up the real '{method}' scaffolding backend (A100/HPC). "
            "See the docstring; verify the current RFdiffusion2/Riff-Diff release at generation time.")
    if method != "mock":
        raise ValueError(f"unknown method {method!r}; options: mock | {' | '.join(sorted(real))}")

    base = _seed_from(theozyme.reaction, theozyme.substrate, n, track)
    records = []
    for i in range(n):
        s = base ^ _seed_from("scaffold", i, track)
        rec = {
            "design_id": f"EXAMPLE_DATA_{track}_scaffold_{i:03d}",
            "method": "mock",
            "track": track,
            "backbone_pdb": None,  # real backend writes a PDB path here
            "length": 220 + int(_unit(s, "len") * 80),      # 220–300 aa (cutinase-like), SYNTHETIC
            "motif_rmsd": round(0.2 + _unit(s, "motif") * 1.2, 3),   # Å, SYNTHETIC
            "catalytic_residues": theozyme.catalytic_residue_ids(),
            "synthetic": True,
        }
        records.append(rec)
    with open(os.path.join(out_dir, f"scaffolds_mock_{track}.json"), "w") as fh:
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
                          bias the (non-catalytic) surface toward thermostabilising residues — never
                          touch the triad.

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
# catalytic_geometry_rmsd(predicted_pdb, theozyme) → the KEY enzyme geometry metric.
# --------------------------------------------------------------------------------------- #
def catalytic_geometry_rmsd(predicted_pdb: Optional[str], theozyme: Theozyme) -> float:
    """RMSD (Å) of the predicted catalytic functional-group atoms vs the theozyme target geometry.

    This is THE enzyme geometry metric: catalytic-geometry RMSD < 0.5 Å vs the theozyme is the pass
    bar (DEFAULT_CUTOFFS['enzyme']['cat_geom'] in the shared filter). A design can fold beautifully
    (high pLDDT) yet present the triad / oxyanion-hole atoms in the wrong place — only this metric
    catches that. (Beyond geometry, this project then RANKS survivors by thermostability — see
    `thermostability_md`.)

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
# thermostability_md(...) — THE PROJECT'S EMPHASIS: rank designs by an MD thermostability proxy.
# --------------------------------------------------------------------------------------- #
def thermostability_md(predicted_pdb: Optional[str], ns: float = 20.0, temperature_K: float = 340.0,
                       tool: str = "mock") -> dict:
    """Short MD to RANK designs by thermostability (OpenMM). Returns RMSF + a melting-proxy.

    This is Project 19's headline metric beyond catalytic geometry. Industrial PET digestion runs hot
    (~65-70 °C, near PET's glass transition, where the polymer becomes accessible) and wild-type
    IsPETase is fragile there — so we rank geometry-passing designs by how well the fold survives.

    Returned fields:
      - `catalytic_rmsf` (Å): fluctuation of the catalytic-triad atoms; LOWER = more rigid active site.
      - `backbone_rmsf`  (Å): mean per-residue backbone fluctuation; LOWER = more stable fold.
      - `melting_proxy`  (0-1): a stability score, e.g. fraction of native contacts retained / inverse
                          of backbone-RMSD growth under an elevated-temperature run. HIGHER = more
                          thermostable. (THIS IS A PROXY, NOT A Tm — DSF gives the real melting temp.)
      - `thermostability_rank_score` (higher = better): convenience combination for ranking.

    Real backend: OpenMM (https://github.com/openmm/openmm) — solvate, minimize, equilibrate, then a
    production run at `temperature_K` (and/or an elevated-temperature / replica run). Compute
    catalytic-atom + backbone RMSF and a melting-proxy (native-contact retention or backbone-RMSD
    growth) with mdtraj. GROMACS is a valid alternative engine.

    >>> A100 NOTE: short MD on small systems (10-50 ns) is T4-feasible for triage, but the production
        thermostability RANKING over many survivors (longer / replica / elevated-temperature) wants an
        A100/HPC. Remember the thermostability <-> activity trade-off: a too-rigid active site can be
        catalytically dead — do not optimise rigidity blindly.

    The mock path returns deterministic SYNTHETIC values so the ranking plumbing runs with no GPU.
    """
    tool = tool.lower()
    if tool in ("openmm", "gromacs"):
        # TODO(student): build system, minimize, equilibrate, run production (and an elevated-T run),
        #   compute catalytic + backbone RMSF and a melting-proxy (native-contact retention / RMSD
        #   growth). Report them; do NOT report a Tm from MD (use DSF for that).
        raise NotImplementedError(
            f"Wire up the '{tool}' thermostability MD: solvate/minimize/equilibrate, run production "
            "(+ an elevated-temperature run), compute catalytic/backbone RMSF + a melting-proxy "
            "(native-contact retention). It is a PROXY, not a Tm. https://github.com/openmm/openmm")
    if tool != "mock":
        raise ValueError(f"unknown tool {tool!r}; options: mock | openmm | gromacs")
    s = _seed_from(str(predicted_pdb), ns, temperature_K)
    catalytic_rmsf = round(0.3 + _unit(s, "crmsf") * 1.4, 3)   # Å, SYNTHETIC (lower better)
    backbone_rmsf = round(0.6 + _unit(s, "brmsf") * 1.8, 3)    # Å, SYNTHETIC (lower better)
    melting_proxy = round(0.45 + _unit(s, "melt") * 0.5, 3)    # 0–1, SYNTHETIC (higher better)
    # Convenience rank score: reward high melting-proxy + low RMSF (SYNTHETIC).
    rank_score = round(melting_proxy - 0.2 * catalytic_rmsf - 0.1 * backbone_rmsf, 3)
    return {
        "ns": ns,
        "temperature_K": temperature_K,
        "catalytic_rmsf": catalytic_rmsf,
        "backbone_rmsf": backbone_rmsf,
        "melting_proxy": melting_proxy,
        "thermostability_rank_score": rank_score,
        "tool": "mock",
        "synthetic": True,
    }


# --------------------------------------------------------------------------------------- #
# dock_substrate(pocket, substrate, tool) → does the PET-mimic ester fit the designed pocket?
# --------------------------------------------------------------------------------------- #
def dock_substrate(pocket: Optional[str], substrate: str = "PET-mimic ester (p-nitrophenyl ester)",
                   tool: str = "mock") -> dict:
    """Dock the PET-mimic ester into the designed pocket as a fit/orientation sanity check.

    Real backend:
      tool="vina" → AutoDock Vina (https://github.com/ccsb-scripps/AutoDock-Vina). Prepare the
                    receptor (designed pocket) + the PET-mimic ester ligand (PDBQT), define the box
                    around the active site, run, and read the top binding score + pose. Docking checks
                    the ester physically fits and is oriented for catalysis (carbonyl C toward Ser-OG)
                    — it is NOT an affinity or activity measurement. PET itself is a polymer; dock a
                    soluble PET-derived / p-nitrophenyl ester FRAGMENT as the accessibility proxy.

    Mock path returns a deterministic SYNTHETIC score + a placeholder pose flag.
    """
    tool = tool.lower()
    if tool == "vina":
        # TODO(student): receptor/ligand prep (PDBQT) → define box at the active site → run Vina →
        #   parse the best score + pose; check the ester carbonyl C is oriented toward Ser-OG.
        raise NotImplementedError(
            "Wire up AutoDock Vina: prep receptor + PET-mimic-ester ligand PDBQT, box the active site, "
            "run, parse the top score/pose; check it orients toward Ser-OG. "
            "https://github.com/ccsb-scripps/AutoDock-Vina")
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


if __name__ == "__main__":
    # No-GPU smoke test: theozyme → scaffold → LigandMPNN(triad fixed) → geometry → THERMOSTABILITY → docking.
    print("== enzyme_tools.py smoke test (Project 19; mock backend; ALL NUMBERS SYNTHETIC) ==")
    theo = build_theozyme("ester_hydrolysis")
    print("theozyme:", theo.reaction)
    for fg in theo.functional_groups:
        print(f"  - {fg.role:16s} {fg.residue}/{fg.atom:4s}  d={fg.target_distance}Å  {fg.note[:46]}")
    scaffolds = scaffold_motif(theo, n=3, track="de_novo")
    print(f"scaffolds: {len(scaffolds)} (mock, track=de_novo)  e.g. {scaffolds[0]['design_id']} "
          f"len={scaffolds[0]['length']} motif_rmsd={scaffolds[0]['motif_rmsd']}Å")
    seqs = ligandmpnn_fix_catalytic(scaffolds[0], theo.catalytic_residue_ids(), n=2)
    print(f"sequences for {scaffolds[0]['design_id']}: {len(seqs)} (catalytic roles fixed: "
          f"{seqs[0]['fixed_catalytic_roles']})")
    cg = catalytic_geometry_rmsd(None, theo)
    print(f"catalytic_geometry_rmsd (mock) = {cg} Å  (pass if < 0.5)")
    thermo = thermostability_md(None, ns=20.0, temperature_K=340.0)
    print(f"thermostability_md (mock): catalytic_rmsf={thermo['catalytic_rmsf']}Å "
          f"melting_proxy={thermo['melting_proxy']} rank_score={thermo['thermostability_rank_score']}")
    dock = dock_substrate(None)
    print(f"dock_substrate (mock): score={dock['vina_score']} in_pocket={dock['pose_in_pocket']} "
          f"oriented_to_ser={dock['oriented_to_ser']}")
    print("OK — plumbing runs with no GPU. Switch backends to rfdiffusion2/riffdiff/ligandmpnn/"
          "openmm/vina on Colab/HPC. NONE of these numbers are real (no kcat, no Tm).")
