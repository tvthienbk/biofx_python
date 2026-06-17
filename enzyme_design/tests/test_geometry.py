"""Tests for enzyme_design.geometry (PDB parsing + Kabsch RMSD)."""

import math
import os

import numpy as np
import pytest

from enzyme_design.geometry import (
    kabsch_rmsd,
    ligand_rmsd,
    motif_ca_rmsd,
    parse_pdb,
)

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


def _load(name):
    with open(os.path.join(EXAMPLES, name)) as fh:
        return parse_pdb(fh.read())


def test_parse_counts_atoms():
    s = _load("active_site.pdb")
    assert len(s) == 28
    assert len(s.select(records=["HETATM"])) == 4
    assert {a.res_name for a in s.select(records=["HETATM"])} == {"LIG"}


def test_ca_by_residue_keys():
    s = _load("active_site.pdb")
    ca = s.ca_by_residue()
    assert set(["A84", "A85", "A86", "A87"]).issubset(ca)


def test_kabsch_identity_is_zero():
    p = np.random.default_rng(0).normal(size=(10, 3))
    assert kabsch_rmsd(p, p.copy()) == pytest.approx(0.0, abs=1e-9)


def test_kabsch_invariant_to_rigid_transform():
    rng = np.random.default_rng(1)
    p = rng.normal(size=(12, 3))
    theta = 0.7
    rot = np.array(
        [[math.cos(theta), -math.sin(theta), 0],
         [math.sin(theta), math.cos(theta), 0],
         [0, 0, 1]]
    )
    q = p @ rot.T + np.array([3.0, -2.0, 5.0])
    # superposed RMSD should recover ~0 despite the rigid motion
    assert kabsch_rmsd(p, q, superpose=True) == pytest.approx(0.0, abs=1e-6)
    # raw RMSD should be large
    assert kabsch_rmsd(p, q, superpose=False) > 1.0


def test_kabsch_known_displacement_no_superpose():
    p = np.zeros((4, 3))
    q = np.zeros((4, 3))
    q[:, 0] = 2.0  # every point shifted 2 A along x
    assert kabsch_rmsd(p, q, superpose=False) == pytest.approx(2.0)


def test_kabsch_shape_mismatch_raises():
    with pytest.raises(ValueError):
        kabsch_rmsd(np.zeros((3, 3)), np.zeros((4, 3)))


def test_motif_ca_rmsd_on_examples_is_small():
    d = _load("active_site.pdb")
    p = _load("active_site_predicted.pdb")
    res = ["A84", "A85", "A86", "A87"]
    # predicted is a rigid transform + ~0.08 A noise -> superposed RMSD sub-A
    assert motif_ca_rmsd(d, p, res, superpose=True) < 0.5
    # without superposition the rigid motion dominates
    assert motif_ca_rmsd(d, p, res, superpose=False) > 1.0


def test_motif_ca_rmsd_missing_residue_raises():
    d = _load("active_site.pdb")
    p = _load("active_site_predicted.pdb")
    with pytest.raises(ValueError, match="missing"):
        motif_ca_rmsd(d, p, ["A999"])


def test_ligand_rmsd_self_is_zero():
    d = _load("active_site.pdb")
    assert ligand_rmsd(d, d, "LIG") == pytest.approx(0.0, abs=1e-9)
