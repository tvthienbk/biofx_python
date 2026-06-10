# Lessons — Project 14 (Hidden Markov Model)

## The one-sentence takeaway

Marginalize the discrete state path with the **forward algorithm** (sum, via
log-sum-exp — not the Viterbi max) so NUTS sees a smooth continuous likelihood,
and break the same state-label symmetry as a mixture with an ordered transform.

## What was new here

Project 13 had latent *membership* over independent points. Here the latent state
**persists in time**: a first-order Markov chain ties successive observations
together. The new computational skill is the **forward recursion**, which sums
over `2^T` possible state paths in `O(T·K^2)` time. Implementing it in
`pytensor.scan` and exposing it as a `pm.Potential` lets us keep gradient-based
NUTS while integrating the discrete states out exactly.

Two ideas generalize far beyond this project:

- **Marginalize discrete latents.** Whenever you can sum a discrete latent out in
  closed form (mixtures, HMMs, marginalized change-points), do it: you trade a
  badly-mixing discrete sampler for smooth gradients.
- **The likelihood need not come from an observed RV.** `pm.Potential` lets you add
  *any* differentiable log-density term — here the forward log-likelihood. The cost
  is that standard prior/posterior predictive machinery doesn't apply
  automatically; you build PPCs by simulating from the generative model yourself.

## Failures and surprises encountered while building this

1. **`return_updates` deprecation in `pytensor.scan`.** The default scan signature
   is changing; passing `return_updates=True` silences a `DeprecationWarning` and
   future-proofs the code. *Lesson:* pin the scan calling convention explicitly.

2. **`sample_prior_predictive` warns under a Potential likelihood.** "The effect of
   Potentials on other parameters is ignored during prior predictive sampling."
   That is expected — there is no observed RV. We restrict prior predictive to the
   *parameters* (`var_names=[...]`) so the call is meaningful and quiet.

3. **`log_likelihood` / LOO is awkward with a single Potential.** A Potential
   bundles the whole-sequence log-likelihood into one term, so there is no natural
   per-observation pointwise log-likelihood for LOO without extra bookkeeping. We
   note this rather than force it; model comparison here leans on recovery + PPC.

4. **Cost scales with T.** Each leapfrog step runs a length-T scan, so SBC and the
   prior sweep had to use short trajectories and small samplers to stay under the
   time budget. *Lesson:* for scan-based likelihoods, calibration is necessarily a
   smoke test unless you can spend real compute.

## The subtle bug worth internalizing

`max` vs `logsumexp` in the recursion is the deepest lesson. Both compile and
sample; R-hat looks fine for both. But `max` computes the Viterbi *best-path*
probability, while `logsumexp` computes the *marginal* likelihood. Using the wrong
one biases the parameters **silently** — convergence diagnostics never flag it.
Only a **recovery test against known truth** (or SBC, or a posterior-predictive
dwell-time check) catches it. This is the single best argument in the whole
portfolio for why "the chains converged" is not the same as "the answer is right."

## How to generalize the technique

- **More states (K>3):** same forward recursion with a K×K transition matrix
  (Dirichlet rows); ordering the emission means still breaks the label symmetry.
- **State decoding:** add the backward pass (forward–backward) for smoothed state
  posteriors, or Viterbi for the MAP path — but keep the *forward* sum for
  parameter inference.
- **Non-Gaussian / multivariate emissions:** swap the emission log-density; the
  recursion is unchanged.
- **Semi-Markov / explicit dwell times:** if dwell times are non-geometric, the
  2-state HMM misfits; the posterior-predictive dwell-time check is the trigger to
  upgrade the model.

## If I built it again

I would add a forward–backward smoothing cell to the clean notebook (overlaying the
decoded state path on the data is a compelling visual), and a small K=3-on-2-state
over-fitting demo to make the model-selection point concrete rather than only in
the extension prompt.
