"""Simulation-Based Calibration (SBC) for the logistic GLM.

SBC checks *inference correctness*, not just convergence. The logic:

  1. Draw (alpha*, beta*) from the prior.
  2. Simulate a binary dataset of size N from the logistic model.
  3. Fit the model; obtain L posterior draws of each coefficient.
  4. Record the rank of each true value among those L draws.

If the sampler + model are calibrated, these ranks are uniformly distributed on
{0, ..., L}. ∪-shapes => over-confident posteriors; ∩-shapes => under-confident;
slopes => bias.

Sampling is kept tiny (short chains, few sims) so the whole script runs in a
couple of minutes on CPU.
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

PRIOR_SD = 1.5
N_OBS = 60
N_SIMS = 50
L = 200          # posterior draws per simulation (chains*draws)
SEED = 20240601


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


def run_sbc(seed: int = SEED) -> dict:
    rng = np.random.default_rng(seed)
    x = rng.normal(0.0, 1.0, size=N_OBS)
    x = (x - x.mean()) / x.std()
    ranks = {"alpha": np.empty(N_SIMS, int), "beta": np.empty(N_SIMS, int)}
    for i in range(N_SIMS):
        alpha_star = rng.normal(0.0, PRIOR_SD)
        beta_star = rng.normal(0.0, PRIOR_SD)
        p = _sigmoid(alpha_star + beta_star * x)
        y = rng.binomial(1, p).astype(int)
        data = {"x": x, "y": y, "n": N_OBS}
        with build_model(data, prior_sd=PRIOR_SD):
            idata = pm.sample(
                draws=L // 2,
                tune=400,
                chains=2,
                random_seed=int(rng.integers(1, 1_000_000)),
                progressbar=False,
                compute_convergence_checks=False,
            )
        post_a = idata.posterior["alpha"].values.ravel()
        post_b = idata.posterior["beta"].values.ravel()
        ranks["alpha"][i] = sbc_rank(alpha_star, post_a)
        ranks["beta"][i] = sbc_rank(beta_star, post_b)
    return ranks


def main() -> None:
    ranks = run_sbc()
    print(f"SBC over {N_SIMS} simulations (N={N_OBS}, L≈{L})")
    reports = {}
    for name, r in ranks.items():
        rep = assert_calibrated(r, n_bins=10)
        reports[name] = rep
        print(f"  {name}: chi2={rep['chi2']:.2f}, dof={rep['dof']}, "
              f"p={rep['pvalue']:.3f}, uniform={rep['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(9, 3.5))
        for ax, (name, r) in zip(axes, ranks.items()):
            ax.hist(r, bins=10, color="#4C72B0", edgecolor="white")
            ax.axhline(N_SIMS / 10, color="k", ls="--", lw=1)
            ax.set(xlabel="rank", ylabel="count", title=f"SBC ranks — {name}")
        fig.suptitle("SBC rank histograms — logistic GLM")
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
