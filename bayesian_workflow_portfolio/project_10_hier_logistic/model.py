"""Hierarchical logistic (varying-intercepts) model for Project 10.

Likelihood:    y_i ~ Bernoulli(p_i),  logit(p_i) = alpha_{g[i]} + beta * x_i
Intercepts:    alpha_g ~ Normal(mu, tau)        # group-varying, exchangeable
Hyperpriors:   mu ~ Normal(0, 1.5);  tau ~ HalfNormal(1);  beta ~ Normal(0, 1.5)

This is the GLM analogue of Project 09: instead of a hierarchical *mean* we have a
hierarchical *intercept* inside a logistic link. The same funnel hazard applies, so
``fit`` defaults to the **non-centered** parameterization
``alpha_g = mu + tau * z_g``. ``build_model(data, parameterization=...)`` builds
either form; a too-tight ``tau_prior_sd`` drives the over-pooling pathology shown
in the broken notebook.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm


def build_model(
    data: dict,
    parameterization: str = "noncentered",
    mu_prior_sd: float = 1.5,
    tau_prior_sd: float = 1.0,
    beta_prior_sd: float = 1.5,
) -> pm.Model:
    """Construct the hierarchical logistic model.

    parameterization : "noncentered" (default, clean) or "centered" (funnel-prone).
    tau_prior_sd     : SD of the HalfNormal prior on the between-group SD ``tau``.
                       A very small value forces excessive pooling of intercepts.
    """
    y = np.asarray(data["y"])
    x = np.asarray(data["x"], dtype=float)
    group = np.asarray(data["group"]).astype(int)
    G = int(data["G"])
    coords = {"group": np.arange(G), "obs": np.arange(len(y))}

    with pm.Model(coords=coords) as model:
        mu = pm.Normal("mu", mu=0.0, sigma=mu_prior_sd)
        tau = pm.HalfNormal("tau", sigma=tau_prior_sd)
        beta = pm.Normal("beta", mu=0.0, sigma=beta_prior_sd)

        if parameterization == "centered":
            alpha = pm.Normal("alpha", mu=mu, sigma=tau, dims="group")
        elif parameterization == "noncentered":
            z = pm.Normal("z", mu=0.0, sigma=1.0, dims="group")
            alpha = pm.Deterministic("alpha", mu + tau * z, dims="group")
        else:
            raise ValueError(f"unknown parameterization: {parameterization!r}")

        eta = alpha[group] + beta * x
        pm.Bernoulli("y", logit_p=eta, observed=y, dims="obs")
    return model


def fit(
    data: dict,
    parameterization: str = "noncentered",
    mu_prior_sd: float = 1.5,
    tau_prior_sd: float = 1.0,
    beta_prior_sd: float = 1.5,
    draws: int = 800,
    tune: int = 1000,
    chains: int = 4,
    target_accept: float = 0.9,
    seed: int = 101,
    **kw,
) -> az.InferenceData:
    """Sample the posterior with NUTS; attach prior + posterior predictive."""
    with build_model(
        data,
        parameterization=parameterization,
        mu_prior_sd=mu_prior_sd,
        tau_prior_sd=tau_prior_sd,
        beta_prior_sd=beta_prior_sd,
    ):
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
    print("=== Non-centered (clean) ===")
    idata = fit(d, parameterization="noncentered", draws=500, tune=1000, chains=2)
    print(az.summary(idata, var_names=["mu", "tau", "beta"]))
    print("divergences:", int(idata.sample_stats["diverging"].sum()))

    print("\n=== Centered + tight tau prior (over-pooling) ===")
    idata_c = fit(d, parameterization="centered", tau_prior_sd=0.1,
                  draws=500, tune=1000, chains=2)
    print(az.summary(idata_c, var_names=["mu", "tau", "beta"]))
    print("divergences:", int(idata_c.sample_stats["diverging"].sum()))
