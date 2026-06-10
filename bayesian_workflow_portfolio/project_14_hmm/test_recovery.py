"""Recovery test for the marginalized 2-state HMM.

We target the transition probabilities, the (ordered) emission means, the
separation, and sigma. These are identified once the emission means are ordered
to break the state-label symmetry. Designed to finish in ~1 minute.

Run with:  python3 -m pytest test_recovery.py -q
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from shared.bayes_utils import check_recovery  # noqa: E402
from data.generate_data import generate  # noqa: E402
from model import fit, add_named  # noqa: E402


def test_recovers_hmm():
    data = generate()
    idata = fit(data, draws=400, tune=800, chains=2, seed=7)
    add_named(idata)
    t = data["truth"]
    truths = {
        "mu_low": t["mu[0]"],
        "mu_high": t["mu[1]"],
        "separation": t["separation"],
        "sigma": t["sigma"],
        "p01": t["p01"],
        "p10": t["p10"],
    }
    results = check_recovery(idata, truths)
    for res in results:
        assert res.covered, f"94% HDI failed to cover truth: {res}"
        assert abs(res.z) < 3.5, f"posterior z-score too large: {res}"


if __name__ == "__main__":
    test_recovers_hmm()
    print("recovery test passed")
