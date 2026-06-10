"""Data-generating process for Project 16 — a single change-point.

Scenario: a reaction-kinetics time series of *counts* (e.g. detected events per
time bin) undergoes a **regime shift** at an unknown time tau — perhaps a catalyst
is added, a channel opens, or a pathway switches on — after which the underlying
rate changes. We observe noisy counts and want to locate the shift and quantify
the before/after rates.

Generative model (coal-mining-disaster style):

    rate_t = lam0   if t <  tau
             lam1   if t >= tau
    y_t ~ Poisson(rate_t)

Index convention: ``tau`` is the index of the **first post-shift** observation, so
indices 0..tau-1 are drawn at rate lam0 and tau..T-1 at rate lam1. This matches the
model's ``switch(tau > t, lam0, lam1)``.

Known truth (recoverable):

  * tau_true  = 70     (out of T = 120)
  * lam0_true = 4.0    (pre-shift rate)
  * lam1_true = 11.0   (post-shift rate)

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

T_LEN = 120
TAU_TRUE = 70
LAM0_TRUE = 4.0
LAM1_TRUE = 11.0
SEED = 20240601


def generate(
    seed: int = SEED,
    T: int = T_LEN,
    tau: int = TAU_TRUE,
    lam0: float = LAM0_TRUE,
    lam1: float = LAM1_TRUE,
) -> dict:
    """Simulate a Poisson count series with one rate change at ``tau``.

    Returns the counts ``y`` and a ``truth`` dict for recovery checks.
    """
    rng = np.random.default_rng(seed)
    idx = np.arange(T)
    rate = np.where(idx < tau, lam0, lam1)
    y = rng.poisson(rate)
    return {
        "y": y.astype(int),
        "T": int(T),
        "truth": {
            "tau": int(tau),
            "lam0": float(lam0),
            "lam1": float(lam1),
        },
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, y=data["y"], T=data["T"])
    return data


if __name__ == "__main__":
    d = save()
    y = d["y"]
    t = d["truth"]
    print(f"Synthesized T={len(y)} count observations with a shift at tau={t['tau']}.")
    print(f"  pre-shift empirical mean  = {y[:t['tau']].mean():.2f} (true lam0={t['lam0']})")
    print(f"  post-shift empirical mean = {y[t['tau']:].mean():.2f} (true lam1={t['lam1']})")
