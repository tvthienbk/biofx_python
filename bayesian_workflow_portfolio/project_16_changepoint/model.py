"""Single change-point model for Project 16, decoupled from the notebook.

Two implementations of the change time ``tau`` are provided:

(a) **Discrete tau** (``build_model``, the classic coal-mining style): a
    ``pm.DiscreteUniform`` prior on tau, with the Poisson rate switched by
    ``pm.math.switch(tau > t, lam0, lam1)``. NUTS samples the continuous rates;
    a Metropolis step updates the integer tau. This yields an explicit (possibly
    multimodal) posterior over tau.

(b) **Marginalized tau** (``marginal_tau_logp`` / ``build_marginal_model``): sum
    the likelihood over all candidate tau analytically (tau has only T-1 possible
    values), giving p(y | lam0, lam1) = sum_tau p(tau) p(y | tau, lam0, lam1).
    This removes the discrete sampler entirely and lets us read off the full
    posterior over tau by reconstructing the per-tau weights. It is the robust,
    fully-continuous-sampling alternative.

Index convention: ``tau`` is the first POST-shift index. ``switch(tau > t, ...)``
puts indices 0..tau-1 on lam0 and tau..T-1 on lam1, matching generate_data.

Priors:
    tau  ~ DiscreteUniform(1, T-1)   (any interior change time, equally likely)
    lam0 ~ Exponential(1/5)          (mean 5; weakly-informative positive rate)
    lam1 ~ Exponential(1/5)

Exposes ``build_model`` / ``fit`` (discrete) and the marginal variants.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm
import pytensor.tensor as pt


def build_model(
    data: dict,
    lam_mean: float = 5.0,
    tau_lower: int = 1,
    tau_upper: int | None = None,
) -> pm.Model:
    """Discrete-tau change-point model (switch-based)."""
    y = np.asarray(data["y"], dtype=float)
    T = len(y)
    idx = np.arange(T)
    if tau_upper is None:
        tau_upper = T - 1
    with pm.Model() as model:
        tau = pm.DiscreteUniform("tau", lower=tau_lower, upper=tau_upper)
        lam0 = pm.Exponential("lam0", 1.0 / lam_mean)
        lam1 = pm.Exponential("lam1", 1.0 / lam_mean)
        rate = pm.math.switch(tau > idx, lam0, lam1)
        pm.Poisson("y", mu=rate, observed=y)
    return model


def fit(
    data: dict,
    lam_mean: float = 5.0,
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 4,
    seed: int = 16,
    **kw,
) -> az.InferenceData:
    """Sample the discrete-tau model and attach prior/posterior predictive."""
    with build_model(data, lam_mean=lam_mean):
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            random_seed=seed,
            progressbar=False,
            idata_kwargs={"log_likelihood": True},
            **kw,
        )
        idata.extend(pm.sample_prior_predictive(draws=400, random_seed=seed))
        idata.extend(
            pm.sample_posterior_predictive(idata, random_seed=seed, progressbar=False)
        )
    return idata


def marginal_tau_logp(y, lam0, lam1, T, lam_mean):
    """Log p(y | lam0, lam1) marginalized over a uniform discrete tau in [1, T-1].

    For each candidate tau, the joint log-prob is
        log(1/(T-1)) + sum_{t<tau} Poisson.logp(y_t; lam0)
                     + sum_{t>=tau} Poisson.logp(y_t; lam1).
    We compute cumulative Poisson log-probs and logsumexp over tau.
    """
    yt = pt.as_tensor_variable(np.asarray(y, dtype="int64"))
    # per-t log Poisson under each rate, shape (T,)
    lp0 = yt * pt.log(lam0) - lam0 - pt.gammaln(yt + 1)
    lp1 = yt * pt.log(lam1) - lam1 - pt.gammaln(yt + 1)
    c0 = pt.concatenate([[0.0], pt.cumsum(lp0)])   # c0[k] = sum_{t<k} lp0
    c1_total = pt.sum(lp1)
    c1 = c1_total - pt.concatenate([[0.0], pt.cumsum(lp1)])  # c1[k] = sum_{t>=k} lp1
    taus = pt.arange(1, T)                          # candidate change indices
    joint = c0[taus] + c1[taus]                     # log lik per tau
    log_prior = -np.log(T - 1)
    return pt.logsumexp(joint + log_prior), joint


def build_marginal_model(data: dict, lam_mean: float = 5.0) -> pm.Model:
    """Continuous-sampling change-point: tau marginalized out via a Potential."""
    y = np.asarray(data["y"], dtype=float)
    T = len(y)
    with pm.Model() as model:
        lam0 = pm.Exponential("lam0", 1.0 / lam_mean)
        lam1 = pm.Exponential("lam1", 1.0 / lam_mean)
        logp, _ = marginal_tau_logp(y, lam0, lam1, T, lam_mean)
        pm.Potential("changepoint", logp)
    return model


def fit_marginal(
    data: dict,
    lam_mean: float = 5.0,
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 4,
    seed: int = 16,
    **kw,
) -> az.InferenceData:
    """Sample the marginalized model (lam0, lam1 only; tau integrated out)."""
    with build_marginal_model(data, lam_mean=lam_mean):
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            random_seed=seed,
            progressbar=False,
            **kw,
        )
    return idata


def tau_posterior_from_marginal(idata: az.InferenceData, data: dict,
                                lam_mean: float = 5.0) -> np.ndarray:
    """Reconstruct the posterior P(tau | y) by averaging the per-tau weights
    over the posterior draws of (lam0, lam1). Returns a length-(T-1) array over
    tau = 1..T-1."""
    import pytensor

    y = np.asarray(data["y"], dtype=float)
    T = len(y)
    lam0 = pt.scalar("lam0")
    lam1 = pt.scalar("lam1")
    _, joint = marginal_tau_logp(y, lam0, lam1, T, lam_mean)
    f = pytensor.function([lam0, lam1], joint)
    l0 = idata.posterior["lam0"].values.ravel()
    l1 = idata.posterior["lam1"].values.ravel()
    # subsample for speed
    n = min(400, len(l0))
    sel = np.linspace(0, len(l0) - 1, n).astype(int)
    probs = np.zeros(T - 1)
    for i in sel:
        j = f(l0[i], l1[i])
        w = np.exp(j - j.max())
        probs += w / w.sum()
    return probs / probs.sum()


if __name__ == "__main__":
    from data.generate_data import generate

    d = generate()
    print("=== discrete-tau model ===")
    idata = fit(d, draws=800, tune=1000, chains=2)
    print(az.summary(idata, var_names=["tau", "lam0", "lam1"]))
    print("=== marginalized-tau model ===")
    idm = fit_marginal(d, draws=800, tune=1000, chains=2)
    print(az.summary(idm, var_names=["lam0", "lam1"]))
    probs = tau_posterior_from_marginal(idm, d)
    print(f"marginal-model MAP tau = {np.argmax(probs) + 1} (true {d['truth']['tau']})")
