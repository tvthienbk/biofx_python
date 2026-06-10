"""Simulation-Based Calibration (SBC) for the Normal location-scale model.

SBC checks *inference correctness* over BOTH parameters (mu, sigma), not just
convergence. The logic, per simulation:

  1. Draw (mu*, sigma*) from the priors.
  2. Simulate a dataset y ~ Normal(mu*, sigma*) of size N.
  3. Fit the model; obtain L posterior draws of mu and sigma.
  4. Record the rank of each true value among those L draws.

If the sampler + model are calibrated, the ranks for mu and for sigma are each
uniformly distributed. Deviations reveal bias (skew), over-confidence (U-shape),
or under-confidence (n-shape).

We keep the sampler tiny (few draws, 2 chains, small N) and use a modest number
of simulations so the whole script runs quickly. To avoid pathological prior
draws of sigma blowing up runtime, we draw sigma from the proper HalfNormal used
by the model.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from shared.bayes_utils import assert_calibrated, sbc_rank  # noqa: E402
from model import PRIOR_MEAN, PRIOR_SD, SIGMA_SCALE, fit  # noqa: E402

N = 30          # data size per simulation
N_SIMS = 35     # number of SBC simulations (kept light)
DRAWS = 120     # posterior draws per sim
TUNE = 120
CHAINS = 2
L = DRAWS * CHAINS


def run_sbc(seed: int = 0):
    """Return (ranks_mu, ranks_sigma) arrays over N_SIMS simulations."""
    rng = np.random.default_rng(seed)
    ranks_mu = np.empty(N_SIMS, dtype=int)
    ranks_sigma = np.empty(N_SIMS, dtype=int)
    for i in range(N_SIMS):
        mu_star = rng.normal(PRIOR_MEAN, PRIOR_SD)            # 1. prior draw mu
        sigma_star = abs(rng.normal(0.0, SIGMA_SCALE))        # 1. prior draw sigma (HalfNormal)
        if sigma_star < 1e-3:
            sigma_star = 1e-3
        y = rng.normal(mu_star, sigma_star, size=N)           # 2. simulate data
        idata = fit({"y": y}, draws=DRAWS, tune=TUNE, chains=CHAINS,
                    seed=int(rng.integers(1, 1_000_000)),
                    compute_convergence_checks=False)          # 3. refit
        post_mu = idata.posterior["mu"].values.ravel()
        post_sigma = idata.posterior["sigma"].values.ravel()
        ranks_mu[i] = sbc_rank(mu_star, post_mu)               # 4. rank statistics
        ranks_sigma[i] = sbc_rank(sigma_star, post_sigma)
    return ranks_mu, ranks_sigma


def main() -> None:
    ranks_mu, ranks_sigma = run_sbc()
    n_bins = 5
    rep_mu = assert_calibrated(ranks_mu, n_bins=n_bins)
    rep_sigma = assert_calibrated(ranks_sigma, n_bins=n_bins)
    print(f"SBC over {N_SIMS} simulations (N={N}, L={L})")
    print(f"  mu   : chi2={rep_mu['chi2']:.2f}, dof={rep_mu['dof']}, "
          f"p={rep_mu['pvalue']:.3f}, uniform={rep_mu['uniform']}")
    print(f"  sigma: chi2={rep_sigma['chi2']:.2f}, dof={rep_sigma['dof']}, "
          f"p={rep_sigma['pvalue']:.3f}, uniform={rep_sigma['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
        for ax, ranks, name in ((axes[0], ranks_mu, "mu"),
                                 (axes[1], ranks_sigma, "sigma")):
            ax.hist(ranks, bins=n_bins, color="#4C72B0", edgecolor="white")
            ax.axhline(N_SIMS / n_bins, color="k", ls="--", lw=1,
                       label="uniform expectation")
            ax.set(xlabel="rank of prior draw", ylabel="count",
                   title=f"SBC ranks — {name}")
            ax.legend()
        fig.suptitle("SBC rank histograms — Normal(mu, sigma)")
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
