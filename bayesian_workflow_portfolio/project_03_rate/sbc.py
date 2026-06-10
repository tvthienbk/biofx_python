"""Simulation-Based Calibration (SBC) for the Poisson rate (offset) model.

SBC checks inference correctness for ``log_rate``. Per simulation:

  1. Draw log_rate* from the prior Normal(0, 2).
  2. Simulate counts y ~ Poisson(exposure * exp(log_rate*)) with VARYING exposures.
  3. Fit the offset model; obtain L posterior draws of log_rate.
  4. Record the rank of log_rate* among those draws.

If the model + sampler are calibrated the ranks are uniform. We keep the sampler
tiny and use a modest number of simulations so the script runs quickly.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from shared.bayes_utils import assert_calibrated, sbc_rank  # noqa: E402
from model import PRIOR_MEAN, PRIOR_SD, fit  # noqa: E402

N = 50          # samples per simulation
N_SIMS = 40     # SBC simulations (kept light so the sweep finishes fast)
DRAWS = 150
TUNE = 150
CHAINS = 2
L = DRAWS * CHAINS
EXPOSURE_LOW = 5.0
EXPOSURE_HIGH = 40.0


def run_sbc(seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    ranks = np.empty(N_SIMS, dtype=int)
    for i in range(N_SIMS):
        log_rate_star = rng.normal(PRIOR_MEAN, PRIOR_SD)               # 1. prior draw
        exposure = rng.uniform(EXPOSURE_LOW, EXPOSURE_HIGH, size=N)    # varying exposure
        lam = np.exp(log_rate_star)
        y = rng.poisson(exposure * lam).astype(int)                   # 2. simulate
        idata = fit({"y": y, "exposure": exposure}, draws=DRAWS, tune=TUNE,
                    chains=CHAINS, seed=int(rng.integers(1, 1_000_000)),
                    compute_convergence_checks=False)                  # 3. refit
        post = idata.posterior["log_rate"].values.ravel()
        ranks[i] = sbc_rank(log_rate_star, post)                       # 4. rank
    return ranks


def main() -> None:
    ranks = run_sbc()
    n_bins = 5
    report = assert_calibrated(ranks, n_bins=n_bins)
    print(f"SBC over {N_SIMS} simulations (N={N}, L={L})")
    print(f"  log_rate: chi2={report['chi2']:.2f}, dof={report['dof']}, "
          f"p={report['pvalue']:.3f}, uniform={report['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.hist(ranks, bins=n_bins, color="#4C72B0", edgecolor="white")
        ax.axhline(N_SIMS / n_bins, color="k", ls="--", lw=1,
                   label="uniform expectation")
        ax.set(xlabel="rank of prior draw", ylabel="count",
               title="SBC rank histogram — Poisson rate (log_rate)")
        ax.legend()
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
