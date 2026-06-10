# Lessons — Project 17 (Gaussian Process)

## Headline takeaways

1. **A GP replaces "what shape?" with "how smooth?".** You stop choosing a
   parametric form and instead encode beliefs about smoothness (kernel) and scale
   (hyperpriors). The modelling effort moves from the mean function to the
   covariance function.

2. **The length-scale prior is the whole ballgame.** Everything that can go wrong
   with a squared-exponential GP — non-identifiability, divergences, ridges,
   bad mixing — traces back to an under-constrained length-scale. An informative,
   zero-avoiding prior (we used `InverseGamma(6,12)`) is not optional polish; it is
   what makes the model identifiable.

3. **Identifiability is a joint-posterior property.** The `(ell, eta)` marginals
   can each look unimodal and reasonable while the *joint* is a diagonal ridge.
   Always look at the pair plot of correlated hyperparameters.

4. **Marginalising the latent function is what makes this affordable.**
   `pm.gp.Marginal` integrates out the `N` function values analytically, so NUTS
   only navigates 3 hyperparameters. Without it, you'd sample an `N`-dim latent
   plus hyperparameters — much harder.

## Failures and surprises encountered while building this

- **Multiprocess sampling hung.** Without a linked BLAS, PyMC's default
  multi-core sampler stalled indefinitely on the GP likelihood. Switching to
  `cores=1` (serial chains) fixed it and was still fast enough. Lesson: in
  constrained environments, serial sampling is a reliable fallback.
- **`gp.predict` in a Python loop is a trap.** Calling `gp.predict` once per
  posterior draw recompiled a PyTensor graph each time and made prediction the
  slowest part of the whole project. Rewriting the conditional mean in **pure
  numpy** (`mu_* = K_*x (K_xx + sigma^2 I)^{-1} y`) made it instant. Lesson: for
  post-hoc GP prediction over many hyperparameter draws, do the linear algebra
  directly rather than through the modelling graph.
- **The `InverseGamma` defaults matter quantitatively.** `IG(6,12)` (mode ≈ 1.7)
  worked; an over-tight prior would bias the curve toward over-smoothing, an
  over-loose one re-opens the ridge. We sanity-checked via prior predictive draws.

## How to generalise the technique

- **Kernel choice encodes assumptions.** ExpQuad → very smooth; Matérn-3/2 →
  rougher, more realistic for many physical signals; Periodic → seasonality;
  sums/products of kernels → additive/interacting structure. Swap the kernel, keep
  the workflow.
- **Heteroscedastic noise.** Replace the scalar `sigma` with an input-dependent
  noise process (a second GP on `log sigma(x)`).
- **Large N.** The `O(N^3)` cost bites; use sparse/inducing-point approximations
  (`pm.gp.MarginalApprox`, variational methods) beyond a few hundred points.
- **Latent (non-Gaussian) likelihoods.** For counts/binary responses use
  `pm.gp.Latent` with a link function — but then the latent `f` is sampled, and
  the cost and the centred-vs-non-centred concerns from the hierarchical projects
  return.
- **Decision use.** The real deliverable is usually a derived quantity of the
  curve (a midpoint, an EC50, a maximum) *with* its uncertainty — propagate the
  posterior through that functional rather than reading a point estimate.
