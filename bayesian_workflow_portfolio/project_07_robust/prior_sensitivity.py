"""Prior sensitivity analysis for the Student-t robust regression.

The parameter that defines robustness is the **degrees of freedom nu**, so the
prior worth stress-testing is the prior on nu. nu controls tail weight:
small nu => heavy tails (very robust, outliers down-weighted); large nu => the
Student-t approaches a Normal (non-robust, outliers dominate again).

We refit the same outlier-contaminated data under three priors on nu, plus a
'nu fixed large' variant that deliberately defeats robustness, and compare the
slope beta (which should be dragged toward the Normal estimate as nu is forced up):

  * Heavy-tail-friendly  Gamma(2, 0.5)   mean 4   -> permits heavy tails.
  * Default               Gamma(2, 0.1)  mean 20  -> flexible.
  * Normal-leaning        Gamma(20, 0.5) mean 40  -> nudges toward Normal.

Teaching point: the robust slope is stable as long as the nu prior PERMITS small
nu. A prior (or fixed value) that forces nu large reintroduces the outlier bias
the Student-t was meant to remove.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402

import arviz as az  # noqa: E402

PRIORS = {
    "Heavy-tail Gamma(2,0.5)": (2.0, 0.5),
    "Default Gamma(2,0.1)": (2.0, 0.1),
    "Normal-leaning Gamma(20,0.5)": (20.0, 0.5),
}


def main() -> None:
    data = generate()
    truth = data["truth"]
    print(f"Data: n={data['n']}, outliers={int(data['is_outlier'].sum())}")
    print(f"True (clean) alpha={truth['alpha']}, beta={truth['beta']}\n")
    header = f"{'nu prior':>30}  {'param':>5}  {'mean':>7}  {'sd':>6}  {'94% HDI':>18}"
    print(header)
    print("-" * len(header))
    for name, (a, b) in PRIORS.items():
        idata = fit(data, model="studentt", nu_a=a, nu_b=b,
                    draws=600, tune=600, chains=2, seed=11)
        summ = az.summary(idata, var_names=["beta", "nu"], hdi_prob=0.94)
        for param in ("beta", "nu"):
            row = summ.loc[param]
            print(f"{name:>30}  {param:>5}  {row['mean']:7.3f}  "
                  f"{row['sd']:6.3f}  [{row['hdi_3%']:6.3f}, {row['hdi_97%']:6.3f}]")
        print()
    print("Interpretation: while the nu prior PERMITS small nu, the data pull nu "
          "low (heavy tails) and the slope beta stays near the clean truth 2.0. A "
          "prior that forces nu large drags beta toward the Normal (outlier-biased) "
          "estimate. The fix for a non-robust fit is to LET nu be small, not fix it.")


if __name__ == "__main__":
    main()
