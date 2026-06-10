"""Simple linear regression for Project 04, decoupled from the notebook.

Likelihood: y_i ~ Normal(alpha + beta * x_std_i, sigma)
Priors:     alpha ~ Normal(0, 5)        (intercept at MEAN dose, standardized)
            beta  ~ Normal(0, 5)         (slope per 1 SD of dose)
            sigma ~ HalfNormal(2)        (proper scale prior, as in Project 02)

The NEW skill is **predictors with priors on slope and intercept**. The KEY
PITFALL is **un-scaled predictors**: when x lives far from zero (doses ~100..600),
the raw intercept is a meaningless extrapolation to x=0, priors are hard to set,
and alpha/beta become strongly correlated (bad sampler geometry). We therefore fit
on the STANDARDIZED predictor x_std = (x - mean) / sd.

By default ``build_model`` uses the standardized predictor (``standardize=True``).
Set ``standardize=False`` to fit on raw x (the broken/demonstration path), where a
too-tight slope prior also bites.

Exposes ``build_model`` and ``fit`` shared by the notebook, tests, SBC, and prior-
sensitivity scripts.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm

ALPHA_SD = 5.0      # weakly-informative on the standardized scale
BETA_SD = 5.0       # weakly-informative slope per 1 SD of x
SIGMA_SCALE = 2.0   # proper HalfNormal scale prior


def build_model(
    data: dict,
    alpha_sd: float = ALPHA_SD,
    beta_sd: float = BETA_SD,
    sigma_scale: float = SIGMA_SCALE,
    standardize: bool = True,
) -> pm.Model:
    """Construct the linear regression model.

    If ``standardize`` is True (correct), the predictor is ``x_std`` (zero mean,
    unit SD). If False, the raw predictor ``x`` is used (the pitfall path).
    """
    y = np.asarray(data["y"])
    x = np.asarray(data["x_std"] if standardize else data["x"])
    with pm.Model() as model:
        alpha = pm.Normal("alpha", mu=0.0, sigma=alpha_sd)
        beta = pm.Normal("beta", mu=0.0, sigma=beta_sd)
        sigma = pm.HalfNormal("sigma", sigma=sigma_scale)
        mu = alpha + beta * x
        pm.Normal("y", mu=mu, sigma=sigma, observed=y)
    return model


def fit(
    data: dict,
    alpha_sd: float = ALPHA_SD,
    beta_sd: float = BETA_SD,
    sigma_scale: float = SIGMA_SCALE,
    standardize: bool = True,
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 4,
    seed: int = 404,
    **kw,
) -> az.InferenceData:
    """Sample the posterior with NUTS and attach prior/posterior predictive."""
    with build_model(data, alpha_sd=alpha_sd, beta_sd=beta_sd,
                     sigma_scale=sigma_scale, standardize=standardize):
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            random_seed=seed,
            progressbar=False,
            idata_kwargs={"log_likelihood": True},
            **kw,
        )
        idata.extend(pm.sample_prior_predictive(draws=500, random_seed=seed))
        idata.extend(pm.sample_posterior_predictive(idata, random_seed=seed,
                                                    progressbar=False))
    return idata


def to_natural(idata: az.InferenceData, data: dict) -> dict:
    """Map standardized coefficients back to the natural (raw-x) scale.

    alpha_nat = alpha_std - beta_std * x_mean / x_sd
    beta_nat  = beta_std / x_sd
    """
    a = idata.posterior["alpha"].values.ravel()
    b = idata.posterior["beta"].values.ravel()
    x_mean, x_sd = data["x_mean"], data["x_sd"]
    beta_nat = b / x_sd
    alpha_nat = a - b * x_mean / x_sd
    return {"alpha": float(alpha_nat.mean()), "beta": float(beta_nat.mean())}


if __name__ == "__main__":
    from data.generate_data import generate

    d = generate()
    idata = fit(d, draws=500, tune=500, chains=2)
    print(az.summary(idata, var_names=["alpha", "beta", "sigma"]))
    print("true (standardized):", d["truth"])
    nat = to_natural(idata, d)
    print(f"recovered natural-scale: alpha={nat['alpha']:.3f}, beta={nat['beta']:.4f}")
    print("true natural-scale:", d["truth_natural"])
