"""Data-generating process for Project 17 — nonparametric curve (Gaussian process).

Scenario: a thermal-melt / dose-response experiment. We measure a smooth
response ``y`` at ``N`` input values ``x`` (e.g. temperature or log-dose). The
*true* underlying response is a smooth nonlinear function ``f_true(x)`` that we do
NOT want to commit to a parametric form (sigmoid, polynomial, ...). Instead we
let a Gaussian process learn the curve nonparametrically.

The known, recoverable quantities are:
  * the latent function values ``f_true(x)`` at the training inputs (the GP mean
    should track these), and
  * the observation noise scale ``sigma`` (a single identifiable scalar).

We deliberately keep ``N`` small (~40) so sampling is light, and we choose a
true length-scale that is well inside the input range so the curve is genuinely
"wiggly enough to be interesting, smooth enough to be learnable".

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

N_POINTS = 40
SIGMA_TRUE = 0.18      # observation noise scale (recoverable scalar)
X_LOW, X_HIGH = 0.0, 10.0
SEED = 20240601


def f_true(x: np.ndarray) -> np.ndarray:
    """The smooth latent response curve we pretend not to know parametrically.

    A gentle sigmoidal rise with a secondary bump — the kind of shape a melt or
    dose-response curve can take. Smooth, but not a single clean logistic.
    """
    x = np.asarray(x, dtype=float)
    rise = 1.0 / (1.0 + np.exp(-(x - 4.0)))           # main sigmoidal transition
    bump = 0.35 * np.exp(-0.5 * ((x - 7.0) / 0.9) ** 2)  # secondary feature
    return 2.0 * rise + bump


def generate(seed: int = SEED, n: int = N_POINTS, sigma: float = SIGMA_TRUE) -> dict:
    """Simulate ``n`` noisy observations of ``f_true`` on a grid of inputs."""
    rng = np.random.default_rng(seed)
    x = np.linspace(X_LOW, X_HIGH, n)
    f = f_true(x)
    y = f + rng.normal(0.0, sigma, size=n)
    return {
        "x": x,
        "y": y,
        "f_true": f,
        "n": int(n),
        "truth": {"sigma": float(sigma)},
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, x=data["x"], y=data["y"], f_true=data["f_true"],
             n=data["n"], sigma=data["truth"]["sigma"])
    return data


if __name__ == "__main__":
    d = save()
    print(f"Synthesized {d['n']} noisy observations of a smooth latent curve.")
    print(f"  x range = [{d['x'].min():.1f}, {d['x'].max():.1f}]")
    print(f"  y range = [{d['y'].min():.2f}, {d['y'].max():.2f}]")
    print(f"True sigma = {d['truth']['sigma']:.3f}  (saved to data/data.npz)")
