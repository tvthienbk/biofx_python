"""Minimal recovery test: does the Student-t (robust) model recover the CLEAN
calibration line (alpha, beta) despite the outliers?

Run with:  python3 -m pytest test_recovery.py -q
Designed to finish in well under a minute.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from shared.bayes_utils import check_recovery  # noqa: E402
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402


def test_robust_recovers_clean_line():
    data = generate()
    idata = fit(data, model="studentt", draws=600, tune=600, chains=2, seed=7)
    # We check the calibration line (alpha, beta) — the scientifically meaningful
    # parameters. We do NOT assert on sigma: the data carry Normal noise of SD 0.6,
    # but the Student-t fits a *scale* whose relation to the marginal SD depends on
    # nu (Var = sigma^2 * nu/(nu-2) for nu>2, undefined for small nu). With heavy
    # tails the estimated scale is legitimately below 0.6, so comparing it to the
    # Normal SD would be apples-to-oranges.
    line_truth = {k: data["truth"][k] for k in ("alpha", "beta")}
    results = check_recovery(idata, line_truth)
    for res in results:
        assert res.covered, f"94% HDI failed to cover truth: {res}"
        assert abs(res.z) < 3, f"posterior z-score too large: {res}"


if __name__ == "__main__":
    test_robust_recovers_clean_line()
    print("recovery test passed")
