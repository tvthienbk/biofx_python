# Lessons — Project 18 (State-Space / Local-Level)

## Headline takeaways

1. **Latent states turn a time series into a hierarchical model in time.** The
   level at each `t` is an unknown to be inferred, linked to its neighbours by the
   random-walk prior. Everything you learned about hierarchical models (pooling,
   non-centred parameterisation, funnels) reappears along the time axis.

2. **Two variances, one wiggle.** Process noise (`sigma_level`) and observation
   noise (`sigma_obs`) both control how jagged the observed series looks. The
   likelihood only weakly separates them; their posteriors anti-correlate. This is
   the defining difficulty of state-space inference.

3. **Priors and data length are the levers.** Informative variance priors break
   the symmetry; longer series sharpen the separation. Neither alone is usually
   enough at realistic `T`.

4. **Non-centred is not optional.** A centred random walk funnels and diverges as
   `sigma_level` shrinks. The non-centred form (standardised innovations scaled by
   `sigma_level`) gives NUTS a flat geometry.

## Failures and surprises encountered while building this

- **Multiprocess sampling hung** without a linked BLAS; `cores=1` fixed it.
- **The centred `GaussianRandomWalk` really does diverge.** We use it deliberately
  in the broken notebook; the divergence count and the funnel are immediate.
- **The AR(1) comparison is subtle.** AR(1) conditions on the previous observation
  and so is fit on `T-1` targets, while the local-level model has a per-time-point
  likelihood on all `T`. The LOO comparison is therefore *indicative* of
  per-observation predictive fit, not a clean nested-model test. We flag this in
  the README — a good reminder that `az.compare` assumes the models score the same
  observations.
- **Recovery is good but the variances are correlated.** Even with the right
  priors, the `(sigma_level, sigma_obs)` pair plot shows the residual confounding;
  honest reporting includes that correlation, not just the marginals.

## How to generalise the technique

- **Local-linear trend.** Add a latent *slope* that also random-walks: captures
  persistent trends, not just level shifts.
- **Seasonal / cyclical components.** Add periodic latent states for daily/annual
  structure (structural time-series decomposition).
- **AR(p) and ARIMA.** Richer stationary dynamics; the AR(1) here is the entry
  point.
- **Non-Gaussian observations.** Counts (Poisson), binary (Bernoulli) emissions
  with the same latent-level backbone — a dynamic GLM.
- **Kalman filter.** For *linear-Gaussian* state-space models the latent states
  can be marginalised analytically (the Kalman filter), giving a much cheaper
  likelihood over just the variances — the natural next efficiency step.
- **Decision use.** Report the *current level* and its *trend* with uncertainty,
  and forecast forward by continuing the random walk — the band fans out, honestly
  reflecting that the future level is less certain.
