"""Simulation-Based Calibration (SBC) for the errors-in-variables model.

We target the regression coefficients (alpha, beta) of the EIV model — the
quantities the project is about (and the ones the naive model attenuates).

For each simulation:
  1. Draw alpha* ~ Normal(0, 5), beta* ~ Normal(0, 5), sigma_y* ~ HalfNormal(2).
  2. Draw true predictors x_true ~ Normal(0, 1); observe x_obs = x_true + N(0, tau_x)
     with the known tau_x; draw y = alpha* + beta* x_true + N(0, sigma_y*).
  3. Refit the EIV model (tau_x supplied) with a small sampler.
  4. Record the rank of alpha* and beta*.

Kept light. tau_x is held at the known value throughout (the measurement-error SD
is assumed calibrated); prior_sensitivity.py studies the effect of getting it wrong.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pymc as pm  # noqa: E402
from shared.bayes_utils import assert_calibrated, sbc_rank  # noqa: E402
from model import build_model  # noqa: E402

N = 60
TAU_X = 0.6
N_SIMS = 18
L = 150


def simulate_one(rng: np.random.Generator):
    alpha = rng.normal(0.0, 5.0)
    beta = rng.normal(0.0, 5.0)
    sigma_y = abs(rng.normal(0.0, 2.0)) + 1e-3
    x_true = rng.normal(0.0, 1.0, size=N)
    x_obs = x_true + rng.normal(0.0, TAU_X, size=N)
    y = alpha + beta * x_true + rng.normal(0.0, sigma_y, size=N)
    data = {"x_obs": x_obs.astype(float), "y": y.astype(float), "n": N,
            "tau_x": TAU_X}
    return data, {"alpha": alpha, "beta": beta}


def run_sbc(seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    ranks = {"alpha": np.empty(N_SIMS, dtype=int),
             "beta": np.empty(N_SIMS, dtype=int)}
    for i in range(N_SIMS):
        data, truth = simulate_one(rng)
        with build_model(data, model="eiv", tau_x=TAU_X):
            idata = pm.sample(
                draws=L,
                tune=400,
                chains=1,
                target_accept=0.95,
                random_seed=int(rng.integers(1, 2**31 - 1)),
                progressbar=False,
                compute_convergence_checks=False,
            )
        for n in ("alpha", "beta"):
            ranks[n][i] = sbc_rank(truth[n], idata.posterior[n].values.ravel())
    return ranks


def main() -> None:
    ranks = run_sbc()
    print(f"SBC over {N_SIMS} simulations (N={N}, tau_x={TAU_X}, L~{L})")
    reports = {}
    for n in ("alpha", "beta"):
        rep = assert_calibrated(ranks[n], n_bins=6)
        reports[n] = rep
        print(f"  {n}: chi2={rep['chi2']:.2f}, dof={rep['dof']}, "
              f"p={rep['pvalue']:.3f}, uniform={rep['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
        for ax, n in zip(axes, ("alpha", "beta")):
            ax.hist(ranks[n], bins=6, color="#4C72B0", edgecolor="white")
            ax.axhline(N_SIMS / 6, color="k", ls="--", lw=1, label="uniform")
            ax.set(xlabel=f"rank of {n}*", ylabel="count",
                   title=f"{n} (p={reports[n]['pvalue']:.2f})")
            ax.legend()
        fig.suptitle("SBC rank histograms — errors-in-variables (alpha, beta)")
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
