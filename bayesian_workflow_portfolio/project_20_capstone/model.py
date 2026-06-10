"""Capstone models for Project 20, decoupled from the notebook.

We provide two models for compound prioritization and a decision layer:

1. ``build_model`` / ``fit`` — the **hierarchical (partial-pooling)** model,
   **non-centred**:
       mu     ~ Normal(0, 2)              population mean effect
       tau    ~ HalfNormal(1)             between-compound sd
       z_j    ~ Normal(0, 1)              standardised compound offsets
       theta_j = mu + tau * z_j
       sigma  ~ HalfNormal(1)             within-compound assay noise
       y_{j,i} ~ Normal(theta_j, sigma)
   Partial pooling shrinks noisy (few-replicate) compounds toward the population
   mean, which is the cure for the winner's-curse trap.

2. ``build_pooled_model`` / ``fit_pooled`` — the **complete-pooling** comparator:
   one shared effect for all compounds (tau -> 0). Used in the LOO comparison; it
   under-fits when compounds genuinely differ.

3. Decision layer (``decision_table``): turns the posterior over theta into an
   expected-utility-per-compound table given a cost-loss specification, plus
   probability-of-being-best and expected regret. This is where the project insists
   on making a DECISION, not stopping at the posterior.

Exposes builders + fit functions so the notebook, tests, SBC, and prior-
sensitivity scripts share one source of truth.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm
import pytensor.tensor as pt


def build_model(data: dict, mu_sd: float = 2.0, tau_sd: float = 1.0,
                sigma_sd: float = 1.0) -> pm.Model:
    """Hierarchical partial-pooling model (non-centred)."""
    comp_idx = np.asarray(data["comp_idx"], dtype=int)
    y = np.asarray(data["y"], dtype=float)
    j = int(data["j"])
    with pm.Model() as model:
        mu = pm.Normal("mu", mu=0.0, sigma=mu_sd)
        tau = pm.HalfNormal("tau", sigma=tau_sd)
        z = pm.Normal("z", 0.0, 1.0, shape=j)
        theta = pm.Deterministic("theta", mu + tau * z)
        sigma = pm.HalfNormal("sigma", sigma=sigma_sd)
        pm.Normal("y_obs", mu=theta[comp_idx], sigma=sigma, observed=y)
    return model


def fit(data: dict, draws: int = 600, tune: int = 1000, chains: int = 2,
        seed: int = 101, target_accept: float = 0.95, **build_kw) -> az.InferenceData:
    """Sample the hierarchical model; attach prior + posterior predictive + loglik."""
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


def build_pooled_model(data: dict, mu_sd: float = 2.0,
                       sigma_sd: float = 1.0) -> pm.Model:
    """Complete-pooling comparator: a single shared effect for all compounds."""
    y = np.asarray(data["y"], dtype=float)
    with pm.Model() as model:
        mu = pm.Normal("mu", mu=0.0, sigma=mu_sd)
        sigma = pm.HalfNormal("sigma", sigma=sigma_sd)
        pm.Normal("y_obs", mu=mu, sigma=sigma, observed=y)
    return model


def fit_pooled(data: dict, draws: int = 600, tune: int = 1000, chains: int = 2,
               seed: int = 101, **kw) -> az.InferenceData:
    """Sample the complete-pooling model; attach log-likelihood for LOO."""
    with build_pooled_model(data):
        idata = pm.sample(
            draws=draws, tune=tune, chains=chains, cores=1,
            random_seed=seed, progressbar=False,
            idata_kwargs={"log_likelihood": True}, **kw,
        )
    return idata


def posterior_theta(idata: az.InferenceData) -> np.ndarray:
    """Return posterior draws of theta as a (n_draws, J) array."""
    th = idata.posterior["theta"]
    return th.stack(sample=("chain", "draw")).transpose("sample", "theta_dim_0").values


def decision_table(idata: az.InferenceData, cost: float = 0.0) -> dict:
    """Turn the posterior over theta into a decision.

    We define the utility of advancing compound j as its true effect minus a fixed
    advancement cost: U_j = theta_j - cost. We then compute, per compound:
      * expected utility    E[theta_j] - cost
      * P(best)             probability theta_j is the largest across compounds
      * expected regret     E[max_k theta_k - theta_j]  (loss vs the oracle)
    The recommended compound minimises expected regret (equivalently maximises
    expected utility here, since cost is common). We also return the naive
    argmax-of-posterior-mean and argmax-of-raw-mean for contrast.
    """
    theta = posterior_theta(idata)              # (S, J)
    S, J = theta.shape
    exp_util = theta.mean(axis=0) - cost
    best_draw = theta.argmax(axis=1)            # which compound is best each draw
    p_best = np.array([(best_draw == j).mean() for j in range(J)])
    row_max = theta.max(axis=1, keepdims=True)
    exp_regret = (row_max - theta).mean(axis=0)
    return {
        "exp_util": exp_util,
        "p_best": p_best,
        "exp_regret": exp_regret,
        "recommend_min_regret": int(np.argmin(exp_regret)),
        "recommend_max_eu": int(np.argmax(exp_util)),
        "argmax_posterior_mean": int(np.argmax(theta.mean(axis=0))),
    }


if __name__ == "__main__":
    from data.generate_data import generate

    d = generate()
    idata = fit(d, draws=400, tune=800, chains=2)
    print(az.summary(idata, var_names=["mu", "tau", "sigma"]))
    n_div = int(idata.sample_stats["diverging"].sum())
    print(f"divergences: {n_div}")
    dec = decision_table(idata)
    print(f"true best     = #{d['best_true']}")
    print(f"raw-mean pick = #{int(np.argmax(d['raw_means']))}")
    print(f"min-regret pick = #{dec['recommend_min_regret']}, "
          f"max-EU pick = #{dec['recommend_max_eu']}")
