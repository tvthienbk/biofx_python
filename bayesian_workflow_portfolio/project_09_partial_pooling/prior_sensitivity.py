"""Prior sensitivity analysis for the hierarchical Normal (partial-pooling) model.

The parameter that matters most in a hierarchical model with *few groups* is the
prior on the between-group SD ``tau``. ``tau`` controls how much each group's
estimate is shrunk toward the grand mean: a tight prior near 0 forces strong
pooling (groups look identical), a diffuse prior permits little pooling (groups
float free). With only J=12 groups the data constrain ``tau`` weakly, so the prior
can have real leverage on both ``tau`` itself and the degree of shrinkage.

We refit the same data under three HalfNormal priors on ``tau``:

  * tight   HalfNormal(0.5) — strong a-priori pull toward complete pooling
  * default HalfNormal(2.0) — our weakly-informative choice
  * vague   HalfNormal(10)  — almost no constraint

and compare the posterior for ``tau`` and ``mu``, plus a shrinkage summary.
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
    "tight HalfNormal(0.5)": 0.5,
    "default HalfNormal(2.0)": 2.0,
    "vague HalfNormal(10)": 10.0,
}


def main() -> None:
    data = generate()
    truth = data["truth"]
    print(f"Data: J={data['J']} groups x {data['n_per']} obs; "
          f"true mu={truth['mu']}, tau={truth['tau']}, sigma={truth['sigma']}\n")
    print(f"{'tau prior':>26}  {'mu mean':>8}  {'tau mean':>9}  "
          f"{'tau 94% HDI':>20}")
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
        summ = az.summary(idata, var_names=["mu", "tau"], hdi_prob=0.94)
        mu_mean = float(summ.loc["mu", "mean"])
        tau_mean = float(summ.loc["tau", "mean"])
        lo = float(summ.loc["tau", "hdi_3%"])
        hi = float(summ.loc["tau", "hdi_97%"])
        rows.append((name, mu_mean, tau_mean, lo, hi))
        print(f"{name:>26}  {mu_mean:8.3f}  {tau_mean:9.3f}  [{lo:6.3f}, {hi:6.3f}]")

    tau_spread = max(r[2] for r in rows) - min(r[2] for r in rows)
    mu_spread = max(r[1] for r in rows) - min(r[1] for r in rows)
    print(f"\nSpread in posterior mean tau across priors: {tau_spread:.3f}")
    print(f"Spread in posterior mean mu  across priors: {mu_spread:.3f}")
    print("Interpretation: mu (grand mean) is robust; tau (and hence the amount of")
    print("shrinkage) is sensitive to its prior when groups are few. Report tau's")
    print("prior explicitly and prefer a weakly-informative HalfNormal over a vague one.")


if __name__ == "__main__":
    main()
