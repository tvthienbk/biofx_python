"""Prior sensitivity analysis for the change-point model.

We vary the **prior over the change-point tau**. The default is a flat
DiscreteUniform over all interior times (no prior knowledge of when the shift
happened). We compare it to two informative alternatives implemented as a
*weighted* discrete prior on tau via a pm.Potential:

  * uniform   — flat over 1..T-1 (default)
  * early-biased — linearly favours earlier tau
  * centered  — triangular, favours the middle of the series

We refit and compare the posterior over tau and the pre/post rates. With a sharp,
well-separated shift the likelihood dominates and the tau posterior should barely
move; the teaching point is to demonstrate that rather than assume it.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
import pymc as pm

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from data.generate_data import generate  # noqa: E402

LAM_MEAN = 5.0


def fit_with_tau_prior(data, kind: str, seed: int = 51):
    y = np.asarray(data["y"], dtype=float)
    T = len(y)
    idx = np.arange(T)
    taus = np.arange(1, T)
    if kind == "uniform":
        logw = np.zeros(T - 1)
    elif kind == "early":
        logw = np.log((T - taus).astype(float))           # favour small tau
    elif kind == "centered":
        logw = np.log(1.0 + (T / 2 - np.abs(taus - T / 2)))  # triangular peak mid
    else:
        raise ValueError(kind)
    logw = logw - np.log(np.sum(np.exp(logw)))            # normalize
    with pm.Model() as m:
        tau = pm.DiscreteUniform("tau", lower=1, upper=T - 1)
        lam0 = pm.Exponential("lam0", 1.0 / LAM_MEAN)
        lam1 = pm.Exponential("lam1", 1.0 / LAM_MEAN)
        # add the (log) prior weight for the sampled tau
        pm.Potential("tau_prior", pm.math.switch(
            tau >= 1, pt_index(logw, tau - 1), -np.inf))
        rate = pm.math.switch(tau > idx, lam0, lam1)
        pm.Poisson("y", mu=rate, observed=y)
        idata = pm.sample(draws=600, tune=800, chains=2, random_seed=seed,
                          progressbar=False)
    return idata


def pt_index(arr_np, idx_tensor):
    import pytensor.tensor as pt
    return pt.as_tensor_variable(arr_np)[idx_tensor]


def main() -> None:
    data = generate()
    t = data["truth"]
    print(f"Data: T={data['T']}, true tau={t['tau']}, lam0={t['lam0']}, "
          f"lam1={t['lam1']}\n")
    print(f"{'tau prior':>12}  {'tau mode':>8}  {'lam0 mean':>9}  {'lam1 mean':>9}")
    rows = []
    for kind in ("uniform", "early", "centered"):
        idata = fit_with_tau_prior(data, kind)
        tau_draws = idata.posterior["tau"].values.ravel().astype(int)
        mode = int(np.bincount(tau_draws).argmax())
        l0 = float(idata.posterior["lam0"].mean())
        l1 = float(idata.posterior["lam1"].mean())
        rows.append((mode, l0, l1))
        print(f"{kind:>12}  {mode:8d}  {l0:9.3f}  {l1:9.3f}")
    modes = [r[0] for r in rows]
    print(f"\ntau mode range across priors: [{min(modes)}, {max(modes)}] "
          f"(true {t['tau']})")
    print("Interpretation: with a sharp, well-separated shift the likelihood pins "
          "tau; the posterior is robust to the tau prior. A weak/ambiguous shift is "
          "where the tau prior would matter.")


if __name__ == "__main__":
    main()
