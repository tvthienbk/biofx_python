"""Simulation-Based Calibration (SBC) for the Student-t robust regression.

SBC checks *inference correctness*, not just convergence:

  1. Draw (alpha*, beta*, sigma*, nu*) from the priors the MODEL assumes.
  2. Simulate a Student-t dataset of size N using nu*.
  3. Fit the Student-t model; obtain L posterior draws of each parameter.
  4. Record the rank of each true value among those L draws.

Calibrated inference => ranks uniform on {0,...,L}. We calibrate the regression
parameters (alpha, beta) and the scale (sigma). CRITICAL: the simulator draws nu
from the SAME Gamma prior the model uses, so simulator and model agree on the
data-generating process — otherwise the sigma ranks come out spuriously
non-uniform. For tractable SBC we use tighter coefficient priors than the model
default (the default Normal(0,5) admits extreme lines that fit slowly) and a
moderate-mean nu prior; SBC validates the machinery over a representative slice.

Sampling is tiny (short chains, few sims) so the whole script runs in ~1-2 min.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from shared.bayes_utils import assert_calibrated, sbc_rank  # noqa: E402
from model import build_model  # noqa: E402

import pymc as pm  # noqa: E402

COEF_SD = 2.0       # tighter than the model default for tractable SBC
SIGMA_SD = 1.0
NU_A, NU_B = 8.0, 0.5   # nu prior used in BOTH simulator and model (mean 16);
                        # keeping simulator and model consistent is what makes
                        # the SBC of (alpha, beta, sigma) valid. A moderate mean
                        # avoids extreme small-nu draws that make fits slow.
N_OBS = 40
N_SIMS = 20
L = 200
SEED = 20240601


def run_sbc(seed: int = SEED) -> dict:
    rng = np.random.default_rng(seed)
    x = rng.uniform(-2.0, 2.0, size=N_OBS)
    x = (x - x.mean()) / x.std()
    names = ("alpha", "beta", "sigma")
    ranks = {k: np.empty(N_SIMS, int) for k in names}
    for i in range(N_SIMS):
        a = rng.normal(0.0, COEF_SD)
        b = rng.normal(0.0, COEF_SD)
        s = abs(rng.normal(0.0, SIGMA_SD)) + 1e-3
        # Draw nu from the SAME prior the model uses, then simulate Student-t data
        # with that nu. Simulator and model now share one generative process, so
        # the ranks for (alpha, beta, sigma) are valid.
        nu_star = rng.gamma(NU_A, 1.0 / NU_B)
        eps = rng.standard_t(nu_star, size=N_OBS) * s
        y = a + b * x + eps
        data = {"x": x, "y": y, "n": N_OBS}
        with build_model(data, model="studentt", coef_sd=COEF_SD, sigma_sd=SIGMA_SD,
                         nu_a=NU_A, nu_b=NU_B):
            idata = pm.sample(
                draws=L // 2, tune=400, chains=2,
                random_seed=int(rng.integers(1, 1_000_000)),
                progressbar=False, compute_convergence_checks=False,
            )
        for name, truth in zip(names, (a, b, s)):
            post = idata.posterior[name].values.ravel()
            ranks[name][i] = sbc_rank(truth, post)
    return ranks


def main() -> None:
    ranks = run_sbc()
    print(f"SBC over {N_SIMS} simulations (N={N_OBS}, L~{L})")
    for name, r in ranks.items():
        rep = assert_calibrated(r, n_bins=4)
        print(f"  {name}: chi2={rep['chi2']:.2f}, dof={rep['dof']}, "
              f"p={rep['pvalue']:.3f}, uniform={rep['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
        for ax, (name, r) in zip(axes, ranks.items()):
            ax.hist(r, bins=4, color="#4C72B0", edgecolor="white")
            ax.axhline(N_SIMS / 4, color="k", ls="--", lw=1)
            ax.set(xlabel="rank", ylabel="count", title=f"SBC — {name}")
        fig.suptitle("SBC rank histograms — Student-t robust regression")
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
