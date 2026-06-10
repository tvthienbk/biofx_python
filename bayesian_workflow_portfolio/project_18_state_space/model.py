"""State-space models for Project 18, decoupled from the notebook.

We provide two models:

1. ``build_model`` / ``fit`` — a **local-level** state-space model:
       level_t = level_{t-1} + w_t,   w_t ~ N(0, sigma_level)   [process noise]
       y_t     = level_t + e_t,       e_t ~ N(0, sigma_obs)     [observation noise]
   The latent level is a Gaussian random walk. We implement it **non-centred**
   (a standardised innovation vector scaled by sigma_level and cumulatively summed)
   so the random walk does not develop a funnel as sigma_level shrinks.

2. ``build_ar1_model`` / ``fit_ar1`` — a stationary **AR(1)** alternative:
       y_t = mu + rho*(y_{t-1} - mu) + e_t,  e_t ~ N(0, sigma).
   This is the natural "no persistent drift" comparator.

THE pitfall: in the local-level model ``sigma_level`` (process) and ``sigma_obs``
(observation) are weakly identified — both shape how wiggly the series is. We use
informative-ish HalfNormal priors and rely on data length to separate them. The
priors must NOT let them trade off freely (the broken notebook shows what happens).

Exposes builders + ``fit`` functions so the notebook, tests, SBC, and prior-
sensitivity scripts share one source of truth.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm
import pytensor.tensor as pt


def build_model(data: dict,
                sigma_level_sd: float = 0.5,
                sigma_obs_sd: float = 1.0,
                level0_sd: float = 5.0) -> pm.Model:
    """Local-level (random-walk + noise) state-space model, non-centred.

    Priors:
      sigma_level ~ HalfNormal(0.5)  -- process noise; expect modest drift.
      sigma_obs   ~ HalfNormal(1.0)  -- observation noise; can be larger.
      level0      ~ Normal(mean(y), 5)
    """
    y = np.asarray(data["y"], dtype=float)
    t = y.size
    with pm.Model() as model:
        sigma_level = pm.HalfNormal("sigma_level", sigma=sigma_level_sd)
        sigma_obs = pm.HalfNormal("sigma_obs", sigma=sigma_obs_sd)
        level0 = pm.Normal("level0", mu=float(y.mean()), sigma=level0_sd)
        # non-centred random walk: standardised innovations -> scaled cumsum
        z = pm.Normal("z", 0.0, 1.0, shape=t - 1)
        increments = z * sigma_level
        level = pm.Deterministic(
            "level", pt.concatenate([[level0], level0 + pt.cumsum(increments)])
        )
        pm.Normal("y_obs", mu=level, sigma=sigma_obs, observed=y)
    return model


def fit(data: dict, draws: int = 600, tune: int = 1000, chains: int = 2,
        seed: int = 101, target_accept: float = 0.95, **build_kw) -> az.InferenceData:
    """Sample the local-level model with NUTS; attach prior + posterior predictive."""
    with build_model(data, **build_kw):
        idata = pm.sample(
            draws=draws, tune=tune, chains=chains, cores=1,
            random_seed=seed, target_accept=target_accept, progressbar=False,
            idata_kwargs={"log_likelihood": True},
        )
        idata.extend(pm.sample_prior_predictive(draws=200, random_seed=seed))
        idata.extend(pm.sample_posterior_predictive(
            idata, random_seed=seed, progressbar=False))
    return idata


def build_ar1_model(data: dict) -> pm.Model:
    """Stationary AR(1) comparator: y_t = mu + rho*(y_{t-1}-mu) + e_t."""
    y = np.asarray(data["y"], dtype=float)
    with pm.Model() as model:
        mu = pm.Normal("mu", mu=float(y.mean()), sigma=5.0)
        rho = pm.Uniform("rho", lower=-1.0, upper=1.0)
        sigma = pm.HalfNormal("sigma", sigma=1.0)
        # likelihood for t >= 1 conditional on previous observation
        pm.Normal("y_obs", mu=mu + rho * (y[:-1] - mu), sigma=sigma, observed=y[1:])
    return model


def fit_ar1(data: dict, draws: int = 600, tune: int = 1000, chains: int = 2,
            seed: int = 101, **kw) -> az.InferenceData:
    """Sample the AR(1) model with NUTS; attach log-likelihood for LOO."""
    with build_ar1_model(data):
        idata = pm.sample(
            draws=draws, tune=tune, chains=chains, cores=1,
            random_seed=seed, progressbar=False,
            idata_kwargs={"log_likelihood": True}, **kw,
        )
    return idata


if __name__ == "__main__":
    from data.generate_data import generate

    d = generate()
    idata = fit(d, draws=400, tune=800, chains=2)
    print(az.summary(idata, var_names=["sigma_level", "sigma_obs", "level0"]))
    n_div = int(idata.sample_stats["diverging"].sum())
    print(f"divergences: {n_div}")
    lvl = idata.posterior["level"].mean(dim=("chain", "draw")).values
    mae = float(np.mean(np.abs(lvl - d["level_true"])))
    print(f"latent-level recovery MAE: {mae:.3f}")
