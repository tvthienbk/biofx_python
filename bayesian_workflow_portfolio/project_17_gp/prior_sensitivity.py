"""Prior sensitivity analysis for the GP — the length-scale prior is THE lever.

We refit the same data under three length-scale priors and compare the
posterior for ``ell``, ``eta``, and ``sigma``, plus the fitted-curve fit:

  * Informative   InverseGamma(6, 12)  -- our default; mass around ell ~ 2.
  * Mild          InverseGamma(3, 6)   -- broader, still proper, ell ~ 3.
  * Vague         InverseGamma(1, 1)   -- heavy-tailed; lets ell wander, which
                  re-opens the length-scale / marginal-variance trade-off.

Teaching point: a GP's identifiability lives almost entirely in the length-scale
prior. With a vague prior, ``ell`` and ``eta`` become correlated and the sampler
struggles; with an informative prior the posterior is well-behaved and the curve
fit is stable. We report posterior summaries and the curve RMSE for each.
"""
from __future__ import annotations

import pathlib
import sys

import arviz as az
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from data.generate_data import generate  # noqa: E402
from model import fit, predict_curve  # noqa: E402

PRIORS = {
    "Informative IG(6,12)": dict(ell_alpha=6.0, ell_beta=12.0),
    "Mild IG(3,6)": dict(ell_alpha=3.0, ell_beta=6.0),
    "Vague IG(1,1)": dict(ell_alpha=1.0, ell_beta=1.0),
}


def main() -> None:
    data = generate()
    print(f"Data: n={data['n']}, true sigma={data['truth']['sigma']:.3f}\n")
    header = f"{'prior':>22}  {'ell mean':>8}  {'eta mean':>8}  {'sigma mean':>10}  {'div':>4}  {'curve MAE':>9}"
    print(header)
    rows = []
    for name, kw in PRIORS.items():
        idata = fit(data, draws=120, tune=200, chains=2, seed=11, **kw)
        s = az.summary(idata, var_names=["ell", "eta", "sigma"])
        n_div = int(idata.sample_stats["diverging"].sum())
        pred = predict_curve(data, idata, x_new=data["x"], seed=5, **kw)
        mae = float(np.mean(np.abs(pred["mean"] - data["f_true"])))
        rows.append((name, s, n_div, mae))
        print(f"{name:>22}  {s.loc['ell','mean']:8.3f}  {s.loc['eta','mean']:8.3f}  "
              f"{s.loc['sigma','mean']:10.3f}  {n_div:4d}  {mae:9.3f}")
    print("\nInterpretation: the informative and mild priors give a stable, "
          "well-mixing fit with sigma near the truth and low curve error. The "
          "vague IG(1,1) prior typically inflates divergences and lets ell/eta "
          "trade off -- the canonical GP non-identifiability. The length-scale "
          "prior is the single most consequential modelling choice here.")


if __name__ == "__main__":
    main()
