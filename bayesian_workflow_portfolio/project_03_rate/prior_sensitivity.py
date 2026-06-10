"""Prior sensitivity analysis for the prior on log_rate.

Refit the same data under three Normal priors on log_rate:

  * Vague        Normal(0, 5)   — very broad on the log scale.
  * Weak-info    Normal(0, 2)   — our default; covers ~exp(-4)..exp(4).
  * Mild-info    Normal(-1, 1)  — centred near a plausible rate, tighter.

With N=50 informative counts the likelihood dominates and the posteriors for
log_rate should nearly coincide. The teaching point mirrors Projects 01/02: priors
matter most when data are scarce; here the data swamp them.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402

PRIORS = {
    "Vague Normal(0,5)": (0.0, 5.0),
    "Weak-info Normal(0,2)": (0.0, 2.0),
    "Mild-info Normal(-1,1)": (-1.0, 1.0),
}


def main() -> None:
    import numpy as np
    import arviz as az

    data = generate()
    print(f"Data: n={data['n']} samples, total events={int(data['y'].sum())}, "
          f"total exposure={data['exposure'].sum():.1f}")
    print(f"True log_rate={data['truth']['log_rate']} "
          f"(rate={np.exp(data['truth']['log_rate']):.3f})\n")
    print(f"{'prior':>24}  {'logr mean':>9}  {'logr sd':>8}  {'rate mean':>9}")
    rows = []
    for name, (m, s) in PRIORS.items():
        idata = fit(data, prior_mean=m, prior_sd=s, draws=600, tune=600,
                    chains=2, seed=404)
        summ = az.summary(idata, var_names=["log_rate"])
        lr_mean = float(summ.loc["log_rate", "mean"])
        lr_sd = float(summ.loc["log_rate", "sd"])
        rate_mean = float(np.exp(idata.posterior["log_rate"].values).mean())
        rows.append((name, lr_mean, lr_sd, rate_mean))
        print(f"{name:>24}  {lr_mean:9.3f}  {lr_sd:8.3f}  {rate_mean:9.3f}")
    spread = max(r[1] for r in rows) - min(r[1] for r in rows)
    print(f"\nMax difference in posterior mean log_rate across priors: {spread:.4f}")
    print("Interpretation: with N=50 the data swamp the prior; conclusions are robust.")


if __name__ == "__main__":
    main()
