# Prior Sensitivity — Project 17 (the length-scale prior is the lever)

## What we vary

We refit the same data under three length-scale priors and compare the posterior
for `ell`, `eta`, `sigma`, the divergence count, and the fitted-curve error
(`prior_sensitivity.py`):

| Label | Prior on `ell` | Character |
|---|---|---|
| Informative | `InverseGamma(6, 12)` | default; mass at `ell ≈ 2` |
| Mild | `InverseGamma(3, 6)` | broader, still proper; `ell ≈ 3` |
| Vague | `InverseGamma(1, 1)` | heavy-tailed; lets `ell` wander |

`eta` and `sigma` priors are held fixed; only the length-scale prior changes,
because **that is the prior that controls identifiability** in a squared-
exponential GP.

## What to expect

- **Informative & Mild:** stable, well-mixing fits. `sigma` lands near the true
  `0.18`, divergences stay at (or near) zero, and the curve MAE is small. The two
  posteriors largely agree — the data are informative enough that a *reasonable*
  length-scale prior suffices.
- **Vague `IG(1,1)`:** the prior puts non-trivial mass on both very small and
  large length-scales. This re-opens the `ell ↔ eta` trade-off: the posterior
  smears along a ridge, divergences appear, ESS drops, and the curve fit becomes
  less stable. This is the *pathology the project is about*, surfaced by relaxing
  the very prior that controls it.

## Interpretation

The headline lesson: in a GP, **robustness is not automatic and it is purchased by
the length-scale prior.** Unlike a well-identified parametric model where a vague
prior is harmless once data accumulate, a GP's `(ell, eta)` ambiguity does not
vanish with more data along the relevant direction — large `ell`/large `eta` and
small `ell`/small `eta` remain genuinely hard to distinguish. The informative,
zero-avoiding inverse-gamma prior is therefore a *modelling* decision, not a
nuisance default. Report the curve and `sigma` under the informative prior, and
disclose that conclusions would degrade under a vague length-scale prior.
