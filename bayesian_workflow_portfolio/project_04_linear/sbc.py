"""Simulation-Based Calibration (SBC) for the linear regression model.

SBC checks inference correctness over (alpha, beta, sigma) on the STANDARDIZED
predictor. Per simulation:

  1. Draw alpha*, beta* ~ Normal(0, 5); sigma* ~ HalfNormal(2) from the priors.
  2. Simulate y ~ Normal(alpha* + beta* * x_std, sigma*) for a fixed x_std design.
  3. Fit the model; obtain L posterior draws of each parameter.
  4. Record the rank of each true value among its posterior draws.

If the model + sampler are calibrated, the ranks for each parameter are uniform.
We keep the sampler tiny and the simulation count modest so the sweep finishes
fast (SBC's cost is dominated by per-fit model compilation).
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from shared.bayes_utils import assert_calibrated, sbc_rank  # noqa: E402
from model import ALPHA_SD, BETA_SD, SIGMA_SCALE, fit  # noqa: E402

N = 40
N_SIMS = 30
DRAWS = 120
TUNE = 120
CHAINS = 2
L = DRAWS * CHAINS


def run_sbc(seed: int = 0):
    """Return dict of rank arrays for alpha, beta, sigma over N_SIMS sims."""
    rng = np.random.default_rng(seed)
    # Fixed standardized design (zero mean, ~unit sd) reused across simulations.
    x_std = rng.normal(0.0, 1.0, size=N)
    x_std = (x_std - x_std.mean()) / x_std.std(ddof=0)
    ranks = {"alpha": np.empty(N_SIMS, int), "beta": np.empty(N_SIMS, int),
             "sigma": np.empty(N_SIMS, int)}
    for i in range(N_SIMS):
        alpha_star = rng.normal(0.0, ALPHA_SD)
        beta_star = rng.normal(0.0, BETA_SD)
        sigma_star = abs(rng.normal(0.0, SIGMA_SCALE))
        if sigma_star < 1e-3:
            sigma_star = 1e-3
        y = rng.normal(alpha_star + beta_star * x_std, sigma_star)
        data = {"x_std": x_std, "x": x_std, "y": y}
        idata = fit(data, draws=DRAWS, tune=TUNE, chains=CHAINS,
                    seed=int(rng.integers(1, 1_000_000)),
                    compute_convergence_checks=False)
        for name, truth in (("alpha", alpha_star), ("beta", beta_star),
                            ("sigma", sigma_star)):
            post = idata.posterior[name].values.ravel()
            ranks[name][i] = sbc_rank(truth, post)
    return ranks


def main() -> None:
    ranks = run_sbc()
    n_bins = 5
    print(f"SBC over {N_SIMS} simulations (N={N}, L={L})")
    reports = {}
    for name in ("alpha", "beta", "sigma"):
        rep = assert_calibrated(ranks[name], n_bins=n_bins)
        reports[name] = rep
        print(f"  {name:>5}: chi2={rep['chi2']:.2f}, dof={rep['dof']}, "
              f"p={rep['pvalue']:.3f}, uniform={rep['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
        for ax, name in zip(axes, ("alpha", "beta", "sigma")):
            ax.hist(ranks[name], bins=n_bins, color="#4C72B0", edgecolor="white")
            ax.axhline(N_SIMS / n_bins, color="k", ls="--", lw=1,
                       label="uniform expectation")
            ax.set(xlabel="rank of prior draw", ylabel="count",
                   title=f"SBC ranks — {name}")
            ax.legend()
        fig.suptitle("SBC rank histograms — linear regression")
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
