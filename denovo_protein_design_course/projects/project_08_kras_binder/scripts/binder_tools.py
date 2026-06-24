"""
binder_tools.py — binder-design + AF2-Multimer wrappers for Project 08 (de novo binders vs KRAS).

Goal: clean, import-safe entry points for the two design paradigms, the AF2-Multimer scorer, and an
isoform-specificity helper, so the notebooks stay thin and the logic is testable WITHOUT a GPU:

    generate_binders_bindcraft(target, hotspots, n, tool="mock")     -> list[BinderDesign]
    generate_binders_rfdiffusion(target, hotspots, n, tool="mock")   -> list[BinderDesign]  (-> ProteinMPNN)
    af2_multimer(binder_seq, target, tool="mock")                    -> {plddt, pae_interaction, scrmsd, shape_complementarity}
    isoform_specificity(binder, isoform, tool="mock")                -> {pae_interaction, ...} (KRAS vs HRAS/NRAS)
    plus hotspot helpers: parse_hotspots(), hotspot_overlap().

This project reuses the BINDER-FAMILY TEMPLATE shape (Project 06, PD-L1): the mock backend is
deterministic, the real backends sit behind documented A100 TODOs, and ALL mock numbers are flagged
SYNTHETIC. The KRAS-specific addition is `isoform_specificity()` — the scientific heart here is not
just "does it bind KRAS?" but "does it bind KRAS and NOT HRAS/NRAS?" (and, ideally, the right ALLELE
and the right NUCLEOTIDE STATE).

DESIGN NOTE FOR STUDENTS
------------------------
Real binder generation (BindCraft / RFdiffusion+ProteinMPNN) and AF2-Multimer are heavy and want an
A100 (see MANUAL.md §2). Each backend's real path is a clearly-marked TODO you complete/verify on
Colab; the heavy import happens lazily INSIDE the function. The module imports fine here with no GPU
and no heavy packages. The `mock` backend is DETERMINISTIC (seeded by sequence/target/hotspots) so you
can develop and unit-test the plumbing — ranking, CSV assembly, the filter hand-off, the isoform panel
— before spending GPU time. NEVER present mock numbers as real results: they are SYNTHETIC by
construction. There are NO measured K_D values anywhere in this module.

KRAS-specific reality (read MANUAL.md §1):
  - KRAS has a small, relatively featureless, highly charged surface — a HARD binder target.
  - The druggable handholds are the switch I / switch II regions (and, for some alleles, an
    allele-specific pocket, e.g. the G12C cysteine or the G12D surface). Choose the epitope on purpose.
  - NUCLEOTIDE STATE matters: GDP-bound ("off") vs GTP/GppNHp-bound ("on") KRAS present different
    switch-region conformations. Model the state you are targeting.
  - SPECIFICITY vs HRAS/NRAS is the real challenge: the three isoforms are ~90%+ identical in the
    G-domain and nearly identical across the switch regions. A binder that hits all three is far less
    useful (and more toxic) than an allele-/isoform-selective one.

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

# The three RAS isoforms in the specificity panel. KRAS is the target; HRAS/NRAS are the
# off-targets you want the binder to AVOID. (Numbering/residues to verify on RCSB — see data/README.md.)
RAS_ISOFORMS = ("KRAS", "HRAS", "NRAS")


@dataclass
class BinderDesign:
    """One designed binder against the target (KRAS)."""
    design_id: str
    sequence: str
    paradigm: str                       # "bindcraft" | "rfdiffusion" | "mock"
    target: str = "KRAS"
    allele: str = "WT"                  # "WT" | "G12C" | "G12D" | ... (which KRAS allele you designed against)
    nucleotide_state: str = "GDP"       # "GDP" | "GTP" / "GppNHp" — the state you modeled
    hotspots: tuple = ()                # KRAS residues the binder was steered to (switch I/II or allele pocket)
    length: Optional[int] = None
    # filled by af2_multimer():
    plddt: Optional[float] = None
    pae_interaction: Optional[float] = None
    scrmsd: Optional[float] = None
    shape_complementarity: Optional[float] = None
    rosetta_dG: Optional[float] = None  # interface energy (REU); real value from PyRosetta/FreeBindCraft
    contact_residues: tuple = ()        # KRAS residues the binder actually contacts (for epitope/effector reasoning)
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
# Hotspot helpers
# --------------------------------------------------------------------------- #
def parse_hotspots(spec) -> tuple:
    """Normalize a hotspot spec into a sorted tuple of residue tokens.

    Accepts a list/tuple/comma-string like 'A32,A35,A38' or ['A32','A35']. For KRAS these are the
    residues of the chosen epitope — the switch I (~res 30-38) / switch II (~res 60-76) regions or an
    allele-specific pocket (e.g. the G12C cysteine). Derive them from the actual KRAS structure +
    nucleotide state you verify (see data/README.md); don't invent them.
    """
    if isinstance(spec, str):
        items = [s.strip() for s in spec.replace(";", ",").split(",") if s.strip()]
    else:
        items = [str(s).strip() for s in spec if str(s).strip()]
    return tuple(sorted(set(items)))


def hotspot_overlap(contact_residues, hotspots) -> float:
    """Fraction of the chosen-epitope hotspots the binder actually contacts.

    Higher ⇒ the binder covers more of the intended surface (e.g. the switch I/II patch). For an
    EFFECTOR-COMPETITION framing, switch-region coverage is a proxy for whether the binder could block
    RAF/effector engagement — a geometry proxy for the competition assay in notebook 04, NOT a
    guarantee of blockade.
    """
    hs = set(parse_hotspots(hotspots))
    if not hs:
        return 0.0
    contacts = set(parse_hotspots(contact_residues))
    return round(len(hs & contacts) / len(hs), 3)


# --------------------------------------------------------------------------- #
# Mock generators (deterministic, no GPU). Numbers are SYNTHETIC.
# --------------------------------------------------------------------------- #
def _mock_generate(paradigm: str, target: str, hotspots, n: int,
                   allele: str = "WT", nucleotide_state: str = "GDP") -> list[BinderDesign]:
    hs = parse_hotspots(hotspots)
    out = []
    for i in range(n):
        seed = _hashints(paradigm, target, allele, nucleotide_state, hs, i)
        length = 50 + (seed % 41)                       # 50-90 aa minibinder (KRAS needs a fair contact area)
        seq = _mock_sequence(seed, length)
        # Each paradigm gets a slightly different mock contact profile so the head-to-head
        # comparison in notebook 04 has structure (still SYNTHETIC).
        n_contact = 1 + (seed % max(1, len(hs))) if hs else 0
        contacts = tuple(hs[: n_contact]) if hs else ()
        out.append(BinderDesign(
            design_id=f"EXAMPLE_DATA_{paradigm}_{i:04d}",
            sequence=seq, paradigm=paradigm, target=target,
            allele=allele, nucleotide_state=nucleotide_state, hotspots=hs,
            length=length, contact_residues=contacts, synthetic=True,
            notes=[_MOCK_FLAG],
        ))
    return out


def generate_binders_bindcraft(target: str, hotspots, n: int = 50, tool: str = "mock",
                               binder_length=(50, 90), allele: str = "WT",
                               nucleotide_state: str = "GDP", **kwargs) -> list[BinderDesign]:
    """BindCraft (one-shot hallucination, AF2-Multimer in the loop). Paradigm #1.

    tool="mock"  -> deterministic SYNTHETIC binders (no GPU; develop the plumbing).
    tool="bindcraft" / "freebindcraft" -> real backend (A100; FreeBindCraft for free-tier fallback).
    `allele` / `nucleotide_state` record WHICH KRAS surface you targeted (e.g. G12C, GDP-bound).
    """
    tool = tool.lower()
    if tool == "mock":
        return _mock_generate("bindcraft", target, hotspots, n, allele, nucleotide_state)
    if tool in ("bindcraft", "freebindcraft"):
        # TODO (Colab, A100): run BindCraft against the cleaned KRAS target (right allele + nucleotide
        #   state) at the switch I/II (or allele-pocket) hotspots.
        #   repo: https://github.com/martinpacesa/BindCraft  (pin a commit)
        #   free-tier fallback: https://github.com/cytokineking/FreeBindCraft  (VERIFY it exists)
        #   key args: target_pdb (KRAS-GDP or KRAS-GppNHp), hotspot_residues=hotspots,
        #             binder_length, num_designs=n
        #   BindCraft already filters on interface confidence; still pass survivors through
        #   af2_multimer() + the shared filter so the head-to-head with RFdiffusion is apples-to-apples.
        #   A100 STRONGLY RECOMMENDED; free T4 -> FreeBindCraft + small num_designs only.
        raise NotImplementedError(
            "Wire up BindCraft/FreeBindCraft here (A100). See MANUAL.md §2 and the pinned repo; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, bindcraft, freebindcraft")


def generate_binders_rfdiffusion(target: str, hotspots, n: int = 1000, tool: str = "mock",
                                 binder_length=(50, 90), mpnn_temperature: float = 0.1,
                                 num_seq_per_backbone: int = 1, allele: str = "WT",
                                 nucleotide_state: str = "GDP", **kwargs) -> list[BinderDesign]:
    """RFdiffusion binder mode -> ProteinMPNN (diffuse backbone, then design sequence). Paradigm #2.

    tool="mock"        -> deterministic SYNTHETIC binders (no GPU).
    tool="rfdiffusion" -> real backend (A100 for 500-1000 backbones).
    """
    tool = tool.lower()
    if tool == "mock":
        return _mock_generate("rfdiffusion", target, hotspots, n, allele, nucleotide_state)
    if tool == "rfdiffusion":
        # TODO (Colab, A100): RFdiffusion binder mode -> ProteinMPNN -> AF2-Multimer.
        #   RFdiffusion:  https://github.com/RosettaCommons/RFdiffusion   (pin a commit)
        #   ColabDesign:  https://github.com/sokrypton/ColabDesign        (binder protocol + ProteinMPNN)
        #   1) diffuse n backbones with ppi.hotspot_res=hotspots (switch I/II or allele pocket),
        #      binderlen in binder_length range, against the right KRAS nucleotide state;
        #   2) ProteinMPNN over each backbone (temperature=mpnn_temperature, num_seq_per_backbone);
        #   3) AF2-Multimer re-prediction of each (binder, KRAS) complex -> pae_interaction.
        #   500-1000 backbones want A100/HPC; small batches OK on T4. AF2-Multimer is the slow step.
        raise NotImplementedError(
            "Wire up RFdiffusion binder mode + ProteinMPNN here (A100). See MANUAL.md §2; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, rfdiffusion")


# --------------------------------------------------------------------------- #
# AF2-Multimer scorer (the key binder metric is pae_interaction).
# --------------------------------------------------------------------------- #
def af2_multimer(binder_seq: str, target: str = "KRAS", tool: str = "mock",
                 hotspots=(), allele: str = "WT", nucleotide_state: str = "GDP", **kwargs) -> dict:
    """Score a (binder, target) complex. Returns the metrics the shared binder filter consumes:
        {plddt, pae_interaction, scrmsd, shape_complementarity}  (+ synthetic flag for mock).

    pae_interaction (AF2-Multimer) is THE key binder metric. tool="mock" returns deterministic
    SYNTHETIC numbers; tool="af2"/"colabfold" runs the real AF2-Multimer on Colab. `target` may be
    any RAS isoform ("KRAS"/"HRAS"/"NRAS") so the same scorer drives the specificity panel.
    """
    tool = tool.lower()
    if not binder_seq or any(c not in _AA for c in binder_seq.upper()):
        return dict(plddt=None, pae_interaction=None, scrmsd=None,
                    shape_complementarity=None, ok=False, error="invalid amino-acid sequence")
    if tool == "mock":
        h = _hashints("af2", target, allele, nucleotide_state, hotspots, binder_seq.upper())
        # Deterministic SYNTHETIC metrics in plausible-but-arbitrary ranges. These are NOT real.
        plddt = 70 + (h % 30)                       # 70-99
        pae_interaction = 4 + (h % 16)              # 4-19 (key binder metric; lower better)
        scrmsd = round(0.8 + (h % 350) / 100.0, 3)  # 0.8-4.3 Å
        sc = round(0.45 + (h % 45) / 100.0, 3)      # 0.45-0.89 shape complementarity
        return dict(plddt=float(plddt), pae_interaction=float(pae_interaction),
                    scrmsd=float(scrmsd), shape_complementarity=sc,
                    ok=True, synthetic=True, error=_MOCK_FLAG)
    if tool in ("af2", "colabfold", "af2_multimer", "multimer"):
        # TODO (Colab): run AF2-Multimer (ColabFold, model_type=multimer) on the (binder, KRAS)
        #   complex; parse mean inter-chain PAE -> pae_interaction, interface pLDDT -> plddt; compute
        #   scRMSD (designed vs predicted binder backbone) and shape complementarity.
        #   repo: https://github.com/sokrypton/ColabFold  (pin a commit). Small complexes OK on T4;
        #   campaign-scale prefers A100. This is usually the slowest step — batch overnight.
        raise NotImplementedError(
            "Wire up AF2-Multimer here (ColabFold, model_type=multimer). See MANUAL.md §2; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, af2/colabfold")


def score_designs(designs: list[BinderDesign], tool: str = "mock") -> list[BinderDesign]:
    """Run af2_multimer() over a list of BinderDesign and fill their metric fields in place."""
    for d in designs:
        m = af2_multimer(d.sequence, target=d.target, tool=tool, hotspots=d.hotspots,
                         allele=d.allele, nucleotide_state=d.nucleotide_state)
        if not m.get("ok", True):
            d.notes.append(f"af2_multimer failed: {m.get('error')}")
            continue
        d.plddt = m["plddt"]
        d.pae_interaction = m["pae_interaction"]
        d.scrmsd = m["scrmsd"]
        d.shape_complementarity = m["shape_complementarity"]
        if m.get("synthetic"):
            d.synthetic = True
    return designs


# --------------------------------------------------------------------------- #
# Isoform-specificity helper — the scientific heart of THIS project.
# --------------------------------------------------------------------------- #
def isoform_specificity(binder, isoform: str, tool: str = "mock", **kwargs) -> dict:
    """Score a binder against a chosen RAS ISOFORM (KRAS / HRAS / NRAS) to assess SELECTIVITY.

    The point of this project is not just "binds KRAS" but "binds KRAS and NOT HRAS/NRAS". This
    re-runs AF2-Multimer (mock here) against the requested isoform's structure and returns the same
    metric dict as af2_multimer(), tagged with the isoform. Compare `pae_interaction` for KRAS vs
    HRAS/NRAS: a SELECTIVE binder should score notably WORSE (higher pae_interaction) on the
    off-target isoforms. Because the three isoforms are nearly identical across the switch regions,
    achieving real selectivity is genuinely hard — report the delta honestly.

    `binder` may be a BinderDesign or a raw sequence string. All mock numbers are SYNTHETIC.
    """
    iso = str(isoform).upper()
    if iso not in RAS_ISOFORMS:
        return dict(isoform=iso, ok=False,
                    error=f"unknown isoform {iso!r}; options: {', '.join(RAS_ISOFORMS)}")
    seq = binder.sequence if isinstance(binder, BinderDesign) else str(binder)
    allele = getattr(binder, "allele", "WT")
    nuc = getattr(binder, "nucleotide_state", "GDP")
    hs = getattr(binder, "hotspots", ())
    # Score the (binder, isoform) complex with the SAME scorer used for the on-target — only the
    # `target` isoform changes. For the off-target isoforms we keep allele="WT" (HRAS/NRAS don't carry
    # the KRAS allele) but preserve the modeled nucleotide state.
    m = af2_multimer(seq, target=iso, tool=tool, hotspots=hs,
                     allele=allele if iso == "KRAS" else "WT", nucleotide_state=nuc)
    m["isoform"] = iso
    return m


def specificity_panel(binder, tool: str = "mock", isoforms=RAS_ISOFORMS) -> dict:
    """Run isoform_specificity() across all RAS isoforms and summarize selectivity for KRAS.

    Returns {per_isoform: {isoform -> pae_interaction}, kras_pae, best_offtarget_pae,
    selectivity_gap, selective}. `selectivity_gap = best_offtarget_pae - kras_pae` (positive ⇒ KRAS is
    the better-scoring target ⇒ some selectivity). This is a teaching proxy on top of AF2-Multimer
    confidence, NOT a measured selectivity — all mock numbers are SYNTHETIC.
    """
    per = {}
    for iso in isoforms:
        m = isoform_specificity(binder, iso, tool=tool)
        per[iso] = m.get("pae_interaction") if m.get("ok", True) else None
    kras = per.get("KRAS")
    offs = [v for k, v in per.items() if k != "KRAS" and v is not None]
    best_off = min(offs) if offs else None              # the off-target the binder hits BEST (worst case for us)
    gap = (best_off - kras) if (kras is not None and best_off is not None) else None
    return dict(
        per_isoform=per, kras_pae=kras, best_offtarget_pae=best_off,
        selectivity_gap=(round(gap, 2) if gap is not None else None),
        selective=(gap is not None and gap > 0),
        synthetic=(tool.lower() == "mock"),
    )


if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps). All numbers are SYNTHETIC.
    # EXAMPLE switch-I/II hotspots on KRAS — verify yours from the actual structure + nucleotide state.
    HOTSPOTS = "A32,A35,A38,A60,A71"   # EXAMPLE_DATA: switch I (~30-38) + switch II (~60-76) residues
    bc = generate_binders_bindcraft("KRAS", HOTSPOTS, n=5, tool="mock", allele="G12C", nucleotide_state="GDP")
    rf = generate_binders_rfdiffusion("KRAS", HOTSPOTS, n=5, tool="mock", allele="G12C", nucleotide_state="GDP")
    score_designs(bc, tool="mock")
    score_designs(rf, tool="mock")
    print(f"BindCraft mock designs:   {len(bc)}")
    print(f"RFdiffusion mock designs: {len(rf)}")
    d = bc[0]
    print("example design:", d.design_id, "allele=", d.allele, "state=", d.nucleotide_state,
          "len=", d.length, "pae_interaction=", d.pae_interaction, "scrmsd=", d.scrmsd,
          "sc=", d.shape_complementarity, "synthetic=", d.synthetic)
    print("epitope coverage (example):", hotspot_overlap(d.contact_residues, HOTSPOTS))
    panel = specificity_panel(d, tool="mock")
    print("isoform specificity panel (SYNTHETIC):", panel["per_isoform"],
          "selectivity_gap=", panel["selectivity_gap"], "selective=", panel["selective"])
    print("REMINDER: every number above is SYNTHETIC (mock) — never report it as a real result. "
          "No K_D anywhere.")
