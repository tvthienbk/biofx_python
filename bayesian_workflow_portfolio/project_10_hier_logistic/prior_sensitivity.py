"""Prior sensitivity for the hierarchical logistic model — the tau prior.

With only G=10 families the between-family SD ``tau`` (on the log-odds intercept)
is weakly identified, so its prior controls how aggressively family intercepts are
pooled. A tight prior collapses all families toward one common intercept
(over-pooling); a vague prior lets them float. We refit under three HalfNormal
priors on tau and compare the posterior for tau, mu, and beta, plus the spread of
the recovered family intercepts (a direct read on pooling).
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import arviz as az  # noqa: E402
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402

PRIORS = {
    "tight HalfNormal(0.1)": 0.1,
    "default HalfNormal(1.0)": 1.0,
    "vague HalfNormal(5.0)": 5.0,
}


def main() -> None:
    data = generate()
    truth = data["truth"]
    print(f"Data: G={data['G']} families x {data['n_per']} obs; "
          f"true mu={truth['mu']}, tau={truth['tau']}, beta={truth['beta']}\n")
    print(f"{'tau prior':>26}  {'mu':>7}  {'tau':>7}  {'beta':>7}  {'alpha spread':>12}")
    rows = []
    for name, tau_sd in PRIORS.items():
        idata = fit(
            data,
            parameterization="noncentered",
            tau_prior_sd=tau_sd,
            draws=600,
            tune=1000,
            chains=2,
            target_accept=0.95,
            seed=202,
        )
        summ = az.summary(idata, var_names=["mu", "tau", "beta"], hdi_prob=0.94)
        alpha_means = idata.posterior["alpha"].mean(dim=("chain", "draw")).values
        spread = float(alpha_means.max() - alpha_means.min())
        row = (name, float(summ.loc["mu", "mean"]), float(summ.loc["tau", "mean"]),
               float(summ.loc["beta", "mean"]), spread)
        rows.append(row)
        print(f"{name:>26}  {row[1]:7.3f}  {row[2]:7.3f}  {row[3]:7.3f}  {row[4]:12.3f}")

    spread_tau = max(r[2] for r in rows) - min(r[2] for r in rows)
    spread_alpha = max(r[4] for r in rows) - min(r[4] for r in rows)
    print(f"\nSpread in posterior mean tau across priors: {spread_tau:.3f}")
    print(f"Spread in family-intercept range across priors: {spread_alpha:.3f}")
    print("Interpretation: a tight tau prior over-pools (family intercepts collapse")
    print("toward a single value); the global slope beta is comparatively robust.")


if __name__ == "__main__":
    main()
