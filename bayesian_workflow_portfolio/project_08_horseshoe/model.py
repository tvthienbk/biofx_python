"""Regularized regression models for Project 08 — horseshoe vs wide-Normal ridge.

We expose BOTH models so the notebook can fit each and compare with LOO:

  horseshoe  a regularized (finite) horseshoe prior on the coefficients,
             NON-CENTERED to avoid the funnel divergences that the centered
             parameterization causes.
  ridge      a wide Normal(0, ridge_sd) prior on every coefficient ('flat'/ridge),
             with no sparsity-inducing structure.

Both share y = beta0 + X @ beta + Normal(0, sigma).

The horseshoe prior factorizes each coefficient's scale into a GLOBAL scale tau
(how many coefficients survive) and a LOCAL scale lambda_j (per-coefficient).
The local scale has very heavy (half-Cauchy) tails, so a coefficient is either
shrunk hard toward zero (most of them) or allowed to escape shrinkage (the few
real ones) — exactly the sparse behavior we want. The 'regularized' (Piironen &
Vehtari) variant additionally caps how large the escaping coefficients can get
via a slab scale c, which stabilizes sampling.

Non-centered parameterization: we sample standardized z_j ~ Normal(0,1) and form
beta_j = z_j * tau * lambda_tilde_j, so the geometry NUTS sees is decoupled from
the scales. The centered version (beta_j ~ Normal(0, tau*lambda_j) directly)
creates a pinched funnel and floods the run with divergences (the seeded bug in
notebook_broken.ipynb).

Exposes ``build_model(data, model=...)`` and ``fit(data, model=..., ...)``.
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm


def build_model(
    data: dict,
    model: str = "horseshoe",
    tau0: float = 0.1,
    slab_scale: float = 2.0,
    slab_df: float = 4.0,
    ridge_sd: float = 5.0,
    centered: bool = False,
) -> pm.Model:
    """Construct a horseshoe or wide-Normal ridge linear regression.

    ``tau0`` sets the global-scale prior (smaller => more aggressive sparsity).
    ``centered=True`` builds the pathological centered horseshoe (for the bug demo).
    """
    X = np.asarray(data["X"], dtype=float)
    y = np.asarray(data["y"], dtype=float)
    n, p = X.shape
    if model not in ("horseshoe", "ridge"):
        raise ValueError("model must be 'horseshoe' or 'ridge'")
    with pm.Model() as m:
        X_data = pm.Data("X", X)
        beta0 = pm.Normal("beta0", 0.0, 5.0)
        sigma = pm.HalfNormal("sigma", 5.0)
        if model == "ridge":
            beta = pm.Normal("beta", 0.0, ridge_sd, shape=p)
        else:
            # Regularized horseshoe (Piironen & Vehtari 2017).
            tau = pm.HalfCauchy("tau", beta=tau0)                 # global scale
            lam = pm.HalfCauchy("lam", beta=1.0, shape=p)         # local scales
            c2 = pm.InverseGamma("c2", alpha=slab_df / 2.0,
                                 beta=slab_df / 2.0 * slab_scale ** 2)  # slab
            lam_tilde = lam * pm.math.sqrt(c2 / (c2 + tau ** 2 * lam ** 2))
            if centered:
                # PATHOLOGICAL: sampling beta directly through the scale funnel.
                beta = pm.Normal("beta", 0.0, tau * lam_tilde, shape=p)
            else:
                # Non-centered: standardized z, then scale up. Decouples geometry.
                z = pm.Normal("z", 0.0, 1.0, shape=p)
                beta = pm.Deterministic("beta", z * tau * lam_tilde)
        mu = pm.Deterministic("mu", beta0 + pm.math.dot(X_data, beta))
        pm.Normal("y", mu=mu, sigma=sigma, observed=y)
    return m


def fit(
    data: dict,
    model: str = "horseshoe",
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 4,
    seed: int = 101,
    target_accept: float = 0.95,
    **kw,
) -> az.InferenceData:
    """Sample the posterior with NUTS and attach prior/posterior predictive.

    ``target_accept`` defaults high (0.95) because the horseshoe geometry, even
    non-centered, benefits from smaller steps.
    """
    build_kw = {k: kw.pop(k) for k in list(kw)
                if k in ("tau0", "slab_scale", "slab_df", "ridge_sd", "centered")}
    with build_model(data, model=model, **build_kw):
        idata = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            random_seed=seed,
            progressbar=False,
            target_accept=target_accept,
            idata_kwargs={"log_likelihood": True},
            **kw,
        )
        idata.extend(pm.sample_prior_predictive(draws=300, random_seed=seed))
        idata.extend(
            pm.sample_posterior_predictive(idata, random_seed=seed, progressbar=False)
        )
    return idata


if __name__ == "__main__":
    from data.generate_data import generate

    d = generate()
    for mdl in ("ridge", "horseshoe"):
        idata = fit(d, model=mdl, draws=500, tune=700, chains=2)
        n_div = int(idata.sample_stats["diverging"].sum())
        bmean = idata.posterior["beta"].mean(("chain", "draw")).values
        print(f"--- {mdl} (divergences={n_div}) ---")
        print("nonzero idx", d["nonzero_idx"],
              "true", [round(float(d["beta_true"][j]), 2) for j in d["nonzero_idx"]])
        print("est at those idx",
              [round(float(bmean[j]), 2) for j in d["nonzero_idx"]])
        zeros = [j for j in range(d["p"]) if j not in d["nonzero_idx"]]
        print("max |est| among true-zeros:", round(float(np.max(np.abs(bmean[zeros]))), 3))
