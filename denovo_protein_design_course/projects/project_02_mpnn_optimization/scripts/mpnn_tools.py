"""
mpnn_tools.py — ProteinMPNN sweep + metrics helpers for Project 02.

Goal: a small, testable API the notebooks import so the plumbing stays thin and runs ANYWHERE
(no GPU, no MPNN install) via a deterministic `mock` backend:

    run_mpnn(backbone, temperature, noise, n_seqs, tool="mock")   -> list[Design-ish dicts]
    sequence_recovery(native, designed)                           -> float in [0, 1]
    shannon_entropy(sequences)                                    -> per-position entropy array + mean
    net_charge(seq, pH=7.4)                                       -> net charge (solubility proxy)
    hydrophobic_fraction(seq)                                     -> exposed-patch proxy in [0, 1]
    camsol_like(seq)                                              -> CamSol-STYLE heuristic (NOT real CamSol)

DESIGN NOTE FOR STUDENTS
------------------------
Real ProteinMPNN/LigandMPNN runs are an external process (clone the repo, run protein_mpnn_run.py).
That is documented as a TODO inside `_real_mpnn`; the heavy/torch path is never imported at module
load, so this file imports fine with NO GPU and NO MPNN install. The `mock` backend is DETERMINISTIC
(seeded by the backbone id + settings) so you can develop and unit-test the sweep, recovery, entropy,
and solubility logic before spending any GPU time.

THE SOLUBILITY FUNCTIONS ARE TEACHING HEURISTICS. `camsol_like` is NOT real CamSol (Sormanni 2015) —
it is a transparent linear combination for teaching. Never present these proxy scores as expression
or solubility *measurements*; only wet-lab express -> SDS-PAGE -> SEC measures that.

Fill in / verify the TODOs against the current ProteinMPNN/LigandMPNN APIs at the start of the course
(these repos change — pin a commit and log it).

Dependencies: numpy (math); the real backend additionally needs a ProteinMPNN/LigandMPNN checkout.
"""
from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass, field, asdict
from typing import Optional

import numpy as np

AA = "ACDEFGHIKLMNPQRSTVWY"

# Kyte-Doolittle hydropathy (positive = hydrophobic). Used by the patch proxy.
KD_HYDROPATHY = {
    "A": 1.8, "C": 2.5, "D": -3.5, "E": -3.5, "F": 2.8, "G": -0.4, "H": -3.2,
    "I": 4.5, "K": -3.9, "L": 3.8, "M": 1.9, "N": -3.5, "P": -1.6, "Q": -3.5,
    "R": -4.5, "S": -0.8, "T": -0.7, "V": 4.2, "W": -0.9, "Y": -1.3,
}
# Side-chain pKa values for a simple Henderson-Hasselbalch net-charge estimate.
PKA = {"D": 3.65, "E": 4.25, "C": 8.3, "Y": 10.07, "H": 6.0, "K": 10.53, "R": 12.48}
PKA_NTERM, PKA_CTERM = 9.0, 2.0


@dataclass
class MpnnSeq:
    """One designed sequence and the setting that produced it."""
    backbone: str
    sequence: str
    temperature: float
    noise: float
    n_seqs: int
    tool: str = "mock"
    seq_index: int = 0
    # filled by the notebooks downstream:
    recovery: Optional[float] = None
    scrmsd: Optional[float] = None          # recapitulation Ca-RMSD (AF2/ESMFold)
    plddt: Optional[float] = None
    net_charge: Optional[float] = None
    hydrophobic_fraction: Optional[float] = None
    camsol_like: Optional[float] = None
    extra: dict = field(default_factory=dict)

    def as_row(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- #
# MPNN backends. The real one shells out to ProteinMPNN; the mock is deterministic.
# --------------------------------------------------------------------------- #
def _real_mpnn(backbone: str, temperature: float, noise: float, n_seqs: int) -> list[str]:
    """Run the REAL ProteinMPNN on a backbone PDB and return designed sequences.

    Heavy/external; implemented as a documented TODO. The canonical call is, e.g.:

        python ProteinMPNN/protein_mpnn_run.py \\
            --pdb_path <backbone> --out_folder <out> \\
            --num_seq_per_target <n_seqs> --sampling_temp "<temperature>" \\
            --backbone_noise "<noise>" --seed 37

    then parse the FASTA in <out>/seqs/. Pin the ProteinMPNN commit and log it.
    LigandMPNN (run.py --model_type protein_mpnn) is an equivalent backend.
    """
    raise NotImplementedError(
        "Wire up ProteinMPNN here. Clone https://github.com/dauparas/ProteinMPNN (pin a commit), "
        "run protein_mpnn_run.py with --sampling_temp/--backbone_noise/--num_seq_per_target on the "
        "backbone PDB, and parse the output FASTA. Until then use tool='mock' to build the plumbing."
    )


def _mock_mpnn(backbone: str, temperature: float, noise: float, n_seqs: int) -> list[str]:
    """Deterministic fake MPNN: same inputs -> same sequences. NEVER a real design.

    Models the qualitative behavior students must observe:
      * higher temperature  -> more diversity (sequences differ more across samples)
      * higher noise         -> a bit more diversity / drift
    It is seeded by (backbone, settings) so the sweep is reproducible. Sequence length is
    derived from the backbone id length only as a stand-in (the real backend reads the PDB).
    """
    base = int(hashlib.sha256(backbone.encode()).hexdigest(), 16)
    length = 60 + (base % 80)                      # 60..139 aa stand-in length
    rng = np.random.default_rng(base % (2**32))
    # A deterministic "native-like" consensus to vary around.
    consensus = "".join(AA[(base >> (i % 60)) % 20] for i in range(length))
    # Diversity grows with temperature and (mildly) noise.
    p_mut = min(0.85, 0.10 + 1.4 * float(temperature) + 0.5 * float(noise))
    seqs = []
    for k in range(int(n_seqs)):
        rk = np.random.default_rng((base + 1000 * k) % (2**32))
        s = list(consensus)
        for i in range(length):
            if rk.random() < p_mut:
                s[i] = AA[int(rk.integers(0, 20))]
        seqs.append("".join(s))
    return seqs


_BACKENDS = {"mock": _mock_mpnn, "proteinmpnn": _real_mpnn, "ligandmpnn": _real_mpnn}


def run_mpnn(backbone: str, temperature: float = 0.2, noise: float = 0.0,
             n_seqs: int = 16, tool: str = "mock") -> list[MpnnSeq]:
    """Design `n_seqs` sequences for `backbone` at the given setting.

    backbone : a backbone identifier (mock) or a PDB path (real backends).
    tool     : 'mock' (deterministic, no GPU) | 'proteinmpnn' | 'ligandmpnn'.
    Returns a list of MpnnSeq records carrying the setting on every row.
    """
    tool = tool.lower()
    if tool not in _BACKENDS:
        raise ValueError(f"unknown tool {tool!r}; options: {sorted(_BACKENDS)}")
    if temperature <= 0:
        raise ValueError("temperature must be > 0")
    raw = _BACKENDS[tool](backbone, float(temperature), float(noise), int(n_seqs))
    out = []
    for i, seq in enumerate(raw):
        out.append(MpnnSeq(backbone=backbone, sequence=seq, temperature=float(temperature),
                           noise=float(noise), n_seqs=int(n_seqs), tool=tool, seq_index=i,
                           net_charge=net_charge(seq),
                           hydrophobic_fraction=hydrophobic_fraction(seq),
                           camsol_like=camsol_like(seq)))
    return out


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #
def sequence_recovery(native: str, designed: str) -> float:
    """Fraction of positions where designed matches native (over the overlap). In [0, 1].

    Typical ProteinMPNN recovery is ~0.40-0.50. This is a SANITY CHECK, not a quality target:
    high recovery can simply mean low diversity. Align by position; we compare over min length.
    """
    native = (native or "").upper()
    designed = (designed or "").upper()
    n = min(len(native), len(designed))
    if n == 0:
        raise ValueError("empty sequence(s); cannot compute recovery")
    matches = sum(1 for a, b in zip(native[:n], designed[:n]) if a == b)
    return matches / n


def shannon_entropy(sequences: list[str]) -> dict:
    """Per-position Shannon entropy (bits) across aligned sequences + the mean.

    Diversity measure: near-0 entropy at a position means MPNN is confident (low temperature);
    high entropy means it is sampling many residues there. Returns
    {'per_position': np.ndarray, 'mean': float, 'n': int, 'length': int}.
    Sequences are compared over the shortest length (assumed already aligned, same backbone).
    """
    seqs = [s.upper() for s in sequences if s]
    if not seqs:
        raise ValueError("no sequences given")
    L = min(len(s) for s in seqs)
    per_pos = np.zeros(L)
    for i in range(L):
        col = [s[i] for s in seqs]
        counts = np.array([col.count(a) for a in AA], dtype=float)
        p = counts[counts > 0] / len(col)
        per_pos[i] = float(-(p * np.log2(p)).sum())
    return {"per_position": per_pos, "mean": float(per_pos.mean()),
            "n": len(seqs), "length": L}


# --------------------------------------------------------------------------- #
# Solubility / expressibility PROXIES. Teaching heuristics — NOT measurements.
# --------------------------------------------------------------------------- #
def net_charge(seq: str, pH: float = 7.4) -> float:
    """Net charge at a given pH via Henderson-Hasselbalch (solubility proxy).

    Very large |net charge| can hurt solubility; this is a soft, sequence-only signal.
    """
    seq = (seq or "").upper()
    if not seq:
        return 0.0
    pos = 1.0 / (1.0 + 10 ** (pH - PKA_NTERM))
    neg = 1.0 / (1.0 + 10 ** (PKA_CTERM - pH))
    for aa in seq:
        if aa in ("K", "R", "H"):
            pos += 1.0 / (1.0 + 10 ** (pH - PKA[aa]))
        elif aa in ("D", "E", "C", "Y"):
            neg += 1.0 / (1.0 + 10 ** (PKA[aa] - pH))
    return round(pos - neg, 3)


def hydrophobic_fraction(seq: str, window: int = 5, threshold: float = 1.5) -> float:
    """Fraction of residues inside a hydrophobic 'patch' (proxy for aggregation risk).

    A residue counts as patch-forming if the mean Kyte-Doolittle hydropathy over a window
    centered on it exceeds `threshold`. Sequence-only stand-in for surface-exposed hydrophobic
    patches (the real signal needs structure + SASA — see SAP). In [0, 1].
    """
    seq = (seq or "").upper()
    n = len(seq)
    if n == 0:
        return 0.0
    h = np.array([KD_HYDROPATHY.get(a, 0.0) for a in seq])
    half = window // 2
    patchy = 0
    for i in range(n):
        lo, hi = max(0, i - half), min(n, i + half + 1)
        if h[lo:hi].mean() > threshold:
            patchy += 1
    return round(patchy / n, 3)


def camsol_like(seq: str) -> float:
    """A CamSol-STYLE solubility heuristic — TEACHING ONLY, *not* real CamSol (Sormanni 2015).

    Real CamSol uses a calibrated per-residue intrinsic-solubility scale plus a sequence/structural
    correction. This transparent stand-in combines: penalize hydrophobic patches, penalize charge
    extremes, reward a moderate net charge. Higher = predicted *more soluble* (relative, unitless).
    USE TO RANK WITHIN A BATCH, NOT AS AN ABSOLUTE SOLUBILITY VALUE.
    """
    seq = (seq or "").upper()
    if not seq:
        return 0.0
    z = net_charge(seq)
    hp = hydrophobic_fraction(seq)
    # moderate charge is good (~ +/- a few); huge |z| is bad; big hydrophobic patches are bad.
    score = 1.0 - 1.5 * hp - 0.05 * max(0.0, abs(z) - 4.0) + 0.05 * min(abs(z), 4.0)
    return round(float(score), 3)


if __name__ == "__main__":
    # Plumbing smoke test with the deterministic mock backend (no GPU, no MPNN install).
    native = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKR"
    designs = run_mpnn("demo_backbone_01", temperature=0.2, noise=0.1, n_seqs=8, tool="mock")
    print(f"designed {len(designs)} sequences for {designs[0].backbone}")
    rec = [round(sequence_recovery(native, d.sequence), 3) for d in designs]
    print("recovery vs a demo native:", rec)
    ent = shannon_entropy([d.sequence for d in designs])
    print(f"mean per-position entropy: {ent['mean']:.3f} bits over {ent['length']} positions")
    d0 = designs[0]
    print(f"proxies (seq 0): net_charge={d0.net_charge}  hydrophobic_fraction={d0.hydrophobic_fraction}  "
          f"camsol_like={d0.camsol_like}  (camsol_like is a HEURISTIC, not real CamSol)")
