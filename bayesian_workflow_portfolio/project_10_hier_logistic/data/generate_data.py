"""Data-generating process for Project 10 — varying intercepts (hierarchical logistic).

Scenario: a binary binding assay ("does protein bind ligand?") is run across many
protein *families*. Each family ``g`` has its own baseline binding propensity,
expressed as a group-varying intercept on the log-odds scale. Families are
exchangeable: their intercepts are drawn from a common population
``Normal(mu, tau)``. A single global covariate (a standardized physicochemical
score) shifts the log-odds for every observation.

Data-generating model::

    alpha_g ~ Normal(mu_true, tau_true)              # family intercepts (log-odds)
    logit(p_i) = alpha_{g[i]} + beta_true * x_i      # linear predictor
    y_i ~ Bernoulli(p_i)

We use a modest number of families with *few* observations each so that
group-level structure matters and over-aggressive pooling is a real risk.

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

MU_TRUE = -0.3      # population-mean intercept (log-odds): slightly below 50/50
TAU_TRUE = 0.9      # between-family SD of intercepts (real, moderate variation)
BETA_TRUE = 1.2     # global covariate effect (log-odds per unit x)
G_GROUPS = 10       # number of protein families
N_PER = 12          # observations per family (few-ish)
SEED = 20240601


def generate(
    seed: int = SEED,
    G: int = G_GROUPS,
    n_per: int = N_PER,
    mu: float = MU_TRUE,
    tau: float = TAU_TRUE,
    beta: float = BETA_TRUE,
) -> dict:
    """Simulate a hierarchical logistic dataset with known truth.

    Returns a dict with:
      * ``y``     : 0/1 outcomes (length G*n_per)
      * ``x``     : standardized covariate per observation
      * ``group`` : integer family index per observation
      * ``G``, ``n_per``
      * ``alpha`` : the true per-family intercepts (length G)
      * ``truth`` : dict of population-level truths for recovery checks
    """
    rng = np.random.default_rng(seed)
    alpha = rng.normal(mu, tau, size=G)
    group = np.repeat(np.arange(G), n_per)
    x = rng.normal(0.0, 1.0, size=G * n_per)
    eta = alpha[group] + beta * x
    p = 1.0 / (1.0 + np.exp(-eta))
    y = rng.binomial(1, p)
    return {
        "y": y.astype(int),
        "x": x.astype(float),
        "group": group.astype(int),
        "G": int(G),
        "n_per": int(n_per),
        "alpha": alpha.astype(float),
        "truth": {"mu": float(mu), "tau": float(tau), "beta": float(beta)},
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        out,
        y=data["y"],
        x=data["x"],
        group=data["group"],
        G=data["G"],
        n_per=data["n_per"],
        alpha=data["alpha"],
        mu=data["truth"]["mu"],
        tau=data["truth"]["tau"],
        beta=data["truth"]["beta"],
    )
    return data


if __name__ == "__main__":
    d = save()
    print(f"Synthesized {d['G']} families x {d['n_per']} obs = {len(d['y'])} observations.")
    print(f"True mu={d['truth']['mu']}, tau={d['truth']['tau']}, beta={d['truth']['beta']}")
    rates = [d["y"][d["group"] == g].mean() for g in range(d["G"])]
    print("per-family empirical binding rates:", np.round(rates, 2))
