"""Data-generating process for Project 14 — a 2-state Hidden Markov Model.

Scenario: an ion channel (or an MD trajectory) switches between a **closed** and
an **open** state over time. The hidden state *persists* — once open it tends to
stay open for a while — so successive observations are correlated through the
latent state. We record a noisy scalar emission at each time step (e.g. a current
or a collective variable) but never observe the state itself.

Generative model:

    s_1 ~ Categorical(pi)                       # initial state (0=closed,1=open)
    s_t | s_{t-1} ~ Categorical(P[s_{t-1}, :])  # Markov transition
    y_t | s_t     ~ Normal(mu[s_t], sigma)      # noisy emission

with a 2x2 transition matrix parameterized by the two *switch* probabilities:

    P = [[1 - p01,   p01  ],
         [  p10  , 1 - p10 ]]

Known truth (recoverable up to the state-label symmetry we break with ordering):

  * p01 (closed->open) = 0.08      # rare switches => long dwell times
  * p10 (open->closed) = 0.15
  * emission means mu  = (-1.5, 1.5)   (sorted ascending)
  * shared sigma       = 0.6
  * length T           = 250

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

P01_TRUE = 0.08    # closed -> open
P10_TRUE = 0.15    # open -> closed
MU_TRUE = np.array([-1.5, 1.5])  # emission means, sorted ascending
SIGMA_TRUE = 0.6
T_LEN = 250
SEED = 20240601


def generate(
    seed: int = SEED,
    T: int = T_LEN,
    p01: float = P01_TRUE,
    p10: float = P10_TRUE,
    mu=MU_TRUE,
    sigma: float = SIGMA_TRUE,
) -> dict:
    """Simulate a 2-state Gaussian-emission HMM trajectory of length ``T``.

    Returns a dict with the observed emissions ``y``, the hidden state path
    ``states`` (for didactic plots), and a ``truth`` dict of recoverable
    parameters.
    """
    rng = np.random.default_rng(seed)
    mu = np.asarray(mu, dtype=float)
    P = np.array([[1 - p01, p01], [p10, 1 - p10]])
    states = np.zeros(T, dtype=int)
    states[0] = rng.choice(2, p=[0.5, 0.5])
    for t in range(1, T):
        states[t] = rng.choice(2, p=P[states[t - 1]])
    y = rng.normal(mu[states], sigma)
    return {
        "y": y.astype(float),
        "states": states.astype(int),
        "truth": {
            "p01": float(p01),
            "p10": float(p10),
            "mu[0]": float(mu[0]),
            "mu[1]": float(mu[1]),
            "sigma": float(sigma),
            "separation": float(mu[1] - mu[0]),
        },
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, y=data["y"], states=data["states"])
    return data


if __name__ == "__main__":
    d = save()
    y, s = d["y"], d["states"]
    frac_open = float((s == 1).mean())
    print(f"Synthesized T={len(y)} time steps; fraction in 'open' state = {frac_open:.2f}")
    print(f"  emission mean={y.mean():.3f}, sd={y.std():.3f}")
    t = d["truth"]
    print(f"True p01={t['p01']:.3f}, p10={t['p10']:.3f}, "
          f"mu=({t['mu[0]']:.2f},{t['mu[1]']:.2f}), sigma={t['sigma']:.2f}, "
          f"separation={t['separation']:.2f}")
