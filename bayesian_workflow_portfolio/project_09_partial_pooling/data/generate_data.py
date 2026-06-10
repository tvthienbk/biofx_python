"""Data-generating process for Project 09 — partial pooling (hierarchical means).

Scenario: a continuous quantity (say a normalized assay readout) is measured on
``J`` plates/labs/batches. Each group ``j`` has its own latent mean ``theta_j``,
but the groups are *exchangeable*: their means are drawn from a common population
distribution ``Normal(mu, tau)``. Crucially each group has only a *few*
observations, so a per-group ("no pooling") estimate is noisy, while a single
grand mean ("complete pooling") ignores real group-to-group variation. Partial
pooling is the principled middle ground.

Data-generating model::

    theta_j ~ Normal(mu_true, tau_true)        # group means
    y_ij    ~ Normal(theta_j, sigma_true)      # observations within a group

We deliberately make ``tau_true`` modest and ``n_j`` small so that shrinkage is
visible and so the *centered* parameterization will struggle (the funnel).

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

MU_TRUE = 5.0       # grand mean of the population of group means
TAU_TRUE = 0.8      # between-group SD (modest -> shrinkage matters)
SIGMA_TRUE = 1.0    # within-group observation noise
J_GROUPS = 12       # number of plates/labs/batches
N_PER = 4           # observations per group (few!)
SEED = 20240601


def generate(
    seed: int = SEED,
    J: int = J_GROUPS,
    n_per: int = N_PER,
    mu: float = MU_TRUE,
    tau: float = TAU_TRUE,
    sigma: float = SIGMA_TRUE,
) -> dict:
    """Simulate a hierarchical Normal dataset with known truth.

    Returns a dict with:
      * ``y``     : flat array of observations (length J*n_per)
      * ``group`` : integer group index per observation
      * ``J``, ``n_per``
      * ``theta`` : the true per-group means (length J)
      * ``truth`` : dict of population-level truths for recovery checks
    """
    rng = np.random.default_rng(seed)
    theta = rng.normal(mu, tau, size=J)
    group = np.repeat(np.arange(J), n_per)
    y = rng.normal(theta[group], sigma)
    return {
        "y": y.astype(float),
        "group": group.astype(int),
        "J": int(J),
        "n_per": int(n_per),
        "theta": theta.astype(float),
        "truth": {"mu": float(mu), "tau": float(tau), "sigma": float(sigma)},
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        out,
        y=data["y"],
        group=data["group"],
        J=data["J"],
        n_per=data["n_per"],
        theta=data["theta"],
        mu=data["truth"]["mu"],
        tau=data["truth"]["tau"],
        sigma=data["truth"]["sigma"],
    )
    return data


if __name__ == "__main__":
    d = save()
    print(f"Synthesized {d['J']} groups x {d['n_per']} obs = {len(d['y'])} observations.")
    print(f"True mu={d['truth']['mu']}, tau={d['truth']['tau']}, sigma={d['truth']['sigma']}")
    print(f"Group means (theta) range: [{d['theta'].min():.2f}, {d['theta'].max():.2f}]")
