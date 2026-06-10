"""Simulation-Based Calibration (SBC) for the change-point model.

We calibrate the **pre/post Poisson rates** (lam0, lam1), the clearly identifiable
parameters. Recipe:

  1. Draw lam0, lam1 ~ Exponential(1/5) and tau ~ DiscreteUniform(1, T-1).
  2. Simulate a Poisson count series with the shift at tau.
  3. Refit the discrete-tau model with a small sampler.
  4. Record the rank of each true rate among its posterior draws.

Calibrated => ranks uniform. The discrete-tau model is cheap (NUTS on 2 rates +
Metropolis on tau), so we can afford a reasonable number of simulations.
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

N_SIMS = 45
T = 120
LAM_MEAN = 5.0
DRAWS = 300
TUNE = 500


def _light_fit(sim, seed):
    """Posterior-only fit (no predictive / log_likelihood) so each SBC iteration
    is cheap."""
    with build_model({"y": sim["y"], "T": T}, lam_mean=LAM_MEAN):
        idata = pm.sample(draws=DRAWS, tune=TUNE, chains=2, random_seed=seed,
                          progressbar=False)
    return idata


def simulate_once(rng) -> dict:
    lam0 = rng.exponential(LAM_MEAN)
    lam1 = rng.exponential(LAM_MEAN)
    tau = int(rng.integers(1, T))
    idx = np.arange(T)
    rate = np.where(idx < tau, lam0, lam1)
    y = rng.poisson(rate)
    return {"y": y.astype(int), "T": T, "lam0": float(lam0), "lam1": float(lam1)}


def run_sbc(seed: int = 0):
    rng = np.random.default_rng(seed)
    ranks = {"lam0": [], "lam1": []}
    for i in range(N_SIMS):
        sim = simulate_once(rng)
        idata = _light_fit(sim, seed=4000 + i)
        for p in ("lam0", "lam1"):
            post = idata.posterior[p].values.ravel()
            ranks[p].append(sbc_rank(sim[p], post))
    return {k: np.asarray(v) for k, v in ranks.items()}


def main() -> None:
    ranks = run_sbc()
    print(f"SBC over {N_SIMS} simulations (T={T}, draws={DRAWS}/chain x2)")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(8, 3.2))
        for ax, (name, r) in zip(axes, ranks.items()):
            rep = assert_calibrated(r, n_bins=10)
            print(f"  {name:>5}: chi2={rep['chi2']:.2f}, p={rep['pvalue']:.3f}, "
                  f"uniform={rep['uniform']}")
            ax.hist(r, bins=10, color="#4C72B0", edgecolor="white")
            ax.axhline(len(r) / 10, color="k", ls="--", lw=1)
            ax.set(title=f"{name} (p={rep['pvalue']:.2f})", xlabel="rank")
        fig.suptitle("SBC rank histograms — change-point rates")
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        for name, r in ranks.items():
            rep = assert_calibrated(r, n_bins=10)
            print(f"  {name:>5}: p={rep['pvalue']:.3f}, uniform={rep['uniform']}")
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
