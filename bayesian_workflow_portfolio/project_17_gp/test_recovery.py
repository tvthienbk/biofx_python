"""Recovery test for the GP model.

Two checks:
  1. The recoverable noise scalar ``sigma`` is recovered within tolerance.
  2. The GP posterior-mean curve tracks the *true latent function* at the
     training inputs within a tolerance (mean absolute error).

Designed to finish well under a minute with light sampling.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from shared.bayes_utils import check_recovery  # noqa: E402
from data.generate_data import generate  # noqa: E402
from model import fit, predict_curve  # noqa: E402


def test_recovers_sigma_and_curve():
    data = generate()
    idata = fit(data, draws=200, tune=350, chains=2, seed=7)
    # 1. identifiable scalar: noise sd
    (res,) = check_recovery(idata, data["truth"])
    assert res.covered, f"94% HDI failed to cover true sigma: {res}"
    assert abs(res.z) < 3, f"sigma posterior z-score too large: {res}"
    # 2. latent function recovery at the training inputs
    pred = predict_curve(data, idata, x_new=data["x"], seed=3)
    mae = float(np.mean(np.abs(pred["mean"] - data["f_true"])))
    assert mae < 0.25, f"GP mean does not track the true curve: MAE={mae:.3f}"


if __name__ == "__main__":
    test_recovers_sigma_and_curve()
    print("GP recovery test passed")
