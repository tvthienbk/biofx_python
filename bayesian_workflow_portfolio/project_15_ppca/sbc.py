"""Simulation-Based Calibration (SBC) for probabilistic PCA.

We calibrate the **identifiable** scalar that survives the rotation symmetry:
the noise ``sigma``. (Raw loadings are non-identified and would not give
meaningful ranks — that is the whole point of this project.) The reconstructed
covariance is also identified but is high-dimensional; sigma is the cleanest
scalar SBC target.

Recipe:
  1. Draw sigma from its HalfNormal(1) prior and W, mu, z from their priors.
  2. Simulate an N x D dataset.
  3. Refit the K=2 model with a small sampler.
  4. Record the rank of the true sigma among posterior sigma draws.

Calibrated => ranks uniform. Kept light: PPCA has N*K latent z's, so each refit
is non-trivial; we use small N and few simulations.
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

N_SIMS = 12
N_OBS = 50
D = 6
K = 2
W_SCALE = 1.0
SIGMA_SD = 1.0
DRAWS = 150
TUNE = 300


def _light_fit(sim, seed):
    """Posterior-only fit (no prior/posterior predictive, no log_likelihood) so
    each SBC iteration is as cheap as possible."""
    with build_model(sim, K=K, w_scale=W_SCALE, prior_sigma_sd=SIGMA_SD):
        idata = pm.sample(draws=DRAWS, tune=TUNE, chains=2, random_seed=seed,
                          target_accept=0.9, progressbar=False)
    return idata


def simulate_once(rng) -> dict:
    W = rng.normal(0.0, W_SCALE, size=(D, K))
    mu = rng.normal(0.0, 1.0, size=D)
    sigma = abs(rng.normal(0.0, SIGMA_SD))
    Z = rng.normal(0.0, 1.0, size=(N_OBS, K))
    X = Z @ W.T + mu + rng.normal(0.0, sigma, size=(N_OBS, D))
    return {"X": X, "D": D, "K": K, "sigma": float(sigma)}


def run_sbc(seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    ranks = np.empty(N_SIMS, dtype=int)
    for i in range(N_SIMS):
        sim = simulate_once(rng)
        idata = _light_fit(sim, seed=3000 + i)
        sig_post = idata.posterior["sigma"].values.ravel()
        ranks[i] = sbc_rank(sim["sigma"], sig_post)
    return ranks


def main() -> None:
    ranks = run_sbc()
    rep = assert_calibrated(ranks, n_bins=8)
    print(f"SBC over {N_SIMS} simulations (N={N_OBS}, D={D}, K={K})")
    print(f"  sigma: chi2={rep['chi2']:.2f}, dof={rep['dof']}, "
          f"p={rep['pvalue']:.3f}, uniform={rep['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.hist(ranks, bins=8, color="#4C72B0", edgecolor="white")
        ax.axhline(N_SIMS / 8, color="k", ls="--", lw=1, label="uniform expectation")
        ax.set(xlabel="rank of true sigma", ylabel="count",
               title="SBC rank histogram — PPCA sigma")
        ax.legend()
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
