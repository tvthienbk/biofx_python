"""
na_binder_tools.py — protein–nucleic-acid binder design wrappers for Project 23
(DNA/RNA-binding mini-proteins).

Goal: clean, import-safe entry points for the NA-aware design + modeling steps, so the
notebooks stay thin and the logic is testable WITHOUT a GPU:

    scaffold_near_na(target_na, n, tool="mock")           -> list[NABinderDesign]   (RFdiffusion near the NA)
    ligandmpnn_na(backbone, na, n, tool="mock")           -> list[NABinderDesign]   (LigandMPNN, NA-aware — central)
    model_complex(protein, na, tool="mock")               -> {pae_interaction, plddt, scrmsd}
    motif_specificity(binder, motif, scrambled, tool="mock") -> {dG_motif, dG_scrambled, dScore, specific}

This project follows the BINDER-FAMILY TEMPLATE (`projects/project_06_pdl1_binder/`,
`scripts/binder_tools.py`): keep the mock deterministic, the real backends behind documented
TODOs with A100 notes, and ALL mock numbers flagged SYNTHETIC. The scientific difference: the
"target" is a **nucleic acid** (DNA or RNA), and the central design tool is **LigandMPNN**, which
explicitly models nucleic-acid context — ProteinMPNN does not.

DESIGN NOTE FOR STUDENTS
------------------------
Real backbone generation near a nucleic acid (RFdiffusion) and protein–NA complex modeling
(AF3-style / Boltz / AF2) are heavy and want an A100 (see MANUAL.md §2). LigandMPNN sequence
design is CPU-cheap. Each backend's real path is a clearly-marked TODO you complete/verify on
Colab; the heavy import happens lazily INSIDE the function. The module imports fine here with no
GPU and no heavy packages. The `mock` backend is DETERMINISTIC (seeded by sequence/target/motif)
so you can develop and unit-test the plumbing — ranking, CSV assembly, the filter hand-off, and the
specificity comparison — before spending GPU time.

The single hardest thing in protein–NA design is **sequence specificity**: a designed protein can
stick to *any* DNA/RNA backbone (the phosphates are negatively charged and generic) without reading
the intended base sequence. Every result here is therefore reported against a **scrambled motif**
control, and the wet-lab plan (notebook 05) mandates a scrambled-NA EMSA/anisotropy control.
NEVER present mock numbers as real results: they are SYNTHETIC by construction, and there is no
fabricated K_D anywhere in this project.

Pinned upstreams (verify they still exist — version-verify cell; pin commits, they change):
  LigandMPNN     https://github.com/dauparas/LigandMPNN       # NA-aware sequence design (CENTRAL). Pin a commit.
  RFdiffusion    https://github.com/RosettaCommons/RFdiffusion # scaffold a backbone near the NA. Pin a commit.
  Boltz          https://github.com/jwohlwend/boltz            # protein–NA complex modeling (Boltz-2). Pin a commit.
  ColabFold      https://github.com/sokrypton/ColabFold        # AF2 complex modeling fallback. Pin a commit.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional

# 20 canonical amino acids, used to synthesize deterministic mock binder sequences.
_AA = "ACDEFGHIKLMNPQRSTVWY"
# Nucleic-acid alphabets (DNA uses T, RNA uses U). Used to validate/normalize target motifs.
_DNA = set("ACGT")
_RNA = set("ACGU")
_MOCK_FLAG = "SYNTHETIC — mock backend, not a real design/prediction"


@dataclass
class NABinderDesign:
    """One designed protein that is meant to bind a nucleic-acid (DNA/RNA) target motif."""
    design_id: str
    sequence: str
    paradigm: str                        # "rfdiffusion+ligandmpnn" | "ligandmpnn" | "proteinmpnn" | "mock"
    na_type: str = "DNA"                 # "DNA" | "RNA"
    target_motif: str = ""               # the intended NA sequence motif (e.g. a TF box / RNA hairpin seq)
    seq_tool: str = "ligandmpnn"         # which sequence designer made this ("ligandmpnn" | "proteinmpnn")
    length: Optional[int] = None
    # filled by model_complex():
    plddt: Optional[float] = None
    pae_interaction: Optional[float] = None   # interface PAE protein<->NA (the key complex metric)
    scrmsd: Optional[float] = None
    # filled by motif_specificity():
    dG_motif: Optional[float] = None          # interface score vs the INTENDED motif (lower = better)
    dG_scrambled: Optional[float] = None       # interface score vs a SCRAMBLED motif (specificity control)
    specificity_score: Optional[float] = None  # dG_scrambled - dG_motif (higher = more specific)
    is_specific: Optional[bool] = None
    synthetic: bool = False              # True => numbers are mock/EXAMPLE_DATA, never report as real
    notes: list = field(default_factory=list)

    def as_row(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- #
# Deterministic hashing + mock-sequence helpers (mock reproducibility — graded).
# --------------------------------------------------------------------------- #
def _hashints(*parts) -> int:
    """Stable integer hash of the inputs (NOT Python's salted hash) for deterministic mock numbers."""
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h, 16)


def _mock_sequence(seed_int: int, length: int) -> str:
    """Deterministic pseudo-random amino-acid sequence (mock binder)."""
    seq = []
    x = seed_int
    for _ in range(length):
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        seq.append(_AA[x % len(_AA)])
    return "".join(seq)


# --------------------------------------------------------------------------- #
# Nucleic-acid motif helpers
# --------------------------------------------------------------------------- #
def normalize_motif(motif: str, na_type: str = "DNA") -> str:
    """Uppercase + validate a target NA motif against the DNA/RNA alphabet.

    The motif is the intended recognition sequence (a transcription-factor box, an RNA hairpin
    sequence, an operator, ...). Derive yours from the complex/literature you verify — don't invent
    one (see data/README.md). Raises ValueError on out-of-alphabet characters so typos fail loudly.
    """
    m = (motif or "").strip().upper().replace(" ", "")
    if not m:
        return ""
    alpha = _RNA if str(na_type).upper() == "RNA" else _DNA
    bad = set(m) - alpha
    if bad:
        raise ValueError(f"motif {motif!r} has non-{na_type} bases {sorted(bad)}; "
                         f"allowed = {sorted(alpha)} (RNA uses U, DNA uses T)")
    return m


def scramble_motif(motif: str, seed: int = 0) -> str:
    """Deterministically shuffle a motif to make a SPECIFICITY CONTROL (same base composition,
    different order). A truly *specific* binder should prefer the real motif over this scramble;
    a binder that does equally well on both is reading the backbone, not the bases.
    """
    import random
    rng = random.Random(seed)
    chars = list(motif)
    # Re-roll until the order actually changes (composition is preserved either way).
    for _ in range(8):
        rng.shuffle(chars)
        if "".join(chars) != motif or len(set(chars)) <= 1:
            break
    return "".join(chars)


# --------------------------------------------------------------------------- #
# Step 1 — scaffold a backbone NEAR the nucleic acid (RFdiffusion). Mock = deterministic.
# --------------------------------------------------------------------------- #
def scaffold_near_na(target_na, n: int = 50, tool: str = "mock",
                     na_type: str = "DNA", binder_length=(40, 90), **kwargs) -> list[NABinderDesign]:
    """RFdiffusion: diffuse `n` protein backbones docked against the nucleic-acid target.

    The NA is held as context so the backbone forms a complementary recognition surface (a helix
    into the major groove, a beta-sheet, a zinc-finger-like motif, ...). Sequence is NOT designed
    yet — that is ligandmpnn_na()'s job. Returns NABinderDesign objects with placeholder sequences.

    tool="mock"        -> deterministic SYNTHETIC backbones (no GPU; develop the plumbing).
    tool="rfdiffusion" -> real backend (A100 for hundreds of backbones near the NA).
    """
    tool = tool.lower()
    motif = normalize_motif(target_na, na_type)
    if tool == "mock":
        out = []
        for i in range(n):
            seed = _hashints("scaffold", motif, na_type, i)
            length = binder_length[0] + (seed % max(1, (binder_length[1] - binder_length[0] + 1)))
            out.append(NABinderDesign(
                design_id=f"EXAMPLE_DATA_scaffold_{i:04d}",
                sequence="X" * length,            # placeholder; ligandmpnn_na() designs the real sequence
                paradigm="rfdiffusion+ligandmpnn", na_type=na_type, target_motif=motif,
                seq_tool="(undesigned)", length=length, synthetic=True,
                notes=[_MOCK_FLAG + " (backbone only — sequence undesigned)"],
            ))
        return out
    if tool == "rfdiffusion":
        # TODO (Colab, A100): RFdiffusion with the nucleic acid as fixed context.
        #   repo: https://github.com/RosettaCommons/RFdiffusion  (pin a commit)
        #   1) prepare a PDB of the target NA (DNA/RNA) in the desired conformation;
        #   2) diffuse n binder backbones docked against it (contigs describe the binder length;
        #      keep the NA chain fixed). Hundreds of backbones want an A100/HPC.
        #   3) pass each backbone to ligandmpnn_na() for NA-aware sequence design.
        #   NOTE: RFdiffusion's NA support is evolving — verify the current protocol/commit and that
        #   it keeps the nucleic acid as context. If unavailable, scaffold against the protein chain
        #   of a known protein–NA complex and re-introduce the NA at the modeling step.
        raise NotImplementedError(
            "Wire up RFdiffusion near the nucleic acid here (A100). See MANUAL.md §2 and the pinned "
            "repo; develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, rfdiffusion")


# --------------------------------------------------------------------------- #
# Step 2 — LigandMPNN, NUCLEIC-ACID-AWARE sequence design (THE central tool). Mock = deterministic.
# --------------------------------------------------------------------------- #
def ligandmpnn_na(backbone, na, n: int = 4, tool: str = "mock",
                  na_type: str = "DNA", temperature: float = 0.1,
                  seq_tool: str = "ligandmpnn", **kwargs) -> list[NABinderDesign]:
    """LigandMPNN: design `n` sequences for a backbone WITH the nucleic acid in context.

    This is the project's central step. LigandMPNN conditions on non-protein atoms — including
    DNA/RNA — so the designed residues at the interface are chosen to read the bases / contact the
    phosphate backbone. ProteinMPNN (seq_tool="proteinmpnn") ignores the NA context; the nb04
    benchmark compares the two at the interface.

    `backbone` is an NABinderDesign from scaffold_near_na() (or a path/handle on Colab).
    `na` is the target motif (string) or a handle to the NA structure.

    tool="mock"        -> deterministic SYNTHETIC sequences (no GPU).
    tool="ligandmpnn"  -> real backend; tool="proteinmpnn" -> NA-blind baseline for the benchmark.
    """
    tool = tool.lower()
    motif = normalize_motif(na if isinstance(na, str) else getattr(backbone, "target_motif", ""), na_type)
    length = getattr(backbone, "length", None) or 60
    parent_id = getattr(backbone, "design_id", "bb")
    if tool == "mock":
        out = []
        for j in range(n):
            # Seed with the sequence designer too, so LigandMPNN vs ProteinMPNN give DIFFERENT mock
            # sequences (gives the nb04 head-to-head structure). Still SYNTHETIC.
            seed = _hashints("ligandmpnn", seq_tool, motif, na_type, parent_id, j, temperature)
            seq = _mock_sequence(seed, length)
            out.append(NABinderDesign(
                design_id=f"{parent_id}_seq{j:02d}_{seq_tool}",
                sequence=seq, paradigm=("ligandmpnn" if seq_tool == "ligandmpnn" else "proteinmpnn"),
                na_type=na_type, target_motif=motif, seq_tool=seq_tool, length=length,
                synthetic=True, notes=[_MOCK_FLAG],
            ))
        return out
    if tool in ("ligandmpnn", "proteinmpnn"):
        # TODO (Colab): run (Ligand)MPNN on the backbone WITH the nucleic acid as context.
        #   LigandMPNN repo: https://github.com/dauparas/LigandMPNN  (pin a commit)
        #   key args: --pdb_path <backbone+NA complex>, --model_type ligand_mpnn (NA-aware),
        #             --temperature (0.1-0.3), --number_of_batches / --batch_size for n sequences,
        #             --fixed_residues / --redesigned_residues to focus the interface.
        #   For the NA-BLIND baseline (benchmark), run ProteinMPNN (or LigandMPNN without the NA in
        #   context) so the comparison isolates the value of the nucleic-acid conditioning.
        #   LigandMPNN/ProteinMPNN are CPU-cheap; this step is NOT the bottleneck (modeling is).
        raise NotImplementedError(
            "Wire up LigandMPNN (NA-aware) here. See MANUAL.md §2 and the pinned repo; the NA must be "
            "in context for the ligand_mpnn model. Develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, ligandmpnn, proteinmpnn")


# --------------------------------------------------------------------------- #
# Step 3 — model the protein–NA complex (AF3-style / Boltz / AF2). Mock = deterministic.
# --------------------------------------------------------------------------- #
def model_complex(protein, na, tool: str = "mock", na_type: str = "DNA", **kwargs) -> dict:
    """Model a (protein, nucleic-acid) complex and return the metrics the shared filter consumes:
        {plddt, pae_interaction, scrmsd}  (+ synthetic flag for mock).

    `pae_interaction` (interface PAE between the protein and the NA chain) is the key protein–NA
    complex-confidence metric, analogous to AF2-Multimer pae_interaction for protein–protein binders.
    Low = the model is confident about the *relative* placement of protein and nucleic acid — it is
    NOT a binding affinity and NOT a specificity measurement (use motif_specificity() for that).

    `protein` is an amino-acid sequence (or NABinderDesign); `na` is the motif string / NA handle.
    tool="mock"           -> deterministic SYNTHETIC numbers; tool="boltz"/"af3"/"af2" -> real (A100).
    """
    tool = tool.lower()
    seq = protein.sequence if isinstance(protein, NABinderDesign) else str(protein)
    motif = normalize_motif(na if isinstance(na, str) else getattr(protein, "target_motif", ""), na_type)
    if not seq or any(c not in _AA for c in seq.upper()):
        return dict(plddt=None, pae_interaction=None, scrmsd=None,
                    ok=False, error="invalid amino-acid sequence")
    if tool == "mock":
        h = _hashints("model", na_type, motif, seq.upper())
        # Deterministic SYNTHETIC metrics in plausible-but-arbitrary ranges. These are NOT real.
        plddt = 70 + (h % 30)                        # 70–99
        pae_interaction = 5 + (h % 16)               # 5–20 Å (key complex metric; lower better)
        scrmsd = round(0.8 + (h % 350) / 100.0, 3)   # 0.8–4.3 Å
        return dict(plddt=float(plddt), pae_interaction=float(pae_interaction),
                    scrmsd=float(scrmsd), ok=True, synthetic=True, error=_MOCK_FLAG)
    if tool in ("boltz", "boltz2", "af3", "alphafold3", "af2", "colabfold"):
        # TODO (Colab, A100): model the protein–NA complex and parse the interface metrics.
        #   Boltz-2 (protein–NA): https://github.com/jwohlwend/boltz   (pin a commit) — supports
        #     nucleic-acid chains; build a YAML/FASTA with the protein + the DNA/RNA motif and run
        #     `boltz predict`. Parse the protein<->NA interface PAE -> pae_interaction, mean pLDDT,
        #     and scRMSD (designed vs predicted protein backbone).
        #   AF3-style servers also model protein–NA; ColabFold/AF2 is a weaker protein–protein fallback.
        #   Complex modeling is the slow step — batch overnight; campaign-scale prefers A100.
        raise NotImplementedError(
            "Wire up protein–NA complex modeling here (Boltz-2 / AF3-style; A100). See MANUAL.md §2 "
            "and the pinned repo; develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, boltz/af3/af2")


def score_designs(designs: list[NABinderDesign], na=None, tool: str = "mock") -> list[NABinderDesign]:
    """Run model_complex() over a list of designs and fill their metric fields in place."""
    for d in designs:
        target = na if na is not None else d.target_motif
        m = model_complex(d.sequence, target, tool=tool, na_type=d.na_type)
        if not m.get("ok", True):
            d.notes.append(f"model_complex failed: {m.get('error')}")
            continue
        d.plddt = m["plddt"]
        d.pae_interaction = m["pae_interaction"]
        d.scrmsd = m["scrmsd"]
        if m.get("synthetic"):
            d.synthetic = True
    return designs


# --------------------------------------------------------------------------- #
# Step 4 — sequence SPECIFICITY: intended motif vs SCRAMBLED motif (the real challenge). Mock=det.
# --------------------------------------------------------------------------- #
def motif_specificity(binder, motif, scrambled=None, tool: str = "mock",
                      na_type: str = "DNA", **kwargs) -> dict:
    """Compare a binder's interface against the INTENDED motif vs a SCRAMBLED motif.

    This is the heart of protein–NA design. A binder that scores ~equally on the real and scrambled
    motifs is reading the (generic, negatively-charged) backbone, not the bases — it is NON-specific.
    We report:
        dG_motif      : interface score vs the intended motif (lower/more-negative = stronger)
        dG_scrambled  : interface score vs the scrambled motif
        dScore        : dG_scrambled - dG_motif  (POSITIVE and large => prefers the real motif => specific)
        specific      : dScore >= SPEC_MARGIN
    On Colab these come from re-modeling the complex against each motif (model_complex) and/or an
    interface-energy calculation; here they are deterministic SYNTHETIC stand-ins.

    NOTE: this is a *computational specificity proxy*, not an experiment. The mandatory experimental
    test is an EMSA / fluorescence-anisotropy assay with a SCRAMBLED-NA control (notebook 05).
    """
    tool = tool.lower()
    seq = binder.sequence if isinstance(binder, NABinderDesign) else str(binder)
    motif = normalize_motif(motif, na_type)
    if scrambled is None:
        scrambled = scramble_motif(motif, seed=_hashints("scramble", motif) % 10**6)
    else:
        scrambled = normalize_motif(scrambled, na_type)
    SPEC_MARGIN = float(kwargs.get("spec_margin", 1.5))   # min dScore (REU-like) to call "specific"
    if tool == "mock":
        # Deterministic SYNTHETIC interface scores. The real motif is given a hash-dependent edge for
        # SOME binders and not others, so the specificity analysis in nb04 has realistic structure:
        # many designs are non-specific (the honest, hard truth of protein–NA design).
        hm = _hashints("spec", "motif", na_type, motif, seq.upper())
        hs = _hashints("spec", "scram", na_type, scrambled, seq.upper())
        dG_motif = -(20 + (hm % 25))                      # ~ -20..-44 (lower = stronger)
        dG_scram = -(20 + (hs % 25))
        dScore = round(dG_scram - dG_motif, 2)            # >0 => prefers the intended motif
        return dict(motif=motif, scrambled=scrambled,
                    dG_motif=float(dG_motif), dG_scrambled=float(dG_scram),
                    dScore=dScore, specific=bool(dScore >= SPEC_MARGIN),
                    spec_margin=SPEC_MARGIN, ok=True, synthetic=True, error=_MOCK_FLAG)
    if tool in ("boltz", "af3", "af2", "rosetta", "colabfold"):
        # TODO (Colab): compute an interface score vs the intended motif AND vs the scrambled motif.
        #   Option A (modeling): model_complex(binder, motif) and model_complex(binder, scrambled);
        #     compare interface PAE / interface pLDDT (specific => better on the intended motif).
        #   Option B (energy): thread the binder onto each NA and score the interface (Rosetta/FoldX).
        #   Report dScore = score(scrambled) - score(motif); a specific design prefers the real motif.
        #   This is a COMPUTATIONAL proxy — the wet-lab scrambled-NA EMSA/anisotropy control is required.
        raise NotImplementedError(
            "Wire up the motif-vs-scrambled specificity calc here (re-model or re-score each motif). "
            "See MANUAL.md §2; develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, boltz/af3/af2/rosetta")


def add_specificity(designs: list[NABinderDesign], motif: str, scrambled=None,
                    tool: str = "mock") -> list[NABinderDesign]:
    """Run motif_specificity() over a list and fill dG_motif / dG_scrambled / specificity_score in place."""
    for d in designs:
        s = motif_specificity(d, motif, scrambled=scrambled, tool=tool, na_type=d.na_type)
        if not s.get("ok", True):
            d.notes.append(f"motif_specificity failed: {s.get('error')}")
            continue
        d.dG_motif = s["dG_motif"]
        d.dG_scrambled = s["dG_scrambled"]
        d.specificity_score = s["dScore"]
        d.is_specific = s["specific"]
        if s.get("synthetic"):
            d.synthetic = True
    return designs


if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps). All numbers are SYNTHETIC.
    NA_TYPE = "DNA"
    MOTIF = "TGACGTCA"  # EXAMPLE DNA motif (a CRE-like 8-bp box, strict ACGT) — VERIFY/REPLACE from your target (data/README.md)
    backbones = scaffold_near_na(MOTIF, n=3, tool="mock", na_type=NA_TYPE)

    # NA-aware (LigandMPNN) vs NA-blind (ProteinMPNN) sequence design over each backbone.
    lig, prot = [], []
    for bb in backbones:
        lig += ligandmpnn_na(bb, MOTIF, n=2, tool="mock", na_type=NA_TYPE, seq_tool="ligandmpnn")
        prot += ligandmpnn_na(bb, MOTIF, n=2, tool="mock", na_type=NA_TYPE, seq_tool="proteinmpnn")

    score_designs(lig, na=MOTIF, tool="mock")
    score_designs(prot, na=MOTIF, tool="mock")
    add_specificity(lig, MOTIF, tool="mock")
    add_specificity(prot, MOTIF, tool="mock")

    print(f"backbones (RFdiffusion mock): {len(backbones)}")
    print(f"LigandMPNN (NA-aware) designs: {len(lig)}   ProteinMPNN (NA-blind) designs: {len(prot)}")
    d = lig[0]
    print("example LigandMPNN design:", d.design_id, "len=", d.length,
          "pae_interaction=", d.pae_interaction, "scrmsd=", d.scrmsd)
    print("  specificity: dG_motif=", d.dG_motif, "dG_scrambled=", d.dG_scrambled,
          "dScore=", d.specificity_score, "specific=", d.is_specific, "synthetic=", d.synthetic)
    n_spec_lig = sum(bool(x.is_specific) for x in lig)
    n_spec_prot = sum(bool(x.is_specific) for x in prot)
    print(f"computationally 'specific' (mock): LigandMPNN {n_spec_lig}/{len(lig)}, "
          f"ProteinMPNN {n_spec_prot}/{len(prot)}")
    print("REMINDER: every number above is SYNTHETIC (mock) — never report it as a real result, and "
          "specificity must be confirmed by a scrambled-NA EMSA/anisotropy assay (notebook 05).")
