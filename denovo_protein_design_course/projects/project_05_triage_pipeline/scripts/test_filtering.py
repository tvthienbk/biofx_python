#!/usr/bin/env python3
"""
test_filtering.py — unit tests for the SHARED 4-layer filter engine (Project 05's deliverable).

These tests assert the CONTRACT of shared/filtering_pipeline.py against the planted, clearly-synthetic
EXAMPLE_DATA designs from scripts/make_example_pool.py:

  * a planted known-GOOD design PASSES every layer for its type, and
  * each planted known-BAD design FAILS the SPECIFIC layer it was built to fail,
  * run_pipeline()/report() produce a ranked table + survival counts,
  * rank_designs() puts a good design above a layer-failing one.

DESIGN CHOICES
--------------
* Imports the COHORT'S SHARED module (`filtering_pipeline`) — this project iterates against the
  shared engine and PRs improvements back; it does NOT fork the module into the project.
* Runs with NO GPU and NO heavy deps (pure-Python scoring). Needs only numpy/pandas + the shared
  module (which needs numpy/pandas; Biopython is only touched if you pass PDB paths, which we don't).
* Plain `assert`s + a `__main__` runner so it works via `python scripts/test_filtering.py`
  (pytest also discovers the `test_*` functions if you have it, but pytest is NOT required).

Run:  python scripts/test_filtering.py
"""
from __future__ import annotations

import os
import sys

# Make the project's scripts/ and the cohort's shared/ importable, regardless of CWD.
_HERE = os.path.dirname(os.path.abspath(__file__))
_SHARED = os.path.abspath(os.path.join(_HERE, "..", "..", "..", "shared"))
sys.path.insert(0, _HERE)
sys.path.insert(0, _SHARED)

import filtering_pipeline as fp          # the SHARED engine — the thing under test
from make_example_pool import known_designs, GOOD_CENTERS, DESIGN_TYPES


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------
def _design_from_row(row: dict) -> fp.Design:
    """Build a fresh fp.Design from a planted EXAMPLE_DATA row (drop the non-Design columns)."""
    drop = {"truth", "note"}
    fields = {k: v for k, v in row.items() if k not in drop}
    # pandas/None hygiene: leave None as None; the layers treat missing metrics as "skip".
    return fp.Design(design_id=row["design_id"], sequence="M", **{
        k: v for k, v in fields.items() if k not in ("design_id",)
    })


def _cutoffs_for(dt: str) -> dict:
    return fp.DEFAULT_CUTOFFS.get(dt, fp.DEFAULT_CUTOFFS["monomer"])


def _planted() -> dict:
    """Map design_id -> planted row for the explicit fixtures."""
    return {r["design_id"]: r for r in known_designs()}


# --------------------------------------------------------------------------------------
# Layer 1 — self-consistency
# --------------------------------------------------------------------------------------
def test_layer1_good_passes_per_type():
    """Each planted known-good design passes Layer 1 for its own design type."""
    P = _planted()
    for dt in DESIGN_TYPES:
        row = P[f"EXAMPLE_DATA_GOOD_{dt}"]
        d = _design_from_row(row)
        assert fp.self_consistency(d, _cutoffs_for(dt)) is True, \
            f"known-good {dt} should pass L1"
        assert d.layers_passed >= 1


def test_layer1_bad_scrmsd_fails():
    row = _planted()["EXAMPLE_DATA_BAD_L1_scrmsd"]
    d = _design_from_row(row)
    assert fp.self_consistency(d, _cutoffs_for("monomer")) is False, \
        "high-scRMSD design must fail L1 (confident about the wrong fold)"


def test_layer1_bad_plddt_fails():
    row = _planted()["EXAMPLE_DATA_BAD_L1_plddt"]
    d = _design_from_row(row)
    assert fp.self_consistency(d, _cutoffs_for("monomer")) is False, \
        "low-pLDDT design must fail L1"


def test_layer1_enzyme_geom_fails():
    row = _planted()["EXAMPLE_DATA_BAD_L1_enzyme_geom"]
    d = _design_from_row(row)
    assert fp.self_consistency(d, _cutoffs_for("enzyme")) is False, \
        "enzyme with bad catalytic geometry must fail L1"


# --------------------------------------------------------------------------------------
# Layer 2 — orthogonal agreement
# --------------------------------------------------------------------------------------
def test_layer2_good_passes():
    row = _planted()["EXAMPLE_DATA_GOOD_monomer"]
    d = _design_from_row(row)
    assert fp.orthogonal_check(d) is True, "known-good design should pass L2"


def test_layer2_bad_orthogonal_fails():
    row = _planted()["EXAMPLE_DATA_BAD_L2_orthogonal"]
    d = _design_from_row(row)
    # passes L1 (AF2 likes it) but the second predictor disagrees → must fail L2.
    assert fp.self_consistency(d, _cutoffs_for("monomer")) is True, \
        "this fixture is meant to pass L1"
    assert fp.orthogonal_check(d) is False, \
        "orthogonal disagreement must fail L2 (predictor-specific overconfidence)"


# --------------------------------------------------------------------------------------
# Layer 3 — physics
# --------------------------------------------------------------------------------------
def test_layer3_good_passes():
    for dt in ("monomer", "binder"):
        row = _planted()[f"EXAMPLE_DATA_GOOD_{dt}"]
        d = _design_from_row(row)
        assert fp.physics_filter(d, _cutoffs_for(dt)) is True, f"known-good {dt} should pass L3"


def test_layer3_bad_solubility_fails():
    row = _planted()["EXAMPLE_DATA_BAD_L3_solubility"]
    d = _design_from_row(row)
    assert fp.physics_filter(d, _cutoffs_for("monomer")) is False, \
        "aggregation-prone design must fail L3 on solubility"


def test_layer3_bad_interface_fails():
    row = _planted()["EXAMPLE_DATA_BAD_L3_interface"]
    d = _design_from_row(row)
    assert fp.physics_filter(d, _cutoffs_for("binder")) is False, \
        "weak-interface binder must fail L3 (rosetta_dG / shape complementarity)"


# --------------------------------------------------------------------------------------
# Layer 4 — dynamics (optional)
# --------------------------------------------------------------------------------------
def test_layer4_good_passes():
    row = _planted()["EXAMPLE_DATA_GOOD_monomer"]
    d = _design_from_row(row)
    assert fp.dynamics_filter(d) is True, "stable known-good design should pass L4"


def test_layer4_bad_dynamics_fails():
    row = _planted()["EXAMPLE_DATA_BAD_L4_dynamics"]
    d = _design_from_row(row)
    # passes the static layers but melts under MD → only L4 catches it.
    assert fp.self_consistency(d, _cutoffs_for("monomer")) is True
    assert fp.physics_filter(d, _cutoffs_for("monomer")) is True
    assert fp.dynamics_filter(d) is False, "folds-but-melts design must fail L4 (MD drift)"


# --------------------------------------------------------------------------------------
# Orchestration: run_pipeline / report / rank_designs
# --------------------------------------------------------------------------------------
def test_run_pipeline_survival_and_report():
    """The good monomer survives L1-L3; the L1-failing design does not; report() runs."""
    P = _planted()
    good = _design_from_row(P["EXAMPLE_DATA_GOOD_monomer"])
    bad = _design_from_row(P["EXAMPLE_DATA_BAD_L1_scrmsd"])
    df = fp.run_pipeline([good, bad], design_type="monomer", use_layers=(1, 2, 3))
    survival = df.attrs.get("survival", {})
    assert survival.get("L1") == 1, "exactly one of the two should survive L1"
    assert df.attrs.get("n_total") == 2
    # report() should run headlessly and return a top table.
    import matplotlib
    matplotlib.use("Agg")
    top = fp.report(df, top_n=5)
    assert top is not None and len(top) == 2


def test_ranking_orders_good_above_bad():
    """rank_designs() should rank the all-layers-passing design above a layer-failing one."""
    P = _planted()
    good = _design_from_row(P["EXAMPLE_DATA_GOOD_monomer"])
    bad = _design_from_row(P["EXAMPLE_DATA_BAD_L1_scrmsd"])
    # run the layers first so layers_passed is populated, then rank.
    fp.run_pipeline([good, bad], design_type="monomer", use_layers=(1, 2, 3))
    ranked = fp.rank_designs([good, bad])
    assert ranked[0].design_id == good.design_id, \
        "the design passing more layers should rank first"


# --------------------------------------------------------------------------------------
# Runner (no pytest required)
# --------------------------------------------------------------------------------------
def _all_tests():
    return [obj for name, obj in sorted(globals().items())
            if name.startswith("test_") and callable(obj)]


def main() -> int:
    tests = _all_tests()
    failures = []
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as e:
            failures.append((t.__name__, str(e)))
            print(f"  FAIL  {t.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            failures.append((t.__name__, repr(e)))
            print(f"  ERROR {t.__name__}: {e!r}")
    print(f"\n{len(tests) - len(failures)}/{len(tests)} tests passed.")
    if failures:
        print("FAILURES:")
        for name, msg in failures:
            print(f"  - {name}: {msg}")
        return 1
    print("All tests passed against the SHARED filtering_pipeline. "
          "(All fixtures are EXAMPLE_DATA — synthetic, not real results.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
