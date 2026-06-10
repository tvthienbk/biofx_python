"""Prior sensitivity analysis for the slope/intercept priors (standardized model).

Refit the same data under three prior widths on (alpha, beta), holding the
standardized predictor fixed:

  * Vague        Normal(0, 20)  — very broad on the standardized scale.
  * Weak-info    Normal(0, 5)   — our default.
  * Tight        Normal(0, 1)   — deliberately narrow.

On the STANDARDIZED scale, coefficients are O(1)-to-O(10), so Normal(0, 5) is a
sensible weakly-informative width and Normal(0, 1) is somewhat tight but not
catastrophic. With N=40 informative points the posteriors should nearly coincide
for the vague and weak-info priors, and the tight prior shrinks the slope only
mildly. The teaching point: standardizing makes priors EASY to set on a common
O(1) scale — the very thing the pitfall (un-scaled x) destroys.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402

PRIORS = {
    "Vague Normal(0,20)": 20.0,
    "Weak-info Normal(0,5)": 5.0,
    "Tight Normal(0,1)": 1.0,
}


def main() -> None:
    import arviz as az

    data = generate()
    print(f"Data: n={data['n']} points; standardized truth "
          f"alpha={data['truth']['alpha']:.3f}, beta={data['truth']['beta']:.3f}\n")
    print(f"{'prior (alpha,beta)':>22}  {'alpha':>7}  {'beta':>7}  {'sigma':>7}")
    rows = []
    for name, sd in PRIORS.items():
        idata = fit(data, alpha_sd=sd, beta_sd=sd, draws=600, tune=600,
                    chains=2, seed=505)
        summ = az.summary(idata, var_names=["alpha", "beta", "sigma"])
        a = float(summ.loc["alpha", "mean"])
        b = float(summ.loc["beta", "mean"])
        s = float(summ.loc["sigma", "mean"])
        rows.append((name, a, b, s))
        print(f"{name:>22}  {a:7.3f}  {b:7.3f}  {s:7.3f}")
    a_spread = max(r[1] for r in rows) - min(r[1] for r in rows)
    b_spread = max(r[2] for r in rows) - min(r[2] for r in rows)
    print(f"\nMax difference across priors:  alpha={a_spread:.4f},  beta={b_spread:.4f}")
    print("Interpretation: on the standardized scale priors are easy and the data")
    print("dominate; the vague and weak-info priors agree closely. Standardizing is")
    print("what makes O(1) priors meaningful — un-scaled x would make this impossible.")


if __name__ == "__main__":
    main()
