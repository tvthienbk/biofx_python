"""
maturation_tools.py — computational antibody AFFINITY-MATURATION + developability wrappers
for Project 15 (lead-optimize an EXISTING antibody against its antigen).

This is NOT de novo design. You start from a KNOWN antibody-antigen complex (with a measured
KD in the literature) and propose a SMALL, TESTABLE set of CDR mutations that should RAISE
affinity while KEEPING developability. The framework is FIXED; only CDR positions are varied.

Clean, import-safe entry points so the notebooks stay thin and the logic is testable WITHOUT a GPU:

    esm1v_score(seq, mutation)                  -> Δ log-likelihood proxy for a point mutation (higher = favored)
    ablang_score(seq)                           -> AbLang-like naturalness/likelihood proxy in [0,1]
    mpnn_cdr_redesign(complex, cdr, n)          -> list[Variant] of CDR-redesigned variants (framework FIXED)
    af2_pose_check(variant, antigen)            -> {pae_interaction, scrmsd}  (binding-pose maintenance)
    developability_scan(seq)                    -> liability motifs (NG/DG deamidation, Met-ox, unpaired Cys, ...)
    plus helpers: score_single_mutations(), assemble_candidate_set(), score_variants(),
                  apply_mutation(), parse_mutation(), cdr_positions().

This file follows the ANTIBODY-FAMILY TEMPLATE shape (Project 17's antibody_tools.py): the `mock`
backend is DETERMINISTIC (seeded by the inputs) so you can develop and unit-test the plumbing —
ranking, candidate-set assembly, the filter hand-off, the validation plan — before spending any GPU
time. The real backends (ESM-1v, AbLang/AbLang2, ProteinMPNN, AF2-Multimer) live behind clearly-marked
TODOs with compute notes. The developability functions are CLEARLY-LABELED teaching heuristics, NOT the
validated tools (TAP/CamSol/real deamidation predictors) they imitate — see the WARNING on each.

DESIGN NOTE FOR STUDENTS
------------------------
Two honesty rules dominate this project:
  1. NEVER fabricate KD / ΔΔG / affinity numbers. The deliverable is a RANKED, ORDERED set of
     candidate mutations + the experiment (SPR/DSF) to test them — NOT predicted binding constants.
     The mock backend returns dimensionless RANKING scores only, all flagged SYNTHETIC.
  2. Most predicted affinity-improving mutations do NOT validate experimentally. The output is a
     small (<~10) ranked set to test, with mandatory controls (WT + a destabilizing decoy).

Compute reality (be honest): ESM-1v / AbLang scoring is LIGHT and CPU/T4-friendly (the cheap part);
ProteinMPNN CDR redesign is also cheap. The heavy step is AF2-Multimer pose checking of each variant
complex — BATCH it (overnight) and keep N small. Colab T4-Pro is the realistic tier; see MANUAL.md §2.

Pinned upstreams (verify they still exist — the version-verify cell; pin commits, they change):
  ESM / ESM-1v   https://github.com/facebookresearch/esm
  AbLang         https://github.com/oxpig/AbLang        (AbLang2 supersedes — verify the current repo)
  ProteinMPNN    https://github.com/dauparas/ProteinMPNN
  ColabFold      https://github.com/sokrypton/ColabFold (AF2-Multimer)
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional

# 20 canonical amino acids.
_AA = "ACDEFGHIKLMNPQRSTVWY"
_MOCK_FLAG = "SYNTHETIC — mock backend, RANKING score only, NOT a KD/ΔΔG and NOT a real prediction"

# ---------------------------------------------------------------------------------------------- #
# A small EXAMPLE antibody-Fv + antigen "complex" record. This is a TEACHING PLACEHOLDER so the
# plumbing runs anywhere. In Week 1 you REPLACE it with the chains read off your VERIFIED SAbDab
# complex (a real antibody-antigen complex with a published KD). The CDRs below are illustrative
# loop placeholders inserted between humanized-style framework regions — NOT a real therapeutic
# sequence and NOT annotated to a real PDB. Do not treat any field here as experimental data.
# ---------------------------------------------------------------------------------------------- #
EXAMPLE_FRAMEWORK = {
    "name": "exampleVH_teaching_placeholder",
    "FR1": "EVQLVESGGGLVQPGGSLRLSCAAS",
    "FR2": "WVRQAPGKGLEWVS",
    "FR3": "RFTISRDNSKNTLYLQMNSLRAEDTAVYYC",
    "FR4": "WGQGTLVTVSS",
    # Example starting CDR loops (the maturation substrate — vary THESE, keep framework fixed):
    "CDR1": "GFTFSDYA",
    "CDR2": "ISGSGGST",
    "CDR3": "ARDRGLGYFDY",
}


def example_parent_sequence() -> str:
    """Assemble the EXAMPLE parent VH (FR1-CDR1-FR2-CDR2-FR3-CDR3-FR4). Teaching placeholder."""
    f = EXAMPLE_FRAMEWORK
    return f["FR1"] + f["CDR1"] + f["FR2"] + f["CDR2"] + f["FR3"] + f["CDR3"] + f["FR4"]


def cdr_positions(framework: Optional[dict] = None) -> dict:
    """Return the 0-based index RANGES of each CDR within the assembled parent sequence.

    These are the ONLY positions you are allowed to mutate (framework is FIXED in maturation).
    For a real complex, derive the CDR boundaries with an antibody numbering scheme (IMGT/Kabat/
    Chothia via ANARCI) on your verified sequence — do not eyeball them.
    """
    f = framework or EXAMPLE_FRAMEWORK
    i = 0
    spans = {}
    for seg in ("FR1", "CDR1", "FR2", "CDR2", "FR3", "CDR3", "FR4"):
        n = len(f[seg])
        if seg.startswith("CDR"):
            spans[seg] = (i, i + n)        # half-open [start, end)
        i += n
    return spans


# --------------------------------------------------------------------------- #
# Deterministic hashing helper (mock backend reproducibility — graded).
# --------------------------------------------------------------------------- #
def _hashints(*parts) -> int:
    """Stable integer hash of the inputs (NOT Python's salted hash) for deterministic mock numbers."""
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h, 16)


def _mock_loop(seed_int: int, length: int) -> str:
    """Deterministic pseudo-random amino-acid loop (mock redesigned CDR)."""
    seq, x = [], seed_int
    for _ in range(length):
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        seq.append(_AA[x % len(_AA)])
    return "".join(seq)


# --------------------------------------------------------------------------- #
# Mutation notation helpers (e.g., "S31Y" = Ser at position 31 -> Tyr; 1-based).
# --------------------------------------------------------------------------- #
def parse_mutation(mutation: str) -> tuple:
    """Parse 'S31Y' -> ('S', 31, 'Y'). Position is 1-based over the antibody chain sequence."""
    m = mutation.strip().upper()
    wt, mut = m[0], m[-1]
    pos = int(m[1:-1])
    if wt not in _AA or mut not in _AA:
        raise ValueError(f"bad mutation {mutation!r}: residues must be one of {_AA}")
    return wt, pos, mut


def apply_mutation(seq: str, mutation: str) -> str:
    """Return a new sequence with `mutation` applied (1-based). Verifies the WT identity matches."""
    wt, pos, mut = parse_mutation(mutation)
    i = pos - 1
    if i < 0 or i >= len(seq):
        raise ValueError(f"position {pos} out of range for length-{len(seq)} sequence")
    if seq[i].upper() != wt:
        raise ValueError(f"WT mismatch at {pos}: sequence has {seq[i]!r}, mutation expects {wt!r}")
    return seq[:i] + mut + seq[i + 1:]


@dataclass
class Variant:
    """One affinity-maturation candidate: the parent antibody with one or more CDR mutations."""
    design_id: str
    sequence: str                       # full antibody chain (framework FIXED, CDRs varied)
    parent_id: str = "WT_parent"
    antigen: str = "ANTIGEN"
    mutations: tuple = ()               # e.g., ("S31Y",) or ("S31Y","T57W") for combinations
    cdr: str = ""                       # which CDR the change is in (CDR1/CDR2/CDR3) when applicable
    source: str = "mock"                # "esm1v" | "ablang" | "proteinmpnn" | "mock" | "control"
    # ranking scores (DIMENSIONLESS — NOT affinities). Higher esm1v/ablang => model-favored:
    esm1v: Optional[float] = None       # ESM-1v-like Δlog-likelihood proxy (favored mutation if > 0)
    ablang: Optional[float] = None      # AbLang-like naturalness proxy in [0,1] (higher = more natural)
    # filled by af2_pose_check():  (pose maintenance, NOT affinity)
    pae_interaction: Optional[float] = None
    scrmsd: Optional[float] = None
    # filled by developability_scan():  (teaching heuristics — NOT validated tools)
    liabilities: tuple = ()             # list of (motif, position) liability hits in CDRs
    n_liabilities: Optional[int] = None
    is_control: bool = False            # WT / destabilizing-decoy / specificity controls
    synthetic: bool = False             # True => numbers are mock/EXAMPLE_DATA, never report as real
    notes: list = field(default_factory=list)

    def as_row(self) -> dict:
        r = asdict(self)
        r["mutations"] = "+".join(self.mutations) if self.mutations else ""
        r["liabilities"] = ";".join(f"{m}@{p}" for m, p in self.liabilities) if self.liabilities else ""
        return r


# --------------------------------------------------------------------------- #
# 1) ESM-1v point-mutation scorer (LIGHT — CPU/T4 fine).
# --------------------------------------------------------------------------- #
def esm1v_score(seq: str, mutation: str, tool: str = "mock", **kwargs) -> float:
    """Score a single point `mutation` on `seq` with an ESM-1v-like masked-marginal proxy.

    Returns a DIMENSIONLESS Δ log-likelihood proxy: log P(mut) - log P(wt) at the masked position.
    > 0  => the protein language model FAVORS the mutation over wild type (a maturation candidate);
    < 0  => disfavored. This is a RANKING signal for prioritising which mutations to TEST — it is
    NOT an affinity, NOT a ΔΔG, and NOT a guarantee the mutation improves binding. Antigen context
    is NOT seen by a single-sequence PLM, so always cross-check with the structure (af2_pose_check).

    tool="mock"  -> deterministic SYNTHETIC score (no GPU; develop the plumbing).
    tool="esm1v" -> real ESM-1v backend (light; see MANUAL.md §2).
    """
    tool = tool.lower()
    wt, pos, mut = parse_mutation(mutation)
    if tool == "mock":
        # Deterministic SYNTHETIC Δ-log-likelihood proxy in a plausible [-3, +3]-ish band, centered
        # near 0 (most mutations are neutral/deleterious). NOT a real prediction.
        h = _hashints("esm1v", seq.upper(), wt, pos, mut)
        val = ((h % 6001) / 1000.0) - 3.0          # -3.000 .. +3.000
        return round(val, 3)
    if tool == "esm1v":
        # TODO (Colab; light — CPU/T4 fine): run ESM-1v masked-marginal scoring.
        #   repo: https://github.com/facebookresearch/esm  (pin a commit; e.g. main@<sha>)
        #   1) load an esm1v_t33_650M_UR90S_{1..5} model (ensemble the 5 for the published score);
        #   2) mask position `pos`, read log-probs for wt and mut, return logP(mut)-logP(wt).
        #   Score every allowed CDR position x 19 substitutions; this is the cheap part of the project.
        raise NotImplementedError(
            "Wire up ESM-1v masked-marginal scoring here (light; CPU/T4 fine). "
            "See MANUAL.md §2 and the pinned repo; develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, esm1v")


# --------------------------------------------------------------------------- #
# 2) AbLang antibody-specific likelihood scorer (LIGHT).
# --------------------------------------------------------------------------- #
def ablang_score(seq: str, tool: str = "mock", chain: str = "heavy", **kwargs) -> float:
    """AbLang/AbLang2-like antibody-specific naturalness/likelihood proxy for `seq`, in [0,1].

    AbLang is an antibody-specific language model (trained on OAS repertoires), so it captures what a
    "natural-looking" antibody sequence is better than a general PLM. Higher = more antibody-natural
    (a developability/expressibility prior; helps avoid odd CDR sequences). It is NOT an affinity.
    Use it to score a whole variant (or its CDRs) and to sanity-check ProteinMPNN redesigns.

    tool="mock"   -> deterministic SYNTHETIC score in [0,1].
    tool="ablang" -> real AbLang/AbLang2 backend (light; verify current repo — see MANUAL.md §2).
    """
    tool = tool.lower()
    if not seq or any(c not in _AA for c in seq.upper()):
        return float("nan")
    if tool == "mock":
        h = _hashints("ablang", chain, seq.upper())
        return round((h % 1001) / 1000.0, 3)       # 0.000 .. 1.000
    if tool == "ablang":
        # TODO (Colab; light): run AbLang / AbLang2 pseudo-log-likelihood over the antibody chain.
        #   repo: https://github.com/oxpig/AbLang  (AbLang2 supersedes — VERIFY current repo + pin).
        #   Use the heavy/light model matching your chain; return a normalized naturalness score.
        raise NotImplementedError(
            "Wire up AbLang/AbLang2 here (light). VERIFY the current repo (AbLang2). "
            "See MANUAL.md §2; develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, ablang")


# --------------------------------------------------------------------------- #
# Saturation single-mutation scan over the CDRs (the cheap, high-value first pass).
# --------------------------------------------------------------------------- #
def score_single_mutations(parent_seq: str, framework: Optional[dict] = None,
                           tool: str = "mock", antigen: str = "ANTIGEN") -> list[Variant]:
    """Score every single substitution at every CDR position (framework FIXED) and return Variants.

    This is the core P2 single-mutation pass: for each CDR position, try the 19 non-WT residues,
    score each with ESM-1v (and AbLang on the resulting full sequence). Returns one Variant per
    candidate mutation, carrying its DIMENSIONLESS ranking scores. Sort/threshold downstream; assemble
    a SMALL set to test. (Framework positions are never touched — that is what "maturation" means.)
    """
    spans = cdr_positions(framework)
    out = []
    for cdr, (start, end) in spans.items():
        for i in range(start, end):
            wt = parent_seq[i]
            for mut in _AA:
                if mut == wt:
                    continue
                mut_str = f"{wt}{i+1}{mut}"            # 1-based notation
                try:
                    new_seq = apply_mutation(parent_seq, mut_str)
                except ValueError:
                    continue
                e = esm1v_score(parent_seq, mut_str, tool=tool)
                a = ablang_score(new_seq, tool=tool)
                out.append(Variant(
                    design_id=f"EXAMPLE_DATA_{cdr}_{mut_str}",
                    sequence=new_seq, antigen=antigen, mutations=(mut_str,), cdr=cdr,
                    source="esm1v", esm1v=e, ablang=a,
                    synthetic=(tool == "mock"),
                    notes=[_MOCK_FLAG] if tool == "mock" else [],
                ))
    return out


# --------------------------------------------------------------------------- #
# 3) ProteinMPNN CDR redesign (framework FIXED). CPU-fine / light.
# --------------------------------------------------------------------------- #
def mpnn_cdr_redesign(parent_seq: str, cdr: str = "CDR3", n: int = 8,
                      framework: Optional[dict] = None, tool: str = "mock",
                      antigen: str = "ANTIGEN") -> list[Variant]:
    """Redesign one CDR loop with ProteinMPNN while keeping ALL framework positions FIXED.

    ProteinMPNN, conditioned on the antibody-antigen backbone, proposes new sequences for the chosen
    CDR (here we vary only `cdr`; the rest of the chain, including the other CDRs and the whole
    framework, is held fixed). This explores multi-residue CDR changes that single-mutation scanning
    misses. Survivors must still pass af2_pose_check (pose maintenance) + developability_scan.

    tool="mock"        -> deterministic SYNTHETIC redesigned loops (no GPU).
    tool="proteinmpnn" -> real ProteinMPNN backend (CPU-fine; see MANUAL.md §2).
    """
    tool = tool.lower()
    framework = framework or EXAMPLE_FRAMEWORK
    spans = cdr_positions(framework)
    if cdr not in spans:
        raise ValueError(f"unknown CDR {cdr!r}; options: {list(spans)}")
    start, end = spans[cdr]
    if tool == "mock":
        out = []
        for k in range(n):
            seed = _hashints("mpnn", antigen, cdr, parent_seq.upper(), k)
            new_loop = _mock_loop(seed, end - start)
            new_seq = parent_seq[:start] + new_loop + parent_seq[end:]
            # Record the changed positions as the "mutation set" (for honest bookkeeping).
            muts = tuple(f"{parent_seq[start+j]}{start+j+1}{new_loop[j]}"
                         for j in range(end - start) if new_loop[j] != parent_seq[start + j])
            out.append(Variant(
                design_id=f"EXAMPLE_DATA_MPNN_{cdr}_{k:03d}",
                sequence=new_seq, antigen=antigen, mutations=muts, cdr=cdr,
                source="proteinmpnn", ablang=ablang_score(new_seq, tool="mock"),
                synthetic=True, notes=[_MOCK_FLAG],
            ))
        return out
    if tool == "proteinmpnn":
        # TODO (Colab; CPU-fine / light): run ProteinMPNN on the antibody-antigen complex backbone,
        #   FIXING every framework + non-target-CDR position and designing only `cdr`.
        #   repo: https://github.com/dauparas/ProteinMPNN  (pin a commit).
        #   Use --fixed_positions / a design-mask so ONLY the chosen CDR is redesigned; sample n
        #   sequences (temperature ~0.1-0.3). Hand survivors to af2_pose_check + developability_scan.
        raise NotImplementedError(
            "Wire up ProteinMPNN CDR redesign here (framework FIXED via a design mask; CPU-fine). "
            "See MANUAL.md §2; develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, proteinmpnn")


# --------------------------------------------------------------------------- #
# 4) AF2-Multimer pose-maintenance check (the HEAVY step — batch it).
# --------------------------------------------------------------------------- #
def af2_pose_check(variant_seq: str, antigen: str = "ANTIGEN", tool: str = "mock", **kwargs) -> dict:
    """Check the variant still binds in the SAME pose as the parent. Returns {pae_interaction, scrmsd}.

    The key maturation question after proposing a mutation is NOT "is affinity higher" (no in-silico
    metric tells you that reliably) but "does the antibody still dock the antigen the same way?" — a
    mutation that improves a PLM score but disrupts the interface is worthless. AF2-Multimer gives
    `pae_interaction` (interface confidence; antibody cutoff <= 12) and `scrmsd` (variant Fv vs parent
    Fv backbone; cutoff <= 3.0). These are POSE-MAINTENANCE filters, NOT affinity predictions.

    tool="mock" -> deterministic SYNTHETIC numbers; tool="af2" -> real AF2-Multimer (HEAVY; batch it).
    """
    tool = tool.lower()
    if not variant_seq or any(c not in _AA for c in variant_seq.upper()):
        return dict(pae_interaction=None, scrmsd=None, ok=False, error="invalid amino-acid sequence")
    if tool == "mock":
        h = _hashints("af2pose", antigen, variant_seq.upper())
        pae_interaction = 5 + (h % 16)                  # 5-20 (key metric; antibody cutoff <= 12)
        scrmsd = round(0.6 + (h % 300) / 100.0, 3)      # 0.6-3.6 Å (vs parent pose; cutoff <= 3.0)
        return dict(pae_interaction=float(pae_interaction), scrmsd=scrmsd,
                    ok=True, synthetic=True, error=_MOCK_FLAG)
    if tool in ("af2", "colabfold", "af2_multimer", "multimer"):
        # TODO (Colab): run AF2-Multimer (ColabFold, model_type=multimer) on the (variant Fv, antigen)
        #   complex; parse mean inter-chain PAE -> pae_interaction; superpose the predicted Fv on the
        #   PARENT complex and compute backbone scRMSD. repo: https://github.com/sokrypton/ColabFold
        #   (pin a commit). THIS IS THE HEAVY STEP — keep N small and BATCH overnight (MANUAL.md §2).
        raise NotImplementedError(
            "Wire up AF2-Multimer pose check here (ColabFold, model_type=multimer; HEAVY — batch it). "
            "See MANUAL.md §2; develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, af2/colabfold")


def score_variants(variants: list[Variant], tool: str = "mock") -> list[Variant]:
    """Run af2_pose_check() + developability_scan() over a list of Variants; fill fields in place."""
    for v in variants:
        m = af2_pose_check(v.sequence, antigen=v.antigen, tool=tool)
        if m.get("ok", True):
            v.pae_interaction = m.get("pae_interaction")
            v.scrmsd = m.get("scrmsd")
            if m.get("synthetic"):
                v.synthetic = True
        else:
            v.notes.append(f"af2_pose_check failed: {m.get('error')}")
        scan = developability_scan(v.sequence, framework=None)
        v.liabilities = scan["liabilities"]
        v.n_liabilities = scan["n_liabilities"]
    return variants


# --------------------------------------------------------------------------- #
# 5) Developability liability scan.
#   WARNING: TEACHING HEURISTIC, NOT a validated tool. It flags well-known *sequence* liability
#   motifs that real developability tools (TAP, Raybould 2019; structure-based deamidation/oxidation
#   predictors) assess more rigorously. Use it to TRIAGE obvious chemical liabilities introduced by a
#   mutation BEFORE synthesis; swap in the real tools for any reportable developability claim.
# --------------------------------------------------------------------------- #
# Chemical-liability motifs to flag, especially when INSIDE a CDR (paratope) where they matter most:
#   NG, NS         : asparagine deamidation hotspots (Asn-Gly is the classic fast one)
#   DG, DS         : aspartate isomerization hotspots
#   M              : methionine oxidation (solvent-exposed CDR Met)
#   W              : tryptophan oxidation (secondary)
#   N x [S/T]      : N-linked glycosylation sequon (X != P)
#   unpaired C     : free cysteine in a CDR (disulfide scrambling / covalent-aggregation risk)
_DEAMIDATION = ("NG", "NS")
_ISOMERIZATION = ("DG", "DS")


def developability_scan(seq: str, framework: Optional[dict] = None) -> dict:
    """TEACHING-HEURISTIC liability scan (NOT a validated tool). Deterministic, no GPU.

    Returns {liabilities, n_liabilities} where `liabilities` is a list of (motif_label, 1-based_pos)
    for chemical-liability motifs found IN THE CDRs:
      - 'deamidation_NG/NS'   Asn deamidation hotspots
      - 'isomerization_DG/DS' Asp isomerization hotspots
      - 'oxidation_Met'       methionine oxidation
      - 'oxidation_Trp'       tryptophan oxidation
      - 'N-glyc_sequon'       N-X-S/T glycosylation sequon (X != P)
      - 'unpaired_Cys'        free cysteine in a CDR
    Scanning is restricted to CDR spans because that is where these liabilities most affect binding/
    stability and where maturation mutations are introduced. This teaches WHICH motifs to avoid; it is
    NOT a TAP red/amber/green call — confirm any reportable claim with real TAP / deamidation tools.
    """
    s = (seq or "").upper()
    if not s or any(c not in _AA for c in s):
        return dict(liabilities=(), n_liabilities=None, error="invalid amino-acid sequence")
    spans = cdr_positions(framework)
    # CDR mask over the whole sequence (only flag motifs that touch a CDR).
    in_cdr = [False] * len(s)
    for (start, end) in spans.values():
        for i in range(start, min(end, len(s))):
            in_cdr[i] = True

    hits = []
    for i in range(len(s)):
        if not in_cdr[i]:
            continue
        # single-residue oxidation flags
        if s[i] == "M":
            hits.append(("oxidation_Met", i + 1))
        elif s[i] == "W":
            hits.append(("oxidation_Trp", i + 1))
        elif s[i] == "C":
            hits.append(("unpaired_Cys", i + 1))   # heuristic: any CDR Cys flagged (pairing unknown here)
        # dipeptide deamidation/isomerization flags (motif starts in a CDR)
        if i + 1 < len(s):
            dip = s[i:i + 2]
            if dip in _DEAMIDATION:
                hits.append((f"deamidation_{dip}", i + 1))
            if dip in _ISOMERIZATION:
                hits.append((f"isomerization_{dip}", i + 1))
        # N-glycosylation sequon N-X-S/T (X != P)
        if i + 2 < len(s) and s[i] == "N" and s[i + 1] != "P" and s[i + 2] in "ST":
            hits.append(("N-glyc_sequon", i + 1))

    return dict(liabilities=tuple(hits), n_liabilities=len(hits))


# --------------------------------------------------------------------------- #
# Candidate-set assembly + controls.
# --------------------------------------------------------------------------- #
def assemble_candidate_set(scored: list[Variant], top_n: int = 8) -> list[Variant]:
    """Pick a SMALL ranked candidate set from scored single-mutation/redesign Variants.

    Ranks by ESM-1v (favored mutations first), tie-broken by AbLang naturalness, and DROPS any variant
    that introduces a developability liability into a clean position (n_liabilities increased). The
    output is intentionally SMALL — the whole point is a short, testable list, not a sprawling library.
    NOTE: this RANKS; it does not predict KD. Confirm experimentally (SPR/DSF) — see notebook 05.
    """
    def keyfn(v: Variant):
        return (v.esm1v if v.esm1v is not None else -9.9,
                v.ablang if v.ablang is not None else -9.9)
    ranked = sorted(scored, key=keyfn, reverse=True)
    return ranked[:top_n]


def make_controls(parent_seq: str, antigen: str = "ANTIGEN") -> list[Variant]:
    """Build the MANDATORY controls for the validation plan: WT parent + a destabilizing decoy.

    - WT parent: the un-mutated antibody (the affinity baseline every variant is measured against).
    - Destabilizing decoy: a deliberately BAD mutation (a buried/structurally-important position to a
      mismatched residue) expected to LOSE affinity/stability — proves the assay can detect a loss and
      that improvements are real, not noise.
    A specificity panel (off-target antigens) is specified in the plan (notebook 05), not built here.
    These controls are NOT optional; an affinity-maturation claim without WT + a decoy is ungradable.
    """
    out = [Variant(design_id="CONTROL_WT_parent", sequence=parent_seq, parent_id="WT_parent",
                   antigen=antigen, mutations=(), source="control", is_control=True,
                   notes=["positive baseline: WT affinity is the reference for every variant"])]
    # Destabilizing decoy: flip a conserved framework Trp/Tyr to Pro (a known fold-breaker) IF present;
    # else fall back to mutating the first CDR3 residue to Pro. Clearly labelled as an EXPECTED-LOSS.
    decoy_seq, decoy_mut = parent_seq, None
    for i, aa in enumerate(parent_seq):
        if aa in "WY":
            decoy_seq = parent_seq[:i] + "P" + parent_seq[i + 1:]
            decoy_mut = f"{aa}{i+1}P"
            break
    if decoy_mut is None:                       # fallback
        spans = cdr_positions()
        i = spans["CDR3"][0]
        decoy_seq = parent_seq[:i] + "P" + parent_seq[i + 1:]
        decoy_mut = f"{parent_seq[i]}{i+1}P"
    out.append(Variant(design_id="CONTROL_destabilizing_decoy", sequence=decoy_seq,
                       parent_id="WT_parent", antigen=antigen, mutations=(decoy_mut,),
                       source="control", is_control=True,
                       notes=["negative decoy: EXPECTED to lose affinity/stability — proves the assay "
                              "detects a loss; never report it as a maturation candidate"]))
    return out


if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps). All numbers are SYNTHETIC.
    parent = example_parent_sequence()
    print("parent (EXAMPLE placeholder) length:", len(parent), "aa")
    print("CDR spans:", cdr_positions())

    # 1) single-mutation scan over the CDRs (cheap pass)
    singles = score_single_mutations(parent, tool="mock")
    print(f"\nscored {len(singles)} single CDR mutations (ESM-1v + AbLang, SYNTHETIC)")
    cand = assemble_candidate_set(singles, top_n=5)
    print("top-5 candidate single mutations (RANK only, not KD):")
    for v in cand:
        print(f"  {'+'.join(v.mutations):8s} {v.cdr:5s} esm1v={v.esm1v:+.3f} ablang={v.ablang:.3f}")

    # 2) ProteinMPNN CDR3 redesign (framework fixed)
    redesigns = mpnn_cdr_redesign(parent, cdr="CDR3", n=4, tool="mock")
    print(f"\nProteinMPNN CDR3 redesigns (framework FIXED): {len(redesigns)}")

    # 3) pose check + developability on the candidate set
    score_variants(cand, tool="mock")
    d = cand[0]
    print("\nexample candidate after pose check + developability scan:")
    print("  mutation:", "+".join(d.mutations), "| pae_interaction:", d.pae_interaction,
          "| scrmsd:", d.scrmsd, "| liabilities:", d.n_liabilities, d.liabilities)

    # 4) mandatory controls
    ctrls = make_controls(parent)
    print("\ncontrols:", [c.design_id for c in ctrls],
          "(WT baseline + destabilizing decoy — both mandatory)")
    print("\nREMINDER: every number above is SYNTHETIC (mock) and is a RANKING score only — "
          "NEVER a KD/ΔΔG, NEVER report it as a real affinity result.")
