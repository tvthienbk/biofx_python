"""Recovery test for the 1-compartment PK model (analytic solution).

Checks that the rate constant ``k`` and the volume ``V`` are recovered within
tolerance from the full design (which includes early + late timepoints, so the
two are identified). Uses the fast analytic model. Finishes well under a minute.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from shared.bayes_utils import check_recovery  # noqa: E402
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402


def test_recovers_k_and_V():
    data = generate()
    idata = fit(data, draws=400, tune=800, chains=2, seed=7)
    results = check_recovery(idata, {"k": data["truth"]["k"], "V": data["truth"]["V"]})
    for res in results:
        assert res.covered, f"94% HDI failed to cover truth: {res}"
        assert abs(res.z) < 3, f"posterior z-score too large: {res}"


if __name__ == "__main__":
    test_recovers_k_and_V()
    print("PK recovery test passed")
