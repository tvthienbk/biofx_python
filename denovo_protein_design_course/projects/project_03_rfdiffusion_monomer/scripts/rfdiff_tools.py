"""
rfdiff_tools.py — backbone-generation + scoring helpers for Project 03.

Goal: three small functions the notebooks import so the campaign logic is testable and the
notebooks stay thin:

    generate_backbones(length, ss_bias, n, tool="mock")  -> list[Backbone]
    self_consistency(backbone, seq, tool="mock")         -> SelfConsistency (scRMSD, pLDDT)
    novelty_tm(pdb, tool="mock")                          -> Novelty (TM-to-nearest natural fold)

DESIGN NOTE FOR STUDENTS
------------------------
The real backends are heavy and environment-specific (RFdiffusion via ColabDesign, ProteinMPNN,
AF2/ESMFold, Foldseek/TM-align), so each is implemented as an adapter you complete/verify on Colab.
Heavy imports happen *inside* the function (lazily), so this module is import-safe with NO GPU and
NO heavy packages installed: it imports fine anywhere, and the real backends raise a clear,
actionable error if their dependency is missing.

A deterministic `mock` backend lets you build and unit-test the *plumbing* (the campaign loop, the
CSV schema, the frontier plot) before you spend GPU time. The mock numbers are SYNTHETIC by
construction — they encode the project's realistic priors (foldability is high for short all-α and
drops with novelty + length, all-β is hardest) ONLY so the example figures look qualitatively right.
**NEVER present mock numbers as real designs** — every mock record is flagged `synthetic=True` and
ids are prefixed `EXAMPLE_DATA_`.

COMPUTE HONESTY
---------------
RFdiffusion on a free Colab T4 is fine for SMALL batches. The full campaign (hundreds of backbones
across lengths {80,120,200,300} and three topologies) realistically needs an A100 / HPC. The real
`generate_backbones` adapter notes this; do not plan the whole sweep on a T4.

Fill in / verify the TODOs against the current RFdiffusion (ColabDesign), ProteinMPNN, ColabFold/
transformers, and Foldseek APIs at the start of the course (these libraries change — pin commits and
log them).
"""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, asdict, field
from typing import Optional

# Pinned upstreams (verify with the version-verify cell in 00_setup / 02_generate; tools change):
#   RFdiffusion : https://github.com/RosettaCommons/RFdiffusion   (pin a commit/tag here)
#   ColabDesign : https://github.com/sokrypton/ColabDesign        (pin a commit/tag here)
#   ProteinMPNN : https://github.com/dauparas/ProteinMPNN         (pin a commit/tag here)
#   ColabFold   : https://github.com/sokrypton/ColabFold          (pin a commit/tag here)
#   Foldseek    : https://github.com/steineggerlab/foldseek       (pin a release here)

SS_BIASES = ("alpha", "beta", "mixed")
CAMPAIGN_LENGTHS = (80, 120, 200, 300)
SELF_CONSISTENT_SCRMSD = 2.0   # foldability bar (Å)
NOVEL_TM = 0.5                  # TM-score to nearest natural fold below which a fold is "novel"


# --------------------------------------------------------------------------- #
# Records
# --------------------------------------------------------------------------- #
@dataclass
class Backbone:
    backbone_id: str
    length: int
    ss_bias: str                       # alpha | beta | mixed
    pdb_path: Optional[str] = None
    tool: str = "mock"
    seed: int = 0
    synthetic: bool = False            # True for the mock backend — never a real design
    notes: str = ""

    def as_row(self) -> dict:
        return asdict(self)


@dataclass
class SelfConsistency:
    scrmsd: Optional[float] = None     # best-of-N MPNN-seq Cα-RMSD (Å); < 2.0 == foldable
    plddt: Optional[float] = None      # mean pLDDT of the refold (0–100); NOT stability
    tool: str = "mock"
    synthetic: bool = False
    ok: bool = True
    error: Optional[str] = None


@dataclass
class Novelty:
    tm_to_pdb: Optional[float] = None  # TM-score to nearest natural fold; < 0.5 == novel
    nearest_pdb: Optional[str] = None
    tool: str = "mock"
    synthetic: bool = False
    ok: bool = True
    error: Optional[str] = None


# --------------------------------------------------------------------------- #
# Backend: generate_backbones
# --------------------------------------------------------------------------- #
def _generate_real(length: int, ss_bias: str, n: int, seed: int, out_dir: str) -> list[Backbone]:
    """RFdiffusion via the ColabDesign notebook. Verify the API/commit and pin it.

    COMPUTE: T4 OK for SMALL n / short length; the full lengths×topology sweep needs A100/HPC.
    """
    try:
        # TODO: import/run the RFdiffusion ColabDesign API you installed in 00_setup.
        #   - contigs = f"{length}-{length}" for a fixed-length monomer
        #   - secondary-structure / block-adjacency conditioning for ss_bias in {alpha,beta,mixed}
        #   - inference.num_designs = n, diffuser.T ~ 50, inference.output_prefix = out_dir/...
        #   then collect the written backbone PDBs into Backbone records.
        raise NotImplementedError(
            "Wire up RFdiffusion here. Run install_rfdiffusion()/the ColabDesign RFdiffusion "
            "notebook in 00_setup, set contigs=f'{length}-{length}', apply the ss_bias "
            "conditioning, run inference.num_designs=n, and parse the output PDBs. "
            "NOTE: full campaign needs A100/HPC — only small batches fit a free T4.")
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            f"RFdiffusion backend not available ({e!r}). Use tool='mock' for the plumbing, or "
            f"install RFdiffusion (ColabDesign) on a GPU runtime — A100/HPC for the full sweep.")


def _generate_mock(length: int, ss_bias: str, n: int, seed: int, out_dir: str) -> list[Backbone]:
    """Deterministic fake backbones so the campaign loop runs with no GPU.
    SYNTHETIC — these are not real designs (no PDB is written)."""
    out = []
    for i in range(n):
        h = hashlib.sha256(f"{length}|{ss_bias}|{seed}|{i}".encode()).hexdigest()
        out.append(Backbone(
            backbone_id=f"EXAMPLE_DATA_{ss_bias}_L{length}_{i:03d}",
            length=length, ss_bias=ss_bias, pdb_path=None, tool="mock",
            seed=seed, synthetic=True, notes="SYNTHETIC mock backbone — not a real design",
        ))
    return out


def generate_backbones(length: int, ss_bias: str = "mixed", n: int = 10,
                       tool: str = "mock", seed: int = 0,
                       out_dir: str = "results/backbones") -> list[Backbone]:
    """Generate `n` monomer backbones of `length` residues with a secondary-structure bias.

    ss_bias ∈ {alpha, beta, mixed}. tool ∈ {mock, rfdiffusion}.
    """
    if ss_bias not in SS_BIASES:
        raise ValueError(f"ss_bias must be one of {SS_BIASES}, got {ss_bias!r}")
    if length <= 0 or n <= 0:
        raise ValueError("length and n must be positive")
    tool = tool.lower()
    if tool in ("rfdiffusion", "rfdiff", "real"):
        return _generate_real(length, ss_bias, n, seed, out_dir)
    if tool == "mock":
        return _generate_mock(length, ss_bias, n, seed, out_dir)
    raise ValueError(f"unknown tool {tool!r}; options: mock, rfdiffusion")


# --------------------------------------------------------------------------- #
# Backend: self_consistency  (ProteinMPNN -> AF2/ESMFold -> scRMSD)
# --------------------------------------------------------------------------- #
def _self_consistency_real(backbone: Backbone, seq: Optional[str],
                           n_seqs: int, tool: str) -> SelfConsistency:
    """ProteinMPNN (n_seqs/backbone) -> fold each with AF2/ESMFold -> best-of-N scRMSD.

    Returns the BEST (lowest) scRMSD over the MPNN sequences, with the refold's mean pLDDT.
    Uses filtering_pipeline.ca_rmsd for the designed-vs-predicted Cα-RMSD.
    """
    try:
        # TODO (verify APIs / pin commits in 00_setup):
        #   1. If seq is None, run ProteinMPNN on backbone.pdb_path: --num_seq_per_target n_seqs,
        #      --sampling_temp 0.1, --backbone_noise 0.0.
        #   2. For each sequence, predict with tool ('esmfold' fast triage, or 'af2' for top picks).
        #   3. scRMSD_i = filtering_pipeline.ca_rmsd(backbone.pdb_path, predicted_pdb_i)
        #   4. Return best-of-N: min scRMSD and the pLDDT of that refold.
        raise NotImplementedError(
            "Wire up self-consistency: ProteinMPNN sequences -> AF2/ESMFold refold -> "
            "ca_rmsd(designed, predicted). Use ESMFold for fast triage, AF2 for top picks.")
    except Exception as e:  # noqa: BLE001
        return SelfConsistency(tool=tool, ok=False,
                               error=f"{e!r}; run tool='mock' or install the refold backend")


def _self_consistency_mock(backbone: Backbone) -> SelfConsistency:
    """Deterministic synthetic scRMSD/pLDDT that ENCODE the project's realistic priors:
    foldability is high for short all-α and DROPS as length grows and topology hardens
    (all-β hardest). Purely for making the example frontier plot look qualitatively right.
    SYNTHETIC — never present as a real measurement."""
    h = int(hashlib.sha256(backbone.backbone_id.encode()).hexdigest(), 16)
    jitter = (h % 1000) / 1000.0                     # 0..1 deterministic "noise"
    # base difficulty by topology and length (higher base => worse scRMSD)
    topo_base = {"alpha": 0.6, "mixed": 1.1, "beta": 1.7}[backbone.ss_bias]
    length_penalty = (backbone.length - 80) / 220.0 * 1.4   # 0 at L80, ~1.4 at L300
    scrmsd = round(topo_base + length_penalty + 1.2 * jitter, 2)   # ~0.6 .. ~4.3 Å
    plddt = round(max(40.0, 95.0 - 9.0 * scrmsd + 4.0 * (1 - jitter)), 1)
    return SelfConsistency(scrmsd=scrmsd, plddt=plddt, tool="mock", synthetic=True,
                           error="SYNTHETIC — mock self-consistency, not a real prediction")


def self_consistency(backbone: Backbone, seq: Optional[str] = None,
                     tool: str = "mock", n_seqs: int = 8) -> SelfConsistency:
    """Best-of-N self-consistency for a backbone.

    tool ∈ {mock, esmfold, af2}. With a real tool, ProteinMPNN designs `n_seqs` sequences
    (unless `seq` is given) and each is refolded; returns the best (lowest) scRMSD + pLDDT.
    """
    tool = tool.lower()
    if tool == "mock":
        return _self_consistency_mock(backbone)
    if tool in ("esmfold", "af2", "colabfold"):
        return _self_consistency_real(backbone, seq, n_seqs, tool)
    raise ValueError(f"unknown tool {tool!r}; options: mock, esmfold, af2")


# --------------------------------------------------------------------------- #
# Backend: novelty_tm  (Foldseek / TM-align vs the PDB)
# --------------------------------------------------------------------------- #
def _novelty_real(pdb: str, db: str, tool: str) -> Novelty:
    """Foldseek easy-search (or TM-align) vs the PDB database -> TM-score to nearest fold.

    The PDB/AFDB database is LARGE and downloaded separately (see data/README.md) — pass its path.
    """
    try:
        # TODO (pin the Foldseek release):
        #   foldseek easy-search pdb db aln.m8 tmp --format-output "query,target,alntmscore"
        #   parse the best (highest) alntmscore as tm_to_pdb and its target as nearest_pdb.
        #   For top picks, confirm with a pairwise TM-align run (alignment-coverage sanity check).
        raise NotImplementedError(
            "Wire up Foldseek: easy-search the design PDB against the PDB database "
            "(downloaded separately, not committed), parse the best alntmscore. "
            "Confirm low-TM 'novel' hits with TM-align (guard against short-alignment artifacts).")
    except Exception as e:  # noqa: BLE001
        return Novelty(tool=tool, ok=False,
                       error=f"{e!r}; run tool='mock' or install Foldseek + the PDB database")


def _novelty_mock(pdb_or_id: str) -> Novelty:
    """Deterministic synthetic TM-to-nearest. SYNTHETIC — not a real Foldseek search."""
    h = int(hashlib.sha256(str(pdb_or_id).encode()).hexdigest(), 16)
    tm = round(0.20 + (h % 600) / 1000.0, 3)         # 0.20 .. 0.80
    return Novelty(tm_to_pdb=tm, nearest_pdb="EXAMPLE_DATA_pdb", tool="mock", synthetic=True,
                   error="SYNTHETIC — mock novelty, not a real Foldseek/TM-align search")


def novelty_tm(pdb: str, tool: str = "mock", db: str = "pdb_db") -> Novelty:
    """TM-score of a design to its nearest natural fold. tool ∈ {mock, foldseek, tmalign}.

    tm_to_pdb < 0.5 ≈ novel fold (Zhang & Skolnick convention). Novelty is REPORTED, not a
    pass/fail filter — see MANUAL.md §4.
    """
    tool = tool.lower()
    if tool == "mock":
        return _novelty_mock(pdb)
    if tool in ("foldseek", "tmalign", "tm-align"):
        return _novelty_real(pdb, db, tool)
    raise ValueError(f"unknown tool {tool!r}; options: mock, foldseek, tmalign")


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps).
    bbs = generate_backbones(length=80, ss_bias="alpha", n=3, tool="mock")
    for bb in bbs:
        sc = self_consistency(bb, tool="mock")
        nv = novelty_tm(bb.backbone_id, tool="mock")
        print(bb.backbone_id, "scrmsd=", sc.scrmsd, "plddt=", sc.plddt,
              "tm_to_pdb=", nv.tm_to_pdb, "| SYNTHETIC" if bb.synthetic else "")
