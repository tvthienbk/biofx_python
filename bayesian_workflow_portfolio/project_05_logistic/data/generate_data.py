"""Data-generating process for Project 05 — binary outcomes (logistic GLM).

Scenario: a ligand either binds (1) or does not bind (0) to a receptor in each
of ``N`` independent wells. The probability of binding rises smoothly with a
continuous covariate ``x`` (e.g. a standardized concentration / hydrophobicity
score). The true relationship is on the *log-odds* (logit) scale::

    logit(p_i) = alpha_true + beta_true * x_i
    y_i        ~ Bernoulli(p_i)

We center/standardize ``x`` so that ``alpha`` is the log-odds of binding at the
mean covariate value, which makes priors interpretable on the probability scale.

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

ALPHA_TRUE = 0.3   # log-odds of binding at mean x  -> p ≈ 0.57
BETA_TRUE = 1.4    # each +1 SD of x multiplies the odds by exp(1.4) ≈ 4.1
N_OBS = 120        # number of wells
SEED = 20240601


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


def generate(
    seed: int = SEED,
    n: int = N_OBS,
    alpha: float = ALPHA_TRUE,
    beta: float = BETA_TRUE,
) -> dict:
    """Simulate ``n`` Bernoulli binding outcomes driven by a logistic link.

    Returns a dict with the covariate ``x`` (standardized), the 0/1 outcomes
    ``y``, the sample size ``n``, and a ``truth`` dict for recovery checks.
    """
    rng = np.random.default_rng(seed)
    x = rng.normal(0.0, 1.0, size=n)          # already ~standardized
    x = (x - x.mean()) / x.std()              # enforce mean 0, sd 1 exactly
    p = _sigmoid(alpha + beta * x)
    y = rng.binomial(1, p).astype(int)
    return {
        "x": x,
        "y": y,
        "p_true": p,
        "n": int(n),
        "truth": {"alpha": float(alpha), "beta": float(beta)},
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
        alpha=data["truth"]["alpha"],
        beta=data["truth"]["beta"],
    )
    return data


if __name__ == "__main__":
    d = save()
    rate = d["y"].mean()
    print(f"Synthesized {d['n']} binding assays; overall binding rate {rate:.3f}.")
    print(f"True alpha = {d['truth']['alpha']:.3f}, beta = {d['truth']['beta']:.3f}")
    print("Saved to data/data.npz")
