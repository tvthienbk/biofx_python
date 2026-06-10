"""Hierarchical Normal (partial-pooling) model for Project 09.

Likelihood:   y_ij ~ Normal(theta_j, sigma)
Group means:  theta_j ~ Normal(mu, tau)
Hyperpriors:  mu ~ Normal(5, 5);  tau ~ HalfNormal(2);  sigma ~ HalfNormal(2)

The central teaching point is **parameterization**. The natural ("centered")
form ``theta_j ~ Normal(mu, tau)`` couples ``theta_j`` to ``tau`` and creates
Neal's funnel: when ``tau`` is small the joint geometry is a sharp neck the
sampler cannot traverse, producing divergences. The **non-centered** form
introduces standard-normal offsets ``z_j`` and sets ``theta_j = mu + tau * z_j``,
which decouples the geometry and removes the funnel.

``build_model(data, parameterization=...)`` builds either form;
``fit`` defaults to the non-centered (clean) version.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm


def build_model(
    data: dict,
    parameterization: str = "noncentered",
    mu_prior_sd: float = 5.0,
    tau_prior_sd: float = 2.0,
) -> pm.Model:
    """Construct the hierarchical Normal model.

    parameterization : "noncentered" (default, clean) or "centered" (funnel-prone).
    tau_prior_sd     : SD of the HalfNormal prior on the between-group SD ``tau``.
    """
    y = np.asarray(data["y"])
    group = np.asarray(data["group"]).astype(int)
    J = int(data["J"])
    coords = {"group": np.arange(J), "obs": np.arange(len(y))}

    with pm.Model(coords=coords) as model:
        mu = pm.Normal("mu", mu=5.0, sigma=mu_prior_sd)
        tau = pm.HalfNormal("tau", sigma=tau_prior_sd)
        sigma = pm.HalfNormal("sigma", sigma=2.0)

        if parameterization == "centered":
            theta = pm.Normal("theta", mu=mu, sigma=tau, dims="group")
        elif parameterization == "noncentered":
            z = pm.Normal("z", mu=0.0, sigma=1.0, dims="group")
            theta = pm.Deterministic("theta", mu + tau * z, dims="group")
        else:
            raise ValueError(f"unknown parameterization: {parameterization!r}")

        pm.Normal("y", mu=theta[group], sigma=sigma, observed=y, dims="obs")
    return model


def fit(
    data: dict,
    parameterization: str = "noncentered",
    mu_prior_sd: float = 5.0,
    tau_prior_sd: float = 2.0,
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
    print(az.summary(idata, var_names=["mu", "tau", "sigma"]))
    print("divergences:", int(idata.sample_stats["diverging"].sum()))

    print("\n=== Centered (funnel-prone) ===")
    idata_c = fit(d, parameterization="centered", draws=500, tune=1000, chains=2)
    print(az.summary(idata_c, var_names=["mu", "tau", "sigma"]))
    print("divergences:", int(idata_c.sample_stats["diverging"].sum()))
