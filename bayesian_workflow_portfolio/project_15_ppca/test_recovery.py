"""Recovery test for probabilistic PCA.

We deliberately target **rotation-invariant, identifiable** quantities — the noise
``sigma`` and the reconstructed covariance ``C = W Wᵀ + sigma^2 I`` (via its trace
``total_var`` and a Frobenius-norm check) — NOT the raw loadings ``W``, which are
identified only up to an orthogonal rotation and would fail any direct recovery
test. Designed to finish in ~40 s.

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
from model import fit, add_identifiable, reconstructed_cov  # noqa: E402


def test_recovers_identifiable_quantities():
    data = generate()
    idata = fit(data, draws=500, tune=1000, chains=2, seed=7)
    add_identifiable(idata)

    # 1) sigma and total_var: HDI must cover the known truth.
    truths = {
        "sigma": data["truth"]["sigma"],
        "total_var": data["truth"]["total_var"],
    }
    for res in check_recovery(idata, truths):
        assert res.covered, f"94% HDI failed to cover truth: {res}"
        assert abs(res.z) < 3.5, f"posterior z-score too large: {res}"

    # 2) The reconstructed covariance (rotation-invariant) must be close to truth.
    C_hat = reconstructed_cov(idata)
    rel_err = np.linalg.norm(C_hat - data["C_true"]) / np.linalg.norm(data["C_true"])
    assert rel_err < 0.20, f"reconstructed covariance off by {rel_err:.3f} (rel Frobenius)"


if __name__ == "__main__":
    test_recovers_identifiable_quantities()
    print("recovery test passed")
