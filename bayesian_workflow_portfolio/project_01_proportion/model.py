"""Beta–Binomial model for Project 01, decoupled from the notebook.

Likelihood: y_i ~ Bernoulli(theta)         (equivalently k ~ Binomial(n, theta))
Prior:      theta ~ Beta(a, b)             (conjugate; default Beta(2, 2))

Beta(2, 2) is a mild, unimodal prior centred at 0.5 that gently pulls away from
the degenerate 0/1 edges — a defensible weakly-informative choice for an assay
probability, and far safer than a "flat" Beta(1, 1) when N is small.

Exposes ``build_model`` and ``fit`` so the notebook, tests, SBC, and prior-
sensitivity scripts all share one source of truth.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm


def build_model(data: dict, a: float = 2.0, b: float = 2.0) -> pm.Model:
    """Construct the Beta–Bernoulli model for observed 0/1 outcomes."""
    y = np.asarray(data["y"])
    with pm.Model() as model:
        theta = pm.Beta("theta", alpha=a, beta=b)
        pm.Bernoulli("y", p=theta, observed=y)
    return model


def fit(
    data: dict,
    a: float = 2.0,
    b: float = 2.0,
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 4,
    seed: int = 101,
    **kw,
) -> az.InferenceData:
    """Sample the posterior with NUTS and attach prior/posterior predictive."""
    with build_model(data, a=a, b=b):
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


def analytic_posterior(data: dict, a: float = 2.0, b: float = 2.0) -> tuple[float, float]:
    """Conjugate posterior is Beta(a + k, b + n - k). Returns (alpha, beta)."""
    k, n = int(data["k"]), int(data["n"])
    return a + k, b + n - k


if __name__ == "__main__":
    from data.generate_data import generate

    d = generate()
    idata = fit(d, draws=500, tune=500, chains=2)
    print(az.summary(idata, var_names=["theta"]))
    a_post, b_post = analytic_posterior(d)
    print(f"Analytic posterior: Beta({a_post}, {b_post}), mean={a_post/(a_post+b_post):.3f}")
