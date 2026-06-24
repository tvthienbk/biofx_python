"""
antibody_tools.py — de-novo VHH/nanobody design + structure-validation + developability wrappers
for Project 17 (nanobodies vs a tumor-associated antigen).

Goal: clean, import-safe entry points for VHH CDR design, the antibody-aware structure scorer, and
the developability heuristics, so the notebooks stay thin and the logic is testable WITHOUT a GPU:

    design_vhh_cdrs(antigen, epitope, framework, n, tool="mock")  -> list[VhhDesign]
    af2_multimer_ab(vhh_seq, antigen, tool="mock")                -> {plddt, pae_interaction, scrmsd, cdr_geom}
    developability(seq)                                           -> {tap_score, camsol_like, humanness}
    plus epitope helpers: parse_epitope(), epitope_overlap(); CDR helpers: extract_cdrs().

This file is the ANTIBODY-FAMILY TEMPLATE (Projects 14-16 follow this shape): keep the mock
deterministic, the real backends behind documented TODOs with A100 notes, and ALL mock numbers
flagged SYNTHETIC. The developability functions are CLEARLY-LABELED teaching heuristics, NOT the
validated tools (TAP/CamSol/Hu-mAb) they imitate — see the WARNING on each.

DESIGN NOTE FOR STUDENTS
------------------------
Real VHH generation (RFantibody = RFdiffusion-Ab + ProteinMPNN; or BoltzGen nanobody mode) and
AF2-Multimer/IgFold are heavy and want an A100 (see MANUAL.md §2). Each backend's real path is a
clearly-marked TODO you complete/verify on Colab; the heavy import happens lazily INSIDE the
function. The module imports fine here with no GPU and no heavy packages. The `mock` backend is
DETERMINISTIC (seeded by antigen/epitope/framework/index) so you can develop and unit-test the
plumbing — ranking, CSV assembly, the filter hand-off — before spending GPU time. NEVER present mock
numbers as real results: they are SYNTHETIC by construction.

Realistic expectations: de novo antibody/nanobody hit rates are LOW. Treat every surviving design as
a *screening input* for a yeast/phage display campaign, not a finished binder.

Pinned upstreams (verify they still exist — version-verify cell; pin commits, they change):
  RFantibody     https://github.com/RosettaCommons/RFantibody     (RFdiffusion-Ab + ProteinMPNN)
  BoltzGen       (verify the current public release at generation time — see MANUAL.md §2)
  ImmuneBuilder  https://github.com/oxpig/ImmuneBuilder            (NanoBodyBuilder2 / IgFold-style)
  ColabFold      https://github.com/sokrypton/ColabFold            (AF2-Multimer)
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional

# 20 canonical amino acids, used to synthesize deterministic mock CDR loops.
_AA = "ACDEFGHIKLMNPQRSTVWY"
_MOCK_FLAG = "SYNTHETIC — mock backend, not a real design/prediction"

# A minimal humanized VHH (camelid VHH3 / "universal" humanized scaffold) framework, split into the
# four framework regions FR1..FR4. CDRs are inserted between them by the mock generator. This is a
# TEACHING placeholder sequence in the cAbBCII10/humanized-VHH spirit — VERIFY and replace with the
# exact framework you choose (e.g., a hu-VHH3 germline) in notebook 01 before any real run.
DEFAULT_FRAMEWORK = {
    "name": "huVHH3_teaching_placeholder",
    "FR1": "QVQLVESGGGLVQPGGSLRLSCAAS",
    "FR2": "WVRQAPGKGLEWVS",
    "FR3": "RFTISRDNSKNTLYLQMNSLRAEDTAVYYC",
    "FR4": "WGQGTLVTVSS",
}


@dataclass
class VhhDesign:
    """One designed VHH/nanobody (single-domain antibody) against the antigen (a TAA)."""
    design_id: str
    sequence: str                       # full VHH: FR1-CDR1-FR2-CDR2-FR3-CDR3-FR4
    tool: str                           # "rfantibody" | "boltzgen" | "mock"
    antigen: str = "HER2"
    epitope: tuple = ()                 # antigen residues the VHH was steered to (the chosen epitope)
    framework: str = DEFAULT_FRAMEWORK["name"]
    cdr1: str = ""
    cdr2: str = ""
    cdr3: str = ""
    # filled by af2_multimer_ab():
    plddt: Optional[float] = None
    pae_interaction: Optional[float] = None
    scrmsd: Optional[float] = None
    cdr_geom: Optional[float] = None    # CDR-loop geometry RMSD vs the modelled VHH (Å); lower = better
    # filled by developability():  (teaching heuristics — NOT validated tools)
    tap_score: Optional[float] = None   # TAP-like flag count proxy (lower = fewer liabilities)
    camsol_like: Optional[float] = None # CamSol-like solubility proxy (higher = more soluble)
    humanness: Optional[float] = None   # OASis/Hu-mAb-like humanness proxy in [0,1] (higher = more human)
    contact_residues: tuple = ()        # antigen residues the VHH actually contacts (for epitope binning)
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


def _mock_loop(seed_int: int, length: int) -> str:
    """Deterministic pseudo-random amino-acid loop (mock CDR)."""
    seq = []
    x = seed_int
    for _ in range(length):
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        seq.append(_AA[x % len(_AA)])
    return "".join(seq)


# --------------------------------------------------------------------------- #
# Epitope helpers (the antibody analogue of binder hotspots)
# --------------------------------------------------------------------------- #
def parse_epitope(spec) -> tuple:
    """Normalize an epitope spec into a sorted tuple of antigen residue tokens.

    Accepts a list/tuple/comma-string like 'A557,A560,A579' or ['A557','A560']. These are the
    antigen residues you steer the VHH toward — derive them from the antigen surface (and, for the
    'overlapping vs non-overlapping with an approved mAb' choice, from the mAb-antigen interface in
    the reference complex; see data/README.md). Don't invent them.
    """
    if isinstance(spec, str):
        items = [s.strip() for s in spec.replace(";", ",").split(",") if s.strip()]
    else:
        items = [str(s).strip() for s in spec if str(s).strip()]
    return tuple(sorted(set(items)))


def epitope_overlap(contact_residues, epitope) -> float:
    """Fraction of the chosen epitope the VHH actually contacts (epitope-binning proxy).

    Use the SAME function against an approved mAb's footprint to reason about whether your VHH would
    COMPETE with (overlap) or be ORTHOGONAL to (non-overlap) that mAb — the P3/P4 epitope-binning
    question. This is a geometry proxy for a competition/binning assay, not a guarantee.
    """
    ep = set(parse_epitope(epitope))
    if not ep:
        return 0.0
    contacts = set(parse_epitope(contact_residues))
    return round(len(ep & contacts) / len(ep), 3)


# --------------------------------------------------------------------------- #
# CDR helpers
# --------------------------------------------------------------------------- #
def extract_cdrs(design: "VhhDesign") -> dict:
    """Return the three CDR loops of a design as a dict (CDR3 dominates paratope diversity)."""
    return {"CDR1": design.cdr1, "CDR2": design.cdr2, "CDR3": design.cdr3}


def _assemble_vhh(framework: dict, cdr1: str, cdr2: str, cdr3: str) -> str:
    """Stitch FR1-CDR1-FR2-CDR2-FR3-CDR3-FR4 into a full VHH sequence."""
    return (framework["FR1"] + cdr1 + framework["FR2"] + cdr2 +
            framework["FR3"] + cdr3 + framework["FR4"])


# --------------------------------------------------------------------------- #
# Mock VHH generator (deterministic, no GPU). Numbers/sequences are SYNTHETIC.
# --------------------------------------------------------------------------- #
def _mock_design(tool: str, antigen: str, epitope, framework: dict, n: int) -> list[VhhDesign]:
    ep = parse_epitope(epitope)
    out = []
    for i in range(n):
        seed = _hashints(tool, antigen, ep, framework["name"], i)
        # CDR lengths roughly mirror camelid VHH distributions (CDR3 is the long, dominant loop).
        len1 = 5 + (seed % 3)                       # CDR1 ~5-7
        len2 = 6 + ((seed >> 3) % 3)                # CDR2 ~6-8
        len3 = 8 + ((seed >> 6) % 13)               # CDR3 ~8-20 (long, hypervariable)
        cdr1 = _mock_loop(seed, len1)
        cdr2 = _mock_loop(seed >> 11, len2)
        cdr3 = _mock_loop(seed >> 19, len3)
        seq = _assemble_vhh(framework, cdr1, cdr2, cdr3)
        # Each design gets a mock contact profile so the epitope-binning view has structure (SYNTHETIC).
        n_contact = 1 + (seed % max(1, len(ep))) if ep else 0
        contacts = tuple(ep[:n_contact]) if ep else ()
        out.append(VhhDesign(
            design_id=f"EXAMPLE_DATA_{tool}_{i:04d}",
            sequence=seq, tool=tool, antigen=antigen, epitope=ep,
            framework=framework["name"], cdr1=cdr1, cdr2=cdr2, cdr3=cdr3,
            contact_residues=contacts, synthetic=True, notes=[_MOCK_FLAG],
        ))
    return out


def design_vhh_cdrs(antigen: str, epitope, framework: Optional[dict] = None, n: int = 50,
                    tool: str = "mock", **kwargs) -> list[VhhDesign]:
    """Design n VHH/nanobody candidates against `antigen` at `epitope`, on a fixed `framework`.

    This is the antibody analogue of binder generation: RFantibody (RFdiffusion-Ab diffuses the CDR
    loops onto the framework against the target epitope, then ProteinMPNN designs the loop sequence)
    or BoltzGen nanobody mode. The framework + epitope are FIXED inputs; the CDRs (especially CDR3)
    are the design variables.

    tool="mock"        -> deterministic SYNTHETIC VHHs (no GPU; develop the plumbing).
    tool="rfantibody"  -> real RFantibody backend (A100; see MANUAL.md §2).
    tool="boltzgen"    -> real BoltzGen nanobody backend (verify release; see MANUAL.md §2).
    """
    tool = tool.lower()
    framework = framework or DEFAULT_FRAMEWORK
    if tool == "mock":
        return _mock_design("mock", antigen, epitope, framework, n)
    if tool == "rfantibody":
        # TODO (Colab, A100): run RFantibody against the cleaned TAA target at the chosen epitope.
        #   repo: https://github.com/RosettaCommons/RFantibody  (pin a commit; e.g. main@<sha>)
        #   1) RFdiffusion-Ab: diffuse CDR loops onto the VHH framework, conditioning on
        #      target_pdb + hotspot/epitope residues (epitope), keeping framework fixed;
        #   2) ProteinMPNN: design the CDR-loop sequences (framework positions fixed);
        #   3) hand survivors to af2_multimer_ab() + the shared antibody filter.
        #   A100 STRONGLY RECOMMENDED; free T4 -> a tiny demo run only. Hit rates are LOW: generate
        #   500+ and route survivors to a display screen (notebook 05). See MANUAL.md §2.
        raise NotImplementedError(
            "Wire up RFantibody here (A100). See MANUAL.md §2 and the pinned repo; "
            "develop with tool='mock' first.")
    if tool == "boltzgen":
        # TODO (Colab, A100): run BoltzGen in nanobody mode against the TAA epitope.
        #   VERIFY the current public BoltzGen release/repo at the start of the course (see MANUAL.md
        #   §2) and pin it; the API is newer and changes. Use it as the [extension] head-to-head with
        #   RFantibody (notebook 04). Develop with tool='mock' first.
        raise NotImplementedError(
            "Wire up BoltzGen nanobody mode here (A100); VERIFY the current release first. "
            "See MANUAL.md §2; develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, rfantibody, boltzgen")


# --------------------------------------------------------------------------- #
# AF2-Multimer / IgFold antibody scorer (key metrics: pae_interaction + CDR geometry).
# --------------------------------------------------------------------------- #
def af2_multimer_ab(vhh_seq: str, antigen: str = "HER2", tool: str = "mock",
                    epitope=(), **kwargs) -> dict:
    """Score a (VHH, antigen) complex. Returns the metrics the shared antibody filter consumes:
        {plddt, pae_interaction, scrmsd, cdr_geom}  (+ synthetic flag for mock).

    pae_interaction (AF2-Multimer, antibody cutoff <=12) is the key complex metric; cdr_geom is a
    CDR-loop geometry RMSD (Ramachandran/loop sanity, e.g. vs an IgFold/NanoBodyBuilder2 model).
    tool="mock" returns deterministic SYNTHETIC numbers; tool="af2"/"igfold" run the real backends.
    """
    tool = tool.lower()
    if not vhh_seq or any(c not in _AA for c in vhh_seq.upper()):
        return dict(plddt=None, pae_interaction=None, scrmsd=None, cdr_geom=None,
                    ok=False, error="invalid amino-acid sequence")
    if tool == "mock":
        h = _hashints("af2ab", antigen, epitope, vhh_seq.upper())
        # Deterministic SYNTHETIC metrics in plausible-but-arbitrary ranges. These are NOT real.
        plddt = 65 + (h % 33)                       # 65-97
        pae_interaction = 5 + (h % 16)              # 5-20 (key metric; antibody cutoff <=12)
        scrmsd = round(0.9 + (h % 320) / 100.0, 3)  # 0.9-4.1 Å
        cdr_geom = round(0.5 + (h % 250) / 100.0, 3)  # 0.5-3.0 Å CDR-loop geometry RMSD
        return dict(plddt=float(plddt), pae_interaction=float(pae_interaction),
                    scrmsd=float(scrmsd), cdr_geom=cdr_geom,
                    ok=True, synthetic=True, error=_MOCK_FLAG)
    if tool in ("af2", "colabfold", "af2_multimer", "multimer"):
        # TODO (Colab): run AF2-Multimer (ColabFold, model_type=multimer) on the (VHH, antigen)
        #   complex; parse mean inter-chain PAE -> pae_interaction, interface pLDDT -> plddt; compute
        #   scRMSD (designed vs predicted VHH backbone). repo: https://github.com/sokrypton/ColabFold
        #   (pin a commit). Small complexes OK on T4; campaign-scale prefers A100 (slowest step).
        raise NotImplementedError(
            "Wire up AF2-Multimer here (ColabFold, model_type=multimer). See MANUAL.md §2; "
            "develop with tool='mock' first.")
    if tool in ("igfold", "immunebuilder", "nanobodybuilder2"):
        # TODO (Colab): model the VHH alone with IgFold / ImmuneBuilder NanoBodyBuilder2 to get a
        #   fast, antibody-aware backbone for CDR-loop geometry (cdr_geom) without an MSA.
        #   repo: https://github.com/oxpig/ImmuneBuilder  (pin a commit). Cheap — T4 fine.
        raise NotImplementedError(
            "Wire up IgFold/ImmuneBuilder here for CDR geometry. See MANUAL.md §2; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, af2/colabfold, igfold/immunebuilder")


def score_designs(designs: list[VhhDesign], tool: str = "mock") -> list[VhhDesign]:
    """Run af2_multimer_ab() + developability() over a list of VhhDesign; fill fields in place."""
    for d in designs:
        m = af2_multimer_ab(d.sequence, antigen=d.antigen, tool=tool, epitope=d.epitope)
        if not m.get("ok", True):
            d.notes.append(f"af2_multimer_ab failed: {m.get('error')}")
            continue
        d.plddt = m["plddt"]
        d.pae_interaction = m["pae_interaction"]
        d.scrmsd = m["scrmsd"]
        d.cdr_geom = m["cdr_geom"]
        if m.get("synthetic"):
            d.synthetic = True
        dev = developability(d.sequence)
        d.tap_score = dev["tap_score"]
        d.camsol_like = dev["camsol_like"]
        d.humanness = dev["humanness"]
    return designs


# --------------------------------------------------------------------------- #
# Developability heuristics.
#   WARNING: these are TEACHING HEURISTICS, NOT the validated tools they imitate.
#   - Real TAP (Therapeutic Antibody Profiler, Raybould 2019) needs a 3-D Fv model and computes five
#     structure-based flags (CDR length, surface hydrophobic/charge patches, charge symmetry).
#   - Real CamSol (Sormanni 2015) is a sequence/structure solubility predictor.
#   - Real humanness uses OASis / Hu-mAb / T20 against human-repertoire databases.
#   Use the functions below ONLY to develop the pipeline and to teach what each axis MEASURES; swap
#   in the real tools (documented as TODOs) before drawing any developability conclusion.
# --------------------------------------------------------------------------- #
# Kyte-Doolittle hydropathy (used only for the CamSol-like solubility heuristic).
_KD = {"A": 1.8, "R": -4.5, "N": -3.5, "D": -3.5, "C": 2.5, "Q": -3.5, "E": -3.5,
       "G": -0.4, "H": -3.2, "I": 4.5, "L": 3.8, "K": -3.9, "M": 1.9, "F": 2.8,
       "P": -1.6, "S": -0.8, "T": -0.7, "W": -0.9, "Y": -1.3, "V": 4.2}
# Residues counted toward net charge at ~neutral pH (sign only; a coarse proxy).
_POS, _NEG = set("KR"), set("DE")
# Sequence-level chemical-liability motifs (deamidation NG/NS, isomerization DG, free Cys, N-glyc NxS/T,
# Met oxidation) — a sequence proxy for what TAP flags structurally. Teaching-grade only.
_LIABILITY_MOTIFS = ("NG", "NS", "DG", "DS")


def developability(seq: str) -> dict:
    """TEACHING-HEURISTIC developability proxies (NOT validated tools). Deterministic, no GPU.

    Returns {tap_score, camsol_like, humanness}:
      - tap_score   : count-based liability proxy (lower = fewer flags). Counts CDR-ish liability
                      motifs + free cysteines + N-glycosylation sequons + a long-CDR3 penalty.
                      A TAP-LIKE flag count, NOT a real TAP red/amber/green call.
      - camsol_like : mean Kyte-Doolittle hydropathy, sign-flipped so HIGHER = more soluble. A crude
                      CamSol-LIKE proxy; real CamSol is structure-aware.
      - humanness   : fraction of residues matching the humanized-VHH framework consensus, in [0,1].
                      A toy OASis/Hu-mAb-LIKE proxy; real humanness scores against human repertoires.
    Every value is a heuristic for TEACHING the axis — never report it as a developability verdict.
    """
    s = (seq or "").upper()
    if not s or any(c not in _AA for c in s):
        return dict(tap_score=None, camsol_like=None, humanness=None,
                    error="invalid amino-acid sequence")

    # --- tap_score: count liabilities (lower is better) -------------------------------------------
    motif_hits = sum(s.count(m) for m in _LIABILITY_MOTIFS)
    free_cys = s.count("C")                                   # disulfide-pairing risk if unpaired
    nglyc = sum(1 for i in range(len(s) - 2)                  # N-X-S/T sequon (X != P)
                if s[i] == "N" and s[i + 1] != "P" and s[i + 2] in "ST")
    long_cdr3_penalty = 1 if len(s) > 130 else 0             # very long VHH (long CDR3) liability proxy
    tap_score = float(motif_hits + free_cys + nglyc + long_cdr3_penalty)

    # --- camsol_like: solubility proxy (higher is better) -----------------------------------------
    mean_kd = sum(_KD[c] for c in s) / len(s)
    camsol_like = round(-mean_kd, 3)                         # flip: hydrophilic (-KD) => higher score

    # --- humanness: consensus-match proxy in [0,1] (higher is better) -----------------------------
    consensus = (DEFAULT_FRAMEWORK["FR1"] + DEFAULT_FRAMEWORK["FR2"] +
                 DEFAULT_FRAMEWORK["FR3"] + DEFAULT_FRAMEWORK["FR4"])
    # Compare composition overlap against the humanized framework consensus (toy proxy).
    from collections import Counter
    cs, cc = Counter(s), Counter(consensus)
    shared = sum(min(cs[a], cc[a]) for a in _AA)
    humanness = round(shared / max(len(s), 1), 3)
    humanness = min(1.0, humanness)

    return dict(tap_score=tap_score, camsol_like=camsol_like, humanness=humanness)


if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps). All numbers are SYNTHETIC.
    EPITOPE = "A557,A560,A579"   # EXAMPLE HER2 epitope residues — VERIFY yours from the antigen surface
    rfa = design_vhh_cdrs("HER2", EPITOPE, n=5, tool="mock")
    bg = design_vhh_cdrs("HER2", EPITOPE, n=5, tool="mock")  # same mock seed family; real run -> tool="boltzgen"
    score_designs(rfa, tool="mock")
    print(f"RFantibody-style mock VHH designs: {len(rfa)}")
    d = rfa[0]
    print("example design:", d.design_id, "len=", len(d.sequence),
          "CDR3=", d.cdr3, "(", len(d.cdr3), "aa )")
    print("  af2:  pae_interaction=", d.pae_interaction, "scrmsd=", d.scrmsd,
          "cdr_geom=", d.cdr_geom, "synthetic=", d.synthetic)
    print("  dev:  tap_score=", d.tap_score, "camsol_like=", d.camsol_like,
          "humanness=", d.humanness, "(TEACHING HEURISTICS — not validated tools)")
    print("  epitope-binning overlap (example):", epitope_overlap(d.contact_residues, EPITOPE))
    print("REMINDER: every number above is SYNTHETIC (mock) — never report it as a real result.")
