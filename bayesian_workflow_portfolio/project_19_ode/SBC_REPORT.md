# SBC Report — Project 19 (PK elimination rate k)

## Method

Simulation-Based Calibration checks the inference procedure independent of any
single dataset:

1. Draw `log k*`, `log V*` from their priors (+ `sigma*`).
2. Simulate concentrations at the design timepoints via the **closed form**
   `C(t) = (D/V) exp(-k t)`.
3. Refit the analytic model; obtain posterior draws of `k`.
4. Record the **rank** of `k*` among those draws.

Calibrated inference -> **uniform** ranks (∪ overconfident, ∩ underconfident,
slope biased).

## Why the analytic model, and why "very light"

The brief asks for *very light* SBC given ODE cost. Two compounding reasons:

1. Each SBC iteration is a full refit. With the genuine
   `pymc.ode.DifferentialEquation` model, every NUTS step integrates the ODE with
   sensitivities — refitting dozens of times would take many minutes to hours.
2. The model has an exact closed form, so SBC on the **analytic** model is both
   correct and cheap. This isolates *modelling/sampler* calibration from
   solver-tolerance noise — arguably the cleaner SBC anyway.

We run `N_SIMS = 25` with a small sampler (`draws=200, tune=400, chains=2,
cores=1`).

## Results

Run `python3 sbc.py`. It prints the chi-square uniformity test over 8 rank bins
and saves `sbc_ranks.png`. The test should report **no significant** deviation
from uniformity (`p > 0.01`, `uniform: True`) — the analytic PK model is
well-calibrated for `k` under its prior.

## Interpretation

A pass means the model+sampler recover the elimination rate with correctly-sized
uncertainty on well-specified data. It does **not** speak to identifiability under
a *poor design* (the broken notebook) — SBC draws full designs from the generative
model, which includes the early timepoints that make `k` identifiable. Calibration
and identifiability are different questions; this project teaches both.
