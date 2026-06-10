"""Data-generating process for Project 11 — varying slopes (correlated random effects).

Scenario: a dose-response experiment. A continuous readout ``y`` responds to a
standardized dose ``x``, but BOTH the baseline (intercept) AND the dose
sensitivity (slope) vary by **cell line**. Crucially the intercept and slope are
*correlated* across cell lines: lines with a higher baseline also tend to respond
more steeply to dose (a positive correlation here). Ignoring that correlation
mis-fits the data — the central teaching point of this project.

Data-generating model (per cell line g)::

    [alpha_g, beta_g] ~ MVNormal([mu_a, mu_b], Sigma)
    Sigma = diag(sd) @ Corr @ diag(sd),   Corr = [[1, rho],[rho, 1]]
    y_ij = alpha_g + beta_g * x_ij + Normal(0, sigma)

We keep cell lines few (G≈8) and observations per line modest so the correlated
structure is learnable but not trivially so.

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

MU_A_TRUE = 2.0     # population-mean intercept
MU_B_TRUE = 1.0     # population-mean slope (dose effect)
SD_A_TRUE = 0.8     # SD of intercepts across cell lines
SD_B_TRUE = 0.5     # SD of slopes across cell lines
RHO_TRUE = 0.6      # intercept-slope correlation (the quantity to recover)
SIGMA_TRUE = 0.5    # within-line observation noise
G_GROUPS = 8        # number of cell lines
N_PER = 10          # observations per cell line
SEED = 20240601


def generate(
    seed: int = SEED,
    G: int = G_GROUPS,
    n_per: int = N_PER,
    mu_a: float = MU_A_TRUE,
    mu_b: float = MU_B_TRUE,
    sd_a: float = SD_A_TRUE,
    sd_b: float = SD_B_TRUE,
    rho: float = RHO_TRUE,
    sigma: float = SIGMA_TRUE,
) -> dict:
    """Simulate a varying-slopes dataset with correlated random effects."""
    rng = np.random.default_rng(seed)
    sd = np.array([sd_a, sd_b])
    corr = np.array([[1.0, rho], [rho, 1.0]])
    cov = np.outer(sd, sd) * corr
    effects = rng.multivariate_normal([mu_a, mu_b], cov, size=G)  # (G, 2)
    alpha = effects[:, 0]
    beta = effects[:, 1]

    group = np.repeat(np.arange(G), n_per)
    x = rng.normal(0.0, 1.0, size=G * n_per)
    mu_y = alpha[group] + beta[group] * x
    y = rng.normal(mu_y, sigma)
    return {
        "y": y.astype(float),
        "x": x.astype(float),
        "group": group.astype(int),
        "G": int(G),
        "n_per": int(n_per),
        "alpha": alpha.astype(float),
        "beta": beta.astype(float),
        "truth": {
            "mu_a": float(mu_a),
            "mu_b": float(mu_b),
            "sd_a": float(sd_a),
            "sd_b": float(sd_b),
            "rho": float(rho),
            "sigma": float(sigma),
        },
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        out,
        y=data["y"], x=data["x"], group=data["group"],
        G=data["G"], n_per=data["n_per"],
        alpha=data["alpha"], beta=data["beta"],
        **{k: v for k, v in data["truth"].items()},
    )
    return data


if __name__ == "__main__":
    d = save()
    print(f"Synthesized {d['G']} cell lines x {d['n_per']} obs = {len(d['y'])} observations.")
    t = d["truth"]
    print(f"True mu_a={t['mu_a']}, mu_b={t['mu_b']}, sd_a={t['sd_a']}, "
          f"sd_b={t['sd_b']}, rho={t['rho']}, sigma={t['sigma']}")
    emp_rho = np.corrcoef(d["alpha"], d["beta"])[0, 1]
    print(f"Empirical intercept-slope corr across the {d['G']} lines: {emp_rho:.2f}")
