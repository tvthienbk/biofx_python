"""Simulation-Based Calibration (SBC) for the local-level model.

We focus the calibration on the **observation noise** ``sigma_obs`` because, of
the two confounded variances, it is the more cleanly checkable scalar given a
short series. (Full joint SBC over both variances is both expensive and partly
confounded by the very identifiability issue the project teaches.)

The standard loop:
  1. Draw sigma_level*, sigma_obs* from their priors (+ a level0).
  2. Simulate a local-level series.
  3. Refit; obtain posterior draws of sigma_obs.
  4. Record the rank of sigma_obs* among them.

Calibrated inference -> uniform ranks. We keep T small and the sampler tiny.

NOTE (compute): each simulation refits a T-dimensional latent random walk; we run
a light ``N_SIMS`` to stay within a couple of minutes.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from shared.bayes_utils import assert_calibrated, sbc_rank  # noqa: E402
from model import build_model  # noqa: E402

import pymc as pm  # noqa: E402

T = 30
N_SIMS = 12
DRAWS = 120
TUNE = 250
SIGMA_LEVEL_SD = 0.5
SIGMA_OBS_SD = 1.0


def _simulate(rng, sigma_level, sigma_obs, level0=5.0):
    level = np.empty(T)
    level[0] = level0
    for i in range(1, T):
        level[i] = level[i - 1] + rng.normal(0.0, sigma_level)
    y = level + rng.normal(0.0, sigma_obs, size=T)
    return y


def run_sbc(seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    ranks = []
    for i in range(N_SIMS):
        sigma_level = abs(rng.normal(0.0, SIGMA_LEVEL_SD))
        sigma_obs = abs(rng.normal(0.0, SIGMA_OBS_SD))
        if sigma_obs < 1e-2:
            continue
        y = _simulate(rng, sigma_level, sigma_obs)
        data = {"y": y, "t": T}
        with build_model(data):
            idata = pm.sample(draws=DRAWS, tune=TUNE, chains=2, cores=1,
                              target_accept=0.95, random_seed=i + 1,
                              progressbar=False)
        post = idata.posterior["sigma_obs"].values.reshape(-1)
        ranks.append(sbc_rank(sigma_obs, post))
    return np.asarray(ranks, dtype=int)


def main() -> None:
    ranks = run_sbc()
    n_bins = 8
    report = assert_calibrated(ranks, n_bins=n_bins)
    print(f"SBC over {len(ranks)} simulations (T={T}) for sigma_obs")
    print(f"  chi-square uniformity test: chi2={report['chi2']:.2f}, "
          f"dof={report['dof']}, p={report['pvalue']:.3f}")
    print(f"  ranks look uniform: {report['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.hist(ranks, bins=n_bins, color="#4C72B0", edgecolor="white")
        ax.axhline(len(ranks) / n_bins, color="k", ls="--", lw=1,
                   label="uniform expectation")
        ax.set(xlabel="rank of prior draw (sigma_obs)", ylabel="count",
               title="SBC rank histogram — local-level obs noise")
        ax.legend()
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
