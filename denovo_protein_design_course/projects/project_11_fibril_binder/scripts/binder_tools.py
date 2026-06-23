"""
binder_tools.py — conformation-specific binder-design + AF2-Multimer wrappers for Project 11
(tau / α-synuclein FIBRIL binders).

Goal: clean, import-safe entry points for the two design paradigms, the AF2-Multimer scorer, and the
project's HARD PART — a conformational-specificity test (model the binder vs the MONOMER and vs the
FIBRIL, and require it to PREFER the fibril) — so the notebooks stay thin and the logic is testable
WITHOUT a GPU:

    generate_binders_bindcraft(target, hotspots, n, tool="mock")     -> list[BinderDesign]
    generate_binders_rfdiffusion(target, hotspots, n, tool="mock")   -> list[BinderDesign]  (-> ProteinMPNN)
    af2_multimer(binder_seq, target, tool="mock")                    -> {plddt, pae_interaction, scrmsd, shape_complementarity}
    conformational_specificity(binder, conformer, tool="mock")       -> {pae_interaction, plddt, ...} for ONE conformer state
    specificity_gap(fibril_metrics, monomer_metrics)                 -> Δ(pae_interaction) = monomer - fibril (want > 0)
    plus epitope helpers: parse_hotspots(), hotspot_overlap().

This project's binder-family TEMPLATE is Project 06 (PD-L1); this file keeps that exact shape so the
filter hand-off and the head-to-head plumbing are identical. What is NEW here is conformational
selectivity: a fibril binder must RECOGNIZE the cross-β fibril surface and REJECT the disordered
monomer. That is much harder than a normal binder problem (see the DESIGN NOTE below), and most
designs will NOT be selective — be honest about it.

DESIGN NOTE FOR STUDENTS
------------------------
Real binder generation (BindCraft / RFdiffusion+ProteinMPNN) and AF2-Multimer are heavy and want an
A100 (see MANUAL.md §2). Each backend's real path is a clearly-marked TODO you complete/verify on
Colab; the heavy import happens lazily INSIDE the function. The module imports fine here with no GPU
and no heavy packages. The `mock` backend is DETERMINISTIC (seeded by sequence/target/conformer/
hotspots) so you can develop and unit-test the plumbing — ranking, CSV assembly, the filter hand-off,
and the monomer-vs-fibril specificity test — before spending GPU time. NEVER present mock numbers as
real results: they are SYNTHETIC by construction. NEVER report a fabricated affinity or selectivity
ratio: the specificity GAP here is a teaching proxy, not a measured fold-selectivity.

A word on the monomer counter-test (the HARD PART)
--------------------------------------------------
The amyloid MONOMER (tau, α-synuclein) is intrinsically disordered — it has no single stable fold to
dock against, so the "monomer model" is itself a modeling caveat (use an ensemble/AFDB model and SAY
SO). The fibril, by contrast, is an ordered cross-β stack with a defined, exposed surface. A genuinely
conformation-specific binder scores WELL against the fibril epitope and POORLY against the monomer.
The `specificity_gap` is the monomer-minus-fibril pae_interaction: positive and large = selective for
the fibril. Experimentally this MUST be confirmed by a fibril-vs-monomer ELISA/SPR (notebook 05) —
the in-silico gap is a hypothesis, not a result.

Pinned upstreams (verify they still exist — version-verify cell; pin commits, they change):
  BindCraft      https://github.com/martinpacesa/BindCraft
  FreeBindCraft  https://github.com/cytokineking/FreeBindCraft   (free-tier fallback — VERIFY)
  RFdiffusion    https://github.com/RosettaCommons/RFdiffusion
  ColabDesign    https://github.com/sokrypton/ColabDesign         (RFdiffusion-binder + ProteinMPNN)
  ColabFold      https://github.com/sokrypton/ColabFold           (AF2-Multimer)
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional

# 20 canonical amino acids, used to synthesize deterministic mock binder sequences.
_AA = "ACDEFGHIKLMNPQRSTVWY"
_MOCK_FLAG = "SYNTHETIC — mock backend, not a real design/prediction"

# The two conformational states the binder is tested against (the HARD PART).
CONFORMERS = ("fibril", "monomer")


@dataclass
class BinderDesign:
    """One designed binder against an amyloid FIBRIL surface (tau PHF or α-synuclein fibril)."""
    design_id: str
    sequence: str
    paradigm: str                       # "bindcraft" | "rfdiffusion" | "mock"
    target: str = "TAU_PHF"             # e.g. "TAU_PHF" (5O3L) | "ASYN_FIBRIL" (6CU7)
    hotspots: tuple = ()                # fibril-surface residues the binder was steered to (the exposed epitope)
    length: Optional[int] = None
    # filled by af2_multimer() (the FIBRIL-state score — the design target):
    plddt: Optional[float] = None
    pae_interaction: Optional[float] = None
    scrmsd: Optional[float] = None
    shape_complementarity: Optional[float] = None
    rosetta_dG: Optional[float] = None  # interface energy (REU); real value from PyRosetta/FreeBindCraft
    contact_residues: tuple = ()        # fibril residues the binder actually contacts (for epitope coverage)
    # filled by conformational_specificity()/specificity_gap() (notebook 04 — the HARD PART):
    pae_monomer: Optional[float] = None     # pae_interaction vs the MONOMER conformer (want HIGH = poor binding)
    pae_fibril: Optional[float] = None      # pae_interaction vs the FIBRIL conformer (want LOW = good binding)
    specificity_gap: Optional[float] = None # pae_monomer - pae_fibril (want POSITIVE & large)
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
    """Deterministic pseudo-random amino-acid sequence (mock binder)."""
    seq = []
    x = seed_int
    for _ in range(length):
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        seq.append(_AA[x % len(_AA)])
    return "".join(seq)


# --------------------------------------------------------------------------- #
# Epitope (fibril-surface hotspot) helpers
# --------------------------------------------------------------------------- #
def parse_hotspots(spec) -> tuple:
    """Normalize a hotspot spec into a sorted tuple of residue tokens.

    Accepts a list/tuple/comma-string like 'A306,A310,A315' or ['A306','A310']. These are the
    fibril-SURFACE residues exposed on the ordered cross-β core (the epitope a fibril binder grips) —
    derive them from the cryo-EM fibril structure (see data/README.md), don't invent them. A good
    fibril epitope is solvent-exposed on the protofilament surface AND distinct from anything ordered
    in the (disordered) monomer.
    """
    if isinstance(spec, str):
        items = [s.strip() for s in spec.replace(";", ",").split(",") if s.strip()]
    else:
        items = [str(s).strip() for s in spec if str(s).strip()]
    return tuple(sorted(set(items)))


def hotspot_overlap(contact_residues, hotspots) -> float:
    """Fraction of the fibril-surface hotspots the binder actually contacts (epitope-coverage proxy).

    Higher ⇒ the binder covers more of the exposed fibril epitope. This is a geometry proxy for the
    fibril-vs-monomer assay in notebook 05 — not a guarantee of conformational selectivity (a binder
    can cover the fibril epitope yet still cross-react with the monomer; that is what the
    specificity_gap test in notebook 04 checks).
    """
    hs = set(parse_hotspots(hotspots))
    if not hs:
        return 0.0
    contacts = set(parse_hotspots(contact_residues))
    return round(len(hs & contacts) / len(hs), 3)


# --------------------------------------------------------------------------- #
# Mock generators (deterministic, no GPU). Numbers are SYNTHETIC.
# --------------------------------------------------------------------------- #
def _mock_generate(paradigm: str, target: str, hotspots, n: int) -> list[BinderDesign]:
    hs = parse_hotspots(hotspots)
    out = []
    for i in range(n):
        seed = _hashints(paradigm, target, hs, i)
        length = 50 + (seed % 41)                       # 50–90 aa binder (fibril grooves like a bit more reach)
        seq = _mock_sequence(seed, length)
        # Each paradigm gets a slightly different mock contact profile so the head-to-head
        # comparison in notebook 04 has structure (still SYNTHETIC).
        n_contact = 1 + (seed % max(1, len(hs))) if hs else 0
        contacts = tuple(hs[: n_contact]) if hs else ()
        out.append(BinderDesign(
            design_id=f"EXAMPLE_DATA_{paradigm}_{i:04d}",
            sequence=seq, paradigm=paradigm, target=target, hotspots=hs,
            length=length, contact_residues=contacts, synthetic=True,
            notes=[_MOCK_FLAG],
        ))
    return out


def generate_binders_bindcraft(target: str, hotspots, n: int = 50, tool: str = "mock",
                               binder_length=(50, 90), **kwargs) -> list[BinderDesign]:
    """BindCraft (one-shot hallucination, AF2-Multimer in the loop) vs the FIBRIL surface. Paradigm #1.

    tool="mock"  -> deterministic SYNTHETIC binders (no GPU; develop the plumbing).
    tool="bindcraft" / "freebindcraft" -> real backend (A100; FreeBindCraft for free-tier fallback).
    """
    tool = tool.lower()
    if tool == "mock":
        return _mock_generate("bindcraft", target, hotspots, n)
    if tool in ("bindcraft", "freebindcraft"):
        # TODO (Colab, A100): run BindCraft against the cleaned FIBRIL target at the exposed-surface
        #   hotspots. The "target" here is one protofilament (or a small fibril stack) extracted from
        #   the cryo-EM structure — NOT the disordered monomer.
        #   repo: https://github.com/martinpacesa/BindCraft  (pin a commit)
        #   free-tier fallback: https://github.com/cytokineking/FreeBindCraft  (VERIFY it exists)
        #   key args: target_pdb (fibril surface), hotspot_residues=hotspots, binder_length, num_designs=n
        #   BindCraft already filters on interface confidence; still pass survivors through
        #   af2_multimer() + conformational_specificity() + the shared filter so the head-to-head and
        #   the monomer-vs-fibril selectivity test are apples-to-apples.
        #   A100 STRONGLY RECOMMENDED; free T4 -> FreeBindCraft + small num_designs only.
        raise NotImplementedError(
            "Wire up BindCraft/FreeBindCraft here (A100). See MANUAL.md §2 and the pinned repo; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, bindcraft, freebindcraft")


def generate_binders_rfdiffusion(target: str, hotspots, n: int = 1000, tool: str = "mock",
                                 binder_length=(50, 90), mpnn_temperature: float = 0.1,
                                 num_seq_per_backbone: int = 1, **kwargs) -> list[BinderDesign]:
    """RFdiffusion binder mode -> ProteinMPNN vs the FIBRIL surface (diffuse backbone, then design seq). Paradigm #2.

    tool="mock"        -> deterministic SYNTHETIC binders (no GPU).
    tool="rfdiffusion" -> real backend (A100 for 500-1000 backbones).
    """
    tool = tool.lower()
    if tool == "mock":
        return _mock_generate("rfdiffusion", target, hotspots, n)
    if tool == "rfdiffusion":
        # TODO (Colab, A100): RFdiffusion binder mode -> ProteinMPNN -> AF2-Multimer.
        #   RFdiffusion:  https://github.com/RosettaCommons/RFdiffusion   (pin a commit)
        #   ColabDesign:  https://github.com/sokrypton/ColabDesign        (binder protocol + ProteinMPNN)
        #   1) diffuse n backbones with ppi.hotspot_res=hotspots on the FIBRIL surface, binderlen in
        #      binder_length range (the flat cross-β surface favors binders that span a groove);
        #   2) ProteinMPNN over each backbone (temperature=mpnn_temperature, num_seq_per_backbone);
        #   3) AF2-Multimer re-prediction of each (binder, fibril) complex -> pae_interaction;
        #   4) then conformational_specificity() vs the MONOMER as the counter-test.
        #   500-1000 backbones want A100/HPC; small batches OK on T4. AF2-Multimer is the slow step.
        raise NotImplementedError(
            "Wire up RFdiffusion binder mode + ProteinMPNN here (A100). See MANUAL.md §2; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, rfdiffusion")


# --------------------------------------------------------------------------- #
# AF2-Multimer scorer (the key binder metric is pae_interaction).
# --------------------------------------------------------------------------- #
def af2_multimer(binder_seq: str, target: str = "TAU_PHF", tool: str = "mock",
                 hotspots=(), conformer: str = "fibril", **kwargs) -> dict:
    """Score a (binder, target) complex for ONE conformer. Returns the metrics the shared binder
    filter consumes: {plddt, pae_interaction, scrmsd, shape_complementarity} (+ synthetic flag).

    `conformer` is "fibril" (the design target) or "monomer" (the counter-test). For the FIBRIL the
    target structure is an ordered protofilament surface; for the MONOMER it is a disordered/ensemble
    model (a modeling caveat — say so). pae_interaction (AF2-Multimer) is THE key binder metric.
    tool="mock" returns deterministic SYNTHETIC numbers; tool="af2"/"colabfold" runs real AF2-Multimer.
    """
    tool = tool.lower()
    conformer = (conformer or "fibril").lower()
    if not binder_seq or any(c not in _AA for c in binder_seq.upper()):
        return dict(plddt=None, pae_interaction=None, scrmsd=None,
                    shape_complementarity=None, ok=False, error="invalid amino-acid sequence")
    if tool == "mock":
        h = _hashints("af2", target, conformer, hotspots, binder_seq.upper())
        # Deterministic SYNTHETIC metrics in plausible-but-arbitrary ranges. These are NOT real.
        # We bias the MONOMER state toward WORSE (higher) pae_interaction so that the mock data has the
        # teaching structure we want — a fraction of designs look fibril-selective. This bias is a
        # TEACHING DEVICE, not a claim that designs are really selective; the real monomer counter-test
        # often shows cross-reactivity. Selectivity must be proven by the wet-lab assay (notebook 05).
        plddt = 70 + (h % 30)                       # 70–99
        base_pae = 4 + (h % 16)                     # 4–19 (key binder metric; lower better)
        if conformer == "monomer":
            base_pae = base_pae + 2 + (h % 9)       # SYNTHETIC monomer penalty (disordered, harder to bind)
        scrmsd = round(0.8 + (h % 350) / 100.0, 3)  # 0.8–4.3 Å
        sc = round(0.45 + (h % 45) / 100.0, 3)      # 0.45–0.89 shape complementarity
        return dict(plddt=float(plddt), pae_interaction=float(base_pae),
                    scrmsd=float(scrmsd), shape_complementarity=sc,
                    conformer=conformer, ok=True, synthetic=True, error=_MOCK_FLAG)
    if tool in ("af2", "colabfold", "af2_multimer", "multimer"):
        # TODO (Colab): run AF2-Multimer (ColabFold, model_type=multimer) on the (binder, target)
        #   complex for the given conformer; parse mean inter-chain PAE -> pae_interaction, interface
        #   pLDDT -> plddt; compute scRMSD (designed vs predicted binder backbone) and shape
        #   complementarity. For conformer="monomer" use a disordered/ensemble monomer model and report
        #   the modeling caveat. repo: https://github.com/sokrypton/ColabFold (pin a commit). Small
        #   complexes OK on T4; campaign-scale prefers A100. This is usually the slowest step — batch.
        raise NotImplementedError(
            "Wire up AF2-Multimer here (ColabFold, model_type=multimer). See MANUAL.md §2; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, af2/colabfold")


def score_designs(designs: list[BinderDesign], tool: str = "mock") -> list[BinderDesign]:
    """Run af2_multimer() (FIBRIL state) over a list of BinderDesign and fill their metric fields."""
    for d in designs:
        m = af2_multimer(d.sequence, target=d.target, tool=tool, hotspots=d.hotspots, conformer="fibril")
        if not m.get("ok", True):
            d.notes.append(f"af2_multimer failed: {m.get('error')}")
            continue
        d.plddt = m["plddt"]
        d.pae_interaction = m["pae_interaction"]
        d.scrmsd = m["scrmsd"]
        d.shape_complementarity = m["shape_complementarity"]
        d.pae_fibril = m["pae_interaction"]
        if m.get("synthetic"):
            d.synthetic = True
    return designs


# --------------------------------------------------------------------------- #
# THE HARD PART — conformational specificity (fibril vs monomer)
# --------------------------------------------------------------------------- #
def conformational_specificity(binder, conformer: str, tool: str = "mock", **kwargs) -> dict:
    """Score ONE binder against ONE conformational state of the target (fibril or monomer).

    `binder` may be a BinderDesign or a raw sequence string. Returns the AF2-Multimer metric dict for
    that state (key field: pae_interaction). Run this for BOTH conformers and feed the two
    pae_interaction values to `specificity_gap()`.

    A conformation-SPECIFIC binder: LOW pae_interaction vs the fibril, HIGH vs the monomer. This is the
    hard requirement that separates a diagnostic-grade conformational binder from a generic sticky
    peptide. tool="mock" is deterministic SYNTHETIC; tool="af2" runs real AF2-Multimer per state.
    """
    if conformer.lower() not in CONFORMERS:
        raise ValueError(f"conformer must be one of {CONFORMERS}, got {conformer!r}")
    seq = binder.sequence if isinstance(binder, BinderDesign) else str(binder)
    target = binder.target if isinstance(binder, BinderDesign) else kwargs.get("target", "TAU_PHF")
    hotspots = binder.hotspots if isinstance(binder, BinderDesign) else kwargs.get("hotspots", ())
    return af2_multimer(seq, target=target, tool=tool, hotspots=hotspots, conformer=conformer.lower())


def specificity_gap(fibril_metrics: dict, monomer_metrics: dict) -> Optional[float]:
    """Conformational-selectivity proxy = pae_interaction(monomer) - pae_interaction(fibril).

    POSITIVE & large ⇒ AF2 is much more confident about the fibril complex than the monomer complex ⇒
    the binder PREFERS the fibril (what we want). ~0 or negative ⇒ the binder cross-reacts with (or
    even prefers) the disordered monomer ⇒ NOT a conformation-specific binder; reject it.

    This is a teaching proxy on a model metric — NOT a measured fold-selectivity. The monomer is
    intrinsically disordered, so its model (and therefore this gap) carries extra uncertainty; the
    fibril-vs-monomer ELISA/SPR in notebook 05 is what actually establishes selectivity.
    """
    pf = fibril_metrics.get("pae_interaction")
    pm = monomer_metrics.get("pae_interaction")
    if pf is None or pm is None:
        return None
    return round(float(pm) - float(pf), 3)


def evaluate_specificity(designs: list[BinderDesign], tool: str = "mock") -> list[BinderDesign]:
    """For each design, score BOTH conformers, store pae_fibril/pae_monomer/specificity_gap in place.

    This is the notebook-04 driver for the HARD PART. After this, a design is "fibril-selective" if its
    specificity_gap clears the chosen threshold (set + justified in notebook 04) — a HYPOTHESIS to be
    tested by the fibril-vs-monomer assay, never a reported selectivity ratio.
    """
    for d in designs:
        mf = conformational_specificity(d, "fibril", tool=tool)
        mm = conformational_specificity(d, "monomer", tool=tool)
        if not (mf.get("ok", True) and mm.get("ok", True)):
            d.notes.append("conformational_specificity failed (invalid sequence?)")
            continue
        d.pae_fibril = mf["pae_interaction"]
        d.pae_monomer = mm["pae_interaction"]
        d.specificity_gap = specificity_gap(mf, mm)
        if mf.get("synthetic") or mm.get("synthetic"):
            d.synthetic = True
    return designs


if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps). All numbers are SYNTHETIC.
    HOTSPOTS = "A306,A310,A315"   # EXAMPLE tau-PHF fibril-surface residues — verify from the cryo-EM structure
    bc = generate_binders_bindcraft("TAU_PHF", HOTSPOTS, n=5, tool="mock")
    rf = generate_binders_rfdiffusion("TAU_PHF", HOTSPOTS, n=5, tool="mock")
    score_designs(bc, tool="mock")
    score_designs(rf, tool="mock")
    evaluate_specificity(bc, tool="mock")     # THE HARD PART: monomer vs fibril
    evaluate_specificity(rf, tool="mock")
    print(f"BindCraft mock designs:   {len(bc)}")
    print(f"RFdiffusion mock designs: {len(rf)}")
    d = bc[0]
    print("example design:", d.design_id, "len=", d.length,
          "pae_fibril=", d.pae_fibril, "pae_monomer=", d.pae_monomer,
          "specificity_gap=", d.specificity_gap, "synthetic=", d.synthetic)
    print("epitope coverage (example):", hotspot_overlap(d.contact_residues, HOTSPOTS))
    n_sel = sum(1 for x in bc + rf if (x.specificity_gap or 0) >= 4)
    print(f"mock fibril-selective (gap>=4): {n_sel}/{len(bc)+len(rf)} (SYNTHETIC — selectivity proven only by assay)")
    print("REMINDER: every number above is SYNTHETIC (mock) — never report it as a real result.")
