"""Prior sensitivity for the local-level model — the process/observation tension.

The two variances sigma_level (process) and sigma_obs (observation) are
confounded. The priors we place on them therefore matter: they are what tilt the
explanation toward "wandering level" vs "noisy measurement of a steady level".

We refit under three prior regimes and compare the posteriors for both variances
and the latent-level recovery:

  * Balanced    sigma_level~HN(0.5), sigma_obs~HN(1.0)  -- our default.
  * Tight-level sigma_level~HN(0.2), sigma_obs~HN(1.0)  -- "level barely drifts":
                forces a smoother level, pushes wiggle into obs noise.
  * Loose-both  sigma_level~HN(2.0), sigma_obs~HN(2.0)  -- vague: lets the two
                variances trade off freely (the confounding, unleashed).

Teaching point: with a reasonably long series the data partially separate the two
variances, but the priors visibly shift the split, especially the vague "loose"
prior. This is the central state-space modelling decision.
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
    "Balanced HN(0.5,1.0)": dict(sigma_level_sd=0.5, sigma_obs_sd=1.0),
    "Tight-level HN(0.2,1.0)": dict(sigma_level_sd=0.2, sigma_obs_sd=1.0),
    "Loose-both HN(2.0,2.0)": dict(sigma_level_sd=2.0, sigma_obs_sd=2.0),
}


def main() -> None:
    data = generate()
    tl = data["truth"]["sigma_level"]
    to = data["truth"]["sigma_obs"]
    print(f"Data: T={data['t']}, true sigma_level={tl}, true sigma_obs={to}\n")
    header = (f"{'prior':>24}  {'s_level':>7}  {'s_obs':>7}  {'div':>4}  "
              f"{'level MAE':>9}")
    print(header)
    for name, kw in PRIORS.items():
        idata = fit(data, draws=400, tune=800, chains=2, seed=11, **kw)
        s = az.summary(idata, var_names=["sigma_level", "sigma_obs"])
        n_div = int(idata.sample_stats["diverging"].sum())
        lvl = idata.posterior["level"].mean(dim=("chain", "draw")).values
        mae = float(np.mean(np.abs(lvl - data["level_true"])))
        print(f"{name:>24}  {s.loc['sigma_level','mean']:7.3f}  "
              f"{s.loc['sigma_obs','mean']:7.3f}  {n_div:4d}  {mae:9.3f}")
    print("\nInterpretation: the balanced prior recovers both variances near the "
          "truth. The tight-level prior over-smooths the level (sigma_level pulled "
          "down, sigma_obs inflated). The loose-both prior lets the two variances "
          "trade off, widening their posteriors -- the confounding made visible. "
          "Prior choice on the two noises is the key state-space decision.")


if __name__ == "__main__":
    main()
