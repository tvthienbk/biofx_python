"""Regression models for Project 07 — Normal vs Student-t (robust) likelihood.

We expose BOTH models so the notebook can fit each and compare with LOO:

  Normal    y_i ~ Normal(alpha + beta*x_i, sigma)
  StudentT  y_i ~ StudentT(nu, alpha + beta*x_i, sigma)

Both share the linear predictor alpha + beta*x. The new skill is **heavy tails**:
the Student-t has a free degrees-of-freedom nu controlling tail weight. Small nu
=> heavy tails that absorb outliers (the likelihood stops over-penalizing far
points), so the fit is robust. As nu -> infinity the Student-t -> Normal, so the
robust model nests the non-robust one.

Priors (weakly informative; x and y are on O(1)-O(10) scales):
  alpha ~ Normal(0, 5)
  beta  ~ Normal(0, 5)
  sigma ~ HalfNormal(5)
  nu    ~ Gamma(2, 0.1)   (mean 20; mass on small nu => allows heavy tails,
                            but also lets nu grow if the data are clean)

Exposes ``build_model(data, model=...)`` and ``fit(data, model=..., ...)``.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm


def build_model(
    data: dict,
    model: str = "studentt",
    coef_sd: float = 5.0,
    sigma_sd: float = 5.0,
    nu_a: float = 2.0,
    nu_b: float = 0.1,
) -> pm.Model:
    """Construct a Normal or Student-t linear regression."""
    x = np.asarray(data["x"], dtype=float)
    y = np.asarray(data["y"], dtype=float)
    if model not in ("normal", "studentt"):
        raise ValueError("model must be 'normal' or 'studentt'")
    with pm.Model() as m:
        x_data = pm.Data("x", x)
        alpha = pm.Normal("alpha", 0.0, coef_sd)
        beta = pm.Normal("beta", 0.0, coef_sd)
        sigma = pm.HalfNormal("sigma", sigma_sd)
        mu = pm.Deterministic("mu", alpha + beta * x_data)
        if model == "studentt":
            nu = pm.Gamma("nu", alpha=nu_a, beta=nu_b)
            pm.StudentT("y", nu=nu, mu=mu, sigma=sigma, observed=y)
        else:
            pm.Normal("y", mu=mu, sigma=sigma, observed=y)
    return m


def fit(
    data: dict,
    model: str = "studentt",
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 4,
    seed: int = 101,
    **kw,
) -> az.InferenceData:
    """Sample the posterior with NUTS and attach prior/posterior predictive."""
    build_kw = {k: kw.pop(k) for k in list(kw)
                if k in ("coef_sd", "sigma_sd", "nu_a", "nu_b")}
    with build_model(data, model=model, **build_kw):
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
        idata.extend(
            pm.sample_posterior_predictive(idata, random_seed=seed, progressbar=False)
        )
    return idata


if __name__ == "__main__":
    from data.generate_data import generate

    d = generate()
    truth = d["truth"]
    for mdl in ("normal", "studentt"):
        idata = fit(d, model=mdl, draws=500, tune=500, chains=2)
        vars_ = ["alpha", "beta", "sigma"] + (["nu"] if mdl == "studentt" else [])
        print(f"--- {mdl} ---")
        print(az.summary(idata, var_names=vars_))
        print("divergences:", int(idata.sample_stats["diverging"].sum()))
    print(f"true (clean) alpha={truth['alpha']}, beta={truth['beta']}, "
          f"sigma={truth['sigma']}")
