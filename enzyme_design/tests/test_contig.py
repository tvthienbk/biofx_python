"""Tests for enzyme_design.contig."""

import pytest

from enzyme_design.contig import (
    Contig,
    ContigError,
    GapSegment,
    MotifSegment,
    build_contig,
    parse_contig,
)


def test_parse_hydra_wrapped():
    c = parse_contig("contigmap.contigs=['10-120,A84-87,10-120']", "150-150")
    assert len(c.segments) == 3
    assert isinstance(c.segments[0], GapSegment)
    assert isinstance(c.segments[1], MotifSegment)
    assert c.segments[1].chain == "A"
    assert c.segments[1].start == 84 and c.segments[1].end == 87
    assert c.length == (150, 150)


def test_motif_residues_flattened():
    c = parse_contig("['5-5,A84-87,5-5']")
    assert c.motif_residues() == ["A84", "A85", "A86", "A87"]


def test_length_range_computation():
    c = parse_contig("['10-120,A84-87,10-120']")
    # min = 10 + 4 + 10 = 24 ; max = 120 + 4 + 120 = 244
    assert c.length_range() == (24, 244)


def test_bare_integer_is_rejected():
    # The protocol's documented pitfall: a bare integer for a generated span.
    with pytest.raises(ContigError, match="bare integer"):
        parse_contig("['120,A84-87,10-120']")


def test_impossible_total_length_detected():
    c = parse_contig("['10-20,A84-87,10-20']", "150-150")
    problems = c.validate()
    assert any("impossible" in p for p in problems)


def test_consistent_total_length_passes():
    c = parse_contig("['10-120,A84-87,10-120']", "150-150")
    assert c.validate() == []


def test_no_motif_is_flagged():
    c = parse_contig("['10-120']")
    assert any("no motif" in p for p in c.validate())


def test_motif_end_before_start_errors():
    with pytest.raises(ContigError):
        MotifSegment(chain="A", start=90, end=80)


def test_multi_chain_letter_motif_errors():
    with pytest.raises(ContigError):
        MotifSegment(chain="AB", start=1, end=2)


def test_chain_break_zero_residues():
    c = parse_contig("['10-10,A84-84,/0,10-10']")
    # break contributes 0; total fixed = 10 + 1 + 0 + 10 = 21
    assert c.length_range() == (21, 21)


def test_build_contig_single_island():
    c = build_contig([("A", 84, 87)], flank=(10, 120), total_length=(150, 150))
    assert c.validate() == []
    contigs, length = c.to_hydra()
    assert contigs == "contigmap.contigs=['10-120,A84-87,10-120']"
    assert length == "contigmap.length='150-150'"


def test_build_contig_multi_island():
    c = build_contig(
        [("A", 84, 85), ("A", 120, 121)],
        flank=(10, 50),
        inter_island=(5, 30),
        total_length=(80, 120),
    )
    toks = c.to_contigs_string()
    assert toks == "10-50,A84-85,5-30,A120-121,10-50"
    assert c.validate() == []


def test_build_contig_impossible_length_raises():
    with pytest.raises(ContigError, match="impossible"):
        build_contig([("A", 84, 87)], flank=(10, 20), total_length=(500, 500))


def test_roundtrip_to_hydra_and_back():
    c1 = build_contig([("A", 10, 14)], flank=(20, 40), total_length=(50, 90))
    contigs, length = c1.to_hydra()
    c2 = parse_contig(contigs, length.split("=", 1)[1])
    assert c1.to_contigs_string() == c2.to_contigs_string()
    assert c1.length == c2.length
