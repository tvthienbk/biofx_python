"""Two-component Gaussian mixture for Project 13, decoupled from the notebook.

Likelihood (marginalized over the latent labels, via ``pm.NormalMixture``):

    y_i ~ sum_k w_k * Normal(mu_k, sigma)

Priors:
    w     ~ Dirichlet(a)                       (mixing weights, default a=(2,2))
    mu    ~ Normal(0, prior_mu_sd)  with an ORDERED transform so mu[0] < mu[1]
    sigma ~ HalfNormal(prior_sigma_sd)         (shared component spread)

**Why the ordered transform?** A finite mixture is invariant under permuting the
component labels: (w, mu) and (w', mu') with the components swapped give the
*identical* likelihood. Across MCMC chains (or even within a chain) the sampler
can hop between these equivalent modes — "label switching" — which corrupts the
per-component marginals and inflates R-hat. Constraining ``mu[0] < mu[1]`` with
``pm.distributions.transforms.ordered`` (and a sorted ``initval``) removes the
symmetry and pins each label to a fixed component.

Exposes ``build_model`` and ``fit`` so the notebook, tests, SBC, and prior-
sensitivity scripts all share one source of truth.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm
import pymc.distributions.transforms as tr


def build_model(
    data: dict,
    w_conc: float = 2.0,
    prior_mu_sd: float = 3.0,
    prior_sigma_sd: float = 1.0,
    ordered: bool = True,
) -> pm.Model:
    """Construct the 2-component Gaussian mixture.

    Set ``ordered=False`` to reproduce the label-switching pathology (used by the
    broken notebook). With ``ordered=True`` (default) the means are forced to be
    increasing, which breaks the labeling symmetry.
    """
    y = np.asarray(data["y"], dtype=float)
    with pm.Model() as model:
        w = pm.Dirichlet("w", a=np.array([w_conc, w_conc]))
        if ordered:
            mu = pm.Normal(
                "mu",
                mu=0.0,
                sigma=prior_mu_sd,
                shape=2,
                transform=tr.ordered,
                initval=np.array([-1.0, 1.0]),
            )
        else:
            mu = pm.Normal("mu", mu=0.0, sigma=prior_mu_sd, shape=2)
        sigma = pm.HalfNormal("sigma", sigma=prior_sigma_sd)
        pm.NormalMixture("y", w=w, mu=mu, sigma=sigma, observed=y)
    return model


def fit(
    data: dict,
    w_conc: float = 2.0,
    prior_mu_sd: float = 3.0,
    prior_sigma_sd: float = 1.0,
    ordered: bool = True,
    draws: int = 500,
    tune: int = 1000,
    chains: int = 4,
    seed: int = 13,
    target_accept: float = 0.9,
    **kw,
) -> az.InferenceData:
    """Sample the posterior with NUTS and attach prior/posterior predictive."""
    with build_model(
        data,
        w_conc=w_conc,
        prior_mu_sd=prior_mu_sd,
        prior_sigma_sd=prior_sigma_sd,
        ordered=ordered,
    ):
        # NOTE: log_likelihood is computed separately below rather than via
        # idata_kwargs, because the ordered-transform `initval` triggers PyMC's
        # "non-default initial_values" path inside in-line log-likelihood compute.
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            random_seed=seed,
            target_accept=target_accept,
            progressbar=False,
            **kw,
        )
        try:
            pm.compute_log_likelihood(idata, progressbar=False)
        except Exception:  # noqa: BLE001  (keep fit robust; LOO is optional here)
            pass
        idata.extend(pm.sample_prior_predictive(draws=400, random_seed=seed))
        idata.extend(
            pm.sample_posterior_predictive(idata, random_seed=seed, progressbar=False)
        )
    return idata


def add_separation(idata: az.InferenceData) -> az.InferenceData:
    """Attach scalar, summary-friendly identifiable quantities to the posterior.

    Adds ``separation`` (mu[1]-mu[0]), ``mu_low``/``mu_high`` (the ordered means
    as named scalars), ``sigma_`` (alias), and ``w_high`` (weight of the higher
    mean). These are plain scalar variables so ``az.summary(var_names=...)`` and
    hence ``check_recovery`` can address them by name.
    """
    mu = idata.posterior["mu"]
    idata.posterior["mu_low"] = mu.isel(mu_dim_0=0)
    idata.posterior["mu_high"] = mu.isel(mu_dim_0=1)
    idata.posterior["separation"] = mu.isel(mu_dim_0=1) - mu.isel(mu_dim_0=0)
    idata.posterior["w_high"] = idata.posterior["w"].isel(w_dim_0=1)
    return idata


if __name__ == "__main__":
    from data.generate_data import generate

    d = generate()
    idata = fit(d, draws=500, tune=1000, chains=2)
    add_separation(idata)
    print(az.summary(idata, var_names=["w", "mu", "sigma", "separation"]))
    print("divergences:", int(idata.sample_stats["diverging"].sum()))
