"""Prior sensitivity analysis for the scale prior in the Normal(mu, sigma) model.

The location prior on mu is held fixed; we vary the PRIOR ON SIGMA across three
proper choices that a careful analyst might consider:

  * HalfNormal(5)   — light tails, our default; discourages huge sigma.
  * Exponential(1/5)— mean ~5, memoryless, slightly heavier near 0.
  * HalfCauchy(5)   — heavy-tailed; permissive about large sigma.

The teaching point: with N=30 informative measurements the posterior for sigma is
well-determined and the three priors give nearly identical answers — BUT the
heavy-tailed HalfCauchy is the safest "weakly-informative" default when data are
scarce, and ALL THREE are vastly better than an improper flat prior (which is the
seeded bug, not a legitimate option to compare here).
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402

PRIORS = ["halfnormal", "exponential", "halfcauchy"]
LABELS = {
    "halfnormal": "HalfNormal(5)",
    "exponential": "Exponential(1/5)",
    "halfcauchy": "HalfCauchy(5)",
}


def main() -> None:
    data = generate()
    y = data["y"]
    print(f"Data: n={data['n']} measurements, empirical mean={y.mean():.3f}, "
          f"sd={y.std(ddof=1):.3f}")
    print(f"True mu={data['truth']['mu']}, sigma={data['truth']['sigma']}\n")
    header = f"{'sigma prior':>18}  {'mu mean':>8}  {'mu sd':>7}  {'sigma mean':>10}  {'sigma sd':>8}"
    print(header)
    rows = []
    import arviz as az
    for prior in PRIORS:
        idata = fit(data, sigma_prior=prior, draws=600, tune=600, chains=2, seed=303)
        summ = az.summary(idata, var_names=["mu", "sigma"])
        mu_mean = float(summ.loc["mu", "mean"])
        mu_sd = float(summ.loc["mu", "sd"])
        sig_mean = float(summ.loc["sigma", "mean"])
        sig_sd = float(summ.loc["sigma", "sd"])
        rows.append((prior, mu_mean, mu_sd, sig_mean, sig_sd))
        print(f"{LABELS[prior]:>18}  {mu_mean:8.3f}  {mu_sd:7.3f}  "
              f"{sig_mean:10.3f}  {sig_sd:8.3f}")
    mu_spread = max(r[1] for r in rows) - min(r[1] for r in rows)
    sig_spread = max(r[3] for r in rows) - min(r[3] for r in rows)
    print(f"\nMax difference across priors:  mu={mu_spread:.4f},  sigma={sig_spread:.4f}")
    print("Interpretation: with N=30 informative data, the proper scale priors agree;")
    print("the choice among them is minor. An IMPROPER flat sigma prior is the real danger.")


if __name__ == "__main__":
    main()
