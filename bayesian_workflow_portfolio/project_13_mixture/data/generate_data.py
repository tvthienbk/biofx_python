"""Data-generating process for Project 13 — a two-component mixture.

Scenario: a biophysical readout (e.g. single-molecule FRET efficiency, or a SAXS
order parameter) reports a signal that comes from **two conformational states**.
Each molecule is, at the moment of measurement, in state 0 ("low") or state 1
("high"). The two states emit Gaussian-distributed signals with different means
but (for simplicity) a shared spread. We observe only the pooled, *unlabelled*
signal — we never see which state produced each point. The histogram is bimodal.

This is the canonical *finite mixture* problem. The new modelling skill is the
**latent component membership**: each observation secretly belongs to a component
and we must infer both the per-component parameters and the mixing weights.

Known truth (recoverable up to the label-symmetry we will deliberately break):

  * weights        w      = (0.35, 0.65)
  * component means mu     = (-2.0, 1.5)
  * shared spread  sigma   = 0.7
  * separation     mu1-mu0 = 3.5   (an identifiable, label-invariant quantity)

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

W_TRUE = np.array([0.35, 0.65])   # mixing weights (must sum to 1)
MU_TRUE = np.array([-2.0, 1.5])   # component means, sorted ascending
SD_TRUE = 0.7                     # shared component standard deviation
N_OBS = 300                       # number of measured molecules
SEED = 20240601


def generate(
    seed: int = SEED,
    n: int = N_OBS,
    w=W_TRUE,
    mu=MU_TRUE,
    sd: float = SD_TRUE,
) -> dict:
    """Simulate ``n`` draws from a 2-component Gaussian mixture.

    Returns a dict with the observed signal ``y``, the (hidden) component labels
    ``z`` for didactic plots, and a ``truth`` dict of recoverable parameters.
    The ``truth`` dict reports both raw per-component params and the
    label-invariant ``separation`` and ``w_high`` (weight of the higher mean),
    which are the quantities recovery tests should target.
    """
    rng = np.random.default_rng(seed)
    w = np.asarray(w, dtype=float)
    mu = np.asarray(mu, dtype=float)
    z = rng.choice(len(w), size=n, p=w)          # latent membership (hidden!)
    y = rng.normal(mu[z], sd)                     # observed pooled signal
    order = np.argsort(mu)                        # ensure mu sorted ascending
    mu_sorted = mu[order]
    w_sorted = w[order]
    return {
        "y": y.astype(float),
        "z": z.astype(int),
        "truth": {
            "mu[0]": float(mu_sorted[0]),
            "mu[1]": float(mu_sorted[1]),
            "sigma": float(sd),
            "w[1]": float(w_sorted[1]),          # weight of the *higher* mean
            "separation": float(mu_sorted[1] - mu_sorted[0]),
        },
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, y=data["y"], z=data["z"])
    return data


if __name__ == "__main__":
    d = save()
    y = d["y"]
    print(f"Synthesized {len(y)} signal measurements from a 2-state mixture.")
    print(f"  empirical mean={y.mean():.3f}, sd={y.std():.3f}, "
          f"range=[{y.min():.2f}, {y.max():.2f}]")
    t = d["truth"]
    print(f"True (sorted) means = ({t['mu[0]']:.2f}, {t['mu[1]']:.2f}), "
          f"sigma={t['sigma']:.2f}, w_high={t['w[1]']:.2f}, "
          f"separation={t['separation']:.2f}")
