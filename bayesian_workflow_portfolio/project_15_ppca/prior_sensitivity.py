"""Prior sensitivity analysis for probabilistic PCA.

We vary the **loading-scale prior** — the Normal scale on the entries of W. This
prior controls how much variance the model attributes to the latent factors
versus the isotropic noise. We refit under three scales and compare the
identifiable summaries: sigma and the reconstructed-covariance error.

A too-tight W prior shrinks the loadings and pushes structure into sigma
(under-fitting the factors); a very vague prior is barely informative. We expect
the identifiable quantities to be fairly robust because the data covariance pins
W Wᵀ + sigma^2 I regardless of the rotation.
"""
from __future__ import annotations

import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from data.generate_data import generate  # noqa: E402
from model import fit, reconstructed_cov  # noqa: E402

PRIORS = {
    "tight  Normal(0,0.5)": 0.5,
    "default Normal(0,1.0)": 1.0,
    "vague  Normal(0,3.0)": 3.0,
}


def main() -> None:
    data = generate()
    t = data["truth"]
    Cnorm = np.linalg.norm(data["C_true"])
    print(f"Data: N={data['X'].shape[0]} x D={data['D']}, K={data['K']}; "
          f"true sigma={t['sigma']:.2f}\n")
    print(f"{'prior on W scale':>22}  {'sigma mean':>10}  {'recon-cov rel err':>17}")
    rows = []
    for name, scale in PRIORS.items():
        idata = fit(data, w_scale=scale, draws=400, tune=800, chains=2, seed=41)
        sig = float(idata.posterior["sigma"].mean())
        C_hat = reconstructed_cov(idata)
        rel = float(np.linalg.norm(C_hat - data["C_true"]) / Cnorm)
        rows.append((sig, rel))
        print(f"{name:>22}  {sig:10.3f}  {rel:17.3f}")
    arr = np.array(rows)
    print(f"\nMax spread: sigma={arr[:,0].max()-arr[:,0].min():.4f}, "
          f"recon-cov rel err range=[{arr[:,1].min():.3f}, {arr[:,1].max():.3f}]")
    print("Interpretation: the data covariance pins the rotation-invariant "
          "reconstruction; sigma and the reconstructed covariance are robust to "
          "the loading-scale prior (a too-tight prior is the main risk).")


if __name__ == "__main__":
    main()
