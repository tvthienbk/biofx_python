# SBC Report — Project 18 (local-level observation noise)

## Method

Simulation-Based Calibration checks the inference procedure independent of any
single dataset:

1. Draw `sigma_level*`, `sigma_obs*` from their HalfNormal priors (and a level0).
2. Simulate a local-level series (`T = 30`).
3. Refit the local-level model; obtain posterior draws of `sigma_obs`.
4. Record the **rank** of `sigma_obs*` among those draws.

Calibrated inference -> **uniform** ranks. ∪-shaped = overconfident, ∩-shaped =
underconfident, slope = biased.

We calibrate on `sigma_obs` because, of the two confounded variances, it is the
more cleanly checkable scalar at short series length. Jointly calibrating both
variances is expensive and partly entangled with the identifiability issue the
project is about.

## Why so few simulations

Each iteration refits a `T`-dimensional latent random walk. We run `N_SIMS = 12`
with a tiny sampler (`draws=120, tune=250, chains=2, cores=1`) so the whole script
finishes in a couple of minutes — a deliberate "SBC: light" compute trade-off.

## Results

Run `python3 sbc.py`. It prints the chi-square uniformity test over 8 rank bins
and saves `sbc_ranks.png`. With ~12 simulations the histogram is coarse; the test
should report **no significant** deviation from uniformity (`p > 0.01`,
`uniform: True`).

## Interpretation

A pass means the model+sampler recover the observation-noise scale with
correctly-sized uncertainty on well-specified data. It does **not** certify the
joint `(sigma_level, sigma_obs)` sub-space — those remain weakly identified, which
is exactly why informative priors matter (see `PRIOR_SENSITIVITY.md`). A larger
`N_SIMS` would sharpen the verdict at proportional compute cost.
