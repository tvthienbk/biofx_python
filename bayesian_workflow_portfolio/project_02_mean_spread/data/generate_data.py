"""Data-generating process for Project 02 — estimating a mean & spread.

Scenario: a concentration (e.g. protein concentration in mg/mL) is measured
``N`` times on the same sample. Each replicate measurement is the true
concentration ``mu_true`` plus independent Gaussian noise with standard deviation
``sigma_true`` (instrument/pipetting error). We want the joint posterior for BOTH
the location ``mu`` and the scale ``sigma`` — the new skill in this project.

This is the natural next step after Project 01: now there are TWO parameters, and
one of them is a *scale*. Scale parameters are where "flat/uninformative" priors
become genuinely dangerous (see model.py and BROKEN_BUGS.md).

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

MU_TRUE = 5.0      # true concentration, mg/mL
SIGMA_TRUE = 1.2   # true measurement noise SD, mg/mL
N_OBS = 30         # number of replicate measurements
SEED = 20240602


def generate(seed: int = SEED, n: int = N_OBS,
             mu: float = MU_TRUE, sigma: float = SIGMA_TRUE) -> dict:
    """Simulate ``n`` replicate measurements ~ Normal(mu, sigma).

    Returns a dict with the observed measurements ``y``, the count ``n``, and the
    ``truth`` dict (mu, sigma) for recovery checks.
    """
    rng = np.random.default_rng(seed)
    y = rng.normal(mu, sigma, size=n)
    return {
        "y": y,
        "n": int(n),
        "truth": {"mu": float(mu), "sigma": float(sigma)},
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, y=data["y"], n=data["n"],
             mu=data["truth"]["mu"], sigma=data["truth"]["sigma"])
    return data


if __name__ == "__main__":
    d = save()
    y = d["y"]
    print(f"Synthesized {d['n']} replicate measurements.")
    print(f"  empirical mean = {y.mean():.3f}, empirical sd = {y.std(ddof=1):.3f}")
    print(f"  True mu = {d['truth']['mu']:.3f}, true sigma = {d['truth']['sigma']:.3f}"
          f"  (saved to data/data.npz)")
