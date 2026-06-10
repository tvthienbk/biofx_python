"""Probabilistic PCA (factor model) for Project 15, decoupled from the notebook.

Model:
    z_n ~ Normal(0, I_K)
    x_n ~ Normal(W z_n + mu, sigma^2 I_D)

Priors:
    W     ~ Normal(0, w_scale)   (D x K loading matrix)
    mu    ~ Normal(0, 1)         (per-dim offset)
    sigma ~ HalfNormal(1)        (isotropic noise sd)

**Non-identifiability, on purpose.** W and z are identified only up to an
orthogonal rotation/sign (W -> W R). Raw loadings therefore have huge R-hat and
must NOT be interpreted directly. We expose the **rotation-invariant** quantities
that ARE identified:

  * sigma (the noise level),
  * the reconstructed covariance C = W Wᵀ + sigma^2 I (and its trace / diagonal),

via ``reconstructed_cov`` / ``add_identifiable``. Recovery tests target those.

Exposes ``build_model`` and ``fit`` for the notebook, tests, SBC, and prior-
sensitivity scripts.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm


def build_model(
    data: dict,
    K: int | None = None,
    w_scale: float = 1.0,
    prior_mu_sd: float = 1.0,
    prior_sigma_sd: float = 1.0,
) -> pm.Model:
    """Construct the probabilistic-PCA model.

    ``K`` defaults to the true latent dimension in ``data['K']``. Pass a larger
    ``K`` to reproduce the over-specification pathology (broken notebook).
    """
    X = np.asarray(data["X"], dtype=float)
    N, D = X.shape
    if K is None:
        K = int(data["K"])
    with pm.Model() as model:
        W = pm.Normal("W", 0.0, w_scale, shape=(D, K))
        mu = pm.Normal("mu", 0.0, prior_mu_sd, shape=D)
        sigma = pm.HalfNormal("sigma", prior_sigma_sd)
        z = pm.Normal("z", 0.0, 1.0, shape=(N, K))
        pm.Normal("X", mu=pm.math.dot(z, W.T) + mu, sigma=sigma, observed=X)
    return model


def fit(
    data: dict,
    K: int | None = None,
    w_scale: float = 1.0,
    prior_mu_sd: float = 1.0,
    prior_sigma_sd: float = 1.0,
    draws: int = 500,
    tune: int = 1000,
    chains: int = 2,
    seed: int = 15,
    target_accept: float = 0.9,
    **kw,
) -> az.InferenceData:
    """Sample the posterior with NUTS and attach prior/posterior predictive."""
    with build_model(
        data,
        K=K,
        w_scale=w_scale,
        prior_mu_sd=prior_mu_sd,
        prior_sigma_sd=prior_sigma_sd,
    ):
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            random_seed=seed,
            target_accept=target_accept,
            progressbar=False,
            idata_kwargs={"log_likelihood": True},
            **kw,
        )
        idata.extend(pm.sample_prior_predictive(draws=200, random_seed=seed))
        idata.extend(
            pm.sample_posterior_predictive(idata, random_seed=seed, progressbar=False)
        )
    return idata


def reconstructed_cov(idata: az.InferenceData) -> np.ndarray:
    """Posterior-mean reconstructed covariance C = E[W Wᵀ + sigma^2 I].

    This is rotation-invariant and therefore identified, unlike W itself.
    """
    W = idata.posterior["W"].stack(s=("chain", "draw")).values  # (D, K, S)
    sig = idata.posterior["sigma"].stack(s=("chain", "draw")).values  # (S,)
    D = W.shape[0]
    WWt = np.einsum("dks,eks->des", W, W)  # (D, D, S)
    C = WWt.mean(axis=-1) + (sig ** 2).mean() * np.eye(D)
    return C


def add_identifiable(idata: az.InferenceData) -> az.InferenceData:
    """Attach the identifiable scalar ``total_var`` = trace(W Wᵀ) + D sigma^2."""
    W = idata.posterior["W"]
    # trace(W Wᵀ) = sum of squared loadings (rotation-invariant)
    sumsq = (W ** 2).sum(dim=("W_dim_0", "W_dim_1"))
    D = W.sizes["W_dim_0"]
    idata.posterior["total_var"] = sumsq + D * idata.posterior["sigma"] ** 2
    return idata


if __name__ == "__main__":
    from data.generate_data import generate

    d = generate()
    idata = fit(d, draws=500, tune=1000, chains=2)
    add_identifiable(idata)
    print(az.summary(idata, var_names=["sigma", "total_var"]))
    C_hat = reconstructed_cov(idata)
    err = np.linalg.norm(C_hat - d["C_true"])
    print(f"reconstructed-cov Frobenius error = {err:.3f}")
    print(f"true total_var = {d['truth']['total_var']:.3f}")
    print("divergences:", int(idata.sample_stats["diverging"].sum()))
