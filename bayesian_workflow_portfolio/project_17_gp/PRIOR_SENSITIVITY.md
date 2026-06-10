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

> **Compute note.** Because a GP-with-Gaussian-noise has a **closed-form marginal
> likelihood**, the script obtains each posterior by self-normalised **importance
> sampling** in pure numpy (prior particles weighted by the marginal likelihood,
> then resampled) instead of running NUTS three times. This is exact up to
> Monte-Carlo error, runs in a few seconds, and avoids the slow no-BLAS GP sampling
> — the same closed-form philosophy as the main model and the SBC script.

## What to expect

- **Informative & Mild:** stable fits. `sigma` lands near the true `0.18`, the
  curve MAE is small, and the `(ell, eta)` correlation is modest. The posteriors
  largely agree — the data + the informative `eta`/`sigma` priors are enough that a
  *reasonable* length-scale prior suffices.
- **Vague `IG(1,1)`:** `sigma` and the curve stay robust (they are pinned by the
  data), but the **length-scale `ell` drifts upward** as its prior loosens and the
  `(ell, eta)` posterior stays correlated — the residual non-identifiability the
  length-scale prior exists to control. Push the prior vaguer still, or shrink the
  data, and this drift becomes a full `(ell, eta)` ridge (see `notebook_broken.ipynb`).

## Interpretation

The headline lesson: in a GP, **what the length-scale prior buys you is control of
`ell` itself.** The fitted curve and the noise scale can look robust while `ell`
quietly wanders — and `ell` is exactly the quantity that governs flexibility and
that trades off with the amplitude `eta`. Unlike a well-identified parametric model
where a vague prior is harmless once data accumulate, a GP's `(ell, eta)` ambiguity
does not vanish along the relevant direction: large `ell`/large `eta` and small
`ell`/small `eta` remain genuinely hard to distinguish. The informative,
zero-avoiding inverse-gamma length-scale prior is therefore a *modelling* decision,
not a nuisance default.
