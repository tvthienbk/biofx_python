"""Data-generating process for Project 12 — errors-in-variables regression.

Scenario: we want the relationship y = alpha + beta * x*, but our instrument adds
noise to BOTH variables. We never see the true predictor x*; we see a noisy
``x_obs = x* + Normal(0, tau_x)``, and a noisy ``y = alpha + beta*x* + Normal(0,
sigma_y)``. Regressing y on x_obs (the naive fit) suffers **attenuation bias**: the
estimated slope is pulled toward 0 by the predictor noise. An errors-in-variables
(EIV) model that treats x* as a latent variable recovers the true slope.

Data-generating model::

    x_true_i ~ Normal(mu_x, sd_x)
    x_obs_i  = x_true_i + Normal(0, tau_x)      # instrument noise in the predictor
    y_i      = alpha + beta * x_true_i + Normal(0, sigma_y)

Run as a script to synthesize the data and print the recoverable truth, including
the textbook attenuation factor that predicts how badly the naive slope is biased.
"""
from __future__ import annotations

import pathlib

import numpy as np

ALPHA_TRUE = 1.0     # intercept
BETA_TRUE = 2.0      # slope (the quantity attenuation bias attacks)
MU_X = 0.0           # mean of the true predictor
SD_X = 1.0           # SD of the true predictor across units
TAU_X = 0.6          # instrument noise SD on the predictor (the culprit)
SIGMA_Y = 0.5        # observation noise SD on the response
N = 120              # number of units
SEED = 20240601


def generate(
    seed: int = SEED,
    n: int = N,
    alpha: float = ALPHA_TRUE,
    beta: float = BETA_TRUE,
    mu_x: float = MU_X,
    sd_x: float = SD_X,
    tau_x: float = TAU_X,
    sigma_y: float = SIGMA_Y,
) -> dict:
    """Simulate an errors-in-variables dataset with known truth."""
    rng = np.random.default_rng(seed)
    x_true = rng.normal(mu_x, sd_x, size=n)
    x_obs = x_true + rng.normal(0.0, tau_x, size=n)
    y = alpha + beta * x_true + rng.normal(0.0, sigma_y, size=n)
    # Textbook attenuation factor lambda = var(x*) / (var(x*) + var(noise)).
    attenuation = sd_x**2 / (sd_x**2 + tau_x**2)
    return {
        "x_obs": x_obs.astype(float),
        "y": y.astype(float),
        "x_true": x_true.astype(float),  # latent; for illustration only
        "n": int(n),
        "tau_x": float(tau_x),           # assumed-known measurement-error SD
        "truth": {
            "alpha": float(alpha),
            "beta": float(beta),
            "sigma_y": float(sigma_y),
        },
        "attenuation_factor": float(attenuation),
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        out,
        x_obs=data["x_obs"], y=data["y"], x_true=data["x_true"],
        n=data["n"], tau_x=data["tau_x"],
        alpha=data["truth"]["alpha"], beta=data["truth"]["beta"],
        sigma_y=data["truth"]["sigma_y"],
        attenuation_factor=data["attenuation_factor"],
    )
    return data


if __name__ == "__main__":
    d = save()
    t = d["truth"]
    print(f"Synthesized n={d['n']} units. True alpha={t['alpha']}, beta={t['beta']}, "
          f"sigma_y={t['sigma_y']}; predictor noise tau_x={d['tau_x']}")
    # naive OLS slope of y on x_obs, to show attenuation up front
    xo, y = d["x_obs"], d["y"]
    b_naive = np.cov(xo, y)[0, 1] / np.var(xo)
    print(f"Naive OLS slope (y on x_obs): {b_naive:.3f}  "
          f"(attenuated toward 0; factor ~{d['attenuation_factor']:.2f})")
    print(f"Expected attenuated slope ~ beta*factor = {t['beta']*d['attenuation_factor']:.3f}")
