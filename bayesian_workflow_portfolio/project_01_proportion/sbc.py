"""Simulation-Based Calibration (SBC) for the Beta–Binomial model.

SBC checks *inference correctness*, not just convergence. The logic:

  1. Draw theta* from the prior.
  2. Simulate a dataset of size N using theta*.
  3. Fit the model; obtain L posterior draws of theta.
  4. Record the rank of theta* among those L draws.

If the sampler + model are calibrated, these ranks are uniformly distributed
on {0, ..., L}. Systematic deviations reveal bias (skewed ranks), over-confident
posteriors (∪-shaped), or under-confident posteriors (∩-shaped).

This script keeps the sampler tiny so it runs in a couple of minutes. Use the
analytic conjugate posterior to make it essentially instantaneous (no MCMC),
which is ideal for SBC because it isolates *modeling* correctness from sampler
noise. An MCMC variant is included for completeness.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from shared.bayes_utils import assert_calibrated, sbc_rank  # noqa: E402

A, B = 2.0, 2.0
N = 80
N_SIMS = 400
L = 256  # posterior draws per simulation


def run_sbc(seed: int = 0) -> np.ndarray:
    """Return an array of SBC ranks using the analytic conjugate posterior."""
    rng = np.random.default_rng(seed)
    ranks = np.empty(N_SIMS, dtype=int)
    for i in range(N_SIMS):
        theta_star = rng.beta(A, B)                      # 1. prior draw
        k = rng.binomial(N, theta_star)                  # 2. simulate data
        post = rng.beta(A + k, B + N - k, size=L)        # 3. exact posterior draws
        ranks[i] = sbc_rank(theta_star, post)            # 4. rank statistic
    return ranks


def main() -> None:
    ranks = run_sbc()
    report = assert_calibrated(ranks, n_bins=16)
    print(f"SBC over {N_SIMS} simulations (N={N}, L={L})")
    print(f"  chi-square uniformity test: chi2={report['chi2']:.2f}, "
          f"dof={report['dof']}, p={report['pvalue']:.3f}")
    print(f"  ranks look uniform: {report['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.hist(ranks, bins=16, color="#4C72B0", edgecolor="white")
        ax.axhline(N_SIMS / 16, color="k", ls="--", lw=1, label="uniform expectation")
        ax.set(xlabel="rank of prior draw", ylabel="count",
               title="SBC rank histogram — Beta–Binomial")
        ax.legend()
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
