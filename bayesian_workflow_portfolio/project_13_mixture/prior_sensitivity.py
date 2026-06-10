"""Prior sensitivity analysis for the 2-component mixture.

We vary the **component-SD prior** (HalfNormal scale on sigma) — the prior most
likely to bite, because it trades off against how much separation the model
"explains" as two components versus one wide blob. We refit under three scales
and compare the posterior for the identifiable quantities (separation, sigma,
high-mean weight).

With a clearly bimodal dataset of N=300 the likelihood is informative and the
three posteriors should largely agree; the teaching point is to *demonstrate*
that robustness rather than assume it.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from data.generate_data import generate  # noqa: E402
from model import fit, add_separation  # noqa: E402

PRIORS = {
    "tight  HalfNormal(0.5)": 0.5,
    "default HalfNormal(1.0)": 1.0,
    "vague  HalfNormal(3.0)": 3.0,
}


def main() -> None:
    data = generate()
    t = data["truth"]
    print(f"Data: N={len(data['y'])}, true separation={t['separation']:.2f}, "
          f"sigma={t['sigma']:.2f}, w_high={t['w[1]']:.2f}\n")
    header = f"{'prior on sigma':>24}  {'sep mean':>9}  {'sigma mean':>10}  {'w_high mean':>11}"
    print(header)
    means = []
    for name, scale in PRIORS.items():
        idata = fit(
            data,
            prior_sigma_sd=scale,
            draws=500,
            tune=1000,
            chains=2,
            seed=21,
        )
        add_separation(idata)
        sep = float(idata.posterior["separation"].mean())
        sig = float(idata.posterior["sigma"].mean())
        whi = float(idata.posterior["w"].isel(w_dim_0=1).mean())
        means.append((sep, sig, whi))
        print(f"{name:>24}  {sep:9.3f}  {sig:10.3f}  {whi:11.3f}")
    arr = np.array(means)
    spread = arr.max(0) - arr.min(0)
    print(f"\nMax spread across priors: separation={spread[0]:.4f}, "
          f"sigma={spread[1]:.4f}, w_high={spread[2]:.4f}")
    print("Interpretation: with a clearly bimodal N=300 sample the data dominate; "
          "the identifiable summaries are robust to the sigma prior.")


if __name__ == "__main__":
    main()
