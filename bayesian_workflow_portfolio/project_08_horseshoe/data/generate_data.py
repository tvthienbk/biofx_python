"""Data-generating process for Project 08 — many predictors, sparse truth.

Scenario: we have ``P`` candidate predictors (e.g. ~20 features: assay readouts,
expression markers, engineered covariates) and want to know which few actually
drive a continuous response ``y``. The truth is SPARSE: only a handful of the P
coefficients are nonzero; the rest are exactly zero. This is the feature-selection
setting where shrinkage priors (the horseshoe) shine and where naive 'significance'
testing invites double-dipping / selection bias.

    y_i = beta_0 + sum_j X_ij * beta_j + Normal(0, sigma)
    only K of the P beta_j are nonzero.

We standardize the columns of X so coefficient magnitudes are comparable. The
KNOWN truth is the full beta vector (mostly zeros); a good sparse model recovers
the nonzero entries and shrinks the rest toward zero.

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

P = 20          # number of candidate predictors
N_OBS = 120     # number of samples
SIGMA_TRUE = 1.0
INTERCEPT_TRUE = 0.5
SEED = 20240601

# Sparse truth: only these indices are nonzero, with these values.
NONZERO = {2: 2.5, 7: -1.8, 13: 1.4}


def generate(
    seed: int = SEED,
    n: int = N_OBS,
    p: int = P,
    sigma: float = SIGMA_TRUE,
    intercept: float = INTERCEPT_TRUE,
    nonzero: dict | None = None,
) -> dict:
    """Simulate a sparse linear model with P predictors, K of them nonzero.

    Returns a dict with design matrix ``X`` (n x p, standardized columns),
    response ``y``, the full ``beta`` truth vector, and a ``truth`` dict whose
    keys name a couple of the nonzero coefficients for recovery checks.
    """
    if nonzero is None:
        nonzero = NONZERO
    rng = np.random.default_rng(seed)
    X = rng.normal(0.0, 1.0, size=(n, p))
    X = (X - X.mean(0)) / X.std(0)            # standardized columns
    beta = np.zeros(p)
    for j, v in nonzero.items():
        beta[j] = v
    y = intercept + X @ beta + rng.normal(0.0, sigma, size=n)
    # name a couple of nonzero coefficients for the recovery test (kept small)
    truth = {f"beta[{j}]": float(v) for j, v in list(nonzero.items())[:2]}
    return {
        "X": X,
        "y": y,
        "beta_true": beta,
        "n": int(n),
        "p": int(p),
        "nonzero_idx": sorted(nonzero),
        "truth": truth,
        "intercept_true": float(intercept),
        "sigma_true": float(sigma),
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        out,
        X=data["X"],
        y=data["y"],
        beta_true=data["beta_true"],
        n=data["n"],
        p=data["p"],
    )
    return data


if __name__ == "__main__":
    d = save()
    print(f"Synthesized n={d['n']} samples, p={d['p']} predictors; "
          f"{len(d['nonzero_idx'])} truly nonzero at indices {d['nonzero_idx']}.")
    print("Nonzero truth:", {f'beta[{j}]': round(float(d['beta_true'][j]), 2)
                             for j in d['nonzero_idx']})
    print("Saved to data/data.npz")
