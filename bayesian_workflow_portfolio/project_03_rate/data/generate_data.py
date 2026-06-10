"""Data-generating process for Project 03 — estimating a rate (Poisson).

Scenario: genomics counts per unit exposure. Each sample i has an *exposure*
``e_i`` (e.g. sequencing depth in kb, or the number of opportunities for an event)
and an observed integer count ``y_i`` of events. The events occur at a common
underlying rate ``lambda`` per unit exposure, so

    y_i ~ Poisson(e_i * lambda).

The KEY PITFALL of this project is **ignoring the exposure/offset**. The exposures
VARY across samples (by design here), so a model that forgets the offset and fits
``y_i ~ Poisson(lambda)`` directly is biased. We make exposure vary precisely so
that omitting it produces a visible bias (see BROKEN_BUGS.md).

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

LOG_RATE_TRUE = -1.2   # true log rate; lambda_true = exp(-1.2) ~ 0.301 events/unit
N_SAMPLES = 50         # number of samples
EXPOSURE_LOW = 5.0     # exposures vary over a wide range so the offset matters
EXPOSURE_HIGH = 40.0
SEED = 20240603


def generate(seed: int = SEED, n: int = N_SAMPLES,
             log_rate: float = LOG_RATE_TRUE) -> dict:
    """Simulate ``n`` Poisson counts with VARYING exposures and a common rate.

    Returns a dict with counts ``y``, exposures ``exposure``, count ``n``, and the
    ``truth`` dict (log_rate) for recovery checks.
    """
    rng = np.random.default_rng(seed)
    # Varying exposures (the whole point of the project): uniform over a wide band.
    exposure = rng.uniform(EXPOSURE_LOW, EXPOSURE_HIGH, size=n)
    lam = np.exp(log_rate)                      # rate per unit exposure
    y = rng.poisson(exposure * lam).astype(int)  # expected count = exposure * rate
    return {
        "y": y,
        "exposure": exposure,
        "n": int(n),
        "truth": {"log_rate": float(log_rate)},
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, y=data["y"], exposure=data["exposure"], n=data["n"],
             log_rate=data["truth"]["log_rate"])
    return data


if __name__ == "__main__":
    d = save()
    y, e = d["y"], d["exposure"]
    naive_rate = y.sum() / d["n"]                 # WRONG: ignores exposure
    correct_rate = y.sum() / e.sum()              # right: total events / total exposure
    print(f"Synthesized {d['n']} samples with exposures in "
          f"[{e.min():.1f}, {e.max():.1f}].")
    print(f"  total events = {y.sum()}, total exposure = {e.sum():.1f}")
    print(f"  naive mean count per sample (IGNORES exposure) = {naive_rate:.3f}")
    print(f"  exposure-adjusted rate (events/exposure)       = {correct_rate:.3f}")
    print(f"  true rate lambda = exp({d['truth']['log_rate']}) = "
          f"{np.exp(d['truth']['log_rate']):.3f}  -> the adjusted rate should match this")
    print(f"  true log_rate = {d['truth']['log_rate']:.3f}  (saved to data/data.npz)")
