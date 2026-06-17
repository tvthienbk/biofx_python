"""Reproducible command builders for the GPU tools (Stages 3-5).

The protocol gives shell snippets for RFdiffusionAA, LigandMPNN and ColabFold.
Hand-typed command lines are where reproducibility quietly breaks (a bare-integer
contig, a ``--fixed_residues`` list that no longer matches the motif, a forgotten
ligand code).  These dataclasses turn a typed config into a validated argument
vector, and cross-check the pieces that the protocol calls out as critical.

Nothing here launches a GPU job; ``to_argv()`` / ``to_shell()`` emit the exact
command you would run inside the Apptainer/conda environment.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass, field
from typing import List, Optional

from .contig import Contig, parse_contig

__all__ = [
    "RFdiffusionAAJob",
    "LigandMPNNJob",
    "ColabFoldJob",
    "PipelineError",
]


class PipelineError(ValueError):
    """Raised when a job config is internally inconsistent."""


@dataclass
class RFdiffusionAAJob:
    """Backbone generation around a motif/ligand (Stage 3, step 7)."""

    input_pdb: str
    contig: Contig
    ligand: Optional[str] = None
    num_designs: int = 100
    diffuser_T: int = 200
    deterministic: bool = True
    output_prefix: str = "output/run1/sample"
    sif: str = "rf_se3_diffusion.sif"
    guide_scale: Optional[float] = None
    extra: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        problems = list(self.contig.validate())
        if self.num_designs <= 0:
            problems.append("num_designs must be > 0")
        if self.diffuser_T <= 0:
            problems.append("diffuser.T must be > 0")
        return problems

    def to_argv(self) -> List[str]:
        problems = self.validate()
        if problems:
            raise PipelineError("; ".join(problems))
        contigs_arg, length_arg = self.contig.to_hydra()
        argv = [
            "apptainer", "run", "--nv", self.sif, "-u", "run_inference.py",
            f"inference.deterministic={self.deterministic}",
            f"diffuser.T={self.diffuser_T}",
            f"inference.input_pdb={self.input_pdb}",
            contigs_arg,
        ]
        if length_arg:
            argv.append(length_arg)
        if self.ligand:
            argv.append(f"inference.ligand={self.ligand}")
        argv.append(f"inference.num_designs={self.num_designs}")
        argv.append(f"inference.output_prefix={self.output_prefix}")
        if self.guide_scale is not None:
            argv.append(f"potentials.guide_scale={self.guide_scale}")
        argv.extend(self.extra)
        return argv

    def to_shell(self) -> str:
        return " ".join(shlex.quote(a) for a in self.to_argv())


@dataclass
class LigandMPNNJob:
    """Ligand-aware sequence design (Stage 4, step 9)."""

    pdb_path: str
    fixed_residues: List[str] = field(default_factory=list)
    model_type: str = "ligand_mpnn"
    number_of_batches: int = 8
    pack_side_chains: bool = True
    out_folder: str = "mpnn/run1/"
    omit_AA: Optional[str] = None
    bias_AA: Optional[str] = None
    seed: Optional[int] = None
    script: str = "run.py"
    extra: List[str] = field(default_factory=list)

    def validate(self, motif_residues: Optional[List[str]] = None) -> List[str]:
        problems: List[str] = []
        if self.model_type not in ("ligand_mpnn", "protein_mpnn"):
            problems.append(f"unknown model_type {self.model_type!r}")
        if self.number_of_batches <= 0:
            problems.append("number_of_batches must be > 0")
        if not self.fixed_residues:
            problems.append(
                "no fixed_residues: catalytic residues must be held fixed "
                "(protocol Stage 4 CRITICAL STEP)"
            )
        if motif_residues is not None:
            missing = [r for r in motif_residues if r not in self.fixed_residues]
            if missing:
                problems.append(
                    f"motif residues not fixed: {missing} — catalytic geometry "
                    f"will be lost"
                )
        return problems

    def to_argv(self, motif_residues: Optional[List[str]] = None) -> List[str]:
        problems = self.validate(motif_residues)
        if problems:
            raise PipelineError("; ".join(problems))
        argv = [
            "python", self.script,
            "--model_type", self.model_type,
            "--pdb_path", self.pdb_path,
            "--fixed_residues", " ".join(self.fixed_residues),
            "--number_of_batches", str(self.number_of_batches),
            "--pack_side_chains", "1" if self.pack_side_chains else "0",
            "--out_folder", self.out_folder,
        ]
        if self.omit_AA:
            argv += ["--omit_AA", self.omit_AA]
        if self.bias_AA:
            argv += ["--bias_AA", self.bias_AA]
        if self.seed is not None:
            argv += ["--seed", str(self.seed)]
        argv.extend(self.extra)
        return argv

    def to_shell(self, motif_residues: Optional[List[str]] = None) -> str:
        return " ".join(shlex.quote(a) for a in self.to_argv(motif_residues))


@dataclass
class ColabFoldJob:
    """Single-sequence reprediction for self-consistency (Stage 5a, step 11)."""

    input_fasta: str
    out_dir: str = "af2/run1/"
    num_models: int = 5
    num_recycle: int = 3
    msa_mode: str = "single_sequence"
    amber: bool = False
    templates: bool = False
    binary: str = "colabfold_batch"
    extra: List[str] = field(default_factory=list)

    def validate(self) -> List[str]:
        problems: List[str] = []
        if self.num_models <= 0:
            problems.append("num_models must be > 0")
        if self.msa_mode not in ("single_sequence", "mmseqs2_uniref_env", "mmseqs2_uniref"):
            problems.append(f"unexpected msa_mode {self.msa_mode!r}")
        return problems

    def to_argv(self) -> List[str]:
        problems = self.validate()
        if problems:
            raise PipelineError("; ".join(problems))
        argv = [
            self.binary,
            "--num-models", str(self.num_models),
            "--num-recycle", str(self.num_recycle),
            "--msa-mode", self.msa_mode,
        ]
        if self.amber:
            argv.append("--amber")
        if self.templates:
            argv.append("--templates")
        argv.extend(self.extra)
        argv += [self.input_fasta, self.out_dir]
        return argv

    def to_shell(self) -> str:
        return " ".join(shlex.quote(a) for a in self.to_argv())


def consistency_check(rfd: RFdiffusionAAJob, mpnn: LigandMPNNJob) -> List[str]:
    """Cross-check that a diffusion job and its sequence-design job agree.

    Verifies the ligand code is carried through and that every motif residue
    from the contig is held fixed by LigandMPNN.
    """
    problems: List[str] = []
    motif = rfd.contig.motif_residues()
    problems.extend(mpnn.validate(motif_residues=motif))
    if rfd.ligand and mpnn.model_type != "ligand_mpnn":
        problems.append(
            "ligand present in diffusion but LigandMPNN model_type is not "
            "ligand_mpnn — pocket residues will be designed blind to the ligand"
        )
    return problems
