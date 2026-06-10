"""Recovery test for the varying-slopes (LKJ) model.

Checks that the correlated, non-centered model recovers the population-level
parameters — the mean intercept/slope, the random-effect SDs, and the observation
noise — within their credible intervals, and that the intercept-slope correlation
``rho`` is covered (it is only loosely identified with G=8 lines, so we check
coverage, not a tight z-score). Fast by design.

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
        correlated=True,
        draws=700,
        tune=1000,
        chains=2,
        target_accept=0.9,
        seed=7,
    )
    # Well-identified population params: require coverage + bounded z.
    well = {k: data["truth"][k] for k in ("mu_a", "mu_b", "sd_a", "sd_b", "sigma")}
    for res in check_recovery(idata, well):
        assert res.covered, f"94% HDI failed to cover truth: {res}"
        assert abs(res.z) < 3, f"posterior z-score too large: {res}"

    # rho is loosely identified with few groups: coverage only.
    (rho_res,) = check_recovery(idata, {"rho": data["truth"]["rho"]})
    assert rho_res.covered, f"94% HDI failed to cover rho: {rho_res}"

    # non-centered LKJ model should be (near) divergence-free
    n_div = int(idata.sample_stats["diverging"].sum())
    assert n_div <= 8, f"too many divergences: {n_div}"


if __name__ == "__main__":
    test_recovers_population_params()
    print("recovery test passed")
