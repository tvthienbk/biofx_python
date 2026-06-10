"""Data-generating process for Project 20 — capstone: compound prioritization.

Scenario: we screen ``J`` candidate compounds in a noisy assay. Each compound ``j``
has a true effect ``theta_j`` (e.g. percent inhibition on a standardized scale).
The compounds are exchangeable draws from a population:

    theta_j ~ Normal(mu, tau)            (between-compound variation)
    y_{j,i} ~ Normal(theta_j, sigma)     (within-compound assay noise)

Crucially, the compounds are measured with **unequal replication**: some have many
replicates (well-estimated), some have very few (noisy). This is what creates the
**winner's-curse** trap — a compound with few replicates can post a high *raw* mean
by chance and look like the winner.

The decision: pick the single best compound to advance. The right answer accounts
for partial pooling (shrinking noisy estimates toward the population) and for a
cost-loss / expected-utility calculation — not the raw maximum.

Recoverable truths: the population parameters ``mu``, ``tau``, the per-compound
``theta_j``, and the identity of the TRUE best compound (largest ``theta_j``).

Run as a script to synthesize the data and print the recoverable truth.
"""
from __future__ import annotations

import pathlib

import numpy as np

J = 12                 # number of compounds
MU_TRUE = 0.0          # population mean effect (recoverable)
TAU_TRUE = 1.0         # between-compound sd (recoverable)
SIGMA_TRUE = 1.0       # within-compound assay noise sd
# SEED is chosen (24) so that, with theta_j ~ N(mu, tau), the winner's curse
# arises NATURALLY and is CORRECTABLE: the true-best compound (#0) happens to be
# well-replicated (n=20, hence recoverable), while a low-replicate compound (#11,
# n=2) posts a lucky-high RAW mean. Partial pooling shrinks the fluke back below
# the well-supported true best. Because theta is a genuine N(mu, tau) draw, the
# population parameters mu and tau remain recoverable.
SEED = 24

# Unequal replication: well-measured compounds first, barely-measured last.
# (This heterogeneity is what powers the winner's-curse demonstration.)
N_REPS = np.array([20, 18, 15, 12, 10, 8, 6, 4, 3, 2, 2, 2])


def generate(seed: int = SEED, j: int = J, mu: float = MU_TRUE,
             tau: float = TAU_TRUE, sigma: float = SIGMA_TRUE,
             n_reps: np.ndarray = N_REPS) -> dict:
    """Simulate a partially-pooled compound screen with unequal replication.

    ``theta_j ~ Normal(mu, tau)`` (genuine population draw, so mu/tau are
    recoverable). The fixed ``seed`` realises a screen in which the winner's curse
    appears and partial pooling corrects it (see the SEED note above).
    """
    rng = np.random.default_rng(seed)
    n_reps = np.asarray(n_reps)[:j]
    theta = mu + tau * rng.standard_normal(j)
    # flatten observations into (compound_index, value) long format
    comp_idx = np.repeat(np.arange(j), n_reps)
    values = np.empty(comp_idx.size)
    pos = 0
    for cj in range(j):
        nj = int(n_reps[cj])
        values[pos:pos + nj] = theta[cj] + sigma * rng.standard_normal(nj)
        pos += nj
    raw_means = np.array([values[comp_idx == cj].mean() for cj in range(j)])
    return {
        "comp_idx": comp_idx.astype(int),
        "y": values,
        "n_reps": n_reps.astype(int),
        "raw_means": raw_means,
        "j": int(j),
        "theta_true": theta,
        "best_true": int(np.argmax(theta)),
        "truth": {"mu": float(mu), "tau": float(tau), "sigma": float(sigma)},
    }


def save(path: str = "data/data.npz", **kw) -> dict:
    data = generate(**kw)
    out = pathlib.Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez(out, comp_idx=data["comp_idx"], y=data["y"], n_reps=data["n_reps"],
             raw_means=data["raw_means"], j=data["j"],
             theta_true=data["theta_true"], best_true=data["best_true"],
             mu=data["truth"]["mu"], tau=data["truth"]["tau"],
             sigma=data["truth"]["sigma"])
    return data


if __name__ == "__main__":
    d = save()
    print(f"Synthesized a screen of J={d['j']} compounds, unequal replication.")
    print(f"  replicates per compound: {d['n_reps']}")
    print(f"  TRUE best compound = #{d['best_true']} "
          f"(theta={d['theta_true'][d['best_true']]:.2f})")
    raw_best = int(np.argmax(d["raw_means"]))
    print(f"  RAW-mean winner    = #{raw_best} "
          f"(raw mean={d['raw_means'][raw_best]:.2f}, n={d['n_reps'][raw_best]})")
    if raw_best != d["best_true"]:
        print("  --> raw winner != true best: WINNER'S CURSE in play.")
    print(f"True mu={d['truth']['mu']}, tau={d['truth']['tau']}, sigma={d['truth']['sigma']} "
          f"(saved to data/data.npz)")
