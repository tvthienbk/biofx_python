"""Recovery test for the hierarchical Normal (partial-pooling) model.

Checks that the non-centered model recovers the population-level parameters
``mu`` and ``tau`` (and ``sigma``) within their credible intervals. Fast by
design (light sampler, small data).

Run with:  python3 -m pytest test_recovery.py -q
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from shared.bayes_utils import check_recovery  # noqa: E402
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402


def test_recovers_population_params():
    data = generate()
    idata = fit(
        data,
        parameterization="noncentered",
        draws=600,
        tune=1000,
        chains=2,
        seed=7,
    )
    # population-level parameters are what partial pooling estimates well
    results = check_recovery(idata, data["truth"])
    for res in results:
        assert res.covered, f"94% HDI failed to cover truth: {res}"
        assert abs(res.z) < 3, f"posterior z-score too large: {res}"

    # and the non-centered parameterization should be (near) divergence-free
    n_div = int(idata.sample_stats["diverging"].sum())
    assert n_div <= 5, f"too many divergences for non-centered model: {n_div}"


if __name__ == "__main__":
    test_recovers_population_params()
    print("recovery test passed")
