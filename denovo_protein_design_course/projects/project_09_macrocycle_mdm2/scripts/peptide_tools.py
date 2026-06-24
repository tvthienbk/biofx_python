"""
peptide_tools.py — peptide / macrocycle binder-design + scoring wrappers for Project 09
(MDM2-p53 macrocyclic/peptide binders).

Goal: clean, import-safe entry points for the peptide-design backends, the Boltz-2 relative
affinity scorer, and the modality comparison, so the notebooks stay thin and the logic is testable
WITHOUT a GPU:

    design_peptide(target, cleft, length, cyclic, n, tool="mock")  -> list[PeptideDesign]
    boltz_affinity(complex, tool="mock")                           -> dict (RELATIVE score scaffold)
    modality_compare(peptides, miniproteins)                       -> dict / table-ready rows
    plus cleft helpers: parse_cleft(), cleft_overlap().

This file matches the BINDER-FAMILY TEMPLATE (scripts/binder_tools.py in Project 06): keep the mock
deterministic, the real backends behind documented TODOs with honest compute notes, and ALL mock
numbers flagged SYNTHETIC.

WHAT IS DIFFERENT FROM A MINI-PROTEIN BINDER (Project 06)
---------------------------------------------------------
The modality here is a SHORT PEPTIDE (linear ~8-20 aa) or a MACROCYCLE (head-to-tail / side-chain
cyclized), not a 40-80 aa mini-protein. That changes the chemistry and the validation, not the
filtering API:
  * peptides are made by SOLID-PHASE PEPTIDE SYNTHESIS (SPPS), not E. coli expression;
  * linear peptides are protease-labile and usually cell-impermeable; CYCLIZATION (and D-amino acids
    / N-methylation / stapling) is what buys protease stability and, sometimes, permeability;
  * predicted affinity for short peptides is UNRELIABLE — rank, don't trust absolute numbers, and
    NEVER fabricate a K_D. Boltz-2 here is a scaffold/ranking signal only.
Project 06's mini-binder path is kept as a FOIL (the peptide-vs-protein modality comparison): we mock
a mini-protein pool with the same API so notebook 04 can compare the two modalities head-to-head.

DESIGN NOTE FOR STUDENTS
------------------------
Real peptide/macrocycle generation (BoltzGen peptide/macrocycle protocols, EvoBind2) and AF2/Boltz-2
scoring are heavier than this module: small peptide inputs are tractable on a Colab T4 (Boltz-2
affinity on small inputs is OK on T4), but a full macrocycle CAMPAIGN prefers Colab Pro (see
MANUAL.md §2). Each backend's real path is a clearly-marked TODO you complete/verify on Colab; the
heavy import happens lazily INSIDE the function. This module imports fine here with no GPU and no
heavy packages. The `mock` backend is DETERMINISTIC (seeded by target/cleft/length/cyclic) so you can
develop and unit-test the plumbing — ranking, CSV assembly, the filter hand-off — before spending GPU
time. NEVER present mock numbers as real results: they are SYNTHETIC by construction.

Pinned upstreams (verify they still exist — version-verify cell; pin commits, they change):
  BoltzGen   (peptide-anything / macrocycle-anything)  — VERIFY the current public release + URL.
  EvoBind2   https://github.com/patrickbryant1/EvoBind  (cyclic/linear peptide binder design — VERIFY)
  Boltz      https://github.com/jwohlwend/boltz          (Boltz-2 structure + affinity)
  ColabFold  https://github.com/sokrypton/ColabFold      (AF2 / AF2-Multimer pAE)
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional

# 20 canonical amino acids, used to synthesize deterministic mock peptide sequences.
# (Real macrocycles may also use D-amino acids / N-methylation / non-canonical residues — a
#  chemistry the mock backend does NOT model; see the D-amino-acid / stapling stretch in nb05.)
_AA = "ACDEFGHIKLMNPQRSTVWY"
_MOCK_FLAG = "SYNTHETIC — mock backend, not a real design/prediction"


@dataclass
class PeptideDesign:
    """One designed peptide / macrocycle against the target cleft (MDM2 p53-binding cleft)."""
    design_id: str
    sequence: str
    modality: str                       # "linear" | "macrocycle" | "miniprotein" (foil)
    tool: str = "mock"                  # "boltzgen" | "evobind2" | "miniprotein-foil" | "mock"
    target: str = "MDM2"
    cleft: tuple = ()                   # MDM2 residues lining the p53 cleft (the Phe19/Trp23/Leu26 pocket)
    length: Optional[int] = None
    cyclic: bool = False               # True ⇒ head-to-tail / side-chain macrocycle
    # filled by score / boltz_affinity:
    plddt: Optional[float] = None
    pae_interaction: Optional[float] = None   # AF2 / Boltz pAE across the peptide-MDM2 interface
    scrmsd: Optional[float] = None
    shape_complementarity: Optional[float] = None
    boltz_affinity_score: Optional[float] = None  # RELATIVE ranking scaffold — NOT a K_D
    contact_residues: tuple = ()        # MDM2 cleft residues the peptide actually contacts
    solubility: Optional[float] = None
    synthetic: bool = False             # True ⇒ numbers are mock/EXAMPLE_DATA, never report as real
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


def _mock_sequence(seed_int: int, length: int) -> str:
    """Deterministic pseudo-random amino-acid sequence (mock peptide)."""
    seq = []
    x = seed_int
    for _ in range(length):
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        seq.append(_AA[x % len(_AA)])
    return "".join(seq)


# --------------------------------------------------------------------------- #
# Cleft helpers (the analog of "hotspots" in the binder template)
# --------------------------------------------------------------------------- #
def parse_cleft(spec) -> tuple:
    """Normalize a cleft-residue spec into a sorted tuple of residue tokens.

    Accepts a list/tuple/comma-string like 'A54,A67,A93,A100' or ['A54','A67']. These are the MDM2
    residues lining the p53-binding cleft (the hydrophobic pocket that buries p53 Phe19/Trp23/Leu26).
    Derive them from the MDM2-p53 complex (e.g., 1YCR — VERIFY on RCSB), don't invent them.
    """
    if isinstance(spec, str):
        items = [s.strip() for s in spec.replace(";", ",").split(",") if s.strip()]
    else:
        items = [str(s).strip() for s in spec if str(s).strip()]
    return tuple(sorted(set(items)))


def cleft_overlap(contact_residues, cleft) -> float:
    """Fraction of the MDM2 cleft residues the peptide actually contacts (engagement proxy).

    Higher ⇒ the peptide covers more of the p53-binding pocket ⇒ more likely to displace p53 and
    restore p53 signalling. This is a geometry proxy for a competition / reporter assay — not a
    guarantee of functional p53 reactivation.
    """
    cl = set(parse_cleft(cleft))
    if not cl:
        return 0.0
    contacts = set(parse_cleft(contact_residues))
    return round(len(cl & contacts) / len(cl), 3)


# --------------------------------------------------------------------------- #
# Mock generator (deterministic, no GPU). Numbers are SYNTHETIC.
# --------------------------------------------------------------------------- #
def _mock_design(modality: str, tool: str, target: str, cleft, length, cyclic: bool,
                 n: int) -> list[PeptideDesign]:
    cl = parse_cleft(cleft)
    out = []
    for i in range(n):
        seed = _hashints(modality, tool, target, cl, length, cyclic, i)
        # Peptides are short; macrocycles tend a touch longer (ring closure). Length jitters around
        # the requested length so a length sweep has structure (still SYNTHETIC).
        if length is None:
            base = 18 if modality == "miniprotein" else (12 if cyclic else 10)
        else:
            base = int(length)
        jitter = (seed % 5) - 2                          # +-2 aa around the requested length
        L = max(6, base + jitter)
        seq = _mock_sequence(seed, L)
        # Each modality/cyclic combo gets a slightly different mock contact profile so the
        # linear-vs-cyclic and peptide-vs-protein comparisons in notebook 04 have structure.
        n_contact = 1 + (seed % max(1, len(cl))) if cl else 0
        contacts = tuple(cl[: n_contact]) if cl else ()
        # Encode the requested length in the id so a length/constraint SWEEP yields UNIQUE ids
        # (calling design_peptide once per length must not collide on i alone).
        len_tag = f"L{int(length)}" if length is not None else "Lna"
        out.append(PeptideDesign(
            design_id=f"EXAMPLE_DATA_{modality}_{'cyc' if cyclic else 'lin'}_{len_tag}_{i:04d}",
            sequence=seq, modality=modality, tool=tool, target=target, cleft=cl,
            length=L, cyclic=cyclic, contact_residues=contacts, synthetic=True,
            notes=[_MOCK_FLAG],
        ))
    return out


def design_peptide(target: str, cleft, length: Optional[int] = None, cyclic: bool = False,
                   n: int = 50, tool: str = "mock", **kwargs) -> list[PeptideDesign]:
    """Design linear or macrocyclic peptide binders against the target cleft.

    Args:
        target : target name (e.g. "MDM2"); the cleaned cleft structure you prepared from 1YCR.
        cleft  : MDM2 cleft residues (the p53 pocket) — the analog of binder "hotspots".
        length : requested peptide length (linear ~8-20; macrocycle ~7-15). None ⇒ a modality default.
        cyclic : True ⇒ macrocycle (head-to-tail / side-chain cyclized); False ⇒ linear.
        n      : number of designs.
        tool   : "mock" (deterministic, no GPU) | "boltzgen" | "evobind2" (real backends).

    Returns: list[PeptideDesign]. Mock numbers are SYNTHETIC.
    """
    tool = tool.lower()
    modality = "macrocycle" if cyclic else "linear"
    if tool == "mock":
        return _mock_design(modality, "mock", target, cleft, length, cyclic, n)
    if tool in ("boltzgen", "macrocycle-anything", "peptide-anything"):
        # TODO (Colab, T4 for small peptides / Pro for a macrocycle campaign):
        #   run BoltzGen's peptide-anything (linear) or macrocycle-anything (cyclic) protocol against
        #   the cleaned MDM2 cleft. VERIFY the current public BoltzGen release + URL first (the
        #   version-verify cell) — mark it clearly; the public interface is moving.
        #   key args: target_pdb (cleaned MDM2 cleft), cleft/hotspot residues=cleft, peptide length,
        #             cyclic flag (head-to-tail), num_designs=n.
        #   Pass survivors through boltz_affinity()/AF2 pAE + the shared filter so the head-to-head
        #   with the mini-protein foil is apples-to-apples.
        raise NotImplementedError(
            "Wire up BoltzGen peptide/macrocycle protocol here. VERIFY the current public release "
            "(version-verify cell). See MANUAL.md §2; develop with tool='mock' first.")
    if tool in ("evobind2", "evobind"):
        # TODO (Colab): run EvoBind2 (MSA-free cyclic/linear peptide binder design) against MDM2.
        #   repo: https://github.com/patrickbryant1/EvoBind  (pin a commit; VERIFY it still exists)
        #   EvoBind2 optimizes a (cyclic) peptide binder sequence against the target with an
        #   AF2-based objective; set the cyclic flag for macrocycles. Small inputs are T4-tractable.
        raise NotImplementedError(
            "Wire up EvoBind2 here (https://github.com/patrickbryant1/EvoBind — VERIFY). "
            "See MANUAL.md §2; develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, boltzgen, evobind2")


def design_miniprotein_foil(target: str, cleft, n: int = 50, tool: str = "mock",
                            binder_length=(40, 80), **kwargs) -> list[PeptideDesign]:
    """Mini-protein binder FOIL for the peptide-vs-protein MODALITY comparison (nb04).

    This stands in for a Project-06-style mini-binder (BindCraft / RFdiffusion-binder) so the modality
    comparison has the other arm. tool="mock" returns deterministic SYNTHETIC mini-proteins; the real
    path defers to the Project-06 binder workflow (BindCraft / RFdiffusion + ProteinMPNN, A100).
    """
    tool = tool.lower()
    if tool == "mock":
        cl = parse_cleft(cleft)
        out = []
        for i in range(n):
            seed = _hashints("miniprotein", target, cl, i)
            L = binder_length[0] + (seed % (binder_length[1] - binder_length[0] + 1))
            seq = _mock_sequence(seed, L)
            n_contact = 1 + (seed % max(1, len(cl))) if cl else 0
            contacts = tuple(cl[: n_contact]) if cl else ()
            out.append(PeptideDesign(
                design_id=f"EXAMPLE_DATA_miniprotein_{i:04d}",
                sequence=seq, modality="miniprotein", tool="miniprotein-foil",
                target=target, cleft=cl, length=L, cyclic=False,
                contact_residues=contacts, synthetic=True, notes=[_MOCK_FLAG],
            ))
        return out
    # TODO (Colab, A100): defer to the Project-06 binder workflow (BindCraft / RFdiffusion-binder +
    #   ProteinMPNN -> AF2-Multimer) against the same MDM2 cleft, so the modality comparison is fair.
    raise NotImplementedError(
        "Mini-protein foil real path = the Project-06 binder workflow (A100). "
        "See projects/project_06_pdl1_binder and MANUAL.md §2; develop with tool='mock' first.")


# --------------------------------------------------------------------------- #
# Scoring: AF2/Boltz pAE + Boltz-2 RELATIVE affinity (NOT a K_D).
# --------------------------------------------------------------------------- #
def _score_complex(seq: str, target: str, cleft, cyclic: bool) -> dict:
    """Deterministic SYNTHETIC interface metrics (mock). NOT real."""
    h = _hashints("score", target, cleft, cyclic, seq.upper())
    plddt = 65 + (h % 32)                        # 65-96
    pae = 5 + (h % 16)                           # 5-20 Å (peptide-MDM2 interface; lower better)
    scrmsd = round(0.9 + (h % 320) / 100.0, 3)   # 0.9-4.1 Å
    sc = round(0.45 + (h % 45) / 100.0, 3)       # 0.45-0.89 shape complementarity
    return dict(plddt=float(plddt), pae_interaction=float(pae),
                scrmsd=scrmsd, shape_complementarity=sc)


def boltz_affinity(complex, target: str = "MDM2", cleft=(), cyclic: bool = False,
                   tool: str = "mock", **kwargs) -> dict:
    """Predict a RELATIVE binding-affinity score for a peptide-target complex.

    `complex` may be a PeptideDesign, a sequence string, or a path to a complex PDB. Returns a dict
    with a `boltz_affinity_score` plus interface metrics. tool="mock" returns deterministic SYNTHETIC
    numbers; tool="boltz" runs the real Boltz-2 affinity head on Colab (small peptide inputs are
    T4-tractable).

    !!! THIS IS A SCAFFOLD / RANKING SIGNAL, NOT A K_D. !!!
    Predicted affinity for short peptides is UNRELIABLE. Use it to PRIORITIZE which hits to synthesize
    first — never report it as a measured affinity, and never fabricate a K_D. (MASTER_BLUEPRINT §9.)
    """
    tool = tool.lower()
    # Resolve the sequence / fields from whatever was passed.
    if isinstance(complex, PeptideDesign):
        seq, target, cleft, cyclic = complex.sequence, complex.target, complex.cleft, complex.cyclic
    elif isinstance(complex, str):
        seq = complex
    else:
        return dict(ok=False, error="pass a PeptideDesign, a sequence, or a complex-PDB path")
    if not seq or any(c not in _AA for c in seq.upper()):
        return dict(ok=False, error="invalid amino-acid sequence",
                    plddt=None, pae_interaction=None, scrmsd=None,
                    shape_complementarity=None, boltz_affinity_score=None)
    if tool == "mock":
        m = _score_complex(seq, target, cleft, cyclic)
        h = _hashints("aff", target, cleft, cyclic, seq.upper())
        # Deterministic SYNTHETIC *relative* score in an arbitrary range. Higher = better RANK only.
        # NOT a K_D, not pK_d, not ΔG. Flagged synthetic.
        rel = round((h % 1000) / 1000.0, 4)      # 0.000-0.999 relative ranking scaffold
        m.update(boltz_affinity_score=rel, ok=True, synthetic=True, error=_MOCK_FLAG)
        return m
    if tool in ("boltz", "boltz2", "boltz-2"):
        # TODO (Colab): run Boltz-2 on the (peptide, MDM2) complex with the affinity head; parse the
        #   predicted-affinity SIGNAL -> boltz_affinity_score (RELATIVE), pAE -> pae_interaction.
        #   repo: https://github.com/jwohlwend/boltz  (pin a version). Small peptide inputs OK on T4.
        #   REPORT RELATIVE RANKING + CAVEATS ONLY — never a fabricated K_D (MASTER_BLUEPRINT §9).
        raise NotImplementedError(
            "Wire up Boltz-2 affinity here (https://github.com/jwohlwend/boltz). "
            "Relative ranking + caveats only, NEVER a K_D. Develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, boltz")


def score_designs(designs: list[PeptideDesign], tool: str = "mock") -> list[PeptideDesign]:
    """Run boltz_affinity() over a list of PeptideDesign and fill their metric fields in place."""
    for d in designs:
        m = boltz_affinity(d, tool=tool)
        if not m.get("ok", True):
            d.notes.append(f"boltz_affinity failed: {m.get('error')}")
            continue
        d.plddt = m["plddt"]
        d.pae_interaction = m["pae_interaction"]
        d.scrmsd = m["scrmsd"]
        d.shape_complementarity = m["shape_complementarity"]
        d.boltz_affinity_score = m["boltz_affinity_score"]
        if m.get("synthetic"):
            d.synthetic = True
    return designs


# --------------------------------------------------------------------------- #
# Modality comparison (peptide vs mini-protein, and linear vs cyclic)
# --------------------------------------------------------------------------- #
def _pass_binder(d: PeptideDesign,
                 scrmsd=2.5, plddt=80, pae=10, sc=0.6) -> bool:
    """Quick all-layers proxy used ONLY for a fast modality-comparison summary in this module.
    The authoritative filtering is the shared filtering_pipeline (design_type='binder') in nb03."""
    return (d.scrmsd is not None and d.scrmsd <= scrmsd
            and d.plddt is not None and d.plddt >= plddt
            and d.pae_interaction is not None and d.pae_interaction <= pae
            and d.shape_complementarity is not None and d.shape_complementarity >= sc)


def modality_compare(*groups, labels=None) -> list[dict]:
    """Summarize hit rate + interface metrics for one or more design groups.

    Pass any number of design lists (e.g. linear peptides, macrocycles, mini-protein foil); returns
    one summary row per group (n, all-layers proxy hit rate, median pAE, median cleft overlap,
    median Boltz relative-affinity rank). Use it for the linear-vs-cyclic AND peptide-vs-protein
    comparisons in notebook 04. Numbers are SYNTHETIC if the designs were mock-scored.
    """
    rows = []
    for i, g in enumerate(groups):
        label = labels[i] if labels and i < len(labels) else (g[0].modality if g else f"group{i}")
        n = len(g)
        passed = sum(_pass_binder(d) for d in g)
        paes = [d.pae_interaction for d in g if d.pae_interaction is not None]
        affs = [d.boltz_affinity_score for d in g if d.boltz_affinity_score is not None]
        overlaps = [cleft_overlap(d.contact_residues, d.cleft) for d in g]
        synthetic = any(d.synthetic for d in g)
        rows.append(dict(
            group=label,
            n=n,
            all_layers_proxy_hits=passed,
            hit_rate_pct=round(100 * passed / max(n, 1), 1),
            median_pae=round(float(_median(paes)), 2) if paes else None,
            median_cleft_overlap=round(float(_median(overlaps)), 3) if overlaps else None,
            median_boltz_rank=round(float(_median(affs)), 4) if affs else None,
            synthetic=synthetic,
        ))
    return rows


def _median(xs):
    xs = sorted(xs)
    n = len(xs)
    if n == 0:
        return float("nan")
    mid = n // 2
    return xs[mid] if n % 2 else (xs[mid - 1] + xs[mid]) / 2.0


if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps). All numbers are SYNTHETIC.
    CLEFT = "A54,A67,A73,A93,A100"   # EXAMPLE MDM2 p53-cleft residues — VERIFY yours from 1YCR
    lin = design_peptide("MDM2", CLEFT, length=12, cyclic=False, n=6, tool="mock")
    cyc = design_peptide("MDM2", CLEFT, length=12, cyclic=True,  n=6, tool="mock")
    mp  = design_miniprotein_foil("MDM2", CLEFT, n=6, tool="mock")
    score_designs(lin, tool="mock")
    score_designs(cyc, tool="mock")
    score_designs(mp,  tool="mock")
    print(f"linear peptides   : {len(lin)}")
    print(f"macrocycles       : {len(cyc)}")
    print(f"mini-protein foil : {len(mp)}")
    d = cyc[0]
    print("example macrocycle:", d.design_id, "len=", d.length, "cyclic=", d.cyclic,
          "pae=", d.pae_interaction, "scrmsd=", d.scrmsd, "sc=", d.shape_complementarity,
          "boltz_rank=", d.boltz_affinity_score, "synthetic=", d.synthetic)
    print("cleft engagement overlap (example):", cleft_overlap(d.contact_residues, CLEFT))
    print("\nmodality_compare (linear vs cyclic vs mini-protein):")
    for row in modality_compare(lin, cyc, mp, labels=["linear", "macrocycle", "miniprotein"]):
        print(" ", row)
    print("\nREMINDER: every number above is SYNTHETIC (mock) — never report it as a real result.")
    print("Boltz affinity is a RELATIVE RANK scaffold, NOT a K_D.")
