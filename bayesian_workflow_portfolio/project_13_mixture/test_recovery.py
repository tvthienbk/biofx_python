"""Recovery test for the 2-component mixture.

We target **identifiable, label-invariant** quantities — the separation between
the component means, the shared sigma, and the weight of the higher-mean
component — rather than raw per-label parameters, which are only identified once
the ordered transform is in place. Designed to finish well under a minute.

Run with:  python3 -m pytest test_recovery.py -q
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from shared.bayes_utils import check_recovery  # noqa: E402
from data.generate_data import generate  # noqa: E402
from model import fit, add_separation  # noqa: E402


def test_recovers_mixture():
    data = generate()
    idata = fit(data, draws=500, tune=1000, chains=2, seed=7)
    add_separation(idata)
    truths = {
        "separation": data["truth"]["separation"],
        "sigma": data["truth"]["sigma"],
        "w_high": data["truth"]["w[1]"],
        "mu_low": data["truth"]["mu[0]"],
        "mu_high": data["truth"]["mu[1]"],
    }
    results = check_recovery(idata, truths)
    for res in results:
        assert res.covered, f"94% HDI failed to cover truth: {res}"
        assert abs(res.z) < 3.5, f"posterior z-score too large: {res}"


if __name__ == "__main__":
    test_recovers_mixture()
    print("recovery test passed")
