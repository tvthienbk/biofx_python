"""Simulation-Based Calibration (SBC) for the 2-component mixture.

SBC checks *inference correctness*, not just convergence:

  1. Draw parameters (separation, weight, sigma) from the prior.
  2. Simulate a mixture dataset using those parameters.
  3. Refit the ordered model; obtain posterior draws.
  4. Record the rank of each true value among its posterior draws.

Calibrated inference => ranks uniform on {0, ..., L}. We deliberately calibrate
only the **identifiable** quantities (separation and the high-mean weight); the
raw per-label means are not separately identified without the data and would not
give meaningful ranks.

Kept light: a handful of simulations with a tiny sampler. Mixtures are slow, so
SBC here is a smoke-level calibration check, not a high-resolution one.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from shared.bayes_utils import assert_calibrated, sbc_rank  # noqa: E402
import pymc as pm  # noqa: E402

from model import build_model, add_separation  # noqa: E402

N_SIMS = 18       # light: mixtures are expensive
N_OBS = 100       # small datasets to keep each fit fast
DRAWS = 150
TUNE = 300
W_CONC = 2.0
MU_SD = 3.0
SIGMA_SD = 1.0


def _light_fit(sim, seed):
    """Posterior-only fit (no prior/posterior predictive) to keep SBC cheap."""
    with build_model({"y": sim["y"]}, w_conc=W_CONC, prior_mu_sd=MU_SD,
                     prior_sigma_sd=SIGMA_SD):
        idata = pm.sample(draws=DRAWS, tune=TUNE, chains=2, random_seed=seed,
                          target_accept=0.9, progressbar=False)
    return idata


def simulate_once(rng) -> dict:
    """Draw params from the prior and simulate a labelled mixture dataset."""
    w = rng.dirichlet([W_CONC, W_CONC])
    mu = np.sort(rng.normal(0.0, MU_SD, size=2))   # sorted to match ordered model
    sigma = abs(rng.normal(0.0, SIGMA_SD))
    z = rng.choice(2, size=N_OBS, p=w)
    y = rng.normal(mu[z], sigma)
    return {
        "y": y,
        "sep": float(mu[1] - mu[0]),
        "w_high": float(w[1]),
        "sigma": float(sigma),
    }


def run_sbc(seed: int = 0):
    rng = np.random.default_rng(seed)
    ranks = {"separation": [], "w[1]": [], "sigma": []}
    for i in range(N_SIMS):
        sim = simulate_once(rng)
        idata = _light_fit(sim, seed=1000 + i)
        add_separation(idata)
        sep_post = idata.posterior["separation"].values.ravel()
        whi_post = idata.posterior["w"].isel(w_dim_0=1).values.ravel()
        sig_post = idata.posterior["sigma"].values.ravel()
        ranks["separation"].append(sbc_rank(sim["sep"], sep_post))
        ranks["w[1]"].append(sbc_rank(sim["w_high"], whi_post))
        ranks["sigma"].append(sbc_rank(sim["sigma"], sig_post))
    return {k: np.asarray(v) for k, v in ranks.items()}


def main() -> None:
    ranks = run_sbc()
    print(f"SBC over {N_SIMS} simulations (N={N_OBS}, draws={DRAWS}/chain x2)")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(11, 3.2))
        for ax, (name, r) in zip(axes, ranks.items()):
            rep = assert_calibrated(r, n_bins=8)
            print(f"  {name:>11}: chi2={rep['chi2']:.2f}, p={rep['pvalue']:.3f}, "
                  f"uniform={rep['uniform']}")
            ax.hist(r, bins=8, color="#4C72B0", edgecolor="white")
            ax.axhline(len(r) / 8, color="k", ls="--", lw=1)
            ax.set(title=f"{name} (p={rep['pvalue']:.2f})", xlabel="rank")
        fig.suptitle("SBC rank histograms — 2-component mixture")
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        for name, r in ranks.items():
            rep = assert_calibrated(r, n_bins=8)
            print(f"  {name:>11}: p={rep['pvalue']:.3f}, uniform={rep['uniform']}")
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
