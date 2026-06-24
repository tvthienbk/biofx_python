"""
multistate_tools.py — two-state backbone generation, multi-state sequence design, and
two-state validation helpers for Project 22 (Conformational-Switch / Multi-State Protein).

Goal: a small set of functions the notebooks import so the multi-state campaign logic is
testable and the notebooks stay thin. A conformational switch is ONE sequence that is
compatible with TWO different backbones (state A and state B) and toggles between them in
response to a trigger (pH, ligand, light, ...). The functions:

    generate_two_states(topology, trigger, tool="mock")            -> TwoStateDef (state_a, state_b)
    multistate_mpnn(state_a, state_b, n, tool="mock")              -> list[SharedSequence]
    af2_predict_state(seq, state, tool="mock")                     -> StatePrediction {plddt, scrmsd_to_state}
    energy_gap(state_a_pred, state_b_pred)                         -> EnergyGap

DESIGN NOTE FOR STUDENTS
------------------------
The real backends are heavy and environment-specific (RFdiffusion via ColabDesign for the two
backbones, ProteinMPNN run in a *tied / multi-state* mode across both states, AF2/ColabFold to
predict BOTH states from one sequence, OpenMM for transition-plausibility MD), so each is an adapter
you complete/verify on Colab. Heavy imports happen *inside* the function (lazily), so this module is
import-safe with NO GPU and NO heavy packages installed: it imports fine anywhere, and the real
backends raise a clear, actionable error if a dependency is missing.

A deterministic `mock` backend lets you build and unit-test the *plumbing* (the campaign loop, the
results CSV schema, the energy-gap reasoning, the figures) before you spend GPU time. The mock
numbers are SYNTHETIC by construction — they encode the project's realistic priors (multi-state
design is VERY hard; a single sequence rarely satisfies both states well; one state usually folds
better than the other; the energy gap is small and noisy) ONLY so the example figures look
qualitatively right. **NEVER present mock numbers as real designs** — every mock record is flagged
`synthetic=True` and ids/sequences are prefixed/labelled `EXAMPLE_DATA_`.

COMPUTE HONESTY
---------------
This is a frontier problem and the most expensive workflow in the course. Two-backbone generation
(RFdiffusion ×2) + multi-state ProteinMPNN + predicting BOTH states with AF2 + transition MD
realistically needs an **A100 / HPC**. A free Colab **T4** can run a *small fallback* (a few designs,
short backbones, ESMFold triage instead of AF2) just to exercise the pipeline. Do not plan the full
multi-state campaign on a T4.

Fill in / verify the TODOs against the current RFdiffusion (ColabDesign), ProteinMPNN, ColabFold,
and OpenMM APIs at the start of the course (these libraries change — pin commits and log them).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, asdict, field
from typing import Optional

# Pinned upstreams (verify with the version-verify cell in 00_setup / 02_generate; tools change):
#   RFdiffusion : https://github.com/RosettaCommons/RFdiffusion   (pin a commit/tag here)
#   ColabDesign : https://github.com/sokrypton/ColabDesign        (pin a commit/tag here)
#   ProteinMPNN : https://github.com/dauparas/ProteinMPNN         (pin a commit/tag here)
#   OpenMM      : https://github.com/openmm/openmm                (pin a release here)

# Conceptual reference for the multi-state design idea (sequence compatible with multiple states):
#   Langan et al. 2019 (LOCKR, Nature) — de novo switchable proteins; the canonical switch reference.

# A switch must fold to EACH state self-consistently AND switch between them, so we apply the
# monomer foldability bar to BOTH states and ALSO reason about the energy gap between them.
SELF_CONSISTENT_SCRMSD = 2.0   # per-state foldability bar (Å); a switch must satisfy this for A AND B
SWITCH_PLDDT = 85.0            # per-state confidence bar (mean pLDDT; NOT stability)
# Energy-gap window (teaching-grade, dimensionless "relative score" units — NOT kcal/mol):
#   too LARGE a gap => the high-energy state is never populated (no switch);
#   too SMALL a gap => the two states are indistinct (no defined OFF/ON).
# The switchable window is a band, not a single threshold. Tune per project from your own data.
SWITCH_GAP_MIN = 0.5
SWITCH_GAP_MAX = 6.0

TRIGGERS = ("pH", "ligand", "light", "temperature")
TOPOLOGIES = ("hinge", "helical_bundle", "loop_to_helix", "domain_swap")


# --------------------------------------------------------------------------- #
# Records
# --------------------------------------------------------------------------- #
@dataclass
class StateBackbone:
    """One conformational state's backbone (geometry only — no sequence yet)."""
    state: str                          # "A" | "B"
    topology: str                       # hinge | helical_bundle | loop_to_helix | domain_swap
    length: int
    pdb_path: Optional[str] = None
    tool: str = "mock"
    seed: int = 0
    synthetic: bool = False
    notes: str = ""

    def as_row(self) -> dict:
        return asdict(self)


@dataclass
class TwoStateDef:
    """A two-state design problem: two backbones + the trigger that toggles between them."""
    state_a: StateBackbone
    state_b: StateBackbone
    trigger: str                        # pH | ligand | light | temperature
    trigger_detail: str = ""            # e.g. "His-rich interface protonates below pH 6"
    tool: str = "mock"
    synthetic: bool = False
    notes: str = ""


@dataclass
class SharedSequence:
    """One candidate sequence designed to be compatible with BOTH state A and state B."""
    design_id: str
    sequence: str
    n_states: int = 2
    # multi-state MPNN's own confidence that the sequence fits both backbones (lower = better fit):
    mpnn_score_a: Optional[float] = None     # per-state negative log-likelihood-ish score
    mpnn_score_b: Optional[float] = None
    tool: str = "mock"
    seed: int = 0
    synthetic: bool = False
    error: Optional[str] = None

    def as_row(self) -> dict:
        return asdict(self)


@dataclass
class StatePrediction:
    """AF2 (or ESMFold) prediction of ONE sequence folded toward ONE target state."""
    state: str                          # "A" | "B"
    plddt: Optional[float] = None       # mean pLDDT of the refold (0–100); NOT stability
    scrmsd_to_state: Optional[float] = None  # Cα-RMSD to that state's designed backbone (Å)
    tool: str = "mock"
    synthetic: bool = False
    ok: bool = True
    error: Optional[str] = None


@dataclass
class EnergyGap:
    """Relative-energy reasoning between the two predicted states (teaching-grade proxy)."""
    gap: Optional[float] = None         # |proxy_energy(B) - proxy_energy(A)| in relative units
    favored_state: Optional[str] = None  # which state the proxy thinks is lower-energy (more stable)
    switchable: Optional[bool] = None    # gap within [SWITCH_GAP_MIN, SWITCH_GAP_MAX]?
    tool: str = "mock"
    synthetic: bool = False
    note: str = ""


# --------------------------------------------------------------------------- #
# Backend: generate_two_states  (RFdiffusion ×2 -> two backbones for one switch)
# --------------------------------------------------------------------------- #
def _generate_two_states_real(topology: str, trigger: str, length: int,
                              seed: int, out_dir: str) -> TwoStateDef:
    """RFdiffusion (via ColabDesign) generates the TWO state backbones for the switch.

    COMPUTE: two backbone-generation runs; A100/HPC for anything beyond a tiny fallback.
    """
    try:
        # TODO (verify the API/commit and pin it in 00_setup):
        #   State A and State B are two related-but-distinct backbones the SAME sequence must adopt.
        #   Two common routes:
        #     (a) generate state A unconditionally / from a motif, then generate state B as a
        #         conformational variant (e.g. partial diffusion / a hinge re-fold of A), OR
        #     (b) take a known two-state template pair (LOCKR latch/cage, a hinge open/closed pair)
        #         and use RFdiffusion to build de novo backbones matching each.
        #   For each: contigs for the chosen `length`, inference.num_designs, diffuser.T ~ 50,
        #   inference.output_prefix = out_dir/state_{A,B}. Collect the two PDBs into StateBackbone.
        raise NotImplementedError(
            "Wire up two-state backbone generation: produce backbone A and a distinct backbone B "
            "that a single sequence must satisfy (partial diffusion / hinge variant of A, or a "
            "LOCKR-style latch/cage pair). NOTE: two RFdiffusion runs — A100/HPC for the campaign.")
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            f"two-state generation backend not available ({e!r}). Use tool='mock' for the plumbing, "
            f"or install RFdiffusion (ColabDesign) on a GPU runtime — A100/HPC for the real campaign.")


def _generate_two_states_mock(topology: str, trigger: str, length: int,
                              seed: int, out_dir: str) -> TwoStateDef:
    """Deterministic fake two-state definition so the campaign loop runs with no GPU.
    SYNTHETIC — no PDB is written; the two states are placeholders for the plumbing."""
    a = StateBackbone(state="A", topology=topology, length=length, pdb_path=None, tool="mock",
                      seed=seed, synthetic=True, notes="SYNTHETIC mock backbone A — not a real design")
    b = StateBackbone(state="B", topology=topology, length=length, pdb_path=None, tool="mock",
                      seed=seed, synthetic=True, notes="SYNTHETIC mock backbone B — not a real design")
    return TwoStateDef(
        state_a=a, state_b=b, trigger=trigger,
        trigger_detail=f"TEMPLATE: {trigger}-triggered toggle between two {topology} states (fill in)",
        tool="mock", synthetic=True,
        notes="SYNTHETIC mock two-state definition — replace with real RFdiffusion backbones")


def generate_two_states(topology: str = "hinge", trigger: str = "pH",
                        tool: str = "mock", length: int = 100, seed: int = 0,
                        out_dir: str = "results/two_state") -> TwoStateDef:
    """Generate the two conformational-state backbones for a switch + record its trigger.

    topology ∈ {hinge, helical_bundle, loop_to_helix, domain_swap}.
    trigger  ∈ {pH, ligand, light, temperature}.
    tool     ∈ {mock, rfdiffusion}.
    """
    if topology not in TOPOLOGIES:
        raise ValueError(f"topology must be one of {TOPOLOGIES}, got {topology!r}")
    if trigger not in TRIGGERS:
        raise ValueError(f"trigger must be one of {TRIGGERS}, got {trigger!r}")
    if length <= 0:
        raise ValueError("length must be positive")
    tool = tool.lower()
    if tool in ("rfdiffusion", "rfdiff", "real"):
        return _generate_two_states_real(topology, trigger, length, seed, out_dir)
    if tool == "mock":
        return _generate_two_states_mock(topology, trigger, length, seed, out_dir)
    raise ValueError(f"unknown tool {tool!r}; options: mock, rfdiffusion")


# --------------------------------------------------------------------------- #
# Backend: multistate_mpnn  (ProteinMPNN tied/ensemble across BOTH states)
# --------------------------------------------------------------------------- #
def _multistate_mpnn_real(state_a: StateBackbone, state_b: StateBackbone,
                          n: int, seed: int, tool: str) -> list[SharedSequence]:
    """ProteinMPNN in MULTI-STATE (tied / ensemble) mode: one sequence scored against BOTH backbones.

    Returns `n` candidate sequences, each with a per-state MPNN score.
    """
    try:
        # TODO (verify APIs / pin commits in 00_setup):
        #   Multi-state design ties the SAME residue identities across both backbones and optimizes
        #   the sequence for the (e.g. averaged) likelihood under BOTH states at once. With the
        #   ColabDesign / ProteinMPNN stack this is done by supplying both PDBs as a tied set
        #   (tied_positions across the two states) so each position shares one amino acid, and
        #   sampling --num_seq_per_target n at --sampling_temp ~0.1.
        #   Record the per-state score (negative log-likelihood-ish) for A and B separately so the
        #   notebook can reason about the trade-off (a good switch fits BOTH, not just one).
        raise NotImplementedError(
            "Wire up multi-state ProteinMPNN: tie residue identities across backbone A and backbone "
            "B, optimize one sequence under BOTH, sample n sequences, and record per-state scores. "
            "A single sequence satisfying two states well is RARE — expect low yield (see MANUAL §1).")
    except Exception as e:  # noqa: BLE001
        return [SharedSequence(
            design_id="ERROR", sequence="", tool=tool, synthetic=False,
            error=f"{e!r}; run tool='mock' or install ProteinMPNN (multi-state mode)")]


def _multistate_mpnn_mock(state_a: StateBackbone, state_b: StateBackbone,
                          n: int, seed: int) -> list[SharedSequence]:
    """Deterministic synthetic shared sequences + per-state scores that ENCODE the realistic prior
    that multi-state design is hard: most sequences fit ONE state much better than the other, and
    only a few balance both. SYNTHETIC — never present as real designs."""
    aa = "ACDEFGHIKLMNPQRSTVWY"
    out = []
    L = max(state_a.length, state_b.length)
    for i in range(n):
        h = hashlib.sha256(f"{state_a.topology}|{state_b.topology}|{seed}|{i}".encode()).hexdigest()
        hi = int(h, 16)
        # deterministic pseudo-sequence (labelled EXAMPLE_DATA — NOT a real design)
        seq = "".join(aa[(hi >> (3 * j)) % 20] for j in range(L))
        # per-state scores: lower = better fit. Make them anti-correlated-ish so balancing is hard.
        jitter = (hi % 1000) / 1000.0
        score_a = round(0.8 + 1.2 * jitter, 3)
        score_b = round(0.8 + 1.2 * (1.0 - jitter), 3)   # when A fits well, B tends to fit worse
        out.append(SharedSequence(
            design_id=f"EXAMPLE_DATA_switch_{state_a.topology}_{i:03d}",
            sequence=seq, n_states=2, mpnn_score_a=score_a, mpnn_score_b=score_b,
            tool="mock", seed=seed, synthetic=True,
            error="SYNTHETIC — mock multi-state MPNN sequence, not a real design"))
    return out


def multistate_mpnn(state_a: StateBackbone, state_b: StateBackbone, n: int = 8,
                    tool: str = "mock", seed: int = 0) -> list[SharedSequence]:
    """Design `n` sequences each compatible with BOTH state_a and state_b (multi-state MPNN).

    tool ∈ {mock, proteinmpnn}. With the real tool, ProteinMPNN ties residue identities across the
    two backbones and optimizes one shared sequence under both (see MANUAL.md §2).
    """
    if not isinstance(state_a, StateBackbone) or not isinstance(state_b, StateBackbone):
        raise TypeError("state_a and state_b must be StateBackbone objects")
    if n <= 0:
        raise ValueError("n must be positive")
    tool = tool.lower()
    if tool == "mock":
        return _multistate_mpnn_mock(state_a, state_b, n, seed)
    if tool in ("proteinmpnn", "mpnn", "real"):
        return _multistate_mpnn_real(state_a, state_b, n, seed, tool)
    raise ValueError(f"unknown tool {tool!r}; options: mock, proteinmpnn")


# --------------------------------------------------------------------------- #
# Backend: af2_predict_state  (predict ONE sequence toward ONE state)
# --------------------------------------------------------------------------- #
def _af2_predict_state_real(seq: str, state: StateBackbone, tool: str) -> StatePrediction:
    """AF2/ColabFold (or ESMFold) prediction of `seq`, scored against `state`'s backbone.

    For a switch you call this for BOTH states (same sequence, two reference backbones) so you can
    ask: does the ONE sequence fold to A *and* to B? (AF2 returns a single model; you compare it to
    each state's backbone, and/or bias prediction toward each state — see the TODO.)
    """
    try:
        # TODO (verify APIs / pin commits in 00_setup):
        #   1. Predict seq with AF2/ColabFold (or ESMFold for fast triage).
        #   2. scrmsd_to_state = filtering_pipeline.ca_rmsd(state.pdb_path, predicted_pdb)
        #   3. plddt = mean pLDDT of the prediction.
        #   CAVEAT: AF2 predicts a single dominant state and may NOT capture both — this is the
        #   central honest limitation of in-silico multi-state validation (see MANUAL §1, §5).
        #   Where possible, bias/seed prediction toward each state (templates, initial guess) and
        #   report BOTH the unbiased prediction and the state-biased ones.
        raise NotImplementedError(
            "Wire up AF2/ESMFold prediction of the sequence and ca_rmsd vs THIS state's backbone. "
            "Run it for state A and state B. Note AF2 may only return one state — report that.")
    except Exception as e:  # noqa: BLE001
        return StatePrediction(state=state.state, tool=tool, ok=False,
                               error=f"{e!r}; run tool='mock' or install the predictor backend")


def _af2_predict_state_mock(seq: str, state: StateBackbone) -> StatePrediction:
    """Deterministic synthetic scRMSD/pLDDT per state that ENCODE the realistic prior: a single
    sequence usually fits ONE state better than the other, and the harder state often fails the
    foldability bar. SYNTHETIC — never present as a real prediction."""
    h = int(hashlib.sha256(f"{seq}|{state.state}|{state.topology}".encode()).hexdigest(), 16)
    jitter = (h % 1000) / 1000.0
    # state A tends to be the "designed-for" state (folds a bit better); state B is harder.
    state_penalty = 0.0 if state.state == "A" else 0.7
    topo_base = {"hinge": 0.9, "helical_bundle": 0.7, "loop_to_helix": 1.2,
                 "domain_swap": 1.4}.get(state.topology, 1.0)
    scrmsd = round(topo_base + state_penalty + 1.3 * jitter, 2)     # ~0.7 .. ~3.4 Å
    plddt = round(max(40.0, 95.0 - 8.0 * scrmsd + 4.0 * (1 - jitter)), 1)
    return StatePrediction(state=state.state, plddt=plddt, scrmsd_to_state=scrmsd,
                           tool="mock", synthetic=True,
                           error="SYNTHETIC — mock per-state prediction, not a real AF2 run")


def af2_predict_state(seq: str, state: StateBackbone, tool: str = "mock") -> StatePrediction:
    """Predict `seq` and score it against ONE state's backbone -> {plddt, scrmsd_to_state}.

    tool ∈ {mock, af2, colabfold, esmfold}. Call once per state (A and B) to validate the switch.
    """
    if not isinstance(state, StateBackbone):
        raise TypeError("state must be a StateBackbone object")
    if not seq:
        return StatePrediction(state=getattr(state, "state", "?"), ok=False,
                               error="empty sequence")
    tool = tool.lower()
    if tool == "mock":
        return _af2_predict_state_mock(seq, state)
    if tool in ("af2", "colabfold", "esmfold"):
        return _af2_predict_state_real(seq, state, tool)
    raise ValueError(f"unknown tool {tool!r}; options: mock, af2, esmfold")


# --------------------------------------------------------------------------- #
# Energy-gap reasoning between the two predicted states
# --------------------------------------------------------------------------- #
def energy_gap(state_a_pred: StatePrediction, state_b_pred: StatePrediction) -> EnergyGap:
    """Teaching-grade relative-energy reasoning between the two predicted states.

    A switch needs the two states to be CLOSE enough in energy to interconvert on a trigger, but
    DISTINCT enough to have a defined OFF/ON. We use a transparent proxy from the per-state
    self-consistency: a state that the sequence fits better (lower scRMSD, higher pLDDT) is treated
    as lower relative energy. The gap is the absolute difference of these proxy energies; we flag it
    `switchable` if it falls inside the band [SWITCH_GAP_MIN, SWITCH_GAP_MAX].

    IMPORTANT: this proxy is in arbitrary relative units, NOT kcal/mol, and is NOT a free energy.
    For real ΔΔG you need physics (FoldX/Rosetta) or MD free-energy methods — see MANUAL §1/§5.
    The point here is to teach the *reasoning*, not to produce a real thermodynamic number.
    """
    def proxy_energy(p: StatePrediction) -> Optional[float]:
        if p is None or p.scrmsd_to_state is None:
            return None
        # higher scRMSD and lower pLDDT => worse fit => higher relative energy
        e = 2.0 * p.scrmsd_to_state
        if p.plddt is not None:
            e += (100.0 - p.plddt) / 20.0
        return round(e, 3)

    ea, eb = proxy_energy(state_a_pred), proxy_energy(state_b_pred)
    synth = bool(getattr(state_a_pred, "synthetic", False) or getattr(state_b_pred, "synthetic", False))
    if ea is None or eb is None:
        return EnergyGap(gap=None, favored_state=None, switchable=None, tool="mock" if synth else "real",
                         synthetic=synth, note="missing per-state prediction; cannot compute gap")
    gap = round(abs(eb - ea), 3)
    favored = "A" if ea <= eb else "B"
    switchable = bool(SWITCH_GAP_MIN <= gap <= SWITCH_GAP_MAX)
    note = ("SYNTHETIC proxy gap (relative units, NOT kcal/mol)" if synth
            else "proxy gap (relative units, NOT kcal/mol) — confirm with physics/MD")
    return EnergyGap(gap=gap, favored_state=favored, switchable=switchable,
                     tool="mock" if synth else "real", synthetic=synth, note=note)


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps).
    tsd = generate_two_states(topology="hinge", trigger="pH", tool="mock", length=100)
    seqs = multistate_mpnn(tsd.state_a, tsd.state_b, n=3, tool="mock")
    for s in seqs:
        pa = af2_predict_state(s.sequence, tsd.state_a, tool="mock")
        pb = af2_predict_state(s.sequence, tsd.state_b, tool="mock")
        eg = energy_gap(pa, pb)
        print(s.design_id,
              "| A scrmsd=", pa.scrmsd_to_state, "B scrmsd=", pb.scrmsd_to_state,
              "| gap=", eg.gap, "favored=", eg.favored_state, "switchable=", eg.switchable,
              "| SYNTHETIC" if s.synthetic else "")
