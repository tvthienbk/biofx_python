"""Data-generating process for Project 06 — overdispersed counts (NB GLM).

Scenario: RNA-seq-like read counts for a gene across ``N`` samples. Expression
depends (on the log scale) on a continuous covariate ``x`` (e.g. a standardized
treatment dose or a latent condition score). Crucially the counts are
**overdispersed**: their variance exceeds their mean, which is the rule rather
than the exception for sequencing data. We generate from a Negative-Binomial:

    log(mu_i) = beta0 + beta1 * x_i
    y_i       ~ NegativeBinomial(mu_i, alpha)

PyMC's NB is parameterized by mean ``mu`` and dispersion ``alpha`` with
Var(y) = mu + mu^2 / alpha. Small ``alpha`` => strong overdispersion; as
alpha -> infinity the NB collapses to Poisson (Var = mu). We pick a modest
``alpha`` so the data are visibly overdispersed and Poisson will fail.

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

BETA0_TRUE = 2.2    # log baseline expression at mean x -> mu ~ exp(2.2) ~ 9
BETA1_TRUE = 0.8    # each +1 SD of x multiplies the mean by exp(0.8) ~ 2.2
ALPHA_TRUE = 2.0    # NB dispersion; small => strongly overdispersed
N_OBS = 150         # number of samples
SEED = 20240601


def generate(
    seed: int = SEED,
    n: int = N_OBS,
    beta0: float = BETA0_TRUE,
    beta1: float = BETA1_TRUE,
    alpha: float = ALPHA_TRUE,
) -> dict:
    """Simulate ``n`` overdispersed counts from a Negative-Binomial GLM.

    Returns a dict with covariate ``x`` (standardized), counts ``y``, sample
    size ``n``, and a ``truth`` dict for recovery checks.
    """
    rng = np.random.default_rng(seed)
    x = rng.normal(0.0, 1.0, size=n)
    x = (x - x.mean()) / x.std()
    mu = np.exp(beta0 + beta1 * x)
    # numpy's negative_binomial uses (n_successes, prob). Convert from (mu, alpha):
    # mean = mu, dispersion alpha => p = alpha / (alpha + mu), r = alpha.
    p = alpha / (alpha + mu)
    y = rng.negative_binomial(alpha, p).astype(int)
    return {
        "x": x,
        "y": y,
        "n": int(n),
        "truth": {"beta0": float(beta0), "beta1": float(beta1), "alpha": float(alpha)},
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        out,
        x=data["x"],
        y=data["y"],
        n=data["n"],
        beta0=data["truth"]["beta0"],
        beta1=data["truth"]["beta1"],
        alpha=data["truth"]["alpha"],
    )
    return data


if __name__ == "__main__":
    d = save()
    y = d["y"]
    print(f"Synthesized {d['n']} counts; mean={y.mean():.2f}, var={y.var():.2f} "
          f"(var/mean={y.var()/y.mean():.2f}; >>1 => overdispersed).")
    print(f"True beta0={d['truth']['beta0']}, beta1={d['truth']['beta1']}, "
          f"alpha={d['truth']['alpha']}")
    print("Saved to data/data.npz")
