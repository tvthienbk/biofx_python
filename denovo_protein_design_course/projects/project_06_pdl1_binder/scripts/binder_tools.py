"""
binder_tools.py — binder-design + AF2-Multimer wrappers for Project 06 (PD-L1 mini-binders).

Goal: clean, import-safe entry points for the two design paradigms and the AF2-Multimer scorer, so
the notebooks stay thin and the logic is testable WITHOUT a GPU:

    generate_binders_bindcraft(target, hotspots, n, tool="mock")     -> list[BinderDesign]
    generate_binders_rfdiffusion(target, hotspots, n, tool="mock")   -> list[BinderDesign]  (-> ProteinMPNN)
    af2_multimer(binder_seq, target, tool="mock")                    -> {plddt, pae_interaction, scrmsd, shape_complementarity}
    plus hotspot helpers: parse_hotspots(), hotspot_overlap().

This file is the BINDER-FAMILY TEMPLATE (Projects 07-13, 23 follow this shape): keep the mock
deterministic, the real backends behind documented TODOs with A100 notes, and ALL mock numbers
flagged SYNTHETIC.

DESIGN NOTE FOR STUDENTS
------------------------
Real binder generation (BindCraft / RFdiffusion+ProteinMPNN) and AF2-Multimer are heavy and want an
A100 (see MANUAL.md §2). Each backend's real path is a clearly-marked TODO you complete/verify on
Colab; the heavy import happens lazily INSIDE the function. The module imports fine here with no GPU
and no heavy packages. The `mock` backend is DETERMINISTIC (seeded by sequence/target/hotspots) so you
can develop and unit-test the plumbing — ranking, CSV assembly, the filter hand-off — before spending
GPU time. NEVER present mock numbers as real results: they are SYNTHETIC by construction.

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


@dataclass
class BinderDesign:
    """One designed binder against the target (PD-L1)."""
    design_id: str
    sequence: str
    paradigm: str                       # "bindcraft" | "rfdiffusion" | "mock"
    target: str = "PDL1"
    hotspots: tuple = ()                # PD-L1 residues the binder was steered to (the PD-1 face)
    length: Optional[int] = None
    # filled by af2_multimer():
    plddt: Optional[float] = None
    pae_interaction: Optional[float] = None
    scrmsd: Optional[float] = None
    shape_complementarity: Optional[float] = None
    rosetta_dG: Optional[float] = None  # interface energy (REU); real value from PyRosetta/FreeBindCraft
    contact_residues: tuple = ()        # PD-L1 residues the binder actually contacts (for epitope competition)
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

    Accepts a list/tuple/comma-string like 'A56,A66,A115' or ['A56','A66']. These are the PD-L1
    residues on the PD-1-binding face (the competitive epitope) — derive them from the PD-1/PD-L1
    interface in the complex (see data/README.md), don't invent them.
    """
    if isinstance(spec, str):
        items = [s.strip() for s in spec.replace(";", ",").split(",") if s.strip()]
    else:
        items = [str(s).strip() for s in spec if str(s).strip()]
    return tuple(sorted(set(items)))


def hotspot_overlap(contact_residues, hotspots) -> float:
    """Fraction of the PD-1-face hotspots the binder actually contacts (epitope-competition proxy).

    Higher ⇒ the binder covers more of the PD-1 footprint ⇒ more likely to BLOCK PD-1. This is a
    geometry proxy for the competition assay in notebook 04 — not a guarantee of blockade.
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
        length = 40 + (seed % 41)                       # 40–80 aa minibinder
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
                               binder_length=(40, 80), **kwargs) -> list[BinderDesign]:
    """BindCraft (one-shot hallucination, AF2-Multimer in the loop). Paradigm #1.

    tool="mock"  -> deterministic SYNTHETIC binders (no GPU; develop the plumbing).
    tool="bindcraft" / "freebindcraft" -> real backend (A100; FreeBindCraft for free-tier fallback).
    """
    tool = tool.lower()
    if tool == "mock":
        return _mock_generate("bindcraft", target, hotspots, n)
    if tool in ("bindcraft", "freebindcraft"):
        # TODO (Colab, A100): run BindCraft against the cleaned PD-L1 target at the PD-1-face hotspots.
        #   repo: https://github.com/martinpacesa/BindCraft  (pin a commit)
        #   free-tier fallback: https://github.com/cytokineking/FreeBindCraft  (VERIFY it exists)
        #   key args: target_pdb, hotspot_residues=hotspots, binder_length, num_designs=n
        #   BindCraft already filters on interface confidence; still pass survivors through
        #   af2_multimer() + the shared filter so the head-to-head with RFdiffusion is apples-to-apples.
        #   A100 STRONGLY RECOMMENDED; free T4 -> FreeBindCraft + small num_designs only.
        raise NotImplementedError(
            "Wire up BindCraft/FreeBindCraft here (A100). See MANUAL.md §2 and the pinned repo; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, bindcraft, freebindcraft")


def generate_binders_rfdiffusion(target: str, hotspots, n: int = 1000, tool: str = "mock",
                                 binder_length=(40, 80), mpnn_temperature: float = 0.1,
                                 num_seq_per_backbone: int = 1, **kwargs) -> list[BinderDesign]:
    """RFdiffusion binder mode -> ProteinMPNN (diffuse backbone, then design sequence). Paradigm #2.

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
        #   1) diffuse n backbones with ppi.hotspot_res=hotspots, binderlen in binder_length range;
        #   2) ProteinMPNN over each backbone (temperature=mpnn_temperature, num_seq_per_backbone);
        #   3) AF2-Multimer re-prediction of each (binder, PD-L1) complex -> pae_interaction.
        #   500-1000 backbones want A100/HPC; small batches OK on T4. AF2-Multimer is the slow step.
        raise NotImplementedError(
            "Wire up RFdiffusion binder mode + ProteinMPNN here (A100). See MANUAL.md §2; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, rfdiffusion")


# --------------------------------------------------------------------------- #
# AF2-Multimer scorer (the key binder metric is pae_interaction).
# --------------------------------------------------------------------------- #
def af2_multimer(binder_seq: str, target: str = "PDL1", tool: str = "mock",
                 hotspots=(), **kwargs) -> dict:
    """Score a (binder, target) complex. Returns the metrics the shared binder filter consumes:
        {plddt, pae_interaction, scrmsd, shape_complementarity}  (+ synthetic flag for mock).

    pae_interaction (AF2-Multimer) is THE key binder metric. tool="mock" returns deterministic
    SYNTHETIC numbers; tool="af2"/"colabfold" runs the real AF2-Multimer on Colab.
    """
    tool = tool.lower()
    if not binder_seq or any(c not in _AA for c in binder_seq.upper()):
        return dict(plddt=None, pae_interaction=None, scrmsd=None,
                    shape_complementarity=None, ok=False, error="invalid amino-acid sequence")
    if tool == "mock":
        h = _hashints("af2", target, hotspots, binder_seq.upper())
        # Deterministic SYNTHETIC metrics in plausible-but-arbitrary ranges. These are NOT real.
        plddt = 70 + (h % 30)                       # 70–99
        pae_interaction = 4 + (h % 16)              # 4–19 (key binder metric; lower better)
        scrmsd = round(0.8 + (h % 350) / 100.0, 3)  # 0.8–4.3 Å
        sc = round(0.45 + (h % 45) / 100.0, 3)      # 0.45–0.89 shape complementarity
        return dict(plddt=float(plddt), pae_interaction=float(pae_interaction),
                    scrmsd=float(scrmsd), shape_complementarity=sc,
                    ok=True, synthetic=True, error=_MOCK_FLAG)
    if tool in ("af2", "colabfold", "af2_multimer", "multimer"):
        # TODO (Colab): run AF2-Multimer (ColabFold, model_type=multimer) on the (binder, PD-L1)
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
        m = af2_multimer(d.sequence, target=d.target, tool=tool, hotspots=d.hotspots)
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


if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps). All numbers are SYNTHETIC.
    HOTSPOTS = "A56,A66,A115"   # EXAMPLE PD-1-face hotspots — verify yours from the PD-1/PD-L1 interface
    bc = generate_binders_bindcraft("PDL1", HOTSPOTS, n=5, tool="mock")
    rf = generate_binders_rfdiffusion("PDL1", HOTSPOTS, n=5, tool="mock")
    score_designs(bc, tool="mock")
    score_designs(rf, tool="mock")
    print(f"BindCraft mock designs:   {len(bc)}")
    print(f"RFdiffusion mock designs: {len(rf)}")
    d = bc[0]
    print("example design:", d.design_id, "len=", d.length,
          "pae_interaction=", d.pae_interaction, "scrmsd=", d.scrmsd,
          "sc=", d.shape_complementarity, "synthetic=", d.synthetic)
    print("epitope-competition overlap (example):",
          hotspot_overlap(d.contact_residues, HOTSPOTS))
    print("REMINDER: every number above is SYNTHETIC (mock) — never report it as a real result.")
