"""Simulation-Based Calibration (SBC) for the regularized horseshoe.

SBC for a sparse, high-dimensional model is expensive, so we keep it SMALL and
calibrate just a couple of coefficients, as the brief allows. The logic:

  1. Draw a full beta vector from the horseshoe prior (most entries ~0, a few
     escape shrinkage), plus beta0 and sigma.
  2. Simulate a dataset of size N.
  3. Fit the (non-centered) horseshoe; obtain L posterior draws of beta.
  4. Record the rank of each chosen coefficient's true value among the L draws.

Calibrated inference => ranks uniform. Because horseshoe priors are heavy-tailed
and the model is high-dimensional, we draw the prior via PyMC's own
sample_prior_predictive on the model (so the simulator and model share EXACTLY the
same prior, the key to a valid SBC), use a small P, few sims, and short chains.

This runs in ~1-2 minutes. SBC here certifies the inference machinery on the
sparse-coefficient targets; sparsity recovery itself is checked in test_recovery.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from shared.bayes_utils import assert_calibrated, sbc_rank  # noqa: E402
from model import build_model  # noqa: E402

import pymc as pm  # noqa: E402

P = 8            # small predictor count for tractable SBC
N_OBS = 60
N_SIMS = 12
L = 200
TAU0 = 0.3
CALIB_IDX = (0, 1)   # the two coefficients we calibrate
SEED = 20240601


def run_sbc(seed: int = SEED) -> dict:
    rng = np.random.default_rng(seed)
    X = rng.normal(0.0, 1.0, size=(N_OBS, P))
    X = (X - X.mean(0)) / X.std(0)
    ranks = {f"beta[{j}]": np.empty(N_SIMS, int) for j in CALIB_IDX}
    base = {"X": X, "y": np.zeros(N_OBS), "n": N_OBS, "p": P}
    for i in range(N_SIMS):
        # 1. draw the prior from the model itself (simulator == model prior)
        with build_model(base, model="horseshoe", tau0=TAU0):
            prior = pm.sample_prior_predictive(
                draws=1, random_seed=int(rng.integers(1, 1_000_000)))
        beta_star = prior.prior["beta"].values.reshape(-1)[:P]
        beta0_star = float(prior.prior["beta0"].values.reshape(-1)[0])
        sigma_star = float(prior.prior["sigma"].values.reshape(-1)[0])
        # 2. simulate data
        y = beta0_star + X @ beta_star + rng.normal(0.0, sigma_star, size=N_OBS)
        data = {"X": X, "y": y, "n": N_OBS, "p": P}
        # 3. fit
        with build_model(data, model="horseshoe", tau0=TAU0):
            idata = pm.sample(
                draws=L // 2, tune=400, chains=2, target_accept=0.95,
                random_seed=int(rng.integers(1, 1_000_000)),
                progressbar=False, compute_convergence_checks=False,
            )
        post = idata.posterior["beta"].values  # (chain, draw, P)
        flat = post.reshape(-1, P)
        for j in CALIB_IDX:
            ranks[f"beta[{j}]"][i] = sbc_rank(beta_star[j], flat[:, j])
    return ranks


def main() -> None:
    ranks = run_sbc()
    print(f"SBC over {N_SIMS} simulations (P={P}, N={N_OBS}, L~{L})")
    for name, r in ranks.items():
        rep = assert_calibrated(r, n_bins=4)
        print(f"  {name}: chi2={rep['chi2']:.2f}, dof={rep['dof']}, "
              f"p={rep['pvalue']:.3f}, uniform={rep['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, len(ranks), figsize=(4 * len(ranks), 3.5))
        for ax, (name, r) in zip(np.atleast_1d(axes), ranks.items()):
            ax.hist(r, bins=4, color="#4C72B0", edgecolor="white")
            ax.axhline(N_SIMS / 4, color="k", ls="--", lw=1)
            ax.set(xlabel="rank", ylabel="count", title=f"SBC — {name}")
        fig.suptitle("SBC rank histograms — regularized horseshoe")
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
