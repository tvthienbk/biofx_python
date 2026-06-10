"""Prior sensitivity for the errors-in-variables model — the assumed measurement-
error SD ``tau_x``.

The EIV model treats tau_x (the predictor's instrument-noise SD) as *known*, e.g.
from calibration. But what if the assumed value is wrong? tau_x directly controls
the de-attenuation: too small and you under-correct (slope stays attenuated); too
large and you over-correct (slope inflated). We refit the EIV model under a range of
assumed tau_x and trace the recovered slope, with the naive (tau_x=0) fit as the
floor and the true tau_x as the reference.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import arviz as az  # noqa: E402
import numpy as np  # noqa: E402
from data.generate_data import generate  # noqa: E402
from model import fit  # noqa: E402

# Assumed tau_x values; true tau_x = 0.6.
ASSUMED_TAU = [0.0, 0.3, 0.6, 0.9]


def main() -> None:
    data = generate()
    true_beta = data["truth"]["beta"]
    true_tau = data["tau_x"]
    print(f"Data: n={data['n']}; true beta={true_beta}, true tau_x={true_tau}\n")
    print(f"{'assumed tau_x':>14}  {'model':>6}  {'beta mean':>9}  {'beta 94% HDI':>20}")
    rows = []
    for tau in ASSUMED_TAU:
        if tau == 0.0:
            # tau_x = 0 is exactly the naive regression (no predictor noise).
            idata = fit(data, model="naive", draws=600, tune=800, chains=2, seed=303)
            label = "naive"
        else:
            idata = fit(data, model="eiv", tau_x=tau, draws=700, tune=1200,
                        chains=2, target_accept=0.95, seed=303)
            label = "eiv"
        summ = az.summary(idata, var_names=["beta"], hdi_prob=0.94)
        bm = float(summ.loc["beta", "mean"])
        lo = float(summ.loc["beta", "hdi_3%"])
        hi = float(summ.loc["beta", "hdi_97%"])
        rows.append((tau, label, bm, lo, hi))
        print(f"{tau:>14.1f}  {label:>6}  {bm:9.3f}  [{lo:6.3f}, {hi:6.3f}]")

    print(f"\nTrue beta = {true_beta}. Naive (tau_x=0) is attenuated;")
    print("correcting with the true tau_x=0.6 recovers it; over-stating tau_x")
    print("over-corrects (slope inflated). The measurement-error SD must be")
    print("calibrated — assume it, but report sensitivity to it.")


if __name__ == "__main__":
    main()
