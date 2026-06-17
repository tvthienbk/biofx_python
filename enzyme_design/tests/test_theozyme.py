"""Tests for enzyme_design.theozyme."""

import pytest

from enzyme_design.theozyme import (
    AtomMap,
    ConstraintBlock,
    GeometricConstraint,
    Theozyme,
    TheozymeError,
    parse_cst,
)


def _demo_block():
    return ConstraintBlock(
        res1=AtomMap(1, ["OG", "CB", "CA"], ["SER"]),
        res2=AtomMap(2, ["C1", "O1"], ["LIG"]),
        constraints=[
            GeometricConstraint("distanceAB", 2.8, 0.2, 100.0),
            GeometricConstraint("angle_A", 109.5, 5.0, 50.0, 360.0),
        ],
    )


def test_atom_map_requires_1_to_3_atoms():
    with pytest.raises(TheozymeError):
        AtomMap(1, [], ["SER"])
    with pytest.raises(TheozymeError):
        AtomMap(1, ["A", "B", "C", "D"], ["SER"])


def test_atom_map_index_must_be_1_or_2():
    with pytest.raises(TheozymeError):
        AtomMap(3, ["OG"], ["SER"])


def test_unknown_constraint_keyword_rejected():
    with pytest.raises(TheozymeError):
        GeometricConstraint("distanceXY", 2.8, 0.2, 100.0)


def test_block_requires_index_order():
    a1 = AtomMap(1, ["OG"], ["SER"])
    a2 = AtomMap(2, ["C1"], ["LIG"])
    with pytest.raises(TheozymeError):
        ConstraintBlock(res1=a2, res2=a1)  # swapped


def test_serialise_contains_expected_tokens():
    theo = Theozyme([_demo_block()], title="demo")
    cst = theo.to_cst()
    assert "CST::BEGIN" in cst and "CST::END" in cst
    assert "ATOM_MAP: 1 atom_name: OG CB CA" in cst
    assert "residue3: SER" in cst
    assert "distanceAB" in cst


def test_roundtrip_parse():
    theo = Theozyme([_demo_block()], title="demo")
    parsed = parse_cst(theo.to_cst())
    assert len(parsed.blocks) == 1
    b = parsed.blocks[0]
    assert b.res1.atoms == ["OG", "CB", "CA"]
    assert b.res1.residue3 == ["SER"]
    assert b.res2.residue3 == ["LIG"]
    kinds = {c.kind for c in b.constraints}
    assert "distanceAB" in kinds and "angle_A" in kinds


def test_validate_flags_missing_distance():
    block = ConstraintBlock(
        res1=AtomMap(1, ["OG"], ["SER"]),
        res2=AtomMap(2, ["C1"], ["LIG"]),
        constraints=[GeometricConstraint("angle_A", 109.5, 5.0, 50.0, 360.0)],
    )
    theo = Theozyme([block])
    assert any("distanceAB" in p for p in theo.validate())


def test_validate_flags_duplicate_constraint():
    block = ConstraintBlock(
        res1=AtomMap(1, ["OG"], ["SER"]),
        res2=AtomMap(2, ["C1"], ["LIG"]),
        constraints=[
            GeometricConstraint("distanceAB", 2.8, 0.2, 100.0),
            GeometricConstraint("distanceAB", 3.0, 0.2, 100.0),
        ],
    )
    assert any("duplicate" in p for p in Theozyme([block]).validate())


def test_catalytic_residues_dedup_and_order():
    theo = Theozyme(
        [
            _demo_block(),
            ConstraintBlock(
                res1=AtomMap(1, ["NE2"], ["HIS"]),
                res2=AtomMap(2, ["OG"], ["SER"]),
                constraints=[GeometricConstraint("distanceAB", 2.7, 0.2, 100.0)],
            ),
        ]
    )
    assert theo.catalytic_residues() == ["SER", "HIS"]


def test_ambiguous_residue_list_roundtrips():
    block = ConstraintBlock(
        res1=AtomMap(1, ["OD1", "CG"], ["ASP", "GLU"]),
        res2=AtomMap(2, ["NE2"], ["HIS"]),
        constraints=[GeometricConstraint("distanceAB", 2.7, 0.2, 100.0)],
    )
    parsed = parse_cst(Theozyme([block]).to_cst())
    assert parsed.blocks[0].res1.residue3 == ["ASP", "GLU"]


def test_unterminated_block_raises():
    with pytest.raises(TheozymeError, match="unterminated"):
        parse_cst("CST::BEGIN\n  TEMPLATE::   ATOM_MAP: 1 atom_name: OG ,\n")
