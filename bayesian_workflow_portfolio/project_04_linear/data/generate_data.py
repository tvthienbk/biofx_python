"""Data-generating process for Project 04 — simple linear regression.

Scenario: a dose-response experiment. A single predictor ``x`` (the dose, on its
natural units, e.g. concentration in micromolar) drives a continuous response ``y``
(e.g. a readout intensity) through a linear relationship with Gaussian noise:

    y_i = alpha + beta * x_i + noise,   noise ~ Normal(0, sigma).

The KEY PITFALL of this project is **un-scaled predictors**. The doses here live on
a natural scale far from zero (e.g. 100..600), which (a) makes the intercept
``alpha`` an extrapolation to x=0 that no longer means anything useful, (b) makes
priors on ``alpha`` and ``beta`` hard to set, and (c) hurts the sampler's geometry
(alpha and beta become strongly correlated). The model fixes this by
**standardizing** x. The broken notebook uses raw x with a too-tight slope prior.

We store BOTH the truth on the natural scale (for interpretation) and provide the
standardized predictor so the model can recover standardized coefficients and map
back. Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

# Truth on the NATURAL (raw-x) scale.
ALPHA_TRUE = 2.0     # response at x = 0 (an extrapolation; doses start near 100)
BETA_TRUE = 0.015    # response increase per unit dose
SIGMA_TRUE = 0.8     # noise SD
N_OBS = 40
DOSE_LOW = 100.0     # doses live far from zero -> the standardization lesson
DOSE_HIGH = 600.0
SEED = 20240604


def generate(seed: int = SEED, n: int = N_OBS,
             alpha: float = ALPHA_TRUE, beta: float = BETA_TRUE,
             sigma: float = SIGMA_TRUE) -> dict:
    """Simulate a linear dose-response with a predictor far from zero.

    Returns x (raw dose), x_std (standardized), y, the standardization constants,
    n, and the ``truth`` dict. Truth is reported for the STANDARDIZED model
    coefficients (alpha_std, beta_std, sigma) because that is what the model fits;
    the natural-scale truth is recoverable from the standardization constants.
    """
    rng = np.random.default_rng(seed)
    x = rng.uniform(DOSE_LOW, DOSE_HIGH, size=n)
    y = alpha + beta * x + rng.normal(0.0, sigma, size=n)

    x_mean = float(x.mean())
    x_sd = float(x.std(ddof=0))
    x_std = (x - x_mean) / x_sd

    # Equivalent coefficients on the standardized scale:
    #   y = alpha + beta*x = alpha + beta*(x_mean + x_sd*x_std)
    #     = (alpha + beta*x_mean) + (beta*x_sd)*x_std
    alpha_std_true = alpha + beta * x_mean
    beta_std_true = beta * x_sd

    return {
        "x": x,
        "x_std": x_std,
        "y": y,
        "x_mean": x_mean,
        "x_sd": x_sd,
        "n": int(n),
        "truth": {
            "alpha": float(alpha_std_true),   # intercept on STANDARDIZED scale
            "beta": float(beta_std_true),     # slope on STANDARDIZED scale
            "sigma": float(sigma),
        },
        "truth_natural": {
            "alpha": float(alpha),
            "beta": float(beta),
            "sigma": float(sigma),
        },
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, x=data["x"], x_std=data["x_std"], y=data["y"],
             x_mean=data["x_mean"], x_sd=data["x_sd"], n=data["n"],
             alpha_std=data["truth"]["alpha"], beta_std=data["truth"]["beta"],
             sigma=data["truth"]["sigma"])
    return data


if __name__ == "__main__":
    d = save()
    print(f"Synthesized {d['n']} dose-response points; doses in "
          f"[{d['x'].min():.0f}, {d['x'].max():.0f}] (far from zero).")
    print(f"  standardization: x_mean={d['x_mean']:.2f}, x_sd={d['x_sd']:.2f}")
    print("  Truth on the STANDARDIZED scale (what the model fits):")
    print(f"    alpha_std={d['truth']['alpha']:.3f}, beta_std={d['truth']['beta']:.3f}, "
          f"sigma={d['truth']['sigma']:.3f}")
    print("  Truth on the NATURAL scale (for interpretation):")
    print(f"    alpha={d['truth_natural']['alpha']:.3f}, "
          f"beta={d['truth_natural']['beta']:.4f}, sigma={d['truth_natural']['sigma']:.3f}")
    print("  (saved to data/data.npz)")
