"""Simulation-Based Calibration (SBC) for the varying-slopes (LKJ) model.

We target the population-level **means** mu_a and mu_b — the intercept and slope a
varying-slopes analysis ultimately reports. (Calibrating the correlation rho would
need far more simulations; with G=8 lines rho is only loosely identified, so we
keep SBC light and focused on the means.)

For each simulation:
  1. Draw mu_a*, mu_b* ~ Normal(0, 5); draw random-effect SDs ~ HalfNormal(1);
     draw a correlation from the LKJ(eta=2) prior; build the 2x2 covariance.
  2. Draw [alpha_g, beta_g] ~ MVNormal, simulate y.
  3. Refit the correlated, non-centered model with a tiny sampler.
  4. Record the rank of mu_a* and mu_b*.

Light by design — LKJ refits are expensive. Read the histograms as "no detectable
miscalibration".
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import pymc as pm  # noqa: E402
from shared.bayes_utils import assert_calibrated, sbc_rank  # noqa: E402
from model import build_model  # noqa: E402

G = 8
N_PER = 10
N_SIMS = 10
L = 100
ETA = 2.0


def _lkj_corr2(rng: np.random.Generator, eta: float) -> float:
    """Draw a single 2x2 LKJ correlation. For n=2, rho ~ 2*Beta(eta,eta)-1."""
    b = rng.beta(eta, eta)
    return 2.0 * b - 1.0


def simulate_one(rng: np.random.Generator):
    mu_a = rng.normal(0.0, 5.0)
    mu_b = rng.normal(0.0, 5.0)
    sd_a = abs(rng.normal(0.0, 1.0))
    sd_b = abs(rng.normal(0.0, 1.0))
    rho = _lkj_corr2(rng, ETA)
    sd = np.array([sd_a, sd_b])
    cov = np.outer(sd, sd) * np.array([[1.0, rho], [rho, 1.0]])
    sigma = abs(rng.normal(0.0, 1.0)) + 1e-3
    effects = rng.multivariate_normal([mu_a, mu_b], cov, size=G)
    group = np.repeat(np.arange(G), N_PER)
    x = rng.normal(0.0, 1.0, size=G * N_PER)
    y = rng.normal(effects[group, 0] + effects[group, 1] * x, sigma)
    data = {"y": y.astype(float), "x": x.astype(float), "group": group.astype(int),
            "G": G, "n_per": N_PER}
    return data, {"mu_a": mu_a, "mu_b": mu_b}


def run_sbc(seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    ranks = {"mu_a": np.empty(N_SIMS, dtype=int), "mu_b": np.empty(N_SIMS, dtype=int)}
    for i in range(N_SIMS):
        data, truth = simulate_one(rng)
        # Sample directly (no prior/posterior predictive) to keep SBC fast.
        with build_model(data, correlated=True, eta=ETA):
            idata = pm.sample(
                draws=L,
                tune=200,
                chains=1,
                target_accept=0.9,
                random_seed=int(rng.integers(1, 2**31 - 1)),
                progressbar=False,
                compute_convergence_checks=False,
            )
        for n in ("mu_a", "mu_b"):
            ranks[n][i] = sbc_rank(truth[n], idata.posterior[n].values.ravel())
    return ranks


def main() -> None:
    ranks = run_sbc()
    print(f"SBC over {N_SIMS} simulations (G={G}, n_per={N_PER}, L~{L})")
    reports = {}
    for n in ("mu_a", "mu_b"):
        rep = assert_calibrated(ranks[n], n_bins=5)
        reports[n] = rep
        print(f"  {n}: chi2={rep['chi2']:.2f}, dof={rep['dof']}, "
              f"p={rep['pvalue']:.3f}, uniform={rep['uniform']}")
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(10, 3.5))
        for ax, n in zip(axes, ("mu_a", "mu_b")):
            ax.hist(ranks[n], bins=5, color="#4C72B0", edgecolor="white")
            ax.axhline(N_SIMS / 5, color="k", ls="--", lw=1, label="uniform")
            ax.set(xlabel=f"rank of {n}*", ylabel="count",
                   title=f"{n} (p={reports[n]['pvalue']:.2f})")
            ax.legend()
        fig.suptitle("SBC rank histograms — varying slopes (LKJ, non-centered)")
        fig.tight_layout()
        fig.savefig(pathlib.Path(__file__).parent / "sbc_ranks.png", dpi=110)
        print("  saved sbc_ranks.png")
    except Exception as exc:  # noqa: BLE001
        print(f"  (plot skipped: {exc})")


if __name__ == "__main__":
    main()
