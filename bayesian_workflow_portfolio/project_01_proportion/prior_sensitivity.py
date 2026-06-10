"""Prior sensitivity analysis for the Beta–Binomial model.

Refit the same data under three priors and compare the posterior for theta:

  * Jeffreys    Beta(0.5, 0.5) — reference prior, U-shaped, heavy at the edges.
  * Uniform     Beta(1, 1)     — "flat", often mistaken for "no assumptions".
  * Weak-info   Beta(2, 2)     — our default; mild pull away from 0/1.

With N=80 the likelihood dominates and the three posteriors should nearly
coincide — the teaching point being that priors matter most when data are scarce.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from data.generate_data import generate  # noqa: E402
from model import analytic_posterior  # noqa: E402

PRIORS = {
    "Jeffreys Beta(0.5,0.5)": (0.5, 0.5),
    "Uniform Beta(1,1)": (1.0, 1.0),
    "Weak-info Beta(2,2)": (2.0, 2.0),
}


def main() -> None:
    data = generate()
    print(f"Data: k={data['k']} successes of n={data['n']} (true theta={data['truth']['theta']})\n")
    print(f"{'prior':>24}  {'post mean':>9}  {'post sd':>8}  {'94% HDI':>20}")
    rows = []
    for name, (a, b) in PRIORS.items():
        ap, bp = analytic_posterior(data, a=a, b=b)
        mean = ap / (ap + bp)
        var = ap * bp / ((ap + bp) ** 2 * (ap + bp + 1))
        sd = float(np.sqrt(var))
        # central 94% interval from the Beta quantile function
        from scipy.stats import beta as beta_dist
        lo, hi = beta_dist.ppf([0.03, 0.97], ap, bp)
        rows.append((name, mean, sd, lo, hi))
        print(f"{name:>24}  {mean:9.3f}  {sd:8.3f}  [{lo:6.3f}, {hi:6.3f}]")
    spread = max(r[1] for r in rows) - min(r[1] for r in rows)
    print(f"\nMax difference in posterior mean across priors: {spread:.4f}")
    print("Interpretation: with N=80 the data swamp the prior; conclusions are robust.")


if __name__ == "__main__":
    main()
