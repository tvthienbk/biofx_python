"""2-state Gaussian-emission HMM for Project 14, with the discrete states
**marginalized out** by the forward algorithm.

We never sample the discrete state path. Instead we compute the exact marginal
likelihood p(y | params) by summing over all state sequences using the forward
recursion, implemented in ``pytensor.scan`` and added to the model with a
``pm.Potential``. NUTS then samples the continuous parameters only.

Parameters & priors:

    p01 ~ Beta(2, 8)        # closed -> open switch prob (prior favours rare switches)
    p10 ~ Beta(2, 8)        # open  -> closed switch prob
    mu  ~ Normal(0, 3), ordered transform so mu[0] < mu[1]  (breaks label symmetry)
    sigma ~ HalfNormal(1)   # shared emission noise

Forward algorithm (in log space):

    a_1[j]    = log pi[j] + log N(y_1; mu_j, sigma)
    a_t[j]    = log N(y_t; mu_j, sigma) + logsumexp_i ( a_{t-1}[i] + log P[i, j] )
    log p(y)  = logsumexp_j a_T[j]

The log-sum-exp normalization at every step is what keeps the recursion a proper
marginal likelihood; omitting it (a classic bug, see the broken notebook) gives a
Viterbi-like *max* path probability instead of the sum, biasing inference.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm
import pymc.distributions.transforms as tr
import pytensor.tensor as pt
from pytensor import scan


def _forward_logp(y, p01, p10, mu, sigma, ordered_correct: bool = True):
    """Forward-algorithm marginal log-likelihood as a pytensor scalar.

    ``ordered_correct=True`` uses the proper log-sum-exp recursion. The argument
    exists so the broken notebook can request the buggy (no-normalization)
    variant for teaching.
    """
    yc = y[:, None]                                   # (T, 1)
    # log emission probs, shape (T, 2)
    logem = -0.5 * pt.log(2.0 * np.pi * sigma ** 2) - 0.5 * ((yc - mu[None, :]) / sigma) ** 2
    # log transition matrix, shape (2, 2)
    logP = pt.log(
        pt.stack([pt.stack([1 - p01, p01]), pt.stack([p10, 1 - p10])])
    )
    log_pi = pt.log(pt.as_tensor([0.5, 0.5]))
    a0 = log_pi + logem[0]

    def step(logem_t, a_prev, logP):
        m = a_prev[:, None] + logP                    # (2 prev, 2 next)
        return logem_t + pt.logsumexp(m, axis=0)

    seq, _ = scan(
        fn=step,
        sequences=[logem[1:]],
        outputs_info=[a0],
        non_sequences=[logP],
        return_updates=True,
    )
    last = seq[-1]
    return pt.logsumexp(last)


def build_model(
    data: dict,
    a_switch: float = 2.0,
    b_switch: float = 8.0,
    prior_mu_sd: float = 3.0,
    prior_sigma_sd: float = 1.0,
    ordered: bool = True,
) -> pm.Model:
    """Construct the marginalized 2-state Gaussian HMM.

    ``ordered=False`` removes the emission-mean ordering, reproducing the
    state-label non-identifiability (used by the broken notebook).
    """
    y = np.asarray(data["y"], dtype=float)
    yt = pt.as_tensor_variable(y)
    with pm.Model() as model:
        p01 = pm.Beta("p01", a_switch, b_switch)
        p10 = pm.Beta("p10", a_switch, b_switch)
        if ordered:
            mu = pm.Normal(
                "mu",
                0.0,
                prior_mu_sd,
                shape=2,
                transform=tr.ordered,
                initval=np.array([-1.0, 1.0]),
            )
        else:
            mu = pm.Normal("mu", 0.0, prior_mu_sd, shape=2)
        sigma = pm.HalfNormal("sigma", prior_sigma_sd)
        pm.Deterministic("separation", mu[1] - mu[0])
        pm.Potential("hmm_forward", _forward_logp(yt, p01, p10, mu, sigma))
    return model


def fit(
    data: dict,
    a_switch: float = 2.0,
    b_switch: float = 8.0,
    prior_mu_sd: float = 3.0,
    prior_sigma_sd: float = 1.0,
    ordered: bool = True,
    draws: int = 500,
    tune: int = 1000,
    chains: int = 2,
    seed: int = 14,
    target_accept: float = 0.9,
    **kw,
) -> az.InferenceData:
    """Sample the posterior with NUTS. (No observed RV, so no PPC here; the
    forward Potential is the likelihood.)"""
    with build_model(
        data,
        a_switch=a_switch,
        b_switch=b_switch,
        prior_mu_sd=prior_mu_sd,
        prior_sigma_sd=prior_sigma_sd,
        ordered=ordered,
    ):
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            random_seed=seed,
            target_accept=target_accept,
            progressbar=False,
            **kw,
        )
        # NOTE: the likelihood lives in a pm.Potential (forward algorithm), so
        # there is no observed RV to do standard prior/posterior predictive on.
        # We sample the *parameter* prior for prior-predictive-style checks.
        idata.extend(pm.sample_prior_predictive(draws=400, random_seed=seed,
                                                var_names=["p01", "p10", "mu", "sigma"]))
    return idata


def add_named(idata: az.InferenceData) -> az.InferenceData:
    """Expose ordered emission means as named scalars for recovery checks."""
    mu = idata.posterior["mu"]
    idata.posterior["mu_low"] = mu.isel(mu_dim_0=0)
    idata.posterior["mu_high"] = mu.isel(mu_dim_0=1)
    return idata


if __name__ == "__main__":
    from data.generate_data import generate

    d = generate()
    idata = fit(d, draws=500, tune=1000, chains=2)
    add_named(idata)
    print(az.summary(idata, var_names=["p01", "p10", "mu", "sigma", "separation"]))
    print("divergences:", int(idata.sample_stats["diverging"].sum()))
    t = d["truth"]
    print(f"truth: p01={t['p01']}, p10={t['p10']}, mu=({t['mu[0]']},{t['mu[1]']}), "
          f"sigma={t['sigma']}")
