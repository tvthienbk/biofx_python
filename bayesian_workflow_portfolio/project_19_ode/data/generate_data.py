"""Data-generating process for Project 19 — mechanistic 1-compartment PK model.

Scenario: a drug is given as a single IV bolus dose ``D`` at time 0 into a single
well-mixed compartment of volume ``V``. The drug is eliminated by a first-order
process with rate constant ``k``. The concentration obeys the ODE

    dC/dt = -k * C,      C(0) = D / V

whose closed-form solution is

    C(t) = (D / V) * exp(-k * t).

We observe noisy concentrations at a handful of timepoints. The recoverable rate
constants are ``k`` (elimination rate) and ``V`` (volume of distribution); the
clearance is CL = k * V.

THE pitfall: practical non-identifiability. If all sampling times lie on the
roughly log-linear decay (the "linear regime" of the log-concentration), the data
constrain the *product / ratio* structure better than each parameter alone —
analogous to the Vmax/Km correlation in Michaelis-Menten. We therefore include
*early* timepoints (where C ~ D/V pins down V) and *later* ones (where the slope
pins down k); the broken notebook deliberately drops the early points to expose
the V <-> k confounding.

We provide BOTH the analytic solution (used by the fast model) and the ODE itself,
and the README explains the compute trade-off.

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

DOSE = 100.0          # mg, single IV bolus (known)
K_TRUE = 0.35         # 1/h elimination rate constant (recoverable)
V_TRUE = 8.0          # L volume of distribution (recoverable)
SIGMA_TRUE = 0.4      # mg/L observation noise sd
# timepoints (h): early points pin down C0 = D/V; later points pin down slope k
TIMES = np.array([0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0, 8.0, 10.0])
SEED = 20240601


def analytic_C(t, k=K_TRUE, V=V_TRUE, dose=DOSE):
    """Closed-form 1-compartment IV-bolus concentration C(t) = (D/V) exp(-k t)."""
    t = np.asarray(t, dtype=float)
    return (dose / V) * np.exp(-k * t)


def generate(seed: int = SEED, k: float = K_TRUE, V: float = V_TRUE,
             sigma: float = SIGMA_TRUE, times: np.ndarray = TIMES,
             dose: float = DOSE) -> dict:
    """Simulate noisy concentrations at the given timepoints."""
    rng = np.random.default_rng(seed)
    t = np.asarray(times, dtype=float)
    C = analytic_C(t, k=k, V=V, dose=dose)
    y = C + rng.normal(0.0, sigma, size=t.size)
    y = np.clip(y, 1e-3, None)  # concentrations are non-negative
    return {
        "t": t,
        "y": y,
        "C_true": C,
        "dose": float(dose),
        "n": int(t.size),
        "truth": {"k": float(k), "V": float(V), "sigma": float(sigma)},
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, t=data["t"], y=data["y"], C_true=data["C_true"],
             dose=data["dose"], k=data["truth"]["k"], V=data["truth"]["V"],
             sigma=data["truth"]["sigma"])
    return data


if __name__ == "__main__":
    d = save()
    print(f"Synthesized {d['n']} noisy concentrations after a {d['dose']:.0f} mg IV bolus.")
    print(f"  times (h): {d['t']}")
    print(f"  C0 = D/V = {d['dose']/d['truth']['V']:.2f} mg/L")
    print(f"True k = {d['truth']['k']:.3f} /h, V = {d['truth']['V']:.2f} L, "
          f"sigma = {d['truth']['sigma']:.2f} mg/L  (saved to data/data.npz)")
