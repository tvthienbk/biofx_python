"""Recovery test for the errors-in-variables model.

The central claim of the project: the EIV model recovers the true regression
coefficients (alpha, beta) that the naive regression *attenuates*. We assert the
EIV model covers the true (alpha, beta) and that its slope is materially closer to
the truth than the naive slope. Fast by design.

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


def test_eiv_recovers_slope_naive_attenuates():
    data = generate()
    truth = {k: data["truth"][k] for k in ("alpha", "beta")}

    eiv = fit(data, model="eiv", draws=800, tune=1500, chains=2,
              target_accept=0.95, seed=7)
    for res in check_recovery(eiv, truth):
        assert res.covered, f"EIV 94% HDI failed to cover truth: {res}"
        assert abs(res.z) < 3, f"EIV posterior z-score too large: {res}"

    # The naive model should attenuate the slope (biased toward 0).
    naive = fit(data, model="naive", draws=600, tune=800, chains=2, seed=7)
    beta_naive = float(naive.posterior["beta"].mean())
    beta_eiv = float(eiv.posterior["beta"].mean())
    true_beta = data["truth"]["beta"]
    assert beta_naive < true_beta - 0.2, f"naive slope not attenuated: {beta_naive}"
    assert abs(beta_eiv - true_beta) < abs(beta_naive - true_beta), (
        f"EIV ({beta_eiv}) not closer to truth ({true_beta}) than naive ({beta_naive})"
    )


if __name__ == "__main__":
    test_eiv_recovers_slope_naive_attenuates()
    print("recovery test passed")
