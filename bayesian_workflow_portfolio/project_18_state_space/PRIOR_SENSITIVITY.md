# Prior Sensitivity — Project 18 (process vs observation noise)

## What we vary

The two variances `sigma_level` (process) and `sigma_obs` (observation) are
confounded; the priors tilt the explanation toward "wandering level" vs "noisy
measurement of a steady level". We refit under three regimes and compare both
posteriors plus latent-level recovery (`prior_sensitivity.py`):

| Label | `sigma_level` prior | `sigma_obs` prior | Character |
|---|---|---|---|
| Balanced | `HalfNormal(0.5)` | `HalfNormal(1.0)` | default |
| Tight-level | `HalfNormal(0.2)` | `HalfNormal(1.0)` | "level barely drifts" |
| Loose-both | `HalfNormal(2.0)` | `HalfNormal(2.0)` | vague; confounding unleashed |

## What to expect

- **Balanced:** both variances land near their truths (`0.30`, `0.60`), low
  divergences, good level recovery.
- **Tight-level:** forces a smoother level — `sigma_level` is pulled down and the
  unexplained wiggle is pushed into `sigma_obs` (inflated). The latent level
  **oversmooths**.
- **Loose-both:** the two variances trade off freely; their posteriors widen and
  anti-correlate. The level recovery degrades and divergences may appear. This is
  the confounding made visible.

## Interpretation

The split between process and observation noise is **not** fully determined by the
data at moderate `T`; the priors visibly shift it. This is the central state-space
modelling decision, and it is a feature, not a bug: encode what you know about how
fast the underlying level can move and how noisy the instrument is. Robustness
here is purchased by *informative* variance priors and by *longer series* — with
much larger `T` the two variances separate better, but the priors still matter at
realistic data lengths.
