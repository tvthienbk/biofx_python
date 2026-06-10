"""Simulation-Based Calibration (SBC) for the Negative-Binomial GLM.

SBC checks *inference correctness*, not just convergence:

  1. Draw (beta0*, beta1*, alpha*) from the prior.
  2. Simulate an overdispersed count dataset of size N.
  3. Fit the NB model; obtain L posterior draws of each parameter.
  4. Record the rank of each true value among those L draws.

Calibrated inference => ranks uniform on {0,...,L}. We focus on the regression
coefficients (beta0, beta1) and the dispersion (alpha). To keep the run fast we
constrain the prior draws to a sensible range (the full Gamma(2,0.1) tail can
produce numerically extreme means); this is standard practice for tractable SBC.

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

BETA0_SD, BETA1_SD = 1.0, 1.0   # tighter than the model default for tractable SBC
ALPHA_A, ALPHA_B = 3.0, 0.5     # Gamma mean 6: moderate dispersion, avoids extremes
N_OBS = 50
N_SIMS = 30
L = 200
SEED = 20240601


def run_sbc(seed: int = SEED) -> dict:
    rng = np.random.default_rng(seed)
    x = rng.normal(0.0, 1.0, size=N_OBS)
    x = (x - x.mean()) / x.std()
    names = ("beta0", "beta1", "alpha")
    ranks = {k: np.empty(N_SIMS, int) for k in names}
    for i in range(N_SIMS):
        b0 = rng.normal(0.0, BETA0_SD)
        b1 = rng.normal(0.0, BETA1_SD)
        a = rng.gamma(ALPHA_A, 1.0 / ALPHA_B)
        mu = np.exp(b0 + b1 * x)
        p = a / (a + mu)
        y = rng.negative_binomial(a, p).astype(int)
        data = {"x": x, "y": y, "n": N_OBS}
        with build_model(data, model="nb", beta0_sd=BETA0_SD, beta1_sd=BETA1_SD,
                         alpha_a=ALPHA_A, alpha_b=ALPHA_B):
            idata = pm.sample(
                draws=L // 2, tune=400, chains=2,
                random_seed=int(rng.integers(1, 1_000_000)),
                progressbar=False, compute_convergence_checks=False,
            )
        for name, truth in zip(names, (b0, b1, a)):
            post = idata.posterior[name].values.ravel()
            ranks[name][i] = sbc_rank(truth, post)
    return ranks


def main() -> None:
    ranks = run_sbc()
    print(f"SBC over {N_SIMS} simulations (N={N_OBS}, L~{L})")
    for name, r in ranks.items():
        rep = assert_calibrated(r, n_bins=6)
        print(f"  {name}: chi2={rep['chi2']:.2f}, dof={rep['dof']}, "
              f"p={rep['pvalue']:.3f}, uniform={rep['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
        for ax, (name, r) in zip(axes, ranks.items()):
            ax.hist(r, bins=6, color="#4C72B0", edgecolor="white")
            ax.axhline(N_SIMS / 6, color="k", ls="--", lw=1)
            ax.set(xlabel="rank", ylabel="count", title=f"SBC — {name}")
        fig.suptitle("SBC rank histograms — Negative-Binomial GLM")
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
