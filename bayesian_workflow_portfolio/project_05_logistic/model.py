"""Logistic-regression (Bernoulli GLM) model for Project 05.

Likelihood:  y_i ~ Bernoulli(p_i)
Link:        logit(p_i) = alpha + beta * x_i      (the logit *link function*)
Priors:      alpha ~ Normal(0, prior_sd)
             beta  ~ Normal(0, prior_sd)          (default prior_sd = 1.5)

The whole point of this project is the **link function**. We never put a prior
on ``p`` directly; we model the linear predictor ``eta = alpha + beta*x`` on the
unconstrained log-odds scale and squash it through the logistic sigmoid. Priors
therefore live on the log-odds scale, and their implications must be read back on
the probability scale (see the prior predictive check).

Default ``prior_sd=1.5`` is *weakly informative on the probability scale*: at the
mean covariate, Normal(0, 1.5) on alpha keeps the implied p spread broadly across
(0, 1) without piling mass at the 0/1 edges. A wide Normal(0, 10) — a common
"non-informative" mistake — instead implies that p is almost certainly ~0 or ~1
before seeing any data (demonstrated in the notebook's prior predictive check).

Exposes ``build_model`` and ``fit`` so the notebook, tests, SBC, and prior-
sensitivity scripts share one source of truth.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm


def build_model(data: dict, prior_sd: float = 1.5) -> pm.Model:
    """Construct the logistic GLM with Normal(0, prior_sd) coefficient priors."""
    x = np.asarray(data["x"], dtype=float)
    y = np.asarray(data["y"], dtype=int)
    with pm.Model() as model:
        x_data = pm.Data("x", x)
        alpha = pm.Normal("alpha", mu=0.0, sigma=prior_sd)
        beta = pm.Normal("beta", mu=0.0, sigma=prior_sd)
        eta = alpha + beta * x_data            # linear predictor (log-odds)
        p = pm.Deterministic("p", pm.math.sigmoid(eta))  # inverse logit link
        pm.Bernoulli("y", p=p, observed=y)
    return model


def fit(
    data: dict,
    prior_sd: float = 1.5,
    draws: int = 800,
    tune: int = 800,
    chains: int = 4,
    seed: int = 101,
    **kw,
) -> az.InferenceData:
    """Sample the posterior with NUTS and attach prior/posterior predictive."""
    with build_model(data, prior_sd=prior_sd):
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
    idata = fit(d, draws=500, tune=500, chains=2)
    print(az.summary(idata, var_names=["alpha", "beta"]))
    n_div = int(idata.sample_stats["diverging"].sum())
    print(f"divergences: {n_div}")
    print(f"true alpha={d['truth']['alpha']}, beta={d['truth']['beta']}")
