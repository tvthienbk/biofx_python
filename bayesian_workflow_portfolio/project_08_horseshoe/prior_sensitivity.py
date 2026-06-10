"""Prior sensitivity analysis for the regularized horseshoe.

The horseshoe's behavior is governed by the GLOBAL SCALE prior, parameterized here
by tau0 (the scale of the HalfCauchy on tau). Smaller tau0 => more aggressive
global shrinkage => sparser solutions; larger tau0 => weaker shrinkage, closer to
a ridge. We refit under three tau0 values and report, for each:

  * the recovered nonzero coefficients (should stay near the truth),
  * the largest |coefficient| among the TRUE-ZERO predictors (a sparsity metric:
    smaller is better / sparser).

Teaching point: the nonzero coefficients are robust across a wide tau0 range
(the data identify them strongly), while the shrinkage of the noise coefficients
tightens as tau0 shrinks. There is a sweet spot: too-small tau0 can also shrink a
genuine weak signal, so tau0 should be set from a prior guess at the number of
relevant predictors, not cranked to zero.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402

TAU0S = {
    "aggressive tau0=0.05": 0.05,
    "default tau0=0.1": 0.1,
    "weak tau0=0.5": 0.5,
}


def main() -> None:
    data = generate()
    nz = data["nonzero_idx"]
    zeros = [j for j in range(data["p"]) if j not in nz]
    print(f"Data: n={data['n']}, p={data['p']}, nonzero at {nz} "
          f"= {[round(float(data['beta_true'][j]),2) for j in nz]}\n")
    header = f"{'tau0 setting':>22}  {'est nonzero':>26}  {'max|noise beta|':>15}"
    print(header)
    print("-" * len(header))
    for name, tau0 in TAU0S.items():
        idata = fit(data, model="horseshoe", tau0=tau0,
                    draws=200, tune=250, chains=2, seed=11, target_accept=0.9)
        bmean = idata.posterior["beta"].mean(("chain", "draw")).values
        est_nz = [round(float(bmean[j]), 2) for j in nz]
        max_noise = float(np.max(np.abs(bmean[zeros])))
        print(f"{name:>22}  {str(est_nz):>26}  {max_noise:15.3f}")
    print("\nInterpretation: the three real coefficients are recovered across all "
          "tau0; the shrinkage of the true-zero coefficients tightens as tau0 "
          "shrinks. Set tau0 from a prior guess at sparsity; do not crank it to 0, "
          "which would also shrink genuine weak signals.")


if __name__ == "__main__":
    main()
