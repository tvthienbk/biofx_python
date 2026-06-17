"""Tests for enzyme_design.pipeline command builders."""

import pytest

from enzyme_design.contig import build_contig, parse_contig
from enzyme_design.pipeline import (
    ColabFoldJob,
    LigandMPNNJob,
    PipelineError,
    RFdiffusionAAJob,
    consistency_check,
)


def _contig():
    return build_contig([("A", 84, 87)], flank=(10, 120), total_length=(150, 150))


def test_rfdiffusion_argv_contains_key_args():
    job = RFdiffusionAAJob(
        input_pdb="input/active_site.pdb",
        contig=_contig(),
        ligand="LIG",
        num_designs=1000,
    )
    argv = job.to_argv()
    assert "run_inference.py" in argv
    assert "inference.input_pdb=input/active_site.pdb" in argv
    assert "inference.ligand=LIG" in argv
    assert "inference.num_designs=1000" in argv
    assert any(a.startswith("contigmap.contigs=") for a in argv)
    assert any(a.startswith("contigmap.length=") for a in argv)


def test_rfdiffusion_rejects_invalid_contig():
    bad = parse_contig("['10-20,A84-87,10-20']", "150-150")  # impossible length
    job = RFdiffusionAAJob(input_pdb="x.pdb", contig=bad)
    with pytest.raises(PipelineError, match="impossible"):
        job.to_argv()


def test_rfdiffusion_zero_designs_rejected():
    job = RFdiffusionAAJob(input_pdb="x.pdb", contig=_contig(), num_designs=0)
    with pytest.raises(PipelineError):
        job.to_argv()


def test_ligandmpnn_requires_fixed_residues():
    job = LigandMPNNJob(pdb_path="s.pdb", fixed_residues=[])
    with pytest.raises(PipelineError, match="fixed_residues"):
        job.to_argv()


def test_ligandmpnn_detects_unfixed_motif():
    job = LigandMPNNJob(pdb_path="s.pdb", fixed_residues=["A84", "A85"])
    with pytest.raises(PipelineError, match="not fixed"):
        job.to_argv(motif_residues=["A84", "A85", "A86", "A87"])


def test_ligandmpnn_argv_ok():
    job = LigandMPNNJob(
        pdb_path="output/run1/sample_0.pdb",
        fixed_residues=["A84", "A85", "A86", "A87"],
        number_of_batches=8,
        pack_side_chains=True,
    )
    argv = job.to_argv(motif_residues=["A84", "A85", "A86", "A87"])
    assert "--model_type" in argv and "ligand_mpnn" in argv
    assert "--pack_side_chains" in argv
    i = argv.index("--fixed_residues")
    assert argv[i + 1] == "A84 A85 A86 A87"


def test_colabfold_single_sequence_default():
    job = ColabFoldJob(input_fasta="designs.fasta")
    argv = job.to_argv()
    assert "--msa-mode" in argv
    assert "single_sequence" in argv
    assert argv[-2:] == ["designs.fasta", "af2/run1/"]


def test_consistency_check_flags_unfixed_motif():
    rfd = RFdiffusionAAJob(input_pdb="x.pdb", contig=_contig(), ligand="LIG")
    mpnn = LigandMPNNJob(pdb_path="s.pdb", fixed_residues=["A84"])  # missing 85-87
    problems = consistency_check(rfd, mpnn)
    assert any("not fixed" in p for p in problems)


def test_consistency_check_passes_when_aligned():
    rfd = RFdiffusionAAJob(input_pdb="x.pdb", contig=_contig(), ligand="LIG")
    mpnn = LigandMPNNJob(
        pdb_path="s.pdb", fixed_residues=["A84", "A85", "A86", "A87"]
    )
    assert consistency_check(rfd, mpnn) == []


def test_ligand_without_ligand_model_flagged():
    rfd = RFdiffusionAAJob(input_pdb="x.pdb", contig=_contig(), ligand="LIG")
    mpnn = LigandMPNNJob(
        pdb_path="s.pdb",
        fixed_residues=["A84", "A85", "A86", "A87"],
        model_type="protein_mpnn",
    )
    problems = consistency_check(rfd, mpnn)
    assert any("blind to the ligand" in p for p in problems)


def test_to_shell_is_quoted_string():
    job = RFdiffusionAAJob(input_pdb="x.pdb", contig=_contig(), ligand="LIG")
    shell = job.to_shell()
    assert isinstance(shell, str)
    assert "run_inference.py" in shell
