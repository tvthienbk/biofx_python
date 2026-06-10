"""Mechanistic 1-compartment PK model for Project 19, decoupled from the notebook.

The mechanism is the ODE  dC/dt = -k C,  C(0) = D/V,  whose closed form is
    C(t) = (D / V) * exp(-k t).

We provide TWO model builders:

1. ``build_model`` / ``fit`` — the **analytic-solution** model. We plug the closed
   form directly into the likelihood. This is exact and fast, and is what the
   tests / SBC / prior-sensitivity use. (See the README's compute note: a generic
   ODE solver inside the sampler is far slower; for a system with a closed form,
   using it is both correct and the responsible choice.)

2. ``build_ode_model`` / ``fit_ode`` — the **`pymc.ode.DifferentialEquation`**
   model. Same model, but the concentration is obtained by numerically integrating
   the ODE. This demonstrates the genuine ODE-inference workflow. It is much slower
   (a solver call with sensitivities at every leapfrog step), so we keep it
   optional and tiny.

Parameterisation note (identifiability): we sample ``k`` and ``V`` on the log
scale with LogNormal priors. The pitfall is the **practical non-identifiability**
of (k, V): early times constrain C0 = D/V (hence V); the decay slope constrains k.
If the data lack early points, V and k correlate (the PK analogue of the
Michaelis-Menten Vmax/Km correlation), which we expose in the broken notebook.

Recoverable parameters: ``k``, ``V`` (and ``sigma``).
"""
from __future__ import annotations

import arviz as az
import numpy as np
import pymc as pm
import pytensor.tensor as pt


def build_model(data: dict,
                k_mu: float = -1.0, k_sd: float = 0.7,
                V_mu: float = 2.0, V_sd: float = 0.5,
                sigma_sd: float = 1.0) -> pm.Model:
    """Analytic 1-compartment model: C(t) = (D/V) exp(-k t).

    Priors (log scale, informative-ish):
      log k ~ Normal(k_mu=-1.0, 0.7)   -> k around exp(-1) ~ 0.37 /h
      log V ~ Normal(V_mu=2.0, 0.5)    -> V around exp(2) ~ 7.4 L
      sigma ~ HalfNormal(1.0)
    """
    t = np.asarray(data["t"], dtype=float)
    y = np.asarray(data["y"], dtype=float)
    dose = float(data["dose"])
    with pm.Model() as model:
        log_k = pm.Normal("log_k", mu=k_mu, sigma=k_sd)
        log_V = pm.Normal("log_V", mu=V_mu, sigma=V_sd)
        k = pm.Deterministic("k", pt.exp(log_k))
        V = pm.Deterministic("V", pt.exp(log_V))
        sigma = pm.HalfNormal("sigma", sigma=sigma_sd)
        C = (dose / V) * pt.exp(-k * t)
        pm.Normal("y_obs", mu=C, sigma=sigma, observed=y)
    return model


def fit(data: dict, draws: int = 600, tune: int = 1000, chains: int = 2,
        seed: int = 101, target_accept: float = 0.9, **build_kw) -> az.InferenceData:
    """Sample the analytic PK model with NUTS; attach prior + posterior predictive."""
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


def build_ode_model(data: dict,
                    k_mu: float = -1.0, k_sd: float = 0.7,
                    V_mu: float = 2.0, V_sd: float = 0.5,
                    sigma_sd: float = 1.0) -> pm.Model:
    """Same model via ``pymc.ode.DifferentialEquation`` (numerical integration).

    Demonstrates the genuine ODE-inference workflow. SLOW: keep draws tiny.
    """
    from pymc.ode import DifferentialEquation
    from scipy.integrate import odeint  # noqa: F401  (DifferentialEquation uses it)

    t = np.asarray(data["t"], dtype=float)
    y = np.asarray(data["y"], dtype=float)
    dose = float(data["dose"])

    def rhs(C, time, theta):
        k = theta[0]
        return -k * C[0]

    ode = DifferentialEquation(func=rhs, times=t, n_states=1, n_theta=1, t0=0.0)
    with pm.Model() as model:
        log_k = pm.Normal("log_k", mu=k_mu, sigma=k_sd)
        log_V = pm.Normal("log_V", mu=V_mu, sigma=V_sd)
        k = pm.Deterministic("k", pt.exp(log_k))
        V = pm.Deterministic("V", pt.exp(log_V))
        sigma = pm.HalfNormal("sigma", sigma=sigma_sd)
        C0 = dose / V
        sol = ode(y0=[C0], theta=[k])          # shape (len(t), 1)
        pm.Normal("y_obs", mu=sol[:, 0], sigma=sigma, observed=y)
    return model


def fit_ode(data: dict, draws: int = 150, tune: int = 300, chains: int = 2,
            seed: int = 101, target_accept: float = 0.9, **build_kw) -> az.InferenceData:
    """Sample the DifferentialEquation model. SLOW — tiny defaults on purpose."""
    with build_ode_model(data, **build_kw):
        idata = pm.sample(
            draws=draws, tune=tune, chains=chains, cores=1,
            random_seed=seed, target_accept=target_accept, progressbar=False,
        )
    return idata


if __name__ == "__main__":
    from data.generate_data import generate

    d = generate()
    idata = fit(d, draws=400, tune=800, chains=2)
    print(az.summary(idata, var_names=["k", "V", "sigma"]))
    n_div = int(idata.sample_stats["diverging"].sum())
    print(f"divergences: {n_div}")
    print(f"truth: k={d['truth']['k']}, V={d['truth']['V']}, sigma={d['truth']['sigma']}")
