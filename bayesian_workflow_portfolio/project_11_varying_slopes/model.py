"""Varying-slopes model with correlated random effects (LKJ) for Project 11.

Two cell-line-level effects per group — an intercept ``alpha_g`` and a slope
``beta_g`` — drawn from a common bivariate distribution whose 2x2 covariance is
given an **LKJ** prior on the correlation. The teaching point is that intercepts
and slopes are *correlated* across cell lines; modeling that correlation (vs
forcing independence) is what fits the data.

Population model::

    [alpha_g, beta_g] ~ MVNormal([mu_a, mu_b], Sigma)
    Sigma via pm.LKJCholeskyCov(eta, sd_dist=HalfNormal)

We use the **non-centered** form: draw standard-normal z (2 x G), and set
effects = mu + (L @ z), where L is the Cholesky factor of Sigma. This decouples
the funnel exactly as in the scalar hierarchical models.

``build_model(data, correlated=True/False, ...)`` builds either the LKJ model or a
diagonal (independent intercept/slope) model used for comparison and as the
broken-notebook misfit. ``fit`` defaults to the correlated, non-centered model.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm
import pytensor.tensor as pt


def build_model(
    data: dict,
    correlated: bool = True,
    eta: float = 2.0,
    sd_prior: float = 1.0,
) -> pm.Model:
    """Construct the varying-slopes model.

    correlated : if True, use LKJCholeskyCov (models intercept-slope correlation);
                 if False, independent (diagonal) random effects — the misfit model.
    eta        : LKJ shape; eta>1 favors weaker correlations, eta=1 is uniform.
    sd_prior   : scale of the HalfNormal prior on the random-effect SDs.
    """
    y = np.asarray(data["y"], dtype=float)
    x = np.asarray(data["x"], dtype=float)
    group = np.asarray(data["group"]).astype(int)
    G = int(data["G"])
    coords = {"group": np.arange(G), "effect": ["alpha", "beta"], "obs": np.arange(len(y))}

    with pm.Model(coords=coords) as model:
        mu = pm.Normal("mu", mu=0.0, sigma=5.0, dims="effect")  # [mu_a, mu_b]
        pm.Deterministic("mu_a", mu[0])  # named for recovery checks
        pm.Deterministic("mu_b", mu[1])
        sigma = pm.HalfNormal("sigma", sigma=1.0)               # obs noise

        z = pm.Normal("z", 0.0, 1.0, dims=("effect", "group"))  # (2, G) std-normal

        if correlated:
            # LKJ prior on the 2x2 correlation; HalfNormal on the two SDs.
            chol, corr, sds = pm.LKJCholeskyCov(
                "chol",
                n=2,
                eta=eta,
                sd_dist=pm.HalfNormal.dist(sigma=sd_prior, size=2),
                compute_corr=True,
            )
            # non-centered: effects = mu + chol @ z   -> (G, 2)
            effects = pm.Deterministic(
                "effects", mu + (chol @ z).T, dims=("group", "effect")
            )
            pm.Deterministic("rho", corr[0, 1])
            pm.Deterministic("sd_a", sds[0])
            pm.Deterministic("sd_b", sds[1])
        else:
            # diagonal: independent intercept and slope SDs, correlation forced to 0
            sd = pm.HalfNormal("sd", sigma=sd_prior, dims="effect")
            effects = pm.Deterministic(
                "effects", mu + (sd[:, None] * z).T, dims=("group", "effect")
            )

        alpha = effects[:, 0]
        beta = effects[:, 1]
        mu_y = alpha[group] + beta[group] * x
        pm.Normal("y", mu=mu_y, sigma=sigma, observed=y, dims="obs")
    return model


def fit(
    data: dict,
    correlated: bool = True,
    eta: float = 2.0,
    sd_prior: float = 1.0,
    draws: int = 800,
    tune: int = 1000,
    chains: int = 4,
    target_accept: float = 0.9,
    seed: int = 101,
    **kw,
) -> az.InferenceData:
    """Sample the posterior with NUTS; attach prior + posterior predictive."""
    with build_model(data, correlated=correlated, eta=eta, sd_prior=sd_prior):
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
    print("=== Correlated (LKJ, non-centered, clean) ===")
    idata = fit(d, correlated=True, draws=500, tune=1000, chains=2)
    print(az.summary(idata, var_names=["mu", "sd_a", "sd_b", "rho", "sigma"]))
    print("divergences:", int(idata.sample_stats["diverging"].sum()))

    print("\n=== Diagonal (independent, misfit) ===")
    idata_d = fit(d, correlated=False, draws=500, tune=1000, chains=2)
    print(az.summary(idata_d, var_names=["mu", "sigma"]))
