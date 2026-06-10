"""Poisson rate model with an exposure offset for Project 03.

Likelihood: y_i ~ Poisson(exposure_i * lambda),  lambda = exp(log_rate)
            equivalently  y_i ~ Poisson(exp(log(exposure_i) + log_rate))
Prior:      log_rate ~ Normal(prior_mean, prior_sd)   (prior on the LOG rate)

The NEW skill is priors for a positive rate via a **log link**: we place a Normal
prior on ``log_rate`` so that ``lambda = exp(log_rate)`` is automatically positive
and the prior is symmetric on the log scale (multiplicative on the rate scale).

The KEY PITFALL is the **exposure offset**. Because exposures vary across samples,
the correct model multiplies the rate by each sample's exposure (equivalently adds
``log(exposure)`` as an offset inside the exp). Omitting the offset biases the rate.
``build_model`` takes a ``use_offset`` flag so the broken notebook / demos can show
the bias explicitly; the default (and only correct) setting is ``use_offset=True``.

Exposes ``build_model`` and ``fit`` shared by the notebook, tests, SBC, and the
prior-sensitivity script.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm

PRIOR_MEAN = 0.0    # prior on log_rate centred at 0 -> lambda ~ 1 event/unit a priori
PRIOR_SD = 2.0      # broad on the log scale: covers ~exp(-4)..exp(4) = 0.018..55


def build_model(
    data: dict,
    prior_mean: float = PRIOR_MEAN,
    prior_sd: float = PRIOR_SD,
    use_offset: bool = True,
) -> pm.Model:
    """Construct the Poisson rate model.

    If ``use_offset`` is True (correct), the expected count is
    ``exposure_i * exp(log_rate)``. If False (the seeded bug), the exposure is
    ignored and the expected count is just ``exp(log_rate)`` for every sample.
    """
    y = np.asarray(data["y"])
    exposure = np.asarray(data["exposure"])
    with pm.Model() as model:
        log_rate = pm.Normal("log_rate", mu=prior_mean, sigma=prior_sd)
        rate = pm.math.exp(log_rate)
        if use_offset:
            mu = exposure * rate           # correct: scale by each exposure
        else:
            mu = rate                      # WRONG: ignores varying exposure
        pm.Poisson("y", mu=mu, observed=y)
    return model


def fit(
    data: dict,
    prior_mean: float = PRIOR_MEAN,
    prior_sd: float = PRIOR_SD,
    use_offset: bool = True,
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 4,
    seed: int = 303,
    **kw,
) -> az.InferenceData:
    """Sample the posterior with NUTS and attach prior/posterior predictive."""
    with build_model(data, prior_mean=prior_mean, prior_sd=prior_sd,
                     use_offset=use_offset):
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


if __name__ == "__main__":
    from data.generate_data import generate

    d = generate()
    print("=== Correct model (with exposure offset) ===")
    idata = fit(d, draws=500, tune=500, chains=2)
    print(az.summary(idata, var_names=["log_rate"]))
    print(f"true log_rate = {d['truth']['log_rate']:.3f}")
    print("\n=== Broken model (offset omitted) — note the bias ===")
    idata_bad = fit(d, draws=500, tune=500, chains=2, use_offset=False)
    print(az.summary(idata_bad, var_names=["log_rate"]))
