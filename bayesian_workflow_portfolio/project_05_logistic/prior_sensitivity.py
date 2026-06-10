"""Prior sensitivity analysis for the logistic GLM.

The pitfall of this project lives entirely in the *width* of the coefficient
priors, so prior sensitivity is the natural place to quantify it. We refit the
same data under three coefficient-prior widths and compare the posterior for
``(alpha, beta)``:

  * Tight     Normal(0, 0.5) — strongly informative; may fight the data.
  * Weak-info Normal(0, 1.5) — our default; sensible on the probability scale.
  * Vague     Normal(0, 10)  — the "non-informative" mistake; on the probability
                               scale this prior is *certain* p is ~0 or ~1.

With N=120 reasonably informative data, the *posterior* for the coefficients
should be fairly stable across the weak and vague priors (the likelihood
dominates), while the *tight* prior visibly shrinks beta toward 0. The deeper
teaching point — that the vague prior is pathological *before* seeing data — is
shown on the probability scale in the notebook's prior predictive check.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402

import arviz as az  # noqa: E402

PRIORS = {
    "Tight Normal(0,0.5)": 0.5,
    "Weak-info Normal(0,1.5)": 1.5,
    "Vague Normal(0,10)": 10.0,
}


def main() -> None:
    data = generate()
    truth = data["truth"]
    print(f"Data: n={data['n']} wells, binding rate={data['y'].mean():.3f}")
    print(f"True alpha={truth['alpha']}, beta={truth['beta']}\n")
    header = f"{'prior':>26}  {'param':>5}  {'mean':>7}  {'sd':>6}  {'94% HDI':>18}"
    print(header)
    print("-" * len(header))
    for name, sd in PRIORS.items():
        idata = fit(data, prior_sd=sd, draws=500, tune=500, chains=2, seed=11)
        summ = az.summary(idata, var_names=["alpha", "beta"], hdi_prob=0.94)
        for param in ("alpha", "beta"):
            row = summ.loc[param]
            lo = row["hdi_3%"]
            hi = row["hdi_97%"]
            print(f"{name:>26}  {param:>5}  {row['mean']:7.3f}  "
                  f"{row['sd']:6.3f}  [{lo:6.3f}, {hi:6.3f}]")
        print()
    print("Interpretation: weak-info and vague priors give nearly identical "
          "posteriors here (data dominate); the tight prior shrinks beta toward 0. "
          "The vague prior's danger is on the PROBABILITY scale before data — see "
          "the notebook prior predictive check.")


if __name__ == "__main__":
    main()
