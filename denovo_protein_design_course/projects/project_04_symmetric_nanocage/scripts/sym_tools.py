"""
sym_tools.py — symmetric-assembly design helpers for Project 04 (nanocage / oligomer design).

Goal: three functions the notebooks import so the plumbing is testable and the notebooks stay thin:

    generate_symmetric(symmetry, length, n, tool="mock")  -> list[Assembly]   (backbone generation)
    tied_mpnn(backbone, symmetry, n_seqs, tool="mock")     -> list[str]        (tied sequence design)
    multimer_predict(seq, symmetry, tool="mock")           -> MultimerScore    (subunit + interface)

DESIGN NOTE FOR STUDENTS
------------------------
Real symmetric RFdiffusion + tied ProteinMPNN + AF2-Multimer are heavy and GPU-bound (an A100 is
recommended for a full C3/C4/D2 campaign — see MANUAL.md §2). So each backend is an adapter you
complete/verify on Colab, with the heavy import done lazily *inside* the function. The module is
import-safe with NO GPU and NO heavy packages: it imports fine here, and every real backend raises a
clear, actionable error if its dependency is missing.

There is also a deterministic `mock` backend so you can build and unit-test the *plumbing*
(symmetry bookkeeping, tied-position layout, record aggregation, ranking) before spending GPU time.

    >>> WARNING: every number the mock backend returns is SYNTHETIC by construction (a hash of the
    >>> inputs). Mock outputs are labelled EXAMPLE_DATA and must NEVER be reported as real results.

Fill in / verify the TODOs against the current RFdiffusion (symmetric), ProteinMPNN (tied), and
ColabFold/AF2-Multimer APIs at the start of the course — these libraries change; pin versions and
log them. Pinned upstreams (verify in 00/02 with the version-verify cell):
    RFdiffusion  https://github.com/RosettaCommons/RFdiffusion   (pin a commit/tag)
    ColabDesign  https://github.com/sokrypton/ColabDesign        (symmetric RFdiffusion + AF2 wrappers)
    SymDesign    https://github.com/kylemeador/symdesign          (symmetry definitions, docking concepts)
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional

# Supported point-group symmetries for this project. The integer is the number of subunits
# (the oligomeric order) that the assembly must close into.
SYMMETRY_ORDER = {
    "C2": 2, "C3": 3, "C4": 4, "C5": 5, "C6": 6,
    "D2": 4, "D3": 6, "D4": 8,
    # Stretch: higher point groups (tetrahedral/octahedral/icosahedral) — see MANUAL.md §2.
    "T": 12, "O": 24, "I": 60,
}


@dataclass
class Assembly:
    """One designed symmetric backbone (the asymmetric unit + its symmetry)."""
    assembly_id: str
    symmetry: str                       # e.g. "C3", "C4", "D2"
    subunit_length: int                 # residues per subunit (the asymmetric unit)
    n_subunits: int                     # oligomeric order implied by `symmetry`
    backbone_pdb: Optional[str] = None  # path to the generated symmetric backbone (None for mock)
    contig: Optional[str] = None        # the symmetric contig string used to generate it
    tool: str = "mock"
    note: str = ""

    def as_row(self) -> dict:
        return asdict(self)


@dataclass
class MultimerScore:
    """AF2-Multimer (ColabFold multimer) readout for one designed sequence in its symmetry."""
    symmetry: str
    subunit_scrmsd: Optional[float] = None     # self-consistency of ONE subunit (designed vs predicted), A
    interface_pae: Optional[float] = None      # mean inter-chain pAE at the interface, A (want < 10)
    symmetry_rmsd: Optional[float] = None       # does the predicted assembly close into target symmetry? A
    plddt: Optional[float] = None              # mean pLDDT of the predicted assembly (0-100)
    interface_energy: Optional[float] = None    # interface energy proxy (REU; more negative = better)
    predicted_order: Optional[int] = None       # oligomeric order the predictor most prefers
    tool: str = "mock"
    ok: bool = True
    error: Optional[str] = None

    def as_row(self) -> dict:
        return asdict(self)


# --------------------------------------------------------------------------- #
# Symmetric contig helpers (teaching scaffold — see data/inputs/symmetry_defs.txt)
# --------------------------------------------------------------------------- #
def symmetric_contig(symmetry: str, length: int) -> str:
    """Return an example symmetric-contig string for RFdiffusion symmetric mode.

    RFdiffusion's symmetric mode replicates the asymmetric unit under the chosen point group.
    The contig describes ONE subunit; `--sym.symmetry` (or the config) applies the operations.
    This is a teaching-grade string; verify the exact contig/flag syntax against the pinned
    RFdiffusion release before you run for real (the flag names have changed across versions).
    """
    if symmetry not in SYMMETRY_ORDER:
        raise ValueError(f"unknown symmetry {symmetry!r}; options: {sorted(SYMMETRY_ORDER)}")
    # One chain of `length` residues as the asymmetric unit; symmetry replicates it.
    return f"{length}-{length}"


def tied_positions(subunit_length: int, n_subunits: int) -> list[list[int]]:
    """Tied-position groups for ProteinMPNN so all symmetry-related copies share one sequence.

    Returns, for each residue i in the asymmetric unit, the list of global indices that must be
    decoded to the SAME amino acid across the n_subunits chains. This is what makes the designed
    assembly genuinely symmetric in sequence (not just in backbone). Verify the exact tied-position
    JSON schema for your ProteinMPNN version; the *concept* (group symmetry-mates) is stable.
    """
    return [[i + c * subunit_length for c in range(n_subunits)] for i in range(subunit_length)]


# --------------------------------------------------------------------------- #
# Backend 1 — symmetric backbone generation
# --------------------------------------------------------------------------- #
def _generate_real(symmetry: str, length: int, n: int) -> list[Assembly]:
    """Real symmetric RFdiffusion. A100 RECOMMENDED for a full campaign (see MANUAL.md §2)."""
    raise NotImplementedError(
        "Wire up symmetric RFdiffusion here. Install per the pinned RFdiffusion/ColabDesign "
        "release in 00_setup, then run inference with symmetric mode, e.g. (verify flags!):\n"
        "  ./scripts/run_inference.py \\\n"
        "    inference.symmetry=<C3|C4|D2> \\\n"
        "    'contigmap.contigs=[<length>-<length>]' \\\n"
        "    inference.num_designs=<n> \\\n"
        "    inference.output_prefix=results/backbones/<sym>\n"
        "Parse each output PDB into an Assembly. NOTE: a full C3/C4/D2 campaign (100s of designs) "
        "wants an A100/HPC; a free T4 realistically only handles a tiny C3 demo.")


def _generate_mock(symmetry: str, length: int, n: int) -> list[Assembly]:
    """Deterministic fake backbones so you can develop the plumbing with no GPU.
    SYNTHETIC by construction — never present these as real designs."""
    order = SYMMETRY_ORDER[symmetry]
    contig = symmetric_contig(symmetry, length)
    out = []
    for i in range(n):
        out.append(Assembly(
            assembly_id=f"EXAMPLE_DATA_{symmetry}_{length}_{i:03d}",
            symmetry=symmetry, subunit_length=length, n_subunits=order,
            backbone_pdb=None, contig=contig, tool="mock",
            note="SYNTHETIC — mock backbone, not a real RFdiffusion design"))
    return out


def generate_symmetric(symmetry: str, length: int, n: int, tool: str = "mock") -> list[Assembly]:
    """Generate `n` symmetric backbones of the given point group with `length` residues/subunit.

    tool ∈ {"mock", "rfdiffusion"}. Use "mock" to test the plumbing anywhere; switch to
    "rfdiffusion" on an A100 once 00_setup has installed it.
    """
    if symmetry not in SYMMETRY_ORDER:
        raise ValueError(f"unknown symmetry {symmetry!r}; options: {sorted(SYMMETRY_ORDER)}")
    if length < 20:
        raise ValueError("subunit_length looks too small for a foldable subunit (>= ~40 typical).")
    tool = tool.lower()
    if tool == "mock":
        return _generate_mock(symmetry, length, n)
    if tool in ("rfdiffusion", "rf", "real"):
        return _generate_real(symmetry, length, n)
    raise ValueError(f"unknown tool {tool!r}; options: mock | rfdiffusion")


# --------------------------------------------------------------------------- #
# Backend 2 — tied sequence design (ProteinMPNN with tied positions)
# --------------------------------------------------------------------------- #
def _tied_mpnn_real(backbone, symmetry: str, n_seqs: int) -> list[str]:
    """Real tied ProteinMPNN. Fast (CPU/T4 fine) — only the diffusion + AF2 steps need an A100."""
    raise NotImplementedError(
        "Wire up tied ProteinMPNN here. Build the tied-position groups with tied_positions(); "
        "pass them so symmetry-related residues decode to the SAME amino acid, e.g. (verify API):\n"
        "  python protein_mpnn_run.py --pdb_path <backbone.pdb> \\\n"
        "    --tied_positions_jsonl tied.jsonl --num_seq_per_target <n_seqs> \\\n"
        "    --sampling_temp 0.1 --out_folder results/seqs/\n"
        "Return the designed sequences (one per design). The tied-vs-untied comparison in "
        "notebook 04 needs BOTH a tied and an untied run.")


def _tied_mpnn_mock(backbone, symmetry: str, n_seqs: int) -> list[str]:
    """Deterministic fake sequences (correct length, valid residues). SYNTHETIC — not real designs."""
    length = getattr(backbone, "subunit_length", 60)
    aa = "ACDEFGHIKLMNPQRSTVWY"
    seqs = []
    base_id = getattr(backbone, "assembly_id", "EXAMPLE_DATA")
    for s in range(n_seqs):
        h = hashlib.sha256(f"{base_id}|{symmetry}|{s}".encode()).digest()
        seq = "".join(aa[h[i % len(h)] % 20] for i in range(length))
        seqs.append(seq)
    return seqs


def tied_mpnn(backbone, symmetry: str, n_seqs: int, tool: str = "mock") -> list[str]:
    """Design `n_seqs` sequences for one symmetric backbone with tied (symmetry-shared) positions.

    Tied positions force every symmetry-related copy of a residue to the same amino acid, which is
    what makes the assembly truly symmetric in sequence. `backbone` is an Assembly (or anything with
    `.subunit_length` / `.assembly_id`). tool ∈ {"mock", "proteinmpnn"}.
    """
    tool = tool.lower()
    if tool == "mock":
        return _tied_mpnn_mock(backbone, symmetry, n_seqs)
    if tool in ("proteinmpnn", "mpnn", "real"):
        return _tied_mpnn_real(backbone, symmetry, n_seqs)
    raise ValueError(f"unknown tool {tool!r}; options: mock | proteinmpnn")


# --------------------------------------------------------------------------- #
# Backend 3 — AF2-Multimer prediction of the assembly
# --------------------------------------------------------------------------- #
def _multimer_real(seq: str, symmetry: str) -> MultimerScore:
    """Real AF2-Multimer / ColabFold multimer. A100 RECOMMENDED for full assemblies."""
    raise NotImplementedError(
        "Wire up AF2-Multimer here. Build a multimer FASTA with the sequence repeated "
        "n_subunits times (one chain per subunit), run ColabFold in multimer mode, then parse:\n"
        "  - subunit scRMSD (designed subunit vs the predicted subunit)\n"
        "  - interface pAE (mean inter-chain PAE; want < 10)\n"
        "  - symmetry RMSD (predicted assembly superposed onto ideal point-group axes)\n"
        "  - interface energy (e.g. a Rosetta InterfaceAnalyzer proxy)\n"
        "Example multimer call (verify against your pinned ColabFold):\n"
        "  colabfold_batch assembly.fasta out/ --model-type alphafold2_multimer_v3 --num-recycle 3")


def _multimer_mock(seq: str, symmetry: str) -> MultimerScore:
    """Deterministic fake AF2-Multimer readout. SYNTHETIC by construction — never report as real."""
    order = SYMMETRY_ORDER.get(symmetry, 3)
    h = int(hashlib.sha256(f"{seq}|{symmetry}".encode()).hexdigest(), 16)
    subunit_scrmsd = round(0.8 + (h % 400) / 100.0, 2)        # 0.80 - 4.79 A
    interface_pae = round(4.0 + (h % 1600) / 100.0, 2)         # 4.00 - 19.99 A
    symmetry_rmsd = round(0.5 + ((h >> 7) % 600) / 100.0, 2)   # 0.50 - 6.49 A
    plddt = round(60 + (h >> 11) % 38, 1)                       # 60 - 97
    interface_energy = round(-((h >> 17) % 60), 1)             # 0 to -59 REU
    # The wrong-oligomer risk: sometimes the predictor "prefers" a different order.
    predicted_order = order if ((h >> 23) % 5) else (order + 1 if order < 8 else order - 1)
    return MultimerScore(
        symmetry=symmetry, subunit_scrmsd=subunit_scrmsd, interface_pae=interface_pae,
        symmetry_rmsd=symmetry_rmsd, plddt=plddt, interface_energy=interface_energy,
        predicted_order=predicted_order, tool="mock", ok=True,
        error="SYNTHETIC — mock AF2-Multimer readout, not a real prediction")


def multimer_predict(seq: str, symmetry: str, tool: str = "mock") -> MultimerScore:
    """Predict the symmetric assembly for `seq` and return subunit/interface/symmetry metrics.

    tool ∈ {"mock", "af2", "colabfold"}. The mock backend is deterministic and SYNTHETIC; switch
    to the real multimer backend on an A100 once 00_setup has installed ColabFold.
    """
    if not seq or any(c not in "ACDEFGHIKLMNPQRSTVWY" for c in seq.upper()):
        return MultimerScore(symmetry=symmetry, ok=False, error="invalid amino-acid sequence")
    tool = tool.lower()
    if tool == "mock":
        return _multimer_mock(seq.upper(), symmetry)
    if tool in ("af2", "colabfold", "multimer", "real"):
        return _multimer_real(seq.upper(), symmetry)
    raise ValueError(f"unknown tool {tool!r}; options: mock | af2/colabfold")


if __name__ == "__main__":
    # Plumbing smoke test with the mock backend (no GPU, no heavy deps). SYNTHETIC output.
    asm = generate_symmetric("C3", length=60, n=2, tool="mock")[0]
    seqs = tied_mpnn(asm, "C3", n_seqs=2, tool="mock")
    score = multimer_predict(seqs[0], "C3", tool="mock")
    print("assembly:", asm.as_row())
    print("seq[0]  :", seqs[0])
    print("score   :", score.as_row())
