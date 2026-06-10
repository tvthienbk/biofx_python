"""Normal location-scale model for Project 02, decoupled from the notebook.

Likelihood: y_i ~ Normal(mu, sigma)
Priors:     mu    ~ Normal(prior_mean, prior_sd)     (weakly-informative location)
            sigma ~ HalfNormal(sigma_scale)          (proper, positive scale prior)

The NEW skill here is jointly inferring a *scale* parameter ``sigma`` alongside a
location ``mu``. The KEY PITFALL is the scale prior: a flat/improper prior on
``sigma`` (uniform on (0, inf)) is not "uninformative" — it is improper, puts
unbounded mass on huge variances, and can wreck inference. We therefore use a
proper HalfNormal by default and offer Exponential / HalfCauchy alternatives for
the prior-sensitivity study.

Exposes ``build_model`` and ``fit`` so the notebook, tests, SBC, and prior-
sensitivity scripts all share one source of truth.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm

# Prior hyperparameters (weakly-informative, on the scale of the data).
PRIOR_MEAN = 5.0     # prior guess for the location mu
PRIOR_SD = 10.0      # broad: 2 SD covers roughly -15..25, far wider than plausible
SIGMA_SCALE = 5.0    # HalfNormal scale for sigma; mass concentrated below ~10


def build_model(
    data: dict,
    prior_mean: float = PRIOR_MEAN,
    prior_sd: float = PRIOR_SD,
    sigma_scale: float = SIGMA_SCALE,
    sigma_prior: str = "halfnormal",
) -> pm.Model:
    """Construct the Normal(mu, sigma) model for replicate measurements.

    ``sigma_prior`` selects the scale prior: 'halfnormal' (default),
    'exponential', or 'halfcauchy'. Used by the prior-sensitivity study.
    """
    y = np.asarray(data["y"])
    with pm.Model() as model:
        mu = pm.Normal("mu", mu=prior_mean, sigma=prior_sd)
        if sigma_prior == "halfnormal":
            sigma = pm.HalfNormal("sigma", sigma=sigma_scale)
        elif sigma_prior == "exponential":
            # mean of Exponential(lam) is 1/lam; match scale ~ sigma_scale
            sigma = pm.Exponential("sigma", lam=1.0 / sigma_scale)
        elif sigma_prior == "halfcauchy":
            sigma = pm.HalfCauchy("sigma", beta=sigma_scale)
        else:  # pragma: no cover - guarded by caller
            raise ValueError(f"unknown sigma_prior: {sigma_prior!r}")
        pm.Normal("y", mu=mu, sigma=sigma, observed=y)
    return model


def fit(
    data: dict,
    prior_mean: float = PRIOR_MEAN,
    prior_sd: float = PRIOR_SD,
    sigma_scale: float = SIGMA_SCALE,
    sigma_prior: str = "halfnormal",
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 4,
    seed: int = 202,
    **kw,
) -> az.InferenceData:
    """Sample the posterior with NUTS and attach prior/posterior predictive."""
    with build_model(data, prior_mean=prior_mean, prior_sd=prior_sd,
                     sigma_scale=sigma_scale, sigma_prior=sigma_prior):
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
    idata = fit(d, draws=500, tune=500, chains=2)
    print(az.summary(idata, var_names=["mu", "sigma"]))
    n_div = int(idata.sample_stats["diverging"].sum())
    print(f"divergences: {n_div}")
