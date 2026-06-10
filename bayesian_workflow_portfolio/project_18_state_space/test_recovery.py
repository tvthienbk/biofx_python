"""Recovery test for the local-level state-space model.

Checks:
  1. Both variances (sigma_level, sigma_obs) are recovered within tolerance.
  2. The latent level trajectory is recovered (mean absolute error vs truth).

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
from model import fit  # noqa: E402


def test_recovers_variances_and_level():
    data = generate()
    idata = fit(data, draws=400, tune=800, chains=2, seed=7)
    results = check_recovery(idata, data["truth"])
    for res in results:
        assert res.covered, f"94% HDI failed to cover truth: {res}"
        assert abs(res.z) < 3, f"posterior z-score too large: {res}"
    # latent trajectory recovery
    lvl = idata.posterior["level"].mean(dim=("chain", "draw")).values
    mae = float(np.mean(np.abs(lvl - data["level_true"])))
    assert mae < 0.5, f"latent level not recovered: MAE={mae:.3f}"


if __name__ == "__main__":
    test_recovers_variances_and_level()
    print("state-space recovery test passed")
