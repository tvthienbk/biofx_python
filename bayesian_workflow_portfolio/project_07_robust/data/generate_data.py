"""Data-generating process for Project 07 — robust regression with outliers.

Scenario: a calibration experiment relates a known input ``x`` to a measured
response ``y`` that should be linear, ``y = alpha + beta*x + noise``. Most
measurements are clean, but a handful are **gross outliers** — a pipetting
error, a bubble, a mis-read plate. The job is to estimate the calibration line
(alpha, beta) without letting those few outliers drag it.

We generate clean data from a Normal noise model, then deliberately corrupt a
small fraction of points with large shifts. The KNOWN truth is the *clean* line;
a robust (Student-t) fit should recover it, while a Normal fit will be dragged.

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

ALPHA_TRUE = 1.0     # intercept of the calibration line
BETA_TRUE = 2.0      # slope
SIGMA_TRUE = 0.6     # clean measurement noise sd
N_OBS = 60           # number of calibration points
N_OUTLIERS = 6       # how many points are corrupted (~10%)
OUTLIER_SHIFT = 9.0  # magnitude of the corruption (in y units)
# Seed chosen so the *clean* points' least-squares line is very close to the true
# (alpha, beta) — i.e. the unlucky sampling slop is small — so that "recover the
# clean line" is a fair target and the Normal-vs-Student-t contrast is about the
# outliers, not about a noise fluke in the clean data.
SEED = 20240608


def generate(
    seed: int = SEED,
    n: int = N_OBS,
    n_out: int = N_OUTLIERS,
    alpha: float = ALPHA_TRUE,
    beta: float = BETA_TRUE,
    sigma: float = SIGMA_TRUE,
    shift: float = OUTLIER_SHIFT,
) -> dict:
    """Simulate a linear calibration with a few gross outliers.

    Returns a dict with the input ``x`` (standardized), response ``y``, a boolean
    ``is_outlier`` mask, sample size ``n``, and a ``truth`` dict (the CLEAN line).
    """
    rng = np.random.default_rng(seed)
    x = rng.uniform(-2.0, 2.0, size=n)
    x = (x - x.mean()) / x.std()
    y = alpha + beta * x + rng.normal(0.0, sigma, size=n)
    # Corrupt a few points with large, signed shifts. We deliberately place the
    # outliers among LOW-LEVERAGE points (smallest |x|, near the centre) and give
    # them BALANCED signs (half up, half down). This makes the corruption a pure
    # vertical-scatter contaminant that inflates a Normal fit's sigma and tugs its
    # estimates, *without* engineering a slope artefact — so the recoverable truth
    # is genuinely the clean line and the teaching contrast (Normal dragged vs
    # Student-t robust) is honest rather than a knife-edge of leverage.
    central = np.argsort(np.abs(x))[:max(n_out * 3, n_out)]
    idx = rng.choice(central, size=n_out, replace=False)
    signs = np.where(np.arange(n_out) % 2 == 0, 1.0, -1.0)
    y[idx] = y[idx] + signs * shift
    is_outlier = np.zeros(n, dtype=bool)
    is_outlier[idx] = True
    return {
        "x": x,
        "y": y,
        "is_outlier": is_outlier,
        "n": int(n),
        "truth": {"alpha": float(alpha), "beta": float(beta), "sigma": float(sigma)},
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        out,
        x=data["x"],
        y=data["y"],
        is_outlier=data["is_outlier"],
        n=data["n"],
        alpha=data["truth"]["alpha"],
        beta=data["truth"]["beta"],
        sigma=data["truth"]["sigma"],
    )
    return data


if __name__ == "__main__":
    d = save()
    print(f"Synthesized {d['n']} calibration points with {int(d['is_outlier'].sum())} "
          f"gross outliers.")
    print(f"True (clean) alpha={d['truth']['alpha']}, beta={d['truth']['beta']}, "
          f"sigma={d['truth']['sigma']}")
    print("Saved to data/data.npz")
