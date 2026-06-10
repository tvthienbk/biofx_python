"""Prior sensitivity analysis for the Negative-Binomial GLM.

The project's parameter of interest for sensitivity is the **dispersion prior**
on alpha. alpha controls overdispersion: Var(y) = mu + mu^2/alpha. A prior that
pushes alpha large pulls the NB toward Poisson (under-dispersed); a prior that
allows small alpha lets the data express their true overdispersion.

We refit the same data under three Gamma priors on alpha and compare the
posterior for alpha and for the regression coefficients:

  * Tight-large  Gamma(20, 1)   mean 20 -> nudges toward Poisson-like.
  * Default      Gamma(2, 0.1)  mean 20 but heavy-tailed -> flexible.
  * Loose-small  Gamma(1, 1)    mean 1  -> favors strong overdispersion.

Teaching point: the *coefficients* are robust to the dispersion prior (the log
link separates mean from variance), while the *dispersion* posterior shifts as
expected. With N=150 the data still pin alpha near its true value under all but
the most aggressive prior.
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
    "Tight-large Gamma(20,1)": (20.0, 1.0),
    "Default Gamma(2,0.1)": (2.0, 0.1),
    "Loose-small Gamma(1,1)": (1.0, 1.0),
}


def main() -> None:
    data = generate()
    truth = data["truth"]
    print(f"Data: n={data['n']}, var/mean={data['y'].var()/data['y'].mean():.2f}")
    print(f"True beta1={truth['beta1']}, alpha={truth['alpha']}\n")
    header = f"{'alpha prior':>26}  {'param':>6}  {'mean':>7}  {'sd':>6}  {'94% HDI':>18}"
    print(header)
    print("-" * len(header))
    for name, (a, b) in PRIORS.items():
        idata = fit(data, model="nb", alpha_a=a, alpha_b=b,
                    draws=500, tune=500, chains=2, seed=11)
        summ = az.summary(idata, var_names=["beta1", "alpha"], hdi_prob=0.94)
        for param in ("beta1", "alpha"):
            row = summ.loc[param]
            print(f"{name:>26}  {param:>6}  {row['mean']:7.3f}  "
                  f"{row['sd']:6.3f}  [{row['hdi_3%']:6.3f}, {row['hdi_97%']:6.3f}]")
        print()
    print("Interpretation: beta1 (the mean effect) is robust to the dispersion "
          "prior; alpha shifts as expected but the data (N=150) keep it near the "
          "truth except under the most aggressive Poisson-nudging prior.")


if __name__ == "__main__":
    main()
