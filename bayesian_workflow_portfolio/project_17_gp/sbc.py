"""Simulation-Based Calibration (SBC) for the GP noise scale.

We focus SBC on the most interpretable, fully identifiable scalar: the observation
noise ``sigma``. The standard SBC loop:

  1. Draw sigma* (and the other hyperparameters) from their priors.
  2. Simulate a small GP dataset using those hyperparameters.
  3. Obtain posterior draws of sigma.
  4. Record the rank of sigma* among those draws.

Calibrated inference -> uniform ranks.

KEY IDEA (compute): a GP-with-Gaussian-noise has a CLOSED-FORM marginal
likelihood, so we obtain the hyperposterior by self-normalised IMPORTANCE
SAMPLING in pure numpy (draw prior particles, weight by the marginal likelihood,
resample) instead of running NUTS per dataset. This is exact up to Monte-Carlo
error, runs in seconds, and lets us afford N_SIMS=200 -- a genuinely informative
calibration. (Per-dataset NUTS would be ~30 s/refit without a linked BLAS.) This
mirrors the project's main-model philosophy: use the closed form when you have it.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from shared.bayes_utils import assert_calibrated, sbc_rank  # noqa: E402

N = 12          # tiny dataset per simulation
N_SIMS = 200    # many sims are affordable because the GP likelihood is analytic
N_PRIOR = 4000  # prior particles for importance-resampling the hyperposterior
L = 256         # posterior draws of sigma per simulation
ELL_A, ELL_B = 6.0, 12.0
ETA_SD = 2.0
SIGMA_SD = 0.5
X = np.linspace(0.0, 10.0, N)
_D2 = (X[:, None] - X[None, :]) ** 2  # squared-distance matrix, reused everywhere


def _draw_prior(rng, size):
    """Vectorised prior draws of (ell, eta, sigma)."""
    ell = 1.0 / rng.gamma(ELL_A, 1.0 / ELL_B, size=size)   # InverseGamma(a,b)
    eta = np.abs(rng.normal(0.0, ETA_SD, size=size))       # HalfNormal
    sigma = np.abs(rng.normal(0.0, SIGMA_SD, size=size))   # HalfNormal
    return ell, eta, sigma


def _simulate(rng, ell, eta, sigma):
    """Draw a function from the GP prior on X, then add noise."""
    K = eta**2 * np.exp(-0.5 * _D2 / ell**2) + 1e-8 * np.eye(N)
    f = rng.multivariate_normal(np.zeros(N), K)
    return f + rng.normal(0.0, sigma, size=N)


def _loglik(y, ell, eta, sigma):
    """GP marginal log-likelihood: N(y; 0, eta^2 ExpQuad(ell) + sigma^2 I)."""
    K = eta**2 * np.exp(-0.5 * _D2 / ell**2) + (sigma**2 + 1e-8) * np.eye(N)
    sign, logdet = np.linalg.slogdet(K)
    alpha = np.linalg.solve(K, y)
    return -0.5 * (y @ alpha + logdet + N * np.log(2 * np.pi))


def run_sbc(seed: int = 0) -> np.ndarray:
    """SBC for sigma using a numpy importance-resampled hyperposterior.

    Because the GP-with-Gaussian-noise marginal likelihood is available in closed
    form, we can perform SBC WITHOUT running MCMC: for each simulated dataset we
    draw many hyperparameter particles from the prior, weight them by the marginal
    likelihood, and resample to obtain (ell, eta, sigma) posterior draws. We then
    rank the true sigma* among the resampled sigma draws. This is exact up to Monte
    Carlo error and runs in seconds for hundreds of simulations.
    """
    rng = np.random.default_rng(seed)
    ranks = []
    for i in range(N_SIMS):
        ell0, eta0, sigma0 = _draw_prior(rng, 1)
        ell0, eta0, sigma0 = float(ell0[0]), float(eta0[0]), float(sigma0[0])
        if sigma0 < 1e-3 or eta0 < 1e-3:
            continue
        y = _simulate(rng, ell0, eta0, sigma0)
        # importance sampling: prior particles weighted by the marginal likelihood
        ellp, etap, sigp = _draw_prior(rng, N_PRIOR)
        logw = np.array([_loglik(y, ellp[k], etap[k], sigp[k]) for k in range(N_PRIOR)])
        logw -= logw.max()
        w = np.exp(logw)
        w /= w.sum()
        idx = rng.choice(N_PRIOR, size=L, p=w)   # resample -> posterior draws
        post_sigma = sigp[idx]
        ranks.append(sbc_rank(sigma0, post_sigma))
    return np.asarray(ranks, dtype=int)


def main() -> None:
    ranks = run_sbc()
    n_bins = 16  # many sims -> a finer histogram is meaningful
    report = assert_calibrated(ranks, n_bins=n_bins)
    print(f"SBC over {len(ranks)} GP simulations (N={N}, analytic) for sigma")
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
        ax.set(xlabel="rank of prior draw (sigma)", ylabel="count",
               title="SBC rank histogram — GP noise scale")
        ax.legend()
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
