"""
cytokine_tools.py — agonist-mini-protein design + per-subunit AF2-Multimer wrappers for Project 13
(de novo IL-2-receptor-selective cytokine mimetics, the Neo-2/15 paradigm).

Goal: clean, import-safe entry points for the design paradigms and the AF2-Multimer scorer, plus the
project's defining twist — RECEPTOR-SUBUNIT SELECTIVITY — so the notebooks stay thin and the logic is
testable WITHOUT a GPU:

    generate_agonists_rfdiffusion(target, hotspots, n, tool="mock")  -> list[AgonistDesign]  (-> ProteinMPNN)
    generate_agonists_bindcraft(target, hotspots, n, tool="mock")    -> list[AgonistDesign]
    af2_multimer(seq, subunit, tool="mock")                          -> {plddt, pae_interaction, scrmsd, shape_complementarity}
    subunit_selectivity(binder, subunit, tool="mock")                -> pae_interaction of the design vs ONE subunit
    selectivity_profile(binder, subunits=SUBUNITS, tool="mock")      -> {subunit: pae_interaction, ...} + a selectivity call
    plus hotspot helpers: parse_hotspots(), hotspot_overlap().

This follows the BINDER-FAMILY TEMPLATE (Project 06 / scripts/binder_tools.py): the mock backend is
DETERMINISTIC, the real backends are clearly-marked TODOs with A100 notes, and ALL mock numbers are
flagged SYNTHETIC. The new piece is per-subunit modeling: a cytokine mimetic is only useful if it
engages the RIGHT receptor subunits (e.g., IL-2Rβ + γc to signal) and SPARES the wrong one (IL-2Rα /
CD25, whose engagement makes native IL-2 toxic). We therefore model each design against EACH subunit
separately and report the SELECTIVITY PROFILE.

DESIGN NOTE FOR STUDENTS
------------------------
Real agonist generation (RFdiffusion+ProteinMPNN / BindCraft) and AF2-Multimer are heavy and want an
A100 (see MANUAL.md §2) — and running AF2-Multimer against THREE subunits roughly triples the cost.
Each backend's real path is a clearly-marked TODO you complete/verify on Colab; the heavy import
happens lazily INSIDE the function. This module imports fine here with no GPU and no heavy packages.
The `mock` backend is DETERMINISTIC (seeded by sequence/subunit/hotspots) so you can develop and
unit-test the plumbing — ranking, the selectivity profile, CSV assembly, the filter hand-off — before
spending GPU time. NEVER present mock numbers as real results: they are SYNTHETIC by construction, and
there is NO fabricated EC50/K_D anywhere in this file.

REMINDER (the science): binding is NOT signaling. A design that engages β and γc in a model is a
HYPOTHESIS of an agonist; only a cell-based STAT-phosphorylation (pSTAT5) assay confirms agonism
(notebook 05). The selectivity profile tells you WHICH subunits it engages, not WHETHER it signals.

Pinned upstreams (verify they still exist — version-verify cell; pin commits, they change):
  RFdiffusion    https://github.com/RosettaCommons/RFdiffusion
  ColabDesign    https://github.com/sokrypton/ColabDesign         (RFdiffusion-binder + ProteinMPNN)
  BindCraft      https://github.com/martinpacesa/BindCraft
  FreeBindCraft  https://github.com/cytokineking/FreeBindCraft     (free-tier fallback — VERIFY)
  ColabFold      https://github.com/sokrypton/ColabFold            (AF2-Multimer, run PER SUBUNIT)
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional

# 20 canonical amino acids, used to synthesize deterministic mock agonist sequences.
_AA = "ACDEFGHIKLMNPQRSTVWY"
_MOCK_FLAG = "SYNTHETIC — mock backend, not a real design/prediction"

# The three IL-2 receptor subunits. β and γc are the SIGNALING pair (engage these to dimerize the
# receptor → JAK/STAT → pSTAT5); α/CD25 is the high-affinity CAPTURE chain (SPARE it for βγ-biased
# selectivity, the Neo-2/15 choice). Edit ENGAGE/SPARE in the notebook if you choose a different goal.
SUBUNITS = ("IL2Ra", "IL2Rb", "gammaC")
ENGAGE_DEFAULT = ("IL2Rb", "gammaC")   # the signaling pair we WANT to engage
SPARE_DEFAULT = ("IL2Ra",)             # the capture chain we WANT to spare (CD25)


@dataclass
class AgonistDesign:
    """One designed cytokine-mimetic mini-protein against the chosen receptor surface."""
    design_id: str
    sequence: str
    paradigm: str                       # "rfdiffusion" | "bindcraft" | "mock"
    target: str = "IL2R_beta_gamma"     # the surface it was steered onto (the signaling pair)
    hotspots: tuple = ()                # receptor residues the design was steered to (β/γc signaling face)
    length: Optional[int] = None
    # filled by score against the ENGAGED subunits (af2_multimer / score_designs):
    plddt: Optional[float] = None
    scrmsd: Optional[float] = None
    shape_complementarity: Optional[float] = None
    rosetta_dG: Optional[float] = None  # interface energy (REU); real value from PyRosetta/FreeBindCraft
    # per-subunit interface confidence — the SELECTIVITY PROFILE (filled by selectivity_profile()):
    pae_by_subunit: dict = field(default_factory=dict)   # {"IL2Ra": .., "IL2Rb": .., "gammaC": ..}
    pae_interaction: Optional[float] = None              # convenience: max pae over the ENGAGED subunits
    contact_residues: tuple = ()        # receptor residues the design actually contacts (epitope proxy)
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
    """Deterministic pseudo-random amino-acid sequence (mock agonist mini-protein)."""
    seq = []
    x = seed_int
    for _ in range(length):
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        seq.append(_AA[x % len(_AA)])
    return "".join(seq)


# --------------------------------------------------------------------------- #
# Hotspot helpers
# --------------------------------------------------------------------------- #
def parse_hotspots(spec) -> tuple:
    """Normalize a hotspot spec into a sorted tuple of residue tokens.

    Accepts a list/tuple/comma-string like 'B41,B42,C100' or ['B41','B42']. These are the receptor
    residues on the SIGNALING face (IL-2Rβ + γc) that you steer the agonist onto — derive them from the
    IL-2/IL-2R interface in the complex (see data/README.md), don't invent them. Tokens are typically
    'chain+number' so β and γc residues are distinguishable.
    """
    if isinstance(spec, str):
        items = [s.strip() for s in spec.replace(";", ",").split(",") if s.strip()]
    else:
        items = [str(s).strip() for s in spec if str(s).strip()]
    return tuple(sorted(set(items)))


def hotspot_overlap(contact_residues, hotspots) -> float:
    """Fraction of the signaling-face hotspots the design actually contacts (engagement proxy).

    Higher ⇒ the design covers more of the β/γc signaling footprint ⇒ more likely to engage (and, if it
    bridges BOTH chains, to dimerize → signal). A geometry proxy — not a guarantee of agonism.
    """
    hs = set(parse_hotspots(hotspots))
    if not hs:
        return 0.0
    contacts = set(parse_hotspots(contact_residues))
    return round(len(hs & contacts) / len(hs), 3)


# --------------------------------------------------------------------------- #
# Mock generators (deterministic, no GPU). Numbers are SYNTHETIC.
# --------------------------------------------------------------------------- #
def _mock_generate(paradigm: str, target: str, hotspots, n: int) -> list[AgonistDesign]:
    hs = parse_hotspots(hotspots)
    out = []
    for i in range(n):
        seed = _hashints(paradigm, target, hs, i)
        length = 50 + (seed % 41)                       # 50–90 aa mini-protein (Neo-2/15-scale)
        seq = _mock_sequence(seed, length)
        # Each paradigm gets a slightly different mock contact profile so the analysis in nb04 has
        # structure (still SYNTHETIC).
        n_contact = 1 + (seed % max(1, len(hs))) if hs else 0
        contacts = tuple(hs[: n_contact]) if hs else ()
        out.append(AgonistDesign(
            design_id=f"EXAMPLE_DATA_{paradigm}_{i:04d}",
            sequence=seq, paradigm=paradigm, target=target, hotspots=hs,
            length=length, contact_residues=contacts, synthetic=True,
            notes=[_MOCK_FLAG],
        ))
    return out


def generate_agonists_rfdiffusion(target: str, hotspots, n: int = 1000, tool: str = "mock",
                                  binder_length=(50, 90), mpnn_temperature: float = 0.1,
                                  num_seq_per_backbone: int = 1, **kwargs) -> list[AgonistDesign]:
    """RFdiffusion binder mode -> ProteinMPNN (diffuse mini-protein backbone, then design sequence).
    Primary paradigm: steer onto the IL-2Rβ + γc signaling surface so the design can bridge both chains.

    tool="mock"        -> deterministic SYNTHETIC designs (no GPU; develop the plumbing).
    tool="rfdiffusion" -> real backend (A100 for 500-1000 backbones).
    """
    tool = tool.lower()
    if tool == "mock":
        return _mock_generate("rfdiffusion", target, hotspots, n)
    if tool == "rfdiffusion":
        # TODO (Colab, A100): RFdiffusion binder mode -> ProteinMPNN -> AF2-Multimer PER SUBUNIT.
        #   RFdiffusion:  https://github.com/RosettaCommons/RFdiffusion   (pin a commit)
        #   ColabDesign:  https://github.com/sokrypton/ColabDesign        (binder protocol + ProteinMPNN)
        #   1) supply BOTH receptor chains (β and γc) as the target so the mini-protein can bridge them;
        #      diffuse n backbones with ppi.hotspot_res=hotspots (β/γc signaling face), binderlen in range;
        #   2) ProteinMPNN over each backbone (temperature=mpnn_temperature, num_seq_per_backbone);
        #   3) AF2-Multimer re-prediction of each (design, subunit) complex for EACH of α/β/γc separately
        #      -> selectivity_profile(). 500-1000 backbones want A100/HPC; AF2 ×3 subunits is the slow step.
        raise NotImplementedError(
            "Wire up RFdiffusion binder mode + ProteinMPNN here (A100). See MANUAL.md §2; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, rfdiffusion")


def generate_agonists_bindcraft(target: str, hotspots, n: int = 50, tool: str = "mock",
                                binder_length=(50, 90), **kwargs) -> list[AgonistDesign]:
    """BindCraft (one-shot hallucination, AF2-Multimer in the loop). Alternative/foil paradigm.

    tool="mock"  -> deterministic SYNTHETIC designs (no GPU; develop the plumbing).
    tool="bindcraft" / "freebindcraft" -> real backend (A100; FreeBindCraft for free-tier fallback).
    """
    tool = tool.lower()
    if tool == "mock":
        return _mock_generate("bindcraft", target, hotspots, n)
    if tool in ("bindcraft", "freebindcraft"):
        # TODO (Colab, A100): run BindCraft against the cleaned IL-2Rβ/γc surface at the signaling hotspots.
        #   repo: https://github.com/martinpacesa/BindCraft  (pin a commit)
        #   free-tier fallback: https://github.com/cytokineking/FreeBindCraft  (VERIFY it exists)
        #   key args: target_pdb (β+γc surface), hotspot_residues=hotspots, binder_length, num_designs=n
        #   Still pass survivors through af2_multimer() PER SUBUNIT + the shared filter so the analysis
        #   is apples-to-apples with RFdiffusion. A100 STRONGLY RECOMMENDED; free T4 -> FreeBindCraft.
        raise NotImplementedError(
            "Wire up BindCraft/FreeBindCraft here (A100). See MANUAL.md §2 and the pinned repo; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, bindcraft, freebindcraft")


# --------------------------------------------------------------------------- #
# AF2-Multimer scorer — run PER SUBUNIT. The key metric is pae_interaction.
# --------------------------------------------------------------------------- #
def af2_multimer(seq: str, subunit: str = "IL2Rb", tool: str = "mock",
                 hotspots=(), **kwargs) -> dict:
    """Score a (design, ONE receptor subunit) complex. Returns the metrics the shared binder filter
    consumes for that subunit:
        {plddt, pae_interaction, scrmsd, shape_complementarity}  (+ synthetic flag for mock).

    pae_interaction (AF2-Multimer) is THE key metric. Call this ONCE PER SUBUNIT (α, β, γc) to build the
    selectivity profile (see selectivity_profile()). tool="mock" returns deterministic SYNTHETIC numbers;
    tool="af2"/"colabfold" runs the real AF2-Multimer on Colab.
    """
    tool = tool.lower()
    if not seq or any(c not in _AA for c in seq.upper()):
        return dict(plddt=None, pae_interaction=None, scrmsd=None,
                    shape_complementarity=None, ok=False, error="invalid amino-acid sequence")
    if tool == "mock":
        # Deterministic SYNTHETIC metrics, SEEDED BY SUBUNIT so the per-subunit profile has structure.
        # We bias the mock so designs tend to engage the SIGNALING pair (β, γc) more than the CAPTURE
        # chain (α) — i.e. the mock leans toward the βγ-biased selectivity we are teaching. This is a
        # TEACHING STAND-IN; it is NOT evidence any real design is selective.
        h = _hashints("af2", subunit, hotspots, seq.upper())
        base = 4 + (h % 16)                         # 4–19 (key metric; lower = more confident interface)
        if subunit in ("IL2Ra",):                   # capture chain: nudge pae UP (less engaged) on average
            pae = min(24.0, base + 5)
        else:                                        # signaling chains (β, γc): nudge pae DOWN (engaged)
            pae = max(2.0, base - 2)
        plddt = 70 + (h % 30)                        # 70–99
        scrmsd = round(0.8 + (h % 350) / 100.0, 3)   # 0.8–4.3 Å (subunit-independent self-consistency)
        sc = round(0.45 + (h % 45) / 100.0, 3)       # 0.45–0.89 shape complementarity
        return dict(plddt=float(plddt), pae_interaction=float(pae),
                    scrmsd=float(scrmsd), shape_complementarity=sc,
                    subunit=subunit, ok=True, synthetic=True, error=_MOCK_FLAG)
    if tool in ("af2", "colabfold", "af2_multimer", "multimer"):
        # TODO (Colab): run AF2-Multimer (ColabFold, model_type=multimer) on the (design, <subunit>)
        #   complex; parse mean inter-chain PAE -> pae_interaction, interface pLDDT -> plddt; compute
        #   scRMSD (designed vs predicted mini-protein backbone) and shape complementarity.
        #   repo: https://github.com/sokrypton/ColabFold  (pin a commit). RUN ONCE PER SUBUNIT (α/β/γc).
        #   Small complexes OK on T4; campaign-scale ×3-subunits prefers A100 — the slowest step.
        raise NotImplementedError(
            "Wire up AF2-Multimer here (ColabFold, model_type=multimer), called PER SUBUNIT. "
            "See MANUAL.md §2; develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, af2/colabfold")


# --------------------------------------------------------------------------- #
# SELECTIVITY — the project's defining twist.
# --------------------------------------------------------------------------- #
def subunit_selectivity(binder, subunit: str, tool: str = "mock", hotspots=()) -> Optional[float]:
    """Model `binder` against ONE receptor subunit and return its pae_interaction for that subunit.

    `binder` may be an AgonistDesign or a raw sequence string. This is the atom of the selectivity
    profile: call it for each of IL-2Rα / IL-2Rβ / γc to see which subunits the design engages. Lower
    pae ⇒ more confidently engaged. (For a βγ-biased agonist you want LOW pae to β and γc, HIGH pae to α.)
    """
    seq = getattr(binder, "sequence", binder)
    hs = hotspots or getattr(binder, "hotspots", ())
    m = af2_multimer(seq, subunit=subunit, tool=tool, hotspots=hs)
    if not m.get("ok", True):
        return None
    return m["pae_interaction"]


def selectivity_profile(binder, subunits=SUBUNITS, tool: str = "mock",
                        engage=ENGAGE_DEFAULT, spare=SPARE_DEFAULT,
                        engage_max_pae: float = 10.0, spare_min_pae: float = 14.0,
                        margin_min: float = 4.0) -> dict:
    """Build the per-subunit SELECTIVITY PROFILE for one design and make a selectivity call.

    Returns a dict:
        {
          "pae_by_subunit": {"IL2Ra": .., "IL2Rb": .., "gammaC": ..},   # the profile
          "engage": (..,), "spare": (..,),
          "engaged_ok": bool,        # LOW pae (<= engage_max_pae) to ALL `engage` subunits
          "spared_ok": bool,         # HIGH pae (>= spare_min_pae) to ALL `spare` subunits
          "selectivity_margin": float,   # min(pae over spare) - max(pae over engage); larger = cleaner
          "selective": bool,         # engaged_ok AND spared_ok AND margin >= margin_min
          "synthetic": bool,
        }

    Defaults encode the Neo-2/15 goal: ENGAGE IL-2Rβ + γc (signal), SPARE IL-2Rα/CD25 (the toxic capture
    chain). Override `engage`/`spare` in the notebook if you chose a different selectivity.

    NOTE: `selective` is an IN-SILICO hypothesis about which subunits are engaged. It does NOT establish
    agonism — binding is not signaling; only a cell pSTAT5 assay does (notebook 05). With tool="mock"
    every number is SYNTHETIC.
    """
    pae = {s: subunit_selectivity(binder, s, tool=tool) for s in subunits}
    eng_vals = [pae[s] for s in engage if pae.get(s) is not None]
    spr_vals = [pae[s] for s in spare if pae.get(s) is not None]

    engaged_ok = bool(eng_vals) and all(v <= engage_max_pae for v in eng_vals)
    spared_ok = bool(spr_vals) and all(v >= spare_min_pae for v in spr_vals)
    if eng_vals and spr_vals:
        margin = round(min(spr_vals) - max(eng_vals), 3)   # high spare - low engage; larger = cleaner
    else:
        margin = None
    selective = bool(engaged_ok and spared_ok and (margin is not None and margin >= margin_min))

    synthetic = bool(getattr(binder, "synthetic", False)) or tool.lower() == "mock"
    profile = dict(
        pae_by_subunit={s: pae[s] for s in subunits},
        engage=tuple(engage), spare=tuple(spare),
        engaged_ok=engaged_ok, spared_ok=spared_ok,
        selectivity_margin=margin, selective=selective, synthetic=synthetic,
    )
    # If we were handed an AgonistDesign, write the profile back onto it for convenience.
    if isinstance(binder, AgonistDesign):
        binder.pae_by_subunit = profile["pae_by_subunit"]
        binder.pae_interaction = max(eng_vals) if eng_vals else None   # worst engaged-subunit pae
        if synthetic:
            binder.synthetic = True
    return profile


def score_designs(designs: list[AgonistDesign], tool: str = "mock",
                  engage=ENGAGE_DEFAULT, spare=SPARE_DEFAULT) -> list[AgonistDesign]:
    """Build the per-subunit selectivity profile for each design (filling pae_by_subunit /
    pae_interaction) AND fill the subunit-independent metrics (plddt/scrmsd/sc) from an engaged subunit.
    Numbers are SYNTHETIC under tool='mock'."""
    for d in designs:
        # per-subunit profile (selectivity) — also sets d.pae_by_subunit + d.pae_interaction (worst engaged)
        selectivity_profile(d, tool=tool, engage=engage, spare=spare)
        # subunit-independent metrics: take them from the first engaged subunit's prediction
        ref_sub = engage[0] if engage else SUBUNITS[1]
        m = af2_multimer(d.sequence, subunit=ref_sub, tool=tool, hotspots=d.hotspots)
        if not m.get("ok", True):
            d.notes.append(f"af2_multimer failed: {m.get('error')}")
            continue
        d.plddt = m["plddt"]
        d.scrmsd = m["scrmsd"]
        d.shape_complementarity = m["shape_complementarity"]
        if m.get("synthetic"):
            d.synthetic = True
    return designs


if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps). All numbers are SYNTHETIC.
    # EXAMPLE β/γc signaling-face hotspots — verify yours from the IL-2/IL-2R interface (data/README.md).
    HOTSPOTS = "B41,B42,C100,C102"
    rf = generate_agonists_rfdiffusion("IL2R_beta_gamma", HOTSPOTS, n=5, tool="mock")
    bc = generate_agonists_bindcraft("IL2R_beta_gamma", HOTSPOTS, n=5, tool="mock")
    score_designs(rf, tool="mock")
    score_designs(bc, tool="mock")
    print(f"RFdiffusion mock designs: {len(rf)}")
    print(f"BindCraft  mock designs:  {len(bc)}")
    d = rf[0]
    prof = selectivity_profile(d, tool="mock")
    print("example design:", d.design_id, "len=", d.length, "plddt=", d.plddt, "scrmsd=", d.scrmsd)
    print("  per-subunit pae (selectivity profile):", prof["pae_by_subunit"], "(SYNTHETIC)")
    print("  engage", prof["engage"], "spare", prof["spare"],
          "| margin=", prof["selectivity_margin"], "| selective=", prof["selective"])
    print("  engagement overlap (β/γc footprint):", hotspot_overlap(d.contact_residues, HOTSPOTS))
    print("REMINDER: every number above is SYNTHETIC (mock) — never report it as a real result,")
    print("and SELECTIVE in silico is NOT an agonist: binding != signaling (cell pSTAT5 decides it).")
