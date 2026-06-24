"""
cofactor_tools.py — cofactor-site spec → scaffold pocket → cofactor-aware sequence → coordination-
geometry helpers for Project 24 (Metalloprotein / Cofactor-Binding De Novo Protein). This follows the
ENZYME-FAMILY TEMPLATE established by Project 18 (Kemp eliminase) — a "theozyme"-style active-site
spec, motif scaffolding, coordinating-residue-fixed sequence design, a geometry RMSD metric, ligand
docking, and a short (caveated) MD — and swaps in this project's target: a COFACTOR COORDINATION
POCKET (e.g. a bis-His heme site) designed and preserved with a cofactor-aware LigandMPNN, validated
by SPECTROSCOPY rather than a catalytic assay.

WHAT IS DIFFERENT FROM PROJECT 18 (the family template) AND PROJECT 20 (the Zn metalloENZYME)
---------------------------------------------------------------------------------------------
- The "active site" here is a COFACTOR-BINDING POCKET, not a catalytic transition-state motif. The
  goal is COORDINATION (and incorporation) of a redox/O2 cofactor — heme (Fe-protoporphyrin IX), a
  [4Fe-4S] cluster, or a structural/catalytic Zn — to build artificial electron-transfer proteins,
  synthetic O2 carriers, and artificial metalloenzymes. Project 20 designs a CATALYTIC Zn site (CO2
  hydration, activity assay); Project 24 designs a cofactor-COORDINATION site (binding, spectroscopy).
- The decisive metric is COORDINATION GEOMETRY (`coordination_geometry`): the metal–ligand distances
  and ligand–metal–ligand angles of the coordination scheme (e.g. the two axial His Nepsilon2 atoms of a
  bis-His heme, Fe–N ~2.0-2.2 A, N-Fe-N ~180 deg), scored as an RMSD vs the target placement. This maps
  onto `catalytic_geom_rmsd` (cat_geom) in the shared filter — for THIS project cat_geom is the
  COORDINATION-geometry RMSD, and plddt_catalytic is the SITE confidence (pLDDT at the coordinating
  residues), not a catalytic-residue confidence.
- Sequence design uses a COFACTOR-AWARE LigandMPNN call (`ligandmpnn_cofactor`) that fixes the
  coordinating residues AND passes the cofactor (heme / cluster / metal) as ligand/atom context —
  vanilla ProteinMPNN is cofactor-blind. This ligand-awareness is exactly why LigandMPNN is central.

DESIGN NOTE FOR STUDENTS
------------------------
The real backends (RFdiffusion2 / Riff-Diff scaffolding, LigandMPNN, AutoDock Vina, OpenMM MD) are
heavy, GPU/A100-bound, and environment-specific. So every function here ships a deterministic `mock`
backend that runs anywhere with NO GPU and NO heavy installs — it lets you build and unit-test the
*plumbing* (cofactor-site spec, file bookkeeping, coordination-geometry scoring, aggregation) before
you spend A100 time. The real backends are written as clearly-marked TODOs you wire up on Colab/HPC.

EVERY number the mock backend returns is SYNTHETIC by construction (seeded hash of the inputs). Never
present a mock value as a real result — flag it `SYNTHETIC` / `EXAMPLE_DATA` in any figure, and NEVER
fabricate a Soret wavelength, an extinction coefficient, an EPR g-value, a redox midpoint potential,
or a cofactor-incorporation fraction. There are NO real spectra in this project.

Realistic expectations (read MASTER_BLUEPRINT 0, 3): de novo cofactor-binding / metalloprotein design
is a long-standing GRAND CHALLENGE and hit rates are LOW. Three honest caveats stack here, mirroring
Project 20 but for a bound cofactor: (1) COORDINATION GEOMETRY != COFACTOR INCORPORATION != FUNCTION —
a perfect bis-His geometry on paper does not mean heme actually loads into the expressed protein, and
loading does not mean the designed redox/O2 behaviour; only SPECTROSCOPY (UV-vis Soret for heme, EPR
for [4Fe-4S], plus a cofactor titration) can confirm. (2) AF2 does NOT place the cofactor or the metal
— it predicts the apo backbone; you read the coordinating-residue geometry/confidence and must dock
or model the cofactor separately. (3) Classical MD models a coordinated metal / heme Fe POORLY (fixed
charges, no charge transfer / polarisation / spin), so MD here is a weak, caveated stability proxy,
not ground truth. This module triages; it does not promise a functional metalloprotein.

Import-safe: this file imports with only the standard library. `numpy` is imported lazily inside the
one function that needs it. Run `python cofactor_tools.py` for a no-GPU smoke test.
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
# Data model. The "active site" is a COFACTOR-BINDING site: the cofactor + its coordinating
# protein ligand atoms + the metal/cluster they hold. We carry a typed CofactorSite so the
# cofactor-aware functions have an explicit description of what must be preserved.
# --------------------------------------------------------------------------------------- #
@dataclass
class CoordinatingGroup:
    """One protein ligand that coordinates the cofactor metal (or H-bonds a cluster S/Fe)."""
    role: str                 # e.g. "axial_ligand_1", "axial_ligand_2", "cluster_ligand_1"
    residue: str              # candidate amino acid (e.g. "HIS", "MET", "CYS", "TYR")
    atom: str                 # the coordinating atom (e.g. "NE2"/"ND1" His; "SD" Met; "SG" Cys)
    target_distance: float    # ideal metal-ligand distance (A): Fe-N(His) ~2.0-2.2; Fe-S(Cys) ~2.3
    target_angle: Optional[float] = None  # ideal ligand-metal-ligand angle (deg) of the scheme
    note: str = ""


# Reference coordination schemes (TEMPLATE values — students VERIFY against real structures).
# These are teaching placeholders for the most common cofactor sites; cite the structure you use.
COORDINATION_SCHEMES = {
    # heme b (Fe-protoporphyrin IX): the iron is held by the 4 porphyrin N's; the PROTEIN supplies
    # the axial ligand(s). Two axial His = bis-His (b-type cytochrome, low-spin, electron transfer);
    # one His + open site = O2/CO binding (myoglobin-like); His/Met = c-type cytochrome axial pair.
    "bis_his_heme": dict(
        cofactor="heme_b", metal="FE", coordination="bis-His (His/His axial pair)",
        n_protein_ligands=2, ligand_residue="HIS", ligand_atom="NE2",
        target_metal_ligand_dist=2.05, target_ligand_metal_ligand_angle=180.0,
        function="low-spin electron transfer (b-type cytochrome-like)",
        note="PLACEHOLDER — verify Fe-Nepsilon2 distance + His-Fe-His angle against a b-type "
             "cytochrome / designed-heme structure; axial His often on opposite helices."),
    "his_met_heme": dict(
        cofactor="heme_c", metal="FE", coordination="His/Met axial pair",
        n_protein_ligands=2, ligand_residue="HIS+MET", ligand_atom="NE2/SD",
        target_metal_ligand_dist=2.1, target_ligand_metal_ligand_angle=175.0,
        function="electron transfer (c-type cytochrome-like; needs covalent CXXCH attachment)",
        note="PLACEHOLDER — c-type heme is covalently attached via a CXXCH motif; the Met S-Fe and "
             "His N-Fe distances differ. Verify against a c-type cytochrome structure."),
    "his_open_heme": dict(
        cofactor="heme_b", metal="FE", coordination="proximal His + open distal site",
        n_protein_ligands=1, ligand_residue="HIS", ligand_atom="NE2",
        target_metal_ligand_dist=2.1, target_ligand_metal_ligand_angle=None,
        function="O2 / CO binding (myoglobin-like synthetic O2 carrier)",
        note="PLACEHOLDER — proximal His coordinates Fe; the distal pocket stays OPEN for O2/CO, "
             "often with a distal His/Gln to H-bond bound O2. Verify against myoglobin (e.g. 1MBN)."),
    "fe4s4_4cys": dict(
        cofactor="[4Fe-4S]", metal="FE", coordination="4 Cys (one per Fe of the cubane)",
        n_protein_ligands=4, ligand_residue="CYS", ligand_atom="SG",
        target_metal_ligand_dist=2.3, target_ligand_metal_ligand_angle=None,
        function="electron transfer (ferredoxin-like Fe-S cluster)",
        note="PLACEHOLDER — each of the 4 cubane Fe is ligated by one Cys Sgamma (~2.3 A); the canonical "
             "ferredoxin motif is CxxCxxC...C. Verify against a ferredoxin structure."),
    "zn_cys2his2": dict(
        cofactor="Zn(II)", metal="ZN", coordination="Cys2His2 (structural zinc finger)",
        n_protein_ligands=4, ligand_residue="CYS+HIS", ligand_atom="SG/NE2",
        target_metal_ligand_dist=2.1, target_ligand_metal_ligand_angle=109.5,
        function="structural metal site (zinc-finger-like) — a simple coordination warm-up",
        note="PLACEHOLDER — tetrahedral Zn held by 2 Cys Sgamma + 2 His N; ~2.0-2.3 A. Verify against a "
             "zinc-finger structure. A good first scheme before tackling heme / Fe-S."),
}


@dataclass
class CofactorSite:
    """The cofactor centre: the cofactor, the metal/cluster, and the protein ligands that hold it.

    For a bis-His heme this is heme b (Fe-protoporphyrin IX) + two axial His (imidazole Nepsilon2). We
    carry it as a typed object so the cofactor-aware functions (`ligandmpnn_cofactor`,
    `coordination_geometry`, `dock_cofactor`) have an explicit description of what must be preserved.
    """
    cofactor: str = "heme_b"           # heme_b | heme_c | [4Fe-4S] | Zn(II)
    metal: str = "FE"                  # FE for heme/Fe-S; ZN for the zinc warm-up
    coordination: str = "bis-His (His/His axial pair)"
    n_protein_ligands: int = 2         # bis-His = 2; His/open = 1; [4Fe-4S] = 4; Cys2His2 = 4
    ligand_residue: str = "HIS"
    ligand_atom: str = "NE2"
    target_metal_ligand_dist: float = 2.05      # A (PLACEHOLDER — verify per scheme)
    target_ligand_metal_ligand_angle: Optional[float] = 180.0  # deg (PLACEHOLDER — verify)
    function: str = "low-spin electron transfer (b-type cytochrome-like)"
    scheme_key: str = "bis_his_heme"

    def coordinating_residue_ids(self) -> list:
        """The protein ligand roles that LigandMPNN must FIX (the coordinating residues)."""
        return [f"axial_ligand_{i + 1}" if "heme" in self.cofactor else f"cluster_ligand_{i + 1}"
                for i in range(self.n_protein_ligands)]


@dataclass
class CofactorSpec:
    """A minimal cofactor-binding-site definition: the cofactor, its function, and the coordination.

    Analogous to the Theozyme in Projects 18/20, but the "active site" is a COFACTOR POCKET. The
    coordinating groups are generated from the chosen CofactorSite / scheme.
    """
    cofactor: str
    function: str
    site_description: str
    coordinating_groups: list = field(default_factory=list)
    cofactor_site: Optional[CofactorSite] = None
    provenance: str = ("TEMPLATE — student fills coordination geometry from a verified reference "
                       "structure / literature (see data/inputs/cofactor_site_def.txt)")

    def to_dict(self) -> dict:
        return asdict(self)

    def coordinating_residue_ids(self) -> list:
        """Roles whose residues must be FIXED during sequence design (the coordinating ligands)."""
        return [g.role for g in self.coordinating_groups]


# --------------------------------------------------------------------------------------- #
# build_cofactor_spec(cofactor, scheme) → a coordination-pocket geometry spec.
# --------------------------------------------------------------------------------------- #
def build_cofactor_spec(cofactor: str = "heme", scheme: str = "bis_his_heme") -> CofactorSpec:
    """Construct a teaching cofactor-binding-site spec for the chosen cofactor + coordination scheme.

    The DEFAULT for this project is a BIS-HIS HEME site: heme b (Fe-protoporphyrin IX) held by two
    axial histidine imidazole nitrogens (Fe-Nepsilon2 ~2.0-2.2 A, His-Fe-His ~180 deg) — the canonical
    b-type-cytochrome electron-transfer motif and the classic target of designed heme proteins
    (DeGrado's "maquette" four-helix bundles; Baker-lab de novo heme proteins). Other schemes are in
    COORDINATION_SCHEMES (His/Met heme, proximal-His O2-binding heme, [4Fe-4S]-4Cys ferredoxin,
    Cys2His2 structural Zn) — pass `scheme=` to pick one.

    The exact distances/angles are TEMPLATE PLACEHOLDERS. Students MUST replace them with values built
    from a VERIFIED reference structure (heme: myoglobin 1MBN or a b-type cytochrome — verify on RCSB;
    Fe-S: a ferredoxin — verify on RCSB) and/or literature, and CITE each value
    (data/inputs/cofactor_site_def.txt). This is the family-template hook adapted for a COFACTOR site:
    where Project 18 placed a base + pi-stack + H-bond donor and Project 20 placed a catalytic
    Zn-His3-OH, Project 24 places a cofactor + its coordinating ligands.
    """
    cofactor = cofactor.lower()
    # normalise common aliases to a scheme
    alias = {
        "heme": "bis_his_heme", "heme_b": "bis_his_heme", "bishis": "bis_his_heme",
        "heme_c": "his_met_heme", "o2": "his_open_heme", "myoglobin": "his_open_heme",
        "fes": "fe4s4_4cys", "fe4s4": "fe4s4_4cys", "ferredoxin": "fe4s4_4cys",
        "zn": "zn_cys2his2", "zinc": "zn_cys2his2",
    }
    scheme = alias.get(scheme, alias.get(cofactor, scheme))
    if scheme not in COORDINATION_SCHEMES:
        raise NotImplementedError(
            f"build_cofactor_spec ships these coordination schemes as templates: "
            f"{sorted(COORDINATION_SCHEMES)}; got cofactor={cofactor!r} scheme={scheme!r}. "
            "Add your own CofactorSite/CoordinatingGroup list for a different scheme (see docstring).")
    s = COORDINATION_SCHEMES[scheme]

    site = CofactorSite(
        cofactor=s["cofactor"], metal=s["metal"], coordination=s["coordination"],
        n_protein_ligands=s["n_protein_ligands"], ligand_residue=s["ligand_residue"],
        ligand_atom=s["ligand_atom"], target_metal_ligand_dist=s["target_metal_ligand_dist"],
        target_ligand_metal_ligand_angle=s["target_ligand_metal_ligand_angle"],
        function=s["function"], scheme_key=scheme)

    # Build the coordinating-group list. For mixed-ligand schemes the residue/atom strings carry both.
    groups = []
    role_prefix = "axial_ligand" if "heme" in site.cofactor else "cluster_ligand"
    res_list = site.ligand_residue.split("+")
    atom_list = site.ligand_atom.split("/")
    for i in range(site.n_protein_ligands):
        res = res_list[i] if i < len(res_list) else res_list[-1]
        atom = atom_list[i] if i < len(atom_list) else atom_list[-1]
        groups.append(CoordinatingGroup(
            role=f"{role_prefix}_{i + 1}", residue=res, atom=atom,
            target_distance=site.target_metal_ligand_dist,
            target_angle=site.target_ligand_metal_ligand_angle,
            note=f"PLACEHOLDER — {res} {atom} coordinates the {site.metal}; FIX during sequence "
                 f"design. {s['note']}"))

    return CofactorSpec(
        cofactor=s["cofactor"],
        function=s["function"],
        site_description=(f"TEMPLATE — {s['coordination']} coordination of {s['cofactor']} for "
                          f"{s['function']}; fill the metal-ligand distances/angles from a verified "
                          "reference structure / literature."),
        coordinating_groups=groups,
        cofactor_site=site,
    )


# --------------------------------------------------------------------------------------- #
# scaffold_cofactor_pocket(cofactor, n, tool) → candidate backbones presenting the pocket.
# --------------------------------------------------------------------------------------- #
def scaffold_cofactor_pocket(cofactor, n: int = 8, tool: str = "mock",
                             out_dir: str = "results/scaffolds") -> list:
    """Generate `n` candidate backbones that present the cofactor-coordination motif.

    `cofactor` may be a CofactorSpec (preferred) or a string (which is built into a default spec).

    Real backends (wire up on an A100 / HPC — scaffolding is the A100-bound step):
      tool="rfdiffusion2"  → RFdiffusion2 all-atom motif scaffolding (Dauparas 2025); can place the
                             cofactor + coordinating ligands as an all-atom motif. VERIFY the current
                             public release/repo at generation time.
      tool="riffdiff"      → Riff-Diff motif-to-protein scaffolding (Schnettler 2025, Nature); VERIFY
                             the current public release/repo at generation time.
      tool="rfdiffusion"   → classic RFdiffusion motif scaffolding (RosettaCommons/RFdiffusion);
                             present the coordinating residues as a motif (treat the cofactor as an
                             external ligand); a smaller free-tier demo, good for the P1 hello-world.

    The mock backend returns deterministic placeholder records so the pipeline runs with no GPU. Each
    record's `motif_rmsd` etc. are SYNTHETIC.

    >>> A100 NOTE: scaffolding a large pool is the compute bottleneck. Free Colab T4 can do a small
        RFdiffusion motif-scaffolding DEMO (tens of backbones); the real campaign (1000s,
        RFdiffusion2/Riff-Diff) wants an A100 (Colab Pro+) or an HPC GPU. Cofactor-pocket placement is
        harder than a single-sidechain motif — budget extra backbones because many will not hold a
        clean coordination geometry (e.g. two axial His on opposite helices at the right Fe distance).
    """
    spec = cofactor if isinstance(cofactor, CofactorSpec) else build_cofactor_spec(str(cofactor))
    os.makedirs(out_dir, exist_ok=True)
    tool = tool.lower()
    real = {"rfdiffusion2", "riffdiff", "rfdiffusion"}
    if tool in real:
        # TODO(student): call the chosen scaffolding backend here on Colab/HPC.
        #   - export the cofactor site as the tool's motif/constraint format (contigs + the cofactor
        #     ligand + the coordinating ligand atoms as an all-atom motif / external ligand),
        #   - run N backbones (1000s for the real campaign — A100),
        #   - return one record per written backbone PDB.
        raise NotImplementedError(
            f"Wire up the real '{tool}' scaffolding backend (A100/HPC). See the docstring; verify the "
            "current RFdiffusion2/Riff-Diff release at generation time. Export the cofactor + "
            "coordinating ligands as the tool's all-atom motif / external-ligand spec.")
    if tool != "mock":
        raise ValueError(f"unknown tool {tool!r}; options: mock | {' | '.join(sorted(real))}")

    site = spec.cofactor_site
    base = _seed_from(spec.cofactor, spec.function, n)
    records = []
    for i in range(n):
        s = base ^ _seed_from("scaffold", i)
        rec = {
            "design_id": f"EXAMPLE_DATA_scaffold_{i:03d}",
            "tool": "mock",
            "backbone_pdb": None,  # real backend writes a PDB path here
            "length": 100 + int(_unit(s, "len") * 100),       # 100-200 aa, SYNTHETIC
            "motif_rmsd": round(0.2 + _unit(s, "motif") * 1.2, 3),   # A, SYNTHETIC
            "coordinating_residues": spec.coordinating_residue_ids(),
            "cofactor": spec.cofactor,
            "metal": site.metal if site else "FE",
            "synthetic": True,
        }
        records.append(rec)
    with open(os.path.join(out_dir, "scaffolds_mock.json"), "w") as fh:
        json.dump(records, fh, indent=2)
    return records


# --------------------------------------------------------------------------------------- #
# ligandmpnn_cofactor(backbone, coordinating_residues, n) → COFACTOR-AWARE sequences, ligands FIXED.
# This is the CENTRAL tool for this project.
# --------------------------------------------------------------------------------------- #
def ligandmpnn_cofactor(backbone: dict, coordinating_residues: list, n: int = 8,
                        cofactor: str = "heme_b", tool: str = "mock") -> list:
    """Design `n` sequences for one backbone with a COFACTOR-AWARE LigandMPNN, FIXING the ligands.

    This is the heart of Project 24 and why LigandMPNN (not vanilla ProteinMPNN) is required: the
    coordinating residues (e.g. the two axial His of a bis-His heme) must hold the cofactor, so (a)
    those positions are FIXED and (b) the cofactor (heme / cluster / metal) is passed as ligand/atom
    context so the model designs the rest of the protein to accommodate (and not clash with) the
    bound cofactor. ProteinMPNN cannot see the cofactor.

    Real backend (CPU-fast — this step is cheap, unlike scaffolding):
      tool="ligandmpnn" → LigandMPNN (https://github.com/dauparas/LigandMPNN). Pass the cofactor as
                          the ligand/atom context (`--ligand_mpnn_use_atom_context 1`) and a
                          fixed-positions list covering ALL coordinating residues so they are NOT
                          redesigned. Verify the current model/flag names against the repo.

    The mock backend returns deterministic placeholder sequences (coordinating positions annotated as
    fixed) so the plumbing runs anywhere. All scores are SYNTHETIC. To make the mock realistic, the
    fixed coordinating positions are seeded as their ligand residue (His = "H", Cys = "C", Met = "M").
    """
    tool = tool.lower()
    if tool == "ligandmpnn":
        # TODO(student): run cofactor-aware LigandMPNN.
        #   - pass the cofactor (heme / [4Fe-4S] / Zn) as the ligand/atom context
        #     (--ligand_mpnn_use_atom_context 1),
        #   - pass --fixed_residues (or the JSON fixed-positions spec) covering ALL coordinating
        #     residues so they are preserved (confirm the numbering matches the backbone PDB),
        #   - choose the appropriate (ligand/metal) checkpoint; parse the FASTA out.
        raise NotImplementedError(
            "Wire up cofactor-aware LigandMPNN (CPU-fast): pass the cofactor as atom/ligand context "
            "and a fixed-positions list for ALL coordinating residues so the coordination scheme is "
            "preserved. https://github.com/dauparas/LigandMPNN")
    if tool != "mock":
        raise ValueError(f"unknown tool {tool!r}; options: mock | ligandmpnn")

    bid = backbone.get("design_id", "bb")
    length = int(backbone.get("length", 140))
    n_lig = max(1, len(coordinating_residues))
    # Spread the fixed coordinating positions across the chain (SYNTHETIC placement).
    fixed_positions = [int((k + 1) * length / (n_lig + 1)) for k in range(n_lig)]
    aa = "ACDEFGHIKLMNPQRSTVWY"
    seqs = []
    for j in range(n):
        s = _seed_from(bid, "ligandmpnn", j)
        chars = [aa[(_seed_from(bid, j, k) >> 3) % 20] for k in range(length)]
        # Seed the fixed coordinating positions as histidine (the common heme/Zn ligand) so the mock
        # sequence visibly carries a "fixed" ligand residue. Real design keeps the true ligand identity.
        for pos in fixed_positions:
            if 0 <= pos < length:
                chars[pos] = "H"
        seqs.append({
            "design_id": f"{bid}_seq{j:02d}",
            "sequence": "".join(chars),
            "fixed_coordinating_roles": list(coordinating_residues),
            "fixed_positions": fixed_positions,
            "cofactor": cofactor,
            "mpnn_score": round(0.8 + _unit(s, "mpnn") * 0.6, 3),  # SYNTHETIC (lower ~ more confident)
            "tool": "mock",
            "synthetic": True,
        })
    return seqs


# --------------------------------------------------------------------------------------- #
# coordination_geometry(predicted_pdb, site) → the KEY metric (maps to cat_geom in the filter).
# --------------------------------------------------------------------------------------- #
def coordination_geometry(predicted_pdb: Optional[str], site) -> float:
    """RMSD (A) of the predicted coordinating atoms vs the target coordination geometry.

    This is THE metric for this project (it populates `catalytic_geom_rmsd` / cat_geom in the shared
    enzyme filter, where for Project 24 cat_geom == COORDINATION-geometry RMSD): coordination-geometry
    RMSD < 0.5 A vs the target scheme is the pass bar. A design can fold beautifully (high pLDDT) yet
    present the coordinating atoms (e.g. the two axial His Nepsilon2) at the wrong distance/angle to hold
    the cofactor — only this metric catches that.

    `site` may be a CofactorSpec or a CofactorSite.

    Real implementation (wire up with the AF2/predicted PDB):
      - parse the predicted (apo) structure (Biopython); AF2 does NOT place the metal/cofactor,
      - extract the coordinating atoms (the `atom` of each coordinating residue at the designed
        positions) and the (modelled/placed) metal position,
      - measure metal-ligand distances + ligand-metal-ligand angles and score them as an RMSD vs the
        target coordination scheme. (For heme, you may first dock/superpose the heme to place the Fe.)
    A teaching-grade Cα/atom superposition helper exists in shared/filtering_pipeline.ca_rmsd; here you
    need an ATOM-level distance/angle deviation over just the coordinating atoms + metal.

    The mock path (predicted_pdb is None or missing) returns a deterministic SYNTHETIC value seeded by
    the site + path, so the filtering plumbing runs with no real structure.
    """
    cof = getattr(site, "cofactor", str(site))
    if predicted_pdb and os.path.exists(predicted_pdb):
        # TODO(student): real atom-level coordination-geometry deviation (distances + angles) vs the
        # target scheme over the coordinating atoms + the (modelled/docked) metal position.
        raise NotImplementedError(
            "Implement atom-level coordination-geometry RMSD (metal-ligand distances + "
            "ligand-metal-ligand angles) vs the target scheme. AF2 gives the apo backbone; place the "
            "metal/cofactor by docking/superposition first (parse with Biopython).")
    s = _seed_from(str(cof), str(predicted_pdb))
    # SYNTHETIC: spread around the 0.5 A cutoff so the demo filter both passes and fails designs.
    return round(0.15 + _unit(s, "coordgeom") * 0.9, 3)


# --------------------------------------------------------------------------------------- #
# dock_cofactor(pocket, cofactor, tool) → does the cofactor fit/orient in the designed pocket?
# --------------------------------------------------------------------------------------- #
def dock_cofactor(pocket: Optional[str], cofactor: str = "heme_b", tool: str = "mock") -> dict:
    """Dock the cofactor into the designed pocket as a fit/orientation sanity check.

    For heme this checks the porphyrin physically fits the pocket and the Fe sits between the axial
    ligands; for a [4Fe-4S] cluster, that the Cys cage can enclose the cubane. Docking is a FIT /
    ORIENTATION check — it is NOT a binding-affinity, an incorporation, or a function measurement
    (only spectroscopy confirms incorporation + function).

    Real backend:
      tool="vina" → AutoDock Vina (https://github.com/ccsb-scripps/AutoDock-Vina). Prepare the
                    receptor (designed pocket) + the cofactor ligand (PDBQT; heme is a large, mostly
                    rigid macrocycle — set up the metal + ring carefully), define the box around the
                    coordination site, run, and read the top score + pose. NOTE: docking metal-bearing
                    cofactors is approximate — treat the score as a coarse fit indicator only.

    Mock path returns a deterministic SYNTHETIC score + a placeholder pose flag.
    """
    tool = tool.lower()
    if tool == "vina":
        # TODO(student): receptor/ligand prep (PDBQT) → define box at the coordination site → run Vina
        #   → parse the best score + pose; check the Fe/metal sits between the coordinating ligands.
        raise NotImplementedError(
            "Wire up AutoDock Vina: prep receptor + cofactor PDBQT (heme macrocycle + Fe), box the "
            "coordination site, run, parse the top score/pose. Metal-cofactor docking is approximate. "
            "https://github.com/ccsb-scripps/AutoDock-Vina")
    if tool != "mock":
        raise ValueError(f"unknown tool {tool!r}; options: mock | vina")
    s = _seed_from(str(pocket), str(cofactor))
    return {
        "cofactor": cofactor,
        "vina_score": round(-5.0 - _unit(s, "dock") * 5.0, 2),   # kcal/mol-ish, SYNTHETIC (heme is big)
        "pose_in_pocket": _unit(s, "pose") > 0.25,                # SYNTHETIC
        "fe_between_ligands": _unit(s, "axial") > 0.30,           # SYNTHETIC (axial coordination check)
        "tool": "mock",
        "synthetic": True,
    }


# --------------------------------------------------------------------------------------- #
# cofactor_site_md(...) — optional short MD of pocket/coordination stability (OpenMM). Mock stub.
# --------------------------------------------------------------------------------------- #
def cofactor_site_md(predicted_pdb: Optional[str], ns: float = 10.0, tool: str = "mock") -> dict:
    """Short MD to check the cofactor pocket / coordination doesn't collapse (OpenMM). Mock = SYNTHETIC.

    Real backend: OpenMM (https://github.com/openmm/openmm) — solvate, minimize, short NPT run.
    Report coordinating-atom RMSF / mean backbone RMSD over the trajectory.

    >>> METAL/COFACTOR-FF CAVEAT: classical force fields model a coordinated metal / heme Fe POORLY
        (fixed charges, no charge transfer / polarisation / spin state; bonded vs non-bonded metal
        models each have failure modes). So this MD is a WEAK, CAVEATED stability proxy for a
        metalloprotein, NOT ground truth. Note this explicitly wherever you report it; for the metal
        centre itself, spectroscopy (not MD) is the real test.
    """
    tool = tool.lower()
    if tool == "openmm":
        # TODO(student): build system (choose a metal/heme FF model + note its limits), minimize,
        #   equilibrate, run `ns`, compute coordinating-atom RMSF + mean backbone RMSD.
        raise NotImplementedError(
            "Wire up OpenMM: solvate/minimize/equilibrate, run a short trajectory, report "
            "coordinating-atom RMSF + mean backbone RMSD. NOTE the classical-metal-FF caveat. "
            "https://github.com/openmm/openmm")
    if tool != "mock":
        raise ValueError(f"unknown tool {tool!r}; options: mock | openmm")
    s = _seed_from(str(predicted_pdb), ns)
    return {
        "ns": ns,
        "md_rmsd": round(0.8 + _unit(s, "md") * 2.6, 3),           # A, SYNTHETIC
        "coordinating_rmsf": round(0.3 + _unit(s, "rmsf") * 1.4, 3),  # A, SYNTHETIC
        "ff_caveat": "classical metal/heme FF is approximate — weak proxy, not ground truth",
        "tool": "mock",
        "synthetic": True,
    }


if __name__ == "__main__":
    # No-GPU smoke test: spec → scaffold → cofactor-aware LigandMPNN(fixed) → coordination geometry →
    # cofactor docking → (caveated) MD. ALL NUMBERS SYNTHETIC.
    print("== cofactor_tools.py smoke test (mock backend; ALL NUMBERS SYNTHETIC) ==")
    spec = build_cofactor_spec("heme", scheme="bis_his_heme")
    print("cofactor :", spec.cofactor, "| function:", spec.function)
    print("coordination:", spec.cofactor_site.coordination)
    for g in spec.coordinating_groups:
        print(f"  - {g.role:16s} {g.residue}/{g.atom:4s}  d={g.target_distance}A  {g.note[:46]}")
    scaffolds = scaffold_cofactor_pocket(spec, n=3)
    print(f"scaffolds: {len(scaffolds)} (mock)  e.g. {scaffolds[0]['design_id']} "
          f"len={scaffolds[0]['length']} motif_rmsd={scaffolds[0]['motif_rmsd']}A")
    seqs = ligandmpnn_cofactor(scaffolds[0], spec.coordinating_residue_ids(), n=2,
                               cofactor=spec.cofactor)
    print(f"sequences for {scaffolds[0]['design_id']}: {len(seqs)} (fixed roles: "
          f"{seqs[0]['fixed_coordinating_roles']}, positions {seqs[0]['fixed_positions']})")
    cg = coordination_geometry(None, spec)
    print(f"coordination_geometry (mock) = {cg} A  (pass if < 0.5)")
    dock = dock_cofactor(None, spec.cofactor)
    print(f"dock_cofactor (mock): score={dock['vina_score']} in_pocket={dock['pose_in_pocket']} "
          f"fe_between_ligands={dock['fe_between_ligands']}")
    md = cofactor_site_md(None, ns=10.0)
    print(f"cofactor_site_md (mock): md_rmsd={md['md_rmsd']}A coordinating_rmsf={md['coordinating_rmsf']}A")
    print("OK — plumbing runs with no GPU. Switch backends to rfdiffusion2/riffdiff/ligandmpnn/vina/"
          "openmm on Colab/HPC. NONE of these numbers are real; confirm with SPECTROSCOPY, not MD.")
