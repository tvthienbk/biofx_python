"""
humanization_tools.py — antibody humanization (CDR grafting / resurfacing) + humanness scoring +
ΔΔG-stability proxy + Vernier-zone back-mutation helpers for Project 16.

Goal: clean, import-safe entry points for the humanization workflow, so the notebooks stay thin and
the logic is testable WITHOUT a GPU:

    graft_cdrs(nonhuman_ab, human_framework, scheme="kabat", tool="mock") -> HumanizedVariant
    resurface(nonhuman_ab, surface_positions, tool="mock")                -> HumanizedVariant   [extension]
    humanness_score(seq, tool="mock")                                     -> {oasis_like, t20_like, germline_id}
    ddg_predict(parental_seq, variant_seq, tool="mock")                   -> {ddg_kcal_mol, ...}
    vernier_backmutations(variant, parental)                              -> [back-mutation suggestions]
    plus helpers: split_regions(), assemble_vh(), score_variants().

This project is part of the ANTIBODY FAMILY and follows the shape of Project 17's antibody_tools.py
(the antibody-family template): keep the mock DETERMINISTIC, the real backends behind documented
TODOs with compute notes, and ALL mock numbers flagged SYNTHETIC. The humanness and ΔΔG functions are
CLEARLY-LABELLED teaching heuristics, NOT the validated tools (OASis / Hu-mAb / T20 / AbLang for
humanness; FoldX / Rosetta for ΔΔG) — see the WARNING on each.

THE PROBLEM (why humanization matters)
--------------------------------------
A non-human (murine / chimeric) therapeutic antibody triggers an anti-drug-antibody (ADA) response in
patients — an immunogenicity / regulatory problem. Humanization rewrites the antibody so it looks like
a human germline antibody (low ADA risk) while keeping the original CDRs that confer binding. The
classic move is **CDR grafting**: transplant the non-human CDRs onto a human germline framework. But
grafting usually **costs affinity and stability** because framework residues that support the CDR loops
(the **Vernier zone**) change. The deliverable is therefore not "a humanized antibody" but
**humanized variants + the humanness↔stability trade-off + the back-mutations needed + a validation
plan** with controls (the parental antibody and an over-humanized decoy).

DESIGN NOTE FOR STUDENTS
------------------------
Real humanness scoring (OASis / Hu-mAb / T20 / AbLang) and ΔΔG prediction (FoldX / Rosetta on an
IgFold / ImmuneBuilder model) are the reportable backends. Each is a clearly-marked TODO you
complete/verify on Colab; the heavy import happens lazily INSIDE the function. The module imports fine
here with no GPU and no heavy packages. The `mock` backend is DETERMINISTIC (seeded by the inputs) so
you can develop and unit-test the plumbing — variant assembly, CSV hand-off, the filter mapping —
before spending compute. NEVER present mock numbers as real results: they are SYNTHETIC by
construction. NEVER fabricate a ΔΔG or a humanness number and report it as real.

Compute is genuinely light here: humanness scoring + IgFold + ΔΔG proxies are free-tier (Colab T4)
friendly (see MANUAL.md §2). This is one of the few antibody-family projects that does NOT need an A100.

Pinned upstreams (verify they still exist — version-verify cell; pin commits, they change):
  AbLang         https://github.com/oxpig/AbLang        (antibody language model; humanness + restoration)
  ImmuneBuilder  https://github.com/oxpig/ImmuneBuilder (IgFold-style Fv structure for ΔΔG modelling)
  ProteinMPNN    https://github.com/dauparas/ProteinMPNN (framework-position optimization [extension])
  Hu-mAb / OASis  (BioPhi: https://github.com/Merck/BioPhi) — VERIFY the current public release/host
                  for OASis/Hu-mAb humanness at course start; T20 is a separate server (verify).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional

# 20 canonical amino acids.
_AA = "ACDEFGHIKLMNPQRSTVWY"
_MOCK_FLAG = "SYNTHETIC — mock backend, not a real graft/prediction"

# --------------------------------------------------------------------------- #
# Teaching placeholder antibodies + frameworks.
#   These are TEACHING placeholder sequences (NOT a specific published therapeutic). The student
#   supplies a real published murine/chimeric therapeutic antibody VH/VL in notebook 01 and VERIFIES
#   it, plus the human germline framework(s) from IMGT/OAS. Do NOT treat these placeholders as a real
#   antibody — see data/README.md.
# --------------------------------------------------------------------------- #
# A non-human (e.g., murine) VH split into framework regions FR1..FR4 and the three CDRs. The CDRs are
# what we KEEP (they confer binding); the frameworks are what we REPLACE with human germline.
NONHUMAN_AB = {
    "name": "murine_VH_teaching_placeholder",   # VERIFY/replace with your real antibody (nb01)
    "chain": "VH",
    "FR1": "EVQLQQSGAELVRPGTSVKISCKAS",          # murine-flavoured FR (teaching placeholder)
    "CDR1": "GYTFTNYG",
    "FR2": "MNWVKQRPGQGLEWIG",
    "CDR2": "INTYTGEP",
    "FR3": "TYADDFKGRFAFSLETSASTAYLQINNLKNEDTATYFC",
    "CDR3": "ARYYGSSYWYFDV",
    "FR4": "WGQGTTLTVSS",
}

# A human germline VH framework (e.g., IGHV3-style) we graft the murine CDRs ONTO. Only FRs are used
# from the human side; the CDRs come from the non-human antibody. TEACHING placeholder — replace with
# the exact IMGT human germline you select in notebook 01.
HUMAN_FRAMEWORK = {
    "name": "human_IGHV_teaching_placeholder",   # VERIFY/replace with the IMGT germline you pick (nb01)
    "chain": "VH",
    "FR1": "EVQLVESGGGLVQPGGSLRLSCAAS",           # human-flavoured FR (teaching placeholder)
    "FR2": "WVRQAPGKGLEWVS",
    "FR3": "RFTISRDNSKNTLYLQMNSLRAEDTAVYYC",
    "FR4": "WGQGTLVTVSS",
}

# Vernier-zone positions: framework residues that pack against / support the CDR loops. When a graft
# changes one of these, it often perturbs the CDR conformation -> affinity/stability loss, so these are
# the prime BACK-MUTATION candidates (restore the non-human residue). Indices below are positions
# WITHIN each framework region (0-based), a TEACHING approximation of the canonical Vernier set
# (Foote & Winter 1992); for a real run map true Kabat/IMGT Vernier positions onto your sequences.
VERNIER_ZONE = {
    "FR1": [2, 24],
    "FR2": [12, 13],          # e.g., the residue just before CDR2 region
    "FR3": [1, 28, 29],       # e.g., the residues just before CDR3 / packing the loop base
}


@dataclass
class HumanizedVariant:
    """One humanized antibody variant produced by grafting (or resurfacing) + (optional) back-mutations."""
    variant_id: str
    sequence: str                       # full VH: FR1-CDR1-FR2-CDR2-FR3-CDR3-FR4
    method: str                         # "cdr_graft" | "resurface" | "parental" | "over_humanized_decoy"
    tool: str                           # "mock" | "ablang" | "proteinmpnn"
    parental: str = NONHUMAN_AB["name"]
    human_framework: str = HUMAN_FRAMEWORK["name"]
    scheme: str = "kabat"               # CDR-definition scheme used for the graft (kabat/chothia/imgt)
    back_mutations: tuple = ()          # Vernier back-mutations applied (e.g., ("FR2:V37I",))
    cdr1: str = ""
    cdr2: str = ""
    cdr3: str = ""
    # filled by humanness_score():  (teaching heuristics — NOT validated tools)
    oasis_like: Optional[float] = None  # OASis-like humanness fraction in [0,1] (higher = more human)
    t20_like: Optional[float] = None    # T20-like humanness score in [0,100] (higher = more human)
    germline_id: Optional[str] = None   # nearest human germline label (teaching proxy)
    # filled by ddg_predict():  (teaching heuristic — NOT FoldX/Rosetta)
    ddg_kcal_mol: Optional[float] = None  # predicted ΔΔG of (variant vs parental); >0 = destabilizing
    # filled by score / bookkeeping:
    n_framework_mutations: Optional[int] = None  # how many FR residues differ from the parental
    synthetic: bool = False             # True => numbers are mock/EXAMPLE_DATA, never report as real
    notes: list = field(default_factory=list)

    def as_row(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- #
# Deterministic hashing helper (mock backend reproducibility — graded).
# --------------------------------------------------------------------------- #
def _hashints(*parts) -> int:
    """Stable integer hash of the inputs (NOT Python's salted hash) for deterministic mock numbers."""
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h, 16)


# --------------------------------------------------------------------------- #
# Region helpers
# --------------------------------------------------------------------------- #
def split_regions(ab: dict) -> dict:
    """Return the FR/CDR regions of an antibody dict (validates the expected keys are present)."""
    required = ("FR1", "CDR1", "FR2", "CDR2", "FR3", "CDR3", "FR4")
    # A human FRAMEWORK dict legitimately lacks CDRs (they come from the non-human antibody):
    if "CDR1" not in ab:
        for k in ("FR1", "FR2", "FR3", "FR4"):
            if k not in ab:
                raise ValueError(f"framework dict missing region {k!r}")
        return {k: ab.get(k, "") for k in ("FR1", "FR2", "FR3", "FR4")}
    for k in required:
        if k not in ab:
            raise ValueError(f"antibody dict missing region {k!r}")
    return {k: ab[k] for k in required}


def assemble_vh(fr1: str, cdr1: str, fr2: str, cdr2: str, fr3: str, cdr3: str, fr4: str) -> str:
    """Stitch FR1-CDR1-FR2-CDR2-FR3-CDR3-FR4 into a full VH/VL sequence."""
    return fr1 + cdr1 + fr2 + cdr2 + fr3 + cdr3 + fr4


def _count_framework_mutations(variant: "HumanizedVariant", parental: dict, human: dict) -> int:
    """Count human-framework residues that differ from the parental framework (a graft 'humanness load').

    Aligned position-by-position within each FR region up to the shorter length (teaching-grade; a real
    run uses a proper Kabat/IMGT alignment). More FR mutations => more human but more risk to the CDR
    support (Vernier zone) => more candidate back-mutations.
    """
    n = 0
    for region in ("FR1", "FR2", "FR3", "FR4"):
        p, h = parental.get(region, ""), human.get(region, "")
        for a, b in zip(p, h):
            if a != b:
                n += 1
    return n


# --------------------------------------------------------------------------- #
# CDR GRAFTING — the core humanization move (transplant non-human CDRs onto human framework).
# --------------------------------------------------------------------------- #
def graft_cdrs(nonhuman_ab: Optional[dict] = None, human_framework: Optional[dict] = None,
               scheme: str = "kabat", back_mutations: tuple = (), tool: str = "mock",
               variant_id: Optional[str] = None, **kwargs) -> HumanizedVariant:
    """Graft the non-human antibody's CDRs onto a human germline framework (CDR grafting).

    The CDRs (CDR1/CDR2/CDR3) come from `nonhuman_ab` (they confer binding and are KEPT); the four
    framework regions (FR1..FR4) come from `human_framework` (they are REPLACED to humanize). Optional
    `back_mutations` restore selected human-framework residues to the parental (non-human) residue —
    these target the Vernier zone to rescue affinity/stability (see vernier_backmutations()).

    tool="mock"        -> deterministic SYNTHETIC graft (no GPU; develop the plumbing).
    tool="ablang"      -> use AbLang to suggest/restore framework residues (humanness-aware) [real].
    tool="proteinmpnn" -> ProteinMPNN framework-position optimization, CDRs fixed [extension, real].

    Returns a HumanizedVariant (sequence + provenance). NOTE: grafting typically loses affinity/
    stability; expect to add Vernier back-mutations and to pay a ΔΔG cost (ddg_predict()).
    """
    tool = tool.lower()
    nonhuman_ab = nonhuman_ab or NONHUMAN_AB
    human_framework = human_framework or HUMAN_FRAMEWORK
    ab = split_regions(nonhuman_ab)
    fw = split_regions(human_framework)

    if tool == "mock":
        # Build the graft: human FRs + non-human CDRs. Apply any back-mutations to the FR regions.
        fr = {"FR1": fw["FR1"], "FR2": fw["FR2"], "FR3": fw["FR3"], "FR4": fw["FR4"]}
        applied = _apply_back_mutations(fr, nonhuman_ab, back_mutations)
        seq = assemble_vh(fr["FR1"], ab["CDR1"], fr["FR2"], ab["CDR2"],
                          fr["FR3"], ab["CDR3"], fr["FR4"])
        vid = variant_id or f"EXAMPLE_DATA_graft_{_hashints(scheme, back_mutations) % 10000:04d}"
        v = HumanizedVariant(
            variant_id=vid, sequence=seq, method="cdr_graft", tool="mock",
            parental=nonhuman_ab["name"], human_framework=human_framework["name"],
            scheme=scheme, back_mutations=tuple(applied),
            cdr1=ab["CDR1"], cdr2=ab["CDR2"], cdr3=ab["CDR3"],
            synthetic=True, notes=[_MOCK_FLAG],
        )
        v.n_framework_mutations = _count_framework_mutations(v, nonhuman_ab, human_framework)
        return v

    if tool == "ablang":
        # TODO (Colab, T4): use AbLang to humanness-aware restore/suggest framework residues after the
        #   CDR graft (AbLang can score residue "humanness" and propose restorations).
        #   repo: https://github.com/oxpig/AbLang  (pin a commit). Light — T4 fine.
        #   Develop with tool='mock' first.
        raise NotImplementedError(
            "Wire up AbLang here (T4). See MANUAL.md §2 and the pinned repo; develop with tool='mock' first.")
    if tool == "proteinmpnn":
        # TODO (Colab, T4): [extension] run ProteinMPNN on an Fv model with the CDR positions FIXED to
        #   redesign/optimize framework positions toward stability while staying human.
        #   repo: https://github.com/dauparas/ProteinMPNN  (pin a commit). CPU/T4 fine.
        #   Develop with tool='mock' first.
        raise NotImplementedError(
            "Wire up ProteinMPNN framework optimization here (CDRs fixed). See MANUAL.md §2; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, ablang, proteinmpnn")


def _apply_back_mutations(fr: dict, nonhuman_ab: dict, back_mutations) -> list:
    """Apply back-mutations of the form 'FR2:7' (restore the parental residue at FR2 position 7, 0-based)
    or 'FR2:V37I' (informational label) to the framework regions IN PLACE; return the labels applied.

    Teaching-grade: a 'FR<region>:<pos>' token restores fr[region][pos] to nonhuman_ab[region][pos]
    when both exist. A 'FR<region>:<from><kabat><to>' token is treated as a label only (we cannot map
    Kabat numbering without a real numbering tool) and is recorded but not applied to the string.
    """
    applied = []
    for bm in back_mutations or ():
        try:
            region, spec = str(bm).split(":", 1)
        except ValueError:
            continue
        if region not in fr:
            continue
        if spec.isdigit():
            pos = int(spec)
            src = nonhuman_ab.get(region, "")
            if 0 <= pos < len(fr[region]) and pos < len(src):
                s = list(fr[region])
                s[pos] = src[pos]
                fr[region] = "".join(s)
                applied.append(f"{region}:{pos}->{src[pos]}")
        else:
            # Kabat-style label (e.g., 'FR2:V37I') — recorded; needs a real numbering tool to apply.
            applied.append(str(bm))
    return applied


# --------------------------------------------------------------------------- #
# RESURFACING — the alternative humanization move (mutate only surface-exposed framework residues).
#   [extension] — compared head-to-head with CDR grafting in notebook 04.
# --------------------------------------------------------------------------- #
def resurface(nonhuman_ab: Optional[dict] = None, surface_positions: Optional[dict] = None,
              tool: str = "mock", variant_id: Optional[str] = None, **kwargs) -> HumanizedVariant:
    """Resurfacing (a.k.a. veneering): keep the non-human framework CORE, mutate only the SURFACE-
    exposed framework residues to their human-consensus identity. Changes fewer residues than grafting
    (lower ΔΔG risk) but achieves less humanness — the trade-off you study in notebook 04.

    `surface_positions` maps each FR region to a list of 0-based surface positions to humanize; the
    human residue is taken from HUMAN_FRAMEWORK at the same position (teaching proxy).

    tool="mock" -> deterministic SYNTHETIC resurfaced variant. Real path = compute solvent exposure on
    an Fv model (IgFold/ImmuneBuilder) and substitute exposed FR residues to human consensus (TODO).
    """
    tool = tool.lower()
    nonhuman_ab = nonhuman_ab or NONHUMAN_AB
    ab = split_regions(nonhuman_ab)
    surface_positions = surface_positions or {"FR1": [2], "FR2": [0, 1], "FR3": [0, 1], "FR4": []}

    if tool == "mock":
        fr = {"FR1": ab["FR1"], "FR2": ab["FR2"], "FR3": ab["FR3"], "FR4": ab["FR4"]}
        changed = []
        for region, positions in surface_positions.items():
            human_src = HUMAN_FRAMEWORK.get(region, "")
            s = list(fr[region])
            for pos in positions:
                if 0 <= pos < len(s) and pos < len(human_src) and s[pos] != human_src[pos]:
                    changed.append(f"{region}:{pos}{s[pos]}->{human_src[pos]}")
                    s[pos] = human_src[pos]
            fr[region] = "".join(s)
        seq = assemble_vh(fr["FR1"], ab["CDR1"], fr["FR2"], ab["CDR2"],
                          fr["FR3"], ab["CDR3"], fr["FR4"])
        vid = variant_id or f"EXAMPLE_DATA_resurface_{_hashints(tuple(changed)) % 10000:04d}"
        v = HumanizedVariant(
            variant_id=vid, sequence=seq, method="resurface", tool="mock",
            parental=nonhuman_ab["name"], human_framework="resurfaced(parental_core)",
            back_mutations=tuple(changed), cdr1=ab["CDR1"], cdr2=ab["CDR2"], cdr3=ab["CDR3"],
            synthetic=True, notes=[_MOCK_FLAG, "resurfacing: surface FR residues only"],
        )
        v.n_framework_mutations = len(changed)
        return v
    # TODO (Colab, T4): real resurfacing — compute per-residue solvent accessibility on an IgFold/
    #   ImmuneBuilder Fv model; humanize only the EXPOSED framework residues. See MANUAL.md §2.
    raise NotImplementedError(
        "Wire up real resurfacing (solvent-exposure-driven) here. See MANUAL.md §2; "
        "develop with tool='mock' first.")


# --------------------------------------------------------------------------- #
# HUMANNESS SCORING.
#   WARNING: this is a TEACHING HEURISTIC, NOT the validated tools it imitates.
#   - Real OASis (Prihoda 2022, BioPhi) scores 9-mer peptides against the Observed Antibody Space.
#   - Real Hu-mAb (Marks 2021) is a germline-content ML classifier.
#   - Real T20 (Gao 2013) scores against a curated human-antibody database via a web server.
#   - AbLang (Olsen 2022) is an antibody language model (per-residue humanness + restoration).
#   Use the function below ONLY to develop the pipeline and to teach what humanness MEASURES; swap in
#   the real tools (documented as TODOs) before drawing any immunogenicity / humanness conclusion.
# --------------------------------------------------------------------------- #
def humanness_score(seq: str, tool: str = "mock") -> dict:
    """TEACHING-HEURISTIC humanness proxies (NOT validated tools). Deterministic, no GPU.

    Returns {oasis_like, t20_like, germline_id}:
      - oasis_like : fraction of overlapping 9-mers that match the human-framework reference set, in
                     [0,1] (higher = more human). A toy OASis-LIKE peptide-identity proxy; real OASis
                     scores 9-mers against the Observed Antibody Space (OAS) human repertoires.
      - t20_like   : a 0–100 rescaling of the same signal (higher = more human). A toy T20-LIKE score;
                     real T20 scores against a curated human-antibody database (Gao 2013).
      - germline_id: nearest human-germline label by FR-region identity (teaching proxy), e.g.
                     'IGHV3-like'. Real germline assignment uses IMGT/V-QUEST or ANARCI.
    Every value is a heuristic for TEACHING the axis — never report it as a humanness / immunogenicity
    verdict. Swap in OASis / Hu-mAb / T20 / AbLang (TODOs) for any reportable claim.
    """
    tool = tool.lower()
    s = (seq or "").upper()
    if not s or any(c not in _AA for c in s):
        return dict(oasis_like=None, t20_like=None, germline_id=None,
                    error="invalid amino-acid sequence")
    if tool != "mock":
        # TODO (Colab, T4): wire up the REAL humanness backend you choose and PIN it:
        #   - OASis / Hu-mAb via BioPhi (https://github.com/Merck/BioPhi) — VERIFY current host/release;
        #   - T20 humanness server (Gao 2013) — VERIFY it is still public;
        #   - AbLang (https://github.com/oxpig/AbLang) for per-residue humanness + restoration.
        #   Report the real score; the heuristic below is for plumbing only.
        raise NotImplementedError(
            "Wire up the real humanness backend (OASis/Hu-mAb/T20/AbLang) and pin it. "
            "See MANUAL.md §2; develop with tool='mock' first.")

    # --- oasis_like: 9-mer identity against the human-framework reference (higher = more human) ----
    human_ref = (HUMAN_FRAMEWORK["FR1"] + HUMAN_FRAMEWORK["FR2"] +
                 HUMAN_FRAMEWORK["FR3"] + HUMAN_FRAMEWORK["FR4"])
    ref_9mers = {human_ref[i:i + 9] for i in range(max(0, len(human_ref) - 8))}
    s_9mers = [s[i:i + 9] for i in range(max(0, len(s) - 8))]
    if not s_9mers:
        oasis_like = 0.0
    else:
        # Per-9-mer best identity fraction vs the reference set (a soft match — teaching proxy).
        def best_identity(kmer: str) -> float:
            best = 0
            for r in ref_9mers:
                ident = sum(1 for a, b in zip(kmer, r) if a == b)
                if ident > best:
                    best = ident
            return best / 9.0
        oasis_like = round(sum(best_identity(k) for k in s_9mers) / len(s_9mers), 3)
    oasis_like = max(0.0, min(1.0, oasis_like))

    # --- t20_like: 0–100 rescale of the same signal (teaching proxy) ------------------------------
    t20_like = round(100.0 * oasis_like, 1)

    # --- germline_id: crude nearest-germline label by FR identity (teaching proxy) ----------------
    # If FR1 looks like the human reference FR1, call it IGHV3-like; else murine-like. Toy proxy only.
    fr1_window = s[:len(HUMAN_FRAMEWORK["FR1"])]
    fr1_ident = sum(1 for a, b in zip(fr1_window, HUMAN_FRAMEWORK["FR1"]) if a == b)
    germline_id = "IGHV3-like(human)" if fr1_ident >= 0.7 * len(HUMAN_FRAMEWORK["FR1"]) else "murine-like"

    return dict(oasis_like=oasis_like, t20_like=t20_like, germline_id=germline_id)


# --------------------------------------------------------------------------- #
# ΔΔG STABILITY PROXY.
#   WARNING: this is a TEACHING HEURISTIC, NOT FoldX or Rosetta.
#   - Real ΔΔG needs a 3-D Fv model (IgFold / ImmuneBuilder) + FoldX (BuildModel/PositionScan) or
#     Rosetta (cartesian_ddg). Those compute the free-energy change of each framework mutation.
#   - The proxy below scores mutations by a coarse amino-acid-substitution penalty so the pipeline
#     runs with no structure and no GPU. Swap in FoldX/Rosetta (TODO) for any reportable ΔΔG.
# --------------------------------------------------------------------------- #
# Coarse per-residue "burial/structure" weights (teaching proxy): hydrophobic/structural residues cost
# more to swap. NOT a force field — a stand-in so the trade-off has structure.
_SUBST_WEIGHT = {"A": 0.5, "R": 1.0, "N": 0.8, "D": 0.9, "C": 1.5, "Q": 0.8, "E": 0.9,
                 "G": 1.2, "H": 1.0, "I": 1.3, "L": 1.3, "K": 1.0, "M": 1.1, "F": 1.4,
                 "P": 1.6, "S": 0.6, "T": 0.7, "W": 1.6, "Y": 1.3, "V": 1.2}


def ddg_predict(parental_seq: str, variant_seq: str, tool: str = "mock") -> dict:
    """TEACHING-HEURISTIC ΔΔG proxy for (variant vs parental). Deterministic, no GPU.

    Returns {ddg_kcal_mol, n_mutations, per_mut}:
      - ddg_kcal_mol : SUM over differing aligned positions of a coarse substitution penalty, signed so
                       that MORE / structurally-costlier framework changes => MORE POSITIVE (more
                       destabilizing). A stand-in for FoldX/Rosetta ΔΔG (units are NOT real kcal/mol).
      - n_mutations  : number of differing aligned positions (parental vs variant).
      - per_mut      : list of (position, parental_aa, variant_aa, penalty).
    Convention: ΔΔG > 0 == destabilizing (the usual FoldX/Rosetta sign). Grafting many framework
    residues raises ΔΔG; Vernier back-mutations should LOWER it. NEVER report this proxy as a real ΔΔG —
    swap in FoldX/Rosetta on an IgFold/ImmuneBuilder model (TODO).
    """
    tool = tool.lower()
    p = (parental_seq or "").upper()
    v = (variant_seq or "").upper()
    if not p or not v or any(c not in _AA for c in p + v):
        return dict(ddg_kcal_mol=None, n_mutations=None, per_mut=[],
                    error="invalid amino-acid sequence")
    if tool != "mock":
        # TODO (Colab, T4): wire up the REAL ΔΔG backend and PIN it:
        #   1) model the Fv with IgFold / ImmuneBuilder (https://github.com/oxpig/ImmuneBuilder);
        #   2) run FoldX (BuildModel/PositionScan) or Rosetta (cartesian_ddg) on each framework
        #      mutation; sum to a ΔΔG. Report real kcal/mol; the proxy below is plumbing only.
        raise NotImplementedError(
            "Wire up FoldX/Rosetta ΔΔG on an IgFold/ImmuneBuilder model and pin it. "
            "See MANUAL.md §2; develop with tool='mock' first.")

    per_mut = []
    total = 0.0
    for i, (a, b) in enumerate(zip(p, v)):
        if a != b:
            # Penalty = average structural weight of the two residues (teaching proxy).
            pen = round((_SUBST_WEIGHT[a] + _SUBST_WEIGHT[b]) / 2.0, 3)
            per_mut.append((i, a, b, pen))
            total += pen
    return dict(ddg_kcal_mol=round(total, 3), n_mutations=len(per_mut), per_mut=per_mut,
                synthetic=True, note=_MOCK_FLAG)


# --------------------------------------------------------------------------- #
# VERNIER-ZONE BACK-MUTATION SUGGESTIONS.
#   The classic affinity/stability rescue: where the graft replaced a Vernier-zone residue (a framework
#   residue that supports the CDR loops), suggest RESTORING the parental (non-human) residue. Each
#   restoration trades a little humanness for (usually) a lot of regained stability/affinity.
# --------------------------------------------------------------------------- #
def vernier_backmutations(grafted: "HumanizedVariant", parental: Optional[dict] = None,
                          human: Optional[dict] = None) -> list:
    """Suggest Vernier-zone back-mutations for a grafted variant (restore parental residues at
    framework positions that support the CDRs and were changed by the graft).

    Returns a list of dicts: {region, pos, human_aa, parental_aa, token} where `token` is a
    back-mutation token ('FR2:7') you can feed back into graft_cdrs(back_mutations=...) to rebuild the
    variant WITH the restoration applied. Only positions in VERNIER_ZONE that actually differ between
    the human framework and the parental are suggested (those are the ones the graft changed).

    Teaching-grade: VERNIER_ZONE uses per-region 0-based positions approximating the canonical Vernier
    set (Foote & Winter 1992). For a real run, map true Kabat/IMGT Vernier positions onto your aligned
    sequences (ANARCI) before suggesting restorations.
    """
    parental = parental or NONHUMAN_AB
    human = human or HUMAN_FRAMEWORK
    suggestions = []
    for region, positions in VERNIER_ZONE.items():
        h = human.get(region, "")
        p = parental.get(region, "")
        for pos in positions:
            if 0 <= pos < len(h) and pos < len(p) and h[pos] != p[pos]:
                suggestions.append(dict(
                    region=region, pos=pos, human_aa=h[pos], parental_aa=p[pos],
                    token=f"{region}:{pos}",
                    rationale=f"Vernier position {region}[{pos}] changed by graft "
                              f"({p[pos]}->{h[pos]}); restoring {p[pos]} may rescue affinity/stability.",
                ))
    return suggestions


# --------------------------------------------------------------------------- #
# Batch scorer: fill humanness + ΔΔG fields for a list of variants (vs a parental sequence).
# --------------------------------------------------------------------------- #
def score_variants(variants: list, parental_seq: str, tool: str = "mock") -> list:
    """Run humanness_score() + ddg_predict() over a list of HumanizedVariant; fill fields in place.

    `parental_seq` is the full non-human VH sequence (the ΔΔG reference + the stability baseline).
    On mock, all numbers are SYNTHETIC.
    """
    for v in variants:
        hm = humanness_score(v.sequence, tool=tool)
        if hm.get("error"):
            v.notes.append(f"humanness_score failed: {hm['error']}")
        else:
            v.oasis_like = hm["oasis_like"]
            v.t20_like = hm["t20_like"]
            v.germline_id = hm["germline_id"]
        dd = ddg_predict(parental_seq, v.sequence, tool=tool)
        if dd.get("error"):
            v.notes.append(f"ddg_predict failed: {dd['error']}")
        else:
            v.ddg_kcal_mol = dd["ddg_kcal_mol"]
            if dd.get("synthetic"):
                v.synthetic = True
    return variants


def parental_sequence(ab: Optional[dict] = None) -> str:
    """Assemble the full parental (non-human) VH sequence — the ΔΔG / humanness baseline."""
    ab = ab or NONHUMAN_AB
    r = split_regions(ab)
    return assemble_vh(r["FR1"], r["CDR1"], r["FR2"], r["CDR2"], r["FR3"], r["CDR3"], r["FR4"])


if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps). All numbers are SYNTHETIC.
    parent = parental_sequence(NONHUMAN_AB)
    print("parental (non-human) VH length:", len(parent), "aa")

    # 1) CDR graft (no back-mutations yet).
    graft = graft_cdrs(NONHUMAN_AB, HUMAN_FRAMEWORK, tool="mock")
    # 2) the Vernier back-mutations the graft suggests.
    bms = vernier_backmutations(graft, NONHUMAN_AB, HUMAN_FRAMEWORK)
    tokens = tuple(b["token"] for b in bms)
    # 3) re-graft WITH the back-mutations applied (the affinity/stability rescue).
    graft_bm = graft_cdrs(NONHUMAN_AB, HUMAN_FRAMEWORK, back_mutations=tokens, tool="mock")
    # 4) resurfacing alternative [extension].
    veneer = resurface(NONHUMAN_AB, tool="mock")
    # 5) an over-humanized DECOY control: graft + over-humanize by also restoring nothing AND
    #    using a hyper-human label (here just the plain graft, flagged as the decoy in the notebooks).

    variants = [graft, graft_bm, veneer]
    score_variants(variants, parent, tool="mock")

    print(f"\nVernier back-mutation suggestions ({len(bms)}):")
    for b in bms:
        print("  ", b["token"], b["rationale"])

    for v in variants:
        print(f"\n[{v.method}] {v.variant_id}  (back_mutations={v.back_mutations})")
        print("   len=", len(v.sequence), " FR-mutations=", v.n_framework_mutations)
        print("   humanness: OASis-like", v.oasis_like, "| T20-like", v.t20_like,
              "| germline", v.germline_id, " (TEACHING HEURISTICS — not validated tools)")
        print("   ddg_proxy:", v.ddg_kcal_mol, "(>0 = destabilizing; NOT real kcal/mol)",
              "synthetic=", v.synthetic)
    print("\nThe trade-off: more humanness usually means more framework mutations means higher ΔΔG;")
    print("Vernier back-mutations should LOWER ΔΔG at a small humanness cost.")
    print("REMINDER: every number above is SYNTHETIC (mock) — never report it as a real result.")
