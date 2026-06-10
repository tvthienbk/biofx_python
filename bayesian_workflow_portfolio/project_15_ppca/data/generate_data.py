"""Data-generating process for Project 15 — probabilistic PCA / factor analysis.

Scenario: a panel of `D` correlated measurements per sample (e.g. intensities at
D spectral channels, or D omics features) is driven by a small number `K` of
underlying latent factors — a low-dimensional structure embedded in a
higher-dimensional readout. We want to recover that latent structure.

Generative model (probabilistic PCA):

    z_n ~ Normal(0, I_K)                      # K latent factor scores per sample
    x_n ~ Normal(W z_n + mu, sigma^2 I_D)     # D observed dims

with a D x K loading matrix W, offset mu, and isotropic noise sigma.

**The key subtlety — non-identifiability.** W and z are only identified up to an
orthogonal rotation/sign: W -> W R, z -> R^T z (with R orthogonal) leaves the
likelihood unchanged. So *raw* loadings are meaningless on their own. The
identifiable quantities are **rotation-invariant**: the noise sigma, and the
reconstructed data covariance C = W Wᵀ + sigma^2 I (equivalently the column space
/ subspace spanned by W).

Known truth and the recoverable, identifiable targets:

  * sigma_true = 0.4
  * C_true = W_true W_trueᵀ + sigma_true^2 I   (the rotation-invariant target)
  * D = 6 observed dims, K = 2 latent factors, N = 150 samples

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

D_DIM = 6
K_LATENT = 2
N_OBS = 150
SIGMA_TRUE = 0.4
SEED = 20240601


def generate(
    seed: int = SEED,
    n: int = N_OBS,
    d: int = D_DIM,
    k: int = K_LATENT,
    sigma: float = SIGMA_TRUE,
) -> dict:
    """Simulate N samples of D-dim data from a K-factor probabilistic-PCA model.

    Returns the observed matrix ``X`` (N x D), and a ``truth`` dict with the
    *identifiable* targets: ``sigma`` and the reconstructed covariance ``C``
    (flattened diagonal + full matrix), which recovery tests should target.
    """
    rng = np.random.default_rng(seed)
    W = rng.normal(0.0, 1.0, size=(d, k))
    mu = rng.normal(0.0, 0.5, size=d)
    Z = rng.normal(0.0, 1.0, size=(n, k))
    X = Z @ W.T + mu + rng.normal(0.0, sigma, size=(n, d))
    C = W @ W.T + sigma ** 2 * np.eye(d)
    return {
        "X": X.astype(float),
        "D": int(d),
        "K": int(k),
        "W_true": W,
        "mu_true": mu,
        "C_true": C,
        "truth": {
            "sigma": float(sigma),
            # a single identifiable scalar: total variance = trace(C)
            "total_var": float(np.trace(C)),
        },
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, X=data["X"], C_true=data["C_true"], W_true=data["W_true"],
             mu_true=data["mu_true"])
    return data


if __name__ == "__main__":
    d = save()
    X = d["X"]
    print(f"Synthesized N={X.shape[0]} samples x D={X.shape[1]} dims, "
          f"K={d['K']} latent factors.")
    print(f"  empirical total variance (trace of sample cov) = "
          f"{np.trace(np.cov(X.T)):.3f}")
    t = d["truth"]
    print(f"True sigma={t['sigma']:.2f}; identifiable total_var=trace(C)="
          f"{t['total_var']:.3f}")
    print("Note: raw loadings W are non-identifiable (rotation/sign); we recover "
          "rotation-invariant quantities (sigma, reconstructed covariance).")
