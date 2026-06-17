"""Tests for metrics, preorg, and selection (Stage 5 filtering)."""

import json
import os

import pytest

from enzyme_design.metrics import SelfConsistency, Thresholds, read_metrics_csv
from enzyme_design.preorg import (
    PreorgProfile,
    StepEnsemble,
    preorg_from_rmsd_samples,
)
from enzyme_design.selection import rank_designs, select_diverse

EXAMPLES = os.path.join(os.path.dirname(__file__), "..", "examples")


# ----- metrics -------------------------------------------------------------
def test_self_consistency_pass():
    m = SelfConsistency("d1", rmsd=0.9, motif_ca_rmsd=0.6, plddt=93, min_pae=2.1,
                        ligand_rmsd=1.2, ptm=0.89, iptm=0.86)
    ok, reasons = m.evaluate()
    assert ok and reasons == []


def test_self_consistency_fail_reports_each_reason():
    m = SelfConsistency("d3", rmsd=2.6, motif_ca_rmsd=1.9, plddt=72, min_pae=7.8,
                        ligand_rmsd=6.1, ptm=0.71, iptm=0.65)
    ok, reasons = m.evaluate()
    assert not ok
    joined = " ".join(reasons)
    for token in ["rmsd", "motif_ca_rmsd", "plddt", "min_pae", "ligand_rmsd", "ptm", "iptm"]:
        assert token in joined


def test_missing_rmsd_cannot_be_judged():
    m = SelfConsistency("dX", plddt=95)
    ok, reasons = m.evaluate()
    assert not ok
    assert any("no RMSD" in r for r in reasons)


def test_none_metric_is_skipped_not_failed():
    # only rmsd measured and it passes; everything else None -> overall pass
    m = SelfConsistency("dY", rmsd=1.0)
    assert m.passes()


def test_custom_thresholds():
    m = SelfConsistency("dZ", rmsd=1.8, motif_ca_rmsd=1.4)
    assert m.passes(Thresholds(max_rmsd=2.0, max_motif_ca_rmsd=1.5))
    assert not m.passes(Thresholds(max_rmsd=1.5))


def test_read_metrics_csv():
    rows = read_metrics_csv(os.path.join(EXAMPLES, "af2_metrics.csv"))
    assert len(rows) == 8
    d1 = next(r for r in rows if r.design_id == "design_0001")
    assert d1.plddt == 93.0


# ----- preorg --------------------------------------------------------------
def test_step_score_monotone():
    good = StepEnsemble("ts1", mean_rmsd=0.5, rmsd_std=0.1, contact_fraction=1.0)
    bad = StepEnsemble("ts1", mean_rmsd=2.0, rmsd_std=0.8, contact_fraction=0.5)
    assert bad.score() > good.score()


def test_contact_fraction_bounds():
    with pytest.raises(ValueError):
        StepEnsemble("x", 0.5, 0.1, contact_fraction=1.5)


def test_worst_step_drives_ranking_not_mean():
    # A design great everywhere except one terrible step must rank by that step.
    samples = {
        "michaelis": [0.4, 0.5, 0.4],
        "ts1": [0.5, 0.6, 0.5],
        "intermediate": [2.4, 2.6, 2.5],  # the bad step
        "product": [0.4, 0.5, 0.4],
    }
    prof = preorg_from_rmsd_samples("d", samples, {"intermediate": 0.5})
    worst = prof.worst_step()
    assert worst.state == "intermediate"
    # worst_score >> mean_score
    assert prof.worst_score() > prof.mean_score()
    assert not prof.passes()
    assert "intermediate" in prof.failing_steps()


def test_well_preorganised_passes():
    samples = {s: [0.4, 0.5, 0.45] for s in ["michaelis", "ts1", "product"]}
    prof = preorg_from_rmsd_samples("d", samples)
    assert prof.passes()
    assert prof.failing_steps() == []


def test_empty_samples_raises():
    with pytest.raises(ValueError):
        preorg_from_rmsd_samples("d", {"ts1": []})


# ----- selection -----------------------------------------------------------
def _build_inputs():
    rows = read_metrics_csv(os.path.join(EXAMPLES, "af2_metrics.csv"))
    with open(os.path.join(EXAMPLES, "preorg_ensembles.json")) as fh:
        data = json.load(fh)
    profiles = {}
    for did, d in data["designs"].items():
        profiles[did] = preorg_from_rmsd_samples(
            did, d["rmsd_samples"], d.get("contacts")
        )
    return rows, profiles


def test_rank_designs_orders_passing_first():
    rows, profiles = _build_inputs()
    clusters = {  # two topology clusters
        "design_0001": "fold_A", "design_0006": "fold_A", "design_0004": "fold_A",
        "design_0002": "fold_B", "design_0005": "fold_B", "design_0008": "fold_B",
        "design_0003": "fold_C", "design_0007": "fold_C",
    }
    ranked = rank_designs(rows, profiles, clusters)
    # passing designs come first
    passing = [r for r in ranked if r.passes_filters]
    assert ranked[: len(passing)] == passing
    # design_0003/0007 fail self-consistency; design_0004 fails preorg at intermediate
    by_id = {r.design_id: r for r in ranked}
    assert not by_id["design_0003"].passes_filters
    assert not by_id["design_0004"].passes_filters
    assert any("intermediate" in r for r in by_id["design_0004"].reasons)
    # best design should be the all-around strong one
    assert ranked[0].design_id == "design_0006"


def test_select_diverse_respects_clusters():
    rows, profiles = _build_inputs()
    clusters = {
        "design_0001": "fold_A", "design_0006": "fold_A",
        "design_0002": "fold_B", "design_0008": "fold_B",
        "design_0005": "fold_B",
    }
    ranked = rank_designs(rows, profiles, clusters)
    chosen = select_diverse(ranked, n=2, per_cluster=1)
    assert len(chosen) == 2
    assert len({c.cluster for c in chosen}) == 2  # one per cluster


def test_select_diverse_fills_when_clusters_exhausted():
    rows, profiles = _build_inputs()
    clusters = {r.design_id: "only_one" for r in rows}
    ranked = rank_designs(rows, profiles, clusters)
    chosen = select_diverse(ranked, n=3, per_cluster=1)
    # only one cluster, but we still fill up to n in pass 2
    assert len(chosen) == 3
