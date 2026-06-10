"""Count-GLM models for Project 06 — Poisson vs Negative-Binomial.

We expose BOTH models so the notebook can fit each and compare them with LOO:

  Poisson GLM      log(mu_i) = beta0 + beta1*x_i,  y_i ~ Poisson(mu_i)
  Neg-Binomial GLM log(mu_i) = beta0 + beta1*x_i,  y_i ~ NB(mu_i, alpha)

The log link keeps mu positive for any linear predictor. The new skill is
**overdispersion**: Poisson forces Var(y)=mu, but real count data (RNA-seq, etc.)
have Var(y) > mu. The NB adds a dispersion parameter alpha with
Var(y) = mu + mu^2/alpha, recovering Poisson as alpha -> infinity.

Priors (weakly informative on the log scale):
  beta0 ~ Normal(0, 2)   (mu ~ exp(N(0,2)); broad but not absurd)
  beta1 ~ Normal(0, 1)
  alpha ~ Gamma(2, 0.1)  (mean 20; supports both mild and strong dispersion)

Exposes ``build_model(data, model=...)`` and ``fit(data, model=..., ...)`` so the
notebook, test, SBC, and prior-sensitivity scripts share one source of truth.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm


def build_model(
    data: dict,
    model: str = "nb",
    beta0_sd: float = 2.0,
    beta1_sd: float = 1.0,
    alpha_a: float = 2.0,
    alpha_b: float = 0.1,
) -> pm.Model:
    """Construct a Poisson or Negative-Binomial count GLM with a log link."""
    x = np.asarray(data["x"], dtype=float)
    y = np.asarray(data["y"], dtype=int)
    if model not in ("nb", "poisson"):
        raise ValueError("model must be 'nb' or 'poisson'")
    with pm.Model() as m:
        x_data = pm.Data("x", x)
        beta0 = pm.Normal("beta0", 0.0, beta0_sd)
        beta1 = pm.Normal("beta1", 0.0, beta1_sd)
        mu = pm.Deterministic("mu", pm.math.exp(beta0 + beta1 * x_data))  # log link
        if model == "nb":
            alpha = pm.Gamma("alpha", alpha=alpha_a, beta=alpha_b)
            pm.NegativeBinomial("y", mu=mu, alpha=alpha, observed=y)
        else:
            pm.Poisson("y", mu=mu, observed=y)
    return m


def fit(
    data: dict,
    model: str = "nb",
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 4,
    seed: int = 101,
    **kw,
) -> az.InferenceData:
    """Sample the posterior with NUTS and attach prior/posterior predictive."""
    with build_model(data, model=model, **{k: kw.pop(k) for k in list(kw)
                                           if k in ("beta0_sd", "beta1_sd",
                                                    "alpha_a", "alpha_b")}):
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
    for mdl in ("poisson", "nb"):
        idata = fit(d, model=mdl, draws=500, tune=500, chains=2)
        vars_ = ["beta0", "beta1"] + (["alpha"] if mdl == "nb" else [])
        print(f"--- {mdl} ---")
        print(az.summary(idata, var_names=vars_))
        print("divergences:", int(idata.sample_stats["diverging"].sum()))
    print(f"true beta0={truth['beta0']}, beta1={truth['beta1']}, alpha={truth['alpha']}")
