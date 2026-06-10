"""Minimal recovery test: does inference recover the known mu and sigma?

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


def test_recovers_mu_and_sigma():
    data = generate()
    idata = fit(data, draws=500, tune=500, chains=2, seed=7)
    results = check_recovery(idata, data["truth"])
    for res in results:
        assert res.covered, f"94% HDI failed to cover truth: {res}"
        assert abs(res.z) < 3, f"posterior z-score too large: {res}"


if __name__ == "__main__":
    test_recovers_mu_and_sigma()
    print("recovery test passed")
