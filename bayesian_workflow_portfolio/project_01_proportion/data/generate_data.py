"""Data-generating process for Project 01 — estimating a proportion.

Scenario: a biochemical binary assay is run ``N`` times; each run independently
"succeeds" (e.g. a substrate is cleaved / a well turns positive) with an unknown
true probability ``theta_true``. The data are the individual 0/1 outcomes.

This is the simplest possible Bayesian problem — a single parameter — so it is
the right place to learn the *whole* workflow end to end.

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

THETA_TRUE = 0.62  # the known success probability we will try to recover
N_TRIALS = 80      # number of independent assay runs
SEED = 20240601


def generate(seed: int = SEED, n: int = N_TRIALS, theta: float = THETA_TRUE) -> dict:
    """Simulate ``n`` Bernoulli assay outcomes with success prob ``theta``.

    Returns a dict with the observed outcomes ``y`` (0/1 array), the number of
    successes ``k``, the count ``n``, and the ``truth`` dict for recovery checks.
    """
    rng = np.random.default_rng(seed)
    y = rng.binomial(1, theta, size=n).astype(int)
    return {
        "y": y,
        "k": int(y.sum()),
        "n": int(n),
        "truth": {"theta": float(theta)},
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, y=data["y"], k=data["k"], n=data["n"], theta=data["truth"]["theta"])
    return data


if __name__ == "__main__":
    d = save()
    print(f"Synthesized {d['n']} assay runs; observed {d['k']} successes "
          f"(empirical rate {d['k']/d['n']:.3f}).")
    print(f"True theta = {d['truth']['theta']:.3f}  (saved to data/data.npz)")
