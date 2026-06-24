"""
binder_tools.py — binder-design + AF2-Multimer wrappers for Project 10 (NDM-1 active-site binders).

This project follows the BINDER-FAMILY TEMPLATE (Project 06, PD-L1). The scientific twist here is
that the target is a **di-zinc metallo-beta-lactamase active site** (NDM-1), so:
  - sequence design near the active-site rim uses **LigandMPNN (Zn-aware)**, not vanilla ProteinMPNN,
    and the two catalytic Zn2+ ions must be PRESERVED in target prep (they are part of the epitope);
  - the goal is not just to BIND but to INHIBIT — to OCCLUDE substrate (carbapenem) access — so this
    module adds two mechanism helpers the PD-L1 template did not need:
        occlusion_score(binder, active_site, tool="mock")          -> does it block substrate access?
        offtarget_specificity(binder, human_metalloenzyme, tool)   -> off-target human Zn-enzyme risk

Clean, import-safe entry points so the notebooks stay thin and the logic is testable WITHOUT a GPU:

    generate_binders_bindcraft(target, hotspots, n, tool="mock")     -> list[BinderDesign]
    generate_binders_rfdiffusion(target, hotspots, n, tool="mock")   -> list[BinderDesign]  (-> LigandMPNN)
    af2_multimer(binder_seq, target, tool="mock")                    -> {plddt, pae_interaction, scrmsd, sc}
    occlusion_score(binder, active_site, tool="mock")                -> {occlusion, ...}  (mechanism)
    offtarget_specificity(binder, human_metalloenzyme, tool="mock")  -> {specificity, ...}  (off-target)
    plus hotspot helpers: parse_hotspots(), hotspot_overlap().

DESIGN NOTE FOR STUDENTS
------------------------
Real binder generation (BindCraft / RFdiffusion+LigandMPNN) and AF2-Multimer are heavy and want an
A100 (see MANUAL.md §2). Each backend's real path is a clearly-marked TODO you complete/verify on
Colab; the heavy import happens lazily INSIDE the function. The module imports fine here with no GPU
and no heavy packages. The `mock` backend is DETERMINISTIC (seeded by sequence/target/hotspots) so
you can develop and unit-test the plumbing — ranking, CSV assembly, the filter hand-off, the
occlusion/specificity analysis — before spending GPU time. NEVER present mock numbers as real
results: they are SYNTHETIC by construction. There are NO fabricated IC50s anywhere in this module —
binding/occlusion proxies are NOT inhibition; the wet-lab inhibition assay (notebook 05) measures that.

Pinned upstreams (verify they still exist — version-verify cell; pin commits, they change):
  BindCraft      https://github.com/martinpacesa/BindCraft
  FreeBindCraft  https://github.com/cytokineking/FreeBindCraft   (free-tier fallback — VERIFY)
  RFdiffusion    https://github.com/RosettaCommons/RFdiffusion
  LigandMPNN     https://github.com/dauparas/LigandMPNN          (Zn-aware sequence design near the metal site)
  ColabFold      https://github.com/sokrypton/ColabFold          (AF2-Multimer)
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
    """One designed binder against the target (NDM-1 active-site rim)."""
    design_id: str
    sequence: str
    paradigm: str                       # "bindcraft" | "rfdiffusion" | "mock"
    target: str = "NDM1"
    hotspots: tuple = ()                # NDM-1 active-site-rim residues the binder was steered to
    length: Optional[int] = None
    # filled by af2_multimer():
    plddt: Optional[float] = None
    pae_interaction: Optional[float] = None
    scrmsd: Optional[float] = None
    shape_complementarity: Optional[float] = None
    rosetta_dG: Optional[float] = None  # interface energy (REU); real value from PyRosetta/FreeBindCraft
    contact_residues: tuple = ()        # NDM-1 residues the binder actually contacts (for rim coverage)
    # filled by occlusion_score() (mechanism — does it block substrate access?):
    occlusion: Optional[float] = None   # 0–1 fraction of the substrate-access channel occluded
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
# Hotspot helpers (the active-site RIM is the competitive epitope here)
# --------------------------------------------------------------------------- #
def parse_hotspots(spec) -> tuple:
    """Normalize a hotspot spec into a sorted tuple of residue tokens.

    Accepts a list/tuple/comma-string like 'A120,A220,A228' or ['A120','A220']. For NDM-1 these are
    the **active-site-rim** residues (the walls of the substrate-access groove around the di-zinc
    site) — derive them from the cleaned di-zinc structure (see data/README.md). Do NOT mutate the
    Zn-coordinating residues themselves (the His/Cys/Asp ligands) — the binder sits on the RIM and
    occludes substrate access; it does not replace the metal ligands.
    """
    if isinstance(spec, str):
        items = [s.strip() for s in spec.replace(";", ",").split(",") if s.strip()]
    else:
        items = [str(s).strip() for s in spec if str(s).strip()]
    return tuple(sorted(set(items)))


def hotspot_overlap(contact_residues, hotspots) -> float:
    """Fraction of the active-site-rim hotspots the binder actually contacts (rim-coverage proxy).

    Higher ⇒ the binder covers more of the substrate-access rim ⇒ more likely to OCCLUDE carbapenem
    access ⇒ more likely to INHIBIT. This is a geometry proxy for the occlusion analysis in notebook
    04 and the inhibition assay in notebook 05 — it is NOT a guarantee of inhibition (binding ≠
    inhibition; only the enzyme-kinetics assay measures inhibition).
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
        # TODO (Colab, A100): run BindCraft against the cleaned NDM-1 target (di-zinc PRESERVED) at
        #   the active-site-rim hotspots.
        #   repo: https://github.com/martinpacesa/BindCraft  (pin a commit)
        #   free-tier fallback: https://github.com/cytokineking/FreeBindCraft  (VERIFY it exists)
        #   key args: target_pdb (Zn ions kept as heteroatoms), hotspot_residues=hotspots (the rim),
        #             binder_length, num_designs=n
        #   NOTE: AF2/BindCraft do not natively model Zn2+ — keep the metal as a target heteroatom and
        #   confirm the binder docks onto the rim that walls the substrate channel (not a distal patch).
        #   BindCraft already filters on interface confidence; still pass survivors through
        #   af2_multimer() + the shared filter so the head-to-head with RFdiffusion is apples-to-apples.
        #   A100 STRONGLY RECOMMENDED; free T4 -> FreeBindCraft + small num_designs only.
        raise NotImplementedError(
            "Wire up BindCraft/FreeBindCraft here (A100, di-zinc preserved). See MANUAL.md §2 and the "
            "pinned repo; develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, bindcraft, freebindcraft")


def generate_binders_rfdiffusion(target: str, hotspots, n: int = 1000, tool: str = "mock",
                                 binder_length=(40, 80), mpnn_temperature: float = 0.1,
                                 num_seq_per_backbone: int = 1, **kwargs) -> list[BinderDesign]:
    """RFdiffusion binder mode -> LigandMPNN (Zn-aware) (diffuse backbone, then design sequence). Paradigm #2.

    For NDM-1 we use **LigandMPNN** (not vanilla ProteinMPNN) so the sequence design near the
    active-site rim is aware of the di-zinc ligand context (Dauparas 2024).

    tool="mock"        -> deterministic SYNTHETIC binders (no GPU).
    tool="rfdiffusion" -> real backend (A100 for 500-1000 backbones).
    """
    tool = tool.lower()
    if tool == "mock":
        return _mock_generate("rfdiffusion", target, hotspots, n)
    if tool == "rfdiffusion":
        # TODO (Colab, A100): RFdiffusion binder mode -> LigandMPNN (Zn-aware) -> AF2-Multimer.
        #   RFdiffusion:  https://github.com/RosettaCommons/RFdiffusion   (pin a commit)
        #   LigandMPNN:   https://github.com/dauparas/LigandMPNN          (Zn-aware; pin a commit)
        #   ColabDesign:  https://github.com/sokrypton/ColabDesign        (binder protocol)
        #   1) diffuse n backbones with ppi.hotspot_res=hotspots (the active-site RIM), binderlen in
        #      binder_length range, with the di-zinc target structure (Zn kept as heteroatoms);
        #   2) LigandMPNN over each backbone (temperature=mpnn_temperature, num_seq_per_backbone),
        #      passing the Zn ions so interface residues near the metal are designed metal-aware;
        #   3) AF2-Multimer re-prediction of each (binder, NDM-1) complex -> pae_interaction.
        #   500-1000 backbones want A100/HPC; small batches OK on T4. AF2-Multimer is the slow step.
        raise NotImplementedError(
            "Wire up RFdiffusion binder mode + LigandMPNN (Zn-aware) here (A100). See MANUAL.md §2; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, rfdiffusion")


# --------------------------------------------------------------------------- #
# AF2-Multimer scorer (the key binder metric is pae_interaction).
# --------------------------------------------------------------------------- #
def af2_multimer(binder_seq: str, target: str = "NDM1", tool: str = "mock",
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
        # TODO (Colab): run AF2-Multimer (ColabFold, model_type=multimer) on the (binder, NDM-1)
        #   complex; parse mean inter-chain PAE -> pae_interaction, interface pLDDT -> plddt; compute
        #   scRMSD (designed vs predicted binder backbone) and shape complementarity.
        #   NOTE: AF2 does not place Zn2+; keep the metal as a target heteroatom and sanity-check that
        #   the predicted binder sits over the substrate-access rim, not elsewhere on NDM-1.
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


# --------------------------------------------------------------------------- #
# MECHANISM #1 — occlusion: does the binder BLOCK substrate (carbapenem) access?
# --------------------------------------------------------------------------- #
def occlusion_score(binder, active_site, tool: str = "mock") -> dict:
    """Does the binder OCCLUDE the substrate-access channel over the di-zinc active site?

    This is the inhibition-mechanism proxy that distinguishes a *blocker* from a mere *sticker*: a
    binder can have a great interface yet sit off the substrate groove and never inhibit. Returns a
    fraction in 0–1 (higher = more of the carbapenem-access channel is occluded) plus a coarse
    `occludes` boolean.

    binder       : a BinderDesign (uses its contact_residues + hotspots) OR a contact-residue spec.
    active_site  : the active-site-rim residue spec (the substrate-access channel walls).
    tool="mock"  : deterministic SYNTHETIC geometry proxy (rim coverage + a hashed pocket-fit term).
    tool="pocket"/"vina": real pocket-geometry / docking backend (A100-noted TODO).

    IMPORTANT: occlusion is a STRUCTURAL proxy. Occlusion ≠ inhibition. Only the nitrocefin /
    carbapenem-hydrolysis kinetics assay (notebook 05) measures inhibition (IC50). No IC50 is
    produced here — that would be fabricated.
    """
    tool = (tool or "mock").lower()
    # Accept either a BinderDesign or a raw contact spec.
    contacts = getattr(binder, "contact_residues", binder)
    bid = getattr(binder, "design_id", "anon")
    seq = getattr(binder, "sequence", "")
    rim = parse_hotspots(active_site)
    cover = hotspot_overlap(contacts, rim)          # fraction of the rim contacted (0–1)
    if tool == "mock":
        # Combine rim coverage with a deterministic "pocket-fit" term so two designs with the same
        # coverage still rank differently in the dry run. ALL SYNTHETIC.
        h = _hashints("occl", bid, seq, rim)
        pocket_fit = (h % 100) / 100.0              # 0–1 SYNTHETIC pocket-complementarity term
        occlusion = round(0.6 * cover + 0.4 * pocket_fit, 3)
        return dict(design_id=bid, occlusion=occlusion, rim_coverage=cover,
                    pocket_fit=round(pocket_fit, 3), occludes=bool(occlusion >= 0.5),
                    ok=True, synthetic=True,
                    note="SYNTHETIC occlusion proxy — occlusion is NOT inhibition; see notebook 05 assay")
    if tool in ("pocket", "vina", "docking"):
        # TODO (Colab/A100): real substrate-occlusion analysis.
        #   1) Build the (binder, NDM-1) complex (AF2-Multimer output, di-zinc kept).
        #   2) Measure the open volume of the substrate-access channel over the di-zinc site WITH and
        #      WITHOUT the binder (e.g., fpocket/CASTp pocket volume, or a SASA-of-the-channel proxy);
        #      occlusion = 1 - V_with_binder / V_without_binder.
        #   3) OPTIONAL: dock a carbapenem (e.g., meropenem) with AutoDock Vina into the channel in the
        #      presence of the binder; loss of a productive pose near the di-zinc site corroborates
        #      occlusion. Vina/fpocket: https://github.com/ccsb-scripps/AutoDock-Vina .
        #   Report occlusion as a STRUCTURAL hypothesis; the kinetics assay (nb 05) tests inhibition.
        raise NotImplementedError(
            "Wire up the real occlusion/pocket-volume (and optional carbapenem docking) backend here. "
            "See MANUAL.md §2; develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, pocket/vina")


def score_occlusion(designs: list[BinderDesign], active_site, tool: str = "mock") -> list[BinderDesign]:
    """Run occlusion_score() over a list of BinderDesign and fill `.occlusion` in place."""
    for d in designs:
        r = occlusion_score(d, active_site, tool=tool)
        if r.get("ok", True):
            d.occlusion = r["occlusion"]
            if r.get("synthetic"):
                d.synthetic = True
    return designs


# --------------------------------------------------------------------------- #
# MECHANISM #2 — off-target specificity vs HUMAN metalloenzymes
# --------------------------------------------------------------------------- #
def offtarget_specificity(binder, human_metalloenzyme, tool: str = "mock") -> dict:
    """Will the binder cross-react with a HUMAN Zn/metalloenzyme (an off-target liability)?

    A di-zinc-site binder that also hits human carbonic anhydrase, MMPs, glyoxalase II, or other
    human metalloenzymes is a safety problem. Returns a `specificity` score in 0–1 (higher = MORE
    NDM-1-selective, i.e. LOWER predicted off-target binding) and the predicted off-target
    pae_interaction it is derived from.

    binder              : a BinderDesign (uses its sequence) OR a raw sequence string.
    human_metalloenzyme : a label/id for the human off-target (e.g. "CA2", "MMP9", "GLO2").
    tool="mock"         : deterministic SYNTHETIC proxy (a hashed off-target pae vs the on-target pae).
    tool="af2"          : real off-target AF2-Multimer (binder vs the human enzyme) backend (A100 TODO).

    This is a SPECIFICITY COUNTER-TEST, mirroring the off-target human-metalloenzyme CONTROL in the
    inhibition assay (notebook 05). Higher specificity = safer. SYNTHETIC for mock; never report as real.
    """
    tool = (tool or "mock").lower()
    seq = getattr(binder, "sequence", binder)
    bid = getattr(binder, "design_id", "anon")
    on_target_pae = getattr(binder, "pae_interaction", None)
    if tool == "mock":
        h = _hashints("offtarget", bid, seq, human_metalloenzyme)
        # SYNTHETIC predicted off-target interface error (Å). Higher off-target pae = MORE selective.
        offtarget_pae = 6 + (h % 18)                  # 6–23 Å SYNTHETIC
        # Map to a 0–1 specificity: large off-target pae (poor off-target binding) -> high specificity.
        specificity = round(min(1.0, max(0.0, (offtarget_pae - 6) / 17.0)), 3)
        return dict(design_id=bid, off_target=str(human_metalloenzyme),
                    specificity=specificity, offtarget_pae=float(offtarget_pae),
                    on_target_pae=on_target_pae, selective=bool(specificity >= 0.5),
                    ok=True, synthetic=True,
                    note="SYNTHETIC specificity proxy — confirm with a real off-target panel on Colab")
    if tool in ("af2", "colabfold", "af2_multimer", "multimer"):
        # TODO (Colab/A100): model (binder, human_metalloenzyme) with AF2-Multimer and parse the
        #   off-target pae_interaction. Compare to the on-target NDM-1 pae_interaction: a SELECTIVE
        #   binder has a much WORSE (higher) off-target pae. Build a small panel of human metalloenzymes
        #   (e.g. carbonic anhydrase II 1CA2, an MMP, glyoxalase II) and report specificity per design.
        #   This is the in-silico mirror of the off-target-metalloenzyme CONTROL in the nb-05 assay.
        raise NotImplementedError(
            "Wire up the off-target AF2-Multimer panel (human metalloenzymes) here (A100). "
            "See MANUAL.md §2; develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, af2/colabfold")


if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps). All numbers are SYNTHETIC.
    # EXAMPLE active-site-rim hotspots — VERIFY yours from the cleaned di-zinc NDM-1 structure.
    HOTSPOTS = "A120,A220,A228"   # EXAMPLE NDM-1 rim residues — replace with verified rim residues
    bc = generate_binders_bindcraft("NDM1", HOTSPOTS, n=5, tool="mock")
    rf = generate_binders_rfdiffusion("NDM1", HOTSPOTS, n=5, tool="mock")
    score_designs(bc, tool="mock")
    score_designs(rf, tool="mock")
    score_occlusion(bc, HOTSPOTS, tool="mock")
    print(f"BindCraft mock designs:   {len(bc)}")
    print(f"RFdiffusion mock designs: {len(rf)}")
    d = bc[0]
    print("example design:", d.design_id, "len=", d.length,
          "pae_interaction=", d.pae_interaction, "scrmsd=", d.scrmsd,
          "sc=", d.shape_complementarity, "occlusion=", d.occlusion, "synthetic=", d.synthetic)
    print("rim-coverage overlap (example):", hotspot_overlap(d.contact_residues, HOTSPOTS))
    occ = occlusion_score(d, HOTSPOTS, tool="mock")
    print("occlusion (example):", occ["occlusion"], "occludes?", occ["occludes"], "—", occ["note"])
    spec = offtarget_specificity(d, "CA2", tool="mock")
    print("off-target specificity vs human CA2 (example):", spec["specificity"], "selective?", spec["selective"])
    print("REMINDER: every number above is SYNTHETIC (mock) — never report it as a real result. "
          "Binding/occlusion ≠ inhibition; the IC50 comes only from the nb-05 assay.")
