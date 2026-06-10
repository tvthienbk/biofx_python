"""Errors-in-variables (measurement-error) model for Project 12.

Two models are exposed:

* ``naive``  : regress y on the *observed* predictor x_obs, ignoring its noise.
               y_i ~ Normal(alpha + beta * x_obs_i, sigma_y).
               This is biased — the slope is attenuated toward 0.

* ``eiv``    : treat the true predictor as a LATENT variable.
               x_true_i ~ Normal(mu_x, sd_x)               # population of true x
               x_obs_i  ~ Normal(x_true_i, tau_x)          # measurement model
               y_i      ~ Normal(alpha + beta * x_true_i, sigma_y)
               With tau_x supplied (assumed known), this recovers the true slope.

``build_model(data, model="eiv"|"naive", tau_x=...)`` builds either;
``fit`` defaults to the EIV model. The measurement-error SD ``tau_x`` is taken as
known (from instrument calibration); the prior-sensitivity script studies how wrong
you can be about it.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm


def build_model(
    data: dict,
    model: str = "eiv",
    tau_x: float | None = None,
    beta_prior_sd: float = 5.0,
) -> pm.Model:
    """Construct the naive or errors-in-variables model.

    model : "eiv" (latent true predictor, default) or "naive" (regress on x_obs).
    tau_x : assumed-known measurement-error SD of the predictor. Defaults to the
            value stored in ``data['tau_x']``.
    """
    x_obs = np.asarray(data["x_obs"], dtype=float)
    y = np.asarray(data["y"], dtype=float)
    n = int(data["n"])
    if tau_x is None:
        tau_x = float(data["tau_x"])
    coords = {"obs": np.arange(n)}

    with pm.Model(coords=coords) as m:
        alpha = pm.Normal("alpha", mu=0.0, sigma=5.0)
        beta = pm.Normal("beta", mu=0.0, sigma=beta_prior_sd)
        sigma_y = pm.HalfNormal("sigma_y", sigma=2.0)

        if model == "naive":
            pm.Normal("y", mu=alpha + beta * x_obs, sigma=sigma_y,
                      observed=y, dims="obs")
        elif model == "eiv":
            # population of true predictor values
            mu_x = pm.Normal("mu_x", mu=0.0, sigma=5.0)
            sd_x = pm.HalfNormal("sd_x", sigma=5.0)
            x_true = pm.Normal("x_true", mu=mu_x, sigma=sd_x, dims="obs")
            # measurement model for the predictor (tau_x assumed known)
            pm.Normal("x_obs", mu=x_true, sigma=tau_x, observed=x_obs, dims="obs")
            # structural model for the response, in terms of the LATENT x_true
            pm.Normal("y", mu=alpha + beta * x_true, sigma=sigma_y,
                      observed=y, dims="obs")
        else:
            raise ValueError(f"unknown model: {model!r}")
    return m


def fit(
    data: dict,
    model: str = "eiv",
    tau_x: float | None = None,
    beta_prior_sd: float = 5.0,
    draws: int = 800,
    tune: int = 1000,
    chains: int = 4,
    target_accept: float = 0.9,
    seed: int = 101,
    **kw,
) -> az.InferenceData:
    """Sample the posterior with NUTS; attach prior + posterior predictive."""
    with build_model(data, model=model, tau_x=tau_x, beta_prior_sd=beta_prior_sd):
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            target_accept=target_accept,
            random_seed=seed,
            progressbar=False,
            idata_kwargs={"log_likelihood": True},
            **kw,
        )
        idata.extend(pm.sample_prior_predictive(draws=500, random_seed=seed))
        idata.extend(
            pm.sample_posterior_predictive(idata, random_seed=seed, progressbar=False)
        )
    return idata


if __name__ == "__main__":
    from data.generate_data import generate

    d = generate()
    print(f"True beta = {d['truth']['beta']} (attenuation factor "
          f"{d['attenuation_factor']:.2f})\n")

    print("=== Naive (regress y on x_obs) -> attenuated slope ===")
    idata_n = fit(d, model="naive", draws=500, tune=1000, chains=2)
    print(az.summary(idata_n, var_names=["alpha", "beta", "sigma_y"]))

    print("\n=== Errors-in-variables (latent x_true) -> recovers slope ===")
    idata_e = fit(d, model="eiv", draws=500, tune=1000, chains=2)
    print(az.summary(idata_e, var_names=["alpha", "beta", "sigma_y"]))
    print("divergences:", int(idata_e.sample_stats["diverging"].sum()))
