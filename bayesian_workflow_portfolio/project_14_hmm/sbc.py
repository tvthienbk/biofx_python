"""Simulation-Based Calibration (SBC) for the marginalized 2-state HMM.

Recipe:
  1. Draw params from the prior: p01,p10 ~ Beta(2,8); mu ~ Normal(0,3) (sorted);
     sigma ~ HalfNormal(1).
  2. Simulate an HMM trajectory of length T.
  3. Refit the ordered, marginalized model with a tiny sampler.
  4. Record the rank of each true value among its posterior draws.

Calibrated inference => ranks uniform on {0,...,L}.

This is **light by necessity**: each HMM refit runs the forward algorithm in
pytensor.scan and costs ~15-30 s even at small T, so we use few simulations and
short trajectories. Treat this as a smoke-level calibration check on the
identifiable quantities (separation and sigma), not a high-resolution audit.
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

N_SIMS = 8
T = 100
DRAWS = 120
TUNE = 250
A_SW, B_SW = 2.0, 8.0
MU_SD, SIGMA_SD = 3.0, 1.0


def _light_fit(sim, seed):
    """Posterior-only fit (no prior predictive) to keep each SBC iteration cheap."""
    with build_model({"y": sim["y"]}, a_switch=A_SW, b_switch=B_SW,
                     prior_mu_sd=MU_SD, prior_sigma_sd=SIGMA_SD):
        idata = pm.sample(draws=DRAWS, tune=TUNE, chains=2, random_seed=seed,
                          target_accept=0.9, progressbar=False)
    return idata


def simulate_once(rng) -> dict:
    p01 = rng.beta(A_SW, B_SW)
    p10 = rng.beta(A_SW, B_SW)
    mu = np.sort(rng.normal(0.0, MU_SD, size=2))
    sigma = abs(rng.normal(0.0, SIGMA_SD))
    P = np.array([[1 - p01, p01], [p10, 1 - p10]])
    s = np.zeros(T, dtype=int)
    s[0] = rng.choice(2, p=[0.5, 0.5])
    for t in range(1, T):
        s[t] = rng.choice(2, p=P[s[t - 1]])
    y = rng.normal(mu[s], sigma)
    return {"y": y, "sep": float(mu[1] - mu[0]), "sigma": float(sigma)}


def run_sbc(seed: int = 0):
    rng = np.random.default_rng(seed)
    ranks = {"separation": [], "sigma": []}
    for i in range(N_SIMS):
        sim = simulate_once(rng)
        idata = _light_fit(sim, seed=2000 + i)
        sep_post = idata.posterior["separation"].values.ravel()
        sig_post = idata.posterior["sigma"].values.ravel()
        ranks["separation"].append(sbc_rank(sim["sep"], sep_post))
        ranks["sigma"].append(sbc_rank(sim["sigma"], sig_post))
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
            rep = assert_calibrated(r, n_bins=6)
            print(f"  {name:>11}: chi2={rep['chi2']:.2f}, p={rep['pvalue']:.3f}, "
                  f"uniform={rep['uniform']}")
            ax.hist(r, bins=6, color="#4C72B0", edgecolor="white")
            ax.axhline(len(r) / 6, color="k", ls="--", lw=1)
            ax.set(title=f"{name} (p={rep['pvalue']:.2f})", xlabel="rank")
        fig.suptitle("SBC rank histograms — 2-state HMM")
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        for name, r in ranks.items():
            rep = assert_calibrated(r, n_bins=6)
            print(f"  {name:>11}: p={rep['pvalue']:.3f}, uniform={rep['uniform']}")
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
