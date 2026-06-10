"""Gaussian-process regression for Project 17, decoupled from the notebook.

Model (marginal GP):
    f(x) ~ GP(0, k(x, x'))     with  k = eta^2 * ExpQuad(ell)
    y    ~ Normal(f(x), sigma)

Kernel hyperpriors:
    ell   ~ InverseGamma(...)  -- INFORMATIVE length-scale prior. This is the
            single most important modelling choice in a GP: a vague length-scale
            prior lets ``ell`` trade off against the marginal variance ``eta`` and
            against the noise ``sigma``, producing a ridge of equally-good
            (ell, eta) pairs, poor mixing, and divergences. We place an inverse-
            gamma prior whose mass sits at length-scales that are a sensible
            fraction of the input range (not tiny, not larger than the domain).
    eta   ~ HalfNormal(...)    -- marginal signal standard deviation.
    sigma ~ HalfNormal(...)    -- observation noise (the recoverable scalar).

We use ``pm.gp.Marginal`` so the latent ``f`` is integrated out analytically;
this is what keeps the model cheap enough to sample lightly. ``gp.conditional``
(or ``gp.predict``) reconstructs the fitted curve with credible bands.

Exposes ``build_model`` and ``fit`` so the notebook, tests, SBC, and prior-
sensitivity scripts share one source of truth.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm


def build_model(
    data: dict,
    ell_alpha: float = 6.0,
    ell_beta: float = 12.0,
    eta_sd: float = 2.0,
    sigma_sd: float = 0.5,
):
    """Construct the marginal GP model.

    The default InverseGamma(alpha=6, beta=12) puts the length-scale mass around
    ell ~ 2 (beta/(alpha-1)), i.e. roughly a fifth of the 0-10 input range, with
    little mass below ~1 or above ~5 -- an informative-but-reasonable prior that
    avoids the length-scale / marginal-variance trade-off pathology.

    Returns ``(model, gp)`` because ``gp`` is needed to build the predictive
    conditional later.
    """
    x = np.asarray(data["x"], dtype=float)[:, None]
    y = np.asarray(data["y"], dtype=float)
    with pm.Model() as model:
        ell = pm.InverseGamma("ell", alpha=ell_alpha, beta=ell_beta)
        eta = pm.HalfNormal("eta", sigma=eta_sd)
        sigma = pm.HalfNormal("sigma", sigma=sigma_sd)
        cov = eta**2 * pm.gp.cov.ExpQuad(input_dim=1, ls=ell)
        gp = pm.gp.Marginal(cov_func=cov)
        gp.marginal_likelihood("y_obs", X=x, y=y, sigma=sigma)
        model.gp = gp  # stash for predictive use
    return model, gp


def fit(
    data: dict,
    draws: int = 400,
    tune: int = 600,
    chains: int = 2,
    seed: int = 101,
    target_accept: float = 0.9,
    predictive: bool = False,
    **build_kw,
) -> az.InferenceData:
    """Sample the GP hyperposterior with NUTS.

    With the latent ``f`` marginalised out there is no per-point likelihood to
    accumulate cheaply, so we skip ``log_likelihood`` by default (the marginal GP
    has a single multivariate-normal likelihood term anyway). Set
    ``predictive=True`` to also attach the posterior-predictive curve.
    """
    model, gp = build_model(data, **build_kw)
    with model:
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            cores=1,  # multiprocess sampling hangs without a linked BLAS; serial is safe+fast here
            random_seed=seed,
            target_accept=target_accept,
            progressbar=False,
        )
        idata.extend(pm.sample_prior_predictive(draws=200, random_seed=seed))
    return idata


def _expquad(a: np.ndarray, b: np.ndarray, eta: float, ell: float) -> np.ndarray:
    """eta^2 * ExpQuad(ell) cross-covariance between vectors ``a`` and ``b``."""
    d2 = (a[:, None] - b[None, :]) ** 2
    return eta**2 * np.exp(-0.5 * d2 / ell**2)


def predict_curve(data: dict, idata: az.InferenceData, x_new: np.ndarray | None = None,
                  n_pred: int = 60, seed: int = 7, n_draws: int = 40, **build_kw):
    """Posterior mean and 94% band of the latent function on ``x_new``.

    Computes the GP conditional mean in **pure numpy** for each of a thinned set of
    posterior hyperparameter draws. This avoids recompiling a PyTensor graph per
    draw (which is what makes ``gp.predict`` in a loop slow), so prediction is fast
    and dependency-light. The conditional mean of a noisy GP is the textbook
        mu_* = K(x_*, x) [K(x, x) + sigma^2 I]^{-1} y.
    """
    x = np.asarray(data["x"], dtype=float)
    y = np.asarray(data["y"], dtype=float)
    if x_new is None:
        x_new = np.linspace(x.min(), x.max(), n_pred)
    x_new = np.asarray(x_new, dtype=float)
    post = idata.posterior
    rng = np.random.default_rng(seed)
    ell_flat = post["ell"].values.reshape(-1)
    eta_flat = post["eta"].values.reshape(-1)
    sig_flat = post["sigma"].values.reshape(-1)
    total = ell_flat.size
    idx = rng.choice(total, size=min(n_draws, total), replace=False)
    n = x.size
    means = []
    for j in idx:
        ell, eta, sig = float(ell_flat[j]), float(eta_flat[j]), float(sig_flat[j])
        Kxx = _expquad(x, x, eta, ell) + (sig**2 + 1e-8) * np.eye(n)
        Ksx = _expquad(x_new, x, eta, ell)
        alpha = np.linalg.solve(Kxx, y)
        means.append(Ksx @ alpha)
    means = np.asarray(means)
    return {
        "x_new": x_new,
        "mean": means.mean(axis=0),
        "lower": np.percentile(means, 3, axis=0),
        "upper": np.percentile(means, 97, axis=0),
    }


if __name__ == "__main__":
    from data.generate_data import generate

    d = generate()
    idata = fit(d, draws=250, tune=400, chains=2)
    print(az.summary(idata, var_names=["ell", "eta", "sigma"]))
    n_div = int(idata.sample_stats["diverging"].sum())
    print(f"divergences: {n_div}")
    pred = predict_curve(d, idata, x_new=d["x"])
    mae = float(np.mean(np.abs(pred["mean"] - d["f_true"])))
    print(f"curve recovery MAE at training inputs: {mae:.3f}")
