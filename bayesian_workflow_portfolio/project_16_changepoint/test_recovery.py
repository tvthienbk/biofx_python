"""Recovery test for the change-point model.

We target the pre/post Poisson rates (``lam0``, ``lam1``) — clearly identifiable —
and check that the change-point ``tau`` is located near the truth via its
posterior mode (a multimodal tau is summarized by mode/HDI, not mean, but here the
posterior is sharp). Fast (<20 s).

Run with:  python3 -m pytest test_recovery.py -q
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from shared.bayes_utils import check_recovery  # noqa: E402
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402


def test_recovers_rates_and_tau():
    data = generate()
    idata = fit(data, draws=800, tune=1000, chains=2, seed=7)

    # Pre/post rates: HDI must cover truth.
    truths = {"lam0": data["truth"]["lam0"], "lam1": data["truth"]["lam1"]}
    for res in check_recovery(idata, truths):
        assert res.covered, f"94% HDI failed to cover truth: {res}"
        assert abs(res.z) < 3.5, f"posterior z-score too large: {res}"

    # tau: posterior MODE should be within +/-2 of the true change index.
    tau_draws = idata.posterior["tau"].values.ravel().astype(int)
    mode = np.bincount(tau_draws).argmax()
    assert abs(mode - data["truth"]["tau"]) <= 2, (
        f"tau mode {mode} far from truth {data['truth']['tau']}"
    )


if __name__ == "__main__":
    test_recovers_rates_and_tau()
    print("recovery test passed")
