"""Simulation-Based Calibration (SBC) for the hierarchical capstone model.

We calibrate on the between-compound sd ``tau`` — the parameter most central to
the partial-pooling behaviour (and the one the prior sensitivity probes). The loop:

  1. Draw mu*, tau*, sigma* from their priors; draw theta_j* = mu* + tau* z_j*.
  2. Simulate a compound screen with the project's replication structure.
  3. Refit the hierarchical model; obtain posterior draws of tau.
  4. Record the rank of tau* among them.

Calibrated inference -> uniform ranks.

NOTE (compute): each refit is a hierarchical NUTS run; we keep N_SIMS light and J
small. The non-centred parameterisation keeps the funnel away even at small tau*.
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

J = 8
N_SIMS = 20
DRAWS = 150
TUNE = 300
MU_SD = 2.0
TAU_SD = 1.0
SIGMA_SD = 1.0
N_REPS = np.array([12, 10, 8, 6, 4, 3, 2, 2])


def _simulate(rng, mu, tau, sigma):
    theta = mu + tau * rng.standard_normal(J)
    comp_idx = np.repeat(np.arange(J), N_REPS)
    y = np.empty(comp_idx.size)
    pos = 0
    for cj in range(J):
        nj = int(N_REPS[cj])
        y[pos:pos + nj] = theta[cj] + sigma * rng.standard_normal(nj)
        pos += nj
    return {"comp_idx": comp_idx.astype(int), "y": y, "j": J}


def run_sbc(seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    ranks = []
    for i in range(N_SIMS):
        mu = rng.normal(0.0, MU_SD)
        tau = abs(rng.normal(0.0, TAU_SD))
        sigma = abs(rng.normal(0.0, SIGMA_SD))
        if sigma < 1e-2:
            sigma = 0.1
        data = _simulate(rng, mu, tau, sigma)
        with build_model(data):
            idata = pm.sample(draws=DRAWS, tune=TUNE, chains=2, cores=1,
                              target_accept=0.95, random_seed=i + 1,
                              progressbar=False)
        post = idata.posterior["tau"].values.reshape(-1)
        ranks.append(sbc_rank(tau, post))
    return np.asarray(ranks, dtype=int)


def main() -> None:
    ranks = run_sbc()
    n_bins = 8
    report = assert_calibrated(ranks, n_bins=n_bins)
    print(f"SBC over {len(ranks)} simulations for tau (hierarchical model)")
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
        ax.set(xlabel="rank of prior draw (tau)", ylabel="count",
               title="SBC rank histogram — between-compound sd tau")
        ax.legend()
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
