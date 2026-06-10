"""Prior sensitivity for the varying-slopes model — the LKJ ``eta``.

The LKJ prior's shape parameter ``eta`` controls how much the model expects the
intercept-slope correlation to be near 0:

  * eta = 1  : uniform over all valid correlations (no prior pull).
  * eta = 2  : mild pull toward 0 (our default).
  * eta = 8  : strong pull toward 0 (skeptical of correlation).

With only G=8 cell lines, rho is weakly identified, so eta can move the posterior
correlation. We refit under three eta values and compare the posterior for rho (and
the population means, which should be robust).
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import arviz as az  # noqa: E402
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402

ETAS = {
    "uniform eta=1": 1.0,
    "default eta=2": 2.0,
    "skeptical eta=8": 8.0,
}


def main() -> None:
    data = generate()
    truth = data["truth"]
    print(f"Data: G={data['G']} lines x {data['n_per']} obs; "
          f"true rho={truth['rho']}, mu_a={truth['mu_a']}, mu_b={truth['mu_b']}\n")
    print(f"{'LKJ prior':>18}  {'rho mean':>8}  {'rho 94% HDI':>20}  "
          f"{'mu_a':>6}  {'mu_b':>6}")
    rows = []
    for name, eta in ETAS.items():
        idata = fit(
            data,
            correlated=True,
            eta=eta,
            draws=600,
            tune=1000,
            chains=2,
            target_accept=0.9,
            seed=202,
        )
        summ = az.summary(idata, var_names=["rho", "mu_a", "mu_b"], hdi_prob=0.94)
        rho_m = float(summ.loc["rho", "mean"])
        lo = float(summ.loc["rho", "hdi_3%"])
        hi = float(summ.loc["rho", "hdi_97%"])
        mua = float(summ.loc["mu_a", "mean"])
        mub = float(summ.loc["mu_b", "mean"])
        rows.append((name, rho_m, lo, hi, mua, mub))
        print(f"{name:>18}  {rho_m:8.3f}  [{lo:6.3f}, {hi:6.3f}]  {mua:6.3f}  {mub:6.3f}")

    rho_spread = max(r[1] for r in rows) - min(r[1] for r in rows)
    mua_spread = max(r[4] for r in rows) - min(r[4] for r in rows)
    print(f"\nSpread in posterior mean rho across eta: {rho_spread:.3f}")
    print(f"Spread in posterior mean mu_a across eta: {mua_spread:.3f}")
    print("Interpretation: a larger eta pulls the estimated correlation toward 0;")
    print("the population means are robust. With few groups, report eta explicitly.")


if __name__ == "__main__":
    main()
