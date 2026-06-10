"""Simulation-Based Calibration (SBC) for the hierarchical logistic model.

For each simulation:
  1. Draw mu* ~ Normal(0, 1.5), tau* ~ HalfNormal(1), beta* ~ Normal(0, 1.5).
  2. Draw family intercepts alpha_g ~ Normal(mu*, tau*), simulate Bernoulli y.
  3. Refit the non-centered model with a tiny sampler.
  4. Record the rank of mu*, tau*, beta* among the posterior draws.

We focus on the population-level parameters mu, tau, beta — what a hierarchical
GLM actually reports. Kept light (few simulations, tiny sampler); hierarchical SBC
is expensive, so read the histograms as "no detectable miscalibration".
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from shared.bayes_utils import assert_calibrated, sbc_rank  # noqa: E402
from model import fit  # noqa: E402

MU_PRIOR_SD = 1.5
TAU_PRIOR_SD = 1.0
BETA_PRIOR_SD = 1.5
G = 10
N_PER = 12
N_SIMS = 40
L = 200


def simulate_one(rng: np.random.Generator):
    mu_star = rng.normal(0.0, MU_PRIOR_SD)
    tau_star = abs(rng.normal(0.0, TAU_PRIOR_SD))
    beta_star = rng.normal(0.0, BETA_PRIOR_SD)
    alpha = rng.normal(mu_star, tau_star, size=G)
    group = np.repeat(np.arange(G), N_PER)
    x = rng.normal(0.0, 1.0, size=G * N_PER)
    eta = alpha[group] + beta_star * x
    p = 1.0 / (1.0 + np.exp(-eta))
    y = rng.binomial(1, p)
    data = {"y": y.astype(int), "x": x.astype(float), "group": group.astype(int),
            "G": G, "n_per": N_PER}
    return data, {"mu": mu_star, "tau": tau_star, "beta": beta_star}


def run_sbc(seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    names = ("mu", "tau", "beta")
    ranks = {n: np.empty(N_SIMS, dtype=int) for n in names}
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
        for n in names:
            post = idata.posterior[n].values.ravel()
            ranks[n][i] = sbc_rank(truth[n], post)
    return ranks


def main() -> None:
    ranks = run_sbc()
    print(f"SBC over {N_SIMS} simulations (G={G}, n_per={N_PER}, L~{L})")
    reports = {}
    for n in ("mu", "tau", "beta"):
        rep = assert_calibrated(ranks[n], n_bins=10)
        reports[n] = rep
        print(f"  {n}: chi2={rep['chi2']:.2f}, dof={rep['dof']}, "
              f"p={rep['pvalue']:.3f}, uniform={rep['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(13, 3.5))
        for ax, n in zip(axes, ("mu", "tau", "beta")):
            ax.hist(ranks[n], bins=10, color="#4C72B0", edgecolor="white")
            ax.axhline(N_SIMS / 10, color="k", ls="--", lw=1, label="uniform")
            ax.set(xlabel=f"rank of {n}*", ylabel="count",
                   title=f"{n} (p={reports[n]['pvalue']:.2f})")
            ax.legend()
        fig.suptitle("SBC rank histograms — hierarchical logistic (non-centered)")
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
