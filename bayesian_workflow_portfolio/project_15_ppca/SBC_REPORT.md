# SBC Report — Probabilistic PCA

## Method

Simulation-Based Calibration checks that the inference procedure is
self-consistent. For PPCA we calibrate the **identifiable** scalar that survives
the rotation symmetry: the isotropic noise **`sigma`**. (Raw loadings are
non-identified and would not produce meaningful ranks — that is the entire point
of this project.) Recipe:

1. Draw `sigma` from its `HalfNormal(1)` prior and `W, mu, z` from their priors.
2. Simulate an `N x D` dataset (`N=50, D=6, K=2`).
3. Refit the `K=2` model with a small sampler (`draws=150, tune=300, chains=2`).
4. Record the **rank** of the true `sigma` among the posterior `sigma` draws.

Calibrated inference ⇒ ranks uniform on `{0, …, L}`. We use `N_SIMS = 12`
simulations with small `N` to keep the run to a couple of minutes.

## Results

Output of `python3 sbc.py` (chi-square uniformity, 8 bins; histogram saved to
`sbc_ranks.png`):

```
SBC over 12 simulations (N=50, D=6, K=2)
  sigma: chi2=4.00, dof=7, p=0.780, uniform=True
```

The `sigma` ranks pass the 8-bin chi-square uniformity test at this smoke-level
resolution. Run the script to regenerate the exact numbers (printed to stdout;
histogram in `sbc_ranks.png`).

## How to read it

- **Flat** histogram → `sigma` inference is calibrated.
- **∪-shape** → posterior on `sigma` too narrow (over-confident).
- **∩-shape** → too wide (under-confident).
- **Slope** → bias (e.g. consistently over- or under-estimating the noise).

`sigma` is the natural SBC target here because it is low-dimensional and strongly
informed by the data once the factor structure is accounted for. The reconstructed
covariance is also identified but is matrix-valued; calibrating it would require a
scalar summary (e.g. its trace) and is left to the higher-resolution production
version. With 12 simulations the histogram is coarse — we look for gross
miscalibration, not fine structure.

## A note on what SBC does *not* test here

SBC on `sigma` does **not** certify the raw loadings (they are not identified, so
"calibration" is undefined for them). That is by design: the project's lesson is
to recognize which quantities are estimable and to direct both interpretation and
calibration at those.
