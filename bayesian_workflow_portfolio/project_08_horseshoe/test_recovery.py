"""Minimal recovery test: does the horseshoe recover the nonzero coefficients
AND shrink the true-zero coefficients toward zero?

Run with:  python3 -m pytest test_recovery.py -q
Designed to finish in well under a minute.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import arviz as az  # noqa: E402
import xarray as xr  # noqa: E402

from shared.bayes_utils import check_recovery  # noqa: E402
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402


def _scalarize_beta(idata, truth):
    """ArviZ's var_names match the VARIABLE name (``beta``), not coordinate labels
    like ``beta[2]``. So we lift the selected coefficients into their own scalar
    posterior variables named exactly like the truth keys, and hand check_recovery
    a small InferenceData it can summarize directly.
    """
    post = idata.posterior
    data_vars = {}
    for key in truth:  # keys look like 'beta[2]'
        j = int(key.split("[")[1].rstrip("]"))
        data_vars[key] = post["beta"].isel(beta_dim_0=j).drop_vars(
            "beta_dim_0", errors="ignore")
    return az.InferenceData(posterior=xr.Dataset(data_vars))


def test_horseshoe_recovers_sparse_truth():
    data = generate()
    idata = fit(data, model="horseshoe", draws=350, tune=500, chains=2, seed=7,
                target_accept=0.95)
    # 1. nonzero coefficients recovered within tolerance
    scalar_idata = _scalarize_beta(idata, data["truth"])
    results = check_recovery(scalar_idata, data["truth"])
    for res in results:
        assert res.covered, f"94% HDI failed to cover truth: {res}"
        assert abs(res.z) < 3, f"posterior z-score too large: {res}"
    # 2. sparsity: true-zero coefficients shrunk near zero
    bmean = idata.posterior["beta"].mean(("chain", "draw")).values
    zeros = [j for j in range(data["p"]) if j not in data["nonzero_idx"]]
    assert np.max(np.abs(bmean[zeros])) < 0.5, "horseshoe failed to shrink true zeros"
    # 3. sampler health: no flood of divergences from the funnel
    n_div = int(idata.sample_stats["diverging"].sum())
    assert n_div < 20, f"too many divergences ({n_div}); check parameterization"


if __name__ == "__main__":
    test_horseshoe_recovers_sparse_truth()
    print("recovery test passed")
