"""Simulation-Based Calibration (SBC) for the hierarchical Normal model.

SBC checks *inference correctness*, not merely convergence. For each simulation:

  1. Draw population-level parameters from the prior:
        mu*  ~ Normal(5, mu_prior_sd)
        tau* ~ HalfNormal(tau_prior_sd)
        sigma* ~ HalfNormal(2)
  2. Draw group means theta_j ~ Normal(mu*, tau*) and simulate y_ij.
  3. Refit the *non-centered* model with a tiny sampler.
  4. Record the rank of mu* and tau* among the posterior draws.

If the model + sampler are calibrated, these ranks are uniform. We focus on the
population-level parameters ``mu`` and ``tau`` because those are what a
partial-pooling analysis actually reports, and because ``tau`` (the between-group
SD) is the parameter whose geometry the funnel attacks — it is the one most worth
calibration-checking.

This is kept deliberately light (few simulations, tiny sampler) so it runs in a
couple of minutes. Hierarchical SBC is genuinely expensive; the point here is to
demonstrate the procedure and read the histogram, not to certify to 3 decimals.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from shared.bayes_utils import assert_calibrated, sbc_rank  # noqa: E402
from model import fit  # noqa: E402

MU_PRIOR_SD = 5.0
TAU_PRIOR_SD = 2.0
J = 12
N_PER = 4
N_SIMS = 40   # light: hierarchical refits are expensive
L = 200       # posterior draws kept per simulation


def simulate_one(rng: np.random.Generator) -> dict:
    """Draw parameters from the prior and simulate one hierarchical dataset."""
    mu_star = rng.normal(5.0, MU_PRIOR_SD)
    tau_star = abs(rng.normal(0.0, TAU_PRIOR_SD))      # HalfNormal
    sigma_star = abs(rng.normal(0.0, 2.0))             # HalfNormal
    theta = rng.normal(mu_star, tau_star, size=J)
    group = np.repeat(np.arange(J), N_PER)
    y = rng.normal(theta[group], sigma_star)
    data = {"y": y.astype(float), "group": group.astype(int), "J": J, "n_per": N_PER}
    return data, {"mu": mu_star, "tau": tau_star}


def run_sbc(seed: int = 0) -> dict:
    """Return arrays of SBC ranks for mu and tau over N_SIMS simulations."""
    rng = np.random.default_rng(seed)
    ranks = {"mu": np.empty(N_SIMS, dtype=int), "tau": np.empty(N_SIMS, dtype=int)}
    for i in range(N_SIMS):
        data, truth = simulate_one(rng)
        idata = fit(
            data,
            parameterization="noncentered",
            draws=L,
            tune=400,
            chains=1,
            target_accept=0.95,
            seed=int(rng.integers(1, 2**31 - 1)),
            compute_convergence_checks=False,
        )
        for name in ("mu", "tau"):
            post = idata.posterior[name].values.ravel()
            ranks[name][i] = sbc_rank(truth[name], post)
    return ranks


def main() -> None:
    ranks = run_sbc()
    print(f"SBC over {N_SIMS} simulations (J={J}, n_per={N_PER}, L~{L})")
    reports = {}
    for name in ("mu", "tau"):
        rep = assert_calibrated(ranks[name], n_bins=10)
        reports[name] = rep
        print(f"  {name}: chi2={rep['chi2']:.2f}, dof={rep['dof']}, "
              f"p={rep['pvalue']:.3f}, uniform={rep['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
        for ax, name in zip(axes, ("mu", "tau")):
            ax.hist(ranks[name], bins=10, color="#4C72B0", edgecolor="white")
            ax.axhline(N_SIMS / 10, color="k", ls="--", lw=1, label="uniform")
            ax.set(xlabel=f"rank of {name}*", ylabel="count",
                   title=f"SBC ranks — {name} (p={reports[name]['pvalue']:.2f})")
            ax.legend()
        fig.suptitle("SBC rank histograms — hierarchical Normal (non-centered)")
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
