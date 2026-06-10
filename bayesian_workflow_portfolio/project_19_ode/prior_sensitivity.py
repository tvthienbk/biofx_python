"""Prior sensitivity for the PK rate constants.

We refit the same data under three prior choices on (log k, log V) and compare the
posteriors and the k-V correlation. The mechanistic priors carry real information
(plausible physiological ranges), so we test how much the conclusion leans on them:

  * Informative   logk~N(-1,0.7), logV~N(2,0.5)  -- our default (plausible ranges).
  * Weak          logk~N(-1,1.5), logV~N(2,1.5)  -- broad but still proper.
  * Vague         logk~N(0,3),    logV~N(0,3)    -- nearly flat on the log scale.

Teaching point: with the full design (early + late timepoints) k and V are
identified and the posterior is fairly robust to the prior. But the (k, V)
posterior correlation grows as the prior loosens -- a window onto the practical
non-identifiability that becomes acute when the design is poor (see the broken
notebook, which drops the early timepoints).
"""
from __future__ import annotations

import pathlib
import sys

import arviz as az
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402

PRIORS = {
    "Informative N(.,.7/.5)": dict(k_sd=0.7, V_sd=0.5),
    "Weak N(.,1.5)": dict(k_sd=1.5, V_sd=1.5),
    "Vague N(0,3)": dict(k_mu=0.0, k_sd=3.0, V_mu=0.0, V_sd=3.0),
}


def main() -> None:
    data = generate()
    tk, tV = data["truth"]["k"], data["truth"]["V"]
    print(f"Data: n={data['n']} timepoints, true k={tk}, true V={tV}\n")
    header = f"{'prior':>22}  {'k mean':>7}  {'V mean':>7}  {'corr(k,V)':>9}  {'div':>4}"
    print(header)
    for name, kw in PRIORS.items():
        idata = fit(data, draws=400, tune=800, chains=2, seed=11, **kw)
        s = az.summary(idata, var_names=["k", "V"])
        kk = idata.posterior["k"].values.reshape(-1)
        VV = idata.posterior["V"].values.reshape(-1)
        corr = float(np.corrcoef(kk, VV)[0, 1])
        n_div = int(idata.sample_stats["diverging"].sum())
        print(f"{name:>22}  {s.loc['k','mean']:7.3f}  {s.loc['V','mean']:7.3f}  "
              f"{corr:9.3f}  {n_div:4d}")
    print("\nInterpretation: with the full (early+late) design, k and V stay near "
          "their truths across priors -- the mechanism is identified by the data. "
          "But the posterior corr(k, V) grows as the prior loosens, revealing the "
          "latent practical non-identifiability that a poor design would expose.")


if __name__ == "__main__":
    main()
