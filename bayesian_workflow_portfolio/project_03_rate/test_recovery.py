"""Minimal recovery test: does the offset model recover the known log_rate?

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


def test_recovers_log_rate():
    data = generate()
    idata = fit(data, draws=500, tune=500, chains=2, seed=7)
    (res,) = check_recovery(idata, data["truth"])
    assert res.covered, f"94% HDI failed to cover truth: {res}"
    assert abs(res.z) < 3, f"posterior z-score too large: {res}"


def test_omitting_offset_biases_estimate():
    """The pitfall, asserted: dropping the exposure offset moves the estimate off."""
    data = generate()
    idata = fit(data, draws=500, tune=500, chains=2, seed=7, use_offset=False)
    (res,) = check_recovery(idata, data["truth"])
    # Without the offset the estimate is biased; the truth should NOT be covered.
    assert not res.covered, (
        "omitting the offset unexpectedly recovered the truth; "
        f"the bias demonstration is broken: {res}"
    )


if __name__ == "__main__":
    test_recovers_log_rate()
    test_omitting_offset_biases_estimate()
    print("recovery tests passed")
