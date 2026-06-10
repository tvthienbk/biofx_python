"""Data-generating process for Project 18 — state-space / local-level model.

Scenario: a sensor or growth-curve time series with a *latent drifting level*.
The thing we actually care about (the true underlying level, e.g. a slowly
changing concentration, temperature, or population size) is not observed directly;
we see it through noisy measurements.

Two distinct noise sources:
  * PROCESS noise  (sigma_level): how much the latent level wanders step-to-step.
  * OBSERVATION noise (sigma_obs): measurement error on top of the level.

The central pitfall of state-space models is that these two variances are
**confounded**: a wiggly observed series can be explained either as a genuinely
wandering level (large process noise, small obs noise) or as a steady level seen
through noisy measurements (small process noise, large obs noise). Data length and
priors are what separate them.

We generate from a **local-level model** (latent Gaussian random walk + Gaussian
observation noise). Recoverable truths: both variances and the latent trajectory.

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

T = 100
SIGMA_LEVEL_TRUE = 0.30   # process noise: latent random-walk step sd
SIGMA_OBS_TRUE = 0.60     # observation noise sd
LEVEL0_TRUE = 5.0         # starting level
SEED = 20240601


def generate(seed: int = SEED, t: int = T,
             sigma_level: float = SIGMA_LEVEL_TRUE,
             sigma_obs: float = SIGMA_OBS_TRUE,
             level0: float = LEVEL0_TRUE) -> dict:
    """Simulate a local-level state-space series of length ``t``."""
    rng = np.random.default_rng(seed)
    level = np.empty(t)
    level[0] = level0
    for i in range(1, t):
        level[i] = level[i - 1] + rng.normal(0.0, sigma_level)
    y = level + rng.normal(0.0, sigma_obs, size=t)
    return {
        "y": y,
        "level_true": level,
        "t": int(t),
        "truth": {
            "sigma_level": float(sigma_level),
            "sigma_obs": float(sigma_obs),
        },
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, y=data["y"], level_true=data["level_true"], t=data["t"],
             sigma_level=data["truth"]["sigma_level"],
             sigma_obs=data["truth"]["sigma_obs"])
    return data


if __name__ == "__main__":
    d = save()
    print(f"Synthesized a local-level series of length T={d['t']}.")
    print(f"  observed y range = [{d['y'].min():.2f}, {d['y'].max():.2f}]")
    print(f"True sigma_level (process) = {d['truth']['sigma_level']:.3f}")
    print(f"True sigma_obs   (observation) = {d['truth']['sigma_obs']:.3f}")
    print("  (saved to data/data.npz)")
