# SBC Report — Project 20 (between-compound SD tau)

## Method

Simulation-Based Calibration checks the inference procedure independent of any
single dataset:

1. Draw `mu*`, `tau*`, `sigma*` from their priors; draw `theta_j* = mu* + tau* z_j*`.
2. Simulate a compound screen with the project's unequal-replication structure.
3. Refit the hierarchical model; obtain posterior draws of `tau`.
4. Record the **rank** of `tau*` among those draws.

Calibrated inference -> **uniform** ranks (∪ overconfident, ∩ underconfident,
slope biased).

We calibrate on **`tau`** because it is the parameter that governs the
partial-pooling behaviour at the heart of the project (and the one the prior
sensitivity probes). `tau` is also the classic hard-to-calibrate hierarchical
variance, so it is the most informative target.

## Why so few simulations

Each iteration is a full hierarchical NUTS refit. We run `N_SIMS = 20` with a small
sampler (`draws=150, tune=300, chains=2, cores=1`, `J = 8`) and the **non-centred**
parameterisation (which keeps the funnel away even at small `tau*`) so the script
finishes in a couple of minutes — a deliberate "SBC: light" compute trade-off.

## Results

Run `python3 sbc.py`. It prints the chi-square uniformity test over 8 rank bins
and saves `sbc_ranks.png`. The test should report **no significant** deviation from
uniformity (`p > 0.01`, `uniform: True`) — the non-centred hierarchical model is
well-calibrated for `tau` under its prior.

## Interpretation

A pass means the model+sampler recover the between-compound sd with correctly-sized
uncertainty on well-specified data — the prerequisite for trusting the downstream
*decision*. (If `tau` were miscalibrated, the shrinkage — and hence the
recommendation — could be systematically off.) Calibration of `tau` underwrites the
whole decision layer; this is the capstone's correctness backbone. A larger
`N_SIMS` would sharpen the verdict at proportional cost.
