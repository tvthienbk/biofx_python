"""Tests for enzyme_design.registry (Stage 6)."""

import pytest

from enzyme_design.registry import (
    ConstructRegistry,
    DesignRecord,
    RegistryError,
    free_cysteines,
    restriction_sites,
)


def test_free_cysteines():
    assert free_cysteines("ACDEFC") == [2, 6]
    assert free_cysteines("ADEFG") == []


def test_restriction_sites_both_strands():
    # NdeI = CATATG (palindrome); EcoRI = GAATTC (palindrome)
    dna = "AAACATATGAAAGAATTCAAA"
    sites = restriction_sites(dna)
    assert "NdeI" in sites and "EcoRI" in sites
    assert sites["NdeI"] == [3]


def test_restriction_site_reverse_complement_detected():
    # BsaI site GGTCTC ; its reverse complement is GAGACC
    dna = "TTTTGAGACCTTTT"
    sites = restriction_sites(dna)
    assert "BsaI" in sites


def test_design_record_rejects_nonstandard_residues():
    with pytest.raises(RegistryError, match="non-standard"):
        DesignRecord("d1", protein_seq="ACDEFGBZ")


def test_pre_synthesis_warnings():
    rec = DesignRecord(
        "d1",
        protein_seq="MAGCDEF",  # has a cysteine
        dna_seq="ATGGCTCATATGGGT",  # contains NdeI (CATATG), len 15 -> multiple of 3
    )
    warns = rec.pre_synthesis_warnings()
    assert any("cysteine" in w for w in warns)
    assert any("restriction" in w for w in warns)


def test_pre_synthesis_flags_bad_length():
    rec = DesignRecord("d1", protein_seq="MAGDEF", dna_seq="ATGGCG")  # len 6 ok
    assert not any("multiple of 3" in w for w in rec.pre_synthesis_warnings())
    rec2 = DesignRecord("d2", protein_seq="MAGDEF", dna_seq="ATGGC")  # len 5
    assert any("multiple of 3" in w for w in rec2.pre_synthesis_warnings())


def test_registry_add_get_duplicate():
    reg = ConstructRegistry()
    reg.add(DesignRecord("d1", protein_seq="MAGDEF", catalytic_residues=["A84"]))
    assert reg.get("d1").catalytic_residues == ["A84"]
    with pytest.raises(RegistryError, match="duplicate"):
        reg.add(DesignRecord("d1", protein_seq="MAGDEF"))


def test_panel_subselection():
    reg = ConstructRegistry()
    for i in range(5):
        reg.add(DesignRecord(f"d{i}", protein_seq="MAGDEF"))
    panel = reg.panel(["d1", "d3"])
    assert len(panel) == 2
    assert {r.design_id for r in panel} == {"d1", "d3"}


def test_csv_roundtrip(tmp_path):
    reg = ConstructRegistry()
    reg.add(
        DesignRecord(
            "design_0001",
            protein_seq="MAGDEFHIK",
            catalytic_residues=["A84", "A85"],
            cluster="fold_A",
            score=0.12,
            motif_ca_rmsd=0.6,
            plddt=93.0,
            worst_preorg=0.8,
        )
    )
    reg.add(DesignRecord("design_0002", protein_seq="MAGDEFHIK", score=None))
    path = tmp_path / "registry.csv"
    reg.to_csv(str(path))
    reloaded = ConstructRegistry.from_csv(str(path))
    assert len(reloaded) == 2
    r1 = reloaded.get("design_0001")
    assert r1.catalytic_residues == ["A84", "A85"]
    assert r1.score == pytest.approx(0.12)
    assert reloaded.get("design_0002").score is None
