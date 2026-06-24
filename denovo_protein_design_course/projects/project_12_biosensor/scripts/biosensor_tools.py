"""
biosensor_tools.py — binder + conformational-switch / split-reporter wrappers for Project 12
(De Novo Binder → Biosensor).

Goal: clean, import-safe entry points so the notebooks stay thin and the logic is testable WITHOUT a
GPU. This project sits on top of the BINDER-FAMILY TEMPLATE (Project 06, PD-L1): the binder module is
the same two-paradigm workflow, and we ADD a switch / split-reporter layer that turns *binding* into
*signal*:

    # --- binder module (reused, same shape as Project 06) ---
    generate_binders_bindcraft(target, hotspots, n, tool="mock")    -> list[BinderDesign]
    generate_binders_rfdiffusion(target, hotspots, n, tool="mock")  -> list[BinderDesign]  (-> ProteinMPNN)
    af2_multimer(binder_seq, target, tool="mock")                   -> {plddt, pae_interaction, scrmsd, sc}
    score_designs(designs, tool="mock")                             -> fills metric fields in place
    parse_hotspots(spec), hotspot_overlap(contacts, hotspots)

    # --- switch / biosensor module (NEW for Project 12) ---
    design_switch(scaffold, reporter, tool="mock")                  -> SwitchDesign
    model_two_state(construct, analyte_present, tool="mock")        -> {on_signal, off_signal, dynamic_range}
    integrate_binder_switch(binder, switch, tool="mock")            -> BiosensorConstruct

The scientific heart here is NOT just "does it bind?" but "does binding flip a clean ON/OFF signal?".
Coupling a binder to a switch with a usable dynamic range is HARD: there is a real trade-off between
binder affinity and switch dynamic range, and most integrated constructs need iteration.

DESIGN NOTE FOR STUDENTS
------------------------
Real binder generation (BindCraft / RFdiffusion+ProteinMPNN), AF2-Multimer, and two-state switch
modeling are heavy and want an A100 (see MANUAL.md §2). Each real backend is a clearly-marked TODO you
complete/verify on Colab; the heavy import happens lazily INSIDE the function. This module imports fine
here with NO GPU and NO heavy packages. The `mock` backend is DETERMINISTIC (seeded by the inputs) so
you can develop and unit-test the plumbing — ranking, CSV assembly, the filter hand-off, the
ON/OFF reasoning — before spending GPU time.

NEVER present mock numbers as real results: they are SYNTHETIC by construction. There are NO measured
luminescence values, NO measured limits of detection (LOD), and NO measured dissociation constants
(K_D) anywhere in this module. on_signal / off_signal / dynamic_range from the mock are teaching
stand-ins, not assay readouts.

Biosensor reality (read MANUAL.md §1):
  - Two switch families are in scope:
      * SPLIT-REPORTER (e.g. split-luciferase / NanoBiT, or split-fluorophore for FRET): the reporter
        is broken into two fragments; binding brings them together (or apart) -> luminescence/FRET.
      * CONFORMATIONAL SWITCH (LOCKR-style "cage + latch + key"): the analyte (or a key peptide it
        exposes) displaces a latch, releasing a functional/reporter element.
  - DYNAMIC RANGE = on_signal / off_signal (fold-change). A sensor with a great binder but a leaky OFF
    state (high background) is a POOR sensor. Report dynamic range, not just "it binds".
  - There is a genuine AFFINITY vs DYNAMIC-RANGE trade-off: a very tight binder can lock the switch ON
    regardless of analyte (no switching); too weak and the ON state never forms. Tune deliberately.
  - LOD (limit of detection) depends on dynamic range AND assay noise; you ESTIMATE it from a planned
    dose-response, you do not read it off a mock number.

Pinned upstreams (verify they still exist — version-verify cell; pin commits, they change):
  BindCraft      https://github.com/martinpacesa/BindCraft
  FreeBindCraft  https://github.com/cytokineking/FreeBindCraft   (free-tier fallback — VERIFY)
  RFdiffusion    https://github.com/RosettaCommons/RFdiffusion   (binder mode + scaffold/switch generation)
  ColabDesign    https://github.com/sokrypton/ColabDesign         (RFdiffusion-binder + ProteinMPNN)
  ColabFold      https://github.com/sokrypton/ColabFold           (AF2-Multimer / two-state AF2 modeling)

Switch / split-reporter references (read references/reading_list.md):
  - Langan et al. 2019 (LOCKR, de novo protein switches, Nature)
  - Quijano-Rubio et al. 2021 (de novo biosensors, Nature)
  - Dixon et al. 2016 (NanoBiT split-luciferase)
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional

# 20 canonical amino acids, used to synthesize deterministic mock sequences.
_AA = "ACDEFGHIKLMNPQRSTVWY"
_MOCK_FLAG = "SYNTHETIC — mock backend, not a real design/prediction/assay"

# Switch families the biosensor module knows about. SPLIT-REPORTER vs CONFORMATIONAL (LOCKR-style).
SWITCH_FAMILIES = ("split_reporter", "lockr")
# Reporters the split-reporter family can use (luminescence or FRET).
REPORTERS = ("split_luciferase", "nanobit", "split_fluorophore_fret")


# =========================================================================== #
# BINDER MODULE (same shape as Project 06's binder_tools.py — the family template)
# =========================================================================== #
@dataclass
class BinderDesign:
    """One designed binder against the analyte/biomarker target."""
    design_id: str
    sequence: str
    paradigm: str                       # "bindcraft" | "rfdiffusion" | "mock"
    target: str = "ANALYTE"             # the chosen biomarker / analyte (student choice)
    hotspots: tuple = ()                # analyte residues the binder was steered to (the epitope)
    length: Optional[int] = None
    # filled by af2_multimer():
    plddt: Optional[float] = None
    pae_interaction: Optional[float] = None
    scrmsd: Optional[float] = None
    shape_complementarity: Optional[float] = None
    rosetta_dG: Optional[float] = None  # interface energy (REU); real value from PyRosetta/FreeBindCraft
    contact_residues: tuple = ()        # analyte residues the binder actually contacts (epitope coverage)
    synthetic: bool = False             # True ⇒ numbers are mock/EXAMPLE_DATA, never report as real
    notes: list = field(default_factory=list)

    def as_row(self) -> dict:
        return asdict(self)


def _hashints(*parts) -> int:
    """Stable integer hash of the inputs (NOT Python's salted hash) for deterministic mock numbers."""
    h = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(h, 16)


def _mock_sequence(seed_int: int, length: int) -> str:
    """Deterministic pseudo-random amino-acid sequence (mock binder/scaffold)."""
    seq = []
    x = seed_int
    for _ in range(length):
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        seq.append(_AA[x % len(_AA)])
    return "".join(seq)


def parse_hotspots(spec) -> tuple:
    """Normalize a hotspot spec into a sorted tuple of residue tokens.

    Accepts 'A12,A45,A60' or ['A12','A45']. These are the analyte residues on the chosen epitope —
    derive them from the analyte structure / a co-complex (see data/README.md), don't invent them.
    """
    if isinstance(spec, str):
        items = [s.strip() for s in spec.replace(";", ",").split(",") if s.strip()]
    else:
        items = [str(s).strip() for s in spec if str(s).strip()]
    return tuple(sorted(set(items)))


def hotspot_overlap(contact_residues, hotspots) -> float:
    """Fraction of the target epitope hotspots the binder actually contacts (epitope-coverage proxy).

    For a biosensor, covering the intended epitope matters because the binder must engage the analyte
    in a way that mechanically couples to the switch. Geometry proxy — not a guarantee.
    """
    hs = set(parse_hotspots(hotspots))
    if not hs:
        return 0.0
    contacts = set(parse_hotspots(contact_residues))
    return round(len(hs & contacts) / len(hs), 3)


def _mock_generate(paradigm: str, target: str, hotspots, n: int) -> list[BinderDesign]:
    hs = parse_hotspots(hotspots)
    out = []
    for i in range(n):
        seed = _hashints(paradigm, target, hs, i)
        length = 40 + (seed % 41)                       # 40–80 aa minibinder
        seq = _mock_sequence(seed, length)
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
    """BindCraft (one-shot hallucination, AF2-Multimer in the loop). Binder paradigm #1.

    tool="mock"  -> deterministic SYNTHETIC binders (no GPU; develop the plumbing).
    tool="bindcraft" / "freebindcraft" -> real backend (A100; FreeBindCraft for free-tier fallback).
    """
    tool = tool.lower()
    if tool == "mock":
        return _mock_generate("bindcraft", target, hotspots, n)
    if tool in ("bindcraft", "freebindcraft"):
        # TODO (Colab, A100): run BindCraft against the cleaned analyte target at the chosen epitope.
        #   repo: https://github.com/martinpacesa/BindCraft  (pin a commit)
        #   free-tier fallback: https://github.com/cytokineking/FreeBindCraft  (VERIFY it exists)
        #   key args: target_pdb, hotspot_residues=hotspots, binder_length, num_designs=n
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
        #   500-1000 backbones want A100/HPC; small batches OK on T4. AF2-Multimer is the slow step.
        raise NotImplementedError(
            "Wire up RFdiffusion binder mode + ProteinMPNN here (A100). See MANUAL.md §2; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, rfdiffusion")


def af2_multimer(binder_seq: str, target: str = "ANALYTE", tool: str = "mock",
                 hotspots=(), **kwargs) -> dict:
    """Score a (binder, analyte) complex. Returns the metrics the shared binder filter consumes:
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
        # TODO (Colab): run AF2-Multimer (ColabFold, model_type=multimer) on the (binder, analyte)
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


# =========================================================================== #
# SWITCH / BIOSENSOR MODULE (NEW for Project 12)
# =========================================================================== #
@dataclass
class SwitchDesign:
    """One designed conformational switch / split-reporter scaffold (no binder coupled yet).

    A switch is the transduction element: it converts a binding event into a measurable change. For a
    split-reporter, that is reconstitution of luminescence/FRET; for a LOCKR-style cage, it is
    latch displacement that releases a functional/reporter element.
    """
    switch_id: str
    family: str                          # "split_reporter" | "lockr"
    reporter: str                        # one of REPORTERS (split_reporter family) or "" (lockr key/latch)
    scaffold: str                        # scaffold name/source (RFdiffusion scaffold or a LOCKR cage)
    sequence: str = ""                   # mock scaffold sequence (SYNTHETIC)
    # intrinsic, analyte-independent switch quality (filled by design_switch, mock = SYNTHETIC):
    closed_plddt: Optional[float] = None # confidence of the OFF/closed state model
    open_plddt: Optional[float] = None   # confidence of the ON/open state model
    toggle_score: Optional[float] = None # 0–1 separation between the two state models (higher better)
    background_leak: Optional[float] = None  # OFF-state signal leak (0–1; lower better)
    synthetic: bool = False
    notes: list = field(default_factory=list)

    def as_row(self) -> dict:
        return asdict(self)


@dataclass
class BiosensorConstruct:
    """A binder integrated with a switch — the actual sensor whose ON/OFF behaviour we reason about."""
    construct_id: str
    binder_id: str
    switch_id: str
    family: str
    reporter: str
    target: str = "ANALYTE"
    binder_sequence: str = ""
    # carried binder metrics (so the construct can be filtered/ranked like a binder, design_type="binder"):
    plddt: Optional[float] = None
    pae_interaction: Optional[float] = None
    scrmsd: Optional[float] = None
    shape_complementarity: Optional[float] = None
    rosetta_dG: Optional[float] = None
    # two-state readout (filled by model_two_state; mock = SYNTHETIC, never a real assay number):
    on_signal: Optional[float] = None    # modeled signal WITH analyte (arbitrary units, SYNTHETIC)
    off_signal: Optional[float] = None   # modeled signal WITHOUT analyte (arbitrary units, SYNTHETIC)
    dynamic_range: Optional[float] = None  # on_signal / off_signal (fold-change; the key sensor metric)
    synthetic: bool = False
    notes: list = field(default_factory=list)

    def as_row(self) -> dict:
        return asdict(self)


def design_switch(scaffold: str, reporter: str, family: str = "split_reporter",
                  n: int = 1, tool: str = "mock", **kwargs) -> list[SwitchDesign]:
    """Design (or borrow) a switch/split-reporter scaffold. Returns n candidate SwitchDesigns.

    family="split_reporter" -> a split-luciferase / NanoBiT / split-FRET reporter scaffold.
    family="lockr"          -> a LOCKR-style cage+latch (reporter="" ; the "key" is exposed on binding).

    tool="mock"        -> deterministic SYNTHETIC switch scaffolds (no GPU; develop the plumbing).
    tool="rfdiffusion" -> real backend: RFdiffusion scaffold/switch generation -> ProteinMPNN (A100).
    tool="lockr"       -> borrow/adapt a published LOCKR cage (Langan 2019) as the scaffold.
    """
    tool = tool.lower()
    family = family.lower()
    if family not in SWITCH_FAMILIES:
        raise ValueError(f"unknown switch family {family!r}; options: {SWITCH_FAMILIES}")
    if family == "split_reporter" and reporter and reporter.lower() not in REPORTERS:
        raise ValueError(f"unknown reporter {reporter!r}; options: {REPORTERS}")

    if tool == "mock":
        out = []
        for i in range(n):
            seed = _hashints("switch", family, reporter, scaffold, i)
            seq = _mock_sequence(seed, 60 + (seed % 60))         # 60–119 aa mock scaffold
            # Deterministic SYNTHETIC intrinsic-quality numbers. NOT real.
            closed_plddt = 70 + (seed % 28)                      # 70–97
            open_plddt = 70 + ((seed >> 3) % 28)                 # 70–97
            toggle = round(0.30 + (seed % 60) / 100.0, 3)        # 0.30–0.89 (state separation)
            leak = round(0.05 + (seed % 35) / 100.0, 3)          # 0.05–0.39 (OFF-state leak)
            out.append(SwitchDesign(
                switch_id=f"EXAMPLE_DATA_switch_{family}_{i:03d}",
                family=family, reporter=(reporter if family == "split_reporter" else ""),
                scaffold=scaffold, sequence=seq,
                closed_plddt=float(closed_plddt), open_plddt=float(open_plddt),
                toggle_score=toggle, background_leak=leak, synthetic=True, notes=[_MOCK_FLAG],
            ))
        return out
    if tool in ("rfdiffusion", "lockr"):
        # TODO (Colab, A100): generate/borrow the switch scaffold.
        #   - tool="rfdiffusion": RFdiffusion scaffold/switch generation -> ProteinMPNN sequence design
        #     (https://github.com/RosettaCommons/RFdiffusion , https://github.com/sokrypton/ColabDesign).
        #   - tool="lockr": adapt a published LOCKR cage+latch (Langan et al. 2019) as the scaffold,
        #     graft the reporter / functional element, redesign the latch interface.
        #   Then model the closed (OFF) and open (ON) states (see model_two_state) and score the toggle.
        #   A100 recommended for scaffold generation + two-state AF2 modeling.
        raise NotImplementedError(
            "Wire up RFdiffusion scaffold / LOCKR-cage switch design here (A100). See MANUAL.md §2; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, rfdiffusion, lockr")


def integrate_binder_switch(binder: BinderDesign, switch: SwitchDesign,
                            tool: str = "mock", **kwargs) -> BiosensorConstruct:
    """Couple a binder to a switch -> a BiosensorConstruct (the integrated sensor).

    The integration concept: binding the analyte must mechanically toggle the switch (displace the
    LOCKR latch, or bring the split-reporter halves together). This function assembles the construct
    record and carries the binder metrics; call model_two_state() to get the ON/OFF readout.

    tool="mock" -> assemble the construct deterministically (no GPU). tool="af2"/"rfdiffusion" ->
    real integrated-construct modeling (A100): build the fusion, model the coupled geometry.
    """
    tool = tool.lower()
    cid = f"{binder.design_id}__{switch.switch_id}"
    construct = BiosensorConstruct(
        construct_id=cid, binder_id=binder.design_id, switch_id=switch.switch_id,
        family=switch.family, reporter=switch.reporter, target=binder.target,
        binder_sequence=binder.sequence,
        plddt=binder.plddt, pae_interaction=binder.pae_interaction, scrmsd=binder.scrmsd,
        shape_complementarity=binder.shape_complementarity, rosetta_dG=binder.rosetta_dG,
        synthetic=bool(binder.synthetic or switch.synthetic),
        notes=list(switch.notes),
    )
    if tool == "mock":
        return construct
    if tool in ("af2", "colabfold", "rfdiffusion"):
        # TODO (Colab, A100): model the INTEGRATED construct (binder fused/grafted onto the switch).
        #   - Build the fusion (linker length/rigidity matters: too floppy -> leaky OFF; too rigid ->
        #     no toggle). Model the coupled geometry with AF2 (and a two-state protocol; see
        #     model_two_state). Check the binder still folds + still presents its epitope in-context.
        #   A100 recommended. The integration is the hard part — most constructs need linker iteration.
        raise NotImplementedError(
            "Wire up integrated-construct modeling here (A100). See MANUAL.md §2; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, af2/colabfold, rfdiffusion")


def model_two_state(construct: BiosensorConstruct, analyte_present: bool = True,
                    tool: str = "mock", **kwargs) -> dict:
    """Model the sensor in one state and return its signal. Call twice (analyte present/absent) to get
    the ON and OFF signals; dynamic_range = on/off.

    Returns {state, signal, ok, synthetic}. The convenience wrapper two_state_readout() below calls
    this for both states and fills construct.on_signal / off_signal / dynamic_range.

    tool="mock" -> deterministic SYNTHETIC signals (arbitrary units; NOT an assay readout). tool="af2"
    -> a TWO-STATE AF2 protocol (model the OFF/closed and ON/open conformations; A100) [extension].
    """
    tool = tool.lower()
    if tool == "mock":
        # Deterministic SYNTHETIC signal. The mock ties the signal to the construct id + state so the
        # ON state is (usually) brighter than the OFF state, with leak — to exercise the dynamic-range
        # reasoning. These are arbitrary units, NOT luminescence / FRET measurements.
        base = _hashints("twostate", construct.construct_id)
        leak = 0.05 + (base % 35) / 100.0              # 0.05–0.39 OFF-state leak fraction
        on = 80.0 + (base % 120)                       # 80–199 a.u. (ON, with analyte) SYNTHETIC
        off = round(on * leak, 3)                       # OFF = leak fraction of ON SYNTHETIC
        signal = on if analyte_present else off
        return dict(state=("ON" if analyte_present else "OFF"),
                    signal=round(float(signal), 3), ok=True, synthetic=True, error=_MOCK_FLAG)
    if tool in ("af2", "colabfold", "two_state"):
        # TODO (Colab, A100): TWO-STATE modeling [extension].
        #   Model the construct WITHOUT analyte (OFF/closed: split halves apart / latch in place) and
        #   WITH analyte (ON/open: halves together / latch displaced). Use AF2 multi-state tricks
        #   (templates, state-specific MSAs) or a LOCKR-style cage+key model. Derive a relative ON vs
        #   OFF signal proxy from the predicted state populations + interface confidence.
        #   These are MODELED proxies, NOT measured luminescence — the assay (notebook 05) measures it.
        raise NotImplementedError(
            "Wire up two-state AF2 modeling here (A100) [extension]. See MANUAL.md §2; "
            "develop with tool='mock' first.")
    raise ValueError(f"unknown tool {tool!r}; options: mock, af2/colabfold/two_state")


def two_state_readout(construct: BiosensorConstruct, tool: str = "mock") -> BiosensorConstruct:
    """Run model_two_state() for BOTH states, fill on_signal/off_signal/dynamic_range in place.

    dynamic_range = on_signal / off_signal (fold-change) is THE key sensor metric — a high-affinity
    binder with a leaky OFF state (low dynamic range) is a poor sensor. Mock numbers are SYNTHETIC.
    """
    on = model_two_state(construct, analyte_present=True, tool=tool)
    off = model_two_state(construct, analyte_present=False, tool=tool)
    if not (on.get("ok") and off.get("ok")):
        construct.notes.append("two_state modeling failed")
        return construct
    construct.on_signal = on["signal"]
    construct.off_signal = off["signal"]
    construct.dynamic_range = round(on["signal"] / max(off["signal"], 1e-6), 3)
    if on.get("synthetic") or off.get("synthetic"):
        construct.synthetic = True
    return construct


def estimate_lod(dynamic_range: float, assay_cv: float = 0.10) -> dict:
    """Teaching-grade LOD *planning* helper: a rough detectability flag from dynamic range + assay CV.

    This is NOT a measured limit of detection. It encodes the intuition that LOD improves with higher
    dynamic range and lower assay noise (coefficient of variation). Use it to PRIORITIZE which
    constructs to test and to design the dose-response in notebook 05 — never report it as a measured
    LOD. A real LOD comes from a fitted dose-response with replicates and a blank (no-analyte) control.
    """
    if dynamic_range is None or dynamic_range <= 1.0:
        return dict(detectable=False, reason="dynamic range <= 1 (no switching)", synthetic=True)
    # Heuristic: need the ON/OFF separation to clear a few assay-noise widths to be detectable.
    separation_in_cv = (dynamic_range - 1.0) / max(assay_cv, 1e-3)
    return dict(detectable=separation_in_cv >= 3.0,
                separation_in_cv=round(float(separation_in_cv), 2),
                note="PLANNING heuristic only — NOT a measured LOD; fit a real dose-response in lab.",
                synthetic=True)


if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps). All numbers are SYNTHETIC.
    TARGET = "ANALYTE"                       # the student's chosen biomarker (verify accession on RCSB)
    HOTSPOTS = "A12,A45,A60"                  # EXAMPLE epitope residues — verify from the analyte structure
    # 1) binder module (reused family workflow)
    bc = generate_binders_bindcraft(TARGET, HOTSPOTS, n=4, tool="mock")
    rf = generate_binders_rfdiffusion(TARGET, HOTSPOTS, n=4, tool="mock")
    score_designs(bc, tool="mock"); score_designs(rf, tool="mock")
    # 2) switch module (new): design a split-reporter switch + a LOCKR-style cage
    sw_split = design_switch("rfdiff_scaffold_01", reporter="split_luciferase",
                             family="split_reporter", n=2, tool="mock")
    sw_lockr = design_switch("lockr_cage_01", reporter="", family="lockr", n=2, tool="mock")
    # 3) integrate the best binder with a switch and reason about ON/OFF
    construct = integrate_binder_switch(bc[0], sw_split[0], tool="mock")
    two_state_readout(construct, tool="mock")
    print("binder pools:", len(bc), "bindcraft +", len(rf), "rfdiffusion")
    print("switches    :", len(sw_split), "split_reporter +", len(sw_lockr), "lockr")
    print("construct   :", construct.construct_id)
    print("  on_signal=", construct.on_signal, " off_signal=", construct.off_signal,
          " dynamic_range=", construct.dynamic_range, " (SYNTHETIC)")
    print("  LOD planning flag:", estimate_lod(construct.dynamic_range, assay_cv=0.10))
    print("REMINDER: every number above is SYNTHETIC (mock) — never report it as a real result/assay.")
