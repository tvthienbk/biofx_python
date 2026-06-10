"""Simulation-Based Calibration (SBC) for the PK rate constant k.

We calibrate on ``k`` (the elimination rate), the headline mechanistic parameter.
We use the **analytic** model so each refit is cheap — this is the responsible
choice for SBC of an ODE model with a closed form, and keeps the script tractable
(the brief calls for "VERY light" SBC given ODE cost).

The loop:
  1. Draw log k*, log V* from their priors (+ sigma*).
  2. Simulate concentrations at the design timepoints via the closed form.
  3. Refit the analytic model; obtain posterior draws of k.
  4. Record the rank of k* among them.

Calibrated inference -> uniform ranks.

NOTE (compute): even with the analytic model each refit is a small NUTS run; we
keep N_SIMS modest. With the genuine DifferentialEquation model this would be
prohibitively slow, which is precisely why SBC here uses the closed form.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from shared.bayes_utils import assert_calibrated, sbc_rank  # noqa: E402
from data.generate_data import TIMES, DOSE, analytic_C  # noqa: E402
from model import build_model  # noqa: E402

import pymc as pm  # noqa: E402

N_SIMS = 25
DRAWS = 200
TUNE = 400
K_MU, K_SD = -1.0, 0.7
V_MU, V_SD = 2.0, 0.5
SIGMA_SD = 1.0


def run_sbc(seed: int = 0) -> np.ndarray:
    rng = np.random.default_rng(seed)
    ranks = []
    for i in range(N_SIMS):
        k = float(np.exp(rng.normal(K_MU, K_SD)))
        V = float(np.exp(rng.normal(V_MU, V_SD)))
        sigma = abs(rng.normal(0.0, SIGMA_SD))
        if sigma < 1e-2:
            sigma = 0.1
        C = analytic_C(TIMES, k=k, V=V, dose=DOSE)
        y = np.clip(C + rng.normal(0.0, sigma, size=TIMES.size), 1e-3, None)
        data = {"t": TIMES, "y": y, "dose": DOSE}
        with build_model(data):
            idata = pm.sample(draws=DRAWS, tune=TUNE, chains=2, cores=1,
                              target_accept=0.9, random_seed=i + 1,
                              progressbar=False)
        post = idata.posterior["k"].values.reshape(-1)
        ranks.append(sbc_rank(k, post))
    return np.asarray(ranks, dtype=int)


def main() -> None:
    ranks = run_sbc()
    n_bins = 8
    report = assert_calibrated(ranks, n_bins=n_bins)
    print(f"SBC over {len(ranks)} simulations for k (analytic PK model)")
    print(f"  chi-square uniformity test: chi2={report['chi2']:.2f}, "
          f"dof={report['dof']}, p={report['pvalue']:.3f}")
    print(f"  ranks look uniform: {report['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 3.5))
        ax.hist(ranks, bins=n_bins, color="#4C72B0", edgecolor="white")
        ax.axhline(len(ranks) / n_bins, color="k", ls="--", lw=1,
                   label="uniform expectation")
        ax.set(xlabel="rank of prior draw (k)", ylabel="count",
               title="SBC rank histogram — PK elimination rate k")
        ax.legend()
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
