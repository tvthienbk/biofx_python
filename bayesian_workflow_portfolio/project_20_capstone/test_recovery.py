"""Recovery test for the hierarchical capstone model.

Checks:
  1. Population parameters mu and tau are recovered within tolerance.
  2. The decision layer identifies the TRUE best compound (or a strong contender):
     the min-expected-regret recommendation matches the true best, AND it differs
     from the naive raw-mean winner (the winner's-curse trap is corrected).

Uses light sampling; finishes well under a minute.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from shared.bayes_utils import check_recovery  # noqa: E402
from data.generate_data import generate  # noqa: E402
from model import fit, decision_table  # noqa: E402


def test_recovers_population_and_decision():
    data = generate()
    idata = fit(data, draws=400, tune=800, chains=2, seed=7)
    # 1. population parameters
    results = check_recovery(idata, {"mu": data["truth"]["mu"],
                                     "tau": data["truth"]["tau"]})
    for res in results:
        assert res.covered, f"94% HDI failed to cover truth: {res}"
        assert abs(res.z) < 3, f"posterior z-score too large: {res}"
    # 2. decision recovers the true best compound
    dec = decision_table(idata)
    raw_pick = int(np.argmax(data["raw_means"]))
    assert dec["recommend_min_regret"] == data["best_true"], (
        f"min-regret pick #{dec['recommend_min_regret']} != "
        f"true best #{data['best_true']}")
    # and the partial-pooling decision differs from the raw-mean winner's curse
    assert raw_pick != data["best_true"], "test setup should exhibit winner's curse"


if __name__ == "__main__":
    test_recovers_population_and_decision()
    print("capstone recovery + decision test passed")
